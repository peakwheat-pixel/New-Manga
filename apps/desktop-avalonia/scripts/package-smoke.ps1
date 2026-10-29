[CmdletBinding()] param([string]$PackageDir,[string]$OutDir=$( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'worktrees/RELEASE-PACKAGE-1/verification/RELEASE-PACKAGE-1/smoke' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'worktrees/RELEASE-PACKAGE-1/verification/RELEASE-PACKAGE-1/smoke' } ))
$ErrorActionPreference='Stop'
$install=$( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/RELEASE-PACKAGE-1/install' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/RELEASE-PACKAGE-1/install' } )
if([string]::IsNullOrWhiteSpace($PackageDir)){$PackageDir=(Get-ChildItem $( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/RELEASE-PACKAGE-1/out' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/RELEASE-PACKAGE-1/out' } ) -Directory -Filter 'NewManga-*win-x64'|Select-Object -First 1).FullName}
New-Item -ItemType Directory -Force $OutDir|Out-Null
$installJson=& (Join-Path $PSScriptRoot 'install.ps1') -PackageDir $PackageDir -InstallDir $install | ConvertFrom-Json
$exe=Join-Path $install 'app/NewManga.App.exe'
& (Join-Path $PSScriptRoot 'smoke.ps1') -Exe $exe -OutDir $OutDir -ExitAfterMs 10000 2>&1 | Tee-Object -FilePath (Join-Path $OutDir 'smoke-console.log') | Out-Null
$smokeCode=$LASTEXITCODE
$shot=Get-ChildItem $OutDir -Recurse -Filter '*.png'|Select-Object -First 1
$uninstallJson=& (Join-Path $PSScriptRoot 'uninstall.ps1') -InstallDir $install | ConvertFrom-Json
$residue=$uninstallJson.install_dir_exists -or $uninstallJson.processes -gt 0
$summary=[ordered]@{ac='AC4';install=$installJson;smoke_exit=$smokeCode;screenshot=if($shot){$shot.FullName}else{$null};uninstall=$uninstallJson;residue=$residue;unattended_scope='install -> launch -> window screenshot/no-console evidence -> exit -> uninstall; shelf semantic check is MANUAL_VERIFY item';generated_at_utc=[DateTime]::UtcNow.ToString('o')}
$summary|ConvertTo-Json -Depth 6|Set-Content (Join-Path $OutDir 'install-smoke.json') -Encoding utf8
$summary|ConvertTo-Json -Depth 4
