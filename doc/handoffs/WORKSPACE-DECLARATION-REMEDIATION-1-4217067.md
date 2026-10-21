---
handoff_id: HANDOFF-WORKSPACE-DECLARATION-REMEDIATION-1-R6
task_id: WORKSPACE-DECLARATION-REMEDIATION-1
author: workspace-hardening (DeepSeek Harness)
reviewer: Codex
status: in_review
review_round: r6 changes_requested fixes (docs/evidence only)
base_commit: 83b111ac104d47b30cf0842f553f97656cd0d8d1
start_commit: f0f19596f
evidence_commit: 421706788ed86d5860a0423443e6323f944c5580
date: 2026-10-21
branch: dsh/WORKSPACE-DECLARATION-REMEDIATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1
---

# WORKSPACE-DECLARATION-REMEDIATION-1 Handoff (review r6, final doc fixes)

> Handoff 不是 Review、不是批准、不是关闭。Task 仍为 `in_review`。
> 本 Task 未执行任何真实 apply/删除/移动/GC/prune/push；未修改历史 Task/证据/untracked 文件。

## 1. 结果摘要（真实仓库，same command / same snapshot）

| 指标 | before | r1 | r2 | r3 | r4 | r6 |
|---|---:|---:|---:|---:|---:|---:|
| declarations | 1858 | 1855 | 1858 | 1858 | 1858 | 1858 |
| protected roots | 1264 | 1262 | 1264 | 1264 | 1264 | 1264 |
| errors | **163** | 15 | 76 | 76 | 76 | **76** |
| warnings | 54 | 239 | 236 | 236 | 236 | 236 |
| exit code | 2 | 2 | 2 | 2 | 2 | 2（fail-closed） |

`same_snapshot=true`：审计前后 4 个采样点；扫描输入 7416 tracked + 1504 untracked，逐文件内容
sha256 聚合；before/after 命令记录实际 argv（含 `--out`），见 `evidence/audit-snapshots.json`。
76 条 residual 分类不变；**不宣称 0，不为 ≤10 削弱 fail-closed**。

## 2. Review r6 修复（仅文档/证据/夹具，未动解析器行为）

- **F-01 资源登记**：Task Resource Manifest 新增 linked worktree
  `G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1`
  （`PRESERVE_REFERENCED`）与 `temp/WORKSPACE-DECL-REMEDIATION/pycache`
  （`NOT_APPLICABLE`，存在但空、未删除，留待核销）；`resource_closeout_status` 改为 `pending`。
- **F-02 Handoff 锚点**：正文 §5 统一为 `421706788ed86d5860a0423443e6323f944c5580`；清理旧轮次正文元数据。
- **F-03 ambiguous 夹具**：改为**同 table role** 的多 code 输入
  （`TABLE_OLD_UNLISTED` + `TABLE_ROW_ARITY`/`TABLE_SCHEMA_INCOMPLETE`），锁定 ambiguous 分支。
- **F-04 whitespace**：`REMEDIATION.md` 与测试文件 EOF 规范为单换行；`git diff --check` 通过。

## 3. 命令 / exit code

| 命令 | 结果 |
|---|---|
| `python -B -m unittest test_declaration_remediation -v` | **exit 0**，26/26 OK |
| `python -B run_suite.py`（既有 80 tests，只读副本） | **exit 0**，80/80 OK |
| `clean_workspace.py --replay-incident <ledger>` | **exit 0**，15/15 REJECT、0 删除、18/18 source |
| `remove_worktrees.py --replay-incident <ledger>` | **exit 0**，同上 |
| before 审计（旧工具） | **exit 2**，163 errors（fail-closed） |
| after 审计（当前工具） | **exit 2**，76 errors / 236 warnings（0 删除） |
| `run_evidence.py` | **exit 0**（`evidence-ok`；自日志/exit 已冻结） |
| `check.ps1` | **exit 1**，FAIL (7 errors, 2 warnings)（base 问题） |

## 4. 治理检查

`check.ps1` exit 1，FAIL (7 errors, 2 warnings)：TASK_LEDGER 过期 ×2、既有 archive/history stale
引用 ×3、REBASELINE_PLAN 超预算、READY DAG 仅允许 `ready`（本 Task `in_review`，由 Lead/Codex
在主仓同步）；未修改 Plan/STATUS/check.ps1/task_ledger.py。

## 5. 提交 / 证据

- evidence commit：`421706788ed86d5860a0423443e6323f944c5580`（32 条 Canonical Evidence 行 pin 它）
- Task-only 记录 commit：紧随其后（本 Handoff + Task 文件）
- 报告/证据：`REMEDIATION.md`、`RESIDUAL.md`、`TRIAGE.md`、`audit-before/after.json`、
  `non-declaration-json-exceptions.json`、`evidence/`（manifest/snapshots/run-evidence/logs）。
- 资源：linked worktree 保留；`temp/.../pycache` 保留未删；`resource_closeout_status: pending`。

## 6. 残余风险

同 r3：44 个不完整 identity 表需 Codex 裁定“补列/明确叙述”；6 泛化声明、6 泛化 destination、
4 env、1 歧义相对路径、2 含 token JSON、1 malformed 行、1 destination prose、3 损坏文件需裁定；
全部在 `RESIDUAL.md` 逐条可审计。
