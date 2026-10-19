#!/usr/bin/env python3
"""Schema propre (sans photo) : feuille (contour mesure sur la photo), rond imprime de 200 mm, et pour chaque noeud G29 de la v1.75
la position de la BUSE (carre rouge) et de la SONDE (rond bleu, 23 mm derriere en +Y). Orientation de la photo : +X (BMG) vers le bas, +Y (arriere) vers la droite.
Usage : python3 docs/schema_sonde_buse.py [RAYON_MAX_SONDE_mm]  (defaut 82)"""
import sys, math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 82.0
OFF = 23.0
POLY = [(-96, -105), (96, -105), (135, -29), (38, 134), (-38, 134), (-135, -29)]   # (X, Y) mm, contour de la feuille mesure sur la photo
fig, ax = plt.subplots(figsize=(10, 12), dpi=110)
ax.set_aspect("equal")
# axes : horizontal = Y (arriere a droite), vertical = X (BMG en bas, axe inverse) -> on trace (Y, X)
P = lambda X, Y: (Y, X)
ax.add_patch(Polygon([P(*p) for p in POLY], closed=True, fc="#1d2a52", ec="#f5a623", lw=3))
ax.add_patch(Circle((0, 0), 100, fill=False, ec="#00bcd4", lw=2, ls="--"))
ax.add_patch(Circle((0, 0), 100 - 0, fill=False, ec="none"))
def tower_clear(nx, ny):   # v1.76 : buse a plus de 94 mm du centre a +-30 deg d'une tour (210 / 330 deg) = la tete touche
    r = math.hypot(nx, ny)
    if r <= 94: return True
    return (nx * -0.866025 + ny * -0.5) / r < 0.866025 and (nx * 0.866025 + ny * -0.5) / r < 0.866025
nb = 0
for J in range(7):
    for I in range(7):
        X = -85 + 28.3333 * I; Y = -77 + 27 * J                 # noeud = position de la SONDE
        nx, ny = X, Y - OFF                                     # la buse est 23 mm devant
        ok = math.hypot(X, Y) <= RMAX and math.hypot(nx, ny) <= 100.05 and tower_clear(nx, ny)
        if ok:
            nb += 1
            ax.plot(*zip(P(nx, ny), P(X, Y)), color="#9aa5c4", lw=1)
            ax.plot(*P(nx, ny), "s", ms=9, color="#e53935", mec="white")
            ax.plot(*P(X, Y), "o", ms=10, color="#42a5f5", mec="white")
        else:
            ax.plot(*P(X, Y), "x", ms=8, color="#888888")
ax.add_patch(Circle((0, 0), RMAX, fill=False, ec="#4caf50", lw=2))
ax.plot(*P(0, 0), "*", ms=14, color="#ffeb3b", mec="black")
ax.annotate("centre X0 Y0", P(0, 0), (8, 12), textcoords="offset points", color="#ffeb3b", fontsize=9)
ax.set_xlim(-130, 150); ax.set_ylim(150, -150)
ax.set_xlabel("Y  (arriere ->)"); ax.set_ylabel("X  (BMG +X en bas)")
ax.text(-125, -140, "avant (Y-)", color="#333"); ax.text(105, -140, "arriere (Y+)", color="#333")
ax.set_title(f"G29 v1.76 : sonde (rond bleu) et buse (carre rouge), sonde a {RMAX:g} mm du centre au plus\n"
             f"{nb}/49 noeuds sondes ; croix grises = noeuds non sondes (limite sonde ou tour) ; pointille cyan = rond imprime 200 mm ; orange = bord de la feuille ; vert = cercle sonde", fontsize=10)
out = Path(__file__).resolve().parent / "schema_sonde_buse.png"
fig.savefig(out, bbox_inches="tight")
print("ecrit", out, nb)
