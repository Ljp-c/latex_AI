import fitz
p = r"E:\latex_AI\纳米材料制备与表征\课程论文\main.pdf"
d = fitz.open(p)
print("pages", len(d), "metadata", d.metadata.get("title"))
txt = "".join(pg.get_text() for pg in d)
import re
print("CJK chars in PDF:", len(re.findall(r"[\u4e00-\u9fff]", txt)))
pix = d[9].get_pixmap(dpi=100); pix.save(r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs\pages\p10.png")
print("ok")
