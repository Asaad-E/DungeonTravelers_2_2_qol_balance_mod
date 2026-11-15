using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DtEngine;
using DtEngine.Suite;
using Xunit;

namespace DtEngine.Tests
{
    public class SkillBatteryTests
    {
        [Fact]
        public void EvaluateVerdict_HurtingCellCannotServeOrWinScoreViaTpGain()
        {
            // Mirrors Gold Steal: no significant win-rate drop, slower won fights (-51% <= -3%),
            // worse HP (-3% <= 0), but saves TP (+10% >= 5%).
            SkillBattery.EvaluateVerdict(
                same: false,
                wins: -0.03, length: -0.51, hp: -0.03, tp: 0.10, alive: 0.0,
                winsT: 0.08, lengthT: 0.03, hpT: 0.03, tpT: 0.05, aliveT: 0.30,
                seW: 0.01, seL: 0.01, seH: 0.01, seT: 0.01, seA: 0.01,
                w: 0.08, l: 0.03, h: 0.03, tpGain: 0.05, aliveGain: 0.30, z: 2.0,
                out bool serves, out bool hurts, out bool unclear, out double score);

            Assert.True(hurts);
            Assert.False(serves);
            Assert.False(unclear);
            Assert.Equal(double.NegativeInfinity, score);
        }

        [Fact]
        public void EvaluateVerdict_WinningSignificantlyStillServesEvenIfSlower()
        {
            SkillBattery.EvaluateVerdict(
                same: false,
                wins: 0.12, length: -0.15, hp: -0.02, tp: 0.0, alive: 0.0,
                winsT: 0.08, lengthT: 0.03, hpT: 0.03, tpT: 0.05, aliveT: 0.30,
                seW: 0.01, seL: 0.01, seH: 0.01, seT: 0.01, seA: 0.01,
                w: 0.08, l: 0.03, h: 0.03, tpGain: 0.05, aliveGain: 0.30, z: 2.0,
                out bool serves, out bool hurts, out bool unclear, out double score);

            Assert.True(serves);
            Assert.False(hurts);
            Assert.False(unclear);
            Assert.True(score > 0);
        }

        [Fact]
        public void EvaluateVerdict_PureTpGainWithoutHurtingStillServes()
        {
            SkillBattery.EvaluateVerdict(
                same: false,
                wins: 0.0, length: 0.01, hp: 0.01, tp: 0.08, alive: 0.0,
                winsT: 0.08, lengthT: 0.03, hpT: 0.03, tpT: 0.05, aliveT: 0.30,
                seW: 0.01, seL: 0.01, seH: 0.01, seT: 0.01, seA: 0.01,
                w: 0.08, l: 0.03, h: 0.03, tpGain: 0.05, aliveGain: 0.30, z: 2.0,
                out bool serves, out bool hurts, out bool unclear, out double score);

            Assert.True(serves);
            Assert.False(hurts);
            Assert.False(unclear);
            Assert.Equal(1.6, score, 6);
        }

        [Fact]
        public void EvaluateVerdict_SlowerFightWithInsignificantHpGainCannotServeViaTp()
        {
            // Mirrors Gold Steal C05 boss at settled runs: -3% wins, -31% length, +1.7% HP (< 3%), +20% TP saved.
            SkillBattery.EvaluateVerdict(
                same: false,
                wins: -0.03, length: -0.31, hp: 0.017, tp: 0.20, alive: 0.0,
                winsT: 0.08, lengthT: 0.03, hpT: 0.03, tpT: 0.05, aliveT: 0.30,
                seW: 0.005, seL: 0.002, seH: 0.002, seT: 0.01, seA: 0.005,
                w: 0.08, l: 0.03, h: 0.03, tpGain: 0.05, aliveGain: 0.30, z: 2.0,
                out bool serves, out bool hurts, out bool unclear, out double score);

            Assert.False(serves);
            Assert.False(unclear);
            Assert.True(score < 1.0);
        }

        static string Root()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null && !File.Exists(Path.Combine(dir.FullName, "CONTRIBUTING.md"))) dir = dir.Parent;
            if (dir == null) throw new InvalidOperationException("the repository root was not found");
            return dir.FullName;
        }

        [Fact]
        public void RowsWithRule_BeforeStatusPlacesStatusBeforeAilmentForSage()
        {
            var root = Root();
            var snap = Snapshot.Load(Path.Combine(root, "build", "engine_snapshot.json"));
            var ctx = new Ctx(snap, root, 1, snap.MeasureInputs);

            var rows = SkillValue.RowsWithRule(ctx, "sage", "always", "status:186", 4, beforeStatus: true)
                .Cast<Obj>()
                .Where(r => Py.Str(r.Get("Role")) == "sage")
                .OrderBy(r => Py.Num(r.Get("Order")))
                .Select(r => Py.Str(r.Get("Action")))
                .ToList();

            int statusIdx = rows.IndexOf("status:186");
            int ailmentIdx = rows.FindIndex(a => a.StartsWith("ailment:"));
            Assert.True(statusIdx >= 0);
            Assert.True(ailmentIdx > statusIdx, "beforeStatus should place status: ahead of sage's ailment: rows");
        }

        [Fact]
        public void BatteryJob_UnderfilledBaseCheckpointsGiveEqualPartySizeAcrossAllRoles()
        {
            var root = Root();
            var snap = Snapshot.Load(Path.Combine(root, "build", "engine_snapshot.json"));
            var ctx = new Ctx(snap, root, 1, snap.MeasureInputs);
            var sc = ctx.Sc("variant");

            foreach (var (cid, expectedSize) in new[] { ("C03", 3), ("C05", 3), ("C06", 4) })
            {
                foreach (var b in ctx.Setup.Battery)
                {
                    foreach (var role in new[] { "shooter", "papillon", "soul summoner", "treasure hunter", "tank" })
                    {
                        var job = ClassStages.BatteryJob(ctx, cid, role, b.name, 1);
                        var names = new List<string>();
                        var party = sc.RecipeParty(job, job.Recipe, names);
                        Assert.Equal(expectedSize, party.Count(u => u.Kind == Kind.Member));
                    }
                }
            }
        }
    }
}
