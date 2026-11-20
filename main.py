#!/usr/bin/env python3
"""Friday 20 November 2026 — one front page (v4 entrypoint).

Builds entry.png by running draw.py, then checks the result:
the file exists, it is 1024x1024, and it is non-empty. Run with:
    python3 main.py
The page is drawn by draw.py from the story list in STORIES.md.
"""

import os
import sys

from PIL import Image

import draw


def build():
    draw.main()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    if not os.path.exists(path):
        print("FAIL: entry.png was not written")
        return 1
    with Image.open(path) as im:
        w, h = im.size
        print(f"entry.png: {w}x{h}, {os.path.getsize(path)} bytes")
        if (w, h) != (1024, 1024):
            print("FAIL: entry.png is not 1024x1024")
            return 1
    if os.path.getsize(path) < 50000:
        print("FAIL: entry.png looks empty")
        return 1
    print("OK: entry.png built and verified")
    return 0


if __name__ == "__main__":
    sys.exit(build())
