# P19 AC2 main-flow runner (stage A: import multi-select -> page count -> reader paging).
# Reuses the R3-005 infrastructure from run-d-acceptance-v3.ps1:
#   fresh timestamped output dir, refuse-overwrite, assertion counters, non-zero exit on
#   any failed key assertion, per-step UIA dumps + screenshots, run-metadata.txt.
# Stage B (workbench Run / export) is attempted read-only: enabled states are recorded as
# FACTS and never forced; disabled controls are reported, not retried (DIR-4).
# Input discipline: keyboard input is ASCII only; Chinese values go through UIA SetValue.
param(
  [string]$RepoRoot = 'G:/CODEX/New Manga',
  [string]$OutDir,
  [switch]$AllowOverwrite,
  [string]$FixtureDir = "$env:TEMP\p19fx\A",
  [int]$ImportWaitSeconds = 90
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification/P19/ac2-main-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) {
  $existing = @(Get-ChildItem $OutDir -Recurse -File -ErrorAction SilentlyContinue)
  if ($existing.Count -gt 0 -and -not $AllowOverwrite) { Write-Host "REFUSING_OVERWRITE $OutDir ($($existing.Count) files)"; exit 4 }
} else { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$ud = Join-Path $OutDir 'uia'; $tr = Join-Path $OutDir 'trace.log'
New-Item -ItemType Directory -Force -Path $ud | Out-Null
Remove-Item $tr -ErrorAction SilentlyContinue

$script:Checks = 0; $script:Fails = 0
$AE=[System.Windows.Automation.AutomationElement]; $TS=[System.Windows.Automation.TreeScope]
$CT=[System.Windows.Automation.ControlType]; $ANY=[System.Windows.Automation.Condition]::TrueCondition
$TITLE = 'M2-RC1 resource channel runtime'
function T($m){ $l='['+(Get-Date -Format 'HH:mm:ss.fff')+'] '+$m; Add-Content -Path $tr -Value $l -Encoding utf8; Write-Host $l }
function A($ok,$what){ $script:Checks++; if($ok){ T "ASSERT PASS $what" } else { $script:Fails++; T "ASSERT FAIL $what" } }
function W{ $c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$TITLE); $AE::RootElement.FindFirst($TS::Children,$c) }
function All($root=$null){ $r = if($root){$root}else{W}; if(-not $r){return @()}; @($r.FindAll($TS::Descendants,$ANY)) }
function Names($root=$null){ @(All $root | ForEach-Object { try{ $_.Current.Name }catch{} } | Where-Object { $_ -ne '' }) }
function PN{ $w=W; if(-not $w){return @()}; $c=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::Pane); @($w.FindAll($TS::Descendants,$c)|%{$_.Current.Name}) }
function Shot($tag){
  $w=W; if(-not $w){ T "SHOT $tag NO_WINDOW"; return }
  try{ $r=$w.Current.BoundingRectangle; if($r.Width -lt 1){T "SHOT $tag EMPTY";return}
    $bmp=New-Object System.Drawing.Bitmap([int]$r.Width,[int]$r.Height); $g=[System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen([int]$r.X,[int]$r.Y,0,0,$bmp.Size); $bmp.Save((Join-Path $OutDir "$tag.png"),[System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose(); T "SHOT $tag OK" } catch { T "SHOT $tag FAILED $($_.Exception.Message)" }
}
function D($tag){ $w=W; if(-not $w){ T "DUMP $tag MISSING"; return }
  $a=All $w; $ls=New-Object System.Collections.Generic.List[string]; $ls.Add("# $tag n=$($a.Count) $(Get-Date -Format o)")
  for($i=0;$i -lt $a.Count;$i++){ $e=$a[$i]; try{ $ty=($e.Current.ControlType.ProgrammaticName -replace 'ControlType\.',''); $ls.Add("$i|$ty|$($e.Current.Name)|en=$($e.Current.IsEnabled)|off=$($e.Current.IsOffscreen)") }catch{} }
  Set-Content -Path (Join-Path $ud "$tag.uia.txt") -Value $ls -Encoding utf8; T "DUMP $tag n=$($a.Count)"; Shot $tag }
function F($n,$ct=$null,$root=$null){ $r = if($root){$root}else{W}; if(-not $r){return $null}
  $cs=New-Object System.Collections.Generic.List[object]
  $cs.Add((New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$n)))
  if($ct){ $cs.Add((New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$ct))) }
  $c=if($cs.Count -gt 1){New-Object System.Windows.Automation.AndCondition($cs.ToArray())}else{$cs[0]}
  $r.FindFirst($TS::Descendants,$c) }
function C($n,$why,$ct=$CT::Button){ $e=F $n $ct; if(-not $e){ T "CLICK $why '$n' NOT_FOUND"; A $false "click:$why"; return $false }
  try{ $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 1000; T "CLICK $why '$n' OK"; A $true "click:$why"; return $true }
  catch{ T "CLICK $why '$n' FAILED $($_.Exception.Message)"; A $false "click:$why"; return $false } }
function SE($n,$v){ $e=F $n $CT::Edit; if(-not $e){ T "SET $n NOT_FOUND"; A $false "set:$n"; return $false }
  try{ $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($v); Start-Sleep -Milliseconds 400; T "SET $n='$v' OK"; A $true "set:$n"; return $true }
  catch{ T "SET $n FAILED"; A $false "set:$n"; return $false } }
function ClickAny($cands,$why){ foreach($c in $cands){ $e=F $c $CT::Button; if($e){ return (C $c $why) } }; T "CLICK $why none-of($($cands -join ','))"; A $false "click:$why"; return $false }
# --- file dialog helpers (validated recipe: navigate to FOLDER, then select items, then ENTER) ---
function DlgWindow{ foreach($n in @('打开','选择文件','选择图片','Open','Select')){ $e=F $n $CT::Window; if($e){return $e} }; $AE::RootElement.FindFirst($TS::Children,(New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::Window))) }
function SelectFixtures($files){
  $dlg = DlgWindow; if(-not $dlg){ T 'DIALOG_NOT_FOUND'; A $false 'dialog:found'; return $false }
  # NOTE: do NOT call SetFocus() on the dialog or its controls. The FEAT owner proved that the
  # native picker rejects element-level focus ("目标元素无法接收焦点"). A modal picker is already
  # foreground, so SendKeys works directly; the path is pasted from the clipboard (proven recipe).
  Start-Sleep -Milliseconds 600
  # navigate to the FOLDER (trailing backslash) via Ctrl+L + clipboard paste
  [System.Windows.Forms.SendKeys]::SendWait('^l'); Start-Sleep -Milliseconds 500
  $path = ($FixtureDir.TrimEnd('\') + '\')
  Set-Clipboard -Value $path; Start-Sleep -Milliseconds 200
  [System.Windows.Forms.SendKeys]::SendWait('^v'); Start-Sleep -Milliseconds 400
  [System.Windows.Forms.SendKeys]::SendWait('{ENTER}'); Start-Sleep -Milliseconds 2000
  T "PICKER_NAVIGATION dir=$path"
  # truly select each fixture item via SelectionItemPattern (type-ahead does NOT work)
  $items = @(
    @($dlg.FindAll($TS::Descendants,(New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::ListItem)))) +
    @($dlg.FindAll($TS::Descendants,(New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::DataItem))))
  )
  $sel = 0
  foreach($f in $files){
    $hit = $items | Where-Object { try { $_.Current.Name -match [regex]::Escape($f) } catch { $false } } | Select-Object -First 1
    if(-not $hit){ T "PICKER_MISSING $f"; continue }
    try{
      $p = $hit.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
      if($sel -eq 0){ $p.Select() } else { $p.AddToSelection() }
      $sel++; T "PICKER_SELECTED $f"
    } catch { T "PICKER_SELECT_FAILED $f $($_.Exception.Message)" }
  }
  A ($sel -eq $files.Count) "picker:selected-all ($sel/$($files.Count))"
  T "PICKER_VISIBLE_ITEMS=$(@($items | ForEach-Object { try { $_.Current.Name } catch {} } | Where-Object { $_ } ).Count)"
  [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
  T 'PICKER_CONFIRMED'
  return ($sel -eq $files.Count)
}
function WaitImportDone($maxSec){
  # Completion signals (learned from the FEAT owner's runner, which asserted the same UI):
  #   1) an import report appears containing 导入报告 + 已导入 + 跳过重复 + 导入失败
  #   2) fallback: "正在导入" disappears while a page-count readout is present
  $dl=(Get-Date).AddSeconds($maxSec)
  while((Get-Date) -lt $dl){
    $n = (Names) -join '|'
    if($n -match '导入报告' -or $n -match '已导入'){
      T 'IMPORT_REPORT=VISIBLE'
      foreach($k in @('已导入','跳过重复','导入失败')){ T ("IMPORT_REPORT_HAS " + $k + "=" + [bool]($n -match $k)) }
      return $true
    }
    if($n -notmatch '正在导入' -and $n -match '页数'){ T 'IMPORT_DONE=no-active-import'; return $true }
    Start-Sleep -Milliseconds 900
  }
  T "IMPORT_WAIT_TIMEOUT ${maxSec}s"; return $false
}

$iso = Join-Path $env:TEMP ('p19-ac2-main-'+[guid]::NewGuid().ToString('N').Substring(0,8))
$exe = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$exeDir = Split-Path $exe
$started = (Get-Date)
T "RUN start iso=$iso outdir=$OutDir"
$meta = New-Object System.Collections.Generic.List[string]
$meta.Add('runner=run-ac2-mainflow-v1.ps1'); $meta.Add('started_local='+$started.ToString('o'))
$meta.Add('outdir='+$OutDir); $meta.Add('iso_root='+$iso); $meta.Add('fixture_dir='+$FixtureDir)
$exitCode = 0; $p = $null
if (-not (Test-Path $exe)) { T 'FATAL exe missing'; $meta.Add('fatal=exe_missing'); $meta | Set-Content (Join-Path $OutDir 'run-metadata.txt') -Encoding utf8; exit 2 }
$exeHash = (Get-FileHash $exe -Algorithm SHA256).Hash.ToLower(); T ('exe sha256='+$exeHash)
$meta.Add('exe_sha256='+$exeHash)
if (-not (Test-Path $FixtureDir)) { T "FATAL fixture dir missing $FixtureDir"; $meta.Add('fatal=fixture_missing'); $meta | Set-Content (Join-Path $OutDir 'run-metadata.txt') -Encoding utf8; exit 5 }
$fx = @(Get-ChildItem -LiteralPath $FixtureDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '^\.(png|jpg|jpeg|pdf)$' } | Sort-Object Name)
T "FIXTURE count=$($fx.Count) files=$((@($fx|%{$_.Name})) -join ',')"
$meta.Add('fixture_count='+$fx.Count)
$env:NEWMANGA_DATA_ROOT = $iso
try {
  $p = Start-Process -FilePath $exe -WorkingDirectory $exeDir -PassThru -RedirectStandardOutput (Join-Path $OutDir 'app-out.log') -RedirectStandardError (Join-Path $OutDir 'app-err.log')
  T "pid=$($p.Id)"
  $dl=(Get-Date).AddSeconds(45); $w=$null
  while((Get-Date) -lt $dl){ Start-Sleep -Milliseconds 700; if($p.HasExited){ T "FATAL early exit=$($p.ExitCode)"; break }; $w=W; if($w){break} }
  if(-not $w){ T 'FATAL no window'; A $false 'app:window'; $exitCode=3 }
  else {
    A $true 'app:window'
    $rd=(Get-Date).AddSeconds(40); while((Get-Date) -lt $rd){ if(-not ((PN -join '|') -match 'starting')){break}; Start-Sleep -Milliseconds 700 }
    T 'READY'; D '01-bookshelf'
    # ---- 1) create book + chapter (ASCII values via UIA SetValue) ----
    $okNew = ClickAny @('+ 新建作品','导入作品') 'open-create'
    D '02-create-dialog'
    SE '作品标题' 'P19Ac2Book' | Out-Null
    ClickAny @('创建作品','创建') 'create-book' | Out-Null
    Start-Sleep -Milliseconds 1200; D '03-book-created'
    ClickAny @('+ 新建章节','新建章节') 'open-chapter' | Out-Null
    Start-Sleep -Milliseconds 800; D '04-chapter-dialog'
    SE '章节标题' 'P19Ac2Ch1' | Out-Null
    ClickAny @('创建章节','创建') 'create-chapter' | Out-Null
    Start-Sleep -Milliseconds 1200; D '05-chapter-created'
    A ((Names) -match 'P19Ac2Book') 'book:visible'
    # ---- 2) import fixtures via chapter-level import ----
    ClickAny @('导入') 'open-import' | Out-Null
    Start-Sleep -Milliseconds 800; D '06-import-panel'
    ClickAny @('📄 选择图片 / PDF 文件（可多选）','📄 选择图片 / PDF 文件') 'open-file-picker' | Out-Null
    Start-Sleep -Milliseconds 1500
    $names = @($fx | ForEach-Object { $_.Name })
    SelectFixtures $names | Out-Null
    $done = WaitImportDone $ImportWaitSeconds
    A $done 'import:finished'
    Start-Sleep -Milliseconds 1500; D '07-after-import'
    $after = (Names) -join '|'
    # Page-count evidence: the shelf readout can lag the DB ("页数 —" / "0 页"), so the UI text is
    # recorded as a FACT while the authoritative assertion uses the chapter's rows in the isolated DB.
    $uiPageMatch = [regex]::Matches($after,'(\d+)\s*页')
    $uiPages = if($uiPageMatch.Count -gt 0){ ($uiPageMatch | ForEach-Object { [int]$_.Groups[1].Value } | Sort-Object -Descending | Select-Object -First 1) } else { -1 }
    T "UI_PAGE_TEXT max=$uiPages raw='$((($after -split '\|') | Where-Object { $_ -match '页' }) -join ' ; ')'"
    $dbPages = -1
    $dbQuery = Join-Path $OutDir 'db-page-count.py'
    @'
import sqlite3, sys
con = sqlite3.connect(sys.argv[1]); cur = con.cursor()
row = cur.execute("select count(*) from pages p join chapters c on p.chapter_id=c.id where c.name=?", (sys.argv[2],)).fetchone()
print(row[0])
'@ | Set-Content -Path $dbQuery -Encoding utf8
    $pyExe = 'C:\Python314\python.exe'
    try { $dbPages = [int]((& $pyExe $dbQuery (Join-Path $iso 'library.db') 'P19Ac2Ch1' 2>$null | Select-Object -Last 1)) } catch { T "DB_QUERY_FAILED $($_.Exception.Message)" }
    T "PAGE_COUNT_DB chapter=P19Ac2Ch1 pages=$dbPages (ui_text=$uiPages)"
    $pages = $dbPages
    T "PAGE_COUNT after_import=$pages expected=$($fx.Count)"
    $meta.Add("pages_after_import=$pages"); $meta.Add("pages_ui_text=$uiPages"); $meta.Add("pages_expected=$($fx.Count)")
    A ($pages -eq $fx.Count) "import:page-count (DB, =expected $($fx.Count))"
    # ---- 3) reader paging (needs >=2 pages) ----
    ClickAny @('阅读') 'open-reader' | Out-Null
    Start-Sleep -Milliseconds 1500; D '08-reader'
    # Reader position comes from the "Image :: Page N" element (the "1 / 2" display is split across
    # separate Text elements, so a joined-string regex mis-matched). Total pages come from the DB.
    $pos1 = (All | Where-Object { try { $_.Current.ControlType -eq $CT::Image -and $_.Current.Name -match 'Page\s+(\d+)' } catch { $false } } | Select-Object -First 1 | ForEach-Object { [int]([regex]::Match($_.Current.Name,'(\d+)').Groups[1].Value) })
    if(-not $pos1){ $pos1 = -1 }
    $tot = $dbPages
    T "READER_PAGE first=$pos1 total=$tot (db)"
    $meta.Add("reader_total=$tot")
    A ($tot -ge 2) 'reader:total>=2'
    $nextOk = $false
    foreach($n in @('Next page','下一页 (←)','下一页')){
      $e=F $n $CT::Button
      if($e){ T "READER_NEXT_CAND '$n' enabled=$($e.Current.IsEnabled)"; if($e.Current.IsEnabled){ C $n 'reader-next' | Out-Null; $nextOk=$true; break } }
    }
    if(-not $nextOk){ T 'READER_NEXT none-enabled'; A $false 'reader:next-available' } else { A $true 'reader:next-available' }
    Start-Sleep -Milliseconds 1500; D '09-reader-after-next'
    $pos2 = (All | Where-Object { try { $_.Current.ControlType -eq $CT::Image -and $_.Current.Name -match 'Page\s+(\d+)' } catch { $false } } | Select-Object -First 1 | ForEach-Object { [int]([regex]::Match($_.Current.Name,'(\d+)').Groups[1].Value) })
    if(-not $pos2){ $pos2 = -1 }
    T "READER_PAGE after_next=$pos2"
    $meta.Add("reader_page_after_next=$pos2")
    A ($pos2 -gt $pos1) 'reader:advanced'
    # ---- 4) workbench Run / export: return to the bookshelf FIRST, select the book, record FACTS only ----
    foreach($n in @('← 返回书架','返回书架')){ $e=F $n $CT::Button; if($e -and $e.Current.IsEnabled){ C $n 'reader-back' | Out-Null; break } }
    Start-Sleep -Milliseconds 1200; D '10-bookshelf-for-selection'
    # ac2-plan-r1.md step 3: the workbench needs a selected book/chapter context, otherwise
    # "启动"/"导出选择页" stay disabled. We establish context by invoking the book entry.
    $wb = W
    $allBtn = @($wb.FindAll($TS::Descendants,(New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::Button))))
    $bookBtn = $allBtn | Where-Object { try { $_.Current.Name -match 'P19Ac2Book' } catch { $false } } | Select-Object -First 1
    if($bookBtn){
      try{ $bookBtn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 1500; T 'BOOK_SELECTED P19Ac2Book'; A $true 'book:selected' }
      catch{ T "BOOK_SELECT_FAILED $($_.Exception.Message)"; A $false 'book:selected' }
    } else { T 'BOOK_ENTRY_NOT_FOUND'; A $false 'book:selected' }
    D '10-book-selected'
    ClickAny @('🛠️ 工作台') 'nav-workbench' | Out-Null
    Start-Sleep -Milliseconds 1500; D '11-workbench'
    foreach($n in @('启动','运行','Run','开始')){
      $e=F $n $CT::Button; if($e){ T "WORKBENCH_RUN control='$n' enabled=$($e.Current.IsEnabled)"; $meta.Add("workbench_run_enabled=$($e.Current.IsEnabled)"); break }
    }
    $ex = F '导出选择页' $CT::Button
    if($ex){ T "EXPORT control enabled=$($ex.Current.IsEnabled)"; $meta.Add("export_enabled=$($ex.Current.IsEnabled)") }
    C '📚 书架' 'nav-back' | Out-Null; D '12-bookshelf-back'
  }
}
finally {
  if($p -and -not $p.HasExited){ $p.CloseMainWindow()|Out-Null; Start-Sleep -Seconds 2 }
  if($p -and -not $p.HasExited){ Stop-Process -Id $p.Id -Force }
  $ended=(Get-Date)
  T "closed exit=$($p.ExitCode)"; T "RUN end checks=$script:Checks fails=$script:Fails"
  $meta.Add('ended_local='+$ended.ToString('o')); $meta.Add('duration_s='+[math]::Round(($ended-$started).TotalSeconds,1))
  $meta.Add("checks=$script:Checks"); $meta.Add("fails=$script:Fails")
  if ($exitCode -eq 0 -and $script:Fails -gt 0) { $exitCode = 1 }
  $meta.Add("exit_code=$exitCode")
  $meta | Set-Content (Join-Path $OutDir 'run-metadata.txt') -Encoding utf8
}
exit $exitCode
