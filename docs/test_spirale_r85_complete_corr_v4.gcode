; === Test de premiere couche : UNE SEULE ligne en spirale sur tout le plateau (sans rond plein) ===
; Spirale de rayon 85 mm, pas 8.0 mm (lignes separees : on voit l'ecrasement partout),
; Spirale seule, sans rond plein au centre. PLA 210 C, ventilateur coupe.
; Duree : environ 2 minutes + palpage. Pendant la 1re couche : DOUBLE-CLIC sur la molette = reglage Z (Decalage Z).
; PREREQUIS : M851 Z-1.22 (deja fait). Spirale complete jusqu'au centre, corrections M421 de l'essai 4.
; Lecture : lignes regulieres et de meme largeur partout = plateau plat et hauteur bonne.
M107
G90
M83
M104 S210            ; la buse chauffe pendant le homing et le palpage
G28
G33 P1
G29                   ; palpage du plateau en plusieurs points (maillage)
; corrections du maillage (essai 4, M851 Z-1.22) : bord BMG -0,35 ; vers tour Y -0,10 ; avant -0,15/-0,10 ; arriere +0,05
M421 I6 J3 Q-0.35
M421 I6 J4 Q-0.35
M421 I6 J5 Q-0.25
M421 I5 J3 Q-0.25
M421 I5 J4 Q-0.25
M421 I5 J5 Q-0.25
M421 I5 J2 Q-0.10
M421 I6 J2 Q-0.10
M421 I5 J1 Q-0.05
M421 I1 J0 Q-0.15
M421 I2 J0 Q-0.15
M421 I3 J0 Q-0.15
M421 I4 J0 Q-0.15
M421 I5 J0 Q-0.15
M421 I2 J1 Q-0.10
M421 I3 J1 Q-0.10
M421 I4 J1 Q-0.10
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
G2 X56.000 Y0.000 I58.000 J0.000 E7.288 F1500
G2 X-52.000 Y0.000 I-54.000 J0.000 E6.786 F1500
G2 X48.000 Y0.000 I50.000 J0.000 E6.283 F1500
G2 X-44.000 Y0.000 I-46.000 J0.000 E5.781 F1500
G2 X40.000 Y0.000 I42.000 J0.000 E5.278 F1500
G2 X-36.000 Y0.000 I-38.000 J0.000 E4.775 F1500
G2 X32.000 Y0.000 I34.000 J0.000 E4.273 F1500
G2 X-28.000 Y0.000 I-30.000 J0.000 E3.770 F1500
G2 X24.000 Y0.000 I26.000 J0.000 E3.267 F1500
G2 X-20.000 Y0.000 I-22.000 J0.000 E2.765 F1500
G2 X16.000 Y0.000 I18.000 J0.000 E2.262 F1500
G2 X-12.000 Y0.000 I-14.000 J0.000 E1.759 F1500
G2 X8.000 Y0.000 I10.000 J0.000 E1.257 F1500
G2 X-4.000 Y0.000 I-6.000 J0.000 E0.754 F1500
G2 X0.000 Y0.000 I2.000 J0.000 E0.251 F1500
G1 E-2 F1800
G1 Z10 F3000
M104 S0
M117 Spirale terminee
G28
