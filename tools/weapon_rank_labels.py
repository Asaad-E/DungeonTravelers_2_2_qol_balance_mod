"""
Weapon speed rank labels that carry their own delay multiplier.

The equipment title bar shows the rank name of the item ("Speed E+"). This tool writes the
delay multiplier stored in the same entry into that name ("Speed E+ (2.45x)"), so the figure
on screen is always the one the game uses: change the multiplier and the label follows.

    python tools/weapon_rank_labels.py SOURCE.pck DEST.pck

Only the names change; the multipliers are copied untouched. Running it on an already
labelled file gives the same file.
"""
import re
import sys
from pck_handler import PckArchive, WeaponRankHelper

LABEL = '{rank} ({delay:.2f}x)'
LABEL_RE = re.compile(r'^(?P<rank>[A-Z]\+?) \((?P<delay>\d+\.\d\d)x\)$')
TOLERANCE = 1e-4


def bare_rank(name):
    """'E+ (2.45x)' -> 'E+'."""
    return name.split(' (')[0]


def relabel(archive):
    """Rewrites every rank name from the multiplier of its own entry. Returns (old, new) pairs."""
    changes = []
    for i, (fn, b) in enumerate(archive.files):
        rank = WeaponRankHelper.read_rank(b)
        label = LABEL.format(rank=bare_rank(rank['name']), delay=rank['delay'])
        archive.files[i] = (fn, WeaponRankHelper.write_rank(b, label))
        changes.append((rank['name'], label))
    return changes


def check(archive):
    """Every label must show the multiplier stored next to it."""
    problems = []
    for fn, b in archive.files:
        rank = WeaponRankHelper.read_rank(b)
        m = LABEL_RE.match(rank['name'])
        if not m:
            problems.append(f"{fn}: rank name '{rank['name']}' carries no multiplier")
        elif abs(float(m.group('delay')) - rank['delay']) > TOLERANCE:
            problems.append(f"{fn}: label '{rank['name']}' but the stored multiplier is {rank['delay']:.4f}")
    return problems


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    archive = PckArchive(sys.argv[1])
    changes = relabel(archive)
    problems = check(archive)
    if problems:
        print('\n'.join(problems))
        return 1
    archive.save(sys.argv[2])
    for old, new in changes:
        print(f"    {old:12s} -> {new}")
    print(f"Wrote {sys.argv[2]}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
