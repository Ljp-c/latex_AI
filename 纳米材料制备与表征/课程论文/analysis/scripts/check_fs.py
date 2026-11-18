import os, io, glob
import numpy as np
from scipy.signal import find_peaks, savgol_filter
ROOT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\raman"
targets = ["jingdianfangsi-633-d03-1-10-1.txt","jingdianfangsi-633-d06-1-5-1.txt",
           "fsTiO2-1-5-1-632nm.txt","fsTiO2-PVP-633nm-1-5-1.txt","TIO2+pvp-d03-1-5-1-633.txt"]
for p in glob.glob(os.path.join(ROOT,"**","*.txt"), recursive=True):
    n = os.path.basename(p)
    if n not in targets: continue
    arr = [ln.split() for ln in io.open(p, errors="ignore") if ln.strip() and ln.strip()[0] not in "#"]
    a = np.array([[float(x) for x in r[:2]] for r in arr if len(r)>=2])
    x,y = a[:,0], a[:,1]
    m = x<=1000
    xs,ys = x[m], y[m]
    base = np.polyval(np.polyfit(xs, ys, 3), xs)
    yy = savgol_filter(ys-base, 9, 2)
    noise = 1.4826*np.median(np.abs(np.diff(yy)))/np.sqrt(2)
    pk,pr = find_peaks(yy, prominence=max(0.03*yy.max(),5*noise), distance=6)
    top = sorted([(pr["prominences"][i], xs[pk[i]]) for i in range(len(pk))], reverse=True)[:5]
    print("%-38s %4d-%4d  %s" % (n, xs.min(), xs.max(), ", ".join("%.0f(%0.f)"%(pos,pro) for pro,pos in top)))
