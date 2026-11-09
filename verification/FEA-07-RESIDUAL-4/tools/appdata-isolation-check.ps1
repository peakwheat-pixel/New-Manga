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
    -SelfTest         prove the comparator is not a no-op and that the delta path really exits 1:
                      run -Verify in a child process against an isolated temp root, once after
                      appending one line (must EXIT 1) and once unchanged (must EXIT 0).
                      Never touches the real %APPDATA%.

  -RootOverride <dir> redirects both trees (self-test / isolated verification only).
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

function Write-Log {
    param([string]$Text)
    if ($LogPath) {
        $dir = Split-Path -Parent $LogPath
        if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        Add-Content -LiteralPath $LogPath -Value $Text -Encoding utf8
    }
    Write-Host $Text
}

function Write-Header {
    param([string]$Mode)
    Write-Log "# appdata-isolation-check mode=$Mode time=$((Get-Date).ToString('o'))"
    Write-Log "# shell=$($PSVersionTable.PSVersion) / $($PSVersionTable.PSEdition) rootOverride=$RootOverride"
    Write-Log "# script=$PSCommandPath"
}

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

function ConvertTo-Hashtable {
    param($Node)
    if ($null -eq $Node) { return $null }
    if ($Node -is [System.Collections.IDictionary]) {
        $table = @{}
        foreach ($key in $Node.Keys) { $table[$key] = ConvertTo-Hashtable $Node[$key] }
        return $table
    }
    if ($Node -is [System.Management.Automation.PSCustomObject]) {
        $table = @{}
        foreach ($property in $Node.PSObject.Properties) { $table[$property.Name] = ConvertTo-Hashtable $property.Value }
        return $table
    }
    return $Node
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

function Start-VerifyChild {
    param([string]$Snapshot, [string]$Root)
    $childLog = Join-Path $Root ('child-' + [guid]::NewGuid().ToString('N') + '.log')
    $pwshPath = (Get-Process -Id $PID).Path
    $arguments = @('-NoProfile', '-File', "`"$PSCommandPath`"", '-Verify', "`"$Snapshot`"", '-RootOverride', "`"$Root`"", '-LogPath', "`"$childLog`"")
    $process = Start-Process -FilePath $pwshPath -ArgumentList $arguments -Wait -PassThru -NoNewWindow
    if (Test-Path -LiteralPath $childLog) {
        Get-Content -LiteralPath $childLog | ForEach-Object { Write-Log "  [child] $_" }
    }
    return $process.ExitCode
}

try {
    switch ($PSCmdlet.ParameterSetName) {
        'Capture' {
            Write-Header -Mode 'Capture'
            $snap = Get-Snapshot -SnapshotRootOverride $RootOverride
            $dir = Split-Path -Parent $Capture
            if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
            $snap | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Capture -Encoding utf8
            Write-Log "SNAPSHOT OK -> $Capture"
            Write-Log "EXIT=0"
        }
        'Verify' {
            Write-Header -Mode 'Verify'
            if (-not (Test-Path -LiteralPath $Verify -PathType Leaf)) {
                Write-Log "FAIL: baseline snapshot missing: $Verify"
                Write-Log "EXIT=1"
                $script:exitCode = 1
                break
            }
            $before = ConvertTo-Hashtable (Get-Content -LiteralPath $Verify -Raw | ConvertFrom-Json)
            $after = Get-Snapshot -SnapshotRootOverride $RootOverride
            $beforeLines = $before.roots.'com.newmanga.desktop'.windowMaterialLines
            $afterLines = $after.roots.'com.newmanga.desktop'.windowMaterialLines
            Write-Log "before: $beforeLines window-material lines; after: $afterLines window-material lines"
            $diffs = Compare-Snapshots -Before $before -After $after
            if ($diffs.Count -gt 0) {
                Write-Log "DELTA DETECTED ($($diffs.Count) item(s)) — real AppData was written:"
                foreach ($diff in $diffs) { Write-Log "  - $diff" }
                Write-Log "EXIT=1"
                $script:exitCode = 1
            }
            else {
                Write-Log "ZERO-WRITE OK: com.newmanga.desktop + NewManga unchanged (delta=0)"
                Write-Log "EXIT=0"
            }
        }
        'SelfTest' {
            Write-Header -Mode 'SelfTest'
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
                $childDirty = Start-VerifyChild -Snapshot $snapshotPath -Root $tempRoot
                if ($childDirty -ne 1) {
                    Write-Log "SELFTEST FAIL: changed root must make -Verify exit 1, got EXIT=$childDirty"
                    Write-Log "EXIT=1"
                    $script:exitCode = 1
                    break
                }
                Write-Log "SELFTEST KILL: appended line detected by child -Verify -> EXIT 1 (real exit code)"

                # Re-baseline after the append, then prove an unchanged root exits 0 against its own baseline.
                $afterDirty = Get-Snapshot -SnapshotRootOverride $tempRoot
                $dirtySnapshotPath = Join-Path $tempRoot 'after-dirty.json'
                $afterDirty | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $dirtySnapshotPath -Encoding utf8
                $childClean = Start-VerifyChild -Snapshot $dirtySnapshotPath -Root $tempRoot
                if ($childClean -ne 0) {
                    Write-Log "SELFTEST FAIL: unchanged root must make -Verify exit 0, got EXIT=$childClean"
                    Write-Log "EXIT=1"
                    $script:exitCode = 1
                    break
                }
                Write-Log "SELFTEST OK: unchanged root -> child -Verify EXIT 0"
                Write-Log "EXIT=0"
            }
            finally {
                if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
            }
        }
    }
}
catch {
    Write-Log "FAIL: $($_.Exception.Message)"
    Write-Log "EXIT=1"
    $script:exitCode = 1
}

exit $script:exitCode
