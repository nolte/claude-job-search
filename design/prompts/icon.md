# Icon prompt

Target: square app/plugin icon, 1024 × 1024 px, later scaled down to 512, 128 and 32 px.
Output file: `design/assets/icon.jpg` (and `icon.svg` after vectorising).

## Current version: paper boat ("zu neuen Ufern")

Replaces the sprout mark to match the otter mascot and the banner. The previous sprout version is kept as `icon-sprout.jpg`; its prompt follows below.

```text
Flat vector app icon, centered symbol on a solid deep blue (#2B5FAE) rounded-square background. Symbol: a white paper boat folded from one sheet, seen from the front, with a clear center fold line and one folded corner, floating on three flat wave shapes in light blue; behind the boat a warm amber (#F5A623) half sun rises from the waves as a simple semicircle. Geometric shapes, uniform rounded corners, no outlines, no gradients, no shadows, no texture. Flat colors only: white, light blue, amber on the deep blue. Symbol fills about 60 percent of the canvas, generous margin, perfectly centered, readable at 32 pixels. Optimistic, calm, trustworthy mood: setting off to new shores.
```

Negative prompt for this version:

```text
text, letters, numbers, watermark, people, animals, faces, hands, photo, 3D render, gradient, glow, drop shadow, bevel, outline, checkerboard pattern, busy background, sail, motor, multiple boats, multiple suns, frame
```

## Previous version: sprout (`icon-sprout.jpg`)

### Prompt (generator-neutral)

```text
Flat vector app icon, centered symbol on a solid deep blue (#2B5FAE) rounded-square background.
Symbol: a white sheet of paper with a small folded top-right corner; a slender green (#3DA35D)
sprout with exactly two symmetric leaves grows out of the upper edge of the sheet; behind the
sprout a half sun in warm amber (#F5A623) rises from the sheet's top edge, as a simple semicircle.
Geometric shapes, uniform rounded corners, no outlines, no gradients, no shadows, no texture.
Three flat accent colors only plus white. Symbol fills about 60 percent of the canvas, generous
margin, perfectly centered, readable at 32 pixels. Optimistic, calm, trustworthy mood: a fresh start.
```

## Negative prompt

```text
text, letters, numbers, watermark, people, faces, hands, photo, 3D render, gradient, glow,
drop shadow, bevel, checkerboard pattern, busy background, extra leaves, multiple suns, frame
```

## Gemini

Use the prompt above as is. Ask for "1:1, 4 variants". Gemini has no negative prompt field:
append `Avoid: <negative prompt>` to the end of the prompt. See skill `nolte-media:gemini-image-handoff`.

## Midjourney

```text
flat vector app icon, white paper sheet with folded corner, green two-leaf sprout growing from it,
amber half sun rising behind, solid deep blue rounded square background, geometric, minimal,
three accent colors, centered --ar 1:1 --style raw --stylize 50 --v 7 --no text, gradient, shadow, photo, people
```

Pin `--seed <n>` once a good result is found and record it below.

## Run record

| Date | Generator and version | Seed | Chosen file | Note |
|---|---|---|---|---|
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed (Provider ohne Seed-Angabe) | `icon-sprout.jpg` | 1024x1024, 2 Varianten, Nr. 1 gewählt (hat drei statt zwei Blätter); Negativ-Prompt als `Avoid:` angehängt |
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed | `icon.jpg` | Papierboot-Version, 1024x1024, 3 Varianten, Nr. 2 gewählt |
