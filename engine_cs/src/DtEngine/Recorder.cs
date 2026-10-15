using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;

namespace DtEngine
{
    /// <summary>The key of an entry of the recorder: a unit; a unit and a name (a skill, an item); or the thief of a stolen item (sim/battle.py Recorder).</summary>
    public readonly struct RecKey : IEquatable<RecKey>
    {
        public readonly Unit Unit;
        public readonly string Name;
        public readonly bool Stolen;      // the key ('stolen', unit)

        public RecKey(Unit unit) { Unit = unit; Name = null; Stolen = false; }
        public RecKey(Unit unit, string name) { Unit = unit; Name = name; Stolen = false; }
        public RecKey(Unit unit, bool stolen) { Unit = unit; Name = null; Stolen = stolen; }

        public bool Equals(RecKey o) => ReferenceEquals(Unit, o.Unit) && Name == o.Name && Stolen == o.Stolen;
        public override bool Equals(object obj) => obj is RecKey k && Equals(k);
        public override int GetHashCode() => System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(Unit) * 31 + (Name == null ? 0 : Name.GetHashCode()) + (Stolen ? 7 : 0);
    }

    /// <summary>A dictionary that keeps the order its keys were first added in (a Python dict), summing the amounts added to a key.</summary>
    public sealed class RecTable
    {
        public readonly List<RecKey> Keys = new List<RecKey>();
        public readonly List<double> Values = new List<double>();
        public readonly List<bool> IsFloat = new List<bool>();       // the value is a float in Python (an amount added to it was one)
        readonly Dictionary<RecKey, int> index = new Dictionary<RecKey, int>();

        public void Add(RecKey key, double amount, bool isFloat = false)
        {
            if (index.TryGetValue(key, out int at)) { Values[at] += amount; if (isFloat) IsFloat[at] = true; }
            else { index[key] = Keys.Count; Keys.Add(key); Values.Add(amount); IsFloat.Add(isFloat); }
        }

        /// <summary>table[key] = max(table.get(key, 0), value)</summary>
        public void Max(RecKey key, double value)
        {
            if (index.TryGetValue(key, out int at)) Values[at] = Math.Max(Values[at], value);
            else { index[key] = Keys.Count; Keys.Add(key); Values.Add(Math.Max(0, value)); IsFloat.Add(false); }
        }

        public double Get(RecKey key) => index.TryGetValue(key, out int at) ? Values[at] : 0.0;
        public int Count => Keys.Count;
    }

    /// <summary>What happened in a battle (sim.battle.Recorder): tables by unit, in the order the units were first recorded.</summary>
    public sealed class Recorder
    {
        public static readonly string[] Names =
        {
            "damage", "healing", "actions", "skill_uses", "tp_spent", "items_used", "chants_started", "chants_done", "chants_broken",
            "performances_broken", "turns_lost", "denied", "delayed", "largest_hit", "deaths",
        };

        public readonly RecTable Damage = new RecTable(), Healing = new RecTable(), Actions = new RecTable(), SkillUses = new RecTable(),
            TpSpent = new RecTable(), ItemsUsed = new RecTable(), ChantsStarted = new RecTable(), ChantsDone = new RecTable(),
            ChantsBroken = new RecTable(), PerformancesBroken = new RecTable(), TurnsLost = new RecTable(), Denied = new RecTable(),
            Delayed = new RecTable(), LargestHit = new RecTable(), Deaths = new RecTable();
        public int Kills;

        public RecTable Table(int k)
        {
            switch (k)
            {
                case 0: return Damage; case 1: return Healing; case 2: return Actions; case 3: return SkillUses; case 4: return TpSpent;
                case 5: return ItemsUsed; case 6: return ChantsStarted; case 7: return ChantsDone; case 8: return ChantsBroken;
                case 9: return PerformancesBroken; case 10: return TurnsLost; case 11: return Denied; case 12: return Delayed;
                case 13: return LargestHit; default: return Deaths;
            }
        }

        static string KeyText(RecKey k)
        {
            if (k.Stolen) return "stolen/u" + k.Unit.Position;
            if (k.Name != null) return "u" + k.Unit.Position + "/" + k.Name;
            return "u" + k.Unit.Position;
        }

        /// <summary>The line the trace carries after the end of a battle: every table in the order of Names, entries in the order they were added.</summary>
        public string TraceLine()
        {
            var sb = new StringBuilder("C");
            for (int t = 0; t < Names.Length; t++)
            {
                var table = Table(t);
                sb.Append(' ').Append(Names[t]).Append(':');
                for (int i = 0; i < table.Count; i++)
                {
                    if (i > 0) sb.Append(',');
                    sb.Append(KeyText(table.Keys[i])).Append('=').Append(Fmt.Num(table.Values[i]));
                }
            }
            sb.Append(" kills:").Append(Kills);
            return sb.ToString();
        }

        static void WriteKey(Utf8JsonWriter w, RecKey k)
        {
            // a unit: [position]; a unit and a name: [position, name]; the thief of a stolen item: ["stolen", position]
            if (k.Stolen) { w.WriteStringValue("stolen"); w.WriteNumberValue(k.Unit.Position); }
            else { w.WriteNumberValue(k.Unit.Position); if (k.Name != null) w.WriteStringValue(k.Name); }
        }

        /// <summary>The record as json: the units of the battle (position, name, kind, side, role, owner, level) and each table as a list of [key..., value].</summary>
        public void Write(Utf8JsonWriter w, List<Unit> units)
        {
            w.WriteStartObject("record");
            w.WriteStartArray("units");
            foreach (var u in units)
            {
                w.WriteStartObject();
                w.WriteNumber("p", u.Position);
                w.WriteString("name", u.Name);
                w.WriteString("kind", u.Kind.ToString().ToLowerInvariant());
                w.WriteNumber("side", u.Side);
                if (u.HasRole) w.WriteString("role", u.Role); else w.WriteNull("role");
                if (u.Owner != null) w.WriteNumber("owner", u.Owner.Position); else w.WriteNull("owner");
                w.WriteNumber("level", u.Level);
                w.WriteEndObject();
            }
            w.WriteEndArray();
            for (int t = 0; t < Names.Length; t++)
            {
                var table = Table(t);
                w.WriteStartArray(Names[t]);
                for (int i = 0; i < table.Count; i++)
                {
                    w.WriteStartArray();
                    WriteKey(w, table.Keys[i]);
                    if (table.IsFloat[i])
                    {
                        string text = Fmt.Num(table.Values[i]);
                        w.WriteRawValue(text.IndexOf('.') < 0 && text.IndexOf('e') < 0 ? text + ".0" : text);
                    }
                    else w.WriteNumberValue(table.Values[i]);
                    w.WriteEndArray();
                }
                w.WriteEndArray();
            }
            w.WriteNumber("kills", Kills);
            w.WriteEndObject();
        }
    }
}
