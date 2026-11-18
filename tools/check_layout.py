#!/usr/bin/env python3
"""Layout lint for the 17 Nov entry: no text may be cut off.

Checks every headline/body/one-liner against the exact font, size and
box width used in build_image.py. Exit 1 if anything would wrap past
its allowed line count (the [:N] slices in build_image.py would drop
words). Run: python3 tools/check_layout.py
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)            # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)        # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)              # noqa: E731


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    mx = 28
    hw = (W - 2 * mx - 14) // 2
    cw = (W - 2 * mx - 4 * 12) / 5
    fails = []

    def check(label, text, fnt, width, max_lines):
        n = len(wrap(d, text, fnt, width))
        status = "OK " if n <= max_lines else "FAIL"
        print(f"{status} {label}: {n}/{max_lines} lines: {text!r}")
        if n > max_lines:
            fails.append(label)

    hero_specs = [(SERIF_B(20), 591 - 20, 2, SERIF(13), 1),
                  (SERIF_B(17), 349 - 20, 2, SERIF(12), 1)]
    for i, hero in enumerate(data["heroes"]):
        hf, hw2, hm, bf, bm = hero_specs[i]
        check(f"hero{i+1} headline", hero["headline"], hf, hw2, hm)
        check(f"hero{i+1} body", hero["body"], bf, hw2, bm)
    for i, card in enumerate(data["cards"]):
        check(f"card{i+3} headline", card["headline"], SERIF_B(13), cw - 16, 2)
        check(f"card{i+3} body", card["body"], SANS(10), cw - 16, 1)
    list_w = W - mx - (mx + 482)
    col_w = (list_w - 20) / 2
    for i, item in enumerate(data["also_on"]):
        num = "%d." % (i + 13)
        avail = col_w - d.textlength(num, font=SANS_B(10)) - 12
        check(f"also-on{i+13}", item, SANS(10), avail, 1)
    if fails:
        print(f"\n{len(fails)} FAILURES: {fails}")
        return 1
    print("\nALL LAYOUT CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
