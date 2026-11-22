using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DtEngine;
using Xunit;

namespace DtEngine.Tests
{
    /// <summary>
    /// Regression tests for medium-severity engine & AI conformity fixes (M5):
    /// - Magic RaceGuard is multiplicative (0x44ee20) rather than additive into damage cut;
    /// - Arcane Shield skips retaliation when its bearer dies from the hit (0x4251a8..0x4251b4);
    /// - MeanHits includes effect 178 (+int(val)+1 hits) matching NumberOfHits;
    /// - Murder License (319) fires linked attack 413 before the bearer's turn (0x437364..0x437488);
    /// - Enemy self-escape (effect 11) removes the enemy in random battles without counting as a kill;
    /// - AI commands 6/7 match enemy attacks by AttackId (disambiguating duplicate names) and PickByKind
    ///   selects units with the most ailments (0x4309a0..0x430a50).
    /// </summary>
    public class MediumFixesTests
    {
        static string Root()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null && !File.Exists(Path.Combine(dir.FullName, "CONTRIBUTING.md"))) dir = dir.Parent;
            if (dir == null) throw new InvalidOperationException("the repository root was not found");
            return dir.FullName;
        }

        static Snapshot LoadSnapshot() => Snapshot.Load(Path.Combine(Root(), "build", "engine_snapshot.json"));

        [Fact]
        public void M5_MagicRaceGuard_IsMultiplicativeNotAdditive()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var fireball = data.SkillList.First(s => s.Name == "Fireball");

            // Enemy of race 8 (guard enchants 227/228: 5% / 10%) casts magic on a member with Magic Barrier (183 = -0.30).
            var caster = new Unit("Spirit", Unit.ENEMIES, 40, 500, 100, new[] { 60, 60, 120, 60, 60, 60 }, null, 1.4, 0.0, 8, Kind.Enemy);
            var target = new Unit("Hero", Unit.PARTY, 40, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            target.SetStatus(new Status(183, -0.30, 5, target)); // Magic Barrier -30%

            var bNoGuard = new Battle(data, new List<Unit> { target }, new List<Unit> { caster }, new PyRandom(1), null, new BattleOptions(), null);
            var act = new Action(caster, AKind.Skill, fireball, 5);
            double dmgNoGuard = bNoGuard.MagicDamageExpected(act, target);

            // Add 1 piece of enchant 228 (race 8 large guard: 0.90x) -> multiplicative gives 0.90 * dmgNoGuard,
            // whereas additive cut would give (1 - 0.30 - 0.10) / (1 - 0.30) = 0.60 / 0.70 = 0.8571 * dmgNoGuard.
            var targetGuarded = target.CloneFresh();
            targetGuarded.SetStatus(new Status(183, -0.30, 5, targetGuarded));
            var ench = new int[GameData.MaxEnchant];
            ench[228] = 1;
            targetGuarded.SetEnchants(ench);
            var bGuarded = new Battle(data, new List<Unit> { targetGuarded }, new List<Unit> { caster.CloneFresh() }, new PyRandom(1), null, new BattleOptions(), null);
            double dmgGuarded = bGuarded.MagicDamageExpected(new Action(bGuarded.Units[1], AKind.Skill, fireball, 5), targetGuarded);

            Assert.Equal(dmgNoGuard * 0.90, dmgGuarded, 6);
        }

        [Fact]
        public void M5_ArcaneShield_DoesNotTriggerWhenBearerDies()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];

            // Siena with Arcane Shield (447) at 1 HP takes lethal 500 damage from an enemy -> must NOT reflect damage.
            bool anyReflected = false;
            for (ulong seed = 1; seed <= 40; seed++)
            {
                var siena = new Unit("Siena", Unit.PARTY, 40, 100, 100, new[] { 40, 10, 80, 80, 10, 10 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Hp = 1 };
                siena.HasUnique = true; siena.UniqueEffect = 447; siena.UniqueValue = 1.0;
                var foe = new Unit("Foe", Unit.ENEMIES, 40, 1000, 100, new[] { 500, 60, 60, 60, 500, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
                var battle = new Battle(data, new List<Unit> { siena }, new List<Unit> { foe }, new PyRandom(seed), null, new BattleOptions(), null);
                battle.Perform(new Action(foe, AKind.Attack) { Target = siena });
                if (!siena.Alive && foe.Hp < 1000) anyReflected = true;
            }
            Assert.False(anyReflected, "Arcane Shield must not retaliate after lethal damage kills its bearer");
        }

        [Fact]
        public void M5_MeanHits_IncludesEffect178()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var caster = new Unit("Hero", Unit.PARTY, 40, 400, 100, new[] { 80, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var foe = new Unit("Foe", Unit.ENEMIES, 40, 1000, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { caster }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);

            var skill = new Skill
            {
                Category = "Technique", IsTechnique = true, Id = 9998, Name = "ExtraHits", Levels = 1, Target = T.SINGLE,
                Attr = 0, Group = 0x10, Weapons = Array.Empty<int>(),
                Effects = new[]
                {
                    new Effect { Id = 0, Kind = 4, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 178, Kind = 2, Values = new[] { 2.0 }, IsInt = new[] { true } },
                },
                Tp = new[] { 5 }, Sp = new[] { 1 }, Speed = new[] { 1.0 }, Turns = new[] { 0.0 },
                Classes = Array.Empty<int>(), Range = T.SHORT
            };
            double expected = battle.MeanHits(new Action(caster, AKind.Skill, skill, 1));
            // 0x417da9..0x4180e3: hits starts at 0; effect 178 adds int(val)+1 = 3 hits and sets any=true (no extra +1 default).
            Assert.Equal(3.0, expected, 9);
        }

        [Fact]
        public void M5_MurderLicense_AndEnemyEscape_WorkAsBinary()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var escAtk = data.GetAttack(326); // Escape (effect 11)
            Assert.NotNull(escAtk);

            // Effect 11 in random battle removes escaping enemy without counting as kill.
            var hero = new Unit("Hero", Unit.PARTY, 40, 500, 100, new[] { 80, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var runner = new Unit("Neko", Unit.ENEMIES, 20, 200, 100, new[] { 40, 40, 40, 40, 40, 40 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var bEsc = new Battle(data, new List<Unit> { hero }, new List<Unit> { runner }, new PyRandom(1), null, new BattleOptions { RandomBattle = true }, null);
            bEsc.Perform(new Action(runner, AKind.Enemy, escAtk, 1) { Target = runner });
            Assert.False(runner.Alive);

            // Murder License (319; CActionPatternE1580, 0x437364..0x437488) deterministically applies raw CCommand_0119 (1.0f)
            // Instakill to a random living opponent at Inner State 12 (NOT EnemyAttack 413 Head Shot).
            var killer = new Unit("Carmilla", Unit.ENEMIES, 50, 2000, 100, new[] { 300, 80, 80, 80, 200, 100 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            killer.SetPassive(319, 1.0);
            killer.Attacks = new[] { 0 };
            var victim = new Unit("Hero", Unit.PARTY, 50, 1000, 100, new[] { 80, 50, 50, 50, 40, 10 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var bMl = new Battle(data, new List<Unit> { victim }, new List<Unit> { killer }, new PyRandom(3), null, new BattleOptions { MaxTime = 0.05 }, null);
            killer.NextTime = 0.01;
            victim.NextTime = 10.0;
            bMl.Run();
            Assert.False(victim.Alive, "Expected Murder License (319) CActionPatternE1580 to apply raw Instakill (119, 1.0f) to victim");
            Assert.False(killer.UsesById.ContainsKey(413), "Murder License must NOT execute EnemyAttack 413 (ENGINE-ONLY-01)");
        }

        [Fact]
        public void M5_AiCommand6And7_UseAttackIdAndPickByKindUsesAilmentCount()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            // Find two distinct attacks sharing the same name (e.g., Let's Snatch It Meow! 665 & 666)
            var a665 = data.GetAttack(665);
            var a666 = data.GetAttack(666);
            Assert.Equal(a665.Name, a666.Name);

            var caster = new Unit("Boss", Unit.ENEMIES, 40, 1000, 100, new[] { 80, 80, 80, 80, 80, 80 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            caster.Attacks = new[] { 665, 666, 0 };
            var allyA = new Unit("AllyA", Unit.ENEMIES, 40, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var allyB = new Unit("AllyB", Unit.ENEMIES, 40, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            allyA.SetStatus(new Status(113, 1.0, 0, null)); // 1 ailment
            allyB.SetStatus(new Status(113, 1.0, 0, null)); // 2 ailments
            allyB.SetStatus(new Status(115, 1.0, 0, null));

            // Command 7 checks uses of slot 1 (id 666) >= 1 -> must NOT fire when only id 665 was used!
            // Command 1 with kind 4 (most ailments on allies) on slot 2 must pick allyB (2 ailments) over allyA (1 ailment).
            var w = new int[16]; w[2] = 100;
            caster.Script = new Script
            {
                Opening = new CommandList
                {
                    Id = 1,
                    Commands = new[]
                    {
                        new Command { Cmd = 1, Args = new[] { 0x4002, 4 }, HasResult = false, ListId = 1 },
                        new Command { Cmd = 7, Args = new[] { 0x4001, 1 }, HasResult = true, Result = 0x4000, ListId = 1 },
                    }
                },
                Sets = new[] { new AiSet { Number = 0, Weights = w, Commands = new CommandList { Id = 2, Commands = Array.Empty<Command>() } } }
            };
            caster.UsesById[665] = 1;
            caster.Uses[a665.Name] = 1;

            var hero = new Unit("Hero", Unit.PARTY, 40, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var battle = new Battle(data, new List<Unit> { hero }, new List<Unit> { caster, allyA, allyB }, new PyRandom(1), null, new BattleOptions(), null);
            var chosen = Ai.Choose(battle, caster);
            Assert.Equal(0, chosen.Atk.Id);
            Assert.Same(allyB, chosen.Target);
        }
    }
}
