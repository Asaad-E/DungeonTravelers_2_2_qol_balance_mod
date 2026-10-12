import json

print("=== SEARCHING TRANSCRIPT FOR SKILL FORMAT AGREEMENTS ===")
with open(r'C:\Users\user\.gemini\antigravity\brain\2ad15c50-899d-428e-a003-82de381500ee\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if any(k in line.lower() for k in ['clean_raging_smash', 'mockup_5class', 'recuadro', 'acordado', 'formato']):
            try:
                obj = json.loads(line)
                src = obj.get('source')
                idx = obj.get('step_index')
                content = str(obj.get('content', ''))
                if any(w in content for w in ['Raging Smash', 'mockup', 'Línea 1', 'Line 1', 'TP Cost']):
                    print(f"Step {idx} [{src}]:")
                    for cl in content.split('\n')[:8]:
                        print("  ", cl[:100])
                    print("-" * 50)
            except Exception:
                pass
