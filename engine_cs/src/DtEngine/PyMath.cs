using System;
using System.Globalization;

namespace DtEngine
{
    /// <summary>Number formatting shared with the Python side of the traces.</summary>
    public static class Fmt
    {
        /// <summary>An integral value below 1e15 as an integer, anything else as the shortest round-trip text, lower case.</summary>
        public static string Num(double x)
        {
            if (double.IsNaN(x)) return "nan";
            if (double.IsPositiveInfinity(x)) return "inf";
            if (double.IsNegativeInfinity(x)) return "-inf";
            if (x == Math.Floor(x) && Math.Abs(x) < 1e15) return ((long)x).ToString(CultureInfo.InvariantCulture);
            return x.ToString("R", CultureInfo.InvariantCulture).Replace("E", "e");
        }
    }

    /// <summary>
    /// The built-in sum() of CPython 3.12 and later over a generator: an int sum while the items are ints, then a float
    /// sum with Neumaier compensation for float items (ints are added to the float sum plainly).
    /// </summary>
    public struct PySum
    {
        bool started;      // false: no item yet (the result is the int 0)
        bool isFloat;
        long iResult;
        double fResult, c;

        public void AddInt(long v)
        {
            if (!isFloat)
            {
                iResult += v;
                started = true;
            }
            else
            {
                fResult += (double)v;
            }
        }

        public void AddFloat(double x)
        {
            if (!isFloat)
            {
                // the generic addition int + float
                fResult = (double)iResult + x;
                isFloat = true;
                started = true;
                c = 0.0;
                return;
            }
            double t = fResult + x;
            if (Math.Abs(fResult) >= Math.Abs(x)) c += (fResult - t) + x;
            else c += (x - t) + fResult;
            fResult = t;
        }

        public double Result
        {
            get
            {
                if (!isFloat) return (double)iResult;
                double r = fResult;
                if (c != 0.0 && !double.IsInfinity(c) && !double.IsNaN(c)) r += c;
                return r;
            }
        }
    }

    public static class PyMath
    {
        /// <summary>int(x): truncation toward zero.</summary>
        public static int Int(double x) => (int)Math.Truncate(x);
        public static long Long(double x) => (long)Math.Truncate(x);

        /// <summary>round(x) with half to even, as an int.</summary>
        public static int Round(double x) => (int)Math.Round(x, MidpointRounding.ToEven);

        public static int FloorDiv(int a, int b)
        {
            int q = a / b;
            if ((a % b != 0) && ((a < 0) != (b < 0))) q--;
            return q;
        }

        public static double Clamp(double v, double low, double high) => Math.Max(low, Math.Min(high, v));

        /// <summary>struct.unpack('&lt;f', struct.pack('&lt;f', v)): the value rounded to a 32-bit float.</summary>
        public static double Single(double v) => (double)(float)v;
    }
}
