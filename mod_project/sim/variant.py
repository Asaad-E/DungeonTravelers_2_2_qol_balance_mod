"""
The Balance variant in the simulator: data_tables/balance_changes.xlsx applied on a copy of the game data.

Each row names a table, a record, a field and (for per-level values) a level, with its vanilla value and its new one.
The vanilla value is checked against what the game files hold; a row that does not match stops the load, so a change
written against a wrong reading cannot pass silently. Nothing here holds a value of the mod.

    from sim.variant import balance_data
    changed = balance_data(game_data())
"""
import copy
import os

import openpyxl

from sim.data import PROJECT_DIR

CHANGES = os.path.join(PROJECT_DIR, 'data_tables', 'balance_changes.xlsx')
DOLL_LIFE = 147                    # the life of a doll is effect 147 of its skill (docs/FORMULAS.md 11.1)


def rows(path=CHANGES, states=('decided', 'built', 'checked')):
    it = openpyxl.load_workbook(path, read_only=True)['Changes'].iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it if r and r[0] is not None and dict(zip(header, r))['State'] in states]


def _same(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        try:
            return int(str(a), 16) == int(str(b), 16)
        except (TypeError, ValueError):
            return str(a).strip() == str(b).strip()


def _check(row, current):
    if not _same(row['Vanilla'], current):
        raise ValueError(f'{row["ID"]}: the vanilla value of {row["Record"]} {row["Field"]} level {row["Level"]} is '
                         f'{current}, not {row["Vanilla"]}')


def _effect_id(field):
    return int(field.split()[1]) if field.startswith('effect ') else int(field.split('effect ')[1].rstrip(')'))


def apply(data, changes):
    """A copy of data with every row of changes applied."""
    import enemy_data
    out = copy.deepcopy(data)
    for row in changes:
        table, record, field, level = row['Table'], str(row['Record']), str(row['Field']), row['Level']
        new = row['New']
        if table == 'sp_curve':
            _check(row, out.sp_curve[level])
            out.sp_curve[level] = new
        elif table == 'skills':
            category, sid = record.split()[0], int(record.split()[1])
            skill = out.skills[(category, sid)]
            if field == 'TP cost':
                _check(row, skill.tp[level - 1]); skill.tp[level - 1] = new
            elif field == 'speed factor':
                _check(row, skill.speed[level - 1]); skill.speed[level - 1] = new
            elif field == 'chant speed factor':
                _check(row, skill.cast[level - 1]); skill.cast[level - 1] = new
            elif field == 'weapon codes':
                _check(row, ', '.join(str(w) for w in skill.weapons))
                skill.weapons = [int(w) for w in str(new).split(',')]
            elif field == 'SP cost':
                _check(row, skill.sp[level - 1]); skill.sp[level - 1] = new
            elif field.startswith('added effect'):
                # 'added effect 106 (kind 4)': an empty slot of the five a skill record holds (tools/extract_vanilla.py)
                # filled with that effect; New lists its value at each level. Lever L13 (what a skill does).
                eid, kind = int(field.split()[2]), int(field.split('kind')[1].strip(' )'))
                if any(e == eid for e, _, _ in skill.effects) or len(skill.effects) >= 5:
                    raise ValueError(f'{row["ID"]}: {record} has no empty slot for effect {eid}')
                skill.effects.append((eid, kind, [float(v) for v in str(new).split(',')]))
            elif 'effect' in field:
                eid = _effect_id(field)
                values = next(v for e, _, v in skill.effects if e == eid)
                _check(row, values[level - 1]); values[level - 1] = new
            else:
                raise ValueError(f'{row["ID"]}: unknown skill field {field}')
        elif table == 'equipment':
            piece = out.equipment[int(record.split()[0])]
            if field == 'ATK (base)':
                _check(row, piece['stats']['atk']); piece['stats']['atk'] = new
            elif field == 'upgrade rate':
                _check(row, piece['rate']); piece['rate'] = new
            elif field in ('class bitmask', 'classes', 'mask_0x40'):
                _check(row, hex(piece['classes']))
                piece['classes'] = int(str(new), 16) if isinstance(new, str) else int(new)
            elif field.startswith('Enchant'):
                idx = int(field.split()[1]) - 1
                _check(row, piece['enchants'][idx])
                piece['enchants'][idx] = int(new)
            else:
                raise ValueError(f'{row["ID"]}: unknown equipment field {field}')
        elif table == 'enemies':
            enemy = out.enemies[int(record.split()[0])]
            if field.startswith('immunity flags'):
                _check(row, hex(enemy['flags']))
                enemy['flags'] = int(str(new), 16)
                enemy['immune'] = [n for bit, n in enemy_data.IMMUNITY_BITS.items() if enemy['flags'] >> bit & 1]
            elif field in ('hp', 'atk', 'def', 'int', 'res', 'dex', 'agi'):
                _check(row, enemy[field]); enemy[field] = int(new)       # lever L01: a stat of the enemy record
            elif field.startswith('resistance '):
                key = 'res_' + field.split()[1]
                _check(row, enemy[key]); enemy[key] = new
            elif field.startswith('passive skill id'):
                if int(row['Vanilla']) not in enemy['passives']:
                    raise ValueError(f'{row["ID"]}: {record} carries no passive {row["Vanilla"]}')
                enemy['passives'] = [int(new) if p == int(row['Vanilla']) else p for p in enemy['passives']]
            elif field in ('equipment drop rate', 'steal rate'):
                continue
            elif field.startswith('AI set '):
                if enemy.get('script') and 'sets' in enemy['script']:
                    set_num = int(field.split()[2])
                    if set_num in enemy['script']['sets']:
                        import re
                        m = re.search(r'slot\s+(\d+)', str(new))
                        slot_idx = int(m.group(1)) if m else int(new)
                        weights = [0] * 16
                        weights[slot_idx] = 100
                        enemy['script']['sets'][set_num]['weights'] = weights
            else:
                raise ValueError(f'{row["ID"]}: unknown enemy field {field}')
        elif table == 'attacks':
            attack = out.attacks[int(record.split()[0])]
            eid = _effect_id(field)
            k = next(i for i, (e, _, _) in enumerate(attack.effects) if e == eid)
            e, kind, v = attack.effects[k]
            _check(row, v)
            attack.effects[k] = (e, kind, new)
        elif table in ('sealbooks', 'enchantments', 'quests'):
            continue
        else:
            raise ValueError(f'{row["ID"]}: unknown table {table}')
    for doll in out.dolls:                     # a doll record follows the life of its skill
        skill = out.skill_by_id.get(doll['skill'])
        if skill is not None and skill.has(DOLL_LIFE):
            doll['turns'] = list(next(v for e, _, v in skill.effects if e == DOLL_LIFE))
    return out


def balance_data(data, path=CHANGES):
    return apply(data, rows(path))
