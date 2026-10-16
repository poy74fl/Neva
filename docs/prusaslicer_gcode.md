# Réglages PrusaSlicer pour la Neva

À faire **une seule fois**, dans *Réglages de l'imprimante* (Printer Settings), puis enregistrer le profil.

## Général
- **Forme du plateau** : circulaire, **diamètre 190 mm** (monte à 200 quand ta zone est validée), origine **0, 0**.
- **Hauteur max d'impression** : selon ta machine (le Z du firmware monte à ~312 mm, vise 200–250).
- **Variante G-code** : *Marlin 2*.
- **Z offset** : 0 (le décalage est réglé dans le firmware : M851 / écran « Décalage Z »).

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
M109 S{first_layer_temperature[0]}
G1 Z5 F3000
G1 X-85 Y0 F6000
G1 Z0.3 F600
G1 E10 F200
G1 E-1 F1800
G1 Z5 F3000
```
Il fait : lancement de la chauffe (`M104`, la buse chauffe pendant le reste), homing, correction de la hauteur au centre (`G33 P1`), **palpage du plateau en plusieurs points (`G29`)**, attente de la température (`M109`), puis une goutte de purge sur le bord gauche (X -85) avant de commencer.

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
M300 S880 P300
```
Il coupe la buse, rétracte, remonte, remet la tête en haut (`G28`) et fait un bip. Pas de `M84` : sur une delta, couper les moteurs peut faire retomber les chariots.

### Avant le changement de couche / après : laisser vide.

## Remarque
- PrusaSlicer 2.6 et plus : l'option *Arc fitting* (Réglages d'impression > Avancé) génère des arcs `G2/G3`, que le firmware accepte (`ARC_SUPPORT`).
- Si l'écran propose « Imprimer » dès le premier clic, il suffit de recliquer pour confirmer.
