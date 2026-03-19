from typing import List, Dict, Any, Callable, Optional

class ContextFirewallPipeline:
    def __init__(self, stages: List[Callable], config: Optional[Dict[str, Any]] = None):
        """
        stages: list of callables, each callable should accept
                (chunks: List[Dict], goal: Optional[str] = None, **stage_kwargs)
                and return a List[Dict].
        config: optional dict mapping stage name (or index) to config dict.
        """
        self.stages = stages
        self.config = config or {}

    def process(self, chunks: List[Dict[str, Any]], goal: Optional[str] = None) -> List[Dict[str, Any]]:
        current = chunks
        for idx, stage in enumerate(self.stages):
            # Determine stage config: if config is dict with stage name or index
            stage_config = {}
            if isinstance(self.config, dict):
                # Try to get by stage name if callable has __name__
                name = getattr(stage, '__name__', f'stage_{idx}')
                stage_config = self.config.get(name, self.config.get(idx, {}))
            # Call stage with chunks, goal, and stage_config as kwargs
            current = stage(chunks=current, goal=goal, **stage_config)
        return current
