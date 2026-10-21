---
handoff_id: HANDOFF-WORKSPACE-DECLARATION-REMEDIATION-1-R2
task_id: WORKSPACE-DECLARATION-REMEDIATION-1
author: workspace-hardening (DeepSeek Harness)
reviewer: Codex
status: in_review
review_round: r2 changes_requested fixes (F-01..F-08)
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
start_commit: f0f19596f
evidence_commit: a431d7084896abe5a824d478925d1dabc45802ef
date: 2026-10-21
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
---

# WORKSPACE-DECLARATION-REMEDIATION-1 Handoff (review r2)

> Handoff 不是 Review、不是批准、不是关闭。Task 仍为 `in_review`。
> 未执行任何真实 apply/删除/移动/GC/prune/push；未修改历史 Task/证据/untracked 文件。

## 1. 结果摘要（真实仓库，同命令/同快照）

| 指标 | before | after (r1) | after (r2) |
|---|---:|---:|---:|
| declarations | 1858 | 1855 | 1858 |
| protected roots | 1264 | 1262 | 1264 |
| errors | **163** | 15 | **76** |
| warnings | 54 | 239 | 236 |
| exit code | 2 | 2 | 2（fail-closed） |

r2 后的 76 条不是回退，而是 Codex Review 要求恢复 fail-closed 的结果：
F-01 使 8 条 path-like prose 恢复 fatal、F-03 使 6 条泛化 destination 恢复 fatal、F-04 使 44 个
不完整 identity 表恢复 fatal、F-05 拒绝 3 个含 NUL/UTF-16 的损坏文件；其余为原有策略性残余。
**不宣称 0，不追求 ≤10；不为数字削弱 fail-closed。**

## 2. Review r2 逐条修复

- **F-01**：`is_descriptive_value` 只在无路径语法/明确占位符时跳过；`is_path_like()` 为真必须解析，
  失败 fatal。新增“spaced data 中文”保护正例与“见 G:/...”嵌入路径 fatal 反例。
- **F-02**：删除文件名启发式；不可解析 JSON 只认 `non-declaration-json-exceptions.json` 的
  `path + sha256`（67 条已审阅日志），sha 不匹配即不豁免；真声明改名 `*.stdout.json`/截断在 token
  前仍 fatal；测试覆盖显式豁免、错误 sha、改名反例。
- **F-03**：path-like generalized destination 恢复 fatal（`DECL_DESTINATION_GENERALIZED`）。
- **F-04**：Resource Manifest/Canonical Evidence 只要声明 identity 列但缺必要列 →
  `TABLE_SCHEMA_INCOMPLETE` fatal；完全无 identity 列的叙述表才 warning。
- **F-05**：GB18030 fallback 仅接受含 CJK 文本；NUL、控制字符比例高、非 CJK 二进制均
  `FILE_UNREADABLE`；正反例已加。
- **F-06**：`RESIDUAL.md` 每条补原始 `message` 字段。
- **F-07**：`run_evidence.py` 生成的日志增加 `PARENT_SHELL` 与 `SHELL: False`（subprocess 列表参数，
  无 shell 插值）。
- **F-08**：Task 证据行数与 Handoff 引用一致（29 行，含 EV-MANIFEST）。

## 3. 保护未削弱

`evidence/protection-delta.json`：旧/新解析器均为 1858 declarations / 1264 roots，无真实保护丢失；
3 个 GBK 历史文件通过 `FILE_ENCODING_LEGACY` 正常读取，3 个损坏文件 fail-closed。

## 4. 命令 / exit code

| 命令 | 结果 |
|---|---|
| `python -B -m unittest test_declaration_remediation -v` | **exit 0**，17/17 OK |
| `python -B run_suite.py`（既有 80 tests，只读副本） | **exit 0**，80/80 OK |
| `clean_workspace.py --replay-incident <ledger>` | **exit 0**，15/15 REJECT、0 删除、18/18 source |
| `remove_worktrees.py --replay-incident <ledger>` | **exit 0**，同上 |
| 真实审计 `--audit-declarations` | **exit 2**，76 errors / 236 warnings（0 删除） |
| `run_evidence.py` | **exit 0**（`evidence-ok`） |
| `check.ps1` | **exit 1**，FAIL (7 errors, 3 warnings)（同 r1 的 base 问题） |

环境：Windows 11 / Python 3.14.6 / Git 2.52；夹具在 `%TEMP%`；旧证据目录只读；
`PYTHONPYCACHEPREFIX` 指向 workspace temp。

## 5. 治理检查

`check.ps1` exit 1：TASK_LEDGER 过期 ×2、既有 archive/history stale 引用 ×3、REBASELINE_PLAN
超预算、READY DAG 仅允许 `ready`（本 Task `in_review`，由 Lead/Codex 在主仓同步）。未修改
Plan/STATUS/check.ps1/task_ledger.py；日志见 `evidence/governance-check.log`。

## 6. 提交 / 证据

- evidence commit：`a431d7084896abe5a824d478925d1dabc45802ef`（代码/测试/报告/日志/manifest 冻结；29 条 Canonical Evidence 行 pin 它）
- Task-only 记录 commit：紧随其后（本 Handoff + Task 文件）
- 报告/证据：`REMEDIATION.md`、`RESIDUAL.md`、`TRIAGE.md`、`audit-before/after.json`、
  `non-declaration-json-exceptions.json`、`evidence/`（environment、manifest、logs）

## 7. 残余

76 条：`DECL_GENERALIZED` 6、`DECL_ENV` 4、`DECL_DESTINATION_GENERALIZED` 6、
`TABLE_SCHEMA_INCOMPLETE` 44、`DECL_RELATIVE_UNRESOLVED` 6、`DECL_UNKNOWN_DISPOSITION` 2、
`JSON_PARSE` 2、`FILE_UNREADABLE` 3、`DECL_RELATIVE_AMBIGUOUS` 1、`TABLE_ROW_ARITY` 1、
`DECL_DESTINATION_UNRESOLVED` 1。全部列于 `RESIDUAL.md`（含 message）；需 Codex/用户裁定。
