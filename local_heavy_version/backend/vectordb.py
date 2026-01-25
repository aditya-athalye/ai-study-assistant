import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from .utils import extract_text

DB_PATH = "notes_db.json"
EMB_PATH = "embeddings.npy"

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load database if exists
notes_db = []
embeddings = []

if os.path.exists(DB_PATH):
    notes_db = json.load(open(DB_PATH, "r"))

if os.path.exists(EMB_PATH):
    embeddings = np.load(EMB_PATH)


def add_notes_to_db(filepath):
    text = extract_text(filepath)
    chunks = text.split("\n\n")

    global notes_db, embeddings

    for chunk in chunks:
        if len(chunk.strip()) < 10:
            continue
        notes_db.append(chunk)

    np_embeds = model.encode(notes_db)
    embeddings = np_embeds

    json.dump(notes_db, open(DB_PATH, "w"))
    np.save(EMB_PATH, embeddings)


def search_notes(query):
    if len(notes_db) == 0:
        return ""

    q_emb = model.encode([query])[0]
    scores = np.dot(embeddings, q_emb)

    best_idx = np.argmax(scores)
    return notes_db[best_idx]
