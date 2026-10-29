"""
The Balance variant in the simulator: data_tables/balance_changes.xlsx applied on a copy of the game data.

Each row names a table, a record, a field and (for per-level values) a level, with its vanilla value and its new one.
The vanilla value is checked against what the game files hold; a row that does not match stops the load, so a change
written against a wrong reading cannot pass silently. Nothing here holds a value of the mod.

    from gamedata.variant import balance_data
    changed = balance_data(game_data())
"""
import copy
import struct
import os

import openpyxl

from gamedata.data import PROJECT_DIR

CHANGES = os.path.join(PROJECT_DIR, 'data_tables', 'balance_changes.xlsx')
DOLL_LIFE = 147                    # the life of a doll is effect 147 of its skill (docs/FORMULAS.md 11.1)


def rows(path=CHANGES, states=('decided', 'built', 'checked')):
    if os.environ.get('BALANCE_PROPOSED') == '1':      # a measure of the rows still proposed, by any tool, set apart
        states = tuple(states) + ('proposed',)
    it =openpyxl.load_workbook(path, read_only=True)['Changes'].iter_rows(values_only=True)
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
            elif field == 'turns':
                _check(row, skill.turns[level - 1]); skill.turns[level - 1] = new
            elif field == 'weapon codes':
                _check(row, ', '.join(str(w) for w in skill.weapons))
                skill.weapons = [int(w) for w in str(new).split(',')]
            elif field == 'target scope':
                _check(row, skill.target); skill.target = int(new)
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
        elif table == 'class_growth':
            # ClassLevelData row '<row> <class>', a stat at a level (tools/balance_values.py class_growth_row)
            stats = out.growth[int(record.split()[0])][level - 1]
            _check(row, stats[field]); stats[field] = new
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
            if field.startswith('steal flag'):
                _check(row, hex(enemy['flags']))
                enemy['flags'] = int(str(new), 16)
                enemy['can_steal'] = bool(enemy['flags'] >> enemy_data.STEAL_BIT & 1)
            elif field.startswith('immunity flags'):
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
            elif field.startswith('equipment slot '):
                # 'equipment slot 1 weight (piece 339)': no battle of the simulator reads it; the record follows the
                # row so that the build can be compared with it (tools/enemy_data.py: three words a slot from 0x84)
                k = int(field.split()[2]) - 1
                _check(row, enemy['raw_68'][9 + 3 * k])
                enemy['raw_68'][9 + 3 * k] = int(new)
                enemy['equipment_slots'][k] = enemy['equipment_slots'][k][:2] + (int(new),)
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
        elif table == 'unique':
            skill = out.unique[int(record.split()[1])]
            if field == 'effect id':             # the effect the skill is a status of (UniqueSkillData 0x50)
                _check(row, skill['effect'])
                skill['effect'] = int(new)
                continue
            rank = int(row['Level'])
            _check(row, skill['values'][rank - 1])
            skill['values'] = [float(new) if k == rank - 1 else v for k, v in enumerate(skill['values'])]
        elif table == 'items':
            # 'effect 1 value': the value of the first pair of that type of the item
            item = out.items[int(record.split()[0])]
            kind = int(field.split()[1])
            at = next(k for k, (t, _) in enumerate(item['effects']) if t == kind)
            _check(row, item['effects'][at][1])
            item['effects'] = [(t, float(new) if k == at else v) for k, (t, v) in enumerate(item['effects'])]
        elif table == 'npcs':
            # '<id> <name> (level <n>)': one of the six stats of a guest ally at one stage (tools/npc_data.py)
            npc = next(n for n in out.npcs if n['id'] == int(record.split()[0]))
            if field.startswith('AI set '):
                # 'AI set <n> weights': the weights of a set of her script, the slots separated by spaces
                the_set = npc['script']['sets'][int(field.split()[2])]
                old, new_weights = [int(x) for x in str(row['Vanilla']).split()], [int(x) for x in str(new).split()]
                if list(the_set['weights'][:len(old)]) != old or any(the_set['weights'][len(old):]):
                    raise ValueError(f'{row["ID"]}: the weights of {record} {field} are {the_set["weights"]}, not {old}')
                the_set['weights'] = new_weights + [0] * (len(the_set['weights']) - len(new_weights))
                continue
            _check(row, npc[field])
            npc[field] = int(new)
        elif table == 'summons':
            # '<id> <name> (level <n>)': one factor of the stats of a form of a summon, or 'AI set <n> weights' of its script
            form = next(s for s in out.summons if s['id'] == int(record.split()[0]))
            if field.startswith('AI set '):
                the_set = form['script']['sets'][int(field.split()[2])]
                old, new_weights = [int(x) for x in str(row['Vanilla']).split()], [int(x) for x in str(new).split()]
                if list(the_set['weights'][:len(old)]) != old or any(the_set['weights'][len(old):]):
                    raise ValueError(f'{row["ID"]}: the weights of {record} {field} are {the_set["weights"]}, not {old}')
                the_set['weights'] = new_weights + [0] * (len(the_set['weights']) - len(new_weights))
                continue
            _check(row, form['factors'][field])
            form['factors'][field] = struct.unpack('<f', struct.pack('<f', float(new)))[0]      # a float of the record
        elif table == 'party_skills':
            continue                    # out of the model; tools/balance_values.py writes and checks the row
        elif table == 'quests':
            continue                    # the simulator has no quests; tools/balance_values.py writes and checks the row
        elif table == 'sealbooks':
            # 'ench_cnt=2 (222 Front line ATK, 268 Critical UP)': the enchantments of the sealbook, in order
            import re
            book = out.sealbooks[int(re.search(r'\((\d+)\)\s*$', record).group(1))]
            listed = {c: [int(x) for x in re.findall(r'[(,]\s*(\d+)\b', str(row[c]))] for c in ('Vanilla', 'New')}
            if listed['Vanilla'] != book['enchants']:
                raise ValueError(f'{row["ID"]}: {record} holds the enchantments {book["enchants"]}, not {listed["Vanilla"]}')
            book['enchants'] = listed['New']
        elif table == 'enchantments':
            # 'stacking flag (0x20 bit 0)': every piece of the enchantment counts once the bit is set (FORMULAS 16.7)
            import re
            eid = int(re.search(r'EnchantData_(\d+)', record).group(1))
            if int(new) & 1:
                out.enchant_stacks.add(eid)
            else:
                out.enchant_stacks.discard(eid)
        elif table == 'zones':
            pass                                # the chance of a wandering shop: nothing of a battle
        else:
            raise ValueError(f'{row["ID"]}: unknown table {table}')
    for doll in out.dolls:                     # a doll record follows the life of its skill
        skill = out.skill_by_id.get(doll['skill'])
        if skill is not None and skill.has(DOLL_LIFE):
            doll['turns'] = list(next(v for e, _, v in skill.effects if e == DOLL_LIFE))
    return out


def balance_data(data, path=CHANGES):
    out = apply(data, rows(path))
    out.arcane_chance = arcane_chance()
    out.interrupt_product = interrupt_product()
    out.survival_guard = lever_patched('L46')
    return out


def lever_patched(lever):
    """Whether the set balance of the sheet ExePatches holds a row of this lever."""
    import exe_patch
    return any(p['lever'] == lever for p in exe_patch.patches('balance'))


def interrupt_product():
    """Whether the set balance of the sheet ExePatches mends the interruption rate (lever L45): Concentrate then
    divides it, as the message of the program tells (docs/FORMULAS.md 2.5)."""
    import exe_patch
    return any(p['lever'] == 'L45' for p in exe_patch.patches('balance'))


def arcane_chance():
    """The roll of Arcane Shield on the variant: the byte the set balance of the sheet ExePatches puts at the
    place of lever L38, or None when the set leaves it alone."""
    import exe_patch
    row = next((p for p in exe_patch.patches('balance') if p['lever'] == 'L38'), None)
    return row['new'][-1] if row else None
