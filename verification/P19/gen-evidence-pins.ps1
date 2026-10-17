# Generate Canonical Evidence table rows for P19 from MEASURED disk bytes.
# BL-19 compliance: hashes are never transcribed by hand; this script reads the bytes
# and emits the exact rows to paste into doc/tasks/P19.md.
#
# Usage:
#   pwsh -NoProfile -File verification/P19/gen-evidence-pins.ps1 -Paths <p1>,<p2>,...
#   pwsh -NoProfile -File verification/P19/gen-evidence-pins.ps1 -FromDir verification/P19/ac2-main-XXXX
param(
  [string]$RepoRoot = 'G:/CODEX/New Manga',
  [string[]]$Paths = @(),
  [string[]]$FromDir = @(),
  [string]$Class = 'CANONICAL',
  [switch]$EmitIds
)
$ErrorActionPreference = 'Stop'

# `pwsh -File` passes `-Paths a,b` as ONE string; normalise both calling styles.
if ($Paths.Count -eq 1 -and $Paths[0] -match ',') { $Paths = $Paths[0] -split ',' }
if ($FromDir.Count -eq 1 -and $FromDir[0] -match ',') { $FromDir = $FromDir[0] -split ',' }
$Paths = @($Paths | Where-Object { $_ -and $_.Trim() } | ForEach-Object { $_.Trim() })
$FromDir = @($FromDir | Where-Object { $_ -and $_.Trim() } | ForEach-Object { $_.Trim() })

$targets = New-Object System.Collections.Generic.List[System.IO.FileInfo]
foreach ($p in $Paths) {
  $full = if ([System.IO.Path]::IsPathRooted($p)) { $p } else { Join-Path $RepoRoot $p }
  if (Test-Path -LiteralPath $full -PathType Leaf) { $targets.Add((Get-Item -LiteralPath $full)) }
  elseif (Test-Path -LiteralPath $full -PathType Container) { Get-ChildItem -LiteralPath $full -Recurse -File | ForEach-Object { $targets.Add($_) } }
  else { Write-Warning "not found: $full" }
}
foreach ($d in $FromDir) {
  $full = if ([System.IO.Path]::IsPathRooted($d)) { $d } else { Join-Path $RepoRoot $d }
  if (Test-Path -LiteralPath $full) { Get-ChildItem -LiteralPath $full -Recurse -File | ForEach-Object { $targets.Add($_) } }
  else { Write-Warning "not found: $full" }
}

$commit = (& git -C $RepoRoot rev-parse HEAD).Trim()
$rows = New-Object System.Collections.Generic.List[string]
$i = 0
foreach ($f in ($targets | Sort-Object FullName -Unique)) {
  $rel = $f.FullName.Replace(($RepoRoot -replace '/', '\'), '').TrimStart('\').Replace('\', '/')
  $sha = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLower()
  $i++
  $id = if ($EmitIds) { "E$i" } else { '' }
  if ($EmitIds) { $rows.Add("| $id | ``$rel`` | ``$commit`` | ``$sha`` | $Class |") }
  else         { $rows.Add("| ``$rel`` | ``$commit`` | ``$sha`` | $Class |") }
}
$rows | ForEach-Object { Write-Output $_ }
Write-Output ("# rows=" + $rows.Count + " commit=" + $commit + " class=" + $Class)
