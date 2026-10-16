using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        static Obj Inp(Ctx c, string script) => Trials.Inp(c, script);

        /// <summary>class_stages.play_engine of a role on a side, with the setup and the rows of policies the trial has made.</summary>
        static Obj PlayRole(Ctx c, string side, string setupName, string cid, string role, int runs)
        {
            var done = c.Run(ClassStages.Job(c, cid, role, runs, side: side, setupName: setupName));
            return ClassStages.Figures(done.Runs, runs, done.Spec.TestedNames.Count > 0 ? done.Spec.TestedNames[0] : null, c.Sc(side).ReferenceLevels()[cid].level, role);
        }

        // --- samba_trial.py -----------------------------------------------------------------------------------------
        public static void SambaTrial(Ctx c, string[] a)
        {
            string cid = a[0]; int runs = a.Length > 1 ? int.Parse(a[1]) : 100;
            var factors = new[] { 1.0, 1.5, 2.0, 2.5 };
            var usual = c.Setup.Policies;
            // her second dance, whichever the sheet gives her (measure_config.json, trials, samba_trial)
            var dances = Trials.Strings(Inp(c, "samba_trial").Get("second"));
            int second = usual.FindIndex(r => r.Str("Role") == "etoile" && dances.Contains(r.Str("Action")));
            if (second < 0) throw new InvalidOperationException("the sheet Policies has no rule of the etoile with " + string.Join(" or ", dances));
            var baseData = c.Data("variant");
            var skill = Kit.SkillNamed(baseData, "Alluring Samba");
            Func<string, string, Obj> play = (side, setupName) => PlayRole(c, side, setupName, cid, "etoile", runs);
            var res = play("variant", null);
            Trials.Say(c, cid + " | Waltz + Mazurka | won " + Py.Pct(res.D("won"), 0) + " | length " + Py.F(res.D("time"), 1));
            var rows = usual.Select((r, i) => i == second ? Kit.With(r, "Action", "status:196") : r).ToList();
            string setupName2 = c.AddSetup(c.Setup.WithPolicies(rows));
            foreach (var factor in factors)
            {
                var scaled = Kit.Mapped(skill, e => e.Id == 196 ? Kit.WithValues(e, e.Values.Select(v => Num.Float(PyMath.RoundTo(v * factor, 3))).ToList()) : e);
                string side = c.AddSide(Kit.WithSkill(baseData, skill, scaled));
                res = play(side, setupName2);
                Trials.Say(c, cid + " | Waltz + Samba x" + Py.G(factor) + " (" + Py.Pct(skill.Effects[0].Values[skill.Effects[0].Values.Length - 1] * factor, 0) + " DEF at the top level) | won "
                           + Py.Pct(res.D("won"), 0) + " | length " + Py.F(res.D("time"), 1));
            }
        }

        // --- etoile_trial.py ----------------------------------------------------------------------------------------
        public static void EtoileTrial(Ctx c, string[] a)
        {
            var inp = Inp(c, "etoile_trial");
            var dances = inp.O("dances");
            string cid = a[0];
            int runs = a.Length > 1 && a[1].All(char.IsDigit) && a[1].Length > 0 ? int.Parse(a[1]) : 60;
            var setup = c.Setup;
            if (a.Contains("primevil"))
            {
                setup = Kit.WithRole(setup, "etoile", "Skill priority", "Primevil; " + setup.Roles["etoile"].Str("Skill priority"));
                var rows = new List<Row>(setup.Policies);
                var added = new Row();
                added.Cells["Role"] = "etoile"; added.Cells["Order"] = 1.5; added.Cells["Condition"] = "party_hp_below:0.5"; added.Cells["Action"] = "heal:0.5";
                rows.Add(added);
                setup = setup.WithPolicies(rows);
            }
            string setupName = c.AddSetup(setup);
            var variant = c.Data("variant");
            var meta = c.Setup.Battery.First(b => b.name == "Meta").roles;
            var parties = new List<(string label, List<string> roles)>
            {
                ("Meta, Etoile for Diva", meta.Select(r => r == "diva" ? "etoile" : r).ToList()),
                ("Meta, Etoile for Papillon", meta.Select(r => r == "papillon" ? "etoile" : r).ToList()),
            };
            var factors = inp.A("factors").Select(Py.Num).ToList();
            foreach (var (label, roles) in parties)
            {
                var cells = new List<string>();
                foreach (var factor in factors)
                {
                    var changes = new List<(Skill, Skill)>();
                    foreach (var s in variant.SkillList)
                    {
                        if (!dances.Has(s.Name) || s.Classes.Length == 0) continue;
                        int effect = (int)Py.Num(dances.Get(s.Name));
                        changes.Add((s, Kit.Mapped(s, e => e.Id == effect ? Kit.WithValues(e, e.Values.Select(v => Num.Float(PyMath.RoundTo(v * factor, 3))).ToList()) : e)));
                    }
                    string side = c.AddSide(Kit.WithSkills(variant, changes));
                    var done = c.Run(Jb.Make(c, side, cid, roles: roles, runs: runs, setupName: setupName));
                    var s2 = Trials.SummaryOf(done);
                    cells.Add("x" + Py.Repr(factor) + " " + Py.Pct(s2.Won, 0) + " / " + Py.F(s2.Time ?? 0.0, 1));
                }
                Trials.Say(c, cid + " | " + label + " | " + string.Join(" | ", cells));
            }
        }

        // --- dance_trial.py -----------------------------------------------------------------------------------------
        public static void DanceTrial(Ctx c, string[] a)
        {
            var inp = Inp(c, "dance_trial");
            var parties = inp.O("parties"); var cases = inp.O("cases"); var dances = inp.O("dances");
            var bosses = a[0].Split(';'); int runs = int.Parse(a[1]);
            var vanilla = c.Data("vanilla"); var variant = c.Data("variant");
            var played = new Dictionary<(string, string, string), (double won, double time)>();
            foreach (var party in parties.Keys)
                foreach (var cid in bosses)
                    foreach (var kv in cases)
                    {
                        object share = kv.Value;
                        var data = share == null ? vanilla : variant;
                        string side = share == null ? "vanilla" : "variant";
                        if (share != null && Py.Num(share) < 1)
                        {
                            var changes = new List<(Skill, Skill)>();
                            foreach (var dance in dances)
                            {
                                var mine = Kit.SkillNamed(data, dance.Key); var game = Kit.SkillNamed(vanilla, dance.Key);
                                int effect = (int)Py.Num(dance.Value);
                                var old = Kit.Values(game, effect);
                                double s = Py.Num(share);
                                changes.Add((mine, Kit.Mapped(mine, e => e.Id == effect ? Kit.WithValues(e, e.Values.Zip(old, (x, o) => Num.Float(o.V + (x - o.V) * s)).ToList()) : e)));
                            }
                            side = c.AddSide(Kit.WithSkills(data, changes));
                        }
                        var done = c.Run(Jb.Make(c, side, cid, roles: Trials.Strings(parties.Get(party)), runs: runs, name: party + "|" + cid + "|" + kv.Key));
                        played[(party, cid, kv.Key)] = (Trials.Share(done), Trials.WonTime(done));
                    }
            foreach (var party in parties.Keys)
            {
                Trials.Say(c, party + " " + Py.ReprObj(parties.Get(party)));
                foreach (var k in cases.Keys)
                    Trials.Say(c, "  " + k.PadRight(30) + " " + string.Join(" | ", bosses.Select(cid => cid + " " + Py.Pct(played[(party, cid, k)].won, 0) + " (" + Py.F(played[(party, cid, k)].time, 0) + "t)")));
            }
        }

        // --- def_debuff_trial.py ------------------------------------------------------------------------------------
        public static void DefDebuffTrial(Ctx c, string[] a)
        {
            var inp = Inp(c, "def_debuff_trial");
            var parties = inp.O("parties");
            var cases = Trials.Strings(inp.Get("cases"));
            string samba = (string)inp.Get("samba"), pierce = (string)inp.Get("pierce");
            int defDown = (int)Py.Num(inp.Get("def_down"));
            var usualActions = Trials.Strings(inp.Get("usual"));
            var bosses = a[0].Split(';'); int runs = int.Parse(a[1]);
            var vanilla = c.Data("vanilla"); var variant = c.Data("variant");
            var played = new Dictionary<(string, string, string), (double won, double time, int level)>();
            foreach (var party in parties.Keys)
                foreach (var cid in bosses)
                    foreach (var k in cases)
                    {
                        var data = k.StartsWith("game") ? vanilla : variant;
                        string side = k.StartsWith("game") ? "vanilla" : "variant";
                        var setup = c.Setup;
                        var sambaSkill = Kit.SkillNamed(data, samba);
                        if (k.Contains("Samba"))
                        {
                            var size = Kit.Values(sambaSkill, defDown);
                            if (k.Contains("of the game")) size = Kit.Values(Kit.SkillNamed(vanilla, samba), defDown);
                            else if (k.Contains(pierce))
                            {
                                var last = Kit.Values(Kit.SkillNamed(data, pierce), 162);
                                var add = last[last.Length - 1];
                                size = size.Select(x => x + add).ToArray();
                            }
                            side = c.AddSide(Kit.WithSkill(data, sambaSkill, Kit.WithEffect(sambaSkill, defDown, size)));
                            var rows = setup.Policies;
                            var picks = Enumerable.Range(0, rows.Count).Where(i => rows[i].Str("Role") == "etoile" && usualActions.Contains(rows[i].Str("Action"))).ToList();
                            var changed = rows.Select((r, i) => i == picks[0] ? Kit.With(r, "Action", "status:" + defDown) : i == picks[1] ? Kit.With(r, "Action", usualActions[0]) : r).ToList();
                            setup = Kit.WithRole(setup.WithPolicies(changed), "etoile", "Skill priority", samba + "; " + setup.Roles["etoile"].Str("Skill priority"));
                        }
                        string setupName = c.AddSetup(setup);
                        var done = c.Run(Jb.Make(c, side, cid, roles: Trials.Strings(parties.Get(party)), runs: runs, setupName: setupName, name: party + "|" + cid + "|" + k));
                        var sc = c.Sc(k.StartsWith("game") ? "vanilla" : "variant");
                        var levels = new Scenario(c.Snap.Sides[side], setup).AllocateSkills(setup.Roles["etoile"], c.Sc(k.StartsWith("game") ? "vanilla" : "variant").ReferenceLevels()[cid].level, int.MaxValue);
                        int level = levels.Where(x => x.id == sambaSkill.Id).Select(x => x.level).FirstOrDefault();
                        played[(party, cid, k)] = (Trials.Share(done), Trials.WonTime(done), level);
                    }
            foreach (var party in parties.Keys)
            {
                Trials.Say(c, party + " " + Py.ReprObj(parties.Get(party)));
                foreach (var k in cases)
                    Trials.Say(c, "  " + k.PadRight(36) + " " + string.Join(" | ", bosses.Select(cid =>
                    {
                        var p = played[(party, cid, k)];
                        return cid + " " + Py.Pct(p.won, 0) + " (" + Py.F(p.time, 0) + "t, Samba " + p.level + ")";
                    })));
            }
        }

        // --- sage_buffs_trial.py ------------------------------------------------------------------------------------
        public static void SageBuffsTrial(Ctx c, string[] a)
        {
            var inp = Inp(c, "sage_buffs_trial");
            var chanted = Trials.Strings(inp.Get("chanted"));
            var sized = inp.O("sized");
            var extraRules = Trials.Strings(inp.Get("extra_rules"));
            var bosses = a[0].Split(';'); int runs = int.Parse(a[1]);
            var cases = new List<(double? chant, double size, int rules)>();
            foreach (int rules in new[] { 2, 5 }) foreach (double size in new[] { 1.0, 1.2 }) foreach (double? chant in new double?[] { null, 2.0, 3.0 }) cases.Add((chant, size, rules));
            var variant = c.Data("variant");
            var results = new Dictionary<((double?, double, int), string), Obj>();
            foreach (var cs in cases)
            {
                var (chant, size, rules) = cs;
                var changes = new List<(Skill, Skill)>();
                foreach (var name in chanted)
                {
                    var skill = Kit.SkillNamed(variant, name);
                    var mine = skill;
                    if (chant != null) mine = Kit.WithCast(mine, mine.Cast.Select(x => Math.Max(chant.Value, x)).ToArray());
                    if (sized.Has(name) && size != 1.0)
                    {
                        int effect = (int)Py.Num(sized.Get(name));
                        mine = Kit.Mapped(mine, e => e.Id == effect ? Kit.WithValues(e, e.Values.Select(v => Num.Float(PyMath.RoundTo(v * size, 2))).ToList()) : e);
                    }
                    changes.Add((skill, mine));
                }
                string side = c.AddSide(Kit.WithSkills(variant, changes));
                var setup = c.Setup;
                if (rules == 5)
                {
                    var policies = setup.Policies;
                    double cut = Py.Num(policies.First(r => r.Str("Role") == "sage" && r.Str("Action").StartsWith("damage")).Get("Order"));
                    var rows = new List<Row>(policies);
                    for (int k = 0; k < extraRules.Count; k++)
                    {
                        var row = new Row();
                        row.Cells["Role"] = "sage"; row.Cells["Order"] = cut - 0.5 + k / 10.0; row.Cells["Condition"] = "always"; row.Cells["Action"] = extraRules[k]; row.Cells["Source"] = "";
                        rows.Add(row);
                    }
                    setup = setup.WithPolicies(rows);
                }
                string setupName = c.AddSetup(setup);
                foreach (var cid in bosses) results[(cs, cid)] = PlayRole(c, side, setupName, cid, "sage", runs);
            }
            Trials.Say(c, "the Sage in the last place of the reference party, " + runs + " battles: wins (length of the won fights)");
            foreach (var cs in cases)
            {
                var (chant, size, rules) = cs;
                string label = rules + " buffs kept up, chant " + (chant == null ? "as it is" : Py.Repr(chant.Value)) + ", size x" + Py.Repr(size);
                var cells = bosses.Select(cid => results[(cs, cid)]).ToList();
                Trials.Say(c, "  " + label.PadRight(44) + " " + string.Join(" | ", bosses.Zip(cells, (cid, r) => cid + " " + Py.Pct(r.D("won"), 0) + " (" + Py.F(Py.Truthy(r.Get("time_won")) ? r.D("time_won") : 0, 0) + "t)"))
                           + " | mean " + Py.Pct(Py.Sum(cells.Select(r => r.D("won"))) / cells.Count, 0));
            }
        }

        // --- provoke_trial.py ---------------------------------------------------------------------------------------
        public static void ProvokeTrial(Ctx c, string[] a)
        {
            var inp = Inp(c, "provoke_trial");
            var provoke = inp.A("provoke"); int enmity = (int)Py.Num(inp.Get("enmity"));
            string cid = a[0]; int runs = int.Parse(a[1]);
            var tried = a.Skip(2).Select(arg => arg.Split(',').Select(x => double.Parse(x, System.Globalization.CultureInfo.InvariantCulture)).ToList()).ToList();
            var data = c.Data("variant");
            var skill = data.Skills[((string)provoke[0], (int)Py.Num(provoke[1]))];
            var built = Kit.Values(skill, enmity);
            var vanilla = inp.A("vanilla").Select(x => x is long l ? Num.Whole(l) : Num.Float(Py.Num(x))).ToArray();
            var cases = new List<(string label, Num[] values)> { ("as the game has it", vanilla), ("as the variant has it", built) };
            foreach (var t in tried) cases.Add((Py.ReprList(t.Cast<object>()), t.Select(Num.Float).ToArray()));
            foreach (var (label, values) in cases)
            {
                string side = c.AddSide(Kit.WithSkill(data, skill, Kit.WithEffect(skill, enmity, values)));
                var res = PlayRole(c, side, null, cid, "tank", runs);
                string share = string.Join(" / ", values.Select(v => Py.Pct((20 + v.V) / (100 + v.V), 0)));
                Trials.Say(c, cid + " | " + label + " | she draws " + share + " | won " + Py.Pct(res.D("won"), 0) + " | length " + Py.F(res.D("time"), 1));
            }
        }
    }
}
