# Mascot prompt: Otter im Papierboot ("zu neuen Ufern")

Alternative to `mascot.md` (Sprössling). Idea: "zu neuen Ufern aufbrechen". A small otter sits in a
paper boat folded from a sheet, the same paper as in the logo, and sets off toward a rising sun.
Target: 1024 × 1024 px, single character, plain background.
Output files: `design/assets/mascot-otter.jpg` (main pose) and `design/assets/mascot-otter-<pose>.jpg`.

## Character

- **Body:** a small round otter, soft shapes, warm brown (`#8A5A3C`) with a lighter cream belly and
  muzzle (`#F3E2C7`). Short tail, small round ears.
- **Face:** two simple dot eyes, small dark nose, a calm friendly smile. No teeth, no eyebrows.
- **Boat:** a white paper boat with one folded corner and a fold line in deep blue (`#2B5FAE`),
  floating on a few flat wave shapes in blue and light blue.
- **Sunrise:** a warm amber (`#F5A623`) half sun on the horizon behind it.
- **Personality:** curious, calm, optimistic. It sets off without hurry. It never makes light of the
  application process.
- **Rules:** a character, not a person. It never holds or shows real data, names or documents.

## Poses

| Pose | Use | Pose description |
|---|---|---|
| `neutral` | default, README | sitting upright in the boat, facing the viewer |
| `paddling` | getting started | one paw with a small paddle, boat slightly tilted forward |
| `lookout` | posting search | paw above the eyes, looking into the distance |
| `arriving` | release, success | standing in the boat, both paws raised, small amber sparkles |

## Prompt (generator-neutral)

```text
Cute flat vector mascot character on a plain off-white (#F7F9FC) background, centered, facing the
viewer. A small round otter with warm brown (#8A5A3C) fur, a cream (#F3E2C7) belly and muzzle, small
round ears, two simple black dot eyes, a small dark nose and a calm friendly smile, sitting upright in
a white paper boat folded from one sheet with a deep blue (#2B5FAE) fold line. The boat floats on a few
flat wave shapes in blue and light blue. Behind it a warm amber (#F5A623) half sun rises on the
horizon. Geometric rounded shapes, no outlines, no gradients, no texture. Friendly, calm, curious,
trustworthy. Character and boat fill about 70 percent of the canvas, readable at small sizes.
```

For another pose append `Pose: <pose description from the table>.` and keep everything else unchanged.
On Cloudflare use the chosen main image as `--ref-image` (model `flux-2-klein-4b`) for consistency.

## Negative prompt

```text
text, letters, numbers, watermark, human, hands, fingers, realistic, photo, 3D render, gradient,
glow, drop shadow, outline, anime, scary, angry, sad, clutter, multiple characters, motor, sail
```

## Gemini

Use the prompt as is, 1:1, 4 variants; append `Avoid: <negative prompt>`. For poses upload the chosen
main image and say "same character, new pose". See skill `nolte-media:gemini-image-handoff`.

## Midjourney

```text
cute flat vector mascot, small round brown otter with cream belly sitting in a white paper boat on
flat blue waves, amber half sun rising behind, off-white background, minimal, geometric
--ar 1:1 --style raw --stylize 100 --v 7 --no text, gradient, shadow, outline, human, photo
```

Pose variants: reuse the main image with `--cref <url> --cw 100`.

## Run record

| Date | Generator and version | Seed | Chosen file | Note |
|---|---|---|---|---|
| 2026-10-25 | Cloudflare Workers AI, flux-2-klein-4b | kein Seed (Provider ohne Seed-Angabe) | `mascot-otter.jpg` | 1024x1024, 3 Varianten, Nr. 3 gewählt (Pose neutral); Negativ-Prompt als `Avoid:` angehängt |
