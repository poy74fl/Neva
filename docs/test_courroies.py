#!/usr/bin/env python3
"""Test des courroies : compare la charge des 3 moteurs (StallGuard des TMC2209) et affiche un resume.

  pip3 install pyserial
  python3 docs/test_courroies.py                      # port detecte automatiquement
  python3 docs/test_courroies.py /dev/cu.usbmodem1101

La machine se met a l'origine (G28) puis les 3 chariots montent/descendent ensemble (Z 60 <-> 200 mm, tete au centre)
a 30 puis 60 mm/s. Le firmware envoie toutes les 250 ms "X:pwm/cs/sg|..." (M122 S1) : on lit pwm et sg de X, Y, Z.
Ferme tout autre terminal serie (PlatformIO, Pronterface) avant. Les mesures sont ajoutees a docs/mesures_courroies.csv.
Le resultat est RELATIF (3 tours entre elles, ou avant/apres reglage), ce n'est pas une tension en newtons.
"""
import re, sys, time, glob, csv, statistics
from datetime import datetime
from pathlib import Path

SPEEDS = (30, 60)              # mm/s
REPS = 3                       # montees + descentes par vitesse
Z_LOW, Z_HIGH = 60, 200        # mm
SAMPLE = re.compile(r"(?<![A-Za-z0-9])([XYZ]):(\d+)/(\d+)/(\d+|-)\|")
OK_SPREAD, WARN_SPREAD = 10.0, 25.0   # ecart max entre tours (%), seuils de depart a affiner avec tes mesures


def parse_line(line):
    """Retourne {'X': (pwm, sg), ...} pour une ligne de rapport, ou {}."""
    out = {}
    for axis, pwm, _cs, sg in SAMPLE.findall(line):
        if sg != "-":
            out[axis] = (int(pwm), int(sg))
    return out


def summarize(passes):
    """passes : {(vitesse, sens): [ {'X':(pwm,sg), ...}, ... ]} -> {(vitesse, sens): {axe: (pwm_median, sg_median, n)}}"""
    res = {}
    for key, samples in passes.items():
        res[key] = {}
        for axis in "XYZ":
            vals = [s[axis] for s in samples if axis in s]
            if len(vals) >= 3:
                vals = vals[1:-1]            # on retire le premier et le dernier (acceleration / arret)
            if vals:
                res[key][axis] = (statistics.median(v[0] for v in vals), statistics.median(v[1] for v in vals), len(vals))
    return res


def spread_pct(values):
    m = statistics.mean(values)
    return 100.0 * (max(values) - min(values)) / m if m else 0.0


def verdict(sp):
    if sp < OK_SPREAD: return "equilibre"
    if sp < WARN_SPREAD: return "a verifier"
    return "desequilibre"


def report(res):
    lines = []
    worst = 0.0
    lines.append(f"{'vitesse':>8} {'sens':<9} {'sg X':>6} {'sg Y':>6} {'sg Z':>6} {'ecart':>7}   {'pwm X':>6} {'pwm Y':>6} {'pwm Z':>6}")
    for (speed, sens), axes in sorted(res.items()):
        if len(axes) < 3:
            lines.append(f"{speed:>5} mm/s {sens:<9} mesures insuffisantes ({', '.join(f'{a}:{v[2]}' for a, v in axes.items())})")
            continue
        sgs = [axes[a][1] for a in "XYZ"]
        sp = spread_pct(sgs)
        worst = max(worst, sp)
        lines.append(f"{speed:>5} mm/s {sens:<9} {sgs[0]:6.0f} {sgs[1]:6.0f} {sgs[2]:6.0f} {sp:6.1f}%   "
                     f"{axes['X'][0]:6.0f} {axes['Y'][0]:6.0f} {axes['Z'][0]:6.0f}")
    lines.append("")
    # une tour qui s'ecarte dans toutes les mesures : on la designe
    dev = {a: [] for a in "XYZ"}
    for axes in res.values():
        if len(axes) == 3:
            mean = statistics.mean(axes[a][1] for a in "XYZ")
            for a in "XYZ":
                dev[a].append(100.0 * (axes[a][1] - mean) / mean if mean else 0.0)
    if all(dev[a] for a in "XYZ"):
        avg = {a: statistics.mean(dev[a]) for a in "XYZ"}
        lines.append("Ecart moyen de chaque tour par rapport a la moyenne des 3 (sg) : " +
                     "  ".join(f"{a} {avg[a]:+.1f}%" for a in "XYZ"))
        far = max(avg, key=lambda a: abs(avg[a]))
        if abs(avg[far]) >= OK_SPREAD / 2:
            lines.append(f"-> la tour {far} se distingue ({avg[far]:+.1f}%) : verifie sa courroie (frequence en pincant) et son frottement.")
    lines.append(f"Ecart maximal entre tours : {worst:.1f}% -> {verdict(worst)}"
                 f"  (seuils provisoires : <{OK_SPREAD:.0f}% ok, <{WARN_SPREAD:.0f}% a verifier)")
    return "\n".join(lines)


class Printer:
    def __init__(self, port, baud=115200):
        import serial
        self.ser = serial.Serial(port, baud, timeout=1)
        self.sink = None

    def _read_until_ok(self, timeout):
        end = time.time() + timeout
        while time.time() < end:
            raw = self.ser.readline().decode(errors="replace").strip()
            if not raw:
                continue
            if self.sink is not None:
                s = parse_line(raw)
                if s:
                    self.sink.append(s)
            if raw.startswith("ok"):
                return
            if raw.startswith("Error"):
                raise RuntimeError(raw)
        raise TimeoutError("pas de reponse 'ok' de la machine")

    def send(self, cmd, timeout=120):
        print(">", cmd)
        self.ser.write((cmd + "\n").encode())
        self._read_until_ok(timeout)

    def start(self):
        time.sleep(2)
        self.ser.reset_input_buffer()
        self.send("M105", 15)


def run(port):
    p = Printer(port)
    p.start()
    p.send("G90")
    p.send("G28", 240)
    p.send(f"G1 X0 Y0 Z{Z_HIGH} F6000")
    p.send("M400")
    p.send("M122 S1 P250")
    passes = {}
    try:
        for speed in SPEEDS:
            for _ in range(REPS):
                for z, sens in ((Z_LOW, "descente"), (Z_HIGH, "montee")):
                    buf = passes.setdefault((speed, sens), [])
                    p.sink = buf
                    p.send(f"G1 Z{z} F{speed * 60}")
                    p.send("M400")
    finally:
        p.sink = None
        try:
            p.send("M122 S0", 10)
        except Exception:
            pass
    return passes


def main(argv):
    port = argv[1] if len(argv) > 1 else None
    if port is None:
        found = sorted(glob.glob("/dev/cu.usbmodem*") + glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
        if not found:
            sys.exit("Aucun port serie trouve : branche l'USB de la SKR et passe le port en argument.")
        port = found[0]
    print("Port :", port)
    res = summarize(run(port))
    print()
    print(report(res))
    out = Path(__file__).resolve().parent / "mesures_courroies.csv"
    new = not out.exists()
    with out.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "vitesse_mm_s", "sens", "axe", "pwm_median", "sg_median", "echantillons"])
        now = datetime.now().isoformat(timespec="seconds")
        for (speed, sens), axes in sorted(res.items()):
            for a, (pwm, sg, n) in axes.items():
                w.writerow([now, speed, sens, a, pwm, sg, n])
    print("\nMesures ajoutees a", out)


if __name__ == "__main__":
    main(sys.argv)
