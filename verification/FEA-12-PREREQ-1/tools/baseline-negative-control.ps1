#!/usr/bin/env pwsh
# FEA-12-PREREQ-1 / AC3 baseline negative control (run BEFORE any card change).
#
# Purpose: prove on the pre-change baseline head that
#   (A) the new delete/trash codes are NOT registered in the Host error projection, so the
#       existing allow-list projector degrades them to category=unknown WITHOUT rewriting the
#       original code string (the C-08 allowedRunErrorCodes pattern this card extends);
#   (B) the frozen (old) Core does not recognise the new M2-C1 rev 2.13 commands, so a new
#       Host request fails closed with a typed error envelope instead of being silently dropped.
#
# Read-only with respect to the repository: loads the already built Release assembly and runs
# the frozen sidecar copy against an isolated data root under the workspace temp directory.

param(
    # Optional overrides so the same probe can run against a temporary baseline worktree.
    [string]$RepoRoot = '',
    [string]$AssemblyPath = '',
    [string]$HeadLabel = ''
)

$ErrorActionPreference = 'Stop'
$root = if ($RepoRoot) { (Resolve-Path $RepoRoot).Path } else { (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path }
$dll = if ($AssemblyPath) { (Resolve-Path $AssemblyPath).Path } else { Join-Path $root 'apps/desktop-avalonia/src/NewManga.CoreClient/bin/Release/net9.0/NewManga.CoreClient.dll' }
$sidecar = 'G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy'
$coreExe = Join-Path $sidecar 'core_service.exe'
$tempRoot = 'G:\CODEX\New Manga.workspace\temp\FEA-12-PREREQ-1\baseline-live-core'

function Write-Section([string]$text) { Write-Output ''; Write-Output "==== $text ====" }

$head = (& git -C $root rev-parse HEAD).Trim()
$dllHash = (Get-FileHash -Algorithm SHA256 -Path $dll).Hash.ToLower()
Write-Section 'ENVIRONMENT'
Write-Output "repo_root=$root"
Write-Output "head=$head"
Write-Output "assembly=$dll"
Write-Output "assembly_sha256=$dllHash"
Write-Output "sidecar=$coreExe"
Write-Output "sidecar_exists=$(Test-Path $coreExe)"

Add-Type -Path $dll
$registry = [NewManga.CoreClient.Commands.HostCommandRegistry]
$dispatcher = [NewManga.CoreClient.Commands.HostCommandDispatcher]
$exType = [NewManga.CoreClient.Wire.CoreOperationException]
$codes = @(
    'BOOK_DELETE_STALE_PREVIEW',
    'BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE',
    'TRASH_ENTRY_NOT_FOUND',
    'TRASH_RESTORE_CONFLICT',
    'TRASH_RESTORE_LAYER_MISMATCH'
)
$newCommands = @(
    'library_preview_permanent_delete_books',
    'library_move_to_trash',
    'library_restore_from_trash',
    'library_list_trash',
    'library_purge_trash'
)

Write-Section 'A1 baseline registry (card commands absent)'
Write-Output "registry_command_count=$($registry::All.Count)"
foreach ($name in $newCommands) {
    $present = $registry::All.ContainsKey($name)
    Write-Output "command=$name present=$present"
}
foreach ($name in $newCommands) {
    try {
        $descriptor = $registry::Get($name)
        Write-Output "get=$name UNEXPECTED_OK core=$($descriptor.CoreCommand) minor=$($descriptor.CoreMinor)"
    }
    catch {
        $inner = $_.Exception
        while ($inner.InnerException) { $inner = $inner.InnerException }
        $code = if ($inner.PSObject.Properties.Name -contains 'Code') { $inner.Code } else { 'n/a' }
        Write-Output "get=$name typed_failure type=$($inner.GetType().Name) code=$code"
    }
}
$single = $registry::Get('library_delete_book_permanently')
$batch = $registry::Get('library_delete_books_permanently')
Write-Output "existing=single library_delete_book_permanently core=$($single.CoreCommand) minor=$($single.CoreMinor)"
Write-Output "existing=batch library_delete_books_permanently core=$($batch.CoreCommand) minor=$($batch.CoreMinor)"

Write-Section 'A2 baseline error projection degrades unknown new codes (code preserved)'
$allowed = $registry::AllowedRunErrorCodes
Write-Output "allowed_run_error_codes_count=$($allowed.Count)"
foreach ($code in $codes) {
    $operationError = $exType::new($code, 'conflict', $false, 'baseline probe', 'req-baseline')
    $projected = $dispatcher::ProjectRunError($operationError, $allowed)
    Write-Output ("code={0} registered={1} projected_code={2} category={3} retryable={4}" -f `
            $code, $allowed.Contains($code), $projected.Code, $projected.Category, $projected.Retryable)
}

Write-Section 'B frozen old Core rejects the rev 2.13 commands (typed, not silent)'
if (-not (Test-Path $coreExe)) {
    Write-Output 'RESULT: SKIPPED (frozen sidecar copy not available)'
    exit 0
}

if (Test-Path $tempRoot) { Remove-Item -Recurse -Force $tempRoot }
$dataRoot = Join-Path $tempRoot 'data'
$derived = Join-Path $dataRoot 'derived'
$catalog = Join-Path $dataRoot 'catalog/catalog.sqlite'
New-Item -ItemType Directory -Force -Path $derived, (Split-Path $catalog -Parent) | Out-Null

$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $coreExe
$psi.WorkingDirectory = $sidecar
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.Environment['NEWMANGA_DATA_ROOT'] = $dataRoot
$psi.Environment['M2RC1_DERIVED_ROOT'] = $derived
$psi.Environment['M2RC2_CATALOG_DB'] = $catalog
$process = [System.Diagnostics.Process]::Start($psi)
try {
    function Send-Frame([string]$label, [string]$command, [int]$minor, [string]$payloadJson) {
        $requestId = "fea12-baseline-$label"
        $line = '{"protocol":"new-manga.core","version":{"major":2,"minor":' + $minor +
                '},"request_id":"' + $requestId + '","command":"' + $command + '","payload":' + $payloadJson + '}'
        $process.StandardInput.WriteLine($line)
        $process.StandardInput.Flush()
        $response = $process.StandardOutput.ReadLine()
        Write-Output "request=$label command=$command version_minor=$minor"
        Write-Output "request_wire=$line"
        Write-Output "response_wire=$response"
    }

    Send-Frame 'ping' 'core.ping' 3 '{}'
    Send-Frame 'preview' 'PreviewPermanentDeleteBooks' 11 '{"bookIds":["book-baseline"]}'
    Send-Frame 'move-to-trash' 'MoveToTrash' 13 '{"entries":[{"book_id":"book-baseline"}],"idempotency_key":"baseline-1"}'
}
finally {
    try { $process.StandardInput.Close() } catch { }
    if (-not $process.WaitForExit(15000)) { try { $process.Kill($true) } catch { } }
    $stderr = $process.StandardError.ReadToEnd()
    if ($stderr) {
        Write-Output '--- core_service stderr tail ---'
        Write-Output (($stderr -split "`n") | Select-Object -Last 12 | Out-String).Trim()
    }
    Write-Output "core_exit_code=$($process.ExitCode)"
    $process.Dispose()
}

Write-Section 'RESULT'
Write-Output 'BASELINE_NEGATIVE_CONTROL=CAPTURED'
