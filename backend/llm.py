import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"

def ask_llm(context, question):
    """
    Sends the question + compressed context to the LLaMA model using Ollama.
    Ensures exam-style, descriptive answers in the tone/language of your notes.
    """

    # ---- Safety trims (Prevent slowdowns or freezing) ----
    if context is None:
        context = ""
    context = context.strip()[:4000]  # limit to avoid huge prompts

    # ---- System instruction for exam-style answers ----
    system_instruction = """
    You are an academic tutor specialized in writing exam-ready answers.

    IMPORTANT RULES:
    - ALWAYS answer in the same tone, style, and language as the provided notes.
    - Your answer must be descriptive, structured, and suitable for college exams.
    - Never add unnecessary humor, casual tone, or creative writing.
    - If the notes contain definitions, laws, or formulas, replicate them precisely.
    - If the user asks something outside the notes, answer normally but academically.
    """

    # ---- Construct final prompt ----
    final_prompt = f"""
    {system_instruction}

    CONTEXT FROM NOTES:
    {context}

    QUESTION FROM STUDENT:
    {question}

    PROVIDE THE FINAL ANSWER BELOW:
    """

    # ---- Payload for Ollama ----
    payload = {
        "model": MODEL_NAME,
        "prompt": final_prompt,
        "stream": False        # FIXED: ensures a single JSON output (required!)
    }

    # ---- Perform request ----
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        data = response.json()     # works now because stream=False
        return data.get("response", "").strip()

    except Exception as e:
        return f"❌ LLM Error: {str(e)}"
