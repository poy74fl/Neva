#!/usr/bin/env python3
"""Colle les zones du plateau (docs/zones_plateau.png) en transparence sur une photo de spirale.

  python3 docs/overlay_zones.py photo.jpg sortie.png CX CY RX RY [rotation_deg]

CX CY : centre de la spirale dans la photo (pixels) ; RX RY : demi-axes en pixels du cercle de 86 mm
(la photo est un peu en perspective : ellipse) ; rotation_deg : angle photo = angle machine + rotation
(defaut -88.5 : tour Z a droite, tour X en haut a gauche, tour Y en bas a gauche).
Les angles machine : 0 = cote BMG (X+), 90 = arriere (tour Z), 210 = tour X, 330 = tour Y."""
import math, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

src, out = sys.argv[1], sys.argv[2]
CX, CY, RX, RY = (float(v) for v in sys.argv[3:7])
ROT = float(sys.argv[7]) if len(sys.argv) > 7 else -88.5
R_REF = 86.0
im = ImageOps.exif_transpose(Image.open(src)).convert("RGBA")
over = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(over)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(im.width * 0.036))
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(im.width * 0.022))
except OSError:
    font = small = ImageFont.load_default()

def pt(r_mm, ang_machine):
    a = math.radians(ang_machine + ROT)
    return (CX + (r_mm / R_REF) * RX * math.cos(a), CY - (r_mm / R_REF) * RY * math.sin(a))

RINGS = [(0, 30, "C"), (30, 60, "B"), (60, 90, "A")]
COLORS = [(231, 76, 60), (52, 152, 219), (46, 204, 113), (241, 196, 15), (155, 89, 182), (230, 126, 34), (26, 188, 156), (233, 30, 99)]
for n in range(8):
    ang = 45 * n
    col = COLORS[n]
    for r0, r1, lab in RINGS:
        if lab == "C":
            continue
        a0, a1 = ang - 22.5, ang + 22.5
        poly = [pt(r1, a0 + (a1 - a0) * k / 20) for k in range(21)] + [pt(r0, a1 - (a1 - a0) * k / 20) for k in range(21)]
        d.polygon(poly, fill=col + ((70 if lab == "A" else 45),), outline=col + (230,))
        x, y = pt((r0 + r1) / 2 if lab == "B" else 76, ang)
        txt = f"{n + 1}{lab}"
        w = d.textlength(txt, font=font)
        d.text((x - w / 2, y - font.size / 2), txt, font=font, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
# centre
poly = [pt(30, 360 * k / 60) for k in range(61)]
d.polygon(poly, fill=(255, 255, 255, 40), outline=(255, 255, 255, 230))
w = d.textlength("C", font=font)
d.text((CX - w / 2, CY - font.size / 2), "C", font=font, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
# reperes
for name, ang in (("BMG", 0), ("tour Z", 90), ("tour X", 210), ("tour Y", 330)):
    x, y = pt(104, ang)
    w = d.textlength(name, font=small)
    d.text((x - w / 2, y - small.size / 2), name, font=small, fill=(255, 235, 59, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
Image.alpha_composite(im, over).convert("RGB").save(out, quality=92)
print("ecrit :", out)
