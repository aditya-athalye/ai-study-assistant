import os

# Simple in-memory storage (no vector embeddings)
# For deployment without heavy ML libraries

all_chunks = []

def chunk_text(text, chunk_size=500):
    """Split text into chunks"""
    chunks = []
    text = text.replace("\n", " ")

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if len(chunk) > 20:
            chunks.append(chunk)
    return chunks


def add_notes_to_db(path):
    """Add notes without vector embeddings (simple text storage)"""
    global all_chunks
    
    from .utils import extract_text
    
    print(f"[INFO] Extracting text from: {path}")
    full_text = extract_text(path)

    if not full_text.strip():
        print("[WARN] Empty text, skipping.")
        return

    chunks = chunk_text(full_text)
    print(f"[INFO] → Created {len(chunks)} chunks")

    all_chunks.extend(chunks)
    print(f"[INFO] Total chunks in memory: {len(all_chunks)}")


def search_notes(query):
    """Simple keyword search (no semantic search)"""
    global all_chunks
    
    if len(all_chunks) == 0:
        return "No notes uploaded yet. Please upload your study materials first."
    
    # Simple keyword matching
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Score chunks by keyword overlap
    scored_chunks = []
    for chunk in all_chunks:
        chunk_lower = chunk.lower()
        chunk_words = set(chunk_lower.split())
        
        # Count matching words
        matches = len(query_words & chunk_words)
        if matches > 0:
            scored_chunks.append((matches, chunk))
    
    # Sort by score and take top 3
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    top_chunks = [chunk for score, chunk in scored_chunks[:3]]
    
    if not top_chunks:
        # If no keyword matches, return first few chunks as context
        return "\n".join(all_chunks[:3])
    
    return "\n".join(top_chunks)


def load_preexisting_notes():
    """Load notes from notes folder on startup"""
    global all_chunks
    
    notes_dir = "backend/notes"
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
        print("[INFO] Created notes directory")

    for filename in os.listdir(notes_dir):
        path = os.path.join(notes_dir, filename)
        if os.path.isfile(path):
            print(f"[AUTO] Adding preexisting note: {filename}")
            add_notes_to_db(path)

    print(f"[INFO] Startup complete. {len(all_chunks)} chunks loaded.")


# Run at import
load_preexisting_notes()