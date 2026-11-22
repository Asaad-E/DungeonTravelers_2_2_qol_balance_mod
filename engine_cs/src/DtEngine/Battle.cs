using System;
using System.Collections.Generic;

namespace DtEngine
{
    /// <summary>The settings a battle reads (the dict `options` of sim.scenario.play).</summary>
    public sealed class BattleOptions
    {
        /// <summary>The same options with RandomBattle off (the boss at the end of a walk of random battles).</summary>
        public BattleOptions NotRandom() { var o = (BattleOptions)MemberwiseClone(); o.RandomBattle = false; return o; }
        public bool RandomBattle;
        public bool HalveEnemies = true;
        public int DollCureTargets = 2;
        public bool Boss;
        public double MaxTime = 400.0;
        // flags of the data that a job sets for its own battles (null: those of the data)
        public bool? SurvivalGuard, InterruptProduct, ThirdEyeDispel;
        public int? PositiveTranceThreshold;
        public bool HasArcaneChance;
        public int ArcaneChance = T.NONE;
        public bool Record;                 // keep the recorder of the battle (sim.battle.Recorder)
    }

    /// <summary>The zone of the cell a fixed battle is fought on.</summary>
    public sealed class Zone
    {
        public int[] Slots = Array.Empty<int>();
        public ZoneFactors Factors;       // null: an empty dict (every factor 1.0)
        public bool NoMagic;
        public Zone Clone() => (Zone)MemberwiseClone();
    }

    /// <summary>Observer of a battle for the traces.</summary>
    public interface IBattleTrace
    {
        void Begin(Battle b);
        void Started(Battle b);
        void TurnStart(Battle b, Unit u);
        void TurnEnd(Battle b, Unit u);
        void Ended(Battle b, BattleResult r);
        void Perform(Battle b, Action a);
        void Hit(Battle b, Action a, Unit target, bool landed);
        void Damage(Battle b, Action a, Unit target, int amount);
        void Restore(Battle b, Unit u, int gained);
        void LoseHp(Battle b, Unit u, int amount);
        void Counter(Battle b, Unit unit, Unit attacker);
    }

    public sealed class BattleResult
    {
        public bool Won, Lost;
        public double Time;
        public int Actions;
        public double LowestHp;
        public int EnemyDamage, EnemyActions, PartyMaxHp;
        public double HpLeft, TpLeft;
        public int Alive;
        public Recorder Record;             // null unless the options ask for it
        public List<Unit> RecordUnits;      // the units of the battle (the record names them by position)
    }

    public sealed class Battle
    {
        // --- what the effects are -----------------------------------------------------------------------
        public const int PLAIN_HIT = 0, MAGIC_POWER = 1;
        const double POISON_SHARE = 0.05;
        const int POISON_CAP = 250;
        const int TRANQUIL_TURNS = 4;
        const int START_GAUGE = 500, RANDOM_ORDER = 20;
        static readonly int[] AMBUSH_CHANCE = { 6, 4 };
        public static readonly int[] AILMENT_IDS = { 113, 114, 115, 116, 117, 118, 119, 120, 122, 123 };
        static readonly bool[] IsAilment = MakeAilmentFlags();
        static readonly string[] AilmentName = MakeAilmentNames();
        static readonly int[] AilmentResist = MakeAilmentResist();
        public static readonly int[] CURE_ORDER = { 113, 115, 117, 114, 116, 120, 122 };
        static readonly int[] ESARHADDON_ORDER = { 113, 115, 117, 114, 116, 122 };
        public static readonly int[] RANDOM_MOVES = { 152, 153, 154, 155 };
        public const int ITEM_CURE_ONE = 6, ITEM_CURE_ALL = 7, CURE_ALL = 8;
        static readonly int[] SPEED_BUFFS = { 168, 217, 221 };
        static readonly int[] CHANT_SPEED_BUFFS = { 214, 265, 281 };
        static readonly int[] CRIT_TERMS = { 31, 174, 211 };
        static readonly int[] ACCURACY_BUFFS = { 166, 197, 337 }, EVASION_BUFFS = { 164, 198, 338 };
        static readonly int[] MAGIC_ACCURACY_BUFFS = { 167, 309, 197, 222, 337 }, MAGIC_EVASION_BUFFS = { 165, 198, 338 };
        static readonly int[] MAGIC_DEFENCE_MODIFIERS = { 163, 196, 205, 336, 213, 220, 223 };
        static readonly int[] DEFENCE_MODIFIERS = { 28, 162, 187, 196, 205, 336, 219 };
        static readonly int[] ATTACK_STATUS_MODIFIERS = { 161, 195, 335, 219 };
        const int LULLABY = 205;
        static readonly int[] LULLABY_ACCURACY = { 278, 353 };
        static readonly int[] MAGIC_HIT_DIVISORS = { 220, 223 };
        const int STAB_EVASION = 253;
        public const int SACRIFICE = 77, MAX_HP_DRAIN = 133, EXTRA_TARGETS = 137;
        const int SAMSARA_STEP = 50;
        const int MURDER = 258, DARK_QUEST = 263, KNOCK_DOWN = 305, PRETEND = 310, MURDER_LICENSE = 319, MURDER_LICENSE_ATTACK = 413, DEMON_WALL = 356, ENEMIES_FLEE = 432, ESCAPE_SELF = 11;
        const int DARK_AURA_TURNS = 4, ECSTASY_TURNS = 3;
        const int SLOW_TARGET_RECOVERY = 5, SLOW_TARGET_TURNS = 5, SUGAR_COMA_RECOVERY = 5, SUGAR_COMA_TURNS = 3;
        const int SPECIAL_SLEEP_EFFECT = 143, SPECIAL_SLEEP_START = 5;
        const double SPECIAL_SLEEP_VALUE = 10.0;
        const int MATERIAL_GUARD = 179;
        const int GENJIMARU = 427, GENJIMARU_ACTION = 107, GENJIMARU_LIFE = 3;
        const int ARCANE_CHANCE = 15;
        const int SHADOW_ATTACK = 2, SHADOW_LIFE = 3;
        const double DOLL_MAGIC_SCALE = 500.0;
        // Exact 0x47b220 CCommand vtable flags: +0x6c (Song) = 210..223, +0x70 (Dance) = 195..205, +0x78 (Geass) = 335..341.
        static readonly int[] SONG_EFFECTS = { 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223 };
        static readonly int[] DANCE_EFFECTS = { 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205 };
        static readonly int[] GEASS_EFFECTS = { 335, 336, 337, 338, 339, 340, 341 };
        static readonly bool[] IsSongEffect = Flags(SONG_EFFECTS), IsDanceEffect = Flags(DANCE_EFFECTS), IsGeassEffect = Flags(GEASS_EFFECTS);
        static readonly bool[] StatusEffect = MakeStatusEffects();
        static readonly bool[] DispelAlways = Flags(new[] { 27, 171, 325, 326, 327, 328, 329, 101, 102, 181, 189, 191, 193, 194 });
        static readonly bool[] DispelIfRaised = Flags(new[] { 21, 26, 28, 31, 41, 42, 43, 44, 45, 46, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173, 174, 184, 185, 186 });
        // Exact CCommand vtable+0x54 (IsBuff) and vtable+0x5c (IsDebuff) classification (0x433b80, 0x481b12).
        static readonly bool[] SignedBuffDebuff = Flags(new[] { 21, 26, 28, 31, 41, 42, 43, 44, 45, 46, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173, 174, 184, 185, 186 });
        static readonly bool[] AlwaysBuffStatus = Flags(new[] { 27, 171, 325, 326, 327, 328, 329 });
        // Exact 22 stat buff/debuff effects counted by Effect 71 (Pursuit Stab / Stab Smash / Drill Lance Attack; 0x44c640..0x44c663).
        static readonly bool[] StatEffect71 = Flags(new[] { 41, 42, 43, 44, 45, 46, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173, 174, 184, 185, 186, 189 });

        // MULTI_HIT: effect -> (base, picks, weights, rondo weights), in the order of the dict
        static readonly (int effect, int baseHits, int[] picks, double[] weights, double[] rondo)[] MULTI_HIT =
        {
            (89, 2, new[] { 0, 1, 2, 3 }, new double[] { 25, 25, 25, 25 }, new double[] { 15, 20, 35, 30 }),
            (90, 3, new[] { 0 }, new double[] { 1 }, new double[] { 1 }),
            (91, 8, new[] { 0 }, new double[] { 1 }, new double[] { 1 }),
            (92, 2, new[] { 0, 1, 2 }, new double[] { 15, 50, 35 }, new double[] { 0, 50, 50 }),
            (94, 0, new[] { 0, 1, 2, 3, 4 }, new double[] { 10, 15, 30, 25, 20 }, new double[] { 0, 15, 25, 30, 30 }),
            (95, 1, new[] { 0, 1, 2, 3, 4 }, new double[] { 10, 15, 30, 25, 20 }, new double[] { 0, 15, 30, 25, 30 }),
            (96, 3, new[] { 0, 1, 2 }, new double[] { 20, 50, 30 }, new double[] { 0, 50, 50 }),
            (97, 2, new[] { 0 }, new double[] { 1 }, new double[] { 1 }),
            (98, 7, new[] { 0 }, new double[] { 1 }, new double[] { 1 }),
            (99, 1, new[] { 0, 1, 2 }, new double[] { 20, 50, 30 }, new double[] { 0, 50, 50 }),
            (100, 4, new[] { 0, 1, 2, 3 }, new double[] { 20, 20, 30, 30 }, new double[] { 0, 20, 30, 50 }),
        };

        static readonly double[] MultiHitMeanNormal = BuildMultiHitMeans(false);
        static readonly double[] MultiHitMeanRondo = BuildMultiHitMeans(true);
        static readonly double[] MultiHitWeightSum = BuildMultiHitWeightSums(false);
        static readonly double[] MultiHitRondoSum = BuildMultiHitWeightSums(true);
        static readonly int[] NullifyEnchantOfAilment = BuildNullifyEnchantTable();

        static double[] BuildMultiHitMeans(bool rondo)
        {
            var r = new double[MULTI_HIT.Length];
            for (int m = 0; m < MULTI_HIT.Length; m++)
            {
                var entry = MULTI_HIT[m];
                var table = rondo ? entry.rondo : entry.weights;
                var s = new PySum();
                for (int i = 0; i < table.Length; i++) s.AddFloat(entry.picks[i] * table[i]);
                var t = new PySum();
                foreach (var w in table) t.AddFloat(w);
                r[m] = entry.baseHits + s.Result / t.Result;
            }
            return r;
        }

        static double[] BuildMultiHitWeightSums(bool rondo)
        {
            var r = new double[MULTI_HIT.Length];
            for (int m = 0; m < MULTI_HIT.Length; m++)
            {
                var table = rondo ? MULTI_HIT[m].rondo : MULTI_HIT[m].weights;
                var s = new PySum();
                foreach (var w in table) s.AddFloat(w);
                r[m] = s.Result;
            }
            return r;
        }

        static int[] BuildNullifyEnchantTable()
        {
            var a = new int[GameData.MaxEffect];
            Array.Fill(a, -1);
            foreach (var (e, ail) in F.ENCHANT_NULLIFY_AILMENT) a[ail] = e;
            return a;
        }

        [Flags]
        enum PerfParts { None = 0, Chant = 1, Song = 2, Dance = 4, Doll = 8, Geass = 16, All = Chant | Song | Dance | Doll | Geass }

        static bool[] Flags(int[] ids)
        {
            var a = new bool[GameData.MaxEffect];
            foreach (int i in ids) a[i] = true;
            return a;
        }

        static bool[] MakeAilmentFlags() => Flags(AILMENT_IDS);

        static string[] MakeAilmentNames()
        {
            var a = new string[GameData.MaxEffect];
            a[113] = "poison"; a[114] = "freeze"; a[115] = "paralysis"; a[116] = "sleep"; a[117] = "silence"; a[118] = "stun";
            a[119] = "instant death"; a[120] = "petrification"; a[122] = "slow"; a[123] = "shadow sew";
            return a;
        }

        static int[] MakeAilmentResist()
        {
            var a = new int[GameData.MaxEffect];
            Array.Fill(a, T.NONE);
            a[113] = 4; a[114] = 4; a[115] = 7; a[116] = 5; a[117] = 5; a[118] = 3; a[119] = 6; a[120] = 6; a[122] = 6;
            return a;
        }

        static bool[] MakeStatusEffects()
        {
            // STATUS_EFFECTS = set(STAT_STATUSES) | {...}
            int[] stat = { 41, 42, 43, 44, 45, 46, 189, 193, 194, 48, 172, 169, 184, 185, 186, 202, 248, 341 };
            int[] more = { 161, 162, 163, 164, 165, 166, 167, 168, 171, 183, 187, 188, 191, 101, 102, 180, 246, 247, 285, 301, 190, 264, 27, 173 };
            var a = Flags(stat);
            foreach (int i in more) a[i] = true;
            return a;
        }

        public static bool IsAilmentId(int e) => e >= 0 && e < IsAilment.Length && IsAilment[e];
        public static bool IsTrueAilmentId(int e) => e >= 0 && e < IsAilment.Length && IsAilment[e] && e != 123;
        public static bool IsBuffStatus(Status s)
        {
            if (s == null) return false;
            int e = s.Effect;
            if ((uint)e >= GameData.MaxEffect) return false;
            if (SignedBuffDebuff[e]) return s.Value >= 0;
            if (e == 32) return s.Value < 0;
            return AlwaysBuffStatus[e];
        }
        public static bool IsDebuffStatus(Status s)
        {
            if (s == null) return false;
            int e = s.Effect;
            if ((uint)e >= GameData.MaxEffect) return false;
            if (SignedBuffDebuff[e]) return s.Value < 0;
            if (e == 32) return s.Value >= 0;
            return e == 30;
        }
        public static string AilmentNameOf(int e) => AilmentName[e];
        public static int AilmentResistOf(int e) => AilmentResist[e];
        public static bool IsSong(int e) => IsSongEffect[e];
        public static bool IsDance(int e) => IsDanceEffect[e];

        /// <summary>Per-thread reusable buffers shared across sequential battles on the same worker thread.</summary>
        sealed class ThreadScratch
        {
            public bool InUse;
            public int[] RecDamage = new int[64], RecActions = new int[64];
            public Action[] LastAction = new Action[64];
            public bool[] Reprisal = new bool[64];
            public int[] ArcaneDamage = new int[64];
            public readonly HashSet<(Unit, int)> Spent = new HashSet<(Unit, int)>();
            public readonly List<(Unit unit, int count)> Covered = new List<(Unit, int)>(8);
            public readonly List<Unit> Guarding = new List<Unit>(8);
            public readonly Action ScratchAction = new Action(null, AKind.Attack);
            public readonly List<Unit> PolicyScratch = new List<Unit>(8);
            public readonly List<Unit> RedirectScratch = new List<Unit>(8);
            public readonly List<Unit> DelayOrderScratch = new List<Unit>(16);
            public readonly int[] StatusScratch = new int[GameData.MaxEffect];
            public readonly int[] DispelRemoveScratch = new int[GameData.MaxEffect];
            public readonly int[] TickScratch = new int[GameData.MaxEffect];
            public Skill[] CandidateSkills = new Skill[32];
            public int[] CandidateLevels = new int[32];
            public OptionEntry[] OptionCache = new OptionEntry[16];
            public Unit[] PickOrdered = new Unit[16];
            public int[] PickWeights = new int[16];
        }

        [ThreadStatic] static ThreadScratch threadScratch;
        readonly ThreadScratch scratch;
        bool scratchRented;

        // --- state -----------------------------------------------------------------------------------------
        public GameData Data;
        public PyRandom Rng;
        public List<Unit> Units;
        public Policy ChooseMember;
        public BattleOptions Options;
        public Zone ZoneInfo;
        public double Time;
        public double MaxTime;
        public int MaxActions = 3000;
        public int Actions;
        public bool Fixed;
        public double LowestHp;
        public IBattleTrace Trace;
        readonly HashSet<(Unit, int)> spent;
        // Recorder, by position
        public int[] RecDamage, RecActions;
        Action[] lastAction;
        bool[] reprisal;
        bool reprisalDirty;
        int[] arcaneDamage;
        bool arcaneDirty;
        bool inCounter;
        Unit deferredCounter;
        bool abortHits;
        int lastDealtDamage;
        bool lastEndured;
        // the full recorder (null when nobody asks for it)
        public Recorder Rec;
        Dictionary<Unit, int> damageByTarget;
        // Cover: units with Cover that took a hit in place of another, in the order they did
        readonly List<(Unit unit, int count)> covered;
        readonly List<Unit> guarding;
        // the "mean" mode of the policies: the random term of the wait is the mean of the six values
        public bool MeanWait;
        int activeDolls;
        bool anyDemonWall;
        int initialPartyCount;

        public Battle(GameData data, List<Unit> party, List<Unit> enemies, PyRandom rng, Policy choose, BattleOptions options, Zone zone,
                      double maxTime = 400.0)
        {
            var ts = threadScratch ?? (threadScratch = new ThreadScratch());
            if (!ts.InUse) { ts.InUse = true; scratch = ts; scratchRented = true; }
            else scratch = new ThreadScratch();

            spent = scratch.Spent; spent.Clear();
            covered = scratch.Covered; covered.Clear();
            guarding = scratch.Guarding; guarding.Clear();
            ScratchAction = scratch.ScratchAction;
            PolicyScratch = scratch.PolicyScratch; PolicyScratch.Clear();
            redirectScratch = scratch.RedirectScratch; redirectScratch.Clear();
            delayOrderScratch = scratch.DelayOrderScratch; delayOrderScratch.Clear();
            statusScratch = scratch.StatusScratch;
            dispelRemoveScratch = scratch.DispelRemoveScratch;
            tickScratch = scratch.TickScratch;
            CandidateSkills = scratch.CandidateSkills;
            CandidateLevels = scratch.CandidateLevels;
            OptionCache = scratch.OptionCache;
            pickOrdered = scratch.PickOrdered;
            pickWeights = scratch.PickWeights;
            RecDamage = scratch.RecDamage;
            RecActions = scratch.RecActions;
            lastAction = scratch.LastAction;
            reprisal = scratch.Reprisal;
            arcaneDamage = scratch.ArcaneDamage;

            Data = data; Rng = rng;
            Units = new List<Unit>(party.Count + enemies.Count + 16);
            Units.AddRange(party);
            Units.AddRange(enemies);
            Grow(Units.Count + 15);
            Array.Clear(RecDamage, 0, Units.Count);
            Array.Clear(RecActions, 0, Units.Count);
            Array.Clear(lastAction, 0, Units.Count);
            Array.Clear(reprisal, 0, Units.Count);
            Array.Clear(arcaneDamage, 0, Units.Count);
            int ocClear = Math.Min(OptionCache.Length, Units.Count);
            for (int k = 0; k < ocClear; k++) OptionCache[k].Owner = null;
            for (int k = 0; k < Units.Count; k++)
            {
                var u = Units[k];
                u.Position = k; u.Roster = roster;
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member) initialPartyCount++;
                if (u.Kind == Kind.Doll && u.Alive) activeDolls++;
                if (u.Has(DEMON_WALL)) anyDemonWall = true;
            }
            roster.Version++;
            ChooseMember = choose;
            Options = options ?? new BattleOptions();
            ZoneInfo = zone;
            MaxTime = maxTime;
            if (Options.Record) Rec = new Recorder();
        }

        void ReleaseScratch()
        {
            if (!scratchRented) return;
            scratchRented = false;
            int n = Units.Count;
            Array.Clear(lastAction, 0, Math.Min(n, lastAction.Length));
            int ocClear = Math.Min(n, OptionCache.Length);
            for (int k = 0; k < ocClear; k++) { OptionCache[k].Owner = null; OptionCache[k].List?.Clear(); }
            Array.Clear(pickOrdered, 0, pickOrdered.Length);
            Array.Clear(CandidateSkills, 0, CandidateSkills.Length);
            ScratchAction.Reset(null, AKind.Attack, null, 1);
            spent.Clear();
            covered.Clear();
            guarding.Clear();
            PolicyScratch.Clear();
            redirectScratch.Clear();
            delayOrderScratch.Clear();
            scratch.RecDamage = RecDamage;
            scratch.RecActions = RecActions;
            scratch.LastAction = lastAction;
            scratch.Reprisal = reprisal;
            scratch.ArcaneDamage = arcaneDamage;
            scratch.CandidateSkills = CandidateSkills;
            scratch.CandidateLevels = CandidateLevels;
            scratch.OptionCache = OptionCache;
            scratch.PickOrdered = pickOrdered;
            scratch.PickWeights = pickWeights;
            scratch.InUse = false;
        }

        void Grow(int position)
        {
            if (position >= RecDamage.Length)
            {
                int size = position * 2 + 8;
                Array.Resize(ref RecDamage, size);
                Array.Resize(ref RecActions, size);
                Array.Resize(ref lastAction, size);
                Array.Resize(ref reprisal, size);
                Array.Resize(ref arcaneDamage, size);
            }
        }

        /// <summary>Objects the policy uses to examine the options of a decision one after the other (it makes the action it chooses afresh).</summary>
        public readonly Action ScratchAction;
        public readonly List<Unit> PolicyScratch;
        readonly List<Unit> redirectScratch;
        readonly List<Unit> delayOrderScratch;
        readonly int[] statusScratch;
        readonly int[] dispelRemoveScratch;
        readonly int[] tickScratch;
        public Skill[] CandidateSkills;
        public int[] CandidateLevels;

        public struct OptionEntry
        {
            public Unit Owner;
            public int Tp;
            public bool Silenced, Frozen, ShadowSewed;
            public List<(Skill skill, int level)> List;
        }

        /// <summary>The skills each unit could use at her last decision, by position (Policy.Options).</summary>
        public OptionEntry[] OptionCache;

        // --- sides -----------------------------------------------------------------------------------------
        // The lists of the units of one side are worked out again only when a unit has fallen, risen or joined since they were made.
        // The arrays are never changed once made, so a caller that holds one while the battle goes on keeps the list as it was.
        readonly Roster roster = new Roster();
        int cacheVersion = -1;
        Unit[] sideAlive0, sideAlive1, sideAll0, sideAll1, targetable0, targetable1, ownSideAll0, ownSideAll1;

        void Refresh()
        {
            if (cacheVersion == roster.Version) return;
            cacheVersion = roster.Version;
            sideAlive0 = sideAlive1 = sideAll0 = sideAll1 = targetable0 = targetable1 = ownSideAll0 = ownSideAll1 = null;
        }

        Unit[] Build(int side, bool aliveOnly)
        {
            int n = 0;
            foreach (var u in Units) if (u.Side == side && (!aliveOnly || CanFight(u))) n++;
            var r = new Unit[n];
            int k = 0;
            foreach (var u in Units) if (u.Side == side && (!aliveOnly || CanFight(u))) r[k++] = u;
            return r;
        }

        /// <summary>Side(side, aliveOnly) as an array that must not be changed.</summary>
        public Unit[] SideArray(int side, bool aliveOnly = true)
        {
            Refresh();
            if (aliveOnly) return side == Unit.PARTY ? (sideAlive0 ?? (sideAlive0 = Build(side, true))) : (sideAlive1 ?? (sideAlive1 = Build(side, true)));
            return side == Unit.PARTY ? (sideAll0 ?? (sideAll0 = Build(side, false))) : (sideAll1 ?? (sideAll1 = Build(side, false)));
        }

        public Unit[] AlliesArray(Unit unit, bool aliveOnly = true) => SideArray(unit.Side, aliveOnly);
        public Unit[] OpponentsArray(Unit unit, bool aliveOnly = true) => SideArray(1 - unit.Side, aliveOnly);

        /// <summary>Targetable(Side(side)) as an array that must not be changed: the living units of the side that can be picked.</summary>
        public Unit[] TargetableArray(int side)
        {
            Refresh();
            ref Unit[] slot = ref (side == Unit.PARTY ? ref targetable0 : ref targetable1);
            if (slot != null) return slot;
            var alive = SideArray(side, true);
            int n = 0;
            foreach (var u in alive) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) n++;
            var r = new Unit[n];
            int k = 0;
            foreach (var u in alive) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) r[k++] = u;
            slot = r;
            return r;
        }

        /// <summary>The candidates of a side with the test of life left out: its units below 2000, alive or fallen.</summary>
        Unit[] OwnSideAll(int side)
        {
            Refresh();
            var cached = side == 0 ? ownSideAll0 : ownSideAll1;
            if (cached != null) return cached;
            var all = SideArray(side, false);
            int n = 0;
            foreach (var u in all) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) n++;
            var r = new Unit[n];
            int k = 0;
            foreach (var u in all) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) r[k++] = u;
            if (side == 0) ownSideAll0 = r; else ownSideAll1 = r;
            return r;
        }

        void AddUnit(Unit unit)
        {
            unit.Position = Units.Count;
            unit.TieKey = unit.Kind == Kind.Enemy ? 994 - unit.Position : -unit.Position;     // a unit made during the battle comes after the others on a tie
            unit.Roster = roster;
            Units.Add(unit);
            roster.Version++;
            Grow(unit.Position);
            RecDamage[unit.Position] = 0;
            RecActions[unit.Position] = 0;
            lastAction[unit.Position] = null;
            reprisal[unit.Position] = false;
            arcaneDamage[unit.Position] = 0;
            if (unit.Position < OptionCache.Length) OptionCache[unit.Position] = default;
            if (unit.Kind == Kind.Doll && unit.Alive) activeDolls++;
            if (unit.Has(DEMON_WALL)) anyDemonWall = true;
        }

        public List<Unit> Side(int side, bool aliveOnly = true)
        {
            var r = new List<Unit>(8);
            foreach (var u in Units) if (u.Side == side && (!aliveOnly || CanFight(u))) r.Add(u);
            return r;
        }

        public List<Unit> Allies(Unit unit, bool aliveOnly = true) => Side(unit.Side, aliveOnly);
        public List<Unit> Opponents(Unit unit, bool aliveOnly = true) => Side(1 - unit.Side, aliveOnly);

        public List<Unit> Members()
        {
            var r = new List<Unit>(8);
            foreach (var u in Units) if (u.Side == Unit.PARTY && u.Kind == Kind.Member) r.Add(u);
            return r;
        }

        static bool CanFight(Unit u) => u.Alive && !(u.St[120] != null && u.St[120].Stage >= 3);

        public bool Over()
        {
            bool party = false, enemies = false;
            foreach (var u in Units)
            {
                if (!CanFight(u)) continue;
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member) party = true;
                if (u.Side == Unit.ENEMIES) enemies = true;
            }
            return !party || !enemies;
        }

        bool HasOwnedDoll(Unit owner)
        {
            if (activeDolls == 0) return false;
            for (int i = 0; i < Units.Count; i++)
            {
                var u = Units[i];
                if (IsPuppet(u) && u.Owner == owner) return true;
            }
            return false;
        }

        // --- the order of turns ------------------------------------------------------------------------------
        public double Wait(Unit unit, Action action = null, bool chanting = false)
        {
            int statName = Unit.AGI;
            double f1 = 1.0, f2 = 1.0;
            double bonus, enchant;
            if (action != null && chanting)
            {
                int cs = action.Skill != null ? action.Skill.ChantStat : (action.Atk != null ? action.Atk.ChantStat : 0);
                statName = cs == 1 ? Unit.INT : cs == 2 ? Unit.RES : Unit.AGI;
                double? cspeed = action.ChantSpeed;
                f2 = cspeed.HasValue && cspeed.Value != 0 ? cspeed.Value : 1.0;
                // _SetTime (0x44a1ab..0x44a309): chanting uses 214, 265, 281 (without double-counting) + chant enchants 54..56.
                bonus = unit.StatusValue(214) + unit.Value(265) + unit.Value(281);
                enchant = unit.HasEnchants ? F.SpeedEnchantBonus(unit.Pieces(54), unit.Pieces(55), unit.Pieces(56), 0.20, 0.10, 0.20) : 0.0;
            }
            else
            {
                bonus = SumStatus(unit, SPEED_BUFFS);
                if (unit.Hp <= 0.4 * unit.MaxHp && unit.Has(261)) bonus += unit.Value(261);
                enchant = unit.HasEnchants ? F.SpeedEnchantBonus(unit.Pieces(51), unit.Pieces(52), unit.Pieces(53)) : 0.0;
                if (action != null && (action.Kind == AKind.Skill || action.Kind == AKind.Enemy))
                {
                    // _SetTime (0x449c81..0x449df6): Techniques/Joint set F1=speed, F2=1.0; Magic post-cast leaves F1=1.0 and sets F2=speed.
                    double spd = action.Speed + (unit.HasUnique && unit.UniqueEffect == 352 ? unit.Value(352) : 0.0);
                    if (action.Skill != null && action.Skill.IsMagic) { f1 = 1.0; f2 = spd; }
                    else { f1 = spd; f2 = 1.0; }
                }
            }
            // Shared tail (0x44a23d..0x44a309): dance speed (201, 340), Self Session (276), On Stage (277), Double Puppet (316) apply to both chanting and acting turns.
            bonus += unit.StatusValue(201) + unit.StatusValue(340) + unit.Value(276) + unit.Value(277) + (HasOwnedDoll(unit) ? unit.Value(316) : 0.0);
            int stat = unit.Stat(statName);
            double random = MeanWait ? F.SPEED_RANDOM_MEAN : F.SPEED_RANDOM[Rng.ChoiceIndex(F.SPEED_RANDOM.Length)];
            double value = F.TurnValue(stat, unit.Weight, unit.Level, f1 * f2, bonus + enchant, unit.St[122] != null,
                                       action != null && action.Kind == AKind.Defend, false, random);
            if (chanting && unit.HasEnchants && unit.Pieces(298) != 0) value = Math.Min(F.VALUE_CAP, value + 0.25);
            return Math.Max(1.0 - F.VALUE_CAP, 1.0 - value);
        }

        public void Start()
        {
            // members, enemies and dolls start at the value of a plain action (0x449176 - 0x449180: _SetTime, slot 0x20 of the battle
            // class); the summon and a guest at a random gauge (0x449194 - 0x4491ba), unless an enemy of the battle has bit 1 of its
            // flags word (+0x54 of its status data, 0x439f3f - 0x439f46, the byte +0x33 of the battle), when they take the plain value too
            int members = 0, enemies = 0;
            bool party297 = false, party295 = false;
            var initParty = new List<Unit>(6);
            foreach (var u in Units)
            {
                u.TieKey = u.Kind == Kind.Member ? 999 - members++ : u.Kind == Kind.Enemy ? 994 - enemies++
                         : u.Kind == Kind.Summon ? (u.IsGuest ? 929 : 930) : -u.Position;
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member)
                {
                    initParty.Add(u);
                    if (u.HasEnchants)
                    {
                        if (u.Pieces(297) != 0) party297 = true;
                        if (u.Pieces(295) != 0) party295 = true;
                    }
                }
            }
            // 0x43daca: compute each party member's base formation target share once at battle start (never recomputed on deaths).
            if (initParty.Count > 0)
            {
                var ordered = new List<Unit>(initParty.Count);
                int frontCount = 0;
                foreach (var u in initParty) if (u.Front) { ordered.Add(u); frontCount++; }
                foreach (var u in initParty) if (!u.Front) ordered.Add(u);
                var row = TargetShareRow(ordered.Count, frontCount);
                for (int k = 0; k < ordered.Count; k++)
                    ordered[k].BaseTargetShare = k < row.Length ? row[k] : row[row.Length - 1];
            }
            // 0x4fecc0 / 0x4ff630: party enchantments 297 (+30 all stats) and 295 (+10% all stats) boost hired guest allies.
            if (party297 || party295)
            {
                foreach (var u in Units)
                {
                    if (!u.IsGuest) continue;
                    for (int s = 0; s < 6; s++)
                    {
                        if (party297) u.Base[s] += 30;
                        if (party295) u.Base[s] += PyMath.Int(u.Base[s] * 0.10);
                    }
                }
            }
            bool flagged = false;
            foreach (var u in Units)
                if (u.Kind == Kind.Enemy && u.EnemyId != T.NONE && Data.Enemies.TryGetValue(u.EnemyId, out var rec) && ((rec.Flags >> 1) & 1) != 0) flagged = true;
            foreach (var u in Units)
            {
                double gauge;
                if ((u.Kind == Kind.Summon || u.Kind == Kind.Npc) && !flagged) gauge = (Rng.RandRange(START_GAUGE) + 1) / 1000.0;
                else gauge = 1.0 - Wait(u);
                u.NextTime = 1.0 - gauge;
            }
            bool ambush = Ambush(Unit.PARTY) || Ambush(Unit.ENEMIES);
            // 0x449184: noTurnJitterFlag (enemy 0x3C bit 1) suppresses the 20% battle-start order scramble.
            if (!ambush && !flagged && Rng.RandRange(100) < RANDOM_ORDER)
                foreach (var u in Units) u.NextTime = 1.0 - Rng.RandRange(93) / 100.0;
            // 0x4491f2..0x44949e: Preemptive Strike (300) is skipped after an ambush, scans living candidates (<2000) only, and stops on first proc.
            if (!ambush)
            {
                foreach (var u in Units)
                    if (CanFight(u) && !NotACandidate(u) && u.Has(300) && Roll(u.Value(300))) { u.NextTime = 0.0; break; }
            }
        }

        bool Ambush(int side)
        {
            bool certain = false;
            foreach (var u in Units) if (u.Side == side && u.Alive && u.Has(321)) certain = true;
            if (!certain && !Options.RandomBattle) return false;
            double maxMine = 0.0; bool anyMine = false;
            foreach (var u in Units) if (u.Side == side && u.Alive) { double v = u.Value(268); if (!anyMine || v > maxMine) { maxMine = v; anyMine = true; } }
            int chance = AMBUSH_CHANCE[side] + PyMath.Int(maxMine * 100);
            if (!certain)
            {
                if (Rng.RandRange(100) >= chance) return false;
                double maxOther = 0.0; bool anyOther = false;
                foreach (var u in Units) if (u.Side != side && u.Alive) { double v = u.Value(267); if (!anyOther || v > maxOther) { maxOther = v; anyOther = true; } }
                if (Rng.RandRange(100) < PyMath.Int(maxOther * 100)) return false;
            }
            foreach (var u in Units) if (u.Side == side && u.Alive) u.NextTime = 0.0;
            return true;
        }

        // --- the battle ------------------------------------------------------------------------------------
        public BattleResult Run()
        {
            try
            {
                Trace?.Begin(this);
                Start();
                Trace?.Started(this);
                LowestHp = PartyHpShare();
                while (!Over() && Time < MaxTime && Actions < MaxActions)
                {
                    Unit unit = null;
                    for (int i = 0; i < Units.Count; i++)
                    {
                        var u = Units[i];
                        if (!u.Alive) continue;
                        if (unit == null || u.NextTime < unit.NextTime || (u.NextTime == unit.NextTime && u.TieKey > unit.TieKey)) unit = u;
                    }
                    Time = unit.NextTime;
                    Trace?.TurnStart(this, unit);
                    Turn(unit);
                    Trace?.TurnEnd(this, unit);
                    LowestHp = Math.Min(LowestHp, PartyHpShare());
                }
                var result = Result();
                Trace?.Ended(this, result);
                return result;
            }
            finally
            {
                ReleaseScratch();
            }
        }

        public double PartyHpShare()
        {
            long hp = 0, max = 0;
            foreach (var u in Units)
            {
                if (u.Side != Unit.PARTY || u.Kind != Kind.Member) continue;
                if (u.Alive) hp += u.Hp;
                max += u.MaxHp;
            }
            return (double)hp / Math.Max(1L, max);
        }

        public BattleResult Result()
        {
            var r = new BattleResult();
            bool enemiesAlive = false, anyMemberAlive = false;
            long hp = 0, maxHp = 0, tp = 0, maxTp = 0;
            int alive = 0, enemyDamage = 0, enemyActions = 0;
            foreach (var u in Units)
            {
                if (u.Side == Unit.ENEMIES)
                {
                    if (CanFight(u)) enemiesAlive = true;
                    enemyDamage += RecDamage[u.Position];
                    enemyActions += RecActions[u.Position];
                }
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member)
                {
                    if (CanFight(u)) { anyMemberAlive = true; alive++; }
                    hp += u.Hp; maxHp += u.MaxHp; tp += u.Tp; maxTp += u.MaxTp;
                }
            }
            r.Won = !enemiesAlive;
            r.Lost = !anyMemberAlive;
            r.Time = Time;
            r.Actions = Actions;
            r.LowestHp = LowestHp;
            r.EnemyDamage = enemyDamage;
            r.EnemyActions = enemyActions;
            r.PartyMaxHp = (int)maxHp;
            r.HpLeft = (double)hp / Math.Max(1L, maxHp);
            r.TpLeft = (double)tp / Math.Max(1L, maxTp);
            r.Alive = alive;
            if (Rec != null) { r.Record = Rec; r.RecordUnits = Units; }
            return r;
        }

        enum Lost { No, Skip, Empty }

        bool ConsumeBarrier(Unit target)
        {
            for (int k = 0; k < 3; k++)
            {
                int ec = k == 0 ? 101 : k == 1 ? 102 : 181;
                var bs = target.St[ec];
                if (bs != null)
                {
                    bs.Value -= 1;
                    if (bs.Value <= 0) target.PopStatus(ec);
                    return true;
                }
            }
            return false;
        }

        void RollAilmentRecovery(Unit unit)
        {
            // Inner State 1 (0x43692f..0x436b60): natural recovery for recovering ailments (113..117, 122) runs BEFORE LostTurn.
            int n = unit.StCount;
            if (n == 0) return;
            var order = n <= tickScratch.Length ? tickScratch : new int[n];
            for (int i = 0; i < n; i++) order[i] = unit.StatusAt(i);
            for (int k = 0; k < n; k++)
            {
                int effect = order[k];
                if (!IsAilment[effect] || effect == 118 || effect == 119 || effect == 120 || effect == 123) continue;
                var s = unit.St[effect];
                if (s == null) continue;
                int chance = s.HasData ? PyMath.Int(s.Data) : 0;
                if (Rng.RandRange(100) < chance) unit.PopStatus(effect);
                else s.WithData(chance + 10);
            }
        }

        void DecrementTimedStatuses(Unit unit)
        {
            // Inner State 8 (0x436d4c): timed status durations decrement BEFORE 259/283/203 turn-loss checks.
            int n = unit.StCount;
            if (n == 0) return;
            var order = n <= tickScratch.Length ? tickScratch : new int[n];
            for (int i = 0; i < n; i++) order[i] = unit.StatusAt(i);
            for (int k = 0; k < n; k++)
            {
                int effect = order[k];
                var s = unit.St[effect];
                if (s != null && s.Turns > 0)
                {
                    s.Turns -= 1;
                    if (s.Turns <= 0) unit.PopStatus(effect);
                }
            }
        }

        void CompletePetrify(Unit unit)
        {
            // 0x48305a..0x4831eb, 0x4f99c1..0x4f9b6b, 0x4fa870:
            // Stage-3 petrification leaves HP intact and Alive = true, ends performances/chant,
            // and clears all other statuses while preserving Status(120) at Stage = 3.
            EndParts(unit, PerfParts.All);
            var pet = unit.St[120];
            var effects = SnapshotStatuses(unit, statusScratch, out int sc);
            for (int k = 0; k < sc; k++)
            {
                int e = effects[k];
                if (e != 120) unit.PopStatus(e);
            }
            if (pet != null) pet.Stage = 3;
            unit.InvalidateRoster();
            // 0x436c82 -> 0x43a4a0: Stage-3 Petrified enemies are defeated/removed from battle; players stay Alive at Stage 3.
            if (unit.Kind == Kind.Enemy && unit.Alive) Fall(unit, null);
        }

        void TickSamba199(Unit unit)
        {
            // 0x436343..0x4365fb: Summons/Guests (3000..3999) run Samba Dance (199) tick only before skipping inner states.
            for (int i = 0; i < Units.Count; i++)
            {
                var t = Units[i];
                if (!t.Alive || t.StCount == 0) continue;
                var s199 = t.St[199];
                if (s199 != null && (s199.Source == unit || (s199.Source == null && t == unit)))
                {
                    int amount = PyMath.Int(t.MaxHp * s199.Value);
                    if (s199.HasData) amount = Math.Min(amount, PyMath.Int(s199.Data));
                    LoseHp(t, amount, s199.Source);
                }
            }
        }

        void Turn(Unit unit)
        {
            Actions++;
            unit.TurnsTaken++;
            unit.Defending = false;
            // 0x4365ff (mov eax,[esi+0xb0]; test eax,eax; jne 0x43875a): ALL extra turns (288 Double Action,
            // 289 Triple Action, and 354 Unique) skip Turn-Start Phases 0..24 and go straight to Action selection.
            bool extraTurn = unit.ExtraTurn;
            // 0x436322..0x43664d: Dolls (2000..2999) skip inner TurnPhaseNo 0..24 completely;
            // Summons/Guests (3000..3999) run only Samba 199 tick + DecrementTimedStatuses before acting.
            if (unit.Kind == Kind.Doll)
            {
                if (!unit.Alive) { EndOfTurn(unit, false, false); return; }
                bool dollActed = false;
                Action dollAct = NextAction(unit);
                if (dollAct != null) { dollActed = true; Perform(dollAct); }
                EndOfTurn(unit, dollActed, !extraTurn);
                return;
            }
            if (unit.Kind == Kind.Summon || unit.Kind == Kind.Npc)
            {
                if (!extraTurn)
                {
                    TickSamba199(unit);
                    DecrementTimedStatuses(unit);
                }
                if (!CanFight(unit)) { EndOfTurn(unit, false, false); return; }
                bool sgActed = false;
                Action sgAct = NextAction(unit);
                if (sgAct != null) { sgActed = true; Perform(sgAct); }
                EndOfTurn(unit, sgActed, !extraTurn);
                return;
            }
            Lost softLost = Lost.No;
            if (!extraTurn)
            {
                // Inner State 0: Esarhaddon (311)
                if (unit.Has(311))
                {
                    int n = PyMath.Int(unit.Value(311));
                    for (int i = 0; i < Math.Min(Math.Max(n, 0), ESARHADDON_ORDER.Length); i++)
                        unit.PopStatus(ESARHADDON_ORDER[i]);
                }
                // Inner State 1: natural recovery of recovering ailments (113..117, 122) before Sleep/Paralysis turn-loss.
                RollAilmentRecovery(unit);
                // Inner State 2: Third Eye Wide (345) of each opponent — initializes recovery chance at 0% (0x47ee00).
                foreach (var other in OpponentsArray(unit))
                {
                    if (other.HasUnique && other.UniqueEffect == 345 && Roll(other.UniqueValue))
                    {
                        int[] choices = { 113, 115, 116, 114, 117, 118, 74 };
                        int effect = choices[Rng.ChoiceIndex(choices.Length)];
                        // X16 (0x47ee73): vanilla skips buff dispel; Balance NOPs the jump (75% dispel chance).
                        if (effect == 74) { if ((Options.ThirdEyeDispel ?? Data.ThirdEyeDispel) && Roll(0.75)) Dispel(unit); }
                        else ApplyAilment(other, unit, effect, 0.75, null, 0);
                    }
                }
                // Inner State 3 (0x436a9b..0x436be3 -> CActionPatternU0008 0x42fb60): Overstock Clearance (446) casts a free
                // weighted item from [1, 6, 45, 49, 55, 56] (weights [20, 20, 20, 15, 15, 15], total 105) without consuming inventory.
                if (unit.Alive && unit.Side == Unit.PARTY && unit.HasUnique && unit.UniqueEffect == 446 && Roll(unit.UniqueValue))
                    RunOverstockClearance(unit);
                // Inner State 4 (0x436be4 -> 0x48305a..0x4831eb): gradual petrification advances 1 -> 2 -> 3 with no natural recovery;
                // at stage 3, barrier (101/102/181) blocks AND cures petrification (0x4830ad), otherwise CompletePetrify.
                var petrify = unit.St[120];
                if (petrify != null && petrify.Stage < 3)
                {
                    petrify.Stage++;
                    if (petrify.Stage == 3)
                    {
                        if (ConsumeBarrier(unit))
                            unit.PopStatus(120);
                        else
                            CompletePetrify(unit);
                    }
                }
                // Inner States 5-7: hard turn loss (dead, Stage>=3 petrify, Sleep 116, Paralysis 115 30%).
                Lost hardLost = LostTurnHard(unit);
                if (hardLost != Lost.No)
                {
                    Rec?.TurnsLost.Add(new RecKey(unit), 1);
                    EndOfTurn(unit, false, true);
                    return;
                }
                // Inner State 8: decrement timed statuses before 259/283/203 turn-loss checks.
                DecrementTimedStatuses(unit);
                // Inner States 9-11: soft turn loss (Warning Shot 259 -> 0.3x attack + Empty on HP dmg, Magnificent Steps 283 -> Skip, Mesmerized 203 -> Skip).
                softLost = LostTurnSoft(unit);
                if (softLost != Lost.No)
                {
                    Rec?.TurnsLost.Add(new RecKey(unit), 1);
                }
                else if (CanFight(unit))
                {
                    // Inner States 12-15 (0x437364..0x4379b0): Murder License 319, Tranquil 357, Usurper 350, ShadowHeart 448.
                    RunTurnStartProcs(unit);
                    // Inner States 16-21: regen, dancer-turn dances (199/200/204/339), and Poison (113).
                    if (CanFight(unit)) TickRegenAndDances(unit);
                    if (!CanFight(unit)) return;
                    // Inner State 22 (0x43851e): Undaunted (355) runs only when turn was not lost.
                    Undaunted(unit.Side);
                }
            }
            else if (!CanFight(unit))
            {
                EndOfTurn(unit, false, false);
                return;
            }
            bool acted = false;
            if (softLost == Lost.No && CanFight(unit))
            {
                Action action = NextAction(unit);
                if (action != null)
                {
                    acted = true;
                    Perform(action);
                }
            }
            EndOfTurn(unit, acted, !extraTurn);
        }

        void RunOverstockClearance(Unit unit)
        {
            // CActionPatternU0008::_Task (0x42fb60..0x4302cf): Rand(105) over [20,40,60,75,90,105] -> items [1,6,45,49,55,56], free cast.
            int r = Rng.RandRange(105);
            int itemId = r < 20 ? 1 : r < 40 ? 6 : r < 60 ? 45 : r < 75 ? 49 : r < 90 ? 55 : 56;
            if (!Data.Items.ContainsKey(itemId)) return;
            var allies = TargetableArray(unit.Side);
            var enemies = TargetableArray(1 - unit.Side);
            Unit target = null;
            if (itemId == 1 && allies.Length > 0)
            {
                target = allies[0];
                for (int i = 1; i < allies.Length; i++) if (allies[i].HpRatio < target.HpRatio) target = allies[i];
            }
            else if (itemId == 6 && allies.Length > 0)
            {
                target = allies[0];
            }
            else if (itemId == 45 && allies.Length > 0)
            {
                target = allies[0];
                for (int i = 1; i < allies.Length; i++) if (allies[i].TpRatio < target.TpRatio) target = allies[i];
            }
            else if (itemId == 49 && allies.Length > 0)
            {
                var pool = PolicyScratch; pool.Clear();
                foreach (var a in allies) if (HasTrueAilment(a)) pool.Add(a);
                target = pool.Count > 0 ? pool[Rng.ChoiceIndex(pool.Count)] : allies[Rng.ChoiceIndex(allies.Length)];
            }
            else if (itemId == 55 && enemies.Length > 0)
            {
                target = enemies[Rng.ChoiceIndex(enemies.Length)];
            }
            else if (itemId == 56 && enemies.Length > 0)
            {
                var front = new List<Unit>(enemies.Length);
                var back = new List<Unit>(enemies.Length);
                foreach (var e in enemies) if (e.Front) front.Add(e); else back.Add(e);
                var row = front.Count == 0 ? back : back.Count == 0 ? front : (Rng.RandRange(2) == 0 ? front : back);
                if (row.Count > 0) target = row[0];
            }
            if (target != null) UseItemFree(unit, itemId, target);
        }

        void RunTurnStartProcs(Unit unit)
        {
            // Inner State 12: Murder License (enemy passive 1580, effect 319; CActionPatternE1580 0x437364..0x437488):
            // deterministically applies raw Instakill (119, value 1.0) to a random living targetable opponent.
            if (unit.Alive && unit.Has(MURDER_LICENSE))
            {
                var foes = TargetableArray(1 - unit.Side);
                if (foes.Length > 0)
                    ApplyAilment(unit, foes[Rng.ChoiceIndex(foes.Length)], 119, 1.0, null, 0);
            }
            if (!unit.Alive || !unit.HasUnique) return;
            int effect = unit.UniqueEffect;
            double value = unit.UniqueValue;
            // Inner State 13: Tranquil Song (357)
            if (effect == 357 && Roll(value))
            {
                foreach (var other in OpponentsArray(unit))
                {
                    other.SetStatus(new Status(41, -0.1, TRANQUIL_TURNS, unit));
                    other.SetStatus(new Status(43, -0.1, TRANQUIL_TURNS, unit));
                }
            }
            // Inner State 14: Usurper of Souls (350)
            if (effect == 350 && Roll(value))
            {
                // one doll of the other side, drawn evenly (0x437787 - 0x437845): never the summon or a guest, never more than one
                var list = new List<Unit>();
                foreach (var u in Units) if (u.Side != unit.Side && u.Alive && u.Kind == Kind.Doll) list.Add(u);
                if (list.Count > 0) RemoveDoll(list[Rng.ChoiceIndex(list.Count)]);
            }
            // Inner State 15: ShadowHeart (448)
            if (effect == 448 && Roll(value))
            {
                // 0x437960: blocked if the unit already owns ANY active doll (not only a shadow), and subject to MAX_ACTIVE_DOLLS.
                bool any = false;
                foreach (var u in Units) if (u.Alive && u.Kind == Kind.Doll && u.Owner == unit) { any = true; break; }
                if (!any && ActiveDollCount() < MAX_ACTIVE_DOLLS) AddShadow(unit);
            }
        }

        void AddShadow(Unit owner)
        {
            var rec = new DollRec { Name = owner.Name + "'s shadow", Turns = new[] { SHADOW_LIFE }, Range = null, Actions = Array.Empty<int>(), Skill = T.NONE };
            var unit = UnitFactory.BuildDoll(owner, rec, 1, null);
            // 0x4fe2e0..0x4fe3d5: copies owner's pre-buff Base stats (not buffed Stat()), doubles ATK once, and copies all non-ailment statuses.
            for (int s = 0; s < 6; s++) unit.Base[s] = owner.Base[s];
            unit.Base[Unit.ATK] *= SHADOW_ATTACK;
            if (owner.OffhandBonus != null)
            {
                unit.OffhandBonus = (int[])owner.OffhandBonus.Clone();
                unit.OffhandBonus[Unit.ATK] *= SHADOW_ATTACK;
            }
            unit.Raw = owner.Raw != null ? (int[])owner.Raw.Clone() : null;
            unit.AdoptPassives((double[])owner.Pv.Clone());
            unit.PvInt = owner.PvInt != null ? (bool[])owner.PvInt.Clone() : null;
            unit.SetEnchants((int[])owner.Enchants.Clone());
            unit.Weapon = owner.Weapon;
            unit.AttackRange = owner.AttackRange;
            unit.AttackAttr = owner.AttackAttr;
            unit.Swing = owner.Swing;
            for (int i = 0; i < owner.StCount; i++)
            {
                var st = owner.St[owner.StatusAt(i)];
                if (st == null || IsTrueAilmentId(st.Effect) || st.Effect == 139) continue;
                unit.SetStatus(new Status(st.Effect, st.Value, st.Turns, st.Source, st.Skill, st.Kind, st.AttackId) { HasData = st.HasData, Data = st.Data, IsInt = st.IsInt });
            }
            unit.ShadowOf = owner;
            unit.Position = Units.Count;
            // 0x43a2a3..0x43a2bf: newly added dolls start at gauge = RandRange(92) / 100.0 -> NextTime = Time + 1.0 - gauge.
            unit.NextTime = Time + 1.0 - Rng.RandRange(92) / 100.0;
            AddUnit(unit);
        }

        void Undaunted(int side)
        {
            foreach (var u in Units)
            {
                if (u.Side == side && !u.Alive && u.Kind == Kind.Member && u.HasUnique && u.UniqueEffect == 355 && Roll(u.UniqueValue))
                {
                    u.Alive = true; u.Hp = 1;
                    u.NextTime = Time + Wait(u);
                }
            }
        }

        Lost Deny(Unit unit, Lost how)
        {
            if (unit.Side == Unit.ENEMIES) Rec?.Denied.Add(new RecKey(unit), 1);
            return how;
        }

        Lost LostTurnHard(Unit unit)
        {
            if (!unit.Alive) return Lost.Skip;
            // 0x436c3f..0x436d4c & 0x4fb590..0x4fb63f: Phase 5 (+0xc8) defeats Stage-3 enemy via _SetDead or skips player;
            // Phase 6 (+0xbc) skips Sleep (116); Phase 7 Paralysis (115) 30%.
            var pet = unit.St[120];
            if (pet != null && pet.Stage >= 3)
            {
                if (unit.Kind == Kind.Enemy && unit.Alive) Fall(unit, null);
                return Deny(unit, Lost.Skip);
            }
            if (unit.St[116] != null) return Deny(unit, Lost.Skip);
            if (unit.St[115] != null && Rng.RandRange(100) < 30) return Deny(unit, Lost.Skip);
            return Lost.No;
        }

        Lost LostTurnSoft(Unit unit)
        {
            // Inner State 9 (0x436d60): Warning Shot (259) — all opposing bearers roll BEFORE State 10 (283).
            // On proc, opposing bearer fires a 0.3x physical basic attack; turn is cancelled ONLY if HP damage lands.
            foreach (var other in OpponentsArray(unit))
            {
                if (other.Has(259) && Roll(other.Value(259)))
                {
                    Action shot = new Action(other, AKind.Attack) { WarningShot = true };
                    if (other.Kind != Kind.Member && other.Attacks != null && other.Attacks.Length > 0)
                    {
                        var atk0 = Data.GetAttack(other.Attacks[0]);
                        if (atk0 != null) shot = new Action(other, AKind.Enemy, atk0, 1) { WarningShot = true };
                    }
                    lastDealtDamage = 0;
                    int preHp = unit.Hp;
                    inCounter = true;
                    try { Resolve(shot, unit, 0); }
                    finally { inCounter = false; }
                    if (lastDealtDamage > 0 || unit.Hp < preHp || !unit.Alive)
                        return Deny(unit, Lost.Empty);
                }
            }
            // Inner State 10 (0x436ee0): Magnificent Steps / Mesmerized (283)
            foreach (var other in OpponentsArray(unit))
            {
                if (other.Has(283) && Roll(other.Value(283))) return Deny(unit, Lost.Skip);
            }
            // Inner State 11: Erotic Dance (203)
            if (unit.Has(203) && Roll(unit.Value(203))) return Deny(unit, Lost.Skip);
            return Lost.No;
        }

        /// <summary>Centralized binary action legality check (0x455bc0 / 0x4f4910 / 0x455d94 / 0x515f7c).
        /// Asserted on Policy.Choose inside Battle.NextAction (not raw synthetic Battle.Perform calls).</summary>
        public bool IsLegalAction(Action action)
        {
            if (action == null || action.Actor == null || !CanFight(action.Actor)) return false;
            var actor = action.Actor;
            if (action.Kind == AKind.Skill)
            {
                var skill = action.Skill;
                if (skill == null || !Policy.UsableInBattle(skill)) return false;
                if (actor.St[123] != null) return false;
                if (skill.IsMagic && (actor.St[117] != null || (ZoneInfo != null && ZoneInfo.NoMagic))) return false;
                if (skill.IsTechnique && actor.St[114] != null) return false;
                if (!Policy.WeaponAllows(actor, skill)) return false;
                if (!action.Paid && EffectiveTpCost(actor, skill, action.Level) > actor.Tp) return false;
                return true;
            }
            if (action.Kind == AKind.Item)
            {
                return action.Item != T.NONE && actor.Items.TryGetValue(action.Item, out int cnt) && cnt > 0;
            }
            return true;
        }

        Action NextAction(Unit unit)
        {
            if (unit.Chant != null)
            {
                var chanted = unit.Chant;
                unit.Chant = null;
                chanted.Chanting = false;
                Rec?.ChantsDone.Add(new RecKey(unit), 1);
                return chanted;
            }
            if (unit.Kind == Kind.Doll) return DollAction(unit);
            Action action;
            if (unit.Side == Unit.PARTY && unit.Kind == Kind.Member && ChooseMember != null)
            {
                StartDecision();
                try { action = ChooseMember.Choose(this, unit); }
                finally { EndDecision(); }
                if (action != null && !IsLegalAction(action))
                    throw new InvalidOperationException($"Policy returned illegal action {action.Kind} ({action.SourceName ?? action.Item.ToString()}) for {unit.Name}");
            }
            else action = Ai.Choose(this, unit);
            if (action == null) return null;
            if (action.Skill != null && (unit.St[123] != null ||
                (unit.St[117] != null && action.Skill.IsMagic) ||
                (unit.St[114] != null && action.Skill.IsTechnique)))
                action = new Action(unit, AKind.Attack);
            double? speed = action.ChantSpeed;
            if (speed.HasValue && speed.Value != 0 && !(unit.HasUnique && unit.UniqueEffect == 358 && Roll(unit.UniqueValue)))
            {
                Pay(action);
                action.Paid = true;
                action.Chanting = true;
                unit.Chant = action;
                Rec?.ChantsStarted.Add(new RecKey(unit), 1);
                return ChantOf(unit, action);
            }
            return action;
        }

        static Action ChantOf(Unit unit, Action a)
        {
            return a.Skill != null ? new Action(unit, AKind.Chant, a.Skill, a.Level)
                 : a.Atk != null ? new Action(unit, AKind.Chant, a.Atk, a.Level)
                 : new Action(unit, AKind.Chant);
        }

        public static int EffectiveTpCost(Unit unit, Skill skill, int level)
        {
            if (skill == null) return 0;
            int cost = skill.Tp[Math.Min(level, skill.Tp.Length) - 1];
            if (cost <= 0) return 0;
            bool technique = skill.IsTechnique;
            if (unit.Pieces(technique ? 246 : 248) != 0) cost = PyMath.Int(cost * 0.8);
            if (unit.Pieces(technique ? 247 : 249) != 0) cost = PyMath.Int(cost * 0.6);
            cost = Math.Max(1, cost);
            if (unit.Has(266)) cost = Math.Max(1, cost - PyMath.Int(Math.Ceiling(cost * unit.Value(266))));
            return cost;
        }

        public static int EffectiveTpCost(Action action) => action.Skill != null ? EffectiveTpCost(action.Actor, action.Skill, action.Level) : 0;

        void Pay(Action action)
        {
            int cost = EffectiveTpCost(action);
            if (cost <= 0) return;
            var unit = action.Actor;
            unit.Tp = Math.Max(0, unit.Tp - cost);
            Rec?.TpSpent.Add(new RecKey(unit), cost);
        }

        void EndOfTurn(Unit unit, bool acted, bool dollTick)
        {
            if (unit.Alive && dollTick && unit.Kind == Kind.Doll)
            {
                unit.Life -= 1;
                if (unit.Life <= 0) RemoveDoll(unit);
            }
            if (!unit.Alive) return;
            // 0x438e50: Heretic Samsara (291) re-rolls fixed resistances Post-Action once latched below 50% HP.
            if (unit.SamsaraState != 0 && (unit.SamsaraState == 2 || unit.Hp < unit.MaxHp / 2.0))
            {
                unit.Samsara = new int[8];
                for (int i = 0; i < 8; i++) unit.Samsara[i] = (Rng.RandRange(2) + 1) * SAMSARA_STEP;
                unit.SamsaraState = 2;
            }
            Action last = acted ? lastAction[unit.Position] : null;
            double wait;
            if (unit.Chant != null) wait = Wait(unit, unit.Chant, true);
            else wait = Wait(unit, last);
            unit.NextTime = Time + wait;
            if (unit.Extra > 0 && unit.Chant == null && unit.St[116] == null && !Over())
            {
                unit.Extra--;
                unit.NextTime = Time;
                unit.ExtraTurn = true;
            }
            else if (unit.ExtraTurn)
            {
                unit.Extra = 0;
                unit.ExtraTurn = false;
                unit.ExtraUnique = false;
            }
            else if (acted && unit.Chant == null && unit.St[116] == null && !Over())
            {
                if (unit.Has(288) && Roll(unit.Value(288))) unit.Extra = 1;
                else if (unit.Has(289) && Roll(unit.Value(289))) unit.Extra = 2;
                else if (unit.HasUnique && unit.UniqueEffect == 354 && Roll(unit.UniqueValue))
                {
                    unit.Extra = 1;
                    unit.ExtraUnique = true;
                }
                if (unit.Extra > 0)
                {
                    unit.Extra--;
                    unit.NextTime = Time;
                    unit.ExtraTurn = true;
                }
            }
        }

        void TickRegenAndDances(Unit unit)
        {
            // Inner States 16-21 (0x437bb5..0x438500): HP/TP regen passives/statuses/enchants, dances on dancer's turn, Poison (113).
            if (unit.HasPassive(246) && unit.St[246] == null) Restore(unit, PyMath.Int(unit.MaxHp * unit.Passive(246)));
            if (unit.HasPassive(247) && unit.St[247] == null && unit.Side == Unit.PARTY)
                unit.Tp = Math.Min(unit.MaxTp, unit.Tp + PyMath.Int(unit.Passive(247)));
            int n = unit.StCount;
            var order = n <= tickScratch.Length ? tickScratch : new int[n];
            for (int i = 0; i < n; i++) order[i] = unit.StatusAt(i);
            for (int k = 0; k < n; k++)
            {
                int effect = order[k];
                var s = unit.St[effect];
                if (s == null) continue;
                if (effect == 246)
                {
                    Restore(unit, PyMath.Int(unit.MaxHp * s.Value));
                }
                else if (effect == 247 && unit.Side == Unit.PARTY)
                {
                    unit.Tp = Math.Min(unit.MaxTp, unit.Tp + PyMath.Int(s.Value));
                }
                else if (effect == 215)
                {
                    double bonus = s.HasData ? s.Data : 0.0;
                    Restore(unit, PyMath.Int(s.Value * (1 + 10 * bonus)));
                }
                else if (effect == 216 && unit.Side == Unit.PARTY)
                {
                    double bonus = s.HasData ? s.Data : 0.0;
                    unit.Tp = Math.Min(unit.MaxTp, unit.Tp + PyMath.Int(s.Value + 100 * bonus));
                }
            }
            EnchantRecovery(unit);
            // Dances 199, 200, 204, 339 tick on the DANCER's turn across all living units bearing that dancer's dance (0x42b5b5).
            // Dance 200 multiplies target.MaxTp (not MaxHp).
            for (int i = 0; i < Units.Count; i++)
            {
                var t = Units[i];
                if (!t.Alive || t.StCount == 0) continue;
                var s199 = t.St[199];
                if (s199 != null && (s199.Source == unit || (s199.Source == null && t == unit)))
                {
                    int amount = PyMath.Int(t.MaxHp * s199.Value);
                    if (s199.HasData) amount = Math.Min(amount, PyMath.Int(s199.Data));
                    LoseHp(t, amount, s199.Source);
                }
                if (!t.Alive) continue;
                var s339 = t.St[339];
                if (s339 != null && (s339.Source == unit || (s339.Source == null && t == unit)))
                {
                    int amount = PyMath.Int(t.MaxHp * s339.Value);
                    if (s339.HasData) amount = Math.Min(amount, PyMath.Int(s339.Data));
                    LoseHp(t, amount, s339.Source);
                }
                if (!t.Alive) continue;
                var s200 = t.St[200];
                if (s200 != null && (s200.Source == unit || (s200.Source == null && t == unit)))
                {
                    int amount = PyMath.Int(t.MaxTp * s200.Value);
                    if (s200.HasData) amount = Math.Min(amount, PyMath.Int(s200.Data));
                    t.Tp = Math.Max(0, t.Tp - amount);
                }
                var s204 = t.St[204];
                if (s204 != null && t.Side == Unit.PARTY && (s204.Source == unit || (s204.Source == null && t == unit)))
                {
                    t.Pep += s204.Value;
                    t.ClampPep();
                }
            }
            if (unit.Alive && unit.St[113] != null && unit.St[116] == null)
            {
                int amount = Math.Min(POISON_CAP, PyMath.Int(unit.MaxHp * POISON_SHARE));
                if (amount <= 0 || amount >= unit.Hp) amount = unit.Hp - 1;
                LoseHp(unit, amount, null);
            }
        }

        /// <summary>State 16, after the statuses: the HP and TP the enchantments of the unit give back every turn (0x437bb5 - 0x437dfb).
        /// HP: max(4, max HP * 0.04 a piece of 144), plus max(2, 0.02 a piece of 145), plus max(10, 0.08 a piece of 148), plus all of
        /// it on 4 in 100 with 296; TP: 4 a piece of 146, 2 of 147, 6 of 149.</summary>
        void EnchantRecovery(Unit unit)
        {
            int heal = 0;
            foreach (var (enchant, share, floor) in F.HP_REGEN_ENCHANTS)
            {
                int n = unit.Pieces(enchant);
                if (n == 0) continue;
                float f = (float)n * (float)share;
                heal += Math.Max(floor, (int)((float)unit.MaxHp * f));
            }
            if (unit.Pieces(F.FULL_RECOVERY_ENCHANT) != 0 && Rng.RandRange(100) < F.FULL_RECOVERY_CHANCE) heal += unit.MaxHp;
            if (heal > 0) Restore(unit, heal);
            int tp = 0;
            foreach (var (enchant, amount) in F.TP_REGEN_ENCHANTS) tp += amount * unit.Pieces(enchant);
            if (tp > 0) unit.Tp = Math.Min(unit.MaxTp, unit.Tp + tp);
        }

        // --- performing an action ----------------------------------------------------------------------------
        public void Perform(Action action)
        {
            var unit = action.Actor;
            Grow(unit.Position);
            lastAction[unit.Position] = action;
            RecActions[unit.Position]++;
            Rec?.Actions.Add(new RecKey(unit), 1);
            Trace?.Perform(this, action);
            if (action.Kind == AKind.Chant)
            {
                lastAction[unit.Position] = null;
                return;
            }
            if (action.Kind == AKind.Defend)
            {
                unit.Defending = true;
                // enchantments 257 and 292: a defending unit recovers max(10, int(max HP * 0.2)) HP and max(5, int(max TP * 0.1)) TP
                // (0x4197ae - 0x41982c, 0x419843 - 0x4198a6)
                if (unit.Pieces(F.DEFEND_HP_ENCHANT) != 0)
                    Healed(unit, Restore(unit, Math.Max(F.DEFEND_HP_FLOOR, PyMath.Int(F.Single(F.Single(unit.MaxHp) * F.Single(F.DEFEND_HP_SHARE))))));
                if (unit.Pieces(F.DEFEND_TP_ENCHANT) != 0)
                    unit.Tp = Math.Min(unit.MaxTp, Math.Max(0, unit.Tp + Math.Max(F.DEFEND_TP_FLOOR, PyMath.Int(F.Single(F.Single(unit.MaxTp) * F.Single(F.DEFEND_TP_SHARE))))));
                return;
            }
            if (action.Kind == AKind.Wait) return;
            if (action.Kind == AKind.Item) { UseItem(action); return; }
            if (ZoneInfo != null && ZoneInfo.NoMagic && unit.Kind != Kind.Doll && action.Spell)
            {
                Rec?.SkillUses.Add(new RecKey(unit, "nullified in an anti-magic zone"), 1);
                return;
            }
            if (!action.Paid && action.Kind == AKind.Skill) Pay(action);
            if (Rec != null) Rec.SkillUses.Add(new RecKey(unit, action.SourceName ?? "Attack"), 1);
            unit.LastSkillId = action.SourceId;
            if (action.Atk != null) unit.RecordUseById(action.Atk.Id);
            if (action.HasRandomMove)
            {
                foreach (int randomEffect in RANDOM_MOVES)
                {
                    if (action.Has(randomEffect))
                    {
                        action = RandomMove(action, randomEffect);
                        if (action == null) return;
                    }
                }
            }
            if (action.Has(228) || action.Has(229) || action.Has(230) || action.Has(231) || action.Has(232) || action.Has(233) || action.Has(146))
            {
                MakeDoll(action);
                return;
            }
            if (action.Has(GENJIMARU))
            {
                MakeGenjimaru(action);
                return;
            }
            if (unit.HasUnique && unit.UniqueEffect == 348 && action.Physical && Roll(unit.UniqueValue)) action.Furious = true;
            Unit[] targets = Targets(action);
            if (targets.Length == 0) return;
            // CActionPatternM0124 (Skill Pattern 13, Magic 230 Primevil; 0x42d1d0): rotate self-slot to end of target order.
            if (action.Skill != null && action.Pattern == 13 && targets.Length > 1)
            {
                int selfIdx = Array.IndexOf(targets, unit);
                if (selfIdx >= 0 && selfIdx < targets.Length - 1)
                {
                    var rot = new Unit[targets.Length];
                    int w = 0;
                    for (int i = 0; i < targets.Length; i++) if (i != selfIdx) rot[w++] = targets[i];
                    rot[w] = unit;
                    targets = rot;
                }
            }
            int hits = NumberOfHits(action);
            if (hits <= 0) return;
            if (action.TargetCode == T.RANDOM)
            {
                var pool = targets;
                if (action.Has(112))
                {
                    int k = Math.Min(pool.Length, Math.Max(1, hits));
                    var idx = Rng.SampleIndices(pool.Length, k);
                    targets = new Unit[idx.Length];
                    for (int i = 0; i < idx.Length; i++) targets[i] = pool[idx[i]];
                }
                else
                {
                    int count = Math.Max(1, hits);
                    targets = new Unit[count];
                    for (int i = 0; i < count; i++) targets[i] = pool[Rng.ChoiceIndex(pool.Length)];
                }
                hits = 1;
            }
            foreach (var t in targets)
            {
                // Counter Whip answers a physical action, never one of a doll, the summon or a guest (P7.3 of the audit)
                if (t.Side != unit.Side && t.Has(303) && !unit.Has(307) && action.Physical && !NotACandidate(unit))
                {
                    Counter(t, unit);
                    // 0x4208a0: if Counter Whip inflicts Freeze/Silence making the queued skill illegal, downgrade to 1-hit basic Attack.
                    if (unit.Alive && action.Skill != null &&
                        ((unit.St[114] != null && action.Skill.IsTechnique) || (unit.St[117] != null && action.Skill.IsMagic)))
                    {
                        action = new Action(unit, AKind.Attack, null, 1, t);
                        targets = new[] { t };
                        hits = 1;
                    }
                    break;
                }
            }
            covered.Clear();
            guarding.Clear();
            if (action.Physical)
            {
                for (int j = 0; j < targets.Length; j++)
                {
                    var t = targets[j];
                    bool repeated = false;                       // a unit that is aimed at twice rolls once
                    for (int q = 0; q < j; q++) if (targets[q] == t) { repeated = true; break; }
                    if (repeated) continue;
                    if (t.Side != unit.Side && t.Has(255) && Roll(t.Value(255))) guarding.Add(t);
                }
            }
            int index = 0;
            deferredCounter = null;
            abortHits = false;
            if (reprisalDirty) { Array.Clear(reprisal, 0, Units.Count); reprisalDirty = false; }
            if (arcaneDirty) { Array.Clear(arcaneDamage, 0, Units.Count); arcaneDirty = false; }
            damageByTarget = Rec != null ? new Dictionary<Unit, int>() : null;
            bool canRetarget = action.TargetCode == T.SINGLE || action.TargetCode == T.RANDOM || action.TargetCode == T.ALLY || action.TargetCode == T.RANDOM_ALLY;
            for (int ti = 0; ti < targets.Length && !abortHits; ti++)
            {
                var target = targets[ti];
                for (int h = 0; h < hits && !abortHits; h++)
                {
                    if (!CanFight(unit)) { abortHits = true; break; }
                    if (!CanFight(target) && !action.Has(105))
                    {
                        // 0x420560..0x420893: mid-action retarget fallback on single/random/ally scopes when target dies mid-multi-hit.
                        if (!canRetarget) break;
                        var pool = TargetableArray(target.Side);
                        if (pool.Length == 0) { abortHits = true; break; }
                        target = pool[Rng.ChoiceIndex(pool.Length)];
                    }
                    Resolve(action, target, index);
                    index++;
                }
            }
            for (int ci = 0; ci < covered.Count; ci++)
            {
                var (cover, count) = covered[ci];
                for (int j = 0; j < count; j++)
                {
                    var s = cover.St[171];
                    if (s != null && Roll(s.Value)) cover.PopStatus(171);
                }
            }
            guarding.Clear();
            // _CheckAfterAttackInterrupt 4-stage post-action chain (0x4247e0..0x4255be):
            // Stage 1: Support Shot (260) on plain non-doll attacks (runs inCounter=true against a living target from targets).
            if (!inCounter && unit.Kind != Kind.Doll && (action.Kind == AKind.Attack || (action.Atk != null && action.Atk.Plain)))
            {
                foreach (var ally in AlliesArray(unit))
                {
                    if (ally != unit && ally.Kind != Kind.Doll && ally.Has(260) && Roll(ally.Value(260)))
                    {
                        Unit first = null;
                        foreach (var t in targets) if (CanFight(t)) { first = t; break; }
                        if (first != null)
                        {
                            Action shot = new Action(ally, AKind.Attack);
                            if (ally.Kind != Kind.Member && ally.Attacks != null && ally.Attacks.Length > 0)
                            {
                                var atk0 = Data.GetAttack(ally.Attacks[0]);
                                if (atk0 != null) shot = new Action(ally, AKind.Enemy, atk0, 1);
                            }
                            inCounter = true;
                            try { Resolve(shot, first, 0); }
                            finally { inCounter = false; }
                        }
                        break;
                    }
                }
            }
            // Stage 2: Deferred Counter (250) on AoE (flag10=0) patterns — max 1 counter; suppresses Stages 3 (249) & 4 (447).
            bool deferredFired = false;
            var dc = deferredCounter;
            deferredCounter = null;
            if (!inCounter && dc != null && CanFight(dc) && CanFight(unit))
            {
                Counter(dc, unit);
                deferredFired = true;
            }
            // Stage 3: Reprisal (249; 0x424d50..0x424de7): front-row living target, !inCounter, skipped if Stage 2 fired.
            if (reprisalDirty)
            {
                if (!deferredFired && !inCounter)
                {
                    foreach (var target in targets)
                    {
                        if (reprisal[target.Position] && target.Front && target.Has(249) && CanFight(target))
                        {
                            Counter(target, unit);
                            break;
                        }
                    }
                }
                Array.Clear(reprisal, 0, Units.Count);
                reprisalDirty = false;
            }
            // Stage 4: Arcane Shield (447; 0x425157..0x42537c): runs AFTER Stage 3 Reprisal, skipped if Stage 2 fired.
            if (arcaneDirty)
            {
                bool fired = deferredFired;
                for (int ui = 0; ui < Units.Count; ui++)
                {
                    int stored = arcaneDamage[ui];
                    if (stored <= 0) continue;
                    arcaneDamage[ui] = 0;
                    if (fired) continue;
                    var bearer = Units[ui];
                    if (CanFight(bearer) && CanFight(unit) && bearer.HasUnique && bearer.UniqueEffect == 447)
                    {
                        LoseHp(unit, PyMath.Int(stored * bearer.UniqueValue), bearer);
                        fired = true;
                    }
                }
                arcaneDirty = false;
            }
            if (action.Has(SACRIFICE) && unit.Alive) LoseHp(unit, unit.MaxHp, unit);
            // Effect 12 (Self-Destruct; 0x44f14a..0x44f165): removes the enemy caster after the attack (not counted as a kill).
            if (action.Has(12) && unit.Kind == Kind.Enemy && unit.Alive)
            {
                unit.Alive = false;
                unit.Chant = null;
                unit.ClearStatuses();
                unit.ClearSongsAndDances();
            }
            if (damageByTarget != null)
            {
                foreach (var kv in damageByTarget)
                    if (unit.Side == Unit.ENEMIES && kv.Key.Side == Unit.PARTY) Rec.LargestHit.Max(new RecKey(unit), kv.Value);
                damageByTarget = null;
            }
        }

        static readonly Unit[] NoUnits = new Unit[0];

        /// <summary>A doll, the summon or a guest: numbered 2000 or more, never a candidate (0x43e6d0), never answered by a counter
        /// (0x43b5f0, 0x43b610).</summary>
        static bool NotACandidate(Unit u) => u.Kind == Kind.Doll || u.Kind == Kind.Summon || u.Kind == Kind.Npc;

        /// <summary>One unit of the actor's own side for scopes 5 and 7 (0x43f450): the unit given when it is still a candidate; a unit
        /// given that is not (dead) yields the candidate with the lowest HP ratio, the last of them on a tie (0x43f668 - 0x43f6e9);
        /// none given, an even roll among the candidates (0x43f7ba).</summary>
        Unit OwnSidePick(Unit chosen, Unit[] candidates)
        {
            if (candidates.Length == 0) return null;
            if (chosen != null)
            {
                if (Array.IndexOf(candidates, chosen) >= 0) return chosen;
                Unit lowest = null; double ratio = 1.0;
                foreach (var u in candidates) if (u.HpRatio <= ratio) { ratio = u.HpRatio; lowest = u; }
                return lowest ?? candidates[candidates.Length - 1];
            }
            return candidates[Rng.ChoiceIndex(candidates.Length)];
        }

        /// <summary>The units an action is aimed at, in order. The array may be one of the shared lists of a side: it must not be changed.</summary>
        Unit[] Targets(Action action)
        {
            if (action.FixedTargets != null)
            {
                var r = new List<Unit>();
                foreach (var t in action.FixedTargets) if (t.Alive || action.Has(105)) r.Add(t);
                return r.ToArray();
            }
            var unit = action.Actor;
            int code = action.TargetCode;
            var foes = TargetableArray(1 - unit.Side);
            // the candidates on the unit's own side: units numbered below 2000 (0x43e6d0), so never a doll, the summon or a guest ally;
            // an action that revives (105) or cures (106) leaves out the test of life, so fallen members are candidates too (0x56d570,
            // stored at +0x3a of the action and passed to 0x43af10 at 0x43ec49)
            var friends = action.Has(105) || action.Has(106) ? OwnSideAll(unit.Side) : TargetableArray(unit.Side);
            var chosen = action.Target;
            if (code == T.SINGLE || code == T.PIERCE || code == T.ROW)
            {
                if (chosen == null || !chosen.Alive || chosen.Side == unit.Side) chosen = PickOpponent(unit, action);
                if (chosen == null) return NoUnits;
                if (code == T.SINGLE)
                {
                    if (action.Has(EXTRA_TARGETS))
                    {
                        // 0x4201e0..0x4202f3: sort all living targetable units of BOTH sides by turn order; step forward from chosen and stop at opposite side.
                        var all = new List<Unit>();
                        foreach (var u in Units) if (u.Alive && !NotACandidate(u)) all.Add(u);
                        InsertionSortByTime(all);
                        var res = new List<Unit> { chosen };
                        int idx = all.IndexOf(chosen);
                        int extra = Math.Max(0, PyMath.Int(action.Val(EXTRA_TARGETS, 0)) - 1);
                        if (idx >= 0)
                        {
                            for (int step = 1; step <= extra && idx + step < all.Count; step++)
                            {
                                var nxt = all[idx + step];
                                if (nxt.Side != chosen.Side) break;
                                res.Add(nxt);
                            }
                        }
                        return res.ToArray();
                    }
                    return new[] { chosen };
                }
                if (code == T.ROW)
                {
                    var r = new List<Unit>();
                    foreach (var t in foes) if (t.Front == chosen.Front) r.Add(t);
                    return r.ToArray();
                }
                var p = new List<Unit> { chosen };
                foreach (var t in Behind(chosen)) if (Array.IndexOf(foes, t) >= 0) p.Add(t);
                return p.ToArray();
            }
            if (code == T.RANDOM) return foes;
            if (code == T.ALL) return foes;
            // everyone / anyone: the candidates of both sides, units below 2000 (0x43e6d0), never a doll, the summon or a guest
            if (code == T.EVERYONE)
            {
                var r = new List<Unit>();
                foreach (var u in Units) if (u.Alive && !NotACandidate(u)) r.Add(u);
                return r.ToArray();
            }
            if (code == T.ANYONE)
            {
                var r = new List<Unit>();
                foreach (var u in Units) if (u.Alive && !NotACandidate(u)) r.Add(u);
                return r.Count > 0 ? new[] { r[Rng.ChoiceIndex(r.Count)] } : NoUnits;
            }
            if (code == T.SELF || code == T.NO_TARGET) return new[] { unit };
            if (code == T.ALLY)
            {
                var one = OwnSidePick(chosen, friends);
                return one != null ? new[] { one } : NoUnits;
            }
            if (code == T.RANDOM_ALLY)
            {
                // a target given that is still a candidate is kept (0x43f5c2); otherwise an even roll
                if (chosen != null && Array.IndexOf(friends, chosen) >= 0) return new[] { chosen };
                return friends.Length > 0 ? new[] { friends[Rng.ChoiceIndex(friends.Length)] } : NoUnits;
            }
            if (code == T.ALLY_ROW)
            {
                var picked = OwnSidePick(chosen, friends);
                if (picked == null) return NoUnits;
                bool row = picked.Front;
                var r = new List<Unit>();
                foreach (var t in friends) if (t.Front == row) r.Add(t);
                return r.ToArray();
            }
            if (code == T.ALLIES) return friends;
            if (code == T.ALLY_MOST_TP_LOST)
            {
                Unit best = null;
                foreach (var u in friends) if (best == null || u.TpRatio < best.TpRatio) best = u;
                return new[] { best };
            }
            return new[] { unit };
        }

        static void InsertionSortByTime(List<Unit> list)
        {
            // stable sort by (next_time, tie key)
            for (int i = 1; i < list.Count; i++)
            {
                var x = list[i];
                int j = i - 1;
                while (j >= 0 && (list[j].NextTime > x.NextTime || (list[j].NextTime == x.NextTime && list[j].TieKey < x.TieKey)))
                {
                    list[j + 1] = list[j];
                    j--;
                }
                list[j + 1] = x;
            }
        }

        Unit PickOpponent(Unit unit, Action action)
        {
            var foes = TargetableArray(1 - unit.Side);
            if (foes.Length == 0) return null;
            if (unit.Side == Unit.ENEMIES) return WeightedPick(unit, foes);
            return foes[Rng.ChoiceIndex(foes.Length)];
        }

        public List<Unit> Behind(Unit unit)
        {
            if (unit.Side == Unit.ENEMIES && unit.Slot != T.NONE)
            {
                var r = new List<Unit>();
                foreach (var u in Units)
                    if (u.Side == Unit.ENEMIES && u.Kind == Kind.Enemy && u.Alive && u.Front != unit.Front && u.Slot != T.NONE && Math.Abs(u.Slot - unit.Slot) <= 1) r.Add(u);
                return r;
            }
            // rows by front flag, in the order of the units; a dict keyed by the flag (insertion order is not read)
            var mine = new List<Unit>(); var other = new List<Unit>();
            foreach (var u in Units)
            {
                if (u.Side == unit.Side && u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc)
                {
                    if (u.Front == unit.Front) mine.Add(u); else other.Add(u);
                }
            }
            int at = mine.IndexOf(unit);
            if (at < 0 || other.Count == 0) return new List<Unit>();
            double centre = at - (mine.Count - 1) / 2.0;
            var res = new List<Unit>();
            for (int j = 0; j < other.Count; j++)
                if (Math.Abs(j - (other.Count - 1) / 2.0 - centre) <= 0.5 && other[j].Alive) res.Add(other[j]);
            return res;
        }

        public List<Unit> Targetable(List<Unit> units)
        {
            var r = new List<Unit>(units.Count);
            foreach (var u in units) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) r.Add(u);
            return r;
        }

        static readonly int[] ShareRowEmpty = { 100 };
        // ShareRowTable[size, front]: row index into F.TARGET_SHARE for size 1..5, front 1..3 (size 5 front 1 falls back to max front=3 -> row 9).
        static readonly int[,] ShareRowTable =
        {
            { 0, 0, 0, 0 },
            { 0, 0, 0, 0 },  // size 1: front 1 -> 0
            { 0, 2, 1, 1 },  // size 2: front 1 -> 2, front 2 -> 1
            { 0, 5, 4, 3 },  // size 3: front 1 -> 5, front 2 -> 4, front 3 -> 3
            { 0, 8, 7, 6 },  // size 4: front 1 -> 8, front 2 -> 7, front 3 -> 6
            { 0, 9, 10, 9 }, // size 5: front 1 -> fallback max front(3)=9, front 2 -> 10, front 3 -> 9
        };

        static int[] TargetShareRow(int size, int front)
        {
            if (size == 0) return ShareRowEmpty;
            if (size > 5) return F.TARGET_SHARE[9];
            front = Math.Max(1, Math.Min(Math.Min(front, 3), size));
            return F.TARGET_SHARE[ShareRowTable[size, front]];
        }

        Unit[] pickOrdered;
        int[] pickWeights;

        Unit WeightedPick(Unit enemy, Unit[] party)
        {
            if (pickOrdered.Length < party.Length) { pickOrdered = new Unit[party.Length * 2]; pickWeights = new int[party.Length * 2]; }
            var ordered = pickOrdered;
            int count = 0, frontCount = 0;
            foreach (var u in party) if (u.Front) { ordered[count++] = u; frontCount++; }
            foreach (var u in party) if (!u.Front) ordered[count++] = u;
            var fallbackRow = TargetShareRow(count, frontCount);
            var weights = pickWeights;
            long total = 0;
            // 0x44a6ca..0x44a724: single active Provoke status (170) per enemy; fixed BaseTargetShare from battle start.
            var p170 = enemy.St[170];
            for (int k = 0; k < count; k++)
            {
                var u = ordered[k];
                int share = u.BaseTargetShare > 0 ? u.BaseTargetShare : (k < fallbackRow.Length ? fallbackRow[k] : fallbackRow[fallbackRow.Length - 1]);
                double provoked = (p170 != null && p170.Source == u) ? p170.Value : 0.0;
                weights[k] = F.TargetWeight(share, provoked, u.Pieces(49), u.Pieces(50));
                total += weights[k];
            }
            double roll = Rng.Random() * total;
            for (int k = 0; k < count; k++)
            {
                roll -= weights[k];
                if (roll < 0) return ordered[k];
            }
            return ordered[count - 1];
        }

        int NumberOfHits(Action action)
        {
            // 0x417da7..0x4180e3: starts at hits=0, any=false; each hit-count effect adds to hits and sets any=true;
            // Double/Triple Attack run only on plain attacks when !any; default hits=1 when !any.
            int hits = 0;
            bool any = false;
            int mhIdx = action.MultiHitIndex;
            bool has178 = action.Has(178) || action.Actor.Has(178);
            bool isPlain = action.Kind == AKind.Attack || (action.Atk != null && action.Atk.Plain);
            if (mhIdx >= 0)
            {
                bool rondo = action.Has(210) || action.Actor.Has(210);
                var m = MULTI_HIT[mhIdx];
                var table = rondo ? m.rondo : m.weights;
                double sum = rondo ? MultiHitRondoSum[mhIdx] : MultiHitWeightSum[mhIdx];
                hits += m.baseHits + WeightedWithSum(m.picks, table, sum);
                any = true;
            }
            if (action.TryVal(93, out double v93) && v93 != 0)
            {
                hits += PyMath.Int(v93);
                any = true;
            }
            // 0x417ffe: Charge/Focusing (178) lives in the merged actor+action command list and adds int(v)+1.
            if (has178)
            {
                hits += PyMath.Int(First(action, action.Actor, 178)) + 1;
                any = true;
            }
            // 0x417d7f..0x418045: Double/Triple Attack apply on player Attack and plain enemy/guest/summon attacks (+0x40 & 1), skipped when any hit effect fired.
            if (isPlain && !any)
            {
                int extra = 0;
                if (action.Actor.Has(252) && Roll(action.Actor.Value(252))) extra += 3;
                if (action.Actor.Has(251) && Roll(action.Actor.Value(251))) extra += 2;
                if (extra != 0) { hits += extra; any = true; }
            }
            if (!any) hits = 1;
            // 0x417cd0: Effect 94 (Danger Shoot + 17 EnemyAttacks) can legitimately roll 0 hits without Rondo (210).
            return Math.Max(0, hits);
        }

        int WeightedWithSum(int[] picks, double[] weights, double total)
        {
            double roll = Rng.Random() * total;
            for (int i = 0; i < picks.Length && i < weights.Length; i++)
            {
                roll -= weights[i];
                if (roll < 0) return picks[i];
            }
            return picks[picks.Length - 1];
        }

        int Weighted(int[] picks, double[] weights)
        {
            var s = new PySum();
            foreach (var w in weights) s.AddFloat(w);
            double roll = Rng.Random() * s.Result;
            for (int i = 0; i < picks.Length && i < weights.Length; i++)
            {
                roll -= weights[i];
                if (roll < 0) return picks[i];
            }
            return picks[picks.Length - 1];
        }

        // --- one hit -----------------------------------------------------------------------------------------
        static bool Aimed(Action action, Unit target)
        {
            int c = action.TargetCode;
            return target.Side != action.Actor.Side || T.OwnSide(c) || c == T.EVERYONE || c == T.ANYONE;
        }

        void Resolve(Action action, Unit target, int index)
        {
            var unit = action.Actor;
            bool hostile = target.Side != unit.Side;
            if (hostile)
            {
                target = Redirect(action, target);
                if (target == null) return;
                bool landed = Hits(action, target);
                Trace?.Hit(this, action, target, landed);
                if (!landed)
                {
                    // 0x421ab9..0x421ade, 0x44f0a0: a missed damaging spell (incl. special-damage magic) still checks Voided,
                    // deals grazed (or full special) damage, and runs AfterHit (ailments, drains, reactive triggers).
                    if (!action.Magic || !Aimed(action, target) || action.Has(25) || Voided(action, target)) return;
                    int preHpMiss = target.Hp;
                    spellMissed = true;
                    int grazed;
                    try { grazed = Damage(action, target, index); }
                    finally { spellMissed = false; }
                    // 0x422b6e: Magic Barrier (183) is consumed on any non-voided magical hit (incl. grazed spell).
                    if (target.St[183] != null) target.PopStatus(183);
                    lastDealtDamage = grazed;
                    if (damageByTarget != null) { damageByTarget.TryGetValue(target, out int had); damageByTarget[target] = had + grazed; }
                    AfterHit(action, target, grazed, preHpMiss);
                    return;
                }
                if (Voided(action, target)) return;
            }
            int preHp = target.Hp;
            int dealt = 0;
            // 0x44bf19 / 0x44eb25: Effect 87 (Only Damages Living) voids damage AND AfterHit/Murder against Undead (5) and Inorganic/Magic Being (6, incl. Ist).
            if (action.Has(87) && (target.Race == 5 || target.Race == 6)) return;
            if (Aimed(action, target) && !action.Has(25) && (action.Physical || action.Magic))
            {
                dealt = Damage(action, target, index);
                // 0x422b58..0x422b6e: consume 1-hit Material Guard (179) on physical hit and Magic Barrier (183) on magical hit.
                if (action.Physical && target.St[MATERIAL_GUARD] != null) target.PopStatus(MATERIAL_GUARD);
                else if (action.Magic && target.St[183] != null) target.PopStatus(183);
                lastDealtDamage = dealt;
                if (damageByTarget != null) { damageByTarget.TryGetValue(target, out int sofar); damageByTarget[target] = sofar + dealt; }
            }
            AfterHit(action, target, dealt, preHp);
        }

        static int[] SnapshotStatuses(Unit u, int[] scratch, out int count)
        {
            count = u.StCount;
            if (count == 0) return Array.Empty<int>();
            var buf = count <= scratch.Length ? scratch : new int[count];
            for (int i = 0; i < count; i++) buf[i] = u.StatusAt(i);
            return buf;
        }

        Unit Redirect(Action action, Unit target)
        {
            int c = action.TargetCode;
            // 0x420b70: Cover (171) only redirects physical actions (effect ID 0), never magic or pure status attacks.
            if (action.Physical && (c == T.SINGLE || c == T.RANDOM))
            {
                redirectScratch.Clear();
                var covers = redirectScratch;
                // only units below 2000 can cover (P5.5 of the audit): never a doll, the summon or a guest
                foreach (var u in TargetableArray(target.Side)) if (u != target && u.St[171] != null && u.Alive) covers.Add(u);
                if (covers.Count > 0)
                {
                    var cover = covers[Rng.ChoiceIndex(covers.Count)];
                    if (covered != null)
                    {
                        int at = -1;
                        for (int q = 0; q < covered.Count; q++) if (covered[q].unit == cover) { at = q; break; }
                        if (at >= 0) covered[at] = (cover, covered[at].count + 1); else covered.Add((cover, 1));
                    }
                    return cover;
                }
            }
            return target;
        }

        /// <summary>0x422640: pattern flag10=1 (sequential A/B/C/T0105/M0140) vs flag10=0 (AoE D/E/F/G/M0124).</summary>
        static bool IsSequentialPattern(Action action)
        {
            int p = action.Pattern;
            if (action.Skill != null && p != 0)
                return p == 1 || p == 2 || p == 3 || p == 8 || p == 14;
            if (action.Atk != null && p != 0)
                return p == 1 || p == 2 || p == 3 || p == 15;
            int c = action.TargetCode;
            return c == T.SINGLE || c == T.RANDOM;
        }

        bool Voided(Action action, Unit target)
        {
            var unit = action.Actor;
            int attr = action.Attr;
            int physAttr = action.PhysicalAttr;
            if (target.HasNullifyEnchant)
            {
                // NULLIFY_ENCHANTS: 120..123 check PhysicalAttr (Slash/Stab/Bash without element overrides); 124..128 check Attr (Fire..Lightning).
                for (int enchant = 120; enchant <= 128; enchant++)
                {
                    if (target.Pieces(enchant) != 0)
                    {
                        bool blowsOnly = enchant <= 123;
                        bool attrMatch = enchant == 123 ? T.Physical(physAttr) : enchant <= 122 ? physAttr == enchant - 119 : attr == enchant - 120;
                        if (attrMatch && (action.Physical || !blowsOnly)) return true;
                    }
                }
            }
            if (target.Has(192) && attr != T.NEUTRAL) return true;
            // 0x421c40: Range Immunity (182) applies ONLY to physical attacks (action.Physical).
            if (target.Has(182) && action.Physical && (action.Reach == T.SHORT || action.Reach == T.MID)) return true;
            // Alter Fate (349; 0x421ca7..0x421db3): full hit void right after 182 and BEFORE counters, barriers, dispel, and AfterHit.
            if (target.HasUnique && target.UniqueEffect == 349 && Roll(target.UniqueValue)) return true;
            // 0x4221ee: Pretend (310) voids physical hit without launching a counterattack.
            if (target.Has(PRETEND) && action.Physical && Roll(target.Value(PRETEND)))
                return true;
            if (target.Has(285) && !spent.Contains((target, 285)) && (action.Physical || action.Magic))
            {
                target.PopStatus(285);
                spent.Add((target, 285));
                return true;
            }
            // Knock Down (305; 0x42222c..0x422246): voids long-range physical hit without launching a counterattack.
            if (target.Has(KNOCK_DOWN) && action.Physical && action.Reach == T.LONG &&
                (target.Kind != Kind.Member || target.Weapon != null) && Roll(target.Value(KNOCK_DOWN)))
                return true;
            // Parry (180; 0x4223b5..0x4223d9): requires physical action with non-neutral attribute.
            if (target.St[180] != null && action.Physical && attr != T.NEUTRAL)
            {
                if (Roll(target.St[180].Value)) target.PopStatus(180);
                return true;
            }
            // Counter / Mind's Eye (250; 0x422540..0x42265f): physical Short/Mid only, !inCounter, !307.
            // Sequential patterns (flag10=1) counter immediately and abort remaining multi-hits; AoE (flag10=0) defers to Stage 2.
            if (!inCounter && action.Physical && target.Has(250) && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
            {
                if (Roll(target.Value(250)))
                {
                    if (IsSequentialPattern(action))
                    {
                        Counter(target, unit);
                        abortHits = true;
                    }
                    else if (deferredCounter == null)
                    {
                        deferredCounter = target;
                    }
                    return true;
                }
            }
            for (int k = 0; k < 3; k++)
            {
                int effect = k == 0 ? 101 : k == 1 ? 102 : 181;
                var s = target.St[effect];
                if (s != null && !(action.Has(140) || action.Has(141) || action.Has(142)) && (action.Physical || action.Magic))
                {
                    s.Value -= 1;
                    if (s.Value <= 0) target.PopStatus(effect);
                    return true;
                }
            }
            return false;
        }

        bool Hits(Action action, Unit target)
        {
            if (action.Furious) return true;
            double chance = HitChance(action, target);
            double dodge = StabDodge(action, target);
            int roll = Rng.RandRange(100);
            // 0x44abe9, 0x44b12a: Stab Evasion (253) only lowers physical hit rate (no free counterattack).
            return roll < PyMath.Round((chance - dodge) * 100);
        }

        double First(Action action, Unit unit, int effect)
        {
            if (action.Has(effect))
            {
                double v = action.Val(effect, 0);
                return v != 0 ? v : 0.0;
            }
            return unit.Value(effect);
        }

        // the terms of a sum(): an int of the data is added as an int, as CPython does (no compensation for it)
        static void AddStatus(ref PySum s, Unit u, int e)
        {
            var st = u.St[e];
            if (st == null) s.AddFloat(0.0);
            else if (st.IsInt) s.AddInt((long)st.Value);
            else s.AddFloat(st.Value);
        }

        static void AddValue(ref PySum s, Unit u, int e)
        {
            var st = u.St[e];
            if (st != null)
            {
                if (st.IsInt) s.AddInt((long)st.Value); else s.AddFloat(st.Value);
            }
            else if (u.HasPassive(e))
            {
                if (u.PassiveIsInt(e)) s.AddInt((long)u.Pv[e]); else s.AddFloat(u.Pv[e]);
            }
            else s.AddFloat(0.0);
        }

        static void AddFirst(ref PySum s, Action action, Unit unit, int e)
        {
            if (action.Has(e))
            {
                double v = action.Val(e, 0);
                if (v == 0) s.AddFloat(0.0);                    // value or 0.0
                else if (action.ValIsInt(e)) s.AddInt((long)v);
                else s.AddFloat(v);
            }
            else AddValue(ref s, unit, e);
        }

        static double SumStatus(Unit u, int[] effects)
        {
            if (u.StCount == 0) return 0.0;
            var s = new PySum();
            for (int i = 0; i < effects.Length; i++) AddStatus(ref s, u, effects[i]);
            return s.Result;
        }

        double SumFirst(Action action, Unit unit, int[] effects)
        {
            var s = new PySum();
            for (int i = 0; i < effects.Length; i++) AddFirst(ref s, action, unit, effects[i]);
            return s.Result;
        }

        static double SumValue(Unit u, int[] effects)
        {
            if (u.StCount == 0 && !u.HasPassives) return 0.0;
            var s = new PySum();
            for (int i = 0; i < effects.Length; i++) AddValue(ref s, u, effects[i]);
            return s.Result;
        }

        double CriticalRateOf(Action action, Unit unit, Unit target, int earlier)
        {
            var s = new PySum();
            foreach (int e in CRIT_TERMS)
            {
                // 0x43e970: merged action+unit command list sums skill effect 31 with unit status/passive effect 31 (Last Stand).
                if (e == 31) { if (action.Has(31)) s.AddFloat(action.Val(31, 0.0)); AddValue(ref s, unit, 31); }
                else AddFirst(ref s, action, unit, e);
            }
            double skill = s.Result + target.Value(32);
            bool hasFixed = action.TryVal(70, out double fixedValue);
            return F.CriticalRate(unit.Stat(Unit.DEX), target.Stat(Unit.AGI), unit.Level, target.Level, skill,
                                  F.CriticalEnchant(unit.Pieces(45), unit.Pieces(46)),
                                  -F.CriticalEnchant(target.Pieces(47), target.Pieces(48)), earlier, unit.Pieces(268) != 0,
                                  hasFixed, fixedValue);
        }

        bool Critical(Action action, Unit target, int index)
        {
            var unit = action.Actor;
            if (target.Side == Unit.ENEMIES && action.Has(110) && target.Race == 2) return true;
            int earlier = action.Has(125) ? index : 0;
            double rate = CriticalRateOf(action, unit, target, earlier);
            return Rng.RandRange(100) < PyMath.Int(rate);
        }

        public bool Special(Action action) => action.IsSpecial;

        int Damage(Action action, Unit target, int index)
        {
            int amount = DamageInner(action, target, index);
            Trace?.Damage(this, action, target, amount);
            return amount;
        }

        int DamageInner(Action action, Unit target, int index)
        {
            bool critical = false;
            int amount;
            bool special = Special(action);
            if (special) amount = SpecialDamage(action, target);
            else if (action.Magic)
            {
                amount = MagicDamageActual(action, target, out critical);
            }
            else
            {
                critical = Critical(action, target, index);
                amount = PhysicalDamageActual(action, target, index, critical);
            }
            if (!special)
            {
                Unit wall = DemonWallOf(target, action.Actor);
                if (wall != null) amount = Math.Max(0, PyMath.Int(amount + amount * wall.Value(DEMON_WALL)));
                var actor = action.Actor;
                int ptThresh = Options.PositiveTranceThreshold ?? Data.PositiveTranceThreshold;
                if (!action.Magic && actor.HasUnique && actor.UniqueEffect == 440 && actor.Pep > ptThresh)
                    amount += PyMath.Int(amount * (actor.Pep - ptThresh) / Math.Max(1.0, actor.UniqueValue) / 100.0);
            }
            if (target.St[116] != null && !special) amount = amount * F.SLEEP_NUM / F.SLEEP_DEN;
            if (!special && action.Actor.Pieces(F.AILING_ENCHANT) != 0 && HasTrueAilment(target)) amount += PyMath.Int(amount * F.AILING_SHARE);
            if (action.Has(86) && target.Kind == Kind.Member && target.ClassId >= F.MAGIC_USER_LOW && target.ClassId < F.MAGIC_USER_HIGH) amount += amount;
            // 0x44f0a0 -> 0x44f0ce: damage cap (296) applies after special damage too (e.g. Heaven or Hell Effect).
            if (action.TryVal(296, out double cap)) amount = Math.Min(amount, PyMath.Int(cap));
            if (action.Has(2))
            {
                target.Tp = Math.Max(0, target.Tp - amount);
                return amount;
            }
            TakeDamage(target, amount, action, critical);
            if (critical && action.Physical && target.Alive && (action.Has(MURDER) || action.Actor.Has(MURDER)))
                ApplyAilment(action.Actor, target, 119, First(action, action.Actor, MURDER), action);
            return amount;
        }

        /// <summary>Demon Wall (356) lowers only the blows of an enemy of race 5, 7 or 8 (0x44cb6c - 0x44cba2; races read at
        /// 0x557e1c, 0x557e7c, 0x557eac); the wall is the first living same-row ally bearing 356 (0x44cbb9, 0x44ef26, 0x43e759).</summary>
        Unit DemonWallOf(Unit target, Unit attacker)
        {
            if (!anyDemonWall || attacker.Side != Unit.ENEMIES || attacker.Kind != Kind.Enemy || F.DEMON_WALL_RACES.IndexOf(attacker.Race) < 0) return null;
            for (int i = 0; i < Units.Count; i++)
            {
                var u = Units[i];
                if (u.Side == target.Side && u.Alive && u.Front == target.Front && u.Has(DEMON_WALL)) return u;
            }
            return null;
        }

        static bool AnyAilment(Unit u)
        {
            if (u.StCount == 0) return false;
            var ids = AILMENT_IDS;
            for (int i = 0; i < ids.Length; i++) if (u.St[ids[i]] != null) return true;
            return false;
        }

        // 0x4faf20 -> 0x4faf90 -> vtable+0x68: true for ailments 113..122, false for Shadow Sew (123; 0x4151f0).
        public static bool HasTrueAilment(Unit u)
        {
            if (u.StCount == 0) return false;
            var ids = AILMENT_IDS;
            for (int i = 0; i < ids.Length; i++)
            {
                int id = ids[i];
                if (id != 123 && u.St[id] != null) return true;
            }
            return false;
        }

        public static int CountTrueAilments(Unit u)
        {
            if (u.StCount == 0) return 0;
            int n = 0;
            var ids = AILMENT_IDS;
            for (int i = 0; i < ids.Length; i++)
            {
                int id = ids[i];
                if (id != 123 && u.St[id] != null) n++;
            }
            return n;
        }

        int CountAilments(Unit u)
        {
            if (u.StCount == 0) return 0;
            int n = 0;
            var ids = AILMENT_IDS;
            for (int i = 0; i < ids.Length; i++) if (u.St[ids[i]] != null) n++;
            return n;
        }

        public double PhysicalDamageValue(Action action, Unit target, int index, double critFactor, bool expect, bool critical, out int immediateZero)
        {
            immediateZero = 0;
            var unit = action.Actor;
            bool furious = action.Furious;
            // 0x43e970: merged action+unit command list sums skill effect 26 with unit status/passive effect 26 (Berserk/Defender/HRHR).
            double modifiers = (action.Has(26) ? action.Val(26, 0.0) : 0.0) + unit.Value(26) + (action.Atk != null ? action.Atk.Power : 0.0) + SumStatus(unit, ATTACK_STATUS_MODIFIERS);
            // Elbow Grease (443; 0x44b3b4..0x44b434): gated on effect 26 (skill power / Berserk); 20% proc per hit.
            if (unit.HasUnique && unit.UniqueEffect == 443 && (action.Has(26) || unit.Has(26)))
            {
                if (expect) modifiers += 0.20 * unit.UniqueValue;
                else if (Rng.RandRange(100) < 20) modifiers += unit.UniqueValue;
            }
            if (IsPuppet(unit) && unit.Owner != null)
                modifiers += unit.Owner.Passive(286, 0.0) + Math.Min(0.05, 0.02 * unit.Owner.Pieces(304) + 0.01 * unit.Owner.Pieces(305));
            if (action.Has(111) && unit.Weapon != null && unit.Weapon.TwoHanded && unit.Weapon.Type == 3) modifiers += action.Val(111, 0);
            double swing = expect ? 0.0 : Swing(unit);
            double atk = unit.Stat(Unit.ATK);
            if (action.Has(49)) atk = unit.Stat(Unit.INT);
            if (action.Has(47)) atk = unit.Stat(Unit.RES);
            if (action.Has(50)) atk = atk * action.Val(50, 0);
            double targetMods = SumStatus(target, DEFENCE_MODIFIERS);
            double times = action.Val(73, 1.0); if (times == 0) times = 1.0;
            int reach = action.Reach;
            int dist = F.Distance(!unit.Front, !target.Front);
            double cut = target.HasEnchants ? 1.0 - (0.10 * target.Pieces(66) + 0.05 * target.Pieces(67) + 0.08 * target.Pieces(70) + 0.04 * target.Pieces(71)) : 1.0;
            bool defending = target.Defending || (guarding.Count > 0 && guarding.Contains(target));
            int resistIndex = T.ResistIndex(action.Attr);
            int resistance = resistIndex >= 0 ? target.Resistance(resistIndex) : 0;
            double raceBonus = (action.Has(88) && (target.Race == 5 || target.Race == 7 || target.Race == 8)) ? action.Val(88, 0) : 0.0;
            // 0x44bf19..0x44bf44 -> 0x557ef0: effect 87 (only living targets) returns 0 against Race 5 (Undead) and Race 6 (Inorganic).
            if (action.Has(87) && (target.Race == 5 || target.Race == 6)) { immediateZero = 1; return 0; }
            double race = (RaceFactor(unit, target) + raceBonus) * ElementFactor(unit, target, action.Attr);
            // 0x44c720: Power Charge (191) does NOT apply during counterattacks (!inCounter).
            double other = target.Value(190) + (inCounter ? 0.0 : unit.StatusValue(191)) + FullHpBonus(unit) + LevelBonus(unit, target);
            var guard = target.St[MATERIAL_GUARD];
            if (guard != null && (guard.Source == null || (guard.Source.Alive && guard.Source.Shield))) other += guard.Value;
            if (target.Side == Unit.PARTY && !target.Front)
            {
                bool any = false; double min = 0;
                foreach (var m in AlliesArray(target))
                {
                    // 0x44c780..0x44c790 -> 0x43aef0(row=1): Imperial Guard (308) requires a front-row shield-bearer.
                    double g = m.Passive(308, 0.0);
                    if (m.Front && m.HasPassive(308) && (m.Kind != Kind.Member || m.Shield) && g != 0.0) { if (!any || g < min) { min = g; any = true; } }
                }
                if (any) other += min;
            }
            // Positive Trance is an integer step after the cut (0x44ccb2, P6.9 of the audit); the expectation keeps it in the bonus
            int ptThreshExp = Options.PositiveTranceThreshold ?? Data.PositiveTranceThreshold;
            if (expect && unit.HasUnique && unit.UniqueEffect == 440 && unit.Pep > ptThreshExp)
                other += (unit.Pep - ptThreshExp) / Math.Max(1.0, unit.UniqueValue) / 100.0;
            if (action.Has(136)) other += action.Val(136, 0) * index;
            if (action.Has(DARK_QUEST) || unit.Has(DARK_QUEST))
                other += First(action, unit, DARK_QUEST) * CountTrueAilments(unit);
            if (action.Has(71))
            {
                // 0x44c640..0x44c663: counts only the 22 stat buff/debuff statuses (StatEffect71).
                int n = 0;
                for (int i = 0; i < target.StCount; i++) if (StatEffect71[target.StatusAt(i)]) n++;
                other += action.Val(71, 0) * n;
            }
            // 0x44c91e: enchant 267 adds +0.10 * (5 - partyCount) per piece for small parties.
            if (unit.Kind == Kind.Member && unit.HasEnchants && unit.Pieces(267) != 0)
                other += 0.10 * Math.Max(0, 5 - initialPartyCount) * unit.Pieces(267);
            double attackZone = ZoneFactor(unit, action);
            double value = F.PhysicalDamage(atk * attackZone, target.Stat(Unit.DEF), modifiers, targetMods,
                                            Math.Min(50, 4 * unit.Pieces(29) + 2 * unit.Pieces(30)),
                                            Math.Min(50, 4 * target.Pieces(33) + 2 * target.Pieces(34)),
                                            swing, times, action.Has(69) || furious, F.RangeFactor(reach, dist), cut, race, resistance,
                                            defending, expect ? critFactor : (critical ? F.CRIT_FACTOR : 1.0), other);
            // 0x44caea: Warning Shot (259) scales physical damage by 3 / 10 (0.3x).
            if (action.WarningShot) value *= 0.3;
            return value;
        }

        int PhysicalDamageActual(Action action, Unit target, int index, bool critical)
        {
            double value = PhysicalDamageValue(action, target, index, 1.0, false, critical, out int zero);
            if (zero == 1) return 0;
            int damage = PyMath.Int(value);
            if (damage <= 0) damage = critical ? 1 + Rng.ChoiceIndex(2) : F.MIN_DAMAGE;
            return damage;
        }

        /// <summary>physical_damage(expect=True): the mean of the rolls; max(3.0, value) or 0 for the immune case.</summary>
        public double PhysicalDamageExpected(Action action, Unit target, double critFactor)
        {
            double value = PhysicalDamageValue(action, target, 0, critFactor, true, false, out int zero);
            if (zero == 1) return 0;
            return Math.Max((double)F.MIN_DAMAGE, value);
        }

        double MagicValue(Action action, Unit target, bool expect, double critical, bool didCritical, out int immediateZero)
        {
            immediateZero = 0;
            // 0x44eb25..0x44eb56 -> 0x557ef0: effect 87 (only living targets) zeroes magic damage against Race 5 (Undead) and Race 6 (Inorganic).
            if (action.Has(87) && (target.Race == 5 || target.Race == 6)) { immediateZero = 1; return 0.0; }
            var unit = action.Actor;
            double power = action.Val(MAGIC_POWER, 0.0);
            if (IsPuppet(unit) && unit.Owner != null)
            {
                var owner = unit.Owner;
                power += DOLL_MAGIC_SCALE * (owner.Passive(286, 0.0) + Math.Min(0.05, 0.02 * owner.Pieces(304) + 0.01 * owner.Pieces(305)));
            }
            double mastery = unit.Passive(244, 0.0);
            double modifiers;
            {
                var s = new PySum(); AddValue(ref s, unit, 195); AddValue(ref s, unit, 335); modifiers = s.Result;
            }
            double second = unit.Value(212);
            int attr = action.Attr;
            double elementBoost = 0.0;
            if (attr >= T.FIRE && attr <= T.LIGHTNING)
            {
                int status, enchant;
                switch (attr)
                {
                    case T.FIRE: status = 325; enchant = 78; break;
                    case T.WATER: status = 326; enchant = 79; break;
                    case T.WIND: status = 328; enchant = 80; break;
                    case T.EARTH: status = 329; enchant = 81; break;
                    default: status = 327; enchant = 82; break;
                }
                int both = F.BothSidesElement(attr);
                elementBoost = Math.Min(F.ELEMENT_BOOST_CAP, F.ELEMENT_ENCHANT_SHARE * ((unit.St[status] != null ? 1 : 0) + unit.Pieces(enchant) + target.Pieces(enchant) + unit.Pieces(both) + target.Pieces(both)));
            }
            int resistIndex = T.ResistIndex(attr);
            int resistance = resistIndex >= 0 ? target.Resistance(resistIndex) : 0;
            double powerBoost = First(action, unit, 27) + First(action, unit, 173);
            double cut = (target.HasEnchants ? Math.Max(-0.25, -(0.10 * target.Pieces(68) + 0.05 * target.Pieces(69) + 0.08 * target.Pieces(70) + 0.04 * target.Pieces(71))) : 0.0) + target.StatusValue(183);
            // 0x44eabb..0x44eb20, 0x44eb59..0x44ebe1, 0x44ed53: RaceGuard (-guard), effect 88 (+bonus vs races 5/7/8),
            // and Limit Field (190) are all additive inside [ebp+0x44] (other) before multiplying by (1 + other).
            double other = target.Value(190) + (RaceGuard(unit, target) - 1.0) + FullHpBonus(unit) + LevelBonus(unit, target);
            if (action.Has(88) && (target.Race == 5 || target.Race == 7 || target.Race == 8))
                other += action.Val(88, 0.0);
            // 0x44ebe1: enchant 267 adds +0.10 * (5 - partyCount) per piece for small parties.
            if (unit.Kind == Kind.Member && unit.HasEnchants && unit.Pieces(267) != 0)
                other += 0.10 * Math.Max(0, 5 - initialPartyCount) * unit.Pieces(267);
            double targetMods = SumValue(target, MAGIC_DEFENCE_MODIFIERS);
            // the swing of a spell is the spell's own (0x44dbc3 - 0x44dc18), never the caster's weapon; an enemy attack has none
            double swing = expect || action.Skill == null ? 0.0 : SwingOf(action.Skill.Swing);
            // 0x44dc50..0x44dc8e: effect 47 (Damage based on RES) switches magic stat from INT to RES (Prism Dawn).
            double magicStat = action.Has(47) ? unit.Stat(Unit.RES) : unit.Stat(Unit.INT);
            return F.MagicDamage(magicStat * ZoneFactor(unit, action), power, target.Stat(Unit.RES), mastery, modifiers,
                                 Math.Min(50, 4 * unit.Pieces(37) + 2 * unit.Pieces(38)), second, elementBoost, targetMods,
                                 Math.Min(50, 4 * target.Pieces(41) + 2 * target.Pieces(42)), swing, powerBoost, cut, resistance,
                                 critical, other);
        }

        bool spellMissed;       // the spell being dealt missed its roll (Hits): its damage is cut, it cannot be critical

        int MagicDamageActual(Action action, Unit target, out bool critical)
        {
            var unit = action.Actor;
            critical = !spellMissed && unit.Has(301) && Rng.RandRange(100) < F.MAGIC_CRIT_CHANCE;
            double value = MagicValue(action, target, false, critical ? F.MAGIC_CRIT_FACTOR : 1.0, critical, out int zero);
            if (zero == 1) return 0;
            int amount = PyMath.Int(value);
            // a missed spell: half of it, three quarters with enchantment 272 (0x44ee33 - 0x44ee5d, divisions toward zero);
            // a spell at 0 or less strikes for 1 to 5 (0x44ee70 - 0x44ee81)
            if (spellMissed) amount = unit.Pieces(F.MISSED_SPELL_ENCHANT) != 0 ? amount * 3 / 4 : amount / 2;
            if (amount <= 0) amount = Rng.RandRange(F.SPELL_FLOOR_ROLL) + 1;
            return amount;
        }

        public double MagicDamageExpected(Action action, Unit target)
        {
            var unit = action.Actor;
            double critical = unit.Has(301) ? 1.0 + (F.MAGIC_CRIT_FACTOR - 1.0) * F.MAGIC_CRIT_CHANCE / 100.0 : 1.0;
            double value = MagicValue(action, target, true, critical, false, out int zero);
            if (zero == 1) return 0.0;
            double damage = value < 1.0 ? (F.SPELL_FLOOR_ROLL + 1) / 2.0 : value;      // the mean of the roll of 1 to 5
            if (action.TryVal(296, out double cap)) damage = Math.Min(damage, (double)PyMath.Int(cap));
            return damage;
        }

        // --- what the policies ask ---------------------------------------------------------------------------
        public double HitChance(Action action, Unit target)
        {
            var unit = action.Actor;
            int roll = action.HitRoll;
            if (roll == 0) return 1.0;
            double chance;
            if (roll == 2)
            {
                double acc;
                if (action.Skill != null && action.Skill.Accuracy != null && action.Skill.Accuracy.Length > 0)
                    acc = action.Skill.Accuracy[Math.Min(action.Level, action.Skill.Accuracy.Length) - 1];
                else
                    acc = action.Atk != null ? action.Atk.Accuracy : 0.0;
                double buffs = SumFirst(action, unit, MAGIC_ACCURACY_BUFFS);
                if (action.Skill != null && action.Skill.Id == LULLABY) buffs += SumFirst(action, unit, LULLABY_ACCURACY);
                double divisor = 1.0;
                foreach (int e in MAGIC_HIT_DIVISORS) if (target.Has(e)) { divisor = target.Value(e); break; }
                if (divisor == 0) divisor = 1.0;
                chance = F.MagicHit(acc, unit.Stat(Unit.INT), target.Stat(Unit.RES), First(action, unit, 30),
                                    Math.Min(50, 3 * unit.Pieces(39) + unit.Pieces(40)), Math.Min(50, 3 * target.Pieces(43) + target.Pieces(44)),
                                    buffs, SumValue(target, MAGIC_EVASION_BUFFS), divisor);
            }
            else
            {
                double skillAcc;
                if (action.Skill != null) skillAcc = action.Val(29, 0.0);
                else skillAcc = action.Atk != null ? action.Atk.Accuracy : 0.0;
                chance = F.PhysicalHit(unit.Stat(Unit.DEX), target.Stat(Unit.AGI), skillAcc, SumFirst(action, unit, ACCURACY_BUFFS),
                                       SumValue(target, EVASION_BUFFS), Math.Min(50, 4 * unit.Pieces(31) + 2 * unit.Pieces(32)),
                                       Math.Min(50, 4 * target.Pieces(35) + 2 * target.Pieces(36)), 1.0 + target.Value(221));
            }
            if (action.Has(55)) chance = action.Val(55, 0) * 100;
            else if (action.Has(72)) chance = action.Val(72, 0) * 100;
            if (roll == 1) chance = F.Clamp(chance, F.HIT_MIN, F.HIT_MAX);
            if (target.St[116] != null) chance = 100.0;
            // 0x44b01e..0x44b099 & 0x44db15: 149 (Four-Letter Word) misses adults (flag&1!=0); 150 (drinking) misses minors (flag&1==0).
            if (action.Has(149) && target.Adult) chance = 0.0;
            if (action.Has(150) && !target.Adult) chance = 0.0;
            return PyMath.Int(chance) / 100.0;
        }

        double StabDodge(Action action, Unit target)
        {
            if (!(action.Physical && action.PhysicalAttr == T.STAB && target.Has(STAB_EVASION)) || action.Furious) return 0.0;
            if (action.Has(55) || action.Has(72) || target.St[116] != null) return 0.0;
            var unit = action.Actor;
            double skillAcc = action.Skill != null ? action.Val(29, 0.0) : (action.Atk != null ? action.Atk.Accuracy : 0.0);
            double buffs = SumFirst(action, unit, ACCURACY_BUFFS);
            double enchant = Math.Min(50, 4 * unit.Pieces(31) + 2 * unit.Pieces(32));
            double targetEnchant = Math.Min(50, 4 * target.Pieces(35) + 2 * target.Pieces(36));
            double divisor = 1.0 + target.Value(221);
            double evasion = SumValue(target, EVASION_BUFFS);
            double full = F.PhysicalHit(unit.Stat(Unit.DEX), target.Stat(Unit.AGI), skillAcc, buffs, evasion, enchant, targetEnchant, divisor);
            double less = F.PhysicalHit(unit.Stat(Unit.DEX), target.Stat(Unit.AGI), skillAcc, buffs, evasion + target.Value(STAB_EVASION), enchant, targetEnchant, divisor);
            return Math.Max(0.0, PyMath.Int(full) - PyMath.Int(less)) / 100.0;
        }

        public double ExpectedDamage(Action action, Unit target)
        {
            if (!edActive) return ExpectedDamageUncached(action, target);
            // within one decision of a policy nothing changes between the questions: an action of the same user, source and level asked about
            // the same target has the same answer, however many Action objects the policy made for it
            int source = action.Skill != null ? action.Skill.Id : action.Atk != null ? action.Atk.Id : 0;
            int type = action.Skill != null ? 1 : action.Atk != null ? 2 : action.Kind == AKind.Attack ? 3 : 0;
            long key = ((((long)action.Actor.Position * 4 + type) * 65536 + source) * 256 + (action.Level & 255)) * 256 + target.Position + 1;
            int slot = (int)((ulong)(key * -7046029254386353131L) >> 53);          // 11 bits
            for (int probe = 0; probe < 8; probe++, slot = (slot + 1) & (ED_SIZE - 1))
            {
                if (edStamp[slot] != EdEpoch)
                {
                    double fresh = ExpectedDamageUncached(action, target);
                    edStamp[slot] = EdEpoch; edKeys[slot] = key; edVals[slot] = fresh;
                    return fresh;
                }
                if (edKeys[slot] == key) return edVals[slot];
            }
            return ExpectedDamageUncached(action, target);
        }

        const int ED_SIZE = 2048;
        // one table for all the battles a thread plays: an entry counts only when it was written in the decision in hand
        [ThreadStatic] static long[] edKeys;
        [ThreadStatic] static double[] edVals;
        [ThreadStatic] static int[] edStamp;
        [ThreadStatic] static int edEpochOfThread;
        bool edActive;
        /// <summary>Rises at each decision of a policy: the figures of the decision before are not kept.</summary>
        public int EdEpoch;

        public void StartDecision()
        {
            if (edKeys == null) { edKeys = new long[ED_SIZE]; edVals = new double[ED_SIZE]; edStamp = new int[ED_SIZE]; }
            EdEpoch = ++edEpochOfThread;
            edActive = true;
        }

        public void EndDecision()
        {
            edActive = false;
        }

        double ExpectedDamageUncached(Action action, Unit target)
        {
            bool special = action.IsSpecial;
            if (action.Has(25) || !(action.Physical || action.Magic || special)) return 0.0;
            if (VisiblyVoided(action, target)) return 0.0;
            double hits = MeanHits(action);
            double chance = HitChance(action, target);
            // a missed spell still strikes for half (three quarters with enchantment 272), and special magic lands at full power even on miss
            if (action.Magic)
            {
                if (special) chance = 1.0;
                else chance += (1 - chance) * (action.Actor.Pieces(F.MISSED_SPELL_ENCHANT) != 0 ? 0.75 : 0.5);
            }
            if (action.Has(139) && target.St[116] != null && !target.Immune("instant death")) return chance * target.Hp;
            if (special)
            {
                double specDmg = SpecialDamage(action, target);
                if (action.TryVal(296, out double specCap)) specDmg = Math.Min(specDmg, specCap);
                return chance * Math.Min(target.Hp, specDmg);
            }
            double perHit;
            if (action.Magic) perHit = MagicDamageExpected(action, target);
            else
            {
                var unit = action.Actor;
                double rate = CriticalRateOf(action, unit, target, 0);
                perHit = PhysicalDamageExpected(action, target, F.ExpectedCriticalFactor(rate));
            }
            if (target.St[116] != null) perHit = perHit * F.SLEEP_NUM / F.SLEEP_DEN;
            Unit wall = DemonWallOf(target, action.Actor);
            if (wall != null) perHit = Math.Max(0.0, perHit + perHit * wall.Value(DEMON_WALL));
            if (action.Actor.Pieces(F.AILING_ENCHANT) != 0 && HasTrueAilment(target)) perHit += perHit * F.AILING_SHARE;
            if (action.Has(86) && target.Kind == Kind.Member && target.ClassId >= F.MAGIC_USER_LOW && target.ClassId < F.MAGIC_USER_HIGH) perHit += perHit;
            if (action.TryVal(296, out double cap)) perHit = Math.Min(perHit, cap);
            return chance * hits * perHit;
        }

        public bool VisiblyVoided(Action action, Unit target)
        {
            return (target.Has(192) && action.Attr != T.NEUTRAL) || (target.Has(182) && (action.Reach == T.SHORT || action.Reach == T.MID));
        }

        public double MeanHits(Action action)
        {
            double hits = 0.0;
            bool any = false;
            int mhIdx = action.MultiHitIndex;
            bool has178 = action.Has(178) || action.Actor.Has(178);
            bool isPlain = action.Kind == AKind.Attack || (action.Atk != null && action.Atk.Plain);
            if (mhIdx >= 0)
            {
                bool rondo = action.Has(210) || action.Actor.Has(210);
                hits += rondo ? MultiHitMeanRondo[mhIdx] : MultiHitMeanNormal[mhIdx];
                any = true;
            }
            if (action.TryVal(93, out double v93) && v93 != 0)
            {
                hits += v93;
                any = true;
            }
            if (has178)
            {
                hits += PyMath.Int(First(action, action.Actor, 178)) + 1;
                any = true;
            }
            if (isPlain && !any)
            {
                double triple = action.Actor.Has(252) ? Math.Min(1.0, action.Actor.Value(252)) : 0.0;
                double dbl = action.Actor.Has(251) ? Math.Min(1.0, action.Actor.Value(251)) : 0.0;
                hits = 3 * triple + 2 * dbl + (1 - triple) * (1 - dbl);
                any = true;
            }
            if (!any) hits = 1.0;
            return Math.Max(1.0, hits);
        }

        int SpecialDamage(Action action, Unit target)
        {
            int amount = RawSpecialDamage(action, target);
            if (!action.Has(142) && target.Has(190)) amount += PyMath.Int(amount * target.Value(190));
            return Math.Max(0, amount);
        }

        int RawSpecialDamage(Action action, Unit target)
        {
            var unit = action.Actor;
            if (action.Has(8)) return PyMath.Int(action.Val(8, 0));
            if (action.Has(12)) return PyMath.Int(unit.Hp * action.Val(12, 0));
            if (action.Has(138))
            {
                int index = T.ResistIndex(action.Attr);
                int res = index >= 0 ? target.Resistance(index) : 0;
                return PyMath.Int(target.MaxHp * action.Val(138, 0) * F.ResistanceFactor(res));
            }
            if (action.Has(140) || action.Has(141))
            {
                // 0x44f9c0 (+0xa5): Halve HP (140) and 3/4 HP (141) work on party members or non-boss enemies.
                bool susceptible = target.Side == Unit.PARTY
                    || (Options.HalveEnemies && !Fixed && (target.EnemyId == T.NONE || !Data.Enemies.TryGetValue(target.EnemyId, out var er) || (er.Flags & 1) == 0));
                if (!susceptible) return 0;
                return action.Has(140) ? target.Hp / 2 : target.Hp * 3 / 4;
            }
            if (action.Has(142)) return Math.Max(0, target.Hp - 1);
            if (action.Has(434)) return Math.Max(0, unit.Hp - 1);
            if (action.Has(435)) return PyMath.Int(unit.Level * action.Val(435, 0));
            return 0;
        }

        double Swing(Unit unit) => SwingOf(unit.Swing);

        double SwingOf(double swing)
        {
            int n = PyMath.Round(100 * swing);
            if (n <= 0) return 0.0;
            return (Rng.RandInt(0, 2 * n) - n) / 100.0;
        }

        double RaceFactor(Unit unit, Unit target)
        {
            if (unit.Side == Unit.PARTY && target.Side == Unit.ENEMIES)
            {
                if (!unit.HasRaceAttackEnchant) return 1.0;
                var s = new PySum();
                if (target.Race != T.NONE && F.RACE_ATTACK.TryGetValue(target.Race, out var list))
                    foreach (var (e, share) in list) s.AddFloat(unit.Pieces(e) * share);
                double bonus = s.Result;
                var t = new PySum();
                // 0x44be88: Feline (196) and Sea Creature (209) are mutually exclusive else-if (IDs 215..217 match Feline only).
                foreach (var (e, ids) in F.RACE_SPECIAL)
                    if (target.EnemyId != T.NONE && ids.Contains(target.EnemyId)) { t.AddInt(unit.Pieces(e)); break; }
                bonus += t.Result;
                return 1.0 + bonus;
            }
            return RaceGuard(unit, target);
        }

        static double RaceGuard(Unit unit, Unit target)
        {
            if (target.HasRaceGuardEnchant && unit.Side == Unit.ENEMIES && target.Side == Unit.PARTY && unit.Race != T.NONE && F.RACE_GUARD.TryGetValue(unit.Race, out var g))
                return 1.0 - F.RACE_GUARD_SHARE_SMALL * target.Pieces(g.small) - F.RACE_GUARD_SHARE_LARGE * target.Pieces(g.large);
            return 1.0;
        }

        static double ElementFactor(Unit unit, Unit target, int attr)
        {
            if (!unit.HasEnchants && !target.HasEnchants) return 1.0;
            int enchant = F.BothSidesElement(attr);
            if (enchant < 0) return 1.0;
            return 1.0 + F.ELEMENT_ENCHANT_SHARE * (unit.Pieces(enchant) + target.Pieces(enchant));
        }

        static double LevelBonus(Unit unit, Unit target) =>
            target.Level > unit.Level ? F.LEVEL_BONUS_SHARE * unit.Pieces(F.HIGHER_LEVEL_ENCHANT)
            : target.Level < unit.Level ? F.LEVEL_BONUS_SHARE * unit.Pieces(F.LOWER_LEVEL_ENCHANT) : 0.0;

        static double FullHpBonus(Unit unit)
        {
            return unit.Hp == unit.MaxHp ? F.FULL_HP_BONUS_SHARE * unit.Pieces(F.FULL_HP_BONUS_ENCHANT) : 0.0;
        }

        double ZoneFactor(Unit unit, Action action)
        {
            double factor = 1.0;
            if (ZoneInfo == null) return factor;
            bool physical = !action.Magic;
            var f = ZoneInfo.Factors;
            // 0x44fbb0: each zone condition (Up, Down, Element match) applies at most ONCE per hit (dedup duplicate slots e.g. St02_0070 (9,9)).
            bool didUp = false, didDown = false, didElem = false;
            foreach (int slot in ZoneInfo.Slots)
            {
                if (!didUp && slot == (physical ? 3 : 4)) { factor *= f != null ? (physical ? f.UpA : f.UpB) : 1.0; didUp = true; }
                if (!didDown && slot == (physical ? 5 : 6)) { factor *= f != null ? (physical ? f.DownA : f.DownB) : 1.0; didDown = true; }
                if (!didElem && slot >= 7 && slot <= 11 && action.Attr == slot - 3) { factor *= f != null ? f.Element : 1.0; didElem = true; }
            }
            return factor;
        }

        // --- damage taken ------------------------------------------------------------------------------------
        void TakeDamage(Unit target, int amount, Action action, bool critical)
        {
            var unit = action != null ? action.Actor : null;
            int origAmount = amount;
            lastEndured = false;
            bool fatal;
            if (Options.SurvivalGuard ?? Data.SurvivalGuard) fatal = target.Hp > 1 && amount >= target.Hp - 1;
            else fatal = amount >= target.Hp;
            if (fatal && target.Has(254) && Roll(target.Value(254)))
            {
                amount = target.Hp - 1;
                lastEndured = true;
            }
            int before = target.Hp;
            LoseHp(target, amount, unit);
            if (unit != null && unit.Side != target.Side)
            {
                Grow(unit.Position);
                RecDamage[unit.Position] += Math.Min(before, amount);
                Rec?.Damage.Add(new RecKey(unit), Math.Min(before, amount));
            }
            if (target.Alive && amount > 0)
            {
                int gained = target.Has(257) ? Math.Max(1, PyMath.Int(amount * target.Value(257))) : 0;
                double share = F.TP_CONVERSION_UP * target.Pieces(72);
                int floor = F.TP_CONVERSION_FLOOR;
                if (target.Pieces(73) != 0)
                {
                    share += F.TP_CONVERSION_MINI * target.Pieces(73);
                    floor = F.TP_CONVERSION_FLOOR_73;
                }
                if (share != 0) gained = Math.Max(floor, gained + PyMath.Int(amount * Math.Min(F.TP_CONVERSION_MAX, share)));
                if (gained != 0) target.Tp = Math.Min(target.MaxTp, target.Tp + gained);
            }
            if (target.Alive && target.Has(312) && !target.EcstasyDone && before >= target.MaxHp / 2.0 && target.MaxHp / 2.0 > target.Hp)
            {
                target.EcstasyDone = true;
                target.SetStatus(new Status(41, target.Value(312), ECSTASY_TURNS, target));
                target.SetStatus(new Status(45, target.Value(312), ECSTASY_TURNS, target));
            }
            if (target.SamsaraState == 0 && target.Has(291) && target.Hp < target.MaxHp / 2.0) target.SamsaraState = 1;
            if (target.Alive && amount > 0)
            {
                target.PopStatus(116);
                // 0x44cfad: Interrupt uses pre-Endure origAmount and runs only on direct physical/magical hits (not Poison/Dance DoTs).
                if (action != null && !action.IsSpecial && (target.Chant != null || Performing(target)))
                    Interrupt(target, origAmount, critical, !action.Magic);
            }
            // Arcane Shield (447; 0x424714, 0x424747..0x42476e): skipped during counters (!inCounter), physical, and special damage;
            // rolls per hit (15% vanilla, 25% Balance via X13) and overwrites stored damage; fires once post-action (Stage 4).
            if (!inCounter && action != null && !action.Physical && !action.IsSpecial && target.Alive && target.HasUnique && target.UniqueEffect == 447 && unit != null && !NotACandidate(unit) && !unit.Has(307) && amount > 0)
            {
                int arcaneSet = Options.HasArcaneChance ? Options.ArcaneChance : Data.ArcaneChance;
                int arcane = arcaneSet != T.NONE && arcaneSet != 0 ? arcaneSet : ARCANE_CHANCE;
                if (Rng.RandRange(100) < arcane)
                {
                    Grow(target.Position);
                    arcaneDamage[target.Position] = amount;
                    arcaneDirty = true;
                }
            }
        }

        void Interrupt(Unit target, int amount, bool critical, bool physical)
        {
            // the interruption enchantments of the target: 57, 58, 59 lower the rate, 60 and 61 raise it (P6.10 of the audit)
            double enchant = 0.10 * target.Pieces(57) + 0.06 * target.Pieces(58) + 0.03 * target.Pieces(59) - 0.06 * target.Pieces(60) + 0.20 * target.Pieces(61);
            double chance = F.InterruptionChance(amount, target.MaxHp, target.Value(264), enchant, critical, physical, Options.InterruptProduct ?? Data.InterruptProduct);
            if (Rng.Random() < chance)
            {
                if (target.Chant != null) Rec?.ChantsBroken.Add(new RecKey(target), 1);
                if (Performing(target)) Rec?.PerformancesBroken.Add(new RecKey(target), 1);
                target.Chant = null;
                EndPerformances(target);
            }
        }

        bool Performing(Unit unit)
        {
            if (unit.HasSongs || unit.HasDances || unit.HasGeass) return true;
            return HasOwnedDoll(unit);
        }

        public void LoseHp(Unit unit, int amount, Unit source)
        {
            if (!unit.Alive || amount <= 0) return;
            Trace?.LoseHp(this, unit, amount);
            unit.Hp -= amount;
            if (unit.Hp <= 0)
            {
                unit.Hp = 0;
                Fall(unit, source);
            }
        }

        void Fall(Unit unit, Unit source)
        {
            if (unit.Has(188) && unit.St[188] != null)
            {
                double value = unit.PopStatus(188).Value;
                unit.Hp = Math.Max(1, PyMath.Int(unit.MaxHp * value));
                return;
            }
            if (unit.Kind == Kind.Doll && unit.Alive) activeDolls--;
            unit.Alive = false;
            unit.Chant = null;
            unit.ClearStatuses();
            // 0x43c1fa: falling clears active song and dance slots on the singer/dancer.
            unit.ClearSongsAndDances();
            if (Rec != null) { Rec.Deaths.Add(new RecKey(unit), 1); if (unit.Side == Unit.ENEMIES) Rec.Kills++; }
            if (activeDolls > 0)
            {
                for (int i = 0; i < Units.Count; i++)
                {
                    var u = Units[i];
                    if (u.Owner == unit && u.Kind == Kind.Doll) RemoveDoll(u);
                }
            }
            foreach (var ally in Units)
            {
                var effects = SnapshotStatuses(ally, statusScratch, out int count);
                for (int i = 0; i < count; i++)
                {
                    int e = effects[i];
                    var s = ally.St[e];
                    if (s != null && s.Source == unit && s.Kind == Status.SongKind) ally.PopStatus(e);
                }
            }
            // 0x43b7a8: Enemy front-row wipe shifts all surviving back-row enemies forward (players never auto-shift).
            if (unit.Side == Unit.ENEMIES && unit.Front)
            {
                bool anyFront = false;
                for (int i = 0; i < Units.Count; i++)
                {
                    var u = Units[i];
                    if (u.Side == Unit.ENEMIES && CanFight(u) && u.Front) { anyFront = true; break; }
                }
                if (!anyFront)
                {
                    for (int i = 0; i < Units.Count; i++)
                    {
                        var u = Units[i];
                        if (u.Side == Unit.ENEMIES && CanFight(u) && !u.Front) u.Front = true;
                    }
                }
            }
        }

        public int Restore(Unit unit, int amount)
        {
            if (!unit.Alive || amount <= 0) return 0;
            int gained = Math.Min(unit.MaxHp - unit.Hp, amount);
            unit.Hp += gained;
            if (gained > 0) Trace?.Restore(this, unit, gained);
            return gained;
        }

        // --- what follows a hit ------------------------------------------------------------------------------
        void AfterHit(Action action, Unit target, int dealt, int preHp)
        {
            var unit = action.Actor;
            bool hostile = target.Side != unit.Side;
            // Capture pre-hit ailment state BEFORE the current hit's ailments are applied (0x422b82 runs before 0x422bd0).
            bool preAiling = hostile && dealt != 0 && target.Alive && HasTrueAilment(target);
            int count = action.Count;
            // the list is walked as worked out before the hit; copy it as the loop can change nothing of it
            for (int i = 0; i < count; i++)
            {
                int effect = action.EffId(i), kind = action.EffKind(i);
                double value = action.EffVal(i);
                if (effect == PLAIN_HIT || effect == MAGIC_POWER || effect == 25 || (kind == 2 && !IsAilment[effect])) continue;
                if (IsAilment[effect])
                {
                    if (Aimed(action, target) || effect == 123)
                    {
                        if (effect == 123)
                        {
                            if (hostile && unit.Level > target.Level && !target.Immune("shadow sew") && target.Pieces(F.ENCHANT_NULLIFY_ALL) == 0 && Roll(value))
                            {
                                target.SetStatus(new Status(123, 1, Math.Max(1.0, action.Turns != 0 ? action.Turns : 1.0), unit));
                                EndParts(target, PartsFor(123));
                            }
                        }
                        else ApplyAilment(unit, target, effect, value, action);
                    }
                    continue;
                }
                if (effect == 74 && hostile)
                {
                    if (Roll(value)) Dispel(target);
                    continue;
                }
                if (effect == 75 && dealt != 0)
                {
                    // 0x422ef2..0x4230b3: HP Drain skips Undead (race 5), dolls, and dead actors; floor 1, capped at target's pre-hit HP.
                    if (target.Race != 5 && unit.Kind != Kind.Doll && unit.Alive)
                    {
                        int drained = Math.Min(preHp, Math.Max(1, PyMath.Int(dealt * value)));
                        Restore(unit, drained);
                    }
                    continue;
                }
                if (effect == 76 && dealt != 0)
                {
                    // 0x422ef2..0x4230b3: TP Drain skips Undead (race 5), dolls, and dead actors; floor 1; subtracts from player target TP.
                    if (target.Race != 5 && unit.Kind != Kind.Doll && unit.Alive)
                    {
                        int drained = Math.Max(1, PyMath.Int(dealt * value));
                        if (target.Kind == Kind.Member) target.Tp = Math.Max(0, target.Tp - drained);
                        if (unit.Kind == Kind.Member) unit.Tp = Math.Min(unit.MaxTp, unit.Tp + drained);
                    }
                    continue;
                }
                if (effect == 2) continue;
                if (effect == 54 && hostile)
                {
                    // 0x423a18..0x423a41: Turn Delay requires dealt > 0, target still alive, and NOT saved by Endure (254).
                    if (dealt > 0 && !lastEndured && target.Alive && !target.Immune("turn delay") && Rng.RandRange(100) < PyMath.Int(value * 100)) Delay(target);
                    continue;
                }
                if (effect == 103 || effect == 9 || effect == 104 || effect == 105 || effect == 128 || effect == 129 || effect == 130 ||
                    effect == 131 || effect == 132 || effect == 426)
                {
                    Heal(action, target, effect, value);
                    continue;
                }
                if (effect == 106 || effect == 235)
                {
                    int n = Math.Min(PyMath.Int(value), CURE_ORDER.Length);
                    for (int k = 0; k < n; k++) target.PopStatus(CURE_ORDER[k]);
                    if (PyMath.Int(value) == CURE_ALL)
                    {
                        // 0x481b12..0x481b39: cure value 8 clears debuffs classified by vtable+0x5c (IsDebuffStatus).
                        var list = SnapshotStatuses(target, statusScratch, out int sc);
                        for (int k = 0; k < sc; k++)
                        {
                            int e = list[k];
                            var s = target.St[e];
                            if (IsDebuffStatus(s)) target.PopStatus(e);
                        }
                    }
                    continue;
                }
                if ((effect == 60 || effect == 61) && hostile)
                {
                    // gold (60) and items (61) are stolen once each (bytes 0x155, 0x154 of the unit); an item can be stolen only from an
                    // enemy whose flags word has bit 15 (0x4503bf - 0x4503d4)
                    bool item = effect == 61;
                    bool allowed = !item || (target.EnemyId != T.NONE && Data.Enemies.TryGetValue(target.EnemyId, out var er) && ((er.Flags >> 15) & 1) != 0);
                    bool already = item ? target.StolenItem : target.StolenGold;
                    double chance = 0.5 * (unit.Stat(Unit.DEX) + 50) / (target.Stat(Unit.AGI) + 50) * action.Val(effect, 0.0);
                    if (allowed && !already && Rng.RandRange(100) < PyMath.Int(F.Clamp(chance, 0.05, 0.95) * 100))
                    {
                        if (item) target.StolenItem = true; else target.StolenGold = true;
                        Rec?.ItemsUsed.Add(new RecKey(unit, true), 1);
                    }
                    continue;
                }
                if (effect == 84 && hostile)
                {
                    if (target.Snack && target.Hp < PyMath.Int(target.MaxHp * 0.5) && Roll(value))
                    {
                        target.Alive = false;
                        if (Rec != null) Rec.Kills++;
                    }
                    continue;
                }
                if (effect == 425)
                {
                    EndParts(target, PerfParts.All);
                    continue;
                }
                if (effect == MAX_HP_DRAIN && hostile && dealt != 0)
                {
                    target.MaxHpBase = Math.Max(1, target.MaxHpBase - PyMath.Int(dealt * value));
                    target.Hp = Math.Min(target.Hp, target.MaxHp);
                    continue;
                }
                if (effect == SPECIAL_SLEEP_EFFECT)
                {
                    ApplyAilment(unit, target, 116, SPECIAL_SLEEP_VALUE, action, SPECIAL_SLEEP_START);
                    continue;
                }
                if (effect == ESCAPE_SELF && target == unit)
                {
                    // 0x47fd52: Escape (11) removes the enemy in both random and fixed battles (not counted as a kill).
                    unit.Alive = false;
                    unit.Chant = null;
                    unit.ClearStatuses();
                    unit.ClearSongsAndDances();
                    continue;
                }
                if (effect == ENEMIES_FLEE && hostile)
                {
                    if (Options.RandomBattle) target.Alive = false;
                    continue;
                }
                if (effect == 170)
                {
                    // 0x44a6ca: single active Provoke status per enemy (new Provoke replaces previous).
                    if (hostile) target.SetStatus(new Status(170, value, action.Turns, unit));
                    continue;
                }
                if (effect == 139 && hostile && target.St[116] != null && !target.Immune("instant death"))
                {
                    // 0x422c23..0x422c50: Sleep Kill consumes Aegis/Nullify barrier (101/102/181) if present.
                    if (!ConsumeBarrier(target)) LoseHp(target, target.Hp, unit);
                    continue;
                }
                if (effect == 10)
                {
                    // 0x47fc30..0x47fcae: enemy Defend / Photosynthesis / Kotatsu Oranges sets the defending state directly.
                    target.Defending = true;
                    continue;
                }
                if (effect == 121 && hostile && !target.Immune("petrification") && target.Resistance(6) < 100 && !Nullified(target, 120))
                {
                    // 0x4f99c1..0x4f9b6b: Instant Petrify checks barrier (101/102/181), attaches Status(120) at Stage = 3,
                    // ends performances, and clears all other statuses while keeping Alive = true and HP intact.
                    if (!ConsumeBarrier(target))
                    {
                        target.SetStatus(new Status(120, 1, 0, unit) { Stage = 3 });
                        CompletePetrify(target);
                    }
                    continue;
                }
                if (effect == 320) continue;
                if (effect == 168 && action.Has(79))
                {
                    if (!Roll(action.Val(79, 0))) continue;
                }
                if ((effect == 66 || effect == 80) && target.Side == Unit.PARTY)
                {
                    if (effect == 80 || target.Pep < 100)
                    {
                        target.Pep += value;
                        target.ClampPep();
                    }
                    continue;
                }
                if (effect == 295 || effect == 296) continue;
                if (kind == 4 || kind == 5 || StatusEffect[effect])
                {
                    bool isSong = IsSongEffect[effect], isDance = IsDanceEffect[effect], isGeass = IsGeassEffect[effect];
                    if (isSong || isDance) PerformSong(unit, action, target, effect, value, isDance);
                    else if (isGeass) PerformGeass(unit, action, target, effect, value);
                    else
                    {
                        var st = new Status(effect, value, action.Turns, unit, action.SourceName, kind, action.Atk != null ? action.Atk.Id : T.NONE) { IsInt = action.EffIsInt(i) };
                        if (effect == 199 || effect == 200 || effect == 339)
                            if (action.TryVal(296, out double cap)) st.WithData(cap);
                        target.SetStatus(st);
                    }
                }
            }
            // Devil's Whisper (320; 0x422b82, 0x422cf1..0x422d32, 0x423560): fires only on damaging hits (dealt != 0) when
            // the target ALREADY had a true ailment (113..122, excluding 123) before the hit's own ailments were applied.
            if (preAiling && target.Alive && (action.Has(320) || unit.Has(320)))
                ApplyAilment(unit, target, 119, First(action, unit, 320), action);
            // the answers of the unit hit (0x423cd0): skipped whole when the attacker is a doll, the summon or a guest (0x423d0e - 0x423d38)
            if (hostile && dealt != 0 && !NotACandidate(unit))
            {
                // Sugar Coma (346; 0x4227d5..0x422822): fires post-damage/post-barrier when target survives a short-range hit.
                if (target.Alive && target.HasUnique && target.UniqueEffect == 346 && action.Reach == T.SHORT && Roll(target.UniqueValue))
                {
                    if (!unit.Immune("slow") && !Nullified(unit, 122))
                        unit.SetStatus(new Status(122, 1.0, 0, target).WithData(SUGAR_COMA_RECOVERY));
                    unit.SetStatus(new Status(168, -0.2, SUGAR_COMA_TURNS, target));
                }
                // Dark Aura (262; 0x423d9b): works on both physical and magical short-range hits; blocked by 304.
                if (target.Has(262) && action.Reach == T.SHORT && !unit.Has(304))
                {
                    int points = PyMath.Int(target.Value(262));
                    int[] order = { 45, 44, 43, 42, 41, 46 };
                    int n = Math.Max(0, Math.Min(points < 0 ? order.Length + points : points, order.Length));
                    for (int k = 0; k < n; k++) unit.SetStatus(new Status(order[k], -0.1, DARK_AURA_TURNS, target));
                }
                // Slow Target (293; 0x423d50..0x4245da): shared Close-range (range == 0) contact gate; Slow (122) routed through ApplyAilment; Speed -0.75 (168) independent.
                if (target.Has(293) && action.Reach == T.SHORT && Roll(target.Value(293)))
                {
                    ApplyAilment(target, unit, 122, 1.0, null, SLOW_TARGET_RECOVERY);
                    unit.SetStatus(new Status(168, -0.75, SLOW_TARGET_TURNS, target));
                }
                // Reprisal (249; 0x424711): front row only, !inCounter, physical Short/Mid, !307.
                if (!inCounter && target.Front && target.Has(249) && action.Physical && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
                {
                    reprisal[target.Position] = Roll(target.Value(249));
                    reprisalDirty = true;
                }
            }
        }

        static PerfParts PartsFor(int effect)
        {
            switch (effect)
            {
                case 114: return PerfParts.Dance | PerfParts.Doll | PerfParts.Geass;
                case 116: return PerfParts.All;
                case 117: return PerfParts.Chant | PerfParts.Song;
                case 118: return PerfParts.All;
                case 121: return PerfParts.All;
                case 123: return PerfParts.All;
                default: return PerfParts.None;
            }
        }

        public static bool PerformanceSlotsTwo(Unit unit, bool dance) => unit.Has(dance ? 284 : 287);
        public static int PerformanceSlots(Unit unit, bool dance) => unit.Has(dance ? 284 : 287) ? 2 : 1;

        void EvictSameSidePerformance(Unit performer, int effect, bool isDance, bool isGeass)
        {
            // 0x43bdd0..0x43cb80: erase same cmdId from any other ally on the same side already performing it.
            foreach (var ally in Units)
            {
                if (ally == performer || ally.Side != performer.Side) continue;
                var ids = isGeass ? ally.GeassIds : isDance ? ally.DanceIds : ally.SongIds;
                var names = isGeass ? ally.Geass : isDance ? ally.Dance : ally.Song;
                int idx = ids.IndexOf(effect);
                if (idx >= 0)
                {
                    ids.RemoveAt(idx);
                    if (idx < names.Count) names.RemoveAt(idx);
                    foreach (var u in Units)
                    {
                        var st = u.St[effect];
                        if (st != null && st.Source == ally && st.Kind == Status.SongKind) u.PopStatus(effect);
                    }
                }
            }
        }

        void PerformGeass(Unit caster, Action action, Unit target, int effect, double value)
        {
            // 0x43cb80..0x43ce30 (AddGeassCommand / DeleteGeassCommand): Geass effects 335..341 share a per-caster
            // performance slot group tracked by cmdId (cap 1, or 2 with effect 284 at 0x43ccc8), evicting same-side duplicates and oldest Geass.
            EvictSameSidePerformance(caster, effect, false, true);
            int keep = caster.Has(284) ? 2 : 1;
            var ownIds = caster.GeassIds;
            var ownNames = caster.Geass;
            string name = action.Skill != null ? action.Skill.Name : action.Atk.Name;
            if (!ownIds.Contains(effect))
            {
                ownIds.Add(effect);
                ownNames.Add(name);
                while (ownIds.Count > keep)
                {
                    int oldId = ownIds[0];
                    ownIds.RemoveAt(0);
                    if (ownNames.Count > 0) ownNames.RemoveAt(0);
                    foreach (var u in Units)
                    {
                        var s = u.St[oldId];
                        if (s != null && s.Source == caster && s.Kind == Status.SongKind) u.PopStatus(oldId);
                    }
                }
            }
            int atkId = action.Atk != null ? action.Atk.Id : T.NONE;
            var st = new Status(effect, value, 0, caster, name, Status.SongKind, atkId);
            if (effect == 339 && action.TryVal(296, out double cap)) st.WithData(cap);
            target.SetStatus(st);
        }

        void PerformSong(Unit singer, Action action, Unit target, int effect, double value, bool dance)
        {
            int bonusEffect = dance ? 280 : 279, up = dance ? 302 : 300, mini = dance ? 303 : 301;
            double bonus = singer.Value(bonusEffect, 0.0) + Math.Min(0.05, 0.02 * singer.Pieces(up) + 0.01 * singer.Pieces(mini));
            EvictSameSidePerformance(singer, effect, dance, false);
            int keep = PerformanceSlots(singer, dance);
            var ownIds = dance ? singer.DanceIds : singer.SongIds;
            var ownNames = dance ? singer.Dance : singer.Song;
            string name = action.Skill != null ? action.Skill.Name : action.Atk.Name;
            if (!ownIds.Contains(effect))
            {
                ownIds.Add(effect);
                ownNames.Add(name);
                while (ownIds.Count > keep)
                {
                    int oldId = ownIds[0];
                    ownIds.RemoveAt(0);
                    if (ownNames.Count > 0) ownNames.RemoveAt(0);
                    foreach (var u in Units)
                    {
                        var s = u.St[oldId];
                        if (s != null && s.Source == singer && s.Kind == Status.SongKind) u.PopStatus(oldId);
                    }
                }
            }
            int atkId = action.Atk != null ? action.Atk.Id : T.NONE;
            if (effect == 215 || effect == 216)
            {
                target.SetStatus(new Status(effect, value, 0, singer, name, Status.SongKind, atkId).WithData(bonus));
            }
            else
            {
                double sign = 1, scale = 1;
                switch (effect)
                {
                    case 195: case 196: case 197: case 198: case 201: case 205: sign = -1; scale = 1; break;
                    case 202: sign = -1; scale = 100; break;
                    case 211: sign = 1; scale = 100; break;
                }
                // 0x43be90: Song/Dance Bonus (279/280) does NOT apply to 200, 203, 204, 219, 220, 221, 223.
                bool noBonus = effect == 200 || effect == 203 || effect == 204 || effect == 219 || effect == 220 || effect == 221 || effect == 223;
                var st = new Status(effect, noBonus ? value : value + sign * scale * bonus, 0, singer, name, Status.SongKind, atkId);
                if ((effect == 199 || effect == 200) && action.TryVal(296, out double cap)) st.WithData(cap);
                target.SetStatus(st);
            }
        }

        public bool ApplyAilment(Unit unit, Unit target, int effect, double value, Action action, int start = T.NONE)
        {
            string name = AilmentName[effect];
            // 0x481ef4..0x483624: recovering ailments (113..117, 122) can be re-applied (stripping barriers / resetting recovery to start);
            // Petrify (120) and Shadow Sew (123) do not overwrite an existing instance; 192 is handled in Voided, not ApplyAilment.
            if (target.Immune(name) || Nullified(target, effect)) return false;
            if ((effect == 120 || effect == 123) && target.St[effect] != null) return false;
            int index = AilmentResist[effect];
            int resistance = index != T.NONE ? target.Resistance(index) : 0;
            int chance = F.AilmentThreshold(value, resistance);
            if (chance <= 0 || Rng.RandRange(100) >= chance) return false;
            if (ConsumeBarrier(target)) return false;
            if (effect == 119)
            {
                LoseHp(target, target.Hp, unit);
                return true;
            }
            if (effect == 118)
            {
                Stun(target);
                return true;
            }
            // 0x4185b7, 0x418812, 0x418a9b: action-inflicted recovering ailments start at 5% natural recovery (Third Eye Wide passes start: 0).
            if (start == T.NONE) start = 5;
            target.SetStatus(new Status(effect, value, 0, unit).WithData(start));
            // 0x4fa056: Sleep (116) strips all active statuses with CommandData flags38 bit 1 (vt+0x8c IsSleepCleared, 36 IDs).
            if (effect == 116)
            {
                var snap = SnapshotStatuses(target, statusScratch, out int sc);
                for (int k = 0; k < sc; k++)
                {
                    int se = snap[k];
                    if (Data.SleepClearedCommands.Contains(se)) target.PopStatus(se);
                }
            }
            EndParts(target, PartsFor(effect));
            return true;
        }

        public static bool Nullified(Unit target, int ailment)
        {
            if (!target.HasEnchants) return false;
            if (target.Pieces(F.ENCHANT_NULLIFY_ALL) != 0) return true;
            if ((uint)ailment < (uint)NullifyEnchantOfAilment.Length)
            {
                int e = NullifyEnchantOfAilment[ailment];
                if (e >= 0 && target.Pieces(e) != 0) return true;
            }
            return false;
        }

        void Stun(Unit target)
        {
            EndParts(target, PartsFor(118));
            double lostTime = Time + 1.0 - target.NextTime;
            target.NextTime = Time + 1.0;
            if (target.Side == Unit.ENEMIES && lostTime > 0) Rec?.Delayed.Add(new RecKey(target), lostTime, true);
        }

        void EndPerformances(Unit unit)
        {
            EndParts(unit, PerfParts.Song | PerfParts.Dance | PerfParts.Doll | PerfParts.Geass);
        }

        void EndParts(Unit unit, PerfParts parts)
        {
            if (parts == PerfParts.None) return;
            if ((parts & PerfParts.Chant) != 0) unit.Chant = null;
            for (int pass = 0; pass < 3; pass++)
            {
                bool wanted = pass == 0 ? ((parts & PerfParts.Song) != 0 && unit.HasSongs)
                            : pass == 1 ? ((parts & PerfParts.Dance) != 0 && unit.HasDances)
                            : ((parts & PerfParts.Geass) != 0 && unit.HasGeass);
                if (!wanted) continue;
                var names = pass == 0 ? unit.Song : pass == 1 ? unit.Dance : unit.Geass;
                var ids = pass == 0 ? unit.SongIds : pass == 1 ? unit.DanceIds : unit.GeassIds;
                foreach (var other in Units)
                {
                    var effects = SnapshotStatuses(other, statusScratch, out int sc);
                    for (int k = 0; k < sc; k++)
                    {
                        int e = effects[k];
                        var s = other.St[e];
                        if (s != null && s.Source == unit && s.Kind == Status.SongKind &&
                            (ids.Contains(e) || (s.Skill != null && names.Contains(s.Skill)))) other.PopStatus(e);
                    }
                }
                names.Clear();
                ids.Clear();
            }
            if ((parts & PerfParts.Doll) != 0 && activeDolls > 0)
            {
                for (int i = 0; i < Units.Count; i++)
                {
                    var u = Units[i];
                    if (u.Owner == unit && u.Kind == Kind.Doll && u.Alive && !u.Arrow && !u.Genjimaru && u.ShadowOf == null) RemoveDoll(u);
                }
            }
        }

        void Delay(Unit target)
        {
            if (!target.Alive) return;
            delayOrderScratch.Clear();
            var order = delayOrderScratch;
            foreach (var u in Units) if (u.Alive) order.Add(u);
            InsertionSortByTime(order);
            int k = order.IndexOf(target);
            if (k + 1 < order.Count)
            {
                var nxt = order[k + 1];
                double tmp = target.NextTime;
                target.NextTime = nxt.NextTime;
                nxt.NextTime = tmp;
                Rec?.Denied.Add(new RecKey(target), 0.0, true);
            }
        }

        public static bool Dispellable(Unit target)
        {
            for (int i = 0; i < target.StCount; i++)
            {
                int e = target.StatusAt(i);
                if (DispelAlways[e] || (DispelIfRaised[e] && target.St[e].Value >= 0)) return true;
            }
            return false;
        }

        void Dispel(Unit target)
        {
            var effects = SnapshotStatuses(target, statusScratch, out int sc);
            if (sc == 0) return;
            var remove = sc <= dispelRemoveScratch.Length ? dispelRemoveScratch : new int[sc];
            int rn = 0;
            for (int k = 0; k < sc; k++)
            {
                int e = effects[k];
                if (DispelAlways[e] || (DispelIfRaised[e] && target.St[e].Value >= 0)) remove[rn++] = e;
            }
            for (int k = 0; k < rn; k++) target.PopStatus(remove[k]);
        }

        void Healed(Unit unit, int gained)
        {
            Rec?.Healing.Add(new RecKey(unit), gained);
        }

        void Heal(Action action, Unit target, int effect, double value)
        {
            var unit = action.Actor;
            bool hasCap = action.TryVal(295, out double cap);
            if (effect == 103)
            {
                double coefficient = value;
                if (IsPuppet(unit) && unit.Owner != null)
                    coefficient += F.DollHealBonus(unit.Owner.Passive(286, 0.0), unit.Owner.Pieces(304), unit.Owner.Pieces(305));
                bool hasFixed = action.TryVal(9, out double fixedValue) && fixedValue != 0;
                int amount;
                if (hasFixed) amount = PyMath.Int(fixedValue);
                else
                {
                    double random = F.HEAL_RANDOM[Rng.ChoiceIndex(F.HEAL_RANDOM.Length)];
                    amount = F.Heal(unit.Stat(Unit.RES), coefficient, unit.Passive(245, 0.0), hasCap, cap, unit.Passive(317, 0.0), random);
                }
                Healed(unit, Restore(target, amount));
            }
            else if (effect == 9 && !action.Has(103))
            {
                Healed(unit, Restore(target, PyMath.Int(value)));
            }
            else if (effect == 104)
            {
                Healed(unit, Restore(target, target.MaxHp));
            }
            else if (effect == 105)
            {
                if (!target.Alive)
                {
                    target.Alive = true;
                    target.Hp = Math.Max(1, PyMath.Int(target.MaxHp * value));
                    target.NextTime = Time + Wait(target);
                }
            }
            else if (effect == 128)
            {
                Healed(unit, Restore(target, PyMath.Int(target.MaxHp * value)));
            }
            else if (effect == 131)
            {
                // Heal Enemy (0x483da0): heals enemy targets only, fixed amount with no cap.
                if (target.Side == Unit.ENEMIES) Healed(unit, Restore(target, PyMath.Int(value)));
            }
            else if (effect == 132)
            {
                Healed(unit, Restore(target, F.FractionRecovery(target.MaxHp, value, hasCap, cap, unit.Passive(317, 0.0))));
            }
            else if (effect == 129)
            {
                target.Tp = Math.Min(target.MaxTp, target.Tp + PyMath.Int(target.MaxTp * value));
            }
            else if (effect == 426)
            {
                target.Tp = Math.Min(target.MaxTp, target.Tp + PyMath.Int(value));
            }
            else if (effect == 130)
            {
                int given = PyMath.Int(unit.Tp * value);
                unit.Tp = 0;
                target.Tp = Math.Min(target.MaxTp, target.Tp + given);
            }
        }

        void Counter(Unit unit, Unit attacker)
        {
            // a counter is never set up against a doll, the summon or a guest (0x43b5f0, 0x43b610 at 0x42261b - 0x422637);
            // and never recurses from inside another counter (0x42039d); the hit that started it stays voided.
            if (inCounter || NotACandidate(attacker)) return;
            if (unit.Alive && attacker.Alive)
            {
                if (unit == attacker) return;
                Trace?.Counter(this, unit, attacker);
                var saved = damageByTarget;              // the counter keeps a record of its own hits
                damageByTarget = null;
                inCounter = true;
                try
                {
                    // an enemy counters with its first attack (P7.1 of the audit); a member with a plain attack (the skill its status
                    // links to is not read: a model limit)
                    Action answer = new Action(unit, AKind.Attack);
                    if (unit.Kind == Kind.Enemy && unit.Attacks != null && unit.Attacks.Length > 0)
                    {
                        var atk = Data.GetAttack(unit.Attacks[0]);
                        if (atk != null) answer = new Action(unit, AKind.Enemy, atk, 1);
                    }
                    Resolve(answer, attacker, 0);
                }
                finally
                {
                    inCounter = false;
                    damageByTarget = saved;
                }
            }
        }

        // --- dolls, random moves, items --------------------------------------------------------------------------
        const int MAX_ACTIVE_DOLLS = 12; // CBattleUnitCtrl::AddDoll (0x43a1a0): units 2000..2999 < 0xc

        // Exact EnemyAttackData summon -> action attack IDs decoded from Command::CCommand_0146::AddTask
        // (guest/summon branch 0x48490a..0x4852c0, enemy branch 0x4852ca..0x485c17).
        static readonly Dictionary<int, int[]> EnemyDollActions = new Dictionary<int, int[]>
        {
            { 690, new[] { 307 } }, { 691, new[] { 308 } },
            { 693, new[] { 310 } }, { 694, new[] { 311 } },
            { 696, new[] { 313 } }, { 697, new[] { 314 } },
            { 699, new[] { 316 } }, { 700, new[] { 317 } },
            { 702, new[] { 319 } }, { 703, new[] { 320 } },
            { 705, new[] { 322 } }, { 706, new[] { 323 } },
            { 708, new[] { 737 } }, { 709, new[] { 738 } },
            { 711, new[] { 740 } }, { 712, new[] { 741 } },
            { 717, new[] { 1480 } }, { 718, new[] { 1481 } }, { 719, new[] { 1482 } },
            { 721, new[] { 1484 } }, { 722, new[] { 1485 } }, { 723, new[] { 1486 } },
            { 725, new[] { 1488 } }, { 726, new[] { 1489 } }, { 727, new[] { 1490 } },
            { 729, new[] { 1492 } }, { 730, new[] { 1493 } }, { 731, new[] { 1494 } },
            { 733, new[] { 1590, 1594, 1598, 1602, 1606 } },
            { 734, new[] { 1591, 1595, 1599, 1603, 1607 } },
            { 735, new[] { 1592, 1596, 1600, 1604, 1608 } },
            { 1789, new[] { 1801 } }, { 1790, new[] { 1802 } }, { 1791, new[] { 1803 } },
        };

        static readonly int[] PUPPET_EFFECTS = { 228, 229, 230, 231, 232, 233 };

        static bool IsArrowAttack(int attackId)
            => attackId == 696 || attackId == 697 || attackId == 1789 || attackId == 1790 || attackId == 1791;

        static bool SamePuppetGroup(Unit a, Unit b)
            // AddPuppetCommand (0x43c83c..0x43c86e): members (0x43e6d0(1,1)), guests/summons (0x43b3a0), and enemies (0x43e6d0(0,0)) each have their own pool.
            => a != null && b != null && a.Side == b.Side && (a.Kind == Kind.Member) == (b.Kind == Kind.Member);

        /// <summary>True when <paramref name="u"/> is an active puppet doll (effects 228..233),
        /// distinct from Star Dust Arrow, Genjimaru, Lilian's shadow, and non-puppet enemy summons.</summary>
        internal static bool IsPuppet(Unit u)
            => u.Kind == Kind.Doll && u.Alive && !u.Arrow && !u.Genjimaru && u.ShadowOf == null && u.PuppetEffect != T.NONE;

        int ActiveDollCount()
        {
            // 0x43a1a0: all active dolls (puppets, arrows, Genjimaru, Lilian's shadow) share the 12-doll cap.
            int count = 0;
            foreach (var u in Units) if (u.Kind == Kind.Doll && u.Alive) count++;
            return count;
        }

        void RemoveSameTypeDolls(Unit owner, int effect)
        {
            // AddPuppetCommand (0x43c83c - 0x43c911): removes any active doll of the same effect in the owner's pool.
            var same = new List<Unit>();
            foreach (var u in Units)
                if (IsPuppet(u) && u.PuppetEffect == effect && SamePuppetGroup(u.Owner, owner)) same.Add(u);
            foreach (var u in same) RemoveDoll(u);
        }

        void MakeDoll(Action action)
        {
            var owner = action.Actor;
            if (action.Kind == AKind.Enemy || owner.Kind != Kind.Member)
            {
                MakeGuestDoll(action);
                return;
            }
            DollRec doll = null;
            foreach (var d in Data.Dolls) if (d.Skill == action.SourceId) { doll = d; break; }
            if (doll == null) return;
            bool arrow = doll.Effect == T.NONE;
            if (arrow)
            {
                var list = new List<Unit>();
                foreach (var u in Units) if (u.Owner == owner && u.Arrow && u.Alive) list.Add(u);
                foreach (var u in list) RemoveDoll(u);
            }
            else
            {
                RemoveSameTypeDolls(owner, doll.Effect);
                int keep = owner.Has(313) ? 2 : 1;
                var own = new List<Unit>();
                foreach (var u in Units) if (IsPuppet(u) && u.Owner == owner) own.Add(u);
                while (own.Count >= keep)
                {
                    RemoveDoll(own[0]);
                    own.RemoveAt(0);
                }
            }
            double n = action.Val(146, 1);
            int count = Math.Max(1, PyMath.Int(n != 0 ? n : 1));
            for (int i = 0; i < count; i++)
            {
                if (ActiveDollCount() >= MAX_ACTIVE_DOLLS) break;
                var unit = UnitFactory.BuildDoll(owner, doll, action.Level, Data);
                unit.Arrow = arrow;
                // 0x4fdfd0: Doll's Life (297) extends only the 6 puppets, not Star Dust Arrow.
                if (!arrow) unit.Life += PyMath.Int(owner.Passive(297, 0.0));
                unit.Position = Units.Count;
                // 0x43a2a3..0x43a2bf: newly summoned dolls start at gauge = RandRange(92) / 100.0 -> NextTime = Time + 1.0 - gauge.
                unit.NextTime = Time + 1.0 - Rng.RandRange(92) / 100.0;
                AddUnit(unit);
            }
        }

        void MakeGuestDoll(Action action)
        {
            var owner = action.Actor;
            if (!EnemyDollActions.TryGetValue(action.SourceId, out var actionIds)) return;

            int puppetEffect = T.NONE;
            foreach (int pe in PUPPET_EFFECTS)
                if (action.Has(pe)) { puppetEffect = pe; break; }
            bool arrow = IsArrowAttack(action.SourceId);

            if (puppetEffect != T.NONE)
            {
                RemoveSameTypeDolls(owner, puppetEffect);
                int keep = owner.Has(313) ? 2 : 1; // 0x43c920: Double Puppet (e.g. Paracas passive 1561)
                var own = new List<Unit>();
                foreach (var u in Units) if (IsPuppet(u) && u.Owner == owner) own.Add(u);
                while (own.Count >= keep)
                {
                    RemoveDoll(own[0]);
                    own.RemoveAt(0);
                }
            }

            double lifeValue = action.Val(147, 3);
            int life = PyMath.Int(lifeValue != 0 ? lifeValue : 3);
            double countValue = action.Val(146, 1);
            int count = Math.Max(1, PyMath.Int(countValue != 0 ? countValue : 1));
            string name = action.Atk != null && !string.IsNullOrEmpty(action.Atk.Name) ? action.Atk.Name : "Doll";

            for (int i = 0; i < count; i++)
            {
                if (ActiveDollCount() >= MAX_ACTIVE_DOLLS) break;
                // CGamePlayerStatusOtherETCDoll (0x4fe5f0) / CGameEnemyStatusETCDoll (0x4fd3d0): copies owner stats, HP=9999, weight=0.0 (0x4fd630).
                var unit = new Unit(name, owner.Side, owner.Level, UnitFactory.DOLL_HP, 0, owner.Base, null, 0.0, 0.0, owner.Race, Kind.Doll);
                unit.Owner = owner;
                unit.Arrow = arrow;
                unit.Life = life;
                unit.SummonAttackId = action.SourceId;
                unit.PuppetEffect = puppetEffect;
                unit.Attacks = actionIds;
                unit.Front = owner.Front;
                unit.Position = Units.Count;
                unit.NextTime = Time + 1.0 - Rng.RandRange(92) / 100.0;
                AddUnit(unit);
            }
        }

        void RemoveDoll(Unit doll)
        {
            if (doll.Alive) activeDolls--;
            doll.Alive = false;
            doll.Chant = null;
        }

        void MakeGenjimaru(Action action)
        {
            foreach (var u in Units) if (u.Alive && u.Genjimaru) return;
            if (ActiveDollCount() >= MAX_ACTIVE_DOLLS) return;
            var turns = new int[10];
            Array.Fill(turns, GENJIMARU_LIFE);
            var record = new DollRec { Skill = GENJIMARU_ACTION, Name = "Genjimaru", Effect = GENJIMARU, Range = null, Turns = turns, Actions = new[] { GENJIMARU_ACTION } };
            // 0x48b31b (push 1): Genjimaru is always created at level 1.
            var unit = UnitFactory.BuildDoll(action.Actor, record, 1, Data);
            unit.Genjimaru = true;
            unit.Position = Units.Count;
            unit.NextTime = Time + 1.0 - Rng.RandRange(92) / 100.0;
            AddUnit(unit);
        }

        Action DollAction(Unit doll)
        {
            if (doll.SummonAttackId != T.NONE)
            {
                if (doll.Attacks == null || doll.Attacks.Length == 0) return new Action(doll, AKind.Attack);
                int chosenAtk = doll.Attacks[Rng.ChoiceIndex(doll.Attacks.Length)];
                var atk = Data.GetAttack(chosenAtk);
                if (atk == null) return null;
                var atkAction = new Action(doll, AKind.Enemy, atk, 1);
                if (atkAction.TargetCode == T.ALLY)
                {
                    Unit best = null;
                    foreach (var m in AlliesArray(doll))
                    {
                        if (NotACandidate(m)) continue;
                        if (best == null || m.HpRatio < best.HpRatio) best = m;
                    }
                    atkAction.Target = best;
                }
                return atkAction;
            }
            var actions = doll.Doll.Actions;
            if (actions.Length == 0) return new Action(doll, AKind.Attack);
            int chosen = actions[Rng.ChoiceIndex(actions.Length)];
            var skill = Data.GetSkill(doll.Doll.Skill == 100 ? "Magic" : "Technique", chosen);
            if (skill == null) return null;
            var action = new Action(doll, AKind.Skill, skill, doll.DollLevel);
            var members = new List<Unit>();
            foreach (var u in AlliesArray(doll)) if (u.Kind == Kind.Member) members.Add(u);
            if (members.Count > 0 && action.TargetCode == T.ALLY)
            {
                Unit best = null;
                foreach (var m in members) if (best == null || m.HpRatio < best.HpRatio) best = m;
                action.Target = best;
            }
            else if (members.Count > 0 && action.TargetCode == T.NO_TARGET && action.Has(235))
            {
                // sorted by -(number of ailments), stable
                var ailing = new List<Unit>(members);
                for (int i = 1; i < ailing.Count; i++)
                {
                    var x = ailing[i];
                    int cx = CountAilments(x);
                    int j = i - 1;
                    while (j >= 0 && CountAilments(ailing[j]) < cx) { ailing[j + 1] = ailing[j]; j--; }
                    ailing[j + 1] = x;
                }
                int take = Math.Min(Options.DollCureTargets, ailing.Count);
                if (take < 0) take = Math.Max(0, ailing.Count + Options.DollCureTargets);
                action.FixedTargets = ailing.GetRange(0, take).ToArray();
            }
            return action;
        }

        Action RandomMove(Action action, int effect)
        {
            RandomMove table = null;
            foreach (var t in Data.RandomMoves) if (t.Effect == effect) { table = t; break; }
            if (table == null) return null;
            bool joker = action.Actor.Has(315);
            var weights = new double[table.Results.Length];
            var picks = new int[weights.Length];
            for (int i = 0; i < weights.Length; i++) { weights[i] = joker ? table.Results[i].JokerWeight : table.Results[i].Weight; picks[i] = i; }
            var result = table.Results[Weighted(picks, weights)];
            var skill = Data.ById(result.Skill);
            if (skill == null) return null;
            bool genji = false;
            foreach (int e in result.Effects) if (e == 427) genji = true;
            if (genji)
            {
                bool present = false;
                foreach (var u in Units) if (u.Alive && u.Genjimaru) present = true;
                if (present)
                {
                    RandomResult empty = null;
                    foreach (var r in table.Results) if (r.Effects.Length == 0) { empty = r; break; }
                    skill = empty != null ? Data.ById(empty.Skill) : null;
                    if (skill == null) return null;
                }
            }
            return new Action(action.Actor, AKind.Skill, skill, action.Level);
        }

        static int ApplyItemMastery(double value, double mastery)
        {
            int v = PyMath.Int(value);
            return v + PyMath.Int(v * mastery);
        }

        public void UseItemFree(Unit unit, int itemId, Unit primaryTarget)
        {
            if (!Data.Items.TryGetValue(itemId, out var item)) return;
            ExecuteItemEffects(unit, item, primaryTarget ?? unit);
        }

        public void UseItem(Action action)
        {
            var unit = action.Actor;
            Item item = null;
            if (action.Item != T.NONE) Data.Items.TryGetValue(action.Item, out item);
            if (item == null || !unit.Items.TryGetValue(action.Item, out int have) || have <= 0) return;
            // ItemData Flags_0x18 bit 8 (0x100): infinite battle items (859..867) are not consumed on use.
            if ((item.Flags & 0x100) == 0)
            {
                unit.Items[action.Item] = have - 1;
                if (unit.Has(274) && Roll(unit.Value(274))) unit.Items[action.Item] += 1;
            }
            Rec?.ItemsUsed.Add(new RecKey(unit, item.Name), 1);
            ExecuteItemEffects(unit, item, action.Target ?? unit);
        }

        void ExecuteItemEffects(Unit unit, Item item, Unit primaryTarget)
        {
            // ItemData w_0x5c (0x456ff0): 16 Single, 17 Row, 18 SideAll.
            Unit[] itemTargets;
            if (item.TargetType == 18)
                itemTargets = TargetableArray(primaryTarget.Side);
            else if (item.TargetType == 17)
            {
                var sideUnits = TargetableArray(primaryTarget.Side);
                var rowList = new List<Unit>(sideUnits.Length);
                foreach (var u in sideUnits) if (u.Front == primaryTarget.Front) rowList.Add(u);
                itemTargets = rowList.Count > 0 ? rowList.ToArray() : new[] { primaryTarget };
            }
            else
                itemTargets = new[] { primaryTarget };
            double mastery = unit.Passive(275, 0.0);
            // Fixed 4-slot layout (0x55b550): slots 0..1 act on ally target, slots 2..3 act on enemy target; -1 is empty.
            int from = primaryTarget.Side == unit.Side ? 0 : 2, to = Math.Min(item.Kinds.Length, from + 2);
            for (int i = from; i < to; i++)
            {
                int kind = item.Kinds[i];
                if (kind < 0) continue;
                double value = item.Values[i];
                if (kind == 0) { foreach (var t in itemTargets) Restore(t, ApplyItemMastery(value, mastery)); }
                else if (kind == 1)
                {
                    foreach (var t in itemTargets) if (CanFight(t)) t.Tp = Math.Min(t.MaxTp, t.Tp + ApplyItemMastery(value, mastery));
                }
                else if (kind == 2)
                {
                    foreach (var t in itemTargets)
                        if (CanFight(t))
                        {
                            int amt = ApplyItemMastery(value, mastery);
                            Restore(t, amt);
                            t.Tp = Math.Min(t.MaxTp, t.Tp + amt);
                        }
                }
                else if (kind == 3)
                {
                    foreach (var ally in AlliesArray(unit)) Restore(ally, ApplyItemMastery(value, mastery));
                }
                else if (kind == 4)
                {
                    foreach (var ally in AlliesArray(unit))
                        if (CanFight(ally)) ally.Tp = Math.Min(ally.MaxTp, ally.Tp + ApplyItemMastery(value, mastery));
                }
                else if (kind == 5)
                {
                    foreach (var ally in AlliesArray(unit))
                        if (CanFight(ally))
                        {
                            int amt = ApplyItemMastery(value, mastery);
                            Restore(ally, amt);
                            ally.Tp = Math.Min(ally.MaxTp, ally.Tp + amt);
                        }
                }
                else if (kind == 8 && !primaryTarget.Alive)
                {
                    primaryTarget.Alive = true;
                    primaryTarget.Hp = Math.Max(1, PyMath.Int(primaryTarget.MaxHp * value / 100.0));
                    primaryTarget.NextTime = Time + Wait(primaryTarget);
                }
                else if (kind == ITEM_CURE_ONE)
                {
                    // 0x50fbcd: cure items clear true ailments 113..122 only (never Shadow Sew 123).
                    foreach (var t in itemTargets)
                    {
                        var present = new List<int>();
                        foreach (int e in AILMENT_IDS) if (e != 123 && t.St[e] != null) present.Add(e);
                        if (present.Count > 0) t.PopStatus(present[Rng.ChoiceIndex(present.Count)]);
                    }
                }
                else if (kind == ITEM_CURE_ALL)
                {
                    foreach (var t in itemTargets)
                    {
                        var present = new List<int>();
                        foreach (int e in AILMENT_IDS) if (e != 123 && t.St[e] != null) present.Add(e);
                        foreach (int e in present) t.PopStatus(e);
                    }
                }
                else if (Data.ItemSkillSpecs.TryGetValue(kind, out var spec))
                {
                    // 0x50b030 / 0x511790 / 0x5117c0: flag 0 rolls value*100% chance and casts at fixedLevel (or max);
                    // flag 1 casts unconditionally at level = clamp(int(value), 1, skill.Levels).
                    if (spec.UseValAsLevel || Rng.RandRange(100) < PyMath.Int(value * 100))
                    {
                        var skill = Data.ById(spec.SkillId);
                        if (skill != null)
                        {
                            int lv = spec.UseValAsLevel ? Math.Max(1, Math.Min(skill.Levels, PyMath.Int(value)))
                                   : (spec.FixedLevel > 0 ? Math.Min(skill.Levels, spec.FixedLevel) : skill.Levels);
                            Perform(new Action(unit, AKind.Skill, skill, lv, primaryTarget) { Paid = true });
                        }
                    }
                }
                else if (Data.ItemSkills.TryGetValue(kind, out int skillId))
                {
                    var skill = Data.ById(skillId);
                    // 0x50b136: item-invoked skills do not spend TP.
                    if (skill != null) Perform(new Action(unit, AKind.Skill, skill, skill.Levels, primaryTarget) { Paid = true });
                }
            }
        }

        public bool Roll(double value)
        {
            return Rng.RandRange(100) < PyMath.Int(value * 100);
        }
    }
}
