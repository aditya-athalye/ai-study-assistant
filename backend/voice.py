import time
from gtts import gTTS
from .main import UPLOAD_FOLDER
from whisper_timestamped import load_model, transcribe

model = load_model("small")

def speech_to_text(path):
    result = transcribe(model, path)
    return result["text"]

def text_to_speech(text):
    timestamp = int(time.time())
    output_path = f"{UPLOAD_FOLDER}/tts_{timestamp}.mp3"

    tts = gTTS(text)
    tts.save(output_path)

    return f"uploads/tts_{timestamp}.mp3"
