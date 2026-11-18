# -*- coding: utf-8 -*-
import os, glob, io

root = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\raman"
rows = []
for p in glob.glob(os.path.join(root, "**", "*.txt"), recursive=True):
    try:
        with io.open(p, "r", encoding="utf-8", errors="ignore") as fh:
            first = fh.readline().strip()
            fh.seek(0)
            data = [ln.split() for ln in fh if ln.strip() and not ln.startswith("#")]
        xs = [float(d[0]) for d in data if len(d) >= 2]
        if not xs:
            continue
        rows.append((os.path.basename(p), round(min(xs), 1), round(max(xs), 1), len(xs)))
    except Exception as e:
        rows.append((os.path.basename(p), "ERR", str(e)[:30], 0))

rows.sort(key=lambda r: (str(r[1])))
print("%-45s %9s %9s %6s" % ("file", "min", "max", "n"))
for r in rows:
    print("%-45s %9s %9s %6s" % r)
print("total", len(rows))
