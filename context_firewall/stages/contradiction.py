import re

# Simple opposite pairs for contradiction detection
_OPPOSITE_PAIRS = {
    frozenset(["yes", "no"]),
    frozenset(["true", "false"]),
    frozenset(["correct", "incorrect"]),
    frozenset(["right", "wrong"]),
    frozenset(["affirmative", "negative"]),
    frozenset(["agree", "disagree"]),
    frozenset(["accept", "reject"]),
    frozenset(["allow", "deny"]),
}

def _normalize(text: str) -> str:
    """
    Lowercase, strip punctuation, collapse whitespace.
    """
    text = text.lower().strip()
    # Remove punctuation (keep letters, digits, spaces)
    text = re.sub(r"[^\w\s]", "", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text

def are_contradictory(a: str, b: str) -> bool:
    """
    Return True if a and b are considered contradictory:
    - One is the negation of the other (contains " not " vs without)
    - Or they are direct opposites from a predefined set.
    """
    na = _normalize(a)
    nb = _normalize(b)

    # Negation check: e.g., "is blue" vs "is not blue"
    if f" not " in na:
        without_not = na.replace(" not ", " ")
        without_not = re.sub(r"\s+", " ", without_not).strip()
        if without_not == nb:
            return True
    if f" not " in nb:
        without_not = nb.replace(" not ", " ")
        without_not = re.sub(r"\s+", " ", without_not).strip()
        if without_not == na:
            return True

    # Direct opposite check
    # Split into words; if both are single words and form an opposite pair, treat as contradictory
    words_a = set(na.split())
    words_b = set(nb.split())
    if len(words_a) == 1 and len(words_b) == 1:
        pair = frozenset([next(iter(words_a)), next(iter(words_b))])
        if pair in _OPPOSITE_PAIRS:
            return True

    return False

def detect_contradictions(chunks):
    """
    Given a list of chunk dicts (each with at least a 'text' field), return a new list where contradictory
    statements are removed, keeping the later chunk when a contradiction is found between an earlier kept chunk
    and the current chunk.
    """
    kept = []
    for chunk in chunks:
        text = chunk.get("text", "")
        # Filter out any kept chunk that contradicts the current chunk
        kept = [k for k in kept if not are_contradictory(k.get("text", ""), text)]
        kept.append(chunk)
    return kept
