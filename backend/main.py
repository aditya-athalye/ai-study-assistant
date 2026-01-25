import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from .llm import ask_llm
from .vectordb import add_notes_to_db, search_notes
from .voice import speech_to_text, text_to_speech

app = FastAPI()

# -------------------------
# CONFIGURATION
# -------------------------
# Render provides the PORT environment variable
PORT = int(os.getenv("PORT", 10000))

# Use /tmp for uploads (Render's disk is ephemeral, so /tmp is the safe place)
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# MIDDLEWARE
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# STATIC MOUNTS
# -------------------------
# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# -------------------------
# API ROUTES
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
    return {"audio": audio_path}

# -------------------------
# FRONTEND SERVING
# -------------------------
# Mount the static directory to serve HTML/CSS/JS
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")