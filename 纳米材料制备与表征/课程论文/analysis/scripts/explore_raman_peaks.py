# -*- coding: utf-8 -*-
import os, glob, io
import numpy as np
from scipy.signal import find_peaks, savgol_filter
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

ROOT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\raman"


def load(p):
    with io.open(p, "r", encoding="utf-8", errors="ignore") as fh:
        arr = [ln.split() for ln in fh if ln.strip() and ln.strip()[0] not in "#"]
    a = np.array([[float(x) for x in r[:2]] for r in arr if len(r) >= 2])
    return a[:, 0], a[:, 1]


def baseline(y, lam=1e5, p=0.01, niter=10):
    from scipy import sparse
    L = len(y)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    w = np.ones(L)
    for _ in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w * y)
        w = p * (y > z) + (1 - p) * (y < z)
    return z


cands = []
for p in glob.glob(os.path.join(ROOT, "**", "*.txt"), recursive=True):
    name = os.path.basename(p)
    low = any(k in name.lower() for k in ["tio2", "tio", "eryanghuatai", "ti02", "fs"])
    if not low:
        continue
    try:
        x, y = load(p)
    except Exception as e:
        print("ERR", name, e)
        continue
    if x.min() > 150:
        continue
    m = x <= 900
    xs, ys = x[m], y[m]
    if len(xs) < 100:
        continue
    try:
        z = baseline(ys, 1e4, 0.5)
    except Exception:
        z = np.percentile(ys, 10)
    yy = ys - z
    sm = savgol_filter(yy, 11, 3)
    noise = np.std(sm[xs < 200]) + 1e-9
    pk, prop = find_peaks(sm, prominence=5 * noise, distance=8)
    top = sorted(zip(prop["prominences"], xs[pk]), reverse=True)[:4]
    print("%-42s %5.0f-%5.0f n=%4d  peaks=%s" % (
        name, xs.min(), x.max(), len(xs),
        ", ".join("%.0f(%.0f)" % (pos, pr / noise) for pr, pos in top)))
