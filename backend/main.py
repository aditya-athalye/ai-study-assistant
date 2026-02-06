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
PORT = int(os.getenv("PORT", 10000))
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
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# -------------------------
# API ROUTES
# -------------------------

@app.post("/ask")
async def ask(
    question: str = Form(...),
    session_id: str = Form(...) # <--- Recieves Session ID from JS
):
    # Search Global + Session ID notes
    context = search_notes(question, session_id)
    answer = ask_llm(context, question)
    return {"answer": answer}

@app.post("/upload-notes")
async def upload_notes(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    is_admin: str = Form("false") # <--- Recieves "true" or "false" string
):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Convert string to boolean
    admin_flag = (is_admin.lower() == 'true')
    
    add_notes_to_db(file_path, session_id, is_admin=admin_flag)
    return {"message": "Notes processed and stored!"}

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
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")