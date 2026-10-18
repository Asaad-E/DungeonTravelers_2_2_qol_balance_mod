using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>dtcli skill-battery [skill names, comma separated]: every active and passive skill a class learns, with and without, in each party of
    /// the sheet BatteryParties at every story boss of each stage where a class that knows it is played, and on rows of random battles of the
    /// same floors; the same seeds with and without. The best cell of each skill is played again at more runs; the verdict comes from it.
    /// Configuration: section skill_battery of data_tables/measure_config.json. Output: docs/generated/SKILL_BATTERY.md and
    /// docs/generated/skill_battery/part_1.json. Balance variant.</summary>
    public static class SkillBattery
    {
        sealed class Entry
        {
            public Skill Skill;
            public string Stage, Role;
            public (string cond, string act)? Rule;
            public string Weapon;                // a weapon in the place of the role's own when hers cannot use the skill, else null
            public string Girl, Label;           // unique-battery: the girl whose unique skill is tested, and the name of that skill
            public string Guest;                 // mercenary-battery: the mercenary hired in the place of the summon
        }

        sealed class Cell
        {
            public Entry Entry;
            public string Cid, Party, Context;
            public int Chain;
            public JobResult Without, With;
            public double Wins, Length, Hp, Tp, Alive;      // with - without: share of wins, share by which the won fights are shorter, HP left, TP left, members alive
            public bool Same, Serves, Hurts;
            public double Score;
        }

        static (double wins, double? time, double hp, double tp, double alive) Figures(JobResult r)
        {
            var won = r.Runs.Where(x => x.Won).ToList();
            int n = r.Runs.Length;
            return ((double)won.Count / n, won.Count > 0 ? Py.Sum(won.Select(x => x.Time)) / won.Count : (double?)null,
                    Py.Sum(r.Runs.Select(x => x.HpLeft)) / n, Py.Sum(r.Runs.Select(x => x.TpLeft)) / n, (double)r.Runs.Sum(x => x.Alive) / n);
        }

        static bool SameRuns(JobResult a, JobResult b)
        {
            if (a.Runs.Length != b.Runs.Length) return false;
            for (int k = 0; k < a.Runs.Length; k++)
            {
                var x = a.Runs[k]; var y = b.Runs[k];
                if (x.Won != y.Won || x.Time != y.Time || x.HpLeft != y.HpLeft || x.TpLeft != y.TpLeft || x.Actions != y.Actions) return false;
            }
            return true;
        }

        static void Judge(Cell cell, Obj cfg)
        {
            double w = cfg.D("wins"), l = cfg.D("length"), h = cfg.D("hp");
            var a = Figures(cell.Without); var b = Figures(cell.With);
            cell.Wins = b.wins - a.wins;
            cell.Length = a.time.HasValue && b.time.HasValue ? 1 - b.time.Value / a.time.Value : 0.0;
            cell.Hp = b.hp - a.hp;
            cell.Tp = b.tp - a.tp;
            cell.Alive = b.alive - a.alive;
            double tpGain = cfg.D("tp"), aliveGain = cfg.D("alive");
            cell.Same = SameRuns(cell.Without, cell.With);
            cell.Serves = !cell.Same && (cell.Wins >= w || (cell.Wins > -w && (cell.Length >= l || cell.Hp >= h || cell.Tp >= tpGain || cell.Alive >= aliveGain)));
            cell.Hurts = !cell.Same && (cell.Wins <= -w || (cell.Wins < w && cell.Length <= -l && cell.Hp <= 0));
            cell.Score = cell.Wins <= -w ? double.NegativeInfinity
                       : new[] { cell.Wins / w, cell.Length / l, cell.Hp / h, cell.Tp / tpGain, cell.Alive / aliveGain }.Max();
        }

        /// <summary>The stages of the configuration ({name, low, high, columns}) that a level falls in.</summary>
        static Obj StageOf(Obj cfg, int level) =>
            cfg.A("stages").Cast<Obj>().FirstOrDefault(s => level >= Py.Num(s.Get("low")) && level <= Py.Num(s.Get("high")));

        /// <summary>The weapon the member takes for a skill that needs one her role does not carry (codes of Policy.WeaponAllows: the type + 1;
        /// 0, any short-range weapon, and 16, a shield, are left as they are): the piece the configuration names for the first type allowed.</summary>
        static string WeaponFor(Ctx c, GameData data, Obj cfg, Skill skill, string role)
        {
            var codes = skill.Weapons.Where(w => w != 0 && w != 16).ToList();
            if (codes.Count == 0 || codes.Count < skill.Weapons.Length) return null;
            var byName = new Dictionary<string, int>();
            foreach (var p in data.Equipment.Values) if (p.Category == 0 && !byName.ContainsKey(p.Name)) byName[p.Name] = p.Type;
            foreach (var part in c.Setup.Roles[role].Str("Weapon").Split(';', '|'))
            {
                string name = part.Contains('=') ? part.Substring(part.IndexOf('=') + 1).Trim() : part.Trim();
                if (byName.TryGetValue(name, out int type) && codes.Contains(type + 1)) return null;
            }
            var names = cfg.O("weapon_of_type");
            foreach (int code in codes) if (names.Has((code - 1).ToString())) return names.S((code - 1).ToString());
            return null;
        }

        static JobSpec Job(Ctx c, Cell cell, bool use, int runs, bool record = false)
        {
            var e = cell.Entry;
            var sc = c.Sc("variant");
            var cp = c.Checkpoint(cell.Cid);
            int levels = e.Skill != null && e.Skill.Levels != 0 ? e.Skill.Levels : 1;
            // the party "Reference" is the reference party of the checkpoint; the others are parties of BatteryParties
            var roles = cell.Party == "Reference" ? null : c.Setup.Battery.First(b => b.name == cell.Party).roles;
            Obj enemies = null;
            Obj options = null;
            if (cell.Chain > 0)
            {
                int level = sc.ReferenceLevels()[cell.Cid].level;
                enemies = Jb.Chain(sc.WalkedZones(cp.Str("Floor"), level).Select(z => z.Name), (long)Py.Num(c.In("skill_battery").Get("chain_seed")), cell.Chain);
                if (cell.Context == "walk_boss") { enemies.Set("then_checkpoint", true); options = new Obj { { "random_battle", true } }; }
            }
            if (e.Guest != null)
                // mercenary-battery: the party as built (with the summon of its grand sealbook) against the same party with the mercenary
                // hired beside it (units 3000 and 3001 of the program)
                return Jb.Make(c, side, cell.Cid, roles: roles, runs: runs, enemies: enemies, options: options, guest: use ? e.Guest : null, record: record,
                               name:e.Guest + "|" + cell.Cid + "|" + cell.Party + "|" + cell.Context + "|" + (use ? 1 : 0));
            Obj recipe;
            if (e.Girl != null)
                // unique-battery: the girl in the place of the role, without and with her unique skill; another member who is the same girl is
                // left out of the party (the same party on both sides)
                recipe = new Obj
                {
                    { "place", "replace_role" }, { "items", "first_kept" }, { "name_not", e.Girl },
                    { "tested", Jb.L(new Obj { { "role", e.Role }, { "character", e.Girl }, { "no_unique", !use },
                                               { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true } }) },
                };
            else
                recipe = new Obj
                {
                    { "place", "replace_role" }, { "items", "first_kept" },
                    { "tested", Jb.L(new Obj { { "role", e.Role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true },
                                               { "extra_skills", new Obj { { e.Skill.Id.ToString(), (long)(use ? levels : 0) } } },
                                               { "pieces", e.Weapon == null ? new Obj() : new Obj { { "Weapon", e.Weapon } } } }) },
                };
            // the pep a girl's unique skill reads (section unique_skills of measure_config.json), as measures/UNIQUE_SKILLS.md plays her
            var pep = c.In("unique_skills").O("pep");
            if (e.Girl != null && pep.Has(e.Girl)) ((Obj)recipe.A("tested")[0]).Set("pep", pep.Get(e.Girl));
            string setupName = use && e.Rule.HasValue ? SetupWithRule(c, e.Role, e.Rule.Value.cond, e.Rule.Value.act, cell.Chain) : null;
            return Jb.Make(c, side, cell.Cid, roles: roles, runs: runs, recipe: recipe, enemies: enemies, setupName: setupName, options: options,
                           name: (e.Label ?? e.Skill.Name) + "|" + e.Girl + "|" + e.Role + "|" + e.Stage + "|" + cell.Cid + "|" + cell.Party + "|" + cell.Context + "|" + (use ? 1 : 0));
        }

        /// <summary>The cells played in batches and judged at once; the runs are let go, only the figures stay.</summary>
        static readonly Dictionary<string, string> setups = new Dictionary<string, string>();
        static string side = "variant";     // the side the jobs play: the variant, or a copy of it with trial changes to skills

        /// <summary>"Power Charge:e191*1.2;Accelerator:turns+1;Shadow Clone:tp*0.8;Prism Dawn:speed*1.2": a copy of the variant with the values
        /// of skills changed (e&lt;id&gt; scales the values of an effect, an int stays an int; tp scales the TP cost; turns adds to the turns; speed
        /// scales the speed factors; cast the chant speed factors), to try a value before building it.</summary>
        public static GameData WithTrial(GameData data, string text)
        {
            var changes = new Dictionary<string, Skill>();
            var growth = new List<(string cls, int stat, double factor)>();
            var npcs = new List<(string name, string stat, double factor)>();
            string[] statNames = { "atk", "def", "int", "res", "dex", "agi", "hp", "tp" };
            foreach (var part in text.Split(';').Select(x => x.Trim()).Where(x => x.Length > 0))
            {
                // class:Witch:int*0.9 scales a stat of the growth of a class at every level (every row of the class)
                if (part.StartsWith("class:"))
                {
                    var bits = part.Substring(6).Split(':');
                    var scale = bits[1].Split('*');
                    int stat = Array.IndexOf(statNames, scale[0].Trim());
                    if (bits.Length != 2 || scale.Length != 2 || stat < 0) throw new InvalidOperationException("trial change '" + part + "': write it as class:Witch:int*0.9");
                    growth.Add((bits[0].Trim(), stat, double.Parse(scale[1].Trim(), System.Globalization.CultureInfo.InvariantCulture)));
                    continue;
                }
                // npc:Natalia:res*1.2 scales a stat (or hp) of every stage of a mercenary
                if (part.StartsWith("npc:"))
                {
                    var bits = part.Substring(4).Split(':');
                    var scale = bits.Length == 2 ? bits[1].Split('*') : new string[0];
                    if (bits.Length != 2 || scale.Length != 2 || Array.IndexOf(statNames, scale[0].Trim()) < 0 || scale[0].Trim() == "tp")
                        throw new InvalidOperationException("trial change '" + part + "': write it as npc:Natalia:res*1.2");
                    npcs.Add((bits[0].Trim(), scale[0].Trim(), double.Parse(scale[1].Trim(), System.Globalization.CultureInfo.InvariantCulture)));
                    continue;
                }
                int colon = part.LastIndexOf(':');
                if (colon <= 0) throw new InvalidOperationException("trial change '" + part + "': write it as Skill name:e26*1.2");
                string name = part.Substring(0, colon).Trim(), op = part.Substring(colon + 1).Trim();
                var skill = changes.TryGetValue(name, out var done) ? done : Kit.SkillNamed(data, name);
                char sign = op.Contains('*') ? '*' : '+';
                var halves = op.Split(sign);
                string what = halves[0].Trim();
                double by = double.Parse(halves[1].Trim(), System.Globalization.CultureInfo.InvariantCulture);
                double F(double v) => sign == '*' ? v * by : v + by;
                var copy = skill.Copy();
                if (what.StartsWith("e"))
                {
                    // e26@6-10: only those levels (1-based) of the effect
                    int lo = 1, hi = int.MaxValue;
                    string id = what.Substring(1);
                    if (id.Contains('@'))
                    {
                        var range = id.Substring(id.IndexOf('@') + 1).Split('-');
                        lo = int.Parse(range[0]); hi = range.Length > 1 ? int.Parse(range[1]) : lo;
                        id = id.Substring(0, id.IndexOf('@'));
                    }
                    int effect = int.Parse(id);
                    copy = Kit.WithEffect(skill, effect, Kit.Values(skill, effect).Select((v, i) => i + 1 < lo || i + 1 > hi ? v
                        : v.Int ? Num.Whole((long)Math.Round(F(v.V))) : Num.Float(Math.Round(F(v.V), 4))).ToList());
                }
                else if (what == "tp") copy.Tp = skill.Tp.Select(v => (int)Math.Round(F(v))).ToArray();
                else if (what == "turns") copy.Turns = skill.Turns.Select(v => F(v)).ToArray();
                else if (what == "speed") copy.Speed = skill.Speed.Select(v => Math.Round(F(v), 4)).ToArray();
                else if (what == "cast") copy = Kit.WithCast(skill, skill.Cast.Select(v => Math.Round(F(v), 4)).ToArray());
                else throw new InvalidOperationException("trial change '" + part + "': e<id>, tp, turns, speed or cast");
                changes[name] = copy;
            }
            var result = Kit.WithSkills(data, changes.Select(kv => (Kit.SkillNamed(data, kv.Key), kv.Value)));
            if (npcs.Count > 0)
            {
                if (ReferenceEquals(result, data)) result = data.ShallowCopy();
                result.Npcs = data.Npcs.Select(r =>
                {
                    var mine = npcs.Where(x => x.name == r.Name).ToList();
                    if (mine.Count == 0) return r;
                    var copy = r.Clone();
                    foreach (var (_, stat, factor) in mine)
                    {
                        if (stat == "hp") throw new InvalidOperationException("a guest ally has no HP (0xAC of NPCData is the gold of the hire)");
                        else { int k = Array.IndexOf(statNames, stat); copy.Stats[k] = (int)Math.Round(copy.Stats[k] * factor); }
                    }
                    return copy;
                }).ToList();
            }
            if (growth.Count > 0)
            {
                if (ReferenceEquals(result, data)) result = data.ShallowCopy();
                result.Growth = new Dictionary<int, int[][]>(data.Growth);
                foreach (var (cls, stat, factor) in growth)
                {
                    int id = data.ClassNames.First(kv => kv.Value == cls).Key;
                    var g = data.GrowthRow[id];
                    var rows = new List<int> { g.row, g.dflt };
                    if (g.byPrevious != null) rows.AddRange(g.byPrevious.Select(x => x.row));
                    foreach (int row in rows.Where(r => r >= 0 && result.Growth.ContainsKey(r)).Distinct())
                        result.Growth[row] = result.Growth[row].Select(lv => lv.Select((v, k) => k == stat ? (int)Math.Round(v * factor) : v).ToArray()).ToArray();
                }
            }
            return result;
        }

        /// <summary>The sheet Policies with the rule of a skill, as a setup of its own that every job with the same rule shares (one scenario for
        /// all of them; a job that carries its rows builds a scenario of its own).</summary>
        static string SetupWithRule(Ctx c, string role, string cond, string act, int chain)
        {
            string key = role + "|" + cond + "|" + act + "|" + (chain > 0);
            if (setups.TryGetValue(key, out var name)) return name;
            // a role whose own rows already use the action keeps them (an added row before her statuses would undo her order)
            if (c.Setup.Policies.Any(r => r.Str("Role") == role && r.Str("Action") == act)) { setups[key] = null; return null; }
            var rows = SkillValue.RowsWithRule(c, role, cond, act, chain, true).Select(o =>
            {
                using (var doc = System.Text.Json.JsonDocument.Parse(PyJson.Dump(o))) return Snapshot.ToRow(doc.RootElement.Clone());
            }).ToList();
            name = c.AddSetup(c.Setup.WithPolicies(rows));
            setups[key] = name;
            return name;
        }

        static void Play(Ctx c, List<Cell> cells, int runs, int batch, Obj cfg)
        {
            for (int start = 0; start < cells.Count; start += batch)
            {
                var part = cells.Skip(start).Take(batch).ToList();
                var jobs = new List<JobSpec>();
                foreach (var cell in part) { jobs.Add(Job(c, cell, false, runs)); jobs.Add(Job(c, cell, true, runs)); }
                var done = c.Run(jobs);
                for (int k = 0; k < part.Count; k++)
                {
                    part[k].Without = done[2 * k]; part[k].With = done[2 * k + 1];
                    Judge(part[k], cfg);
                    part[k].Without = null; part[k].With = null;
                }
                done.Clear(); jobs.Clear();
                c.Say("skill-battery: " + Math.Min(start + batch, cells.Count) + " of " + cells.Count + " cells at " + runs + " runs");
            }
        }

        public static void Run(Ctx c, string[] args)
        {
            var cfg = c.In("skill_battery");
            var data = c.Data("variant");
            var sc = c.Sc("variant");
            // arguments: skill names (comma separated, or * for every skill), runs of the scan, runs of the confirmation, and "variants": every
            // active is played under each condition of rule_variants (a damage skill forced by skill:Name), and the best cell of all reads
            var only = args.Length > 0 && args[0] != "*" ? new HashSet<string>(args[0].Split(',').Select(x => x.Trim())) : null;
            int scanRuns = args.Length > 1 ? int.Parse(args[1]) : (int)Py.Num(cfg.Get("scan_runs"));
            int confirmRuns = args.Length > 2 ? int.Parse(args[2]) : (int)Py.Num(cfg.Get("confirm_runs"));
            bool variants = args.Length > 3 && args[3] == "variants";
            string trial = args.Length > 4 ? args[4] : "";
            side = "variant";
            if (trial.Length > 0) side = c.AddSide(WithTrial(c.Data("variant"), trial));
            var conditions = variants ? cfg.A("rule_variants").Select(x => (string)x).ToList() : null;
            var categories = new HashSet<string>(cfg.A("categories").Select(x => (string)x));
            var outEffects = new HashSet<int>(cfg.A("out_of_fight_effects").Select(x => (int)Py.Num(x)));
            var nonDamage = new HashSet<int>(SkillValue.Candidates(c, data).Select(s => s.Id));
            var levels = sc.ReferenceLevels();
            var story = c.Setup.Checkpoints.Select(r => r.Str("ID")).Where(id => id.StartsWith((string)cfg.Get("story_prefix")) && levels.ContainsKey(id)).ToList();
            var stages = cfg.A("stages").Cast<Obj>().ToList();
            var cidsOf = stages.ToDictionary(s => s.S("name"), s => story.Where(id => StageOf(cfg, levels[id].level)?.S("name") == s.S("name")).ToList());

            var entries = new List<Entry>();
            var outOfFight = new List<Skill>();
            var noRole = new List<Skill>();
            foreach (var skill in data.SkillList.OrderBy(s => s.Id))
            {
                if (!categories.Contains(skill.Category) || skill.Classes.Length == 0) continue;
                if (only != null && !only.Contains(skill.Name)) continue;
                if (!skill.IsPassive && !Policy.UsableInBattle(skill)) { outOfFight.Add(skill); continue; }
                if (skill.IsPassive && skill.Effects.Length > 0 && skill.Effects.All(x => outEffects.Contains(x.Id))) { outOfFight.Add(skill); continue; }
                var names = new HashSet<string>(skill.Classes.Select(data.ClassName).Where(n => n != null));
                bool any = false;
                foreach (var st in stages)
                {
                    if (cidsOf[st.S("name")].Count == 0) continue;
                    var columns = st.A("columns").Select(x => (string)x).ToList();
                    string own = columns[columns.Count - 1];
                    // one role for each class that learns it: the first of RoleOrder whose class of the stage it is, else the first whose path holds it
                    var roles = new List<string>();
                    foreach (var cls in skill.Classes.Select(data.ClassName).Where(n => n != null).Distinct())
                    {
                        string r = c.Setup.RoleOrder.FirstOrDefault(x => c.Setup.Roles[x].Str(own) == cls)
                                   ?? c.Setup.RoleOrder.FirstOrDefault(x => columns.Any(col => c.Setup.Roles[x].Str(col) == cls));
                        if (r != null && !roles.Contains(r)) roles.Add(r);
                    }
                    foreach (var role in roles)
                    {
                        any = true;
                        (string cond, string act)? rule = !skill.IsPassive && nonDamage.Contains(skill.Id) ? SkillValue.RuleFor(c, skill) : ((string, string)?)null;
                        if (variants && !skill.IsPassive)
                        {
                            string act = rule.HasValue ? rule.Value.act : "skill:" + skill.Name;
                            foreach (var cond in conditions)
                                entries.Add(new Entry { Skill = skill, Stage = st.S("name"), Role = role, Weapon = WeaponFor(c, data, cfg, skill, role), Rule = (cond, act) });
                        }
                        else entries.Add(new Entry { Skill = skill, Stage = st.S("name"), Role = role, Weapon = WeaponFor(c, data, cfg, skill, role), Rule = rule });
                    }
                }
                if (!any) noRole.Add(skill);
            }

            int chain = (int)Py.Num(cfg.Get("chain"));
            var cells = new List<Cell>();
            foreach (var e in entries)
                foreach (var cid in cidsOf[e.Stage])
                    foreach (var b in c.Setup.Battery)
                    {
                        cells.Add(new Cell { Entry = e, Cid = cid, Party = b.name, Context = "boss", Chain = 0 });
                        int level = levels[cid].level;
                        bool zones = sc.WalkedZones(c.Checkpoint(cid).Str("Floor"), level).Count > 0;
                        if (chain > 0 && zones)
                            cells.Add(new Cell { Entry = e, Cid = cid, Party = b.name, Context = "random", Chain = chain });
                        // variants: also a walk of random battles of the floor and then the boss, nothing healed between them
                        if (variants && zones)
                            cells.Add(new Cell { Entry = e, Cid = cid, Party = b.name, Context = "walk_boss", Chain = (int)Py.Num(cfg.Get("walk")) });
                    }
            int batch = (int)Py.Num(cfg.Get("batch"));
            Play(c, cells, scanRuns, batch, cfg);

            // the best cells of each skill, played again at more runs; the best of them is the one the verdict reads
            var bySkill = cells.GroupBy(x => x.Entry.Skill.Id).ToDictionary(g => g.Key, g => g.ToList());
            int keep = (int)Py.Num(cfg.Get("confirm_cells"));
            var confirm = new List<Cell>();
            var again = new Dictionary<int, List<Cell>>();
            foreach (var kv in bySkill)
            {
                var tops = kv.Value.Where(x => !x.Same).OrderByDescending(x => x.Score).Take(keep).ToList();
                if (tops.Count == 0) continue;
                again[kv.Key] = tops.Select(t => new Cell { Entry = t.Entry, Cid = t.Cid, Party = t.Party, Context = t.Context, Chain = t.Chain }).ToList();
                confirm.AddRange(again[kv.Key]);
            }
            Play(c, confirm, confirmRuns, batch, cfg);
            var best = again.ToDictionary(kv => kv.Key, kv => kv.Value.Where(x => !x.Same).OrderByDescending(x => x.Score).FirstOrDefault() ?? kv.Value[0]);

            double good = cfg.D("good_share");
            var rows = new List<object>();
            var lines = new List<string>();
            var counts = new Dictionary<string, int>();
            foreach (var kv in bySkill.OrderBy(k => k.Value[0].Entry.Skill.Name, StringComparer.Ordinal))
            {
                var all = kv.Value;
                var skill = all[0].Entry.Skill;
                int n = all.Count, serves = all.Count(x => x.Serves), hurts = all.Count(x => x.Hurts), same = all.Count(x => x.Same);
                best.TryGetValue(kv.Key, out var top);
                string verdict;
                if (top == null) verdict = "no effect";
                else if (top.Serves) verdict = (double)serves / n >= good ? "good" : "niche";
                else if ((double)hurts / n >= good) verdict = "hurts";
                else verdict = "dead";
                counts[verdict] = counts.GetValueOrDefault(verdict) + 1;
                string stagesPlayed = string.Join(", ", all.Select(x => x.Entry.Stage + " (" + x.Entry.Role + (x.Entry.Weapon != null ? ", " + x.Entry.Weapon : "") + ")").Distinct())
                                      + (variants ? "; rules: " + string.Join(", ", all.Where(x => x.Entry.Rule.HasValue).Select(x => x.Entry.Rule.Value.cond).Distinct()) : "");
                string where = top == null ? "-" : top.Cid + " " + top.Context + ", " + top.Party + " (" + top.Entry.Stage
                               + (top.Entry.Rule.HasValue ? "; " + top.Entry.Rule.Value.cond + " / " + top.Entry.Rule.Value.act : "") + ")";
                string figs = top == null ? "-" : Py.Pct(top.Wins, 0, true) + " / " + Py.Pct(top.Length, 0, true) + " / " + Py.Pct(top.Hp, 0, true);
                lines.Add("| " + skill.Name + " | " + skill.Category + " | " + stagesPlayed + " | " + n + " | " + Py.Pct((double)serves / n, 0) + " | "
                          + Py.Pct((double)hurts / n, 0) + " | " + Py.Pct((double)same / n, 0) + " | " + where + " | " + figs + " | " + verdict + " |");
                rows.Add(new Obj
                {
                    { "skill", skill.Name }, { "id", (long)skill.Id }, { "category", skill.Category }, { "verdict", verdict },
                    { "cells", (long)n }, { "serves", (long)serves }, { "hurts", (long)hurts }, { "same", (long)same },
                    { "best", top == null ? null : new Obj { { "checkpoint", top.Cid }, { "context", top.Context }, { "party", top.Party },
                                                             { "stage", top.Entry.Stage }, { "role", top.Entry.Role }, { "wins", top.Wins },
                                                             { "length", top.Length }, { "hp_left", top.Hp } } },
                    { "scan", Jb.L(all.Select(x => (object)new Obj { { "checkpoint", x.Cid }, { "context", x.Context }, { "party", x.Party },
                                                                     { "stage", x.Entry.Stage }, { "wins", x.Wins }, { "length", x.Length },
                                                                     { "hp_left", x.Hp }, { "same", x.Same } })) },
                });
            }

            string tag = (variants ? "skill_battery_variants" : "skill_battery") + (trial.Length > 0 ? "_trial" : "");
            string dir = c.Path("docs", "generated", tag);
            Directory.CreateDirectory(dir);
            M.ClearFolder(dir);
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(rows), false);
            var order = new[] { "good", "niche", "dead", "hurts", "no effect" };
            var text = new List<string>
            {
                "# Every skill with and without (generated)", "",
                "Generated by `dtcli skill-battery`. Do not edit. Balance variant. Each active and passive skill a class learns, at its top level, on the member of the first role "
                    + "(sheet Roles) whose class path holds a class that learns it, at each stage of section skill_battery of data_tables/measure_config.json; that member stands in "
                    + "each party of the sheet BatteryParties (in the place of the same role, else of the last member), at every story boss of the stage and on rows of "
                    + chain + " random battles of its floor. Without: the same member with the skill at level 0; the same seeds. A non-damage active is used by the rule of "
                    + "dtcli skill-value; damage skills and passives by the policy of the model. Played as: one role for each class that learns the skill, the "
                    + "first whose class of the stage it is, else the first whose path holds it; when her weapon cannot use the skill she takes the piece weapon_of_type names "
                    + "for a type it allows (shown beside the role). A status skill goes before the statuses the role keeps up. Scan: " + scanRuns + " runs a cell; the " + keep + " best cells of each "
                    + "skill again at " + confirmRuns + " runs, and the verdict reads the best of those.", "",
                "A cell serves: wins +" + Py.Pct(cfg.D("wins"), 0) + ", or wins not down that much and won fights " + Py.Pct(cfg.D("length"), 0) + " shorter or HP left +"
                    + Py.Pct(cfg.D("hp"), 0) + " or TP left +" + Py.Pct(cfg.D("tp"), 0) + " or " + Py.F(cfg.D("alive"), 1) + " more members alive at the end. Good: the best cell serves and " + Py.Pct(good, 0) + " or more of the cells serve; niche: the best cell serves, fewer do; dead: "
                    + "the best cell does not serve; hurts: no cell serves and " + Py.Pct(good, 0) + " or more make it worse; no effect: every battle the same with and "
                    + "without (the skill does nothing the model plays, or the model never uses it): to read.", "",
                "**" + bySkill.Count + " skills played: " + string.Join(", ", order.Select(v => counts.GetValueOrDefault(v) + " " + v)) + ". "
                    + outOfFight.Count + " out of the fight, " + noRole.Count + " with no role that plays their class. " + cells.Count + " cells.**", "",
                "| Skill | Kind | Played as | Cells | Serve | Hurt | Same | Best cell | Best: wins / length / HP left | Verdict |",
                "|---|---|---|---|---|---|---|---|---|---|",
            };
            text.AddRange(lines);
            if (outOfFight.Count > 0) text.AddRange(new[] { "", "Out of the fight (actives not usable in battle; passives whose every effect is in out_of_fight_effects): "
                                                            + string.Join(", ", outOfFight.Select(s => s.Name)) + "." });
            if (noRole.Count > 0) text.AddRange(new[] { "", "No role plays a class that learns: " + string.Join(", ", noRole.Select(s => s.Name)) + "." });
            if (variants) text.Insert(2, "**Variants:** every active under each condition of rule_variants (" + string.Join(", ", conditions)
                                         + "), a damage skill forced by skill:Name, and a third context, walk_boss: " + Py.Num(cfg.Get("walk"))
                                         + " random battles of the floor and then the boss, nothing healed between them; the verdict reads the best cell of all of them.");
            if (variants) text.Insert(3, "");
            if (trial.Length > 0) { text.Insert(2, "**Trial:** the variant with " + trial + " (not built; to try a value)."); text.Insert(3, ""); }
            c.WriteText(c.Path("docs", "generated", tag.ToUpperInvariant() + ".md"), M.Lines(text), false);
            c.Say("skill-battery: " + string.Join(", ", order.Select(v => counts.GetValueOrDefault(v) + " " + v)));
        }

        /// <summary>The suite's pass (measure skill-battery): every skill with and without, then the skills it finds dead, hurting or of no effect
        /// again under the rules of rule_variants and the walk then the boss (docs/generated/SKILL_BATTERY.md and SKILL_BATTERY_VARIANTS.md);
        /// a skill of situational use is read by its best rule.</summary>
        public static void RunWithVariants(Ctx c)
        {
            Run(c, new[] { "*" });
            var rows = (List<object>)c.ReadJson(c.Path("docs", "generated", "skill_battery", "part_1.json"));
            var rest = rows.Cast<Obj>().Where(r => r.S("verdict") == "dead" || r.S("verdict") == "hurts" || r.S("verdict") == "no effect")
                           .Select(r => r.S("skill")).ToList();
            var cfg = c.In("skill_battery");
            if (rest.Count > 0)
                Run(c, new[] { string.Join(",", rest), Py.Str(cfg.Get("scan_runs")), Py.Str(cfg.Get("confirm_runs")), "variants" });
        }

        /// <summary>How a mercenary plays in one cell, read from the recorder of the runs with her and without her: her actions per battle
        /// and those of the summon beside her, her share of the damage of the party side, her healing against the party's max HP, the share of each of her
        /// actions, and the damage per unit of time of the members and of the summon, with her against without her (an action of hers
        /// that undoes or replaces one of the party shows there).</summary>
        sealed class Profile
        {
            public double Actions, SummonActions, DamageShare, HealShare, Members, Summon, Length;
            public List<(string name, double share)> Uses = new List<(string, double)>();
        }

        static Profile ProfileOf(JobResult without, JobResult with, string guest)
        {
            bool IsGuest(Unit u) => u.Kind == Kind.Summon && u.Name == guest;
            bool IsSummon(Unit u) => u.Kind == Kind.Summon && u.Name != guest;
            bool IsMember(Unit u) => u.Side == Unit.PARTY && (u.Kind == Kind.Member || u.Kind == Kind.Doll);
            // per side of the cell: damage per time of the members and of the summon; with her, also her figures
            (double members, double summon, double time, double battles, double guestActs, double summonActs, double guestDmg, double partyDmg,
             double guestHeal, double partyMaxHp, Dictionary<string, double> uses) Sum(JobResult r)
            {
                double m = 0, s = 0, t = 0, b = 0, ga = 0, sa = 0, gd = 0, pd = 0, gh = 0, ph = 0;
                var uses = new Dictionary<string, double>();
                foreach (var run in r.Runs)
                    foreach (var part in run.Parts)
                    {
                        if (part.Record == null) continue;
                        var rec = part.Record;
                        t += part.Time; b += 1; ph += part.PartyMaxHp;
                        for (int i = 0; i < rec.Damage.Count; i++)
                        {
                            var u = rec.Damage.Keys[i].Unit; double v = rec.Damage.Values[i];
                            if (u.Side != Unit.PARTY) continue;
                            pd += v;
                            if (IsGuest(u)) gd += v; else if (IsSummon(u)) s += v; else if (IsMember(u)) m += v;
                        }
                        for (int i = 0; i < rec.Healing.Count; i++)
                        {
                            var u = rec.Healing.Keys[i].Unit; double v = rec.Healing.Values[i];
                            if (u.Side != Unit.PARTY) continue;
                            if (IsGuest(u)) gh += v;
                        }
                        for (int i = 0; i < rec.Actions.Count; i++)
                        {
                            var u = rec.Actions.Keys[i].Unit;
                            if (IsGuest(u)) ga += rec.Actions.Values[i]; else if (IsSummon(u)) sa += rec.Actions.Values[i];
                        }
                        for (int i = 0; i < rec.SkillUses.Count; i++)
                        {
                            var k = rec.SkillUses.Keys[i];
                            if (IsGuest(k.Unit)) uses[k.Name ?? "?"] = uses.GetValueOrDefault(k.Name ?? "?") + rec.SkillUses.Values[i];
                        }
                    }
                return (m, s, t, b, ga, sa, gd, pd, gh, ph, uses);
            }
            var a = Sum(without); var w = Sum(with);
            double Rate(double x, double t) => t > 0 ? x / t : 0;
            double Change(double x, double y) => x > 0 ? y / x - 1 : 0;
            var p = new Profile
            {
                Actions = w.battles > 0 ? w.guestActs / w.battles : 0,
                SummonActions = w.battles > 0 ? w.summonActs / w.battles : 0,
                DamageShare = w.partyDmg > 0 ? w.guestDmg / w.partyDmg : 0,
                HealShare = w.partyMaxHp > 0 ? w.guestHeal / w.partyMaxHp : 0,
                Members = Change(Rate(a.members, a.time), Rate(w.members, w.time)),
                Summon = Change(Rate(a.summon, a.time), Rate(w.summon, w.time)),
                Length = a.time > 0 && a.battles > 0 && w.battles > 0 ? 1 - (w.time / w.battles) / (a.time / a.battles) : 0,
            };
            double total = w.uses.Values.Sum();
            if (total > 0) p.Uses = w.uses.OrderByDescending(kv => kv.Value).Select(kv => (kv.Key, kv.Value / total)).ToList();
            return p;
        }

        /// <summary>dtcli mercenary-battery [scan runs] [confirm runs] [names|*] [trial]: each mercenary hired beside the summon of the grand
        /// sealbook, at the stage the bar offers at that point of the story (sheet MercenaryUnlocks), against the party as built, in the
        /// reference party and each party of BatteryParties, at every checkpoint of the difficulty curve where the bar offers her, and on
        /// rows of random battles of its floor; the same seeds, thresholds and verdicts as skill-battery; docs/generated/MERCENARY_BATTERY.md.</summary>
        public static void RunMercenaries(Ctx c, string[] args)
        {
            var cfg = c.In("skill_battery");
            var data = c.Data("variant");
            var sc = c.Sc("variant");
            int scanRuns = args.Length > 0 ? int.Parse(args[0]) : (int)Py.Num(cfg.Get(cfg.Has("mercenary_scan_runs") ? "mercenary_scan_runs" : "scan_runs"));
            int confirmRuns = args.Length > 1 ? int.Parse(args[1]) : (int)Py.Num(cfg.Get(cfg.Has("mercenary_confirm_runs") ? "mercenary_confirm_runs" : "confirm_runs"));
            // [names|*] [trial]: only these mercenaries, on a copy of the variant with the trial values (the report is then _TRIAL)
            var onlyGuests = args.Length > 2 && args[2] != "*" ? new HashSet<string>(args[2].Split(',').Select(x => x.Trim())) : null;
            string trial = args.Length > 3 ? args[3] : "";
            side = "variant";
            if (trial.Length > 0) side = c.AddSide(WithTrial(c.Data("variant"), trial));
            var levels = sc.ReferenceLevels();
            var cids = DifficultyCurve.Checkpoints(c).Where(levels.ContainsKey).ToList();
            var parties = new List<string> { "Reference" };
            parties.AddRange(c.Setup.Battery.Select(b => b.name));
            var guests = data.Npcs.GroupBy(r => r.Name).Select(g => (name: g.Key, first: g.Min(r => r.Level)))
                             .Where(g => onlyGuests == null || onlyGuests.Contains(g.name)).OrderBy(g => g.name, StringComparer.Ordinal).ToList();
            int chain = (int)Py.Num(cfg.Get("chain"));
            var cells = new List<Cell>();
            foreach (var (name, first) in guests)
            {
                var e = new Entry { Guest = name, Label = name, Stage = "", Role = "guest" };
                // only where the bar offers her (sheet MercenaryUnlocks): the stage there is the one the job builds
                foreach (var cid in cids.Where(x => UnitFactory.GuestStageAt(data, c.Setup, name, x) != null))
                    foreach (var party in parties)
                    {
                        cells.Add(new Cell { Entry = e, Cid = cid, Party = party, Context = "boss", Chain = 0 });
                        if (chain > 0 && sc.WalkedZones(c.Checkpoint(cid).Str("Floor"), levels[cid].level).Count > 0)
                            cells.Add(new Cell { Entry = e, Cid = cid, Party = party, Context = "random", Chain = chain });
                    }
            }
            int batch = (int)Py.Num(cfg.Get("batch"));
            Play(c, cells, scanRuns, batch, cfg);
            var byGuest = cells.GroupBy(x => x.Entry.Guest).ToDictionary(g => g.Key, g => g.ToList());
            int keep = (int)Py.Num(cfg.Get("confirm_cells"));
            var again = new Dictionary<string, List<Cell>>();
            foreach (var kv in byGuest)
            {
                var tops = kv.Value.Where(x => !x.Same).OrderByDescending(x => x.Score).Take(keep).ToList();
                if (tops.Count > 0) again[kv.Key] = tops.Select(t => new Cell { Entry = t.Entry, Cid = t.Cid, Party = t.Party, Context = t.Context, Chain = t.Chain }).ToList();
            }
            Play(c, again.Values.SelectMany(x => x).ToList(), confirmRuns, batch, cfg);
            var best = again.ToDictionary(kv => kv.Key, kv => kv.Value.Where(x => !x.Same).OrderByDescending(x => x.Score).FirstOrDefault() ?? kv.Value[0]);

            // how each one plays: the reference party at every boss of the story and the postgame where the bar offers her (not only the
            // checkpoints of the curve, so a mercenary of the late postgame is read on all her fights), with the recorder
            int profileRuns = (int)Py.Num(cfg.Get("mercenary_profile_runs"));
            var profiled = new Dictionary<string, List<(string cid, Profile p)>>();
            var allCids = c.Setup.Checkpoints.Select(r => r.Str("ID")).Where(levels.ContainsKey).ToList();
            var toProfile = new List<Cell>();
            foreach (var (name, _) in guests)
            {
                var e = cells.FirstOrDefault(x => x.Entry.Guest == name)?.Entry;
                if (e == null) continue;            // offered at no checkpoint of the curve: not in the battery
                foreach (var cid in allCids.Where(x => UnitFactory.GuestStageAt(data, c.Setup, name, x) != null))
                    toProfile.Add(new Cell { Entry = e, Cid = cid, Party = "Reference", Context = "boss", Chain = 0 });
            }
            // the recorder keeps every battle of a job until it is read: small batches, each read and let go before the next, keep the
            // memory bounded (one batch of the size of the scan held about a million battle records)
            int profileBatch = (int)Py.Num(cfg.Get("mercenary_profile_batch"));
            for (int start = 0; start < toProfile.Count; start += profileBatch)
            {
                var part = toProfile.Skip(start).Take(profileBatch).ToList();
                var jobs = new List<JobSpec>();
                foreach (var cell in part) { jobs.Add(Job(c, cell, false, profileRuns, true)); jobs.Add(Job(c, cell, true, profileRuns, true)); }
                var done = c.Run(jobs);
                for (int k = 0; k < part.Count; k++)
                {
                    string g = part[k].Entry.Guest;
                    if (!profiled.ContainsKey(g)) profiled[g] = new List<(string, Profile)>();
                    profiled[g].Add((part[k].Cid, ProfileOf(done[2 * k], done[2 * k + 1], g)));
                }
                done.Clear(); jobs.Clear();
                c.Say("mercenary-battery: profile, " + Math.Min(start + profileBatch, toProfile.Count) + " of " + toProfile.Count + " cells at " + profileRuns + " runs");
            }

            double good = cfg.D("good_share");
            var rows = new List<object>();
            var lines = new List<string>();
            var counts = new Dictionary<string, int>();
            foreach (var (name, first) in guests)
            {
                if (!byGuest.TryGetValue(name, out var all)) continue;
                int n = all.Count, serves = all.Count(x => x.Serves), hurts = all.Count(x => x.Hurts), same = all.Count(x => x.Same);
                best.TryGetValue(name, out var top);
                string verdict = top == null ? "no effect" : top.Serves ? ((double)serves / n >= good ? "good" : "niche")
                               : (double)hurts / n >= good ? "hurts" : "dead";
                counts[verdict] = counts.GetValueOrDefault(verdict) + 1;
                string from = all.Select(x => x.Cid).First();
                string where = top == null ? "-" : top.Cid + " " + top.Context + ", " + top.Party;
                string figs = top == null ? "-" : Py.Pct(top.Wins, 0, true) + " / " + Py.Pct(top.Length, 0, true) + " / " + Py.Pct(top.Hp, 0, true);
                double meanWins = all.Average(x => x.Wins);
                lines.Add("| " + name + " | " + first + " | " + from + " | " + n + " | " + Py.Pct((double)serves / n, 0) + " | " + Py.Pct((double)hurts / n, 0) + " | "
                          + Py.Pct((double)same / n, 0) + " | " + Py.Pct(meanWins, 1, true) + " | " + where + " | " + figs + " | " + verdict + " |");
                rows.Add(new Obj
                {
                    { "guest", name }, { "first_level", (long)first }, { "verdict", verdict }, { "cells", (long)n }, { "serves", (long)serves },
                    { "hurts", (long)hurts }, { "same", (long)same }, { "mean_wins", meanWins },
                    { "best", top == null ? null : new Obj { { "checkpoint", top.Cid }, { "context", top.Context }, { "party", top.Party },
                                                             { "wins", top.Wins }, { "length", top.Length }, { "hp_left", top.Hp } } },
                    { "scan", Jb.L(all.Select(x => (object)new Obj { { "checkpoint", x.Cid }, { "context", x.Context }, { "party", x.Party },
                                                                     { "wins", x.Wins }, { "length", x.Length }, { "hp_left", x.Hp }, { "same", x.Same } })) },
                });
            }
            string tag = trial.Length > 0 || onlyGuests != null ? "mercenary_battery_trial" : "mercenary_battery";
            string dir = c.Path("docs", "generated", tag);
            Directory.CreateDirectory(dir);
            M.ClearFolder(dir);
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(rows), false);
            var order = new[] { "good", "niche", "dead", "hurts", "no effect" };
            var text = new List<string>
            {
                "# Every mercenary, hired or not (generated)", "",
                "Generated by `dtcli mercenary-battery`. Do not edit. Balance variant. Each mercenary hired beside the summon of the party's "
                    + "grand sealbook (the program builds both, units 3000 and 3001), at the stage the bar offers at that point of the story (sheet "
                    + "MercenaryUnlocks: of the stages whose flag is open, the one of the highest level), against the party as built: the reference "
                    + "party of the checkpoint and each party of the sheet BatteryParties, at every checkpoint of the difficulty curve where the bar offers her, "
                    + "and on rows of " + chain + " random battles of its floor; the same seeds. Scan: " + scanRuns + " runs a cell; the " + keep
                    + " best cells of each mercenary again at " + confirmRuns + " runs, and the verdict reads the best of those. Thresholds and verdicts "
                    + "as SKILL_BATTERY.md. Mean wins: the change of the share of wins over every cell.", "",
                "**" + rows.Count + " mercenaries played: " + string.Join(", ", order.Select(v => counts.GetValueOrDefault(v) + " " + v)) + ". " + cells.Count + " cells.**", "",
                "| Mercenary | First stage | From | Cells | Serve | Hurt | Same | Mean wins | Best cell | Best: wins / length / HP left | Verdict |",
                "|---|---|---|---|---|---|---|---|---|---|---|",
            };
            text.AddRange(lines);

            // how each one plays (the recorder), the mean of her cells
            text.Add("");
            text.Add("## How each one plays");
            text.Add("");
            text.Add("The reference party at every boss of the story and the postgame where the bar offers her (not only those of the curve), " + profileRuns + " runs a cell with the recorder, with her and without her; "
                     + "the mean of her cells. Actions: hers per battle, and those of the summon beside her. Damage: her share of the damage of the "
                     + "party side. Healing: hers in a battle against the party's max HP. Members and summon: their damage per unit of time with her against without her. Her actions: the share of each.");
            text.Add("");
            text.Add("| Mercenary | Cells | Actions | Summon's | Damage | Healing | Members | Summon | Fights shorter | Her actions |");
            text.Add("|---|---|---|---|---|---|---|---|---|---|");
            foreach (var (name, _) in guests)
            {
                if (!profiled.TryGetValue(name, out var list) || list.Count == 0) continue;
                double Mean(Func<Profile, double> f) => list.Average(x => f(x.p));
                var uses = new Dictionary<string, double>();
                foreach (var (_, p) in list) foreach (var (n, s) in p.Uses) uses[n] = uses.GetValueOrDefault(n) + s / list.Count;
                string acts = string.Join(", ", uses.OrderByDescending(kv => kv.Value).Take(5).Select(kv => kv.Key + " " + Py.Pct(kv.Value, 0)));
                text.Add("| " + name + " | " + list.Count + " | " + Py.F(Mean(p => p.Actions), 1) + " | " + Py.F(Mean(p => p.SummonActions), 1) + " | "
                         + Py.Pct(Mean(p => p.DamageShare), 0) + " | " + Py.Pct(Mean(p => p.HealShare), 0) + " | " + Py.Pct(Mean(p => p.Members), 0, true) + " | "
                         + Py.Pct(Mean(p => p.Summon), 0, true) + " | " + Py.Pct(Mean(p => p.Length), 0, true) + " | " + acts + " |");
                var row = (Obj)rows.First(r => ((Obj)r).S("guest") == name);
                row.Set("profile", Jb.L(list.Select(x => (object)new Obj
                {
                    { "checkpoint", x.cid }, { "actions", x.p.Actions }, { "summon_actions", x.p.SummonActions }, { "damage_share", x.p.DamageShare },
                    { "heal_share", x.p.HealShare }, { "members", x.p.Members }, { "summon", x.p.Summon }, { "length", x.p.Length },
                    { "uses", Jb.L(x.p.Uses.Select(u => (object)Jb.L(new object[] { u.name, u.share }))) },
                })));
            }

            // who the bar offers at each checkpoint, and what each one adds there (every party, bosses and random battles of the scan)
            text.Add("");
            text.Add("## At each checkpoint");
            text.Add("");
            text.Add("The mercenaries the bar offers at each checkpoint of the curve, by the mean share by which the won fights are shorter over "
                     + "the cells of the scan there (every party, the boss and the random battles); in brackets, the mean change of the share of wins.");
            text.Add("");
            text.Add("| Checkpoint | Mercenaries, best first |");
            text.Add("|---|---|");
            foreach (var cid in cids)
            {
                var here = cells.Where(x => x.Cid == cid).GroupBy(x => x.Entry.Guest)
                                .Select(g => (name: g.Key, length: g.Average(x => x.Length), wins: g.Average(x => x.Wins))).OrderByDescending(x => x.length).ToList();
                if (here.Count == 0) continue;
                text.Add("| " + cid + " | " + string.Join(", ", here.Select(x => x.name + " " + Py.Pct(x.length, 0, true) + " (" + Py.Pct(x.wins, 0, true) + ")")) + " |");
            }
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(rows), false);
            if (trial.Length > 0) { text.Insert(2, "**Trial:** the variant with " + trial + " (not built; to try a value)."); text.Insert(3, ""); }
            c.WriteText(c.Path("docs", "generated", tag.ToUpperInvariant() + ".md"), M.Lines(text), false);
            c.Say("mercenary-battery: " + string.Join(", ", order.Select(v => counts.GetValueOrDefault(v) + " " + v)));
        }

        /// <summary>dtcli unique-battery [scan runs] [confirm runs]: the unique skill of each girl, with and without, as skill-battery plays a
        /// skill: the girl in each role of the sheet Roles that names her (column Characters), in each party of BatteryParties (in the place of
        /// that role, else of the last member), at every story boss from the chapter she joins in, at each stage of section skill_battery, and
        /// on rows of random battles of its floor; the same seeds, thresholds and verdicts; docs/generated/UNIQUE_BATTERY.md.</summary>
        public static void RunUnique(Ctx c, string[] args)
        {
            var cfg = c.In("skill_battery");
            var data = c.Data("variant");
            var sc = c.Sc("variant");
            int scanRuns = args.Length > 0 ? int.Parse(args[0]) : (int)Py.Num(cfg.Get("scan_runs"));
            int confirmRuns = args.Length > 1 ? int.Parse(args[1]) : (int)Py.Num(cfg.Get("confirm_runs"));
            side = "variant";
            var names = c.In("unique_skills").O("skills");
            var levels = sc.ReferenceLevels();
            var story = c.Setup.Checkpoints.Select(r => r.Str("ID")).Where(id => id.StartsWith((string)cfg.Get("story_prefix")) && levels.ContainsKey(id)).ToList();
            var stages = cfg.A("stages").Cast<Obj>().ToList();
            var cidsOf = stages.ToDictionary(s => s.S("name"), s => story.Where(id => StageOf(cfg, levels[id].level)?.S("name") == s.S("name")).ToList());
            var entries = new List<Entry>();
            var joinedAt = new Dictionary<(string girl, string cid), bool>();
            foreach (var girl in data.Characters.Where(x => x.UniqueSkill != T.NONE).OrderBy(x => x.Name, StringComparer.Ordinal))
            {
                string label = Py.Str(names.O(girl.UniqueSkill.ToString()).Get("name"));
                var roles = c.Setup.RoleOrder.Where(r => (c.Setup.Roles[r].Str("Characters (order of preference)") ?? "").Split(';').Select(n => n.Trim()).Contains(girl.Name)).ToList();
                foreach (var st in stages)
                    foreach (var role in roles)
                        entries.Add(new Entry { Girl = girl.Name, Label = label, Stage = st.S("name"), Role = role });
                foreach (var cid in story) joinedAt[(girl.Name, cid)] = sc.Available(c.Checkpoint(cid).Str("Chapter")).Contains(girl.Name);
            }
            int chain = (int)Py.Num(cfg.Get("chain"));
            var cells = new List<Cell>();
            foreach (var e in entries)
                foreach (var cid in cidsOf[e.Stage].Where(x => joinedAt[(e.Girl, x)]))
                    foreach (var b in c.Setup.Battery)
                    {
                        cells.Add(new Cell { Entry = e, Cid = cid, Party = b.name, Context = "boss", Chain = 0 });
                        if (chain > 0 && sc.WalkedZones(c.Checkpoint(cid).Str("Floor"), levels[cid].level).Count > 0)
                            cells.Add(new Cell { Entry = e, Cid = cid, Party = b.name, Context = "random", Chain = chain });
                    }
            int batch = (int)Py.Num(cfg.Get("batch"));
            Play(c, cells, scanRuns, batch, cfg);
            var byGirl = cells.GroupBy(x => x.Entry.Girl).ToDictionary(g => g.Key, g => g.ToList());
            int keep = (int)Py.Num(cfg.Get("confirm_cells"));
            var again = new Dictionary<string, List<Cell>>();
            foreach (var kv in byGirl)
            {
                var tops = kv.Value.Where(x => !x.Same).OrderByDescending(x => x.Score).Take(keep).ToList();
                if (tops.Count > 0) again[kv.Key] = tops.Select(t => new Cell { Entry = t.Entry, Cid = t.Cid, Party = t.Party, Context = t.Context, Chain = t.Chain }).ToList();
            }
            Play(c, again.Values.SelectMany(x => x).ToList(), confirmRuns, batch, cfg);
            var best = again.ToDictionary(kv => kv.Key, kv => kv.Value.Where(x => !x.Same).OrderByDescending(x => x.Score).FirstOrDefault() ?? kv.Value[0]);

            double good = cfg.D("good_share");
            var rows = new List<object>();
            var lines = new List<string>();
            var counts = new Dictionary<string, int>();
            foreach (var kv in byGirl.OrderBy(k => k.Key, StringComparer.Ordinal))
            {
                var all = kv.Value;
                int n = all.Count, serves = all.Count(x => x.Serves), hurts = all.Count(x => x.Hurts), same = all.Count(x => x.Same);
                best.TryGetValue(kv.Key, out var top);
                string verdict = top == null ? "no effect" : top.Serves ? ((double)serves / n >= good ? "good" : "niche")
                               : (double)hurts / n >= good ? "hurts" : "dead";
                counts[verdict] = counts.GetValueOrDefault(verdict) + 1;
                // by stage: the share of cells where it serves and where it hurts
                string byStage = string.Join(", ", stages.Select(st => st.S("name")).Where(sn => all.Any(x => x.Entry.Stage == sn)).Select(sn =>
                {
                    var part = all.Where(x => x.Entry.Stage == sn).ToList();
                    return sn + " " + Py.Pct((double)part.Count(x => x.Serves) / part.Count, 0) + " / " + Py.Pct((double)part.Count(x => x.Hurts) / part.Count, 0);
                }));
                string rolesPlayed = string.Join(", ", all.Select(x => x.Entry.Role).Distinct());
                string where = top == null ? "-" : top.Cid + " " + top.Context + ", " + top.Party + " (" + top.Entry.Role + ")";
                string figs = top == null ? "-" : Py.Pct(top.Wins, 0, true) + " / " + Py.Pct(top.Length, 0, true) + " / " + Py.Pct(top.Hp, 0, true);
                lines.Add("| " + kv.Key + " | " + all[0].Entry.Label + " | " + rolesPlayed + " | " + n + " | " + Py.Pct((double)serves / n, 0) + " | "
                          + Py.Pct((double)hurts / n, 0) + " | " + Py.Pct((double)same / n, 0) + " | " + byStage + " | " + where + " | " + figs + " | " + verdict + " |");
                rows.Add(new Obj
                {
                    { "girl", kv.Key }, { "skill", all[0].Entry.Label }, { "verdict", verdict }, { "cells", (long)n }, { "serves", (long)serves },
                    { "hurts", (long)hurts }, { "same", (long)same },
                    { "best", top == null ? null : new Obj { { "checkpoint", top.Cid }, { "context", top.Context }, { "party", top.Party }, { "role", top.Entry.Role },
                                                             { "wins", top.Wins }, { "length", top.Length }, { "hp_left", top.Hp } } },
                    { "scan", Jb.L(all.Select(x => (object)new Obj { { "checkpoint", x.Cid }, { "context", x.Context }, { "party", x.Party }, { "role", x.Entry.Role },
                                                                     { "stage", x.Entry.Stage }, { "wins", x.Wins }, { "length", x.Length },
                                                                     { "hp_left", x.Hp }, { "same", x.Same } })) },
                });
            }
            string dir = c.Path("docs", "generated", "unique_battery");
            Directory.CreateDirectory(dir);
            M.ClearFolder(dir);
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(rows), false);
            var order = new[] { "good", "niche", "dead", "hurts", "no effect" };
            var text = new List<string>
            {
                "# Every unique skill with and without (generated)", "",
                "Generated by `dtcli unique-battery`. Do not edit. Balance variant. The unique skill of each girl, as `dtcli skill-battery` plays a skill: the girl "
                    + "in each role of the sheet Roles that names her (column Characters), in each party of the sheet BatteryParties (in the place of that role, else "
                    + "of the last member; another member who is the same girl is left out), at every story boss of each stage of section skill_battery of "
                    + "data_tables/measure_config.json from the chapter she joins in, and on rows of " + chain + " random battles of its floor. Without: the same girl "
                    + "without her unique skill; the same seeds. Scan: " + scanRuns + " runs a cell; the " + keep + " best cells of each girl again at " + confirmRuns
                    + " runs, and the verdict reads the best of those. Thresholds and verdicts as SKILL_BATTERY.md. By stage: the share of the cells where it serves "
                    + "/ where it hurts.", "",
                "**" + byGirl.Count + " unique skills played: " + string.Join(", ", order.Select(v => counts.GetValueOrDefault(v) + " " + v)) + ". " + cells.Count + " cells.**", "",
                "| Girl | Unique skill | Roles | Cells | Serve | Hurt | Same | By stage | Best cell | Best: wins / length / HP left | Verdict |",
                "|---|---|---|---|---|---|---|---|---|---|---|",
            };
            text.AddRange(lines);
            c.WriteText(c.Path("docs", "generated", "UNIQUE_BATTERY.md"), M.Lines(text), false);
            c.Say("unique-battery: " + string.Join(", ", order.Select(v => counts.GetValueOrDefault(v) + " " + v)));
        }
    }
}
