import sys
sys.path.insert(0, '.')

from context_firewall.pipeline import ContextFirewallPipeline

def test_pipeline_runs_stages():
    # Simple dummy stages that just add a marker
    def stage1(chunks, goal=None, **kwargs):
        for c in chunks:
            c['stage1'] = True
        return chunks
    def stage2(chunks, goal=None, **kwargs):
        for c in chunks:
            c['stage2'] = True
        return chunks

    pipeline = ContextFirewallPipeline(stages=[stage1, stage2])
    chunks = [{"text": "hello"}]
    result = pipeline.process(chunks, goal="test")
    assert len(result) == 1
    assert result[0].get('stage1') is True
    assert result[0].get('stage2') is True

def test_pipeline_preserves_order():
    def stage_a(chunks, goal=None, **kwargs):
        for c in chunks:
            c['a'] = len(chunks)  # just some marker
        return chunks
    def stage_b(chunks, goal=None, **kwargs):
        for c in chunks:
            c['b'] = True
        return chunks
    pipeline = ContextFirewallPipeline(stages=[stage_a, stage_b])
    chunks = [{"text": "one"}, {"text": "two"}]
    result = pipeline.process(chunks)
    assert result[0]['a'] == 2
    assert result[0]['b'] is True
    assert result[1]['a'] == 2
    assert result[1]['b'] is True

def test_pipeline_with_config():
    def stage_conf(chunks, goal=None, **kwargs):
        # kwargs contains config for this stage if any
        config = kwargs.get('config', {})
        factor = config.get('factor', 1)
        for c in chunks:
            c['value'] = len(c.get('text', '')) * factor
        return chunks
    pipeline = ContextFirewallPipeline(stages=[stage_conf])
    chunks = [{"text": "hi"}]
    result = pipeline.process(chunks, config={"stage_conf": {"factor": 2}})
    assert result[0]['value'] == 2 * len("hi")
