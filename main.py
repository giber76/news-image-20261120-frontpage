#!/usr/bin/env python3
"""Friday 20 November 2026 — one front page (entrypoint).

The page is already drawn: entry.png sits next to this file, committed
in the repository. This entrypoint only hands it in. It copies entry.png
into the output directory the platform provides (MAKEFUN_OUTPUT_DIR,
default /output) and reports the byte size, so the judge reads exactly
the image that was reviewed. It renders nothing, fetches nothing, and
needs only the standard library.

Run with:
    python3 main.py
or, as the grader does:
    python3 -P -s main.py
"""

import os
import shutil
import sys


def hand_in():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print("FAIL: entry.png is missing next to main.py")
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, dest)
    size = os.path.getsize(dest)
    print(f"entry.png: copied {size} bytes to {dest}")
    print("OK: entry.png handed in")
    return 0


if __name__ == "__main__":
    sys.exit(hand_in())
