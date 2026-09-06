import os
from typing import Optional

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from digital or scanned PDF using pdfplumber, pypdf, or pypdfium2."""
    text_parts = []
    
    # 1. Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
        if text_parts:
            return '\n\n'.join(text_parts)
    except Exception as e:
        print(f"pdfplumber notice: {e}")

    # 2. Try pypdf fallback
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            p_text = page.extract_text()
            if p_text:
                text_parts.append(p_text.strip())
        if text_parts:
            return '\n\n'.join(text_parts)
    except Exception as e:
        print(f"pypdf notice: {e}")

    # 3. Fallback to raw text scan
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
            import re
            # Extract printable ASCII words from raw PDF streams
            words = re.findall(r'[A-Za-z0-9+/=.,:_\-@#₹\s]{4,}', raw)
            if words:
                return ' '.join(words[:2000])
            return raw[:5000]
    except Exception as e:
        return f"[PDF Extraction Error: {str(e)}]"

def extract_text_from_excel(file_path: str) -> str:
    """Extract rows, columns, and cell values from .xlsx or .xls files."""
    try:
        import pandas as pd
        excel_file = pd.ExcelFile(file_path)
        sheet_texts = []
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Drop empty columns/rows
            df = df.dropna(how='all')
            sheet_texts.append(f"=== Sheet: {sheet_name} ===\n" + df.to_string(index=False))
        return '\n\n'.join(sheet_texts)
    except Exception as e:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            lines = []
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                lines.append(f"=== Sheet: {sheet} ===")
                for row in ws.iter_rows(values_only=True):
                    row_vals = [str(v).strip() for v in row if v is not None]
                    if row_vals:
                        lines.append(" | ".join(row_vals))
            return '\n'.join(lines)
        except Exception as ex:
            return f"[Excel Extraction Error: {str(e)} / {str(ex)}]"

def extract_text_from_image(file_path: str) -> str:
    """Extract text from image using Tesseract OCR if installed, with safe fallback and visual metadata."""
    text = ""
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(file_path).convert('L')
        text = pytesseract.image_to_string(img, lang='eng').strip()
    except Exception as e:
        pass

    if text:
        return text

    # Extract visual metadata as structured text
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            w, h = img.size
            format_name = img.format or "IMAGE"
            return f"[Visual Evidence Artifact: {os.path.basename(file_path)} | Dimensions: {w}x{h} px | Format: {format_name}]"
    except Exception:
        return f"[Image Evidence Received: {os.path.basename(file_path)}]"

def extract_text(file_path: str) -> str:
    """Auto-detect file format and extract textual content cleanly."""
    if not os.path.exists(file_path):
        return f"[File not found: {file_path}]"

    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ('.xlsx', '.xls'):
        return extract_text_from_excel(file_path)
    elif ext in ('.txt', '.csv', '.json', '.log'):
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'):
        return extract_text_from_image(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return f"[Unsupported binary format: {ext}]"
