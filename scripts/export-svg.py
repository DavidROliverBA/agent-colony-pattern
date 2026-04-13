#!/usr/bin/env python3
"""Convert Excalidraw JSON files to SVG.

Handles the element types used in the Agent Colony diagrams:
rectangle, ellipse, diamond, line, arrow, text.

Not a full Excalidraw renderer — just enough to produce readable GitHub-friendly
SVG for the specific diagrams in this repo. Ignores the "rough" hand-drawn style
and uses clean geometric primitives instead, which renders better at small sizes.
"""

import json
import os
import sys
from pathlib import Path
from xml.sax.saxutils import escape

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DIAGRAMS_DIR = REPO_ROOT / "diagrams"


def svg_header(width, height, pad=20):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{-pad} {-pad} {width + 2*pad} {height + 2*pad}" '
        f'width="{width + 2*pad}" height="{height + 2*pad}" '
        f'font-family="Virgil, Segoe UI Emoji, sans-serif">\n'
        f'<rect x="{-pad}" y="{-pad}" width="{width + 2*pad}" height="{height + 2*pad}" fill="#ffffff"/>\n'
    )


def svg_footer():
    return "</svg>\n"


def compute_bounds(elements):
    """Compute the bounding box of all visible elements."""
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf")
    for el in elements:
        if el.get("isDeleted"):
            continue
        x = el.get("x", 0)
        y = el.get("y", 0)
        w = el.get("width", 0)
        h = el.get("height", 0)
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)
    if min_x == float("inf"):
        return 0, 0, 800, 600
    return min_x, min_y, max_x - min_x, max_y - min_y


def fill_attr(el):
    bg = el.get("backgroundColor")
    if bg is None or bg == "transparent":
        return 'fill="none"'
    fill_style = el.get("fillStyle", "solid")
    if fill_style == "solid" or fill_style == "cross-hatch" or fill_style == "hachure":
        return f'fill="{bg}"'
    return f'fill="{bg}"'


def stroke_attrs(el):
    stroke = el.get("strokeColor", "#1e1e1e")
    width = el.get("strokeWidth", 1)
    style = el.get("strokeStyle", "solid")
    dash = ""
    if style == "dashed":
        dash = f' stroke-dasharray="{width * 4} {width * 2}"'
    elif style == "dotted":
        dash = f' stroke-dasharray="{width} {width * 2}"'
    return f'stroke="{stroke}" stroke-width="{width}"{dash}'


def transform_attr(el):
    angle = el.get("angle", 0)
    if not angle:
        return ""
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 0)
    h = el.get("height", 0)
    cx = x + w / 2
    cy = y + h / 2
    deg = angle * 180 / 3.141592653589793
    return f' transform="rotate({deg} {cx} {cy})"'


def render_rectangle(el):
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 0)
    h = el.get("height", 0)
    rx = 8  # slight rounding to match Excalidraw's sharp rectangles
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'{fill_attr(el)} {stroke_attrs(el)}{transform_attr(el)}/>\n'
    )


def render_ellipse(el):
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 0)
    h = el.get("height", 0)
    cx = x + w / 2
    cy = y + h / 2
    rx = w / 2
    ry = h / 2
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
        f'{fill_attr(el)} {stroke_attrs(el)}{transform_attr(el)}/>\n'
    )


def render_diamond(el):
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 0)
    h = el.get("height", 0)
    points = f"{x + w/2},{y} {x + w},{y + h/2} {x + w/2},{y + h} {x},{y + h/2}"
    return (
        f'<polygon points="{points}" '
        f'{fill_attr(el)} {stroke_attrs(el)}{transform_attr(el)}/>\n'
    )


def render_line_or_arrow(el, is_arrow):
    x = el.get("x", 0)
    y = el.get("y", 0)
    points = el.get("points", [])
    if not points:
        return ""
    # Points are relative to x, y
    abs_points = [(x + p[0], y + p[1]) for p in points]
    # Arrows render as direct straight lines from start to end (ignore
    # intermediate waypoints that Excalidraw adds for routing). Lines keep
    # their polyline shape because they often draw borders or underlines.
    if is_arrow and len(abs_points) > 2:
        abs_points = [abs_points[0], abs_points[-1]]
    path_d = "M " + " L ".join(f"{px},{py}" for px, py in abs_points)
    arrow_marker = ""
    if is_arrow:
        arrow_marker = ' marker-end="url(#arrowhead)"'
    return (
        f'<path d="{path_d}" fill="none" '
        f'{stroke_attrs(el)}{arrow_marker}{transform_attr(el)}/>\n'
    )


MIN_FONT_SIZE = 16  # enforce readability at GitHub's rendered size

def render_text(el):
    x = el.get("x", 0)
    y = el.get("y", 0)
    w = el.get("width", 200)
    h = el.get("height", 20)
    text = el.get("text", "") or ""
    font_size = max(el.get("fontSize", 16), MIN_FONT_SIZE)
    text_align = el.get("textAlign", "left")
    vertical_align = el.get("verticalAlign", "top")
    color = el.get("strokeColor", "#1e1e1e")

    anchor_map = {"left": "start", "center": "middle", "right": "end"}
    anchor = anchor_map.get(text_align, "start")

    if text_align == "center":
        tx = x + w / 2
    elif text_align == "right":
        tx = x + w
    else:
        tx = x

    # Split on newlines and render each line
    lines = text.split("\n")
    line_height = font_size * 1.25

    if vertical_align == "middle":
        total_h = len(lines) * line_height
        start_y = y + h / 2 - total_h / 2 + font_size * 0.9
    else:
        start_y = y + font_size * 0.9

    result = ""
    for i, line in enumerate(lines):
        ty = start_y + i * line_height
        escaped = escape(line)
        result += (
            f'<text x="{tx}" y="{ty}" fill="{color}" '
            f'font-size="{font_size}" text-anchor="{anchor}">{escaped}</text>\n'
        )
    return result


RENDERERS = {
    "rectangle": render_rectangle,
    "ellipse": render_ellipse,
    "diamond": render_diamond,
    "line": lambda el: render_line_or_arrow(el, is_arrow=False),
    "arrow": lambda el: render_line_or_arrow(el, is_arrow=True),
    "text": render_text,
}


def convert(input_path: Path, output_path: Path):
    with open(input_path) as f:
        data = json.load(f)

    elements = [e for e in data.get("elements", []) if not e.get("isDeleted")]

    min_x, min_y, width, height = compute_bounds(elements)

    # Shift all elements to origin
    shifted_elements = []
    for el in elements:
        new_el = dict(el)
        new_el["x"] = el.get("x", 0) - min_x
        new_el["y"] = el.get("y", 0) - min_y
        shifted_elements.append(new_el)

    # Order: rectangles/ellipses/diamonds first, then lines/arrows, then text on top
    def order_key(el):
        t = el.get("type")
        if t in ("rectangle", "ellipse", "diamond"):
            return 0
        if t in ("line", "arrow"):
            return 1
        return 2

    shifted_elements.sort(key=order_key)

    svg_parts = [svg_header(width, height)]

    # Arrowhead marker definition
    svg_parts.append(
        '<defs>\n'
        '  <marker id="arrowhead" markerWidth="10" markerHeight="10" '
        'refX="9" refY="5" orient="auto" markerUnits="strokeWidth">\n'
        '    <path d="M 0 0 L 10 5 L 0 10 z" fill="#1e1e1e"/>\n'
        '  </marker>\n'
        '</defs>\n'
    )

    for el in shifted_elements:
        renderer = RENDERERS.get(el.get("type"))
        if renderer:
            svg_parts.append(renderer(el))

    svg_parts.append(svg_footer())
    output_path.write_text("".join(svg_parts))
    return output_path.stat().st_size


def main():
    files = sorted(DIAGRAMS_DIR.glob("*.excalidraw"))
    if not files:
        print(f"No .excalidraw files found in {DIAGRAMS_DIR}", file=sys.stderr)
        sys.exit(1)

    for f in files:
        out = f.with_suffix(".svg")
        size = convert(f, out)
        print(f"Exported: {out.name} ({size} bytes)")


if __name__ == "__main__":
    main()
