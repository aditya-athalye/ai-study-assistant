import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your local modules
# Note: These use relative imports (e.g., .llm) assuming you run this as a module
from .llm import ask_llm
from .vectordb import add_notes_to_db, search_notes
from .voice import speech_to_text, text_to_speech

app = FastAPI()

# PORT for Railway/Render
PORT = int(os.getenv("PORT", 10000))

# Upload folder setup
# We use /tmp for Render because other folders are read-only in some environments
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# 1. SERVE UPLOADED FILES
# -------------------------
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# -------------------------
# 2. API ROUTES
# -------------------------

@app.post("/ask")
async def ask(question: str = Form(...)):
    context = search_notes(question)
    answer = ask_llm(context, question)
    return {"answer": answer}

@app.post("/upload-notes")
async def upload_notes(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    add_notes_to_db(file_path)

    return {"message": "Notes uploaded successfully!"}

@app.post("/voice-to-text")
async def vtt(file: UploadFile = File(...)):
    audio_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    text = speech_to_text(audio_path)
    return {"text": text}

@app.post("/text-to-voice")
async def ttv(text: str = Form(...)):
    audio_path = text_to_speech(text)
    # The frontend expects a relative path like "uploads/filename.mp3"
    # Ensure text_to_speech returns a path that works with the /uploads mount
    return {"audio": audio_path}

# -------------------------
# 3. SERVE FRONTEND (STATIC FILES)
# -------------------------
# This MUST come after the API routes so it doesn't block them.

# Get the absolute path to the "static" folder inside "backend"
# This ensures it works correctly on Render regardless of the working directory
static_path = os.path.join(os.path.dirname(__file__), "static")

# Check if directory exists to avoid startup errors if you forgot to create it
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    print(f"WARNING: Static folder not found at {static_path}. Frontend will not load.")