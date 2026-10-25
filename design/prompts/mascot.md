# Mascot prompt: "Sprössling"

Target: a friendly character for the docs, release notes and empty states. 1024 × 1024 px,
single character, plain background. Output files: `design/assets/mascot.jpg` (main pose) and
`design/assets/mascot-<pose>.jpg` for the poses below.

## Character

Sprössling is a small sprout that grew out of a sheet of paper, the same motif as the logo.

- **Body:** a rounded, upright seedling bulb in fresh green (`#3DA35D`) with two leaf "ears" on
  top. Round and soft, about as wide as tall.
- **Face:** two simple dot eyes and a small calm smile. No mouth detail, no teeth, no eyebrows.
- **Base:** it stands on a white sheet of paper with a folded corner (deep blue `#2B5FAE` shadow
  line), like a pot. A small amber (`#F5A623`) half sun glows behind it.
- **Personality:** patient, encouraging, quietly optimistic. Never pushy or comic. It supports
  the user in a serious process (job applications) without making light of it.
- **Rules:** it is a character, not a person. It never holds or shows real data, names or documents.

## Poses (consistency set)

| Pose | Use | Pose description |
|---|---|---|
| `neutral` | default, README | standing, facing the viewer, leaves relaxed |
| `waving` | getting started | one leaf raised like a wave |
| `reading` | posting analysis | looking down at a small blank page |
| `celebrating` | release, successful export | both leaves up, small amber sparkles |

## Prompt (generator-neutral)

```text
Cute flat vector mascot character on a plain off-white (#F7F9FC) background, centered, full body,
facing the viewer. A small round green (#3DA35D) sprout character with two leaf-shaped ears, two
simple black dot eyes and a small calm smile, standing on a white sheet of paper with a folded
corner, a warm amber (#F5A623) half sun glowing behind it. Deep blue (#2B5FAE) used only for the
paper's fold line and a soft contact shadow. Geometric rounded shapes, thick uniform proportions,
no outlines, no gradients, no texture. Friendly, calm, encouraging, trustworthy. Pose: standing
neutral, leaves relaxed. Character fills about 70 percent of the canvas, readable at small sizes.
```

For another pose replace the last sentences with `Pose: <pose description from the table>.` and
keep everything else unchanged. Use the same seed or, on Cloudflare, the main image as `--ref-image`
(model `flux-2-klein-4b`) so the character stays consistent.

## Negative prompt

```text
text, letters, numbers, watermark, human, hands, fingers, realistic, photo, 3D render, gradient,
glow, drop shadow, outline, anime, scary, angry, sad, clutter, multiple characters, extra leaves
```

## Gemini

Use the prompt as is, 1:1, 4 variants; append `Avoid: <negative prompt>`. For poses upload the
chosen main image and say "same character, new pose". See skill `nolte-media:gemini-image-handoff`.

## Midjourney

```text
cute flat vector mascot, round green sprout character with two leaf ears and dot eyes, standing on
white paper sheet with folded corner, amber half sun behind, off-white background, minimal, geometric
--ar 1:1 --style raw --stylize 100 --v 7 --no text, gradient, shadow, outline, human, photo
```

Pose variants: reuse the main image with `--cref <url> --cw 100`.

## Run record

| Date | Generator and version | Seed | Chosen file | Note |
|---|---|---|---|---|
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed (Provider ohne Seed-Angabe) | `mascot.jpg` | 1024x1024, 3 Varianten, Nr. 1 gewählt (Pose neutral); Negativ-Prompt als `Avoid:` angehängt |
