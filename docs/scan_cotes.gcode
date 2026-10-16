; === Balayage par cotes : hauteur du plateau le long de 4 axes (G30, sans maillage) ===
; Droite = cote extrudeur BMG (+X), gauche (-X), arriere (+Y, vers la tour Z), avant (-Y).
; A lancer depuis le terminal de Simplify3D connecte. Duree : environ 3 a 4 minutes. Pas de chauffe, pas de filament.
; Colle ensuite les lignes "Bed X: .. Y: .. Z: .." : on compare les 4 cotes a rayon egal.
G90
G28
G33 P1
M420 S0              ; maillage coupe : valeurs brutes
M118 E1 === DEBUT DU BALAYAGE PAR COTES ===
G30 X0 Y0            ; reference au centre
M118 E1 --- DROITE (cote BMG) ---
G30 X30 Y0
G30 X50 Y0
G30 X70 Y0
G30 X85 Y0
M118 E1 --- GAUCHE ---
G30 X-30 Y0
G30 X-50 Y0
G30 X-70 Y0
G30 X-85 Y0
M118 E1 --- ARRIERE ---
G30 X0 Y30
G30 X0 Y50
G30 X0 Y70
G30 X0 Y85
M118 E1 --- AVANT ---
G30 X0 Y-30
G30 X0 Y-50
G30 X0 Y-65
M118 E1 --- retour au centre ---
G30 X0 Y0            ; si la valeur a change, la mesure derive
M118 E1 === FIN DU BALAYAGE PAR COTES ===
G1 Z50 F3000
M300 S2700 P300
