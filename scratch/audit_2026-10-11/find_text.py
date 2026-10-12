"""Every text box of the lessons, the library and the string table that holds a word: find_text.py WORD [WORD ...]"""
import os
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from pck_handler import PckArchive                          # noqa: E402

BOX = re.compile(rb'[\x20-\x7e\n]{6,}\x00')


def main():
    words = [w.lower() for w in sys.argv[1:]]
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    for pack in ('Lesson.pck', 'Teaching.pck', 'StringData.pck', 'KeyHelpData.pck', 'IntroductionData.pck'):
        path = os.path.join(PROJECT, 'backups', pack)
        if not os.path.exists(path):
            continue
        for name, blob in PckArchive(path).files:
            for m in BOX.finditer(bytes(blob)):
                text = m.group()[:-1].decode('latin-1')
                if any(w in text.lower() for w in words):
                    print(f'{pack} / {name}: {text!r}')


if __name__ == '__main__':
    main()
