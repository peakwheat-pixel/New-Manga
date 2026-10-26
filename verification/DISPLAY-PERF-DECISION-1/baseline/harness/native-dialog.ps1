# DISPLAY-PERF-DECISION-1 / baseline — drive the app's NATIVE file-open dialog.
#
# The product's import path is a native Windows picker
# (tauri_plugin_dialog -> IFileOpenDialog), which the WebView cannot touch. This
# helper fills the dialog's file-name edit and confirms it, so a REAL import can
# run through the real code path without a human in the loop.
#
# Observability only + one synthetic confirmation; it never edits product files.
#
# Usage:
#   pwsh -File native-dialog.ps1 -ProcessId 1234 -Paths 'C:\a.jpg','C:\b.jpg' [-TimeoutMs 15000]

param(
  [Parameter(Mandatory = $true)][int]$ProcessId,
  [string[]]$Paths = @(),
  [string]$PathFile = "",
  [int]$TimeoutMs = 20000
)

if ($PathFile) {
  $Paths = @(Get-Content -LiteralPath $PathFile | Where-Object { $_.Trim().Length -gt 0 } | ForEach-Object { $_.Trim() })
}
if ($Paths.Count -eq 0) { Write-Output (ConvertTo-Json @{ ok = $false; error = "no paths given" } -Compress); exit 2 }

$ErrorActionPreference = "Continue"
Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public class DpDlg {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumWindowsProc cb, IntPtr lParam);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetClassName(IntPtr hWnd, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr hWnd);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr hWnd, uint msg, IntPtr wParam, string lParam);
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

  public static string ClassOf(IntPtr h) { var sb = new StringBuilder(256); GetClassName(h, sb, 256); return sb.ToString(); }
  public static string TextOf(IntPtr h) { var sb = new StringBuilder(512); GetWindowText(h, sb, 512); return sb.ToString(); }

  public static List<IntPtr> TopWindowsOf(uint pid) {
    var list = new List<IntPtr>();
    EnumWindows(delegate(IntPtr h, IntPtr p) {
      uint wp; GetWindowThreadProcessId(h, out wp);
      if (wp == pid) list.Add(h);
      return true;
    }, IntPtr.Zero);
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
$deadline = (Now-Ms) + $TimeoutMs

# ---- 1. locate the dialog window owned by the app process ---------------
$dlg = [IntPtr]::Zero
while ((Now-Ms) -lt $deadline -and $dlg -eq [IntPtr]::Zero) {
  foreach ($h in [DpDlg]::TopWindowsOf([uint32]$ProcessId)) {
    if (-not [DpDlg]::IsWindowVisible($h)) { continue }
    $cls = [DpDlg]::ClassOf($h)
    if ($cls -eq "#32770") { $dlg = $h; break }
    if ($cls -eq "Alternate Modal Top Most") { $dlg = $h; break }
  }
  if ($dlg -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 60 }
}
if ($dlg -eq [IntPtr]::Zero) {
  Write-Output (ConvertTo-Json @{ ok = $false; error = "dialog window not found"; pid = $ProcessId } -Compress)
  exit 4
}

$dlgTitle = [DpDlg]::TextOf($dlg)
$dlgClass = [DpDlg]::ClassOf($dlg)
$children = [DpDlg]::ChildrenOf($dlg)

# ---- 2. find the file-name edit (control id 1148 = cmb13/edit) ----------
$edit = [IntPtr]::Zero
$editInfo = @()
foreach ($c in $children) {
  $cls = [DpDlg]::ClassOf($c)
  $id = [DpDlg]::GetDlgCtrlID($c)
  $editInfo += @{ hwnd = [string]$c; cls = $cls; id = $id }
  if ($cls -eq "Edit" -and $id -eq 1148) { $edit = $c; break }
}
if ($edit -eq [IntPtr]::Zero) {
  foreach ($c in $children) { if ([DpDlg]::ClassOf($c) -eq "Edit") { $edit = $c; break } }
}
if ($edit -eq [IntPtr]::Zero) {
  Write-Output (ConvertTo-Json @{ ok = $false; error = "file-name edit not found"; dlgClass = $dlgClass; dlgTitle = $dlgTitle; children = $editInfo } -Depth 6 -Compress)
  exit 5
}

# ---- 3. write the absolute path(s) into the edit ------------------------
# A multi-select open dialog accepts one quoted path per line.
$value = ($Paths | ForEach-Object { '"' + $_ + '"' }) -join "`r`n"
if ($Paths.Count -eq 1) { $value = $Paths[0] }
[void][DpDlg]::SendMessage($edit, 0x000C, [IntPtr]::Zero, $value)  # WM_SETTEXT
Start-Sleep -Milliseconds 120

# ---- 4. confirm (IDOK) -------------------------------------------------
[void][DpDlg]::PostMessage($dlg, 0x0111, [IntPtr]1, [IntPtr]::Zero)  # WM_COMMAND / IDOK
Start-Sleep -Milliseconds 700

$stillOpen = [DpDlg]::IsWindowVisible($dlg)
Write-Output (ConvertTo-Json @{
  ok = (-not $stillOpen)
  dlgHwnd = [string]$dlg
  dlgClass = $dlgClass
  dlgTitle = $dlgTitle
  editHwnd = [string]$edit
  editId = [DpDlg]::GetDlgCtrlID($edit)
  writtenValue = $value
  dialogStillOpen = $stillOpen
  childCount = $children.Count
} -Compress)
