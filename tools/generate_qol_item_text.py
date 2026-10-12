"""
QoL item text: proposes the description of each item for the QoL variant and keeps it in a
workbook that is edited by hand.

    python tools/generate_qol_item_text.py

Workbook: data_tables/qol_item_text.xlsx
  * QoL_Desc is the text the build uses. Put "yes" in Edited to keep your wording.
  * Rule set by the user: original text + (data). The game's sentence, joke included, stays; what the
    item does is added in a final parenthesis when the sentence does not already say it:
        "Sandwich filled with soft, fluffy eggs."  ->  "Sandwich filled with soft, fluffy eggs. (HP/TP +10, cures 1 ailment)"
  * Where the vanilla text gives a vague size, the amount replaces the word and nothing is appended:
        "Restore an ally's HP (medium)."  ->  "Restore an ally's HP (+250)."      A text never carries both.
  * The data is what the item does when used on an ally (its first two effect pairs). Items with an
    effect that is not decoded, and items whose text would pass the 70 characters of the battle bar, stay as written and
    say why in the Note column. The same description is shown in battle, so it stays one line.
"""
import os
import re
import sys
import collections
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from pck_handler import PckArchive, ItemHelper
from text_checks import ITEM_RESTORE, ITEM_ALLY_PAIRS, item_pairs, item_data, check_item_text
from shortened_text import ITEM_SENTENCES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_PATH = os.path.join(BASE_DIR, 'backups', 'ItemData.pck')
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
PREVIOUS_PATH = os.path.join(TABLES_DIR, 'items.xlsx')
OUTPUT_PATH = os.path.join(TABLES_DIR, 'qol_item_text.xlsx')

import rules
MAX_LINE = rules.setting('battle_line_width')     # an item line is also the battle bar: 70, measured on screen
HEADERS = ['Filename', 'Item_Name', 'Vanilla_Desc', 'QoL_Desc', 'Edited', 'Effect_Pairs', 'Previous_Mod_Desc', 'Note']
VAGUE_RE = re.compile(r"Restore (?P<what>an ally's HP|an ally's TP|all allies' HP) \((?:small|medium|large)\)")


def propose(b, desc, name=''):
    """Returns (text, note)."""
    effect_type, value = item_pairs(b)[0]
    m = VAGUE_RE.search(desc)
    if m and ITEM_RESTORE[m.group('what')] == effect_type and value == int(value):
        return desc[:m.start()] + f"Restore {m.group('what')} (+{int(value)})" + desc[m.end():], ''
    if all(t == -1 for t, _ in item_pairs(b)[:ITEM_ALLY_PAIRS]):
        return desc, ''
    every, missing = item_data(b, desc)
    if every is None:
        return desc, 'has an effect that is not decoded'
    if not missing:
        return desc, ''
    text = f"{desc} ({', '.join(missing)})"
    if len(text) <= MAX_LINE:
        return text, ''
    if name in ITEM_SENTENCES:      # one line: the original is made shorter (shortened_text.py)
        text = f"{ITEM_SENTENCES[name]} ({', '.join(missing)})"
        if len(text) <= MAX_LINE:
            return text, 'original sentence shortened to fit'
    return desc, f"no room for ({', '.join(missing)}): {len(text)} characters"


def load_column(path, sheet, key, value, only_edited=False):
    if not os.path.exists(path):
        return {}
    wb = openpyxl.load_workbook(path)
    if sheet not in wb.sheetnames:
        return {}
    ws = wb[sheet]
    header = [c.value for c in ws[1]]
    if key not in header or value not in header:
        return {}
    k, v = header.index(key), header.index(value)
    e = header.index('Edited') if only_edited else None
    return {r[k]: r[v] for r in ws.iter_rows(min_row=2, values_only=True)
            if r[k] and (e is None or str(r[e] or '').strip().lower() == 'yes')}


def build_rows():
    edited = load_column(OUTPUT_PATH, 'Items', 'Filename', 'QoL_Desc', only_edited=True)
    previous = {}
    if os.path.exists(PREVIOUS_PATH):
        wb = openpyxl.load_workbook(PREVIOUS_PATH, read_only=True)
        ws = wb[wb.sheetnames[0]]
        header = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        if 'Filename' in header and 'Modded_Desc' in header:
            f, d = header.index('Filename'), header.index('Modded_Desc')
            previous = {r[f]: r[d] for r in ws.iter_rows(min_row=2, values_only=True) if r[f]}
    rows, stats = [], collections.Counter()
    for fn, b in PckArchive(BACKUP_PATH).files:
        item = ItemHelper.read_item(b)
        desc, note = (edited[fn], '') if fn in edited else propose(b, item['desc'], item['name'])
        problems, _ = check_item_text(b, desc, item['desc'], ITEM_SENTENCES.get(item['name']))
        if problems or '\n' in desc or (len(desc) > MAX_LINE and desc != item['desc']):
            raise SystemExit(f"{fn} ({item['name']}): '{desc}' {problems or 'breaks the one-line limit'}")
        desc.encode('latin-1')
        stats['edited by hand' if fn in edited else
              'amount in place of the vague size' if VAGUE_RE.search(item['desc']) and desc != item['desc'] else
              'shortened original + (data)' if note.startswith('original sentence shortened') else
              'original + (data)' if desc != item['desc'] else
              'kept: ' + note.split(':')[0].split(' for (')[0] if note else 'kept: nothing to add'] += 1
        pairs = ' | '.join(', '.join(f'{t}:{v:g}' for t, v in side if t != -1)
                           for side in (item_pairs(b)[:ITEM_ALLY_PAIRS], item_pairs(b)[ITEM_ALLY_PAIRS:]))
        rows.append([fn, item['name'], item['desc'], desc, 'yes' if fn in edited else '', pairs, previous.get(fn, ''), note])
    return rows, stats


def main():
    rows, stats = build_rows()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Items'
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='305496')
    ws.freeze_panes = 'C2'
    for i, width in enumerate([20, 28, 80, 80, 8, 36, 80, 60], 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    how = wb.create_sheet('How to edit')
    for line in [
        'QoL_Desc is the text the build writes into ItemData.pck. One line, 70 characters at most (the battle bar).',
        'To word an item yourself: change QoL_Desc and put "yes" in Edited. The generator keeps that row.',
        'The original sentence must stay. Data goes in a final parenthesis: "(HP/TP +10, cures 1 ailment)". '
        'The build checks every piece of it against the binary and rejects a changed sentence.',
        'An amount in place of a vague size is written as "Restore an ally\'s HP (+250)."',
        'Effect_Pairs lists the (type:value) pairs: used on an ally | used on an enemy. Types read so far: 0 HP, 1 TP, '
        '2 HP and TP, 3 party HP, 4 party TP, 6 cure one ailment, 7 cure all ailments, 8 revive (% HP), 9 light '
        '(x5 steps), 10 leave the dungeon, 16 sleep chance, 22 cancel Shadow Sew, 23 restore lowered stats, 24 skill points.',
    ]:
        how.append([line])
    how.column_dimensions['A'].width = 130
    wb.save(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}: {len(rows)} items")
    for key in sorted(stats):
        print(f"    {stats[key]:4d}  {key}")


if __name__ == '__main__':
    sys.exit(main())
