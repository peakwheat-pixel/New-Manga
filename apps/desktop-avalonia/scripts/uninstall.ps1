[CmdletBinding()] param([string]$InstallDir=$( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/RELEASE-PACKAGE-1/install' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/RELEASE-PACKAGE-1/install' } ),[string]$DataRoot=$(Join-Path $env:APPDATA 'com.newmanga.desktop'),[switch]$PurgeData)
$ErrorActionPreference='Stop'
Get-Process NewManga.App -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$InstallDir*" } | Stop-Process -Force -ErrorAction SilentlyContinue
if(Test-Path $InstallDir){Remove-Item $InstallDir -Recurse -Force}
if($PurgeData -and (Test-Path $DataRoot)){Remove-Item $DataRoot -Recurse -Force}
@{uninstalled=$true;install_dir=$InstallDir;install_dir_exists=(Test-Path $InstallDir);data_root=$DataRoot;data_root_exists=(Test-Path $DataRoot);processes=@(Get-Process NewManga.App -ErrorAction SilentlyContinue).Count}|ConvertTo-Json -Depth 3
