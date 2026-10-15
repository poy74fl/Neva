; === Test des courroies : comparaison de la charge des 3 moteurs (StallGuard des TMC2209) ===
; Les 3 chariots montent et descendent ensemble (mouvement Z pur, tete au centre, a 30 puis 60 mm/s).
; Le firmware envoie toutes les 250 ms une ligne "X:pwm/cs/sg|...  Y:...  Z:...  E0:..." sur le port serie.
; Le 3e nombre (sg) est la valeur StallGuard : un chariot dont le sg s'ecarte nettement des 2 autres
; a une courroie plus lache/plus serree ou un frottement. Pour un resume automatique : docs/test_courroies.py
; L'ecran affiche en direct la MOYENNE du sg de chaque tour et l'ecart max entre tours : "X180 Y177 Z183 e7%"
; (e = ecart max / moyenne). Le resultat reste affiche a la fin. Il se lance aussi depuis le menu "Tests" > "Test courroies".
; Pas de chauffe, pas de filament necessaires. Duree : environ 1 minute.
M117 Test courroies...
G90
G28
G1 X0 Y0 Z200 F6000
M400
M122 S1 P250           ; rapport continu toutes les 250 ms (fin : M122 S0)
M118 E1 === COURROIES 30 mm/s ===
G1 Z60 F1800
G1 Z200 F1800
G1 Z60 F1800
G1 Z200 F1800
G1 Z60 F1800
G1 Z200 F1800
M400
M118 E1 === COURROIES 60 mm/s ===
G1 Z60 F3600
G1 Z200 F3600
G1 Z60 F3600
G1 Z200 F3600
G1 Z60 F3600
G1 Z200 F3600
M400
M122 S0                ; fin du rapport continu : le resultat reste affiche sur l'ecran (X.. Y.. Z.. e..%)
