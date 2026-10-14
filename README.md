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
- Options activées : `TMC_DEBUG` + `MONITOR_DRIVER_STATUS`, `BABYSTEPPING` + `BABYSTEP_ZPROBE_OFFSET`, `PROBE_OFFSET_WIZARD`, `MULTIPLE_PROBING 3`, `FILAMENT_LOAD_UNLOAD_GCODES`, `PID_EDIT_MENU` + `PID_AUTOTUNE_MENU`, `SHOW_REMAINING_TIME`, `S_CURVE_ACCELERATION`, `LIN_ADVANCE` (K = 0,22 par défaut, à régler avec `M900 K…` : un Bowden de 1100 mm demande une valeur plus haute), `FAN_KICKSTART_TIME 100`
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
2. `TEMP_SENSOR_0` (1 = thermistance 100k standard) et `TEMP_SENSOR_BED` si plateau chauffant.
3. **Sonde PINDA** : `NOZZLE_TO_PROBE_OFFSET` à mesurer, sens du signal (`Z_MIN_PROBE_ENDSTOP_INVERTING`) à vérifier avec `M119`.
4. Sens des moteurs (`INVERT_X/Y/Z_DIR`, `INVERT_E0_DIR`) et type des fins de course (`*_ENDSTOP_INVERTING`).


## 3. Câblage SKR 1.4 pour un delta

- **Homing sensorless en haut** (X, Y, Z) : pas de fins de course mécaniques. Garde les jumpers **DIAG** posés sur X, Y et Z : le DIAG du driver arrive sur X-STOP, Y-STOP, Z-STOP, que Marlin utilise comme ports **MAX** (`*_MAX_ENDSTOP_INVERTING false` pour les TMC2209 : DIAG passe à HIGH au décrochage). Ne branche rien d'autre sur ces ports.
- Thermistance hotend sur `T1`/`TH0`, chauffe sur `HE0`, plateau chauffant éventuel sur `T0`/`HB`. Vérifie sur la sérigraphie de ta carte.
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
- **Capteur KW12 (microswitch mécanique) :** pas d'alimentation à brancher. Relie deux fils seulement : **COM** à GND et **NO** au signal du port E0-DET (pas au 5 V), avec le levier enfoncé par le filament. Config : `FIL_RUNOUT_STATE HIGH` + pull-up interne.
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

L'ordre du menu est écrit dans le code de Marlin, pas dans la config. Le dossier `marlin-patches/` contient trois fichiers à copier **par-dessus** ceux de Marlin 2.1.2.5 :

| Fichier du dépôt | À copier dans Marlin-2.1.2.5/ |
|---|---|
| `marlin-patches/Marlin/src/lcd/menu/menu_main.cpp` | `Marlin/src/lcd/menu/menu_main.cpp` |
| `marlin-patches/Marlin/src/lcd/language/language_fr.h` | `Marlin/src/lcd/language/language_fr.h` |
| `marlin-patches/Marlin/_Bootscreen.h` | `Marlin/_Bootscreen.h` (logo de démarrage « Fake Prusa PRO HT-ish », à côté de `Configuration.h`) |

Le logo de démarrage (`SHOW_CUSTOM_BOOTSCREEN`) se refait avec `python3 marlin-patches/make_bootscreen.py` (logo par défaut « PRUSA PRO HT-ish », `--texte` pour le texte seul, `--neva` pour « DAGOMA NEVA », aperçu dans `docs/bootscreen_apercu.png`) ou `python3 marlin-patches/make_bootscreen.py mon_logo.png` pour ta propre image (convertie en noir et blanc, 128×64).

Ordre obtenu (hors impression) : 1 Surveiller, 2 Préchauffage (ex-Température), 3 Impr. depuis la SD, 4 Actualiser média, 5 Changer filament, 6 Configuration, 7 Mouvement, 8 Lumière, 9 Infos imprimante.
Pendant une impression, le menu garde ses entrées (Pause, Arrêter, Régler…). `PSU_CONTROL` est désactivé, donc « Allumer/Éteindre alim. » a disparu. Le menu « Infos imprimante » (version, carte, thermistances, statistiques) est en dernier. Le diff est dans `marlin-patches/menu-neva.diff`.

## 5. Premier démarrage (sécurité d'abord)

1. Moteurs débranchés de la tête : vérifie les températures (`M105`) et que la thermistance réagit.
2. `M119` : chaque fin de course doit passer à `TRIGGERED` quand tu le presses (et seulement à ce moment).
3. Teste chaque tour avec `G91` / petit `G1 Z5`. Si elle descend au lieu de monter, inverse `INVERT_*_DIR`.
4. `G28` avec la main prête sur l'alimentation, puis `M500`.
5. Calibre avec `G33`, puis `M500`.
