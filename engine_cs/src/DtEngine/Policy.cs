using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine
{
    /// <summary>sim/policy.py: what a party member does on its turn, by the rules of its role.</summary>
    public sealed class Policy
    {
        static readonly int[] HEAL_EFFECTS = { 103, 104, 128, 132 };
        static readonly int[] DOLL_EFFECTS = { 228, 229, 230, 231, 232, 233 };
        const string EVERY_ROLE = "*";

        enum Cond { Always, AllyHpBelow, PartyHpBelow, AllyDown, AllyTpBelow, SelfTpBelow, SelfHpBelow, EnemyBuffed, AllyAiling, TurnAtMost, EnemiesAtLeast, Boss, NoDoll, DollSlotFree }
        enum Act { Damage, Heal, Revive, Status, Dispel, Doll, Tp, Cure, Ailment, Item, Skill, Defend }

        sealed class Rule
        {
            public Cond Condition;
            public string CArg;
            public Act Action;
            public string AArg;
            public string ActionName;
        }

        readonly Dictionary<string, List<Rule>> rules = new Dictionary<string, List<Rule>>();
        readonly double tpWeight, tpReserve, punishedBlowFloor, healReserveCasts, partyBuffRecastShare, ailmentMinChance;

        public Policy(List<Row> policyRows, Setup setup)
        {
            double Get(string key, double dflt)
            {
                object v = setup.Setting(key);
                return v == null ? dflt : Setup.ToDouble(v);
            }
            // settings.get(key, default) or 0 : a missing or empty figure is the default
            tpWeight = Get("tp_weight", 0.0);
            tpReserve = Get("tp_reserve", 0.0);
            punishedBlowFloor = Get("punished_blow_floor", 0);
            healReserveCasts = Get("heal_reserve_casts", 0);
            partyBuffRecastShare = Get("party_buff_recast_share", 0);
            ailmentMinChance = Get("ailment_min_chance", 0.5);
            var sorted = policyRows.OrderBy(r => r.Str("Role"), StringComparer.Ordinal).ThenBy(r => r.Dbl("Order")).ToList();
            foreach (var r in sorted)
            {
                string c = r.Str("Condition"), a = r.Str("Action");
                string cond = c, cArg = null, act = a, aArg = null;
                int p = c.IndexOf(':');
                if (p >= 0) { cond = c.Substring(0, p); cArg = c.Substring(p + 1); }
                p = a.IndexOf(':');
                if (p >= 0) { act = a.Substring(0, p); aArg = a.Substring(p + 1); }
                var rule = new Rule { Condition = ParseCond(cond, r), CArg = cArg == "" ? null : cArg, Action = ParseAct(act, r), AArg = aArg == "" ? null : aArg, ActionName = act };
                string role = r.Str("Role");
                if (!rules.TryGetValue(role, out var list)) rules[role] = list = new List<Rule>();
                list.Add(rule);
            }
        }

        static Cond ParseCond(string name, Row r)
        {
            switch (name)
            {
                case "always": return Cond.Always;
                case "ally_hp_below": return Cond.AllyHpBelow;
                case "party_hp_below": return Cond.PartyHpBelow;
                case "ally_down": return Cond.AllyDown;
                case "ally_tp_below": return Cond.AllyTpBelow;
                case "self_tp_below": return Cond.SelfTpBelow;
                case "self_hp_below": return Cond.SelfHpBelow;
                case "enemy_buffed": return Cond.EnemyBuffed;
                case "ally_ailing": return Cond.AllyAiling;
                case "turn_at_most": return Cond.TurnAtMost;
                case "enemies_at_least": return Cond.EnemiesAtLeast;
                case "boss": return Cond.Boss;
                case "no_doll": return Cond.NoDoll;
                case "doll_slot_free": return Cond.DollSlotFree;
            }
            throw new InvalidOperationException("unknown condition " + name + " in role " + r.Str("Role"));
        }

        static Act ParseAct(string name, Row r)
        {
            switch (name)
            {
                case "damage": return Act.Damage;
                case "heal": return Act.Heal;
                case "revive": return Act.Revive;
                case "status": return Act.Status;
                case "dispel": return Act.Dispel;
                case "doll": return Act.Doll;
                case "tp": return Act.Tp;
                case "cure": return Act.Cure;
                case "ailment": return Act.Ailment;
                case "item": return Act.Item;
                case "skill": return Act.Skill;
                case "defend": return Act.Defend;
            }
            throw new InvalidOperationException("unknown action " + name + " in role " + r.Str("Role"));
        }

        // --- what a member can do ----------------------------------------------------------------------------
        public static bool UsableInBattle(Skill skill)
        {
            if (skill.IsTechnique) return (skill.Group & 0x10) != 0;
            if (skill.IsMagic) return (skill.Group & 0x08) != 0;
            return false;
        }

        public static bool WeaponAllows(Unit unit, Skill skill)
        {
            if (skill.Weapons.Length == 0) return true;
            var weapon = unit.Weapon;
            foreach (int code in skill.Weapons)
            {
                if (code == 0 && weapon != null && weapon.Range == 0) return true;
                if (code == 16 && unit.Shield) return true;
                if (weapon != null && weapon.Type + 1 == code) return true;
            }
            return false;
        }

        /// <summary>The skills the member can use now. The list is made again only when the TP of the member, a silence or a freeze on her, or the
        /// battle has changed what it depends on; callers only read it.</summary>
        public static List<(Skill skill, int level)> Options(Battle battle, Unit unit)
        {
            var cache = battle.OptionCache;
            int at = unit.Position;
            if (at >= cache.Length) { Array.Resize(ref battle.OptionCache, Math.Max(at + 1, cache.Length * 2)); cache = battle.OptionCache; }
            ref var entry = ref cache[at];
            bool silenced = unit.St[117] != null, frozen = unit.St[114] != null;
            if (entry.List != null && entry.Owner == unit && entry.Tp == unit.Tp && entry.Silenced == silenced && entry.Frozen == frozen) return entry.List;
            var list = ComputeOptions(battle, unit);
            entry = new Battle.OptionEntry { Owner = unit, Tp = unit.Tp, Silenced = silenced, Frozen = frozen, List = list };
            return list;
        }

        static List<(Skill skill, int level)> ComputeOptions(Battle battle, Unit unit)
        {
            var found = new List<(Skill, int)>();
            foreach (var (skillId, lv) in unit.Skills)
            {
                var skill = battle.Data.ById(skillId);
                if (skill == null || !UsableInBattle(skill) || !WeaponAllows(unit, skill)) continue;
                if (skill.IsMagic && (unit.St[117] != null || (battle.ZoneInfo != null && battle.ZoneInfo.NoMagic))) continue;
                if (skill.IsTechnique && unit.St[114] != null) continue;
                int level = Math.Max(1, Math.Min(lv, skill.Levels));
                if (skill.Tp[level - 1] > unit.Tp) continue;
                found.Add((skill, level));
            }
            return found;
        }

        static bool Gives(Skill skill, int effect) => skill.HasEffect(effect);

        static bool GivesAny(Skill skill, int[] effects)
        {
            foreach (int e in effects) if (skill.HasEffect(e)) return true;
            return false;
        }

        public static bool Puts(Skill skill, int effect)
        {
            foreach (var e in skill.Effects) if (e.Id == effect && e.Kind != 2) return true;
            return false;
        }

        // --- choosing ------------------------------------------------------------------------------------------
        public Action Choose(Battle battle, Unit unit)
        {
            string role = unit.HasRole ? unit.Role : "attacker";
            rules.TryGetValue(EVERY_ROLE, out var common);
            if (!rules.TryGetValue(role, out var own)) rules.TryGetValue("attacker", out own);
            if (common != null) foreach (var rule in common) { var chosen = TryRule(battle, unit, rule); if (chosen != null) return chosen; }
            if (own != null) foreach (var rule in own) { var chosen = TryRule(battle, unit, rule); if (chosen != null) return chosen; }
            var attack = new Action(unit, AKind.Attack);
            var target = BestSingleTarget(battle, unit, attack);
            if (target == null || battle.ExpectedDamage(attack, target) <= 0) return new Action(unit, AKind.Defend);
            if (Punished(unit, attack, target) && (Heals(battle, unit) || WeakBlow(battle, attack, target))) return new Action(unit, AKind.Defend);
            attack.Target = target;
            return attack;
        }

        Action TryRule(Battle battle, Unit unit, Rule rule)
        {
            if (!Check(rule.Condition, battle, unit, rule.CArg)) return null;
            switch (rule.Action)
            {
                case Act.Damage: return ActDamage(battle, unit);
                case Act.Heal: return ActHeal(battle, unit, rule.AArg);
                case Act.Revive: return ActRevive(battle, unit);
                case Act.Status: return ActStatus(battle, unit, rule.AArg);
                case Act.Dispel: return ActDispel(battle, unit);
                case Act.Doll: return ActDoll(battle, unit, rule.AArg);
                case Act.Tp: return ActTp(battle, unit, rule.AArg);
                case Act.Cure: return ActCure(battle, unit, rule.AArg);
                case Act.Ailment: return ActAilment(battle, unit, rule.AArg);
                case Act.Item: return ActItem(battle, unit, rule.AArg, null);
                case Act.Skill: return ActSkill(battle, unit, rule.AArg);
                default: return new Action(unit, AKind.Defend);
            }
        }

        static double Fraction(string arg, double dflt) => !string.IsNullOrEmpty(arg) ? double.Parse(arg.Trim(), System.Globalization.CultureInfo.InvariantCulture) : dflt;

        bool Check(Cond cond, Battle b, Unit u, string a)
        {
            switch (cond)
            {
                case Cond.Always: return true;
                case Cond.AllyHpBelow:
                    {
                        double f = Fraction(a, 0.5);
                        foreach (var m in b.AlliesArray(u)) if (m.Kind == Kind.Member && m.HpRatio < f) return true;
                        return false;
                    }
                case Cond.PartyHpBelow:
                    {
                        long hp = 0, max = 0;
                        foreach (var m in b.AlliesArray(u)) if (m.Kind == Kind.Member) { hp += m.Hp; max += m.MaxHp; }
                        return hp < Fraction(a, 0.6) * max;
                    }
                case Cond.AllyDown:
                    foreach (var m in b.SideArray(Unit.PARTY, false)) if (m.Kind == Kind.Member && !m.Alive) return true;
                    return false;
                case Cond.AllyTpBelow:
                    {
                        double f = Fraction(a, 0.3);
                        foreach (var m in b.AlliesArray(u)) if (m.Kind == Kind.Member && m != u && m.MaxTp != 0 && m.TpRatio < f) return true;
                        return false;
                    }
                case Cond.SelfTpBelow: return u.MaxTp != 0 && u.TpRatio < Fraction(a, 0.3);
                case Cond.SelfHpBelow: return u.HpRatio < Fraction(a, 0.5);
                case Cond.EnemyBuffed:
                    foreach (var t in EnemiesOf(b, u)) if (Battle.Dispellable(t)) return true;
                    return false;
                case Cond.AllyAiling: return AnyAiling(b, u, a);
                case Cond.TurnAtMost: return u.TurnsTaken <= PyMath.Int(Fraction(a, 1));
                case Cond.EnemiesAtLeast: return EnemiesOf(b, u).Length >= PyMath.Int(Fraction(a, 2));
                case Cond.Boss: return b.Fixed || b.Options.Boss;
                case Cond.NoDoll:
                    foreach (var x in b.Units) if (x.Owner == u && x.Alive && x.Kind == Kind.Doll) return false;
                    return true;
                case Cond.DollSlotFree:
                    {
                        int n = 0;
                        foreach (var x in b.Units) if (x.Owner == u && x.Alive && x.Kind == Kind.Doll && !x.Arrow) n++;
                        return n < (u.Has(313) ? 2 : 1);
                    }
            }
            return false;
        }

        // --- the cost of time and TP of an action ---------------------------------------------------------------
        public double TimeOf(Battle battle, Action action)
        {
            var unit = action.Actor;
            double t = ExpectedWait(battle, unit, action, false);
            double? cs = action.ChantSpeed;
            if (cs.HasValue && cs.Value != 0) t += ExpectedWait(battle, unit, action, true);
            return t;
        }

        public static double ExpectedWait(Battle battle, Unit unit, Action action, bool chanting)
        {
            bool saved = battle.MeanWait;
            battle.MeanWait = true;
            try { return battle.Wait(unit, action, chanting); }
            finally { battle.MeanWait = saved; }
        }

        List<int> HealCosts(Battle battle, Unit unit)
        {
            var costs = new List<int>();
            foreach (var (skillId, level) in unit.Skills)
            {
                var skill = battle.Data.ById(skillId);
                if (skill != null && UsableInBattle(skill) && GivesAny(skill, HEAL_EFFECTS))
                    costs.Add(skill.Tp[Math.Max(1, Math.Min(level, skill.Levels)) - 1]);
            }
            return costs;
        }

        bool Heals(Battle battle, Unit unit)
        {
            string role = unit.HasRole ? unit.Role : "attacker";
            bool anyHeal = false;
            if (rules.TryGetValue(role, out var list)) foreach (var r in list) if (r.ActionName == "heal") anyHeal = true;
            return !unit.Front && anyHeal && HealCosts(battle, unit).Count > 0;
        }

        bool WeakBlow(Battle battle, Action action, Unit target)
        {
            double floor = punishedBlowFloor;
            return floor != 0 && battle.ExpectedDamage(action, target) < floor * target.MaxHp;
        }

        double HealReserve(Battle battle, Unit unit)
        {
            double casts = healReserveCasts;
            if (casts == 0 || !Heals(battle, unit)) return 0.0;
            var costs = HealCosts(battle, unit);
            int min = costs[0];
            foreach (int c in costs) if (c < min) min = c;
            return casts * min;
        }

        public double TpPenalty(Unit unit, Action action)
        {
            if (unit.MaxTp == 0) return 1.0;
            return 1.0 + tpWeight * action.TpCost / unit.MaxTp;
        }

        static Unit[] EnemiesOf(Battle battle, Unit unit) => battle.TargetableArray(1 - unit.Side);

        // --- best target -------------------------------------------------------------------------------------------
        public static Unit BestSingleTarget(Battle battle, Unit unit, Action action)
        {
            var foes = EnemiesOf(battle, unit);
            if (foes.Length == 0) return null;
            Unit best = null;
            int ba = 0; double bb = 0, bc = 0;
            foreach (var t in foes)
            {
                double dmg = battle.ExpectedDamage(action, t);
                int a; double b, c;
                if (dmg <= 0) { a = 3; b = 999999.0; c = 0; }
                else
                {
                    bool kills = dmg >= t.Hp;
                    bool chanting = t.Chant != null;
                    bool asleep = t.St[116] != null;
                    bool done = false;
                    a = 0; b = 0; c = 0;
                    if (asleep && !kills && !action.Has(139))
                    {
                        bool otherAwake = false;
                        foreach (var f in foes) if (f != t && f.St[116] == null) { otherAwake = true; break; }
                        if (otherAwake) { a = 2; b = t.Hp / Math.Max(1.0, dmg); c = 0; done = true; }
                    }
                    if (!done)
                    {
                        double ratio = t.Hp / Math.Max(1.0, dmg);
                        if (kills)
                        {
                            double threat = (chanting ? 2.0 : 1.0) * (battle.Fixed && t.MaxHp > 3000 ? 1.5 : 1.0) * Math.Max(1.0, t.Stat(Unit.ATK));
                            a = 0; b = ratio; c = -threat;
                        }
                        else
                        {
                            if (chanting) ratio /= 2.5;
                            a = 1; b = ratio; c = -t.Stat(Unit.ATK);
                        }
                    }
                }
                if (best == null || a < ba || (a == ba && (b < bb || (b == bb && c < bc)))) { best = t; ba = a; bb = b; bc = c; }
            }
            return best;
        }

        static double RandomMoveValue(Battle battle, Action action)
        {
            int effect = 0;
            foreach (int e in Battle.RANDOM_MOVES) if (action.Has(e)) { effect = e; break; }
            RandomMove table = null;
            foreach (var t in battle.Data.RandomMoves) if (t.Effect == effect) { table = t; break; }
            if (table == null) return 0.0;
            bool joker = action.Actor.Has(315);
            double total = 0.0, weight = 0.0;
            foreach (var r in table.Results)
            {
                var skill = battle.Data.ById(r.Skill);
                double w = joker ? r.JokerWeight : r.Weight;
                weight += w;
                if (skill != null && r.Effects.Length > 0)
                    total += w * DamageValue(battle, new Action(action.Actor, AKind.Skill, skill, action.Level), out _);
            }
            return weight != 0 ? total / weight : 0.0;
        }

        static void AddMin(ref PySum sum, int hp, double dmg)
        {
            // min(t.hp, damage): the int when it is not above the float, else the float
            if (dmg < hp) sum.AddFloat(dmg); else sum.AddInt(hp);
        }

        static bool IsRandomMove(Action action)
        {
            if (action.Skill == null) return false;
            foreach (int e in Battle.RANDOM_MOVES) if (action.Has(e)) return true;
            return false;
        }

        /// <summary>Expected damage the action deals over its targets (each capped at the target's HP) and the target it is aimed at.</summary>
        public static double DamageValue(Battle battle, Action action, out Unit targetOut)
        {
            targetOut = null;
            if (IsRandomMove(action)) return RandomMoveValue(battle, action);
            int code = action.TargetCode;
            var foes = EnemiesOf(battle, action.Actor);
            if (foes.Length == 0) return 0.0;
            if (code == T.SINGLE || code == T.PIERCE)
            {
                var target = BestSingleTarget(battle, action.Actor, action);
                double dmg = battle.ExpectedDamage(action, target);
                double total = dmg < target.Hp ? dmg : target.Hp;
                if (code == T.PIERCE)
                {
                    // the units the blow goes on to, as Battle.Targets takes them: those the target keeps behind it
                    // (Battle.Behind, the program's list at 0x64 - 0x68) that can be targeted (2026-10-16; sim/policy.py
                    // took the first foe of the other row, and only from the front row)
                    foreach (var behind in battle.Behind(target))
                    {
                        if (Array.IndexOf(foes, behind) < 0) continue;
                        double d2 = battle.ExpectedDamage(action, behind);
                        total += d2 < behind.Hp ? d2 : behind.Hp;
                    }
                }
                targetOut = target;
                return total;
            }
            if (code == T.ROW)
            {
                var first = new List<Unit>(); var second = new List<Unit>();
                bool firstFront = foes[0].Front;
                foreach (var t in foes) { if (t.Front == firstFront) first.Add(t); else second.Add(t); }
                var best = first;
                double bestSum = RowSum(battle, action, first);
                if (second.Count > 0)
                {
                    double s2 = RowSum(battle, action, second);
                    if (s2 > bestSum) { best = second; bestSum = s2; }
                }
                targetOut = best[0];
                return RowSum(battle, action, best);
            }
            if (code == T.RANDOM)
            {
                double hits = battle.MeanHits(action);
                var single = new Action(action.Actor, action.Kind, action.Skill, action.Level);
                if (action.Atk != null) single = new Action(action.Actor, action.Kind, action.Atk, action.Level);
                var sum = new PySum();
                foreach (var t in foes) sum.AddFloat(battle.ExpectedDamage(single, t) / Math.Max(1.0, battle.MeanHits(single)));
                double mean = sum.Result / foes.Length;
                return hits * mean;
            }
            if (code == T.ALL || code == T.EVERYONE) return RowSum(battle, action, foes);
            return 0.0;
        }

        static double RowSum(Battle battle, Action action, Unit[] row)
        {
            var sum = new PySum();
            foreach (var t in row) AddMin(ref sum, t.Hp, battle.ExpectedDamage(action, t));
            return sum.Result;
        }

        static double RowSum(Battle battle, Action action, List<Unit> row)
        {
            var sum = new PySum();
            foreach (var t in row) AddMin(ref sum, t.Hp, battle.ExpectedDamage(action, t));
            return sum.Result;
        }

        // --- conditions and actions ------------------------------------------------------------------------------
        static bool Punished(Unit unit, Action action, Unit target)
        {
            if (target == null || !action.Physical) return false;
            return (target.Has(249) && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307)) ||
                   (target.Has(262) && action.Reach == T.SHORT && !unit.Has(304));
        }

        Action ActDamage(Battle battle, Unit unit)
        {
            // The candidates are the plain attack and each option that damages (or plays a random move), in this order. They are examined with
            // one object that is made over for each; the action chosen is made afresh at the end.
            var scratch = battle.ScratchAction;
            var options = Options(battle, unit);
            if (battle.CandidateSkills.Length < options.Count)
            {
                battle.CandidateSkills = new Skill[options.Count * 2];
                battle.CandidateLevels = new int[options.Count * 2];
            }
            var candidateSkills = battle.CandidateSkills;
            var candidateLevels = battle.CandidateLevels;
            int candidates = 0;
            foreach (var (skill, level) in options)
            {
                scratch.Reset(unit, AKind.Skill, skill, level);
                int code = scratch.TargetCode;
                bool hits = (code == T.SINGLE || code == T.RANDOM || code == T.ROW || code == T.PIERCE || code == T.ALL || code == T.EVERYONE) &&
                            (scratch.Physical || scratch.Magic || battle.Special(scratch));
                if (hits || IsRandomMoveAny(scratch)) { candidateSkills[candidates] = skill; candidateLevels[candidates] = level; candidates++; }
            }
            double reserve = HealReserve(battle, unit);
            scratch.Reset(unit, AKind.Attack, null, 1);
            double plainTotal = DamageValue(battle, scratch, out Unit plainTarget);
            bool plainKills = plainTarget != null && plainTotal >= plainTarget.Hp;
            Skill bestSkill = null; int bestLevel = 0; Unit bestTarget = null;
            bool haveBest = false, bestIsAttack = false;
            double bestScore = 0.0;
            for (int c = -1; c < candidates; c++)
            {
                if (c < 0) scratch.Reset(unit, AKind.Attack, null, 1);
                else scratch.Reset(unit, AKind.Skill, candidateSkills[c], candidateLevels[c]);
                var action = scratch;
                int tpCost = action.TpCost;
                if (tpCost > unit.Tp * (1.0 - tpReserve) && tpCost > 0) continue;
                if (tpCost > 0 && unit.Tp - tpCost < reserve) continue;
                double total = DamageValue(battle, action, out Unit target);
                if (total <= 0) continue;
                if (action.Kind == AKind.Attack && Punished(unit, action, target) && (Heals(battle, unit) || WeakBlow(battle, action, target))) continue;
                double waitTime = TimeOf(battle, action);
                double penalty = TpPenalty(unit, action);
                if (tpCost > 0 && plainKills && target == plainTarget) penalty *= 1.0 + 3.0 * ((double)tpCost / Math.Max(1, unit.MaxTp));
                if (tpCost > 0 && target != null && target.Hp > 0)
                {
                    double rawDmg = (action.TargetCode == T.SINGLE || action.TargetCode == T.PIERCE) ? battle.ExpectedDamage(action, target) : total;
                    if (rawDmg > total * 1.5)
                    {
                        double wasteRatio = rawDmg / Math.Max(1.0, total);
                        penalty *= 1.0 + Math.Min(2.0, (wasteRatio - 1.0) * 0.5);
                    }
                }
                double killMult = 1.0;
                if (target != null && total >= target.Hp) killMult = 1.35;
                else if (action.TargetCode == T.ALL || action.TargetCode == T.EVERYONE || action.TargetCode == T.ROW || action.TargetCode == T.RANDOM)
                {
                    int kills = 0;
                    foreach (var f in EnemiesOf(battle, unit)) if (battle.ExpectedDamage(action, f) >= f.Hp) kills++;
                    if (kills > 0) killMult = 1.0 + 0.25 * kills;
                }
                double chantMult = 1.0;
                if (target != null && target.Chant != null) chantMult = 1.25;
                double score = (total * killMult * chantMult) / waitTime / penalty;
                if (score > bestScore)
                {
                    haveBest = true; bestScore = score;
                    bestIsAttack = c < 0; bestSkill = c < 0 ? null : candidateSkills[c]; bestLevel = c < 0 ? 1 : candidateLevels[c];
                    bestTarget = target;
                }
            }
            if (!haveBest) return null;
            var best = bestIsAttack ? new Action(unit, AKind.Attack) : new Action(unit, AKind.Skill, bestSkill, bestLevel);
            best.Target = bestTarget;
            return best;
        }

        static bool ProvokedByUnit(Unit enemy, Unit unit)
        {
            foreach (var p in enemy.ProvokedBy) if (p.unit == unit) return true;
            return false;
        }

        static bool IsRandomMoveAny(Action action)
        {
            foreach (int e in Battle.RANDOM_MOVES) if (action.Has(e)) return true;
            return false;
        }

        static double ExpectedHeal(Battle battle, Action action, Unit target)
        {
            double value;
            if (action.TryVal(103, out value))
            {
                bool hasCap = action.TryVal(295, out double cap);
                double amount = F.Heal(action.Actor.Stat(Unit.RES), value, action.Actor.Passive(245, 0.0), hasCap, cap, action.Actor.Passive(317, 0.0), 0.50);
                double fixedV = action.Val(9, 0);
                return fixedV != 0 ? fixedV : amount;
            }
            if (action.Has(104)) return target.MaxHp;
            if (action.Has(128)) return PyMath.Int(target.MaxHp * action.Val(128, 0));
            if (action.Has(132))
            {
                bool hasCap = action.TryVal(295, out double cap);
                return F.FractionRecovery(target.MaxHp, action.Val(132, 0), hasCap, cap);
            }
            return 0;
        }

        Action ActHeal(Battle battle, Unit unit, string arg)
        {
            double threshold = Fraction(arg, 0.6);
            var hurt = new List<Unit>();
            foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member && m.HpRatio < threshold) hurt.Add(m);
            if (hurt.Count == 0) return null;
            Action best = null; double bestScore = 0.0;
            foreach (var (skill, level) in Options(battle, unit))
            {
                if (!GivesAny(skill, HEAL_EFFECTS)) continue;
                var action = new Action(unit, AKind.Skill, skill, level);
                Unit target; double restored;
                int code = action.TargetCode;
                if (code == T.ALLY)
                {
                    target = null;
                    foreach (var m in hurt) if (target == null || m.HpRatio < target.HpRatio) target = m;
                    restored = Math.Min(target.MaxHp - target.Hp, ExpectedHeal(battle, action, target));
                    if (target.HpRatio < 0.25) restored *= 1.3;
                }
                else if (code == T.ALLIES || code == T.ALLY_ROW || code == T.SELF)
                {
                    Unit[] group = code != T.SELF ? battle.AlliesArray(unit) : new[] { unit };
                    target = null;
                    var sum = new PySum();
                    foreach (var m in group)
                    {
                        if (m.Kind != Kind.Member) continue;
                        sum.AddFloat(Math.Min(m.MaxHp - m.Hp, ExpectedHeal(battle, action, m)) * (m.HpRatio < 0.25 ? 1.3 : 1.0));
                    }
                    restored = sum.Result;
                }
                else continue;
                double score = restored / TimeOf(battle, action) / TpPenalty(unit, action);
                if (score > bestScore)
                {
                    best = action; bestScore = score;
                    best.Target = target;
                }
            }
            if (best == null && unit.Items.Count > 0) return ActItem(battle, unit, "heal", null);
            return best;
        }

        Action ActRevive(Battle battle, Unit unit)
        {
            Unit dead = null;
            foreach (var m in battle.SideArray(Unit.PARTY, false)) if (!m.Alive && m.Kind == Kind.Member) { dead = m; break; }
            if (dead == null) return null;
            foreach (var (skill, level) in Options(battle, unit))
                if (Gives(skill, 105)) return new Action(unit, AKind.Skill, skill, level, dead);
            return ActItem(battle, unit, "revive", dead);
        }

        /// <summary>act_item(policy, battle, unit, arg, target): the policy is not read.</summary>
        public static Action ActItem(Battle battle, Unit unit, string arg, Unit target)
        {
            int[] kinds;
            switch (arg)
            {
                case "heal": kinds = new[] { 0, 3 }; break;
                case "tp": kinds = new[] { 1 }; break;
                case "revive": kinds = new[] { 8 }; break;
                case "cure": kinds = new[] { Battle.ITEM_CURE_ALL, Battle.ITEM_CURE_ONE }; break;
                default: kinds = Array.Empty<int>(); break;
            }
            int hurt = 0;
            foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member && m.Alive && m.HpRatio < 0.6) hurt++;
            bool found = false;
            bool bestParty = false; double bestSize = 0; int bestId = 0;
            foreach (var kv in unit.Items)
            {
                int itemId = kv.Key, count = kv.Value;
                battle.Data.Items.TryGetValue(itemId, out var item);
                if (count <= 0 || item == null) continue;
                bool any = false;
                for (int i = 0; i < item.Kinds.Length; i++) if (Array.IndexOf(kinds, item.Kinds[i]) >= 0) any = true;
                if (!any) continue;
                bool party = false;
                for (int i = 0; i < item.Kinds.Length; i++) if (item.Kinds[i] == 3) party = true;
                double size;
                if (arg != "cure")
                {
                    bool first = true; size = 0;
                    for (int i = 0; i < item.Kinds.Length; i++)
                        if (Array.IndexOf(kinds, item.Kinds[i]) >= 0)
                        {
                            double v = item.Values[i] != 0 ? item.Values[i] : 0;
                            if (first || v > size) { size = v; first = false; }
                        }
                }
                else
                {
                    size = 0;
                    for (int i = 0; i < item.Kinds.Length; i++) if (item.Kinds[i] == Battle.ITEM_CURE_ALL) size = 1;
                }
                bool flag = party == (hurt >= 2);
                // max() of the tuples (flag, size, item id)
                if (!found) { found = true; bestParty = flag; bestSize = size; bestId = itemId; }
                else
                {
                    int cmp = flag.CompareTo(bestParty);
                    if (cmp == 0) cmp = size.CompareTo(bestSize);
                    if (cmp == 0) cmp = itemId.CompareTo(bestId);
                    if (cmp > 0) { bestParty = flag; bestSize = size; bestId = itemId; }
                }
            }
            if (!found) return null;
            if (target == null)
            {
                Unit best = null;
                foreach (var m in battle.AlliesArray(unit))
                {
                    if (m.Kind != Kind.Member) continue;
                    double key = arg != "tp" ? m.HpRatio : m.TpRatio;
                    if (best == null || key < (arg != "tp" ? best.HpRatio : best.TpRatio)) best = m;
                }
                target = best;
            }
            return new Action(unit, AKind.Item, null, 1, target, bestId);
        }

        Action ActStatus(Battle battle, Unit unit, string arg)
        {
            int effect = int.Parse(arg);
            double reserve = HealReserve(battle, unit);
            foreach (var (skill, level) in Options(battle, unit))
            {
                if (!Puts(skill, effect)) continue;
                var action = new Action(unit, AKind.Skill, skill, level);
                if (action.TpCost > 0 && unit.Tp - action.TpCost < reserve) continue;
                bool dance = Battle.IsDance(effect);
                if ((Battle.IsSong(effect) || dance))
                {
                    var own = dance ? unit.Dance : unit.Song;
                    if (!own.Contains(skill.Name) && own.Count >= Battle.PerformanceSlots(unit, dance)) continue;
                }
                int code = action.TargetCode;
                if (code == T.SELF || code == T.NO_TARGET)
                {
                    if (unit.St[effect] != null) continue;
                    if (effect == 26)
                    {
                        if (unit.HpRatio < 0.35) continue;
                        var foes = EnemiesOf(battle, unit);
                        if (foes.Length == 1 && foes[0].Hp < Math.Max(100.0, unit.Stat(Unit.ATK) * 1.5)) continue;
                    }
                    return action;
                }
                if (code == T.ALLY)
                {
                    var lacking = new List<Unit>();
                    foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member && m.St[effect] == null) lacking.Add(m);
                    if (lacking.Count == 0) continue;
                    if (effect == 171)
                    {
                        Unit best = null; int b0 = 0, b1 = 0, b2 = 0;
                        foreach (var m in lacking)
                        {
                            int k0 = m.Chant != null ? 0 : 1, k1 = m.HpRatio < 0.4 ? 0 : 1, k2 = m.Stat(Unit.DEF);
                            if (best == null || k0 < b0 || (k0 == b0 && (k1 < b1 || (k1 == b1 && k2 < b2)))) { best = m; b0 = k0; b1 = k1; b2 = k2; }
                        }
                        action.Target = best;
                    }
                    else if (effect == 162 && unit.St[170] != null && lacking.Contains(unit))
                        // a defence buff of a unit that draws the blows (Provoke up) goes on herself: she is the one hit
                        action.Target = unit;
                    else
                    {
                        Unit best = null; int bk = 0;
                        foreach (var m in lacking)
                        {
                            // 168 (a speed buff such as Accelerator): the ally who hits hardest, by her higher of ATK and INT
                            int k = effect == 161 ? m.Stat(Unit.ATK) : effect == 162 ? -m.Stat(Unit.DEF) : (effect == 27 || effect == 173) ? m.Stat(Unit.INT)
                                  : effect == 168 ? Math.Max(m.Stat(Unit.ATK), m.Stat(Unit.INT)) : 0;
                            if (best == null || k > bk) { best = m; bk = k; }
                        }
                        action.Target = best;
                    }
                    return action;
                }
                // EVERYONE (Limit Field): a status on every unit of the field, kept up as a party buff is
                if (code == T.ALLIES || code == T.ALLY_ROW || code == T.EVERYONE)
                {
                    int members = 0, lackingN = 0;
                    foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member) { members++; if (m.St[effect] == null) lackingN++; }
                    double share = partyBuffRecastShare;
                    if (lackingN == 0 || lackingN < share * members) continue;
                    return action;
                }
                if (code == T.SINGLE || code == T.ALL || code == T.ROW)
                {
                    var foes = new List<Unit>();
                    foreach (var t in EnemiesOf(battle, unit))
                    {
                        bool lacks = t.St[effect] == null || (effect == 170 && !ProvokedByUnit(t, unit));
                        if (lacks && !battle.VisiblyVoided(action, t)) foes.Add(t);
                    }
                    if (foes.Count == 0) continue;
                    Unit best = null; int b0 = 0, b1 = 0, b2 = 0;
                    foreach (var t in foes)
                    {
                        int k0 = t.Chant != null ? 1 : 0, k1 = (battle.Fixed && t.MaxHp > 3000) ? 1 : 0, k2 = t.Stat(Unit.ATK);
                        if (best == null || k0 > b0 || (k0 == b0 && (k1 > b1 || (k1 == b1 && k2 > b2)))) { best = t; b0 = k0; b1 = k1; b2 = k2; }
                    }
                    action.Target = best;
                    return action;
                }
            }
            return null;
        }

        static readonly System.Collections.Concurrent.ConcurrentDictionary<string, int[]> ailmentLists = new System.Collections.Concurrent.ConcurrentDictionary<string, int[]>();

        /// <summary>The ailments an argument names ('120;116'), all of them when it names none; the array must not be changed.</summary>
        static int[] AilmentsOf(string arg)
        {
            string key = arg ?? "";
            if (ailmentLists.TryGetValue(key, out var found)) return found;
            var r = new List<int>();
            if (!string.IsNullOrEmpty(arg))
            {
                foreach (var x in arg.Split(';')) if (x.Trim().Length > 0) r.Add(int.Parse(x.Trim()));
            }
            else r.AddRange(Battle.AILMENT_IDS);
            return ailmentLists.GetOrAdd(key, r.ToArray());
        }

        /// <summary>Whether a member of the party carries one of the ailments named (the test of the condition ally_ailing).</summary>
        static bool AnyAiling(Battle battle, Unit unit, string arg)
        {
            var wanted = AilmentsOf(arg);
            foreach (var m in battle.AlliesArray(unit))
            {
                if (m.Kind != Kind.Member) continue;
                foreach (int e in wanted) if (m.St[e] != null) return true;
            }
            return false;
        }

        static List<Unit> AilingMembers(Battle battle, Unit unit, string arg)
        {
            var wanted = AilmentsOf(arg);
            var r = new List<Unit>();
            foreach (var m in battle.AlliesArray(unit))
            {
                if (m.Kind != Kind.Member) continue;
                foreach (int e in wanted) if (m.St[e] != null) { r.Add(m); break; }
            }
            return r;
        }

        Action ActAilment(Battle battle, Unit unit, string arg)
        {
            double floor = ailmentMinChance * 100;
            Action best = null;
            bool haveKey = false; int bestMax = 0; double bestChance = 0;
            foreach (int effect in AilmentsOf(arg))
            {
                string name = Battle.AilmentNameOf(effect);
                foreach (var (skill, level) in Options(battle, unit))
                {
                    var action = battle.ScratchAction;
                    action.Reset(unit, AKind.Skill, skill, level);
                    bool has = false; double value = 0;
                    int n = action.Count;
                    for (int i = 0; i < n; i++) if (action.EffId(i) == effect && action.EffKind(i) != 2) { has = true; value = action.EffVal(i); break; }
                    int code = action.TargetCode;
                    if (!has || !(code == T.SINGLE || code == T.RANDOM || code == T.ROW || code == T.PIERCE || code == T.ALL)) continue;
                    foreach (var target in EnemiesOf(battle, unit))
                    {
                        if (target.Immune(name) || target.St[effect] != null || Battle.Nullified(target, effect)) continue;
                        double chance;
                        if (effect == 123) chance = unit.Level > target.Level ? value * 100 : 0.0;
                        else
                        {
                            int index = Battle.AilmentResistOf(effect);
                            chance = F.AilmentChance(value, index != T.NONE ? target.Resistance(index) : 0);
                        }
                        int maxHp = target.MaxHp;
                        bool greater = !haveKey || maxHp > bestMax || (maxHp == bestMax && chance > bestChance);
                        if (chance >= floor && greater)
                        {
                            best = new Action(unit, AKind.Skill, skill, level);
                            haveKey = true; bestMax = maxHp; bestChance = chance;
                            best.Target = target;
                        }
                    }
                }
                if (best != null) return best;
            }
            return null;
        }

        Action ActDispel(Battle battle, Unit unit)
        {
            var buffed = new List<Unit>();
            foreach (var t in EnemiesOf(battle, unit)) if (Battle.Dispellable(t)) buffed.Add(t);
            if (buffed.Count == 0) return null;
            foreach (var (skill, level) in Options(battle, unit))
            {
                if (!Gives(skill, 74)) continue;
                var action = new Action(unit, AKind.Skill, skill, level);
                Unit best = null; int b0 = 0, b1 = 0, b2 = 0, b3 = 0;
                foreach (var t in buffed)
                {
                    if (battle.VisiblyVoided(action, t)) continue;
                    int k0 = (t.Has(192) || t.Has(182)) ? 1 : 0;
                    int k1 = (t.St[161] != null || t.St[26] != null) ? 1 : 0;
                    int k2 = (battle.Fixed && t.MaxHp > 3000) ? 1 : 0;
                    int k3 = t.Stat(Unit.ATK);
                    bool greater = best == null || k0 > b0 || (k0 == b0 && (k1 > b1 || (k1 == b1 && (k2 > b2 || (k2 == b2 && k3 > b3)))));
                    if (greater) { best = t; b0 = k0; b1 = k1; b2 = k2; b3 = k3; }
                }
                if (best != null)
                {
                    action.Target = best;
                    return action;
                }
            }
            return null;
        }

        Action ActDoll(Battle battle, Unit unit, string arg)
        {
            var dolls = new List<(Skill, int)>();
            foreach (var (s, lv) in Options(battle, unit)) if (GivesAny(s, DOLL_EFFECTS)) dolls.Add((s, lv));
            if (dolls.Count == 0) return null;
            if (!string.IsNullOrEmpty(arg))
            {
                foreach (var name in arg.Split('|'))
                {
                    foreach (var (s, lv) in dolls)
                        if (s.Name == name.Trim()) return new Action(unit, AKind.Skill, s, lv);
                }
                return null;
            }
            var bestD = dolls[0];
            foreach (var d in dolls) if (d.Item2 > bestD.Item2) bestD = d;
            return new Action(unit, AKind.Skill, bestD.Item1, bestD.Item2);
        }

        static readonly string[] HeavyRoles = { "attacker", "mage", "healer", "valkyrie", "dark lord", "magical princess", "sage" };

        Action ActTp(Battle battle, Unit unit, string arg)
        {
            double f = Fraction(arg, 0.5);
            Unit target = null; int bp = 0; double bt = 0;
            foreach (var m in battle.AlliesArray(unit))
            {
                if (m.Kind != Kind.Member || m.MaxTp == 0 || !(m.TpRatio < f)) continue;
                int prio = Array.IndexOf(HeavyRoles, m.HasRole ? m.Role : "") >= 0 ? 0 : 1;
                double ratio = m.TpRatio;
                if (target == null || prio < bp || (prio == bp && ratio < bt)) { target = m; bp = prio; bt = ratio; }
            }
            if (target == null) return null;
            foreach (var (skill, level) in Options(battle, unit))
                if (Gives(skill, 129) || Gives(skill, 426)) return new Action(unit, AKind.Skill, skill, level, target);
            // 130 (Self-Sacrifice): the giver passes all her TP, so only from a fuller giver to an emptier ally
            foreach (var (skill, level) in Options(battle, unit))
                if (Gives(skill, 130) && target != unit && unit.Tp > 0 && unit.TpRatio > target.TpRatio) return new Action(unit, AKind.Skill, skill, level, target);
            return ActItem(battle, unit, "tp", target);
        }

        Action ActCure(Battle battle, Unit unit, string arg)
        {
            var wanted = AilmentsOf(arg);
            var ailing = AilingMembers(battle, unit, arg);
            if (ailing.Count == 0) return null;
            Unit target = null; int bk = 0;
            foreach (var m in ailing)
            {
                int k = 0;
                foreach (int e in wanted) if (m.St[e] != null) k++;
                if (target == null || k > bk) { target = m; bk = k; }
            }
            var carried = new List<int>();
            foreach (int e in wanted) if (target.St[e] != null) carried.Add(e);
            foreach (var (skill, level) in Options(battle, unit))
            {
                if (!Gives(skill, 106)) continue;
                var action = new Action(unit, AKind.Skill, skill, level);
                double v = action.Val(106, 0); int n = v != 0 ? PyMath.Int(v) : 0;
                bool any = false;
                for (int i = 0; i < Math.Min(Math.Max(n, 0), Battle.CURE_ORDER.Length); i++)
                    foreach (int e in carried) if (e == Battle.CURE_ORDER[i]) any = true;
                if (any)
                {
                    action.Target = action.TargetCode == T.ALLY ? target : null;
                    return action;
                }
            }
            if (unit.Items.Count > 0) return ActItem(battle, unit, "cure", target);
            return null;
        }

        Action ActSkill(Battle battle, Unit unit, string arg)
        {
            foreach (var (skill, level) in Options(battle, unit))
            {
                if (skill.Name == arg)
                {
                    var action = new Action(unit, AKind.Skill, skill, level);
                    if (action.TargetCode == T.SINGLE || action.TargetCode == T.PIERCE) action.Target = BestSingleTarget(battle, unit, action);
                    return action;
                }
            }
            return null;
        }
    }
}
