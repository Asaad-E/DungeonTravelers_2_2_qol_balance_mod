using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Text.Json;

namespace DtEngine.Suite
{
    /// <summary>
    /// The behaviours of Python that the reports of the measures depend on, byte for byte: float formatting (`%.2f`, `:.0%`, `repr`),
    /// `json.dump`, the statistics module and the truthiness of a value. Nothing here is particular to a measure.
    /// </summary>
    public static class Py
    {
        static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

        // --- numbers as text -------------------------------------------------------------------------------------
        static void Decompose(double x, out BigInteger mantissa, out int exponent)
        {
            long bits = BitConverter.DoubleToInt64Bits(x);
            int e = (int)((bits >> 52) & 0x7FF);
            long fraction = bits & 0xFFFFFFFFFFFFFL;
            if (e == 0) { mantissa = fraction; exponent = -1074; }
            else { mantissa = fraction | (1L << 52); exponent = e - 1075; }
        }

        /// <summary>'%.{digits}f' % x: the exact value of x rounded half to even at `digits` decimals; the sign of a negative zero and of a
        /// value that rounds to zero is kept.</summary>
        public static string Fixed(double x, int digits)
        {
            if (double.IsNaN(x)) return "nan";
            if (double.IsPositiveInfinity(x)) return "inf";
            if (double.IsNegativeInfinity(x)) return "-inf";
            bool negative = x < 0 || (x == 0 && double.IsNegative(x));
            Decompose(Math.Abs(x), out var mantissa, out int exponent);
            BigInteger numerator = mantissa * BigInteger.Pow(10, digits), denominator = BigInteger.One;
            if (exponent >= 0) numerator <<= exponent; else denominator <<= -exponent;
            var quotient = BigInteger.DivRem(numerator, denominator, out var remainder);
            int cmp = (remainder * 2).CompareTo(denominator);
            if (cmp > 0 || (cmp == 0 && !quotient.IsEven)) quotient += 1;
            string text = quotient.ToString(Inv);
            if (digits > 0)
            {
                if (text.Length <= digits) text = new string('0', digits - text.Length + 1) + text;
                text = text.Substring(0, text.Length - digits) + "." + text.Substring(text.Length - digits);
            }
            return (negative ? "-" : "") + text;
        }

        /// <summary>f'{x:.{digits}f}' or, with plus, f'{x:+.{digits}f}'.</summary>
        public static string F(double x, int digits, bool plus = false)
        {
            string s = Fixed(x, digits);
            return plus && !s.StartsWith("-") ? "+" + s : s;
        }

        /// <summary>f'{x:.{digits}%}' (the product by 100 is a float product, as in Python).</summary>
        public static string Pct(double x, int digits, bool plus = false)
        {
            if (double.IsNaN(x) || double.IsInfinity(x)) return F(x, digits, plus) + "%";
            return F(x * 100.0, digits, plus) + "%";
        }

        /// <summary>repr(float).</summary>
        public static string Repr(double x)
        {
            if (double.IsNaN(x)) return "NaN";
            if (double.IsPositiveInfinity(x)) return "Infinity";
            if (double.IsNegativeInfinity(x)) return "-Infinity";
            if (x == 0) return double.IsNegative(x) ? "-0.0" : "0.0";
            string r = Math.Abs(x).ToString("E16", Inv);        // placeholder, replaced below by the shortest digits
            string shortest = Math.Abs(x).ToString("R", Inv);
            // the shortest digits and the decimal exponent of the value
            string digits; int pointAt;                           // value = 0.DIGITS * 10^pointAt
            int ePos = shortest.IndexOfAny(new[] { 'E', 'e' });
            string mant = ePos >= 0 ? shortest.Substring(0, ePos) : shortest;
            int exp10 = ePos >= 0 ? int.Parse(shortest.Substring(ePos + 1), Inv) : 0;
            int dot = mant.IndexOf('.');
            string intPart = dot >= 0 ? mant.Substring(0, dot) : mant, frac = dot >= 0 ? mant.Substring(dot + 1) : "";
            string all = intPart + frac;
            int lead = 0;
            while (lead < all.Length - 1 && all[lead] == '0') lead++;
            digits = all.Substring(lead).TrimEnd('0');
            if (digits.Length == 0) digits = "0";
            pointAt = intPart.Length - lead + exp10;
            // CPython repr: the 'r' format uses exponent notation when the decimal exponent is below -4 or at least 16
            int decpt = pointAt;                                   // x = 0.d1d2.. * 10^decpt
            string sign = x < 0 ? "-" : "";
            if (decpt > 16 || decpt < -3)
            {
                string m = digits.Length == 1 ? digits : digits.Substring(0, 1) + "." + digits.Substring(1);
                int e10 = decpt - 1;
                return sign + m + "e" + (e10 < 0 ? "-" : "+") + Math.Abs(e10).ToString("00", Inv);
            }
            if (decpt <= 0) return sign + "0." + new string('0', -decpt) + digits;
            if (digits.Length <= decpt) return sign + digits + new string('0', decpt - digits.Length) + ".0";
            return sign + digits.Substring(0, decpt) + "." + digits.Substring(decpt);
        }

        /// <summary>f'{x:g}'</summary>
        public static string G(double x) => PyRepr.G(x);

        /// <summary>repr() of a value read from JSON (None, True, numbers, str, list, dict).</summary>
        public static string ReprObj(object v) => PyRepr.Of(v);

        public static string ReprList(IEnumerable<object> items) => PyRepr.Of(items.ToList());

        // --- truthiness, numbers of mixed kind -------------------------------------------------------------------
        public static bool Truthy(object v)
        {
            switch (v)
            {
                case null: return false;
                case bool b: return b;
                case long l: return l != 0;
                case int i: return i != 0;
                case double d: return d != 0.0;
                case string s: return s.Length > 0;
                case ICollection c: return c.Count > 0;
                default: return true;
            }
        }

        public static double Num(object v)
        {
            switch (v)
            {
                case double d: return d;
                case long l: return l;
                case int i: return i;
                case bool b: return b ? 1 : 0;
                default: throw new InvalidOperationException("not a number: " + (v ?? "None"));
            }
        }

        // --- sums and statistics ---------------------------------------------------------------------------------
        /// <summary>sum() of floats (CPython 3.12 and later).</summary>
        public static double Sum(IEnumerable<double> items)
        {
            var s = new PySum();
            foreach (var x in items) s.AddFloat(x);
            return s.Result;
        }

        /// <summary>sum() of a generator that yields ints and floats, each as the kind it has in Python.</summary>
        public static double SumMixed(IEnumerable<(double value, bool isFloat)> items)
        {
            var s = new PySum();
            foreach (var (v, f) in items) { if (f) s.AddFloat(v); else s.AddInt((long)v); }
            return s.Result;
        }

        public static long SumInt(IEnumerable<bool> items) { long n = 0; foreach (var b in items) if (b) n++; return n; }

        /// <summary>statistics.median of numbers.</summary>
        public static double Median(IEnumerable<double> items)
        {
            var d = items.OrderBy(x => x).ToList();
            if (d.Count == 0) throw new InvalidOperationException("no median for empty data");
            int i = d.Count / 2;
            if (d.Count % 2 == 1) return d[i];
            return (d[i - 1] + d[i]) / 2;
        }

        /// <summary>statistics.mean of floats: the exact mean rounded once to the nearest float.</summary>
        public static double Mean(IEnumerable<double> items)
        {
            var list = items.ToList();
            if (list.Count == 0) throw new InvalidOperationException("mean requires at least one data point");
            // exact sum as a fraction over 2^1074
            BigInteger total = BigInteger.Zero;
            foreach (var x in list)
            {
                Decompose(Math.Abs(x), out var m, out int e);
                var scaled = m << (e + 1074);
                total += x < 0 ? -scaled : scaled;
            }
            return Ratio(total, BigInteger.Pow(2, 1074) * list.Count);
        }

        /// <summary>The float nearest to numerator / denominator (round half to even), as int / int does in Python.</summary>
        public static double Ratio(BigInteger numerator, BigInteger denominator)
        {
            if (numerator.IsZero) return 0.0;
            bool negative = numerator.Sign < 0;
            numerator = BigInteger.Abs(numerator);
            // scale so that the quotient has 55 or 56 bits, then round to 53 with a sticky bit
            long nb = (long)numerator.GetBitLength(), db = (long)denominator.GetBitLength();
            int shift = (int)(55 - (nb - db));
            BigInteger n = numerator, d = denominator;
            if (shift > 0) n <<= shift; else d <<= -shift;
            var q = BigInteger.DivRem(n, d, out var rem);
            long qb = (long)q.GetBitLength();
            // q has 55 or 56 bits; the value is q * 2^-shift (+ rem)
            int drop = (int)(qb - 53);
            // subnormal results
            int exponent = -shift + drop;                      // the value of the lowest kept bit is 2^exponent
            if (exponent < -1074) { drop += -1074 - exponent; exponent = -1074; }
            var kept = q >> drop;
            var low = q - (kept << drop);
            var half = BigInteger.One << (drop - 1);
            int cmp = low.CompareTo(half);
            bool above = cmp > 0 || (cmp == 0 && !rem.IsZero);
            bool tie = cmp == 0 && rem.IsZero;
            if (above || (tie && !kept.IsEven)) kept += 1;
            double result = (double)kept * Math.Pow(2, 0);     // kept < 2^54: exact
            result = Math.ScaleB((double)kept, exponent);
            return negative ? -result : result;
        }

        // --- text helpers ----------------------------------------------------------------------------------------
        /// <summary>'; '.join / ', '.join over objects printed as str() would.</summary>
        public static string Join(string separator, IEnumerable<object> items) => string.Join(separator, items.Select(Str));

        /// <summary>str(value) for the kinds a row holds.</summary>
        public static string Str(object v)
        {
            switch (v)
            {
                case null: return "None";
                case string s: return s;
                case bool b: return b ? "True" : "False";
                case long l: return l.ToString(Inv);
                case int i: return i.ToString(Inv);
                case double d: return Repr(d);
                default: return v.ToString();
            }
        }

        /// <summary>str(x).strip().split(';') parts, each stripped (the usual list in a cell).</summary>
        public static List<string> SplitList(object cell, char separator = ';') =>
            Str(cell).Split(separator).Select(x => x.Trim()).ToList();
    }

    /// <summary>A dictionary that keeps the order of its keys (a Python dict) and writes itself as json.dump does.</summary>
    public sealed class Obj : IEnumerable<KeyValuePair<string, object>>
    {
        readonly List<string> keys = new List<string>();
        readonly Dictionary<string, object> map = new Dictionary<string, object>();

        public void Add(string key, object value) => Set(key, value);
        public void Set(string key, object value)
        {
            if (!map.ContainsKey(key)) keys.Add(key);
            map[key] = value;
        }
        public bool Has(string key) => map.ContainsKey(key);
        public object this[string key] { get => map[key]; set => Set(key, value); }
        public object Get(string key) => map.TryGetValue(key, out var v) ? v : null;
        public int Count => keys.Count;
        public IEnumerable<string> Keys => keys;
        public bool Remove(string key) { if (!map.Remove(key)) return false; keys.Remove(key); return true; }
        public double D(string key) => Py.Num(map[key]);
        public double? DN(string key) => map.TryGetValue(key, out var v) && v != null ? Py.Num(v) : (double?)null;
        public string S(string key) => (string)map[key];
        public long L(string key) => Convert.ToInt64(map[key], CultureInfo.InvariantCulture);
        public List<object> A(string key) => (List<object>)map[key];
        public Obj O(string key) => (Obj)map[key];
        public IEnumerator<KeyValuePair<string, object>> GetEnumerator()
        {
            foreach (var k in keys) yield return new KeyValuePair<string, object>(k, map[k]);
        }
        IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
    }

    /// <summary>json.dump and json.load over Obj, List&lt;object&gt;, long, double, string, bool and null.</summary>
    public static class PyJson
    {
        /// <summary>json.dumps(value) (indent null) or json.dumps(value, indent=n).</summary>
        public static string Dump(object value, int? indent = null)
        {
            var sb = new StringBuilder();
            Write(sb, value, indent, 0);
            return sb.ToString();
        }

        static void NewLine(StringBuilder sb, int? indent, int level)
        {
            sb.Append('\n').Append(' ', indent.Value * level);
        }

        static void Write(StringBuilder sb, object v, int? indent, int level)
        {
            switch (v)
            {
                case null: sb.Append("null"); break;
                case bool b: sb.Append(b ? "true" : "false"); break;
                case long l: sb.Append(l.ToString(CultureInfo.InvariantCulture)); break;
                case int i: sb.Append(i.ToString(CultureInfo.InvariantCulture)); break;
                case double d: sb.Append(Py.Repr(d)); break;
                case string s: WriteString(sb, s); break;
                case Obj o:
                    if (o.Count == 0) { sb.Append("{}"); break; }
                    sb.Append('{');
                    bool first = true;
                    foreach (var kv in o)
                    {
                        if (!first) sb.Append(indent.HasValue ? "," : ", ");
                        first = false;
                        if (indent.HasValue) NewLine(sb, indent, level + 1);
                        WriteString(sb, kv.Key);
                        sb.Append(": ");
                        Write(sb, kv.Value, indent, level + 1);
                    }
                    if (indent.HasValue) NewLine(sb, indent, level);
                    sb.Append('}');
                    break;
                case IEnumerable<object> list:
                    var items = list.ToList();
                    if (items.Count == 0) { sb.Append("[]"); break; }
                    sb.Append('[');
                    for (int k = 0; k < items.Count; k++)
                    {
                        if (k > 0) sb.Append(indent.HasValue ? "," : ", ");
                        if (indent.HasValue) NewLine(sb, indent, level + 1);
                        Write(sb, items[k], indent, level + 1);
                    }
                    if (indent.HasValue) NewLine(sb, indent, level);
                    sb.Append(']');
                    break;
                default:
                    throw new InvalidOperationException("cannot write " + v.GetType());
            }
        }

        static void WriteString(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    case '\b': sb.Append("\\b"); break;
                    case '\f': sb.Append("\\f"); break;
                    default:
                        if (c < 0x20 || c > 0x7e) sb.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
        }

        public static object Parse(string text)
        {
            using (var doc = JsonDocument.Parse(text, new JsonDocumentOptions { MaxDepth = 256 })) return From(doc.RootElement);
        }

        public static object From(JsonElement e)
        {
            switch (e.ValueKind)
            {
                case JsonValueKind.Object:
                    var o = new Obj();
                    foreach (var p in e.EnumerateObject()) o.Set(p.Name, From(p.Value));
                    return o;
                case JsonValueKind.Array:
                    var l = new List<object>();
                    foreach (var x in e.EnumerateArray()) l.Add(From(x));
                    return l;
                case JsonValueKind.String: return e.GetString();
                case JsonValueKind.True: return true;
                case JsonValueKind.False: return false;
                case JsonValueKind.Null: return null;
                default:
                    string raw = e.GetRawText();
                    if (raw.IndexOfAny(new[] { '.', 'e', 'E' }) < 0) return long.Parse(raw, CultureInfo.InvariantCulture);
                    return double.Parse(raw, NumberStyles.Float, CultureInfo.InvariantCulture);
            }
        }
    }
}
