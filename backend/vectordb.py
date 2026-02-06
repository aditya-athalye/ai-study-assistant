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
if PINECONE_API_KEY:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing_indexes = [index.name for index in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=768, # <--- Gemini Embeddings are 768 dimensions
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    index = pc.Index(INDEX_NAME)
else:
    index = None

# Configure Google Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ======================================================
# HELPER FUNCTIONS
# ======================================================
def get_embedding(text):
    """Generates embedding using Google Gemini (0 RAM Usage)"""
    try:
        # 'embedding-001' is Google's optimized embedding model
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document",
            title="Study Notes"
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
    if not index: return

    print(f"[INFO] Processing file: {path}")
    full_text = extract_text(path) # <--- Uses Vision for Images now!
    
    if not full_text: return

    text_chunks = chunk_text(full_text)
    vectors = []
    filename = os.path.basename(path)
    category = "global" if is_admin else session_id

    for i, chunk in enumerate(text_chunks):
        emb = get_embedding(chunk)
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
        index.upsert(vectors=vectors)
        print(f"[SUCCESS] Uploaded {len(vectors)} chunks.")

def search_notes(query, session_id):
    if not index: return "Database Error."

    try:
        # Get query embedding from Gemini
        query_emb = genai.embed_content(
            model="models/embedding-001",
            content=query,
            task_type="retrieval_query"
        )['embedding']
        
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