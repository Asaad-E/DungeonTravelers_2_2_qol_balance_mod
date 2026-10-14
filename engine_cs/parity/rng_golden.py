"""
Writes the golden file of the random generator test: for many seeds a long list of calls (random, getrandbits,
randrange, randint, choice, sample, choices) run on random.Random with their results, to be replayed by the C# generator.

    python engine_cs/parity/rng_golden.py [path]        default: build/engine_rng_golden.json
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from pyrng import CountingRandom, fmt_num  # noqa: E402

SEEDS = [0, 1, 2, 3, 7, 42, 255, 256, 1000, 20261005, 20261005 + 1, 20261005 + 39, 2 ** 31 - 1, 2 ** 31, 2 ** 32 - 1, 2 ** 32,
         2 ** 32 + 5, 2 ** 40 + 7, 2 ** 52 + 11, 123456789012345]


def make_ops(rnd, count):
    ops = []
    for _ in range(count):
        kind = rnd.choice(['random', 'bits', 'range', 'range', 'int', 'choice', 'choice', 'sample', 'choices'])
        if kind == 'random':
            ops.append(['random'])
        elif kind == 'bits':
            ops.append(['bits', rnd.randint(1, 32)])
        elif kind == 'range':
            ops.append(['range', rnd.choice([1, 2, 3, 5, 6, 12, 20, 93, 100, 500, 1000, 65535, 65536, 2 ** 20, 2 ** 31 - 1, rnd.randint(1, 10 ** 6)])])
        elif kind == 'int':
            a = rnd.randint(-5, 20)
            ops.append(['int', a, a + rnd.randint(0, 40)])
        elif kind == 'choice':
            ops.append(['choice', rnd.randint(1, 30)])
        elif kind == 'sample':
            n = rnd.randint(1, 21)
            ops.append(['sample', n, rnd.randint(0, n)])
        else:
            n = rnd.randint(1, 8)
            ops.append(['choices', [rnd.randint(1, 60) for _ in range(n)]])
    return ops


def run(seed, ops):
    r = CountingRandom(seed)
    out = []
    for op in ops:
        kind = op[0]
        if kind == 'random':
            out.append(fmt_num(r.random()))
        elif kind == 'bits':
            out.append(str(r.getrandbits(op[1])))
        elif kind == 'range':
            out.append(str(r.randrange(op[1])))
        elif kind == 'int':
            out.append(str(r.randint(op[1], op[2])))
        elif kind == 'choice':
            out.append(str(r.choice(list(range(op[1])))))
        elif kind == 'sample':
            out.append(','.join(str(x) for x in r.sample(list(range(op[1])), op[2])))
        else:
            weights = op[1]
            out.append(str(r.choices(list(range(len(weights))), weights=weights)[0]))
    return out, r.words


def main(path):
    rnd = random.Random(2026)
    cases = []
    for seed in SEEDS:
        ops = make_ops(rnd, 3000)
        out, words = run(seed, ops)
        cases.append({'seed': seed, 'ops': ops, 'out': out, 'words': words})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cases, f, separators=(',', ':'))
    print(path, len(cases), 'seeds,', sum(len(c['ops']) for c in cases), 'calls')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT, 'build', 'engine_rng_golden.json'))
