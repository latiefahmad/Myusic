#!/usr/bin/env python3
"""Rasterise the ZMyusic monogram to every asset the platforms ship.

Draws the mark directly with Pillow instead of relying on an SVG renderer,
so the exact same geometry and brand colours land in every output. Run from
the repository root:

    py branding/make_assets.py
"""
from __future__ import annotations

import os
from PIL import Image, ImageDraw

NAVY_TOP = (7, 26, 60)      # #071A3C
NAVY_BOTTOM = (11, 44, 99)  # #0B2C63
CYAN = (34, 211, 238)       # #22D3EE
CYAN_SOFT = (103, 232, 249)  # #67E8F9
BLUE = (37, 99, 235)        # #2563EB

SS = 4  # supersample factor for smooth edges


def _lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def _bg(size):
    """Navy vertical gradient inside a rounded squircle, with a cyan glow."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = Image.new("RGBA", (1, size))
    for y in range(size):
        grad.putpixel((0, y), _lerp(NAVY_TOP, NAVY_BOTTOM, y / max(1, size - 1)) + (255,))
    grad = grad.resize((size, size))

    # radial cyan glow near the top-centre
    glow = Image.new("L", (size, size), 0)
    gd = ImageDraw.Draw(glow)
    cx, cy, r = size / 2, size * 0.44, size * 0.46
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        rr = r * t
        alpha = int(72 * (1 - t) ** 1.4)
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=alpha)
    glow_rgb = Image.new("RGBA", (size, size), CYAN + (0,))
    glow_rgb.putalpha(glow)
    grad.alpha_composite(glow_rgb)

    # squircle mask (rounded rect, radius ~22.5% of the side)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.2246), fill=255)
    img.paste(grad, (0, 0), mask)
    return img


def _draw_mark(draw, size, scale=1.0):
    """The interlocked Z + M, as thick rounded strokes with a cyan->blue ink."""
    # Work in the SVG's 1024 coordinate space, centred and scaled.
    def P(x, y):
        return (size / 2 + (x - 512) * scale * size / 1024,
                size / 2 + (y - 512) * scale * size / 1024)

    w = 92 * scale * size / 1024
    r = w / 2

    def seg(p, q):
        # rounded thick segment: a line plus a disc at each end
        draw.line([p, q], fill=255, width=int(round(w)))
        for c in (p, q):
            draw.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255)

    pts = {
        "z_tl": P(268, 300), "z_tr": P(520, 300),
        "z_bl": P(268, 724), "z_br": P(520, 724),
        "m_tl": P(556, 724), "m_tr": P(844, 724),
        "m_peak1": P(700, 560), "m_top_l": P(556, 300), "m_top_r": P(844, 300),
    }
    # Z: top bar, diagonal, bottom bar
    seg(pts["z_tl"], pts["z_tr"])
    seg(pts["z_tr"], pts["z_bl"])
    seg(pts["z_bl"], pts["z_br"])
    # M: left stem, peak, valley, right stem  (shares the Z's bottom-right area)
    seg(pts["m_tl"], pts["m_top_l"])
    seg(pts["m_top_l"], pts["m_peak1"])
    seg(pts["m_peak1"], pts["m_top_r"])
    seg(pts["m_top_r"], pts["m_tr"])


def _ink_layer(size, scale=1.0):
    """The mark as a gradient-filled mask over transparent."""
    S = size * SS
    mask = Image.new("L", (S, S), 0)
    _draw_mark(ImageDraw.Draw(mask), S, scale)
    grad = Image.new("RGBA", (S, S))
    for y in range(S):
        t = y / max(1, S - 1)
        col = _lerp(CYAN_SOFT, BLUE, t) if t < 0.5 else _lerp(CYAN, BLUE, (t - 0.5) * 2)
        grad.paste(col + (255,), (0, y, S, y + 1))
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


def icon(size, scale=1.0, transparent=False):
    S = size * SS
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0)) if transparent else _bg(S)
    base.alpha_composite(_ink_layer(S, scale))
    return base.resize((size, size), Image.LANCZOS)


def banner(w, h):
    S_w, S_h = w * SS, h * SS
    bg = Image.new("RGBA", (S_w, S_h), (0, 0, 0, 0))
    grad = Image.new("RGBA", (1, S_h))
    for y in range(S_h):
        grad.putpixel((0, y), _lerp(NAVY_TOP, NAVY_BOTTOM, y / max(1, S_h - 1)) + (255,))
    bg.alpha_composite(grad.resize((S_w, S_h)))
    # glow behind the mark
    glow = Image.new("L", (S_w, S_h), 0)
    gd = ImageDraw.Draw(glow)
    cx, cy, r = S_w * 0.72, S_h * 0.5, S_h * 0.95
    for i in range(48, 0, -1):
        t = i / 48
        rr = r * t
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=int(70 * (1 - t) ** 1.4))
    g_rgb = Image.new("RGBA", (S_w, S_h), CYAN + (0,))
    g_rgb.putalpha(glow)
    bg.alpha_composite(g_rgb)
    # mark on the right
    mark = _ink_layer(S_h, scale=0.62)
    bg.alpha_composite(mark, (int(S_w * 0.72 - S_h / 2), 0))
    return bg.resize((w, h), Image.LANCZOS)


def _save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", path, img.size)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    def R(*p):
        return os.path.join(root, *p)

    master = icon(1024)
    _save(master, R("Logo.png"))
    _save(master, R("docs", "assets", "Logo.png"))
    _save(icon(512), R("app", "src", "main", "ic_launcher-playstore.png"))
    _save(master, R("desktopApp", "packaging", "icons", "AppIcon.png"))
    _save(master, R("ios", ".github", "assets", "icon.png"))

    b = banner(1600, 500)
    _save(b, R("Banner.png"))
    _save(b, R("docs", "assets", "Banner.png"))

    # Android mipmaps
    dens = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    for name, px in dens.items():
        _save(icon(px), R("app", "src", "main", "res", f"mipmap-{name}", "ic_launcher.png"))
        _save(icon(px), R("app", "src", "main", "res", f"mipmap-{name}", "ic_launcher_round.png"))

    # web extension icons
    for px in (16, 32, 48, 96, 128):
        _save(icon(px), R("web", "extension", "public", "icon", f"{px}.png"))

    print("done")


if __name__ == "__main__":
    main()
