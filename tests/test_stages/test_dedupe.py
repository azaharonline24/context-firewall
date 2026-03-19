import sys
sys.path.insert(0, '.')

from context_firewall.stages.dedupe import deduplicate_chunks

def test_dedupe_exact():
    chunks = [
        {"text": "hello world", "timestamp": 1, "source_id": "a"},
        {"text": "foo bar", "timestamp": 2, "source_id": "b"},
        {"text": "hello world", "timestamp": 3, "source_id": "c"},
        {"text": "baz", "timestamp": 4, "source_id": "d"},
    ]
    result = deduplicate_chunks(chunks)
    assert result == [
        {"text": "hello world", "timestamp": 1, "source_id": "a"},
        {"text": "foo bar", "timestamp": 2, "source_id": "b"},
        {"text": "baz", "timestamp": 4, "source_id": "d"},
    ]

def test_dedupe_empty():
    assert deduplicate_chunks([]) == []

def test_dedupe_no_dupes():
    chunks = [{"text": "a", "timestamp": 1}, {"text": "b", "timestamp": 2}]
    assert deduplicate_chunks(chunks) == chunks

def test_dedupe_all_same():
    chunks = [{"text": "same", "timestamp": 1}, {"text": "same", "timestamp": 2}]
    assert deduplicate_chunks(chunks) == [{"text": "same", "timestamp": 1}]

def test_dedupe_preserves_other_fields():
    chunks = [
        {"text": "hello", "id": 1, "extra": "x"},
        {"text": "world", "id": 2, "extra": "y"},
        {"text": "hello", "id": 3, "extra": "z"},
    ]
    result = deduplicate_chunks(chunks)
    assert len(result) == 2
    assert result[0]["text"] == "hello"
    assert result[0]["id"] == 1
    assert result[0]["extra"] == "x"
    assert result[1]["text"] == "world"
    assert result[1]["id"] == 2
    assert result[1]["extra"] == "y"
