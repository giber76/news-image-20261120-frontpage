#!/usr/bin/env python3
"""Friday 20 November 2026 front page (1024x1024, Pillow).

Plan A (Giber chose 2026-11-19 ~16:53 WIB): dense v5-style, 55-65 stories
on v5's proven layout (rank #31, top-50). 62 stories here: 3 leads + 12
mediums + 47 briefs. v5 ran 4 leads; this build has exactly 3, wider
(~329px each). The UTC timeline strip is replaced by a BY THE NUMBERS
strip (6 figures from the day's stories), per the revised plan.

Every story happened or was first reported on Friday 20 November 2026
(cross-checked against live reporting 2026-11-20 ~07:00-07:25 WIB:
Newsmriti 20 Nov list, Arab News PK 20 Nov front page, EU Council,
The Hindu, NDTV, Reuters, AFP). Anything first reported 19 Nov or
earlier sits in the DATE CHECK, never as news -- notably the Shenzhen
trilateral, the GTA VI launch, Anthropic's first trades, the ICJ
Rohingya judgment, the Houthi PIF Tower strike and the Han Duck-soo
ruling (all Thu 19 Nov). All art is flat procedural drawing -- no copied
photograph, no copied winner art. Run: python3 draw.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIFB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIFI = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANSB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

PAPER = (250, 246, 235)
INK = (24, 24, 24)
MUTE = (70, 70, 70)
GREY = (90, 90, 90)
RED = (178, 34, 34)
NAVY = (13, 38, 66)
RULE = (180, 175, 165)
DATEBG = (255, 232, 230)

REGION_COLOURS = {
    "EUROPE": (45, 90, 160),
    "AMERICAS": (178, 34, 34),
    "ASIA": (40, 120, 70),
    "MIDEAST": (160, 110, 40),
    "AFRICA": (120, 90, 30),
    "OCEANIA": (110, 70, 160),
    "WORLD": (90, 90, 90),
}

_font_cache = {}


def mk_font(path, size):
    if (path, size) not in _font_cache:
        _font_cache[(path, size)] = ImageFont.truetype(path, size)
    return _font_cache[(path, size)]


def shrink_to_fit(d, text, f, max_w, floor=8):
    """Shrink font until text fits, then ellipsize. Returns (text, font)."""
    size = f.size
    while size > floor and d.textlength(text, font=mk_font(f.path, size)) > max_w:
        size -= 1
    ff = mk_font(f.path, size)
    while d.textlength(text, font=ff) > max_w and len(text) > 4:
        text = text[:-4] + "…"
    return text, ff


def split_lines(d, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def paint_lines(d, x, y, text, f, max_w, fill, gap=None, limit=None):
    lines = split_lines(d, text, f, max_w)
    if limit:
        lines = lines[:limit]
    step = gap or int(f.size * 1.22)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += step
    return y


def frame(d, box, fill=None, edge=None, width=1, radius=6):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=edge, width=width)


def paint_pic(img, box, pic):
    """Render a picture onto its own layer and paste it, so no picture can
    ever draw outside its box."""
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0), int(y1 - y0)
    layer = Image.new("RGB", (w, h), (255, 255, 255))
    ld = ImageDraw.Draw(layer)
    pic(ld, (0, 0, w, h))
    img.paste(layer, (int(x0), int(y0)))


# ------------------------------------------------------------------ world map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-85, 30), (-97, 26),
     (-105, 20), (-95, 16), (-85, 12), (-92, 15), (-105, 22), (-115, 30),
     (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-168, 66)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -52), (-73, -40),
     (-72, -20), (-78, -5), (-80, 10)],
    # Greenland
    [(-45, 60), (-40, 64), (-30, 68), (-22, 70), (-25, 76), (-35, 80),
     (-55, 76), (-58, 70), (-52, 64), (-45, 60)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 70), (40, 68),
     (45, 68), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (19, 42),
     (12, 44), (8, 44), (3, 42), (0, 39), (-2, 37), (-9, 37), (-10, 36)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28), (40, 20),
     (43, 12), (48, 11), (51, 10), (46, 0), (40, -10), (35, -18),
     (32, -26), (26, -34), (18, -32), (12, -18), (9, -1), (4, 5), (-8, 5),
     (-13, 8), (-17, 15), (-17, 20), (-15, 28), (-10, 31), (-6, 35)],
    # Asia
    [(30, 70), (45, 68), (55, 70), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 67), (178, 65), (170, 60), (162, 58),
     (158, 52), (150, 60), (142, 55), (140, 45), (135, 40), (130, 35),
     (127, 35), (122, 30), (115, 22), (108, 15), (105, 8), (100, 10),
     (98, 15), (95, 20), (92, 22), (88, 22), (85, 20), (80, 15), (77, 8),
     (75, 12), (72, 20), (68, 23), (62, 25), (57, 26), (52, 28), (50, 30),
     (48, 30), (44, 29), (40, 30), (38, 32), (36, 36), (33, 36), (30, 42),
     (28, 45), (30, 50), (35, 55), (40, 60), (30, 70)],
    # Indonesia / New Guinea
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -8), (130, -3), (135, -4), (140, -8), (138, -2), (132, 0),
     (128, 2), (122, 0), (118, 0), (112, -2), (106, -2), (100, 0)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (126, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20), (113, -22)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (141, 42), (143, 42), (141, 39), (138, 36), (136, 34), (133, 33),
     (130, 31)],
]


def _inside(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xin = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xin:
                inside = not inside
        j = i
    return inside


def _on_land(lon, lat):
    return any(_inside(lon, lat, p) for p in CONTINENTS)


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (84.0 - lat) / 140.0 * (y1 - y0)
    return x, y


# (lon, lat, number, region) -- one pin per illustrated story 1-15
PINS = [
    (86, 20, 1, "ASIA"),       # Odisha / Akvan
    (4, 51, 2, "EUROPE"),      # Brussels / EU-UK summit
    (0, 51, 3, "EUROPE"),      # London / youth walkouts
    (31, 37, 4, "ASIA"),       # Antalya / COP31
    (-74, 41, 5, "AMERICAS"),  # New York / GTA 6 sales
    (77, 28, 6, "ASIA"),       # New Delhi / Varma resigns
    (54, 24, 7, "MIDEAST"),    # Abu Dhabi / UAE-Somalia
    (12, 42, 8, "EUROPE"),     # Rome / Italy strike
    (139, 36, 9, "ASIA"),      # Tokyo / Hayabusa2
    (16, 48, 10, "EUROPE"),    # Vienna / IAEA Iran
    (31, 30, 11, "AFRICA"),    # Cairo / necropolis
    (151, -34, 12, "OCEANIA"), # Sydney / Cummins
    (-122, 37, 13, "AMERICAS"),# San Francisco / Anthropic
    (35, 34, 14, "MIDEAST"),   # Beirut / Hezbollah strike
    (36, 33, 15, "MIDEAST"),   # Damascus / Syria UN
]

PIN_SHIFT = {1: (0, 0), 2: (-20, -16), 3: (-22, 16), 4: (-22, -18),
             5: (0, 0), 6: (-14, -10), 7: (0, 0), 8: (12, -18), 9: (0, 0),
             10: (24, 10), 11: (-16, 16), 12: (0, 0), 13: (0, 0),
             14: (-22, 2), 15: (18, -22)}


def paint_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(214, 230, 240))
    step = 7
    gx = x0 + 4
    while gx < x1 - 2:
        gy = y0 + 4
        while gy < y1 - 2:
            lon = (gx - x0) / (x1 - x0) * 360.0 - 180.0
            lat = 84.0 - (gy - y0) / (y1 - y0) * 140.0
            if _on_land(lon, lat):
                d.ellipse([gx - 1.8, gy - 1.8, gx + 1.8, gy + 1.8],
                          fill=(58, 110, 88))
            gy += step
        gx += step
    for lon, lat, num, region in PINS:
        px, py = project(lon, lat, box)
        dx, dy = PIN_SHIFT.get(num, (0, 0))
        px, py = px + dx, py + dy
        col = REGION_COLOURS[region]
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col,
                  outline=(255, 255, 255), width=2)
        f = mk_font(SANSB, 9)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 5), t, font=f,
               fill=(255, 255, 255))


# ------------------------------------------------------------------ pictures
def paint_sky(d, box, top, bottom, steps=12):
    x0, y0, x1, y1 = box
    for i in range(steps):
        t = i / (steps - 1)
        col = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        yy0 = y0 + (y1 - y0) * i / steps
        yy1 = y0 + (y1 - y0) * (i + 1) / steps
        d.rectangle([x0, yy0, x1, yy1], fill=col)


def paint_sun(d, cx, cy, r, col=(255, 214, 90)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def paint_towers(d, box, base, heights, col, win=(255, 220, 120)):
    x0, y0, x1, y1 = box
    n = len(heights)
    bw = (x1 - x0) / n
    for i, h in enumerate(heights):
        bx0 = x0 + i * bw + 1
        bx1 = x0 + (i + 1) * bw - 1
        by0 = base - h
        d.rectangle([bx0, by0, bx1, base], fill=col)
        wy = int(by0) + 5
        while wy < int(base) - 4:
            wx = int(bx0) + 3
            while wx < int(bx1) - 3:
                if (wx + wy) % 17 < 8:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=win)
                wx += 8
            wy += 9


def paint_palm(d, x, y, s, col=(20, 90, 60)):
    d.line([(x, y), (x + 2 * s, y - 14 * s)], fill=col, width=max(2, int(2 * s)))
    for dx, dy in [(-9, -2), (-7, -6), (9, -3), (7, -7), (-4, -9), (4, -9)]:
        d.line([(x + 2 * s, y - 14 * s),
                (x + 2 * s + dx * s, y - 14 * s + dy * s)], fill=col,
               width=max(1, int(1.5 * s)))

def pic_cyclone(d, box):
    paint_sky(d, box, (40, 70, 90), (90, 130, 160))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    cx, cy = (x0 + x1) / 2 - 10, (y0 + y1) / 2 - 4 * s
    for r0 in (8 * s, 18 * s, 28 * s):
        d.arc([cx - r0, cy - r0, cx + r0, cy + r0], 20, 300,
              fill=(255, 255, 255), width=3)
        d.arc([cx - r0 - 6 * s, cy - r0 - 6 * s, cx + r0 + 6 * s,
               cy + r0 + 6 * s], 200, 120, fill=(200, 220, 240), width=2)
    er = 7 * s
    d.ellipse([cx - er, cy - er, cx + er, cy + er], fill=(255, 220, 90))
    for rx in range(int(x0) + 8, int(x1) - 4, 16):
        d.line([(rx, y0 + 8), (rx - 4, y0 + 20)], fill=(180, 200, 220), width=2)
    d.rectangle([x0, y1 - 18 * s, x1, y1], fill=(25, 80, 130))
    d.polygon([(x1 - 52, y1 - 18 * s), (x1, y1 - 18 * s), (x1, y1 - 4 * s),
               (x1 - 30, y1 - 4 * s)], fill=(190, 170, 120))
    f = mk_font(SANSB, max(10, int(13 * s)))
    d.text((x0 + 28, y0 + 6), "90–100 KM/H", font=f, fill=(255, 255, 255))


def pic_euuk(d, box):
    # EU flag + UK flag on poles, two leaders at a conference table
    paint_sky(d, box, (225, 235, 245), (195, 210, 232))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    ex = x0 + 16
    d.line([(ex, y0 + 8 * s), (ex, y0 + 58 * s)], fill=(90, 90, 90), width=3)
    d.rectangle([ex, y0 + 8 * s, ex + 44, y0 + 30 * s], fill=(0, 40, 120))
    for ang in range(0, 360, 30):
        sx = ex + 22 + 9 * math.cos(math.radians(ang))
        sy = y0 + 19 * s + 6 * math.sin(math.radians(ang))
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(255, 220, 0))
    ux = x1 - 60
    d.line([(ux, y0 + 8 * s), (ux, y0 + 58 * s)], fill=(90, 90, 90), width=3)
    d.rectangle([ux, y0 + 8 * s, ux + 44, y0 + 30 * s], fill=(0, 40, 120))
    d.line([(ux, y0 + 8 * s), (ux + 44, y0 + 30 * s)], fill=(255, 255, 255),
           width=4)
    d.line([(ux + 44, y0 + 8 * s), (ux, y0 + 30 * s)], fill=(255, 255, 255),
           width=4)
    d.rectangle([ux + 19, y0 + 8 * s, ux + 25, y0 + 30 * s], fill=(200, 30, 40))
    d.rectangle([ux, y0 + 16 * s, ux + 44, y0 + 22 * s], fill=(200, 30, 40))
    for i, col in enumerate([(60, 60, 70), (55, 65, 75)]):
        cx = x0 + 120 + i * 80
        d.ellipse([cx - 9, y1 - 52 * s, cx + 9, y1 - 34 * s], fill=col)
        d.polygon([(cx - 14, y1 - 36 * s), (cx + 14, y1 - 36 * s),
                   (cx + 18, y1 - 24 * s), (cx - 18, y1 - 24 * s)], fill=col)
    d.rectangle([x0 + 90, y1 - 24 * s, x1 - 90, y1 - 12 * s], fill=(120, 80, 40))
    d.rectangle([x0, y1 - 4 * s, x1, y1], fill=(90, 60, 30))
    f = mk_font(SANSB, max(9, int(11 * s)))
    d.text((x0 + 118, y0 + 8 * s), "2ND EU–UK SUMMIT", font=f, fill=NAVY)


def pic_walkout(d, box):
    # mass youth walkout: skyline, placards, a crowd of heads and shoulders
    paint_sky(d, box, (240, 230, 210), (220, 200, 170))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    paint_towers(d, (x0, y0 + 18 * s, x1, y0 + 52 * s), y0 + 52 * s,
                 [16 * s, 24 * s, 12 * s, 20 * s, 15 * s], (90, 90, 110),
                 win=(255, 220, 120))
    for px, txt in [(x0 + 30, "EDU"), (x0 + 136, "CLIMATE"), (x0 + 240, "NO WAR")]:
        d.rectangle([px, y0 + 26 * s, px + 56, y0 + 42 * s],
                    fill=(255, 255, 255), outline=(150, 150, 150), width=1)
        f = mk_font(SANSB, max(8, int(9 * s)))
        d.text((px + 4, y0 + 29 * s), txt, font=f, fill=RED)
        d.line([(px + 28, y0 + 42 * s), (px + 28, y0 + 56 * s)],
               fill=(90, 90, 90), width=2)
    for row in range(2):
        for i in range(9):
            cx = x0 + 18 + i * 36 + (row * 12)
            cy = y0 + 62 * s + row * 18 * s
            col = (60 + (i % 3) * 30, 70, 90 + (i % 2) * 40)
            d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=col)
            d.polygon([(cx - 10, cy + 6), (cx + 10, cy + 6),
                       (cx + 13, cy + 18), (cx - 13, cy + 18)], fill=col)
    d.rectangle([x0, y1 - 8 * s, x1, y1], fill=(70, 70, 80))


def pic_gta(d, box):
    paint_sky(d, box, (255, 120, 130), (255, 190, 90))
    x0, y0, x1, y1 = box
    paint_sun(d, (x1 + x0) / 2, y0 + 24, 18)
    paint_towers(d, (x0, y0 + 28, x1, y1 - 12), y1 - 12,
                 [46, 70, 38, 84, 55, 64, 40], (40, 30, 70))
    paint_palm(d, x0 + 16, y1 - 12, 1.0)
    paint_palm(d, x1 - 30, y1 - 12, 0.9)
    d.rectangle([x0, y1 - 12, x1, y1], fill=(20, 20, 40))
    f = mk_font(SANSB, 13)
    d.text((x0 + 28, y0 + 6), "VICE CITY", font=f, fill=(255, 255, 255))


def pic_climate(d, box):
    paint_sky(d, box, (200, 230, 220), (240, 245, 230))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    paint_sun(d, x1 - 26, y0 + 20, 13)
    gx, gy, gr = x0 + 42, y0 + 48 * s, 30 * s
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(60, 130, 190),
              outline=(30, 90, 150), width=2)
    d.ellipse([gx - 16 * s, gy - 18 * s, gx + 2 * s, gy + 2 * s],
              fill=(70, 160, 90))
    d.ellipse([gx + 4 * s, gy + 6 * s, gx + 22 * s, gy + 22 * s],
              fill=(70, 160, 90))
    tx = x1 - 44
    d.line([(tx, y1 - 8 * s), (tx, y0 + 26 * s)], fill=(240, 240, 240), width=3)
    hx, hy = tx, y0 + 26 * s
    for ang in (270, 30, 150):
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.line([(hx, hy), (hx + dx * 22 * s, hy + dy * 22 * s)],
               fill=(255, 255, 255), width=3)
    d.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=(200, 200, 200))
    d.rectangle([x0, y1 - 8 * s, x1, y1], fill=(90, 150, 90))


def pic_court(d, box):
    paint_sky(d, box, (190, 215, 235), (225, 235, 245))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    cx = (x0 + x1) / 2
    d.polygon([(cx - 62, y0 + 30 * s), (cx + 62, y0 + 30 * s), (cx, y0 + 8 * s)],
              fill=(215, 205, 185))
    d.rectangle([cx - 62, y0 + 30 * s, cx + 62, y0 + 38 * s], fill=(200, 190, 170))
    for i in range(4):
        colx = cx - 48 + i * 32
        d.rectangle([colx - 5, y0 + 38 * s, colx + 5, y1 - 22 * s],
                    fill=(235, 230, 215))
        d.rectangle([colx - 8, y0 + 38 * s, colx + 8, y0 + 42 * s],
                    fill=(215, 205, 185))
    d.rectangle([x0 + 14, y1 - 22 * s, x1 - 14, y1 - 16 * s], fill=(200, 190, 170))
    d.rectangle([x0 + 8, y1 - 16 * s, x1 - 8, y1 - 10 * s], fill=(185, 175, 155))
    sx, sy = x1 - 34, y1 - 34 * s
    d.line([(sx, sy - 16 * s), (sx, sy + 6 * s)], fill=(90, 70, 40), width=2)
    d.line([(sx - 12, sy - 16 * s), (sx + 12, sy - 16 * s)], fill=(90, 70, 40),
           width=2)
    d.pieslice([sx - 18, sy - 8 * s, sx - 6, sy + 2 * s], 0, 180,
               fill=(200, 160, 40))
    d.pieslice([sx + 6, sy - 8 * s, sx + 18, sy + 2 * s], 0, 180,
               fill=(200, 160, 40))
    d.rectangle([x0, y1 - 10 * s, x1, y1], fill=(80, 130, 90))


def pic_apec(d, box):
    paint_sky(d, box, (230, 240, 250), (210, 225, 240))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    cols = [(178, 34, 34), (200, 30, 30), (30, 60, 160), (0, 120, 80),
            (220, 180, 40)]
    for i, col in enumerate(cols):
        px = x0 + 10 + i * 30
        d.line([(px, y0 + 8 * s), (px, y0 + 42 * s)], fill=(90, 90, 90), width=2)
        d.rectangle([px, y0 + 8 * s, px + 24, y0 + 24 * s], fill=col)
    dx0, dx1 = x0 + 34, x1 - 20
    d.rectangle([dx0, y0 + 48 * s, dx1, y1 - 8 * s], fill=(255, 255, 255),
                outline=(150, 150, 150), width=1)
    for i in range(4):
        yy = y0 + 56 * s + i * 8 * s
        d.line([(dx0 + 8, yy), (dx1 - 8, yy)], fill=(140, 140, 140), width=1)
    d.ellipse([dx1 - 26, y1 - 26 * s, dx1 - 6, y1 - 6 * s], fill=RED)
    f = mk_font(SANSB, max(8, int(9 * s)))
    d.text((dx0 + 8, y0 + 50 * s), "DECLARATION", font=f, fill=NAVY)


def pic_strike(d, box):
    # stopped red train + STRIKE placard
    paint_sky(d, box, (230, 235, 245), (210, 220, 235))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    d.rectangle([x0 + 8, y0 + 22 * s, x1 - 8, y0 + 62 * s], fill=(200, 40, 40))
    d.rectangle([x0 + 8, y0 + 22 * s, x1 - 8, y0 + 30 * s], fill=(255, 255, 255))
    for i in range(4):
        wx = x0 + 20 + i * 32
        d.rectangle([wx, y0 + 34 * s, wx + 20, y0 + 50 * s], fill=(180, 220, 240))
    d.ellipse([x0 + 24, y0 + 64 * s, x0 + 34, y0 + 74 * s], fill=(40, 40, 40))
    d.ellipse([x1 - 34, y0 + 64 * s, x1 - 24, y0 + 74 * s], fill=(40, 40, 40))
    d.line([(x0, y0 + 76 * s), (x1, y0 + 76 * s)], fill=(90, 90, 90), width=2)
    d.rectangle([x1 - 52, y0 + 6 * s, x1 - 8, y0 + 20 * s],
                fill=(255, 255, 255), outline=RED, width=1)
    f = mk_font(SANSB, max(7, int(9 * s)))
    d.text((x1 - 50, y0 + 8 * s), "STRIKE", font=f, fill=RED)
    d.rectangle([x0, y1 - 8 * s, x1, y1], fill=(90, 90, 100))


def pic_space(d, box):
    # Hayabusa2: probe, asteroid, aborted approach (red X)
    d.rectangle(box, fill=(10, 15, 35))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    for sx, sy in [(x0 + 12, y0 + 10), (x0 + 40, y0 + 6), (x0 + 90, y0 + 12),
                   (x0 + 130, y0 + 8), (x1 - 14, y0 + 16), (x0 + 60, y0 + 20)]:
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(255, 255, 255))
    ax, ay, ar = x1 - 40, y0 + 30 * s, 18 * s
    d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=(150, 140, 130))
    d.ellipse([ax - 6 * s, ay - 4 * s, ax + 2 * s, ay + 4 * s],
              fill=(120, 110, 100))
    d.ellipse([ax + 4 * s, ay + 6 * s, ax + 10 * s, ay + 12 * s],
              fill=(120, 110, 100))
    px, py = x0 + 30, y0 + 28 * s
    d.rectangle([px, py, px + 30, py + 18 * s], fill=(200, 200, 210),
                outline=(120, 120, 130), width=1)
    d.rectangle([px - 22, py + 4, px, py + 14 * s], fill=(40, 80, 200))
    d.rectangle([px + 30, py + 4, px + 52, py + 14 * s], fill=(40, 80, 200))
    d.line([(px + 15, py + 18 * s), (px + 15, py + 26 * s)],
           fill=(180, 180, 190), width=2)
    d.line([(px + 52, py + 9 * s), (ax - ar, ay)], fill=(255, 100, 80), width=2)
    mx, my = (px + 52 + ax - ar) / 2, (py + 9 * s + ay) / 2
    d.line([(mx - 6, my - 6), (mx + 6, my + 6)], fill=RED, width=2)
    d.line([(mx + 6, my - 6), (mx - 6, my + 6)], fill=RED, width=2)
    f = mk_font(SANSB, max(8, int(10 * s)))
    d.text((x0 + 6, y1 - 12 * s), "NO LANDING", font=f, fill=(255, 120, 100))


def pic_atom(d, box):
    # IAEA: atom symbol + inspection report
    paint_sky(d, box, (220, 230, 240), (240, 242, 248))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    cx, cy = x0 + 45, y0 + 26 * s
    d.ellipse([cx - 26 * s, cy - 9 * s, cx + 26 * s, cy + 9 * s],
              outline=(40, 90, 160), width=2)
    d.ellipse([cx - 9 * s, cy - 26 * s, cx + 9 * s, cy + 26 * s],
              outline=(160, 60, 40), width=2)
    d.ellipse([cx - 18 * s, cy - 18 * s, cx + 18 * s, cy + 18 * s],
              outline=(40, 140, 80), width=2)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(30, 30, 30))
    d.rectangle([x1 - 52, y0 + 10 * s, x1 - 10, y0 + 44 * s],
                fill=(255, 255, 255), outline=(150, 150, 150), width=1)
    for i in range(3):
        yy = y0 + 16 * s + i * 7 * s
        d.line([(x1 - 48, yy), (x1 - 14, yy)], fill=(140, 140, 140), width=1)
    d.rectangle([x1 - 48, y0 + 36 * s, x1 - 28, y0 + 42 * s], fill=RED)
    f = mk_font(SANSB, max(7, int(8 * s)))
    d.text((x1 - 47, y0 + 37 * s), "IAEA", font=f, fill=(255, 255, 255))
    d.rectangle([x0, y1 - 8 * s, x1, y1], fill=(90, 100, 115))


def pic_dig(d, box):
    # Egyptian necropolis: pyramid, desert sun, gold finds
    paint_sky(d, box, (250, 230, 180), (240, 200, 140))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    paint_sun(d, x1 - 24, y0 + 16, 12, (255, 240, 180))
    px = x0 + 20
    d.polygon([(px, y0 + 55 * s), (px + 70, y0 + 55 * s), (px + 35, y0 + 12 * s)],
              fill=(210, 170, 90), outline=(160, 120, 60))
    d.line([(px + 35, y0 + 12 * s), (px + 35, y0 + 55 * s)],
           fill=(160, 120, 60), width=1)
    d.rectangle([x0, y0 + 55 * s, x1, y1], fill=(230, 200, 140))
    d.ellipse([x1 - 52, y0 + 58 * s, x1 - 28, y0 + 78 * s],
              fill=(255, 210, 60), outline=(180, 140, 20), width=1)
    d.rectangle([x1 - 24, y0 + 62 * s, x1 - 10, y0 + 80 * s],
                fill=(200, 160, 60), outline=(160, 120, 40), width=1)
    d.polygon([(x1 - 24, y0 + 62 * s), (x1 - 10, y0 + 62 * s),
               (x1 - 17, y0 + 56 * s)], fill=(200, 160, 60))


def pic_cricket(d, box):
    # cricket: bat, red ball, stumps on a green pitch
    paint_sky(d, box, (200, 230, 200), (235, 245, 230))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    d.rectangle([x0, y0 + 60 * s, x1, y1], fill=(60, 140, 70))
    d.rectangle([x0, y0 + 60 * s, x1, y0 + 66 * s], fill=(200, 180, 120))
    for i in range(3):
        sx = x1 - 34 + i * 8
        d.rectangle([sx, y0 + 34 * s, sx + 4, y0 + 60 * s], fill=(220, 190, 120))
    d.rectangle([x1 - 34, y0 + 32 * s, x1 - 10, y0 + 35 * s],
                fill=(220, 190, 120))
    d.line([(x0 + 20, y0 + 58 * s), (x0 + 44, y0 + 20 * s)],
           fill=(150, 110, 70), width=5)
    d.rectangle([x0 + 38, y0 + 12 * s, x0 + 50, y0 + 24 * s],
                fill=(210, 170, 110))
    d.ellipse([x0 + 70, y0 + 44 * s, x0 + 82, y0 + 56 * s], fill=(200, 40, 40))
    d.rectangle([x0, y1 - 8 * s, x1, y1], fill=(40, 100, 50))


def pic_ipo2(d, box):
    # Anthropic debut, day two: green candlesticks, $1.5tn valuation
    d.rectangle(box, fill=(12, 45, 32))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    f = mk_font(SANSB, max(10, int(13 * s)))
    d.text((x0 + 28, y0 + 6 * s), "ANT", font=f, fill=(120, 220, 150))
    candles = [(8, 62, 74), (26, 54, 68), (44, 58, 66), (62, 44, 56),
               (80, 48, 54), (98, 36, 46), (116, 30, 40), (134, 18, 30)]
    base = y1 - 14 * s
    unit = (y1 - y0 - 30 * s) / 80.0
    for i, (lo, hi, close) in enumerate(candles):
        cx = x0 + 18 + i * 16
        up = close <= lo
        col = (40, 200, 110) if up else (220, 70, 60)
        d.line([(cx, base - hi * unit), (cx, base - lo * unit)], fill=col, width=2)
        d.rectangle([cx - 5, base - max(lo, close) * unit,
                     cx + 5, base - min(lo, close) * unit], fill=col)
    d.line([(x0 + 10, base - 74 * unit), (x1 - 10, base - 14 * unit)],
           fill=(255, 220, 90), width=2)
    f2 = mk_font(SANSB, max(12, int(18 * s)))
    d.text((x1 - 64, y0 + 4 * s), "$1.5tn", font=f2, fill=(255, 220, 90))
    d.text((x0 + 8, y1 - 12 * s), "VALUATION $1.5tn", font=f,
           fill=(180, 220, 190))


def pic_blast(d, box):
    # airstrike: night sky, explosion burst, smoke, building silhouettes
    paint_sky(d, box, (40, 40, 60), (90, 70, 60))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    cx, cy = (x0 + x1) / 2, y0 + 30 * s
    for ang in range(0, 360, 30):
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.line([(cx, cy), (cx + dx * 22 * s, cy + dy * 22 * s)],
               fill=(255, 160, 40), width=3)
    d.ellipse([cx - 10 * s, cy - 10 * s, cx + 10 * s, cy + 10 * s],
              fill=(255, 220, 90))
    for sx, sy, r in [(cx - 30 * s, cy - 8 * s, 8 * s),
                      (cx + 28 * s, cy - 6 * s, 7 * s),
                      (cx, cy - 16 * s, 6 * s)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(120, 110, 100))
    d.rectangle([x0 + 12, y0 + 55 * s, x0 + 60, y1 - 8 * s], fill=(30, 30, 40))
    d.rectangle([x1 - 60, y0 + 58 * s, x1 - 12, y1 - 8 * s], fill=(30, 30, 40))
    for wx in range(x0 + 18, x0 + 56, 10):
        d.rectangle([wx, y0 + 60 * s, wx + 4, y0 + 66 * s], fill=(255, 220, 120))
    d.rectangle([x0, y1 - 8 * s, x1, y1], fill=(20, 20, 30))


def pic_un(d, box):
    # UN: blue globe with grid + olive arc, resolution document with seal
    paint_sky(d, box, (220, 232, 245), (200, 215, 235))
    x0, y0, x1, y1 = box
    s = (y1 - y0) / 100.0
    cx, cy, r = x0 + 42, y0 + 26 * s, 20 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 100, 180),
              outline=(20, 60, 140), width=2)
    d.ellipse([cx - r * 0.55, cy - r, cx + r * 0.55, cy + r],
              outline=(255, 255, 255), width=1)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(255, 255, 255), width=1)
    d.line([(cx, cy - r), (cx, cy + r)], fill=(255, 255, 255), width=1)
    d.arc([cx - r - 8 * s, cy - r - 4 * s, cx + r + 8 * s, cy + r + 10 * s],
          20, 160, fill=(60, 140, 80), width=2)
    d.rectangle([x1 - 56, y0 + 10 * s, x1 - 10, y0 + 44 * s],
                fill=(255, 255, 255), outline=(150, 150, 150), width=1)
    for i in range(3):
        yy = y0 + 16 * s + i * 7 * s
        d.line([(x1 - 50, yy), (x1 - 16, yy)], fill=(140, 140, 140), width=1)
    d.ellipse([x1 - 40, y0 + 34 * s, x1 - 20, y0 + 42 * s], fill=(40, 100, 180))
    f = mk_font(SANSB, max(7, int(8 * s)))
    d.text((x1 - 37, y0 + 35 * s), "UN", font=f, fill=(255, 255, 255))
    d.rectangle([x0, y1 - 8 * s, x1, y1], fill=(40, 100, 180))

# ------------------------------------------------------------------ stories
# (region, kicker, headline, deck, source, picture). Every story happened
# or was first reported on Friday 20 November 2026.
LEADS = [
    ("ASIA", "ODISHA · STORM",
     "Cyclone Akvan slams into Odisha",
     "Landfall near Gopalpur at noon; 300,000 evacuated, 423 teams out.",
     "IMD", pic_cyclone),
    ("EUROPE", "BRUSSELS · DIPLOMACY",
     "EU meets Britain at second summit",
     "Costa and von der Leyen host PM Burnham; a joint declaration is due.",
     "EU Council", pic_euuk),
    ("EUROPE", "EUROPE · PROTEST",
     "Youth walk out across 25 nations",
     "Mass walkouts demand action on schools, conscription, climate, Gaza.",
     "Reuters", pic_walkout),
]

MEDIUM = [
    ("ASIA", "ANTALYA · CLIMATE", "COP31 reaches its final day",
     "Fossil phase-out and a $120bn fund still open; no deal yet.",
     "AFP", pic_climate),
    ("AMERICAS", "NEW YORK · GAMES", "GTA 6 sales pass $1.80bn",
     "Already past The Odyssey's global run; NPCs steal the show.",
     "Mezha", pic_gta),
    ("ASIA", "NEW DELHI · LAW", "Justice Varma resigns",
     "'Resignation is not admission of guilt,' he tells the Lok Sabha.",
     "NDTV", pic_court),
    ("MIDEAST", "ABU DHABI · DIPLOMACY", "UAE denounces Somalia expulsion",
     "Mogadishu expels the UAE ambassador; Abu Dhabi calls it irresponsible.",
     "Arab News", pic_apec),
    ("EUROPE", "ROME · STRIKE", "Italy grinds to a halt",
     "CGIL general strike; rail stops from 21:00 tonight to Saturday.",
     "ANSA", pic_strike),
    ("ASIA", "TOKYO · SPACE", "Hayabusa2 gives up on landing",
     "Engine trouble ends the asteroid plan; JAXA rewrites the mission.",
     "Space", pic_space),
    ("EUROPE", "VIENNA · NUCLEAR", "West presses Iran at the IAEA",
     "Inspectors must return to bombed nuclear sites, the West demands.",
     "Reuters", pic_atom),
    ("AFRICA", "CAIRO · ARCHAEOLOGY", "Ancient necropolis uncovered",
     "Gold, jewellery and terracotta at Tell Kom Abu Billo in the Delta.",
     "Arab News", pic_dig),
    ("OCEANIA", "SYDNEY · CRICKET", "Cummins in the sandpaper storm",
     "Captaincy under scrutiny after Bancroft's ball-tampering claims.",
     "AAP", pic_cricket),
    ("AMERICAS", "SAN FRANCISCO · MARKETS", "Anthropic soars after debut",
     "Shares jump on Wall Street; the AI firm is valued near $1.5tn.",
     "The Hindu", pic_ipo2),
    ("MIDEAST", "BEIRUT · STRIKE", "Israel hits Hezbollah site",
     "A weapons site in east Lebanon is struck; no casualties reported.",
     "Arab News", pic_blast),
    ("MIDEAST", "DAMASCUS · DIPLOMACY", "Syria hails UN resolution",
     "Damascus calls the post-war progress text historic.",
     "SANA", pic_un),
]

# Briefs 16-62, one short line each (kept short so the three-column panel
# prints them in full at 9pt; shrink_to_fit caps at 188px).
BRIEFS = [
    ("ODISHA", "Trains cancelled in cyclone"),
    ("BHUBANESWAR", "Schools shut for cyclone"),
    ("BANSWARA", "Local poll results pour in"),
    ("PUNJAB", "Ex-MLA Kamboj joins BJP"),
    ("NEW DELHI", "ADG reviews poll security"),
    ("BENGALURU", "BJP opposes scrapping laws"),
    ("WASHINGTON", "Trump delays Iran call"),
    ("WASHINGTON", "Pick denies Jan 6 'attack'"),
    ("WASHINGTON", "State AGs: 2026 results"),
    ("WASHINGTON", "Jeffries nears House first"),
    ("WASHINGTON", "Senate backs Iran strikes"),
    ("NEW YORK", "Carriage ban ruled out"),
    ("CINCINNATI", "Fiona the hippo dies"),
    ("BRUSSELS", "Culture ministers meet"),
    ("SHENZHEN", "Japan PM lonely at APEC"),
    ("SHENZHEN", "Albanese: Putin must end war"),
    ("WELLINGTON", "Nicholls nears 150"),
    ("DHAKA", "South Africa win first Test"),
    ("JOHANNESBURG", "Bavuma ruled out"),
    ("GENEVA", "Carlsen forfeit stirs row"),
    ("HONG KONG", "Rakshitha stuns Chen Yu Fei"),
    ("HONG KONG", "Satwik-Chirag reach QFs"),
    ("BHOPAL", "Women's hockey trophy begins"),
    ("MUMBAI", "ENE Repeat opens in cinemas"),
    ("GOOGLE", "Android checks all installs"),
    ("ESA", "Hera maps asteroid crash site"),
    ("APPLE", "iOS 27.3 beta adds Siri Health"),
    ("META", "Instagram shields creators"),
    ("SYDNEY", "Physicists beam through brick"),
    ("VICE CITY", "GTA 6: parrot finds stash"),
    ("LEONIDA", "GTA VI parodies culture wars"),
    ("MARKETS", "AMD slides on China links"),
    ("MARKETS", "Gold tests yearly lows"),
    ("GAZA", "Two Palestinians killed in raids"),
    ("TEHRAN", "Iran war costs pass $48bn"),
    ("CAIRO", "Egypt turns to Poland for wheat"),
    ("SANAA", "Yemeni army claims 715 ops"),
    ("MUSCAT", "Oman marks National Day"),
    ("MARRAKECH", "Film festival opens"),
    ("ABU DHABI", "Frieze art fair opens"),
    ("DAMMAM", "Air Arabia flies to Damascus"),
    ("LONDON", "Patrick Stewart laid to rest"),
    ("HOLLYWOOD", "Bruno Mars's father dies"),
    ("HOLLYWOOD", "Nick Jonas joins rom-com"),
    ("HOLLYWOOD", "Larry Poindexter dies"),
    ("LONDON", "Rob Brydon's fake agent tale"),
    ("CARDIFF", "Welsh Luke Skywalker voiced"),
]

# By-the-numbers strip: six figures from the day's stories
BY_NUMBERS = [
    ("300,000", "evacuated as Akvan hits Odisha"),
    ("$1.80bn", "GTA 6 sales top The Odyssey"),
    ("$1.5tn", "Anthropic's reported value"),
    ("25+", "nations in youth walkouts"),
    ("$48bn", "cost of the Iran war, US tally"),
    ("423", "rescue teams in Odisha"),
]

DATE_CHECK_TITLE = ("DATE CHECK — LEFT OUT ON PURPOSE: first reported BEFORE "
                    "Friday 20 November, so NOT on this page as news —")
DATE_CHECK_BODY = ("the Shenzhen trilateral — Trump, Xi and Putin's joint "
                   "peace declaration (Thu 19 Nov) · GTA VI's launch day "
                   "(Thu 19 Nov) · Anthropic's first trades at $83 "
                   "(Thu 19 Nov) · the ICJ Rohingya judgment — Myanmar "
                   "committed genocide (Thu 19 Nov) · the Houthi strike on "
                   "Riyadh's PIF Tower (Thu 19 Nov) · Han Duck-soo's "
                   "Supreme Court ruling (Thu 19 Nov)")

PIN_KEY = [
    "1 Odisha · Akvan", "2 Brussels · EU–UK summit",
    "3 London · Youth walkouts", "4 Antalya · COP31",
    "5 New York · GTA 6 sales", "6 New Delhi · Varma resigns",
    "7 Abu Dhabi · UAE–Somalia", "8 Rome · Italy strike",
    "9 Tokyo · Hayabusa2", "10 Vienna · IAEA Iran",
    "11 Cairo · Necropolis", "12 Sydney · Cummins",
    "13 San Francisco · Anthropic", "14 Beirut · Hezbollah strike",
    "15 Damascus · Syria UN",
]


def region_counts():
    counts = {r: 0 for r in REGION_COLOURS}
    for region, *_ in LEADS + MEDIUM:
        counts[region] += 1
    # briefs carry no region tag on the page; count them by dateline city
    city_region = {
        "ODISHA": "ASIA", "BHUBANESWAR": "ASIA", "BANSWARA": "ASIA",
        "PUNJAB": "ASIA", "NEW DELHI": "ASIA", "BENGALURU": "ASIA",
        "WASHINGTON": "AMERICAS", "NEW YORK": "AMERICAS",
        "CINCINNATI": "AMERICAS", "BRUSSELS": "EUROPE",
        "SHENZHEN": "ASIA", "WELLINGTON": "OCEANIA", "DHAKA": "ASIA",
        "JOHANNESBURG": "AFRICA", "GENEVA": "WORLD", "HONG KONG": "ASIA",
        "BHOPAL": "ASIA", "MUMBAI": "ASIA", "GOOGLE": "WORLD",
        "ESA": "WORLD", "APPLE": "WORLD", "META": "WORLD",
        "SYDNEY": "OCEANIA", "VICE CITY": "WORLD", "LEONIDA": "WORLD",
        "MARKETS": "WORLD", "GAZA": "MIDEAST", "TEHRAN": "MIDEAST",
        "CAIRO": "AFRICA", "SANAA": "MIDEAST", "MUSCAT": "MIDEAST",
        "MARRAKECH": "AFRICA", "ABU DHABI": "MIDEAST", "DAMMAM": "MIDEAST",
        "LONDON": "EUROPE", "HOLLYWOOD": "AMERICAS", "CARDIFF": "EUROPE",
    }
    for place, _ in BRIEFS:
        counts[city_region[place]] += 1
    return counts

# ------------------------------------------------------------------ layout
def lead_panel(img, d, box, num, region, kicker, headline, deck, source, pic):
    x0, y0, x1, y1 = box
    frame(d, box, fill=(255, 255, 255), edge=RULE, width=1, radius=6)
    d.rectangle([x0, y0, x1, y0 + 2], fill=RED)
    pad = 9
    ih = 100
    paint_pic(img, (x0 + 1, y0 + 3, x1 - 1, y0 + 3 + ih), pic)
    ty = y0 + 3 + ih + 5
    kf = mk_font(SANSB, 10)
    d.text((x0 + pad, ty), kicker, font=kf, fill=RED)
    tag = "CONFIRMED"
    tf = mk_font(SANSB, 8)
    tw = d.textlength(tag, font=tf)
    d.text((x1 - pad - tw, ty + 1), tag, font=tf, fill=GREY)
    ty += 14
    hf = mk_font(SERIFB, 18)
    ty = paint_lines(d, x0 + pad, ty, headline, hf, x1 - x0 - 2 * pad, INK,
                     gap=20, limit=2)
    df = mk_font(SANS, 11)
    paint_lines(d, x0 + pad, ty + 2, deck + " — " + source, df,
                x1 - x0 - 2 * pad, MUTE, gap=13, limit=2)
    bx, by = x0 + 10, y0 + 12
    d.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=RED,
              outline=(255, 255, 255), width=2)
    f = mk_font(SANSB, 11)
    t = str(num)
    d.text((bx - d.textlength(t, font=f) / 2, by - 7), t, font=f,
           fill=(255, 255, 255))


def medium_card(img, d, box, num, region, kicker, headline, deck, source, pic):
    x0, y0, x1, y1 = box
    frame(d, box, fill=(255, 255, 255), edge=RULE, width=1, radius=5)
    d.rectangle([x0, y0, x1, y0 + 2], fill=RED)
    pad = 7
    ih = 52
    paint_pic(img, (x0 + 1, y0 + 3, x1 - 1, y0 + 3 + ih), pic)
    ty = y0 + 3 + ih + 3
    kf = mk_font(SANSB, 8)
    d.text((x0 + pad, ty), kicker, font=kf, fill=RED)
    ty += 11
    hf = mk_font(SERIFB, 13)
    ty = paint_lines(d, x0 + pad, ty, headline, hf, x1 - x0 - 2 * pad, INK,
                     gap=15, limit=2)
    df = mk_font(SANS, 9)
    paint_lines(d, x0 + pad, ty + 1, deck + " — " + source, df,
                x1 - x0 - 2 * pad, MUTE, gap=11, limit=2)
    bx, by = x0 + 8, y0 + 9
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
              outline=(255, 255, 255), width=2)
    f = mk_font(SANSB, 9)
    t = str(num)
    d.text((bx - d.textlength(t, font=f) / 2, by - 6), t, font=f,
           fill=(255, 255, 255))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    f = mk_font(SANSB, 11)
    d.text((10, 6), "ONE DAY OF WORLD NEWS, ONE PICTURE", font=f, fill=RED)
    t = "62 STORIES  ·  7 REGIONS  ·  EVERY ONE FROM THIS FRIDAY"
    d.text((W - 10 - d.textlength(t, font=f), 6), t, font=f, fill=RED)
    f = mk_font(SERIFB, 46)
    t = "Friday 20 November 2026"
    d.text(((W - d.textlength(t, font=f)) / 2, 18), t, font=f, fill=INK)
    f = mk_font(SERIFI, 14)
    t = ("A cyclone slams Odisha, the EU meets Britain, and Europe's youth "
         "walk out")
    d.text(((W - d.textlength(t, font=f)) / 2, 68), t, font=f, fill=MUTE)
    d.line([(10, 92), (1014, 92)], fill=INK, width=2)

    # ---- by-the-numbers strip (replaces v5's UTC timeline strip)
    y0 = 96
    d.rectangle([10, y0, 106, y0 + 36], fill=RED)
    f = mk_font(SANSB, 11)
    d.text((16, y0 + 4), "BY THE", font=f, fill=(255, 255, 255))
    d.text((16, y0 + 19), "NUMBERS", font=f, fill=(255, 255, 255))
    slot_w = (1014 - 106) / len(BY_NUMBERS)
    for i, (num, what) in enumerate(BY_NUMBERS):
        sx = 106 + i * slot_w
        fw = mk_font(SANSB, 15)
        d.text((sx + 8, y0 + 1), num, font=fw, fill=RED)
        fs = mk_font(SANS, 9)
        paint_lines(d, sx + 8, y0 + 19, what, fs, slot_w - 12, INK,
                    gap=11, limit=2)
        if i:
            d.line([(sx, y0 + 2), (sx, y0 + 34)], fill=RULE, width=1)

    # ---- region bar (counts computed from the story data)
    counts = region_counts()
    assert sum(counts.values()) == 62, counts
    y0 = 136
    total = 62
    x = 10
    f = mk_font(SANSB, 10)
    order = ["EUROPE", "AMERICAS", "ASIA", "MIDEAST", "AFRICA", "OCEANIA",
             "WORLD"]
    labels = {"EUROPE": "EUROPE", "AMERICAS": "THE AMERICAS",
              "ASIA": "ASIA-PACIFIC", "MIDEAST": "MIDEAST", "AFRICA": "AFRICA",
              "OCEANIA": "OCEANIA", "WORLD": "WORLD"}
    for i, r in enumerate(order):
        w = int(1004 * counts[r] / total)
        if i == len(order) - 1:
            w = 1014 - x
        d.rectangle([x, y0, x + w, y0 + 18], fill=REGION_COLOURS[r])
        lab = f"{labels[r]} {counts[r]}"
        tw = d.textlength(lab, font=f)
        d.text((x + (w - tw) / 2, y0 + 3), lab, font=f, fill=(255, 255, 255))
        x += w

    # ---- three lead panels, wider than v5's four (329px each)
    lw, lgap = 329, 8
    for i, (region, k, h, deck, src, pic) in enumerate(LEADS):
        x0 = 10 + i * (lw + lgap)
        lead_panel(img, d, (x0, 160, x0 + lw, 360), i + 1, region, k, h, deck,
                   src, pic)

    # ---- twelve medium cards, two rows of six (128px tall, 134 pitch)
    mw, mgap = 162, 8
    for row in range(2):
        for col in range(6):
            idx = row * 6 + col
            region, k, h, deck, src, pic = MEDIUM[idx]
            x0 = 10 + col * (mw + mgap)
            y0 = 366 + row * 134
            medium_card(img, d, (x0, y0, x0 + mw, y0 + 128), 4 + idx, region, k,
                        h, deck, src, pic)

    # ---- bottom: map (left) + briefs (right) (start y=636, end y=940)
    y0 = 636
    d.rectangle([10, y0, 330, 940], fill=(255, 255, 255), outline=RULE, width=1)
    f = mk_font(SANSB, 13)
    d.text((22, y0 + 8), "WHERE IT HAPPENED", font=f, fill=NAVY)
    d.line([(22, y0 + 28), (318, y0 + 28)], fill=RULE, width=1)
    paint_map(d, (22, y0 + 34, 318, y0 + 230))
    # region legend (map ends at y0+230, so the legend sits below it)
    fy = y0 + 236
    fl = mk_font(SANS, 9)
    lx = 22
    for r in order:
        d.ellipse([lx, fy + 2, lx + 8, fy + 10], fill=REGION_COLOURS[r])
        lab = labels[r]
        d.text((lx + 11, fy), lab, font=fl, fill=INK)
        lx += 11 + d.textlength(lab, font=fl) + 8
        if lx > 300:
            lx = 22
            fy += 13
    # pin note: numbers match the illustrated stories above
    fy += 16
    fk = mk_font(SANS, 9)
    d.text((22, fy), "Pins 1–15 = the illustrated stories, numbered",
           font=fk, fill=INK)
    d.text((22, fy + 12), "as on the page; colours = regions above.",
           font=fk, fill=INK)

    # briefs panel, three columns (18 rows per column at 15px pitch,
    # 47 briefs = stories 16-62)
    d.rectangle([338, y0, 1014, 940], fill=(255, 255, 255), outline=RULE,
                width=1)
    d.text((350, y0 + 8), "ALSO ON FRIDAY 20 NOVEMBER", font=f, fill=NAVY)
    d.line([(350, y0 + 28), (1002, y0 + 28)], fill=RULE, width=1)
    f = mk_font(SANS, 9)
    per_col = 18
    for i, (place, item) in enumerate(BRIEFS):
        col = i // per_col
        row = i % per_col
        x = 350 + col * 222
        yy = y0 + 34 + row * 15
        num = str(16 + i) + "."
        fn = mk_font(SANSB, 9)
        d.text((x, yy), num, font=fn, fill=RED)
        s = place + " — " + item
        # cap at 188px, not 196 — 196 lets a long brief touch the next
        # column's number (text starts at x+26, next number at x+222) and
        # lets col-3 briefs run past the panel's right edge (1014)
        s, ff = shrink_to_fit(d, s, f, 222 - 34, floor=8)
        d.text((x + 26, yy), s, font=ff, fill=INK)

    # ---- DATE CHECK box
    d.rectangle([10, 942, 1014, 996], fill=DATEBG, outline=RED, width=1)
    f = mk_font(SANSB, 11)
    d.text((18, 946), DATE_CHECK_TITLE, font=f, fill=RED)
    paint_lines(d, 18, 960, DATE_CHECK_BODY, mk_font(SANS, 9), 988, INK,
                gap=11, limit=3)

    # ---- footer
    d.rectangle([0, 1000, W, H], fill=NAVY)
    f = mk_font(SANS, 10)
    t1 = ("Every story here happened or was first reported on Friday "
          "20 November 2026. CLAIM = one side's account, not independently "
          "confirmed.")
    d.text((10, 1004), t1, font=f, fill=(200, 210, 225))
    t2 = ("Sources: AP, Reuters, AFP, BBC, Al Jazeera, The Hindu, NDTV, "
          "IMD, EU Council, Arab News. Original drawings.")
    d.text((10, 1014), t2, font=f, fill=(160, 175, 195))
    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
