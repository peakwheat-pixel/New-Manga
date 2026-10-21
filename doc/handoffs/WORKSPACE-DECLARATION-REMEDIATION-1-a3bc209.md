---
handoff_id: HANDOFF-WORKSPACE-DECLARATION-REMEDIATION-1-R4
task_id: WORKSPACE-DECLARATION-REMEDIATION-1
author: workspace-hardening (DeepSeek Harness)
reviewer: Codex
status: in_review
review_round: r4 changes_requested fixes
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
start_commit: f0f19596f
evidence_commit: a3bc20901067a743d09ebd48c623d0a017df021f
date: 2026-10-21
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
---

# WORKSPACE-DECLARATION-REMEDIATION-1 Handoff (review r4)

> Handoff 不是 Review、不是批准、不是关闭。Task 仍为 `in_review`。
> 未执行任何真实 apply/删除/移动/GC/prune/push；未修改历史 Task/证据/untracked 文件。

## 1. 结果摘要（真实仓库，same command / same snapshot）

| 指标 | before | r1 | r2 | r3 | r4 |
|---|---:|---:|---:|---:|---:|
| declarations | 1858 | 1855 | 1858 | 1858 | 1858 |
| protected roots | 1264 | 1262 | 1264 | 1264 | 1264 |
| errors | **163** | 15 | 76 | 76 | **76** |
| warnings | 54 | 239 | 236 | 236 | 236 |
| exit code | 2 | 2 | 2 | 2 | 2（fail-closed） |

快照：`same_snapshot=true`（审计前后共 4 个采样点：before/after 各 audit 前后）。
git HEAD `f0f19596f…`；扫描输入 7416 tracked + 1504 untracked，逐文件内容 sha256 聚合
`scanned_input_sha256`；before/after 命令记录实际 argv（含 `--out`），见
`evidence/audit-snapshots.json`。76 条 residual 分类不变（`TABLE_SCHEMA_INCOMPLETE` 44、
`DECL_GENERALIZED` 6、`DECL_DESTINATION_GENERALIZED` 6、`DECL_RELATIVE_UNRESOLVED` 6、
`DECL_ENV` 4、`FILE_UNREADABLE` 3、`DECL_UNKNOWN_DISPOSITION` 2、`JSON_PARSE` 2、
`DECL_RELATIVE_AMBIGUOUS` 1、`TABLE_ROW_ARITY` 1、`DECL_DESTINATION_UNRESOLVED` 1）。
**不宣称 0，不为 ≤10 削弱 fail-closed。**

## 2. Review r4 逐条修复

- **F-01（P1）**：新增 `_prose_probe()` 三态分类：`identity`（安全可解析 → 登记保护）、
  `error`（已解析但 identity 不安全/不可读 → 保留原 GuardError 为 fatal）、`prose`（仅
  `DECL_BARE_NAME`/`DECL_RELATIVE_UNRESOLVED`/`DECL_RELATIVE_NO_ROOT` 三类“非身份”才跳过）。
  generalized junction（顶层 CJK/空格名指向 workspace/managed root）在 source 与 evidence pin
  两个入口都 fatal。新增 3 个 junction 夹具（generalized source fatal、safe junction 保护、
  generalized evidence fatal）。
- **快照（P2）**：`run_evidence.py` 对实际扫描输入（tracked + untracked，逐文件内容 sha256）取
  指纹；before/after audit 前后各采样一次（4 点一致 `same_snapshot=true`）；命令记录为实际 argv
  （含 `--out`），不再手写漏参数。
- **TRIAGE（P2）**：`build_reports.py` 索引键改为 `(file, locator, role)`，source/destination/evidence/
  table 各自归因；第 45–48 行 source generalized 不再被 destination 覆盖，TRIAGE 重新生成。
- **run_evidence 自日志（P2）**：新增 `evidence/run-evidence.log`（完整 COMMAND/CWD/
  PARENT_SHELL/SHELL/EXIT_CODE）与 `evidence/run-evidence.exitcode`，均已冻结进 manifest。
- r2/r3 已通过的 F-02/F-03/F-04/F-05/F-06/F-07/F-08 语义不变。

## 3. 命令 / exit code

| 命令 | 结果 |
|---|---|
| `python -B -m unittest test_declaration_remediation -v` | **exit 0**，23/23 OK |
| `python -B run_suite.py`（既有 80 tests，只读副本） | **exit 0**，80/80 OK |
| `clean_workspace.py --replay-incident <ledger>` | **exit 0**，15/15 REJECT、0 删除、18/18 source |
| `remove_worktrees.py --replay-incident <ledger>` | **exit 0**，同上 |
| before 审计（旧工具） | **exit 2**，163 errors（fail-closed） |
| after 审计（当前工具） | **exit 2**，76 errors / 236 warnings（0 删除） |
| `run_evidence.py` | **exit 0**（`evidence-ok`；自日志/exit 文件已冻结） |
| `check.ps1` | **exit 1**，FAIL (7 errors, 2 warnings)（base 问题） |

## 4. 治理检查

`check.ps1` exit 1，FAIL (7 errors, 2 warnings)：TASK_LEDGER 过期 ×2、既有 archive/history stale
引用 ×3、REBASELINE_PLAN 超预算、READY DAG 仅允许 `ready`（本 Task `in_review`，由 Lead/Codex
在主仓同步）；未修改 Plan/STATUS/check.ps1/task_ledger.py。

## 5. 提交 / 证据

- evidence commit：`2deab2f077cd91bbd71bdb4bd599432e1b2d3242`（32 条 Canonical Evidence 行 pin 它）
- Task-only 记录 commit：紧随其后（本 Handoff + Task 文件）
- 报告/证据：`REMEDIATION.md`、`RESIDUAL.md`（完整 message）、`TRIAGE.md`（role 索引）、
  `audit-before/after.json`、`non-declaration-json-exceptions.json`、`evidence/`（含 snapshots、
  run-evidence.log/exit）。

## 6. 残余风险

同 r3：44 个不完整 identity 表需 Codex 裁定“补列/明确叙述”；6 泛化声明、6 泛化 destination、
4 env、1 歧义相对路径、2 含 token JSON、1 malformed 行、1 destination prose、3 损坏文件需裁定；
全部在 `RESIDUAL.md` 逐条可审计。
