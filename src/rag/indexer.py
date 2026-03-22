import json
import pickle
import numpy as np
import faiss
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DOCUMENTS_PATH = BASE_DIR / "data" / "processed" / "rag_documents.json"
INDEX_DIR = BASE_DIR / "data" / "processed" / "faiss_index"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
BATCH_SIZE = 50 


def load_documents(path: Path = DOCUMENTS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def embed_texts(texts: list[str], client: OpenAI) -> np.ndarray:
    """
    Embeds a list of texts in batches.
    Returns a NumPy array with shape (N, EMBEDDING_DIM).
    """
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"  Embeddings for {min(i + BATCH_SIZE, len(texts))}/{len(texts)} documents")

    return np.array(all_embeddings, dtype=np.float32)


def build_index(documents: list[dict], client: OpenAI) -> tuple[faiss.Index, list[dict]]:
    """
    Create a FAISS IndexFlatIP (inner product = cosine similarity with normalized vectors).
    Returns (index, metadata_list).
    """
    texts = [doc["text"] for doc in documents]
    metadata = [{"id": doc["id"], **doc["metadata"]} for doc in documents]

    print(f"Embedding {len(texts)} documents with {EMBEDDING_MODEL}...")
    embeddings = embed_texts(texts, client)

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings)

    print(f"FAISS index built: {index.ntotal} vectors, {EMBEDDING_DIM}D")
    return index, metadata


def save_index(index: faiss.Index, metadata: list[dict], output_dir: Path = INDEX_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(output_dir / "index.faiss"))

    with open(output_dir / "metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

    print(f"Index saved to: {output_dir}")


def load_index(index_dir: Path = INDEX_DIR) -> tuple[faiss.Index, list[dict]]:
    index = faiss.read_index(str(index_dir / "index.faiss"))

    with open(index_dir / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)

    return index, metadata


def build_and_save(documents_path: Path = DOCUMENTS_PATH, index_dir: Path = INDEX_DIR):
    """Entry point — loads documents, builds and saves the index."""
    client = OpenAI()
    documents = load_documents(documents_path)

    print(f"Loaded {len(documents)} documents")
    index, metadata = build_index(documents, client)
    save_index(index, metadata, index_dir)

    return index, metadata


if __name__ == "__main__":
    build_and_save()
