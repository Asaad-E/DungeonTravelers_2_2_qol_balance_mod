using System;
using System.Collections.Generic;

namespace DtEngine
{
    /// <summary>
    /// CPython's random.Random on a Mersenne Twister (MT19937), with the algorithms of the methods the simulator
    /// calls: random(), getrandbits(k), randrange(n), randint(a, b), choice(seq), sample(pool, k), choices(weights).
    /// Words counts the 32-bit outputs consumed, which the traces compare.
    /// </summary>
    public sealed class PyRandom
    {
        const int N = 624, M = 397;
        readonly uint[] mt = new uint[N];
        int index;
        public long Words;
        /// <summary>When not null, every call is appended as a line (debugging of a divergence).</summary>
        public List<string> Log;

        public PyRandom(ulong seed)
        {
            Seed(seed);
        }

        void InitGenrand(uint s)
        {
            mt[0] = s;
            for (int i = 1; i < N; i++)
                mt[i] = unchecked(1812433253u * (mt[i - 1] ^ (mt[i - 1] >> 30)) + (uint)i);
            index = N;
        }

        void InitByArray(uint[] key)
        {
            InitGenrand(19650218u);
            int i = 1, j = 0;
            int k = N > key.Length ? N : key.Length;
            for (; k > 0; k--)
            {
                mt[i] = unchecked((mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1664525u)) + key[j] + (uint)j);
                i++; j++;
                if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
                if (j >= key.Length) j = 0;
            }
            for (k = N - 1; k > 0; k--)
            {
                mt[i] = unchecked((mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1566083941u)) - (uint)i);
                i++;
                if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
            }
            mt[0] = 0x80000000u;
        }

        /// <summary>random.Random(seed) for a non-negative int seed: init_by_array on the 32-bit words of the seed.</summary>
        public void Seed(ulong seed)
        {
            uint lo = (uint)(seed & 0xFFFFFFFFu), hi = (uint)(seed >> 32);
            uint[] key = hi != 0 ? new[] { lo, hi } : new[] { lo };
            InitByArray(key);
            Words = 0;
        }

        public uint GenrandUint32()
        {
            if (index >= N)
            {
                int kk;
                uint y;
                for (kk = 0; kk < N - M; kk++)
                {
                    y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
                    mt[kk] = mt[kk + M] ^ (y >> 1) ^ ((y & 1u) != 0 ? 0x9908b0dfu : 0u);
                }
                for (; kk < N - 1; kk++)
                {
                    y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
                    mt[kk] = mt[kk + (M - N)] ^ (y >> 1) ^ ((y & 1u) != 0 ? 0x9908b0dfu : 0u);
                }
                y = (mt[N - 1] & 0x80000000u) | (mt[0] & 0x7fffffffu);
                mt[N - 1] = mt[M - 1] ^ (y >> 1) ^ ((y & 1u) != 0 ? 0x9908b0dfu : 0u);
                index = 0;
            }
            uint r = mt[index++];
            r ^= r >> 11;
            r ^= (r << 7) & 0x9d2c5680u;
            r ^= (r << 15) & 0xefc60000u;
            r ^= r >> 18;
            Words++;
            return r;
        }

        /// <summary>random.random(): 53 bits from two words.</summary>
        public double Random()
        {
            uint a = GenrandUint32() >> 5, b = GenrandUint32() >> 6;
            double v = (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
            if (Log != null) Log.Add("random -> " + Fmt.Num(v));
            return v;
        }

        /// <summary>getrandbits(k) for 0 &lt;= k &lt;= 32.</summary>
        public uint GetRandBits(int k)
        {
            if (k == 0) return 0;
            uint r = GenrandUint32() >> (32 - k);
            if (Log != null) Log.Add("bits(" + k + ") -> " + r);
            return r;
        }

        /// <summary>_randbelow_with_getrandbits(n), n &gt; 0.</summary>
        public int RandBelow(int n)
        {
            int k = BitLength(n);
            uint r = GetRandBits(k);
            while (r >= (uint)n) r = GetRandBits(k);
            return (int)r;
        }

        static int BitLength(int n)
        {
            int k = 0;
            while (n != 0) { k++; n >>= 1; }
            return k;
        }

        /// <summary>randrange(n), n &gt; 0 (raises when empty, like Python).</summary>
        public int RandRange(int n)
        {
            if (n <= 0) throw new InvalidOperationException("empty range for randrange()");
            return RandBelow(n);
        }

        /// <summary>randint(a, b) = randrange(a, b + 1).</summary>
        public int RandInt(int a, int b)
        {
            int width = b + 1 - a;
            if (width <= 0) throw new InvalidOperationException("empty range in randrange");
            return a + RandBelow(width);
        }

        /// <summary>choice(seq): the index chosen in a sequence of this length.</summary>
        public int ChoiceIndex(int length)
        {
            if (length <= 0) throw new InvalidOperationException("Cannot choose from an empty sequence");
            return RandBelow(length);
        }

        /// <summary>sample(pool, k) for the list branch of CPython (population small): the selected indices in order.</summary>
        public int[] SampleIndices(int n, int k)
        {
            if (k < 0 || k > n) throw new InvalidOperationException("Sample larger than population or is negative");
            long setsize = 21;
            if (k > 5) setsize += (long)Math.Pow(4, Math.Ceiling(Math.Log(k * 3) / Math.Log(4)));
            if (n > setsize) throw new NotSupportedException("sample of a large population");
            var pool = new int[n];
            for (int i = 0; i < n; i++) pool[i] = i;
            var result = new int[k];
            for (int i = 0; i < k; i++)
            {
                int j = RandBelow(n - i);
                result[i] = pool[j];
                pool[j] = pool[n - i - 1];
            }
            return result;
        }

        /// <summary>choices(population, weights)[0]: the index picked by cumulative integer weights and bisect_right.</summary>
        public int ChoicesIndex(double[] weights)
        {
            int n = weights.Length;
            var cum = new double[n];
            double acc = 0;
            for (int i = 0; i < n; i++) { acc += weights[i]; cum[i] = acc; }
            double total = cum[n - 1] + 0.0;
            double x = Random() * total;
            int lo = 0, hi = n - 1;
            while (lo < hi)
            {
                int mid = (lo + hi) / 2;
                if (x < cum[mid]) hi = mid; else lo = mid + 1;
            }
            return lo;
        }
    }
}
