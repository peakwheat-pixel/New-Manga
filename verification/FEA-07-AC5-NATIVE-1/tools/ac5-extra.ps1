# FEA-07-AC5-NATIVE-1 / ac5-extra.ps1
# 追加原生子项：primary-switch（换主屏）/ fullscreen（最大化+全屏切换）/ ime（中文 IME 输入）/ theme-draft-unplug（未 flush 编辑 + 拔屏）。
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidateSet('primary-switch', 'fullscreen', 'ime', 'theme-draft-unplug')][string]$Mode,
  [string]$OutDir = ""
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'; New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class ExtraApi {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct DISPLAY_DEVICE { public int cb; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string DeviceName; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceString; public int StateFlags; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceID; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceKey; }
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmDeviceName;
    public ushort dmSpecVersion, dmDriverVersion, dmSize, dmDriverExtra; public uint dmFields;
    public int dmPositionX, dmPositionY; public uint dmDisplayOrientation, dmDisplayFixedOutput;
    public short dmColor, dmDuplex, dmYResolution, dmTTOption, dmCollate;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmFormName;
    public ushort dmLogPixels; public uint dmBitsPerPel, dmPelsWidth, dmPelsHeight, dmDisplayFlags, dmDisplayFrequency;
    public uint dmICMMethod, dmICMIntent, dmMediaType, dmDitherType, dmReserved1, dmReserved2, dmPanningWidth, dmPanningHeight;
  }
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplayDevicesW(string dev, uint i, ref DISPLAY_DEVICE dd, uint flags);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplaySettingsW(string dev, int mode, ref DEVMODE dm);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int ChangeDisplaySettingsExW(string dev, ref DEVMODE dm, IntPtr hwnd, uint flags, IntPtr param);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);

  public static DEVMODE NewDevMode() { var dm = new DEVMODE(); dm.dmSize = (ushort)Marshal.SizeOf(dm); return dm; }
  public static string[] Displays() {
    var list = new List<string>();
    for (uint i = 0; i < 16; i++) {
      var dd = new DISPLAY_DEVICE(); dd.cb = Marshal.SizeOf(dd);
      if (!EnumDisplayDevicesW(null, i, ref dd, 0)) break;
      if ((dd.StateFlags & 0x1) == 0) continue;
      var dm = NewDevMode(); if (!EnumDisplaySettingsW(dd.DeviceName, -1, ref dm)) continue;
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", dd.DeviceName, dd.DeviceString, dm.dmPelsWidth, dm.dmPelsHeight, dm.dmPositionX, dm.dmPositionY, ((dd.StateFlags & 0x4) != 0) ? 1 : 0));
    }
    return list.ToArray();
  }
  public static string SetPrimary(string dev) {
    var dm = NewDevMode();
    if (!EnumDisplaySettingsW(dev, -1, ref dm)) return "ERR";
    int rc = ChangeDisplaySettingsExW(dev, ref dm, IntPtr.Zero, 0x00000001 | 0x00000010 /*UPDATEREGISTRY|SET_PRIMARY*/, IntPtr.Zero);
    return "rc=" + rc;
  }
  public static IntPtr Main(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      RECT r; GetWindowRect(h, out r);
      if (r.right - r.left < 200) return true;
      found = h; return false;
    }, IntPtr.Zero);
    return found;
  }
  public static string Rect(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    uint d = GetDpiForWindow(h);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", r.left, r.top, r.right - r.left, r.bottom - r.top, d, Math.Round(d / 96.0 * 100), IsZoomed(h) ? 1 : 0);
  }
  public static string Click(int x, int y) {
    SetCursorPos(x, y); System.Threading.Thread.Sleep(120);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); System.Threading.Thread.Sleep(80);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
    return "clicked " + x + "," + y;
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture([int]$x, [int]$y, [int]$w, [int]$h, [string]$file) {
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h)); $g.Dispose()
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  [pscustomobject]@{ file = (Split-Path $file -Leaf); width = $w; height = $h; sha256 = (Get-FileHash -Algorithm SHA256 -Path $file).Hash.ToLowerInvariant() }
}
function Displays { @([ExtraApi]::Displays() | ForEach-Object { $p = $_ -split '\|'; [pscustomobject]@{ device = $p[0]; adapter = $p[1]; width = [int]$p[2]; height = [int]$p[3]; x = [int]$p[4]; y = [int]$p[5]; primary = ($p[6] -eq '1') } }) }
function Launch-App {
  $root = Join-Path $env:TEMP ("nm-fea07-extra-{0}-{1}" -f $Mode, $stamp)
  $dr = Join-Path $root 'data'; $ld = Join-Path $root 'logs'; $th = Join-Path $root 'theme'
  New-Item -ItemType Directory -Force -Path $dr, $ld, $th | Out-Null
  $exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
  $appArgs = @('--data-root', $dr, '--log-dir', $ld, '--theme-home', $th, '--shell=v2')
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
  foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
  $proc = [System.Diagnostics.Process]::Start($psi)
  $main = [IntPtr]::Zero
  for ($i = 0; $i -lt 50; $i++) { Start-Sleep -Milliseconds 500; $main = [ExtraApi]::Main([uint32]$proc.Id); if ($main -ne [IntPtr]::Zero) { break } }
  if ($main -eq [IntPtr]::Zero) { throw 'window not found' }
  Start-Sleep -Milliseconds 2000
  return @{ proc = $proc; hwnd = $main; dataRoot = $dr; logDir = $ld; themeHome = $th; root = $root }
}
function UiaWindow($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { return $w } }
  return $null
}
function Find-ByName($root, [string]$name, $controlType) {
  $cond = New-Object System.Windows.Automation.AndCondition(
    (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $controlType)),
    (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)))
  return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
}
function Click-Element($el) {
  $p = $el.GetClickablePoint()
  [ExtraApi]::Click([int]$p.X, [int]$p.Y) | Out-Null
}

$displayState = Displays
$result = [ordered]@{ mode = $Mode; capturedAt = (Get-Date -Format o); displaysBefore = $displayState }
$shotsList = @()

switch ($Mode) {
  'primary-switch' {
    $fourK = $displayState | Where-Object { $_.width -eq 3840 } | Select-Object -First 1
    if (-not $fourK) { throw '4K not active' }
    $app = Launch-App
    $result.pid = $app.proc.Id
    $before = ([ExtraApi]::Rect($app.hwnd)) -split '\|'
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-before.png" -f $stamp, $Mode))
    $result.before = [ordered]@{ displays = $displayState; window = [ordered]@{ left = [int]$before[0]; top = [int]$before[1]; width = [int]$before[2]; height = [int]$before[3]; dpi = [int]$before[4]; percent = [int]$before[5]; zoomed = ($before[6] -eq '1') } }
    $set = [ExtraApi]::SetPrimary($fourK.device)
    Start-Sleep -Milliseconds 2500
    $after = Displays
    $rect = ([ExtraApi]::Rect($app.hwnd)) -split '\|'
    $shotsList += Capture ($after | Where-Object { $_.primary }).x ($after | Where-Object { $_.primary }).y ($after | Where-Object { $_.primary }).width ($after | Where-Object { $_.primary }).height (Join-Path $shots ("{0}-{1}-after.png" -f $stamp, $Mode))
    $result.setPrimary = $set
    $result.after = [ordered]@{ displays = $after; window = [ordered]@{ left = [int]$rect[0]; top = [int]$rect[1]; width = [int]$rect[2]; height = [int]$rect[3]; dpi = [int]$rect[4]; percent = [int]$rect[5]; zoomed = ($rect[6] -eq '1') }; appAlive = (-not $app.proc.HasExited) }
    $aoc = $displayState | Where-Object { $_.width -eq 2560 } | Select-Object -First 1
    if ($aoc) { $result.restorePrimary = [ExtraApi]::SetPrimary($aoc.device); Start-Sleep -Milliseconds 2000; $result.restored = Displays }
    if (-not $app.proc.HasExited) { $app.proc.Kill($true); $app.proc.WaitForExit(5000) | Out-Null }
  }
  'fullscreen' {
    $app = Launch-App
    $result.pid = $app.proc.Id
    $win = UiaWindow $app.proc.Id
    $before = ([ExtraApi]::Rect($app.hwnd)) -split '\|'
    $result.before = [ordered]@{ left = [int]$before[0]; top = [int]$before[1]; width = [int]$before[2]; height = [int]$before[3]; dpi = [int]$before[4]; percent = [int]$before[5]; zoomed = ($before[6] -eq '1') }
    $maxBtn = Find-ByName $win '最大化' ([System.Windows.Automation.ControlType]::Button)
    if ($maxBtn) { Click-Element $maxBtn; Start-Sleep -Milliseconds 1500 }
    $maxed = ([ExtraApi]::Rect($app.hwnd)) -split '\|'
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-max.png" -f $stamp, $Mode))
    $result.maximized = [ordered]@{ left = [int]$maxed[0]; top = [int]$maxed[1]; width = [int]$maxed[2]; height = [int]$maxed[3]; dpi = [int]$maxed[4]; percent = [int]$maxed[5]; zoomed = ($maxed[6] -eq '1') }
    # F11 全屏切换（应用快捷键）经 UIA 发送键盘
    [ExtraApi]::SetForegroundWindow($app.hwnd) | Out-Null
    Start-Sleep -Milliseconds 400
    # 应用全屏键为 F（R-020 记录：按钮/F/Esc），F11 无效果已实测
    [System.Windows.Forms.SendKeys]::SendWait('f')
    Start-Sleep -Milliseconds 1500
    $fs1 = ([ExtraApi]::Rect($app.hwnd)) -split '\|'
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-fkey.png" -f $stamp, $Mode))
    $result.afterFKey = [ordered]@{ left = [int]$fs1[0]; top = [int]$fs1[1]; width = [int]$fs1[2]; height = [int]$fs1[3]; dpi = [int]$fs1[4]; percent = [int]$fs1[5]; zoomed = ($fs1[6] -eq '1') }
    [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
    Start-Sleep -Milliseconds 1200
    $fs2 = ([ExtraApi]::Rect($app.hwnd)) -split '\|'
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-esc.png" -f $stamp, $Mode))
    $result.afterEsc = [ordered]@{ left = [int]$fs2[0]; top = [int]$fs2[1]; width = [int]$fs2[2]; height = [int]$fs2[3]; dpi = [int]$fs2[4]; percent = [int]$fs2[5]; zoomed = ($fs2[6] -eq '1') }
    if (-not $app.proc.HasExited) { $app.proc.Kill($true); $app.proc.WaitForExit(5000) | Out-Null }
  }
  'ime' {
    $app = Launch-App
    $result.pid = $app.proc.Id
    $win = UiaWindow $app.proc.Id
    [ExtraApi]::SetForegroundWindow($app.hwnd) | Out-Null
    Start-Sleep -Milliseconds 500
    # 打开命令面板（Ctrl+K）
    [System.Windows.Forms.SendKeys]::SendWait('^k')
    Start-Sleep -Milliseconds 1200
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-palette.png" -f $stamp, $Mode))
    $editCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
    $edits = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCond)
    $result.editCount = $edits.Count
    if ($edits.Count -eq 0) { throw 'no edit control in palette' }
    $target = $edits[$edits.Count - 1]
    try { $target.SetFocus() } catch { Click-Element $target }
    Start-Sleep -Milliseconds 600
    # 切中文输入法（MS Pinyin 布局）并输入拼音
    $sigKb = @'
using System;
using System.Runtime.InteropServices;
public static class Kb {
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr LoadKeyboardLayoutW(string id, uint flags);
  [DllImport("user32.dll")] public static extern IntPtr ActivateKeyboardLayout(IntPtr hkl, uint flags);
}
'@
    Add-Type -TypeDefinition $sigKb
    $hkl = [Kb]::LoadKeyboardLayoutW('00000804', 0x00000001)
    $old = [Kb]::ActivateKeyboardLayout($hkl, 0)
    Start-Sleep -Milliseconds 500
    $result.keyboard = [ordered]@{ loaded = [int64]$hkl; previous = [int64]$old }
    foreach ($ch in @('n','i','h','a','o')) { [System.Windows.Forms.SendKeys]::SendWait($ch); Start-Sleep -Milliseconds 180 }
    Start-Sleep -Milliseconds 600
    [System.Windows.Forms.SendKeys]::SendWait(' ')
    Start-Sleep -Milliseconds 800
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-typed.png" -f $stamp, $Mode))
    $val = $null
    try { $val = ($target.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).Current.Value } catch { $val = $null }
    $result.committedValue = $val
    $result.imeComposed = [bool]($val -match '你好|nihao')
    if (-not $app.proc.HasExited) { $app.proc.Kill($true); $app.proc.WaitForExit(5000) | Out-Null }
  }
  'theme-draft-unplug' {
    $app = Launch-App
    $result.pid = $app.proc.Id
    $win = UiaWindow $app.proc.Id
    $themeBtn = Find-ByName $win '主题工作室' ([System.Windows.Automation.ControlType]::Button)
    if (-not $themeBtn) { $themeBtn = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::AutomationIdProperty, 'ThemeStudioButton'))) }
    if (-not $themeBtn) { throw 'theme studio button not found' }
    Click-Element $themeBtn
    Start-Sleep -Milliseconds 2200
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-studio.png" -f $stamp, $Mode))
    # 记录 theme-home 文件（判断未 flush 是否落盘）
    function ThemeHashes {
      $h = @{}
      Get-ChildItem $app.themeHome -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $h[$_.FullName] = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash }
      return $h
    }
    $themeBefore = ThemeHashes
    $result.themeFilesBefore = ($themeBefore.Keys | ForEach-Object { Split-Path $_ -Leaf })
    # 触发一次编辑（点击候选 swatch/按钮：取 studio 内按钮列表并点第一个非关闭按钮）
    $btnCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
    $btns = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $btnCond)
    $clicked = $null
    foreach ($b in $btns) {
      $n = $b.Current.Name
      if ($n -and $n -notmatch '关闭|最小化|最大化|主题工作室') { Click-Element $b; $clicked = $n; break }
    }
    $result.clickedForDraft = $clicked
    Start-Sleep -Milliseconds 1200
    $shotsList += Capture $displayState[0].x $displayState[0].y $displayState[0].width $displayState[0].height (Join-Path $shots ("{0}-{1}-draft.png" -f $stamp, $Mode))
    $themeAfterEdit = ThemeHashes
    $result.themeUnchangedBeforeUnplug = (($themeBefore.Keys | Sort-Object) -join '|') -eq (($themeAfterEdit.Keys | Sort-Object) -join '|')
    # OS 级拔屏（自动迁移路径）
    $ds = & DisplaySwitch.exe /internal 2>&1 | Out-String
    Start-Sleep -Milliseconds 3000
    $afterUnplug = Displays
    $rect = ([ExtraApi]::Rect($app.hwnd)) -split '\|'
    $shotsList += Capture ($afterUnplug[0]).x ($afterUnplug[0]).y ($afterUnplug[0]).width ($afterUnplug[0]).height (Join-Path $shots ("{0}-{1}-after-unplug.png" -f $stamp, $Mode))
    $themeAfterUnplug = ThemeHashes
    $result.unplug = [ordered]@{
      displaySwitch = $ds.Trim(); displays = $afterUnplug
      window = [ordered]@{ left = [int]$rect[0]; top = [int]$rect[1]; width = [int]$rect[2]; height = [int]$rect[3]; dpi = [int]$rect[4]; percent = [int]$rect[5]; zoomed = ($rect[6] -eq '1') }
      appAlive = (-not $app.proc.HasExited)
      themeFilesAfterUnplug = ($themeAfterUnplug.Keys | ForEach-Object { Split-Path $_ -Leaf })
      themeUnchanged = ((($themeBefore.Keys | Sort-Object) -join '|') -eq (($themeAfterUnplug.Keys | Sort-Object) -join '|'))
    }
    & DisplaySwitch.exe /extend 2>&1 | Out-Null
    Start-Sleep -Milliseconds 3000
    $restored = Displays
    $result.afterRestore = $restored
    if (-not $app.proc.HasExited) { $app.proc.Kill($true); $app.proc.WaitForExit(5000) | Out-Null }
  }
}

$result.screenshots = $shotsList
$out = Join-Path $OutDir ("extra-{0}-{1}.json" -f $Mode, $stamp)
$result | ConvertTo-Json -Depth 9 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
$result | ConvertTo-Json -Depth 9 | Write-Host
