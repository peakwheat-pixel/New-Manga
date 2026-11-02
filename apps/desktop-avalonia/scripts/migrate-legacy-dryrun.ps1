[CmdletBinding()] param([string]$LegacyRoot=$(Join-Path $env:APPDATA 'com.newmanga.desktop'),[string]$TargetRoot=$(Join-Path $env:APPDATA 'com.newmanga.desktop'))
$ErrorActionPreference='Stop'
$plan=@{dry_run=$true;legacy_root=$LegacyRoot;target_root=$TargetRoot;legacy_exists=(Test-Path $LegacyRoot);actions=@()}
if(Test-Path $LegacyRoot){$files=Get-ChildItem $LegacyRoot -Recurse -File -ErrorAction SilentlyContinue; $bytes=($files|Measure-Object Length -Sum).Sum
 $plan.actions+=@{action='copy';source=$LegacyRoot;target=$TargetRoot;bytes=$bytes;files=$files.Count;note='copy-only, no delete, idempotent; dry-run writes nothing'}}
else{$plan.actions+=@{action='none';note='legacy Tauri data root not found (fresh install)'}}
$plan.writes_performed=0
$plan|ConvertTo-Json -Depth 5
