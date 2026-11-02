using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        /// <summary>dtcli seat-trial CHECKPOINTS RUNS ROLES [attacker]: each role in the parties of BatteryParties, in the place of her own kind
        /// (as class-stages does) and, with "attacker", in the place of the last attacker; wins and length of the won fights, mean over the parties.</summary>
        public static void SeatTrial(Ctx c, string[] a)
        {
            var cids = a[0].Split(';'); int runs = int.Parse(a[1]); var roles = a[2].Split(',').Select(x => x.Trim()).ToList();
            var parties = c.Setup.Battery.Select(b => b.name).ToList();
            Trials.Say(c, runs + " battles per party; wins % / length of the won fights; own place > place of the last attacker");
            foreach (var cid in cids)
            {
                foreach (var role in roles)
                {
                    var w = new double[2]; var l = new double[2]; var n = new int[2]; int used = 0;
                    foreach (var party in parties)
                    {
                        RunResult[][] pair;
                        try { var d = c.Run(new[] { false, true }.Select(seat => ClassStages.BatteryJob(c, cid, role, party, runs, seat)).ToList()); pair = new[] { d[0].Runs, d[1].Runs }; }
                        catch (System.InvalidOperationException) { continue; } // the characters of the role are already in this party
                        used++;
                        for (int seat = 0; seat < 2; seat++)
                        {
                            var res = pair[seat];
                            var won = res.Where(r => r.Won).ToList();
                            w[seat] += 100.0 * won.Count / res.Length;
                            if (won.Count > 0) { l[seat] += won.Average(r => r.Time); n[seat]++; }
                        }
                    }
                    Trials.Say(c, cid + " | " + role + " | parties " + used + " | " + (w[0] / System.Math.Max(1, used)).ToString("0") + "% > " + (w[1] / System.Math.Max(1, used)).ToString("0") + "% | "
                                  + (n[0] > 0 ? (l[0] / n[0]).ToString("0.0") : "-") + " > " + (n[1] > 0 ? (l[1] / n[1]).ToString("0.0") : "-"));
                }
            }
        }
    }
}
