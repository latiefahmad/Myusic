#!/usr/bin/env python3
"""Rasterise the ZMyusic monogram to every Android themed-icon PNG.

The launcher icon system ships, per density, a set of background (opaque,
full-bleed) and foreground (transparent, holds the finished mark in a given
shape + tint) layers. This regenerates them all from the same monogram so the
whole family stays consistent.

Run from the repository root:

    py branding/make_android_icons.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import make_assets as A

NAVY_TOP = A.NAVY_TOP
NAVY_BOTTOM = A.NAVY_BOTTOM
CYAN = A.CYAN
CYAN_SOFT = A.CYAN_SOFT
BLUE = A.BLUE
SILVER = (203, 213, 225)
VIOLET = (167, 139, 250)

SS = 4
DENS = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
# Foreground canvases are 108dp: the same pixels-per-density as the mipmap,
# scaled by 108/48 relative to the 48dp-ish shell. The shipped files are 324px
# at xxhdpi (144 * 2.25), so the foreground scale is density_px * 2.25.
FG_SCALE = 2.25


def _lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def _grad(size, top, bottom):
    return A._bg_gradient(size, size, top, bottom)


def _mark_mask(size):
    """The Z + M as a single thick-stroke mask, on a transparent canvas."""
    return A._mark_mask(size, 1.0)

def _ink(size, c1, c2):
    """Gradient-filled mark over transparency.

    Passing the default brand ink (CYAN_SOFT -> BLUE) reuses the shared smooth
    ramp so the themed layers match the launcher icon exactly; any other tint
    falls back to a plain two-stop ramp.
    """
    if (c1, c2) == (CYAN_SOFT, BLUE):
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        mask = _mark_mask(size)
        out.paste(A._ink_ramp(size, mask.getbbox()), (0, 0), mask)
        return out
    grad = _grad(size, c1, c2)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(grad, (0, 0), _mark_mask(size))
    return out


def _shape_mask(size, shape, inset=0.0):
    """Full-bleed container silhouette for foreground layers."""
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    pad = size * inset
    box = [pad, pad, size - 1 - pad, size - 1 - pad]
    if shape == "apple":
        d.rounded_rectangle(box, radius=int((size - 2 * pad) * 0.2246), fill=255)
    elif shape == "samsung":
        d.rounded_rectangle(box, radius=int((size - 2 * pad) * 0.30), fill=255)
    elif shape == "circle":
        d.ellipse(box, fill=255)
    else:  # full
        d.rectangle(box, fill=255)
    return m


def _bg_opaque(size):
    """Navy gradient, full square (adaptive-icon backgrounds are cropped)."""
    S = size
    img = _grad(S, NAVY_TOP, NAVY_BOTTOM)
    glow = Image.new("L", (S, S), 0)
    gd = ImageDraw.Draw(glow)
    cx, cy, r = S / 2, S * 0.44, S * 0.46
    for i in range(48, 0, -1):
        t = i / 48
        rr = r * t
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=int(72 * (1 - t) ** 1.4))
    gl = Image.new("RGBA", (S, S), CYAN + (0,))
    gl.putalpha(glow)
    img.alpha_composite(gl)
    return img


def _clipped(img, shape, inset=0.0):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), _shape_mask(img.size[0], shape, inset))
    return out


def themed_foreground(size, shape, tint, *, glow=False, translucent=False, dark=False):
    """A finished mark inside its own silhouette, as the launcher alias shows it."""
    S = size
    c1, c2 = tint
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if translucent:
        fill = (255, 255, 255, 46) if not dark else (255, 255, 255, 30)
        plate = Image.new("RGBA", (S, S), fill)
        base.alpha_composite(_clipped(plate, shape))
    elif dark:
        plate = _grad(S, NAVY_TOP, (4, 16, 40))
        plate.alpha_composite(_clipped(Image.new("RGBA", (S, S), (0, 0, 0, 90)), shape))
        base.alpha_composite(plate)
    else:
        plate = _grad(S, NAVY_TOP, NAVY_BOTTOM)
        base.alpha_composite(_clipped(plate, shape))

    ink = _ink(S, c1, c2)
    if glow:
        halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        hm = _mark_mask(S).filter(ImageFilter.GaussianBlur(S * 0.02))
        col = Image.new("RGBA", (S, S), c1 + (150,))
        col.putalpha(hm)
        halo.alpha_composite(col)
        base.alpha_composite(halo)
    base.alpha_composite(ink)

    # clip the whole foreground back to its silhouette
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(base, (0, 0), _shape_mask(S, shape))
    return out


def monochrome_mark(size):
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (size, size), (255, 255, 255, 255)), (0, 0), _mark_mask(size))
    return out


def _save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, px in DENS.items():
        fg = int(px * FG_SCALE)
        d = os.path.join(root, "app", "src", "main", "res", f"mipmap-{name}")

        # Apple-squircle family (launcher adaptive + liquid glass + glass bg)
        _save(_bg_opaque(fg), os.path.join(d, "ic_glass_background.png"))
        for fname, args in {
            "ic_liquid_glass_foreground.png": dict(tint=(CYAN_SOFT, BLUE)),
            "ic_liquid_glass_dark_foreground.png": dict(tint=(CYAN_SOFT, BLUE), dark=True),
            "ic_liquid_glass_clear_foreground.png": dict(tint=(CYAN_SOFT, BLUE), translucent=True),
            "ic_liquid_glass_clear_dark_foreground.png": dict(tint=(CYAN_SOFT, BLUE), translucent=True, dark=True),
        }.items():
            _save(themed_foreground(fg, "apple", args.pop("tint"), **args), os.path.join(d, fname))

        # clear background variants (translucent plate on the navy field)
        for fname, dark in (("ic_glass_clear_background.png", False),
                            ("ic_glass_clear_dark_background.png", True),
                            ("ic_glass_dark_background.png", True)):
            img = _bg_opaque(fg)
            if dark:
                img.alpha_composite(Image.new("RGBA", (fg, fg), (0, 0, 0, 60)))
            _save(img, os.path.join(d, fname))
        _save(monochrome_mark(fg), os.path.join(d, "ic_glass_monochrome.png"))

        # Pixel family (circle silhouette)
        for fname, args in {
            "ic_pixel_glass_foreground.png": dict(tint=(CYAN_SOFT, BLUE)),
            "ic_pixel_glass_dark_foreground.png": dict(tint=(CYAN_SOFT, BLUE), dark=True),
            "ic_pixel_glass_clear_foreground.png": dict(tint=(CYAN_SOFT, BLUE), translucent=True),
            "ic_pixel_glass_clear_dark_foreground.png": dict(tint=(CYAN_SOFT, BLUE), translucent=True, dark=True),
        }.items():
            _save(themed_foreground(fg, "circle", args.pop("tint"), **args), os.path.join(d, fname))

        # Samsung family (wider squircle)
        for fname, args in {
            "ic_samsung_glass_foreground.png": dict(tint=(CYAN_SOFT, BLUE)),
            "ic_samsung_glass_dark_foreground.png": dict(tint=(CYAN_SOFT, BLUE), dark=True),
            "ic_samsung_glass_clear_foreground.png": dict(tint=(CYAN_SOFT, BLUE), translucent=True),
            "ic_samsung_glass_clear_dark_foreground.png": dict(tint=(CYAN_SOFT, BLUE), translucent=True, dark=True),
        }.items():
            _save(themed_foreground(fg, "samsung", args.pop("tint"), **args), os.path.join(d, fname))

        # Neon family: transparent canvas with a glowing mark (cyan/silver/violet)
        neons = {
            "cyan": (CYAN, BLUE),
            "silver": (SILVER, (148, 163, 184)),
            "violet": (VIOLET, (124, 58, 237)),
        }
        for tone, tint in neons.items():
            canvas = Image.new("RGBA", (fg, fg), (0, 0, 0, 0))
            halo = Image.new("RGBA", (fg, fg), (0, 0, 0, 0))
            hm = _mark_mask(fg).filter(ImageFilter.GaussianBlur(fg * 0.025))
            col = Image.new("RGBA", (fg, fg), tint[0] + (170,))
            col.putalpha(hm)
            halo.alpha_composite(col)
            canvas.alpha_composite(halo)
            canvas.alpha_composite(_ink(fg, tint[0], tint[1]))
            _save(canvas, os.path.join(d, f"ic_neon_{tone}_foreground.png"))
            _save(canvas, os.path.join(d, f"ic_pixel_neon_{tone}_foreground.png"))
            _save(canvas, os.path.join(d, f"ic_samsung_neon_{tone}_foreground.png"))

        # monochrome foreground (themed-icon monochrome layer)
        _save(monochrome_mark(fg), os.path.join(d, "ic_monochrome_foreground.png"))

    print("android themed icons written")


if __name__ == "__main__":
    main()
