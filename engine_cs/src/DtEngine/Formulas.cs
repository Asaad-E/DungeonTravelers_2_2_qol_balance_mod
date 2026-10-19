using System;
using System.Collections.Generic;

namespace DtEngine
{
    /// <summary>The battle formulas as pure functions, in the order of operations of the program (docs/FORMULAS.md).</summary>
    public static class F
    {
        public const double HIT_SCALE = 0.885;
        public const double HIT_MIN = 5.0, HIT_MAX = 100.0;
        public const double MAGIC_HIT_PER_POINT = 0.002;
        public const double MAGIC_HIT_MIN = 25.0, MAGIC_HIT_MAX = 95.0;
        public const double ATTACK_BASE = 2.0;
        public const double DEFENCE_FACTOR = 1.35;
        public const double MAGIC_DEFENCE_FACTOR = 1.5;
        public const double RESIST_PER_POINT = 0.5;
        public const double DEFENDING = 0.5;
        public const double DAMAGE_CUT_FLOOR = 0.75;
        public const double INTERRUPT_HP_FACTOR = 1.5;
        public const double INTERRUPT_MAX = 0.95;
        public const int INTERRUPT_CRITICAL = 33;
        public const double SPEED_STAT_BASE = 100.0, SPEED_STAT_DIV = 200.0;
        public const double WEIGHT_DIV = 12.0;
        public const double SPEED_HALF = 0.5;
        public const double SLOW = 0.5;
        public const double SPEED_BONUS_MIN = -0.5, SPEED_BONUS_MAX = 0.5;
        public const double DEFEND_SPEED = 1.15;
        public const double ESCAPE_SPEED = 1.20;
        public const double VALUE_CAP = 0.92;
        public static readonly double[] SPEED_RANDOM = { 0.0, 0.01, 0.02, 0.03, 0.04, 0.05 };
        public const double CRIT_DEX = 0.2;
        public const double CRIT_LEVEL = 0.5;
        public const double CRIT_UP = 4.0, CRIT_MINI_UP = 2.0;
        public const double CRIT_ENCHANT_MAX = 50.0, CRIT_ENCHANT_MIN = -50.0;
        public const double CRIT_PER_EARLIER_HIT = 5.0;
        public const double CRIT_MIN = 5.0, CRIT_MIN_268 = 20.0, CRIT_MAX = 50.0;
        public const double CRIT_FACTOR = 1.25;
        public const int MAGIC_CRIT_CHANCE = 20;
        public const double MAGIC_CRIT_FACTOR = 1.25;
        public const int MIN_DAMAGE = 3;
        public const int SLEEP_NUM = 3, SLEEP_DEN = 2;
        public const double TP_CONVERSION_UP = 0.05, TP_CONVERSION_MINI = 0.1;
        public const double TP_CONVERSION_MAX = 0.5;
        public const int TP_CONVERSION_FLOOR = 1, TP_CONVERSION_FLOOR_73 = 5;

        /// <summary>The mean of the six speed draws as the policies take it: sum(values) / len(values).</summary>
        public static readonly double SPEED_RANDOM_MEAN = MeanOf(SPEED_RANDOM);

        static double MeanOf(double[] v)
        {
            var s = new PySum();
            foreach (var x in v) s.AddFloat(x);
            return s.Result / v.Length;
        }

        // PLAIN_ATTACK_ENCHANTS, in the order of the dict
        public static readonly (int enchant, int effect, double value)[] PLAIN_ATTACK_ENCHANTS =
        {
            (161, 75, 0.5), (162, 75, 0.15), (163, 76, 0.2), (164, 76, 0.05),
            (153, 113, 0.18), (154, 116, 0.15), (155, 117, 0.18), (156, 114, 0.18), (157, 115, 0.15),
            (158, 118, 0.12), (159, 120, 0.1), (165, 122, 0.12), (197, 119, 0.75), (160, 119, 0.07),
        };

        // ENCHANT_SHARE: enchantment -> (figure, divisor, floor); figure 0 hp, 1 tp, 2.. the six stats
        public static readonly Dictionary<int, (int figure, int divisor, int floor)> ENCHANT_SHARE = BuildShare();
        public const int FIG_HP = -1, FIG_TP = -2; // otherwise the index of the stat 0..5 (atk, def, int, res, dex, agi)

        static Dictionary<int, (int, int, int)> BuildShare()
        {
            var d = new Dictionary<int, (int, int, int)>();
            int[] figs = { FIG_HP, FIG_TP, 0, 1, 2, 3, 4, 5 };
            for (int g = 0; g < 8; g++)
            {
                d[g * 3] = (figs[g], 10, 4);
                d[g * 3 + 1] = (figs[g], 20, 2);
                d[g * 3 + 2] = (figs[g], -10, 0);
            }
            return d;
        }

        public static readonly Dictionary<int, int> ENCHANT_ALL_STATS = new Dictionary<int, int> { { 24, 1 }, { 25, 3 }, { 26, 6 }, { 27, 9 }, { 28, 12 } };

        public static readonly Dictionary<int, (int index, int value)[]> ENCHANT_RESIST = BuildResist();

        static (int, int)[] Elem(int v) => new[] { (3, v), (4, v), (5, v), (6, v), (7, v) };
        static (int, int)[] Phys(int v) => new[] { (0, v), (1, v), (2, v) };

        static Dictionary<int, (int, int)[]> BuildResist()
        {
            var d = new Dictionary<int, (int, int)[]>();
            void One(int e, int i, int v) { d[e] = new[] { (i, v) }; }
            One(88, 3, 20); One(89, 3, 10); One(90, 3, -20); One(91, 4, 20); One(92, 4, 10); One(93, 4, -20);
            One(94, 5, 20); One(95, 5, 10); One(96, 5, -20); One(97, 6, 20); One(98, 6, 10); One(99, 6, -20);
            One(100, 7, 20); One(101, 7, 10); One(102, 7, -20);
            d[103] = Elem(50); d[104] = Elem(15); d[105] = Elem(7); d[106] = Elem(-15);
            One(107, 0, 20); One(108, 0, 10); One(109, 0, -20); One(110, 1, 20); One(111, 1, 10); One(112, 1, -20);
            One(113, 2, 20); One(114, 2, 10); One(115, 2, -20);
            d[116] = Phys(25); d[117] = Phys(10); d[118] = Phys(5); d[119] = Phys(-10);
            One(310, 3, 100); One(311, 3, 50); One(312, 3, -50); One(315, 4, 100); One(316, 4, 50); One(317, 4, -50);
            One(320, 5, 100); One(321, 5, 50); One(322, 5, -50); One(325, 6, 100); One(326, 6, 50); One(327, 6, -50);
            One(330, 7, 100); One(331, 7, 50); One(332, 7, -50);
            d[335] = Elem(75); d[336] = Elem(-30);
            One(340, 0, 100); One(341, 0, 50); One(342, 0, -50); One(345, 1, 100); One(346, 1, 50); One(347, 1, -50);
            One(350, 2, 100); One(351, 2, 50); One(352, 2, -50);
            d[355] = Phys(50); d[356] = Phys(-20);
            return d;
        }

        public const int ENCHANT_RESIST_CAP = 100;

        // ENCHANT_LINE: enchantment -> (front line, [(stat index, share)]); a share below 1 is int(stat * share), else int(stat / share)
        public static readonly Dictionary<int, (bool front, (int stat, double share)[] shares)> ENCHANT_LINE =
            new Dictionary<int, (bool, (int, double)[])>
            {
                { 222, (true, new[] { (0, 0.08) }) },
                { 223, (true, new[] { (0, 25.0), (1, 25.0) }) },
                { 224, (false, new[] { (2, 0.08) }) },
                { 225, (false, new[] { (2, 25.0), (3, 25.0) }) },
                { 281, (false, new[] { (4, 50.0), (5, 50.0) }) },
            };

        public static readonly (int enchant, int ailment)[] ENCHANT_NULLIFY_AILMENT =
            { (129, 118), (130, 114), (131, 113), (132, 116), (133, 117), (134, 119), (135, 120), (136, 115), (139, 122) };
        public const int ENCHANT_NULLIFY_ALL = 137;

        // RACE_ATTACK: race -> [(enchantment, share)]
        public static readonly Dictionary<int, (int enchant, double share)[]> RACE_ATTACK = new Dictionary<int, (int, double)[]>
        {
            { 8, new[] { (170, 0.3), (171, 0.15), (203, 0.6) } },
            { 7, new[] { (172, 0.3), (173, 0.15), (204, 0.6) } },
            { 6, new[] { (174, 0.3), (175, 0.15), (205, 0.6) } },
            { 4, new[] { (176, 0.6), (177, 0.3), (178, 0.15) } },
            { 5, new[] { (179, 0.3), (180, 0.15), (206, 0.6) } },
            { 9, new[] { (181, 0.3), (182, 0.15), (207, 0.6) } },
            { 2, new[] { (183, 0.3), (184, 0.15), (208, 0.6) } },
            { 0, new[] { (185, 1.0), (186, 0.5) } },
        };

        public static readonly HashSet<int> FELINES = new HashSet<int>
        {
            210, 211, 212, 215, 216, 217, 220, 221, 222, 250, 251, 252, 253, 290, 291, 292, 805, 806, 807, 810, 811, 812, 1000,
        };
        public static readonly HashSet<int> SEA_CREATURES = new HashSet<int>
        {
            59, 60, 61, 101, 102, 103, 104, 193, 194, 195, 204, 205, 206, 207, 215, 216, 217, 257, 783, 784, 785, 799, 839, 840, 842,
        };
        // RACE_SPECIAL: [(196, FELINES), (209, SEA_CREATURES)]
        public static readonly (int enchant, HashSet<int> ids)[] RACE_SPECIAL = { (196, FELINES), (209, SEA_CREATURES) };

        public static readonly Dictionary<int, (int small, int large)> RACE_GUARD = new Dictionary<int, (int, int)>
        {
            { 8, (227, 228) }, { 7, (229, 230) }, { 6, (231, 232) }, { 4, (233, 234) }, { 5, (235, 236) }, { 9, (237, 238) },
            { 2, (239, 240) }, { 0, (241, 242) }, { 3, (243, 244) },
        };
        public const double RACE_GUARD_SHARE_SMALL = 0.05, RACE_GUARD_SHARE_LARGE = 0.10;

        /// <summary>attribute -> both-sides enchantment (4 fire .. 8 lightning)</summary>
        public static int BothSidesElement(int attr)
        {
            switch (attr)
            {
                case 4: return 251;
                case 5: return 252;
                case 6: return 253;
                case 7: return 254;
                case 8: return 255;
                default: return -1;
            }
        }
        public const double ELEMENT_ENCHANT_SHARE = 0.2;
        public static readonly List<int> DEMON_WALL_RACES = new List<int> { 5, 7, 8 };   // the attacker races Demon Wall stops (0x557e1c, 0x557e7c, 0x557eac)
        public const double ELEMENT_BOOST_CAP = 0.4;          // the element boost of a spell is at most 0.4 (0x44e409, 0x44e41e)
        public const int FULL_HP_BONUS_ENCHANT = 271;
        // enchantments 219 and 220: +0.1 a piece to the other bonus of a blow or a spell when the target's level is above (219) or
        // below (220) the attacker's (0x44ca01 - 0x44ca8b, 0x44ecc1 - 0x44ed4b)
        public const int HIGHER_LEVEL_ENCHANT = 219, LOWER_LEVEL_ENCHANT = 220;
        public const double LEVEL_BONUS_SHARE = 0.1;
        // enchantment 264: +0.02 to the class weapon modifier of the stats when any piece carries it (0x4f7fb0 - 0x4f7fd9)
        public const int WEAPON_MODIFIER_ENCHANT = 264;
        // a missed spell deals half its damage, three quarters with enchantment 272; at 0 or less it deals 1 to 5 (0x44ee33 - 0x44ee81)
        public const int MISSED_SPELL_ENCHANT = 272, SPELL_FLOOR_ROLL = 5;
        // the recovery of the enchantments every turn, state 16 (0x437bb5 - 0x437dfb): (enchantment, share of max HP a piece, floor)
        public static readonly (int enchant, double share, int floor)[] HP_REGEN_ENCHANTS = { (144, 0.04, 4), (145, 0.02, 2), (148, 0.08, 10) };
        public const int FULL_RECOVERY_ENCHANT = 296, FULL_RECOVERY_CHANCE = 4;
        public static readonly (int enchant, int amount)[] TP_REGEN_ENCHANTS = { (146, 4), (147, 2), (149, 6) };
        // enchantments 257 and 292: what a defending unit recovers (0x4197ae - 0x41982c, 0x419843 - 0x4198a6)
        public const int DEFEND_HP_ENCHANT = 257, DEFEND_TP_ENCHANT = 292, DEFEND_HP_FLOOR = 10, DEFEND_TP_FLOOR = 5;
        public const double DEFEND_HP_SHARE = 0.2, DEFEND_TP_SHARE = 0.1;
        public const double WEAPON_MODIFIER_UP = 0.02;
        // enchantment 293: +1 to the rank of the bearer's own unique skill when it is 1 to 8 (0x4f716e - 0x4f7186)
        public const int UNIQUE_RANK_ENCHANT = 293;
        public const double FULL_HP_BONUS_SHARE = 0.1;
        public const int MAGIC_USER_LOW = 12, MAGIC_USER_HIGH = 20; // range(12, 20)
        public const int AILING_ENCHANT = 280;
        public const double AILING_SHARE = 0.15;

        public static readonly int[][] TARGET_SHARE =
        {
            new[] { 100 }, new[] { 50, 50 }, new[] { 60, 40 }, new[] { 33, 34, 33 }, new[] { 38, 38, 24 }, new[] { 40, 30, 30 },
            new[] { 28, 28, 28, 16 }, new[] { 30, 30, 20, 20 }, new[] { 31, 23, 23, 23 }, new[] { 24, 24, 24, 14, 14 },
            new[] { 26, 26, 16, 16, 16 },
        };
        public const int ENMITY_UP = 10, ENMITY_DOWN = 5, ENMITY_MIN = 10;

        public static readonly double[] HEAL_RANDOM = { 0.48, 0.49, 0.50, 0.51, 0.52 };
        public const double DOLL_HEAL_SCALE = 20.0;
        public const double DOLL_HEAL_UP = 0.02, DOLL_HEAL_MINI_UP = 0.01, DOLL_HEAL_MAX = 0.05;

        public const int SHORT = 0, MID = 1, LONG = 2, NO_RANGE = 3;

        // --- functions ---------------------------------------------------------------------------------------
        public static double Single(double v) => (double)(float)v;

        public static double Clamp(double v, double lo, double hi) => Math.Max(lo, Math.Min(hi, v));

        public static double TurnValue(double stat, double weight, double level, double actionFactor, double bonus, bool slowed,
                                       bool defending, bool escaping, double random)
        {
            double b = (stat + SPEED_STAT_BASE) / SPEED_STAT_DIV;
            double speed = (b * (1 + random) - (weight / WEIGHT_DIV) * (1 + level / 100.0)) * actionFactor * SPEED_HALF;
            if (slowed) speed *= SLOW;
            double value = speed * (1 + bonus);
            if (defending) value *= DEFEND_SPEED;
            if (escaping) value *= ESCAPE_SPEED;
            return Math.Min(VALUE_CAP, value);
        }

        public static double SpeedEnchantBonus(int up, int miniUp, int down, double perUp = 0.10, double perMini = 0.05, double perDown = 0.10)
        {
            return Clamp(up * perUp + miniUp * perMini - down * perDown, SPEED_BONUS_MIN, SPEED_BONUS_MAX);
        }

        public static double PhysicalHit(double dex, double targetAgi, double skillAccuracy, double buffs, double targetBuffs,
                                         double enchant, double targetEnchant, double divisor)
        {
            double a = HIT_SCALE * (100 + dex) / (100 + targetAgi) + skillAccuracy;
            double b = (buffs - targetBuffs + a) * 100;
            return Clamp((b + enchant - targetEnchant) / divisor, HIT_MIN, HIT_MAX);
        }

        public static double AttackValue(double atk, double modifiers, double enchant, double swing)
        {
            return atk * (ATTACK_BASE + swing) * (1 + modifiers) * (1 + enchant * 0.01);
        }

        public static double DefenceValue(double defence, double modifiers, double enchant)
        {
            return defence * DEFENCE_FACTOR * (1 + modifiers) * (1 + enchant * 0.01);
        }

        public static double ResistanceFactor(double resistance) => (100 - resistance * RESIST_PER_POINT) * 0.01;

        public static double PhysicalDamage(double atk, double targetDef, double modifiers, double targetModifiers, double enchant,
                                            double targetEnchant, double swing, double times, bool ignoreDefence, double rangeFactor,
                                            double damageCut, double race, double resistance, bool defending, double critical,
                                            double other)
        {
            double defence = ignoreDefence ? 0.0 : DefenceValue(targetDef, targetModifiers, targetEnchant);
            double a = AttackValue(atk, modifiers, enchant, swing) * times - defence;
            double b = a * rangeFactor * Math.Max(DAMAGE_CUT_FLOOR, damageCut);
            double c = b * race * ResistanceFactor(resistance) * 1.0 * (defending ? DEFENDING : 1.0) * critical;
            return Math.Max(0.0, c * (1 + other));
        }

        public static double MagicHit(double spellAccuracy, double intel, double targetRes, double looseSpirit, double enchant,
                                      double targetEnchant, double buffs, double targetEvasion, double divisor)
        {
            double a = spellAccuracy + (intel - targetRes) * MAGIC_HIT_PER_POINT + looseSpirit;
            double b = a * 100 + enchant - targetEnchant;
            return Clamp(b * (1 + buffs) / divisor * (1 - targetEvasion), MAGIC_HIT_MIN, MAGIC_HIT_MAX);
        }

        public static double MagicDamage(double intel, double power, double targetRes, double mastery, double modifiers, double enchant,
                                         double secondModifiers, double elementBoost, double targetModifiers, double targetEnchant,
                                         double swing, double powerBoost, double damageCut, double resistance, double critical,
                                         double other)
        {
            double a = intel * (ATTACK_BASE + swing);
            double b = (a + power * (1 + mastery) * (1 + modifiers)) * (1 + enchant * 0.01);
            double c = b * (1 + secondModifiers) * (1 + elementBoost);
            double defence = targetRes * MAGIC_DEFENCE_FACTOR * (1 + targetModifiers) * (1 + targetEnchant * 0.01);
            double damage = (c - defence) * (1 + powerBoost) * (1 + damageCut) * ResistanceFactor(resistance);
            return Math.Max(0.0, damage * (1 + other) * critical);
        }

        public static double InterruptionChance(double damage, double maxHp, double modifier, double enchant, bool critical, bool physical,
                                                bool product)
        {
            double rate = 0.0;
            if (physical)
            {
                double divisor = product ? maxHp * INTERRUPT_HP_FACTOR * (1 + modifier) : maxHp * INTERRUPT_HP_FACTOR + (1 + modifier);
                double a = Clamp(damage / divisor, 0.0, INTERRUPT_MAX);
                rate = PyMath.Int(Clamp(a - enchant, 0.0, INTERRUPT_MAX) * 100) / 100.0;
            }
            if (critical) rate = 1 - (1 - rate) * (1 - INTERRUPT_CRITICAL / 100.0);
            return rate;
        }

        public static double CriticalEnchant(int up, int miniUp) => Math.Min(CRIT_ENCHANT_MAX, CRIT_UP * up + CRIT_MINI_UP * miniUp);

        public static double CriticalRate(double dex, double targetAgi, double level, double targetLevel, double skill, double enchant,
                                          double targetEnchant, int earlierHits, bool floor268, bool hasFixed, double fixedValue)
        {
            if (hasFixed) return fixedValue * 100.0;
            double a = (dex + targetAgi) != 0 ? (dex * CRIT_DEX) / (dex + targetAgi) * 100.0 : 0.0;
            double b = Math.Max(0.0, (level - targetLevel) * CRIT_LEVEL);
            double rate = (a + b + skill) * (1 + Math.Min(CRIT_ENCHANT_MAX, enchant) * 0.02) * (1 + Math.Max(CRIT_ENCHANT_MIN, targetEnchant) * 0.02);
            rate += CRIT_PER_EARLIER_HIT * earlierHits;
            return Clamp(rate, floor268 ? CRIT_MIN_268 : CRIT_MIN, CRIT_MAX);
        }

        public static double ExpectedCriticalFactor(double rate) => 1.0 + (CRIT_FACTOR - 1.0) * PyMath.Int(rate) / 100.0;

        public static int Distance(bool attackerBack, bool targetBack) => (attackerBack ? 1 : 0) + (targetBack ? 1 : 0);

        public static double RangeFactor(int attackRange, int dist)
        {
            if (attackRange == SHORT) return dist == 0 ? 1.0 : dist == 1 ? 0.75 : 0.5;
            if (attackRange == MID) return dist == 2 ? 0.75 : 1.0;
            return 1.0;
        }

        public static double AilmentChance(double baseValue, double resistance)
        {
            double chance = baseValue * 100.0;
            int steps = PyMath.Int(resistance / 10);
            return chance - steps * chance / 10.0 - 0.0;
        }

        public static int AilmentThreshold(double baseValue, double resistance)
        {
            double chance = Single(Single(baseValue) * 100.0);
            int steps = PyMath.Int(resistance / 10);
            return PyMath.Int(Single(chance - Single(Single(steps * chance) / 10.0)));
        }

        public static int TargetWeight(int share, double provoked, int up, int down)
        {
            return Math.Max(ENMITY_MIN, share + PyMath.Int(provoked) + ENMITY_UP * up - ENMITY_DOWN * down);
        }

        public static double DollHealBonus(double effect286, int up, int miniUp)
        {
            return DOLL_HEAL_SCALE * effect286 + DOLL_HEAL_SCALE * Math.Min(DOLL_HEAL_MAX, DOLL_HEAL_UP * up + DOLL_HEAL_MINI_UP * miniUp);
        }

        public static int Heal(double res, double coefficient, double mastery, bool hasCap, double cap, double capBonus, double random)
        {
            int amount = PyMath.Int(res * random * coefficient * (1 + mastery));
            if (hasCap)
            {
                int limit = PyMath.Int(cap);
                limit += PyMath.Int(limit * capBonus);
                amount = Math.Min(amount, limit);
            }
            return amount;
        }

        public static int FractionRecovery(double maximum, double value, bool hasCap, double cap)
        {
            int amount = PyMath.Int(maximum * value);
            return hasCap ? Math.Min(amount, PyMath.Int(cap)) : amount;
        }

        /// <summary>sim.progression.after_battle_recovery</summary>
        public static int AfterBattleRecovery(double maximum, double fraction, bool full)
        {
            fraction = full ? 1.0 : fraction;
            return fraction > 0 ? Math.Max(1, PyMath.Int(maximum * fraction)) : 0;
        }

        /// <summary>sim.progression.after_battle_fraction(values, extras)</summary>
        public static double AfterBattleFraction(List<double> values, List<double> extras)
        {
            var s = new PySum();
            foreach (var v in values) s.AddFloat(v);
            double a = values.Count == 0 ? 0.0 : s.Result;
            double cap = Math.Min(0.30, a);
            var e = new PySum();
            foreach (var v in extras) e.AddFloat(v);
            double b = extras.Count == 0 ? 0.0 : e.Result;
            return cap + b;
        }
    }
}
