[CmdletBinding()] param([Parameter(Mandatory=$true)][string]$PackageDir,[string]$InstallDir='G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1/install',[string]$DataRoot=$(Join-Path $env:APPDATA 'com.newmanga.desktop'),[switch]$SkipBackup)
$ErrorActionPreference='Stop'
if(-not (Test-Path (Join-Path $PackageDir 'app/NewManga.App.exe'))){throw "package app missing"}
if(Test-Path $InstallDir){Remove-Item $InstallDir -Recurse -Force}
New-Item -ItemType Directory -Force $InstallDir|Out-Null
Copy-Item (Join-Path $PackageDir '*') $InstallDir -Recurse -Force
$lic=@('LICENSE','NOTICE.md','THIRD_PARTY_LICENSES.md'); $ok=$true
foreach($n in $lic){if((Get-FileHash (Join-Path $PackageDir $n)).Hash -ne (Get-FileHash (Join-Path $InstallDir $n)).Hash){$ok=$false}}
$backup=$null
if(-not $SkipBackup -and (Test-Path $DataRoot)){ $backupDir=Join-Path $DataRoot 'backups'; New-Item -ItemType Directory -Force $backupDir|Out-Null; $backup=Join-Path $backupDir ("first-run-"+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss')+".zip"); Compress-Archive -Path (Join-Path $DataRoot '*') -DestinationPath $backup -CompressionLevel Optimal -ErrorAction SilentlyContinue }
@{installed=$true;install_dir=$InstallDir;version=(Get-Content (Join-Path $InstallDir 'VERSION.json') -Raw|ConvertFrom-Json).version;data_root=$DataRoot;data_root_created=(-not (Test-Path $DataRoot));first_run_backup=$backup;license_copy_ok=$ok;exe=(Join-Path $InstallDir 'app/NewManga.App.exe')}|ConvertTo-Json -Depth 3
