#!/usr/bin/env python3
"""Genere docs/zones_plateau.png : le plateau decoupe en zones nommees (secteur 1-8 + anneau A/B, centre C)
avec les noeuds du maillage (I,J) pour relier un retour d'impression a une correction M421.
Vue de dessus, avant (Y-) en bas, cote BMG (X+) a droite."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

R_PLATEAU = 100
RINGS = [30, 60, 90]            # C < 30, B 30-60, A 60-90
SECTORS = {                     # angle central (degres, 0 = cote BMG, sens antihoraire vu de dessus)
    1: (0,   "BMG"),
    2: (45,  "arriere droit"),
    3: (90,  "arriere"),
    4: (135, "arriere gauche"),
    5: (180, "gauche"),
    6: (225, "avant gauche\n(tour X)"),
    7: (270, "avant"),
    8: (315, "avant droit\n(tour Y)"),
}
fig, ax = plt.subplots(figsize=(11, 11), dpi=150)
ax.set_aspect("equal")
ax.set_xlim(-150, 150); ax.set_ylim(-150, 150)
ax.axis("off")
ax.add_patch(plt.Circle((0, 0), R_PLATEAU, fill=False, lw=2, color="#333"))
for r in RINGS[:2]:
    ax.add_patch(plt.Circle((0, 0), r, fill=False, lw=1.2, color="#888", ls="--"))
for k in range(8):
    a = math.radians(22.5 + 45 * k)
    ax.plot([30 * math.cos(a), 100 * math.cos(a)], [30 * math.sin(a), 100 * math.sin(a)], color="#888", lw=1.2, ls="--")
# etiquettes de zones
for n, (ang, name) in SECTORS.items():
    a = math.radians(ang)
    for ring, rmid in (("A", 75), ("B", 45)):
        ax.text(rmid * math.cos(a), rmid * math.sin(a) + 3, f"{n}{ring}", ha="center", va="center", fontsize=17, fontweight="bold", color="#b00020")
    ax.text(116 * math.cos(a), 116 * math.sin(a), name, ha="center", va="center", fontsize=11, color="#222")
ax.text(0, 0, "C\ncentre", ha="center", va="center", fontsize=15, fontweight="bold", color="#b00020")
# noeuds du maillage
for i in range(7):
    for j in range(7):
        x = -85 + 28.333 * i; y = -77 + 27 * j
        if math.hypot(x, y) <= 100:
            ax.plot(x, y, "o", ms=3, color="#1565c0")
            ax.text(x + 1.5, y - 4.5, f"{i},{j}", fontsize=6.5, color="#1565c0")
# reperes machine
for name, ang in (("tour X", 210), ("tour Y", 330), ("tour Z", 90)):
    a = math.radians(ang)
    ax.plot(135 * math.cos(a), 135 * math.sin(a), "s", ms=11, color="#555")
    ax.text(135 * math.cos(a), 135 * math.sin(a) - 9, name, ha="center", fontsize=9, color="#555")
ax.text(0, -143, "AVANT (Y-)", ha="center", fontsize=11, color="#555")
ax.text(0, 142, "ARRIERE (Y+)", ha="center", fontsize=11, color="#555")
ax.set_title("Zones du plateau (vue de dessus) : secteur 1-8 + anneau A (60-85 mm) / B (30-60 mm) / C (centre)\n"
             "points bleus = noeuds du maillage I,J (M421 I<i> J<j>)", fontsize=10)
out = Path(__file__).resolve().parent / "zones_plateau.png"
fig.savefig(out, bbox_inches="tight")
print("ecrit :", out)
