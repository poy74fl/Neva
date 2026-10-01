# Dagoma Neva : Marlin 2.1.2.5 pour BTT SKR Mini E3 V3.0

Configuration de départ pour une Neva d'origine (delta, 12 V) avec une carte SKR Mini E3 V3.0.
Basée sur l'exemple `delta/generic` de Marlin 2.1.2.5, avec :

- `MOTHERBOARD BOARD_BTT_SKR_MINI_E3_V3_0`, USB natif (`SERIAL_PORT -1`, 115200 bauds)
- Drivers `TMC2209` (UART) sur X, Y, Z, E0, 800 mA, 16 micropas
- `EEPROM_SETTINGS` activé (nécessaire pour garder la géométrie delta avec `M500`)
- Écran `MKS_MINI_12864_V3` + `SDSUPPORT` (lecteur SD de la carte, l'écran n'en a pas)
- Vitesses, accélérations et homing volontairement prudents

> **État : non compilée.** Le réseau de la session bloquait le téléchargement de PlatformIO.
> Les valeurs marquées `NEVA:` sont des estimations que je n'ai pas pu confirmer : le dépôt
> `dagoma3d/Marlin` ne contient pas de config Neva.

## 1. Récupérer les vraies valeurs de ta Neva (avant de débrancher l'ancienne carte)

Connecte l'imprimante (Pronterface, OctoPrint, Cura…) et envoie `M503`. Note surtout :

| Commande | À reporter dans `Configuration.h` |
|---|---|
| `M92` | `DEFAULT_AXIS_STEPS_PER_UNIT` (X/Y/Z : modifier `XYZ_PULLEY_TEETH`, E : 4e valeur) |
| `M665` L / R / H | `DELTA_DIAGONAL_ROD` / `DELTA_RADIUS` / `DELTA_HEIGHT` |
| `M666` | `DELTA_ENDSTOP_ADJ` |
| `M301` ou `M303` | PID du hotend (`DEFAULT_Kp/Ki/Kd`), sinon lance `M303 E0 S200 C8 U1` |

Envoie aussi `M119` (état des fins de course) et note le type de capteur de Z utilisé par ta Neva.
Si tu as le `Configuration.h` de l'ancien firmware, c'est encore mieux : envoie-le-moi.

## 2. Ce qu'il reste à régler pour ta machine

1. Valeurs `NEVA:` de `Configuration.h` (géométrie delta, rayon imprimable, dents des poulies).
2. `TEMP_SENSOR_0` (1 = thermistance 100k standard) et `TEMP_SENSOR_BED` si plateau chauffant.
3. **Sonde / fin de course Z** : le config actuel n'a aucune sonde (calibration manuelle).
   À adapter selon ton capteur (`FIX_MOUNTED_PROBE`, `Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN`, `NOZZLE_TO_PROBE_OFFSET`).
4. Sens des moteurs (`INVERT_X/Y/Z_DIR`, `INVERT_E0_DIR`) et type des fins de course (`*_ENDSTOP_HIT_STATE`).

## 3. Câblage SKR Mini E3 V3 pour un delta

- Fins de course de tour : connecteurs X-STOP, Y-STOP, Z-STOP (Marlin les utilise comme fins de course **max** en delta).
- Thermistance hotend sur `TH0`, chauffe sur `HE`, ventilateur de buse sur `FAN0`/`FAN1`.
- Alimentation : vérifie 12 V vs 24 V avant de brancher (la carte accepte 12–24 V).
- Les drivers étant des TMC2209 : mets les jumpers DIAG comme sur la doc BTT, ou retire-les si tu n'utilises pas le sensorless.

## 3b. Écran MKS Mini 12864 V3

L'écran ne se branche **pas** directement : les brochages des connecteurs EXP1 de la SKR et de l'écran sont différents.
Deux options :
1. **Câble custom** (cas par défaut de cette config) : suivre le schéma dans
   `Marlin/src/pins/stm32g0/pins_BTT_SKR_MINI_E3_V3_0.h` (bloc `FYSETC_MINI_12864_2_1`). Vérifie l'ergot et le sens de chaque connecteur : une erreur peut griller l'écran.
2. **Adaptateur Voron "SKR Mini Screen Adaptor"** (PCB à imprimer/commander) : ajouter `#define SKR_MINI_SCREEN_ADAPTER` dans `Configuration.h`.

Les LED NeoPixel de l'écran se règlent ensuite via `NEOPIXEL_LED` (non activé ici).

## 4. Compiler et flasher

```bash
git clone --branch 2.1.2.5 https://github.com/MarlinFirmware/Marlin.git
cp marlin-config/Configuration.h marlin-config/Configuration_adv.h Marlin/Marlin/
cd Marlin && pio run -e STM32G0B1RE_btt
```

Le firmware est dans `.pio/build/STM32G0B1RE_btt/firmware.bin`. Copie-le à la racine d'une carte SD
(FAT32), nomme-le `firmware.bin`, mets la carte dans la SKR et redémarre. Le fichier devient `FIRMWARE.CUR`.
Tu peux aussi utiliser VS Code + l'extension Auto Build Marlin.

## 5. Premier démarrage (sécurité d'abord)

1. Moteurs débranchés de la tête : vérifie les températures (`M105`) et que la thermistance réagit.
2. `M119` : chaque fin de course doit passer à `TRIGGERED` quand tu le presses (et seulement à ce moment).
3. Teste chaque tour avec `G91` / petit `G1 Z5`. Si elle descend au lieu de monter, inverse `INVERT_*_DIR`.
4. `G28` avec la main prête sur l'alimentation, puis `M500`.
5. Calibre : `M665`/`M666` ou `G33` si tu ajoutes une sonde, puis `M500`.
