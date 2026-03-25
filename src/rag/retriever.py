import numpy as np
import faiss
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

from .indexer import load_index, EMBEDDING_MODEL, INDEX_DIR

load_dotenv()

REWRITE_SYSTEM_PROMPT = """Ти си медицински асистент за български пациенти.
Получаваш въпрос от пациент и трябва да го пренапишеш така, че да е
по-подходящ за търсене в база данни с лекари и медицински специалности.
 
Правила:
- Запази оригиналния смисъл и симптоми.
- Добави подходящи медицински термини на български (напр. "болка в гърдите" → добави "кардиология, сърдечни заболявания").
- Ако въпросът е за запис, цена, НЗОК, работно време — НЕ добавяй специалности, само уточни административния въпрос.
- Върни само пренаписания текст — без обяснения, без кавички."""

RERANK_SYSTEM_PROMPT = """Ти си медицински асистент. Оценяваш релевантността на документи спрямо въпрос на пациент.
 
За всеки документ върни JSON обект с едно поле "score" — число от 0.0 до 1.0.
0.0 = напълно нерелевантен, 1.0 = перфектно съвпадение.
 
Отговори САМО с валиден JSON масив, без никакъв друг текст.
Пример за 3 документа: [{"score": 0.9}, {"score": 0.3}, {"score": 0.7}]"""

class MedicalRetriever:
    """
    Retrieves relevant documents based on a given query.
    Supports filtering by document type and specialty.
    """

    def __init__(self, index_dir: Path = INDEX_DIR):
        self.client = OpenAI()
        self.index, self.metadata = load_index(index_dir)
        print(f"Retriever loaded: {self.index.ntotal} documents in the index")

    def rewrite_query(self, query: str) -> str:
        """
        Rewrites the patient query to improve embedding recall.
        Adds relevant medical terminology while preserving original intent.
        Falls back to the original query on any error.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=200,
                messages=[
                    {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
            )
            rewritten = response.choices[0].message.content.strip()
            return rewritten if rewritten else query
        except Exception as e:
            print(f"[rewrite_query] fallback to original — {e}")
            return query

    def _embed_query(self, query: str) -> np.ndarray:
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[query],
        )
        vector = np.array([response.data[0].embedding], dtype=np.float32)
        faiss.normalize_L2(vector)
        return vector

    def _vector_search(
        self,
        query_vector: np.ndarray,
        fetch_k: int,
        doc_type: str | None,
        specialty_id: str | None,
    ) -> list[dict]:
        """Raw FAISS search with optional metadata filtering."""
        scores, indices = self.index.search(query_vector, min(fetch_k, self.index.ntotal))
 
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
                "vector_score": float(score),
                "id": meta["id"],
                "type": meta.get("type"),
                "specialty": meta.get("specialty"),
                "specialty_id": meta.get("specialty_id"),
                "doctor_id": meta.get("doctor_id"),
                "accepts_nhif": meta.get("accepts_nhif"),
                "price": meta.get("price"),
                "rating": meta.get("rating"),
            })
        return results

    def rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        """
        Reranks candidates using GPT-4o-mini.
 
        Each candidate must have an "id" field that corresponds to a key
        in self.metadata (used to build the document snippet for the LLM).
        Falls back to the original vector order on any error.
        """
        if not candidates:
            return candidates
 
        # Build a text snippet for each candidate using the id
        id_to_meta = {m["id"]: m for m in self.metadata}
        snippets = []
        for c in candidates:
            meta = id_to_meta.get(c["id"], {})
            # Use whatever text fields are available in metadata
            parts = []
            if meta.get("specialty"):
                parts.append(f"Специалност: {meta['specialty']}")
            if meta.get("type"):
                parts.append(f"Тип: {meta['type']}")
            # Include the id itself as a hint
            parts.append(f"ID: {c['id']}")
            snippets.append(" | ".join(parts))
 
        docs_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(snippets))
        user_message = f"Въпрос на пациент: {query}\n\nДокументи:\n{docs_text}"
 
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": RERANK_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )
            import json
            raw = response.choices[0].message.content.strip()
            scores_list = json.loads(raw)
 
            if len(scores_list) != len(candidates):
                raise ValueError(
                    f"Reranker returned {len(scores_list)} scores for {len(candidates)} candidates"
                )
 
            for candidate, score_obj in zip(candidates, scores_list):
                candidate["rerank_score"] = float(score_obj["score"])
 
            candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
 
        except Exception as e:
            print(f"[rerank] fallback to vector order — {e}")
            # Assign vector score as rerank_score fallback
            for c in candidates:
                c.setdefault("rerank_score", c["vector_score"])
 
        return candidates

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_type: str | None = None,
        specialty_id: str | None = None,
        rewrite: bool = True,
        rerank: bool = True,
    ) -> list[dict]:
        """
        Full retrieval pipeline: rewrite → embed → vector search → rerank.
 
        Parameters
        ----------
        query : patient's question (Bulgarian)
        top_k : number of final results to return
        doc_type : "doctor" | "specialty" | "knowledge_base" | None
        specialty_id : filter by a specific specialty
        rewrite : whether to apply query rewriting (default True)
        rerank : whether to apply LLM reranking (default True)
 
        Returns a list of result dicts ordered by rerank_score (or
        vector_score if reranking is disabled / fails).
        """
        effective_query = self.rewrite_query(query) if rewrite else query
        if rewrite:
            print(f"[rewrite] '{query}'\n → '{effective_query}'")
 
        # Fetch extra candidates so the reranker has something to work with
        fetch_k = top_k * 6 if (doc_type or specialty_id or rerank) else top_k
        query_vector = self._embed_query(effective_query)
        candidates = self._vector_search(query_vector, fetch_k, doc_type, specialty_id)
 
        if rerank and candidates:
            # Rerank the top min(top_k*4, all) candidates to keep latency reasonable
            pool = candidates[: top_k * 4]
            pool = self.rerank(query, pool)
            # Merge back any remaining candidates (unranked) at the end
            ranked_ids = {c["id"] for c in pool}
            tail = [c for c in candidates if c["id"] not in ranked_ids]
            candidates = pool + tail
 
        return candidates[:top_k]

    def search_doctors(
        self,
        query: str,
        top_k: int = 3,
        specialty_id: str | None = None,
        nhif_only: bool = False,
    ) -> list[dict]:
        """Searches for doctors. Optional filter by specialty and NHIF."""
        results = self.search(
            query,
            top_k=top_k * 4,
            doc_type="doctor",
            specialty_id=specialty_id,
        )
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
        Builds a context string for the RAG prompt.
        Uses the full pipeline (rewrite + rerank) and returns a formatted
        text ready to be inserted into an LLM system prompt.
        """
        results = self.search(query, top_k=top_k)
 
        if not results:
            return "No relevant information found."
 
        context_parts = []
        for r in results:
            score_info = (
                f"rerank={r['rerank_score']:.3f}, vector={r['vector_score']:.3f}"
                if "rerank_score" in r
                else f"vector={r['vector_score']:.3f}"
            )
            context_parts.append(
                f"[{r['type'].upper()} | {score_info}]\n{r['id']}"
            )
 
        return "\n\n---\n\n".join(context_parts)
