using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DtEngine;
using Xunit;

namespace DtEngine.Tests
{
    public class DollTests
    {
        static string Root()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null && !File.Exists(Path.Combine(dir.FullName, "CONTRIBUTING.md"))) dir = dir.Parent;
            if (dir == null) throw new InvalidOperationException("the repository root was not found");
            return dir.FullName;
        }

        static Snapshot LoadSnapshot() => Snapshot.Load(Path.Combine(Root(), "build", "engine_snapshot.json"));

        static List<Unit> DollsOfType(Battle battle, int skillId)
            => battle.Units.Where(u => u.Alive && u.Kind == Kind.Doll && u.Side == Unit.PARTY && u.Doll != null && u.Doll.Skill == skillId).ToList();

        [Fact]
        public void AddPuppet_ReplacesSameDollBeforeCheckingOwnerCap_AndForbidsDuplicatesAcrossParty()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var sc = new Scenario(data, snap.Setup);
            var party = sc.PartyOfRoles("C40", new List<string> { "soul summoner", "soul summoner" }, null, null);
            var s1 = party[0];
            var s2 = party[1];
            Assert.True(s1.Has(313));
            Assert.True(s2.Has(313));

            var enemy = UnitFactory.BuildEnemy(data, data.Enemies.Keys.First(), true);
            var battle = new Battle(data, party, new List<Unit> { enemy }, new PyRandom(1), null, new BattleOptions(), null);

            var spartan = data.SkillList.First(s => s.Name == "Spartan");
            var mercidarian = data.SkillList.First(s => s.Name == "Mercidarian");
            var musiy = data.SkillList.First(s => s.Name == "Musiy");

            // Summoner 1 brings out Spartan and Mercidarian.
            battle.Perform(new Action(s1, AKind.Skill, spartan, 10));
            battle.Perform(new Action(s1, AKind.Skill, mercidarian, 10));
            Assert.Single(DollsOfType(battle, spartan.Id));
            Assert.Single(DollsOfType(battle, mercidarian.Id));

            // Recasting Mercidarian by Summoner 1 (with Double Puppet) replaces her old Mercidarian
            // BEFORE checking the 2-doll owner cap (0x43c862 - 0x43c960), keeping Spartan alive.
            var firstMerc = DollsOfType(battle, mercidarian.Id)[0];
            battle.Perform(new Action(s1, AKind.Skill, mercidarian, 10));
            var mercs = DollsOfType(battle, mercidarian.Id);
            Assert.Single(mercs);
            Assert.NotSame(firstMerc, mercs[0]);
            Assert.Single(DollsOfType(battle, spartan.Id));

            // Summoner 2 casting Mercidarian removes Summoner 1's Mercidarian (party-wide uniqueness).
            battle.Perform(new Action(s2, AKind.Skill, mercidarian, 10));
            mercs = DollsOfType(battle, mercidarian.Id);
            Assert.Single(mercs);
            Assert.Same(s2, mercs[0].Owner);
            Assert.Single(DollsOfType(battle, spartan.Id));

            // Summoner 1 now has only 1 doll left (Spartan), so she can add Musiy cleanly.
            battle.Perform(new Action(s1, AKind.Skill, musiy, 7));
            Assert.Equal(2, battle.Units.Count(u => u.Alive && u.Kind == Kind.Doll && u.Owner == s1));
            Assert.Single(DollsOfType(battle, musiy.Id));
        }

        [Fact]
        public void SoulSummonerPolicy_FillsDistinctDollsAcrossMultipleSummoners()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var sc = new Scenario(data, snap.Setup);
            var party = sc.PartyOfRoles("C40", new List<string> { "soul summoner", "soul summoner", "soul summoner" }, null, null);
            var enemy = UnitFactory.BuildEnemy(data, data.Enemies.Keys.First(), true);
            var battle = new Battle(data, party, new List<Unit> { enemy }, new PyRandom(2), null, new BattleOptions(), null);

            // Policy has 5 named dolls in priority order: Mercidarian | Spartan | Musiy | Catalina | Oracles.
            // Two Soul Summoners fill 4 distinct dolls; the 3rd fills the 5th and then falls through to damage.
            var picked = new List<string>();
            foreach (var caster in new[] { party[0], party[1], party[0], party[1], party[2] })
            {
                var act = sc.Policy.Choose(battle, caster);
                Assert.Equal(AKind.Skill, act.Kind);
                picked.Add(act.Skill.Name);
                battle.Perform(act);
            }
            Assert.Equal(new[] { "Mercidarian", "Spartan", "Musiy", "Catalina", "Oracles" }, picked);
            Assert.Equal(5, battle.Units.Count(u => u.Alive && u.Kind == Kind.Doll && u.Side == Unit.PARTY));

            // Once all 5 policy dolls are already out on the side, a free slot falls through to an attack/skill
            // instead of replacing a teammate's doll.
            var fallback = sc.Policy.Choose(battle, party[2]);
            Assert.DoesNotContain(fallback.SourceName, picked);
        }

        [Fact]
        public void StarDustArrow_RemainsPerOwnerSubjectToActiveDollCap()
        {
            var snap = LoadSnapshot();
            var data = snap.Sides["variant"];
            var sc = new Scenario(data, snap.Setup);
            var party = sc.PartyOfRoles("C40", new List<string> { "shooter", "shooter", "shooter", "shooter", "shooter" }, null, null);
            var enemy = UnitFactory.BuildEnemy(data, data.Enemies.Keys.First(), true);
            var battle = new Battle(data, party, new List<Unit> { enemy }, new PyRandom(3), null, new BattleOptions(), null);
            var arrow = data.SkillList.First(s => s.Name == "Star Dust Arrow");

            battle.Perform(new Action(party[0], AKind.Skill, arrow, 10));
            battle.Perform(new Action(party[1], AKind.Skill, arrow, 10));

            Assert.Equal(3, battle.Units.Count(u => u.Alive && u.Arrow && u.Owner == party[0]));
            Assert.Equal(3, battle.Units.Count(u => u.Alive && u.Arrow && u.Owner == party[1]));

            // Casting Star Dust Arrow across 5 archers (5 x 3 = 15) stops at the 12-doll active cap (0x43a1a0).
            battle.Perform(new Action(party[2], AKind.Skill, arrow, 10));
            battle.Perform(new Action(party[3], AKind.Skill, arrow, 10));
            battle.Perform(new Action(party[4], AKind.Skill, arrow, 10));
            Assert.Equal(12, battle.Units.Count(u => u.Alive && u.Kind == Kind.Doll && u.ShadowOf == null));
        }
    }
}
