"""
QoL skill text: proposes the level-up lines of the QoL variant (base game values,
nothing rebalanced) and keeps them in a workbook that is edited by hand.

    python mod_project/tools/generate_qol_skill_text.py

Workbook: mod_project/data_tables/qol_skill_text.xlsx
  * QoL_Desc / QoL_LvUp are the texts the build uses. Edit them freely.
  * Put "yes" in the Edited column to keep your wording; this script then leaves
    that row alone. Rows without it are regenerated on every run.
  * Every number comes from data_tables/vanilla_source_of_truth.xlsx. Numbers in
    edited rows are checked against the binary by the build and by the tests.

Style: docs/SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md (the user's standard)
  Line 1  vanilla description, untouched
  Line 2  what the skill does, level by level:  ATK: 125% -> 134 -> 143 -> ... -> 200%
  Line 3  what it costs:                        Turns | TP Cost | Speed
  Allowed forms only: one value per level; base + exact step for a linear table
  ("ATK: 130% (+8%/Lv) -> 202% (L10 Max)"); first -> last for durations and speed.
  Never an average. What does not fit is left out and listed in the Left_Out column.
"""
import os
import re
import sys
import itertools
import collections
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
SOURCE_PATH = os.path.join(TABLES_DIR, 'vanilla_source_of_truth.xlsx')
PREVIOUS_PATH = os.path.join(TABLES_DIR, 'skills.xlsx')
OUTPUT_PATH = os.path.join(TABLES_DIR, 'qol_skill_text.xlsx')

MAX_LINE = 85        # measured on screen
MAX_BOX_LINES = 3    # description + level-up lines
SEP = ' | '
HEADERS = ['Category', 'Filename', 'Skill_Name', 'Levels', 'Vanilla_Desc', 'Vanilla_LvUp', 'QoL_Desc', 'QoL_LvUp',
           'Edited', 'Coverage', 'Phrases_Kept_As_Vanilla', 'Tables_Not_Shown', 'Not_Level_By_Level', 'Left_Out',
           'Previous_Mod_Desc', 'Previous_Mod_LvUp']

# Effect ids whose meaning is established (see the Effects sheet of the source of truth).
POWER_PHYS = 26      # damage = 100% + value
POWER_MAGIC = 1      # magic power
ACCURACY_PHYS = 29   # paired with "Accuracy UP" in every technique that has both
AILMENT_IDS = collections.OrderedDict([
    ('Poison', 113), ('Freeze', 114), ('Paralysis', 115), ('Sleep', 116), ('Silence', 117),
    ('Stun', 118), ('Instakill', 119), ('Petrify', 120), ('Slow', 122),
])
EFFECT_STEMS = {            # vanilla phrase -> (effect id, label), verified effects only
    'HP absorption rate': (75, 'HP Absorb'),
    'TP absorption rate': (76, 'TP Absorb'),
    'Number of enemies attacked': (137, 'Targets'),
    'Recovery cap': (295, 'Heal Cap'),
}
NO_GUESS_STEMS = ('Damage', 'Magic damage')   # their unit depends on the effect behind them
ARRAY_STEMS = {             # vanilla phrase -> per-level array of the skill header
    'TP Cost': 'tp_cost',
    'Time until next turn': 'speed',
    'Chant time': 'cast',
    'Chant speed': 'cast',
    'Duration': 'turns',
}
# array -> (label, number style), in the order of the cost line
ARRAY_LABELS = collections.OrderedDict([
    ('turns', ('Turns', 'num')),
    ('tp_cost', ('TP Cost', 'num')),
    ('speed', ('Speed', 'mult')),
    ('cast', ('Chant', 'mult')),
])
COST_KINDS = {'Turns': 'turns', 'TP Cost': 'tp', 'Speed': 'speed', 'Chant': 'chant'}


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
def load_skills():
    wb = openpyxl.load_workbook(SOURCE_PATH)
    skills = collections.OrderedDict()
    for r in wb['Skills'].iter_rows(min_row=2, values_only=True):
        skills[(r[0], r[1])] = {
            'category': r[0], 'fn': r[1], 'name': r[3], 'levels': r[4],
            'desc': r[17] or '', 'lvup': r[18] or '', 'arrays': {}, 'slots': [],
        }
    for r in wb['SkillLevels'].iter_rows(min_row=2, values_only=True):
        s = skills[(r[0], r[1])]
        values = [0 if v is None else v for v in r[10:10 + s['levels']]]
        if r[5].startswith('effect'):
            s['slots'].append({'key': r[5], 'id': r[6], 'tail': r[8], 'values': values})
        else:
            s['arrays'][r[5]] = values
    uniques = []
    for r in wb['UniqueSkills'].iter_rows(min_row=2, values_only=True):
        uniques.append({'category': 'Unique', 'fn': r[0], 'name': r[2], 'values': list(r[4:14]), 'desc': r[21] or ''})
    return list(skills.values()), uniques


def load_previous_mod():
    """Wording of the earlier mod, shown next to the proposal as a reference for hand edits."""
    if not os.path.exists(PREVIOUS_PATH):
        return {}
    ws = openpyxl.load_workbook(PREVIOUS_PATH)['Skills']
    return {(r[1], r[2]): (r[8] or '', r[9] or '') for r in ws.iter_rows(min_row=2, values_only=True) if r[1]}


def load_edited_rows():
    """Rows the user marked as Edited keep their text."""
    if not os.path.exists(OUTPUT_PATH):
        return {}
    ws = openpyxl.load_workbook(OUTPUT_PATH)['Skills']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Category', 'Filename', 'QoL_Desc', 'QoL_LvUp', 'Edited') if name in header}
    if len(col) < 5:
        return {}
    edited = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if str(r[col['Edited']] or '').strip().lower() in ('yes', 'y', 'true', '1', 'x'):
            edited[(r[col['Category']], r[col['Filename']])] = (r[col['QoL_Desc']] or '', r[col['QoL_LvUp']] or '')
    return edited


# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------
def num(v):
    v = round(v, 2)
    return str(int(v)) if v == int(v) else f'{v:g}'


def is_fraction(values):
    """Floats in a small range are rates; integers are flat amounts."""
    return any(isinstance(v, float) for v in values) and all(abs(v) <= 5 for v in values)


STYLES = {   # style -> (transform, unit, show the sign)
    'power': (lambda v: 100 * (1 + v), '%', False),
    'pct': (lambda v: 100 * v, '%', False),
    'abs_pct': (lambda v: 100 * abs(v), '%', False),
    'neg_pct': (lambda v: -100 * v, '%', False),
    'signed_pct': (lambda v: 100 * v, '%', True),
    'plus_pct': (lambda v: 100 * abs(v), '%', True),      # "ATK: +8%"
    'minus_pct': (lambda v: -100 * abs(v), '%', False),   # "DEF: -11%"
    'num': (lambda v: v, '', False),
    'abs_num': (lambda v: abs(v), '', False),
    'neg_num': (lambda v: -v, '', False),
    # Resistance is stored in points where 100 is immunity: one point is 1% of the damage taken.
    'num_pct': (lambda v: v, '%', False),
    'abs_num_pct': (lambda v: abs(v), '%', False),
    'neg_num_pct': (lambda v: -v, '%', False),
    'mult': (lambda v: v, 'x', False),
}


class Segment:
    """One 'Label: values' piece of a line, or a piece of vanilla wording kept as is."""

    def __init__(self, label, values=None, style='num', group='A', extra=False, text=None):
        self.label, self.values, self.style, self.group, self.extra, self.text = label, values, style, group, extra, text

    def is_data(self):
        return self.text is None

    def shown(self):
        return [round(STYLES[self.style][0](v), 2) for v in self.values]

    def is_constant(self):
        return len(set(self.shown())) == 1

    def is_linear(self):
        shown = self.shown()
        diffs = {round(b - a, 2) for a, b in zip(shown, shown[1:])}
        return len(shown) >= 3 and len(diffs) == 1

    def step_bounds(self):
        """(smallest, largest) rise per level when the table always rises but not evenly; else None."""
        shown = self.shown()
        diffs = [round(b - a, 2) for a, b in zip(shown, shown[1:])]
        if len(shown) < 3 or min(diffs) <= 0 or min(diffs) == max(diffs):
            return None
        return min(diffs), max(diffs)

    def kind(self):
        if not self.is_data():
            return 'text'
        return COST_KINDS.get(self.label, 'effect') if self.group == 'B' else 'effect'

    def modes(self, main=False):
        """Ways the specification allows this table to be printed, best first.

        list    one value per level                    10% -> 12 -> 13 -> ... -> 20%
        step    base, exact step [and cap]             38 (+4/Lv) -> 74        same step at every level
        srange  base, bounds of the step, cap          10% (+1-2%/Lv) -> 20%   step changes between levels
        ends    first -> last                          0.65x -> 0.75x
        drop    left out of the box
        """
        kind = self.kind()
        if kind == 'text':
            return ['text', 'drop']
        if self.is_constant():
            return ['const'] if main else ['const', 'drop']
        if len(self.values) == 2:
            return ['list'] if main or kind == 'tp' else ['list', 'drop']
        if kind in ('speed', 'chant'):
            return ['ends', 'drop']
        if kind == 'turns':
            return ['list', 'ends', 'drop']
        modes = ['list'] + (['step'] if self.is_linear() else ['srange'] if self.step_bounds() else []) + ['ends']
        return modes if main or kind == 'tp' else modes + ['drop']

    def cost(self, mode, main=False):
        """What the player loses when the table is printed this way (0 = nothing).

        Rule agreed with the user: every effect of the skill stays in the box. The main
        effect is shown level by level; to make room, the TP cost and the secondary
        effects turn into base + step, and speed and chant are the first to go.
        """
        kind = self.kind()
        if mode == 'drop':
            if kind in ('speed', 'chant'):
                return 1
            return {'turns': 4, 'text': 3}.get(kind, 8)
        if mode == 'ends':
            if kind in ('speed', 'chant'):
                return 0
            if kind == 'turns':
                return 1
            return 100 if main else 6 if kind == 'tp' else 2.5
        if mode == 'step':     # exact, but the player has to add
            return 2 if main else 1
        if mode == 'srange':   # bounds of the step: true, less precise than the list
            return 3 if main else 2.5 if kind == 'tp' else 1.2
        return 0

    def render(self, mode, main=False, levels=None):
        if mode == 'text':
            return self.text
        _, unit, signed = STYLES[self.style]
        shown = self.shown()

        def one(v, with_unit=True):
            return ('+' if signed and v > 0 else '') + num(v) + (unit if with_unit else '')

        if mode == 'const':
            return f'{self.label}: {one(shown[0])}'
        if mode == 'list':
            if len(shown) <= 5:
                body = ' -> '.join(one(v) for v in shown)
                return f'{self.label}: {body}' + (f' (L1-{levels} Max)' if main and levels else '')
            return f'{self.label}: ' + ' -> '.join(
                [one(shown[0])] + [one(v, False) for v in shown[1:-1]] + [one(shown[-1])])
        if mode == 'ends':
            return f'{self.label}: {one(shown[0])} -> {one(shown[-1])}'
        if mode == 'srange':   # the step changes between levels: give its real bounds, never an average
            lo, hi = self.step_bounds()
            note = f'+{num(lo)}-{num(hi)}{unit}/Lv'
            return f'{self.label}: {one(shown[0])} ({note}) -> {one(shown[-1])}'
        step = shown[1] - shown[0]
        note = ('+' if step >= 0 else '') + num(step) + unit + '/Lv'
        if main or self.kind() == 'tp':
            return (f'{self.label}: {one(shown[0])} ({note}) -> {one(shown[-1])}'
                    + (f' (L{levels} Max)' if main and levels else ''))
        return f'{self.label}: {one(shown[0])} ({note})'


# ---------------------------------------------------------------------------
# Vanilla phrase parsing and matching
# ---------------------------------------------------------------------------
def split_phrases(lvup):
    text = lvup.replace('\n', ' ').strip()
    if not text.startswith('LvUp:'):
        return None
    phrases = []
    for raw in re.findall(r'.*?\b(?:UP|DOWN)\b', text[5:]):
        raw = raw.strip()
        # "Can cure poison > paralysis > ... TP Cost UP": the lead-in is plain text.
        m = re.match(r'^(.*\S)\s+(TP Cost (?:UP|DOWN))$', raw)
        if m and m.group(1):
            phrases += [m.group(1), m.group(2)]
        else:
            phrases.append(raw)
    return phrases


def stem_of(phrase):
    m = re.match(r'^(.*)\s+(UP|DOWN)$', phrase)
    return (m.group(1), m.group(2)) if m else (None, None)


def varies(values):
    return len(set(values)) > 1


def generic_style(stem, values, direction='UP'):
    wording = re.search(r'decrease|reduc', stem, re.I)
    lowering = all(v <= 0 for v in values) and wording
    # "Interruption rate DOWN" stores how much is taken off: show it as a negative amount.
    taken_off = direction == 'DOWN' and not wording and all(v >= 0 for v in values)
    if not is_fraction(values):
        style = 'abs_num' if lowering else 'neg_num' if taken_off else 'num'
        return style + '_pct' if re.search(r'resistance', stem, re.I) else style
    if lowering:
        return 'abs_pct'
    if taken_off:
        return 'neg_pct'
    return 'signed_pct' if any(v < 0 for v in values) else 'pct'


def literal(text):
    if text.startswith('Can cure '):
        text = 'Cures: ' + text[len('Can cure '):]
    return Segment(None, text=text)


def build_segments(skill):
    """Returns (segments, unresolved phrases, per-level tables left unexplained)."""
    phrases = split_phrases(skill['lvup']) or []
    arrays, slots = skill['arrays'], skill['slots']
    magic = skill['category'] == 'Magic'
    used = set()          # array names and slot keys already shown
    resolved = {}         # phrase index -> [Segment]

    def slot_by_id(eff_id, tail=None):
        for sl in slots:
            if sl['id'] == eff_id and sl['key'] not in used and (tail is None or sl['tail'] == tail):
                return sl
        return None

    def array_segment(name, extra=False):
        label, style = ARRAY_LABELS[name]
        return Segment(label, arrays[name], style, group='B', extra=extra)

    # 1. Phrases whose table is known for certain.
    for idx, phrase in enumerate(phrases):
        stem, direction = stem_of(phrase)
        if stem is None:
            continue
        if stem in ARRAY_STEMS:
            name = ARRAY_STEMS[stem]
            if name in arrays and varies(arrays[name]) and name not in used:
                resolved[idx] = [array_segment(name)]
                used.add(name)
        elif stem in ('Damage', 'Magic damage'):
            sl = slot_by_id(POWER_MAGIC) if magic else slot_by_id(POWER_PHYS, tail=2)
            if sl and varies(sl['values']):
                resolved[idx] = [Segment('Pwr', sl['values'], 'num') if magic else Segment('ATK', sl['values'], 'power')]
                used.add(sl['key'])
        elif stem in ('Accuracy', 'Magic accuracy'):
            if magic and 'arr_0xFC' in arrays and varies(arrays['arr_0xFC']) and 'arr_0xFC' not in used:
                resolved[idx] = [Segment('Accuracy', arrays['arr_0xFC'], 'pct')]
                used.add('arr_0xFC')
            elif not magic:
                sl = slot_by_id(ACCURACY_PHYS)
                if sl and varies(sl['values']):
                    resolved[idx] = [Segment('Accuracy', sl['values'], 'signed_pct')]
                    used.add(sl['key'])
        elif stem in EFFECT_STEMS:
            eff_id, label = EFFECT_STEMS[stem]
            sl = slot_by_id(eff_id)
            if sl and varies(sl['values']):
                resolved[idx] = [Segment(label, sl['values'], generic_style(stem, sl['values'], direction))]
                used.add(sl['key'])
        else:
            m = re.match(r'^([A-Za-z]+(?:/[A-Za-z]+)*) rate$', stem)
            if m and all(a in AILMENT_IDS for a in m.group(1).split('/')):
                names = m.group(1).split('/')
                found = [slot_by_id(AILMENT_IDS[a]) for a in names]
                if all(found) and any(varies(f['values']) for f in found):
                    resolved[idx] = [Segment(a, f['values'], 'pct') for a, f in zip(names, found)]
                    used.update(f['key'] for f in found)

    # 2. What is left: phrases without a table, and level-dependent tables without a phrase.
    open_phrases = [i for i, p in enumerate(phrases) if i not in resolved and stem_of(p)[0] is not None]
    open_series = [(n, v) for n, v in arrays.items() if n not in used and n != 'sp_cost' and varies(v)]
    open_series += [(sl['key'], sl['values']) for sl in slots if sl['key'] not in used and varies(sl['values'])]
    slot_series = [s for s in open_series if s[0].startswith('effect')]

    def take(idx, key, values):
        stem, direction = stem_of(phrases[idx])
        label, style = stem, generic_style(stem, values, direction)
        # "ATK increase UP" -> "ATK: +8%", "DEF decrease UP" -> "DEF: -11%" (the approved mockups),
        # unless the short label is one the cost line already uses.
        m = re.match(r'^(.*\S) (increases?|decrease)$', stem)
        if m and is_fraction(values) and m.group(1) not in COST_KINDS:
            label = m.group(1)
            style = 'plus_pct' if m.group(2).startswith('increase') else 'minus_pct'
        resolved[idx] = [Segment(label, values, style)]
        used.add(key)

    while True:
        phr = [i for i in open_phrases if i not in resolved]
        ser = [x for x in slot_series if x[0] not in used]
        if not phr or len(phr) != len(ser):
            break
        guessable = [i for i in phr if stem_of(phrases[i])[0] not in NO_GUESS_STEMS]
        if len(phr) == 1:
            # One unexplained phrase and one unexplained effect table: they belong together.
            if guessable:
                take(phr[0], *ser[0])
            break
        # "X decrease UP" against the only table holding negative values.
        dec = [i for i in guessable if re.search(r'decrease', phrases[i], re.I)]
        neg = [x for x in ser if all(v <= 0 for v in x[1])]
        if len(dec) == 1 and len(neg) == 1:
            take(dec[0], *neg[0])
            continue
        break

    segments, unresolved = [], []
    for idx, phrase in enumerate(phrases):
        if idx in resolved:
            segments.extend(resolved[idx])
        else:
            segments.append(literal(phrase))
            if stem_of(phrase)[0] is not None:
                unresolved.append(phrase)

    # 3. Extras: known tables that no phrase mentions.
    damage_open = any(stem_of(p)[0] in NO_GUESS_STEMS for p in unresolved)
    sl = None if magic or damage_open else slot_by_id(POWER_PHYS, tail=2)
    if sl:
        segments.append(Segment('ATK', sl['values'], 'power', extra=True))
        used.add(sl['key'])
    sl = slot_by_id(POWER_MAGIC) if magic and not damage_open else None
    if sl and min(sl['values']) > 1:
        segments.append(Segment('Pwr', sl['values'], 'num', extra=True))
        used.add(sl['key'])
    for name, eff_id in AILMENT_IDS.items():
        sl = slot_by_id(eff_id)
        if sl and is_fraction(sl['values']):
            segments.append(Segment(name, sl['values'], 'pct', extra=True))
            used.add(sl['key'])
    if magic and 'arr_0xFC' in arrays and 'arr_0xFC' not in used and varies(arrays['arr_0xFC']):
        segments.append(Segment('Accuracy', arrays['arr_0xFC'], 'pct', extra=True))
        used.add('arr_0xFC')
    for name in ARRAY_LABELS:
        values = arrays.get(name)
        if not values or name in used or not any(values):
            continue
        if not varies(values) and (name == 'tp_cost' or values[0] == 1):
            continue   # fixed TP is already on screen; 1x is the neutral multiplier
        segments.append(array_segment(name, extra=True))
        used.add(name)

    # Effect line first, then the cost line in a fixed order.
    cost_order = [label for label, _ in ARRAY_LABELS.values()]
    cost = sorted([s for s in segments if s.group == 'B'], key=lambda s: cost_order.index(s.label))
    segments = [s for s in segments if s.group == 'A'] + cost
    hidden = [key for key, values in open_series if key not in used]
    return segments, unresolved, hidden


# ---------------------------------------------------------------------------
# Fitting into the text box
# ---------------------------------------------------------------------------
OVERFLOW_COST = 0.5   # an effect printed on the cost line


def line_fits(parts):
    return sum(len(p) for p in parts) + len(SEP) * max(len(parts) - 1, 0) <= MAX_LINE


def fit(segments, levels, max_lines):
    """Returns (lines, shortened, left out), or (None, [], []) when nothing fits.

    Line 2 is for effects and line 3 for costs. Tries every allowed way of printing
    each table and keeps the layout in which the player loses the least.
    """
    main_at = next((i for i, s in enumerate(segments) if s.kind() == 'effect'), None)
    if main_at is None:
        main_at = next((i for i, s in enumerate(segments) if s.is_data()), None)
    mode_sets = [s.modes(main=(i == main_at)) for i, s in enumerate(segments)]

    def cost(i, mode):
        return segments[i].cost(mode, main=(i == main_at))

    combos = sorted(itertools.product(*[range(len(m)) for m in mode_sets]),
                    key=lambda c: (sum(cost(i, mode_sets[i][k]) for i, k in enumerate(c)), sum(c)))
    best = None
    for combo in combos:
        base = sum(cost(i, mode_sets[i][k]) for i, k in enumerate(combo))
        if best and base >= best[0]:
            break
        chosen = [(i, mode_sets[i][k]) for i, k in enumerate(combo) if mode_sets[i][k] != 'drop']
        if not any(segments[i].is_data() for i, _ in chosen):
            continue
        parts = [(segments[i].group, segments[i].render(m, main=(i == main_at), levels=levels if levels > 1 else None))
                 for i, m in chosen]
        effects = [p for g, p in parts if g == 'A']
        costs = [p for g, p in parts if g == 'B']
        # (lines, penalty): effects on line 2 and costs on line 3; an effect that does not fit
        # on line 2 may open line 3 at a small price, and a box with only one kind may use both.
        if max_lines < 2:
            layouts = [([effects + costs], 0)]
        elif effects and costs:
            layouts = [([effects[:cut], effects[cut:] + costs], OVERFLOW_COST * (len(effects) - cut))
                       for cut in range(len(effects), 0, -1)]
        else:
            only = effects or costs
            layouts = [([only], 0)] + [([only[:cut], only[cut:]], 0) for cut in range(len(only) - 1, 0, -1)]
        for lines, penalty in layouts:
            if all(line_fits(line) for line in lines) and (best is None or base + penalty < best[0]):
                shortened = [segments[i].label for i, k in enumerate(combo)
                             if mode_sets[i][k] in ('ends', 'srange') and cost(i, mode_sets[i][k])]
                left_out = [segments[i].label or segments[i].text for i, k in enumerate(combo)
                            if mode_sets[i][k] == 'drop']
                best = (base + penalty, [SEP.join(line) for line in lines], shortened, left_out)
                break
    if best is None:
        return None, [], []
    lines = best[1]
    # A long main list says where it ends when there is room: "... -> 520 (L10)"
    main = segments[main_at] if main_at is not None else None
    if main and main.kind() == 'effect' and levels > 5:
        head = lines[0].split(SEP)[0]
        if head.count(' -> ') == levels - 1 and len(lines[0]) + len(f' (L{levels})') <= MAX_LINE:
            lines[0] = head + f' (L{levels})' + lines[0][len(head):]
    return lines, best[2], best[3]


def generate_skill(skill):
    row = {'coverage': 'Unchanged', 'lvup': skill['lvup'], 'unresolved': [], 'hidden': [],
           'shortened': [], 'left_out': []}
    if skill['lvup'].startswith('dummy'):
        row['coverage'] = 'Skipped (internal)'
        return row
    segments, unresolved, hidden = build_segments(skill)
    row['unresolved'], row['hidden'] = unresolved, hidden
    if not any(s.is_data() for s in segments):
        return row    # nothing to add: keep the vanilla text byte for byte
    lines, shortened, left_out = fit(segments, skill['levels'], MAX_BOX_LINES - len(skill['desc'].split('\n')))
    if lines is None:
        row['coverage'] = 'ERROR: does not fit'
        return row
    row['lvup'], row['shortened'], row['left_out'] = '\n'.join(lines), shortened, left_out
    row['coverage'] = 'Partial' if unresolved else 'Full'
    return row


def generate_unique(unique):
    values = unique['values']
    style = 'pct' if is_fraction(values) else 'num'
    if style == 'pct' and any(v < 0 for v in values):
        style = 'signed_pct'
    levels = Segment('Lv1-9', values[:9], style)
    crown = Segment('Crown EX', values[9:], style)
    line = levels.render('const' if levels.is_constant() else 'list') + SEP + crown.render('const')
    return unique['desc'] + '\n' + line


# ---------------------------------------------------------------------------
# Checks and output
# ---------------------------------------------------------------------------
def check_box(name, vanilla_desc, desc, lvup, problems):
    lines = desc.split('\n') + (lvup.split('\n') if lvup else [])
    if len(lines) > MAX_BOX_LINES:
        problems.append(f"{name}: {len(lines)} lines")
    added = lines[len(vanilla_desc.split('\n')):] if desc.startswith(vanilla_desc) else lines
    for line in added:
        if len(line) > MAX_LINE:
            problems.append(f"{name}: line of {len(line)} chars: '{line}'")
    if '~' in desc + lvup:
        problems.append(f"{name}: contains tilde")
    try:
        (desc + lvup).encode('latin-1')
    except UnicodeEncodeError:
        problems.append(f"{name}: not encodable for the game")


def add_sheet(wb, title, headers, rows):
    ws = wb.create_sheet(title)
    ws.append(headers)
    hdr_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    hdr_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row in rows:
        ws.append(row)
    ws.freeze_panes = 'A2'
    for col_num, header in enumerate(headers, 1):
        sample = [max(len(l) for l in str(r[col_num - 1]).split('\n')) for r in rows[:400] if r[col_num - 1] is not None]
        ws.column_dimensions[get_column_letter(col_num)].width = min(max([len(str(header))] + sample) + 2, 90)
    return ws


def main():
    print("=== Proposing QoL skill text from the vanilla source of truth ===")
    if not os.path.exists(SOURCE_PATH):
        print(f"Error: {SOURCE_PATH} not found. Run tools/extract_vanilla.py first.")
        sys.exit(1)
    skills, uniques = load_skills()
    previous, edited = load_previous_mod(), load_edited_rows()

    problems, rows = [], []
    coverage = collections.Counter()
    for skill in skills:
        key = (skill['category'], skill['fn'])
        row = generate_skill(skill)
        desc, lvup, flag = skill['desc'], row['lvup'], ''
        if key in edited:
            desc, lvup = edited[key]
            flag, row['coverage'] = 'yes', 'Edited by hand'
        coverage[(skill['category'], row['coverage'])] += 1
        if row['coverage'].startswith('ERROR'):
            problems.append(f"{skill['name']}: proposed text does not fit in {MAX_BOX_LINES} lines")
        check_box(skill['name'], skill['desc'], desc, lvup, problems)
        prev = previous.get(key, ('', ''))
        rows.append([skill['category'], skill['fn'], skill['name'], skill['levels'], skill['desc'], skill['lvup'],
                     desc, lvup, flag, row['coverage'], '; '.join(row['unresolved']), ', '.join(row['hidden']),
                     ', '.join(row['shortened']), ', '.join(row['left_out']), prev[0], prev[1]])
    for unique in uniques:
        key = ('Unique', unique['fn'])
        desc = generate_unique(unique)
        flag, kind = '', 'Full'
        if key in edited:
            desc, flag, kind = edited[key][0], 'yes', 'Edited by hand'
        coverage[('Unique', kind)] += 1
        check_box(unique['name'], unique['desc'], desc, '', problems)
        prev = previous.get(key, ('', ''))
        rows.append(['Unique', unique['fn'], unique['name'], 10, unique['desc'], '', desc, '', flag, kind, '', '',
                     '', '', prev[0], prev[1]])

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    add_sheet(wb, 'Skills', HEADERS, rows)
    cats = ['Technique', 'Magic', 'Passive', 'Unique']
    kinds = sorted({k for _, k in coverage})
    add_sheet(wb, 'Summary', ['Coverage'] + cats + ['Total'],
              [[k] + [coverage[(c, k)] for c in cats] + [sum(coverage[(c, k)] for c in cats)] for k in kinds])
    add_sheet(wb, 'How to edit', ['Topic', 'Detail'], [
        ['Editable columns', 'QoL_Desc and QoL_LvUp. The build uses exactly what is written there.'],
        ['Keep your wording', 'Write "yes" in Edited. Rows without it are regenerated by generate_qol_skill_text.py.'],
        ['Numbers', 'Checked against the binary by build_variant.py and the tests: a wrong figure stops the build.'],
        ['Limits', f'{MAX_BOX_LINES} lines per box (description included), {MAX_LINE} characters per line, no tilde.'],
        ['Standard', 'docs/SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md. Line 1 vanilla, line 2 effect, line 3 costs.'],
        ['Notation', 'ATK: 125% -> 134 -> ... -> 200%  |  ATK: 130% (+8%/Lv) -> 202% (L10 Max)  |  Speed: 0.8x -> 0.9x'],
        ['Never', 'Averages such as "(avg +3.33%/Lv)". A step is written only when it is the same at every level.'],
        ['Previous_Mod_*', 'Wording of the earlier mod, for reference only. Its numbers were not taken from the binary.'],
    ])
    wb.save(OUTPUT_PATH)

    print(f"    {'Coverage':<22}" + ''.join(f'{c:>11}' for c in cats))
    for k in kinds:
        print(f"    {k:<22}" + ''.join(f'{coverage[(c, k)]:>11}' for c in cats))
    print(f"Saved: {OUTPUT_PATH}")

    if problems:
        print(f"\n[FAIL] {len(problems)} text problem(s):")
        for p in problems:
            print(f"    {p}")
        sys.exit(1)
    print(f"\n[OK] {len(rows)} boxes within {MAX_BOX_LINES} lines and {MAX_LINE} characters per line.")


if __name__ == "__main__":
    main()
