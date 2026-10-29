# -*- coding: utf-8 -*-
"""
单晶硅 PDF 卡片的计算与绘制（图 2-6、表 2-1）

思路
----
1. 枚举 hkl（取 h>=k>=l>=0 的独立组合，其余排列由多重性统一计入）；
2. 用 Fd-3m 的 8 个原子坐标按 F = f * sum(exp(2*pi*i*(hx+ky+lz))) 求结构因子，
   |F|^2 = 0 的晶面即消光，直接舍弃；
3. 立方晶系 d = a / sqrt(h^2+k^2+l^2)，由 Bragg 方程得 2*theta；
4. 多重性 N 由 "排列数 x 2^(非零指数个数)" 得到，含正负号；
5. 相对强度 I ∝ N * |F|^2 * LP，分别用常数 f=14 和 Cromer-Mann f(s) 两种模型；
6. 按 d 分组（如 333 与 511 的 d 相同），组内强度相加，归一化后画棒图。

运行：python pdfcard.py
输出：终端打印表 2-1 的 LaTeX 行；在 ../assets/pdfcard.png 生成两面板棒图。
"""
import itertools
import math
import os

import matplotlib
matplotlib.use("Agg")           # 无界面后端，便于在脚本中直接保存图片
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

A = 5.43                        # 点阵常数 / Å
LAM = 1.5406                    # Cu Kα1 波长 / Å
F0 = 14                         # 常数原子散射因子：Si 的原子序数
B_T = 0.5                       # 温度因子 / Å^2
HMAX = 8                        # 枚举范围：0 <= l <= k <= h <= HMAX

# Fd-3m 的 8 个 Si 原子分数坐标
ATOMS = [
    (0.00, 0.00, 0.00), (0.00, 0.50, 0.50),
    (0.50, 0.00, 0.50), (0.50, 0.50, 0.00),
    (0.25, 0.25, 0.25), (0.25, 0.75, 0.75),
    (0.75, 0.25, 0.75), (0.75, 0.75, 0.25),
]

# Si 的 Cromer-Mann 系数
CM_A = (6.2915, 3.0353, 1.9891, 1.5410)
CM_B = (2.4386, 32.3337, 0.6785, 81.6937)
CM_C = 1.1407


def structure_factor(h, k, l):
    """|F|/f：8 个原子相位因子的复数和的模。"""
    re = im = 0.0
    for x, y, z in ATOMS:
        phi = 2.0 * math.pi * (h * x + k * y + l * z)
        re += math.cos(phi)
        im += math.sin(phi)
    return math.hypot(re, im)


def f_cm(s):
    """Cromer-Mann 原子散射因子 f(s)，s = sin(theta)/lambda。"""
    return sum(a * math.exp(-b * s * s) for a, b in zip(CM_A, CM_B)) + CM_C


def multiplicity(h, k, l):
    """等价晶面数：排列数 x 2^(非零指数个数)。"""
    perms = set(itertools.permutations((h, k, l)))
    return sum(2 ** sum(1 for v in p if v != 0) for p in perms)


def collect_reflections():
    """枚举允许反射，按 d 分组后返回列表（已按 d 降序排列）。"""
    groups = {}
    for h in range(0, HMAX + 1):
        for k in range(0, h + 1):
            for l in range(0, k + 1):
                if h == k == l == 0:
                    continue
                fm = structure_factor(h, k, l)
                if fm < 1e-6:                       # 结构因子为零：消光
                    continue
                d = A / math.sqrt(h * h + k * k + l * l)
                if LAM / (2.0 * d) > 1.0:           # 超出 Cu Kα1 的衍射极限
                    continue
                two_theta = 2.0 * math.degrees(math.asin(LAM / (2.0 * d)))
                theta = math.radians(two_theta / 2.0)
                lp = (1.0 + math.cos(math.radians(two_theta)) ** 2) / (
                    math.sin(theta) ** 2 * math.cos(theta))
                s = 1.0 / (2.0 * d)
                n = multiplicity(h, k, l)
                g = groups.setdefault(round(d, 5), {
                    "d": d, "two_theta": two_theta, "F2": (F0 * fm) ** 2,
                    "mult": 0, "I14": 0.0, "Ifs": 0.0, "hkl": [],
                })
                if (h, k, l) not in g["hkl"]:
                    g["hkl"].append((h, k, l))
                g["mult"] += n
                g["I14"] += n * (F0 * fm) ** 2 * lp
                # |F| 中的 f(s) 与温度因子都只影响强度，不改变消光判断
                g["Ifs"] += n * (f_cm(s) * fm) ** 2 * lp * math.exp(-2.0 * B_T * s * s)
    rows = sorted(groups.values(), key=lambda r: r["d"], reverse=True)

    i14_max = max(r["I14"] for r in rows)
    ifs_max = max(r["Ifs"] for r in rows)
    for r in rows:
        r["I14r"] = 100.0 * r["I14"] / i14_max
        r["Ifsr"] = 100.0 * r["Ifs"] / ifs_max
        r["hkl"].sort(reverse=True)         # 让 511/333 这类退化组合按指数降序显示
        r["label"] = "/".join("".join(str(v) for v in hkl) for hkl in r["hkl"])
    return rows


def print_latex_rows(rows):
    """打印可直接粘贴到表 2-1 的行。"""
    for r in rows:
        print("{} & {:.4f} & {:.2f} & {} & {:.0f} & {:.1f} & {:.1f} \\\\".format(
            r["label"], r["d"], r["two_theta"], r["mult"], r["F2"], r["I14r"], r["Ifsr"]))


def plot_sticks(rows, outfile):
    """画两面板棒图：左为常数 f=14，右为 f(s)+温度因子。"""
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                         "axes.linewidth": 0.8})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    panels = [(axes[0], "I14r", "(a) constant $f=14$"),
              (axes[1], "Ifsr", "(b) $f(s)$ + $B=0.5$ Å$^2$")]
    for ax, key, title in panels:
        for r in rows:
            ax.vlines(r["two_theta"], 0.0, r[key], color="#365F91", linewidth=1.1)
        ax.set_xlim(20, 160)
        ax.set_ylim(0, 112)
        ax.xaxis.set_major_locator(MultipleLocator(20))
        ax.yaxis.set_major_locator(MultipleLocator(20))
        ax.grid(True, linestyle=":", linewidth=0.45, color="#999999")
        ax.set_xlabel(r"$2\theta$ (degree)")
        ax.set_title(title, fontsize=8.5, pad=4)
        ax.tick_params(direction="in", top=True, right=True, length=2.5)
    axes[0].set_ylabel("Relative intensity (%)")

    # 标注主要衍射线
    marked = {"111", "220", "311", "400", "331", "422", "511/333", "440"}
    for ax, key, _ in panels:
        for r in rows:
            if r["label"] in marked:
                ax.text(r["two_theta"], r[key] + 3.0, r["label"], rotation=90,
                        ha="center", va="bottom", fontsize=5.8, color="#243F60")
    fig.tight_layout(pad=0.4)
    fig.savefig(outfile, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    outdir = os.path.abspath(outdir)
    rows = collect_reflections()
    print_latex_rows(rows)
    plot_sticks(rows, os.path.join(outdir, "pdfcard.png"))
    print("共 {} 条衍射线，图已保存到 {}".format(len(rows), os.path.join(outdir, "pdfcard.png")))


if __name__ == "__main__":
    main()
