using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>tools/skill_worth.py: what each attacking skill is worth beside the best one of its own class; docs/generated/SKILL_WORTH.md.</summary>
    public static class SkillWorth
    {
        static string Head(string name)
        {
            int at = name.IndexOf(" zone", StringComparison.Ordinal);
            return at < 0 ? name : name.Substring(0, at);
        }

        static string Four(string name) => name.Length <= 4 ? name : name.Substring(0, 4);

        /// <summary>The analysis of one role at one checkpoint: an item of the measure skill_scores.</summary>
        public static Obj Item(Ctx c, GameData data, string cid, string role, int groups, string side = "variant", string setupName = null)
        {
            var sc = c.Sc(side);
            var cp = c.Checkpoint(cid);
            string floor = cp.Str("Floor");
            int level = sc.ReferenceLevels()[cid].level;
            var zones = data.Floors.Where(z => Head(z.Name) == floor && z.Formations.Length > 0).ToList();
            if (zones.Count == 0) zones = data.Floors.Where(z => Four(z.Name) == Four(floor) && z.Formations.Length > 0).ToList();
            var contexts = Jb.L(new Obj { { "kind", "fixed" }, { "floor", floor }, { "number", (long)Scenario.BattleNumbers(cp)[Scenario.BattleNumbers(cp).Length - 1] } });
            if (zones.Count > 0 && groups > 0)
                contexts.Add(new Obj { { "kind", "draws" }, { "zones", Jb.L(zones.Select(z => (object)z.Name)) }, { "seed", 1L }, { "count", (long)groups } });
            var row = c.Setup.Roles[role];
            string who = row.Str("Characters (order of preference)").Split(';').Select(n => n.Trim()).First();
            var chars = data.Characters.ToDictionary(x => x.Name);
            var learnable = new HashSet<int>(sc.ClassesSoFar(row, level));
            var extra = new Obj();
            foreach (var s in data.SkillList)
                if ((s.Category == "Technique" || s.Category == "Magic") && s.Classes.Any(learnable.Contains) && Policy.UsableInBattle(s))
                    extra.Set(s.Id.ToString(), (long)(s.Levels != 0 ? s.Levels : 1));
            var recipe = new Obj
            {
                { "name_not", chars[who].Name }, { "first", 4L }, { "drop_others", true },
                { "tested", Jb.L(new Obj { { "role", role }, { "character", who }, { "level", (long)level }, { "forge", sc.ForgeOpen(floor) }, { "unique_pieces", true }, { "extra_skills", extra } }) },
            };
            var item = new Obj { { "side", side }, { "setup", setupName }, { "job", JobObj(c, cid, role, recipe, side, setupName) }, { "contexts", contexts }, { "zone", true } };
            return item;
        }

        /// <summary>The job as the dictionary make_job gives (the measure reads it as a file of jobs would be read).</summary>
        static Obj JobObj(Ctx c, string cid, string role, Obj recipe, string side, string setupName)
        {
            var party = new Obj { { "cid", cid }, { "roles", null }, { "level", null }, { "crown", 0L }, { "recipe", recipe } };
            var job = new Obj
            {
                { "id", cid + "|" + role }, { "side", side }, { "runs", 1L }, { "seed", Convert.ToInt64(c.Setup.Settings["seed"]) }, { "trace", 0L }, { "record", false },
                { "kit", null }, { "options", new Obj() }, { "party", party }, { "enemies", new Obj { { "kind", "checkpoint" } } },
            };
            if (setupName != null) job.Set("setup", setupName);
            return job;
        }

        public static void Run(Ctx c)
        {
            string dir = c.Path("docs", "generated", "skill_worth");
            var data = c.Data("variant");
            int groups = c.SetInt("skill_worth_groups");
            Directory.CreateDirectory(dir);
            foreach (var st in M.Stages(c))
            {
                var plan = new List<(string cid, string role, int level, Obj item)>();
                foreach (var cid in ClassStages.Checkpoints(st))
                {
                    int level = c.Sc("variant").ReferenceLevels()[cid].level;
                    foreach (var role in c.Setup.RoleOrder) plan.Add((cid, role, level, Item(c, data, cid, role, groups)));
                }
                var jobs = plan.Select((p, k) => { var j = p.item; j.Set("id", "scores" + k); j.Set("measure", "skill_scores"); return j; }).ToList();
                var played = c.Measure(jobs);
                var rows = new List<object>();
                for (int k = 0; k < plan.Count; k++)
                {
                    var (cid, role, level, _) = plan[k];
                    var (cls, _) = c.Sc("variant").ClassPath(c.Setup.Roles[role], level);
                    string clsName = data.ClassName(cls);
                    var contexts = new List<(string name, List<(string skill, double value)> sc)>();
                    var raw = played[k].A("contexts");
                    for (int g = 0; g < raw.Count; g++)
                    {
                        // dict(list of pairs): a name met again keeps its place and takes the later value
                        var dict = new List<(string, double)>();
                        foreach (List<object> pair in (List<object>)raw[g])
                        {
                            string name = (string)pair[0]; double value = Py.Num(pair[1]);
                            int at = dict.FindIndex(x => x.Item1 == name);
                            if (at >= 0) dict[at] = (name, value); else dict.Add((name, value));
                        }
                        contexts.Add((g == 0 ? "boss" : "random", dict));
                    }
                    foreach (var (name, sc) in contexts)
                    {
                        double best = sc.Count > 0 ? sc.Max(x => x.value) : 0.0;
                        string top = null; double topValue = 0;
                        foreach (var (skill, value) in sc) if (top == null || value > topValue) { top = skill; topValue = value; }
                        foreach (var (skill, value) in sc)
                            rows.Add(new Obj
                            {
                                { "checkpoint", cid }, { "role", role }, { "class", clsName }, { "context", name }, { "skill", skill },
                                { "ratio", best != 0 ? value / best : 0.0 }, { "best", top },
                            });
                    }
                }
                c.WriteText(Path.Combine(dir, st.S("Stage") + ".json"), PyJson.Dump(rows), false);
            }
        }

        public static void Report(Ctx c)
        {
            var data = c.Data("vanilla");
            string dir = c.Path("docs", "generated", "skill_worth");
            double dead = c.SetDouble("skill_dead_ratio");
            var best = new List<(string skill, Obj row)>();
            foreach (var name in M.Listing(dir))
                foreach (Obj r in (List<object>)c.ReadJson(Path.Combine(dir, name)))
                {
                    if (r.S("skill") == "(plain attack)") continue;
                    int at = best.FindIndex(b => b.skill == r.S("skill"));
                    if (at < 0) best.Add((r.S("skill"), r));
                    else if (r.D("ratio") > best[at].row.D("ratio")) best[at] = (r.S("skill"), r);
                }
            var attacking = best.Select((b, i) => (b, i)).OrderBy(x => x.b.row.D("ratio")).ThenBy(x => x.i).Select(x => x.b).ToList();
            var damaging = new HashSet<string>(best.Select(b => b.skill));
            var others = data.SkillList.Where(s => (s.Category == "Technique" || s.Category == "Magic") && s.Classes.Length > 0 && Policy.UsableInBattle(s)).Select(s => s.Name)
                             .Distinct().Where(n => !damaging.Contains(n)).ToList();
            others.Sort(string.CompareOrdinal);
            int nDead = attacking.Count(a => a.row.D("ratio") < dead);
            var text = new List<string>
            {
                "# What each attacking skill is worth (generated)", "",
                "Generated by `dtcli skill-worth`. Do not edit. Balance variant. Worth: the best share, over every checkpoint of its stages, role and context (the boss fight or a random battle of the floor), of the value per time and TP of the best attacking option of the same member, every skill at its top level. Below "
                    + Py.Pct(dead, 0) + " (Settings skill_dead_ratio) a skill is dead for damage.", "",
                "**" + (attacking.Count - nDead) + " of " + attacking.Count + " attacking skills worth at least " + Py.Pct(dead, 0) + " of the best of their class somewhere; " + nDead
                    + " dead for damage. " + others.Count + " skills deal no damage (read by hand).**", "",
                "| Skill | Worth | Where (checkpoint, role, class, context) | Best there |", "|---|---|---|---|",
            };
            foreach (var (skill, r) in attacking)
            {
                string flag = r.D("ratio") < dead ? " **dead**" : "";
                text.Add("| " + skill + " | " + Py.Pct(r.D("ratio"), 0) + flag + " | " + r.S("checkpoint") + ", " + r.S("role") + ", " + Py.Str(r.Get("class")) + ", " + r.S("context") + " | " + r.S("best") + " |");
            }
            text.AddRange(new[] { "", "## Skills that deal no damage (read by hand)", "", string.Join(", ", others), "" });
            c.WriteText(c.Path("docs", "generated", "SKILL_WORTH.md"), M.Lines(text), false);
        }
    }
}
