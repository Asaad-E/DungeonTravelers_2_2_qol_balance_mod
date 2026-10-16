using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>measures/skill_value_contested.py: the skills SKILL_VALUE.md leaves "to read", measured at the bosses the party does not win every time;
    /// measures/SKILL_VALUE_CONTESTED.md.</summary>
    public static class SkillValueContested
    {
        static List<(string name, string role)> ToRead(Ctx c)
        {
            var names = new List<(string, string)>();
            foreach (var line in Ctx.ReadText(c.Path("docs", "generated", "SKILL_VALUE.md")).Split('\n'))
            {
                var cells = line.Trim().Trim('|').Split('|').Select(x => x.Trim()).ToList();
                if (cells.Count == 6 && cells[5] == "to read")
                {
                    string role = cells[1]; int at = role.IndexOf(" (", StringComparison.Ordinal);
                    names.Add((cells[0], at >= 0 ? role.Substring(0, at) : role));
                }
            }
            return names;
        }

        public static void Run(Ctx c, int runs = 30)
        {
            var inp = c.In("skill_value_contested");
            var contested = inp.A("contested").Select(x => (string)x).ToList();
            var notBattle = inp.O("not_battle");
            var data = c.Data("variant");
            var sc = c.Sc("variant");
            var levels = sc.ReferenceLevels();
            var names = ToRead(c);
            var plan = new List<(string name, string role, string kind, List<(string cid, int without, int with)> cells)>();
            var jobs = new List<JobSpec>();
            foreach (var (name, role) in names)
            {
                var skill = data.SkillList.First(s => s.Name == name && s.Classes.Length > 0);
                var cells = new List<(string, int, int)>();
                string kind = null;
                if (notBattle.Has(name)) kind = (string)notBattle.Get(name);
                else if (skill.Effects.Any(e => SkillValue.IsAilment(e.Id) && e.Kind != 2)) kind = "ailment";
                else
                    foreach (var cid in contested)
                    {
                        var learnable = new HashSet<int>(sc.ClassesSoFar(c.Setup.Roles[role], levels[cid].level));
                        if (!skill.Classes.Any(learnable.Contains)) continue;
                        cells.Add((cid, jobs.Count, jobs.Count + 1));
                        jobs.Add(SkillValue.Job(c, role, cid, skill, false, 0, runs));
                        jobs.Add(SkillValue.Job(c, role, cid, skill, true, 0, runs));
                    }
                plan.Add((name, role, kind, cells));
            }
            var done = c.Run(jobs);
            var rows = new List<object>();
            foreach (var p in plan)
            {
                var cells = p.cells.Select(x => (object)new Obj { { "checkpoint", x.cid }, { "without", SkillValue.Figures(done[x.without]) }, { "with", SkillValue.Figures(done[x.with]) } }).ToList();
                var row = new Obj { { "skill", p.name }, { "role", p.role }, { "cells", cells } };
                if (p.kind != null) row.Set("kind", p.kind);
                rows.Add(row);
            }
            Parts.Write(c, "skill_value_contested", rows);
        }

        public static void Report(Ctx c)
        {
            var inp = c.In("skill_value_contested");
            double wins0 = inp.D("wins"), length0 = inp.D("length"), hp0 = inp.D("hp");
            var contested = inp.A("contested").Select(x => (string)x).ToList();
            var rows = Parts.Read(c, "skill_value_contested");
            rows = rows.Select((r, i) => (r, i)).OrderBy(x => x.r.S("skill"), StringComparer.Ordinal).ThenBy(x => x.i).Select(x => x.r).ToList();
            var lines = new List<string>();
            var tally = new List<(string key, int n)>();
            foreach (var r in rows)
            {
                string verdict, best;
                if (r.Has("kind") && Py.Truthy(r.Get("kind")))
                {
                    verdict = r.S("kind") == "ailment" ? "see SKILL_AILMENTS.md" : "out of the fight: " + r.S("kind");
                    best = "-";
                }
                else if (r.A("cells").Count == 0) { verdict = "not learnt by the role at these bosses"; best = "-"; }
                else
                {
                    var found = new List<(double score, string cid, double wins, double length, double hp)>();
                    foreach (Obj cell in r.A("cells"))
                    {
                        var a = cell.O("without"); var b = cell.O("with");
                        double wins = b.D("won") - a.D("won");
                        double length = Py.Truthy(a.Get("time_won")) && Py.Truthy(b.Get("time_won")) ? 1 - b.D("time_won") / a.D("time_won") : 0.0;
                        double hp = b.D("hp_left") - a.D("hp_left");
                        found.Add((Math.Max(Math.Max(wins / wins0, length / length0), hp / hp0), cell.S("checkpoint"), wins, length, hp));
                    }
                    var top = found[0];
                    foreach (var f in found.Skip(1))
                    {
                        int cmp = f.score.CompareTo(top.score);
                        if (cmp == 0) cmp = string.CompareOrdinal(f.cid, top.cid);
                        if (cmp == 0) cmp = f.wins.CompareTo(top.wins);
                        if (cmp == 0) cmp = f.length.CompareTo(top.length);
                        if (cmp == 0) cmp = f.hp.CompareTo(top.hp);
                        if (cmp > 0) top = f;
                    }
                    verdict = top.score >= 1 ? "serves" : "nothing shown";
                    best = top.cid + ": wins " + Py.Pct(top.wins, 0, true) + ", length " + Py.Pct(top.length, 0, true) + ", HP left " + Py.F(top.hp * 100, 0, true) + " points";
                }
                string key = verdict.Split(':')[0];
                int at = tally.FindIndex(t => t.key == key);
                if (at >= 0) tally[at] = (key, tally[at].n + 1); else tally.Add((key, 1));
                lines.Add("| " + r.S("skill") + " | " + r.S("role") + " | " + best + " | " + verdict + " |");
            }
            var ordered = tally.Select((t, i) => (t, i)).OrderBy(x => -x.t.n).ThenBy(x => x.i).Select(x => x.t).ToList();
            var text = new List<string>
            {
                "# The support skills left \"to read\", at the contested bosses (generated by measures/skill_value_contested.py)", "",
                "Bosses: " + string.Join(", ", contested) + ". Each skill with and without, as tools/skill_value.py plays it; the best of its bosses is shown. Serves: " + Py.Pct(wins0, 0)
                    + " of wins, " + Py.Pct(length0, 0) + " of length or " + Py.F(hp0 * 100, 0) + " points of the HP the party ends with.", "",
                "**" + string.Join("; ", ordered.Select(t => t.n + " " + t.key)) + " (of " + rows.Count + ").**", "",
                "| Skill | Played as | Best boss | Verdict |", "|---|---|---|---|",
            };
            text.AddRange(lines);
            c.WriteText(c.Path("measures", "SKILL_VALUE_CONTESTED.md"), M.Lines(text), true);
        }
    }
}
