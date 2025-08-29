# ML Service - Similarity Detection

This service provides similarity detection between titles using multiple algorithms:
- **Levenshtein Distance**: String edit distance for typo detection
- **Phonetic Similarity**: Double Metaphone codes for sound-alike detection
- **Lexical Similarity**: TF-IDF + Cosine similarity for word-based matching
- **Semantic Similarity**: Sentence transformers for meaning-based matching

## Project Structure

```
ml-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application with endpoints
│   └── utils/
│       ├── __init__.py
│       └── similarity.py       # All similarity calculation functions
├── test_similarity.py          # Test script for similarity functions
├── requirements.txt
├── Dockerfile
└── README.md
```

## Key Features

### 1. Separated Functions
- **Levenshtein Distance**: Now in `_levenshtein_distance_score()` function
- **Phonetic Similarity**: Clean `_phonetic_score()` function using Double Metaphone
- **Lexical Similarity**: TF-IDF vectorization with cosine similarity
- **Semantic Similarity**: Sentence transformer embeddings

### 2. Early Break Logic
- Checks Levenshtein distance first for quick matches
- Returns early if exactly one match is found
- Combines results from multiple similarity methods

### 3. User Threshold Control
- All similarity functions accept user-defined threshold
- Consistent threshold application across all methods
- Default threshold of 0.75 if none provided

## API Endpoints

### POST `/check-similarity`
Check if a title is similar to existing titles.

**Request Body:**
```json
{
  "title": "string",
  "existing_titles": ["string"],
  "threshold": 0.8  // optional, defaults to 0.75
}
```

**Response:**
```json
{
  "status": "Not Unique" | "Unique",
  "matches": [
    {
      "title": "string",
      "similarity": 0.95,
      "type": "levenshtein" | "phonetic" | "lexical" | "semantic"
    }
  ]
}
```

## Usage Examples

### Running Tests
```bash
cd ml-service
python test_similarity.py
```

### Starting the Service
```bash
cd ml-service
uvicorn app.main:app --reload
```

## Algorithm Details

### Levenshtein Distance
- Normalized edit distance (0-1 scale)
- 1.0 = identical strings
- 0.0 = completely different
- Good for detecting typos and minor variations

### Phonetic Similarity
- Uses Double Metaphone algorithm
- 1.0 = identical phonetic codes
- 0.0 = different phonetic codes
- Good for sound-alike titles

### Lexical Similarity
- TF-IDF vectorization of text
- Cosine similarity between vectors
- Good for word-based similarity

### Semantic Similarity
- Sentence transformer embeddings
- Cosine similarity in semantic space
- Good for meaning-based similarity

## Performance Optimizations

1. **Early Break**: Returns immediately when Levenshtein matches are found
2. **Single Match Detection**: Returns early if exactly one match is found
3. **Efficient Deduplication**: Removes duplicate matches by title and type
4. **Threshold Filtering**: Only processes scores above user threshold

## Dependencies

- FastAPI: Web framework
- NumPy: Numerical computations
- Jellyfish: String similarity algorithms
- Scikit-learn: TF-IDF and cosine similarity
- Sentence-transformers: Semantic embeddings (optional)
