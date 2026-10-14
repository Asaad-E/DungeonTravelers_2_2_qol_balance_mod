using System;
using System.Diagnostics;
using System.IO;
using DtEngine;
using Xunit;

namespace DtEngine.Tests
{
    /// <summary>
    /// The tests of the engine against sim/. The golden files and the traces come from Python (engine_cs/parity/); a test writes
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

        static string Golden(string name, string script)
        {
            string path = Path.Combine(Root(), "build", name);
            if (!File.Exists(path)) Python(script + " " + path);
            return path;
        }

        [Fact]
        public void RandomGeneratorGivesWhatCPythonGives()
        {
            var (n, errors) = SelfCheck.RngCheck(Golden("engine_rng_golden.json", "engine_cs/parity/rng_golden.py"));
            Assert.True(n >= 50000);
            Assert.Empty(errors);
        }

        [Fact]
        public void FormulasGiveWhatPythonGives()
        {
            var (n, errors) = FormulaCheck.Run(Golden("engine_formulas_golden.json", "engine_cs/parity/formulas_golden.py"));
            Assert.True(n >= 50000);
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

        [Fact]
        public void TracesOfTheFixedCasesMatchPython()
        {
            // the regression cases and one checkpoint of each side, compared line by line by the Python driver
            string output = Python("engine_cs/parity/run_parity.py corpus --seeds 20261005 --runs 1 --trace 1 --workers 4 --threads 2 --only smoke");
            Assert.Contains(" 0 differences", output);
        }
    }
}
