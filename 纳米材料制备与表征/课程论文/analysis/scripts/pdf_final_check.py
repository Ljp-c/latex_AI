import fitz, re
p = r"E:\latex_AI\纳米材料制备与表征\课程论文\交付\纳米材料制备实验课程论文+刘佳鹏+24012639.pdf"
d = fitz.open(p)
print("pages", len(d))
txt = "".join(pg.get_text() for pg in d)
print("CJK", len(re.findall(r"[\u4e00-\u9fff]", txt)))
refs = re.findall(r"\[(\d+)\]", txt)
print("max ref index", max(int(x) for x in refs))
pix = d[len(d)-1].get_pixmap(dpi=100)
pix.save(r"E:\latex_AI\纳米材料制备与表征\课程论文\analysis\outputs\last_page.png")
print("ok")
