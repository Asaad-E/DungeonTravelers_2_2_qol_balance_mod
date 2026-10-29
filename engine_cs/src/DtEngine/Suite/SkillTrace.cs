using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        sealed class TraceTally
        {
            public int Battles, Casts, RecastActive, Chants, ActorActions, ActorTurns;
            public double ActorSeconds;
            public int CastTargets, CastTargetsActive;
            public double IntervalOn, IntervalOff; public int TurnsOn, TurnsOff;
            public Dictionary<int, double> Before = new Dictionary<int, double>();
            public Dictionary<string, double> StatDelta = new Dictionary<string, double>();
            public Dictionary<string, int> StatN = new Dictionary<string, int>();
            public List<string> Sample = new List<string>();
            public int HitsOnLanded, HitsOnTotal, HitsOffLanded, HitsOffTotal;
            public Dictionary<string, int> ActsOn = new Dictionary<string, int>(), ActsOff = new Dictionary<string, int>();
        }

        /// <summary>dtcli skill-trace ROLE SKILL BOSS RUNS: plays the one-skill-trial cell with the skill (the rule of skill-value) under a
        /// trace and counts how the skill is used: casts, casts on a target that already carries the status, chants, the turns the
        /// caster spends on it, the real interval between turns of a unit with and without the status, and the stats of the target
        /// before and after the cast.</summary>
        public static void SkillTrace(Ctx c, string[] a)
        {
            string role = a[0], name = a[1], cid = a[2]; int runs = int.Parse(a[3]);
            bool sample = a.Length > 4 && a[4] == "sample";
            var data = c.Data("variant");
            var skill = Kit.SkillNamed(data, name);
            (string, string)? rule = skill.Category == "Passive" ? ("ally_down", "revive") : ((string, string)?)null;
            var statusIds = skill.Effects.Where(e => e.Kind != 2).Select(e => e.Id).ToArray();
            var t = new TraceTally();
            Battle current = null;
            var statNames = new[] { "ATK", "DEF", "INT", "RES", "DEX", "AGI" };
            (Unit target, int[] stats, int hp, int maxHp, int snapshotTurn)? pending = null;

            TextTrace.PerformHook = (b, act) =>
            {
                if (act.Actor.Kind != Kind.Member) return;
                if (b != current) { current = b; t.Battles++; }
                if (act.Kind == AKind.Chant) { if (act.Skill != null && act.Skill.Name == name) t.Chants++; return; }
                t.ActorActions++;
                if (act.Actor.HasRole && act.Actor.Role == role)
                {
                    string an = act.SourceName ?? "Attack";
                    var dict = statusIds.Any(id => act.Actor.St[id] != null) ? t.ActsOn : t.ActsOff;
                    dict[an] = dict.GetValueOrDefault(an) + 1;
                }
                if (act.Skill == null || act.Skill.Name != name || act.Kind != AKind.Skill) return;
                t.Casts++;
                var targets = new List<Unit>();
                int code = act.TargetCode;
                if (code == T.SELF || code == T.NO_TARGET) targets.Add(act.Actor);
                else if (code == T.ALLY && act.Target != null) targets.Add(act.Target);
                else if (code == T.ALLIES || code == T.ALLY_ROW || code == T.EVERYONE) targets.AddRange(b.Members());
                else if (act.Target != null) targets.Add(act.Target);
                bool active = false;
                foreach (var u in targets)
                {
                    t.CastTargets++;
                    if (statusIds.Any(id => u.St[id] != null)) { t.CastTargetsActive++; active = true; }
                }
                if (active && targets.Count == 1) t.RecastActive++;
                if (targets.Count > 0)
                {
                    var u = targets[0];
                    pending = (u, new[] { u.Stat(Unit.ATK), u.Stat(Unit.DEF), u.Stat(Unit.INT), u.Stat(Unit.RES), u.Stat(Unit.DEX), u.Stat(Unit.AGI) }, u.Hp, u.MaxHp, 0);
                }
                if (sample && t.Sample.Count < 60)
                    t.Sample.Add("t=" + Fmt.Num(b.Time) + " " + act.Actor.Name + " casts " + name + " [" + string.Join(",", act.Skill.Effects.Select(e => e.Id + "/" + e.Kind)) + "] on " + string.Join(",", targets.Select(u => u.Name + (statusIds.Any(id => u.St[id] != null) ? "[active]" : ""))));
            };
            TextTrace.HitHook = (b, act, target, landed) =>
            {
                if (!(act.Actor.HasRole && act.Actor.Role == role) || target.Side == act.Actor.Side) return;
                if (statusIds.Any(id => act.Actor.St[id] != null)) { t.HitsOnTotal++; if (landed) t.HitsOnLanded++; } else { t.HitsOffTotal++; if (landed) t.HitsOffLanded++; }
            };
            TextTrace.RestoreHook = (b, u, g) => { if (sample && pending.HasValue && t.Sample.Count < 60) { t.Sample.Add("   restore " + u.Name + " +" + g); } };
            TextTrace.TurnEndHook = (b, u) =>
            {
                if (u.Kind == Kind.Member)
                {
                    double interval = u.NextTime - b.Time;
                    bool on = statusIds.Any(id => u.St[id] != null);
                    if (on) { t.IntervalOn += interval; t.TurnsOn++; } else { t.IntervalOff += interval; t.TurnsOff++; }
                }
                if (pending.HasValue)
                {
                    var p = pending.Value; pending = null;
                    for (int i = 0; i < 6; i++)
                    {
                        int after = p.target.Stat(i);
                        t.StatDelta[statNames[i]] = t.StatDelta.GetValueOrDefault(statNames[i]) + (after - p.stats[i]);
                        t.StatN[statNames[i]] = t.StatN.GetValueOrDefault(statNames[i]) + 1;
                    }
                    t.StatDelta["HP"] = t.StatDelta.GetValueOrDefault("HP") + (p.target.Hp - p.hp);
                    t.StatDelta["MaxHP"] = t.StatDelta.GetValueOrDefault("MaxHP") + (p.target.MaxHp - p.maxHp);
                    t.StatN["HP"] = t.StatN.GetValueOrDefault("HP") + 1;
                    t.StatN["MaxHP"] = t.StatN.GetValueOrDefault("MaxHP") + 1;
                    if (sample && t.Sample.Count < 60) t.Sample.Add("   target " + p.target.Name + " after turn: hp " + p.target.Hp + "/" + p.target.MaxHp + " (was " + p.hp + "/" + p.maxHp + ")");
                }
            };
            try
            {
                var job = SkillValue.Job(c, role, cid, skill, true, 0, runs, rule: rule);
                job.Trace = 1;
                var res = c.Run(job);
                var won = res.Runs.Where(r => r.Won).ToList();
                Trials.Say(c, name + " (" + role + ") " + cid + ", " + runs + " traced battles: won " + Py.Pct((double)won.Count / res.Runs.Length, 0)
                           + " | length " + Py.F(won.Count > 0 ? Py.Sum(won.Select(r => r.Time)) / won.Count : 0, 1));
                double nb = Math.Max(1, t.Battles);
                Trials.Say(c, "  casts/battle " + Py.F(t.Casts / nb, 2) + " | chants/battle " + Py.F(t.Chants / nb, 2) + " | member actions/battle " + Py.F(t.ActorActions / nb, 1)
                           + " | share of member actions " + Py.Pct(t.Casts / (double)Math.Max(1, t.ActorActions), 1));
                Trials.Say(c, "  cast targets already carrying the status: " + t.CastTargetsActive + "/" + t.CastTargets + " ("
                           + Py.Pct(t.CastTargetsActive / (double)Math.Max(1, t.CastTargets), 0) + "); single-target recasts on active: " + t.RecastActive);
                Trials.Say(c, "  mean interval to next turn, unit with status " + (t.TurnsOn > 0 ? Py.F(t.IntervalOn / t.TurnsOn, 3) : "-") + " (" + t.TurnsOn + " turns) vs without "
                           + (t.TurnsOff > 0 ? Py.F(t.IntervalOff / t.TurnsOff, 3) : "-") + " (" + t.TurnsOff + " turns)");
                Trials.Say(c, "  mean change in the first target by the end of the casting turn: " + string.Join(", ", t.StatDelta.Select(kv => kv.Key + " " + Py.F(kv.Value / Math.Max(1, t.StatN[kv.Key]), 1))));
                Trials.Say(c, "  actions of the " + role + " with the status on : " + string.Join(", ", t.ActsOn.OrderByDescending(kv => kv.Value).Take(8).Select(kv => kv.Key + " " + kv.Value)));
                Trials.Say(c, "  actions of the " + role + " with the status off: " + string.Join(", ", t.ActsOff.OrderByDescending(kv => kv.Value).Take(8).Select(kv => kv.Key + " " + kv.Value)));
                Trials.Say(c, "  hit rate of the " + role + " on foes: status on " + Py.Pct(t.HitsOnLanded / (double)Math.Max(1, t.HitsOnTotal), 1) + " (" + t.HitsOnTotal + " blows), off " + Py.Pct(t.HitsOffLanded / (double)Math.Max(1, t.HitsOffTotal), 1) + " (" + t.HitsOffTotal + ")");
                foreach (var l in t.Sample) Trials.Say(c, "    " + l);
            }
            finally { TextTrace.PerformHook = null; TextTrace.TurnEndHook = null; TextTrace.RestoreHook = null; TextTrace.HitHook = null; }
        }

        /// <summary>dtcli skill-rule-trial ROLE SKILL BOSSES RUNS CONDITION [ACTION [before_status]]: one-skill-trial with the condition of the
        /// rule (and, when given, its action) set by hand, to see what a skill is worth under a rule other than "always".</summary>
        public static void SkillRuleTrial(Ctx c, string[] a)
        {
            string role = a[0], name = a[1]; var bosses = a[2].Split(';'); int runs = int.Parse(a[3]); string cond = a[4];
            string act = a.Length > 5 && a[5] != "-" ? a[5] : null;
            bool beforeStatus = a.Length > 6 && a[6] == "before_status";
            var data = c.Data("variant");
            var skill = Kit.SkillNamed(data, name);
            var rule = (cond, act ?? SkillValue.RuleFor(c, skill).act);
            var figures = new Dictionary<(string, bool), Obj>();
            foreach (var cid in bosses)
                foreach (var use in new[] { false, true })
                {
                    JobSpec job;
                    if (use && beforeStatus)
                    {
                        // the same job, with the rule put before the first status row of the role
                        job = SkillValue.Job(c, role, cid, skill, use, 0, runs, rule: rule);
                        var rows = SkillValue.RowsWithRule(c, role, rule.Item1, rule.Item2, 0, true);
                        job = Jb.Make(c, "variant", cid, runs: runs, crown: 0, policyRows: rows, name: name + "|" + role + "|" + cid + "|bs",
                                      recipe: RecipeOf(c, role, cid, skill, use));
                    }
                    else job = SkillValue.Job(c, role, cid, skill, use, 0, runs, rule: rule);
                    figures[(cid, use)] = SkillValue.Figures(c.Run(job));
                }
            Trials.Say(c, name + " (" + role + ") rule " + rule.Item1 + " / " + rule.Item2 + (beforeStatus ? " before status" : "") + ", " + runs + " battles: without > with | wins | length of the won fights | HP left");
            foreach (var cid in bosses)
            {
                var x = figures[(cid, false)]; var y = figures[(cid, true)];
                string length = Py.Truthy(x.Get("time_won")) && Py.Truthy(y.Get("time_won")) ? Py.F(x.D("time_won"), 1) + " > " + Py.F(y.D("time_won"), 1) : "-";
                Trials.Say(c, cid + " | " + Py.Pct(x.D("won"), 0) + " > " + Py.Pct(y.D("won"), 0) + " | " + length + " | " + Py.Pct(x.D("hp_left"), 0) + " > " + Py.Pct(y.D("hp_left"), 0));
            }
        }

        static Obj RecipeOf(Ctx c, string role, string cid, Skill skill, bool use)
        {
            var cp = c.Checkpoint(cid); var sc = c.Sc("variant");
            int levels = skill.Levels != 0 ? skill.Levels : 1;
            var extra = new Dictionary<int, int> { { skill.Id, use ? levels : 0 } };
            return new Obj
            {
                { "drop_last", true }, { "items", "first_kept" },
                { "tested", Jb.L(new Obj { { "role", role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true },
                                           { "extra_skills", Jb.Dict(extra.Select(kv => new KeyValuePair<string, object>(kv.Key.ToString(), (long)kv.Value))) } }) },
            };
        }
    }
}
