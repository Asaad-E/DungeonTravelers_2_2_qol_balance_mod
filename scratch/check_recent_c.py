import json

with open(r'C:\Users\user\.gemini\antigravity\brain\871a67c2-16ed-4a6f-9d97-5ad0c6bf235a\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        content = obj.get('content', '')
        # look for recent messages mentioning joint or c
        step = obj.get('step_index')
        if step and step > 4700:
            if 'joint' in content.lower() or 'punto c' in content.lower() or 'cost' in content.lower():
                print(f"--- STEP {step} ({obj.get('source')}) ---")
                for subline in content.split('\n'):
                    if any(k in subline.lower() for k in ['joint', 'cost', 'punto c', 'divine punishment', 'rush zanber', 'tp']):
                        print(subline[:120])
