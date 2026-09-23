import asyncio
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.globalization import Language
from winrt.windows.graphics.imaging import BitmapDecoder
from winrt.windows.storage import StorageFile

async def run_ocr():
    try:
        engine = OcrEngine.try_create_from_user_profile_languages()
        if engine is None:
            engine = OcrEngine.try_create_from_language(Language("zh-CN"))

        for p in range(4, 6):
            file_path = f"E:\\latex_AI\\Experiment\\page_{p}.png"
            file = await StorageFile.get_file_from_path_async(file_path)
            stream = await file.open_async(0)
            decoder = await BitmapDecoder.create_async(stream)
            sb = await decoder.get_software_bitmap_async()
            res = await engine.recognize_async(sb)
            print(f"--- OCR RESULT PAGE {p} START ---")
            for line in res.lines: print(line.text)
            print(f"--- OCR RESULT PAGE {p} END ---")
        
    except Exception as e:
        print("Error during OCR:", e)

if __name__ == "__main__":
    asyncio.run(run_ocr())
