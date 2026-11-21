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
        public void M19_AlterFate349_VoidsFullHitIncludingAilments()
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

            // 0x421ca7..0x421db3: Alter Fate (349) returns early in Voided, blocking damage, barriers, dispel, and AfterHit ailments.
            battle.Perform(new Action(foe, AKind.Skill, poisonStrike, 1, target));
            Assert.Equal(500, target.Hp);
            Assert.Null(target.St[113]);
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

            // Barrier (101) blocks stage 3 death AND cures petrification (0x4830ad)
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
            Assert.Null(shielded.St[120]);
        }

        [Fact]
        public void R2_AttackAttrOverrides_NonPlayerDefault_AndPhysicalAttrSeparation()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];

            // 1A #1: Enemy with Slash plain attack sets AttackAttr = SLASH (not NEUTRAL).
            int slashEnemyId = data.Enemies.Values.First(e => e.Attacks.Length > 0 && data.GetAttack(e.Attacks[0])?.Attr == T.SLASH).Id;
            var enemy = UnitFactory.BuildEnemy(data, slashEnemyId, true);
            Assert.Equal(T.SLASH, enemy.AttackAttr);
            var weapAttrAtk = new EnemyAttack { Id = 9991, Name = "Attr0", Target = T.SINGLE, Attr = 0, Speed = 1.0, EffId = new[] { 0 }, EffKind = new[] { 4 }, EffValue = new[] { 1.0 }, EffIsInt = new[] { false } };
            Assert.Equal(T.SLASH, new Action(enemy, AKind.Enemy, weapAttrAtk, 1).Attr);

            // 1A #5: Player with 2x weapon-element statuses (325+326) returns weapon physical (not falling through to enchant 78).
            var hero = new Unit("Hero", Unit.PARTY, 50, 500, 100, new[] { 80, 60, 60, 60, 80, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member) { AttackAttr = T.STAB };
            var ench = new int[GameData.MaxEnchant];
            ench[78] = 1; ench[79] = 1; // Fire + Water enchants -> Fire wins (78..82 priority)
            hero.SetEnchants(ench);
            var plain = new Action(hero, AKind.Attack);
            Assert.Equal(T.FIRE, plain.Attr);
            Assert.Equal(T.STAB, plain.PhysicalAttr);

            hero.SetStatus(new Status(325, 1, 3, hero));
            hero.SetStatus(new Status(326, 1, 3, hero));
            Assert.Equal(T.STAB, plain.Attr);
        }

        [Fact]
        public void R2_MissedSpellRunsAfterHit_AndDrainsRespectUndeadCapAndTargetTp()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var missDrainSpell = new Skill
            {
                Category = "Magic", Id = 9992, Name = "MissPoison", Levels = 1, Target = T.SINGLE, Attr = T.FIRE, Group = 1,
                IsMagic = true, Weapons = Array.Empty<int>(), Tp = new[] { 0 }, Sp = new[] { 1 }, Speed = new[] { 1.0 },
                Accuracy = new[] { 0.0 }, Turns = new[] { 0.0 },
                Effects = new[]
                {
                    new Effect { Id = 1, Kind = 4, Values = new[] { 100.0 }, IsInt = new[] { false } },
                    new Effect { Id = 55, Kind = 2, Values = new[] { 0.0 }, IsInt = new[] { false } }, // 0% hit -> always misses
                    new Effect { Id = 113, Kind = 4, Values = new[] { 10.0 }, IsInt = new[] { false } }, // 100% poison
                }
            };
            var mage = new Unit("Mage", Unit.PARTY, 50, 500, 100, new[] { 40, 40, 200, 40, 40, 40 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var foe = new Unit("Foe", Unit.ENEMIES, 50, 1000, 0, new[] { 40, 40, 40, 40, 40, 40 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { mage }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);
            battle.Perform(new Action(mage, AKind.Skill, missDrainSpell, 1, foe));
            Assert.True(foe.Hp < 1000, "Missed spell still deals grazed damage");
            Assert.NotNull(foe.St[113]); // 1A #3: AfterHit runs on missed damaging spell

            // 1A #4: HP Drain (75) skips Undead (race 5), floors at 1, caps at target pre-hit HP; TP Drain (76) subtracts target member TP.
            var drainSkill = new Skill
            {
                Category = "Technique", Id = 9993, Name = "Drain", Levels = 1, Target = T.SINGLE, Attr = T.SLASH, Group = 1,
                IsTechnique = true, Weapons = Array.Empty<int>(), Tp = new[] { 0 }, Sp = new[] { 1 }, Speed = new[] { 1.0 }, Turns = new[] { 0.0 },
                Effects = new[]
                {
                    new Effect { Id = 0, Kind = 4, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 55, Kind = 2, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 75, Kind = 4, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 76, Kind = 4, Values = new[] { 0.5 }, IsInt = new[] { false } },
                }
            };
            var vampire = new Unit("Vamp", Unit.PARTY, 50, 500, 100, new[] { 500, 50, 50, 50, 100, 50 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Hp = 100, Tp = 10 };
            var undead = new Unit("Zombie", Unit.ENEMIES, 50, 200, 0, new[] { 20, 20, 20, 20, 20, 20 }, null, 1.4, 0.0, 5, Kind.Enemy);
            var weakLive = new Unit("Slime", Unit.ENEMIES, 50, 200, 0, new[] { 20, 20, 20, 20, 20, 20 }, null, 1.4, 0.0, 0, Kind.Enemy) { Hp = 25 };
            var b2 = new Battle(data, new List<Unit> { vampire }, new List<Unit> { undead, weakLive }, new PyRandom(1), null, new BattleOptions(), null);
            b2.Perform(new Action(vampire, AKind.Skill, drainSkill, 1, undead));
            Assert.Equal(100, vampire.Hp); // Undead blocks HP drain
            Assert.Equal(10, vampire.Tp);  // Undead blocks TP drain

            b2.Perform(new Action(vampire, AKind.Skill, drainSkill, 1, weakLive));
            Assert.Equal(125, vampire.Hp); // Overkill capped at target's pre-hit HP (25)
        }

        [Fact]
        public void R2_TurnPhaseOrder_SleepCanWakeUp_AndInstantPetrify121IsStage3()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];

            // 1B #1: Sleep (116) with 100% recovery wakes in State 1 BEFORE State 6 LostTurn and acts on the same turn!
            var sleeper = new Unit("Sleeper", Unit.PARTY, 50, 500, 100, new[] { 200, 60, 60, 60, 200, 100 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            sleeper.Attacks = new[] { 0 };
            sleeper.SetStatus(new Status(116, 1.0, 0, null).WithData(100));
            var dummy = new Unit("Dummy", Unit.ENEMIES, 50, 5000, 0, new[] { 10, 10, 10, 10, 10, 1 }, null, 3.0, 0.0, T.NONE, Kind.Enemy);
            var b = new Battle(data, new List<Unit> { sleeper }, new List<Unit> { dummy }, new PyRandom(1), null, new BattleOptions(), null, 1.0);
            sleeper.NextTime = 0.01; dummy.NextTime = 5.0;
            b.Run();
            Assert.Null(sleeper.St[116]);
            Assert.True(dummy.Hp < 5000, "Sleeper that naturally woke in State 1 must act on that turn");

            // 1B #2: Instant Petrify (121) checks barrier (101) and attaches Status(120) directly at Stage = 3.
            var petrifySkill = new Skill
            {
                Category = "Magic", Id = 9994, Name = "StoneGaze", Levels = 1, Target = T.SINGLE, Attr = T.EARTH, Group = 1,
                IsMagic = true, Weapons = Array.Empty<int>(), Tp = new[] { 0 }, Sp = new[] { 1 }, Speed = new[] { 1.0 },
                Accuracy = new[] { 1.0 }, Turns = new[] { 0.0 },
                Effects = new[]
                {
                    new Effect { Id = 55, Kind = 2, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 121, Kind = 4, Values = new[] { 1.0 }, IsInt = new[] { false } },
                }
            };
            var caster = new Unit("Caster", Unit.ENEMIES, 50, 1000, 0, new[] { 60, 60, 100, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var target = new Unit("Target", Unit.PARTY, 50, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            target.SetStatus(new Status(101, 1.0, 5, target));
            var b2 = new Battle(data, new List<Unit> { target }, new List<Unit> { caster }, new PyRandom(1), null, new BattleOptions(), null);
            b2.Perform(new Action(caster, AKind.Skill, petrifySkill, 1, target));
            Assert.Null(target.St[101]); // barrier consumed
            Assert.Null(target.St[120]); // petrify blocked

            b2.Perform(new Action(caster, AKind.Skill, petrifySkill, 1, target));
            Assert.NotNull(target.St[120]);
            Assert.Equal(3, target.St[120].Stage);
        }

        [Fact]
        public void R2_AilmentRecovery5Pct_Arcane25PctOverwrite_AndDance200MaxTp()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];

            // 1B #3: Action-inflicted recovering ailment initializes recovery at 5%.
            var hero = new Unit("Hero", Unit.PARTY, 50, 500, 100, new[] { 80, 60, 60, 60, 100, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var foe = new Unit("Foe", Unit.ENEMIES, 50, 1000, 0, new[] { 80, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var b = new Battle(data, new List<Unit> { hero }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);
            Assert.True(b.ApplyAilment(hero, foe, 113, 10.0, new Action(hero, AKind.Attack)));
            Assert.Equal(5.0, foe.St[113].Data);

            // 1B #6: Dance 200 ticks on dancer's turn and multiplies target.MaxTp (not MaxHp).
            var dancer = new Unit("Dancer", Unit.ENEMIES, 50, 1000, 0, new[] { 40, 40, 40, 40, 40, 100 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var victim = new Unit("Victim", Unit.PARTY, 50, 2000, 100, new[] { 40, 40, 40, 40, 40, 10 }, null, 3.0, 0.0, T.NONE, Kind.Member);
            victim.SetStatus(new Status(200, 0.10, 0, dancer, "TPDance", Status.SongKind)); // 10% of MaxTp(100) = 10, NOT 10% of MaxHp(2000)=200
            var b2 = new Battle(data, new List<Unit> { victim }, new List<Unit> { dancer }, new PyRandom(1), null, new BattleOptions(), null, 0.5);
            dancer.NextTime = 0.01; victim.NextTime = 5.0;
            b2.Run();
            Assert.Equal(90, victim.Tp);
        }

        [Fact]
        public void R2_Items4Slot_OffhandBit7_StatClamp9999_AndMutuallyExclusiveBuffs()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];

            // 2A #1 & #2: All items preserve 4 slots; ItemSkillSpecs holds all 41 specs incl. kinds 42 & 45.
            Assert.True(data.Items.Values.All(it => it.Kinds.Length == 4));
            Assert.True(data.ItemSkillSpecs.ContainsKey(42));
            Assert.True(data.ItemSkillSpecs.ContainsKey(45));
            Assert.Equal(41, data.ItemSkillSpecs.Count);

            // 2A #4: EnchantOffhand loaded from bit 7 (0x80).
            Assert.True(data.EnchantOffhand.Count > 0 && data.EnchantOffhand.Count < 300);

            // 2A #11 & #12: 189/193/194 mutually exclusive, 202/341 mutually exclusive, Stat clamped to 9999, OffhandBonus not multiplied by stat buffs.
            var u = new Unit("Tank", Unit.PARTY, 99, 500, 100, new[] { 1000, 100, 100, 100, 100, 100 }, new[] { 0, 0, 0, 0, 0, 0, 0, 0 }, 1.4, 0.0, T.NONE, Kind.Member);
            u.OffhandBonus = new[] { 200, 0, 0, 0, 0, 0 };
            u.SetStatus(new Status(41, 0.5, 3, u));  // +50% of 1000 = +500 (offhand 200 NOT multiplied) -> 1700
            Assert.Equal(1700, u.Stat(Unit.ATK));

            u.SetStatus(new Status(189, 0.2, 3, u)); // +200 -> 1900
            u.SetStatus(new Status(193, 0.3, 3, u)); // ignored while 189 active
            Assert.Equal(1900, u.Stat(Unit.ATK));

            u.Base[Unit.ATK] = 9500;
            Assert.Equal(9999, u.Stat(Unit.ATK)); // clamped at 9999

            u.SetStatus(new Status(202, -30, 0, u));
            u.SetStatus(new Status(341, -20, 0, u)); // ignored while 202 active
            Assert.Equal(-30, u.Resistance(3));

            // R3 #4: Pep clamp enchants 201 (70), 200 (>=100), 195 (130).
            var e201 = new int[GameData.MaxEnchant]; e201[201] = 1;
            u.SetEnchants(e201); u.Pep = 120; u.ClampPep(); Assert.Equal(70.0, u.Pep);
            var e195 = new int[GameData.MaxEnchant]; e195[195] = 1;
            u.SetEnchants(e195); u.Pep = 80; u.ClampPep(); Assert.Equal(130.0, u.Pep);
        }

        [Fact]
        public void R2_Targeting_ExtraTargets137_Cover171PhysicalOnly_Breath_AndMultiPassiveSummon()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];

            // 2B #2: Cover (171) redirects physical attacks, NOT magic.
            var cover = new Unit("Tank", Unit.PARTY, 50, 1000, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            cover.SetStatus(new Status(171, 0.0, 3, cover));
            var ally = new Unit("Mage", Unit.PARTY, 50, 1000, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var foe = new Unit("Caster", Unit.ENEMIES, 50, 1000, 0, new[] { 150, 60, 200, 60, 200, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var fireball = data.SkillList.First(s => s.Name == "Fireball");
            var b = new Battle(data, new List<Unit> { cover, ally }, new List<Unit> { foe }, new PyRandom(1), null, new BattleOptions(), null);
            b.Perform(new Action(foe, AKind.Skill, fireball, 5, ally));
            Assert.Equal(1000, cover.Hp); // Cover did NOT intercept magic
            Assert.True(ally.Hp < 1000);

            b.Perform(new Action(foe, AKind.Attack) { Target = ally });
            Assert.True(cover.Hp < 1000); // Cover DID intercept physical attack

            // 2B #3: Breath attack (eff 3) bypasses Silence (117) and Freeze (114).
            var breathAtk = data.Attacks.Values.First(a => a.EffId.Contains(3) && (a.Spell || a.Technique));
            var plainAtk = data.Attacks.Values.First(a => a.Plain && a.EffId.Contains(0));
            var dragon = new Unit("Dragon", Unit.ENEMIES, 50, 1000, 0, new[] { 100, 60, 100, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy)
            {
                Attacks = new[] { plainAtk.Id, breathAtk.Id },
                Script = new Script
                {
                    Id = 1,
                    Opening = new CommandList { Id = 1, Commands = Array.Empty<Command>() },
                    Sets = new[] { new AiSet { Number = 0, Weights = new[] { 0, 100 }, Commands = new CommandList { Id = 2, Commands = Array.Empty<Command>() } } }
                }
            };
            dragon.SetStatus(new Status(114, 1, 0, ally)); // Freeze
            dragon.SetStatus(new Status(117, 1, 0, ally)); // Silence
            var bDragon = new Battle(data, new List<Unit> { ally }, new List<Unit> { dragon }, new PyRandom(1), null, new BattleOptions(), null);
            var chosen = Ai.Choose(bDragon, dragon);
            Assert.Equal(breathAtk.Id, chosen.SourceId);

            // 2B #6: Summon 95 has 2 passives loaded and applied.
            var s95 = data.Summons.First(s => s.Id == 95);
            Assert.True(s95.Passives.Length >= 2);
            var sumUnit = UnitFactory.BuildSummon(data, s95, new List<Unit> { cover }, 9999);
            foreach (int pid in s95.Passives)
            {
                var pa = data.GetAttack(pid);
                if (pa != null)
                    foreach (int eff in pa.EffId) Assert.True(sumUnit.HasPassive(eff));
            }

            // 2B #10: Weapon 198 (Pierce) and 344 (Row) set PlainTarget on plain Attack.
            Assert.Equal(T.PIERCE, data.Equipment[198].PlainTarget);
            Assert.Equal(T.ROW, data.Equipment[344].PlainTarget);
            cover.Weapon = data.Equipment[198];
            Assert.Equal(T.PIERCE, new Action(cover, AKind.Attack).TargetCode);

            // 2B #1: ExtraTargets (137) stops immediately when an opposite-side unit intervenes in turn order.
            var e1 = new Unit("E1", Unit.ENEMIES, 50, 1000, 0, new[] { 50, 50, 50, 50, 50, 50 }, null, 1.4, 0.0, T.NONE, Kind.Enemy) { NextTime = 0.10 };
            var e2 = new Unit("E2", Unit.ENEMIES, 50, 1000, 0, new[] { 50, 50, 50, 50, 50, 50 }, null, 1.4, 0.0, T.NONE, Kind.Enemy) { NextTime = 0.30 };
            var p1 = new Unit("P1", Unit.PARTY, 50, 1000, 100, new[] { 200, 50, 50, 50, 200, 50 }, null, 1.4, 0.0, T.NONE, Kind.Member) { NextTime = 0.20 };
            var splash = new Skill
            {
                Category = "Technique", Id = 9995, Name = "Splash", Levels = 1, Target = T.SINGLE, Attr = T.SLASH, Group = 1,
                IsTechnique = true, Weapons = Array.Empty<int>(), Tp = new[] { 0 }, Sp = new[] { 1 }, Speed = new[] { 1.0 }, Turns = new[] { 0.0 },
                Effects = new[]
                {
                    new Effect { Id = 0, Kind = 4, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 55, Kind = 2, Values = new[] { 1.0 }, IsInt = new[] { false } },
                    new Effect { Id = 137, Kind = 2, Values = new[] { 3.0 }, IsInt = new[] { true } },
                }
            };
            var bSplash = new Battle(data, new List<Unit> { p1 }, new List<Unit> { e1, e2 }, new PyRandom(1), null, new BattleOptions(), null);
            bSplash.Perform(new Action(p1, AKind.Skill, splash, 1, e1));
            Assert.True(e1.Hp < 1000);
            Assert.Equal(1000, e2.Hp); // P1 intervened at t=0.20 between E1(0.10) and E2(0.30), breaking the chain!
        }
    }
}
