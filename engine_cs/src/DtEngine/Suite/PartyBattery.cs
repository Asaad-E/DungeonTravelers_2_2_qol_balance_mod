using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>tools/party_battery.py: each party of the sheet BatteryParties at each boss of Settings battery_checkpoints, vanilla and variant;
    /// docs/generated/PARTY_BATTERY.md.</summary>
    public static class PartyBattery
    {
        const double Z95 = 1.96;

        public static List<string> Checkpoints(Ctx c) =>
            Py.Str(c.Setup.Settings["battery_checkpoints"]).Split(';').Select(x => x.Trim()).Where(x => x.Length > 0).ToList();

        public static (double low, double high) Wilson(long wins, long runs)
        {
            if (runs == 0) return (0.0, 1.0);
            double p = (double)wins / runs, z2 = Z95 * Z95;
            double centre = (p + z2 / (2 * runs)) / (1 + z2 / runs);
            double half = Z95 * Math.Sqrt(p * (1 - p) / runs + z2 / (4.0 * runs * runs)) / (1 + z2 / runs);
            return (Math.Max(0.0, centre - half), Math.Min(1.0, centre + half));
        }

        public static void Run(Ctx c)
        {
            string dir = c.Path("docs", "generated", "party_battery");
            int runs = c.SetInt("battery_runs");
            var cids = Checkpoints(c);
            var tasks = new List<(string cid, string name, string side)>();
            foreach (var cid in cids) foreach (var b in c.Setup.Battery) foreach (var side in new[] { "vanilla", "variant" }) tasks.Add((cid, b.name, side));
            var roles = c.Setup.Battery.ToDictionary(b => b.name, b => b.roles);
            var jobs = tasks.Select(t => Jb.Make(c, t.side, t.cid, roles: roles[t.name], runs: runs, name: t.cid + "|" + t.name + "|" + t.side)).ToList();
            var played = c.Run(jobs);
            var cells = new Dictionary<(string, string, string), Obj>();
            for (int k = 0; k < tasks.Count; k++)
            {
                var (cid, name, side) = tasks[k];
                var res = played[k].Runs;
                var won = res.Where(r => r.Won).ToList();
                var party = c.Sc(side).PartyOfRoles(cid, roles[name], null, null).Where(u => u.Kind == Kind.Member).ToList();
                cells[(cid, name, side)] = new Obj
                {
                    { "runs", (long)res.Length }, { "wins", (long)won.Count },
                    { "time", won.Count > 0 ? (object)(Py.Sum(won.Select(r => r.Time)) / won.Count) : null },
                    { "lowest_hp", Py.Sum(res.Select(r => r.LowestHp)) / res.Length },
                    { "tp_left", won.Count > 0 ? (object)(Py.Sum(won.Select(r => r.TpLeft)) / won.Count) : null },
                    { "members", Jb.L(party.Select(u => (object)(u.Name + " (" + (u.HasRole ? u.Role : "None") + ")"))) },
                };
            }
            var rows = new List<object>();
            foreach (var cid in cids)
                foreach (var b in c.Setup.Battery)
                    rows.Add(new Obj { { "id", cid }, { "party", b.name }, { "vanilla", cells[(cid, b.name, "vanilla")] }, { "variant", cells[(cid, b.name, "variant")] } });
            Directory.CreateDirectory(dir);
            M.ClearFolder(dir);
            c.WriteText(Path.Combine(dir, "part_1.json"), PyJson.Dump(rows), false);
        }

        static double Share(Obj cell) => (double)cell.L("wins") / cell.L("runs");

        static Obj Best(Dictionary<(string, string), Obj> rows, string cid, List<string> names, string side)
        {
            Obj best = null; double top = 0;
            foreach (var n in names)
            {
                if (!rows.TryGetValue((cid, n), out var row)) continue;
                var cell = row.O(side);
                if (best == null || Share(cell) > top) { best = cell; top = Share(cell); }
            }
            return best;
        }

        public static void Report(Ctx c)
        {
            string dir = c.Path("docs", "generated", "party_battery");
            var all = new List<Obj>();
            foreach (var name in M.Listing(dir)) all.AddRange(((List<object>)c.ReadJson(Path.Combine(dir, name))).Cast<Obj>());
            var rows = new Dictionary<(string, string), Obj>();
            foreach (var r in all) rows[(r.S("id"), r.S("party"))] = r;
            if (rows.Count == 0) { c.Say("no parts: run \"all\" first"); return; }
            var groups = new List<(string archetype, List<string> names)>();
            foreach (var b in c.Setup.Battery)
            {
                var g = groups.FirstOrDefault(x => x.archetype == b.archetype);
                if (g.names == null) groups.Add((b.archetype, new List<string> { b.name })); else g.names.Add(b.name);
            }
            var partyNames = c.Setup.Battery.Select(b => b.name).ToList();
            var every = Checkpoints(c).Where(cid => partyNames.Any(n => rows.ContainsKey((cid, n)))).ToList();
            long runs = rows.Values.First().O("vanilla").L("runs");
            var floor = every.ToDictionary(cid => cid, cid => M.Floor(c, cid));
            var boss = c.Setup.Checkpoints.ToDictionary(r => r.Str("ID"), r => r.Str("Boss (as the story page names it)"));
            var data = c.Data("vanilla");
            var names = new Dictionary<string, string>();
            foreach (var cp in c.Setup.Checkpoints)
            {
                string id = cp.Str("ID");
                if (!every.Contains(id)) continue;
                var ids = new List<int>();
                foreach (int n in Scenario.BattleNumbers(cp))
                    foreach (var b in data.Fixed)
                        if (b.Floor == cp.Str("Floor") && b.Number == n) foreach (var (e, _) in b.Enemies) ids.Add(e);
                EnemyRec top = null;
                foreach (var e in ids) { var rec = data.Enemies[e]; if (top == null || rec.Hp > top.Hp) top = rec; }
                names[id] = top.Name;
            }
            var above = new Dictionary<string, int>();
            foreach (var side in new[] { "vanilla", "variant" })
            {
                int n = 0;
                foreach (var cid in every) foreach (var g in groups) if (Share(Best(rows, cid, g.names, side)) >= floor[cid]) n++;
                above[side] = n;
            }
            int cellCount = every.Count * groups.Count;
            var width = Wilson(runs / 2, runs);
            var lines = new List<string>
            {
                "# The battery of parties (generated)", "",
                "Generated by `dtcli party-battery`. Do not edit. Parties: sheet `BatteryParties` of `sim_setup.xlsx`; bosses: Settings `battery_checkpoints`; "
                    + runs + " battles a cell, the same seeds in vanilla and on the variant. At " + runs + " battles a share near 50% is known to about "
                    + Py.F(100 * (width.high - width.low) / 2, 0) + " points either way (95%). Floor: the least win share the class the guide gives the boss allows.", "",
                "**Archetype and boss pairs at or above the floor: " + above["vanilla"] + " of " + cellCount + " in vanilla, " + above["variant"] + " of " + cellCount + " on the variant.**", "",
                "## Archetypes: win share, vanilla > variant", "",
                "An archetype with several parties shows the best of them on each side. **Bold**: the variant is below the floor.", "",
                "| Checkpoint | Boss | Floor | " + string.Join(" | ", groups.Select(g => g.archetype)) + " |", "|---|---|---|" + string.Concat(groups.Select(g => "---|")),
            };
            foreach (var cid in every)
            {
                var parts = new List<string>();
                foreach (var g in groups)
                {
                    var v = Best(rows, cid, g.names, "vanilla"); var m = Best(rows, cid, g.names, "variant");
                    string text = Py.Pct(Share(v), 0) + " > " + Py.Pct(Share(m), 0);
                    parts.Add(Share(m) < floor[cid] ? "**" + text + "**" : text);
                }
                lines.Add("| " + cid + " | " + (names.TryGetValue(cid, out var nm) ? nm : boss.GetValueOrDefault(cid, "")) + " | " + Py.Pct(floor[cid], 0) + " | " + string.Join(" | ", parts) + " |");
            }
            lines.AddRange(new[] { "", "## Every party on the variant: win share and its 95% interval", "",
                "| Checkpoint | " + string.Join(" | ", partyNames) + " |", "|---|" + string.Concat(partyNames.Select(x => "---|")) });
            foreach (var cid in every)
            {
                var parts = new List<string>();
                foreach (var n in partyNames)
                {
                    var m = rows[(cid, n)].O("variant");
                    var (low, high) = Wilson(m.L("wins"), m.L("runs"));
                    parts.Add(Py.Pct(Share(m), 0) + " (" + Py.Pct(low, 0) + " - " + Py.Pct(high, 0) + ")");
                }
                lines.Add("| " + cid + " | " + string.Join(" | ", parts) + " |");
            }
            lines.AddRange(new[] { "", "## Every party in vanilla: win share", "",
                "| Checkpoint | " + string.Join(" | ", partyNames) + " |", "|---|" + string.Concat(partyNames.Select(x => "---|")) });
            foreach (var cid in every)
                lines.Add("| " + cid + " | " + string.Join(" | ", partyNames.Select(n => Py.Pct(Share(rows[(cid, n)].O("vanilla")), 0))) + " |");
            lines.AddRange(new[] { "", "## Who stands in each party", "", "The first and the last boss of the battery where five members have joined.", "",
                "| Party | Checkpoint | Members (role) |", "|---|---|---|" });
            var full = every.Where(cid => partyNames.All(n => rows[(cid, n)].O("variant").A("members").Count >= 5)).ToList();
            foreach (var n in partyNames)
            {
                var pick = full.Count > 0 ? new List<string> { full[0], full[full.Count - 1] } : every.Take(1).ToList();
                foreach (var cid in pick)
                    lines.Add("| " + n + " | " + cid + " | " + string.Join(", ", rows[(cid, n)].O("variant").A("members").Select(x => (string)x)) + " |");
            }
            var shortParties = new List<(string cid, string n, int k)>();
            foreach (var cid in every) foreach (var n in partyNames)
                {
                    int k = rows[(cid, n)].O("variant").A("members").Count;
                    if (k < 5) shortParties.Add((cid, n, k));
                }
            if (shortParties.Count > 0)
            {
                var set = shortParties.Select(s => s.cid + " (" + s.k + " members)").Distinct().ToList();
                set.Sort(string.CompareOrdinal);
                lines.Add("");
                lines.Add("Fewer than five characters have joined at: " + string.Join(", ", set) + ".");
            }
            c.WriteText(c.Path("docs", "generated", "PARTY_BATTERY.md"), M.Lines(lines), false);
        }
    }
}
