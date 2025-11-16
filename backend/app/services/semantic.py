from typing import List, Dict, Any, Iterable, Tuple
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer, util


@dataclass
class SkillItem:
    id: str
    name: str
    description: str


class SemanticSkillMatcher:
    """
    Semantic skill matcher using SentenceTransformers.

    - Accepts catalog as EITHER:
        (A) list[dict]: rows with keys like role_title/skill/skill_category/skill_type
        (B) dict[str, list[str]]: canonical skill -> list of aliases
    - Provides BOTH:
        • top_matches_for_text(text, top_k, score_threshold)  -> list[dict]
        • predict(text, top_k, threshold)                     -> list[(skill_label, score)]
          (for compatibility with your router code)
    """

    def __init__(
        self,
        catalog: List[Dict[str, Any]] | Dict[str, List[str]],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        # Normalize the incoming catalog to a list[dict] with common fields.
        self.catalog_raw: List[Dict[str, Any]] = self._normalize_catalog(catalog)
        self.model_name = model_name

        # Lazy-loaded fields
        self._model: SentenceTransformer | None = None
        self._catalog_texts: List[str] | None = None
        self._catalog_embeddings = None

    # ---------- catalog normalization ----------

    def _normalize_catalog(
        self, catalog: List[Dict[str, Any]] | Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Convert either a list-of-rows or a dict-of-aliases into a unified
        list-of-rows with keys: role_title, skill, skill_category, skill_type.
        """
        rows: List[Dict[str, Any]] = []

        # Case A: already a list of dict rows
        if isinstance(catalog, list):
            for r in catalog:
                # Ensure required keys exist; default blanks if missing
                rows.append({
                    "role_title":    r.get("role_title", ""),
                    "skill":         r.get("skill") or r.get("name") or "",
                    "skill_category":r.get("skill_category", ""),
                    "skill_type":    r.get("skill_type", ""),
                })
            return rows

        # Case B: dict of {canonical_skill: [aliases]}
        if isinstance(catalog, dict):
            for canon, aliases in catalog.items():
                # canonical entry
                rows.append({
                    "role_title":     "",
                    "skill":          str(canon),
                    "skill_category": "",
                    "skill_type":     "canonical",
                })
                # alias entries
                if isinstance(aliases, list):
                    for a in aliases:
                        rows.append({
                            "role_title":     "",
                            "skill":          str(a),
                            "skill_category": "",
                            "skill_type":     "alias",
                        })
            return rows

        # Fallback: empty
        return rows

    # ---------- internal helpers ----------

    def _ensure_model(self) -> SentenceTransformer:
        """Load the SentenceTransformer model only when first needed."""
        if self._model is None:
            # device="cpu" to avoid GPU/config issues and stay lighter
            self._model = SentenceTransformer(self.model_name, device="cpu")
        return self._model

    def _ensure_catalog_embeddings(self):
        """Compute catalog embeddings only once."""
        if self._catalog_embeddings is None:
            model = self._ensure_model()
            # Build text for each catalog skill/role row
            self._catalog_texts = [
                f"{row.get('role_title','')} - {row.get('skill','')} - {row.get('skill_category','')}"
                for row in self.catalog_raw
            ]
            self._catalog_embeddings = model.encode(
                self._catalog_texts,
                convert_to_tensor=True,
                normalize_embeddings=True,
            )
        return self._catalog_embeddings

    # ---------- public API (original) ----------

    def top_matches_for_text(
        self,
        text: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Given a free-text (e.g. extracted resume text), return top matching
        skills/roles from the catalog with cosine similarity scores.
        """
        if not text or not text.strip():
            return []

        model = self._ensure_model()
        catalog_emb = self._ensure_catalog_embeddings()

        query_emb = model.encode(
            [text],
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        cos_scores = util.cos_sim(query_emb, catalog_emb)[0]  # shape [N]
        scores = cos_scores.cpu().numpy()

        # Rank highest → lowest
        top_idx = np.argsort(-scores)[:top_k]
        results: List[Dict[str, Any]] = []

        for idx in top_idx:
            score = float(scores[idx])
            if score < score_threshold:
                continue
            row = self.catalog_raw[int(idx)]
            results.append(
                {
                    "score": score,
                    "role_title": row.get("role_title"),
                    "skill": row.get("skill"),
                    "skill_category": row.get("skill_category"),
                    "skill_type": row.get("skill_type"),
                }
            )

        return results

    # ---------- public API (compat with your router) ----------

    def predict(
        self,
        text: str,
        top_k: int = 6,
        threshold: float = 0.5,
    ) -> List[Tuple[str, float]]:
        """
        Compatibility shim for code that expects:
           List[(skill_label: str, score: float in 0..1)]
        Uses top_matches_for_text under the hood and returns (skill, score).
        """
        rows = self.top_matches_for_text(text, top_k=top_k, score_threshold=threshold)
        out: List[Tuple[str, float]] = []
        for r in rows:
            lab = (r.get("skill") or "").strip()
            sc  = float(r.get("score") or 0.0)
            if lab:
                # clamp to 0..1 just in case
                out.append((lab, max(0.0, min(1.0, sc))))
        return out
