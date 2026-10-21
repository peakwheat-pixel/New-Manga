---
task: WORKSPACE-DECLARATION-REMEDIATION-1-REVIEW-R7
reviewer: Codex
author: workspace-hardening
base_commit: f0f19596f
reviewed_head: f3d8cb27b196472d12f979c29788ad3966ab026f
implementation_head: cacd1c021a34c363f5b36d1b2b72f19f07acc081
decision: approved
review_mode: read_only
---

## 1. 结论（A–D）

**A — F-05：通过。** Resource Manifest 的 `resource_type`、`source_path`、`disposition`、`destination_path` 和 Canonical Evidence 的 `evidence_id`、`path` 都纳入重复列检查；命中重复即报 `TABLE_DUPLICATE_IDENTITY_COLUMN` fatal，并跳过该表，不会登记首列内容。[实现位置](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:1268>)

严格来说，`_exact_column()` 本身仍会返回第一个匹配索引；但它的解析调用方会在使用行值之前先检查重复列，重复表不会走到登记路径。测试覆盖 Resource Manifest 重复 `source_path` fatal、Canonical Evidence 重复 `path` fatal，以及单列有效声明仍将候选判为 `REJECT`。[新增夹具](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests/test_declaration_remediation.py:236>)

**B — P3：通过。** `_find_column` 已从 Python 代码删除，`git grep` 在提交树的 `*.py` 中无命中。交接文档有一处文字提及该名称，内容是在记录其删除，不是代码调用。

**C — 证据与回归：通过。** `f3d8cb2` 是 E11 `cacd1c0` 的直接子提交；相对 E11 只更新 Task/交接记录，无代码变更。E11 的 32 条 Canonical Evidence pin 全部指向 E11 且哈希匹配，30 项 manifest 也逐项匹配。冻结日志记录新增测试 29/29、既有测试 80/80、双 replay 各 15/15 拒绝且 0 删除、18 个 source 覆盖、审计 76 errors/236 warnings、`run_evidence.py` exit 0。`git diff --check` 本轮实跑 exit 0。

相对 base 的变更限于工具代码、本 Task 的 verification、Task 与 handoff；未发现范围外历史文件改动或 Git 路径删除。保护差异记录为 declarations/root 均保持 1858/1264，dropped/added 均为 0。本轮没有执行删除、push、GC 或 prune。

**D — 集成：可以进入集成。** 76 条残余已逐条列明并归类；保留它们不要求削弱 fail-closed 行为。集成后仍须保留审计对这些错误的拒绝效果，并在 Task 关闭前完成资源核销及主线治理检查。

## 2. Findings

无代码或证据阻塞项。`_exact_column()` 的首个匹配行为由解析层的重复检查约束；当前没有其他 Python 调用方绕过该检查。

## 3. AC1–AC7 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | PASS | before/after 审计、163 项 TRIAGE 与 REMEDIATION 报告随 E11 固定。 |
| AC2 | PASS | E11 本轮未改 JSON 声明处理；冻结证据与 manifest pin 匹配。 |
| AC3 | PASS | E11 本轮未改路径解析规则；保护差异无丢失声明。 |
| AC4 | PASS | E11 本轮未改编码边界；既有回归日志固定。 |
| AC5 | PASS | 六类身份列均有重复检查；两类表的重复列负例与正常保护正例均覆盖。 |
| AC6 | PASS | `RESIDUAL.md` 列出 76 条并给出分组与处理裁定。 |
| AC7 | PASS | 32 pins、30 manifest、测试/replay/audit/runner 结果均可从 E11 复算或读取；`git diff --check` exit 0。 |

## 4. 残余裁定

76 条由 **61 条应保留的 fail-closed 错误**和 **15 条待后续政策/内容裁定的历史问题**组成。[残余清单](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/RESIDUAL.md:84>)

- 61 条：44 `TABLE_SCHEMA_INCOMPLETE`、6 `DECL_RELATIVE_UNRESOLVED`、2 `DECL_UNKNOWN_DISPOSITION`、6 `DECL_DESTINATION_GENERALIZED`、3 `FILE_UNREADABLE`。不应通过静默跳过或批量改历史文件降低数量。
- 15 条：6 `DECL_GENERALIZED`、4 `DECL_ENV`、1 `DECL_RELATIVE_AMBIGUOUS`、2 `JSON_PARSE`、1 `TABLE_ROW_ARITY`、1 `DECL_DESTINATION_UNRESOLVED`。保留为待裁定项，不作为本次解析器修复的集成阻塞。

审计仍是 76 errors、exit 2，表示清理操作仍须 fail-closed。此批准不代表对残余条目授权清理或删除。Task 的 `resource_closeout_status` 仍为 `pending`；在关闭 Task 前应核销并保留所登记的 worktree 与临时缓存状态。

## 5. 运行证据

| 命令/证据 | 本轮状态与 exit | 结果 |
|---|---|---|
| `git diff --check f0f19596f..f3d8cb27b196472d12f979c29788ad3966ab026f` | 已运行，**0** | 无 whitespace 错误。 |
| E11 pin/manifest 只读复算（Git blob SHA-256） | 已运行，**0** | 32 pins 全匹配；manifest 30 项全匹配。 |
| `git grep -n '_find_column' f3d8cb27... -- '*.py'` | 已运行，**1** | 无 Python 命中；exit 1 表示无匹配。 |
| 目标 worktree `git status --short --branch` | 已运行，**0** | `dsh/WORKSPACE-DECLARATION-REMEDIATION-1` 干净。 |
| 新增测试与既有测试 | **NOT_RUN** | E11 冻结日志分别记录 `Ran 29 tests / OK / exit 0`、`Ran 80 tests / OK / exit 0`。 |
| 双 incident replay | **NOT_RUN** | E11 JSON 分别记录 15/15 rejected、0 deleted、0 violations、18 个 source 覆盖。 |
| before/after audit | **NOT_RUN** | 冻结结果分别为 163/54、76/236；after exit 2，符合 fail-closed。 |
| `run_evidence.py` | **NOT_RUN** | E11 的 runner 日志与 exit 文件记录 `evidence-ok`、exit 0。该脚本会重写证据日志、快照和 manifest，因此本轮没有执行。 |

主仓在审查开始时已有大量未提交/未跟踪内容；当前仍有 1,245 个状态条目。目标交付 worktree 保持干净。本轮只执行了读取、哈希复算和 diff 检查。

**推荐下一步：**在现有干净且授权的集成 worktree 集成 `f3d8cb27b`，随后运行治理检查并完成资源核销；不要在当前 dirty 主仓直接集成。