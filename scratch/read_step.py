import json

with open(r'C:\Users\user\.gemini\antigravity\brain\871a67c2-16ed-4a6f-9d97-5ad0c6bf235a\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        step = obj.get('step_index')
        if step in [5258, 5260, 5270, 5275, 5280, 5290]:
            print(f"=== STEP {step} ===")
            print(obj.get('content', '')[:1000])
