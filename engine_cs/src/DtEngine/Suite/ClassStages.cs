using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>tools/class_stages.py: every class at the stage of the game where it is played; docs/generated/CLASS_STAGES.md.</summary>
    public static class ClassStages
    {
        public static List<string> Checkpoints(Obj stage) => Py.Str(stage.Get("Checkpoints")).Split(';').Select(x => x.Trim()).ToList();

        /// <summary>engine_jobs: the reference party of the checkpoint with the last member replaced by the member of the role (none: as it is).</summary>
        public static JobSpec Job(Ctx c, string cid, string role, int runs, string side = "variant", List<object> policyRows = null, string setupName = null)
        {
            var cp = c.Checkpoint(cid);
            Obj recipe = null;
            if (role != null)
                recipe = new Obj
                {
                    { "drop_last", true }, { "items", "first_kept" },
                    { "tested", Jb.L(new Obj { { "role", role }, { "forge", c.Sc(side).ForgeOpen(cp.Str("Floor")) } }) },
                };
            return Jb.Make(c, side, cid, runs: runs, crown: 0, record: true, recipe: recipe, policyRows: policyRows, setupName: setupName, name: cid + "|" + role);
        }

        /// <summary>figures(): the dictionary play() returns, from the results of the runs (with their records).</summary>
        public static Obj Figures(RunResult[] res, int runs, string testedName, int level, string role)
        {
            double share = 0.0;
            foreach (var r in res)
                foreach (var p in r.Parts)
                {
                    var dmg = p.Record.Damage;
                    var total = new PySum(); var mine = new PySum();
                    for (int i = 0; i < dmg.Count; i++)
                    {
                        var u = dmg.Keys[i].Unit;
                        if (u.Side != Unit.PARTY) continue;
                        if (dmg.IsFloat[i]) total.AddFloat(dmg.Values[i]); else total.AddInt((long)dmg.Values[i]);
                        var who = u.Owner ?? u;
                        if (who.Name == testedName && who.HasRole && who.Role == role)
                        {
                            if (dmg.IsFloat[i]) mine.AddFloat(dmg.Values[i]); else mine.AddInt((long)dmg.Values[i]);
                        }
                    }
                    double t = total.Result;
                    if (t == 0) t = 1;
                    share += mine.Result / t / r.Parts.Count;
                }
            var won = res.Where(r => r.Won).ToList();
            return new Obj
            {
                { "won", (double)won.Count / runs }, { "time", Py.Sum(res.Select(r => r.Time)) / runs },
                { "time_won", won.Count > 0 ? (object)(Py.Sum(won.Select(r => r.Time)) / won.Count) : null },
                { "share", share / runs }, { "character", testedName }, { "level", (long)level },
                { "lowest_hp", Py.Sum(res.Select(r => r.LowestHp)) / runs }, { "hp_left", Py.Sum(res.Select(r => r.HpLeft)) / runs },
            };
        }

        public static void Run(Ctx c, string onlyStage = null)
        {
            string dir = c.Path("docs", "generated", "class_stages");
            int runs = c.SetInt("check_runs");
            var sc = c.Sc("variant");
            var cids = new List<string>();
            foreach (var st in M.Stages(c)) if (onlyStage == null || st.S("Stage") == onlyStage) cids.AddRange(Checkpoints(st));
            var roles = new List<string> { null };
            roles.AddRange(c.Setup.RoleOrder);
            var jobs = new List<JobSpec>();
            foreach (var cid in cids) foreach (var role in roles) jobs.Add(Job(c, cid, role, runs));
            var done = c.Run(jobs);
            Directory.CreateDirectory(dir);
            int at = 0;
            foreach (var cid in cids)
            {
                int level = sc.ReferenceLevels()[cid].level;
                var outObj = new Obj { { "base", null }, { "roles", new Obj() } };
                foreach (var role in roles)
                {
                    var d = done[at++];
                    string tested = d.Spec.TestedNames.Count > 0 ? d.Spec.TestedNames[0] : null;
                    var r = Figures(d.Runs, runs, tested, level, role);
                    if (role == null) { outObj.Set("base", r); continue; }
                    var (cls, _) = sc.ClassPath(c.Setup.Roles[role], level);
                    r.Set("class", c.Data("variant").ClassName(cls));
                    outObj.O("roles").Set(role, r);
                }
                foreach (var name in M.Listing(dir))
                    if (name.StartsWith(cid + "_") && name.EndsWith(".json")) File.Delete(Path.Combine(dir, name));
                c.WriteText(Path.Combine(dir, cid + "_1.json"), PyJson.Dump(outObj, 1), false);
            }
        }

        static double Median(IEnumerable<object> xs) => Py.Median(xs.Select(Py.Num));

        public static void Report(Ctx c)
        {
            string dir = c.Path("docs", "generated", "class_stages");
            double slow = c.SetDouble("class_slow_ratio"), weak = c.SetDouble("class_weak_wins");
            var byClass = c.In("class_kinds");
            string KindOf(string role, string cls) =>
                Py.Str(byClass.Get(c.Setup.Roles[role].Str("Lv30 class"))) == "support" ? "support" : (cls != null && byClass.Has(cls) ? Py.Str(byClass.Get(cls)) : "attacker");
            var text = new List<string>
            {
                "# Every class at its stage (generated)", "",
                "Generated by `tools/class_stages.py`. Do not edit. Balance variant; each role takes the last place of the reference party of the checkpoint (15 fights each). Cells: wins / length of the won fights against the median attacker / share of the party damage. An attacker is slow above "
                    + Py.F(slow, 2) + "; a support or tank is weak when its wins in the contested fights fall " + Py.Pct(weak, 0) + " below the median. Kinds of class: sheet ClassKinds; a role whose path ends in a support class is a support at every stage.", "",
            };
            var rowsOut = new List<string>();
            foreach (var st in M.Stages(c))
            {
                var cids = Checkpoints(st);
                var measured = new List<(string cid, Obj roles)>();
                foreach (var cid in cids)
                    foreach (var name in M.Listing(dir))
                        if (name.StartsWith(cid + "_") && name.EndsWith(".json"))
                        {
                            var part = (Obj)c.ReadJson(Path.Combine(dir, name));
                            int at = measured.FindIndex(m => m.cid == cid);
                            if (at < 0) { measured.Add((cid, new Obj())); at = measured.Count - 1; }
                            foreach (var kv in part.O("roles")) measured[at].roles.Set(kv.Key, kv.Value);
                        }
                text.Add("## " + st.S("Stage") + " (" + string.Join(", ", cids) + ")");
                text.Add("");
                if (measured.Count == 0) { text.Add("Not measured yet."); text.Add(""); continue; }
                Func<string, Obj> rolesOf = cid => measured.First(m => m.cid == cid).roles;
                Func<string, double> medianWon = cid => Median(rolesOf(cid).Select(kv => ((Obj)kv.Value).Get("won")));
                var hard = measured.Where(m => medianWon(m.cid) < 0.5).Select(m => m.cid).ToList();
                var usable = measured.Select(m => m.cid).Where(x => !hard.Contains(x)).ToList();
                var contested = usable.Where(x => medianWon(x) < 1.0).ToList();
                var attMedian = new Dictionary<string, double?>();
                foreach (var cid in usable)
                {
                    var times = new List<double>();
                    foreach (var kv in rolesOf(cid))
                    {
                        var r = (Obj)kv.Value;
                        if (KindOf(kv.Key, (string)r.Get("class")) == "attacker" && Py.Truthy(r.Get("time_won"))) times.Add(r.D("time_won"));
                    }
                    attMedian[cid] = times.Count > 0 ? Py.Median(times) : (double?)null;
                }
                var winMedian = contested.ToDictionary(x => x, x => medianWon(x));
                if (hard.Count > 0)
                {
                    text.Add("Hard for every class (median wins below half; out of the verdicts): " + string.Join(", ", hard.Select(x => x + " (" + Py.Pct(medianWon(x), 0) + ")")) + ".");
                    text.Add("");
                }
                text.Add("| Role | Class | Kind | " + string.Join(" | ", measured.Select(m => m.cid)) + " | Measure | Verdict |");
                text.Add("|" + string.Concat(Enumerable.Repeat("---|", 5 + measured.Count)));
                foreach (var role in c.Setup.RoleOrder)
                {
                    var cells = new List<string>();
                    string cls = null;
                    foreach (var m in measured)
                    {
                        var r = m.roles.Get(role) as Obj;
                        if (r == null) { cells.Add("-"); continue; }
                        cls = (string)r.Get("class");
                        double? ratio = usable.Contains(m.cid) && Py.Truthy(attMedian[m.cid]) && Py.Truthy(r.Get("time_won")) ? r.D("time_won") / attMedian[m.cid].Value : (double?)null;
                        cells.Add(Py.Pct(r.D("won"), 0) + " / " + (ratio == null ? "-" : Py.F(ratio.Value, 2)) + " / " + Py.Pct(r.D("share"), 0));
                    }
                    string kind = KindOf(role, cls), measure, verdict;
                    if (kind == "attacker")
                    {
                        var ratios = new List<double>();
                        foreach (var cid in usable)
                        {
                            var r = rolesOf(cid).Get(role) as Obj;
                            if (Py.Truthy(attMedian[cid]) && r != null && Py.Truthy(r.Get("time_won"))) ratios.Add(r.D("time_won") / attMedian[cid].Value);
                        }
                        double? value = ratios.Count > 0 ? Py.Sum(ratios) / ratios.Count : (double?)null;
                        verdict = value != null && value.Value > slow ? "slow" : "within";
                        measure = value != null ? "length " + Py.F(value.Value, 2) : "no win";
                    }
                    else
                    {
                        var gaps = new List<double>();
                        foreach (var cid in contested)
                            if (rolesOf(cid).Get(role) is Obj r) gaps.Add(r.D("won") - winMedian[cid]);
                        double? value = gaps.Count > 0 ? Py.Sum(gaps) / gaps.Count : (double?)null;
                        verdict = value != null && value.Value < -weak ? "weak" : "within";
                        measure = value != null ? "wins " + Py.Pct(value.Value, 0, true) + " on the median" : "no contested fight";
                    }
                    rowsOut.Add(verdict);
                    text.Add("| " + role + " | " + Py.Str(cls) + " | " + kind + " | " + string.Join(" | ", cells) + " | " + measure + " | " + verdict + " |");
                }
                text.Add("");
            }
            int bad = rowsOut.Count(v => v != "within");
            text.Insert(4, "**" + (rowsOut.Count - bad) + " of " + rowsOut.Count + " role and stage rows within the band, " + bad + " slow or weak.**");
            text.Insert(5, "");
            c.WriteText(c.Path("docs", "generated", "CLASS_STAGES.md"), M.Lines(text), false);
        }
    }
}
