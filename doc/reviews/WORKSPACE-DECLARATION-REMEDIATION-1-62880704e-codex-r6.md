---
task: WORKSPACE-DECLARATION-REMEDIATION-1-REVIEW-R6
reviewer: Codex
author: workspace-hardening
base_commit: f0f19596f
reviewed_head: 62880704e
implementation_head: 4f2e65304
decision: changes_requested
review_mode: read_only
---

## 1. 结论（A–F）

- **A — 通过。** [Task](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/tasks/WORKSPACE-DECLARATION-REMEDIATION-1.md:155>) 已登记 linked worktree 为 `PRESERVE_REFERENCED`，temp/pycache 为 `NOT_APPLICABLE` 并说明其用途、现状；`resource_closeout_status` 为 `pending`。复核时两个目录均存在，pycache 为空。
- **B — 通过。** [Handoff](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/doc/handoffs/WORKSPACE-DECLARATION-REMEDIATION-1-4f2e653.md:10>) 的 frontmatter 与正文均锚定 E9 `4f2e65304`；Task 的 `delivery_head` 也指向 E9。未发现旧 `2deab2f` 引用。
- **C — 通过。** ambiguous 夹具以同一 `table` role 的两个不同 code 调用 `match_status`，并断言旧 code 返回 `None`，覆盖了不猜测分支。它是 matcher 级断言，没有覆盖完整 TRIAGE 输出路径。
- **D — 通过。** `git diff --check f0f19596f..62880704e` exit `0`。
- **E — 证据与范围基本通过。** 32 条 pin 均能从 E9 和当前工作树复算；30 条 manifest 项也全部匹配。冻结日志记录 26 新测试、80 既有测试通过；双 replay 均为 15/15 REJECT、0 删除、0 violations、18/18 source；审计为 76 errors / 236 warnings、exit `2`；`run_evidence.py` 记录 exit `0`。没有发现历史文件改动或 Git diff 删除项；本地回放记录 0 删除，worktree 与 pycache 仍存在。**本轮未执行 push；作者此前是否推送无法由本地快照证明。**
- **F — 暂不能进入集成。** 76 条残余均有逐条记录，但解析器另有下述 P2 fail-open 缺口。修复并重新冻结证据前，不建议集成。

## 2. Findings

- **F-05 P2 — 重复身份列会静默漏掉声明。** [clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:1267>) 的 `_exact_column()` 对重复列名只返回第一个索引；`parse_table_block()` 只校验行宽，不拒绝重复身份表头。Resource Manifest 中重复的 `source_path` 会只将第一列传给保护索引，第二个路径被忽略；Canonical Evidence 中重复的 `path` 也只 pin 第一列。这与 AC5 的 fail-closed 表格要求冲突。应拒绝重复身份列并为 Resource Manifest 与 Canonical Evidence 补夹具，再重跑并冻结证据。
- **P3，非阻断：** `clean_workspace.py:1259` 的 `_find_column()` 已无调用，是遗留 helper。

除 F-05 外，A–D 的 r5 问题已修复。由于 F-05 可能使资源声明未受保护，本轮判定为 `changes_requested`。

## 3. AC1–AC7 判定

- **AC1：MET** — 分诊与报告证据齐全；冻结记录包含 163 条 triage。
- **AC2：MET** — JSON 异常清单与精确路径、SHA 例外证据已 pin。
- **AC3：MET** — path-like 与 generalized junction 的 fail-closed 语义有对应代码和证据。
- **AC4：MET** — 历史编码与二进制拒绝结果有冻结证据。
- **AC5：PARTIAL** — 不完整 schema 与 malformed row 有处理；重复身份列仍可静默漏项。
- **AC6：MET** — `RESIDUAL.md` 有 76 条记录。
- **AC7：MET（冻结证据）** — pins、manifest 与日志校验通过；本轮没有重跑测试。

## 4. 残余裁定

`RESIDUAL.md` 的 76 条与审计后 76 errors 对应，逐条说明了原因和建议处理方式；这些建议仍待 Codex/用户裁定。它们可以继续作为 fail-closed 残余跟踪，但当前真实仓库审计仍 exit `2`，不能据此放行真实清理。

`governance-check.log` 记录 exit `1`（7 errors、2 warnings），包括过期 `TASK_LEDGER`、失效文档引用、Plan 预算及 READY DAG 与 Task `in_review` 状态不一致。Task 文档说明由 Codex 在主仓集成时处理；完成集成与关闭前仍须核销。

## 5. 运行证据

以下均为只读复核；未运行会写入证据目录的 `run_evidence.py`。

- `git diff --check f0f19596f..62880704e` — **exit 0**
- `git diff --name-status 4f2e65304..62880704e` — **exit 0**；仅 Task 与 Handoff
- Python `-B` 内联 SHA-256 复算（读取 E9 Git blob 与工作树）— **exit 0**；32/32 pins、30/30 manifest 匹配
- 只读读取 E9 JSON — **exit 0**；审计前 163 errors / 54 warnings，审计后 76 errors / 236 warnings；双 replay 各 15/15、0 删除、18/18 source
- 新增测试、既有测试、`run_evidence.py`、真实审计：**NOT_RUN**。冻结证据记录分别为 26 tests `OK`、80 tests `OK`、runner exit `0`、真实审计 exit `2`
- 治理检查：**NOT_RUN**；冻结日志记录 exit `1`
- 状态复核：目标 worktree 两次均干净；主仓 1601 条既存状态记录的 SHA-256 前后相同（`DB129DB8…519A233`）

**建议下一步：** 将 F-05 交由 `workspace-hardening` 修复，增加重复身份列 fatal 检查及夹具、重新冻结 E9 证据后再申请复核。