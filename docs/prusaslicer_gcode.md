# Réglages PrusaSlicer pour la Neva

À faire **une seule fois**, dans *Réglages de l'imprimante* (Printer Settings), puis enregistrer le profil.

## Général
- **Forme du plateau** : *Personnalisée*, importer `docs/forme_plateau.svg` (disque de 190 mm, origine **0, 0**), ou *Circulaire* de 190 mm de diamètre. Sinon colle à la main la ligne de `docs/forme_plateau_bed_shape.txt` dans le fichier de profil.
- **Hauteur max d'impression** : selon ta machine (le Z du firmware monte à ~312 mm, vise 200–250).
- **Variante G-code** : *Marlin 2*.
- **Z offset** : 0 (le décalage est réglé dans le firmware : `M851 Z-1.233` / écran « Décalage Z »).

## Extrudeur
- **Distances d'extrusion relatives** (Use relative E distances) : **coché**.
- **Rétraction** : 2 mm à 40 mm/s pour commencer (Bowden BMG : monte à 3–4 mm au besoin).

## G-code personnalisé

### Début du G-code (Start G-code)
```
M107
G90
M83
M104 S{first_layer_temperature[0]}
G28
G33 P1
G29
G1 X-45 Y-77.94 F6000
G1 Z5 F3000
M109 S{first_layer_temperature[0]}
G1 Z0.3 F600
G1 E8 F200
G3 X45 Y-77.94 I45 J77.94 E7 F1200
G1 E-2 F1800
G1 Z5 F3000
```
Il fait : lancement de la chauffe (`M104`, la buse chauffe pendant le reste), homing, correction de la hauteur au centre (`G33 P1`), **palpage du plateau en plusieurs points (`G29`)**, déplacement à 5 mm au-dessus du début de la ligne de purge, attente de la température (`M109`, la goutte tombe donc sur la purge), puis **une vraie ligne de purge en arc de cercle à l'avant du plateau** (rayon 90 mm, de X −45 Y −77,94 à X +45 Y −77,94, 94 mm de long, 0,3 mm de haut, précédée d'un petit tas de 8 mm de filament et suivie d'une rétraction de 2 mm) avant de commencer. Les anciens `M421` ont été retirés avec le nouveau maillage (31 nœuds).

### Fin du G-code (End G-code)
```
M104 S0
M107
G91
G1 E-2 F1800
G1 Z10 F3000
G90
G28
M117 Impression terminee
M300 S2700 P300
```
Il coupe la buse, rétracte, remonte, remet la tête en haut (`G28`) et fait un bip. Pas de `M84` : sur une delta, couper les moteurs peut faire retomber les chariots.

### Avant le changement de couche / après : laisser vide.

## Remarque
- PrusaSlicer 2.6 et plus : l'option *Arc fitting* (Réglages d'impression > Avancé) génère des arcs `G2/G3`, que le firmware accepte (`ARC_SUPPORT`).
- Si l'écran propose « Imprimer » dès le premier clic, il suffit de recliquer pour confirmer.

> Depuis la v1.76 : les 19 `M421` de l'ancien maillage sont retirés du début de G-code (le maillage a changé : 31 nœuds sondés). Les corrections par zone seront à refaire avec `docs/test_spirale_r85_complete_v13.gcode` si besoin.

> Ventilateurs (depuis le montage) : profil « PLA Neva » avec refroidissement actif (`cooling = 1`, ventilateur à 100 % dès la couche 2, pleine vitesse à la couche 3, 100 % sur les ponts, ralentissement si la couche dure moins de 20 s). La sortie `M106` va sur FAN0 ; le ventilateur du hotend est sur FAN1 et démarre seul au-dessus de 50 °C.

> Réglages d'impression : le bundle contient maintenant aussi le profil « Neva 0.2mm PLA » (couche 0,2 mm, 2 périmètres, remplissage 15 % gyroïde, vitesses prudentes : 40 mm/s périmètres, 50 mm/s remplissage, 20 mm/s première couche, jupe de 1 tour, étiquetage des objets pour `M486`). Hauteur max de l'imprimante : 300 mm.

> Couche par couche : `layer_gcode = G92 E0` (obligatoire avec l'extrusion relative `M83` : sans lui PrusaSlicer refuse de découper avec l'erreur « Ajoutez G92 E0 à layer_gcode »).

> Vitesses d'impression (profil « Neva 0.2mm PLA ») : première couche 20 mm/s, périmètres extérieurs 40, périmètres 60, remplissage 80, plein 60, dessus 40, ponts 40, déplacements 150 mm/s. `slowdown_below_layer_time = 8` : PrusaSlicer ne ralentit une couche que si elle dure moins de 8 s (20 s la ralentissait inutilement sur les petites pièces comme un cube de 20 mm).
