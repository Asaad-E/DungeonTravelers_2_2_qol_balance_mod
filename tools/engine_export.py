"""
The snapshot the C# battle engine (engine_cs/) reads: everything the simulator of sim/ touches in a battle and in the
building of a party and its enemies, for the game as it is ("vanilla") and for the Balance variant, plus the choices of
the model (data_tables/sim_setup.xlsx). Python stays the owner of the data; the engine holds no value of the mod.

    python tools/engine_export.py [path]         writes build/engine_snapshot.json (or the path given)

A field the engine takes as a whole number is checked here: a figure with a fraction stops the export.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, HERE)

FORMAT = 1
DEFAULT_OUT = os.path.join(PROJECT, 'build', 'engine_snapshot.json')


def whole(value, what):
    """A figure the engine keeps as an int."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value == int(value):
        return int(value)
    raise ValueError(f'{what}: {value!r} is not a whole number')


def whole_list(values, what):
    return [whole(v, what) for v in values]


def num(value):
    """A number kept as it is; None stays None."""
    return value


def skill_json(s):
    return {
        'category': s.category, 'id': s.id, 'name': s.name, 'levels': whole(s.levels, 'levels'), 'target': s.target,
        'attr': s.attr, 'group': s.group, 'weapons': list(s.weapons or []),
        'effects': [[e, k, list(v)] for e, k, v in s.effects],
        'tp': whole_list(s.tp, f'tp of {s.name}'), 'sp': whole_list(s.sp, f'sp of {s.name}'), 'speed': list(s.speed),
        'cast': None if s.cast is None else list(s.cast),
        'accuracy': None if s.accuracy is None else list(s.accuracy),
        'turns': list(s.turns), 'classes': list(s.classes or []), 'range': s.range, 'chant_stat': s.chant_stat,
    }


def attack_json(a):
    return {
        'id': a.id, 'name': a.name, 'target': a.target, 'attr': a.attr, 'chant_speed': a.chant_speed,
        'accuracy': a.accuracy, 'power': a.power, 'turns': a.turns, 'speed': a.speed,
        'effects': [[e, k, v] for e, k, v in a.effects], 'range': a.range, 'passive': bool(a.passive),
        'chant_stat': a.chant_stat, 'spell': bool(a.spell),
    }


def command_json(c):
    out = {'cmd': c['cmd']}
    if 'args' in c:
        out['args'] = list(c['args'])
    if 'result' in c:
        out['result'] = c['result']
    if 'once' in c:
        out['once'] = bool(c['once'])
    if 'and' in c:
        out['and'] = command_json(c['and'])
    return out


def script_json(script):
    if not script:
        return None
    return {
        'id': script['id'],
        'opening': [command_json(c) for c in script['opening']],
        'sets': [{'set': k, 'weights': list(v['weights']), 'commands': [command_json(c) for c in v['commands']]}
                 for k, v in script['sets'].items()],
    }


def enemy_json(e):
    return {
        'id': e['id'], 'name': e['name'], 'race': e['race'], 'flags': e['flags'], 'swing': e['swing'],
        'weight': e['weight'], 'immune': list(e['immune']), 'snack': bool(e['snack']),
        'level': whole(e['level'], 'enemy level'), 'hp': whole(e['hp'], f"hp of enemy {e['id']}"),
        **{s: whole(e[s], f"{s} of enemy {e['id']}") for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')},
        'exp': e['exp'], 'gold': e['gold'],
        **{k: e[k] for k in ('res_slash', 'res_stab', 'res_bash', 'res_fire', 'res_water', 'res_wind', 'res_earth',
                             'res_lightning')},
        'attacks': list(e['attacks']), 'passives': list(e['passives']), 'script': script_json(e.get('script')),
    }


def equipment_json(p):
    return {
        'id': p['id'], 'name': p['name'], 'category': p['category'],
        'stats': {s: whole(v, f"{s} of piece {p['id']}") for s, v in p['stats'].items()},
        'rate': p['rate'], 'classes': p['classes'], 'swing': p['swing'], 'rank': p['rank'], 'type': p['type'],
        'enchants': list(p['enchants']), 'two_handed': bool(p['two_handed']), 'range': p['range'], 'attr': p['attr'],
    }


def side_json(data, flags):
    import class_data
    growth_row = {}
    for class_id, row in class_data.GROWTH_ROW.items():
        if isinstance(row, dict):
            growth_row[str(class_id)] = {'by_previous': [[k, v] for k, v in row.items()], 'default': min(row.values())}
        else:
            growth_row[str(class_id)] = {'row': row}
    return {
        'flags': flags,
        'skills': [skill_json(s) for s in data.skills.values()],
        'unique': [{'id': k, 'effect': v['effect'], 'values': list(v['values'])} for k, v in data.unique.items()],
        'attacks': [attack_json(a) for a in data.attacks.values()],
        'enemies': [enemy_json(e) for e in data.enemies.values()],
        'growth': [[k, [[g['atk'], g['def'], g['int'], g['res'], g['dex'], g['agi'], g['hp'], g['tp']] for g in rows]]
                   for k, rows in data.growth.items()],
        'growth_row': growth_row,
        'class_names': [[k, v] for k, v in data.class_names.items()],
        'class_modifiers': [{'class': m['class'], 'previous': m['previous'],
                             'entries': [{'modifier': x['modifier'], 'slot': x['slot'], 'type': x['type']}
                                         for x in m['entries']]} for m in data.class_modifiers],
        'characters': [{'name': c['name'], 'base_class': c['base_class'], 'flag': c['flag'],
                        'start_exp': c['start_exp'], 'unique_skill': c['unique_skill']} for c in data.characters],
        'equipment': [equipment_json(p) for p in data.equipment.values()],
        'enchant_stacks': sorted(data.enchant_stacks),
        'sealbooks': [{'id': k, 'enchants': list(v['enchants'])} for k, v in data.sealbooks.items()],
        'weapon_ranks': [[k, v] for k, v in data.weapon_ranks.items()],
        'items': [{'id': k, 'name': v['name'], 'effects': [[t, val] for t, val in v['effects']]}
                  for k, v in data.items.items()],
        'item_skills': [[k, v] for k, v in data.item_skills.items()],
        'exp_curve': [[k, v] for k, v in data.exp_curve.items()],
        'sp_curve': [[k, v] for k, v in data.sp_curve.items()],
        'floors': [{'dungeon': z['dungeon'], 'floor': z['floor'], 'zone': z['zone'], 'name': z['name'],
                    'formations': [{'chance': f['chance'], 'enemies': [[e, bool(fr)] for e, fr in f['enemies']],
                                    'number': f['number'], 'slots': list(f.get('slots', ()))} for f in z['formations']],
                    'equipment': [{'equipment': p['equipment'],
                                   'levels': [[k, lo, hi] for k, (lo, hi) in p['levels'].items()]}
                                  for p in z['equipment']]} for z in data.floors],
        'fixed': [{'floor': b['floor'], 'number': b['number'], 'enemies': [[e, bool(fr)] for e, fr in b['enemies']],
                   'slots': list(b.get('slots', ())), 'has_slots': 'slots' in b} for b in data.fixed],
        'battle_cells': [{'floor': k[0], 'number': k[1],
                          'cells': [{'zone': c['zone'], 'slots': list(c['slots'])} for c in v]}
                         for k, v in data.battle_cells.items()],
        'zone_factors': [{'floor': k[0], 'zone': k[1], 'down_a': v['down_a'], 'down_b': v['down_b'],
                          'element': v['element'], 'up_a': v['up_a'], 'up_b': v['up_b']}
                         for k, v in data.zone_factors.items()],
        'summons': [{'id': s['id'], 'family': s['family'], 'enemy': s['enemy'], 'level': s['level'], 'rank': s['rank'],
                     'name': s['name'], 'factors': {k: v for k, v in s['factors'].items()},
                     'attacks': list(s['attacks']), 'passive': s['passive'], 'script': script_json(s['script'])}
                    for s in data.summons],
        'npcs': [{'id': n['id'], 'character': n['character'], 'level': whole(n['level'], 'level of a guest'), 'raw_1c': n['raw_1c'],
                  'name': n['name'], 'attacks': list(n['attacks']), 'kind': n['kind'], 'hp': whole(n['hp'], f"hp of guest {n['id']}"),
                  'extra_attack': n['extra_attack'],
                  **{s: whole(n[s], f"{s} of guest {n['id']}") for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')},
                  'script': script_json(n['script'])} for n in data.npcs],
        'dolls': [{'skill': d['skill'], 'effect': d['effect'], 'name': d['name'], 'range': d['range'],
                   'turns': whole_list(d['turns'], 'doll turns'),
                   'actions': [{'skill': a['skill']} for a in d['actions']]} for d in data.dolls],
        'random_moves': [{'effect': t['effect'],
                          'results': [{'skill': r['skill'], 'weight': r['weight'], 'joker_weight': r['joker_weight'],
                                       'effects': [x[0] for x in r['effects']]} for r in t['results']]}
                         for t in data.random_moves],
    }


def rows_json(rows):
    """Rows of a sheet as they are: text, numbers and empty cells."""
    return [dict(r) for r in rows]


def setup_json(setup):
    return {
        'settings': dict(setup.settings),
        'policies': rows_json(setup.policies),
        'roles': [dict(r) for r in setup.roles.values()],
        'composition': list(setup.composition),
        'checkpoints': rows_json(setup.checkpoints),
        'joins': [[chapter, list(names)] for chapter, names in setup.joins],
        'guide_levels': [[k, v['Level']] for k, v in setup.guide_levels.items()],
        'grand_sealbooks': rows_json(setup.grand_sealbooks),
        'unique_gear': rows_json(setup.unique_gear),
        'personal_sealbooks': rows_json(setup.personal_sealbooks),
        'kit': rows_json(setup.kit),
        'preparation': rows_json(setup.preparation),
        'zone_changes': rows_json(setup.zone_changes),
        'enchant_plan': rows_json(setup.enchant_plan),
        'enchant_slots': rows_json(setup.enchant_slots),
        'battery': [[k, v[0], list(v[1])] for k, v in setup.battery.items()],
    }


def measure_inputs(setup, vanilla, variant):
    """What the measures of the suite (engine_cs/src/DtEngine/Suite) take from the workbooks and from the constants of the
    Python readers: sheets as rows, lists of parties, names of things. The measures themselves hold none of it."""
    import class_stages
    import guide_curve
    out = {
        'class_stages': rows_json(class_stages.stages(setup)),
        'class_kinds': class_stages.kinds(),
        'guide_sheet': rows_json(guide_curve.sheet(setup)),
        'guide_difficulty': dict(setup.guide_difficulty),
        'anchors': rows_json(setup.anchors),
        'audit_readings': rows_json(setup.audit_readings),
    }
    sys.path.insert(0, os.path.join(PROJECT, 'measures'))
    import win_rates
    out['win_rates'] = {'parties': {k: [v[0], v[1], v[2]] for k, v in win_rates.PARTIES.items()}, 'flag': win_rates.FLAG}
    import sim_audit
    from sim.battle import HANDLED
    out['sim_audit'] = {'tiers': [list(t) for t in sim_audit.TIERS], 'late': list(sim_audit.LATE), 'seeds': sim_audit.SEEDS,
                        'enemy': sim_audit.ACTIVES_ENEMY, 'tries': sim_audit.ACTIVE_TRIES, 'fallback': sim_audit.ACTIVES_FALLBACK,
                        'outside': sorted(e for e, where in HANDLED.items() if where.startswith('outside battle'))}
    import mercenaries
    import party_skills
    import postgame_compare
    import unique_skills
    import skill_value_contested
    import random_battles
    import regression_r04
    out['mercenaries'] = {'places': list(mercenaries.PLACES)}
    out['party_skills'] = {'places': list(party_skills.PLACES), 'resist': dict(party_skills.RESIST),
                           'skills': {k: [v[0], dict(v[1])] for k, v in party_skills.SKILLS.items()}}
    out['postgame_compare'] = {'steps': list(postgame_compare.STEPS)}
    out['unique_skills'] = {'roles': dict(unique_skills.ROLES), 'places': [list(p) for p in unique_skills.PLACES], 'pep': dict(unique_skills.PEP),
                            'skills': {str(k): {'name': v['name'], 'values': list(v['values'])} for k, v in variant.unique.items()}}
    out['skill_value_contested'] = {'contested': list(skill_value_contested.CONTESTED), 'not_battle': dict(skill_value_contested.NOT_BATTLE),
                                    'wins': skill_value_contested.WINS, 'length': skill_value_contested.LENGTH, 'hp': skill_value_contested.HP}
    out['random_battles'] = {'chain': random_battles.CHAIN, 'ahead': random_battles.AHEAD}
    out['regression_r04'] = {'substitutes': {k: list(v) for k, v in regression_r04.SUBSTITUTES.items()}}
    out['boss_rows_check'] = boss_rows_inputs(vanilla, variant)
    out['design_rows'] = design_rows_inputs(vanilla)
    out['trials'] = trial_inputs(vanilla)
    return out


def design_rows_inputs(vanilla):
    """measures/design_rows.py: the rows it reads of the vanilla workbook, the cells of the maps, what the floors hold that the battle does not
    need (encounter rate, the lowering factors of a zone), and the buff of each kind of meal."""
    import design_rows
    import item_effect_data
    import map_data
    columns = {'Equipment': ('Upgrade_Rate', 'Category', 'ATK', 'Type_Code', 'Name', 'Enchant_Count'), 'Items': ('Name', 'Buy_Price'),
               'FoodMenu': ('Name', 'Price') + tuple(f'Eff{k}_ID' for k in range(1, 6))}
    sheets = {name: [{c: row.get(c) for c in cols} for row in design_rows.sheet(name)] for name, cols in columns.items()}
    buffs = {}
    for kind, (skill, level) in item_effect_data.meal_buffs().items():
        found = vanilla.skill_by_id[skill]
        buffs[str(kind)] = {'skill': skill, 'name': found.name, 'level': level, 'turns': found.turns[level - 1]}
    return {'swaps': dict(design_rows.SWAPS), 'no_magic': design_rows.NO_MAGIC, 'down': list(design_rows.DOWN), 'steps_a_turn': design_rows.STEPS_A_TURN,
            'sheets': sheets, 'buffs': buffs,
            'maps': {name: [list(c['slots']) for c in m['cells']] for name, m in map_data.maps().items()},
            'floors': [{'encounter': f['encounter'], 'down': [f['zone_factors']['down_a'], f['zone_factors']['down_b']] if f.get('zone_factors') else None}
                       for f in vanilla.floors]}


def trial_inputs(vanilla):
    """The constants of the trial scripts of measures/ that dtcli plays as commands: their parties, cases and names."""
    import dance_trial
    import def_debuff_trial
    import etoile_dances
    import etoile_trial
    import lize_ideas
    import magic_wall
    import measure_open_rows
    import provoke_trial
    import sage_buffs_trial
    import tp_items_trial
    import curve_ablation

    def lists(table):
        return {k: list(v) for k, v in table.items()}

    return {
        'dance_trial': {'parties': lists(dance_trial.PARTIES), 'cases': dict(dance_trial.CASES), 'dances': dict(dance_trial.DANCES)},
        'def_debuff_trial': {'parties': lists(def_debuff_trial.PARTIES), 'cases': list(def_debuff_trial.CASES), 'samba': def_debuff_trial.SAMBA,
                             'pierce': def_debuff_trial.PIERCE, 'def_down': def_debuff_trial.DEF_DOWN, 'usual': list(def_debuff_trial.USUAL)},
        'etoile_dances': {'dances': dict(etoile_dances.DANCES), 'pairs': [list(p) for p in etoile_dances.PAIRS]},
        'etoile_trial': {'dances': dict(etoile_trial.DANCES), 'factors': list(etoile_trial.FACTORS)},
        'lize_ideas': {'girl': lize_ideas.GIRL, 'ideas': [[label, list(idea) if isinstance(idea, tuple) else idea] for label, idea in lize_ideas.IDEAS]},
        'magic_wall': {'elements': list(magic_wall.ELEMENTS)},
        'measure_open_rows': {'weapon': dict(measure_open_rows.WEAPON), 'role': dict(measure_open_rows.ROLE), 'stage': dict(measure_open_rows.STAGE)},
        'provoke_trial': {'provoke': list(provoke_trial.PROVOKE), 'enmity': provoke_trial.ENMITY, 'vanilla': list(provoke_trial.VANILLA)},
        'sage_buffs_trial': {'chanted': list(sage_buffs_trial.CHANTED), 'sized': dict(sage_buffs_trial.SIZED), 'extra_rules': list(sage_buffs_trial.EXTRA_RULES)},
        'tp_items_trial': {'fruit': tp_items_trial.FRUIT, 'trials': lists(tp_items_trial.TRIALS)},
        'curve_ablation': {'places': list(curve_ablation.PLACES), 'cases': list(curve_ablation.CASES)},
        'sealbook_names': {str(k): v['name'] for k, v in vanilla.sealbooks.items()},
    }


ENEMY_FIELDS = ('hp', 'atk', 'def', 'int', 'res', 'dex', 'agi', 'res_slash', 'res_stab', 'res_bash', 'res_fire', 'res_water', 'res_wind',
                'res_earth', 'res_lightning')


def boss_rows_inputs(vanilla, variant):
    """measures/boss_rows_check.py: the live rows of enemy stats by the checkpoint written in their record, and for each such checkpoint
    the stats of the enemy records on the variant with those rows taken out, as the changes from the variant. The export stops when
    the variant of these rows is not the variant of the snapshot, or when the changes do not give back the data without the rows."""
    import re
    import boss_rows_check
    from sim import variant as variant_mod
    rows = variant_mod.rows()
    found = {}
    for row in rows:
        if row['Table'] == 'enemies' and row['Field'] in boss_rows_check.FIELDS:
            where = re.search(r'\(([CP]\d+a?)\)', str(row['Record']))
            if where:
                found.setdefault(where.group(1), []).append(row)

    def with_flags(data):
        data.arcane_chance = variant_mod.arcane_chance()
        data.interrupt_product = variant_mod.interrupt_product()
        return data

    whole_variant = with_flags(variant_mod.apply(vanilla, rows))
    if text_of(side_json(whole_variant, flags_of(whole_variant))) != text_of(side_json(variant, flags_of(variant))):
        raise ValueError('the variant built from the rows is not the variant of the snapshot')
    # the rows of the table enemies read and write enemy records and nothing else: the data without the rows of a boss is the data
    # of the variant but for the stats of the records those rows touch, so only those records are built again
    import types
    enemy_rows = [r for r in rows if r['Table'] == 'enemies']
    touched = {int(str(r['Record']).split()[0]) for r in enemy_rows}
    small = types.SimpleNamespace(enemies={e: vanilla.enemies[e] for e in touched}, dolls=[], skill_by_id={})
    without = {}
    for cid, mine in found.items():
        ids = {r['ID'] for r in mine}
        bare = variant_mod.apply(small, [r for r in enemy_rows if r['ID'] not in ids])
        changes = {}
        for e, rec in bare.enemies.items():
            other = variant.enemies[e]
            if {k: v for k, v in rec.items() if k not in ENEMY_FIELDS} != {k: v for k, v in other.items() if k not in ENEMY_FIELDS}:
                raise ValueError(f'the record of enemy {e} without the rows of {cid} differs from the variant in more than its stats')
            diff = {f: rec[f] for f in ENEMY_FIELDS if rec[f] != other[f]}
            if diff:
                changes[str(e)] = diff
        without[cid] = changes
    return {'fields': list(boss_rows_check.FIELDS), 'keys': list(boss_rows_check.KEYS),
            'rows': {cid: [{'ID': r['ID'], 'Field': r['Field'], 'New': r['New'], 'Vanilla': r['Vanilla']} for r in mine] for cid, mine in found.items()},
            'without': without}


def flags_of(data):
    return {'arcane_chance': getattr(data, 'arcane_chance', None),
            'interrupt_product': bool(getattr(data, 'interrupt_product', False)),
            'survival_guard': bool(getattr(data, 'survival_guard', False))}


def snapshot():
    from sim import setup as setup_mod
    from sim.data import game_data
    from sim.variant import balance_data
    vanilla = game_data()
    variant = balance_data(vanilla)
    return {'format': FORMAT,
            'sides': {'vanilla': side_json(vanilla, flags_of(vanilla)), 'variant': side_json(variant, flags_of(variant))},
            'setup': setup_json(setup_mod.load()),
            'measures': measure_inputs(setup_mod.load(), vanilla, variant)}


def text_of(obj):
    """An exported side or setup as the text the engine reads."""
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def digest(text):
    import hashlib
    return hashlib.sha1(text.encode('utf-8')).hexdigest()


def hashes_path(path):
    return path + '.hashes'


def write(path=DEFAULT_OUT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    snap = snapshot()
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(snap, f, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    # what the snapshot holds, by content: a tool that sends a side or a setup of its own sends only the ones that differ
    with open(hashes_path(path), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'sides': {name: digest(text_of(side)) for name, side in snap['sides'].items()},
                   'setup': digest(text_of(snap['setup']))}, f)
    return path


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    print(write(target), os.path.getsize(target), 'bytes')
