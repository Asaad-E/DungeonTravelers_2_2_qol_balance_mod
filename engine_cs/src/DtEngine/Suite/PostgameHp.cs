using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        /// <summary>dtcli postgame-hp RUNS MULTIPLIERS [BOSSES]: the bosses of postgame-compare where the variant wins over the flag more than vanilla (or
        /// the ones named, P05;P06), played again on the variant at the same crown with the max HP of every foe of the fight times each multiplier;
        /// wins % and length of the won fights, vanilla > variant > each multiplier.</summary>
        public static void PostgameHp(Ctx c, string[] a)
        {
            int runs = int.Parse(a[0]); var mults = a[1].Split(';').Select(x => double.Parse(x, System.Globalization.CultureInfo.InvariantCulture)).ToList();
            var named = a.Length > 2 ? a[2].Split(';').ToHashSet() : null;
            double flag = c.In("postgame_compare").D("flag");
            var rows = Parts.Read(c, "postgame_compare").OrderBy(r => r.S("id"), StringComparer.Ordinal)
                .Where(r => named != null ? named.Contains(r.S("id")) : r.O("vanilla").D("won") >= r.D("floor") && r.O("variant").D("won") - r.O("vanilla").D("won") > flag).ToList();
            var data = c.Data("variant");
            var jobs = new List<JobSpec>();
            foreach (var r in rows)
            {
                string cid = r.S("id"); int crown = (int)r.L("crown");
                var cp = c.Checkpoint(cid);
                var ids = new HashSet<int>();
                foreach (int number in Scenario.BattleNumbers(cp))
                    foreach (var (enemy, _) in data.FindFixed(cp.Str("Floor"), number).Enemies) ids.Add(enemy);
                foreach (var m in mults)
                {
                    var changes = new Obj();
                    foreach (int id in ids) changes.Set(id.ToString(), new Obj { { "hp", Math.Floor(data.Enemies[id].Hp * m) } });
                    jobs.Add(Jb.Make(c, "variant", cid, runs: runs, crown: crown, name: cid + "|" + m, enemyChanges: changes));
                }
            }
            var done = c.Run(jobs);
            Trials.Say(c, runs + " battles; crown of postgame-compare; wins % / length of the won fights; vanilla > variant > variant with foe HP times " + string.Join(", ", mults));
            int k = 0;
            foreach (var r in rows)
            {
                var cells = new List<string>();
                foreach (var m in mults)
                {
                    var res = done[k++].Runs; var won = res.Where(x => x.Won).ToList();
                    cells.Add((100.0 * won.Count / res.Length).ToString("0") + "% / " + (won.Count > 0 ? won.Average(x => x.Time).ToString("0.0") : "-"));
                }
                Func<Obj, string> f = o => (o.D("won") * 100).ToString("0") + "% / " + (Py.Truthy(o.Get("time")) ? o.D("time").ToString("0.0") : "-");
                Trials.Say(c, r.S("id") + " " + Py.Str(r.Get("boss")) + " | crown " + r.L("crown") + " | " + f(r.O("vanilla")) + " > " + f(r.O("variant")) + " > " + string.Join(" > ", cells));
            }
        }
    }
}
