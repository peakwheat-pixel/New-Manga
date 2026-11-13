# AUDIT-12-CAND-001: publish output path/cleanup policy tests (no dotnet publish).
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $scriptRoot '..\..\..')).Path
. (Join-Path $scriptRoot 'publish-paths.ps1')

$failures = [System.Collections.Generic.List[string]]::new()
$passes = 0

function Check {
    param([string]$Name, [scriptblock]$Body)
    try {
        & $Body
        $script:passes++
        Write-Output "PASS $Name"
    }
    catch {
        $failures.Add("$Name :: $($_.Exception.Message)")
        Write-Output "FAIL $Name :: $($_.Exception.Message)"
    }
}

function Expect-Throws {
    param([string]$Name, [scriptblock]$Body)
    try {
        & $Body | Out-Null
        $failures.Add("$Name :: expected a throw")
        Write-Output "FAIL $Name :: expected a throw"
    }
    catch {
        $script:passes++
        Write-Output "PASS $Name"
    }
}

Check 'default output is inside workspace publish root' {
    $default = Get-DefaultPublishOutputDirectory -RepoRoot $repoRoot
    $workspace = Get-PublishWorkspaceRoot -RepoRoot $repoRoot
    if (-not (Test-PathInside -Path $default -Root ([IO.Path]::Combine($workspace, 'publish')))) {
        throw "default output is not under workspace publish root: $default"
    }
}

Check 'default output is outside the repository' {
    $default = Get-DefaultPublishOutputDirectory -RepoRoot $repoRoot
    if (Test-PathInside -Path $default -Root $repoRoot) {
        throw "default output is inside the repository: $default"
    }
}

Expect-Throws 'repository path is rejected' {
    $inside = [IO.Path]::Combine($repoRoot, 'apps', 'desktop-avalonia', 'artifacts', 'win-x64-single')
    Assert-SafePublishOutput -Path $inside -RepoRoot $repoRoot -AllowDelete | Out-Null
}

Expect-Throws 'drive root is rejected' {
    $drive = [IO.Path]::GetPathRoot($repoRoot)
    Assert-SafePublishOutput -Path $drive -RepoRoot $repoRoot -AllowDelete | Out-Null
}

Expect-Throws 'empty path is rejected' {
    Assert-SafePublishOutput -Path '  ' -RepoRoot $repoRoot -AllowDelete | Out-Null
}

Check 'workspace publish disposable directory may be cleaned' {
    $workspace = Get-PublishWorkspaceRoot -RepoRoot $repoRoot
    $disposable = [IO.Path]::Combine($workspace, 'publish', 'audit12-disposable-' + [Guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Force -Path $disposable | Out-Null
    try {
        $marker = [IO.Path]::Combine($disposable, 'marker.txt')
        Set-Content -LiteralPath $marker -Value 'x' -Encoding utf8
        $resolved = Assert-SafePublishOutput -Path $disposable -RepoRoot $repoRoot -AllowDelete
        if (-not $resolved) { throw 'Assert returned no path' }
        Remove-Item -LiteralPath $resolved -Recurse -Force
        if (Test-Path -LiteralPath $disposable) { throw 'disposable directory was not removed' }
    }
    finally {
        if (Test-Path -LiteralPath $disposable) {
            Remove-Item -LiteralPath $disposable -Recurse -Force
        }
    }
}

Expect-Throws 'existing directory outside publish root is not cleaned' {
    $outside = Join-Path ([IO.Path]::GetTempPath()) ('nm-publish-outside-' + [Guid]::NewGuid().ToString('N').Substring(0, 8))
    New-Item -ItemType Directory -Force -Path $outside | Out-Null
    try {
        Assert-SafePublishOutput -Path $outside -RepoRoot $repoRoot -AllowDelete | Out-Null
    }
    finally {
        if (Test-Path -LiteralPath $outside) {
            Remove-Item -LiteralPath $outside -Recurse -Force
        }
    }
}

Write-Output "SUMMARY passes=$passes failures=$($failures.Count)"
if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Output "DETAIL $_" }
    exit 1
}

exit 0
