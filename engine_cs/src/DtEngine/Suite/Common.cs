using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>Small readers shared by the measures: sheets from the snapshot, the figures of a summary, directory listings.</summary>
    public static class M
    {
        public static List<Obj> Rows(Ctx c, string key) => c.Inputs.A(key).Cast<Obj>().ToList();

        /// <summary>str(x).split(';') with each part stripped.</summary>
        public static List<string> Parts(string text) => text.Split(';').Select(x => x.Trim()).ToList();

        /// <summary>The stages of the sheet ClassStages (tools/class_stages.py stages()).</summary>
        public static List<Obj> Stages(Ctx c) => Rows(c, "class_stages");

        public static string CellStr(Obj row, string key) => Py.Str(row.Get(key));

        /// <summary>_summary(raw) of tools/engine_client.py: the figures of sim.measures.summary as floats.</summary>
        public static Obj Summary(Obj raw) => new Obj
        {
            { "won", raw.D("won") }, { "time", raw.DN("time") }, { "lowest_hp", raw.D("lowest_hp") }, { "pressure", raw.D("pressure") },
        };

        /// <summary>The names of a folder, sorted as Python sorts strings.</summary>
        public static List<string> Listing(string dir)
        {
            if (!Directory.Exists(dir)) return new List<string>();
            var names = Directory.GetFileSystemEntries(dir).Select(System.IO.Path.GetFileName).ToList();
            names.Sort(string.CompareOrdinal);
            return names;
        }

        public static void ClearFolder(string dir)
        {
            foreach (var name in Listing(dir)) File.Delete(System.IO.Path.Combine(dir, name));
        }

        public static string Lines(IEnumerable<string> lines) => string.Join("\n", lines) + "\n";

        /// <summary>The floor of wins of the class the guide gives a checkpoint (Settings guide_&lt;class&gt;_min_won).</summary>
        public static double Floor(Ctx c, string cid)
        {
            var guide = c.In("guide_difficulty");
            string cls = guide.Has(cid) ? Py.Str(guide.Get(cid)) : "normal";
            return Setup.ToDouble(c.Setup.Settings["guide_" + cls + "_min_won"]);
        }

        public static double Share(IEnumerable<RunResult> runs) => 0;
    }

    /// <summary>The noise of the battles (configuration "statistics"): a difference counts only above max(threshold, z standard errors),
    /// and a length is read only when both sides won at least min_wins fights.</summary>
    public static class Noise
    {
        public static double Z(Ctx c) => c.Inputs.Has("statistics") ? c.In("statistics").D("z") : 2.0;
        public static int MinWins(Ctx c) => c.Inputs.Has("statistics") ? (int)Py.Num(c.In("statistics").Get("min_wins")) : 20;

        /// <summary>The standard error of the mean of b[k] - a[k] (run k of both sides plays the same seed).</summary>
        public static double Paired(IReadOnlyList<double> a, IReadOnlyList<double> b)
        {
            int n = Math.Min(a.Count, b.Count);
            if (n < 2) return double.PositiveInfinity;
            double mean = 0;
            for (int k = 0; k < n; k++) mean += b[k] - a[k];
            mean /= n;
            double ss = 0;
            for (int k = 0; k < n; k++) { double d = b[k] - a[k] - mean; ss += d * d; }
            return Math.Sqrt(ss / (n - 1) / n);
        }

        /// <summary>Two jobs of the same seeds, side by side: the differences (b - a) of wins, HP left and length (on the runs both won;
        /// null below min_wins of them) and their paired standard errors.</summary>
        public static Obj Compare(JobResult a, JobResult b, int minWins)
        {
            int n = Math.Min(a.Runs.Length, b.Runs.Length);
            var A = a.Runs.Take(n).ToList(); var B = b.Runs.Take(n).ToList();
            var o = new Obj
            {
                { "runs", (long)n },
                { "wins", n == 0 ? 0.0 : (B.Count(x => x.Won) - A.Count(x => x.Won)) / (double)n },
                { "wins_se", Paired(A.Select(x => x.Won ? 1.0 : 0.0).ToList(), B.Select(x => x.Won ? 1.0 : 0.0).ToList()) },
                { "hp", n == 0 ? 0.0 : B.Average(x => x.HpLeft) - A.Average(x => x.HpLeft) },
                { "hp_se", Paired(A.Select(x => x.HpLeft).ToList(), B.Select(x => x.HpLeft).ToList()) },
            };
            var both = Enumerable.Range(0, n).Where(k => A[k].Won && B[k].Won).ToList();
            o.Set("both_won", (long)both.Count);
            double ta = both.Count > 0 ? both.Average(k => A[k].Time) : 0;
            if (both.Count >= minWins && ta > 0)
            {
                o.Set("length", 1 - both.Average(k => B[k].Time) / ta);
                o.Set("length_se", Paired(both.Select(k => B[k].Time / ta).ToList(), both.Select(k => A[k].Time / ta).ToList()));
            }
            return o;
        }

        /// <summary>Whether the length of two summary cells ({won, time, runs}) may be compared: both won at least min_wins fights
        /// (a cell without its number of runs is read as before).</summary>
        public static bool LengthReadable(Obj a, Obj b, int minWins)
        {
            if (!Py.Truthy(a.Get("time")) || !Py.Truthy(b.Get("time"))) return false;
            if (!a.Has("runs") || !b.Has("runs")) return true;
            return a.D("won") * a.D("runs") >= minWins - 1e-9 && b.D("won") * b.D("runs") >= minWins - 1e-9;
        }

        /// <summary>A difference divided by the bar it must pass (max(threshold, z * se)); 0 when the figure is missing.</summary>
        public static double Ratio(Obj cmp, string key, double threshold, double z)
        {
            if (!cmp.Has(key) || cmp.Get(key) == null) return 0.0;
            double se = cmp.Has(key + "_se") ? cmp.D(key + "_se") : 0.0;
            return cmp.D(key) / Math.Max(threshold, z * se);
        }

        /// <summary>The standard error of the difference of two shares of wins of independent runs.</summary>
        public static double Shares(double pa, int na, double pb, int nb) =>
            na < 1 || nb < 1 ? double.PositiveInfinity : Math.Sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb);

        /// <summary>A difference that stands above the noise: at least the threshold and at least z standard errors.</summary>
        public static bool Above(double diff, double threshold, double se, double z) => diff >= Math.Max(threshold, z * se);
        public static bool Below(double diff, double threshold, double se, double z) => diff <= -Math.Max(threshold, z * se);
    }
}
