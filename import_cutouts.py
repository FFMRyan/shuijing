"""Import pre-cropped bead photos from crystal_cutouts_named/ into image/.

Each cutout is a JPG named by its Chinese crystal name. We map Chinese name →
code id (used by index.html) and copy as image/{id}.png with a circular alpha
mask + 200×200 resize. Crystals with no matching code id are skipped.

If a name appears in multiple source folders, the FIRST one (per CSV order) wins
— main infographics (494362/499426/503774) take precedence over the themed
tables (507086/510224).
"""

import csv
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(__file__)
SRC  = os.path.join(ROOT, "crystal_cutouts_named")
OUT  = os.path.join(ROOT, "image")
CSV_PATH = os.path.join(SRC, "命名对应表.csv")
OUT_SIZE = 200

# Chinese name → code id (None means skip — no matching crystal in index.html)
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
    # 水/黑/土
    "茶晶":      "smoky",
    "黑发晶":    "black-rutile",
    "虎眼石":    "tiger",
    "虎睛石":    "tiger",            # alias
    "黑曜石":    "obsidian",
    "黑碧玺":    "black-tour",
    # 火
    "朱砂":      "cinnabar",         # accessory
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
    # 土 yellow series
    "黄水晶":    "citrine",
    "黄玉髓":    "yellow-chalcedony",
    "蜜蜡":      "amber",
    "金发晶":    "goldhair",
    "钛晶":      "titanium",
    # 水/blue series
    "托帕石":    "topaz",
    "海蓝宝":    "aqua",
    "蓝海宝":    "aqua",              # alias
    "蓝针水晶":  "blue-needle",
    "蓝针":      "blue-needle",        # alias
    "海纹石":    "larimar",
    "天河石":    "amazonite",
    "绿松石":    "turquoise",
    "拉长石":    "labradorite",
    "鹰眼石":    "hawkeye",
    "蓝纹石":    "blue-lace",
    "蓝晶石":    "kyanite",
    "青金石":    "lapis",
    # purple
    "紫龙晶":    "charoite",
    "紫水晶":    "amethyst",
    "舒俱来":    "sugilite",
    "紫云母":    "lepidolite",
    "紫发晶":    "purple-rutile",
    # 新增 26 种 (扩展水晶库)
    "岫玉":          "xiu-jade",
    "猫眼石":        "cats-eye",
    "绿玉髓":        "chrysoprase",
    "凤凰石":        "phoenix-stone",
    "坦桑石":        "tanzanite",
    "墨玉":          "ink-jade",
    "天铁陨石":      "tibetan-tektite",
    "帕拉伊巴":      "paraiba",
    "彼得石":        "pietersite",
    "磷灰石":        "apatite",
    "蓝玉髓":        "blue-chalcedony",
    "蓝砂石":        "blue-sandstone",
    "金曜石":        "gold-obsidian",
    "尖晶石":        "spinel",
    "星光芙蓉":      "star-rose",
    "极光23":        "aurora-23",
    "蔷薇石":        "rose-stone",
    "碧玺":          "tourmaline-mix",
    "紫幽灵":        "purple-phantom",
    "紫发超七":      "purple-super-seven",
    "超七水晶":      "super-seven",
    "红绿宝":        "ruby-zoisite",
    "红胶花":        "red-glue-flower",
    "锂辉石":        "kunzite",
    "日光石":        "sunlight-stone",
    "琥珀":          "succinite",
}


def round_resize(im, out_size=OUT_SIZE):
    """Resize to square + apply circular alpha mask."""
    # First make it square by center-cropping
    w, h = im.size
    s = min(w, h)
    left = (w - s) // 2
    top  = (h - s) // 2
    im = im.crop((left, top, left + s, top + s)).convert("RGBA")
    im = im.resize((out_size, out_size), Image.LANCZOS)
    mask = Image.new("L", (out_size, out_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, out_size, out_size), fill=255)
    out = Image.new("RGBA", (out_size, out_size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def main():
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f"CSV not found: {CSV_PATH}")
    os.makedirs(OUT, exist_ok=True)

    rows = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    written = {}        # id → source_path (first wins)
    skipped_no_id = []  # cn names with no code id
    missing_file = []   # csv references file that doesn't exist

    for r in rows:
        cn   = r["crystal_name"].strip()
        rel  = r["output_file"].strip()
        path = os.path.join(SRC, rel)

        cid = NAME_TO_ID.get(cn)
        if cid is None:
            skipped_no_id.append(cn)
            continue
        if cid in written:
            continue                   # first occurrence wins
        if not os.path.exists(path):
            missing_file.append(rel)
            continue

        try:
            im = Image.open(path)
            out = round_resize(im)
            out.save(os.path.join(OUT, f"{cid}.png"), "PNG", optimize=True)
            written[cid] = rel
        except Exception as e:
            print(f"  ERROR {rel}: {e}")

    print(f"\nWrote {len(written)} bead images to {OUT}")
    print(f"  Skipped (no code id mapping): {len(set(skipped_no_id))} unique names")
    if missing_file:
        print(f"  Missing source files: {len(missing_file)}")
    # Print summary of what's covered
    if written:
        print("\nCovered code ids:")
        for cid in sorted(written):
            print(f"  {cid}  ← {written[cid]}")


if __name__ == "__main__":
    main()
