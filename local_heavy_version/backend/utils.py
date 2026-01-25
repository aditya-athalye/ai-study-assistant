import pdfplumber

def extract_text(path):
    text = ""
    if path.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    elif path.endswith(".txt"):
        text = open(path, "r", encoding="utf-8").read()
    else:
        return ""
    return text
