---
handoff_id: HANDOFF-WORKSPACE-DECLARATION-REMEDIATION-1
task_id: WORKSPACE-DECLARATION-REMEDIATION-1
author: workspace-hardening (DeepSeek Harness)
reviewer: Codex
status: in_review
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
start_commit: f0f19596f
evidence_commit: dca07bd3d5ebbe21c39c5d596dd3295aef8c10d1
date: 2026-10-21
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
---

# WORKSPACE-DECLARATION-REMEDIATION-1 Handoff

> Handoff 不是 Review、不是批准、不是关闭。Task 状态仍为 `in_review`。
> 本 Task 未执行任何真实 apply/删除/移动/GC/prune/push；未修改任何历史 Task/证据/untracked 文件。

## 1. 结果摘要（真实仓库，同命令/同快照）

| 指标 | before | after |
|---|---:|---:|
| declarations | 1858 | 1855 |
| protected roots | 1264 | 1262 |
| errors | **163** | **15** |
| warnings | 54 | 239 |
| exit code | 2（fail-closed） | 2（fail-closed） |

15 条残余全部列于 `RESIDUAL.md`（file/code/message/tracked/owner/原因/裁定建议）：
`DECL_GENERALIZED` 6、`DECL_ENV` 4、`JSON_PARSE` 2、`DECL_RELATIVE_AMBIGUOUS` 1、
`TABLE_ROW_ARITY` 1、`DECL_DESTINATION_UNRESOLVED` 1。
**未达 ≤10 目标**：10 条是 Task 明确要求保留待裁定的策略性缺口（泛化 workspace root、env），
5 条是真实非策略残余；达到 10 需要削弱 fail-closed 或改写冻结历史，二者都被 Task 禁止（详见 RESIDUAL.md）。

## 2. 修复内容（仅 `tools/governance/clean_workspace.py` 解析核心）

1. **AC2 JSON 识别**：BOM 容错加载；不可解析 JSON 仅在（含 `source_path`/`resource_type`/`disposition`
   token | 文件名像声明清单 | tracked 且非 instrumentation 命名）时 `JSON_PARSE` fatal；其余
   `JSON_NON_DECLARATION` warning。JSON_PARSE 69 → 2。
2. **AC3 非路径 source**：`NOT_APPLICABLE`/`none yet`/中文说明/占位符 → `DECL_SOURCE_NOT_A_PATH`
   warning 并跳过（不登记保护）；bare 标识符仍 `DECL_BARE_NAME` fatal；真实 path-like `PRESERVE_*`
   失败仍 fatal。DECL_BARE_NAME 57 → 0、DECL_UNKNOWN_DISPOSITION 9 → 0、DECL_RELATIVE_UNRESOLVED 6 → 0。
3. **AC4 历史编码**：`read_text` UTF-8 失败 → GB18030 严格解码 + `FILE_ENCODING_LEGACY` warning；
   两种编码失败仍 `FILE_UNREADABLE`。FILE_UNREADABLE 3 → 0。
4. **AC5 叙述表格**：Resource Manifest / Canonical Evidence 仅接受精确英文 schema；叙述/中文表格跳过并
   warning；真正 malformed 资源表仍 `TABLE_ROW_ARITY`。
5. **未削弱 F-01…F-07**：既有 80 tests 全过；tracked 非 instrumentation 不可解析 JSON 仍 fatal；
   path-like unresolvable destination 仍 fatal；junction/alias 保护不变。

## 3. 保护未丢失（AC7）

`evidence/protection-delta.json`：旧解析器 1858/1264 → 新 1855/1262；被移除的 3 条声明均为旧解析器
误把 prose 串登记为保护身份；逐条检查不存在为单一现有路径，故**无真实保护丢失**；新增保护覆盖不变。

## 4. 命令 / exit code

| 命令 | 结果 |
|---|---|
| `python -B -m unittest test_declaration_remediation -v`（新 14 夹具） | **exit 0**，14/14 OK |
| `python -B run_suite.py`（既有 80 tests，只读副本） | **exit 0**，80/80 OK |
| `clean_workspace.py --replay-incident <ledger>` | **exit 0**，15/15 REJECT、0 删除、18/18 source |
| `remove_worktrees.py --replay-incident <ledger>` | **exit 0**，同上 |
| `clean_workspace.py --repo G:/CODEX/New Manga --workspace-root G:/CODEX/New Manga.workspace --audit-declarations` | **exit 2**，15 errors / 239 warnings（fail-closed，0 删除） |
| `run_evidence.py` | **exit 0**（`evidence-ok`） |
| `check.ps1 -TaskPath ...` | **exit 1**，FAIL (7 errors, 3 warnings)（见下） |

环境：Windows 11 / Python 3.14.6 / Git 2.52；测试夹具均在 `%TEMP%`；旧 evidency 目录只读；
`PYTHONPYCACHEPREFIX` 指向 `G:/CODEX/New Manga.workspace/temp/WORKSPACE-DECL-REMEDIATION/pycache`。

## 5. 治理检查（worktree）

`check.ps1` exit 1，`FAIL (7 errors, 3 warnings)`：2 条 TASK_LEDGER 过期 + 3 条既有
`archive/history` stale 引用 + `REBASELINE_PLAN` 超预算 + READY DAG 仍只允许 `ready`（本 Task 已
`in_review`，由 Lead/Codex 在主仓同步 Plan）。均未修改 Plan/STATUS/check.ps1/task_ledger.py；
最终治理检查由 Codex 在主仓集成后执行。原始输出+exit：`evidence/governance-check.log`。

## 6. 提交 / 证据

- evidence commit：`dca07bd3d`（代码/测试/报告/日志/manifest 冻结；27 条 Canonical Evidence 行 pin 它）
- Task-only 记录 commit：紧随其后（本 Handoff + Task 文件）
- 报告：`REMEDIATION.md`、`RESIDUAL.md`、`TRIAGE.md`（163 行逐条）、`audit-before.json`、`audit-after.json`
- 证据目录：`verification/WORKSPACE-DECLARATION-REMEDIATION-1/evidence/`（environment、manifest、logs）

## 7. 残余风险

1. 15 条残余需 Codex/用户裁定后才能让真实仓库 audit 接近 0（10 条策略性 + 5 条真实缺口）。
2. 69 条不可解析 JSON 中 58 条 BOM/格式容忍后已正常解析；剩余 2 条 token 文件与 9 条 untracked
   instrumentation 已按规则分类，但 tracked instrumentation 命名规则依赖文件名启发式。
3. warning 增至 239（其中 91 条 `TABLE_NOT_CANONICAL_EVIDENCE`、65 条 `DECL_SOURCE_NOT_A_PATH`）：
   保守跳过、不登记保护，Review 可抽查是否应保留某些叙述表为声明。
4. 真实仓库仍 fail-closed（exit 2），本 Task 不授权也不执行任何真实清理。
