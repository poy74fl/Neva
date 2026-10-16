#!/usr/bin/env python3
"""Genere docs/test_premiere_couche_spirale.gcode : une SEULE ligne en spirale sur tout le plateau
(pas de 8 mm : les lignes restent separees, on voit l'ecrasement partout), qui se termine par un
rond plein (pas de 0,45 mm) au centre. Spirale faite avec des demi-cercles G2/G3 (une centaine de lignes de G-code).

  python3 docs/make_test_spirale.py            -> rayon exterieur 90 mm, rond plein de 20 mm
  python3 docs/make_test_spirale.py 85 18      -> rayon exterieur 85 mm, rond plein de 18 mm
  python3 docs/make_test_spirale.py 85 0 test_spirale_r85_sans_centre.gcode corr   -> sans rond plein au centre (R_DISC = 0)
  python3 docs/make_test_spirale.py 85 20 test_spirale_r85_corrigee.gcode corr
        -> comme ci-dessus, ecrit dans le fichier donne, avec les corrections M421 du maillage (arriere, cote droit)
"""
import math, sys
from pathlib import Path

R_OUT = float(sys.argv[1]) if len(sys.argv) > 1 else 90.0   # rayon exterieur de la spirale (mm)
R_DISC = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0  # rayon du rond plein central (mm)
OUT_NAME = sys.argv[3] if len(sys.argv) > 3 else "test_premiere_couche_spirale.gcode"
WITH_CORR = len(sys.argv) > 4 and sys.argv[4] == "corr"
CORR = [  # corrections du maillage determinees avec docs/test_5_carres_correction.gcode (Q > 0 : buse plus haute)
    "M421 I2 J6 Q0.20", "M421 I3 J6 Q0.20", "M421 I4 J6 Q0.20",
    "M421 I2 J5 Q0.10", "M421 I3 J5 Q0.10", "M421 I4 J5 Q0.10",
    "M421 I5 J3 Q-0.10", "M421 I6 J3 Q-0.06", "M421 I5 J4 Q-0.10", "M421 I6 J4 Q-0.06",
    "M421 I5 J5 Q-0.08", "M421 I6 J5 Q-0.10", "M421 I5 J6 Q-0.08", "M421 I6 J6 Q-0.10",
]
PITCH_OUT, PITCH_DISC = 8.0, 0.45                          # pas des deux spirales (mm)
K = 0.040                                                  # mm de filament par mm de ligne (0,45 x 0,2 + ecrasement)
F = 1500                                                   # 25 mm/s


def spiral_out(pitch, r_end):
    """Spirale d'Archimede approchee par des demi-cercles a deux centres A=(-d/2,0), B=(d/2,0), d=pitch/2.
    Du centre vers l'exterieur. Retourne [(start, end, centre, sens)] avec sens +1 = antihoraire."""
    d = pitch / 2.0
    A, B = (-d / 2, 0.0), (d / 2, 0.0)
    arcs = []
    # premier demi-cercle : centre A, de (A.x + r, 0) vers (A.x - r, 0) avec r = d/2 (petit)
    r = d / 2.0
    pos = (A[0] + r, 0.0)
    use_A = True
    while True:
        c = A if use_A else B
        rad = abs(pos[0] - c[0])
        end = (c[0] - math.copysign(rad, pos[0] - c[0]), 0.0)
        arcs.append((pos, end, c, +1))
        pos = end
        use_A = not use_A
        if max(abs(pos[0] - A[0]), abs(pos[0] - B[0])) >= r_end:
            break
    return arcs


def reverse(arcs):
    out = []
    for s, e, c, sens in reversed(arcs):
        out.append((e, s, c, -sens))
    return out


def rotate180(arcs):
    return [((-s[0], -s[1]), (-e[0], -e[1]), (-c[0], -c[1]), sens) for s, e, c, sens in arcs]


outer = reverse(spiral_out(PITCH_OUT, R_OUT))    # de l'exterieur vers le centre, pas de 8 mm
disc = reverse(spiral_out(PITCH_DISC, R_DISC)) if R_DISC > 0 else []   # rond plein, de R_DISC vers le centre (R_DISC = 0 : pas de rond plein)

# --- raccord : la spirale exterieure s'arrete a "end1", le rond plein doit commencer au meme point ---
# (la spirale exterieure s'arrete vers r ~ pas/2 ; on la coupe quand elle atteint R_DISC)
cut = []
for a in outer:
    cut.append(a)
    r_end = math.hypot(*a[1])
    if r_end <= R_DISC:
        break
outer = cut
join = outer[-1][1]
if disc and (abs(disc[0][0][0] - join[0]) > 1e-6 or abs(disc[0][0][1] - join[1]) > 1e-6):
    # le rond plein est tourne de 180 degres si besoin pour que son debut tombe sur le raccord
    r2 = rotate180(disc)
    if abs(r2[0][0][0] - join[0]) < abs(disc[0][0][0] - join[0]):
        disc = r2
# si le point de depart du rond plein est un peu decale (|dx| < pas), on le ramene par un petit segment
arcs_all = outer + disc

# ------------------------------------------------------------------ G-code
L = []
a = L.append
a("; === Test de premiere couche : UNE SEULE ligne en spirale sur tout le plateau" + (", puis un rond plein ===" if R_DISC > 0 else " (sans rond plein) ==="))
a(f"; Spirale de rayon {R_OUT:.0f} mm, pas {PITCH_OUT:.1f} mm (lignes separees : on voit l'ecrasement partout),")
a(f"; puis rond plein de {R_DISC:.0f} mm au centre (pas {PITCH_DISC} mm). PLA 210 C, ventilateur coupe." if R_DISC > 0 else "; Spirale seule, sans rond plein au centre. PLA 210 C, ventilateur coupe.")
a("; Duree : environ " + ("4 minutes" if R_DISC > 0 else "2 minutes") + " + palpage. Pendant la 1re couche : DOUBLE-CLIC sur la molette = reglage Z (Decalage Z).")
a("; Lecture : lignes regulieres et de meme largeur partout = plateau plat et hauteur bonne.")
a("M107")
a("G90")
a("M83")
a("M104 S210            ; la buse chauffe pendant le homing et le palpage")
a("G28")
a("G33 P1")
a("G29                   ; palpage du plateau en plusieurs points (maillage)")
if WITH_CORR:
    a("; corrections du maillage (arriere +0,20 ; droite -0,10 puis -0,06 au bord ; coin arriere-droit -0,08 / -0,10)")
    for c in CORR: a(c)
a("M109 S210")
a("G1 Z5 F3000")
sx, sy = arcs_all[0][0]
a(f"G1 X{sx + math.copysign(5, sx):.2f} Y{sy:.2f} F6000     ; point de purge, juste a l'exterieur de la spirale")
a("G1 Z0.3 F600")
a("G1 E12 F200")
a("G1 E-1 F1800")
a(f"G1 X{sx:.2f} Y{sy:.2f} F6000")
a("G1 Z0.2 F300")
a("G1 E1 F600")
total = 0.0
for s, e, c, sens in arcs_all:
    rad = math.hypot(s[0] - c[0], s[1] - c[1])
    length = math.pi * rad
    total += length
    i, j = c[0] - s[0], c[1] - s[1]
    g = "G3" if sens > 0 else "G2"
    a(f"{g} X{e[0]:.3f} Y{e[1]:.3f} I{i:.3f} J{j:.3f} E{length * K:.3f} F{F}")
a("G1 E-2 F1800")
a("G1 Z10 F3000")
a("M104 S0")
a("M117 Spirale terminee")
a("G28")

out = Path(__file__).resolve().parent / OUT_NAME
out.write_text("\n".join(L) + "\n")
print(f"{len(arcs_all)} arcs, {total:.0f} mm de ligne, {total * K:.0f} mm de filament, {total / (F / 60):.0f} s -> {out}")

# controle de continuite
prev = None
for s, e, c, sens in arcs_all:
    if prev is not None:
        gap = math.hypot(s[0] - prev[0], s[1] - prev[1])
        if gap > 0.6:
            print("ATTENTION : saut de", round(gap, 3), "mm au raccord", prev, "->", s)
    prev = e
