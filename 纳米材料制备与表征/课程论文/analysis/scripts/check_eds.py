import os, re
import numpy as np
ROOT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\sem\SEM专业实验-2024级（包含EDS）\EDS 1-10组\eds"
for rel in [r"5\500.txt", r"5\900.txt", r"1\500-1.txt", r"10\总谱图ceo2.txt"]:
    p = os.path.join(ROOT, rel)
    data, started = [], False
    for line in open(p, errors="ignore"):
        s = line.strip()
        if s.startswith("#SPECTRUM"):
            started = True; continue
        if s.startswith("#"):
            continue
        if started and re.match(r"^[-\d.]+,\s*[-\d.]+", s):
            a, b = s.split(",")
            data.append((float(a), float(b)))
    a = np.array(data)
    print(rel, "n=", len(a), "x", a[:,0].min() if len(a) else None, a[:,0].max() if len(a) else None,
          "ymax", a[:,1].max() if len(a) else None, "ysum", a[:,1].sum() if len(a) else None)
