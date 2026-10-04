# BeVo paper demo

Static project page for **Behavior-Conditioned Animal Vocalization Generation**.

## Current state

- Paper title, authors, affiliations, abstract summary, dataset statistics, method summary, and reported results are included.
- The supplied dataset overview, Event-Aware modeling figure, and AnimalCLAP t-SNE figure are included.
- The listening panel shows only real reference audio and the final Event-Aware model output. Six current final-model examples are playable; matched real recordings are still awaiting audio.
- Species tabs show the exact test-manifest prompts paired with these outputs. These six examples are representative current selections, not a curated "best of" set.
- The WAV files in `audio/` are browser-compatible PCM copies of outputs from `outputs/test_inference`; the inference script uses the trained `outputs/all_animals/checkpoints/best.safetensors` checkpoint. The script's generic `finetuned_checkpoint` argument does not mean these are the separate fine-tuned baseline results in the paper's comparison table.
- Paper/code/dataset links are still awaiting source material.

## Preview locally

Serve the repository root with any static HTTP server. The site has no build step and no third-party runtime dependency.

## Add audio later

1. Add matched real-reference recordings to `audio/` and connect the A player to the species tabs.
2. Review whether these six current generated examples should remain or be replaced by curated final selections.
3. Keep the pairing scientifically accurate: the real recording should match species and vocalization type, but must not be described as exhibiting a specific behavior unless that behavior is verified.

Recommended filename pattern:

```text
{species}_{anchor}_{sample-id}_{system}.wav
```

For example: `hyena_whoop_001_event-aware.wav`.

## GitHub Pages

This repository is published directly from the root of the `main` branch. GitHub Pages keeps the public project URL unchanged when the page content is updated.
