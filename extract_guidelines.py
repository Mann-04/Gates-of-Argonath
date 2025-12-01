"""Extract Model Based works section from PDF guidelines"""
import pdfplumber

pdf_path = r"c:\Users\91890\Downloads\RM-Review-2-Guidelines.pdf"

with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += page.extract_text() + "\n"
    
    # Find Model Based works section
    lines = full_text.split('\n')
    in_section = False
    section_text = []
    
    for i, line in enumerate(lines):
        if 'model' in line.lower() and 'based' in line.lower() and 'work' in line.lower():
            in_section = True
            section_text.append(line)
            # Get next 50 lines
            for j in range(i+1, min(i+100, len(lines))):
                section_text.append(lines[j])
            break
    
    print("="*80)
    print("MODEL BASED WORKS SECTION:")
    print("="*80)
    print('\n'.join(section_text[:100]))
    
    # Also save to file
    with open('guidelines_section.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(section_text))
