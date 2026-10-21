---
handoff_id: HANDOFF-WORKSPACE-DECLARATION-REMEDIATION-1-R3
task_id: WORKSPACE-DECLARATION-REMEDIATION-1
author: workspace-hardening (DeepSeek Harness)
reviewer: Codex
status: in_review
review_round: r3 changes_requested fixes (F-01..F-08)
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
start_commit: f0f19596f
evidence_commit: 2c38980c98385be79e4d67e801a954d698955c80
date: 2026-10-21
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
---

# WORKSPACE-DECLARATION-REMEDIATION-1 Handoff (review r3)

> Handoff 不是 Review、不是批准、不是关闭。Task 仍为 `in_review`。
> 未执行任何真实 apply/删除/移动/GC/prune/push；未修改历史 Task/证据/untracked 文件。

## 1. 结果摘要（真实仓库，same command / same snapshot）

| 指标 | before | r1 | r2 | r3 |
|---|---:|---:|---:|---:|
| declarations | 1858 | 1855 | 1858 | 1858 |
| protected roots | 1264 | 1262 | 1264 | 1264 |
| errors | **163** | 15 | 76 | **76** |
| warnings | 54 | 239 | 236 | 236 |
| exit code | 2 | 2 | 2 | 2（fail-closed） |

Snapshot：git HEAD `f0f19596fa9df6b561626b27f1c086b095552be7`，`git ls-files -z -- doc/tasks verification` sha256
`6eaeb3923c7f299f`、7416 个 tracked 扫描文件；before/after 使用同一快照（`same_snapshot=true`，
见 `evidence/audit-snapshots.json`）。before 由旧工具重跑并记录完整命令/cwd/shell/exit。
76 条 residual 分类：`TABLE_SCHEMA_INCOMPLETE` 44、`DECL_GENERALIZED` 6、
`DECL_DESTINATION_GENERALIZED` 6、`DECL_RELATIVE_UNRESOLVED` 6、`DECL_ENV` 4、
`FILE_UNREADABLE` 3、`DECL_UNKNOWN_DISPOSITION` 2、`JSON_PARSE` 2、
`DECL_RELATIVE_AMBIGUOUS` 1、`TABLE_ROW_ARITY` 1、`DECL_DESTINATION_UNRESOLVED` 1。
**不宣称 0，不为 ≤10 削弱 fail-closed。**

## 2. Review r3 逐条修复

- **F-01（P1）**：prose 跳过前先 `_probe_identity()`；已存在的仓库顶层单组件（含空格/CJK，如
  `资料 文件`、`中文目录`）会正常解析并登记保护；不存在才 warning。新增“已存在顶层 CJK/空格路径保护”
  正例与“不存在单组件 CJK → warning”反例。
- **F-05（P1）**：控制字符比例检查对所有长度生效（不再仅 `>=64`）；24 bytes、20×0x01 + CJK 的
  GB18030 payload 被拒绝为 `FILE_UNREADABLE`；新增该组合反例。
- **F-06（P2）**：`RESIDUAL.md` 移除 240 字符截断，保留 audit JSON 原始完整 `message`（表格内
  `<br>` 转义、`|` 转义）。
- **AC1/TRIAGE（P2）**：`build_reports.py` 的 `decision_for()` 改为按 r2 实际 error/warning 数据
  匹配；6 条 generalized destination 现显示 `after: DECL_DESTINATION_GENERALIZED / still fatal`，
  `ENV-BUNDLE-1-FU1` 的 `DECL_UNKNOWN_DISPOSITION` 显示仍 fatal；TRIAGE 重新生成。
- **before/after 快照（P2）**：before 由旧工具重跑，`audit-before.log`/`audit-after.log` 均含完整
  命令（含 `-B`、参数）、cwd、`PARENT_SHELL`、`SHELL=False`、exit；新增
  `evidence/audit-snapshots.json`（git HEAD + `git ls-files -z` sha256 + 工具 sha256 +
  `same_snapshot`）。
- **Handoff 计数（P3）**：`check.ps1` 实际为 **7 errors / 2 warnings**，本文与 Task 一致。
- r2 已通过的 F-02/F-03/F-04/F-07/F-08 语义保持不变。

## 3. 命令 / exit code

| 命令 | 结果 |
|---|---|
| `python -B -m unittest test_declaration_remediation -v` | **exit 0**，20/20 OK |
| `python -B run_suite.py`（既有 80 tests，只读副本） | **exit 0**，80/80 OK |
| `clean_workspace.py --replay-incident <ledger>` | **exit 0**，15/15 REJECT、0 删除、18/18 source |
| `remove_worktrees.py --replay-incident <ledger>` | **exit 0**，同上 |
| before 审计（旧工具） | **exit 2**，163 errors（fail-closed） |
| after 审计（当前工具） | **exit 2**，76 errors / 236 warnings（0 删除） |
| `run_evidence.py` | **exit 0**（`evidence-ok`） |
| `check.ps1` | **exit 1**，FAIL (7 errors, 2 warnings)（base 问题） |

环境：Windows 11 / Python 3.14.6 / Git 2.52；夹具在 `%TEMP%`；旧证据目录只读；
`PYTHONPYCACHEPREFIX` 指向 workspace temp。

## 4. 治理检查

`check.ps1` exit 1，FAIL (7 errors, 2 warnings)：TASK_LEDGER 过期 ×2、既有 archive/history stale
引用 ×3、REBASELINE_PLAN 超预算、READY DAG 仅允许 `ready`（本 Task `in_review`，由 Lead/Codex
在主仓同步）；未修改 Plan/STATUS/check.ps1/task_ledger.py。

## 5. 提交 / 证据

- evidence commit：`2c38980c98385be79e4d67e801a954d698955c80`（冻结代码/测试/报告/日志/manifest/snapshot；30 条 Canonical Evidence 行 pin 它）
- Task-only 记录 commit：紧随其后（本 Handoff + Task 文件）
- 报告/证据：`REMEDIATION.md`、`RESIDUAL.md`（完整 message）、`TRIAGE.md`（数据驱动）、
  `audit-before/after.json`、`non-declaration-json-exceptions.json`、`evidence/`。

## 6. 残余风险

76 条残余：44 个不完整 identity 表需 Codex 裁定“补列/明确叙述”；6 泛化声明、6 泛化 destination、
4 env、1 歧义相对路径、2 含 token JSON、1 malformed 行、1 destination prose、3 损坏文件需裁定。
全部在 `RESIDUAL.md` 逐条可审计。
