using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DtEngine;
using Xunit;
using F = DtEngine.F;

namespace DtEngine.Tests
{
    /// The engine against what players measured in the game (sheet Calibration of data_tables/sim_setup.xlsx, rows K01 - K05
    /// and K08; K06, K07 and the after-battle part of K08 are data and live in tests/test_calibration.py). Each test names its
    /// row and the page the figures come from; the figures are the players' own, copied here only as expected results.
    /// Moved here from the Python simulator's tests when it was removed (2026-10-16).
    public class CalibrationTests
    {
        static string Root()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null && !File.Exists(Path.Combine(dir.FullName, "CONTRIBUTING.md"))) dir = dir.Parent;
            return dir.FullName;
        }

        static GameData Vanilla()
        {
            string path = Path.Combine(Root(), "build", "engine_snapshot.json");
            return Snapshot.Load(path).Sides["vanilla"];
        }

        static double Wait(double stat, double weight, double level, double bonus, bool defending = false)
            => 1.0 - F.TurnValue(stat, weight, level, 1.0, bonus, false, defending, false, 0.025);   // the mean of the draws

        static Unit Member(string name, int[] stats, double swing = 0.0)
        {
            var u = new Unit(name, Unit.PARTY, 1, 1, 0, stats, null, 0.0, swing, T.NONE, Kind.Member);
            u.Pv = Enumerable.Repeat(double.NaN, GameData.MaxEffect).ToArray();
            return u;
        }

        [Fact]
        public void K01_TurnOrderReproducesTheSpeedTestOfTheJapaneseWiki()
        {
            // atwiki dt2-2 page 105: A (rank A, AGI 261, five speed UP) and B (rank B, AGI 47, n speed UP) only defend; turns of A
            // during 10 turns of B were 80, 76, 71, 67, 63, 58, 58 for n = 0..6. B is a level 1 crowned character. No constant fitted.
            int[] measured = { 80, 76, 71, 67, 63, 58, 58 };
            double waitA = Wait(261, 1.20, 1, F.SpeedEnchantBonus(5, 0, 0), true);
            Assert.Equal(0.08, waitA, 9);                                   // A sits on the cap
            for (int n = 0; n < measured.Length; n++)
            {
                double waitB = Wait(47, 1.60, 1, F.SpeedEnchantBonus(n, 0, 0), true);
                Assert.InRange(10 * waitB / waitA, measured[n] - 0.7, measured[n] + 0.7);
            }
        }

        [Fact]
        public void K02_EachPieceShortensTheChantUntilTheThird()
        {
            // atwiki dt2-2 page 105: the turns of a capped unit while another chants Resurrect Lv1 ten times fell with each piece
            // of chant speed UP (61, 51, 40, 31) and not with the fourth (31). The code (0x449f5e - 0x44a1d4): 0.20 a piece, kept
            // at 0.5, reached by the third. This checks the shape (assumption A30).
            var wait = Enumerable.Range(0, 5).Select(n => Wait(84, 1.6, 50, F.SpeedEnchantBonus(n, 0, 0, 0.20, 0.10, 0.20))).ToArray();
            for (int i = 0; i < 3; i++) Assert.True(wait[i] > wait[i + 1]);
            Assert.Equal(wait[3], wait[4], 12);
        }

        [Fact]
        public void K03_TheSealbookTestFitsAQuarterMore()
        {
            // atwiki dt2-2 page 105 (Heqet sealbook): unarmed hits of Yae and Luco on Hola-Orange went from 170 to 213 and from 52
            // to 65 on a critical hit; damage is kept as an integer after the factor.
            foreach (var (normal, critical) in new[] { (170, 213), (52, 65) })
            {
                double low = Math.Max(normal, critical / F.CRIT_FACTOR);
                double high = Math.Min(normal + 1, (critical + 1) / F.CRIT_FACTOR);
                Assert.True(low < high);
            }
        }

        [Fact]
        public void K04_EveryMeasuredDaedalusAttackFallsInTheRangeOfTheFormula()
        {
            // atwiki dt2-2 page 105: one hit of Daedalus Attack Lv10 by crowned Yae, level 99, with Lance Mastery Lv10, against
            // Hola-Orange, with the ATK of the status screen. Every measured hit falls inside the range the formula gives over the
            // swing of the weapon, within 2% (the Gabas Ring worn with the Lance is not identified). The range is taken over many
            // draws of the swing.
            var data = Vanilla();
            var skill = data.SkillList.First(s => s.Name == "Daedalus Attack");
            int enemyId = data.Enemies.First(kv => kv.Value.Name == "Hola-Orange").Key;
            var cases = new[] { ("Lance", 251, (790, 841), (970, 1062)), ("Heavy Lance", 251, (901, 1001), (1097, 1245)),
                                ("Don Quixote", 262, (826, 896), (1056, 1120)) };
            foreach (var (name, atk, normal, critical) in cases)
            {
                var weapon = data.Equipment.Values.First(p => p.Name == name);
                var stats = new[] { atk, 1, 1, 1, 1, 1 };
                var member = Member("Yae", stats, weapon.Swing);
                member.Level = 99;
                member.Weapon = weapon; member.AttackRange = weapon.Range; member.AttackAttr = weapon.Attr;
                var target = UnitFactory.BuildEnemy(data, enemyId, true);
                var battle = new Battle(data, new List<Unit> { member }, new List<Unit> { target }, new PyRandom(0), null, new BattleOptions(), null);
                var action = new Action(member, AKind.Skill, skill, 10);
                foreach (var (measured, crit) in new[] { (normal, false), (critical, true) })
                {
                    double low = double.MaxValue, high = double.MinValue;
                    for (int k = 0; k < 4000; k++)
                    {
                        double v = battle.PhysicalDamageValue(action, target, 0, 1.0, false, crit, out _);
                        low = Math.Min(low, v); high = Math.Max(high, v);
                    }
                    Assert.True(measured.Item1 >= low * 0.98, $"{name} crit={crit}: {measured.Item1} under {low}");
                    Assert.True(measured.Item2 <= high * 1.02, $"{name} crit={crit}: {measured.Item2} over {high}");
                }
            }
        }

        [Fact]
        public void K05_SummonStatsAreTheBestOfThePartyTimesTheFactorOfTheForm()
        {
            // atwiki dt2-2 page 105: [best stat of the party, stat of the summon] pairs, and the lowest stats.
            var data = Vanilla();
            var lowest = new Dictionary<string, int[]> { { "Bigfoot", new[] { 33, 31, 16, 24, 17, 10 } },
                                                         { "Ghast", new[] { 45, 42, 15, 33, 21, 17 } },
                                                         { "Cupid", new[] { 49, 44, 19, 37, 24, 23 } } };
            foreach (var kv in lowest)
            {
                var form = data.Summons.Where(s => s.Name == kv.Key).OrderBy(s => s.Level).First();
                var unit = UnitFactory.BuildSummon(data, form, new List<Unit> { Member("test", new[] { 1, 1, 1, 1, 1, 1 }) }, 1);
                Assert.Equal(kv.Value, unit.Base);
            }
            string[] names = { "atk", "def", "int", "res", "dex", "agi" };
            var pairs = new (string summon, int level, string stat, (int best, int measured)[] values)[]
            {
                ("Bigfoot", 13, "atk", new[] { (19, 38), (21, 42), (22, 44), (24, 48), (25, 51) }),
                ("Bigfoot", 13, "def", new[] { (23, 35), (24, 36), (25, 38) }),
                ("Bigfoot", 13, "int", new[] { (24, 18), (25, 19), (27, 20), (28, 21) }),
                ("Bigfoot", 13, "dex", new[] { (19, 18), (20, 19), (22, 20), (23, 21), (26, 24), (27, 25), (29, 27), (30, 28) }),
                ("Bigfoot", 13, "agi", new[] { (13, 11), (15, 13), (17, 15), (19, 17), (20, 18), (21, 19), (22, 20), (23, 20), (24, 21), (26, 23), (27, 24) }),
                ("Ghast", 12, "atk", new[] { (23, 46), (24, 48), (25, 50) }),
                ("Ghast", 12, "agi", new[] { (26, 18) }),
                ("Ghast", 18, "atk", new[] { (22, 50), (27, 61) }),
                ("Ghast", 18, "int", new[] { (28, 17) }),
                ("Ghast", 18, "dex", new[] { (30, 25) }),
                ("Ghast", 18, "agi", new[] { (27, 22) }),
                ("Cupid", 15, "int", new[] { (22, 20), (24, 22), (27, 24), (28, 25) }),
                ("Cupid", 15, "dex", new[] { (23, 25), (26, 29), (29, 32), (30, 33) }),
                ("Cupid", 15, "agi", new[] { (27, 24) }),
            };
            foreach (var (summon, level, stat, values) in pairs)
            {
                var form = data.Summons.First(s => s.Name == summon && s.Level == level);
                int at = Array.IndexOf(names, stat);
                foreach (var (best, measured) in values)
                {
                    var stats = new[] { 1, 1, 1, 1, 1, 1 };
                    stats[at] = best;
                    var unit = UnitFactory.BuildSummon(data, form, new List<Unit> { Member("test", stats) }, 1);
                    Assert.True(unit.Base[at] == measured, $"{summon} {level} {stat} {best}: {unit.Base[at]}, measured {measured}");
                }
            }
        }

        [Fact]
        public void K08_MaidMasteryTakesGenerousHeartTo22Percent()
        {
            // atwiki dt2-2 page 120 and GameFAQs (Class Skill info - Maid): Maid Mastery adds a point per level to Generous Heart
            // (12% becomes 22% at its top). The cap of two maids at 30% is in tests/test_calibration.py.
            var data = Vanilla();
            var skill = data.SkillList.First(s => s.Name == "Generous Heart");
            var mastery = data.SkillList.First(s => s.Name == "Maid Mastery");
            var maid = Member("maid", new[] { 1, 1, 1, 1, 1, 1 });
            var bonus = mastery.Effects.First(e => e.Id == 278).Values;
            maid.Pv[278] = bonus[bonus.Length - 1];
            var top = new Action(maid, AKind.Skill, skill, skill.Levels);
            Assert.Equal(0.22, top.Val(272, 0.0), 9);
            Assert.Equal(0.19, top.Val(273, 0.0), 9);   // TP: 0.09 + 0.10
        }
    }
}
