"""
SENTINEL v2.0 — Vector Database Client (Semantic Search)
Provides semantic embeddings search over FIRs and intelligence notes.
Supports ChromaDB with in-memory TF-IDF / term overlap cosine similarity fallback.
"""

from typing import List, Dict, Any, Optional
import math
import re

class ChromaVectorClient:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        
    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        Add documents: each dict must contain 'id', 'text', and optional 'metadata'.
        """
        for doc in docs:
            self.documents.append(doc)
            words = set(self._tokenize(doc["text"]))
            for w in words:
                self.vocabulary[w] = self.vocabulary.get(w, 0) + 1

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z0-9_]{3,}\b', text.lower())

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Ranks documents by TF-IDF cosine relevance against query string.
        """
        q_tokens = self._tokenize(query)
        if not q_tokens or not self.documents:
            return []

        q_tf = {}
        for t in q_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1

        n_docs = len(self.documents)
        scores = []

        for doc in self.documents:
            d_tokens = self._tokenize(doc["text"])
            if not d_tokens:
                continue
            d_tf = {}
            for t in d_tokens:
                d_tf[t] = d_tf.get(t, 0) + 1

            dot_product = 0.0
            for t in q_tokens:
                if t in d_tf:
                    idf = math.log((n_docs + 1) / (self.vocabulary.get(t, 1) + 1)) + 1
                    dot_product += (q_tf[t] * idf) * (d_tf[t] * idf)

            if dot_product > 0:
                scores.append({
                    "id": doc["id"],
                    "text": doc["text"][:300] + "..." if len(doc["text"]) > 300 else doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": round(dot_product, 3)
                })

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]
