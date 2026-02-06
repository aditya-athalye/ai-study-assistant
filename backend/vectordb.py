import os
import uuid
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from .utils import extract_text

# ======================================================
# CONFIGURATION
# ======================================================
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
INDEX_NAME = "study-assistant"

# Initialize Pinecone
index = None
if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        existing_indexes = [i.name for i in pc.list_indexes()]
        
        # Create index if it doesn't exist (768 Dimensions for Gemini)
        if INDEX_NAME not in existing_indexes:
            pc.create_index(
                name=INDEX_NAME,
                dimension=768, 
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        index = pc.Index(INDEX_NAME)
    except Exception as e:
        print(f"[ERROR] Pinecone Init Failed: {e}")

# Configure Google Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ======================================================
# HELPER FUNCTIONS
# ======================================================
def get_embedding(text, task_type="retrieval_document"):
    """Generates embedding using the NEW Gemini model (768 dims)"""
    try:
        # Use the correct new model name
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type=task_type,
            title="Study Notes" if task_type == "retrieval_document" else None,
            output_dimensionality=768
        )
        return result['embedding']
    except Exception as e:
        print(f"[ERROR] Gemini Embedding Failed: {e}")
        return None

def chunk_text(text, chunk_size=1000):
    """Splits text into larger chunks for Gemini"""
    chunks = []
    text = text.replace("\n", " ")
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

# ======================================================
# CORE DATABASE FUNCTIONS
# ======================================================
def add_notes_to_db(path, session_id, is_admin=False):
    if not index: 
        print("[ERROR] Database not connected.")
        return

    print(f"[INFO] Processing file: {path}")
    full_text = extract_text(path)
    
    if not full_text: 
        print("[WARN] No text extracted.")
        return

    text_chunks = chunk_text(full_text)
    vectors = []
    filename = os.path.basename(path)
    category = "global" if is_admin else session_id

    print(f"[INFO] Generating embeddings for {len(text_chunks)} chunks...")

    for i, chunk in enumerate(text_chunks):
        # Generate embedding for storage
        emb = get_embedding(chunk, task_type="retrieval_document")
        if emb:
            vector_id = f"{category}_{i}_{str(uuid.uuid4())[:8]}"
            vectors.append({
                "id": vector_id,
                "values": emb,
                "metadata": {
                    "text": chunk,
                    "source": filename,
                    "category": category
                }
            })

    # Upsert to Pinecone
    if vectors:
        batch_size = 50
        for i in range(0, len(vectors), batch_size):
            index.upsert(vectors=vectors[i:i + batch_size])
        print(f"[SUCCESS] Uploaded {len(vectors)} chunks.")

def search_notes(query, session_id):
    if not index: return "Database Error."

    try:
        # Generate embedding for query
        query_emb = get_embedding(query, task_type="retrieval_query")
        
        if not query_emb:
            return "Error generating query embedding."

        # Search Global + Session
        results = index.query(
            vector=query_emb,
            top_k=5,
            include_metadata=True,
            filter={"category": {"$in": ["global", session_id]}} 
        )
        
        contexts = [m['metadata']['text'] for m in results['matches']]
        return "\n\n".join(contexts) if contexts else "No notes found."

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return ""