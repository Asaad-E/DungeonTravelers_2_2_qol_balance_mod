"""Rows in the state proposed (the build and the simulator leave them out; BALANCE_PROPOSED=1 measures them):
the forge rate of the light blades and the power of Danger Shoot.

    python propose_daggers.py DAGGER_FACTOR TANTOU_FACTOR DANGER_SHOOT_ADD        e.g. 1 2 0.10
"""
import os
import sys
import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim.data import game_data                                # noqa: E402

CHANGES = os.path.join(PROJECT, 'data_tables', 'balance_changes.xlsx')
PIECES = ((53, 'W043'), (79, 'W044'), (356, 'W045'))
WHY_BLADE = ('Proposed 2026-10-11 (classes slow at their stage: Assassin, Treasure Hunter, Kunoichi). The light blades '
             'gain 1.0 - 1.3 ATK a forge level, the swords, axes and katanas 1.6 - 3.2; damage is attack less defence '
             '(FORMULAS 2.4), so at C30 a Kunoichi (ATK 133 against a boss of DEF 162) deals 11 with a plain blow and '
             'the Treasure Hunter 4 at C40. Lever L14, as the Whip (W005)')
WHY_SHOT = ('Proposed 2026-10-11 (the Trickster is 19 - 22% slower than the median attacker at C10, C13, C18): Danger '
            'Shoot dealt about 120 a use where Fireball and Frost Slash dealt 155 - 160; the same amount added at every '
            'level')


def main():
    # the factor of the Dagger and the Kukri, the one of the Tantou, what Danger Shoot gains; a factor of 1 writes no row
    factors = {53: float(sys.argv[1]), 79: float(sys.argv[1]), 356: float(sys.argv[2])}
    add = float(sys.argv[3])
    data = game_data()
    wb = openpyxl.load_workbook(CHANGES)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    for n in range(ws.max_row, 1, -1):                         # a new run takes the place of the last proposal
        if ws.cell(row=n, column=head.index('State') + 1).value == 'proposed' and \
                str(ws.cell(row=n, column=1).value)[:2] in ('W0', 'Y0'):
            ws.delete_rows(n)
    rows = []
    for pid, rid in PIECES:
        piece, factor = data.equipment[pid], factors[pid]
        if factor == 1:
            continue
        rows.append({'ID': rid, 'Table': 'equipment', 'Record': f"{pid} {piece['name']}", 'Field': 'upgrade rate',
                     'Vanilla': round(piece['rate'], 4), 'New': round(piece['rate'] * factor, 2), 'Lever': 'L14',
                     'Serves': 'F04, J27', 'Why': WHY_BLADE})
    (category, number), skill = next((k, s) for k, s in data.skills.items() if s.name == 'Danger Shoot')
    power = next(v for e, _, v in skill.effects if e == 26)
    for level, value in enumerate(power, 1):
        rows.append({'ID': f'Y{level:03d}', 'Table': 'skills', 'Record': f'{category} {number} Danger Shoot',
                     'Field': 'effect 26 (power)', 'Level': level, 'Vanilla': round(value, 4),
                     'New': round(value + add, 2), 'Lever': 'L12', 'Serves': 'F04', 'Why': WHY_SHOT})
    for row in rows:
        row.update({'Decided': '2026-10-11', 'State': 'proposed'})
        ws.append([row.get(name) for name in head])
    wb.save(CHANGES)
    for row in rows:
        print(row['ID'], row['Record'], row['Field'], row.get('Level') or '', row['Vanilla'], '->', row['New'])


if __name__ == '__main__':
    main()
