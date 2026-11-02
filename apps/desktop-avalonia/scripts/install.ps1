[CmdletBinding()] param(
  [Parameter(Mandatory=$true)][string]$PackageDir,
  [string]$InstallDir=$( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/FINAL-VALIDATION-1/install' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/FINAL-VALIDATION-1/install' } ),
  [string]$DataRoot=$(Join-Path $env:APPDATA 'com.newmanga.desktop'),
  [switch]$SkipBackup
)
$ErrorActionPreference='Stop'
if(-not (Test-Path (Join-Path $PackageDir 'app/NewManga.App.exe'))){throw "package app missing"}
# FINAL-VALIDATION-1 AC2: the Core sidecar must travel WITH the package and be
# discoverable through the packaged layout (<app dir>/core-sidecar), otherwise
# the installed app cannot reach the Python Core at all.
$pkgSidecar=Join-Path $PackageDir 'app/core-sidecar'
foreach($n in @('core_service.exe','host_bridge.exe')){if(-not (Test-Path (Join-Path $pkgSidecar $n))){throw "package Core sidecar missing: app/core-sidecar/$n"}}
if(Test-Path $InstallDir){Remove-Item $InstallDir -Recurse -Force}
New-Item -ItemType Directory -Force $InstallDir|Out-Null
Copy-Item (Join-Path $PackageDir '*') $InstallDir -Recurse -Force
$lic=@('LICENSE','NOTICE.md','THIRD_PARTY_LICENSES.md'); $ok=$true
foreach($n in $lic){if((Get-FileHash (Join-Path $PackageDir $n)).Hash -ne (Get-FileHash (Join-Path $InstallDir $n)).Hash){$ok=$false}}
$backup=$null
if(-not $SkipBackup -and (Test-Path $DataRoot)){ $backupDir=Join-Path $DataRoot 'backups'; New-Item -ItemType Directory -Force $backupDir|Out-Null; $backup=Join-Path $backupDir ("first-run-"+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss')+".zip"); Compress-Archive -Path (Join-Path $DataRoot '*') -DestinationPath $backup -CompressionLevel Optimal -ErrorAction SilentlyContinue }
$installedSidecar=Join-Path $InstallDir 'app/core-sidecar'
$modelsDir=Join-Path $installedSidecar 'models'
$sidecarFiles=if(Test-Path $installedSidecar){@(Get-ChildItem $installedSidecar -Recurse -File)}else{@()}
$versionJson=Get-Content (Join-Path $InstallDir 'VERSION.json') -Raw|ConvertFrom-Json
@{
  installed=$true
  install_dir=$InstallDir
  version=$versionJson.version
  variant=$versionJson.variant
  data_root=$DataRoot
  data_root_created=(-not (Test-Path $DataRoot))
  first_run_backup=$backup
  license_copy_ok=$ok
  exe=(Join-Path $InstallDir 'app/NewManga.App.exe')
  sidecar_bundled=(Test-Path (Join-Path $installedSidecar 'core_service.exe'))
  sidecar_files=$sidecarFiles.Count
  sidecar_bytes=if($sidecarFiles){($sidecarFiles|Measure-Object Length -Sum).Sum}else{0}
  models_bundled=(Test-Path $modelsDir)
}|ConvertTo-Json -Depth 3
