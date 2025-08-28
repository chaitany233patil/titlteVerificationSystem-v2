from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional

import numpy as np
import jellyfish
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer, util as st_util
    _sbert_model: SentenceTransformer | None = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
except Exception:
    _sbert_model = None


class SimilarityRequest(BaseModel):
    title: str
    existing_titles: List[str]
    threshold: Optional[float] = None


class Match(BaseModel):
    title: str
    similarity: float
    type: Literal['phonetic', 'lexical', 'semantic']


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"]
)


@app.get('/health')
def health():
    return {'ok': True}


def _phonetic_score(a: str, b: str) -> float:
    # Use Double Metaphone codes; compare primary code equality or Levenshtein distance
    a_codes = jellyfish.metaphone(a)
    b_codes = jellyfish.metaphone(b)
    if a_codes == b_codes:
        return 1.0
    # fallback: normalized edit distance in metaphone space
    dist = jellyfish.levenshtein_distance(a_codes, b_codes)
    max_len = max(len(a_codes), len(b_codes)) or 1
    return 1.0 - (dist / max_len)


def _lexical_scores(query: str, corpus: List[str]) -> List[float]:
    texts = [query] + corpus
    vec = TfidfVectorizer().fit_transform(texts)
    sims = cosine_similarity(vec[0:1], vec[1:]).flatten()
    return sims.tolist()


def _semantic_scores(query: str, corpus: List[str]) -> List[float]:
    if _sbert_model is None or not corpus:
        return [0.0 for _ in corpus]
    q_emb = _sbert_model.encode([query], convert_to_tensor=True)
    c_emb = _sbert_model.encode(corpus, convert_to_tensor=True)
    sims = st_util.cos_sim(q_emb, c_emb).cpu().numpy().flatten().tolist()
    return sims


@app.post('/check-similarity')
def check_similarity(payload: SimilarityRequest) -> Dict[str, Any]:
    title = payload.title.strip()
    existing = [t.strip() for t in payload.existing_titles if t and t.strip()]
    if not title:
        return {"status": "Invalid", "matches": []}
    if not existing:
        return {"status": "Unique", "matches": []}

    # Compute scores
    phonetic = [ _phonetic_score(title.lower(), t.lower()) for t in existing ]
    lexical = _lexical_scores(title, existing)
    semantic = _semantic_scores(title, existing)

    matches: List[Match] = []

    # Thresholds (use provided threshold for all, else defaults)
    base_thresh = payload.threshold if payload.threshold is not None else 0.75
    PHONETIC_THRESH = max(0.0, min(1.0, base_thresh if payload.threshold is not None else 0.85))
    LEXICAL_THRESH = max(0.0, min(1.0, base_thresh))
    SEMANTIC_THRESH = max(0.0, min(1.0, base_thresh))

    for i, t in enumerate(existing):
        if phonetic[i] >= PHONETIC_THRESH:
            matches.append(Match(title=t, similarity=float(round(phonetic[i], 4)), type='phonetic'))
        if lexical[i] >= LEXICAL_THRESH:
            matches.append(Match(title=t, similarity=float(round(lexical[i], 4)), type='lexical'))
        if semantic[i] >= SEMANTIC_THRESH:
            matches.append(Match(title=t, similarity=float(round(semantic[i], 4)), type='semantic'))

    # Deduplicate by (title, type) keeping max similarity
    dedup: Dict[tuple, Match] = {}
    for m in matches:
        key = (m.title, m.type)
        if key not in dedup or m.similarity > dedup[key].similarity:
            dedup[key] = m

    final_matches = sorted(dedup.values(), key=lambda m: m.similarity, reverse=True)
    status = "Not Unique" if final_matches else "Unique"

    return {
        "status": status,
        "matches": [m.dict() for m in final_matches]
    }

