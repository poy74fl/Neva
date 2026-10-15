; === Balayage de la hauteur du plateau : 13 mesures G30 (sans maillage) ===
; A lancer depuis la carte de l'ecran, avec le terminal de Simplify3D connecte :
; les lignes "Bed X: .. Y: .. Z: .." s'affichent dans le terminal. Duree : environ 3 minutes.
; Pas de chauffe, pas de filament necessaires. Main pres de l'interrupteur 12 V la premiere fois.
G90
G28
G33 P1
M420 S0              ; maillage coupe : valeurs brutes
M118 E1 === DEBUT DU BALAYAGE ===
G30 X0 Y0            ; reference au centre
M118 E1 --- cercle 60 mm ---
G30 X60 Y0
G30 X30 Y52
G30 X-30 Y52
G30 X-60 Y0
G30 X-30 Y-52
G30 X30 Y-52
M118 E1 --- cercle 75 mm ---
G30 X75 Y0
G30 X37.5 Y65
G30 X-37.5 Y65
G30 X-75 Y0
G30 X-37.5 Y-65
G30 X37.5 Y-65
M118 E1 --- retour au centre ---
G30 X0 Y0            ; si la valeur a change, la mesure derive
M118 E1 === FIN DU BALAYAGE ===
G1 Z50 F3000
M300 S880 P150
