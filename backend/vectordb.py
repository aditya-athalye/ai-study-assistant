import os
from .utils import extract_text

# Simple in-memory storage (no heavy vector database)
all_chunks = []

def chunk_text(text, chunk_size=500):
    """Split text into manageable chunks"""
    chunks = []
    text = text.replace("\n", " ")
    
    # improved chunking to avoid cutting words in half (simple approach)
    words = text.split()
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def add_notes_to_db(path):
    """Read a file and add its content to memory"""
    global all_chunks
    
    print(f"[INFO] Processing: {path}")
    try:
        full_text = extract_text(path)
        
        if not full_text or not full_text.strip():
            print("[WARN] File was empty or unreadable.")
            return

        new_chunks = chunk_text(full_text)
        all_chunks.extend(new_chunks)
        print(f"[SUCCESS] Added {len(new_chunks)} chunks. Total DB size: {len(all_chunks)}")
        
    except Exception as e:
        print(f"[ERROR] Failed to process {path}: {e}")

def search_notes(query):
    """Find relevant chunks based on keyword overlap"""
    global all_chunks
    
    if not all_chunks:
        return ""
    
    query_words = set(query.lower().split())
    
    scored_chunks = []
    for chunk in all_chunks:
        chunk_words = set(chunk.lower().split())
        # Count how many query words appear in this chunk
        score = len(query_words.intersection(chunk_words))
        if score > 0:
            scored_chunks.append((score, chunk))
    
    # Sort by highest score first
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 3 matches
    top_matches = [chunk for score, chunk in scored_chunks[:3]]
    
    return "\n\n".join(top_matches)

def load_preexisting_notes():
    """Scan the 'notes' folder and load everything on startup"""
    # Robust path finding: looks for 'notes' folder in the same directory as this script
    current_dir = os.path.dirname(__file__)
    notes_dir = os.path.join(current_dir, "notes")
    
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
        print(f"[INIT] Created notes folder at {notes_dir}")
        return

    print(f"[INIT] Scanning for notes in: {notes_dir}")
    files = os.listdir(notes_dir)
    
    if not files:
        print("[INIT] No notes found to load.")
        return

    for filename in files:
        file_path = os.path.join(notes_dir, filename)
        if os.path.isfile(file_path):
            add_notes_to_db(file_path)

# Load notes immediately when this file is imported
load_preexisting_notes()