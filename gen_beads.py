"""Generate placeholder bead PNGs from crystal/accessory/rope color data.

Each PNG is 200x200, round, with a radial gradient from glow → color,
a soft white highlight, transparent background. Filename = id.png.

The list below is kept in sync with index.html's CRYSTALS / ACCESSORIES / ROPES.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "image")
os.makedirs(OUT, exist_ok=True)

SIZE = 200          # output size (px)
PAD = 6             # transparent margin so glow doesn't get clipped
R = SIZE // 2 - PAD # bead radius
CX, CY = SIZE // 2, SIZE // 2


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render_bead(color_hex, glow_hex):
    """Radial gradient round bead with highlight."""
    color = hex2rgb(color_hex)
    glow = hex2rgb(glow_hex)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    px = img.load()
    # Highlight offset (toward upper-left)
    hx, hy = CX - R * 0.30, CY - R * 0.35
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x - CX, y - CY
            d = math.hypot(dx, dy)
            if d > R + 1:
                continue
            # Outside the circle, fade to transparent over 1px (anti-alias)
            if d > R:
                alpha = int(255 * (R + 1 - d))
            else:
                alpha = 255
            # Distance to highlight center, normalized 0..1 within radius
            hd = math.hypot(x - hx, y - hy) / (R * 1.15)
            hd = max(0.0, min(1.0, hd))
            # Smoothstep
            t = hd * hd * (3 - 2 * hd)
            base = mix(glow, color, t)
            # White spec on top
            spec = math.hypot(x - (CX - R * 0.32), y - (CY - R * 0.40)) / (R * 0.32)
            if spec < 1.0:
                k = (1 - spec) ** 2 * 0.55
                base = (
                    int(base[0] + (255 - base[0]) * k),
                    int(base[1] + (255 - base[1]) * k),
                    int(base[2] + (255 - base[2]) * k),
                )
            # Edge darkening for 3D
            edge = d / R
            if edge > 0.85:
                k = ((edge - 0.85) / 0.15) ** 2 * 0.55
                base = (
                    int(base[0] * (1 - k)),
                    int(base[1] * (1 - k)),
                    int(base[2] * (1 - k)),
                )
            px[x, y] = (base[0], base[1], base[2], alpha)
    return img


def render_rope(color_hex, glow_hex):
    """Same as bead but with a faint inner ring to evoke a cord."""
    img = render_bead(color_hex, glow_hex)
    draw = ImageDraw.Draw(img)
    ring = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(ring)
    d2.ellipse(
        [CX - R * 0.65, CY - R * 0.65, CX + R * 0.65, CY + R * 0.65],
        outline=(255, 255, 255, 110),
        width=3,
    )
    img.alpha_composite(ring)
    return img


def render_auto():
    """Rainbow conic for the 'auto' rope (随主调)."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    px = img.load()
    stops = [
        (0.0, hex2rgb("#e8d99a")),
        (0.20, hex2rgb("#6bd984")),
        (0.40, hex2rgb("#5db9e8")),
        (0.60, hex2rgb("#ff7d7d")),
        (0.80, hex2rgb("#d4a76a")),
        (1.0, hex2rgb("#e8d99a")),
    ]
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x - CX, y - CY
            d = math.hypot(dx, dy)
            if d > R + 1:
                continue
            alpha = 255 if d <= R else int(255 * (R + 1 - d))
            # Angle 0..1 starting from top, clockwise
            ang = (math.atan2(dy, dx) + math.pi / 2) / (2 * math.pi)
            if ang < 0:
                ang += 1
            # Find segment
            for i in range(len(stops) - 1):
                a0, c0 = stops[i]
                a1, c1 = stops[i + 1]
                if a0 <= ang <= a1:
                    t = (ang - a0) / (a1 - a0)
                    col = mix(c0, c1, t)
                    break
            else:
                col = stops[-1][1]
            # Inward darkening near center for orb depth
            d_norm = d / R
            shade = 0.85 + 0.15 * (1 - d_norm)
            col = (int(col[0] * shade), int(col[1] * shade), int(col[2] * shade))
            px[x, y] = (col[0], col[1], col[2], alpha)
    return img


# ============ Catalog (sync with index.html) ============

CRYSTALS = [
    # 金
    ("clear",         "#e8e8ff", "#ffffff"),
    ("pearl",         "#fff5e8", "#ffffff"),
    ("moonstone",     "#c8d8ff", "#e0ecff"),
    ("tridacna",      "#f5f0e8", "#ffffff"),
    ("goldhair",      "#d4a548", "#f5d168"),
    ("white-phantom", "#dcdce8", "#ffffff"),
    ("silver-rutile", "#b8b8c8", "#e0e0e8"),
    ("titanium",      "#c4a040", "#e8c880"),
    ("opal",          "#d8e8e8", "#fff5e8"),
    # 木
    ("green",         "#3fa66a", "#5fd48c"),
    ("jade",          "#2d8f4d", "#6fd285"),
    ("peridot",       "#9ac74e", "#c0e078"),
    ("aventurine",    "#6fb578", "#a4dba8"),
    ("turquoise",     "#3ec5b8", "#80e0d4"),
    ("green-rutile",  "#3a8855", "#5fc080"),
    ("malachite",     "#1a7548", "#3aa570"),
    ("garden",        "#6a9f6a", "#9ccc9c"),
    ("prehnite",      "#b8d090", "#d8e8b0"),
    ("fluorite",      "#9ad885", "#c0ec98"),
    ("tsavorite",     "#00ad6c", "#4adb8e"),
    ("moldavite",     "#3a6a48", "#7aa080"),
    # 水
    ("obsidian",      "#2a2438", "#5a4d75"),
    ("aqua",          "#5fc8d8", "#8ce0ec"),
    ("lapis",         "#1d3a8a", "#4a78c0"),
    ("kyanite",       "#3a78c8", "#7aa8e0"),
    ("labradorite",   "#4a6080", "#8aa0c0"),
    ("blue-lace",     "#85b8d8", "#b0d4e8"),
    ("black-rutile",  "#1a1428", "#4a3858"),
    ("black-tour",    "#0a0a18", "#3a3050"),
    ("larimar",       "#6ec5d0", "#a0e0e8"),
    ("amazonite",     "#5fbfbe", "#8ad8d4"),
    ("hawkeye",       "#2a4a78", "#5070a8"),
    ("blue-needle",   "#4a8ed0", "#80b8e8"),
    # 火
    ("amethyst",      "#9d5cd9", "#b87aff"),
    ("rose",          "#ff9bb8", "#ffb6cd"),
    ("agate",         "#c43a3a", "#e85d5d"),
    ("strawberry",    "#e57aa0", "#ffadc8"),
    ("garnet",        "#8a1538", "#c83555"),
    ("ametrine",      "#b878d0", "#e8b070"),
    ("rhodonite",     "#e07a8a", "#ffb0c0"),
    ("nanhong",       "#a01818", "#d04040"),
    ("charoite",      "#8a5cb0", "#b890dc"),
    ("sugilite",      "#7848a0", "#a878c8"),
    ("morganite",     "#f4b8c4", "#ffd0d8"),
    ("red-rutile",    "#b02838", "#d04050"),
    ("red-rabbit",    "#c25068", "#e07088"),
    ("lepidolite",    "#a07ec0", "#c0a0d8"),
    ("purple-rutile", "#7050a0", "#9070c0"),
    ("sakura",        "#f0d0d8", "#ffe8ec"),
    # 土
    ("citrine",       "#ffc94d", "#ffdb70"),
    ("smoky",         "#6b4a3a", "#8c6553"),
    ("tiger",         "#b67926", "#d99847"),
    ("amber",         "#e8a040", "#ffc870"),
    ("sunstone",      "#e87530", "#ffaa55"),
    ("yellow-rutile", "#d4a040", "#f0c870"),
    ("yellow-tiger",  "#c89030", "#e8b860"),
    ("topaz",         "#e8c060", "#ffd890"),
    ("yellow-chalcedony","#e8b850","#ffd078"),
    ("spessartine",   "#e87530", "#ffa050"),
]

ACCESSORIES = [
    ("pearl-disc",     "#f0e8ee", "#ffffff"),
    ("silver-lotus",   "#c8c8d8", "#ffffff"),
    ("silver-pixiu",   "#a8a8b8", "#e0e0e8"),
    ("small-bell",     "#d4a52e", "#f5d168"),
    ("jade-peace",     "#3fa66a", "#5fd48c"),
    ("bodhi",          "#c89060", "#e8b890"),
    ("coconut-disc",   "#6a4030", "#8a6048"),
    ("green-tower",    "#2d8f4d", "#5fd485"),
    ("obsidian-pixiu", "#2a2438", "#5a4d75"),
    ("lapis-bead",     "#1d3a8a", "#4a78c0"),
    ("kyanite-spacer", "#3a78c8", "#7aa8e0"),
    ("labra-pendant",  "#4a6080", "#8aa0c0"),
    ("lucky-bead",     "#c83a4c", "#ff6080"),
    ("nanhong-lotus",  "#a02830", "#d04050"),
    ("rose-heart",     "#ff9bb8", "#ffb6cd"),
    ("cinnabar",       "#c41818", "#e84040"),
    ("gold-peach",     "#e8a833", "#ffc94d"),
    ("amber-bead",     "#d4a060", "#f0c890"),
    ("tiger-pixiu",    "#b67926", "#d99847"),
    ("ruyi",           "#c8a040", "#e0c060"),
]

ROPES = [
    # auto handled separately
    ("silver",      "#a8a8b8", "#d8d8e0"),
    ("gold",        "#d4a52e", "#f5d168"),
    ("white-jade",  "#e8e8f0", "#ffffff"),
    ("dark-green",  "#1a5a3a", "#3a8055"),
    ("light-green", "#7ac478", "#a8e0a0"),
    ("linen",       "#b8a878", "#d4c498"),
    ("black",       "#3a3448", "#5a5468"),
    ("navy",        "#1a2858", "#3a5588"),
    ("lake-blue",   "#5fa8d0", "#8ad0e8"),
    ("red",         "#c8344c", "#e85068"),
    ("pink",        "#ff8aa8", "#ffb6cd"),
    ("purple",      "#8050d8", "#b080f0"),
    ("yellow",      "#e8c040", "#ffd870"),
    ("brown",       "#7a4a28", "#a06848"),
    ("camel",       "#c8a070", "#e8c4a0"),
]


def save(name, img):
    img.save(os.path.join(OUT, f"{name}.png"), "PNG", optimize=True)


def main():
    total = 0
    for name, color, glow in CRYSTALS:
        save(name, render_bead(color, glow))
        total += 1
    for name, color, glow in ACCESSORIES:
        save(name, render_bead(color, glow))
        total += 1
    save("auto", render_auto())
    total += 1
    for name, color, glow in ROPES:
        save(name, render_rope(color, glow))
        total += 1
    print(f"Generated {total} bead PNGs into {OUT}")


if __name__ == "__main__":
    main()
