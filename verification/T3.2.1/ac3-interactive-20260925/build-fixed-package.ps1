$ErrorActionPreference = "Stop"
$evidence = Split-Path -Parent $MyInvocation.MyCommand.Path
$wt = "G:\CODEX\New Manga.worktrees\T3.2.1-antigravity-repair-11"
$expectedHead = "8738c41d7215920935e6fa067d3740e69280cdc6"
$python = "G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312\Scripts\python.exe"
$buildScript = Join-Path $wt "packaging\build.ps1"
$actualHead = (& git -C $wt rev-parse HEAD).Trim()
$status = @(& git -C $wt status --porcelain)
if ($actualHead -ne $expectedHead) { throw "Unexpected source HEAD: $actualHead" }
if ($status.Count -ne 0) { throw "Source worktree is not clean: $($status -join '; ')" }
& git -C $wt diff --quiet 188d72a9d144b8cab16f77757abc46318ac8e5e6 $expectedHead -- src packaging tests
$srcDiffExit = $LASTEXITCODE
@(
  "FIXED_SOURCE_HEAD=$actualHead"
  "SOURCE_WORKTREE_STATUS=CLEAN"
  "GIT_DIFF_188D72A_TO_8738C41_SRC_PACKAGING_TESTS_EXIT=$srcDiffExit"
  "BUILD_SCRIPT=$buildScript"
  "PYTHON=$python"
  "PYTHON_VERSION=$((& $python --version 2>&1 | Out-String).Trim())"
  "PYINSTALLER_VERSION=$((& $python -m PyInstaller --version 2>&1 | Out-String).Trim())"
  "PYSIDE6_VERSION=$((& $python -c 'import PySide6; print(PySide6.__version__)' 2>&1 | Out-String).Trim())"
) | Set-Content -LiteralPath (Join-Path $evidence "source-binding.log") -Encoding UTF8
& $python -m pip freeze 2>&1 | Set-Content -LiteralPath (Join-Path $evidence "build-environment-freeze.log") -Encoding UTF8
$freezeExit = $LASTEXITCODE
Add-Content -LiteralPath (Join-Path $evidence "source-binding.log") -Value "PIP_FREEZE_EXIT=$freezeExit" -Encoding UTF8
if ($srcDiffExit -ne 0 -or $freezeExit -ne 0) { throw "Source binding or environment snapshot check failed" }
foreach ($n in 1,2) {
  $out = "C:\Users\49745\AppData\Local\Temp\codex-t321-ac3-20260925-build$n"
  $work = "C:\Users\49745\AppData\Local\Temp\codex-t321-ac3-20260925-work$n"
  if (Test-Path -LiteralPath $out) { throw "Build output path already exists: $out" }
  if (Test-Path -LiteralPath $work) { throw "Build work path already exists: $work" }
  $log = Join-Path $evidence "build$n.raw.log"
  $exit = 0
  try {
    & $buildScript -OutputDir $out -WorkDir $work -PythonExe $python *>&1 | Tee-Object -FilePath $log
    if ($LASTEXITCODE -ne 0) { throw "build.ps1 returned native exit $LASTEXITCODE" }
  } catch {
    $exit = 1
    Add-Content -LiteralPath $log -Value ("BUILD_EXCEPTION=" + $_.ToString()) -Encoding UTF8
  }
  Add-Content -LiteralPath $log -Value "BUILD_SCRIPT_EXIT_CODE=$exit" -Encoding UTF8
  if ($exit -ne 0) { throw "Build $n failed; inspect $log" }
  $manifest = Join-Path $out "artifact-manifest.sha256"
  $exe = Join-Path $out "NewManga\NewManga.exe"
  if (-not (Test-Path -LiteralPath $manifest) -or -not (Test-Path -LiteralPath $exe)) { throw "Build $n artifact or manifest missing" }
  Copy-Item -LiteralPath $manifest -Destination (Join-Path $evidence "build$n-artifact-manifest.sha256")
  $exeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
  Add-Content -LiteralPath $log -Value "NEW_MANGA_EXE_SHA256=$exeHash" -Encoding UTF8
  Add-Content -LiteralPath (Join-Path $evidence "source-binding.log") -Value ("BUILD" + $n + "_OUTPUT=" + $out + "; EXE_SHA256=" + $exeHash) -Encoding UTF8
}
$lines1 = Get-Content -LiteralPath (Join-Path $evidence "build1-artifact-manifest.sha256")
$lines2 = Get-Content -LiteralPath (Join-Path $evidence "build2-artifact-manifest.sha256")
$diff = Compare-Object -ReferenceObject $lines1 -DifferenceObject $lines2
$diff | Format-Table -AutoSize | Out-String | Set-Content -LiteralPath (Join-Path $evidence "build-manifest-diff.raw.txt") -Encoding UTF8
"MANIFEST1_LINES=$($lines1.Count); MANIFEST2_LINES=$($lines2.Count); DIFF_LINES=$(@($diff).Count)" | Add-Content -LiteralPath (Join-Path $evidence "source-binding.log") -Encoding UTF8
