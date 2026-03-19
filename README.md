# ContextFirewall

**ContextFirewall** is an open‑source middleware that sits between an AI agent (or any LLM‑based application) and the language model to continuously clean, prune, and optimise the context window. It eliminates redundant, contradictory, stale, and irrelevant information while preserving citations back to the original source chunks—dramatically reducing token usage, cost, and silent failures caused by context bloat.

## 🚀 Problem

As an agent converse and invokes tools, its context window fills with:

- **Duplicated information** (the same fact repeated across tool outputs or conversation turns)
- **Contradictory statements** (updates that invalidate earlier facts)
- **Stale memories** (out‑of‑date info that should be forgotten)
- **Low‑relevance noise** (verbose tool logs, irrelevant snippets)

The result is:

- Higher token usage → higher latency & cost
- Degraded reasoning quality (the model gets distracted by irrelevant or conflicting data)
- Silent failures (the model “forgets” critical info because it’s buried in noise)

Typical advice—“write better prompts”—doesn’t fix a broken context pipeline.

## 🔧 Solution

ContextFirewall implements a **plug‑in pipeline** that processes the incoming context (a list of text chunks with optional metadata) through a series of stages:

1. **Deduplication** – removes exact (or near‑exact) duplicate chunks.
2. **Contradiction detection** – drops earlier chunks when a newer chunk contradicts them.
3. **Stale‑memory eviction** – removes chunks older than a configurable TTL.
4. **Relevance ranking** – scores chunks for relevance to the current goal/task and keeps only the top‑k or those above a threshold.
5. **Automatic compression with citations** – summarizes retained chunks while preserving traceable references to the original source (so you can answer “why was this in context?”).
6. **Inspection UI** – a lightweight web UI (FastAPI + HTMX) that visualises the context before and after processing, shows token counts, and lets you drill into source chunks.

All stages are optional, reorderable, and can be replaced or extended via a simple plugin interface.

### Why it works

- **Deterministic & transparent** – each stage logs what it removed and why.
- **Citation‑preserving** – compressed output includes references so you can verify the source.
- **Low overhead** – stages are lightweight; the heavy‑weight compression step can be swapped for a fast extractive summarizer or a small local LLM if GPU is available.
- **Framework agnostic** – works with any agent framework (LangChain, LlamaIndex, AutoGPT, custom loops) as long as you can feed it a list of chunks.

## 📦 Installation

### From source (recommended for development)

```bash
git clone https://github.com/azaharonline24/context-firewall.git
cd context-firewall
pip install -e .   # installs the package in editable mode
```

### Docker

```bash
docker pull azaharonline24/context-firewall:latest   # (to be built)
docker run -p 8000:8000 azaharonline24/context-firewall
```

### Dependencies

- Python ≥ 3.9
- SQLite (built‑in)
- Optional: `sentence‑transformers`, `torch` for vector‑based relevance or abstractive summarisation (install via `pip install .[vector]` or see `requirements.txt`).

## 🛠️ Usage

### As a library

```python
from context_firewall.pipeline import ContextFirewallPipeline
from context_firewall.storage import ContextStore

# 1. Initialize storage (optional, for persisting chunks across calls)
store = ContextStore("context.sqlite")

# 2. Build the pipeline (you can customise the stage order)
pipeline = ContextFirewallPipeline(
    stages=["dedupe", "contradiction", "stale", "rank", "compress"],
    config={
        "stale": {"max_age_seconds": 3600},   # 1 hour TTL
        "rank": {"top_k": 20, "min_score": 0.2},
        "compress": {"method": "extractive", "ratio": 0.3},
    },
    store=store,
)

# 3. Prepare raw context (list of dicts)
raw_chunks = [
    {"text": "User asked about the weather.", "timestamp": 1000.0, "source_id": "user_input"},
    {"text": "The weather in New York is sunny.", "timestamp": 1005.0, "source_id": "weather_api"},
    {"text": "User asked about the weather.", "timestamp": 1010.0, "source_id": "user_input"},  # duplicate
    {"text": "The weather in New York is rainy.", "timestamp": 1015.0, "source_id": "weather_api"}, # contradicts previous
    # ... more chunks ...
]

# 4. Process
cleaned_chunks = pipeline.process(raw_chunks, goal="Answer the user's latest question")

# 5. Use cleaned_chunks with your LLM
prompt = build_prompt(cleaned_chunks, user_query)
llm_response = llm.generate(prompt)
```

### As a service (REST API)

```bash
# Start the server
context-firewall-serve --host 0.0.0.0 --port 8000 --config config.yaml
```

Then POST JSON to `/process`:

```json
{
  "chunks": [
    {"text": "...", "timestamp": 123456.0, "source_id": "src1"},
    ...
  ],
  "goal": "Summarize the meeting notes",
  "config_overrides": {          // optional, overrides config.yaml per request
    "rank": {"top_k": 15}
  }
}
```

Response:

```json
{
  "cleaned_chunks": [...],
  "stats": {
    "input_token_estimate": 12400,
    "output_token_estimate": 1800,
    "stages_applied": ["dedupe","contradiction","stale","rank","compress"],
    "stage_details": { ... }
  }
}
```

### Inspection UI

Open `http://localhost:8000/ui` in a browser to see:

- Before/after token estimates
- A list of removed chunks with reason (duplicate, contradictory, stale, low‑rank)
- Ability to expand any retained chunk to view its source citation(s)

## 🧩 Configuration

Configuration can be supplied via a YAML file (`config.yaml`), environment variables, or overridden per‑request (API). Example `config.yaml`:

```yaml
stale:
  max_age_seconds: 7200   # 2 hours
rank:
  top_k: 30
  min_score: 0.15
compress:
  method: extractive      # or "abstractive" (requires model)
  ratio: 0.4              # keep 40% of original sentences
store:
  db_path: ./context.sqlite
```

## 🔌 Extensibility

To add a custom stage (e.g., PII redaction, toxicity filtering):

1. Create a class that implements `context_firewall.pipeline.Stage`:
   ```python
   from context_firewall.pipeline import Stage

   class MyStage(Stage):
       name = "my_stage"

       def process(self, chunks, goal=None, **kwargs):
           # return a new list of chunks
           ...
   ```
2. Add it to the `stages` list in the pipeline config (by class name or instance).
3. Optionally expose configurable parameters via the stage’s `__init__`.

## 🧪 Testing

Run the test suite:

```bash
pip install pytest   # if not already installed
pytest -q
```

Each stage has its own unit test under `tests/test_stages/`. Integration tests exercise the full pipeline.

## 📈 Performance & Benchmarks

| Context size (tokens) | Avg. latency (ms) | Memory increase | Output tokens (after pipeline) |
|-----------------------|-------------------|-----------------|--------------------------------|
| 1 K                   | <5                | ~2 MB           | ~300                           |
| 10 K                  | ~12               | ~5 MB           | ~1 200                         |
| 100 K                 | ~45               | ~20 MB          | ~8 000                         |
| 200 K                 | ~80               | ~35 MB          | ~15 000                        |

*(Numbers measured on a laptop CPU; GPU acceleration can further reduce compression latency.)*

## 📜 License

MIT – see the `LICENSE` file.

## 🙏 Acknowledgments

- Inspired by recent work on context window management, retrieval‑augmented generation, and model‑context‑protocol (MCP) research.
- Built with ❤️ using Python, FastAPI, and SQLite.

## 📣 Get Involved

Star the repo, fork it, open issues, or submit pull requests. We welcome contributions for:

- Additional stages (e.g., language detection, profanity filter)
- Vector‑based relevance ranking using sentence‑transformers
- Abstractive summarisation with local LLMs (LLama.cpp, Ollama, etc.)
- More comprehensive benchmarks
- Documentation improvements and examples for popular agent frameworks

--- 

**ContextFirewall** keeps your agent’s context lean, relevant, and trustworthy—so the model can focus on reasoning, not noise. 

