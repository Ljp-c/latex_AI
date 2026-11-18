# -*- coding: utf-8 -*-
"""Fibre diameter statistics for the electrospun mat (bright fibres on dark)."""
import os
import numpy as np
import cv2
from skimage import filters, morphology, measure


ROOT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\sem\SEM专业实验-2024级（包含EDS）\SEM 1-10组\5"
OUT = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs"

name = "spin_q001"
meta = {}
for line in open(os.path.join(ROOT, name + ".txt"), errors="ignore"):
    if "=" in line:
        k, v = line.strip().split("=", 1)
        meta[k] = v
nm = float(meta["PixelSize"])
print("PixelSize nm/px", nm, "MicronMarker", meta.get("MicronMarker"), "Mag", meta.get("Magnification"))

img = cv2.imdecode(np.fromfile(os.path.join(ROOT, name + ".jpg"), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
img = img[6:400, 6:604].astype(float) / 255.0
th = filters.threshold_otsu(img)
bw = img > th
bw = morphology.remove_small_objects(bw, 60)
dist = cv2.distanceTransform(bw.astype(np.uint8), cv2.DIST_L2, 5)
skel = morphology.skeletonize(bw)
vals = dist[skel]
vals = vals[vals > 1]
d = 2 * vals * nm
print("n=%d mean=%.0f sd=%.0f median=%.0f min=%.0f max=%.0f" %
      (len(d), d.mean(), d.std(), np.median(d), d.min(), d.max()))
np.save(os.path.join(OUT, "fibre_d.npy"), d)
print("coverage", bw.mean())
