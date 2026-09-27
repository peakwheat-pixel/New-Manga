# M2-S1 fixed-point / environment reconnaissance.
#
# Read-only. Emits a deterministic transcript so the Owner branch base,
# clone shape (standalone vs linked worktree), fixed Contract blob and
# environment can be re-derived by the non-author Reviewer.
#
# Run:
#   pwsh -NoProfile -File verification/M2-S1/probes/00_recon.ps1 `
#     | Tee-Object -FilePath verification/M2-S1/raw/00-recon.log
#
# No product code, no user library, no network.

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $repo

function Emit([string]$label, [scriptblock]$body) {
    Write-Output "--- $label ---"
    try { & $body 2>&1 | ForEach-Object { "$_" } }
    catch { "EXCEPTION: $($_.Exception.Message)" }
}

Write-Output "# M2-S1 reconnaissance transcript"
Write-Output ("# generated_utc: " + [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))
Write-Output ("# repo: " + $repo)

Emit 'git rev-parse --show-toplevel'      { git rev-parse --show-toplevel }
Emit 'git rev-parse --git-dir'            { git rev-parse --git-dir }
Emit 'git rev-parse --absolute-git-dir'   { git rev-parse --absolute-git-dir }
Emit 'git rev-parse --git-common-dir'     { git rev-parse --git-common-dir }
Emit 'git rev-parse HEAD'                 { git rev-parse HEAD }
Emit 'git rev-parse --abbrev-ref HEAD'    { git rev-parse --abbrev-ref HEAD }
Emit 'git rev-parse --short HEAD'         { git rev-parse --short HEAD }
Emit 'git status --porcelain=v1 --branch' { git status --porcelain=v1 --branch }
Emit 'git remote -v'                      { git remote -v }
Emit 'git worktree list'                  { git worktree list }
Emit 'worktree-marker .git/commondir exists?' {
    if (Test-Path (Join-Path (git rev-parse --absolute-git-dir) 'commondir')) { 'YES (linked worktree)' } else { 'NO (standalone clone)' }
}
Emit '.git/objects/info/alternates exists?' {
    if (Test-Path (Join-Path (git rev-parse --absolute-git-dir) 'objects\info\alternates')) { 'YES' } else { 'NO' }
}
Emit '.git/config'                        { Get-Content (Join-Path (git rev-parse --absolute-git-dir) 'config') }
Emit 'refs/remotes/origin/master'         { git rev-parse refs/remotes/origin/master }
Emit 'git log -3 --oneline --decorate'    { git log -3 --oneline --decorate }
Emit 'fixed Contract blob (HEAD:...) '    { git rev-parse 'HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md' }
Emit 'fixed base blob (base:...) '        { git rev-parse '85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md' }
Emit 'origin/master Contract blob'        { git rev-parse 'origin/master:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md' }
Emit 'tracked file counts'                {
    "all=" + (git ls-files | Measure-Object -Line).Lines
    "src=" + (git ls-files src | Measure-Object -Line).Lines
    "tests=" + (git ls-files tests | Measure-Object -Line).Lines
    "verification/M2-S1=" + (git ls-files verification/M2-S1 | Measure-Object -Line).Lines
}
Emit 'git version'                        { git --version }
Emit 'python --version'                   { python --version }
Emit 'python executable'                  { (Get-Command python).Source }
Emit 'OS version'                         { [System.Environment]::OSVersion.VersionString }
Emit 'pwsh version / language mode'       { "$($PSVersionTable.PSVersion) / $($ExecutionContext.SessionState.LanguageMode)" }
Emit 'TEMP'                               { $env:TEMP }
Emit 'processor identifier'               { $env:PROCESSOR_IDENTIFIER }
Emit 'processor architecture'             { $env:PROCESSOR_ARCHITECTURE }
Emit 'logical processors'                 { $env:NUMBER_OF_PROCESSORS }
Emit 'USERNAME / USERDOMAIN'              { "$env:USERNAME / $env:USERDOMAIN" }
Emit 'host memory / python facts'         { python (Join-Path $PSScriptRoot '00_meminfo.py') }
Emit 'disk free on C:'                    { Get-PSDrive C | ForEach-Object { "UsedGB=$([math]::Round($_.Used/1GB,2)) FreeGB=$([math]::Round($_.Free/1GB,2))" } }
Write-Output "# END"
