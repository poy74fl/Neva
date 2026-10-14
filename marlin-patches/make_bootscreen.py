#!/usr/bin/env python3
"""Genere marlin-patches/Marlin/_Bootscreen.h (ecran de demarrage 128x64).

  python3 make_bootscreen.py                 -> logo "FAKE PRUSA PRO HT00" avec la machine (blague)
  python3 make_bootscreen.py --texte         -> meme logo, texte seul
  python3 make_bootscreen.py --neva          -> logo "DAGOMA NEVA" (petite delta)
  python3 make_bootscreen.py mon_logo.png    -> convertit ton image (noir/blanc, 128x64)

Un pixel allume (blanc dans l'image) = un pixel allume sur l'ecran.
Ecrit aussi docs/bootscreen_apercu.png (apercu agrandi).
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 128, 64
ROOT = Path(__file__).resolve().parent
OUT_H = ROOT / "Marlin" / "_Bootscreen.h"
OUT_PNG = ROOT.parent / "docs" / "bootscreen_apercu.png"
FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
]


def font(size):
    for f in FONTS:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    try:
        import matplotlib
        p = Path(matplotlib.__file__).parent / "mpl-data/fonts/ttf/DejaVuSans-Bold.ttf"
        return ImageFont.truetype(str(p), size)
    except Exception:
        return ImageFont.load_default()


def default_logo():
    im = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(im)
    # petite imprimante delta : 3 tours, plateau, effecteur et bras
    cx = 26
    for x in (cx - 18, cx, cx + 18):                 # tours
        d.line([(x, 8), (x, 46)], fill=1, width=2)
    d.line([(cx - 20, 8), (cx + 20, 8)], fill=1, width=1)   # haut
    d.rectangle([cx - 24, 47, cx + 24, 50], fill=1)         # plateau
    d.polygon([(cx - 5, 31), (cx + 5, 31), (cx, 37)], fill=1)  # effecteur + buse
    for x in (cx - 18, cx, cx + 18):                 # bras
        d.line([(x, 20), (cx, 31)], fill=1, width=1)
    for x in (cx - 18, cx, cx + 18):                 # chariots
        d.rectangle([x - 2, 18, x + 2, 22], fill=1)
    # textes
    x0, avail = 54, W - 54 - 2
    for txt, top, size in (("DAGOMA", 8, 16), ("NEVA", 28, 26)):
        while size > 6 and d.textlength(txt, font=font(size)) > avail:
            size -= 1
        d.text((x0, top), txt, font=font(size), fill=1)
    d.line([(x0, 58), (W - 3, 58)], fill=1, width=1)
    return im


def centered(d, txt, top, size, avail=W - 8):
    while size > 5 and d.textlength(txt, font=font(size)) > avail:
        size -= 1
    w = d.textlength(txt, font=font(size))
    d.text(((W - w) / 2, top), txt, font=font(size), fill=1)


def prusa_logo():
    im = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(im)
    centered(d, "FAKE", 1, 13)
    centered(d, "PRUSA", 14, 27)
    d.rounded_rectangle([14, 45, W - 15, 62], radius=4, outline=1, width=2)
    centered(d, "PRO HT00", 47, 13, avail=W - 40)
    return im


def draw_machine(d, ox, oy):
    """Imprimante delta vue de face (56 x 62 px), dessinee a partir du coin (ox, oy)."""
    def X(x): return ox + x
    def Y(y): return oy + y
    # base et plateau
    d.rectangle([X(1), Y(55), X(55), Y(61)], fill=1)
    d.rectangle([X(8), Y(48), X(48), Y(51)], fill=1)
    d.rectangle([X(23), Y(43), X(33), Y(47)], fill=1)          # piece imprimee
    # tours (arriere plus fine) et plaque du haut
    d.line([(X(5), Y(5)), (X(5), Y(55))], fill=1, width=3)
    d.line([(X(51), Y(5)), (X(51), Y(55))], fill=1, width=3)
    d.line([(X(28), Y(7)), (X(28), Y(48))], fill=1, width=1)
    d.rectangle([X(2), Y(2), X(54), Y(6)], fill=1)
    # chariots
    d.rectangle([X(3), Y(15), X(7), Y(21)], fill=0)
    d.rectangle([X(3), Y(16), X(7), Y(20)], outline=1)
    d.rectangle([X(49), Y(15), X(53), Y(21)], fill=0)
    d.rectangle([X(49), Y(16), X(53), Y(20)], outline=1)
    d.rectangle([X(26), Y(10), X(30), Y(14)], fill=1)
    # bras
    d.line([(X(7), Y(18)), (X(23), Y(35))], fill=1, width=1)
    d.line([(X(49), Y(18)), (X(33), Y(35))], fill=1, width=1)
    d.line([(X(28), Y(14)), (X(28), Y(34))], fill=1, width=1)
    # effecteur + buse
    d.rectangle([X(22), Y(34), X(34), Y(38)], fill=1)
    d.polygon([(X(25), Y(39)), (X(31), Y(39)), (X(28), Y(43))], fill=1)


def prusa_machine_logo():
    im = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(im)
    draw_machine(d, 2, 1)
    x0, avail = 62, W - 62 - 2
    def txt(t, top, size):
        while size > 5 and d.textlength(t, font=font(size)) > avail:
            size -= 1
        d.text((x0, top), t, font=font(size), fill=1)
    txt("FAKE", 1, 13)
    txt("PRUSA", 14, 20)
    d.rounded_rectangle([x0, 42, W - 3, 58], radius=3, outline=1, width=2)
    t = "PRO HT00"
    size = 11
    while size > 5 and d.textlength(t, font=font(size)) > avail - 8:
        size -= 1
    w = d.textlength(t, font=font(size))
    d.text((x0 + (avail - w) / 2, 43), t, font=font(size), fill=1)
    return im


def from_image(path):
    im = Image.open(path).convert("L")
    im = ImageOps.contain(im, (W, H))
    canvas = Image.new("L", (W, H), 0)
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return canvas.point(lambda v: 255 if v > 127 else 0).convert("1")


def to_header(im):
    data = []
    for y in range(H):
        for xb in range(W // 8):
            b = 0
            for bit in range(8):
                if im.getpixel((xb * 8 + bit, y)):
                    b |= 0x80 >> bit
            data.append(b)
    lines = []
    for i in range(0, len(data), 16):
        lines.append("  " + ", ".join(f"0x{v:02X}" for v in data[i:i + 16]) + ",")
    return (
        "#pragma once\n"
        "// Ecran de demarrage Neva (genere par marlin-patches/make_bootscreen.py)\n"
        "#define CUSTOM_BOOTSCREEN_TIMEOUT 3000\n"
        f"#define CUSTOM_BOOTSCREEN_BMPWIDTH {W}\n"
        "const unsigned char custom_start_bmp[] PROGMEM = {\n"
        + "\n".join(lines) + "\n};\n"
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--neva":
        im = default_logo()
    elif args and args[0] == "--texte":
        im = prusa_logo()
    elif args:
        im = from_image(args[0])
    else:
        im = prusa_machine_logo()
    OUT_H.write_text(to_header(im))
    big = im.convert("L").resize((W * 6, H * 6), Image.NEAREST)
    bg = Image.new("RGB", big.size, (10, 20, 60))
    fg = Image.new("RGB", big.size, (240, 240, 255))
    OUT_PNG.parent.mkdir(exist_ok=True)
    Image.composite(fg, bg, big).save(OUT_PNG)
    print("ecrit :", OUT_H, "et", OUT_PNG)
