using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine
{
    /// <summary>What a party member does on its turn, by the rules of its role.</summary>
    public sealed class Policy
    {
        static readonly int[] HEAL_EFFECTS = { 103, 104, 128, 132 };
        static readonly int[] DOLL_EFFECTS = { 228, 229, 230, 231, 232, 233 };
        static readonly int[] ITEM_HEAL_KINDS = { 0, 2, 3, 5 };
        static readonly int[] ITEM_TP_KINDS = { 1, 2, 4, 5 };
        static readonly int[] ITEM_REVIVE_KINDS = { 8 };
        static readonly int[] ITEM_CURE_KINDS = { Battle.ITEM_CURE_ALL, Battle.ITEM_CURE_ONE };
        static readonly int[] RANDOM_HARM_EFFECTS = { 0, 1, 8, 113, 114, 115, 116, 117, 118, 119, 120, 122, 123, 140, 143, 435 };
        static readonly int[] RANDOM_HEAL_EFFECTS = { 9, 103, 104, 128, 132 };
        static readonly int[] RANDOM_BAD_EFFECTS = { 425, 143 };
        static readonly int[] RANDOM_GOOD_EFFECTS = { 427 };
        const string EVERY_ROLE = "*";

        enum Cond { Always, AllyHpBelow, PartyHpBelow, AllyDown, AllyTpBelow, SelfTpBelow, SelfHpBelow, EnemyBuffed, AllyAiling, TurnAtMost, EnemiesAtLeast, Boss, NoDoll, DollSlotFree, FoesAttack, FoesCast, EnemyNamed, NoFoeDispels }
        enum Act { Damage, Heal, Revive, Status, Dispel, Doll, Tp, Cure, Ailment, Item, Skill, Defend }

        sealed class Rule
        {
            public Cond Condition;
            public string CArg;
            public Act Action;
            public string AArg;
            public string ActionName;
            // Pre-parsed arguments (avoid repeated string parsing/splitting in hot loops)
            public double CNum;
            public int CInt;
            public int CAttr;
            public string[] CNames;
            public int[] CAilments;
            public int AEffect;
            public double ANum;
            public int[] AAilments;
            public double AilmentFloor;
            public bool HasOwnFloor;
            public string[] DollNames;
        }

        readonly Dictionary<string, List<Rule>> rules = new Dictionary<string, List<Rule>>();
        readonly HashSet<string> rolesWithHeal = new HashSet<string>(StringComparer.Ordinal);
        readonly double tpWeight, tpReserve, punishedBlowFloor, healReserveCasts, partyBuffRecastShare, ailmentMinChance;
        readonly double[] ailmentFloorByEffect = new double[GameData.MaxEffect];

        readonly Setup policySetup;              // for the settings read per effect (ailment_min_chance_<effect>)

        public Policy(List<Row> policyRows, Setup setup)
        {
            policySetup = setup;
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
            Array.Fill(ailmentFloorByEffect, double.NaN);
            foreach (int e in Battle.AILMENT_IDS)
            {
                object own = setup.Setting("ailment_min_chance_" + e);
                if (own != null) ailmentFloorByEffect[e] = Setup.ToDouble(own) * 100.0;
            }
            var sorted = policyRows.OrderBy(r => r.Str("Role"), StringComparer.Ordinal).ThenBy(r => r.Dbl("Order")).ToList();
            foreach (var r in sorted)
            {
                string c = r.Str("Condition"), a = r.Str("Action");
                string cond = c, cArg = null, act = a, aArg = null;
                int p = c.IndexOf(':');
                if (p >= 0) { cond = c.Substring(0, p); cArg = c.Substring(p + 1); }
                p = a.IndexOf(':');
                if (p >= 0) { act = a.Substring(0, p); aArg = a.Substring(p + 1); }
                var parsedCond = ParseCond(cond, r);
                var parsedAct = ParseAct(act, r);
                string ca = cArg == "" ? null : cArg;
                string aa = aArg == "" ? null : aArg;
                var rule = new Rule { Condition = parsedCond, CArg = ca, Action = parsedAct, AArg = aa, ActionName = act };
                switch (parsedCond)
                {
                    case Cond.AllyHpBelow: rule.CNum = Fraction(ca, 0.5); break;
                    case Cond.PartyHpBelow: rule.CNum = Fraction(ca, 0.6); break;
                    case Cond.AllyTpBelow: rule.CNum = Fraction(ca, 0.3); break;
                    case Cond.SelfTpBelow: rule.CNum = Fraction(ca, 0.3); break;
                    case Cond.SelfHpBelow: rule.CNum = Fraction(ca, 0.5); break;
                    case Cond.TurnAtMost: rule.CInt = PyMath.Int(Fraction(ca, 1)); break;
                    case Cond.EnemiesAtLeast: rule.CInt = PyMath.Int(Fraction(ca, 2)); break;
                    case Cond.FoesCast: rule.CNum = Fraction(ca, 0.3); break;
                    case Cond.FoesAttack:
                        {
                            var parts = (ca ?? "").Split(':');
                            rule.CAttr = int.Parse(parts[0].Trim());
                            rule.CNum = parts.Length > 1 ? Fraction(parts[1], 0.3) : 0.3;
                            break;
                        }
                    case Cond.EnemyNamed:
                        {
                            var raw = (ca ?? "").Split('|');
                            rule.CNames = new string[raw.Length];
                            for (int i = 0; i < raw.Length; i++) rule.CNames[i] = raw[i].Trim();
                            break;
                        }
                    case Cond.AllyAiling: rule.CAilments = AilmentsOf(ca); break;
                }
                switch (parsedAct)
                {
                    case Act.Heal: rule.ANum = Fraction(aa, 0.6); break;
                    case Act.Status: rule.AEffect = int.Parse(aa); break;
                    case Act.Tp: rule.ANum = Fraction(aa, 0.5); break;
                    case Act.Cure: rule.AAilments = AilmentsOf(aa); break;
                    case Act.Ailment:
                        {
                            double floor = ailmentMinChance * 100.0;
                            bool ownFloor = false;
                            string ailArg = aa;
                            int at = (ailArg ?? "").IndexOf('@');
                            if (at >= 0)
                            {
                                floor = double.Parse(ailArg.Substring(at + 1), System.Globalization.CultureInfo.InvariantCulture) * 100.0;
                                ailArg = ailArg.Substring(0, at);
                                ownFloor = true;
                            }
                            rule.AilmentFloor = floor;
                            rule.HasOwnFloor = ownFloor;
                            rule.AAilments = AilmentsOf(ailArg);
                            foreach (int e in rule.AAilments)
                                if (e >= 0 && e < ailmentFloorByEffect.Length && double.IsNaN(ailmentFloorByEffect[e]))
                                {
                                    object own = setup.Setting("ailment_min_chance_" + e);
                                    if (own != null) ailmentFloorByEffect[e] = Setup.ToDouble(own) * 100.0;
                                }
                            break;
                        }
                    case Act.Doll:
                        if (!string.IsNullOrEmpty(aa))
                        {
                            var raw = aa.Split('|');
                            rule.DollNames = new string[raw.Length];
                            for (int i = 0; i < raw.Length; i++) rule.DollNames[i] = raw[i].Trim();
                        }
                        break;
                }
                string role = r.Str("Role");
                if (parsedAct == Act.Heal) rolesWithHeal.Add(role);
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
                case "foes_attack": return Cond.FoesAttack;
                case "foes_cast": return Cond.FoesCast;
                case "enemy_named": return Cond.EnemyNamed;
                case "no_foe_dispels": return Cond.NoFoeDispels;
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

        /// <summary>Weapon/shield/armor requirement check matching CGamePlayerStatus::vtable+0x12c (0x4f4910):
        /// -1 any, 0 short-range weapon, 1..14 weapon type (code - 1), 15 special weapon types 14..20,
        /// 16 shield in off-hand, 17 head armor equipped, 18 body armor equipped, 19 any weapon equipped in slot 0.</summary>
        public static bool WeaponAllows(Piece weapon, bool shield, Skill skill, bool hasHead = false, bool hasBody = false)
        {
            if (skill.Weapons.Length == 0) return true;
            foreach (int code in skill.Weapons)
            {
                if (code == -1) return true;
                if (code == 0 && weapon != null && weapon.Range == 0) return true;
                if (code == 15 && weapon != null && weapon.Type >= 14 && weapon.Type <= 20) return true;
                if (code == 16 && shield) return true;
                if (code == 17 && hasHead) return true;
                if (code == 18 && hasBody) return true;
                if (code == 19 && weapon != null) return true;
                if (code >= 1 && code <= 14 && weapon != null && weapon.Type + 1 == code) return true;
            }
            return false;
        }

        public static bool WeaponAllows(Unit unit, Skill skill) => WeaponAllows(unit.Weapon, unit.Shield, skill, unit.HasHead, unit.HasBody);

        /// <summary>The skills the member can use now. The list is made again only when the TP of the member, a silence, freeze, or
        /// shadow sew on her, or the battle has changed what it depends on; callers only read it.</summary>
        public static List<(Skill skill, int level)> Options(Battle battle, Unit unit)
        {
            var cache = battle.OptionCache;
            int at = unit.Position;
            if (at >= cache.Length) { Array.Resize(ref battle.OptionCache, Math.Max(at + 1, cache.Length * 2)); cache = battle.OptionCache; }
            ref var entry = ref cache[at];
            bool silenced = unit.St[117] != null, frozen = unit.St[114] != null, shadowSewed = unit.St[123] != null;
            if (entry.List != null && entry.Owner == unit && entry.Tp == unit.Tp && entry.Silenced == silenced && entry.Frozen == frozen && entry.ShadowSewed == shadowSewed) return entry.List;
            var list = entry.List ?? new List<(Skill, int)>(16);
            ComputeOptions(battle, unit, silenced, frozen, shadowSewed, list);
            entry = new Battle.OptionEntry { Owner = unit, Tp = unit.Tp, Silenced = silenced, Frozen = frozen, ShadowSewed = shadowSewed, List = list };
            return list;
        }

        static (Skill skill, int level)[] GetUsableSkills(GameData data, Unit unit)
        {
            var cached = unit.UsableSkills;
            if (cached != null) return cached;
            var skills = unit.Skills;
            var buf = new List<(Skill, int)>(skills.Count);
            for (int i = 0; i < skills.Count; i++)
            {
                var (skillId, lv) = skills[i];
                var skill = data.ById(skillId);
                if (skill == null || !UsableInBattle(skill) || !WeaponAllows(unit, skill)) continue;
                buf.Add((skill, Math.Max(1, Math.Min(lv, skill.Levels))));
            }
            var arr = buf.ToArray();
            unit.UsableSkills = arr;
            return arr;
        }

        static void ComputeOptions(Battle battle, Unit unit, bool silenced, bool frozen, bool shadowSewed, List<(Skill skill, int level)> found)
        {
            found.Clear();
            // 0x455d94: Shadow Sew (123) blocks both Technique and Magic skills.
            if (shadowSewed) return;
            bool noMagic = silenced || (battle.ZoneInfo != null && battle.ZoneInfo.NoMagic);
            int tp = unit.Tp;
            var usable = GetUsableSkills(battle.Data, unit);
            for (int i = 0; i < usable.Length; i++)
            {
                var (skill, level) = usable[i];
                if (skill.IsMagic && noMagic) continue;
                if (skill.IsTechnique && frozen) continue;
                if (Battle.EffectiveTpCost(unit, skill, level) > tp) continue;
                found.Add((skill, level));
            }
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
            if (common != null)
                for (int i = 0; i < common.Count; i++) { var chosen = TryRule(battle, unit, common[i]); if (chosen != null) return chosen; }
            if (own != null)
                for (int i = 0; i < own.Count; i++) { var chosen = TryRule(battle, unit, own[i]); if (chosen != null) return chosen; }
            var attack = battle.ScratchAction;
            attack.Reset(unit, AKind.Attack, null, 1);
            var target = BestSingleTarget(battle, unit, attack);
            if (target == null || battle.ExpectedDamage(attack, target) <= 0) return new Action(unit, AKind.Defend);
            if (Punished(unit, attack, target) && (Heals(battle, unit) || WeakBlow(battle, attack, target))) return new Action(unit, AKind.Defend);
            return new Action(unit, AKind.Attack, null, 1, target);
        }

        Action TryRule(Battle battle, Unit unit, Rule rule)
        {
            if (!Check(rule, battle, unit)) return null;
            switch (rule.Action)
            {
                case Act.Damage: return ActDamage(battle, unit);
                case Act.Heal: return ActHeal(battle, unit, rule.ANum);
                case Act.Revive: return ActRevive(battle, unit);
                case Act.Status: return ActStatus(battle, unit, rule.AEffect);
                case Act.Dispel: return ActDispel(battle, unit);
                case Act.Doll: return ActDoll(battle, unit, rule.DollNames);
                case Act.Tp: return ActTp(battle, unit, rule.ANum);
                case Act.Cure: return ActCure(battle, unit, rule.AAilments);
                case Act.Ailment: return ActAilment(battle, unit, rule);
                case Act.Item: return ActItem(battle, unit, rule.AArg, null);
                case Act.Skill: return ActSkill(battle, unit, rule.AArg);
                default: return new Action(unit, AKind.Defend);
            }
        }

        /// <summary>foes_cast[:SHARE]: the attacks the living foes can use are spells (magic damage, met by the RES of the party) in SHARE or more
        /// of them (default 0.3): a song of magic defence is sung where the foes cast.</summary>
        static bool FoesCast(Battle b, Unit u, double share)
        {
            int all = 0, mine = 0;
            foreach (var t in EnemiesOf(b, u))
                foreach (int id in t.Attacks)
                {
                    var k = b.Data.GetAttack(id);
                    if (k != null && !k.Passive) { all++; if (k.Spell) mine++; }
                }
            return all > 0 && mine >= share * all;
        }

        /// <summary>foes_attack:ATTR[:SHARE]: the attacks the living foes can use are of attribute ATTR (1 slash, 2 stab, 3 bash, 4 - 8 the
        /// elements) in SHARE or more of them (default 0.3): a guard against one kind of blow is cast where the foes strike with it.</summary>
        static bool FoesAttack(Battle b, Unit u, int attr, double share)
        {
            int all = 0, mine = 0;
            foreach (var t in EnemiesOf(b, u))
                foreach (int id in t.Attacks)
                {
                    var k = b.Data.GetAttack(id);
                    if (k != null && !k.Passive) { all++; if (k.Attr == attr) mine++; }
                }
            return all > 0 && mine >= share * all;
        }

        /// <summary>no_foe_dispels: no living foe has an attack that strips buffs (effect 74): a buff the foes would strip at every blow is
        /// not kept up against them, as a player stops casting it again.</summary>
        static bool NoFoeDispels(Battle b, Unit u)
        {
            foreach (var t in EnemiesOf(b, u))
                foreach (int id in t.Attacks)
                {
                    var k = b.Data.GetAttack(id);
                    if (k != null && !k.Passive && k.EffId != null && Array.IndexOf(k.EffId, 74) >= 0) return false;
                }
            return true;
        }

        static double Fraction(string arg, double dflt) => !string.IsNullOrEmpty(arg) ? double.Parse(arg.Trim(), System.Globalization.CultureInfo.InvariantCulture) : dflt;

        bool Check(Rule rule, Battle b, Unit u)
        {
            switch (rule.Condition)
            {
                case Cond.Always: return true;
                case Cond.AllyHpBelow:
                    {
                        double f = rule.CNum;
                        foreach (var m in b.AlliesArray(u)) if (m.Kind == Kind.Member && m.HpRatio < f) return true;
                        return false;
                    }
                case Cond.PartyHpBelow:
                    {
                        long hp = 0, max = 0;
                        foreach (var m in b.AlliesArray(u)) if (m.Kind == Kind.Member) { hp += m.Hp; max += m.MaxHp; }
                        return hp < rule.CNum * max;
                    }
                case Cond.AllyDown:
                    foreach (var m in b.SideArray(Unit.PARTY, false)) if (m.Kind == Kind.Member && !m.Alive) return true;
                    return false;
                case Cond.AllyTpBelow:
                    {
                        double f = rule.CNum;
                        foreach (var m in b.AlliesArray(u)) if (m.Kind == Kind.Member && m != u && m.MaxTp != 0 && m.TpRatio < f) return true;
                        return false;
                    }
                case Cond.SelfTpBelow: return u.MaxTp != 0 && u.TpRatio < rule.CNum;
                case Cond.SelfHpBelow: return u.HpRatio < rule.CNum;
                case Cond.EnemyBuffed:
                    foreach (var t in EnemiesOf(b, u)) if (Battle.Dispellable(t)) return true;
                    return false;
                case Cond.AllyAiling: return AnyAiling(b, u, rule.CAilments);
                case Cond.TurnAtMost: return u.TurnsTaken <= rule.CInt;
                case Cond.EnemiesAtLeast: return EnemiesOf(b, u).Length >= rule.CInt;
                case Cond.Boss: return b.Fixed || b.Options.Boss;
                case Cond.FoesAttack: return FoesAttack(b, u, rule.CAttr, rule.CNum);
                case Cond.FoesCast: return FoesCast(b, u, rule.CNum);
                case Cond.NoFoeDispels: return NoFoeDispels(b, u);
                case Cond.EnemyNamed:
                    // a strategy of a guide for one boss: the rule holds while an enemy of that name stands (names split by |)
                    foreach (var t in EnemiesOf(b, u))
                        for (int i = 0; i < rule.CNames.Length; i++) if (t.Name == rule.CNames[i]) return true;
                    return false;
                case Cond.NoDoll:
                    foreach (var x in b.Units) if (x.Owner == u && x.Alive && x.Kind == Kind.Doll) return false;
                    return true;
                case Cond.DollSlotFree:
                    {
                        int n = 0;
                        foreach (var x in b.Units) if (Battle.IsPuppet(x) && x.Owner == u) n++;
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

        static int MinHealCost(Battle battle, Unit unit)
        {
            int min = int.MaxValue;
            var skills = unit.Skills;
            for (int i = 0; i < skills.Count; i++)
            {
                var (skillId, level) = skills[i];
                var skill = battle.Data.ById(skillId);
                if (skill != null && UsableInBattle(skill) && GivesAny(skill, HEAL_EFFECTS))
                {
                    int cost = Battle.EffectiveTpCost(unit, skill, Math.Max(1, Math.Min(level, skill.Levels)));
                    if (cost < min) min = cost;
                }
            }
            return min == int.MaxValue ? -1 : min;
        }

        bool Heals(Battle battle, Unit unit)
        {
            if (unit.Front) return false;
            string role = unit.HasRole ? unit.Role : "attacker";
            return rolesWithHeal.Contains(role) && MinHealCost(battle, unit) >= 0;
        }

        bool WeakBlow(Battle battle, Action action, Unit target)
        {
            double floor = punishedBlowFloor;
            return floor != 0 && battle.ExpectedDamage(action, target) < floor * target.MaxHp;
        }

        double HealReserve(Battle battle, Unit unit)
        {
            double casts = healReserveCasts;
            if (casts == 0 || unit.Front) return 0.0;
            string role = unit.HasRole ? unit.Role : "attacker";
            if (!rolesWithHeal.Contains(role)) return 0.0;
            int min = MinHealCost(battle, unit);
            return min >= 0 ? casts * min : 0.0;
        }

        public double TpPenalty(Unit unit, Action action)
        {
            if (unit.MaxTp == 0) return 1.0;
            return 1.0 + tpWeight * Battle.EffectiveTpCost(action) / unit.MaxTp;
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

        static bool HasAnyEffect(int[] effects, int[] ids)
        {
            for (int i = 0; i < effects.Length; i++)
            {
                int e = effects[i];
                for (int j = 0; j < ids.Length; j++)
                    if (e == ids[j]) return true;
            }
            return false;
        }

        static double RandomMoveValue(Battle battle, Action action)
        {
            int effect = 0;
            foreach (int e in Battle.RANDOM_MOVES) if (action.Has(e)) { effect = e; break; }
            RandomMove table = null;
            foreach (var t in battle.Data.RandomMoves) if (t.Effect == effect) { table = t; break; }
            if (table == null) return 0.0;
            bool joker = action.Actor.Has(315);
            double unitScale = Math.Max(25.0, action.Actor.Stat(Unit.ATK) * 0.8);
            double total = 0.0, weight = 0.0;
            foreach (var r in table.Results)
            {
                var skill = battle.Data.ById(r.Skill);
                double w = joker ? r.JokerWeight : r.Weight;
                weight += w;
                if (skill == null || r.Effects.Length == 0) continue;
                var sub = new Action(action.Actor, AKind.Skill, skill, action.Level);
                int tc = sub.TargetCode;
                bool targetsFoes = tc == T.SINGLE || tc == T.RANDOM || tc == T.ROW || tc == T.PIERCE || tc == T.ALL;
                bool targetsAllies = T.OwnSide(tc);
                bool harms = HasAnyEffect(r.Effects, RANDOM_HARM_EFFECTS);
                bool heals = HasAnyEffect(r.Effects, RANDOM_HEAL_EFFECTS);
                if (targetsFoes)
                {
                    if (heals)
                    {
                        var foes = EnemiesOf(battle, action.Actor);
                        double avgHeal = unitScale;
                        if (foes.Length > 0)
                        {
                            double h = ExpectedHeal(battle, sub, foes[0]);
                            if (h > 0) avgHeal = Math.Min(foes[0].MaxHp - foes[0].Hp, h);
                        }
                        total -= w * avgHeal;
                    }
                    else
                    {
                        double dmg = DamageValue(battle, sub, out _);
                        if (dmg > 0) total += w * dmg;
                        else total += w * unitScale * 0.5;
                    }
                }
                else if (targetsAllies)
                {
                    if (harms) total -= w * unitScale * 1.5;
                    else total += w * unitScale * 0.5;
                }
                else
                {
                    if (heals || HasAnyEffect(r.Effects, RANDOM_BAD_EFFECTS)) total -= w * unitScale * 0.5;
                    else if (HasAnyEffect(r.Effects, RANDOM_GOOD_EFFECTS)) total += w * unitScale;
                }
            }
            return weight != 0 ? total / weight : 0.0;
        }

        static void AddMin(ref PySum sum, int hp, double dmg)
        {
            // min(t.hp, damage): the int when it is not above the float, else the float
            if (dmg < hp) sum.AddFloat(dmg); else sum.AddInt(hp);
        }

        static bool IsRandomMove(Action action) => action.Skill != null && action.HasRandomMove;

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
                    // (Battle.Behind, the program's list at 0x64 - 0x68) that can be targeted (2026-10-16; before, the
                    // first foe of the other row, and only from the front row)
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
                bool firstFront = foes[0].Front;
                Unit firstRep = null, secondRep = null;
                var firstSum = new PySum();
                var secondSum = new PySum();
                for (int i = 0; i < foes.Length; i++)
                {
                    var t = foes[i];
                    if (t.Front == firstFront)
                    {
                        if (firstRep == null) firstRep = t;
                        AddMin(ref firstSum, t.Hp, battle.ExpectedDamage(action, t));
                    }
                    else
                    {
                        if (secondRep == null) secondRep = t;
                        AddMin(ref secondSum, t.Hp, battle.ExpectedDamage(action, t));
                    }
                }
                double s1 = firstSum.Result;
                if (secondRep != null)
                {
                    double s2 = secondSum.Result;
                    if (s2 > s1) { targetOut = secondRep; return s2; }
                }
                targetOut = firstRep;
                return s1;
            }
            if (code == T.RANDOM)
            {
                double hits = battle.MeanHits(action);
                double denom = Math.Max(1.0, hits);
                var sum = new PySum();
                for (int i = 0; i < foes.Length; i++)
                    sum.AddFloat(battle.ExpectedDamage(action, foes[i]) / denom);
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
            for (int i = 0; i < options.Count; i++)
            {
                var (skill, level) = options[i];
                scratch.Reset(unit, AKind.Skill, skill, level);
                int code = scratch.TargetCode;
                bool hits = (code == T.SINGLE || code == T.RANDOM || code == T.ROW || code == T.PIERCE || code == T.ALL || code == T.EVERYONE) &&
                            (scratch.Physical || scratch.Magic || scratch.IsSpecial);
                if (hits || scratch.HasRandomMove) { candidateSkills[candidates] = skill; candidateLevels[candidates] = level; candidates++; }
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
                int tpCost = Battle.EffectiveTpCost(action);
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

        /// <summary>A member lacks a buff when she has none of that effect, or when the one she has was put by the summon or a guest
        /// and is weaker than this action's (a status of the same effect replaces the old one even when weaker, 0x4f9b72: a player
        /// casts her stronger buff again over a guest's weaker one; P13.4 of the audit).</summary>
        static bool Lacks(Unit m, int effect, Action action)
        {
            var s = m.St[effect];
            if (s == null) return true;
            if (s.Source == null || (s.Source.Kind != Kind.Summon && s.Source.Kind != Kind.Npc)) return false;
            double mine = action.Val(effect, 0.0);
            return Math.Abs(s.Value) < Math.Abs(mine);
        }

        static bool ProvokedByUnit(Unit enemy, Unit unit) => enemy.St[170] != null && enemy.St[170].Source == unit;

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

        Action ActHeal(Battle battle, Unit unit, double threshold)
        {
            var hurt = battle.PolicyScratch;
            hurt.Clear();
            foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member && m.HpRatio < threshold) hurt.Add(m);
            if (hurt.Count == 0) return null;
            Skill bestSkill = null; int bestLevel = 0; Unit bestTarget = null; double bestScore = 0.0;
            var scratch = battle.ScratchAction;
            foreach (var (skill, level) in Options(battle, unit))
            {
                if (!GivesAny(skill, HEAL_EFFECTS)) continue;
                scratch.Reset(unit, AKind.Skill, skill, level);
                var action = scratch;
                Unit target; double restored;
                int code = action.TargetCode;
                if (code == T.ALLY)
                {
                    target = null;
                    foreach (var m in hurt) if (target == null || m.HpRatio < target.HpRatio) target = m;
                    restored = Math.Min(target.MaxHp - target.Hp, ExpectedHeal(battle, action, target));
                    if (target.HpRatio < 0.25) restored *= 1.3;
                    if (action.Has(104) && target.HpRatio < 0.4)
                    {
                        int critical = 0;
                        foreach (var m in hurt) if (m.HpRatio < 0.4) critical++;
                        if (critical <= 2 && (target.MaxHp - target.Hp) >= target.MaxHp * 0.35)
                            restored *= 2.5;
                    }
                }
                else if (code == T.ALLY_ROW)
                {
                    var frontSum = new PySum();
                    var backSum = new PySum();
                    Unit frontRep = null, backRep = null;
                    foreach (var m in battle.AlliesArray(unit))
                    {
                        if (m.Kind != Kind.Member) continue;
                        double v = Math.Min(m.MaxHp - m.Hp, ExpectedHeal(battle, action, m)) * (m.HpRatio < 0.25 ? 1.3 : 1.0);
                        if (m.Front) { frontSum.AddFloat(v); if (frontRep == null) frontRep = m; }
                        else { backSum.AddFloat(v); if (backRep == null) backRep = m; }
                    }
                    double fVal = frontSum.Result, bVal = backSum.Result;
                    if (frontRep != null && (backRep == null || fVal >= bVal)) { target = frontRep; restored = fVal; }
                    else { target = backRep; restored = bVal; }
                }
                else if (code == T.ALLIES || code == T.SELF)
                {
                    target = null;
                    var sum = new PySum();
                    if (code == T.SELF)
                    {
                        if (unit.Kind == Kind.Member)
                            sum.AddFloat(Math.Min(unit.MaxHp - unit.Hp, ExpectedHeal(battle, action, unit)) * (unit.HpRatio < 0.25 ? 1.3 : 1.0));
                    }
                    else
                    {
                        foreach (var m in battle.AlliesArray(unit))
                        {
                            if (m.Kind != Kind.Member) continue;
                            sum.AddFloat(Math.Min(m.MaxHp - m.Hp, ExpectedHeal(battle, action, m)) * (m.HpRatio < 0.25 ? 1.3 : 1.0));
                        }
                    }
                    restored = sum.Result;
                }
                else continue;
                double score = restored / TimeOf(battle, action) / TpPenalty(unit, action);
                if (score > bestScore)
                {
                    bestSkill = skill; bestLevel = level; bestScore = score;
                    bestTarget = target;
                }
            }
            if (bestSkill != null) return new Action(unit, AKind.Skill, bestSkill, bestLevel, bestTarget);
            if (unit.Items.Count > 0) return ActItem(battle, unit, "heal", null);
            return null;
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
                case "heal": kinds = ITEM_HEAL_KINDS; break;
                case "tp": kinds = ITEM_TP_KINDS; break;
                case "revive": kinds = ITEM_REVIVE_KINDS; break;
                case "cure": kinds = ITEM_CURE_KINDS; break;
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
                int allySlots = Math.Min(2, item.Kinds.Length);
                bool any = false;
                for (int i = 0; i < allySlots; i++) if (Array.IndexOf(kinds, item.Kinds[i]) >= 0) any = true;
                if (!any) continue;
                bool party = false;
                for (int i = 0; i < allySlots; i++) if (item.Kinds[i] == 3 || item.Kinds[i] == 4 || item.Kinds[i] == 5) party = true;
                double size;
                if (arg != "cure")
                {
                    bool first = true; size = 0;
                    for (int i = 0; i < allySlots; i++)
                        if (Array.IndexOf(kinds, item.Kinds[i]) >= 0)
                        {
                            double v = item.Values[i] != 0 ? item.Values[i] : 0;
                            if (first || v > size) { size = v; first = false; }
                        }
                }
                else
                {
                    size = 0;
                    for (int i = 0; i < allySlots; i++) if (item.Kinds[i] == Battle.ITEM_CURE_ALL) size = 1;
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

        Action ActStatus(Battle battle, Unit unit, int effect)
        {
            double reserve = HealReserve(battle, unit);
            var scratch = battle.ScratchAction;
            bool isDance = Battle.IsDance(effect);
            bool isPerf = Battle.IsSong(effect) || isDance;
            var options = Options(battle, unit);
            for (int oi = 0; oi < options.Count; oi++)
            {
                var (skill, level) = options[oi];
                if (!Puts(skill, effect)) continue;
                int tpCost = Battle.EffectiveTpCost(unit, skill, level);
                if (tpCost > 0 && unit.Tp - tpCost < reserve) continue;
                if (isPerf)
                {
                    bool hasAny = isDance ? unit.HasDances : unit.HasSongs;
                    if (hasAny)
                    {
                        var own = isDance ? unit.Dance : unit.Song;
                        if (!own.Contains(skill.Name) && own.Count >= Battle.PerformanceSlots(unit, isDance)) continue;
                    }
                    else if (Battle.PerformanceSlots(unit, isDance) <= 0) continue;
                }
                scratch.Reset(unit, AKind.Skill, skill, level);
                var action = scratch;
                int code = action.TargetCode;
                if (code == T.SELF || code == T.NO_TARGET)
                {
                    if (!Lacks(unit, effect, action)) continue;
                    if (effect == 26)
                    {
                        if (unit.HpRatio < 0.35) continue;
                        var foes = EnemiesOf(battle, unit);
                        if (foes.Length == 1 && foes[0].Hp < Math.Max(100.0, unit.Stat(Unit.ATK) * 1.5)) continue;
                    }
                    return new Action(unit, AKind.Skill, skill, level);
                }
                if (code == T.ALLY)
                {
                    var lacking = battle.PolicyScratch;
                    lacking.Clear();
                    foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member && Lacks(m, effect, action)) lacking.Add(m);
                    if (lacking.Count == 0) continue;
                    Unit chosenTarget;
                    if (effect == 171)
                    {
                        Unit best = null; int b0 = 0, b1 = 0, b2 = 0;
                        foreach (var m in lacking)
                        {
                            int k0 = m.Chant != null ? 0 : 1, k1 = m.HpRatio < 0.4 ? 0 : 1, k2 = m.Stat(Unit.DEF);
                            if (best == null || k0 < b0 || (k0 == b0 && (k1 < b1 || (k1 == b1 && k2 < b2)))) { best = m; b0 = k0; b1 = k1; b2 = k2; }
                        }
                        chosenTarget = best;
                    }
                    else if (effect == 162 && ProvokingAnyEnemy(battle, unit))
                    {
                        // a defence buff of a unit that draws the blows (Provoke up) goes on herself, the one hit, and on nobody else:
                        // the buff raises the DEF of the target by a share, so it is worth the turn on the highest DEF only
                        if (!lacking.Contains(unit)) continue;
                        chosenTarget = unit;
                    }
                    else
                    {
                        Unit best = null; int bk = 0;
                        foreach (var m in lacking)
                        {
                            // 168 (a speed buff such as Accelerator): the ally who hits hardest, by her higher of ATK and INT
                            int k = effect == 161 ? m.Stat(Unit.ATK) : effect == 162 ? m.Stat(Unit.DEF) : (effect == 27 || effect == 173) ? m.Stat(Unit.INT)
                                  : effect == 168 ? Math.Max(m.Stat(Unit.ATK), m.Stat(Unit.INT)) : 0;
                            if (best == null || k > bk) { best = m; bk = k; }
                        }
                        chosenTarget = best;
                    }
                    return new Action(unit, AKind.Skill, skill, level, chosenTarget);
                }
                if (code == T.ALLY_ROW)
                {
                    Unit frontTarget = null;
                    int frontMembers = 0, frontLacking = 0;
                    foreach (var m in battle.AlliesArray(unit))
                    {
                        if (m.Kind == Kind.Member && m.Front)
                        {
                            frontMembers++;
                            if (frontTarget == null) frontTarget = m;
                            if (Lacks(m, effect, action)) frontLacking++;
                        }
                    }
                    if (frontMembers == 0 || frontLacking == 0) continue;
                    return new Action(unit, AKind.Skill, skill, level, frontTarget);
                }
                // EVERYONE (Limit Field): a status on every unit of the field, kept up as a party buff is
                if (code == T.ALLIES || code == T.EVERYONE)
                {
                    int members = 0, lackingN = 0;
                    foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member) { members++; if (Lacks(m, effect, action)) lackingN++; }
                    double share = partyBuffRecastShare;
                    if (lackingN == 0 || lackingN < share * members) continue;
                    return new Action(unit, AKind.Skill, skill, level);
                }
                if (code == T.SINGLE || code == T.ALL || code == T.ROW)
                {
                    var foes = battle.PolicyScratch;
                    foes.Clear();
                    foreach (var t in EnemiesOf(battle, unit))
                    {
                        if (effect == 84 && (!t.Snack || t.Hp >= PyMath.Int(t.MaxHp * 0.5))) continue;
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
                    return new Action(unit, AKind.Skill, skill, level, best);
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
        static bool AnyAiling(Battle battle, Unit unit, int[] wanted)
        {
            foreach (var m in battle.AlliesArray(unit))
            {
                if (m.Kind != Kind.Member || m.StCount == 0) continue;
                for (int i = 0; i < wanted.Length; i++) if (m.St[wanted[i]] != null) return true;
            }
            return false;
        }

        static List<Unit> AilingMembers(Battle battle, Unit unit, int[] wanted)
        {
            var r = battle.PolicyScratch;
            r.Clear();
            foreach (var m in battle.AlliesArray(unit))
            {
                if (m.Kind != Kind.Member || m.StCount == 0) continue;
                for (int i = 0; i < wanted.Length; i++) if (m.St[wanted[i]] != null) { r.Add(m); break; }
            }
            return r;
        }

        Action ActAilment(Battle battle, Unit unit, Rule rule)
        {
            double floor = rule.AilmentFloor;
            bool ownFloor = rule.HasOwnFloor;
            var ailments = rule.AAilments;
            Skill bestSkill = null; int bestLevel = 0; Unit bestTarget = null;
            bool haveKey = false; int bestMax = 0; double bestChance = 0;
            var options = Options(battle, unit);
            var foes = EnemiesOf(battle, unit);
            var action = battle.ScratchAction;
            for (int ai = 0; ai < ailments.Length; ai++)
            {
                int effect = ailments[ai];
                string name = Battle.AilmentNameOf(effect);
                double ownEffFloor = (uint)effect < (uint)ailmentFloorByEffect.Length ? ailmentFloorByEffect[effect] : double.NaN;
                double floorOf = (double.IsNaN(ownEffFloor) || ownFloor) ? floor : ownEffFloor;
                int index = effect == 123 ? T.NONE : Battle.AilmentResistOf(effect);
                for (int oi = 0; oi < options.Count; oi++)
                {
                    var (skill, level) = options[oi];
                    if (!skill.HasEffect(effect)) continue;
                    action.Reset(unit, AKind.Skill, skill, level);
                    int code = action.TargetCode;
                    if (!(code == T.SINGLE || code == T.RANDOM || code == T.ROW || code == T.PIERCE || code == T.ALL)) continue;
                    bool has = false; double value = 0;
                    int n = action.Count;
                    for (int i = 0; i < n; i++) if (action.EffId(i) == effect && action.EffKind(i) != 2) { has = true; value = action.EffVal(i); break; }
                    if (!has) continue;
                    for (int fi = 0; fi < foes.Length; fi++)
                    {
                        var target = foes[fi];
                        if (target.Immune(name) || target.St[effect] != null || Battle.Nullified(target, effect)) continue;
                        double chance;
                        if (effect == 123) chance = unit.Level > target.Level ? value * 100 : 0.0;
                        else chance = F.AilmentChance(value, index != T.NONE ? target.Resistance(index) : 0);
                        int maxHp = target.MaxHp;
                        bool greater = !haveKey || maxHp > bestMax || (maxHp == bestMax && chance > bestChance);
                        if (chance >= floorOf && greater)
                        {
                            bestSkill = skill; bestLevel = level; bestTarget = target;
                            haveKey = true; bestMax = maxHp; bestChance = chance;
                        }
                    }
                }
                if (bestSkill != null) return new Action(unit, AKind.Skill, bestSkill, bestLevel, bestTarget);
            }
            return null;
        }

        Action ActDispel(Battle battle, Unit unit)
        {
            var buffed = battle.PolicyScratch;
            buffed.Clear();
            foreach (var t in EnemiesOf(battle, unit)) if (Battle.Dispellable(t)) buffed.Add(t);
            if (buffed.Count == 0) return null;
            var scratch = battle.ScratchAction;
            foreach (var (skill, level) in Options(battle, unit))
            {
                if (!Gives(skill, 74)) continue;
                scratch.Reset(unit, AKind.Skill, skill, level);
                var action = scratch;
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
                    return new Action(unit, AKind.Skill, skill, level, best);
            }
            return null;
        }

        static bool DollActiveOnSide(Battle battle, Unit unit, Skill skill)
        {
            foreach (var x in battle.Units)
            {
                if (!Battle.IsPuppet(x) || x.Side != unit.Side) continue;
                // AddPuppetCommand (0x43c83c..0x43c86e): guest/summon puppets do not conflict with party members' puppets.
                if (x.Owner != null && (x.Owner.Kind == Kind.Member) != (unit.Kind == Kind.Member)) continue;
                if ((x.Doll != null && x.Doll.Skill == skill.Id) || skill.HasEffect(x.PuppetEffect)) return true;
            }
            return false;
        }

        Action ActDoll(Battle battle, Unit unit, string[] dollNames)
        {
            var options = Options(battle, unit);
            if (dollNames != null)
            {
                for (int ni = 0; ni < dollNames.Length; ni++)
                {
                    string name = dollNames[ni];
                    for (int i = 0; i < options.Count; i++)
                    {
                        var (s, lv) = options[i];
                        if (s.Name == name && GivesAny(s, DOLL_EFFECTS) && !DollActiveOnSide(battle, unit, s))
                            return new Action(unit, AKind.Skill, s, lv);
                    }
                }
                return null;
            }
            Skill bestSkill = null; int bestLevel = -1;
            for (int i = 0; i < options.Count; i++)
            {
                var (s, lv) = options[i];
                if (GivesAny(s, DOLL_EFFECTS) && !DollActiveOnSide(battle, unit, s) && (bestSkill == null || lv > bestLevel))
                {
                    bestSkill = s; bestLevel = lv;
                }
            }
            return bestSkill != null ? new Action(unit, AKind.Skill, bestSkill, bestLevel) : null;
        }

        static bool ProvokingAnyEnemy(Battle battle, Unit unit)
        {
            foreach (var f in EnemiesOf(battle, unit))
                if (f.St[170] != null && f.St[170].Source == unit) return true;
            return false;
        }

        static readonly string[] HeavyRoles =
        {
            "tank", "attacker", "healer", "mage", "shooter", "dolls", "dark lord", "papillon",
            "valkyrie", "treasure hunter", "soul summoner", "magical princess", "sage",
            "kunoichi", "mistress", "joker"
        };

        Action ActTp(Battle battle, Unit unit, double f)
        {
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

        Action ActCure(Battle battle, Unit unit, int[] wanted)
        {
            var ailing = AilingMembers(battle, unit, wanted);
            if (ailing.Count == 0) return null;
            Unit target = null; int bk = 0;
            for (int ai = 0; ai < ailing.Count; ai++)
            {
                var m = ailing[ai];
                int k = 0;
                for (int i = 0; i < wanted.Length; i++) if (m.St[wanted[i]] != null) k++;
                if (target == null || k > bk) { target = m; bk = k; }
            }
            var scratch = battle.ScratchAction;
            var options = Options(battle, unit);
            for (int oi = 0; oi < options.Count; oi++)
            {
                var (skill, level) = options[oi];
                if (!Gives(skill, 106)) continue;
                scratch.Reset(unit, AKind.Skill, skill, level);
                double v = scratch.Val(106, 0); int n = v != 0 ? PyMath.Int(v) : 0;
                int limit = Math.Min(Math.Max(n, 0), Battle.CURE_ORDER.Length);
                bool any = false;
                for (int i = 0; i < limit && !any; i++)
                {
                    int ce = Battle.CURE_ORDER[i];
                    if (target.St[ce] != null)
                        for (int w = 0; w < wanted.Length; w++) if (wanted[w] == ce) { any = true; break; }
                }
                if (any)
                    return new Action(unit, AKind.Skill, skill, level, scratch.TargetCode == T.ALLY ? target : null);
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
                    else if (action.TargetCode == T.ALLY)
                    {
                        Unit best = null;
                        foreach (var m in battle.AlliesArray(unit)) if (m.Kind == Kind.Member && (best == null || m.HpRatio < best.HpRatio)) best = m;
                        action.Target = best;
                    }
                    return action;
                }
            }
            return null;
        }
    }
}
