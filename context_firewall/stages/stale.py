def evict_stale(chunks, max_age_seconds: float, reference_time: float):
    """
    Remove chunks older than max_age_seconds relative to reference_time.
    Each chunk is expected to be a dict with a 'timestamp' key (float).
    If a chunk lacks a timestamp, it is kept (treated as unknown age).
    Returns a new list of chunks that are not stale.
    """
    if max_age_seconds < 0:
        raise ValueError("max_age_seconds must be non-negative")
    cutoff = reference_time - max_age_seconds
    result = []
    for chunk in chunks:
        ts = chunk.get("timestamp")
        if ts is None:
            # No timestamp -> keep
            result.append(chunk)
        elif ts >= cutoff:
            result.append(chunk)
        # else: stale, skip
    return result
