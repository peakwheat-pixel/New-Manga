# probe-process-tree.ps1
# Diagnostics script for AC1: inspect all owned processes, command lines, working sets, and webview2 process types.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = '',
    [int]$SettleSeconds = 40
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]

if (-not $OutDir) {
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    $OutDir = Join-Path $RepoRoot "verification\P20-MEM-OPT-1\ac1-probe-$ts"
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'probe-trace.log'
$detailJson = Join-Path $OutDir 'process-tree.json'

function T([string]$m) {
    $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m
    $l | Add-Content $trace -Encoding utf8
    Write-Host $l
}

$launcherCode = @"
using System;
using System.IO;
using System.Runtime.InteropServices;
public class DesktopLauncherProbe {
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

    public static int StartProcess(string exePath, string workDir, string outFile, string errFile, string desktop = "WinSta0\\Default") {
        STARTUPINFO si = new STARTUPINFO();
        si.cb = Marshal.SizeOf(si);
        si.lpDesktop = desktop;
        si.dwFlags = 0x00000100; // STARTF_USESTDHANDLES

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
}
"@
if (-not ([System.Management.Automation.PSTypeName]'DesktopLauncherProbe').Type) {
    Add-Type -TypeDefinition $launcherCode
}

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20ac1-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'
$outLog = Join-Path $OutDir 'app-out.log'

T "Starting probe: exe=$exe iso=$iso settle=${SettleSeconds}s"
$rootPid = [DesktopLauncherProbe]::StartProcess($exe, (Split-Path $exe), $outLog, $errLog)
if ($rootPid -le 0) {
    T "FAILED to start process, err=$rootPid"
    exit 1
}
T "Root pid=$rootPid"

$dl = (Get-Date).AddSeconds(30)
$win = $false
while ((Get-Date) -lt $dl) {
    Start-Sleep -Milliseconds 300
    try {
        $p = Get-Process -Id $rootPid -ErrorAction SilentlyContinue
        if (-not $p) { break }
        $r = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        if ($r.FindFirst($TS::Children, $c)) { $win = $true; break }
    } catch {}
}
T "window_found=$win"

T "Waiting ${SettleSeconds}s for settle..."
Start-Sleep -Seconds $SettleSeconds

function Get-OwnedProcessesWithDetails([int]$rootPid) {
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

$ownedProcs = Get-OwnedProcessesWithDetails $rootPid
$records = @()
$totalWs = 0
$wvTotalWs = 0
$wvCount = 0

foreach ($op in $ownedProcs) {
    $pidNum = [int]$op.ProcessId
    $pr = Get-Process -Id $pidNum -ErrorAction SilentlyContinue
    $ws = 0
    if ($pr) {
        try { $ws = $pr.WorkingSet64 } catch {}
    }
    $totalWs += $ws
    $cmd = [string]$op.CommandLine
    
    $wvType = "non-webview"
    $subType = ""
    if ($op.Name -eq 'msedgewebview2.exe') {
        $wvCount++
        $wvTotalWs += $ws
        if ($cmd -match '--type=([^\s]+)') {
            $wvType = $matches[1]
        } else {
            $wvType = "browser (embedded main)"
        }
        if ($cmd -match '--utility-sub-type=([^\s]+)') {
            $subType = $matches[1]
        }
    }

    $rec = [PSCustomObject]@{
        ProcessId = $pidNum
        ParentProcessId = [int]$op.ParentProcessId
        Name = $op.Name
        WorkingSetMB = [math]::Round($ws / 1MB, 2)
        WebViewType = $wvType
        UtilitySubType = $subType
        CommandLine = $cmd
    }
    $records += $rec
    T ("PROC {0,-18} pid={1,-6} parent={2,-6} ws={3,6} MB  wvType={4} {5}" -f $op.Name, $pidNum, $op.ParentProcessId, $rec.WorkingSetMB, $wvType, $subType)
}

T ("TOTAL_OWNED_COUNT = {0}" -f $records.Count)
T ("TOTAL_WORKING_SET = {0:N1} MB" -f ($totalWs / 1MB))
T ("WEBVIEW_COUNT     = {0}" -f $wvCount)
T ("WEBVIEW_TOTAL_WS  = {0:N1} MB" -f ($wvTotalWs / 1MB))

$records | ConvertTo-Json -Depth 5 | Set-Content $detailJson -Encoding utf8

# Clean up
$p = Get-Process -Id $rootPid -ErrorAction SilentlyContinue
if ($p) {
    $p.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 2
    Stop-Process -Id $rootPid -Force -ErrorAction SilentlyContinue
}
foreach ($r in $records) {
    Get-Process -Id $r.ProcessId -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
T "Cleanup complete."
