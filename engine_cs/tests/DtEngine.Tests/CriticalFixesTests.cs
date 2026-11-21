using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DtEngine;
using Xunit;

namespace DtEngine.Tests
{
    /// <summary>
    /// Regression tests for the four critical binary-conformity fixes verified against DT22_en_unwrapped.exe:
    /// C1 (magic post-cast speed linear, 0x449c81..0x449df6),
    /// C2 (X16 Third Eye Wide dispel and X17 Positive Trance threshold parameterized per side),
    /// C3 (enemy doll summons 0x4852ca and AI command 6 doll check 0x432028..0x432156),
    /// C4 (player doll equipment/class modifiers without reset bonus 0x4f3290/0x4f7c00, doll weight 0.0 0x4fd630,
    ///     and guest doll exact EnemyAttackData actions + Double Puppet + group isolation 0x48490a/0x43c85a).
    /// </summary>
    public class CriticalFixesTests
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
        public void C1_MagicPostCastSpeed_IsLinearNotSquared()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["vanilla"];
            var fireball = data.SkillList.First(s => s.Name == "Fireball");
            Assert.True(fireball.IsMagic);
            double spd = fireball.Speed[0]; // > 1.0 (2.25 in vanilla)
            Assert.True(spd > 1.5);

            var mage = new Unit("Mage", Unit.PARTY, 10, 100, 100, new[] { 20, 20, 40, 30, 20, 30 }, null, 2.0, 0.0, T.NONE, Kind.Member);
            var enemy = UnitFactory.BuildEnemy(data, data.Enemies.Keys.First(), true);
            var battle = new Battle(data, new List<Unit> { mage }, new List<Unit> { enemy }, new PyRandom(1), null, new BattleOptions(), null);
            battle.MeanWait = true;

            var action = new Action(mage, AKind.Skill, fireball, 1);
            double got = battle.Wait(mage, action, chanting: false);
            double expectedLinear = 1.0 - F.TurnValue(30, 2.0, 10, spd, 0.0, false, false, false, F.SPEED_RANDOM_MEAN);
            double wrongSquared = 1.0 - F.TurnValue(30, 2.0, 10, spd * spd, 0.0, false, false, false, F.SPEED_RANDOM_MEAN);

            Assert.NotEqual(expectedLinear, wrongSquared, 4);
            Assert.Equal(expectedLinear, got, 9);
        }

        [Fact]
        public void C2_ExePatches_X16_And_X17_AreScopedToVariantOnly()
        {
            var snap = LoadSnapshot();
            var van = snap.Sides["vanilla"];
            var bal = snap.Sides["variant"];

            Assert.False(van.ThirdEyeDispel);
            Assert.True(bal.ThirdEyeDispel);
            Assert.Equal(100, van.PositiveTranceThreshold);
            Assert.Equal(85, bal.PositiveTranceThreshold);

            // Positive Trance (Alisia, effect 440) at Pep=100: zero bonus in vanilla, positive bonus in variant.
            var alisiaVan = new Unit("Alisia", Unit.PARTY, 50, 500, 100, new[] { 200, 100, 50, 50, 100, 100 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            alisiaVan.HasUnique = true; alisiaVan.UniqueEffect = 440; alisiaVan.UniqueValue = 5.0; alisiaVan.Pep = 100.0;
            var alisiaBal = alisiaVan.CloneFresh();

            var enemyVan = UnitFactory.BuildEnemy(van, van.Enemies.Keys.First(), true);
            var enemyBal = UnitFactory.BuildEnemy(bal, bal.Enemies.Keys.First(), true);
            var bVan = new Battle(van, new List<Unit> { alisiaVan }, new List<Unit> { enemyVan }, new PyRandom(42), null, new BattleOptions(), null);
            var bBal = new Battle(bal, new List<Unit> { alisiaBal }, new List<Unit> { enemyBal }, new PyRandom(42), null, new BattleOptions(), null);

            double dmgVan = bVan.PhysicalDamageValue(new Action(alisiaVan, AKind.Attack), enemyVan, 0, 1.0, expect: true, critical: false, out _);
            double dmgBal = bBal.PhysicalDamageValue(new Action(alisiaBal, AKind.Attack), enemyBal, 0, 1.0, expect: true, critical: false, out _);
            Assert.True(dmgBal > dmgVan, $"Expected variant Positive Trance damage ({dmgBal}) > vanilla ({dmgVan}) at Pep=100");
        }

        [Fact]
        public void C3_EnemyDollSummon_SpawnsWorkingDollsAndAiCommand6DetectsThem()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var summonFamiliar = data.GetAttack(690); // Summon Familiar: effect 146 = 2, effect 147 = 3, action = 307
            Assert.NotNull(summonFamiliar);

            // Find an enemy whose script uses command 6 on a doll summon attack, or test directly with Summon Familiar (690).
            var enemyRec = data.Enemies.Values.First(e => e.Attacks.Contains(690));
            var caster = UnitFactory.BuildEnemy(data, enemyRec.Id, true);
            var member = new Unit("Tank", Unit.PARTY, 50, 1000, 100, new[] { 100, 100, 50, 50, 80, 80 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var battle = new Battle(data, new List<Unit> { member }, new List<Unit> { caster }, new PyRandom(7), null, new BattleOptions(), null);

            battle.Perform(new Action(caster, AKind.Enemy, summonFamiliar, 1));
            var enemyDolls = battle.Units.Where(u => u.Alive && u.Kind == Kind.Doll && u.Side == Unit.ENEMIES).ToList();
            Assert.Equal(2, enemyDolls.Count);
            foreach (var d in enemyDolls)
            {
                Assert.Same(caster, d.Owner);
                Assert.Equal(690, d.SummonAttackId);
                Assert.Equal(new[] { 307 }, d.Attacks);
                Assert.Equal(0.0, d.Weight);
                Assert.Equal(caster.Base, d.Base);
            }

            // Build a 1-command AI script testing command 6 ("is attack 690 active?") -> pick otherSlot if true, else slot690.
            int slot690 = Array.IndexOf(caster.Attacks, 690);
            Assert.True(slot690 >= 0);
            int otherSlot = slot690 == 0 ? 1 : 0;
            var weights = new int[16];
            weights[slot690] = 100;
            caster.Script = new Script
            {
                Opening = new CommandList
                {
                    Id = 1,
                    Commands = new[]
                    {
                        new Command { Cmd = 6, Args = new[] { 0x4000 + slot690 }, HasResult = true, Result = 0x4000 + otherSlot, ListId = 1 }
                    }
                },
                Sets = new[]
                {
                    new AiSet { Number = 0, Weights = weights, Commands = new CommandList { Id = 2, Commands = Array.Empty<Command>() } }
                }
            };
            var picked = Ai.Choose(battle, caster);
            Assert.Equal(caster.Attacks[otherSlot], picked.SourceId);

            // Once dolls expire/are removed, command 6 evaluates false and falls back to set 0 (slot690).
            foreach (var d in enemyDolls) d.Alive = false;
            var pickedAfter = Ai.Choose(battle, caster);
            Assert.Equal(690, pickedAfter.SourceId);
        }

        [Fact]
        public void C4_PlayerDollInheritsEquipmentWithoutResetBonus_AndGuestDollsWorkWithDoublePuppet()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var sc = new Scenario(data, snap.Setup);

            // 1. Player doll inherits equipment + class modifiers, excludes crown/reset bonus, has weight 0.0.
            var party = sc.PartyOfRoles("C40", new List<string> { "soul summoner" }, null, null);
            var ss = party[0];
            Assert.NotNull(ss.DollBase);
            int row = data.GrowthRowOf(ss.ClassId, ss.PreviousClass);
            int[] rawGrowth = data.Stats(row, ss.Level);
            // Equipped Soul Summoner's DollBase ATK must exceed bare ClassLevelData growth (equipment + class mods applied).
            Assert.True(ss.DollBase[Unit.ATK] > rawGrowth[Unit.ATK],
                $"Expected DollBase ATK ({ss.DollBase[Unit.ATK]}) > bare growth ({rawGrowth[Unit.ATK]})");

            var spartan = data.Dolls.First(d => d.Skill == 95);
            var playerDoll = UnitFactory.BuildDoll(ss, spartan, 10, data);
            Assert.Equal(0.0, playerDoll.Weight);
            Assert.True(playerDoll.Base[Unit.ATK] >= ss.DollBase[Unit.ATK]);

            // Rebuild same member with crownBonus = 50: DollBase inherits crownBonus (+50 copied at 0x4f3586..0x4f358c).
            var equip = new List<UnitFactory.PieceUse> { new UnitFactory.PieceUse(0, ss.Weapon.Id, 5) };
            var uncrowned = UnitFactory.BuildMember(data, ss.Character, ss.ClassId, ss.Level, ss.PreviousClass, equip, ss.Skills, 0, "u0", true, null, T.NONE, null, null);
            var crowned = UnitFactory.BuildMember(data, ss.Character, ss.ClassId, ss.Level, ss.PreviousClass, equip, ss.Skills, 50, "u50", true, null, T.NONE, null, null);
            Assert.Equal(uncrowned.Base[Unit.ATK] + 50, crowned.Base[Unit.ATK]);
            Assert.True(crowned.DollBase[Unit.ATK] >= uncrowned.DollBase[Unit.ATK] + 50);

            // 2. Guest doll (Paracas Lv53 with passive 1561 = Double Puppet 313): keeps both Oracles (722) and Catalina (725),
            //    uses Paracas's stats (not Grimoire/Magi/Vulgate), and does not replace a party member's Oracles.
            var paracasRec = data.Npcs.First(n => n.Name == "Paracas" && n.Passives.Contains(1561));
            var paracas = UnitFactory.BuildGuest(data, paracasRec);
            Assert.True(paracas.Has(313));
            var enemy = UnitFactory.BuildEnemy(data, data.Enemies.Keys.First(), true);
            var battle = new Battle(data, new List<Unit> { ss, paracas }, new List<Unit> { enemy }, new PyRandom(3), null, new BattleOptions(), null);

            // Party member summons Oracles (skill 96, effect 229).
            var oraclesSkill = data.SkillList.First(s => s.Name == "Oracles");
            battle.Perform(new Action(ss, AKind.Skill, oraclesSkill, 10));

            // Guest Paracas summons Oracles (attack 722 -> action 1485) and Catalina (attack 725 -> action 1488).
            battle.Perform(new Action(paracas, AKind.Enemy, data.GetAttack(722), 1));
            battle.Perform(new Action(paracas, AKind.Enemy, data.GetAttack(725), 1));

            // Member's Oracles must still be alive (guest pool is isolated, 0x43c85a).
            Assert.Single(battle.Units, u => u.Alive && u.Kind == Kind.Doll && u.Owner == ss && u.PuppetEffect == 229);

            // Both of Paracas's dolls must be alive simultaneously (Double Puppet) with Paracas's own stats and real action IDs.
            var paracasDolls = battle.Units.Where(u => u.Alive && u.Kind == Kind.Doll && u.Owner == paracas).ToList();
            Assert.Equal(2, paracasDolls.Count);
            Assert.Contains(paracasDolls, d => d.SummonAttackId == 722 && d.Attacks.SequenceEqual(new[] { 1485 }) && d.Base.SequenceEqual(paracas.Base));
            Assert.Contains(paracasDolls, d => d.SummonAttackId == 725 && d.Attacks.SequenceEqual(new[] { 1488 }) && d.Base.SequenceEqual(paracas.Base));
        }
    }
}
