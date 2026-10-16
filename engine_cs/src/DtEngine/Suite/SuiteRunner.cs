using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace DtEngine.Suite
{
    /// <summary>The measures of the project that play battles, run on the engine in one process: `dtcli suite` runs them all at once, `dtcli &lt;name&gt;` one.</summary>
    public static class SuiteRunner
    {
        public static List<MeasureDef> All()
        {
            return new List<MeasureDef>
            {
                new MeasureDef { Name = "difficulty-curve", Run = c => { DifficultyCurve.Run(c); DifficultyCurve.Report(c); } },
                new MeasureDef { Name = "party-battery", Run = c => { PartyBattery.Run(c); PartyBattery.Report(c); } },
                new MeasureDef { Name = "guide-curve", Run = c => { GuideCurve.Run(c); GuideCurve.Report(c); } },
                new MeasureDef { Name = "sim-anchors", Run = SimAnchors.Run },
                new MeasureDef { Name = "class-stages", Run = c => { ClassStages.Run(c); ClassStages.Report(c); } },
                new MeasureDef { Name = "skill-value", Run = c => { SkillValue.Run(c); SkillValue.Report(c); } },
                new MeasureDef { Name = "skill-ailments", Run = c => { SkillValue.RunAilments(c); SkillValue.ReportAilments(c); } },
                new MeasureDef { Name = "boss-fit", After = new[] { "difficulty-curve" }, Run = c => { BossFit.Run(c); BossFit.Report(c); } },
                new MeasureDef { Name = "skill-worth", Run = c => { SkillWorth.Run(c); SkillWorth.Report(c); } },
                new MeasureDef { Name = "sim-audit", Run = c => { SimAudit.Passives(c); SimAudit.Usage(c); SimAudit.Actives(c); SimAudit.Report(c); } },
                new MeasureDef { Name = "mercenaries", Run = c => { Mercenaries.Run(c); Mercenaries.Report(c); } },
                new MeasureDef { Name = "party-skills", Run = c => { PartySkills.Run(c); PartySkills.Report(c); } },
                new MeasureDef { Name = "postgame-compare", Run = c => { PostgameCompare.Run(c); PostgameCompare.Report(c); } },
                new MeasureDef { Name = "unique-skills", Run = c => { UniqueSkills.Run(c); UniqueSkills.Report(c); } },
                new MeasureDef { Name = "skill-value-contested", After = new[] { "skill-value" }, Run = c => { SkillValueContested.Run(c); SkillValueContested.Report(c); } },
                new MeasureDef { Name = "random-battles", Run = c => { RandomBattles.Run(c); RandomBattles.Report(c); } },
                new MeasureDef { Name = "regression-r04", After = new[] { "party-battery" }, Run = c => { RegressionR04.Run(c); RegressionR04.Report(c); } },
                new MeasureDef { Name = "boss-rows-check", Run = c => BossRowsCheck.Run(c) },
                new MeasureDef { Name = "support-chains", Run = c => SupportChains.Run(c) },
                new MeasureDef { Name = "support-stages", Run = c => SupportStages.Run(c) },
                new MeasureDef { Name = "design-rows", Run = c => DesignRows.Run(c) },
                new MeasureDef { Name = "win-rates", Run = c => { WinRates.Run(c); WinRates.Report(c); } },
                new MeasureDef { Name = "class-balance", Run = c => ClassSearch.Run(c, new[] { "preset=balance" }) },
            };
        }

        static string Opt(string[] args, string name, string dflt = null)
        {
            for (int i = 0; i < args.Length - 1; i++) if (args[i] == name) return args[i + 1];
            return dflt;
        }

        /// <summary>dtcli suite | dtcli &lt;measure&gt; [--snapshot S] [--root R] [--threads N] [--only a,b]</summary>
        public static int Main(string command, string[] args)
        {
            var all = All();
            if (TrialRegistry.Knows(command))
            {
                string rootT = Path.GetFullPath(Opt(args, "--root", Directory.GetCurrentDirectory()));
                var snapT = Snapshot.Load(Opt(args, "--snapshot", Path.Combine(rootT, "build", "engine_snapshot.json")));
                if (Opt(args, "--extra") != null) snapT.LoadExtra(Opt(args, "--extra"));
                var ctxT = new Ctx(snapT, rootT, int.Parse(Opt(args, "--threads", Environment.ProcessorCount.ToString())), snapT.MeasureInputs);
                try { TrialRegistry.Commands[command](ctxT, Positional(args)); }
                catch (Exception ex) { Console.Error.WriteLine(command + " failed: " + ex.GetType().Name + ": " + ex.Message); return 1; }
                return 0;
            }
            string root = Path.GetFullPath(Opt(args, "--root", Directory.GetCurrentDirectory()));
            string snapshotPath = Opt(args, "--snapshot", Path.Combine(root, "build", "engine_snapshot.json"));
            int threads = int.Parse(Opt(args, "--threads", Environment.ProcessorCount.ToString()));
            var chosen = command == "suite" ? all : all.Where(m => m.Name == command).ToList();
            string only = Opt(args, "--only");
            if (only != null) { var names = only.Split(',').ToHashSet(); chosen = all.Where(m => names.Contains(m.Name)).ToList(); }
            var timer = Stopwatch.StartNew();
            var snap = Snapshot.Load(snapshotPath);
            var ctx = new Ctx(snap, root, threads, snap.MeasureInputs);
            double loaded = timer.Elapsed.TotalSeconds;
            // a measure starts when the measures whose files it reads are done
            var tasks = new Dictionary<string, Task>();
            var seconds = new Dictionary<string, double>();
            var failures = new Dictionary<string, string>();
            var chosenNames = chosen.Select(m => m.Name).ToHashSet();
            foreach (var m in chosen)
            {
                var deps = m.After.Where(chosenNames.Contains).Select(n => tasks[n]).ToArray();
                var def = m;
                tasks[m.Name] = Task.Run(async () =>
                {
                    await Task.WhenAll(deps.Select(d => d.ContinueWith(_ => { })));
                    var own = Stopwatch.StartNew();
                    try
                    {
                        if (def.After.Any(n => chosenNames.Contains(n) && failures.ContainsKey(n))) throw new InvalidOperationException("a measure it reads from failed");
                        def.Run(ctx);
                    }
                    catch (Exception ex)
                    {
                        lock (failures) failures[def.Name] = ex.GetType().Name + ": " + ex.Message + "\n" + ex.StackTrace;
                    }
                    lock (seconds) seconds[def.Name] = own.Elapsed.TotalSeconds;
                });
            }
            Task.WaitAll(tasks.Values.ToArray());
            Console.WriteLine("snapshot " + loaded.ToString("0.0") + " s; " + chosen.Count + " measures in " + timer.Elapsed.TotalSeconds.ToString("0.0") + " s on " + threads + " threads");
            foreach (var m in chosen)
                Console.WriteLine("  " + seconds[m.Name].ToString("0.0").PadLeft(6) + " s  " + m.Name + (failures.ContainsKey(m.Name) ? "  FAILED" : ""));
            foreach (var kv in failures) Console.WriteLine("failed " + kv.Key + ": " + kv.Value);
            return failures.Count == 0 ? 0 : 1;
        }

        public static bool Knows(string command) => command == "suite" || All().Any(m => m.Name == command) || TrialRegistry.Knows(command);

        /// <summary>The arguments of a command that are not options of dtcli (the arguments of the script it stands for).</summary>
        public static string[] Positional(string[] args)
        {
            var found = new List<string>();
            string[] withValue = { "--snapshot", "--root", "--threads", "--only", "--extra" };
            for (int i = 1; i < args.Length; i++)
            {
                if (Array.IndexOf(withValue, args[i]) >= 0) { i++; continue; }
                found.Add(args[i]);
            }
            return found.ToArray();
        }
    }
}
