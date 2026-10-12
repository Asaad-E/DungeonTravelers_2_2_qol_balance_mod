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
import rules
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
from game_profile import layout                           # noqa: E402  (data_tables/record_layouts.json)
UNIQUE_VALUES = layout('UniqueSkillData')['values']
# Line: the figure of the game; Balance_Line: the one the Balance variant holds where its program patch changes it
# (sheet ExePatches of balance_criteria.xlsx), worded in balance_skill_text.xlsx
UNIQUE_NOTE_LINES = {line for column in ('Line', 'Balance_Line')
                     for line in rules.pairs('UniqueSkillNotes', 'Skill', column).values() if line}
# a line whose figure is worked out from what the entry stores (sheet DerivedLines): Concentrate on the Balance variant
DERIVED_LINES = {r['Line'] for r in rules.rows('DerivedLines') if r.get('Line')}
UNIQUE_LABELS = set(rules.pairs('UniqueSkillLabels', 'Skill', 'Label').values())   # in place of 'Lv1-9'
TOLERANCE = 0.006


_DOLL_ACTION_PCKS = None

DOLL_ACTIONS = {
    49: ('Technique', ['TechniqueSkillData_0106.bin']),
    95: ('Technique', ['TechniqueSkillData_0101.bin']),
    96: ('Technique', ['TechniqueSkillData_0102.bin']),
    97: ('Technique', ['TechniqueSkillData_0104.bin']),
    98: ('Technique', ['TechniqueSkillData_0103.bin']),
    100: ('Magic', ['MagicSkillData_0235.bin']),
}


_ORIGINALS_DIR = None


def use_originals(folder):
    """The folder the action skills of the dolls are read from: backups/ unless a variant builds on other values
    (tools/build_variant.py balance), where the text of a doll skill must state the power of the built action."""
    global _ORIGINALS_DIR, _DOLL_ACTION_PCKS
    _ORIGINALS_DIR, _DOLL_ACTION_PCKS = folder, None


def _get_doll_action_slots(skill_id, levels):
    global _DOLL_ACTION_PCKS
    if skill_id not in DOLL_ACTIONS:
        return []
    if _DOLL_ACTION_PCKS is None:
        import os
        from pck_handler import PckArchive
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_dir = _ORIGINALS_DIR or os.path.join(base_dir, 'backups')
        _DOLL_ACTION_PCKS = {
            'Technique': dict(PckArchive(os.path.join(backup_dir, 'TechniqueSkillData.pck')).files),
            'Magic': dict(PckArchive(os.path.join(backup_dir, 'MagicSkillData.pck')).files),
        }
    cat, filenames = DOLL_ACTIONS[skill_id]
    lay = SKILL_LAYOUTS[cat]
    slots = []
    for fn in filenames:
        b = _DOLL_ACTION_PCKS[cat][fn]
        for k in range(i32(b, lay['count'])):
            off = lay['slots'] + k * SLOT_SIZE
            slots.append((i32(b, off), i32(b, off + 4 + 4 * LEVELS), read_array(b, off + 4)[0][:levels]))
    return slots


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
    if category == 'Technique':
        sid = i32(b, 0)
        tables['slots'].extend(_get_doll_action_slots(sid, levels))
    return tables


def displays(values):
    """Ways a stored table can legitimately be printed: as is, as a percentage, as 100% + value, or halved
    (the power of a heal as the multiple of RES it restores: docs/FORMULAS.md 6b)."""
    return [list(values), [100 * v for v in values], [100 * (1 + v) for v in values], [0.5 * v for v in values]]


def close(a, b):
    return abs(abs(a) - abs(b)) < TOLERANCE


def series_fits(shown, table):
    table = [round(v, 2) for v in table]
    if len(shown) == 1:
        return all(close(shown[0], v) for v in table)
    if len(shown) == len(table) and all(close(s, v) for s, v in zip(shown, table)):
        return True
    distinct = [v for k, v in enumerate(table) if k == 0 or not close(v, table[k-1])]
    if len(shown) == len(distinct) and all(close(s, d) for s, d in zip(shown, distinct)):
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
        t = tables.get('turns')
        if t and any(t):
            return [t]
        st = [v for i, _, v in slots if i == 147]
        if st:
            return st
        return [t]
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
    if label == 'Lv1-9' or (label in UNIQUE_LABELS and tables.get('unique')):
        return [tables.get('unique')]
    if label == 'Crown EX':
        return [tables.get('ex')]
    return None


def check_skill_text(category, b, text):
    """Returns (problems, verified claims, numbers that could not be tied to any table)."""
    if category == 'Unique':     # a line of the sheet UniqueSkillNotes holds a figure the entry does not store
        text = chr(10).join(line for line in text.split(chr(10)) if line not in UNIQUE_NOTE_LINES)
    text = chr(10).join(line for line in text.split(chr(10)) if line not in DERIVED_LINES)
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
ITEM_PAIRS = layout('ItemData')['pairs']
ITEM_PAIR_COUNT = 4
ITEM_ALLY_PAIRS = 2
ITEM_RESTORE = {             # vanilla wording -> effect type of the pair that holds the amount
    "an ally's HP": 0,
    "an ally's TP": 1,
    "all allies' HP": 3,
}
ITEM_AMOUNT_RE = re.compile(r"Restore (?P<what>an ally's HP|an ally's TP|all allies' HP) \(\+(?P<amount>\d+)\)")
ITEM_DATA_RE = re.compile(r' \((?P<data>[^()]*)\)$')
LIGHT_STEPS_PER_UNIT = rules.setting('light_steps_per_unit')   # Flashlight stores 10 and lights 50 steps (DT2-2 wiki)
FULL_RESTORE = rules.setting('full_restore')



def _item_wording(row):
    def wording(value):
        if row['Full_Text'] and value >= FULL_RESTORE:
            return row['Full_Text']
        return row['Text'].replace('{v}', f"{value * row['Scale']:g}")
    return wording


# effect type -> (data shown, wording of the game that already says it or None). Sheet ItemEffects of
# data_tables/qol_rules.xlsx: {v} in Text is the stored value times Scale. The types were decoded with
# the item list of the DT2-2 wiki (pages/36.html); ailment types hold the chance in %, buff types as a
# fraction, light as units of 5 steps.
ITEM_EFFECTS = {int(r['Type']): (_item_wording(r), r['Already_Said_By'] or None) for r in rules.rows('ItemEffects')}
# Effects that hurt: an item made only of these is meant for an enemy, and its data is the enemy's side.
ITEM_HARMFUL = {int(r['Type']) for r in rules.rows('ItemEffects') if rules.yes(r['Harmful'])}


def item_pairs(b):
    return [(struct.unpack_from('<i', b, ITEM_PAIRS + 8 * k)[0], struct.unpack_from('<f', b, ITEM_PAIRS + 8 * k + 4)[0])
            for k in range(ITEM_PAIR_COUNT)]


def item_data(b, vanilla_text=''):
    """(everything the item does for an ally, what its text does not say yet), or (None, None) when one of
    its effects is not decoded. Each is a list of short phrases: ['HP/TP +10', 'cures 1 ailment']."""
    every, missing = [], []
    pairs = item_pairs(b)
    side = pairs[:ITEM_ALLY_PAIRS]
    used = [t for t, _ in side if t != -1]
    if used and all(t in ITEM_HARMFUL for t in used) and any(t != -1 for t, _ in pairs[ITEM_ALLY_PAIRS:]):
        side = pairs[ITEM_ALLY_PAIRS:]
    for effect_type, value in side:
        if effect_type == -1:
            continue
        if effect_type not in ITEM_EFFECTS:
            return None, None
        wording, said_by = ITEM_EFFECTS[effect_type]
        every.append(wording(value))
        if not (said_by and re.search(said_by, vanilla_text, re.I)):
            missing.append(wording(value))
    return every, missing


def check_item_text(b, text, vanilla_text=None, shortened=None):
    """An item text is the original, plus an amount in place of a vague size, plus data in a final
    parenthesis. Every piece of data must be what the item's own effect pairs hold.
    shortened: the approved shorter form of the original sentence, for items whose sentence plus data
    would not fit in one line. Returns (problems, verified claims)."""
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
        if plain != vanilla_plain and plain != shortened:
            problems.append(f"'{text}': the original wording changed")
    return problems, verified


# ---------------------------------------------------------------------------
# Enemy attacks (also the abilities of summoned monsters)
# ---------------------------------------------------------------------------
ENEMY_SLOT_COUNT = layout('EnemyAttackData')['slot_count']      # int, then (int effect id, float value, int tail) slots of 12 bytes
ENEMY_SLOTS = layout('EnemyAttackData')['slots']
ENEMY_DATA_LINE = 'Target:'  # vanilla line 1: "Target: Single / Type: Stab / Range: Long"
ENEMY_TOKEN_RE = re.compile(r'^(?P<label>[A-Za-z][A-Za-z ./]*): (?P<value>[+-]?\d+(?:\.\d+)?[%x]?)$')
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
WORDING_FIXES = [(r['Pattern'], rules.id_set(r['Needs_Effects']), rules.id_set(r['Lacks_Effects']), r['Replacement'])
                 for r in rules.rows('WordingFixes')]       # sheet WordingFixes of qol_rules.xlsx
# Effects written on the data line, after the ailments: (id, label, how the value is written), in the
# order written. Sheet EnemyEffects of qol_rules.xlsx; the labels are the ones the skill boxes use.
# Meaning and evidence of each id: EFFECT_NAMES.
ENEMY_EFFECTS = [(int(r['Effect_ID']), r['Label'], r['Style']) for r in rules.rows('EnemyEffects')]
# the effects written after the power of the attack: when the line is short of room they are the ones left out
ENEMY_AFTER_POWER = {int(r['Effect_ID']) for r in rules.rows('EnemyEffects') if rules.yes(r.get('After_Power'))}
# the effects written only on the attacks a summon of the player can use (the scope the power of an attack has too)
ENEMY_SUMMON_ONLY = {int(r['Effect_ID']) for r in rules.rows('EnemyEffects') if str(r.get('Scope') or '') == 'summons'}


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
    if style == 'abs_num':                       # a decrease stored as a negative figure, under a label that says so
        return f'{abs(round(value, 2)):g}'
    if style == 'half_x':                        # a heal: half the stored figure is what multiplies RES (docs/FORMULAS.md 6b)
        return f'{round(value / 2, 2):g}x'
    if style == 'abs_pct':
        return f'{abs(round(value * 100, 1)):g}%'
    pct = round(value * 100, 1)
    return f'{pct:+g}%' if style == 'signed_pct' else f'{pct:g}%'


def enemy_effect_facts(b):
    """{label: written value} of the other effects of an enemy attack. An effect that appears twice with
    different values, or whose label is already taken, is left out: it cannot be stated in one item."""
    slots = enemy_attack_slots(b)
    facts, late = {}, {}
    for effect_id, label, style in ENEMY_EFFECTS:
        values = {round(v, 4) for i, v, _ in slots if i == effect_id}
        if len(values) != 1 or label in facts or label in late:
            continue
        if effect_id in ENEMY_SUMMON_ONLY and i32(b, 0) not in summon_attacks():
            continue
        value = values.pop()
        if value == 0 or (style == 'pct' and not 0 < value <= 1):
            continue
        (late if effect_id in ENEMY_AFTER_POWER else facts)[label] = write_value(value, style)
    power = round(struct.unpack_from('<f', b, ENEMY_POWER)[0], 4)
    if power and i32(b, 0) in power_scope() and any(i == PLAIN_HIT for i, _, _ in slots) and POWER_LABEL not in facts:
        facts[POWER_LABEL] = write_value(power, 'signed_pct')
    facts.update({label: value for label, value in late.items() if label not in facts})
    return facts


ENEMY_POWER = layout('EnemyAttackData')['power']           # float: what a physical attack adds to the modifiers of its attack value (0x44b497)
PLAIN_HIT = 0                # the effect of a hit that deals physical damage
POWER_LABEL = rules.setting('enemy_power_label')
_POWER_SCOPE = []


def summon_attacks():
    """Ids of the enemy attacks a summon or a guest ally of the player can use, the passive of each among them."""
    if not _SUMMON_ATTACKS:
        import summon_data
        import npc_data
        for summon in summon_data.summons():
            _SUMMON_ATTACKS.update(summon['attacks'])
            if summon.get('passive') is not None:
                _SUMMON_ATTACKS.add(summon['passive'])
        for guest in npc_data.npcs():               # a guest ally shows her abilities on the same screen
            _SUMMON_ATTACKS.update(guest['attacks'])
            if guest.get('extra_attack') is not None:
                _SUMMON_ATTACKS.add(guest['extra_attack'])
    return _SUMMON_ATTACKS


_SUMMON_ATTACKS = set()


def power_scope():
    """Ids of the enemy attacks whose power is shown: the ones a summon or a guest ally of the player can use."""
    if not _POWER_SCOPE:
        _POWER_SCOPE.append(summon_attacks() if rules.setting('enemy_power_scope') == 'summons' else set())
    return _POWER_SCOPE[0]


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


# ---------------------------------------------------------------------------
# Meals (ice cream and ramen shops)
# ---------------------------------------------------------------------------
FOOD_COUNT = layout('FoodMenuData')['count']            # int, then (int effect id, float value) pairs from 0x20
FOOD_PAIRS = layout('FoodMenuData')['pairs']
FOOD_HP, FOOD_TP, FOOD_BOTH = 62, 63, 64      # tenths of the maximum (DT2-2 wiki: stored 2 = "HP 2/10")
FOOD_VAGUE_RE = re.compile(r'(?:a tiny bit of|a little|some|a lot of) (HP and TP|HP|TP)')
FOOD_EXACT_RE = re.compile(r'(\d+)% (HP and TP|HP and (\d+)% TP|HP|TP)')


def food_effects(b):
    count = struct.unpack_from('<i', b, FOOD_COUNT)[0]
    return [struct.unpack_from('<if', b, FOOD_PAIRS + 8 * k) for k in range(count)]


def food_amounts(b):
    """(HP %, TP %) a meal restores, None where it restores none."""
    effects = dict(food_effects(b))
    both = effects.get(FOOD_BOTH)
    hp, tp = effects.get(FOOD_HP, both), effects.get(FOOD_TP, both)
    return (None if hp is None else round(hp * 10), None if tp is None else round(tp * 10))


def food_text(b, effect_line):
    """The effect line with the stored amount in place of the vague one."""
    hp, tp = food_amounts(b)

    def exact(m):
        what = m.group(1)
        if what == 'HP and TP' and hp is not None and tp is not None:
            return f'{hp}% HP and TP' if hp == tp else f'{hp}% HP and {tp}% TP'
        if what == 'HP' and hp is not None:
            return f'{hp}% HP'
        if what == 'TP' and tp is not None:
            return f'{tp}% TP'
        return m.group(0)
    text = FOOD_VAGUE_RE.sub(exact, effect_line)
    levels = meal_buff_levels()
    for effect_type, _ in food_effects(b):         # "gain Aim" -> "gain Aim Lv10": the level the program gives the buff
        phrase = MEAL_PHRASES.get(effect_type)
        if phrase and effect_type in levels and phrase in text:
            text = text.replace(phrase, f'{phrase} Lv{levels[effect_type]}', 1)
    return text


MEAL_PHRASES = {int(r['Type']): r['Phrase'] for r in rules.rows('MealBuffs') if r.get('Phrase') and str(r['Type']).isdigit()}
_MEAL_LEVELS = []


def meal_buff_levels():
    """{meal effect type: level of the buff}, read from the program (tools/item_effect_data.py)."""
    if not _MEAL_LEVELS:
        import item_effect_data
        _MEAL_LEVELS.append({kind: level for kind, (_, level) in item_effect_data.meal_buffs().items()})
    return _MEAL_LEVELS[0]


def check_food_text(b, text, vanilla_text):
    """Only the amount may change, and it must be the stored one. Returns (problems, verified)."""
    if text == vanilla_text:
        return [], 0
    if text != food_text(b, vanilla_text):
        return [f"'{text}': not the original sentence with the stored amounts ({food_amounts(b)})"], 0
    return [], len(re.findall(r'\d+%', text))


# ---------------------------------------------------------------------------
# Party skills
# ---------------------------------------------------------------------------
# The entry holds who must be in the party and the id of its effect, and no amount. The DT2-2 wiki
# (pages/72.html) lists the upper bound of each bonus and the rule: the bonus grows with the number of
# awards and reaches the bound with all of them (half of it with half of them). The game says the rule
# itself ("Party skills grow stronger the more Awards you obtain."). Bounds and wording: sheets
# PartySkillBounds and Settings of qol_rules.xlsx.
PARTY_EFFECT = layout('PartySkillData')['effect']
PARTY_LINE = rules.setting('party_line_width')
PARTY_SENTENCES = {int(r['Effect_ID']): (r['Sentence'], [part.strip() for part in str(r['Bounds']).split(',') if part.strip()])
                   for r in rules.rows('PartySkillBounds')}
PARTY_BOUNDS = {effect_id: bounds for effect_id, (_, bounds) in PARTY_SENTENCES.items()}


def party_skill_bounds(b):
    return PARTY_BOUNDS.get(struct.unpack_from('<i', b, PARTY_EFFECT)[0], [])


def party_skill_text(b, effect_line):
    """The sentence of the rules sheet for the effect of this entry, or the game's line when it has none."""
    sentence, _ = PARTY_SENTENCES.get(struct.unpack_from('<i', b, PARTY_EFFECT)[0], ('', []))
    return sentence or effect_line


def check_party_skill_text(b, text, vanilla_text):
    """The original line, or the sentence of the rules sheet carrying every bound it lists.
    Returns (problems, verified)."""
    if text == vanilla_text:
        return [], 0
    problems, bounds = [], party_skill_bounds(b)
    if text != party_skill_text(b, vanilla_text):
        problems.append(f"'{text}': not the sentence of the sheet PartySkillBounds")
    figures = re.findall(r'[+-]\d+%?', text)
    if sorted(figures) != sorted(bounds) and not (len(set(bounds)) == 1 and figures == bounds[:1] and 'each' in text):
        problems.append(f"'{text}': its figures {figures} are not the bounds of the table {bounds}")
    if len(text) > PARTY_LINE:
        problems.append(f"'{text}': {len(text)} characters, the box of the party skill list holds {PARTY_LINE}")
    return problems, 0 if problems else len(bounds)


# ---------------------------------------------------------------------------
# Joint skills
# ---------------------------------------------------------------------------
# A joint skill has one sentence. Where it speaks of an effect whose value the entry stores, the value
# is written into the sentence: "High chance of instakill." -> "85% chance of instakill.". The sentences
# are the sheet JointSkillSentences of qol_rules.xlsx, with {eID} where the value of effect ID goes; how
# each value is written is the sheet JointEffects. A skill without a row keeps the game's text.
JOINT_SLOTS, JOINT_SLOT_COUNT = layout('JoinSkillData')['slots'], layout('JoinSkillData')['slot_count']
JOINT_PLACE_RE = re.compile(r'\{e(\d+)\}')
JOINT_STYLES = {
    'chance': lambda v: f'{min(100 * v, 100):g}%',          # a chance stored above 100% is 100%
    'pct': lambda v: f'{100 * v:g}%',
    'signed_pct': lambda v: f'{100 * v:+g}%',
    'signed_points_pct': lambda v: f'{v:+g}%',
    'signed_num': lambda v: f'{v:+g}',
    'num': lambda v: f'{v:g}',
    'times': lambda v: f'{1 + v:g}x',
}
JOINT_EFFECTS = {int(r['Effect_ID']): (r['Style'], str(r['Text'])) for r in rules.rows('JointEffects')}
JOINT_SENTENCES = rules.pairs('JointSkillSentences', 'Skill', 'Sentence')


def joint_effects(b):
    count = struct.unpack_from('<i', b, JOINT_SLOT_COUNT)[0]
    return [struct.unpack_from('<ifi', b, JOINT_SLOTS + 12 * k) for k in range(count)]


def joint_skill_text(b, name, vanilla_text):
    """(text, problems): the sentence of the rules sheet with the stored values, or the game's text."""
    template = JOINT_SENTENCES.get(name)
    if template is None:
        return vanilla_text, []
    stored, problems = {i: v for i, v, _ in joint_effects(b)}, []

    def value(m):
        effect_id = int(m.group(1))
        if effect_id not in stored:
            problems.append(f'{name}: the sentence quotes effect {effect_id}, which the skill does not hold')
            return m.group(0)
        if effect_id not in JOINT_EFFECTS:
            problems.append(f'{name}: effect {effect_id} has no row in the sheet JointEffects')
            return m.group(0)
        style, text = JOINT_EFFECTS[effect_id]
        return text if style == 'text' else JOINT_STYLES[style](stored[effect_id])
    return JOINT_PLACE_RE.sub(value, template), problems


def check_joint_skill_text(b, name, text, vanilla_text):
    """The game's text, or the sentence of the rules sheet filled from the entry. Returns (problems, verified)."""
    if text == vanilla_text:
        return [], 0
    expected, problems = joint_skill_text(b, name, vanilla_text)
    if text != expected:
        problems.append(f"'{text}': not the sentence of the rules sheet with the stored values ('{expected}')")
    return problems, 0 if problems else len(JOINT_PLACE_RE.findall(JOINT_SENTENCES[name]))


# ---------------------------------------------------------------------------
# The voice of the game
# ---------------------------------------------------------------------------
# Hard rule of decided: nothing shown in the game may speak from outside it ("player guide", "the game
# data holds no figure"). Where a figure comes from is recorded in the workbooks, never on screen.
# Words: sheet OutOfGameWords of qol_rules.xlsx.
OUT_OF_GAME_RE = re.compile(r'\b(' + '|'.join(re.escape(r['Word']) for r in rules.rows('OutOfGameWords')) + r')\b', re.I)


def out_of_game_words(text, vanilla_text=''):
    """Words of the forbidden list that the mod put into a text (the game's own wording is left alone)."""
    kept = {w.lower() for w in OUT_OF_GAME_RE.findall(vanilla_text or '')}
    return sorted({w.lower() for w in OUT_OF_GAME_RE.findall(text or '')} - kept)
