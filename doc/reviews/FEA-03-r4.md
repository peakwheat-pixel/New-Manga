---
document_id: FEA-03-r4
kind: independent_implementation_review
reviewer: fea03-impl-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea03-impl-reviewer` 续任，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 起草、范围冻结/UNFREEZE、实现、r1–r3 返修"
reviewer_independent: true
reviewed_by_implementer: false
author: "codex（实现交付）+ dsh（r1–r3 返修 commit 8875e74ef；Task 卡 deferral 在主仓库工作区未提交）"
base_commit: 692d8b584
reviewed_head: 8875e74ef
reviewed_head_full: 8875e74ef91a03cc190d918fb4a70a4451e3da18
repository_under_review: "G:/CODEX/New Manga.workspace/FEA-03（branch feat/fea-03，只读审查）"
main_head_at_review: 8c40fe011
date: 2026-11-02
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 12
---

# Review：FEA-03 实现复核 r4（base `692d8b584` / reviewed_head `8875e74ef`）

**结论：`changes_requested`（P0 × 0 / P1 × 1 / P2 × 12）。**

r3 的两条 P1 中，**R-04 已按 DSH 的 V19 integration deferral + V13 补测处置，P1 关闭**（余下为 P2 证据/断言完整性问题，R-18）；**R-01 只闭合了一部分**：`open→patch→prepare→apply(open token)`、同 token 重放、重启后同 token 重放均通过，但 **新 token（seq1）重放不命中 receipt**（`DRAFT_CANDIDATE_NOT_FOUND`），且同一 draft 状态在新 token 下可再提交出 **内容完全相同的第 3 个 revision**（见 §2）。因此仍为 `changes_requested`。

本报告只对 `8875e74ef` 有效，不构成集成批准、不构成 Task done、不构成 Gate 关闭。审查者未参与实现/返修；只读被审 head，测试产物写 `%TEMP%`，未 commit/push。

**r4 范围**：`git diff 692d8b584..8875e74ef` 3 文件（`drafts.py` +1/−1、`tests/editing/test_draft_protection.py` +18、`verification/FEA-03/v-matrix.md` +5/−1）；无 `doc/`、无 Handoff、无 C# 变更。

---

## 0. 复核对象、方法与环境

| 项 | 值 |
|---|---|
| 实现 worktree | `G:\CODEX\New Manga.workspace\FEA-03`（branch `feat/fea-03`，HEAD `8875e74ef`，工作区 clean） |
| 被审 commit | `8875e74ef fix(fea-03): 处置实现复核 r3（R-01 receipt 幂等键、V13 测试、V19 deferral 登记）` |
| 环境 | Windows；CPython 3.14.6；pytest 9.1.1；.NET SDK 10.0.401；dotnet artifacts 指到 `%TEMP%` |
| 重跑 | 全量 `tests/core tests/domain tests/editing tests/infrastructure`；`dotnet test`；针对 R-01 四个场景与重复 revision 的生产装配复现 |
| 未执行 | 未重跑 pins（本 head 未触冻结面；r1 已 15/15 PASS）；R-17 的跨完整性级别权限场景未实跑（静态判定）；V19 组合场景按 deferral 未跑 |

---

## 1. r3 findings 逐项 disposition

| r3 ID | r3 级别 | r4 状态 | 核验结论与证据 |
|---|---|---|---|
| **R-01** receipt 幂等键 | P1 | **open（部分修复，仍 P1）** | 修复：receipt `DraftSequence` 改为 `edit_token.draft_sequence`（`drafts.py:497`），与重放查找键（`:383`）一致。实测：**(a)** open(seq0)→patch(seq1)→prepare(seq1)→apply(open token) **成功**；**(b)** 同 token 重放 **返回同 `revisionIds`**，revision count 2→2；**(c)** 重启后同 token 重放 **命中 receipt**；(d) **新 token（seq1）重放同内容 → `DRAFT_CANDIDATE_NOT_FOUND`（未命中 receipt(seq1)）**。进一步：持新 token（seq1）对同一 draft 状态 prepare 一个内容等价的 candidate（style 同值）再 apply，会写出 **第 3 个 snapshot 完全相同的 revision**（count 2→3，last two snapshots equal=True）——若 `DraftSequence` 指 draft 序号（AC4 语义），这是“同 (DraftId,DraftSequence) 新增 revision”的直接违反；若指 token 序号（seq0≠seq1），则 Lead 的 (d) 期望本身不成立，需要 DSH 明确语义并写清。 |
| **R-02** 崩溃锁回收 | P1 | **closed** | r3 已修复并复现（死 PID 有/无句柄均 False；`os._exit` 后重启 journal available=True、写成功）；本 head 未回退。 |
| **R-03** close→reopen 锁重建 | P1 | **closed** | r2 已修，本 head 未回退。 |
| **R-04** AC6/V13、AC11/V19 | P1 | **closed（P1 关闭，余留 R-18/P2）** | V19 已在主仓库工作区 Task 卡「契约 deferral 登记」+ worktree `v-matrix.md` 登记为 **DSH 集成验证 deferral**（merge 后跨路径组合测试；理由：本卡不改旧路径、V18 覆盖 tests/core 旧路径回归）。该 deferral 的**实体内容可接受**（有 owner、理由、验收载体）→ P1 关闭；但 canonical 化与 V13 断言完整性存在问题，降级为 **R-18（P2）**。 |
| **R-05** 孤儿假冲突 | P1 | **closed** | r3 已修复（DISCARDED 过滤；page/region 级 orphan 重开均通过）；本 head 未回退。 |
| **R-06** V10 单元级异常注入 | P2 | **open** | 无测试变更；仍只有真实子进程 A/B/C。 |
| **R-07** V9/V21 precedence、V14/V15/V20/V22 分支 | P2 | **open** | 无测试变更；V9/V21“过期先于 receipt”仍未先产生 receipt。 |
| **R-08** `git diff --check` | P2 | **open（恶化）** | `git diff --check b83bc7703..8875e74ef` = **EXIT=2**，两条：`draft_journal.py:421: new blank line at EOF.` + `v-matrix.md:36: new blank line at EOF.`（r4 的 v-matrix 变更**新增**了一条）；区间 `692d8b584..8875e74ef` 也 EXIT=2。Lead 期望的“0”未达到。 |
| **R-09** Handoff/summary/证据落后 | P2 | **open** | 无 doc/Handoff 变更：Handoff `:6,14,81` 仍 `delivery_head:null`/`b83bc7703 未提交`；`summary.md:3` 同。 |
| **R-10** ports.py 契约 docstring | P2 | **open** | 未改（`ports.py:106`）。 |
| **R-11** 代码卫生 | P2 | **open** | 未改（`draft_journal.py:92-95` 重复赋值、`:5` 未用 `errno`；`drafts.py:523-544` 重复 except 清 intent）；新测试文件尾部无换行、函数间仅 1 个空行（P2，并入 R-18）。 |
| **R-12** C# conflicted/dispose | P2 | **open** | 未改（`DraftBuffer.cs:69`）。 |
| **R-13** 生产关闭接线 | P2 | **open** | 未改（`app.py:182,445`、`core_service.py:5822` 仍 `conn.close()`）。 |
| **R-14** recovery 错误包装 | P2 | **open** | 未改（`drafts.py:646-685`）。 |
| **R-15** cleanup 剥夺新 owner | P2 | **closed** | r3 已修（owner 匹配才释放）；本 head 未回退。 |
| **R-16** 修复无回归测试 | P2 | **open** | 本 head 仅新增 V13 测试（1 个）；R-01（r4）、R-02/R-05（r3）修复仍无专测；1051 passed 不覆盖这些路径（R-01 的 (d)/重复 revision 用例为证）。最小测试清单见 §4。 |
| **R-17** OpenProcess 失败 fail-open | P2 | **open** | 未改：`_process_is_alive`（`draft_journal.py:35-38`）对任何 `OpenProcess` 失败返回 False，未区分 `ERROR_ACCESS_DENIED`；跨完整性级别时可能误删活写者的锁（未实跑，静态判定）。 |

**新增（r4）**：

| r4 ID | 级别 | 位置 | 问题 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R-18** | P2 | `tests/editing/test_draft_protection.py:415-430`；`verification/FEA-03/v-matrix.md:19,25,35-36`；主仓库 `doc/tasks/FEA-03.md`（未提交，+2 行） | ①**V13 测试不完整**：只断言 `origin=="machine"` 与 pointer 不变；未断言 candidate 四字段键集、revision count 不变、存在活跃草稿（V13“翻译产物 vs 活跃草稿”），也未验证 apply 只新增 1 revision；测试文件无结尾换行、函数间仅 1 空行。②**V19 deferral 证据 hygiene**：Task 卡 deferral 行在**主仓库工作区未提交**（`git status: M doc/tasks/FEA-03.md`），无 Closeout/版本记录；`v-matrix.md` 的 V13/V19 行仍写 `NOT_RUN`/“未执行”，与新增说明矛盾；说明文本含 **TAB 控制字符**（`已补 <TAB>est_machine_...`，应为 `test_machine_...`）；v-matrix 变更新增文件尾空行（R-08）。 | 见左；实测 V13 测试在 1051 passed 中通过。 | 补 V13 断言（四字段、count 不变、活跃草稿）；提交 Task 卡 deferral 并加 Closeout 行；修正 v-matrix 行状态与 TAB 拼写、删除尾空行；测试文件补结尾换行与 PEP8 空行。 | open |

---

## 2. R-01 四场景 + 重复 revision 复现（生产 `assemble_production_core`）

```text
open token seq: 0
draft seq: 1
(a) apply open token OK: {'<region>': '<rev>'}
(b) same-token replay: {...} equal: True
revision count: 2 -> 2
receipt(seq0): True receipt(seq1): False
new token seq: 1
(d) new-token replay RAISED: DraftError DRAFT_CANDIDATE_NOT_FOUND candidate registry entry is missing
(c) restart same-token replay: {...}   # 命中 receipt(seq0)
restart new token seq: 1
(d2) restart new-token replay RAISED: DraftError DRAFT_CANDIDATE_NOT_FOUND candidate registry entry is missing
```

重复 revision（同 draft 状态 + 新 token + 内容等价 candidate）：

```text
first apply: {...} count: 2 current: <rev1>
new token seq: 1
second apply (identical content via style) OK: {...}
revision count: 2 -> 3
last two snapshots equal: True nos: 3 2
new-token replay after second apply: {...}   # 第二次 apply 后 receipt(seq1) 才存在
```

**判读**：
- 当前实现把 receipt 键定为 **token 的 `DraftSequence`**，而 token 序号会随 draft 前进（open 时 0，patch 后新 token 为 1），因此同一 draft 状态可对应不同 receipt 键：旧 token（0）重放可命中；新 token（1）重放不命中，并且可再次提交出内容相同的 revision。
- 若按 AC4 的“同 `(DraftId, DraftSequence)` 不新增 revision”把 DraftSequence 理解为 **draft 序号**，这是 P1 违反；若理解为 **token 序号**，则需在卡/契约写明“新 token = 新提交键”并说明重复 revision 的防护（当前没有）。
- **建议最小修复**：receipt 的写入与查找统一用 `draft.draft_sequence`（`drafts.py:497` 改回 draft seq；`:383` 改成先取 draft 再 `read_receipt(draft_id, draft.draft_sequence)`，draft 缺失时回退 token seq），token 只做过期/归属校验；这样 (a)(b)(c)(d) 均命中，且同 draft 状态不会因换 token 再落 revision。补 §4-1/§4-2 测试。

---

## 3. V13 测试与 V19 deferral 评估

### V13（`tests/editing/test_draft_protection.py:415-430`）

**已满足**：`origin="machine"` 的 candidate 可 prepare；prepare 后 `current_revision_id` 不变（`assert` at `:428-429`）。
**未满足/未断言**（相对 AC6/V13）：
1. candidate 四字段键集（`{candidateId, RegionId, BaseRevisionId, origin}`）未断言；
2. `region_revisions` count 未断言不变；
3. 场景未包含“**活跃草稿**”（V13：翻译产物 vs 活跃草稿）；当前测试没有 open draft；
4. 未验证 apply 后只新增 1 revision（V13 只要求 candidate，但 AC6 要求 apply 语义一致；可作为补充）；
5. 测试文件无结尾换行、函数间仅 1 空行（style）。

**结论**：V13 从 NOT_RUN 提升为 **PARTIAL**；断言足够证明 machine candidate 不写指针，但不足以完整覆盖 AC6/V13。归入 R-18（P2）。

### V19 deferral（主仓库 `doc/tasks/FEA-03.md`「契约 deferral 登记」+ worktree v-matrix）

**实体内容可接受**：`V19（旧→新/新→旧组合） → DSH 集成验证（merge 后跨路径组合测试）`，理由为“本卡不改旧路径；旧路径行为不变由 tests/core 回归覆盖（V18）”。作为 DSH（Lead/Integrator）对验收载体的裁决，实现复核可以接受该 deferral，R-04 的 P1 关闭。**遗留 hygiene**：
- Task 卡改动在**主仓库工作区未提交**（`M doc/tasks/FEA-03.md`），无 Closeout/版本记录；应在 DSH 集成提交中 canonical 化（或至少记录 deferral 来源与生效点）。
- `v-matrix.md` 的 V19 行仍为 `NOT_RUN` 且旧说明“测试源/基线未执行”，与新增 deferral 说明不一致；V13 行仍 `NOT_RUN`，与新测试矛盾。
- 说明文本含 TAB（`est_machine...` 拼写错误），并新增文件尾空行（R-08）。
- V19 组合场景仍未执行；若 DSH 集成验证延后，需在 Handoff/checkpoint 里保留 NOT_RUN 与 owner。

---

## 4. R-16 最小回归测试清单（仍缺）

1. **R-01 (a)-(d)**：open→patch→prepare→apply(open token)；同 token 重放返回同 revisionIds；重启同 token 命中；新 token（seq1）同内容重放命中（当前失败，应作为红灯测试）。
2. **重复 revision 防护**：成功 apply 后，换新 token + 内容等价 candidate 再 apply，断言不新增 revision（当前会 2→3）。
3. **R-02**：死 PID（无残留句柄）`.lock` → 新 `DraftJournal` available=True 且写成功；真实 `os._exit` 子进程 → 重启 journal 可写；活 PID → True。
4. **R-05/R-15**：page/region 级 orphan discard → 新 Session 重新 open 并 patch 成功；transfer A→B 后 `discard_orphans({"sB"})` 不剥夺 B（B patch 成功）。
5. **R-17**（若保留现状）：至少静态/单元测试覆盖 `_process_is_alive` 对无效 pid=False、活 pid=True；跨权限场景无法测时在风险登记写明。
6. **V13** 断言补强（见 §3）。

---

## 5. 回归验证（本 head，EXIT 均为 0，worktree 保持 clean）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 全量 Python | `python -m pytest tests/core tests/domain tests/editing tests/infrastructure -q -p no:cacheprovider` | **PASS**：`1051 passed, 1 warning in 87.97s`（与 DSH 侧 1051 一致），EXIT=0 | job output |
| BRIDGE dotnet | `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj --artifacts-path %TEMP%\fea03-r4-dotnet` | **PASS**：通过 31 / 失败 0 / 跳过 0，EXIT=0 | job output |
| 范围 | `git diff --name-only 692d8b584..8875e74ef` | 3 文件：`drafts.py`、`tests/editing/test_draft_protection.py`、`verification/FEA-03/v-matrix.md`；无 doc/Handoff/C# | 命令输出 |
| whitespace | `git diff --check b83bc7703..8875e74ef` | **FAIL**：EXIT=2，`draft_journal.py:421` + `v-matrix.md:36` 两处 new blank line at EOF（R-08） | 命令输出 |
| 任务卡 deferral | 主仓库 `git status` | `M doc/tasks/FEA-03.md`（未提交）；worktree v-matrix 说明含 TAB/拼写错误、行状态未更新（R-18） | 命令输出 |
| pins | 未重跑（本 head 未触冻结面）；r1 已 15/15 PASS | N/A | — |

---

## 6. 结论与复审要求

- **P0 = 0 / P1 = 1 / P2 = 12 → `changes_requested`**。
- 放行所需（最小）：**R-01** —— 按 §2 建议统一 receipt 的写入/查找键为 `draft.draft_sequence`（或由 DSH 明确 token 序号语义并实现重复 revision 防护），补 §4-1/§4-2 测试；修完后本项可关闭。
- **R-04 已按 deferral + V13 补测关闭 P1**；剩余 V13 断言、V19 canonical 登记、v-matrix 状态/拼写/尾空行归入 **R-18（P2）**，需在集成前修正。
- 可接受遗留（P2，需登记）：R-06/R-07（V10 注入、V9/V21 precedence、V14/V15/V20/V22 分支）、R-08（尾空行与真实范围证据）、R-09（Handoff/summary 更新）、R-10（ports docstring）、R-11（卫生）、R-12（C#）、R-13（生产 close 接线）、R-14（recovery 包装）、R-16（回归测试清单）、R-17（ACCESS_DENIED 区分）、R-18（V13/V19 证据）。
- **边界声明**：本报告只审 `8875e74ef` 的实现交付，不构成集成批准、不构成 Task done、不构成 Gate 关闭；r1–r3 报告保持历史记录；head 若再变化需对新 fixed head 重审。审查者 `fea03-impl-reviewer` 未参与实现/返修，未 commit/push；本报告写于主仓库工作区 `doc/reviews/FEA-03-r4.md`（未提交）。
