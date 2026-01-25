# 📘 AI Study Assistant — A Developer's Journey
### *From "It works on my machine" to "Live on the Cloud"*

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white)

This isn't just a chatbot; it is a documentation of my deep dive into the world of **LLMs, APIs, and Software Deployment**.

I started this project as a complete beginner with a simple goal: *"I want to build an AI that knows my notes."* What followed was a crash course in Python, memory management, and the painful reality of cloud hosting vs. local hardware.

---

## 📂 Repository Contents
This repository contains **two complete versions** of the application, representing the different stages of my engineering process:

### 1. ☁️ The Cloud Version (Main Branch)
* **Status:** **Live & Deployed**
* **Engine:** Groq API (Llama 3.3)
* **Storage:** Lightweight In-Memory Vector Search
* **Hosting:** Render (Optimized for 512MB RAM limit)
* **Why:** Re-engineered from scratch to solve the "it won't deploy" problem.

### 2. 💻 The Local Version (`/local_heavy_version`)
* **Status:** **Legacy / Experimental**
* **Engine:** **Ollama** (Running Llama 3 locally)
* **Voice:** **OpenAI Whisper** (Offline Speech-to-Text)
* **Embeddings:** **SentenceTransformers** (all-MiniLM-L6-v2) + NumPy
* **OCR/PDF:** **pdfplumber**
* **Why:** The original "powerhouse" version that runs 100% offline but requires heavy hardware (GPU + 8GB+ RAM).

---

## 🚀 The Story:

### Phase 1: "I want to run everything locally!" 💻
I started with a dream: a privacy-focused AI that runs 100% offline. I didn't want to use APIs; I wanted to own the stack.
* **The Stack:** I successfully built a backend using **FastAPI**, integrated **Ollama** for the LLM, and **Whisper** for voice.
* **The Struggle:**
    * *Dependency Hell:* I spent days just figuring out why `numpy` needed `gcc` or why `torch` versions were conflicting.
    * *The "Context" Problem:* I learned the hard way that you can't just "feed a PDF" to an AI. I had to learn about **Chunking** and **Vector Embeddings** to stop the AI from hallucinating.
    * *JSON Errors:* Ollama kept returning broken JSON, breaking my frontend. I had to write custom parsers to sanitize the output.

### Phase 2: The "It Won't Deploy" Reality Check 🛑
Once the app was perfect on my laptop, I tried to show it to the world. I thought deployment was just "uploading code." I was wrong.
* **Attempt 1 (Railway):** Free tier removed.
* **Attempt 2 (Oracle Cloud):** Couldn't bypass the sign-up restrictions.
* **Attempt 3 (Render):** My app crashed instantly.
* **The Realization:** My local app used 6GB+ of RAM. Render's free tier gives you **512MB**. My app was trying to fit an elephant into a matchbox.

### Phase 3: The Great Refactor (Optimization) 🛠️
I had to make a choice: give up, or re-engineer everything. I chose the latter. I tore down my heavy code and rebuilt it for efficiency.
* **Heavy LLM → Fast API:** I switched from local Ollama to **Groq API** (Llama 3.3). It’s faster and lightweight.
* **Heavy Vector DB → In-Memory Search:** I wrote a custom, simple keyword/cosine similarity search that runs in milliseconds without heavy libraries.
* **Frontend Serving:** I learned how to serve static HTML/JS files directly from FastAPI, solving the "404 Not Found" errors.

---

## 🧠 What I Learned (The "Newbie" List)
Beyond the code, I learned the invisible things that tutorials don't tell you:

1.  **Deployment is 50% of the work:** Writing code is easy; making it run on a Linux server 5,000 miles away is hard.
2.  **Environment Variables are life-savers:** I learned to stop hardcoding keys and use `.env` files properly.
3.  **Ports & Addresses:** I spent hours debugging why `localhost:8000` didn't work on the cloud (Hint: It needs to be `0.0.0.0` and the correct `PORT` env var).
4.  **Static Files & Paths:** Understanding relative vs. absolute paths was a nightmare until I fixed my folder structure.
5.  **Git Hygiene:** I learned (after many mistakes) how to structure a repo so it doesn't look like a mess of random files.

---

## 🛠️ How to Run This Project

### Option 1: Run the Cloud Version (Lightweight)
*This is the version currently deployed.*

1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/AI-STUDENT-ASSISTANT.git](https://github.com/YOUR_USERNAME/AI-STUDENT-ASSISTANT.git)
    cd AI-STUDENT-ASSISTANT
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up API Key:**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

4.  **Run the Server:**
    ```bash
    uvicorn backend.main:app --reload
    ```
    *Open `http://127.0.0.1:8000` in your browser.*

### Option 2: Run the Local Version (Heavy)
*Use this if you have a GPU and want to run Ollama locally.*

1.  **Navigate to the heavy folder:**
    ```bash
    cd local_heavy_version
    ```

2.  **Install Heavy Dependencies:**
    *(Note: You need `ollama` installed on your system first)*
    ```bash
    pip install -r requirements.txt
    ```
    *(Requirements include: `fastapi`, `uvicorn`, `gtts`, `sentence-transformers`, `pdfplumber`, `numpy`, `whisper-timestamped`)*

3.  **Run the Server:**
    ```bash
    uvicorn backend.main:app --reload
    ```

---

## 🔮 Possible Future Improvements 
* [ ] Improve the search algorithm using lightweight embeddings (TF-IDF).
* [ ] Add a user login system.

---

