"""One-off edit (2026-10-13): the player installer writes every new file beside its place first and moves them in
at the end, after checking that none is held open, so that a failure half way leaves the game as it was; and four
decisions of that day are written on their rows of balance_changes.xlsx. Run once; kept as the record of the edit.
"""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, 'installer', 'mod_patch.ps1')
CHANGES = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
EDITS = [
("""if ($stale) { $problems += $updated }
if ($problems.Count -gt 0) { Stop-With $problems }
""", """if ($stale) { $problems += $updated }
# a file the game holds open cannot be replaced: found now, before anything is written
foreach ($w in $writes) {
    try { [System.IO.File]::Open((Join-Path $root $w.Rel), [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None).Dispose() }
    catch { $problems += "$($w.Rel): in use. Close the game and run this again." }
}
if ($problems.Count -gt 0) { Stop-With $problems }
"""),
("""# 3. write: the copy of the original first, then the file. What another variant changed and this one does not goes back.
try {
    foreach ($w in $writes) {
        if ($null -ne $w.Source) { Write-File (Join-Path $backup $w.Rel) $w.Source }
        Write-File (Join-Path $root $w.Rel) $w.Bytes
    }
""", """# 3. write. First the copy of every original and every new file beside its place, under another name; only when all
# of them are on the disk is each moved into its place, so a failure before that leaves the game as it was. What
# another variant changed and this one does not goes back.
$staged = '.dt22new'
try {
    foreach ($w in $writes) {
        if ($null -ne $w.Source) { Write-File (Join-Path $backup $w.Rel) $w.Source }
        Write-File ((Join-Path $root $w.Rel) + $staged) $w.Bytes
    }
    foreach ($w in $writes) {
        $target = Join-Path $root $w.Rel
        Move-Item -LiteralPath ($target + $staged) -Destination $target -Force
    }
"""),
("""} catch {
    Write-Host "A file could not be written: $($_.Exception.Message)"
    Write-Host 'Close the game and run this again. To put everything back, run the Uninstall .bat.'
    exit 1
}""", """} catch {
    foreach ($w in $writes) {
        $left = (Join-Path $root $w.Rel) + $staged
        if (Test-Path -LiteralPath $left) { Remove-Item -LiteralPath $left -Force }
    }
    Write-Host "A file could not be written: $($_.Exception.Message)"
    Write-Host 'Close the game and run this again. To put everything back, run the Uninstall .bat.'
    exit 1
}"""),
]
NOTES = {
    'W042': ' | 2026-10-13 : kept. The DLC of the game gives the same doubling, and it cuts the grind',
    'P090': ' | 2026-10-13 : kept: one piece, given once',
}
HEAL = (' | 2026-10-13 : kept beyond the quarter the other costs keep to: a spell of healing has to be chanted and an item '
        'is used at once by anyone, and the lower cost makes up for it')


def main():
    with open(SCRIPT, encoding='utf-8') as f:
        text = f.read()
    for old, new in EDITS:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    with open(SCRIPT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    wb = openpyxl.load_workbook(CHANGES)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    col = {k: head.index(k) for k in ('ID', 'Record', 'Field', 'Why', 'State', 'Vanilla', 'New')}
    done = 0
    for row in ws.iter_rows(min_row=2):
        rid = row[col['ID']].value
        if rid in NOTES:
            row[col['Why']].value = str(row[col['Why']].value) + NOTES[rid]
            done += 1
        elif row[col['State']].value == 'built' and str(row[col['Record']].value).endswith(' Heal') \
                and row[col['Field']].value == 'TP cost' and row[col['Vanilla']].value == 3 and row[col['New']].value == 2:
            row[col['Why']].value = str(row[col['Why']].value) + HEAL
            done += 1
    assert done == 3, done
    wb.save(CHANGES)
    print('installer staged,', done, 'rows noted')


if __name__ == '__main__':
    main()
