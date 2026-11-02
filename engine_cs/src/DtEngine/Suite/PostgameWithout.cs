using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        /// <summary>dtcli postgame-without RUNS TABLES [PARTIES] --extra build/engine_extra_groups.json: the bosses of postgame-compare where the variant wins over
        /// the flag more than vanilla, at the crown of postgame-compare, played by each party (reference, or a party of win_rates) on vanilla, on the variant and on
        /// the variant without the rows of each table (python tools/engine_sides.py groups); wins %, vanilla > variant > without each table.</summary>
        public static void PostgameWithout(Ctx c, string[] a)
        {
            int runs = int.Parse(a[0]); var tables = a[1].Split(';').ToList();
            var win = c.In("win_rates").O("parties");
            var parties = a.Length > 2 ? a[2].Split(';').ToList() : new List<string> { "reference" };
            double flag = c.In("postgame_compare").D("flag");
            var rows = Parts.Read(c, "postgame_compare").OrderBy(r => r.S("id"), StringComparer.Ordinal)
                .Where(r => r.O("vanilla").D("won") >= r.D("floor") && r.O("variant").D("won") - r.O("vanilla").D("won") > flag).ToList();
            var sides = new List<string> { "vanilla", "variant" }; sides.AddRange(tables.Select(t => "rows|without|" + t));
            var jobs = new List<JobSpec>();
            foreach (var party in parties)
                foreach (var r in rows)
                    foreach (var side in sides)
                    {
                        List<string> roles = party == "reference" ? null : ((string)((List<object>)win.Get(party))[0]).Split(';').Select(x => x.Trim()).ToList();
                        jobs.Add(Jb.Make(c, side, r.S("id"), roles: roles, runs: runs, crown: (int)r.L("crown"), name: party + "|" + r.S("id") + "|" + side));
                    }
            var done = c.Run(jobs);
            Trials.Say(c, runs + " battles; crown of postgame-compare; wins %; vanilla > variant > the variant without the rows of: " + string.Join(", ", tables));
            int k = 0;
            foreach (var party in parties)
            {
                Trials.Say(c, "party " + party);
                foreach (var r in rows)
                {
                    var cells = new List<string>();
                    foreach (var side in sides) cells.Add((100.0 * Trials.Share(done[k++])).ToString("0") + "%");
                    Trials.Say(c, r.S("id") + " " + Py.Str(r.Get("boss")) + " | " + string.Join(" > ", cells));
                }
            }
        }
    }
}
