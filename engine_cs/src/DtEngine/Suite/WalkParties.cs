using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>dtcli walk-parties [key=value ...]: the walk of random-battles for each party: the reference party of the checkpoint and each
    /// party of BatteryParties, rows of random battles in a row at the floor of each checkpoint with one bag for the row, vanilla and the
    /// variant on the same seeds. On demand, not part of the suite; writes build/walk_parties[_OUT].json (tools/walk_parties_chart.py draws it).
    /// battles=N (default section random_battles), rows=N (Settings check_runs), cids=C26,C32 (default every checkpoint of the curve),
    /// parties=Reference+Meta (default all), enemy=atk*1.1,def*1.1,hp*1.1 (the random enemies of the floors of those checkpoints, on the
    /// variant side only, scaled), trial="Skill:e1*1.1; class:Witch:int*1.25" (as skill-battery, on the variant side), out=NAME.</summary>
    public static class WalkParties
    {
        public static void Run(Ctx c, string[] args)
        {
            var cfg = c.In("random_battles");
            int chain = (int)cfg.L("chain"), rows = c.SetInt("check_runs"), ahead = (int)cfg.L("ahead");
            List<string> only = null, onlyParties = null;
            string enemy = "", outName = "", trial = "";
            foreach (var a in args)
            {
                int eq = a.IndexOf('=');
                if (eq < 0) throw new InvalidOperationException("walk-parties: write the arguments as key=value (" + a + ")");
                string key = a.Substring(0, eq).Trim(), value = a.Substring(eq + 1).Trim();
                switch (key)
                {
                    case "battles": chain = int.Parse(value); break;
                    case "rows": rows = int.Parse(value); break;
                    case "cids": only = value.Split(',').Select(x => x.Trim()).ToList(); break;
                    case "parties": onlyParties = value.Split('+').Select(x => x.Trim()).ToList(); break;
                    case "enemy": enemy = value; break;
                    case "out": outName = value; break;
                    case "trial": trial = value; break;
                    default: throw new InvalidOperationException("walk-parties: unknown argument " + key + " (battles, rows, cids, parties, enemy, trial, out)");
                }
            }
            var parties = new List<(string name, List<string> roles)> { ("Reference", null) };
            parties.AddRange(c.Setup.Battery.Select(b => (b.name, b.roles.ToList())));
            if (onlyParties != null) parties = parties.Where(p => onlyParties.Contains(p.name)).ToList();
            var ids = DifficultyCurve.Checkpoints(c);
            if (only != null) ids = ids.Where(only.Contains).ToList();

            // the variant side, with the random enemies of the floors of the chosen checkpoints scaled
            string variant = "variant";
            var baseData = trial.Length > 0 ? SkillBattery.WithTrial(c.Data("variant"), trial) : c.Data("variant");
            if (trial.Length > 0 && enemy.Length == 0) variant = c.AddSide(baseData);
            if (enemy.Length > 0)
            {
                var scale = enemy.Split(',').Select(x => x.Trim().Split('*')).ToDictionary(x => x[0].Trim(), x => double.Parse(x[1], CultureInfo.InvariantCulture));
                var data = baseData;
                string[] stats = { "atk", "def", "int", "res", "dex", "agi" };
                var touched = new HashSet<int>();
                foreach (var cid in ids)
                    foreach (var z in RandomBattles.ZonesOf(c, "variant", cid, ahead) ?? new List<FloorZone>())
                        foreach (var f in z.Formations) foreach (var (id, _) in f.Enemies) touched.Add(id);
                var changes = new List<(int id, Dictionary<string, double> fields)>();
                foreach (int id in touched.Where(data.Enemies.ContainsKey))
                {
                    var rec = data.Enemies[id];
                    var fields = new Dictionary<string, double>();
                    foreach (var kv in scale)
                    {
                        int s = Array.IndexOf(stats, kv.Key);
                        if (kv.Key == "hp") fields["hp"] = Math.Round(rec.Hp * kv.Value);
                        else if (s >= 0) fields[kv.Key] = Math.Round(rec.Stats[s] * kv.Value);
                        else throw new InvalidOperationException("walk-parties: enemy stat " + kv.Key + " (hp, atk, def, int, res, dex, agi)");
                    }
                    changes.Add((id, fields));
                }
                variant = c.AddSide(data.WithEnemyStats(changes));
                c.Say("walk-parties: " + changes.Count + " random enemies scaled (" + enemy + ")");
            }

            var jobs = new List<JobSpec>();
            var index = new Dictionary<(string, string, string), int>();
            foreach (var (name, roles) in parties)
                foreach (var cid in ids)
                    foreach (var side in new[] { "vanilla", "variant" })
                    {
                        var zones = RandomBattles.ZonesOf(c, side, cid, ahead);
                        if (zones == null) continue;
                        index[(name, cid, side)] = jobs.Count;
                        jobs.Add(Jb.Make(c, side == "variant" ? variant : side, cid, roles: roles, runs: rows, name: name + "|" + cid + "|" + side,
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
                { "battles", (long)chain }, { "rows", (long)rows }, { "enemy", enemy }, { "trial", trial },
                { "checkpoints", Jb.L(ids.Cast<object>()) },
                { "parties", Jb.L(parties.Select(p => (object)new Obj
                    {
                        { "name", p.name }, { "roles", p.roles == null ? null : Jb.L(p.roles.Cast<object>()) },
                        { "cells", Jb.L(ids.Select(cid => (object)new Obj { { "id", cid }, { "vanilla", Figures(p.name, cid, "vanilla") }, { "variant", Figures(p.name, cid, "variant") } })) },
                    })) },
            };
            string path = c.Path("build", "walk_parties" + (outName.Length > 0 ? "_" + outName : "") + ".json");
            c.WriteText(path, PyJson.Dump(outObj, 1), false);
            c.Say("walk-parties: written " + path);
        }
    }
}
