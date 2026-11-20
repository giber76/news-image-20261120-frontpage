#!/usr/bin/env python3
"""Draw the v2 front page for news-image-20261120.

A clean magazine-style front page: 3 leads, 10 feature cards, 14 briefs,
a 6-stat numbers strip, a schematic world map with pins 1-13, a DATE CHECK
strip and a footer. Every story was verified against live sources on
Friday 20 November 2026 as an event of that day (or a development first
reported that day). All drawings are original vector work made with PIL;
no photographs, no copied artwork.

Run:  python3 draw.py            -> writes entry.png (1024x1024, <=1 MiB)
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
MUTED = (90, 86, 76)
RED = (179, 38, 30)
BLUE = (31, 78, 121)
TEAL = (15, 118, 110)
GOLD = (150, 105, 20)
LINE = (180, 172, 156)
SEA = (223, 232, 236)
LAND = (221, 214, 198)
LANDLINE = (185, 176, 154)

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)             # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)        # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)               # noqa: E731


def wrap(d, text, f, width):
    """Greedy word wrap; returns list of lines that fit `width` px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, f, width, fill=INK, leading=None, max_lines=None):
    """Draw wrapped paragraph; returns y just below the last line."""
    leading = leading or int(f.size * 1.32)
    lines = wrap(d, text, f, width)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def rule(d, x, y, w, fill=INK, h=2):
    d.rectangle([x, y, x + w, y + h - 1], fill=fill)


# ---------------------------------------------------------------- illustrations
def illo_cyclone(d, x, y, w, h):
    """Spiral storm over a coastline: sea above, land below."""
    d.rectangle([x, y, x + w, y + h], fill=(58, 110, 150))
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h * 0.72),
               (x + int(w * 0.62), y + h * 0.66), (x + int(w * 0.4), y + h * 0.8)],
              fill=(96, 140, 90))
    cx, cy = x + int(w * 0.42), y + int(h * 0.42)
    for r in range(8, int(min(w, h) * 0.52), 7):
        a0 = r * 0.55
        pts = []
        for k in range(0, 200, 8):
            a = math.radians(a0 + k * 1.6)
            rr = r * (0.55 + 0.45 * k / 200.0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.82))
        d.line(pts, fill=(255, 255, 255), width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    for i in range(6):
        rx = x + int(w * (0.68 + 0.05 * i))
        d.line([(rx, y + 6), (rx - 4, y + 18)], fill=(200, 225, 240), width=2)


def illo_kyiv(d, x, y, w, h):
    """Night skyline, missile streaks, fires."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 34, 58))
    for i in range(14):
        sx = x + 6 + i * 7
        d.point((sx, y + 6 + (i * 13) % 22), fill=(255, 255, 255))
    base = y + h
    heights = [0.55, 0.8, 0.45, 0.95, 0.6, 0.75, 0.5, 0.85, 0.4, 0.7]
    bw = w / len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx + 1, base - h * hh, bx + bw - 1, base], fill=(12, 18, 34))
        if i % 3 == 0:
            d.rectangle([bx + bw * 0.4, base - h * hh - 8, bx + bw * 0.6,
                         base - h * hh], fill=(12, 18, 34))
    for sx, sy in [(0.18, 0.30), (0.55, 0.18), (0.82, 0.38)]:
        px, py = x + w * sx, y + h * sy
        d.line([(px, py), (px + 26, py + 16)], fill=(255, 190, 80), width=3)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 220, 130))
    for fx in (0.30, 0.68):
        fx0 = x + w * fx
        d.polygon([(fx0, base - 6), (fx0 + 7, base - 22), (fx0 + 14, base - 6)],
                  fill=(255, 140, 40))


def illo_cop(d, x, y, w, h):
    """Globe with a rising sun behind it."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 226, 205))
    sx, sy = x + int(w * 0.72), y + int(h * 0.42)
    for k in range(8):
        a = math.radians(k * 45)
        d.line([(sx + 26 * math.cos(a), sy + 26 * math.sin(a)),
                (sx + 36 * math.cos(a), sy + 36 * math.sin(a))],
               fill=(220, 150, 40), width=3)
    d.ellipse([sx - 20, sy - 20, sx + 20, sy + 20], fill=(245, 180, 60))
    cx, cy, r = x + int(w * 0.38), y + int(h * 0.52), int(min(w, h) * 0.42)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 180))
    d.ellipse([cx - r * 0.55, cy - r * 0.7, cx - r * 0.1, cy - r * 0.25],
              fill=(110, 180, 110))
    d.ellipse([cx + r * 0.1, cy + r * 0.15, cx + r * 0.6, cy + r * 0.6],
              fill=(110, 180, 110))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 330, fill=(255, 255, 255), width=2)


def illo_chart_down(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 238, 236))
    for gy in range(1, 4):
        yy = y + h * gy / 4
        d.line([(x + 4, yy), (x + w - 4, yy)], fill=(225, 200, 195), width=1)
    pts = [(x + 6 + i * (w - 12) / 6, y + h * (0.18 + 0.13 * i) + (6 if i % 2 else -4))
           for i in range(7)]
    d.line(pts, fill=RED, width=3)
    d.polygon(pts + [(pts[-1][0], y + h - 4), (pts[0][0], y + h - 4)],
              fill=(179, 38, 30))
    ex, ey = pts[-1]
    d.polygon([(ex - 2, ey - 12), (ex + 12, ey - 2), (ex - 2, ey + 2)], fill=RED)


def illo_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 26, 40))
    for i in range(10):
        d.point((x + 8 + (i * 29) % (w - 10), y + 6 + (i * 17) % 24),
                fill=(255, 255, 255))
    cx, cy, r = x + int(w * 0.62), y + int(h * 0.55), int(min(w, h) * 0.34)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(170, 165, 155))
    for ox, oy, orr in [(-0.4, -0.3, 0.16), (0.3, 0.1, 0.12), (-0.1, 0.4, 0.10),
                        (0.45, -0.35, 0.08)]:
        d.ellipse([cx + ox * r - orr * r, cy + oy * r - orr * r,
                   cx + ox * r + orr * r, cy + oy * r + orr * r],
                  fill=(140, 135, 125))
    px, py = x + int(w * 0.2), y + int(h * 0.3)
    d.rectangle([px - 9, py - 3, px + 9, py + 3], fill=(200, 200, 210))
    d.rectangle([px - 3, py - 7, px + 3, py + 7], fill=(150, 150, 165))
    d.line([(px + 9, py), (cx - r - 2, cy - 6)], fill=(255, 255, 255), width=1)


def illo_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 224))
    # EU flag bar
    d.rectangle([x + 6, y + 6, x + w // 2 - 4, y + h - 6], fill=(0, 51, 153))
    ecx, ecy = x + w // 4, y + h // 2
    for k in range(12):
        a = math.radians(k * 30 - 90)
        d.ellipse([ecx + 13 * math.cos(a) - 2, ecy + 13 * math.sin(a) - 2,
                   ecx + 13 * math.cos(a) + 2, ecy + 13 * math.sin(a) + 2],
                  fill=(255, 204, 0))
    # UK flag bar (simplified union jack)
    ux0, ux1 = x + w // 2 + 4, x + w - 6
    d.rectangle([ux0, y + 6, ux1, y + h - 6], fill=(1, 33, 105))
    d.line([(ux0, y + 6), (ux1, y + h - 6)], fill=(255, 255, 255), width=5)
    d.line([(ux1, y + 6), (ux0, y + h - 6)], fill=(255, 255, 255), width=5)
    d.line([(ux0, y + h // 2 - 4), (ux1, y + h // 2 - 4)], fill=(200, 16, 46), width=6)
    d.line([(ux0 + (ux1 - ux0) // 2 - 3, y + 6),
            (ux0 + (ux1 - ux0) // 2 - 3, y + h - 6)], fill=(200, 16, 46), width=6)


def illo_bars_up(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 242, 238))
    vals = [0.30, 0.45, 0.62, 0.78]
    bw = w / 5
    for i, v in enumerate(vals):
        bx = x + bw * (i + 0.5)
        d.rectangle([bx, y + h - 6 - h * v * 0.8, bx + bw * 0.7, y + h - 6],
                    fill=TEAL if i < 3 else GOLD)
    d.line([(x + 4, y + h - 6), (x + w - 4, y + h - 6)], fill=INK, width=2)


def illo_bank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 236, 228))
    d.polygon([(x + w * 0.12, y + h * 0.28), (x + w * 0.5, y + h * 0.08),
               (x + w * 0.88, y + h * 0.28)], fill=(90, 90, 100))
    for i in range(4):
        cx0 = x + w * (0.18 + i * 0.21)
        d.rectangle([cx0, y + h * 0.32, cx0 + w * 0.09, y + h * 0.82],
                    fill=(120, 120, 130))
    d.rectangle([x + w * 0.1, y + h * 0.82, x + w * 0.9, y + h * 0.9],
                fill=(90, 90, 100))
    d.line([(x + 6, y + h * 0.55), (x + w - 6, y + h * 0.55)], fill=TEAL, width=3)


def illo_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 240, 226))
    d.ellipse([x + w * 0.55, y + h * 0.1, x + w * 0.95, y + h * 0.55],
              fill=(120, 180, 90), outline=(70, 120, 50), width=2)
    bx, by = x + int(w * 0.30), y + int(h * 0.30)
    d.rounded_rectangle([bx - 7, by - 4, bx + 34, by + 10], radius=5,
                        fill=(205, 170, 120), outline=(120, 85, 40))
    d.rectangle([bx + 32, by - 1, bx + 52, by + 7], fill=(160, 120, 70))
    d.ellipse([x + w * 0.72, y + h * 0.62, x + w * 0.72 + 12, y + h * 0.62 + 12],
              fill=(178, 34, 34), outline=(120, 20, 20))
    for sx in (0.12, 0.20, 0.28):
        d.line([(x + w * sx, y + h * 0.92), (x + w * sx, y + h * 0.62)],
               fill=(220, 190, 120), width=3)


def illo_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 236, 228))
    for i, col in enumerate([RED, BLUE, GOLD]):
        sx = x + w * (0.18 + i * 0.32)
        d.line([(sx, y + h * 0.35), (sx, y + h * 0.92)], fill=(90, 80, 70), width=3)
        d.rectangle([sx - 16, y + h * 0.12, sx + 16, y + h * 0.36], fill=col)
        d.line([(sx - 12, y + h * 0.20), (sx + 12, y + h * 0.20)],
               fill=(255, 255, 255), width=2)
        d.line([(sx - 12, y + h * 0.28), (sx + 12, y + h * 0.28)],
               fill=(255, 255, 255), width=2)


def illo_pill(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 244))
    cx, cy = x + int(w * 0.42), y + int(h * 0.52)
    d.rounded_rectangle([cx - 34, cy - 11, cx + 34, cy + 11], radius=11,
                        fill=(255, 255, 255), outline=(60, 60, 80), width=2)
    d.rounded_rectangle([cx - 34, cy - 11, cx, cy + 11], radius=11, fill=TEAL)
    d.rectangle([cx - 2, cy - 11, cx + 2, cy + 11], fill=(60, 60, 80))
    for ox, oy, r in [(0.78, 0.25, 5), (0.85, 0.62, 4), (0.68, 0.75, 3)]:
        d.ellipse([x + w * ox - r, y + h * oy - r, x + w * ox + r, y + h * oy + r],
                  fill=(200, 90, 90), outline=(140, 40, 40))


def illo_sub(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 238))
    for wy in (0.78, 0.88):
        yy = y + h * wy
        d.arc([x + 4, yy - 8, x + w - 4, yy + 8], 0, 180, fill=(90, 130, 160),
              width=2)
    cx, cy = x + int(w * 0.5), y + int(h * 0.45)
    d.rounded_rectangle([cx - 42, cy - 12, cx + 42, cy + 12], radius=12,
                        fill=(70, 80, 95))
    d.rectangle([cx - 12, cy - 24, cx + 8, cy - 10], fill=(70, 80, 95))
    d.line([(cx + 8, cy - 20), (cx + 22, cy - 20)], fill=(70, 80, 95), width=2)
    d.ellipse([cx + 28, cy - 4, cx + 34, cy + 2], fill=(220, 220, 230))


def illo_arch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 230, 210))
    d.rectangle([x + w * 0.14, y + h * 0.30, x + w * 0.86, y + h * 0.92],
                fill=(178, 120, 70))
    d.pieslice([x + w * 0.34, y + h * 0.30, x + w * 0.66, y + h * 0.78], 180, 360,
               fill=(240, 230, 210))
    d.rectangle([x + w * 0.06, y + h * 0.24, x + w * 0.94, y + h * 0.32],
                fill=(140, 90, 50))
    for fx in (0.22, 0.78):
        d.rectangle([x + w * fx - 2, y + h * 0.10, x + w * fx + 2, y + h * 0.26],
                    fill=(200, 60, 60))
    d.rectangle([x + w * 0.44, y + h * 0.62, x + w * 0.56, y + h * 0.92],
                fill=(90, 60, 40))


# ---------------------------------------------------------------- world map
def lonlat_to_xy(lon, lat, x0, y0, mw, mh):
    return (x0 + (lon + 180.0) / 360.0 * mw,
            y0 + (75.0 - lat) / 130.0 * mh)


CONTINENTS = {
    "north_america": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                      (-85, 70), (-75, 62), (-60, 55), (-55, 47), (-65, 44),
                      (-75, 35), (-80, 25), (-90, 21), (-97, 16), (-105, 20),
                      (-115, 28), (-125, 40), (-125, 49), (-140, 60),
                      (-155, 58), (-165, 60)],
    "greenland": [(-58, 64), (-45, 60), (-30, 68), (-20, 70), (-30, 76),
                  (-55, 76), (-60, 70)],
    "south_america": [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8),
                      (-40, -20), (-48, -28), (-58, -38), (-65, -45),
                      (-70, -52), (-73, -40), (-75, -20), (-80, -5)],
    "africa": [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31),
               (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20),
               (32, -28), (20, -35), (15, -30), (12, -18), (9, 4), (-8, 5),
               (-15, 11)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
               (10, 59), (18, 56), (21, 55), (28, 60), (30, 70), (40, 68),
               (45, 60), (40, 50), (35, 45), (28, 41), (23, 36), (19, 40),
               (12, 44), (8, 44), (3, 42), (-2, 37), (-9, 37)],
    "asia": [(40, 68), (60, 70), (75, 73), (90, 75), (110, 76), (130, 72),
             (160, 70), (178, 66), (170, 60), (162, 55), (158, 50),
             (142, 45), (135, 35), (127, 35), (122, 30), (120, 22),
             (110, 20), (105, 10), (100, 8), (98, 15), (92, 20), (88, 22),
             (80, 15), (77, 8), (72, 20), (66, 25), (60, 25), (55, 26),
             (50, 29), (48, 30), (44, 29), (40, 35), (36, 36)],
    "australia": [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32),
                  (137, -35), (140, -38), (147, -39), (150, -37), (153, -27),
                  (146, -19), (142, -11), (135, -12), (130, -13), (126, -14),
                  (122, -17), (118, -20)],
    "se_asia": [(95, 5), (100, 0), (103, -3), (108, -6), (113, -8),
                (118, -9), (120, -10), (115, -5), (110, 0), (105, 3),
                (100, 6)],
}

# (lon, lat, badge dx, badge dy) for the 13 featured stories
PINS = [
    (85.5, 19.5, 10, -8),    # 1 Akvan / Odisha
    (30.5, 50.4, 8, -10),    # 2 Kyiv
    (30.7, 36.9, 12, 6),     # 3 Antalya
    (127.0, 37.5, 8, -10),   # 4 Seoul (AI sell-off)
    (8.65, 49.87, 12, -10),  # 5 Darmstadt (BepiColombo)
    (4.35, 50.85, -16, -8),  # 6 Brussels
    (139.7, 35.7, 8, -10),   # 7 Tokyo (Japan CPI)
    (116.4, 39.9, 8, -10),   # 8 Beijing
    (174.8, -41.3, -16, -8), # 9 Wellington
    (12.5, 41.9, 10, 8),     # 10 Rome
    (2.17, 41.38, -16, 6),   # 11 Barcelona
    (-77.0, 38.9, 8, -10),   # 12 Washington
    (77.2, 28.6, 10, -8),    # 13 New Delhi
]


def draw_map(d, x0, y0, mw, mh):
    d.rectangle([x0, y0, x0 + mw, y0 + mh], fill=SEA, outline=LINE)
    for pts in CONTINENTS.values():
        xy = [lonlat_to_xy(lon, lat, x0, y0, mw, mh) for lon, lat in pts]
        d.polygon(xy, fill=LAND, outline=LANDLINE)
    # Japan + UK hints
    for lon, lat in [(140, 38), (141, 42), (-2, 54), (-4, 57)]:
        px, py = lonlat_to_xy(lon, lat, x0, y0, mw, mh)
        d.ellipse([px - 2, py - 3, px + 2, py + 3], fill=LAND, outline=LANDLINE)
    fpin = SANS_B(9)
    for i, (lon, lat, dx, dy) in enumerate(PINS, start=1):
        px, py = lonlat_to_xy(lon, lat, x0, y0, mw, mh)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        bx, by = px + dx, py + dy
        d.line([(px, py), (bx, by)], fill=RED, width=1)
        d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=RED,
                  outline=(255, 255, 255))
        label = str(i)
        tw = d.textlength(label, font=fpin)
        d.text((bx - tw / 2, by - 5), label, font=fpin, fill=(255, 255, 255))


# ---------------------------------------------------------------- content
LEADS = [
    dict(num=1, kicker="1 · INDIA — CYCLONE AKVAN", illo=illo_cyclone,
         head="Cyclone Akvan slams Odisha coast",
         dek=("Landfall near Gopalpur on Friday morning, winds 70–80 km/h "
              "gusting to 90. More than 300,000 evacuated, 423 rescue teams "
              "out, 9,341 shelters open, 69 trains cancelled. No major "
              "damage yet. — IMD / The Hindu")),
    dict(num=2, kicker="2 · UKRAINE — KYIV", illo=illo_kyiv,
         head="Kyiv hit by overnight missile barrage",
         dek=("Ballistic missiles struck from about 01:25, fires in three "
              "districts, Dnipro bridges damaged and a Kharkiv hospital hit, "
              "four hurt. It follows Putin's vow of retaliation for the "
              "Crimea bridge strike. — Kyiv Post / Reuters")),
    dict(num=3, kicker="3 · TÜRKIYE — COP31", illo=illo_cop,
         head="COP31 ends in deadlock on fossil fuels",
         dek=("Closing day in Antalya ends without a deal. The slimmed draft "
              "— 80 paragraphs, no fossil-fuel phase-out, no $120bn "
              "adaptation figure — is still contested at midnight. "
              "— UN News / Reuters")),
]

FEATURES = [
    dict(num=4, kicker="ASIA — MARKETS", illo=illo_chart_down,
         head="Asia's AI sell-off deepens",
         dek=("Nikkei −4.5%, Kospi −4.7%, SoftBank −15%. Taiex's worst "
              "week since 1990; region's worst since 2020.")),
    dict(num=5, kicker="SPACE — MERCURY", illo=illo_mercury,
         head="BepiColombo reaches Mercury",
         dek=("After eight years, the ESA–JAXA probe arrives. Orbit capture "
              "is Saturday — only the second ever.")),
    dict(num=6, kicker="EUROPE — SUMMIT", illo=illo_flags,
         head="Burnham's first EU–UK reset summit",
         dek=("Costa and von der Leyen host the UK prime minister. Food "
              "trade, a carbon link and a youth scheme.")),
    dict(num=7, kicker="JAPAN — PRICES", illo=illo_bars_up,
         head="Japan prices rise 2.3% in October",
         dek=("Headline CPI up from 2.1%; core 2.2%. Markets price a "
              "December BoJ rise to 1.50% at about 86%.")),
    dict(num=8, kicker="CHINA — RATES", illo=illo_bank,
         head="China holds lending rates",
         dek=("One-year LPR 3.0%, five-year 3.5% — unchanged for an 18th "
              "straight month. Beijing waits.")),
    dict(num=9, kicker="SPORT — CRICKET", illo=illo_cricket,
         head="Phillips 118 powers New Zealand",
         dek=("Day two in Wellington: 118 off 216 balls in a 216-run stand "
              "with Nicholls (175*). NZ 368 all out.")),
    dict(num=10, kicker="ITALY — STRIKE", illo=illo_strike,
         head="Italy stops for a general strike",
         dek=("CGIL's 24-hour stoppage, rallies in about 100 squares "
              "against the 2027 budget. Students join.")),
    dict(num=11, kicker="HEALTH — CANCER", illo=illo_pill,
         head="Cancer pill shrinks tumours in 60.7%",
         dek=("Daraxonrasib plus chemo, presented in Barcelona: tumours "
              "shrank in 60.7% of 61 patients.")),
    dict(num=12, kicker="USA — DEFENCE", illo=illo_sub,
         head="Sub sale would shrink US fleet, CBO warns",
         dek=("Selling 3–5 Virginia-class boats to Australia from 2032 "
              "would shrink the US Navy 'for many years'.")),
    dict(num=13, kicker="INDIA — DIPLOMACY", illo=illo_arch,
         head="Modi opens SCO dialogue; Pakistan attends",
         dek=("First civilisational forum at Purana Qila; Pakistan's "
              "minister is the first to visit since May 2023.")),
]

BRIEFS = [
    ("FLORIDA —", "St Johns River is forecast to crest at 18.6 ft on Friday "
     "evening, above the 1953 record broken on Thursday. Schools shut; "
     "100+ rescued in Brevard."),
    ("IOWA —", "The Friday noon detonation of 68 unstable explosive barrels "
     "— about five tons of degraded lead azide — was put off to Monday "
     "after the governor asked."),
    ("TONGA —", "Government schools close on Friday as the El Niño drought "
     "bites, a day after a state of emergency was declared."),
    ("SEOUL —", "The ruling party's push to impeach Chief Justice Cho "
     "Hee-dae formalises on Friday; the Presidential Office denies any "
     "prior consultation."),
    ("HONG KONG —", "Quarter-finals day at the Hong Kong Open: Loh Kean Yew "
     "meets Lakshya Sen at Kai Tak Arena."),
    ("TAIPEI —", "Taiwan's short-sale curbs take effect on Friday: stocks "
     "down 3.5% or more cannot be shorted below the prior close; the cap "
     "drops to 1%."),
    ("TURIN —", "ATP Finals, day six: Alcaraz faces Cobolli, then Medvedev "
     "meets Tiafoe in a winner-takes-all fight for the last semi-final "
     "place."),
    ("UNICEF —", "World Children's Day, 20 November: 'My day. My rights. "
     "My future.' — 37 years since the Convention on the Rights of the "
     "Child."),
    ("WELLINGTON —", "Nicholls 175 not out in the 216-run stand with "
     "Phillips; New Zealand 368 all out against India."),
    ("GOLD —", "Spot gold breaks below $3,600 to $3,551.68, its worst week "
     "in eight months and lowest since September 2025."),
    ("SEOUL —", "Samsung names Choi Won-joon to run its mobile business, "
     "replacing TM Roh, who stays co-CEO; Hwang Sang-joon takes memory."),
    ("CYBER —", "Mandiant says a China-linked group used a critical vCenter "
     "flaw (CVSS 9.8) as a zero-day since early September. Broadcom "
     "patched it on Thursday."),
    ("CRYPTO —", "Bitcoin trades near $61,900, down about 28% for the "
     "quarter, as gold slides and real rates surge."),
    ("MALAWI —", "Fuel queues turn violent as shortages bite: a 20-litre "
     "daily ration, petrol at about $3.24 a litre — more than double the "
     "world average."),
]

NUMBERS = [
    ("300,000+", "evacuated from Akvan's path"),
    ("−4.5%", "Nikkei on Friday"),
    ("423", "rescue teams in Odisha"),
    ("216", "runs, Phillips–Nicholls stand"),
    ("18.6 ft", "St Johns River crest, forecast"),
    ("60.7%", "tumour response, Daraxonrasib"),
]

DATE_CHECK = ("NOT TODAY — FIRST REPORTED THURSDAY 19 NOVEMBER: "
              "Trump–Xi–Putin Shenzhen summit · Anthropic's $83 IPO pricing "
              "and Nasdaq debut · ICJ rules Myanmar committed genocide "
              "against the Rohingya · GTA VI midnight launch · $190.4m Van "
              "Gogh sale · Voyager 1 one light-day from the Sun · Senate "
              "rejects Iran war-powers measure")

FOOTER_LINE1 = ("Every story above happened or was first reported on Friday "
                 "20 November 2026. Claims are attributed to their sources, "
                 "not asserted as fact.")
FOOTER_SOURCES = ("Sources: IMD · The Hindu · Kyiv Post · Reuters · UN News "
                  "· ESA · EU Council · Statistics Bureau of Japan · PBC · "
                  "Cricinfo · CGIL · Revolution Medicines · CBO · MEA · "
                  "Florida officials · Al Jazeera · BWF · Taiwan FSC · ATP "
                  "· UNICEF · CoinDesk · Mandiant · Samsung Newsroom")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=RED)

    # ---- masthead
    d.text((12, 14), "THE FRONT PAGE", font=SERIF_B(34), fill=INK)
    d.text((W - 12 - d.textlength("FRIDAY 20 NOVEMBER 2026", font=SANS_B(21)), 16),
           "FRIDAY 20 NOVEMBER 2026", font=SANS_B(21), fill=RED)
    d.text((W - 12 - d.textlength("27 STORIES · 6 CONTINENTS", font=SANS(11)), 42),
           "27 STORIES · 6 CONTINENTS", font=SANS(11), fill=MUTED)
    rule(d, 12, 62, W - 24, fill=INK, h=2)
    rule(d, 12, 66, W - 24, fill=RED, h=1)
    tag = "One day. The whole world. Every story verified."
    d.text(((W - d.textlength(tag, font=SANS(12))) / 2, 74), tag,
           font=SANS(12), fill=MUTED)

    y = 94
    # ---- leads
    lead1 = LEADS[0]
    x1, w1 = 12, 544
    d.text((x1, y), lead1["kicker"], font=SANS_B(11), fill=RED)
    y2 = para(d, x1, y + 16, lead1["head"], SERIF_B(27), w1, leading=32,
              max_lines=2)
    illo_y = y2 + 4
    lead1["illo"](d, x1, illo_y, w1, 86)
    para(d, x1, illo_y + 92, lead1["dek"], SANS(13), w1, leading=17,
         max_lines=3)
    leads_bottom = illo_y + 92 + 3 * 17

    x2, w2 = 568, 444
    yy = y
    for lead in LEADS[1:]:
        d.text((x2 + 128, yy), lead["kicker"], font=SANS_B(11), fill=RED)
        hy = para(d, x2 + 128, yy + 14, lead["head"], SERIF_B(17), w2 - 128,
                  leading=21, max_lines=2)
        lead["illo"](d, x2, yy + 2, 118, 112)
        para(d, x2 + 128, hy + 2, lead["dek"], SANS(11), w2 - 128,
             leading=14, max_lines=4)
        yy += 116
        if lead is LEADS[1]:
            rule(d, x2, yy - 6, w2, fill=LINE, h=1)
    leads_bottom = max(leads_bottom, yy)
    rule(d, 12, leads_bottom + 4, W - 24, fill=INK, h=2)

    # ---- numbers strip
    y = leads_bottom + 12
    cw = (W - 24) / 6
    for i, (num, lab) in enumerate(NUMBERS):
        cx = 12 + i * cw
        nw = d.textlength(num, font=SANS_B(19))
        d.text((cx + (cw - nw) / 2, y), num, font=SANS_B(19), fill=RED)
        lw = d.textlength(lab, font=SANS(9))
        d.text((cx + (cw - lw) / 2, y + 22), lab, font=SANS(9), fill=MUTED)
        if i:
            d.line([(cx, y + 2), (cx, y + 34)], fill=LINE, width=1)
    y += 38
    rule(d, 12, y, W - 24, fill=INK, h=2)

    # ---- features: 2 rows x 5
    y += 8
    card_w, card_h, gap = 196, 126, 4
    for r in range(2):
        for c in range(5):
            f = FEATURES[r * 5 + c]
            cx = 10 + c * (card_w + gap)
            cy = y + r * (card_h + gap)
            f["illo"](d, cx, cy, card_w, 50)
            d.ellipse([cx + 4, cy + 4, cx + 22, cy + 22], fill=RED,
                      outline=(255, 255, 255))
            nb = str(f["num"])
            tw = d.textlength(nb, font=SANS_B(10))
            d.text((cx + 13 - tw / 2, cy + 8), nb, font=SANS_B(10),
                   fill=(255, 255, 255))
            d.text((cx, cy + 54), f["kicker"], font=SANS_B(8), fill=RED)
            para(d, cx, cy + 66, f["head"], SERIF_B(12), card_w, leading=15,
                 max_lines=2)
            para(d, cx, cy + 96, f["dek"], SANS(10), card_w, leading=11,
                 max_lines=3)
    y += 2 * card_h + gap + 6

    # ---- world map
    d.text((12, y), "WHERE IT HAPPENED — THE 13 FEATURED STORIES, PINNED",
           font=SANS_B(11), fill=INK)
    y += 16
    draw_map(d, 12, y, W - 24, 76)
    y += 76 + 6
    rule(d, 12, y, W - 24, fill=INK, h=2)

    # ---- briefs
    y += 8
    d.text((12, y), "IN BRIEF", font=SANS_B(12), fill=RED)
    y += 20
    col_w = 490
    for i, (lead, text) in enumerate(BRIEFS):
        col = i % 2
        row = i // 2
        bx = 12 + col * (col_w + 20)
        by = y + row * 23
        full = lead + " " + text
        lines = wrap(d, full, SANS(11), col_w)[:2]
        ly = by
        for li, ln in enumerate(lines):
            if li == 0:
                lw = d.textlength(lead + " ", font=SANS_B(11))
                d.text((bx, ly), lead + " ", font=SANS_B(11), fill=INK)
                d.text((bx + lw, ly), ln[len(lead) + 1:], font=SANS(11),
                       fill=INK)
            else:
                d.text((bx, ly), ln, font=SANS(11), fill=INK)
            ly += 11.5
    y += 7 * 23 + 6
    rule(d, 12, y, W - 24, fill=LINE, h=1)

    # ---- date check
    y += 8
    para(d, 12, y, DATE_CHECK, SANS_B(10), W - 24, fill=MUTED, leading=13,
         max_lines=2)
    y += 26
    rule(d, 12, y, W - 24, fill=INK, h=2)

    # ---- footer
    y += 7
    para(d, 12, y, FOOTER_LINE1, SANS(10), W - 24, leading=13, max_lines=1)
    y += 13
    para(d, 12, y, FOOTER_SOURCES, SANS(9), W - 24, fill=MUTED, leading=12,
         max_lines=2)
    y += 24
    if y > H:
        print(f"WARNING: content overflows by {y - H}px", file=sys.stderr)
    return img


def main():
    img = build()
    img.save("entry.png", optimize=True)
    size = os.path.getsize("entry.png")
    print(f"entry.png: {img.size[0]}x{img.size[1]}, {size} bytes")
    assert img.size == (1024, 1024), "must be 1024x1024"
    assert size <= 1048576, "must be <= 1 MiB"


if __name__ == "__main__":
    main()
