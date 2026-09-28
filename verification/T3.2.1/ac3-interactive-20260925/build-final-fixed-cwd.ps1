$ErrorActionPreference = "Stop"
$wt = "G:\CODEX\New Manga.worktrees\T3.2.1-antigravity-repair-11"
$expectedHead = "8738c41d7215920935e6fa067d3740e69280cdc6"
$python = "G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312\Scripts\python.exe"
$evidence = "G:\CODEX\New Manga\verification\T3.2.1\ac3-interactive-20260925"
$buildScript = Join-Path $wt "packaging\build.ps1"
Set-Location -LiteralPath $wt
[Environment]::CurrentDirectory = $wt
$actualHead = (& git -C $wt rev-parse HEAD).Trim()
$status = @(& git -C $wt status --porcelain)
$psCwd = (Get-Location).Path
$nativeCwd = [Environment]::CurrentDirectory
if ($actualHead -ne $expectedHead) { throw "Unexpected source HEAD: $actualHead" }
if ($status.Count -ne 0) { throw "Source worktree is not clean: $($status -join '; ')" }
if ($psCwd -ne $wt -or $nativeCwd -ne $wt) { throw "Build working directory mismatch: PowerShell=$psCwd Native=$nativeCwd" }
& git -C $wt diff --quiet 188d72a9d144b8cab16f77757abc46318ac8e5e6 $expectedHead -- src packaging tests
$srcDiffExit = $LASTEXITCODE
@(
  "FIXED_SOURCE_HEAD=$actualHead"
  "SOURCE_WORKTREE_STATUS=CLEAN"
  "POWERSHELL_CWD=$psCwd"
  "NATIVE_CWD=$nativeCwd"
  "GIT_DIFF_188D72A_TO_8738C41_SRC_PACKAGING_TESTS_EXIT=$srcDiffExit"
  "EXACT_BUILD_COMMAND=& $buildScript -OutputDir <OUTPUT> -WorkDir <WORK> -PythonExe $python"
) | Set-Content -LiteralPath (Join-Path $evidence "build-fixed-cwd-binding.log") -Encoding UTF8
if ($srcDiffExit -ne 0) { throw "Source-path diff check failed" }
foreach ($n in 3,4) {
  $out = "C:\Users\49745\AppData\Local\Temp\codex-t321-ac3-20260925-build$n"
  $work = "C:\Users\49745\AppData\Local\Temp\codex-t321-ac3-20260925-work$n"
  if (Test-Path -LiteralPath $out) { throw "Build output path already exists: $out" }
  if (Test-Path -LiteralPath $work) { throw "Build work path already exists: $work" }
  $log = Join-Path $evidence "build$n-fixed-cwd.raw.log"
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
  Copy-Item -LiteralPath $manifest -Destination (Join-Path $evidence "build$n-fixed-cwd-artifact-manifest.sha256")
  $exeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
  Add-Content -LiteralPath $log -Value "NEW_MANGA_EXE_SHA256=$exeHash" -Encoding UTF8
  Add-Content -LiteralPath (Join-Path $evidence "build-fixed-cwd-binding.log") -Value ("BUILD" + $n + "_OUTPUT=" + $out + "; EXE_SHA256=" + $exeHash) -Encoding UTF8
}
$one = Join-Path $evidence "build3-fixed-cwd-artifact-manifest.sha256"
$two = Join-Path $evidence "build4-fixed-cwd-artifact-manifest.sha256"
$lines1 = Get-Content -LiteralPath $one
$lines2 = Get-Content -LiteralPath $two
$diff = Compare-Object -ReferenceObject $lines1 -DifferenceObject $lines2
$diff | Format-Table -AutoSize | Out-String | Set-Content -LiteralPath (Join-Path $evidence "build3-4-manifest-diff.raw.txt") -Encoding UTF8
"MANIFEST3_LINES=$($lines1.Count); MANIFEST4_LINES=$($lines2.Count); DIFF_LINES=$(@($diff).Count)" | Add-Content -LiteralPath (Join-Path $evidence "build-fixed-cwd-binding.log") -Encoding UTF8
