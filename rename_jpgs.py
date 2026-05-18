"""Rename the 93 Chinese-named JPGs in image/ to English-id PNGs.

For each `image/{中文名}.jpg`:
  1. Strip any `_rXX_cYY` suffix to get the bare Chinese name
  2. Look up English code id via NAME_TO_ID
  3. Convert to 200×200 RGBA PNG with circular alpha mask
  4. Save as `image/{code_id}.png` (overwrites existing — content is the same photo)
  5. Delete the Chinese JPG

The 5 large `image-1778850*.jpg` source files are deleted at the end (they
belong in souces/, not image/).
"""

import os
import re
from PIL import Image, ImageDraw

IMG_DIR = os.path.join(os.path.dirname(__file__), "image")
OUT_SIZE = 200

NAME_TO_ID = {
    # 金
    "白水晶":    "clear",
    "白幽灵":    "white-phantom",
    "月光石":    "moonstone",
    "樱花玛瑙":  "sakura",
    "东陵玉":    "aventurine",
    "欧泊":      "opal",
    # 木
    "葡萄石":    "prehnite",
    "绿橄榄":    "peridot",
    "孔雀石":    "malachite",
    "绿幽灵":    "green",
    "沙弗莱":    "tsavorite",
    "萤石":      "fluorite",
    "捷克陨石":  "moldavite",
    "岫玉":      "xiu-jade",
    "猫眼石":    "cats-eye",
    "绿玉髓":    "chrysoprase",
    # 水
    "茶晶":      "smoky",
    "黑发晶":    "black-rutile",
    "虎眼石":    "tiger",
    "虎睛石":    "tiger",
    "黑曜石":    "obsidian",
    "黑碧玺":    "black-tour",
    "凤凰石":    "phoenix-stone",
    "坦桑石":    "tanzanite",
    "墨玉":      "ink-jade",
    "天铁陨石":  "tibetan-tektite",
    "帕拉伊巴":  "paraiba",
    "彼得石":    "pietersite",
    "磷灰石":    "apatite",
    "蓝玉髓":    "blue-chalcedony",
    "蓝砂石":    "blue-sandstone",
    "金曜石":    "gold-obsidian",
    # 火
    "朱砂":      "cinnabar",
    "南红":      "nanhong",
    "石榴石":    "garnet",
    "玛瑙":      "agate",
    "红兔毛":    "red-rabbit",
    "红发晶":    "red-rutile",
    "红纹石":    "rhodonite",
    "草莓晶":    "strawberry",
    "粉水晶":    "rose",
    "摩根石":    "morganite",
    "太阳石":    "sunstone",
    "芬达石":    "spessartine",
    "尖晶石":    "spinel",
    "星光芙蓉":  "star-rose",
    "极光23":    "aurora-23",
    "蔷薇石":    "rose-stone",
    "碧玺":      "tourmaline-mix",
    "紫幽灵":    "purple-phantom",
    "紫发超七":  "purple-super-seven",
    "超七水晶":  "super-seven",
    "红绿宝":    "ruby-zoisite",
    "红胶花":    "red-glue-flower",
    "锂辉石":    "kunzite",
    # 土
    "黄水晶":    "citrine",
    "黄玉髓":    "yellow-chalcedony",
    "蜜蜡":      "amber",
    "金发晶":    "goldhair",
    "钛晶":      "titanium",
    "日光石":    "sunlight-stone",
    "琥珀":      "succinite",
    # blue (water)
    "托帕石":    "topaz",
    "海蓝宝":    "aqua",
    "蓝海宝":    "aqua",
    "蓝针水晶":  "blue-needle",
    "蓝针":      "blue-needle",
    "海纹石":    "larimar",
    "天河石":    "amazonite",
    "绿松石":    "turquoise",
    "拉长石":    "labradorite",
    "鹰眼石":    "hawkeye",
    "蓝纹石":    "blue-lace",
    "蓝晶石":    "kyanite",
    "青金石":    "lapis",
    # purple (fire)
    "紫龙晶":    "charoite",
    "紫水晶":    "amethyst",
    "舒俱来":    "sugilite",
    "紫云母":    "lepidolite",
    "紫发晶":    "purple-rutile",
}


def round_resize(im, out_size=OUT_SIZE):
    w, h = im.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    im = im.crop((left, top, left + s, top + s)).convert("RGBA")
    im = im.resize((out_size, out_size), Image.LANCZOS)
    mask = Image.new("L", (out_size, out_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, out_size, out_size), fill=255)
    out = Image.new("RGBA", (out_size, out_size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def parse_name(fname):
    base = os.path.splitext(fname)[0]                  # strip .jpg
    base = re.sub(r"_r\d+_c\d+$", "", base)            # strip _r02_c04 suffix
    return base


def main():
    if not os.path.isdir(IMG_DIR):
        raise SystemExit(IMG_DIR + " not found")

    converted = {}     # id → src filename
    duplicates = []    # later occurrences (skipped)
    unmapped = []      # chinese name with no code id
    source_jpgs = []   # the 1242× full sources

    for fname in sorted(os.listdir(IMG_DIR)):
        if not fname.lower().endswith(".jpg"):
            continue
        src = os.path.join(IMG_DIR, fname)

        # Full-size source jpgs like image-1778850494362.jpg
        if fname.startswith("image-"):
            source_jpgs.append(fname)
            os.remove(src)
            continue

        cn = parse_name(fname)
        cid = NAME_TO_ID.get(cn)
        if not cid:
            unmapped.append(fname)
            continue
        if cid in converted:
            duplicates.append(fname)
            os.remove(src)
            continue

        try:
            im = Image.open(src)
            round_resize(im).save(
                os.path.join(IMG_DIR, f"{cid}.png"), "PNG", optimize=True
            )
            os.remove(src)
            converted[cid] = fname
        except Exception as e:
            print(f"  ERROR {fname}: {e}")

    print(f"Converted {len(converted)} JPGs → English-id PNGs")
    print(f"Deleted {len(duplicates)} duplicates")
    print(f"Deleted {len(source_jpgs)} full-size source JPGs")
    if unmapped:
        print(f"\nUnmapped (left in place — add to NAME_TO_ID to import):")
        for u in unmapped:
            print(f"  {u}")


if __name__ == "__main__":
    main()
