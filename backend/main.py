from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()
import os

from .llm import ask_llm
from .vectordb import add_notes_to_db, search_notes
from .voice import speech_to_text, text_to_speech

app = FastAPI()

# PORT for Railway
PORT = int(os.getenv("PORT", 10000))

# Upload folder for Railway
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded audio
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# -------------------------
# ASK LLM
# -------------------------
@app.post("/ask")
async def ask(question: str = Form(...)):
    context = search_notes(question)
    answer = ask_llm(context, question)
    return {"answer": answer}

# -------------------------
# UPLOAD NOTES
# -------------------------
@app.post("/upload-notes")
async def upload_notes(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    add_notes_to_db(file_path)

    return {"message": "Notes uploaded successfully!"}

# -------------------------
# VOICE → TEXT
# -------------------------
@app.post("/voice-to-text")
async def vtt(file: UploadFile = File(...)):
    audio_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    text = speech_to_text(audio_path)
    return {"text": text}

# -------------------------
# TEXT → VOICE
# -------------------------
@app.post("/text-to-voice")
async def ttv(text: str = Form(...)):
    audio_path = text_to_speech(text)
    return {"audio": audio_path}
