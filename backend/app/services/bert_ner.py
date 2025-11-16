from typing import List, Tuple, Dict
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import numpy as np

class BertSkillNER:
    """
    Extracts candidate phrases with BERT NER and maps them to your catalog via SBERT.
    """
    def __init__(self, catalog: Dict[str, List[str]],
                 ner_model: str = "dslim/bert-base-NER",
                 embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.ner = pipeline("token-classification", model=ner_model, aggregation_strategy="simple")
        self.labels = list(catalog.keys())
        self.embed = SentenceTransformer(embed_model)
        self.label_emb = self.embed.encode(self.labels, normalize_embeddings=True, convert_to_numpy=True)

    def extract_terms(self, text: str) -> List[str]:
        out = set()
        for ent in self.ner(text):
            chunk = (ent.get("word") or "").strip()
            if chunk and len(chunk) <= 60:
                out.add(chunk)
        return sorted(out)

    def map_to_skills(self, terms: List[str], threshold: float = 0.65) -> List[Tuple[str, float]]:
        """
        Map extracted terms to catalog labels using cosine similarity.
        Default threshold raised to 0.65 to reduce noisy matches.
        """
        if not terms: return []
        q = self.embed.encode(terms, normalize_embeddings=True, convert_to_numpy=True)
        sims = util.cos_sim(q, self.label_emb).cpu().numpy()
        picks = []
        for i, term in enumerate(terms):
            j = int(np.argmax(sims[i]))
            score = float(sims[i, j])
            if score >= threshold:
                picks.append((self.labels[j], score))
        # keep best score per label
        best: Dict[str, float] = {}
        for lab, sc in picks:
            best[lab] = max(sc, best.get(lab, 0.0))
        return sorted(best.items(), key=lambda x: x[1], reverse=True)
