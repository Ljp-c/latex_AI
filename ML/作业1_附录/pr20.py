# -*- coding: utf-8 -*-
"""作业1：20 个阈值（各样本预测概率）下的混淆矩阵、P、R、F1 与 P-R 曲线

判正规则：预测概率 >= 阈值 t 判为小狗（正例）。
曲线起点补 (R=0, P=1)，即全部样本都判为反例。
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 题目表 1、表 2，已按预测概率降序
A = [("狗", 0.95), ("狗", 0.91), ("狗", 0.80), ("猫", 0.75), ("狗", 0.63),
     ("狗", 0.58), ("狗", 0.53), ("猫", 0.51), ("狗", 0.49), ("猫", 0.48),
     ("猫", 0.47), ("猫", 0.46), ("狗", 0.43), ("猫", 0.42), ("猫", 0.35),
     ("猫", 0.31), ("狗", 0.29), ("猫", 0.20), ("猫", 0.12), ("狗", 0.06)]
B = [("狗", 0.90), ("狗", 0.85), ("狗", 0.80), ("狗", 0.75), ("狗", 0.70),
     ("猫", 0.66), ("狗", 0.62), ("狗", 0.55), ("狗", 0.52), ("狗", 0.49),
     ("猫", 0.48), ("猫", 0.45), ("猫", 0.41), ("猫", 0.38), ("猫", 0.35),
     ("猫", 0.31), ("狗", 0.25), ("猫", 0.20), ("猫", 0.09), ("猫", 0.02)]


def sweep(data, name):
    n_pos = sum(1 for lab, _ in data if lab == "狗")
    tp = fp = 0
    X, Y = [0.0], [1.0]          # 起点：全判反例
    print(f"\n===== 分类器{name}：20 个阈值 =====")
    print(f"{'k':>2} {'t':>5} {'TP':>3} {'FP':>3} {'FN':>3} {'TN':>3} {'P':>8} {'R':>7} {'F1':>8}")
    for k, (lab, t) in enumerate(data, 1):
        tp += lab == "狗"
        fp += lab == "猫"
        fn, tn = n_pos - tp, len(data) - n_pos - fp
        P, R = tp / (tp + fp), tp / n_pos
        F1 = 2 * P * R / (P + R)
        print(f"{k:>2} {t:>5.2f} {tp:>3} {fp:>3} {fn:>3} {tn:>3} {P:>8.4f} {R:>7.2f} {F1:>8.4f}")
        X.append(R)
        Y.append(P)
    return X, Y


xA, yA = sweep(A, "A")
xB, yB = sweep(B, "B")

plt.figure(figsize=(6, 4.5), dpi=300)
plt.plot(xA, yA, "r-o", ms=4, lw=1.5, label="分类器A")
plt.plot(xB, yB, "b-s", ms=4, lw=1.5, label="分类器B")
plt.plot([0, 1], [0, 1], "k--", lw=0.8, label="P = R")
plt.xlabel("查全率 R")
plt.ylabel("查准率 P")
plt.xlim(0, 1.02)
plt.ylim(0, 1.05)
plt.grid(alpha=0.3)
plt.legend(loc="lower left")
plt.tight_layout()
plt.savefig("PR曲线_20阈值.png")
print("\n图已保存：PR曲线_20阈值.png")
