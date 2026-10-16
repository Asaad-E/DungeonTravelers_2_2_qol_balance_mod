"""
Plays each trial command of dtcli (the ports of the trial scripts of measures/) and the Python script it stands for (with --engine) on the same
arguments, and compares what they print and write.

    python engine_cs/parity/gate_trials.py [part of a command name]       e.g. magic-wall
    python engine_cs/parity/gate_trials.py mazurka

samba_trial and def_debuff_trial look for a rule of the Etoile (Dumbing Mazurka, status:201) that the sheet Policies no longer holds, so they
stop on the sheet as it is, in both paths. `mazurka` compares them on the sheet with that rule put back (the rule of Salsa turned into it, for the
script and for the snapshot alike). The extra sides of rows_trial and curve_ablation come from tools/engine_sides.py (`rows P038` and `ablation`);
curve_ablation also needs measures/balance_changes_at_dc1a09b.xlsx, which is not in the repository, so these two are compared by hand with it.
"""
import json
import os
import runpy
import subprocess
import sys
import tempfile
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DLL = os.path.join(PROJECT, 'engine_cs', 'src', 'DtEngine.Cli', 'bin', 'Release', 'net10.0', 'dtcli.dll')
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

# (script, dtcli command, arguments)
CASES = [
    ('measures/curve_recheck.py', 'curve-recheck', ['C15;C17', '20']),
    ('measures/etoile_dances.py', 'etoile-dances', ['C40', '8']),
    ('measures/magic_wall.py', 'magic-wall', []),
    ('measures/measure_open_rows.py', 'measure-open-rows', ['Roulette Circus']),
    ('measures/measure_open_rows.py', 'measure-open-rows', ['Bible Thump']),
    ('measures/measure_open_rows.py', 'measure-open-rows', ['Support Shot']),
    ('measures/etoile_trial.py', 'etoile-trial', ['C40', '8']),
    ('measures/etoile_trial.py', 'etoile-trial', ['C40', '8', 'primevil']),
    ('measures/dance_trial.py', 'dance-trial', ['C26;C30', '10']),
    ('measures/sage_buffs_trial.py', 'sage-buffs-trial', ['C30;C36', '6']),
    ('measures/provoke_trial.py', 'provoke-trial', ['C30', '8', '250,325,400,500,600']),
    ('measures/boss_trim_trial.py', 'boss-trim-trial', ['C30', '10', 'hp*1.15', 'atk=game,int=game', 'hp*1.15,atk=game,int=game']),
    ('measures/grand_sealbook_trial.py', 'grand-sealbook-trial', ['955', 'P24', '10']),
    ('measures/lize_ideas.py', 'lize-ideas', ['dolls', 'C18', '10']),
    ('measures/mercenary_trial.py', 'mercenary-trial', ['Marion', 'C40', '10', 'atk=1.5', 'dex=1.5']),
    ('measures/mercenary_trial.py', 'mercenary-trial', ['Natalia', 'C40', '10', 'without=diva']),
    ('measures/mercenary_trial.py', 'mercenary-trial', ['none', 'C40', '10', 'without=diva']),
    ('measures/one_skill_trial.py', 'one-skill-trial', ['mistress', 'Ecstasy', 'C26;C30', '10']),
    ('measures/one_skill_trial.py', 'one-skill-trial', ['tank', 'Parry', 'C26', '10']),
    ('measures/tp_items_trial.py', 'tp-items-trial', ['C30', '6']),
    ('measures/worth_with_weapon.py', 'worth-with-weapon', ['Bible Thump', 'sage', 'Tome']),
]
MAZURKA = [('measures/samba_trial.py', 'samba-trial', ['C40', '8']), ('measures/def_debuff_trial.py', 'def-debuff-trial', ['C30;C36', '8'])]


def lines(run):
    return run.stdout.replace('\r\n', '\n').strip().split('\n') if run.stdout.strip() else []


def first_difference(a, b):
    for k in range(max(len(a), len(b))):
        x, y = (a[k] if k < len(a) else '<end>'), (b[k] if k < len(b) else '<end>')
        if x != y:
            return f'   line {k + 1}\n     python: {x[:300]}\n     dtcli:  {y[:300]}'
    return ''


def written():
    folder = os.path.join(PROJECT, 'measures')
    return {n: open(os.path.join(folder, n), 'rb').read().replace(b'\r\n', b'\n') for n in os.listdir(folder) if n.startswith('open_rows_')}


def compare(script, command, args, extra=(), wrapper=None, snapshot=None):
    began = time.time()
    python = [sys.executable] + (wrapper if wrapper else [os.path.join(PROJECT, script)]) + args + ['--engine']
    py = subprocess.run(python, cwd=PROJECT, env=ENV, capture_output=True, text=True, encoding='utf-8')
    mid = time.time()
    before = written()
    cmd = ['dotnet', DLL, command, *args, *extra] + (['--snapshot', snapshot] if snapshot else [])
    cs = subprocess.run(cmd, cwd=PROJECT, env=ENV, capture_output=True, text=True, encoding='utf-8')
    a, b = lines(py), lines(cs)
    same = a == b and py.returncode == 0 and cs.returncode == 0 and all(written().get(n) == d for n, d in before.items())
    print(f'{"same" if same else "DIFFERENT"}  {command} {" ".join(args)}  (python {mid - began:.1f} s, dtcli {time.time() - mid:.1f} s; {len(a)} lines)', flush=True)
    if not same:
        print('   return codes', py.returncode, cs.returncode, (py.stderr or '')[-300:], (cs.stderr or '')[-300:])
        print(first_difference(a, b))
    return same


def with_rule():
    """The path of a snapshot whose sheet Policies holds the rule of the Etoile with status:201 (the rule of Salsa turned into it)."""
    snap = json.load(open(os.path.join(PROJECT, 'build', 'engine_snapshot.json'), encoding='utf-8'))
    for r in snap['setup']['policies']:
        if r['Role'] == 'etoile' and str(r['Action']) == 'status:199':
            r['Action'] = 'status:201'
    path = os.path.join(tempfile.mkdtemp(), 'snapshot_with_rule.json')
    json.dump(snap, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    return path


def run_script(script, rest):
    """The script with the same turn of the rule applied to the sheet it loads."""
    sys.path[:0] = [PROJECT, os.path.join(PROJECT, 'tools'), os.path.join(PROJECT, 'measures')]
    from sim import setup as setup_mod
    original = setup_mod.load

    def load(*a, **k):
        s = original(*a, **k)
        for r in s.policies:
            if r['Role'] == 'etoile' and str(r['Action']) == 'status:199':
                r['Action'] = 'status:201'
        return s
    setup_mod.load = load
    sys.argv = [script] + rest
    runpy.run_path(os.path.join(PROJECT, script), run_name='__main__')


def main(only=None):
    bad = 0
    if only == 'mazurka':
        snapshot = with_rule()
        for script, command, args in MAZURKA:
            bad += not compare(script, command, args, wrapper=[os.path.abspath(__file__), 'script', script], snapshot=snapshot)
    else:
        for script, command, args in CASES:
            if only is None or only in command:
                bad += not compare(script, command, args)
    print('differences:', bad)
    return 1 if bad else 0


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'script':
        run_script(sys.argv[2], sys.argv[3:])
        sys.exit(0)
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
