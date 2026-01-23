import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

# Choose your cloud LLM model (free options available)
HF_MODEL = "mistralai/Mistral-7B-Instruct"  
# You may also use: "meta-llama/Llama-3.1-8B-Instruct"

API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def ask_llm(context, question):
    prompt = f"""
You are a knowledgeable study assistant. Answer clearly and in exam-friendly descriptive style.
Do NOT change the tone or language style from the student's notes.

Context:
{context}

Question:
{question}

Answer:
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 350,
            "temperature": 0.4,
            "top_p": 0.9
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    try:
        output = response.json()

        # HF returns a list of dicts
        if isinstance(output, list):
            return output[0]["generated_text"]
        if "generated_text" in output:
            return output["generated_text"]

        return "Error: Unexpected API format"

    except Exception as e:
        return f"LLM Error: {str(e)}"
