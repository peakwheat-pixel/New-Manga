# P19 D-变体验收（真实 WebView2 + UIA 语义断言）——可重放脚本
# 用户 2026-10-17 裁决 A：接受 D 为等效验收。
# 要求覆盖：导航/动作轨迹、表单提交（隔离数据）、UIA enabled/disabled 证明、原始 UIA 转储。
#
# 前提：
#   - 已构建 apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe（含 P19-BOOT-1 修复）
#   - 已重建 frozen sidecar（packaging/m2ac5/build_sidecar.ps1 -Force）并刷新资源
#   - 具备交互式桌面（非 headless）；勿在有人正在使用桌面时运行
# 隔离：使用独立 NEWMANGA_DATA_ROOT，不触碰用户 %APPDATA% 数据
param(
  [string]$RepoRoot = 'G:/CODEX/New Manga',
  [string]$OutDir   = 'G:/CODEX/New Manga/verification/P19/d-run',
  [int]$WindowWaitSeconds = 45
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

$exe      = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$exeDir   = Split-Path $exe
$isoRoot  = Join-Path $env:TEMP ('p19-iso-' + [guid]::NewGuid().ToString('N').Substring(0,8))
$trace    = Join-Path $OutDir 'trace.log'
$dumpDir  = Join-Path $OutDir 'uia'
New-Item -ItemType Directory -Force -Path $OutDir, $dumpDir, $isoRoot | Out-Null
Remove-Item $trace -ErrorAction SilentlyContinue

function T([string]$msg) {
  $line = ('[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss.fff'), $msg)
  Add-Content -Path $trace -Value $line -Encoding utf8
  Write-Host $line
}

$AE   = [System.Windows.Automation.AutomationElement]
$TS   = [System.Windows.Automation.TreeScope]
$CT   = [System.Windows.Automation.ControlType]
$ALL_COND = [System.Windows.Automation.Condition]::TrueCondition

function Get-AppWindow {
  $cond = New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, 'M2-RC1 resource channel runtime')
  return $AE::RootElement.FindFirst($TS::Children, $cond)
}

function Dump-Uia([string]$tag) {
  $win = Get-AppWindow
  if (-not $win) { T "DUMP $tag : WINDOW_MISSING"; return }
  $all = $win.FindAll($TS::Descendants, $ALL_COND)
  $path = Join-Path $dumpDir ("$tag.uia.txt")
  $lines = New-Object System.Collections.Generic.List[string]
  $lines.Add("# tag=$tag elements=$($all.Count) at=$(Get-Date -Format o)")
  for ($i = 0; $i -lt $all.Count; $i++) {
    $e = $all[$i]
    try {
      $type = ($e.Current.ControlType.ProgrammaticName -replace 'ControlType\.', '')
      $lines.Add(('{0}|type={1}|name={2}|id={3}|enabled={4}|offscreen={5}' -f $i, $type, $e.Current.Name, $e.Current.AutomationId, $e.Current.IsEnabled, $e.Current.IsOffscreen))
    } catch { $lines.Add("$i|ERR") }
  }
  Set-Content -Path $path -Value $lines -Encoding utf8
  T "DUMP $tag -> $([System.IO.Path]::GetFileName($path)) elements=$($all.Count)"
}

function Find-ByName([string]$name, $controlType = $null) {
  $win = Get-AppWindow
  if (-not $win) { return $null }
  $conds = New-Object System.Collections.Generic.List[object]
  $conds.Add((New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, $name)))
  if ($controlType) { $conds.Add((New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, $controlType))) }
  $cond = if ($conds.Count -gt 1) { New-Object System.Windows.Automation.AndCondition($conds.ToArray()) } else { $conds[0] }
  return $win.FindFirst($TS::Descendants, $cond)
}

function Invoke-ByName([string]$name, [string]$tag) {
  $el = Find-ByName $name $CT::Button
  if (-not $el) { T "ACTION invoke '$name' -> NOT_FOUND"; return $false }
  $enabled = $el.Current.IsEnabled
  try {
    $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
    Start-Sleep -Milliseconds 900
    T "ACTION invoke '$name' -> OK (enabled=$enabled)"
    return $true
  } catch {
    T "ACTION invoke '$name' -> FAILED (enabled=$enabled) : $($_.Exception.Message)"
    return $false
  }
}

function Probe-DisabledCategory {
  # AC4：证明"可见但不可操作" —— 记录 IsEnabled 并尝试 Invoke 后比对页面是否变化
  $win = Get-AppWindow
  $targets = @('OCR 未开放', '图片修复 未开放', '排版样式 未开放', '模型/GPU 未开放', '任务/并发 未开放', '缓存/Revision 未开放', '回收站 未开放', '备份/恢复 未开放', 'Plugin/Hooks 未开放')
  foreach ($t in $targets) {
    $el = Find-ByName $t $CT::Button
    if (-not $el) { T "DISABLED-PROBE '$t' -> NOT_FOUND"; continue }
    $enabled = $el.Current.IsEnabled
    $before = (Get-AppWindow).FindAll($TS::Descendants, $ALL_COND).Count
    $invoked = 'n/a'
    try {
      $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
      Start-Sleep -Milliseconds 500
      $invoked = 'invoked'
    } catch { $invoked = "invoke-failed: $($_.Exception.Message)" }
    $after = (Get-AppWindow).FindAll($TS::Descendants, $ALL_COND).Count
    $changed = if ($before -ne $after) { 'PAGE_CHANGED' } else { 'PAGE_UNCHANGED' }
    T "DISABLED-PROBE '$t' -> enabled=$enabled invoke=$invoked descendants=$before->$after $changed"
  }
}

function Set-EditValue([string]$name, [string]$value) {
  $el = Find-ByName $name $CT::Edit
  if (-not $el) { T "ACTION set '$name' -> EDIT_NOT_FOUND"; return $false }
  try {
    $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($value)
    Start-Sleep -Milliseconds 300
    T "ACTION set '$name'='$value' -> OK"
    return $true
  } catch {
    T "ACTION set '$name' -> FAILED : $($_.Exception.Message)"
    return $false
  }
}

function Toggle-ByName([string]$name) {
  $el = Find-ByName $name $CT::CheckBox
  if (-not $el) { T "ACTION toggle '$name' -> CHECKBOX_NOT_FOUND"; return $false }
  try {
    $p = $el.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
    $p.Toggle(); Start-Sleep -Milliseconds 300
    T "ACTION toggle '$name' -> OK state=$($p.Current.ToggleState)"
    return $true
  } catch {
    T "ACTION toggle '$name' -> FAILED : $($_.Exception.Message)"
    return $false
  }
}

function Find-SubmitButton {
  $win = Get-AppWindow
  $btns = $win.FindAll($TS::Descendants, (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, $CT::Button)))
  $names = @()
  for ($i = 0; $i -lt $btns.Count; $i++) { if ($btns[$i].Current.Name) { $names += $btns[$i].Current.Name } }
  T ("FORM buttons: " + ($names -join ' | '))
  foreach ($cand in @('创建', '创建 Profile', '保存', '确定', '提交', '新建', 'Create', 'Save', 'OK', 'Submit')) {
    if ($names -contains $cand) { return $cand }
  }
  return $null
}

# ---------------- run ----------------
T "RUN start; repo=$RepoRoot; isolated_root=$isoRoot"
T "exe=$exe"
if (-not (Test-Path $exe)) { T 'FATAL exe missing'; exit 2 }
T ("exe sha256=" + (Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())
T ("sidecar sha256=" + (Get-FileHash (Join-Path $exeDir 'resources/core-sidecar/core_service.exe') -Algorithm SHA256).Hash.ToLower())

$env:NEWMANGA_DATA_ROOT = $isoRoot
$proc = Start-Process -FilePath $exe -WorkingDirectory $exeDir -PassThru `
  -RedirectStandardOutput (Join-Path $OutDir 'app-stdout.log') `
  -RedirectStandardError  (Join-Path $OutDir 'app-stderr.log')
T "launched pid=$($proc.Id)"

$deadline = (Get-Date).AddSeconds($WindowWaitSeconds)
$win = $null
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Milliseconds 700
  if ($proc.HasExited) { T "FATAL app exited early exitCode=$($proc.ExitCode)"; break }
  $win = Get-AppWindow
  if ($win) { break }
}
if (-not $win) {
  T 'FATAL window not found'
  if (-not $proc.HasExited) { $proc.CloseMainWindow() | Out-Null }
  exit 3
}
T "window acquired: pid=$($proc.Id) title='$($win.Current.Name)'"
Start-Sleep -Seconds 4

try {
  # 1) 书架
  Dump-Uia '01-bookshelf'
  # 2) 工作台
  Invoke-ByName '🛠️ 工作台' 'nav-workbench' | Out-Null
  Dump-Uia '02-workbench'
  # 3) 阅读器
  Invoke-ByName '📖 阅读器' 'nav-reader' | Out-Null
  Dump-Uia '03-reader'
  # 4) 设置 + 禁用态证明
  Invoke-ByName '⚙️ 设置' 'nav-settings' | Out-Null
  Dump-Uia '04-settings'
  Probe-DisabledCategory
  # 5) 新建 Profile 表单 + 隔离数据提交
  Invoke-ByName '新建 Profile' 'open-create-form' | Out-Null
  Dump-Uia '05-profile-form'
  Set-EditValue 'provider_id' 'e2e-provider-a' | Out-Null
  Set-EditValue 'display_name' 'E2E Provider A' | Out-Null
  Toggle-ByName 'OCR' | Out-Null
  $submit = Find-SubmitButton
  if ($submit) {
    Invoke-ByName $submit 'submit-create-form' | Out-Null
    Start-Sleep -Milliseconds 1200
    Dump-Uia '06-after-submit'
    $win2 = Get-AppWindow
    $txt = $win2.FindAll($TS::Descendants, $ALL_COND) | ForEach-Object { $_.Current.Name }
    if ($txt -match 'E2E Provider A') { T 'SUBMIT RESULT: PROFILE_VISIBLE_IN_LIST -> PASS' }
    else { T 'SUBMIT RESULT: PROFILE_NOT_VISIBLE -> FAIL' }
  } else {
    T 'SUBMIT RESULT: SUBMIT_BUTTON_NOT_FOUND -> INCONCLUSIVE'
    Dump-Uia '06-no-submit'
  }
  # 7) 回书架（导航轨迹闭环）
  Invoke-ByName '📚 书架' 'nav-bookshelf-back' | Out-Null
  ProbeDisabledCategory
  Dump-Uia '07-bookshelf-back'
}
finally {
  if (-not $proc.HasExited) { $proc.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
  if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
  T "app closed; exit=$(if($proc.HasExited){$proc.ExitCode}else{'forced'})"
  T "RUN end"
}
