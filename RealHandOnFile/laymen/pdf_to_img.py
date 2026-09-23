import fitz

doc = fitz.open(r"e:\latex_AI\Experiment\image_to_pdf_docsmall.com.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=150)
pix.save(r"e:\latex_AI\Experiment\page_0.png")
if len(doc) > 1:
    pix = doc[1].get_pixmap(dpi=150)
    pix.save(r"e:\latex_AI\Experiment\page_1.png")
print(f"Extracted {len(doc)} pages as images.")
