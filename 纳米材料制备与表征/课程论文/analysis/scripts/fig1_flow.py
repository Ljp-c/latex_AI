# -*- coding: utf-8 -*-
"""Figure 1: process flow chart of the two preparation routes."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE = r"E:\latex_AI\纳米材料制备与表征\课程论文"
FIG = os.path.join(BASE, "figures")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "savefig.bbox": "tight"})

fig, ax = plt.subplots(figsize=(7.1, 4.4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

C1 = "#e8eef7"
C2 = "#f7f0e6"
EDGE = "#4a5568"


def box(x, y, w, h, text, color, fs=7.2):
    p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
                       linewidth=0.8, edgecolor=EDGE, facecolor=color)
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, linespacing=1.25)


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=7,
                                 linewidth=0.8, color=EDGE, shrinkA=1, shrinkB=1))


ax.text(2.5, 9.55, "(a) Sol-gel route: TiO$_2$ nanoparticles", ha="center", fontsize=8.2)
ax.text(7.5, 9.55, "(b) Electrospinning route: TiO$_2$ nanofibres", ha="center", fontsize=8.2)

# sol-gel lane
sg = [
    (8.6, "15 mL Ti(OBu)$_4$ + 52.5 mL EtOH\n(magnetic stirring) $\\rightarrow$ solution A"),
    (7.2, "15 mL H$_2$O + 6 mL HAc + 52.5 mL EtOH\n+ 6-8 drops HCl, pH $\\leq$ 3 $\\rightarrow$ solution B"),
    (5.8, "A dropped into B, 40 $\\degree$C water bath, 4 h\n$\\rightarrow$ white gel"),
    (4.4, "dried at 80 $\\degree$C for 20 h,\nground $\\rightarrow$ pale-yellow powder"),
    (2.9, "annealed in air, 4 h\n200 / 300 / 400 / 500 / 600 / 700 / 800 / 900 $\\degree$C"),
]
for y, t in sg:
    box(2.5, y, 4.8, 1.15, t, C1)
for (y1, _), (y2, _) in zip(sg, sg[1:]):
    arrow(2.5, y1 - 0.6, 2.5, y2 + 0.6)

# electrospinning lane
es = [
    (8.6, "8.5 mL Ti(OBu)$_4$ + 30 mL EtOH\n+ 0.5 mL acetylacetone $\\rightarrow$ solution A"),
    (7.2, "2 mL HAc + 3 mL H$_2$O + 30 mL EtOH\n$\\rightarrow$ solution B"),
    (5.8, "B into A; 15 mL mixed sol + 1.1 g PVP\nstirred until clear $\\rightarrow$ spinning sol"),
    (4.4, "12-15 kV, 0.02 mL/min,\nroller collector $\\rightarrow$ composite fibre mat"),
    (2.9, "annealed in air, 4 h\n200 / 300 / 400 / 500 / 600 / 700 / 800 / 900 $\\degree$C"),
]
for y, t in es:
    box(7.5, y, 4.8, 1.15, t, C2)
for (y1, _), (y2, _) in zip(es, es[1:]):
    arrow(7.5, y1 - 0.6, 7.5, y2 + 0.6)

box(5.0, 0.75, 8.6, 0.75,
    "Characterisation: XRD  $\\cdot$  Raman  $\\cdot$  SEM/EDS  $\\cdot$  UV-Vis (DRS, Tauc plot)", "#eef2ee", fs=7.4)
arrow(2.5, 2.3, 3.2, 1.15)
arrow(7.5, 2.3, 6.8, 1.15)

fig.savefig(os.path.join(FIG, "fig1_flow.pdf"))
fig.savefig(os.path.join(FIG, "fig1_flow.png"), dpi=600)
print("ok")

