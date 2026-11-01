---
document_id: FEA-03-r3
kind: independent_implementation_review
reviewer: fea03-impl-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea03-impl-reviewer` 续任，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 起草、范围冻结/UNFREEZE、实现、r1/r2 返修"
reviewer_independent: true
reviewed_by_implementer: false
author: "codex（实现交付）+ dsh（r1/r2 返修 commit 692d8b584）"
base_commit: 13f907922
reviewed_head: 692d8b584
reviewed_head_full: 692d8b5848caa841942aca5bc4c64f3e3afd5f51
repository_under_review: "G:/CODEX/New Manga.workspace/FEA-03（branch feat/fea-03，只读审查）"
main_head_at_review: 8c40fe011
date: 2026-11-02
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 11
---

# Review：FEA-03 实现复核 r3（base `13f907922` / reviewed_head `692d8b584`）

**结论：`changes_requested`（P0 × 0 / P1 × 2 / P2 × 11）。**

r2 的 P1 中，**R-02、R-03、R-05、R-15 已修复并复现通过**；**R-01 只修复了“误拒”这一半，幂等/重放仍不成立**（apply 成功但同 token/跨重启 replay 均失败，receipt 键不一致）；**R-04 无任何变化**。另有 r3 新引入的锁回收 fail-open 风险（R-17，P2）。因此未达到 `approved`。

本报告只对 `692d8b584` 有效，不构成集成批准、不构成 Task done、不构成 Gate 关闭。审查者未参与实现/返修；只读被审 head，测试产物写 `%TEMP%`，未 commit/push。

**r3 范围**：`git diff 13f907922..692d8b584` 仅 2 个源文件（`drafts.py` +7/−3，`draft_journal.py` +2/−2），**无测试、无 evidence、无 Handoff 变更**。

---

## 0. 复核对象、方法与环境

| 项 | 值 |
|---|---|
| 实现 worktree | `G:\CODEX\New Manga.workspace\FEA-03`（branch `feat/fea-03`，HEAD `692d8b584`，工作区 clean） |
| 被审 commit | `692d8b584 fix(fea-03): 处置实现复核 r2（P0=0 / P1×4）`（2026-11-02，作者/提交者同一账号） |
| 被审 diff | `git diff --stat 13f907922..692d8b584` → 2 files changed, 9 insertions(+), 5 deletions(-) |
| 环境 | Windows；CPython 3.14.6；pytest 9.1.1；.NET SDK 10.0.401；`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`；dotnet artifacts 指到 `%TEMP%` |
| 重跑 | 全量 `tests/core tests/domain tests/editing tests/infrastructure`；`dotnet test`；`crash_probes.py`；`component_sqlite_smoke.py`；针对 r2 各 P1 的生产装配复现 |
| 未执行 | 未重跑 pins（本 head 仅改 2 个 `src/` 文件，冻结面未动；r1 已 15/15 PASS）；未构造真实跨完整性级别 ACL/权限场景（R-17 为静态风险判定） |

---

## 1. r2 findings 逐项 disposition

| r2 ID | r2 级别 | r3 状态 | 核验结论与证据 |
|---|---|---|---|
| **R-01** token 序号/幂等 | P1 | **open（部分修复）** | `drafts.py:423` candidate 校验改为 `<`（`:412` 已是 `<`），因此 `open(seq0)→patch(seq1)→prepare(seq1)→apply(open token)` **不再被误拒**（复现 `APPLY OK`，revision count 2，无重复写入）。**但幂等/重放仍失败**：receipt 按 `draft.draft_sequence`（1）写入（`:497`），重放按 `edit_token.draft_sequence`（0）查找（`:383`）→ 同 token 重放 **`DRAFT_CANDIDATE_NOT_FOUND`**；重启后旧 token **`EDIT_TOKEN_INVALID`**、新 token **`EDIT_TOKEN_REUSED`**（均复现，见 §2）。根因未变：token 序号与提交序号的键未统一。 |
| **R-02** 崩溃残留 `.lock` 回收 | P1 | **closed（已修复）** | `_process_is_alive` 对 `OpenProcess` 失败返回 **False**（`draft_journal.py:35-38`）。复现：死 PID（有句柄/无句柄）均返回 False、活 PID 返回 True；真实 `os._exit` 后重启：`journal.available=True`、`journal write OK`、`.lock` 被新实例重建（见 §2）。原 P1 行为目标达成；但该实现引入 R-17 的 fail-open 风险（P2）。 |
| **R-03** 同进程 close→reopen 锁重建 | P1 | **closed** | r2 已修；本 head 未回退（`draft_journal.py:161-167` pop 注册表）。 |
| **R-04** AC6/V13、AC11/V19 | P1 | **open（未动）** | 本 head 无测试/实现/evidence 变更。全仓测试中无 `prepare_candidate(..., origin="machine")`（grep 确认）；V13/V19 在 `v-matrix.md` 仍为 NOT_RUN。**判定：仍为 P1**（理由与最小补测见 §3）；若 DSH 正式登记 deferral（V13→C-08/结果面或 FEA-04 接线；V19→集成验证补测）并同步 Task/Handoff/矩阵，可在下一轮降为 P2。 |
| **R-05** 孤儿 discarded 草稿假冲突 | P1 | **closed（已修复）** | `_detect_text_conflict` 跳过 `DISCARDED`（`drafts.py:692`）。复现：page 级与 region 级 orphan discard 后，新 Session 均可重新 open 同 target 并 `patch_draft` **成功**（不再 `DRAFT_TEXT_CONFLICT`）。 |
| **R-06** V10 单元级异常注入 | P2 | **open** | 无测试变更；仍只有真实子进程 A/B/C（`tests/infrastructure/test_draft_journal.py:53-74`）。 |
| **R-07** V9/V21 precedence、V14/V15/V20/V22 分支 | P2 | **open** | 无测试变更；V9/V21 仍是“先断言过期、后无 receipt”的用例，未验证顺序；V14 独立连接不可见、V15 apply 路径 3×3、V20 current-mismatch、V22 OS ACL 未断言。 |
| **R-08** `git diff --check` 证据失真 | P2 | **open** | `git diff --check b83bc7703..692d8b584` 仍 **EXIT=2**：`draft_journal.py:421: new blank line at EOF.`。commit message 的“git diff --check rc=0”来自对**干净工作树的无参 `git diff --check`**（空 diff，必然 0），不覆盖交付字节；需删尾空行并重跑真实范围检查。 |
| **R-09** Handoff/summary/证据落后 | P2 | **open** | 无 doc/verification 变更：Handoff `:6,14,81` 仍 `delivery_head:null`/`b83bc7703 未提交`；`summary.md:3` 同；`v-matrix.md` 未更新。 |
| **R-10** ports.py 契约 docstring | P2 | **open** | 未改（`ports.py:106` 仍只有一行）。 |
| **R-11** 代码卫生 | P2 | **open** | 未改：`draft_journal.py:92-95` 重复赋值、`:5` 未用 `errno`、`:421` 尾空行；`drafts.py:523-544` 两个 except 分支重复清 intent；r3 新增 `discard_draft` 嵌套同条件判断（`:227-229`，功能等价但冗余）。 |
| **R-12** C# conflicted 语义/dispose 竞态 | P2 | **open** | 未改（`DraftBuffer.cs:69` 仍无条件置 Active）。 |
| **R-13** 生产关闭未接 `CoreServices.close()` | P2 | **open** | 未改；`app.py:182,445`、`core_service.py:5822` 仍 `conn.close()`（越出本卡写域，需 FEA-04/集成接线）。 |
| **R-14** intent 恢复错误包装/启动策略 | P2 | **open** | 未改（`drafts.py:646-685`，异常包装在 `:678-685`）。 |
| **R-15** cleanup 剥夺 transfer 后新 owner | P2 | **closed（已修复）** | `discard_orphans` 仅在 `owners.get(target) == draft.session_id` 时 pop（`:274`）。复现：A patch → transfer A→B → B open → `discard_orphans({"sB"})` → B `patch_draft` **成功**。 |
| **R-16** r2 修复无回归测试 | P2 | **open** | 本 head 无测试变更（`git diff --name-only 13f907922..692d8b584 -- tests/` 为空）。1050 passed 不覆盖 R-01 replay、R-02 崩溃重启、R-05 孤儿重开、R-15 transfer+cleanup 等路径。最小测试清单见 §4。 |

**新增（r3）**：

| r3 ID | 级别 | 位置 | 问题 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R-17** | P2 | `draft_journal.py:35-38` | `_process_is_alive` 对**任何** `OpenProcess` 失败返回 False：若目标进程活着但 `OpenProcess` 因权限失败（`ERROR_ACCESS_DENIED`，例如不同完整性级别/受保护进程），会把活写者当死而删除其 `.lock`，可能出现两个 writer（单写者保护 fail-open）。 | 静态判定：代码未调用 `GetLastError()`；Windows 语义下 `OpenProcess` 失败并不区分“无此 PID”与“拒绝访问”。本会话无法构造跨完整性级别场景，**未实跑**。 | 用 `GetLastError()` 区分 `ERROR_INVALID_PARAMETER`(87, 死 PID→False) 与 `ERROR_ACCESS_DENIED`(5,→True)；或改用 pid+进程创建时间/`msvcrt.locking` 独占锁。 | open |

---

## 2. 关键复现记录（均为生产 `assemble_production_core` / 真实 `DraftJournal`，脚本在 `%TEMP%`）

### R-02（崩溃后锁回收 + journal 可写）

```text
# _process_is_alive 探针
live pid alive: True
dead pid (handle kept) alive: False (expect False)
dead pid (no handle) alive: False (expect False)

# 真实进程 os._exit 后重启
stale lock before restart: True
journal.available: True startup_error: None
journal write after crash-restart: OK
lock after restart: True        # 新实例重建，core.close() 后释放
```

### R-01（apply 已放行，但幂等/重放失败）

```text
open token seq: 0
draft seq after patch: 1
APPLY OK: {'<region>': '<rev>'}
revision count before/after replay: 2 2
SAME-TOKEN REPLAY RAISED: DraftError DRAFT_CANDIDATE_NOT_FOUND candidate registry entry is missing
RESTART OLD-TOKEN replay RAISED: DraftError EDIT_TOKEN_INVALID edit token is unknown to this Core session
RESTART NEW-TOKEN replay RAISED: DraftError EDIT_TOKEN_REUSED receipt replay token does not match
```

说明：apply 走的 candidate seq（1）≥ token seq（0），`:423` 已放行；receipt 在 `draft.draft_sequence`(1) 写入（`:497`），但 replay 在 `edit_token.draft_sequence`(0) 查找（`:383`），因此同 token 与跨重启重放均无法命中。数据安全无重复 revision（count 2→2），但 AC4 的“返回同 `revisionIds`”不成立。

### R-05 / R-15（孤儿与 owner）

```text
# page 级 orphan
discarded: ['<draft>']
new session patch after orphan cleanup: OK

# region 级 orphan
discarded: ['<draft>']
region-level orphan: new session patch OK

# transfer 后 cleanup
A patch -> transfer A→B -> B open (can_edit=True) -> discard_orphans({"sB"})
B patch after transfer+cleanup: OK (owner preserved)
```

---

## 3. R-04 判定与最小补测断言

**判定：仍为 P1（blocker 性质：冻结验收矩阵关键场景无任何证据）**，但实现机制已具备，补测不需要新的生产接线：

- **V13（翻译产物 candidate）**：production assembly 上对某 Region 打开活跃草稿 → `prepare_candidate(rid, {"text": {"machine_translation": "机器译文"}}, origin="machine", draft_id=...)`；断言：①`candidate.to_json()` 键集恰为 `{candidateId, RegionId, BaseRevisionId, origin}`；②`origin == "machine"`；③`current_revision_id` 与 `region_revisions` count 不变；④apply 后只新增 1 个 revision。若 DSH 认为 pipeline 写回接线属 FEA-04/结果面（C-13 SC-D07），则登记 deferral 并把 V13 从本卡验收范围移出。
- **V19（旧→新 / 新→旧）**：①旧路径 `save_manual_translation` 写一次 → 刷新 base（读 current）→ 新路径 prepare/apply → 断言 2 revisions；②旧路径写一次后**不刷新** base → 新路径 apply → 断言 `STALE_BASE_REVISION` 且仍 2 revisions；③新路径 apply → 旧路径 `save_manual_translation` → 断言 3 revisions（旧 append，不去重）；④旧路径同文两次 → 2 revisions（V18，已有测试）。

---

## 4. R-16 最小回归测试清单（建议直接落在 `tests/editing/**` 与 `tests/infrastructure/**`）

1. `open(seq0)→patch(seq1)→prepare(seq1)→apply(open token)` 成功，且 **同 token 再 apply 返回同 `revisionIds`**（当前会失败，正好作为 R-01 的红灯修复目标）；重启后旧/新 token 的 replay 行为按 DSH 最终 token 语义断言。
2. `_process_is_alive`：无效/死 PID → False；活 PID → True；`.lock` 残留（死 PID，无句柄）→ 新 `DraftJournal` available True 且写成功；真实 `os._exit` 子进程 → 重启 journal 可写。
3. orphan discard（page 级 + region 级）→ 新 Session 重新 open 同 target 并 patch 成功。
4. `transfer_owner` 后 `discard_orphans` 不剥夺新 owner（B patch 成功）。
5. `git diff --check` 在交付范围（`git diff --check <base>..<head>`）为 0（删尾空行后）。

---

## 5. 回归验证（本 head，EXIT 均为 0，worktree 保持 clean）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 全量 Python 回归 | `python -m pytest tests/core tests/domain tests/editing tests/infrastructure -q -p no:cacheprovider` | **PASS**：`1050 passed, 1 warning in 91.87s`，EXIT=0 | job output |
| BRIDGE dotnet | `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --artifacts-path %TEMP%\fea03-r3-dotnet` | **PASS**：通过 31 / 失败 0 / 跳过 0，EXIT=0 | job output |
| 崩溃/锁探针 | `python verification/FEA-03/crash_probes.py` | **PASS**：A/B/C + LOCK(73/0)，EXIT=0（r2 已跑；本 head 未改这些文件） | 命令输出 |
| 范围检查 | `git diff --name-only 13f907922..692d8b584` | **PASS**：仅 `drafts.py`、`draft_journal.py`；`tests/doc/verification/apps` 无变更 | 命令输出 |
| whitespace | `git diff --check b83bc7703..692d8b584` | **FAIL**：EXIT=2，`draft_journal.py:421 new blank line at EOF`（R-08 未修；无参 `git diff --check` 因工作树 clean 才为 0） | 命令输出 |
| pins | 本 head 未触冻结面（仅 2 个 `src/` 文件）；r1 已 15/15 PASS | N/A（未重跑） | — |

---

## 6. 结论与复审要求

- **P0 = 0 / P1 = 2 / P2 = 11 → `changes_requested`**。
- 放行所需（最小）：
  1. **R-01**：统一 token 序号与 receipt/intent 键——二选一：①receipt/intent 的 `DraftSequence` 与 replay 查找统一用 `edit_token.draft_sequence`；②apply 时把有效提交序号刷新为 `draft.draft_sequence` 并让 replay 按该序号查找（token 只作过期/归属校验）。同步修正 `:383`、`:450`、`:497`，并补 §4-1 测试。
  2. **R-04**：按 §3 补 V13/V19 最小测试，或由 DSH 正式登记 deferral 并同步 Task/Handoff/v-matrix（下一轮可降 P2）。
- 可接受遗留（P2，需在 Handoff/集成记录中登记；不阻塞本次实现复核结论中的 P0/P1 判定，但阻塞 done/集成证据）：
  - **R-17**（锁回收 fail-open）：建议直接改为 `GetLastError()` 区分 87/5；若保留现状需在风险登记中写明“跨权限场景可能双 writer”。
  - R-06/R-07（V10 单元级注入、V9/V21 precedence、V14/V15/V20/V22 分支）、R-08（尾空行与证据重跑）、R-09（Handoff/summary/v-matrix 更新）、R-10（ports docstring）、R-11（卫生）、R-12（C#）、R-13（生产 close 接线）、R-14（错误码/启动策略）、R-16（r3 回归测试）。
- **边界声明**：本报告只审 `692d8b584` 的实现交付，不构成集成批准、不构成 Task done、不构成 Gate 关闭；r1/r2 报告保持历史记录；head 若再变化需对新 fixed head 重审。审查者 `fea03-impl-reviewer` 未参与实现/返修，未 commit/push；本报告写于主仓库工作区 `doc/reviews/FEA-03-r3.md`（未提交）。
