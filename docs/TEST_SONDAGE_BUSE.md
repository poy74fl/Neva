# Firmware de test T1 : palpage avec la buse (`SENSORLESS_PROBING`)

Branche : `claude/neva-test-sondage-buse` (la v1.67 stable reste sur `claude/zen-mayer-tgigb3`, intacte). Version affichée : `1.67-T6`. **Firmware d'expérience : ne pas imprimer avec.**

## Ce qui change par rapport à la v1.67
- `FIX_MOUNTED_PROBE` désactivé, `SENSORLESS_PROBING` activé : la SuperPINDA n'est plus lue. Marlin n'accepte qu'un seul type de sonde.
- `NOZZLE_TO_PROBE_OFFSET { 0, 0, 0 }` : la buse est la sonde, plus de décalage de 23 mm. `NEVA_MESH_SHIFT` désactivé (inutile).
- Le palpage lit les DIAG des 3 tours (X, Y, Z en MAX) comme le homing, avec les sensibilités `X/Y/Z_STALL_SENSITIVITY 75` et le courant de homing. `G33` calibre sur 70 % du rayon (environ 63 mm).
- Tout le reste est identique à la v1.67 (palpage 30 / 8 mm/s, `MULTIPLE_PROBING 2`, maillage 7 × 7 sur 85 mm).

## Avant de flasher
1. Garder une copie du `firmware.bin` v1.67 pour revenir en arrière.
2. Buse **propre et froide**, sans filament coulé, plateau dégagé, main sur l'alimentation 12 V.
3. Ne pas décompresser par-dessus la v1.67 : dossier à part. Flasher par la SD de la carte mère, avec un nouveau nom de fichier.

## Premiers essais (dans cet ordre, ne pas boucler)
1. `M115` doit afficher `(NEVA-v1.67-T1)`. `M119` : plus de ligne `z_probe`, les `*_max` doivent rester `open`.
2. L'EEPROM change de taille avec ce réglage : les valeurs delta peuvent revenir à celles de `Configuration.h` (pas de `M502` nécessaire). Vérifier `M851` : doit être proche de `Z0`.
3. `G28`, puis un seul `G30 X0 Y0` : la buse descend, doit s'arrêter **au contact** du plateau. Si elle ne s'arrête pas (le moteur saute), couper l'alimentation.
4. Régler la sensibilité **du palpage** avec `M914 P1 X.. Y.. Z..` (T2 : distincte de celle du homing, qui reste `M914 X75 Y75 Z75`, et non enregistrée par `M500` ; `M914 P1` seul affiche les valeurs ; défaut 100). Plus haut = déclenche plus facilement. Trop haut : déclenche en l'air. Trop bas : pousse fort sur le plateau. À 8 mm/s le signal StallGuard est plus faible qu'à 30 mm/s : si ça ne déclenche pas de façon fiable, monter `Z_PROBE_FEEDRATE_SLOW` (par exemple 15 mm/s) et recompiler.
5. Répétabilité : 5 × `G30 X0 Y0`, puis 5 × `G30 X70 Y0`. On cherche un écart de moins de 0,1 mm.
6. « Calibration auto » (menu Tests : `G28`, `G33`, `M500`), puis `G33` encore pour juger l'écart-type (v1.67 : environ 0,03).
7. **Mesure du coin BMG** : `docs/scan_cotes.gcode` (marche tel quel, `G30` est maintenant à la position de la buse). Comparer à la carte au papier du SUIVI (X70 Y0 +0,36 ; X80 Y0 +0,63). Si la buse mesure aussi ce creux, c'est la tête qui s'incline ; si elle ne le voit pas, c'est un défaut de la SuperPINDA.

## Retour à la v1.67
Reflasher le `firmware.bin` v1.67 (nouveau nom de fichier), puis « Calibration auto ». Vérifier `M851 Z` (−1,233) avant tout test.

## Historique des essais
- **T1** : `G30 X0 Y0` → `Probing Failed` (la buse touche le plateau sans déclencher à la sensibilité 75). Monter la sensibilité à 100 avec `M914` fait échouer `G28` (les tours s'arrêtent en route) : la sensibilité du homing et celle du palpage ne peuvent pas être communes.
- **T2** : sensibilités séparées (`M914 P1`, patch `marlin-patches/palpage-sensibilite.diff`, fichiers `module/probe.cpp` et `gcode/feature/trinamic/M911-M914.cpp`).
- **T2, résultat** : `Probing Failed` même à la sensibilité 220 (la buse touche le plateau). La sensibilité n'est donc pas la cause.
- **T3** : cause trouvée dans Marlin 2.1.2.5 (`module/endstops.cpp`). Pendant le palpage la buse **descend** (sens « − »), or Marlin ne teste dans ce sens que les ports MIN. Le DIAG des TMC2209 est sur les ports MAX (homing en haut), et le port X-MIN est en fait E0-DET (le capteur de filament). Le calage n'était donc jamais lu. Correctif (`marlin-patches/palpage-descente-max.diff`, `module/endstops.cpp`) : pendant la descente de palpage seulement, on teste aussi X/Y/Z-MAX et on ignore les ports MIN.
- **T3, résultat** : à 140 le palpage déclenche (Z −1,70, la buse a enfoncé le plateau de 1,5 mm) mais pas à chaque fois ; à 160, 180 et 200 la tête s'arrête **en l'air** (faux déclenchement du StallGuard à l'accélération du départ). Pas de plage de sensibilité fiable.
- **T4** : le StallGuard est ignoré sous une vitesse minimale (`TCOOLTHRS`, 15 mm/s par défaut, réglable `M914 P1 S..`), ce qui masque l'accélération du départ. En contrepartie le palpage se fait en une seule mesure à 20 mm/s (`MULTIPLE_PROBING` désactivé, car Marlin refuse la valeur 1 ; `Z_PROBE_FEEDRATE_SLOW` et `_FAST` à 20 mm/s), car sous ~15 mm/s le signal n'est de toute façon pas exploitable. Sensibilité de palpage par défaut 120.
- **T4b** : correction de compilation (`MULTIPLE_PROBING 1` est refusé par Marlin : « must be 2 or more »), `Z_PROBE_FEEDRATE_FAST` = `SLOW` pour supprimer la pré-descente rapide jusqu'à Z20.
- **T4b, résultat** : la tête s'arrête encore en l'air.
- **T4c** : ajoute une ligne de diagnostic après chaque mesure (`Palpage: depart Z.. arret Z.. declenche X.. Y.. Z.. | DIAG au depart .. a la fin ..`) pour savoir quelle tour déclenche, à quelle hauteur, et si un DIAG est déjà actif avant de partir.
- **T4b, résultat** : à la sensibilité 80 le palpage déclenche à Z −1,84 (±0,01 mm sur 5 mesures, au centre comme à X70). Le balayage `docs/scan_buse_coin_bmg.gcode` ne retrouve pas la carte au papier : X57 +0,33, X70 −0,04, X70 Y25 +0,08, Y70 +0,48, X80 échoue. La buse enfonce le plateau d'environ 1,8 mm avant que le moteur cale (souplesse des courroies et des bras), et cet enfoncement varie avec la position.
- **T5** : courant moteur propre au palpage (`NEVA_PROBE_CURRENT`, 500 mA par défaut au lieu de 800 ; `M914 P1 C..` pour le régler, 0 = courant normal). Moins de courant = moins d'effort de la buse sur le plateau, donc moins d'enfoncement. Le courant normal est restauré après chaque mesure. Critère : X57 vers −0,1, X70 vers +0,36, X70 Y25 vers +0,56 (carte au papier). Sinon on arrête.
- **T5, résultat** : avec 500 mA le palpage s'arrête en l'air à 120, puis donne Z −2,25 (sensibilité 80), −2,85 (60) et −3,23 (40) : plus profond qu'à 800 mA (−1,84). Le diagnostic montre que seule la tour Y déclenche, à Z −3,23, soit plus bas que la limite de descente (−2) : Marlin ne l'applique que si l'axe Z est « de confiance » (`axis_is_trusted`), sinon il prend −10 mm.
- **T6** : la limite de descente du palpage sensorless est toujours `-offset.z + Z_PROBE_LOW_POINT` (`module/probe.cpp`), `Z_PROBE_LOW_POINT` passe à −4 ; la ligne `Palpage:` affiche la limite utilisée (`limite Z..`) ; réglages de départ : courant normal (`NEVA_PROBE_CURRENT 0`), sensibilité 80.
