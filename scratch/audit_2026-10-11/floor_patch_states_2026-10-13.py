"""One-off edit (2026-10-13) of tools/floor_patch.py and tools/install_variant.py: writing puts every chance of a
wandering shop in the state the live rows ask for (the value of its row, or the value of the game), whatever the
game holds there, so a row dropped or changed since the last install no longer blocks the tool or stays written.
Run once; kept as the record of the edit.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, 'tools', 'floor_patch.py')
INSTALL = os.path.join(ROOT, 'tools', 'install_variant.py')
Q = '"' * 3

NEW = f'''def shop_places():
    {Q}{{(dungeon, entry): [offset in the parameter file]}} of every field a row of this table may write: the chances of
    the wandering shops of every zone of every floor. Whatever the game holds at those places, the rest of the file
    must be the file kept in backups/.{Q}
    found = {{}}
    for dungeon, entry, block in zone_blocks().values():
        found.setdefault((dungeon, entry), []).extend(block + offset for offset in FIELDS.values())
    return found


def state_of(wanted):
    {Q}({{dungeon: 'game' | 'variant' | 'other'}}, problems): what each pack of the game holds at the places a row of this
    table may write, against the values of the game and against the rows given. 'other': a value neither of them asks
    for, left by an older build or by a row since changed or dropped; writing puts it right. A pack whose parameter
    files differ from those of backups/ anywhere else is a problem: not the game this mod was made for, and nothing
    is written.{Q}
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    asked = {{(p['dungeon'], p['entry'], p['at']): p['new'] for p in wanted}}
    states, problems, by_dungeon = {{}}, [], {{}}
    for (dungeon, entry), places in shop_places().items():
        by_dungeon.setdefault(dungeon, []).append((entry, places))
    with zipfile.ZipFile(floor_data.FLOOR_ZIP) as archive:
        for dungeon, entries in sorted(by_dungeon.items()):
            path = os.path.join(mod_config.game_dir(), relative(dungeon))
            if not os.path.exists(path) or os.path.getsize(path) != index[dungeon]['size']:
                problems.append(f'{{relative(dungeon)}}: missing, or not the size of the game this mod was made for')
                continue
            kinds = set()
            with open(path, 'rb') as f:
                for entry, places in sorted(entries):
                    original = bytearray(archive.read(f'{{dungeon}}/{{entry}}'))
                    f.seek(index[dungeon]['entries'][entry])
                    held = bytearray(f.read(len(original)))
                    for at in places:
                        now, game = bytes(held[at:at + 4]), bytes(original[at:at + 4])
                        want = asked.get((dungeon, entry, at), game)
                        kinds.add('variant' if now == want and want != game else 'game' if now == game else 'other')
                        held[at:at + 4] = game
                    if held != original:
                        problems.append(f'{{relative(dungeon)}} {{entry}}: not the file of the game this mod was made for')
            states[dungeon] = 'other' if 'other' in kinds else 'variant' if 'variant' in kinds else 'game'
    return states, problems


def write(wanted):
    {Q}Puts every place a row of this table may write in the state the rows given ask for: the value of the row where
    one is given, the value of the game everywhere else. So a row that was dropped, or whose value changed since the
    last install, is put right by the next one. Nothing is written when a pack has a problem. Returns the packs and
    the places that changed.{Q}
    states, problems = state_of(wanted)
    if problems:
        raise Refused('; '.join(problems))
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    asked = {{(p['dungeon'], p['entry'], p['at']): p['new'] for p in wanted}}
    packs, changed = set(), 0
    with zipfile.ZipFile(floor_data.FLOOR_ZIP) as archive:
        for (dungeon, entry), places in sorted(shop_places().items()):
            original = archive.read(f'{{dungeon}}/{{entry}}')
            base = index[dungeon]['entries'][entry]
            with open(os.path.join(mod_config.game_dir(), relative(dungeon)), 'r+b') as f:
                for at in places:
                    want = asked.get((dungeon, entry, at), bytes(original[at:at + 4]))
                    f.seek(base + at)
                    if f.read(4) != want:
                        f.seek(base + at)
                        f.write(want)
                        packs.add(dungeon)
                        changed += 1
    return len(packs), changed


def apply():
    {Q}The live rows written; every other place of the table at the value of the game.{Q}
    wanted = pokes()
    packs, changed = write(wanted)
    return packs, len(wanted), changed


def restore():
    {Q}The values of the game at every place a row of this table may write.{Q}
    packs, changed = write([])
    return packs, changed, changed


'''
TOOL_EDITS = [
    ("""            packs, count = apply() if mode == 'apply' else restore()
            print(f"Floors: {count} values {'of the variant written' if mode == 'apply' else 'of the game put back'} in "
                  f'{packs} packs of {DUNGEON}')""",
     """            packs, count, changed = apply() if mode == 'apply' else restore()
            print(f"Floors: {count} values {'of the variant held' if mode == 'apply' else 'of the game put back'}; "
                  f'{changed} places written in {packs} packs of {DUNGEON}')"""),
    ("""            print(f'{len(wanted)} rows in {len(states)} packs: ' + ', '.join(f'{k} {v}' for k, v in sorted(states.items())))""",
     """            print(f'{len(wanted)} rows; {len(states)} packs: ' + ', '.join(f'{k} {v}' for k, v in sorted(states.items())))"""),
    ("""A row: Record is the zone""",
     """Writing puts every chance of a wandering shop of every zone in the state the live rows ask for: the value of its row,
or the value of the game where no live row names it. A row dropped or changed since the last install is therefore put
right by the next one, with no record kept of what was written before.

A row: Record is the zone"""),
]
INSTALL_EDIT = ("""        packs, count = floor_patch.apply() if variant == 'balance' else floor_patch.restore()
    except floor_patch.Refused as reason:
        return [f'    Floors: REFUSED, nothing written: {reason}']
    what = 'values of the variant written' if variant == 'balance' else 'values of the game'
    return [f'    Floors: {count} {what} in {packs} packs of the dungeons']""",
                """        packs, count, changed = floor_patch.apply() if variant == 'balance' else floor_patch.restore()
    except floor_patch.Refused as reason:
        return [f'    Floors: REFUSED, nothing written: {reason}']
    what = f'{count} values of the variant held' if variant == 'balance' else 'the values of the game'
    return [f'    Floors: {what}; {changed} places written in {packs} packs of the dungeons']""")


def main():
    with open(TOOL, encoding='utf-8') as f:
        text = f.read()
    a, b = text.index('def state_of(wanted):'), text.index('def main():')
    text = text[:a] + NEW + text[b:]
    for old, new in TOOL_EDITS:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    with open(TOOL, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    with open(INSTALL, encoding='utf-8') as f:
        text = f.read()
    assert text.count(INSTALL_EDIT[0]) == 1
    with open(INSTALL, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text.replace(*INSTALL_EDIT))
    print('floor_patch rewritten')


if __name__ == '__main__':
    main()
