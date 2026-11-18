import fitz, os
p = r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs\eds_report_1.pdf"
if os.path.exists(p):
    d = fitz.open(p)
    print("pages", len(d))
    for i in range(min(2, len(d))):
        pix = d[i].get_pixmap(dpi=110)
        out = p.replace(".pdf", "_p%d.png" % (i+1))
        pix.save(out)
        print(out)
        print(d[i].get_text()[:400])
else:
    print("missing")
