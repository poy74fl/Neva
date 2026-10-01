# Dagoma Neva : Marlin 2.1.2.5 pour BTT SKR Mini E3 V3.0

Configuration de départ pour une Neva d'origine (delta, 12 V) avec une carte SKR Mini E3 V3.0.
Basée sur l'exemple `delta/generic` de Marlin 2.1.2.5, avec :

- `MOTHERBOARD BOARD_BTT_SKR_MINI_E3_V3_0`, USB natif (`SERIAL_PORT -1`, 115200 bauds)
- Drivers `TMC2209` (UART) sur X, Y, Z, E0, 800 mA, 16 micropas
- `EEPROM_SETTINGS` activé (nécessaire pour garder la géométrie delta avec `M500`)
- Écran `MKS_MINI_12864_V3` + `SDSUPPORT` (lecteur SD de la carte mère ; celui de l'écran n'est pas utilisable avec la SKR Mini E3 V3, Marlin ne le gère pas)
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
- Thermistance hotend sur `TH0`, chauffe sur `HE`.
- Ventilateurs : **FAN0** = ventilateur de pièce (commandé par `M106`/`M107`, réglé par le slicer) ; **FAN1** = ventilateur de la hotend, automatique (`E0_AUTO_FAN_PIN`) : il démarre au-dessus de 50 °C et s'arrête quand la buse refroidit. FAN2 reste libre.
  Vérifie que ces ventilateurs sont en 12 V (ou 24 V) comme ton alimentation.
- Alimentation : vérifie 12 V vs 24 V avant de brancher (la carte accepte 12–24 V).
- Les drivers étant des TMC2209 : mets les jumpers DIAG comme sur la doc BTT, ou retire-les si tu n'utilises pas le sensorless.

## 3b. Écran MKS Mini 12864 V3

L'écran ne se branche **pas** directement : les brochages des connecteurs EXP1 de la SKR et de l'écran sont différents.
Deux options :
1. **Câble custom** (cas par défaut de cette config) : suivre le schéma dans
   `Marlin/src/pins/stm32g0/pins_BTT_SKR_MINI_E3_V3_0.h` (bloc `FYSETC_MINI_12864_2_1`). Vérifie l'ergot et le sens de chaque connecteur : une erreur peut griller l'écran.
2. **Adaptateur Voron "SKR Mini Screen Adaptor"** (PCB à imprimer/commander) : ajouter `#define SKR_MINI_SCREEN_ADAPTER` dans `Configuration.h`.

Les LED NeoPixel de l'écran se règlent ensuite via `NEOPIXEL_LED` (non activé ici).

## 3c. Sonde inductive

Config : `FIX_MOUNTED_PROBE` sur le connecteur **PROBE** (PC14), calibration delta `G33` et menu de calibration activés.
Le Z est toujours référencé sur la butée de la tour Z (pas sur la sonde).

- **Alimentation :** la plupart des capteurs inductifs (LJ12A3, etc.) demandent 6-36 V, et leur sortie est au niveau de leur alimentation, donc **12 V**. Les entrées de la carte sont en 3,3 V. **Ne relie jamais la sortie directement à PC14** : utilise un pont diviseur, un optocoupleur ou un module de conversion de niveau. Choisis plutôt un capteur 5 V ou conçu pour carte 3D (type PINDA ou LJ18A3 avec module).
- **Type de sortie :** NPN-NO déclenche à LOW (valeur actuelle), PNP ou NC à HIGH (`Z_MIN_PROBE_ENDSTOP_HIT_STATE`). Vérifie avec `M119` : `z_probe: TRIGGERED` doit apparaître seulement quand un métal passe devant.
- **Plateau :** un inductif ne détecte que le métal. Si ton plateau est en verre, il faut une plaque métallique dessous.
- **Offsets :** mesure la distance buse -> sonde en X, Y (`NOZZLE_TO_PROBE_OFFSET`) et règle Z avec `M851` / l'écran. Les valeurs actuelles sont des estimations.
- **Rayon de sonde :** avec le décalage en Y, vérifie que la zone sondée ne sort pas du plateau.

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
