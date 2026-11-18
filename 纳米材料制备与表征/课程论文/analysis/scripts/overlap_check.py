# -*- coding: utf-8 -*-
"""Rough self-check: character n-gram overlap between the paper and the lecture notes."""
import re, glob, os

BASE = r"E:\latex_AI\纳米材料制备与表征"
PAPER = [
    os.path.join(BASE, "课程论文", "content", "abstract.tex"),
] + sorted(glob.glob(os.path.join(BASE, "课程论文", "content", "body", "*.tex")))
LECT = [
    os.path.join(BASE, "X射线粉末衍射", "X射线粉末衍射.md"),
    os.path.join(BASE, "扫描电子显微镜", "实验讲义.md"),
    os.path.join(BASE, "拉曼散射", "实验讲义.md"),
    os.path.join(BASE, "磁控溅射", "实验讲义.md"),
]
N = 13


def norm(t):
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", "", t)
    t = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", t)
    return t


def grams(t, n=N):
    return {t[i:i + n] for i in range(len(t) - n + 1)}


paper = "".join(norm(open(p, encoding="utf-8").read()) for p in PAPER)
gp = grams(paper)
lect = "".join(norm(open(p, encoding="utf-8").read()) for p in LECT if os.path.exists(p))
gl = grams(lect)
inter = gp & gl
print("paper chars: %d, n-grams: %d" % (len(paper), len(gp)))
print("lecture n-grams: %d" % len(gl))
print("overlapping n-grams: %d (%.2f%% of paper)" % (len(inter), 100.0 * len(inter) / max(1, len(gp))))
for s in list(inter)[:15]:
    print("  ", s)
