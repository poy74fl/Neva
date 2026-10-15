; === Animation de chauffe : la tete balaie de gauche a droite comme une barre de progression ===
; A coller dans le G-code de DEBUT du slicer (PrusaSlicer : Reglages imprimante > G-code personnalise).
; Duree de l'animation = 20 x 2,5 s = 50 s. Regle-la sur le temps de chauffe reel de ta buse :
;   change les G4 P2500 (en ms). La fin est toujours attendue par M109, la temperature est donc garantie.
;
G28                               ; origine
G33 P1                            ; la sonde recale Z0
G29                               ; palpage du plateau en plusieurs points (maillage)
M104 S[first_layer_temperature]   ; lance la chauffe SANS attendre (Cura : {material_print_temperature_layer_0})
M117 Chauffe en cours...
G1 Z100 F6000                     ; hauteur de securite au-dessus du plateau
G1 X-60 Y0 F6000                   ; depart a gauche
G1 X-54 F3600
G4 P2500
G1 X-48 F3600
G4 P2500
G1 X-42 F3600
G4 P2500
G1 X-36 F3600
G4 P2500
G1 X-30 F3600
G4 P2500
G1 X-24 F3600
G4 P2500
G1 X-18 F3600
G4 P2500
G1 X-12 F3600
G4 P2500
G1 X-6 F3600
G4 P2500
G1 X0 F3600
G4 P2500
G1 X6 F3600
G4 P2500
G1 X12 F3600
G4 P2500
G1 X18 F3600
G4 P2500
G1 X24 F3600
G4 P2500
G1 X30 F3600
G4 P2500
G1 X36 F3600
G4 P2500
G1 X42 F3600
G4 P2500
G1 X48 F3600
G4 P2500
G1 X54 F3600
G4 P2500
G1 X60 F3600
G4 P2500
M109 S[first_layer_temperature]   ; attend la fin de la chauffe si elle n'est pas finie
M117 Impression...
G1 X0 Y0 Z10 F6000               ; revient au centre, puis ton G-code habituel continue
; === fin de l'animation ===
