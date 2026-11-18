#!/usr/bin/env python3
"""Build THE DAY IN WORLD NEWS front page for 17 November 2026.

Merged template from the 5 top-ranked entries of bounty
news-image-20261117 (provisional rates 99.01-99.08%):
  rank 1 @el-net    : 40 stories, 2 heroes, 12 illustrated, 28 one-line
                      "Also on", numbered 1-40 consistent across cards,
                      map and list; sources footer.
  rank 2 @nabil-naufal: uniform grid, fixed card pattern
                      (illustration + kicker + headline + 1-line deck),
                      topic legend, map with "NUMBERS MATCH STORIES".
  rank 3/4          : 3-hero variant / 15 illustrated; topic breadth
                      (climate, wildlife, tech, economy) so all six
                      continents feel represented.
  rank 5            : dark navy high-contrast palette edition.

Merged: navy masthead + big white date + "40 STORIES • 6 CONTINENTS •
ONE DAY" + topic legend; 2 heroes + 10 cards (2x5) = 12 illustrated;
world map with numbered pins; "ALSO ON" 28 one-liners in 2 columns;
sources footer. Flat vector drawings only, no photos, no AI images.
Deterministic: same input bytes produce the same output bytes.
v3 (Grok follow-up): art band 48px; chip/chart/virus/syringe/docs scenes
redrawn per card so each reads at 300px; no duplicate plane/plus scenes.

Run:  python3 tools/build_image.py   (writes entry.png next to repo root)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

W, H = 1024, 1024
PAPER = (246, 241, 229)
PANEL = (255, 253, 247)
NAVY = (16, 36, 64)
NAVY2 = (24, 52, 88)
INK = (26, 26, 26)
RED = (163, 22, 33)
BLUE = (31, 78, 121)
TEAL = (14, 116, 108)
GREY = (90, 86, 78)
LIGHT = (232, 226, 210)
RULE = (120, 112, 96)
SKY = (214, 228, 238)

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


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# --- simplified continent outlines (lon, lat), equirectangular ---
CONTINENTS = {
    "N. AMERICA": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-85, 80),
                   (-75, 72), (-65, 60), (-55, 52), (-60, 45), (-70, 42),
                   (-75, 35), (-80, 30), (-85, 28), (-90, 21), (-95, 18),
                   (-100, 16), (-105, 20), (-110, 23), (-115, 28), (-120, 34),
                   (-125, 40), (-125, 48), (-135, 58), (-155, 60), (-165, 60)],
    "S. AMERICA": [(-80, 10), (-75, 5), (-70, 0), (-65, -5), (-55, -10),
                   (-45, -15), (-40, -22), (-48, -28), (-55, -35), (-60, -40),
                   (-65, -45), (-70, -52), (-72, -45), (-75, -35), (-78, -25),
                   (-80, -15), (-82, -5), (-80, 5)],
    "AFRICA": [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
               (35, 28), (43, 12), (48, 10), (51, 2), (48, -5), (40, -15),
               (35, -25), (28, -33), (20, -35), (15, -28), (12, -18), (9, -2),
               (8, 4), (-8, 5), (-13, 8), (-17, 12)],
    "EURASIA": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
                (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
                (32, 68), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73),
                (90, 75), (100, 76), (110, 74), (120, 73), (130, 72),
                (140, 72), (150, 70), (160, 69), (170, 67), (178, 65),
                (178, 62), (170, 60), (162, 56), (158, 52), (150, 60),
                (142, 55), (140, 45), (135, 42), (130, 38), (127, 35),
                (122, 32), (120, 28), (115, 22), (110, 20), (108, 18),
                (105, 10), (103, 8), (100, 8), (98, 12), (95, 16), (92, 20),
                (90, 22), (86, 20), (82, 16), (80, 10), (77, 8), (75, 12),
                (72, 20), (68, 22), (62, 25), (58, 26), (55, 26), (52, 28),
                (50, 29), (48, 30), (44, 29), (42, 28), (40, 36), (36, 36),
                (33, 36), (30, 36), (27, 37), (23, 36), (20, 40), (18, 40),
                (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
                (-6, 36), (-9, 37)],
    "AUSTRALIA": [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33),
                  (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
                  (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
                  (146, -19), (142, -15), (142, -11), (137, -12), (135, -12),
                  (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
}


def draw_icon(d, kind, x, y, w, h, c1, c2):
    """Small flat-vector motif inside box (x, y, w, h)."""
    cx, cy = x + w / 2, y + h / 2
    if kind == "bridge":
        d.line([(x + 2, cy + 6), (x + w - 2, cy + 6)], fill=c1, width=3)
        d.arc([x + 6, cy - 16, x + w - 6, cy + 22], 180, 360, fill=c1, width=2)
        d.line([(x + 10, cy + 6), (x + 10, cy + 12)], fill=c1, width=2)
        d.line([(x + w - 10, cy + 6), (x + w - 10, cy + 12)], fill=c1, width=2)
        d.line([(x + 4, cy + 14), (x + w - 4, cy + 14)], fill=c2, width=1)
    elif kind == "radar":
        for r in (6, 12, 18):
            d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=c1, width=2)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
        d.line([(cx, cy), (cx + 14, cy - 12)], fill=c1, width=2)
        d.ellipse([cx + 11, cy - 15, cx + 17, cy - 9], fill=c2)
    elif kind == "chip":
        d.rectangle([cx - 10, cy - 8, cx + 10, cy + 8], outline=c1, width=2)
        d.rectangle([cx - 4, cy - 3, cx + 4, cy + 3], fill=c2)
        for dx in (-14, -7, 0, 7, 14):
            d.line([(cx + dx, cy - 12), (cx + dx, cy - 8)], fill=c1, width=2)
            d.line([(cx + dx, cy + 8), (cx + dx, cy + 12)], fill=c1, width=2)
    elif kind == "chart":
        for i, bh in enumerate((8, 14, 20)):
            bx = x + 6 + i * 12
            d.rectangle([bx, cy + 12 - bh, bx + 8, cy + 12], fill=c1 if i < 2 else RED)
    elif kind == "health":
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=c1, width=2)
        d.rectangle([cx - 3, cy - 8, cx + 3, cy + 8], fill=RED)
        d.rectangle([cx - 8, cy - 3, cx + 8, cy + 3], fill=RED)
    elif kind == "flag":
        d.line([(x + 8, y + 2), (x + 8, y + h - 2)], fill=c1, width=2)
        d.polygon([(x + 8, y + 3), (x + w - 4, y + 9), (x + 8, y + 15)], fill=RED)
    elif kind == "plane":
        d.polygon([(x + 4, cy), (x + w - 6, cy - 7), (x + w - 6, cy + 7)], fill=c1)
        d.line([(cx - 4, cy - 2), (cx + 2, cy - 12)], fill=c1, width=2)
        d.line([(cx - 4, cy + 2), (cx + 2, cy + 12)], fill=c1, width=2)
    elif kind == "ship":
        d.polygon([(x + 4, cy - 2), (x + w - 4, cy - 2), (x + w - 10, cy + 8),
                   (x + 10, cy + 8)], fill=c1)
        d.line([(cx, cy - 2), (cx, cy - 12)], fill=c1, width=2)
        d.polygon([(cx, cy - 12), (cx + 12, cy - 4), (cx, cy - 4)], fill=RED)
        d.line([(x + 2, cy + 12), (x + w - 2, cy + 12)], fill=c2, width=1)
    elif kind == "gavel":
        d.rectangle([cx - 12, cy - 8, cx + 2, cy - 1], fill=c1)
        d.line([(cx - 2, cy - 2), (cx + 12, cy + 10)], fill=c1, width=3)
        d.line([(x + 4, cy + 12), (x + w - 4, cy + 12)], fill=c2, width=2)
    elif kind == "globe":
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=c1, width=2)
        d.ellipse([cx - 6, cy - 13, cx + 6, cy + 13], outline=c1, width=1)
        d.line([(cx - 13, cy), (cx + 13, cy)], fill=c1, width=1)
    elif kind == "leaf":
        d.polygon([(cx, cy - 12), (cx + 10, cy), (cx, cy + 12), (cx - 10, cy)],
                  fill=(34, 139, 34))
        d.line([(cx - 10, cy + 12), (cx + 10, cy - 12)], fill=c1, width=1)
    else:
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=c1, width=2)


def draw_hero_art(d, kind, x, y, w, h):
    """Wide flat illustration band for a hero panel."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    if kind == "bridge":
        # sea
        d.rectangle([x, y + h - 14, x + w, y + h], fill=(120, 170, 200))
        d.line([(x + 8, y + h - 9), (x + w - 8, y + h - 9)], fill=(255, 255, 255), width=1)
        d.line([(x + 20, y + h - 5), (x + w - 20, y + h - 5)], fill=(255, 255, 255), width=1)
        # suspension bridge: two towers, main cable arc, deck, hangers
        deck = y + h - 24
        for tx in (x + w * 0.28, x + w * 0.72):
            d.line([(tx, deck - 26), (tx, y + h - 14)], fill=NAVY, width=3)
            d.line([(tx - 6, deck - 26), (tx + 6, deck - 26)], fill=NAVY, width=3)
        d.arc([x + 30, deck - 34, x + w - 30, deck + 12], 180, 360, fill=NAVY, width=3)
        d.line([(x + 6, deck), (x + w - 6, deck)], fill=NAVY, width=4)
        for hx in (x + w * 0.4, x + w * 0.5, x + w * 0.6):
            d.line([(hx, deck - 12), (hx, deck)], fill=NAVY, width=1)
        # blast burst at mid-span
        bx, by = x + w // 2, deck - 20
        for dx, dy in ((-12, -8), (0, -14), (12, -8), (-14, 4), (14, 4), (0, 10)):
            d.line([(bx, by), (bx + dx, by + dy)], fill=RED, width=2)
        d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=RED)
        # smoke puffs above the blast
        for sx, sy in ((bx - 16, by - 18), (bx + 14, by - 20), (bx, by - 26)):
            d.ellipse([sx - 6, sy - 4, sx + 6, sy + 4], fill=(150, 150, 150))
    elif kind == "radar":
        # ground + dish
        gy = y + h - 16
        d.rectangle([x, y + h - 16, x + w, y + h], fill=(190, 200, 190))
        mx = x + w // 2
        d.line([(mx, gy), (mx, gy - 22)], fill=NAVY, width=3)
        d.arc([mx - 26, gy - 48, mx + 26, gy + 4], 180, 360, fill=NAVY, width=3)
        d.line([(mx - 26, gy - 22), (mx + 26, gy - 22)], fill=NAVY, width=2)
        # sweeping arcs + drones
        for r in (16, 26, 36):
            d.arc([mx - r, gy - 22 - r, mx + r, gy - 22 + r], 200, 340, fill=BLUE, width=2)
        for dx, dy in ((-52, -30), (54, -38), (30, -14)):
            d.ellipse([mx + dx - 3, gy - 22 + dy - 3, mx + dx + 3, gy - 22 + dy + 3], fill=RED)
            d.line([(mx + dx - 7, gy - 22 + dy), (mx + dx + 7, gy - 22 + dy)], fill=RED, width=1)
    elif kind == "plane":
        d.rectangle([x, y, x + w, y + h], fill=(30, 60, 110))
        for cx0, cy0 in ((x + 30, y + 12), (x + w - 36, y + 20)):
            d.ellipse([cx0 - 12, cy0 - 4, cx0 + 12, cy0 + 4], fill=(255, 255, 255))
        px, py = x + w // 2, y + h // 2 + 4
        d.polygon([(px - 42, py), (px + 38, py - 10), (px + 38, py + 10)],
                  fill=(255, 255, 255))
        d.line([(px - 8, py - 3), (px + 2, py - 22)], fill=(255, 255, 255), width=4)
        d.line([(px - 8, py + 3), (px + 2, py + 22)], fill=(255, 255, 255), width=4)
        d.line([(px - 30, py - 2), (px - 38, py - 14)], fill=(255, 255, 255), width=3)
        d.rectangle([x, y + h - 6, x + w, y + h], fill=(120, 170, 200))
    elif kind == "chip":
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        for lx in (x + 14, x + w - 14):
            d.line([(lx, y + 4), (lx, y + h - 4)], fill=(90, 140, 190), width=2)
        for ly in (y + 8, y + h - 8):
            d.line([(x + 6, ly), (x + w - 6, ly)], fill=(90, 140, 190), width=2)
        cx, cy = x + w // 2, y + h // 2
        for px in (cx - 12, cx, cx + 12):
            d.line([(px, cy - 18), (px, cy - 10)], fill=(255, 214, 120), width=3)
            d.line([(px, cy + 10), (px, cy + 18)], fill=(255, 214, 120), width=3)
        d.rectangle([cx - 18, cy - 10, cx + 18, cy + 10], fill=(31, 78, 121),
                    outline=(255, 214, 120), width=3)
        d.rectangle([cx - 7, cy - 4, cx + 7, cy + 4], fill=(255, 214, 120))
    elif kind == "chart":
        d.rectangle([x, y, x + w, y + h], fill=(255, 253, 247))
        base = y + h - 6
        bw = (w - 24) // 4
        for i, bh in enumerate((34, 26, 18, 10)):
            bx = x + 12 + i * bw
            d.rectangle([bx, base - bh, bx + bw - 6, base],
                        fill=RED if i == 3 else NAVY2)
        # thick red down arrow, top right
        ax, ay = x + w - 30, y + 8
        d.polygon([(ax, ay), (ax + 18, ay), (ax + 9, ay + 14)], fill=RED)
    elif kind == "health":
        d.rectangle([x, y, x + w, y + h], fill=(255, 240, 240))
        cx, cy = x + w // 2, y + h // 2
        d.rectangle([cx - 5, cy - 14, cx + 5, cy + 14], fill=RED)
        d.rectangle([cx - 14, cy - 5, cx + 14, cy + 5], fill=RED)
        for dx, dy in ((-30, -8), (30, -10), (-24, 10), (26, 8)):
            d.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3], fill=NAVY2)
    elif kind == "flag":
        d.rectangle([x, y, x + w, y + h], fill=SKY)
        d.polygon([(x, y + h), (x + w * 0.3, y + h - 16), (x + w * 0.6, y + h),
                   (x + w, y + h - 12), (x + w, y + h)], fill=(120, 150, 120))
        px = x + w // 2
        d.line([(px, y + 6), (px, y + h - 8)], fill=NAVY, width=2)
        d.polygon([(px, y + 8), (px + 26, y + 14), (px, y + 20)], fill=RED)
    elif kind == "ship":
        d.rectangle([x, y, x + w, y + h], fill=SKY)
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(120, 170, 200))
        cx, cy = x + w // 2, y + h // 2
        d.polygon([(cx - 30, cy), (cx + 30, cy), (cx + 22, cy + 10), (cx - 22, cy + 10)],
                  fill=NAVY)
        d.line([(cx, cy), (cx, cy - 14)], fill=NAVY, width=2)
        d.polygon([(cx, cy - 14), (cx + 14, cy - 4), (cx, cy - 4)], fill=RED)
        for dx in (-40, -8, 34):
            d.ellipse([cx + dx - 3, cy + 14 - 3, cx + dx + 3, cy + 14 + 3],
                      fill=(26, 26, 26))
    elif kind == "globe":
        d.rectangle([x, y, x + w, y + h], fill=SKY)
        cx, cy = x + w // 2, y + h // 2
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=NAVY, width=2)
        d.ellipse([cx - 7, cy - 16, cx + 7, cy + 16], outline=NAVY, width=1)
        d.line([(cx - 16, cy), (cx + 16, cy)], fill=NAVY, width=1)
        d.ellipse([cx + 20, cy - 4, cx + 28, cy + 4], fill=RED)
        d.ellipse([cx - 28, cy + 6, cx - 20, cy + 14], fill=RED)
        # thick red migration arrow across the globe
        d.line([(cx - 24, cy + 14), (cx + 24, cy - 14)], fill=RED, width=3)
        d.polygon([(cx + 24, cy - 14), (cx + 12, cy - 14), (cx + 24, cy - 2)],
                  fill=RED)
    elif kind == "leaf":
        d.rectangle([x, y, x + w, y + h], fill=(220, 240, 220))
        d.ellipse([x + w - 22, y + 4, x + w - 6, y + 20], fill=(255, 214, 120))
        d.polygon([(x, y + h), (x + w * 0.4, y + h - 14), (x + w * 0.7, y + h),
                   (x + w, y + h - 10), (x + w, y + h)], fill=(120, 180, 120))
        cx, cy = x + w // 2, y + h // 2 - 2
        d.polygon([(cx, cy - 12), (cx + 12, cy), (cx, cy + 12), (cx - 12, cy)],
                  fill=(34, 139, 34))
    elif kind == "virus":
        d.rectangle([x, y, x + w, y + h], fill=(255, 240, 240))
        cx, cy = x + w // 2, y + h // 2
        for sx, sy in ((17, 0), (12, 12), (0, 17), (-12, 12), (-17, 0),
                       (-12, -12), (0, -17), (12, -12)):
            d.line([(cx + sx * 0.6, cy + sy * 0.6), (cx + sx, cy + sy)],
                   fill=RED, width=3)
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=RED)
        d.ellipse([cx - 4, cy - 6, cx + 2, cy + 0], fill=(255, 255, 255))
    elif kind == "syringe":
        d.rectangle([x, y, x + w, y + h], fill=(230, 240, 255))
        cx, cy = x + w // 2, y + h // 2
        d.polygon([(cx - 16, cy + 6), (cx + 2, cy - 12), (cx + 8, cy - 6),
                   (cx - 10, cy + 12)], fill=(255, 255, 255), outline=NAVY, width=2)
        d.line([(cx + 8, cy - 6), (cx + 22, cy - 20)], fill=NAVY, width=2)
        d.line([(cx - 16, cy + 6), (cx - 24, cy + 14)], fill=NAVY, width=3)
        d.ellipse([cx - 6, cy - 2, cx + 2, cy + 6], fill=RED)
    elif kind == "docs":
        d.rectangle([x, y, x + w, y + h], fill=SKY)
        cx, cy = x + w // 2, y + h // 2
        d.rectangle([cx - 26, cy - 12, cx + 6, cy + 12], fill=(255, 255, 255),
                    outline=NAVY, width=2)
        for ly in (cy - 6, cy, cy + 6):
            d.line([(cx - 21, ly), (cx + 1, ly)], fill=NAVY2, width=2)
        d.line([(cx + 16, cy - 14), (cx + 16, cy + 14)], fill=NAVY, width=2)
        d.polygon([(cx + 16, cy - 14), (cx + 30, cy - 10), (cx + 16, cy - 6)],
                  fill=RED)
        d.polygon([(cx + 16, cy - 6), (cx + 30, cy - 2), (cx + 16, cy + 2)],
                  fill=(255, 255, 255))
    else:
        d.rectangle([x, y, x + w, y + h], fill=SKY)
        d.ellipse([x + w // 2 - 12, y + h // 2 - 12, x + w // 2 + 12, y + h // 2 + 12],
                  outline=NAVY, width=2)


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28

    # ---------- navy masthead (rank 5 palette, rank 1 date) ----------
    d.rectangle([0, 0, W, 150], fill=NAVY)
    tf = SERIF_B(40)
    tw = d.textlength(data["title"], font=tf)
    d.text(((W - tw) / 2, 14), data["title"], font=tf, fill=(255, 255, 255))
    df = SERIF_B(38)
    dw = d.textlength(data["date_line"], font=df)
    d.text(((W - dw) / 2, 62), data["date_line"], font=df, fill=(255, 255, 255))
    sf = SANS_B(15)
    sw = d.textlength(data["subtitle"], font=sf)
    d.text(((W - sw) / 2, 108), data["subtitle"], font=sf, fill=(255, 214, 120))
    legend = ("WAR & SECURITY  •  POLITICS & DIPLOMACY  •  ECONOMY & MARKETS  •  "
              "HEALTH  •  SCIENCE & SPACE  •  CULTURE & SPORT  •  CLIMATE & DISASTERS")
    lf = SANS(10)
    lw = d.textlength(legend, font=lf)
    d.text(((W - lw) / 2, 132), legend, font=lf, fill=(170, 195, 220))

    # ---------- heroes: 2 side by side (rank 1) ----------
    hy, hh = 160, 168
    hw = (W - 2 * mx - 14) // 2
    for i, hero in enumerate(data["heroes"]):
        x = mx + i * (hw + 14)
        d.rectangle([x, hy, x + hw, hy + hh], fill=PANEL, outline=RULE, width=1)
        draw_hero_art(d, hero["icon"], x + 1, hy + 1, hw - 2, 50)
        ty = hy + 58
        d.text((x + 10, ty), "%d  •  %s" % (i + 1, hero["kicker"]),
               font=SANS_B(11), fill=RED)
        ty += 17
        hf = SERIF_B(19)
        for ln in wrap(d, hero["headline"], hf, hw - 20)[:2]:
            d.text((x + 10, ty), ln, font=hf, fill=INK)
            ty += 22
        bf = SERIF(12)
        for ln in wrap(d, hero["body"], bf, hw - 20)[:2]:
            d.text((x + 10, ty), ln, font=bf, fill=INK)
            ty += 15

    # ---------- cards: 2 rows x 5 cols (rank 1), fixed pattern (rank 2) ----------
    cy0 = 338
    cols, rows = 5, 2
    gap_x, gap_y = 12, 10
    cw = (W - 2 * mx - (cols - 1) * gap_x) / cols
    ch = 108
    for idx, b in enumerate(data["cards"]):
        r, c = divmod(idx, cols)
        x = mx + c * (cw + gap_x)
        yy = cy0 + r * (ch + gap_y)
        d.rectangle([x, yy, x + cw, yy + ch], fill=PANEL, outline=RULE, width=1)
        draw_hero_art(d, b["icon"], x + 1, yy + 1, cw - 2, 48)
        # story number badge on the art band
        bx0, by0 = x + cw - 26, yy + 6
        d.ellipse([bx0, by0, bx0 + 20, by0 + 20], fill=RED,
                  outline=(255, 255, 255), width=2)
        num = str(idx + 3)
        nw = d.textlength(num, font=SANS_B(11))
        d.text((bx0 + (20 - nw) / 2, by0 + 3), num, font=SANS_B(11),
               fill=(255, 255, 255))
        d.text((x + 8, yy + 53), b["kicker"], font=SANS_B(9), fill=RED)
        hf2 = SERIF_B(13)
        hlines = wrap(d, b["headline"], hf2, cw - 16)[:2]
        hyy = draw_lines(d, hlines, x + 8, yy + 66, hf2, INK, 13)
        bf2 = SANS(10)
        blines = wrap(d, b["body"], bf2, cw - 16)[:1]
        draw_lines(d, blines, x + 8, hyy + 2, bf2, INK, 12)

    # ---------- map + also-on (rank 1 footer) ----------
    fy = 574
    fh = 388
    map_x, map_w = mx, 470
    list_x, list_w = mx + 482, W - mx - (mx + 482)
    # map panel
    d.rectangle([map_x, fy, map_x + map_w, fy + fh], fill=PANEL, outline=RULE, width=1)
    d.text((map_x + 10, fy + 8), "WHERE IT HAPPENED", font=SANS_B(13), fill=INK)
    d.text((map_x + 10, fy + 27), "Numbers match the stories",
           font=SANS(11), fill=GREY)
    px0, py0 = map_x + 8, fy + 50
    pw, ph = map_w - 16, 230

    def project(lon, lat):
        return (px0 + (lon + 180) / 360.0 * pw,
                py0 + (80 - lat) / 135.0 * ph)

    for name, poly in CONTINENTS.items():
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(214, 206, 184), outline=(110, 102, 86))
    for dot in data["map_dots"]:
        cx, cy = project(dot["lon"], dot["lat"])
        cx += dot.get("dx", 0)
        cy += dot.get("dy", 0)
        r = 9
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                  outline=(255, 255, 255), width=2)
        label = str(dot["n"])
        lw = d.textlength(label, font=SANS_B(10))
        d.text((cx - lw / 2, cy - 7), label, font=SANS_B(10), fill=(255, 255, 255))
    ly = py0 + ph + 10
    legend = "   •   ".join("%d %s" % (dot["n"], dot["label"])
                            for dot in data["map_dots"])
    for ln in wrap(d, legend, SANS(10), map_w - 20):
        d.text((map_x + 10, ly), ln, font=SANS(10), fill=GREY)
        ly += 14
    d.text((map_x + 10, fy + fh - 34),
           "Six continents, one day: every pin is a story above.",
           font=SANS(10), fill=GREY)
    # also-on panel
    d.rectangle([list_x, fy, list_x + list_w, fy + fh], fill=PANEL, outline=RULE, width=1)
    d.text((list_x + 10, fy + 8), "ALSO ON TUESDAY 17 NOVEMBER",
           font=SANS_B(13), fill=INK)
    col_w = (list_w - 20) / 2
    ay = fy + 30
    for i, item in enumerate(data["also_on"]):
        col = 0 if i < 14 else 1
        row = i if i < 14 else i - 14
        x = list_x + 10 + col * col_w
        yy = ay + row * 25
        num = "%d." % (i + 13)
        d.text((x, yy), num, font=SANS_B(10), fill=RED)
        tx = x + d.textlength(num, font=SANS_B(10)) + 4
        for ln in wrap(d, item, SANS(10), col_w - (tx - x) - 8)[:1]:
            d.text((tx, yy), ln, font=SANS(10), fill=INK)
            yy += 12

    # ---------- footer (rank 1 sources line) ----------
    fy2 = 976
    d.line([(mx, fy2), (W - mx, fy2)], fill=RULE, width=1)
    fw = d.textlength(data["footer"], font=SANS(9))
    if fw <= W - 2 * mx:
        d.text(((W - fw) / 2, fy2 + 7), data["footer"], font=SANS(9), fill=GREY)
    else:
        for j, ln in enumerate(wrap(d, data["footer"], SANS(9), W - 2 * mx)):
            lw2 = d.textlength(ln, font=SANS(9))
            d.text(((W - lw2) / 2, fy2 + 6 + j * 12), ln, font=SANS(9), fill=GREY)
    tg = d.textlength(data["tagline"], font=SANS_B(10))
    d.text(((W - tg) / 2, fy2 + 26), data["tagline"], font=SANS_B(10), fill=NAVY2)

    out = os.path.join(ROOT, "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    sys.exit(main())
