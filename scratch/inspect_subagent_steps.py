import json

path = r'C:\Users\user\.gemini\antigravity\brain\47ae34aa-cf91-420c-b3de-bf16ac651c5e\.system_generated\logs\transcript.jsonl'
with open(path, encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        if d.get('source') == 'MODEL' and d.get('type') == 'PLANNER_RESPONSE':
            thinking = d.get('thinking', '')
            step = d.get('step_index')
            first_sent = thinking.split('\n')[0][:120] if thinking else ''
            print(f"Step {step}: {first_sent}")
