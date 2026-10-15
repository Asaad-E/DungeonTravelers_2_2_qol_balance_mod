using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace DtEngine
{
    /// <summary>The figures sim.measures.expedition returns.</summary>
    public sealed class ExpeditionResult
    {
        public double Won, ReachedLimit;
        public double[] TpAfter;
    }

    /// <summary>One row of sim.measures.check_change: the checkpoint, the figures of the two sides and the windows the change leaves.</summary>
    public sealed class CheckRow
    {
        public string Cid;
        public int LevelBefore, LevelAfter;
        public Summary Before, After;
        public List<string> Out = new List<string>();
    }

    /// <summary>The measures of sim/measures.py that play battles (expedition, play_checkpoint, check_change) and sim.scenario.walked_zones.</summary>
    public static class Measures
    {
        /// <summary>sim.measures.expedition: random battles in a row on one floor zone, HP and TP carried over, until the party falls or the
        /// limit of battles. battles, runs, kit: null takes the setting (0 too, as `battles or setting` does).</summary>
        public static ExpeditionResult Expedition(Scenario sc, string floor, int level, string cid, List<string> roles, int? battles, int? runs,
                                                  int? kit, int threads = 1)
        {
            var setup = sc.Setup;
            var zone = sc.FindZone(floor);
            var cp = setup.Checkpoint(cid);
            int gear = sc.CheckpointGear(cid);
            int nBattles = battles.HasValue && battles.Value != 0 ? battles.Value : setup.SettingInt("expedition_battles");
            int nRuns = runs.HasValue && runs.Value != 0 ? runs.Value : setup.SettingInt("expedition_runs");
            var composition = roles ?? setup.Composition;
            ulong seed = (ulong)setup.SettingInt("seed");
            var options = new Dictionary<string, object> { { "random_battle", true } };
            var results = new RunResult[nRuns];
            void One(int k)
            {
                ulong s = seed + (ulong)k;
                var picks = new PyRandom(s);                         // rng = random.Random(seed + k), used for the groups
                var opts = Scenario.OptionsFrom(setup, options);
                results[k] = sc.PlayRun(() => sc.ReferenceParty(composition, cp.Str("Chapter"), level, gear, 0, cp.Str("Floor"), kit),
                                        () =>
                                        {
                                            var groups = new List<Group>();
                                            for (int i = 0; i < nBattles; i++) groups.Add(sc.RandomGroup(zone, picks));
                                            return groups;
                                        }, s, opts);
            }
            if (threads <= 1 || nRuns <= 1) for (int k = 0; k < nRuns; k++) One(k);
            else Parallel.For(0, nRuns, new ParallelOptions { MaxDegreeOfParallelism = threads }, One);
            long wonSum = 0, full = 0;
            var tpCurve = new double[nBattles];
            for (int k = 0; k < nRuns; k++)
            {
                var parts = results[k].Parts;
                int n = parts.Count(p => p.Won);
                wonSum += n;
                if (n == nBattles) full++;
                for (int i = 0; i < parts.Count; i++) tpCurve[i] += parts[i].TpLeft / nRuns;
            }
            var tp = new double[Math.Min(nBattles, 8)];
            for (int i = 0; i < tp.Length; i++) tp[i] = PyMath.RoundTo(tpCurve[i], 2);
            return new ExpeditionResult { Won = (double)wonSum / nRuns, ReachedLimit = (double)full / nRuns, TpAfter = tp };
        }

        static readonly string[] WindowKeys = { "won", "time", "lowest_hp", "pressure" };

        static double? Figure(Summary s, string key)
        {
            switch (key)
            {
                case "won": return s.Won;
                case "time": return s.Time;
                case "lowest_hp": return s.LowestHp;
                default: return s.Pressure;
            }
        }

        /// <summary>sim.measures.check_change with the data already changed (the whole variant): each checkpoint played by the reference party on the
        /// two sides, and the windows of the sheet Settings that the figures leave.</summary>
        public static List<CheckRow> CheckChange(Scenario before, Scenario after, List<string> checkpoints, int? runs, int threads = 1)
        {
            var setup = before.Setup;
            int n = runs.HasValue && runs.Value != 0 ? runs.Value : setup.SettingInt("check_runs");
            var windows = new Dictionary<string, double>();
            foreach (var key in WindowKeys) windows[key] = setup.SettingDouble("check_" + key + "_window");
            var rows = new List<CheckRow>();
            foreach (var cid in checkpoints)
            {
                var (levelA, a) = before.PlayCheckpoint(cid, n, threads);
                var (levelB, b) = after.PlayCheckpoint(cid, n, threads);
                var row = new CheckRow { Cid = cid, LevelBefore = levelA, LevelAfter = levelB, Before = a, After = b };
                foreach (var key in WindowKeys)
                {
                    double width = windows[key];
                    double? x = Figure(a, key), y = Figure(b, key);
                    if (!x.HasValue || !y.HasValue)
                    {
                        if (x.HasValue != y.HasValue) row.Out.Add(key);
                        continue;
                    }
                    bool relative = key == "time" || key == "pressure";
                    if (Math.Abs(y.Value - x.Value) > (relative ? width * x.Value : width)) row.Out.Add(key);
                }
                rows.Add(row);
            }
            return rows;
        }

        // --- jobs -------------------------------------------------------------------------------------------------------
        static string Str(JsonElement e, string name) => e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() : null;
        static int? Int(JsonElement e, string name) => e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.Number ? (int?)v.GetInt32() : null;
        static List<string> Strings(JsonElement e, string name)
        {
            if (!e.TryGetProperty(name, out var v) || v.ValueKind != JsonValueKind.Array) return null;
            return v.EnumerateArray().Select(x => x.GetString()).ToList();
        }

        static void WriteSummary(Utf8JsonWriter w, string name, Summary s)
        {
            w.WriteStartObject(name);
            w.WriteNumber("won", s.Won);
            if (s.Time.HasValue) w.WriteNumber("time", s.Time.Value); else w.WriteNull("time");
            w.WriteNumber("lowest_hp", s.LowestHp);
            w.WriteNumber("pressure", s.Pressure);
            w.WriteEndObject();
        }

        /// <summary>One measure job (JSON) played; the result is written as an object. {id, measure, side, ...}.</summary>
        static void RunJob(Snapshot snap, Dictionary<string, Scenario> scenarios, JsonElement job, Utf8JsonWriter w, int threads)
        {
            string measure = Str(job, "measure");
            string side = Str(job, "side") ?? "variant";
            var sc = scenarios[side];
            w.WriteString("measure", measure);
            switch (measure)
            {
                case "expedition":
                    {
                        var r = Expedition(sc, Str(job, "floor"), Int(job, "level").Value, Str(job, "cid"), Strings(job, "roles"), Int(job, "battles"),
                                           Int(job, "runs"), Int(job, "kit"), threads);
                        w.WriteNumber("won", r.Won);
                        w.WriteNumber("reached_limit", r.ReachedLimit);
                        w.WriteStartArray("tp_after");
                        foreach (var x in r.TpAfter) w.WriteNumberValue(x);
                        w.WriteEndArray();
                        break;
                    }
                case "walked_zones":
                    {
                        w.WriteStartArray("zones");
                        foreach (var z in sc.WalkedZones(Str(job, "floor"), Int(job, "level").Value)) w.WriteStringValue(z.Name);
                        w.WriteEndArray();
                        break;
                    }
                case "play_checkpoint":
                    {
                        var (level, summary) = sc.PlayCheckpoint(Str(job, "cid"), Int(job, "runs"), threads);
                        w.WriteNumber("level", level);
                        WriteSummary(w, "summary", summary);
                        break;
                    }
                case "check_change":
                    {
                        var other = scenarios[Str(job, "changed_side") ?? "variant"];
                        var rows = CheckChange(sc, other, Strings(job, "checkpoints"), Int(job, "runs"), threads);
                        w.WriteStartArray("rows");
                        foreach (var row in rows)
                        {
                            w.WriteStartObject();
                            w.WriteString("cid", row.Cid);
                            w.WriteNumber("level_before", row.LevelBefore);
                            w.WriteNumber("level_after", row.LevelAfter);
                            WriteSummary(w, "before", row.Before);
                            WriteSummary(w, "after", row.After);
                            w.WriteStartArray("out");
                            foreach (var k in row.Out) w.WriteStringValue(k);
                            w.WriteEndArray();
                            w.WriteEndObject();
                        }
                        w.WriteEndArray();
                        break;
                    }
                default:
                    throw new InvalidOperationException("unknown measure " + measure);
            }
        }

        /// <summary>dtcli measure: a file of measure jobs in, a file of results out (one object per job, in order).</summary>
        public static int RunFile(Snapshot snap, string jobsPath, string outPath, int threads, out int errors)
        {
            var scenarios = new Dictionary<string, Scenario>();
            foreach (var kv in snap.Sides) scenarios[kv.Key] = new Scenario(kv.Value, snap.Setup);
            JsonDocument doc = JsonDocument.Parse(File.ReadAllBytes(jobsPath));
            var jobs = doc.RootElement.ValueKind == JsonValueKind.Array ? doc.RootElement.EnumerateArray().ToList()
                                                                       : doc.RootElement.GetProperty("jobs").EnumerateArray().ToList();
            var outputs = new byte[jobs.Count][];
            int failed = 0;
            Parallel.For(0, jobs.Count, new ParallelOptions { MaxDegreeOfParallelism = Math.Max(1, Math.Min(threads, jobs.Count)) }, i =>
            {
                string id = jobs[i].GetProperty("id").GetString();
                try
                {
                    using (var stream = new MemoryStream())
                    {
                        using (var w = new Utf8JsonWriter(stream))
                        {
                            w.WriteStartObject();
                            w.WriteString("id", id);
                            // jobs run side by side: the runs of one job are played in turn unless a single job is given the threads
                            RunJob(snap, scenarios, jobs[i], w, jobs.Count == 1 ? threads : 1);
                            w.WriteEndObject();
                        }
                        outputs[i] = stream.ToArray();
                    }
                }
                catch (Exception ex)
                {
                    System.Threading.Interlocked.Increment(ref failed);
                    outputs[i] = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new Dictionary<string, string> { { "id", id }, { "error", ex.GetType().Name + ": " + ex.Message } }));
                }
            });
            using (var f = File.Create(outPath))
            {
                f.WriteByte((byte)'[');
                for (int i = 0; i < outputs.Length; i++)
                {
                    if (i > 0) f.WriteByte((byte)',');
                    f.Write(outputs[i], 0, outputs[i].Length);
                }
                f.WriteByte((byte)']');
            }
            errors = failed;
            return jobs.Count;
        }
    }
}
