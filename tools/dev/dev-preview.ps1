# DEV-PREVIEW-1: 本地开发预览启动器（改完即见，不生成安装包）
#
# 背景：tauri.conf.json 只有 frontendDist（打包用），没有 devUrl，所以
# `cargo tauri dev` 无法直接热更新；同时 src-tauri 的 dev 路径强制要求
# M2RC1_SRC_ROOT / M2RC1_DERIVED_ROOT / M2RC1_MANAGED_ROOT / M2RC2_CATALOG_DB
# （见 src/main.rs 的 expect 契约）。
#
# 本脚本使用 dev-only 覆盖配置，并通过环境变量启用 build.rs 的本地预览例外；
# 冻结的生产 Tauri 配置保持不变：
#   1. 启动 Vite dev server（http://localhost:5188，HMR）
#   2. 用 --config 覆盖方式加载 tauri.dev.conf.json（devUrl + dev-only CSP）
#   3. 所有可写数据根都钉在 workspace 的隔离目录，不碰用户数据
#
# 用法（仓库根目录或任意目录均可）：
#   pwsh -NoProfile -File tools/dev/dev-preview.ps1
#   pwsh -NoProfile -File tools/dev/dev-preview.ps1 -NoVite     # 已手动起好 vite
#
# 结束：Ctrl+C 关闭桌面窗口后，脚本会顺带停掉自己启动的 Vite 进程。

[CmdletBinding()]
param(
    # 复用已经在跑的 Vite（不再由本脚本启动/停止）
    [switch]$NoVite,
    # 只起 Vite 浏览器预览，不编译 Rust（纯 UI 预览用）
    [switch]$ViteOnly
)

$ErrorActionPreference = 'Stop'

# Vite 端口固定 5188：必须与 apps/desktop/frontend/vite.config.ts（server.port +
# strictPort）和 apps/desktop/src-tauri/tauri.dev.conf.json（build.devUrl）一致；
# 声明为常量、不提供参数覆盖，避免「等错端口 / devUrl 指向别处」的配置漂移。
Set-Variable -Name VitePort -Value 5188 -Option Constant

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$frontendDir = Join-Path $repoRoot 'apps\desktop\frontend'
$srcTauriDir = Join-Path $repoRoot 'apps\desktop\src-tauri'
$devConfPath = Join-Path $srcTauriDir 'tauri.dev.conf.json'
$dataRoot = 'G:\CODEX\New Manga.workspace\dev-preview\data'

if (-not (Test-Path -LiteralPath $devConfPath -PathType Leaf)) {
    throw "缺少 dev 覆盖配置: $devConfPath"
}

function Test-PortListening {
    param([int]$Port)
    return $null -ne (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1)
}

function Wait-PortListening {
    param([int]$Port, [int]$TimeoutSeconds = 90)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-PortListening -Port $Port) { return $true }
        Start-Sleep -Milliseconds 400
    }
    return $false
}

# 校验 $Port 上是「本项目的 Vite dev server」，而不是碰巧占用端口的其它服务。
# 判据（IPv4/IPv6 任一栈探测成功即可，但两条判据须同时满足）：
#   1) GET /@vite/client 返回 200 —— Vite dev server 的独有端点；
#   2) GET / 的 HTML 引用 /src/main.tsx —— 本项目 index.html 的入口。
# 判据 2 与 apps/desktop/frontend/index.html 耦合，改动入口路径时同步这里。
# -NoProxy：本机可能配置全局代理（如 127.0.0.1:7890），环回探测必须直连。
function Test-OurVite {
    param([int]$Port)
    foreach ($probeHost in @('127.0.0.1', '[::1]')) {
        try {
            $root = Invoke-WebRequest -Uri "http://${probeHost}:$Port/" -UseBasicParsing -NoProxy -TimeoutSec 5
            if ($root.StatusCode -ne 200) { continue }
            $client = Invoke-WebRequest -Uri "http://${probeHost}:$Port/@vite/client" -UseBasicParsing -NoProxy -TimeoutSec 5
            if ($client.StatusCode -eq 200 -and "$($root.Content)" -match '/src/main\.tsx') {
                return $true
            }
        } catch {
            continue
        }
    }
    return $false
}

# 复用端口上的服务前调用；身份不明时 fail-closed 退出，并给出占用者排查指引。
function Assert-ReusableVite {
    param([int]$Port)
    if (Test-OurVite -Port $Port) { return }
    $hint = ''
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($listener) {
        $owner = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
        $hint = "（当前占用：pid $($listener.OwningProcess)，进程名 $(if ($owner) { $owner.ProcessName } else { '未知' })）"
    }
    throw @"
端口 $Port 被占用，且 HTTP 探测确认它不是本项目的 Vite dev server$hint。
为避免把其它应用的页面装进带真实 IPC 的 Tauri 窗口，脚本拒绝复用（fail-closed）。
排查占用者：
  Get-NetTCPConnection -LocalPort $Port -State Listen | Format-List LocalAddress,LocalPort,OwningProcess
  Get-Process -Id <OwningProcess>
若它确实是刚启动、尚未就绪的本项目 Vite，等几秒重试；否则请先结束该进程释放 $Port。
"@
}

# 只清理「本次启动」的进程树：按记录的 PID + 进程创建时间核对，绝不按端口反查，
# 防止本脚本的 Vite 提前退出、端口被其它进程接管后误杀对方。
# taskkill /T 覆盖 cmd.exe -> npm -> node.exe(Vite) 整条链。
function Stop-LaunchedTree {
    param(
        [int]$ProcessId,
        [Nullable[datetime]]$StartTime,
        [string]$Label
    )
    $live = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $live) {
        Write-Host "[dev-preview] $Label (pid $ProcessId) 已自行退出，无需清理"
        return
    }
    $liveStart = $null
    try { $liveStart = $live.StartTime } catch { }
    if ($null -eq $StartTime -or $null -eq $liveStart -or $liveStart -ne $StartTime) {
        Write-Warning "[dev-preview] pid $ProcessId 与本次启动的 $Label 不匹配（PID 可能已被复用），跳过清理以免误杀；如确认无其它用途，可手动 Stop-Process -Id $ProcessId"
        return
    }
    Write-Host "[dev-preview] 停止 $Label 进程树 (pid $ProcessId)"
    & "$env:SystemRoot\System32\taskkill.exe" /PID $ProcessId /T /F | Out-Null
}

# --- 隔离的可写数据根（workspace，不进 Git） --------------------------------
$dirs = [ordered]@{
    derived  = Join-Path $dataRoot 'derived'
    managed  = Join-Path $dataRoot 'managed'
    dataRoot = Join-Path $dataRoot 'data-root'
    catalog  = Join-Path $dataRoot 'catalog'
    webview2 = Join-Path $dataRoot 'webview2-udd'
}
foreach ($dir in $dirs.Values) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# --- 单实例锁 + 残留清理 ------------------------------------------------------
# 开发预览共用同一份 WebView2 用户数据目录与 SQLite 目录；两个实例并发启动会
# 互相锁死（WebView2 0x800700AA「请求的资源在使用中」/ sqlite unable to open
# database file）。另外应用 panic 时 Python Core 子进程可能成为孤儿并继续占用
# catalog.sqlite，所以启动前先清理「父进程已死」的本项目残留，再用文件锁阻止并发。
$lockPath = Join-Path $dataRoot '.dev-preview.lock'
try {
    $script:devPreviewLock = [System.IO.File]::Open(
        $lockPath,
        [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None)
} catch {
    throw @"
[dev-preview] 另一个预览实例正在启动或运行（锁文件被占用：$lockPath）。
请先关闭已打开的预览窗口，等待其完全退出后再试。
"@
}

$stale = @()
# 持有锁后：父进程已死的 Core sidecar 一定是崩溃孤儿。
$stale += Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match 'bootstrap\.core_service|infrastructure\.resource_channel\.host_bridge' -and
    -not (Get-Process -Id $_.ParentProcessId -ErrorAction SilentlyContinue)
}
# 持有锁后：任何使用本 UDF 的 WebView2 进程都不可能是合法实例（合法实例已被锁排除），
# 它们会锁住 profile 导致下一次创建报 0x800700AA，因此全部清理。
$stale += Get-CimInstance Win32_Process -Filter "Name='msedgewebview2.exe'" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match 'dev-preview\\data\\webview2-udd'
}
foreach ($proc in $stale) {
    Write-Host "[dev-preview] 清理上次崩溃残留进程: pid $($proc.ProcessId) $($proc.Name)"
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
}
if ($stale.Count -gt 0) { Start-Sleep -Milliseconds 800 }

$running = Get-Process -Name 'm2rc1-desktop' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($running) {
    throw @"
[dev-preview] 已有 m2rc1-desktop 在运行（pid $($running.Id)），拒绝并发启动。
预览与正式版共用 WebView2 用户数据目录与 SQLite 目录，两个实例同时运行会导致
WebView2 报 0x800700AA（资源在使用中）或 SQLite 报 unable to open database file。
请先关闭已打开的应用窗口（或结束该进程）后再启动预览。
"@
}

# --- dev 模式环境（同时清掉会切到 probe/ac1/packaged 模式的开关） -----------
Remove-Item Env:M2RC1_PROBE_OUT  -ErrorAction SilentlyContinue
Remove-Item Env:M2AC1_TEST_MODE  -ErrorAction SilentlyContinue
Remove-Item Env:M2RC1_PACKAGED   -ErrorAction SilentlyContinue
Remove-Item Env:M2RC1_FIXTURES   -ErrorAction SilentlyContinue

$env:M2RC1_SRC_ROOT     = Join-Path $repoRoot 'src'
$env:M2RC1_DERIVED_ROOT = $dirs.derived
$env:M2RC1_MANAGED_ROOT = $dirs.managed
$env:NEWMANGA_DATA_ROOT = $dirs.dataRoot
$env:M2RC2_CATALOG_DB   = Join-Path $dirs.catalog 'catalog.sqlite'
# WebView2 用户数据目录隔离到 workspace：既不与已安装的正式版争用默认
# %LOCALAPPDATA%\<identifier>\EBWebView，也保证崩溃残留不会污染正式版。
$env:WEBVIEW2_USER_DATA_FOLDER = $dirs.webview2
if (-not $env:M2RC1_PYTHON) {
    $python = (Get-Command python -ErrorAction SilentlyContinue)
    if ($python) { $env:M2RC1_PYTHON = $python.Source }
}

Write-Host "[dev-preview] repo      = $repoRoot"
Write-Host "[dev-preview] data roots= $dataRoot"
Write-Host "[dev-preview] vite      = http://localhost:$VitePort"

# --- Vite 启动/等待与 cargo tauri dev 共用同一 try/finally ------------------
# Vite 的启动与 90s 就绪等待也纳入 try：等待超时、依赖缺失、Ctrl+C 等任何
# 异常路径都会进入 finally，清理且只清理本次启动的进程树。
$viteProcess = $null
$viteStartTime = $null

try {
    # --- 1. Vite dev server --------------------------------------------------
    if ($NoVite) {
        if (-not (Test-PortListening -Port $VitePort)) {
            throw "-NoVite 指定了复用 Vite，但 $VitePort 端口没有监听"
        }
        Assert-ReusableVite -Port $VitePort
        Write-Host "[dev-preview] 复用已运行的 Vite ($VitePort)"
    } elseif (Test-PortListening -Port $VitePort) {
        Assert-ReusableVite -Port $VitePort
        Write-Host "[dev-preview] $VitePort 已在监听，复用现有 Vite"
    } else {
        if (-not (Test-Path -LiteralPath (Join-Path $frontendDir 'node_modules') -PathType Container)) {
            throw "前端依赖缺失：先在 $frontendDir 执行 npm ci"
        }
        $npmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue)
        if (-not $npmCmd) { throw 'npm.cmd 不在 PATH 中' }
        $viteLog = Join-Path $dataRoot 'vite.log'
        $viteErr = Join-Path $dataRoot 'vite.err.log'
        Write-Host "[dev-preview] 启动 Vite（日志: $viteLog）"
        $viteProcess = Start-Process -FilePath $env:ComSpec `
            -ArgumentList '/c', "`"$($npmCmd.Source)`" run dev" `
            -WorkingDirectory $frontendDir `
            -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput $viteLog -RedirectStandardError $viteErr
        try { $viteStartTime = $viteProcess.StartTime } catch { $viteStartTime = $null }
        if (-not (Wait-PortListening -Port $VitePort -TimeoutSeconds 90)) {
            throw "Vite 在 90 秒内没有监听 $VitePort（看 $viteErr）"
        }
        Write-Host "[dev-preview] Vite 就绪"
    }

    if ($ViteOnly) {
        $url = "http://localhost:$VitePort"
        Write-Host "[dev-preview] -ViteOnly：浏览器打开 $url 即可（假数据预览）"
        try {
            Start-Process $url | Out-Null
        } catch {
            Write-Warning "[dev-preview] 自动打开浏览器失败，请手动访问 $url"
        }
        if ($null -ne $viteProcess) {
            Write-Host '[dev-preview] 已尝试自动打开浏览器；按 Ctrl+C 结束，结束后 Vite 会被停止'
            while ($true) { Start-Sleep -Seconds 1 }
        }
        return
    }

    # --- 2. cargo tauri dev（devUrl 指向 Vite；Rust 改动自动重编） ----------
    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        throw 'cargo 不在 PATH 中（无法编译桌面壳）'
    }
    Write-Host '[dev-preview] cargo tauri dev（首次编译较慢；改 React 立即 HMR，改 Rust 自动重编）'
    $env:M2RC1_DEV_PREVIEW = '1'
    try {
        Push-Location $srcTauriDir
        try {
            # WebView2 在 profile 被残留进程占用时会立刻返回 0x800700AA（资源忙），
            # 属于瞬时故障：清理该 UDF 的 WebView2 进程后重试一次即可恢复。
            $attempt = 0
            $maxAttempts = 2
            do {
                $attempt++
                $captured = [System.Collections.Generic.List[string]]::new()
                & cargo tauri dev --config $devConfPath 2>&1 | ForEach-Object {
                    $captured.Add("$_")
                    $_
                }
                $exit = $LASTEXITCODE
                $joined = $captured -join "`n"
                if ($exit -ne 0 -and $attempt -lt $maxAttempts -and $joined -match '0x800700AA') {
                    Write-Host "[dev-preview] WebView2 报告资源忙（0x800700AA），清理残留后自动重试（第 $($attempt + 1)/$maxAttempts 次）…"
                    Get-CimInstance Win32_Process -Filter "Name='msedgewebview2.exe'" -ErrorAction SilentlyContinue |
                        Where-Object { $_.CommandLine -match 'dev-preview\\data\\webview2-udd' } |
                        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
                    Start-Sleep -Seconds 3
                    continue
                }
                break
            } while ($true)
        } finally {
            Pop-Location
        }
    } finally {
        Remove-Item Env:M2RC1_DEV_PREVIEW -ErrorAction SilentlyContinue
    }
    if ($exit -ne 0) {
        # 0xFFFFFFFF (-1)：应用窗口被用户关闭（或进程被结束），Tauri CLI 会打印一条
        # `error: process didn't exit successfully ... (exit code: 0xffffffff)`。
        # 这是正常结束路径，不是编译失败；此处明确区分，避免误导。
        if ($exit -eq -1 -or $exit -eq 4294967295) {
            Write-Host '[dev-preview] 应用窗口已关闭（Tauri 退出码 -1 / 0xffffffff），预览正常结束。'
        } else {
            Write-Warning "[dev-preview] cargo tauri dev 退出码 $exit —— 编译或启动失败，请查看上方报错原文。"
        }
    }
} finally {
    if ($null -ne $viteProcess) {
        Stop-LaunchedTree -ProcessId $viteProcess.Id -StartTime $viteStartTime -Label 'Vite'
        if (Test-PortListening -Port $VitePort) {
            Write-Warning "[dev-preview] 清理后 $VitePort 仍被占用；脚本不按端口反查进程（防误杀）。若并非你手动起的其它服务，请确认：Get-NetTCPConnection -LocalPort $VitePort -State Listen"
        }
    }
    if ($script:devPreviewLock) {
        try { $script:devPreviewLock.Dispose() } catch { }
        $script:devPreviewLock = $null
    }
}
