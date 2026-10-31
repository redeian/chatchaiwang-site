#!/usr/bin/env python3
"""Normalise the organisation marks into web-sized PNGs for the site.

Source files live in ~/HermesHome/resume/logos-picked (fetched from each
organisation's own site). Everything is trimmed to its ink and exported at a
single optical height so the wall reads as one row, not a ransom note.
"""
from __future__ import annotations

import pathlib
import subprocess

from PIL import Image

SRC = pathlib.Path.home() / "HermesHome/resume/logos-picked"
OUT = pathlib.Path(__file__).resolve().parent / "assets/logos"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HEIGHT = 96          # 2x a 48 px band height
PAPER = (245, 242, 234, 255)

WANT = ["senate", "etda", "pdpc", "dpim", "true", "srithai", "tcc",
        "depa", "stanford", "oceg", "utcc", "smu"]


def trim(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im


def from_svg(path: pathlib.Path) -> Image.Image:
    tmp = OUT / f".{path.stem}.png"
    subprocess.run(
        [CHROME, "--headless=new", "--hide-scrollbars", "--disable-gpu",
         "--default-background-color=00000000", "--force-device-scale-factor=1",
         "--window-size=1200,600", f"--screenshot={tmp}", str(path)],
        check=True, capture_output=True,
    )
    im = Image.open(tmp).convert("RGBA").copy()
    tmp.unlink(missing_ok=True)
    return trim(im)


def key_white(im: Image.Image) -> Image.Image:
    """Raster sources usually ship on an opaque white card. Make that white
    transparent first, or the trim keeps the card and the wall shows slabs."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 0 and r > 243 and g > 243 and b > 243:
                px[x, y] = (r, g, b, 0)
    return im


def from_raster(path: pathlib.Path) -> Image.Image:
    return trim(key_white(Image.open(path)))


def main():
    made = []
    for key in WANT:
        svg, png = SRC / f"{key}.svg", SRC / f"{key}.png"
        if svg.exists():
            im = from_svg(svg)
        elif png.exists():
            im = from_raster(png)
        else:
            print("missing", key)
            continue
        k = HEIGHT / im.height
        out = im.resize((max(1, round(im.width * k)), HEIGHT), Image.LANCZOS)
        # white-only marks disappear on paper; flatten anything that is mostly
        # transparent ink into a dark tone so it survives the grayscale filter
        px = out.load()
        dark = sum(1 for y in range(0, out.height, 3) for x in range(0, out.width, 3)
                   if px[x, y][3] > 40 and (px[x, y][0] + px[x, y][1] + px[x, y][2]) / 3 > 200)
        total = sum(1 for y in range(0, out.height, 3) for x in range(0, out.width, 3)
                    if px[x, y][3] > 40)
        if total and dark / total > 0.75:
            for y in range(out.height):
                for x in range(out.width):
                    r, g, b, a = px[x, y]
                    if a > 40:
                        px[x, y] = (40, 38, 34, a)
            print("recoloured light mark", key)
        out.save(OUT / f"{key}.png", optimize=True)
        made.append((key, out.size, (OUT / f"{key}.png").stat().st_size))
    for key, size, nbytes in made:
        print(f"{key:10} {size[0]:4}x{size[1]:<4} {nbytes//1024}K")


if __name__ == "__main__":
    main()
