using System;
using System.Diagnostics;
using System.IO;
using DtEngine;
using Xunit;

namespace DtEngine.Tests
{
    /// <summary>
    /// The tests of the engine. The golden files were recorded from CPython and the Python formulas before sim/ was removed (2026-10-16)
    /// and are kept in golden/; earlier, a test wrote
    /// them first when they are not there. Python 3 with the dependencies of the repository must be on the path.
    /// </summary>
    public class ParityTests
    {
        static string Root()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null && !File.Exists(Path.Combine(dir.FullName, "CONTRIBUTING.md"))) dir = dir.Parent;
            if (dir == null) throw new InvalidOperationException("the repository root was not found");
            return dir.FullName;
        }

        static string Python(string args)
        {
            var psi = new ProcessStartInfo("python", args)
            {
                WorkingDirectory = Root(), RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false,
            };
            psi.Environment["PYTHONIOENCODING"] = "utf-8";
            using (var p = Process.Start(psi))
            {
                string output = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
                p.WaitForExit();
                if (p.ExitCode != 0) throw new InvalidOperationException("python " + args + " failed:\n" + output);
                return output;
            }
        }

        /// <summary>A golden file of the tests: what CPython and the Python formulas gave, recorded once (a fixed sample, kept with
        /// the tests since the Python simulator was removed on 2026-10-16).</summary>
        static string Golden(string name, string script)
        {
            return Path.Combine(Root(), "engine_cs", "tests", "DtEngine.Tests", "golden", name);
        }

        [Fact]
        public void RandomGeneratorGivesWhatCPythonGives()
        {
            var (n, errors) = SelfCheck.RngCheck(Golden("engine_rng_golden.json", "engine_cs/parity/rng_golden.py"));
            Assert.True(n >= 10000);   // the stored sample: 5 seeds
            Assert.Empty(errors);
        }

        [Fact]
        public void FormulasGiveWhatPythonGives()
        {
            var (n, errors) = FormulaCheck.Run(Golden("engine_formulas_golden.json", "engine_cs/parity/formulas_golden.py"));
            Assert.True(n >= 5000);    // the stored sample: 6,000 cases over every formula
            Assert.Empty(errors);
        }

        [Fact]
        public void RoundingToDecimalsGivesWhatPythonGives()
        {
            var (n, errors) = SelfCheck.RoundCheck(Golden("engine_round_golden.json", "engine_cs/parity/round_golden.py"));
            Assert.True(n >= 4000);
            Assert.Empty(errors);
        }

        [Fact]
        public void TheTextOfFloatsMeansAndJsonIsWhatPythonGives()
        {
            var (n, errors) = DtEngine.Suite.PyFormatCheck.Run(Golden("engine_pyformat_golden.json", "engine_cs/parity/py_format_golden.py"));
            Assert.True(n >= 20000);
            Assert.Empty(errors);
        }

        [Fact]
        public void PySumFollowsTheBuiltInSum()
        {
            // 0.1 + 0.2 + 0.3 with compensation is 0.6, where the plain sum gives 0.6000000000000001
            var s = new PySum();
            s.AddFloat(0.1); s.AddFloat(0.2); s.AddFloat(0.3);
            Assert.Equal(0.6, s.Result);
            Assert.NotEqual(0.6, 0.1 + 0.2 + 0.3);
        }

        [Fact]
        public void SnapshotLoadsAndBuildsTheReferenceParty()
        {
            string path = Path.Combine(Root(), "build", "engine_snapshot.json");
            if (!File.Exists(path)) Python("tools/engine_export.py");
            var snap = Snapshot.Load(path);
            Assert.Contains("vanilla", snap.Sides.Keys);
            Assert.Contains("variant", snap.Sides.Keys);
            var sc = new Scenario(snap.Sides["variant"], snap.Setup);
            var party = sc.PartyOfRoles("C10", snap.Setup.Composition, null, null);
            Assert.True(party.Count >= 4);
            foreach (var u in party) Assert.True(u.MaxHp > 0);
        }

        static Snapshot LoadSnapshot()
        {
            string path = Path.Combine(Root(), "build", "engine_snapshot.json");
            if (!File.Exists(path)) Python("tools/engine_export.py");
            return Snapshot.Load(path);
        }

        [Fact]
        public void PartiesAndEnemiesMadeFromTemplatesPlayLikeFreshOnes()
        {
            // a job that comes after another one with the same party and enemies gets copies of what the first one built; the same job
            // played alone builds its own. Their traces must be the same, line by line.
            var snap = LoadSnapshot();
            foreach (var side in new[] { "vanilla", "variant" })
                foreach (var cid in new[] { "C06", "C24", "C40" })
                {
                    JobSpec Make(string id, ulong seed) => new JobSpec { Id = id, Side = side, Cid = cid, Runs = 1, Seed = seed, EnemyKind = "checkpoint", Trace = 1 };
                    var after = JobRunner.Run(snap, new System.Collections.Generic.List<JobSpec> { Make("first", 5), Make("second", 100) }, 1);
                    var alone = JobRunner.Run(snap, new System.Collections.Generic.List<JobSpec> { Make("second", 100) }, 1);
                    Assert.Null(after[1].Error);
                    Assert.NotEmpty(alone[0].TraceLines);
                    Assert.Equal(alone[0].TraceLines, after[1].TraceLines);
                }
        }

        [Fact]
        public void TheRecorderAddsUpToTheFiguresOfTheBattleAndDoesNotDependOnThreads()
        {
            var snap = LoadSnapshot();
            JobSpec Make() => new JobSpec { Id = "rec", Side = "variant", Cid = "C24", Runs = 4, Seed = 7, EnemyKind = "checkpoint", Record = true };
            var one = JobRunner.Run(snap, new System.Collections.Generic.List<JobSpec> { Make() }, 1)[0];
            var many = JobRunner.Run(snap, new System.Collections.Generic.List<JobSpec> { Make() }, 4)[0];
            Assert.Null(one.Error);
            for (int k = 0; k < 4; k++)
                for (int i = 0; i < one.Runs[k].Parts.Count; i++)
                {
                    var part = one.Runs[k].Parts[i];
                    Assert.NotNull(part.Record);
                    int damage = 0, actions = 0;
                    for (int j = 0; j < part.Record.Damage.Count; j++) if (part.Record.Damage.Keys[j].Unit.Side == Unit.ENEMIES) damage += (int)part.Record.Damage.Values[j];
                    for (int j = 0; j < part.Record.Actions.Count; j++) if (part.Record.Actions.Keys[j].Unit.Side == Unit.ENEMIES) actions += (int)part.Record.Actions.Values[j];
                    Assert.Equal(part.EnemyDamage, damage);
                    Assert.Equal(part.EnemyActions, actions);
                    Assert.Equal(part.Record.TraceLine(), many.Runs[k].Parts[i].Record.TraceLine());
                }
        }



    }
}
