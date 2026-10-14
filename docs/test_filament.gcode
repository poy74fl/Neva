; === Test du filament : chauffe, extrusion mesuree, retrait, controle du capteur ===
; A copier sur la SD de l'ecran et a lancer depuis "Impr. depuis la SD" (filament deja charge).
; Avant : marque le filament avec un feutre a 120 mm de l'entree de l'extrudeur.
; Pendant : la tete ne bouge pas. Place un recipient sous la buse (la machine laisse sortir du plastique).
M117 Chauffe 200C...
M104 S200
M109 S200            ; attend les 200 C
M83                  ; extrusion relative
G92 E0
M117 Extrusion 10 mm
G1 E10 F100          ; purge de 10 mm (nettoie la buse)
G4 S3
M117 Marque a 120mm !
G4 S10               ; 10 s pour verifier que la marque est a 120 mm
M117 Extrusion 100 mm
G1 E100 F100         ; 100 mm a 1,7 mm/s (environ 60 s)
G4 S2
M117 Mesure: marque?
G4 S15               ; la marque doit etre a 20 mm de l'entree (120 - 100)
M117 Retrait 5 mm
G1 E-5 F1800         ; retraction de controle
G4 S2
G1 E5 F600
M117 Test termine
M104 S0
M84 E
; Resultat : distance parcourue par la marque = 100 mm -> E-steps OK (415).
; Si elle est differente : M92 E{415 * 100 / distance mesuree}, puis M500.
