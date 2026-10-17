using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>tools/boss_fit.py gentle: the bosses the curve marks easier, a little harder with the other parties inside their share; docs/generated/BOSS_FIT.md.</summary>
    public static class BossFit
    {
        static readonly string[] Figures = { "won", "time", "lowest_hp", "pressure" };
        static double Easier(string key) => key == "time" || key == "pressure" ? -1 : 1;
        static bool Relative(string key) => key == "time" || key == "pressure";

        public static List<(double hp, double attack)> Pairs(Ctx c)
        {
            var pairs = new List<(double, double)> { (1.0, 1.0) };
            foreach (var pair in Py.Str(c.Setup.Settings["boss_fit_gentle"]).Split(';'))
            {
                var x = pair.Split('/');
                pairs.Add((double.Parse(x[0].Trim(), System.Globalization.CultureInfo.InvariantCulture), double.Parse(x[1].Trim(), System.Globalization.CultureInfo.InvariantCulture)));
            }
            return pairs;
        }

        static List<Obj> CurveRows(Ctx c)
        {
            string dir = c.Path("docs", "generated", "difficulty_curve");
            var rows = new List<Obj>();
            foreach (var name in M.Listing(dir)) rows.AddRange(((List<object>)c.ReadJson(Path.Combine(dir, name))).Cast<Obj>());
            return rows;
        }

        static List<Obj> Todo(Ctx c)
        {
            var skip = new HashSet<string>((c.Setup.Settings.TryGetValue("boss_fit_skip", out var v) ? Py.Str(v ?? "") : "").Split(';').Select(x => x.Trim()).Where(x => x.Length > 0));
            return CurveRows(c).Where(r => r.A("out").Count > 0 && !skip.Contains(r.S("id"))).ToList();
        }

        /// <summary>The enemies of the boss fights of a checkpoint that appear in no random formation (vanilla data), by id.</summary>
        public static List<int> BossEnemies(Ctx c, string cid)
        {
            var data = c.Data("vanilla");
            var cp = c.Checkpoint(cid);
            var common = new HashSet<int>();
            foreach (var z in data.Floors) foreach (var f in z.Formations) foreach (var (e, _) in f.Enemies) common.Add(e);
            var ids = new HashSet<int>();
            foreach (int n in Scenario.BattleNumbers(cp))
            {
                var battle = data.Fixed.First(b => b.Floor == cp.Str("Floor") && b.Number == n);
                foreach (var (e, _) in battle.Enemies) ids.Add(e);
            }
            ids.ExceptWith(common);
            var list = ids.ToList();
            list.Sort();
            return list;
        }

        /// <summary>scaled_changes(): the stats of the enemy records a job of the engine changes.</summary>
        public static Obj ScaledChanges(GameData variant, List<int> ids, double hp, double attack)
        {
            var o = new Obj();
            foreach (var e in ids)
            {
                var rec = variant.Enemies[e];
                o.Set(e.ToString(), new Obj
                {
                    { "hp", (long)PyMath.Round(rec.Hp * hp) }, { "atk", (long)PyMath.Round(rec.Stats[Unit.ATK] * attack) }, { "int", (long)PyMath.Round(rec.Stats[Unit.INT] * attack) },
                });
            }
            return o;
        }

        public static void Run(Ctx c, string only = null)
        {
            string dir = c.Path("docs", "generated", "boss_fit");
            var variant = c.Data("variant");
            int runs = c.SetInt("check_runs"), partyRuns = c.SetInt("boss_fit_party_runs");
            var wanted = only == null ? null : new HashSet<string>(only.Split(';').Select(x => x.Trim()));
            var tasks = new List<(Obj row, (double hp, double attack) pair)>();
            foreach (var row in Todo(c)) foreach (var pair in Pairs(c)) if (wanted == null || wanted.Contains(row.S("id"))) tasks.Add((row, pair));
            var changes = tasks.Select(t => t.pair == (1.0, 1.0) ? null : ScaledChanges(variant, BossEnemies(c, t.row.S("id")), t.pair.hp, t.pair.attack)).ToList();
            var cpJobs = new List<Obj>();
            for (int k = 0; k < tasks.Count; k++)
            {
                var job = new Obj { { "id", "pc" + k }, { "measure", "play_checkpoint" }, { "side", "variant" }, { "cid", tasks[k].row.S("id") }, { "runs", (long)runs } };
                if (changes[k] != null && changes[k].Count > 0) job.Set("enemy_changes", changes[k]);
                cpJobs.Add(job);
            }
            var checkpoints = c.Measure(cpJobs);
            var jobs = new List<JobSpec>();
            for (int k = 0; k < tasks.Count; k++)
                foreach (var b in c.Setup.Battery)
                    jobs.Add(Jb.Make(c, "variant", tasks[k].row.S("id"), roles: b.roles, runs: partyRuns, enemyChanges: changes[k],
                                     name: tasks[k].row.S("id") + "|" + Py.Repr(tasks[k].pair.hp) + "|" + Py.Repr(tasks[k].pair.attack) + "|" + b.name));
            var done = c.Run(jobs);
            int at = 0;
            var data = new List<object>();
            for (int k = 0; k < tasks.Count; k++)
            {
                var parties = new Obj();
                foreach (var b in c.Setup.Battery)
                {
                    var results = done[at++].Runs;
                    parties.Set(b.name, (double)results.Count(r => r.Won) / results.Length);
                }
                data.Add(new Obj
                {
                    { "id", tasks[k].row.S("id") }, { "hp", tasks[k].pair.hp }, { "attack", tasks[k].pair.attack },
                    { "enemies", Jb.L(BossEnemies(c, tasks[k].row.S("id")).Select(e => (object)(long)e)) },
                    { "figures", M.Summary(checkpoints[k].O("summary")) }, { "parties", parties },
                });
            }
            Directory.CreateDirectory(dir);
            foreach (var name in M.Listing(dir))
                if (name.StartsWith("gentle_update_") || (name.StartsWith("gentle_") && only == null)) File.Delete(Path.Combine(dir, name));
            c.WriteText(Path.Combine(dir, "gentle_" + (only != null ? "update_" : "") + "1.json"), PyJson.Dump(data), false);
        }

        // --- the choice and the report -------------------------------------------------------------------------------
        sealed class Tried
        {
            public Obj Raw;
            public double Hp, Attack;
            public List<(string key, double gap)> Gaps;
            public List<(string archetype, double share)> Archetypes;
            public List<string> Below, Harder;
            public double Distance;
            public Obj Figures => Raw.O("figures");
        }

        sealed class Found
        {
            public string Id;
            public List<string> Names;
            public double Floor;
            public Obj Vanilla;
            public List<Tried> TriedList;
            public Tried Kept;
            public string Why;
        }

        static List<(string key, double gap)> Gaps(Ctx c, Obj vanilla, Obj fig)
        {
            var o = new List<(string, double)>();
            foreach (var key in Figures)
            {
                var a = vanilla.Get(key); var b = fig.Get(key);
                if (a == null || b == null) continue;
                double window = c.SetDouble("check_" + key + "_window");
                double width = window * (Relative(key) ? Py.Num(a) : 1.0);
                o.Add((key, width != 0 ? Easier(key) * (Py.Num(b) - Py.Num(a)) / width : 0.0));
            }
            return o;
        }

        static List<Found> Choice(Ctx c)
        {
            string dir = c.Path("docs", "generated", "boss_fit");
            var data = c.Data("vanilla");
            var rows = new List<Obj>();
            foreach (var name in M.Listing(dir))
                if (name.StartsWith("gentle_")) rows.AddRange(((List<object>)c.ReadJson(Path.Combine(dir, name))).Cast<Obj>());
            var pairs = Pairs(c);
            var order = new Dictionary<(double, double), int>();
            for (int i = 0; i < pairs.Count; i++) order[pairs[i]] = i;
            var archetypes = new List<(string archetype, List<string> names)>();
            foreach (var b in c.Setup.Battery)
            {
                var g = archetypes.FirstOrDefault(x => x.archetype == b.archetype);
                if (g.names == null) archetypes.Add((b.archetype, new List<string> { b.name })); else g.names.Add(b.name);
            }
            var curve = new List<Obj>();
            foreach (var r in CurveRows(c))
            {
                int at = curve.FindIndex(x => x.S("id") == r.S("id"));
                if (at >= 0) curve[at] = r; else curve.Add(r);
            }
            var found = new List<Found>();
            foreach (var row in curve)
            {
                string cid = row.S("id");
                var latest = new List<Obj>();
                foreach (var r in rows.Where(x => x.S("id") == cid))
                {
                    int at = latest.FindIndex(x => x.D("hp") == r.D("hp") && x.D("attack") == r.D("attack"));
                    if (at >= 0) latest[at] = r; else latest.Add(r);
                }
                var tried = latest.OrderBy(r => order[(r.D("hp"), r.D("attack"))]).Select(r => new Tried { Raw = r, Hp = r.D("hp"), Attack = r.D("attack") }).ToList();
                if (tried.Count == 0) continue;
                double floor = M.Floor(c, cid);
                foreach (var t in tried)
                {
                    t.Gaps = Gaps(c, row.O("vanilla"), t.Figures);
                    t.Archetypes = archetypes.Select(g => (g.archetype, g.names.Select(n => t.Raw.O("parties").D(n)).Max())).ToList();
                    t.Below = t.Archetypes.Where(a => a.share < floor).Select(a => a.archetype).OrderBy(x => x, StringComparer.Ordinal).ToList();
                    t.Harder = t.Gaps.Where(g => g.gap < -1.0).Select(g => g.key).OrderBy(x => x, StringComparer.Ordinal).ToList();
                    t.Distance = Py.Sum(t.Gaps.Select(g => Math.Abs(g.gap)));
                }
                var baseT = tried[0];
                Tried kept; string why;
                if (baseT.Below.Count > 0) { kept = null; why = "left alone, below the floor before any change: " + string.Join(", ", baseT.Below); }
                else
                {
                    var allowed = tried.Skip(1).Where(t => t.Below.Count == 0 && t.Harder.Count == 0).ToList();
                    var candidates = new List<Tried> { baseT }; candidates.AddRange(allowed);
                    Tried best = null; (double, int) bestKey = (0, 0);
                    foreach (var t in candidates)
                    {
                        var key = (PyMath.RoundTo(t.Distance, 3), order[(t.Hp, t.Attack)]);
                        if (best == null || key.Item1 < bestKey.Item1 || (key.Item1 == bestKey.Item1 && key.Item2 < bestKey.Item2)) { best = t; bestKey = key; }
                    }
                    if (ReferenceEquals(best, baseT))
                    {
                        kept = null;
                        why = allowed.Count > 0 ? "left alone: no allowed pair is nearer to vanilla" : "left alone: every pair takes an archetype below the floor or passes vanilla";
                    }
                    else { kept = best; why = "kept"; }
                }
                var ids = tried[0].Raw.A("enemies").Select(x => (int)Py.Num(x)).ToList();
                found.Add(new Found { Id = cid, Names = ids.Select(e => data.Enemies[e].Name).ToList(), Floor = floor, Vanilla = row.O("vanilla"), TriedList = tried, Kept = kept, Why = why });
            }
            return found;
        }

        static string Share(double x) => Py.Pct(x, 0);

        static string FiguresText(Obj f)
        {
            if (!Py.Truthy(f.Get("time"))) return Share(f.D("won"));
            return Share(f.D("won")) + " / " + Py.F(f.D("time"), 1) + " / " + Share(f.D("lowest_hp")) + " / " + Py.F(f.D("pressure"), 2);
        }

        public static void Report(Ctx c)
        {
            var found = Choice(c);
            var lines = new List<string>
            {
                "# Bosses made a little harder, with the other parties inside their share (generated)", "",
                "Generated by `dtcli boss-fit`. Do not edit. The rule is in the header of the tool; the pairs it may try are Settings `boss_fit_gentle` ("
                    + Py.Str(c.Setup.Settings["boss_fit_gentle"]) + ": factor on HP / factor on ATK and INT). Reference party: wins / length / lowest HP / pressure. Archetypes: the win share of the best party of each (sheet BatteryParties). Floor: the least win share the class of the boss allows.", "",
                "**" + found.Count(r => r.Kept != null) + " of " + found.Count + " bosses changed.**", "",
                "| Checkpoint | Boss | Floor | Vanilla | Variant, no change | Kept | Variant with it | Archetypes with it |", "|---|---|---|---|---|---|---|---|",
            };
            foreach (var r in found)
            {
                var baseT = r.TriedList[0]; var kept = r.Kept;
                var last = kept ?? baseT;
                string arch = string.Join(", ", last.Archetypes.Select(a => a.archetype + " " + Share(a.share)));
                string what = kept != null ? "HP x" + Py.F(kept.Hp, 2) + ", ATK and INT x" + Py.F(kept.Attack, 2) : r.Why;
                lines.Add("| " + r.Id + " | " + string.Join(", ", r.Names) + " | " + Share(r.Floor) + " | " + FiguresText(r.Vanilla) + " | " + FiguresText(baseT.Figures) + " | " + what + " | "
                          + (kept != null ? FiguresText(kept.Figures) : "") + " | " + arch + " |");
            }
            lines.AddRange(new[] { "", "## Every pair tried", "", "| Checkpoint | HP | ATK, INT | Reference party | Gap to vanilla (window widths) | Below the floor | Past vanilla on |", "|---|---|---|---|---|---|---|" });
            foreach (var r in found)
                foreach (var t in r.TriedList)
                    lines.Add("| " + r.Id + " | x" + Py.F(t.Hp, 2) + " | x" + Py.F(t.Attack, 2) + " | " + FiguresText(t.Figures) + " | " + Py.F(t.Distance, 1) + " | "
                              + (t.Below.Count > 0 ? string.Join(", ", t.Below) : "-") + " | " + (t.Harder.Count > 0 ? string.Join(", ", t.Harder) : "-") + " |");
            c.WriteText(c.Path("docs", "generated", "BOSS_FIT.md"), M.Lines(lines), false);
        }
    }
}
