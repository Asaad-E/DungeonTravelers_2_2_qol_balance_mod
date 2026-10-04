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

Value = collections.namedtuple('Value', 'figure name source note')

SOURCES = collections.OrderedDict([
    ('dt22-wiki', 'Japanese wiki of Dungeon Travelers 2-2, https://w.atwiki.jp/dt2-2/ pages 38, 39, 40 and 105 (same game)'),
    ('dt2-wiki', 'Japanese wiki of the first Dungeon Travelers 2, https://w.atwiki.jp/dungeon-travelers2/pages/200.html '
                 '(same system, another game: not confirmed for this one)'),
])
# The user chose to show the first game's figures too (2026-10-04). Each row keeps its source.
SHOWN_SOURCES = ('dt22-wiki', 'dt2-wiki')

TIER_RE = re.compile(r' (?:(?:Mini|Grand|Mega)?(?:UP|DOWN)|buff)$')
VALUES = {}


def tier(ids, figure, source, note=''):
    """The figure replaces the tier word of the vanilla name: 'Max HP UP' -> 'Max HP +10%'."""
    for enchant_id in ids:
        assert enchant_id not in VALUES, enchant_id
        VALUES[enchant_id] = Value(figure, None, source, note)


def named(enchant_id, name, source, note=''):
    """Names that do not end in a tier word are worded by hand."""
    assert enchant_id not in VALUES, enchant_id
    VALUES[enchant_id] = Value(None, name, source, note)


DT22, DT2 = 'dt22-wiki', 'dt2-wiki'

# --- Stats (page 38/39: each enchantment is rounded down on its own; UP and MiniUP stack) -----------
tier([0], '+10%', DT22, 'At least +4. Max HP bonuses stack up to +50%')
tier([3], '+10%', DT22)
tier([6, 9, 12, 15, 18, 21], '+10%', DT22, 'At least +4')
tier([1], '+5%', DT22, 'At least +2. Max HP bonuses stack up to +50%')
tier([4], '+5%', DT22)
tier([7, 10, 13, 16, 19, 22], '+5%', DT22, 'At least +2')
tier([5], '-10%', DT22)
tier([8, 11, 14, 17, 20, 23], '-5%', DT22, 'The first game\'s wiki lists -10%')
tier([2], '-10%', DT2, 'The DT2-2 wiki lists this one as unknown (-??%)')

# --- Combat abilities: the DT2-2 wiki gives no figure for any of them -------------------------------
tier([29, 37], '+4%', DT2, 'First game: stacks up to +50%')
tier([30, 38], '+2%', DT2, 'First game: stacks up to +50%')
tier([49], '+5%', DT2)
tier([50], '-5%', DT2)
tier([51], '+10%', DT2, 'DT2-2 player test: only five of them count')
tier([52], '+5%', DT2)
tier([54], '+20%', DT2, 'DT2-2 player test: only three of them count')
tier([55], '+10%', DT2)
tier([58], '-6%', DT2)
tier([59], '-3%', DT2)
tier([60], '+6%', DT2)
named(72, 'Convert 5% of received damage into TP', DT2, 'First game: at least 1 TP, also from poison and traps')
tier([78, 79, 80, 81, 82], '+20%', DT2, 'First game: magic of that element x1.2, and the weapon attacks with that element')

# --- Damage taken (stack; DT2-2 wiki: total reduction capped at -25%) -------------------------------
tier([66, 68], '-10%', DT22, 'Damage reductions stack down to -25%')
tier([67, 69], '-5%', DT22, 'Damage reductions stack down to -25%')
tier([70], '-8%', DT22, 'Physical and magic. Damage reductions stack down to -25%')
tier([71], '-4%', DT22, 'Physical and magic. Damage reductions stack down to -25%')

# --- Resistances ------------------------------------------------------------------------------------
# The guide and the binary (skill effects) hold resistance as points where 100 is immunity, so a point
# is one percent of the damage taken. Written with % at the user's request.
tier([88, 91, 94, 97, 100, 107, 110, 113], '+20%', DT22)
tier([89, 92, 95, 98, 101, 108, 111, 114], '+10%', DT22)
tier([90, 93, 96, 99, 102, 109, 112, 115], '-20%', DT22)
tier([104], '+15%', DT22, 'Each of the five elements')
tier([105], '+7%', DT22, 'Each of the five elements')
tier([106], '-15%', DT22, 'Each of the five elements')
tier([103], '+50%', DT22, 'Each of the five elements')
tier([335], '+75%', DT22, 'Each of the five elements')
tier([336], '-30%', DT22, 'Each of the five elements')
tier([117], '+10%', DT22, 'Slash, stab and bash')
tier([118], '+5%', DT22, 'Slash, stab and bash')
tier([116], '+25%', DT22, 'Slash, stab and bash')
tier([355], '+50%', DT22, 'Slash, stab and bash')
tier([356], '-20%', DT22, 'Slash, stab and bash')
tier([119], '-10%', DT2, 'Slash, stab and bash. The DT2-2 wiki lists this one as unknown (-??)')
tier([311, 316, 321, 326, 331, 341, 346, 351], '+50%', DT22)
tier([310, 315, 320, 325, 330, 340, 345, 350], '+100%', DT22)
tier([312, 317, 322, 327, 332, 342, 347, 352], '-50%', DT22)

# --- Recovery every turn (stack) --------------------------------------------------------------------
named(145, 'Recover 2% HP every turn', DT22)
named(144, 'Recover 4% HP every turn', DT22)
named(148, 'Recover 8% HP every turn', DT22)
named(147, 'Recover 2 TP every turn', DT22)
named(146, 'Recover 4 TP every turn', DT22)
named(149, 'Recover 6 TP every turn', DT22)

# --- Normal attack effects and race bonuses: only the first game's wiki has figures -----------------
named(162, 'Normal attacks absorb HP (15% of damage)', DT2, 'First game: no effect on undead')
named(161, 'Normal attacks absorb HP (50% of damage)', DT2, 'First game: no effect on undead')
named(164, 'Normal attacks absorb TP (5% of damage)', DT2, 'First game: no effect on undead')
named(163, 'Normal attacks absorb TP (20% of damage)', DT2, 'First game: no effect on undead')
tier([171, 173, 175, 178, 180, 182, 184], '+20%', DT2, 'First game: physical damage x1.2')
tier([170, 172, 174, 177, 179, 181, 183], '+40%', DT2, 'First game: physical damage x1.4')
tier([186], '+50%', DT2, 'First game: physical damage x1.5')
tier([176, 185, 196], '+100%', DT2, 'First game: physical damage x2')

# --- Songs, grand sealbooks -------------------------------------------------------------------------
named(300, 'Songs +2% (Carol +20%, Chorale +2)', DT22, 'Carol +20%, Chorale +2, every other song +2%')
named(301, 'Songs +1% (Carol +10%, Chorale +1)', DT22, 'Carol +10%, Chorale +1, every other song +1%')
named(258, 'Equipment from treasure boxes: level +2', DT22, 'Page 40, grand sealbook Kaguya')
named(270, 'EXP from higher-level enemies +15%', DT22, 'Page 40, grand sealbook Dragon Puppy')
named(267, 'Damage +10% per missing party member', DT22,
      'Page 105, player test of grand sealbook Heket: 110% / 120% / 130% / 140% with 4 / 3 / 2 / 1 members')


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
