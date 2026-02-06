import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import uuid
from .utils import extract_text

# ======================================================
# CONFIGURATION
# ======================================================
# Get API Key from Render Environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "study-assistant"

# Initialize Pinecone
if PINECONE_API_KEY:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Create index if it doesn't exist (Optional safety check)
    existing_indexes = [index.name for index in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        try:
            pc.create_index(
                name=INDEX_NAME,
                dimension=384, # Matches 'all-MiniLM-L6-v2'
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        except Exception as e:
            print(f"[WARN] Could not create index: {e}")
    
    index = pc.Index(INDEX_NAME)
else:
    print("[WARN] PINECONE_API_KEY not found. Database features will fail.")
    index = None

# Initialize Embedding Model (Small & Fast for Render Free Tier)
# This downloads a ~90MB model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# ======================================================
# HELPER FUNCTIONS
# ======================================================

def chunk_text(text, chunk_size=500):
    """Split text into manageable chunks with overlap"""
    chunks = []
    text = text.replace("\n", " ")
    words = text.split()
    
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        
        # When chunk is full, add to list and reset
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            # Keep last 50 words for overlap (better context)
            current_chunk = current_chunk[-50:] 
            current_length = len(" ".join(current_chunk))
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

# ======================================================
# CORE DATABASE FUNCTIONS
# ======================================================

def add_notes_to_db(path):
    """
    Extracts text from file -> Embeds it -> Uploads to Pinecone
    """
    if not index:
        print("[ERROR] Pinecone index not initialized.")
        return

    print(f"[INFO] Processing file: {path}")
    try:
        # 1. Extract Text using your existing utils.py
        full_text = extract_text(path)
        
        if not full_text or not full_text.strip():
            print("[WARN] File empty or unreadable.")
            return

        # 2. Chunk Text
        text_chunks = chunk_text(full_text)
        print(f"[INFO] Created {len(text_chunks)} chunks.")

        # 3. Embed & Prepare for Pinecone
        vectors = []
        embeddings = model.encode(text_chunks)
        
        filename = os.path.basename(path)

        for i, chunk in enumerate(text_chunks):
            vector_id = f"{filename}_{i}_{str(uuid.uuid4())[:8]}"
            
            vectors.append({
                "id": vector_id,
                "values": embeddings[i].tolist(),
                "metadata": {
                    "text": chunk,
                    "source": filename
                }
            })

        # 4. Upsert to Pinecone (Batching 100 at a time)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
            
        print(f"[SUCCESS] Uploaded {len(vectors)} chunks to Pinecone.")

    except Exception as e:
        print(f"[ERROR] Failed to add notes: {e}")

def search_notes(query):
    """
    Embeds query -> Searches Pinecone -> Returns top text matches
    """
    if not index:
        return "Database Error: Pinecone not connected."

    try:
        # 1. Embed Question
        query_embedding = model.encode(query).tolist()
        
        # 2. Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=5,  # Get top 5 matches for better context
            include_metadata=True
        )
        
        # 3. Extract Text
        contexts = []
        for match in results['matches']:
            # Confidence score check (optional)
            if match['score'] > 0.3: 
                contexts.append(match['metadata']['text'])
        
        if not contexts:
            return "No relevant notes found."

        return "\n\n".join(contexts)

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return ""