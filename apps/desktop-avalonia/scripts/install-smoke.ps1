[CmdletBinding()] param([string]$PackageDir,[string]$InstallDir='G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1/install',[string]$Out='G:/CODEX/New Manga.workspace/worktrees/RELEASE-PACKAGE-1/verification/RELEASE-PACKAGE-1/smoke/install-smoke.json')
$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @"
using System;using System.Runtime.InteropServices;using System.Text;using System.Collections.Generic;
public static class WinGuard{public delegate bool EnumProc(IntPtr h,IntPtr l);[DllImport("user32.dll")]static extern bool EnumWindows(EnumProc p,IntPtr l);[DllImport("user32.dll")]static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);[DllImport("user32.dll",CharSet=CharSet.Unicode)]static extern int GetClassName(IntPtr h,StringBuilder s,int n);
public static int ConsoleWindows(uint pid){int n=0;EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);if(p==pid){var sb=new StringBuilder(64);GetClassName(h,sb,64);if(sb.ToString().Contains("Console"))n++;}return true;},IntPtr.Zero);return n;}}
"@
if([string]::IsNullOrWhiteSpace($PackageDir)){$PackageDir=(Get-ChildItem 'G:/CODEX/New Manga.workspace/task-envs/RELEASE-PACKAGE-1/out' -Directory -Filter 'NewManga-*win-x64'|Select-Object -First 1).FullName}
New-Item -ItemType Directory -Force (Split-Path $Out)|Out-Null
& (Join-Path $PSScriptRoot 'install.ps1') -PackageDir $PackageDir -InstallDir $InstallDir -SkipBackup|Out-Null
$exe=Join-Path $InstallDir 'app/NewManga.App.exe'
$p=Start-Process -FilePath $exe -ArgumentList '--exit-after=6000' -PassThru
$deadline=[DateTime]::UtcNow.AddSeconds(10); $handle=0
while([DateTime]::UtcNow -lt $deadline -and -not $p.HasExited){$p.Refresh(); if($p.MainWindowHandle -ne 0){$handle=[int64]$p.MainWindowHandle;break}; Start-Sleep -Milliseconds 100}
$console=[WinGuard]::ConsoleWindows([uint32]$p.Id)
$exited=$p.WaitForExit(15000); $code=if($exited){$p.ExitCode}else{-1}
if(-not $exited){$p.Kill()}
& (Join-Path $PSScriptRoot 'uninstall.ps1') -InstallDir $InstallDir|Out-Null
$summary=[ordered]@{ac='AC4b';launched_from_install_dir=$true;exe=$exe;window_handle_found=($handle -ne 0);window_handle=$handle;console_window_count=$console;exit_code=$code;exit_ok=($code -eq 0);residual_processes=@(Get-Process NewManga.App -ErrorAction SilentlyContinue).Count;install_dir_after=(Test-Path $InstallDir);sidecar_bundled=$false;generated_at_utc=[DateTime]::UtcNow.ToString('o')}
$summary|ConvertTo-Json -Depth 4|Set-Content $Out -Encoding utf8; $summary|ConvertTo-Json -Compress
