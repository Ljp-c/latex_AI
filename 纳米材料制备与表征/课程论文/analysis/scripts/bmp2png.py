import cv2, numpy as np, os
p = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\data\sem\SEM专业实验-2024级（包含EDS）\EDS 1-10组\eds\5\500.bmp"
img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
print(img.shape, img.dtype)
out = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs\eds5_500.png"
cv2.imencode(".png", img)[1].tofile(out)
print("saved", out)
