import whisper_timestamped as whisper
from gtts import gTTS
import uuid
import os

model = whisper.load_model("base")

def speech_to_text(audio_path):
    result = whisper.transcribe(model, audio_path)
    return result["text"]

def text_to_speech(text):
    filename = f"uploads/{uuid.uuid4()}.mp3"
    tts = gTTS(text)
    tts.save(filename)
    return filename
