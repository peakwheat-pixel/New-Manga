$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$artifactRoot = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926'
$simulationRoot = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\host-simulation-20260926'
$sourceDist = Join-Path $artifactRoot 'build2\dist'
$stage = Join-Path $simulationRoot '程序目录只读'
$program = Join-Path $stage 'NewManga'
$logs = Join-Path $simulationRoot 'logs'
$profile = Join-Path $simulationRoot '用户配置隔离'
$localAppData = Join-Path $profile 'AppData\Local'
$roaming = Join-Path $profile 'AppData\Roaming'
$temp = Join-Path $simulationRoot 'temp'
$fixtureDir = Join-Path $simulationRoot 'fixture'
$stdout = Join-Path $logs 'app.stdout.log'
$stderr = Join-Path $logs 'app.stderr.log'
$launchJson = Join-Path $logs 'process-start.json'
$exitJson = Join-Path $logs 'process-exit.json'
if (Test-Path -LiteralPath $simulationRoot) { throw "Refusing to reuse simulation output: $simulationRoot" }
if (!(Test-Path -LiteralPath $sourceDist)) { throw "Missing fixed Build2 input: $sourceDist" }
New-Item -ItemType Directory -Path $simulationRoot,$stage,$program,$logs,$localAppData,$roaming,$temp,$fixtureDir -Force | Out-Null
Copy-Item -Path (Join-Path $sourceDist '*') -Destination $program -Recurse

# Protect only this newly-created staged copy; retain SYSTEM/admin recovery access.
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$acl = Get-Acl -LiteralPath $stage
$acl.SetAccessRuleProtection($true, $false)
$acl.Access | ForEach-Object { [void]$acl.RemoveAccessRuleAll($_) }
$inherit = [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [Security.AccessControl.InheritanceFlags]::ObjectInherit
$prop = [Security.AccessControl.PropagationFlags]::None
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($identity.User, [Security.AccessControl.FileSystemRights]::ReadAndExecute, $inherit, $prop, [Security.AccessControl.AccessControlType]::Allow))
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new('S-1-5-18'), [Security.AccessControl.FileSystemRights]::FullControl, $inherit, $prop, [Security.AccessControl.AccessControlType]::Allow))
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'), [Security.AccessControl.FileSystemRights]::FullControl, $inherit, $prop, [Security.AccessControl.AccessControlType]::Allow))
Set-Acl -LiteralPath $stage -AclObject $acl
$writeProbe = Join-Path $stage 'read-only-write-probe.tmp'
try { [IO.File]::WriteAllText($writeProbe, 'should-not-be-created'); $writeDenied = $false; Remove-Item -LiteralPath $writeProbe -Force } catch [UnauthorizedAccessException] { $writeDenied = $true } catch { if ($_.Exception -is [System.IO.IOException] -and $_.Exception.Message -match 'denied|access') { $writeDenied = $true } else { throw } }
if (!$writeDenied) { throw 'Read-only program directory write probe unexpectedly succeeded' }

# Generate a synthetic test page outside the package and isolated user-data root.
Add-Type -AssemblyName System.Drawing
$imagePath = Join-Path $fixtureDir '漫画页-测试.png'
$bitmap = [Drawing.Bitmap]::new(520,760)
$graphics = [Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([Drawing.Color]::White)
$pen = [Drawing.Pen]::new([Drawing.Color]::FromArgb(35,35,35), 4)
$graphics.DrawRectangle($pen, 24, 24, 472, 305)
$graphics.FillEllipse([Drawing.Brushes]::LightSkyBlue, 90, 70, 135, 170)
$graphics.FillEllipse([Drawing.Brushes]::LightPink, 285, 86, 130, 150)
$graphics.DrawRectangle($pen, 24, 350, 472, 370)
$font = [Drawing.Font]::new('Arial', 22)
$graphics.DrawString('Synthetic release-gate page', $font, [Drawing.Brushes]::Black, 48, 395)
$graphics.DrawString('No user artwork or private source files', $font, [Drawing.Brushes]::DarkSlateGray, 48, 445)
$bitmap.Save($imagePath, [Drawing.Imaging.ImageFormat]::Png)
$font.Dispose(); $pen.Dispose(); $graphics.Dispose(); $bitmap.Dispose()
$fixtureHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $imagePath).Hash.ToLowerInvariant()

$os = Get-CimInstance Win32_OperatingSystem
$pathValue = "$env:SystemRoot\System32;$env:SystemRoot"
$machine = [ordered]@{
  captured_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
  computer = $env:COMPUTERNAME
  user_sid = $identity.User.Value
  os_caption = $os.Caption
  os_version = $os.Version
  os_build = $os.BuildNumber
  os_architecture = $os.OSArchitecture
  app_source_head = '08f9bd85137965df922db524bc92917af513bd24'
  app_exe = (Join-Path $program 'NewManga.exe')
  app_cwd = $program
  data_root_expected = (Join-Path $localAppData 'New Manga')
  localappdata_override = $localAppData
  program_directory_acl_write_probe = 'DENIED'
  path_value = $pathValue
  python_visible_on_path = $false
  py_visible_on_path = $false
  git_visible_on_path = $false
  source_fixture = $imagePath
  source_fixture_sha256_before = $fixtureHash
  log_directory = $logs
  claim_scope = 'User-approved local host simulation; not a separate clean Windows machine or Sandbox.'
}
$envReport = Join-Path $logs 'host-environment.json'
$machine | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $envReport -Encoding utf8

# Launch with a deliberately minimal PATH and per-run data/profile/temp roots.
$env:PATH = $pathValue
$env:LOCALAPPDATA = $localAppData
$env:APPDATA = $roaming
$env:TEMP = $temp
$env:TMP = $temp
@('NEWMANGA_DATA_ROOT','PYTHONPATH','PYTHONHOME','PYTHONUSERBASE','QML2_IMPORT_PATH','QML_IMPORT_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','PYINSTALLER_CONFIG_DIR') | ForEach-Object { Remove-Item -LiteralPath "Env:$_" -ErrorAction SilentlyContinue }
$timer = [Diagnostics.Stopwatch]::StartNew()
$startUtc = [DateTimeOffset]::UtcNow
$exe = Join-Path $program 'NewManga.exe'
$p = Start-Process -FilePath $exe -WorkingDirectory $program -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$ready = $false
$windowHandle = '0x0'
while ($timer.Elapsed.TotalSeconds -lt 60) {
  try { $p.Refresh(); $windowHandle = ('0x{0:X}' -f $p.MainWindowHandle.ToInt64()) } catch {}
  if ($p.HasExited) { break }
  if ($p.MainWindowHandle -ne [IntPtr]::Zero) { $ready = $true; break }
  Start-Sleep -Milliseconds 200
}
$timer.Stop()
$record = [ordered]@{
  started_at_utc = $startUtc.ToString('o')
  window_handle_ready_at_utc = if ($ready) { [DateTimeOffset]::UtcNow.ToString('o') } else { $null }
  pid = $p.Id
  exe = $exe
  working_directory = $program
  command_line = '"' + $exe + '" (no arguments)'
  effective_path = $env:PATH
  localappdata = $env:LOCALAPPDATA
  app_window_handle = $windowHandle
  seconds_to_main_window_handle = [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000, 3)
  main_window_handle_ready = $ready
  stdout = $stdout
  stderr = $stderr
}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $launchJson -Encoding utf8
Write-Output ('LAUNCH_RECORD=' + $launchJson)
Write-Output ('PID=' + $p.Id + '; WINDOW_HANDLE=' + $windowHandle + '; READY=' + $ready + '; ELAPSED_SECONDS=' + [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000,3))
if ($p.HasExited) {
  $exitCode = $p.ExitCode
  [ordered]@{pid=$p.Id; exited_at_utc=[DateTimeOffset]::UtcNow.ToString('o'); exit_code=$exitCode; outcome='exited before interaction'} | ConvertTo-Json | Set-Content -LiteralPath $exitJson -Encoding utf8
  exit $exitCode
}
$p.WaitForExit()
$exitCode = $p.ExitCode
[ordered]@{pid=$p.Id; exited_at_utc=[DateTimeOffset]::UtcNow.ToString('o'); exit_code=$exitCode; outcome='process exit observed by launcher'} | ConvertTo-Json | Set-Content -LiteralPath $exitJson -Encoding utf8
Write-Output ('PROCESS_EXIT=' + $exitCode)
exit $exitCode
