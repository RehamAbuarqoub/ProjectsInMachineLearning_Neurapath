from typing import Dict, List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer, util

class SemanticSkillMatcher:
    """
    Computes similarity of the resume text to catalog labels and returns strong matches.
    """
    def __init__(self, catalog: Dict[str, List[str]], model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.catalog = catalog
        self.labels = list(catalog.keys())
        self.model = SentenceTransformer(model_name)
        self.label_emb = self.model.encode(self.labels, normalize_embeddings=True, convert_to_numpy=True)

    def _chunk(self, text: str, max_len: int = 220):
        import re
        sents = re.split(r"(?<=[\.\!\?])\s+", text)
        chunks, buf = [], ""
        for s in sents:
            if len(buf) + len(s) < max_len:
                buf = (buf + " " + s).strip()
            else:
                if buf: chunks.append(buf)
                buf = s
        if buf: chunks.append(buf)
        return chunks or [text]

    def predict(self, text: str, top_k: int = 5, threshold: float = 0.62) -> List[Tuple[str, float]]:
        """
        Default threshold raised to 0.62 to avoid spurious matches.
        """
        chunks = self._chunk(text)
        emb = self.model.encode(chunks, normalize_embeddings=True, convert_to_numpy=True)
        sims = util.cos_sim(emb, self.label_emb).cpu().numpy()
        label_scores = sims.max(axis=0)
        idx = np.argsort(-label_scores)[: max(top_k*4, 30)]
        return [(self.labels[i], float(label_scores[i])) for i in idx if label_scores[i] >= threshold]
