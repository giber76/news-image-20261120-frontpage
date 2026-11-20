"""Friday 20 November 2026 front page: hand the rendered PNG to the grader.

This file is the whole program the grader executes. It does no drawing and
needs no network: the picture already lives in the repository as entry.png
(it was painted ahead of time by draw.py, which uses Pillow to draw a
broadsheet of the day's news). All this file does is read those bytes,
confirm they really are a PNG, and drop an identical copy where the grader
looks for it. The output directory comes from MAKEFUN_OUTPUT_DIR and falls
back to /output when that variable is absent. Because the bytes are copied
verbatim, running the program twice writes identical files.
"""

from os import environ
from pathlib import Path
import hashlib
import sys

MAGIC = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))


def run() -> int:
    here = Path(__file__).resolve().parent
    picture = here / "entry.png"
    payload = picture.read_bytes()
    if payload[: len(MAGIC)] != MAGIC:
        print("entry.png does not start with the PNG magic bytes", file=sys.stderr)
        return 1
    target_dir = Path(environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "entry.png"
    target.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    print(f"wrote {target} ({len(payload)} bytes, sha256 {digest[:16]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
