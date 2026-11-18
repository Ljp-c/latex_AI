import fitz
p = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs\eds_TiO.pdf"
d = fitz.open(p)
print("pages", len(d))
for i in range(len(d)):
    t = d[i].get_text().strip()
    print("--- page", i+1, "chars", len(t))
    if t:
        print(t[:600])
pix = d[0].get_pixmap(dpi=120)
pix.save(p.replace(".pdf", "_p1.png"))
print("saved png")
