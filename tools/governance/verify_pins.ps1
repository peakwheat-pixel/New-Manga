#!/usr/bin/env pwsh
# Verify every frozen-contract pin matches the contract file's actual SHA-256.
# Root cause this guards against: computing the pin before the freeze commit's last edit.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$map = @{
 'C01b'='FEA-C01b_STORAGE_CONTRACT_DRAFT.md'; 'C02'='FEA-C02_V11R_AMENDMENT_DRAFT.md';
 'C03'='FEA-C03_PRESENTATION_SETTINGS_DRAFT.md'; 'C04b'='FEA-C04b_DELETE_PROTOCOL_DRAFT.md';
 'C05'='FEA-C05_PAGE_VISIBILITY_DRAFT.md'; 'C06'='FEA-C06_SOURCE_AUTH_DRAFT.md';
 'C07'='FEA-C07_API_INVENTORY.md'; 'C08'='FEA-C08_RUN_SNAPSHOT_DRAFT.md';
 'C11'='FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md'; 'C12'='FEA-C12_CHECKER_SCOPE_DRAFT.md';
 'C13'='FEA-C13_DRAFT_PROTECTION_DRAFT.md'; 'C14'='FEA-C14_SOURCE_RELOCATION_DRAFT.md'; 'C15'='FEA-C15_SOURCE_STORAGE_DRAFT.md'; 'C16'='FEA-C16_SOURCE_READ_WIRE_DRAFT.md'; 'C09'='FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md'; 'C10'='FEA-C10_INTERACTION_DRAFT.md'; 'FEA01'='FEA-01_CONTRACT_DRAFT.md'; 'C17'='FEA-C17_SOURCE_SYNC_DRAFT.md'
}
$bad = 0
foreach ($id in ($map.Keys | Sort-Object)) {
  $rec = Join-Path $root "doc/plan/FEA-CONTRACT-FROZEN-$id.md"
  $src = Join-Path $root "doc/plan/$($map[$id])"
  if (-not (Test-Path $rec)) { Write-Output "MISSING-RECORD $id"; $bad++; continue }
  if (-not (Test-Path $src)) { Write-Output "MISSING-CONTRACT $id"; $bad++; continue }
  $m = Select-String -Path $rec -Pattern '\|\s*sha256[^|]*\|\s*`([0-9a-f]{64})`' | Select-Object -First 1
  if (-not $m) { Write-Output "NO-PIN $id"; $bad++; continue }
  $pin = $m.Matches[0].Groups[1].Value
  $act = (Get-FileHash -Algorithm SHA256 -Path $src).Hash.ToLower()
  if ($pin -ne $act) { Write-Output "MISMATCH $id pin=$($pin.Substring(0,12)) actual=$($act.Substring(0,12))"; $bad++ }
  else { Write-Output "OK $id $($pin.Substring(0,12))" }
}
if ($bad -gt 0) { Write-Output "PIN AUDIT: FAIL ($bad)"; exit 1 }
Write-Output "PIN AUDIT: PASS (all $($map.Count))"
exit 0
