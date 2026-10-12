import json

with open(r'C:\Users\user\.gemini\antigravity\brain\2ad15c50-899d-428e-a003-82de381500ee\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        idx = data.get('step_index')
        if idx in [2768, 2769, 2770, 2771, 2772]:
            print(f"=== MODEL STEP {idx} ===")
            txt = data.get('content', '')
            print(txt.encode('ascii', errors='replace').decode('ascii'))
            print("=" * 50)
