using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        sealed class BlowTally
        {
            public int Battles, Aimed, AimedLongPhysical, AimedMidPhysical, AimedShortPhysical, Counters, WithBlow;
            public double Damage, Won, Time;
        }

        /// <summary>dtcli passive-blows ROLE SKILL BOSSES RUNS [WEAPON]: plays the cell of the skill battery without and with a passive that
        /// answers the blows aimed at its bearer (Knock Down) and counts, per boss, the blows aimed at the member of ROLE, how many are
        /// physical and of long range, how many the passive answers, the damage the member takes and the figures of the fight.
        /// BOSSES is a list of checkpoints separated by ';' or "story" for every checkpoint of the story of the battery.</summary>
        public static void PassiveBlows(Ctx c, string[] a)
        {
            string role = a[0], name = a[1]; int runs = int.Parse(a[3]); string weapon = a.Length > 4 && a[4] != "-" ? a[4] : null;
            var data = c.Data("variant"); var skill = Kit.SkillNamed(data, name);
            var cfg = c.In("skill_battery"); var levels = c.Sc("variant").ReferenceLevels();
            var bosses = a[2] == "story"
                ? c.Setup.Checkpoints.Select(r => r.Str("ID")).Where(id => id.StartsWith((string)cfg.Get("story_prefix")) && levels.ContainsKey(id)).ToList()
                : a[2].Split(';').ToList();
            var total = new Dictionary<bool, BlowTally> { { false, new BlowTally() }, { true, new BlowTally() } };
            Trials.Say(c, name + " (" + role + "), " + runs + " battles per boss: blows aimed at the " + role + " per battle | physical long range (with the skill) | answers the skill adds (counters with minus without) | damage taken without > with | wins | length of won");
            foreach (var cid in bosses)
            {
                var res = new Dictionary<bool, BlowTally>();
                foreach (bool use in new[] { false, true })
                {
                    var t = new BlowTally(); res[use] = t;
                    Battle current = null;
                    Func<Unit, bool> mine = u => u.Kind == Kind.Member && u.HasRole && u.Role == role;
                    TextTrace.PerformHook = (b, act) => { if (b != current) { current = b; t.Battles++; } };
                    TextTrace.HitHook = (b, act, target, landed) =>
                    {
                        if (!mine(target) || act.Actor.Side == target.Side) return;
                        t.Aimed++;
                        if (act.Physical && act.Reach == T.LONG) t.AimedLongPhysical++;
                        if (act.Physical && act.Reach == T.MID) t.AimedMidPhysical++;
                        if (act.Physical && act.Reach == T.SHORT) t.AimedShortPhysical++;
                    };
                    TextTrace.CounterHook = (b, unit, attacker) => { if (mine(unit)) t.Counters++; };
                    TextTrace.DamageHook = (b, act, target, amount) =>
                    {
                        if (!mine(target) || act.Actor.Side == target.Side) return;
                        t.Damage += amount;
                    };
                    try
                    {
                        int levelsOf = skill.Levels != 0 ? skill.Levels : 1;
                        var sc = c.Sc("variant"); var cp = c.Checkpoint(cid);
                        var recipe = new Obj
                        {
                            { "place", "replace_role" }, { "items", "first_kept" },
                            { "tested", Jb.L(new Obj { { "role", role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true },
                                                       { "extra_skills", new Obj { { skill.Id.ToString(), (long)(use ? levelsOf : 0) } } },
                                                       { "pieces", weapon == null ? new Obj() : new Obj { { "Weapon", weapon } } } }) },
                        };
                        var job = Jb.Make(c, "variant", cid, runs: runs, recipe: recipe, name: name + "|blows|" + role + "|" + cid + "|" + weapon + "|" + (use ? 1 : 0));
                        job.Trace = 1;
                        var done = c.Run(job);
                        var won = done.Runs.Where(r => r.Won).ToList();
                        t.Won = (double)won.Count / done.Runs.Length;
                        t.Time = won.Count > 0 ? Py.Sum(won.Select(r => r.Time)) / won.Count : 0;
                    }
                    finally { TextTrace.PerformHook = null; TextTrace.HitHook = null; TextTrace.CounterHook = null; TextTrace.DamageHook = null; }
                }
                var x = res[false]; var y = res[true]; double nb = Math.Max(1, y.Battles), nx = Math.Max(1, x.Battles);
                Trials.Say(c, cid + " | aimed " + Py.F(x.Aimed / nx, 1) + " | physical long " + Py.F(y.AimedLongPhysical / nb, 2) + " mid " + Py.F(y.AimedMidPhysical / nb, 2) + " short " + Py.F(y.AimedShortPhysical / nb, 2) + " | extra answers " + Py.F(y.Counters / nb - x.Counters / nx, 2)
                           + " | damage " + Py.F(x.Damage / nx, 0) + " > " + Py.F(y.Damage / nb, 0) + " | wins " + Py.Pct(x.Won, 1) + " > " + Py.Pct(y.Won, 1) + " | length " + Py.F(x.Time, 1) + " > " + Py.F(y.Time, 1));
                foreach (bool use in new[] { false, true })
                {
                    var s = total[use]; var t = res[use];
                    s.Battles += t.Battles; s.Aimed += t.Aimed; s.AimedLongPhysical += t.AimedLongPhysical; s.AimedMidPhysical += t.AimedMidPhysical; s.AimedShortPhysical += t.AimedShortPhysical; s.Counters += t.Counters;
                    s.Damage += t.Damage; s.Won += t.Won; s.Time += t.Time;
                    if (t.AimedLongPhysical > 0) s.WithBlow++;
                }
            }
            int n = Math.Max(1, bosses.Count); var f = total[false]; var w = total[true];
            Trials.Say(c, "all " + bosses.Count + " bosses: blows aimed per battle " + Py.F(f.Aimed / (double)Math.Max(1, f.Battles), 1) + ", physical long range " + Py.F(w.AimedLongPhysical / (double)Math.Max(1, w.Battles), 2)
                       + " (" + Py.Pct(w.AimedLongPhysical / (double)Math.Max(1, w.Aimed), 1) + " of them), physical mid " + Py.F(w.AimedMidPhysical / (double)Math.Max(1, w.Battles), 2) + " (" + Py.Pct(w.AimedMidPhysical / (double)Math.Max(1, w.Aimed), 1) + "), physical short " + Py.F(w.AimedShortPhysical / (double)Math.Max(1, w.Battles), 2) + " (" + Py.Pct(w.AimedShortPhysical / (double)Math.Max(1, w.Aimed), 1) + "); bosses where one is aimed at her: " + w.WithBlow + " of " + bosses.Count
                       + "; extra answers per battle " + Py.F(w.Counters / (double)Math.Max(1, w.Battles) - f.Counters / (double)Math.Max(1, f.Battles), 2) + "; damage taken per battle " + Py.F(f.Damage / (double)Math.Max(1, f.Battles), 0) + " > " + Py.F(w.Damage / (double)Math.Max(1, w.Battles), 0)
                       + "; mean wins " + Py.Pct(f.Won / n, 1) + " > " + Py.Pct(w.Won / n, 1) + "; mean length " + Py.F(f.Time / n, 2) + " > " + Py.F(w.Time / n, 2));
        }
    }
}
