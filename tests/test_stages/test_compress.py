import sys
sys.path.insert(0, '.')

from context_firewall.stages.compress import compress_chunks

def test_compress_basic():
    chunks = [
        {"text": "The quick brown fox jumps over the lazy dog. It is a sunny day.", "source_id": "doc1"},
        {"text": "Python is a great programming language. Many developers love it.", "source_id": "doc2"},
    ]
    # compress to about 50% of sentences
    result = compress_chunks(chunks, ratio=0.5)
    assert len(result) == 2
    for r in result:
        assert 'text' in r
        assert isinstance(r['text'], str)
        # Ensure original metadata preserved
        assert 'source_id' in r
        # Ensure text is not empty
        assert len(r['text'].strip()) > 0

def test_compress_ratio_one():
    chunks = [{"text": "One sentence.", "source_id": "x"}]
    result = compress_chunks(chunks, ratio=1.0)
    assert len(result) == 1
    # With ratio 1.0 we expect same text (maybe same sentences)
    assert result[0]['text'] == chunks[0]['text']

def test_compress_ratio_zero():
    chunks = [{"text": "Some text.", "source_id": "y"}]
    result = compress_chunks(chunks, ratio=0.0)
    # Expect empty string or maybe we keep at least one sentence? We'll decide to return empty string.
    assert len(result) == 1
    assert result[0]['text'].strip() == ''

def test_compres_empty():
    assert compress_chunks([]) == []
