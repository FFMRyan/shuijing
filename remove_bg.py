"""Remove the light/white background from image/index-tg.png.

Strategy:
  1. Backup original to image/index-tg-original.png (skip if exists).
  2. Convert to RGBA.
  3. Flood-fill from each of the four corners with a Manhattan tolerance
     that catches the light backdrop without eating into the wood / beads.
  4. Soft-feather the resulting alpha edge so the cutout sits nicely on
     the dark hero background instead of having harsh aliasing.
  5. Save back to image/index-tg.png.
"""

from PIL import Image, ImageDraw, ImageFilter
import os
import shutil

SRC = 'image/index-tg.png'
BAK = 'image/index-tg-original.png'
THRESH = 55  # Manhattan distance from seed pixel — tuned for soft white backdrop with shadows

def main():
    if not os.path.exists(SRC):
        print(f'missing {SRC}')
        return
    if not os.path.exists(BAK):
        shutil.copy2(SRC, BAK)
        print(f'backed up → {BAK}')

    img = Image.open(SRC).convert('RGBA')
    w, h = img.size

    for corner in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(img, corner, (0, 0, 0, 0), thresh=THRESH)

    # Also try a few mid-edge seeds in case the backdrop colour varies across the photo
    for x in (w // 4, w // 2, 3 * w // 4):
        for y in (0, h - 1):
            px = img.getpixel((x, y))
            if px[3] != 0:
                ImageDraw.floodfill(img, (x, y), (0, 0, 0, 0), thresh=THRESH)
    for y in (h // 4, h // 2, 3 * h // 4):
        for x in (0, w - 1):
            px = img.getpixel((x, y))
            if px[3] != 0:
                ImageDraw.floodfill(img, (x, y), (0, 0, 0, 0), thresh=THRESH)

    # Soft-feather: blur the alpha channel slightly, then re-merge
    r, g, b, a = img.split()
    a_blur = a.filter(ImageFilter.GaussianBlur(radius=1.2))
    img = Image.merge('RGBA', (r, g, b, a_blur))

    img.save(SRC)
    print(f'done → {SRC}  ({w}×{h})')

if __name__ == '__main__':
    main()
