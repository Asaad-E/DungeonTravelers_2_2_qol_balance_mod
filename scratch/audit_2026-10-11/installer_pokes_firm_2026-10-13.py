"""One-off edit (2026-10-13) of installer/mod_patch.ps1, after the audit of that day: what was written in place into
the packs of the dungeons is known from pokes.txt and from the list of every variant unpacked beside the script, so a
lost pokes.txt or an update of the mod with other values no longer leaves a value behind or stops the install; the
record is written before the places are; the packs are tested for being in use; and a copy of an original is written
under another name and moved, so a crash cannot leave half a copy. Run once; kept as the record of the edit.
"""
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'installer', 'mod_patch.ps1')
EDITS = [
("""function Undo-Pokes([object[]]$list) {""", """function Known-Pokes {
    # every value this mod may have written in place: the record of the last install, and the lists of the variants
    # unpacked beside this script (an older record may be lost, or made by another version of the same variant)
    $list = @()
    foreach ($file in @(Get-ChildItem -Path $modDir -Filter *.txt -File)) { $list += (Read-Pokes $file.FullName) }
    return ,$list
}

function Undo-Pokes([object[]]$list) {"""),
("""    $kept = Backup-Files
    $written = Read-Pokes $pokeFile
""", """    $kept = Backup-Files
    $written = Known-Pokes
"""),
("""# the values written in place: each place must hold the value of the game or the one this variant writes
$pokes = Read-Pokes $manifest
$odd = @{}
foreach ($k in $pokes) {
    if ($odd.ContainsKey($k.Rel)) { continue }
    $path = Join-Path $root $k.Rel
    if (-not (Test-Path $path)) { $odd[$k.Rel] = 'not found in the game' }
    elseif (-not ((Holds-At $path $k.Offset $k.Old) -or (Holds-At $path $k.Offset $k.New))) {
        $odd[$k.Rel] = 'not the original file (another version of the game, or another mod is installed)'
    }
}
foreach ($rel in $odd.Keys) { $problems += "${rel}: $($odd[$rel])" }
""", """# the values written in place: each place must hold the value of the game, the one this variant writes, or one this
# mod is known to have written there before (another variant, or an older version of this one)
$pokes = Read-Pokes $manifest
$known = Known-Pokes
$before = @{}
foreach ($k in $known) {
    $key = "$($k.Rel.ToLower())|$($k.Offset)"
    if (-not $before.ContainsKey($key)) { $before[$key] = @() }
    $before[$key] += ,$k.New
}
$odd = @{}
foreach ($k in $pokes) {
    if ($odd.ContainsKey($k.Rel)) { continue }
    $path = Join-Path $root $k.Rel
    if (-not (Test-Path $path)) { $odd[$k.Rel] = 'not found in the game'; continue }
    $fine = (Holds-At $path $k.Offset $k.Old) -or (Holds-At $path $k.Offset $k.New)
    foreach ($value in @($before["$($k.Rel.ToLower())|$($k.Offset)"])) {
        if (-not $fine -and $null -ne $value -and (Holds-At $path $k.Offset $value)) { $fine = $true }
    }
    if (-not $fine) { $odd[$k.Rel] = 'not the original file (another version of the game, or another mod is installed)' }
}
foreach ($rel in $odd.Keys) { $problems += "${rel}: $($odd[$rel])" }
"""),
("""foreach ($w in $writes) {
    try { [System.IO.File]::Open((Join-Path $root $w.Rel), [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None).Dispose() }
    catch { $problems += "$($w.Rel): in use. Close the game and run this again." }
}
""", """$touched = @($writes | ForEach-Object { $_.Rel }) + @($pokes | ForEach-Object { $_.Rel } | Sort-Object -Unique)
foreach ($rel in $touched) {
    if (-not (Test-Path (Join-Path $root $rel))) { continue }
    try { [System.IO.File]::Open((Join-Path $root $rel), [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None).Dispose() }
    catch { $problems += "${rel}: in use. Close the game and run this again." }
}
"""),
("""        if ($null -ne $w.Source) { Write-File (Join-Path $backup $w.Rel) $w.Source }
        Write-File ((Join-Path $root $w.Rel) + $staged) $w.Bytes
    }
""", """        if ($null -ne $w.Source) {                    # the copy too goes under another name first: never half a copy
            $copy = Join-Path $backup $w.Rel
            Write-File ($copy + $staged) $w.Source
            Move-Item -LiteralPath ($copy + $staged) -Destination $copy -Force
        }
        Write-File ((Join-Path $root $w.Rel) + $staged) $w.Bytes
    }
"""),
("""    [void](Undo-Pokes (Read-Pokes $pokeFile))             # what another variant wrote in place goes back first
    foreach ($k in $pokes) { Put-At (Join-Path $root $k.Rel) $k.Offset $k.New }
    if ($pokes.Count -gt 0) { [System.IO.File]::WriteAllLines($pokeFile, [string[]]@($pokes | ForEach-Object { $_.Line })) }
    elseif (Test-Path $pokeFile) { Remove-Item -Path $pokeFile -Force }
""", """    # the record first: what was known and what is about to be written, so a stop half way leaves nothing unrecorded
    $record = @($known | ForEach-Object { $_.Line }) + @($pokes | ForEach-Object { $_.Line }) | Sort-Object -Unique
    if ($record.Count -gt 0) { [System.IO.File]::WriteAllLines($pokeFile, [string[]]$record) }
    [void](Undo-Pokes $known)                             # what this mod wrote in place before goes back first
    foreach ($k in $pokes) { Put-At (Join-Path $root $k.Rel) $k.Offset $k.New }
    if ($pokes.Count -gt 0) { [System.IO.File]::WriteAllLines($pokeFile, [string[]]@($pokes | ForEach-Object { $_.Line })) }
    elseif (Test-Path $pokeFile) { Remove-Item -Path $pokeFile -Force }
"""),
]


def main():
    with open(PATH, encoding='utf-8') as f:
        text = f.read()
    for old, new in EDITS:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(len(EDITS), 'edits')


if __name__ == '__main__':
    main()
