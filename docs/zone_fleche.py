#!/usr/bin/env python3
"""Dessine sur docs/plaque_palpage.jpg le contour de la feuille (hexagone, arriere en fleche), la zone atteignable par la SONDE
(distance au bord >= MARGE) et les noeuds du maillage G29 (7x7, y de -77 a +85). Machine : +X vers le bas de la photo, +Y vers la droite.
Usage : python3 docs/zone_fleche.py [MARGE_mm]"""
import sys, math
from pathlib import Path
from PIL import Image, ImageDraw
MARGE = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
CX, CY, S = 432.2, 893.9, 3.5          # centre du rond B (px) et echelle (px/mm)
# sommets du contour de la feuille mesures sur la photo (X, Y) en mm : bouts plats avant/arriere + diagonales a 30 degres
POLY = [(-96, -105), (96, -105), (135, -29), (38, 134), (-38, 134), (-135, -29)]
def px(X, Y): return (CX + Y * S, CY + X * S)
def dist_bord(X, Y):                    # polygone convexe : distance au bord le plus proche (>0 = dedans)
    best = 1e9
    for i in range(len(POLY)):
        (x1, y1), (x2, y2) = POLY[i], POLY[(i + 1) % len(POLY)]
        ex, ey = x2 - x1, y2 - y1
        n = math.hypot(ex, ey)
        best = min(best, (ex * (Y - y1) - ey * (X - x1)) / n * (1 if True else -1))
    return best
# orientation du polygone : on teste le centre
sgn = 1 if dist_bord(0, 0) > 0 else -1
d = lambda X, Y: sgn * dist_bord(X, Y)
im = Image.open(Path(__file__).resolve().parent / "plaque_palpage.jpg").convert("RGBA")
ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); g = ImageDraw.Draw(ov)
# zone sonde (vert translucide) : pixel par pixel
for u in range(0, im.size[0], 3):
    for v in range(130, im.size[1], 3):
        X, Y = (v - CY) / S, (u - CX) / S
        if d(X, Y) >= MARGE and math.hypot(X, Y - 23) <= 100:
            g.rectangle([u, v, u + 2, v + 2], fill=(0, 200, 80, 70))
g.polygon([px(*p) for p in POLY], outline=(255, 255, 0, 255))
g.line([px(*p) for p in POLY] + [px(*POLY[0])], fill=(255, 255, 0, 255), width=3)
n_ok = 0
for J in range(7):
    for I in range(7):
        X = -85 + 28.3333 * I; Y = -77 + 27 * J
        ok = d(X, Y) >= MARGE and math.hypot(X, Y - 23) <= 100.05   # sonde sur la feuille ET buse (23 mm devant) a 100 mm au plus
        n_ok += ok
        u, v = px(X, Y)
        g.ellipse([u - 7, v - 7, u + 7, v + 7], fill=(0, 120, 255, 255) if ok else (255, 40, 40, 255), outline=(255, 255, 255, 255))
        g.text((u + 9, v - 6), f"{I},{J}", fill=(255, 255, 255, 255))
g.rectangle([0, 0, 924, 60], fill=(0, 0, 0, 170))
g.text((10, 8), f"Jaune : contour de la feuille mesure sur la photo | Vert : zone SONDE (>= {MARGE:g} mm du bord, buse a 100 mm au plus)", fill=(255, 255, 255, 255))
g.text((10, 30), f"Bleu : noeud G29 sonde ({n_ok}/49) | Rouge : noeud ecarte (sonde trop pres du bord ou dehors)", fill=(255, 255, 255, 255))
out = Path(__file__).resolve().parent / "zone_fleche.png"
Image.alpha_composite(im, ov).convert("RGB").save(out)
print("ecrit", out, "noeuds bleus :", n_ok)
for J in range(7):
    print(" ".join("#" if d(-85+28.3333*I,-77+27*J)>=MARGE and math.hypot(-85+28.3333*I,-77+27*J-23)<=100.05 else "." for I in range(7)), "  J=%d"%J)
