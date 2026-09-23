"""Extract text from old .doc format using olefile and raw text extraction."""
import olefile
import re
import struct

doc_path = r"e:\latex_AI\RealHandOnFile\vickers_hardness\data\24012720(2).doc"

ole = olefile.OleFileIO(doc_path)
print("=== OLE Streams ===")
for stream in ole.listdir():
    print("/".join(stream))

# Try to extract text from WordDocument stream
if ole.exists("WordDocument"):
    data = ole.openstream("WordDocument").read()
    print(f"\n=== WordDocument stream size: {len(data)} bytes ===")
    
    # Try to extract readable text
    # In .doc format, text is stored in the WordDocument stream
    # The FIB (File Information Block) is at the beginning
    
    # Try simple approach: extract all printable ASCII/UTF-16 sequences
    # First check if it's Unicode (UTF-16LE)
    text_parts = []
    
    # Try UTF-16LE decoding of the whole stream
    try:
        decoded = data.decode('utf-16-le', errors='ignore')
        # Filter to printable characters
        cleaned = ''.join(c if c.isprintable() or c in '\n\r\t' else ' ' for c in decoded)
        # Collapse spaces
        cleaned = re.sub(r' {2,}', ' ', cleaned)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        if len(cleaned.strip()) > 50:
            text_parts.append(("UTF-16LE", cleaned))
    except:
        pass
    
    # Try ASCII approach - look for sequences of printable chars
    ascii_text = []
    current = []
    for b in data:
        if 32 <= b < 127 or b in (10, 13):
            current.append(chr(b))
        else:
            if len(current) > 3:
                ascii_text.append(''.join(current))
            current = []
    if current:
        ascii_text.append(''.join(current))
    
    ascii_combined = '\n'.join(ascii_text)
    if len(ascii_combined.strip()) > 50:
        text_parts.append(("ASCII segments", ascii_combined))
    
    for method, text in text_parts:
        print(f"\n=== Text extracted via {method} ===")
        # Print first 5000 chars
        print(text[:5000])

# Also try 1Table or 0Table streams
for stream_name in ["1Table", "0Table"]:
    if ole.exists(stream_name):
        data = ole.openstream(stream_name).read()
        print(f"\n=== {stream_name} stream size: {len(data)} bytes ===")

ole.close()
