import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import extract_text

# -----------------------------
# Load Embedding Model
# -----------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Vector Store Location
# -----------------------------
DB_FOLDER = "backend/notes_db"

if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

EMBED_FILE = os.path.join(DB_FOLDER, "embeddings.npy")
TEXT_FILE = os.path.join(DB_FOLDER, "chunks.txt")

# Initialize memory-based store
all_chunks = []
all_vectors = []


# -----------------------------
# Chunk Text Function
# -----------------------------
def chunk_text(text, chunk_size=500):
    chunks = []
    text = text.replace("\n", " ")

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if len(chunk) > 20:     # ignore tiny garbage chunks
            chunks.append(chunk)
    return chunks


# -----------------------------
# Add Notes To Vector DB
# -----------------------------
def add_notes_to_db(path):
    global all_chunks, all_vectors

    print(f"[INFO] Extracting text from: {path}")
    full_text = extract_text(path)

    if not full_text.strip():
        print("[WARN] Empty text, skipping.")
        return

    chunks = chunk_text(full_text)
    print(f"[INFO] → Created {len(chunks)} chunks")

    embeddings = embedder.encode(chunks)

    all_chunks.extend(chunks)
    all_vectors.extend(embeddings)

    # Save to disk
    np.save(EMBED_FILE, np.array(all_vectors))

    with open(TEXT_FILE, "a", encoding="utf-8") as f:
        for c in chunks:
            f.write(c + "\n")

    print(f"[INFO] Successfully embedded {len(chunks)} chunks from file.")


# -----------------------------
# Search Notes (Semantic Search)
# -----------------------------
def search_notes(query):
    global all_chunks, all_vectors

    if len(all_chunks) == 0:
        return ""

    q_vec = embedder.encode([query])

    sims = cosine_similarity(q_vec, np.array(all_vectors))[0]

    top_idx = sims.argsort()[-3:][::-1]   # top 3 chunks
    top_chunks = [all_chunks[i] for i in top_idx]

    return "\n".join(top_chunks)


# -----------------------------
# Load Preexisting Notes
# -----------------------------
def load_preexisting_notes():
    global all_chunks, all_vectors

    # Load previous DB
    if os.path.exists(EMBED_FILE) and os.path.exists(TEXT_FILE):
        print("[INFO] Loading existing vector DB...")
        all_vectors = np.load(EMBED_FILE).tolist()

        with open(TEXT_FILE, "r", encoding="utf-8") as f:
            all_chunks = [line.strip() for line in f.readlines()]

        print(f"[INFO] Loaded {len(all_chunks)} chunks from disk.")
    else:
        print("[INFO] No prebuilt DB found. Building fresh.")

    # Auto-load notes folder
    notes_dir = "backend/notes"
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)

    for filename in os.listdir(notes_dir):
        path = os.path.join(notes_dir, filename)

        if os.path.isfile(path):
            print(f"[AUTO] Adding preexisting note: {filename}")
            add_notes_to_db(path)

    print("[INFO] Startup note load complete.")


# Run at import
load_preexisting_notes()
