# BeVo paper demo

Static project page for **Behavior-Conditioned Animal Vocalization Generation**.

## Current state

- Paper title, authors, affiliations, abstract summary, dataset statistics, method summary, and reported results are included.
- The supplied dataset overview, Event-Aware modeling figure, and AnimalCLAP t-SNE figure are included.
- The listening panel shows only real reference audio and the selected final Event-Aware model output. Both are clearly marked as awaiting audio until matching files are supplied.
- Species tabs show provisional demonstration prompts and vocalization anchors. The final prompt-to-audio pairings must be confirmed before publication.
- Earlier fine-tuned baseline WAV files remain in `audio/` as unused repository assets; they are not displayed or represented as final-model outputs.
- Paper/code/dataset links are still awaiting source material.

## Preview locally

Serve the repository root with any static HTTP server. The site has no build step and no third-party runtime dependency.

## Add audio later

1. Put finalized audio files in `audio/`.
2. Confirm each demonstration prompt and vocalization anchor in `script.js` against the selected final-model output.
3. Add the matched real-reference and final Event-Aware audio URLs to the two cards in `index.html` and connect them to the species tabs in `script.js`.
4. Keep the pairing scientifically accurate: the real recording should match species and vocalization type, but must not be described as exhibiting a specific behavior unless that behavior is verified.

Recommended filename pattern:

```text
{species}_{anchor}_{sample-id}_{system}.wav
```

For example: `hyena_whoop_001_event-aware.wav`.

## GitHub Pages

This repository is published directly from the root of the `main` branch. GitHub Pages keeps the public project URL unchanged when the page content is updated.
