"""
TF-IDF + RandomForest multi-label skill detector.
Used when you have a labeled resume dataset. Otherwise alias+semantic+NER still return value.
"""
import ast, json, os
from typing import List, Dict, Any, Optional
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score

from app.services.text import clean_text, find_spans, merge_spans

ARTIF_PATH = "app/artifacts/skill_rf.pkl"

def _parse_labels(x):
    if isinstance(x, list): return x
    if pd.isna(x): return []
    s = str(x).strip()
    try: return json.loads(s)
    except Exception:
        try: return ast.literal_eval(s)
        except Exception: return [t.strip().lower() for t in s.replace(",", ";").split(";") if t.strip()]

class SkillModelManager:
    def __init__(self, catalog: Dict[str, List[str]], roles: Dict[str, Any]):
        self.catalog, self.roles = catalog, roles
        self.pipe: Optional[Pipeline] = None
        self.mlb: Optional[MultiLabelBinarizer] = None
        self.thresh: float = 0.35
        self.state, self.message, self.scores = "idle", None, None
        if os.path.exists(ARTIF_PATH):
            try:
                art = joblib.load(ARTIF_PATH)
                self.pipe, self.mlb = art["pipe"], art["mlb"]
                self.thresh = art.get("thresh", self.thresh)
                self.state = "done"
            except Exception as e:
                self.state, self.message = "error", f"Model load failed: {e}"

    def _alias2canon(self) -> Dict[str,str]:
        m = {}
        for canon, aliases in self.catalog.items():
            m[canon.lower()] = canon.lower()
            for a in aliases: m[a.lower()] = canon.lower()
        return m

    def normalize_labels(self, labs: List[str]) -> List[str]:
        a2c = self._alias2canon()
        return sorted({a2c.get(l.lower(), l.lower()) for l in labs})

    def _build(self, n_estimators=300, ngram=(1,2), min_df=2):
        vec = TfidfVectorizer(lowercase=True, analyzer="word", ngram_range=ngram, min_df=min_df, max_df=0.9)
        rf  = RandomForestClassifier(n_estimators=n_estimators, max_features="sqrt", n_jobs=-1, random_state=42)
        clf = OneVsRestClassifier(rf, n_jobs=-1)
        return Pipeline([("tfidf", vec), ("clf", clf)])

    def train(self, train_csv: str, test_csv: Optional[str], thresh: float, n_estimators=300, ngram=(1,2), min_df=2):
        self.state, self.message, self.scores = "running", None, None
        try:
            df = pd.read_csv(train_csv)
            df["labels"] = df["labels"].apply(_parse_labels).apply(self.normalize_labels)
            df["resume_text"] = df["resume_text"].fillna("").astype(str).apply(clean_text)

            labels = sorted({lab for labs in df["labels"] for lab in labs})
            mlb = MultiLabelBinarizer(classes=labels); mlb.fit([labels])

            if test_csv and os.path.exists(test_csv):
                df_test = pd.read_csv(test_csv)
                df_test["labels"] = df_test["labels"].apply(_parse_labels).apply(self.normalize_labels)
                df_test["resume_text"] = df_test["resume_text"].fillna("").astype(str).apply(clean_text)
            else:
                df_test = df.sample(frac=0.2, random_state=42)
                df = df.drop(df_test.index)

            pipe = self._build(n_estimators=n_estimators, ngram=ngram, min_df=min_df)
            Xtr, Ytr = df["resume_text"].tolist(), mlb.transform(df["labels"])
            pipe.fit(Xtr, Ytr)

            def _eval(dframe):
                X = dframe["resume_text"].tolist()
                Yt = mlb.transform(dframe["labels"])
                Yp = pipe.predict_proba(X)
                Yh = (Yp >= thresh).astype(int)
                return {"micro_f1": float(f1_score(Yt, Yh, average="micro", zero_division=0)),
                        "macro_f1": float(f1_score(Yt, Yh, average="macro", zero_division=0))}

            self.scores = {"train": _eval(df), "test": _eval(df_test)}
            os.makedirs(os.path.dirname(ARTIF_PATH), exist_ok=True)
            joblib.dump({"pipe": pipe, "mlb": mlb, "thresh": thresh}, ARTIF_PATH)

            self.pipe, self.mlb, self.thresh, self.state = pipe, mlb, thresh, "done"
        except Exception as e:
            self.state, self.message = "error", str(e)

    def predict_enriched(self, text: str):
        names = set()
        if self.pipe and self.mlb:
            probs = self.pipe.predict_proba([text])[0]
            names = {self.mlb.classes_[i] for i, p in enumerate(probs) if p >= self.thresh}

        enriched = {}
        # Alias evidence with spans
        for canon, aliases in self.catalog.items():
            from app.services.text import find_spans, merge_spans
            spans = []
            for a in aliases: spans += find_spans(text, a)
            spans = merge_spans(spans)
            if spans:
                enriched[canon] = {"skill": canon, "score": round(0.5 + 0.25*len(spans), 2),
                                   "evidence_offsets": spans,
                                   "aliases_matched": [a for a in aliases if find_spans(text, a)]}
        # RF names
        for s in names:
            enriched.setdefault(s, {"skill": s, "score": 0.6, "evidence_offsets": [], "aliases_matched": []})
        return sorted(enriched.values(), key=lambda x: x["score"], reverse=True)

    def compute_gaps(self, extracted: List[str], required: List[str]) -> List[str]:
        ex = {e.lower() for e in extracted}
        return [r.lower() for r in required if r.lower() not in ex]

    def status(self): return {"state": self.state, "message": self.message, "scores": self.scores}
