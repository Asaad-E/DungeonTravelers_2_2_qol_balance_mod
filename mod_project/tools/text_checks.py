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
# An item holds four (int effect type, float value) pairs. The first two act when it is used on an
# ally, the last two when it is used on an enemy (Deep-Fried Mystery: 2:175, 30:0.75 | 0:175, 25:0.75,
# which the DT2-2 wiki describes as "HP and TP 175 and maybe Berserk; on an enemy, maybe ATK up").
ITEM_PAIRS = 0x24
ITEM_PAIR_COUNT = 4
ITEM_ALLY_PAIRS = 2
ITEM_RESTORE = {             # vanilla wording -> effect type of the pair that holds the amount
    "an ally's HP": 0,
    "an ally's TP": 1,
    "all allies' HP": 3,
}
ITEM_AMOUNT_RE = re.compile(r"Restore (?P<what>an ally's HP|an ally's TP|all allies' HP) \(\+(?P<amount>\d+)\)")
ITEM_DATA_RE = re.compile(r' \((?P<data>[^()]*)\)$')
LIGHT_STEPS_PER_UNIT = 5     # Flashlight stores 10 and lights 50 steps; same ratio in the 4 light items (DT2-2 wiki)
FULL_RESTORE = 9999

# effect type -> (data shown, wording of the game that already says it or None)
ITEM_EFFECTS = {
    0: (lambda v: 'full HP' if v >= FULL_RESTORE else f'HP +{v:g}', r'Fully restore'),
    1: (lambda v: f'TP +{v:g}', None),
    2: (lambda v: f'HP/TP +{v:g}', None),
    3: (lambda v: f'party HP +{v:g}', None),
    4: (lambda v: f'party TP +{v:g}', None),
    6: (lambda v: 'cures 1 ailment', r'one status ailment'),
    7: (lambda v: 'cures all ailments', r'all status ailments'),
    8: (lambda v: f'revives at {v:g}% HP', None),
    9: (lambda v: f'{v * LIGHT_STEPS_PER_UNIT:g} steps', None),
    10: (lambda v: 'leaves the dungeon', r'escape|warp'),
    16: (lambda v: f'sleep {v:g}%', None),
    22: (lambda v: 'cancels Shadow Sew', r'Shadow Sew'),
    23: (lambda v: 'restores stats', r'debuffed stats'),
    24: (lambda v: f'SP +{v:g}', None),
}


def item_pairs(b):
    return [(struct.unpack_from('<i', b, ITEM_PAIRS + 8 * k)[0], struct.unpack_from('<f', b, ITEM_PAIRS + 8 * k + 4)[0])
            for k in range(ITEM_PAIR_COUNT)]


def item_data(b, vanilla_text=''):
    """(everything the item does for an ally, what its text does not say yet), or (None, None) when one of
    its effects is not decoded. Each is a list of short phrases: ['HP/TP +10', 'cures 1 ailment']."""
    every, missing = [], []
    for effect_type, value in item_pairs(b)[:ITEM_ALLY_PAIRS]:
        if effect_type == -1:
            continue
        if effect_type not in ITEM_EFFECTS:
            return None, None
        wording, said_by = ITEM_EFFECTS[effect_type]
        every.append(wording(value))
        if not (said_by and re.search(said_by, vanilla_text, re.I)):
            missing.append(wording(value))
    return every, missing


def check_item_text(b, text, vanilla_text=None):
    """An item text is the original, plus an amount in place of a vague size, plus data in a final
    parenthesis. Every piece of data must be what the item's own effect pairs hold.
    Returns (problems, verified claims)."""
    problems, verified = [], 0
    effect_type, value = item_pairs(b)[0]
    body = text
    m = ITEM_DATA_RE.search(text)
    every, _ = item_data(b)
    if m and (vanilla_text is None or not vanilla_text.endswith(m.group(0))):
        body = text[:m.start()]
        for piece in m.group('data').split(', '):
            if every is not None and piece in every:
                verified += 1
            else:
                problems.append(f"'({m.group('data')})': '{piece}' is not what the item does ({every})")
    claims = list(ITEM_AMOUNT_RE.finditer(body))
    if len(claims) != len(re.findall(r'\(\+\d', body)):
        problems.append(f"'{text}': an amount is written in a form the checker does not know")
    for c in claims:
        if ITEM_RESTORE[c.group('what')] != effect_type or abs(float(c.group('amount')) - value) > TOLERANCE:
            problems.append(f"'{c.group(0)}' does not match the binary (effect type {effect_type}, value {value:g})")
        else:
            verified += 1
    if vanilla_text is not None:
        plain = ITEM_AMOUNT_RE.sub(lambda c: f"Restore {c.group('what')} (size)", body)
        vanilla_plain = re.sub(r'\((?:small|medium|large)\)', '(size)', vanilla_text)
        if plain != vanilla_plain:
            problems.append(f"'{text}': the original wording changed")
    return problems, verified


# ---------------------------------------------------------------------------
# Enemy attacks (also the abilities of summoned monsters)
# ---------------------------------------------------------------------------
ENEMY_SLOT_COUNT = 0x48      # int, then (int effect id, float value, int tail) slots of 12 bytes
ENEMY_SLOTS = 0x4C
ENEMY_DATA_LINE = 'Target:'  # vanilla line 1: "Target: Single / Type: Stab / Range: Long"
ENEMY_TOKEN_RE = re.compile(r'^(?P<label>[A-Za-z][A-Za-z ./]*): (?P<value>[+-]?\d+(?:\.\d+)?%?)$')
AILMENT_NAMES = {v: k for k, v in AILMENT_LABELS.items()}

# Figures that the game's own prose states: effect id -> (wording, factor between the stored value and the
# figure). Where the prose of the original gives another figure than the data, the data is what the game does.
STATED_FIGURES = {
    70: (r'fixed critical hit rate of (\d+)%', 100),
    296: (r'\(Cap: (\d+)\)', 1),
    8: (r'(?:Deal|does|deals) (\d+) (?:fixed )?damage', 1),
    55: (r'(?:With|fixed) (\d+)% (?:accuracy|chance to hit)', 100),
}
# Words of the original prose that name another effect than the one stored. The data is what the game
# does, so the word is corrected and the rest of the sentence stays: (wording, ids the entry must hold,
# ids it must not hold, replacement).
WORDING_FIXES = [
    (r"(lowers the victims') defense", {161}, {162}, r'\1 physical attack'),   # Heavy Stomp, Mega Stomp: 161 is Physical Attack
]
# Effects written on the data line, after the ailments: id -> (label, how the value is written).
# The labels are the ones the skill boxes use. Meaning and evidence of each id: EFFECT_NAMES.
ENEMY_EFFECTS = [
    (8, 'Fixed damage', 'num'), (138, 'Max HP damage', 'pct'), (199, 'Max HP damage', 'pct'), (296, 'Cap', 'num'),
    (55, 'Accuracy', 'pct'), (70, 'Critical rate', 'pct'), (31, 'Critical rate', 'plus_num_pct'),
    (75, 'HP Absorb', 'pct'), (76, 'TP Absorb', 'pct'),
    (54, 'Turn delay rate', 'pct'), (74, 'Buff cancel rate', 'pct'), (79, 'Speed decrease chance', 'pct'),
    (123, 'Shadow Sew', 'pct'),
    (161, 'ATK', 'signed_pct'), (162, 'DEF', 'signed_pct'), (163, 'Magic defense', 'signed_pct'),
    (164, 'Physical evasion', 'signed_pct'), (165, 'Magic evasion', 'signed_pct'),
    (166, 'Physical accuracy', 'signed_pct'), (167, 'Magic accuracy', 'signed_pct'), (168, 'Speed', 'signed_pct'),
    (80, 'Pep', 'signed_num'),
]


def enemy_attack_slots(b):
    count = struct.unpack_from('<i', b, ENEMY_SLOT_COUNT)[0]
    return [struct.unpack_from('<ifi', b, ENEMY_SLOTS + 12 * k) for k in range(count)]


def enemy_ailments(b):
    """{ailment label: chance in %} of an enemy attack, or None when the data cannot be stated plainly
    (the same ailment twice, or a chance of 0). A stored chance above 100% always happens: it is 100%."""
    found = {}
    for effect_id, value, _ in enemy_attack_slots(b):
        if effect_id not in AILMENT_NAMES:
            continue
        pct = min(round(value * 100, 1), 100)
        if AILMENT_NAMES[effect_id] in found or pct <= 0:
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


def write_value(value, style):
    if style == 'num':
        return f'{round(value, 2):g}'
    if style == 'signed_num':
        return f'{round(value, 2):+g}'
    if style == 'plus_num_pct':
        return f'{round(value, 1):+g}%'
    pct = round(value * 100, 1)
    return f'{pct:+g}%' if style == 'signed_pct' else f'{pct:g}%'


def enemy_effect_facts(b):
    """{label: written value} of the other effects of an enemy attack. An effect that appears twice with
    different values, or whose label is already taken, is left out: it cannot be stated in one item."""
    slots = enemy_attack_slots(b)
    facts = {}
    for effect_id, label, style in ENEMY_EFFECTS:
        values = {round(v, 4) for i, v, _ in slots if i == effect_id}
        if len(values) != 1 or label in facts:
            continue
        value = values.pop()
        if value == 0 or (style == 'pct' and not 0 < value <= 1):
            continue
        facts[label] = write_value(value, style)
    return facts


def stated_in_prose(prose):
    """Labels whose figure the prose of the attack already gives."""
    said = set()
    for effect_id, (pattern, _) in STATED_FIGURES.items():
        if re.search(pattern, prose):
            said.update(label for i, label, _ in ENEMY_EFFECTS if i == effect_id)
    return said


STAT_LABELS = ('ATK', 'DEF', 'Magic defense', 'Physical evasion', 'Magic evasion', 'Physical accuracy',
               'Magic accuracy', 'Speed')


def enemy_effect_tokens(b, prose):
    """['HP Absorb: 30%', 'ATK/DEF: -25%']: what the prose does not already give as a figure.
    Stat changes of the same size share one item."""
    said = stated_in_prose(prose)
    tokens, stats = [], {}
    for label, value in enemy_effect_facts(b).items():
        if label in said:
            continue
        if label in STAT_LABELS:
            stats.setdefault(value, []).append(label)
        else:
            tokens.append(f'{label}: {value}')
    return tokens + [f'{join_labels(labels)}: {value}' for value, labels in stats.items()]


def join_labels(labels):
    """['Physical accuracy', 'Magic accuracy'] -> 'Physical/Magic accuracy'; ['ATK', 'DEF'] -> 'ATK/DEF'."""
    last_words = {label.split(' ')[-1] for label in labels}
    if len(labels) > 1 and len(last_words) == 1 and all(' ' in label for label in labels):
        return '/'.join(label.rsplit(' ', 1)[0] for label in labels) + ' ' + last_words.pop()
    return '/'.join(labels)


def split_labels(text):
    """The reverse of join_labels."""
    parts = text.split('/')
    if ' ' in parts[-1] and any(part not in STAT_LABELS for part in parts[:-1]):
        word = parts[-1].rsplit(' ', 1)[1]
        return [part if part in STAT_LABELS else f'{part} {word}' for part in parts]
    return parts


def correct_prose(b, prose):
    """Replaces a figure of the original prose that the data does not hold by the stored one."""
    slots = enemy_attack_slots(b)
    for effect_id, (pattern, factor) in STATED_FIGURES.items():
        m = re.search(pattern, prose)
        stored = {round(v * factor, 2) for i, v, _ in slots if i == effect_id}
        if m and len(stored) == 1 and float(m.group(1)) not in stored:
            prose = prose[:m.start(1)] + f'{stored.pop():g}' + prose[m.end(1):]
    ids = {i for i, _, _ in slots}
    for pattern, needs, excludes, replacement in WORDING_FIXES:
        if needs <= ids and not excludes & ids:
            prose = re.sub(pattern, replacement, prose)
    return prose


def check_enemy_attack_text(b, text, vanilla_text):
    """The prose must be the original prose, except for a figure corrected to the stored value; line 1 may
    only gain items that the entry holds. Returns (problems, verified claims)."""
    lines, vanilla_lines = text.split('\n'), vanilla_text.split('\n')
    has_data_line = vanilla_lines[0].startswith(ENEMY_DATA_LINE)
    prose, vanilla_prose = ('\n'.join(x[1:]) if has_data_line else '\n'.join(x) for x in (lines, vanilla_lines))
    verified = 0
    if prose != vanilla_prose:
        if prose != correct_prose(b, vanilla_prose):
            return [f"'{text}': the prose differs from the original"], 0
        verified += 1
    if not has_data_line or lines[0] == vanilla_lines[0]:
        if lines[0] != vanilla_lines[0] and has_data_line is False and prose == vanilla_prose:
            return [f"'{lines[0]}': line 1 may only add data after the original data line"], 0
        return [], verified
    if not lines[0].startswith(vanilla_lines[0] + ' / '):
        return [f"'{lines[0]}': line 1 may only add data after the original data line"], 0
    ailments, facts = enemy_ailments(b) or {}, enemy_effect_facts(b)
    for token in lines[0][len(vanilla_lines[0]) + 3:].split(' / '):
        m = ENEMY_TOKEN_RE.match(token)
        if not m:
            return [f"'{token}': not a 'Label: value' item"], 0
        labels = split_labels(m.group('label'))
        if all(label in AILMENT_LABELS for label in labels):
            ok = all(label in ailments and f'{ailments[label]:g}%' == m.group('value') for label in labels)
        elif all(label in STAT_LABELS for label in labels):
            ok = all(facts.get(label) == m.group('value') for label in labels)
        else:
            ok = facts.get(m.group('label')) == m.group('value')
        if not ok:
            return [f"'{token}' does not match the binary (ailments {ailments}, effects {facts})"], 0
        verified += len(labels)
    return [], verified
