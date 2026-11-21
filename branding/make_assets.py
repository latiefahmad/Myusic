#!/usr/bin/env python3
"""Rasterise the ZMyusic monogram to every asset the platforms ship.

Draws the mark directly with Pillow instead of relying on an SVG renderer,
so the exact same geometry and brand colours land in every output. Run from
the repository root:

    py branding/make_assets.py
"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

NAVY_TOP = (7, 26, 60)      # #071A3C
NAVY_BOTTOM = (11, 44, 99)  # #0B2C63
CYAN = (34, 211, 238)       # #22D3EE
CYAN_SOFT = (103, 232, 249)  # #67E8F9
BLUE = (37, 99, 235)        # #2563EB
TAGLINE = (120, 204, 252)   # #78CCFC - sampled from the original banner

SS = 4  # supersample factor for smooth edges

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(ROOT, "app", "src", "main", "res", "font")
WORDMARK_FONT = os.path.join(HERE, "fonts", "ArchivoBlack-Regular.ttf")

# The ink ramp, interpolated as ONE continuous gradient. The old two-piece
# lerp jumped ~85 units across its midpoint, which read as a hard seam on
# large renders; these three stops are sampled evenly by numpy instead.
INK_STOPS = (
    (0.0, CYAN_SOFT),
    (0.45, CYAN),
    (1.0, BLUE),
)
# Direction of the ink ramp, in mark-normalised units: mostly vertical with a
# slight rightward lean, matching the original artwork.
INK_DY = 0.887

# ------------------------------------------------------------------ banner
# Every banner coordinate below is measured from the shipped Myusic banner
# (1600x500) so the ZMyusic lockup keeps the exact same rhythm: mark inset,
# wordmark top, underline bar and tagline. Only the horizontal placement of
# the whole lockup is centred, because "ZMyusic" is wider than "Myusic".
BANNER_W, BANNER_H = 1600, 500
MARK_LEFT = 199.0        # visual left edge of the mark
MARK_CENTER_Y = 249.5
MARK_REF_W = 292.0       # visual width in the reference banner
TEXT_SPACING = 62.0      # mark right edge -> text block left edge
TEXT_INDENT = 30.0       # text block left edge -> wordmark left edge
WORDMARK_TOP = 169.0
WORDMARK_INK_H = 142.0
BAR_OFFSET_X = 0.0       # bar aligns with the text block left edge
BAR_OFFSET_Y = 151.0     # wordmark top + 151 = bar top (320 in the original)
BAR_W = 96.0
BAR_H = 5.0
TAGLINE_OFFSET_X = 3.0
TAGLINE_OFFSET_Y = 193.0  # wordmark top + 193 = tagline top (362 in the original)
TAGLINE_INK_H = 34.0


def _lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def _sample_ramp(stops, t):
    """Piecewise-linear sample of a stop ramp, vectorised over t."""
    pos = np.asarray([s[0] for s in stops], dtype=float)
    cols = np.asarray([s[1] for s in stops], dtype=float)
    t = np.clip(t, 0.0, 1.0)
    return np.stack([np.interp(t, pos, cols[:, i]) for i in range(3)], axis=-1)


def _fit_font(path, text, target_ink_h):
    """Return (font, bbox) sized so the glyph ink is exactly target_ink_h tall."""
    probe = 800
    f = ImageFont.truetype(path, probe)
    bb = f.getbbox(text)
    size = max(1, int(round(probe * target_ink_h / (bb[3] - bb[1]))))
    f = ImageFont.truetype(path, size)
    return f, f.getbbox(text)


def _bg_gradient(w, h, top, bottom):
    """A plain vertical two-stop gradient at any size (numpy, no banding)."""
    t = np.linspace(0.0, 1.0, h)[:, None]
    cols = np.stack([top[i] + (bottom[i] - top[i]) * t[:, 0] for i in range(3)], axis=-1)
    arr = np.repeat(cols[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def _squircle_mask(size):
    """Rounded-rect coverage mask, radius ~22.5% of the side (Apple squircle)."""
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=int(size * 0.2246), fill=255)
    return m


def _bg(size):
    """Navy vertical gradient inside a rounded squircle, with a cyan glow."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = _bg_gradient(size, size, NAVY_TOP, NAVY_BOTTOM)

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
    img.paste(grad, (0, 0), _squircle_mask(size))
    return img


# ------------------------------------------------------------------- mark
# The approved "B AIR" geometry. Expressed in the 1024 design space the rest
# of the family speaks, so the same numbers drive Android, iOS and the SVGs:
#   inset  = 24.5% of the canvas on every side  -> the ink box below
#   gap    = 8 design units of clear space between the Z and the M
#   stroke = 13 units
# A little extra air around the mark reads far better at launcher sizes than
# the tighter original, which looked cramped once the M met the Z.
MARK_INSET = 0.245
MARK_BOX_MIN, MARK_BOX_MAX = 0, 1024
MARK_GAP = 8.0
MARK_STROKE = 13.0
MARK_PEAK = 0.18  # how far the M's middle vertex drops below the baseline

# The inset box, in the 1024 design space: (x0, y0) -> (x1, y1).
_box = (MARK_BOX_MIN, MARK_BOX_MAX)
MARK_X0 = MARK_BOX_MIN + (MARK_BOX_MAX - MARK_BOX_MIN) * MARK_INSET
MARK_X1 = MARK_BOX_MAX - (MARK_BOX_MAX - MARK_BOX_MIN) * MARK_INSET
MARK_Y0 = MARK_X0
MARK_Y1 = MARK_X1


def _u(u, v, box):
    """Map mark-normalised units (0..100) onto a pixel box."""
    x0, y0, x1, y1 = box
    return (x0 + u / 100.0 * (x1 - x0), y0 + v / 100.0 * (y1 - y0))


def _mark_units(gap=None):
    """The mark as normalised 0..100 strokes: (start, end) in unit space."""
    g = MARK_GAP if gap is None else gap
    zl, zr = 4 + g / 2.0, 46 - g / 2.0
    ml, mr = 54 + g / 2.0, 96 - g / 2.0
    top, bot = 8.0, 92.0
    mid = (top + bot) / 2.0 + (bot - top) * MARK_PEAK
    return [
        ((zl, top), (zr, top)),      # Z top bar
        ((zr, top), (zl, bot)),      # Z diagonal
        ((zl, bot), (zr, bot)),      # Z bottom bar
        ((ml, bot), (ml, top)),      # M left stem
        ((ml, top), ((ml + mr) / 2.0, mid)),  # M peak
        (((ml + mr) / 2.0, mid), (mr, top)),  # M valley
        ((mr, top), (mr, bot)),      # M right stem
    ]


def _draw_mark(draw, size, scale=1.0, gap=None):
    """The interlocked Z + M, as thick rounded strokes.

    `scale` shrinks the whole mark (including its inset) inside `size`, so a
    scale of 1.0 fills the canvas at the approved B-AIR proportions.
    """
    inset = MARK_INSET * size
    box = (inset, inset, size - inset, size - inset)
    if scale != 1.0:
        cx = cy = size / 2.0
        box = tuple(cx + (v - cx) * scale if i % 2 == 0 else cy + (v - cy) * scale
                    for i, v in enumerate(box))
    w = MARK_STROKE / 100.0 * min(box[2] - box[0], box[3] - box[1])
    r = w / 2.0

    def seg(p, q):
        a, b = _u(*p, box), _u(*q, box)
        draw.line([a, b], fill=255, width=int(round(w)))
        for c in (a, b):
            draw.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255)

    for a, b in _mark_units(gap):
        seg(a, b)


def _mark_mask(size, scale=1.0, gap=None):
    """The mark as a plain coverage mask at `size`, ready to fill."""
    m = Image.new("L", (size, size), 0)
    _draw_mark(ImageDraw.Draw(m), size, scale, gap)
    return m


def _mark_extent(size, scale=1.0, gap=None):
    """Visual bounding box of the mark inside a `size` canvas."""
    return _mark_mask(size, scale, gap).getbbox()


def _mark_segments_1024(gap=None):
    """The mark as stroked centre-line segments in the 1024 design space,
    for the vector writers. Handy because Android/iOS SVGs want absolutes.
    """
    inset = 1024.0 * MARK_INSET
    box = (inset, inset, 1024 - inset, 1024 - inset)
    return [(_u(*a, box), _u(*b, box)) for a, b in _mark_units(gap)]


def _mark_stroke_1024():
    inset = 1024.0 * MARK_INSET
    side = 1024.0 - 2 * inset
    return MARK_STROKE / 100.0 * side


def _mark_extent_1024():
    return _mark_extent(1024, 1.0)


def _ink_ramp(size, extent=None, dy=INK_DY):
    """The cyan->blue ink, laid diagonally across the mark's own bounding box."""
    if extent is None:
        extent = (0, 0, size - 1, size - 1)
    x0, y0, x1, y1 = extent
    yy, xx = np.mgrid[0:size, 0:size]
    span = (x1 - x0) + (y1 - y0) * dy
    t = ((xx - x0) + (yy - y0) * dy) / max(1.0, span)
    rgb = _sample_ramp(INK_STOPS, t).astype(np.uint8)
    rgba = np.dstack([rgb, np.full((size, size), 255, np.uint8)])
    return Image.fromarray(rgba, "RGBA")


def _ink_layer(size, scale=1.0, gap=None):
    """The mark as a gradient-filled mask over transparency.

    Callers pass an already-supersampled size (`size * SS`), so this renders at
    exactly that resolution. Multiplying by SS here again used to blow a 1024
    icon up to a 16384px canvas and crash the iOS preview step.
    """
    mask = _mark_mask(size, scale, gap)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(_ink_ramp(size, mask.getbbox()), (0, 0), mask)
    return out


def icon(size, scale=1.0, transparent=False):
    S = size * SS
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0)) if transparent else _bg(S)
    base.alpha_composite(_ink_layer(S, scale))
    return base.resize((size, size), Image.LANCZOS)


def banner(w, h, wordmark="ZMyusic", tagline="YouTube Music, beautifully yours."):
    """Navy lockup: the mark on the left, name + bar + tagline on the right.

    The whole lockup is horizontally centred; every internal offset mirrors the
    original banner so the mark keeps its size and the text block its rhythm.
    """
    S_w = int(round(w * SS))
    S_h = int(round(h * SS))
    k = S_w / BANNER_W  # banner is designed at 1600x500, scale to any canvas

    bg = Image.new("RGBA", (S_w, S_h), (0, 0, 0, 0))
    bg.alpha_composite(_bg_gradient(S_w, S_h, NAVY_TOP, NAVY_BOTTOM))

    word_f, word_bb = _fit_font(WORDMARK_FONT, wordmark, WORDMARK_INK_H * k)
    tag_f, tag_bb = _fit_font(os.path.join(FONT_DIR, "sf_pro_display_regular.otf"),
                              tagline, TAGLINE_INK_H * k)
    word_w = word_bb[2] - word_bb[0]
    tag_w = tag_bb[2] - tag_bb[0]
    text_w = max(TEXT_INDENT * k + word_w, BAR_OFFSET_X * k + BAR_W * k,
                 TAGLINE_OFFSET_X * k + tag_w)
    mark_w = MARK_REF_W * k
    group_w = mark_w + TEXT_SPACING * k + text_w
    mark_x = (S_w - group_w) / 2.0
    text_x = mark_x + mark_w + TEXT_SPACING * k

    # cyan glow behind the mark
    glow = Image.new("L", (S_w, S_h), 0)
    gd = ImageDraw.Draw(glow)
    cx, cy, r = mark_x + mark_w / 2.0, S_h * 0.5, S_h * 0.95
    for i in range(48, 0, -1):
        t = i / 48
        rr = r * t
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=int(78 * (1 - t) ** 1.4))
    g_rgb = Image.new("RGBA", (S_w, S_h), CYAN + (0,))
    g_rgb.putalpha(glow)
    bg.alpha_composite(g_rgb)

    # the mark, scaled so its ink is exactly MARK_REF_W wide. The mask has to
    # be drawn on a canvas big enough for that target; drawing it at 1024 with
    # scale > 1 clipped the rounded caps off every edge.
    full = _mark_extent(1024, 1.0)
    target = MARK_REF_W * k
    m_size = int(round(1024 * target / (full[2] - full[0])))
    mask = _mark_mask(m_size, 1.0)
    mbb = mask.getbbox()
    ink = Image.new("RGBA", (m_size, m_size), (0, 0, 0, 0))
    ink.paste(_ink_ramp(m_size, mbb), (0, 0), mask)
    bg.alpha_composite(ink, (int(round(mark_x - mbb[0])),
                             int(round(MARK_CENTER_Y * k - (mbb[3] - mbb[1]) / 2.0 - mbb[1]))))

    d = ImageDraw.Draw(bg)
    word_top = WORDMARK_TOP * k
    d.text((text_x + TEXT_INDENT * k - word_bb[0], word_top - word_bb[1]),
           wordmark, font=word_f, fill=(255, 255, 255, 255))

    bar_x = text_x + BAR_OFFSET_X * k
    bar_y = word_top + BAR_OFFSET_Y * k
    d.rounded_rectangle([bar_x, bar_y, bar_x + BAR_W * k, bar_y + BAR_H * k],
                        radius=BAR_H * k / 2.0, fill=CYAN + (255,))

    d.text((text_x + TAGLINE_OFFSET_X * k - tag_bb[0],
            word_top + TAGLINE_OFFSET_Y * k - tag_bb[1]),
           tagline, font=tag_f, fill=TAGLINE + (255,))

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
