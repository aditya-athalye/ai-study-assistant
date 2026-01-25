import os

# Voice features disabled for deployment (too heavy for 512MB)
# These features require whisper and gTTS which exceed memory limits

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/uploads")

def speech_to_text(path):
    """Voice to text - disabled in deployment"""
    return "Voice-to-text is not available in the deployed version due to memory constraints. This feature works in the local version."

def text_to_speech(text):
    """Text to speech - disabled in deployment"""
    # Return a dummy path
    return "uploads/feature_disabled.mp3"