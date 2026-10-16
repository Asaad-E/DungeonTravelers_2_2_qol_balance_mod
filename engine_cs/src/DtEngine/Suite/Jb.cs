using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace DtEngine.Suite
{
    /// <summary>Builds the jobs of the engine the way tools/engine_client.py make_job does, and the small dictionaries the jobs hold.</summary>
    public static class Jb
    {
        public static List<object> L(params object[] items) => new List<object>(items);
        public static List<object> L(IEnumerable<object> items) => new List<object>(items);

        public static Obj Dict(IEnumerable<KeyValuePair<string, object>> items)
        {
            var o = new Obj();
            foreach (var kv in items) o.Set(kv.Key, kv.Value);
            return o;
        }

        public static Obj Fixed(string floor, IEnumerable<int> numbers) =>
            new Obj { { "kind", "fixed" }, { "battles", L(numbers.Select(n => (object)L(floor, (long)n))) } };

        public static Obj Chain(IEnumerable<string> zones, long seed, int battles) =>
            new Obj { { "kind", "chain" }, { "zones", L(zones.Cast<object>()) }, { "seed", seed }, { "battles", (long)battles } };

        /// <summary>engine_client.make_job. recipe, options, extraSkills, settings, policyRows, flags and enemyChanges are dictionaries ready to write.</summary>
        public static JobSpec Make(Ctx c, string side, string cid, IEnumerable<string> roles = null, int runs = 1, long? seed = null, int? level = null,
                                   int? crown = null, Obj enemies = null, Obj options = null, int? kit = null, string guest = null, string name = null,
                                   bool record = false, Obj recipe = null, Dictionary<int, int> extraSkills = null, Obj settings = null,
                                   List<object> policyRows = null, Obj flags = null, Obj enemyChanges = null, string setupName = null)
        {
            var party = new Obj
            {
                { "cid", cid }, { "roles", roles == null ? null : L(roles.Cast<object>()) }, { "level", level.HasValue ? (object)(long)level.Value : null },
                { "crown", crown.HasValue ? (object)(long)crown.Value : null },
            };
            if (guest != null) party.Set("guest", guest);
            if (recipe != null) party.Set("recipe", recipe);
            var job = new Obj
            {
                { "id", name ?? (side + "-" + cid) }, { "side", side }, { "runs", (long)runs },
                { "seed", seed ?? Convert.ToInt64(c.Setup.Settings["seed"]) }, { "trace", 0L }, { "record", record },
                { "kit", kit.HasValue ? (object)(long)kit.Value : null }, { "options", options ?? new Obj() }, { "party", party },
                { "enemies", enemies ?? new Obj { { "kind", "checkpoint" } } },
            };
            if (setupName != null) job.Set("setup", setupName);
            if (extraSkills != null && extraSkills.Count > 0)
            {
                var x = new Obj();
                foreach (var kv in extraSkills) x.Set(kv.Key.ToString(), (long)kv.Value);
                job.Set("extra_skills", x);
            }
            if (settings != null && settings.Count > 0) job.Set("settings", settings);
            if (policyRows != null) job.Set("policy_rows", policyRows);
            if (flags != null && flags.Count > 0) job.Set("flags", flags);
            if (enemyChanges != null && enemyChanges.Count > 0) job.Set("enemy_changes", enemyChanges);
            return Spec(job);
        }

        /// <summary>A job written as a dictionary, read by the engine as a file of jobs would be.</summary>
        public static JobSpec Spec(Obj job)
        {
            using (var doc = JsonDocument.Parse(PyJson.Dump(job))) return JobSpec.FromJson(doc.RootElement);
        }

        /// <summary>A row of a sheet as a dictionary of cells.</summary>
        public static Obj RowObj(Row r)
        {
            var o = new Obj();
            foreach (var kv in r.Cells) o.Set(kv.Key, kv.Value);
            return o;
        }

        // --- the figures a measure takes from the runs of a job -----------------------------------------------
        public static List<RunResult> Won(JobResult r) => r.Runs.Where(x => x.Won).ToList();

        public static double MeanTime(List<RunResult> runs) => Py.Sum(runs.Select(r => r.Time)) / runs.Count;
        public static double MeanHpLeft(IEnumerable<RunResult> runs, int n) => Py.Sum(runs.Select(r => r.HpLeft)) / n;
        public static double MeanTpLeft(IEnumerable<RunResult> runs, int n) => Py.Sum(runs.Select(r => r.TpLeft)) / n;
        public static double MeanLowest(IEnumerable<RunResult> runs, int n) => Py.Sum(runs.Select(r => r.LowestHp)) / n;
    }
}
