from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Dict, Any, Optional

from .utils.similarity import check_similarity_scores, find_matches_with_threshold, _levenshtein_distance_score


class SimilarityRequest(BaseModel):
    title: str
    existing_titles: List[str]
    threshold: Optional[float] = None


class Match(BaseModel):
    title: str
    similarity: float
    type: Literal['phonetic', 'lexical', 'semantic', 'levenshtein']


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get('/')
def root():
    return {
        'message': 'ML Service API',
        'endpoints': {
            'health': '/health',
            'check_similarity': '/check-similarity'
        },
        'status': 'running'
    }


@app.get('/health')
def health():
    return {'ok': True}


@app.get('/favicon.ico')
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)  # No content response


@app.post('/check-similarity')
def check_similarity(payload: SimilarityRequest) -> Dict[str, Any]:
    title = payload.title.strip()
    existing = [t.strip() for t in payload.existing_titles if t and t.strip()]
    if not title:
        return {"status": "Invalid", "matches": []}
    if not existing:
        return {"status": "Unique", "matches": []}

    # Use user threshold or default to 0.75
    threshold = payload.threshold if payload.threshold is not None else 0.75
    
    # Check Levenshtein distance first for early break
    levenshtein_matches = []
    for t in existing:
        score = _levenshtein_distance_score(title, t)
        if score >= threshold:
            levenshtein_matches.append({
                "title": t,
                "similarity": float(round(score, 4)),
                "type": "levenshtein"
            })
        score = _levenshtein_distance_score(' '.join(title.split()[::-1]), t)
        if score >= threshold:
            levenshtein_matches.append({
                "title": t,
                "similarity": float(round(score, 4)),
                "type": "levenshtein"
            })
    
    # If we found Levenshtein matches, check if we should return early
    if levenshtein_matches:
        # If we have a very strong Levenshtein match (e.g. exact or near-exact),
        # we can safely return without running heavier methods.
        max_lev = max(m["similarity"] for m in levenshtein_matches)
        if max_lev >= max(threshold, 0.95):
            final_matches = sorted(levenshtein_matches, key=lambda m: m["similarity"], reverse=True)
            return {
                "status": "Not Unique",
                "matches": final_matches
            }

        # Check if any of these titles also have matches in other methods
        matched_titles = set(match["title"] for match in levenshtein_matches)
        
        # Get other similarity scores only for the titles that already
        # matched via Levenshtein, to avoid unnecessary work.
        candidate_titles = [t for t in existing if t in matched_titles]
        phonetic, lexical, semantic = check_similarity_scores(title, candidate_titles, threshold)
        
        # Check for additional matches in other methods
        other_matches = []
        for i, t in enumerate(candidate_titles):
            if phonetic[i] >= threshold:
                other_matches.append({
                    "title": t,
                    "similarity": float(round(phonetic[i], 4)),
                    "type": "phonetic"
                })
            if lexical[i] >= threshold:
                other_matches.append({
                    "title": t,
                    "similarity": float(round(lexical[i], 4)),
                    "type": "lexical"
                })
            if semantic[i] >= threshold:
                other_matches.append({
                    "title": t,
                    "similarity": float(round(semantic[i], 4)),
                    "type": "semantic"
                })
        
        # Combine all matches and deduplicate
        all_matches = levenshtein_matches + other_matches
        dedup = {}
        for m in all_matches:
            key = (m["title"], m["type"])
            if key not in dedup or m["similarity"] > dedup[key]["similarity"]:
                dedup[key] = m
        
        final_matches = sorted(dedup.values(), key=lambda m: m["similarity"], reverse=True)
        
        return {
            "status": "Not Unique",
            "matches": final_matches
        }
    
    # If no Levenshtein matches, proceed with other methods
    phonetic, lexical, semantic = check_similarity_scores(title, existing, threshold)
    
    # Find matches using the utility function
    matches = find_matches_with_threshold(phonetic, lexical, semantic, existing, threshold)
    
    # If we found exactly one match, return early
    if len(matches) == 1:
        return {
            "status": "Not Unique",
            "matches": matches
        }
    
    # If we found multiple matches, return them
    if matches:
        return {
            "status": "Not Unique",
            "matches": matches
        }
    
    # No matches found
    return {
        "status": "Unique",
        "matches": []
    }

