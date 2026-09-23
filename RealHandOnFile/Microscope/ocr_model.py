import asyncio
import os
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.globalization import Language
from winrt.windows.graphics.imaging import BitmapDecoder
from winrt.windows.storage import StorageFile

async def run_ocr():
    try:
        engine = OcrEngine.try_create_from_user_profile_languages()
        if engine is None:
            engine = OcrEngine.try_create_from_language(Language("zh-CN"))

        model_dir = r"e:\latex_AI\MUCMAterialEXperiment\Microscope\model"
        output_path = r"e:\latex_AI\MUCMAterialEXperiment\Microscope\ocr_model_output.txt"
        
        files = sorted(os.listdir(model_dir), key=lambda x: int(x.split('(')[0].replace('.png','')) if '(' not in x else int(x.split('(')[0]))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for filename in files:
                if not filename.endswith('.png'):
                    continue
                file_path = os.path.join(model_dir, filename)
                file = await StorageFile.get_file_from_path_async(file_path)
                stream = await file.open_async(0)
                decoder = await BitmapDecoder.create_async(stream)
                sb = await decoder.get_software_bitmap_async()
                res = await engine.recognize_async(sb)
                f.write(f"--- OCR RESULT {filename} START ---\n")
                for line in res.lines:
                    f.write(line.text + "\n")
                f.write(f"--- OCR RESULT {filename} END ---\n\n")
                print(f"Processed: {filename}")
        
        print("OCR complete!")
        
    except Exception as e:
        print("Error during OCR:", e)

if __name__ == "__main__":
    asyncio.run(run_ocr())
