using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;

namespace DtEngine.Suite
{
    /// <summary>What every measure shares: the snapshot, the folder of the repository, the number of threads for battles, and the way a
    /// measure writes its outputs.</summary>
    public sealed class Ctx
    {
        public readonly Snapshot Snap;
        public readonly string Root;
        public readonly int Threads;
        /// <summary>The section "measures" of the snapshot: the sheets and constants the measures take from the workbooks and the Python readers.</summary>
        public readonly Obj Inputs;
        readonly Dictionary<string, Scenario> scenarios = new Dictionary<string, Scenario>();
        public readonly ConcurrentDictionary<string, double> Seconds = new ConcurrentDictionary<string, double>();
        readonly object console = new object();

        public Ctx(Snapshot snap, string root, int threads, Obj inputs)
        {
            Snap = snap; Root = root; Threads = Math.Max(1, threads); Inputs = inputs;
            foreach (var kv in snap.Sides) scenarios[kv.Key] = new Scenario(kv.Value, snap.Setup);
        }

        public Setup Setup => Snap.Setup;

        int trialSides, trialSetups;

        /// <summary>Adds data a trial has changed as a side of its own and gives its name for the jobs (call it before the jobs that use it are played).</summary>
        public string AddSide(GameData data)
        {
            string name = "trial-side-" + (++trialSides);
            Snap.Sides[name] = data;
            lock (scenarios) scenarios[name] = new Scenario(data, Snap.Setup);
            return name;
        }

        /// <summary>Adds choices of the model a trial has changed as a setup of its own and gives its name for the jobs.</summary>
        public string AddSetup(Setup setup)
        {
            string name = "trial-setup-" + (++trialSetups);
            Snap.Setups[name] = setup;
            return name;
        }
        public Scenario Sc(string side) => scenarios[side];
        public GameData Data(string side) => Snap.Sides[side];

        public Obj In(string key) => (Obj)Inputs[key];

        // --- the settings of the model -----------------------------------------------------------------------
        public int SetInt(string key) => Setup.SettingInt(key);
        public double SetDouble(string key) => Setup.SettingDouble(key);
        public string SetStr(string key) => Setup.Settings.TryGetValue(key, out var v) && v != null ? Setup.PyStr(v) : null;

        public Row Checkpoint(string cid) => Setup.Checkpoint(cid);

        // --- battles -------------------------------------------------------------------------------------------
        /// <summary>The jobs played, in order (the runs of a job in parallel with the others).</summary>
        public List<JobResult> Run(List<JobSpec> jobs)
        {
            var results = JobRunner.Run(Snap, jobs, Threads, false, scenarios);
            foreach (var r in results) if (r.Error != null) throw new InvalidOperationException("job " + r.Spec.Id + ": " + r.Error);
            return results;
        }

        public JobResult Run(JobSpec job) => Run(new List<JobSpec> { job })[0];

        /// <summary>The jobs played; a job that fails keeps its error in the result (the others are played all the same).</summary>
        public List<JobResult> RunLoose(List<JobSpec> jobs) => JobRunner.Run(Snap, jobs, Threads, false, scenarios);

        /// <summary>The k-th of n slices of a list, as `items[(k - 1) * len(items) // n: k * len(items) // n]`.</summary>
        public static List<T> Slice<T>(List<T> items, int k, int n) => items.Skip((k - 1) * items.Count / n).Take(k * items.Count / n - (k - 1) * items.Count / n).ToList();

        /// <summary>Measure jobs of the engine (play_checkpoint, check_change, expedition, walked_zones, skill_scores, probe): the answers, in order.</summary>
        public List<Obj> Measure(List<Obj> jobs)
        {
            var texts = Measures.RunJobs(Snap, jobs.Select(j => JsonDocument.Parse(PyJson.Dump(j)).RootElement).ToList(), Threads, scenarios);
            var answers = new List<Obj>();
            foreach (var bytes in texts)
            {
                var o = (Obj)PyJson.Parse(Encoding.UTF8.GetString(bytes));
                if (o.Has("error")) throw new InvalidOperationException("measure job " + o.S("id") + ": " + o.S("error"));
                answers.Add(o);
            }
            return answers;
        }

        // --- files ---------------------------------------------------------------------------------------------
        public string Path(params string[] parts) => System.IO.Path.Combine(new[] { Root }.Concat(parts).ToArray());

        /// <summary>open(path, 'w', encoding='utf-8') on Windows (text mode: line ends are CR LF) or with newline='\n' (lf).</summary>
        public void WriteText(string path, string text, bool lf)
        {
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(path));
            if (!lf) text = text.Replace("\n", "\r\n");
            File.WriteAllBytes(path, new UTF8Encoding(false).GetBytes(text));
        }

        /// <summary>Text read back as Python reads it in text mode (CR LF becomes LF).</summary>
        public static string ReadText(string path) => File.ReadAllText(path, Encoding.UTF8).Replace("\r\n", "\n");

        public object ReadJson(string path) => PyJson.Parse(ReadText(path));

        public void Say(string line)
        {
            lock (console) Console.WriteLine(line);
        }
    }

    /// <summary>One measure of the suite: a name for the command line, the names of the measures whose files it reads, and what it does.</summary>
    public sealed class MeasureDef
    {
        public string Name;
        public string[] After = new string[0];
        public Action<Ctx> Run;
    }
}
