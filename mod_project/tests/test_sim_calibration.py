"""The simulator against what players measured in the game (sheet Calibration of data_tables/sim_setup.xlsx).

Each class is one row of the sheet; its docstring names the row and the page the figures come from. The figures are
the players' own and are copied here only as the expected results of a test."""
import math
import random
import sys
import unittest

import _paths
sys.path.insert(0, _paths.PROJECT_DIR)
from sim import formulas as f
from sim import progression
from sim.data import game_data
from sim.battle import Action, Battle
from sim.units import Unit, PARTY, build_enemy, build_summon

STATS = ('atk', 'def', 'int', 'res', 'dex', 'agi')


class CriticalFactor(unittest.TestCase):
    def test_the_sealbook_test_fits_a_quarter_more(self):
        """K03, atwiki dt2-2 page 105 (Heqet sealbook): unarmed hits of Yae and Luco on Hola-Orange went from 170 to
        213 and from 52 to 65 on a critical hit. Damage is kept as an integer after the factor, so a normal hit of
        170 is some x with int(x) = 170, and the critical one int(x * 1.25) must be possible for such an x."""
        for normal, critical in ((170, 213), (52, 65)):
            low = max(normal, critical / f.CRIT_FACTOR)
            high = min(normal + 1, (critical + 1) / f.CRIT_FACTOR)
            with self.subTest(normal=normal):
                self.assertLess(low, high)


class DaedalusAttack(unittest.TestCase):
    """K04, atwiki dt2-2 page 105: one hit of Daedalus Attack Lv10 by crowned Yae, level 99, with Lance Mastery Lv10,
    against Hola-Orange (DEF 10, stab resistance -20), with the ATK of the status screen. Every measured hit must
    fall inside the range the formula gives over the swing of the weapon, within 2%: the Gabas Ring worn with the
    Lance is not identified among the records, and the lowest critical hit with it (970) is 1.8% under the model.
    The Heavy Lance is one of the weapons 183 - 199 that effect 111 of the skill rewards (0x44b44d - 0x44b475)."""
    CASES = (('Lance', 251, (790, 841), (970, 1062)), ('Heavy Lance', 251, (901, 1001), (1097, 1245)),
             ('Don Quixote', 262, (826, 896), (1056, 1120)))

    def test_every_measured_hit_falls_in_the_range_of_the_formula(self):
        data = game_data()
        skill = next(s for s in data.skills.values() if s.name == 'Daedalus Attack')
        enemy_id = next(i for i, e in data.enemies.items() if e['name'] == 'Hola-Orange')
        for name, atk, normal, critical in self.CASES:
            weapon = next(p for p in data.equipment.values() if p['name'] == name)
            member = Unit('Yae', PARTY, 99, 1, 0, {s: 1 for s in STATS}, swing=weapon['swing'])
            member.base['atk'], member.weapon = atk, weapon
            member.attack_range, member.attack_attr = weapon['range'], weapon['attr']
            target = build_enemy(data, enemy_id)
            battle = Battle(data, [member], [target], random.Random(0))
            action = Action(member, 'skill', skill, 10)
            for measured, crit in ((normal, False), (critical, True)):
                ends = []
                for swing in (-weapon['swing'], weapon['swing']):
                    battle.swing = lambda unit, s=swing: s
                    ends.append(battle.physical_damage(action, target, 0, crit))
                low, high = ends
                with self.subTest(weapon=name, critical=crit):
                    self.assertGreaterEqual(min(measured), low * 0.98)
                    self.assertLessEqual(max(measured), high * 1.02)


class ChantStat(unittest.TestCase):
    """K06, atwiki dt2-2 page 105 (version 1.03): the stat each spell of the player is chanted with, by class. The
    Japanese name of the page, the English name of the game, the stat of the page."""
    TABLE = (
        ('ヒール', 'Heal', 'res'), ('エンラージブラッド', 'Blood Rage', 'int'), ('サークルヒール', 'Circle Heal', 'res'),
        ('プロテクション', 'Protect', 'res'), ('ムーンカーテン', 'Moon Curtain', 'res'), ('ライフブリング', 'Life Bring', 'int'),
        ('ブレイブ', 'Brave', 'res'), ('ファイアボール', 'Fireball', 'int'), ('アイスエッジ', 'Ice Edge', 'int'),
        ('エアカッター', 'Air Cutter', 'int'), ('ストーンハンマー', 'Stone Hammer', 'int'), ('サンダーボルト', 'Thunderbolt', 'int'),
        ('ポイズン', 'Poison', 'int'), ('ファイアブラスト', 'Fire Blast', 'int'), ('ブラッドドレイン', 'Blood Absorb', 'int'),
        ('ミニサークルナース', 'Mini Circle Nurse', 'res'), ('スタン', 'Stun', 'int'), ('フリーズ', 'Freeze', 'int'),
        ('サイレンス', 'Silence', 'int'), ('パラリシス', 'Paralyze', 'int'), ('エンチャントファイア', 'Fire Enchant', 'res'),
        ('サークルブレイブ', 'Circle Brave', 'res'), ('サークルプロテクト', 'Circle Protect', 'res'),
        ('ディバインシールド', 'Divine Shield', 'res'), ('ナース', 'Nurse', 'res'), ('リザレクション', 'Resurrect', 'res'),
        ('スロウ', 'Slow', 'int'), ('インフェルノ', 'Inferno', 'int'), ('クリムゾンフレア', 'Crimson Flare', 'int'),
        ('ソウルドレイン', 'Soul Absorb', 'int'), ('レインボーフラッシュ', 'Rainbow Flash', 'int'),
        ('アクセラレーター', 'Accelerator', 'res'), ('イリュージョン', 'Illusion', 'res'), ('プリズムドーン', 'Prism Dawn', 'res'),
        ('テラー', 'Terrorize', 'int'), ('スリープ', 'Sleep', 'int'), ('デス', 'Death', 'int'), ('ペトリファクション', 'Petrify', 'int'),
        ('ディスペル', 'Dispel', 'int'), ('スタブプロテクト', 'Stab Guard', 'res'), ('カットプロテクト', 'Slash Guard', 'res'),
        ('ブロウプロテクト', 'Bash Guard', 'res'), ('アンプリケイション', 'Amplify', 'res'), ('サンベール', 'Sun Veil', 'res'),
        ('シャインクルス', 'Shine Curse', 'int'), ('フルヒール', 'Full Heal', 'res'), ('サークルナース', 'Circle Nurse', 'res'),
        ('インシュランス', 'Insurance', 'res'), ('忍術：影分身', 'Shadow Clone', 'agi'), ('忍術：影縫い', 'Shadow Sew', 'int'),
        ('忍術：日遁', 'Light Scroll', 'int'), ('忍術：火遁', 'Fire Scroll', 'int'), ('忍術：水遁', 'Water Scroll', 'int'),
        ('忍術：雷遁', 'Lightning Scroll', 'int'), ('忍術：風遁', 'Wind Scroll', 'int'), ('忍術：土遁', 'Earth Scroll', 'int'),
        ('子守唄', 'Lullaby', 'res'), ('精霊賛辞ファンタジア', 'Spiritual Fantasia', 'int'), ('神聖礼拝ヒムヌス', 'Sacred Hymn', 'int'),
        ('充実キャロル', 'Replenishing Carol', 'int'), ('至福コラール', 'Blissful Chorale', 'int'),
        ('経験促進ピーアン', 'Experience Paean', 'int'), ('パニックボイス', 'Panic Voice', 'int'), ('連撃必倒ロンド', 'Barrage Rondo', 'int'),
        ('会心集中プレリュード', 'Concentration Prelude', 'int'), ('信仰速読レクイエム', 'Reading Requiem', 'int'),
        ('魔導的中バラード', 'Sorcerous Ballad', 'int'), ('疾風迅雷マーチ', 'Lightning March', 'int'),
        ('褒美と躾', 'Carrot and Stick', 'int'), ('プリマヴェール', 'Primevil', 'agi'), ('ソウルイーター', 'Soul Eater', 'int'),
        ('リミットフィールド', 'Limit Field', 'res'), ('ヘブン・オア・ヘル', 'Heaven or Hell', 'agi'))

    def test_every_spell_of_the_table_chants_with_the_stat_the_players_found(self):
        spells = {s.name: s for s in game_data().skills.values() if s.category == 'Magic'}
        for japanese, english, stat in self.TABLE:
            with self.subTest(spell=english, page=japanese):
                self.assertEqual(spells[english].chant_stat, stat)


class SummonStats(unittest.TestCase):
    """K05, atwiki dt2-2 page 105: [best stat of the party, stat of the summon] pairs, and the lowest stats."""
    LOWEST = {'Bigfoot': (33, 31, 16, 24, 17, 10), 'Ghast': (45, 42, 15, 33, 21, 17), 'Cupid': (49, 44, 19, 37, 24, 23)}
    PAIRS = {('Bigfoot', 13): {'atk': [(19, 38), (21, 42), (22, 44), (24, 48), (25, 51)],
                               'def': [(23, 35), (24, 36), (25, 38)],
                               'int': [(24, 18), (25, 19), (27, 20), (28, 21)],
                               'dex': [(19, 18), (20, 19), (22, 20), (23, 21), (26, 24), (27, 25), (29, 27), (30, 28)],
                               'agi': [(13, 11), (15, 13), (17, 15), (19, 17), (20, 18), (21, 19), (22, 20), (23, 20),
                                       (24, 21), (26, 23), (27, 24)]},
             ('Ghast', 12): {'atk': [(23, 46), (24, 48), (25, 50)], 'agi': [(26, 18)]},
             ('Ghast', 18): {'atk': [(22, 50), (27, 61)], 'int': [(28, 17)], 'dex': [(30, 25)], 'agi': [(27, 22)]},
             ('Cupid', 15): {'int': [(22, 20), (24, 22), (27, 24), (28, 25)],
                             'dex': [(23, 25), (26, 29), (29, 32), (30, 33)], 'agi': [(27, 24)]}}

    @classmethod
    def setUpClass(cls):
        cls.data = game_data()

    def form(self, name, level):
        return next(s for s in self.data.summons if s['name'] == name and s['level'] == level)

    def summon(self, form, stat, best):
        member = Unit('test', PARTY, 1, 1, 0, {s: 1 for s in STATS})
        member.base[stat] = best
        return build_summon(self.data, form, [member], 1)

    def test_a_weak_party_gives_the_lowest_stats(self):
        for name, lowest in self.LOWEST.items():
            form = min((s for s in self.data.summons if s['name'] == name), key=lambda s: s['level'])
            unit = self.summon(form, 'atk', 1)
            with self.subTest(summon=name):
                self.assertEqual(tuple(unit.base[s] for s in STATS), lowest)

    def test_each_stat_is_the_best_of_the_party_times_the_factor_of_the_form(self):
        for (name, level), stats in self.PAIRS.items():
            form = self.form(name, level)
            for stat, pairs in stats.items():
                for best, measured in pairs:
                    with self.subTest(summon=name, level=level, stat=stat, best=best):
                        self.assertEqual(self.summon(form, stat, best).base[stat], measured)


class EncounterSteps(unittest.TestCase):
    """K07, atwiki dt2-2 page 105: steps to each of 50 random battles in the Ruined Shrine Cave (St00_0010), version
    1.03, walking a corridor of five steps; merchants and smiths counted as battles. Without a sealbook, 19.64 steps
    when every battle was fled and 22.96 when every enemy was killed; with the Mangochin sealbook (one piece of
    enchantment 214, encounter rate GrandUP), 15.08 and 22.68. A won battle is followed by the grace of the code;
    a fled one is not (the flag of 0x4bc770 is not set). The model must fall within two standard errors of a mean
    of 50 draws."""
    MEASURED = {(False, ()): 19.64, (True, ()): 22.96, (False, (214,)): 15.08, (True, (214,)): 22.68}

    def test_the_mean_steps_fall_within_the_spread_of_fifty_battles(self):
        zone = next(fl for fl in game_data().floors if fl['floor'] == 'St00_0010')['encounter']
        for (won, pieces), measured in self.MEASURED.items():
            chance = progression.encounter_chance(zone, pieces=pieces) / 100
            model = progression.steps_between_battles(zone, pieces=pieces,
                                                      grace=progression.ENCOUNTER_GRACE if won else 0)
            spread = math.sqrt(1 - chance) / chance / math.sqrt(50)
            with self.subTest(won=won, pieces=pieces):
                self.assertLess(abs(model - measured), 2 * spread)


class GenerousHeart(unittest.TestCase):
    def test_two_maids_reach_the_cap(self):
        """K08, atwiki dt2-2 page 120 and GameFAQs (Class Skill info - Maid): Maid Mastery adds a point per level
        to Generous Heart (12% becomes 22% at its top); with two members who have both, the party recovers 30% of
        max HP and TP after a battle, and no more."""
        data = game_data()
        skill = next(s for s in data.skills.values() if s.name == 'Generous Heart')
        mastery = next(s for s in data.skills.values() if s.name == 'Maid Mastery')
        maid = Unit('maid', PARTY, 1, 1, 0, {s: 1 for s in STATS})
        maid.passives[278] = mastery.effects[0][2][-1]
        top = Action(maid, 'skill', skill, len(skill.effects[0][2]))
        hp, tp = top.value(272), top.value(273)
        self.assertAlmostEqual(hp, 0.22)
        self.assertAlmostEqual(progression.after_battle_fraction([hp, hp]), 0.30)
        self.assertAlmostEqual(progression.after_battle_fraction([tp, tp]), 0.30)
        self.assertLess(progression.after_battle_fraction([hp]), 0.30)
        self.assertEqual(progression.after_battle_recovery(1000, 0.30), 300)
        self.assertEqual(progression.after_battle_recovery(1000, 0.0, full=True), 1000)


if __name__ == '__main__':
    unittest.main()
