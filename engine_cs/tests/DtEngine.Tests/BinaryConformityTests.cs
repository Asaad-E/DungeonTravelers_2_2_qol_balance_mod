using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DtEngine;
using Xunit;

namespace DtEngine.Tests
{
    /// <summary>
    /// Regression tests for binary conformity fixes verified against DT22_en_unwrapped.exe via Capstone:
    /// B1 Double/Triple Attack on plain enemy/guest attacks (0x417d7f..0x417da4);
    /// B2 Support Shot for enemies and guests/summons (0x4253ae..0x4255be);
    /// B3 Song/Dance classification (0x47b220), enemy/guest songs, and Fall() song/dance clear (0x43c1fa);
    /// B4 Passive weapon/shield gating incl. code 19 (0x4f4910, 0x4f4cca);
    /// B5 Devil's Whisper (320) passive on actor (0x4235d5..0x42363a);
    /// B6 Charge/Focusing (178) status on actor (0x417ffe);
    /// B7 Irena Forerunner (358) charges TP (0x417713) & M18 UseItem does not charge TP (0x50b136);
    /// B8 Effects 149/150 Adult/Minor hit polarity (0x44b01e..0x44b099);
    /// B9 Enemy Defend effect 10 sets Defending state (0x47fc30..0x47fcae);
    /// B10 Arcane Shield (447) post-action retaliation skipping attackers >= 2000 (0x425157..0x425248);
    /// B11 Shadow Heart (448) keeps weapon range/attr & buffs, survives interrupt, no Doll Mastery leak (0x4fe2e0);
    /// B12 Resistance clamp [-100, +100] (0x4fc6c7..0x4fc751);
    /// M15 Action.Attr weapon-element statuses/enchants on weapon-attribute skills (0x4161e1);
    /// M16 Damage cap (296) applies after special damage (0x44f0a0..0x44f0ce);
    /// M19 Alter Fate (349) zeroes HP/TP damage only, not ailments (0x421cef);
    /// M20 Knock Down (305) checks defender weapon (0x42222c);
    /// M22 Petrification (120) 3-stage lethal tick (0x48305a..0x483115);
    /// M23 Counter anti-recursion (0x42039d) & enchant 263 unarmed Rank A delay (0x4f55ab).
    /// </summary>
    public class BinaryConformityTests
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
        public void B1_DoubleTripleAttack_AppliesToPlainEnemyAttacks()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var plainAtk = data.Attacks.Values.First(a => a.Plain && a.EffId.Contains(0) && a.Target == T.SINGLE);
            var foe = new Unit("Boss", Unit.ENEMIES, 50, 1000, 0, new[] { 100, 60, 60, 60, 100, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            foe.SetPassive(251, 1.0); // 100% Double Attack
            var hero = new Unit("Hero", Unit.PARTY, 50, 5000, 100, new[] { 80, 60, 60, 60, 80, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var battle = new Battle(data, new List<Unit> { hero }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);

            double meanHits = battle.MeanHits(new Action(foe, AKind.Enemy, plainAtk, 1));
            Assert.Equal(2.0, meanHits, 6);
        }

        [Fact]
        public void B2_SupportShot_FiresForGuestsAndEnemies()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var plainAtk = data.Attacks.Values.First(a => a.Plain && a.EffId.Contains(0) && a.Target == T.SINGLE);

            var hero = new Unit("Hero", Unit.PARTY, 50, 1000, 100, new[] { 100, 60, 60, 60, 200, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var guest = new Unit("GuestArcher", Unit.PARTY, 50, 9999, 0, new[] { 200, 60, 60, 60, 200, 60 }, null, 1.4, 0.0, T.NONE, Kind.Summon)
            {
                IsGuest = true,
                Attacks = new[] { plainAtk.Id },
            };
            guest.SetPassive(260, 1.0); // 100% Support Shot
            var foe1 = new Unit("Foe", Unit.ENEMIES, 50, 5000, 0, new[] { 60, 40, 60, 60, 40, 40 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var hero2 = hero.CloneFresh();
            var foe2 = foe1.CloneFresh();

            var bWith = new Battle(data, new List<Unit> { hero, guest }, new List<Unit> { foe1 }, new PyRandom(1), null, new BattleOptions(), null);
            bWith.Perform(new Action(hero, AKind.Attack) { Target = foe1 });

            var bWithout = new Battle(data, new List<Unit> { hero2 }, new List<Unit> { foe2 }, new PyRandom(1), null, new BattleOptions(), null);
            bWithout.Perform(new Action(hero2, AKind.Attack) { Target = foe2 });

            Assert.True(foe1.Hp < foe2.Hp, "Guest with Support Shot (260) must fire follow-up shot on ally plain attack");
        }

        [Fact]
        public void B3_SongDanceClassification_EnemySongs_AndFallClearsSlots()
        {
            Assert.True(Battle.IsSong(219));
            Assert.True(Battle.IsSong(221));
            Assert.False(Battle.IsDance(219));
            Assert.False(Battle.IsDance(221));
            Assert.True(Battle.IsDance(200));
            Assert.True(Battle.IsDance(203));
            Assert.True(Battle.IsDance(204));
            Assert.True(Battle.IsDance(205));

            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var enemySong = data.GetAttack(1457); // Heroic Quadrille (effect 219)
            Assert.NotNull(enemySong);

            var singer = new Unit("BossSinger", Unit.ENEMIES, 50, 500, 0, new[] { 80, 60, 60, 60, 80, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var hero = new Unit("Hero", Unit.PARTY, 50, 500, 100, new[] { 80, 60, 60, 60, 80, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var battle = new Battle(data, new List<Unit> { hero }, new List<Unit> { singer }, new PyRandom(1), null, new BattleOptions(), null);

            battle.Perform(new Action(singer, AKind.Enemy, enemySong, 1));
            Assert.Contains(enemySong.Name, singer.Song);
            Assert.NotNull(singer.St[219]);

            battle.LoseHp(singer, singer.Hp, hero);
            Assert.False(singer.Alive);
            Assert.Empty(singer.Song);
            Assert.Empty(singer.Dance);
        }

        [Fact]
        public void B4_PassiveWeaponAndShieldGating()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var sword = data.EquipmentList.First(p => p.Category == 0 && p.Type == 0); // Sword (code 1)
            var bow = data.EquipmentList.First(p => p.Category == 0 && p.Type == 7);   // Bow (code 8)
            var shield = data.EquipmentList.First(p => p.Category == 1);              // Shield (code 16)

            var swordMastery = data.GetSkill("Passive", 241);   // weapons=[1]
            var supportShot = data.GetSkill("Passive", 271);    // weapons=[8]
            var weaponMastery = data.GetSkill("Passive", 251);  // weapons=[19] (any weapon)
            var imperialGuard = data.GetSkill("Passive", 277);  // weapons=[16] (shield)

            var skills = new List<(int, int)> { (241, 10), (271, 10), (251, 10), (277, 10) };

            // Equipped with Bow + no shield: gets Support Shot (260) and Weapon Mastery (298), NOT Sword Mastery (243) or Imperial Guard (308).
            var archer = UnitFactory.BuildMember(data, data.Characters[0], 0, 50, T.NONE,
                new List<UnitFactory.PieceUse> { new UnitFactory.PieceUse(0, bow.Id, 0) },
                skills, 0, "Archer", false, null, T.NONE, null, null);
            Assert.True(archer.HasPassive(260));
            Assert.True(archer.HasPassive(298));
            Assert.False(archer.HasPassive(243));
            Assert.False(archer.HasPassive(308));

            // Equipped with Sword + Shield: gets Sword Mastery (243), Weapon Mastery (298), Imperial Guard (308), NOT Support Shot (260).
            var knight = UnitFactory.BuildMember(data, data.Characters[0], 0, 50, T.NONE,
                new List<UnitFactory.PieceUse> { new UnitFactory.PieceUse(0, sword.Id, 0), new UnitFactory.PieceUse(1, shield.Id, 0) },
                skills, 0, "Knight", true, null, T.NONE, null, null);
            Assert.True(knight.HasPassive(243));
            Assert.True(knight.HasPassive(298));
            Assert.True(knight.HasPassive(308));
            Assert.False(knight.HasPassive(260));

            // Unarmed: Weapon Mastery (code 19) is NOT active.
            var unarmed = UnitFactory.BuildMember(data, data.Characters[0], 0, 50, T.NONE,
                new List<UnitFactory.PieceUse>(), skills, 0, "Unarmed", true, null, T.NONE, null, null);
            Assert.False(unarmed.HasPassive(298));
            Assert.NotNull(swordMastery); Assert.NotNull(supportShot); Assert.NotNull(weaponMastery); Assert.NotNull(imperialGuard);
        }

        [Fact]
        public void B5_DevilsWhisper320_TriggersFromActorPassiveOnlyOnPreExistingTrueAilmentAndDamage()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var foe = new Unit("WhisperBoss", Unit.ENEMIES, 50, 1000, 0, new[] { 80, 60, 60, 60, 200, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            foe.SetPassive(320, 1.0); // 100% Devil's Whisper
            var hero = new Unit("Hero", Unit.PARTY, 50, 2000, 100, new[] { 80, 60, 60, 60, 20, 20 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            hero.SetStatus(new Status(113, 1.0, 0, foe)); // Pre-existing Poison

            var battle = new Battle(data, new List<Unit> { hero }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);
            battle.Perform(new Action(foe, AKind.Attack) { Target = hero });
            Assert.False(hero.Alive, "Devil's Whisper passive (320) must inflict instant death on a damaging hit against a pre-ailing target");

            // Must NOT fire when target has only Shadow Sew (123; vtable+0x68 = false at 0x4151f0).
            var heroSew = new Unit("HeroSew", Unit.PARTY, 50, 2000, 100, new[] { 80, 60, 60, 60, 20, 20 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            heroSew.SetStatus(new Status(123, 1.0, 2, foe));
            var bSew = new Battle(data, new List<Unit> { heroSew }, new List<Unit> { foe.CloneFresh() }, new PyRandom(1), null, new BattleOptions(), null);
            bSew.Units[1].SetPassive(320, 1.0);
            bSew.Perform(new Action(bSew.Units[1], AKind.Attack) { Target = heroSew });
            Assert.True(heroSew.Alive, "Shadow Sew (123) is not an ailment for Devil's Whisper (0x4151f0)");

            // Must NOT fire on a hit that applies the ailment for the first time (0x422b82 runs before 0x422bd0).
            var heroFresh = new Unit("HeroFresh", Unit.PARTY, 50, 2000, 100, new[] { 80, 60, 60, 60, 20, 20 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var scream = data.GetAttack(679); // Scream of Despair: physical + 100% Poison (113)
            var bFresh = new Battle(data, new List<Unit> { heroFresh }, new List<Unit> { foe.CloneFresh() }, new PyRandom(1), null, new BattleOptions(), null);
            bFresh.Units[1].SetPassive(320, 1.0);
            bFresh.Perform(new Action(bFresh.Units[1], AKind.Enemy, scream, 1) { Target = heroFresh });
            Assert.True(heroFresh.Alive, "Devil's Whisper must check pre-hit ailments before the current hit's ailments land");
        }

        [Fact]
        public void B6_ChargeFocusing178_ChecksActorStatusAndExactHitCount()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var foe = new Unit("Charger", Unit.ENEMIES, 50, 1000, 0, new[] { 80, 60, 60, 60, 100, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            foe.SetStatus(new Status(178, 2.0, 3, foe)); // Focusing (val=2 -> 0 + (2+1) = 3 hits at 0x417da9..0x4180e3)
            var hero = new Unit("Hero", Unit.PARTY, 50, 2000, 100, new[] { 80, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var battle = new Battle(data, new List<Unit> { hero }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);

            Assert.Equal(3.0, battle.MeanHits(new Action(foe, AKind.Attack)), 6);
            foe.SetStatus(new Status(178, 1.0, 2, foe)); // Power Charge (val=1 -> 2 hits)
            Assert.Equal(2.0, battle.MeanHits(new Action(foe, AKind.Attack)), 6);
        }

        [Fact]
        public void B7_And_M18_ForerunnerChargesTp_And_UseItemIsFree()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var fireball = data.SkillList.First(s => s.Name == "Fireball");
            int expectedCost = Battle.EffectiveTpCost(new Unit("Irena", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 100, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member), fireball, 5);
            Assert.True(expectedCost > 0);

            var irena = new Unit("Irena", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 100, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            irena.HasUnique = true; irena.UniqueEffect = 358; irena.UniqueValue = 1.0; // 100% Forerunner
            var foe = new Unit("Foe", Unit.ENEMIES, 50, 1000, 0, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { irena }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);

            // Instant-cast (not previously chanted/paid) must still deduct TP in Perform.
            battle.Perform(new Action(irena, AKind.Skill, fireball, 5, foe));
            Assert.Equal(100 - expectedCost, irena.Tp);

            // M18: item-invoked skill must NOT charge TP.
            if (data.ItemSkills.Count > 0)
            {
                var kv = data.ItemSkills.First();
                var item = data.Items.Values.FirstOrDefault(it => it.Kinds.Contains(kv.Key));
                if (item != null)
                {
                    int tpBefore = irena.Tp;
                    irena.Items[item.Id] = 1;
                    battle.UseItem(new Action(irena, AKind.Item, null, 1, foe, item.Id));
                    Assert.Equal(tpBefore, irena.Tp);
                }
            }
        }

        [Fact]
        public void B8_Effects149And150_AdultMinorPolarity()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var atk149 = data.GetAttack(1821); // Four-Letter Word (149: misses adults, hits minors)
            var atk150 = data.GetAttack(1849); // Sheep's Feast (150: misses minors, hits adults)
            var foe = new Unit("Foe", Unit.ENEMIES, 50, 1000, 0, new[] { 80, 60, 100, 60, 80, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var adult = new Unit("Adult", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Adult = true };
            var minor = new Unit("Minor", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Adult = false };
            var battle = new Battle(data, new List<Unit> { adult, minor }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);

            Assert.Equal(0.0, battle.HitChance(new Action(foe, AKind.Enemy, atk149, 1), adult));
            Assert.True(battle.HitChance(new Action(foe, AKind.Enemy, atk149, 1), minor) > 0.0);
            Assert.Equal(0.0, battle.HitChance(new Action(foe, AKind.Enemy, atk150, 1), minor));
            Assert.True(battle.HitChance(new Action(foe, AKind.Enemy, atk150, 1), adult) > 0.0);
        }

        [Fact]
        public void B9_EnemyDefendEffect10_SetsDefendingState()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var defendAtk = data.GetAttack(325); // Defend (effects: 10, 162)
            var foe = new Unit("GuardFoe", Unit.ENEMIES, 50, 1000, 0, new[] { 80, 60, 60, 60, 80, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var hero = new Unit("Hero", Unit.PARTY, 50, 500, 100, new[] { 80, 60, 60, 60, 80, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var battle = new Battle(data, new List<Unit> { hero }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);

            battle.Perform(new Action(foe, AKind.Enemy, defendAtk, 1));
            Assert.True(foe.Defending);
            Assert.Null(foe.St[10]);
        }

        [Fact]
        public void B10_ArcaneShield447_FiresPostActionAndSkipsSummons()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var siena = new Unit("Siena", Unit.PARTY, 50, 2000, 100, new[] { 40, 40, 80, 80, 40, 40 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            siena.HasUnique = true; siena.UniqueEffect = 447; siena.UniqueValue = 1.0;
            var dollAttacker = new Unit("EnemyDoll", Unit.ENEMIES, 50, 9999, 0, new[] { 200, 40, 40, 40, 200, 40 }, null, 0.0, 0.0, T.NONE, Kind.Doll);
            var opts = new BattleOptions { HasArcaneChance = true, ArcaneChance = 100 };
            var battle = new Battle(data, new List<Unit> { siena }, new List<Unit> { dollAttacker }, new PyRandom(1), null, opts, null);

            battle.Perform(new Action(dollAttacker, AKind.Attack) { Target = siena });
            Assert.Equal(9999, dollAttacker.Hp);
        }

        [Fact]
        public void B12_ResistanceClampedToMinus100Plus100()
        {
            var unit = new Unit("Hero", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, new[] { 80, -80, 0, 90, -90, 0, 0, 0 }, 1.4, 0.0, T.NONE, Kind.Member);
            unit.SetStatus(new Status(185, 50, 3, unit));  // Slash +50 -> 130 clamped to 100
            unit.SetStatus(new Status(184, -50, 3, unit)); // Stab -50 -> -130 clamped to -100
            unit.SetStatus(new Status(169, 50, 3, unit));  // Elem +50 -> Fire 140 clamped to 100
            Assert.Equal(100, unit.Resistance(0));
            Assert.Equal(-100, unit.Resistance(1));
            Assert.Equal(100, unit.Resistance(3));
        }

        [Fact]
        public void M16_DamageCap296_AppliesToSpecialDamage()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var hoh = data.GetSkill("Technique", 141); // Heaven or Hell Effect: eff 138 (10% max HP) + eff 296 (cap 222 at lv1)
            Assert.NotNull(hoh);
            var hero = new Unit("Hero", Unit.PARTY, 50, 500, 100, new[] { 80, 60, 60, 60, 200, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var boss = new Unit("BigBoss", Unit.ENEMIES, 50, 100000, 0, new[] { 80, 60, 60, 60, 10, 10 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { hero }, new List<Unit> { boss }, new PyRandom(1), null, new BattleOptions(), null);

            double cap = hoh.Effects.First(e => e.Id == 296).Values[0];
            double expected = battle.ExpectedDamage(new Action(hero, AKind.Skill, hoh, 1), boss);
            Assert.True(expected <= cap + 1e-6 && expected > 0, $"Expected capped special damage in (0, {cap}], got {expected}");
        }

        [Fact]
        public void M19_AlterFate349_ZeroesDamageWithoutBlockingAilments()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var poisonStrike = new Skill
            {
                Category = "Technique", Id = 9998, Name = "PoisonStrike", Levels = 1, Target = T.SINGLE, Attr = T.SLASH, Group = 0x11,
                IsTechnique = true, Weapons = Array.Empty<int>(), Tp = new[] { 0 }, Sp = new[] { 1 }, Speed = new[] { 1.0 }, Turns = new[] { 0.0 },
                Effects = new[]
                {
                    new Effect { Id = 0, Kind = 4, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 55, Kind = 2, Values = new[] { 1.0 }, IsInt = new[] { false } }, // 100% hit
                    new Effect { Id = 113, Kind = 4, Values = new[] { 10.0 }, IsInt = new[] { false } }, // 100% poison
                }
            };
            var target = new Unit("Yuni", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            target.HasUnique = true; target.UniqueEffect = 349; target.UniqueValue = 1.0; // 100% Alter Fate
            var foe = new Unit("Foe", Unit.ENEMIES, 50, 1000, 0, new[] { 200, 60, 60, 60, 200, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { target }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);

            battle.Perform(new Action(foe, AKind.Skill, poisonStrike, 1, target));
            Assert.Equal(500, target.Hp);
            Assert.NotNull(target.St[113]);
        }

        [Fact]
        public void M22_Petrify120_ActsAtStage1And2_KillsAtStage3UnlessBarrier()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var victim = new Unit("Victim", Unit.PARTY, 50, 500, 100, new[] { 300, 60, 60, 60, 300, 100 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            victim.Attacks = new[] { 0 };
            var foe = new Unit("Medusa", Unit.ENEMIES, 50, 5000, 0, new[] { 10, 10, 10, 10, 10, 1 }, null, 3.0, 0.0, T.NONE, Kind.Enemy);
            victim.SetStatus(new Status(120, 1.0, 0, foe));
            var battle = new Battle(data, new List<Unit> { victim }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null, 50.0);
            var res = battle.Run();
            Assert.True(res.Lost, "Gradual petrification must kill at stage 3 (0x48305a..0x483115)");
            Assert.True(foe.Hp < 5000, "Unit at petrify stage 1-2 must still act before stage 3 death (0x4fb5c0/0x4fb600)");

            // Barrier (101) blocks stage 3 death (0x41f920)
            var shielded = new Unit("Shielded", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 60, 60, 60, 100 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var st120 = new Status(120, 1.0, 0, foe) { Stage = 2 };
            shielded.SetStatus(st120);
            shielded.SetStatus(new Status(101, 1.0, 5, shielded));
            var foe2 = new Unit("Medusa2", Unit.ENEMIES, 50, 5000, 0, new[] { 10, 100, 10, 100, 10, 1 }, null, 3.0, 0.0, T.NONE, Kind.Enemy);
            var b2 = new Battle(data, new List<Unit> { shielded }, new List<Unit> { foe2 }, new PyRandom(1), null, new BattleOptions(), null, 1.5);
            shielded.NextTime = 0.01;
            foe2.NextTime = 10.0;
            b2.Run();
            Assert.True(shielded.Alive, "Barrier 101 must block stage 3 petrification death (0x41f920)");
            Assert.Null(shielded.St[101]);
        }
    }
}
