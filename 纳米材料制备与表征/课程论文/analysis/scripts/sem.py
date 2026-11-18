# -*- coding: utf-8 -*-
"""SEM: morphology plate, watershed grain sizing, histograms."""
import os, re, csv
import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage import filters, morphology, segmentation, measure

BASE = r"E:\latex_AI\纳米材料制备与表征\课程论文"
ROOT = os.path.join(BASE, "analysis", "data", "sem", "SEM专业实验-2024级（包含EDS）", "SEM 1-10组", "5")
OUT = os.path.join(BASE, "analysis", "outputs")
FIG = os.path.join(BASE, "figures")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.linewidth": 0.8,
    "xtick.direction": "in", "ytick.direction": "in", "legend.frameon": False,
    "savefig.bbox": "tight",
})


def meta(name):
    d = {}
    with open(os.path.join(ROOT, name + ".txt"), "r", errors="ignore") as fh:
        for line in fh:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                d[k] = v
    return d


def load(name, crop=(8, 396, 8, 604)):
    path = os.path.join(ROOT, name + ".jpg")
    buf = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)
    y0, y1, x0, x1 = crop
    return img[y0:y1, x0:x1].astype(float) / 255.0, float(meta(name)["PixelSize"])


def segment(img, min_area_px=100, h=1.0, hmax=2.0):
    blur = filters.gaussian(img, h)
    th = filters.threshold_otsu(blur)
    bw = blur < th
    bw = morphology.remove_small_objects(bw, min_area_px)
    bw = morphology.opening(bw, morphology.disk(1))
    dist = cv2.distanceTransform(bw.astype(np.uint8), cv2.DIST_L2, 5)
    markers = measure.label(morphology.h_maxima(filters.gaussian(dist, 1.0), hmax))
    lab = segmentation.watershed(-dist, markers, mask=bw)
    return lab


def sizes_nm(lab, nm_per_px):
    props = measure.regionprops(lab)
    d = []
    for p in props:
        if p.area < 100:
            continue
        eq = 2 * np.sqrt(p.area / np.pi) * nm_per_px
        d.append(eq)
    return np.array(d)


def overlay(img, lab, path):
    rgb = np.dstack([img] * 3)
    b = segmentation.find_boundaries(lab, mode="inner")
    rgb[b] = [1.0, 0.1, 0.1]
    fig, ax = plt.subplots(figsize=(5.2, 3.9))
    ax.imshow(rgb, interpolation="nearest")
    ax.set_axis_off()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    names = ["200_q001", "300_q006", "500_q001", "700_q001", "900_q001"]
    temps = {"200_q001": 200, "300_q006": 300, "500_q001": 500, "700_q001": 700, "900_q001": 900}
    stats = {}
    for n in names:
        img, nm = load(n)
        lab = segment(img)
        d = sizes_nm(lab, nm)
        stats[n] = dict(px=nm, n=len(d), mean=float(np.mean(d)) if len(d) else 0,
                        sd=float(np.std(d)) if len(d) else 0,
                        p50=float(np.median(d)) if len(d) else 0,
                        dmin=float(np.min(d)) if len(d) else 0,
                        dmax=float(np.max(d)) if len(d) else 0)
        overlay(img, lab, os.path.join(OUT, "sem_overlay_%s.png" % n))
        print("%-10s %.3f nm/px  N=%3d  mean=%6.1f  sd=%5.1f  median=%6.1f" %
              (n, nm, stats[n]["n"], stats[n]["mean"], stats[n]["sd"], stats[n]["p50"]))
        np.save(os.path.join(OUT, "sem_sizes_%s.npy" % n), d)

    # ---------- morphology plate ----------
    fig = plt.figure(figsize=(6.9, 3.6))
    gs = fig.add_gridspec(2, 6, hspace=0.06, wspace=0.06)
    cells = [(0, slice(0, 2)), (0, slice(2, 4)), (0, slice(4, 6)),
             (1, slice(0, 3)), (1, slice(3, 6))]
    letters = "abcde"
    for (r, cs), n, L in zip(cells, names, letters):
        ax = fig.add_subplot(gs[r, cs])
        path = os.path.join(ROOT, n + ".jpg")
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        ax.imshow(img, cmap="gray", interpolation="nearest")
        ax.set_axis_off()
        ax.text(0.02, 0.97, "(%s) %d $\\degree$C" % (L, temps[n]), transform=ax.transAxes,
                color="white", fontsize=7.5, va="top", ha="left")
    fig.savefig(os.path.join(FIG, "fig6_sem.pdf"))
    fig.savefig(os.path.join(FIG, "fig6_sem.png"), dpi=600)
    plt.close(fig)

    # ---------- size histograms ----------
    hist_names = ["300_q006", "500_q001", "700_q001"]
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.4))
    for ax, n in zip(axes, hist_names):
        d = np.load(os.path.join(OUT, "sem_sizes_%s.npy" % n))
        ax.hist(d, bins=18, color="#4a5568", edgecolor="white", linewidth=0.4)
        ax.axvline(np.mean(d), color="#c53030", lw=1.0, ls="--")
        ax.set_title("%d $\\degree$C  (n = %d)" % (temps[n], len(d)), fontsize=8)
        ax.set_xlabel("Particle size (nm)")
        if n == "300_q006":
            ax.set_ylabel("Count")
        ax.text(0.96, 0.92, "%.0f $\\pm$ %.0f nm" % (np.mean(d), np.std(d)),
                transform=ax.transAxes, ha="right", va="top", fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig7_sem_hist.pdf"))
    fig.savefig(os.path.join(FIG, "fig7_sem_hist.png"), dpi=600)
    plt.close(fig)

    with open(os.path.join(OUT, "sem_sizes.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("image,temp_C,nm_per_px,N,mean_nm,sd_nm,median_nm,min_nm,max_nm\n")
        for n in names:
            s = stats[n]
            fh.write("%s,%d,%.4f,%d,%.2f,%.2f,%.2f,%.2f,%.2f\n" % (
                n, temps[n], s["px"], s["n"], s["mean"], s["sd"], s["p50"], s["dmin"], s["dmax"]))
