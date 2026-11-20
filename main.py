"""Friday 20 November 2026 front page: hand the rendered PNG to the grader.

The picture already lives in this repository as entry.png — it was drawn
ahead of time by draw.py (Pillow, original vector illustrations, no
photographs). This file is the whole program the grader executes: it does
no drawing and needs no network. All it does is read those bytes, confirm
they really are a PNG, and drop an identical copy where the grader looks
for it. The output directory comes from MAKEFUN_OUTPUT_DIR and falls back
to /output when that variable is absent. Because the bytes are copied
verbatim, running the program twice writes identical files.
"""

import hashlib
import os
import sys

MAGIC = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    picture = os.path.join(here, "entry.png")
    with open(picture, "rb") as fh:
        payload = fh.read()
    if payload[: len(MAGIC)] != MAGIC:
        print("entry.png does not start with the PNG magic bytes",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as fh:
        fh.write(payload)
    digest = hashlib.sha256(payload).hexdigest()
    print(f"wrote {target} ({len(payload)} bytes, sha256 {digest[:16]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
