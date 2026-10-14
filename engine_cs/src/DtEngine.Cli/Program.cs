using System;
using System.Collections.Generic;
using System.IO;
using DtEngine;

namespace DtEngine.Cli
{
    public static class Program
    {
        static string Opt(string[] args, string name, string dflt = null)
        {
            for (int i = 0; i < args.Length - 1; i++) if (args[i] == name) return args[i + 1];
            return dflt;
        }

        /// <summary>dtcli run --snapshot S --jobs J --out R [--trace-out T] [--threads N]</summary>
        static int RunCommand(string[] args)
        {
            string snapshotPath = Opt(args, "--snapshot"), jobsPath = Opt(args, "--jobs"), outPath = Opt(args, "--out"), traceOut = Opt(args, "--trace-out");
            int threads = int.Parse(Opt(args, "--threads", Environment.ProcessorCount.ToString()));
            var timer = System.Diagnostics.Stopwatch.StartNew();
            var snap = Snapshot.Load(snapshotPath);
            double loaded = timer.Elapsed.TotalSeconds;
            var jobs = JobRunner.LoadJobs(jobsPath);
            timer.Restart();
            var results = JobRunner.Run(snap, jobs, threads);
            double played = timer.Elapsed.TotalSeconds;
            JobRunner.WriteResults(outPath, results);
            if (traceOut != null) JobRunner.WriteTraces(traceOut, results);
            long battles = 0;
            foreach (var r in results) battles += r.Battles;
            int errors = results.FindAll(r => r.Error != null).Count;
            double buildSeconds = Scenario.BuildTicks / (double)System.Diagnostics.Stopwatch.Frequency;
            Console.WriteLine("gc: " + GC.CollectionCount(0) + " gen0, " + GC.CollectionCount(1) + " gen1, " + GC.CollectionCount(2) + " gen2, paused " +
                              GC.GetTotalPauseDuration().TotalSeconds.ToString("0.00") + " s, allocated " + (GC.GetTotalAllocatedBytes() / 1048576) + " MB");
            Console.WriteLine("building allocated " + (Scenario.BuildBytes / 1048576) + " MB");
            Console.WriteLine("building parties and enemies took " + buildSeconds.ToString("0.00") + " s of cpu time over all threads");
            Console.WriteLine("snapshot " + loaded.ToString("0.00") + " s; " + jobs.Count + " jobs, " + battles + " battles in " + played.ToString("0.000") + " s (" +
                              (battles / Math.Max(played, 1e-9)).ToString("0.0") + " battles/s on " + threads + " threads); " + errors + " errors");
            foreach (var r in results) if (r.Error != null) Console.WriteLine("  error in " + r.Spec.Id + ": " + r.Error);
            return errors == 0 ? 0 : 1;
        }

        /// <summary>dtcli trace --snapshot S --job J --out T [--level 1|2]: plays the job(s) of the file one run after the other and writes the trace.</summary>
        static int TraceCommand(string[] args)
        {
            string snapshotPath = Opt(args, "--snapshot"), jobPath = Opt(args, "--job"), outPath = Opt(args, "--out");
            int level = int.Parse(Opt(args, "--level", "1"));
            var snap = Snapshot.Load(snapshotPath);
            var jobs = JobRunner.LoadJobs(jobPath);
            foreach (var j in jobs) j.Trace = level;
            var results = JobRunner.Run(snap, jobs, 1);
            JobRunner.WriteTraces(outPath, results);
            foreach (var r in results) if (r.Error != null) Console.WriteLine("error in " + r.Spec.Id + ": " + r.Error);
            Console.WriteLine("trace of " + jobs.Count + " job(s) written to " + outPath);
            return results.Exists(r => r.Error != null) ? 1 : 0;
        }

        public static int Main(string[] args)
        {
            if (args.Length == 0) { Console.Error.WriteLine("usage: dtengine <command> ..."); return 2; }
            switch (args[0])
            {
                case "check-rng":
                    {
                        var (n, errors) = SelfCheck.RngCheck(args[1]);
                        Console.WriteLine("rng: " + n + " calls compared, " + errors.Count + " differences");
                        foreach (var e in errors) Console.WriteLine("  " + e);
                        return errors.Count == 0 ? 0 : 1;
                    }
                case "check-formulas":
                    {
                        var (n, errors) = FormulaCheck.Run(args[1]);
                        Console.WriteLine("formulas: " + n + " cases compared, " + errors.Count + " differences");
                        foreach (var e in errors) Console.WriteLine("  " + e);
                        return errors.Count == 0 ? 0 : 1;
                    }
                case "run":
                    return RunCommand(args);
                case "trace":
                    return TraceCommand(args);
                default:
                    Console.Error.WriteLine("unknown command " + args[0]);
                    return 2;
            }
        }
    }
}
