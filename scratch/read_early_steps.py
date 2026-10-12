import json

with open(r'C:\Users\user\.gemini\antigravity\brain\2ad15c50-899d-428e-a003-82de381500ee\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get('step_index', 0)
        if 160 <= idx <= 235:
            if obj.get('source') == 'USER_EXPLICIT':
                print(f"User Step {idx}: {obj.get('content')}\n")
