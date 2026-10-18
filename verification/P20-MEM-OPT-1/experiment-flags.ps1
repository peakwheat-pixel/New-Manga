# experiment-flags.ps1
# Test different WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS and trim strategies.
param(
    [string]$ArgsToTest = "",
    [switch]$DoTrim,
    [int]$SettleSeconds = 12
)
$ErrorActionPreference = 'Continue'
$RepoRoot = 'G:\CODEX\New Manga'

$launcherCode = @"
using System;
using System.IO;
using System.Runtime.InteropServices;
public class ExperimentLauncher {
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct STARTUPINFO {
        public int cb;
        public string lpReserved;
        public string lpDesktop;
        public string lpTitle;
        public int dwX;
        public int dwY;
        public int dwXSize;
        public int dwYSize;
        public int dwXCountChars;
        public int dwYCountChars;
        public int dwFillAttribute;
        public int dwFlags;
        public short wShowWindow;
        public short cbReserved2;
        public IntPtr lpReserved2;
        public IntPtr hStdInput;
        public IntPtr hStdOutput;
        public IntPtr hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct PROCESS_INFORMATION {
        public IntPtr hProcess;
        public IntPtr hThread;
        public int dwProcessId;
        public int dwThreadId;
    }

    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern bool CreateProcess(
        string lpApplicationName,
        string lpCommandLine,
        IntPtr lpProcessAttributes,
        IntPtr lpThreadAttributes,
        bool bInheritHandles,
        uint dwCreationFlags,
        IntPtr lpEnvironment,
        string lpCurrentDirectory,
        ref STARTUPINFO lpStartupInfo,
        out PROCESS_INFORMATION lpProcessInformation);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool CloseHandle(IntPtr hObject);

    [DllImport("psapi.dll", SetLastError = true)]
    public static extern bool EmptyWorkingSet(IntPtr hProcess);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr OpenProcess(uint dwDesiredAccess, bool bInheritHandle, int dwProcessId);

    public static int StartProcess(string exePath, string workDir, string outFile, string errFile, string desktop = "WinSta0\\Default") {
        STARTUPINFO si = new STARTUPINFO();
        si.cb = Marshal.SizeOf(si);
        si.lpDesktop = desktop;
        si.dwFlags = 0x00000100;

        FileStream outStream = new FileStream(outFile, FileMode.Create, FileAccess.Write, FileShare.ReadWrite | FileShare.Inheritable);
        FileStream errStream = new FileStream(errFile, FileMode.Create, FileAccess.Write, FileShare.ReadWrite | FileShare.Inheritable);
        si.hStdOutput = outStream.SafeFileHandle.DangerousGetHandle();
        si.hStdError = errStream.SafeFileHandle.DangerousGetHandle();
        si.hStdInput = IntPtr.Zero;

        PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
        bool ok = CreateProcess(null, exePath, IntPtr.Zero, IntPtr.Zero, true, 0, IntPtr.Zero, workDir, ref si, out pi);
        int err = Marshal.GetLastWin32Error();

        outStream.Dispose();
        errStream.Dispose();
        if (pi.hProcess != IntPtr.Zero) CloseHandle(pi.hProcess);
        if (pi.hThread != IntPtr.Zero) CloseHandle(pi.hThread);

        if (!ok) return -err;
        return pi.dwProcessId;
    }

    public static bool TrimProcess(int pid) {
        IntPtr h = OpenProcess(0x001F0FFF, false, pid);
        if (h == IntPtr.Zero) return false;
        bool res = EmptyWorkingSet(h);
        CloseHandle(h);
        return res;
    }
}
"@
if (-not ([System.Management.Automation.PSTypeName]'ExperimentLauncher').Type) {
    Add-Type -TypeDefinition $launcherCode
}

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20exp-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso

if ($ArgsToTest) {
    $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = $ArgsToTest
    Write-Host "Set WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = $ArgsToTest"
} else {
    Remove-Item Env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS -ErrorAction SilentlyContinue
}

$outF = "$iso\out.log"; $errF = "$iso\err.log"
$rootPid = [ExperimentLauncher]::StartProcess($exe, (Split-Path $exe), $outF, $errF)
Write-Host "Launched rootPid=$rootPid"

# Wait for startup
$dl = (Get-Date).AddSeconds(20)
while ((Get-Date) -lt $dl) {
    Start-Sleep -Milliseconds 300
    if (Test-Path $errF) {
        $c = Get-Content $errF -Raw -ErrorAction SilentlyContinue
        if ($c -and $c -match 'm2rc1-title') { break }
    }
}

Start-Sleep -Seconds $SettleSeconds

function Get-OwnedProcesses([int]$rootPid) {
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name, CommandLine)
    $byParent = @{}
    $procMap = @{}
    foreach ($x in $all) {
        $pid2 = [int]$x.ParentProcessId
        $procMap[[int]$x.ProcessId] = $x
        if (-not $byParent.ContainsKey($pid2)) { $byParent[$pid2] = @() }
        $byParent[$pid2] += $x
    }
    
    $owned = New-Object System.Collections.ArrayList
    $queue = New-Object System.Collections.Queue
    if ($procMap.ContainsKey($rootPid)) {
        [void]$owned.Add($procMap[$rootPid])
    }
    $queue.Enqueue($rootPid)
    $seen = @{}
    $seen[$rootPid] = $true

    while ($queue.Count -gt 0) {
        $cur = [int]$queue.Dequeue()
        if ($byParent.ContainsKey($cur)) {
            foreach ($ch in $byParent[$cur]) {
                $chPid = [int]$ch.ProcessId
                if (-not $seen.ContainsKey($chPid)) {
                    $seen[$chPid] = $true
                    [void]$owned.Add($ch)
                    $queue.Enqueue($chPid)
                }
            }
        }
    }
    return $owned
}

if ($DoTrim) {
    Write-Host "Executing EmptyWorkingSet on all owned processes..."
    $procs = Get-OwnedProcesses $rootPid
    foreach ($p in $procs) {
        [ExperimentLauncher]::TrimProcess([int]$p.ProcessId) | Out-Null
    }
    Start-Sleep -Seconds 3
}

$procs = Get-OwnedProcesses $rootPid
$totalWs = 0
$m2 = 0; $cs = 0; $hb = 0; $wv = 0; $wvCount = 0

foreach ($op in $procs) {
    $pidNum = [int]$op.ProcessId
    $pr = Get-Process -Id $pidNum -ErrorAction SilentlyContinue
    $ws = 0
    if ($pr) {
        try { $ws = $pr.WorkingSet64 } catch {}
    }
    $totalWs += $ws
    switch ($op.Name) {
        'm2rc1-desktop.exe' { $m2 += $ws }
        'core_service.exe' { $cs += $ws }
        'host_bridge.exe' { $hb += $ws }
        'msedgewebview2.exe' { $wv += $ws; $wvCount++ }
    }
    Write-Host ("  {0,-18} pid={1,-6} ws={2,6:N1} MB" -f $op.Name, $pidNum, ($ws / 1MB))
}

Write-Host "--------------------------------------------------------"
Write-Host ("RESULT: total={0:N1} MB (m2={1:N1}, core={2:N1}, host_bridge={3:N1}, webview={4:N1} in {5} procs)" -f `
    ($totalWs / 1MB), ($m2 / 1MB), ($cs / 1MB), ($hb / 1MB), ($wv / 1MB), $wvCount)
Write-Host "--------------------------------------------------------"

# Cleanup
$p = Get-Process -Id $rootPid -ErrorAction SilentlyContinue
if ($p) {
    $p.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 1
    Stop-Process -Id $rootPid -Force -ErrorAction SilentlyContinue
}
foreach ($r in $procs) {
    Get-Process -Id $r.ProcessId -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
