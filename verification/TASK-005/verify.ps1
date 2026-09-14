param(
    [string]$BaseCommit = 'd65901b953e6fb26043344ed3d668520847eb295',
    [string]$ReviewedHead = 'HEAD',
    [string]$PythonExe = 'python'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $repoRoot

try {
    $base = (git rev-parse "$BaseCommit^{commit}").Trim()
    if ($LASTEXITCODE -ne 0) { throw "Cannot resolve base commit: $BaseCommit" }
    $head = (git rev-parse "$ReviewedHead^{commit}").Trim()
    if ($LASTEXITCODE -ne 0) { throw "Cannot resolve reviewed head: $ReviewedHead" }
    git merge-base --is-ancestor $base $head
    if ($LASTEXITCODE -ne 0) { throw "$base is not an ancestor of $head" }

    $allowedExact = @(
        '.gitignore',
        'requirements.txt',
        'requirements-dev.txt',
        'src/domain/__init__.py',
        'src/ui/__init__.py',
        'doc/tasks/TASK-005.md'
    )
    $allowedPrefixes = @(
        'src/bootstrap/',
        'src/ui/qml/',
        'tests/core/',
        'verification/TASK-005/'
    )
    $changedPaths = @(git diff --name-only $base $head --)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot enumerate changed paths' }
    foreach ($path in $changedPaths) {
        $allowed = $path -in $allowedExact
        $allowed = $allowed -or ($allowedPrefixes | Where-Object { $path.StartsWith($_) })
        $allowed = $allowed -or $path -like 'doc/handoffs/TASK-005-*.md'
        $allowed = $allowed -or $path -like 'doc/reviews/TASK-005-*.md'
        if (-not $allowed) { throw "Path outside TASK-005 allowance: $path" }
        if ($path -match '^doc/tasks/TASK-(00[6-9]|0[12][0-9])\.md$') {
            throw "Frozen task changed: $path"
        }
    }
    Write-Output "PASS: base/head ancestry and $($changedPaths.Count) allowed paths"

    $expectedCore = @(
        'PySide6_Essentials==6.11.2',
        'shiboken6==6.11.2'
    )
    $expectedDev = @(
        '-r requirements.txt',
        'altgraph==0.17.5',
        'colorama==0.4.6',
        'iniconfig==2.3.0',
        'packaging==26.3',
        'pefile==2024.8.26',
        'pluggy==1.6.0',
        'Pygments==2.21.0',
        'pyinstaller==6.22.3',
        'pyinstaller-hooks-contrib==2026.7',
        'pytest==9.1.1',
        'pywin32-ctypes==0.2.3',
        'setuptools==84.0.0'
    )
    $actualCore = @(Get-Content 'requirements.txt' | Where-Object { $_.Trim() })
    $actualDev = @(Get-Content 'requirements-dev.txt' | Where-Object { $_.Trim() })
    if ((Compare-Object $actualCore $expectedCore).Count -ne 0) {
        throw 'requirements.txt does not match the approved exact lock'
    }
    if ((Compare-Object $actualDev $expectedDev).Count -ne 0) {
        throw 'requirements-dev.txt does not match the approved exact lock'
    }
    if (($actualCore + $actualDev) -match '^(torch|transformers|onnxruntime|PySide6_Addons)(==|$)') {
        throw 'Core/dev requirements contain a forbidden heavy or Addons dependency'
    }
    Write-Output 'PASS: exact Core/dev dependency lock with no heavy AI or PySide6 Addons'

    $pythonVersion = (& $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')").Trim()
    if ($LASTEXITCODE -ne 0) { throw "Cannot execute Python: $PythonExe" }
    if (-not $pythonVersion.StartsWith('3.12.')) {
        throw "TASK-005 requires Python 3.12, got $pythonVersion"
    }
    & $PythonExe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'pip check failed' }
    $presentHeavy = (& $PythonExe -c "import importlib.util; print(','.join(name for name in ('torch','transformers','onnxruntime') if importlib.util.find_spec(name) is not None))").Trim()
    if ($LASTEXITCODE -ne 0) { throw 'Optional dependency probe failed' }
    if ($presentHeavy) { throw "Heavy optional dependencies installed: $presentHeavy" }
    Write-Output "PASS: Python $pythonVersion environment is consistent and heavy AI dependencies are absent"

    $previousPythonPath = $env:PYTHONPATH
    $previousQtPlatform = $env:QT_QPA_PLATFORM
    try {
        $env:PYTHONPATH = (Join-Path $repoRoot 'src')
        $env:QT_QPA_PLATFORM = 'offscreen'
        & $PythonExe -m pytest tests/core
        if ($LASTEXITCODE -ne 0) { throw 'Core pytest failed' }
        & $PythonExe -m bootstrap.app --smoke-test
        if ($LASTEXITCODE -ne 0) { throw 'QML smoke startup failed' }
    }
    finally {
        $env:PYTHONPATH = $previousPythonPath
        $env:QT_QPA_PLATFORM = $previousQtPlatform
    }
    Write-Output 'PASS: core pytest and real QML smoke startup'

    $markdownPaths = @('doc/tasks/TASK-005.md')
    $markdownPaths += @(Get-ChildItem 'verification/TASK-005' -Filter '*.md' | ForEach-Object {
        Resolve-Path -Relative $_.FullName
    })
    $linkCount = 0
    foreach ($markdownPath in $markdownPaths) {
        $content = Get-Content -Raw $markdownPath
        $fenceCount = ([regex]::Matches($content, '(?m)^```')).Count
        if ($fenceCount % 2 -ne 0) { throw "Unbalanced code fence: $markdownPath" }
        foreach ($match in [regex]::Matches($content, '\[[^\]]+\]\((?<target>[^)#]+)(?:#[^)]+)?\)')) {
            $target = $match.Groups['target'].Value
            if ($target -match '^(https?://|#)') { continue }
            $resolvedTarget = Join-Path (Split-Path $markdownPath) $target
            if (-not (Test-Path -LiteralPath $resolvedTarget)) {
                throw "Broken local link: $markdownPath -> $target"
            }
            $linkCount++
        }
    }
    Write-Output "PASS: $linkCount local Markdown links and balanced code fences"

    git diff --check $base $head --
    if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed' }
    Write-Output "PASS: git diff --check $base $head"
}
finally {
    Pop-Location
}
