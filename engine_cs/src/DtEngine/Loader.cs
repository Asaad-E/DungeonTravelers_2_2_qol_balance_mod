using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace DtEngine
{
    /// <summary>A row of a sheet of the setup: text, numbers and empty cells (null) by column name.</summary>
    public sealed class Row
    {
        public readonly Dictionary<string, object> Cells = new Dictionary<string, object>();

        public bool Has(string key) => Cells.TryGetValue(key, out var v) && v != null;
        public object Get(string key) => Cells.TryGetValue(key, out var v) ? v : null;

        /// <summary>Python truthiness of a cell.</summary>
        public bool Truthy(string key) => Setup.Truthy(Get(key));

        public string Str(string key)
        {
            var v = Get(key);
            return v == null ? "None" : Setup.PyStr(v);
        }

        public int Int(string key) => Setup.ToInt(Get(key));
        public double Dbl(string key) => Setup.ToDouble(Get(key));
    }

    /// <summary>The choices of the model (sim.setup.Setup), as the snapshot holds them.</summary>
    public sealed class Setup
    {
        public Dictionary<string, object> Settings = new Dictionary<string, object>();
        public List<Row> Policies = new List<Row>();
        public Dictionary<string, Row> Roles = new Dictionary<string, Row>();
        public List<string> RoleOrder = new List<string>();
        public List<string> Composition = new List<string>();
        public List<Row> Checkpoints = new List<Row>();
        public List<(string chapter, List<string> names)> Joins = new List<(string, List<string>)>();
        public Dictionary<string, double?> GuideLevels = new Dictionary<string, double?>();
        public List<Row> MercenaryUnlocks = new List<Row>();
        public List<Row> GrandSealbooks = new List<Row>(), UniqueGear = new List<Row>(), PersonalSealbooks = new List<Row>(),
                         Kit = new List<Row>(), Preparation = new List<Row>(), ZoneChanges = new List<Row>(),
                         EnchantPlan = new List<Row>(), EnchantSlots = new List<Row>();
        public List<(string name, string archetype, List<string> roles)> Battery = new List<(string, string, List<string>)>();

        public static bool Truthy(object v)
        {
            if (v == null) return false;
            if (v is string s) return s.Length > 0;
            if (v is long l) return l != 0;
            if (v is double d) return d != 0.0;
            if (v is bool b) return b;
            return true;
        }

        public static string PyStr(object v)
        {
            if (v == null) return "None";
            if (v is string s) return s;
            if (v is long l) return l.ToString(System.Globalization.CultureInfo.InvariantCulture);
            if (v is double d) return d == Math.Floor(d) && Math.Abs(d) < 1e15 ? ((long)d).ToString(System.Globalization.CultureInfo.InvariantCulture) + ".0" : Fmt.Num(d);
            if (v is bool b) return b ? "True" : "False";
            return v.ToString();
        }

        public static int ToInt(object v)
        {
            if (v is long l) return (int)l;
            if (v is double d) return (int)Math.Truncate(d);
            if (v is string s) return int.Parse(s.Trim(), System.Globalization.CultureInfo.InvariantCulture);
            if (v is bool b) return b ? 1 : 0;
            throw new InvalidOperationException("not a number: " + (v ?? "None"));
        }

        public static double ToDouble(object v)
        {
            if (v is long l) return l;
            if (v is double d) return d;
            if (v is string s) return double.Parse(s.Trim(), System.Globalization.CultureInfo.InvariantCulture);
            if (v is bool b) return b ? 1 : 0;
            throw new InvalidOperationException("not a number: " + (v ?? "None"));
        }

        /// <summary>The same choices with other figures for some settings (a job that sets some of its own).</summary>
        public Setup WithSettings(Dictionary<string, object> overrides)
        {
            var copy = (Setup)MemberwiseClone();
            copy.Settings = new Dictionary<string, object>(Settings);
            foreach (var kv in overrides) copy.Settings[kv.Key] = kv.Value;
            return copy;
        }

        /// <summary>The same choices with another sheet of policies (a job that replaces the rows).</summary>
        public Setup WithPolicies(List<Row> rows)
        {
            var copy = (Setup)MemberwiseClone();
            copy.Policies = rows;
            return copy;
        }

        public bool HasSetting(string key) => Settings.TryGetValue(key, out var v) && v != null;
        public object Setting(string key) => Settings.TryGetValue(key, out var v) ? v : null;
        public double SettingDouble(string key) => ToDouble(Settings[key]);
        public int SettingInt(string key) => ToInt(Settings[key]);

        public Row Checkpoint(string cid)
        {
            foreach (var c in Checkpoints) if (c.Str("ID") == cid) return c;
            throw new InvalidOperationException("no checkpoint " + cid);
        }
    }

    /// <summary>Reads the snapshot written by tools/engine_export.py.</summary>
    public sealed class Snapshot
    {
        public System.Collections.Concurrent.ConcurrentDictionary<string, GameData> Sides = new System.Collections.Concurrent.ConcurrentDictionary<string, GameData>();   // added to while measures of the suite read it
        public Setup Setup;
        public System.Collections.Concurrent.ConcurrentDictionary<string, Setup> Setups = new System.Collections.Concurrent.ConcurrentDictionary<string, Setup>();      // setups a job names (tools that change the sheets of the setup)
        public Suite.Obj MeasureInputs;      // the section "measures": sheets and constants the measures of the suite take from the workbooks and readers

        /// <summary>The setup a job names; the one of the snapshot when it names none.</summary>
        public Setup SetupNamed(string name)
        {
            if (string.IsNullOrEmpty(name)) return Setup;
            if (!Setups.TryGetValue(name, out var s)) throw new InvalidOperationException("no setup " + name);
            return s;
        }

        /// <summary>Adds the sides and setups of a second file ({"sides": {...}, "setups": {...}}) to the snapshot, under their own names.</summary>
        public void LoadExtra(string path)
        {
            byte[] bytes = File.ReadAllBytes(path);
            using (var doc = JsonDocument.Parse(bytes, new JsonDocumentOptions { MaxDepth = 256 }))
            {
                var root = doc.RootElement;
                if (root.TryGetProperty("sides", out var sides))
                    foreach (var side in sides.EnumerateObject()) Sides[side.Name] = LoadSide(side.Value);
                if (root.TryGetProperty("setups", out var setups))
                    foreach (var s in setups.EnumerateObject()) Setups[s.Name] = LoadSetup(s.Value);
            }
        }

        public static Snapshot Load(string path)
        {
            byte[] bytes = File.ReadAllBytes(path);
            using (var doc = JsonDocument.Parse(bytes, new JsonDocumentOptions { MaxDepth = 256 }))
            {
                var root = doc.RootElement;
                var snap = new Snapshot();
                foreach (var side in root.GetProperty("sides").EnumerateObject())
                    snap.Sides[side.Name] = LoadSide(side.Value);
                snap.Setup = LoadSetup(root.GetProperty("setup"));
                if (root.TryGetProperty("measures", out var inputs)) snap.MeasureInputs = (Suite.Obj)Suite.PyJson.From(inputs);
                return snap;
            }
        }

        // --- helpers ------------------------------------------------------------------------------------
        public static object Plain(JsonElement e)
        {
            switch (e.ValueKind)
            {
                case JsonValueKind.Null: return null;
                case JsonValueKind.True: return true;
                case JsonValueKind.False: return false;
                case JsonValueKind.String: return e.GetString();
                case JsonValueKind.Number:
                    if (e.TryGetInt64(out long l) && !e.GetRawText().Contains('.') && !e.GetRawText().Contains('e') && !e.GetRawText().Contains('E')) return l;
                    return e.GetDouble();
                default: throw new InvalidOperationException("unexpected json value " + e.ValueKind);
            }
        }

        public static Row ToRow(JsonElement e)
        {
            var r = new Row();
            foreach (var p in e.EnumerateObject()) r.Cells[p.Name] = Plain(p.Value);
            return r;
        }

        static List<Row> Rows(JsonElement e)
        {
            var list = new List<Row>();
            foreach (var x in e.EnumerateArray()) list.Add(ToRow(x));
            return list;
        }

        static int I(JsonElement e) => e.ValueKind == JsonValueKind.Null ? T.NONE : (int)Math.Truncate(e.GetDouble());
        static double D(JsonElement e) => e.GetDouble();
        static string S(JsonElement e) => e.ValueKind == JsonValueKind.Null ? null : e.GetString();
        static bool B(JsonElement e) => e.GetBoolean();

        static int[] Ints(JsonElement e)
        {
            var l = new int[e.GetArrayLength()];
            int k = 0;
            foreach (var x in e.EnumerateArray()) l[k++] = I(x);
            return l;
        }

        static bool IsWhole(JsonElement e)
        {
            string raw = e.GetRawText();
            return raw.IndexOf('.') < 0 && raw.IndexOf('e') < 0 && raw.IndexOf('E') < 0;
        }

        static bool[] Wholes(JsonElement e)
        {
            var l = new bool[e.GetArrayLength()];
            int k = 0;
            foreach (var x in e.EnumerateArray()) l[k++] = x.ValueKind == JsonValueKind.Number && IsWhole(x);
            return l;
        }

        static double[] Doubles(JsonElement e)
        {
            if (e.ValueKind == JsonValueKind.Null) return null;
            var l = new double[e.GetArrayLength()];
            int k = 0;
            foreach (var x in e.EnumerateArray()) l[k++] = D(x);
            return l;
        }

        static (int, bool)[] EnemyList(JsonElement e)
        {
            var l = new (int, bool)[e.GetArrayLength()];
            int k = 0;
            foreach (var x in e.EnumerateArray()) l[k++] = (I(x[0]), B(x[1]));
            return l;
        }

        /// <summary>The bit of each immunity name; filled while the snapshot loads, read only afterwards.</summary>
        public static readonly Dictionary<string, int> ImmuneBits = new Dictionary<string, int>();
        public static int ImmuneBit(string name)
        {
            lock (ImmuneBits)
            {
                if (!ImmuneBits.TryGetValue(name, out int bit)) { bit = ImmuneBits.Count; ImmuneBits[name] = bit; }
                return bit;
            }
        }

        static int nextListId;

        static Command LoadCommand(JsonElement e, CommandList owner)
        {
            var c = new Command { Cmd = I(e.GetProperty("cmd")), ListId = owner.Id };
            if (e.TryGetProperty("args", out var args)) c.Args = Ints(args);
            if (e.TryGetProperty("result", out var res)) { c.HasResult = true; c.Result = I(res); }
            if (e.TryGetProperty("once", out var once)) { c.HasOnce = true; c.Once = B(once); }
            if (e.TryGetProperty("and", out var and)) c.And = LoadCommand(and, owner);
            return c;
        }

        static CommandList LoadCommands(JsonElement e)
        {
            var list = new CommandList { Id = ++nextListId };
            var cmds = new List<Command>();
            foreach (var x in e.EnumerateArray()) cmds.Add(LoadCommand(x, list));
            list.Commands = cmds.ToArray();
            return list;
        }

        public static Script LoadScript(JsonElement e)
        {
            if (e.ValueKind == JsonValueKind.Null) return null;
            var s = new Script { Id = I(e.GetProperty("id")), Opening = LoadCommands(e.GetProperty("opening")) };
            var sets = new List<AiSet>();
            foreach (var x in e.GetProperty("sets").EnumerateArray())
                sets.Add(new AiSet { Number = I(x.GetProperty("set")), Weights = Ints(x.GetProperty("weights")), Commands = LoadCommands(x.GetProperty("commands")) });
            s.Sets = sets.ToArray();
            return s;
        }

        static int ChantStatOf(JsonElement e)
        {
            string s = S(e);
            return s == "int" ? 1 : s == "res" ? 2 : s == "agi" ? 3 : 0;
        }

        static GameData LoadSide(JsonElement e)
        {
            var d = new GameData();
            var flags = e.GetProperty("flags");
            d.ArcaneChance = I(flags.GetProperty("arcane_chance"));
            d.InterruptProduct = B(flags.GetProperty("interrupt_product"));
            d.SurvivalGuard = B(flags.GetProperty("survival_guard"));

            foreach (var s in e.GetProperty("skills").EnumerateArray())
            {
                var k = new Skill
                {
                    Category = S(s.GetProperty("category")), Id = I(s.GetProperty("id")), Name = S(s.GetProperty("name")),
                    Levels = I(s.GetProperty("levels")), Target = I(s.GetProperty("target")), Attr = I(s.GetProperty("attr")),
                    Group = s.GetProperty("group").ValueKind == JsonValueKind.Null ? 0 : I(s.GetProperty("group")),
                    Weapons = Ints(s.GetProperty("weapons")), Tp = Ints(s.GetProperty("tp")), Sp = Ints(s.GetProperty("sp")),
                    Speed = Doubles(s.GetProperty("speed")), Cast = Doubles(s.GetProperty("cast")),
                    Accuracy = Doubles(s.GetProperty("accuracy")), Turns = Doubles(s.GetProperty("turns")),
                    Classes = Ints(s.GetProperty("classes")), Range = I(s.GetProperty("range")),
                    ChantStat = ChantStatOf(s.GetProperty("chant_stat")),
                };
                k.IsMagic = k.Category == "Magic"; k.IsTechnique = k.Category == "Technique"; k.IsPassive = k.Category == "Passive";
                var effs = new List<Effect>();
                foreach (var x in s.GetProperty("effects").EnumerateArray())
                    effs.Add(new Effect { Id = I(x[0]), Kind = I(x[1]), Values = Doubles(x[2]), IsInt = Wholes(x[2]) });
                k.Effects = effs.ToArray();
                bool any = false;
                if (k.Cast != null) foreach (var c in k.Cast) if (c != 0) any = true;
                k.Chanted = k.IsMagic && k.Cast != null && k.Cast.Length > 0 && any;
                d.SkillList.Add(k);
                d.Skills[(k.Category, k.Id)] = k;
                if (!k.IsPassive) d.SkillById[k.Id] = k;
            }
            foreach (var u in e.GetProperty("unique").EnumerateArray())
                d.Unique[I(u.GetProperty("id"))] = new UniqueSkill { Id = I(u.GetProperty("id")), Effect = I(u.GetProperty("effect")), Values = Doubles(u.GetProperty("values")), IsInt = Wholes(u.GetProperty("values")) };
            foreach (var a in e.GetProperty("attacks").EnumerateArray())
            {
                var k = new EnemyAttack
                {
                    Id = I(a.GetProperty("id")), Name = S(a.GetProperty("name")), Target = I(a.GetProperty("target")),
                    Attr = I(a.GetProperty("attr")), ChantSpeed = D(a.GetProperty("chant_speed")),
                    Accuracy = D(a.GetProperty("accuracy")), Power = D(a.GetProperty("power")), Turns = I(a.GetProperty("turns")),
                    Speed = D(a.GetProperty("speed")), Range = I(a.GetProperty("range")), Passive = B(a.GetProperty("passive")),
                    ChantStat = ChantStatOf(a.GetProperty("chant_stat")), Spell = B(a.GetProperty("spell")),
                };
                var ids = new List<int>(); var kinds = new List<int>(); var vals = new List<double>(); var wholes = new List<bool>();
                foreach (var x in a.GetProperty("effects").EnumerateArray()) { ids.Add(I(x[0])); kinds.Add(I(x[1])); vals.Add(D(x[2])); wholes.Add(IsWhole(x[2])); }
                k.EffId = ids.ToArray(); k.EffKind = kinds.ToArray(); k.EffValue = vals.ToArray(); k.EffIsInt = wholes.ToArray();
                d.Attacks[k.Id] = k;
            }
            foreach (var en in e.GetProperty("enemies").EnumerateArray())
            {
                var r = new EnemyRec
                {
                    Id = I(en.GetProperty("id")), Name = S(en.GetProperty("name")), Race = I(en.GetProperty("race")),
                    Level = I(en.GetProperty("level")), Hp = I(en.GetProperty("hp")), Flags = en.GetProperty("flags").GetInt64(),
                    Swing = D(en.GetProperty("swing")), Weight = D(en.GetProperty("weight")), Snack = B(en.GetProperty("snack")),
                    Exp = D(en.GetProperty("exp")), Gold = D(en.GetProperty("gold")),
                    Attacks = Ints(en.GetProperty("attacks")), Passives = Ints(en.GetProperty("passives")),
                    Script = LoadScript(en.GetProperty("script")),
                };
                string[] st = { "atk", "def", "int", "res", "dex", "agi" };
                for (int i = 0; i < 6; i++) r.Stats[i] = I(en.GetProperty(st[i]));
                string[] rs = { "res_slash", "res_stab", "res_bash", "res_fire", "res_water", "res_wind", "res_earth", "res_lightning" };
                for (int i = 0; i < 8; i++) r.Resist[i] = I(en.GetProperty(rs[i]));
                foreach (var n in en.GetProperty("immune").EnumerateArray()) r.ImmuneMask |= 1L << ImmuneBit(n.GetString());
                d.Enemies[r.Id] = r;
            }
            foreach (var g in e.GetProperty("growth").EnumerateArray())
            {
                var rows = new List<int[]>();
                foreach (var lv in g[1].EnumerateArray()) rows.Add(Ints(lv));
                d.Growth[I(g[0])] = rows.ToArray();
            }
            foreach (var g in e.GetProperty("growth_row").EnumerateObject())
            {
                int cls = int.Parse(g.Name);
                if (g.Value.TryGetProperty("row", out var row)) d.GrowthRow[cls] = (I(row), null, 0);
                else
                {
                    var list = new List<(int, int)>();
                    foreach (var x in g.Value.GetProperty("by_previous").EnumerateArray()) list.Add((I(x[0]), I(x[1])));
                    d.GrowthRow[cls] = (0, list.ToArray(), I(g.Value.GetProperty("default")));
                }
            }
            foreach (var c in e.GetProperty("class_names").EnumerateArray()) d.ClassNames[I(c[0])] = S(c[1]);
            foreach (var m in e.GetProperty("class_modifiers").EnumerateArray())
            {
                var cm = new ClassMod { Class = I(m.GetProperty("class")), Previous = I(m.GetProperty("previous")) };
                var es = new List<ModEntry>();
                foreach (var x in m.GetProperty("entries").EnumerateArray())
                    es.Add(new ModEntry { Modifier = D(x.GetProperty("modifier")), Slot = I(x.GetProperty("slot")), Type = I(x.GetProperty("type")) });
                cm.Entries = es.ToArray();
                d.ClassModifiers.Add(cm);
            }
            foreach (var c in e.GetProperty("characters").EnumerateArray())
                d.Characters.Add(new Character
                {
                    Name = S(c.GetProperty("name")), BaseClass = I(c.GetProperty("base_class")), Flag = I(c.GetProperty("flag")),
                    StartExp = c.GetProperty("start_exp").ValueKind == JsonValueKind.Null ? 0 : I(c.GetProperty("start_exp")),
                    UniqueSkill = I(c.GetProperty("unique_skill")),
                });
            foreach (var p in e.GetProperty("equipment").EnumerateArray())
            {
                var piece = new Piece
                {
                    Id = I(p.GetProperty("id")), Name = S(p.GetProperty("name")), Category = I(p.GetProperty("category")),
                    Rate = D(p.GetProperty("rate")), Classes = p.GetProperty("classes").GetInt64(), Swing = D(p.GetProperty("swing")),
                    Rank = I(p.GetProperty("rank")), Type = I(p.GetProperty("type")), Enchants = Ints(p.GetProperty("enchants")),
                    TwoHanded = B(p.GetProperty("two_handed")), Range = I(p.GetProperty("range")), Attr = I(p.GetProperty("attr")),
                };
                string[] st = { "atk", "def", "int", "res", "dex", "agi" };
                var stats = p.GetProperty("stats");
                for (int i = 0; i < 6; i++) piece.Stats[i] = I(stats.GetProperty(st[i]));
                d.Equipment[piece.Id] = piece;
                d.EquipmentList.Add(piece);
            }
            foreach (var x in e.GetProperty("enchant_stacks").EnumerateArray()) d.EnchantStacks.Add(I(x));
            foreach (var s in e.GetProperty("sealbooks").EnumerateArray()) d.SealbookEnchants[I(s.GetProperty("id"))] = Ints(s.GetProperty("enchants"));
            foreach (var r in e.GetProperty("weapon_ranks").EnumerateArray()) d.WeaponRanks[I(r[0])] = D(r[1]);
            foreach (var it in e.GetProperty("items").EnumerateArray())
            {
                var item = new Item { Id = I(it.GetProperty("id")), Name = S(it.GetProperty("name")) };
                var kinds = new List<int>(); var vals = new List<double>();
                foreach (var x in it.GetProperty("effects").EnumerateArray()) { kinds.Add(I(x[0])); vals.Add(x[1].ValueKind == JsonValueKind.Null ? 0 : D(x[1])); }
                item.Kinds = kinds.ToArray(); item.Values = vals.ToArray();
                d.Items[item.Id] = item;
            }
            foreach (var x in e.GetProperty("item_skills").EnumerateArray()) d.ItemSkills[I(x[0])] = I(x[1]);
            foreach (var x in e.GetProperty("exp_curve").EnumerateArray()) d.ExpCurve[I(x[0])] = D(x[1]);
            foreach (var x in e.GetProperty("sp_curve").EnumerateArray()) d.SpCurve[I(x[0])] = D(x[1]);
            foreach (var z in e.GetProperty("floors").EnumerateArray())
            {
                var fz = new FloorZone
                {
                    Dungeon = S(z.GetProperty("dungeon")), Floor = S(z.GetProperty("floor")), Name = S(z.GetProperty("name")),
                    Zone = I(z.GetProperty("zone")),
                };
                var fs = new List<FormationRec>();
                foreach (var f in z.GetProperty("formations").EnumerateArray())
                    fs.Add(new FormationRec { Chance = D(f.GetProperty("chance")), Enemies = EnemyList(f.GetProperty("enemies")), Number = I(f.GetProperty("number")), Slots = Ints(f.GetProperty("slots")) });
                fz.Formations = fs.ToArray();
                var eq = new List<(int, (int, int, int)[])>();
                foreach (var p in z.GetProperty("equipment").EnumerateArray())
                {
                    var lv = new List<(int, int, int)>();
                    foreach (var x in p.GetProperty("levels").EnumerateArray()) lv.Add((I(x[0]), I(x[1]), I(x[2])));
                    eq.Add((I(p.GetProperty("equipment")), lv.ToArray()));
                }
                fz.Equipment = eq.ToArray();
                d.Floors.Add(fz);
            }
            foreach (var b in e.GetProperty("fixed").EnumerateArray())
                d.Fixed.Add(new FixedBattle { Floor = S(b.GetProperty("floor")), Number = I(b.GetProperty("number")), Enemies = EnemyList(b.GetProperty("enemies")), Slots = Ints(b.GetProperty("slots")) });
            foreach (var b in e.GetProperty("battle_cells").EnumerateArray())
            {
                var cells = new List<BattleCell>();
                foreach (var c in b.GetProperty("cells").EnumerateArray()) cells.Add(new BattleCell { Zone = I(c.GetProperty("zone")), Slots = Ints(c.GetProperty("slots")) });
                d.BattleCells[(S(b.GetProperty("floor")), I(b.GetProperty("number")))] = cells.ToArray();
            }
            foreach (var z in e.GetProperty("zone_factors").EnumerateArray())
                d.ZoneFactorsMap[(S(z.GetProperty("floor")), I(z.GetProperty("zone")))] = new ZoneFactors
                {
                    DownA = D(z.GetProperty("down_a")), DownB = D(z.GetProperty("down_b")), Element = D(z.GetProperty("element")),
                    UpA = D(z.GetProperty("up_a")), UpB = D(z.GetProperty("up_b")),
                };
            foreach (var s in e.GetProperty("summons").EnumerateArray())
            {
                var f = new SummonForm
                {
                    Id = I(s.GetProperty("id")), Family = I(s.GetProperty("family")), Enemy = I(s.GetProperty("enemy")),
                    Level = I(s.GetProperty("level")), Rank = I(s.GetProperty("rank")), Name = S(s.GetProperty("name")),
                    Attacks = Ints(s.GetProperty("attacks")), Passive = I(s.GetProperty("passive")),
                    Script = LoadScript(s.GetProperty("script")),
                };
                string[] st = { "atk", "def", "int", "res", "dex", "agi" };
                for (int i = 0; i < 6; i++) f.Factors[i] = D(s.GetProperty("factors").GetProperty(st[i]));
                d.Summons.Add(f);
            }
            foreach (var n in e.GetProperty("npcs").EnumerateArray())
            {
                var npc = new NpcRec
                {
                    Id = I(n.GetProperty("id")), Character = I(n.GetProperty("character")), Level = I(n.GetProperty("level")),
                    Rank = I(n.GetProperty("raw_1c")), Cost = n.TryGetProperty("cost", out var c) ? I(c) : 0,
                    Contract = n.TryGetProperty("contract", out var ct) ? I(ct) : 0,
                    UnlockFlag = n.TryGetProperty("unlock_flag", out var uf) ? I(uf) : 0,
                    Passives = n.TryGetProperty("passives", out var ps) ? Ints(ps) : new int[0],
                    Name = S(n.GetProperty("name")), Attacks = Ints(n.GetProperty("attacks")),
                    Script = LoadScript(n.GetProperty("script")),
                };
                string[] st = { "atk", "def", "int", "res", "dex", "agi" };
                for (int i = 0; i < 6; i++) npc.Stats[i] = I(n.GetProperty(st[i]));
                d.Npcs.Add(npc);
            }
            foreach (var x in e.GetProperty("dolls").EnumerateArray())
            {
                var doll = new DollRec
                {
                    Skill = I(x.GetProperty("skill")), Effect = I(x.GetProperty("effect")), Name = S(x.GetProperty("name")),
                    Range = S(x.GetProperty("range")), Turns = Ints(x.GetProperty("turns")),
                };
                var acts = new List<int>();
                foreach (var a in x.GetProperty("actions").EnumerateArray()) acts.Add(I(a.GetProperty("skill")));
                doll.Actions = acts.ToArray();
                d.Dolls.Add(doll);
            }
            foreach (var t in e.GetProperty("random_moves").EnumerateArray())
            {
                var rm = new RandomMove { Effect = I(t.GetProperty("effect")) };
                var rs = new List<RandomResult>();
                foreach (var r in t.GetProperty("results").EnumerateArray())
                    rs.Add(new RandomResult { Skill = I(r.GetProperty("skill")), Weight = D(r.GetProperty("weight")), JokerWeight = D(r.GetProperty("joker_weight")), Effects = Ints(r.GetProperty("effects")) });
                rm.Results = rs.ToArray();
                d.RandomMoves.Add(rm);
            }
            return d;
        }

        static Setup LoadSetup(JsonElement e)
        {
            var s = new Setup();
            foreach (var p in e.GetProperty("settings").EnumerateObject()) s.Settings[p.Name] = Plain(p.Value);
            s.Policies = Rows(e.GetProperty("policies"));
            foreach (var r in Rows(e.GetProperty("roles"))) { s.Roles[r.Str("Role")] = r; s.RoleOrder.Add(r.Str("Role")); }
            foreach (var x in e.GetProperty("composition").EnumerateArray()) s.Composition.Add(x.GetString());
            s.Checkpoints = Rows(e.GetProperty("checkpoints"));
            foreach (var j in e.GetProperty("joins").EnumerateArray())
            {
                var names = new List<string>();
                foreach (var n in j[1].EnumerateArray()) names.Add(n.GetString());
                s.Joins.Add((j[0].GetString(), names));
            }
            foreach (var g in e.GetProperty("guide_levels").EnumerateArray())
                s.GuideLevels[g[0].GetString()] = g[1].ValueKind == JsonValueKind.Null ? (double?)null : g[1].GetDouble();
            s.GrandSealbooks = Rows(e.GetProperty("grand_sealbooks"));
            s.UniqueGear = Rows(e.GetProperty("unique_gear"));
            s.PersonalSealbooks = Rows(e.GetProperty("personal_sealbooks"));
            if (e.TryGetProperty("mercenary_unlocks", out var mu)) s.MercenaryUnlocks = Rows(mu);
            s.Kit = Rows(e.GetProperty("kit"));
            s.Preparation = Rows(e.GetProperty("preparation"));
            s.ZoneChanges = Rows(e.GetProperty("zone_changes"));
            s.EnchantPlan = Rows(e.GetProperty("enchant_plan"));
            s.EnchantSlots = Rows(e.GetProperty("enchant_slots"));
            foreach (var b in e.GetProperty("battery").EnumerateArray())
            {
                var roles = new List<string>();
                foreach (var r in b[2].EnumerateArray()) roles.Add(r.GetString());
                s.Battery.Add((b[0].GetString(), b[1].GetString(), roles));
            }
            return s;
        }
    }
}
