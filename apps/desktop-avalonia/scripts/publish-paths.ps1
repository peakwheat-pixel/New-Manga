# Shared output-path policy for publish.ps1 (AUDIT-12-CAND-001).
# The default publish output must live in the adjacent workspace, and the recursive
# cleanup may only touch a directory under <workspace>\publish.
Set-StrictMode -Version Latest

function Get-PublishWorkspaceRoot {
    param([Parameter(Mandatory)][string]$RepoRoot)

    $resolved = (Resolve-Path -LiteralPath $RepoRoot).Path
    $parent = Split-Path -Parent $resolved
    $leaf = Split-Path -Leaf $resolved
    return (Join-Path $parent ($leaf + '.workspace'))
}

function Get-DefaultPublishOutputDirectory {
    param([Parameter(Mandatory)][string]$RepoRoot)

    return [IO.Path]::Combine(
        (Get-PublishWorkspaceRoot -RepoRoot $RepoRoot),
        'publish',
        'apps-desktop-avalonia',
        'win-x64-single')
}

function Test-PathInside {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Root)

    $full = [IO.Path]::GetFullPath($Path)
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $comparison = [StringComparison]::OrdinalIgnoreCase
    $separator = [IO.Path]::DirectorySeparatorChar
    return ($full.Equals($rootFull, $comparison) -or $full.StartsWith($rootFull + $separator, $comparison))
}

function Assert-SafePublishOutput {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$RepoRoot,
        [switch]$AllowDelete)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw 'publish output directory must not be empty'
    }

    $full = [IO.Path]::GetFullPath($Path)
    $driveRoot = [IO.Path]::GetPathRoot($full)
    if ($full -eq $driveRoot) {
        throw "refusing a drive-root publish output: $full"
    }

    if (Test-PathInside -Path $full -Root $RepoRoot) {
        throw "publish output must live outside the repository: $full"
    }

    if ($AllowDelete -and (Test-Path -LiteralPath $full)) {
        $publishRoot = [IO.Path]::Combine((Get-PublishWorkspaceRoot -RepoRoot $RepoRoot), 'publish')
        if (-not (Test-PathInside -Path $full -Root $publishRoot)) {
            throw "refusing recursive cleanup outside the publish workspace root: $full"
        }
    }

    return $full
}
