"""Second part of the one-off edit of 2026-10-12: the test of the program patch works on whatever program files the
machine has; the example of the configuration file."""
import io
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = chr(10)
path = os.path.join(PROJECT, 'tests', 'test_balance_ground_truth.py')
s = io.open(path, encoding='utf-8').read()
a = s.index("            vanilla = {'game file': exe_patch.VANILLA_COPY")
b = s.index("            rows = exe_patch.patches('balance')", a)
new = ("            vanilla, targets = {}, []" + NL +
       "            for label, game_file, copy in exe_patch.find_targets():" + NL +
       "                vanilla[label] = copy if os.path.exists(copy) else game_file" + NL +
       "                shutil.copy2(vanilla[label], os.path.join(folder, label))" + NL +
       "                targets.append((label, os.path.join(folder, label), os.path.join(folder, 'kept', label + '.vanilla.exe')))" + NL +
       "            first = targets[0][0]" + NL)
s = s[:a] + new + s[b:]
for old, fresh in (
        ("self.assertEqual([d[2] for d in done], [19, 19])", "self.assertEqual([d[2] for d in done], [19] * len(targets))"),
        ("self.assertEqual(set(exe_patch.installed_set(targets)['game file'].values()), {'patched'})",
         "self.assertEqual(set(exe_patch.installed_set(targets)[first].values()), {'patched'})"),
        ("self.assertEqual(exe_patch.restore(targets), ['game file', 'unwrapped file'])",
         "self.assertEqual(exe_patch.restore(targets), [label for label, _, _ in targets])"),
        ("with open(targets[1][1], 'r+b') as f:", "with open(targets[-1][1], 'r+b') as f:"),
        ("self.assertEqual(exe_patch.sha(targets[0][1]), exe_patch.sha(vanilla['game file']))",
         "self.assertEqual(exe_patch.sha(targets[0][1]), exe_patch.sha(vanilla[first]))")):
    assert s.count(old) == 1, old
    s = s.replace(old, fresh)
io.open(path, 'w', encoding='utf-8', newline=NL).write(s)
example = '''{
  "game_dir": "D:/Games/DungeonTravelers2-2_EN",
  "program_files": [],
  "formula_exe": "",
  "save_dir": ""
}
'''
io.open(os.path.join(PROJECT, 'config.example.json'), 'w', encoding='utf-8', newline=NL).write(example)
print('applied')
