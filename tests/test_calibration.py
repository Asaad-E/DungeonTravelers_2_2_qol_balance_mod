"""The data of the game against what players measured (sheet Calibration of data_tables/sim_setup.xlsx, rows K06, K07 and
the after-battle part of K08; the rows the battle engine plays, K01 - K05 and K08, are engine_cs/tests/DtEngine.Tests/
CalibrationTests.cs). Moved from the tests of the Python simulator when it was removed (2026-10-16). The figures are the
players' own and are copied here only as the expected results of a test."""
import math
import sys
import unittest

import _paths
sys.path.insert(0, _paths.PROJECT_DIR)
from gamedata import progression
from gamedata.data import game_data


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
        """K08, atwiki dt2-2 page 120 and GameFAQs (Class Skill info - Maid): with two members who have Generous Heart and
        Maid Mastery at their top (22% of HP, 19% of TP each; CalibrationTests.K08 checks those), the party recovers 30%
        of max HP and TP after a battle, and no more."""
        hp, tp = 0.22, 0.19
        self.assertAlmostEqual(progression.after_battle_fraction([hp, hp]), 0.30)
        self.assertAlmostEqual(progression.after_battle_fraction([tp, tp]), 0.30)
        self.assertLess(progression.after_battle_fraction([hp]), 0.30)
        self.assertEqual(progression.after_battle_recovery(1000, 0.30), 300)
        self.assertEqual(progression.after_battle_recovery(1000, 0.0, full=True), 1000)


if __name__ == '__main__':
    unittest.main()
