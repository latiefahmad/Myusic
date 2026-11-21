#!/usr/bin/env python3
"""Replace the iOS Icon Composer wave layers with the ZMyusic Z+M mark.

Keeps the same three layer files and names so icon.json still composes them;
only the SVG geometry changes. Each segment is a rounded rect plus end discs,
the same construction the original waves used. Run from the repo root:

    py branding/make_ios_icon.py
"""
from __future__ import annotations

import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Capsule segments of the mark in the 1024 viewBox (centre-line endpoints).
W = 92.0  # stroke width
SEG = [
    (268, 300, 520, 300),   # Z top bar
    (520, 300, 268, 724),   # Z diagonal
    (268, 724, 520, 724),   # Z bottom bar
    (556, 724, 556, 300),   # M left stem
    (556, 300, 700, 560),   # M peak
    (700, 560, 844, 300),   # M valley
    (844, 300, 844, 724),   # M right stem
]

TOP = [0, 1]                 # Z top + diagonal
MIDDLE = [2, 4, 5]           # Z bottom + M peak/valley
BOTTOM = [3, 6]              # M stems


def capsule(ax, ay, bx, by):
    r = W / 2
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    cx, cy = (ax + bx) / 2, (ay + by) / 2
    parts = [
        f'<rect x="{-length / 2:.2f}" y="{-r:.2f}" width="{length:.2f}" height="{W:.2f}" rx="{r:.2f}" transform="translate({cx:.2f} {cy:.2f}) rotate({ang:.2f})"/>',
        f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="{r:.2f}"/>',
        f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{r:.2f}"/>',
    ]
    return "".join(parts)


def svg(indices):
    body = "".join(capsule(*SEG[i]) for i in indices)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" '
        'viewBox="0 0 1024 1024"><g fill="#FFFFFF">' + body + "</g></svg>"
    )


def main():
    base = os.path.join(ROOT, "ios", "App", "Myusic")
    layers = {"wave-top.svg": TOP, "wave-middle.svg": MIDDLE, "wave-bottom.svg": BOTTOM}
    icons = [
        "AppIcon.icon", "AppIconGlassDark.icon", "AppIconGlassClear.icon",
        "AppIconGlassClearDark.icon", "AppIconMonochrome.icon",
    ]
    for icon in icons:
        assets = os.path.join(base, icon, "Assets")
        if not os.path.isdir(assets):
            continue
        for name, idx in layers.items():
            with open(os.path.join(assets, name), "w", encoding="utf-8", newline="\n") as f:
                f.write(svg(idx))
        print("updated", icon)
    print("done")


if __name__ == "__main__":
    main()
