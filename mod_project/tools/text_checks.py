"""
Checks a skill text against the binary and against the display specification
(docs/SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md).

Used by the variant build and by the test suite, so the wording of each skill can be
edited by hand while its figures stay tied to the data.

Understood notation:
    Label: 125% -> 134 -> 143 -> ... -> 200% (L10)     one value per level
    Label: +8% -> +10% -> +12% -> +15% -> +18% (L1-5 Max)
    Label: 130% (+8%/Lv) -> 202% (L10 Max)             base, exact step, cap (linear tables)
    Label: +20% (+2%/Lv)                               base and exact step
    Label: 10% (+1-2%/Lv) -> 20%                       base, bounds of an uneven step, cap
    Label: 0.8x -> 0.9x                                first -> last
    Label: 0.85x                                       value that does not change
Rejected: averages, e.g. "(avg +3.33%/Lv)".
"""
import re
import struct
from extract_vanilla import SKILL_LAYOUTS, SLOT_SIZE, LEVELS, i32, read_array, leading_nonzero

NUM = r'[+-]?\d+(?:\.\d+)?'
SEGMENT_RE = re.compile(r'^(?P<label>[^:]+?): (?P<body>.+)$')
# "12% Max HP -> 15% -> 18%": each value may carry a unit and a few plain words.
VALUE_RE = rf'{NUM}[%x]?(?: [A-Za-z][A-Za-z ]*?)?'
SERIES_RE = re.compile(rf'^{VALUE_RE}(?: -> {VALUE_RE})*$')
STEP_RE = re.compile(r'^(?P<step>[+-]\d+(?:\.\d+)?)(?:-(?P<step_hi>\d+(?:\.\d+)?))?[%x]?/Lv$')
LEVELS_RE = re.compile(r'^L(?:1-)?(?P<n>\d+)(?: Max)?$')

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


def step_fits(shown, step, table):
    """'base (+step/Lv) [-> cap]': the table must rise by exactly that step at every level.
    'base (+lo-hi/Lv) -> cap': lo and hi must be the smallest and the largest rise."""
    lo, hi = step
    table = [round(v, 2) for v in table]
    if len(table) < 2 or not close(shown[0], table[0]):
        return False
    if len(shown) > 1 and not close(shown[-1], table[-1]):
        return False
    diffs = [abs(round(b - a, 2)) for a, b in zip(table, table[1:])]
    if hi is None:
        return all(abs(d - abs(lo)) < TOLERANCE for d in diffs)
    return len(shown) > 1 and abs(min(diffs) - abs(lo)) < TOLERANCE and abs(max(diffs) - hi) < TOLERANCE


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
        if re.search(r'\bavg\b', segment):
            problems.append(f"'{segment}': averages are not allowed by the display specification")
            continue
        if not re.search(r'\d', segment):
            continue
        m = SEGMENT_RE.match(segment)
        if not m:
            loose.append(segment)
            continue
        label, body = m.group('label'), m.group('body')
        notes = re.findall(r'\(([^)]*)\)', body)
        plain = re.sub(r'\s*\([^)]*\)', '', body).strip()
        if not SERIES_RE.match(plain):
            loose.append(segment)
            continue
        shown = [float(x) for x in re.findall(rf'(?:^|-> )({NUM})', plain)]
        step = next(((float(sm.group('step')), float(sm.group('step_hi')) if sm.group('step_hi') else None)
                     for sm in map(STEP_RE.match, notes) if sm), None)

        # A reserved label is held to its own table; if the skill has no such table
        # (a passive whose vanilla phrase is "Speed UP"), any table of the skill may explain it.
        allowed = [t for t in (expected_tables(label, category, tables) or []) if t]
        strict = bool(allowed)
        candidates = allowed if strict else [t for t in everything if t]

        match = None
        for table in candidates:
            for disp in displays(table):
                if (step_fits(shown, step, disp) if step is not None else series_fits(shown, disp)):
                    match = disp
                    break
            if match:
                break
        if match is None:
            if strict or len(shown) > 1 or step is not None:
                problems.append(f"'{segment}' does not match the binary"
                                + (f" ({[round(v, 2) for v in candidates[0]]})" if strict and candidates else ''))
            else:
                loose.append(segment)
            continue
        verified += 1

        for note in notes:
            lv = LEVELS_RE.match(note)
            if lv and int(lv.group('n')) not in (1, tables['levels']):
                problems.append(f"'{segment}': says level {lv.group('n')} but the skill has {tables['levels']} levels")
    return problems, verified, loose


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------
ITEM_PAIRS = 0x24            # four (int effect type, float value) pairs
ITEM_PAIR_COUNT = 4
ITEM_RESTORE = {             # vanilla wording -> effect type of the pair that holds the amount
    "an ally's HP": 0,
    "an ally's TP": 1,
    "all allies' HP": 3,
}
ITEM_AMOUNT_RE = re.compile(r"Restore (?P<what>an ally's HP|an ally's TP|all allies' HP) \(\+(?P<amount>\d+)\)")


def item_pairs(b):
    return [(struct.unpack_from('<i', b, ITEM_PAIRS + 8 * k)[0], struct.unpack_from('<f', b, ITEM_PAIRS + 8 * k + 4)[0])
            for k in range(ITEM_PAIR_COUNT)]


def check_item_text(b, text):
    """Every amount an item text states must be the value of the item's first effect pair, of the stated kind.
    Returns (problems, verified claims)."""
    problems, verified = [], 0
    effect_type, value = item_pairs(b)[0]
    claims = list(ITEM_AMOUNT_RE.finditer(text))
    if len(claims) != len(re.findall(r'\(\+\d', text)):
        problems.append(f"'{text}': an amount is written in a form the checker does not know")
    for m in claims:
        if ITEM_RESTORE[m.group('what')] != effect_type or abs(float(m.group('amount')) - value) > TOLERANCE:
            problems.append(f"'{m.group(0)}' does not match the binary (effect type {effect_type}, value {value:g})")
        else:
            verified += 1
    return problems, verified


# ---------------------------------------------------------------------------
# Enemy attacks (also the abilities of summoned monsters)
# ---------------------------------------------------------------------------
ENEMY_SLOT_COUNT = 0x48      # int, then (int effect id, float value, int tail) slots of 12 bytes
ENEMY_SLOTS = 0x4C
ENEMY_DATA_LINE = 'Target:'  # vanilla line 1: "Target: Single / Type: Stab / Range: Long"
ENEMY_TOKEN_RE = re.compile(r'^(?P<labels>[A-Za-z]+(?:/[A-Za-z]+)*): (?P<pct>\d+(?:\.\d+)?)%$')
AILMENT_NAMES = {v: k for k, v in AILMENT_LABELS.items()}


def enemy_attack_slots(b):
    count = struct.unpack_from('<i', b, ENEMY_SLOT_COUNT)[0]
    return [struct.unpack_from('<ifi', b, ENEMY_SLOTS + 12 * k) for k in range(count)]


def enemy_ailments(b):
    """{ailment label: chance in %} of an enemy attack, or None when the data cannot be stated plainly
    (the same ailment twice, or a chance outside 0-100%)."""
    found = {}
    for effect_id, value, _ in enemy_attack_slots(b):
        if effect_id not in AILMENT_NAMES:
            continue
        pct = round(value * 100, 1)
        if AILMENT_NAMES[effect_id] in found or not 0 < pct <= 100:
            return None
        found[AILMENT_NAMES[effect_id]] = pct
    return found


def enemy_ailment_tokens(b):
    """['Poison: 30%', 'Freeze/Silence: 20%']: ailments in slot order, grouped when the chance is the same."""
    found = enemy_ailments(b)
    groups = {}
    for label, pct in (found or {}).items():
        groups.setdefault(pct, []).append(label)
    return [f"{'/'.join(labels)}: {pct:g}%" for pct, labels in groups.items()]


def check_enemy_attack_text(b, text, vanilla_text):
    """The prose must be the vanilla prose; line 1 may only gain the ailment chances stored in the entry.
    Returns (problems, verified claims)."""
    lines, vanilla_lines = text.split('\n'), vanilla_text.split('\n')
    if lines[1:] != vanilla_lines[1:]:
        return [f"'{text}': the prose differs from the original"], 0
    if lines[0] == vanilla_lines[0]:
        return [], 0
    if not vanilla_lines[0].startswith(ENEMY_DATA_LINE) or not lines[0].startswith(vanilla_lines[0] + ' / '):
        return [f"'{lines[0]}': line 1 may only add data after the original data line"], 0
    stated = {}
    for token in lines[0][len(vanilla_lines[0]) + 3:].split(' / '):
        m = ENEMY_TOKEN_RE.match(token)
        if not m or any(label not in AILMENT_LABELS for label in m.group('labels').split('/')):
            return [f"'{token}': not a known 'Ailment: N%' token"], 0
        for label in m.group('labels').split('/'):
            stated[label] = float(m.group('pct'))
    if stated != enemy_ailments(b):
        return [f"'{lines[0]}' does not match the binary ({enemy_ailments(b)})"], 0
    return [], len(stated)
