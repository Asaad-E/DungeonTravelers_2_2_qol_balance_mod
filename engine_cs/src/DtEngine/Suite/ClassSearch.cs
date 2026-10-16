using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>dtcli class-search [stage] [scan runs] [confirm runs] [checkpoints, comma separated, or *] [boss|random|all]
    /// [enemy changes on the variant, as 1036.hp=8800,1037.atk=200]: every party of the classes of a stage (a class
    /// may repeat; no more members of a line than characters of that line have joined), vanilla and variant, at every story boss of the stage at its
    /// reference level and on a row of random battles of each floor of the stage. A wide scan, then the candidates again at more runs: a new dominant
    /// party (wins high and the fight much shorter than the median party, where vanilla did not allow it) and a party that falls from vanilla.
    /// Not part of the suite: a mass test on demand. Configuration: section class_search of data_tables/measure_config.json. Output:
    /// measures/CLASS_SEARCH_&lt;STAGE&gt;.md and build/class_search/&lt;stage&gt;.json.</summary>
    public static class ClassSearch
    {
        sealed class Fig { public double Won, Time = double.NaN, Low; }

        sealed class Target
        {
            public string Id, Cid, Context, Floor;
            public int Size;
            public List<List<string>> Parties = new List<List<string>>();      // classes of each party
            public List<Fig> Vanilla = new List<Fig>(), Variant = new List<Fig>();
            public double Median, BestVanillaTime = double.NaN;
        }

        sealed class Candidate
        {
            public Target T;
            public int Party;
            public string Kind;      // "dominant" or "drop"
            public Fig Vanilla, Variant;
            public bool Confirmed;
        }

        static Fig Figures(JobResult r)
        {
            var won = r.Runs.Where(x => x.Won).ToList();
            return new Fig
            {
                Won = (double)won.Count / r.Runs.Length,
                Time = won.Count > 0 ? Py.Sum(won.Select(x => x.Time)) / won.Count : double.NaN,
                Low = Py.Sum(r.Runs.Select(x => x.LowestHp)) / r.Runs.Length,
            };
        }

        /// <summary>Every multiset of the classes of the given size whose count of members of each line stays within the limits.</summary>
        static List<List<string>> Multisets(List<string> classes, Dictionary<string, string> lineOf, Dictionary<string, int> limits, int size)
        {
            var found = new List<List<string>>();
            var pick = new List<string>();
            var used = new Dictionary<string, int>();
            void Walk(int from)
            {
                if (pick.Count == size) { found.Add(new List<string>(pick)); return; }
                for (int i = from; i < classes.Count; i++)
                {
                    string line = lineOf[classes[i]];
                    int n = used.GetValueOrDefault(line);
                    if (n >= limits.GetValueOrDefault(line)) continue;
                    used[line] = n + 1; pick.Add(classes[i]);
                    Walk(i);
                    pick.RemoveAt(pick.Count - 1); used[line] = n;
                }
            }
            Walk(0);
            return found;
        }

        static JobSpec Job(Ctx c, Target t, List<string> roles, string side, int runs, long seed, int chain, long chainSeed, string name, Obj changes)
        {
            Obj enemies = null, options = null;
            if (t.Context == "random")
            {
                var sc = c.Sc("variant");
                enemies = Jb.Chain(sc.WalkedZones(t.Floor, sc.ReferenceLevels()[t.Cid].level).Select(z => z.Name), chainSeed, chain);
                options = new Obj { { "random_battle", true } };
            }
            return Jb.Make(c, side, t.Cid, roles: roles, runs: runs, seed: seed, enemies: enemies, options: options, name: name,
                           enemyChanges: side == "variant" ? changes : null);
        }

        /// <summary>"1036.hp=8800,1037.atk=200": the stats of enemy records set on the variant for this search, as the job field enemy_changes.</summary>
        static Obj Changes(string text)
        {
            var o = new Obj();
            if (string.IsNullOrWhiteSpace(text)) return o;
            foreach (var part in text.Split(',').Select(x => x.Trim()).Where(x => x.Length > 0))
            {
                int dot = part.IndexOf('.'), eq = part.IndexOf('=');
                if (dot <= 0 || eq <= dot) throw new InvalidOperationException("enemy change '" + part + "': write it as id.field=value");
                string id = part.Substring(0, dot).Trim(), field = part.Substring(dot + 1, eq - dot - 1).Trim();
                double value = double.Parse(part.Substring(eq + 1).Trim(), System.Globalization.CultureInfo.InvariantCulture);
                if (!o.Has(id)) o.Set(id, new Obj());
                ((Obj)o.Get(id)).Set(field, value);
            }
            return o;
        }

        public static void Run(Ctx c, string[] args)
        {
            var cfg = c.In("class_search");
            var stageCfg = cfg.A("stages").Cast<Obj>().ToList();
            string stageName = args.Length > 0 ? args[0] : stageCfg[0].S("name");
            var st = stageCfg.FirstOrDefault(s => s.S("name") == stageName) ?? throw new InvalidOperationException("no stage " + stageName + " in class_search");
            int scanRuns = args.Length > 1 ? int.Parse(args[1]) : (int)Py.Num(cfg.Get("scan_runs"));
            int confirmRuns = args.Length > 2 ? int.Parse(args[2]) : (int)Py.Num(cfg.Get("confirm_runs"));
            var only = args.Length > 3 && args[3] != "*" ? new HashSet<string>(args[3].Split(',').Select(x => x.Trim())) : null;
            string contextArg = args.Length > 4 ? args[4] : "all";
            if (contextArg != "all" && contextArg != "boss" && contextArg != "random") throw new InvalidOperationException("context must be boss, random or all");
            string changesText = args.Length > 5 ? args[5] : "";
            var changes = Changes(changesText);
            int chain = (int)Py.Num(cfg.Get("chain"));
            long seed = (long)Py.Num(cfg.Get("seed")), confirmSeed = (long)Py.Num(cfg.Get("confirm_seed")), chainSeed = (long)Py.Num(cfg.Get("chain_seed"));
            int batch = (int)Py.Num(cfg.Get("batch"));
            var contexts = cfg.A("contexts").Select(x => (string)x).Where(x => contextArg == "all" || x == contextArg).ToList();
            var data = c.Data("variant");
            var sc = c.Sc("variant");
            var levels = sc.ReferenceLevels();

            // the classes of the stage, each played through one role: the role named after the class, else the first of RoleOrder that has it
            string column = st.S("column");
            var roleOf = new Dictionary<string, string>();
            var lineOf = new Dictionary<string, string>();
            foreach (var role in c.Setup.RoleOrder)
            {
                string cls = c.Setup.Roles[role].Str(column);
                if (string.IsNullOrEmpty(cls)) continue;
                if (!roleOf.ContainsKey(cls) || string.Equals(role, cls, StringComparison.OrdinalIgnoreCase)) roleOf[cls] = role;
                lineOf[cls] = c.Setup.Roles[role].Str("Base class");
            }
            var classes = roleOf.Keys.OrderBy(x => x, StringComparer.Ordinal).ToList();
            var baseOf = data.Characters.ToDictionary(ch => ch.Name, ch => data.ClassName(ch.BaseClass));

            // the targets: each boss of the stage and, once for each floor and level, a row of random battles of it
            var targets = new List<Target>();
            var floors = new HashSet<string>();
            foreach (var cp in c.Setup.Checkpoints)
            {
                string cid = cp.Str("ID");
                if (!cid.StartsWith(cfg.S("story_prefix")) || !levels.ContainsKey(cid)) continue;
                int level = levels[cid].level;
                if (level < Py.Num(st.Get("low")) || level > Py.Num(st.Get("high"))) continue;
                if (only != null && !only.Contains(cid)) continue;
                var joined = sc.Available(cp.Str("Chapter")).Where(baseOf.ContainsKey).ToList();
                var limits = joined.GroupBy(n => baseOf[n]).ToDictionary(g => g.Key, g => g.Count());
                int size = Math.Min((int)Py.Num(cfg.Get("party_size")), joined.Count);
                var parties = Multisets(classes, lineOf, limits, size);
                if (contexts.Contains("boss"))
                    targets.Add(new Target { Id = cid, Cid = cid, Context = "boss", Floor = cp.Str("Floor"), Size = size, Parties = parties });
                string floorKey = cp.Str("Floor") + "|" + level;
                if (contexts.Contains("random") && sc.WalkedZones(cp.Str("Floor"), level).Count > 0 && floors.Add(floorKey))
                    targets.Add(new Target { Id = cid + " random", Cid = cid, Context = "random", Floor = cp.Str("Floor"), Size = size, Parties = parties });
            }
            long cells = targets.Sum(t => (long)t.Parties.Count);
            c.Say("class-search " + stageName + ": " + targets.Count + " targets, " + cells + " party cells, " + (2 * cells * scanRuns) + " runs at " + scanRuns + " a cell");
            if (scanRuns == 0) return;     // 0 runs: the plan only

            // the scan, in batches of cells
            var all = targets.SelectMany(t => t.Parties.Select((p, i) => (t, i))).ToList();
            foreach (var t in targets) { t.Vanilla.AddRange(new Fig[t.Parties.Count]); t.Variant.AddRange(new Fig[t.Parties.Count]); }
            for (int start = 0; start < all.Count; start += batch)
            {
                var part = all.Skip(start).Take(batch).ToList();
                var jobs = new List<JobSpec>();
                foreach (var (t, i) in part)
                {
                    var roles = t.Parties[i].Select(x => roleOf[x]).ToList();
                    jobs.Add(Job(c, t, roles, "vanilla", scanRuns, seed, chain, chainSeed, t.Id + "|" + i + "|vanilla", changes));
                    jobs.Add(Job(c, t, roles, "variant", scanRuns, seed, chain, chainSeed, t.Id + "|" + i + "|variant", changes));
                }
                var done = c.Run(jobs);
                for (int k = 0; k < part.Count; k++) { var (t, i) = part[k]; t.Vanilla[i] = Figures(done[2 * k]); t.Variant[i] = Figures(done[2 * k + 1]); }
                done.Clear(); jobs.Clear();
                c.Say("class-search: " + Math.Min(start + batch, all.Count) + " of " + all.Count + " cells");
            }

            // the candidates of each target
            double win = cfg.D("win"), time = cfg.D("time"), vanillaWin = cfg.D("vanilla_win"), vanillaLength = cfg.D("vanilla_length"), drop = cfg.D("drop");
            var candidates = new List<Candidate>();
            foreach (var t in targets)
            {
                var times = t.Variant.Where(f => !double.IsNaN(f.Time)).Select(f => f.Time).ToList();
                t.Median = times.Count > 0 ? Py.Median(times) : double.NaN;
                var strong = t.Vanilla.Where(f => f.Won >= win && !double.IsNaN(f.Time)).Select(f => f.Time).ToList();
                t.BestVanillaTime = strong.Count > 0 ? strong.Min() : double.NaN;
                for (int i = 0; i < t.Parties.Count; i++)
                {
                    var v = t.Vanilla[i]; var m = t.Variant[i];
                    if (Dominant(m, v, t.Median, win, time, vanillaWin, vanillaLength)) candidates.Add(new Candidate { T = t, Party = i, Kind = "dominant", Vanilla = v, Variant = m });
                    if (v.Won - m.Won >= drop) candidates.Add(new Candidate { T = t, Party = i, Kind = "drop", Vanilla = v, Variant = m });
                }
            }
            int cap = (int)Py.Num(cfg.Get("confirm_max"));
            var chosen = candidates.Where(x => x.Kind == "dominant").OrderBy(x => x.Variant.Time / x.T.Median).Take(cap)
                .Concat(candidates.Where(x => x.Kind == "drop").OrderByDescending(x => x.Vanilla.Won - x.Variant.Won).Take(cap)).ToList();
            if (chosen.Count > 0 && confirmRuns > 0)
            {
                var jobs = new List<JobSpec>();
                foreach (var x in chosen)
                {
                    var roles = x.T.Parties[x.Party].Select(n => roleOf[n]).ToList();
                    jobs.Add(Job(c, x.T, roles, "vanilla", confirmRuns, confirmSeed, chain, chainSeed, x.T.Id + "|" + x.Party + "|vanilla|confirm", changes));
                    jobs.Add(Job(c, x.T, roles, "variant", confirmRuns, confirmSeed, chain, chainSeed, x.T.Id + "|" + x.Party + "|variant|confirm", changes));
                }
                var done = c.Run(jobs);
                for (int k = 0; k < chosen.Count; k++)
                {
                    var x = chosen[k];
                    x.Vanilla = Figures(done[2 * k]); x.Variant = Figures(done[2 * k + 1]);
                    x.Confirmed = x.Kind == "dominant" ? Dominant(x.Variant, x.Vanilla, x.T.Median, win, time, vanillaWin, vanillaLength) : x.Vanilla.Won - x.Variant.Won >= drop;
                }
            }
            Report(c, cfg, stageName, targets, candidates, chosen, scanRuns, confirmRuns, chain, changesText);
        }

        static bool Dominant(Fig m, Fig v, double median, double win, double time, double vanillaWin, double vanillaLength) =>
            m.Won >= win && !double.IsNaN(m.Time) && m.Time < time * median
            && (v.Won < vanillaWin || double.IsNaN(v.Time) || v.Time >= vanillaLength * m.Time);

        static string Len(double x) => double.IsNaN(x) ? "-" : Py.F(x, 1);

        static string Party(List<string> p) => string.Join(", ", p);

        static void Report(Ctx c, Obj cfg, string stage, List<Target> targets, List<Candidate> candidates, List<Candidate> chosen, int scanRuns, int confirmRuns, int chain,
                           string changesText)
        {
            double win = cfg.D("win"), drop = cfg.D("drop");
            var dominant = chosen.Where(x => x.Kind == "dominant" && x.Confirmed).ToList();
            var drops = chosen.Where(x => x.Kind == "drop" && x.Confirmed).ToList();
            var text = new List<string>
            {
                "# Every party of the " + stage + " classes (generated)", "",
                "Generated by `dtcli class-search " + stage + "`. Do not edit. Every party of the classes of the stage (a class may repeat; no more members of a "
                    + "line than characters of that line have joined by the checkpoint; each class played through the role named after it, else the first role "
                    + "of RoleOrder that has it), vanilla and variant with the same seeds, at every story boss of the stage at its reference level (boss) and on "
                    + "a row of " + chain + " random battles of each floor of the stage (random). Scan: " + scanRuns + " runs a cell; the candidates again at "
                    + confirmRuns + " runs (at most " + Py.Num(cfg.Get("confirm_max")) + " of each kind). Section class_search of data_tables/measure_config.json."
                    + (string.IsNullOrWhiteSpace(changesText) ? "" : " **Trial: the variant played with the enemy changes " + changesText + ".**"), "",
                "Dominant: variant wins " + Py.Pct(win, 0) + " or more in under " + Py.Pct(cfg.D("time"), 0) + " of the median length of the target's parties, "
                    + "where vanilla won under " + Py.Pct(cfg.D("vanilla_win"), 0) + " or took " + Py.F(cfg.D("vanilla_length"), 1) + " times as long. Drop: variant "
                    + "wins " + Py.Pct(drop, 0) + " points fewer than vanilla. Beyond vanilla: shorter than the shortest vanilla party of the target that wins "
                    + Py.Pct(win, 0) + " or more.", "",
                "**" + targets.Count + " targets, " + targets.Sum(t => t.Parties.Count) + " party cells. Scan: " + candidates.Count(x => x.Kind == "dominant")
                    + " dominant and " + candidates.Count(x => x.Kind == "drop") + " drop candidates. "
                    + (confirmRuns == 0 ? "Not confirmed (0 confirmation runs): the scan only.**" : "Confirmed: " + dominant.Count + " dominant ("
                    + dominant.Count(x => !double.IsNaN(x.T.BestVanillaTime) && x.Variant.Time < x.T.BestVanillaTime) + " beyond vanilla), " + drops.Count + " drops.**"), "",
                "## Confirmed dominant parties", "",
                "| Target | Party | Vanilla: wins / length / lowest HP | Variant: wins / length / lowest HP | Of the median | Shortest vanilla party | Beyond vanilla |",
                "|---|---|---|---|---|---|---|",
            };
            foreach (var x in dominant.OrderBy(x => x.Variant.Time / x.T.Median))
                text.Add("| " + x.T.Id + " | " + Party(x.T.Parties[x.Party]) + " | " + Py.Pct(x.Vanilla.Won, 0) + " / " + Len(x.Vanilla.Time) + " / " + Py.Pct(x.Vanilla.Low, 0)
                         + " | " + Py.Pct(x.Variant.Won, 0) + " / " + Len(x.Variant.Time) + " / " + Py.Pct(x.Variant.Low, 0) + " | " + Py.Pct(x.Variant.Time / x.T.Median, 0)
                         + " | " + Len(x.T.BestVanillaTime) + " | " + (!double.IsNaN(x.T.BestVanillaTime) && x.Variant.Time < x.T.BestVanillaTime ? "yes" : "no") + " |");
            text.AddRange(new[] { "", "## Confirmed drops", "", "| Target | Party | Vanilla: wins / length / lowest HP | Variant: wins / length / lowest HP |", "|---|---|---|---|" });
            foreach (var x in drops.OrderByDescending(x => x.Vanilla.Won - x.Variant.Won))
                text.Add("| " + x.T.Id + " | " + Party(x.T.Parties[x.Party]) + " | " + Py.Pct(x.Vanilla.Won, 0) + " / " + Len(x.Vanilla.Time) + " / " + Py.Pct(x.Vanilla.Low, 0)
                         + " | " + Py.Pct(x.Variant.Won, 0) + " / " + Len(x.Variant.Time) + " / " + Py.Pct(x.Variant.Low, 0) + " |");

            // each class: the mean share of wins of the parties that hold it, over every target; and its worst target
            text.AddRange(new[] { "", "## Classes", "", "Mean share of wins of the parties that hold the class (scan), vanilla > variant, and the target where it falls most.", "",
                                  "| Class | Cells | Vanilla | Variant | Change | Worst target | Change there |", "|---|---|---|---|---|---|---|" });
            var names = targets.SelectMany(t => t.Parties.SelectMany(p => p)).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();
            foreach (var cls in names)
            {
                double van = 0, var = 0; long n = 0;
                string worst = "-"; double worstChange = double.PositiveInfinity;
                foreach (var t in targets)
                {
                    double tv = 0, tm = 0; int tn = 0;
                    for (int i = 0; i < t.Parties.Count; i++)
                        if (t.Parties[i].Contains(cls)) { tv += t.Vanilla[i].Won; tm += t.Variant[i].Won; tn++; }
                    if (tn == 0) continue;
                    van += tv; var += tm; n += tn;
                    if ((tm - tv) / tn < worstChange) { worstChange = (tm - tv) / tn; worst = t.Id; }
                }
                text.Add("| " + cls + " | " + n + " | " + Py.Pct(van / n, 1) + " | " + Py.Pct(var / n, 1) + " | " + Py.F(100 * (var - van) / n, 1, true) + " | " + worst
                         + " | " + Py.F(100 * worstChange, 1, true) + " |");
            }

            text.AddRange(new[] { "", "## Targets", "", "| Target | Parties | Median length (variant) | Best variant party: wins / length | Shortest vanilla party at " + Py.Pct(win, 0) + " | Dominant candidates | Drop candidates |",
                                  "|---|---|---|---|---|---|---|" });
            foreach (var t in targets)
            {
                int best = Enumerable.Range(0, t.Parties.Count).OrderByDescending(i => t.Variant[i].Won).ThenBy(i => double.IsNaN(t.Variant[i].Time) ? double.MaxValue : t.Variant[i].Time).FirstOrDefault();
                string bestText = t.Parties.Count == 0 ? "-" : Party(t.Parties[best]) + ": " + Py.Pct(t.Variant[best].Won, 0) + " / " + Len(t.Variant[best].Time);
                text.Add("| " + t.Id + " | " + t.Parties.Count + " | " + Len(t.Median) + " | " + bestText + " | " + Len(t.BestVanillaTime) + " | "
                         + candidates.Count(x => x.T == t && x.Kind == "dominant") + " | " + candidates.Count(x => x.T == t && x.Kind == "drop") + " |");
            }
            c.WriteText(c.Path("measures", "CLASS_SEARCH_" + stage.ToUpperInvariant() + ".md"), M.Lines(text), true);

            var raw = new Obj
            {
                { "stage", stage }, { "scan_runs", (long)scanRuns }, { "confirm_runs", (long)confirmRuns },
                { "targets", Jb.L(targets.Select(t => (object)new Obj { { "id", t.Id }, { "median", double.IsNaN(t.Median) ? null : (object)t.Median },
                    { "parties", Jb.L(t.Parties.Select((p, i) => (object)new Obj { { "classes", Jb.L(p.Cast<object>()) }, { "vanilla", FigObj(t.Vanilla[i]) }, { "variant", FigObj(t.Variant[i]) } })) } })) },
                { "confirmed", Jb.L(chosen.Select(x => (object)new Obj { { "target", x.T.Id }, { "kind", x.Kind }, { "classes", Jb.L(x.T.Parties[x.Party].Cast<object>()) },
                    { "vanilla", FigObj(x.Vanilla) }, { "variant", FigObj(x.Variant) }, { "confirmed", x.Confirmed } })) },
            };
            c.WriteText(c.Path("build", "class_search", stage + ".json"), PyJson.Dump(raw), true);
            c.Say("class-search: written measures/CLASS_SEARCH_" + stage.ToUpperInvariant() + ".md (" + dominant.Count + " dominant, " + drops.Count + " drops confirmed)");
        }

        static Obj FigObj(Fig f) => new Obj { { "won", f.Won }, { "time", double.IsNaN(f.Time) ? null : (object)f.Time }, { "lowest_hp", f.Low } };
    }
}
