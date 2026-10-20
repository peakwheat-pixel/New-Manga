---
id: P02PRE-R1H-R6-EXEC-A4
title: Round6 attempt4 最终安全复核与一次性 P02PRE-R1H 执行
kind: verification
status: blocked
approval: user_authorized_automatic_20261012
suggested_owner: Codex
owner: Codex /root
reviewer: DeepSeek Harness (non-author post-run evidence review)
integrator: Codex /root
depends_on: [P02PRE-R1H-R6-A4]
base_commit: 343895fb5f0329c0c07a7104ec321b698f967607
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R1H-R6-EXEC-A4：Round6 attempt4 最终安全复核与一次性执行

## 来源与目标

父 Task=`P02PRE-R1H` AC4–AC7。Owner/author 与 frozen attempt4 executor/protocol 的作者均为 Codex；A4 静态修复 Task 已完成并集成，代码由非作者 DeepSeek Harness 审查。当前主线=`main@343895fb5f0329c0c07a7104ec321b698f967607`，tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`。

本 Task 只推进 R1H 一次性 Round6 集成执行及其后 Review。用户已明确授权必要的宿主查询、AppContainer/profile/registry/ACL 验证、动态隔离、P02PRE、Build/Cargo、AC1–AC7、修复、Review、重测和集成；该授权不替代本 Task 的执行前证据，也不改变任何 Gate。用户已撤销完成后关机要求，禁止关机。Windows Sandbox 禁止查询、安装、启用或启动。

## Acceptance Criteria

- [ ] 执行前复核精确执行器 `verification/P02/p02pre-r1h-round6-integrator-attempt4-20261012.ps1`、控制协议 attempt4、父 Task 与冻结 manifest；核实它们的 SHA-256、主机/用户/SID/token、PowerShell 7.6.6/Core/FullLanguage、Git/PowerShell 子进程映像、参数/CWD、路径/ACL/streams、main/Owner refs/status/index、TEMP/cache/scratch、受保护文件基线哈希与七个唯一输出目标。
- [ ] 七个输出文件均在运行前确认不存在、未被 ignore、路径组件无 reparse、处于许可卷/父目录；`:(exclude).tmp.driveupload` 作为每个 Git status 的独立 argv 参数，不查询该路径。
- [ ] 仅以 `C:\Program Files\PowerShell\7\pwsh.exe` 在仓库根运行 frozen attempt4 executor，最多一次；只允许执行器/protocol 中的单次三参数 `File.Replace` 及固定的验证子进程。所有子进程身份/映像/argv/CWD 必须落在 frozen allowlist；任何身份、路径、输出、观察、写入或证据异常立即停止，不重试、不清理、不回滚。
- [ ] 新输出只通过协议规定的 `CreateNew` 生成。根进程 stdout/stderr/exit 由 Codex 仅写入下列本 Task 独有的、运行前确认 absent 的捕获目标；保留执行器 partial evidence。
- [ ] Parser/selfcheck/capability 和执行前后文件/状态证据按实记录；执行结束后由 DeepSeek Harness 对冻结的 R1H 输出作非作者 Review，Codex 独立复算 pins 并 adjudicate，再刷新父 Task/DAG。
- [ ] 任何本 Task 结果都不自动解除 `Build Gate=BLOCKED` 或 `Hard Build Barrier=EFFECTIVE`；本 Task 不运行 Build/Cargo 或系统 AC1–AC7。`private_registry_absence=UNPROVABLE` 和 Owner 风险例外原值保持。

## 允许修改范围

### 运行前只读冻结输入

- `verification/P02/p02pre-r1h-round6-integrator-attempt4-20261012.ps1`
- `verification/P02/p02pre-r1h-round6-integration-protocol-attempt4-20261012.md`
- `verification/P02/p02pre-r1h-round6-integration-protocol-attempt3-20261012.md`
- `verification/P02/p02pre-r1h-round6-integration-protocol-20261012.md`
- `verification/P02/p02pre-r1h-manifest-20261012.md`
- `verification/P02/p02pre-r1h-round6-attempt4-selfcheck-20261012.ps1`
- `verification/P02/codex-p02pre-r1h-attempt4-owner-delivery-pins-20261012.json`
- `doc/tasks/P02PRE-R1H.md`、`doc/tasks/P02.md`、`doc/09_COLLABORATION.md`、`AGENTS.md`

### 执行器唯一八项文件写入 allowlist

- `verification/P02/p02pre-r1h-selfcheck.ps1` — 唯一受控 Replace destination。
- `verification/P02/p02pre-r1h-selfcheck-round6-stage-20261012.ps1`
- `verification/P02/p02pre-r1h-selfcheck-round5-recovery-20261012.ps1`
- `verification/P02/p02pre-r1h-selfcheck-round5-integrated-backup-20261012.ps1`
- `verification/P02/p02pre-r1h-round6-handoff-20261012.md`
- `verification/P02/p02pre-r1h-integration-round6-execution-20261012.json`
- `verification/P02/p02pre-r1h-selfcheck-round6-20261012.json`
- `verification/P02/p02pre-r1h-engine-preflight-round6-20261012.json`

### Codex 运行捕获与 post-run Review 证据

- `verification/P02/codex-p02pre-r1h-round6-exec-attempt4-20261012.stdout.log`
- `verification/P02/codex-p02pre-r1h-round6-exec-attempt4-20261012.stderr.log`
- `verification/P02/codex-p02pre-r1h-round6-exec-attempt4-20261012.exit`
- `verification/P02/codex-p02pre-r1h-round6-exec-review-pins-20261012.json`
- `verification/P02/dsh-p02pre-r1h-round6-exec-review-20261012.prompt.md`
- `verification/P02/dsh-p02pre-r1h-round6-exec-review-20261012.stdout.jsonl`
- `verification/P02/dsh-p02pre-r1h-round6-exec-review-20261012.stderr.log`
- `verification/P02/dsh-p02pre-r1h-round6-exec-review-20261012.exit`
- `verification/P02/codex-subagent-p02pre-r1h-round6-exec-review-20261012.md`
- `verification/P02/p02pre-r1h-round6-exec-review-postpins-20261012.json`
- `verification/P02/p02pre-r1h-round6-exec-review-adjudication-20261012.md`
- 本 Task、父 Task 交接记录以及专用 rolling checkpoint。Plan/STATUS/Index 只在运行前/后更新，绝不在 executor 的 S0–S2 窗口内编辑。

以上列出的新 evidence 目标在使用前必须逐一检查 absent 与 unignored；本 Task 不授予目录级写权限。Attempt4 executor、现有源文件/Task/manifest、Round5/R1G 输出和所有用户漫画/用户文件均只读。不得触碰 `.tmp.driveupload`。

## 禁止范围

- 禁止 Windows Sandbox、Build、Cargo、系统 AC1–AC7，以及任何超出上述逐项 allowlist 的写入。
- 禁止对 mode=`120000` 的非-reparse leaf 读取内容/hash、解析/访问 link target、查 ACL 或枚举其目标子项。
- 禁止 profile/registry/ACL/Windows feature 修改；只允许冻结 manifest 中明确列出的 getter/query/API 验证。
- 禁止 retry、rollback、cleanup、删除/覆盖 R1G/Round5 文件，禁止杀死子进程或临时添加 timeout policy。
- 任一未知子进程、未授权路径、身份不符、输出 collision、哈希/ACL/状态漂移或缺失证据立即停止；保持真实状态，不自动恢复。

## 运行记录

- 父 Task=`P02PRE-R1H`；A4 静态子 Task=`P02PRE-R1H-R6-A4` 已 `done`，integration commit=`343895fb5f0329c0c07a7104ec321b698f967607`。
- 当前状态：仅启动本 Task 的 final pre-run 核验；attempt4 executor 尚未调用。
- 风险/Gate 原值：`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; system AC1–AC7=`BLOCKED / NOT_RUN`。
- 下一步：按父 Task AC5 和 frozen protocol 逐项完成 pre-run 证据；全部匹配后才允许一次执行，之后 dispatch 非作者 DeepSeek Harness post-run Review。

## Codex pre-run blocker adjudication（2026-10-12）

- 本 Task executor 未调用；File.Replace、validation child、R1H capture、OS/API、Build/Cargo、system AC 均 `NOT_RUN`。本次只读核对发现冻结 attempt4 executor 的 `AssertRefs` 固定要求 root=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`，`$IndexHash=214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；Live root 已因 A4 精确集成变为 `main@343895fb5f0329c0c07a7104ec321b698f967607` / tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`，`.git/index` SHA-256=`C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`。因此 frozen refs/index precondition 不匹配，执行前停住；不能把该 mismatch 写成 Gate 或测试失败。
- Codex Owner worktree 只读核对为 `agent/codex/P02PRE-R1H@c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d` / tree=`96e7273ddd5fd27bee567bba27f19453cabe0842`；无代码或任务文件被改写。
- 2026-10-12 受控 root status（PS7.6.6、`--no-optional-locks`、NUL porcelain-v2、独立 pathspec `:(exclude).tmp.driveupload`）=`1055 NUL / 71878 bytes / SHA-256 8D49CEE897C02C76545A7DE72060E26E08FC283DE3AE90FCCADFEF68690752BA`，exit=0/stderr=0；status 前后 index SHA 均为上列 `C5CA...`，HEAD/tree/index tree 一致，无 staged change。与紧邻集成后的原始受控快照 `1054 / 71452 / 5CC08C56EF64FAAAC2F2A835DC2ED15B125E8726969EC0BD8CEE37F18E3DAD19` 相比 `+1 record / +426 bytes`，具体路径归因 `UNKNOWN / NOT_VERIFIED`。保留全部既有 dirty/untracked 内容。
- Codex 将此执行切片标记为 `BLOCKED`，并创建依赖修复 Task `P02PRE-R1H-R6-EXEC-A5`。A5 只生成新的 attempt5 executor/protocol/Handoff，重新绑定已集成 main HEAD 与 index，非作者 Review 与 Codex adjudication 通过后才可继续最终 pre-run。attempt4 frozen files 保持不变。
- Gate 原值不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；原文 `technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；system AC1–AC7=`BLOCKED / NOT_RUN`。任务结束不关机；Windows Sandbox 不触碰。
