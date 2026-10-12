import os, time

now = time.time()
print("=== RECENT CONVERSATIONS IN BRAIN ===")
brain_dir = r'C:\Users\user\.gemini\antigravity\brain'
if os.path.exists(brain_dir):
    entries = []
    for entry in os.listdir(brain_dir):
        p = os.path.join(brain_dir, entry)
        if os.path.isdir(p):
            mtime = os.path.getmtime(p)
            entries.append((mtime, entry))
    entries.sort(reverse=True)
    for mtime, entry in entries[:10]:
        t_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        print(f"{t_str} | {entry}")

print("\n=== RECENT FILES IN REPO (last 3 hours) ===")
repo_dir = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2'
recent_files = []
for root, dirs, files in os.walk(repo_dir):
    if '.git' in root or '__pycache__' in root:
        continue
    for f in files:
        p = os.path.join(root, f)
        try:
            mtime = os.path.getmtime(p)
            if now - mtime < 3 * 3600:
                recent_files.append((mtime, p))
        except Exception:
            pass
recent_files.sort(reverse=True)
for mtime, p in recent_files[:25]:
    t_str = time.strftime("%H:%M:%S", time.localtime(mtime))
    print(f"{t_str} | {p}")
