using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>dtcli support-battery [runs] [stage]: each support and tank class of each stage, in the last place of each party of the sheet BatteryParties,
    /// against the same party with the control role in that place, at every story boss of the stage, on a row of random battles of its floor and
    /// on that row followed by the boss (HP, TP and items carried, nothing healed between fights but what the game heals). Many figures, from the
    /// record of each battle. Configuration: section support_battery of data_tables/measure_config.json. Output: docs/generated/SUPPORT_BATTERY.md
    /// and docs/generated/support_battery/part_1.json. Balance variant.</summary>
    public static class SupportBattery
    {
        static readonly string[] Keys = { "won", "reached", "time", "lowest_hp", "hp_left", "tp_left", "deaths", "items", "healing", "taken" };

        sealed class Cell
        {
            public string Stage, Cid, Party, Context, Role;
            public Dictionary<string, double> Fig;
        }

        /// <summary>The figures of a job: means over its runs (time over the won runs).</summary>
        static Dictionary<string, double> Figures(JobResult r, int walk)
        {
            var f = Keys.ToDictionary(k => k, k => 0.0);
            int n = r.Runs.Length, won = 0;
            double time = 0;
            foreach (var run in r.Runs)
            {
                if (run.Won) { won++; time += run.Time; }
                f["reached"] += walk > 0 ? (run.Parts.Count > walk || (run.Parts.Count == walk && run.Won) ? 1 : 0) : 1;
                f["lowest_hp"] += run.LowestHp;
                f["hp_left"] += run.HpLeft;
                f["tp_left"] += run.TpLeft;
                foreach (var part in run.Parts)
                {
                    var rec = part.Record;
                    if (rec == null) continue;
                    for (int i = 0; i < rec.Deaths.Count; i++) if (Ours(rec.Deaths.Keys[i].Unit)) f["deaths"] += rec.Deaths.Values[i];
                    for (int i = 0; i < rec.ItemsUsed.Count; i++) if (Ours(rec.ItemsUsed.Keys[i].Unit)) f["items"] += rec.ItemsUsed.Values[i];
                    for (int i = 0; i < rec.Healing.Count; i++) if (Ours(rec.Healing.Keys[i].Unit)) f["healing"] += rec.Healing.Values[i];
                    for (int i = 0; i < rec.Damage.Count; i++) if (rec.Damage.Keys[i].Unit.Side == Unit.ENEMIES) f["taken"] += rec.Damage.Values[i];
                }
            }
            foreach (var k in Keys) if (k != "won" && k != "time") f[k] /= n;
            f["won"] = (double)won / n;
            f["time"] = won > 0 ? time / won : double.NaN;
            return f;
        }

        static bool Ours(Unit u) => u.Side == Unit.PARTY;

        public static void Run(Ctx c, string[] args)
        {
            var cfg = c.In("support_battery");
            var data = c.Data("variant");
            var sc = c.Sc("variant");
            int runs = args.Length > 0 ? int.Parse(args[0]) : (int)Py.Num(cfg.Get("runs"));
            int walk = (int)Py.Num(cfg.Get("walk"));
            long seed = (long)Py.Num(cfg.Get("chain_seed"));
            string control = cfg.S("control");
            var kinds = new HashSet<string>(cfg.A("kinds").Select(x => (string)x));
            var byClass = c.In("class_kinds");
            var levels = sc.ReferenceLevels();
            var story = c.Setup.Checkpoints.Select(r => r.Str("ID")).Where(id => id.StartsWith(cfg.S("story_prefix")) && levels.ContainsKey(id)).ToList();

            // the roles of each stage: one for each support or tank class of the stage (the first of RoleOrder), and the control
            var plan = new List<(string stage, string column, List<string> cids, List<(string role, string cls, string kind)> roles)>();
            foreach (var st in cfg.A("stages").Cast<Obj>())
            {
                if (args.Length > 1 && st.S("name") != args[1]) continue;     // a second argument: one stage only
                string column = st.S("column");
                var cids = story.Where(id => levels[id].level >= Py.Num(st.Get("low")) && levels[id].level <= Py.Num(st.Get("high"))).ToList();
                var roles = new List<(string, string, string)>();
                var seen = new HashSet<string>();
                foreach (var role in c.Setup.RoleOrder)
                {
                    string cls = c.Setup.Roles[role].Str(column);
                    string kind = byClass.Has(cls) ? Py.Str(byClass.Get(cls)) : "attacker";
                    if (role == control) roles.Add((role, cls, "control"));
                    else if (kinds.Contains(kind) && seen.Add(cls)) roles.Add((role, cls, kind));
                }
                if (cids.Count > 0) plan.Add((st.S("name"), column, cids, roles));
            }

            var contexts = cfg.A("contexts").Select(x => (string)x).ToList();
            var cells = new List<Cell>();
            foreach (var p in plan)
                foreach (var cid in p.cids)
                {
                    bool zones = sc.WalkedZones(c.Checkpoint(cid).Str("Floor"), levels[cid].level).Count > 0;
                    foreach (var b in c.Setup.Battery)
                        foreach (var context in contexts)
                        {
                            if (context != "boss" && !zones) continue;
                            foreach (var r in p.roles) cells.Add(new Cell { Stage = p.stage, Cid = cid, Party = b.name, Context = context, Role = r.role });
                        }
                }

            int batch = (int)Py.Num(cfg.Get("batch"));
            for (int start = 0; start < cells.Count; start += batch)
            {
                var part = cells.Skip(start).Take(batch).ToList();
                var jobs = part.Select(cell => Job(c, cell, runs, walk, seed)).ToList();
                var done = c.Run(jobs);
                for (int k = 0; k < part.Count; k++) part[k].Fig = Figures(done[k], part[k].Context == "boss" ? 0 : walk);
                done.Clear(); jobs.Clear();
                c.Say("support-battery: " + Math.Min(start + batch, cells.Count) + " of " + cells.Count + " cells at " + runs + " runs");
            }
            Report(c, cfg, plan.Select(p => (p.stage, p.cids, p.roles)).ToList(), cells, runs, walk, control);
        }

        static JobSpec Job(Ctx c, Cell cell, int runs, int walk, long seed)
        {
            var sc = c.Sc("variant");
            var cp = c.Checkpoint(cell.Cid);
            var roles = c.Setup.Battery.First(b => b.name == cell.Party).roles;
            var recipe = new Obj
            {
                { "drop_last", true }, { "items", "first_kept" },
                { "tested", Jb.L(new Obj { { "role", cell.Role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true } }) },
            };
            Obj enemies = null, options = null;
            if (cell.Context != "boss")
            {
                var zones = sc.WalkedZones(cp.Str("Floor"), c.Sc("variant").ReferenceLevels()[cell.Cid].level).Select(z => z.Name);
                enemies = Jb.Chain(zones, seed, walk);
                if (cell.Context == "walk_boss") enemies.Set("then_checkpoint", true);
                options = new Obj { { "random_battle", true } };
            }
            return Jb.Make(c, "variant", cell.Cid, roles: roles, runs: runs, recipe: recipe, enemies: enemies, options: options, record: true,
                           name: cell.Stage + "|" + cell.Cid + "|" + cell.Party + "|" + cell.Context + "|" + cell.Role);
        }

        static string Signed(double x, int digits) => double.IsNaN(x) ? "-" : Py.F(x, digits, true);

        static void Report(Ctx c, Obj cfg, List<(string stage, List<string> cids, List<(string role, string cls, string kind)> roles)> plan,
                           List<Cell> cells, int runs, int walk, string control)
        {
            double w = cfg.D("wins"), h = cfg.D("hp"), d = cfg.D("deaths"), it = cfg.D("items"), good = cfg.D("good_share");
            var at = cells.ToDictionary(x => (x.Stage, x.Cid, x.Party, x.Context, x.Role));
            var rows = new List<object>();
            var text = new List<string>
            {
                "# Supports and tanks in every party (generated)", "",
                "Generated by `dtcli support-battery`. Do not edit. Balance variant, " + runs + " runs a cell, the same seeds for every role. Each support and tank "
                    + "class of a stage (sheet ClassKinds; one role for each class, the first of RoleOrder) in the last place of each party of the sheet BatteryParties, "
                    + "against the same party with the " + control + " in that place (the control). Contexts: boss, the fights of the checkpoint with everything full; "
                    + "walk, a row of " + walk + " random battles of its floor; walk_boss, that row and then the boss. HP, TP and items are carried from fight to fight and "
                    + "nothing is healed between them but what the game heals (Generous Heart). Section support_battery of data_tables/measure_config.json.", "",
                "Each figure is the mean over the cells of the role minus the control in the same cell: wins and reached (the share of rows that reach the boss) in "
                    + "points, length of the won fights in %, lowest HP, HP and TP left in points of the party's maximum, deaths, items and healing a run, damage taken "
                    + "in % of the control's. A cell serves: wins +" + Py.Pct(w, 0) + ", or wins not down that much and lowest HP +" + Py.Pct(h, 0) + ", or "
                    + Py.F(d, 1) + " deaths fewer, or " + Py.F(it, 1) + " items fewer, and none of those four worse by as much (worse: one of them is). Serves as support: " + Py.Pct(good, 0) + " or more of its cells serve; niche: "
                    + "some do; does not serve: none.", "",
            };
            foreach (var (stage, cids, roles) in plan)
            {
                text.Add("## " + stage + " (" + cids.Count + " bosses: " + string.Join(", ", cids) + ")");
                text.Add("");
                text.Add("| Role | Class | Kind | Context | Cells | Wins | Reached | Length | Lowest HP | HP left | TP left | Deaths | Items | Healing | Taken | Serve | Worse | Verdict |");
                text.Add("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|");
                foreach (var (role, cls, kind) in roles)
                {
                    if (kind == "control") continue;
                    var mine = cells.Where(x => x.Stage == stage && x.Role == role).ToList();
                    int serving = 0;
                    var byContext = new List<string>();
                    foreach (var context in mine.Select(x => x.Context).Distinct().ToList().Concat(new[] { "all" }))
                    {
                        var set = context == "all" ? mine : mine.Where(x => x.Context == context).ToList();
                        var pairs = set.Select(x => (x, at[(x.Stage, x.Cid, x.Party, x.Context, control)])).ToList();
                        double Mean(Func<Dictionary<string, double>, Dictionary<string, double>, double> f)
                        {
                            var vals = pairs.Select(p => f(p.x.Fig, p.Item2.Fig)).Where(v => !double.IsNaN(v)).ToList();
                            return vals.Count > 0 ? vals.Average() : double.NaN;
                        }
                        bool Worse(Dictionary<string, double> a, Dictionary<string, double> b) =>
                            a["won"] - b["won"] <= -w || b["lowest_hp"] - a["lowest_hp"] >= h || a["deaths"] - b["deaths"] >= d || a["items"] - b["items"] >= it;
                        bool Serves(Dictionary<string, double> a, Dictionary<string, double> b)
                        {
                            if (a["won"] - b["won"] >= w) return true;
                            if (Worse(a, b)) return false;
                            return a["lowest_hp"] - b["lowest_hp"] >= h || b["deaths"] - a["deaths"] >= d || b["items"] - a["items"] >= it;
                        }
                        int s = pairs.Count(p => Serves(p.x.Fig, p.Item2.Fig));
                        int worse = pairs.Count(p => Worse(p.x.Fig, p.Item2.Fig) && !Serves(p.x.Fig, p.Item2.Fig));
                        if (context == "all") serving = s;
                        string verdict = context != "all" ? "" : (double)s / Math.Max(1, pairs.Count) >= good ? "serves" : s > 0 ? "niche" : "does not serve";
                        text.Add("| " + role + " | " + cls + " | " + kind + " | " + context + " | " + pairs.Count + " | "
                                 + Signed(100 * Mean((a, b) => a["won"] - b["won"]), 0) + " | " + Signed(100 * Mean((a, b) => a["reached"] - b["reached"]), 0) + " | "
                                 + Signed(100 * Mean((a, b) => double.IsNaN(a["time"]) || double.IsNaN(b["time"]) ? double.NaN : a["time"] / b["time"] - 1), 0) + " | "
                                 + Signed(100 * Mean((a, b) => a["lowest_hp"] - b["lowest_hp"]), 0) + " | " + Signed(100 * Mean((a, b) => a["hp_left"] - b["hp_left"]), 0) + " | "
                                 + Signed(100 * Mean((a, b) => a["tp_left"] - b["tp_left"]), 0) + " | " + Signed(Mean((a, b) => a["deaths"] - b["deaths"]), 2) + " | "
                                 + Signed(Mean((a, b) => a["items"] - b["items"]), 2) + " | " + Signed(Mean((a, b) => a["healing"] - b["healing"]), 0) + " | "
                                 + Signed(100 * Mean((a, b) => b["taken"] > 0 ? a["taken"] / b["taken"] - 1 : double.NaN), 0) + " | "
                                 + Py.Pct((double)s / Math.Max(1, pairs.Count), 0) + " | " + Py.Pct((double)worse / Math.Max(1, pairs.Count), 0) + " | " + verdict + " |");
                    }
                    rows.Add(new Obj { { "stage", stage }, { "role", role }, { "class", cls }, { "kind", kind }, { "cells", (long)mine.Count }, { "serve", (long)serving } });
                }
                text.Add("");
            }
            string dir = c.Path("docs", "generated", "support_battery");
            Directory.CreateDirectory(dir);
            M.ClearFolder(dir);
            var raw = cells.Select(x => (object)new Obj { { "stage", x.Stage }, { "checkpoint", x.Cid }, { "party", x.Party }, { "context", x.Context }, { "role", x.Role },
                                                          { "figures", Jb.Dict(x.Fig.Select(kv => new KeyValuePair<string, object>(kv.Key, double.IsNaN(kv.Value) ? null : (object)kv.Value))) } }).ToList();
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(new Obj { { "verdicts", rows }, { "cells", raw } }), false);
            c.WriteText(c.Path("docs", "generated", "SUPPORT_BATTERY.md"), M.Lines(text), false);
            c.Say("support-battery: written docs/generated/SUPPORT_BATTERY.md");
        }
    }
}
