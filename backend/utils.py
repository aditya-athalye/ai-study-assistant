import PyPDF2

def extract_text(path):
    path = path.lower()

    # PDF
    if path.endswith(".pdf"):
        reader_pdf = PyPDF2.PdfReader(path)
        text = ""
        for p in reader_pdf.pages:
            text += p.extract_text() or ""
        return text

    # TXT
    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # Images not supported in deployed version (too heavy)
    if path.endswith((".jpg", ".jpeg", ".png")):
        return "Image OCR is not available in the deployed version due to memory constraints. Please use PDF or TXT files."

    return ""