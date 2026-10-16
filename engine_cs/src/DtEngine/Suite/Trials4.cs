using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>The trials that need data built from rows of balance_changes.xlsx other than the variant of the snapshot: tools/engine_sides.py writes the sides,
    /// `--extra build/engine_extra_rows.json` (or ..._ablation.json) brings them in.</summary>
    public static class TrialsC
    {
        // --- rows_trial.py ------------------------------------------------------------------------------------------
        public static void RowsTrial(Ctx c, string[] a)
        {
            var ids = a[0].Split(','); var bosses = a[1].Split(';'); int runs = int.Parse(a[2]);
            var win = c.In("win_rates").O("parties");
            var parties = new List<string> { "reference" }; parties.AddRange(win.Keys);
            var played = new Dictionary<(string, string, bool), (double won, double time, double low)>();
            foreach (var p in parties)
                foreach (var cid in bosses)
                    foreach (var without in new[] { true, false })
                    {
                        string side = without ? "rows|without" : "variant";
                        if (p == "reference")
                        {
                            var job = new Obj { { "id", "pc" }, { "measure", "play_checkpoint" }, { "side", side }, { "cid", cid }, { "runs", (long)runs } };
                            var s = M.Summary(c.Measure(new List<Obj> { job })[0].O("summary"));
                            played[(p, cid, without)] = (s.D("won"), Py.Truthy(s.Get("time")) ? s.D("time") : 0, s.D("lowest_hp"));
                        }
                        else
                        {
                            var roles = ((string)((List<object>)win.Get(p))[0]).Split(';').Select(r => r.Trim()).ToList();
                            var done = c.Run(Jb.Make(c, side, cid, roles: roles, runs: runs, name: p + "|" + cid + "|" + without));
                            played[(p, cid, without)] = (Trials.Share(done), Trials.WonTime(done), Py.Sum(done.Runs.Select(r => r.LowestHp)) / done.Runs.Length);
                        }
                    }
            Trials.Say(c, "without " + string.Join(", ", ids) + " > with: wins (length, lowest HP), " + runs + " battles");
            foreach (var p in parties)
                Trials.Say(c, "  " + p.PadRight(16) + " " + string.Join(" | ", bosses.Select(cid =>
                {
                    var x = played[(p, cid, true)]; var y = played[(p, cid, false)];
                    return cid + " " + Py.Pct(x.won, 0) + " > " + Py.Pct(y.won, 0) + " (" + Py.F(x.time, 0) + " > " + Py.F(y.time, 0) + "t, " + Py.Pct(x.low, 0) + " > " + Py.Pct(y.low, 0) + ")";
                })));
        }

        // --- curve_ablation.py --------------------------------------------------------------------------------------
        static string FileOf(Ctx c, string cas, string runs) =>
            c.Path("measures", "curve_ablation_" + cas.Replace(" ", "_").Replace(",", "_") + (runs != null ? "_" + runs : "") + ".json");

        public static void CurveAblation(Ctx c, string[] a)
        {
            var inp = c.In("trials").O("curve_ablation");
            var places = inp.A("places").Select(x => (string)x).ToList();
            var cases = inp.A("cases").Select(x => (string)x).ToList();
            if (a[0] == "report") { Report(c, places, cases); return; }
            string runsText = a.Length > 1 && a[1].Length > 0 ? a[1] : null;
            foreach (var cas in a[0] == "all" ? cases : new List<string> { a[0] })
            {
                var jobs = places.Select(cid => new Obj
                {
                    { "id", "cc-" + cid }, { "measure", "check_change" }, { "side", "ablation|" + cas + "|vanilla" }, { "changed_side", "ablation|" + cas + "|variant" },
                    { "checkpoints", Jb.L(cid) }, { "runs", runsText != null ? (object)long.Parse(runsText) : null },
                }).ToList();
                var rows = new List<object>();
                foreach (var raw in c.Measure(jobs))
                    foreach (Obj row in raw.A("rows"))
                    {
                        var before = M.Summary(row.O("before")); before.Set("level", row.L("level_before"));
                        var after = M.Summary(row.O("after")); after.Set("level", row.L("level_after"));
                        rows.Add(new Obj { { "id", row.S("cid") }, { "vanilla", before }, { "variant", after }, { "out", row.A("out") } });
                        Trials.Say(c, cas + " " + row.S("cid") + " " + Py.ReprObj(row.A("out")));
                    }
                c.WriteText(FileOf(c, cas, runsText), PyJson.Dump(rows), false);
            }
        }

        static string Cell(Obj r)
        {
            var signs = new List<string>();
            var vanilla = r.O("vanilla"); var variant = r.O("variant");
            foreach (string k in r.A("out"))
                if (vanilla.Get(k) != null && variant.Get(k) != null)
                    signs.Add(k + " " + ((variant.D(k) - vanilla.D(k)) * (k == "time" || k == "pressure" ? -1 : 1) > 0 ? "easier" : "harder"));
            return Py.Pct(variant.D("won"), 0) + " / " + Py.F(variant.D("time"), 1) + " / " + Py.Pct(variant.D("lowest_hp"), 0) + " / " + Py.F(variant.D("pressure"), 2)
                   + (signs.Count > 0 ? " (" + string.Join(", ", signs) + ")" : "");
        }

        static void Report(Ctx c, List<string> places, List<string> cases)
        {
            var found = new List<(string cas, Dictionary<string, Obj> rows)>();
            foreach (var cas in cases)
            {
                string path = c.Path("measures", "curve_ablation_" + cas.Replace(" ", "_") + ".json");
                if (!File.Exists(path)) continue;
                found.Add((cas, ((List<object>)c.ReadJson(path)).Cast<Obj>().ToDictionary(r => r.S("id"))));
            }
            var lines = new List<string>
            {
                "# What moved the checkpoints of the curve (generated by measures/curve_ablation.py)", "",
                "Cells: wins / length / lowest HP / pressure of the variant, and what is out of the window of vanilla. \"now\": the variant as it is; \"then\": every change since commit dc1a09b taken back; the others: that change alone taken back.", "",
                "| Case | " + string.Join(" | ", places) + " |", "|---|" + string.Concat(places.Select(p => "---|")),
            };
            foreach (var (cas, rows) in found) lines.Add("| " + cas + " | " + string.Join(" | ", places.Select(p => Cell(rows[p]))) + " |");
            c.WriteText(c.Path("measures", "CURVE_ABLATION.md"), M.Lines(lines), true);
        }
    }
}
