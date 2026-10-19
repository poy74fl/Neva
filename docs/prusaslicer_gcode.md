# Réglages PrusaSlicer pour la Neva

À faire **une seule fois**, dans *Réglages de l'imprimante* (Printer Settings), puis enregistrer le profil.

## Général
- **Forme du plateau** : *Personnalisée*, importer `docs/forme_plateau.svg` : disque de 170 mm coupé par les trois côtés de la feuille triangulaire à 58 mm du centre (côtés à 75 mm, bord relevé exclu). Origine **0, 0**. Sinon colle à la main la ligne de `docs/forme_plateau_bed_shape.txt` dans le fichier de profil.
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
M421 I3 J1 Q-0.03
M421 I2 J2 Q-0.03
M421 I3 J2 Q-0.06
M421 I4 J2 Q-0.03
M421 I1 J3 Q-0.03
M421 I2 J3 Q-0.06
M421 I3 J3 Q-0.08
M421 I4 J3 Q-0.06
M421 I2 J4 Q-0.03
M421 I3 J4 Q-0.06
M421 I4 J4 Q-0.03
M421 I4 J5 Q-0.06
M421 I4 J6 Q-0.06
M109 S{first_layer_temperature[0]}
G1 Z5 F3000
G1 X-85 Y0 F6000
G1 Z0.3 F600
G1 E10 F200
G1 E-1 F1800
G1 Z5 F3000
```
Il fait : lancement de la chauffe (`M104`, la buse chauffe pendant le reste), homing, correction de la hauteur au centre (`G33 P1`), **palpage du plateau en plusieurs points (`G29`)**, **treize corrections du maillage (`M421`)** déterminées avec `docs/test_spirale_r85_complete_corr_v11.gcode` (centre et anneau milieu un peu plus écrasés, arrière gauche/droite ajustés, la zone du bord BMG, qui n'est plus imprimée, n'est plus corrigée), attente de la température (`M109`), puis une goutte de purge sur le bord gauche (X -85) avant de commencer.

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
