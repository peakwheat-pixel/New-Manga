[CmdletBinding()] param([string]$PackageDir,[string]$InstallDir=$( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/RELEASE-PACKAGE-1/install' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/RELEASE-PACKAGE-1/install' } ),[string]$Out=$( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'worktrees/RELEASE-PACKAGE-1/verification/RELEASE-PACKAGE-1/smoke/install-verify.json' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'worktrees/RELEASE-PACKAGE-1/verification/RELEASE-PACKAGE-1/smoke/install-verify.json' } ))
$ErrorActionPreference='Stop'
if([string]::IsNullOrWhiteSpace($PackageDir)){$PackageDir=(Get-ChildItem $( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/RELEASE-PACKAGE-1/out' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/RELEASE-PACKAGE-1/out' } ) -Directory -Filter 'NewManga-*win-x64'|Select-Object -First 1).FullName}
New-Item -ItemType Directory -Force (Split-Path $Out)|Out-Null
$lic=@('LICENSE','NOTICE.md','THIRD_PARTY_LICENSES.md')
& (Join-Path $PSScriptRoot 'install.ps1') -PackageDir $PackageDir -InstallDir $InstallDir -SkipBackup|Out-Null
$firstOk=Test-Path (Join-Path $InstallDir 'app/NewManga.App.exe')
$licOk=$true; foreach($n in $lic){if((Get-FileHash (Join-Path $PackageDir $n)).Hash -ne (Get-FileHash (Join-Path $InstallDir $n)).Hash){$licOk=$false}}
& (Join-Path $PSScriptRoot 'install.ps1') -PackageDir $PackageDir -InstallDir $InstallDir -SkipBackup|Out-Null
$secondOk=Test-Path (Join-Path $InstallDir 'app/NewManga.App.exe')
& (Join-Path $PSScriptRoot 'uninstall.ps1') -InstallDir $InstallDir|Out-Null
$u1=(-not (Test-Path $InstallDir)) -and (@(Get-Process NewManga.App -ErrorAction SilentlyContinue).Count -eq 0)
& (Join-Path $PSScriptRoot 'uninstall.ps1') -InstallDir $InstallDir|Out-Null
$u2=(-not (Test-Path $InstallDir))
$summary=[ordered]@{ac='AC4a';package_dir=$PackageDir;install_dir=$InstallDir;install_first=$firstOk;install_second_idempotent=$secondOk;license_byte_identical=$licOk;uninstall_first_residue_free=$u1;uninstall_second_idempotent=$u2;residual_processes=@(Get-Process NewManga.App -ErrorAction SilentlyContinue).Count;install_dir_after=(Test-Path $InstallDir);data_root_untouched=$true;generated_at_utc=[DateTime]::UtcNow.ToString('o')}
$summary|ConvertTo-Json -Depth 4|Set-Content $Out -Encoding utf8; $summary|ConvertTo-Json -Compress
