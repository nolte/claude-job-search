# Logo prompt

Target: horizontal logo for README and docs header, 2400 × 800 px (3:1). The model draws only
the mark; the wordmark "claude-job-search" is set as live text next to it (see `design/README.md`).
Output files: `design/assets/logo.jpg`, `logo.svg` (vectorised, transparent background).

## Current version: paper boat ("zu neuen Ufern")

Replaces the sprout mark to match the otter mascot and the banner. The previous sprout version is kept as `logo-sprout.jpg`; its prompt follows below.

```text
Flat vector logo mark on a plain off-white (#F7F9FC) background, mark placed on the left third of a wide canvas, the right two thirds left empty. Mark: a white paper boat with deep blue (#2B5FAE) fold lines, folded from one sheet, seen from the front, floating on three flat wave shapes in blue and light blue; behind the boat a warm amber (#F5A623) half sun rises from the waves as a simple semicircle. Geometric shapes, uniform rounded corners, no outlines, no gradients, no shadows, no texture. Three flat accent colors only. Clean, optimistic, calm, trustworthy: setting off to new shores. Works in one color and at small sizes.
```

Negative prompt for this version:

```text
text, letters, numbers, watermark, people, animals, faces, hands, photo, 3D render, gradient, glow, drop shadow, bevel, outline, checkerboard pattern, busy background, sail, motor, multiple boats, multiple suns, frame
```

## Previous version: sprout (`logo-sprout.jpg`)

### Prompt (generator-neutral)

```text
Flat vector logo mark on a plain off-white (#F7F9FC) background, mark placed on the left third of
a wide canvas, the right two thirds left empty. Mark: a rounded sheet of paper in deep blue
(#2B5FAE) with a small folded top-right corner; a slender green (#3DA35D) sprout with exactly two
symmetric leaves grows out of the upper edge of the sheet; behind the sprout a half sun in warm
amber (#F5A623) rises as a simple semicircle. Geometric shapes, uniform rounded corners, no
outlines, no gradients, no shadows, no texture. Three flat accent colors only. Clean, optimistic,
calm, trustworthy: a fresh start. Works in one color and at small sizes.
```

## Negative prompt

```text
text, letters, typography, numbers, watermark, people, faces, hands, photo, 3D render, gradient,
glow, drop shadow, bevel, checkerboard pattern, busy background, extra leaves, multiple suns
```

## Gemini

Use the prompt as is, aspect ratio 3:1 (or 16:9 and crop), 4 variants. Append
`Avoid: <negative prompt>`. See skill `nolte-media:gemini-image-handoff`.

## Midjourney

```text
flat vector logo mark, deep blue paper sheet with folded corner, green two-leaf sprout growing
from it, amber half sun rising behind, off-white background, mark on the left, empty space on the
right, geometric, minimal --ar 3:1 --style raw --stylize 50 --v 7 --no text, gradient, shadow, photo, people
```

## Variant: dark mode

Same prompt; replace the background with deep navy `#0F1B33` and the sheet with off-white
`#F7F9FC`. Output file: `logo-dark.jpg`.

## Run record

| Date | Generator and version | Seed | Chosen file | Note |
|---|---|---|---|---|
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed (Provider ohne Seed-Angabe) | `logo-sprout.jpg` | 1920x640, 2 Varianten, Nr. 2 gewählt; Negativ-Prompt als `Avoid:` angehängt |
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed | `logo.jpg` | Papierboot-Version, 1920x640, 3 Varianten, Nr. 1 gewählt |
