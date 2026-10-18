; === T-buse : hauteur du plateau mesuree par la BUSE aux points de la carte au papier (SUIVI.md) ===
; Firmware de test 1.67-T4b ou plus (SENSORLESS_PROBING). Pas de G33 : l'origine Z reste celle de l'EEPROM.
; Sensibilite de palpage : M914 P1 X80 Y80 Z80 (a envoyer AVANT, valeur qui marche chez toi).
; Duree : environ 3 minutes. Pas de chauffe, pas de filament. Main pres de l'interrupteur 12 V.
; Lecture : (Z du point) - (Z du centre). Si le defaut du coin BMG est vu par la buse :
;   X57 Y0 : -0.10   X70 Y0 : +0.36   X80 Y0 : +0.63   X70 Y25 : +0.56   X70 Y-25 : +0.01   (carte au papier)
G90
G28
M420 S0              ; maillage coupe : valeurs brutes
M118 E1 === DEBUT DU BALAYAGE BUSE ===
G30 X0 Y0            ; reference au centre
M118 E1 --- axe X, cote BMG ---
G30 X57 Y0
G30 X70 Y0
G30 X80 Y0
M118 E1 --- coin BMG ---
G30 X70 Y25
G30 X70 Y-25
M118 E1 --- autres cotes ---
G30 X-70 Y0
G30 X0 Y70
G30 X0 Y-65
M118 E1 --- retour au centre ---
G30 X0 Y0            ; si la valeur a change, la mesure derive
M118 E1 === FIN DU BALAYAGE BUSE ===
G1 Z50 F3000
M300 S2700 P300
