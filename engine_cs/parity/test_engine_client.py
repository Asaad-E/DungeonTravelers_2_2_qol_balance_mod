"""
The figures of tools/engine_client.py (the C# engine) equal those of sim/, for a sample of jobs.

    python -m unittest discover -s engine_cs/parity -p "test_engine_client.py"

The sample: parties of several compositions at several checkpoints on both sides (sim.scenario.play_party), the summary of a job
(sim.measures.summary), sim.measures.play_checkpoint, sim.measures.expedition, sim.measures.check_change and
sim.scenario.walked_zones. Floats are compared for equality, and so are the types of the figures.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
for path in (PROJECT, os.path.join(PROJECT, 'tools'), HERE):
    if path not in sys.path:
        sys.path.insert(0, path)

import engine_client as engine  # noqa: E402
import pyref  # noqa: E402

STATE = {}


def state():
    if not STATE:
        STATE.update(pyref.load_state())
    return STATE


def plain(result):
    """A result of sim.scenario.play without the recorder."""
    out = {k: v for k, v in result.items() if k not in ('record', 'parts')}
    out['parts'] = [{k: v for k, v in p.items() if k != 'record'} for p in result['parts']]
    return out


def shape(value):
    """The value with the type of each figure, to compare both."""
    if isinstance(value, dict):
        return {k: shape(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [shape(v) for v in value]
    return (type(value).__name__, value)


class EngineClientTest(unittest.TestCase):
    def test_play_party_equals_sim(self):
        from sim import scenario
        setup = state()['setup']
        cases = [('vanilla', 'C06', None, 3), ('variant', 'C17', None, 3), ('variant', 'C24', ['attacker', 'diva', 'mage'], 4),
                 ('vanilla', 'C40', None, 2), ('variant', 'P24', None, 2)]
        for side, cid, roles, runs in cases:
            roles = roles or list(setup.composition)
            roles = [r for r in roles if r in setup.roles] or list(setup.composition)
            mine = engine.play_party(side, cid, roles, runs)
            theirs = [plain(r) for r in scenario.play_party(state()['sides'][side], setup, cid, roles, runs)]
            self.assertEqual(shape(mine), shape(theirs), f'{side} {cid}')

    def test_summary_equals_sim(self):
        from sim import measures, scenario
        setup = state()['setup']
        for side, cid in (('vanilla', 'C10'), ('variant', 'C30')):
            job = engine.make_job(side, cid, roles=list(setup.composition), runs=5, seed=77)
            mine = engine.summary(job)
            cp = setup.checkpoint(cid)
            data = state()['sides'][side]
            raw = scenario.play(data, setup, lambda: scenario.party_of_roles(data, setup, cid, list(setup.composition)),
                                lambda: [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)], runs=5, seed=77)
            self.assertEqual(shape(mine), shape(measures.summary(raw)), f'{side} {cid}')

    def test_play_checkpoint_equals_sim(self):
        from sim import measures
        setup = state()['setup']
        for side, cid, runs in (('vanilla', 'C03', 4), ('variant', 'C22', 4), ('variant', 'P10', 3)):
            mine = engine.play_checkpoint(side, cid, runs)
            theirs = measures.play_checkpoint(state()['sides'][side], setup, cid, runs)
            self.assertEqual(shape(mine), shape(theirs), f'{side} {cid}')

    def test_expedition_equals_sim(self):
        from sim import measures
        setup = state()['setup']
        data = state()['sides']['variant']
        zone = next(z['name'] for z in data.floors if z['formations'] and z['name'].startswith('St05'))
        mine = engine.expedition('variant', zone, 20, 'C10', battles=6, runs=4)
        theirs = measures.expedition(data, setup, zone, 20, 'C10', battles=6, runs=4)
        self.assertEqual(shape(mine), shape(theirs))
        mine = engine.expedition('variant', zone, 20, 'C10', roles=['attacker', 'diva'], battles=4, runs=3, kit=0)
        theirs = measures.expedition(data, setup, zone, 20, 'C10', roles=['attacker', 'diva'], battles=4, runs=3, kit=0)
        self.assertEqual(shape(mine), shape(theirs))

    def test_check_change_equals_sim(self):
        from sim import measures
        setup = state()['setup']
        mine = engine.check_change('C05', 'C18', runs=4)
        theirs = measures.check_change(state()['sides']['vanilla'], setup, [], ['C05', 'C18'], runs=4, changed=state()['sides']['variant'])
        self.assertEqual(shape(mine), shape([(cid, b, a, o) for cid, b, a, o in theirs]))

    def test_walked_zones_equals_sim(self):
        from sim import scenario
        data, setup = state()['sides']['variant'], state()['setup']
        for floor, level in (('St05_1010', 20), ('St10_0010', 40), ('St00_0010', 3)):
            mine = engine.walked_zones('variant', floor, level)
            theirs = [z['name'] for z in scenario.walked_zones(data, setup, floor, level)]
            self.assertEqual(mine, theirs, f'{floor} {level}')


if __name__ == '__main__':
    unittest.main()
