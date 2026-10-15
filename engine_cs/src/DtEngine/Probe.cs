using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace DtEngine
{
    /// <summary>The probe of tools/sim_audit.py actives: a skill performed by one user into a battle prepared by hand (no turn is played), several
    /// times on fresh battles and seeds, and what changed compared with what the tool expects of it.</summary>
    public static class Probe
    {
        sealed class Expectation
        {
            public string Key, Test;
            public int Effect;
            public double? GaugeAbove;       // an ailment that leaves no status: the gauge of a unit is put back past this time
            public bool Fell;                // an ailment that leaves no status: a unit that was alive falls
            public bool Met;
        }

        struct UnitState
        {
            public Unit Unit;
            public bool Alive;
            public int Hp, Tp;
            public int[] Statuses;
            public double NextTime;
            public int Items;
            public bool Stolen;
        }

        static double Num(JsonElement e, string name, double dflt) => e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.Number ? v.GetDouble() : dflt;

        static List<UnitState> Snapshot(Battle b)
        {
            var list = new List<UnitState>(b.Units.Count);
            foreach (var u in b.Units)
            {
                var statuses = u.StatusOrder();
                Array.Sort(statuses);
                list.Add(new UnitState { Unit = u, Alive = u.Alive, Hp = u.Hp, Tp = u.Tp, Statuses = statuses, NextTime = PyMath.RoundTo(u.NextTime, 6), Items = u.Items.Count, Stolen = u.Stolen });
            }
            return list;
        }

        static bool Same(List<UnitState> a, List<UnitState> b)
        {
            if (a.Count != b.Count) return false;
            for (int i = 0; i < a.Count; i++)
            {
                var x = a[i]; var y = b[i];
                if (!ReferenceEquals(x.Unit, y.Unit) || x.Alive != y.Alive || x.Hp != y.Hp || x.Tp != y.Tp || x.NextTime != y.NextTime || x.Items != y.Items ||
                    x.Stolen != y.Stolen || !x.Statuses.SequenceEqual(y.Statuses)) return false;
            }
            return true;
        }

        /// <summary>The measure probe: {job: the reference party (cid, level, crown), user: a tested member, skill, level, expect: [...], tries, prelude: {...}}.
        /// The result holds the keys of the expectations that were never met, or the crash that stopped the tries.</summary>
        public static void WriteProbe(Scenario sc, JsonElement job, Utf8JsonWriter w)
        {
            var spec = JobSpec.FromJson(job.GetProperty("job"));
            var cp = sc.Setup.Checkpoint(spec.Cid);
            int partyLevel = spec.Level ?? sc.ReferenceLevels()[spec.Cid].level;
            int gear = sc.CheckpointGear(spec.Cid);
            int crown = spec.Crown ?? (cp.Truthy("Crown bonus") ? cp.Int("Crown bonus") : 0);
            var user = sc.BuildTested(spec, TestedSpec.FromJson(job.GetProperty("user")), new HashSet<string>(), out _);
            var skill = sc.Data.ById(job.GetProperty("skill").GetInt32());
            int level = job.GetProperty("level").GetInt32();
            int tries = job.GetProperty("tries").GetInt32();
            var pre = job.GetProperty("prelude");
            var expect = new List<Expectation>();
            foreach (var x in job.GetProperty("expect").EnumerateArray())
            {
                var e = new Expectation { Key = x.GetProperty("key").GetString(), Test = x.GetProperty("test").GetString() };
                if (x.TryGetProperty("effect", out var ef)) e.Effect = ef.GetInt32();
                if (x.TryGetProperty("gauge_above", out var g) && g.ValueKind == JsonValueKind.Number) e.GaugeAbove = g.GetDouble();
                if (x.TryGetProperty("fell", out var f)) e.Fell = f.ValueKind == JsonValueKind.True;
                expect.Add(e);
            }
            double nextTime = Num(pre, "next_time", 0.5);
            string crash = null;
            for (int seed = 0; seed < tries; seed++)
            {
                // battle_for: the first four members of the reference party that are not the user, then the user
                var whole = sc.ReferenceParty(spec.Roles ?? sc.Setup.Composition, cp.Str("Chapter"), partyLevel, gear, crown, cp.Str("Floor"), spec.Kit, spec.ExtraSkills,
                                              spec.Bag, spec.ExtraEnchants, spec.More);
                var party = whole.Where(u => u.Kind == Kind.Member && u.Name != user.Name).Take(4).ToList();
                party.Add(user);
                if (pre.TryGetProperty("halve", out var halve) && halve.ValueKind == JsonValueKind.True)
                    foreach (var u in party) { u.Hp = Math.Max(1, u.MaxHp / 2); u.Tp = Math.Max(u.Tp / 2, 0); }
                user.MaxTp = pre.GetProperty("user_max_tp").GetInt32();
                user.Tp = pre.GetProperty("user_tp").GetInt32();
                int fallen = pre.GetProperty("fallen").GetInt32();
                party[fallen].Alive = false;
                party[fallen].Hp = 0;
                foreach (var st in pre.GetProperty("statuses").EnumerateArray())
                    party[st[0].GetInt32()].SetStatus(new Status(st[1].GetInt32(), st[2].GetDouble(), st[3].GetInt32(), null));
                var foes = new List<Unit>();
                foreach (var f in pre.GetProperty("foes").EnumerateArray()) foes.Add(sc.EnemyUnit(f[0].GetInt32(), f[1].GetBoolean()));
                var foeStatus = pre.GetProperty("foe_status");
                foreach (var f in foes)
                {
                    f.ImmuneMask = 0;
                    f.ResistBase = new int[8];
                    f.SetStatus(new Status(foeStatus[0].GetInt32(), foeStatus[1].GetDouble(), foeStatus[2].GetInt32(), f));
                }
                var b = new Battle(sc.Data, party, foes, new PyRandom((ulong)seed), null, Scenario.OptionsFrom(sc.Setup, null), null);
                foreach (var u in b.Units) u.NextTime = nextTime;
                var before = Snapshot(b);
                var hpBefore = new Dictionary<Unit, int>();
                foreach (var u in b.Units) hpBefore[u] = u.Hp;
                var action = new Action(user, AKind.Skill, skill, level);
                int code = action.TargetCode;
                if (code == T.ALLY || code == T.ALLY_ROW) action.Target = b.Units[2];
                try { b.Perform(action); }
                catch (Exception ex) { crash = ex.GetType().Name + ": " + ex.Message; break; }
                var others = b.Units.Where(u => !ReferenceEquals(u, b.Units[0])).ToList();
                foreach (var e in expect)
                {
                    switch (e.Test)
                    {
                        case "hp_lost":
                            if (b.Units.Any(u => hpBefore.TryGetValue(u, out int h) && u.Hp < h)) e.Met = true;
                            break;
                        case "ailment":
                            {
                                bool seen = others.Any(u => u.St[e.Effect] != null)
                                    || (e.GaugeAbove.HasValue && others.Any(u => u.NextTime > e.GaugeAbove.Value))
                                    || (e.Fell && others.Any(u => !u.Alive && hpBefore.TryGetValue(u, out int h) && h != 0));
                                e.Met = e.Met || seen;
                                break;
                            }
                        case "status":
                            e.Met = e.Met || b.Units.Any(u => u.St[e.Effect] != null);
                            break;
                        case "changed":
                            break;
                        default:
                            throw new InvalidOperationException("unknown test " + e.Test);
                    }
                }
                user.Tp += action.TpCost;
                foreach (var e in expect)
                    if (e.Test == "changed" && !Same(Snapshot(b), before)) e.Met = true;
                if (expect.All(e => e.Met)) break;
            }
            w.WriteStartArray("missed");
            if (crash == null) foreach (var e in expect) if (!e.Met) w.WriteStringValue(e.Key);
            w.WriteEndArray();
            if (crash != null) w.WriteString("crash", crash); else w.WriteNull("crash");
            w.WriteString("user", user.Name);
        }
    }
}
