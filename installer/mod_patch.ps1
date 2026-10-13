# Dungeon Travelers 2-2 (PC, English) mod: applies a variant to your own copy of the game, or takes it out.
#
# This archive holds no file of the game: only the differences. Unpack it into the folder of the game (the one that
# holds the .exe and the folder Data) and run the Install .bat of the variant. Close the game first.
#
#   mod_patch.ps1 install <variant>    checks every file, keeps a copy of each in the folder backup beside this
#                                      script, then changes it
#   mod_patch.ps1 uninstall            puts every file back from that folder
#
# The packs of the dungeons are large, so a variant changes a few bytes of them in place (lines "poke" of its list):
# no copy is kept, the list of what was written is (pokes.txt beside this script), and the value of the game goes back
# wherever the file still holds the one the mod wrote.
#
# Nothing is written unless every file is the one this mod was made for (each is checked by its SHA-256), and
# unless every file changed before is still as this script left it (the list installed.txt beside this script): a
# game that was updated or repaired since then is not written over with the copies of an older one.
param([string]$Mode = 'install', [string]$Variant = '')

$ErrorActionPreference = 'Stop'
$modDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $modDir
$backup = Join-Path $modDir 'backup'
$stateFile = Join-Path $modDir 'installed.txt'
$pokeFile = Join-Path $modDir 'pokes.txt'

function Get-Sha([byte[]]$bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return -join ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) } finally { $sha.Dispose() }
}

function To-Bytes([string]$hex) {
    $bytes = New-Object byte[] ($hex.Length / 2)
    for ($i = 0; $i -lt $bytes.Length; $i++) { $bytes[$i] = [Convert]::ToByte($hex.Substring($i * 2, 2), 16) }
    return ,$bytes
}

function Holds([byte[]]$data, [int]$offset, [byte[]]$bytes) {
    if ($offset + $bytes.Length -gt $data.Length) { return $false }
    for ($i = 0; $i -lt $bytes.Length; $i++) { if ($data[$offset + $i] -ne $bytes[$i]) { return $false } }
    return $true
}

function Write-File([string]$path, [byte[]]$bytes) {
    $folder = Split-Path -Parent $path
    if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }
    [System.IO.File]::WriteAllBytes($path, $bytes)
}

function Backup-Files {
    # relative paths of everything kept in the backup folder
    if (-not (Test-Path $backup)) { return @() }
    $prefix = $backup.TrimEnd('\') + '\'
    return @(Get-ChildItem -Path $backup -Recurse -File | ForEach-Object { $_.FullName.Substring($prefix.Length) })
}

function Read-State {
    # what this script wrote last time: relative path (lower case) -> SHA-256. Empty when there is no list.
    $state = @{}
    if (Test-Path $stateFile) {
        foreach ($line in [System.IO.File]::ReadAllLines($stateFile)) {
            $p = $line.Split('|')
            if ($p.Length -eq 2) { $state[$p[0].ToLower()] = $p[1] }
        }
    }
    return $state
}

function Changed-Since([hashtable]$state, [string]$rel, [string[]]$known) {
    # true when the file of the game is neither what this script wrote nor one of the known states of it
    if (-not $state.ContainsKey($rel.ToLower())) { return $false }
    $game = Join-Path $root $rel
    if (-not (Test-Path $game)) { return $true }
    $now = Get-Sha ([System.IO.File]::ReadAllBytes($game))
    return ($now -ne $state[$rel.ToLower()]) -and ($known -notcontains $now)
}

$updated = @('The game was updated or repaired after the mod was installed, so the copies kept in',
             "$(Split-Path -Leaf $modDir)\backup belong to an older game. Delete the folder $(Split-Path -Leaf $modDir)\backup and the file",
             "$(Split-Path -Leaf $modDir)\installed.txt, have the launcher of the game check its files, and install again.")

function Holds-At([string]$path, [int]$offset, [byte[]]$bytes) {
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

function Known-Pokes {
    # every value this mod may have written in place: the record of the last install, and the lists of the variants
    # unpacked beside this script (an older record may be lost, or made by another version of the same variant)
    $list = @()
    foreach ($file in @(Get-ChildItem -Path $modDir -Filter *.txt -File)) { $list += (Read-Pokes $file.FullName) }
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

function Stop-With([string[]]$lines) {
    foreach ($line in $lines) { Write-Host $line }
    Write-Host ''
    Write-Host 'Nothing was changed.'
    exit 1
}

if (-not (Test-Path (Join-Path $root 'Data\ENG\Parameter'))) {
    Stop-With @("This is not the folder of the game: $root",
                'Unpack the archive into the folder that holds the .exe of the game and its folder Data.')
}

if ($Mode -eq 'uninstall') {
    $kept = Backup-Files
    $written = Known-Pokes
    if ($kept.Count -eq 0 -and $written.Count -eq 0) { Write-Host 'No backup here: the mod is not installed.'; exit 0 }
    $state = Read-State
    $moved = @()
    foreach ($rel in $kept) {
        $original = Get-Sha ([System.IO.File]::ReadAllBytes((Join-Path $backup $rel)))
        if (Changed-Since $state $rel @($original)) { $moved += "${rel}: changed since the mod was installed" }
    }
    if ($moved.Count -gt 0) { Stop-With ($moved + $updated) }
    try {
        foreach ($rel in $kept) { Copy-Item -Path (Join-Path $backup $rel) -Destination (Join-Path $root $rel) -Force }
        [void](Undo-Pokes $written)
        if (Test-Path $pokeFile) { Remove-Item -Path $pokeFile -Force }
    } catch {
        Stop-With @("A file could not be written: $($_.Exception.Message)", 'Close the game and run this again.')
    }
    if (Test-Path $backup) { Remove-Item -Path $backup -Recurse -Force }
    if (Test-Path $stateFile) { Remove-Item -Path $stateFile -Force }
    Write-Host "The game is as it was: $($kept.Count) file(s) put back."
    exit 0
}

# ---- install ---------------------------------------------------------------------------------------------------
$manifest = Join-Path $modDir "$Variant.txt"
if (-not (Test-Path $manifest)) { Stop-With @("No variant '$Variant' in this archive.") }
$ops = [System.IO.File]::ReadAllBytes((Join-Path $modDir "$Variant.ops"))
$blob = [System.IO.File]::ReadAllBytes((Join-Path $modDir "$Variant.dat"))
$files = @()
$layouts = @{}
foreach ($line in [System.IO.File]::ReadAllLines($manifest)) {
    $p = $line.Split('|')
    if ($p[0] -eq 'file') {
        $files += ,@{ Rel = $p[1]; Old = $p[2]; New = $p[3]; Size = [int]$p[4]; Start = [int]$p[5]; Count = [int]$p[6] }
    } elseif ($p[0] -eq 'exe') {
        if (-not $layouts.ContainsKey($p[1])) { $layouts[$p[1]] = @() }
        $layouts[$p[1]] += ,@{ Offset = [Convert]::ToInt32($p[2], 16); Old = (To-Bytes $p[3]); New = (To-Bytes $p[4]) }
    }
}

$state = Read-State
$stale = $false
$problems = @()
$writes = @()          # what to write: Rel, Bytes, and Source (the original, to keep) when there is no copy yet
$named = @{}

# 1. the data files: each from its original, which is the copy kept here or the file of the game
foreach ($f in $files) {
    $named[$f.Rel.ToLower()] = $true
    $game = Join-Path $root $f.Rel
    $copy = Join-Path $backup $f.Rel
    if (-not (Test-Path $game)) { $problems += "$($f.Rel): not found in the game"; continue }
    $hasCopy = Test-Path $copy
    $path = $game
    if ($hasCopy) { $path = $copy }
    if ($hasCopy -and (Changed-Since $state $f.Rel @($f.Old, $f.New))) {
        $problems += "$($f.Rel): changed since the mod was installed"
        $stale = $true
        continue
    }
    $source = [System.IO.File]::ReadAllBytes($path)
    if ((Get-Sha $source) -ne $f.Old) {
        $problems += "$($f.Rel): not the original file (another version of the game, or another mod is installed)"
        continue
    }
    $out = New-Object byte[] $f.Size
    $pos = 0
    for ($k = 0; $k -lt $f.Count; $k++) {
        $at = ($f.Start + $k) * 12
        $kind = [BitConverter]::ToInt32($ops, $at)
        $from = [BitConverter]::ToInt32($ops, $at + 4)
        $length = [BitConverter]::ToInt32($ops, $at + 8)
        if ($kind -eq 0) { [System.Buffer]::BlockCopy($source, $from, $out, $pos, $length) }
        else { [System.Buffer]::BlockCopy($blob, $from, $out, $pos, $length) }
        $pos += $length
    }
    if ($pos -ne $f.Size -or (Get-Sha $out) -ne $f.New) { $problems += "$($f.Rel): the result does not check"; continue }
    $keep = $null
    if (-not $hasCopy) { $keep = $source }
    $writes += ,@{ Rel = $f.Rel; Bytes = $out; Source = $keep }
}

# 2. the program: every .exe of the folder that is the program, whatever its name
$programs = 0
foreach ($exe in @(Get-ChildItem -Path $root -Filter *.exe -File)) {
    if ($layouts.Count -eq 0) { break }            # a variant that leaves the program alone: step 3 puts it back
    $rel = $exe.Name
    $copy = Join-Path $backup $rel
    $hasCopy = Test-Path $copy
    $path = $exe.FullName
    if ($hasCopy) { $path = $copy }
    $source = [System.IO.File]::ReadAllBytes($path)
    if ($hasCopy -and (Changed-Since $state $rel @((Get-Sha $source)))) {
        $problems += "${rel}: changed since the mod was installed"
        $stale = $true
        continue
    }
    $rows = $null
    foreach ($name in $layouts.Keys) {
        $fits = $true
        foreach ($row in $layouts[$name]) { if (-not (Holds $source $row.Offset $row.Old)) { $fits = $false; break } }
        if ($fits) { $rows = $layouts[$name]; break }
    }
    if ($null -eq $rows) {
        if ($hasCopy) { $problems += "${rel}: its copy in the backup is not the program this mod was made for" }
        continue                                   # another .exe of the folder: left alone
    }
    $programs++
    $named[$rel.ToLower()] = $true
    $out = New-Object byte[] $source.Length
    [System.Buffer]::BlockCopy($source, 0, $out, 0, $source.Length)
    foreach ($row in $rows) { for ($i = 0; $i -lt $row.New.Length; $i++) { $out[$row.Offset + $i] = $row.New[$i] } }
    $keep = $null
    if (-not $hasCopy) { $keep = $source }
    $writes += ,@{ Rel = $rel; Bytes = $out; Source = $keep }
}
if ($layouts.Count -gt 0 -and $programs -eq 0 -and -not $stale) {
    $problems += 'No program file of the game found here in its original state (is another mod installed?)'
}

# a file another variant changed and this one leaves alone goes back in step 3: it must be as it was left too
foreach ($rel in (Backup-Files)) {
    if ($named.ContainsKey($rel.ToLower())) { continue }
    $original = Get-Sha ([System.IO.File]::ReadAllBytes((Join-Path $backup $rel)))
    if (Changed-Since $state $rel @($original)) { $problems += "${rel}: changed since the mod was installed"; $stale = $true }
}
# the values written in place: each place must hold the value of the game, the one this variant writes, or one this
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
if ($stale) { $problems += $updated }
# a file the game holds open cannot be replaced: found now, before anything is written
$touched = @($writes | ForEach-Object { $_.Rel }) + @($pokes | ForEach-Object { $_.Rel } | Sort-Object -Unique)
foreach ($rel in $touched) {
    if (-not (Test-Path (Join-Path $root $rel))) { continue }
    try { [System.IO.File]::Open((Join-Path $root $rel), [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None).Dispose() }
    catch { $problems += "${rel}: in use. Close the game and run this again." }
}
if ($problems.Count -gt 0) { Stop-With $problems }

# 3. write. First the copy of every original and every new file beside its place, under another name; only when all
# of them are on the disk is each moved into its place, so a failure before that leaves the game as it was. What
# another variant changed and this one does not goes back.
$staged = '.dt22new'
try {
    foreach ($w in $writes) {
        if ($null -ne $w.Source) {                    # the copy too goes under another name first: never half a copy
            $copy = Join-Path $backup $w.Rel
            Write-File ($copy + $staged) $w.Source
            Move-Item -LiteralPath ($copy + $staged) -Destination $copy -Force
        }
        Write-File ((Join-Path $root $w.Rel) + $staged) $w.Bytes
    }
    foreach ($w in $writes) {
        $target = Join-Path $root $w.Rel
        Move-Item -LiteralPath ($target + $staged) -Destination $target -Force
    }
    [System.IO.File]::WriteAllLines($stateFile, [string[]]@($writes | ForEach-Object { "$($_.Rel)|$(Get-Sha $_.Bytes)" }))
    # the record first: what was known and what is about to be written, so a stop half way leaves nothing unrecorded
    $record = @($known | ForEach-Object { $_.Line }) + @($pokes | ForEach-Object { $_.Line }) | Sort-Object -Unique
    if ($record.Count -gt 0) { [System.IO.File]::WriteAllLines($pokeFile, [string[]]$record) }
    [void](Undo-Pokes $known)                             # what this mod wrote in place before goes back first
    foreach ($k in $pokes) { Put-At (Join-Path $root $k.Rel) $k.Offset $k.New }
    if ($pokes.Count -gt 0) { [System.IO.File]::WriteAllLines($pokeFile, [string[]]@($pokes | ForEach-Object { $_.Line })) }
    elseif (Test-Path $pokeFile) { Remove-Item -Path $pokeFile -Force }
    $back = 0
    foreach ($rel in (Backup-Files)) {
        if (-not $named.ContainsKey($rel.ToLower())) {
            Copy-Item -Path (Join-Path $backup $rel) -Destination (Join-Path $root $rel) -Force
            $back++
        }
    }
} catch {
    foreach ($w in $writes) {
        $left = (Join-Path $root $w.Rel) + $staged
        if (Test-Path -LiteralPath $left) { Remove-Item -LiteralPath $left -Force }
    }
    Write-Host "A file could not be written: $($_.Exception.Message)"
    Write-Host 'Close the game and run this again. To put everything back, run the Uninstall .bat.'
    exit 1
}
Write-Host "Done: $($files.Count) data file(s) changed, $programs program file(s) patched."
if ($pokes.Count -gt 0) { Write-Host "$($pokes.Count) value(s) changed in the files of the dungeons." }
if ($back -gt 0) { Write-Host "$back file(s) of another variant put back as the original." }
Write-Host "A copy of every original is in $(Split-Path -Leaf $modDir)\backup. To take the mod out, run the Uninstall .bat."
