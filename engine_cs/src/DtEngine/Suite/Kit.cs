using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine.Suite
{
    /// <summary>A number that keeps the kind it has in Python (an int stays an int through the arithmetic that keeps it one).</summary>
    public readonly struct Num
    {
        public readonly double V;
        public readonly bool Int;
        public Num(double v, bool isInt) { V = v; Int = isInt; }
        public static Num Float(double v) => new Num(v, false);
        public static Num Whole(long v) => new Num(v, true);
        public static Num operator +(Num a, Num b) => new Num(a.V + b.V, a.Int && b.Int);
    }

    /// <summary>The changes the trial scripts of measures/ make to the data of a side before they play it: values of skills and items, stats of
    /// guests, enchantments of a sealbook; and to the choices of the model: a column of a role, the rows of the policies. Each gives a copy;
    /// the side and the setup of the snapshot are never edited.</summary>
    public static class Kit
    {
        // --- skills -------------------------------------------------------------------------------------------------
        /// <summary>next(s for s in data.skills.values() if s.name == name [and s.classes])</summary>
        public static Skill SkillNamed(GameData d, string name, bool withClasses = false) =>
            d.SkillList.First(s => s.Name == name && (!withClasses || s.Classes.Length > 0));

        /// <summary>The values of an effect, as list(v) of the first effect with that id.</summary>
        public static Num[] Values(Skill s, int effect)
        {
            var e = s.Effects.First(x => x.Id == effect);
            return e.Values.Select((v, i) => new Num(v, e.IsInt != null && i < e.IsInt.Length && e.IsInt[i])).ToArray();
        }

        public static Effect WithValues(Effect e, IList<Num> values) =>
            new Effect { Id = e.Id, Kind = e.Kind, Values = values.Select(v => v.V).ToArray(), IsInt = values.Select(v => v.Int).ToArray() };

        /// <summary>A copy of the skill whose effects are mapped (the effects the map leaves are shared).</summary>
        public static Skill Mapped(Skill s, Func<Effect, Effect> map)
        {
            var copy = s.Copy();
            copy.Effects = s.Effects.Select(map).ToArray();
            return copy;
        }

        /// <summary>A copy of the skill whose effects with this id take the values.</summary>
        public static Skill WithEffect(Skill s, int effect, IList<Num> values) => Mapped(s, e => e.Id == effect ? WithValues(e, values) : e);

        public static Skill WithCast(Skill s, double[] cast)
        {
            var copy = s.Copy();
            copy.Cast = cast;
            bool any = cast != null && cast.Any(c => c != 0);
            copy.Chanted = copy.IsMagic && cast != null && cast.Length > 0 && any;
            return copy;
        }

        /// <summary>The data with the skills replaced (each by the copy of the skill it stands for).</summary>
        public static GameData WithSkills(GameData d, IEnumerable<(Skill old, Skill replacement)> changes)
        {
            var list = changes.ToList();
            if (list.Count == 0) return d;
            var copy = d.ShallowCopy();
            copy.SkillList = d.SkillList.Select(s => { foreach (var (o, n) in list) if (ReferenceEquals(s, o)) return n; return s; }).ToList();
            copy.Skills = new Dictionary<(string, int), Skill>(d.Skills);
            copy.SkillById = new Dictionary<int, Skill>(d.SkillById);
            foreach (var (o, n) in list)
            {
                copy.Skills[(o.Category, o.Id)] = n;
                foreach (var kv in d.SkillById.ToList()) if (ReferenceEquals(kv.Value, o)) copy.SkillById[kv.Key] = n;
            }
            return copy;
        }

        public static GameData WithSkill(GameData d, Skill old, Skill replacement) => WithSkills(d, new[] { (old, replacement) });

        // --- other records ------------------------------------------------------------------------------------------
        /// <summary>The item with its effects replaced by [(kind, value)].</summary>
        public static GameData WithItemEffects(GameData d, int item, int[] kinds, double[] values)
        {
            var copy = d.ShallowCopy();
            copy.Items = new Dictionary<int, Item>(d.Items);
            var old = d.Items[item];
            copy.Items[item] = new Item { Id = old.Id, Name = old.Name, Kinds = kinds, Values = values };
            return copy;
        }

        public static GameData WithSealbook(GameData d, int book, int[] enchants)
        {
            var copy = d.ShallowCopy();
            copy.SealbookEnchants = new Dictionary<int, int[]>(d.SealbookEnchants);
            copy.SealbookEnchants[book] = enchants;
            return copy;
        }

        /// <summary>Every stage of the guest ally called name with the stat (atk, def, int, res, dex, agi or hp) multiplied: int(record[stat] * factor).</summary>
        public static GameData WithGuestScaled(GameData d, string name, IEnumerable<(string stat, double factor)> factors)
        {
            var copy = d.ShallowCopy();
            string[] stats = { "atk", "def", "int", "res", "dex", "agi" };
            copy.Npcs = d.Npcs.Select(n =>
            {
                if (n.Name != name) return n;
                var c = (NpcRec)n.Clone();
                foreach (var (stat, factor) in factors)
                {
                    int at = Array.IndexOf(stats, stat);
                    if (stat == "hp") throw new InvalidOperationException("a guest ally has no HP (0xAC of NPCData is the gold of the hire)");
                    else if (at >= 0) c.Stats[at] = (int)(c.Stats[at] * factor);
                    else throw new InvalidOperationException("no stat " + stat);
                }
                return c;
            }).ToList();
            return copy;
        }

        // --- the setup ----------------------------------------------------------------------------------------------
        public static Row Edited(Row row, string column, object value)
        {
            var r = new Row();
            foreach (var kv in row.Cells) r.Cells[kv.Key] = kv.Value;
            r.Cells[column] = value;
            return r;
        }

        /// <summary>A copy of a row of the sheet Policies with one column changed (dict(r, Action=...)).</summary>
        public static Row With(Row row, string column, object value) => Edited(row, column, value);

        public static Setup WithRole(Setup s, string role, string column, object value)
        {
            var copy = s.WithPolicies(s.Policies);
            copy.Roles = new Dictionary<string, Row>(s.Roles);
            copy.Roles[role] = Edited(s.Roles[role], column, value);
            return copy;
        }

        public static Setup WithGrandSealbooks(Setup s, List<Row> rows)
        {
            var copy = s.WithPolicies(s.Policies);
            copy.GrandSealbooks = rows;
            return copy;
        }

        /// <summary>A copy of the setup with these rows of the sheet UniqueGear (none: every member wears the forged pieces of her plan).</summary>
        public static Setup WithUniqueGear(Setup s, List<Row> rows)
        {
            var copy = s.WithPolicies(s.Policies);
            copy.UniqueGear = rows;
            return copy;
        }
    }
}
