# Scope Delta：P02 Scratch Build Process Isolation Design r2

- 时间：2026-10-09（Asia/Shanghai）。状态：`FROZEN_FOR_R2_REPAIR`。
- 父子任务：父 Task=`P02`（仍 `in_progress / ACTIVE`）；Codex-only 子任务=`P02 Scratch Build Process Isolation Design`；r1 Review 固定候选=`c542a31b102cdc5c129efd9df155a2760ed777b2`，tree=`5af3d8b4de75da0be13ce3fbbc81df26fabb9f7f`。
- Owner=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。当前工作 branch=`codex/P02-process-isolation`，worktree=`C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`。

## 变更原因

DeepSeek Harness 在 `dsh-review-process-isolation-r1.response.md` 的 R-03 指出，Standalone clone 路径及形态必须同步登记进 P02 的 Codex-only scratch boundary；当前登记仍说 `scratch worktree`，且没有固定 host 路径。此 scope delta 由 Codex 在用户持续有效的 PROJECT_ORCHESTRATION_AUTHORIZATION 下签发，仅关闭该设计的治理登记差异。

## 精确修改许可

在 `doc/tasks/P02.md` 中，只允许修改标题为 `Codex-only scratch-build output boundary` 的现有段落：把工作目录形态从 scratch worktree 更新为独立 non-linked clone，固定 clone 的 host 绝对路径为 `G:\CODEX\P02-scratch-build-source`，记录来源 commit `7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`、`git clone --no-hardlinks`、clone 内 common Git directory、无 alternates、清空 origin 与硬链接逐文件复核要求；保留现有输出 allowlist、Task 状态及禁止范围。路径在创建时必须不存在；若占用即 BLOCKED，不得自行换址。

本修订不改 P02 产品范围、AC、Owner allowlist、共享 IPC/Schema、产品代码、依赖、实现角色、用户数据边界或 Git 协作规则；不改变 P02 当前唯一 Active Task。

## r2 允许路径

- `doc/tasks/P02.md`：仅上述 Codex-only scratch-build output boundary 段落。
- `verification/P02/codex-scratch-build-process-isolation-proposal-r1.md`
- `verification/P02/codex-scratch-build-plan.md`
- `verification/P02/codex-scratch-build-gate.md`
- `verification/P02/codex-process-isolation-root-start-manifest.json`
- `verification/P02/codex-checkpoint-p02-process-isolation-start-r1.md`（保留原文；只读）
- `verification/P02/codex-checkpoint-p02-process-isolation-review-r1.md`
- `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`
- 本子任务 `verification/P02/**` 下的 Review、prompt、dispatch、evidence 与 checkpoint 附件。

其他项目路径、root 203 项未提交现场、Owner worktree 与 common `.git` 均不在本轮可写范围。

## 交付与 Gate

- 逐项关闭或明确保持 BLOCKED/NOT_VERIFIED：R-01 至 R-11；不得把缺失的运行态事实转写为 PASS。
- 通过路线校验、Markdown 链接校验、`git diff --check` 后，固定新 commit；由 DeepSeek Harness 对 exact HEAD 进行独立复审。
- 复审通过最多允许尝试隔离 smoke；它不授权 build。Smoke 必须使用真实 HostFolder 集合和绑定该配置的 hash 重复 RO/RW/unmapped/network 判别。产品 build、runner、Vitest、GUI/WebView 仍需 Build Gate。
- 本 scope delta 与修订 Proposal 在同一固定 candidate 中接受独立 Review；独立 Review 通过前不得启动 Sandbox。



## r3/r4 scope extension（2026-10-09；冻结于 r3 candidate `92361e3578eedb93d7cf6c4c5a4db06652d31fe9`）

DSH r3 exact-head Review 的 R3-05 指出原 scope 仍标记 `FROZEN_FOR_R2_REPAIR`，未覆盖 r3 在 Task boundary 中新增的 Smoke admission 与 scratch-local canary 约束。本 extension 在既定父 Task=P02、Codex-only process-isolation 子任务和用户 `PROJECT_ORCHESTRATION_AUTHORIZATION` 内登记后续修订；不扩大产品范围，也不取代 P02 Owner allowlist。

- 当前状态：`FROZEN_FOR_R4_REVIEW`；Owner=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex；r3 exact review=`APPROVED_WITH_CONDITIONS`，r4 修改只用于关闭 R3-01..R3-05。R3-06（AC 计数口径）明确延期至 P02 closeout。
- `doc/tasks/P02.md`：只可改现有 `Codex-only scratch-build output boundary` 段，以登记 Smoke admission 条件、规范 clone 命令和本 scope 引用。
- `verification/P02/**`：只允许修订下列 process-isolation 设计/证据文件，及生成同一子任务 r4 prompt/dispatch/response/exit/session/mount/stderr/checkpoint/validation 文件：
  - `codex-scratch-build-process-isolation-proposal-r1.md`
  - `codex-scratch-build-plan.md`
  - `codex-scratch-build-gate.md`
  - `codex-scratch-build-input-host-inventory-r2-build-addendum.md`
  - `codex-scratch-build-process-isolation-scope-delta-r1.md`（本 extension）
  - `codex-checkpoint-p02-process-isolation-r3-start.md`（只追加/校正 r3 hash 时间点 erratum 及 R3-01 MSVC/SDK input 分类措辞一致性修正）
  - `codex-checkpoint-p02-process-isolation-r3-delivery.md`、`codex-checkpoint-p02-process-isolation-r3-review.md`、`codex-checkpoint-p02-process-isolation-r4-start.md` 与 r4 delivery/review checkpoint
  - `codex-process-isolation-r3-validation.md` 与 r4 validation record
  - 本子任务 `dsh-review-process-isolation-r3.*`、`dsh-review-process-isolation-r4.*` 正式审查附件
- r4 选择只修正文档：不改 r3 WSB XML，故 canonical config bytes/hash 仍为 2609 / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`。不得改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、Owner 生产 allowlist、产品实现/测试、Schema/IPC/依赖、任何 root/其他作者 dirty 文件或用户数据。
- r3 DSH Review 仅批准有条件的设计并允许非提权只读 preflight；本 extension 本身不授权任何 Windows Feature 变更/启用、提权、Sandbox 启动/连接、Smoke、Build 或产品验收。R3-01/C1、R3-02/C2 未在 r4 Review 通过前，不运行 `wsb start`、不冻结 Build config；任何 Gate 状态缺少实测仍保持 `UNKNOWN`/`NOT_RUN`/`BLOCKED`。

## r5 P3 documentation closure (2026-10-09; based on reviewed candidate `fb0a7668d948ae68f15fd59aaffd6aedf6663c99`)

DSH r4 exact-head design Review=`APPROVED`（P0/P1/P2/P3=`0/0/0/3`），仅发现 N-01..N-03 三项非阻断 P3 文档一致性问题。此 extension 在 PROJECT_ORCHESTRATION_AUTHORIZATION 下将最小纯文档修订冻结为 `FROZEN_FOR_R5_REVIEW`；父 Task=P02，Codex-only process-isolation 子任务，Owner/author=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。

- `doc/tasks/P02.md`：只允许改现有 `Codex-only scratch-build output boundary` 段中的 scope 标题引用，将其统一为实际标题 `§ r3/r4 scope extension`（N-03）。
- `verification/P02/codex-scratch-build-input-host-inventory-r2-build-addendum.md`：只允许修复 N-01 的旧 r2 config 指代，准确写明当前冻结的 r3 Smoke config 不含两个 Git roots。
- `verification/P02/codex-scratch-build-plan.md`：只允许修复 N-01 的旧 proposal review state，登记 r3=`APPROVED_WITH_CONDITIONS`、r4=`APPROVED`（仅设计）、N-01..N-03 待关闭；保留 Smoke/Build/产品验收为原有 BLOCKED / NOT_AUTHORIZED / NOT_RUN 状态。
- `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`：允许追加本 r5 extension，并只就地扩写 r3/r4 extension 中 r3-start 的许可行（原 :52；不改其他文字），用于修复 N-02 文件级许可描述过窄及闭合 N-04。
- `verification/P02/**`：只允许新增本 r5 的 start/delivery/review checkpoint、validation record 以及 `dsh-review-process-isolation-r4.*`、`dsh-review-process-isolation-r5.*` 正式 Review 附件；包括 `codex-checkpoint-p02-process-isolation-r4-review.md`。

不得修改 r3 WSB XML 或其 canonical hash；不得改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、P02 Owner allowlist、产品实现/测试、Schema/IPC/依赖、root/其他作者 dirty 文件或用户数据。此修订不授权 Windows Feature 查询/变更、提权、Sandbox、Smoke、Build 或产品测试；Hard Build Barrier 继续有效。R5 exact-head 非作者 Review 通过后，最多进入本机非提权只读 preflight。

## r6 N-04/N-05 documentation repair (2026-10-09; based on reviewed candidate `1c7efb172b8e9d766e38f84cf3728a90bb5953d0`)

DSH r5 exact-head design Review=`APPROVED_WITH_CONDITIONS`（P0/P1/P2/P3=`0/0/0/2`）。本 extension 在 PROJECT_ORCHESTRATION_AUTHORIZATION 下将 N-04/N-05 两项新 P3 条件冻结为 `FROZEN_FOR_R6_REVIEW`；父 Task=P02，Codex-only process-isolation 子任务，Owner/author=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。

- `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`：仅允许按上文 r5 extension 的授权，扩写 r3/r4 extension 中 r3-start 的一行文件许可；删除本文件 r5 extension 末尾误留的两个字符 `` `n `` 并补 LF 文件尾；追加本 r6 extension。不得改其他既有文字。
- `verification/P02/**`：允许入库 r5 delivery/review checkpoints、r5 DSH dispatch/response/session/mount/exit/stderr 附件、r6 start/delivery/review checkpoints、r6 validation，以及 `dsh-review-process-isolation-r6.*` 正式 Review 附件。
- 不得修改 P02 Task boundary、Build plan、host inventory、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、P02 Owner allowlist、产品实现/测试、Schema/IPC/依赖、r3 WSB XML/canonical hash、root/其他作者 dirty 文件或用户数据。
- R6验收：N-04 许可精确覆盖上述 :52 一行就地扩写；N-05 移除字面 `` `n `` 且文件以 LF 结束；r3 XML bytes/hash 不变；路线 validator 与 `git diff --check` 通过；DSH exact-head 非作者复审通过。
- 本 extension 不授权 Windows Feature 查询/变更、提权、Sandbox、Smoke、Build 或产品测试。Smoke admission=`NOT_ADMITTED`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier 继续有效。R6 review 通过后最多进入本机非提权只读 preflight。

## r7 P02 preflight R1 Review repair and authorization audit trail (2026-10-10; based on reviewed candidate 561f4105171b99910d739698380787f35203d3f2)

DeepSeek Harness exact-head review of the non-elevated preflight candidate returned APPROVED_WITH_CONDITIONS, P0/P1/P2/P3 = 0/0/1/5. P2-01 requires an auditable authorization basis for the four current-status document edits; P3-01 through P3-05 request precise status wording, raw host observation provenance, path-count reconciliation, frozen-root-manifest time semantics, and HostFolder mapping-domain labels.

Authorization basis: on 2026-10-10 the user issued the persistent PROJECT_ORCHESTRATION_AUTHORIZATION in the active Codex task, explicitly authorizing Codex to maintain the project plan, status, task graph, checkpoints, run necessary verification, obtain independent Review, and integrate locally without repeated approval. This is consistent with repository AGENTS.md assigning Codex plan/status/task coordination and integration. This extension records a narrow, pre-repair scope; it does not broaden P02 product scope or the Antigravity Owner allowlist. It supersedes earlier prohibitions on the named shared-document edits only to the exact extent listed below.

Parent Task=P02 remains in_progress / ACTIVE. Owner/author=Codex; non-author Reviewer=DeepSeek Harness; Integrator=Codex. This is a documentation/evidence repair only. No Windows Feature query or change, elevation, Sandbox, clone creation, Smoke, Build, product test, GUI, or WebView is authorized. All existing UNKNOWN, BLOCKED, NOT_ADMITTED, NOT_AUTHORIZED, and NOT_RUN states remain unchanged unless supported by the listed read-only evidence.

Allowed paths and exact scope:
- doc/STATUS.md: update only the top current P02 status segment to cite the R1 Review and corrected preflight evidence; preserve historical records and all other Task states.
- doc/REBASELINE_PLAN.md: update only the top current checkpoint with the R1 Review result, R2 repair status, and corrected evidence pointers; preserve history and dependency states.
- doc/00_INDEX.md: update only the first current-work paragraph with the corrected evidence/review status.
- doc/tasks/P02.md: update only the existing Codex Scratch Isolation Preflight checkpoint rows to cite R1 Review disposition and corrected evidence; do not alter AC, product scope, Owner allowlist, Task dependency, or parent status.
- verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md: append this extension only.
- verification/P02/codex-scratch-build-preflight-r1.md: close P3-01, P3-02, P3-04, and P3-05 by removing PASS wording from the predicted source-pin state, adding the machine-readable observation evidence link and provenance, clarifying the root manifest is frozen at its recorded earlier HEAD while its 203 entries match live main, and distinguishing HostFolder roots from Smoke XML mapping count.
- verification/P02/codex-scratch-build-preflight-hostfolders-r1.tsv: add a mappingDomain column classifying the fixed scratch root as scratch RW, nine external Smoke input roots as Smoke RO, and two Git roots as Build-only RO. Do not change observed path-existence results.
- verification/P02/codex-scratch-build-preflight-observations-r1.json: add read-only, non-elevated host identity/resource and WSB package observations with exact CIM property provenance, collection time, source commands, and derived units.
- verification/P02/codex-checkpoint-p02-non-elevated-preflight-delivery.md: reconcile the changed-path count to four status-document segments plus ten verification files, including that checkpoint.
- verification/P02/codex-checkpoint-p02-preflight-scope-frozen.md: add a pointer to this authorization extension; retain its original time and measurement record.
- verification/P02/codex-checkpoint-p02-preflight-review-r1.md and verification/P02/codex-checkpoint-p02-preflight-r2-start.md: record R1 Review and the frozen R2 repair boundary.
- verification/P02/dsh-review-p02-preflight-r1.{prompt.md,response.md,exit.txt,stderr.txt,session.json,mount.txt}: preserve the R1 review packet, final text event, exit/stderr, and mounted session metadata; do not commit the full JSONL stream because it contains non-deliverable internal reasoning events.
- verification/P02/codex-checkpoint-p02-preflight-r2-delivery.md, verification/P02/codex-checkpoint-p02-preflight-r2-review.md, verification/P02/codex-preflight-r2-validation.md, and verification/P02/dsh-review-p02-preflight-r2.{prompt.md,response.md,exit.txt,stderr.txt,session.json,mount.txt}: record the frozen-candidate validation and exact-head R2 independent Review evidence.

R2 acceptance: close P2-01 and address or explicitly disposition each P3-01..P3-05; route validator, Markdown link checks, and git diff --check pass; exact changed path set is contained by this allowlist; root protected manifest remains 203/203 with zero candidate-path overlap; DeepSeek Harness reviews the exact fixed R2 HEAD. Even if accepted, this review only confirms the documentation/evidence repair and the preflight remains BLOCKED / INCOMPLETE while Windows Sandbox Feature stays UNKNOWN. Smoke remains NOT_ADMITTED / NOT_AUTHORIZED / NOT_RUN; Build Gate remains BLOCKED and build NOT_AUTHORIZED / NOT_RUN; AC1–AC7 remain BLOCKED / NOT_RUN; Hard Build Barrier remains effective.
## r8 P02 preflight R2 review finding repair and R3 exact-head review (2026-10-10; based on reviewed HEAD 7d8951c28cd954d7e325cd53e7991f3bec87d971)

DeepSeek Harness reviewed the exact R2 candidate and returned APPROVED, P0/P1/P2/P3=0/0/0/3. R1 P2-01 and P3-01..P3-05 are closed. R2 N-01..N-03 are nonblocking documentation/evidence consistency findings; the parent Task remains in_progress / ACTIVE. This extension is limited to those three findings and does not alter P02 product scope, ACs, Owner allowlist, dependencies, or any Smoke/Build/Product gate.

Allowed paths and exact scope:
- verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md: append this r8 extension only.
- verification/P02/codex-checkpoint-p02-preflight-r2-review.md: record the exact R2 review and freeze the narrow R3 repair/review boundary.
- verification/P02/codex-preflight-r2-validation.md: distinguish the 24-path fixed-change snapshot at 80cf5651 from the 26-path reviewed HEAD at 7d8951c2; identify the six unchanged inherited files covered by the original R1 freeze; record the exact-head 7d8951c2 validation and final R3 validation.
- verification/P02/codex-checkpoint-p02-preflight-r2-delivery.md: update only review disposition, findings, and next action.
- verification/P02/codex-checkpoint-p02-non-elevated-preflight-start.md: clarify that the completion sentence is a retrospective delivery-time note; preserve the original scope-freeze timestamp and measurements.
- verification/P02/dsh-review-p02-preflight-r2.{prompt.md,response.md,exit.txt,stderr.txt,session.json,mount.txt}: preserve the R2 review packet and mounted session metadata.
- verification/P02/dsh-review-p02-preflight-r3.{prompt.md,response.md,exit.txt,stderr.txt,session.json,mount.txt}: preserve the exact-head R3 review packet and mounted session metadata.
- verification/P02/codex-checkpoint-p02-preflight-r3-start.md and verification/P02/codex-checkpoint-p02-preflight-r3-delivery.md: record the R3 repair start and fixed validated candidate.
- doc/STATUS.md: update only the top current P02 status segment with R2 result, narrow R3 repair/review state, and unchanged gates.
- doc/REBASELINE_PLAN.md: update only the top current checkpoint with R2 result, exact R3 repair scope, and next action.
- doc/00_INDEX.md: update only the first current-work paragraph.
- doc/tasks/P02.md: update only the existing Codex Scratch Isolation Preflight checkpoint rows; preserve AC, Owner allowlist, dependency graph, and parent state.

R3 acceptance: N-01 explicitly distinguishes R1-frozen inherited paths from r7 additions and reports the fixed-change and reviewed-HEAD counts with their exact commits; N-02 records the independent exact-head 7d8951c2 validator/link/diff results and the author-side final-candidate rerun; N-03 makes the start checkpoint timeline internally consistent without rewriting its historical timestamp. Re-run the route validator, Markdown link checks, and `git diff --check`; verify the exact candidate path set is within the union of the R1 freeze and r7/r8 allowlists; recheck the root protected manifest at 203/203 with zero candidate overlap; obtain DeepSeek Harness review of the exact final R3 HEAD before local fast-forward. Feature remains UNKNOWN; full preflight BLOCKED / INCOMPLETE; Smoke NOT_ADMITTED / NOT_AUTHORIZED / NOT_RUN; Build Gate BLOCKED and build NOT_AUTHORIZED / NOT_RUN; AC1–AC7 BLOCKED / NOT_RUN; Hard Build Barrier remains effective.
