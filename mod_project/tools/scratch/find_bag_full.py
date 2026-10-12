import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
import re

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

# Search for strings related to inventory full
full_matches = [m.start() for m in re.finditer(rb'(?:bag|inventory|item|cannot carry)[^\x00]{0,40}(?:full|max|limit)[^\x00]*', code, re.IGNORECASE)]
print(f"Inventory full string occurrences: {len(full_matches)}")
for idx in full_matches[:10]:
    s = code[idx:idx+80].split(b'\x00')[0].decode('latin-1', errors='ignore')
    print(f"  0x{idx:06x}: '{s}'")
