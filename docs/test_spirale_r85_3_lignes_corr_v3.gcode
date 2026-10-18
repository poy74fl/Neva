; === Test de premiere couche : UNE SEULE ligne en spirale sur tout le plateau (tours exterieurs seulement) ===
; Spirale de rayon 85 mm, pas 8.0 mm (lignes separees : on voit l'ecrasement partout),
; Seulement les tours exterieurs, jusqu'a 61 mm du centre. PLA 210 C, ventilateur coupe.
; Duree : environ 1 minute + palpage. Pendant la 1re couche : DOUBLE-CLIC sur la molette = reglage Z (Decalage Z).
; PREREQUIS : M851 Z-1.22 puis M500. Corrections M421 : droite -0,25, avant -0,10, arriere +0,05 (essai 3)
; Lecture : lignes regulieres et de meme largeur partout = plateau plat et hauteur bonne.
M107
G90
M83
M104 S210            ; la buse chauffe pendant le homing et le palpage
G28
G33 P1
G29                   ; palpage du plateau en plusieurs points (maillage)
; corrections du maillage (essai 3, avec M851 Z-1.22) : droite -0,25 ; avant -0,10 / -0,05 ; arriere +0,05
M421 I5 J2 Q-0.25
M421 I6 J2 Q-0.25
M421 I5 J3 Q-0.25
M421 I6 J3 Q-0.25
M421 I5 J4 Q-0.25
M421 I6 J4 Q-0.25
M421 I5 J5 Q-0.25
M421 I6 J5 Q-0.25
M421 I5 J1 Q-0.15
M421 I1 J0 Q-0.10
M421 I2 J0 Q-0.10
M421 I3 J0 Q-0.10
M421 I4 J0 Q-0.10
M421 I5 J0 Q-0.10
M421 I2 J1 Q-0.05
M421 I3 J1 Q-0.05
M421 I4 J1 Q-0.05
M421 I1 J6 Q0.05
M421 I2 J6 Q0.05
M421 I3 J6 Q0.05
M421 I4 J6 Q0.05
M421 I5 J6 Q0.05
M421 I1 J5 Q0.05
M421 I2 J5 Q0.05
M421 I3 J5 Q0.05
M421 I4 J5 Q0.05
M109 S210
G1 Z5 F3000
G1 X-89.00 Y0.00 F6000     ; point de purge, juste a l'exterieur de la spirale
G1 Z0.3 F600
G1 E12 F200
G1 E-1 F1800
G1 X-84.00 Y0.00 F6000
G1 Z0.2 F300
G1 E1 F600
G2 X80.000 Y0.000 I82.000 J0.000 E10.304 F1500
G2 X-76.000 Y0.000 I-78.000 J0.000 E9.802 F1500
G2 X72.000 Y0.000 I74.000 J0.000 E9.299 F1500
G2 X-68.000 Y0.000 I-70.000 J0.000 E8.796 F1500
G2 X64.000 Y0.000 I66.000 J0.000 E8.294 F1500
G2 X-60.000 Y0.000 I-62.000 J0.000 E7.791 F1500
G1 E-2 F1800
G1 Z10 F3000
M117 Spirale terminee - buse chaude
G28
