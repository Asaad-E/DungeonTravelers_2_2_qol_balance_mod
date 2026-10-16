using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>The trial scripts of measures/ and tools/ that play battles: each is a command of dtcli with the arguments of its script, printing what the script
    /// prints. They take the cases, parties and constants of the script from the snapshot (section measures, trials) and the data they change from Kit.</summary>
    public static class Trials
    {
        public static Obj Inp(Ctx c, string script) => c.In("trials").O(script);

        public static List<string> Strings(object list) => ((List<object>)list).Select(x => (string)x).ToList();

        /// <summary>The summary a job of the engine gives (sim.measures.summary of its runs).</summary>
        public static Summary SummaryOf(JobResult done) => Summary.Of(done.Runs.ToList());

        public static double Share(JobResult done) => (double)done.Runs.Count(r => r.Won) / done.Runs.Length;

        /// <summary>sum(r['time'] for r in won) / len(won) if won else 0</summary>
        public static double WonTime(JobResult done)
        {
            var won = done.Runs.Where(r => r.Won).ToList();
            return won.Count > 0 ? Py.Sum(won.Select(r => r.Time)) / won.Count : 0;
        }

        public static void Say(Ctx c, string line) => c.Say(line);

        // --- curve_recheck.py -------------------------------------------------------------------------------------------
        public static void CurveRecheck(Ctx c, string[] a)
        {
            var bosses = a[0].Split(';'); int runs = int.Parse(a[1]);
            var jobs = bosses.Select(cid => new Obj
            {
                { "id", "cc-" + cid }, { "measure", "check_change" }, { "side", "vanilla" }, { "changed_side", "variant" }, { "checkpoints", Jb.L(cid) }, { "runs", (long)runs },
            }).ToList();
            Say(c, runs + " battles: the game > the variant | wins | length | lowest HP | pressure | out of the window");
            foreach (var raw in c.Measure(jobs))
                foreach (Obj row in raw.A("rows"))
                {
                    var before = M.Summary(row.O("before")); var after = M.Summary(row.O("after"));
                    var outList = row.A("out").Select(x => (string)x).ToList();
                    Say(c, row.S("cid") + " | " + string.Join(" | ", new[] { "won", "time", "lowest_hp", "pressure" }.Select(k => DifficultyCurve.Fmt(before.Get(k), k) + " > " + DifficultyCurve.Fmt(after.Get(k), k)))
                           + " | " + (outList.Count > 0 ? string.Join(", ", outList) : "within"));
                }
        }

        // --- etoile_dances.py -------------------------------------------------------------------------------------------
        public static void EtoileDances(Ctx c, string[] a)
        {
            var inp = Inp(c, "etoile_dances");
            string cid = a[0]; int runs = a.Length > 1 ? int.Parse(a[1]) : 60;
            var dances = inp.O("dances");
            var usual = c.Setup.Policies;
            var wanted = new[] { "status:195", "status:199", "status:201" };
            var picks = Enumerable.Range(0, usual.Count).Where(i => usual[i].Str("Role") == "etoile" && wanted.Contains(usual[i].Str("Action"))).ToList();
            if (picks.Count != 2) throw new InvalidOperationException("expected two dance rules, found " + picks.Count);
            var sc = c.Sc("variant");
            int level = sc.ReferenceLevels()[cid].level;
            foreach (List<object> pair in inp.A("pairs"))
            {
                string x = (string)pair[0], y = (string)pair[1];
                var rows = new List<object>();
                for (int i = 0; i < usual.Count; i++)
                {
                    var o = Jb.RowObj(usual[i]);
                    if (i == picks[0]) o.Set("Action", "status:" + Py.Str(dances.Get(x)));
                    else if (i == picks[1]) o.Set("Action", "status:" + Py.Str(dances.Get(y)));
                    rows.Add(o);
                }
                var done = c.Run(ClassStages.Job(c, cid, "etoile", runs, policyRows: rows));
                var res = ClassStages.Figures(done.Runs, runs, done.Spec.TestedNames.Count > 0 ? done.Spec.TestedNames[0] : null, level, "etoile");
                Say(c, cid + " | " + x + " + " + y + " | won " + Py.Pct(res.D("won"), 0) + " | length " + Py.F(res.D("time"), 1));
            }
        }

        // --- magic_wall.py ----------------------------------------------------------------------------------------------
        static (string name, double value) BestOption(Ctx c, string side, string role, string cid)
        {
            var item = SkillWorth.Item(c, c.Data(side), cid, role, 0, side);
            item.Set("id", "scores0"); item.Set("measure", "skill_scores");
            var answer = c.Measure(new List<Obj> { item })[0];
            var scores = new List<(string name, double value)>();
            foreach (List<object> pair in (List<object>)answer.A("contexts")[0])
            {
                string name = (string)pair[0]; double value = Py.Num(pair[1]);
                int at = scores.FindIndex(x => x.name == name);
                if (at >= 0) scores[at] = (name, value); else scores.Add((name, value));
            }
            if (scores.Count == 0) throw new InvalidOperationException("ValueError");
            var best = scores[0];
            foreach (var s in scores) if (s.value > best.value) best = s;
            return best;
        }

        public static void MagicWall(Ctx c, string[] a)
        {
            var elements = Strings(Inp(c, "magic_wall").Get("elements"));
            var ids = c.Setup.Checkpoints.Select(r => r.Str("ID")).ToList();
            ids = ids.Skip(ids.IndexOf("C30")).ToList();
            foreach (var cid in ids)
            {
                var cells = new List<string>();
                string wall = "";
                foreach (var (tag, side) in new[] { ("vanilla", "vanilla"), ("mod", "variant") })
                {
                    var data = c.Data(side);
                    double mage, lord; string spell;
                    try
                    {
                        var m = BestOption(c, side, "mage", cid); spell = m.name; mage = m.value;
                        lord = BestOption(c, side, "dark lord", cid).value;
                    }
                    catch (Exception error)
                    {
                        cells.Add(tag + ": " + (error.Message == "ValueError" ? "ValueError" : error.GetType().Name));
                        continue;
                    }
                    cells.Add(lord != 0 ? tag + " " + Py.Pct(mage / lord, 0) + " (" + spell + ")" : tag + " -");
                    var cp = c.Checkpoint(cid);
                    var numbers = Scenario.BattleNumbers(cp);
                    var fight = data.Fixed.First(b => b.Floor == cp.Str("Floor") && b.Number == numbers[numbers.Length - 1]);
                    wall = string.Join("; ", fight.Enemies.Take(3).Select(e => data.Enemies[e.enemy].Name + " " + string.Join("/", elements.Select(el => data.Enemies[e.enemy].Resist[Array.IndexOf(new[] { "slash", "stab", "bash", "fire", "water", "wind", "earth", "lightning" }, el)]))));
                }
                Say(c, cid + " | " + string.Join(" | ", cells) + " | " + wall);
            }
        }

        // --- measure_open_rows.py -----------------------------------------------------------------------------------------
        public static void MeasureOpenRows(Ctx c, string[] a)
        {
            var inp = Inp(c, "measure_open_rows");
            string name = a[0];
            var data = c.Data("variant");
            var setup = c.Setup;
            var skill = Kit.SkillNamed(data, name, true);
            string role; Obj st;
            var roleOf = inp.O("role"); var stageOf = inp.O("stage"); var weaponOf = inp.O("weapon");
            if (roleOf.Has(name))
            {
                role = (string)roleOf.Get(name);
                st = M.Stages(c).First(s => s.S("Stage") == (string)stageOf.Get(name));
            }
            else { var found = SkillValue.Place(c, data, skill); role = found.Value.role; st = found.Value.stage; }
            string setupName = null;
            if (weaponOf.Has(name)) setupName = c.AddSetup(Kit.WithRole(setup, role, "Weapon", weaponOf.Get(name)));
            bool passive = skill.Category == "Passive";
            int runs = c.SetInt("check_runs");
            var cells = new List<object>();
            foreach (var cid in ClassStages.Checkpoints(st))
            {
                var cell = new Obj { { "checkpoint", cid } };
                foreach (var use in new[] { false, true })
                {
                    (string, string)? rule = null;
                    if (passive && use)
                    {
                        // a passive needs no rule: the one added is a copy of the role's own damage rule, placed just before it
                        var own = setup.Policies.Where(r => r.Str("Role") == role).OrderBy(r => Py.Num(r.Get("Order"))).First(r => r.Str("Action").StartsWith("damage"));
                        rule = (own.Str("Condition"), own.Str("Action"));
                    }
                    var done = c.Run(SkillValue.Job(c, role, cid, skill, use, 0, runs, setupName: setupName, rule: rule));
                    cell.Set(use ? "with" : "without", SkillValue.Figures(done));
                }
                cells.Add(cell);
                Say(c, name + " " + role + " " + Py.ReprObj(cell));
            }
            var outObj = new Obj { { "skill", name }, { "role", role }, { "stage", st.S("Stage") }, { "cells", cells } };
            c.WriteText(c.Path("measures", "open_rows_" + name.Replace(" ", "_") + ".json"), PyJson.Dump(outObj, 1), false);
        }
    }
}
