import os
import google.generativeai as genai
import PyPDF2

# Configure Gemini with your API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text(path):
    """
    Extracts text from PDF, TXT, or Images using Gemini Vision.
    Capable of reading handwriting.
    """
    if not os.path.exists(path):
        return ""

    ext = os.path.splitext(path)[1].lower()
    
    try:
        # 1. Image Handling (Handwriting OCR)
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            print(f"[INFO] Analyzing Image with Gemini Vision: {path}")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with open(path, "rb") as image_file:
                image_data = image_file.read()
                
            response = model.generate_content([
                "Transcribe the text in this image exactly. If it is handwriting, convert it to digital text.",
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            return response.text

        # 2. PDF Handling (Hybrid: PyPDF2 first, then Vision if needed)
        # Note: For free tier speed, we stick to standard PyPDF2 for PDFs 
        # unless you want to upload PDF Images (scans).
        elif ext == ".pdf":
            reader = PyPDF2.PdfReader(path)
            text = ""
            for p in reader.pages:
                text += p.extract_text() or ""
            return text

        # 3. TXT Handling
        elif ext == ".txt":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        return ""
    
    return ""