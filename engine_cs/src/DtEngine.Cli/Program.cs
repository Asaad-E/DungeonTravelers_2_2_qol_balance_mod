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

        /// <summary>dtcli run --snapshot S --jobs J --out R [--trace-out T | --trace-digest D] [--threads N]</summary>
        static int RunCommand(string[] args)
        {
            string snapshotPath = Opt(args, "--snapshot"), jobsPath = Opt(args, "--jobs"), outPath = Opt(args, "--out"), traceOut = Opt(args, "--trace-out");
            int threads = int.Parse(Opt(args, "--threads", Environment.ProcessorCount.ToString()));
            var timer = System.Diagnostics.Stopwatch.StartNew();
            var snap = Snapshot.Load(snapshotPath);
            if (Opt(args, "--extra") != null) snap.LoadExtra(Opt(args, "--extra"));
            double loaded = timer.Elapsed.TotalSeconds;
            var jobs = JobRunner.LoadJobs(jobsPath);
            timer.Restart();
            string digestOut = Opt(args, "--trace-digest");
            if (digestOut != null) foreach (var j in jobs) if (j.Trace == 0) j.Trace = 1;
            var results = JobRunner.Run(snap, jobs, threads, digestOut != null);
            double played = timer.Elapsed.TotalSeconds;
            JobRunner.WriteResults(outPath, results);
            if (traceOut != null) JobRunner.WriteTraces(traceOut, results);
            if (digestOut != null) JobRunner.WriteDigests(digestOut, results);
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

        /// <summary>dtcli measure --snapshot S --jobs J --out R [--threads N]: the measures of sim/measures.py (expedition, play_checkpoint, check_change, walked_zones).</summary>
        static int MeasureCommand(string[] args)
        {
            string snapshotPath = Opt(args, "--snapshot"), jobsPath = Opt(args, "--jobs"), outPath = Opt(args, "--out");
            int threads = int.Parse(Opt(args, "--threads", Environment.ProcessorCount.ToString()));
            var timer = System.Diagnostics.Stopwatch.StartNew();
            var snap = Snapshot.Load(snapshotPath);
            if (Opt(args, "--extra") != null) snap.LoadExtra(Opt(args, "--extra"));
            double loaded = timer.Elapsed.TotalSeconds;
            timer.Restart();
            int count = Measures.RunFile(snap, jobsPath, outPath, threads, out int errors);
            Console.WriteLine("snapshot " + loaded.ToString("0.00") + " s; " + count + " measure jobs in " + timer.Elapsed.TotalSeconds.ToString("0.000") + " s on " + threads + " threads; " + errors + " errors");
            return errors == 0 ? 0 : 1;
        }

        /// <summary>Counts the allocations of the runtime by type (the AllocationTick events: one for each 100 KB allocated).</summary>
        sealed class AllocationListener : System.Diagnostics.Tracing.EventListener
        {
            public readonly Dictionary<string, long> Bytes = new Dictionary<string, long>();
            protected override void OnEventSourceCreated(System.Diagnostics.Tracing.EventSource source)
            {
                if (source.Name == "Microsoft-Windows-DotNETRuntime")
                    EnableEvents(source, System.Diagnostics.Tracing.EventLevel.Verbose, (System.Diagnostics.Tracing.EventKeywords)0x1);
            }
            protected override void OnEventWritten(System.Diagnostics.Tracing.EventWrittenEventArgs e)
            {
                if (e.EventName == null || !e.EventName.StartsWith("GCAllocationTick")) return;
                string type = "?"; long amount = 0;
                for (int i = 0; i < e.PayloadNames.Count; i++)
                {
                    if (e.PayloadNames[i] == "TypeName") type = e.Payload[i] as string;
                    if (e.PayloadNames[i] == "AllocationAmount64") amount = Convert.ToInt64(e.Payload[i]);
                }
                lock (Bytes) { Bytes.TryGetValue(type, out long old); Bytes[type] = old + amount; }
            }
        }

        /// <summary>dtcli profile --snapshot S --jobs J [--repeat N]: plays the jobs on one thread and says the time, the bytes allocated and the types that were allocated.</summary>
        static int ProfileCommand(string[] args)
        {
            string snapshotPath = Opt(args, "--snapshot"), jobsPath = Opt(args, "--jobs");
            int repeat = int.Parse(Opt(args, "--repeat", "3"));
            var snap = Snapshot.Load(snapshotPath);
            var jobs = JobRunner.LoadJobs(jobsPath);
            JobRunner.Run(snap, jobs, 1);                                    // warm up
            Scenario.BuildTicks = 0; Scenario.BuildBytes = 0;
            using (var listener = new AllocationListener())
            {
                long a0 = GC.GetAllocatedBytesForCurrentThread();
                var timer = System.Diagnostics.Stopwatch.StartNew();
                long battles = 0;
                for (int r = 0; r < repeat; r++)
                {
                    var results = JobRunner.Run(snap, jobs, 1);
                    foreach (var x in results) battles += x.Battles;
                }
                double seconds = timer.Elapsed.TotalSeconds;
                long allocated = GC.GetAllocatedBytesForCurrentThread() - a0;
                Console.WriteLine("building parties and enemies: " + (Scenario.BuildTicks / (double)System.Diagnostics.Stopwatch.Frequency).ToString("0.00") + " s, " + (Scenario.BuildBytes / 1048576) + " MB (all the repeats and the warm-up)");
                Console.WriteLine(battles + " battles in " + seconds.ToString("0.00") + " s = " + (battles / seconds).ToString("0") + " battles/s; allocated " +
                                  (allocated / 1024.0 / 1024.0 / battles).ToString("0.000") + " MB a battle");
                List<KeyValuePair<string, long>> list;
                lock (listener.Bytes) list = new List<KeyValuePair<string, long>>(listener.Bytes);
                list.Sort((x, y) => y.Value.CompareTo(x.Value));
                long total = 0;
                foreach (var kv in list) total += kv.Value;
                foreach (var kv in list.GetRange(0, Math.Min(25, list.Count)))
                    Console.WriteLine("  " + (100.0 * kv.Value / Math.Max(1, total)).ToString("0.0").PadLeft(5) + " %  " + kv.Key);
            }
            return 0;
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
                case "measure":
                    return MeasureCommand(args);
                case "profile":
                    return ProfileCommand(args);
                case "check-round":
                    {
                        var (n, errors) = SelfCheck.RoundCheck(args[1]);
                        Console.WriteLine("round: " + n + " cases compared, " + errors.Count + " differences");
                        foreach (var e in errors) Console.WriteLine("  " + e);
                        return errors.Count == 0 ? 0 : 1;
                    }
                default:
                    Console.Error.WriteLine("unknown command " + args[0]);
                    return 2;
            }
        }
    }
}
