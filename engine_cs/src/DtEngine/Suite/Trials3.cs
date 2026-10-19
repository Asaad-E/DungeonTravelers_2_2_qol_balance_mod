using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        static string FloatText(double x) => Py.Repr(x);

        static double EnemyField(EnemyRec rec, string field)
        {
            string[] stats = { "atk", "def", "int", "res", "dex", "agi" };
            string[] resists = { "res_slash", "res_stab", "res_bash", "res_fire", "res_water", "res_wind", "res_earth", "res_lightning" };
            if (field == "hp") return rec.Hp;
            int s = Array.IndexOf(stats, field), r = Array.IndexOf(resists, field);
            if (s >= 0) return rec.Stats[s];
            if (r >= 0) return rec.Resist[r];
            throw new InvalidOperationException("no enemy field " + field);
        }

        // --- boss_trim_trial.py -------------------------------------------------------------------------------------
        public static void BossTrimTrial(Ctx c, string[] a)
        {
            string cid = a[0]; int runs = int.Parse(a[1]);
            var cases = new List<string> { "" }; cases.AddRange(a.Skip(2));
            var partyNames = new List<string> { "reference" };
            var win = c.In("win_rates").O("parties");
            partyNames.AddRange(win.Keys);
            var variant = c.Data("variant"); var vanilla = c.Data("vanilla");
            var cp = c.Checkpoint(cid);
            var ids = new List<int>();
            foreach (int n in Scenario.BattleNumbers(cp))
                foreach (var (e, _) in variant.FindFixed(cp.Str("Floor"), n).Enemies) if (!ids.Contains(e) && variant.Enemies.ContainsKey(e)) ids.Add(e);
            var played = new Dictionary<(string, string), (double won, double time)>();
            foreach (var p in partyNames)
                foreach (var k in cases)
                {
                    var changes = new Obj();
                    foreach (var part in k.Split(',').Where(x => x.Trim().Length > 0))
                        foreach (var id in ids)
                        {
                            var rec = variant.Enemies[id];
                            var fields = changes.Has(id.ToString()) ? changes.O(id.ToString()) : new Obj();
                            if (part.Contains('*'))
                            {
                                var xs = part.Split('*');
                                string field = xs[0].Trim();
                                fields.Set(field, (long)PyMath.Round(EnemyField(rec, field) * double.Parse(xs[1], System.Globalization.CultureInfo.InvariantCulture)));
                            }
                            else
                            {
                                string field = part.Split('=')[0].Trim();
                                fields.Set(field, (long)EnemyField(vanilla.Enemies[id], field));
                            }
                            changes.Set(id.ToString(), fields);
                        }
                    if (p == "reference")
                    {
                        var job = new Obj { { "id", "pc" }, { "measure", "play_checkpoint" }, { "side", "variant" }, { "cid", cid }, { "runs", (long)runs } };
                        if (changes.Count > 0) job.Set("enemy_changes", changes);
                        var summary = M.Summary(c.Measure(new List<Obj> { job })[0].O("summary"));
                        played[(p, k)] = (summary.D("won"), Py.Truthy(summary.Get("time")) ? summary.D("time") : 0);
                    }
                    else
                    {
                        var roles = ((string)((List<object>)win.Get(p))[0]).Split(';').Select(r => r.Trim()).ToList();
                        var done = c.Run(Jb.Make(c, "variant", cid, roles: roles, runs: runs, enemyChanges: changes, name: p + "|" + k));
                        played[(p, k)] = (Trials.Share(done), Trials.WonTime(done));
                    }
                }
            Trials.Say(c, cid + " | " + string.Join(" | ", cases.Select(k => k.Length > 0 ? k : "variant")));
            foreach (var p in partyNames)
                Trials.Say(c, "  " + p.PadRight(16) + " " + string.Join(" | ", cases.Select(k => Py.Pct(played[(p, k)].won, 0) + " (" + Py.F(played[(p, k)].time, 0) + "t)")));
        }

        // --- grand_sealbook_trial.py ----------------------------------------------------------------------------------
        public static void GrandSealbookTrial(Ctx c, string[] a)
        {
            int book = int.Parse(a[0]); string cid = a[1]; int runs = int.Parse(a[2]);
            var vanilla = c.Data("vanilla"); var data = c.Data("variant");
            var row = new Row();
            row.Cells["From checkpoint"] = c.Setup.Checkpoints[0].Str("ID"); row.Cells["Sealbook"] = (long)book; row.Cells["Name"] = ""; row.Cells["Source"] = "";
            string setupName = c.AddSetup(Kit.WithGrandSealbooks(c.Setup, new List<Row> { row }));
            var both = data.SealbookEnchants[book];
            string name = Py.Str(c.In("trials").O("sealbook_names").Get(book.ToString()));
            foreach (var (label, enchants) in new[] { ("one enchantment", vanilla.SealbookEnchants[book]), ("two", both) })
            {
                string side = c.AddSide(Kit.WithSealbook(data, book, enchants));
                var job = new Obj { { "id", "pc" }, { "measure", "play_checkpoint" }, { "side", side }, { "setup", setupName }, { "cid", cid }, { "runs", (long)runs } };
                var res = M.Summary(c.Measure(new List<Obj> { job })[0].O("summary"));
                Trials.Say(c, name + " " + cid + " | " + label + " " + Py.ReprList(enchants.Select(x => (object)(long)x)) + " | won " + Py.Pct(res.D("won"), 0) + " | length " + Py.F(res.D("time"), 1)
                           + " | lowest HP " + Py.Pct(res.D("lowest_hp"), 0));
            }
        }

        /// <summary>dtcli unique-gear-trial [runs]: at every checkpoint from the first that gives a unique piece (sheet UniqueGear) to the
        /// last, the reference party with its unique pieces against the same party in the forged pieces of its plan (chosen enchantments,
        /// sheet EnchantPlan) in their place; the register row S16 (a forged piece beats the unique ones).</summary>
        public static void UniqueGearTrial(Ctx c, string[] a)
        {
            int runs = a.Length > 0 ? int.Parse(a[0]) : 200;
            string none = c.AddSetup(Kit.WithUniqueGear(c.Setup, new List<Row>()));
            var order = c.Setup.Checkpoints.Select(r => r.Str("ID")).ToList();
            int from = c.Setup.UniqueGear.Select(r => order.IndexOf(r.Str("From checkpoint"))).Where(i => i >= 0).Min();
            foreach (var cid in order.Skip(from))
            {
                var jobs = new List<Obj>();
                foreach (var setup in new[] { (string)null, none })
                {
                    var job = new Obj { { "id", "pc" }, { "measure", "play_checkpoint" }, { "side", "variant" }, { "cid", cid }, { "runs", (long)runs } };
                    if (setup != null) job.Set("setup", setup);
                    jobs.Add(job);
                }
                var done = c.Measure(jobs);
                var u = M.Summary(done[0].O("summary")); var f = M.Summary(done[1].O("summary"));
                var pieces = c.Setup.UniqueGear.Where(r => order.IndexOf(r.Str("From checkpoint")) <= order.IndexOf(cid)).Select(r => r.Str("Piece"));
                Trials.Say(c, cid + " | unique pieces: won " + Py.Pct(u.D("won"), 0) + ", length " + Py.F(u.DN("time") ?? 0, 1) + " | forged instead: won "
                           + Py.Pct(f.D("won"), 0) + ", length " + Py.F(f.DN("time") ?? 0, 1) + " | " + string.Join(", ", pieces));
            }
        }

        // --- lize_ideas.py ------------------------------------------------------------------------------------------
        public static void LizeIdeas(Ctx c, string[] a)
        {
            var inp = Inp(c, "lize_ideas");
            string girl = (string)inp.Get("girl");
            string role = a[0], cid = a[1]; int runs = a.Length > 2 ? int.Parse(a[2]) : 100;
            var cp = c.Checkpoint(cid);
            foreach (List<object> pair in inp.A("ideas"))
            {
                string label = (string)pair[0]; object idea = pair[1];
                var tested = new Obj { { "role", role }, { "character", girl }, { "no_unique", !(idea is string s && s == "own") }, { "forge", c.Sc("variant").ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true } };
                if (idea is List<object> tup) tested.Set("passives_add", new Obj { { Py.Str(tup[0]), tup[1] } });
                var recipe = new Obj { { "name_not", girl }, { "first", 4L }, { "items", "first_kept" }, { "tested", Jb.L(tested) } };
                var res = c.Run(Jb.Make(c, "variant", cid, runs: runs, crown: 0, recipe: recipe, name: role + "|" + cid + "|" + label));
                var won = res.Runs.Where(r => r.Won).ToList();
                Trials.Say(c, role + " " + cid + " | " + label + " | won " + Py.Pct((double)won.Count / res.Runs.Length, 0) + " | length "
                           + Py.F(won.Count > 0 ? Py.Sum(won.Select(r => r.Time)) / won.Count : 0, 1) + " | HP left " + Py.Pct(Py.Sum(res.Runs.Select(r => r.HpLeft)) / res.Runs.Length, 0));
            }
        }

        // --- mercenary_trial.py -------------------------------------------------------------------------------------
        public static void MercenaryTrial(Ctx c, string[] a)
        {
            string name = a[0], cid = a[1]; int runs = int.Parse(a[2]);
            var factors = new List<(string stat, string factor)>();
            string without = null;
            foreach (var arg in a.Skip(3))
            {
                var kv = arg.Split(new[] { '=' }, 2);
                if (kv[0] == "without") without = kv[1]; else factors.Add((kv[0], kv[1]));
            }
            var data = c.Data("variant");
            string side = "variant";
            if (factors.Count > 0) side = c.AddSide(Kit.WithGuestScaled(data, name, factors.Select(f => (f.stat, double.Parse(f.factor, System.Globalization.CultureInfo.InvariantCulture)))));
            var recipe = without != null ? new Obj { { "role_not", without } } : null;
            var res = c.Run(Jb.Make(c, side, cid, runs: runs, crown: 0, guest: name == "summon" ? null : name == "none" ? "none" : name, recipe: recipe, name: name + "|" + cid));
            var won = res.Runs.Where(r => r.Won).ToList();
            string shown = string.Join(" ", a.Skip(3));
            Trials.Say(c, name + " " + cid + " " + (shown.Length > 0 ? shown : "as she is") + " | won " + Py.Pct((double)won.Count / res.Runs.Length, 0) + " | length "
                       + Py.F(won.Count > 0 ? Py.Sum(won.Select(r => r.Time)) / won.Count : 0, 1) + " | HP left " + Py.Pct(Py.Sum(res.Runs.Select(r => r.HpLeft)) / res.Runs.Length, 0));
        }

        // --- one_skill_trial.py -------------------------------------------------------------------------------------
        public static void OneSkillTrial(Ctx c, string[] a)
        {
            string role = a[0], name = a[1]; var bosses = a[2].Split(';'); int runs = int.Parse(a[3]);
            var data = c.Data("variant");
            var skill = Kit.SkillNamed(data, name);
            var figures = new Dictionary<(string, bool), Obj>();
            foreach (var cid in bosses)
                foreach (var use in new[] { false, true })
                {
                    (string, string)? rule = skill.Category == "Passive" ? ("ally_down", "revive") : ((string, string)?)null;
                    figures[(cid, use)] = SkillValue.Figures(c.Run(SkillValue.Job(c, role, cid, skill, use, 0, runs, rule: rule)));
                }
            Trials.Say(c, name + " (" + role + "), " + runs + " battles: without > with | wins | length of the won fights | HP left");
            foreach (var cid in bosses)
            {
                var x = figures[(cid, false)]; var y = figures[(cid, true)];
                string length = Py.Truthy(x.Get("time_won")) && Py.Truthy(y.Get("time_won")) ? Py.F(x.D("time_won"), 1) + " > " + Py.F(y.D("time_won"), 1) : "-";
                Trials.Say(c, cid + " | " + Py.Pct(x.D("won"), 0) + " > " + Py.Pct(y.D("won"), 0) + " | " + length + " | " + Py.Pct(x.D("hp_left"), 0) + " > " + Py.Pct(y.D("hp_left"), 0));
            }
        }

        // --- tp_items_trial.py --------------------------------------------------------------------------------------
        public static void TpItemsTrial(Ctx c, string[] a)
        {
            var inp = Inp(c, "tp_items_trial");
            int fruit = (int)Py.Num(inp.Get("fruit"));
            string cid = a[0]; int runs = a.Length > 1 ? int.Parse(a[1]) : 40;
            var meta = c.Setup.Battery.First(b => b.name == "Meta").roles;
            var roles = meta.Select(r => r == "diva" ? "healer" : r).ToList();
            var baseData = c.Data("variant");
            foreach (var kv in inp.O("trials"))
            {
                var t = (List<object>)kv.Value;
                long count = (long)Py.Num(t[0]); double share = Py.Num(t[1]); double amount = Py.Num(t[2]);
                string side = c.AddSide(Kit.WithItemEffects(baseData, fruit, new[] { 1 }, new[] { amount }));
                string shareText = Py.Repr(share);
                var rows = c.Setup.Policies.Select(r => r.Str("Action").StartsWith("tp:") && r.Str("Condition") == "ally_tp_below:0.15"
                    ? Kit.With(Kit.With(r, "Condition", "ally_tp_below:" + shareText), "Action", "tp:" + shareText) : r).ToList();
                string setupName = c.AddSetup(c.Setup.WithPolicies(rows));
                var recipe = new Obj { { "bag_set", new Obj { { fruit.ToString(), count } } } };
                var done = c.Run(Jb.Make(c, side, cid, roles: roles, runs: runs, setupName: setupName, recipe: recipe, name: kv.Key));
                var s = Trials.SummaryOf(done);
                Trials.Say(c, cid + " | " + kv.Key + " | " + Py.Pct(s.Won, 0) + " | " + Py.F(s.Time ?? 0.0, 1));
            }
        }

        // --- worth_with_weapon.py -----------------------------------------------------------------------------------
        static List<(string ctx, List<(string name, double value)> scores)> Contexts(Ctx c, string setupName, string cid, string role)
        {
            var item = SkillWorth.Item(c, c.Data("variant"), cid, role, c.SetInt("skill_worth_groups"), "variant", setupName);
            item.Set("id", "scores0"); item.Set("measure", "skill_scores");
            var answer = c.Measure(new List<Obj> { item })[0];
            var found = new List<(string, List<(string, double)>)>();
            var raw = answer.A("contexts");
            for (int g = 0; g < raw.Count; g++)
            {
                var dict = new List<(string, double)>();
                foreach (List<object> pair in (List<object>)raw[g])
                {
                    string n = (string)pair[0]; double v = Py.Num(pair[1]);
                    int at = dict.FindIndex(x => x.Item1 == n);
                    if (at >= 0) dict[at] = (n, v); else dict.Add((n, v));
                }
                found.Add((g == 0 ? "boss" : "random", dict));
            }
            return found;
        }

        static (string name, double value) Top(List<(string name, double value)> scores)
        {
            var best = scores[0];
            foreach (var s in scores) if (s.value > best.value) best = s;
            return best;
        }

        public static void WorthWithWeapon(Ctx c, string[] a)
        {
            string name = a[0], role = a[1], weapon = a[2];
            string usualName = null;                                   // the sheet as it is
            string trialName = c.AddSetup(Kit.WithRole(c.Setup, role, "Weapon", weapon));
            foreach (var st in M.Stages(c))
            {
                if (st.S("Stage") != "advanced" && st.S("Stage") != "late") continue;
                foreach (var cid in ClassStages.Checkpoints(st))
                {
                    var plain = Contexts(c, usualName, cid, role);
                    var trial = Contexts(c, trialName, cid, role);
                    for (int k = 0; k < plain.Count && k < trial.Count; k++)
                    {
                        var x = plain[k].scores; var y = trial[k].scores;
                        if (!y.Any(s => s.name == name)) { Trials.Say(c, cid + " " + plain[k].ctx + " " + name + " is not an option"); continue; }
                        var bestA = Top(x); var bestB = Top(y);
                        double mine = y.First(s => s.name == name).value;
                        Trials.Say(c, cid + " " + plain[k].ctx.PadRight(6) + " " + name + " " + Py.Pct(mine / bestB.value, 0) + " of " + bestB.name + " (with a " + weapon + "); "
                                   + Py.Pct(mine / bestA.value, 0) + " of " + bestA.name + " (usual weapon)");
                    }
                }
            }
        }
    }
}
