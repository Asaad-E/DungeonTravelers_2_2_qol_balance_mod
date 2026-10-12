with open('mod_project/docs/FORMULAS.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('"All stats +N"')
print(text[max(0, idx - 400):min(len(text), idx + 600)])
