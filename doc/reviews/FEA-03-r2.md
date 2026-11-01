---
document_id: FEA-03-r2
kind: independent_implementation_review
reviewer: fea03-impl-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea03-impl-reviewer` 续任，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 起草、范围冻结/UNFREEZE、实现、r1 返修"
reviewer_independent: true
reviewed_by_implementer: false
author: "codex（实现交付）+ dsh（r1 返修 commit 13f907922）"
base_commit: 7a31c331e
reviewed_head: 13f907922
reviewed_head_full: 13f907922ffab6b885cac95c7dbae57e8977cffc
repository_under_review: "G:/CODEX/New Manga.workspace/FEA-03（branch feat/fea-03，只读审查）"
main_head_at_review: 8c40fe011
date: 2026-11-02
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 4
p2_count: 11
---

# Review：FEA-03 实现复核 r2（base `7a31c331e` / reviewed_head `13f907922`）

**结论：`changes_requested`（P0 × 0 / P1 × 4 / P2 × 11）。**

r1 的 5 条 P1 中，**R-03 已修复**；**R-01、R-02、R-05 只修复了一部分/行为仍不满足**；**R-04 未动**（与 Lead 说明一致）。因此不满足 `approved` 条件。

本报告只对 `13f907922` 有效，不构成集成批准、不构成 Task done、不构成 Gate 关闭。审查者未参与实现与返修；只读被审 head，测试产物写 `%TEMP%`，未 commit/push。

**r2 范围界定**：`git diff 7a31c331e..13f907922` 仅 2 个源文件（`drafts.py` +21/−4，`draft_journal.py` +2/−0），**无测试、无 evidence、无 Handoff 变更**；因此 r1 的 P2 文档/证据项全部保持原状。

---

## 0. 复核对象、方法与环境

| 项 | 值 |
|---|---|
| 实现 worktree | `G:\CODEX\New Manga.workspace\FEA-03`（branch `feat/fea-03`，HEAD `13f907922`，工作区 clean） |
| 被审 diff | `git diff --stat 7a31c331e..13f907922` → 2 files changed, 20 insertions(+), 7 deletions(-) |
| 被审 commit | `13f907922 fix(fea-03): 处置实现复核 r1（P0=0 / P1×5）`（作者/提交者同一账号；2026-11-02 01:04:39 +0800） |
| 环境 | Windows；CPython 3.14.6；pytest 9.1.1；.NET SDK 10.0.401；`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`；dotnet artifacts 指到 `%TEMP%` |
| 重跑范围 | 全量 `tests/core + tests/domain + tests/editing + tests/infrastructure`；`dotnet test`；`crash_probes.py`；`component_sqlite_smoke.py`；针对 r1 各 P1 的最小复现脚本 |
| 未执行 | 未重跑 pins（本 head 仅改 2 个 `src/` 文件，冻结面字节未动；r1 已 15/15 PASS）；未做真实 OS ACL（V22）；未审 Host/IPC（未接线） |

---

## 1. r1 findings 逐项 disposition

| r1 ID | r1 级别 | r2 状态 | 核验结论与证据 |
|---|---|---|---|
| **R-01** token 序号/幂等 | P1 | **open（部分修复，仍不满足）** | 只改了 `drafts.py:410`（`draft.draft_sequence < edit_token.draft_sequence` 才拒绝）。但 `:421` 仍要求 candidate 的 `draft_sequence == token.draft_sequence`：`open()`（token seq 0）→ `patch()`（draft seq 1）→ `prepare_candidate()`（candidate seq 1）→ `apply_candidates(open_token, [candidate])` 仍抛 **`DRAFT_CANDIDATE_INVALID candidate sequence differs from token`**（复现）。若 candidate 在 patch 前准备（candidate seq 0）则该 apply 能成功，但 receipt 按 `draft.draft_sequence`（1）写入（`:495`）而重放按 `token.draft_sequence`（0）查找（`:381-383`），同 token 重放 → **`DRAFT_CANDIDATE_NOT_FOUND`**；重启后重放旧 token → **`EDIT_TOKEN_INVALID`**，新 token → **`EDIT_TOKEN_REUSED`**（均复现，详见 §2）。 |
| **R-02** 崩溃残留 `.lock` 回收 | P1 | **open（部分修复）** | `import shutil` 已补（`:10`），NameError 消失；死 PID 且仍有句柄（`OpenProcess` 成功 + `GetExitCodeProcess`≠259）时回收成功（复现 available=True）。**但 `_process_is_alive` 未改**：`:35-38` 仍是 `if not handle: return True`（注释“Unknown owner (permissions): be conservative and treat it as alive”）。常见崩溃（无残留句柄）下 `OpenProcess` 失败 → 被判活 → 不回收：`os._exit` 后重启，`journal.available=False`、`startup_error=DRAFT_JOURNAL_LOCKED`，写 journal 抛 `DRAFT_JOURNAL_UNWRITABLE`，`.lock` 永久残留（复现）。**commit message 声称“`_process_is_alive` 对死 PID 返回 False”与代码不符**（diff 中无该改动）。 |
| **R-03** 同进程 close→reopen 锁重建 | P1 | **closed（已修复）** | `close()` 归零后 `_SHARED_LOCKS.pop(key, None)`（`draft_journal.py:161-167`）。复现：`j1.close()` → 磁盘 `.lock` 不存在 → 新 `DraftJournal` → `.lock exists on disk: True` → 子进程 `LOCK` 探针 **exit 73**（此前为 0）。修复有效；但**未补回归测试**（见 R-16）。 |
| **R-04** AC6/V13、AC11/V19 | P1 | **open（未动）** | 本 head 无测试/实现/evidence 变更。确认：V13 无测试、`prepare_candidate(` 在生产 `src/**` 仍无调用点；V19 的旧→新（刷新/未刷新）、新→旧组合仍无测试；V18 旧路径回归有既有测试（`test_draft_protection.py:98-103` + `tests/core` 通过），但不等价于 V19。**可由已实现机制部分满足**：candidate registry 已支持 `origin="machine"`（`drafts.py:302-367`，四字段在 `:349-354`），可作为 V13 的最小验证入口；V19 可用既有 `core.editing.save_manual_translation`（旧路径）+ drafts prepare/apply（新路径）编写，无需新生产接线。因此本项仍为 **r2 P1**，最小补测建议见 §3。 |
| **R-05** 孤儿 discarded 草稿假冲突 | P1 | **open（部分修复）** | `discard_orphans` 已改为：`delete_receipts` + `delete_draft` + 释放 owner/target/candidates/tokens，保留 `_drafts` 的 `discarded` 状态（`drafts.py:257-282`）。但 `_detect_text_conflict`（`:683-699`）仍遍历 `self._drafts.values()` 且**不过滤 `DISCARDED`**：复现 orphan discard 后新 Session 对同 page target 的 `patch_draft` 仍抛 **`DRAFT_TEXT_CONFLICT`**（原症状未消除）。另发现新问题 R-15（cleanup 无条件 `_owners.pop` 会剥夺 transfer 后的新 owner）。 |
| **R-06** V10 单元级异常注入 | P2 | **open** | 无测试改动；仍只有真实子进程三阶段（`tests/infrastructure/test_draft_journal.py:53-74`）。 |
| **R-07** V9/V21 precedence、V14/V15/V20/V22 分支 | P2 | **open** | 无测试改动；V9/V21 的“过期先于 receipt”测试仍未先产生 receipt；V14 独立连接不可见、V15 apply 路径 3×3、V20 current-mismatch、V22 OS ACL 仍未断言。 |
| **R-08** `git diff --check` 证据失真 | P2 | **open** | 本 head 上 `git diff --check b83bc7703..13f907922` 仍 **EXIT=2**：`src/infrastructure/filesystem/draft_journal.py:421: new blank line at EOF.`（仅核对 r2 区间 `7a31c331e..13f907922` 时 exit 0，说明旧问题未修）。`test-commands.md:18` 未更新。 |
| **R-09** Handoff/summary/证据落后于交付 head | P2 | **open** | 本 head 无 doc/verification 变更：`doc/handoffs/FEA-03-b83bc7703.md:6,14,81` 仍写 `delivery_head:null`/`b83bc7703 未提交`；`summary.md:3` 同；`v-matrix.md` 未更新；且 commit message 的 R-02 声明与代码不符（见 R-02），证据链需在集成前修正。 |
| **R-10** ports.py 删除既有契约 docstring | P2 | **open** | 未改；`src/application/editing/ports.py:106` 仍只剩一行 docstring。 |
| **R-11** 代码卫生 | P2 | **open** | 未改：`draft_journal.py:92-95` 重复赋值、`:5` 未用 `errno`、`:421` 文件尾空行；`drafts.py:521-542` 两个 except 分支仍重复清 intent。 |
| **R-12** C# conflicted 语义/dispose 竞态 | P2 | **open** | `DraftBuffer.cs` 未改（仍 `:69` 无条件置 Active；`DisposeAsync` 取消/竞态未处理）。 |
| **R-13** 生产关闭未接 `CoreServices.close()` | P2 | **open** | 未改；`app.py:182,445`、`core_service.py:5822` 仍 `conn.close()`（越出本卡写域，需 FEA-04/集成接线）。 |
| **R-14** intent 恢复错误包装/启动策略 | P2 | **open** | `drafts.py:675-681` 未改，仍把具体 cause 统一为 `DRAFT_JOURNAL_UNWRITABLE` 并在构造期抛出。 |

**新增（r2）**：

| r2 ID | 级别 | 位置 | 问题 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R-15** | P2 | `drafts.py:272-274`（`discard_orphans`） | cleanup 无条件 `self._owners.pop(target, None)`：若 target 已 `transfer_owner` 给活跃 Session B，而旧 Session A 的草稿仍在 `_drafts`，`discard_orphans({"sB"})` 会把 B 的 owner 记录删掉 → B 后续 patch 被误判 `DRAFT_READ_ONLY`。 | 生产装配复现：A open/patch → transfer A→B → B open（can_edit=True）→ `discard_orphans({"sB"})` 丢弃 A → B `patch_draft` 抛 `DRAFT_READ_ONLY`。 | 仅当 `self._owners.get(target) == draft.session_id` 时 pop owner；`target_by_session` 同理。 | open |
| **R-16** | P2 | `tests/`（本 head 无变更） | r2 的 R-01/R-02/R-03/R-05 修复**无回归测试**；1050 passed 是因为既有测试未覆盖这些失败路径（r1 已指出测试缺口），不能作为修复证据。 | `git diff --name-only 7a31c331e..13f907922 -- tests/` 为空。 | 至少补 4 个测试：open→patch→prepare→apply（open token）+ 同 token replay；死 PID 无句柄 crash→restart 可写；close→reopen 后 `.lock` 存在且第二进程 73；orphan discard 后新 Session patch 成功。 | open |

---

## 2. 关键复现记录（均为生产 `assemble_production_core` 或真实 `DraftJournal`，脚本在 `%TEMP%`）

### R-01（open→patch→apply 与幂等）

```text
# 场景 A：edit-open token（seq 0）→ patch（draft seq 1）→ prepare（candidate seq 1）→ apply
open token seq: 0
draft seq after patch: 1
APPLY RAISED: DraftError DRAFT_CANDIDATE_INVALID candidate sequence differs from token

# 场景 B：candidate 在 patch 前准备（seq 0）→ patch（draft seq 1）→ apply(open token)
apply with token seq 0 draft seq 1 -> {'<region>': '<rev>'}
receipt at token seq present: False
receipt at draft seq present: True
SAME-TOKEN REPLAY RAISED: DraftError DRAFT_CANDIDATE_NOT_FOUND candidate registry entry is missing
# 重启后：
restart replay with old token RAISED: DraftError EDIT_TOKEN_INVALID edit token is unknown to this Core session
restart replay with new token RAISED: DraftError EDIT_TOKEN_REUSED receipt replay token does not match
```

结论：`<` 放宽只解除了 `:410` 一处误拒；`:421` 的 candidate 序列相等校验、receipt 写入键（draft seq，`:495`）与重放查找键（token seq，`:381-383`）不一致，使得“open→patch→apply”与“同 token 幂等/跨重启幂等”仍不成立。

### R-02（崩溃后重启可写性）

```text
# 无残留句柄的死 PID（正常模拟“进程崩溃后 OS 已回收句柄”）：
stale lock exists before restart: True
second core assembled; journal.available: False startup_error: DRAFT_JOURNAL_LOCKED
journal write after crash-restart RAISED: DraftJournalError DRAFT_JOURNAL_UNWRITABLE draft journal is not writable
lock remains: True

# 死 PID 且仍有句柄（手工 Popen 保留 handle；OpenProcess 成功）：
stale lock (handle kept): available = True lock exists after True   # 回收成功（import shutil 修复生效）

# 手工死 PID 无句柄：
stale lock (no handle): available = False lock exists after True    # 仍不回收
```

### R-03（close→reopen 锁）

```text
j1 available True lock exists True
after close lock exists False
j2 available True lock exists on disk True
subprocess LOCK exit (expect 73): 73
```

### R-05 / R-15（孤儿与 owner）

```text
discarded: ['<draft>']
journal exists after discard: False
discarded draft query status: discarded
new draft can_edit: True
new session patch RAISED: DraftError DRAFT_TEXT_CONFLICT text changes conflict across Sessions

# R-15：transfer 后 orphan cleanup 剥夺新 owner
after transfer, B can_edit: True
discarded: ['<draft-A>']
B patch after orphan cleanup RAISED: DraftError DRAFT_READ_ONLY Session no longer owns this draft
```

### R-04（覆盖确认）

```text
grep prepare_candidate( src/**  → 仅 drafts.py:302 定义，无生产调用点
git diff --name-only 7a31c331e..13f907922 -- tests/ → 空
v-matrix.md V13/V19 仍为 NOT_RUN（本 head 未改）
```

**最小补测建议（不新增生产接线）**：
- **V13**：在 production assembly 上打开某 Region 的活跃草稿 → `prepare_candidate(region, patch, origin="machine")` → 断言 candidate 四字段、`current_revision_id`/revision count 不变；再 apply 断言只有 1 个新 revision。若 DSH 认为 pipeline 写回接线属 FEA-04，则应在卡中登记 deferral 并把矩阵/Task 同步。
- **V19**：①旧路径 `save_manual_translation` 写一次 → 刷新 base（读 current）→ 新路径 prepare/apply → 断言 2 revisions；②旧路径写一次 → 不刷新 base → 新路径 apply → 断言 `STALE_BASE_REVISION` 且仍 1 revision；③新路径 apply → 旧路径 `save_manual_translation` → 断言 2 revisions（旧 append）。

---

## 3. 回归验证（本 head，EXIT 均为 0，worktree 保持 clean）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 全量 Python 回归 | `python -m pytest tests/core tests/domain tests/editing tests/infrastructure -q -p no:cacheprovider` | **PASS**：`1050 passed, 1 warning in 87.63s`（基线 885 + 新增 165），EXIT=0 | job output |
| BRIDGE dotnet | `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --artifacts-path %TEMP%\fea03-r2-dotnet` | **PASS**：通过 31 / 失败 0 / 跳过 0，EXIT=0 | job output |
| 崩溃/锁探针 | `python verification/FEA-03/crash_probes.py` | **PASS**：A/B/C + LOCK(73/0)，EXIT=0 | 命令输出 |
| 组件 SQLite smoke | `python verification/FEA-03/component_sqlite_smoke.py` | **PASS**：5 项 JSON 全 PASS，EXIT=0 | 命令输出 |
| 范围检查 | `git diff --stat/--name-only 7a31c331e..13f907922` | **PASS**：仅 `drafts.py`、`draft_journal.py`；`tests/doc/verification/apps` 无变更 | 命令输出 |
| whitespace | `git diff --check b83bc7703..13f907922` | **FAIL**：EXIT=2，`draft_journal.py:421 new blank line at EOF`（R-08 未修） | 命令输出 |
| pins | 本 head 未触冻结面（仅 2 个 `src/` 文件）；r1 已 `PIN AUDIT PASS (all 15)` | N/A（未重跑） | — |
| OS ACL（V22） | — | **NOT_RUN**（环境/权限未做真实 ACL；仅复核测试源） | — |

**结论**：回归数字与 DSH 侧 1050 passed 一致，dotnet 31 passed；但这些测试**不覆盖** r2 修复涉及的失败路径（R-01/R-02/R-05 复现均在此套件外），因此测试通过不能作为 r2 修复验收证据。

---

## 4. 结论与复审要求

- **P0 = 0 / P1 = 4 / P2 = 11 → `changes_requested`**。
- 放行条件（最小返修清单）：
  1. **R-01**：统一 token 语义——明确 token 的 `DraftSequence` 是“edit-open 序列”还是“提交序列”；同步修正 `:421` candidate 序列校验、`:381-383` receipt 查找键、`:448/:495` intent/receipt 写入键，使 open→patch→prepare→apply 与同 token/跨重启 replay 同时成立；补 §2 的测试。
  2. **R-02**：`_process_is_alive` 用 `GetLastError()` 区分 `ERROR_INVALID_PARAMETER`（死 PID → False）与 `ERROR_ACCESS_DENIED`（→ True），或改 pid+创建时间/独占文件锁；补“死 PID 无句柄→重启可写”测试；同步修正 commit message 与 Handoff 的不实声明。
  3. **R-05**：`_detect_text_conflict` 跳过 `DISCARDED`/无活跃 Session 草稿；`discard_orphans` 仅在 owner 等于该草稿 Session 时 pop；补“orphan discard→新 Session 同页可编辑”与“transfer 后 cleanup 不夺 owner”测试。
  4. **R-04**：按 §2 最小补测 V13/V19，或由 DSH 明确 deferral 并更新冻结矩阵/Handoff；本项维持 P1。
  5. **P2 收口**：R-08（删除文件尾空行并重跑证据）、R-09（Handoff/summary/v-matrix 更新到交付 head 并如实记录 r2 修复范围）、R-10（恢复 ports docstring）、R-11（卫生）、R-12（C#）、R-13（生产 close 接线/FEA-04）、R-14（错误码/启动策略）、R-06/R-07（补测试/修订矩阵）、R-15（owner pop）、R-16（r2 回归测试）。
- **边界声明**：本报告只审 `13f907922` 的实现交付，**不构成集成批准、不构成 Task done、不构成 Gate 关闭**；r1 报告保持历史记录；head 若再变化需对新 fixed head 重审。审查者 `fea03-impl-reviewer` 未参与实现/返修，未 commit/push；本报告写于主仓库工作区 `doc/reviews/FEA-03-r2.md`（未提交）。
