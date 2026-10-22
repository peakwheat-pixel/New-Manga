# P02PRE-R1H Owner remediation round 4 — R1H-007

你是实现 Owner `/root/p02_r1h_codex_owner`。Integrator/Adjudicator=`/root`；后续 Reviewer=`/root/p02_r1h_remediation_review`（必须独立，不能由你自审）。请先核验下列输入 pins，再按本任务完成一个最小、受限的修复。

## 冻结起点

- Repository=`G:\CODEX\New Manga`
- Worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- Branch=`agent/codex/P02PRE-R1H`
- Required starting HEAD / required parent=`0ecada4182d624d4f352a253e09db3bdecbee5d1`
- Tree=`06986f47ac8363a32ecbf2d0e41ec1d680510940`
- 输入 pin 文件=`verification/P02/codex-p02pre-r1h-owner-remediation-round4-20261012.pins.json`
- 本 Owner prompt=`verification/P02/codex-p02pre-r1h-owner-remediation-round4-20261012.prompt.md`

先确认 branch、HEAD、tree、clean controlled status 和全部 pins。若起点不符或有任何不明 dirty/untracked 路径，不得覆盖或清理，停止并报告。不得 reset、clean、stash、删除或改写原有用户内容。

## 唯一问题与最小改动

独立 Review 已发现并由 Codex adjudicate：`R1H-007 / P2 / OPEN`。在 `verification/P02/p02pre-r1h-selfcheck.ps1` 中，`$expectedDirectTexts` 是 sparse integer-key `[ordered]` dictionary；`$expectedDirectTexts[$index]` 把整数解释为 insertion-order 值位置，而非整数 key，导致真实合法 candidate 的 prefix 正例比较错位并返回 false。Microsoft 官方语义和 root adjudication 见冻结输入。

仅将该 allowlist 的取值改成明确的 object-key lookup（例如 `$expectedDirectTexts[[object]$index]`），或采用同等大小且无顺序依赖的普通 hashtable；首选最小正确改动。不要改 `$prefix` 左侧的数组索引。

必须保留并静态核对：13 项 outer-loop prefix exact allowlist、nested staging/guard/commands/member-call/assignment/control-flow 限制、R1H-005 pure-memory helper allowlist、合法真实 candidate 正例、四个 source-only memory mutation negative fixtures 及 R1H-001..006 的已有约束。禁止把 fixture 当作已运行。

## 写入范围、交付与验收

- 必需写入：`verification/P02/p02pre-r1h-selfcheck.ps1`。
- 仅当需修正准确交付说明时，可一并改 `verification/P02/p02pre-r1h-handoff-20261012.md`。
- `verification/P02/p02pre-r1h-capture.ps1` 及其它所有文件只读。不得改 Task、manifest、Plan/STATUS/index、pins、Review/adjudication/checkpoint 或任何 gate 状态。
- 仅允许运行 `git diff --check`。禁止 PowerShell parser/selfcheck/preflight/capture、getter/API、tests、Build/Cargo、AC1–AC7、OS dynamic、Windows Sandbox。
- 保持同一 branch；以 frozen HEAD 为 parent 交付固定 commit；提供 commit、tree、parent、文件清单与 bytes/SHA-256、受控 status 和 `git diff --check` exit。交付新 Handoff；不得自行 integration 或 Review。
- handoff 必须如实声明未运行 parser/selfcheck/fixtures/preflight/capture/tests/Build/AC/OS dynamic。记录实际执行器模型/力度（仅报告实际信息）。

## 不得改变的 Gate

`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；保留原文 `technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。

## 完成后交接

停止在交付边界，将新 HEAD/Handoff/commands/status/pins 交给 `/root`。由 root 独立核验交付，再派 `/root/p02_r1h_remediation_review` 复审；你不得自审、集成、解除 Build Barrier 或宣称任何 Gate/AC PASS。
