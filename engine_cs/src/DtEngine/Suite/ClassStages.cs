using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>dtcli class-stages: every class at the stage of the game where it is played; docs/generated/CLASS_STAGES.md.</summary>
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

        /// <summary>The role in a party of BatteryParties: in the place of the same role, else of the last member of the same kind and line (an attacker
        /// for an attacker, a support of the Maid line for one), else of the last attacker, else of the last member.</summary>
        static JobSpec BatteryJob(Ctx c, string cid, string role, string party, int runs)
        {
            var cp = c.Checkpoint(cid);
            var sc = c.Sc("variant");
            var data = c.Data("variant");
            int level = sc.ReferenceLevels()[cid].level;
            string Kind(string r) => KindOf(c, r, data.ClassName(sc.ClassPath(c.Setup.Roles[r], level).Item1));
            var roles = c.Setup.Battery.First(b => b.name == party).roles.ToList();
            string Line(string r) => c.Setup.Roles[r].Str("Base class");
            int slot = roles.IndexOf(role);
            if (slot < 0) slot = roles.FindLastIndex(r => Kind(r) == Kind(role) && Line(r) == Line(role));
            if (slot < 0 && Kind(role) == "attacker") slot = roles.FindLastIndex(r => Kind(r) == "attacker");
            // a support or tank of another line takes the place of an attacker: the party keeps the supports it has
            if (slot < 0) slot = roles.FindLastIndex(r => Kind(r) == "attacker");
            if (slot < 0) slot = roles.Count - 1;
            roles[slot] = role;
            var recipe = new Obj
            {
                { "place", "replace_role" }, { "items", "first_kept" },
                { "tested", Jb.L(new Obj { { "role", role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) } }) },
            };
            return Jb.Make(c, "variant", cid, roles: roles, runs: runs, crown: 0, record: true, recipe: recipe, name: cid + "|" + party + "|" + role);
        }

        /// <summary>The kind of a role at a stage: support when its path ends in a support class, else the kind of its class (sheet ClassKinds).</summary>
        static string KindOf(Ctx c, string role, string cls)
        {
            var byClass = c.In("class_kinds");
            return Py.Str(byClass.Get(c.Setup.Roles[role].Str("Lv30 class"))) == "support" ? "support" : (cls != null && byClass.Has(cls) ? Py.Str(byClass.Get(cls)) : "attacker");
        }

        /// <summary>Every role at every checkpoint of its stage, in the parties of section class_stages_report: the reference party of the checkpoint
        /// (the role in its last place) and each party of BatteryParties; the same seeds for every role. A role's figures are the mean over the
        /// parties; its length is taken against the median attacker of the same party, then averaged (ratio).</summary>
        public static void Run(Ctx c, string onlyStage = null)
        {
            string dir = c.Path("docs", "generated", "class_stages");
            var cfg = c.In("class_stages_report");
            int runs = (int)Py.Num(cfg.Get("runs"));
            var sc = c.Sc("variant");
            var data = c.Data("variant");
            var parties = new List<string>();
            if (Py.Truthy(cfg.Get("reference_party"))) parties.Add(null);
            if (Py.Truthy(cfg.Get("battery_parties"))) parties.AddRange(c.Setup.Battery.Select(b => b.name));
            var cids = new List<string>();
            foreach (var st in M.Stages(c)) if (onlyStage == null || st.S("Stage") == onlyStage) cids.AddRange(Checkpoints(st));
            var roles = c.Setup.RoleOrder.ToList();
            var jobs = new List<JobSpec>();
            foreach (var cid in cids)
                foreach (var party in parties)
                    foreach (var role in roles) jobs.Add(party == null ? Job(c, cid, role, runs) : BatteryJob(c, cid, role, party, runs));
            var done = c.Run(jobs);
            Directory.CreateDirectory(dir);
            int at = 0;
            foreach (var cid in cids)
            {
                int level = sc.ReferenceLevels()[cid].level;
                var byParty = new List<Dictionary<string, Obj>>();
                foreach (var party in parties)
                {
                    var figs = new Dictionary<string, Obj>();
                    foreach (var role in roles)
                    {
                        var d = done[at++];
                        string tested = d.Spec.TestedNames.Count > 0 ? d.Spec.TestedNames[0] : null;
                        var r = Figures(d.Runs, runs, tested, level, role);
                        var (cls, _) = sc.ClassPath(c.Setup.Roles[role], level);
                        r.Set("class", data.ClassName(cls));
                        figs[role] = r;
                    }
                    // the length of each role against the median attacker of this party
                    var times = figs.Where(kv => KindOf(c, kv.Key, (string)kv.Value.Get("class")) == "attacker" && Py.Truthy(kv.Value.Get("time_won")))
                                    .Select(kv => kv.Value.D("time_won")).ToList();
                    double? median = times.Count > 0 ? Py.Median(times) : (double?)null;
                    foreach (var r in figs.Values)
                        r.Set("ratio", median.HasValue && Py.Truthy(r.Get("time_won")) ? (object)(r.D("time_won") / median.Value) : null);
                    byParty.Add(figs);
                }
                var outObj = new Obj { { "parties", Jb.L(parties.Select(x => (object)(x ?? "reference"))) }, { "runs", (long)runs }, { "roles", new Obj() } };
                foreach (var role in roles)
                {
                    var all = byParty.Select(f => f[role]).ToList();
                    double Mean(string key) => all.Average(r => r.D(key));
                    var ratios = all.Where(r => Py.Truthy(r.Get("ratio"))).Select(r => r.D("ratio")).ToList();
                    var wonTimes = all.Where(r => Py.Truthy(r.Get("time_won"))).Select(r => r.D("time_won")).ToList();
                    outObj.O("roles").Set(role, new Obj
                    {
                        { "won", Mean("won") }, { "time_won", wonTimes.Count > 0 ? (object)wonTimes.Average() : null },
                        { "ratio", ratios.Count > 0 ? (object)ratios.Average() : null }, { "share", Mean("share") },
                        { "lowest_hp", Mean("lowest_hp") }, { "hp_left", Mean("hp_left") }, { "class", all[0].Get("class") },
                        { "character", all[0].Get("character") }, { "level", (long)level },
                        { "by_party", Jb.L(parties.Select((x, k) => (object)new Obj { { "party", x ?? "reference" }, { "won", all[k].D("won") }, { "ratio", all[k].Get("ratio") } })) },
                    });
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
            var cfg = c.In("class_stages_report");
            int parties = (Py.Truthy(cfg.Get("reference_party")) ? 1 : 0) + (Py.Truthy(cfg.Get("battery_parties")) ? c.Setup.Battery.Count : 0);
            int runs = (int)Py.Num(cfg.Get("runs"));
            var text = new List<string>
            {
                "# Every class at its stage (generated)", "",
                "Generated by `dtcli class-stages`. Do not edit. Balance variant; each role at every checkpoint of its stage in " + parties + " parties: the reference party of the checkpoint (in its last place) and each party of the sheet BatteryParties (in the place of the same role, else of the last member), " + runs + " fights each, " + (parties * runs) + " a cell; the same seeds for every role. Cells, the mean over the parties: wins / length of the won fights against the median attacker of the same party / share of the party damage. An attacker is slow above "
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
                var hard = measured.Where(m => medianWon(m.cid) < c.In("class_stages_report").D("hard_below")).Select(m => m.cid).ToList();
                var usable = measured.Select(m => m.cid).Where(x => !hard.Contains(x)).ToList();
                var contested = usable.Where(x => medianWon(x) < 1.0).ToList();
                var attMedian = new Dictionary<string, double?>();
                foreach (var cid in usable)
                {
                    var times = new List<double>();
                    foreach (var kv in rolesOf(cid))
                    {
                        var r = (Obj)kv.Value;
                        if (KindOf(c, kv.Key, (string)r.Get("class")) == "attacker" && Py.Truthy(r.Get("time_won"))) times.Add(r.D("time_won"));
                    }
                    attMedian[cid] = times.Count > 0 ? Py.Median(times) : (double?)null;
                    // the ratio to the median attacker, taken party by party when the measure holds it

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
                        double? ratio = !usable.Contains(m.cid) ? (double?)null : r.Has("ratio") ? (Py.Truthy(r.Get("ratio")) ? r.D("ratio") : (double?)null)
                                      : Py.Truthy(attMedian[m.cid]) && Py.Truthy(r.Get("time_won")) ? r.D("time_won") / attMedian[m.cid].Value : (double?)null;
                        cells.Add(Py.Pct(r.D("won"), 0) + " / " + (ratio == null ? "-" : Py.F(ratio.Value, 2)) + " / " + Py.Pct(r.D("share"), 0));
                    }
                    string kind = KindOf(c, role, cls), measure, verdict;
                    if (kind == "attacker")
                    {
                        var ratios = new List<double>();
                        foreach (var cid in usable)
                        {
                            var r = rolesOf(cid).Get(role) as Obj;
                            if (r != null && r.Has("ratio")) { if (Py.Truthy(r.Get("ratio"))) ratios.Add(r.D("ratio")); }
                            else if (Py.Truthy(attMedian[cid]) && r != null && Py.Truthy(r.Get("time_won"))) ratios.Add(r.D("time_won") / attMedian[cid].Value);
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
