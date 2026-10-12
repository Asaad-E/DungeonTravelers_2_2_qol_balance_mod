"""
Line 1 of a skill: the one line the game shows in battle, where the skill level is unknown.

Damage cannot be given as a figure there, so line 1 says how hard the skill hits with one word
from a fixed scale, chosen by the average of the real per-level values in the binary. The chance
of an ailment is given as a figure in the shortest true form:

    "Deal bash damage to one enemy. May stun."  ->  "Deal minor bash damage to one enemy. May stun (30%+)."

Damage scale (the words and the 80% floor were set by hand; the other bounds come from the data)

    Word           Physical: average ATK         Magic: average Pwr
    negligible     below 80%                     below 80
    minor          80% - 124%                    80 - 249
    moderate       125% - 149%                   250 - 399
    major          150% - 174%                   400 - 499
    severe         175% - 224%                   500 - 699
    tremendous     225% and above                700 and above   (out of the scale; the game's own word)

Ailment chance (the rule)

    (25%)       the chance is the same at every level
    (30%+)      it starts at 30% and rises by 10 points or less over the levels
    (20-50%)    it rises by more: first level - last level
    (100%)      it always happens (a stored chance above 100% is written as 100%)
    The tilde of "~30%+" cannot be used: the game font has no glyph for it.

Everything else (the rule: line 1 must say the value)

    A skill that deals no damage says how much it does in the same three forms, at the end of its
    sentence: "Raise the party's ATK (8%+)."  "ATK bonus with sword equipped (3-15%)."
    When the sentence does not name what the figure measures, the label goes with it:
    "Revive a dead ally (HP on revival 40-88%)."  The exact value of each level is in the box below.

A skill is given a damage word only when the known power table is the whole story: if it carries
an effect that is not understood (a second multiplier, a formula based on the target's HP), its
sentence is left as the game wrote it.
"""
import re
import statistics
import rules

POWER_PHYS, POWER_MAGIC = 26, 1
DAMAGE_XN = 73
# The scale, the word beyond it and the sentences below are sheets of data_tables/qol_rules.xlsx
# (DamageScale, Settings, Line1Templates). Edit them there.
_SCALE = rules.rows('DamageScale')
DAMAGE_WORDS = tuple(r['Word'] for r in _SCALE[:-1])
OUT_OF_SCALE = _SCALE[-1]['Word']
PHYS_BOUNDS = tuple(r['Physical_Below'] for r in _SCALE[:-1])      # average ATK in %
MAGIC_BOUNDS = tuple(r['Magic_Below'] for r in _SCALE[:-1])        # average Pwr
SMALL_RISE = rules.setting('small_rise')                           # points of chance; up to this the text says "30%+"

AILMENT_VERBS = {       # wording of the game -> effect id whose value is the chance
    'poison': 113, 'freeze': 114, 'paralyze': 115, 'cause sleep': 116, 'silence': 117,
    'stun': 118, 'instakill': 119, 'petrify': 120, 'slow': 122,
    'delay enemy turn': 54, 'cancel enemy buffs': 74,
}
SPELL_VERBS = {         # first word of a pure ailment spell -> effect id
    'Poison': 113, 'Freeze': 114, 'Paralyze': 115, 'Put': 116, 'Silence': 117,
    'Stun': 118, 'Instakill': 119, 'Petrify': 120, 'Slow': 122,
}
AILMENT_NOUNS = {'instakill': 119}      # "Low chance of instakill."
AILMENT_IDS = set(AILMENT_VERBS.values())
# Effects that leave the power table as the measure of one hit. Every id here is named, with its
# evidence, in EFFECT_NAMES of extract_vanilla.py (a test holds this). They are: the plain hit, accuracy,
# chances of side effects, HP/TP absorb, the number of hits or targets, who can be hit, stat changes
# on the target, and conditions the sentence itself states (RES-based, ignores defense, critical hit,
# bonus against a kind of enemy or with a weapon).
SAFE_EFFECTS = {0, POWER_PHYS, POWER_MAGIC, 29, 55, 72, 75, 76, 137,                     # hit, accuracy, absorb, targets
                31, 70, 110, 125,                                                        # critical hits
                90, 92, 93, 94, 95, 96, 97, 99, 136,                                     # number of hits, falloff
                47, 69, 71, 87, 88, 111,                                                 # stated conditions
                79, 133, 161, 162, 163, 164, 165, 166, 167, 168} | AILMENT_IDS          # effects on the target
# Not here on purpose: 73 (damage tied to base attack, formula not known), 138 and 199 (damage taken from
# the target's max HP), 8 (fixed damage), 146 and 147 (the damage belongs to the summoned unit).

VANILLA_WORDS = ('tremendous', 'enormous', 'powerful')
DAMAGE_KINDS = ('bash', 'bashing', 'slash', 'stab', 'fire', 'water', 'lightning', 'wind', 'earth',
                'non-elemental', 'mid-range', 'long-range', 'RES-based', 'defense-piercing')
ALL_DAMAGE_WORDS = DAMAGE_WORDS + (OUT_OF_SCALE,)
DAMAGE_WORD_RE = re.compile(r'\b(' + '|'.join(ALL_DAMAGE_WORDS + VANILLA_WORDS) + r')\b', re.I)
CHANCE = r'\((?P<chance>\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?%\+?)\)'
MAY_RE = re.compile(r'May (?P<verbs>[a-z/ ]+?)(?: ' + CHANCE + r')?\.')
NOUN_RE = re.compile(r'chance of (?P<noun>[a-z]+)(?: ' + CHANCE + r')?\.')
SPELL_RE = re.compile(r'^(?P<verb>[A-Z][a-z]+) [^.()]*?(?: ' + CHANCE + r')?\.$')
CHANCE_NOTE_RE = re.compile(r' ' + CHANCE)

# Sentences that name no damage at all: where the word goes was decided by hand.
TEMPLATES = rules.pairs('Line1Templates', 'Vanilla_Phrase', 'With_Damage_Word')


# ---------------------------------------------------------------------------
# What the binary says
# ---------------------------------------------------------------------------
def tier(value, bounds, words, beyond):
    for bound, word in zip(bounds, words):
        if value < bound:
            return word
    return beyond


def damage_basis(slots):
    """('physical' | 'magic', average shown value) of a skill, or (None, reason) when no word can be given.
    slots: (effect id, tail, values cut to the levels of the skill)."""
    phys = [v for i, t, v in slots if i == POWER_PHYS and t == 2 and v]
    magic = [v for i, t, v in slots if i == POWER_MAGIC and v and max(v) > 1]
    if len(phys) + len(magic) != 1:
        return None, 'no single power table'
    unknown = sorted({i for i, _, _ in slots if i not in SAFE_EFFECTS and i != DAMAGE_XN})
    if unknown:
        return None, 'carries effects that are not understood: ' + ', '.join(map(str, unknown))
    multiplier = [v for i, _, v in slots if i == DAMAGE_XN and v]
    if phys and multiplier:
        # "Damage xn" in the game's table. The DT2-2 wiki lists it as the ATK multiplier of the skill
        # (Spiral Arrow 330% -> 400%), so it is the measure of the hit.
        return 'physical', statistics.mean(100 * v for v in multiplier[0])
    if phys:
        return 'physical', statistics.mean(100 * (1 + v) for v in phys[0])
    return 'magic', statistics.mean(magic[0])


def damage_word(slots):
    kind, value = damage_basis(slots)
    if kind is None:
        return None
    return tier(value, PHYS_BOUNDS if kind == 'physical' else MAGIC_BOUNDS, DAMAGE_WORDS, OUT_OF_SCALE)


def pct(value):
    return f'{round(100 * value, 1):g}'


def chance_text(slots, effect_ids):
    """'25%', '30%+', '20-50%' or '100%' for the ailments named in a sentence. None when it cannot be said
    in one figure: an ailment is missing, falls with the level, or the ailments differ."""
    texts = set()
    for effect_id in effect_ids:
        tables = [v for i, _, v in slots if i == effect_id and v]
        if len(tables) != 1:
            return None
        values = [min(round(100 * v, 1), 100) for v in tables[0]]
        if min(values) <= 0 or values != sorted(values):
            return None
        first, last = values[0], values[-1]
        if first == last:
            texts.add(f'{first:g}%')
        elif last - first <= SMALL_RISE:
            texts.add(f'{first:g}%+')
        else:
            texts.add(f'{first:g}-{last:g}%')
    return texts.pop() if len(texts) == 1 else None


def verbs_to_ids(verbs):
    parts = verbs.split('/')
    return [AILMENT_VERBS[p] for p in parts] if all(p in AILMENT_VERBS for p in parts) else None


def chance_claims(desc):
    """(effect ids, stated chance or None, position where a chance note belongs) for every place of a
    sentence that speaks of an ailment chance."""
    claims = []
    for m in MAY_RE.finditer(desc):
        ids = verbs_to_ids(m.group('verbs'))
        if ids:
            claims.append((ids, m.group('chance'), m.start() + len('May ') + len(m.group('verbs'))))
    for m in NOUN_RE.finditer(desc):
        if m.group('noun') in AILMENT_NOUNS:
            claims.append(([AILMENT_NOUNS[m.group('noun')]], m.group('chance'), m.start() + len('chance of ') + len(m.group('noun'))))
    m = SPELL_RE.match(desc)
    if m and not claims and m.group('verb') in SPELL_VERBS and 'chance' not in desc:
        end = m.start('chance') - 2 if m.group('chance') else len(desc) - 1
        claims.append(([SPELL_VERBS[m.group('verb')]], m.group('chance'), end))
    return claims


# ---------------------------------------------------------------------------
# Writing it into the sentence
# ---------------------------------------------------------------------------
def with_case(word, original):
    return word.capitalize() if original[:1].isupper() else word


def put_damage_word(desc, word):
    """Returns the sentence with the damage word, or None when no rule knows where it goes."""
    m = DAMAGE_WORD_RE.search(desc)
    if m:                                                   # the game already grades it: use our scale
        new = with_case(word, m.group(0))
        head = desc[:m.start()]
        if head.endswith('an ') and new[0] not in 'aeiou':
            head = head[:-3] + 'a '
        elif head.endswith('a ') and new[0] in 'aeiou':
            head = head[:-2] + 'an '
        return head + new + desc[m.end():]
    for sentence, template in TEMPLATES.items():
        if sentence in desc:
            return desc.replace(sentence, template.format(w=word))
    pos = desc.find('damage')
    if pos > 0:                                             # "Deal bash damage" -> "Deal minor bash damage"
        start = pos
        while True:
            before = desc[:start].rstrip()
            last = before.split(' ')[-1]
            if last.lower() not in [k.lower() for k in DAMAGE_KINDS]:
                break
            start = len(before) - len(last)
        at_sentence_start = start == 0 or desc[:start].rstrip().endswith('.')
        if at_sentence_start:       # "Lightning damage" -> "Minor lightning damage"
            rest = desc[start:]
            keep = rest.split(' ')[0] in ('RES-based',)
            return desc[:start] + word.capitalize() + ' ' + (rest if keep else rest[0].lower() + rest[1:])
        return desc[:start] + word + ' ' + desc[start:]
    m = re.search(r'\bAttack (?=(one enemy|an enemy)\b)', desc)
    if m:                                                   # "Attack one enemy" -> "Deal minor damage to one enemy"
        return desc[:m.start()] + f'Deal {word} damage to ' + desc[m.end():]
    m = re.search(r'\bAttack ', desc)
    if m:
        return desc[:m.start()] + f'Deal {word} damage ' + desc[m.end():]
    return None


def put_chances(desc, slots):
    """'May stun.' -> 'May stun (30%+).'; 'Stun one enemy.' -> 'Stun one enemy (65%+).'
    Returns (text, notes)."""
    notes, text = [], desc
    for ids, stated, pos in sorted(chance_claims(desc), key=lambda c: -c[2]):
        if stated:
            continue
        chance = chance_text(slots, ids)
        if chance:
            text = text[:pos] + f' ({chance})' + text[pos:]
        elif all(any(i == effect_id for i, _, _ in slots) for effect_id in ids):
            notes.append('chance not stated: the ailments of this sentence have different chances, or one always happens')
    return text, notes


def propose(desc, slots, max_len):
    """Line 1 with its damage word and its ailment chances. Returns (text, notes); notes say what could not be done."""
    notes = []
    text = desc
    word = damage_word(slots)
    kind, reason = damage_basis(slots)
    if word:
        candidate = put_damage_word(desc, word)
        if candidate is None:
            notes.append(f'damage is {word} but no rule knows where to say it')
        elif len(candidate) > max_len:
            notes.append(f'damage is {word} but the sentence would be {len(candidate)} characters')
        else:
            text = candidate
    elif any(i in (POWER_PHYS, POWER_MAGIC) for i, _, _ in slots) and reason != 'no single power table':
        notes.append('no damage word: ' + reason)
    candidate, chance_notes = put_chances(text, slots)
    notes.extend(chance_notes)
    if candidate != text and len(candidate) > max_len:
        notes.append(f'chance left out: the sentence would be {len(candidate)} characters')
    else:
        text = candidate
    return text, notes


# ---------------------------------------------------------------------------
# Skills that deal no damage: how much they do
# ---------------------------------------------------------------------------
FIGURE = r'\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)?[%x]?\+?'
NOTE_RE = re.compile(r' \((?P<body>(?:[A-Za-z][A-Za-z /&-]*? )?' + FIGURE + r'(?:, (?:[A-Za-z][A-Za-z /&-]*? )?' + FIGURE + r')*)\)')
PIECE_RE = re.compile(r'^(?:(?P<label>[A-Za-z][A-Za-z /&-]*?) )?(?P<lo>\d+(?:\.\d+)?)(?:-(?P<hi>\d+(?:\.\d+)?))?(?P<unit>[%x]?)(?P<plus>\+?)$')
IGNORED_LABEL_WORDS = {'rate', 'increase', 'increases', 'decrease', 'bonus', 'amount', 'the', 'and', 'for'}


def has_power_table(slots):
    return any((i == POWER_PHYS and t == 2) or (i == POWER_MAGIC and v and max(v) > 1) for i, t, v in slots)


def figure(values, unit):
    """The three forms, for any table: '10%', '8%+', '8-18%'. values are the magnitudes as shown."""
    shown = [abs(round(v, 2)) for v in values]
    first, last = shown[0], shown[-1]
    if all(v == first for v in shown):
        return f'{first:g}{unit}'
    if unit == '%' and 0 < last - first <= SMALL_RISE:
        return f'{first:g}%+'
    return f'{first:g}-{last:g}{unit}'


def label_words(label):
    return [w for w in re.findall(r'[A-Za-z]+', label.lower()) if w not in IGNORED_LABEL_WORDS]


def label_is_said(label, sentence, fully=True):
    """The sentence already names what the figure measures: all the words of the label, or at least one."""
    said = [w[:5] in sentence.lower() for w in label_words(label)]
    return all(said) if fully else any(said)


def put_values(desc, effects, max_len):
    """effects: (label, values as shown, unit) of the skill, in the order of its box.
    Returns (text, notes)."""
    if not effects:
        return desc, []
    stem, dot = (desc[:-1], '.') if desc.endswith('.') else (desc, '')
    labelled = ', '.join(f'{label} {figure(values, unit)}' for label, values, unit in effects)
    bare = figure(effects[0][1], effects[0][2])
    if len(effects) == 1 and label_is_said(effects[0][0], desc):
        candidates = [bare]
    elif len(effects) == 1 and label_is_said(effects[0][0], desc, fully=False):
        candidates = [labelled, bare]        # the label when it fits; the sentence names it well enough otherwise
    else:
        candidates = [labelled]
    for body in candidates:
        text = f'{stem} ({body}){dot}'
        if len(text) <= max_len:
            return text, []
    return desc, [f'values left out: the sentence would be {len(stem) + len(candidates[-1]) + 3 + len(dot)} characters']


def value_matches(piece, tables):
    """A figure of line 1 must be one of the tables of the skill, in the form the rule gives it."""
    m = PIECE_RE.match(piece)
    if not m:
        return False
    lo, hi = float(m.group('lo')), float(m.group('hi')) if m.group('hi') else None
    for values in tables:
        for shown in ([abs(v) for v in values], [abs(100 * v) for v in values], [abs(100 * (1 + v)) for v in values]):
            shown = [round(v, 2) for v in shown]
            first, last = shown[0], shown[-1]
            if hi is not None:
                ok = first == lo and last == hi
            elif m.group('plus'):
                ok = first == lo and 0 < last - first <= SMALL_RISE
            else:
                ok = all(v == lo for v in shown)
            if ok:
                return True
    return False


# ---------------------------------------------------------------------------
# Checking a sentence against the binary
# ---------------------------------------------------------------------------
def strip_chances(desc, vanilla_desc=''):
    """Line 1 without its figures in parentheses: what is left must carry no figure the game did not write."""
    return NOTE_RE.sub(lambda m: m.group(0) if m.group(0) in vanilla_desc else '', desc)


def check_line1(desc, vanilla_desc, slots, other_tables=()):
    """Every damage word and every chance of line 1 must be what the binary gives. Returns (problems, verified)."""
    problems, verified = [], 0
    stated = [w.lower() for w in DAMAGE_WORD_RE.findall(desc)]
    kept = [w.lower() for w in DAMAGE_WORD_RE.findall(vanilla_desc)]
    expected = damage_word(slots)
    for word in stated:
        if word == expected:
            verified += 1
        elif not (expected is None and word in kept):       # the game's own wording on an ungraded skill
            problems.append(f"'{desc}': says {word} damage, the binary gives {expected or 'no grade'}")
    claims = chance_claims(desc)
    for ids, chance, _ in claims:
        if chance is None:
            continue
        expected_chance = chance_text(slots, ids)
        if chance == expected_chance:
            verified += 1
        else:
            problems.append(f"'{desc}': says ({chance}), the binary gives {expected_chance or 'no single chance'}")
    chances = [chance for _, chance, _ in claims if chance]
    tables = [v for _, _, v in slots if v] + [list(v) for v in other_tables if v]
    for m in NOTE_RE.finditer(desc):
        if m.group(0) in vanilla_desc or m.group('body') in chances:
            continue
        for piece in m.group('body').split(', '):
            if value_matches(piece, tables):
                verified += 1
            else:
                problems.append(f"'{desc}': ({piece}) is not a table of this skill in the form the rule gives it")
    return problems, verified
