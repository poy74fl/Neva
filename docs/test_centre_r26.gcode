; === Test de premiere couche : UNE SEULE ligne en spirale sur tout le plateau (sans rond plein) ===
; Spirale de rayon 26 mm, pas 8.0 mm (lignes separees : on voit l'ecrasement partout),
; Spirale seule, sans rond plein au centre. PLA 210 C, ventilateur coupe.
; Duree : environ 2 minutes + palpage. Pendant la 1re couche : DOUBLE-CLIC sur la molette = reglage Z (Decalage Z).
; Lecture : lignes regulieres et de meme largeur partout = plateau plat et hauteur bonne.
M107
G90
M83
M104 S210            ; la buse chauffe pendant le homing et le palpage
G28
G33 P1
G29                   ; palpage du plateau en plusieurs points (maillage)
M109 S210
G1 Z5 F3000
G1 X29.00 Y0.00 F6000     ; point de purge, juste a l'exterieur de la spirale
G1 Z0.3 F600
G1 E12 F200
G1 E-1 F1800
G1 X24.00 Y0.00 F6000
G1 Z0.2 F300
G1 E1 F600
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
