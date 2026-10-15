using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace DtEngine
{
    /// <summary>The analysis calls on a battle made by hand that tools/skill_worth.py, tools/sim_audit.py and the scripts of measures/ make:
    /// the options of a member scored by the value of their damage per time and TP. No battle is played.</summary>
    public static class Analysis
    {
        static bool Bool(JsonElement e, string name) => e.TryGetProperty(name, out var v) && v.ValueKind == JsonValueKind.True;

        /// <summary>The groups of enemies a measure job names: {kind: fixed, floor, number} one group; {kind: draws, zones, seed, count} count groups of
        /// random battles from one generator, each drawing its zone and then its formation (measures.random_group(data, rng.choice(zones), rng)).</summary>
        public static List<Group> Contexts(Scenario sc, JsonElement list)
        {
            var groups = new List<Group>();
            foreach (var c in list.EnumerateArray())
            {
                string kind = c.GetProperty("kind").GetString();
                if (kind == "fixed") groups.Add(sc.FixedBattle(c.GetProperty("floor").GetString(), c.GetProperty("number").GetInt32()));
                else if (kind == "draws")
                {
                    var zones = c.GetProperty("zones").EnumerateArray().Select(x => sc.FindZone(x.GetString())).ToList();
                    var rng = new PyRandom(c.GetProperty("seed").GetUInt64());
                    for (int i = 0, n = c.GetProperty("count").GetInt32(); i < n; i++) groups.Add(sc.RandomGroup(zones[rng.ChoiceIndex(zones.Count)], rng));
                }
                else throw new InvalidOperationException("unknown context " + kind);
            }
            return groups;
        }

        static bool Hits(Battle b, Action act)
        {
            int code = act.TargetCode;
            bool hits = (code == T.SINGLE || code == T.RANDOM || code == T.ROW || code == T.PIERCE || code == T.ALL || code == T.EVERYONE) &&
                        (act.Physical || act.Magic || b.Special(act));
            if (hits) return true;
            foreach (int e in Battle.RANDOM_MOVES) if (act.Has(e)) return true;
            return false;
        }

        /// <summary>tools/skill_worth.py scores() and the scores of tools/sim_audit.py usage: for each damaging option of the member (skill name -> damage
        /// over its targets per time and per TP), in the order of a Python dict, and the plain attack. attackFirst: the plain attack comes first under
        /// the name Attack and is scored as a skill is; else it comes last under the name (plain attack), with no TP term.</summary>
        public static List<(string name, double value)> SkillScores(Scenario sc, List<Unit> party, Unit member, Group enemies, bool useZone, bool attackFirst)
        {
            var b = new Battle(sc.Data, party, enemies.Units, new PyRandom(0), null, Scenario.OptionsFrom(sc.Setup, null), useZone ? enemies.Zone : null);
            member.Tp = member.MaxTp;
            var names = new List<string>();
            var values = new Dictionary<string, double>();
            void Put(string name, double value)
            {
                if (!values.ContainsKey(name)) names.Add(name);
                values[name] = value;
            }
            if (attackFirst)
            {
                var attack = new Action(member, AKind.Attack);
                double total = Policy.DamageValue(b, attack, out _);
                Put("Attack", total / sc.Policy.TimeOf(b, attack) / sc.Policy.TpPenalty(member, attack));
            }
            foreach (var (skill, level) in Policy.Options(b, member))
            {
                var act = new Action(member, AKind.Skill, skill, level);
                if (!Hits(b, act)) continue;
                double total = Policy.DamageValue(b, act, out _);
                Put(skill.Name, total / sc.Policy.TimeOf(b, act) / sc.Policy.TpPenalty(member, act));
            }
            if (!attackFirst)
            {
                var attack = new Action(member, AKind.Attack);
                double total = Policy.DamageValue(b, attack, out _);
                Put("(plain attack)", total / sc.Policy.TimeOf(b, attack));
            }
            return names.Select(n => (n, values[n])).ToList();
        }

        /// <summary>The measure skill_scores: {job: a job of the engine (its party, with a recipe that names the tested member), contexts: [...],
        /// zone: whether the battles carry the zone of their cell, attack_first}. The result holds, for each group of enemies, the list [name, value].</summary>
        public static void WriteSkillScores(Scenario sc, JsonElement job, System.Text.Json.Utf8JsonWriter w)
        {
            var spec = JobSpec.FromJson(job.GetProperty("job"));
            var tested = new List<Unit>();
            var party = sc.RecipeParty(spec, spec.Recipe, spec.TestedNames, tested);
            var member = tested[0];
            bool zone = Bool(job, "zone"), attackFirst = Bool(job, "attack_first");
            w.WriteString("tested", member.Name);
            w.WriteStartArray("contexts");
            foreach (var group in Contexts(sc, job.GetProperty("contexts")))
            {
                w.WriteStartArray();
                foreach (var (name, value) in SkillScores(sc, party, member, group, zone, attackFirst))
                {
                    w.WriteStartArray();
                    w.WriteStringValue(name);
                    w.WriteNumberValue(value);
                    w.WriteEndArray();
                }
                w.WriteEndArray();
            }
            w.WriteEndArray();
        }
    }
}
