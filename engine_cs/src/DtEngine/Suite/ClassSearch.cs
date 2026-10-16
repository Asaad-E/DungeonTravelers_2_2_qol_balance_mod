using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>dtcli class-search [STAGE] [preset=NAME] [scan=N] [confirm=N] [cids=C34,C38] [context=boss|random|all] [with=Class*2+Class]
    /// [without=Class+Class] [sample=N] [compare=vanilla|variant] [enemy=1036.hp=8800,1037.def=201] [trial=Skill:e191*1.1;Skill:turns+1] [kit=N]
    /// [out=NAME]: preset= takes the arguments of a preset of the configuration (presets), the others given override them; without= leaves out
    /// the parties that hold any of those classes; sample= plays N parties of each target drawn at random (seed of the configuration). Every party of the classes of a stage (a class may
    /// repeat; no more members of a line than characters of that line have joined; with= keeps the parties that hold those classes), played on two
    /// sides with the same seeds, A and B: vanilla and the variant, or with compare=variant the variant and the variant with the trial values (enemy=
    /// stats of enemies and trial= values of skills go to B; kit= is the bag of both). At every story boss of the stage at its reference level and on a
    /// row of random battles of each floor. A wide scan, then the candidates again at more runs: a dominant party of B (wins high, the fight much
    /// shorter than the median, where A did not allow it), a party that falls from A; and each class, A against B. Not part of the suite.
    /// Configuration: section class_search of data_tables/measure_config.json. Output: measures/CLASS_SEARCH_&lt;STAGE&gt;[_&lt;OUT&gt;].md and
    /// build/class_search/&lt;stage&gt;[_&lt;out&gt;].json.</summary>
    public static class ClassSearch
    {
        sealed class Fig { public double Won, Time = double.NaN, Low; }

        sealed class Target
        {
            public string Id, Cid, Context, Floor;
            public int Size;
            public List<List<string>> Parties = new List<List<string>>();      // classes of each party
            public List<Fig> A = new List<Fig>(), B = new List<Fig>();
            public double Median, BestATime = double.NaN;
        }

        sealed class Candidate
        {
            public Target T;
            public int Party;
            public string Kind;      // "dominant" or "drop"
            public Fig A, B;
            public bool Confirmed;
        }

        /// <summary>The choices of one search, from the arguments.</summary>
        sealed class Plan
        {
            public string Stage, Context = "all", Compare = "vanilla", Enemy = "", Trial = "", Out = "";
            public int? Scan, Confirm, Kit;
            public HashSet<string> Cids;
            public List<(string cls, int count)> With = new List<(string, int)>();
            public List<string> Without = new List<string>();
            public int? Sample;
            public string Preset = "";
            public string SideA, SideB;
            public Obj EnemyChanges = new Obj();
            public string LabelA => Compare == "variant" ? "variant" : "vanilla";
            public string LabelB => Compare == "variant" ? "trial" : "variant";
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

        /// <summary>"1036.hp=8800,1037.def=201": stats of enemy records, as the job field enemy_changes.</summary>
        static Obj EnemyChanges(string text)
        {
            var o = new Obj();
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

        static Plan Parse(Ctx c, Obj cfg, string[] args)
        {
            // the arguments as key=value pairs: those of the preset first, then the ones given (a later key wins)
            var given = new List<(string key, string value)>();
            string stage = args.Length > 0 && !args[0].Contains('=') ? args[0] : null;
            foreach (var arg in args.Skip(stage != null ? 1 : 0))
            {
                int eq = arg.IndexOf('=');
                if (eq <= 0) throw new InvalidOperationException("argument '" + arg + "': write it as key=value");
                given.Add((arg.Substring(0, eq).Trim(), arg.Substring(eq + 1).Trim()));
            }
            var pairs = new List<(string key, string value)>();
            var preset = given.Where(g => g.key == "preset").Select(g => g.value).LastOrDefault();
            if (preset != null)
            {
                var presets = cfg.O("presets");
                if (!presets.Has(preset)) throw new InvalidOperationException("no preset " + preset + " (presets: " + string.Join(", ", presets.Keys) + ")");
                foreach (var kv in (Obj)presets.Get(preset))
                {
                    if (kv.Key == "stage") stage = stage ?? Py.Str(kv.Value);
                    else if (kv.Key != "about") pairs.Add((kv.Key, Py.Str(kv.Value)));
                }
            }
            pairs.AddRange(given.Where(g => g.key != "preset"));
            var p = new Plan { Stage = stage ?? cfg.A("stages").Cast<Obj>().First().S("name"), Preset = preset ?? "" };
            foreach (var (key, value) in pairs)
            {
                switch (key)
                {
                    case "scan": p.Scan = int.Parse(value); break;
                    case "confirm": p.Confirm = int.Parse(value); break;
                    case "cids": p.Cids = new HashSet<string>(value.Split(',').Select(x => x.Trim()).Where(x => x.Length > 0)); break;
                    case "context": p.Context = value; break;
                    case "compare": p.Compare = value; break;
                    case "enemy": p.Enemy = value; break;
                    case "trial": p.Trial = value; break;
                    case "kit": p.Kit = int.Parse(value); break;
                    case "out": p.Out = value; break;
                    case "sample": p.Sample = int.Parse(value); break;
                    case "without": p.Without = value.Split('+').Select(x => x.Trim()).Where(x => x.Length > 0).ToList(); break;
                    case "with":
                        foreach (var part in value.Split('+').Select(x => x.Trim()).Where(x => x.Length > 0))
                        {
                            int star = part.LastIndexOf('*');
                            p.With.Add(star > 0 ? (part.Substring(0, star).Trim(), int.Parse(part.Substring(star + 1))) : (part, 1));
                        }
                        break;
                    default: throw new InvalidOperationException("unknown argument '" + key + "' (preset, scan, confirm, cids, context, with, without, sample, compare, enemy, trial, kit, out)");
                }
            }
            if (p.Context != "all" && p.Context != "boss" && p.Context != "random") throw new InvalidOperationException("context must be boss, random or all");
            if (p.Compare != "vanilla" && p.Compare != "variant") throw new InvalidOperationException("compare must be vanilla or variant");
            if (p.Compare == "variant" && p.Enemy.Length == 0 && p.Trial.Length == 0) throw new InvalidOperationException("compare=variant needs enemy= or trial=");
            p.EnemyChanges = EnemyChanges(p.Enemy);
            p.SideA = p.Compare == "variant" ? "variant" : "vanilla";
            p.SideB = p.Trial.Length > 0 ? c.AddSide(SkillBattery.WithTrial(c.Data("variant"), p.Trial)) : "variant";
            return p;
        }

        static JobSpec Job(Ctx c, Plan p, Target t, List<string> roles, bool sideB, int runs, long seed, int chain, long chainSeed, string name)
        {
            Obj enemies = null, options = null;
            if (t.Context == "random")
            {
                var sc = c.Sc("variant");
                enemies = Jb.Chain(sc.WalkedZones(t.Floor, sc.ReferenceLevels()[t.Cid].level).Select(z => z.Name), chainSeed, chain);
                options = new Obj { { "random_battle", true } };
            }
            return Jb.Make(c, sideB ? p.SideB : p.SideA, t.Cid, roles: roles, runs: runs, seed: seed, enemies: enemies, options: options, name: name, kit: p.Kit,
                           enemyChanges: sideB ? p.EnemyChanges : null);
        }

        static bool Holds(List<string> party, List<(string cls, int count)> with, List<string> without) =>
            with.All(w => party.Count(x => x == w.cls) >= w.count) && !without.Any(party.Contains);

        /// <summary>n parties of the list drawn at random with the seed (the same draw every time), in their order.</summary>
        static List<List<string>> Sampled(List<List<string>> parties, int n, long seed)
        {
            if (n >= parties.Count) return parties;
            var rng = new Random((int)(seed % int.MaxValue));
            var keys = parties.Select((x, i) => (key: rng.NextDouble(), i)).OrderBy(k => k.key).Take(n).Select(k => k.i).OrderBy(i => i).ToList();
            return keys.Select(i => parties[i]).ToList();
        }

        public static void Run(Ctx c, string[] args)
        {
            var cfg = c.In("class_search");
            var p = Parse(c, cfg, args);
            var st = cfg.A("stages").Cast<Obj>().FirstOrDefault(s => s.S("name") == p.Stage) ?? throw new InvalidOperationException("no stage " + p.Stage + " in class_search");
            int scanRuns = p.Scan ?? (int)Py.Num(cfg.Get("scan_runs"));
            int confirmRuns = p.Confirm ?? (int)Py.Num(cfg.Get("confirm_runs"));
            int chain = (int)Py.Num(cfg.Get("chain"));
            long seed = (long)Py.Num(cfg.Get("seed")), confirmSeed = (long)Py.Num(cfg.Get("confirm_seed")), chainSeed = (long)Py.Num(cfg.Get("chain_seed"));
            int batch = (int)Py.Num(cfg.Get("batch"));
            var contexts = cfg.A("contexts").Select(x => (string)x).Where(x => p.Context == "all" || x == p.Context).ToList();
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
            foreach (var w in p.With) if (!roleOf.ContainsKey(w.cls)) throw new InvalidOperationException("with: no class " + w.cls + " at the stage " + p.Stage);
            foreach (var w in p.Without) if (!roleOf.ContainsKey(w)) throw new InvalidOperationException("without: no class " + w + " at the stage " + p.Stage);
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
                if (p.Cids != null && !p.Cids.Contains(cid)) continue;
                var joined = sc.Available(cp.Str("Chapter")).Where(baseOf.ContainsKey).ToList();
                var limits = joined.GroupBy(n => baseOf[n]).ToDictionary(g => g.Key, g => g.Count());
                int size = Math.Min((int)Py.Num(cfg.Get("party_size")), joined.Count);
                var parties = Multisets(classes, lineOf, limits, size).Where(x => Holds(x, p.With, p.Without)).ToList();
                if (p.Sample.HasValue) parties = Sampled(parties, p.Sample.Value, seed);
                if (contexts.Contains("boss"))
                    targets.Add(new Target { Id = cid, Cid = cid, Context = "boss", Floor = cp.Str("Floor"), Size = size, Parties = parties });
                string floorKey = cp.Str("Floor") + "|" + level;
                if (contexts.Contains("random") && sc.WalkedZones(cp.Str("Floor"), level).Count > 0 && floors.Add(floorKey))
                    targets.Add(new Target { Id = cid + " random", Cid = cid, Context = "random", Floor = cp.Str("Floor"), Size = size, Parties = parties });
            }
            long cells = targets.Sum(t => (long)t.Parties.Count);
            c.Say("class-search " + p.Stage + " (" + p.LabelA + " > " + p.LabelB + "): " + targets.Count + " targets, " + cells + " party cells, " + (2 * cells * scanRuns)
                  + " runs at " + scanRuns + " a cell");
            if (scanRuns == 0) return;     // scan=0: the plan only

            // the scan, in batches of cells
            var all = targets.SelectMany(t => t.Parties.Select((x, i) => (t, i))).ToList();
            foreach (var t in targets) { t.A.AddRange(new Fig[t.Parties.Count]); t.B.AddRange(new Fig[t.Parties.Count]); }
            for (int start = 0; start < all.Count; start += batch)
            {
                var part = all.Skip(start).Take(batch).ToList();
                var jobs = new List<JobSpec>();
                foreach (var (t, i) in part)
                {
                    var roles = t.Parties[i].Select(x => roleOf[x]).ToList();
                    jobs.Add(Job(c, p, t, roles, false, scanRuns, seed, chain, chainSeed, t.Id + "|" + i + "|A"));
                    jobs.Add(Job(c, p, t, roles, true, scanRuns, seed, chain, chainSeed, t.Id + "|" + i + "|B"));
                }
                var done = c.Run(jobs);
                for (int k = 0; k < part.Count; k++) { var (t, i) = part[k]; t.A[i] = Figures(done[2 * k]); t.B[i] = Figures(done[2 * k + 1]); }
                done.Clear(); jobs.Clear();
                c.Say("class-search: " + Math.Min(start + batch, all.Count) + " of " + all.Count + " cells");
            }

            // the candidates of each target
            double win = cfg.D("win"), time = cfg.D("time"), vanillaWin = cfg.D("vanilla_win"), vanillaLength = cfg.D("vanilla_length"), drop = cfg.D("drop");
            var candidates = new List<Candidate>();
            foreach (var t in targets)
            {
                var times = t.B.Where(f => !double.IsNaN(f.Time)).Select(f => f.Time).ToList();
                t.Median = times.Count > 0 ? Py.Median(times) : double.NaN;
                var strong = t.A.Where(f => f.Won >= win && !double.IsNaN(f.Time)).Select(f => f.Time).ToList();
                t.BestATime = strong.Count > 0 ? strong.Min() : double.NaN;
                for (int i = 0; i < t.Parties.Count; i++)
                {
                    var a = t.A[i]; var b = t.B[i];
                    if (Dominant(b, a, t.Median, win, time, vanillaWin, vanillaLength)) candidates.Add(new Candidate { T = t, Party = i, Kind = "dominant", A = a, B = b });
                    if (a.Won - b.Won >= drop) candidates.Add(new Candidate { T = t, Party = i, Kind = "drop", A = a, B = b });
                }
            }
            int cap = (int)Py.Num(cfg.Get("confirm_max"));
            var chosen = candidates.Where(x => x.Kind == "dominant").OrderBy(x => x.B.Time / x.T.Median).Take(cap)
                .Concat(candidates.Where(x => x.Kind == "drop").OrderByDescending(x => x.A.Won - x.B.Won).Take(cap)).ToList();
            if (chosen.Count > 0 && confirmRuns > 0)
            {
                var jobs = new List<JobSpec>();
                foreach (var x in chosen)
                {
                    var roles = x.T.Parties[x.Party].Select(n => roleOf[n]).ToList();
                    jobs.Add(Job(c, p, x.T, roles, false, confirmRuns, confirmSeed, chain, chainSeed, x.T.Id + "|" + x.Party + "|A|confirm"));
                    jobs.Add(Job(c, p, x.T, roles, true, confirmRuns, confirmSeed, chain, chainSeed, x.T.Id + "|" + x.Party + "|B|confirm"));
                }
                var done = c.Run(jobs);
                for (int k = 0; k < chosen.Count; k++)
                {
                    var x = chosen[k];
                    x.A = Figures(done[2 * k]); x.B = Figures(done[2 * k + 1]);
                    x.Confirmed = x.Kind == "dominant" ? Dominant(x.B, x.A, x.T.Median, win, time, vanillaWin, vanillaLength) : x.A.Won - x.B.Won >= drop;
                }
            }
            Report(c, cfg, p, targets, candidates, chosen, scanRuns, confirmRuns, chain);
        }

        static bool Dominant(Fig b, Fig a, double median, double win, double time, double vanillaWin, double vanillaLength) =>
            b.Won >= win && !double.IsNaN(b.Time) && b.Time < time * median
            && (a.Won < vanillaWin || double.IsNaN(a.Time) || a.Time >= vanillaLength * b.Time);

        static string Len(double x) => double.IsNaN(x) ? "-" : Py.F(x, 1);

        static string Party(List<string> p) => string.Join(", ", p);

        static double MedianOr(IEnumerable<double> xs) { var l = xs.Where(x => !double.IsNaN(x)).ToList(); return l.Count > 0 ? Py.Median(l) : double.NaN; }

        static void Report(Ctx c, Obj cfg, Plan p, List<Target> targets, List<Candidate> candidates, List<Candidate> chosen, int scanRuns, int confirmRuns, int chain)
        {
            double win = cfg.D("win"), drop = cfg.D("drop"), fastShare = cfg.D("fast_share");
            string A = p.LabelA, B = p.LabelB;
            var dominant = chosen.Where(x => x.Kind == "dominant" && x.Confirmed).ToList();
            var drops = chosen.Where(x => x.Kind == "drop" && x.Confirmed).ToList();
            var trial = new List<string>();
            if (p.Trial.Length > 0) trial.Add("skills " + p.Trial);
            if (p.Enemy.Length > 0) trial.Add("enemies " + p.Enemy);
            if (p.Kit.HasValue) trial.Add("kit " + p.Kit + " on both sides");
            if (p.With.Count > 0) trial.Add("parties with " + string.Join(" + ", p.With.Select(w => w.cls + (w.count > 1 ? " x" + w.count : ""))));
            if (p.Without.Count > 0) trial.Add("parties without " + string.Join(", ", p.Without));
            if (p.Sample.HasValue) trial.Add("a sample of " + p.Sample + " parties a target");
            if (p.Preset.Length > 0) trial.Add("preset " + p.Preset);
            var text = new List<string>
            {
                "# Every party of the " + p.Stage + " classes (generated)", "",
                "Generated by `dtcli class-search " + p.Stage + "`. Do not edit. Every party of the classes of the stage (a class may repeat; no more members of a "
                    + "line than characters of that line have joined by the checkpoint; each class played through the role named after it, else the first role "
                    + "of RoleOrder that has it), on two sides with the same seeds: A " + A + ", B " + B + "; at every story boss of the stage at its reference level "
                    + "(boss) and on a row of " + chain + " random battles of each floor of the stage (random). Scan: " + scanRuns + " runs a cell; the candidates again at "
                    + confirmRuns + " runs (at most " + Py.Num(cfg.Get("confirm_max")) + " of each kind). Section class_search of data_tables/measure_config.json.", "",
                trial.Count > 0 ? "**This search: " + string.Join("; ", trial) + ".**" + (p.Trial.Length > 0 || p.Enemy.Length > 0 ? " Skill and enemy values go to B, which is not built." : "")
                                : "Every party, no trial values.", "",
                "Dominant: B wins " + Py.Pct(win, 0) + " or more in under " + Py.Pct(cfg.D("time"), 0) + " of the median length of the target's parties on B, "
                    + "where A won under " + Py.Pct(cfg.D("vanilla_win"), 0) + " or took " + Py.F(cfg.D("vanilla_length"), 1) + " times as long. Drop: B wins "
                    + Py.Pct(drop, 0) + " points fewer than A. Beyond A: shorter than the shortest party of A at the target that wins " + Py.Pct(win, 0) + " or more.", "",
                "**" + targets.Count + " targets, " + targets.Sum(t => t.Parties.Count) + " party cells. Scan: " + candidates.Count(x => x.Kind == "dominant")
                    + " dominant and " + candidates.Count(x => x.Kind == "drop") + " drop candidates. "
                    + (confirmRuns == 0 ? "Not confirmed (0 confirmation runs): the scan only.**" : "Confirmed: " + dominant.Count + " dominant ("
                    + dominant.Count(x => !double.IsNaN(x.T.BestATime) && x.B.Time < x.T.BestATime) + " beyond A), " + drops.Count + " drops.**"), "",
                "## Confirmed dominant parties", "",
                "| Target | Party | " + A + ": wins / length / lowest HP | " + B + ": wins / length / lowest HP | Of the median | Shortest of A | Beyond A |",
                "|---|---|---|---|---|---|---|",
            };
            foreach (var x in dominant.OrderBy(x => x.B.Time / x.T.Median))
                text.Add("| " + x.T.Id + " | " + Party(x.T.Parties[x.Party]) + " | " + Py.Pct(x.A.Won, 0) + " / " + Len(x.A.Time) + " / " + Py.Pct(x.A.Low, 0)
                         + " | " + Py.Pct(x.B.Won, 0) + " / " + Len(x.B.Time) + " / " + Py.Pct(x.B.Low, 0) + " | " + Py.Pct(x.B.Time / x.T.Median, 0)
                         + " | " + Len(x.T.BestATime) + " | " + (!double.IsNaN(x.T.BestATime) && x.B.Time < x.T.BestATime ? "yes" : "no") + " |");
            text.AddRange(new[] { "", "## Confirmed drops", "", "| Target | Party | " + A + ": wins / length / lowest HP | " + B + ": wins / length / lowest HP |", "|---|---|---|---|" });
            foreach (var x in drops.OrderByDescending(x => x.A.Won - x.B.Won))
                text.Add("| " + x.T.Id + " | " + Party(x.T.Parties[x.Party]) + " | " + Py.Pct(x.A.Won, 0) + " / " + Len(x.A.Time) + " / " + Py.Pct(x.A.Low, 0)
                         + " | " + Py.Pct(x.B.Won, 0) + " / " + Len(x.B.Time) + " / " + Py.Pct(x.B.Low, 0) + " |");

            // each class, A against B: wins, length of the parties that win at the bar, lowest HP, and its share of the fastest parties
            text.AddRange(new[] { "", "## Classes, " + A + " > " + B, "",
                "Over the scan of every target, the parties that hold the class: mean share of wins; median length of those that win " + Py.Pct(win, 0) + " or more; "
                    + "mean lowest HP; and the share of the fastest " + Py.Pct(fastShare, 0) + " of the parties of each target (by length, among those that win "
                    + Py.Pct(win, 0) + " or more) that hold the class. The worst target: where its wins fall most.", "",
                "| Class | Cells | Wins | Length | Lowest HP | Among the fastest | Wins change | Worst target | Change there |", "|---|---|---|---|---|---|---|---|---|" });
            var names = targets.SelectMany(t => t.Parties.SelectMany(x => x)).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();
            List<int> Fastest(Target t, List<Fig> side)
            {
                var ok = Enumerable.Range(0, t.Parties.Count).Where(i => side[i].Won >= win && !double.IsNaN(side[i].Time)).OrderBy(i => side[i].Time).ToList();
                return ok.Take(Math.Max(1, (int)Math.Ceiling(ok.Count * fastShare))).ToList();
            }
            var fastA = targets.ToDictionary(t => t, t => Fastest(t, t.A));
            var fastB = targets.ToDictionary(t => t, t => Fastest(t, t.B));
            foreach (var cls in names)
            {
                double wa = 0, wb = 0, la = 0, lb = 0; long n = 0;
                var lenA = new List<double>(); var lenB = new List<double>();
                int inFastA = 0, inFastB = 0, fastNA = 0, fastNB = 0;
                string worst = "-"; double worstChange = double.PositiveInfinity;
                foreach (var t in targets)
                {
                    double tv = 0, tm = 0; int tn = 0;
                    for (int i = 0; i < t.Parties.Count; i++)
                    {
                        if (!t.Parties[i].Contains(cls)) continue;
                        tv += t.A[i].Won; tm += t.B[i].Won; tn++;
                        la += t.A[i].Low; lb += t.B[i].Low;
                        if (t.A[i].Won >= win) lenA.Add(t.A[i].Time);
                        if (t.B[i].Won >= win) lenB.Add(t.B[i].Time);
                    }
                    inFastA += fastA[t].Count(i => t.Parties[i].Contains(cls)); fastNA += fastA[t].Count;
                    inFastB += fastB[t].Count(i => t.Parties[i].Contains(cls)); fastNB += fastB[t].Count;
                    if (tn == 0) continue;
                    wa += tv; wb += tm; n += tn;
                    if ((tm - tv) / tn < worstChange) { worstChange = (tm - tv) / tn; worst = t.Id; }
                }
                if (n == 0) continue;
                text.Add("| " + cls + " | " + n + " | " + Py.Pct(wa / n, 1) + " > " + Py.Pct(wb / n, 1) + " | " + Len(MedianOr(lenA)) + " > " + Len(MedianOr(lenB))
                         + " | " + Py.Pct(la / n, 0) + " > " + Py.Pct(lb / n, 0) + " | " + Py.Pct(fastNA > 0 ? (double)inFastA / fastNA : 0, 0) + " > "
                         + Py.Pct(fastNB > 0 ? (double)inFastB / fastNB : 0, 0) + " | " + Py.F(100 * (wb - wa) / n, 1, true) + " | " + worst + " | " + Py.F(100 * worstChange, 1, true) + " |");
            }

            text.AddRange(new[] { "", "## Targets", "", "| Target | Parties | Median length (" + B + ") | Best party of " + B + ": wins / length | Shortest of " + A + " at " + Py.Pct(win, 0)
                                  + " | Dominant candidates | Drop candidates |", "|---|---|---|---|---|---|---|" });
            foreach (var t in targets)
            {
                int best = Enumerable.Range(0, t.Parties.Count).OrderByDescending(i => t.B[i].Won).ThenBy(i => double.IsNaN(t.B[i].Time) ? double.MaxValue : t.B[i].Time).FirstOrDefault();
                string bestText = t.Parties.Count == 0 ? "-" : Party(t.Parties[best]) + ": " + Py.Pct(t.B[best].Won, 0) + " / " + Len(t.B[best].Time);
                text.Add("| " + t.Id + " | " + t.Parties.Count + " | " + Len(t.Median) + " | " + bestText + " | " + Len(t.BestATime) + " | "
                         + candidates.Count(x => x.T == t && x.Kind == "dominant") + " | " + candidates.Count(x => x.T == t && x.Kind == "drop") + " |");
            }
            string suffix = p.Out.Length > 0 ? "_" + p.Out : "";
            c.WriteText(c.Path("measures", "CLASS_SEARCH_" + p.Stage.ToUpperInvariant() + suffix.ToUpperInvariant() + ".md"), M.Lines(text), true);

            var raw = new Obj
            {
                { "stage", p.Stage }, { "a", A }, { "b", B }, { "trial", string.Join("; ", trial) }, { "scan_runs", (long)scanRuns }, { "confirm_runs", (long)confirmRuns },
                { "targets", Jb.L(targets.Select(t => (object)new Obj { { "id", t.Id }, { "median", double.IsNaN(t.Median) ? null : (object)t.Median },
                    { "parties", Jb.L(t.Parties.Select((x, i) => (object)new Obj { { "classes", Jb.L(x.Cast<object>()) }, { "a", FigObj(t.A[i]) }, { "b", FigObj(t.B[i]) } })) } })) },
                { "confirmed", Jb.L(chosen.Select(x => (object)new Obj { { "target", x.T.Id }, { "kind", x.Kind }, { "classes", Jb.L(x.T.Parties[x.Party].Cast<object>()) },
                    { "a", FigObj(x.A) }, { "b", FigObj(x.B) }, { "confirmed", x.Confirmed } })) },
            };
            c.WriteText(c.Path("build", "class_search", p.Stage + suffix + ".json"), PyJson.Dump(raw), true);
            c.Say("class-search: written measures/CLASS_SEARCH_" + p.Stage.ToUpperInvariant() + suffix.ToUpperInvariant() + ".md (" + dominant.Count + " dominant, " + drops.Count + " drops confirmed)");
        }

        static Obj FigObj(Fig f) => new Obj { { "won", f.Won }, { "time", double.IsNaN(f.Time) ? null : (object)f.Time }, { "lowest_hp", f.Low } };
    }
}
