---
task: WORKSPACE-CLEANUP-TOOL-HARDENING-1-REVIEW-R2
reviewer: Codex
author: dsh-workspace-hardening
base_commit: b8a1e519703f13af73b320dded117004b4bb189a
reviewed_head: beeac02afee45d1b58bcbd8110bbc31048a23675
implementation_head: dbd6cbf5f3afa0d38bb3aa7b869198c4209f4499
decision: changes_requested
review_mode: read_only
---

## 1. 结论（F-01..F-07）

- **F-01：已修复。** 声明同时登记词法路径和真实目标；真实入口 junction 夹具证明真实目标候选与 alias 候选均为 `REJECT`。
- **F-02：未完全修复，仍有 P1 问题。** 非忽略 untracked 声明已纳入扫描，但 malformed JSON 只有含字面 `PRESERVE` 才整态拒绝；`MIGRATE`、`ARCHIVE` 声明也具保护性，存在漏保护后继续清理的路径。审计数字可区分：7351+1504 是枚举的路径数，2268 `.md`+1146 `.json` 是解析的文件数；Handoff 将前者称作“声明文件”不准确。
- **F-03：已修复。** `is_path_like()` 规则明确；不可解析的 path-like destination 记完整性错误并拒绝，说明文字和占位符按规则放行。
- **F-04：已修复。** apply 前按词法路径和真实路径检查 `--out` 是否等于或位于候选；清册写入和删除都在检查之后。夹具覆盖普通 inside 和 junction inside；未见单独的 `--out` 等于候选夹具。
- **F-05：部分修复，仍需处理。** 27 条中，25 条指向 `dbd6cbf5f` 的 commit pin 均通过字节重算；另 2 条 SHA-only pin 匹配工作区字节。但 `dbd6` 的 manifest 只有 10 项且不含 `governance-check.log`；`beeac` 又新增该日志并修改 manifest。当前工作区 manifest 为 11/11，`beeac` commit blob 口径为 10/11：治理日志 SHA 因 `core.autocrlf=true` 与 Git blob 字节不一致。证据集合没有完整冻结在声明的 evidence commit。
- **F-06：已修复。** stash 与权限故障注入经 `main(argv)` 入口验证；重复 inventory identity 明确报 `INVENTORY_DUPLICATE_IDENTITY`。AC4 的 11 类用例均有拒绝断言。
- **F-07：已修复。** 治理检查的 5 个 error 归因为 worktree 缺少主仓未跟踪 drafts/archive 内容及既有 stale refs；4 个 warning 区分了仓库级 warning 和本 Task 的 Handoff evidence-dir warning。

## 2. Findings

1. **F-02 / P1：malformed JSON 中的保护声明可能被当作 warning 放行**  
   [clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/tools/governance/clean_workspace.py:1198>) 在 JSON 解析失败时只检查 `"PRESERVE" in raw`；否则添加 `JSON_NONSTANDARD` warning，`run_clean_workspace()` 只因 `index.errors` 拒绝。可是 `MIGRATE`、`ARCHIVE` 也会被 `is_protective()` 视为保护 disposition。一个语法错误但含候选 `source_path` 和 `"disposition":"MIGRATE"`、不含 `PRESERVE` 的声明文件因此可能漏掉保护而继续 apply。建议将扫描范围内 JSON 解析失败一律记为完整性错误，并增加 `MIGRATE`/`ARCHIVE` 反例测试。

2. **F-05 / P2：evidence commit 与最终证据清单不一致**  
   [Task 记录](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-CLEANUP-TOOL-HARDENING-1/doc/tasks/WORKSPACE-CLEANUP-TOOL-HARDENING-1.md:133>) 声明 evidence commit `dbd6cbf5f` 包含全部证据，但 `dbd6..beeac` 仍新增 `governance-check.log`、修改 `manifest.sha256`，并更新 Handoff。建议先提交包含最终日志和最终 manifest 的 evidence commit，再提交只引用它的 Task 记录；同时按 Git blob 字节固定 SHA 基准并重算。

## 3. AC1–AC7 判定表

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | PASS | 词法及真实目标双重保护；junction 真实入口夹具确认目标候选 `REJECT`。 |
| AC2 | **FAIL** | malformed JSON 的非 `PRESERVE` 保护 disposition 可只产生 warning，整态拒绝不完整。 |
| AC3 | PASS | 交付测试日志记录逐文件 size/SHA-256 清册及 apply 接受门槛；本轮未重跑。 |
| AC4 | PASS | 证据映射列出 11 类夹具及断言；stash/权限另经 `main(argv)`。 |
| AC5 | PASS | 默认 dry-run、候选 digest 对照及 apply 前 `--out` 防自删检查；普通与 junction inside 均有夹具。 |
| AC6 | PASS | 回放证据：两个工具均 15/15 拒绝、0 删除、0 violation；审计记录 18/18 incident source 有声明覆盖。 |
| AC7 | PARTIAL | 交付记录新测试 77/77、`test_ac_gate.py` 12/12；`run-resource-manifest-cases.py` 为 0/32、exit 1，归因于范围外的 TASK_LEDGER 仓库状态并已披露。 |

## 4. 是否可进入集成

**不可进入集成。** F-02 尚有 P1 失效关闭缺口，F-05 的证据冻结顺序和 commit 字节验证也未闭合。

当前主仓 [STATUS.md](<G:/CODEX/New Manga/doc/STATUS.md:7>) 仍记为 `ready` / R1 `changes_requested`，被审分支 Task 记录为 `in_review`。STATUS 不在本 Task 的 `allowed_paths`，本轮未修改；Codex 后续应按生命周期同步权威状态。

## 5. 运行证据（只读命令 + exit）

本轮未运行测试或治理 checker；仅读取已提交日志和执行只读 Git/字节核验。

- `git --no-optional-locks status --short --branch`（目标 worktree）：exit `0`，HEAD 为 `beeac02afee45d1b58bcbd8110bbc31048a23675`，worktree clean。
- `git diff --name-only b8a1e5197..dbd6cbf5f`：exit `0`，25 个路径，全部在 frozen `allowed_paths` 内。
- `git diff --name-only dbd6cbf5f..beeac02afee45d1b58bcbd8110bbc31048a23675`：exit `0`，4 个路径，全部在 `allowed_paths` 内；包含 Task、Handoff、治理日志新增和 manifest 修改。
- `git cat-file` 与 SHA-256 重算：显式 commit pins `25/25`；两条 SHA-only pins 匹配工作区字节 `2/2`。manifest 当前工作区 `11/11`，但 `beeac` Git blob 为 `10/11`；不匹配项是 `governance-check.log`。
- `tests/run_suite.py`：**NOT_RUN**（交付日志记录 77/77，exit `0`）。
- `test_ac_gate.py`：**NOT_RUN**（交付日志记录 12/12，exit `0`）。
- `run-resource-manifest-cases.py`：**NOT_RUN**（交付日志记录 0/32，exit `1`）。
- `run_evidence.py`：**NOT_RUN**（交付记录 exit `0`）。
- `check.ps1 -TaskPath ...`：**NOT_RUN**（保存日志记录 exit `1`，5 errors / 4 warnings）。
- 本轮未执行任何真实删除、移动、分支清理、GC、prune 或 push。交付日志中的 apply 测试针对隔离 fixture；真实仓库快照证据记录为未变化。

**推荐下一步：**由 Owner `dsh-workspace-hardening` 修复 malformed JSON 的 fail-closed 路径，并完成独立冻结 evidence commit 与 Task-only 引用提交后，再以新 head 提交 Codex 复审。