using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        /// <summary>dtcli doll-trial ROLE SKILL BOSSES RUNS CONDITION [ACTION]: skill-rule-trial with the recorder on, to see what a doll skill
        /// brings: the damage of the owner and of her dolls per battle, the actions of the dolls, the dolls summoned, without and with the skill.</summary>
        public static void DollTrial(Ctx c, string[] a)
        {
            string role = a[0], name = a[1]; var bosses = a[2].Split(';'); int runs = int.Parse(a[3]); string cond = a[4];
            string act = a.Length > 5 && a[5] != "-" ? a[5] : null;
            var data = c.Data("variant");
            var skill = Kit.SkillNamed(data, name);
            var rule = (cond, act ?? SkillValue.RuleFor(c, skill).act);
            Trials.Say(c, name + " (" + role + ") rule " + rule.Item1 + " / " + rule.Item2 + ", " + runs + " battles: without > with | owner damage | doll damage | doll actions | dolls summoned per battle | wins | length of won | party total damage");
            foreach (var cid in bosses)
            {
                var cells = new double[2][];
                foreach (var use in new[] { false, true })
                {
                    var res = c.Run(SkillValue.Job(c, role, cid, skill, use, 0, runs, rule: rule, record: true)).Runs;
                    double own = 0, doll = 0, acts = 0, summoned = 0, total = 0;
                    foreach (var r in res)
                        foreach (var p in r.Parts)
                        {
                            for (int i = 0; i < p.Record.Damage.Count; i++)
                            {
                                var u = p.Record.Damage.Keys[i].Unit;
                                if (u.Side != Unit.PARTY) continue;
                                double v = p.Record.Damage.Values[i];
                                total += v;
                                if (u.Kind == Kind.Doll && u.Owner != null && u.Owner.HasRole && u.Owner.Role == role) doll += v;
                                else if (u.HasRole && u.Role == role) own += v;
                            }
                            for (int i = 0; i < p.Record.Actions.Count; i++)
                            {
                                var u = p.Record.Actions.Keys[i].Unit;
                                if (u.Side == Unit.PARTY && u.Kind == Kind.Doll && u.Owner != null && u.Owner.HasRole && u.Owner.Role == role) acts += p.Record.Actions.Values[i];
                            }
                            for (int i = 0; i < p.Record.SkillUses.Count; i++)
                            {
                                var k = p.Record.SkillUses.Keys[i]; var u = k.Unit;
                                if (u.HasRole && u.Role == role && k.Name != null && k.Name == name) summoned += p.Record.SkillUses.Values[i];
                            }
                        }
                    double n = res.Length;
                    var won = res.Where(r => r.Won).ToList();
                    cells[use ? 1 : 0] = new[] { own / n, doll / n, acts / n, summoned / n, 100.0 * won.Count / n, won.Count > 0 ? won.Average(r => r.Time) : 0, total / n };
                }
                var x = cells[0]; var y = cells[1];
                Trials.Say(c, cid + " | " + x[0].ToString("0") + " > " + y[0].ToString("0") + " | " + x[1].ToString("0") + " > " + y[1].ToString("0")
                              + " | " + x[2].ToString("0.0") + " > " + y[2].ToString("0.0") + " | " + x[3].ToString("0.0") + " > " + y[3].ToString("0.0")
                              + " | " + x[4].ToString("0") + "% > " + y[4].ToString("0") + "% | " + x[5].ToString("0.0") + " > " + y[5].ToString("0.0") + " | " + x[6].ToString("0") + " > " + y[6].ToString("0"));
            }
        }
    }
}
