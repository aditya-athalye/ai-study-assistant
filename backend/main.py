import os
import csv
import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

# Import your local modules
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

# File path for the Analytics Log
ANALYTICS_FILE = "/tmp/analytics_log.csv"

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
# HELPER FUNCTIONS
# -------------------------
def log_question(session_id, question):
    """Saves the question and session ID to a CSV file for the HOD."""
    file_exists = os.path.exists(ANALYTICS_FILE)
    
    try:
        with open(ANALYTICS_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Write header if file is new
            if not file_exists:
                writer.writerow(["Timestamp", "Session ID", "Question"])
                
            # Write the data
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, session_id, question])
    except Exception as e:
        print(f"Analytics Log Error: {e}")

# -------------------------
# STATIC MOUNTS
# -------------------------
# Serve uploaded files (if needed for audio playback)
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# -------------------------
# API ROUTES
# -------------------------

@app.post("/ask")
async def ask(
    question: str = Form(...),
    session_id: str = Form(...) 
):
    # 1. Log the question (Analytics)
    log_question(session_id, question)
    
    # 2. Search Pinecone (Global + Session notes)
    context = search_notes(question, session_id)
    
    # 3. Get Answer from LLM
    answer = ask_llm(context, question)
    
    return {"answer": answer}

@app.post("/upload-notes")
async def upload_notes(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    is_admin: str = Form("false") # Receives "true" or "false" string from frontend
):
    # Save file temporarily
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Convert string "true"/"false" to actual Boolean
    admin_flag = (is_admin.lower() == 'true')
    
    # Upload to Pinecone
    add_notes_to_db(file_path, session_id, is_admin=admin_flag)
    
    return {"message": "Notes processed and stored in the Cloud Database!"}

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
# ANALYTICS DOWNLOAD ROUTE
# -------------------------
@app.get("/download-analytics")
async def download_analytics():
    """
    Secret link for the Admin/HOD to download the logs.
    """
    if os.path.exists(ANALYTICS_FILE):
        return FileResponse(
            ANALYTICS_FILE, 
            media_type="text/csv", 
            filename="exam_analytics.csv"
        )
    return {"error": "No data logged yet."}

# -------------------------
# FRONTEND SERVING
# -------------------------
# Mount the static directory to serve HTML/CSS/JS
# This must be the LAST route to avoid conflicts
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")