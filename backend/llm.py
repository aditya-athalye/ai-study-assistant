import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================
# GROQ API CONFIGURATION (Fast & Free)
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_llm(context, question):
    """
    Using Groq API for fast LLM inference
    Model: Llama 3.3 70B (via Groq's LPU)
    """
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construct messages in chat format
    messages = [
        {
            "role": "system",
            "content": "You are a knowledgeable study assistant. Answer clearly and in exam-friendly descriptive style. Use the context provided to answer questions accurately."
        },
        {
            "role": "user",
            "content": f"""Context from notes:
{context}

Question: {question}

Provide a clear, descriptive answer based on the context above."""
        }
    ]
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 500,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        
        return answer
    
    except requests.exceptions.HTTPError as e:
        # SPECIFIC FIX: Handle Rate Limits (429) gently
        if response.status_code == 429:
            return "Server busy, please wait 10 seconds and try again."
        elif response.status_code == 401:
            return "Error: Invalid API key. Please check your GROQ_API_KEY in .env file."
        else:
            return f"API Error: {str(e)}"
    
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The server is taking too long."
    
    except Exception as e:
        return f"Error: {str(e)}"