#!/usr/bin/env python3
"""Clean and crop TreeViz SVG/PNG exports.

The script removes generated scale-bar layers, crops the SVG viewBox based on
the raster content, regenerates an opaque light PNG, and can write dark-mode
copies using the same default branch-color remap used by the TreeViz UI.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image


DARK_COLOR_MAP = {
    "#000": "#f4f7fb",
    "#000000": "#f4f7fb",
    "#0d5c4d": "#49c4b0",
    "#0f766e": "#59cdb8",
    "#111111": "#f4f7fb",
    "#117865": "#59cdb8",
    "#172125": "#f4f7fb",
    "#1c2024": "#f4f7fb",
    "#333333": "#f4f7fb",
    "#334155": "#d6e0ea",
    "#475569": "#c6d1dc",
    "#5f6b76": "#c6d1dc",
    "#64748b": "#b8c5d2",
    "#7b8791": "#adb9c5",
    "#8a93a1": "#9eacb9",
    "#94a3b8": "#9eacb9",
}


def strip_scale_bar(svg: str) -> tuple[str, int]:
    return re.subn(r'<g data-tv-layer="scale-bar">.*?</g>', "", svg)


def content_bbox(png: Path, layout: str, white_threshold: int, ignore_scale_bar_corner: bool) -> tuple[int, int, int, int]:
    image = Image.open(png).convert("RGBA")
    pixels = image.load()
    width, height = image.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(8, max(8, height - 8)):
        for x in range(8, max(8, width - 8)):
            if ignore_scale_bar_corner and layout != "rectangular" and x < 500 and y > height - 110:
                continue
            red, green, blue, alpha = pixels[x, y]
            if alpha and not (red > white_threshold and green > white_threshold and blue > white_threshold):
                xs.append(x)
                ys.append(y)
    if not xs:
        return (0, 0, width, height)
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def pad_bbox(bbox: tuple[int, int, int, int], image_size: tuple[int, int], layout: str, pad: int) -> tuple[int, int, int, int]:
    left, top, right, bottom = bbox
    width, height = image_size
    if layout in {"circular", "radial"}:
        side = max(right - left, bottom - top) + 2 * pad
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2
        left = round(center_x - side / 2)
        top = round(center_y - side / 2)
        right = left + round(side)
        bottom = top + round(side)
        if left < 0:
            right -= left
            left = 0
        if top < 0:
            bottom -= top
            top = 0
        if right > width:
            left -= right - width
            right = width
        if bottom > height:
            top -= bottom - height
            bottom = height
        return (max(0, left), max(0, top), right, bottom)
    return (
        max(0, left - pad),
        max(0, top - pad),
        min(width, right + pad),
        min(height, bottom + pad),
    )


def crop_svg_viewbox(svg_path: Path, bbox: tuple[int, int, int, int]) -> tuple[int, int, int]:
    svg, removed = strip_scale_bar(svg_path.read_text())
    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top
    svg = re.sub(r'width="[^"]+"', f'width="{width}"', svg, count=1)
    svg = re.sub(r'height="[^"]+"', f'height="{height}"', svg, count=1)
    svg = re.sub(r'viewBox="[^"]+"', f'viewBox="{left} {top} {width} {height}"', svg, count=1)
    svg_path.write_text(svg)
    return removed, width, height


def run_rsvg(svg: Path, png: Path, background: str | None = None) -> None:
    command = ["rsvg-convert"]
    if background:
        command.extend(["-b", background])
    command.extend([str(svg), "-o", str(png)])
    subprocess.run(command, check=True)


def darken_svg(svg: str, background: str) -> str:
    dark = svg
    for source, target in DARK_COLOR_MAP.items():
        dark = re.sub(re.escape(source), target, dark, flags=re.IGNORECASE)
    match = re.search(r'viewBox="([^" ]+) ([^" ]+) ([^" ]+) ([^" ]+)"', dark)
    if not match:
        raise ValueError("SVG is missing a root viewBox")
    x, y, width, height = match.groups()
    background_rect = f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{background}"/>'
    return dark.replace('><g data-tv-id="zoom-group"', f">{background_rect}<g data-tv-id=\"zoom-group\"", 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg", required=True, type=Path)
    parser.add_argument("--png", required=True, type=Path)
    parser.add_argument("--layout", choices=["rectangular", "circular", "radial"], required=True)
    parser.add_argument("--pad", type=int, default=24)
    parser.add_argument("--white-threshold", type=int, default=248)
    parser.add_argument("--keep-scale-bar-corner", action="store_true", help="include the bottom-left scale-bar region when computing the crop")
    parser.add_argument("--dark-copy", action="store_true")
    parser.add_argument("--dark-background", default="#0b1115")
    args = parser.parse_args()

    if shutil.which("rsvg-convert") is None:
        raise SystemExit("rsvg-convert is required to regenerate PNG files")
    if not args.svg.exists():
        raise SystemExit(f"missing SVG: {args.svg}")
    if not args.png.exists():
        raise SystemExit(f"missing PNG: {args.png}")

    raw = content_bbox(
        args.png,
        args.layout,
        args.white_threshold,
        ignore_scale_bar_corner=not args.keep_scale_bar_corner,
    )
    image_size = Image.open(args.png).size
    padded = pad_bbox(raw, image_size, args.layout, args.pad)
    removed, width, height = crop_svg_viewbox(args.svg, padded)
    run_rsvg(args.svg, args.png, background="white")

    print(f"raw bbox: {raw}")
    print(f"cropped viewBox: {padded}")
    print(f"output size: {width}x{height}")
    print(f"scale-bar layers removed: {removed}")

    if args.dark_copy:
        dark_svg = args.svg.with_name(args.svg.stem + "_dark.svg")
        dark_png = args.png.with_name(args.png.stem + "_dark.png")
        dark_svg.write_text(darken_svg(args.svg.read_text(), args.dark_background))
        run_rsvg(dark_svg, dark_png)
        print(f"dark SVG: {dark_svg}")
        print(f"dark PNG: {dark_png}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
