from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .llm import ask_llm
from .vectordb import add_notes_to_db, search_notes
from .voice import speech_to_text, text_to_speech
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve audio files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# ASK AI
# -------------------------
@app.post("/ask")
async def ask(question: str = Form(...)):
    context = search_notes(question)
    answer = ask_llm(context, question)
    return {"answer": answer}

# -------------------------
# Upload Notes → VectorDB
# -------------------------
@app.post("/upload-notes")
async def upload_notes(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    add_notes_to_db(file_path)
    return {"message": "Notes uploaded successfully!"}

# -------------------------
# Whisper STT
# -------------------------
@app.post("/voice-to-text")
async def vtt(file: UploadFile = File(...)):
    audio_path = f"uploads/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())
    text = speech_to_text(audio_path)
    return {"text": text}

# -------------------------
# gTTS TTS
# -------------------------
@app.post("/text-to-voice")
async def ttv(text: str = Form(...)):
    audio_path = text_to_speech(text)
    return {"audio": audio_path}
