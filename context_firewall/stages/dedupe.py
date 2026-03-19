def deduplicate_chunks(chunks):
    """
    Remove duplicate chunks while preserving the order of first occurrence.
    """
    seen = set()
    result = []
    for chunk in chunks:
        if chunk not in seen:
            seen.add(chunk)
            result.append(chunk)
    return result
