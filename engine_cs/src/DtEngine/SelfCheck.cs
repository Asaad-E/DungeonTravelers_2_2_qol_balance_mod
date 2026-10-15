using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace DtEngine
{
    /// <summary>Checks of single parts against golden files written by the Python side.</summary>
    public static class SelfCheck
    {
        /// <summary>Compares PyMath.RoundTo with the round(x, n) of Python, bit by bit (engine_cs/parity/round_golden.py).</summary>
        public static (int compared, List<string> errors) RoundCheck(string path)
        {
            var errors = new List<string>();
            int compared = 0;
            using (var doc = JsonDocument.Parse(File.ReadAllBytes(path)))
            {
                foreach (var c in doc.RootElement.EnumerateArray())
                {
                    double x = c[0].GetDouble();
                    int n = c[1].GetInt32();
                    double expected = c[2].GetDouble();
                    double got = PyMath.RoundTo(x, n);
                    compared++;
                    if (BitConverter.DoubleToInt64Bits(got) != BitConverter.DoubleToInt64Bits(expected) && errors.Count < 20)
                        errors.Add("round(" + x.ToString("R") + ", " + n + "): got " + got.ToString("R") + ", expected " + expected.ToString("R"));
                }
            }
            return (compared, errors);
        }

        /// <summary>Replays the calls of engine_cs/parity/rng_golden.py; returns the number of calls compared and the differences.</summary>
        public static (int compared, List<string> errors) RngCheck(string path)
        {
            var errors = new List<string>();
            int compared = 0;
            using (var doc = JsonDocument.Parse(File.ReadAllBytes(path)))
            {
                foreach (var c in doc.RootElement.EnumerateArray())
                {
                    ulong seed = c.GetProperty("seed").GetUInt64();
                    var rng = new PyRandom(seed);
                    var ops = c.GetProperty("ops");
                    var outs = c.GetProperty("out");
                    int i = 0;
                    var outEnum = outs.EnumerateArray();
                    foreach (var op in ops.EnumerateArray())
                    {
                        outEnum.MoveNext();
                        string expected = outEnum.Current.GetString();
                        string kind = op[0].GetString();
                        string got;
                        switch (kind)
                        {
                            case "random": got = Fmt.Num(rng.Random()); break;
                            case "bits": got = rng.GetRandBits(op[1].GetInt32()).ToString(); break;
                            case "range": got = rng.RandRange(op[1].GetInt32()).ToString(); break;
                            case "int": got = rng.RandInt(op[1].GetInt32(), op[2].GetInt32()).ToString(); break;
                            case "choice": got = rng.ChoiceIndex(op[1].GetInt32()).ToString(); break;
                            case "sample": got = string.Join(",", rng.SampleIndices(op[1].GetInt32(), op[2].GetInt32())); break;
                            default:
                                got = rng.ChoicesIndex(op[1].EnumerateArray().Select(x => (double)x.GetInt32()).ToArray()).ToString();
                                break;
                        }
                        compared++;
                        if (got != expected && errors.Count < 20) errors.Add("seed " + seed + " call " + i + " " + op + ": got " + got + ", expected " + expected);
                        i++;
                    }
                    if (rng.Words != c.GetProperty("words").GetInt64() && errors.Count < 20)
                        errors.Add("seed " + seed + ": " + rng.Words + " words, expected " + c.GetProperty("words").GetInt64());
                }
            }
            return (compared, errors);
        }
    }
}
