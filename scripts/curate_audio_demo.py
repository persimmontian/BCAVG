#!/usr/bin/env python3
"""Curate exact-ID test/output pairs and build static demo media.

Requires numpy, scipy, soundfile, matplotlib, Pillow. Full clips receive one
shared scalar playback gain per pair, then PCM16 encoding. No trimming,
stretching, filtering, or independent level normalization is performed.
"""

import argparse
import hashlib
import json
import math
import re
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal, sparse


SPECIES = {
    "hyena": ("Spotted hyena", "whoop"),
    "meerkat": ("Meerkat", "alarm call"),
    "marmoset": ("Common marmoset", "phee"),
    "goat": ("Domestic goat", "mother kid reunion"),
    "zebra": ("Plains zebra", "quagga quagga"),
    "zebrafinch": ("Zebra finch", "song"),
}
SAMPLE_RATE = 44100
NFFT = 1024
HOP = 220
TIME_BINS = 96
DB_MIN = -80
DB_MAX = 0


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def source_relative(location):
    marker = "/test/"
    if marker not in location:
        raise ValueError(f"Not a test-split path: {location}")
    return Path(location.split(marker, 1)[1])


def read_audio(filename):
    channels, sample_rate = sf.read(filename, dtype="float32", always_2d=True)
    if not np.isfinite(channels).all() or len(channels) == 0:
        raise ValueError(f"Invalid waveform: {filename}")
    mono = channels.mean(axis=1)
    if sample_rate != SAMPLE_RATE:
        factor = math.gcd(sample_rate, SAMPLE_RATE)
        mono = signal.resample_poly(mono, SAMPLE_RATE // factor, sample_rate // factor)
    return channels, sample_rate, mono


def mel_filterbank():
    freqs = np.fft.rfftfreq(NFFT, 1 / SAMPLE_RATE)
    mel_max = 2595 * np.log10(1 + SAMPLE_RATE / 2 / 700)
    edges = 700 * (10 ** (np.linspace(0, mel_max, 66) / 2595) - 1)
    bank = np.zeros((64, len(freqs)), dtype=np.float32)
    for index in range(64):
        left, center, right = edges[index:index + 3]
        bank[index] = np.maximum(0, np.minimum(
            (freqs - left) / (center - left),
            (right - freqs) / (right - center)))
        bank[index] /= max(bank[index].sum(), 1e-12)
    return sparse.csr_matrix(bank)


BANK = mel_filterbank()


def stft(mono):
    if len(mono) < NFFT:
        mono = np.pad(mono, (0, NFFT - len(mono)))
    freqs, times, values = signal.stft(
        mono, fs=SAMPLE_RATE, window="hann", nperseg=NFFT,
        noverlap=NFFT - HOP, boundary="zeros", padded=True)
    return freqs, times, values


def time_resize(values):
    old = np.linspace(0, 1, values.shape[-1])
    new = np.linspace(0, 1, TIME_BINS)
    return np.stack([np.interp(new, old, row) for row in np.atleast_2d(values)])


def features(mono, channels):
    _, _, values = stft(mono)
    power = np.abs(values) ** 2
    mel_power = np.asarray(BANK @ power)
    distribution = mel_power.mean(axis=1)
    distribution = np.sqrt(distribution / max(distribution.sum(), 1e-20))
    relative_db = 10 * np.log10(np.maximum(mel_power, 1e-20) / max(mel_power.max(), 1e-20))
    texture = time_resize(np.clip((relative_db + 50) / 50, 0, 1)).ravel()
    envelope = time_resize(np.sqrt(power.sum(axis=0)))[0]
    envelope /= max(envelope.max(), 1e-12)
    rms = np.sqrt(np.mean(channels.astype(np.float64) ** 2))
    peak = np.max(np.abs(channels))
    clipping = np.mean(np.abs(channels) >= 0.999)
    silence = np.mean(envelope < 0.05)
    return {
        "distribution": distribution, "texture": texture,
        "envelope": envelope, "rms_dbfs": float(20 * np.log10(max(rms, 1e-12))),
        "peak": float(peak), "clipping_fraction": float(clipping),
        "silence_fraction": float(silence),
    }


def cosine(a, b):
    return float(np.dot(a, b) / max(np.linalg.norm(a) * np.linalg.norm(b), 1e-20))


def score_pair(real, generated):
    spectral = cosine(real["distribution"], generated["distribution"])
    texture = cosine(real["texture"], generated["texture"])
    envelope = cosine(real["envelope"], generated["envelope"])
    level_gap = abs(real["rms_dbfs"] - generated["rms_dbfs"])
    silence_gap = abs(real["silence_fraction"] - generated["silence_fraction"])
    quality_penalty = (
        0.15 * min(level_gap / 30, 1)
        + 0.05 * silence_gap
        + 0.10 * min(max(0, -generated["rms_dbfs"] - 60) / 30, 1)
        + min(generated["clipping_fraction"] * 2, 0.2))
    score = 0.50 * spectral + 0.35 * texture + 0.15 * envelope - quality_penalty
    return {
        "selection_score": round(score, 6),
        "spectral_distribution_similarity": round(spectral, 6),
        "time_frequency_similarity": round(texture, 6),
        "envelope_similarity": round(envelope, 6),
        "rms_gap_db": round(level_gap, 3),
        "real_rms_dbfs": round(real["rms_dbfs"], 3),
        "generated_rms_dbfs": round(generated["rms_dbfs"], 3),
        "real_clipping_fraction": round(real["clipping_fraction"], 6),
        "generated_clipping_fraction": round(generated["clipping_fraction"], 6),
    }


def analyze(args):
    manifest = json.loads(args.manifest.read_text())
    groups = defaultdict(list)
    errors = []
    excluded = []
    for index, record in enumerate(manifest, 1):
        relative = source_relative(record["location"])
        try:
            real_channels, real_rate, real_mono = read_audio(args.real_root / relative)
            gen_channels, gen_rate, gen_mono = read_audio(args.generated_root / relative)
            real_features = features(real_mono, real_channels)
            gen_features = features(gen_mono, gen_channels)
            quality_bad = (
                real_features["rms_dbfs"] < -85 or gen_features["rms_dbfs"] < -85
                or real_features["peak"] < 1e-5 or gen_features["peak"] < 1e-5
                or abs(real_features["rms_dbfs"] - gen_features["rms_dbfs"]) > 30
                or gen_features["clipping_fraction"] > 0.01
                or real_features["clipping_fraction"] > 0.05)
            if quality_bad:
                excluded.append(str(relative))
                continue
            groups[(record["animal"], record["label"])].append({
                "animal": record["animal"], "label": record["label"],
                "prompt": record["prompt"], "source": relative.as_posix(),
                "real_duration": len(real_channels) / real_rate,
                "generated_duration": len(gen_channels) / gen_rate,
                "metrics": score_pair(real_features, gen_features),
            })
        except Exception as error:
            errors.append({"source": str(relative), "error": str(error)})
        if index % 200 == 0:
            print(f"Compared {index}/{len(manifest)} exact-ID pairs", flush=True)
    ranked = []
    for (animal, label), candidates in sorted(groups.items()):
        candidates.sort(key=lambda item: (-item["metrics"]["selection_score"], item["source"]))
        ranked.append({"animal": animal, "label": label,
                       "candidate_count": len(candidates), "candidates": candidates[:5]})
    report = {
        "method": {
            "description": "Curated exact-ID test/output pairs, ranked within each condition label.",
            "weights": {"spectral_distribution": 0.50, "time_frequency": 0.35, "envelope": 0.15},
            "notes": "Spectral features use level normalization for shape comparison; a level-gap and clipping penalty is applied. This is a showcase selection metric, not a paper evaluation metric or evidence of behavioral correctness.",
            "analysis_sample_rate": SAMPLE_RATE, "fft_size": NFFT, "hop_samples": HOP,
            "plot_db_range": [DB_MIN, DB_MAX],
            "plot_reference": "One common peak STFT amplitude across both clips in each pair",
            "playback_processing": "One shared scalar gain per pair, joint sample peak at -3 dBFS; PCM16 encoding only. No spectral or temporal editing.",
        },
        "total_manifest_records": len(manifest), "labels_with_candidates": len(ranked),
        "excluded_low_quality": excluded, "errors": errors, "ranked": ranked,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"Ranked {len(ranked)} labels; excluded {len(excluded)}; errors {len(errors)}", flush=True)
    if errors or len(ranked) != 42:
        raise RuntimeError("Incomplete candidate coverage; inspect report before building")


def write_browser_audio(source, target, gain):
    info = sf.info(source)
    if info.format == "WAV" and info.subtype == "PCM_16" and abs(gain - 1) < 1e-12:
        shutil.copyfile(source, target)
    else:
        channels, rate = sf.read(source, dtype="float64", always_2d=True)
        sf.write(target, channels * gain, rate, subtype="PCM_16")


def plot_settings(animal, duration):
    """Choose a readable display, identically for both members of a pair.

    These are visualization settings, not the paper's AFDD feature extraction
    or the fixed settings used by the showcase ranking heuristic above.
    """
    low_pitch = animal in {"hyena", "goat", "zebra"}
    if duration < 0.08:
        window = 256
    elif duration < 0.2:
        window = 512
    elif duration < 0.5:
        window = 2048 if low_pitch else 1024
    else:
        window = 4096 if low_pitch else 2048
    return {
        "window": "hann", "fft_size": window, "hop_samples": window // 16,
        "frequency_scale": "log" if low_pitch else "linear",
        "frequency_limits_hz": [50 if low_pitch else 0, SAMPLE_RATE / 2],
        "time_unit": "ms" if duration < 0.5 else "s",
        "image_pixels": [1920, 840], "db_range": [DB_MIN, DB_MAX],
    }


def display_stft(mono, settings):
    window = settings["fft_size"]
    if len(mono) < window:
        mono = np.pad(mono, (0, window - len(mono)))
    return signal.stft(
        mono, fs=SAMPLE_RATE, window=settings["window"], nperseg=window,
        noverlap=window - settings["hop_samples"], boundary="zeros", padded=True)


def record_plot_method(report):
    report["method"]["plot_settings"] = {
        "description": "Duration-adaptive Hann windows and species-aware frequency axes, identical within each real/generated pair. Settings recorded per selected pair. No image smoothing or interpolation.",
        "reference": "Joint peak STFT amplitude across the two exported playback clips",
        "db_range": [DB_MIN, DB_MAX], "image_pixels": [1920, 840],
        "note": "Display parameters only; fixed ranking-analysis FFT/hop and paper evaluation metrics are unchanged.",
    }


def plot_spectrum(mono, common_duration, shared_reference_db, target, settings):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    freqs, times, values = display_stft(mono, settings)
    # scipy STFT uses Hann-window coherent-gain normalization. Multiply by
    # two for the positive-frequency sinusoid amplitude convention.
    db = 20 * np.log10(np.maximum(np.abs(values) * 2, 1e-12)) - shared_reference_db
    time_factor = 1000 if settings["time_unit"] == "ms" else 1
    fig, ax = plt.subplots(figsize=(9.6, 4.2), dpi=200)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#090b18")
    mesh = ax.pcolormesh(times * time_factor, freqs / 1000, db, cmap="magma",
                         vmin=DB_MIN, vmax=DB_MAX, shading="auto", rasterized=True)
    ax.set_yscale(settings["frequency_scale"])
    ax.set_ylim(*(np.asarray(settings["frequency_limits_hz"]) / 1000))
    ax.set_xlim(0, common_duration * time_factor)
    if settings["frequency_scale"] == "log":
        ax.set_yticks([0.1, 0.5, 2, 8, 20])
        ax.set_yticklabels(["0.1", "0.5", "2", "8", "20"])
        ax.minorticks_off()
    else:
        ax.set_yticks([0, 5, 10, 15, 20])
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=3))
    ax.set_xlabel(f"Time ({settings['time_unit']})", fontsize=18)
    ax.set_ylabel("Frequency (kHz)", fontsize=18)
    ax.tick_params(labelsize=16)
    colorbar = fig.colorbar(mesh, ax=ax, pad=0.022, fraction=0.035)
    colorbar.set_label("dB re. pair peak", fontsize=15)
    colorbar.set_ticks([-80, -60, -40, -20, 0])
    colorbar.ax.tick_params(labelsize=14)
    fig.subplots_adjust(left=0.11, right=0.91, bottom=0.22, top=0.96)
    fig.savefig(target, dpi=200, metadata={
        "Software": "BCAVG demo: Python scipy STFT / Matplotlib; no image smoothing",
        "Description": json.dumps({**settings, "shared_reference_db": shared_reference_db}),
    })
    plt.close(fig)


def build(args):
    report = json.loads(args.report.read_text())
    report["method"].pop("waveform_editing", None)
    report["method"]["playback_processing"] = (
        "Same gain for both members of each pair, bringing their joint sample peak to -3 dBFS; "
        "PCM16 conversion only, no crop, time stretching, filtering or independent normalization. "
        "Original source files are unchanged."
    )
    audio_root = args.repo / "audio"
    spectrum_root = args.repo / "spectrograms"
    audio_root.mkdir(exist_ok=True)
    spectrum_root.mkdir(exist_ok=True)
    by_animal = defaultdict(list)
    for entry in report["ranked"]:
        by_animal[entry["animal"]].append(entry["candidates"][0])
    data = {}
    selected = []
    for animal, (name, preferred) in SPECIES.items():
        key = "zebra-finch" if animal == "zebrafinch" else animal
        samples = []
        candidates = sorted(by_animal[animal], key=lambda item: (item["label"] != preferred, item["label"]))
        for candidate in candidates:
            relative = Path(candidate["source"])
            sample_number = relative.stem.rsplit("_", 1)[-1]
            identifier = f"{key}-{slug(candidate['label'])}-{slug(sample_number)}"
            real_target = audio_root / f"{identifier}-real.wav"
            gen_target = audio_root / f"{identifier}-generated.wav"
            real_source, gen_source = args.real_root / relative, args.generated_root / relative
            real_channels, _, _ = read_audio(real_source)
            gen_channels, _, _ = read_audio(gen_source)
            joint_peak = max(np.abs(real_channels).max(), np.abs(gen_channels).max())
            playback_gain = 10 ** (-3 / 20) / max(joint_peak, 1e-12)
            write_browser_audio(real_source, real_target, playback_gain)
            write_browser_audio(gen_source, gen_target, playback_gain)
            _, _, real_mono = read_audio(real_target)
            _, _, gen_mono = read_audio(gen_target)
            common_duration = max(candidate["real_duration"], candidate["generated_duration"])
            settings = plot_settings(animal, common_duration)
            peak = max(np.abs(display_stft(real_mono, settings)[2]).max(),
                       np.abs(display_stft(gen_mono, settings)[2]).max()) * 2
            shared_reference_db = float(20 * np.log10(max(peak, 1e-12)))
            real_plot = spectrum_root / f"{identifier}-real.png"
            gen_plot = spectrum_root / f"{identifier}-generated.png"
            plot_spectrum(real_mono, common_duration, shared_reference_db, real_plot, settings)
            plot_spectrum(gen_mono, common_duration, shared_reference_db, gen_plot, settings)
            label = candidate["label"].capitalize().replace("Mother kid", "Mother–kid")
            item = {
                "id": identifier, "label": label, "prompt": candidate["prompt"],
                "realAudio": f"audio/{real_target.name}",
                "generatedAudio": f"audio/{gen_target.name}",
                "realSpectrogram": f"spectrograms/{real_plot.name}",
                "generatedSpectrogram": f"spectrograms/{gen_plot.name}",
                "duration": round(candidate["real_duration"], 4),
                "realDuration": round(candidate["real_duration"], 4),
                "generatedDuration": round(candidate["generated_duration"], 4),
                "source": candidate["source"],
                "playbackGainDb": round(20 * math.log10(playback_gain), 3),
            }
            samples.append(item)
            selected.append({**candidate, "id": identifier,
                             "playback_gain_db": item["playbackGainDb"],
                             "spectrogram_settings": {**settings, "shared_reference_db": shared_reference_db},
                             "real_sha256": hashlib.sha256(real_target.read_bytes()).hexdigest(),
                             "generated_sha256": hashlib.sha256(gen_target.read_bytes()).hexdigest()})
            print(f"Built {len(selected):02d}/42: {animal} / {candidate['label']} ({candidate['metrics']['selection_score']:.3f})", flush=True)
        data[key] = {"name": name, "samples": samples}
    (args.repo / "samples.js").write_text(
        "// Curated exact-ID test/final-model pairs. See data/audio-curation.json.\n"
        + "const demoSamples = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n")
    report["selected"] = selected
    record_plot_method(report)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"Built {len(selected)} pairs, {len(selected) * 2} spectrograms", flush=True)


def replot(args):
    """Redraw selected pairs only: never rerank or rewrite playback audio."""
    report = json.loads(args.report.read_text())
    selected = report["selected"]
    for index, item in enumerate(selected, 1):
        real_path = args.repo / "audio" / f"{item['id']}-real.wav"
        gen_path = args.repo / "audio" / f"{item['id']}-generated.wav"
        for path, hash_key in [(real_path, "real_sha256"), (gen_path, "generated_sha256")]:
            if hashlib.sha256(path.read_bytes()).hexdigest() != item[hash_key]:
                raise ValueError(f"Exported audio has changed: {path}")
        _, _, real_mono = read_audio(real_path)
        _, _, gen_mono = read_audio(gen_path)
        duration = max(len(real_mono) / SAMPLE_RATE, len(gen_mono) / SAMPLE_RATE)
        settings = plot_settings(item["animal"], duration)
        peak = max(np.abs(display_stft(real_mono, settings)[2]).max(),
                   np.abs(display_stft(gen_mono, settings)[2]).max()) * 2
        reference = float(20 * np.log10(max(peak, 1e-12)))
        for mono, suffix in [(real_mono, "real"), (gen_mono, "generated")]:
            plot_spectrum(mono, duration, reference,
                          args.repo / "spectrograms" / f"{item['id']}-{suffix}.png", settings)
        item["spectrogram_settings"] = {**settings, "shared_reference_db": reference}
        print(f"Redrew {index:02d}/{len(selected)}: {item['id']} "
              f"(FFT {settings['fft_size']}, hop {settings['hop_samples']})", flush=True)
    record_plot_method(report)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")


def review(args):
    from PIL import Image, ImageDraw, ImageFont
    report = json.loads(args.report.read_text())
    args.review_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    pairs = report["selected"]
    for offset in range(0, len(pairs), 6):
        batch = pairs[offset:offset + 6]
        sheet = Image.new("RGB", (1200, len(batch) * 285 + 35), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text((110, 4), "REAL TEST RECORDING", fill="#14312a", font=font)
        draw.text((700, 4), "FINAL MODEL OUTPUT", fill="#14312a", font=font)
        for row, item in enumerate(batch):
            y = row * 285 + 35
            draw.text((12, y), f"{item['animal']} / {item['label']} / {item['id']}",
                      fill="#14312a", font=font)
            for column, suffix in enumerate(["real", "generated"]):
                image = Image.open(args.repo / "spectrograms" / f"{item['id']}-{suffix}.png")
                image = image.resize((600, 263))
                sheet.paste(image, (column * 600, y + 22))
        target = args.review_dir / f"pairs-{offset // 6 + 1:02d}.jpg"
        sheet.save(target, quality=90)
        print(target, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["analyze", "build", "replot", "review"])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--real-root", type=Path)
    parser.add_argument("--generated-root", type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path)
    parser.add_argument("--review-dir", type=Path, default=Path("/tmp/BCAVG-spectrogram-review"))
    args = parser.parse_args()
    if args.mode in {"analyze", "build"} and not all(
            [args.manifest, args.real_root, args.generated_root]):
        parser.error("analyze/build require --manifest, --real-root and --generated-root")
    args.report = args.report or args.repo / "data/audio-curation.json"
    {"analyze": analyze, "build": build, "replot": replot, "review": review}[args.mode](args)


if __name__ == "__main__":
    main()
