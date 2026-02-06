import os
import google.generativeai as genai
import PyPDF2

# Configure Gemini with your API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text(path):
    """
    Extracts text from PDF, TXT, or Images using Gemini Vision.
    Respects original filename case to prevent 'No such file' errors.
    """
    # 1. Check if file exists (Crucial step)
    if not os.path.exists(path):
        print(f"[ERROR] File not found at path: {path}")
        return ""

    # 2. Get extension safely
    ext = os.path.splitext(path)[1].lower()
    
    try:
        # Image Handling (Handwriting OCR)
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".heic"]:
            print(f"[INFO] Analyzing Image with Gemini Vision: {path}")
            model = genai.GenerativeModel('gemini-1.5-flash')
            with open(path, "rb") as image_file:
                image_data = image_file.read()
            response = model.generate_content([
                "Transcribe the text in this image exactly.",
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            return response.text if response else ""

        # PDF Handling (Standard)
        elif ext == ".pdf":
            reader = PyPDF2.PdfReader(path)
            text = ""
            for p in reader.pages:
                text += p.extract_text() or ""
            return text

        # TXT Handling
        elif ext == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        return ""
    
    return ""