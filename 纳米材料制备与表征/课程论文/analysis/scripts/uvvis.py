# -*- coding: utf-8 -*-
"""UV-Vis diffuse reflectance: spectra, Kubelka-Munk and Tauc plots."""
import os, re, io, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

BASE = r"E:\latex_AI\纳米材料制备与表征\课程论文"
ROOT = os.path.join(BASE, "analysis", "data", "uvvis", "分光光度计", "solid", "24nano第四组")
OUT = os.path.join(BASE, "analysis", "outputs")
FIG = os.path.join(BASE, "figures")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.linewidth": 0.8,
    "xtick.direction": "in", "ytick.direction": "in", "legend.frameon": False,
    "savefig.bbox": "tight",
})

HC = 1239.841984  # eV nm


def parse(path):
    hdr, data = {}, []
    with io.open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            m = re.match(r"^([A-Za-z][\w ]*?):\s*(.*)$", s)
            if m and not data:
                hdr[m.group(1).strip()] = m.group(2).strip()
                continue
            if re.match(r"^[-\d.]+\s+[-\d.]+$", s):
                a, b = s.split()
                data.append((float(a), float(b)))
    arr = np.array(data)
    return hdr, arr[:, 0], arr[:, 1]


files = sorted(glob.glob(os.path.join(ROOT, "tio2-*.TXT")))
spectra = {}
for p in files:
    m = re.search(r"tio2-(\d{3})", os.path.basename(p))
    if not m:
        continue
    hdr, wl, A = parse(p)
    o = np.argsort(wl)
    spectra[int(m.group(1))] = (wl[o], A[o], hdr)

# the 900 C export has a non-zeroed baseline (negative absorbance), exclude it
for t in [t for t in list(spectra) if spectra[t][1].min() < -0.02]:
    print("exclude %d C: negative absorbance (baseline not zeroed)" % t)
    spectra.pop(t)

print("samples:", sorted(spectra))
if spectra:
    k = sorted(spectra)[0]
    wl, A, hdr = spectra[k]
    print("range", wl.min(), wl.max(), "A range", A.min(), A.max())
    for key in ("Data Mode", "Slit Width", "Scan Speed", "Sampling Interval"):
        print(key, hdr.get(key))

fig, ax = plt.subplots(figsize=(4.3, 3.3))
colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(spectra)))
for c, t in zip(colors, sorted(spectra)):
    wl, A, _ = spectra[t]
    ax.plot(wl, A, lw=0.9, color=c, label="%d $\\degree$C" % t)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Absorbance (a.u.)")
ax.set_xlim(300, 600)
ax.legend(fontsize=6.5, ncol=2)
fig.savefig(os.path.join(FIG, "fig9_uvvis.pdf"))
fig.savefig(os.path.join(FIG, "fig9_uvvis.png"), dpi=600)
plt.close(fig)


def tauc(A, wl, exponent=0.5):
    """A is absorbance (=-log R); convert to Kubelka-Munk F(R), then Tauc."""
    R = np.clip(10.0 ** (-A), 1e-4, 0.9999)
    F = (1 - R) ** 2 / (2 * R)
    hv = HC / wl
    y = (F * hv) ** exponent
    return hv, y


eg = {}
fig, ax = plt.subplots(figsize=(4.3, 3.4))
for c, t in zip(colors, sorted(spectra)):
    wl, A, _ = spectra[t]
    hv, y = tauc(A, wl, 0.5)
    o = np.argsort(hv)
    hv, y = hv[o], y[o]
    ax.plot(hv, y, lw=0.9, color=c, label="%d $\\degree$C" % t)
    # linear region: 15%..55% of max on the rising edge
    ymax = np.max(y)
    idx = np.where((y > 0.30 * ymax) & (y < 0.70 * ymax))[0]
    if len(idx) > 8:
        hv_f, y_f = hv[idx], y[idx]
        p = np.polyfit(hv_f, y_f, 1)
        eg[t] = -p[1] / p[0]
        ax.plot(hv_f, np.polyval(p, hv_f), color=c, lw=1.2, ls="--")
ax.set_xlabel("Photon energy (eV)")
ax.set_ylabel("$(F(R)\\,h\\nu)^{1/2}$ (a.u.)")
ax.set_xlim(2.0, 4.2)
ax.legend(fontsize=6.5, ncol=2)
fig.savefig(os.path.join(FIG, "fig10_tauc.pdf"))
fig.savefig(os.path.join(FIG, "fig10_tauc.png"), dpi=600)
plt.close(fig)

with open(os.path.join(OUT, "uvvis_eg.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    fh.write("temp_C,Eg_eV\n")
    for t in sorted(eg):
        fh.write("%d,%.3f\n" % (t, eg[t]))
print({k: round(v, 2) for k, v in sorted(eg.items())})
