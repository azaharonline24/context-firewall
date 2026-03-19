def deduplicate_chunks(chunks):
    """
    Remove duplicate chunks based on the 'text' field while preserving the order of first occurrence.
    Each chunk is expected to be a dict with a 'text' key.
    """
    seen = set()
    result = []
    for chunk in chunks:
        text = chunk.get("text")
        if text is None:
            # If no text, treat as unique (or could skip). We'll treat as unique.
            result.append(chunk)
            continue
        if text not in seen:
            seen.add(text)
            result.append(chunk)
    return result
