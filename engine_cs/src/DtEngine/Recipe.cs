using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace DtEngine
{
    /// <summary>A member put into a party that the job names by her role: what the tools call the "tested" member (build_role_member).</summary>
    public sealed class TestedSpec
    {
        public string Role;
        public string Character;                  // null: the first of the role's preference not among the members kept, else any character of her base class
        public int? Level, Crown;                 // null: those of the party
        public bool Forge;
        public List<(int id, int level)> Extra = new List<(int, int)>();
        public bool UniquePieces;                 // the unique gear and the personal sealbook of the role at the checkpoint
        public bool NoUnique;                     // the character without her unique skill
        public List<(int effect, double amount)> PassivesAdd = new List<(int, double)>();
        public double? Pep;
        public Dictionary<string, string> Pieces;   // pieces in the place of the role's own (column of the sheet Roles -> name), over the unique pieces

        public static TestedSpec FromJson(JsonElement e)
        {
            var t = new TestedSpec { Role = e.GetProperty("role").GetString() };
            if (e.TryGetProperty("character", out var c) && c.ValueKind == JsonValueKind.String) t.Character = c.GetString();
            if (e.TryGetProperty("level", out var l) && l.ValueKind == JsonValueKind.Number) t.Level = l.GetInt32();
            if (e.TryGetProperty("crown", out var cr) && cr.ValueKind == JsonValueKind.Number) t.Crown = cr.GetInt32();
            if (e.TryGetProperty("forge", out var f)) t.Forge = f.ValueKind == JsonValueKind.True;
            if (e.TryGetProperty("extra_skills", out var x) && x.ValueKind == JsonValueKind.Object)
                foreach (var p in x.EnumerateObject()) t.Extra.Add((int.Parse(p.Name), p.Value.GetInt32()));
            if (e.TryGetProperty("unique_pieces", out var u)) t.UniquePieces = u.ValueKind == JsonValueKind.True;
            if (e.TryGetProperty("no_unique", out var n)) t.NoUnique = n.ValueKind == JsonValueKind.True;
            if (e.TryGetProperty("passives_add", out var pa) && pa.ValueKind == JsonValueKind.Object)
                foreach (var p in pa.EnumerateObject()) t.PassivesAdd.Add((int.Parse(p.Name), p.Value.GetDouble()));
            if (e.TryGetProperty("pep", out var pep) && pep.ValueKind == JsonValueKind.Number) t.Pep = pep.GetDouble();
            if (e.TryGetProperty("pieces", out var pc) && pc.ValueKind == JsonValueKind.Object)
            {
                t.Pieces = new Dictionary<string, string>();
                foreach (var p in pc.EnumerateObject()) t.Pieces[p.Name] = p.Value.GetString();
            }
            return t;
        }
    }

    /// <summary>A bonus given to the first members of the party (a party skill: measures/party_skills.py).</summary>
    public sealed class BonusSpec
    {
        public int Count;
        public int Hp, Tp;
        public List<(int index, int amount)> Resist = new List<(int, int)>();
        public List<(int index, int amount)> Stats = new List<(int, int)>();

        public static BonusSpec FromJson(JsonElement e)
        {
            var b = new BonusSpec { Count = e.GetProperty("count").GetInt32() };
            if (e.TryGetProperty("hp", out var hp)) b.Hp = hp.GetInt32();
            if (e.TryGetProperty("tp", out var tp)) b.Tp = tp.GetInt32();
            if (e.TryGetProperty("resist", out var r) && r.ValueKind == JsonValueKind.Object)
                foreach (var p in r.EnumerateObject()) b.Resist.Add((int.Parse(p.Name), p.Value.GetInt32()));
            if (e.TryGetProperty("stats", out var s) && s.ValueKind == JsonValueKind.Object)
                foreach (var p in s.EnumerateObject()) b.Stats.Add((StatIndex(p.Name), p.Value.GetInt32()));
            return b;
        }

        static int StatIndex(string name)
        {
            switch (name)
            {
                case "atk": return Unit.ATK;
                case "def": return Unit.DEF;
                case "int": return Unit.INT;
                case "res": return Unit.RES;
                case "dex": return Unit.DEX;
                case "agi": return Unit.AGI;
                default: throw new InvalidOperationException("no stat " + name);
            }
        }
    }

    /// <summary>What the tools do to the reference party of a checkpoint before they play it: a bonus on its first members, a filter on
    /// its members, a tested member in the place of some, the summon left out. Every field is data given by the tool.</summary>
    public sealed class PartyRecipe
    {
        public List<BonusSpec> Bonuses = new List<BonusSpec>();
        public List<(int item, int count)> BagSet;     // the bag of the first unit with these items set, given to every member (measures/tp_items_trial.py)
        public string NameNot, RoleNot;           // members (units that have a role, for RoleNot) left out
        public bool DropLast;                     // members[:-1]
        public int? First;                        // members[:n]
        public bool DropOthers;                   // the summon and every unit that is no member
        public List<TestedSpec> Tested = new List<TestedSpec>();
        public string Place = "append";           // "append": kept + tested + others; "replace_role": the member of the tested role is replaced, else the last place
        public string Items = "none";             // "first_kept": the tested member takes the bag of the first member kept (an empty bag when none); "all_first": every member takes the bag of the first member after the placing

        public static PartyRecipe FromJson(JsonElement e)
        {
            var r = new PartyRecipe();
            if (e.TryGetProperty("bonuses", out var b) && b.ValueKind == JsonValueKind.Array)
                foreach (var x in b.EnumerateArray()) r.Bonuses.Add(BonusSpec.FromJson(x));
            if (e.TryGetProperty("bag_set", out var bs) && bs.ValueKind == JsonValueKind.Object)
            {
                r.BagSet = new List<(int, int)>();
                foreach (var p in bs.EnumerateObject()) r.BagSet.Add((int.Parse(p.Name), p.Value.GetInt32()));
            }
            if (e.TryGetProperty("name_not", out var nn) && nn.ValueKind == JsonValueKind.String) r.NameNot = nn.GetString();
            if (e.TryGetProperty("role_not", out var rn) && rn.ValueKind == JsonValueKind.String) r.RoleNot = rn.GetString();
            if (e.TryGetProperty("drop_last", out var dl)) r.DropLast = dl.ValueKind == JsonValueKind.True;
            if (e.TryGetProperty("first", out var fi) && fi.ValueKind == JsonValueKind.Number) r.First = fi.GetInt32();
            if (e.TryGetProperty("drop_others", out var dop)) r.DropOthers = dop.ValueKind == JsonValueKind.True;
            if (e.TryGetProperty("tested", out var t) && t.ValueKind == JsonValueKind.Array)
                foreach (var x in t.EnumerateArray()) r.Tested.Add(TestedSpec.FromJson(x));
            if (e.TryGetProperty("place", out var pl) && pl.ValueKind == JsonValueKind.String) r.Place = pl.GetString();
            if (e.TryGetProperty("items", out var it) && it.ValueKind == JsonValueKind.String) r.Items = it.GetString();
            return r;
        }
    }

    public sealed partial class Scenario
    {
        /// <summary>The index random_group draws among the formations of a zone whose enemies are all known (rng.choices over their chances).</summary>
        public int RandomIndex(FloorZone zone, PyRandom rng)
        {
            var formations = zone.Formations.Where(f => f.Enemies.All(e => Data.Enemies.ContainsKey(e.enemy))).ToList();
            var weights = formations.Select(f => (double)Math.Max(1, (int)f.Chance)).ToArray();
            return rng.ChoicesIndex(weights);
        }

        /// <summary>A copy of a party built once, for one run: the same sharing of the bags of items as in the party it was made from.</summary>
        public static List<Unit> CloneOf(List<Unit> template) => CloneParty(template);

        /// <summary>The member a TestedSpec names, built for the checkpoint of a job (build_role_member as the tools call it). taken: the characters already in the party.</summary>
        public Unit BuildTested(JobSpec job, TestedSpec t, HashSet<string> taken, out string name)
        {
            var cp = Setup.Checkpoint(job.Cid);
            int level = job.Level ?? ReferenceLevels()[job.Cid].level;
            int gear = CheckpointGear(job.Cid);
            int crown = job.Crown ?? (cp.Truthy("Crown bonus") ? cp.Int("Crown bonus") : 0);
            string chapter = cp.Str("Chapter"), floor = cp.Str("Floor");
            var chars = new Dictionary<string, Character>();
            foreach (var c in Data.Characters) chars[c.Name] = c;
            var row = Setup.Roles[t.Role];
            Character who;
            if (t.Character != null) who = chars[t.Character];
            else
            {
                string pick = row.Str("Characters (order of preference)").Split(';').Select(n => n.Trim())
                                 .FirstOrDefault(n => chars.ContainsKey(n) && !taken.Contains(n));
                if (pick == null)
                {
                    int baseClass = ClassId(row.Str("Base class"));
                    pick = Data.Characters.First(c => !taken.Contains(c.Name) && c.BaseClass == baseClass).Name;
                }
                who = chars[pick];
            }
            if (t.NoUnique) who = new Character { Name = who.Name, BaseClass = who.BaseClass, Flag = who.Flag, StartExp = who.StartExp, UniqueSkill = T.NONE };
            name = who.Name;
            var pieces = t.UniquePieces ? UniquePieces(t.Role, chapter, floor) : null;
            if (t.Pieces != null)
            {
                pieces = pieces != null ? new Dictionary<string, string>(pieces) : new Dictionary<string, string>();
                foreach (var kv in t.Pieces) pieces[kv.Key] = kv.Value;
            }
            int sealbook = t.UniquePieces ? PersonalSealbook(t.Role, chapter, floor) : T.NONE;
            var tested = BuildRoleMember(t.Role, who, t.Level ?? level, gear, t.Crown ?? crown, t.Forge, pieces, Array.Empty<int>(), sealbook,
                                         t.Extra.Count > 0 ? t.Extra : null);
            foreach (var (effect, amount) in t.PassivesAdd) tested.SetPassive(effect, tested.Passive(effect, 0.0) + amount, false);
            if (t.Pep.HasValue) tested.Pep = t.Pep.Value;
            return tested;
        }

        /// <summary>The reference party of a checkpoint after the recipe of a job: what tools/class_stages.py, tools/skill_value.py, tools/skill_worth.py,
        /// tools/sim_audit.py and the scripts of measures/ do with scenario.reference_party and scenario.build_role_member.
        /// names: the characters the tested members were given.</summary>
        public List<Unit> RecipeParty(JobSpec job, PartyRecipe r, List<string> names, List<Unit> testedUnits = null)
        {
            var cp = Setup.Checkpoint(job.Cid);
            int level = job.Level ?? ReferenceLevels()[job.Cid].level;
            int gear = CheckpointGear(job.Cid);
            int crown = job.Crown ?? (cp.Truthy("Crown bonus") ? cp.Int("Crown bonus") : 0);
            string chapter = cp.Str("Chapter"), floor = cp.Str("Floor");
            var roles = job.Roles ?? Setup.Composition;
            var whole = ReferenceParty(roles, chapter, level, gear, crown, floor, job.Kit, job.ExtraSkills, job.Bag, job.ExtraEnchants, job.More);
            foreach (var bonus in r.Bonuses)
            {
                foreach (var u in whole.Where(u => u.Kind == Kind.Member).Take(bonus.Count))
                {
                    if (bonus.Hp != 0) { u.MaxHpBase += bonus.Hp; u.Hp = u.MaxHp; }
                    if (bonus.Tp != 0) { u.MaxTp += bonus.Tp; u.Tp = u.MaxTp; }
                    foreach (var (index, amount) in bonus.Resist) u.ResistBase[index] += amount;
                    foreach (var (index, amount) in bonus.Stats) u.Base[index] += amount;
                }
            }
            if (r.BagSet != null)
            {
                var bag = new Dictionary<int, int>(whole[0].Items);
                foreach (var (item, count) in r.BagSet) bag[item] = count;
                foreach (var u in whole) if (u.Kind == Kind.Member) u.Items = bag;
            }
            var members = whole.Where(u => u.Kind == Kind.Member && (r.NameNot == null || u.Name != r.NameNot)
                                           && (r.RoleNot == null || !(u.HasRole && u.Role == r.RoleNot))).ToList();
            var others = whole.Where(u => u.Kind != Kind.Member && (r.RoleNot == null || !(u.HasRole && u.Role == r.RoleNot))).ToList();
            if (r.DropLast && members.Count > 0) members.RemoveAt(members.Count - 1);
            if (r.First.HasValue && members.Count > r.First.Value) members.RemoveRange(r.First.Value, members.Count - r.First.Value);
            var chars = new Dictionary<string, Character>();
            foreach (var c in Data.Characters) chars[c.Name] = c;
            foreach (var t in r.Tested)
            {
                var tested = BuildTested(job, t, new HashSet<string>(members.Select(u => u.Name)), out string name);
                names?.Add(name);
                testedUnits?.Add(tested);
                if (r.Items == "first_kept") tested.Items = members.Count > 0 ? members[0].Items : new Dictionary<int, int>();
                if (r.Place == "replace_role")
                {
                    int same = members.FindIndex(u => u.HasRole && u.Role == t.Role);
                    if (same >= 0) members[same] = tested;
                    else
                    {
                        int size = Setup.HasSetting("party_size") ? Setup.SettingInt("party_size") : 5;
                        members = members.Take(size - 1).ToList();
                        members.Add(tested);
                    }
                }
                else members.Add(tested);
            }
            if (r.Items == "all_first" && members.Count > 0) foreach (var u in members) u.Items = members[0].Items;
            if (r.DropOthers) others.Clear();
            var result = new List<Unit>(members);
            result.AddRange(others);
            return result;
        }
    }
}
