# BOOK-FIXTURE-1 — 用隔离数据根启动 Avalonia App（复测入口）
#
# 用法：
#   pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1
#   pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1 -DataRoot <另一个隔离根>
#
# 只做三件事：解析 App 可执行文件（优先 FINAL-VALIDATION-1 发布件）、校验隔离数据根、
# 以 `--data-root <隔离根>` 启动（Host 会把同名 NEWMANGA_DATA_ROOT 传给 Core sidecar）。
# 不会读写真实 %APPDATA%；清理见 verification/BOOK-FIXTURE-1/RETEST.md。
[CmdletBinding()]
param(
    [string]$DataRoot = 'G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data',
    [string]$AppExe = '',
    [string]$S4Fixtures = 'G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1/fixtures',
    # READER-PROGRESS-1: extra AppOptions (e.g. --demo-write on an isolated root) for evidence runs.
    [string[]]$ExtraArgs = @(),
    [switch]$NoLaunch
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')

function Resolve-AppExe([string]$explicit) {
    if (-not [string]::IsNullOrWhiteSpace($explicit)) { return $explicit }
    $candidates = @(
        'G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/out/NewManga-0.1.0-win-x64/app/NewManga.App.exe',
        'G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/out/NewManga-0.1.0-win-x64-models/app/NewManga.App.exe',
        (Join-Path $repoRoot 'apps/desktop-avalonia/src/NewManga.App/bin/Release/net9.0/win-x64/publish/NewManga.App.exe')
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    throw "Avalonia App not found; pass -AppExe (build the RELEASE-PACKAGE-1/FINAL-VALIDATION-1 package first)"
}

$exe = Resolve-AppExe $AppExe
$appDir = Split-Path $exe -Parent
$sidecarDir = Join-Path $appDir 'core-sidecar'
$hasSidecar = Test-Path (Join-Path $sidecarDir 'core_service.exe')
$hasBook = Test-Path (Join-Path $DataRoot 'library.db')
if (-not $hasBook) {
    throw "no library.db under DataRoot=$DataRoot; run apps/desktop-avalonia/scripts/new-test-book.ps1 first"
}

Write-Host "app        : $exe"
Write-Host "data root  : $DataRoot"
Write-Host "sidecar    : $(if ($hasSidecar) { $sidecarDir } else { 'MISSING next to app (packaged build expected)' })"
Write-Host "models     : $(if ($hasSidecar -and (Test-Path (Join-Path $sidecarDir 'models'))) { 'bundled' } else { 'not bundled (detect/run needs a models package or NEWMANGA_DETECTOR_WEIGHTS)' })"
Write-Host ""
Write-Host "复测要点（详见 verification/BOOK-FIXTURE-1/RETEST.md）："
Write-Host "  1) 书架应出现「BOOK-FIXTURE-1 日漫_JA 测试书」；数据根 = $DataRoot"
Write-Host "  2) 现有壳层阅读器页仍是 S4 fixture（4000x60000 tile 长条 + 两张排版图），可用于 webtoon 工作集测量"
Write-Host "  3) 沉浸 Esc/H 目前无产品入口（ReaderWindow 未被实例化，见 RETEST.md 缺口）；该项 BLOCKED"
Write-Host "  4) 清理：Remove-Item -Recurse '$DataRoot'（只删隔离根，不动 %APPDATA%）"
Write-Host ""

if ($NoLaunch) {
    Write-Host "(-NoLaunch: not starting the app)"
    exit 0
}

# Reader fixtures are resolved from NEWMANGA_S4_FIXTURES by the shell; keep the
# documented fallback explicit so the same reader page is used on any machine.
if (Test-Path $S4Fixtures) { $env:NEWMANGA_S4_FIXTURES = $S4Fixtures }
# AppOptions only has --data-root=<value> form: a bare "--data-root <path>" would
# be parsed as the literal value "true" (AppOptions.Parse). The = form plus
# quotes is required because the workspace path contains a space.
$argLine = "--data-root=`"$DataRoot`"" + (($ExtraArgs | ForEach-Object { " $_" }) -join "")
Write-Host "launch args: $argLine"
$process = Start-Process -FilePath $exe -ArgumentList $argLine -PassThru
Write-Host "started NewManga.App.exe (pid=$($process.Id)); close the window (or kill the pid) to end the session."
