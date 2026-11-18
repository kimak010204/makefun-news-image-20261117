#!/usr/bin/env python3
"""Entry for make.fun news-image-20261117.

Copies the bundled front page (``image.png``) to the output directory as
``entry.png``.

The bundled image is a 1024x1024 newspaper front page, "THE WORLD —
TUESDAY, NOVEMBER 17, 2026", summing up the day's world news in five
stories: the Crimea bridge strike, Trump's Asia trip, the Strait of
Hormuz tanker attacks, the failed Vulcan rocket launch, and the
JPMorgan outage.

Pure Python 3.13 standard library. No network, no randomness, no clock:
the output is a byte-for-byte copy of the bundled image, so two runs
produce identical bytes.
"""

import os
import shutil
import struct
import sys

MAX_IMAGE_BYTES = 1024 * 1024  # 1 MiB competition limit
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    """Print a clear error and exit non-zero."""
    print("error: " + message, file=sys.stderr)
    return 1


def png_dimensions(path):
    """Return (width, height) from a PNG file's IHDR chunk."""
    with open(path, "rb") as handle:
        header = handle.read(8)
        if header != PNG_MAGIC:
            raise ValueError("not a PNG file (bad magic bytes)")
        chunk = handle.read(8)
        if len(chunk) < 8 or chunk[4:8] != b"IHDR":
            raise ValueError("not a PNG file (no IHDR chunk)")
        width, height = struct.unpack(">II", handle.read(8))
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "image.png")

    if not os.path.isfile(source):
        return fail("bundled image not found: " + source)

    try:
        width, height = png_dimensions(source)
    except (OSError, ValueError) as exc:
        return fail("bundled image.png is not a valid PNG: " + str(exc))

    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        return fail(
            "bundled image.png is %dx%d, expected %dx%d"
            % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT)
        )

    size = os.path.getsize(source)
    if size == 0:
        return fail("bundled image.png is empty (0 bytes)")
    if size > MAX_IMAGE_BYTES:
        return fail(
            "bundled image.png is %d bytes, over the %d byte limit"
            % (size, MAX_IMAGE_BYTES)
        )

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    destination = os.path.join(output_dir, "entry.png")

    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        return fail("failed to copy image to %s: %s" % (destination, exc))

    # Verify the copy is complete and intact: a truncated or corrupt
    # write must fail loudly instead of shipping a bad entry.
    copied = os.path.getsize(destination)
    if copied != size:
        return fail(
            "copied image is %d bytes, expected %d" % (copied, size)
        )
    try:
        copied_width, copied_height = png_dimensions(destination)
    except (OSError, ValueError) as exc:
        return fail("copied image failed validation: " + str(exc))
    if (copied_width, copied_height) != (width, height):
        return fail("copied image dimensions changed during copy")

    print(
        "wrote %s (%dx%d, %d bytes)"
        % (destination, width, height, size)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
