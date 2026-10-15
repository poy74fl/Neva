#!/usr/bin/env python3
"""Recopie docs/test_premiere_couche_spirale.gcode dans marlin-config/Configuration_adv.h
(macro NEVA_TEST_SPIRALE_GCODE du menu Tests). A relancer apres python3 docs/make_test_spirale.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GC = ROOT / "docs" / "test_premiere_couche_spirale.gcode"
CFG = ROOT / "marlin-config" / "Configuration_adv.h"
BEGIN, END = "  // BEGIN NEVA_SPIRALE (genere par docs/make_macro_spirale.py)\n", "  // END NEVA_SPIRALE\n"

lines = []
for l in GC.read_text().splitlines():
    l = l.split(";")[0].strip()
    if l:
        lines.append(l)
body = "  #define NEVA_TEST_SPIRALE_GCODE \\\n" + " \\\n".join(f'    "{l}\\n"' for l in lines[:-1]) + f' \\\n    "{lines[-1]}"\n'
block = BEGIN + body + END

s = CFG.read_text()
if BEGIN in s:
    a, b = s.index(BEGIN), s.index(END) + len(END)
    s = s[:a] + block + s[b:]
else:
    key = '  #define MAIN_MENU_ITEM_1_DESC "Test 1ere couche"'
    assert s.count(key) == 1
    s = s.replace(key, block + "\n" + key)
CFG.write_text(s)
print(len(lines), "lignes ->", CFG)
