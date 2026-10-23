# PLUGIN-RUNTIME-PACKAGED-PYTHON-1 — verification for the bundled runtime.
#
# Copies a complete Python runtime the way `build_sidecar.ps1
# -BundlePythonRuntime` does, then proves:
#   1) `Copy-PluginPythonRuntime` produced python/python.exe + DLLs/Lib/pyd;
#   2) that copied interpreter boots with a MINIMAL PATH (no host Python env)
#      and imports the modules the hook runtime needs;
#   3) `_hook_interpreter()` resolves `<sidecar>/python/python.exe` under a
#      simulated frozen sidecar (the real packaged resolution branch).
#
# Usage:
#   pwsh -File packaging/m2ac5/verify_bundled_python.ps1 [-PythonRuntime <dir>] [-OutDir <dir>]

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)][string]$PythonRuntime = "C:\Python314",
    [Parameter(Mandatory = $false)][string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path

if (-not $OutDir) {
    $OutDir = Join-Path ([System.IO.Path]::GetTempPath()) ("nm-plugin-python-verify-" + [guid]::NewGuid().ToString("N").Substring(0, 8))
}
$sidecar = Join-Path $OutDir "core-sidecar"
New-Item -ItemType Directory -Path $sidecar -Force | Out-Null
# a fake sidecar executable so the runtime directory sits next to "python/",
# exactly like the frozen layout.
Set-Content -LiteralPath (Join-Path $sidecar "core-sidecar.exe") -Encoding ascii -Value "stub"

. (Join-Path $repoRoot "packaging/bundle_python_runtime.ps1")
Copy-PluginPythonRuntime -Bundle $sidecar -RuntimeDir $PythonRuntime

$python = Join-Path $sidecar "python/python.exe"
foreach ($required in @("python/python.exe", "python/plugin-python.txt", "python/Lib/os.py", "python/DLLs")) {
    if (-not (Test-Path -LiteralPath (Join-Path $sidecar $required))) {
        throw "bundled runtime layout incomplete: missing $required"
    }
}

# 2) minimal-PATH boot + required imports (no host Python on PATH)
$origPath = $env:PATH
try {
    $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
    $smoke = & $python -I -c "import socket, ssl, sqlite3, json, hashlib; print('bundled-runtime-ok')" 2>&1
    if ($LASTEXITCODE -ne 0 -or ($smoke -join "`n") -notmatch "bundled-runtime-ok") {
        throw "minimal-PATH smoke failed (exit=$LASTEXITCODE): $smoke"
    }

    # 3) frozen resolution: _hook_interpreter() must pick <sidecar>/python/python.exe
    $resolveScript = @"
import sys
from pathlib import Path
sys.path.insert(0, r'$repoRoot\src'.replace('\\', '\\\\'))
sys.frozen = True
sys.executable = r'$sidecar\core-sidecar.exe'
from infrastructure.plugins.service import _hook_interpreter
resolved = _hook_interpreter()
expected = r'$sidecar\python\python.exe'
assert Path(resolved) == Path(expected), f'unexpected interpreter: {resolved!r} (expected {expected!r})'
print('frozen-resolution-ok:', resolved)
"@
    $resolveFile = Join-Path $OutDir "resolve_check.py"
    Set-Content -LiteralPath $resolveFile -Encoding utf8 -Value $resolveScript
    $resolveOut = & (Join-Path $PythonRuntime "python.exe") -I $resolveFile 2>&1
    if ($LASTEXITCODE -ne 0 -or ($resolveOut -join "`n") -notmatch "frozen-resolution-ok") {
        throw "frozen resolution check failed (exit=$LASTEXITCODE): $resolveOut"
    }
    # 4) run a REAL sandboxed hook with the bundled interpreter (AppContainer)
    $hookScript = @"
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, r'$repoRoot\src'.replace('\\', '\\\\'))
from infrastructure.plugins.sandbox import AppContainerSandbox
from infrastructure.plugins.service import PluginService
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
root = Path(tempfile.mkdtemp(prefix='nm-bundled-hook-'))
plugin = root / 'plugins' / 'acme-bundled'
plugin.mkdir(parents=True)
(plugin / 'plugin.py').write_text("def after_detect(payload):\n    return {'bundled': True}\n", encoding='utf-8')
(plugin / 'manifest.json').write_text(json.dumps({'id': 'acme-bundled', 'name': 'b', 'version': '1.0.0', 'entry': 'plugin.py', 'hooks': ['after_detect'], 'permissions': []}), encoding='utf-8')
conn, _ = open_database(root / 'library.db', latest_known_schema_version=max(m.schema_version for m in default_migrations()))
MigrationRunner(conn, default_migrations()).apply_pending()
sandbox = AppContainerSandbox(interpreter=r'$sidecar\python\python.exe')
service = PluginService(conn, root / 'plugins', app_version='0.1.0', sandbox=sandbox, allow_unsandboxed=False)
try:
    service.set_global_enabled(True)
    service.set_plugin_enabled('acme-bundled', True)
    outcome = service.run_hook('after_detect', {})
    assert outcome['applied'] is True, outcome
    assert outcome['results'][0]['result'] == {'bundled': True}, outcome
    print('bundled-sandbox-hook-ok')
finally:
    sandbox.close()
    conn.close()
"@
    $hookFile = Join-Path $OutDir "hook_check.py"
    Set-Content -LiteralPath $hookFile -Encoding utf8 -Value $hookScript
    $hookOut = & $python -I $hookFile 2>&1
    if ($LASTEXITCODE -ne 0 -or ($hookOut -join "`n") -notmatch "bundled-sandbox-hook-ok") {
        throw "bundled sandbox hook failed (exit=$LASTEXITCODE): $hookOut"
    }
    Write-Output ($hookOut -join "`n")

    Write-Output "verify_bundled_python: OK ($sidecar)"
    Write-Output ($resolveOut -join "`n")
}
finally {
    $env:PATH = $origPath
}
