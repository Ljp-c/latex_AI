"""OCR the Hall Effect experiment data image."""
import sys
sys.path.insert(0, r'e:\latex_AI')

# Try using pytesseract or easyocr
try:
    from PIL import Image
    img = Image.open(r'e:\latex_AI\RealHandOnFile\horeEffect\ReportTemplate\data\32fcd6aca9612af39d4a7387746935a3.jpg')
    print(f"Image size: {img.size}")
except Exception as e:
    print(f"PIL error: {e}")

# Try easyocr
try:
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    result = reader.readtext(r'e:\latex_AI\RealHandOnFile\horeEffect\ReportTemplate\data\32fcd6aca9612af39d4a7387746935a3.jpg')
    print("\n=== EasyOCR Results ===")
    for (bbox, text, conf) in result:
        print(f"  [{conf:.2f}] {text}")
except ImportError:
    print("easyocr not installed")
except Exception as e:
    print(f"easyocr error: {e}")

# Try pytesseract
try:
    import pytesseract
    from PIL import Image
    img = Image.open(r'e:\latex_AI\RealHandOnFile\horeEffect\ReportTemplate\data\32fcd6aca9612af39d4a7387746935a3.jpg')
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    print("\n=== Tesseract Results ===")
    print(text)
except ImportError:
    print("pytesseract not installed")
except Exception as e:
    print(f"pytesseract error: {e}")
