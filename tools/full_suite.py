"""
Every measure of the project played on the C# engine (engine_cs/), then the reports, the generated checklists and the tests: the
whole of docs/generated/ and of the figures of measures/ written again from the current data and model.

    python tools/full_suite.py            the whole suite, with the time of each step and the total
    python tools/full_suite.py --list     the steps, without running them

Each step is a command of a tool that also runs alone (`python tools/class_stages.py engine`, `python measures/unique_skills.py
engine`, ...): those commands play their battles in one process with one engine, or split their cells in parts that run at once.
The Python paths of the tools (`all`, `run`) are not used here and stay as they were.
"""
import os
import subprocess
import sys
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STEPS = [
    ['tools/engine_export.py'],
    ['tools/difficulty_curve.py', 'engine'], ['tools/difficulty_curve.py', 'report'],
    ['tools/party_battery.py', 'engine'], ['tools/party_battery.py', 'report'],
    ['tools/class_stages.py', 'engine'], ['tools/class_stages.py', 'report'],
    ['tools/skill_value.py', 'engine'], ['tools/skill_value.py', 'report'],
    ['tools/skill_value.py', 'engine-ailments'], ['tools/skill_value.py', 'ailments_report'],
    ['tools/boss_fit.py', 'gentle-engine'], ['tools/boss_fit.py', 'gentle-report'],
    ['tools/skill_worth.py', 'engine'], ['tools/skill_worth.py', 'report'],
    ['tools/guide_curve.py', 'engine'], ['tools/guide_curve.py', 'report'],
    ['tools/sim_anchors.py', 'engine'],
    ['tools/sim_audit.py', 'passives-engine'], ['tools/sim_audit.py', 'usage-engine'], ['tools/sim_audit.py', 'actives-engine'],
    ['tools/sim_audit.py', 'report'],
    ['measures/win_rates.py', 'engine'], ['measures/win_rates.py', 'report'],
    ['measures/mercenaries.py', 'engine'], ['measures/mercenaries.py', 'report'],
    ['measures/party_skills.py', 'engine'], ['measures/party_skills.py', 'report'],
    ['measures/postgame_compare.py', 'engine'], ['measures/postgame_compare.py', 'report'],
    ['measures/unique_skills.py', 'engine'], ['measures/unique_skills.py', 'report'],
    ['measures/skill_value_contested.py', 'engine'], ['measures/skill_value_contested.py', 'report'],
    ['measures/random_battles.py', 'engine'], ['measures/random_battles.py', 'report'],
    ['measures/regression_r04.py', 'witnesses'], ['measures/regression_r04.py', 'play', '1/1', '--engine'],
    ['measures/regression_r04.py', 'report'],
    ['measures/boss_rows_check.py', '--engine'], ['measures/design_rows.py', '--engine'],
    ['measures/support_chains.py', '--engine'], ['measures/support_stages.py', '--engine'],
    ['tools/balance_baseline.py'], ['tools/checkpoint_levels.py'], ['tools/sim_coverage.py'], ['tools/verdicts.py'],
    ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'],
]


def main(args):
    if '--list' in args:
        for step in STEPS:
            print('python', ' '.join(step))
        return 0
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    started, failed = time.time(), []
    for step in STEPS:
        began = time.time()
        run = subprocess.run([sys.executable, *step], cwd=PROJECT, env=env, capture_output=True, text=True, encoding='utf-8',
                             errors='replace')
        tail = [line for line in (run.stdout + run.stderr).strip().splitlines() if line.strip()][-1:] or ['']
        mark = '' if run.returncode == 0 else '  FAILED'
        print(f'{time.time() - began:6.0f} s  python {" ".join(step)}{mark}\n          {tail[0][:150]}', flush=True)
        if run.returncode:
            failed.append(' '.join(step))
    print(f'total {time.time() - started:.0f} s; {len(STEPS) - len(failed)} of {len(STEPS)} steps passed'
          + (f'; failed: {"; ".join(failed)}' if failed else ''))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))
