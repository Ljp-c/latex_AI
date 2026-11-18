import os, re
import numpy as np
ROOT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\sem\SEM专业实验-2024级（包含EDS）\EDS 1-10组\eds"
p = os.path.join(ROOT, r"5\500.txt")
data, started = [], False
for line in open(p, errors="ignore"):
    s = line.strip()
    if s.startswith("#SPECTRUM"): started=True; continue
    if s.startswith("#"): continue
    if started and re.match(r"^[-\d.]+,\s*[-\d.]+", s):
        a,b = s.split(","); data.append((float(a), float(b)))
a = np.array(data)
for lo, hi in [(0.35,0.75),(4.3,4.8)]:
    m = (a[:,0]>=lo)&(a[:,0]<=hi)
    print(lo, hi, "max", a[m,1].max(), "argmax x", a[m][np.argmax(a[m,1]),0])
    print(a[m][::4].round(0).astype(int).tolist()[:14])
