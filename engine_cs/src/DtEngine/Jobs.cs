using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace DtEngine
{
    /// <summary>
    /// One job: a party (a checkpoint's reference party or a list of roles, at a level) against enemies (the fixed
    /// battles of a checkpoint, a list of fixed battles, or random formations of a floor zone), a number of runs and a seed.
    /// </summary>
    public sealed class JobSpec
    {
        public string Id;
        public string Side = "vanilla";
        public string Cid;
        public List<string> Roles;                 // null: the composition of the setup
        public int? Level;
        public int? Crown;
        public string EnemyKind = "checkpoint";    // checkpoint | fixed | zone
        public List<(string floor, int number)> Battles = new List<(string, int)>();
        public string ZoneName;
        public int ZoneBattles;
        public int Runs = 1;
        public ulong Seed;
        public int? Kit;
        public List<(int id, int level)> ExtraSkills = new List<(int, int)>();
        public List<(int id, int pieces)> ExtraEnchants = new List<(int, int)>();
        public List<int> Bag;                      // item ids that replace the sheet Kit (one share each); null: the sheet
        public Dictionary<string, object> Options = new Dictionary<string, object>();
        public int Trace;

        public static JobSpec FromJson(JsonElement e)
        {
            var j = new JobSpec { Id = e.GetProperty("id").GetString(), Side = e.GetProperty("side").GetString() };
            var party = e.GetProperty("party");
            j.Cid = party.GetProperty("cid").GetString();
            if (party.TryGetProperty("roles", out var roles) && roles.ValueKind == JsonValueKind.Array)
                j.Roles = roles.EnumerateArray().Select(x => x.GetString()).ToList();
            if (party.TryGetProperty("level", out var level) && level.ValueKind == JsonValueKind.Number) j.Level = level.GetInt32();
            if (party.TryGetProperty("crown", out var crown) && crown.ValueKind == JsonValueKind.Number) j.Crown = crown.GetInt32();
            var en = e.GetProperty("enemies");
            j.EnemyKind = en.GetProperty("kind").GetString();
            if (j.EnemyKind == "fixed")
                foreach (var b in en.GetProperty("battles").EnumerateArray()) j.Battles.Add((b[0].GetString(), b[1].GetInt32()));
            if (j.EnemyKind == "zone")
            {
                j.ZoneName = en.GetProperty("floor").GetString();
                j.ZoneBattles = en.GetProperty("battles").GetInt32();
            }
            j.Runs = e.GetProperty("runs").GetInt32();
            j.Seed = e.GetProperty("seed").GetUInt64();
            if (e.TryGetProperty("kit", out var kit) && kit.ValueKind == JsonValueKind.Number) j.Kit = kit.GetInt32();
            if (e.TryGetProperty("extra_enchants", out var ench) && ench.ValueKind == JsonValueKind.Object)
                foreach (var p in ench.EnumerateObject()) j.ExtraEnchants.Add((int.Parse(p.Name), p.Value.GetInt32()));
            if (e.TryGetProperty("bag", out var bag) && bag.ValueKind == JsonValueKind.Array) j.Bag = bag.EnumerateArray().Select(x => x.GetInt32()).ToList();
            if (e.TryGetProperty("extra_skills", out var extra) && extra.ValueKind == JsonValueKind.Object)
                foreach (var p in extra.EnumerateObject()) j.ExtraSkills.Add((int.Parse(p.Name), p.Value.GetInt32()));
            if (e.TryGetProperty("options", out var opts) && opts.ValueKind == JsonValueKind.Object)
                foreach (var p in opts.EnumerateObject())
                    j.Options[p.Name] = p.Value.ValueKind == JsonValueKind.True ? (object)true : p.Value.ValueKind == JsonValueKind.False ? false
                        : p.Value.ValueKind == JsonValueKind.Number ? (object)p.Value.GetDouble() : p.Value.ValueKind == JsonValueKind.String ? p.Value.GetString() : null;
            if (e.TryGetProperty("trace", out var tr) && tr.ValueKind == JsonValueKind.Number) j.Trace = tr.GetInt32();
            return j;
        }
    }

    public sealed class JobResult
    {
        public JobSpec Spec;
        public RunResult[] Runs;
        public string Error;
        public List<string> TraceLines;
        public double Seconds;
        public long Battles;
    }

    public static class JobRunner
    {
        /// <summary>Runs one run of a job (run number k), with an optional trace.</summary>
        public static RunResult RunOne(Snapshot snap, Dictionary<string, Scenario> scenarios, JobSpec job, int k, TextTrace trace)
        {
            var sc = scenarios[job.Side];
            var setup = snap.Setup;
            var cp = setup.Checkpoint(job.Cid);
            ulong seed = job.Seed + (ulong)k;
            var options = Scenario.OptionsFrom(setup, job.Options);
            var roles = job.Roles ?? setup.Composition;
            Func<List<Unit>> partyFactory = () =>
            {
                int level = job.Level ?? sc.ReferenceLevels()[job.Cid].level;
                int gear = sc.CheckpointGear(job.Cid);
                int crown = job.Crown ?? (cp.Truthy("Crown bonus") ? cp.Int("Crown bonus") : 0);
                return sc.ReferenceParty(roles, cp.Str("Chapter"), level, gear, crown, cp.Str("Floor"), job.Kit, job.ExtraSkills, job.Bag, job.ExtraEnchants);
            };
            Func<List<Group>> enemyFactory;
            if (job.EnemyKind == "checkpoint")
                enemyFactory = () => Scenario.BattleNumbers(cp).Select(n => sc.FixedBattle(cp.Str("Floor"), n)).ToList();
            else if (job.EnemyKind == "fixed")
                enemyFactory = () => job.Battles.Select(b => sc.FixedBattle(b.floor, b.number)).ToList();
            else
            {
                var zone = sc.FindZone(job.ZoneName);
                var picks = new PyRandom(seed);
                options.RandomBattle = true;
                enemyFactory = () =>
                {
                    var groups = new List<Group>();
                    for (int i = 0; i < job.ZoneBattles; i++) groups.Add(sc.RandomGroup(zone, picks));
                    return groups;
                };
            }
            Action<Battle, int> onBattle = null;
            if (trace != null)
            {
                trace.Run = k;
                onBattle = (b, i) => { trace.BattleIndex = i; b.Trace = trace; };
            }
            return sc.PlayRun(partyFactory, enemyFactory, seed, options, onBattle);
        }

        public static List<JobResult> Run(Snapshot snap, List<JobSpec> jobs, int threads)
        {
            var scenarios = new Dictionary<string, Scenario>();
            foreach (var kv in snap.Sides) scenarios[kv.Key] = new Scenario(kv.Value, snap.Setup);
            var results = jobs.Select(j => new JobResult { Spec = j, Runs = new RunResult[j.Runs] }).ToList();
            // work items: (job, run); traced jobs run whole, in one piece, so that their lines stay in order
            var items = new List<(int job, int run)>();
            for (int i = 0; i < jobs.Count; i++)
            {
                if (jobs[i].Trace > 0) items.Add((i, -1));
                else for (int k = 0; k < jobs[i].Runs; k++) items.Add((i, k));
            }
            var clocks = new double[jobs.Count];
            var options = new ParallelOptions { MaxDegreeOfParallelism = Math.Max(1, threads) };
            Parallel.ForEach(items, options, item =>
            {
                var job = jobs[item.job];
                var res = results[item.job];
                var started = System.Diagnostics.Stopwatch.StartNew();
                try
                {
                    if (item.run < 0)
                    {
                        var trace = new TextTrace(job.Trace);
                        for (int k = 0; k < job.Runs; k++) res.Runs[k] = RunOne(snap, scenarios, job, k, trace);
                        res.TraceLines = trace.Lines;
                    }
                    else res.Runs[item.run] = RunOne(snap, scenarios, job, item.run, null);
                }
                catch (Exception ex)
                {
                    lock (res) res.Error = ex.GetType().Name + ": " + ex.Message + " " + ex.StackTrace;
                }
                lock (res) res.Seconds += started.Elapsed.TotalSeconds;
            });
            foreach (var r in results)
                if (r.Error == null) foreach (var run in r.Runs) if (run != null) r.Battles += run.Parts.Count;
            return results;
        }

        // --- results as json -----------------------------------------------------------------------------------
        static void WritePart(Utf8JsonWriter w, double time, bool won, bool lost, int actions, double lowest, int enemyDamage, int enemyActions,
                              int partyMaxHp, double hpLeft, double tpLeft, int alive)
        {
            w.WriteBoolean("won", won);
            w.WriteBoolean("lost", lost);
            w.WriteNumber("time", time);
            w.WriteNumber("actions", actions);
            w.WriteNumber("lowest_hp", lowest);
            w.WriteNumber("enemy_damage", enemyDamage);
            w.WriteNumber("enemy_actions", enemyActions);
            w.WriteNumber("party_max_hp", partyMaxHp);
            w.WriteNumber("hp_left", hpLeft);
            w.WriteNumber("tp_left", tpLeft);
            w.WriteNumber("alive", alive);
        }

        public static void WriteResults(string path, List<JobResult> results)
        {
            using (var stream = File.Create(path))
            using (var w = new Utf8JsonWriter(stream, new JsonWriterOptions { Indented = false }))
            {
                w.WriteStartArray();
                foreach (var r in results)
                {
                    w.WriteStartObject();
                    w.WriteString("id", r.Spec.Id);
                    if (r.Error != null) { w.WriteString("error", r.Error); w.WriteEndObject(); continue; }
                    w.WriteNumber("seconds", r.Seconds);
                    w.WriteNumber("battles", r.Battles);
                    w.WriteStartArray("runs");
                    foreach (var run in r.Runs)
                    {
                        w.WriteStartObject();
                        WritePart(w, run.Time, run.Won, run.Lost, run.Actions, run.LowestHp, run.EnemyDamage, run.EnemyActions, run.PartyMaxHp, run.HpLeft, run.TpLeft, run.Alive);
                        w.WriteStartArray("parts");
                        foreach (var p in run.Parts)
                        {
                            w.WriteStartObject();
                            WritePart(w, p.Time, p.Won, p.Lost, p.Actions, p.LowestHp, p.EnemyDamage, p.EnemyActions, p.PartyMaxHp, p.HpLeft, p.TpLeft, p.Alive);
                            w.WriteEndObject();
                        }
                        w.WriteEndArray();
                        w.WriteEndObject();
                    }
                    w.WriteEndArray();
                    var s = Summary.Of(r.Runs.ToList());
                    w.WriteStartObject("summary");
                    w.WriteNumber("won", s.Won);
                    if (s.Time.HasValue) w.WriteNumber("time", s.Time.Value); else w.WriteNull("time");
                    w.WriteNumber("lowest_hp", s.LowestHp);
                    w.WriteNumber("pressure", s.Pressure);
                    w.WriteEndObject();
                    w.WriteEndObject();
                }
                w.WriteEndArray();
            }
        }

        public static void WriteTraces(string path, List<JobResult> results)
        {
            using (var w = new StreamWriter(path, false, new UTF8Encoding(false)))
            {
                w.NewLine = "\n";
                foreach (var r in results)
                {
                    if (r.TraceLines == null) continue;
                    w.WriteLine("## job " + r.Spec.Id);
                    foreach (var l in r.TraceLines) w.WriteLine(l);
                }
            }
        }

        public static List<JobSpec> LoadJobs(string path)
        {
            using (var doc = JsonDocument.Parse(File.ReadAllBytes(path)))
            {
                var jobs = new List<JobSpec>();
                var root = doc.RootElement;
                if (root.ValueKind == JsonValueKind.Object && root.TryGetProperty("job", out var wrapped)) { jobs.Add(JobSpec.FromJson(wrapped)); return jobs; }
                if (root.ValueKind == JsonValueKind.Object && root.TryGetProperty("id", out _)) { jobs.Add(JobSpec.FromJson(root)); return jobs; }
                var arr = root.ValueKind == JsonValueKind.Array ? root : root.GetProperty("jobs");
                foreach (var e in arr.EnumerateArray()) jobs.Add(JobSpec.FromJson(e));
                return jobs;
            }
        }
    }
}
