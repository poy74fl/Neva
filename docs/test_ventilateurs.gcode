; === Test des ventilateurs (aucun mouvement, aucun palpage) ===
; Ventilateurs d'impression (FAN0) : 50 % puis 100 % puis arret.
; Ventilateur du hotend (HE1) : doit demarrer tout seul au-dessus de 50 C.
M412 S0               ; capteur de filament coupe pour ce test (pas de filament charge)
M117 Test ventilos
M107
M117 Piece 50%
M106 S128
G4 S6
M117 Piece 100%
M106 S255
G4 S6
M107
M117 Piece arret
G4 S3
M117 Chauffe 60C : hotend ventilo?
M104 S60
M109 S60
M300 S2700 P300
M117 60C : ventilo hotend?
G4 S10
M104 S0
M412 S1               ; capteur de filament remis en service
M117 Fini - hotend refroidit
M300 S2700 P300
