using System;
using System.Collections.Generic;
using System.Linq;

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
        public int AttackId = T.NONE;
        public int Kind = 5;
        public bool HasData;
        public double Data;
        public int Stage;             // petrification stage counter (0x48305a: lethal at stage 3)
        public bool IsInt;            // the value is an int in the Python (taken as it is from the data)

        public Status(int effect, double value, double turns = 0, Unit source = null, string skill = null, int kind = 5, int attackId = T.NONE)
        {
            Effect = effect; Value = value; Turns = turns; Source = source; Skill = skill; Kind = kind; AttackId = attackId;
        }

        public Status WithData(double data) { HasData = true; Data = data; return this; }
    }

    /// <summary>What the lists of the units of a battle depend on: a number that rises each time a unit falls, rises or joins.</summary>
    public sealed class Roster
    {
        public int Version;
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
        public int MaxHpBase, BaseHp, MaxTp, Hp, Tp;
        public int[] Base = new int[6];
        public int[] OffhandBonus;            // off-hand dual-wield weapon stats added after stat buffs (0x4fc26f..0x4fc5c1)
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
        [ThreadStatic] static Stack<Status[]> statusPool;
        public Status[] St = NoStatuses;
        int[] stOrder = Array.Empty<int>();
        public int StCount;
        int statModCount;               // count of active statuses affecting Stat(name)
        bool hasElemResistPassive;      // true if any ElementResistBuffs passive is set
        // passives: NaN when the effect is not among them
        public double[] Pv = NoPassives;
        public Action.FxSet PlainEffects;     // the effects of the plain attack of this unit (made when first asked)
        public bool[] PvInt;          // null: no passive is a whole number written as an int
        public int[] Enchants = NoEnchants;
        public bool HasEnchants;
        public bool HasNullifyEnchant;
        public bool HasRaceAttackEnchant;
        public bool HasRaceGuardEnchant;

        public long ImmuneMask;
        public List<(int id, int level)> Skills = new List<(int, int)>();
        internal (Skill skill, int level)[] UsableSkills;     // filtered battle-usable skills matching weapon, built lazily and shared by clones
        public bool HasPassives => Pv != NoPassives;
        public int[] Attacks = Array.Empty<int>();
        public Script Script;
        public Piece Weapon;
        public int AttackRange = T.SHORT, AttackAttr = T.NEUTRAL;
        bool alive = true;
        public Roster Roster;
        public bool Alive
        {
            get { return alive; }
            set { if (alive != value) { alive = value; if (Roster != null) Roster.Version++; } }
        }
        /// <summary>0x4fb600 (vtable+0xc8): true when Petrification (120) has reached Stage >= 3.</summary>
        public bool IsFullPetrified => St[120] != null && St[120].Stage >= 3;
        /// <summary>0x4fbd90 (vtable+0xe8): alive AND not Stage-3 Petrified (targetable, healable, counted for victory/defeat).</summary>
        public bool CanFight => alive && !IsFullPetrified;
        public void InvalidateRoster() { if (Roster != null) Roster.Version++; }
        public double NextTime;
        public Action Chant;
        List<string> song, dance, geass;
        List<int> songIds, danceIds, geassIds;
        public List<string> Song => song ?? (song = new List<string>());
        public List<string> Dance => dance ?? (dance = new List<string>());
        public List<string> Geass => geass ?? (geass = new List<string>());
        public List<int> SongIds => songIds ?? (songIds = new List<int>());
        public List<int> DanceIds => danceIds ?? (danceIds = new List<int>());
        public List<int> GeassIds => geassIds ?? (geassIds = new List<int>());
        public bool HasSongs => (songIds != null && songIds.Count > 0) || (song != null && song.Count > 0);
        public bool HasDances => (danceIds != null && danceIds.Count > 0) || (dance != null && dance.Count > 0);
        public bool HasGeass => (geassIds != null && geassIds.Count > 0) || (geass != null && geass.Count > 0);
        public void ClearSongsAndDances() { song?.Clear(); dance?.Clear(); geass?.Clear(); songIds?.Clear(); danceIds?.Clear(); geassIds?.Clear(); }
        public Unit Owner;
        public int TurnsTaken;
        public int LastSkillId = T.NONE;
        Dictionary<string, int> uses;
        public Dictionary<string, int> Uses => uses ?? (uses = new Dictionary<string, int>());
        Dictionary<int, int> usesById;
        public Dictionary<int, int> UsesById => usesById ?? (usesById = new Dictionary<int, int>());
        public int UsesOf(int id) => usesById != null && usesById.TryGetValue(id, out int n) ? n : 0;
        public void RecordUseById(int id) { var d = UsesById; d.TryGetValue(id, out int n); d[id] = n + 1; }
        HashSet<long> onceDone;
        public HashSet<long> OnceDone => onceDone ?? (onceDone = new HashSet<long>());
        public bool HasOnceDone(long key) => onceDone != null && onceDone.Contains(key);
        public bool EcstasyDone;
        public int SamsaraState;               // 0 None, 1 False, 2 a list
        public int[] Samsara;
        public int AiSet;
        public int Life;
        public int BaseTargetShare;            // initial formation target share computed once at battle start (0x43daca)
        public double Pep = 100.0;
        public bool HasUnique;
        public int UniqueEffect;
        public double UniqueValue;
        public Character Character;
        public int ClassId = T.NONE;
        public int PreviousClass = T.NONE;
        public bool Defending, StolenGold, StolenItem;     // a gold steal and an item steal each succeed once (0x155, 0x154 of the unit)
        public Dictionary<int, int> Items = new Dictionary<int, int>();
        public bool Adult, Shield, HasHead, HasBody;
        public string Role = "attacker";
        public bool HasRole;
        public int[] Raw;
        public int[] DollBase;        // exact player-doll base stats from 0x4f7c00 (growth without reset bonus + copied equipment + class mods + equip enchants)
        public int Sealbook = T.NONE;
        public int EnemyId = T.NONE;
        public bool IsGuest;          // a hired guest ally (built with the kind of the summon)
        public int TieKey;            // order on a tie of times (0x440b85): member 999 - slot, enemy 994 - index, summon 930, guest 929, doll lowest
        public int Slot = T.NONE;              // formation slot of an enemy; NONE when not set
        public double Exp, Gold;
        public bool Snack;
        public DollRec Doll;
        public int DollLevel;
        public int SummonAttackId = T.NONE;    // EnemyAttackData id that summoned a guest/enemy doll (0x4320e3 / 0x432111)
        public int PuppetEffect = T.NONE;      // 228..233 puppet effect id for same-type uniqueness and owner cap (0x43c816)
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
            MaxHpBase = hp; BaseHp = hp; MaxTp = tp; Hp = hp; Tp = tp;
            Array.Copy(baseStats, Base, 6);
            if (resist != null) Array.Copy(resist, ResistBase, 8);
            Weight = weight; Swing = swing; Race = race;
        }

        /// <summary>A unit as it was when it was built, made from a unit that has not been in a battle: what is only read (passives,
        /// enchantments, skills, attacks, script) is shared, what a battle changes is made new. The bag of items is copied unless copyItems is false.</summary>
        public Unit CloneFresh(bool copyItems = true)
        {
            var c = (Unit)MemberwiseClone();
            c.Base = (int[])Base.Clone();
            if (OffhandBonus != null) c.OffhandBonus = (int[])OffhandBonus.Clone();
            c.ResistBase = (int[])ResistBase.Clone();
            c.St = NoStatuses; c.stOrder = Array.Empty<int>(); c.StCount = 0; c.statModCount = 0;
            pvShared = true; c.pvShared = true;
            c.song = null; c.dance = null; c.geass = null; c.songIds = null; c.danceIds = null; c.geassIds = null;
            c.uses = null; c.usesById = null; c.onceDone = null;
            c.Items = copyItems ? new Dictionary<int, int>(Items) : Items;
            c.Chant = null; c.Owner = null; c.ShadowOf = null; c.AiTargets = null; c.Samsara = null; c.Roster = null;
            return c;
        }

        /// <summary>Clamps Pep to [70, 130] and applies pep-locking enchantments 201 (70), 200 (>=100), 195 (130) (0x4f69e0..0x4f6a6a).</summary>
        public void ClampPep()
        {
            Pep = F.Clamp(Pep, 70.0, 130.0);
            if (!HasEnchants) return;
            if (Pieces(201) != 0) Pep = 70.0;
            if (Pieces(200) != 0 && Pep < 100.0) Pep = 100.0;
            if (Pieces(195) != 0) Pep = 130.0;
        }

        // --- statuses --------------------------------------------------------------------------------------
        static bool IsStatModEffect(int e) => (e >= 41 && e <= 46) || e == 48 || e == 120 || e == 189 || e == 193 || e == 194;
        static bool IsElemResistBuff(int e) => e == 169 || e == 202 || e == 248 || e == 341;

        static Status[] RentStatusArray()
        {
            var pool = statusPool;
            if (pool != null && pool.Count > 0) return pool.Pop();
            return new Status[GameData.MaxEffect];
        }

        public bool HasStatus(int e) => St[e] != null;

        public void SetStatus(Status s)
        {
            // 0x4f9950 (vtable+0xc8): Stage-3 Petrified units reject all new statuses except explicit 120 updates.
            if (IsFullPetrified && s.Effect != 120) return;
            if (St == NoStatuses) St = RentStatusArray();
            bool wasPet3 = IsFullPetrified;
            // 0x4f9bff..0x4f9c7c (vtable+0x7c == 1 -> 325..329): elemental weapon enchants are mutually exclusive.
            if (s.Effect >= 325 && s.Effect <= 329)
            {
                for (int e = 325; e <= 329; e++) if (e != s.Effect && St[e] != null) PopStatus(e);
            }
            // 0x4f9c7c..0x4f9cfc (vtable+0x84 == 1 -> 101, 102, 181): barriers are mutually exclusive.
            else if (s.Effect == 101 || s.Effect == 102 || s.Effect == 181)
            {
                if (s.Effect != 101 && St[101] != null) PopStatus(101);
                if (s.Effect != 102 && St[102] != null) PopStatus(102);
                if (s.Effect != 181 && St[181] != null) PopStatus(181);
            }
            if (St[s.Effect] == null)
            {
                if (StCount == stOrder.Length) Array.Resize(ref stOrder, Math.Max(8, StCount * 2));
                stOrder[StCount++] = s.Effect;
                if (IsStatModEffect(s.Effect)) statModCount++;
            }
            St[s.Effect] = s;
            if (wasPet3 != IsFullPetrified) InvalidateRoster();
        }

        public Status PopStatus(int e)
        {
            var s = St[e];
            if (s == null) return null;
            bool wasPet3 = IsFullPetrified;
            St[e] = null;
            if (IsStatModEffect(e)) statModCount--;
            for (int i = 0; i < StCount; i++)
                if (stOrder[i] == e)
                {
                    for (int j = i; j < StCount - 1; j++) stOrder[j] = stOrder[j + 1];
                    StCount--;
                    break;
                }
            // 0x4fc63a..0x4fc644: clamp current HP to MaxHp when Max HP buff (172) is removed.
            if (e == MAX_HP_BUFF && Hp > MaxHp) Hp = MaxHp;
            if (wasPet3 != IsFullPetrified) InvalidateRoster();
            return s;
        }

        public void ClearStatuses()
        {
            bool wasPet3 = IsFullPetrified;
            for (int i = 0; i < StCount; i++) St[stOrder[i]] = null;
            StCount = 0;
            statModCount = 0;
            if (wasPet3) InvalidateRoster();
        }

        /// <summary>0x4fa960 (ClearBattleStatuses): removes battle-only statuses while preserving true ailments (113..122).</summary>
        public void ClearBattleStatuses()
        {
            int write = 0;
            int mods = 0;
            bool wasPet3 = IsFullPetrified;
            for (int i = 0; i < StCount; i++)
            {
                int e = stOrder[i];
                bool keep = e >= 113 && e <= 122;
                if (keep)
                {
                    stOrder[write++] = e;
                    if (IsStatModEffect(e)) mods++;
                }
                else
                {
                    St[e] = null;
                }
            }
            StCount = write;
            statModCount = mods;
            if (Hp > MaxHp) Hp = MaxHp;
            if (wasPet3 != IsFullPetrified) InvalidateRoster();
        }

        /// <summary>Clears all statuses and returns the status backing array to the thread-local pool.</summary>
        public void ReleaseStatuses()
        {
            if (St == NoStatuses) return;
            ClearStatuses();
            var pool = statusPool ?? (statusPool = new Stack<Status[]>(32));
            if (pool.Count < 32) pool.Push(St);
            St = NoStatuses;
        }

        /// <summary>The effects of the statuses, in order (a copy: list(unit.statuses)).</summary>
        public int[] StatusOrder()
        {
            if (StCount == 0) return Array.Empty<int>();
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
        bool pvShared;          // Pv and PvInt belong to other units made from the same template: copied before they are changed

        public void SetPassive(int e, double v, bool isInt = false)
        {
            if (Pv == NoPassives) Pv = NewPassives();
            else if (pvShared)
            {
                Pv = (double[])Pv.Clone();
                if (PvInt != null) PvInt = (bool[])PvInt.Clone();
                pvShared = false;
            }
            Pv[e] = v;
            if (IsElemResistBuff(e) && !double.IsNaN(v)) hasElemResistPassive = true;
            if (isInt) { if (PvInt == null) PvInt = new bool[GameData.MaxEffect]; PvInt[e] = true; }
            else if (PvInt != null) PvInt[e] = false;
        }

        /// <summary>The unit takes this array as its passives (NaN where there is none); the caller keeps no reference.</summary>
        public void AdoptPassives(double[] values)
        {
            Pv = values;
            hasElemResistPassive = !double.IsNaN(values[169]) || !double.IsNaN(values[202])
                                || !double.IsNaN(values[248]) || !double.IsNaN(values[341]);
        }

        public void SetEnchants(int[] pieces)
        {
            Enchants = pieces;
            HasEnchants = true;
            bool nulli = false;
            for (int e = 120; e <= 128; e++) if (pieces[e] != 0) { nulli = true; break; }
            HasNullifyEnchant = nulli;
            bool ra = false;
            foreach (var list in F.RACE_ATTACK.Values)
            {
                foreach (var (e, _) in list) if (pieces[e] != 0) { ra = true; break; }
                if (ra) break;
            }
            if (!ra)
                foreach (var (e, _) in F.RACE_SPECIAL) if (pieces[e] != 0) { ra = true; break; }
            HasRaceAttackEnchant = ra;
            bool rg = false;
            foreach (var g in F.RACE_GUARD.Values)
                if (pieces[g.small] != 0 || pieces[g.large] != 0) { rg = true; break; }
            HasRaceGuardEnchant = rg;
        }

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
            int off = OffhandBonus != null ? OffhandBonus[name] : 0;
            if (statModCount == 0)
            {
                int r = b + off;
                return r <= 0 ? 0 : r > 9999 ? 9999 : r;
            }
            int total = b;
            var s = St[StatBuff[name]];
            if (s != null) total += PyMath.Int(b * s.Value);
            // 0x4fc140: 189 / 193 / 194 are mutually exclusive (first present wins).
            s = St[189];
            if (s != null) total += PyMath.Int(b * s.Value);
            else if ((s = St[193]) != null) total += PyMath.Int(b * s.Value);
            else if ((s = St[194]) != null) total += PyMath.Int(b * s.Value);
            if (St[TRUMP_CARD] != null)
            {
                if (name == ATK) total += PyMath.Int(Base[DEF] * St[TRUMP_CARD].Value);
                else if (name == DEF) total -= 10000;
            }
            if (St[120] != null)
            {
                // 0x4fc01d..0x4fc04c: Petrify adds Raw[DEF]/2 and subtracts Raw[AGI]/2.
                int rawStat = Raw != null ? Raw[name] : b;
                if (name == DEF) total += rawStat / 2;
                else if (name == AGI) total -= rawStat / 2;
            }
            // 0x4fc26f..0x4fc5c1: off-hand dual-wield weapon contribution is added after stat buffs, then clamped to [0, 9999].
            total += off;
            return total <= 0 ? 0 : total > 9999 ? 9999 : total;
        }

        public int MaxHp
        {
            get
            {
                int hp = MaxHpBase;
                if (StCount == 0) return hp;
                var s = St[MAX_HP_BUFF];
                // 0x4f7c29, 0x4fc089: effect 172 multiplies pre-enchant BaseHp (growth + crown), not post-enchant MaxHpBase.
                if (s != null) hp += PyMath.Int(BaseHp * s.Value);
                return hp;
            }
        }

        public int Resistance(int index)
        {
            if (SamsaraState == 2) return Samsara[index];
            // 0x4fc1b0..0x4fc1e4: Effect 192 (All Resistances 100) adds +10000 to all 8 resistances, clamping to +100.
            if (StCount != 0 && St[192] != null) return 100;
            int value = ResistBase[index];
            if (index >= 3)
            {
                if (StCount != 0 || hasElemResistPassive)
                {
                    // 0x4fc1e6: 202 and 341 are mutually exclusive (202 wins); 169 and 248 remain additive.
                    if (Has(169)) value += PyMath.Int(Value(169));
                    if (Has(202)) value += PyMath.Int(Value(202));
                    else if (Has(341)) value += PyMath.Int(Value(341));
                    if (Has(248)) value += PyMath.Int(Value(248));
                }
            }
            else if (StCount != 0)
            {
                // PHYSICAL_RESIST_BUFFS {185: 0, 184: 1, 186: 2}
                int e = index == 0 ? 185 : index == 1 ? 184 : 186;
                var s = St[e];
                if (s != null) value += PyMath.Int(s.Value);
            }
            // 0x4fc6c7..0x4fc751: clamp all 8 resistances to [-100, +100] before Samsara (416..423) overrides.
            return value < -100 ? -100 : value > 100 ? 100 : value;
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

        /// <summary>enchant_bonus: what the enchantments add to a character. Fills total[6], returns hp, tp, resist[8].
        /// ENCHANT_SHARE (0..23) scales naked baseStats; ENCHANT_LINE (222..225, 281) scales gearedStats (0x4f8bd0..0x4f8d8f).</summary>
        public static void EnchantBonus(Dictionary<int, int> enchants, int[] baseStats, int baseHp, int baseTp, bool front,
                                        int[] total, out int hpOut, out int tpOut, int[] resistOut, int[] gearedStats = null)
        {
            Array.Clear(total, 0, 6);
            int[] lineSource = gearedStats ?? baseStats;
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
                            total[stat] += share < 1 ? PyMath.Int(lineSource[stat] * share) : PyMath.Int(lineSource[stat] / share);
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
                                       Dictionary<int, int> items, int sealbook, int[] partyEnchants, Dictionary<int, int> forged,
                                       int? uniqueLevel = null, List<(int effect, double value, bool isInt)> passives = null)
        {
            int row = data.GrowthRowOf(classId, previous);
            int[] grown = data.Stats(row, level);
            var characterStats = new int[6];
            for (int s = 0; s < 6; s++) characterStats[s] = grown[s] + crownBonus;
            int hp = grown[6] + crownBonus, tp = grown[7] + crownBonus;
            var passiveValues = new double[GameData.MaxEffect];
            Array.Fill(passiveValues, double.NaN);
            bool[] passiveInt = null;
            if (passives != null)
            {
                // passive_values = dict(passives): a later entry of one effect replaces the earlier
                foreach (var (effect, value, isInt) in passives)
                {
                    passiveValues[effect] = value;
                    if (isInt) { if (passiveInt == null) passiveInt = new bool[GameData.MaxEffect]; passiveInt[effect] = true; }
                    else if (passiveInt != null) passiveInt[effect] = false;
                }
            }
            Piece mainWeapon = null;
            bool hasShield = false;
            foreach (var use in equipment)
            {
                var piece = data.Equipment[use.EquipId];
                if (use.Slot == 0 && piece.Category == 0) mainWeapon = piece;
                if (use.Slot == 1 && piece.Category == 1) hasShield = true;
            }
            if (skills != null)
            {
                foreach (var (skillId, lv) in skills)
                {
                    var skill = data.GetSkill("Passive", skillId);
                    // 0x4f4cca..0x4f4cd7: gate every passive by player->vtable+0x12c(PassiveSkillData+0x6c)
                    if (skill != null && Policy.WeaponAllows(mainWeapon, hasShield, skill))
                    {
                        foreach (var eff in skill.Effects)
                        {
                            int at = Math.Min(lv, eff.Values.Length) - 1;
                            double value = eff.Values[at];
                            bool valueInt = eff.IsInt[at];
                            // 0x4f9b72..0x4f9bf5: duplicate passive effect IDs overwrite the earlier slot (last wins).
                            passiveValues[eff.Id] = value;
                            if (valueInt) { if (passiveInt == null) passiveInt = new bool[GameData.MaxEffect]; passiveInt[eff.Id] = true; }
                            else if (passiveInt != null) passiveInt[eff.Id] = false;
                        }
                    }
                }
            }
            bool hasUnique = false;
            int uniqueEffect = 0;
            double uniqueValue = 0;
            bool offhandFilter = data.EnchantOffhand.Count > 0 || data.EnchantStacks.Count > 0;
            // an enchantment on any active piece (off-hand weapon requires bit 7, 0x4f636b), sealbook, grand sealbook or forge
            bool Carries(int enchant) => equipment.Any(u =>
                                         {
                                             var p = data.Equipment[u.EquipId];
                                             if (u.Slot == 1 && p.Category == 0 && offhandFilter && !data.EnchantOffhand.Contains(enchant)) return false;
                                             return p.Enchants.Contains(enchant);
                                         })
                                         || (sealbook != T.NONE && data.SealbookEnchants.TryGetValue(sealbook, out var own) && own.Contains(enchant))
                                         || (partyEnchants != null && partyEnchants.Contains(enchant))
                                         || (forged != null && forged.TryGetValue(enchant, out int count) && count > 0);
            int rank = uniqueLevel ?? UniqueRank(level, crownBonus);
            // enchantment 293 raises the rank of her own unique skill by one when it is 1 to 8 (0x4f716e - 0x4f7186)
            if (rank >= 1 && rank <= 8 && Carries(F.UNIQUE_RANK_ENCHANT)) rank += 1;
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
            // CGamePlayerStatusETCDoll (0x4f3586..0x4f35fc): inherits characterStats (including crownBonus), personal & grand sealbooks.
            var dollTotals = (int[])characterStats.Clone();
            int[] offhandBonus = null;
            var enchants = new Dictionary<int, int>();
            var dollEnchants = new Dictionary<int, int>();
            Piece weapon = null;
            double yearning = PV(YEARNING, 0.0);
            int yearningFloor = PyMath.Int(yearning);
            var modifiers = ModifierList(data, classId, previous);
            // enchantment 264 on any active piece, the sealbook, the grand sealbook or the forge adds 0.02 to the class weapon modifier
            // (once, not per piece: 0x4f7fb0 - 0x4f7fd9)
            double modifierUp = Carries(F.WEAPON_MODIFIER_ENCHANT) ? F.WEAPON_MODIFIER_UP : 0.0;
            var gains = new int[6];
            var dollGains = new int[6];
            foreach (var use in equipment)
            {
                var piece = data.Equipment[use.EquipId];
                int[] rawStats = PieceStats(piece, use.Upgrade);
                int[] stats = (int[])rawStats.Clone();
                bool isOffhandWeapon = use.Slot == 1 && piece.Category == 0;
                if (use.Slot == 0 && piece.Category == 0) weapon = piece;
                if (isOffhandWeapon)
                {
                    double share = PV(DUAL_WIELD, 0.0);
                    if (share != 0.0)
                    {
                        offhandBonus = offhandBonus ?? new int[6];
                        for (int s = 0; s < 6; s++) offhandBonus[s] += PyMath.Int(rawStats[s] * share);
                    }
                }
                else
                {
                    // 0x4f6530: Equipment Mastery (243 + 298) scales ATK and RES of every equipped piece except off-hand weapon.
                    stats[Unit.ATK] = stats[Unit.ATK] + PyMath.Int(stats[Unit.ATK] * mastery);
                    stats[Unit.RES] = stats[Unit.RES] + PyMath.Int(stats[Unit.RES] * mastery);
                    for (int s = 0; s < 6; s++) totals[s] += stats[s];
                    // CGamePlayerStatusETCDoll: copies all active pieces without passives (mastery=0, dualWield=0 -> slot 1 weapon skipped).
                    for (int s = 0; s < 6; s++) dollTotals[s] += rawStats[s];
                }
                foreach (int e in piece.Enchants)
                {
                    // 0x4f6334..0x4f638d: off-hand weapon enchantments only register if EnchantData 0x20 bit 7 (0x80) is set.
                    if (isOffhandWeapon && offhandFilter && !data.EnchantOffhand.Contains(e)) continue;
                    enchants.TryGetValue(e, out int c);
                    enchants[e] = c + 1;
                    dollEnchants.TryGetValue(e, out int dc);
                    dollEnchants[e] = dc + 1;
                }
                foreach (var entry in modifiers)
                {
                    bool matches = entry.Slot == use.Slot && (use.Slot != 0 || piece.Type == entry.Type)
                                   && (use.Slot != 1 || piece.Category == 1);
                    if (matches)
                    {
                        // 0x4f7fdf..0x4f8044: class modifiers use raw upgraded piece stats (before mastery) and floor each gain at int(yearning).
                        for (int s = 0; s < 6; s++)
                        {
                            if (rawStats[s] > 0)
                            {
                                gains[s] += Math.Max(yearningFloor, PyMath.Int((characterStats[s] + rawStats[s]) * (entry.Modifier + 0.01 * yearning + modifierUp)));
                                if (!isOffhandWeapon)
                                    dollGains[s] += Math.Max(0, PyMath.Int((characterStats[s] + rawStats[s]) * (entry.Modifier + modifierUp)));
                            }
                        }
                    }
                }
            }
            for (int s = 0; s < 6; s++) totals[s] += gains[s];
            for (int s = 0; s < 6; s++) dollTotals[s] += dollGains[s];
            if (sealbook != T.NONE && data.SealbookEnchants.TryGetValue(sealbook, out var sbe))
                foreach (int e in sbe)
                {
                    enchants.TryGetValue(e, out int c); enchants[e] = c + 1;
                    dollEnchants.TryGetValue(e, out int dc); dollEnchants[e] = dc + 1;
                }
            if (partyEnchants != null)
                foreach (int e in partyEnchants)
                {
                    enchants.TryGetValue(e, out int c); enchants[e] = c + 1;
                    dollEnchants.TryGetValue(e, out int dc); dollEnchants[e] = dc + 1;
                }
            if (forged != null)
                foreach (var kv in forged)
                {
                    enchants.TryGetValue(kv.Key, out int c); enchants[kv.Key] = c + kv.Value;
                    dollEnchants.TryGetValue(kv.Key, out int dc); dollEnchants[kv.Key] = dc + kv.Value;
                }
            var counted = new Dictionary<int, int>();
            foreach (var kv in enchants) counted[kv.Key] = data.EnchantStacks.Contains(kv.Key) ? kv.Value : Math.Min(kv.Value, 1);
            var dollCounted = new Dictionary<int, int>();
            foreach (var kv in dollEnchants) dollCounted[kv.Key] = data.EnchantStacks.Contains(kv.Key) ? kv.Value : Math.Min(kv.Value, 1);
            var bonusTotal = new int[6];
            var resistBonus = new int[8];
            // 0x4f8270 (Stage 4): EnchantBonus runs BEFORE Stage-5 Dual-Wield offhandBonus (0x4fbdd0), using totals only.
            EnchantBonus(counted, characterStats, hp, tp, front, bonusTotal, out int bonusHp, out int bonusTp, resistBonus, totals);
            for (int s = 0; s < 6; s++) totals[s] += bonusTotal[s];
            var dollBonusTotal = new int[6];
            var dollResistUnused = new int[8];
            EnchantBonus(dollCounted, characterStats, hp, tp, front, dollBonusTotal, out _, out _, dollResistUnused, dollTotals);
            for (int s = 0; s < 6; s++) dollTotals[s] += dollBonusTotal[s];
            int baseHpPreEnchant = hp;
            // 0x4fc62f: MaxHp and MaxTp are clamped to >= 1.
            hp = Math.Max(1, hp + bonusHp);
            tp = Math.Max(1, tp + bonusTp);
            var resist = new int[8];
            for (int i = 0; i < 8; i++) resist[i] = crownBonus + resistBonus[i];
            // 0x4f5556..0x4f55df: weapon rank, else enchant 263 -> Rank A (WeaponRanks[1]), else ClassData +0x24 unarmed rank.
            double rankDelay;
            if (weapon != null && weapon.Rank != T.NONE && weapon.Rank >= 0)
                rankDelay = data.WeaponRanks[weapon.Rank];
            else if (counted.ContainsKey(263) && data.WeaponRanks.TryGetValue(1, out double rankA))
                rankDelay = rankA;
            else if (data.ClassUnarmedRanks.TryGetValue(classId, out int unarmedRank) && data.WeaponRanks.TryGetValue(unarmedRank, out double classUnarmed))
                rankDelay = classUnarmed;
            else
                rankDelay = UnarmedDelay(data);
            int charRace = character != null ? character.Race : T.NONE;
            var unit = new Unit(name ?? (character != null ? character.Name : "class " + classId), Unit.PARTY, level, hp, tp, totals, resist,
                                rankDelay, weapon != null ? weapon.Swing : 0.0, charRace, Kind.Member);
            unit.BaseHp = baseHpPreEnchant;
            unit.OffhandBonus = offhandBonus;
            unit.AdoptPassives(passiveValues);
            unit.PvInt = passiveInt;
            unit.Raw = (int[])characterStats.Clone();
            unit.DollBase = dollTotals;
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
            bool shield = false, hasHead = false, hasBody = false;
            foreach (var use in equipment)
            {
                var p = data.Equipment[use.EquipId];
                if (use.Slot == 1 && p.Category == 1) shield = true;
                if (use.Slot == 2) hasHead = true;
                if (use.Slot == 3) hasBody = true;
            }
            unit.Shield = shield;
            unit.HasHead = hasHead;
            unit.HasBody = hasBody;
            unit.ClassId = classId;
            unit.PreviousClass = previous;
            unit.Front = front;
            if (items != null) unit.Items = new Dictionary<int, int>(items);
            unit.ClampPep();
            return unit;
        }

        public static double UnarmedDelay(GameData data) => data.WeaponRanks[5];

        static int FirstAttackAttr(GameData data, int[] attacks)
        {
            if (attacks != null && attacks.Length > 0)
            {
                var first = data.GetAttack(attacks[0]);
                if (first != null && first.Attr >= 1 && first.Attr <= 9) return first.Attr;
            }
            return T.NEUTRAL;
        }

        public static Unit BuildEnemy(GameData data, int enemyId, bool front, string name = null)
        {
            var e = data.Enemies[enemyId];
            var unit = new Unit(name ?? e.Name, Unit.ENEMIES, e.Level, e.Hp, 0, e.Stats, e.Resist, e.Weight, e.Swing, e.Race, Kind.Enemy);
            unit.ImmuneMask = e.ImmuneMask;
            unit.Attacks = e.Attacks;
            unit.AttackAttr = FirstAttackAttr(data, e.Attacks);
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

        /// <summary>measures/mercenaries.py build: a guest ally as a unit of the party side, with the stats, the attacks and the
        /// script of her record; the attack of her field 0x98 is taken as a passive when it is one.</summary>
        public static Unit BuildGuest(GameData data, NpcRec record)
        {
            double weight = data.WeaponRanks.TryGetValue(record.Rank, out var w) ? w : 2.0;
            // a guest ally has no HP and is never a target (0x43e6d0); the figure only keeps the unit standing
            var unit = new Unit(record.Name, Unit.PARTY, record.Level, 9999, 0, record.Stats, null, weight, 0.0, T.NONE, Kind.Summon);
            unit.IsGuest = true;
            unit.Attacks = record.Attacks;
            unit.AttackAttr = FirstAttackAttr(data, record.Attacks);
            unit.Script = record.Script;
            foreach (int id in record.Passives)
                if (data.Attacks.TryGetValue(id, out var extra) && extra.Passive)
                    for (int k = 0; k < extra.EffId.Length; k++) unit.SetPassive(extra.EffId[k], extra.EffValue[k], extra.EffIsInt[k]);
            return unit;
        }

        /// <summary>The stage the bar offers at a checkpoint: of the stages of the guest whose flag is open there (sheet MercenaryUnlocks),
        /// the one of the highest level (0x58adb0 - 0x58b060); null when none is open.</summary>
        public static NpcRec GuestStageAt(GameData data, Setup setup, string name, string cid)
        {
            int at = setup.Checkpoints.FindIndex(r => r.Str("ID") == cid);
            int Index(string id) => string.IsNullOrEmpty(id) ? -1 : setup.Checkpoints.FindIndex(r => r.Str("ID") == id);
            var open = new HashSet<int>();
            foreach (var r in setup.MercenaryUnlocks)
            {
                int from = Index(r.Str("From checkpoint")), until = Index(r.Str("Until checkpoint"));
                if (from >= 0 && at >= from && (until < 0 || at <= until)) open.Add(r.Int("Flag"));
            }
            NpcRec best = null;
            foreach (var r in data.Npcs)
                if (r.Name == name && open.Contains(r.UnlockFlag) && (best == null || r.Level > best.Level)) best = r;
            return best;
        }

        /// <summary>The record of the guest whose level is the highest not above the level, else her first (the model before 2026-10-17).</summary>
        public static NpcRec GuestStage(GameData data, string name, int level)
        {
            NpcRec under = null, first = null;
            var mine = new List<NpcRec>();
            foreach (var r in data.Npcs) if (r.Name == name) mine.Add(r);
            // sorted by level (stable)
            var sorted = new List<NpcRec>(mine);
            for (int i = 1; i < sorted.Count; i++)
            {
                var x = sorted[i];
                int j = i - 1;
                while (j >= 0 && sorted[j].Level > x.Level) { sorted[j + 1] = sorted[j]; j--; }
                sorted[j + 1] = x;
            }
            foreach (var r in sorted) { if (first == null) first = r; if (r.Level <= level) under = r; }
            if (first == null) throw new InvalidOperationException("no guest " + name);
            return under ?? first;
        }

        public static Unit BuildSummon(GameData data, SummonForm form, List<Unit> party, int hp, int[] partyEnchants = null)
        {
            data.Enemies.TryGetValue(form.Enemy, out var enemy);
            Dictionary<int, int> partyCounted = null;
            if (partyEnchants != null && partyEnchants.Length > 0)
            {
                partyCounted = new Dictionary<int, int>();
                foreach (int e in partyEnchants)
                {
                    partyCounted.TryGetValue(e, out int c);
                    partyCounted[e] = data.EnchantStacks.Contains(e) ? c + 1 : 1;
                }
            }
            var memberStats = new List<int[]>(party.Count);
            var tmpBonus = new int[6];
            var tmpResist = new int[8];
            foreach (var m in party)
            {
                if (m.Kind != Kind.Member) continue;
                var src = (int[])(m.Raw != null ? m.Raw : m.Base).Clone();
                // 0x4f7ac0: temporary naked party copies include Grand Sealbook stat enchantments before taking the party max.
                if (partyCounted != null)
                {
                    EnchantBonus(partyCounted, src, m.BaseHp, m.MaxTp, m.Front, tmpBonus, out _, out _, tmpResist, src);
                    for (int s = 0; s < 6; s++) src[s] += tmpBonus[s];
                }
                memberStats.Add(src);
            }
            var stats = new int[6];
            for (int s = 0; s < 6; s++)
            {
                int floor = enemy != null ? enemy.Stats[s] : 0;
                bool any = false;
                int best = 0;
                foreach (var src in memberStats)
                {
                    int v = src[s];
                    if (!any || v > best) { best = v; any = true; }
                }
                stats[s] = Math.Max(floor, PyMath.Int(PyMath.Single(best * form.Factors[s])));
            }
            double weight = data.WeaponRanks.TryGetValue(form.Rank, out var w) ? w : 2.0;
            var unit = new Unit(form.Name, Unit.PARTY, form.Level, hp, 0, stats, null, weight, 0.0, T.NONE, Kind.Summon);
            unit.Attacks = form.Attacks;
            unit.AttackAttr = FirstAttackAttr(data, form.Attacks);
            unit.Script = form.Script;
            // 0x50030b..0x500497: apply all passive_count (up to 5) passives on SummonData.
            var passives = form.Passives != null && form.Passives.Length > 0
                ? form.Passives
                : (form.Passive != T.NONE ? new[] { form.Passive } : Array.Empty<int>());
            foreach (int pid in passives)
                if (pid != T.NONE && data.Attacks.TryGetValue(pid, out var pa))
                    for (int k = 0; k < pa.EffId.Length; k++) unit.SetPassive(pa.EffId[k], pa.EffValue[k], pa.EffIsInt[k]);
            return unit;
        }

        public static Unit BuildDoll(Unit owner, DollRec doll, int level, GameData data)
        {
            int[] baseStats;
            if (owner.DollBase != null)
            {
                // CGamePlayerStatusETCDoll (0x4f3290 + 0x4f7c00): characterStats (with crown) + copied equipment + class mods + all enchants
                baseStats = (int[])owner.DollBase.Clone();
            }
            else if (owner.Kind == Kind.Member && data != null && owner.ClassId != T.NONE)
            {
                int row = data.GrowthRowOf(owner.ClassId, owner.PreviousClass);
                int[] grown = data.Stats(row, owner.Level);
                baseStats = new int[6];
                Array.Copy(grown, baseStats, 6);
            }
            else
            {
                baseStats = (int[])owner.Base.Clone();
            }
            // 0x4fdfd0: Soul Seal (314) applies only to the 6 puppets (effects 228..233), not Arrow or Genjimaru.
            bool isPuppet = doll.Effect >= 228 && doll.Effect <= 233;
            if (isPuppet && data != null && owner.Has(SOUL_SEAL) && owner.Sealbook != T.NONE && data.Enemies.ContainsKey(owner.Sealbook))
            {
                var sealed_ = data.Enemies[owner.Sealbook];
                for (int s = 0; s < 6; s++) baseStats[s] += PyMath.Int(sealed_.Stats[s] * owner.Value(SOUL_SEAL));
            }
            // All three doll vtables (0x6d4768, 0x6d4dd8, 0x6d434c) map weight slot +0xf4 to 0x4fd630 (fldz; ret => 0.0),
            // initialize MaxTP = 9999, copy owner's enchantments (0x4fd867 -> 0x4f3290), inherit owner Swing (M02.01b),
            // and copy the 12-command caster status whitelist 0x6cc7b8 ([41..46, 48, 189, 193, 194, 256, 286]).
            var unit = new Unit(doll.Name, owner.Side, owner.Level, DOLL_HP, 9999, baseStats, null, 0.0, owner.Swing, T.NONE, Kind.Doll);
            if (owner.HasEnchants) unit.SetEnchants((int[])owner.Enchants.Clone());
            int[] dollStatusWhitelist = { 41, 42, 43, 44, 45, 46, 48, 189, 193, 194, 256, 286 };
            for (int wi = 0; wi < dollStatusWhitelist.Length; wi++)
            {
                int cmd = dollStatusWhitelist[wi];
                var ost = owner.St[cmd];
                if (ost != null)
                    unit.SetStatus(new Status(ost.Effect, ost.Value, ost.Turns, ost.Source, ost.Skill, ost.Kind, ost.AttackId) { HasData = ost.HasData, Data = ost.Data, IsInt = ost.IsInt });
            }
            unit.Owner = owner;
            unit.Life = doll.Turns[level - 1];
            unit.Doll = doll;
            unit.DollLevel = level;
            unit.PuppetEffect = doll.Effect;
            unit.AttackRange = doll.Range == "short" ? T.SHORT : doll.Range == "mid" ? T.MID : doll.Range == "long" ? T.LONG : T.SHORT;
            unit.Front = owner.Front;
            return unit;
        }
    }
}
