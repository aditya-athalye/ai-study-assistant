import os
import uuid
from pinecone import Pinecone, ServerlessSpec
from fastembed import TextEmbedding # <--- NEW LIGHTWEIGHT IMPORT
from .utils import extract_text

# ======================================================
# CONFIGURATION
# ======================================================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "study-assistant"

# Initialize Pinecone
if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        # Create index if it doesn't exist
        existing_indexes = [index.name for index in pc.list_indexes()]
        if INDEX_NAME not in existing_indexes:
            pc.create_index(
                name=INDEX_NAME,
                dimension=384, 
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        index = pc.Index(INDEX_NAME)
    except Exception as e:
        print(f"[ERROR] Pinecone Init Failed: {e}")
        index = None
else:
    print("[WARN] PINECONE_API_KEY not found. Database features will fail.")
    index = None

# Initialize Embedding Model (Lightweight ONNX version)
# This uses ~200MB RAM instead of 500MB+
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# ======================================================
# HELPER FUNCTIONS
# ======================================================
def chunk_text(text, chunk_size=500):
    chunks = []
    text = text.replace("\n", " ")
    words = text.split()
    
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-50:] 
            current_length = len(" ".join(current_chunk))
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

# ======================================================
# CORE DATABASE FUNCTIONS
# ======================================================
def add_notes_to_db(path, session_id, is_admin=False):
    if not index:
        print("[ERROR] Pinecone index not ready.")
        return

    print(f"[INFO] Processing file: {path}")
    try:
        full_text = extract_text(path)
        if not full_text or not full_text.strip():
            print("[WARN] File empty or unreadable.")
            return

        text_chunks = chunk_text(full_text)
        vectors = []
        
        # FastEmbed handles lists of strings directly
        # It returns a generator, so we convert to list
        embeddings = list(model.embed(text_chunks))
        
        filename = os.path.basename(path)
        category = "global" if is_admin else session_id

        for i, chunk in enumerate(text_chunks):
            vector_id = f"{category}_{i}_{str(uuid.uuid4())[:8]}"
            vectors.append({
                "id": vector_id,
                "values": embeddings[i].tolist(), # Convert numpy to list for Pinecone
                "metadata": {
                    "text": chunk,
                    "source": filename,
                    "category": category
                }
            })

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            index.upsert(vectors=vectors[i:i + batch_size])
            
        print(f"[SUCCESS] Uploaded {len(vectors)} chunks to category: {category}")

    except Exception as e:
        print(f"[ERROR] Failed to add notes: {e}")

def search_notes(query, session_id):
    if not index: return "Database Error: Pinecone not connected."

    try:
        # FastEmbed expects a list, even for a single query
        query_embedding = list(model.embed([query]))[0].tolist()
        
        # 1. Search Global
        global_results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
            filter={"category": "global"}
        )
        
        # 2. Search Session
        session_results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
            filter={"category": session_id}
        )
        
        # 3. Combine
        all_matches = global_results['matches'] + session_results['matches']
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        contexts = []
        seen = set()
        
        for match in all_matches[:5]:
            text = match['metadata']['text']
            if text not in seen:
                contexts.append(text)
                seen.add(text)
        
        if not contexts:
            return "No relevant notes found."
            
        return "\n\n".join(contexts)

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return ""