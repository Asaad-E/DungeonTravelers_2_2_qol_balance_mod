using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine
{
    /// <summary>The enemies of one battle, with the zone of the cell it is fought on (scenario.Group).</summary>
    public sealed class Group
    {
        public List<Unit> Units = new List<Unit>();
        public Zone Zone;
        public string Floor;
        public int Number = T.NONE;       // NONE for a random formation
        public bool Boss;                 // the boss after a walk of random battles: never played as a random battle
    }

    /// <summary>Arguments of build_member that a job gives to every member it builds (unique_level, passives).</summary>
    public sealed class MemberExtras
    {
        public int? UniqueLevel;
        public List<(int effect, double value, bool isInt)> Passives;
        public Dictionary<string, string> Pieces;      // pieces that take the place of the role's own (column of the sheet Roles -> name)
    }

    public sealed class RunResult
    {
        public bool Won, Lost;
        public double Time;
        public int Actions;
        public double LowestHp;
        public int EnemyDamage, EnemyActions, PartyMaxHp;
        public double HpLeft, TpLeft;
        public int Alive;
        public List<BattleResult> Parts = new List<BattleResult>();
    }

    /// <summary>A party and its enemies built for a checkpoint, and the runs played.</summary>
    public sealed partial class Scenario
    {
        static readonly (int level, string label)[] STAGES = { (30, "Lv30 class"), (15, "Lv15 class"), (1, "Base class") };
        static readonly int[] ONE_PER_PIECE = { 6, 9, 12, 15, 18, 21 };
        const int NO_MAGIC = 2;

        /// <summary>Time spent building parties and enemies, in Stopwatch ticks, over all runs (for the speed report).</summary>
        public static long BuildTicks;
        /// <summary>Bytes allocated by the building of parties and enemies, over all runs (for the speed report).</summary>
        public static long BuildBytes;

        public readonly GameData Data;
        public readonly Setup Setup;
        public readonly Policy Policy;
        readonly BattleOptions baseOptions;
        readonly double maxTime;

        // caches of pure functions of the data
        readonly object cacheLock = new object();
        Dictionary<string, (int level, string source)> levels;
        readonly Dictionary<string, int> gear = new Dictionary<string, int>();

        public Scenario(GameData data, Setup setup, List<Row> extraPolicies = null)
        {
            Data = data; Setup = setup;
            Policy = new Policy(extraPolicies == null || extraPolicies.Count == 0 ? setup.Policies : setup.Policies.Concat(extraPolicies).ToList(), setup);
            baseOptions = OptionsFrom(setup, null);
            maxTime = setup.HasSetting("max_time") ? Setup.ToDouble(setup.Setting("max_time")) : 400.0;
        }

        static bool Truthy(Setup setup, string key) => Setup.Truthy(setup.Setting(key));

        public static BattleOptions OptionsFrom(Setup setup, Dictionary<string, object> extra)
        {
            var o = new BattleOptions();
            object Get(string key)
            {
                if (extra != null && extra.TryGetValue(key, out var v)) return v;
                return setup.Setting(key);
            }
            bool Has(string key) => (extra != null && extra.ContainsKey(key)) || setup.Settings.ContainsKey(key);
            o.RandomBattle = Setup.Truthy(Get("random_battle"));
            o.HalveEnemies = Has("halve_enemies") ? Setup.Truthy(Get("halve_enemies")) : true;
            o.DollCureTargets = Has("doll_cure_targets") ? Setup.ToInt(Get("doll_cure_targets")) : 2;
            o.Boss = Setup.Truthy(Get("boss"));
            return o;
        }

        // --- classes and levels --------------------------------------------------------------------------------
        public int ClassId(string name)
        {
            foreach (var kv in Data.ClassNames) if (kv.Value == name) return kv.Key;
            throw new InvalidOperationException("no class " + name);
        }

        public int LevelOfExp(double exp)
        {
            int level = 1;
            double total = 0;
            foreach (var kv in Data.ExpCurve)
            {
                total += kv.Value;
                if (total <= exp) level = kv.Key;
            }
            return level;
        }

        public (int cls, int previous) ClassPath(Row role, int level)
        {
            string b = role.Str("Base class"), l15 = role.Str("Lv15 class"), l30 = role.Str("Lv30 class");
            if (level >= 30) return (ClassId(l30), ClassId(l15));
            if (level >= 15) return (ClassId(l15), ClassId(b));
            return (ClassId(b), T.NONE);
        }

        public List<int> ClassesSoFar(Row role, int level)
        {
            var names = new List<string> { role.Str("Base class") };
            if (level >= 15) names.Add(role.Str("Lv15 class"));
            if (level >= 30) names.Add(role.Str("Lv30 class"));
            return names.Select(ClassId).ToList();
        }

        long SpTotal(int level)
        {
            long total = 0;
            for (int lv = 1; lv <= level; lv++) total += Data.SpCurve.TryGetValue(lv, out var v) ? (long)v : 0;
            return total;
        }

        static string[] SplitTrim(string s, char sep, bool dropEmpty)
        {
            var parts = s.Split(sep).Select(x => x.Trim()).ToArray();
            return dropEmpty ? parts.Where(x => x.Length > 0).ToArray() : parts;
        }

        /// <summary>allocate_skills: skill points of the level spent on the role's priority list, in the order they are raised.</summary>
        public List<(int id, int level)> AllocateSkills(Row role, int level, int maxTp)
        {
            var classes = ClassesSoFar(role, level);
            var byName = SkillsByName(classes);
            var wanted = new List<Skill>();
            foreach (var n in role.Str("Skill priority").Split(';'))
                if (byName.TryGetValue(n.Trim(), out var s)) wanted.Add(s);
            long budget = SpTotal(level);
            var order = new List<Skill>();
            var levels = new Dictionary<Skill, int>();

            void RaiseTo(Skill skill, int target)
            {
                while ((levels.TryGetValue(skill, out int cur) ? cur : 0) < Math.Min(target, skill.Levels))
                {
                    cur = levels.TryGetValue(skill, out int c2) ? c2 : 0;
                    if (skill.Tp.Length > 0 && skill.Tp[cur] > maxTp) return;
                    long cost = skill.Sp.Length > 0 ? skill.Sp[cur] : 1;
                    if (cost > budget) return;
                    budget -= cost;
                    if (!levels.ContainsKey(skill)) order.Add(skill);
                    levels[skill] = cur + 1;
                }
            }

            string plan = role.Truthy("Skill plan") ? role.Str("Skill plan") : null;
            if (plan != null)
            {
                foreach (var entryRaw in plan.Split(';'))
                {
                    string entry = entryRaw.Trim();
                    int p = entry.IndexOf(':');
                    string name = p >= 0 ? entry.Substring(0, p) : entry;
                    string target = p >= 0 ? entry.Substring(p + 1) : "";
                    if (byName.TryGetValue(name.Trim(), out var skill))
                    {
                        string t = target.Trim();
                        RaiseTo(skill, t == "" || t == "max" ? skill.Levels : int.Parse(t));
                    }
                }
            }
            else
            {
                foreach (var skill in wanted) RaiseTo(skill, 1);
                foreach (var skill in wanted) RaiseTo(skill, skill.Levels);
            }
            return order.Select(s => (s.Id, levels[s])).ToList();
        }

        // the skills a set of classes can learn, by name: the first skill of each name in the order of the data (pure, cached)
        readonly Dictionary<string, Dictionary<string, Skill>> byNameCache = new Dictionary<string, Dictionary<string, Skill>>();

        Dictionary<string, Skill> SkillsByName(List<int> classes)
        {
            var learnable = new HashSet<int>(classes);
            string key = string.Join(",", learnable.OrderBy(x => x));
            lock (byNameCache)
            {
                if (byNameCache.TryGetValue(key, out var cached)) return cached;
                var byName = new Dictionary<string, Skill>();
                foreach (var skill in Data.SkillList)
                {
                    bool any = false;
                    foreach (int c in skill.Classes) if (learnable.Contains(c)) { any = true; break; }
                    if (any && !byName.ContainsKey(skill.Name)) byName[skill.Name] = skill;
                }
                byNameCache[key] = byName;
                return byName;
            }
        }

        Dictionary<string, List<Piece>> piecesByName;

        Piece PieceByName(string name, int classId)
        {
            if (piecesByName == null)
            {
                var index = new Dictionary<string, List<Piece>>();
                foreach (var piece in Data.EquipmentList)
                {
                    if (!index.TryGetValue(piece.Name, out var list)) index[piece.Name] = list = new List<Piece>();
                    list.Add(piece);
                }
                piecesByName = index;       // (a race between two threads builds the same index twice)
            }
            foreach (var option in name.Split('|'))
            {
                string o = option.Trim();
                if (piecesByName.TryGetValue(o, out var list))
                    foreach (var piece in list)
                        if (((piece.Classes >> classId) & 1) != 0) return piece;
            }
            return null;
        }

        // --- gear and levels of a checkpoint ---------------------------------------------------------------------
        public int GearLevel(string floorName, int level, int minFormations, int margin)
        {
            int dungeon = int.Parse(floorName.Substring(2, 2));
            int best = 0;
            bool any = false;
            foreach (var floor in Data.Floors)
            {
                if (int.Parse(floor.Dungeon.Substring(2)) > dungeon || floor.Formations.Length < minFormations) continue;
                int strongest = int.MinValue;
                foreach (var f in floor.Formations) foreach (var (e, _) in f.Enemies) strongest = Math.Max(strongest, Data.Enemies[e].Level);
                if (strongest > level + margin) continue;
                foreach (var piece in floor.Equipment)
                    foreach (var (_, lo, hi) in piece.levels) { if (!any || hi > best) { best = hi; any = true; } }
            }
            return any ? best : 0;
        }

        public static int[] BattleNumbers(Row cp)
        {
            return cp.Str("Battle (several joined by + are fought in a row)").Split('+').Select(int.Parse).ToArray();
        }

        public int CheckpointGear(string cid)
        {
            lock (cacheLock)
            {
                if (gear.TryGetValue(cid, out int cached)) return cached;
                int best = 0;
                int minF = Setup.SettingInt("gear_min_formations"), margin = Setup.SettingInt("gear_level_margin");
                foreach (var cp in Setup.Checkpoints)
                {
                    int level = int.MinValue;
                    foreach (int number in BattleNumbers(cp))
                        foreach (var b in Data.Fixed)
                            if (b.Floor == cp.Str("Floor") && b.Number == number)
                                foreach (var (e, _) in b.Enemies) level = Math.Max(level, Data.Enemies[e].Level);
                    best = Math.Max(best, GearLevel(cp.Str("Floor"), level, minF, margin));
                    gear[cp.Str("ID")] = best;
                    if (cp.Str("ID") == cid) return best;
                }
                throw new KeyNotFoundException(cid);
            }
        }

        int EnchantSlotsFor(int upgrade)
        {
            int best = 0;
            foreach (var r in Setup.EnchantSlots) if (upgrade >= r.Int("Least upgrade")) best = Math.Max(best, r.Int("Slots"));
            return best;
        }

        sealed class ForgePiece { public bool Weapon; public int Upgrade, Free; public HashSet<int> Has = new HashSet<int>(); }

        Dictionary<int, int> ForgeEnchants(string roleName, List<UnitFactory.PieceUse> equipment)
        {
            var plan = Setup.EnchantPlan.Where(r => r.Str("Role") == roleName).OrderBy(r => r.Dbl("Order")).ToList();
            var pieces = new List<ForgePiece>();
            foreach (var use in equipment)
                pieces.Add(new ForgePiece { Weapon = Data.Equipment[use.EquipId].Category == 0, Upgrade = use.Upgrade, Free = EnchantSlotsFor(use.Upgrade) });
            double fill = Setup.HasSetting("enchant_fill") ? Setup.SettingDouble("enchant_fill") : 0.0;
            long freeSum = 0;
            foreach (var p in pieces) freeSum += p.Free;
            int budget = PyMath.Round(fill * freeSum);
            var found = new Dictionary<int, int>();
            foreach (var row in plan)
            {
                int eid = row.Int("Enchant_ID"), placed = 0;
                foreach (var piece in pieces)
                {
                    while (budget > 0 && placed < row.Int("Most per member") && piece.Free > 0
                           && (row.Str("Slot") == "any" || row.Str("Slot") == (piece.Weapon ? "weapon" : "armour"))
                           && piece.Upgrade >= (row.Truthy("Least upgrade of the piece") ? row.Int("Least upgrade of the piece") : 0)
                           && !(piece.Has.Contains(eid) && Array.IndexOf(ONE_PER_PIECE, eid) >= 0))
                    {
                        piece.Free--;
                        piece.Has.Add(eid);
                        found.TryGetValue(eid, out int c);
                        found[eid] = c + 1;
                        placed++;
                        budget--;
                    }
                }
            }
            return found;
        }

        public bool ForgeOpen(string floor)
        {
            if (floor == null) return false;
            int from = Setup.HasSetting("forge_from_dungeon") ? Setup.SettingInt("forge_from_dungeon") : 99;
            return int.Parse(floor.Substring(2, 2)) >= from;
        }

        // --- members --------------------------------------------------------------------------------------------------
        public Unit BuildRoleMember(string roleName, Character character, int level, int upgrade, int crown, bool forge,
                                    Dictionary<string, string> pieces, int[] partyEnchants, int sealbook, List<(int id, int level)> extra = null,
                                    List<(int id, int pieces)> extraEnchants = null, MemberExtras more = null)
        {
            var role = Setup.Roles[roleName];
            string Cell(string column)
            {
                if (pieces != null && pieces.TryGetValue(column, out var over)) return over;
                return role.Truthy(column) ? role.Str(column) : null;
            }
            var (cls, previous) = ClassPath(role, level);
            var equipment = new List<UnitFactory.PieceUse>();
            string className = Data.ClassName(cls);
            string[] slotColumns = { "Weapon", "Off hand", "Head", "Body", "Accessory" };
            for (int slot = 0; slot < 5; slot++)
            {
                string value = Cell(slotColumns[slot]);
                if (string.IsNullOrEmpty(value)) continue;
                var entries = SplitTrim(value, ';', true);
                string chosen = null;
                foreach (var e in entries)
                {
                    int eq = e.IndexOf('=');
                    if (eq >= 0 && e.Substring(0, eq).Trim() == className) { chosen = e.Substring(eq + 1); break; }
                }
                if (chosen == null) foreach (var e in entries) if (e.IndexOf('=') < 0) { chosen = e; break; }
                if (string.IsNullOrEmpty(chosen)) continue;
                var piece = PieceByName(chosen.Trim(), cls);
                if (piece != null)
                {
                    if (slot == 1 && equipment.Count > 0 && Data.Equipment[equipment[0].EquipId].TwoHanded) continue;
                    equipment.Add(new UnitFactory.PieceUse(slot, piece.Id, upgrade));
                }
            }
            bool front = role.Str("Row") == "front";
            var bare = UnitFactory.BuildMember(Data, character, cls, level, previous, equipment, null, crown, null, front, null, sealbook, partyEnchants,
                                               MergeEnchants(null, extraEnchants), more?.UniqueLevel, more?.Passives);
            var skills = AllocateSkills(role, level, bare.MaxTp);
            if (extra != null)
            {
                // skills.update(extra_skills): an id already there keeps its place and takes the new level
                foreach (var (id, lv) in extra)
                {
                    int at = skills.FindIndex(x => x.id == id);
                    if (at >= 0) skills[at] = (id, lv); else skills.Add((id, lv));
                }
            }
            skills = skills.Where(s => s.level > 0).ToList();
            bool dual = false;
            foreach (var (sid, _) in skills)
            {
                var p = Data.GetSkill("Passive", sid);
                if (p != null) foreach (var e in p.Effects) if (e.Id == UnitFactory.DUAL_WIELD) dual = true;
            }
            equipment = equipment.Where(u => !(u.Slot == 1 && Data.Equipment[u.EquipId].Category == 0 && !dual)).ToList();
            var forged = forge ? ForgeEnchants(roleName, equipment) : null;
            var unit = UnitFactory.BuildMember(Data, character, cls, level, previous, equipment, skills, crown, null, front, null, sealbook, partyEnchants,
                                               MergeEnchants(forged, extraEnchants), more?.UniqueLevel, more?.Passives);
            unit.Role = roleName;
            unit.HasRole = true;
            bool shield = false;
            foreach (var u in equipment) if (u.Slot == 1 && Data.Equipment[u.EquipId].Category == 1) shield = true;
            unit.Shield = shield;
            return unit;
        }

        static Dictionary<string, string> WithPieces(Dictionary<string, string> own, MemberExtras more)
        {
            if (more?.Pieces == null) return own;
            var merged = new Dictionary<string, string>(own);
            foreach (var kv in more.Pieces) merged[kv.Key] = kv.Value;
            return merged;
        }

        static Dictionary<int, int> MergeEnchants(Dictionary<int, int> forged, List<(int id, int pieces)> extra)
        {
            if (extra == null || extra.Count == 0) return forged;
            var merged = forged != null ? new Dictionary<int, int>(forged) : new Dictionary<int, int>();
            foreach (var (id, n) in extra) { merged.TryGetValue(id, out int c); merged[id] = c + n; }
            return merged;
        }

        public List<string> Available(string chapter)
        {
            var names = new List<string>();
            foreach (var (joinedIn, chars) in Setup.Joins)
            {
                names.AddRange(chars);
                if (chapter.StartsWith(joinedIn, StringComparison.Ordinal) || (joinedIn == "Prologue" && chapter == "Prologue")) break;
            }
            return names;
        }

        int CheckpointIndex(string chapter, string floor)
        {
            int first = -1, last = -1;
            for (int k = 0; k < Setup.Checkpoints.Count; k++)
            {
                var c = Setup.Checkpoints[k];
                if (c.Str("Chapter") == chapter && (floor == null || c.Str("Floor") == floor)) { if (first < 0) first = k; last = k; }
            }
            if (first < 0)
            {
                for (int k = 0; k < Setup.Checkpoints.Count; k++)
                    if (Setup.Checkpoints[k].Str("Chapter") == chapter) { if (first < 0) first = k; last = k; }
            }
            if (first < 0) return T.NONE;
            return floor == null ? last : first;
        }

        int OrderOf(string checkpoint)
        {
            for (int k = 0; k < Setup.Checkpoints.Count; k++) if (Setup.Checkpoints[k].Str("ID") == checkpoint) return k;
            return T.NONE;
        }

        Dictionary<string, string> UniquePieces(string role, string chapter, string floor)
        {
            var found = new Dictionary<string, string>();
            int at = CheckpointIndex(chapter, floor);
            if (at == T.NONE) return found;
            foreach (var r in Setup.UniqueGear)
            {
                int o = OrderOf(r.Str("From checkpoint"));
                if (r.Str("Role") == role && o != T.NONE && o <= at) found[r.Str("Slot")] = r.Str("Piece");
            }
            return found;
        }

        int PersonalSealbook(string role, string chapter, string floor)
        {
            int at = CheckpointIndex(chapter, floor);
            int found = T.NONE;
            foreach (var r in Setup.PersonalSealbooks)
            {
                int o = OrderOf(r.Str("From checkpoint"));
                if (at != T.NONE && r.Str("Role") == role && o != T.NONE && o <= at) found = r.Int("Sealbook");
            }
            return found;
        }

        int GrandSealbook(string chapter, string floor)
        {
            int at = CheckpointIndex(chapter, floor);
            if (at == T.NONE) return T.NONE;
            int found = T.NONE;
            foreach (var r in Setup.GrandSealbooks)
            {
                int o = OrderOf(r.Str("From checkpoint"));
                if (o != T.NONE && o <= at) found = r.Int("Sealbook");
            }
            return found;
        }

        Unit SealbookSummon(int sealbook, List<Unit> party)
        {
            var members = party.Where(u => u.Kind == Kind.Member).ToList();
            double average = (double)members.Sum(u => (long)u.Level) / Math.Max(1, members.Count);
            SummonForm last = null;
            foreach (var f in Data.Summons.Where(f => f.Family == sealbook && f.Level <= average).OrderBy(f => f.Level))
                last = f;
            if (last == null) return null;
            var unit = UnitFactory.BuildSummon(Data, last, members, Setup.SettingInt("summon_hp"));
            unit.Level = last.Level;
            return unit;
        }

        // The party of a checkpoint is the same each time it is asked for with the same arguments: it is built once and each run gets a copy.
        readonly System.Collections.Concurrent.ConcurrentDictionary<string, List<Unit>> partyTemplates = new System.Collections.Concurrent.ConcurrentDictionary<string, List<Unit>>();
        readonly System.Collections.Concurrent.ConcurrentDictionary<(int, bool), Unit> enemyTemplates = new System.Collections.Concurrent.ConcurrentDictionary<(int, bool), Unit>();

        const int MAX_PARTY_TEMPLATES = 256;
        int partyTemplateCount;

        static string PartyKey(List<string> composition, string chapter, int level, int upgrade, int crown, string floor, int? kit,
                               List<(int id, int level)> extra, List<int> bagOverride, List<(int id, int pieces)> extraEnchants, MemberExtras more)
        {
            var c = System.Globalization.CultureInfo.InvariantCulture;
            var b = new System.Text.StringBuilder();
            b.Append(string.Join("|", composition)).Append('#').Append(chapter).Append('#').Append(level).Append('#').Append(upgrade).Append('#').Append(crown)
             .Append('#').Append(floor ?? "~").Append('#').Append(kit.HasValue ? kit.Value.ToString(c) : "~").Append('#');
            if (extra != null) foreach (var (id, lv) in extra) b.Append(id).Append(':').Append(lv).Append(',');
            b.Append('#');
            if (bagOverride != null) { b.Append('b'); foreach (int id in bagOverride) b.Append(id).Append(','); }
            b.Append('#');
            if (extraEnchants != null) foreach (var (id, n) in extraEnchants) b.Append(id).Append(':').Append(n).Append(',');
            b.Append('#');
            if (more != null)
            {
                if (more.UniqueLevel.HasValue) b.Append('u').Append(more.UniqueLevel.Value);
                if (more.Passives != null) foreach (var (e, v, w) in more.Passives) b.Append('p').Append(e).Append('=').Append(v.ToString("R", c)).Append(w ? "i" : "f");
                if (more.Pieces != null) foreach (var kv in more.Pieces.OrderBy(x => x.Key, StringComparer.Ordinal)) b.Append('c').Append(kv.Key).Append('=').Append(kv.Value);
            }
            return b.ToString();
        }

        static List<Unit> CloneParty(List<Unit> template)
        {
            var bags = new Dictionary<Dictionary<int, int>, Dictionary<int, int>>(ReferenceComparer.Instance);
            var party = new List<Unit>(template.Count);
            foreach (var t in template)
            {
                var c = t.CloneFresh();
                if (!bags.TryGetValue(t.Items, out var bag)) bags[t.Items] = bag = c.Items;
                c.Items = bag;
                party.Add(c);
            }
            return party;
        }

        sealed class ReferenceComparer : IEqualityComparer<Dictionary<int, int>>
        {
            public static readonly ReferenceComparer Instance = new ReferenceComparer();
            public bool Equals(Dictionary<int, int> a, Dictionary<int, int> b) => ReferenceEquals(a, b);
            public int GetHashCode(Dictionary<int, int> a) => System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(a);
        }

        /// <summary>An enemy as UnitFactory.BuildEnemy makes it: built once for each enemy and row, then copied.</summary>
        public Unit EnemyUnit(int enemyId, bool front)
        {
            if (!enemyTemplates.TryGetValue((enemyId, front), out var template))
                template = enemyTemplates.GetOrAdd((enemyId, front), UnitFactory.BuildEnemy(Data, enemyId, front));
            return template.CloneFresh();
        }

        public List<Unit> ReferenceParty(List<string> composition, string chapter, int level, int upgrade, int crown, string floor, int? kit = null,
                                         List<(int id, int level)> extra = null, List<int> bagOverride = null,
                                         List<(int id, int pieces)> extraEnchants = null, MemberExtras more = null)
        {
            string key = PartyKey(composition, chapter, level, upgrade, crown, floor, kit, extra, bagOverride, extraEnchants, more);
            if (!partyTemplates.TryGetValue(key, out var template))
            {
                // a great many different parties (random cases) would fill the memory with templates nobody asks for again
                if (System.Threading.Interlocked.Increment(ref partyTemplateCount) > MAX_PARTY_TEMPLATES)
                {
                    partyTemplates.Clear();
                    System.Threading.Interlocked.Exchange(ref partyTemplateCount, 1);
                }
                template = partyTemplates.GetOrAdd(key, BuildReferenceParty(composition, chapter, level, upgrade, crown, floor, kit, extra, bagOverride, extraEnchants, more));
            }
            return CloneParty(template);
        }

        List<Unit> BuildReferenceParty(List<string> composition, string chapter, int level, int upgrade, int crown, string floor, int? kit,
                                       List<(int id, int level)> extra, List<int> bagOverride, List<(int id, int pieces)> extraEnchants, MemberExtras more)
        {
            var chars = new Dictionary<string, Character>();
            foreach (var c in Data.Characters) chars[c.Name] = c;
            var pool = Available(chapter);
            int sealbook = GrandSealbook(chapter, floor);
            int[] partyEnchants = sealbook != T.NONE && Data.SealbookEnchants.TryGetValue(sealbook, out var book) && book.Length > 0 ? book : Array.Empty<int>();
            int size = Setup.HasSetting("party_size") ? Setup.SettingInt("party_size") : 5;
            var taken = new HashSet<string>();
            var party = new List<Unit>();
            bool forge = ForgeOpen(floor);
            foreach (var roleName in composition)
            {
                if (party.Count >= size) break;
                var role = Setup.Roles[roleName];
                int baseClass = ClassId(role.Str("Base class"));
                foreach (var raw in role.Str("Characters (order of preference)").Split(';'))
                {
                    string name = raw.Trim();
                    chars.TryGetValue(name, out var c);
                    if (pool.Contains(name) && !taken.Contains(name) && c != null && c.BaseClass == baseClass)
                    {
                        int joinLevel = LevelOfExp(c.StartExp);
                        party.Add(BuildRoleMember(roleName, c, Math.Max(level, joinLevel), upgrade, crown, forge, WithPieces(UniquePieces(roleName, chapter, floor), more),
                                                  partyEnchants, PersonalSealbook(roleName, chapter, floor), extra, extraEnchants, more));
                        taken.Add(name);
                        break;
                    }
                }
            }
            foreach (var name in pool)
            {
                if (party.Count >= size) break;
                chars.TryGetValue(name, out var c);
                if (taken.Contains(name) || c == null) continue;
                foreach (var roleName in Setup.RoleOrder)
                {
                    var role = Setup.Roles[roleName];
                    if (ClassId(role.Str("Base class")) == c.BaseClass)
                    {
                        int joinLevel = LevelOfExp(c.StartExp);
                        party.Add(BuildRoleMember(roleName, c, Math.Max(level, joinLevel), upgrade, crown, forge, WithPieces(UniquePieces(roleName, chapter, floor), more),
                                                  partyEnchants, PersonalSealbook(roleName, chapter, floor), extra, extraEnchants, more));
                        taken.Add(name);
                        break;
                    }
                }
            }
            int front = Setup.HasSetting("front_size") ? Setup.SettingInt("front_size") : 3;
            int frontCount = party.Count(u => u.Front);
            if (frontCount > front)
            {
                var order = party.Where(u => u.Front).OrderBy(u => u.MaxHp).ToList();
                for (int i = 0; i < frontCount - front; i++) order[i].Front = false;
            }
            if (!party.Any(u => u.Front) && party.Count > 0)
            {
                Unit best = null;
                foreach (var u in party) if (best == null || u.MaxHp > best.MaxHp) best = u;
                best.Front = true;
            }
            int count = kit ?? (Setup.HasSetting("kit_count") ? Setup.SettingInt("kit_count") : 0);
            var bag = new Dictionary<int, int>();
            if (bagOverride != null)
            {
                foreach (int id in bagOverride) bag[id] = PyMath.Round(count * 1.0);
            }
            else
            {
                foreach (var r in Setup.Kit)
                {
                    double share = r.Truthy("Share") ? r.Dbl("Share") : 1.0;
                    bag[r.Int("Item_ID")] = PyMath.Round(count * share);
                }
            }
            foreach (var u in party) u.Items = bag;
            if (sealbook != T.NONE)
            {
                var summon = SealbookSummon(sealbook, party);
                if (summon != null)
                {
                    summon.Items = new Dictionary<int, int>();
                    party.Add(summon);
                }
            }
            return party;
        }

        public List<Unit> PartyOfRoles(string cid, List<string> roles, int? level, int? crown)
        {
            var cp = Setup.Checkpoint(cid);
            int lv = level ?? ReferenceLevels()[cid].level;
            int cr = crown ?? (cp.Truthy("Crown bonus") ? cp.Int("Crown bonus") : 0);
            return ReferenceParty(roles, cp.Str("Chapter"), lv, CheckpointGear(cid), cr, cp.Str("Floor"));
        }

        // --- enemies ----------------------------------------------------------------------------------------------------
        public Group FixedBattle(string floor, int number)
        {
            var battle = Data.FindFixed(floor, number);
            var group = new Group();
            foreach (var (enemy, front) in battle.Enemies) group.Units.Add(EnemyUnit(enemy, front));
            for (int i = 0; i < Math.Min(group.Units.Count, battle.Slots.Length); i++) group.Units[i].Slot = battle.Slots[i];
            group.Zone = BattleZone(floor, number);
            group.Floor = floor;
            group.Number = number;
            return group;
        }

        public Zone BattleZone(string floor, int number)
        {
            if (!Data.BattleCells.TryGetValue((floor, number), out var cells) || cells.Length == 0) return null;
            var cell = cells[0];
            var zone = new Zone { Slots = cell.Slots.Where(v => v != 0).ToArray(), NoMagic = cell.Slots.Contains(NO_MAGIC) };
            if (Data.ZoneFactorsMap.TryGetValue((floor, cell.Zone), out var f)) zone.Factors = f;
            return zone;
        }

        public Group RandomGroup(FloorZone zone, PyRandom rng)
        {
            var formations = zone.Formations.Where(f => f.Enemies.All(e => Data.Enemies.ContainsKey(e.enemy))).ToList();
            var weights = formations.Select(f => (double)Math.Max(1, (int)f.Chance)).ToArray();
            var pick = formations[rng.ChoicesIndex(weights)];
            var group = new Group();
            foreach (var (e, front) in pick.Enemies) group.Units.Add(EnemyUnit(e, front));
            for (int i = 0; i < Math.Min(group.Units.Count, pick.Slots.Length); i++) group.Units[i].Slot = pick.Slots[i];
            return group;
        }

        /// <summary>measures.random_group with the formation drawn already (index among the formations whose enemies are all known).</summary>
        public Group RandomGroupAt(FloorZone zone, int index)
        {
            var formations = zone.Formations.Where(f => f.Enemies.All(e => Data.Enemies.ContainsKey(e.enemy))).ToList();
            var pick = formations[index];
            var group = new Group();
            foreach (var (e, front) in pick.Enemies) group.Units.Add(EnemyUnit(e, front));
            for (int i = 0; i < Math.Min(group.Units.Count, pick.Slots.Length); i++) group.Units[i].Slot = pick.Slots[i];
            return group;
        }

        /// <summary>scenario.Group(build_enemy(...) for each enemy of the list): a battle away from any cell of the floor.</summary>
        public Group CustomGroup(List<EnemySpec> enemies)
        {
            var group = new Group();
            foreach (var spec in enemies)
            {
                var unit = EnemyUnit(spec.Enemy, spec.Front);
                if (spec.HasScript) unit.Script = spec.Script;
                if (spec.Attacks != null) unit.Attacks = spec.Attacks;
                if (spec.Passives != null)
                    foreach (int attackId in spec.Passives)
                    {
                        var attack = Data.GetAttack(attackId);
                        if (attack != null)
                            for (int k = 0; k < attack.EffId.Length; k++) unit.SetPassive(attack.EffId[k], attack.EffValue[k], attack.EffIsInt[k]);
                    }
                group.Units.Add(unit);
            }
            return group;
        }

        public FloorZone FindZone(string name)
        {
            foreach (var z in Data.Floors) if (z.Name == name) return z;
            throw new InvalidOperationException("no floor zone " + name);
        }

        int ZoneLevel(string floor, int number, double share)
        {
            if (!Data.BattleCells.TryGetValue((floor, number), out var cells) || cells.Length == 0) return T.NONE;
            int zone = cells[0].Zone;
            var formations = new List<(int level, double chance)>();
            foreach (var z in Data.Floors)
            {
                if (z.Floor != floor || z.Zone != zone) continue;
                foreach (var f in z.Formations)
                {
                    if (!f.Enemies.All(e => Data.Enemies.ContainsKey(e.enemy))) continue;
                    int lv = int.MinValue;
                    foreach (var (e, _) in f.Enemies) lv = Math.Max(lv, Data.Enemies[e].Level);
                    formations.Add((lv, f.Chance));
                }
            }
            if (formations.Count == 0) return T.NONE;
            double total = 0;
            foreach (var (_, c) in formations) total += c;
            double covered = 0;
            // sorted(formations): by level, then by chance
            foreach (var (level, chance) in formations.OrderBy(x => x.level).ThenBy(x => x.chance))
            {
                covered += chance;
                if (covered >= share * total) return level;
            }
            return formations.Max(x => x.level);
        }

        public Dictionary<string, (int level, string source)> ReferenceLevels()
        {
            lock (cacheLock)
            {
                if (levels != null) return levels;
                double share = Setup.SettingDouble("zone_level_share");
                var found = new Dictionary<string, (int, string)>();
                int previous = 0;
                foreach (var cp in Setup.Checkpoints)
                {
                    string id = cp.Str("ID");
                    Setup.GuideLevels.TryGetValue(id, out var guide);
                    int zone = ZoneLevel(cp.Str("Floor"), BattleNumbers(cp)[0], share);
                    int level; string source;
                    if (guide.HasValue) { level = (int)Math.Truncate(guide.Value); source = "guide"; }
                    else if (zone != T.NONE) { level = zone; source = "zone"; }
                    else { level = previous; source = "before"; }
                    if (level < previous) { level = previous; source = source + ", held"; }
                    found[id] = (level, source);
                    previous = level;
                }
                levels = found;
                return levels;
            }
        }

        void Prepare(List<Unit> party, Group enemies)
        {
            foreach (var row in Setup.Preparation)
            {
                if (row.Str("Floor") == enemies.Floor && enemies.Number != T.NONE && row.Int("Battle") == enemies.Number)
                {
                    int index = row.Int("Resistance index"), value = row.Int("Value");
                    foreach (var unit in party) unit.ResistBase[index] = Math.Max(unit.ResistBase[index], value);
                }
            }
            foreach (var row in Setup.ZoneChanges)
            {
                var zone = enemies.Zone;
                if (zone != null && row.Str("Floor") == enemies.Floor && enemies.Number != T.NONE && row.Int("Battle") == enemies.Number)
                {
                    var slots = new List<int>(zone.Slots);
                    int slot = row.Int("Slot");
                    int k = slots.IndexOf(slot);
                    if (k >= 0)
                    {
                        object ns = row.Get("New slot");
                        if (ns == null || (ns is string s && s == "")) slots.RemoveAt(k);
                        else slots[k] = Setup.ToInt(ns);
                    }
                    var changed = zone.Clone();
                    changed.Slots = slots.ToArray();
                    enemies.Zone = changed;
                }
            }
        }

        /// <summary>sim.scenario.walked_zones: the zones of a floor a party of this level walks (random battles, the strongest enemy at most
        /// gear_level_margin levels above it); when the floor has none, the zones of its dungeon under the same rule.</summary>
        public List<FloorZone> WalkedZones(string floorName, int level)
        {
            int margin = Setup.SettingInt("gear_level_margin");
            bool Fits(FloorZone zone)
            {
                if (zone.Formations.Length == 0) return false;
                int top = int.MinValue;
                bool any = false;
                foreach (var f in zone.Formations)
                    foreach (var (e, _) in f.Enemies)
                        if (Data.Enemies.TryGetValue(e, out var rec)) { top = Math.Max(top, rec.Level); any = true; }
                if (!any) throw new InvalidOperationException("max() of an empty sequence");
                return top <= level + margin;
            }
            string Head(string name)
            {
                int at = name.IndexOf(" zone", StringComparison.Ordinal);
                return at < 0 ? name : name.Substring(0, at);
            }
            string Four(string name) => name.Length <= 4 ? name : name.Substring(0, 4);
            var found = new List<FloorZone>();
            foreach (var z in Data.Floors) if (Head(z.Name) == floorName && Fits(z)) found.Add(z);
            if (found.Count > 0) return found;
            foreach (var z in Data.Floors) if (Four(z.Name) == Four(floorName) && Fits(z)) found.Add(z);
            return found;
        }

        /// <summary>sim.scenario.play with the options of the setup and a seed: the runs, in order (a run does not depend on the others).</summary>
        public RunResult[] PlayRuns(Func<List<Unit>> partyFactory, Func<ulong, List<Group>> enemyFactoryFor, int runs, ulong seed, BattleOptions options,
                                    int threads = 1)
        {
            var results = new RunResult[runs];
            if (threads <= 1 || runs <= 1)
                for (int k = 0; k < runs; k++) results[k] = PlayRun(partyFactory, () => enemyFactoryFor(seed + (ulong)k), seed + (ulong)k, options);
            else
                System.Threading.Tasks.Parallel.For(0, runs, new System.Threading.Tasks.ParallelOptions { MaxDegreeOfParallelism = threads },
                    k => results[k] = PlayRun(partyFactory, () => enemyFactoryFor(seed + (ulong)k), seed + (ulong)k, options));
            return results;
        }

        /// <summary>sim.measures.play_checkpoint: the level of the party and the summary of its runs at the fixed battles of the checkpoint.</summary>
        /// <summary>A job's guest that hires nobody but keeps the summon (the side "without" of the mercenary battery).</summary>
        public const string NO_GUEST = "-";

        /// <summary>The party with the mercenary the sheet CheckpointGuests hires for this boss, if any.</summary>
        public List<Unit> WithCheckpointGuest(List<Unit> party, string cid)
        {
            string guest = Setup.CheckpointGuest(cid);
            if (guest == null) return party;
            var stage = UnitFactory.GuestStageAt(Data, Setup, guest, cid);
            if (stage != null) party.Add(UnitFactory.BuildGuest(Data, stage));
            return party;
        }

        public (int level, Summary summary) PlayCheckpoint(string cid, int? runs, int threads = 1)
        {
            var cp = Setup.Checkpoint(cid);
            int level = ReferenceLevels()[cid].level;
            int gear = CheckpointGear(cid);
            int crown = cp.Truthy("Crown bonus") ? cp.Int("Crown bonus") : 0;
            int n = runs ?? Setup.SettingInt("runs");
            ulong seed = (ulong)Setup.SettingInt("seed");
            var results = PlayRuns(() => WithCheckpointGuest(ReferenceParty(Setup.Composition, cp.Str("Chapter"), level, gear, crown, cp.Str("Floor")), cid),
                                   s => BattleNumbers(cp).Select(number => FixedBattle(cp.Str("Floor"), number)).ToList(),
                                   n, seed, OptionsFrom(Setup, null), threads);
            return (level, Summary.Of(results.ToList()));
        }

        // --- play ------------------------------------------------------------------------------------------------------
        /// <summary>One run of scenario.play for run number k: party and enemy groups built fresh, a generator seeded with seed + k.</summary>
        public RunResult PlayRun(Func<List<Unit>> partyFactory, Func<List<Group>> enemyFactory, ulong seed, BattleOptions options,
                                 Action<Battle, int> onBattle = null, PyRandom rngOverride = null)
        {
            var rng = rngOverride ?? new PyRandom(seed);
            long t0 = System.Diagnostics.Stopwatch.GetTimestamp(), b0 = GC.GetAllocatedBytesForCurrentThread();
            var party = partyFactory();
            var groups = enemyFactory();
            System.Threading.Interlocked.Add(ref BuildTicks, System.Diagnostics.Stopwatch.GetTimestamp() - t0);
            System.Threading.Interlocked.Add(ref BuildBytes, GC.GetAllocatedBytesForCurrentThread() - b0);
            RunResult result = null;
            int index = 0;
            foreach (var enemies in groups)
            {
                foreach (var unit in party)
                {
                    unit.ClearStatuses();
                    unit.Chant = null;
                    unit.Song = new List<string>();
                    unit.Dance = new List<string>();
                }
                party = party.Where(u => u.Kind == Kind.Member || u.Kind == Kind.Summon).ToList();
                Prepare(party, enemies);
                var battle = new Battle(Data, party, enemies.Units, rng, Policy, enemies.Boss ? options.NotRandom() : options, enemies.Zone, maxTime);
                battle.Fixed = enemies.Number != T.NONE;
                onBattle?.Invoke(battle, index++);
                var part = battle.Run();
                if (result == null)
                {
                    result = new RunResult
                    {
                        Won = part.Won, Lost = part.Lost, Time = part.Time, Actions = part.Actions, LowestHp = part.LowestHp,
                        EnemyDamage = part.EnemyDamage, EnemyActions = part.EnemyActions, PartyMaxHp = part.PartyMaxHp,
                        HpLeft = part.HpLeft, TpLeft = part.TpLeft, Alive = part.Alive,
                    };
                    result.Parts.Add(part);
                }
                else
                {
                    result.Parts.Add(part);
                    result.Won = part.Won; result.Lost = part.Lost;
                    result.Time = result.Time + part.Time;
                    result.Actions = result.Actions + part.Actions;
                    result.HpLeft = part.HpLeft;
                    result.LowestHp = Math.Min(result.LowestHp, part.LowestHp);
                    result.EnemyDamage += part.EnemyDamage;
                    result.EnemyActions += part.EnemyActions;
                    result.TpLeft = part.TpLeft;
                    result.Alive = part.Alive;
                }
                if (!part.Won) break;
                RecoverAfterBattle(party);
            }
            return result;
        }

        /// <summary>docs/FORMULAS.md 12.14: the living members with Generous Heart give the party a share, capped at 0.30.</summary>
        public static void RecoverAfterBattle(List<Unit> party)
        {
            var living = party.Where(u => u.Alive && u.Kind == Kind.Member).ToList();
            for (int pass = 0; pass < 2; pass++)
            {
                int effect = pass == 0 ? 272 : 273;
                var values = new List<double>(); var extras = new List<double>();
                foreach (var u in living)
                {
                    double v = u.Passive(effect, 0.0);
                    if (u.HasPassive(effect) && v != 0.0)
                    {
                        values.Add(v + u.Passive(278, 0.0));
                        extras.Add(u.Passive(353, 0.0));
                    }
                }
                double share = F.AfterBattleFraction(values, extras);
                foreach (var u in living)
                {
                    bool full = effect == 272 && u.Pieces(193) > 0;
                    int gain = F.AfterBattleRecovery(pass == 0 ? u.MaxHp : u.MaxTp, share, full);
                    if (pass == 0) u.Hp = Math.Min(u.MaxHp, u.Hp + gain);
                    else u.Tp = Math.Min(u.MaxTp, u.Tp + gain);
                }
            }
        }
    }

    /// <summary>sim.measures.summary: the figures of a set of battles of one checkpoint.</summary>
    public sealed class Summary
    {
        public double Won;
        public double? Time;
        public double LowestHp, Pressure;

        public static Summary Of(List<RunResult> results)
        {
            int runs = Math.Max(1, results.Count);
            var wins = results.Where(r => r.Won).ToList();
            long actions = 0, damage = 0, partyMax = 0;
            foreach (var r in results) { actions += r.EnemyActions; damage += r.EnemyDamage; partyMax += r.PartyMaxHp; }
            double maxHp = (double)partyMax / runs;
            var s = new Summary { Won = (double)wins.Count / runs };
            if (wins.Count > 0)
            {
                var t = new PySum();
                foreach (var r in wins) t.AddFloat(r.Time);
                s.Time = t.Result / wins.Count;
            }
            var l = new PySum();
            foreach (var r in results) l.AddFloat(r.LowestHp);
            s.LowestHp = l.Result / runs;
            s.Pressure = actions != 0 && maxHp != 0 ? (double)damage / actions / maxHp : 0.0;
            return s;
        }
    }
}
