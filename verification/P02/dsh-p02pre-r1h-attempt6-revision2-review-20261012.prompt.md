# DSH Revision 2 独立静态 Review：P02PRE-R1H-R6-EXEC-A6

你是非作者独立 Reviewer；实现 Owner=Antigravity，Integrator/Adjudicator=Codex `/root`。本 Review 的 CWD 必须为固定 A6 linked worktree 根目录：`C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga`；branch=`agent/antigravity/P02PRE-R1H-R6-EXEC-A6`，base/reviewed HEAD=`343895fb5f0329c0c07a7104ec321b698f967607`。Agy 交付保持未暂存状态。

## 冻结输入

先只读打开 `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-r2-review-input-manifest-20261012.json`。严格只读该 manifest 列出的 36 个路径：其 revision2 源清单、27 项源输入、3 项候选交付和 5 项 Review context。候选交付为：

1. `verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1`
2. `verification/P02/p02pre-r1h-round6-integration-protocol-attempt6-20261012.md`
3. `verification/P02/p02pre-r1h-round6-attempt6-exec-handoff-20261012.md`

Review manifest SHA-256=`10FEA3C8302D8ED7D59DB96F1972F027BB96D01079A4ED652B6D53BBD6299888`；Codex 已于 dispatch 前独立核验 36/36 路径的 SHA-256 与 byte length，证据=`G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-r2-review-input-verification-20261012.json`。此证据与 manifest 均在精确输入包内。DSH 自己若无法 hash，必须标记 `NOT_VERIFIED`，不得尝试 ACL/权限修复，也不要声称 DSH hashes 通过。

**读取边界：**不许 `glob`、目录遍历/列表、搜索未列出的文件、shell/process、ACL/权限查询或修改、外部链接访问、任何写入；禁止访问 `.tmp.driveupload`。不要读取 Task mutable state、STATUS、Plan 或其他未列路径。逐项列出本次实际成功打开的精确输入路径；未打开项标 `NOT_READ`。关键源文件未读时不能批准。

## Review 目标

完整审查 3 个候选文件及相关 A4/A5 精确源，按 immutable A6 Task contract、此前 DSH findings 与 Codex adjudication 评估：

- F-01：协议/Handoff 是否准确引用 revision2 manifest、声明 `checkpointIncludedInInputPins=true` 并指明已 pin 的 attempt5 parser-pass checkpoint。
- F-02：root legacy Owner Handoff 是否出现在 r2 input pins，byte/SHA 与文件一致；实际 Owner Handoff pin 是否仍准确。
- AC2/F-03 accepted subfinding：七个新建输出是否都采用唯一 attempt6 专属名称，协议/Handoff 所有引用一致；`destination` 是否保持原受保护路径；`CreateNew`、absent/write-safe 检查、同目录限制和既有写入闭包是否保留。
- 第一版 F-03 算术子 finding 与 F-05 是否仅按 Codex adjudication 如实记录为拒绝，不夸大为修复；F-04 外部 pin 说明是否客观。
- Executor 与协议是否与冻结的 Task、身份/path/ACL/API/子进程和 Gate 约束一致；任何实现改动是否超出必要范围。
- Handoff 是否将 Owner 声明和 Codex 实际验证分开；是否准确说明此前 `git diff --check` 对未跟踪文件的限制；Parser-only 原始输出是否完整且不暗示 executor/runtime/OS/API 被运行。
- 是否明确未获得任何 Gate、Build/Cargo 或 system AC1–AC7 PASS；保留 `private_registry_absence=UNPROVABLE` 与既有 owner waiver。
- 输出路径唯一/不存在的 Codex 检查不等于 DSH 检查；对未独立验证事实保持限定。

## 审查方式与输出

这是只读静态内容审查。不要运行 Parser、executor、纯内存 assertions、tests、Build/Cargo、OS/API、child process、profile/registry/ACL 或系统 AC1–AC7。按 `APPROVED_STATIC_CONTENT` 或 `CHANGES_REQUESTED` 判定；逐项报告 P0/P1/P2/P3 计数、路径/行号、证据、可执行修复，以及独立打开路径清单和任何方法限制。只有无未解决 P0/P1/P2 且关键输入已阅读时才能 `APPROVED_STATIC_CONTENT`。不得将静态 Review 等同于 Parser、集成或 Gate 通过。
