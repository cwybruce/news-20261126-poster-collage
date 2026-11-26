"""Copy the pre-rendered poster-collage image for 26 November 2026.

The poster was drawn at build time by draw_poster.py (PIL + fonts) and
stored as entry.png beside this file. This script is a pure-stdlib copier:
it only copies that pre-rendered image into the grader's output directory,
so it needs no third-party packages, fonts, or network access.
"""

import os
import shutil
import sys

MAX_SIZE = 1048576  # 1 MiB

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def main():
    if not os.path.isfile(SRC):
        print("error: entry.png not found next to main.py", file=sys.stderr)
        return 1

    size = os.path.getsize(SRC)
    if size > MAX_SIZE:
        print(
            "error: entry.png is %d bytes, over the %d-byte limit"
            % (size, MAX_SIZE),
            file=sys.stderr,
        )
        return 1

    with open(SRC, "rb") as f:
        magic = f.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        print(
            "error: entry.png is not a valid PNG file "
            "(bad magic bytes: %r)" % (magic,),
            file=sys.stderr,
        )
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dest)

    copied = os.path.getsize(dest)
    if copied != size:
        print(
            "error: copied size %d does not match source size %d"
            % (copied, size),
            file=sys.stderr,
        )
        return 1

    print("copied entry.png (%d bytes) to %s" % (copied, dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
