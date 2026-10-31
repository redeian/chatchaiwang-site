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
        "depa", "stanford", "oceg", "utcc", "smu", "smu-seal"]

# Some sources ship a monochrome seal. Tint it to the organisation's own site
# blue (#354ca1, taken from smu.edu's stylesheet) rather than leaving it grey.
TINT = {"smu-seal": (53, 76, 161)}


def trim(im: Image.Image) -> Image.Image:
    """Crop to the ink, then add a small transparent margin so no mark sits flush
    against its neighbour in the row — a file drawn to its own canvas edge
    otherwise reads as a sliced logo."""
    im = im.convert("RGBA")
    bbox = im.getbbox()
    if not bbox:
        return im
    core = im.crop(bbox)
    pad = max(2, int(round(max(core.size) * 0.04)))
    canvas = Image.new("RGBA", (core.width + pad * 2, core.height + pad * 2), (0, 0, 0, 0))
    canvas.alpha_composite(core, (pad, pad))
    return canvas


def from_svg(path: pathlib.Path) -> Image.Image:
    """Render at the file's own pixel size. Opening the SVG directly lets Chrome
    centre and crop anything wider than the window, which silently sliced a mark."""
    head = path.read_text(encoding="utf-8", errors="ignore")[:600]
    import re
    m = re.search(r'width="([\d.]+)"\s+height="([\d.]+)"', head) or \
        re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
    w, h = (float(m.group(1)), float(m.group(2))) if m else (1200.0, 600.0)
    scale = min(1.0, 1600.0 / max(w, h))
    w, h = max(1, int(w * scale)), max(1, int(h * scale))
    tmp_html = OUT / f".{path.stem}.html"
    tmp = OUT / f".{path.stem}.png"
    tmp_html.write_text(
        "<html><body style='margin:0;background:transparent'>"
        f"<img src='{path.as_uri()}' width='{w}' height='{h}' style='display:block'>"
        "</body></html>", encoding="utf-8")
    subprocess.run(
        [CHROME, "--headless=new", "--hide-scrollbars", "--disable-gpu",
         "--default-background-color=00000000", "--force-device-scale-factor=1",
         f"--window-size={w},{h}", f"--screenshot={tmp}", str(tmp_html)],
        check=True, capture_output=True,
    )
    im = Image.open(tmp).convert("RGBA").copy()
    tmp.unlink(missing_ok=True)
    tmp_html.unlink(missing_ok=True)
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
        if key in TINT:
            r, g, b = TINT[key]
            px = out.load()
            for y in range(out.height):
                for x in range(out.width):
                    _, _, _, a = px[x, y]
                    if a:
                        px[x, y] = (r, g, b, a)
        out.save(OUT / f"{key}.png", optimize=True)
        made.append((key, out.size, (OUT / f"{key}.png").stat().st_size))
    for key, size, nbytes in made:
        print(f"{key:10} {size[0]:4}x{size[1]:<4} {nbytes//1024}K")


if __name__ == "__main__":
    main()
