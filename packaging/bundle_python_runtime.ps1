# PLUGIN-RUNTIME-PACKAGED-PYTHON-1 — shared "bundle a relocatable Python runtime"
# helper for the packaging scripts.
#
# The frozen sidecar is not a Python CLI, so plugin hooks need a real
# interpreter next to it. `_hook_interpreter()` looks for
# `<sidecar>/python/python.exe` (after NEWMANGA_PLUGIN_PYTHON / a sibling
# python.exe), so this helper copies a COMPLETE relocatable runtime into
# `<Bundle>/python/`:
#
#   python.exe, python3.dll, python3XX.dll, vcruntime*.dll, *.pyd (root)
#   DLLs/ (extension modules), Lib/ (standard library, site-packages excluded)
#
# It deliberately does NOT copy Lib/site-packages: third-party packages are
# not part of the plugin-hook ABI (hooks use the stdlib only) and would bloat
# the installer; if a future release needs them this helper must grow an
# explicit allowlist.
#
# Fail-closed: a missing python.exe / python3XX.dll / Lib directory throws.

function Copy-PluginPythonRuntime {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Bundle,
        [Parameter(Mandatory = $true)][string]$RuntimeDir
    )

    $source = (Resolve-Path -LiteralPath $RuntimeDir).Path
    $pythonExe = Join-Path $source "python.exe"
    if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
        throw "plugin python runtime is missing python.exe: $source"
    }
    $target = Join-Path $Bundle "python"
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    New-Item -ItemType Directory -Path $target -Force | Out-Null

    # 1) root executables, runtime DLLs and built-in extension modules
    Copy-Item -LiteralPath $pythonExe -Destination $target -Force
    foreach ($pattern in @("python3*.dll", "python3*.pyd", "vcruntime*.dll", "*.pyd")) {
        foreach ($file in @(Get-ChildItem -LiteralPath $source -Filter $pattern -File -ErrorAction SilentlyContinue)) {
            Copy-Item -LiteralPath $file.FullName -Destination $target -Force
        }
    }

    # 2) DLLs + standard library (site-packages intentionally excluded)
    $dlls = Join-Path $source "DLLs"
    if (Test-Path -LiteralPath $dlls -PathType Container) {
        Copy-Item -LiteralPath $dlls -Destination (Join-Path $target "DLLs") -Recurse -Force
    }
    $lib = Join-Path $source "Lib"
    if (-not (Test-Path -LiteralPath $lib -PathType Container)) {
        throw "plugin python runtime is missing Lib/: $source"
    }
    $libTarget = Join-Path $target "Lib"
    New-Item -ItemType Directory -Path $libTarget -Force | Out-Null
    Get-ChildItem -LiteralPath $lib -Force | Where-Object {
        $_.Name -notin @("site-packages", "test", "tests", "idlelib", "tkinter", "turtledemo")
    } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $libTarget -Recurse -Force
    }

    # 3) record the interpreter location for the launcher / audit
    Set-Content -LiteralPath (Join-Path $target "plugin-python.txt") -Encoding utf8 -Value @(
        "PLUGIN-RUNTIME-PACKAGED-PYTHON-1 bundled runtime"
        "Interpreter: python/python.exe (relative to the sidecar)"
        "Source: $source"
        "Launcher may set NEWMANGA_PLUGIN_PYTHON to this interpreter; _hook_interpreter() also resolves python/python.exe"
    )

    # 4) sha256 manifest of the bundled runtime (release auditability)
    $manifest = Join-Path $target "plugin-python.sha256"
    $lines = Get-ChildItem -LiteralPath $target -Recurse -File |
        Where-Object { $_.Name -ne "plugin-python.sha256" } |
        Sort-Object FullName |
        ForEach-Object {
            $relative = $_.FullName.Substring($target.Length + 1).Replace("\", "/")
            $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            "$hash  $relative"
        }
    Set-Content -LiteralPath $manifest -Encoding ascii -Value $lines
    Write-Host "bundle_python_runtime: sha256 manifest ($($lines.Count) files) -> $manifest"

    # 5) fail-closed smoke: the copied runtime must import the modules the
    #    plugin runtime depends on, with a minimal PATH (no host PYTHONHOME).
    $smoke = & (Join-Path $target "python.exe") -I -c "import socket, ssl, sqlite3, json, hashlib; print('plugin-python-smoke-ok')" 2>&1
    if ($LASTEXITCODE -ne 0 -or ($smoke -join "`n") -notmatch "plugin-python-smoke-ok") {
        throw "bundled python runtime failed its smoke check (exit=$LASTEXITCODE): $smoke"
    }
    Write-Host "bundle_python_runtime: OK -> $target (smoke import socket/ssl/sqlite3/json/hashlib)"
}
