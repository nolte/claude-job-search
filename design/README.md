# Design: logo and icon

Source of truth for the visual identity of `claude-job-search`. The images are generated from
the prompts in `prompts/`; this folder holds everything needed to generate them again.

## Concept: Neuanfang, zu neuen Ufern

A job application marks a fresh start, "zu neuen Ufern aufbrechen". The mark combines three elements and nothing else:

1. **A paper boat** folded from one sheet of paper (the *Bewerbungsunterlagen*), seen from the front.
2. **Flat waves** under the boat (the crossing).
3. **A half sun on the horizon** behind the boat (sunrise, a new day).

The mascot is an otter in the paper boat (`prompts/mascot-otter.md`); the banner shows it. The
earlier sprout concept (paper sheet with a sprout) stays as `*-sprout.jpg` and in `prompts/mascot.md`.

No text, no people, no company or product marks. The shapes stay flat and geometric so the mark
still reads at 16 px.

## Palette

Tokens match the MkDocs theme (`primary: blue`, `accent: light blue`) plus accents. The sprout green is used only by the earlier sprout version; the otter adds a brown (`#8A5A3C`) and cream (`#F3E2C7`).

| Role | Name | Hex |
|---|---|---|
| Primary (sheet, outline) | Deep blue | `#2B5FAE` |
| Sunrise | Warm amber | `#F5A623` |
| Sprout | Fresh green | `#3DA35D` |
| Background (logo) | Off-white | `#F7F9FC` |

## Files

| File | Purpose |
|---|---|
| `prompts/logo.md` | Wide logo (paper boat mark plus space for the wordmark); sprout version kept below |
| `prompts/icon.md` | Square icon (paper boat); sprout version kept below |
| `prompts/banner.md` | Wide README banner (4:1) with dark variant and embedding snippet |
| `prompts/mascot.md` | Mascot "Sprössling": character description, pose set, consistency notes |
| `prompts/mascot-otter.md` | Alternative mascot: otter in a paper boat ("zu neuen Ufern") |
| `scripts/add_wordmark.py` | Sets title and tagline onto `assets/banner-art.jpg`, writes `assets/banner.jpg` |
| `assets/` | Chosen results (`logo.jpg`, `icon.jpg`, `banner.jpg`, plus `.meta.json` sidecars with the exact prompt); created when you commit a result |

## Reproducibility

Image models are not deterministic. Reproducibility here means: same prompt text, same model
and settings, and the chosen result committed under `assets/`. After each generation, fill in
the **Run record** at the bottom of the prompt file (model, version, date, seed if the tool
gives one, file name of the chosen result). Change a prompt only together with a new run record.

## Workflow

1. Generate 4 variants with the prompt of the file (Gemini or Midjourney section).
2. Pick one; if it has a fake checkerboard background, run the `nolte-media:png-to-transparent-svg` agent on it.
3. Save under `assets/` using the file names in the prompt file; fill in the run record.
4. Wordmark ("claude-job-search") is never rendered by the model. The banner is composed from `assets/banner-art.jpg` (scene and mascot only) and the text by `python3 -I design/scripts/add_wordmark.py`, which writes `assets/banner.jpg`. It needs Pillow and Liberation Sans (`fonts-liberation`).
