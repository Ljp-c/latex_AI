import fitz
import sys

def read_pdf(file_path):
    print(f"Reading {file_path}")
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    print("\n--- EXTRACTED TEXT (First 2000 chars) ---")
    print(text[:2000])
    
    print("\n--- EXTRACTED TEXT (Last 2000 chars) ---")
    if len(text) > 2000:
        print(text[-2000:])
    
read_pdf(r"E:\latex_AI\MUCMAterialEXperiment\vickers_hardness\硬度-实验报告模板.pdf")
