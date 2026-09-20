# BeVo paper demo

Static project page for **Behavior-Conditioned Animal Vocalization Generation**.

## Current state

- Paper title, authors, affiliations, abstract summary, dataset statistics, method summary, and reported results are included.
- The supplied dataset overview, Event-Aware modeling figure, and AnimalCLAP t-SNE figure are included.
- Audio cards, paper/code/dataset links, anchors, durations, and example prompts are intentionally left as clearly labeled placeholders.

## Preview locally

Serve the `dist` directory with any static HTTP server. The site has no build step and no third-party runtime dependency.

## Add audio later

1. Put finalized audio files in `dist/audio/`.
2. Add each behavior prompt, anchor, duration, and audio source to the matching sample card in `dist/index.html`.
3. Replace a placeholder player with a native `<audio controls preload="none">` element or the shared player component added in a later pass.
4. Keep each compared system on the same prompt-duration pair.

Recommended filename pattern:

```text
{species}_{anchor}_{sample-id}_{system}.wav
```

For example: `hyena_whoop_001_event-aware.wav`.

## GitHub Pages

This repository is published directly from the root of the `main` branch. GitHub Pages keeps the public project URL unchanged when the page content is updated.
