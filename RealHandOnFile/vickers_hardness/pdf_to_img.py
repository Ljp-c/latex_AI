import fitz

doc = fitz.open(r"E:\latex_AI\MUCMAterialEXperiment\vickers_hardness\硬度-实验报告模板.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save(r"E:\latex_AI\MUCMAterialEXperiment\vickers_hardness\page_0.png")
if len(doc) > 1:
    pix = doc[1].get_pixmap(dpi=150)
    pix.save(r"E:\latex_AI\MUCMAterialEXperiment\vickers_hardness\page_1.png")
print(f"Extracted {len(doc)} pages as images.")
