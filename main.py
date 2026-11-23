#!/usr/bin/env python3
"""Publish the rendered front page into the make.fun output directory.

Standard library only: no Pillow, no network.  The renderer in art/render.py
is the only thing that needs Pillow; this copier just moves the finished PNG
into place, refusing to publish anything that breaks the bounty's gate rules.
"""

import os
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "art" / "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_EDGE = 1024
MAX_BYTES = 1048576


def ihdr_size(data):
    """Return (width, height) from the PNG's IHDR chunk."""
    assert data[:8] == PNG_SIGNATURE, "not a PNG: bad signature"
    assert data[12:16] == b"IHDR", "not a PNG: first chunk is not IHDR"
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    if not SOURCE.exists():
        print("error: source image missing: %s\n"
              "       render it first with: python3 art/render.py" % SOURCE,
              file=sys.stderr)
        return 1

    data = SOURCE.read_bytes()
    width, height = ihdr_size(data)

    assert width <= MAX_EDGE, "width %d exceeds %d" % (width, MAX_EDGE)
    assert height <= MAX_EDGE, "height %d exceeds %d" % (height, MAX_EDGE)
    assert len(data) <= MAX_BYTES, "size %d exceeds %d" % (len(data), MAX_BYTES)

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "entry.png"
    written = target.write_bytes(data)
    assert written == len(data), "wrote %d of %d bytes" % (written, len(data))
    assert target.read_bytes() == data, "bytes on disk differ from source"

    print("copied %s -> %s (%d bytes, %dx%d)"
          % (SOURCE, target, len(data), width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
