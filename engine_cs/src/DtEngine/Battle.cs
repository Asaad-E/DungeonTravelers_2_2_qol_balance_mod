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
        public bool? SurvivalGuard, InterruptProduct;
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
        static readonly int[] SPEED_BUFFS = { 168, 217, 221, 201, 340, 316 };
        static readonly int[] CHANT_SPEED_BUFFS = { 214, 265, 281 };
        static readonly int[] CRIT_TERMS = { 31, 174, 211 };
        static readonly int[] ACCURACY_BUFFS = { 166, 197, 337 }, EVASION_BUFFS = { 164, 198, 338 };
        static readonly int[] MAGIC_ACCURACY_BUFFS = { 167, 309, 197, 222, 278, 353 }, MAGIC_EVASION_BUFFS = { 165, 198 };
        static readonly int[] MAGIC_DEFENCE_MODIFIERS = { 163, 196, 205, 336, 213, 220, 223 };
        static readonly int[] DEFENCE_MODIFIERS = { 28, 162, 187, 196, 205, 336, 219 };
        static readonly int[] ATTACK_STATUS_MODIFIERS = { 161, 195, 335, 219 };
        const int LULLABY = 205;
        static readonly int[] LULLABY_ACCURACY = { 278, 353 };
        static readonly int[] MAGIC_HIT_DIVISORS = { 220, 223 };
        const int STAB_EVASION = 253;
        public const int SACRIFICE = 77, MAX_HP_DRAIN = 133, EXTRA_TARGETS = 137;
        const int SAMSARA_STEP = 50;
        const int MURDER = 258, DARK_QUEST = 263, KNOCK_DOWN = 305, PRETEND = 310, DEMON_WALL = 356, ENEMIES_FLEE = 432;
        const int DARK_AURA_TURNS = 4, ECSTASY_TURNS = 3;
        const int SLOW_TARGET_RECOVERY = 5, SLOW_TARGET_TURNS = 5, SUGAR_COMA_RECOVERY = 5, SUGAR_COMA_TURNS = 3;
        const int SPECIAL_SLEEP_EFFECT = 143, SPECIAL_SLEEP_START = 5;
        const double SPECIAL_SLEEP_VALUE = 10.0;
        const int MATERIAL_GUARD = 179;
        const int GENJIMARU = 427, GENJIMARU_ACTION = 107, GENJIMARU_LIFE = 3;
        const int ARCANE_CHANCE = 15;
        const int SHADOW_ATTACK = 2, SHADOW_LIFE = 3;
        const double DOLL_MAGIC_SCALE = 500.0;
        static readonly int[] SONG_EFFECTS = { 211, 212, 213, 214, 215, 216, 217, 218, 220, 222, 223 };
        static readonly int[] DANCE_EFFECTS = { 195, 196, 197, 198, 199, 201, 202, 205, 219, 221 };
        static readonly bool[] IsSongEffect = Flags(SONG_EFFECTS), IsDanceEffect = Flags(DANCE_EFFECTS);
        static readonly bool[] StatusEffect = MakeStatusEffects();
        static readonly bool[] DispelAlways = Flags(new[] { 27, 171, 325, 326, 327, 328, 329, 101, 102, 181, 189, 191, 193, 194 });
        static readonly bool[] DispelIfRaised = Flags(new[] { 21, 26, 28, 31, 41, 42, 43, 44, 45, 46, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173, 174, 184, 185, 186 });

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
        public static string AilmentNameOf(int e) => AilmentName[e];
        public static int AilmentResistOf(int e) => AilmentResist[e];
        public static bool IsSong(int e) => IsSongEffect[e];
        public static bool IsDance(int e) => IsDanceEffect[e];

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
        readonly HashSet<(Unit, int)> spent = new HashSet<(Unit, int)>();
        // Recorder, by position
        public int[] RecDamage = new int[64], RecActions = new int[64];
        // the full recorder (null when nobody asks for it)
        public Recorder Rec;
        Dictionary<Unit, int> damageByTarget;
        // Cover: units with Cover that took a hit in place of another, in the order they did
        readonly List<(Unit unit, int count)> covered = new List<(Unit, int)>();
        readonly List<Unit> guarding = new List<Unit>();
        // the "mean" mode of the policies: the random term of the wait is the mean of the six values
        public bool MeanWait;

        public Battle(GameData data, List<Unit> party, List<Unit> enemies, PyRandom rng, Policy choose, BattleOptions options, Zone zone,
                      double maxTime = 400.0)
        {
            Data = data; Rng = rng;
            Units = new List<Unit>(party.Count + enemies.Count + 16);
            Units.AddRange(party);
            Units.AddRange(enemies);
            for (int k = 0; k < Units.Count; k++) { Units[k].Position = k; Units[k].Roster = roster; }
            roster.Version++;
            ChooseMember = choose;
            Options = options ?? new BattleOptions();
            ZoneInfo = zone;
            MaxTime = maxTime;
            if (Options.Record) Rec = new Recorder();
            if (RecDamage.Length < Units.Count + 16) { RecDamage = new int[Units.Count + 32]; RecActions = new int[Units.Count + 32]; }
        }

        void Grow(int position)
        {
            if (position >= RecDamage.Length)
            {
                Array.Resize(ref RecDamage, position * 2 + 8);
                Array.Resize(ref RecActions, position * 2 + 8);
            }
        }

        /// <summary>Objects the policy uses to examine the options of a decision one after the other (it makes the action it chooses afresh).</summary>
        public readonly Action ScratchAction = new Action(null, AKind.Attack);
        public Skill[] CandidateSkills = new Skill[32];
        public int[] CandidateLevels = new int[32];

        public struct OptionEntry
        {
            public Unit Owner;
            public int Tp;
            public bool Silenced, Frozen;
            public List<(Skill skill, int level)> List;
        }

        /// <summary>The skills each unit could use at her last decision, by position (Policy.Options).</summary>
        public OptionEntry[] OptionCache = new OptionEntry[16];

        // --- sides -----------------------------------------------------------------------------------------
        // The lists of the units of one side are worked out again only when a unit has fallen, risen or joined since they were made.
        // The arrays are never changed once made, so a caller that holds one while the battle goes on keeps the list as it was.
        readonly Roster roster = new Roster();
        int cacheVersion = -1;
        Unit[] sideAlive0, sideAlive1, sideAll0, sideAll1, targetable0, targetable1;

        void Refresh()
        {
            if (cacheVersion == roster.Version) return;
            cacheVersion = roster.Version;
            sideAlive0 = sideAlive1 = sideAll0 = sideAll1 = targetable0 = targetable1 = null;
        }

        Unit[] Build(int side, bool aliveOnly)
        {
            int n = 0;
            foreach (var u in Units) if (u.Side == side && (u.Alive || !aliveOnly)) n++;
            var r = new Unit[n];
            int k = 0;
            foreach (var u in Units) if (u.Side == side && (u.Alive || !aliveOnly)) r[k++] = u;
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
            var r = new List<Unit>();
            foreach (var u in SideArray(side, false)) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) r.Add(u);
            return r.ToArray();
        }

        void AddUnit(Unit unit)
        {
            unit.Position = Units.Count;
            unit.TieKey = unit.Kind == Kind.Enemy ? 994 - unit.Position : -unit.Position;     // a unit made during the battle comes after the others on a tie
            unit.Roster = roster;
            Units.Add(unit);
            roster.Version++;
            Grow(unit.Position);
        }

        public List<Unit> Side(int side, bool aliveOnly = true)
        {
            var r = new List<Unit>(8);
            foreach (var u in Units) if (u.Side == side && (u.Alive || !aliveOnly)) r.Add(u);
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

        public bool Over()
        {
            bool party = false, enemies = false;
            foreach (var u in Units)
            {
                if (!u.Alive) continue;
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member) party = true;
                if (u.Side == Unit.ENEMIES) enemies = true;
            }
            return !party || !enemies;
        }

        // --- the order of turns ------------------------------------------------------------------------------
        public double Wait(Unit unit, Action action = null, bool chanting = false)
        {
            int statName = Unit.AGI;
            double f1 = 1.0, f2 = 1.0;
            var s = new PySum();
            foreach (int e in SPEED_BUFFS) AddStatus(ref s, unit, e);
            double bonus = s.Result + unit.Passive(316, 0.0) * (unit.Kind == Kind.Doll ? 1 : 0);
            if (unit.Hp <= 0.4 * unit.MaxHp && unit.Has(261)) bonus += unit.Value(261);
            double enchant = F.SpeedEnchantBonus(unit.Pieces(51), unit.Pieces(52), unit.Pieces(53));
            if (action != null)
            {
                if (chanting)
                {
                    int cs = action.Skill != null ? action.Skill.ChantStat : (action.Atk != null ? action.Atk.ChantStat : 0);
                    statName = cs == 1 ? Unit.INT : cs == 2 ? Unit.RES : Unit.AGI;
                    double? cspeed = action.ChantSpeed;
                    f2 = cspeed.HasValue && cspeed.Value != 0 ? cspeed.Value : 1.0;
                    var c = new PySum();
                    foreach (int e in CHANT_SPEED_BUFFS) AddStatus(ref c, unit, e);
                    bonus = c.Result + unit.Passive(265, 0.0) + unit.Passive(281, 0.0);
                    enchant = F.SpeedEnchantBonus(unit.Pieces(54), unit.Pieces(55), unit.Pieces(56), 0.20, 0.10, 0.20);
                }
                else if (action.Kind == AKind.Skill || action.Kind == AKind.Enemy)
                {
                    f1 = action.Speed + (unit.HasUnique && unit.UniqueEffect == 352 ? unit.Value(352) : 0.0);
                    if (action.Skill != null && action.Skill.IsMagic) f2 = f1;
                    bool song = false, dance = false;
                    foreach (int e in SONG_EFFECTS) if (action.Has(e)) { song = true; break; }
                    if (song) bonus += unit.Value(276);
                    foreach (int e in DANCE_EFFECTS) if (action.Has(e)) { dance = true; break; }
                    if (dance) bonus += unit.Value(277);
                }
            }
            int stat = unit.Stat(statName);
            double random = MeanWait ? F.SPEED_RANDOM_MEAN : F.SPEED_RANDOM[Rng.ChoiceIndex(F.SPEED_RANDOM.Length)];
            double value = F.TurnValue(stat, unit.Weight, unit.Level, f1 * f2, bonus + enchant, unit.St[122] != null,
                                       action != null && action.Kind == AKind.Defend, false, random);
            if (chanting && unit.Pieces(298) != 0) value = Math.Min(F.VALUE_CAP, value + 0.25);
            return Math.Max(1.0 - F.VALUE_CAP, 1.0 - value);
        }

        public void Start()
        {
            // members, enemies and dolls start at the value of a plain action (0x449176 - 0x449180: _SetTime, slot 0x20 of the battle
            // class); the summon and a guest at a random gauge (0x449194 - 0x4491ba), unless an enemy of the battle has bit 1 of its
            // flags word (+0x54 of its status data, 0x439f3f - 0x439f46, the byte +0x33 of the battle), when they take the plain value too
            int members = 0, enemies = 0;
            foreach (var u in Units)
                u.TieKey = u.Kind == Kind.Member ? 999 - members++ : u.Kind == Kind.Enemy ? 994 - enemies++
                         : u.Kind == Kind.Summon ? (u.IsGuest ? 929 : 930) : -u.Position;
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
            if (!ambush && Rng.RandRange(100) < RANDOM_ORDER)
                foreach (var u in Units) u.NextTime = 1.0 - Rng.RandRange(93) / 100.0;
            foreach (var u in Units)
                if (u.Has(300) && Roll(u.Value(300))) u.NextTime = 0.0;
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
            Trace?.Begin(this);
            Start();
            Trace?.Started(this);
            LowestHp = PartyHpShare();
            while (!Over() && Time < MaxTime && Actions < MaxActions)
            {
                Unit unit = null;
                foreach (var u in Units)
                {
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
                    if (u.Alive) enemiesAlive = true;
                    enemyDamage += RecDamage[u.Position];
                    enemyActions += RecActions[u.Position];
                }
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member)
                {
                    if (u.Alive) { anyMemberAlive = true; alive++; }
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

        void Turn(Unit unit)
        {
            Actions++;
            unit.TurnsTaken++;
            unit.Defending = false;
            bool again = unit.ExtraTurn && unit.ExtraUnique;
            if (unit.Has(311))
            {
                int n = PyMath.Int(unit.Value(311));
                for (int i = 0; i < Math.Min(Math.Max(n, 0), ESARHADDON_ORDER.Length) && i < ESARHADDON_ORDER.Length; i++)
                    unit.PopStatus(ESARHADDON_ORDER[i]);
            }
            if (unit.SamsaraState != 0 && (unit.SamsaraState == 2 || unit.Hp < unit.MaxHp / 2.0))
            {
                unit.Samsara = new int[8];
                for (int i = 0; i < 8; i++) unit.Samsara[i] = (Rng.RandRange(2) + 1) * SAMSARA_STEP;
                unit.SamsaraState = 2;
            }
            // state 2: Third Eye Wide of each opponent
            foreach (var other in OpponentsArray(unit))
            {
                if (other.HasUnique && other.UniqueEffect == 345 && Roll(other.UniqueValue))
                {
                    int[] choices = { 113, 115, 116, 114, 117, 118, 74 };
                    int effect = choices[Rng.ChoiceIndex(choices.Length)];
                    if (effect != 74) ApplyAilment(other, unit, effect, 0.75, null);
                }
            }
            bool acted = false;
            Lost lost = LostTurn(unit);
            if (lost != Lost.No)
            {
                Rec?.TurnsLost.Add(new RecKey(unit), 1);
            }
            else
            {
                BeforeAction(unit);
                Action action = unit.Alive ? NextAction(unit) : null;
                if (action != null)
                {
                    acted = true;
                    Perform(action);
                }
            }
            EndOfTurn(unit, acted, lost != Lost.Skip && !again);
            Undaunted();
        }

        void BeforeAction(Unit unit)
        {
            if (!unit.HasUnique) return;
            int effect = unit.UniqueEffect;
            double value = unit.UniqueValue;
            if (effect == 446 && unit.Items.Count > 0 && Roll(value) && ChooseMember != null)
            {
                bool hurt = false;
                foreach (var m in AlliesArray(unit)) if (m.Kind == Kind.Member && m.HpRatio < 0.6) { hurt = true; break; }
                var item = Policy.ActItem(this, unit, hurt ? "heal" : "tp", null);
                if (item != null) UseItem(item);
            }
            if (effect == 357 && Roll(value))
            {
                foreach (var other in OpponentsArray(unit))
                {
                    other.SetStatus(new Status(41, -0.1, TRANQUIL_TURNS, unit));
                    other.SetStatus(new Status(43, -0.1, TRANQUIL_TURNS, unit));
                }
            }
            if (effect == 350 && Roll(value))
            {
                // one doll of the other side, drawn evenly (0x437787 - 0x437845): never the summon or a guest, never more than one
                var list = new List<Unit>();
                foreach (var u in Units) if (u.Side != unit.Side && u.Alive && u.Kind == Kind.Doll) list.Add(u);
                if (list.Count > 0) RemoveDoll(list[Rng.ChoiceIndex(list.Count)]);
            }
            if (effect == 448 && Roll(value))
            {
                bool any = false;
                foreach (var u in Units) if (u.Alive && u.ShadowOf == unit) { any = true; break; }
                if (!any) AddShadow(unit);
            }
        }

        void AddShadow(Unit owner)
        {
            var rec = new DollRec { Name = owner.Name + "'s shadow", Turns = new[] { SHADOW_LIFE }, Range = null, Actions = Array.Empty<int>(), Skill = T.NONE };
            var unit = UnitFactory.BuildDoll(owner, rec, 1, null);
            for (int s = 0; s < 6; s++) unit.Base[s] = owner.Stat(s);
            unit.Base[Unit.ATK] *= SHADOW_ATTACK;
            unit.AdoptPassives((double[])owner.Pv.Clone());
            unit.PvInt = owner.PvInt != null ? (bool[])owner.PvInt.Clone() : null;
            unit.SetEnchants((int[])owner.Enchants.Clone());
            unit.Swing = owner.Swing;
            unit.ShadowOf = owner;
            unit.Position = Units.Count;
            unit.NextTime = Time + Wait(unit);
            AddUnit(unit);
        }

        

        void Undaunted()
        {
            foreach (var u in Units)
            {
                if (!u.Alive && u.Kind == Kind.Member && u.HasUnique && u.UniqueEffect == 355 && Roll(u.UniqueValue))
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

        Lost LostTurn(Unit unit)
        {
            if (!unit.Alive) return Lost.Skip;
            if (unit.St[120] != null || unit.St[116] != null) return Deny(unit, Lost.Skip);
            if (unit.St[115] != null && Rng.RandRange(100) < 30) return Deny(unit, Lost.Skip);
            foreach (var other in OpponentsArray(unit))
            {
                if (other.Has(259) && Roll(other.Value(259))) return Deny(unit, Lost.Empty);
                if (other.Has(283) && Roll(other.Value(283))) return Deny(unit, Lost.Skip);
            }
            if (unit.Has(203) && Roll(unit.Value(203))) return Deny(unit, Lost.Skip);
            return Lost.No;
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
            if (unit.Side == Unit.PARTY && unit.Kind == Kind.Member && ChooseMember != null) { StartDecision(); try { action = ChooseMember.Choose(this, unit); } finally { EndDecision(); } }
            else action = Ai.Choose(this, unit);
            if (action == null) return null;
            if ((unit.St[117] != null && action.Skill != null && action.Skill.IsMagic) ||
                (unit.St[114] != null && action.Skill != null && action.Skill.IsTechnique))
                action = new Action(unit, AKind.Attack);
            double? speed = action.ChantSpeed;
            if (speed.HasValue && speed.Value != 0 && !(unit.HasUnique && unit.UniqueEffect == 358 && Roll(unit.UniqueValue)))
            {
                Pay(action);
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

        void Pay(Action action)
        {
            int cost = action.TpCost;
            if (cost <= 0) return;
            var unit = action.Actor;
            bool technique = action.Skill != null && action.Skill.IsTechnique;
            if (unit.Pieces(technique ? 246 : 248) != 0) cost = PyMath.Int(cost * 0.8);
            if (unit.Pieces(technique ? 247 : 249) != 0) cost = PyMath.Int(cost * 0.6);
            cost = Math.Max(1, cost);
            if (unit.Has(266)) cost = Math.Max(1, cost - PyMath.Int(Math.Ceiling(cost * unit.Value(266))));
            unit.Tp = Math.Max(0, unit.Tp - cost);
            Rec?.TpSpent.Add(new RecKey(unit), cost);
        }

        readonly Dictionary<Unit, Action> lastAction = new Dictionary<Unit, Action>();

        void EndOfTurn(Unit unit, bool acted, bool ticks)
        {
            if (unit.Alive && ticks) Tick(unit);
            if (!unit.Alive) return;
            Action last = null;
            if (acted) lastAction.TryGetValue(unit, out last);
            double wait;
            if (unit.Chant != null) wait = Wait(unit, unit.Chant, true);
            else wait = Wait(unit, last);
            unit.NextTime = Time + wait;
            if (unit.Extra > 0)
            {
                unit.Extra--;
                unit.NextTime = Time;
                unit.ExtraTurn = true;
            }
            else if (unit.ExtraTurn)
            {
                unit.ExtraTurn = false;
                unit.ExtraUnique = false;
            }
            else if (acted && unit.Chant == null && !Over())
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

        readonly int[] tickScratch = new int[GameData.MaxEffect];

        void Tick(Unit unit)
        {
            if (unit.HasPassive(246) && unit.St[246] == null) Restore(unit, PyMath.Int(unit.MaxHp * unit.Passive(246)));
            if (unit.HasPassive(247) && unit.St[247] == null && unit.Side == Unit.PARTY)
                unit.Tp = Math.Min(unit.MaxTp, unit.Tp + PyMath.Int(unit.Passive(247)));
            // list(unit.statuses): a snapshot of the effects, here at the start of the walk
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
                    foreach (var ally in AlliesArray(unit)) Restore(ally, PyMath.Int(s.Value * (1 + 10 * bonus)));
                }
                else if (effect == 216)
                {
                    double bonus = s.HasData ? s.Data : 0.0;
                    var allies = AlliesArray(unit);
                    var ally = allies[Rng.ChoiceIndex(allies.Length)];
                    ally.Tp = Math.Min(ally.MaxTp, ally.Tp + PyMath.Int(s.Value + 100 * bonus));
                }
                else if (effect == 113 && unit.St[116] == null)
                {
                    int amount = Math.Min(POISON_CAP, PyMath.Int(unit.MaxHp * POISON_SHARE));
                    if (amount <= 0 || amount >= unit.Hp) amount = unit.Hp - 1;
                    LoseHp(unit, amount, null);
                }
                else if (effect == 199 || effect == 339)
                {
                    int amount = PyMath.Int(unit.MaxHp * s.Value);
                    if (s.HasData) amount = Math.Min(amount, PyMath.Int(s.Data));
                    LoseHp(unit, amount, s.Source);
                }
                else if (effect == 200)
                {
                    int amount = PyMath.Int(unit.MaxHp * s.Value);
                    if (s.HasData) amount = Math.Min(amount, PyMath.Int(s.Data));
                    unit.Tp = Math.Max(0, unit.Tp - amount);
                }
                else if (effect == 204 && unit.Side == Unit.PARTY)
                {
                    unit.Pep = Math.Max(70.0, Math.Min(130.0, unit.Pep + s.Value));
                }
                if (IsAilment[effect] && unit.St[effect] != null && effect != 119 && effect != 123)
                {
                    int chance = s.HasData ? PyMath.Int(s.Data) : 0;
                    if (Rng.RandRange(100) < chance)
                    {
                        unit.PopStatus(effect);
                        continue;
                    }
                    s.WithData(chance + 10);
                }
                if (s.Turns > 0 && unit.St[effect] != null)
                {
                    s.Turns -= 1;
                    if (s.Turns <= 0) unit.PopStatus(effect);
                }
            }
            if (unit.Kind == Kind.Doll)
            {
                unit.Life -= 1;
                if (unit.Life <= 0) RemoveDoll(unit);
            }
        }

        // --- performing an action ----------------------------------------------------------------------------
        public void Perform(Action action)
        {
            var unit = action.Actor;
            lastAction[unit] = action;
            Grow(unit.Position);
            RecActions[unit.Position]++;
            Rec?.Actions.Add(new RecKey(unit), 1);
            Trace?.Perform(this, action);
            if (action.Kind == AKind.Chant)
            {
                lastAction[unit] = null;
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
            if (!action.Chanting && action.Kind == AKind.Skill && !action.ChantSpeed.HasValue) Pay(action);
            string key = action.SourceName ?? "Attack";
            Rec?.SkillUses.Add(new RecKey(unit, key), 1);
            unit.LastSkillId = action.SourceId;
            unit.Uses.TryGetValue(key, out int used);
            unit.Uses[key] = used + 1;
            foreach (int randomEffect in RANDOM_MOVES)
            {
                if (action.Has(randomEffect))
                {
                    action = RandomMove(action, randomEffect);
                    if (action == null) return;
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
            int hits = NumberOfHits(action);
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
            reprisal.Clear();
            damageByTarget = Rec != null ? new Dictionary<Unit, int>() : null;
            foreach (var target in targets)
            {
                for (int h = 0; h < hits; h++)
                {
                    if (!unit.Alive || (!target.Alive && !action.Has(105))) break;
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
            // Reprisal after the action: the first target, in order, whose record is set and who still bears it and stands (0x424d50 -
            // 0x424de7); one counter for the whole action
            foreach (var target in targets)
            {
                if (reprisal.TryGetValue(target, out bool set) && set && target.Has(249) && target.Alive)
                {
                    Counter(target, unit);
                    break;
                }
            }
            reprisal.Clear();
            if (action.Has(SACRIFICE) && unit.Alive) LoseHp(unit, unit.MaxHp, unit);
            if (damageByTarget != null)
            {
                foreach (var kv in damageByTarget)
                    if (unit.Side == Unit.ENEMIES && kv.Key.Side == Unit.PARTY) Rec.LargestHit.Max(new RecKey(unit), kv.Value);
                damageByTarget = null;
            }
            // Support Shot: the givers are units below 2000 of the attacker's side, and a doll's attack starts none (P7.3 of the audit)
            if (action.Kind == AKind.Attack && !NotACandidate(unit))
            {
                foreach (var ally in TargetableArray(unit.Side))
                {
                    if (ally != unit && ally.Has(260) && Roll(ally.Value(260)))
                    {
                        Unit first = null;
                        foreach (var t in targets) if (t.Alive) { first = t; break; }
                        if (first == null)
                        {
                            var opp = OpponentsArray(unit);
                            if (opp.Length > 0) first = opp[0];
                        }
                        if (first != null) Resolve(new Action(ally, AKind.Attack), first, 0);
                        break;
                    }
                }
            }
        }

        static readonly Unit[] NoUnits = new Unit[0];
        readonly Dictionary<Unit, bool> reprisal = new Dictionary<Unit, bool>();

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
                        var order = new List<Unit>();
                        foreach (var t in foes) if (t != chosen) order.Add(t);
                        InsertionSortByTime(order);
                        var res = new List<Unit> { chosen };
                        int n = Math.Max(0, PyMath.Int(action.Val(EXTRA_TARGETS, 0)) - 1);
                        for (int i = 0; i < Math.Min(n, order.Count); i++) res.Add(order[i]);
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

        static readonly Dictionary<(int, int), int> ShareRows = new Dictionary<(int, int), int>
        {
            { (1, 1), 0 }, { (1, 0), 0 }, { (2, 2), 1 }, { (2, 1), 2 }, { (3, 3), 3 }, { (3, 2), 4 }, { (3, 1), 5 }, { (4, 3), 6 },
            { (4, 2), 7 }, { (4, 1), 8 }, { (5, 3), 9 }, { (5, 2), 10 },
        };

        static int[] TargetShareRow(int size, int front)
        {
            if (size == 0) return new[] { 100 };
            front = Math.Max(1, Math.Min(Math.Min(front, 3), size));
            if (!ShareRows.TryGetValue((size, front), out int row))
            {
                int best = int.MinValue;
                foreach (var k in ShareRows.Keys) if (k.Item1 == size && k.Item2 > best) best = k.Item2;
                if (best == int.MinValue) throw new InvalidOperationException("max() of an empty sequence");
                row = ShareRows[(size, best)];
            }
            return size <= 5 ? F.TARGET_SHARE[row] : F.TARGET_SHARE[9];
        }

        Unit[] pickOrdered = new Unit[16];
        int[] pickWeights = new int[16];

        Unit WeightedPick(Unit enemy, Unit[] party)
        {
            if (pickOrdered.Length < party.Length) { pickOrdered = new Unit[party.Length * 2]; pickWeights = new int[party.Length * 2]; }
            var ordered = pickOrdered;
            int count = 0, frontCount = 0;
            foreach (var u in party) if (u.Front) { ordered[count++] = u; frontCount++; }
            foreach (var u in party) if (!u.Front) ordered[count++] = u;
            var row = TargetShareRow(count, frontCount);
            var weights = pickWeights;
            long total = 0;
            for (int k = 0; k < count; k++)
            {
                var u = ordered[k];
                int share = k < row.Length ? row[k] : row[row.Length - 1];
                double provoked = 0.0;
                if (enemy.St[170] != null)
                    foreach (var (pu, pv) in enemy.ProvokedBy) if (pu == u) { provoked = pv; break; }
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
            bool rondo = action.Has(210) || action.Actor.Has(210);
            int hits = 0;
            bool found = false;
            foreach (var m in MULTI_HIT)
            {
                if (action.Has(m.effect))
                {
                    var table = rondo ? m.rondo : m.weights;
                    hits = m.baseHits + Weighted(m.picks, table);
                    found = true;
                    break;
                }
            }
            if (!found)
            {
                double v = action.Val(93, 1);
                hits = PyMath.Int(v != 0 ? v : 1);
                if (action.Kind == AKind.Attack)
                {
                    int extra = 0;
                    if (action.Actor.Has(252) && Roll(action.Actor.Value(252))) extra += 3;
                    if (action.Actor.Has(251) && Roll(action.Actor.Value(251))) extra += 2;
                    hits = extra != 0 ? extra : 1;
                }
            }
            if (action.Has(178)) hits += PyMath.Int(action.Val(178, 0)) + 1;
            return Math.Max(1, hits);
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
                if (!landed) return;
                if (Voided(action, target)) return;
            }
            int dealt = 0;
            if (Aimed(action, target) && !action.Has(25) && (action.Physical || action.Magic))
            {
                dealt = Damage(action, target, index);
                if (damageByTarget != null) { damageByTarget.TryGetValue(target, out int sofar); damageByTarget[target] = sofar + dealt; }
            }
            AfterHit(action, target, dealt);
        }

        Unit Redirect(Action action, Unit target)
        {
            int c = action.TargetCode;
            if (c == T.SINGLE || c == T.RANDOM)
            {
                var covers = new List<Unit>();
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

        bool Voided(Action action, Unit target)
        {
            var unit = action.Actor;
            int attr = action.Attr;
            // NULLIFY_ENCHANTS in the order of the dict: 120 slash, 121 stab, 122 bash, 123 every blow, 124 fire ... 128 lightning
            for (int enchant = 120; enchant <= 128; enchant++)
            {
                if (target.Pieces(enchant) != 0)
                {
                    bool attrMatch = enchant == 123 ? T.Physical(attr) : enchant <= 122 ? attr == enchant - 119 : attr == enchant - 120;
                    bool blowsOnly = enchant <= 123;
                    if (attrMatch && (action.Physical || !blowsOnly)) return true;
                }
            }
            if (target.Has(192) && attr != T.NEUTRAL) return true;
            if (target.Has(182) && (action.Reach == T.SHORT || action.Reach == T.MID)) return true;
            if (target.HasUnique && target.UniqueEffect == 349 && Roll(target.UniqueValue)) return true;
            if (target.Has(PRETEND) && action.Physical && Roll(target.Value(PRETEND)))
            {
                Counter(target, unit);
                return true;
            }
            if (target.Has(285) && !spent.Contains((target, 285)) && (action.Physical || action.Magic))
            {
                target.PopStatus(285);
                spent.Add((target, 285));
                return true;
            }
            if (target.Has(KNOCK_DOWN) && action.Physical && action.Reach == T.LONG &&
                (unit.Side == Unit.ENEMIES || unit.Weapon != null) && Roll(target.Value(KNOCK_DOWN)))
            {
                Counter(target, unit);
                return true;
            }
            if (target.St[180] != null && action.Physical)
            {
                if (Roll(target.St[180].Value)) target.PopStatus(180);
                return true;
            }
            if (target.Has(250) && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
            {
                if (Roll(target.Value(250)))
                {
                    Counter(target, unit);
                    return true;
                }
            }
            if (target.HasUnique && target.UniqueEffect == 346 && action.Reach == T.SHORT && Roll(target.UniqueValue))
            {
                unit.SetStatus(new Status(122, 1.0, 0, target).WithData(SUGAR_COMA_RECOVERY));
                unit.SetStatus(new Status(168, -0.2, SUGAR_COMA_TURNS, target));
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
            if (roll < PyMath.Round((chance - dodge) * 100)) return true;
            if (dodge != 0 && roll < PyMath.Round(chance * 100) && target.Alive) Counter(target, action.Actor);
            return false;
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

        double SumFirst(Action action, Unit unit, int[] effects)
        {
            var s = new PySum();
            foreach (int e in effects) AddFirst(ref s, action, unit, e);
            return s.Result;
        }

        static double SumValue(Unit u, int[] effects)
        {
            var s = new PySum();
            foreach (int e in effects) AddValue(ref s, u, e);
            return s.Result;
        }

        double CriticalRateOf(Action action, Unit unit, Unit target, int earlier)
        {
            var s = new PySum();
            foreach (int e in CRIT_TERMS) AddFirst(ref s, action, unit, e);
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

        public bool Special(Action action)
        {
            return action.Has(8) || action.Has(12) || action.Has(138) || action.Has(140) || action.Has(141) || action.Has(142) ||
                   action.Has(434) || action.Has(435);
        }

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
                if (!action.Magic && actor.HasUnique && actor.UniqueEffect == 440 && actor.Pep > 100)
                    amount += PyMath.Int(amount * (actor.Pep - 100) / Math.Max(1.0, actor.UniqueValue) / 100.0);
            }
            if (target.St[116] != null && !special) amount = amount * F.SLEEP_NUM / F.SLEEP_DEN;
            if (!special && action.Actor.Pieces(F.AILING_ENCHANT) != 0 && AnyAilment(target)) amount += PyMath.Int(amount * F.AILING_SHARE);
            if (action.Has(86) && target.Kind == Kind.Member && target.ClassId >= F.MAGIC_USER_LOW && target.ClassId < F.MAGIC_USER_HIGH) amount += amount;
            if (action.Magic)
            {
                if (action.TryVal(296, out double cap)) amount = Math.Min(amount, PyMath.Int(cap));
            }
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

        /// <summary>The first living unit of the target's side that has Demon Wall.</summary>
        /// <summary>Demon Wall (356) lowers only the blows of an enemy of race 5, 7 or 8 (0x44cb6c - 0x44cba2; races read at
        /// 0x557e1c, 0x557e7c, 0x557eac); the wall is the first unit of the target's side that bears it.</summary>
        Unit DemonWallOf(Unit target, Unit attacker)
        {
            if (attacker.Side != Unit.ENEMIES || attacker.Kind != Kind.Enemy || F.DEMON_WALL_RACES.IndexOf(attacker.Race) < 0) return null;
            foreach (var u in Units) if (u.Side == target.Side && u.Alive && u.Has(DEMON_WALL)) return u;
            return null;
        }

        static bool AnyAilment(Unit u)
        {
            foreach (int e in AILMENT_IDS) if (u.St[e] != null) return true;
            return false;
        }

        int CountAilments(Unit u)
        {
            int n = 0;
            foreach (int e in AILMENT_IDS) if (u.St[e] != null) n++;
            return n;
        }

        public double PhysicalDamageValue(Action action, Unit target, int index, double critFactor, bool expect, bool critical, out int immediateZero)
        {
            immediateZero = 0;
            var unit = action.Actor;
            bool furious = action.Furious;
            double modifiers = First(action, unit, 26) + (action.Atk != null ? action.Atk.Power : 0.0);
            {
                var s = new PySum();
                foreach (int e in ATTACK_STATUS_MODIFIERS) AddStatus(ref s, unit, e);
                modifiers += s.Result;
            }
            if (unit.HasUnique && unit.UniqueEffect == 443) modifiers += unit.UniqueValue;
            if (unit.Kind == Kind.Doll && unit.Owner != null)
                modifiers += unit.Owner.Passive(286, 0.0) + Math.Min(0.05, 0.02 * unit.Owner.Pieces(304) + 0.01 * unit.Owner.Pieces(305));
            if (action.Has(111) && unit.Weapon != null && unit.Weapon.TwoHanded && unit.Weapon.Type == 3) modifiers += action.Val(111, 0);
            double swing = expect ? 0.0 : Swing(unit);
            double atk = unit.Stat(Unit.ATK);
            if (action.Has(49)) atk = unit.Stat(Unit.INT);
            if (action.Has(47)) atk = unit.Stat(Unit.RES);
            if (action.Has(50)) atk = atk * action.Val(50, 0);
            double targetMods;
            {
                var s = new PySum();
                foreach (int e in DEFENCE_MODIFIERS) AddStatus(ref s, target, e);
                targetMods = s.Result;
            }
            double times = action.Val(73, 1.0); if (times == 0) times = 1.0;
            int reach = action.Reach;
            int dist = F.Distance(!unit.Front, !target.Front);
            double cut = 1.0 - (0.10 * target.Pieces(66) + 0.05 * target.Pieces(67) + 0.08 * target.Pieces(70) + 0.04 * target.Pieces(71));
            bool defending = target.Defending || guarding.Contains(target);
            int resistIndex = T.ResistIndex(action.Attr);
            int resistance = resistIndex >= 0 ? target.Resistance(resistIndex) : 0;
            double raceBonus = (action.Has(88) && (target.Race == 5 || target.Race == 7 || target.Race == 8)) ? action.Val(88, 0) : 0.0;
            if (action.Has(87) && target.Race == 5) { immediateZero = 1; return 0; }
            double race = (RaceFactor(unit, target) + raceBonus) * ElementFactor(unit, target, action.Attr);
            double other = target.Value(190) + unit.StatusValue(191) + FullHpBonus(unit) + LevelBonus(unit, target);
            var guard = target.St[MATERIAL_GUARD];
            if (guard != null && (guard.Source == null || (guard.Source.Alive && guard.Source.Shield))) other += guard.Value;
            if (target.Side == Unit.PARTY && !target.Front)
            {
                bool any = false; double min = 0;
                foreach (var m in AlliesArray(target))
                {
                    double g = m.Passive(308, 0.0);       // passives.get(308) truthy only when non-zero
                    if (m.HasPassive(308) && g != 0.0) { if (!any || g < min) { min = g; any = true; } }
                }
                if (any) other += min;
            }
            // Positive Trance is an integer step after the cut (0x44ccb2, P6.9 of the audit); the expectation keeps it in the bonus
            if (expect && unit.HasUnique && unit.UniqueEffect == 440 && unit.Pep > 100)
                other += (unit.Pep - 100) / Math.Max(1.0, unit.UniqueValue) / 100.0;
            if (action.Has(136)) other += action.Val(136, 0) * index;
            if (action.Has(DARK_QUEST) || unit.Has(DARK_QUEST))
                other += First(action, unit, DARK_QUEST) * CountAilments(unit);
            if (action.Has(71))
            {
                int n = 0;
                for (int i = 0; i < target.StCount; i++) if (!IsAilment[target.StatusAt(i)]) n++;
                other += action.Val(71, 0) * n;
            }
            double attackZone = ZoneFactor(unit, action);
            double value = F.PhysicalDamage(atk * attackZone, target.Stat(Unit.DEF), modifiers, targetMods,
                                            Math.Min(50, 4 * unit.Pieces(29) + 2 * unit.Pieces(30)),
                                            Math.Min(50, 4 * target.Pieces(33) + 2 * target.Pieces(34)),
                                            swing, times, action.Has(69) || furious, F.RangeFactor(reach, dist), cut, race, resistance,
                                            defending, expect ? critFactor : (critical ? F.CRIT_FACTOR : 1.0), other);
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

        double MagicValue(Action action, Unit target, bool expect, double critical, bool didCritical)
        {
            var unit = action.Actor;
            double power = action.Val(MAGIC_POWER, 0.0);
            if (unit.Kind == Kind.Doll && unit.Owner != null)
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
            double cut = Math.Max(-0.25, -(0.10 * target.Pieces(68) + 0.05 * target.Pieces(69) + 0.08 * target.Pieces(70) + 0.04 * target.Pieces(71))) + target.StatusValue(183);
            double other = target.Value(190) + FullHpBonus(unit) + LevelBonus(unit, target);
            cut += RaceGuard(unit, target) - 1.0;
            double targetMods;
            {
                var s = new PySum();
                foreach (int e in MAGIC_DEFENCE_MODIFIERS) AddValue(ref s, target, e);
                targetMods = s.Result;
            }
            // the swing of a spell is the spell's own (0x44dbc3 - 0x44dc18), never the caster's weapon; an enemy attack has none
            double swing = expect || action.Skill == null ? 0.0 : SwingOf(action.Skill.Swing);
            return F.MagicDamage(unit.Stat(Unit.INT) * ZoneFactor(unit, action), power, target.Stat(Unit.RES), mastery, modifiers,
                                 Math.Min(50, 4 * unit.Pieces(37) + 2 * unit.Pieces(38)), second, elementBoost, targetMods,
                                 Math.Min(50, 4 * target.Pieces(41) + 2 * target.Pieces(42)), swing, powerBoost, cut, resistance,
                                 critical, other);
        }

        int MagicDamageActual(Action action, Unit target, out bool critical)
        {
            var unit = action.Actor;
            critical = unit.Has(301) && Rng.RandRange(100) < F.MAGIC_CRIT_CHANCE;
            double value = MagicValue(action, target, false, critical ? F.MAGIC_CRIT_FACTOR : 1.0, critical);
            return Math.Max(0, PyMath.Int(value));
        }

        public double MagicDamageExpected(Action action, Unit target)
        {
            var unit = action.Actor;
            double critical = unit.Has(301) ? 1.0 + (F.MAGIC_CRIT_FACTOR - 1.0) * F.MAGIC_CRIT_CHANCE / 100.0 : 1.0;
            double value = MagicValue(action, target, true, critical, false);
            double damage = Math.Max(0.0, value);
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
            if (action.Has(149) && target.Adult == false) chance = 0.0;
            if (action.Has(150) && target.Adult == true) chance = 0.0;
            return PyMath.Int(chance) / 100.0;
        }

        double StabDodge(Action action, Unit target)
        {
            if (!(action.Physical && action.Attr == T.STAB && target.Has(STAB_EVASION)) || action.Furious) return 0.0;
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
            if (action.Has(25) || !(action.Physical || action.Magic || Special(action))) return 0.0;
            if (VisiblyVoided(action, target)) return 0.0;
            double hits = MeanHits(action);
            double chance = HitChance(action, target);
            if (action.Has(139) && target.St[116] != null && !target.Immune("instant death")) return chance * target.Hp;
            if (Special(action)) return chance * Math.Min(target.Hp, SpecialDamage(action, target));
            double perHit;
            if (action.Magic) perHit = MagicDamageExpected(action, target);
            else
            {
                var unit = action.Actor;
                double rate = CriticalRateOf(action, unit, target, 0);
                perHit = PhysicalDamageExpected(action, target, F.ExpectedCriticalFactor(rate));
            }
            if (target.St[116] != null && !Special(action)) perHit = perHit * F.SLEEP_NUM / F.SLEEP_DEN;
            if (!Special(action))
            {
                Unit wall = DemonWallOf(target, action.Actor);
                if (wall != null) perHit = Math.Max(0.0, perHit + perHit * wall.Value(DEMON_WALL));
            }
            if (!Special(action) && action.Actor.Pieces(F.AILING_ENCHANT) != 0 && AnyAilment(target)) perHit += perHit * F.AILING_SHARE;
            if (action.Has(86) && target.Kind == Kind.Member && target.ClassId >= F.MAGIC_USER_LOW && target.ClassId < F.MAGIC_USER_HIGH) perHit += perHit;
            if (action.Magic)
            {
                if (action.TryVal(296, out double cap)) perHit = Math.Min(perHit, cap);
            }
            return chance * hits * perHit;
        }

        public bool VisiblyVoided(Action action, Unit target)
        {
            return (target.Has(192) && action.Attr != T.NEUTRAL) || (target.Has(182) && (action.Reach == T.SHORT || action.Reach == T.MID));
        }

        public double MeanHits(Action action)
        {
            bool rondo = action.Has(210) || action.Actor.Has(210);
            foreach (var m in MULTI_HIT)
            {
                if (action.Has(m.effect))
                {
                    var table = rondo ? m.rondo : m.weights;
                    var s = new PySum();
                    for (int i = 0; i < table.Length; i++) s.AddFloat(m.picks[i] * table[i]);
                    var t = new PySum();
                    foreach (var w in table) t.AddFloat(w);
                    return m.baseHits + s.Result / t.Result;
                }
            }
            double hits = action.Val(93, 1);
            if (hits == 0) hits = 1;
            if (action.Kind == AKind.Attack)
            {
                double triple = action.Actor.Has(252) ? Math.Min(1.0, action.Actor.Value(252)) : 0.0;
                double dbl = action.Actor.Has(251) ? Math.Min(1.0, action.Actor.Value(251)) : 0.0;
                hits = 3 * triple + 2 * dbl + (1 - triple) * (1 - dbl);
            }
            return hits;
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
            if (action.Has(140)) return target.Side == Unit.PARTY || Options.HalveEnemies ? target.Hp / 2 : 0;
            if (action.Has(141)) return target.Hp * 3 / 4;
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
                var s = new PySum();
                if (target.Race != T.NONE && F.RACE_ATTACK.TryGetValue(target.Race, out var list))
                    foreach (var (e, share) in list) s.AddFloat(unit.Pieces(e) * share);
                double bonus = s.Result;
                var t = new PySum();
                foreach (var (e, ids) in F.RACE_SPECIAL) if (target.EnemyId != T.NONE && ids.Contains(target.EnemyId)) t.AddInt(unit.Pieces(e));
                bonus += t.Result;
                return 1.0 + bonus;
            }
            return RaceGuard(unit, target);
        }

        static double RaceGuard(Unit unit, Unit target)
        {
            if (unit.Side == Unit.ENEMIES && target.Side == Unit.PARTY && unit.Race != T.NONE && F.RACE_GUARD.TryGetValue(unit.Race, out var g))
                return 1.0 - F.RACE_GUARD_SHARE_SMALL * target.Pieces(g.small) - F.RACE_GUARD_SHARE_LARGE * target.Pieces(g.large);
            return 1.0;
        }

        static double ElementFactor(Unit unit, Unit target, int attr)
        {
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
            foreach (int slot in ZoneInfo.Slots)
            {
                if (slot == (physical ? 3 : 4)) factor *= f != null ? (physical ? f.UpA : f.UpB) : 1.0;
                if (slot == (physical ? 5 : 6)) factor *= f != null ? (physical ? f.DownA : f.DownB) : 1.0;
                if (slot >= 7 && slot <= 11 && action.Attr == slot - 3) factor *= f != null ? f.Element : 1.0;
            }
            return factor;
        }

        // --- damage taken ------------------------------------------------------------------------------------
        void TakeDamage(Unit target, int amount, Action action, bool critical)
        {
            var unit = action != null ? action.Actor : null;
            bool fatal;
            if (Options.SurvivalGuard ?? Data.SurvivalGuard) fatal = target.Hp > 1 && amount >= target.Hp - 1;
            else fatal = amount >= target.Hp;
            if (fatal && target.Has(254) && Roll(target.Value(254))) amount = target.Hp - 1;
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
            if (target.SamsaraState == 0 && target.Has(291)) target.SamsaraState = 1;
            if (target.Alive && amount > 0)
            {
                target.PopStatus(116);
                if (target.Chant != null || Performing(target))
                    Interrupt(target, amount, critical, action == null || !action.Magic);
            }
            if (target.HasUnique && target.UniqueEffect == 447 && unit != null && !unit.Has(307) && amount > 0)
            {
                int arcaneSet = Options.HasArcaneChance ? Options.ArcaneChance : Data.ArcaneChance;
                int arcane = arcaneSet != T.NONE && arcaneSet != 0 ? arcaneSet : ARCANE_CHANCE;
                if (Rng.RandRange(100) < arcane) LoseHp(unit, PyMath.Int(amount * target.UniqueValue), target);
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
            if (unit.Song.Count > 0 || unit.Dance.Count > 0) return true;
            foreach (var u in Units) if (u.Owner == unit && u.Alive && u.Kind == Kind.Doll) return true;
            return false;
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
            unit.Alive = false;
            unit.Chant = null;
            unit.ClearStatuses();
            if (Rec != null) { Rec.Deaths.Add(new RecKey(unit), 1); if (unit.Side == Unit.ENEMIES) Rec.Kills++; }
            var dolls = new List<Unit>();
            foreach (var u in Units) if (u.Owner == unit && u.Kind == Kind.Doll) dolls.Add(u);
            foreach (var d in dolls) RemoveDoll(d);
            foreach (var ally in Units)
            {
                int n = ally.StCount;
                if (n == 0) continue;
                var effects = ally.StatusOrder();
                foreach (int e in effects)
                {
                    var s = ally.St[e];
                    if (s != null && s.Source == unit && s.Kind == Status.SongKind) ally.PopStatus(e);
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
        void AfterHit(Action action, Unit target, int dealt)
        {
            var unit = action.Actor;
            bool hostile = target.Side != unit.Side;
            bool song = false;
            if (action.Skill != null && action.Skill.IsMagic && action.TpCost == 0)
                foreach (int e in SONG_EFFECTS) if (action.Has(e)) { song = true; break; }
            bool dance = false;
            foreach (int e in DANCE_EFFECTS) if (action.Has(e)) { dance = true; break; }
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
                if (effect == 75 && dealt != 0) { Restore(unit, PyMath.Int(dealt * value)); continue; }
                if (effect == 76 && dealt != 0) { unit.Tp = Math.Min(unit.MaxTp, unit.Tp + PyMath.Int(dealt * value)); continue; }
                if (effect == 2) continue;
                if (effect == 54 && hostile)
                {
                    if (!target.Immune("turn delay") && Rng.RandRange(100) < PyMath.Int(value * 100)) Delay(target);
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
                        var list = target.StatusOrder();
                        foreach (int e in list)
                        {
                            var s = target.St[e];
                            if (s != null && s.Source != null && s.Source.Side != target.Side) target.PopStatus(e);
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
                    EndParts(target, PartsAll);
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
                if (effect == ENEMIES_FLEE && hostile)
                {
                    if (Options.RandomBattle) target.Alive = false;
                    continue;
                }
                if (effect == 170)
                {
                    if (hostile)
                    {
                        int at = -1;
                        for (int q = 0; q < target.ProvokedBy.Count; q++) if (target.ProvokedBy[q].unit == unit) { at = q; break; }
                        if (at >= 0) target.ProvokedBy[at] = (unit, value); else target.ProvokedBy.Add((unit, value));
                        target.SetStatus(new Status(170, value, action.Turns, unit));
                    }
                    continue;
                }
                if (effect == 139 && hostile && target.St[116] != null && !target.Immune("instant death"))
                {
                    LoseHp(target, target.Hp, unit);
                    continue;
                }
                if (effect == 121 && hostile && !target.Immune("petrification") && target.Resistance(6) < 100 && !Nullified(target, 120))
                {
                    target.SetStatus(new Status(120, 1, 0, unit));
                    EndParts(target, PartsFor(121));
                    continue;
                }
                if (effect == 320 && hostile && AnyAilment(target))
                {
                    ApplyAilment(unit, target, 119, value, action);
                    continue;
                }
                if (effect == 168 && action.Has(79))
                {
                    if (!Roll(action.Val(79, 0))) continue;
                }
                if ((effect == 66 || effect == 80) && target.Side == Unit.PARTY)
                {
                    target.Pep = effect == 80 || target.Pep < 100 ? Math.Max(70.0, Math.Min(130.0, target.Pep + value)) : target.Pep;
                    continue;
                }
                if (effect == 295 || effect == 296) continue;
                if (kind == 4 || kind == 5 || StatusEffect[effect])
                {
                    if (song || dance) PerformSong(unit, action, target, effect, value, dance);
                    else
                    {
                        var st = new Status(effect, value, action.Turns, unit, action.SourceName, kind) { IsInt = action.EffIsInt(i) };
                        if (effect == 199 || effect == 200 || effect == 339)
                            if (action.TryVal(296, out double cap)) st.WithData(cap);
                        target.SetStatus(st);
                    }
                }
            }
            // the answers of the unit hit (0x423cd0): skipped whole when the attacker is a doll, the summon or a guest (0x423d0e - 0x423d38)
            if (hostile && dealt != 0 && !NotACandidate(unit))
            {
                // Dark Aura: each stat debuff is set to -0.1, not deepened (0x423d9b onward)
                if (target.Has(262) && action.Physical && action.Reach == T.SHORT && !unit.Has(304))
                {
                    int points = PyMath.Int(target.Value(262));
                    int[] order = { 45, 44, 43, 42, 41, 46 };
                    int n = Math.Max(0, Math.Min(points < 0 ? order.Length + points : points, order.Length));
                    for (int k = 0; k < n; k++) unit.SetStatus(new Status(order[k], -0.1, DARK_AURA_TURNS, target));
                }
                // Slow Target is a passive of the unit hit, which slows the unit that hit it (0x424317 - 0x42436b)
                if (target.Has(293) && action.Reach == T.SHORT && Roll(target.Value(293)) && !unit.Immune("slow"))
                {
                    unit.SetStatus(new Status(122, 1.0, 0, target).WithData(SLOW_TARGET_RECOVERY));
                    unit.SetStatus(new Status(168, -0.75, SLOW_TARGET_TURNS, target));
                }
                // Reprisal rolls on every hit and writes the result on the target's record, the last hit's roll standing
                // (0x424711); one counter at most is set up after the whole action (0x4247e0)
                if (target.Has(249) && action.Physical && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
                    reprisal[target] = Roll(target.Value(249));
            }
        }

        static readonly string[] PartsAll = { "chant", "song", "dance", "doll" };
        static string[] PartsFor(int effect)
        {
            switch (effect)
            {
                case 114: return new[] { "dance", "doll" };
                case 116: return PartsAll;
                case 117: return new[] { "chant", "song" };
                case 118: return PartsAll;
                case 121: return PartsAll;
                case 123: return PartsAll;
                default: return Array.Empty<string>();
            }
        }

        public static bool PerformanceSlotsTwo(Unit unit, bool dance) => unit.Has(dance ? 284 : 287);
        public static int PerformanceSlots(Unit unit, bool dance) => unit.Has(dance ? 284 : 287) ? 2 : 1;

        void PerformSong(Unit singer, Action action, Unit target, int effect, double value, bool dance)
        {
            int bonusEffect = dance ? 280 : 279, up = dance ? 302 : 300, mini = dance ? 303 : 301;
            double bonus = singer.Value(bonusEffect, 0.0) + Math.Min(0.05, 0.02 * singer.Pieces(up) + 0.01 * singer.Pieces(mini));
            int keep = PerformanceSlots(singer, dance);
            var own = dance ? singer.Dance : singer.Song;
            string name = action.Skill != null ? action.Skill.Name : action.Atk.Name;
            if (!own.Contains(name))
            {
                own.Add(name);
                while (own.Count > keep)
                {
                    string old = own[0];
                    own.RemoveAt(0);
                    foreach (var u in Units)
                    {
                        var effects = u.StatusOrder();
                        foreach (int e in effects)
                        {
                            var s = u.St[e];
                            if (s != null && s.Source == singer && s.Skill == old) u.PopStatus(e);
                        }
                    }
                }
            }
            if (effect == 215 || effect == 216)
            {
                target.SetStatus(new Status(effect, value, 0, singer, name, Status.SongKind).WithData(bonus));
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
                var st = new Status(effect, value + sign * scale * bonus, 0, singer, name, Status.SongKind);
                if (effect == 199 && action.TryVal(296, out double cap)) st.WithData(cap);
                target.SetStatus(st);
            }
        }

        public bool ApplyAilment(Unit unit, Unit target, int effect, double value, Action action, int start = T.NONE)
        {
            string name = AilmentName[effect];
            if (target.Immune(name) || target.St[effect] != null) return false;
            if (target.Has(192) || Nullified(target, effect)) return false;
            int index = AilmentResist[effect];
            int resistance = index != T.NONE ? target.Resistance(index) : 0;
            int chance = F.AilmentThreshold(value, resistance);
            if (chance <= 0 || Rng.RandRange(100) >= chance) return false;
            for (int k = 0; k < 3; k++)
            {
                int ec = k == 0 ? 101 : k == 1 ? 102 : 181;
                var s = target.St[ec];
                if (s != null)
                {
                    s.Value -= 1;
                    if (s.Value <= 0) target.PopStatus(ec);
                    return false;
                }
            }
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
            if (start == T.NONE) start = action != null && action.Turns != 0 ? PyMath.Int(action.Turns) : 0;
            target.SetStatus(new Status(effect, value, 0, unit).WithData(start));
            EndParts(target, PartsFor(effect));
            return true;
        }

        public static bool Nullified(Unit target, int ailment)
        {
            if (target.Pieces(F.ENCHANT_NULLIFY_ALL) != 0) return true;
            foreach (var (e, a) in F.ENCHANT_NULLIFY_AILMENT) if (a == ailment && target.Pieces(e) != 0) return true;
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
            EndParts(unit, new[] { "song", "dance", "doll" });
        }

        void EndParts(Unit unit, string[] parts)
        {
            bool chant = false, song = false, dance = false, doll = false;
            foreach (var p in parts) { if (p == "chant") chant = true; if (p == "song") song = true; if (p == "dance") dance = true; if (p == "doll") doll = true; }
            if (chant) unit.Chant = null;
            for (int pass = 0; pass < 2; pass++)
            {
                bool wanted = pass == 0 ? song : dance;
                if (!wanted) continue;
                var names = pass == 0 ? unit.Song : unit.Dance;
                foreach (var other in Units)
                {
                    if (other.StCount == 0) continue;
                    var effects = other.StatusOrder();
                    foreach (int e in effects)
                    {
                        var s = other.St[e];
                        if (s != null && s.Source == unit && s.Kind == Status.SongKind && s.Skill != null && names.Contains(s.Skill)) other.PopStatus(e);
                    }
                }
                if (pass == 0) unit.Song = new List<string>(); else unit.Dance = new List<string>();
            }
            if (doll)
            {
                var list = new List<Unit>();
                foreach (var u in Units)
                    if (u.Owner == unit && u.Kind == Kind.Doll && u.Alive && !u.Arrow && !u.Genjimaru) list.Add(u);
                foreach (var d in list) RemoveDoll(d);
            }
        }

        void Delay(Unit target)
        {
            if (!target.Alive) return;
            var order = new List<Unit>();
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
            var effects = target.StatusOrder();
            var remove = new List<int>();
            foreach (int e in effects)
                if (DispelAlways[e] || (DispelIfRaised[e] && target.St[e].Value >= 0)) remove.Add(e);
            foreach (int e in remove) target.PopStatus(e);
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
                if (unit.Kind == Kind.Doll && unit.Owner != null)
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
                // Heal Enemy: a fixed amount, the value itself, with no cap (0x483da0 - 0x483dad)
                Healed(unit, Restore(target, PyMath.Int(value)));
            }
            else if (effect == 132)
            {
                Healed(unit, Restore(target, F.FractionRecovery(target.MaxHp, value, hasCap, cap)));
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
            // a counter is never set up against a doll, the summon or a guest (0x43b5f0, 0x43b610 at 0x42261b - 0x422637); the
            // hit that started it stays voided
            if (NotACandidate(attacker)) return;
            if (unit.Alive && attacker.Alive)
            {
                if (unit == attacker) return;
                var saved = damageByTarget;              // the counter keeps a record of its own hits
                damageByTarget = null;
                // an enemy counters with its first attack (P7.1 of the audit); a member with a plain attack (the skill its status
                // links to is not read: a model limit)
                Action answer = new Action(unit, AKind.Attack);
                if (unit.Kind == Kind.Enemy && unit.Attacks != null && unit.Attacks.Length > 0)
                {
                    var atk = Data.GetAttack(unit.Attacks[0]);
                    if (atk != null) answer = new Action(unit, AKind.Enemy, atk, 1);
                }
                Resolve(answer, attacker, 0);
                damageByTarget = saved;
            }
        }

        // --- dolls, random moves, items --------------------------------------------------------------------------
        void MakeDoll(Action action)
        {
            var owner = action.Actor;
            if (owner.Side == Unit.PARTY && owner.Kind != Kind.Member)
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
                int keep = owner.Has(313) ? 2 : 1;
                var own = new List<Unit>();
                foreach (var u in Units) if (u.Owner == owner && u.Kind == Kind.Doll && u.Alive && !u.Arrow) own.Add(u);
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
                var unit = UnitFactory.BuildDoll(owner, doll, action.Level, Data);
                unit.Arrow = arrow;
                unit.Life += PyMath.Int(owner.Passive(297, 0.0));
                unit.Position = Units.Count;
                unit.NextTime = Time + Wait(unit);
                AddUnit(unit);
            }
        }

        void MakeGuestDoll(Action action)
        {
            var owner = action.Actor;
            DollRec doll = null;
            foreach (var d in Data.Dolls) if (d.Effect != T.NONE && action.Has(d.Effect)) { doll = d; break; }
            if (doll == null) return;
            double lifeValue = action.Val(147, 3);
            int life = PyMath.Int(lifeValue != 0 ? lifeValue : 3);
            int level = doll.Turns.Length;
            for (int k = 0; k < doll.Turns.Length; k++) if (doll.Turns[k] >= life) { level = k + 1; break; }
            var list = new List<Unit>();
            foreach (var u in Units) if (u.Owner == owner && u.Kind == Kind.Doll && u.Alive) list.Add(u);
            foreach (var u in list) RemoveDoll(u);
            var unit = UnitFactory.BuildDoll(owner, doll, level, Data);
            unit.Arrow = false;
            unit.Life = life;
            unit.Position = Units.Count;
            unit.NextTime = Time + Wait(unit);
            AddUnit(unit);
        }

        void RemoveDoll(Unit doll)
        {
            doll.Alive = false;
            doll.Chant = null;
        }

        void MakeGenjimaru(Action action)
        {
            foreach (var u in Units) if (u.Alive && u.Genjimaru) return;
            var turns = new int[10];
            Array.Fill(turns, GENJIMARU_LIFE);
            var record = new DollRec { Skill = GENJIMARU_ACTION, Name = "Genjimaru", Effect = GENJIMARU, Range = null, Turns = turns, Actions = new[] { GENJIMARU_ACTION } };
            var unit = UnitFactory.BuildDoll(action.Actor, record, action.Level, Data);
            unit.Genjimaru = true;
            unit.Position = Units.Count;
            unit.NextTime = Time + Wait(unit);
            AddUnit(unit);
        }

        Action DollAction(Unit doll)
        {
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

        public void UseItem(Action action)
        {
            var unit = action.Actor;
            Item item = null;
            if (action.Item != T.NONE) Data.Items.TryGetValue(action.Item, out item);
            if (item == null || !unit.Items.TryGetValue(action.Item, out int have) || have <= 0) return;
            unit.Items[action.Item] = have - 1;
            if (unit.Has(274) && Roll(unit.Value(274))) unit.Items[action.Item] += 1;
            Rec?.ItemsUsed.Add(new RecKey(unit, item.Name), 1);
            var target = action.Target ?? unit;
            double mastery = unit.Passive(275, 0.0);
            // pairs 0 and 1 of an item act on a unit of the user's side, pairs 2 and 3 on one of the other side (P11.1 of the audit)
            int from = target.Side == unit.Side ? 0 : 2, to = Math.Min(item.Kinds.Length, from + 2);
            for (int i = from; i < to; i++)
            {
                int kind = item.Kinds[i];
                double value = item.Values[i];
                if (kind == 0) Restore(target, PyMath.Int(value) + PyMath.Int(value * mastery));
                else if (kind == 1) target.Tp = Math.Min(target.MaxTp, target.Tp + PyMath.Int(value));
                else if (kind == 3)
                {
                    foreach (var ally in AlliesArray(unit)) Restore(ally, PyMath.Int(value) + PyMath.Int(value * mastery));
                }
                else if (kind == 8 && !target.Alive)
                {
                    target.Alive = true;
                    target.Hp = Math.Max(1, PyMath.Int(target.MaxHp * value / 100.0));
                    target.NextTime = Time + Wait(target);
                }
                else if (kind == ITEM_CURE_ONE)
                {
                    var present = new List<int>();
                    foreach (int e in AILMENT_IDS) if (target.St[e] != null) present.Add(e);
                    if (present.Count > 0) target.PopStatus(present[Rng.ChoiceIndex(present.Count)]);
                }
                else if (kind == ITEM_CURE_ALL)
                {
                    var present = new List<int>();
                    foreach (int e in AILMENT_IDS) if (target.St[e] != null) present.Add(e);
                    foreach (int e in present) target.PopStatus(e);
                }
                else if (Data.ItemSkills.TryGetValue(kind, out int skillId))
                {
                    var skill = Data.ById(skillId);
                    if (skill != null) Perform(new Action(unit, AKind.Skill, skill, skill.Levels, action.Target));
                }
            }
        }

        public bool Roll(double value)
        {
            return Rng.RandRange(100) < PyMath.Int(value * 100);
        }
    }
}
