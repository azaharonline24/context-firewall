# Context Firewall for AI agents

## Problem
AI agents suffer from context bloat: as conversations and tool traces grow, the context window fills with irrelevant, contradictory, or stale information, leading to degraded reasoning, increased costs, and silent failures. Existing solutions focus on better prompts, but the real issue is broken context pipelines that accumulate garbage.

## Proposed Solution
Build open-source middleware that sits between the model and the application (or agent framework) to continuously clean and optimize the context. It implements:
- Context deduplication (removing redundant information)
- Contradiction detection (flagging or removing conflicting statements)
- Stale-memory eviction (dropping outdated facts based on time or relevance)
- Relevance ranking for tool outputs (scoring and keeping only useful tool results)
- Automatic compression with citations (summarizing chunks while preserving traceability to source)
- Inspection UI ("Why was this in context?") for debugging and trust

The middleware exposes a simple API: it receives raw context (messages, tool outputs, memories) and returns a pruned, compressed, citation-rich context ready for the model.

## Key Decisions
- **Language:** Python (for broad compatibility with agent ecosystems)
- **Architecture:** Plugin‑based pipeline where each stage (dedupe, contradiction, etc.) is a separate module; easy to enable/disable or reorder.
- **Storage:** Lightweight SQLite index for tracking context chunks, timestamps, and source citations; no external dependencies beyond standard library.
- **Compression:** Use extractive summarization (sentence scoring) plus optional abstractive summarization via a small local LLM (e.g., distillation of Phi‑3) if GPU available; fallback to extractive only.
- **Citations:** Each compressed sentence retains a list of source chunk IDs; UI can expand to show original text.
- **Relevance Ranking:** Combine BM25 keyword match, vector similarity (if embeddings enabled), and recency scoring; weights configurable via YAML.
- **UI:** Simple web‑based dashboard (FastAPI + HTMX) visualizing context before/after, token counts, and drill‑down into sources.
- **Extensibility:** Allow custom stages via entry points; users can write their own filters (e.g., PII removal, toxicity scoring).

## File Changes
| File | Change Type | Responsibility |
|------|-------------|----------------|
| `context_firewall/__init__.py` | New | Package init, version |
| `context_firewall/pipeline.py` | New | Main pipeline orchestration, stage management |
| `context_firewall/stages/dedupe.py` | New | Remove duplicate chunks (exact and fuzzy) |
| `context_firewall/stages/contradiction.py` | New | Detect contradictory statements using NLI model |
| `context_firewall/stages/stale.py` | New | Evict old chunks based on TTL or relevance decay |
| `context_firewall/stages/rank.py` | New | Score chunks for relevance to current goal/task |
| `context_firewall/stages/compress.py` | New | Summarize chunks while preserving citations |
| `context_firewall/storage.py` | New | SQLite schema and CRUD for chunks, metadata, citations |
| `context_firewall/api.py` | New | FastAPI endpoints: `/process`, `/stats`, `/ui/*` |
| `context_firewall/config.py` | New | Load YAML config, defaults, environment overrides |
| `tests/test_pipeline.py` | New | Unit tests for pipeline integration |
| `tests/test_stages/*.py` | New | Tests for each stage |
| `docs/` | New | Design doc, API guide, deployment examples |
| `requirements.txt` | New | Dependencies: fastapi, uvicorn, sqlalchemy, sentence-transformers (optional), nltk, torch (optional) |
| `Dockerfile` | New | Containerize for easy deployment |
| `docker-compose.yml` | New | Optional: run with Redis cache for embeddings |
| `cli.py` | New | Command‑line interface for testing and debugging |

## Testing Strategy
- **Unit tests:** Each stage receives predefined input chunks and asserts expected output (e.g., dupe removal, contradiction flagging).
- **Integration tests:** Full pipeline with sample agent conversations (loaded from fixtures) verifies token reduction, preservation of correct information, and citation integrity.
- **Property‑based tests:** Using hypothesis to ensure that output token count never exceeds input and that all retained citations are traceable.
- **Performance benchmarks:** Measure latency and memory usage for context sizes ranging from 1k to 200k tokens.
- **UI tests:** Selenium‑lite (Playwright) scripts to verify inspection UI shows correct before/after views.
- **Edge cases:** Empty context, highly repetitive context, contradictory statements, multilingual text (if embeddings support).
- **CI:** GitHub Actions running on Linux, macOS, Windows; test matrix with/without optional GPU‑dependent packages.

## Approval Request
Please review this design. If it looks good, say “Looks good” or “Go ahead” and I’ll proceed with the initial setup (repo skeleton, core pipeline, and storage).