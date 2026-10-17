param([string]$RepoRoot='G:/CODEX/New Manga',[string]$OutDir='G:/CODEX/New Manga/verification/P19/d-run-v2')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient; Add-Type -AssemblyName UIAutomationTypes
$exe=Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'; $exeDir=Split-Path $exe
$iso=Join-Path $env:TEMP ('p19v2-'+[guid]::NewGuid().ToString('N').Substring(0,8)); $ud=Join-Path $OutDir 'uia'; $tr=Join-Path $OutDir 'trace.log'
New-Item -ItemType Directory -Force -Path $OutDir,$ud,$iso|Out-Null; Remove-Item $tr -ErrorAction SilentlyContinue
$AE=[System.Windows.Automation.AutomationElement]; $TS=[System.Windows.Automation.TreeScope]; $CT=[System.Windows.Automation.ControlType]; $ANY=[System.Windows.Automation.Condition]::TrueCondition
$TITLE='M2-RC1 resource channel runtime'
function T($m){ $l='['+(Get-Date -Format 'HH:mm:ss.fff')+'] '+$m; Add-Content -Path $tr -Value $l -Encoding utf8; Write-Host $l }
function W{ $c=New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$TITLE); $AE::RootElement.FindFirst($TS::Children,$c) }
function PN{ $w=W; if(-not $w){return @()}; $c=New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::Pane); @($w.FindAll($TS::Descendants,$c)|%{$_.Current.Name}) }
function D($tag){ $w=W; if(-not $w){T "DUMP $tag MISSING";return}; $all=$w.FindAll($TS::Descendants,$ANY); $ls=New-Object System.Collections.Generic.List[string]; $ls.Add("# $tag n=$($all.Count) $(Get-Date -Format o)"); for($i=0;$i -lt $all.Count;$i++){ $e=$all[$i]; try{ $ty=($e.Current.ControlType.ProgrammaticName -replace 'ControlType\.',''); $ls.Add("$i|$ty|$($e.Current.Name)|en=$($e.Current.IsEnabled)|off=$($e.Current.IsOffscreen)") }catch{} }; Set-Content -Path (Join-Path $ud "$tag.uia.txt") -Value $ls -Encoding utf8; T "DUMP $tag n=$($all.Count)" }
function F($n,$ct=$null){ $w=W; if(-not $w){return $null}; $cs=New-Object System.Collections.Generic.List[object]; $cs.Add((New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty,$n))); if($ct){$cs.Add((New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$ct)))}; $c=if($cs.Count -gt 1){New-Object System.Windows.Automation.AndCondition($cs.ToArray())}else{$cs[0]}; $w.FindFirst($TS::Descendants,$c) }
function C($n,$why){ $e=F $n $CT::Button; if(-not $e){T "CLICK $why '$n' NOT_FOUND";return $false}; $en=$e.Current.IsEnabled; try{ $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 900; T "CLICK $why '$n' OK en=$en"; return $true }catch{ T "CLICK $why '$n' FAILED en=$en $($_.Exception.Message)"; return $false } }
function SE($n,$v){ $e=F $n $CT::Edit; if(-not $e){T "SET $n EDIT_NOT_FOUND";return $false}; try{ $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($v); Start-Sleep -Milliseconds 300; T "SET $n='$v' OK"; return $true }catch{ T "SET $n FAILED"; return $false } }
function TG($n){ $e=F $n $CT::CheckBox; if(-not $e){T "TOGGLE $n NOT_FOUND";return $false}; try{ $p=$e.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern); $p.Toggle(); Start-Sleep -Milliseconds 300; T "TOGGLE $n OK state=$($p.Current.ToggleState)"; return $true }catch{ T "TOGGLE $n FAILED"; return $false } }
function PR{ foreach($n in @('OCR 未开放','图片修复 未开放','排版样式 未开放','模型/GPU 未开放','任务/并发 未开放','缓存/Revision 未开放','回收站 未开放','备份/恢复 未开放','Plugin/Hooks 未开放')){ $e=F $n $CT::Button; if(-not $e){T "PROBE '$n' NOT_FOUND";continue}; $en=$e.Current.IsEnabled; $b=(PN -join '|'); $iv='n/a'; try{ $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 600; $iv='invoked' }catch{ $iv='failed' }; $a=(PN -join '|'); $ch=if($b -eq $a){'PAGE_UNCHANGED'}else{'PAGE_CHANGED'}; $na=@((PN)|?{$_ -match '未开放'}); T "PROBE '$n' en=$en invoke=$iv $ch panes=[$($na -join '/')]" } }

T "RUN start iso=$iso"
if(-not(Test-Path $exe)){ T 'FATAL exe missing'; exit 2 }
T ('exe sha256='+(Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())
$env:NEWMANGA_DATA_ROOT=$iso
$p=Start-Process -FilePath $exe -WorkingDirectory $exeDir -PassThru -RedirectStandardOutput (Join-Path $OutDir 'app-out.log') -RedirectStandardError (Join-Path $OutDir 'app-err.log')
T "pid=$($p.Id)"; $dl=(Get-Date).AddSeconds(45); $w=$null
while((Get-Date) -lt $dl){ Start-Sleep -Milliseconds 700; if($p.HasExited){T "FATAL early exit=$($p.ExitCode)";break}; $w=W; if($w){break} }
if(-not $w){ T 'FATAL no window'; if(-not $p.HasExited){$p.CloseMainWindow()|Out-Null}; exit 3 }
$rd=(Get-Date).AddSeconds(40); while((Get-Date) -lt $rd){ if(-not ((PN -join '|') -match 'starting')){break}; Start-Sleep -Milliseconds 700 }
T 'READY'
try{
  D '01-bookshelf'
  C '🛠️ 工作台' 'nav-workbench'|Out-Null; D '02-workbench'
  C '📖 阅读器' 'nav-reader'|Out-Null; D '03-reader'
  C '⚙️ 设置' 'nav-settings'|Out-Null; D '04-settings'
  C 'Provider' 'cat-provider'|Out-Null; D '05-provider'
  $ok=C '新建 Profile' 'open-form'; D '06-form'
  SE 'provider_id' 'e2e-provider-a'|Out-Null; SE 'display_name' 'E2E Provider A'|Out-Null; SE 'endpoint（绝对 HTTP(S)，无 userinfo/query/fragment）' 'https://api.example.test/v1'|Out-Null; SE 'model' 'e2e-model'|Out-Null; TG 'OCR'|Out-Null
  $w2=W; $bs=@($w2.FindAll($TS::Descendants,(New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty,$CT::Button)))|%{$_.Current.Name}); T ("FORM buttons: "+($bs -join ' | '))
  $sb=$null; foreach($c in @('创建','创建 Profile','保存','确定','提交','Create','Save','OK','Submit')){ if($bs -contains $c){$sb=$c;break} }
  if($sb){ C $sb 'submit'|Out-Null; Start-Sleep -Milliseconds 1500; D '07-after-submit'; $txt=@((W).FindAll($TS::Descendants,$ANY)|%{$_.Current.Name}); if(($txt -join '|') -match 'E2E Provider A'){T 'SUBMIT PROFILE_VISIBLE -> PASS'}else{T 'SUBMIT PROFILE_NOT_VISIBLE -> FAIL'} } else { T 'SUBMIT BUTTON_NOT_FOUND -> INCONCLUSIVE' }
  C '⚙️ 设置' 're-enter-settings'|Out-Null; PR
  C '📚 书架' 'nav-back'|Out-Null; D '08-bookshelf-back'
}
finally{ if(-not $p.HasExited){$p.CloseMainWindow()|Out-Null;Start-Sleep -Seconds 2}; if(-not $p.HasExited){Stop-Process -Id $p.Id -Force}; T "closed exit=$($p.ExitCode)"; T 'RUN end' }
