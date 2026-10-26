A = [("狗",0.95),("狗",0.91),("狗",0.80),("猫",0.75),("狗",0.63),("狗",0.58),("狗",0.53),("猫",0.51),
     ("狗",0.49),("猫",0.48),("猫",0.47),("猫",0.46),("狗",0.43),("猫",0.42),("猫",0.35),("猫",0.31),
     ("狗",0.29),("猫",0.20),("猫",0.12),("狗",0.06)]
B = [("狗",0.90),("狗",0.85),("狗",0.80),("狗",0.75),("狗",0.70),("猫",0.66),("狗",0.62),("狗",0.55),
     ("狗",0.52),("狗",0.49),("猫",0.48),("猫",0.45),("猫",0.41),("猫",0.38),("猫",0.35),("猫",0.31),
     ("狗",0.25),("猫",0.20),("猫",0.09),("猫",0.02)]

def sweep(data):
    n_pos = sum(1 for lab, _ in data if lab == "狗")
    tp = fp = 0
    X, Y = [0], [1]                      # 起点 (R=0, P=1)
    for lab, _ in data:
        tp += lab == "狗"; fp += lab == "猫"
        P, R = tp / (tp + fp), tp / n_pos
        X.append(R); Y.append(P)
        print(f"TP={tp:2d} FP={fp:2d} FN={n_pos-tp:2d} TN={20-tp-fp:2d} P={P:.4f} R={R:.2f} F1={2*P*R/(P+R):.4f}")
    return X, Y

import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]   # 显示中文
xA, yA = sweep(A); xB, yB = sweep(B)
plt.plot(xA, yA, "r-o", ms=3, label="分类器A")
plt.plot(xB, yB, "b-s", ms=3, label="分类器B")
plt.plot([0, 1], [0, 1], "k--", lw=0.8, label="P=R")
plt.xlabel("查全率 R"); plt.ylabel("查准率 P")
plt.xlim(0, 1.02); plt.ylim(0, 1.02); plt.grid(alpha=0.3); plt.legend()
plt.savefig("PR曲线.png", dpi=300)
plt.show()