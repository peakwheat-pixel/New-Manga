# FEA-12-DSIM-1 — static scan evidence (Windows recycle-bin API + test path literals)
#
# Read-only. Prints the exact commands/patterns used and their hit counts so a
# reviewer can reproduce every zero-hit claim. Exit code 0 = all scans clean.
[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()

function Get-SourceFiles {
    param(
        [string]$Root,
        [string[]]$Suffixes,
        [string[]]$ExcludedDirs
    )
    $files = [System.Collections.Generic.List[string]]::new()
    $queue = [System.Collections.Generic.Queue[string]]::new()
    $queue.Enqueue($Root)
    while ($queue.Count -gt 0) {
        $current = $queue.Dequeue()
        foreach ($dir in [IO.Directory]::GetDirectories($current)) {
            $name = [IO.Path]::GetFileName($dir).ToLowerInvariant()
            if ($ExcludedDirs -contains $name) { continue }
            $queue.Enqueue($dir)
        }
        foreach ($file in [IO.Directory]::GetFiles($current)) {
            $extension = [IO.Path]::GetExtension($file).ToLowerInvariant()
            if ($Suffixes -contains $extension) { $files.Add($file) }
        }
    }
    return , $files
}

$sourceSuffixes = @('.py', '.cs', '.csproj', '.props', '.targets', '.xaml', '.ps1')
$excludedDirs = @(
    'bin', 'obj', 'target', 'dist', 'build', '__pycache__', '.git', '.vs',
    'node_modules', 'testresults', '.pytest_cache', '.venv', 'site-packages'
)
# Windows recycle-bin APIs / bindings that must never appear in production
# source (the frozen scope: no real OS recycle-bin call may be implemented).
$apiTokens = @(
    'shfileoperation', 'shfileopstruct', 'ifileoperation',
    'ifileoperationprogresssink', 'shell32', 'microsoft.visualbasic',
    'windows.storage', 'send2trash', 'winshell', 'win32com',
    'shell.application', 'fof_allowundo'
)

Write-Output '== AC4 / AC1: Windows recycle-bin API scan (src/** + apps/**) =='
Write-Output ("command: Select-String -Pattern '<tokens>' over " + ($sourceSuffixes -join ',') + " files")
Write-Output ("tokens : " + ($apiTokens -join '|'))
Write-Output ("excluded dirs: " + ($excludedDirs -join ','))

$totalScanned = 0
$apiHits = [System.Collections.Generic.List[string]]::new()
foreach ($name in @('src', 'apps')) {
    $root = Join-Path $RepoRoot $name
    $files = Get-SourceFiles -Root $root -Suffixes $sourceSuffixes -ExcludedDirs $excludedDirs
    $totalScanned += $files.Count
    $rootHits = 0
    foreach ($file in $files) {
        $text = [IO.File]::ReadAllText($file).ToLowerInvariant()
        foreach ($token in $apiTokens) {
            if ($text.Contains($token)) {
                $relative = [IO.Path]::GetRelativePath($RepoRoot, $file).Replace('\', '/')
                $apiHits.Add("${relative}: $token")
                $rootHits++
            }
        }
    }
    Write-Output ("scanned {0,-5} files={1,-4} hits={2}" -f $name, $files.Count, $rootHits)
}
Write-Output ("TOTAL scanned files = {0}; API hits = {1}" -f $totalScanned, $apiHits.Count)
if ($totalScanned -lt 100) { $failures.Add('API scan covered fewer than 100 files (suspicious)') }
if ($apiHits.Count -gt 0) {
    foreach ($hit in $apiHits) { Write-Output ("HIT: " + $hit) }
    $failures.Add('Windows recycle-bin API reference found in src/** or apps/**')
}

Write-Output ''
Write-Output '== AC4: test-source real-path-literal scan (tests/fea12/**) =='
$forbiddenNeedles = @(
    ('%' + 'APPDATA' + '%'),
    ('%' + 'LOCALAPPDATA' + '%'),
    ('%' + 'USERPROFILE' + '%'),
    ('$' + 'env:APPDATA'),
    ('$Recycle' + '.Bin')
)
$drivePath = [regex]::new('(?<![A-Za-z0-9_])' + '[A-Za-z]' + ':' + '[\\/]')
$testFiles = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'tests/fea12') -Filter '*.py' -File)
Write-Output ("command: Select-String -SimpleMatch each pattern + regex drive-path over tests/fea12/*.py")
Write-Output ("files  : " + (($testFiles | ForEach-Object { $_.Name }) -join ', '))
$testHits = [System.Collections.Generic.List[string]]::new()
foreach ($file in $testFiles) {
    $text = [IO.File]::ReadAllText($file.FullName)
    foreach ($needle in $forbiddenNeedles) {
        if ($text.Contains($needle)) {
            $testHits.Add("$($file.Name): forbidden literal " + $needle)
        }
    }
    foreach ($match in $drivePath.Matches($text)) {
        $testHits.Add("$($file.Name): volume path " + $match.Value)
    }
}
Write-Output ("TOTAL test files = {0}; literal hits = {1}" -f $testFiles.Count, $testHits.Count)
if ($testFiles.Count -lt 2) { $failures.Add('test-source scan covered fewer than 2 files (suspicious)') }
if ($testHits.Count -gt 0) {
    foreach ($hit in $testHits) { Write-Output ("HIT: " + $hit) }
    $failures.Add('real path literal found in tests/fea12/**')
}

Write-Output ''
Write-Output '== AC3: D-flow modules contain no permanent-delete / DB / process fallback =='
$dflowModules = @(
    'src/application/maintenance/recycle_gateway.py',
    'src/infrastructure/filesystem/simulated_recycle_bin.py'
)
$fallbackPatterns = @(
    'rmtree(', 'unlink(', 'os.remove(', 'os.unlink(', 'os.rmdir(',
    'remove_managed(', 'purge_pages(', 'permanently_delete(',
    'sqlite', 'subprocess', 'ctypes', 'winreg', 'os.system('
)
Write-Output ("command: Select-String -SimpleMatch patterns over the two D-flow modules")
Write-Output ("patterns: " + ($fallbackPatterns -join ', '))
$moduleHits = [System.Collections.Generic.List[string]]::new()
$moduleLines = 0
foreach ($relative in $dflowModules) {
    $full = Join-Path $RepoRoot $relative
    $text = [IO.File]::ReadAllText($full)
    $moduleLines += ([regex]::Matches($text, "`n")).Count
    foreach ($pattern in $fallbackPatterns) {
        if ($text.Contains($pattern)) { $moduleHits.Add("${relative}: " + $pattern) }
    }
    Write-Output ("checked " + $relative)
}
Write-Output ("TOTAL modules = {0}; total lines = {1}; fallback hits = {2}" -f $dflowModules.Count, $moduleLines, $moduleHits.Count)
if ($moduleHits.Count -gt 0) {
    foreach ($hit in $moduleHits) { Write-Output ("HIT: " + $hit) }
    $failures.Add('D-flow module contains a permanent-delete/DB/process fallback token')
}

Write-Output ''
if ($failures.Count -gt 0) {
    foreach ($failure in $failures) { Write-Output ("FAIL: " + $failure) }
    Write-Output ("static scan: FAIL ({0} problems)" -f $failures.Count)
    exit 1
}
Write-Output 'static scan: PASS (0 API hits, 0 real-path literals, 0 delete/DB fallbacks)'
exit 0
