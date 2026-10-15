"""
Writes the golden file of PyMath.RoundTo: round(x, n) of Python for many floats (ties, near-ties, small, large, random).

    python engine_cs/parity/round_golden.py [path]        default: build/engine_round_golden.json
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))


def cases():
    rnd = random.Random(1234)
    out = []
    ties = [0.125, 0.375, 0.625, 0.875, 2.675, 1.005, 0.5, 1.5, 2.5, 0.015625, 0.045, 0.055, 1.115, 1.125, 3.14159, 0.005, 0.015, 0.025]
    for x in ties:
        for n in (0, 1, 2, 3):
            out.append((x, n))
            out.append((-x, n))
    for _ in range(4000):
        kind = rnd.choice(['unit', 'wide', 'eighth', 'tiny', 'share', 'big'])
        if kind == 'unit':
            x = rnd.random()
        elif kind == 'wide':
            x = rnd.uniform(-1000, 1000)
        elif kind == 'eighth':
            x = rnd.randint(-4000, 4000) / 8
        elif kind == 'tiny':
            x = rnd.uniform(0, 1) * 10 ** rnd.randint(-12, -1)
        elif kind == 'share':
            x = sum(rnd.random() / 7 for _ in range(rnd.randint(1, 40)))
        else:
            x = rnd.uniform(0, 1) * 10 ** rnd.randint(2, 15)
        out.append((x, rnd.choice([0, 1, 2, 2, 2, 3, 4])))
    out += [(0.0, 2), (-0.0, 2), (-0.001, 2), (5e-324, 2), (1.7976931348623157e308, 2), (123456789.987654321, 2)]
    return out


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT, 'build', 'engine_round_golden.json')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    rows = [[x, n, round(x, n)] for x, n in cases()]
    with open(target, 'w', encoding='utf-8') as f:
        json.dump(rows, f)
    print(target, len(rows), 'cases')


if __name__ == '__main__':
    main()
