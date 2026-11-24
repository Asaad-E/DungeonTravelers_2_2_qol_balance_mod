using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DtEngine;
using Xunit;

namespace DtEngine.Tests
{
    /// <summary>
    /// Regression tests for high-severity engine and policy fixes verified against DT22_en_unwrapped.exe:
    /// A2 (magic hit/evasion buffs 337/338 and Lullaby-only 278/353 at 0x44d759..0x44d95f;
    ///     speed passives 276/277/316 at 0x44a23d..0x44a303; Barrage Rondo 210 as a tracked song),
    /// A5 (Policy effective TP gating with Economy/TP-cut enchants, RandomMoveValue penalizing harmful outcomes,
    ///     T.ALLY_ROW heal row selection, and Protect checking Provoke on enemies).
    /// </summary>
    public class HighFixesTests
    {
        static string Root()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null && !File.Exists(Path.Combine(dir.FullName, "CONTRIBUTING.md"))) dir = dir.Parent;
            if (dir == null) throw new InvalidOperationException("the repository root was not found");
            return dir.FullName;
        }

        static Snapshot LoadSnapshot() => Snapshot.Load(Path.Combine(Root(), "build", "engine_snapshot.json"));

        static Row MakePolicyRow(string role, double order, string cond, string act)
        {
            var r = new Row();
            r.Cells["Role"] = role;
            r.Cells["Order"] = order;
            r.Cells["Condition"] = cond;
            r.Cells["Action"] = act;
            return r;
        }

        [Fact]
        public void A2_MagicHitAndEvasionBuffs_MatchBinary()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var fireball = data.SkillList.First(s => s.Name == "Fireball");
            var lullaby = data.SkillList.First(s => s.Id == 205);

            var caster = new Unit("Mage", Unit.PARTY, 30, 300, 100, new[] { 40, 40, 60, 60, 40, 40 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var target = new Unit("Foe", Unit.ENEMIES, 30, 500, 100, new[] { 40, 40, 60, 220, 40, 40 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { caster }, new List<Unit> { target }, new PyRandom(1), null, new BattleOptions(), null);

            var fbAction = new Action(caster, AKind.Skill, fireball, 1);
            double baseFb = battle.HitChance(fbAction, target);

            // 278 (Maid Mastery) and 353 (Maximum Maid) must NOT affect non-Lullaby magic spells.
            caster.SetPassive(278, 0.10);
            caster.SetPassive(353, 0.13);
            Assert.Equal(baseFb, battle.HitChance(fbAction, target), 9);

            // 337 raises magic accuracy and 338 raises magic evasion (0x44d88d, 0x44d8be).
            caster.SetStatus(new Status(337, 0.20, 3, caster));
            double with337 = battle.HitChance(fbAction, target);
            Assert.True(with337 > baseFb, $"Expected 337 to raise magic hit ({with337} > {baseFb})");
            target.SetStatus(new Status(338, 0.20, 3, target));
            double with337And338 = battle.HitChance(fbAction, target);
            double expected337And338 = PyMath.Int(F.MagicHit(fireball.Accuracy[0], 60, 220, 0.0, 0, 0, 0.20, 0.20, 1.0)) / 100.0;
            Assert.True(with337And338 < with337, $"Expected 338 to lower magic hit ({with337And338} < {with337})");
            Assert.Equal(expected337And338, with337And338, 9);

            // On Lullaby (skill 205), 278 + 353 apply ONCE, not twice.
            caster.PopStatus(337);
            target.PopStatus(338);
            var lulAction = new Action(caster, AKind.Skill, lullaby, 1);
            double gotLul = battle.HitChance(lulAction, target);
            double expectedLul = PyMath.Int(F.MagicHit(lullaby.Accuracy[0], 60, 220, 0.0, 0, 0, 0.23, 0.0, 1.0)) / 100.0;
            double wrongDoubleLul = PyMath.Int(F.MagicHit(lullaby.Accuracy[0], 60, 220, 0.0, 0, 0, 0.46, 0.0, 1.0)) / 100.0;
            Assert.NotEqual(expectedLul, wrongDoubleLul, 4);
            Assert.Equal(expectedLul, gotLul, 9);
        }

        [Fact]
        public void A2_SpeedPassives_276_277_316_MatchBinary()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var spartan = data.SkillList.First(s => s.Name == "Spartan");

            var owner = new Unit("SS", Unit.PARTY, 40, 400, 100, new[] { 80, 60, 80, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var enemy = new Unit("Foe", Unit.ENEMIES, 40, 1000, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { owner }, new List<Unit> { enemy }, new PyRandom(2), null, new BattleOptions(), null);
            battle.MeanWait = true;

            // 316 (Double Puppet speed) has NO effect while owner has no active dolls.
            double baseWait = battle.Wait(owner, new Action(owner, AKind.Attack), chanting: false);
            owner.SetPassive(316, 0.18);
            Assert.Equal(baseWait, battle.Wait(owner, new Action(owner, AKind.Attack), chanting: false), 9);

            // Summon an owned doll -> [battleUnit+0xd4..0xd8] non-empty -> 316 speeds up the owner.
            battle.Perform(new Action(owner, AKind.Skill, spartan, 1));
            double withDollWait = battle.Wait(owner, new Action(owner, AKind.Attack), chanting: false);
            double expectedWith316 = 1.0 - F.TurnValue(60, 1.4, 40, 1.0, 0.18, false, false, false, F.SPEED_RANDOM_MEAN);
            Assert.True(withDollWait < baseWait, $"Expected 316 to speed up puppeteer ({withDollWait} < {baseWait})");
            Assert.Equal(expectedWith316, withDollWait, 9);

            // 276 (Self Session) and 277 (On Stage) speed up non-chanting actions unconditionally (0x44a23d, 0x44a273).
            owner.SetPassive(316, 0.0);
            owner.SetPassive(276, 0.12);
            double with276 = battle.Wait(owner, new Action(owner, AKind.Attack), chanting: false);
            double expectedWith276 = 1.0 - F.TurnValue(60, 1.4, 40, 1.0, 0.12, false, false, false, F.SPEED_RANDOM_MEAN);
            Assert.Equal(expectedWith276, with276, 9);
        }

        [Fact]
        public void A2_BarrageRondo_IsTrackedAsSongAndReplacedByNewSong()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var rondo = data.SkillList.First(s => s.Name == "Barrage Rondo");
            var march = data.SkillList.First(s => s.Name == "Lightning March");

            var diva = new Unit("Diva", Unit.PARTY, 40, 400, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var enemy = new Unit("Foe", Unit.ENEMIES, 40, 1000, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { diva }, new List<Unit> { enemy }, new PyRandom(3), null, new BattleOptions(), null);

            battle.Perform(new Action(diva, AKind.Skill, rondo, 1));
            Assert.Contains("Barrage Rondo", diva.Song);
            Assert.NotNull(diva.St[210]);

            // Without Self Session (287), singing Lightning March must replace Barrage Rondo.
            battle.Perform(new Action(diva, AKind.Skill, march, 1));
            Assert.DoesNotContain("Barrage Rondo", diva.Song);
            Assert.Null(diva.St[210]);
            Assert.Contains("Lightning March", diva.Song);
        }

        [Fact]
        public void A5_PolicyTpGating_RespectsEconomyAndTpEnchants()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var inferno = data.SkillList.First(s => s.Name == "Inferno");
            int baseCost = inferno.Tp[0];
            Assert.True(baseCost >= 30);

            var witch = new Unit("Witch", Unit.PARTY, 50, 400, 100, new[] { 40, 40, 120, 80, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            witch.Skills.Add((inferno.Id, 1));
            witch.SetPassive(266, 0.35); // Economy -35% TP cost
            int effCost = Battle.EffectiveTpCost(witch, inferno, 1);
            Assert.True(effCost < baseCost);

            witch.Tp = effCost; // Enough with Economy, insufficient under raw baseCost
            var enemy = new Unit("Foe", Unit.ENEMIES, 50, 1000, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { witch }, new List<Unit> { enemy }, new PyRandom(4), null, new BattleOptions(), null);

            var opts = Policy.Options(battle, witch);
            Assert.Contains(opts, o => o.skill.Id == inferno.Id);
        }

        [Fact]
        public void A5_PolicyProtectChecksProvokedEnemy_AndAllyRowHealTargetsBestRow()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var protect = data.SkillList.First(s => s.Name == "Protect");
            var provoke = data.SkillList.First(s => s.Name == "Provoke");

            var tank = new Unit("Tank", Unit.PARTY, 40, 500, 100, new[] { 80, 100, 40, 40, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Role = "tank", HasRole = true };
            var higherDefAlly = new Unit("Pal", Unit.PARTY, 40, 500, 100, new[] { 80, 200, 40, 40, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Role = "attacker", HasRole = true };
            tank.Skills.Add((protect.Id, 1));
            tank.Skills.Add((provoke.Id, 1));

            var enemy = new Unit("Foe", Unit.ENEMIES, 40, 1000, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Enemy);
            var battle = new Battle(data, new List<Unit> { tank, higherDefAlly }, new List<Unit> { enemy }, new PyRandom(5), null, new BattleOptions(), null);
            battle.Perform(new Action(tank, AKind.Skill, provoke, 1, enemy));
            Assert.Null(tank.St[170]); // Provoke lives on enemy, not tank
            Assert.NotNull(enemy.St[170]);

            var policy = new Policy(new List<Row> { MakePolicyRow("tank", 1.0, "always", "status:162") }, snap.Setup);
            var chosen = policy.Choose(battle, tank);
            Assert.Equal(protect.Id, chosen.Skill.Id);
            Assert.Same(tank, chosen.Target);

            // Synthetic T.ALLY_ROW heal: back row injured, front row full -> must target back row member.
            var rowHeal = new Skill
            {
                Category = "Magic", IsMagic = true, Id = 9999, Name = "Row Heal", Levels = 1, Target = T.ALLY_ROW,
                Attr = -1, Group = 0x08, Weapons = Array.Empty<int>(),
                Effects = new[] { new Effect { Id = 128, Kind = 4, Values = new[] { 0.5 }, IsInt = new[] { false } } },
                Tp = new[] { 5 }, Sp = new[] { 1 }, Speed = new[] { 1.0 }, Cast = null, Accuracy = null, Turns = new[] { 0.0 },
                Classes = Array.Empty<int>(), Range = T.NO_RANGE, ChantStat = 0, Swing = 0.0
            };
            var frontAlly = new Unit("Front", Unit.PARTY, 40, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Front = true, Hp = 500, Role = "healer", HasRole = true };
            var backAlly = new Unit("Back", Unit.PARTY, 40, 500, 100, new[] { 60, 60, 60, 60, 60, 60 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Front = false, Hp = 100, Role = "mage", HasRole = true };
            frontAlly.Skills.Add((rowHeal.Id, 1));
            data.SkillById[rowHeal.Id] = rowHeal;
            try
            {
                var b2 = new Battle(data, new List<Unit> { frontAlly, backAlly }, new List<Unit> { enemy.CloneFresh() }, new PyRandom(6), null, new BattleOptions(), null);
                var healPolicy = new Policy(new List<Row> { MakePolicyRow("healer", 1.0, "ally_hp_below:0.9", "heal:0.9") }, snap.Setup);
                var hAct = healPolicy.Choose(b2, frontAlly);
                Assert.Equal(rowHeal.Id, hAct.Skill.Id);
                Assert.Same(backAlly, hAct.Target);
            }
            finally
            {
                data.SkillById.Remove(rowHeal.Id);
            }
        }

        [Fact]
        public void A5_PolicyRandomMoveValue_PenalizesEnemyHealInHeavenOrHell()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var hoh = data.SkillList.First(s => s.Name == "Heaven or Hell");
            var dmgHalf = data.ById(141); // damage outcome of Heaven or Hell

            var joker = new Unit("Joker", Unit.PARTY, 50, 500, 100, new[] { 150, 80, 60, 60, 80, 80 }, null, 1.4, 0.0, T.NONE, Kind.Member);
            var boss = new Unit("Boss", Unit.ENEMIES, 50, 10000, 100, new[] { 80, 80, 80, 80, 80, 80 }, null, 1.4, 0.0, T.NONE, Kind.Enemy) { Hp = 5000 };
            var battle = new Battle(data, new List<Unit> { joker }, new List<Unit> { boss }, new PyRandom(7), null, new BattleOptions(), null);

            double dmgOnly = Policy.DamageValue(battle, new Action(joker, AKind.Skill, dmgHalf, 1), out _);
            double hohVal = Policy.DamageValue(battle, new Action(joker, AKind.Skill, hoh, 1), out _);
            Assert.True(hohVal < 0.5 * dmgOnly, $"Expected Heaven or Hell value ({hohVal}) < 0.5 * damage-only ({0.5 * dmgOnly}) when enemy is injured");
        }

        [Fact]
        public void A6_PolicyAntiStupidity_ParryRevivePriorityAilmentCapAndRedundantHeal()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];

            // 1) Parry awareness: physical skill must not burn TP into Parry (180); fall back to 0-TP plain attack.
            var geo = data.SkillList.First(s => s.Name == "Geo Break");
            var attacker = new Unit("Yae", Unit.PARTY, 90, 1500, 300, new[] { 400, 300, 100, 100, 150, 150 }, null, 1.8, 0.0, T.SLASH, Kind.Member) { Role = "dark lord", HasRole = true };
            attacker.Skills.Add((geo.Id, 1));
            var boss = new Unit("Riko", Unit.ENEMIES, 90, 30000, 100, new[] { 300, 300, 200, 200, 100, 100 }, null, 1.0, 0.0, T.NONE, Kind.Enemy);
            boss.SetStatus(new Status(180, 0.5, 5, boss));
            var bParry = new Battle(data, new List<Unit> { attacker }, new List<Unit> { boss }, new PyRandom(10), null, new BattleOptions(), null);
            var dmgPolicy = new Policy(new List<Row> { MakePolicyRow("dark lord", 1.0, "always", "damage") }, snap.Setup);
            var chosen = dmgPolicy.Choose(bParry, attacker);
            Assert.Equal(AKind.Attack, chosen.Kind); // 0-TP poke to strip Parry, NOT 42-TP Geo Break

            // 2) Revive priority: dead healer must be revived before dead DPS sitting in slot 0.
            var deadDps = new Unit("DPS", Unit.PARTY, 50, 500, 100, new[] { 100, 80, 50, 50, 80, 80 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Role = "attacker", HasRole = true, Hp = 0, Alive = false };
            var deadHealer = new Unit("Bishop", Unit.PARTY, 50, 500, 100, new[] { 50, 80, 100, 120, 80, 80 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Role = "healer", HasRole = true, Hp = 0, Alive = false };
            var savior = new Unit("Savior", Unit.PARTY, 50, 500, 100, new[] { 80, 80, 80, 80, 80, 80 }, null, 1.4, 0.0, T.NONE, Kind.Member) { Role = "dark lord", HasRole = true };
            int reviveItemId = data.Items.First(kv => kv.Value.Kinds.Contains(8)).Key;
            savior.Items[reviveItemId] = 2;
            var bRev = new Battle(data, new List<Unit> { deadDps, deadHealer, savior }, new List<Unit> { boss.CloneFresh() }, new PyRandom(11), null, new BattleOptions(), null);
            var revPolicy = new Policy(new List<Row> { MakePolicyRow("dark lord", 1.0, "ally_down", "revive") }, snap.Setup);
            var revAct = revPolicy.Choose(bRev, savior);
            Assert.Equal(AKind.Item, revAct.Kind);
            Assert.Same(deadHealer, revAct.Target);

            // 3) Redundant heal suppression: when another ally is already chanting Circle Heal and nobody is critical (<35%), skip secondary heal.
            var circleHeal = data.SkillList.First(s => s.Name == "Circle Heal");
            var singleHeal = data.SkillList.First(s => s.Name == "Heal");
            var bishop = new Unit("Irena", Unit.PARTY, 50, 500, 200, new[] { 40, 80, 80, 120, 60, 60 }, null, 1.6, 0.0, T.NONE, Kind.Member) { Role = "healer", HasRole = true, Hp = 250 };
            var sage = new Unit("Fiora", Unit.PARTY, 50, 500, 200, new[] { 40, 80, 120, 80, 60, 60 }, null, 1.6, 0.0, T.NONE, Kind.Member) { Role = "sage", HasRole = true, Hp = 500 };
            sage.Skills.Add((singleHeal.Id, 1));
            bishop.Chant = new Action(bishop, AKind.Skill, circleHeal, 1);
            var bHeal = new Battle(data, new List<Unit> { bishop, sage }, new List<Unit> { boss.CloneFresh() }, new PyRandom(12), null, new BattleOptions(), null);
            var healPolicy = new Policy(new List<Row> { MakePolicyRow("sage", 1.0, "ally_hp_below:0.7", "heal:0.7"), MakePolicyRow("sage", 2.0, "always", "defend") }, snap.Setup);
            var sageAct = healPolicy.Choose(bHeal, sage);
            Assert.Equal(AKind.Defend, sageAct.Kind);

            // 4) Ailment spam cap: Silence (117) is capped at 2 attempts per enemy per battle.
            var silence = data.SkillList.First(s => s.Name == "Silence");
            var casterBoss = new Unit("Caster", Unit.ENEMIES, 50, 10000, 100, new[] { 80, 80, 120, 80, 60, 60 }, null, 1.0, 0.0, T.NONE, Kind.Enemy);
            int spellAtkId = data.Attacks.First(kv => kv.Value != null && !kv.Value.Passive && kv.Value.Spell).Key;
            casterBoss.Attacks = new[] { spellAtkId };
            sage.Skills.Clear();
            sage.Skills.Add((silence.Id, 1));
            var bAil = new Battle(data, new List<Unit> { sage }, new List<Unit> { casterBoss }, new PyRandom(13), null, new BattleOptions(), null);
            var ailPolicy = new Policy(new List<Row> { MakePolicyRow("sage", 1.0, "always", "ailment:117@0.01"), MakePolicyRow("sage", 2.0, "always", "defend") }, snap.Setup);
            Assert.Equal(silence.Id, ailPolicy.Choose(bAil, sage).Skill.Id);
            Assert.Equal(silence.Id, ailPolicy.Choose(bAil, sage).Skill.Id);
            Assert.Equal(AKind.Defend, ailPolicy.Choose(bAil, sage).Kind); // 3rd attempt skipped
        }
    }
}
