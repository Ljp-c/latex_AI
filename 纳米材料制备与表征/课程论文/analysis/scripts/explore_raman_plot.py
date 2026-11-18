# -*- coding: utf-8 -*-
"""Review candidate Raman spectra for the TiO2 temperature series."""
import os, io, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\raman"
OUT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs"

targets = [
    "tio2+400-d03-1-1-1-633.txt",
    "400TiO2-633nm-1-5-1.txt",
    "TIO2-500-633-1-1-1.txt",
    "tio2-600-633-d03-1-5-1.txt",
    "_ti02  600.txt",
    "700TiO2-wqs-1-5-1-632nm.txt",
    "TiO2-700-1-5-1-632nm.txt",
    "900TiO2-1-5-1-632nm.txt",
    "900TiO2wyx-1-5-1-632nm.txt",
    "tio2-300-633-d06-1-5-1.txt",
    "tio2-800-633-d06-1-5-1.txt",
    "fsTiO2-1-5-1-632nm.txt",
]


def load(p):
    with io.open(p, "r", encoding="utf-8", errors="ignore") as fh:
        arr = [ln.split() for ln in fh if ln.strip() and ln.strip()[0] not in "#"]
    a = np.array([[float(x) for x in r[:2]] for r in arr if len(r) >= 2])
    return a[:, 0], a[:, 1]


paths = {}
for p in glob.glob(os.path.join(ROOT, "**", "*.txt"), recursive=True):
    paths.setdefault(os.path.basename(p), p)

fig, axes = plt.subplots(6, 2, figsize=(9, 12))
for ax, t in zip(axes.ravel(), targets):
    p = paths.get(t)
    if not p:
        ax.set_title("missing: " + t, fontsize=7)
        continue
    x, y = load(p)
    m = x <= 2100
    ax.plot(x[m], y[m], lw=0.7, color="k")
    ax.set_title(t, fontsize=7)
    ax.tick_params(labelsize=6)
    for pos in (144, 399, 516, 639, 447, 612):
        ax.axvline(pos, color="0.7", lw=0.4, ls=":")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "raman_review.png"), dpi=110)
print("saved", os.path.join(OUT, "raman_review.png"))
