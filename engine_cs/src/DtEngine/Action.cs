using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;

namespace DtEngine
{
    public enum AKind { Attack = 0, Skill = 1, Enemy = 2, Item = 3, Defend = 4, Wait = 5, Chant = 6 }

    /// <summary>What a unit does on its turn (sim.battle.Action). source: a Skill, an EnemyAttack, or neither.</summary>
    public sealed class Action
    {
        public const int PLAIN_HIT = 0, MAGIC_POWER = 1;
        public Unit Actor;
        public AKind Kind;
        public Skill Skill;
        public EnemyAttack Atk;
        public int Level;
        public Unit Target;
        public int Item = T.NONE;
        public Unit[] FixedTargets;
        public bool Chanting, Furious, Paid;

        // the effects at the level of the action: id, kind, value; the first of each id is what value() finds. The arrays are shared
        // between the actions that have the same effects (a skill at a level whose figures take nothing from the user, an enemy
        // attack, the plain attack of a unit): they are never changed once made.
        FxSet fx;

        /// <summary>The effects of a skill at a level, or of an attack, as arrays and a 512-bit presence mask (built once).</summary>
        public sealed class FxSet
        {
            public int Count;
            public int[] Id, Kind;
            public double[] Val;
            public bool[] IsInt;
            public ulong M0, M1, M2, M3, M4, M5, M6, M7;
            public bool IsPhysical, IsMagic, IsSpecial, HasRandomMove;
            public int HitRoll;
            public int MultiHitIndex = -1;

            [MethodImpl(MethodImplOptions.AggressiveInlining)]
            public bool HasBit(int effect)
            {
                if ((uint)effect >= 512u) return HasLinear(effect);
                ulong bit = 1UL << (effect & 63);
                switch (effect >> 6)
                {
                    case 0: return (M0 & bit) != 0;
                    case 1: return (M1 & bit) != 0;
                    case 2: return (M2 & bit) != 0;
                    case 3: return (M3 & bit) != 0;
                    case 4: return (M4 & bit) != 0;
                    case 5: return (M5 & bit) != 0;
                    case 6: return (M6 & bit) != 0;
                    default: return (M7 & bit) != 0;
                }
            }

            bool HasLinear(int effect)
            {
                for (int i = 0; i < Count; i++) if (Id[i] == effect) return true;
                return false;
            }

            public void FinalizeMask()
            {
                ulong m0 = 0, m1 = 0, m2 = 0, m3 = 0, m4 = 0, m5 = 0, m6 = 0, m7 = 0;
                for (int i = 0; i < Count; i++)
                {
                    int e = Id[i];
                    if ((uint)e < 512u)
                    {
                        ulong bit = 1UL << (e & 63);
                        switch (e >> 6)
                        {
                            case 0: m0 |= bit; break;
                            case 1: m1 |= bit; break;
                            case 2: m2 |= bit; break;
                            case 3: m3 |= bit; break;
                            case 4: m4 |= bit; break;
                            case 5: m5 |= bit; break;
                            case 6: m6 |= bit; break;
                            case 7: m7 |= bit; break;
                        }
                    }
                }
                M0 = m0; M1 = m1; M2 = m2; M3 = m3; M4 = m4; M5 = m5; M6 = m6; M7 = m7;
                IsPhysical = HasBit(PLAIN_HIT);
                IsMagic = !IsPhysical && HasBit(MAGIC_POWER);
                HitRoll = IsPhysical ? 1 : (HasBit(MAGIC_POWER) || HasBit(25)) ? 2 : 0;
                IsSpecial = HasBit(8) || HasBit(12) || HasBit(138) || HasBit(140) || HasBit(141) || HasBit(142) || HasBit(434) || HasBit(435);
                HasRandomMove = HasBit(152) || HasBit(153) || HasBit(154) || HasBit(155);
                // Matches Battle.MULTI_HIT order: 89, 90, 91, 92, 94, 95, 96, 97, 98, 99, 100
                MultiHitIndex = HasBit(89) ? 0 : HasBit(90) ? 1 : HasBit(91) ? 2 : HasBit(92) ? 3
                              : HasBit(94) ? 4 : HasBit(95) ? 5 : HasBit(96) ? 6 : HasBit(97) ? 7
                              : HasBit(98) ? 8 : HasBit(99) ? 9 : HasBit(100) ? 10 : -1;
            }
        }

        public Action(Unit actor, AKind kind, Skill skill = null, int level = 1, Unit target = null, int item = T.NONE, Unit[] fixedTargets = null)
        {
            Actor = actor; Kind = kind; Skill = skill; Level = level; Target = target; Item = item; FixedTargets = fixedTargets;
        }

        public Action(Unit actor, AKind kind, EnemyAttack atk, int level)
        {
            Actor = actor; Kind = kind; Atk = atk; Level = level;
        }

        /// <summary>Makes this object the action Action(actor, kind, skill, level) would be (to examine many options with one object).</summary>
        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public void Reset(Unit actor, AKind kind, Skill skill, int level)
        {
            Actor = actor; Kind = kind; Skill = skill; Atk = null; Level = level; Target = null; Item = T.NONE; FixedTargets = null;
            Chanting = false; Furious = false; Paid = false; fx = null;
        }

        public bool HasSource => Skill != null || Atk != null;
        public string SourceName => Skill != null ? Skill.Name : Atk != null ? Atk.Name : null;
        public int SourceId => Skill != null ? Skill.Id : Atk != null ? Atk.Id : T.NONE;

        static readonly int[] BonusNone = Array.Empty<int>();
        static readonly int[] Bonus278_353 = { 278, 353 };
        static readonly int[] Bonus278 = { 278 };

        static int[] ValueBonus(int e)
        {
            switch (e)
            {
                case 128: case 129: case 130: case 168: return Bonus278_353;
                case 272: case 273: return Bonus278;
                default: return BonusNone;
            }
        }

        static FxSet MakeSet(int capacity) => new FxSet { Id = new int[capacity], Kind = new int[capacity], Val = new double[capacity], IsInt = new bool[capacity] };

        static void AddTo(FxSet set, int id, int kind, double value, bool isInt)
        {
            if (set.Count == set.Id.Length)
            {
                int n = Math.Max(4, set.Count * 2);
                Array.Resize(ref set.Id, n); Array.Resize(ref set.Kind, n); Array.Resize(ref set.Val, n); Array.Resize(ref set.IsInt, n);
            }
            set.Id[set.Count] = id; set.Kind[set.Count] = kind; set.Val[set.Count] = value; set.IsInt[set.Count] = isInt;
            set.Count++;
        }

        FxSet SkillEffects()
        {
            var skill = Skill;
            // the effects of a skill depend on the user only through the bonus effects
            bool shareable = !skill.TakesFromUser;
            if (shareable)
            {
                var cache = skill.FxByLevel;
                if (cache != null && Level >= 1 && Level <= cache.Length && cache[Level - 1] != null) return cache[Level - 1];
            }
            var set = MakeSet(skill.Effects.Length);
            foreach (var e in skill.Effects)
            {
                double v = e.Values[Math.Min(Level, e.Values.Length) - 1];
                var bonus = ValueBonus(e.Id);
                var sum = new PySum();
                foreach (int b in bonus) sum.AddFloat(Actor.Passive(b, 0.0));
                // sum() of nothing is the int 0
                v = v + (bonus.Length == 0 ? 0.0 : sum.Result);
                AddTo(set, e.Id, e.Kind, v, bonus.Length == 0 && e.IsInt[Math.Min(Level, e.Values.Length) - 1]);
            }
            set.FinalizeMask();
            if (shareable && Level >= 1)
            {
                lock (skill)
                {
                    if (skill.FxByLevel == null || skill.FxByLevel.Length < Level) { var bigger = new FxSet[Math.Max(Level, skill.Levels)]; if (skill.FxByLevel != null) Array.Copy(skill.FxByLevel, bigger, skill.FxByLevel.Length); skill.FxByLevel = bigger; }
                    skill.FxByLevel[Level - 1] = set;
                }
            }
            return set;
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        FxSet GetFx()
        {
            var s = fx;
            return s != null ? s : Refresh();
        }

        FxSet Refresh()
        {
            FxSet set;
            if (Skill != null) set = SkillEffects();
            else if (Atk != null) set = Atk.Fx ?? (Atk.Fx = MakeAttackSet(Atk));
            else if (Kind == AKind.Attack) set = Actor.PlainEffects ?? (Actor.PlainEffects = MakePlainSet(Actor));
            else set = Empty;
            fx = set;
            return set;
        }

        static readonly FxSet Empty = MakeEmpty();
        static FxSet MakeEmpty() { var s = MakeSet(0); s.FinalizeMask(); return s; }

        static FxSet MakeAttackSet(EnemyAttack atk)
        {
            var set = MakeSet(atk.EffId.Length);
            for (int i = 0; i < atk.EffId.Length; i++) AddTo(set, atk.EffId[i], atk.EffKind[i], atk.EffValue[i], atk.EffIsInt[i]);
            set.FinalizeMask();
            return set;
        }

        static FxSet MakePlainSet(Unit actor)
        {
            var set = MakeSet(4);
            AddTo(set, PLAIN_HIT, 4, 1.0, false);
            if (actor.HasEnchants)
            {
                foreach (var (enchant, effect, value) in F.PLAIN_ATTACK_ENCHANTS)
                {
                    if (actor.Pieces(enchant) != 0)
                    {
                        bool present = false;
                        for (int i = 0; i < set.Count; i++) if (set.Id[i] == effect) { present = true; break; }
                        if (!present) AddTo(set, effect, 4, value, false);
                    }
                }
            }
            set.FinalizeMask();
            return set;
        }

        public int Count => GetFx().Count;
        public int EffId(int i) => fx.Id[i];
        public bool EffIsInt(int i) => fx.IsInt[i];

        /// <summary>Whether the first effect of that id carries a whole number written as an int.</summary>
        public bool ValIsInt(int effect)
        {
            var s = GetFx();
            if (!s.HasBit(effect)) return false;
            int n = s.Count; var ids = s.Id;
            for (int i = 0; i < n; i++) if (ids[i] == effect) return s.IsInt[i];
            return false;
        }
        public int EffKind(int i) => fx.Kind[i];
        public double EffVal(int i) => fx.Val[i];

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public bool Has(int effect) => GetFx().HasBit(effect);

        /// <summary>value(effect, default): the first effect of that id.</summary>
        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public double Val(int effect, double dflt)
        {
            var s = GetFx();
            if (!s.HasBit(effect)) return dflt;
            int n = s.Count; var ids = s.Id;
            for (int i = 0; i < n; i++) if (ids[i] == effect) return s.Val[i];
            return dflt;
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public bool TryVal(int effect, out double value)
        {
            var s = GetFx();
            if (!s.HasBit(effect)) { value = 0; return false; }
            int n = s.Count; var ids = s.Id;
            for (int i = 0; i < n; i++) if (ids[i] == effect) { value = s.Val[i]; return true; }
            value = 0;
            return false;
        }

        public int TargetCode
        {
            get
            {
                if (Skill == null && Atk == null) return Kind == AKind.Attack ? T.SINGLE : T.SELF;
                return Skill != null ? Skill.Target : Atk.Target;
            }
        }

        static int WeaponElement(int e)
        {
            switch (e) { case 325: return 4; case 326: return 5; case 327: return 8; case 328: return 6; default: return 7; }
        }

        static int EnchantElement(int e)
        {
            switch (e) { case 78: return 4; case 79: return 5; case 80: return 6; case 81: return 7; default: return 8; }
        }

        int WeaponAttrWithOverrides()
        {
            // 0x4161e1..0x416275: weapon-element statuses (325..329) and weapon-element enchants (78..82) apply to both plain attacks and weapon-attribute skills.
            if (Actor.StCount > 0)
            {
                int count = 0, element = 0;
                for (int e = 325; e <= 329; e++)
                    if (Actor.St[e] != null) { count++; element = WeaponElement(e); }
                if (count == 1) return element;
            }
            if (Actor.HasEnchants)
            {
                int count = 0, element = 0;
                for (int e = 78; e <= 82; e++)
                    if (Actor.Pieces(e) != 0) { count++; element = EnchantElement(e); }
                if (count == 1) return element;
            }
            return Actor.AttackAttr;
        }

        public int Attr
        {
            get
            {
                if (Skill == null && Atk == null) return WeaponAttrWithOverrides();
                int a = Skill != null ? Skill.Attr : Atk.Attr;
                if (a == T.NONE || a == -1 || a == T.WEAPON_ATTR) return WeaponAttrWithOverrides();
                return a;
            }
        }

        public bool Physical => GetFx().IsPhysical;
        public bool Magic => GetFx().IsMagic;
        public bool IsSpecial => GetFx().IsSpecial;
        public bool HasRandomMove => GetFx().HasRandomMove;
        public int MultiHitIndex => GetFx().MultiHitIndex;

        /// <summary>0 none, 1 physical, 2 magic</summary>
        public int HitRoll => GetFx().HitRoll;

        public bool Spell => (Skill != null && Skill.IsMagic) || (Atk != null && Atk.Spell);

        public int Reach
        {
            get
            {
                if (Skill == null && Atk == null) return Actor.AttackRange;
                if (Skill != null)
                {
                    var s = Skill;
                    if (s.IsMagic) return T.NO_RANGE;
                    if (s.Range == T.SHORT && s.Weapons.Length > 0 && Actor.Weapon != null)
                    {
                        bool zero = false;
                        foreach (int w in s.Weapons) if (w == 0) zero = true;
                        return zero ? (Actor.AttackRange >= 0 ? Math.Min(Actor.AttackRange, T.SHORT) : T.SHORT) : s.Range;
                    }
                    return s.Range != T.NONE ? s.Range : Actor.AttackRange;
                }
                return Atk.Range != T.NONE ? Atk.Range : T.NO_RANGE;
            }
        }

        public int TpCost
        {
            get
            {
                if (Skill != null) return Skill.Tp[Math.Min(Level, Skill.Tp.Length) - 1];
                return 0;
            }
        }

        public double Speed
        {
            get
            {
                if (Skill != null) return Skill.Speed[Math.Min(Level, Skill.Speed.Length) - 1];
                if (Atk != null) return Atk.Speed != 0 ? Atk.Speed : 1.0;
                return 1.0;
            }
        }

        /// <summary>chant_speed: null when the action is not chanted.</summary>
        public double? ChantSpeed
        {
            get
            {
                if (Skill != null && Skill.Chanted) return Skill.Cast[Math.Min(Level, Skill.Cast.Length) - 1];
                if (Atk != null && Atk.Chanted) return Atk.ChantSpeed;
                return null;
            }
        }

        public double Turns
        {
            get
            {
                if (Skill != null) return Skill.Turns[Math.Min(Level, Skill.Turns.Length) - 1];
                if (Atk != null) return Atk.Turns;
                return 0;
            }
        }

        public override string ToString() => Actor.Name + " " + Kind + " " + SourceName + " L" + Level;
    }
}
