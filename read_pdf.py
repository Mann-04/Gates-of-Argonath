"""Read PDF and find Model Based works section"""
import pdfplumber
import sys

pdf_path = r"c:\Users\91890\Downloads\RM-Review-2-Guidelines.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Search through all pages
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                # Look for Model Based section
                if 'model' in text.lower() and ('based' in text.lower() or 'base' in text.lower()) and 'work' in text.lower():
                    print(f"\n{'='*80}")
                    print(f"Found on page {page_num + 1}")
                    print(f"{'='*80}\n")
                    print(text)
                    print(f"\n{'='*80}\n")
                    break
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
