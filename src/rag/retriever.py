import numpy as np
import faiss
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

from .indexer import load_index, EMBEDDING_MODEL, INDEX_DIR

load_dotenv()


class MedicalRetriever:
    """
    Retrieves relevant documents based on a given query.
    Supports filtering by document type and specialty.
    """

    def __init__(self, index_dir: Path = INDEX_DIR):
        self.client           = OpenAI()
        self.index, self.metadata = load_index(index_dir)
        print(f"Retriever loaded: {self.index.ntotal} documents in the index")

    def _embed_query(self, query: str) -> np.ndarray:
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[query],
        )
        vector = np.array([response.data[0].embedding], dtype=np.float32)
        faiss.normalize_L2(vector)
        return vector

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_type: str | None = None,
        specialty_id: str | None = None,
    ) -> list[dict]:
        """
        Searches for the top_k most relevant documents.

        Parameters:
            query — the question of the patient
            top_k — number of results
            doc_type — "doctor" | "specialty" | "knowledge_base" | None
            specialty_id — filters by a specific specialty

        Returns a list of dicts with keys: score, id, type, text (from metadata).
        """
        query_vector = self._embed_query(query)

        fetch_k = top_k * 6 if (doc_type or specialty_id) else top_k
        fetch_k = min(fetch_k, self.index.ntotal)

        scores, indices = self.index.search(query_vector, fetch_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            meta = self.metadata[idx]

            if doc_type and meta.get("type") != doc_type:
                continue

            if specialty_id and meta.get("specialty_id") != specialty_id:
                continue

            results.append({
                "score": float(score),
                "id": meta["id"],
                "type": meta.get("type"),
                "specialty": meta.get("specialty"),
                "specialty_id": meta.get("specialty_id"),
                "doctor_id": meta.get("doctor_id"),
                "accepts_nhif": meta.get("accepts_nhif"),
                "price": meta.get("price"),
                "rating": meta.get("rating"),
            })

            if len(results) >= top_k:
                break

        return results

    def search_doctors(
        self,
        query: str,
        top_k: int = 3,
        specialty_id: str | None = None,
        nhif_only: bool = False,
    ) -> list[dict]:
        """Searches for doctors. Optional filter by specialty and NHIF."""
        results = self.search(query, top_k=top_k * 4, doc_type="doctor", specialty_id=specialty_id)

        if nhif_only:
            results = [r for r in results if r.get("accepts_nhif")]

        return results[:top_k]

    def search_specialties(self, query: str, top_k: int = 3) -> list[dict]:
        """Searches for suitable specialties by symptoms."""
        return self.search(query, top_k=top_k, doc_type="specialty")

    def search_knowledge_base(self, query: str, top_k: int = 3) -> list[dict]:
        """Searches in the knowledge base — prices, working hours, FAQ."""
        return self.search(query, top_k=top_k, doc_type="knowledge_base")

    def build_context(self, query: str, top_k: int = 5) -> str:
        """
        Builds a context for the RAG prompt from a mixed search.
        Returns a formatted text, ready to be submitted to the LLM.
        """
        results = self.search(query, top_k=top_k)

        if not results:
            return "No relevant information found."

        context_parts = []
        for r in results:
            context_parts.append(f"[{r['type'].upper()} | score: {r['score']:.3f}]\n{r['id']}")

        return "\n\n---\n\n".join(context_parts)
