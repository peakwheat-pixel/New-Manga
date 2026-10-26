# DISPLAY-PERF-DECISION-1 / baseline — import REAL pages through the product's
# own native picker, without a human in the loop.
#
# The product import path is tauri_plugin_dialog -> IFileOpenDialog. This helper
# finds that dialog (class #32770, owned by the app process), writes the
# absolute path(s) into its file-name edit (control id 1148) and confirms with
# WM_COMMAND/IDOK — the same command the Open button sends.
#
# Modes:
#   -FileList <txt>   one quoted path per entry, space separated (multi-select)
#   -PathArg <path>   exactly one path
#   -CancelOnly       cancel any visible dialog owned by the process and exit
#   -NoCancel         do not cancel anything first (use right after the picker opens)
#
# Observes only + one synthetic confirmation; never edits product files.

param(
  [Parameter(Mandatory = $true)][int]$ProcessId,
  [string]$PathArg = "",
  [string]$FileList = "",
  [switch]$CancelOnly,
  [switch]$NoCancel,
  [int]$TimeoutMs = 20000
)

$ErrorActionPreference = "Continue"
Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class DpImp {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumWindowsProc cb, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetClassName(IntPtr hWnd, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr hWnd);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr hWnd, uint msg, IntPtr wParam, string lParam);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
  public static string ClassOf(IntPtr h) { var sb = new StringBuilder(256); GetClassName(h, sb, 256); return sb.ToString(); }
  public static string TextOf(IntPtr h) { var sb = new StringBuilder(512); GetWindowText(h, sb, 512); return sb.ToString(); }
  public static List<IntPtr> TopWindowsOf(uint pid) {
    var list = new List<IntPtr>();
    EnumWindows(delegate(IntPtr h, IntPtr p) { uint wp; GetWindowThreadProcessId(h, out wp); if (wp == pid) list.Add(h); return true; }, IntPtr.Zero);
    return list;
  }
  public static List<IntPtr> ChildrenOf(IntPtr parent) {
    var list = new List<IntPtr>();
    EnumChildWindows(parent, delegate(IntPtr h, IntPtr p) { list.Add(h); return true; }, IntPtr.Zero);
    return list;
  }
}
"@

function Now-Ms { [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() }

function Find-Dialog {
  foreach ($h in [DpImp]::TopWindowsOf([uint32]$ProcessId)) {
    if (-not [DpImp]::IsWindowVisible($h)) { continue }
    if ([DpImp]::ClassOf($h) -eq "#32770") { return $h }
  }
  return [IntPtr]::Zero
}

# ---- optional: cancel whatever dialog is open --------------------------
$canceled = 0
if (-not $NoCancel) {
  foreach ($h in [DpImp]::TopWindowsOf([uint32]$ProcessId)) {
    if ([DpImp]::IsWindowVisible($h) -and [DpImp]::ClassOf($h) -eq "#32770") {
      [void][DpImp]::PostMessage($h, 0x0111, [IntPtr]2, [IntPtr]::Zero)  # IDCANCEL
      $canceled++
    }
  }
  if ($canceled -gt 0) { Start-Sleep -Milliseconds 900 }
}
if ($CancelOnly) {
  Write-Output (ConvertTo-Json @{ ok = $true; canceled = $canceled; cancelOnly = $true } -Compress)
  exit 0
}

# ---- locate the open dialog -------------------------------------------
$deadline = (Now-Ms) + $TimeoutMs
$dlg = [IntPtr]::Zero
while ((Now-Ms) -lt $deadline -and $dlg -eq [IntPtr]::Zero) {
  $dlg = Find-Dialog
  if ($dlg -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 50 }
}
if ($dlg -eq [IntPtr]::Zero) {
  Write-Output (ConvertTo-Json @{ ok = $false; error = "dialog not found"; canceledPrevious = $canceled } -Compress)
  exit 4
}

# ---- file-name edit (control id 1148) ---------------------------------
$edit = [IntPtr]::Zero
foreach ($c in [DpImp]::ChildrenOf($dlg)) {
  if ([DpImp]::ClassOf($c) -eq "Edit" -and [DpImp]::GetDlgCtrlID($c) -eq 1148) { $edit = $c; break }
}
if ($edit -eq [IntPtr]::Zero) {
  Write-Output (ConvertTo-Json @{ ok = $false; error = "edit 1148 not found"; dlg = [string]$dlg } -Compress)
  exit 5
}

$value = $PathArg
if ($FileList) {
  $parts = @(Get-Content -LiteralPath $FileList | Where-Object { $_.Trim().Length -gt 0 } | ForEach-Object { '"' + $_.Trim() + '"' })
  $value = $parts -join " "
}
if (-not $value) {
  Write-Output (ConvertTo-Json @{ ok = $false; error = "no path given" } -Compress)
  exit 2
}

[void][DpImp]::SendMessage($edit, 0x000C, [IntPtr]::Zero, $value)  # WM_SETTEXT
Start-Sleep -Milliseconds 250
[void][DpImp]::PostMessage($dlg, 0x0111, [IntPtr]1, [IntPtr]::Zero)  # WM_COMMAND / IDOK
Start-Sleep -Milliseconds 1200
$stillOpen = [DpImp]::IsWindowVisible($dlg)

Write-Output (ConvertTo-Json @{
  ok = (-not $stillOpen)
  canceledPrevious = $canceled
  dlgHwnd = [string]$dlg
  dlgTitle = [DpImp]::TextOf($dlg)
  editHwnd = [string]$edit
  writtenChars = $value.Length
  valueHead = $(if ($value.Length -gt 200) { $value.Substring(0, 200) } else { $value })
  dialogStillOpen = $stillOpen
} -Compress)
