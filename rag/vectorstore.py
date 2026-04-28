# ============================================================================
# VECTOR STORE — FAISS-based vector storage for RAG retrieval
# Uses sentence-transformers with multilingual model (Sinhala + English)
# ============================================================================

import os
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.bin")
CHUNKS_PATH = os.path.join(BASE_DIR, "chunks_store.npy")
MODEL_CACHE_DIR = os.path.join(BASE_DIR, "model_cache")

# Model name — multilingual, supports Sinhala + English, CPU friendly
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_embedding_model():
    """
    Load the sentence-transformers model.
    Uses local cache after first download.
    """
    try:
        from sentence_transformers import SentenceTransformer
        print(f"Loading embedding model: {MODEL_NAME}")
        print(f"Model cache directory: {MODEL_CACHE_DIR}")
        model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_CACHE_DIR)
        print("Embedding model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading embedding model: {e}")
        return None


def build_faiss_index(chunks, model):
    """
    Build a FAISS index from text chunks and save to disk.

    Args:
        chunks: List of text chunks
        model: SentenceTransformer model

    Returns:
        FAISS index, or None on error
    """
    try:
        import faiss

        if not chunks:
            print("Error: No chunks provided for indexing.")
            return None

        print(f"Encoding {len(chunks)} chunks... (this may take a moment on CPU)")
        embeddings = model.encode(chunks, show_progress_bar=True, batch_size=16)
        embeddings = np.array(embeddings, dtype="float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        # Build index (Inner Product after normalization = cosine similarity)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        # Save index to disk
        faiss.write_index(index, FAISS_INDEX_PATH)
        print(f"FAISS index saved to {FAISS_INDEX_PATH}")

        # Save chunks mapping
        np.save(CHUNKS_PATH, np.array(chunks, dtype=object))
        print(f"Chunks mapping saved to {CHUNKS_PATH}")

        return index

    except Exception as e:
        print(f"Error building FAISS index: {e}")
        return None


def load_faiss_index():
    """
    Load an existing FAISS index from disk.

    Returns:
        Tuple of (FAISS index, chunks list), or (None, None) on error
    """
    try:
        import faiss

        if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
            print("No existing FAISS index found on disk.")
            return None, None

        print(f"Loading FAISS index from {FAISS_INDEX_PATH}")
        index = faiss.read_index(FAISS_INDEX_PATH)

        chunks = np.load(CHUNKS_PATH, allow_pickle=True).tolist()
        print(f"FAISS index loaded: {index.ntotal} vectors, {len(chunks)} chunks")

        return index, chunks

    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None, None


def get_or_build_index(chunks=None):
    """
    Load existing FAISS index from disk, or build a new one if not found.

    Args:
        chunks: List of text chunks (required only for building new index)

    Returns:
        Tuple of (index, chunks, model)
    """
    model = load_embedding_model()
    if model is None:
        return None, None, None

    # Try loading existing index
    index, stored_chunks = load_faiss_index()
    if index is not None and stored_chunks is not None:
        return index, stored_chunks, model

    # Build new index
    if chunks is None or len(chunks) == 0:
        print("No chunks provided and no existing index. Cannot proceed.")
        return None, None, model

    print("Building new FAISS index...")
    index = build_faiss_index(chunks, model)
    if index is not None:
        return index, chunks, model

    return None, None, model


def retrieve(query, index, chunks, model, top_k=3):
    """
    Retrieve the top-k most relevant chunks for a query.

    Args:
        query: Query string (can be in Sinhala or English)
        index: FAISS index
        chunks: List of text chunks
        model: SentenceTransformer model
        top_k: Number of results to return

    Returns:
        List of dicts with 'chunk' and 'score' keys
    """
    try:
        if index is None or model is None or not chunks:
            return []

        # Encode query
        query_embedding = model.encode([query])
        query_embedding = np.array(query_embedding, dtype="float32")

        import faiss
        faiss.normalize_L2(query_embedding)

        # Search
        k = min(top_k, len(chunks))
        scores, indices = index.search(query_embedding, k)

        results = []
        for i in range(k):
            idx = indices[0][i]
            if 0 <= idx < len(chunks):
                results.append({
                    "chunk": chunks[idx],
                    "score": float(scores[0][i])
                })

        return results

    except Exception as e:
        print(f"Error during retrieval: {e}")
        return []


# ============================================================================
# Module test
# ============================================================================
if __name__ == "__main__":
    from knowledge_base import get_chunks

    chunks = get_chunks()
    index, stored_chunks, model = get_or_build_index(chunks)

    if index and model:
        # Test English query
        print("\n=== English Query: 'irrigation tanks' ===")
        results = retrieve("irrigation tanks and reservoirs", index, stored_chunks, model)
        for i, r in enumerate(results):
            print(f"\n--- Result {i+1} (Score: {r['score']:.4f}) ---")
            print(r["chunk"][:200] + "...")

        # Test Sinhala query
        print("\n=== Sinhala Query: 'බුද්ධාගමය' (Buddhism) ===")
        results = retrieve("බුද්ධාගමය හඳුන්වා දීම", index, stored_chunks, model)
        for i, r in enumerate(results):
            print(f"\n--- Result {i+1} (Score: {r['score']:.4f}) ---")
            print(r["chunk"][:200] + "...")
