import easyocr
import PyPDF2
from PIL import Image
import os

reader = easyocr.Reader(['en'], gpu=False)

def extract_text(path):
    path = path.lower()

    # PDF
    if path.endswith(".pdf"):
        reader_pdf = PyPDF2.PdfReader(path)
        text = ""
        for p in reader_pdf.pages:
            text += p.extract_text() or ""
        return text

    # Images → OCR
    if path.endswith((".jpg", ".jpeg", ".png")):
        result = reader.readtext(path, detail=0)
        return " ".join(result)

    # TXT
    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    return ""
