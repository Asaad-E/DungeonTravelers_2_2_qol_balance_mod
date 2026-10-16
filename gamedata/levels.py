"""The reference level of each checkpoint (A15, the decision of 2026-10-07): the guides' level, else the level of the random
enemies of the zone where the boss stands, else the level of the checkpoint before. Pure data, no battle: moved here from
the removed Python simulator (its scenario module) on 2026-10-16; the C# engine has the same rule (Scenario.ReferenceLevels)."""


def battle_numbers(cp):
    """The fixed battles of a checkpoint: one number, or several joined by + that are fought in a row."""
    return [int(n) for n in str(cp['Battle (several joined by + are fought in a row)']).split('+')]


def zone_level(data, floor, number, share):
    """The level of the random enemies of the floor zone whose cell starts a fixed battle: the lowest level L such that
    the formations whose strongest enemy is at most L make up the share of the encounters (chance of each formation;
    floor_data). None when the battle is started away from a cell of the floor or the zone has no formations."""
    cells = data.battle_cells.get((floor, number))
    if not cells:
        return None
    zone = cells[0]['zone']
    formations = [(max(data.enemies[e]['level'] for e, _ in f['enemies']), f['chance'])
                  for z in data.floors if z['floor'] == floor and z['zone'] == zone for f in z['formations']
                  if all(e in data.enemies for e, _ in f['enemies'])]
    if not formations:
        return None
    total, covered = sum(c for _, c in formations), 0
    for level, chance in sorted(formations):
        covered += chance
        if covered >= share * total:
            return level
    return max(level for level, _ in formations)


def reference_levels(data, setup):
    """{checkpoint: (level, where it comes from)} in the order of the sheet: never below the level of the checkpoint before,
    since a party does not lose levels."""
    share = float(setup.settings['zone_level_share'])
    found, previous = {}, 0
    for cp in setup.checkpoints:
        guide = setup.guide_levels.get(cp['ID'])
        zone = zone_level(data, cp['Floor'], battle_numbers(cp)[0], share)
        if guide is not None and guide['Level'] is not None:
            level, source = int(guide['Level']), 'guide'
        elif zone is not None:
            level, source = zone, 'zone'
        else:
            level, source = previous, 'before'
        if level < previous:
            level, source = previous, source + ', held'
        found[cp['ID']] = (level, source)
        previous = level
    return found
