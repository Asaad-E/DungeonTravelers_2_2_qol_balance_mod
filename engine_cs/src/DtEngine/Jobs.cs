using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading;
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
        public List<List<EnemySpec>> Groups;                        // kind enemies: the battles, each a list of enemies
        public List<(string zone, int index)> Formations;           // kind formation: the battles, each one formation of a floor zone
        public int Runs = 1;
        public int StartRun;                        // first run index to execute (for incremental prefix extension when Trace == 0)
        public ulong Seed;
        public int? Kit;
        public List<(int id, int level)> ExtraSkills = new List<(int, int)>();
        public List<(int id, int pieces)> ExtraEnchants = new List<(int, int)>();
        public List<int> Bag;                      // item ids that replace the sheet Kit (one share each); null: the sheet
        public Dictionary<string, object> Options = new Dictionary<string, object>();
        public int Trace;
        public bool Record;                         // return the recorder of every battle
        public bool? SurvivalGuard, InterruptProduct;          // flags of the data set for this job
        public bool HasArcaneChance;
        public int ArcaneChance = T.NONE;
        public Dictionary<string, object> Settings;            // settings of the model that this job sets for itself
        public List<(int id, Dictionary<string, double> fields)> EnemyChanges;    // stats of enemy records for this job (GameData.with_changes)
        public List<Row> PolicyRows;               // the rows of the sheet Policies for this job, in place of the ones of the setup
        public List<Row> Policies;                 // rows added to the sheet Policies for this job (they sort by role and order with the others)
        public string Guest;                       // null: the party as built; "none": its members only; else the name of a guest ally hired beside the summon
        public Exception OwnError;                 // why the scenario of the job could not be made
        public Scenario Own;                       // the scenario of a job with rows of its own (made by JobRunner.Run)
        public string SetupName;                   // a setup of the snapshot's extra file, by name; null: the setup of the snapshot
        public PartyRecipe Recipe;                 // what is done to the reference party before it is played
        public Lazy<List<Unit>> RecipeTemplate;    // the party of the recipe, built once (made by JobRunner.Run)
        public List<string> TestedNames = new List<string>();     // the characters the tested members were given
        public List<string> ChainZones;            // kind chain: the zones a row of random battles draws from, by name
        public ulong ChainSeed;                    // kind chain: the generator shared by all the runs, in the order they play
        public int ChainCount;                     // kind chain: battles in a row
        public bool ChainThenCheckpoint;           // kind chain: the fixed battles of the checkpoint after the row (a walk, then its boss)
        public IReadOnlyList<List<(FloorZone zone, int index)>> ChainPicks;  // kind chain: the formations drawn for each run (made by JobRunner.Run)
        public MemberExtras More;                  // unique_level and passives given to every member built

        public static List<(int id, Dictionary<string, double> fields)> ParseEnemyChanges(JsonElement changes)
        {
            var list = new List<(int, Dictionary<string, double>)>();
            foreach (var p in changes.EnumerateObject())
            {
                var fields = new Dictionary<string, double>();
                foreach (var f in p.Value.EnumerateObject()) fields[f.Name] = f.Value.GetDouble();
                list.Add((int.Parse(p.Name), fields));
            }
            return list;
        }

        public static JobSpec FromJson(JsonElement e)
        {
            var j = new JobSpec { Id = e.GetProperty("id").GetString(), Side = e.GetProperty("side").GetString() };
            var party = e.GetProperty("party");
            j.Cid = party.GetProperty("cid").GetString();
            if (e.TryGetProperty("setup", out var setupName) && setupName.ValueKind == JsonValueKind.String) j.SetupName = setupName.GetString();
            if (party.TryGetProperty("recipe", out var recipe) && recipe.ValueKind == JsonValueKind.Object) j.Recipe = PartyRecipe.FromJson(recipe);
            if (party.TryGetProperty("roles", out var roles) && roles.ValueKind == JsonValueKind.Array)
                j.Roles = roles.EnumerateArray().Select(x => x.GetString()).ToList();
            if (party.TryGetProperty("level", out var level) && level.ValueKind == JsonValueKind.Number) j.Level = level.GetInt32();
            if (party.TryGetProperty("crown", out var crown) && crown.ValueKind == JsonValueKind.Number) j.Crown = crown.GetInt32();
            if (party.TryGetProperty("guest", out var guest) && guest.ValueKind == JsonValueKind.String) j.Guest = guest.GetString();
            if (party.TryGetProperty("unique_level", out var ul) && ul.ValueKind == JsonValueKind.Number)
                (j.More ?? (j.More = new MemberExtras())).UniqueLevel = ul.GetInt32();
            if (party.TryGetProperty("passives", out var pv) && pv.ValueKind == JsonValueKind.Object)
            {
                var more = j.More ?? (j.More = new MemberExtras());
                more.Passives = new List<(int, double, bool)>();
                foreach (var p in pv.EnumerateObject())
                {
                    string raw = p.Value.GetRawText();
                    bool whole = raw.IndexOf('.') < 0 && raw.IndexOf('e') < 0 && raw.IndexOf('E') < 0;
                    more.Passives.Add((int.Parse(p.Name), p.Value.GetDouble(), whole));
                }
            }
            if (e.TryGetProperty("flags", out var flags) && flags.ValueKind == JsonValueKind.Object)
            {
                if (flags.TryGetProperty("survival_guard", out var sg)) j.SurvivalGuard = sg.GetBoolean();
                if (flags.TryGetProperty("interrupt_product", out var ip)) j.InterruptProduct = ip.GetBoolean();
                if (flags.TryGetProperty("arcane_chance", out var ac))
                {
                    j.HasArcaneChance = true;
                    j.ArcaneChance = ac.ValueKind == JsonValueKind.Null ? T.NONE : ac.GetInt32();
                }
            }
            if (e.TryGetProperty("settings", out var set) && set.ValueKind == JsonValueKind.Object)
            {
                j.Settings = new Dictionary<string, object>();
                foreach (var p in set.EnumerateObject()) j.Settings[p.Name] = Snapshot.Plain(p.Value);
            }
            if (e.TryGetProperty("enemy_changes", out var changes) && changes.ValueKind == JsonValueKind.Object)
                j.EnemyChanges = ParseEnemyChanges(changes);
            if (e.TryGetProperty("policy_rows", out var polRows) && polRows.ValueKind == JsonValueKind.Array)
                j.PolicyRows = polRows.EnumerateArray().Select(Snapshot.ToRow).ToList();
            if (e.TryGetProperty("policies", out var pol) && pol.ValueKind == JsonValueKind.Array)
                j.Policies = pol.EnumerateArray().Select(Snapshot.ToRow).ToList();
            if (party.TryGetProperty("pieces", out var pcs) && pcs.ValueKind == JsonValueKind.Object)
            {
                var more = j.More ?? (j.More = new MemberExtras());
                more.Pieces = new Dictionary<string, string>();
                foreach (var p in pcs.EnumerateObject()) more.Pieces[p.Name] = p.Value.GetString();
            }
            var en = e.GetProperty("enemies");
            j.EnemyKind = en.GetProperty("kind").GetString();
            if (j.EnemyKind == "fixed")
                foreach (var b in en.GetProperty("battles").EnumerateArray()) j.Battles.Add((b[0].GetString(), b[1].GetInt32()));
            if (j.EnemyKind == "enemies")
            {
                j.Groups = new List<List<EnemySpec>>();
                foreach (var g in en.GetProperty("groups").EnumerateArray())
                    j.Groups.Add(g.EnumerateArray().Select(EnemySpec.FromJson).ToList());
            }
            if (j.EnemyKind == "formation")
            {
                j.Formations = new List<(string, int)>();
                foreach (var f in en.GetProperty("picks").EnumerateArray()) j.Formations.Add((f[0].GetString(), f[1].GetInt32()));
            }
            if (j.EnemyKind == "chain")
            {
                j.ChainZones = en.GetProperty("zones").EnumerateArray().Select(x => x.GetString()).ToList();
                j.ChainSeed = en.GetProperty("seed").GetUInt64();
                j.ChainCount = en.GetProperty("battles").GetInt32();
                j.ChainThenCheckpoint = en.TryGetProperty("then_checkpoint", out var then) && then.ValueKind == JsonValueKind.True;
            }
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
            if (e.TryGetProperty("record", out var rec) && (rec.ValueKind == JsonValueKind.True || rec.ValueKind == JsonValueKind.False)) j.Record = rec.GetBoolean();
            if (e.TryGetProperty("trace", out var tr) && tr.ValueKind == JsonValueKind.Number) j.Trace = tr.GetInt32();
            return j;
        }
    }

    /// <summary>An enemy of a battle given by the job: its id, its row, and optionally a script and attacks of its own (a test of the AI).</summary>
    public sealed class EnemySpec
    {
        public int Enemy;
        public bool Front;
        public bool HasScript;
        public Script Script;
        public int[] Attacks;
        public int[] Passives;                      // passive attacks added to the enemy's own (their effects become passives of the unit)

        public static EnemySpec FromJson(JsonElement x)
        {
            var spec = new EnemySpec { Enemy = x[0].GetInt32(), Front = x[1].GetBoolean() };
            if (x.GetArrayLength() > 2 && x[2].ValueKind == JsonValueKind.Object)
            {
                var over = x[2];
                if (over.TryGetProperty("script", out var script)) { spec.HasScript = true; spec.Script = Snapshot.LoadScript(script); }
                if (over.TryGetProperty("attacks", out var attacks)) spec.Attacks = attacks.EnumerateArray().Select(a => a.GetInt32()).ToArray();
                if (over.TryGetProperty("passives", out var passives)) spec.Passives = passives.EnumerateArray().Select(a => a.GetInt32()).ToArray();
            }
            return spec;
        }
    }

    public sealed class JobResult
    {
        public JobSpec Spec;
        public RunResult[] Runs;
        public string Error;
        public List<string> TraceLines;
        public string TraceDigest;
        public double Seconds;
        public long Battles;
    }

    public static class JobRunner
    {
        sealed class PreparedJob
        {
            public JobSpec Job;
            public Scenario Sc;
            public Row Cp;
            public BattleOptions Options;
            public Lazy<List<Unit>> PartyTemplate;
            public string CpFloor;
            public int[] CpBattles;
            public (FloorZone zone, int index)[] Formations;
            public FloorZone Zone;
        }

        static PreparedJob Prepare(IDictionary<string, Scenario> scenarios, JobSpec job)
        {
            var sc = job.Own ?? scenarios[job.Side];
            var setup = sc.Setup;
            var cp = setup.Checkpoint(job.Cid);
            var options = Scenario.OptionsFrom(setup, job.Options);
            options.Record = job.Record || job.Trace > 0;
            options.SurvivalGuard = job.SurvivalGuard;
            options.InterruptProduct = job.InterruptProduct;
            options.HasArcaneChance = job.HasArcaneChance;
            options.ArcaneChance = job.ArcaneChance;
            if (job.EnemyKind == "formation" || job.EnemyKind == "zone") options.RandomBattle = true;

            var roles = job.Roles ?? setup.Composition;
            string guest = job.Guest ?? (job.EnemyKind == "checkpoint" ? setup.CheckpointGuest(job.Cid) : null);
            var partyTemplate = new Lazy<List<Unit>>(() =>
            {
                List<Unit> built;
                if (job.RecipeTemplate != null)
                    built = Scenario.CloneOf(job.RecipeTemplate.Value);
                else if (job.Recipe != null)
                    built = sc.RecipeParty(job, job.Recipe, job.TestedNames);
                else
                {
                    int level = job.Level ?? sc.ReferenceLevels()[job.Cid].level;
                    int gear = sc.CheckpointGear(job.Cid);
                    int crown = job.Crown ?? (cp.Truthy("Crown bonus") ? cp.Int("Crown bonus") : 0);
                    built = sc.ReferenceParty(roles, cp.Str("Chapter"), level, gear, crown, cp.Str("Floor"), job.Kit, job.ExtraSkills, job.Bag, job.ExtraEnchants, job.More);
                }
                if (guest == "none")
                    built = built.Where(u => u.Kind == Kind.Member).ToList();
                else if (guest != null && guest != Scenario.NO_GUEST)
                {
                    // a hired guest ally stands beside the summon of the grand sealbook (units 3000 and 3001, 0x449771 and 0x449839), at the
                    // stage the bar offers at this point of the story
                    int leaderSealbook = T.NONE;
                    foreach (var m in built) if (m.Kind == Kind.Member) { leaderSealbook = m.Sealbook; break; }
                    var g = sc.GuestUnit(guest, job.Cid, leaderSealbook);
                    if (g != null) built.Add(g);
                }
                return built;
            }, LazyThreadSafetyMode.ExecutionAndPublication);

            var p = new PreparedJob { Job = job, Sc = sc, Cp = cp, Options = options, PartyTemplate = partyTemplate };
            if (job.EnemyKind == "checkpoint" || (job.EnemyKind == "chain" && job.ChainThenCheckpoint))
            {
                p.CpFloor = cp.Str("Floor");
                p.CpBattles = Scenario.BattleNumbers(cp).ToArray();
            }
            if (job.EnemyKind == "formation")
            {
                p.Formations = new (FloorZone, int)[job.Formations.Count];
                for (int i = 0; i < job.Formations.Count; i++)
                    p.Formations[i] = (sc.FindZone(job.Formations[i].zone), job.Formations[i].index);
            }
            else if (job.EnemyKind == "zone")
            {
                p.Zone = sc.FindZone(job.ZoneName);
            }
            return p;
        }

        static RunResult RunPrepared(PreparedJob p, int k, TextTrace trace)
        {
            var job = p.Job;
            var sc = p.Sc;
            ulong seed = job.Seed + (ulong)k;
            Func<List<Unit>> partyFactory = () => Scenario.CloneOf(p.PartyTemplate.Value);
            Func<List<Group>> enemyFactory;
            if (job.EnemyKind == "checkpoint")
            {
                enemyFactory = () =>
                {
                    var groups = new List<Group>(p.CpBattles.Length);
                    for (int i = 0; i < p.CpBattles.Length; i++) groups.Add(sc.FixedBattle(p.CpFloor, p.CpBattles[i]));
                    return groups;
                };
            }
            else if (job.EnemyKind == "fixed")
            {
                enemyFactory = () =>
                {
                    var groups = new List<Group>(job.Battles.Count);
                    for (int i = 0; i < job.Battles.Count; i++) groups.Add(sc.FixedBattle(job.Battles[i].floor, job.Battles[i].number));
                    return groups;
                };
            }
            else if (job.EnemyKind == "enemies")
            {
                enemyFactory = () =>
                {
                    var groups = new List<Group>(job.Groups.Count);
                    for (int i = 0; i < job.Groups.Count; i++) groups.Add(sc.CustomGroup(job.Groups[i]));
                    return groups;
                };
            }
            else if (job.EnemyKind == "chain")
            {
                enemyFactory = () =>
                {
                    var picks = job.ChainPicks[k];
                    int extra = p.CpBattles != null ? p.CpBattles.Length : 0;
                    var groups = new List<Group>(picks.Count + extra);
                    for (int i = 0; i < picks.Count; i++) groups.Add(sc.RandomGroupAt(picks[i].zone, picks[i].index));
                    if (p.CpBattles != null)
                        for (int i = 0; i < p.CpBattles.Length; i++) { var g = sc.FixedBattle(p.CpFloor, p.CpBattles[i]); g.Boss = true; groups.Add(g); }
                    return groups;
                };
            }
            else if (job.EnemyKind == "formation")
            {
                enemyFactory = () =>
                {
                    var groups = new List<Group>(p.Formations.Length);
                    for (int i = 0; i < p.Formations.Length; i++) groups.Add(sc.RandomGroupAt(p.Formations[i].zone, p.Formations[i].index));
                    return groups;
                };
            }
            else
            {
                var picks = new PyRandom(seed);
                enemyFactory = () =>
                {
                    var groups = new List<Group>(job.ZoneBattles);
                    for (int i = 0; i < job.ZoneBattles; i++) groups.Add(sc.RandomGroup(p.Zone, picks));
                    return groups;
                };
            }
            Action<Battle, int> onBattle = null;
            if (trace != null)
            {
                trace.Run = k;
                onBattle = (b, i) => { trace.BattleIndex = i; b.Trace = trace; };
            }
            return sc.PlayRun(partyFactory, enemyFactory, seed, p.Options, onBattle);
        }

        /// <summary>Runs one run of a job (run number k), with an optional trace.</summary>
        public static RunResult RunOne(Snapshot snap, IDictionary<string, Scenario> scenarios, JobSpec job, int k, TextTrace trace)
            => RunPrepared(Prepare(scenarios, job), k, trace);

        static string DigestOf(List<string> lines)
        {
            using (var sha = System.Security.Cryptography.SHA256.Create())
            {
                var bytes = Encoding.UTF8.GetBytes(string.Join("\n", lines));
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
            }
        }

        /// <summary>digestOnly: a traced job keeps the SHA-256 of its trace instead of its lines (to compare two builds of the engine on a great many jobs).</summary>
        public static List<JobResult> Run(Snapshot snap, List<JobSpec> jobs, int threads, bool digestOnly = false, IDictionary<string, Scenario> shared = null)
        {
            var scenarios = shared;
            if (scenarios == null)
            {
                scenarios = new ConcurrentDictionary<string, Scenario>();
                foreach (var kv in snap.Sides) scenarios[kv.Key] = new Scenario(kv.Value, snap.Setup);
            }
            var prepared = new PreparedJob[jobs.Count];
            for (int i = 0; i < jobs.Count; i++)
            {
                var j = jobs[i];
                try
                {
                    if ((j.Policies != null && j.Policies.Count > 0) || (j.Settings != null && j.Settings.Count > 0) || j.PolicyRows != null || j.EnemyChanges != null)
                    {
                        // a rule the policy does not know stops this job only
                        var basis = snap.SetupNamed(j.SetupName);
                        if (j.PolicyRows != null) basis = basis.WithPolicies(j.PolicyRows);
                        var data = j.EnemyChanges != null ? snap.Sides[j.Side].WithEnemyStats(j.EnemyChanges) : snap.Sides[j.Side];
                        j.Own = new Scenario(data, j.Settings != null ? basis.WithSettings(j.Settings) : basis, j.Policies);
                    }
                    else if (!string.IsNullOrEmpty(j.SetupName))
                    {
                        string namedKey = j.Side + "\0" + j.SetupName;
                        if (!scenarios.TryGetValue(namedKey, out var sc0))
                        {
                            sc0 = new Scenario(snap.Sides[j.Side], snap.SetupNamed(j.SetupName));
                            if (scenarios is ConcurrentDictionary<string, Scenario> cd) sc0 = cd.GetOrAdd(namedKey, sc0);
                            else scenarios[namedKey] = sc0;
                        }
                        j.Own = sc0;
                    }
                    var own = j.Own ?? scenarios[j.Side];
                    if (j.Recipe != null) j.RecipeTemplate = new Lazy<List<Unit>>(() => own.RecipeParty(j, j.Recipe, j.TestedNames), LazyThreadSafetyMode.ExecutionAndPublication);
                    if (j.EnemyKind == "chain")
                        j.ChainPicks = own.GetChainPicks(j.ChainZones, j.ChainSeed, j.ChainCount, j.Runs);
                    prepared[i] = Prepare(scenarios, j);
                }
                catch (Exception ex) { j.OwnError = ex; }
            }
            var results = new List<JobResult>(jobs.Count);
            var workEnd = new int[jobs.Count];
            var workIsTrace = new bool[jobs.Count];
            var workStartRun = new int[jobs.Count];
            int totalWork = 0;
            for (int i = 0; i < jobs.Count; i++)
            {
                var j = jobs[i];
                results.Add(new JobResult { Spec = j, Runs = new RunResult[j.Runs] });
                if (j.Trace > 0)
                {
                    workIsTrace[i] = true;
                    totalWork += 1;
                }
                else
                {
                    int start = Math.Max(0, Math.Min(j.StartRun, j.Runs));
                    workStartRun[i] = start;
                    totalWork += j.Runs - start;
                }
                workEnd[i] = totalWork;
            }
            var elapsedTicks = new long[jobs.Count];
            if (totalWork > 0)
            {
                int par = Math.Max(1, threads);
                int chunk = Math.Max(1, Math.Min(32, totalWork / (par * 16 + 1)));
                var options = new ParallelOptions { MaxDegreeOfParallelism = par };
                Parallel.ForEach(Partitioner.Create(0, totalWork, chunk), options, range =>
                {
                    int jobIdx = Array.BinarySearch(workEnd, range.Item1);
                    if (jobIdx < 0) jobIdx = ~jobIdx;
                    else jobIdx++;
                    for (int w = range.Item1; w < range.Item2; w++)
                    {
                        while (w >= workEnd[jobIdx]) jobIdx++;
                        int jobStart = jobIdx == 0 ? 0 : workEnd[jobIdx - 1];
                        var job = jobs[jobIdx];
                        var res = results[jobIdx];
                        long t0 = Stopwatch.GetTimestamp();
                        try
                        {
                            if (job.OwnError != null) throw job.OwnError;
                            if (workIsTrace[jobIdx])
                            {
                                var trace = new TextTrace(job.Trace);
                                for (int k = 0; k < job.Runs; k++) res.Runs[k] = RunPrepared(prepared[jobIdx], k, trace);
                                if (digestOnly) res.TraceDigest = DigestOf(trace.Lines);
                                else res.TraceLines = trace.Lines;
                            }
                            else
                            {
                                int k = workStartRun[jobIdx] + (w - jobStart);
                                res.Runs[k] = RunPrepared(prepared[jobIdx], k, null);
                            }
                        }
                        catch (Exception ex)
                        {
                            lock (res) res.Error = ex.GetType().Name + ": " + ex.Message + " " + ex.StackTrace;
                        }
                        Interlocked.Add(ref elapsedTicks[jobIdx], Stopwatch.GetTimestamp() - t0);
                    }
                });
            }
            double invFreq = 1.0 / Stopwatch.Frequency;
            for (int i = 0; i < results.Count; i++)
            {
                var r = results[i];
                r.Seconds = elapsedTicks[i] * invFreq;
                if (r.Error == null) foreach (var run in r.Runs) if (run != null) r.Battles += run.Parts.Count;
            }
            return results;
        }

        // --- results as json -----------------------------------------------------------------------------------
        static void WritePart(Utf8JsonWriter w, double time, bool won, bool lost, int actions, double lowest, int enemyDamage, int enemyActions,
                              int partyMaxHp, double hpLeft, double tpLeft, int alive, BattleResult part = null)
        {
            if (part != null && part.Record != null) part.Record.Write(w, part.RecordUnits);
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
                    if (r.Spec.TestedNames.Count > 0)
                    {
                        w.WriteStartArray("tested");
                        foreach (var n in r.Spec.TestedNames) w.WriteStringValue(n);
                        w.WriteEndArray();
                    }
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
                            WritePart(w, p.Time, p.Won, p.Lost, p.Actions, p.LowestHp, p.EnemyDamage, p.EnemyActions, p.PartyMaxHp, p.HpLeft, p.TpLeft, p.Alive, p);
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

        public static void WriteDigests(string path, List<JobResult> results)
        {
            using (var w = new StreamWriter(path, false, new UTF8Encoding(false)))
            {
                w.NewLine = "\n";
                foreach (var r in results) w.WriteLine(r.Spec.Id + " " + (r.Error != null ? "error" : r.TraceDigest ?? "-"));
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
