#!/usr/bin/env python3
"""Genere docs/test_5_carres.gcode : 5 carres pleins de 20 mm, une seule couche, au centre et a 70 mm
a droite (BMG), a l'arriere, a gauche et a l'avant. Compare l'ecrasement de la 1re couche aux 5 endroits.
Environ 4 minutes + palpage. PLA 210 C, ventilateur coupe."""
from pathlib import Path

SIDE, PITCH, K, F = 20.0, 0.45, 0.040, 1500
SQUARES = [("CENTRE", 0, 0), ("DROITE (BMG)", 70, 0), ("ARRIERE", 0, 70), ("GAUCHE", -70, 0), ("AVANT", 0, -70)]

L = []
a = L.append
a("; === Test de 5 carres : l'ecrasement de la 1re couche est-il le meme partout ? ===")
a("; Carres de 20 mm : centre, droite (cote BMG), arriere, gauche, avant (a 70 mm du centre). PLA 210 C.")
a("; Lecture : des carres pleins, lisses et de meme aspect = hauteur bonne partout. Un carre rugueux/raye = buse trop haute ;")
a("; un carre transparent/ecrase avec des bourrelets = buse trop basse. Pendant le centre : double-clic molette = reglage Z.")
a("M107")
a("G90")
a("M83")
a("M104 S210            ; la buse chauffe pendant le homing et le palpage")
a("G28")
a("G33 P1")
a("G29                  ; palpage du plateau en plusieurs points (maillage)")
a("M109 S210")
a("G1 Z5 F3000")
a("G1 X-85 Y0 F6000     ; goutte de purge sur le bord gauche")
a("G1 Z0.3 F600")
a("G1 E10 F200")
a("G1 E-1 F1800")
a("G1 Z5 F3000")
n = int(SIDE / PITCH)
for name, cx, cy in SQUARES:
    x0, y0 = cx - SIDE / 2, cy - SIDE / 2
    a(f"M117 Carre {name}")
    a(f"G1 X{x0:.2f} Y{y0:.2f} F6000")
    a("G1 Z0.2 F300")
    a("G1 E1 F600")
    for i in range(n + 1):
        x = x0 + i * PITCH
        ya, yb = (y0, y0 + SIDE) if i % 2 == 0 else (y0 + SIDE, y0)
        a(f"G1 X{x:.2f} Y{yb:.2f} E{SIDE * K:.3f} F{F}")
        if i < n:
            a(f"G1 X{x + PITCH:.2f} Y{yb:.2f} E{PITCH * K:.3f} F{F}")
    a("G1 E-1 F1800")
    a("G1 Z5 F3000")
a("M104 S0")
a("M117 Test 5 carres termine")
a("G28")
a("M300 S2700 P300")
out = Path(__file__).resolve().parent / "test_5_carres.gcode"
out.write_text("\n".join(L) + "\n")
print(f"{len(L)} lignes -> {out}")
