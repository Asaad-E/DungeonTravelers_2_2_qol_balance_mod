import json

with open(r'C:\Users\user\.gemini\antigravity\brain\871a67c2-16ed-4a6f-9d97-5ad0c6bf235a\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        content = obj.get('content', '')
        if any(term in content.lower() for term in ['punto c', 'point c', 'joint skill', 'coste de joint', 'costos de joint']):
            step = obj.get('step_index')
            role = obj.get('source')
            # Print first 250 chars
            preview = content.replace('\n', ' ')[:200]
            print(f"Step {step} ({role}): {preview}")
