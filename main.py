#!/usr/bin/env python3
"""news-image-01 V2 entry: copy the bundled front-page image to the output dir.

The image sums up the world's news of Friday 13 November 2026 in 16
stories: Iran claims a strike on a US radar site in Bahrain; Russian
drones hit a Kyiv hospital; the EU agrees a five-nation team for the
Ukraine talks; Turkiye and Qatar sign a mutual defence pact; the UN
watchdog on Iran's uninspected plant; Microsoft's global outage;
Pope Leo XIV's homecoming Mass in Chiclayo; US wholesale prices up
6.5%; the yen near 160; COP31 climate science row; Gaza winter aid;
the Assam bus crash; the Kenya building collapse; Pakistan's raids;
Kane's England caps record; and the 1960 'doomsday' paper date.
The ticker adds: the FBI's $400m North Korea hack, the US record
483,200 deportations, the Senate summoning Huang & Lutnick, and
Zelensky meeting US envoys.
"""

import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
MAX_DIM = 1024


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def jpeg_dimensions(data):
    """Return (width, height) from a JPEG's Start Of Frame segment."""
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        fail("not a JPEG (missing SOI marker)")
    if data[-2:] != b"\xff\xd9":
        fail("not a whole JPEG (missing EOI marker)")
    pos = 2
    while pos + 9 < len(data):
        if data[pos] != 0xFF:
            fail("bad JPEG marker")
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        size = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            height = struct.unpack(">H", data[pos + 5:pos + 7])[0]
            width = struct.unpack(">H", data[pos + 7:pos + 9])[0]
            return width, height
        pos += 2 + size
    fail("no JPEG Start Of Frame segment found")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "image.jpg")
    dst = os.path.join(out_dir, "entry.png")
    if not os.path.isfile(src):
        fail("image.jpg is missing from the entry")
    with open(src, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        fail(f"image is {len(data)} bytes, over the 1 MiB limit")
    width, height = jpeg_dimensions(data)
    if width > MAX_DIM or height > MAX_DIM:
        fail(f"image is {width}x{height}, over the 1024x1024 limit")
    print(f"image.jpg: {width}x{height}, {len(data)} bytes")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
