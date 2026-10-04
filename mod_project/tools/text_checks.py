"""
Checks that every number written in a skill text is the value stored in a binary.

Used by the variant build and by the test suite, so hand-edited wording is free
while the figures stay tied to the data.

Understood notation (the project style guide):
    Label: 80% -> 110% (+3%/Lv, L1-10)       range with the per-level step
    Label: 80% -> 110% (avg +3.33%/Lv)       range of a non-linear table
    Label: 10 -> 14 -> 18 -> 21 -> 24 (L1-5) one value per level
    Label (L1-10): 70 -> 105 -> ... -> 520   one value per level, long form
    Label: 0.85x                             value that does not change
"""
import re
from extract_vanilla import SKILL_LAYOUTS, SLOT_SIZE, LEVELS, i32, read_array, leading_nonzero

NUM = r'[+-]?\d+(?:\.\d+)?'
VALUE = rf'{NUM}[%x]?'
SERIES_RE = re.compile(
    rf'(?P<series>{VALUE}(?: -> {VALUE})*)'
    rf'(?: \((?P<avg>avg )?(?P<step>{NUM})[%x]?/Lv(?:, L1-(?P<lv_step>\d+))?\)| \(L1-(?P<lv_list>\d+)\))?')
SEGMENT_RE = re.compile(r'^(?P<label>[^:]+?)(?: \(L1-(?P<lv>\d+)\))?: (?P<body>.+)$')

AILMENT_LABELS = {
    'Poison': 113, 'Freeze': 114, 'Paralysis': 115, 'Sleep': 116, 'Silence': 117,
    'Stun': 118, 'Instakill': 119, 'Petrify': 120, 'Slow': 122,
}
EFFECT_LABELS = {'HP Absorb': 75, 'TP Absorb': 76, 'Targets': 137, 'Heal Cap': 295}
UNIQUE_VALUES = 0x1C
TOLERANCE = 0.006


def skill_tables(category, b):
    """Per-level tables of one skill entry, cut to its number of levels."""
    if category == 'Unique':
        values = read_array(b, UNIQUE_VALUES)[0]
        return {'levels': 9, 'unique': values[:9], 'ex': values[9:], 'slots': []}
    lay = SKILL_LAYOUTS[category]
    sp = read_array(b, lay['sp'])[0]
    speed = read_array(b, lay['speed'])[0] if 'speed' in lay else []
    levels = leading_nonzero(sp) or leading_nonzero(speed) or 1
    tables = {'levels': levels, 'slots': []}
    for key, name in (('tp', 'tp'), ('turns', 'turns'), ('speed', 'speed'), ('cast', 'cast'), ('arr_0xFC', 'accuracy')):
        if key in lay:
            tables[name] = read_array(b, lay[key])[0][:levels]
    for k in range(i32(b, lay['count'])):
        off = lay['slots'] + k * SLOT_SIZE
        tables['slots'].append((i32(b, off), i32(b, off + 4 + 4 * LEVELS), read_array(b, off + 4)[0][:levels]))
    return tables


def displays(values):
    """Ways a stored table can legitimately be printed: as is, as a percentage, or as 100% + value."""
    return [list(values), [100 * v for v in values], [100 * (1 + v) for v in values]]


def close(a, b):
    return abs(abs(a) - abs(b)) < TOLERANCE


def series_fits(shown, table):
    table = [round(v, 2) for v in table]
    if len(shown) == 1:
        return all(close(shown[0], v) for v in table)
    if len(shown) == len(table) and all(close(s, v) for s, v in zip(shown, table)):
        return True
    return len(shown) == 2 and close(shown[0], table[0]) and close(shown[1], table[-1])


def step_fits(step, is_avg, table):
    table = [round(v, 2) for v in table]
    if len(table) < 2:
        return False
    diffs = [b - a for a, b in zip(table, table[1:])]
    if is_avg:
        return abs(abs(step) - abs(round((table[-1] - table[0]) / (len(table) - 1), 2))) < 0.011
    return all(abs(abs(round(d, 2)) - abs(step)) < 0.006 for d in diffs)


def expected_tables(label, category, tables):
    """Tables a label is allowed to quote. None means 'any table of the skill'."""
    slots = tables['slots']
    if label == 'TP Cost':
        return [tables.get('tp')]
    if label == 'Turns':
        return [tables.get('turns')]
    if label == 'Speed':
        return [tables.get('speed')]
    if label == 'Chant':
        return [tables.get('cast')]
    if label == 'Pwr':
        return [v for i, _, v in slots if i == 1]
    if label == 'ATK':
        damage = [v for i, t, v in slots if i == 26 and t == 2]
        if damage:
            return damage
    if label in AILMENT_LABELS:
        return [v for i, _, v in slots if i == AILMENT_LABELS[label]]
    if label in EFFECT_LABELS:
        return [v for i, _, v in slots if i == EFFECT_LABELS[label]]
    if label == 'Lv1-9':
        return [tables.get('unique')]
    if label == 'Crown EX':
        return [tables.get('ex')]
    return None


def check_skill_text(category, b, text):
    """Returns (problems, verified claims, numbers that could not be tied to any table)."""
    tables = skill_tables(category, b)
    everything = [v for k, v in tables.items() if k not in ('levels', 'slots') and v] + [v for _, _, v in tables['slots']]
    problems, verified, loose = [], 0, []

    for segment in [s.strip() for line in text.split('\n') for s in line.split(' | ')]:
        if not re.search(r'\d', segment):
            continue
        m = SEGMENT_RE.match(segment)
        if not m:
            loose.append(segment)
            continue
        label, body = m.group('label'), m.group('body')
        sm = SERIES_RE.match(body)
        if not sm:
            loose.append(segment)
            continue
        shown = [float(re.match(NUM, x).group()) for x in sm.group('series').split(' -> ')]
        # A reserved label is held to its own table; if the skill has no such table
        # (a passive whose vanilla phrase is "Speed UP"), any table of the skill may explain it.
        allowed = [t for t in (expected_tables(label, category, tables) or []) if t]
        strict = bool(allowed)
        candidates = allowed if strict else [t for t in everything if t]

        match = None
        for table in candidates:
            for disp in displays(table):
                if series_fits(shown, disp):
                    match = disp
                    break
            if match:
                break
        if match is None:
            if strict or len(shown) > 1:
                problems.append(f"'{segment}' does not match the binary"
                                + (f" ({[round(v, 2) for v in candidates[0]]})" if strict and candidates else ''))
            else:
                loose.append(segment)
            continue
        verified += 1

        if sm.group('step') is not None and not step_fits(float(sm.group('step')), bool(sm.group('avg')), match):
            problems.append(f"'{segment}': the per-level step is not the one of the binary table")
        for lv in (m.group('lv'), sm.group('lv_step'), sm.group('lv_list')):
            if lv is not None and int(lv) != tables['levels']:
                problems.append(f"'{segment}': says L1-{lv} but the skill has {tables['levels']} levels")
    return problems, verified, loose
