using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace DtEngine.Suite
{
    /// <summary>The golden file of engine_cs/parity/py_format_golden.py: what Python gives for the text of a float, statistics.mean and median, and json.dumps.</summary>
    public static class PyFormatCheck
    {
        public static (int compared, List<string> errors) Run(string path)
        {
            var errors = new List<string>();
            int compared = 0;
            using (var doc = JsonDocument.Parse(File.ReadAllBytes(path)))
            {
                var root = doc.RootElement;
                foreach (var row in root.GetProperty("floats").EnumerateArray())
                {
                    double x = row[0].GetDouble();
                    var expected = row[1].EnumerateArray().Select(e => e.GetString()).ToList();
                    var got = new List<string> { Py.Repr(x), Py.F(x, 0), Py.F(x, 1), Py.F(x, 2), Py.Pct(x, 0), Py.Pct(x, 1), Py.Pct(x, 0, true), Py.F(x, 0, true), Py.G(x) };
                    for (int i = 0; i < expected.Count; i++)
                    {
                        compared++;
                        if (got[i] != expected[i] && errors.Count < 20) errors.Add("format " + i + " of " + Py.Repr(x) + ": got " + got[i] + ", expected " + expected[i]);
                    }
                }
                foreach (var row in root.GetProperty("means").EnumerateArray())
                {
                    var xs = row[0].EnumerateArray().Select(e => e.GetDouble()).ToList();
                    double mean = Py.Mean(xs), median = Py.Median(xs);
                    compared += 2;
                    if (mean != row[1].GetDouble() && errors.Count < 20) errors.Add("mean of " + string.Join(",", xs.Select(Py.Repr)) + ": got " + Py.Repr(mean) + ", expected " + Py.Repr(row[1].GetDouble()));
                    if (median != row[2].GetDouble() && errors.Count < 20) errors.Add("median of " + string.Join(",", xs.Select(Py.Repr)) + ": got " + Py.Repr(median));
                }
                foreach (var row in root.GetProperty("documents").EnumerateArray())
                {
                    var value = PyJson.From(row[0]);
                    string plain = PyJson.Dump(value), indented = PyJson.Dump(value, 1), shown = Py.ReprObj(value);
                    compared += 3;
                    if (shown != row[3].GetString() && errors.Count < 20) errors.Add("repr: got " + shown + ", expected " + row[3].GetString());
                    if (plain != row[1].GetString() && errors.Count < 20) errors.Add("json.dumps: got " + plain + ", expected " + row[1].GetString());
                    if (indented != row[2].GetString() && errors.Count < 20) errors.Add("json.dumps indent=1: got " + indented + ", expected " + row[2].GetString());
                }
            }
            return (compared, errors);
        }
    }
}
