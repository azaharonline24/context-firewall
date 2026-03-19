import re
from typing import List, Dict, Any, Optional

def _tokenize(text: str) -> List[str]:
    # Lowercase, split on non-alphanumeric
    text = text.lower()
    tokens = re.findall(r"\w+", text)
    return tokens

def rank_chunks(chunks: List[Dict[str, Any]], query: str, top_k: Optional[int] = None, min_score: float = 0.0) -> List[Dict[str, Any]]:
    """
    Rank chunks by simple term frequency matching.
    Each chunk is expected to have a 'text' field.
    Returns a new list of chunks with an added 'score' field (float between 0 and 1).
    Optionally limit to top_k and filter by min_score.
    """
    if not chunks:
        return []
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        # No query tokens, return original order with score 0
        for c in chunks:
            c = dict(c)  # copy to avoid mutating original
            c['score'] = 0.0
        return chunks

    scored = []
    for chunk in chunks:
        chunk_copy = dict(chunk)  # shallow copy
        text = chunk_copy.get('text', '')
        if not isinstance(text, str):
            text = str(text)
        tokens = _tokenize(text)
        total = len(tokens)
        if total == 0:
            score = 0.0
        else:
            matches = sum(1 for t in tokens if t in query_tokens)
            score = matches / total  # simple proportion
        chunk_copy['score'] = score
        scored.append(chunk_copy)

    # Sort descending by score
    scored.sort(key=lambda x: x['score'], reverse=True)

    # Apply min_score filter
    if min_score > 0.0:
        scored = [c for c in scored if c['score'] >= min_score]

    # Apply top_k
    if top_k is not None and top_k >= 0:
        scored = scored[:top_k]

    return scored
