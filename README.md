# BeVo paper demo

Static project page for **Behavior-Conditioned Animal Vocalization Generation**.

## Current state

- Paper title, authors, affiliations, abstract summary, dataset statistics, method summary, and reported results are included.
- The supplied dataset overview, Event-Aware modeling figure, and AnimalCLAP t-SNE figure are included.
- The listening panel pairs six real test recordings with the corresponding final Event-Aware model outputs; both sides are playable.
- Species tabs show the exact test-manifest prompts paired with these outputs. These six examples are representative current selections, not a curated "best of" set.
- Generated WAV files in `audio/` are browser-compatible PCM copies of outputs from `outputs/test_inference`; the inference script uses the trained `outputs/all_animals/checkpoints/best.safetensors` checkpoint. The script's generic `finetuned_checkpoint` argument does not mean these are the separate fine-tuned baseline results in the paper's comparison table.
- Real WAV files come from the corresponding paths under `last_data/test/`, not the training split. Five were copied without audio conversion; the zebra recording was converted from float WAV to 16-bit PCM WAV for browser compatibility.
- Paper/code/dataset links are still awaiting source material.

## Preview locally

Serve the repository root with any static HTTP server. The site has no build step and no third-party runtime dependency.

## Audio pairing

| Species | Test recording under `last_data/test/` | Site reference asset |
| --- | --- | --- |
| Hyena | `hyena/whoop/whoop_sample_1009.wav` | `audio/hyena-whoop-real.wav` |
| Meerkat | `meerkat/alarm_call/alarm_call_sample_408.wav` | `audio/meerkat-alarm-real.wav` |
| Marmoset | `marmoset/Phee/Phee_sample_1.wav` | `audio/marmoset-phee-real.wav` |
| Goat | `goat/Mother-kid reunion/Mother-kid reunion_sample_0.wav` | `audio/goat-reunion-real.wav` |
| Zebra | `zebra/quagga quagga/quagga quagga_sample_0.wav` | `audio/zebra-contact-real.wav` |
| Zebra finch | `zebrafinch/song/song_sample_1.wav` | `audio/zebra-finch-song-real.wav` |

Review whether these six current generated examples should remain or be replaced by curated final selections. A test recording matches its generated sample's species and vocalization type, but a behavioral prompt must not be presented as verified behavior in that individual recording.

Recommended filename pattern:

```text
{species}_{anchor}_{sample-id}_{system}.wav
```

For example: `hyena_whoop_001_event-aware.wav`.

## GitHub Pages

This repository is published directly from the root of the `main` branch. GitHub Pages keeps the public project URL unchanged when the page content is updated.
