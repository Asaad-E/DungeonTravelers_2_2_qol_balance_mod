import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sample_audit_batch as sab  # noqa: E402

SCRIPT = os.path.join(ROOT, "tools", "sample_audit_batch.py")

SYNTH_TRACE = """B 0 0
U 0 Hero|party|0|1|L5|hp50|tp10
U 1 Slime|enemy|1|1|L1|hp20|tp0
S 0 1 w4
r 0x1234
r 0x5678
T 1 1 a0 A0:attack:-:L1;H0>1=1;D0>1=7; | 50/10/1/2 13/0/1/3 | w6
T 2 3 a1 A1:attack:-:L1;H1>0=0; | 50/10/1/4 13/0/1/5 | w7
T 3 4 a0 A0:attack:-:L1;H0>1=1;D0>1=13; | 50/10/1/6 0/0/0/5 | w9
E 1 0 4 3 50 50 10 1 0 0 50
"""


def make_catalog(per=8):
    cat = []
    for s in sab.STRATA_ORDER:
        for i in range(per):
            cat.append({"id": "%s%02d" % (s[:2].upper(), i), "stratum": s, "title": "t"})
    return cat


class Args:
    no_trace = True
    trace_file = None
    snapshot = None
    job = None
    dtcli = "nonexistent"
    level = 2


class StratificationTests(unittest.TestCase):
    def test_exact_stratification(self):
        m = sab.build_manifest(1, 42, make_catalog(), [], Args())
        self.assertEqual(len(m["catalog_items"]), 12)
        for s in sab.STRATA_ORDER:
            self.assertEqual(m["strata_counts"][s], 3)
            self.assertEqual(sum(1 for i in m["catalog_items"] if i["stratum"] == s), 3)
        self.assertEqual(len({i["id"] for i in m["catalog_items"]}), 12)
        self.assertEqual(m["trace_events"], [])
        self.assertEqual(m["round"], 1)
        self.assertEqual(m["seed"], 42)

    def test_real_catalog_stratification(self):
        inv = sab.load_json(sab.DEFAULT_INVENTORY)
        m = sab.build_manifest(1, 7, inv["audit_catalog"], [], Args())
        self.assertEqual([m["strata_counts"][s] for s in sab.STRATA_ORDER], [3, 3, 3, 3])

    def test_zero_overlap_across_rounds(self):
        cat = make_catalog(8)
        seen = []
        for rnd in range(1, 3):  # 8 per stratum -> 2 rounds of 3 leaves 2
            m = sab.build_manifest(rnd, 100 + rnd, cat, seen, Args())
            ids = [i["id"] for i in m["catalog_items"]]
            self.assertFalse(set(ids) & set(seen))
            seen.extend(ids)
        self.assertEqual(len(seen), len(set(seen)))

    def test_exhausted_stratum_errors(self):
        cat = make_catalog(3)
        first = [i["id"] for i in sab.sample_catalog(cat, [], __import__("random").Random(1))]
        with self.assertRaises(SystemExit):
            sab.sample_catalog(cat, first, __import__("random").Random(1))

    def test_reproducible_seed(self):
        cat = make_catalog()
        a = sab.build_manifest(1, 123, cat, [], Args())
        b = sab.build_manifest(1, 123, cat, [], Args())
        c = sab.build_manifest(1, 124, cat, [], Args())
        self.assertEqual(a, b)
        self.assertNotEqual([i["id"] for i in a["catalog_items"]], [i["id"] for i in c["catalog_items"]])


class TraceTests(unittest.TestCase):
    def test_parse_and_select(self):
        recs = sab.parse_trace_lines(SYNTH_TRACE.splitlines())
        kinds = {r["event_kind"] for r in recs}
        self.assertEqual(kinds, {"damage", "hit", "turn_end"})
        import random
        pk = sab.select_trace_events(recs, random.Random(5), 5)
        self.assertEqual(len(pk), 3)
        self.assertEqual({p["event_kind"] for p in pk}, {"damage", "hit", "turn_end"})
        self.assertEqual(len({p["id"] for p in pk}), 3)
        for p in pk:
            self.assertEqual(p["stratum"], "trace_event")
            self.assertEqual(p["seed"], 5)
            self.assertTrue(p["raw_trace_lines"][0].startswith("B "))
            self.assertTrue(p["raw_trace_lines"][-1].startswith("T "))
            json.dumps(p)

    def test_rng_context(self):
        recs = sab.parse_trace_lines(SYNTH_TRACE.splitlines())
        t1 = [r for r in recs if r["event_kind"] == "turn_end"][0]["battle_context"]
        self.assertEqual(t1["rng_words_before_turn"], 4)
        self.assertEqual(t1["rng_words_after_turn"], 6)
        self.assertEqual(t1["rng_draws_for_turn"], ["r 0x1234", "r 0x5678"])
        dmg = [r for r in recs if r["event_kind"] == "damage"][0]["event"]
        self.assertEqual((dmg["actor"], dmg["target"], dmg["amount"]), (0, 1, 7))

    def test_trace_file_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            tf = os.path.join(td, "t.txt")
            with open(tf, "w") as fh:
                fh.write(SYNTH_TRACE)
            a = Args()
            a.no_trace = False
            a.trace_file = tf
            m = sab.build_manifest(1, 9, make_catalog(), [], a)
            self.assertEqual(len(m["trace_events"]), 3)
            self.assertEqual(m["total_items"], 15)
            self.assertEqual(m["strata_counts"]["trace_event"], 3)

    def test_no_trace_source_is_pending_not_fabricated(self):
        a = Args()
        a.no_trace = False
        m = sab.build_manifest(1, 9, make_catalog(), [], a)
        self.assertEqual(m["trace_events"], [])
        self.assertTrue(m["trace_status"].startswith("pending"))


class CliTests(unittest.TestCase):
    def run_cli(self, *extra):
        return subprocess.run([sys.executable, SCRIPT] + list(extra), capture_output=True, text=True, cwd=ROOT)

    def test_cli_exit_zero_and_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            o1, o2 = os.path.join(td, "a.json"), os.path.join(td, "b.json")
            r1 = self.run_cli("--round", "1", "--seed", "2026", "--no-trace", "--out", o1)
            r2 = self.run_cli("--round", "1", "--seed", "2026", "--no-trace", "--out", o2)
            self.assertEqual(r1.returncode, 0, r1.stderr)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            with open(o1) as f1, open(o2) as f2:
                a, b = json.load(f1), json.load(f2)
            self.assertEqual(a, b)
            self.assertEqual(len(a["catalog_items"]), 12)
            self.assertEqual(a["strata_counts"]["core_combat"], 3)
            self.assertEqual(a["seed"], 2026)

    def test_cli_excludes_state_ids(self):
        with tempfile.TemporaryDirectory() as td:
            o1 = os.path.join(td, "a.json")
            r = self.run_cli("--round", "1", "--seed", "5", "--no-trace", "--out", o1)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(o1, encoding="utf-8") as fh:
                ids = json.load(fh)["sampled_item_ids"]
            st = os.path.join(td, "state.json")
            with open(st, "w", encoding="utf-8") as fh:
                json.dump({"phase4": {"sampled_item_ids": ids}}, fh)
            o2 = os.path.join(td, "b.json")
            r = self.run_cli("--round", "2", "--seed", "5", "--no-trace", "--state", st, "--out", o2)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(o2, encoding="utf-8") as fh:
                ids2 = json.load(fh)["sampled_item_ids"]
            self.assertFalse(set(ids) & set(ids2))
            self.assertEqual(len(ids2), 12)

    def test_cli_stdout_when_no_out(self):
        r = self.run_cli("--round", "1", "--seed", "1", "--no-trace")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["round"], 1)


if __name__ == "__main__":
    unittest.main()
