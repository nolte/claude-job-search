#!/usr/bin/env python3
"""Set the wordmark onto the banner art (design/assets/banner-art.jpg -> banner.jpg).

The image model draws scene and mascot only; text is set here so it stays exact.
Needs Pillow and Liberation Sans (Debian/Ubuntu: fonts-liberation).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path("/usr/share/fonts/truetype/liberation")
TITLE, SUBTITLE = "claude-job-search", "Bewerbungsunterlagen mit Claude Code"
NAVY, BLUE = "#1B3A6B", "#2B5FAE"
X, TITLE_SIZE, SUB_SIZE, GAP = 780, 100, 42, 26


def main() -> None:
    root = Path(__file__).resolve().parent.parent / "assets"
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--art", type=Path, default=root / "banner-art.jpg")
    ap.add_argument("--out", type=Path, default=root / "banner.jpg")
    args = ap.parse_args()

    img = Image.open(args.art).convert("RGB")
    draw = ImageDraw.Draw(img)
    title = ImageFont.truetype(str(FONTS / "LiberationSans-Bold.ttf"), TITLE_SIZE)
    sub = ImageFont.truetype(str(FONTS / "LiberationSans-Regular.ttf"), SUB_SIZE)
    t_box = draw.textbbox((0, 0), TITLE, font=title)
    s_box = draw.textbbox((0, 0), SUBTITLE, font=sub)
    block = (t_box[3] - t_box[1]) + GAP + (s_box[3] - s_box[1])
    y = (img.height * 0.70 - block) / 2  # centre above the waves
    draw.text((X - t_box[0], y - t_box[1]), TITLE, font=title, fill=NAVY)
    y2 = y + (t_box[3] - t_box[1]) + GAP
    draw.text((X - s_box[0], y2 - s_box[1]), SUBTITLE, font=sub, fill=BLUE)
    img.save(args.out, quality=95)


if __name__ == "__main__":
    main()
