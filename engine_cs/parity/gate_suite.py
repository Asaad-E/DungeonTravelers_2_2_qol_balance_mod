"""
The gate of `dtcli suite`: the suite is run (the snapshot is exported first) and everything it wrote under docs/generated/ and measures/ is compared
with the files of the last commit, which are what the Python paths of the measures wrote on the same data: no difference may be left, line ends aside.

    python engine_cs/parity/gate_suite.py            exports, runs `dtcli suite`, then `git diff --ignore-cr-at-eol` of docs/generated and measures

Run it on a tree whose data, model and measures are the ones of the last commit (otherwise a difference may come from them, not from the port).
"""
import os
import subprocess
import sys
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, 'tools'))


def main():
    import engine_client
    import engine_export
    engine_export.write(engine_client.SNAPSHOT)
    dll = engine_client.ensure_built()
    began = time.time()
    run = subprocess.run(['dotnet', dll, 'suite', '--snapshot', engine_client.SNAPSHOT, '--root', PROJECT], cwd=PROJECT, capture_output=True, text=True)
    print(run.stdout.strip())
    if run.returncode:
        print(run.stderr.strip())
        return 1
    print(f'suite: {time.time() - began:.0f} s')
    diff = subprocess.run(['git', 'diff', '--ignore-cr-at-eol', '--stat', '--', 'docs/generated', 'measures'], cwd=PROJECT, capture_output=True, text=True)
    print(diff.stdout.strip() or 'no difference from the last commit in docs/generated and measures')
    return 1 if diff.stdout.strip() else 0


if __name__ == '__main__':
    sys.exit(main())
