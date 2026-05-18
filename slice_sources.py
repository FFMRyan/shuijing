"""Slice individual crystal beads from the three souces/ infographic JPGs.

Each source is 1242x1660 with a 4x6 grid of bead photos.
We crop each cell's bead (top-center round area), apply a circular mask,
resize to 200x200 RGBA PNG, and save as image/{code_id}.png.

Cells whose Chinese name has no matching code ID are skipped (their previous
generated PNG placeholders remain in image/).
"""

import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(__file__)
SRC  = os.path.join(ROOT, "souces")
OUT  = os.path.join(ROOT, "image")
os.makedirs(OUT, exist_ok=True)

# ------------- Grid calibration (per source image) -------------
# Measured from vertical/horizontal strip samples on the 1242×1660 sources.
COL_X      = [110, 305, 500, 685, 880, 1095]       # x-centers of 6 columns
ROW_Y      = [355, 720, 1080, 1440]                # y-centers of 4 rows (centered on bead, not bead+label area)
BEAD_RADIUS = 75                                    # tight crop, no label bleed
OUT_SIZE   = 200                                    # output PNG size

# ------------- Cell label → code id mapping per source -------------
# Entries with id=None are skipped (no matching id in our CRYSTALS data).
IMG1_FILE = "image-1778850494362.jpg"               # light / silver / green / dark
IMG1 = [
    [("白水晶","clear"),    ("白幽灵","white-phantom"), ("月光石","moonstone"),  ("樱花玛瑙","sakura"),  ("东陵玉","aventurine"), ("欧泊","opal")],
    [("葡萄石","prehnite"), ("绿橄榄","peridot"),       ("岫玉",None),           ("孔雀石","malachite"), ("绿幽灵","green"),       ("帕拉伊巴",None)],
    [("沙弗莱","tsavorite"),("猫眼石",None),            ("萤石","fluorite"),     ("绿玉髓",None),        ("捷克陨石","moldavite"), ("茶晶","smoky")],
    [("黑发晶","black-rutile"),("天铁陨石",None),       ("虎眼石","tiger"),      ("黑曜石","obsidian"),  ("黑碧玺","black-tour"),  ("墨玉",None)],
]

IMG2_FILE = "image-1778850499426.jpg"               # red / pink / orange / yellow
IMG2 = [
    [("朱砂","cinnabar"),    ("南红","nanhong"),          ("石榴石","garnet"),       ("极光23",None),        ("玛瑙","agate"),         ("红兔毛","red-rabbit")],
    [("红发晶","red-rutile"),("碧玺",None),               ("蔷薇石",None),           ("红纹石","rhodonite"), ("尖晶石",None),          ("草莓晶","strawberry")],
    [("粉水晶","rose"),      ("摩根石","morganite"),      ("星光芙蓉",None),         ("日光石",None),        ("太阳石","sunstone"),    ("芬达石","spessartine")],
    [("黄水晶","citrine"),   ("黄玉髓","yellow-chalcedony"),("蜜蜡","amber"),         ("金发晶","goldhair"),  ("琥珀",None),            ("钛晶","titanium")],
]

IMG3_FILE = "image-1778850503774.jpg"               # blue / purple
IMG3 = [
    [("托帕石","topaz"),     ("海蓝宝","aqua"),           ("蓝针水晶","blue-needle"),("海纹石","larimar"),   ("蓝玉髓",None),          ("磷灰石",None)],
    [("天河石","amazonite"), ("凤凰石",None),             ("绿松石","turquoise"),    ("拉长石","labradorite"),("彼得石",None),         ("蓝砂石",None)],
    [("鹰眼石","hawkeye"),   ("蓝纹石","blue-lace"),      ("蓝晶石","kyanite"),      ("青金石","lapis"),     ("坦桑石",None),          ("紫龙晶","charoite")],
    [("紫水晶","amethyst"),  ("红绿宝",None),             ("舒俱来","sugilite"),     ("紫云母","lepidolite"),("紫发晶","purple-rutile"),("锂辉石",None)],
]

SOURCES = [(IMG1_FILE, IMG1), (IMG2_FILE, IMG2), (IMG3_FILE, IMG3)]


def round_crop(im, cx, cy, r, out_size):
    box = (cx - r, cy - r, cx + r, cy + r)
    bead = im.crop(box).convert("RGBA").resize((out_size, out_size), Image.LANCZOS)
    mask = Image.new("L", (out_size, out_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, out_size, out_size), fill=255)
    out = Image.new("RGBA", (out_size, out_size), (0, 0, 0, 0))
    out.paste(bead, (0, 0), mask)
    return out


def main():
    saved = 0
    skipped = 0
    for fname, grid in SOURCES:
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            print(f"SKIP source missing: {path}")
            continue
        im = Image.open(path).convert("RGB")
        for r, row in enumerate(grid):
            for c, (cn, cid) in enumerate(row):
                if not cid:
                    skipped += 1
                    continue
                cx, cy = COL_X[c], ROW_Y[r]
                bead = round_crop(im, cx, cy, BEAD_RADIUS, OUT_SIZE)
                bead.save(os.path.join(OUT, f"{cid}.png"), "PNG", optimize=True)
                print(f"  {fname} [{r}][{c}] {cn} → {cid}.png")
                saved += 1
    print(f"\nSaved {saved}, skipped {skipped} (no code id)")


if __name__ == "__main__":
    main()
