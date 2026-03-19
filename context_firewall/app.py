from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .storage import ContextStore
from .pipeline import ContextFirewallPipeline
from .stages.dedupe import deduplicate_chunks
from .stages.contradiction import detect_contradictions
from .stages.stale import evict_stale
from .stages.rank import rank_chunks
from .stages.compress import compress_chunks

app = FastAPI(title="ContextFirewall", version="0.1.0")

# Default stage order and config
DEFAULT_STAGES = [
    ("dedupe", deduplicate_chunks, {}),
    ("contradiction", detect_contradictions, {}),
    ("stale", evict_stale, {"max_age_seconds": 3600.0}),  # 1 hour TTL
    ("rank", rank_chunks, {"top_k": 20, "min_score": 0.1}),
    ("compress", compress_chunks, {"ratio": 0.5}),
]

def make_pipeline(stage_configs=None, store: Optional[ContextStore] = None):
    """
    Build a ContextFirewallPipeline with the default stages.
    stage_configs: dict mapping stage name to config overrides (dict).
    store: optional ContextStore instance for persistence.
    Returns (pipeline, store).
    """
    stage_configs = stage_configs or {}
    stages = []
    for name, func, default_cfg in DEFAULT_STAGES:
        cfg = dict(default_cfg)
        if name in stage_configs:
            cfg.update(stage_configs[name])
        # Wrap the function to match pipeline signature: (chunks, goal=None, **cfg)
        def wrapper(chunks, goal=None, **kw):
            # Merge default cfg with any passed kw (kw should be empty from pipeline)
            final_cfg = dict(cfg)
            final_cfg.update(kw)
            return func(chunks, goal=goal, **final_cfg)
        stages.append(wrapper)
    pipeline = ContextFirewallPipeline(stages)
    return pipeline, store

# Initialize storage (optional, can be None)
# Using a relative path; in production you might want to configure via env var.
try:
    store = ContextStore("context.sqlite")
except Exception:
    store = None  # fallback to no persistence
pipeline, _ = make_pipeline(store=store)

class ProcessRequest(BaseModel):
    chunks: List[Dict[str, Any]]
    goal: Optional[str] = None
    config: Optional[Dict[str, Any]] = None  # per-stage config overrides

class ProcessResponse(BaseModel):
    cleaned_chunks: List[Dict[str, Any]]
    stats: Dict[str, Any]

@app.post("/process", response_model=ProcessResponse)
async def process_context(request: ProcessRequest):
    try:
        # If config provided, we need to rebuild pipeline with those overrides
        if request.config:
            pipeline, _ = make_pipeline(stage_configs=request.config, store=store)
        else:
            pipeline, _ = make_pipeline(store=store)
        cleaned = pipeline.process(request.chunks, goal=request.goal)
        # Rough token estimate: split by whitespace
        def estimate_tokens(text):
            return len(str(text).split())
        input_tokens = sum(estimate_tokens(c.get("text", "")) for c in request.chunks)
        output_tokens = sum(estimate_tokens(c.get("text", "")) for c in cleaned)
        stats = {
            "input_chunk_count": len(request.chunks),
            "output_chunk_count": len(cleaned),
            "input_token_estimate": input_tokens,
            "output_token_estimate": output_tokens,
            "stages_applied": [s.__name__ if hasattr(s, '__name__') else str(s) for s in pipeline.stages],
        }
        return ProcessResponse(cleaned_chunks=cleaned, stats=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: simple root endpoint
@app.get("/")
async def root():
    return {"message": "ContextFirewall API is running. See /docs for Swagger UI."}

# To run: uvicorn context_firewall.app:app --host 0.0.0.0 --port 8000
