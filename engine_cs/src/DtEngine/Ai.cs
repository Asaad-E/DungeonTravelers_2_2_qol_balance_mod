using System;
using System.Collections.Generic;

namespace DtEngine
{
    /// <summary>What an enemy, a summon or a guest ally does on its turn (its script of EnemyAIData).</summary>
    public static class Ai
    {
        const int TARGET = 1;
        const int CHAIN = 0x1000, TO_SET = 0x2000, SLOT = 0x4000, ATTACK_ID = 0x8000;

        // a decision: 0 none, 1 slot, 2 attack id, 3 set
        struct Decided
        {
            public int Kind, Value;
            public Decided(int kind, int value) { Kind = kind; Value = value; }
            public bool None => Kind == 0;
        }

        static bool IsBreath(EnemyAttack atk)
        {
            if (atk.EffId == null) return false;
            for (int i = 0; i < atk.EffId.Length; i++) if (atk.EffId[i] == 3) return true;
            return false;
        }

        public static Action Choose(Battle battle, Unit unit)
        {
            var attacks = unit.Attacks;
            // the targets set by command 1 hold for the choice they were set in: the program empties the sixteen lists at the start of
            // every choice (0x430f8c - 0x430fa6)
            unit.AiTargets?.Clear();
            if (attacks.Length == 0) return new Action(unit, AKind.Defend);
            var chosen = ChooseAttack(battle, unit);
            // 0x431206..0x4313b5: Enemy-only Freeze/Silence/Shadow Sew attack overrides (skipped for Summons/NPCs);
            // Breath (effect ID 3) bypasses Silence (117, spells) and Freeze (114, techniques), NOT Shadow Sew (123).
            if (unit.Kind == Kind.Enemy && chosen.Atk != null)
            {
                bool blocked = unit.St[123] != null
                    || (!IsBreath(chosen.Atk) && ((unit.St[117] != null && chosen.Atk.Spell) || (unit.St[114] != null && chosen.Atk.Technique)));
                if (blocked) return AttackAction(battle, unit, 0, T.NONE);
            }
            return chosen;
        }

        static Action ChooseAttack(Battle battle, Unit unit)
        {
            var attacks = unit.Attacks;
            var script = unit.Script;
            if (script == null) return AttackAction(battle, unit, RollUniform(battle, attacks), T.NONE);
            unit.AiSet = 0;
            Decided decided = Run(battle, unit, script.Opening, -1);
            // a set switch marks the set left as done; a switch to a set already done this choice, or to no set, ends the choice
            // (0x4311c8, 0x431054, 0x43105c): no limit on the number of switches
            ulong doneMask = 0;
            HashSet<int> doneOverflow = null;
            bool first = true;
            while (decided.None || decided.Kind == 3)
            {
                if (!decided.None)
                {
                    int cur = unit.AiSet;
                    if ((uint)cur < 64u) doneMask |= 1UL << cur;
                    else (doneOverflow ?? (doneOverflow = new HashSet<int>())).Add(cur);
                    int next = decided.Value;
                    bool alreadyDone = (uint)next < 64u ? (doneMask & (1UL << next)) != 0 : (doneOverflow != null && doneOverflow.Contains(next));
                    if (alreadyDone || script.Get(next) == null) { decided = new Decided(0, 0); break; }
                    unit.AiSet = next;
                }
                var entry = script.Get(unit.AiSet) ?? (first ? script.Get(script.MinSet()) : null);
                first = false;
                if (entry == null)
                {
                    decided = new Decided(1, RollUniform(battle, attacks));
                    break;
                }
                int slot = RollWeights(battle, entry.Weights, attacks.Length);
                var found = Run(battle, unit, entry.Commands, slot);
                decided = !found.None ? found : new Decided(1, slot);
            }
            if (decided.None || decided.Kind == 3) decided = new Decided(1, 0);
            if (decided.Kind == 1) return AttackAction(battle, unit, decided.Value, T.NONE);
            return AttackAction(battle, unit, 0, decided.Value, true);
        }

        static int RollUniform(Battle battle, int[] attacks) => battle.Rng.RandRange(attacks.Length);

        static int RollWeights(Battle battle, int[] weights, int count)
        {
            long total = 0;
            int usableCount = 0, last = 0;
            for (int slot = 0; slot < weights.Length; slot++)
                if (weights[slot] != 0 && slot < count) { total += weights[slot]; usableCount++; last = slot; }
            if (usableCount == 0) return 0;
            int roll = battle.Rng.RandRange((int)total);
            for (int slot = 0; slot < weights.Length; slot++)
            {
                if (weights[slot] != 0 && slot < count)
                {
                    roll -= weights[slot];
                    if (roll < 0) return slot;
                }
            }
            return last;
        }

        static Decided Run(Battle battle, Unit unit, CommandList list, int rolled)
        {
            var commands = list.Commands;
            // a set switch whose second tail byte is 0 does not stop the commands (0x4325cf): the next ones still run, and one that
            // decides an attack wins; the switch is taken when none does
            var pending = new Decided(0, 0);
            for (int k = 0; k < commands.Length; k++)
            {
                var command = commands[k];
                if (command.Cmd == TARGET)
                {
                    if (unit.AiTargets == null) unit.AiTargets = new List<(int, int)>();
                    int at = -1;
                    for (int q = 0; q < unit.AiTargets.Count; q++) if (unit.AiTargets[q].word == command.Args[0]) { at = q; break; }
                    if (at >= 0) unit.AiTargets[at] = (command.Args[0], command.Args[1]);
                    else unit.AiTargets.Add((command.Args[0], command.Args[1]));
                    continue;
                }
                long key = ((long)list.Id << 20) | (uint)k;
                bool once = command.HasOnce && command.Once;
                if (once && unit.HasOnceDone(key)) continue;
                if (!Passes(battle, unit, command, rolled)) continue;
                var result = FinalResult(battle, unit, command, rolled);
                if (result.None) continue;
                if (once) unit.OnceDone.Add(key);
                if (result.Kind == 3 && !command.Stop) { pending = result; continue; }
                return result;
            }
            return pending;
        }

        static Decided FinalResult(Battle battle, Unit unit, Command command, int rolled)
        {
            int result = command.Result;
            while ((result & CHAIN) != 0)
            {
                command = command.And;
                if (!Passes(battle, unit, command, rolled)) return new Decided(0, 0);
                result = command.Result;
            }
            if ((result & TO_SET) != 0) return new Decided(3, result & 0x0FFF);
            // a slot the unit does not have, or an attack id it does not carry, decides nothing (P4.8 of the audit)
            if ((result & SLOT) != 0) return (result & 0x0FFF) < unit.Attacks.Length ? new Decided(1, result & 0x0FFF) : new Decided(0, 0);
            if ((result & ATTACK_ID) != 0) return Array.IndexOf(unit.Attacks, result & 0x0FFF) >= 0 ? new Decided(2, result & 0x0FFF) : new Decided(0, 0);
            return new Decided(0, 0);
        }

        /// <summary>The attack id a skill word names, or NONE.</summary>
        static int SkillOf(Unit unit, int word)
        {
            if ((word & SLOT) != 0)
            {
                int slot = word & 0x3FFF;
                return slot < unit.Attacks.Length ? unit.Attacks[slot] : T.NONE;
            }
            if ((word & ATTACK_ID) != 0) return word & 0x3FFF;
            return T.NONE;
        }

        static bool Passes(Battle battle, Unit unit, Command command, int rolled)
        {
            int cid = command.Cmd;
            var args = command.Args;
            if (cid == 2) return unit.TurnsTaken <= args[0];
            if (cid == 3 || cid == 10 || cid == 12 || cid == 13 || cid == 14)
            {
                int value = SourceValue(battle, unit, args[0]);
                // 0x431a51..0x432480: SourceValue == -1 means empty/false source and always fails comparisons.
                if (value < 0) return false;
                int n = args[1];
                switch (cid)
                {
                    case 3: return value <= n;
                    case 10: return value > n;
                    case 12: return value >= n;
                    case 13: return value < n;
                    default: return value == n;
                }
            }
            if (cid == 4 || cid == 11) return SourceValue(battle, unit, args[0]) > 0;
            if (cid == 5)
            {
                int last = unit.LastSkillId;
                return last != T.NONE && last == SkillOf(unit, args[0]);
            }
            if (cid == 6)
            {
                int id = SkillOf(unit, args[0]);
                var attack = id != T.NONE ? battle.Data.GetAttack(id) : null;
                if (attack != null && attack.SummonsDoll)
                {
                    // 0x432028..0x432156: when the attack carries effect 146 (0x92, doll summon), check active dolls owned by self with matching summon attack id.
                    foreach (var u in battle.Units)
                        if (u.Alive && u.Kind == Kind.Doll && u.Owner == unit && u.SummonAttackId == id) return true;
                    return false;
                }
                string name = attack != null ? attack.Name : null;
                // 0x431e8b..0x432173: check self for timed/song statuses, and living opponents for dance / 335..341 statuses.
                for (int i = 0; i < unit.StCount; i++)
                {
                    var s = unit.St[unit.StatusAt(i)];
                    if (s.Source == unit && (s.Turns != 0 || Battle.IsSong(s.Effect)) && (s.AttackId != T.NONE ? s.AttackId == id : s.Skill == name))
                        return true;
                }
                foreach (var u in battle.OpponentsArray(unit))
                {
                    for (int i = 0; i < u.StCount; i++)
                    {
                        var s = u.St[u.StatusAt(i)];
                        if (s.Source == unit && (Battle.IsDance(s.Effect) || (s.Effect >= 335 && s.Effect <= 341))
                            && (s.AttackId != T.NONE ? s.AttackId == id : s.Skill == name))
                            return true;
                    }
                }
                return false;
            }
            if (cid == 7)
            {
                int id = SkillOf(unit, args[0]);
                var attack = id != T.NONE ? battle.Data.GetAttack(id) : null;
                if (attack == null) return false;
                // with an attack already rolled, the command holds only when it names that attack (0x4321aa - 0x4321b7)
                if (rolled >= 0 && rolled < unit.Attacks.Length && unit.Attacks[rolled] != id) return false;
                return unit.UsesOf(id) >= args[1];
            }
            if (cid == 9)
            {
                // 0x43232e: Opcode 9 (dead ally) always returns false for Enemies.
                if (unit.Kind == Kind.Enemy) return false;
                foreach (var u in battle.AlliesArray(unit, false)) if (!u.Alive && u.Kind != Kind.Doll) return true;
                return false;
            }
            return false;
        }

        static int SourceValue(Battle battle, Unit unit, int source)
        {
            // allies are the candidates of the unit's side (0x43e6d0): units below 2000, never a doll, the summon or a guest
            var allies = battle.TargetableArray(unit.Side);
            var foes = battle.TargetableArray(1 - unit.Side);
            switch (source)
            {
                case 0: return PyMath.Int(unit.HpRatio * 100);
                case 1: { int m = 100; bool any = false; foreach (var u in allies) { int v = PyMath.Int(u.HpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : -1; }
                case 2: { int m = 100; bool any = false; foreach (var u in foes) { int v = PyMath.Int(u.HpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : -1; }
                case 3: { int m = 100; bool any = false; foreach (var u in allies) { int v = PyMath.Int(u.TpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : -1; }
                case 4: { int m = 100; bool any = false; foreach (var u in foes) { int v = PyMath.Int(u.TpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : -1; }
                case 5: { foreach (var u in allies) if (HasAilmentOrDebuff(u)) return 1; return -1; }
                case 6: { foreach (var u in foes) if (HasAilmentOrDebuff(u)) return 1; return -1; }
                case 7: { foreach (var u in foes) if (u.Chant != null) return 1; return -1; }
                case 8: { foreach (var u in foes) if (!u.Front) return 1; return -1; }
                case 9: { foreach (var u in foes) if (u.Front) return 1; return -1; }
                case 10: { foreach (var u in foes) if (HasBuff(u)) return 1; return -1; }
                case 11: { foreach (var u in allies) if (HasDebuff(u)) return 1; return -1; }
                default: return -1;
            }
        }

        static int DebuffCount(Unit u)
        {
            int n = 0;
            for (int i = 0; i < u.StCount; i++) if (Battle.IsDebuffStatus(u.St[u.StatusAt(i)])) n++;
            return n;
        }

        static int AilmentAndDebuffCount(Unit u) => Battle.CountTrueAilments(u) + DebuffCount(u);

        static bool HasAilmentOrDebuff(Unit u) => Battle.HasTrueAilment(u) || HasDebuff(u);

        static void MostAilments(Unit[] list, List<Unit> outList, bool skipPetrified = false)
        {
            // 0x433b80..0x433d70: counts true ailments + debuffs (vtable+0x5c); keeps 0-ties so all eligible candidates tie uniformly.
            int best = -1;
            foreach (var u in list)
            {
                if (skipPetrified && u.St[120] != null) continue;
                int c = AilmentAndDebuffCount(u);
                if (c > best) { best = c; outList.Clear(); outList.Add(u); }
                else if (c == best) outList.Add(u);
            }
        }

        static bool HasBuff(Unit unit)
        {
            for (int i = 0; i < unit.StCount; i++)
                if (Battle.IsBuffStatus(unit.St[unit.StatusAt(i)])) return true;
            return false;
        }

        static bool HasDebuff(Unit unit)
        {
            for (int i = 0; i < unit.StCount; i++)
                if (Battle.IsDebuffStatus(unit.St[unit.StatusAt(i)])) return true;
            return false;
        }

        static void PickCurePriority(Unit[] allies, List<Unit> found)
        {
            // 0x433e67..0x4342c9: strict 9-tier priority ladder:
            // Slow(122) > Petrify3(120, Stage>=3) > Petrify1-2(120, Stage<3) > Sleep(116) > Freeze(114) > Silence(117) > Paralysis(115) > Poison(113) > Debuff(+0x5c).
            foreach (var u in allies) if (u.St[122] != null) found.Add(u);
            if (found.Count > 0) return;
            foreach (var u in allies) if (u.St[120] != null && u.St[120].Stage >= 3) found.Add(u);
            if (found.Count > 0) return;
            foreach (var u in allies) if (u.St[120] != null && u.St[120].Stage < 3) found.Add(u);
            if (found.Count > 0) return;
            int[] tiers = { 116, 114, 117, 115, 113 };
            for (int t = 0; t < tiers.Length; t++)
            {
                int e = tiers[t];
                foreach (var u in allies) if (u.St[e] != null) found.Add(u);
                if (found.Count > 0) return;
            }
            foreach (var u in allies) if (HasDebuff(u)) found.Add(u);
        }

        static Action AttackAction(Battle battle, Unit unit, int slot, int attackId, bool byId = false)
        {
            if (!byId) attackId = unit.Attacks[Math.Min(slot, unit.Attacks.Length - 1)];
            var attack = battle.Data.GetAttack(attackId);
            if (attack == null) return new Action(unit, AKind.Defend);
            var action = new Action(unit, AKind.Enemy, attack, 1);
            int kind = T.NONE;
            if (unit.AiTargets != null)
                foreach (var (word, k) in unit.AiTargets)
                    if (SkillOf(unit, word) == attackId) kind = k;
            if (kind != T.NONE) action.Target = PickByKind(battle, unit, kind, attack);
            return action;
        }

        /// <summary>The unit a target kind of command 1 names (0x433350): the candidates that qualify are collected and one is drawn
        /// evenly among them (0x4346b5 - 0x4346cd); the candidates of a side are units below 2000 (0x43e6d0).</summary>
        static Unit PickByKind(Battle battle, Unit unit, int kind, EnemyAttack attack)
        {
            var allies = battle.TargetableArray(unit.Side);
            var foes = battle.TargetableArray(1 - unit.Side);
            var found = battle.PolicyScratch;
            found.Clear();
            switch (kind)
            {
                case 0: Lowest(allies, false, found); break;
                case 1: Lowest(foes, false, found); break;
                case 2: Lowest(allies, true, found); break;
                case 3: Lowest(foes, true, found); break;
                case 4: MostAilments(allies, found); break;
                // 0x4338ec: Target Mode 5 keeps petrified foes in consideration (no skipPetrified filter).
                case 5: MostAilments(foes, found); break;
                case 9: PickCurePriority(allies, found); break;
                // 0x43453a (vtable+0x7c): Target Modes 13 & 14 check true ailments ONLY (excluding stat debuffs).
                case 13: foreach (var u in allies) if (Battle.HasTrueAilment(u)) found.Add(u); break;
                case 14: foreach (var u in foes) if (Battle.HasTrueAilment(u)) found.Add(u); break;
                case 6: foreach (var u in foes) if (u.Chant != null) found.Add(u); break;
                case 7: foreach (var u in foes) if (!u.Front) found.Add(u); break;
                case 8:
                    foreach (var u in allies)
                    {
                        bool shares = false;
                        for (int i = 0; i < attack.EffId.Length; i++) if (u.St[attack.EffId[i]] != null) shares = true;
                        if (!shares) found.Add(u);
                    }
                    break;
                case 10: foreach (var u in foes) if (u.Front) found.Add(u); break;
                case 11: foreach (var u in foes) if (HasBuff(u)) found.Add(u); break;
                case 12: foreach (var u in allies) if (HasDebuff(u)) found.Add(u); break;
                case 15:
                    foreach (var u in battle.AlliesArray(unit, false))
                        if (!u.Alive && u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) found.Add(u);
                    break;
                default: break;
            }
            return found.Count == 0 ? null : found[battle.Rng.ChoiceIndex(found.Count)];
        }

        static void Lowest(Unit[] list, bool tp, List<Unit> found)
        {
            // 0x43083e: compares truncated integer percents (0..100).
            int best = int.MaxValue;
            foreach (var u in list) { int v = PyMath.Int((tp ? u.TpRatio : u.HpRatio) * 100); if (v < best) best = v; }
            foreach (var u in list) if (PyMath.Int((tp ? u.TpRatio : u.HpRatio) * 100) == best) found.Add(u);
        }
    }
}
