"""OCR all PNG images in the horeEffect folder using Windows OCR API."""
import asyncio
import os
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.globalization import Language
from winrt.windows.graphics.imaging import BitmapDecoder
from winrt.windows.storage import StorageFile

async def ocr_images():
    engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        engine = OcrEngine.try_create_from_language(Language("zh-CN"))
    
    base_dir = r"e:\latex_AI\MUCMAterialEXperiment\horeEffect"
    # Sort files naturally: 1(3).png, 2(3).png, ... 8.png
    png_files = sorted(
        [f for f in os.listdir(base_dir) if f.endswith('.png')],
        key=lambda x: int(x.split('(')[0]) if '(' in x else int(x.split('.')[0])
    )
    
    all_text = []
    for fname in png_files:
        file_path = os.path.join(base_dir, fname)
        print(f"\n{'='*60}")
        print(f"--- OCR: {fname} ---")
        print(f"{'='*60}")
        try:
            file = await StorageFile.get_file_from_path_async(file_path)
            stream = await file.open_async(0)
            decoder = await BitmapDecoder.create_async(stream)
            sb = await decoder.get_software_bitmap_async()
            res = await engine.recognize_async(sb)
            text = "\n".join(line.text for line in res.lines)
            print(text)
            all_text.append(f"\n=== {fname} ===\n{text}")
        except Exception as e:
            print(f"Error OCR {fname}: {e}")
    
    # Save to file
    output_path = os.path.join(base_dir, "ocr_output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))
    print(f"\nOCR results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(ocr_images())
