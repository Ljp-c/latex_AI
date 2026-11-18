import fitz, os
p = r"E:\latex_AI\纳米材料制备与表征\课程论文\main.pdf"
out = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs\pages"
os.makedirs(out, exist_ok=True)
d = fitz.open(p)
print("pages", len(d))
for i in range(len(d)):
    pix = d[i].get_pixmap(dpi=100)
    pix.save(os.path.join(out, "p%02d.png" % (i+1)))
print("done")
