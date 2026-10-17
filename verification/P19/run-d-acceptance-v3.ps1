# P19 D-variant acceptance runner v3.
# Fixes R3-005: (1) fresh timestamped output dir by default, (2) refuses to overwrite a
# non-empty output dir unless -AllowOverwrite, (3) key assertion failures exit non-zero,
# (4) writes run-metadata.txt (timestamps/hashes/counts) and per-step screenshots (R3-004).
# v2 is preserved unchanged so its pinned sha256 stays valid; this is a new artifact.
param(
  [string]$RepoRoot = 'G:/CODEX/New Manga',
  [string]$OutDir,
  [switch]$AllowOverwrite,
  [int]$WindowWaitSeconds = 45
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Drawing

# ---------- output dir: fresh + refuse overwrite (R3-005) ----------
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification/P19/d-run-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) {
    $existing = @(Get-ChildItem $OutDir -Recurse -File -ErrorAction SilentlyContinue)
    if ($existing.Count -gt 0 -and -not $AllowOverwrite) {
        Write-Host "REFUSING_OVERWRITE OutDir already has $($existing.Count) file(s): $OutDir"
        exit 4
    }
} else {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}
$ud = Join-Path $OutDir 'uia'
$tr = Join-Path $OutDir 'trace.log'
New-Item -ItemType Directory -Force -Path $ud | Out-Null
Remove-Item $tr -ErrorAction SilentlyContinue

# ---------- assertion counters (R3-005) ----------
$script:Checks = 0
$script:Fails  = 0

$AE=[System.Windows.Automation.AutomationElement]; $TS=[System.Windows.Automation.TreeScope]
$CT=[System.Windows.Automation.ControlType]; $ANY=[System.Windows.Automation.Condition]::TrueCondition
$TITLE = 'M2-RC1 resource channel runtime'

function T($m){ $l='['+(Get-Date -Format 'HH:mm:ss.fff')+'] '+$m; Add-Content -Path $tr -Value $l -Encoding utf8; Write-Host $l }
function A($ok,$what){ $script:Checks++; if($ok){ T "ASSERT PASS $what" } else { $script:Fails++; T "ASSERT FAIL $what" } }
function W{ $c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$TITLE); $AE::RootElement.FindFirst($TS::Children,$c) }
function PN{ $w=W; if(-not $w){return @()}; $c=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::Pane); @($w.FindAll($TS::Descendants,$c)|%{$_.Current.Name}) }
function Shot($tag){
    $w=W; if(-not $w){ T "SHOT $tag NO_WINDOW"; return }
    try{
        $r=$w.Current.BoundingRectangle
        if($r.Width -lt 1 -or $r.Height -lt 1){ T "SHOT $tag EMPTY_BOUNDS"; return }
        $bmp=New-Object System.Drawing.Bitmap([int]$r.Width,[int]$r.Height)
        $g=[System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen([int]$r.X,[int]$r.Y,0,0,$bmp.Size)
        $bmp.Save((Join-Path $OutDir "$tag.png"),[System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose(); $bmp.Dispose(); T "SHOT $tag OK"
    } catch { T "SHOT $tag FAILED $($_.Exception.Message)" }
}
function D($tag){
    $w=W; if(-not $w){ T "DUMP $tag MISSING"; return }
    $all=$w.FindAll($TS::Descendants,$ANY); $ls=New-Object System.Collections.Generic.List[string]
    $ls.Add("# $tag n=$($all.Count) $(Get-Date -Format o)")
    for($i=0;$i -lt $all.Count;$i++){ $e=$all[$i]; try{ $ty=($e.Current.ControlType.ProgrammaticName -replace 'ControlType\.',''); $ls.Add("$i|$ty|$($e.Current.Name)|en=$($e.Current.IsEnabled)|off=$($e.Current.IsOffscreen)") }catch{} }
    Set-Content -Path (Join-Path $ud "$tag.uia.txt") -Value $ls -Encoding utf8
    T "DUMP $tag n=$($all.Count)"
    Shot $tag
}
function F($n,$ct=$null){
    $w=W; if(-not $w){return $null}
    $cs=New-Object System.Collections.Generic.List[object]
    $cs.Add((New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$n)))
    if($ct){ $cs.Add((New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$ct))) }
    $c=if($cs.Count -gt 1){New-Object System.Windows.Automation.AndCondition($cs.ToArray())}else{$cs[0]}
    $w.FindFirst($TS::Descendants,$c)
}
function C($n,$why){
    $e=F $n $CT::Button
    if(-not $e){ T "CLICK $why '$n' NOT_FOUND"; A $false "click:$why"; return $false }
    $en=$e.Current.IsEnabled
    try{
        $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
        Start-Sleep -Milliseconds 900
        T "CLICK $why '$n' OK en=$en"
        A $true "click:$why"
        return $true
    } catch { T "CLICK $why '$n' FAILED en=$en $($_.Exception.Message)"; A $false "click:$why"; return $false }
}
function SE($n,$v){
    $e=F $n $CT::Edit
    if(-not $e){ T "SET $n EDIT_NOT_FOUND"; A $false "set:$n"; return $false }
    try{ $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($v); Start-Sleep -Milliseconds 300; T "SET $n='$v' OK"; A $true "set:$n"; return $true }
    catch { T "SET $n FAILED"; A $false "set:$n"; return $false }
}
function TG($n){
    $e=F $n $CT::CheckBox
    if(-not $e){ T "TOGGLE $n NOT_FOUND"; A $false "toggle:$n"; return $false }
    try{ $p=$e.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern); $p.Toggle(); Start-Sleep -Milliseconds 300; T "TOGGLE $n OK state=$($p.Current.ToggleState)"; A $true "toggle:$n"; return $true }
    catch { T "TOGGLE $n FAILED"; A $false "toggle:$n"; return $false }
}
# AC4: un-delivered partitions must be visible, disabled, and NOT invokable.
function PR{
    # Actual control names are "<partition>，未开放：等待 section schema 冻结" (comma + reason),
    # so match on the partition-name prefix plus the 未开放 marker instead of an exact string.
    foreach($n in @('OCR','图片修复','排版样式','模型/GPU','任务/并发','缓存/Revision','回收站','备份/恢复','Plugin/Hooks')){
        $win = W
        $e = if($win){ ($win.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | Where-Object { try { $_.Current.ControlType -eq $CT::Button -and $_.Current.Name -match ("^" + [regex]::Escape($n) + ".*未开放") } catch { $false } } | Select-Object -First 1) } else { $null }
        if(-not $e){ T "PROBE '$n' NOT_FOUND"; A $false "disabled-present:$n"; continue }
        $en=$e.Current.IsEnabled
        $b=(PN -join '|'); $iv='n/a'
        try{ $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 600; $iv='invoked' }
        catch{ $iv='failed' }
        $a=(PN -join '|'); $ch=if($b -eq $a){'PAGE_UNCHANGED'}else{'PAGE_CHANGED'}
        $na=@((PN)|?{$_ -match '未开放'})
        T "PROBE '$n' en=$en invoke=$iv $ch panes=[$($na -join '/')]"
        # Pass = disabled AND invoke did not navigate away.
        A ((-not $en) -and ($ch -eq 'PAGE_UNCHANGED')) "disabled-not-invokable:$n"
    }
}

$iso = Join-Path $env:TEMP ('p19v3-'+[guid]::NewGuid().ToString('N').Substring(0,8))
$exe = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$exeDir = Split-Path $exe
$started = (Get-Date)
T "RUN start iso=$iso outdir=$OutDir"
$meta = New-Object System.Collections.Generic.List[string]
$meta.Add("runner=run-d-acceptance-v3.ps1")
$meta.Add("started_local=" + $started.ToString('o'))
$meta.Add("outdir=" + $OutDir)
$meta.Add("iso_root=" + $iso)
$meta.Add("repo_root=" + $RepoRoot)

$exitCode = 0
$p = $null
if (-not (Test-Path $exe)) { T 'FATAL exe missing'; $meta.Add('fatal=exe_missing'); $meta | Set-Content (Join-Path $OutDir 'run-metadata.txt') -Encoding utf8; exit 2 }
$exeHash = (Get-FileHash $exe -Algorithm SHA256).Hash.ToLower()
T ('exe sha256=' + $exeHash)
$meta.Add("exe=" + $exe)
$meta.Add("exe_sha256=" + $exeHash)
$env:NEWMANGA_DATA_ROOT = $iso

try {
    $p = Start-Process -FilePath $exe -WorkingDirectory $exeDir -PassThru `
        -RedirectStandardOutput (Join-Path $OutDir 'app-out.log') -RedirectStandardError (Join-Path $OutDir 'app-err.log')
    T "pid=$($p.Id)"
    $dl = (Get-Date).AddSeconds($WindowWaitSeconds); $w=$null
    while((Get-Date) -lt $dl){
        Start-Sleep -Milliseconds 700
        if($p.HasExited){ T "FATAL early exit=$($p.ExitCode)"; break }
        $w=W; if($w){ break }
    }
    if(-not $w){ T 'FATAL no window'; A $false 'app:window'; $exitCode = 3 }
    else {
        A $true 'app:window'
        $rd=(Get-Date).AddSeconds(40)
        while((Get-Date) -lt $rd){ if(-not ((PN -join '|') -match 'starting')){break}; Start-Sleep -Milliseconds 700 }
        T 'READY'
        D '01-bookshelf'
        C '🛠️ 工作台' 'nav-workbench'|Out-Null; D '02-workbench'
        C '📖 阅读器' 'nav-reader'|Out-Null;   D '03-reader'
        C '⚙️ 设置'   'nav-settings'|Out-Null; D '04-settings'
        C 'Provider'  'cat-provider'|Out-Null; D '05-provider'
        $ok=C '新建 Profile' 'open-form'|Out-Null; D '06-form'
        SE 'provider_id' 'e2e-provider-a'|Out-Null
        SE 'display_name' 'E2E Provider A'|Out-Null
        SE 'endpoint（绝对 HTTP(S)，无 userinfo/query/fragment）' 'https://api.example.test/v1'|Out-Null
        SE 'model' 'e2e-model'|Out-Null
        TG 'OCR'|Out-Null
        $w2=W
        $bs=@($w2.FindAll($TS::Descendants,(New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::Button)))|%{$_.Current.Name})
        T ("FORM buttons: "+($bs -join ' | '))
        $sb=$null
        foreach($c in @('创建','创建 Profile','保存','确定','提交','Create','Save','OK','Submit')){ if($bs -contains $c){$sb=$c;break} }
        if($sb){
            C $sb 'submit'|Out-Null; Start-Sleep -Milliseconds 1500; D '07-after-submit'
            $txt=@((W).FindAll($TS::Descendants,$ANY)|%{$_.Current.Name})
            A (($txt -join '|') -match 'E2E Provider A') 'submit:profile-visible'
        } else { T 'SUBMIT BUTTON_NOT_FOUND'; A $false 'submit:button-found' }
        C '⚙️ 设置' 're-enter-settings'|Out-Null
        PR
        C '📚 书架' 'nav-back'|Out-Null; D '08-bookshelf-back'
    }
}
finally {
    if($p -and -not $p.HasExited){ $p.CloseMainWindow()|Out-Null; Start-Sleep -Seconds 2 }
    if($p -and -not $p.HasExited){ Stop-Process -Id $p.Id -Force }
    $ended = (Get-Date)
    T "closed exit=$($p.ExitCode)"
    T "RUN end checks=$script:Checks fails=$script:Fails"
    $meta.Add("ended_local=" + $ended.ToString('o'))
    $meta.Add("duration_s=" + [math]::Round(($ended-$started).TotalSeconds,1))
    $meta.Add("checks=$script:Checks")
    $meta.Add("fails=$script:Fails")
    # R3-005: non-zero exit when any key assertion failed.
    if ($exitCode -eq 0 -and $script:Fails -gt 0) { $exitCode = 1 }
    $meta.Add("exit_code=$exitCode")
    $meta | Set-Content (Join-Path $OutDir 'run-metadata.txt') -Encoding utf8
}
exit $exitCode
