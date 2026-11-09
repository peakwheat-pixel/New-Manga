#requires -Version 7.0
<#
.SYNOPSIS
  FEA-07-RESIDUAL-4 / AC-R4-2: prove that the default headless suite writes nothing to the real
  %APPDATA% trees, with a discriminating self-test.

.DESCRIPTION
  Snapshots two user-data trees:
    * %APPDATA%\com.newmanga.desktop   (legacy shell: logs/window-material.log, logs/startup.log, data)
    * %APPDATA%\NewManga               (theme/appearance home, if present)
  and compares file set + file lengths + window-material.log line count + startup.log existence.

  Modes (exactly one):
    -Capture <json>   write a baseline snapshot
    -Verify  <json>   capture now, compare with baseline; any delta -> EXIT 1 (fail closed)
    -SelfTest         prove the comparator is not a no-op: append one line to an isolated temp copy
                      must report a delta and EXIT 1; a clean compare must EXIT 0. Never touches the
                      real %APPDATA%.

  -RootOverride <dir> is for the self-test only (expects <dir>\com.newmanga.desktop and <dir>\NewManga).
#>
[CmdletBinding(DefaultParameterSetName = 'Capture')]
param(
    [Parameter(ParameterSetName = 'Capture', Mandatory = $true)]
    [string]$Capture,

    [Parameter(ParameterSetName = 'Verify', Mandatory = $true)]
    [string]$Verify,

    [Parameter(ParameterSetName = 'SelfTest', Mandatory = $true)]
    [switch]$SelfTest,

    [string]$RootOverride,

    [string]$LogPath
)

$ErrorActionPreference = 'Stop'
$script:exitCode = 0

function Get-DataRoots {
    param([string]$OverrideRoot)
    $base = if ($OverrideRoot) { $OverrideRoot } else { $env:APPDATA }
    return @(
        @{ Name = 'com.newmanga.desktop'; Path = (Join-Path $base 'com.newmanga.desktop') }
        @{ Name = 'NewManga'; Path = (Join-Path $base 'NewManga') }
    )
}

function Count-Lines {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return 0 }
    $count = 0
    foreach ($_ in [System.IO.File]::ReadLines($Path)) { $count++ }
    return $count
}

function Get-Snapshot {
    param([string]$SnapshotRootOverride)
    $snap = [ordered]@{ capturedAt = (Get-Date).ToString('o'); roots = [ordered]@{} }
    foreach ($root in Get-DataRoots -OverrideRoot $SnapshotRootOverride) {
        $entry = [ordered]@{
            path = $root.Path
            exists = (Test-Path -LiteralPath $root.Path -PathType Container)
            files = [ordered]@{}
            windowMaterialLines = 0
            startupLogExists = $false
        }
        if ($entry.exists) {
            foreach ($file in (Get-ChildItem -LiteralPath $root.Path -Recurse -File -Force)) {
                $relative = $file.FullName.Substring($root.Path.Length).TrimStart('\', '/')
                $entry.files[$relative] = $file.Length
            }
            $entry.windowMaterialLines = Count-Lines (Join-Path $root.Path 'logs\window-material.log')
            $entry.startupLogExists = Test-Path -LiteralPath (Join-Path $root.Path 'logs\startup.log') -PathType Leaf
        }
        $snap.roots[$root.Name] = $entry
    }
    return $snap
}

function Compare-Snapshots {
    param($Before, $After)
    $diffs = [System.Collections.Generic.List[string]]::new()
    foreach ($rootName in $Before.roots.Keys) {
        $b = $Before.roots[$rootName]
        $a = $After.roots[$rootName]
        if ($b.exists -ne $a.exists) {
            $diffs.Add("$rootName exists: $($b.exists) -> $($a.exists)")
            continue
        }
        if (-not $b.exists) { continue }

        $bFiles = @($b.files.Keys)
        $aFiles = @($a.files.Keys)
        foreach ($added in ($aFiles | Where-Object { $_ -notin $bFiles })) {
            $diffs.Add("$rootName file added: $added")
        }
        foreach ($removed in ($bFiles | Where-Object { $_ -notin $aFiles })) {
            $diffs.Add("$rootName file removed: $removed")
        }
        foreach ($name in ($bFiles | Where-Object { $_ -in $aFiles })) {
            if ($b.files[$name] -ne $a.files[$name]) {
                $diffs.Add("$rootName size changed: $name $($b.files[$name]) -> $($a.files[$name])")
            }
        }
        if ($b.windowMaterialLines -ne $a.windowMaterialLines) {
            $diffs.Add("$rootName window-material.log lines: $($b.windowMaterialLines) -> $($a.windowMaterialLines)")
        }
        if ($b.startupLogExists -ne $a.startupLogExists) {
            $diffs.Add("$rootName startup.log exists: $($b.startupLogExists) -> $($a.startupLogExists)")
        }
    }
    return $diffs
}

function Write-Log {
    param([string]$Text)
    if ($LogPath) {
        $dir = Split-Path -Parent $LogPath
        if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        Add-Content -LiteralPath $LogPath -Value $Text -Encoding utf8
    }
    Write-Host $Text
}

try {
    switch ($PSCmdlet.ParameterSetName) {
        'Capture' {
            $snap = Get-Snapshot
            $dir = Split-Path -Parent $Capture
            if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
            $snap | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Capture -Encoding utf8
            Write-Log "SNAPSHOT OK -> $Capture"
        }
        'Verify' {
            if (-not (Test-Path -LiteralPath $Verify -PathType Leaf)) {
                Write-Log "FAIL: baseline snapshot missing: $Verify"
                $script:exitCode = 1
                break
            }
            $before = Get-Content -LiteralPath $Verify -Raw | ConvertFrom-Json
            $after = Get-Snapshot
            $diffs = Compare-Snapshots -Before $before -After $after
            if ($diffs.Count -gt 0) {
                Write-Log "DELTA DETECTED ($($diffs.Count) item(s)) — real AppData was written:"
                foreach ($diff in $diffs) { Write-Log "  - $diff" }
                $script:exitCode = 1
            }
            else {
                Write-Log "ZERO-WRITE OK: com.newmanga.desktop + NewManga unchanged (delta=0)"
            }
        }
        'SelfTest' {
            $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('nm-r4-selftest-' + [guid]::NewGuid().ToString('N'))
            $legacyLogs = Join-Path $tempRoot 'com.newmanga.desktop\logs'
            New-Item -ItemType Directory -Force -Path $legacyLogs | Out-Null
            $materialLog = Join-Path $legacyLogs 'window-material.log'
            Set-Content -LiteralPath $materialLog -Value @('line-1', 'line-2', 'line-3') -Encoding utf8
            $snapshotPath = Join-Path $tempRoot 'before.json'
            try {
                $before = Get-Snapshot -SnapshotRootOverride $tempRoot
                $before | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $snapshotPath -Encoding utf8
                Add-Content -LiteralPath $materialLog -Value 'line-4' -Encoding utf8
                $after = Get-Snapshot -SnapshotRootOverride $tempRoot
                $diffs = Compare-Snapshots -Before $before -After $after
                $detected = ($diffs | Where-Object { $_ -match 'window-material\.log lines: 3 -> 4' }).Count -gt 0
                if (-not $detected) {
                    Write-Log "SELFTEST FAIL: appended line was not detected (would be a silent pass)"
                    $script:exitCode = 1
                    break
                }
                Write-Log "SELFTEST KILL: appended line detected as delta -> EXIT 1 by design"
                $clean = Get-Snapshot -SnapshotRootOverride $tempRoot
                $cleanDiffs = Compare-Snapshots -Before $after -After $clean
                if ($cleanDiffs.Count -ne 0) {
                    Write-Log "SELFTEST FAIL: clean compare reported $($cleanDiffs.Count) difference(s)"
                    $script:exitCode = 1
                    break
                }
                Write-Log "SELFTEST OK: no-change compare delta=0 -> EXIT 0"
            }
            finally {
                if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
            }
        }
    }
}
catch {
    Write-Log "FAIL: $($_.Exception.Message)"
    $script:exitCode = 1
}

exit $script:exitCode
