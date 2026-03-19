import sys
sys.path.insert(0, '.')

from context_firewall.stages.dedupe import deduplicate_chunks

def test_dedupe_exact():
    chunks = ["hello world", "foo bar", "hello world", "baz"]
    result = deduplicate_chunks(chunks)
    assert result == ["hello world", "foo bar", "baz"]

def test_dedupe_empty():
    assert deduplicate_chunks([]) == []

def test_dedupe_no_dupes():
    chunks = ["a", "b", "c"]
    assert deduplicate_chunks(chunks) == chunks

def test_dedupe_all_same():
    chunks = ["same", "same", "same"]
    assert deduplicate_chunks(chunks) == ["same"]
