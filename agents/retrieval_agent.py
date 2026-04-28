# ============================================================================
# RETRIEVAL AGENT — Retrieves relevant knowledge base chunks
# Uses RAG pipeline (FAISS + sentence-transformers)
# ============================================================================

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RetrievalAgent:
    """
    Agent responsible for retrieving relevant knowledge base chunks
    for a given student answer and question combination.
    """

    def __init__(self, index, chunks, model):
        """
        Initialize the RetrievalAgent.

        Args:
            index: FAISS index
            chunks: List of text chunks from knowledge base
            model: SentenceTransformer model for encoding queries
        """
        self.index = index
        self.chunks = chunks
        self.model = model

    def retrieve(self, student_answer, question, top_k=3):
        """
        Retrieve the most relevant knowledge base chunks for the
        student answer and question combination.

        Combines the student answer with the question text for
        better retrieval accuracy.

        Args:
            student_answer: The student's answer text (may be in Sinhala)
            question: The question text
            top_k: Number of chunks to retrieve

        Returns:
            List of dicts: [{"chunk": str, "score": float}, ...]
        """
        try:
            if self.index is None or self.model is None or not self.chunks:
                print("RetrievalAgent: Index, model, or chunks not available.")
                return []

            # Combine question + answer for better retrieval
            combined_query = f"{question} {student_answer}"

            from rag.vectorstore import retrieve as vs_retrieve
            results = vs_retrieve(
                query=combined_query,
                index=self.index,
                chunks=self.chunks,
                model=self.model,
                top_k=top_k
            )

            if results:
                print(f"RetrievalAgent: Retrieved {len(results)} chunks.")
                for i, r in enumerate(results):
                    print(f"  Chunk {i+1}: score={r['score']:.4f}, "
                          f"length={len(r['chunk'].split())} words")
            else:
                print("RetrievalAgent: No chunks retrieved.")

            return results

        except Exception as e:
            print(f"RetrievalAgent error: {e}")
            return []
