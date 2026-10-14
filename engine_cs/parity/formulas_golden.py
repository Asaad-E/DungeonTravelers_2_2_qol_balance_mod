"""
Writes the golden file of the formulas test: sim/formulas.py (and the built-in sum()) called on random inputs, with the
results as text (the shared number format), to be replayed by the C# functions.

    python engine_cs/parity/formulas_golden.py [path]      default: build/engine_formulas_golden.json
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, HERE)
from pyrng import fmt_num  # noqa: E402
from sim import formulas as f  # noqa: E402
from sim import progression  # noqa: E402


def cases(rnd, n):
    out = []

    def add(fn, args, value):
        out.append({'fn': fn, 'args': args, 'out': fmt_num(value)})

    for _ in range(n):
        stat, weight, level = rnd.randint(0, 400), rnd.choice([1.0, 1.2, 1.3, 2.15, 2.9]) + rnd.random() * 0.01, rnd.randint(1, 99)
        factor = rnd.choice([1.0, 1.5, 2.25, 0.85, rnd.uniform(0.5, 3)])
        bonus = rnd.choice([0.0, rnd.uniform(-0.5, 1.5)])
        slowed, defending, escaping = rnd.random() < 0.2, rnd.random() < 0.2, rnd.random() < 0.1
        rand = rnd.choice(f.SPEED_RANDOM)
        add('turn_value', [stat, weight, level, factor, bonus, slowed, defending, escaping, rand],
            f.turn_value(stat, weight, level, factor, bonus, slowed, defending, escaping, rand))

        up, mini, down = rnd.randint(0, 6), rnd.randint(0, 6), rnd.randint(0, 6)
        add('speed_enchant_bonus', [up, mini, down, 0.10, 0.05, 0.10], f.speed_enchant_bonus(up, mini, down))
        add('speed_enchant_bonus', [up, mini, down, 0.20, 0.10, 0.20], f.speed_enchant_bonus(up, mini, down, 0.20, 0.10, 0.20))

        dex, agi = rnd.randint(0, 500), rnd.randint(0, 500)
        acc, buffs, tb = rnd.choice([0.0, rnd.uniform(-0.3, 0.5)]), rnd.choice([0.0, rnd.uniform(0, 0.6)]), rnd.choice([0.0, rnd.uniform(0, 0.6)])
        en, ten = rnd.randint(0, 50), rnd.randint(0, 50)
        div = 1.0 + rnd.choice([0.0, rnd.uniform(0, 0.5)])
        add('physical_hit', [dex, agi, acc, buffs, tb, en, ten, div], f.physical_hit(dex, agi, acc, buffs, tb, en, ten, div))

        atk, dfn = rnd.randint(0, 900), rnd.randint(0, 900)
        mods, tmods = rnd.choice([0.0, rnd.uniform(-0.5, 2)]), rnd.choice([0.0, rnd.uniform(-0.5, 1.5)])
        aen, den = rnd.randint(0, 50), rnd.randint(0, 50)
        swing = rnd.choice([0.0, rnd.randint(-15, 15) / 100.0])
        times = rnd.choice([1.0, 1.5, 2.0])
        ignore = rnd.random() < 0.1
        rf = rnd.choice([1.0, 0.75, 0.5])
        cut = rnd.choice([1.0, 0.9, 0.5, 0.8])
        race = rnd.choice([1.0, 1.3, 0.85])
        res = rnd.choice([0, 10, 50, -20, 100])
        defending = rnd.random() < 0.2
        crit = rnd.choice([1.0, 1.25])
        other = rnd.choice([0.0, rnd.uniform(-0.3, 0.8)])
        add('physical_damage', [atk, dfn, mods, tmods, aen, den, swing, times, ignore, rf, cut, race, res, defending, crit, other],
            f.physical_damage(atk, dfn, mods, tmods, aen, den, swing, times, ignore, rf, cut, race, res, 1.0, defending, crit, other))

        sa, intel, tres = rnd.uniform(0.5, 1.0), rnd.randint(0, 600), rnd.randint(0, 600)
        loose, men, mten = rnd.choice([0.0, rnd.uniform(0, 0.2)]), rnd.randint(0, 50), rnd.randint(0, 50)
        mb, ev = rnd.choice([0.0, rnd.uniform(0, 0.5)]), rnd.choice([0.0, rnd.uniform(0, 0.5)])
        mdiv = rnd.choice([1.0, 1.3, 0.8])
        add('magic_hit', [sa, intel, tres, loose, men, mten, mb, ev, mdiv], f.magic_hit(sa, intel, tres, loose, men, mten, mb, ev, mdiv))

        power = rnd.randint(0, 900)
        mastery, mm = rnd.choice([0.0, rnd.uniform(0, 0.3)]), rnd.choice([0.0, rnd.uniform(0, 1.0)])
        sec, eb = rnd.choice([0.0, rnd.uniform(0, 0.5)]), rnd.choice([0.0, 0.2, 0.4, 0.6])
        tmod = rnd.choice([0.0, rnd.uniform(-0.2, 1.0)])
        pb, dcut = rnd.choice([0.0, rnd.uniform(0, 0.5)]), rnd.choice([0.0, -0.25, rnd.uniform(-0.25, 0.3)])
        mcrit = rnd.choice([1.0, 1.25])
        add('magic_damage', [intel, power, tres, mastery, mm, aen, sec, eb, tmod, den, swing, pb, dcut, res, mcrit, other],
            f.magic_damage(intel, power, tres, mastery, mm, aen, sec, eb, tmod, den, swing, pb, dcut, res, mcrit, other))

        dmg, mhp = rnd.randint(1, 3000), rnd.randint(50, 3000)
        mod, enc = rnd.choice([0.0, rnd.uniform(0, 0.5)]), rnd.choice([0.0, 0.1, 0.16, 0.25])
        crit_b, phys, prod = rnd.random() < 0.3, rnd.random() < 0.8, rnd.random() < 0.5
        add('interruption_chance', [dmg, mhp, mod, enc, crit_b, phys, prod], f.interruption_chance(dmg, mhp, mod, enc, crit_b, phys, prod))

        cu, cm = rnd.randint(0, 8), rnd.randint(0, 8)
        add('critical_enchant', [cu, cm], f.critical_enchant(cu, cm))
        lvl, tl = rnd.randint(1, 99), rnd.randint(1, 99)
        skill = rnd.choice([0.0, rnd.uniform(0, 30)])
        ce, cte = rnd.choice([0.0, rnd.uniform(0, 60)]), rnd.choice([0.0, -rnd.uniform(0, 60)])
        eh = rnd.choice([0, 0, 1, 3])
        f268 = rnd.random() < 0.2
        fixed = rnd.choice([None, None, None, 0.0, 0.3, 1.0])
        add('critical_rate', [dex, agi, lvl, tl, skill, ce, cte, eh, f268, fixed is not None, fixed or 0.0],
            f.critical_rate(dex, agi, lvl, tl, skill, ce, cte, eh, f268, fixed))
        ecf = rnd.uniform(0, 60)
        add('expected_critical_factor', [ecf], f.expected_critical_factor(ecf))

        base = rnd.choice([0.1, 0.15, 0.25, 0.3, 0.5, 0.75, 0.8, 1.0, 10.0, rnd.uniform(0, 1)])
        resv = rnd.choice([0, 5, 10, 15, 25, 50, 100, -20, -35, 99, 101])
        add('ailment_chance', [base, resv], f.ailment_chance(base, resv))
        add('ailment_threshold', [base, resv], f.ailment_threshold(base, resv))

        share = rnd.choice([100, 50, 60, 40, 33, 34, 24, 28, 16, 14, 26])
        prov = rnd.choice([0.0, 250, 99.7])
        pu, pd = rnd.randint(0, 3), rnd.randint(0, 3)
        add('target_weight', [share, prov, pu, pd], f.target_weight(share, prov, pu, pd))

        e286 = rnd.choice([0.0, rnd.uniform(0, 0.2)])
        du, dm = rnd.randint(0, 4), rnd.randint(0, 4)
        add('doll_heal_bonus', [e286, du, dm], f.doll_heal_bonus(e286, du, dm))

        hres, coef = rnd.randint(0, 600), rnd.uniform(0.2, 12.0)
        hm = rnd.choice([0.0, rnd.uniform(0, 0.5)])
        cap = rnd.choice([None, None, rnd.randint(50, 900), rnd.uniform(50, 900)])
        capb = rnd.choice([0.0, rnd.uniform(0, 0.5)])
        hr = rnd.choice(f.HEAL_RANDOM)
        add('heal', [hres, coef, hm, cap is not None, cap or 0.0, capb, hr], f.heal(hres, coef, hm, cap, capb, hr))

        mx, val = rnd.randint(50, 5000), rnd.uniform(0.05, 1.0)
        capf = rnd.choice([None, rnd.randint(10, 800)])
        add('fraction_recovery', [mx, val, capf is not None, capf or 0], f.fraction_recovery(mx, val, capf))

        v = rnd.uniform(0, 1.0e6)
        add('single', [v], f.single(v))

        frac, full = rnd.choice([0.0, 0.05, 0.3, 0.65]), rnd.random() < 0.2
        add('after_battle_recovery', [mx, frac, full], progression.after_battle_recovery(mx, frac, full))
        vals = [round(rnd.uniform(0.01, 0.2), 2) for _ in range(rnd.randint(0, 4))]
        extras = [round(rnd.uniform(0.0, 0.1), 2) for _ in range(len(vals))]
        add('after_battle_fraction', [vals, extras], progression.after_battle_fraction(vals, extras))

        # the built-in sum() over floats and ints, the way the simulator adds its terms
        items = []
        for _ in range(rnd.randint(0, 9)):
            items.append(rnd.choice([0.0, 0.1, 0.15, 0.2, 0.3, 0.05, 0.01, round(rnd.uniform(-0.5, 1.5), 3), rnd.uniform(-1, 1), 1, 2, 0, -1]))
        add('pysum', [items, [isinstance(x, int) for x in items]], sum(items))
    return out


def main(path):
    rnd = random.Random(7)
    data = cases(rnd, 4000)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f_:
        json.dump(data, f_, separators=(',', ':'))
    print(path, len(data), 'cases')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT, 'build', 'engine_formulas_golden.json'))
