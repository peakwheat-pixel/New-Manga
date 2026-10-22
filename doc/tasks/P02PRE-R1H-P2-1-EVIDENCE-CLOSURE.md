---
id: P02PRE-R1H-P2-1-EVIDENCE-CLOSURE
title: P2-1 item-level evidence provenance closure
kind: verification
status: historical
dispatch_state: EXECUTED_20261012 / BLOCKED_P2_1_OPEN
approval: user_authorized_p02_executor_transfer_20261012
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex /root
depends_on: []
base_commit: 343895fb5f0329c0c07a7104ec321b698f967607
branch: agent/zcode/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE
worktree: C:/Users/49745/.codex/worktrees/p2-p2-1-zcode/New Manga
integration_commit: null
---

# P02PRE-R1H-P2-1-EVIDENCE-CLOSURE：追溯 H1 P2-1 的 15 项原始证据来源

## 来源与目标

H1 的 v2 final pre-run 记录 `PRE_RUN_PASS`，但独立 DSH Review 指出 23 个 PASS 中的 15 个 `checks[].evidence` 标签在 13 项冻结输入内不能解析到 item-level raw evidence。Codex 已接受该 finding，保持 OPEN；H1 acceptance 与 X6 都 blocked。

本 Task 只检查已有材料，判断这 15 项是否能映射到可复核的原始来源或精确冻结文件 span。不得重跑 final pre-run、不得执行器生成替代证据。若无法逐项闭合，保留 blocker 并记录缺失来源；不得把 JSON 的 observed 值、作者声明或聊天记录提升为 raw evidence。

Owner=ZCode（按用户 2026-10-12 指示）；Reviewer=DeepSeek Harness（仅在形成 closure candidate 后由 Codex 派发）；Integrator/Adjudicator=Codex /root。ZCode 已于 2026-10-12 实际执行本 Task，最终状态=`blocked / EXECUTED_20261012 / BLOCKED_P2_1_OPEN`；15 项中仅 `e-root-status`、`e-agy-status` 两项有可复核 span，13 项无合格 item-level raw source。Codex 已复核 pins 与两个 span，整体 P2-1 保持 OPEN；因未形成 15/15 closure candidate，未派 DSH focused Review。派发提示词=`verification/P02/zcode-p02pre-r1h-p2-1-evidence-closure-prompt-20261012.md`，报告与 Handoff 位于 ZCode Owner worktree。

## Acceptance Criteria

- [x] 对以下 15 项逐项给出 item-level 来源路径、精确行号或 JSON Pointer、源文件 size/SHA-256、来源时间/身份依据，以及为何该内容满足“原始证据”或确定性 span mapping：`tools`、`a-identity`、`b-registry-wer-localdumps`、`b-profile-moniker`、`c-temp-paths`、`e-root-refs`、`e-owner-refs`、`e-agy-refs`、`e-root-status`、`e-owner-status`、`e-agy-status`、`e-root-index-hash`、`f-protected-file-pin`、`h-targets-initial`、`h-targets-final-prewrite`。（报告逐项列明；仅两项合格，其余 13 项准确记录为无来源。）
- [x] 若发现已存在于仓库外的原始采集文件，仅可逐字节复制到新的、已确认 absent/unignored 的 `verification/P02/zcode-p02pre-r1h-p2-1-recovered-source-<basename>-20261012.bin`，不得改写原件；同时记录原始与副本的 size/SHA-256。不得复制无 item-level 原始内容的 summary/template 冒充 raw evidence。（未发现属于 15 项 v2 时点的 raw file；`%TEMP%\root-status-z.txt` 属 attempt1 时点，未复制。）
- [x] 汇总到 `verification/P02/zcode-p02pre-r1h-p2-1-evidence-closure-report-20261012.md`。如果任何一项仍无合格来源，结论必须为 `BLOCKED / P2-1 OPEN`，列出未闭合项与准确原因；不能标记 closure candidate。（报告结论 `BLOCKED / P2-1 OPEN`，§6 列出 13 项未闭合项。）
- [ ] 候选证据须由 Codex 非作者逐 pin 核验，并取得 DeepSeek Harness focused independent Review 与 Codex 逐项 adjudication；ZCode 不审查或批准自己的材料。
- [x] 所有 attempt1/v2 原始文件、A6 冻结 Task、protocol、executor 和 Handoff 均保持原字节不变；任何 path/hash 漂移均 stop，不覆盖、不重跑。（15/15 冻结输入 pins 与 3 项 review context pins 匹配；H1 Task 依历史 verification record 处理。）

## 允许修改范围

- `doc/tasks/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE.md`
- `verification/P02/zcode-p02pre-r1h-p2-1-evidence-closure-report-20261012.md`
- 仅当找到合格的既存 raw source 时：`verification/P02/zcode-p02pre-r1h-p2-1-recovered-source-<basename>-20261012.bin`
- 本 Task 自己的 Handoff；不得改 Plan、STATUS、索引、父 P02 Task 或 H1 Task。

## 禁止范围

不得运行/dot-source attempt6 executor；不得运行 final pre-run、生成新采集或并行重跑；不得使用 `File.Replace`、ProcessObserver/ProcessSnapshot/native Toolhelp 枚举、profile/registry/ACL 写 API、capture、Build/Cargo、AC1–AC7、Windows Sandbox、Qoder 或由 ZCode Agent 递归调用 ZCode CLI。用户于 2026-10-12 后续直接授权 Codex Coordinator 使用本机 ZCode CLI 完成本次派发；该授权不扩大原始证据搜索范围。不得访问 `G:\CODEX\New Manga\.tmp.driveupload`；不得 reset/clean/stash/覆盖/删除/stage/commit；不得改写或删除任何已有 attempt1/v2/H1 Review/A6 输入。只读搜索限定于本 Task 列出的 P02 pinned 输入、相应 Agy delivery worktree 冻结源与 `%TEMP%` 中 P02 运行时段的相关暂存材料；不做全盘扫描。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 15 项 source trace | 固定 PowerShell 7.6.6 只读核对 pin 与逐项 span；Codex independently reconstructed two status spans | ZCode 独立 worktree；现有 pin 来源只读 | `DONE / BLOCKED / P2-1 OPEN`（2 项部分映射；13 项无 raw source） | ZCode 报告 §1–§6；Codex 复算 `79291B/0DB72CDA…`、`223B/25316B54…` |
| Evidence copy integrity | 仅对确实找到的 raw 文件执行 CreateNew 逐字节复制并重算源/副本 SHA-256 | 找到原始文件且目标 absent/unignored | `NOT_TRIGGERED`：无属于 15 项 v2 时点的合格 raw file；attempt1 `root-status-z.txt` 未复制 | 报告 §5.2/§5.4 |
| DSH focused Review | Codex 完成候选输入 pin verification 后再派发 | 所有 15 项均有合格映射 | `BLOCKED / NOT_DISPATCHED`：13 项未闭合 | 报告 §6/§8；Handoff |

## 依赖、风险与阻塞

上游 H1 Task=`P02PRE-R1H-R6-ZCODE-H1` 仍为 `in_review / DSH_REVIEW_CHANGES_REQUESTED`；其 P2-1 为本 Task 的待关闭 finding，不要求 H1 先完成。若原始采集文件已不存在且无法从 pinned spans 确定性映射，本 Task 停止为 `blocked / P2-1 OPEN`，不以重新运行补造证据。H1 Review 被接受前不创建 X6 Task。

## 交付与运行记录

- ZCode CLI session=`sess_c297a288-813f-4dfa-92f1-bae7d37d05b8`；内置 Agent session=`agent_8886fd38-6ba0-41d4-a084-6ee8cf40dc8d`；CLI exit=0。两个直接长任务调用各等待 15 分钟后中断，stdout/stderr 均为空；无覆盖，详细尝试日志由 Codex 保存于 root `verification/P02`。
- 报告：Owner worktree `verification/P02/zcode-p02pre-r1h-p2-1-evidence-closure-report-20261012.md`（27065 / `DA3C419658AE6FD8FB42A93488666A622FF80DAAD5A565A5E92E0B2615C6AE43`）。Handoff：同目录 `zcode-p02pre-r1h-p2-1-evidence-closure-handoff-20261012.md`（5733 / `456CD1E8B33B4DF1E3ECADB5BECF9D23AF613E83AB0A7B780514B3610ECA98DF`）。Task 更新=8184 / `D17105FFCD823EB323C8C05FEA85E06C49BC8FD4C0162FEFE0394EE9027263`。
- Review：`BLOCKED / NOT_DISPATCHED`；Codex 已完成非作者 pins/spans 复核与整体 `P2-1 OPEN` adjudication；没有接受 H1 gate 或 X6。
- 下一接收者：Codex /root 已记录结果；后续若要追查仓库外 CLI harness forensic 输出，先由用户授权扩大只读范围。当前无 READY 子 Task。

## 2026-10-22 归档为 historical（用户裁决）

用户在 2026-10-22 明确裁决：**这些历史线不再继续**。

- 本 Task 原状态：`blocked`；现归档为 `historical`，作为历史证据保留，不再派发 Owner/Reviewer，不再推进。
- 保留内容：原 Task 正文、Canonical Evidence、Resource Manifest、Handoff 与历史 Review 一律不改，仅 frontmatter `status` 变更并追加本条记录。
- 依据：产品边界已明确只允许 Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy 新架构；P02 时期 Legacy 线不再释放实现、诊断或修复任务。
- 恢复：如需重新激活，须由用户重新裁决并走新的 Task 生命周期，不得据此恢复旧作业。
