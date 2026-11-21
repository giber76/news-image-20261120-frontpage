#!/usr/bin/env python3
"""Friday 20 November 2026 — one front page (v4, 36 stories).

Re-authored from scratch for round 2. Winner study (top 10, 20 Nov):
winners run 24-40 stories (mean 34.2); our 69-story v3 scored 971,449
(#1,182) while 36-story pages top the board. v4 cuts to 36 stories
(3 leads + 10 mediums + 23 briefs), leads with the winners' consensus
trio (Akvan, Kyiv missiles, COP31), adds a timeline strip and a
BY FIELD bar, switches to a solid dark map and 2-column briefs.
Every story happened or was first reported on Friday 20 November 2026.
See STORIES.md and news-image-20261120-v4-study.md.
Deterministic: no randomness, no timestamps in the image.

v7: same 36 stories and layout; the abstract illustrations are redrawn
as literal scenes (Kyiv's trend-line missiles, the cricket field, the
strike dots, the yen number, the ballot bar, the GTA sunset, the small
cyclone) and a HOW SURE legend marks each card CONFIRMED / CLAIM /
FORECAST (dots in the kicker rows).
"""

import math
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 243, 232)
PAPER = (250, 246, 236)
INK = (26, 32, 44)
RED = (178, 34, 34)
DARKRED = (139, 0, 0)
NAVY = (18, 38, 66)
DARKBLUE = (16, 42, 80)
TEAL = (0, 110, 110)
GREY = (110, 110, 105)
LIGHTGREY = (200, 198, 188)
GOLD = (184, 134, 11)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF = FONT_DIR + "DejaVuSerif-Bold.ttf"
SERIF_REG = FONT_DIR + "DejaVuSerif.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
LIB_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
LIB_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, fnt, max_w):
    """Wrap text to fit max_w pixels, returning a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, fill, max_w, line_h=None, max_lines=None):
    """Draw wrapped text, return the y after the last line."""
    if line_h is None:
        line_h = fnt.size + 3
    lines = wrap_text(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += line_h
    return y


def num_badge(draw, x, y, n, r=11):
    """Red circle with a white number, top-left at (x, y)."""
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], fill=RED, outline=(255, 255, 255), width=1)
    f = font(SANS_BOLD, 12)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((x + r - tw / 2, y + r - 8), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- data

LEADS = [
    {
        "n": 1, "place": "ODISHA", "field": "STORM",
        "head": "Cyclone Akvan slams into Odisha",
        "dek": "Landfall near Gopalpur at noon; 300,000 evacuated, 423 rescue teams out. — IMD",
        "scene": "cyclone",
    },
    {
        "n": 2, "place": "KYIV", "field": "WAR",
        "head": "Russia fires a wave of ballistic missiles at Kyiv",
        "dek": "Missiles from 01:25; 3 Dnipro bridges hit. — Kyiv Independent",
        "scene": "kyiv",
    },
    {
        "n": 3, "place": "ANTALYA", "field": "CLIMATE",
        "head": "COP31 reaches its final day deadlocked",
        "dek": "Phase-out dropped; $120bn adaptation fund unresolved. — AFP",
        "scene": "cop31",
    },
]

MEDIUMS = [
    {"n": 4, "place": "BRUSSELS", "field": "DIPLOMACY",
     "head": "EU meets Britain at second EU–UK summit",
     "dek": "Costa and von der Leyen host PM Burnham; declaration due. — EU Council",
     "scene": "flags"},
    {"n": 5, "place": "SEOUL / TOKYO", "field": "MARKETS",
     "head": "AI sell-off sinks Asia to worst week since 2020",
     "dek": "Nikkei −4.8%, KOSPI −5.7%, SoftBank −15%. — Morningstar",
     "scene": "chart_down"},
    {"n": 6, "place": "NEW YORK", "field": "GAMES",
     "head": "GTA 6 sales pass $1.80bn",
     "dek": "Already past The Odyssey's global run. — Mezha",
     "scene": "gta"},
    {"n": 7, "place": "SAN FRANCISCO", "field": "MARKETS",
     "head": "Anthropic ends its first day up 17%",
     "dek": "Shares close at $97.17, above the $83 offer. — Morningstar",
     "scene": "chart_up"},
    {"n": 8, "place": "WELLINGTON", "field": "CRICKET",
     "head": "Phillips makes history with 118",
     "dek": "First batter with centuries vs India in all three formats in one year. — ICC",
     "scene": "cricket"},
    {"n": 9, "place": "ROME", "field": "STRIKE",
     "head": "Italy grinds to a halt",
     "dek": "CGIL general strike; rail stops 21:00 tonight to Saturday. — ANSA",
     "scene": "strike"},
    {"n": 10, "place": "TOKYO", "field": "ECONOMY",
     "head": "Japan core inflation quickens to 2.2%",
     "dek": "Above BoJ's 2% target a second month; Dec hike eyed. — Reuters",
     "scene": "yen"},
    {"n": 11, "place": "SENEGAL", "field": "MIGRATION",
     "head": "Migrant boat capsizes off Senegal",
     "dek": "Four bodies recovered, dozens missing off Yenne. — Reuters",
     "scene": "boat"},
    {"n": 12, "place": "SAN SALVADOR", "field": "POLITICS",
     "head": "Bukele files to run for a third term",
     "dek": "Registers for the 28 Feb 2027 vote; a 2025 amendment lets him run again. — Reuters",
     "scene": "ballot"},
    {"n": 13, "place": "BARCELONA", "field": "HEALTH",
     "head": "Pancreatic cancer pill shrinks tumours 60.7%",
     "dek": "Daraxonrasib + chemo in 61 patients; early trial. — Revolution Medicines",
     "scene": "pill"},
]

BRIEFS = [
    (14, "WASHINGTON", "Trump delays Iran call to 2027"),
    (15, "WASHINGTON", "Senate backs Iran strikes, 51–48"),
    (16, "CINCINNATI", "Fiona the hippo dies (swallowed a hat at the zoo)"),
    (17, "LONDON", "UK admits offensive cyber ops"),
    (18, "PARIS", "Fourth weekend of cost-of-living protests"),
    (19, "NEW DELHI", "Modi opens the SCO Civilisational Dialogue Forum"),
    (20, "BHOPAL", "MP scraps its two-child policy for local elections"),
    (21, "GAZA", "Four nations urge aid access to flooded areas"),
    (22, "F1", "Full-time race stewards from the 2027 season"),
    (23, "WASHINGTON", "US details Venezuela $12bn"),
    (24, "ODISHA", "Trains cancelled in the cyclone"),
    (25, "BHUBANESWAR", "Schools shut for the cyclone"),
    (26, "SHENZHEN", "Japan PM lonely at APEC"),
    (27, "SHENZHEN", "Albanese: Putin must end the war"),
    (28, "GOOGLE", "Android checks all installs"),
    (29, "ESA", "Hera maps the asteroid crash site"),
    (30, "APPLE", "iOS 27.3 beta adds Siri Health"),
    (31, "GAZA", "Two Palestinians killed in raids"),
    (32, "TEHRAN", "Iran war costs pass $48bn (US tally)"),
    (33, "CAIRO", "Egypt turns to Poland for wheat"),
    (34, "LONDON", "Patrick Stewart laid to rest"),
    (35, "EUROPE", "Youth walk out across 25+ nations"),
    (36, "SYDNEY", "Physicists beam a message through brick"),
]

REGIONS = [
    ("EUROPE", 9, (30, 80, 160)),
    ("AMERICAS", 7, (178, 34, 34)),
    ("ASIA-PACIFIC", 9, (34, 139, 80)),
    ("MIDEAST", 3, (146, 110, 30)),
    ("AFRICA", 2, (220, 120, 20)),
    ("OCEANIA", 2, (0, 130, 130)),
    ("WORLD", 4, (110, 110, 105)),
]

FIELDS = [
    ("War & security", 6, (120, 30, 30)),
    ("Politics & courts", 7, (40, 60, 140)),
    ("Economy & markets", 6, (20, 110, 40)),
    ("Culture & sport", 4, (150, 80, 160)),
    ("Climate & disasters", 4, (0, 130, 130)),
    ("Labour & society", 3, (180, 120, 20)),
    ("Science & tech", 3, (100, 60, 140)),
    ("Diplomacy", 3, (110, 110, 105)),
]

NUMBERS = [
    ("300,000", "evacuated as Akvan hits"),
    ("$97.17", "Anthropic's first close, +17%"),
    ("118", "Phillips' historic century"),
    ("−7%", "Asia shares' worst since 2020"),
    ("$120bn", "COP31 finance unresolved"),
    ("2.2%", "Japan core inflation, BoJ hike"),
]

TIMELINE = [
    ("01:25", "Kyiv missiles"),
    ("06:30", "Akvan landfall"),
    ("Morning", "Japan CPI 2.2%"),
    ("Midday", "Anthropic $97.17"),
    ("Afternoon", "COP31 deadlocked"),
    ("21:00", "Italy rail stops"),
    ("Midnight", "COP31 text due"),
]

DATECHECK = (
    "First reported Thursday 19 Nov, so NOT on this page as news: the Shenzhen "
    "trilateral · Anthropic's $83 IPO pricing · the ICJ Rohingya judgment · "
    "GTA VI's launch · the $190.4m Van Gogh sale · the Houthi strike on Riyadh's "
    "PIF Tower · Han Duck-soo's ruling · Pete Rose's pardon · Hayabusa2's "
    "asteroid-target change (JAXA, 17 Nov). Not yet: COP31's final deal."
)

SOURCES = (
    "Every story here happened, or was first reported, on Friday 20 November 2026. "
    "Disputed claims are attributed, not stated as fact. Sources: Reuters, AP, AFP, "
    "BBC, The Hindu, IMD, ICC, Kyiv Independent, Morningstar. Original drawings."
)

# pin positions (lon, lat) for stories 1-13 on the map
PINS = {
    1: (86, 20), 2: (30, 50), 3: (30, 37), 4: (4, 51), 5: (127, 37),
    6: (-74, 41), 7: (-122, 38), 8: (175, -41), 9: (12, 42), 10: (139, 35),
    11: (-17, 15), 12: (-89, 14), 13: (2, 41),
}

# simplified continent polygons in lon/lat, drawn cream on a dark map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 70), (-85, 66),
     (-80, 45), (-75, 35), (-80, 26), (-90, 21), (-97, 26), (-105, 20),
     (-110, 23), (-117, 33), (-125, 40), (-125, 49), (-135, 58), (-155, 58),
     (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-48, -28), (-58, -35), (-65, -45), (-70, -52), (-73, -40),
     (-72, -20), (-77, -12), (-80, -3)],
    # Europe
    [(-10, 37), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (30, 70), (20, 70),
     (12, 65), (5, 60), (5, 58), (-5, 58), (-10, 52), (-10, 43)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 11),
     (48, 0), (40, -10), (36, -18), (32, -28), (20, -35), (15, -27),
     (12, -18), (9, -1), (-8, 4), (-17, 15), (-16, 25)],
    # Asia
    [(30, 70), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 66), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52),
     (150, 59), (142, 50), (140, 40), (135, 35), (130, 32), (127, 35),
     (122, 30), (120, 25), (115, 22), (110, 20), (105, 10), (100, 8),
     (98, 12), (95, 16), (92, 21), (89, 22), (86, 20), (80, 15), (77, 8),
     (75, 20), (72, 20), (68, 23), (62, 25), (58, 26), (52, 28), (48, 30),
     (44, 29), (40, 32), (36, 36), (32, 36), (28, 38)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
]


# ---------------------------------------------------------------- scenes

def scene_cyclone(d, x, y, w, h):
    # v7: bigger, denser cyclone — storm bands fill the empty sky, the
    # spiral is thicker and wider, the eye is warmer, rain sweeps the
    # whole frame, and a shoreline with a surge wave anchors the bottom.
    d.rectangle([x, y, x + w, y + h], fill=(58, 105, 155))
    d.rectangle([x, y, x + w, y + 14], fill=(38, 70, 110))
    d.rectangle([x, y + 14, x + w, y + 20], fill=(48, 88, 132))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(90, 140, 90))
    d.rectangle([x, y + h - 26, x + w, y + h - 22], fill=(210, 190, 140))
    d.arc([x + 10, y + h - 34, x + 90, y + h - 12], start=180, end=360,
          fill=(255, 255, 255), width=3)
    cx, cy = x + w // 2 + 18, y + h // 2 - 8
    d.arc([cx - 78, cy - 58, cx + 78, cy + 58], start=150, end=430,
          fill=(200, 220, 240), width=3)
    for i, r in enumerate(range(14, 58, 8)):
        start = 180 + i * 25
        d.arc([cx - r, cy - r, cx + r, cy + r], start=start, end=start + 270,
              fill=(255, 255, 255), width=6)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 205, 80))
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14],
              outline=(255, 255, 255), width=2)
    for i in range(22):
        rx = x + 6 + (i * 29) % (w - 12)
        ry = y + 22 + (i * 19) % (h - 52)
        d.line([rx, ry, rx - 5, ry + 11], fill=(215, 232, 248), width=2)
    f = font(SANS_BOLD, 11)
    d.text((x + 8, y + h - 22), "90–100 KM/H", font=f, fill=(255, 255, 255))


def scene_kyiv(d, x, y, w, h):
    # v7: the three straight orange "trend lines" are gone — missiles now
    # fall on curved trails, with explosion bursts where they hit and a
    # damaged Dnipro bridge silhouette along the bottom.
    d.rectangle([x, y, x + w, y + h], fill=(12, 18, 38))
    for i in range(24):
        sx = x + (i * 37) % w
        sy = y + (i * 13) % (h // 2)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220))
    # skyline
    base = y + h - 18
    d.rectangle([x, base, x + w, y + h], fill=(8, 12, 26))
    for i, bh in enumerate([34, 52, 28, 62, 40, 55, 30, 48]):
        bx = x + 8 + i * 40
        d.rectangle([bx, base - bh, bx + 30, base], fill=(20, 28, 52))
        for wy in range(base - bh + 6, base - 4, 10):
            d.rectangle([bx + 5, wy, bx + 10, wy + 5], fill=(255, 200, 90))

    def curve(p0, p1, p2, n=24):
        pts = []
        for k in range(n + 1):
            t = k / n
            px = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            py = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
            pts.append((px, py))
        return pts

    # curved missile trails (warhead at the low end)
    pts1 = curve((x + 155, y + 2), (x + 120, y + 45), (x + 78, y + 78))
    d.line(pts1, fill=(255, 140, 40), width=3)
    d.ellipse([pts1[-1][0] - 4, pts1[-1][1] - 4, pts1[-1][0] + 4, pts1[-1][1] + 4],
              fill=(255, 220, 120))
    pts2 = curve((x + 240, y + 0), (x + 228, y + 40), (x + 200, y + 72))
    d.line(pts2, fill=(255, 140, 40), width=3)
    d.ellipse([pts2[-1][0] - 4, pts2[-1][1] - 4, pts2[-1][0] + 4, pts2[-1][1] + 4],
              fill=(255, 220, 120))
    # explosion bursts where the missiles hit
    for (bx, by) in [(x + 78, y + 80), (x + 200, y + 74)]:
        d.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(255, 120, 20))
        d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(255, 220, 120))
        for ang in range(0, 360, 45):
            ex = bx + int(16 * math.cos(math.radians(ang)))
            ey = by + int(16 * math.sin(math.radians(ang)))
            d.line([bx, by, ex, ey], fill=(255, 180, 60), width=2)
    # damaged bridge silhouette along the bottom (one span dropped)
    byy = y + h - 10
    for (sx0, sx1) in [(x, x + 168), (x + 198, x + w)]:
        d.line([sx0, byy, sx1, byy], fill=(140, 150, 170), width=2)
    for sx in (x + 60, x + 130, x + 250):
        d.line([sx, byy, sx, y + h], fill=(140, 150, 170), width=2)
    d.line([x + 168, byy, x + 198, y + h - 2], fill=(140, 150, 170), width=2)
    d.ellipse([x + 176, byy - 5, x + 190, byy + 5], fill=(255, 120, 20))
    f = font(SANS_BOLD, 11)
    d.text((x + 32, y + 10), "01:25 · 7 WAVES", font=f, fill=(255, 255, 255))


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 90, 70))
    # globe
    cx, cy, r = x + 70, y + h // 2, 42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 160, 200))
    d.ellipse([cx - r + 12, cy - r + 8, cx - r + 34, cy - r + 26], fill=(60, 140, 80))
    d.ellipse([cx + 2, cy + 6, cx + 28, cy + 30], fill=(60, 140, 80))
    d.arc([cx - r, cy - r, cx + r, cy + r], start=0, end=360, fill=(255, 255, 255), width=2)
    # thermometer
    tx = x + w - 60
    d.rounded_rectangle([tx, y + 18, tx + 16, y + h - 30], radius=8, fill=(255, 255, 255))
    d.ellipse([tx - 6, y + h - 44, tx + 22, y + h - 16], fill=(220, 40, 40))
    d.rectangle([tx + 5, y + 40, tx + 11, y + h - 30], fill=(220, 40, 40))
    f = font(SANS_BOLD, 12)
    d.text((x + w - 150, y + 10), "FINAL DAY", font=f, fill=(255, 255, 255))
    f2 = font(SANS_BOLD, 11)
    d.text((x + 122, y + h - 20), "$120BN FINANCE GAP", font=f2, fill=(255, 255, 255))


def scene_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 235, 245))
    # EU flag
    d.rectangle([x + 12, y + 8, x + 62, y + h - 8], fill=(0, 51, 153))
    for k in range(8):
        ang = k * math.pi / 4
        px = x + 37 + int(12 * math.cos(ang))
        py = y + h // 2 + int(12 * math.sin(ang))
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 220, 0))
    # UK flag
    d.rectangle([x + w - 62, y + 8, x + w - 12, y + h - 8], fill=(1, 33, 105))
    d.line([x + w - 62, y + 8, x + w - 12, y + h - 8], fill=(255, 255, 255), width=5)
    d.line([x + w - 12, y + 8, x + w - 62, y + h - 8], fill=(255, 255, 255), width=5)
    d.line([x + w - 37, y + 8, x + w - 37, y + h - 8], fill=(255, 255, 255), width=8)
    d.line([x + w - 62, y + h // 2, x + w - 12, y + h // 2], fill=(255, 255, 255), width=8)


def scene_chart_down(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 40))
    pts = [(x + 10, y + 8), (x + 40, y + 14), (x + 70, y + 11), (x + 100, y + 20),
           (x + 130, y + 18), (x + 160, y + 28), (x + 185, y + 30)]
    d.line(pts, fill=(255, 70, 70), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 70, 70))
    f = font(SANS_BOLD, 11)
    d.text((x + 10, y + h - 16), "NIKKEI −4.8% · KOSPI −5.7%", font=f, fill=(255, 120, 120))


def scene_gta(d, x, y, w, h):
    # v7: dusk skyline + controller, not just a sunset — the sun sets
    # behind a lit skyline and a game controller sits in the foreground.
    d.rectangle([x, y, x + w, y + 14], fill=(90, 45, 120))
    d.rectangle([x, y + 14, x + w, y + 26], fill=(200, 80, 110))
    d.rectangle([x, y + 26, x + w, y + h], fill=(255, 140, 70))
    d.ellipse([x + w - 88, y + 4, x + w - 60, y + 32], fill=(255, 225, 130))
    base = y + h - 12
    d.rectangle([x, base, x + w, y + h], fill=(35, 22, 55))
    for i, bh in enumerate([10, 18, 12, 22, 14, 20, 11, 16]):
        bx = x + 4 + i * 24
        d.rectangle([bx, base - bh, bx + 18, base], fill=(25, 15, 45))
        for wy in range(base - bh + 3, base - 2, 6):
            d.rectangle([bx + 3, wy, bx + 6, wy + 3], fill=(255, 200, 90))
    cx0, cy0 = x + w // 2 - 30, y + h - 20
    d.rounded_rectangle([cx0, cy0, cx0 + 60, cy0 + 16], radius=8,
                        fill=(20, 20, 30))
    d.ellipse([cx0 + 8, cy0 + 5, cx0 + 16, cy0 + 13], fill=(60, 60, 80))
    d.ellipse([cx0 + 44, cy0 + 5, cx0 + 52, cy0 + 13], fill=(60, 60, 80))
    for j, col in enumerate([(220, 60, 60), (60, 200, 80),
                             (60, 120, 220), (240, 200, 60)]):
        bx = cx0 + 24 + (j % 2) * 6
        by = cy0 + 3 + (j // 2) * 6
        d.ellipse([bx, by, bx + 4, by + 4], fill=col)
    f = font(SANS_BOLD, 11)
    d.text((x + 26, y + 4), "VICE CITY", font=f, fill=(255, 255, 255))
    f2 = font(SANS_BOLD, 11)
    d.text((x + 8, y + h - 14), "$1.80BN", font=f2, fill=(255, 220, 90))


def scene_chart_up(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 50, 30))
    pts = [(x + 10, y + 24), (x + 40, y + 20), (x + 70, y + 22), (x + 100, y + 14),
           (x + 130, y + 16), (x + 160, y + 8), (x + 185, y + 6)]
    d.line(pts, fill=(80, 220, 120), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(80, 220, 120))
    f = font(SANS_BOLD, 12)
    d.text((x + 10, y + h - 16), "$97.17 · +17%", font=f, fill=(140, 255, 170))


def scene_cricket(d, x, y, w, h):
    # v7: batsman + stumps + ball on a pitch, not a green field + dot.
    d.rectangle([x, y, x + w, y + h], fill=(60, 140, 60))
    d.rectangle([x, y + 30, x + w, y + h - 6], fill=(205, 180, 130))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(45, 110, 45))
    sx = x + w - 26
    for k in range(3):
        d.rectangle([sx + k * 5, y + 18, sx + k * 5 + 3, y + 34],
                    fill=(250, 240, 200))
    d.rectangle([sx, y + 16, sx + 13, y + 18], fill=(250, 240, 200))
    bx = x + w - 62
    d.ellipse([bx, y + 8, bx + 10, y + 18], fill=(255, 255, 255))
    d.rectangle([bx + 1, y + 18, bx + 9, y + 32], fill=(255, 255, 255))
    d.line([bx + 3, y + 32, bx + 1, y + 44], fill=(30, 30, 40), width=3)
    d.line([bx + 7, y + 32, bx + 9, y + 44], fill=(30, 30, 40), width=3)
    d.line([bx + 8, y + 22, bx + 20, y + 40], fill=(180, 140, 90), width=4)
    d.ellipse([x + 66, y + 12, x + 74, y + 20], fill=(200, 40, 40))
    f = font(SANS_BOLD, 13)
    d.text((x + 26, y + 4), "118", font=f, fill=(255, 255, 255))


def scene_strike(d, x, y, w, h):
    # v7: a halted train + a strike placard, not dots on sticks.
    d.rectangle([x, y, x + w, y + h], fill=(235, 228, 205))
    d.line([x + 6, y + 42, x + w - 6, y + 42], fill=(60, 60, 60), width=2)
    d.line([x + 6, y + 46, x + w - 6, y + 46], fill=(60, 60, 60), width=2)
    d.rounded_rectangle([x + 80, y + 14, x + w - 8, y + 40], radius=4,
                        fill=(150, 30, 30))
    d.rounded_rectangle([x + 80, y + 14, x + 104, y + 40], radius=4,
                        fill=(120, 20, 20))
    for wx in (x + 88, x + 112, x + 134, x + 156, x + 174):
        d.rectangle([wx, y + 19, wx + 14, y + 28], fill=(255, 255, 255))
    for wx in (x + 92, x + 114, x + 136, x + 158, x + 180):
        d.ellipse([wx, y + 40, wx + 8, y + 48], fill=(30, 30, 30))
    d.line([x + 50, y + 30, x + 50, y + 48], fill=(90, 60, 30), width=3)
    d.rectangle([x + 24, y + 6, x + 76, y + 30], fill=(255, 255, 255),
                outline=(200, 30, 30), width=2)
    f = font(SANS_BOLD, 8)
    d.text((x + 28, y + 14), "SCIOPERO", font=f, fill=(200, 30, 30))


def scene_yen(d, x, y, w, h):
    # v7: price tags + a shopping basket, not a bare number.
    d.rectangle([x, y, x + w, y + h], fill=(235, 240, 245))
    for (tx, ty, label) in [(x + 26, y + 4, "¥198"), (x + 26, y + 20, "¥350")]:
        d.rectangle([tx, ty, tx + 52, ty + 13], fill=(255, 255, 255),
                    outline=(180, 40, 40), width=1)
        d.ellipse([tx + 4, ty + 5, tx + 8, ty + 9], fill=(180, 40, 40))
        f = font(SANS_BOLD, 9)
        d.text((tx + 12, ty + 2), label, font=f, fill=(180, 40, 40))
    bx0, by0 = x + w - 72, y + 16
    d.arc([bx0 + 8, by0 - 8, bx0 + 56, by0 + 12], start=180, end=360,
          fill=(120, 80, 40), width=3)
    d.rectangle([bx0 + 12, by0 - 2, bx0 + 22, by0 + 10], fill=(60, 140, 60))
    d.ellipse([bx0 + 30, by0 - 4, bx0 + 44, by0 + 10], fill=(230, 120, 30))
    d.rectangle([bx0 + 46, by0, bx0 + 56, by0 + 10], fill=(200, 180, 90))
    d.polygon([(bx0, by0 + 10), (bx0 + 64, by0 + 10), (bx0 + 58, by0 + 30),
               (bx0 + 6, by0 + 30)], fill=(150, 100, 50))
    d.line([bx0 + 6, by0 + 18, bx0 + 58, by0 + 18], fill=(120, 80, 40), width=2)
    f2 = font(SANS_BOLD, 12)
    d.text((x + 8, y + h - 16), "2.2%", font=f2, fill=(200, 40, 40))


def scene_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 130, 180))
    for i in range(4):
        wy = y + 14 + i * 12
        d.arc([x + 10, wy, x + w - 10, wy + 10], start=0, end=180,
              fill=(255, 255, 255), width=2)
    d.polygon([(x + 60, y + h - 22), (x + 140, y + h - 22), (x + 130, y + h - 8),
               (x + 70, y + h - 8)], fill=(140, 90, 40))
    d.line([x + 100, y + h - 22, x + 100, y + 14], fill=(60, 40, 20), width=3)
    d.polygon([(x + 100, y + 14), (x + 130, y + 28), (x + 100, y + 28)],
              fill=(255, 255, 255))


def scene_ballot(d, x, y, w, h):
    # v7: a ballot box with a paper going into the slot, not a grey bar.
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 110))
    bx0, by0 = x + 42, y + 16
    d.rectangle([bx0, by0, bx0 + 96, y + h - 4], fill=(225, 225, 225))
    d.rectangle([bx0, by0, bx0 + 96, by0 + 6], fill=(200, 200, 200))
    d.rectangle([bx0 + 28, by0 + 1, bx0 + 68, by0 + 5], fill=(40, 40, 40))
    d.polygon([(bx0 + 34, by0 + 2), (bx0 + 50, by0 + 2), (bx0 + 56, y + 2),
               (bx0 + 40, y + 2)], fill=(255, 255, 255))
    d.line([bx0 + 42, y + 8, bx0 + 46, y + 12], fill=(200, 30, 30), width=2)
    d.line([bx0 + 46, y + 12, bx0 + 54, y + 4], fill=(200, 30, 30), width=2)
    f = font(SANS_BOLD, 11)
    t = "VOTE"
    tw = d.textlength(t, font=f)
    d.text((bx0 + (96 - tw) / 2, by0 + 16), t, font=f, fill=(30, 60, 110))
    f2 = font(SANS_BOLD, 9)
    d.text((x + w - 72, y + 4), "28 FEB 2027", font=f2, fill=(255, 255, 255))


def scene_pill(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 245, 240))
    d.rounded_rectangle([x + 20, y + 6, x + 90, y + 26], radius=10,
                        fill=(255, 255, 255), outline=(200, 40, 40), width=2)
    d.rounded_rectangle([x + 90, y + 6, x + 160, y + 26], radius=10,
                        fill=(200, 40, 40))
    f = font(SANS_BOLD, 12)
    d.text((x + 14, y + h - 18), "60.7% RESPONSE", font=f, fill=(200, 40, 40))


SCENES = {
    "cyclone": scene_cyclone, "kyiv": scene_kyiv, "cop31": scene_cop31,
    "flags": scene_flags, "chart_down": scene_chart_down, "gta": scene_gta,
    "chart_up": scene_chart_up, "cricket": scene_cricket,
    "strike": scene_strike, "yen": scene_yen, "boat": scene_boat,
    "ballot": scene_ballot, "pill": scene_pill,
}


# ---------------------------------------------------------------- how sure

# v7: every lead/medium card carries a status dot in its kicker row
# (right end), explained by the legend under the map. CONFIRMED = it
# happened / is on the record. CLAIM = attributed, not yet verified
# (#13 pill: early trial, no control group, company-reported).
# FORECAST = scheduled / expected (#9 Italy: rail stops 21:00 tonight).
HOW_SURE = {
    1: "CONFIRMED", 2: "CONFIRMED", 3: "CONFIRMED", 4: "CONFIRMED",
    5: "CONFIRMED", 6: "CONFIRMED", 7: "CONFIRMED", 8: "CONFIRMED",
    9: "FORECAST", 10: "CONFIRMED", 11: "CONFIRMED", 12: "CONFIRMED",
    13: "CLAIM",
}
HOW_SURE_COL = {
    "CONFIRMED": (34, 139, 80),
    "CLAIM": (200, 130, 0),
    "FORECAST": (30, 80, 160),
}


def sure_dot(d, cx, cy, status, r=5):
    """HOW SURE marker: coloured dot, centre (cx, cy), in the kicker row."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=HOW_SURE_COL[status], outline=INK, width=1)


# ---------------------------------------------------------------- page

def draw_map(d, x, y, w, h):
    """Solid dark map with cream continents and red numbered pins."""
    d.rectangle([x, y, x + w, y + h], fill=DARKBLUE)
    lon0, lon1, lat0, lat1 = -170, 190, 85, -60

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(232, 222, 190), outline=(200, 190, 160))
    # pins (manual nudge for the European cluster so numbers stay readable)
    pin_nudge = {2: (0, -7), 3: (2, 9), 4: (-9, -5), 9: (9, 3), 13: (-11, 7)}
    for n, (lon, lat) in PINS.items():
        px, py = proj(lon, lat)
        dx, dy = pin_nudge.get(n, (0, 0))
        px += dx
        py += dy
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = font(SANS_BOLD, 9)
        t = str(n)
        tw = d.textlength(t, font=f)
        d.text((px - tw / 2, py - 6), t, font=f, fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 12  # outer margin
    CW = W - 2 * M  # 1000

    # ---- masthead
    f_mast = font(SANS_BOLD, 13)
    d.text((M, 6), "THE WORLD IN ONE DAY", font=f_mast, fill=RED)
    r = "FRIDAY'S NEWS · ONE PAGE · 36 STORIES"
    d.text((W - M - d.textlength(r, font=f_mast), 6), r, font=f_mast, fill=INK)
    d.line([M, 28, W - M, 28], fill=RED, width=2)

    # ---- title + subhead
    f_title = font(SERIF, 50)
    d.text((M, 32), "Friday 20 November 2026", font=f_title, fill=NAVY)
    f_sub = font(LIB_SERIF_IT, 15)
    d.text((M, 88),
           "A cyclone comes ashore in Odisha · Missiles rain on Kyiv · Climate talks reach their final day",
           font=f_sub, fill=DARKRED)

    # ---- region bar (label shrinks until it fits its segment; small
    # counts get narrow segments, so AFRICA/OCEANIA drop a size or two)
    y = 112
    total = sum(n for _, n, _ in REGIONS)
    bx = M
    for name, n, col in REGIONS:
        seg_w = CW * n / total
        d.rectangle([bx, y, bx + seg_w - 1, y + 19], fill=col)
        label = f"{name} {n}"
        f_reg = font(SANS_BOLD, 11)
        for sz in (11, 10, 9, 8):
            f_try = font(SANS_BOLD, sz)
            if d.textlength(label, font=f_try) <= seg_w - 4:
                f_reg = f_try
                break
        tw = d.textlength(label, font=f_reg)
        ty = y + max(3, (19 - f_reg.size) // 2)
        d.text((bx + (seg_w - tw) / 2, ty), label, font=f_reg, fill=(255, 255, 255))
        bx += seg_w

    # ---- by-field bar (label shrinks until it fits its segment; never
    # omitted — a missing label is worse than a smaller one)
    y = 133
    bx = M
    for name, n, col in FIELDS:
        seg_w = CW * n / total
        d.rectangle([bx, y, bx + seg_w - 1, y + 16], fill=col)
        label = f"{name} {n}"
        f_field = font(SANS_BOLD, 9)
        for sz in (9, 8, 7, 6):
            f_try = font(SANS_BOLD, sz)
            if d.textlength(label, font=f_try) <= seg_w - 4:
                f_field = f_try
                break
        tw = d.textlength(label, font=f_field)
        ty = y + max(2, (16 - f_field.size) // 2)
        d.text((bx + (seg_w - tw) / 2, ty), label, font=f_field,
               fill=(255, 255, 255))
        bx += seg_w

    # ---- by the numbers
    y = 153
    f_lab = font(SANS_BOLD, 10)
    d.text((M, y + 8), "BY THE", font=f_lab, fill=RED)
    d.text((M, y + 20), "NUMBERS", font=f_lab, fill=RED)
    col_w = (CW - 90) / 6
    f_num = font(SANS_BOLD, 21)
    f_cap = font(SANS, 9)
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + 90 + i * col_w
        d.text((cx, y), num, font=f_num, fill=RED)
        draw_wrapped(d, cx, y + 26, cap, f_cap, INK, col_w - 8, line_h=11,
                     max_lines=2)

    # ---- timeline strip
    y = 196
    d.rectangle([M, y, W - M, y + 20], fill=(232, 226, 208))
    f_tl = font(SANS_BOLD, 10)
    d.text((M + 6, y + 4), "THE DAY", font=f_tl, fill=RED)
    tx = M + 78
    f_tlb = font(SANS, 9)
    for i, (t, what) in enumerate(TIMELINE):
        seg = f"{t}  {what}"
        if i < len(TIMELINE) - 1:
            seg += "   ·   "
        d.text((tx, y + 4), seg, font=f_tlb, fill=INK)
        tx += d.textlength(seg, font=f_tlb)

    # ---- leads (3 columns)
    y = 222
    lead_h = 170
    lead_w = (CW - 12) / 3
    for i, lead in enumerate(LEADS):
        lx = M + i * (lead_w + 6)
        scene_h = 102
        SCENES[lead["scene"]](d, lx, y, lead_w, scene_h)
        num_badge(d, lx + 6, y + 6, lead["n"])
        ty = y + scene_h + 4
        f_kick = font(SANS_BOLD, 10)
        d.text((lx, ty), f"{lead['place']} · {lead['field']}", font=f_kick, fill=RED)
        sure_dot(d, lx + lead_w - 6, ty + 5, HOW_SURE[lead["n"]])
        ty += 14
        f_head = font(SERIF, 17)
        ty = draw_wrapped(d, lx, ty, lead["head"], f_head, INK, lead_w,
                          line_h=19, max_lines=2)
        f_dek = font(SANS, 10)
        draw_wrapped(d, lx, ty + 2, lead["dek"], f_dek, INK, lead_w,
                     line_h=12, max_lines=2)
        d.line([lx, y, lx, y + lead_h], fill=LIGHTGREY, width=1)

    # ---- mediums (2 rows x 5)
    y = 222 + lead_h + 8
    med_w = (CW - 16) / 5
    med_h = 110
    for row in range(2):
        for col in range(5):
            m = MEDIUMS[row * 5 + col]
            mx = M + col * (med_w + 4)
            my = y + row * (med_h + 6)
            scene_h = 50
            SCENES[m["scene"]](d, mx, my, med_w, scene_h)
            num_badge(d, mx + 4, my + 4, m["n"], r=9)
            ty = my + scene_h + 3
            f_kick = font(SANS_BOLD, 8)
            d.text((mx, ty), f"{m['place']} · {m['field']}", font=f_kick, fill=RED)
            sure_dot(d, mx + med_w - 6, ty + 5, HOW_SURE[m["n"]])
            ty += 11
            f_head = font(SANS_BOLD, 11)
            ty = draw_wrapped(d, mx, ty, m["head"], f_head, INK, med_w,
                              line_h=13, max_lines=2)
            f_dek = font(SANS, 9)
            draw_wrapped(d, mx, ty + 1, m["dek"], f_dek, INK, med_w,
                         line_h=11, max_lines=2)

    # ---- map + briefs
    y = 222 + lead_h + 8 + 2 * med_h + 6 + 8
    map_w = 330
    map_h = 210  # v7: 25px shorter to fit the HOW SURE legend below
    f_sec = font(SANS_BOLD, 13)
    d.text((M, y), "WHERE IT HAPPENED", font=f_sec, fill=RED)
    draw_map(d, M, y + 20, map_w, map_h)
    f_leg = font(SANS, 9)
    d.text((M, y + 20 + map_h + 4),
           "Red numbers mark stories 1–13. Positions are approximate.",
           font=f_leg, fill=GREY)
    # HOW SURE legend (v7): two lines under the map caption; the dots
    # match the status dot in each lead/medium kicker row.
    ly = y + 20 + map_h + 16
    f_how = font(SANS_BOLD, 9)
    d.text((M, ly), "HOW SURE", font=f_how, fill=RED)
    hx = M + d.textlength("HOW SURE ", font=f_how)
    d.ellipse([hx, ly + 1, hx + 8, ly + 9], fill=HOW_SURE_COL["CONFIRMED"],
              outline=INK, width=1)
    d.text((hx + 12, ly), "CONFIRMED — on the record", font=f_leg, fill=INK)
    ly += 12
    hx = M
    d.ellipse([hx, ly + 1, hx + 8, ly + 9], fill=HOW_SURE_COL["CLAIM"],
              outline=INK, width=1)
    d.text((hx + 12, ly), "CLAIM — attributed", font=f_leg, fill=INK)
    hx += 12 + d.textlength("CLAIM — attributed ", font=f_leg)
    d.ellipse([hx, ly + 1, hx + 8, ly + 9], fill=HOW_SURE_COL["FORECAST"],
              outline=INK, width=1)
    d.text((hx + 12, ly), "FORECAST — scheduled", font=f_leg, fill=INK)

    bx = M + map_w + 14
    bw = W - M - bx
    d.text((bx, y), "ALSO ON FRIDAY 20 NOVEMBER — 23 MORE STORIES",
           font=f_sec, fill=RED)
    col_w = (bw - 12) / 2
    f_bnum = font(SANS_BOLD, 10)
    f_bplace = font(SANS_BOLD, 10)
    f_btext = font(SANS, 10)
    row_h = 21
    for i, (n, place, text) in enumerate(BRIEFS):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        x = bx + col * (col_w + 12)
        yy = y + 22 + row * row_h
        d.text((x, yy), str(n), font=f_bnum, fill=RED)
        px = x + 22
        d.text((px, yy), place + " —", font=f_bplace, fill=INK)
        tx = px + d.textlength(place + " — ", font=f_bplace)
        # wrap the brief text to the remaining width, at most 2 lines
        lines = wrap_text(d, text, f_btext, col_w - (tx - x))
        d.text((tx, yy), lines[0] if lines else "", font=f_btext, fill=INK)
        if len(lines) > 1:
            d.text((px, yy + 12), lines[1], font=f_btext, fill=INK)

    # ---- date check
    y = 905
    d.rectangle([M, y, W - M, y + 55], outline=RED, width=2)
    f_dc = font(SANS_BOLD, 11)
    d.text((M + 8, y + 6), "DATE CHECK", font=f_dc, fill=RED)
    f_dct = font(SANS, 10)
    draw_wrapped(d, M + 96, y + 6, DATECHECK, f_dct, INK, W - M - 96 - 8,
                 line_h=13, max_lines=4)

    # ---- footer
    f_foot = font(SANS, 8)
    draw_wrapped(d, M, 968, SOURCES, f_foot, GREY, CW, line_h=10, max_lines=2)

    img.save("entry.png")
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
