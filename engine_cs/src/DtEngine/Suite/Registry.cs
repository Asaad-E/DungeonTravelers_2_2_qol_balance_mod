using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

namespace DtEngine.Suite
{
    /// <summary>The trial scripts that play battles, as commands of dtcli: the name of the script with hyphens, the arguments of the script.</summary>
    public static class TrialRegistry
    {
        public static readonly Dictionary<string, Action<Ctx, string[]>> Commands = new Dictionary<string, Action<Ctx, string[]>>
        {
            { "curve-recheck", Trials.CurveRecheck },
            { "etoile-dances", Trials.EtoileDances },
            { "magic-wall", Trials.MagicWall },
            { "measure-open-rows", Trials.MeasureOpenRows },
            { "samba-trial", TrialsB.SambaTrial },
            { "etoile-trial", TrialsB.EtoileTrial },
            { "dance-trial", TrialsB.DanceTrial },
            { "def-debuff-trial", TrialsB.DefDebuffTrial },
            { "sage-buffs-trial", TrialsB.SageBuffsTrial },
            { "provoke-trial", TrialsB.ProvokeTrial },
            { "boss-trim-trial", TrialsB.BossTrimTrial },
            { "grand-sealbook-trial", TrialsB.GrandSealbookTrial },
            { "lize-ideas", TrialsB.LizeIdeas },
            { "mercenary-trial", TrialsB.MercenaryTrial },
            { "one-skill-trial", TrialsB.OneSkillTrial },
            { "tp-items-trial", TrialsB.TpItemsTrial },
            { "worth-with-weapon", TrialsB.WorthWithWeapon },
            { "rows-trial", TrialsC.RowsTrial },
            { "curve-ablation", TrialsC.CurveAblation },
            { "skill-battery", SkillBattery.Run },
            { "unique-battery", SkillBattery.RunUnique },
            { "mercenary-battery", SkillBattery.RunMercenaries },
            { "sealbook-battery", SkillBattery.RunSealbooks },
            { "support-battery", SupportBattery.Run },
            { "class-search", ClassSearch.Run },
            { "walk-parties", WalkParties.Run },
        };

        public static bool Knows(string command) => Commands.ContainsKey(command);
    }

    /// <summary>The text Python gives that the trial commands print: format 'g', repr of a str, a list and a dict.</summary>
    public static class PyRepr
    {
        /// <summary>f'{x:g}'</summary>
        public static string G(double x)
        {
            if (double.IsNaN(x)) return "nan";
            if (double.IsInfinity(x)) return x > 0 ? "inf" : "-inf";
            if (x == 0) return double.IsNegative(x) ? "-0" : "0";
            string e = Math.Abs(x).ToString("E5", CultureInfo.InvariantCulture);          // d.ddddde+XXX, six significant digits
            int at = e.IndexOf('E');
            string digits = e.Substring(0, at).Replace(".", "");
            int exp = int.Parse(e.Substring(at + 1), CultureInfo.InvariantCulture);
            digits = digits.TrimEnd('0');
            if (digits.Length == 0) digits = "0";
            string sign = x < 0 ? "-" : "";
            if (exp < -4 || exp >= 6)
            {
                string mantissa = digits.Length > 1 ? digits.Substring(0, 1) + "." + digits.Substring(1) : digits;
                return sign + mantissa + "e" + (exp < 0 ? "-" : "+") + Math.Abs(exp).ToString("00", CultureInfo.InvariantCulture);
            }
            if (exp >= 0)
            {
                string intPart = digits.Length > exp + 1 ? digits.Substring(0, exp + 1) : digits + new string('0', exp + 1 - digits.Length);
                string frac = digits.Length > exp + 1 ? digits.Substring(exp + 1) : "";
                return sign + intPart + (frac.Length > 0 ? "." + frac : "");
            }
            return sign + "0." + new string('0', -exp - 1) + digits;
        }

        public static string Str(string s)
        {
            bool single = s.Contains('\'') && !s.Contains('"');
            char quote = single ? '"' : '\'';
            var sb = new StringBuilder();
            sb.Append(quote);
            foreach (char ch in s)
            {
                if (ch == quote || ch == '\\') sb.Append('\\').Append(ch);
                else if (ch == '\n') sb.Append("\\n");
                else if (ch == '\r') sb.Append("\\r");
                else if (ch == '\t') sb.Append("\\t");
                else sb.Append(ch);
            }
            sb.Append(quote);
            return sb.ToString();
        }

        /// <summary>repr() of a value read from JSON: None, True, an int, a float, a str, a list or a dict.</summary>
        public static string Of(object v)
        {
            switch (v)
            {
                case null: return "None";
                case bool b: return b ? "True" : "False";
                case long l: return l.ToString(CultureInfo.InvariantCulture);
                case int i: return i.ToString(CultureInfo.InvariantCulture);
                case double d: return Py.Repr(d);
                case string s: return Str(s);
                case Obj o: return "{" + string.Join(", ", o.Select(kv => Str(kv.Key) + ": " + Of(kv.Value))) + "}";
                case IEnumerable<object> list: return "[" + string.Join(", ", list.Select(Of)) + "]";
                default: return v.ToString();
            }
        }
    }
}
