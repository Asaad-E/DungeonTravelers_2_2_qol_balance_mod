using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        /// <summary>dtcli chant-break-trial ROLE SKILL BOSSES RUNS CONDITION [ACTION]: skill-rule-trial with the chants of the enemies counted
        /// (started, finished, broken, per battle), to see what a skill that raises the critical rate does against enemy casters.</summary>
        public static void ChantBreakTrial(Ctx c, string[] a)
        {
            string role = a[0], name = a[1]; var bosses = a[2].Split(';'); int runs = int.Parse(a[3]); string cond = a[4];
            string act = a.Length > 5 && a[5] != "-" ? a[5] : null;
            var data = c.Data("variant");
            var skill = Kit.SkillNamed(data, name);
            var rule = (cond, act ?? SkillValue.RuleFor(c, skill).act);
            Trials.Say(c, name + " (" + role + ") rule " + rule.Item1 + " / " + rule.Item2 + ", " + runs + " battles: without > with | enemy chants started | finished | broken per battle | wins | damage taken per battle");
            foreach (var cid in bosses)
            {
                var cells = new double[2][];
                foreach (var use in new[] { false, true })
                {
                    var res = c.Run(SkillValue.Job(c, role, cid, skill, use, 0, runs, rule: rule, record: true)).Runs;
                    double started = 0, done = 0, broken = 0;
                    foreach (var r in res)
                        foreach (var p in r.Parts)
                        {
                            Tally(p.Record.ChantsStarted, ref started); Tally(p.Record.ChantsDone, ref done); Tally(p.Record.ChantsBroken, ref broken);
                        }
                    cells[use ? 1 : 0] = new[] { started / res.Length, done / res.Length, broken / res.Length,
                                                 100.0 * res.Count(r => r.Won) / res.Length, res.Average(r => (double)r.EnemyDamage) };
                }
                var x = cells[0]; var y = cells[1];
                Trials.Say(c, cid + " | " + F(x[0]) + " > " + F(y[0]) + " | " + F(x[1]) + " > " + F(y[1]) + " | " + F(x[2]) + " > " + F(y[2])
                              + " | " + x[3].ToString("0") + "% > " + y[3].ToString("0") + "% | " + x[4].ToString("0") + " > " + y[4].ToString("0"));
            }
        }

        static string F(double v) => v.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture);

        static void Tally(RecTable table, ref double sum)
        {
            for (int i = 0; i < table.Count; i++)
                if (table.Keys[i].Unit.Side == Unit.ENEMIES) sum += table.Values[i];
        }
    }
}
