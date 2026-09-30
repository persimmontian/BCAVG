# BeVo paper demo

Static project page for **Behavior-Conditioned Animal Vocalization Generation**.

## Current state

- Paper title, authors, affiliations, abstract summary, dataset statistics, method summary, and reported results are included.
- The supplied dataset overview, Event-Aware modeling figure, and AnimalCLAP t-SNE figure are included.
- Six playable fine-tuned baseline examples are included, one per species. Each tab shows the exact generation prompt, vocalization anchor, source sample filename, and duration from `cache/test_audio_manifest.json` in the supplied local project.
- The source inference files were converted from 44.1 kHz float WAV to 16-bit PCM WAV for browser playback. They are fine-tuned TangoFlux outputs from `outputs/test_inference`, not Event-Aware outputs.
- Matched real, Event-Aware, and zero-shot audio, along with paper/code/dataset links, are still awaiting source material.

## Preview locally

Serve the repository root with any static HTTP server. The site has no build step and no third-party runtime dependency.

## Add audio later

1. Put finalized audio files in `audio/`.
2. Add each behavior prompt, anchor, duration, source filename, and audio URL to the species entry in `script.js`.
3. Add matched real and Event-Aware files to the comparison cards in `index.html` once they are provided.
4. Keep each compared system on the same prompt-duration pair.

Recommended filename pattern:

```text
{species}_{anchor}_{sample-id}_{system}.wav
```

For example: `hyena_whoop_001_event-aware.wav`.

## GitHub Pages

This repository is published directly from the root of the `main` branch. GitHub Pages keeps the public project URL unchanged when the page content is updated.
