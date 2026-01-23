# 📘 AI Study Assistant — Context-Aware Notes + Voice + OCR + LLM

A lightweight, fully local, context-aware study assistant that lets you:

- Upload typed or handwritten notes  
- Ask questions and get structured, exam-style answers  
- Speak to the AI and receive voice replies  
- Get text responses like ChatGPT  
- Use OCR for handwritten images  
- Run everything **free**, **locally**, and deploy using Railway

This project was built to understand how to integrate **LLMs**, **Vector Databases**, **OCR**, **Whisper**, and **Text-to-Speech** into one unified system.

---

# 🚀 Features

### ✔ LLM Integration  
- Uses **LLaMA models via Ollama**  
- Answers grounded in your uploaded notes  
- Generates **exam-ready descriptive answers**  
- Matches the tone and language of the notes  

### ✔ Vector Database  
- Embeds notes using **SentenceTransformers**  
- Local vector store with cosine similarity  
- Chunking support for long PDFs  

### ✔ Notes Upload  
- Accepts PDFs, typed notes, scanned images, handwritten pages  
- Uses **EasyOCR** for handwriting recognition  
- Extracts text + stores embeddings automatically  

### ✔ Voice Input (Speech-to-Text)  
- Whisper-timestamped  
- Offline  
- Accurate for noisy environments  

### ✔ Voice Output (Text-to-Speech)  
- Converts responses into MP3 files  
- Uses gTTS  
- Railway-safe storage path  

### ✔ Modern Frontend  
- ChatGPT-like UI  
- Smooth message bubbles  
- Dark theme  
- Enter-to-send  
- Fully responsive  

### ✔ Railway Deployment Ready  
- **Procfile** included  
- **railway.toml** included  
- `/mnt/data/uploads` support  
- CPU-only compatible  
- No broken paths  

---

# 🧪 Tech Stack

### **Backend**
- FastAPI  
- Uvicorn  
- Whisper Timestamped  
- gTTS  
- SentenceTransformers  
- EasyOCR  
- scikit-learn  
- PyPDF2  
- Requests  

### **Frontend**
- HTML  
- CSS  
- JavaScript  

### **Deployment**
- Railway  
- GitHub Pages (for frontend)  

---

# 📁 Project Structure

```css
ai-student-assistant/

├── backend/
│   ├── main.py
│   ├── llm.py
│   ├── vectordb.py
│   ├── voice.py
│   ├── utils.py
│   ├── notes/
│   └── notes_db/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── requirements.txt
├── Procfile
└── railway.toml

---

🛠 Installation (Local)
1. Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd ai-student-assistant

2. Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows

3. Install backend dependencies
pip install -r requirements.txt

4. Start backend server
uvicorn backend.main:app --reload

5. Open frontend
Just open:
frontend/index.html

---

📄 API Routes

| Method | Route            | Description    |
| ------ | ---------------- | -------------- |
| POST   | `/ask`           | Ask a question |
| POST   | `/upload-notes`  | Upload notes   |
| POST   | `/voice-to-text` | Speech → Text  |
| POST   | `/text-to-voice` | Text → Audio   |

---
🎯 My Journey Building This Project

I created this project because I wanted to understand how real applications integrate modern AI. Not just generating text, but handling:

-OCR

-vector embeddings

-LLM context retrieval

-voice input

-voice output

-chunking logic

-clean UI

-deployment on Railway

It started as a simple idea:
“Make an AI that learns from my notes and explains concepts like an exam tutor.”

And evolved into a complete multi-modal AI assistant that can learn from handwritten or typed notes, speak back responses, retrieve contextual info, and run entirely locally without APIs.

Each iteration fixed something:

-proper OCR

-PDF text extraction

-Whisper improvements

-vector DB organization

-UI redesign

-deployment fixes

-handling /mnt/data

-making it CPU-only

-refining the overall structure

It became more than a project — it became a way to deeply understand the entire pipeline of LLM apps.