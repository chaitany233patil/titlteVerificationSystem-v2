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

print(_sbert_model)

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
    
    if not a_codes or not b_codes:
        return 0.0

    distance = jellyfish.levenshtein_distance(a_codes, b_codes)
    max_len = max(len(a_codes), len(b_codes))
    similarity = 1 - (distance / max_len)

    return similarity


def _phonetic_scores(query: str, corpus: List[str]) -> List[float]:
    """Vectorized phonetic similarity for a query against a corpus.

    This avoids recomputing the metaphone of the query for every title
    and is significantly faster for large corpora.
    """
    if not corpus:
        return []

    q_code = jellyfish.metaphone(query)
    if not q_code:
        return [0.0 for _ in corpus]

    scores: List[float] = []
    for t in corpus:
        t_code = jellyfish.metaphone(t)
        if q_code == t_code:
            scores.append(1.0)
            continue
        if not t_code:
            scores.append(0.0)
            continue
        dist = jellyfish.levenshtein_distance(q_code, t_code)
        max_len = max(len(q_code), len(t_code))
        scores.append(1.0 - (dist / max_len))

    return scores


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
    
    # Encode query once
    q_emb = _sbert_model.encode([query], convert_to_tensor=True)
    # Encode corpus in a single batch (still O(N) but much faster than
    # calling encode for each item).
    c_emb = _sbert_model.encode(corpus, convert_to_tensor=True)
    sims = st_util.cos_sim(q_emb, c_emb).cpu().numpy().flatten().tolist()
    return sims


def check_similarity_scores(title: str, existing: List[str], threshold: float) -> Tuple[List[float], List[float], List[float]]:
    """Calculate all similarity scores for a title against existing titles."""
    if not existing:
        return [], [], []

    # Phonetic scores (vectorized implementation)
    phonetic = _phonetic_scores(title.lower(), [t.lower() for t in existing])

    # Lexical scores for all titles
    lexical = _lexical_scores(title, existing, threshold)

    # Limit expensive semantic computation to the most promising candidates.
    # We keep all methods but only run the heaviest one on a subset.
    n = len(existing)
    semantic: List[float] = [0.0] * n

    # Decide how many candidates should go through semantic similarity.
    max_semantic_candidates = min(500, n)

    # Sort indices by lexical score (desc) and take the top candidates.
    sorted_indices = sorted(range(n), key=lambda i: lexical[i], reverse=True)
    candidate_indices = sorted_indices[:max_semantic_candidates]

    # Additionally, ensure we keep any titles whose lexical score is already
    # above (threshold - 0.1), in case the top-N heuristic would miss them.
    extra_indices = [
        i for i in range(n)
        if lexical[i] >= max(threshold - 0.1, 0.0) and i not in candidate_indices
    ]
    candidate_indices.extend(extra_indices)

    # Deduplicate indices while preserving order
    seen = set()
    unique_candidate_indices = []
    for idx in candidate_indices:
        if idx not in seen:
            seen.add(idx)
            unique_candidate_indices.append(idx)

    if unique_candidate_indices:
        candidate_corpus = [existing[i] for i in unique_candidate_indices]
        candidate_semantic = _semantic_scores(title, candidate_corpus, threshold)
        for i, score in zip(unique_candidate_indices, candidate_semantic):
            semantic[i] = score

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
