---
document_id: FEA-03-r5
kind: independent_implementation_review
reviewer: fea03-impl-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea03-impl-reviewer` 续任，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 起草、范围冻结/UNFREEZE、实现、r1–r4 返修"
reviewer_independent: true
reviewed_by_implementer: false
author: "codex（实现交付）+ dsh（r1–r4 返修 commit 1db802f8b；Task 卡 deferral 在主仓库工作区未提交）"
base_commit: 8875e74ef
reviewed_head: 1db802f8b
reviewed_head_full: 1db802f8b7af436433456e546798047e4b04953d
repository_under_review: "G:/CODEX/New Manga.workspace/FEA-03（branch feat/fea-03，只读审查）"
main_head_at_review: 8c40fe011
date: 2026-11-02
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 13
---

# Review：FEA-03 实现复核 r5（base `8875e74ef` / reviewed_head `1db802f8b`）

**结论：`approved`（P0 × 0 / P1 × 0 / P2 × 13）。**

r4 的唯一 P1（R-01 receipt 幂等键）已闭环：receipt 写入与查找统一为 **draft 序号**（draft 缺失回退 token 序号），复现 (a) apply 成功、(b) 同 token 重放同 `revisionIds`、(c) 重启后同 token 重放命中 receipt、(d) 新 token 重放已进入 receipt 分支（错误提示为 receipt token 不匹配，**不再是 `DRAFT_CANDIDATE_NOT_FOUND`**）、(e) 新 token + 等价 candidate 不再产生重复 revision（count 稳定）。剩余均为 P2（语义边界、测试补强、证据 hygiene），按 Review 模板 P0/P1=0 时 `approved`。

**本 `approved` 的边界**：只对 `1db802f8b` 的实现交付有效；不构成集成批准、不构成 Task done、不构成 Gate 关闭。P2 中 R-08/R-18（`git diff --check`、v-matrix/Task 卡 canonical 化、Handoff 更新）建议在 DSH 集成前收口；R-19 是 AC4 语义边界，需 DSH 明确口径（若要求“任何同 `(DraftId,DraftSequence)` token 都必须返回同 `revisionIds`”，则 R-19 升级为 P1 并需再修）。

审查者未参与实现/返修；只读被审 head，测试产物写 `%TEMP%`，未 commit/push。主仓库工作区新增本报告（未提交）。

---

## 0. 复核对象、方法与环境

| 项 | 值 |
|---|---|
| 实现 worktree | `G:\CODEX\New Manga.workspace\FEA-03`（branch `feat/fea-03`，HEAD `1db802f8b`，工作区 clean） |
| 被审 commit | `1db802f8b fix(fea-03): 处置实现复核 r4（R-01 receipt 键=draft 序号；补同 token 重放测试）` |
| 被审 diff | `git diff --stat 8875e74ef..1db802f8b` → 2 files changed, 37 insertions(+), 2 deletions(-)（`drafts.py`、`tests/editing/test_draft_protection.py`） |
| 环境 | Windows；CPython 3.14.6；pytest 9.1.1；.NET SDK 10.0.401；dotnet artifacts 指到 `%TEMP%` |
| 重跑 | 全量 `tests/core tests/domain tests/editing tests/infrastructure`；`dotnet test`；R-01 五分支 + 重复 revision 的生产装配复现 |
| 未执行 | 未重跑 pins（本 head 未触冻结面；r1 已 15/15 PASS）；R-17 跨完整性级别权限场景未实跑；V19 组合场景按 deferral 未跑 |

---

## 1. r4 findings 逐项 disposition

| r4 ID | r4 级别 | r5 状态 | 核验结论与证据 |
|---|---|---|---|
| **R-01** receipt 幂等键 | P1 | **closed（P1 关闭；语义边界降为 P2 R-19）** | 修复生效：`drafts.py:383-390` 按 `draft.draft_sequence` 查找 receipt（draft 缺失回退 token seq）、`:503` 写入同键。复现见 §2：(a) apply 成功；(b) 同 token 重放 **同 revisionIds**，count 2→2；(c) 重启后同 token 重放 **命中 receipt**；(d) 新 token 重放进入 receipt 分支并抛 `EDIT_TOKEN_REUSED`（`receipt replay token does not match`），**不再是 `DRAFT_CANDIDATE_NOT_FOUND`**；(e) 新 token + 等价 candidate 返回 receipt 的 `revisionIds`，**count 保持 2、无重复 revision**。残余为 tokenId 门与 replay 查找边界（R-19，P2）。 |
| **R-04** AC6/V13、AC11/V19 | P1 | **closed（P1 关闭）** | V19 deferral 已登记（主仓库工作区 `doc/tasks/FEA-03.md` + worktree `v-matrix.md`）；V13 已补 `test_machine_result_candidate_prepare_keeps_pointer`。实体处置可接受；断言完整性与证据 canonical 化见 R-18（P2）。 |
| **R-02** 崩溃锁回收 | P1 | **closed** | r3 已修并复现；本 head 未回退。 |
| **R-03** close→reopen 锁重建 | P1 | **closed** | r2 已修；本 head 未回退。 |
| **R-05** 孤儿假冲突 | P1 | **closed** | r3 已修；本 head 未回退。 |
| **R-06** V10 单元级异常注入 | P2 | **open（可接受遗留）** | 仍只有真实子进程 A/B/C；建议作为 FEA-04/集成回归补测项登记。 |
| **R-07** V9/V21 precedence、V14/V15/V20/V22 分支 | P2 | **open（可接受遗留）** | 无测试变更；矩阵不得把这些分支标 PASS。 |
| **R-08** `git diff --check` | P2 | **open（可接受但建议集成前修）** | 本 head 交付范围 `git diff --check b83bc7703..1db802f8b` 仍 **EXIT=2**：`draft_journal.py:421` + `v-matrix.md:36` 两处 new blank line at EOF；r5 区间 `8875e74ef..1db802f8b` 为 0。Lead 期望的 0 未达到（见 §5）。 |
| **R-09** Handoff/summary 落后 | P2 | **open（可接受但建议集成前修）** | 无 doc 变更：Handoff `:6,14,81` 仍 `delivery_head:null`/`b83bc7703 未提交`；`summary.md:3` 同。 |
| **R-10** ports.py docstring | P2 | **open（可接受遗留）** | 未改（`ports.py:106`）。 |
| **R-11** 代码卫生 | P2 | **open（可接受遗留）** | `draft_journal.py:92-95`、`:5` 未用 `errno`；`drafts.py:529-550` 重复 except 清 intent；新测试文件无结尾换行、函数间 1 空行。 |
| **R-12** C# conflicted/dispose | P2 | **open（可接受遗留）** | 未改（`DraftBuffer.cs:69` 无条件 Active；`DisposeAsync` 取消/竞态未处理）。 |
| **R-13** 生产关闭接线 | P2 | **open（可接受遗留，归 FEA-04/集成）** | 未改（`app.py:182,445`、`core_service.py:5822` 仍 `conn.close()`）。 |
| **R-14** recovery 错误包装 | P2 | **open（可接受遗留）** | 未改（`drafts.py:652-691`，异常包装在 `:684-691`）。 |
| **R-15** cleanup 剥夺新 owner | P2 | **closed** | r3 已修；本 head 未回退。 |
| **R-16** 修复回归测试 | P2 | **open（部分：仅补 1 个测试）** | 新增 `test_same_token_replay_after_patch_returns_same_revisions`（`tests/editing/test_draft_protection.py:432-458`）覆盖 (b) 的同 token 重放；缺 (d)/(e)/(f)、跨重启新 token、重复 revision 断言、R-02/R-05 专项测试（清单见 §3）。 |
| **R-17** OpenProcess fail-open | P2 | **open（可接受遗留，建议修）** | `_process_is_alive`（`draft_journal.py:35-38`）对任何 OpenProcess 失败返回 False，未区分 `ERROR_ACCESS_DENIED`；建议 `GetLastError()` 区分 87/5。 |
| **R-18** V13 断言/证据 hygiene | P2 | **open（可接受但建议集成前修）** | V13 测试仍仅断言 `origin=="machine"` + pointer 不变；缺 candidate 四字段、revision count、活跃草稿场景；测试文件无结尾换行/单空行。`v-matrix.md:19,25` 仍 `NOT_RUN`；说明行含 TAB（`est_machine_...` 拼写错误，`:35`）；文件尾空行（`:36`）；Task 卡 deferral 在主仓库**未提交**。 |

**新增（r5）**：

| r5 ID | 级别 | 位置 | 问题 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R-19** | P2 | `drafts.py:383-403`（receipt 查找/重放分支）、`:500-511`（写 receipt） | **AC4 语义边界（非数据安全）**：①新 token（seq1）重放同一 draft 状态时，receipt 已命中但 `tokenId` 门使其抛 `EDIT_TOKEN_REUSED`，不返回 `revisionIds`；②**新观察**：commit（receipt seq1）后再 patch 到 seq2，再用旧 token 重放 → 查找用当前 draft seq2，receipt 未命中 → `DRAFT_CANDIDATE_NOT_FOUND`（r4 的 token-key 查找在该场景曾命中）。两者都不产生重复 revision，但“同 `(DraftId,DraftSequence)` 幂等返回”取决于 DraftSequence 口径。 | 见 §2 的 (d)、(f) 输出。 | 由 DSH 明确 AC4 的 DraftSequence 口径：若要求“同 `(DraftId,DraftSequence)` 任何 token 都返回同 `revisionIds`”，则放宽 receipt 分支的 tokenId 门（校验 draft/session 归属即可）并在查找失败时回退 token seq/按 tokenId 扫描本 draft receipts；补 (d)/(f) 测试。若维持 token 身份严格语义，则在卡/Handoff 写明并保留 NOT_RUN。 | open |

---

## 2. R-01 复现记录（生产 `assemble_production_core`，脚本在 `%TEMP%`）

```text
open token seq: 0
draft seq: 1
(a) apply open token OK: {'<region>': '<rev>'}
(b) same-token replay: {...} equal: True
revision count: 2 -> 2
receipt(seq0): False receipt(seq1): True          # receipt 按 draft 序号写入

new token seq: 1
(d) new-token replay RAISED: DraftError EDIT_TOKEN_REUSED receipt replay token does not match
    # 进入 receipt 分支（不再是 DRAFT_CANDIDATE_NOT_FOUND），但 tokenId 不同 → 拒绝返回

(e) new-token + equivalent candidate apply: {...}  # 返回 receipt 的 revisionIds
revision count after (e): 2
last two snapshots equal: False nos: 2 1          # 无重复 revision（r4 的 2→3 已消除）

(c) restart same-token replay: {...}               # 命中 receipt(seq1)
restart new token seq: 1
(d2) restart new-token replay RAISED: DraftError EDIT_TOKEN_REUSED receipt replay token does not match

# (f) 额外观察：commit 后再 patch 到 seq2，再重放旧 token
(f) replay old token after later patch RAISED: DraftError DRAFT_CANDIDATE_NOT_FOUND candidate registry entry is missing
```

**判读**：r4 P1 的两个具体缺陷（同 token 重放误拒/重复 revision）均已消除；剩余为 **tokenId 门/查找键口径**（R-19，P2）。若 DSH 的 AC4 口径是“同 `(DraftId,DraftSequence)`（含新 token）必须返回同 `revisionIds`”，则 R-19 需升 P1 并修复；若口径是“同 token 才做幂等重放、新 token 视为新提交键”，当前行为可接受但需在卡中明确。

---

## 3. R-16 测试覆盖评估与最小补测

新增 `test_same_token_replay_after_patch_returns_same_revisions` 覆盖：open→patch→prepare→apply→**同 token 再 apply（candidate 已失效时走 receipt 分支）** 返回同 `revisionIds`，17 个 editing 测试全过。**仍缺**：

1. (d) 新 token（seq1）重放：期望按 DSH 语义断言返回同 `revisionIds` 或 `EDIT_TOKEN_REUSED`（当前行为记录，红/绿取决于 R-19 口径）。
2. (e) 重复 revision 防护：成功 apply 后新 token + 等价 candidate 再 apply，断言 revision count 不变（r5 手工已验证 count=2）。
3. (c) 跨重启同 token 重放（现有 `test_receipt_intent_recovers...` 覆盖 receipt-write-crash 路径，建议补普通 restart replay）。
4. (f) commit 后再 patch 再 replay（当前 `DRAFT_CANDIDATE_NOT_FOUND`，随 R-19 口径决定期望）。
5. R-02：死 PID（无句柄）`.lock` → 新 journal available=True 且写成功；真实 `os._exit` 重启可写。
6. R-05/R-15：page/region 级 orphan discard → 新 Session 同 target 可编辑；transfer 后 cleanup 不夺 owner。
7. `_process_is_alive`：无效/死 PID=False、活 PID=True。

---

## 4. V13 / V19 与证据 hygiene

- **V13**：`test_machine_result_candidate_prepare_keeps_pointer`（`:415-431`）断言 `origin=="machine"`、pointer 不变。**仍 PARTIAL**：缺 ①candidate 四字段键集 `{candidateId,RegionId,BaseRevisionId,origin}`；②revision count 不变；③“翻译产物 vs **活跃草稿**”场景（当前未 open draft）；④测试末尾无换行、函数间仅 1 空行。最小补测：在现有测试中先 `open_draft`，prepare 后断言 `candidate.to_json()` 键集、`region_revisions` count 与 pointer 均不变。
- **V19**：deferral 已登记为“DSH 集成验证（merge 后跨路径组合测试）”，实体可接受。**hygiene 待收口**：`v-matrix.md:19,25` 仍 `NOT_RUN`/旧说明（与 V13 新测试矛盾）；说明行 `:35` 含 **TAB** 且拼写为 `est_machine_...`（应为 `test_machine_...`）；`:36` 文件尾空行；Task 卡 deferral 在主仓库工作区**未提交**（`git status: M doc/tasks/FEA-03.md`），无 Closeout/版本记录。建议 DSH 在集成提交中 canonical 化（matrix 行状态、TAB/EOF、Task 卡 closeout）。
- `git diff --check`：**本 head 交付范围仍 EXIT=2**（`draft_journal.py:421`、`v-matrix.md:36`）；r5 区间为 0。Lead 期望的 0 未达到，属 R-08/R-18 P2。

---

## 5. P2 逐条 disposition（是否可接受遗留）

| P2 | disposition | 说明 |
|---|---|---|
| R-06 V10 单元级注入 | **接受遗留** | 由 FEA-04/集成回归补测；矩阵保持如实状态，不标 PASS。 |
| R-07 V9/V21 precedence、V14/V15/V20/V22 分支 | **接受遗留** | 同上；集成执行 V 矩阵时逐项记录。 |
| R-08 `git diff --check` | **接受但建议集成前修** | 删除两处文件尾空行并重跑真实范围证据（`b83bc7703..head`）；属证据质量阻断项而非实现缺陷。 |
| R-09 Handoff/summary | **接受但建议集成前修** | Handoff `delivery_head`/HEAD 文本、v-matrix 状态与 evidence 必须更新到交付 head。 |
| R-10 ports docstring | **接受遗留** | 建议恢复冻结端口文档；不影响当前运行。 |
| R-11 代码卫生 | **接受遗留** | 重复赋值/未用 import/测试空行，随下一次触碰文件时修。 |
| R-12 C# conflicted/dispose | **接受遗留** | 属 BRIDGE 语义细化，不接线 Host；FEA-04/后续处理。 |
| R-13 生产 close 接线 | **接受遗留（跨 Task）** | 本卡写域不含 `app.py`/`core_service.py`；FEA-04 接线时统一 `CoreServices.close()`。 |
| R-14 recovery 错误包装 | **接受遗留** | 当前 fail-closed 方向安全；错误码/启动策略随集成决策。 |
| R-16 回归测试 | **接受但建议集成前补关键 2 项** | 至少补 (e) 重复 revision 防回归与 R-02 崩溃锁重启测试。 |
| R-17 OpenProcess fail-open | **接受遗留（建议尽快修）** | 风险场景为跨完整性级别；建议 `GetLastError()` 区分 87/5。 |
| R-18 V13 断言/证据 hygiene | **接受但建议集成前修** | V13 断言补强；v-matrix TAB/拼写/EOF/行状态；Task 卡 deferral 提交与 Closeout。 |
| R-19 replay 语义边界 | **接受遗留（需 DSH 口径）** | 按 §2 决定是否放宽 tokenId 门/查找回退；若 AC4 要求强一致则升 P1 再修。 |

---

## 6. 回归验证（本 head，EXIT 均为 0，worktree 保持 clean）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 全量 Python | `python -m pytest tests/core tests/domain tests/editing tests/infrastructure -q -p no:cacheprovider` | **PASS**：`1052 passed, 1 warning in 88.13s`（与 DSH 侧 1052 一致），EXIT=0 | job output |
| BRIDGE dotnet | `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --artifacts-path %TEMP%\fea03-r5-dotnet` | **PASS**：通过 31 / 失败 0 / 跳过 0，EXIT=0 | job output |
| editing 测试单文件 | `python -m pytest tests/editing/test_draft_protection.py -q` | **PASS**：17 passed（含新增 2 个） | 命令输出 |
| 范围 | `git diff --name-only 8875e74ef..1db802f8b` | 2 文件：`drafts.py`、`tests/editing/test_draft_protection.py` | 命令输出 |
| whitespace | `git diff --check b83bc7703..1db802f8b` | **FAIL**：EXIT=2，`draft_journal.py:421` + `v-matrix.md:36`（R-08/R-18） | 命令输出 |
| 交付环境 | 主仓库 `git status` | `M doc/tasks/FEA-03.md`（deferral 未提交）+ 4 份本席位 review 报告未跟踪 | 命令输出 |
| pins | 未重跑（本 head 未触冻结面）；r1 已 15/15 PASS | N/A | — |

---

## 7. 结论与边界

- **`approved`（P0 = 0 / P1 = 0 / P2 = 13）**。r4 唯一 P1（R-01）已按 draft 序号键修复并复现通过；重复 revision 已消除；R-04 的 V19 deferral + V13 补测作为实现侧处置可接受。
- **该 `approved` 不构成集成批准/Task done/Gate 关闭**；P2 中 R-08/R-09/R-18 建议在 DSH 集成前收口（证据 canonical 化、`git diff --check`、Handoff/矩阵更新），R-19 需 DSH 裁定 AC4 的 DraftSequence 口径（若要求新 token 同键幂等，则升 P1 再修）。
- 审查者 `fea03-impl-reviewer` 未参与实现/返修，未 commit/push；本报告写于主仓库工作区 `doc/reviews/FEA-03-r5.md`（未提交）。被审 head 若变化（含返修 commit），本报告自动失效。
