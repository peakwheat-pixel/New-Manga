# P02PRE-R1F Round 3 独立 Review

你是本任务的非作者 Reviewer。请对以下冻结对象做只读、基于文件内容的独立审查，并将结论直接输出为 Markdown。不要编辑或创建仓库文件；不要运行任何命令、PowerShell parser、capture script、host getter、OS/token/path/ACL/TEMP/cache/WER/registry query、Build/Cargo 或 AC1–AC7。

## 固定 Review 对象

基线：仓库 G:/CODEX/New Manga，branch main，HEAD cddff58469b56e181019a8ddfeade80684bc7eb9；工作区原有 dirty/untracked 内容保留。

1. Task：doc/tasks/P02PRE-R1F.md，11487 bytes，SHA-256 736C470C01199D268E64C65CEE0497A26026EB8F3441A9879DDAC9FA32E05F21
2. Manifest：verification/P02/p02pre-r1f-manifest-20261011.md，12368 bytes，SHA-256 C19171CC5991733DD419C4C7E6BD74B506FA6E649196EFBBE261E19E3EDA9F98
3. Capture script：verification/P02/p02pre-r1f-capture.ps1，55603 bytes，SHA-256 4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54
4. Codex PS 5.1 isolated self-check evidence：verification/P02/p02pre-r1f-r2-selfcheck-20261011.json，1548 bytes，SHA-256 FE1989875B773AF7C02CB3A05CA9ED25AA9F7AB7581F57D4CB3D77CE055DDB96
5. Previous Round 2 report for finding context only: verification/P02/dsh-p02pre-r1f-review-r2-20261011.stdout.md

Codex reports independently matching local hashes using .NET SHA-256, Get-FileHash, and certutil; please do not claim your own hash verification unless you actually performed it.

## Review focus

- Verify the exact P02PRE-R1F read-only scope, host/root identity checks, stop/fail-closed behavior, child-process allowlist and the sole CreateNew evidence write against Task and Manifest.
- Check tracked-symlink behavior: skip only the exact leaf where Git index mode is 120000 and the live leaf has ReparsePoint; do not follow/hash/ACL-query the target; other reparse/mode mismatches stop.
- Reassess Round 2 finding R1F-R2-F1: the report alleged conditional comparison output could leak from Assert-InventoryPolicySelfCheck. The delivered code explicitly discards the assertion call's output. The attached Codex-only PS 5.1 evidence parsed the exact current source, extracted only Get-InventoryAction and Assert-InventoryPolicySelfCheck, ran them in memory, and reports output count 0 with capture/getter/write not invoked. Decide whether this closes the observable-output concern, without treating it as host execution evidence.
- Verify Round 2 finding R1F-R2-F2: repositoryOmittedCountKnown must be true only when both repository candidate lists are known; otherwise aggregate repositoryOmittedPaths must remain null.
- Verify Round 2 finding R1F-R2-F3: the nonexistent planned R5 parser path must not be in the protected-file list; final R6 parser path is present and must exist with matching source hash before capture.
- Check PowerShell 5.1 compatibility and the Task/Manifest/script alignment, including exact paths, no stale release steps, and no expansion of write permissions.
- Treat the owner risk decisions below as governance state only; they do not substitute for technical evidence or approve the capture/build.

## Prior findings

Round 1 decision=CHANGES_REQUESTED (P0/P1/P2/P3=0/1/2/2); F1–F5 were independently marked closed in Round 2. Round 2 decision=CHANGES_REQUESTED (0/0/0/3) with the three P3 findings above. Codex addressed them in the reviewed source. Confirm each one against the exact frozen bytes and state whether any remains open.

## Required report structure

1. Exact objects reviewed and any access limitation.
2. Decision exactly one of APPROVED, APPROVED_WITH_CONDITIONS, or CHANGES_REQUESTED, plus P0/P1/P2/P3 counts.
3. Finding table with severity, file/line, evidence, and disposition; explicitly adjudicate R1F-R2-F1/F2/F3 and prior F1–F5.
4. Scope/security findings and limitations.
5. State clearly that static review is not runtime evidence and does not release capture or any Gate.

For this Task's release criterion, Codex needs an exact APPROVED with no open findings. If you cannot establish that, use CHANGES_REQUESTED and describe the smallest required repair. Do not return a recommendation to ask the user: current authorization permits the work, but it does not imply PASS.

## Governance state to preserve

private_registry_absence=UNPROVABLE; Technical Gate=NOT_SATISFIED; Owner Risk Acceptance=APPROVED; Gate Disposition=WAIVED_BY_OWNER; Build Authorization=AUTHORIZED_WITH_EXCEPTION; exact residual-risk text=technical condition unmet; user explicitly accepted residual risk. Build Gate remains BLOCKED; Hard Build Barrier remains EFFECTIVE; Build/Cargo=NOT_RUN; AC1–AC7=BLOCKED / NOT_RUN. Do not call Windows Sandbox or alter it.
