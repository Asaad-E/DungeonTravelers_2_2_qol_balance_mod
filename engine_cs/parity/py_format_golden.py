"""
Writes the golden file of the Python behaviours the reports of the measures of engine_cs/src/DtEngine/Suite depend on: the text of a float
(`%.nf`, `:.n%`, `:+.n%`, `:g`, repr), statistics.mean and statistics.median, json.dumps (plain and with indent=1) and the repr of a document.

    python engine_cs/parity/py_format_golden.py [path]        default: build/engine_pyformat_golden.json
"""
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))


def floats():
    rnd = random.Random(4321)
    out = [0.0, -0.0, 0.5, 1.5, 2.5, 0.125, 0.375, 0.625, 0.045, 0.055, 1.005, 2.675, 0.015, 0.025, 0.005, 1.0, 100.0, 1e15, 1e16, 1e17, 1.5e300,
           1e-4, 1e-5, 1.2345e-5, 5e-324, 0.1, 0.2, 0.3, 0.1 + 0.2, 1 / 3, 2 / 3, 0.95, 0.985, 0.995, 0.9949999999, -0.4, -0.5, -0.0049, 123456789.987654321]
    for _ in range(3000):
        kind = rnd.choice(['unit', 'wide', 'eighth', 'tiny', 'share', 'big', 'pct'])
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
        elif kind == 'pct':
            x = rnd.randint(0, 2000) / rnd.choice([8, 16, 40, 200, 1000, 2000])
        else:
            x = rnd.uniform(0, 1) * 10 ** rnd.randint(2, 20)
        out.append(x)
    return out


def texts(x):
    return [repr(x), '%.0f' % x, '%.1f' % x, '%.2f' % x, f'{x:.0%}', f'{x:.1%}', f'{x:+.0%}', f'{x:+.0f}', f'{x:g}']


def lists():
    rnd = random.Random(99)
    out = []
    for _ in range(300):
        n = rnd.randint(1, 12)
        out.append([rnd.choice([rnd.random(), rnd.randint(0, 40) / 8, rnd.uniform(-1, 1), rnd.random() * 10 ** rnd.randint(-5, 5)]) for _ in range(n)])
    return out


def documents():
    return [
        {'a': 1, 'b': [1.0, 2.5, None, True, False, 'text'], 'c': {}, 'd': [], 'e': {'x': [], 'y': {'z': 1e-05}}},
        [{'id': 'C03', 'won': 1.0, 'time': None, 'name': 'café テスト "quoted" back\\slash\ttab'}, 12, -3, 0.1, 1e16, 123456789012345.6],
        {'k': [[1, 2], [3, [4, {'m': [5.0]}]]]},
        [],
        {},
    ]


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT, 'build', 'engine_pyformat_golden.json')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    data = {
        'floats': [[x, texts(x)] for x in floats()],
        'means': [[xs, statistics.mean(xs), statistics.median(xs)] for xs in lists()],
        'documents': [[doc, json.dumps(doc), json.dumps(doc, indent=1), repr(doc)] for doc in documents()],
    }
    with open(target, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print(target, len(data['floats']), 'floats,', len(data['means']), 'lists,', len(data['documents']), 'documents')


if __name__ == '__main__':
    main()
