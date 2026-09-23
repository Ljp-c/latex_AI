"""OCR the Hall Effect data image using Windows built-in OCR."""
import asyncio
import sys

async def run_ocr():
    try:
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.globalization import Language
        from winrt.windows.graphics.imaging import BitmapDecoder
        from winrt.windows.storage import StorageFile
        
        engine = OcrEngine.try_create_from_user_profile_languages()
        if engine is None:
            engine = OcrEngine.try_create_from_language(Language("zh-CN"))
        
        file_path = r"E:\latex_AI\RealHandOnFile\horeEffect\ReportTemplate\data\32fcd6aca9612af39d4a7387746935a3.jpg"
        file = await StorageFile.get_file_from_path_async(file_path)
        stream = await file.open_async(0)
        decoder = await BitmapDecoder.create_async(stream)
        sb = await decoder.get_software_bitmap_async()
        res = await engine.recognize_async(sb)
        print("=== Windows OCR Results ===")
        for line in res.lines:
            print(line.text)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_ocr())
