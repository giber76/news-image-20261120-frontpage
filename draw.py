#!/usr/bin/env python3
"""Friday 20 November 2026 — one-page broadsheet (news-image-20261120).

Draws the whole 1024x1024 front page with Pillow: masthead, by-the-numbers
strip, region bar, 3 illustrated leads, 12 illustrated medium cards, a
dotted world map with numbered pins, briefs 16-69, a DATE CHECK box and a
footer. Every illustration is a flat procedural drawing made here (no
photos, no copied art). Deterministic: two runs produce identical bytes.

Run:  python3 draw.py   ->   writes entry.png next to this file.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

# ---------- palette ----------
PAPER = "#f8f3e6"
CARD = "#fffdf6"
INK = "#16233f"
NAVY = "#1f3a5f"
RED = "#b01e24"
DARKRED = "#8f171c"
GRAY = "#5c5c5c"
LIGHTGRAY = "#8a8a8a"
LINE = "#c9c2ae"
SKY = "#cfe3f2"
SEA = "#bcd8ec"
SAND = "#e8dcc0"

REGION_COLORS = {
    "Europe": "#2b5ea7",
    "Americas": "#c0392b",
    "Asia-Pacific": "#2e7d32",
    "Mideast": "#8a6d1b",
    "Africa": "#d35400",
    "Oceania": "#7d3c98",
    "World": "#666666",
}
REGION_COUNTS = [
    ("EUROPE", "Europe", 10),
    ("THE AMERICAS", "Americas", 13),
    ("ASIA-PACIFIC", "Asia-Pacific", 19),
    ("MIDEAST", "Mideast", 10),
    ("AFRICA", "Africa", 4),
    ("OCEANIA", "Oceania", 3),
    ("WORLD", "World", 10),
]

# ---------- fonts ----------
F = "/usr/share/fonts/truetype/liberation/"
def font(name, size):
    return ImageFont.truetype(F + name, size)

SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)
SANS_I = lambda s: font("LiberationSans-Italic.ttf", s)

# ---------- text helpers ----------
def wrap(draw, text, fnt, width):
    """Word-wrap `text` to fit `width` px; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_lines(draw, x, y, lines, fnt, fill, leading=None, align="left", x2=None):
    """Draw lines starting at (x, y); returns y just below the last line."""
    if leading is None:
        leading = fnt.size + 3
    for ln in lines:
        if align == "center":
            draw.text((x, y), ln, font=fnt, fill=fill, anchor="ma")
        elif align == "right":
            draw.text((x2, y), ln, font=fnt, fill=fill, anchor="ra")
        else:
            draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y

def badge(draw, cx, cy, r, num, fnt):
    """Red circle with a white number (story number)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=DARKRED, width=1)
    draw.text((cx, cy), str(num), font=fnt, fill="white", anchor="mm")

def card(draw, x, y, w, h, fill=CARD):
    draw.rectangle([x, y, x + w, y + h], fill=fill, outline=LINE, width=1)

# ---------- story data ----------
LEADS = [
    dict(n=1, tag="ODISHA · STORM", region="Asia-Pacific",
         headline="Cyclone Akvan slams into Odisha",
         body="Landfall near Gopalpur at noon; 300,000 evacuated, 423 teams out. — IMD",
         scene="cyclone"),
    dict(n=2, tag="BRUSSELS · DIPLOMACY", region="Europe",
         headline="EU meets Britain at second EU summit",
         body="Costa and von der Leyen host PM Burnham; a joint declaration is due. — EU Council",
         scene="summit"),
    dict(n=3, tag="EUROPE · PROTEST", region="World",
         headline="Youth walk out across 25 nations",
         body="Mass walkouts demand action on schools, conscription, climate, Gaza. — Reuters",
         scene="crowd"),
]

MEDIUMS = [
    dict(n=4, tag="ANTALYA · CLIMATE", region="Asia-Pacific",
         headline="COP31 reaches its final day",
         body="Fossil phase-out and a $120bn fund still open. — AFP",
         scene="cop"),
    dict(n=5, tag="NEW YORK · GAMES", region="Americas",
         headline="GTA 6 sales pass $1.80bn",
         body="Already past The Odyssey's run. — Mezha",
         scene="vicecity"),
    dict(n=6, tag="NEW DELHI · LAW", region="Asia-Pacific",
         headline="Justice Varma resigns",
         body="Resignation is not admission of guilt. — NDTV",
         scene="court"),
    dict(n=7, tag="ABU DHABI · DIPLOMACY", region="Mideast",
         headline="UAE denounces Somalia expulsion",
         body="UAE envoy expelled; Abu Dhabi calls it irresponsible.",
         scene="document"),
    dict(n=8, tag="ROME · STRIKE", region="Europe",
         headline="Italy grinds to a halt",
         body="CGIL strike; rail stops 21:00 tonight to Saturday. — ANSA",
         scene="train"),
    dict(n=9, tag="TOKYO · SPACE", region="Asia-Pacific",
         headline="Hayabusa2 gives up on landing",
         body="Engine trouble ends the asteroid plan. — Space",
         scene="space"),
    dict(n=10, tag="VIENNA · NUCLEAR", region="Europe",
         headline="West presses Iran at the IAEA",
         body="Inspectors must return to bombed sites. — Reuters",
         scene="atom"),
    dict(n=11, tag="CAIRO · ARCHAEOLOGY", region="Africa",
         headline="Ancient necropolis uncovered",
         body="Gold and terracotta at Tell Kom Abu Billo. — Arab News",
         scene="pyramid"),
    dict(n=12, tag="SYDNEY · CRICKET", region="Oceania",
         headline="Cummins in the sandpaper storm",
         body="Captaincy under scrutiny after Bancroft's ball-tampering claims.",
         scene="cricket"),
    dict(n=13, tag="SAN FRANCISCO · MARKETS", region="Americas",
         headline="Anthropic soars after debut",
         body="Shares jump; valued near $1.5tn. — The Hindu",
         scene="chart"),
    dict(n=14, tag="BEIRUT · STRIKE", region="Mideast",
         headline="Israel hits Hezbollah site",
         body="A weapons site in east Lebanon is struck. — Arab News",
         scene="blast"),
    dict(n=15, tag="DAMASCUS · DIPLOMACY", region="World",
         headline="Syria hails UN resolution",
         body="Damascus calls the post-war progress text historic. — SANA",
         scene="globe"),
]

# (number, city, headline) — concise headlines, all verified 20 Nov stories.
BRIEFS = [
    (16, "ODISHA", "Trains cancelled in cyclone"),
    (17, "BHUBANESWAR", "Schools shut for cyclone"),
    (18, "BANSWARA", "Local poll results pour in"),
    (19, "PUNJAB", "Ex-MLA Kamboj joins BJP"),
    (20, "NEW DELHI", "ADG reviews poll security"),
    (21, "BENGALURU", "BJP opposes scrapping laws"),
    (22, "WASHINGTON", "Trump delays Iran call"),
    (23, "WASHINGTON", "Pick denies Jan 6 attack"),
    (24, "WASHINGTON", "State AGs: 2026 results"),
    (25, "WASHINGTON", "Jeffries nears House first"),
    (26, "WASHINGTON", "Senate backs Iran strikes"),
    (27, "NEW YORK", "Carriage ban ruled out"),
    (28, "CINCINNATI", "Fiona the hippo dies"),
    (29, "BRUSSELS", "Culture ministers meet"),
    (30, "SHENZHEN", "Japan PM lonely at APEC"),
    (31, "SHENZHEN", "Albanese: Putin must end war"),
    (32, "WELLINGTON", "Nicholls nears 150"),
    (33, "DHAKA", "South Africa win first Test"),
    (34, "JOHANNESBURG", "Bavuma ruled out"),
    (35, "GENEVA", "Carlsen forfeit stirs row"),
    (36, "HONG KONG", "Rakshitha stuns Chen Yu Fei"),
    (37, "HONG KONG", "Satwik-Chirag reach QFs"),
    (38, "BHOPAL", "Women's hockey trophy begins"),
    (39, "MUMBAI", "ENE Repeat opens in cinemas"),
    (40, "GOOGLE", "Android checks all installs"),
    (41, "ESA", "Hera maps asteroid crash site"),
    (42, "APPLE", "iOS 27.3 beta adds Siri Health"),
    (43, "META", "Instagram shields creators"),
    (44, "SYDNEY", "Physicists beam through brick"),
    (45, "VICE CITY", "GTA 6: parrot finds stash"),
    (46, "LEONIDA", "GTA VI parodies culture wars"),
    (47, "MARKETS", "AMD slides on China links"),
    (48, "MARKETS", "Gold tests yearly lows"),
    (49, "GAZA", "Two Palestinians killed in raids"),
    (50, "TEHRAN", "Iran war costs pass $48bn"),
    (51, "CAIRO", "Egypt turns to Poland for wheat"),
    (52, "SANAA", "Yemeni army claims 715 ops"),
    (53, "MUSCAT", "Oman marks National Day"),
    (54, "MARRAKECH", "Film festival opens"),
    (55, "ABU DHABI", "Frieze art fair opens"),
    (56, "DAMMAM", "Air Arabia flies to Damascus"),
    (57, "LONDON", "Patrick Stewart laid to rest"),
    (58, "HOLLYWOOD", "Bruno Mars's father dies"),
    (59, "HOLLYWOOD", "Nick Jonas joins rom-com"),
    (60, "HOLLYWOOD", "Larry Poindexter dies"),
    (61, "LONDON", "Rob Brydon's fake agent tale"),
    (62, "CARDIFF", "Welsh Luke Skywalker voiced"),
    (63, "LONDON", "UK admits cyber ops"),
    (64, "PARIS", "Fourth weekend of cost protests"),
    (65, "NEW DELHI", "Modi opens SCO forum"),
    (66, "BHOPAL", "MP scraps two-child policy"),
    (67, "GAZA", "Four nations urge aid access"),
    (68, "F1", "Full-time stewards from 2027"),
    (69, "WASHINGTON", "US details Venezuela $12bn"),
]

NUMBERS = [
    ("300,000", "evacuated as Akvan hits Odisha"),
    ("$1.80bn", "GTA 6 sales top The Odyssey"),
    ("$1.5tn", "Anthropic's reported value"),
    ("25+", "nations in youth walkouts"),
    ("$48bn", "cost of the Iran war, US tally"),
    ("423", "rescue teams in Odisha"),
]

DATE_CHECK_ITEMS = (
    "the Shenzhen trilateral — Trump, Xi and Putin's joint peace declaration (Thu 19 Nov) · "
    "GTA VI's launch day (Thu 19 Nov) · Anthropic's first trades at $83 (Thu 19 Nov) · "
    "the ICJ Rohingya judgment — Myanmar committed genocide (Thu 19 Nov) · "
    "the Houthi strike on Riyadh's PIF Tower (Thu 19 Nov) · "
    "Han Duck-soo's Supreme Court ruling (Thu 19 Nov)"
)

# Map pins: (story number, lon, lat) — lon/lat of the place named.
PINS = [
    (1, 85.0, 20.0), (2, 4.4, 50.8), (3, -0.1, 51.5), (4, 30.7, 36.9),
    (5, -74.0, 40.7), (6, 77.2, 28.6), (7, 54.4, 24.5), (8, 12.5, 41.9),
    (9, 139.7, 35.7), (10, 16.4, 48.2), (11, 31.2, 30.0), (12, 151.2, -33.9),
    (13, -122.4, 37.8), (14, 35.5, 33.9), (15, 36.3, 33.5),
]
PIN_REGION = {1: "Asia-Pacific", 2: "Europe", 3: "World", 4: "Asia-Pacific",
              5: "Americas", 6: "Asia-Pacific", 7: "Mideast", 8: "Europe",
              9: "Asia-Pacific", 10: "Europe", 11: "Africa", 12: "Oceania",
              13: "Americas", 14: "Mideast", 15: "Mideast"}

# Coarse landmass boxes (lon_min, lon_max, lat_min, lat_max) for the dot map.
LAND = [
    (-168, -55, 50, 72), (-125, -66, 25, 49), (-118, -77, 8, 32),
    (-58, -20, 60, 84), (-80, -35, -55, 12), (-10, 40, 36, 70),
    (-18, 52, -35, 35), (35, 63, 12, 42), (40, 180, 42, 77),
    (60, 140, 5, 42), (95, 141, -10, 10), (113, 154, -40, -10),
    (129, 146, 30, 46), (-5, 2, 50, 59), (95, 141, -11, 6),
    (166, 179, -47, -34),
]

# ---------- scene illustrations (all flat procedural drawings) ----------
def person(d, cx, base, h, color, head_r=5):
    """Simple head-and-shoulders silhouette."""
    d.ellipse([cx - head_r, base - h, cx + head_r, base - h + 2 * head_r], fill=color)
    d.pieslice([cx - h * 0.42, base - h * 0.45, cx + h * 0.42, base + 2], 180, 360, fill=color)

def scene_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#9fc3e0")
    # spiral: concentric arcs, widening gaps
    cx, cy = x + w * 0.52, y + h * 0.52
    for i, r in enumerate(range(8, int(min(w, h) * 0.52), 9)):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=200 + i * 55, end=200 + i * 55 + 250,
              fill="#ffffff" if i % 2 == 0 else "#e8f2fa", width=4)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill="#ffd94d", outline="#d9a400", width=2)
    # rain: diagonal streaks, denser at the edges
    for i in range(26):
        rx = x + 6 + (i * 37) % (w - 12)
        ry = y + 4 + (i * 53) % (h - 18)
        d.line([rx, ry, rx - 5, ry + 12], fill="#5b87ad", width=2)
    # wind label, top-right — well clear of the number badge at top-left
    label = "90–100 KM/H"
    fnt = SANS_B(13)
    tw = d.textlength(label, font=fnt)
    lx = x + w - tw - 10
    d.rectangle([lx - 6, y + 6, lx + tw + 6, y + 24], fill="#12365e")
    d.text((lx, y + 8), label, font=fnt, fill="white")

def scene_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # EU flag (left) and UK flag (right)
    fx, fy, fw, fh = x + 14, y + 10, 52, 32
    d.rectangle([fx, fy, fx + fw, fy + fh], fill="#1e3a8a")
    for k in range(12):
        a = 2 * math.pi * k / 12
        sx, sy = fx + fw / 2 + 15 * math.cos(a), fy + fh / 2 + 10 * math.sin(a)
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill="#ffd94d")
    ux, uy, uw, uh = x + w - 66, y + 10, 52, 32
    d.rectangle([ux, uy, ux + uw, uy + uh], fill="#1e3a8a")
    d.rectangle([ux, uy + uh / 2 - 4, ux + uw, uy + uh / 2 + 4], fill="white")
    d.rectangle([ux + uw / 2 - 4, uy, ux + uw / 2 + 4, uy + uh], fill="white")
    d.rectangle([ux, uy + uh / 2 - 2, ux + uw, uy + uh / 2 + 2], fill=RED)
    d.rectangle([ux + uw / 2 - 2, uy, ux + uw / 2 + 2, uy + uh], fill=RED)
    # banner (kept high so it stays clear of the seated silhouettes)
    bf = SANS_B(12)
    banner = "2ND EU–UK SUMMIT"
    tw = d.textlength(banner, font=bf)
    d.rectangle([x + w / 2 - tw / 2 - 8, y + 32, x + w / 2 + tw / 2 + 8, y + 52], fill="white", outline=NAVY)
    d.text((x + w / 2 - tw / 2, y + 36), banner, font=bf, fill=NAVY)
    # table + three seated silhouettes
    d.rectangle([x + 30, y + h - 26, x + w - 30, y + h - 10], fill="#7a5230")
    for sx in (x + w * 0.30, x + w * 0.50, x + w * 0.70):
        person(d, sx, y + h - 26, 34, "#2c2c34", head_r=7)
    d.rectangle([x + w * 0.30 - 2, y + h - 40, x + w * 0.30 + 2, y + h - 26], fill="#2c2c34")

def scene_crowd(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#e9d9a8")
    # building backs
    for bx, bw, bh, bc in ((0, 60, 46, "#b9a06a"), (64, 46, 62, "#a68f5c"),
                           (150, 70, 40, "#c4b183"), (226, 52, 56, "#b09a63"),
                           (282, 48, 44, "#c4b183")):
        d.rectangle([x + bx, y + h - bh - 30, x + bx + bw, y + h - 30], fill=bc)
        for wx in range(bx + 8, bx + bw - 6, 14):
            d.rectangle([x + wx, y + h - bh - 20, x + wx + 7, y + h - bh - 10], fill="#f4e9c8")
    # placards on sticks
    signs = [("EDU", x + 52, "#c0392b"), ("CLIMATE", x + 150, "#2e7d32"), ("NO WAR", x + 252, "#2b5ea7")]
    for label, sx, sc in signs:
        d.line([sx, y + 22, sx, y + 62], fill="#5c4a2a", width=2)
        fnt = SANS_B(11)
        tw = d.textlength(label, font=fnt)
        d.rectangle([sx - tw / 2 - 5, y + 8, sx + tw / 2 + 5, y + 24], fill="white", outline=sc, width=2)
        d.text((sx - tw / 2, y + 10), label, font=fnt, fill=sc)
    # crowd: rows of heads/shoulders in varied colours
    cols = ["#7d3c98", "#c0392b", "#2e7d32", "#2b5ea7", "#d35400", "#8a6d1b"]
    for row, base in enumerate((y + h - 6, y + h - 22)):
        for i in range(11):
            cx = x + 12 + i * 29 + (row * 14)
            person(d, cx, base, 26 if row == 0 else 22, cols[(i + row * 3) % len(cols)], head_r=6)

def scene_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#bfe0c8")
    d.ellipse([x + w - 34, y + 6, x + w - 6, y + 34], fill="#ffd94d")
    d.ellipse([x + 14, y + 12, x + 62, y + h - 8], fill="#2e7d32")
    d.ellipse([x + 24, y + 18, x + 44, y + 32], fill="#7fbf8f")
    d.ellipse([x + 34, y + 34, x + 56, y + 46], fill="#7fbf8f")
    d.arc([x + 8, y + 6, x + 68, y + h - 2], 200, 340, fill="white", width=2)

def scene_vicecity(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#141a33")
    for i in range(24):
        sx = x + 4 + (i * 53) % (w - 8)
        sy = y + 3 + (i * 29) % 18
        d.ellipse([sx, sy, sx + 1.5, sy + 1.5], fill="white")
    # skyline with lit windows
    for bx, bw, bh in ((6, 26, 30), (36, 20, 42), (60, 30, 26), (94, 22, 38), (120, 26, 30)):
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill="#232c4d")
        for wy in range(y + h - bh + 5, y + h - 4, 9):
            for wx in range(x + bx + 4, x + bx + bw - 4, 8):
                if (wx + wy) % 17 < 8:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill="#ffd94d")
    fnt = SANS_B(11)
    d.text((x + 26, y + 6), "VICE CITY", font=fnt, fill="#ff7ad9")

def scene_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#e6dcc4")
    d.polygon([(x + 18, y + 16), (x + w / 2, y + 4), (x + w - 18, y + 16)], fill="#c9b489")
    d.rectangle([x + 18, y + 16, x + w - 18, y + 20], fill="#8a7a58")
    for cx in (x + 30, x + w / 2, x + w - 30):
        d.rectangle([cx - 4, y + 20, cx + 4, y + h - 12], fill="#efe6cf", outline="#8a7a58")
    d.rectangle([x + 14, y + h - 12, x + w - 14, y + h - 6], fill="#8a7a58")
    # scales of justice, small, centred
    sx, sy = x + w / 2, y + 30
    d.line([sx, sy, sx, sy + 12], fill="#5c4a2a", width=2)
    d.line([sx - 12, sy + 2, sx + 12, sy + 2], fill="#5c4a2a", width=2)
    d.polygon([(sx - 16, sy + 8), (sx - 8, sy + 8), (sx - 12, sy + 2)], fill="#d9a400")
    d.polygon([(sx + 8, sy + 8), (sx + 16, sy + 8), (sx + 12, sy + 2)], fill="#d9a400")

def scene_document(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#e9e2d0")
    d.rectangle([x + w * 0.28, y + 6, x + w * 0.72, y + h - 6], fill="white", outline="#8a8a8a")
    fnt = SANS_B(9)
    t = "DECLARATION"
    d.text((x + w / 2 - d.textlength(t, font=fnt) / 2, y + 9), t, font=fnt, fill=RED)
    for i, ly in enumerate(range(y + 22, y + h - 12, 7)):
        d.line([x + w * 0.32, ly, x + w * 0.68, ly], fill="#9a9a9a", width=1)
    # two small flags at the base
    d.rectangle([x + 8, y + h - 22, x + 30, y + h - 10], fill="#1e3a8a")
    d.rectangle([x + w - 30, y + h - 22, x + w - 8, y + h - 10], fill="#0e7a3d")

def scene_train(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#dfe9f2")
    d.rectangle([x + 8, y + 14, x + w - 8, y + h - 16], fill="#c0392b")
    d.rectangle([x + 8, y + 14, x + w - 8, y + 26], fill="white")
    for wx in range(x + 16, x + w - 16, 18):
        d.rectangle([wx, y + 30, wx + 11, y + 40], fill="#bfe3f2")
    # wheels + rail
    for cx in (x + 34, x + w - 34):
        d.ellipse([cx - 7, y + h - 24, cx + 7, y + h - 10], fill="#2c2c34")
    d.line([x, y + h - 8, x + w, y + h - 8], fill="#5c5c5c", width=3)
    fnt = SANS_B(10)
    t = "STRIKE"
    tw = d.textlength(t, font=fnt)
    d.rectangle([x + w - tw - 14, y + 4, x + w - 6, y + 18], fill="white", outline=RED, width=2)
    d.text((x + w - tw - 10, y + 6), t, font=fnt, fill=RED)

def scene_space(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#0e1530")
    for i in range(18):
        sx = x + 4 + (i * 47) % (w - 8)
        sy = y + 3 + (i * 31) % (h - 8)
        d.ellipse([sx, sy, sx + 1.5, sy + 1.5], fill="white")
    d.ellipse([x + w - 52, y + 8, x + w - 12, y + 48], fill="#9a9a9a", outline="#6a6a6a")
    d.ellipse([x + w - 44, y + 16, x + w - 34, y + 26], fill="#7a7a7a")
    d.ellipse([x + w - 30, y + 30, x + w - 22, y + 38], fill="#7a7a7a")
    # satellite with panels
    sx, sy = x + 30, y + h - 22
    d.rectangle([sx - 5, sy - 5, sx + 5, sy + 5], fill="#d9d9d9", outline="#666")
    d.rectangle([sx - 22, sy - 3, sx - 6, sy + 3], fill="#2b5ea7")
    d.rectangle([sx + 6, sy - 3, sx + 22, sy + 3], fill="#2b5ea7")
    d.arc([x + 4, y + 4, x + w - 4, y + h - 4], 300, 60, fill="#5b87ad", width=1)

def scene_atom(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#eef2f6")
    cx, cy = x + w * 0.32, y + h * 0.52
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    for a in (90, 210, 330):
        d.pieslice([cx - 17, cy - 17, cx + 17, cy + 17], a - 55, a - 5, fill="#f2b705")
    # small document at right
    d.rectangle([x + w - 46, y + 10, x + w - 12, y + h - 10], fill="white", outline="#8a8a8a")
    for ly in range(y + 16, y + h - 14, 6):
        d.line([x + w - 41, ly, x + w - 17, ly], fill="#9a9a9a", width=1)

def scene_pyramid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#f0e0b8")
    d.ellipse([x + w - 30, y + 6, x + w - 8, y + 28], fill="#ffd94d")
    d.polygon([(x + 14, y + h - 8), (x + w * 0.45, y + 12), (x + w * 0.82, y + h - 8)], fill="#c9a45c")
    d.polygon([(x + 14, y + h - 8), (x + w * 0.45, y + 12), (x + w * 0.45, y + h - 8)], fill="#b08d42")
    for gx, gy in ((x + 26, y + h - 14), (x + 40, y + h - 20), (x + w - 24, y + h - 14)):
        d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill="#d9a400")

def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#8fbf6f")
    d.rectangle([x + 10, y + h - 16, x + w - 10, y + h - 8], fill="#d9c08a")
    # stumps
    for sx in (x + 24, x + 29, x + 34):
        d.line([sx, y + h - 26, sx, y + h - 16], fill="#f4e9c8", width=2)
    # bat + ball
    d.line([x + w - 52, y + 14, x + w - 30, y + h - 22], fill="#8a6d3b", width=5)
    d.ellipse([x + w - 26, y + 12, x + w - 16, y + 22], fill=RED)
    d.arc([x + w - 60, y + h - 34, x + w - 10, y + h - 6], 200, 330, fill="white", width=2)

def scene_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#0d2b16")
    # bars, rising left to right
    heights = [10, 16, 14, 22, 28, 34]
    bw = (w - 16) // len(heights)
    for i, bh in enumerate(heights):
        bx = x + 8 + i * bw
        d.rectangle([bx, y + h - 6 - bh, bx + bw - 3, y + h - 6], fill="#2ecc71")
    # "ANT" label sits right of the number badge; the trend line starts
    # further right again, so neither touches the label.
    fnt = SANS_B(10)
    d.text((x + 26, y + 6), "ANT", font=fnt, fill="#7be495")
    f2 = SANS_B(11)
    t = "$1.5tn"
    d.text((x + w - d.textlength(t, font=f2) - 8, y + 5), t, font=f2, fill="white")
    # trend line: starts right of the ANT label, rises to the top-right
    pts = [(x + 62, y + h - 16), (x + 80, y + h - 26), (x + 100, y + h - 24),
           (x + 124, y + h - 34), (x + w - 10, y + 16)]
    d.line(pts, fill="#ffd94d", width=2)

def scene_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#2b1a12")
    cx, cy = x + w / 2, y + h / 2
    for i in range(12):
        a = 2 * math.pi * i / 12
        x2, y2 = cx + 34 * math.cos(a), cy + 24 * math.sin(a)
        d.line([cx, cy, x2, y2], fill="#ff9d00", width=3)
    d.ellipse([cx - 16, cy - 12, cx + 16, cy + 12], fill="#ffd94d")
    d.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill="#fff3b0")

def scene_globe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#dfe9f2")
    d.ellipse([x + 12, y + 8, x + 62, y + h - 8], fill="#2b5ea7")
    d.ellipse([x + 22, y + 14, x + 40, y + 26], fill="#7fbf8f")
    d.ellipse([x + 34, y + 32, x + 54, y + 44], fill="#7fbf8f")
    d.arc([x + 8, y + 4, x + 66, y + h - 4], 200, 340, fill="white", width=2)
    d.rectangle([x + w - 52, y + 12, x + w - 12, y + h - 12], fill="white", outline="#8a8a8a")
    for ly in range(y + 18, y + h - 16, 6):
        d.line([x + w - 47, ly, x + w - 17, ly], fill="#9a9a9a", width=1)

SCENES = {
    "cyclone": scene_cyclone, "summit": scene_summit, "crowd": scene_crowd,
    "cop": scene_cop, "vicecity": scene_vicecity, "court": scene_court,
    "document": scene_document, "train": scene_train, "space": scene_space,
    "atom": scene_atom, "pyramid": scene_pyramid, "cricket": scene_cricket,
    "chart": scene_chart, "blast": scene_blast, "globe": scene_globe,
}

# ---------- dotted world map ----------
def _on_land(lon, lat):
    for lo0, lo1, la0, la1 in LAND:
        if lo0 <= lon <= lo1 and la0 <= lat <= la1:
            return True
    return False

def draw_map(d, x, y, w, h):
    """Dotted world map with numbered pins (1-15), de-collided."""
    d.rectangle([x, y, x + w, y + h], fill="#eef3f6", outline=LINE, width=1)
    # dots every 4 degrees
    for lon in range(-180, 181, 4):
        for lat in range(-55, 86, 4):
            if _on_land(lon, lat):
                px = x + (lon + 180) / 360.0 * w
                py = y + (85 - lat) / 140.0 * h
                d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill="#7d8aa0")
    # pin positions, then push overlapping pins apart (leader lines stay true)
    pos = []
    for n, lon, lat in PINS:
        px = x + (lon + 180) / 360.0 * w
        py = y + (85 - lat) / 140.0 * h
        pos.append([n, px, py, px, py])
    for _ in range(30):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx, dy = pos[j][1] - pos[i][1], pos[j][2] - pos[i][2]
                dist = math.hypot(dx, dy)
                if dist < 19 and dist > 0.01:
                    push = (19 - dist) / 2.0
                    ux, uy = dx / dist, dy / dist
                    pos[i][1] -= ux * push; pos[i][2] -= uy * push
                    pos[j][1] += ux * push; pos[j][2] += uy * push
                    moved = True
        if not moved:
            break
    fnt = SANS_B(8)
    for n, px, py, tx, ty in pos:
        if abs(px - tx) > 2 or abs(py - ty) > 2:
            d.line([tx, ty, px, py], fill="#5c5c5c", width=1)
        col = REGION_COLORS[PIN_REGION[n]]
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col, outline="white", width=1)
        d.text((px, py), str(n), font=fnt, fill="white", anchor="mm")

# ---------- layout ----------
def draw_masthead(d):
    f_kick = SANS_B(11)
    d.text((8, 2), "ONE DAY OF WORLD NEWS, ONE PICTURE", font=f_kick, fill=RED)
    right = "69 STORIES · 7 REGIONS · EVERY ONE FROM THIS FRIDAY"
    d.text((1016, 2), right, font=f_kick, fill=RED, anchor="ra")
    d.line([8, 17, 1016, 17], fill=INK, width=2)
    f_title = SERIF_B(54)
    d.text((512, 22), "Friday 20 November 2026", font=f_title, fill=INK, anchor="ma")
    f_sub = SERIF_I(15)
    d.text((512, 80), "A cyclone slams Odisha, the EU meets Britain, and Europe's youth walk out",
           font=f_sub, fill=NAVY, anchor="ma")

def draw_numbers(d):
    y0, y1 = 98, 128
    d.rectangle([8, y0, 108, y1], fill=RED)
    f_lab = SANS_B(12)
    d.text((58, y0 + 4), "BY THE", font=f_lab, fill="white", anchor="ma")
    d.text((58, y0 + 17), "NUMBERS", font=f_lab, fill="white", anchor="ma")
    cell_w = (1016 - 108) / len(NUMBERS)
    f_num = SERIF_B(20)
    f_cap = SANS(10)
    for i, (num, cap) in enumerate(NUMBERS):
        cx = 108 + cell_w * i + cell_w / 2
        if i:
            d.line([108 + cell_w * i, y0 + 4, 108 + cell_w * i, y1 - 4], fill=LINE, width=1)
        d.text((cx, y0 + 1), num, font=f_num, fill=RED, anchor="ma")
        d.text((cx, y0 + 21), cap, font=f_cap, fill=GRAY, anchor="ma")
    d.line([8, y1 + 2, 1016, y1 + 2], fill=INK, width=1)

def draw_region_bar(d):
    y0, y1 = 134, 150
    total_w = 1016 - 8
    # proportional widths, with a floor so narrow labels stay readable
    raw = [(label, col, n, total_w * n / 69.0) for label, col, n in REGION_COUNTS]
    widths = [max(w, 58.0) for _, _, _, w in raw]
    over = sum(widths) - total_w
    # take the excess back from the widest segment
    widest = max(range(len(widths)), key=lambda i: widths[i])
    widths[widest] -= over
    x = 8
    fnt = SANS_B(11)
    fnt_small = SANS_B(10)
    for (label, col, n), w in zip(REGION_COUNTS, widths):
        use = fnt if d.textlength(f"{label} {n}", font=fnt) <= w - 6 else fnt_small
        d.rectangle([x, y0, x + w, y1], fill=REGION_COLORS[col])
        d.text((x + w / 2, y0 + 3), f"{label} {n}", font=use, fill="white", anchor="ma")
        x += w
    assert abs(x - 1016) < 1.5, f"region bar width mismatch: ends at {x}"

def draw_lead(d, lead, x, y, w):
    h = 204
    card(d, x, y, w, h)
    scene_h = 112
    SCENES[lead["scene"]](d, x + 1, y + 1, w - 2, scene_h)
    badge(d, x + 17, y + 17, 13, lead["n"], SANS_B(12))
    ty = y + scene_h + 8
    f_tag = SANS_B(10)
    d.text((x + 10, ty), lead["tag"], font=f_tag, fill=RED)
    d.text((x + w - 10, ty), "CONFIRMED", font=f_tag, fill=NAVY, anchor="ra")
    f_head = SERIF_B(19)
    lines = wrap(d, lead["headline"], f_head, w - 20)
    hy = text_lines(d, x + 10, ty + 15, lines[:2], f_head, INK, leading=20)
    f_body = SANS(11)
    blines = wrap(d, lead["body"], f_body, w - 20)
    text_lines(d, x + 10, hy + 2, blines[:3], f_body, INK, leading=12)

def draw_medium(d, med, x, y, w, h):
    card(d, x, y, w, h)
    scene_h = 50
    SCENES[med["scene"]](d, x + 1, y + 1, w - 2, scene_h)
    badge(d, x + 12, y + 12, 9, med["n"], SANS_B(9))
    ty = y + scene_h + 4
    f_tag = SANS_B(9)
    d.text((x + 7, ty), med["tag"], font=f_tag, fill=RED)
    f_head = SERIF_B(13)
    lines = wrap(d, med["headline"], f_head, w - 14)
    hy = text_lines(d, x + 7, ty + 11, lines[:2], f_head, INK, leading=14)
    f_body = SANS(10)
    blines = wrap(d, med["body"], f_body, w - 14)
    text_lines(d, x + 7, hy + 1, blines[:2], f_body, INK, leading=11)

def draw_bottom(d):
    y0 = 624
    # --- map panel (left) ---
    d.text((8, y0), "WHERE IT HAPPENED", font=SANS_B(13), fill=INK)
    draw_map(d, 8, y0 + 20, 300, 232)
    ly = y0 + 258
    f_leg = SANS(9)
    items = [("Europe", "Europe"), ("The Americas", "Americas"),
             ("Asia-Pacific", "Asia-Pacific"), ("Mideast", "Mideast"),
             ("Africa", "Africa"), ("Oceania", "Oceania"), ("World", "World")]
    lx, ly2 = 8, ly
    for label, key in items:
        if lx + 12 + d.textlength(label, font=f_leg) > 308:
            lx, ly2 = 8, ly2 + 13
        d.ellipse([lx, ly2 + 2, lx + 8, ly2 + 10], fill=REGION_COLORS[key])
        d.text((lx + 11, ly2), label, font=f_leg, fill=INK)
        lx += 12 + d.textlength(label, font=f_leg) + 10
    d.text((8, ly2 + 14), "Pins 1–15 = the illustrated stories, numbered",
           font=f_leg, fill=GRAY)
    d.text((8, ly2 + 26), "as on the page; colours = regions above.",
           font=f_leg, fill=GRAY)
    # --- briefs panel (right) ---
    bx = 316
    d.text((bx, y0), "ALSO ON FRIDAY 20 NOVEMBER", font=SANS_B(13), fill=INK)
    d.line([bx, y0 + 18, 1016, y0 + 18], fill=INK, width=1)
    f_num = SANS_B(10)
    f_txt = SANS(10)
    col_w = 229
    col_x = [bx, bx + col_w + 6, bx + 2 * (col_w + 6)]
    by = y0 + 26
    pitch = 15
    for i, (n, city, head) in enumerate(BRIEFS):
        col = i // 18
        row = i % 18
        cx = col_x[col]
        cy = by + row * pitch
        prefix = f"{n}. {city} — "
        # shorten the headline (drop trailing words) until the line fits
        htext = head
        while d.textlength(prefix + htext, font=f_txt) > col_w and " " in htext:
            htext = htext.rsplit(" ", 1)[0] + "…"
        line = prefix + htext
        assert d.textlength(line, font=f_txt) <= col_w + 1, f"brief {n} overflows: {line}"
        d.text((cx, cy), prefix, font=f_num, fill=RED)
        d.text((cx + d.textlength(prefix, font=f_num), cy), htext, font=f_txt, fill=INK)

def draw_date_check(d):
    y0, y1 = 938, 992
    d.rectangle([8, y0, 1016, y1], outline=RED, width=2)
    f_head = SANS_B(11)
    f_body = SANS(10)
    d.text((16, y0 + 3),
           "DATE CHECK — LEFT OUT ON PURPOSE: first reported BEFORE Friday 20 November, so NOT on this page as news —",
           font=f_head, fill=RED)
    lines = wrap(d, DATE_CHECK_ITEMS, f_body, 1016 - 32)
    text_lines(d, 16, y0 + 17, lines[:3], f_body, INK, leading=11)

def draw_footer(d):
    fnt = SANS(9)
    d.text((8, 996),
           "Every story here happened, or was first reported, on Friday 20 November 2026. CLAIM = one side's account, not independently confirmed.",
           font=fnt, fill=GRAY)
    d.text((8, 1008),
           "Sources: AP, Reuters, AFP, BBC, Al Jazeera, The Hindu, NDTV, IMD, EU Council, Arab News. Original drawings.",
           font=fnt, fill=GRAY)

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_numbers(d)
    draw_region_bar(d)
    lead_y, lead_w, lead_gap = 156, 330, 9
    for i, lead in enumerate(LEADS):
        draw_lead(d, lead, 8 + i * (lead_w + lead_gap), lead_y, lead_w)
    med_w, med_h, med_gap = 161, 122, 8
    med_y1, med_y2 = 368, 496
    for i, med in enumerate(MEDIUMS):
        row, col = divmod(i, 6)
        x = 8 + col * (med_w + med_gap)
        y = med_y1 if row == 0 else med_y2
        draw_medium(d, med, x, y, med_w, med_h)
    draw_bottom(d)
    draw_date_check(d)
    draw_footer(d)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT}: {img.size[0]}x{img.size[1]}")

if __name__ == "__main__":
    main()
