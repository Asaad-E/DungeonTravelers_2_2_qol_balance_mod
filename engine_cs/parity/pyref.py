"""
The Python side of the parity tests: plays a job of the engine's job format with sim/ (which stays as it is) and, when asked,
writes the same trace lines as the C# engine (engine_cs/src/DtEngine/Trace.cs). Nothing of sim/ is edited: the methods of
sim.battle.Battle are wrapped at run time from here, and the generator of sim.scenario.play is replaced by one that counts
the 32-bit words it draws (engine_cs/parity/pyrng.py).

A job is a dict:
    id, side ('vanilla' | 'variant'), runs, seed, trace (0, 1 or 2), kit (int or None), options ({name: value}),
    party   {cid, roles (list or None), level (int or None), crown (int or None)}
    enemies {kind: 'checkpoint'} | {kind: 'fixed', battles: [[floor, number], ...]} | {kind: 'zone', floor: name, battles: n}
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
for path in (PROJECT, os.path.join(PROJECT, 'tools'), HERE):
    if path not in sys.path:
        sys.path.insert(0, path)

from pyrng import CountingRandom, fmt_num  # noqa: E402

STATS = ('atk', 'def', 'int', 'res', 'dex', 'agi')


class Tracer:
    def __init__(self):
        self.active = False
        self.level = 0
        self.lines = []
        self.events = []
        self.run = 0
        self.battle_index = 0
        self.turn = 0
        self.plain = False

    def reset(self, level):
        self.active = level > 0
        self.level = level
        self.lines = []
        self.events = []
        self.battle_index = 0
        self.turn = 0


TRACER = Tracer()
EXTRA = {}            # skills given on top of the plan to every member of the party of the job in hand ({id: level})
EXTRA_ENCHANTS = {}   # enchantments (pieces of each) added to every member of that party ({id: pieces})


def unit_line(u):
    weapon = getattr(u, 'weapon', None)
    skills = ','.join(f'{sid}:{lv}' for sid, lv in u.skills.items())
    passives = ','.join(f'{e}={fmt_num(v)}' for e, v in sorted(u.passives.items()))
    enchants = ','.join(f'{e}:{n}' for e, n in sorted(u.enchants.items()) if n > 0)
    items = ','.join(f'{i}:{n}' for i, n in sorted(u.items.items()))
    unique = f'{u.unique[0]}:{fmt_num(u.unique[1])}' if u.unique else '-'
    slot = getattr(u, 'slot', None)
    return ('U {pos} {name}|{kind}|{side}|{front}|L{level}|hp{hp}|tp{tp}|st{st}|rs{rs}|w{w}|sw{sw}|role{role}|cls{cls}|sk{sk}|pv{pv}|en{en}'
            '|im{im}|it{it}|at{at}|ar{ar}|aa{aa}|wp{wp}|un{un}|ad{ad}|sh{sh}|sl{sl}').format(
        pos=u.position, name=u.name, kind=u.kind, side=u.side, front=1 if u.front else 0, level=u.level, hp=fmt_num(u.max_hp_base),
        tp=fmt_num(u.max_tp), st=','.join(fmt_num(u.base[s]) for s in STATS), rs=','.join(fmt_num(r) for r in u.resist_base),
        w=fmt_num(u.weight), sw=fmt_num(u.swing), role=getattr(u, 'role', '-'),
        cls='-' if u.class_id is None else u.class_id, sk=skills, pv=passives, en=enchants,
        im=','.join(sorted(u.immune)), it=items, at=','.join(str(a) for a in u.attacks), ar=u.attack_range, aa=u.attack_attr,
        wp='-' if weapon is None else weapon['id'], un=unique, ad=1 if u.adult else 0, sh=1 if u.shield else 0,
        sl='-' if slot is None else slot)


def _flush_rng(battle):
    rng = battle.rng
    log = getattr(rng, 'log', None)
    if TRACER.level >= 2 and log:
        TRACER.lines.extend('r ' + entry for entry in log)
        del log[:]


def install():
    """Wraps the methods of sim.battle.Battle that the trace reads. Idempotent."""
    from sim import battle as B
    from sim import scenario
    if getattr(B.Battle, '_parity_installed', False):
        return
    B.Battle._parity_installed = True
    Battle = B.Battle
    orig = {name: getattr(Battle, name) for name in ('run', 'start', 'turn', 'perform', 'hits', 'damage', 'restore', 'lose_hp')}

    def run(self):
        t = TRACER
        if not t.active:
            return orig['run'](self)
        t.turn = 0
        if t.level >= 2 and getattr(self.rng, 'log', None) is None:
            self.rng.log = []
        t.lines.append(f'B {t.run} {t.battle_index}')
        for u in self.units:
            t.lines.append(unit_line(u))
        result = orig['run'](self)
        t.lines.append('E {} {} {} {} {} {} {} {} {} {} {}'.format(
            int(result['won']), int(result['lost']), fmt_num(result['time']), result['actions'], fmt_num(result['lowest_hp']),
            fmt_num(result['hp_left']), fmt_num(result['tp_left']), result['alive'], result['enemy_damage'],
            result['enemy_actions'], result['party_max_hp']))
        t.battle_index += 1
        return result

    def start(self):
        orig['start'](self)
        t = TRACER
        if t.active:
            _flush_rng(self)
            t.lines.append('S' + ''.join(' ' + fmt_num(u.next_time) for u in self.units) + f' w{self.rng.words}')

    def turn(self, unit):
        t = TRACER
        if not t.active:
            return orig['turn'](self, unit)
        t.events = []
        orig['turn'](self, unit)
        _flush_rng(self)
        t.turn += 1
        states = ''.join(' {}/{}/{}/{}'.format(fmt_num(u.hp), fmt_num(u.tp), 1 if u.alive else 0, fmt_num(u.next_time)) for u in self.units)
        t.lines.append(f'T {t.turn} {fmt_num(self.time)} a{unit.position} {"".join(t.events)} |{states} | w{self.rng.words}')

    def perform(self, action):
        t = TRACER
        if t.active:
            name = getattr(action.source, 'name', None)
            t.events.append(f'A{action.actor.position}:{action.kind}:{"-" if name is None else name}:L{action.level};')
        return orig['perform'](self, action)

    def hits(self, action, target):
        ok = orig['hits'](self, action, target)
        if TRACER.active:
            TRACER.events.append(f'H{action.actor.position}>{target.position}={int(ok)};')
        return ok

    def damage(self, action, target, index):
        amount = orig['damage'](self, action, target, index)
        if TRACER.active and amount is not None:
            TRACER.events.append(f'D{action.actor.position}>{target.position}={fmt_num(amount)};')
        return amount

    def restore(self, unit, amount):
        gained = orig['restore'](self, unit, amount)
        if TRACER.active and gained > 0:
            TRACER.events.append(f'R{unit.position}+{fmt_num(gained)};')
        return gained

    def lose_hp(self, unit, amount, source):
        if TRACER.active and unit.alive and amount > 0:
            TRACER.events.append(f'L{unit.position}-{fmt_num(amount)};')
        return orig['lose_hp'](self, unit, amount, source)

    for name, fn in (('run', run), ('start', start), ('turn', turn), ('perform', perform), ('hits', hits), ('damage', damage),
                     ('restore', restore), ('lose_hp', lose_hp)):
        setattr(Battle, name, fn)

    # the generator of scenario.play: random.Random(seed + k) becomes a generator that counts its words
    def make_random(seed=None):
        if TRACER.plain:
            import random
            return random.Random(seed)
        r = CountingRandom(seed)
        if TRACER.active and TRACER.level >= 2:
            r.log = []
        return r

    scenario.random = types.SimpleNamespace(Random=make_random)

    # skills given on top of the plan (build_role_member has the argument; reference_party does not pass it)
    original_member = scenario.build_role_member

    def build_role_member(*args, **kwargs):
        if EXTRA and kwargs.get('extra_skills') is None:
            kwargs['extra_skills'] = dict(EXTRA)
        return original_member(*args, **kwargs)

    scenario.build_role_member = build_role_member

    # enchantments added to every member, through the argument `forged` of build_member
    original_build = scenario.build_member

    def build_member(*args, **kwargs):
        if EXTRA_ENCHANTS:
            merged = dict(kwargs.get('forged') or {})
            for e, n in EXTRA_ENCHANTS.items():
                merged[e] = merged.get(e, 0) + n
            kwargs['forged'] = merged
        return original_build(*args, **kwargs)

    scenario.build_member = build_member


def load_state():
    from sim import setup as setup_mod
    from sim.data import game_data
    from sim.variant import balance_data
    vanilla = game_data()
    return {'sides': {'vanilla': vanilla, 'variant': balance_data(vanilla)}, 'setup': setup_mod.load()}


def _result_dict(r):
    keys = ('won', 'lost', 'time', 'actions', 'lowest_hp', 'enemy_damage', 'enemy_actions', 'party_max_hp', 'hp_left', 'tp_left', 'alive')
    out = {k: (bool(r[k]) if k in ('won', 'lost') else r[k]) for k in keys}
    return out


def run_job(job, state):
    """Plays the job with sim/. Returns (result dict, trace lines)."""
    from sim import measures, scenario
    install()
    data = state['sides'][job['side']]
    setup = state['setup']
    cp = setup.checkpoint(job['party']['cid'])
    party_spec, enemy_spec = job['party'], job['enemies']
    roles = party_spec.get('roles') or list(setup.composition)
    options = dict(job.get('options') or {})
    saved_comp, saved_kit, saved_bag = setup.composition, setup.settings.get('kit_count'), setup.kit
    TRACER.reset(int(job.get('trace') or 0))
    EXTRA.clear()
    EXTRA.update({int(k): int(v) for k, v in (job.get('extra_skills') or {}).items()})
    EXTRA_ENCHANTS.clear()
    EXTRA_ENCHANTS.update({int(k): int(v) for k, v in (job.get('extra_enchants') or {}).items()})
    runs = []
    try:
        if job.get('kit') is not None:
            setup.settings['kit_count'] = job['kit']
        if job.get('bag') is not None:
            setup.kit = [{'Item_ID': int(i), 'Share': 1} for i in job['bag']]
        setup.composition = list(roles)
        level = party_spec.get('level')
        if level is None:
            level = scenario.reference_levels(data, setup)[cp['ID']][0]
        gear = scenario.checkpoint_gear(data, setup, cp['ID'])
        crown = party_spec.get('crown')
        if crown is None:
            crown = int(cp['Crown bonus'] or 0)

        def party_factory():
            return scenario.reference_party(data, setup, cp['Chapter'], level, gear, crown, cp['Floor'])

        for k in range(int(job['runs'])):
            seed = int(job['seed']) + k
            TRACER.run = k
            TRACER.battle_index = 0
            if enemy_spec['kind'] == 'checkpoint':
                def enemy_factory():
                    return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
                battle_setup = options
            elif enemy_spec['kind'] == 'fixed':
                def enemy_factory():
                    return [scenario.fixed_battle(data, floor, number) for floor, number in enemy_spec['battles']]
                battle_setup = options
            else:
                zone = next(z for z in data.floors if z['name'] == enemy_spec['floor'])
                picks = CountingRandom(seed)

                def enemy_factory():
                    return [measures.random_group(data, zone, picks) for _ in range(int(enemy_spec['battles']))]
                battle_setup = dict(options, random_battle=True)
            result = scenario.play(data, setup, party_factory, enemy_factory, runs=1, seed=seed, battle_setup=battle_setup)[0]
            run = _result_dict(result)
            run['parts'] = [_result_dict(p) for p in result['parts']]
            run['_raw'] = result
            runs.append(run)
    finally:
        EXTRA.clear()
        EXTRA_ENCHANTS.clear()
        setup.composition = saved_comp
        setup.settings['kit_count'] = saved_kit
        setup.kit = saved_bag
    summary = measures.summary([r['_raw'] for r in runs])
    for r in runs:
        del r['_raw']
    lines = TRACER.lines
    TRACER.reset(0)
    return {'id': job['id'], 'runs': runs, 'summary': summary}, lines
