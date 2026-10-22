# P02PRE-R1G 冻结 Manifest（R1F one-shot recovery；PowerShell 7.6.6）

## 基线与裁决

- **Historical pin errata (R-007)**：最早 Task AC1 记录 `7246 / 7A1E711E8A1B1E85C91D6948BF8EEF6A797E80DCBAB5ED04EEEF41843F51C4BC`；manifest 早期头部记录 `6677 / F47B1249D57BD630F927E6E964E2243396999008CE584172E13C67D75995321B`，两者不一致且均已过期。首轮 DSH Review prompt 实际冻结 Task=`10012 / BB686F68873DD09160B403B4D85843E803FB8C84B94DB211683D658EDBAC0995`、manifest=`10599 / BC103E0B7032561DF20AA2D0F91D226ED690915F476054F25D805C0455693D3E`；这两组也是历史 snapshot，不表示当前文件字节。下一轮 exact Task/manifest pins 由新 DSH prompt 外部冻结，作为 Review 输入。
- Predecessor Task=`doc/tasks/P02PRE-R1F.md`；原 Review input=`30565 / C39E9CB2730A2C6EE37153A945093D276FD2BD8F951E302C764EF776D2F5EAE7`。R1F Task 在 R1G 初始冻结时的 post-run 文档快照=`32536 / 3C3F1BA523475B6D70A720766D5CE2BC077D5DB56D4EFF94B6D789472F7E398C`；它已被后续 Review 集成取代。两组值均明确是历史版本 pins，不表示当前 Task 文件状态。
- R1F capture manifest 在 R1G 初始冻结时的原始版本=`44417 / 7F251BD0C2283192DFC53ACB0338E171AC369D24C1CDB859684809DD5A33FA73`；后续 post-run Review addendum 已追加。当前 R1F Task/manifest pins 由最新 recovery checkpoint 和 R1G dispatch prompt 分别记录，不沿用本行历史值作为当前文件 hash。
- R1F script=`verification/P02/p02pre-r1f-capture.ps1`，`67582 / 5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316`。
- R1F failed one-shot JSON=`verification/P02/p02pre-r1f-evidence-20261011.json`，`23131 / DCB22B8EE1FC7ED824FDE12CDA68BE208DCDBAD9D88531C5E3171C0396F7CF70`；它不是 R1G baseline，也不得覆盖。
- DSH post-run Review continuation #1=`verification/P02/dsh-p02pre-r1f-postrun-review-followup1-20261011.stdout.md`，`7704 / 67DCF1502498188D49A7E9779FF6956CEF80CAF64BB21BBD53DF886BD237FBDF`，decision=`CHANGES_REQUESTED (0/0/2/2)`。Codex 对四项 finding 的 adjudication=`verification/P02/p02pre-r1f-postrun-adjudication-20261011.md`，以实际文件 hash 为准。
- R1F evidence proves only failure at main `.git/index` prehash due `Get-FileHash` `CommandNotFoundException`; module-discovery cause is `UNPROVABLE`. No evidence proves PowerShell 7 incompatibility. R1G uses a new engine contract and therefore requires fresh candidate Review and pre-run release.

## Owner、Review、工作区

- R1G implementation Owner=`Antigravity`；non-author Reviewer=`DeepSeek Harness`（两次派发未形成有效 Review）；follow-up 2=`Codex independent Reviewer sub-agent`，其 `CHANGES_REQUESTED` 已由 Codex adjudicate；Task/manifest owner and final Integrator/Adjudicator=`Codex /root`。
- Repo=`G:\CODEX\New Manga`，main base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Antigravity branch=`agent/antigravity/P02PRE-R1G`；linked worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；common-dir=`G:/CODEX/New Manga/.git`；initial worktree status clean. The worktree does not contain main’s uncommitted files; Antigravity reads the frozen R1F source from the absolute main path and writes only its assigned new files in this worktree.
- Parent runtime and exact no-profile child both observed=`PowerShell 7.6.6 / Core`, `pwsh.exe` path=`C:\Program Files\PowerShell\7\pwsh.exe`; capability preflight PASS evidence=`verification/P02/p02pre-r1g-engine-preflight-20261011.json` (PID=33564, exit=0, expected modules/cmdlets, FullLanguage).

## Inherited scope and exact deltas

除下列明示差异外，R1G 完整继承 R1F manifest 的 identity、main/scratch roots/refs、`.tmp.driveupload` path-only exclusion、tracked symlink no-follow、Git argv/order、96 protected path policy、TEMP/cache/scratch/WER/registry/ACL getter allowlist、失败关闭和禁止项。Agent 不得扩张 R1F 的 OS/path/query 范围。

唯一功能性差异：

1. Child executor 从 R1F Windows PowerShell 5.1 改为固定 `C:\Program Files\PowerShell\7\pwsh.exe` / PowerShell `7.6.6` / PSEdition=`Core`。
2. Capture 前单独运行 no-profile engine capability preflight。该 preflight 只读取 `$PSVersionTable`、`$PSHOME`、`$env:PSModulePath`、`$ExecutionContext.SessionState.LanguageMode`、`Get-Command Get-FileHash`、`Get-Command Get-Acl`，以及 `Microsoft.PowerShell.Utility` / `Microsoft.PowerShell.Security` 模块的 name/version/path；不得运行 capture script、Git、host getter、registry/ACL/profile API、Build/Cargo/AC。Parent 将其原始 stdout/stderr/exit 与结构化记录缓冲在内存；进程退出后仅以 `CreateNew` 写 engine-preflight JSON。任何 exit/version/edition/path/language/command/module mismatch 均停止，不启动 capture。
3. Candidate script 在 evidence JSON 中记录 child runtime、实际阶段状态和 stop detail。至少有阶段 `identity`、`mainRepository`、`scratchRepository`、`environment`、`paths`、`wer`、`protectedHashes`；未进入阶段必须显式为 `NOT_REACHED`，当前失败阶段标 `FAILED`，不得沿用初始化 `UNPROVABLE` 冒充已执行。错误要区分 runtime prerequisite、repository prehash、inventory/query stop。
4. Parent runner 以 .NET `ProcessStartInfo.ArgumentList` 启动固定 child，记录完整 executable/argv/CWD/PID/exit、source file SHA-256 before 与 after、stdout/stderr byte length/hash。源文件哈希来自 parent 对冻结路径的读取，只能证明 pre/post 文件 pin 未变，**不能**声称 OS 已证明进程映射/执行的字节。stdout/stderr 先内存缓冲；child exit 后以 `CreateNew` 写文件。runner/evidence 目标已存在则不启动，不覆盖、不重试。
5. 新 script 使用新 task id、manifest/evidence paths；除上述状态字段/engine attestation 与 runtime contract 外，代码行为应保持最小差异。R1F 原文件和所有 R1F outputs 永远只读。

## Executor 与命令契约

- Candidate=`verification/P02/p02pre-r1g-capture.ps1`。
- Engine preflight child executable=`C:\Program Files\PowerShell\7\pwsh.exe`，exact argv=`-NoLogo -NoProfile -NonInteractive -Command <manifest 所列固定 preflight code>`，CWD=`G:\CODEX\New Manga`。
- Exact preflight code（整串作为一个 `-Command` argument，通过 `ProcessStartInfo.ArgumentList` 传入）：

```powershell
$ErrorActionPreference='Stop'; $mods=@(Get-Module -ListAvailable Microsoft.PowerShell.Utility,Microsoft.PowerShell.Security | ForEach-Object {[ordered]@{name=$_.Name;version=$_.Version.ToString();path=$_.Path}}); $cmds=[ordered]@{}; foreach($n in @('Get-FileHash','Get-Acl')){$c=Get-Command -Name $n -ErrorAction Stop; $cmds[$n]=[ordered]@{commandType=$c.CommandType.ToString();source=$c.Source;version=[string]$c.Version}}; $o=[ordered]@{version=$PSVersionTable.PSVersion.ToString();edition=$PSVersionTable.PSEdition;psHome=$PSHOME;modulePath=$env:PSModulePath;languageMode=$ExecutionContext.SessionState.LanguageMode.ToString();modules=$mods;commands=$cmds}; ConvertTo-Json -InputObject $o -Depth 8 -Compress
```

- Preflight PASS requires exit=0; `version=7.6.6`; `edition=Core`; `psHome=C:\Program Files\PowerShell\7`; `languageMode=FullLanguage`; both required commands resolve from the expected PowerShell module family. Module names/version/path and full `PSModulePath` are recorded as evidence, not used as a write allowlist. Any mismatch/error means no capture child start.
- Capture child executable 同上，exact argv=`-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File verification/P02/p02pre-r1g-capture.ps1`，CWD=`G:\CODEX\New Manga`。
- 唯一允许 capture child processes 继承 R1F manifest 的 Git executable 和 `whoami.exe /all`；不得新增 shell、package manager、network、compiler、COM、helper 或未知子进程。`ProcessStartInfo.ArgumentList` 与 actual child PID 必须留证。
- R1G candidate child launcher contract：`Invoke-CapturedProcess` 必须接受 argument array，逐项加入 `.ArgumentList` 并在 evidence 中记录同一有序 `argumentList`；不得用 `.Arguments` 拼接命令字符串。Git 共用固定 argv prefix `--no-optional-locks`, `-c`, `core.quotepath=false`, `-c`, `core.fsmonitor=false`, `-c`, `core.untrackedCache=false`, `-C`, `<Root>`，其后分别接当前 `Invoke-Git` 各 call site 的 Git 参数项；`whoami.exe` 唯一参数为 `/all`。当前 status pathspec `:(exclude).tmp.driveupload` 必须作为一个 argv 元素传入；不得访问该排除路径。命令、参数顺序、子进程范围不可扩张。
- Candidate self-check 在独立 no-profile PowerShell 7 child 中 parse exact bytes、运行纯函数内存 assertions；不 dot-source/invoke capture、不运行 host getter。Parser/self-check artifact 由 Codex在 dispatch 后缓冲采集，使用新唯一目标。

## 唯一输出目标与写入

- Agent-owned candidate files：
  - `verification/P02/p02pre-r1g-capture.ps1`
  - `verification/P02/p02pre-r1g-author-selfcheck-20261011.json`
  - `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md`
- Codex-owned engine/runtime evidence：
  - `verification/P02/p02pre-r1g-engine-preflight-20261011.json`
  - `verification/P02/p02pre-r1g-selfcheck-20261011.json`
  - `verification/P02/p02pre-r1g-runner-evidence-20261011.json`
  - `verification/P02/p02pre-r1g-evidence-20261011.json`
  - `verification/P02/p02pre-r1g-capture-20261011.stdout.log`
  - `verification/P02/p02pre-r1g-capture-20261011.stderr.log`
  - `verification/P02/p02pre-r1g-capture-20261011.exit`
- DSH pre-review：`verification/P02/dsh-p02pre-r1g-review-20261011.prompt.md`、`.stdout.md`、`.stderr.log`、`.exit`。
- DSH post-review：`verification/P02/dsh-p02pre-r1g-postrun-review-20261011.prompt.md`、`.stdout.md`、`.stderr.log`、`.exit`。
- Codex adjudication/checkpoint：`verification/P02/p02pre-r1g-adjudication-20261011.md`、`verification/P02/codex-checkpoint-p02pre-r1g-20261011.md`。
- All targets are individually checked absent immediately before their creation. Candidate evidence is created once by the child using `FileMode.CreateNew`. Parent artifacts are created only after relevant child exits, also with `CreateNew`. No append/overwrite/move/delete/cleanup/retry.

## Codex 集成已审查 capture source（R-004）

R1G capture 的命令使用 main CWD=`G:\CODEX\New Manga` 与相对路径 `-File verification/P02/p02pre-r1g-capture.ps1`；当前 main destination 只读存在性核查为 absent，candidate 仅位于 Antigravity linked worktree。为避免执行未经审查或未 pin 的复制品，必须按以下受控集成顺序使该相对路径解析到已审查字节：

1. 新一轮 DeepSeek Harness Review 必须以 Codex 独立 pre-dispatch pin evidence 和 worktree branch HEAD 为冻结事实；当前候选 branch=`agent/antigravity/P02PRE-R1G`、HEAD=`6e1c00fee3db07805c92c25cdc311af9279ceb51`、source=`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga\verification\P02\p02pre-r1g-capture.ps1`、`80593 bytes / SHA-256 2CC9C49F0708B4D174749ACE5F3C92BCD6D6B2E2825CA908412BCE2B2436778F`。若 HEAD 或 pin 改变，重新冻结并 Review。DSH 只做 exact-path 内容审查，不负责计算 pins；Codex 在 Review 后复算所有输入 pins，不匹配则 Review 无效。
2. Review 与 Codex adjudication 通过后，Codex 再核对 main destination `G:\CODEX\New Manga\verification\P02\p02pre-r1g-capture.ps1` 仍 absent；从上述精确 worktree source 读取 bytes，以 `FileMode.CreateNew` 新建 destination，flush 后复算 destination size/SHA。任何异常、target 已存在或 hash 不同都停止；不覆盖、不删除、不清理、不重试。
3. Capture 前再核对 main source hash 与 Review pin 精确相同，并在 runner evidence 中记录 absolute source/destination、worktree HEAD、size/SHA、CreateNew 与 post-copy check。随后才按本 manifest 的 main CWD 与相对 `-File` argv 执行。该 integration 只新增已审查脚本文件，不隐含执行或证明脚本。

Handoff 不在自身内容中写入包含它自己的 delivery HEAD；Codex 在本 Task、adjudication 和 checkpoint 中外部记录最终交付 HEAD。

## 2026-10-12 parser/self-check 与 PowerShell 7 engine preflight

- Integrated candidate parser/self-check=`PASS`，PowerShell 7.6.6/Core，PID=46780，exit=0、stderr=0、parse errors=0；selected pure-function assertions、inventory policy/serialization/parser 与 bounded phase-map assertions 全部通过。Capture/getter/registry-ACL-profile API/Build/Cargo/AC 均未调用。Evidence=`verification/P02/p02pre-r1g-selfcheck-20261011.json`（6225 / `AE4F21E7BD39B037BEFD5B686C4FB9FB74864530B886C36437F182541938874E`）。
- Exact no-profile capability preflight=`PASS`，PowerShell 7.6.6/Core、FullLanguage，PID=33564，exit=0、stderr=0；expected PSHOME、Microsoft.PowerShell.Utility/Security modules 与 `Get-FileHash` / `Get-Acl` 均匹配。Capture/Git/host getter/profile/registry/ACL/build/AC 均未调用。Evidence=`verification/P02/p02pre-r1g-engine-preflight-20261011.json`（4121 / `903C1C37BBFD5836B6196DF08F903E9063C5415E84D5415D0828060B207480CB`）。
- Live main=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。Final pre-run remains ACTIVE; capture remains `BLOCKED / NOT_RUN` until explicit `PRE_RUN_PASS`.
## Release sequence and stop conditions

1. Antigravity commits only its three assigned files to the task branch. Codex validates branch/base/common-dir, exact allowed diff, selfcheck pins and clean status; no direct merge by Agent.
2. The first DSH report and later DSH follow-up attempt are retained but neither is accepted for AC4 release. The first had a directory-enumeration policy deviation; the later trace used prohibited `grep` four times, read a Codex pin artifact omitted from the exact-path table, and had no final response. The later DSH dispatch also used the main repository CWD instead of the reviewed linked worktree root required by `doc/09_COLLABORATION.md` §6.1. Codex assigned a separate non-author Reviewer sub-agent under §1 as the fallback. It reviews only the frozen Task/manifest/script/selfcheck/Handoff and prior adjudication inputs; it does not write files, run code, or access `.tmp.driveupload`. Codex verifies frozen pins and adjudicates; neither failed DSH attempt is treated as a Review.
3. After a compliant Review and Codex adjudication, Codex integrates the exact reviewed script bytes from the pinned branch source into the absent main destination using `CreateNew`; source and destination hashes must match the Review pin, as specified above. If the destination exists or any byte differs, stop.
4. Codex runs isolated parse/self-check and no-profile engine preflight on the exact integrated candidate. Any mismatch means `CAPTURE=BLOCKED / NOT_RUN`; no capture start.
5. Codex freezes checkpoint and rechecks identity/SID, refs, Git status/index, 96 protected hashes, Task/manifest/review/source pins, main integrated source hash and all output targets absent. Failure keeps capture blocked.
6. After explicit Codex `PRE_RUN_PASS`, execute one capture. Any unknown child, identity mismatch, unauthorized access/write, output-target collision, timeout or evidence anomaly stops and preserves all produced evidence. No retry.
7. DeepSeek Harness post-run Review, Codex five-state adjudication and Plan/STATUS/checkpoint refresh. R1G review/parse/preflight/capture evidence never automatically changes a P02 Gate.
## 2026-10-12 remediation Review round 1 — BLOCKED_BY_MISSING_EVIDENCE

- Reviewer=`DeepSeek Harness` (non-author); DSH session=`session-a35eed45-d8d3-4676-8955-03bd630f9927`; CLI exit=0; original verdict=`BLOCKED_BY_MISSING_EVIDENCE`, P1 `RP-001`.
- Frozen prompt=`verification/P02/dsh-p02pre-r1g-remediation-review-20261012.prompt.md`; stdout=`verification/P02/dsh-p02pre-r1g-remediation-review-20261012.stdout.jsonl`. Codex audited 8 tool calls; all were exact-path `read`, no shell/PowerShell/Git/tests/glob/grep/subagent/enumeration/write or out-of-scope path. The prompt incorrectly required the Reviewer to calculate bytes/SHA while allowing only a read tool that exposes neither; adjudication=`verification/P02/p02pre-r1g-remediation-review-adjudication-20261012.md`, `CONFIRMED / ACCEPTED` as process mismatch, not candidate Review approval.
- Codex post-review rehashed all nine prompt paths and matched each frozen pin; evidence=`verification/P02/codex-p02pre-r1g-review-input-pins-remediation-20261012.json`. DSH itself did not independently verify the hashes. Its candidate-code observations are advisory only and do not close previous findings.
- Codex independently confirmed candidate `Invoke-CapturedProcess` uses `.Arguments` string concatenation despite the `.ArgumentList` child contract; Antigravity owns the minimal fix under the existing three-file path allowance. No parser/preflight/capture is implied.

## 2026-10-12 owner repair completed; DSH follow-up 1 invalidated; Codex Reviewer fallback — SUPERSEDED BY FOLLOW-UP 2

- Antigravity Owner delivery HEAD=`6e1c00fee3db07805c92c25cdc311af9279ceb51`; prior Owner HEAD=`6943c6727c82c706d90a3ed4c14617b04c98d360`. Codex verified only the existing three candidate files changed, worktree clean, `git diff --check` exit=0, exact argv arrays and updated Handoff/self-check pins. Delivery adjudication=`verification/P02/p02pre-r1g-argumentlist-delivery-adjudication-20261012.md`; this is not independent Review or runtime evidence.
- Handoff reports one `git status --porcelain` invocation in the linked worktree without the approved exclusion pathspec. Whether its same-named relative excluded path was queried is `WORKTREE_RELATIVE_EXCLUDED_PATH_ACCESS=NOT_VERIFIED`; this does not establish access to the main repository path. Codex used the exact exclusion in its own subsequent status checks and did not access that path. Reviewer should decide whether this process uncertainty affects content-review acceptance; do not query the excluded path.
- Current script pin=`80593 / 2CC9C49F0708B4D174749ACE5F3C92BCD6D6B2E2825CA908412BCE2B2436778F`; author self-check=`2462 / 016FA5BA0FCA16FCDB63D62CD0BAF5B723DE5AEF0A6B392DA13C41D88230AEB6`; Handoff=`22604 / 2996A3D05E9010C73F7D57B7249532EB3B33FE071E071FA009968B38DFE1D716`.
- Codex creates and verifies a pin-evidence artifact before Reviewer assignment. Reviewer assesses content only and does not calculate hashes; Codex rehashes the exact same inputs after Review and invalidates the Review if any pin differs.
- Follow-up DSH targets: `verification/P02/dsh-p02pre-r1g-remediation-review-followup1-20261012.prompt.md`, `.stdout.jsonl`, `.stderr.log`, `.exit`; pre/post Codex pin evidence=`verification/P02/codex-p02pre-r1g-review-input-pins-followup1-20261012.json`. No verdict is assumed before raw trace and response adjudication.
- DSH follow-up 1 adjudication=`verification/P02/p02pre-r1g-review-followup1-dispatch-adjudication-20261012.md`; post-review pin evidence=`verification/P02/codex-p02pre-r1g-review-input-pins-followup1-post-20261012.json`. Trace records 16 `read`, 4 `grep`, 1 incomplete tool call, 1 out-of-table pin-file read; DSH process stopped without a final response or observed exit code. All 12 source pins matched after stop. This is `INVALIDATED / NOT_A_REVIEW`, not AC4 evidence.
- Next Reviewer=`Codex independent Reviewer sub-agent` (non-author; project protocol §1 fallback after DSH procedure deviations); root Codex remains Integrator/Adjudicator. Review output=`verification/P02/codex-subagent-p02pre-r1g-review-followup2-20261012.md`; pre/post pins=`verification/P02/codex-p02pre-r1g-review-input-pins-fallback-20261012.json` and `verification/P02/codex-p02pre-r1g-review-input-pins-fallback-post-20261012.json`.
## 2026-10-12 independent Codex Reviewer follow-up 2 — SUPERSEDED BY OWNER FOLLOW-UP 3 DELIVERY

- Reviewer=/root/p02_r1g_review_fallback（Codex Reviewer role；非作者），root=Codex /root。Reviewed branch=agent/antigravity/P02PRE-R1G，HEAD=6e1c00fee3db07805c92c25cdc311af9279ceb51，controlled worktree clean，base→HEAD 恰为原三文件。
- Valid Review=CHANGES_REQUESTED，P0/P1/P2/P3=0/0/2/0。Report=verification/P02/codex-subagent-p02pre-r1g-review-followup2-20261012.md（6016 / B84B1A6183D2727420D04CF51EC916BEB5567C8E07E15CA02C79A7D8387F5AF9）；Codex adjudication=verification/P02/p02pre-r1g-review-followup2-adjudication-20261012.md（3091 / DA6270AD689AB9DEA60122194F301EA348438965AC4DE9F21602C429A4528412）。Root rehashed the exact 12 frozen inputs; pre/post/current all 12/12 MATCH.
- R-009 / P2 accepted and open: if a WER directory record is REPARSE_POINT or NOT_DIRECTORY, set WER classification and phase to FAILED, record exact stop detail, and do not run protectedHashes/ACL stability. Existing query errors remain fail-stop. No reparse point was followed or target content-read evidence inferred.
- R-010 / P2 accepted and open: both JSON fallback objects must retain the fixed bounded full phase map, including aclStability, without serializing unbounded Result/inventory.
- Current Active Task=P02PRE-R1G，status=in_progress / R-009_R-010_REPAIR_ACTIVE；Owner=Antigravity；exact prompt=verification/P02/antigravity-p02pre-r1g-review-fixes3-20261012.prompt.md（3495 / 902CDE94377D0714DDDBC79540568FC95B46B9D0E519B163240C4D5E7302D58A）。Allowed candidate writes remain the same three branch files. After delivery, Codex validates scope and freezes new pins; non-author Reviewer reviews fixes before parser/self-check/preflight/capture release.
- Parser/self-check/preflight/capture/host getters/Build/Cargo/AC1–AC7 remain NOT_RUN. The prior DSH round 1 blocked and follow-up 1 invalidated results remain unchanged. WORKTREE_RELATIVE_EXCLUDED_PATH_ACCESS=NOT_VERIFIED.

## 2026-10-12 Owner follow-up 3 delivery — accepted for independent Review

- Antigravity resumed existing conversation 4cd35c4c-6a12-4953-bb4f-3bde5d687b6e with CLI 1.3.3. Dispatch JSON status=SUCCESS, exit=0. Branch=agent/antigravity/P02PRE-R1G；base=cddff58469b56e181019a8ddfeade80684bc7eb9；delivery HEAD=946938bd0696dfddd01f87d61fe6723c63ecdc86；tree=09c8241cb0f4af509004eed070a10bb292d933c7；controlled status clean；base→HEAD exactly the three authorized files.
- Codex delivery adjudication=verification/P02/p02pre-r1g-r009-r010-delivery-adjudication-20261012.md, 3832 / 8F020377B5BDA73DF12A0123600CD3D52F6A9A23FDB0D3A3E2F9F125E1EEDAE7 . Captured stdout=verification/P02/antigravity-p02pre-r1g-review-fixes3-20261012.stdout.json (13503 / 16B51CD430BD84AB0FF49C5B951C658104B5EDD07C91800E6909BC21F01C00E8), stderr=0 / E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855, exit marker=3 / 13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354.
- New pins confirmed by Codex: candidate script 81991 / 3C7D85AB3E20C023873197FE391B8F22DFB319038F43B7C554DC4F38927AADDF; self-check 2462 / 54D71B4F10F4520F12D7EB41389BE750301A6A726ECCE8655A3D7CCDEAC4B20C; Handoff 18665 / F221C8020F47C64544476DCB3AFCFAE1FAEC0F31E1B0767856FA4AC17A10B770.
- Delivery is ACCEPTED_FOR_INDEPENDENT_REVIEW only. R-009/R-010 remain subject to a new non-author Review. Review prompt=verification/P02/codex-subagent-p02pre-r1g-review-followup3-20261012.prompt.md; pre/post pin evidence targets=verification/P02/codex-p02pre-r1g-review-input-pins-followup3-20261012.json and verification/P02/codex-p02pre-r1g-review-input-pins-followup3-post-20261012.json; report target=verification/P02/codex-subagent-p02pre-r1g-review-followup3-20261012.md.
- No parser/self-check/preflight/capture/host getter/Build/Cargo/AC was run. Owner-reported absence of main-repository reads has no complete command trace; it is not independent path-access evidence. Prior WORKTREE_RELATIVE_EXCLUDED_PATH_ACCESS=NOT_VERIFIED remains.
- Main candidate is absent and not integrated. No AC4 release or Gate status change.

## Gate and risk invariants

## 2026-10-12 follow-up 3 independent Review — APPROVED_STATIC_CONTENT
- Exact main integration target (Codex `CreateNew`) and evidence output=`verification/P02/p02pre-r1g-integration-followup3-20261012.json`; create only after all three main candidate destinations are proven absent and candidate branch/HEAD/source pins match the Review pins.
- Codex integration completed after all three main destinations were confirmed absent: `CreateNew` from exact reviewed worktree HEAD; source and destination bytes/SHA-256 match the review pins, source stayed stable, and main HEAD remains `cddff58469b56e181019a8ddfeade80684bc7eb9`. Evidence=`verification/P02/p02pre-r1g-integration-followup3-20261012.json` (3553 bytes / `8682D89CC66FA982CC95B5B6EC649EF12B611D1963EE9C4E655BEC736ED0DF44`). No commit or staging was performed.

- Non-author Reviewer=`/root/p02_r1g_review_followup3`（Codex Reviewer，gpt-6.1-sol / medium），branch=`agent/antigravity/P02PRE-R1G`，base=`cddff58469b56e181019a8ddfeade80684bc7eb9`，reviewed HEAD=`946938bd0696dfddd01f87d61fe6723c63ecdc86`。Verdict=`APPROVED_STATIC_CONTENT`，findings P0/P1/P2/P3=`0/0/0/0`。报告=`verification/P02/codex-subagent-p02pre-r1g-review-followup3-20261012.md`；Codex adjudication=`verification/P02/p02pre-r1g-review-followup3-adjudication-20261012.md`。

- Root independently checked the same 11 exact content inputs before and after Review: `11/11 MATCH`; post-pin evidence=`verification/P02/codex-p02pre-r1g-review-input-pins-followup3-post-20261012.json`. The pre-pin JSON contains a metadata-only `mainGit.controlledStatus.nulRecords=0` summary error; correction artifact=`verification/P02/codex-p02pre-r1g-review-input-pins-followup3-correction-20261012.json` records the correct freeze count 873. All 11 content pins match unchanged.

- Codex disposition: R-009 and R-010=`FIXED_STATIC`; close those static Review findings. Parser/self-check, PS7 no-profile child capability, OS isolation/write closure, capture, Build/Cargo, and AC1–AC7 remain unrun/unverified. This Review does not release Build Gate or Hard Build Barrier.

Keep exact values: `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; exact text `technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. R1G is read-only, and does not create/delete profiles or write registry/ACL. Windows Sandbox remains untouched.
