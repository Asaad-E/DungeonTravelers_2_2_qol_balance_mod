using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>dtcli walk-parties [battles] [rows]: the walk of random-battles for each party: the reference party of the checkpoint and
    /// each party of BatteryParties, rows of random battles in a row at the floor of each checkpoint with one bag for the row, vanilla and
    /// the variant on the same seeds. On demand, not part of the suite; writes build/walk_parties.json (tools/walk_parties_chart.py draws it).</summary>
    public static class WalkParties
    {
        public static void Run(Ctx c, string[] args)
        {
            var cfg = c.In("random_battles");
            int chain = args.Length > 0 ? int.Parse(args[0]) : (int)cfg.L("chain");
            int rows = args.Length > 1 ? int.Parse(args[1]) : c.SetInt("check_runs");
            int ahead = (int)cfg.L("ahead");
            var parties = new List<(string name, List<string> roles)> { ("Reference", null) };
            parties.AddRange(c.Setup.Battery.Select(b => (b.name, b.roles.ToList())));
            var ids = DifficultyCurve.Checkpoints(c);
            var jobs = new List<JobSpec>();
            var index = new Dictionary<(string, string, string), int>();
            foreach (var (name, roles) in parties)
                foreach (var cid in ids)
                    foreach (var side in new[] { "vanilla", "variant" })
                    {
                        var zones = RandomBattles.ZonesOf(c, side, cid, ahead);
                        if (zones == null) continue;
                        index[(name, cid, side)] = jobs.Count;
                        jobs.Add(Jb.Make(c, side, cid, roles: roles, runs: rows, name: name + "|" + cid + "|" + side,
                                         enemies: Jb.Chain(zones.Select(z => z.Name), 11, chain)));
                    }
            c.Say("walk-parties: " + jobs.Count + " jobs of " + rows + " rows of " + chain + " battles");
            var done = c.Run(jobs);
            Obj Figures(string name, string cid, string side)
            {
                if (!index.TryGetValue((name, cid, side), out int at)) return null;
                var res = done[at].Runs;
                var s = Summary.Of(res.ToList());
                return new Obj
                {
                    { "won", s.Won }, { "time", s.Time.HasValue ? (object)(s.Time.Value / chain) : null }, { "lowest_hp", s.LowestHp },
                    { "tp_left", Py.Sum(res.Select(r => r.TpLeft)) / res.Length },
                };
            }
            var outObj = new Obj
            {
                { "battles", (long)chain }, { "rows", (long)rows },
                { "checkpoints", Jb.L(ids.Cast<object>()) },
                { "parties", Jb.L(parties.Select(p => (object)new Obj
                    {
                        { "name", p.name }, { "roles", p.roles == null ? null : Jb.L(p.roles.Cast<object>()) },
                        { "cells", Jb.L(ids.Select(cid => (object)new Obj { { "id", cid }, { "vanilla", Figures(p.name, cid, "vanilla") }, { "variant", Figures(p.name, cid, "variant") } })) },
                    })) },
            };
            string path = c.Path("build", "walk_parties.json");
            c.WriteText(path, PyJson.Dump(outObj, 1), false);
            c.Say("walk-parties: written " + path);
        }
    }
}
