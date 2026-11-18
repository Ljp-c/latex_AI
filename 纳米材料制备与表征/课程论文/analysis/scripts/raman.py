# -*- coding: utf-8 -*-
"""Raman: baseline correction, peak picking and temperature-series figure."""
import os, io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter
from scipy import sparse
from scipy.sparse.linalg import spsolve

BASE = r"E:\latex_AI\纳米材料制备与表征\课程论文"
ROOT = os.path.join(BASE, "analysis", "data", "raman")
OUT = os.path.join(BASE, "analysis", "outputs")
FIG = os.path.join(BASE, "figures")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.linewidth": 0.8,
    "xtick.direction": "in", "ytick.direction": "in", "legend.frameon": False,
    "savefig.bbox": "tight",
})

SERIES = [
    ("400", "tio2+400-d03-1-1-1-633.txt"),
    ("500", "TIO2-500-633-1-1-1.txt"),
    ("600", "tio2-600-633-d03-1-5-1.txt"),
    ("700-A", "TiO2-700-1-5-1-632nm.txt"),
    ("700-B", "700TiO2-wqs-1-5-1-632nm.txt"),
    ("900", "900TiO2-1-5-1-632nm.txt"),
]

ANATASE = [(144, "E$_g$"), (197, "E$_g$"), (399, "B$_{1g}$"), (516, "A$_{1g}$+B$_{1g}$"), (639, "E$_g$")]
RUTILE = [(235, "2-phonon"), (447, "E$_g$"), (612, "A$_{1g}$")]


def load(path):
    with io.open(path, "r", encoding="utf-8", errors="ignore") as fh:
        arr = [ln.split() for ln in fh if ln.strip() and ln.strip()[0] not in "#"]
    a = np.array([[float(x) for x in r[:2]] for r in arr if len(r) >= 2])
    return a[:, 0], a[:, 1]


def als(y, lam=1e5, p=0.01, niter=12):
    L = len(y)
    D = sparse.diags([1.0, -2.0, 1.0], [0, -1, -2], shape=(L, L - 2))
    w = np.ones(L)
    z = y
    for _ in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        z = spsolve((W + lam * D.dot(D.T)).tocsc(), w * y)
        w = p * (y > z) + (1 - p) * (y < z)
    return z


def find_bands(x, y):
    yy = savgol_filter(y, 9, 3)
    noise = 1.4826 * np.median(np.abs(np.diff(yy))) / np.sqrt(2) + 1e-9
    prom = max(0.03 * np.max(yy), 5 * noise)
    pk, prop = find_peaks(yy, prominence=prom, distance=6)
    out = []
    for i, pr in zip(pk, prop["prominences"]):
        if 100 <= x[i] <= 1000:
            out.append((float(x[i]), float(pr / noise)))
    out.sort(key=lambda r: -r[1])
    return out[:6]


results = {}
fig, ax = plt.subplots(figsize=(4.6, 4.6))
off, STEP = 0.0, 1.05
ticks, labels = [], []
for label, fname in SERIES:
    p = os.path.join(ROOT, "24nano")
    hits = [os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in fs if f == fname]
    if not hits:
        print("missing", fname)
        continue
    x, y = load(hits[0])
    m = (x >= 80) & (x <= 1000)
    xs, ys = x[m], y[m]
    base = als(ys)
    yy = ys - base
    yy = yy / (np.max(yy) + 1e-9)
    ax.plot(xs, yy + off, lw=0.8, color="k")
    ticks.append(off + 0.55)
    labels.append(label.replace("-A", " (a)").replace("-B", " (b)") + " $\\degree$C")
    off += STEP
    results[label] = dict(file=fname, bands=find_bands(xs, yy), xmin=float(xs.min()), xmax=float(xs.max()))

for pos in [p for p, _ in ANATASE]:
    ax.axvline(pos, color="0.75", lw=0.5, ls=":")
for pos in [p for p, _ in RUTILE]:
    ax.axvline(pos, color="0.55", lw=0.5, ls="--")

ax.set_xlim(80, 1000)
ax.set_ylim(-0.12, off + 0.25)
ax.set_yticks(ticks)
ax.set_yticklabels(labels, fontsize=7.5)
ax.set_xlabel("Raman shift (cm$^{-1}$)")
ax.set_ylabel("Intensity (a.u.)")

from matplotlib.lines import Line2D
handles = [Line2D([0], [0], color="0.75", ls=":", lw=0.8, label="Anatase modes"),
           Line2D([0], [0], color="0.55", ls="--", lw=0.8, label="Rutile modes")]
ax.legend(handles=handles, fontsize=6.5, loc="upper right", bbox_to_anchor=(1.0, 1.0))

fig.savefig(os.path.join(FIG, "fig5_raman.pdf"))
fig.savefig(os.path.join(FIG, "fig5_raman.png"), dpi=600)
plt.close(fig)

with open(os.path.join(OUT, "raman_peaks.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    fh.write("label,file,range,top_bands_cm-1\n")
    for k, v in results.items():
        fh.write("%s,%s,%d-%d,%s\n" % (k, v["file"], v["xmin"], v["xmax"],
                                       " ".join("%.0f(%.0f)" % b for b in v["bands"])))

for k, v in results.items():
    print(k, v["file"], ["%d" % b[0] for b in v["bands"]])
