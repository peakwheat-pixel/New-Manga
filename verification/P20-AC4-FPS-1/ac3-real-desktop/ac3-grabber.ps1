# AC3 抢抓器：在 runner TEARDOWN 关闭 App 之前抓走面板 CSV/JSON
# 背景：run-ac4-fps.ps1 的 ValuePattern 抓取必然失败（WebView2 返回 null），
#       且失败后约 6 秒即 TEARDOWN 关闭 App，手工抓取窗口极短。
# 本脚本以 0.4s 轮询 trace，检测到 SCROLL end 立即用 TextPattern 抓取。
param([string]$OutDir, [string]$Label)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$trace = Join-Path $OutDir 'fps-trace.log'
$deadline = (Get-Date).AddMinutes(30)
Write-Output "[grabber] watching $trace for 'SCROLL end label=$Label'"

while ((Get-Date) -lt $deadline) {
    if (Test-Path $trace) {
        $t = Get-Content $trace -Raw -ErrorAction SilentlyContinue
        if ($t -match "SCROLL end label=$Label") {
            Write-Output "[grabber] SCROLL end detected at $(Get-Date -Format 'HH:mm:ss.fff')"
            $app = Get-Process -Name m2rc1-desktop -ErrorAction SilentlyContinue | Select-Object -First 1
            if (-not $app) { Write-Output "[grabber] APP_ALREADY_GONE"; exit 3 }
            $root = [System.Windows.Automation.AutomationElement]::RootElement
            $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $app.Id)
            $win = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $cond)
            if (-not $win) { Write-Output "[grabber] WINDOW_GONE"; exit 3 }

            function ClickBtn($name) {
                $c = New-Object System.Windows.Automation.AndCondition(
                    (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)),
                    (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)))
                $b = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $c)
                if ($b) { try { $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); return $true } catch { return $false } }
                return $false
            }
            function ReadTextarea() {
                $els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
                foreach ($e in $els) {
                    try {
                        if (($e.Current.ControlType.ProgrammaticName -replace 'ControlType\.','') -eq 'Edit') {
                            $t = $e.GetCurrentPattern([System.Windows.Automation.TextPattern]::Pattern).DocumentRange.GetText(-1)
                            if ($t -match '^seq,frame_ts_ms' -or $t -match '^\s*\{\s*"') { return $t }
                        }
                    } catch {}
                }
                return $null
            }
            function ReadDocName() {
                $els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
                foreach ($e in $els) {
                    try { $n = $e.Current.Name; if ($n -match '^M2FPS ') { return $n } } catch {}
                }
                return $null
            }

            # 顺序：先抓 DOC 摘要（不加锁、最快）
            $doc = ReadDocName
            if ($doc) { $doc | Set-Content (Join-Path $OutDir "fps-$Label-title-summary.txt") -Encoding utf8 -NoNewline; Write-Output "[grabber] DOC: $doc" }

            # Show CSV -> 读
            [void](ClickBtn 'FPS: Show CSV'); Start-Sleep -Milliseconds 900
            $csv = ReadTextarea
            if ($csv -and $csv -match '^seq,frame_ts_ms') { $csv | Set-Content (Join-Path $OutDir "fps-$Label-samples.csv") -Encoding utf8 -NoNewline; Write-Output "[grabber] CSV saved: $($csv.Length) chars" }
            else { Write-Output "[grabber] CSV_MISS" }

            # Show JSON -> 读
            [void](ClickBtn 'FPS: Show JSON'); Start-Sleep -Milliseconds 900
            $json = ReadTextarea
            if ($json -and $json -match '^\s*\{\s*"') { $json | Set-Content (Join-Path $OutDir "fps-$Label-summary.json") -Encoding utf8 -NoNewline; Write-Output "[grabber] JSON saved: $($json.Length) chars" }
            else { Write-Output "[grabber] JSON_MISS" }

            # 抢在 runner 关闭前再确认一次 App 状态
            Write-Output "[grabber] app_alive=$((Get-Process -Id $app.Id -ErrorAction SilentlyContinue) -ne $null)"
            exit 0
        }
    }
    Start-Sleep -Milliseconds 400
}
Write-Output "[grabber] TIMEOUT"
exit 4
