# BeVo paper demo

Static project page for **Behavior-Conditioned Animal Vocalization Generation: Event-Aware Modeling and Multidimensional Evaluation**.

## Current state

- Paper title, all six authors and four affiliations, abstract summary, dataset statistics, method summary, and reported results match the supplied final manuscript.
- The paper PDF is available at `paper/BCAVG.pdf`. BeVo is linked at https://huggingface.co/datasets/Xinghour/BeVo; the model code is linked at https://github.com/xinghour/BCAVG.
- Results reproduce the full overall table, including the Real Reference and both language-aligned fidelity metrics. Optional tables show dataset splits and species-wise results. The conditioning summary includes macro accuracy, mAP, and the target-probability increase rate; the 85.39% rate is not an accuracy improvement.
- The method panel includes the training and inference settings: 400 epochs, batch size 64, AdamW at 1e-5, 50 generation steps, guidance scale 4.5, and target duration from the corresponding real test recording.
- The supplied dataset overview, Event-Aware modeling figure, and AnimalCLAP t-SNE figure are included.
- The listening panel contains 42 matched test-recording/final-model pairs: hyena (8 condition labels), meerkat (6), marmoset (6), goat (8), zebra (4), and zebra finch (10).
- Species and condition-label tabs show the selected sample's exact test-manifest prompt. There are only two systems: real reference and final Event-Aware generation, with no old-baseline listening slots.
- Generated WAV files come from `outputs/test_inference`; the inference script uses the trained `outputs/all_animals/checkpoints/best.safetensors` checkpoint. Its generic `finetuned_checkpoint` argument does not mean these are the separate fine-tuned baseline results in the paper's comparison table.
- Real WAV files come from the corresponding exact-ID paths under `last_data/test/`, not the training split. Both members of each pair are exported as browser-compatible PCM16 WAVs. The same gain is applied to both, bringing their joint sample peak to -3 dBFS for comfortable playback while preserving their relative level. Source files are unchanged; no cropping, time stretching, filtering, or independent normalization is applied.
- Each playable file has a spectrogram (84 images) exported at 1920×840 with web-readable labels. Within each pair, both plots use identical time/frequency axes, duration-adaptive Hann STFT settings, one shared amplitude reference, and an 80 dB color range. Hyena, goat, and zebra use logarithmic frequency from 50 Hz to 22.05 kHz; the other species use linear frequency from 0 to 22.05 kHz. Short events use milliseconds on the time axis. Per-pair settings are recorded in the curation report. Spectrograms describe the exported playback audio, not independently normalized images.
- Samples are curated for spectral resemblance from 3,100 exact-ID candidate pairs, subject to silence, clipping, and level-gap checks. This showcase is not a random sample, a model-wide performance estimate, or proof of behavioral correctness.
- Exact corpus preprocessing thresholds are not added until the corresponding source settings have been verified.

## Preview locally

Serve the repository root with any static HTTP server. The site has no build step and no third-party runtime dependency.

## Audio provenance and reproduction

`samples.js` is the browser catalog. `data/audio-curation.json` records exact source paths, prompts, the ranked shortlist for every label, selected asset paths/hashes, playback gain, and selection settings. The original six pairs remain in `audio/` only as a fallback for a missing catalog.

Condition labels include vocalization categories as well as behavioral contexts. A prompt describes a category-associated condition, not behavior independently verified in the particular reference recording. The page explicitly discloses the spectral-resemblance curation.

The optional offline curation script requires NumPy, SciPy, SoundFile, Matplotlib, and Pillow. These are not website runtime dependencies.

```sh
python scripts/curate_audio_demo.py analyze \
  --manifest /Volumes/Untitled/tfab_baseline2/cache/test_audio_manifest.json \
  --real-root /Volumes/Untitled/last_data/test \
  --generated-root /Volumes/Untitled/tfab_baseline2/outputs/test_inference
python scripts/curate_audio_demo.py build \
  --manifest /Volumes/Untitled/tfab_baseline2/cache/test_audio_manifest.json \
  --real-root /Volumes/Untitled/last_data/test \
  --generated-root /Volumes/Untitled/tfab_baseline2/outputs/test_inference
```

## GitHub Pages

This repository is published directly from the root of the `main` branch. GitHub Pages keeps the public project URL unchanged when the page content is updated.
