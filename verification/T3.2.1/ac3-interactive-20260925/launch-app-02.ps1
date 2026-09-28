$ErrorActionPreference = "Stop"
$runId = "02"
$desktop = Join-Path $env:USERPROFILE "Desktop"
$mount = Join-Path $desktop "ac3-interactive-20260925"
$package = Join-Path $desktop "NewManga"
$exe = Join-Path $package "NewManga.exe"
$manifest = Join-Path $mount "build3-fixed-cwd-artifact-manifest.sha256"
$stdoutPath = Join-Path $mount ("app-run-" + $runId + ".raw.stdout.log")
$stderrPath = Join-Path $mount ("app-run-" + $runId + ".raw.stderr.log")
$processPath = Join-Path $mount ("app-run-" + $runId + ".process.log")
$baselinePath = Join-Path $mount "sandbox-baseline.log"
$launchAudit = Join-Path $mount ("guest-launch-" + $runId + ".log")
"SCRIPT_ENTERED=$([DateTime]::UtcNow.ToString('o'))" | Set-Content -LiteralPath $launchAudit -Encoding UTF8
if (-not (Test-Path -LiteralPath $exe)) { throw "Mapped package executable not found: $exe" }
$exeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
$manifestLine = Get-Content -LiteralPath $manifest | Where-Object { $_ -match '\s+NewManga\.exe$' } | Select-Object -First 1
$expectedHash = (($manifestLine -split '\s+')[0]).ToLowerInvariant()
$hashMatch = ($exeHash -eq $expectedHash)
$os = Get-CimInstance Win32_OperatingSystem
$baseline = @(
  "RUN_ID=$runId"
  "UTC_START=$([DateTime]::UtcNow.ToString('o'))"
  "COMPUTERNAME=$env:COMPUTERNAME"
  "USER=$(& whoami.exe)"
  "OS_CAPTION=$($os.Caption)"
  "OS_VERSION=$($os.Version)"
  "OS_BUILD=$($os.BuildNumber)"
  "OS_ARCH=$($os.OSArchitecture)"
  "POWERSHELL_VERSION=$($PSVersionTable.PSVersion)"
  "PATH=$env:PATH"
  "PACKAGE_EXE=$exe"
  "PACKAGE_EXE_SHA256=$exeHash"
  "PACKAGE_MANIFEST_SHA256=$expectedHash"
  "PACKAGE_HASH_MATCH=$hashMatch"
  "COMMAND_LINE=$exe (normal GUI launch; no --smoke-test)"
  "DATA_ROOT=$env:LOCALAPPDATA\New Manga"
  "DATA_ROOT_EXISTS_BEFORE=$(Test-Path -LiteralPath (Join-Path $env:LOCALAPPDATA 'New Manga'))"
)
foreach ($name in @("python", "py", "git")) {
  $whereOutput = @(& "$env:WINDIR\System32\where.exe" $name 2>&1)
  $whereExit = $LASTEXITCODE
  $baseline += "WHERE_$($name.ToUpperInvariant())_EXIT=$whereExit"
  $baseline += "WHERE_$($name.ToUpperInvariant())_OUTPUT=$($whereOutput -join ' | ')"
}
$fixtureDir = Join-Path $desktop "codex-t321-ac3-fixture-20260925"
$baseline += "FIXTURE_DIR=$fixtureDir"
$baseline += "FIXTURE_FILES=$((Get-ChildItem -LiteralPath $fixtureDir -File | ForEach-Object { $_.Name + ':' + (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }) -join ' | ')"
$baseline | Set-Content -LiteralPath $baselinePath -Encoding UTF8
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.WorkingDirectory = $package
$psi.Arguments = ""
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$startedAt = [DateTime]::UtcNow
$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
$started = $proc.Start()
if (-not $started) { throw "Could not start packaged GUI executable" }
$childProcessId = $proc.Id
$stdoutTask = $proc.StandardOutput.ReadToEndAsync()
$stderrTask = $proc.StandardError.ReadToEndAsync()
$proc.WaitForExit()
$stdout = $stdoutTask.GetAwaiter().GetResult()
$stderr = $stderrTask.GetAwaiter().GetResult()
$stdout | Set-Content -LiteralPath $stdoutPath -Encoding UTF8
$stderr | Set-Content -LiteralPath $stderrPath -Encoding UTF8
@(
  "RUN_ID=$runId"
  "UTC_START=$($startedAt.ToString('o'))"
  "UTC_END=$([DateTime]::UtcNow.ToString('o'))"
  "PID=$childProcessId"
  "EXE=$exe"
  "ARGUMENTS=(empty)"
  "HASH_MATCH=$hashMatch"
  "EXIT_CODE=$($proc.ExitCode)"
  "PROCESS_STILL_RUNNING=$([bool](Get-Process -Id $childProcessId -ErrorAction SilentlyContinue))"
) | Set-Content -LiteralPath $processPath -Encoding UTF8
