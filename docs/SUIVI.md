# Suivi Neva : état à la v1.75

Fiche pour reprendre le projet dans une nouvelle conversation. Branche : `claude/dagoma-neva-marlin-b6ktj3` (dépôt poy74fl/Neva).

## Machine
Dagoma Neva (delta), carte BTT SKR 1.4 (LPC1768), 4 × TMC2209, écran BTT Mini 12864 V2, sonde SuperPINDA derrière la buse (X0 Y23), extrudeur BMG Bowden côté droit (+X), sans plateau chauffant, sans ventilateur pour l'instant. Marlin 2.1.2.5, PlatformIO sur Mac, Simplify3D pour le terminal, PrusaSlicer pour le slicing. Alimentation 12 V. Le firmware se flashe uniquement par la carte SD de la carte mère (`firmware.bin`, 12 V seulement). Toujours décompresser le zip en entier (remplacer un seul dossier sous Finder efface le reste).

## Firmware stable : v1.75
Zip : `Marlin-Neva-v1.75-complet.zip`. « Calibration auto » (`G28`, `G33`, `M500`) fonctionne avec la v1.74 (confirmé par l'utilisateur) ; `G29` complet à confirmer.
- Palpage : sonde limitée à 75 mm du centre (`NEVA_PROBE_MAX_RADIUS 75`, `PROBING_MARGIN` 25) ; pour affiner sans nouvelle version : `G33 R<mm>`, `G29 L R F B`.
- Version affichée sous le logo et au démarrage (`NEVA_FW_VERSION`) ; relancer `make_bootscreen.py` à chaque changement. Config : `marlin-config/`, correctifs : `marlin-patches/` (voir `README.md`). Points clés :
- `M851 Z` = **−1,233** (réglé au babystep par l'utilisateur, enregistré dans l'EEPROM ; −1,195 lors de la validation des `M421`).
- Calibration `G33` : écart-type environ 0,03. Hauteur 312,06, rayon 91,34 (valeurs en EEPROM, ne pas faire `M502`).
- Palpage : `MULTIPLE_PROBING 2`, approche 30 mm/s, mesure 8 mm/s, la tête remonte à 30 mm après `G29` (`Z_AFTER_PROBING`).
- Maillage 7 × 7, lu avec le décalage de la sonde (`NEVA_MESH_SHIFT`), fondu du maillage à 10 mm (`ENABLE_LEVELING_FADE_HEIGHT`).
- Options : `SET_PROGRESS_MANUALLY` (`M73` de PrusaSlicer), `EMERGENCY_PARSER`, `CANCEL_OBJECTS`, `STATUS_MESSAGE_SCROLLING`, `SOUND_MENU_ITEM`, `SCROLL_LONG_FILENAMES`, tri des fichiers par date, « Imprimer le dernier ».
- Piège connu : ne **jamais** limiter la portée de la buse en palpage (v1.62 cassait `G29` : le point avant du maillage demande 100 mm).
- Piège connu : le logo de démarrage (`_Bootscreen.h`) est généré par `marlin-patches/make_bootscreen.py` ; le relancer à chaque changement de version.
- Piège connu : ajouter une option qui change la taille de l'EEPROM (ex. `SOUND_MENU_ITEM`) efface les réglages enregistrés (refaire « Calibration auto »).

## Profil PrusaSlicer
`docs/Neva_PrusaSlicer.ini` (bundle : imprimante « Dagoma Neva Marlin » + filament « PLA Neva »), forme du plateau `docs/forme_plateau.svg`, réglages dans `docs/prusaslicer_gcode.md`. Début de G-code : `G28`, `G33 P1`, `G29`, 19 `M421`, purge à X −85. Hauteur max choisie : 300 mm (la hauteur sûre est environ 312 mm au centre et 290 mm au bord).

## Défaut connu (non résolu)
Dans le coin côté BMG (X > 62, Y > −10), la buse est **0,3 à 0,6 mm trop basse**, de façon stable et reproductible, alors que la sonde mesure un plateau lisse. Mesures au papier (écart par rapport au centre) : X57 Y0 −0,10 ; X70 Y0 +0,36 ; X80 Y0 +0,63 ; X70 Y25 +0,56 ; X70 Y−25 +0,01. Éliminé : tuyau et faisceau (les soulever ne change rien), contact mécanique, feuille d'impression (tournée, la bosse reste), plaque magnétique (la plaque sous la tête est en PETG), bras et poulie X (rien d'anormal). Hypothèse restante : la tête s'incline (rotules des bras X à plus de 50° de la verticale, côté opposé à la tour X). Contournement : la forme de plateau exclut ce coin.

## Plaque : mesures sur la photo (v1.73)
Rond imprimé 200 mm (centre validé par l'utilisateur), feuille en hexagone dont les bords plats sont à 103 à 108 mm du centre, coins coupés à 133 à 142 mm. Le palpage est limité à `NEVA_PROBE_MAX_RADIUS 75` mm pour la sonde (v1.74 ; 85,5 mm échouait encore) (observé : échecs à 89,2 et 89,6 mm alors que la photo montre de la place ; cause non établie). Image : `docs/plaque_palpage.jpg`.

## Feuille triangulaire : hypothèse abandonnée (v1.69)
On avait déduit que les côtés de la feuille étaient à ~75 mm du centre. C'est faux : sur les photos la feuille dépasse de 15 à 20 mm l'anneau de 85 mm dans toutes les directions et couvre le disque de 200 mm. La sonde est bien sur la feuille au point qui échoue (X −85, Y +27) : la cause du `Probing Failed` reste inconnue. Constat : les deux seuls échecs de `G29` sont à 89,2 et 89,6 mm du centre (la sonde est alors dans le vide), tout ce qui est à 85 mm ou moins réussit. v1.72 : « Calibration auto » = `G33 R20` (sonde à 65,5 mm du centre au plus ; sans R, 85,5 mm : la sonde sort de la plaque pendant `G33`, cause exacte non établie). v1.71 : `PROBING_MARGIN 14.5` (sonde limitée à 85,5 mm du centre), `G33` standard (cercle de 62,5 mm), plateau PrusaSlicer = disque de 190 mm.

## Piste initiale : le bord de la feuille triangulaire
Pendant « Calibration auto », l'utilisateur voit la **sonde sortir de la feuille du côté du BMG** : les points de `G33` sont à 30°, 90°, 150°, 210°, 270°, 330° sur un cercle de 67 mm (sonde), et le côté du triangle est le plus proche du centre dans les directions 30°, 150°, 270°. Le coin BMG où la buse est trop basse (X > 62, Y > −10) est donc peut-être le **bord de la feuille** (relevé, et mal vu par la sonde à induction). La rotation de 120° n'a rien changé parce qu'un triangle tourné de 120° se pose au même endroit. Test proposé : enlever la feuille, `G28`, `G29`, puis mesure au papier (centre, `X80 Y0`, `X70 Y25`) sur la base nue. Si l'écart disparaît, limiter `G33` (`PROBING_MARGIN` plus grand, par exemple 20 → cercle de 57 mm) et la zone de `G29` à ce que la feuille couvre ; il faut aussi la distance centre-bord de la feuille aux directions 30°, 150° et 270°.

## Prochaine expérience : sonder avec la buse
Idée : `SENSORLESS_PROBING` (delta + TMC2209) pour mesurer la hauteur de la buse elle-même, sans décalage de sonde. Limites : précision probablement 0,1 à 0,2 mm, couple faible en 12 V, buse propre et froide, remplace **tout** le palpage (`G33` et `G29`). À faire comme **firmware de test séparé** (zip distinct, ne pas modifier la v1.67), pour cartographier le coin BMG sans papier. Garder une copie de `firmware.bin` v1.67 pour revenir en arrière. Si la calibration est perdue : « Calibration auto » (menu Tests : `G28`, `G33`, `M500`).

## Fichiers de test utiles
`docs/test_spirale_r85_complete_corr_v11.gcode` (contrôle avec les corrections actuelles), `docs/test_spirale_r85_complete_sans_corr.gcode`, `docs/zones_plateau.png` (carte des zones 1 à 8, anneaux A/B, centre C), `docs/overlay_zones.py` (colle les zones sur une photo).

## Habitudes de travail
Réponses en français, courtes ; ne pas boucler sur des tests ; l'utilisateur flashe quand il le décide ; ne jamais envoyer `M502` ; ne jamais déplacer un chariot seul ; vérifier `M851` avant un test.
