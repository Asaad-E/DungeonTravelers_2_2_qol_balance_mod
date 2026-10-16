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

        static JobSpec Job(Ctx c, Cell cell, bool use, int runs)
        {
            var e = cell.Entry;
            var sc = c.Sc("variant");
            var cp = c.Checkpoint(cell.Cid);
            int levels = e.Skill.Levels != 0 ? e.Skill.Levels : 1;
            var roles = c.Setup.Battery.First(b => b.name == cell.Party).roles;
            Obj enemies = null;
            Obj options = null;
            if (cell.Chain > 0)
            {
                int level = sc.ReferenceLevels()[cell.Cid].level;
                enemies = Jb.Chain(sc.WalkedZones(cp.Str("Floor"), level).Select(z => z.Name), (long)Py.Num(c.In("skill_battery").Get("chain_seed")), cell.Chain);
                if (cell.Context == "walk_boss") { enemies.Set("then_checkpoint", true); options = new Obj { { "random_battle", true } }; }
            }
            var recipe = new Obj
            {
                { "place", "replace_role" }, { "items", "first_kept" },
                { "tested", Jb.L(new Obj { { "role", e.Role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true },
                                           { "extra_skills", new Obj { { e.Skill.Id.ToString(), (long)(use ? levels : 0) } } },
                                           { "pieces", e.Weapon == null ? new Obj() : new Obj { { "Weapon", e.Weapon } } } }) },
            };
            string setupName = use && e.Rule.HasValue ? SetupWithRule(c, e.Role, e.Rule.Value.cond, e.Rule.Value.act, cell.Chain) : null;
            return Jb.Make(c, "variant", cell.Cid, roles: roles, runs: runs, recipe: recipe, enemies: enemies, setupName: setupName, options: options,
                           name: e.Skill.Name + "|" + e.Stage + "|" + cell.Cid + "|" + cell.Party + "|" + cell.Context + "|" + (use ? 1 : 0));
        }

        /// <summary>The cells played in batches and judged at once; the runs are let go, only the figures stay.</summary>
        static readonly Dictionary<string, string> setups = new Dictionary<string, string>();

        /// <summary>The sheet Policies with the rule of a skill, as a setup of its own that every job with the same rule shares (one scenario for
        /// all of them; a job that carries its rows builds a scenario of its own).</summary>
        static string SetupWithRule(Ctx c, string role, string cond, string act, int chain)
        {
            string key = role + "|" + cond + "|" + act + "|" + (chain > 0);
            if (setups.TryGetValue(key, out var name)) return name;
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

            string tag = variants ? "skill_battery_variants" : "skill_battery";
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
                    + "tools/skill_value.py; damage skills and passives by the policy of the model. Played as: one role for each class that learns the skill, the "
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
            c.WriteText(c.Path("docs", "generated", tag.ToUpperInvariant() + ".md"), M.Lines(text), false);
            c.Say("skill-battery: " + string.Join(", ", order.Select(v => counts.GetValueOrDefault(v) + " " + v)));
        }
    }
}
