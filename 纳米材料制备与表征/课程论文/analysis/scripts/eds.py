# -*- coding: utf-8 -*-
"""EDS: parse EMSA spectra and plot representative Ti/O spectrum."""
import os, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = r"E:\latex_AI\纳米材料制备与表征\课程论文"
ROOT = os.path.join(BASE, "analysis", "data", "sem", "SEM专业实验-2024级（包含EDS）", "EDS 1-10组", "eds")
OUT = os.path.join(BASE, "analysis", "outputs")
FIG = os.path.join(BASE, "figures")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.linewidth": 0.8,
    "xtick.direction": "in", "ytick.direction": "in", "legend.frameon": False,
    "savefig.bbox": "tight",
})

LINES = [(0.277, "C K$\\alpha$"), (0.452, "Ti L$\\alpha$"), (0.525, "O K$\\alpha$"),
         (1.487, "Al K$\\alpha$"), (4.512, "Ti K$\\alpha$"), (4.932, "Ti K$\\beta$")]
LABELS = [(0.31, 118, "C"), (0.57, 106, "O"), (1.52, 40, "Al"), (4.56, 70, "Ti K$\\alpha$"), (5.00, 26, "Ti K$\\beta$")]


def parse(path):
    data, started, hdr = [], False, {}
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("#SPECTRUM"):
                started = True
                continue
            if s.startswith("#"):
                if ":" in s:
                    k, v = s.lstrip("#").split(":", 1)
                    hdr[k.strip()] = v.strip()
                continue
            if started and re.match(r"^[-\d.]+,\s*[-\d.]+", s):
                a, b = s.split(",")
                data.append((float(a), float(b)))
    arr = np.array(data)
    return hdr, arr[:, 0], arr[:, 1]


def net_area(x, y, lo, hi):
    m = (x >= lo) & (x <= hi)
    xs, ys = x[m], y[m]
    if len(xs) < 8:
        return 0.0
    base = np.linspace(np.median(ys[:3]), np.median(ys[-3:]), len(ys))
    return float(np.trapezoid(np.clip(ys - base, 0, None), xs))


cases = [("eds5_500", r"5\500.txt", "500 $\\degree$C"),
         ("eds5_900", r"5\900.txt", "900 $\\degree$C")]
fig, axes = plt.subplots(2, 1, figsize=(4.4, 3.8), sharex=True)
ratios = {}
for ax, (tag, rel, lab) in zip(axes, cases):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print("missing", p)
        continue
    hdr, x, y = parse(p)
    m = (x >= 0.10) & (x <= 6)
    ax.plot(x[m], y[m], lw=0.6, color="k")
    ax.set_ylabel("Counts")
    ax.text(5.85, 140, lab, ha="right", fontsize=7.5)
    ax.set_xlim(0.10, 6)
    ax.set_ylim(0, 160)
    for pos, name in LINES:
        ax.axvline(pos, color="0.7", lw=0.5, ls=":")
    o = net_area(x, y, 0.44, 0.62)
    ti = net_area(x, y, 4.40, 4.66)
    ratios[tag] = ti / o if o else 0
    print(tag, "O_area=%.0f Ti_area=%.0f ratio=%.2f  live=%.1f" % (o, ti, ratios[tag], float(hdr.get("LIVETIME", 0))))
for lx, ly, lt in LABELS:
    axes[0].text(lx, ly, lt, fontsize=6.2, color="0.25", rotation=90, va="bottom", ha="center")
    axes[1].text(lx, ly, lt, fontsize=6.2, color="0.25", rotation=90, va="bottom", ha="center")
axes[1].set_xlabel("Energy (keV)")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig8_eds.pdf"))
fig.savefig(os.path.join(FIG, "fig8_eds.png"), dpi=600)
plt.close(fig)

with open(os.path.join(OUT, "eds_ratio.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    fh.write("sample,ITiKa_IOKa\n")
    for k, v in ratios.items():
        fh.write("%s,%.3f\n" % (k, v))
print(ratios)



