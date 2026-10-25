# README banner prompt

Target: wide banner at the top of `README.md` and the docs landing page, 2400 × 600 px (4:1).
Output files: `design/assets/banner-art.jpg` (model output), `banner.jpg` (with wordmark), later `banner-dark.jpg`.
The model draws scene and mascot only and writes `design/assets/banner-art.jpg`; title and tagline are set on
top by `design/scripts/add_wordmark.py`, which writes the final `design/assets/banner.jpg` (see `design/README.md`).

## Prompt (generator-neutral)

```text
Wide flat vector banner illustration, calm sunrise landscape, off-white (#F7F9FC) sky fading to
nothing, no gradients. Left third: the project mark, a deep blue (#2B5FAE) paper sheet with folded
top-right corner and a slender green (#3DA35D) two-leaf sprout growing out of it, an amber (#F5A623)
half sun rising behind. Across the bottom, a low horizon of two or three simple rolling hills in
overlapping flat tones of blue and light blue. The right two thirds stay mostly empty for the
title text, with only a few small amber and light-blue dots as subtle sparkle. Geometric shapes,
rounded corners, no outlines, no shadows, no texture. Optimistic, calm, trustworthy: a fresh start.
```

## Current version: otter in a paper boat

`design/assets/banner-art.jpg` (and with wordmark `banner.jpg`) uses the otter mascot (`mascot-otter.md`) instead of the sprout mark. Generated on
Cloudflare (`flux-2-klein-4b`, 1920 × 480) with `mascot-otter.jpg` downscaled to 512 × 512 as `--ref-image`
(the endpoint wants references under 512 × 512) and this prompt:

```text
Wide flat vector banner illustration on an off-white (#F7F9FC) sky, no gradients. Left third: the exact
character from the reference image, a small round brown otter with cream belly sitting in a white paper boat with a deep blue
fold line, on flat blue waves, with a warm amber half sun rising behind it. Keep the character, boat and colors identical to
the reference. Across the bottom a low horizon of two or three simple rolling hills and waves in overlapping flat tones of blue and
light blue. The right two thirds stay mostly empty for title text, with only a few small amber and light-blue dots as subtle
sparkle. Geometric shapes, rounded corners, no outlines, no shadows, no texture. Optimistic, calm, trustworthy: setting off to new shores.
Avoid: text, letters, typography, numbers, watermark, human, photo, 3D render, gradient, glow, drop shadow, outline, clutter on the right side, multiple characters.
```

The earlier sprout version stays as `banner-sprout.jpg` (prompt above).

## Negative prompt

```text
text, letters, typography, numbers, watermark, people, faces, hands, photo, 3D render, gradient,
glow, drop shadow, checkerboard pattern, busy background, clutter on the right side
```

## Gemini

Use the prompt as is, aspect ratio 4:1 (or 16:9 and crop to 4:1), 4 variants. Append
`Avoid: <negative prompt>`. See skill `nolte-media:gemini-image-handoff`.

## Midjourney

```text
flat vector banner, sunrise over soft hills, deep blue paper sheet with green two-leaf sprout and
amber half sun on the left, empty space on the right, off-white background, geometric, minimal
--ar 4:1 --style raw --stylize 50 --v 7 --no text, gradient, shadow, photo, people
```

## Variant: dark mode

Replace the sky with deep navy `#0F1B33`, the sheet with off-white `#F7F9FC`, and lighten the hills.
Output file: `banner-dark.jpg`.

## README embedding (after a result is committed)

```markdown
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="design/assets/banner-dark.jpg">
  <img alt="claude-job-search" src="design/assets/banner.jpg">
</picture>
```

## Run record

| Date | Generator and version | Seed | Chosen file | Note |
|---|---|---|---|---|
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed (Provider ohne Seed-Angabe) | `banner-sprout.jpg` | 1920x480, 2 Varianten, Nr. 1 gewählt; Negativ-Prompt als `Avoid:` angehängt |
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed | `banner-art.jpg` | Otter-Version, Referenz `mascot-otter.jpg` (512x512), 3 Varianten, Nr. 1 gewählt |
