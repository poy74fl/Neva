# Dagoma Neva : Marlin 2.1.2.5 pour BTT SKR 1.4 (LPC1768)

Configuration de départ pour une Neva d'origine (delta, 12 V) avec une carte **BTT SKR 1.4** (non Turbo),
des drivers **TMC2209 V1.3**, un écran **MKS Mini 12864 V3**, deux ventilateurs et une sonde **PINDA**.
Basée sur l'exemple `delta/generic` de Marlin 2.1.2.5, avec :

- `MOTHERBOARD BOARD_BTT_SKR_V1_4`, USB (`SERIAL_PORT -1`)
- Drivers `TMC2209` (UART) sur X, Y, Z, E0, 800 mA, 16 micropas
- Écran `MKS_MINI_12864_V3` sur EXP1 + EXP2 (nappes standard) et `SDSUPPORT` : avec un écran, la SKR 1.4 utilise par défaut la **SD de l'écran**
- `EEPROM_SETTINGS` activé (nécessaire pour garder la géométrie delta avec `M500`)
- Ventilateurs : pièce sur FAN0, hotend automatique sur FAN1 (`E0_AUTO_FAN_PIN`)
- Sonde `FIX_MOUNTED_PROBE` + calibration `G33`
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
3. **Sonde PINDA** : `NOZZLE_TO_PROBE_OFFSET` à mesurer, sens du signal (`Z_MIN_PROBE_ENDSTOP_HIT_STATE`) à vérifier avec `M119`.
4. Sens des moteurs (`INVERT_X/Y/Z_DIR`, `INVERT_E0_DIR`) et type des fins de course (`*_ENDSTOP_HIT_STATE`).


## 3. Câblage SKR 1.4 pour un delta

- Fins de course de tour : X-STOP, Y-STOP, Z-STOP (Marlin les utilise comme fins de course **max** en delta). Retire les jumpers DIAG si tu ne fais pas de sensorless.
- Thermistance hotend sur `T1`/`TH0`, chauffe sur `HE0`, plateau chauffant éventuel sur `T0`/`HB`. Vérifie sur la sérigraphie de ta carte.
- Ventilateurs : **FAN0** = ventilateur de pièce (`M106`/`M107`) ; **FAN1** = ventilateur de la hotend, automatique : il démarre au-dessus de 50 °C et s'arrête quand la buse refroidit. Vérifie leur tension (12 V ou 24 V comme l'alimentation).
- Alimentation : vérifie 12 V vs 24 V avant de brancher.
- **Drivers TMC2209 V1.3 en UART :** consulte la doc BTT pour les jumpers à retirer sous les drivers et la configuration du mode UART sur la SKR 1.4. Après flash, `M122` doit afficher les drivers sans erreur de communication. Si l'UART ne marche pas, remplace `TMC2209` par `TMC2209_STANDALONE` dans `Configuration.h` : le courant se règle alors avec le potentiomètre (Vref) et les micropas avec les jumpers.

## 3b. Écran MKS Mini 12864 V3

Brancher les deux nappes de l'écran sur **EXP1** et **EXP2** de la SKR 1.4. Le MKS Mini 12864 V3 se comporte comme un FYSETC Mini 12864 2.1 pour Marlin. Respecte l'ergot et le sens, en particulier que la nappe EXP1 de l'écran aille sur EXP1 et l'EXP2 sur EXP2. Vérifie sur la doc MKS : certains écrans demandent d'inverser les nappes.
Le lecteur SD de l'écran est utilisé pour imprimer. Pour flasher le firmware, c'est le lecteur de la carte mère (voir ci-dessous).

## 3c. Sonde inductive

Config : `FIX_MOUNTED_PROBE` sur le connecteur **PROBE** (P0.10), calibration delta `G33` et menu de calibration activés.
Le Z est toujours référencé sur la butée de la tour Z (pas sur la sonde).

- **Alimentation :** la plupart des capteurs inductifs (LJ12A3, etc.) demandent 6-36 V, et leur sortie est au niveau de leur alimentation, donc **12 V**. Les entrées de la carte sont en 3,3 V. **Ne relie jamais la sortie directement à P0.10** : utilise un pont diviseur, un optocoupleur ou un module de conversion de niveau. Choisis plutôt un capteur 5 V ou conçu pour carte 3D (type PINDA ou LJ18A3 avec module).
- **Type de sortie :** NPN-NO déclenche à LOW (valeur actuelle), PNP ou NC à HIGH (`Z_MIN_PROBE_ENDSTOP_HIT_STATE`). Vérifie avec `M119` : `z_probe: TRIGGERED` doit apparaître seulement quand un métal passe devant.
- **Plateau :** un inductif ne détecte que le métal. Si ton plateau est en verre, il faut une plaque métallique dessous.
- **Offsets :** mesure la distance buse -> sonde en X, Y (`NOZZLE_TO_PROBE_OFFSET`) et règle Z avec `M851` / l'écran. Les valeurs actuelles sont des estimations.
- **Rayon de sonde :** avec le décalage en Y, vérifie que la zone sondée ne sort pas du plateau.

### PINDA : points d'attention

- **Tension :** les PINDA Prusa fonctionnent en 5 V (il y a un fil 5 V sur le connecteur PROBE de la carte). Contrôle la fiche de ta version : les versions V1 (3 fils) et V2 (4 fils, avec thermistance de compensation) se câblent différemment. Ne l'alimente pas en 12 V si ta fiche indique 5 V.
- **Niveau du signal :** une sortie 5 V sur une entrée 3,3 V est risquée. Mesure d'abord au multimètre la tension de la broche signal (déclenchée / non déclenchée) avant de la relier à P0.10. Si elle dépasse 3,3 V, ajoute un diviseur (par exemple 2 k + 3,3 k) ou un convertisseur de niveau.
- **Sens :** le PINDA est souvent NC (sortie active au repos). Si `M119` donne `z_probe: TRIGGERED` sans métal, passe `Z_MIN_PROBE_ENDSTOP_HIT_STATE` à `HIGH`.
- **Portée :** environ 1 à 2 mm sur de l'acier, moins sur de l'aluminium. Le Z de `NOZZLE_TO_PROBE_OFFSET` est proche de la hauteur de la sonde au-dessus de la buse : à régler avec `M851` / test papier.
- **Dérive thermique :** le PINDA dérive quand le plateau chauffe. Marlin n'utilise pas la thermistance de la V2 : fais ta calibration `G33` plateau et hotend à température d'impression.


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

## 5. Premier démarrage (sécurité d'abord)

1. Moteurs débranchés de la tête : vérifie les températures (`M105`) et que la thermistance réagit.
2. `M119` : chaque fin de course doit passer à `TRIGGERED` quand tu le presses (et seulement à ce moment).
3. Teste chaque tour avec `G91` / petit `G1 Z5`. Si elle descend au lieu de monter, inverse `INVERT_*_DIR`.
4. `G28` avec la main prête sur l'alimentation, puis `M500`.
5. Calibre avec `G33`, puis `M500`.
