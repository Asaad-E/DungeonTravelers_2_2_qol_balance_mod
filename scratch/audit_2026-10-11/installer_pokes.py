"""One-off edit (2026-10-13) of installer/mod_patch.ps1: the values a variant writes in place into the packs of the
dungeons (lines "poke" of its list, tools/floor_patch.py). Run once; kept as the record of the edit.
"""
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'installer', 'mod_patch.ps1')
B = chr(92)
EDITS = [
("""$stateFile = Join-Path $modDir 'installed.txt'
""", """$stateFile = Join-Path $modDir 'installed.txt'
$pokeFile = Join-Path $modDir 'pokes.txt'
"""),
("""# Nothing is written unless every file is the one this mod was made for (each is checked by its SHA-256), and
""", """# The packs of the dungeons are large, so a variant changes a few bytes of them in place (lines "poke" of its list):
# no copy is kept, the list of what was written is (pokes.txt beside this script), and the value of the game goes back
# wherever the file still holds the one the mod wrote.
#
# Nothing is written unless every file is the one this mod was made for (each is checked by its SHA-256), and
"""),
("""function Stop-With([string[]]$lines) {""", """function Holds-At([string]$path, [int]$offset, [byte[]]$bytes) {
    $stream = [System.IO.File]::OpenRead($path)
    try {
        if ($offset + $bytes.Length -gt $stream.Length) { return $false }
        $held = New-Object byte[] $bytes.Length
        $stream.Position = $offset
        [void]$stream.Read($held, 0, $held.Length)
        for ($i = 0; $i -lt $bytes.Length; $i++) { if ($held[$i] -ne $bytes[$i]) { return $false } }
        return $true
    } finally { $stream.Dispose() }
}

function Put-At([string]$path, [int]$offset, [byte[]]$bytes) {
    $stream = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite)
    try { $stream.Position = $offset; $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

function Read-Pokes([string]$path) {
    # the lines "poke|file|offset|old|new" of a list
    $list = @()
    if (Test-Path $path) {
        foreach ($line in [System.IO.File]::ReadAllLines($path)) {
            $p = $line.Split('|')
            if ($p[0] -eq 'poke') {
                $list += ,@{ Rel = $p[1]; Offset = [Convert]::ToInt32($p[2], 16); Old = (To-Bytes $p[3]); New = (To-Bytes $p[4]); Line = $line }
            }
        }
    }
    return ,$list
}

function Undo-Pokes([object[]]$list) {
    # the value of the game goes back wherever the file still holds the one the mod wrote
    $count = 0
    foreach ($k in $list) {
        $path = Join-Path $root $k.Rel
        if ((Test-Path $path) -and (Holds-At $path $k.Offset $k.New)) { Put-At $path $k.Offset $k.Old; $count++ }
    }
    return $count
}

function Stop-With([string[]]$lines) {"""),
("""    $kept = Backup-Files
    if ($kept.Count -eq 0) { Write-Host 'No backup here: the mod is not installed.'; exit 0 }
""", """    $kept = Backup-Files
    $written = Read-Pokes $pokeFile
    if ($kept.Count -eq 0 -and $written.Count -eq 0) { Write-Host 'No backup here: the mod is not installed.'; exit 0 }
"""),
("""        foreach ($rel in $kept) { Copy-Item -Path (Join-Path $backup $rel) -Destination (Join-Path $root $rel) -Force }
    } catch {""", """        foreach ($rel in $kept) { Copy-Item -Path (Join-Path $backup $rel) -Destination (Join-Path $root $rel) -Force }
        [void](Undo-Pokes $written)
        if (Test-Path $pokeFile) { Remove-Item -Path $pokeFile -Force }
    } catch {"""),
("""    Remove-Item -Path $backup -Recurse -Force
""", """    if (Test-Path $backup) { Remove-Item -Path $backup -Recurse -Force }
"""),
("""if ($stale) { $problems += $updated }
if ($problems.Count -gt 0) { Stop-With $problems }
""", """# the values written in place: each place must hold the value of the game or the one this variant writes
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
if ($stale) { $problems += $updated }
if ($problems.Count -gt 0) { Stop-With $problems }
"""),
("""    [System.IO.File]::WriteAllLines($stateFile, [string[]]@($writes | ForEach-Object { "$($_.Rel)|$(Get-Sha $_.Bytes)" }))
""", """    [System.IO.File]::WriteAllLines($stateFile, [string[]]@($writes | ForEach-Object { "$($_.Rel)|$(Get-Sha $_.Bytes)" }))
    [void](Undo-Pokes (Read-Pokes $pokeFile))             # what another variant wrote in place goes back first
    foreach ($k in $pokes) { Put-At (Join-Path $root $k.Rel) $k.Offset $k.New }
    if ($pokes.Count -gt 0) { [System.IO.File]::WriteAllLines($pokeFile, [string[]]@($pokes | ForEach-Object { $_.Line })) }
    elseif (Test-Path $pokeFile) { Remove-Item -Path $pokeFile -Force }
"""),
("""if ($back -gt 0) { Write-Host "$back file(s) of another variant put back as the original." }
""", """if ($pokes.Count -gt 0) { Write-Host "$($pokes.Count) value(s) changed in the files of the dungeons." }
if ($back -gt 0) { Write-Host "$back file(s) of another variant put back as the original." }
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
