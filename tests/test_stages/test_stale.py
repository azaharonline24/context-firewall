import sys
sys.path.insert(0, '.')

from context_firewall.stages.stale import evict_stale

def test_evict_stale_basic():
    now = 1000.0
    chunks = [
        {"text": "old", "timestamp": 500.0},   # 500 sec old
        {"text": "recent", "timestamp": 950.0}, # 50 sec old
        {"text": "very old", "timestamp": 100.0}, # 900 sec old
    ]
    # max_age 300 seconds -> keep only those with timestamp >= now - 300 = 700
    result = evict_stale(chunks, max_age_seconds=300.0, reference_time=now)
    assert len(result) == 1
    assert result[0]["text"] == "recent"

def test_evict_stale_none():
    now = 500.0
    chunks = [
        {"text": "a", "timestamp": 400.0},
        {"text": "b", "timestamp": 450.0},
    ]
    result = evict_stale(chunks, max_age_seconds=200.0, reference_time=now)  # keep >=300
    assert len(result) == 2  # both >=300? Actually 400 and 450 both >=300, yes.

def test_evict_stale_all_old():
    now = 100.0
    chunks = [
        {"text": "old1", "timestamp": 50.0},
        {"text": "old2", "timestamp": 30.0},
    ]
    result = evict_stale(chunks, max_age_seconds=10.0, reference_time=now)  # keep >=90
    assert result == []

def test_evict_stale_no_timestamp():
    # If a chunk lacks timestamp, we could treat as infinitely old? We'll decide to keep it? 
    # For simplicity, we assume all chunks have timestamp; but we can decide to keep those missing.
    chunks = [{"text": "no time"}]
    result = evict_stale(chunks, max_age_seconds=10.0, reference_time=500.0)
    # We'll implement to keep chunks without timestamp (or treat as very old?). Let's decide to keep them.
    assert result == chunks

def test_evict_stale_empty():
    assert evict_stale([], max_age_seconds=100.0, reference_time=0.0) == []
