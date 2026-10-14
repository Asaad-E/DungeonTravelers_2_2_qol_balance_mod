using System;
using System.Collections.Generic;

namespace DtEngine
{
    public enum Kind { Member = 0, Enemy = 1, Summon = 2, Doll = 3, Npc = 4 }

    /// <summary>One status on a unit. Turns 0 means it stays until removed (docs/FORMULAS.md 12.18).</summary>
    public sealed class Status
    {
        public const int SongKind = -2;      // kind 'song'
        public int Effect;
        public double Value;
        public double Turns;
        public Unit Source;
        public string Skill;
        public int Kind = 5;
        public bool HasData;
        public double Data;
        public bool IsInt;            // the value is an int in the Python (taken as it is from the data)

        public Status(int effect, double value, double turns = 0, Unit source = null, string skill = null, int kind = 5)
        {
            Effect = effect; Value = value; Turns = turns; Source = source; Skill = skill; Kind = kind;
        }

        public Status WithData(double data) { HasData = true; Data = data; return this; }
    }

    public sealed class Unit
    {
        public const int PARTY = 0, ENEMIES = 1;
        public const int ATK = 0, DEF = 1, INT = 2, RES = 3, DEX = 4, AGI = 5;
        public static readonly int[] StatBuff = { 41, 42, 43, 44, 45, 46 };
        static readonly int[] AllStatBuffs = { 189, 193, 194 };
        static readonly int[] ElementResistBuffs = { 169, 202, 248, 341 };
        public const int MAX_HP_BUFF = 172, TRUMP_CARD = 48;

        public string Name;
        public int Side, Level;
        public Kind Kind;
        public int MaxHpBase, MaxTp, Hp, Tp;
        public int[] Base = new int[6];
        public int[] ResistBase = new int[8];
        public double Weight, Swing;
        public int Race = T.NONE;
        public bool Front = true;
        public int Position;

        // statuses: one entry per effect id, in the order they were put (a dict)
        // (arrays are shared, read only, until the unit gets a first status, passive or enchantment: most units have few)
        static readonly Status[] NoStatuses = new Status[GameData.MaxEffect];
        static readonly double[] NoPassives = NewPassives();
        static readonly int[] NoEnchants = new int[GameData.MaxEnchant];
        public Status[] St = NoStatuses;
        int[] stOrder = Array.Empty<int>();
        public int StCount;
        // passives: NaN when the effect is not among them
        public double[] Pv = NoPassives;
        public bool[] PvInt;          // null: no passive is a whole number written as an int
        public int[] Enchants = NoEnchants;

        public long ImmuneMask;
        public List<(int id, int level)> Skills = new List<(int, int)>();
        public int[] Attacks = Array.Empty<int>();
        public Script Script;
        public Piece Weapon;
        public int AttackRange = T.SHORT, AttackAttr = T.NEUTRAL;
        public bool Alive = true;
        public double NextTime;
        public Action Chant;
        public List<string> Song = new List<string>(), Dance = new List<string>();
        public Unit Owner;
        public int TurnsTaken;
        public int LastSkillId = T.NONE;
        public Dictionary<string, int> Uses = new Dictionary<string, int>();
        public HashSet<long> OnceDone = new HashSet<long>();
        public bool EcstasyDone;
        public int SamsaraState;               // 0 None, 1 False, 2 a list
        public int[] Samsara;
        public int AiSet;
        public int Life;
        public List<(Unit unit, double value)> ProvokedBy = new List<(Unit, double)>();
        public double Pep = 100.0;
        public bool HasUnique;
        public int UniqueEffect;
        public double UniqueValue;
        public Character Character;
        public int ClassId = T.NONE;
        public bool Defending, Stolen;
        public Dictionary<int, int> Items = new Dictionary<int, int>();
        public bool Adult, Shield;
        public string Role = "attacker";
        public bool HasRole;
        public int[] Raw;
        public int Sealbook = T.NONE;
        public int EnemyId = T.NONE;
        public int Slot = T.NONE;              // formation slot of an enemy; NONE when not set
        public double Exp, Gold;
        public bool Snack;
        public DollRec Doll;
        public int DollLevel;
        public bool Arrow, Genjimaru;
        public Unit ShadowOf;
        public int Extra;
        public bool ExtraTurn, ExtraUnique;
        public List<(int word, int kind)> AiTargets;
        public int Id;                         // an index for tables, given by the owner of the units

        static double[] NewPassives()
        {
            var a = new double[GameData.MaxEffect];
            Array.Fill(a, double.NaN);
            return a;
        }

        public Unit(string name, int side, int level, int hp, int tp, int[] baseStats, int[] resist, double weight, double swing, int race, Kind kind)
        {
            Name = name; Side = side; Level = level; Kind = kind;
            MaxHpBase = hp; MaxTp = tp; Hp = hp; Tp = tp;
            Array.Copy(baseStats, Base, 6);
            if (resist != null) Array.Copy(resist, ResistBase, 8);
            Weight = weight; Swing = swing; Race = race;
        }

        // --- statuses --------------------------------------------------------------------------------------
        public bool HasStatus(int e) => St[e] != null;

        public void SetStatus(Status s)
        {
            if (St == NoStatuses) St = new Status[GameData.MaxEffect];
            if (St[s.Effect] == null)
            {
                if (StCount == stOrder.Length) Array.Resize(ref stOrder, Math.Max(8, StCount * 2));
                stOrder[StCount++] = s.Effect;
            }
            St[s.Effect] = s;
        }

        public Status PopStatus(int e)
        {
            var s = St[e];
            if (s == null) return null;
            St[e] = null;
            for (int i = 0; i < StCount; i++)
                if (stOrder[i] == e)
                {
                    for (int j = i; j < StCount - 1; j++) stOrder[j] = stOrder[j + 1];
                    StCount--;
                    break;
                }
            return s;
        }

        public void ClearStatuses()
        {
            for (int i = 0; i < StCount; i++) St[stOrder[i]] = null;
            StCount = 0;
        }

        /// <summary>The effects of the statuses, in order (a copy: list(unit.statuses)).</summary>
        public int[] StatusOrder()
        {
            var r = new int[StCount];
            Array.Copy(stOrder, r, StCount);
            return r;
        }

        public int StatusAt(int i) => stOrder[i];

        public double StatusValue(int e, double dflt = 0.0) { var s = St[e]; return s != null ? s.Value : dflt; }

        // --- passives -------------------------------------------------------------------------------------
        public bool HasPassive(int e) => !double.IsNaN(Pv[e]);
        public bool PassiveIsInt(int e) => PvInt != null && PvInt[e];
        public double Passive(int e, double dflt = 0.0) { double v = Pv[e]; return double.IsNaN(v) ? dflt : v; }
        public void SetPassive(int e, double v, bool isInt = false)
        {
            if (Pv == NoPassives) Pv = NewPassives();
            Pv[e] = v;
            if (isInt) { if (PvInt == null) PvInt = new bool[GameData.MaxEffect]; PvInt[e] = true; }
            else if (PvInt != null) PvInt[e] = false;
        }

        /// <summary>The unit takes this array as its passives (NaN where there is none); the caller keeps no reference.</summary>
        public void AdoptPassives(double[] values) { Pv = values; }

        public void SetEnchants(int[] pieces) { Enchants = pieces; }

        public bool Has(int e) => St[e] != null || !double.IsNaN(Pv[e]);

        /// <summary>Value of an effect on the unit, as a status or a passive (a status first).</summary>
        public double Value(int e, double dflt = 0.0)
        {
            var s = St[e];
            if (s != null) return s.Value;
            double v = Pv[e];
            return double.IsNaN(v) ? dflt : v;
        }

        public int Pieces(int enchant) => Enchants[enchant];

        public bool Immune(string name) => Snapshot.ImmuneBits.TryGetValue(name, out int bit) && (ImmuneMask & (1L << bit)) != 0;

        // --- stats -----------------------------------------------------------------------------------------
        public int Stat(int name)
        {
            int b = Base[name];
            int total = b;
            var s = St[StatBuff[name]];
            if (s != null) total += PyMath.Int(b * s.Value);
            for (int i = 0; i < 3; i++)
            {
                s = St[AllStatBuffs[i]];
                if (s != null) total += PyMath.Int(b * s.Value);
            }
            if (name == ATK && St[TRUMP_CARD] != null) total += PyMath.Int(Base[DEF] * St[TRUMP_CARD].Value);
            if (name == DEF && St[TRUMP_CARD] != null) total = 0;
            if (St[120] != null)
            {
                if (name == DEF) total += b / 2;
                if (name == AGI) total -= b / 2;
            }
            return Math.Max(0, total);
        }

        public int MaxHp
        {
            get
            {
                int hp = MaxHpBase;
                var s = St[MAX_HP_BUFF];
                if (s != null) hp += PyMath.Int(hp * s.Value);
                return hp;
            }
        }

        public int Resistance(int index)
        {
            if (SamsaraState == 2) return Samsara[index];
            int value = ResistBase[index];
            if (index >= 3)
            {
                for (int i = 0; i < 4; i++)
                {
                    int e = ElementResistBuffs[i];
                    if (Has(e)) value += PyMath.Int(Value(e));
                }
            }
            else
            {
                // PHYSICAL_RESIST_BUFFS {185: 0, 184: 1, 186: 2}
                int e = index == 0 ? 185 : index == 1 ? 184 : 186;
                var s = St[e];
                if (s != null) value += PyMath.Int(s.Value);
            }
            return value;
        }

        public bool IsMember => Kind == Kind.Member;

        public double HpRatio { get { int m = MaxHp; return m != 0 ? (double)Hp / m : 0.0; } }
        public double TpRatio => MaxTp != 0 ? (double)Tp / MaxTp : 1.0;

        public override string ToString() => Name + " L" + Level + " " + Hp + "/" + MaxHp;
    }

    public static class UnitFactory
    {
        public const int MASTERY = 243, MASTERY_ALL = 298, DUAL_WIELD = 256, YEARNING = 449;
        public const int DOLL_HP = 9999;
        public const int ADULT_BIT = 13;
        public const int SOUL_SEAL = 314;

        public static int[] StatArray() => new int[6];

        public static (int figure, int divisor, int floor)? Share(int e) => F.ENCHANT_SHARE.TryGetValue(e, out var v) ? v : ((int, int, int)?)null;

        public static ClassMod[] ClassModifierEntries(GameData data, int classId, int previous)
        {
            // the first exact match; else the first with no previous class; else the first row
            ClassMod exact = null, none = null, first = null;
            foreach (var m in data.ClassModifiers)
            {
                if (m.Class != classId) continue;
                if (first == null) first = m;
                if (exact == null && m.Previous == previous) exact = m;
                if (none == null && m.Previous == T.NONE) none = m;
            }
            var chosen = exact ?? none ?? first;
            return chosen == null ? Array.Empty<ClassMod>() : new[] { chosen };
        }

        public static ModEntry[] ModifierList(GameData data, int classId, int previous)
        {
            var c = ClassModifierEntries(data, classId, previous);
            return c.Length == 0 ? Array.Empty<ModEntry>() : c[0].Entries;
        }

        /// <summary>enchant_bonus: what the enchantments add to a character. Fills total[6], returns hp, tp, resist[8].</summary>
        public static void EnchantBonus(Dictionary<int, int> enchants, int[] baseStats, int baseHp, int baseTp, bool front,
                                        int[] total, out int hpOut, out int tpOut, int[] resistOut)
        {
            Array.Clear(total, 0, 6);
            int hp = 0, tp = 0;
            var resist = new int[8];
            foreach (var kv in enchants)
            {
                int e = kv.Key, n = kv.Value;
                for (int rep = 0; rep < n; rep++)
                {
                    if (F.ENCHANT_SHARE.TryGetValue(e, out var sh))
                    {
                        int source = sh.figure == F.FIG_HP ? baseHp : sh.figure == F.FIG_TP ? baseTp : baseStats[sh.figure];
                        int share = Math.Max(sh.floor, PyMath.Int(source / (double)Math.Abs(sh.divisor)));
                        share = sh.divisor > 0 ? share : -share;
                        if (sh.figure == F.FIG_HP) hp += share;
                        else if (sh.figure == F.FIG_TP) tp += share;
                        else total[sh.figure] += share;
                    }
                    if (F.ENCHANT_ALL_STATS.TryGetValue(e, out int all))
                        for (int s = 0; s < 6; s++) total[s] += all;
                    if (F.ENCHANT_RESIST.TryGetValue(e, out var rs))
                        foreach (var (index, value) in rs) resist[index] += value;
                    if (F.ENCHANT_LINE.TryGetValue(e, out var line) && line.front == front)
                        foreach (var (stat, share) in line.shares)
                            total[stat] += share < 1 ? PyMath.Int(baseStats[stat] * share) : PyMath.Int(baseStats[stat] / share);
                }
            }
            int halfHp = PyMath.Int(baseHp / 2.0), halfTp = PyMath.Int(baseTp / 2.0);
            int cap = F.ENCHANT_RESIST_CAP;
            hpOut = Math.Max(-halfHp, Math.Min(halfHp, hp));
            tpOut = Math.Max(-halfTp, Math.Min(halfTp, tp));
            for (int i = 0; i < 8; i++) resistOut[i] = Math.Max(-cap, Math.Min(cap, resist[i]));
        }

        public static int UniqueRank(int level, int crownBonus) => crownBonus >= 50 ? 10 : level / 10;

        public sealed class PieceUse
        {
            public int Slot, EquipId, Upgrade;
            public PieceUse(int slot, int equipId, int upgrade) { Slot = slot; EquipId = equipId; Upgrade = upgrade; }
        }

        public static int[] PieceStats(Piece piece, int upgrade)
        {
            var r = new int[6];
            for (int s = 0; s < 6; s++) r[s] = piece.Stats[s] != 0 ? piece.Stats[s] + PyMath.Int(upgrade * piece.Rate) : 0;
            return r;
        }

        public static Unit BuildMember(GameData data, Character character, int classId, int level, int previous, List<PieceUse> equipment,
                                       List<(int id, int level)> skills, int crownBonus, string name, bool front,
                                       Dictionary<int, int> items, int sealbook, int[] partyEnchants, Dictionary<int, int> forged)
        {
            int row = data.GrowthRowOf(classId, previous);
            int[] grown = data.Stats(row, level);
            var characterStats = new int[6];
            for (int s = 0; s < 6; s++) characterStats[s] = grown[s] + crownBonus;
            int hp = grown[6] + crownBonus, tp = grown[7] + crownBonus;
            var passiveValues = new double[GameData.MaxEffect];
            Array.Fill(passiveValues, double.NaN);
            bool[] passiveInt = null;
            if (skills != null)
            {
                foreach (var (skillId, lv) in skills)
                {
                    var skill = data.GetSkill("Passive", skillId);
                    if (skill != null)
                    {
                        foreach (var eff in skill.Effects)
                        {
                            int at = Math.Min(lv, eff.Values.Length) - 1;
                            double value = eff.Values[at];
                            bool valueInt = eff.IsInt[at];
                            bool hasExisting = !double.IsNaN(passiveValues[eff.Id]);
                            double existing = hasExisting ? passiveValues[eff.Id] : value;
                            bool existingInt = hasExisting ? passiveInt != null && passiveInt[eff.Id] : valueInt;
                            bool keep = Math.Abs(existing) >= Math.Abs(value);       // max(a, b, key=abs): the first of equals
                            passiveValues[eff.Id] = keep ? existing : value;
                            bool chosenInt = keep ? existingInt : valueInt;
                            if (chosenInt) { if (passiveInt == null) passiveInt = new bool[GameData.MaxEffect]; passiveInt[eff.Id] = true; }
                            else if (passiveInt != null) passiveInt[eff.Id] = false;
                        }
                    }
                }
            }
            bool hasUnique = false;
            int uniqueEffect = 0;
            double uniqueValue = 0;
            int rank = UniqueRank(level, crownBonus);
            if (character != null && character.UniqueSkill != T.NONE && rank > 0)
            {
                if (data.Unique.TryGetValue(character.UniqueSkill, out var u))
                {
                    hasUnique = true;
                    uniqueEffect = u.Effect;
                    uniqueValue = u.Values[Math.Min(10, rank) - 1];
                    passiveValues[u.Effect] = uniqueValue;
                    if (u.IsInt[Math.Min(10, rank) - 1]) { if (passiveInt == null) passiveInt = new bool[GameData.MaxEffect]; passiveInt[u.Effect] = true; }
                    else if (passiveInt != null) passiveInt[u.Effect] = false;
                }
            }
            double PV(int e, double d) => double.IsNaN(passiveValues[e]) ? d : passiveValues[e];
            double mastery = PV(MASTERY, 0.0) + PV(MASTERY_ALL, 0.0);
            var totals = (int[])characterStats.Clone();
            var enchants = new Dictionary<int, int>();
            var enchantOrder = new List<int>();
            Piece weapon = null;
            double yearning = PV(YEARNING, 0.0);
            var modifiers = ModifierList(data, classId, previous);
            var gains = new int[6];
            foreach (var use in equipment)
            {
                var piece = data.Equipment[use.EquipId];
                int[] stats = PieceStats(piece, use.Upgrade);
                if (use.Slot == 0 && piece.Category == 0)
                {
                    weapon = piece;
                    stats[Unit.ATK] = stats[Unit.ATK] + PyMath.Int(stats[Unit.ATK] * mastery);
                    stats[Unit.RES] = stats[Unit.RES] + PyMath.Int(stats[Unit.RES] * mastery);
                }
                if (use.Slot == 1 && piece.Category == 0)
                {
                    double share = PV(DUAL_WIELD, 0.0);
                    for (int s = 0; s < 6; s++) stats[s] = PyMath.Int(stats[s] * share);
                }
                for (int s = 0; s < 6; s++) totals[s] += stats[s];
                foreach (int e in piece.Enchants)
                {
                    enchants.TryGetValue(e, out int c);
                    enchants[e] = c + 1;
                }
                foreach (var entry in modifiers)
                {
                    bool matches = entry.Slot == use.Slot && (use.Slot != 0 || piece.Type == entry.Type)
                                   && (use.Slot != 1 || piece.Category == 1);
                    if (matches)
                        for (int s = 0; s < 6; s++)
                            if (stats[s] > 0)
                                gains[s] += Math.Max(0, PyMath.Int((characterStats[s] + stats[s]) * (entry.Modifier + 0.01 * yearning)));
                }
            }
            for (int s = 0; s < 6; s++) totals[s] += gains[s];
            if (sealbook != T.NONE && data.SealbookEnchants.TryGetValue(sealbook, out var sbe))
                foreach (int e in sbe) { enchants.TryGetValue(e, out int c); enchants[e] = c + 1; }
            if (partyEnchants != null)
                foreach (int e in partyEnchants) { enchants.TryGetValue(e, out int c); enchants[e] = c + 1; }
            if (forged != null)
                foreach (var kv in forged) { enchants.TryGetValue(kv.Key, out int c); enchants[kv.Key] = c + kv.Value; }
            var counted = new Dictionary<int, int>();
            foreach (var kv in enchants) counted[kv.Key] = data.EnchantStacks.Contains(kv.Key) ? kv.Value : Math.Min(kv.Value, 1);
            var bonusTotal = new int[6];
            var resistBonus = new int[8];
            EnchantBonus(counted, characterStats, hp, tp, front, bonusTotal, out int bonusHp, out int bonusTp, resistBonus);
            for (int s = 0; s < 6; s++) totals[s] += bonusTotal[s];
            hp += bonusHp; tp += bonusTp;
            var resist = new int[8];
            for (int i = 0; i < 8; i++) resist[i] = crownBonus + resistBonus[i];
            double rankDelay = weapon != null && weapon.Rank != T.NONE && weapon.Rank >= 0 ? data.WeaponRanks[weapon.Rank] : UnarmedDelay(data);
            var unit = new Unit(name ?? (character != null ? character.Name : "class " + classId), Unit.PARTY, level, hp, tp, totals, resist,
                                rankDelay, weapon != null ? weapon.Swing : 0.0, T.NONE, Kind.Member);
            unit.AdoptPassives(passiveValues);
            unit.PvInt = passiveInt;
            unit.Raw = (int[])characterStats.Clone();
            if (counted.Count > 0)
            {
                var pieces = new int[GameData.MaxEnchant];
                foreach (var kv in counted) pieces[kv.Key] = kv.Value;
                unit.SetEnchants(pieces);
            }
            unit.Sealbook = sealbook;
            unit.Weapon = weapon;
            unit.AttackRange = weapon != null ? weapon.Range : T.SHORT;
            unit.AttackAttr = weapon != null ? weapon.Attr : 3;
            if (skills != null)
                foreach (var (sid, lv) in skills)
                    if (!data.IsPassiveId(sid)) unit.Skills.Add((sid, lv));
            unit.HasUnique = hasUnique; unit.UniqueEffect = uniqueEffect; unit.UniqueValue = uniqueValue;
            unit.Character = character;
            unit.Adult = character != null && character.Flag == 1;
            bool shield = false;
            foreach (var use in equipment) if (use.Slot == 1 && data.Equipment[use.EquipId].Category == 1) shield = true;
            unit.Shield = shield;
            unit.ClassId = classId;
            unit.Front = front;
            if (items != null) unit.Items = new Dictionary<int, int>(items);
            return unit;
        }

        public static double UnarmedDelay(GameData data) => data.WeaponRanks[5];

        public static Unit BuildEnemy(GameData data, int enemyId, bool front, string name = null)
        {
            var e = data.Enemies[enemyId];
            var unit = new Unit(name ?? e.Name, Unit.ENEMIES, e.Level, e.Hp, 0, e.Stats, e.Resist, e.Weight, e.Swing, e.Race, Kind.Enemy);
            unit.ImmuneMask = e.ImmuneMask;
            unit.Attacks = e.Attacks;
            unit.Script = e.Script;
            unit.Front = front;
            unit.EnemyId = enemyId;
            unit.Exp = e.Exp; unit.Gold = e.Gold;
            unit.Snack = e.Snack;
            unit.Adult = ((e.Flags >> ADULT_BIT) & 1) != 0;
            foreach (int attackId in e.Passives)
            {
                var attack = data.GetAttack(attackId);
                if (attack != null)
                    for (int k = 0; k < attack.EffId.Length; k++) unit.SetPassive(attack.EffId[k], attack.EffValue[k], attack.EffIsInt[k]);
            }
            return unit;
        }

        public static Unit BuildSummon(GameData data, SummonForm form, List<Unit> party, int hp)
        {
            data.Enemies.TryGetValue(form.Enemy, out var enemy);
            var stats = new int[6];
            for (int s = 0; s < 6; s++)
            {
                int floor = enemy != null ? enemy.Stats[s] : 0;
                bool any = false;
                int best = 0;
                foreach (var m in party)
                {
                    if (m.Kind != Kind.Member) continue;
                    int v = m.Raw != null ? m.Raw[s] : m.Base[s];
                    if (!any || v > best) { best = v; any = true; }
                }
                stats[s] = Math.Max(floor, PyMath.Int(PyMath.Single(best * form.Factors[s])));
            }
            double weight = data.WeaponRanks.TryGetValue(form.Rank, out var w) ? w : 2.0;
            var unit = new Unit(form.Name, Unit.PARTY, form.Level, hp, 0, stats, null, weight, 0.0, T.NONE, Kind.Summon);
            unit.Attacks = form.Attacks;
            unit.Script = form.Script;
            if (form.Passive != T.NONE && data.Attacks.TryGetValue(form.Passive, out var pa))
                for (int k = 0; k < pa.EffId.Length; k++) unit.SetPassive(pa.EffId[k], pa.EffValue[k], pa.EffIsInt[k]);
            return unit;
        }

        public static Unit BuildDoll(Unit owner, DollRec doll, int level, GameData data)
        {
            var baseStats = (int[])owner.Base.Clone();
            if (data != null && owner.Has(SOUL_SEAL) && owner.Sealbook != T.NONE && data.Enemies.ContainsKey(owner.Sealbook))
            {
                var sealed_ = data.Enemies[owner.Sealbook];
                for (int s = 0; s < 6; s++) baseStats[s] += PyMath.Int(sealed_.Stats[s] * owner.Value(SOUL_SEAL));
            }
            var unit = new Unit(doll.Name, owner.Side, owner.Level, DOLL_HP, 0, baseStats, null, owner.Weight, 0.0, T.NONE, Kind.Doll);
            unit.Owner = owner;
            unit.Life = doll.Turns[level - 1];
            unit.Doll = doll;
            unit.DollLevel = level;
            unit.AttackRange = doll.Range == "short" ? T.SHORT : doll.Range == "mid" ? T.MID : doll.Range == "long" ? T.LONG : T.SHORT;
            unit.Front = owner.Front;
            return unit;
        }
    }
}
