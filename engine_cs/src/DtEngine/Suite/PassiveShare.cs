using System;
using System.Collections.Generic;
using System.Linq;

namespace DtEngine.Suite
{
    public static partial class TrialsB
    {
        sealed class ShareTally
        {
            public int Battles; public double Won, Time;
            public Dictionary<string, double> Damage = new Dictionary<string, double>();
            public Dictionary<string, int> Blows = new Dictionary<string, int>();
            public double RoleAttackDamage; public int RoleAttacks;
            public double HealGained; public int HealCasts; public double HpLeft;
            public string Weapon = "-"; public double RoleAtk, RoleWeaponAtk, RoleRes, RoleWeaponRes; public int Seen;
        }

        /// <summary>dtcli passive-share ROLE SKILL BOSS RUNS: plays the one-skill-trial cell without and with the skill under a trace and
        /// tells what share of the damage the party deals each role makes, the damage of a plain attack of ROLE and its ATK and weapon.</summary>
        public static void PassiveShare(Ctx c, string[] a)
        {
            string role = a[0], name = a[1], cid = a[2]; int runs = int.Parse(a[3]); string weapon = a.Length > 4 && a[4] != "-" ? a[4] : null;
            var data = c.Data("variant");
            var skill = Kit.SkillNamed(data, name);
            (string, string)? rule = skill.Category == "Passive" ? ("ally_down", "revive") : ((string, string)?)null;
            var results = new Dictionary<bool, ShareTally>();
            foreach (bool use in new[] { false, true })
            {
                var t = new ShareTally(); results[use] = t;
                Battle current = null; Action live = null;
                TextTrace.PerformHook = (b, act) =>
                {
                    if (b != current) { current = b; t.Battles++; }
                    live = act.Actor.Kind == Kind.Member && act.Actor.HasRole && act.Actor.Role == role && act.Kind == AKind.Skill ? act : null;
                    if (live != null) t.HealCasts++;
                    if (act.Actor.Kind == Kind.Member && act.Actor.HasRole && act.Actor.Role == role && t.Seen < 1 && act.Actor.Weapon != null)
                    {
                        t.Seen++; t.Weapon = act.Actor.Weapon.Name; t.RoleAtk = act.Actor.Stat(Unit.ATK); t.RoleWeaponAtk = act.Actor.Weapon.Stats[Unit.ATK]; t.RoleRes = act.Actor.Stat(Unit.RES); t.RoleWeaponRes = act.Actor.Weapon.Stats[Unit.RES];
                    }
                };
                TextTrace.RestoreHook = (b, u, g) => { if (live != null) t.HealGained += g; };
                TextTrace.TurnEndHook = (b, u) => { live = null; };
                TextTrace.DamageHook = (b, act, target, amount) =>
                {
                    if (act.Actor.Kind != Kind.Member || target.Side == act.Actor.Side) return;
                    string who = act.Actor.HasRole ? act.Actor.Role : act.Actor.Name;
                    t.Damage[who] = t.Damage.GetValueOrDefault(who) + amount;
                    t.Blows[who] = t.Blows.GetValueOrDefault(who) + 1;
                    if (who == role && act.Kind == AKind.Attack) { t.RoleAttackDamage += amount; t.RoleAttacks++; }
                };
                try
                {
                    var cp = c.Checkpoint(cid); var sc = c.Sc("variant");
                    int levels = skill.Levels != 0 ? skill.Levels : 1;
                    var recipe = new Obj
                    {
                        { "place", "replace_role" }, { "items", "first_kept" },
                        { "tested", Jb.L(new Obj { { "role", role }, { "forge", sc.ForgeOpen(cp.Str("Floor")) }, { "unique_pieces", true },
                                                   { "extra_skills", new Obj { { skill.Id.ToString(), (long)(use ? levels : 0) } } },
                                                   { "pieces", weapon == null ? new Obj() : new Obj { { "Weapon", weapon } } } }) },
                    };
                    var job = Jb.Make(c, "variant", cid, runs: runs, recipe: recipe, name: name + "|share|" + role + "|" + cid + "|" + weapon + "|" + (use ? 1 : 0));
                    job.Trace = 1;
                    var res = c.Run(job);
                    var won = res.Runs.Where(r => r.Won).ToList();
                    t.Won = (double)won.Count / res.Runs.Length;
                    t.Time = won.Count > 0 ? Py.Sum(won.Select(r => r.Time)) / won.Count : 0;
                    t.HpLeft = SkillValue.Figures(res).D("hp_left");
                }
                finally { TextTrace.PerformHook = null; TextTrace.DamageHook = null; TextTrace.RestoreHook = null; TextTrace.TurnEndHook = null; }
            }
            foreach (bool use in new[] { false, true })
            {
                var t = results[use]; double nb = Math.Max(1, t.Battles); double total = t.Damage.Values.Sum();
                Trials.Say(c, name + (use ? " WITH" : " WITHOUT") + " (" + role + ") " + cid + ", " + runs + " battles: won " + Py.Pct(t.Won, 1) + " | length of won " + Py.F(t.Time, 1)
                           + " | damage dealt per battle " + Py.F(total / nb, 0));
                Trials.Say(c, "  " + role + ": weapon " + t.Weapon + " (ATK " + Py.F(t.RoleWeaponAtk, 0) + "), ATK stat of the unit " + Py.F(t.RoleAtk, 0) + " | RES " + Py.F(t.RoleRes, 0) + " (weapon RES " + Py.F(t.RoleWeaponRes, 0) + ")"
                           + " | plain attack " + Py.F(t.RoleAttackDamage / Math.Max(1, t.RoleAttacks), 1) + " per blow, " + Py.F(t.RoleAttacks / nb, 1) + " blows per battle");
                Trials.Say(c, "  HP restored by the skills of " + role + ": " + Py.F(t.HealGained / nb, 0) + " per battle in " + Py.F(t.HealCasts / nb, 1) + " casts (" + Py.F(t.HealGained / Math.Max(1, t.HealCasts), 1) + " per cast) | HP left of the party " + Py.Pct(t.HpLeft, 1));
                Trials.Say(c, "  share of the damage by role: " + string.Join(", ", t.Damage.OrderByDescending(kv => kv.Value).Select(kv => kv.Key + " " + Py.Pct(kv.Value / Math.Max(1, total), 1) + " (" + Py.F(kv.Value / nb, 0) + ")")));
            }
        }
    }
}
