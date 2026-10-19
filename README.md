# Dagoma Neva : Marlin 2.1.2.5 pour BTT SKR 1.4 (LPC1768)

Configuration de départ pour une Neva d'origine (delta, 12 V) avec une carte **BTT SKR 1.4** (non Turbo),
des drivers **TMC2209 V1.3**, un écran **BTT Mini 12864 V2**, deux ventilateurs et une sonde **PINDA**.
Basée sur l'exemple `delta/generic` de **Marlin 2.1.2.5** (tag officiel : ces fichiers ne fonctionnent pas avec une autre version), avec :

- `MOTHERBOARD BOARD_BTT_SKR_V1_4`, USB (`SERIAL_PORT -1`)
- Drivers `TMC2209` (UART) sur X, Y, Z, E0, 800 mA, 16 micropas
- Écran `BTT_MINI_12864` sur EXP1 + EXP2 (nappes standard) et `SDSUPPORT` : avec un écran, la SKR 1.4 utilise par défaut la **SD de l'écran**
- `EEPROM_SETTINGS` activé (nécessaire pour garder la géométrie delta avec `M500`)
- Ventilateurs : pièce sur FAN0, hotend automatique sur FAN1 (`E0_AUTO_FAN_PIN`)
- Sonde `FIX_MOUNTED_PROBE` + calibration `G33`
- Extrudeur BMG en Bowden sur E0 (`415` pas/mm pour un moteur 1,8°, à adapter à ton moteur) ; pas de plateau chauffant (`TEMP_SENSOR_BED 0`)
- Options activées : `TMC_DEBUG` + `MONITOR_DRIVER_STATUS`, `BABYSTEPPING` + `BABYSTEP_ZPROBE_OFFSET`, `PROBE_OFFSET_WIZARD`, `MULTIPLE_PROBING 3`, `FILAMENT_LOAD_UNLOAD_GCODES`, `PID_EDIT_MENU` + `PID_AUTOTUNE_MENU`, `SHOW_REMAINING_TIME`, `S_CURVE_ACCELERATION`, `LIN_ADVANCE` (K = 0,22 par défaut, à régler avec `M900 K…` : un Bowden de 870 mm demande une valeur plus haute), `FAN_KICKSTART_TIME 100`
- Vitesses, accélérations et homing (50 mm/s) volontairement prudents

> **État : non compilée.** Le réseau de la session bloquait le téléchargement de PlatformIO.
> Les valeurs marquées `NEVA:` sont des estimations que je n'ai pas pu confirmer : le dépôt
> `dagoma3d/Marlin` ne contient pas de config Neva.

## 1. Récupérer les vraies valeurs de ta Neva (avant de débrancher l'ancienne carte)

Connecte l'imprimante (Pronterface, OctoPrint, Cura…) et envoie `M503`. Note surtout :

| Commande | À reporter dans `Configuration.h` |
|---|---|
| `M92` | `DEFAULT_AXIS_STEPS_PER_UNIT` (X/Y/Z : modifier `XYZ_PULLEY_TEETH` (20 dents = 80 pas/mm), E : 4e valeur) |
| `M665` L / R / H | `DELTA_DIAGONAL_ROD` / `DELTA_RADIUS` / `DELTA_HEIGHT` |
| `M666` | `DELTA_ENDSTOP_ADJ` |
| `M301` ou `M303` | PID du hotend (`DEFAULT_Kp/Ki/Kd`), sinon lance `M303 E0 S200 C8 U1` |

Envoie aussi `M119` (état des fins de course) et note le type de capteur de Z utilisé par ta Neva.
Si tu as le `Configuration.h` de l'ancien firmware, c'est encore mieux : envoie-le-moi.

## 2. Ce qu'il reste à régler pour ta machine

1. Valeurs `NEVA:` de `Configuration.h` (géométrie delta, rayon imprimable, dents des poulies).
2. `TEMP_SENSOR_0` (1 = thermistance 100k standard, valeur retenue après vérification sur la machine ; 1047 = Pt1000 sur la SKR 1.4) et `TEMP_SENSOR_BED` si plateau chauffant.
3. **Sonde PINDA** : `NOZZLE_TO_PROBE_OFFSET` à mesurer, sens du signal (`Z_MIN_PROBE_ENDSTOP_INVERTING`) à vérifier avec `M119`.
4. Sens des moteurs (`INVERT_X/Y/Z_DIR`, `INVERT_E0_DIR`) et type des fins de course (`*_ENDSTOP_INVERTING`).


## 3. Câblage SKR 1.4 pour un delta

- **Homing sensorless en haut** (X, Y, Z) : pas de fins de course mécaniques. Garde les jumpers **DIAG** posés sur X, Y et Z : le DIAG du driver arrive sur X-STOP, Y-STOP, Z-STOP, que Marlin utilise comme ports **MAX** (`*_MAX_ENDSTOP_INVERTING false` pour les TMC2209 : DIAG passe à HIGH au décrochage). Ne branche rien d'autre sur ces ports.
- Sonde de température (thermistance 100 k) sur `TH0`, chauffe sur `HE0`, plateau chauffant éventuel sur `T0`/`HB`. Vérifie sur la sérigraphie de ta carte.
- Ventilateurs : **FAN0** = ventilateur de pièce (`M106`/`M107`) ; **FAN1** = ventilateur de la hotend, automatique : il démarre au-dessus de 50 °C et s'arrête quand la buse refroidit. Vérifie leur tension (12 V ou 24 V comme l'alimentation).
- Alimentation : vérifie 12 V vs 24 V avant de brancher.
- **Drivers TMC2209 V1.3 en UART :** consulte la doc BTT pour les jumpers à retirer sous les drivers et la configuration du mode UART sur la SKR 1.4. Après flash, `M122` doit afficher les drivers sans erreur de communication. Si l'UART ne marche pas, remplace `TMC2209` par `TMC2209_STANDALONE` dans `Configuration.h` : le courant se règle alors avec le potentiomètre (Vref) et les micropas avec les jumpers.

### Sensorless : réglage

Config : `SENSORLESS_HOMING`, `X/Y/Z_STALL_SENSITIVITY 75` (réglé sur la machine, tête montée), `HOMING_BUMP_MM { 3, 3, 3 }` + `HOMING_BUMP_DIVISOR { 2, 2, 2 }` (double contact comme sur l'ancienne Neva),
`IMPROVE_HOMING_RELIABILITY`. Courants de homing identiques sur les 3 tours, et les moteurs ne sont pas coupés à l'arrêt (pas de `DISABLE_X/Y/Z`).

1. Place les chariots au milieu des tours à la main, bras libres, plateau dégagé.
2. `G28` avec la main sur l'alimentation. Si une tour ne s'arrête pas au sommet, augmente la sensibilité (`M914 X Y Z <valeur>`, 0 à 255 pour un TMC2209). Si elle s'arrête en route, diminue-la.
3. Les trois tours doivent s'arrêter au même niveau : sinon ajuste chaque valeur séparément.
4. Quand c'est bon, reporte les valeurs dans `Configuration_adv.h` ou fais `M500`.

Attention : en 12 V le couple est limité, ce qui rend le sensorless moins fiable qu'en 24 V. Si le homing n'est pas fiable, la solution la plus sûre est des fins de course mécaniques (adapter `*_MAX_ENDSTOP_INVERTING` selon leur type).

## 3b. Écran BTT Mini 12864 V2

Brancher les deux nappes de l'écran sur **EXP1** et **EXP2** de la SKR 1.4. Le BTT Mini 12864 V2 se comporte comme un FYSETC Mini 12864 2.1 pour Marlin. Respecte l'ergot et le sens, en particulier que la nappe EXP1 de l'écran aille sur EXP1 et l'EXP2 sur EXP2. Vérifie sur la doc BTT : certains écrans demandent d'inverser les nappes.
Le lecteur SD de l'écran est utilisé pour imprimer. Pour flasher le firmware, c'est le lecteur de la carte mère (voir ci-dessous).

## 3c. Sonde inductive

Config : `FIX_MOUNTED_PROBE` sur le connecteur **PROBE** (P0.10), calibration delta `G33` et menu de calibration activés.
Le Z est toujours référencé sur la butée de la tour Z (pas sur la sonde).

- **Alimentation :** la plupart des capteurs inductifs (LJ12A3, etc.) demandent 6-36 V, et leur sortie est au niveau de leur alimentation, donc **12 V**. Les entrées de la carte sont en 3,3 V. **Ne relie jamais la sortie directement à P0.10** : utilise un pont diviseur, un optocoupleur ou un module de conversion de niveau. Choisis plutôt un capteur 5 V ou conçu pour carte 3D (type PINDA ou LJ18A3 avec module).
- **Type de sortie :** NPN-NO : `Z_MIN_PROBE_ENDSTOP_INVERTING true` (valeur actuelle) ; PNP ou NC : `false`. Vérifie avec `M119` : `z_probe: TRIGGERED` doit apparaître seulement quand un métal passe devant.
- **Plateau :** un inductif ne détecte que le métal. Si ton plateau est en verre, il faut une plaque métallique dessous.
- **Offsets :** mesure la distance buse -> sonde en X, Y (`NOZZLE_TO_PROBE_OFFSET`) et règle Z avec `M851` / l'écran. Les valeurs actuelles sont des estimations.
- **Rayon de sonde :** avec le décalage en Y, vérifie que la zone sondée ne sort pas du plateau.

### SuperPINDA : points d'attention

- **Modèle :** c'est une SuperPINDA (celle de la Prusa MK3S) : 3 fils (+5 V, GND, signal), **sans thermistance**, conçue pour peu dériver avec la température. La calibration à chaud reste conseillée, mais c'est moins critique qu'avec une PINDA d'origine.
- **Tension :** alimente-la en **5 V** (le connecteur PROBE de la SKR 1.4 en fournit un : vérifie le brochage sur la doc BTT avant de brancher). Jamais en 12 V.
- **Niveau du signal :** mesure au multimètre la tension du fil signal (métal près de la sonde / pas de métal) avant de la relier à P0.10. Les entrées de la LPC1768 tolèrent en principe 5 V, mais vérifie la doc BTT.
- **Sens :** teste avec `M119` : `z_probe` doit passer à `TRIGGERED` quand tu approches un métal, et seulement dans ce cas. Si c'est inversé, change `Z_MIN_PROBE_ENDSTOP_INVERTING` (`true` / `false`).
- **Portée :** quelques mm sur de l'acier, moins sur de l'aluminium. Le Z de `NOZZLE_TO_PROBE_OFFSET` se règle avec l'assistant du menu (`PROBE_OFFSET_WIZARD`) ou avec le test du papier et `M851`.

## 3d. Capteur de fin de filament

Config : `FILAMENT_RUNOUT_SENSOR` sur le port **E0-DET** de la SKR 1.4 (broche P1.26, imposée par le fichier de pins de Marlin), script `M600` (changement de filament), buse parquée pendant la pause.

- **Retire le jumper DIAG de l'E0 :** il est sur la même broche et enverrait le signal du driver dans le capteur.
- **Conflit possible avec le sensorless :** avec le homing sensorless en haut, Marlin réutilise aussi P1.26 comme « fin de course min » de X. Le capteur ne gêne pas les impressions, mais teste `G28` après installation : si une tour s'arrête bizarrement en redescendant, c'est que le capteur est lu comme un X-MIN. La solution serait de changer la broche dans le fichier de pins de Marlin.
- **Sens du signal :** `M119` doit afficher `filament: ` (ou `E0 ...`) avec un état différent selon que le filament est présent ou non. Si c'est inversé, change `FIL_RUNOUT_STATE` (`LOW`/`HIGH`).
- **Bowden :** règle `FILAMENT_CHANGE_UNLOAD_LENGTH` et `FILAMENT_CHANGE_FAST_LOAD_LENGTH` (valeurs d'exemple 500/450 mm) sur la longueur réelle de ton tube.
- **Capteur KW12 (microswitch mécanique) :** pas d'alimentation à brancher. Relie deux fils seulement : **COM** à GND et **NO** au signal du port E0-DET (pas au 5 V), avec le levier enfoncé par le filament. Config : `FIL_RUNOUT_STATE HIGH` + pull-up interne. Attention au sens de `M119` : `filament: TRIGGERED` veut dire **filament présent**, `open` veut dire **plus de filament**.
  Le montage COM+NO est « sécurisé » : un fil coupé est lu comme « plus de filament » et arrête l'impression, au lieu de passer inaperçu. Ne câble pas la borne NC.

## 4. Compiler et flasher

```bash
git clone --branch 2.1.2.5 https://github.com/MarlinFirmware/Marlin.git
cp marlin-config/Configuration.h marlin-config/Configuration_adv.h Marlin/Marlin/
cd Marlin && pio run -e LPC1768
```

Le firmware est dans `.pio/build/LPC1768/firmware.bin`. Copie-le à la racine d'une carte microSD (FAT32),
mets-la dans le lecteur **de la carte mère** (le bootloader ne lit pas la SD de l'écran), nomme-le `firmware.bin`
et redémarre : le fichier devient `FIRMWARE.CUR`. Utilise un nouveau nom de fichier à chaque flash.
Tu peux aussi utiliser VS Code + l'extension Auto Build Marlin.

## 4b. Menu principal réorganisé (patch du code de Marlin)

L'ordre du menu est écrit dans le code de Marlin, pas dans la config. Le dossier `marlin-patches/` contient sept fichiers à copier **par-dessus** ceux de Marlin 2.1.2.5 :

| Fichier du dépôt | À copier dans Marlin-2.1.2.5/ |
|---|---|
| `marlin-patches/Marlin/src/lcd/menu/menu_main.cpp` | `Marlin/src/lcd/menu/menu_main.cpp` |
| `marlin-patches/Marlin/src/lcd/language/language_fr.h` | `Marlin/src/lcd/language/language_fr.h` |
| `marlin-patches/Marlin/src/lcd/marlinui.cpp` | `Marlin/src/lcd/marlinui.cpp` (atténuation auto du rétroéclairage, diff dans `marlin-patches/dim-led.diff`) |
| `marlin-patches/Marlin/src/lcd/dogm/marlinui_DOGM.cpp` | `Marlin/src/lcd/dogm/marlinui_DOGM.cpp` (supprime l'écran Marlin qui suit le logo, diff dans `marlin-patches/boot-sans-marlin.diff`) |
| `marlin-patches/Marlin/src/gcode/sd/M24_M25.cpp` | `Marlin/src/gcode/sd/M24_M25.cpp` (refuse de lancer une impression SD sans filament : message « Charger le filament ! », diff dans `marlin-patches/bloque-sans-filament.diff`) |
| `marlin-patches/Marlin/src/feature/tmc_util.cpp` | `Marlin/src/feature/tmc_util.cpp` (StallGuard des TMC2209 dans `M122 S1` + affichage des courroies sur l'écran, diff dans `marlin-patches/tmc-courroies.diff`) |
| `marlin-patches/Marlin/_Bootscreen.h` | `Marlin/_Bootscreen.h` (logo de démarrage « Fake Prusa PRO HT-ish », à côté de `Configuration.h`) |

**Atténuation automatique de l'écran** : sans action sur la molette pendant `NEVA_LED_DIM_TIMEOUT_S` secondes (60 par défaut, au repos comme en impression), le rétroéclairage passe à `NEVA_LED_DIM_BRIGHTNESS` (20 sur 255) ; il revient dès que tu tournes ou appuies sur la molette, et reste à pleine luminosité tant qu'un message attend ta réponse (fin d'impression en vert, changement de filament…). Réglages dans `Configuration_adv.h` ; commente `NEVA_LED_DIM_TIMEOUT_S` pour désactiver (le patch `marlinui.cpp` reste alors inactif).

**Menu « Tests »** (en bas du menu principal, au repos) : scripts G-code intégrés au firmware, « Test 1ere couche » (carré de 60 × 60 mm, PLA 210 °C, ventilateur coupé) et « Test filament » (extrusion de 100 mm mesurée). Ils sont aussi dans `docs/test_premiere_couche.gcode` et `docs/test_filament.gcode`. Réglage dans `Configuration_adv.h` (`CUSTOM_MENU_MAIN`).

**Palpage du plateau (maillage)** : `AUTO_BED_LEVELING_BILINEAR`, grille 7 × 7 sur le disque de rayon 77 mm (`PROBING_MARGIN 20`, limité par le décalage de la sonde de 23 mm), soit 29 points. Chaque G-code de test et le G-code de début du slicer enchaînent `G28`, `G33 P1` (hauteur), `G29` (maillage), puis la chauffe ; `G29` active la correction pour toute l'impression. Après le flash : `M502`, `M500`. `G28` désactive le maillage ; `M420 V1` l'affiche.

**Test des courroies** (menu « Tests » > « Test courroies », ou `docs/test_courroies.gcode`) : les 3 chariots montent et descendent ensemble (Z 60 ↔ 200 mm, à 30 puis 60 mm/s) pendant que `M122 S1 P250` lit le `sg` (StallGuard) de chaque TMC2209. **L'écran affiche (rafraîchi toutes les 2 s) la moyenne de chaque tour et l'écart maximal : `X180 Y177 Z183 e7%`** (e = écart max / moyenne), et le résultat reste affiché à la fin (patch `tmc_util.cpp`, diff dans `marlin-patches/tmc-courroies.diff`). Les mêmes valeurs sortent sur le port série ; `python3 docs/test_courroies.py` (pyserial) calcule en plus un résumé détaillé (montée/descente, 30/60 mm/s) et ajoute les mesures à `docs/mesures_courroies.csv`. Résultat relatif (3 tours entre elles, ou avant/après réglage), pas une tension en newtons ; seuils 10 % / 25 % provisoires. Sans le patch, Marlin affiche « - » à la place du `sg` sur TMC2209.

**Chargement automatique au repos** : machine au repos, quand le filament arrive devant le capteur, la buse chauffe à `NEVA_AUTOLOAD_TEMP` (210 °C) puis `M701` charge le filament. Patch dans `marlinui.cpp` ; commente `NEVA_AUTOLOAD_TEMP` dans `Configuration_adv.h` pour désactiver.

**Version de ton firmware** : `NEVA_FW_VERSION` (dans `Configuration.h`, incrémenté à chaque mise à jour poussée sur la branche) s'affiche sur la ligne du bas de l'écran de contrôle au démarrage (« Fake Prusa fw v1.59 », via `STARTUP_COMMANDS` / `M117`). Il est aussi dans l'étiquette `(NEVA-vX.Y)` visible dans `M115` et au démarrage. Depuis la v1.65 : `SET_PROGRESS_MANUALLY` (la commande `M73` de PrusaSlicer fixe le pourcentage et le temps restant affichés), `EMERGENCY_PARSER` (`M112`, `M108`, `M410` immédiats, même file pleine), `STATUS_MESSAGE_SCROLLING`, `SOUND_MENU_ITEM` (entrée « Sons » du menu pour couper le bip), `ENABLE_LEVELING_FADE_HEIGHT` (correction du maillage estompée jusqu'à 10 mm de hauteur), `CANCEL_OBJECTS` (`M486`, menu « Annuler objet » pendant l'impression ; dans PrusaSlicer activer « Étiqueter les objets » / *Label objects*) et `SERVICE_INTERVAL_1` (rappel « Courroies » après 100 h d'impression). `POWER_LOSS_RECOVERY` volontairement laissé désactivé. Depuis la v1.64, `SCROLL_LONG_FILENAMES` : dans le menu SD, le nom du fichier sélectionné défile quand il est trop long pour l'écran (`SDSORT_CACHE_VFATS 5` : noms jusqu'à 65 caractères gardés en RAM) ; les écrans de confirmation « Imprimer / Réimprimer … ? » affichent le nom sur plusieurs lignes (jusqu'à 47 caractères). Depuis la v1.63, `MULTIPLE_PROBING 2` (une approche rapide + une seule mesure lente par point, au lieu de deux mesures moyennées : G29 et G33 sont plus courts) et `Z_AFTER_PROBING 30` (la tête remonte à 30 mm à la fin de `G29` au lieu de rester à 5 mm). Depuis la v1.76 : rayon max de la sonde remonté à 88 mm (`NEVA_PROBE_MAX_RADIUS 88`, `PROBING_MARGIN` 12 mm) : 29 nœuds sondés sur 49 (X ±85 à Y +4, X 0 à Y +85 en plus ; les nœuds à 89,6 mm et plus restent exclus). `Probe::can_reach` refuse les points où la buse dépasse 94 mm du centre dans un secteur de ±30° autour d'une tour (X à 210°, Y à 330°) : la tête touche la tour à X −86,07 Y −49,31 (constaté), donc les nœuds X ±85 Y −23 ne sont pas sondés. « Calibration auto » = `G33 R13` : même cercle de 52 mm qu'en v1.74 et v1.75. Depuis la v1.75 : `G29` repasse (la v1.74 répondait « ? (L,R,F,B) out of bounds. ») : `Probe::good_bounds` ne vérifie plus que la portée de la buse sur les bords du maillage (±85) ; les nœuds où la sonde dépasserait 82 mm sont toujours écartés un par un pendant `G29` et extrapolés. Rayon max de la sonde remonté à 82 mm (`NEVA_PROBE_MAX_RADIUS 82`, `PROBING_MARGIN` 18 mm) : 25 nœuds sondés sur 49. « Calibration auto » = `G33 R7` (cercle de la buse à 52 mm, sonde à 75 mm au plus, comme la v1.74). Depuis la v1.74 : rayon max de la sonde réduit de 85,5 à 75 mm (`NEVA_PROBE_MAX_RADIUS 75`, `PROBING_MARGIN` 25 mm) : la sonde sortait encore de la plaque à 85,5 mm ; il reste 21 nœuds sondés sur 49, les autres sont extrapolés. « Calibration auto » = `G33` simple (cercle de la buse à 52 mm, sonde à 75 mm au plus). Depuis la v1.73 : bloc « Plaque Neva » dans `Configuration.h` avec les mesures prises sur la photo (rond imprimé de 200 mm centré sur X0 Y0, bords plats à 103 à 108 mm du centre) ; `NEVA_PROBE_MAX_RADIUS 85.5` règle le rayon maximal de la sonde (`PROBING_MARGIN` en découle) : pour élargir le palpage, il suffit de monter cette seule valeur. Depuis la v1.72 : « Calibration auto » fait `G33 R20` : la buse palpe sur un cercle de 42,5 mm et la sonde, 23 mm derrière, reste à 65,5 mm du centre au plus (sans R, 85,5 mm : la sonde sortait de la plaque pendant `G33`). Depuis la v1.71 : `PROBING_MARGIN 14.5` : la sonde ne va pas à plus de 85,5 mm du centre. Elle échoue (« Probing Failed ») vers 89 à 90 mm (échecs constatés à 89,2 et 89,6 mm) alors que tous les points à 85 mm ou moins réussissent. Le cercle de palpage de `G33` passe à 62,5 mm. La règle des deux nœuds de la v1.70 est retirée ; la zone d'impression reste le disque de 190 mm. Depuis la v1.67 : `NOZZLE_TO_PROBE_OFFSET` Z par défaut à −1,233 (−1,195 lors de la validation des `M421`, puis −1,233 réglé au babystep par l'utilisateur ; la valeur enregistrée dans l'EEPROM l'emporte sur ce défaut) (valeur réglée sur la machine). Zone d'impression : le coin côté BMG (X > 62, Y > −12) est exclu dans PrusaSlicer (`docs/forme_plateau.svg`), la buse y est 0,3 à 0,6 mm trop basse sans que la sonde le voie. La v1.62 limitait la buse à 95 mm du centre en palpage : c'était une erreur (le point avant du maillage demande 100 mm, `G29` s'arrêtait en « out of bounds » et le print partait sans maillage). Retirée en v1.66. Depuis la v1.61, le message d'accueil de l'écran de contrôle (`WELCOME_MSG`, `language_fr.h`) est lui-même « Fake Prusa fw vX.Y » : la version reste visible en permanence, même quand le message `M117` du démarrage a expiré. Depuis la v1.60, elle est aussi affichée sous le logo de l'écran de démarrage : `marlin-patches/make_bootscreen.py` lit `NEVA_FW_VERSION` dans `Configuration.h` et régénère `_Bootscreen.h` — relancer `python3 marlin-patches/make_bootscreen.py` à chaque changement de version.

Le logo de démarrage (`SHOW_CUSTOM_BOOTSCREEN`) se refait avec `python3 marlin-patches/make_bootscreen.py` (logo par défaut « PRUSA PRO HT-ish », `--texte` pour le texte seul, `--neva` pour « DAGOMA NEVA », aperçu dans `docs/bootscreen_apercu.png`) ou `python3 marlin-patches/make_bootscreen.py mon_logo.png` pour ta propre image (convertie en noir et blanc, 128×64).

Ordre obtenu (hors impression) : 1 Surveiller, 2 Préchauffage (ex-Température), 3 Impr. depuis la SD, 4 Actualiser média, 5 Changer filament, 6 Configuration, 7 Mouvement, 8 Lumière, 9 Infos imprimante.

**Écran qui bugue dans le menu SD (v1.38)** : l'écran et la SD partagent les fils SCK/MOSI. Avant, la carte était relue à chaque rafraîchissement de l'écran (pas de tri) et, avec `NO_SD_DETECT`, l'écran n'était jamais réinitialisé après un accès SD. Maintenant : liste triée en RAM une seule fois (`SDCARD_SORT_ALPHA` + `SDSORT_CACHE_NAMES`), `REINIT_NOISY_LCD` forcé, et l'entrée « Impr. depuis la SD » lit la carte puis réinitialise l'écran avant d'ouvrir la liste.

**Dossier seul dans la liste SD (v1.39)** : avec le tri en RAM, si un dossier était le seul élément de la liste (par ex. un dossier `tests` seul sur la carte), Marlin le prenait pour un fichier et proposait de l'imprimer. Correctif dans `Marlin/src/sd/cardreader.cpp` (diff : `marlin-patches/cardreader-dossier-seul.diff`).

**Plus besoin d'« Actualiser média » (v1.40)** : sans détection de carte, la SD n'était lue qu'après « Actualiser média ». Maintenant « Impr. depuis la SD » remonte la carte (M21) à chaque ouverture, puis réinitialise l'écran. « Actualiser média » reste disponible.

**« Imprimer » sélectionné d'office (v1.41)** : à l'écran de confirmation après le choix d'un fichier, « Imprimer » est déjà sélectionné (avant : « Annuler »). Il suffit de recliquer pour lancer ; tourner la molette change de choix. Patch : `Marlin/src/lcd/menu/menu_media.cpp`.

**Test courroies : résultat figé à l'écran (v1.42)** : le résultat final (X, Y, Z, écart) est mémorisé et affiché sur l'écran « COURROIES: FINI » jusqu'au prochain test, même si les compteurs sont remis à zéro ensuite. Il est aussi toujours envoyé sur le port série (`Courroies: X… Y… Z… e…%`).

**Palpage plus lent (v1.43)** : la sonde descendait à 200 mm/s (approche) puis 100 mm/s (mesure), ce qui pouvait faire bouger la tête et fausser la mesure. Maintenant 30 mm/s pour l'approche et 5 mm/s pour la mesure finale (`Z_PROBE_FEEDRATE_FAST/SLOW`). Un `G29` et un `G33` prennent plus de temps ; après ce changement, refaire `G33` + `M500` et vérifier la hauteur de première couche (`M851 Z` si besoin).

**Réglage Z enregistré automatiquement (v1.44)** : quand tu quittes l'écran « Décalage Z » (double-clic sur la molette pendant l'impression, puis un clic pour sortir), les paramètres sont enregistrés comme avec `M500` (bip de confirmation). Patch : `Marlin/src/lcd/menu/menu.cpp`.

**Menu « Calibration auto » (v1.45)** : dans le menu Tests, un clic lance `G28`, `G33` puis `M500` (enregistrement). Il fonctionne sans filament. Réglages PrusaSlicer (début/fin de G-code avec `G29`) : voir `docs/prusaslicer_gcode.md`.

**Réimprimer en fin d'impression (v1.47)** : à la fin d'une impression SD, l'écran propose directement « Reimprimer <fichier> ? » avec « Imprimer » déjà sélectionné : un clic relance la même impression, tourner la molette puis cliquer annule. Le fichier doit rester dans le dossier courant de la carte (patch : `Marlin/src/lcd/menu/menu_media.cpp`, option `SD_REPRINT_LAST_SELECTED_FILE`).

**Chauffe pendant le palpage (v1.48)** : dans les tests du menu et les fichiers de `docs/`, `M104 S210` est lancé avant `G28` (la buse chauffe pendant le homing et le palpage), `M109 S210` n'attend la température qu'après `G29`. Gain : plusieurs minutes. À surveiller : la sonde chauffe un peu avec la buse ; si la hauteur de première couche change, corriger le décalage Z une fois.

**Calibration G33 sur un cercle plus large (v1.49)** : `PROBING_MARGIN` passe de 20 à 10. `G33` mesure maintenant sur un cercle de 67 mm de rayon (avant 57 mm), plus près des bords où se voit le défaut. Le maillage `G29` ne change pas (77 mm). Après avoir flashé : refaire la « Calibration auto ».

**Maillage plus large (v1.50)** : le maillage `G29` couvrait un disque de 77 mm (100 - 23, décalage de la sonde). Il couvre maintenant 85 mm (`NEVA_MESH_MARGIN 15` dans `Configuration.h`, patch `Marlin/src/module/probe.h`). Sur les côtés et à l'arrière la sonde atteint ce rayon ; à l'avant la buse devrait aller trop loin (la sonde est 23 mm derrière la buse) : ces points sont ignorés automatiquement et le maillage y est extrapolé. Grille 7×7 : environ 28 mm entre points.

**Bip plus fort, écran réparé en fin d'opération (v1.51)** : le bip de fin des tests passe à 2700 Hz / 300 ms (le buzzer de l'écran est plus fort vers 2-3 kHz). Quand la machine redevient inactive (plus de commandes ni de mouvements depuis 1,5 s) et que l'écran d'accueil est affiché, l'écran est réinitialisé une fois, ce qui répare l'affichage perturbé par les moteurs ou le bip (patch : `Marlin/src/lcd/marlinui.cpp`).

**Balayage par côtés** : `docs/scan_cotes.gcode` mesure la hauteur du plateau le long de 4 axes (droite = côté BMG, gauche, arrière, avant) jusqu'à 85 mm, pour comparer les côtés à rayon égal.

**Maillage décalé de la sonde (v1.52)** : le maillage est mesuré avec la buse 23 mm devant la sonde, mais l'erreur de la delta dépend de la position de la *buse*. Avec `NEVA_MESH_SHIFT` (`Configuration.h`, patch `Marlin/src/feature/bedlevel/abl/bbl.cpp`), le maillage est lu là où la sonde se trouvait quand la buse était à cet endroit. Effet attendu : l'avant (jusqu'à 100 mm) est couvert par le maillage au lieu d'être extrapolé, et l'arrière (test du papier : « coincé ») est mieux corrigé. Pour revenir à l'ancien comportement : commenter `#define NEVA_MESH_SHIFT`. Tests : `docs/test_papier_fin.gcode` puis la spirale.

**Correctif G29 (v1.53)** : depuis la v1.50, `G29` répondait `? (L,R,F,B) out of bounds.` et ne faisait aucun maillage (l'avant du maillage, à -85 mm, demandait à la buse d'aller à -108 mm, hors de sa course). La borne avant est maintenant -77 mm (rayon imprimable - décalage Y de la sonde). Le maillage a 33 points sondés sur 49 ; les autres sont extrapolés. En v1.50 à v1.52 : `G29 F-77` donnait le bon maillage.

**Écran qui "saute" (v1.54)** : la réinitialisation de l'écran (v1.51) se déclenchait aussi pendant un palpage ou une attente de chauffe, quand la file de commandes est brièvement vide, ce qui faisait sauter l'affichage. Elle n'a plus lieu pendant une chauffe en attente ou une impression, et seulement après 10 s d'inactivité.

**Fichiers SD du plus récent au plus ancien (v1.55)** : la liste de l'écran est triée par date de modification (le plus récent en premier, dossiers en tête ; à date égale, ordre alphabétique) au lieu de l'ordre alphabétique. Patch : `Marlin/src/sd/cardreader.cpp`. Limite : seuls les 40 premiers éléments d'un dossier (ordre de la carte) sont triés (`SDSORT_LIMIT`).

**« Imprimer » sélectionné d'office, correctif (v1.56)** : depuis la v1.41 la sélection par défaut restait sur « Annuler », car `goto_screen()` remet la sélection à zéro après l'avoir réglée. Elle est maintenant réglée au premier affichage de l'écran de confirmation (choix d'un fichier, et « Reimprimer » de fin d'impression). Patch : `Marlin/src/lcd/menu/menu_media.cpp`.

**Nom du fichier à la réimpression (v1.57)** : l'écran « Reimprimer » affichait le nom court 8.3 (`TEST_~75.GCO?`) ; il affiche maintenant le nom complet, avec un espace avant le « ? ».

**Palpage plus rapide (v1.58)** : mesure lente 8 mm/s (au lieu de 5) et dégagement entre deux mesures 3 mm (au lieu de 5). Gain estimé : 35 à 45 % sur la durée d'un `G29`. À vérifier : la hauteur de première couche et les corrections `M421` (docs/test_5_carres_correction.gcode) peuvent bouger de quelques centièmes.

**« Imprimer le dernier » (v1.59)** : nouvelle entrée du menu principal. Elle remonte la carte, prend le premier fichier (le plus récent, grâce au tri par date) de la racine, et affiche « Imprimer le dernier <fichier> ? » avec « Imprimer » déjà sélectionné. Si la racine ne contient aucun fichier : « Aucun fichier ». Patchs : `menu_media.cpp` et `menu_main.cpp`.
Pendant une impression, le menu garde ses entrées (Pause, Arrêter, Régler…). `PSU_CONTROL` est désactivé, donc « Allumer/Éteindre alim. » a disparu. Le menu « Infos imprimante » (version, carte, thermistances, statistiques) est en dernier. Le diff est dans `marlin-patches/menu-neva.diff`.

## 5. Premier démarrage (sécurité d'abord)

1. Moteurs débranchés de la tête : vérifie les températures (`M105`) et que la thermistance réagit.
2. `M119` : chaque fin de course doit passer à `TRIGGERED` quand tu le presses (et seulement à ce moment).
3. Teste chaque tour avec `G91` / petit `G1 Z5`. Si elle descend au lieu de monter, inverse `INVERT_*_DIR`.
4. `G28` avec la main prête sur l'alimentation, puis `M500`.
5. Calibre avec `G33`, puis `M500`.
