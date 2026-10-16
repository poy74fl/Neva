; === Test du papier FIN : meme chose a Z 0,1 mm (epaisseur de la feuille) pour mieux distinguer les points ===
; Materiel : une feuille de papier (80 g, ~0,1 mm). Pas de chauffe, pas de filament.
; A chaque arret, l'ecran affiche le point. Glisse la feuille sous la buse :
;   - au CENTRE, note la sensation (frottement leger) : c'est la reference ;
;   - aux autres points, dis si c'est PLUS SERRE, PAREIL ou PLUS LIBRE qu'au centre.
; Clic sur la molette pour passer au point suivant.
; A 0,1 mm la buse touche presque la feuille : un point "libre" est plus haut que celui qui "frotte" ou "gratte".
G90
G28
G33 P1
G29                              ; maillage actif pendant tout le test
G1 Z5 F3000
G1 X0 Y0 F6000
G1 Z0.1 F600
M0 1/6 CENTRE (reference)
G1 Z5 F3000
G1 X70 Y0 F6000
G1 Z0.1 F600
M0 2/6 DROITE (cote BMG) 70
G1 Z5 F3000
G1 X-70 Y0 F6000
G1 Z0.1 F600
M0 3/6 GAUCHE 70
G1 Z5 F3000
G1 X0 Y60 F6000
G1 Z0.1 F600
M0 4/6 ARRIERE 60
G1 Z5 F3000
G1 X0 Y-70 F6000
G1 Z0.1 F600
M0 5/6 AVANT 70
G1 Z5 F3000
G1 X0 Y0 F6000
G1 Z0.1 F600
M0 6/6 CENTRE (controle)
G1 Z50 F3000
M300 S2700 P300
