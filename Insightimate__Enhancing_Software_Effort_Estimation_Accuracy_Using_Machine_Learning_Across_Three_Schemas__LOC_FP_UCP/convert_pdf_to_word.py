#!/usr/bin/env python3
"""
Convert PDF to Word (DOCX) format
Preserves layout, images, tables, and formatting
"""

from pdf2docx import Converter
import sys

def convert_pdf_to_docx(pdf_file, docx_file):
    """Convert PDF to DOCX with progress display"""
    print(f"Converting {pdf_file} to {docx_file}...")
    print("This may take a few minutes for a 38-page document...")
    
    try:
        cv = Converter(pdf_file)
        cv.convert(docx_file, start=0, end=None)
        cv.close()
        print(f"✓ Conversion complete: {docx_file}")
        return True
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        return False

if __name__ == "__main__":
    pdf_input = "main.pdf"
    docx_output = "main.docx"
    
    success = convert_pdf_to_docx(pdf_input, docx_output)
    sys.exit(0 if success else 1)
