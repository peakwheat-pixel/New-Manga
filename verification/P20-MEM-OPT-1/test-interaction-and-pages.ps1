# test-interaction-and-pages.ps1
# Test four-page navigation and interaction responsiveness post-trim
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga'
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]

$launcherCode = @"
using System;
using System.IO;
using System.Runtime.InteropServices;
public class InteractionLauncher {
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
if (-not ([System.Management.Automation.PSTypeName]'InteractionLauncher').Type) {
    Add-Type -TypeDefinition $launcherCode
}

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20testint-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$outF = "$iso\out.log"; $errF = "$iso\err.log"

$rootPid = [InteractionLauncher]::StartProcess($exe, (Split-Path $exe), $outF, $errF)
Write-Host "Launched rootPid=$rootPid"

$dl = (Get-Date).AddSeconds(20)
$win = $null
while ((Get-Date) -lt $dl) {
    Start-Sleep -Milliseconds 300
    try {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        $h = $root.FindFirst($TS::Children, $c)
        if ($h) { $win = $h; break }
    } catch {}
}

if (-not $win) {
    Write-Host "Window not found!"
    exit 1
}
Write-Host "Window found: $($win.Current.Name)"

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

# Wait 6s initial settle
Start-Sleep -Seconds 6

# Trim all owned processes
Write-Host "Trimming all processes..."
$procs = Get-OwnedProcesses $rootPid
foreach ($p in $procs) {
    [InteractionLauncher]::TrimProcess([int]$p.ProcessId) | Out-Null
}
Start-Sleep -Seconds 2

# Measure 4-page navigation responsiveness
$pages = @('📚 书架', '🛠️ 工作台', '📖 阅读器', '⚙️ 设置', '📚 书架')
$latencies = @()

foreach ($pg in $pages) {
    $pc = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $pg)
    $btn = $win.FindFirst($TS::Descendants, $pc)
    if (-not $btn) {
        Write-Host "PAGE $pg NOT FOUND"
        continue
    }
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
    $sw.Stop()
    $lat = $sw.Elapsed.TotalMilliseconds
    $latencies += $lat
    Write-Host ("Navigated to '{0}' in {1:N1} ms" -f $pg, $lat)
    Start-Sleep -Milliseconds 600
}

# Measure memory after interactions
$postWs = 0
foreach ($p in (Get-OwnedProcesses $rootPid)) {
    $pr = Get-Process -Id ([int]$p.ProcessId) -ErrorAction SilentlyContinue
    if ($pr) { try { $postWs += $pr.WorkingSet64 } catch {} }
}
Write-Host ("Memory after interactions: {0:N1} MB" -f ($postWs / 1MB))

# Cleanup
if ($win) {
    $p = Get-Process -Id $rootPid -ErrorAction SilentlyContinue
    if ($p) {
        $p.CloseMainWindow() | Out-Null
        Start-Sleep -Seconds 1
        Stop-Process -Id $rootPid -Force -ErrorAction SilentlyContinue
    }
}
foreach ($r in (Get-OwnedProcesses $rootPid)) {
    Get-Process -Id $r.ProcessId -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}
