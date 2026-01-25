import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"

def ask_llm(context, question):
    prompt = f"""
You are an exam-answering assistant.
Write answers **exactly** in the style of the notes.
Do NOT change tone or language.
Be descriptive, structured, and exam-oriented.

Context:
{context}

Question:
{question}

Answer:
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload)

    try:
        return r.json()["response"]
    except:
        print("LLM Error:", r.text)
        return "Error: Could not generate answer."
