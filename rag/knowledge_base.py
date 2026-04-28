# ============================================================================
# KNOWLEDGE BASE LOADER — Loads and chunks the knowledge document
# ============================================================================

import os


def load_knowledge_base(file_path=None):
    """
    Load the Anuradhapura knowledge base text file.
    Returns the full text content as a string.
    """
    if file_path is None:
        # Default path relative to project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "anuradhapura_knowledge.txt")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Error: Knowledge base file not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return ""


def chunk_text(text, chunk_size=200, overlap=50):
    """
    Split text into overlapping chunks of approximately chunk_size words
    with overlap words of overlap between consecutive chunks.

    Args:
        text: The full text to chunk
        chunk_size: Target number of words per chunk (~200)
        overlap: Number of overlapping words between chunks (~50)

    Returns:
        List of text chunks
    """
    if not text:
        return []

    # Split into words
    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start += step

    return chunks


def get_chunks(file_path=None, chunk_size=200, overlap=50):
    """
    Load the knowledge base and return overlapping chunks.
    Convenience function combining loading and chunking.

    Args:
        file_path: Path to the knowledge base file (optional)
        chunk_size: Words per chunk
        overlap: Overlap words between chunks

    Returns:
        List of text chunk strings
    """
    text = load_knowledge_base(file_path)
    if not text:
        return []

    chunks = chunk_text(text, chunk_size, overlap)
    print(f"Knowledge base loaded: {len(chunks)} chunks created "
          f"(~{chunk_size} words each, {overlap} word overlap)")
    return chunks


# ============================================================================
# Module test
# ============================================================================
if __name__ == "__main__":
    chunks = get_chunks()
    print(f"\nTotal chunks: {len(chunks)}")
    if chunks:
        print(f"\nFirst chunk preview ({len(chunks[0].split())} words):")
        print(chunks[0][:300] + "...")
        print(f"\nLast chunk preview ({len(chunks[-1].split())} words):")
        print(chunks[-1][:300] + "...")
