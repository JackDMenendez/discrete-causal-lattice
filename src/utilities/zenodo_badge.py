"""
zenodo_badge.py
Render a Zenodo-style DOI badge as a PNG for inclusion on the paper's
title page.  Pure-PIL implementation so no SVG-to-PDF toolchain is
required.  Re-run this script if the DOI or Zenodo identifier changes.

Output: paper/figures/zenodo_doi_badge.png
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT  = os.path.join(ROOT, "paper", "figures", "zenodo_doi_badge.png")

# --- Configuration matches the live Zenodo badge -----------------------------
LABEL_TEXT = "DOI"
VALUE_TEXT = "10.5281/zenodo.19866911"

# Zenodo's badge palette (sampled from the live SVG)
LABEL_BG = (85, 85, 85)        # #555 dark grey
VALUE_BG = (0, 126, 198)       # #007ec6 brand blue
TEXT_FG  = (255, 255, 255)
SHADOW   = (1, 1, 1, 64)       # 25% black for the bottom drop shadow

FONT_NAME = "arial.ttf"
FONT_SIZE = 32                 # render at high resolution then scale down
PAD_X     = 14                 # horizontal padding inside each segment
PAD_Y     = 8                  # vertical padding
GAP       = 0                  # segments butt against each other (no gap)
SCALE     = 4                  # supersample factor for crisp downscaling


def _measure(draw: ImageDraw.ImageDraw, text: str,
             font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def render() -> str:
    font = ImageFont.truetype(FONT_NAME, FONT_SIZE * SCALE)
    tmp  = Image.new("RGBA", (10, 10))
    d    = ImageDraw.Draw(tmp)

    label_w, label_h = _measure(d, LABEL_TEXT, font)
    value_w, value_h = _measure(d, VALUE_TEXT, font)
    text_h = max(label_h, value_h)
    seg_h  = text_h + 2 * PAD_Y * SCALE
    label_seg_w = label_w + 2 * PAD_X * SCALE
    value_seg_w = value_w + 2 * PAD_X * SCALE
    total_w = label_seg_w + value_seg_w + GAP * SCALE
    total_h = seg_h

    img = Image.new("RGBA", (total_w, total_h), (255, 255, 255, 0))
    d   = ImageDraw.Draw(img)

    # Two flat segments (Zenodo's actual badge is flat-style, not rounded pill)
    d.rectangle([(0, 0), (label_seg_w, total_h)], fill=LABEL_BG)
    d.rectangle([(label_seg_w + GAP * SCALE, 0),
                 (total_w, total_h)], fill=VALUE_BG)

    # Centered text in each segment
    label_x = (label_seg_w - label_w) // 2
    label_y = (total_h - text_h) // 2 - 2 * SCALE
    d.text((label_x, label_y), LABEL_TEXT, font=font, fill=TEXT_FG)

    value_x = label_seg_w + GAP * SCALE + (value_seg_w - value_w) // 2
    value_y = (total_h - text_h) // 2 - 2 * SCALE
    d.text((value_x, value_y), VALUE_TEXT, font=font, fill=TEXT_FG)

    # Downsample for sharpness
    final_size = (total_w // SCALE, total_h // SCALE)
    img = img.resize(final_size, Image.LANCZOS)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG")
    return OUT


if __name__ == "__main__":
    path = render()
    print(f"Wrote {path}")
