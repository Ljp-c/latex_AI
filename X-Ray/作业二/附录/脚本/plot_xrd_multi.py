#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
plot_xrd_multi.py
=================

作业二专用：读取 make_origin_ready.py 生成的 ready_norm 数据，
绘制“多曲线 + PDF 卡片”的 XRD 图。

本脚本只做三件事：
1. 读取 8 组已归一化的 XRD 数据；
2. 按温度偏移叠图；
3. 在下方画出锐钛矿 PDF 21-1272 / 金红石 PDF 21-1276 的标准棒图，
   并给出 23-30° 的局部放大。

不做峰拟合、Scherrer 尺寸、Spurr-Myers 相含量或晶格参数精修；
这些是后续课程内容。

用法：
    python .\脚本\plot_xrd_multi.py
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NORM_DIR = ROOT / "资料" / "原数据" / "ready_norm"
FIG_DIR = ROOT / "课程论文" / "assets" / "xrd"

SAMPLES = [200, 300, 400, 500, 600, 700, 800, 900]

# PDF 卡片：2theta / 相对强度 / hkl
ANATASE_PDF: List[Tuple[float, float, str]] = [
    (25.28, 100, "(101)"),
    (36.95, 10, "(103)"),
    (37.80, 20, "(004)"),
    (38.58, 10, "(112)"),
    (48.05, 35, "(200)"),
    (53.89, 20, "(105)"),
    (55.06, 20, "(211)"),
    (62.12, 4, "(213)"),
    (62.69, 14, "(204)"),
    (68.76, 6, "(116)"),
    (70.31, 6, "(220)"),
    (74.03, 2, "(107)"),
    (75.03, 10, "(215)"),
    (76.02, 4, "(301)"),
]
RUTILE_PDF: List[Tuple[float, float, str]] = [
    (27.45, 100, "(110)"),
    (36.09, 50, "(101)"),
    (39.19, 8, "(200)"),
    (41.23, 25, "(111)"),
    (44.05, 10, "(210)"),
    (54.32, 60, "(211)"),
    (56.64, 20, "(220)"),
    (62.75, 10, "(002)"),
    (64.04, 10, "(310)"),
    (69.01, 20, "(301)"),
    (69.79, 12, "(112)"),
]


def load_xy(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    rows = []
    with open(path, encoding="gbk") as fh:
        for i, raw in enumerate(fh):
            if i < 3:
                continue
            line = raw.strip()
            if not line:
                continue
            parts = re.split(r"\t+|\s+", line)
            if len(parts) < 2:
                continue
            try:
                rows.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    arr = np.asarray(rows, dtype=float)
    order = np.argsort(arr[:, 0])
    return arr[order, 0], arr[order, 1]


def sample_colors():
    cmap = plt.get_cmap("viridis")
    return {t: cmap(v) for t, v in zip(SAMPLES, np.linspace(0.12, 0.88, len(SAMPLES)))}


def setup_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 9,
            "legend.fontsize": 7.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.linewidth": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.minor.size": 2.0,
            "ytick.minor.size": 2.0,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def plot() -> None:
    colors = sample_colors()
    offset = 100.0
    fig = plt.figure(figsize=(7.2, 8.8))
    gs = GridSpec(3, 1, height_ratios=[2.4, 0.65, 1.1], hspace=0.08)
    ax = fig.add_subplot(gs[0])
    axpdf = fig.add_subplot(gs[1], sharex=ax)
    ax2 = fig.add_subplot(gs[2])

    handles = []
    for i, t in enumerate(SAMPLES):
        x, y = load_xy(NORM_DIR / f"{t}.txt")
        (line,) = ax.plot(x, y + i * offset, color=colors[t], lw=0.65, zorder=2)
        handles.append(line)

    ax.set_xlim(20, 80)
    ax.set_ylim(-5, len(SAMPLES) * offset + 18)
    ax.set_ylabel("Intensity (a.u.)")
    ax.set_yticks([])
    ax.tick_params(labelbottom=False)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(2))
    ax.text(0.012, 0.985, "(a)", transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")
    ax.legend(
        handles=handles,
        labels=[f"{t} $^\\circ$C" for t in SAMPLES],
        loc="upper left",
        bbox_to_anchor=(1.015, 1.0),
        frameon=False,
        fontsize=7.5,
        handlelength=1.2,
        labelspacing=0.32,
        borderaxespad=0.0,
    )

    y_anatase, y_rutile, stick_h = 1.05, 0.05, 0.72
    for pos, inten, _ in ANATASE_PDF:
        axpdf.vlines(pos, y_anatase, y_anatase + inten / 100.0 * stick_h, color="tab:green", linewidth=1.1)
    for pos, inten, _ in RUTILE_PDF:
        axpdf.vlines(pos, y_rutile, y_rutile + inten / 100.0 * stick_h, color="tab:red", linewidth=1.1)
    axpdf.axhline(1.0, color="0.75", lw=0.5, zorder=0)
    for pos, inten, hkl in ANATASE_PDF:
        if hkl in ("(101)", "(004)", "(200)", "(211)"):
            axpdf.text(pos, y_anatase + inten / 100.0 * stick_h + 0.04, hkl, color="tab:green", fontsize=6.2, ha="center", va="bottom")
    for pos, inten, hkl in RUTILE_PDF:
        if hkl in ("(110)", "(101)", "(211)"):
            axpdf.text(pos, y_rutile + inten / 100.0 * stick_h + 0.04, hkl, color="tab:red", fontsize=6.2, ha="center", va="bottom")
    axpdf.text(79.5, y_anatase + 0.50, "Anatase 71-1167", color="tab:green", fontsize=7.2, va="center", ha="right", bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    axpdf.text(79.5, y_rutile + 0.50, "Rutile 75-1756", color="tab:red", fontsize=7.2, va="center", ha="right", bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    axpdf.set_ylim(-0.05, 2.02)
    axpdf.set_yticks([])
    axpdf.set_xlabel(r"$2\theta$ (degree)")
    axpdf.xaxis.set_major_locator(MultipleLocator(10))
    axpdf.xaxis.set_minor_locator(MultipleLocator(2))
    axpdf.tick_params(axis="y", left=False, right=False)
    axpdf.text(0.012, 0.92, "(b)", transform=axpdf.transAxes, fontsize=10, fontweight="bold", va="top")

    for i, t in enumerate(SAMPLES):
        x, y = load_xy(NORM_DIR / f"{t}.txt")
        mask = (x >= 23.0) & (x <= 30.0)
        ax2.plot(x[mask], y[mask] + i * offset, color=colors[t], lw=0.7, zorder=2)
    ax2.axvline(25.28, color="tab:green", ls="--", lw=0.8, alpha=0.65, zorder=1)
    ax2.axvline(27.45, color="tab:red", ls="--", lw=0.8, alpha=0.65, zorder=1)
    ax2.text(0.326, 0.96, "A(101)", transform=ax2.transAxes, color="tab:green", fontsize=7.5, ha="center", va="top", bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    ax2.text(0.636, 0.96, "R(110)", transform=ax2.transAxes, color="tab:red", fontsize=7.5, ha="center", va="top", bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    ax2.set_xlim(23, 30)
    ax2.set_ylim(-5, len(SAMPLES) * offset + 70)
    ax2.set_xlabel(r"$2\theta$ (degree)")
    ax2.set_ylabel("Intensity (a.u.)")
    ax2.xaxis.set_major_locator(MultipleLocator(1))
    ax2.xaxis.set_minor_locator(MultipleLocator(0.2))
    ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax2.set_yticks([])
    ax2.text(0.012, 0.985, "(c)", transform=ax2.transAxes, fontsize=10, fontweight="bold", va="top")

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / "fig1_xrd_stack.png", dpi=600)
    fig.savefig(FIG_DIR / "fig1_xrd_stack.pdf")
    plt.close(fig)


def main() -> int:
    setup_matplotlib()
    plot()
    print(f"图件已输出到：{FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
