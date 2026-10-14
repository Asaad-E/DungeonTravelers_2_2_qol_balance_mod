using System;
using System.Collections.Generic;

namespace DtEngine
{
    // Skill target codes (sim/data.py)
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
        public bool Chanted;
        public bool HasEffect(int id) { foreach (var e in Effects) if (e.Id == id) return true; return false; }
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
        public bool Passive, Spell;
        public int ChantStat;
        public bool Chanted => ChantSpeed != 0;
    }

    public sealed class Command
    {
        public int Cmd;
        public int[] Args = Array.Empty<int>();
        public bool HasResult;
        public int Result;
        public bool HasOnce, Once;
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
        public AiSet Get(int number) { foreach (var s in Sets) if (s.Number == number) return s; return null; }
        public int MinSet() { int m = int.MaxValue; foreach (var s in Sets) m = Math.Min(m, s.Number); return Sets.Length == 0 ? 0 : m; }
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
        public int BaseClass, Flag;
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
        public Script Script;
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
        public List<ClassMod> ClassModifiers = new List<ClassMod>();
        public List<Character> Characters = new List<Character>();
        public Dictionary<int, Piece> Equipment = new Dictionary<int, Piece>();
        public List<Piece> EquipmentList = new List<Piece>();
        public HashSet<int> EnchantStacks = new HashSet<int>();
        public Dictionary<int, int[]> SealbookEnchants = new Dictionary<int, int[]>();
        public Dictionary<int, double> WeaponRanks = new Dictionary<int, double>();
        public Dictionary<int, Item> Items = new Dictionary<int, Item>();
        public Dictionary<int, int> ItemSkills = new Dictionary<int, int>();
        public SortedDictionary<int, double> ExpCurve = new SortedDictionary<int, double>();
        public Dictionary<int, double> SpCurve = new Dictionary<int, double>();
        public List<FloorZone> Floors = new List<FloorZone>();
        public List<FixedBattle> Fixed = new List<FixedBattle>();
        public Dictionary<(string, int), BattleCell[]> BattleCells = new Dictionary<(string, int), BattleCell[]>();
        public Dictionary<(string, int), ZoneFactors> ZoneFactorsMap = new Dictionary<(string, int), ZoneFactors>();
        public List<SummonForm> Summons = new List<SummonForm>();
        public List<DollRec> Dolls = new List<DollRec>();
        public List<RandomMove> RandomMoves = new List<RandomMove>();

        // flags of the variant
        public int ArcaneChance = T.NONE;
        public bool InterruptProduct, SurvivalGuard;

        public Skill GetSkill(string category, int id) => Skills.TryGetValue((category, id), out var s) ? s : null;
        public Skill ById(int id) => SkillById.TryGetValue(id, out var s) ? s : null;
        public bool IsPassiveId(int id) => Skills.ContainsKey(("Passive", id));
        public EnemyAttack GetAttack(int id) => Attacks.TryGetValue(id, out var a) ? a : null;

        public FixedBattle FindFixed(string floor, int number)
        {
            foreach (var b in Fixed) if (b.Floor == floor && b.Number == number) return b;
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
