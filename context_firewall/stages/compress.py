import re
from typing import List, Dict, Any

def _split_sentences(text: str) -> List[str]:
    """
    Naive sentence split: split on punctuation . ! ? followed by whitespace or end.
    Keeps the punctuation with the sentence.
    """
    if not text:
        return []
    # Regex: split on (?<=[.!?])\s+
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty strings
    return [s for s in sentences if s]

def compress_chunks(chunks: List[Dict[str, Any]], ratio: float = 0.5) -> List[Dict[str, Any]]:
    """
    Extractive summarization: keep the first N sentences of each chunk,
    where N = ceil(num_sentences * ratio). Order of sentences is preserved.
    If ratio <= 0, returns empty string for each chunk.
    If ratio >= 1, returns original chunk unchanged.
    Other fields are copied shallowly.
    """
    if not chunks:
        return []
    if ratio <= 0.0:
        # Return empty strings but keep other fields
        return [{**c, "text": ""} for c in chunks]
    if ratio >= 1.0:
        # Return a shallow copy to avoid mutating original
        return [dict(c) for c in chunks]

    result = []
    for chunk in chunks:
        chunk_copy = dict(chunk)  # shallow copy
        text = chunk_copy.get("text", "")
        if not isinstance(text, str):
            text = str(text)
        sentences = _split_sentences(text)
        if not sentences:
            chunk_copy["text"] = ""
            result.append(chunk_copy)
            continue
        num_keep = max(1, int(len(sentences) * ratio + 0.999999))  # ceil
        if num_keep > len(sentences):
            num_keep = len(sentences)
        kept_sentences = sentences[:num_keep]
        chunk_copy["text"] = " ".join(kept_sentences)
        result.append(chunk_copy)
    return result
