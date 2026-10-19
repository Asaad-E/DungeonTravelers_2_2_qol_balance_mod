using System;
using System.Collections.Generic;
using System.Text;

namespace DtEngine
{
    /// <summary>
    /// The text trace of a battle: one header per battle, one line per turn, with the events of the turn, the state of every
    /// unit and the count of 32-bit random words drawn. The golden check (dtcli golden) compares these lines with the recorded ones.
    /// Level 2 adds the draws of the generator.
    /// </summary>
    public sealed class TextTrace : IBattleTrace
    {
        public readonly List<string> Lines = new List<string>();
        readonly StringBuilder events = new StringBuilder();
        readonly int level;
        int turn;
        public int Run, BattleIndex;

        public TextTrace(int level = 1) { this.level = level; }

        static string N(double x) => Fmt.Num(x);

        static string KindName(Kind k) => k.ToString().ToLowerInvariant();

        static string ImmuneNames(long mask)
        {
            var names = new List<string>();
            foreach (var kv in Snapshot.ImmuneBits) if ((mask & (1L << kv.Value)) != 0) names.Add(kv.Key);
            names.Sort(StringComparer.Ordinal);
            return string.Join(",", names);
        }

        public static string UnitLine(Unit u)
        {
            var sb = new StringBuilder();
            sb.Append("U ").Append(u.Position).Append(' ').Append(u.Name).Append('|').Append(KindName(u.Kind)).Append('|').Append(u.Side).Append('|')
              .Append(u.Front ? 1 : 0).Append("|L").Append(u.Level).Append("|hp").Append(u.MaxHpBase).Append("|tp").Append(u.MaxTp).Append("|st");
            for (int i = 0; i < 6; i++) { if (i > 0) sb.Append(','); sb.Append(u.Base[i]); }
            sb.Append("|rs");
            for (int i = 0; i < 8; i++) { if (i > 0) sb.Append(','); sb.Append(u.ResistBase[i]); }
            sb.Append("|w").Append(N(u.Weight)).Append("|sw").Append(N(u.Swing)).Append("|role").Append(u.HasRole ? u.Role : "-")
              .Append("|cls").Append(u.ClassId == T.NONE ? "-" : u.ClassId.ToString()).Append("|sk");
            for (int i = 0; i < u.Skills.Count; i++) { if (i > 0) sb.Append(','); sb.Append(u.Skills[i].id).Append(':').Append(u.Skills[i].level); }
            sb.Append("|pv");
            bool first = true;
            for (int e = 0; e < GameData.MaxEffect; e++)
                if (u.HasPassive(e)) { if (!first) sb.Append(','); first = false; sb.Append(e).Append('=').Append(N(u.Pv[e])); }
            sb.Append("|en");
            first = true;
            for (int e = 0; e < GameData.MaxEnchant; e++)
                if (u.Enchants[e] > 0) { if (!first) sb.Append(','); first = false; sb.Append(e).Append(':').Append(u.Enchants[e]); }
            sb.Append("|im").Append(ImmuneNames(u.ImmuneMask)).Append("|it");
            var ids = new List<int>(u.Items.Keys);
            ids.Sort();
            for (int i = 0; i < ids.Count; i++) { if (i > 0) sb.Append(','); sb.Append(ids[i]).Append(':').Append(u.Items[ids[i]]); }
            sb.Append("|at");
            for (int i = 0; i < u.Attacks.Length; i++) { if (i > 0) sb.Append(','); sb.Append(u.Attacks[i]); }
            sb.Append("|ar").Append(u.AttackRange).Append("|aa").Append(u.AttackAttr).Append("|wp").Append(u.Weapon != null ? u.Weapon.Id.ToString() : "-")
              .Append("|un").Append(u.HasUnique ? u.UniqueEffect + ":" + N(u.UniqueValue) : "-")
              .Append("|ad").Append(u.Adult ? 1 : 0).Append("|sh").Append(u.Shield ? 1 : 0).Append("|sl").Append(u.Slot == T.NONE ? "-" : u.Slot.ToString());
            return sb.ToString();
        }

        void FlushRng(Battle b)
        {
            if (level < 2 || b.Rng.Log == null) return;
            foreach (var l in b.Rng.Log) Lines.Add("r " + l);
            b.Rng.Log.Clear();
        }

        public void Begin(Battle b)
        {
            turn = 0;
            if (level >= 2 && b.Rng.Log == null) b.Rng.Log = new List<string>();
            Lines.Add("B " + Run + " " + BattleIndex);
            foreach (var u in b.Units) Lines.Add(UnitLine(u));
        }

        public void Started(Battle b)
        {
            FlushRng(b);
            var sb = new StringBuilder("S");
            foreach (var u in b.Units) sb.Append(' ').Append(N(u.NextTime));
            sb.Append(" w").Append(b.Rng.Words);
            Lines.Add(sb.ToString());
        }

        public void TurnStart(Battle b, Unit u) { events.Clear(); }

        public void TurnEnd(Battle b, Unit u)
        {
            FlushRng(b);
            turn++;
            var sb = new StringBuilder();
            sb.Append("T ").Append(turn).Append(' ').Append(N(b.Time)).Append(" a").Append(u.Position).Append(' ').Append(events).Append(" |");
            foreach (var x in b.Units)
                sb.Append(' ').Append(x.Hp).Append('/').Append(x.Tp).Append('/').Append(x.Alive ? 1 : 0).Append('/').Append(N(x.NextTime));
            sb.Append(" | w").Append(b.Rng.Words);
            Lines.Add(sb.ToString());
        }

        public void Ended(Battle b, BattleResult r)
        {
            Lines.Add("E " + (r.Won ? 1 : 0) + " " + (r.Lost ? 1 : 0) + " " + N(r.Time) + " " + r.Actions + " " + N(r.LowestHp) + " " + N(r.HpLeft) + " " +
                      N(r.TpLeft) + " " + r.Alive + " " + r.EnemyDamage + " " + r.EnemyActions + " " + r.PartyMaxHp);
            if (r.Record != null) Lines.Add(r.Record.TraceLine());
        }

        public void Perform(Battle b, Action a)
        {
            events.Append("A").Append(a.Actor.Position).Append(':').Append(a.Kind.ToString().ToLowerInvariant()).Append(':').Append(a.SourceName ?? "-")
                  .Append(":L").Append(a.Level).Append(';');
        }

        public void Hit(Battle b, Action a, Unit target, bool landed)
        {
            events.Append("H").Append(a.Actor.Position).Append('>').Append(target.Position).Append('=').Append(landed ? 1 : 0).Append(';');
        }

        public void Damage(Battle b, Action a, Unit target, int amount)
        {
            events.Append("D").Append(a.Actor.Position).Append('>').Append(target.Position).Append('=').Append(amount).Append(';');
        }

        public void Restore(Battle b, Unit u, int gained)
        {
            events.Append("R").Append(u.Position).Append('+').Append(gained).Append(';');
        }

        public void LoseHp(Battle b, Unit u, int amount)
        {
            events.Append("L").Append(u.Position).Append('-').Append(amount).Append(';');
        }
    }
}
