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
}
