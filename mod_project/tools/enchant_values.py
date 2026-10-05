"""
Figures of the enchantments, each with its source.

EnchantData.pck stores no magnitude (an entry is an id, three strings and a few flags) and no
table of magnitudes was found in the executable: the effect of each enchantment lives in code.
The figures below therefore come from player guides, never from the binary, and every one of
them names the guide it comes from. An enchantment without a trustworthy figure has no entry
here and keeps its vanilla name.

Sources
  dt22-wiki  Japanese wiki of Dungeon Travelers 2-2 (https://w.atwiki.jp/dt2-2/):
             pages 38 and 39 (enchant effects), 40 (grand sealbooks), 105 (player tests).
             Same game. These figures are shown by the QoL variant.
  dt2-wiki   Japanese wiki of the first Dungeon Travelers 2
             (https://w.atwiki.jp/dungeon-travelers2/pages/200.html). Same enchant system but
             another game: where both wikis give a figure they agree, except for the stat DOWN
             enchantments and two stacking caps. Shown by decision of the user; not confirmed
             for this game.
"""
import re
import collections
import rules

Value = collections.namedtuple('Value', 'figure name source note')

# The figures and the guides are sheets of data_tables/qol_rules.xlsx (EnchantValues, EnchantSources).
# A row holds either Figure, which replaces the tier word of the vanilla name ('Max HP UP' ->
# 'Max HP +10%'), or Name, for names that do not end in a tier word.
SOURCES = collections.OrderedDict((r['Source'], r['Description']) for r in rules.rows('EnchantSources'))
# The user chose to show the first game's figures too (2026-10-04). Each row keeps its source.
SHOWN_SOURCES = tuple(r['Source'] for r in rules.rows('EnchantSources') if rules.yes(r['Shown']))

TIER_RE = re.compile(r' (?:(?:Mini|Grand|Mega)?(?:UP|DOWN)|buff)$')
VALUES = {}
for _row in rules.rows('EnchantValues'):
    assert _row['Enchant_ID'] not in VALUES, _row['Enchant_ID']
    assert bool(_row['Figure']) != bool(_row['Name']), f"enchant {_row['Enchant_ID']}: give Figure or Name, not both"
    VALUES[int(_row['Enchant_ID'])] = Value(str(_row['Figure']) or None, _row['Name'] or None, _row['Source'], _row['Note'])


def proposal(enchant_id, vanilla_name):
    """(name, source, note) proposed for an enchantment, or None when no guide gives a figure."""
    value = VALUES.get(enchant_id)
    if value is None:
        return None
    if value.name is not None:
        return value.name, value.source, value.note
    name, count = TIER_RE.subn(' ' + value.figure, vanilla_name)
    if count != 1:
        raise ValueError(f"enchant {enchant_id} '{vanilla_name}' does not end in a tier word")
    return name, value.source, value.note


def qol_name(enchant_id, vanilla_name):
    """Name shown by the QoL variant: the proposal when its source is trusted, else the vanilla name."""
    found = proposal(enchant_id, vanilla_name)
    if found and found[1] in SHOWN_SOURCES:
        return found[0]
    return vanilla_name
