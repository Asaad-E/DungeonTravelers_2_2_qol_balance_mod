using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>tools/skill_value.py: what each skill that deals no damage adds to a fight (docs/generated/SKILL_VALUE.md) and what each hostile skill adds
    /// (docs/generated/SKILL_AILMENTS.md).</summary>
    public static class SkillValue
    {

        public static bool IsAilment(int effect) => Array.IndexOf(Battle.AILMENT_IDS, effect) >= 0;

        /// <summary>(condition, action) of the rule that makes a member use the skill where it serves.</summary>
        public static (string cond, string act) RuleFor(Ctx c, Skill skill)
        {
            var effects = skill.Effects;
            // the rules of measure_config.json (skill_value, rules), in order: the first whose effects the skill has
            foreach (var r in c.In("skill_value").A("rules"))
            {
                var rule = (Obj)r;
                var ids = new HashSet<int>(rule.A("effects").Select(x => (int)Py.Num(x)));
                if (effects.Any(e => ids.Contains(e.Id))) return (rule.S("condition"), rule.S("action"));
            }
            var ailment = effects.FirstOrDefault(e => IsAilment(e.Id) && e.Kind != 2);
            if (ailment != null) return ("always", "ailment:" + ailment.Id);
            var status = effects.FirstOrDefault(e => (e.Kind == 4 || e.Kind == 5) && !IsAilment(e.Id));
            if (status != null && Policy.Puts(skill, status.Id)) return ("always", "status:" + status.Id);
            return ("always", "skill:" + skill.Name);
        }

        /// <summary>(role, stage row) where the skill is first played, or null.</summary>
        public static (string role, Obj stage)? Place(Ctx c, GameData data, Skill skill)
        {
            var names = new HashSet<string>();
            foreach (int cls in skill.Classes) names.Add(data.ClassName(cls));
            foreach (var st in M.Stages(c))
            {
                string stage = st.S("Stage");
                string col = stage == "base" ? "Base class" : stage == "intermediate" ? "Lv15 class" : "Lv30 class";
                foreach (var role in c.Setup.RoleOrder)
                    if (names.Contains(c.Setup.Roles[role].Str(col))) return (role, st);
            }
            return null;
        }

        public static List<Skill> Candidates(Ctx c, GameData data)
        {
            var attackingEffects = new HashSet<int>(c.In("skill_value").A("attacking").Select(x => (int)Py.Num(x)));
            var found = new List<Skill>();
            foreach (var s in data.SkillList.OrderBy(x => x.Id))
            {
                if (!(s.Category == "Technique" || s.Category == "Magic") || s.Classes.Length == 0 || !Policy.UsableInBattle(s)) continue;
                bool attacking = s.Effects.Any(e => attackingEffects.Contains(e.Id) && (e.Kind == 2 || e.Kind == 4))
                                 || s.Effects.Any(e => Array.IndexOf(Battle.RANDOM_MOVES, e.Id) >= 0);
                if (!attacking) found.Add(s);
            }
            return found;
        }

        public static List<Skill> Hostile(Ctx c, GameData data)
        {
            var found = new List<Skill>();
            foreach (var s in Candidates(c, data))
            {
                bool enemy = s.Target >= T.SINGLE && s.Target <= T.ALL;
                bool ailment = s.Effects.Any(e => IsAilment(e.Id) && e.Kind != 2);
                bool debuff = enemy && s.Effects.Any(e => e.Kind == 5 && e.Values.Min() < 0);
                if (enemy && (ailment || debuff)) found.Add(s);
            }
            return found;
        }

        static object Plus(object order) => order is long l ? (object)(l + 1) : Py.Num(order) + 1;

        /// <summary>The job of the engine that plays one cell: the reference party with the member of the role, with or without the skill and its rule.</summary>
        public static JobSpec Job(Ctx c, string role, string cid, Skill skill, bool use, int chain, int runs, string name = null, string setupName = null, (string cond, string act)? rule = null)
        {
            var cp = c.Checkpoint(cid);
            var sc = c.Sc("variant");
            int level = sc.ReferenceLevels()[cid].level;
            int levels = skill.Levels != 0 ? skill.Levels : 1;
            var extra = new Dictionary<int, int> { { skill.Id, use ? levels : 0 } };
            var zones = sc.WalkedZones(cp.Str("Floor"), level);
            Obj enemies = chain > 0 && zones.Count > 0 ? Jb.Chain(zones.Select(z => z.Name), (int)c.In("skill_value").D("chain_seed"), chain) : null;
            List<object> rows = null;
            if (use)
            {
                var (cond, act) = rule ?? RuleFor(c, skill);
                rows = RowsWithRule(c, role, cond, act, chain);
            }
            var recipe = new Obj
            {
                { "drop_last", true }, { "items", "first_kept" },
                { "tested", Jb.L(new Obj { { "role", role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true },
                                           { "extra_skills", Jb.Dict(extra.Select(kv => new KeyValuePair<string, object>(kv.Key.ToString(), (long)kv.Value))) } }) },
            };
            return Jb.Make(c, "variant", cid, runs: runs, crown: 0, recipe: recipe, enemies: enemies, policyRows: rows, setupName: setupName,
                           name: name ?? (skill.Name + "|" + role + "|" + cid + "|" + (use ? 1 : 0) + "|" + chain));
        }

        /// <summary>The sheet Policies with one rule added for the role: before her first damage row (else after her last row), or with
        /// beforeStatus a status before her first status row; on random rows an ailment goes first, after revives, heals and cures.</summary>
        public static List<object> RowsWithRule(Ctx c, string role, string cond, string act, int chain, bool beforeStatus = false)
        {
            List<object> rows;
            {
                var saved = c.Setup.Policies;
                var mine = saved.Where(r => r.Str("Role") == role).OrderBy(r => Py.Num(r.Get("Order"))).ToList();
                object cut = null;
                foreach (var r in mine) if (r.Str("Action").StartsWith("damage")) { cut = r.Get("Order"); break; }
                // beforeStatus: a status skill goes before the statuses the role keeps up (a performer keeps one dance or song up)
                if (beforeStatus && act.StartsWith("status:"))
                    foreach (var r in mine) if (r.Str("Action").StartsWith("status:")) { cut = r.Get("Order"); break; }
                if (cut == null)
                {
                    object top = 0L;
                    foreach (var r in mine) if (Py.Num(r.Get("Order")) > Py.Num(top) || ReferenceEquals(top, null)) top = r.Get("Order");
                    cut = Plus(top);
                }
                if (chain > 0 && act.StartsWith("ailment:"))
                {
                    var first = mine.FirstOrDefault(r => !(r.Str("Action").StartsWith("revive") || r.Str("Action").StartsWith("heal") || r.Str("Action").StartsWith("cure")));
                    if (first != null) cut = first.Get("Order");
                }
                rows = new List<object>();
                foreach (var r in saved)
                {
                    var o = Jb.RowObj(r);
                    if (r.Str("Role") == role && Py.Num(r.Get("Order")) >= Py.Num(cut)) o.Set("Order", Plus(r.Get("Order")));
                    rows.Add(o);
                }
                rows.Add(new Obj { { "Role", role }, { "Order", cut }, { "Condition", cond }, { "Action", act } });
            }
            return rows;
        }

        public static Obj Figures(JobResult done)
        {
            var res = done.Runs;
            var won = res.Where(r => r.Won).ToList();
            return new Obj
            {
                { "won", (double)won.Count / res.Length }, { "time_won", won.Count > 0 ? (object)(Py.Sum(won.Select(r => r.Time)) / won.Count) : null },
                { "hp_left", Py.Sum(res.Select(r => r.HpLeft)) / res.Length },
            };
        }

        static List<string> StageCheckpoints(Obj st) => ClassStages.Checkpoints(st);

        public static void Run(Ctx c)
        {
            string dir = c.Path("docs", "generated", "skill_value");
            var data = c.Data("variant");
            int runs = c.SetInt("check_runs");
            var every = Candidates(c, data);
            int count = c.SetInt("skill_value_checkpoints");
            var plan = new List<(Skill skill, string role, Obj st, List<string> cids)>();
            foreach (var skill in every)
            {
                var found = Place(c, data, skill);
                if (found == null) { plan.Add((skill, null, null, new List<string>())); continue; }
                var cids = StageCheckpoints(found.Value.stage);
                plan.Add((skill, found.Value.role, found.Value.stage, count != 0 ? cids.Take(count).ToList() : cids));
            }
            var jobs = new List<JobSpec>();
            foreach (var p in plan) if (p.role != null) foreach (var cid in p.cids) foreach (var use in new[] { false, true }) jobs.Add(Job(c, p.role, cid, p.skill, use, 0, runs));
            var done = c.Run(jobs);
            int at = 0;
            var rows = new List<object>();
            foreach (var p in plan)
            {
                if (p.role == null) { rows.Add(new Obj { { "skill", p.skill.Name }, { "role", null } }); continue; }
                var cells = new List<object>();
                foreach (var cid in p.cids)
                {
                    var without = Figures(done[at++]); var withIt = Figures(done[at++]);
                    cells.Add(new Obj { { "checkpoint", cid }, { "without", without }, { "with", withIt } });
                }
                var (cond, act) = RuleFor(c, p.skill);
                rows.Add(new Obj { { "skill", p.skill.Name }, { "role", p.role }, { "stage", p.st.S("Stage") }, { "rule", cond + " / " + act }, { "cells", cells } });
            }
            Directory.CreateDirectory(dir);
            M.ClearFolder(dir);
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(rows), false);
        }

        public static void RunAilments(Ctx c)
        {
            string dir = c.Path("docs", "generated", "skill_ailments");
            var data = c.Data("variant");
            int runs = c.SetInt("check_runs");
            int chain = c.SetInt("ailment_chain");
            var plan = new List<(Skill skill, string role, Obj st, List<string> cids)>();
            foreach (var skill in Hostile(c, data))
            {
                var found = Place(c, data, skill);
                if (found == null) continue;
                plan.Add((skill, found.Value.role, found.Value.stage, StageCheckpoints(found.Value.stage)));
            }
            var contexts = new[] { ("boss", 0), ("random", chain) };
            var jobs = new List<JobSpec>();
            foreach (var p in plan) foreach (var cid in p.cids) foreach (var (context, length) in contexts) foreach (var use in new[] { false, true })
                            jobs.Add(Job(c, p.role, cid, p.skill, use, length, runs));
            var done = c.Run(jobs);
            int at = 0;
            var rows = new List<object>();
            foreach (var p in plan)
            {
                var cells = new List<object>();
                foreach (var cid in p.cids)
                    foreach (var (context, length) in contexts)
                    {
                        var without = Figures(done[at++]); var withIt = Figures(done[at++]);
                        cells.Add(new Obj { { "checkpoint", cid }, { "context", context }, { "without", without }, { "with", withIt } });
                    }
                var (cond, act) = RuleFor(c, p.skill);
                rows.Add(new Obj { { "skill", p.skill.Name }, { "role", p.role }, { "stage", p.st.S("Stage") }, { "rule", cond + " / " + act }, { "cells", cells } });
            }
            Directory.CreateDirectory(dir);
            M.ClearFolder(dir);
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(rows), false);
        }

        static List<Obj> ReadRows(Ctx c, string dir)
        {
            var rows = new List<Obj>();
            foreach (var name in M.Listing(dir)) rows.AddRange(((List<object>)c.ReadJson(Path.Combine(dir, name))).Cast<Obj>());
            return rows;
        }

        static List<Obj> SortedBySkill(List<Obj> rows)
        {
            // sorted(rows, key=lambda r: r['skill']): a stable sort by code point
            return rows.Select((r, i) => (r, i)).OrderBy(x => x.r.S("skill"), StringComparer.Ordinal).ThenBy(x => x.i).Select(x => x.r).ToList();
        }

        public static void ReportAilments(Ctx c)
        {
            var rows = ReadRows(c, c.Path("docs", "generated", "skill_ailments"));
            var lines = new List<string>();
            foreach (var r in SortedBySkill(rows))
            {
                var figs = new List<string>();
                foreach (var context in new[] { "boss", "random" })
                {
                    var cells = r.A("cells").Cast<Obj>().Where(x => x.S("context") == context).ToList();
                    double wins = Py.Sum(cells.Select(x => x.O("with").D("won") - x.O("without").D("won"))) / Math.Max(1, cells.Count);
                    var gains = cells.Where(x => Py.Truthy(x.O("with").Get("time_won")) && Py.Truthy(x.O("without").Get("time_won")))
                                     .Select(x => 1 - x.O("with").D("time_won") / x.O("without").D("time_won")).ToList();
                    double hp = Py.Sum(cells.Select(x => x.O("with").D("hp_left") - x.O("without").D("hp_left"))) / Math.Max(1, cells.Count);
                    figs.Add(Py.Pct(wins, 0, true) + " / " + Py.Pct(gains.Count > 0 ? Py.Sum(gains) / gains.Count : 0.0, 0, true) + " / " + Py.Pct(hp, 0, true));
                }
                lines.Add("| " + r.S("skill") + " | " + r.S("role") + " (" + r.S("stage") + ") | " + r.S("rule") + " | " + figs[0] + " | " + figs[1] + " |");
            }
            var text = new List<string>
            {
                "# Ailments and debuffs: what each adds (generated)", "",
                "Generated by `tools/skill_value.py ailments`. Do not edit. Balance variant. Each hostile skill at the stage where it is first played, used by its role before attacking where it can land (an ailment on random rows: as the opening move, after revives, heals and cures), against the role without it. Cells: wins / length of the won fights (shorter is +) / party HP left at the end. Boss: the boss fights of the stage; random: rows of ailment_chain random battles of each floor, HP and TP carried.",
                "", "| Skill | Played as | Rule | Boss | Random rows |", "|---|---|---|---|---|",
            };
            text.AddRange(lines);
            c.WriteText(c.Path("docs", "generated", "SKILL_AILMENTS.md"), M.Lines(text), false);
        }

        public static void Report(Ctx c)
        {
            double floor = c.SetDouble("skill_value_floor");
            var rows = ReadRows(c, c.Path("docs", "generated", "skill_value"));
            var lines = new List<string>();
            int flagged = 0;
            foreach (var r in SortedBySkill(rows))
            {
                if (r.Get("role") == null) { lines.Add("| " + r.S("skill") + " | - | - | - | - | no role plays a class that learns it |"); continue; }
                var cells = r.A("cells").Cast<Obj>().ToList();
                double wins = Py.Sum(cells.Select(x => x.O("with").D("won") - x.O("without").D("won"))) / cells.Count;
                var gains = cells.Where(x => Py.Truthy(x.O("with").Get("time_won")) && Py.Truthy(x.O("without").Get("time_won")))
                                 .Select(x => 1 - x.O("with").D("time_won") / x.O("without").D("time_won")).ToList();
                double gain = gains.Count > 0 ? Py.Sum(gains) / gains.Count : 0.0;
                string verdict = gain < floor && wins <= 0 ? "to read" : "serves";
                if (verdict == "to read") flagged++;
                lines.Add("| " + r.S("skill") + " | " + r.S("role") + " (" + r.S("stage") + ") | " + r.S("rule") + " | " + Py.Pct(wins, 0, true) + " | " + Py.Pct(gain, 0, true) + " | " + verdict + " |");
            }
            var text = new List<string>
            {
                "# What each skill that deals no damage adds (generated)", "",
                "Generated by `tools/skill_value.py`. Do not edit. Balance variant; boss fights of the first stage where the class is played; the member with the skill used first where it serves, against the member without it. Wins: the change of the share of wins. Length: how much shorter the won fights are. Below "
                    + Py.Pct(floor, 0) + " of length and no wins gained: to read.", "",
                "**" + (rows.Count - flagged) + " of " + rows.Count + " skills serve in the fights of the audit; " + flagged + " to read.**", "",
                "| Skill | Played as | Rule | Wins | Length | Verdict |", "|---|---|---|---|---|---|",
            };
            text.AddRange(lines);
            c.WriteText(c.Path("docs", "generated", "SKILL_VALUE.md"), M.Lines(text), false);
        }
    }
}
