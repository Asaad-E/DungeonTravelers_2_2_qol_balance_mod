using System;
using System.Collections.Generic;

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
        public bool Chanting, Furious;

        // the effects at the level of the action: id, kind, value; the first of each id is what value() finds. The arrays are shared
        // between the actions that have the same effects (a skill at a level whose figures take nothing from the user, an enemy
        // attack, the plain attack of a unit): they are never changed once made.
        int fxCount = -1;
        int[] fxId, fxKind;
        double[] fxVal;
        bool[] fxInt;

        /// <summary>The effects of a skill at a level, or of an attack, as arrays (built once).</summary>
        public sealed class FxSet
        {
            public int Count;
            public int[] Id, Kind;
            public double[] Val;
            public bool[] IsInt;
        }

        // expected damage on each target, worked out once per action (a policy asks for it many times in one decision, and
        // nothing changes between the questions)


        public Action(Unit actor, AKind kind, Skill skill = null, int level = 1, Unit target = null, int item = T.NONE, Unit[] fixedTargets = null)
        {
            Actor = actor; Kind = kind; Skill = skill; Level = level; Target = target; Item = item; FixedTargets = fixedTargets;
        }

        public Action(Unit actor, AKind kind, EnemyAttack atk, int level)
        {
            Actor = actor; Kind = kind; Atk = atk; Level = level;
        }

        /// <summary>Makes this object the action Action(actor, kind, skill, level) would be (to examine many options with one object).</summary>
        public void Reset(Unit actor, AKind kind, Skill skill, int level)
        {
            Actor = actor; Kind = kind; Skill = skill; Atk = null; Level = level; Target = null; Item = T.NONE; FixedTargets = null;
            Chanting = false; Furious = false; fxCount = -1;
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

        void Refresh()
        {
            FxSet set;
            if (Skill != null) set = SkillEffects();
            else if (Atk != null) set = Atk.Fx ?? (Atk.Fx = MakeAttackSet(Atk));
            else if (Kind == AKind.Attack) set = Actor.PlainEffects ?? (Actor.PlainEffects = MakePlainSet(Actor));
            else set = Empty;
            fxId = set.Id; fxKind = set.Kind; fxVal = set.Val; fxInt = set.IsInt; fxCount = set.Count;
        }

        static readonly FxSet Empty = MakeSet(0);

        static FxSet MakeAttackSet(EnemyAttack atk)
        {
            var set = MakeSet(atk.EffId.Length);
            for (int i = 0; i < atk.EffId.Length; i++) AddTo(set, atk.EffId[i], atk.EffKind[i], atk.EffValue[i], atk.EffIsInt[i]);
            return set;
        }

        static FxSet MakePlainSet(Unit actor)
        {
            var set = MakeSet(4);
            AddTo(set, PLAIN_HIT, 4, 1.0, false);
            foreach (var (enchant, effect, value) in F.PLAIN_ATTACK_ENCHANTS)
            {
                if (actor.Pieces(enchant) != 0)
                {
                    bool present = false;
                    for (int i = 0; i < set.Count; i++) if (set.Id[i] == effect) { present = true; break; }
                    if (!present) AddTo(set, effect, 4, value, false);
                }
            }
            return set;
        }

        public int Count { get { if (fxCount < 0) Refresh(); return fxCount; } }
        public int EffId(int i) => fxId[i];
        public bool EffIsInt(int i) => fxInt[i];

        /// <summary>Whether the first effect of that id carries a whole number written as an int.</summary>
        public bool ValIsInt(int effect)
        {
            if (fxCount < 0) Refresh();
            for (int i = 0; i < fxCount; i++) if (fxId[i] == effect) return fxInt[i];
            return false;
        }
        public int EffKind(int i) => fxKind[i];
        public double EffVal(int i) => fxVal[i];

        public bool Has(int effect)
        {
            if (fxCount < 0) Refresh();
            for (int i = 0; i < fxCount; i++) if (fxId[i] == effect) return true;
            return false;
        }

        /// <summary>value(effect, default): the first effect of that id.</summary>
        public double Val(int effect, double dflt)
        {
            if (fxCount < 0) Refresh();
            for (int i = 0; i < fxCount; i++) if (fxId[i] == effect) return fxVal[i];
            return dflt;
        }

        public bool TryVal(int effect, out double value)
        {
            if (fxCount < 0) Refresh();
            for (int i = 0; i < fxCount; i++) if (fxId[i] == effect) { value = fxVal[i]; return true; }
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

        public int Attr
        {
            get
            {
                if (Skill == null && Atk == null)
                {
                    int count = 0, element = 0;
                    for (int e = 325; e <= 329; e++)
                        if (Actor.St[e] != null) { count++; element = WeaponElement(e); }
                    if (count == 1) return element;
                    return Actor.AttackAttr;
                }
                int a = Skill != null ? Skill.Attr : Atk.Attr;
                if (a == T.NONE || a == -1 || a == T.WEAPON_ATTR) return Actor.AttackAttr;
                return a;
            }
        }

        public bool Physical => Has(PLAIN_HIT);
        public bool Magic => !Has(PLAIN_HIT) && Has(MAGIC_POWER);

        /// <summary>0 none, 1 physical, 2 magic</summary>
        public int HitRoll
        {
            get
            {
                if (Has(PLAIN_HIT)) return 1;
                if (Has(MAGIC_POWER) || Has(25)) return 2;
                return 0;
            }
        }

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
                        return zero ? Math.Min(Actor.AttackRange, T.SHORT) : s.Range;
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
