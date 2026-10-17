using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>tools/sim_audit.py: does every rule of the simulator actually act? Passives, usage and actives; docs/generated/SIM_AUDIT.md.</summary>
    public static class SimAudit
    {
        const string EveryRole = "*";

        static Obj Inp(Ctx c) => c.In("sim_audit");

        static HashSet<int> Ints(IEnumerable<object> list) => new HashSet<int>(list.Select(x => (int)Py.Num(x)));

        /// <summary>Why a skill a plan never uses is situational, by the first group of measure_config.json (sim_audit, situational) it shares an effect with; null if none.</summary>
        static string Situational(Ctx c, HashSet<int> effects)
        {
            foreach (var g in Inp(c).A("situational"))
            {
                var group = (Obj)g;
                if (Ints(group.A("effects")).Overlaps(effects)) return group.S("why");
            }
            return null;
        }
        static List<(string column, int level, string cid)> Tiers(Ctx c) =>
            Inp(c).A("tiers").Cast<List<object>>().Select(t => ((string)t[0], (int)Py.Num(t[1]), (string)t[2])).ToList();
        static (int level, string cid) Late(Ctx c) { var l = Inp(c).A("late"); return ((int)Py.Num(l[0]), (string)l[1]); }

        static (string role, int level, string cid)? RoleFor(Ctx c, GameData data, int classId)
        {
            string name = data.ClassName(classId);
            foreach (var (column, level, cid) in Tiers(c))
                foreach (var role in c.Setup.RoleOrder)
                    if (c.Setup.Roles[role].Str(column) == name) return (role, level, cid);
            return null;
        }

        static string FirstCharacter(Ctx c, string role) => c.Setup.Roles[role].Str("Characters (order of preference)").Split(';').Select(x => x.Trim()).First();

        /// <summary>fights_job(): the reference party of the checkpoint with the tested member in the place of the one of her role.</summary>
        static Obj Recipe(Ctx c, string role, string character, int level, string cid, Dictionary<int, int> extra)
        {
            var cp = c.Checkpoint(cid);
            var ex = new Obj();
            if (extra != null) foreach (var kv in extra) ex.Set(kv.Key.ToString(), (long)kv.Value);
            return new Obj
            {
                { "name_not", character }, { "place", "replace_role" }, { "items", "all_first" },
                { "tested", Jb.L(new Obj { { "role", role }, { "character", character }, { "level", (long)level }, { "forge", c.Sc("vanilla").ForgeOpen(cp.Str("Floor")) }, { "extra_skills", ex } }) },
            };
        }

        static JobSpec FightsJob(Ctx c, string role, string character, int level, string cid, Dictionary<int, int> extra, string name) =>
            Jb.Make(c, "vanilla", cid, runs: (int)Py.Num(Inp(c).Get("seeds")), level: level, crown: 0, record: true, recipe: Recipe(c, role, character, level, cid, extra), name: name);

        static List<string> Fingerprint(RunResult[] results)
        {
            var list = new List<string>();
            foreach (var r in results)
            {
                var dmg = r.Parts[0].Record.Damage;
                var pairs = new List<(string name, double value)>();
                for (int i = 0; i < dmg.Count; i++) pairs.Add((dmg.Keys[i].Unit.Name, dmg.Values[i]));
                var sorted = pairs.OrderBy(p => p.name, StringComparer.Ordinal).ThenBy(p => p.value).Select(p => p.name + "=" + Py.Repr(p.value + 0.0));
                list.Add(string.Join("|", new[] { r.Won ? "1" : "0", Py.Repr(PyMath.RoundTo(r.Time, 6) + 0.0), r.Actions.ToString(), string.Join(",", sorted),
                                                  Py.Repr(PyMath.RoundTo(r.HpLeft, 6) + 0.0), Py.Repr(PyMath.RoundTo(r.TpLeft, 6) + 0.0) }));
            }
            return list;
        }

        static void Write(Ctx c, string phase, List<string> lines, string summary)
        {
            c.WriteText(c.Path("docs", "generated", "sim_audit", phase + ".md"), "## " + phase + "\n\n" + summary + ".\n\n" + string.Join("\n", lines) + "\n", false);
        }

        // --- passives ------------------------------------------------------------------------------------------------
        public static void Passives(Ctx c)
        {
            var data = c.Data("vanilla");
            var outside = new HashSet<int>(Inp(c).A("outside").Select(x => (int)Py.Num(x)));
            var plan = new List<(int sid, string name, List<int> effects, string how, string result, int at)>();
            var jobs = new List<JobSpec>();
            foreach (var skill in data.SkillList.Where(s => s.Category == "Passive").OrderBy(s => s.Id))
            {
                var effects = skill.Effects.Select(e => e.Id).ToList();
                if (effects.Count > 0 && effects.All(outside.Contains)) { plan.Add((skill.Id, skill.Name, effects, "-", "outside battle", -1)); continue; }
                (string role, int level, string cid)? found = null;
                foreach (int cls in skill.Classes) { found = RoleFor(c, data, cls); if (found != null) break; }
                if (found == null) { plan.Add((skill.Id, skill.Name, effects, "-", "no role learns it", -1)); continue; }
                var (role, level, cid) = found.Value;
                string character = FirstCharacter(c, role);
                int top = skill.Levels != 0 ? skill.Levels : 1;
                jobs.Add(FightsJob(c, role, character, level, cid, new Dictionary<int, int> { { skill.Id, top } }, "fights" + jobs.Count));
                jobs.Add(FightsJob(c, role, character, level, cid, new Dictionary<int, int> { { skill.Id, 0 } }, "fights" + jobs.Count));
                plan.Add((skill.Id, skill.Name, effects, role + " (" + character + ", " + level + ", " + cid + ")", null, jobs.Count - 2));
            }
            var played = c.Run(jobs);
            var rows = new List<(int sid, string name, List<int> effects, string how, string result)>();
            foreach (var p in plan)
            {
                string result = p.result;
                if (p.at >= 0) result = Fingerprint(played[p.at].Runs).SequenceEqual(Fingerprint(played[p.at + 1].Runs)) ? "no effect seen" : "acts";
                rows.Add((p.sid, p.name, p.effects, p.how, result));
            }
            Write(c, "passives", new[] { "| Passive | Effects | Tested as | Result |", "|---|---|---|---|" }.Concat(
                      rows.Select(r => "| " + r.sid + " " + r.name + " | " + string.Join(", ", r.effects) + " | " + r.how + " | " + r.result + " |")).ToList(),
                  rows.Count(r => r.result == "acts") + " act, " + rows.Count(r => r.result == "no effect seen") + " no effect seen, " + rows.Count(r => r.result == "outside battle")
                  + " outside battle, " + rows.Count(r => r.result == "no role learns it") + " with no role, of " + rows.Count + " passive skills");
        }

        // --- usage ---------------------------------------------------------------------------------------------------
        public static void Usage(Ctx c)
        {
            var data = c.Data("vanilla");
            var sc = c.Sc("vanilla");
            var chars = data.Characters.Select(x => x.Name).ToHashSet();
            var tiers = Tiers(c);
            var places = tiers.Select(t => (t.level, t.cid)).ToList(); places.Add(Late(c));
            var cells = new List<(string role, string character, int level, string cid)>();
            foreach (var role in c.Setup.RoleOrder)
            {
                string character = FirstCharacter(c, role);
                if (!chars.Contains(character)) continue;
                foreach (var (level, cid) in places) cells.Add((role, character, level, cid));
            }
            var jobs = cells.Select((x, k) => FightsJob(c, x.role, x.character, x.level, x.cid, null, "fights" + k)).ToList();
            var fought = c.Run(jobs);
            var items = new List<Obj>();
            for (int k = 0; k < cells.Count; k++)
            {
                var cp = c.Checkpoint(cells[k].cid);
                items.Add(new Obj
                {
                    { "id", "scores" + k }, { "measure", "skill_scores" }, { "side", "vanilla" }, { "job", JobObjOf(c, cells[k], k) },
                    { "contexts", Jb.L(new Obj { { "kind", "fixed" }, { "floor", cp.Str("Floor") }, { "number", (long)Scenario.BattleNumbers(cp)[0] } }) },
                    { "zone", false }, { "attack_first", true },
                });
            }
            var scored = c.Measure(items);
            var rows = new List<(string role, string who, int level, string cid, string name, string why)>();
            int at = 0;
            foreach (var role in c.Setup.RoleOrder)
            {
                string character = FirstCharacter(c, role);
                if (!chars.Contains(character)) continue;
                var rules = c.Setup.Policies.Where(r => r.Str("Role") == role || r.Str("Role") == EveryRole).ToList();
                var statusRules = new HashSet<int>(rules.Where(r => r.Str("Action").StartsWith("status:")).Select(r => int.Parse(r.Str("Action").Split(':')[1])));
                foreach (var (level, cid) in places)
                {
                    var res = fought[at].Runs;
                    var used = new HashSet<string>();
                    foreach (var r in res) foreach (var p in r.Parts)
                            for (int i = 0; i < p.Record.SkillUses.Count; i++)
                            {
                                var key = p.Record.SkillUses.Keys[i];
                                if (key.Unit.HasRole && key.Unit.Role == role && key.Unit.Name == character) used.Add(key.Name);
                            }
                    var spec = jobs[at];
                    var party = sc.RecipeParty(spec, spec.Recipe, new List<string>());
                    var member = party.First(u => u.HasRole && u.Role == role && u.Name == character);
                    var scores = new List<(string name, double value)>();
                    foreach (List<object> pair in scored[at].A("contexts")[0] as List<object>)
                    {
                        string name = (string)pair[0]; double value = Py.Num(pair[1]);
                        int idx = scores.FindIndex(x => x.name == name);
                        if (idx >= 0) scores[idx] = (name, value); else scores.Add((name, value));
                    }
                    at++;
                    string bestName = null; double bestValue = 0;
                    foreach (var (n, v) in scores) if (bestName == null || v > bestValue) { bestName = n; bestValue = v; }
                    foreach (var (sid, lv) in member.Skills)
                    {
                        var skill = data.ById(sid);
                        if (skill == null || !Policy.UsableInBattle(skill) || used.Contains(skill.Name)) continue;
                        var effects = new HashSet<int>(skill.Effects.Select(e => e.Id));
                        string why;
                        if (!Policy.WeaponAllows(member, skill)) why = "not usable with the weapon of the role";
                        else if (scores.Any(x => x.name == skill.Name))
                        {
                            double mine = scores.First(x => x.name == skill.Name).value, best = scores.First(x => x.name == bestName).value;
                            double share = best != 0 ? mine / best : 0.0;
                            why = "dominated: " + Py.Pct(share, 0) + " of the best (" + bestName + ") at the start of the fight";
                        }
                        else if (Situational(c, effects) is string because) why = because;
                        else if (effects.Any(e => Policy.Puts(skill, e)))
                        {
                            var kept = effects.Where(e => Policy.Puts(skill, e) && statusRules.Contains(e)).OrderBy(e => e).ToList();
                            why = kept.Count > 0 ? "a rule keeps effect " + kept[0] + " up: another skill gives it first" : "no rule of the role uses it";
                        }
                        else why = "other";
                        rows.Add((role, character, level, cid, skill.Name, why));
                    }
                }
            }
            var counts = new SortedDictionary<string, int>(StringComparer.Ordinal);
            foreach (var r in rows) { string key = r.why.Split(':')[0]; counts[key] = counts.GetValueOrDefault(key) + 1; }
            Write(c, "usage", new[] { "| Role | Level | Fight | Skill never used | Why |", "|---|---|---|---|---|" }.Concat(
                      rows.Select(r => "| " + r.role + " (" + r.who + ") | " + r.level + " | " + r.cid + " | " + r.name + " | " + r.why + " |")).ToList(),
                  rows.Count + " skills of a plan never used: " + string.Join(", ", counts.Select(kv => kv.Value + " " + kv.Key)));
        }

        static Obj JobObjOf(Ctx c, (string role, string character, int level, string cid) cell, int k)
        {
            var party = new Obj { { "cid", cell.cid }, { "roles", null }, { "level", (long)cell.level }, { "crown", 0L }, { "recipe", Recipe(c, cell.role, cell.character, cell.level, cell.cid, null) } };
            return new Obj
            {
                { "id", "scores" + k }, { "side", "vanilla" }, { "runs", Inp(c).Get("seeds") }, { "seed", Convert.ToInt64(c.Setup.Settings["seed"]) }, { "trace", 0L }, { "record", true },
                { "kit", null }, { "options", new Obj() }, { "party", party }, { "enemies", new Obj { { "kind", "checkpoint" } } },
            };
        }

        // --- actives -------------------------------------------------------------------------------------------------
        public static void Actives(Ctx c)
        {
            var data = c.Data("vanilla");
            var every = data.SkillList.Where(s => (s.Category == "Technique" || s.Category == "Magic") && Policy.UsableInBattle(s)).OrderBy(s => s.Id).ToList();
            var late = Late(c);
            long enemy = (long)Py.Num(Inp(c).Get("enemy"));
            var prelude = new Obj
            {
                { "halve", true }, { "user_max_tp", 9999L }, { "user_tp", 4999L }, { "fallen", 0L },
                { "statuses", Jb.L(Jb.L(1L, 113L, 0L, 3L), Jb.L(1L, 116L, 0L, 3L)) },
                { "foes", Jb.L(Jb.L(enemy, true), Jb.L(enemy, false)) }, { "foe_status", Jb.L(161L, 0.2, 3L) }, { "next_time", 0.5 },
            };
            var partyObj = new Obj
            {
                { "id", "actives" }, { "side", "vanilla" }, { "runs", 1L }, { "seed", Convert.ToInt64(c.Setup.Settings["seed"]) }, { "trace", 0L }, { "record", false },
                { "kit", null }, { "options", new Obj() },
                { "party", new Obj { { "cid", late.cid }, { "roles", null }, { "level", (long)late.level }, { "crown", 0L } } },
                { "enemies", new Obj { { "kind", "checkpoint" } } },
            };
            var plan = new List<(Skill skill, string role, List<string> expect)>();
            var items = new List<Obj>();
            foreach (var skill in every)
            {
                string role = null, who = null;
                foreach (int cls in skill.Classes)
                {
                    var found = RoleFor(c, data, cls);
                    if (found != null) { role = found.Value.role; who = FirstCharacter(c, role); break; }
                }
                if (role == null) { role = (string)Inp(c).Get("fallback"); who = FirstCharacter(c, role); }
                var kinds = new List<(int e, int kind)>();
                foreach (var ef in skill.Effects) if (!kinds.Contains((ef.Id, ef.Kind))) kinds.Add((ef.Id, ef.Kind));
                var expect = new List<string>();
                var damageEffects = Ints(Inp(c).A("damage_effects"));
                if (kinds.Any(k => ((k.e == 0 || k.e == 1) && k.kind == 4) || damageEffects.Contains(k.e))) expect.Add("damage");
                foreach (var (e, kind) in kinds)
                {
                    if (kind == 4 && SkillValue.IsAilment(e)) expect.Add("ailment " + e);
                    if (kind == 5) expect.Add("status " + e);
                }
                if (expect.Count == 0) expect.Add("anything");
                var tests = new List<object>();
                foreach (var key in expect)
                {
                    if (key == "damage") tests.Add(new Obj { { "key", key }, { "test", "hp_lost" } });
                    else if (key == "anything") tests.Add(new Obj { { "key", key }, { "test", "changed" } });
                    else
                    {
                        int e = int.Parse(key.Split(' ')[1]);
                        var test = new Obj { { "key", key }, { "test", key.StartsWith("ailment") ? "ailment" : "status" }, { "effect", (long)e } };
                        if (key.StartsWith("ailment")) { test.Set("gauge_above", e == 118 ? (object)0.5 : null); test.Set("fell", e == 119); }
                        tests.Add(test);
                    }
                }
                var user = new Obj { { "role", role }, { "character", who }, { "level", (long)late.level }, { "forge", false } };
                plan.Add((skill, role, expect));
                items.Add(new Obj
                {
                    { "id", "probe" + items.Count }, { "measure", "probe" }, { "side", "vanilla" }, { "setup", null }, { "job", partyObj }, { "user", user }, { "skill", (long)skill.Id },
                    { "level", (long)(skill.Levels != 0 ? skill.Levels : 1) }, { "expect", tests }, { "tries", Inp(c).Get("tries") }, { "prelude", prelude },
                });
            }
            var played = c.Measure(items);
            var rows = new List<(Skill skill, string role, string result)>();
            for (int k = 0; k < plan.Count; k++)
            {
                var done = played[k];
                List<string> missed;
                if (done.Get("crash") != null) missed = new List<string> { "crash " + done.S("crash") };
                else { var m = done.A("missed").Select(x => (string)x).ToHashSet(); missed = plan[k].expect.Where(m.Contains).ToList(); }
                rows.Add((plan[k].skill, plan[k].role, missed.Count == 0 ? "acts" : "not seen: " + string.Join(", ", missed)));
            }
            int flagged = rows.Count(r => r.result != "acts");
            Write(c, "actives", new[] { "| Skill | Effects | Performed by | Result |", "|---|---|---|---|" }.Concat(
                      rows.Select(r => "| " + r.skill.Id + " " + r.skill.Name + " | " + string.Join(", ", r.skill.Effects.Select(e => e.Id + "/" + e.Kind)) + " | " + r.role + " | " + r.result + " |")).ToList(),
                  (rows.Count - flagged) + " act as their effects say, " + flagged + " to read, of " + rows.Count + " active skills");
        }

        // --- the report ----------------------------------------------------------------------------------------------
        public static void Report(Ctx c)
        {
            string dir = c.Path("docs", "generated", "sim_audit");
            var parts = M.Listing(dir).Where(p => p.EndsWith(".md")).ToList();
            var text = new List<string> { "# Audit of the simulator (generated)", "", "Generated by `dtcli sim-audit`. Do not edit: run the phases again, then `report`.", "" };
            var flagged = new List<string>();
            foreach (var p in parts)
            {
                string body = Ctx.ReadText(Path.Combine(dir, p));
                text.Add(body);
                var lines = body.Split('\n').ToList();                  // str.splitlines on text that has only \n
                if (body.EndsWith("\n")) lines.RemoveAt(lines.Count - 1);
                if (p.StartsWith("passives")) flagged.AddRange(lines.Where(l => l.EndsWith("| no effect seen |")).Select(l => l.Split('|')[1].Trim()));
                if (p.StartsWith("usage"))
                    foreach (var line in lines)
                    {
                        var cells = line.Split('|').Select(x => x.Trim()).ToList();
                        if (cells.Count > 5 && (cells[5].StartsWith("no rule") || cells[5].StartsWith("not usable")))
                        {
                            string head = cells[1]; int at = head.IndexOf(" (", StringComparison.Ordinal);
                            flagged.Add("usage " + (at >= 0 ? head.Substring(0, at) : head) + " | " + cells[4]);
                        }
                    }
                if (p.StartsWith("actives")) flagged.AddRange(lines.Where(l => l.StartsWith("| ") && l.Contains("| not seen")).Select(l => l.Split('|')[1].Trim()));
            }
            var readings = new List<(string key, Obj row)>();
            foreach (var r in M.Rows(c, "audit_readings"))
            {
                string key = Py.Str(r.Get("ID")).Trim();
                int at = readings.FindIndex(x => x.key == key);
                if (at >= 0) readings[at] = (key, r); else readings.Add((key, r));
            }
            var unread = flagged.Where(x => !readings.Any(r => r.key == x)).ToList();
            var head2 = new List<string>
            {
                "**Checklist: " + (flagged.Count - unread.Count) + " of " + flagged.Count + " passives, active skills and skills never used have a reading** (sheet AuditReadings of data_tables/sim_setup.xlsx)"
                    + (unread.Count > 0 ? ": unread " + string.Join(", ", unread) : "") + ".",
                "", "| Skill or point | Result | Reading |", "|---|---|---|",
            };
            head2.AddRange(readings.Select(r => "| " + r.key + " | " + Py.Str(r.row.Get("Result")) + " | " + Py.Str(r.row.Get("Reading")) + " |"));
            head2.Add("");
            text.InsertRange(4, head2);
            c.WriteText(c.Path("docs", "generated", "SIM_AUDIT.md"), M.Lines(text), false);
        }
    }
}
