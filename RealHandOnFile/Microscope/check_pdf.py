import sys

try:
    import pypdf
    print("pypdf available")
except ImportError:
    pass

try:
    import PyPDF2
    print("PyPDF2 available")
except ImportError:
    pass

try:
    import fitz
    print("fitz available")
except ImportError:
    pass
