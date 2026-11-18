# -*- coding: utf-8 -*-
"""XRD analysis v2: region-based peak detection + single pseudo-Voigt fits."""
import os, re, io, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit

BASE = r"E:\latex_AI\纳米材料制备与表征\课程论文"
DATA = os.path.join(BASE, "analysis", "data", "xrd")
OUT = os.path.join(BASE, "analysis", "outputs")
FIG = os.path.join(BASE, "figures")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.linewidth": 0.8,
    "xtick.direction": "in", "ytick.direction": "in", "legend.frameon": False,
    "savefig.bbox": "tight",
})

LAMBDA = 1.54056
A101, R110 = 25.28, 27.45


def parse(path):
    header, rows = {}, []
    with io.open(path, "r", encoding="gbk", errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            m = re.match(r"^([\u4e00-\u9fa5A-Za-z ]+?)[=:：]\s*(.*)$", s)
            if m and not rows:
                header[m.group(1).strip()] = m.group(2).strip()
                continue
            if re.match(r"^\s*[\d.]+ \d+", s):
                a, b = s.split()[:2]
                rows.append((float(a), float(b)))
    if not rows:
        raise RuntimeError("no data: " + path)
    arr = np.array(rows)
    return header, arr[:, 0], arr[:, 1]


def pv(x, amp, xc, fwhm, eta):
    t = (x - xc) / fwhm
    return amp * (eta / (1 + 4 * t * t) + (1 - eta) * np.exp(-4 * np.log(2) * t * t))


def fit_one(x, y, lo, hi, guess):
    m = (x >= lo) & (x <= hi)
    xs, ys = x[m], y[m]
    if len(xs) < 25:
        return None
    edge = np.r_[ys[:8], ys[-8:]]
    base = np.polyval(np.polyfit(np.r_[xs[:8], xs[-8:]], edge, 1), xs)
    sig = ys - base
    sm = savgol_filter(sig, 9, 2)
    i = int(np.argmax(sm))
    resid = sm - savgol_filter(sm, 41, 2)
    if sm[i] < 6 * (np.std(resid) + 1e-9):
        return None
    p0 = [max(sm[i], 1.0), xs[i], 0.4, 0.5]
    bounds = ([0, guess - 0.45, 0.10, 0.0], [np.inf, guess + 0.45, 2.6, 1.0])
    try:
        p, _ = curve_fit(lambda t, a, c, w, e: a * pv(t, 1.0, c, w, e), xs, sig,
                         p0=p0, bounds=bounds, maxfev=60000)
    except Exception:
        return None
    amp, c, w, e = p
    area = amp * w * (e * np.pi / 2 + (1 - e) * np.sqrt(np.pi / (4 * np.log(2))))
    return {"xc": float(c), "fwhm": abs(float(w)), "amp": float(amp), "area": float(area)}


def scherrer(fwhm_deg, two_theta, K=0.9):
    beta = np.deg2rad(abs(fwhm_deg))
    th = np.deg2rad(two_theta / 2)
    return K * LAMBDA / (beta * np.cos(th)) / 10.0


def temperature(name):
    m = re.search(r"(200|300|400|500|600|700|800|900)", name)
    return int(m.group(1)) if m else None


GROUPS = {"G1": "g1", "G3": "g3", "G5": "g5", "G6": "g6"}
series = {}
for gid, sub in GROUPS.items():
    for p in glob.glob(os.path.join(DATA, sub, "**", "*.txt"), recursive=True):
        name = os.path.basename(p)
        t = temperature(name)
        if t is None:
            continue
        h, x, y = parse(p)
        series.setdefault(gid, {}).setdefault(t, []).append((name, x, y, h))

# prefer non zero-padded names when several files share a temperature
for gid in series:
    for t in series[gid]:
        series[gid][t].sort(key=lambda r: (r[0].startswith("0"), len(r[0]), r[0]))
        series[gid][t] = series[gid][t][0]

rows, fits = [], {}
for gid in sorted(series):
    for t in sorted(series[gid]):
        name, x, y, h = series[gid][t]
        A = fit_one(x, y, 24.2, 26.6, A101)
        R = fit_one(x, y, 26.6, 29.2, R110)
        if R and abs(R["xc"] - R110) > 0.35:
            R = None
        if A and abs(A["xc"] - A101) > 0.5:
            A = None
        rp = 0.0
        if R and A:
            rp = 100 * R["area"] / (R["area"] + 0.8 * A["area"])
        elif R and not A:
            rp = 100.0
        D = scherrer(A["fwhm"], A["xc"]) if A else None
        row = dict(group=gid, temp=t, file=name,
                   A_2theta=A["xc"] if A else None, A_fwhm=A["fwhm"] if A else None,
                   R_2theta=R["xc"] if R else None, R_fwhm=R["fwhm"] if R else None,
                   D_nm=D, rutile_pct=rp,
                   start=h.get("起始角"), stop=h.get("终止角"), step=h.get("步宽"))
        rows.append(row)
        fits[(gid, t)] = (x, y, A, R)

cols = ["group", "temp", "file", "A_2theta", "A_fwhm", "R_2theta", "R_fwhm", "D_nm", "rutile_pct", "start", "stop", "step"]
with open(os.path.join(OUT, "xrd_peaks.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    fh.write(",".join(cols) + "\n")
    for r in rows:
        out = []
        for c in cols:
            v = r[c]
            out.append(("%.4f" % v) if isinstance(v, float) else ("" if v is None else str(v)))
        fh.write(",".join(out) + "\n")

main = "G6"
fig, ax = plt.subplots(figsize=(3.25, 3.9))
off, step_off = 0.0, 1.0
for t, (name, x, y, h) in sorted(series[main].items()):
    m = (x >= 20) & (x <= 80)
    xs, ys = x[m], y[m]
    ax.plot(xs, ys / ys.max() + off, lw=0.45, color="k")
    ax.text(78.5, off + 0.62, "%d $\\degree$C" % t, ha="right", fontsize=5.2)
    off += step_off
ax.set_xlim(20, 80)
ax.set_yticks([])
ax.set_xlabel(r"2$\theta$ (degree)")
ax.set_ylabel("Intensity (a.u.)")
for pos in (A101, R110):
    ax.axvline(pos, color="0.65", lw=0.6, ls="--")
ax.text(A101 - 1.6, 0.15, "A(101)", fontsize=7, color="0.35", rotation=90)
ax.text(R110 + 0.5, 0.15, "R(110)", fontsize=7, color="0.35", rotation=90)
fig.savefig(os.path.join(FIG, "fig2_xrd_stack.pdf"))
fig.savefig(os.path.join(FIG, "fig2_xrd_stack.png"), dpi=600)
plt.close(fig)

sel = sorted([r for r in rows if r["group"] == main], key=lambda r: r["temp"])
T = [r["temp"] for r in sel]
D = [r["D_nm"] if r["D_nm"] else np.nan for r in sel]
RP = [r["rutile_pct"] for r in sel]
fig, ax1 = plt.subplots(figsize=(4.2, 3.1))
ax1.plot(T, D, "o-", ms=3.5, lw=1.0, color="#2b6cb0")
ax1.set_xlabel("Annealing temperature ($\\degree$C)")
ax1.set_ylabel("Crystallite size (nm)", color="#2b6cb0")
ax1.tick_params(axis="y", colors="#2b6cb0")
ax2 = ax1.twinx()
ax2.plot(T, RP, "s--", ms=3.5, lw=1.0, color="#c53030")
ax2.set_ylabel("Rutile fraction (%)", color="#c53030")
ax2.tick_params(axis="y", colors="#c53030")
ax2.set_ylim(-5, 105)
fig.savefig(os.path.join(FIG, "fig3_xrd_quant.pdf"))
fig.savefig(os.path.join(FIG, "fig3_xrd_quant.png"), dpi=600)
plt.close(fig)

cmp_t = 800
fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.9))
colors = {"G1": "#2b6cb0", "G3": "#2f855a", "G5": "#b7791f", "G6": "#805ad5"}
markers = {"G1": "o", "G3": "^", "G5": "s", "G6": "D"}
for g in ["G1", "G3", "G5", "G6"]:
    ss = sorted([r for r in rows if r["group"] == g], key=lambda r: r["temp"])
    tt = [r["temp"] for r in ss]
    dd = [r["D_nm"] if r["D_nm"] else np.nan for r in ss]
    rr = [r["rutile_pct"] for r in ss]
    axes[0].plot(tt, dd, marker=markers[g], ms=3.0, lw=0.8, color=colors[g], label=g)
    axes[1].plot(tt, rr, marker=markers[g], ms=3.0, lw=0.8, color=colors[g], label=g)
axes[0].set_xlabel("Annealing temperature ($\\degree$C)")
axes[0].set_ylabel("Crystallite size (nm)")
axes[1].set_xlabel("Annealing temperature ($\\degree$C)")
axes[1].set_ylabel("Rutile fraction (%)")
axes[1].set_ylim(-5, 105)
axes[0].legend(fontsize=7, title="Group", title_fontsize=7, ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig4_xrd_groups.pdf"))
fig.savefig(os.path.join(FIG, "fig4_xrd_groups.png"), dpi=600)
plt.close(fig)

for r in sorted(rows, key=lambda r: (r["group"], r["temp"])):
    print("%-3s %4d %-24s A=%s fwhm=%s D=%s nm  R=%5.1f%%" % (
        r["group"], r["temp"], r["file"][:24],
        "%.2f" % r["A_2theta"] if r["A_2theta"] else "  -  ",
        "%.3f" % r["A_fwhm"] if r["A_fwhm"] else "  -  ",
        "%.1f" % r["D_nm"] if r["D_nm"] else "  -  ", r["rutile_pct"]))

