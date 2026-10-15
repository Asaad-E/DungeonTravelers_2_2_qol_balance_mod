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


RECORD_TABLES = ('damage', 'healing', 'actions', 'skill_uses', 'tp_spent', 'items_used', 'chants_started', 'chants_done',
                 'chants_broken', 'performances_broken', 'turns_lost', 'denied', 'delayed', 'largest_hit', 'deaths')


def unit_view(u):
    owner = getattr(u, 'owner', None)
    return (u.position, u.name, u.kind, u.side, u.level, getattr(u, 'role', None), None if owner is None else owner.position)


def key_view(key):
    if isinstance(key, tuple):
        return tuple(('stolen' if k == 'stolen' else unit_view(k) if not isinstance(k, str) else k) for k in key)
    return unit_view(key)


def record_view(record):
    """A recorder as plain data, each table in the order its keys were added; the units as the engine names them."""
    out = {name: [(key_view(k), v) for k, v in getattr(record, name).items()] for name in RECORD_TABLES}
    out['kills'] = record.kills
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

    def test_record_equals_sim(self):
        from sim import scenario
        setup = state()['setup']
        cases = [('vanilla', 'C06', None, 3), ('variant', 'C17', None, 3), ('variant', 'C24', ['attacker', 'diva', 'mage'], 4),
                 ('vanilla', 'C40', None, 2), ('variant', 'P24', None, 2), ('variant', 'C30', ['soul summoner', 'mistress', 'healer'], 3)]
        for side, cid, roles, runs in cases:
            roles = [r for r in (roles or list(setup.composition)) if r in setup.roles] or list(setup.composition)
            job = engine.make_job(side, cid, roles=roles, runs=runs, record=True)
            mine = engine.play(job)
            theirs = scenario.play_party(state()['sides'][side], setup, cid, roles, runs)
            for a, b in zip(mine, theirs):
                self.assertEqual(shape(record_view(a['record'])), shape(record_view(b['record'])), f'{side} {cid}')
                for pa, pb in zip(a['parts'], b['parts']):
                    self.assertEqual(shape(record_view(pa['record'])), shape(record_view(pb['record'])), f'{side} {cid} part')

    def test_data_of_the_tool_equals_sim(self):
        """A side changed in Python, and a setup changed in Python, go to the engine with the call."""
        from sim import measures, scenario
        setup = state()['setup']
        variant = state()['sides']['variant']
        changed = variant.with_changes([('enemies', e, 'hp', variant.enemies[e]['hp'] * 2) for e in list(variant.enemies)[:40]])
        cid = 'C12'
        mine = engine.play_checkpoint_sim(changed, setup, cid, 6)
        theirs = measures.play_checkpoint(changed, setup, cid, 6)
        self.assertEqual(shape(mine), shape(theirs))
        saved = setup.policies
        try:
            setup.policies = [dict(r) for r in saved if r['Role'] != 'diva']
            mine = engine.play_party_sim(variant, setup, 'C24', ['diva', 'attacker', 'mage'], 5)
            theirs = scenario.play_party(variant, setup, 'C24', ['diva', 'attacker', 'mage'], 5)
        finally:
            setup.policies = saved
        self.assertEqual(shape(mine), shape([plain(r) for r in theirs]))

    def test_recipe_and_chain_equal_sim(self):
        """The tested member of class_stages.py and a row of random battles shared by the runs (tools/skill_value.py)."""
        import class_stages
        import skill_value
        data, setup = state()['sides']['variant'], state()['setup']
        for cid, role in (('C10', 'healer'), ('C24', 'tank'), ('C36', None)):
            self.assertEqual(shape(class_stages.play_engine(data, setup, cid, role, 6)), shape(class_stages.play(data, setup, cid, role, 6)))
        skill = next(s for s in skill_value.candidates(data) if skill_value.place(data, setup, s))
        role, st = skill_value.place(data, setup, skill)
        cid = [c.strip() for c in str(st['Checkpoints']).split(';')][0]
        setup.settings['check_runs'] = 6
        for use in (False, True):
            self.assertEqual(shape(skill_value.play_engine(data, setup, role, cid, skill, use, 5)),
                             shape(skill_value.play(data, setup, role, cid, skill, use, 5)))

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
