import numpy as np
import jellyfish
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple

try:
    from sentence_transformers import SentenceTransformer, util as st_util
    _sbert_model: SentenceTransformer | None = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
except Exception:
    _sbert_model = None


def _levenshtein_distance_score(a: str, b: str) -> float:
    """Calculate normalized Levenshtein distance score between two strings."""
    if not a or not b:
        return 0.0
    
    # Calculate Levenshtein distance
    dist = jellyfish.levenshtein_distance(a.lower(), b.lower())
    max_len = max(len(a), len(b))
    
    # Normalize to 0-1 range where 1 means identical
    if max_len == 0:
        return 1.0
    
    return 1.0 - (dist / max_len)


def _phonetic_score(a: str, b: str) -> float:
    """Calculate phonetic similarity using Double Metaphone codes."""
    # Use Double Metaphone codes; compare primary code equality
    a_codes = jellyfish.metaphone(a)
    b_codes = jellyfish.metaphone(b)
    
    if a_codes == b_codes:
        return 1.0
    
    # If metaphone codes don't match, return 0
    return 0.0


def _lexical_scores(query: str, corpus: List[str], threshold: float) -> List[float]:
    """Calculate lexical similarity scores using TF-IDF and cosine similarity."""
    if not corpus:
        return []
    
    texts = [query] + corpus
    vec = TfidfVectorizer().fit_transform(texts)
    sims = cosine_similarity(vec[0:1], vec[1:]).flatten()
    return sims.tolist()


def _semantic_scores(query: str, corpus: List[str], threshold: float) -> List[float]:
    """Calculate semantic similarity scores using sentence transformers."""
    if _sbert_model is None or not corpus:
        return [0.0 for _ in corpus]
    
    q_emb = _sbert_model.encode([query], convert_to_tensor=True)
    c_emb = _sbert_model.encode(corpus, convert_to_tensor=True)
    sims = st_util.cos_sim(q_emb, c_emb).cpu().numpy().flatten().tolist()
    return sims


def check_similarity_scores(title: str, existing: List[str], threshold: float) -> Tuple[List[float], List[float], List[float]]:
    """Calculate all similarity scores for a title against existing titles."""
    phonetic = [_phonetic_score(title.lower(), t.lower()) for t in existing]
    lexical = _lexical_scores(title, existing, threshold)
    semantic = _semantic_scores(title, existing, threshold)
    
    return phonetic, lexical, semantic


def find_matches_with_threshold(phonetic: List[float], lexical: List[float], semantic: List[float], 
                               existing: List[str], threshold: float) -> List[dict]:
    """Find matches based on threshold and return early if only one match found."""
    matches = []
    
    for i, t in enumerate(existing):
        # Check phonetic similarity
        if phonetic[i] >= threshold:
            matches.append({
                "title": t,
                "similarity": float(round(phonetic[i], 4)),
                "type": "phonetic"
            })
        
        # Check lexical similarity
        if lexical[i] >= threshold:
            matches.append({
                "title": t,
                "similarity": float(round(lexical[i], 4)),
                "type": "lexical"
            })
        
        # Check semantic similarity
        if semantic[i] >= threshold:
            matches.append({
                "title": t,
                "similarity": float(round(semantic[i], 4)),
                "type": "semantic"
            })
    
    # Deduplicate by (title, type) keeping max similarity
    dedup = {}
    for m in matches:
        key = (m["title"], m["type"])
        if key not in dedup or m["similarity"] > dedup[key]["similarity"]:
            dedup[key] = m
    
    final_matches = sorted(dedup.values(), key=lambda m: m["similarity"], reverse=True)
    
    return final_matches
