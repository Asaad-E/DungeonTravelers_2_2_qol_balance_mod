"""One-off edit (2026-10-13): what the audit of 2026-10-12 left open in the workbooks. Rows of balance_changes.xlsx
that named a row of the register that is not theirs name the right one; the SP cost of First Grid goes back (the
passive adds nothing that can be measured); rows of the register with a wrong figure or a closing that did not hold
are rewritten with what was measured; the note of a window of the settings says what it is. Run once; kept as the
record of the edit.
"""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHANGES = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
CRITERIA = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
SETUP = os.path.join(ROOT, 'data_tables', 'sim_setup.xlsx')

# rows of the changes: (start of the record, the row of the register they named) -> the rows they serve
SERVES = {('Technique 58 Magic Barrier', 'F09'): 'F13', ("Technique 104 Catalina's Action", 'F09'): 'F94',
          ('538 Kite Shield', 'F09'): 'F05', ('666 Fluted Armor', 'F09'): 'F05',
          ('Technique 38 Sleep Sting', 'F09'): 'F04, J27', ('Technique 39 Silence Sting', 'F09'): 'F04, J27',
          ('Technique 40 Stun Sting', 'F09'): 'F04, J27', ('Technique 51 Phoenix', 'F09'): 'F04, F58'}
EASY = ('1002 Countess of Vrachia', '760 Eros', '825 Afanc')       # the three bosses of rows G094 - G102
FIRST_GRID = ' | 2026-10-13 : measured (the Dark Lord of the reference party without the passive, with it at 10% and at ' \
             '15%, 200 battles at C30, C36, C38 and C40): wins within 4 points and length within 2% in the three cases. '
SAMAEL = (' | 2026-10-13 : measured (measures/rows_trial.py, 150 battles at P23, without the row > with it): the reference '
          'party 21% > 34% of wins, Meta 25% > 37%; no other party of the battery wins the fight either way')

REGISTER = {
    'S22': {'Vanilla_Result': 'The reference party at its level (64), 200 battles: 85% of wins in 33.2 turns in the game, the '
                              'lowest HP of the party 33% (measures/curve_recheck.py, 2026-10-13). Of the parties of the '
                              'battery, Mage-Heavy wins 62%, Juggernaut-Plus 19% and the two without a healer none '
                              '(measures/WIN_RATES.md)',
            'Balance_Result': 'On the variant the reference party wins 97% in 31.1 turns: easier, accepted on 2026-10-13 '
                              '(Regression R08)',
            'Why': 'A wall for a party without a Diva or a healer, not for one built for it: the fight asks for a heal every '
                   'turn, as the guides say',
            'Verdict': 'partly true: won 85% by a prepared party, never by one with no healer',
            'Decision': '2026-10-13: no change of its own; easier on the variant, accepted'},
    'S20': {'Status': 'not a problem',
            'Balance_Result': 'The EXP of a quest is not changed. What the variant changes beside it: the gold of the 41 quests '
                              'that pay gold x1.40 (P rows of the table quests), and the EXP of a member below the level of the '
                              'enemies (the factors by level gap, sheet ExePatches)',
            'Why': 'Of the 471 quests none pays EXP as its reward in a field the variant writes: the reward is an item, a piece, '
                   'EXP or gold by its kind (QuestData 0x38), and only gold was raised. The claim stands as the game has it; '
                   'the members who are behind catch up in battles, not through quests',
            'Verdict': 'true as stated; not answered by a change of quests',
            'Decision': '2026-10-11: quest gold x1.40 approved; 2026-10-13: the row says that this is not EXP'},
    'S08': {'Verdict': 'partly true: a summon acts like the slowest member of the party',
            'Why': 'Its wait is that of the slowest member (median 0.42 at level 90), still sooner than most bosses (0.42 - '
                   '0.55): late for a party, not too late to act. Its weight is data of each form (tools/summon_data.py)',
            'Decision': '2026-10-09: no change of its speed'},
    'S07': {'Vanilla_Result': 'CLASS_STAGES.md (2026-10-13): at the advanced stage her fights last 0.61 of those of the median '
                              'attacker with 46 - 67% of the damage of the party. The peak is one boss: 0.34 at C30, Heartless '
                              'Avenger, who resists slash, stab and bash at 90, 100 and 90 and the elements at 50 to 100. At '
                              'C22, C34 and C40 she stands at 0.67 to 0.72; late (P08 - P24) at 0.98',
            'Why': 'She is far ahead where the boss shuts physical damage out, which is what a mage is for; elsewhere she is '
                   'the fastest attacker by a third, and level with the others in the postgame',
            'Decision': '2026-10-13: not a problem where the boss is the weak one to magic; no change'},
    'J32': {'Why': 'Trump Card multiplies her damage (+60% to +150%) and takes her DEF away while it lasts: any hit fells her '
                   'unless someone covers her. It is the trade the class is built on (docs/CLASS_IDENTITY.md)',
            'Decision': '2026-10-09: no change; the fragility is what the Joker is'},
    'S17': {'Why': 'The pieces that cut damage add up to a quarter at most (docs/FORMULAS.md 2.4: never below 0.75); the claim '
                   'compares it with the half of the first game. It is a constant of the program, and a party defends itself '
                   'with DEF, guards and Cover, which the cap does not touch',
            'Decision': '2026-10-10: no change; raising it would be a patch of the program for a build nobody is missing'},
}
R01_NOTE = (' The Witch is the case: 0.61 of the median attacker at the advanced stage, 0.34 at C30 alone, a boss that '
            'resists physical damage at 90 - 100 (row S07, decided 2026-10-13: not a problem there)')
WINDOW_NOTE = ('choice: about one standard error of the difference of two shares of 40 battles near 0.7 (each share is known '
               'to about 7 points), so a crossing by less than 15 points may be chance: measures/curve_recheck.py settles it '
               'with 200 battles')


def main():
    wb = openpyxl.load_workbook(CHANGES)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    col = {name: head.index(name) for name in ('ID', 'Record', 'Serves', 'Why', 'State')}
    moved = 0
    for row in ws.iter_rows(min_row=2):
        rid, record, serves = (row[col[k]].value for k in ('ID', 'Record', 'Serves'))
        for (start, old), new in SERVES.items():
            if str(record).startswith(start) and serves == old:
                row[col['Serves']].value = new
                moved += 1
        if str(rid).startswith('G') and serves == 'F15' and str(record).startswith(EASY):
            row[col['Serves']].value = 'R08, R10'
            row[col['Why']].value = str(row[col['Why']].value).replace(' (user request)', '')
            moved += 1
        if rid == 'P031':
            row[col['State']].value = 'dropped'
            row[col['Why']].value = str(row[col['Why']].value) + FIRST_GRID + 'Dropped: a passive that adds nothing does not cost more'
        if rid == 'P032':
            row[col['Why']].value = str(row[col['Why']].value) + FIRST_GRID + 'Kept: harmless'
        if rid == 'P038':
            row[col['Why']].value = str(row[col['Why']].value) + SAMAEL
    assert moved == 25, moved
    wb.save(CHANGES)

    wb = openpyxl.load_workbook(CRITERIA)
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    done = 0
    for row in ws.iter_rows(min_row=2):
        for column, value in REGISTER.get(row[0].value, {}).items():
            row[head.index(column)].value = value
            done += 1
    assert done == sum(len(v) for v in REGISTER.values())
    ws = wb['Regression']
    head = [c.value for c in ws[1]]
    result = next(i for i, h in enumerate(head) if str(h).startswith('Result'))
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'R01':
            row[result].value = str(row[result].value) + '.' + R01_NOTE
    wb.save(CRITERIA)

    wb = openpyxl.load_workbook(SETUP)
    ws = wb['Settings']
    for row in ws.iter_rows():
        if row[0].value == 'check_won_window':
            row[3].value = WINDOW_NOTE
    wb.save(SETUP)
    print(moved, 'rows moved,', done, 'cells of the register')


if __name__ == '__main__':
    main()
