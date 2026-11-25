using System;
using System.Collections.Generic;

namespace DtEngine
{
    // Skill target codes (gamedata/data.py)
    public static class T
    {
        public const int SINGLE = 0, RANDOM = 1, ROW = 2, PIERCE = 3, ALL = 4;
        public const int ALLY = 5, RANDOM_ALLY = 6, ALLY_ROW = 7, ALLIES = 8, SELF = 9, NO_TARGET = 10, ALLY_MOST_TP_LOST = 12;
        public const int EVERYONE = 14, ANYONE = 15;
        public static bool OwnSide(int t) => t >= 5 && t <= 13;
        // attribute codes
        public const int WEAPON_ATTR = 0, SLASH = 1, STAB = 2, BASH = 3, FIRE = 4, WATER = 5, WIND = 6, EARTH = 7, LIGHTNING = 8, NEUTRAL = 9;
        public static bool Physical(int a) => a >= 1 && a <= 3;
        /// <summary>RESIST_INDEX.get(attr): -1 when the attribute has none (weapon, neutral).</summary>
        public static int ResistIndex(int attr) => attr >= SLASH && attr <= LIGHTNING ? attr - 1 : -1;
        public const int SHORT = 0, MID = 1, LONG = 2, NO_RANGE = 3;
        public const int NONE = -1;   // an absent integer field (Python None)
    }

    public sealed class Effect
    {
        public int Id, Kind;
        public double[] Values;
        public bool[] IsInt;        // the value of each level was written as a whole number (an int in Python)
    }

    public sealed class Skill
    {
        public string Category;
        public bool IsMagic, IsTechnique, IsPassive;
        public double Swing;      // a spell's own swing (file 0x124), rolled per cast; an enemy attack has none
        public int Id;
        public string Name;
        public int Levels;
        public int Target = T.NONE;
        public int Attr = T.NONE;          // -1 also stands for None
        public int Group;
        public int[] Weapons;
        public Effect[] Effects;
        public int[] Tp, Sp;
        public double[] Speed;
        public double[] Cast;              // null when the field is absent
        public double[] Accuracy;          // null when the field is absent
        public double[] Turns;
        public int[] Classes;
        public int Range = T.NONE;
        public int ChantStat;              // 0 none, 1 int, 2 res, 3 agi
        public int Pattern;                // Skill Trailer[4] -> CActionSkill::_CreatePattern (0x41e060)
        public bool Chanted;
        public bool HasEffect(int id) { foreach (var e in Effects) if (e.Id == id) return true; return false; }

        /// <summary>The effects at each level as arrays shared by the actions (Action.FxSet), made when first asked.</summary>
        public Action.FxSet[] FxByLevel;

        /// <summary>A copy that shares the effects, with the caches empty (a trial changes the copy).</summary>
        public Skill Copy() { var c = (Skill)MemberwiseClone(); c.FxByLevel = null; c.takes = 0; c.damageCand = 0; return c; }

        int takes;     // 0 not worked out, 1 yes, 2 no
        /// <summary>Whether a figure of the skill takes something from its user (the bonus effects 128 - 130, 272, 273).</summary>
        public bool TakesFromUser
        {
            get
            {
                if (takes == 0)
                {
                    bool yes = false;
                    foreach (var e in Effects) if (e.Id == 128 || e.Id == 129 || e.Id == 130 || e.Id == 272 || e.Id == 273) yes = true;
                    takes = yes ? 1 : 2;
                }
                return takes == 1;
            }
        }

        int damageCand; // 0 not worked out, 1 yes, 2 no
        /// <summary>Whether this skill is a damage or random-move candidate in Policy.ActDamage.</summary>
        public bool IsDamageCandidate
        {
            get
            {
                if (damageCand == 0)
                {
                    bool enemyTarget = Target == T.SINGLE || Target == T.RANDOM || Target == T.ROW || Target == T.PIERCE || Target == T.ALL || Target == T.EVERYONE;
                    bool yes = false;
                    foreach (var e in Effects)
                    {
                        int id = e.Id;
                        if (id == 152 || id == 153 || id == 154 || id == 155) { yes = true; break; }
                        if (enemyTarget && (id == 0 || id == 1 || id == 8 || id == 12 || id == 138 || id == 140 || id == 141 || id == 142 || id == 434 || id == 435))
                        {
                            yes = true;
                            break;
                        }
                    }
                    damageCand = yes ? 1 : 2;
                }
                return damageCand == 1;
            }
        }
    }

    public sealed class EnemyAttack
    {
        public int Id;
        public string Name;
        public int Target, Attr;
        public double ChantSpeed, Accuracy, Power, Speed;
        public int Turns;
        public int[] EffId, EffKind;
        public double[] EffValue;
        public bool[] EffIsInt;
        public int Range = T.NONE;
        public bool Passive, Plain, Spell, Technique; // Plain: bit 0 (+0x40); Technique: bit 1 (freeze); Spell: bit 2 (silence, anti-magic)
        public int ChantStat;
        public int Pattern;                // EnemyAttack +0x90 (Trailer[2]) -> CActionEnemyAttack::_CreatePattern (0x41a4a0)
        public bool Chanted => ChantSpeed != 0;
        public Action.FxSet Fx;       // the effects as arrays shared by the actions (made when first asked)
        int summonsDollState;         // 0 unknown, 1 false, 2 true
        public bool SummonsDoll
        {
            get
            {
                if (summonsDollState != 0) return summonsDollState == 2;
                bool found = false;
                if (EffId != null)
                    for (int k = 0; k < EffId.Length; k++) if (EffId[k] == 146) { found = true; break; }
                summonsDollState = found ? 2 : 1;
                return found;
            }
        }
    }

    public sealed class Command
    {
        public int Cmd;
        public int[] Args = Array.Empty<int>();
        public bool HasResult;
        public int Result;
        public bool HasOnce, Once;
        public bool Stop = true;   // second tail byte: stop reading the commands after a set switch (0x4325cf); top level only
        public Command And;
        public int ListId;     // identity of the list the command stands in (the key of once_done)
    }

    public sealed class CommandList
    {
        public int Id;
        public Command[] Commands;
    }

    public sealed class AiSet
    {
        public int Number;
        public int[] Weights;
        public CommandList Commands;
    }

    public sealed class Script
    {
        public int Id;
        public CommandList Opening;
        public AiSet[] Sets;
        int minSet = int.MinValue;
        public AiSet Get(int number) { for (int i = 0; i < Sets.Length; i++) if (Sets[i].Number == number) return Sets[i]; return null; }
        public int MinSet()
        {
            if (minSet != int.MinValue) return minSet;
            if (Sets.Length == 0) { minSet = 0; return 0; }
            int m = Sets[0].Number;
            for (int i = 1; i < Sets.Length; i++) if (Sets[i].Number < m) m = Sets[i].Number;
            minSet = m;
            return m;
        }
    }

    public sealed class EnemyRec
    {
        public int Id;
        public string Name;
        public int Race, Level, Hp;
        public long Flags;
        public double Swing, Weight;
        public long ImmuneMask;
        public bool Snack;
        public int[] Stats = new int[6];          // atk, def, int, res, dex, agi
        public double Exp, Gold;
        public int[] Resist = new int[8];
        public int[] Attacks, Passives;
        public Script Script;
        public object Clone()
        {
            var c = (EnemyRec)MemberwiseClone();
            c.Stats = (int[])Stats.Clone();
            c.Resist = (int[])Resist.Clone();
            return c;
        }
    }

    public sealed class Piece
    {
        public int Id;
        public string Name;
        public int Category, Rank, Type, Range, Attr;
        public int[] Stats = new int[6];
        public double Rate, Swing;
        public long Classes;
        public int[] Enchants;
        public bool TwoHanded;
        public int PlainTarget = T.SINGLE;   // EquipmentData 0x54 bit 4 (Pierce) / bit 5 (Row)
    }

    public sealed class ClassMod
    {
        public int Class;
        public int Previous = T.NONE;
        public ModEntry[] Entries;
    }

    public sealed class ModEntry
    {
        public double Modifier;
        public int Slot, Type = T.NONE;
    }

    public sealed class Character
    {
        public string Name;
        public int BaseClass, Flag, Race;  // Race: PlayerStatusData +0x30 (e.g. Ist = 6 Magic Being; 0x55d810)
        public double[] Pep = Array.Empty<double>(); // PlayerStatusData +0x3c: 21-float event motivation deltas
        public int StartExp;
        public int UniqueSkill = T.NONE;
    }

    public sealed class UniqueSkill
    {
        public int Id, Effect;
        public double[] Values;
        public bool[] IsInt;
    }

    public sealed class Item
    {
        public int Id;
        public string Name;
        public int Flags;                  // ItemData Flags_0x18 (bit 2: battle usable, bit 4: enemy-targetable, bit 8: infinite)
        public int TargetType = 16;        // ItemData w_0x5c: 16 Single, 17 Row, 18 SideAll (0x456ff0)
        public int[] Kinds;
        public double[] Values;
    }

    public sealed class FormationRec
    {
        public double Chance;
        public (int enemy, bool front)[] Enemies;
        public int Number;
        public int[] Slots;
    }

    public sealed class FloorZone
    {
        public string Dungeon, Floor, Name;
        public int Zone;
        public FormationRec[] Formations;
        public (int equipment, (int key, int lo, int hi)[] levels)[] Equipment;
    }

    public sealed class FixedBattle
    {
        public string Floor;
        public int Number;
        public (int enemy, bool front)[] Enemies;
        public int[] Slots;
    }

    public sealed class ZoneFactors
    {
        public double DownA, DownB, Element, UpA, UpB;
    }

    public sealed class BattleCell
    {
        public int Zone;
        public int[] Slots;
    }

    public sealed class SummonForm
    {
        public int Id, Family, Enemy, Level, Rank;
        public string Name;
        public double[] Factors = new double[6];
        public int[] Attacks;
        public int Passive = T.NONE;
        public int[] Passives = Array.Empty<int>();
        public Script Script;
    }

    /// <summary>A guest ally at one stage of her growth (tools/npc_data.py).</summary>
    public sealed class NpcRec
    {
        // Cost: the gold of the hire (0xAC; a guest ally has no HP); Contract: the battles won it lasts (0xB0); UnlockFlag: the flag that
        // opens the stage in the bar (0xB4); Passives: its passive EnemyAttackData ids (0x94 count, 0x98 ids)
        public int Id, Character, Level, Rank, Cost, Contract, UnlockFlag;
        public string Name;
        public int[] Attacks;
        public int[] Passives = new int[0];
        public int[] Stats = new int[6];
        public Script Script;
        public NpcRec Clone() { var c = (NpcRec)MemberwiseClone(); c.Stats = (int[])Stats.Clone(); return c; }
    }

    public sealed class DollRec
    {
        public int Skill;
        public int Effect = T.NONE;
        public string Name, Range;
        public int[] Turns;
        public int[] Actions;     // skill ids of the hidden actions
    }

    public sealed class RandomResult
    {
        public int Skill;
        public double Weight, JokerWeight;
        public int[] Effects;
    }

    public sealed class RandomMove
    {
        public int Effect;
        public RandomResult[] Results;
    }

    /// <summary>The game data of one side (vanilla or variant): what sim.data.GameData holds and the battle touches.</summary>
    public sealed class GameData
    {
        public const int MaxEffect = 512;
        public const int MaxEnchant = 512;

        public List<Skill> SkillList = new List<Skill>();
        public Dictionary<(string, int), Skill> Skills = new Dictionary<(string, int), Skill>();
        public Dictionary<int, Skill> SkillById = new Dictionary<int, Skill>();
        public Dictionary<int, UniqueSkill> Unique = new Dictionary<int, UniqueSkill>();
        public Dictionary<int, EnemyAttack> Attacks = new Dictionary<int, EnemyAttack>();
        public Dictionary<int, EnemyRec> Enemies = new Dictionary<int, EnemyRec>();
        public Dictionary<int, int[][]> Growth = new Dictionary<int, int[][]>();   // row -> level-1 -> [atk, def, int, res, dex, agi, hp, tp]
        public Dictionary<int, (int row, (int previous, int row)[] byPrevious, int dflt)> GrowthRow = new Dictionary<int, (int, (int, int)[], int)>();
        public Dictionary<int, string> ClassNames = new Dictionary<int, string>();
        public Dictionary<int, int> ClassUnarmedRanks = new Dictionary<int, int>();
        public List<ClassMod> ClassModifiers = new List<ClassMod>();
        public List<Character> Characters = new List<Character>();
        public Dictionary<int, Piece> Equipment = new Dictionary<int, Piece>();
        public List<Piece> EquipmentList = new List<Piece>();
        public HashSet<int> EnchantStacks = new HashSet<int>();
        public HashSet<int> EnchantOffhand = new HashSet<int>();
        // CommandData.pck +0x38 bit 1 (vt+0x8c IsSleepCleared, 36 IDs; 0x4fa056) and bit 2 == 0 (vt+0x90 ClearOnDeath exempt, 8 IDs; 0x4fa8b1)
        public HashSet<int> SleepClearedCommands = new HashSet<int>
        {
            146, 147, 171, 180, 190, 228, 229, 230, 231, 232, 233, 235,
            249, 250, 253, 255, 259, 260, 267, 268, 283, 285, 296, 300,
            303, 305, 306, 308, 320, 345, 350, 357, 446, 447, 448, 449
        };
        public HashSet<int> DeathExemptCommands = new HashSet<int> { 67, 68, 81, 133, 134, 188, 355, 428 };
        public Dictionary<int, int[]> SealbookEnchants = new Dictionary<int, int[]>();
        public Dictionary<int, double> WeaponRanks = new Dictionary<int, double>();
        public Dictionary<int, Item> Items = new Dictionary<int, Item>();
        public Dictionary<int, int> ItemSkills = new Dictionary<int, int>();
        public Dictionary<int, (int SkillId, bool UseValAsLevel, int FixedLevel)> ItemSkillSpecs = new Dictionary<int, (int, bool, int)>();
        public SortedDictionary<int, double> ExpCurve = new SortedDictionary<int, double>();
        public Dictionary<int, double> SpCurve = new Dictionary<int, double>();
        public List<FloorZone> Floors = new List<FloorZone>();
        public List<FixedBattle> Fixed = new List<FixedBattle>();
        public Dictionary<(string, int), BattleCell[]> BattleCells = new Dictionary<(string, int), BattleCell[]>();
        public Dictionary<(string, int), ZoneFactors> ZoneFactorsMap = new Dictionary<(string, int), ZoneFactors>();
        public List<SummonForm> Summons = new List<SummonForm>();
        public List<NpcRec> Npcs = new List<NpcRec>();
        public List<DollRec> Dolls = new List<DollRec>();
        public List<RandomMove> RandomMoves = new List<RandomMove>();

        // flags of the variant
        public int ArcaneChance = T.NONE;
        public bool InterruptProduct, SurvivalGuard, ThirdEyeDispel;
        public int PositiveTranceThreshold = 100;

        /// <summary>The same data with the stats of some enemy records changed (GameData.with_changes on 'enemies'): a copy that shares everything else.
        /// changes: enemy id -> field -> value; the fields are those of the record (hp, atk, def, int, res, dex, agi, res_slash ... res_lightning).</summary>
        public GameData WithEnemyStats(List<(int id, Dictionary<string, double> fields)> changes)
        {
            var copy = (GameData)MemberwiseClone();
            copy.Enemies = new Dictionary<int, EnemyRec>(Enemies);
            string[] stats = { "atk", "def", "int", "res", "dex", "agi" };
            string[] resists = { "res_slash", "res_stab", "res_bash", "res_fire", "res_water", "res_wind", "res_earth", "res_lightning" };
            foreach (var (id, fields) in changes)
            {
                var rec = (EnemyRec)Enemies[id].Clone();
                foreach (var kv in fields)
                {
                    int value = (int)kv.Value;
                    int s = Array.IndexOf(stats, kv.Key), r = Array.IndexOf(resists, kv.Key);
                    if (kv.Key == "hp") rec.Hp = value;
                    else if (s >= 0) rec.Stats[s] = value;
                    else if (r >= 0) rec.Resist[r] = value;
                    else throw new InvalidOperationException("no enemy field " + kv.Key);
                }
                copy.Enemies[id] = rec;
            }
            return copy;
        }

        Dictionary<(string, int), FixedBattle> fixedIndex;
        Skill[] skillByIdArr;
        EnemyAttack[] attackByIdArr;

        /// <summary>A copy that shares every table; a trial replaces the tables it changes in the copy.</summary>
        public GameData ShallowCopy()
        {
            var copy = (GameData)MemberwiseClone();
            copy.skillByIdArr = null;
            copy.attackByIdArr = null;
            copy.fixedIndex = null;
            return copy;
        }

        public Skill GetSkill(string category, int id) => Skills.TryGetValue((category, id), out var s) ? s : null;

        public Skill ById(int id)
        {
            var arr = skillByIdArr;
            if (arr == null && SkillById.Count > 0)
            {
                int max = 0;
                foreach (int k in SkillById.Keys) if (k > max) max = k;
                if (max < 4096)
                {
                    arr = new Skill[max + 1];
                    foreach (var kv in SkillById) if (kv.Key >= 0) arr[kv.Key] = kv.Value;
                    skillByIdArr = arr;
                }
            }
            if (arr != null && (uint)id < (uint)arr.Length) return arr[id];
            return SkillById.TryGetValue(id, out var s) ? s : null;
        }

        public bool IsPassiveId(int id) => Skills.ContainsKey(("Passive", id));

        public EnemyAttack GetAttack(int id)
        {
            var arr = attackByIdArr;
            if (arr == null && Attacks.Count > 0)
            {
                int max = 0;
                foreach (int k in Attacks.Keys) if (k > max) max = k;
                if (max < 8192)
                {
                    arr = new EnemyAttack[max + 1];
                    foreach (var kv in Attacks) if (kv.Key >= 0) arr[kv.Key] = kv.Value;
                    attackByIdArr = arr;
                }
            }
            if (arr != null && (uint)id < (uint)arr.Length) return arr[id];
            return Attacks.TryGetValue(id, out var a) ? a : null;
        }

        public FixedBattle FindFixed(string floor, int number)
        {
            var map = fixedIndex;
            if (map == null)
            {
                map = new Dictionary<(string, int), FixedBattle>(Fixed.Count);
                foreach (var b in Fixed) if (!map.ContainsKey((b.Floor, b.Number))) map[(b.Floor, b.Number)] = b;
                fixedIndex = map;
            }
            if (map.TryGetValue((floor, number), out var found)) return found;
            throw new InvalidOperationException("no fixed battle " + floor + " " + number);
        }

        public int[][] GrowthOf(int row) => Growth[row];

        public int[] Stats(int row, int level) => Growth[row][Math.Max(1, Math.Min(99, level)) - 1];

        /// <summary>class_data.growth_row(class_id, previous)</summary>
        public int GrowthRowOf(int classId, int previous)
        {
            var g = GrowthRow[classId];
            if (g.byPrevious == null) return g.row;
            foreach (var (p, r) in g.byPrevious) if (p == previous) return r;
            return g.dflt;
        }

        public string ClassName(int id) => ClassNames.TryGetValue(id, out var n) ? n : null;
    }
}
