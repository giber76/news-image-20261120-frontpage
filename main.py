#!/usr/bin/env python3
"""Entrypoint for the news-image-20261120 entry.

The grader runs this file. It copies the rendered front page (entry.png,
produced by running draw.py) to /output/entry.png. Standard library only,
no network, no extra dependencies.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"


def main():
    if not os.path.isfile(SRC):
        print(f"entry.png not found next to {__file__}", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    shutil.copyfile(SRC, DST)
    print(f"copied {SRC} -> {DST} ({os.path.getsize(DST)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
