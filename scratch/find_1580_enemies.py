import sys
sys.path.append('mod_project/tools')
import enemy_data

enemies = enemy_data.enemies()
found = []
for e in enemies:
    # check skills of enemy: skills are in e.skills or similar
    # let's inspect attributes of e
    skills = getattr(e, 'skills', []) or getattr(e, 'attacks', [])
    # let's check all fields
    s_ids = [s for s in getattr(e, 'skill_ids', [])] if hasattr(e, 'skill_ids') else []
    for attr in dir(e):
        val = getattr(e, attr)
        if isinstance(val, (list, tuple)) and 1580 in val:
            found.append((e.id, getattr(e, 'name', ''), attr, val))

if not found:
    # check raw enemy data
    import glob, struct
    for path in glob.glob('mod_project/backups/EnemyData*.bin') + glob.glob('mod_project/backups/*Enemy*.pck'):
        pass
    # let's print dir(enemies[0])
    print('Enemy fields:', [a for a in dir(enemies[0]) if not a.startswith('_')])
    for e in enemies:
        # check if 1580 in any list attribute
        for a in ['actions', 'skills', 'passives', 'attacks']:
            if hasattr(e, a):
                l = getattr(e, a)
                if any(1580 == x or (isinstance(x, (tuple, list)) and 1580 in x) or getattr(x, 'id', None) == 1580 for x in l):
                    found.append((e.id, getattr(e, 'name', ''), a))

print('Enemies with 1580:', found[:10])
