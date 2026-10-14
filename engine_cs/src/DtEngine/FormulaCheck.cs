using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace DtEngine
{
    public static class FormulaCheck
    {
        static double D(JsonElement a, int i) => a[i].GetDouble();
        static int I(JsonElement a, int i) => (int)a[i].GetDouble();
        static bool B(JsonElement a, int i) => a[i].GetBoolean();

        /// <summary>Replays the calls of engine_cs/parity/formulas_golden.py; returns the number compared and the differences.</summary>
        public static (int compared, List<string> errors) Run(string path)
        {
            var errors = new List<string>();
            int compared = 0;
            using (var doc = JsonDocument.Parse(File.ReadAllBytes(path)))
            {
                foreach (var c in doc.RootElement.EnumerateArray())
                {
                    string fn = c.GetProperty("fn").GetString();
                    var a = c.GetProperty("args");
                    string expected = c.GetProperty("out").GetString();
                    string got;
                    switch (fn)
                    {
                        case "turn_value":
                            got = Fmt.Num(F.TurnValue(D(a, 0), D(a, 1), D(a, 2), D(a, 3), D(a, 4), B(a, 5), B(a, 6), B(a, 7), D(a, 8))); break;
                        case "speed_enchant_bonus":
                            got = Fmt.Num(F.SpeedEnchantBonus(I(a, 0), I(a, 1), I(a, 2), D(a, 3), D(a, 4), D(a, 5))); break;
                        case "physical_hit":
                            got = Fmt.Num(F.PhysicalHit(D(a, 0), D(a, 1), D(a, 2), D(a, 3), D(a, 4), D(a, 5), D(a, 6), D(a, 7))); break;
                        case "physical_damage":
                            got = Fmt.Num(F.PhysicalDamage(D(a, 0), D(a, 1), D(a, 2), D(a, 3), D(a, 4), D(a, 5), D(a, 6), D(a, 7), B(a, 8), D(a, 9), D(a, 10), D(a, 11), D(a, 12), B(a, 13), D(a, 14), D(a, 15))); break;
                        case "magic_hit":
                            got = Fmt.Num(F.MagicHit(D(a, 0), D(a, 1), D(a, 2), D(a, 3), D(a, 4), D(a, 5), D(a, 6), D(a, 7), D(a, 8))); break;
                        case "magic_damage":
                            got = Fmt.Num(F.MagicDamage(D(a, 0), D(a, 1), D(a, 2), D(a, 3), D(a, 4), D(a, 5), D(a, 6), D(a, 7), D(a, 8), D(a, 9), D(a, 10), D(a, 11), D(a, 12), D(a, 13), D(a, 14), D(a, 15))); break;
                        case "interruption_chance":
                            got = Fmt.Num(F.InterruptionChance(D(a, 0), D(a, 1), D(a, 2), D(a, 3), B(a, 4), B(a, 5), B(a, 6))); break;
                        case "critical_enchant":
                            got = Fmt.Num(F.CriticalEnchant(I(a, 0), I(a, 1))); break;
                        case "critical_rate":
                            got = Fmt.Num(F.CriticalRate(D(a, 0), D(a, 1), D(a, 2), D(a, 3), D(a, 4), D(a, 5), D(a, 6), I(a, 7), B(a, 8), B(a, 9), D(a, 10))); break;
                        case "expected_critical_factor":
                            got = Fmt.Num(F.ExpectedCriticalFactor(D(a, 0))); break;
                        case "ailment_chance":
                            got = Fmt.Num(F.AilmentChance(D(a, 0), D(a, 1))); break;
                        case "ailment_threshold":
                            got = Fmt.Num(F.AilmentThreshold(D(a, 0), D(a, 1))); break;
                        case "target_weight":
                            got = Fmt.Num(F.TargetWeight(I(a, 0), D(a, 1), I(a, 2), I(a, 3))); break;
                        case "doll_heal_bonus":
                            got = Fmt.Num(F.DollHealBonus(D(a, 0), I(a, 1), I(a, 2))); break;
                        case "heal":
                            got = Fmt.Num(F.Heal(D(a, 0), D(a, 1), D(a, 2), B(a, 3), D(a, 4), D(a, 5), D(a, 6))); break;
                        case "fraction_recovery":
                            got = Fmt.Num(F.FractionRecovery(D(a, 0), D(a, 1), B(a, 2), D(a, 3))); break;
                        case "single":
                            got = Fmt.Num(F.Single(D(a, 0))); break;
                        case "after_battle_recovery":
                            got = Fmt.Num(F.AfterBattleRecovery(D(a, 0), D(a, 1), B(a, 2))); break;
                        case "after_battle_fraction":
                            got = Fmt.Num(F.AfterBattleFraction(a[0].EnumerateArray().Select(x => x.GetDouble()).ToList(),
                                                                a[1].EnumerateArray().Select(x => x.GetDouble()).ToList())); break;
                        case "pysum":
                            {
                                var s = new PySum();
                                var items = a[0].EnumerateArray().ToList();
                                var ints = a[1].EnumerateArray().ToList();
                                for (int k = 0; k < items.Count; k++)
                                {
                                    if (ints[k].GetBoolean()) s.AddInt((long)items[k].GetDouble()); else s.AddFloat(items[k].GetDouble());
                                }
                                got = Fmt.Num(s.Result);
                                break;
                            }
                        default: throw new InvalidOperationException("unknown function " + fn);
                    }
                    compared++;
                    if (got != expected && errors.Count < 30) errors.Add(fn + " " + a + ": got " + got + ", expected " + expected);
                }
            }
            return (compared, errors);
        }
    }
}
