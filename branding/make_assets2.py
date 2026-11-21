#!/usr/bin/env python3
"""The rest of the ZMyusic asset family: vectors, SVG sources, TV/Wear,
desktop ICO/ICNS and the iOS preview images. Run from the repo root:

    py branding/make_assets2.py
"""
from __future__ import annotations

import os
import shutil
import struct

from PIL import Image

import make_assets as A

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def R(*p):
    return os.path.join(ROOT, *p)


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", os.path.relpath(path, ROOT), img.size)


# ---------------------------------------------------------------- vector XML

# The Z + M as stroked capsule segments on the 108dp adaptive canvas. Android
# masks crop to ~66dp, so the ink is scaled into the centre.

def _fg_vector(path, comment):
    segs = [
        (268, 300, 520, 300), (520, 300, 268, 724), (268, 724, 520, 724),
        (556, 724, 556, 300), (556, 300, 700, 560), (700, 560, 844, 300),
        (844, 300, 844, 724),
    ]
    # map 1024-space to the 108dp canvas, mark box (196..906) -> (19.8..88.2)
    def m(v):
        return round(19.8 + (v - 196) * (88.2 - 19.8) / (906 - 196), 2)

    w = round(92 * (88.2 - 19.8) / (906 - 196), 2)
    paths = "\n".join(
        f'  <path android:pathData="M{m(ax)},{m(ay)} L{m(bx)},{m(by)}" '
        f'android:strokeColor="#FFFFFFFF" android:strokeWidth="{w}" '
        f'android:strokeLineCap="round" android:strokeLineJoin="round"/>'
        for ax, ay, bx, by in segs
    )
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!--
  {comment}
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
{paths}
</vector>
'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print("wrote", os.path.relpath(path, ROOT))


def _logo_vector(path, viewport_w, viewport_h, comment, pad=0.0):
    """The Z+M as a stroked mark on a WxH viewport (used for ic_logo.xml)."""
    segs = [
        (268, 300, 520, 300), (520, 300, 268, 724), (268, 724, 520, 724),
        (556, 724, 556, 300), (556, 300, 700, 560), (700, 560, 844, 300),
        (844, 300, 844, 724),
    ]
    # mark box in 1024-space is x 222..890, y 254..770 (stroke included)
    bx0, bx1, by0, by1 = 222, 890, 254, 770
    sw, sh = viewport_w, viewport_h
    scale = min(sw / (bx1 - bx0), sh / (by1 - by0)) * (1 - pad)
    ox = (sw - (bx1 - bx0) * scale) / 2 - bx0 * scale
    oy = (sh - (by1 - by0) * scale) / 2 - by0 * scale

    def X(v):
        return round(v * scale + ox, 2)

    def Y(v):
        return round(v * scale + oy, 2)

    w = round(92 * scale, 2)
    paths = "\n".join(
        f'  <path d="M{X(ax)},{Y(ay)} L{X(bx)},{Y(by)}" '
        f'fill="none" stroke="#FFFFFF" stroke-width="{w}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        for ax, ay, bx, by in segs
    )
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!--
  {comment}
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="{round(sw)}dp"
    android:height="{round(sh)}dp"
    android:viewportWidth="{int(sw)}"
    android:viewportHeight="{int(sh)}">
{paths}
</vector>
'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print("wrote", os.path.relpath(path, ROOT))


def _notification_vector(path):
    segs = [
        (268, 300, 520, 300), (520, 300, 268, 724), (268, 724, 520, 724),
        (556, 724, 556, 300), (556, 300, 700, 560), (700, 560, 844, 300),
        (844, 300, 844, 724),
    ]
    bx0, bx1, by0, by1 = 222, 890, 254, 770
    # fit inside a 22dp content box on a 24dp canvas
    size = 22.0
    scale = size / max(bx1 - bx0, by1 - by0)
    ox = (24 - (bx1 - bx0) * scale) / 2 - bx0 * scale
    oy = (24 - (by1 - by0) * scale) / 2 - by0 * scale

    def X(v):
        return round(v * scale + ox, 2)

    def Y(v):
        return round(v * scale + oy, 2)

    w = round(92 * scale, 2)
    paths = "\n".join(
        f'  <path android:pathData="M{X(ax)},{Y(ay)} L{X(bx)},{Y(by)}" '
        f'android:strokeColor="#FFFFFFFF" android:strokeWidth="{w}" '
        f'android:strokeLineCap="round" android:strokeLineJoin="round"/>'
        for ax, ay, bx, by in segs
    )
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!--
  Status-bar / notification silhouette of the ZMyusic mark. The system keeps
    only the alpha channel, so the fill is opaque white and the ink sits inside
    the 22dp content box Android expects on a 24dp canvas.
-->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
{paths}
</vector>
'''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    print("wrote", os.path.relpath(path, ROOT))


def _bg_vectors():
    """Wear/reused solid backgrounds (navy gradient) keep their shape."""
    for rel in ("wearos/src/main/res/drawable/ic_launcher_background.xml",):
        src = R("app", "src", "main", "res", "drawable", "ic_launcher_background.xml")
        dst = R(rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        print("copied", os.path.relpath(dst, ROOT))


# ------------------------------------------------------------------ SVG files

MARK_SVG = '''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- The ZMyusic Z+M monogram, as white strokes tinted by the caller. -->
  <g stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none" transform="translate({ox} {oy}) scale({s})">
    <path d="M268 300 H520 L268 724 H520"/>
    <path d="M556 724 V300 L700 560 L844 300 V724"/>
  </g>
</svg>
'''


def _mark_svg(path, w, h, pad=0.08):
    bx0, bx1, by0, by1 = 222, 890, 254, 770
    s = min(w / (bx1 - bx0), h / (by1 - by0)) * (1 - pad)
    ox = (w - (bx1 - bx0) * s) / 2 - bx0 * s
    oy = (h - (by1 - by0) * s) / 2 - by0 * s
    txt = MARK_SVG.format(w=w, h=h, sw=round(92 * s, 2), ox=round(ox, 2), oy=round(oy, 2), s=round(s, 4))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    print("wrote", os.path.relpath(path, ROOT))


FAVICON = '''<svg width="1024" height="1024" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="bg" x1="512" y1="0" x2="512" y2="1024" gradientUnits="userSpaceOnUse">
<stop stop-color="#071A3C"/>
<stop offset="1" stop-color="#0B2C63"/>
</linearGradient>
<radialGradient id="glow" cx="0" cy="0" r="1" gradientTransform="translate(512 450) rotate(90) scale(470)" gradientUnits="userSpaceOnUse">
<stop stop-color="#22D3EE" stop-opacity="0.28"/>
<stop offset="1" stop-color="#22D3EE" stop-opacity="0"/>
</radialGradient>
<linearGradient id="mark" x1="260" y1="250" x2="780" y2="800" gradientUnits="userSpaceOnUse">
<stop stop-color="#67E8F9"/>
<stop offset="0.45" stop-color="#22D3EE"/>
<stop offset="1" stop-color="#2563EB"/>
</linearGradient>
<clipPath id="squircle"><rect width="1024" height="1024" rx="230"/></clipPath>
</defs>
<g clip-path="url(#squircle)">
<rect width="1024" height="1024" fill="url(#bg)"/>
<rect width="1024" height="1024" fill="url(#glow)"/>
</g>
<g stroke="url(#mark)" stroke-width="92" stroke-linecap="round" stroke-linejoin="round" fill="none">
<path d="M268 300 H520 L268 724 H520"/>
<path d="M556 724 V300 L700 560 L844 300 V724"/>
</g>
</svg>
'''


# ----------------------------------------------------------- ICO / ICNS writer

def write_ico(path, sizes=(16, 24, 32, 48, 64, 128, 256)):
    imgs = [A.icon(s).convert("RGBA") for s in sizes]
    imgs[0].save(path, format="ICO", sizes=[(s, s) for s in sizes])
    print("wrote", os.path.relpath(path, ROOT), "ICO")


def write_icns(path, master=1024):
    """Minimal ICNS: ic07..ic14 PNG-encoded entries."""
    types = {
        "ic07": 128, "ic08": 256, "ic09": 512, "ic10": 1024,
        "ic11": 32, "ic12": 64, "ic13": 256, "ic14": 512,
    }
    chunks = []
    for tag, px in types.items():
        img = A.icon(px).convert("RGBA")
        tmp = R("branding", "_tmp.png")
        img.save(tmp)
        with open(tmp, "rb") as f:
            data = f.read()
        chunks.append(tag.encode("ascii") + struct.pack(">I", len(data) + 8) + data)
    os.remove(tmp)
    body = b"".join(chunks)
    with open(path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", len(body) + 8) + body)
    print("wrote", os.path.relpath(path, ROOT), "ICNS")


def main():
    # Vector drawables
    _fg_vector(R("app", "src", "main", "res", "drawable", "ic_launcher_foreground.xml"),
               "The ZMyusic mark. The 108dp canvas keeps the ink inside the 66dp\n    safe zone every launcher mask crops to.")
    _fg_vector(R("wearos", "src", "main", "res", "drawable", "ic_launcher_foreground.xml"),
               "The ZMyusic mark for Wear OS.")
    _logo_vector(R("app", "src", "main", "res", "drawable", "ic_logo.xml"), 28, 24.2,
                 "The ZMyusic mark, drawn as rounded capsules so every renderer\n    (Compose, TV, Wear) shows the same shape. Tinted by the caller.")
    _logo_vector(R("wearos", "src", "main", "res", "drawable", "ic_logo.xml"), 28, 24.2,
                 "The ZMyusic mark for Wear OS.")
    _notification_vector(R("app", "src", "main", "res", "drawable", "ic_notification_logo.xml"))
    _bg_vectors()

    # SVG sources
    _mark_svg(R("app", "src", "main", "assets", "Logo.svg"), 560, 484, pad=0.0)
    _mark_svg(R("app", "src", "main", "assets", "LogoTransparent.svg"), 560, 484, pad=0.0)
    with open(R("web", "app", "public", "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(FAVICON)
    print("wrote web/app/public/favicon.svg")
    with open(R("docs", "assets", "favicon.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(FAVICON)
    print("wrote docs/assets/favicon.svg")

    # Desktop ICO / ICNS
    write_ico(R("desktopApp", "packaging", "icons", "AppIcon.ico"))
    write_icns(R("desktopApp", "packaging", "icons", "AppIcon.icns"))

    # TV banner (1024x576, TV-safe) and Wear launcher icons
    tv = A.banner(1024, 576)
    for dens in ("", "drawable-hdpi", "drawable-mdpi", "drawable-xhdpi"):
        p = R("tv", "src", "main", "res", dens, "tv_banner.png") if dens else R("tv", "src", "main", "res", "drawable", "tv_banner.png")
        save(tv, p)
    for dens, px in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144)):
        save(A.icon(px), R("wearos", "src", "main", "res", f"mipmap-{dens}", "ic_launcher.png"))

    # iOS preview images (light/dark) for each AppIconPreviews imageset
    previews = {
        "AppIconPreview": (False, "glass"),
        "AppIconGlassDarkPreview": (True, "glass"),
        "AppIconGlassClearPreview": (False, "clear"),
        "AppIconGlassClearDarkPreview": (True, "clear"),
        "AppIconMonochromePreview": (False, "mono"),
    }
    for name, (dark, kind) in previews.items():
        base = R("ios", "App", "Myusic", "Assets.xcassets", "AppIconPreviews", f"{name}.imageset")
        if kind == "mono":
            img = A.icon(1024).convert("RGBA")
        elif kind == "clear":
            plate = A._bg(1024 * 1)
            img = A.icon(1024)
        else:
            img = A.icon(1024)
        for variant in ("light", "dark"):
            save(img, os.path.join(base, f"{variant}.png"))

    print("done")


if __name__ == "__main__":
    main()
