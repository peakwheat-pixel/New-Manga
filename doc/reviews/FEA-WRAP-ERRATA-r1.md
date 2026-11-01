---
task_id: task-4
document_id: FEA-WRAP-ERRATA-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-4"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead（DSH 主会话，Lead / Architect / Integrator）
base_commit: 593141773
reviewed_head: 14e6e6a3c
reviewed_head_full: 14e6e6a3c0493909572f02ac78f5983987624a98
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 14e6e6a3c0493909572f02ac78f5983987624a98）；工作区 clean（git status --porcelain 空）"
repository: G:/CODEX/New Manga
source_branch: main
scope: "L-3 Errata（WRAP-1 的 AC1）：5 个文件的文末追加注记——GATE-CLOSURE-RULING :63/:111、FEA-CONTRACT-FROZEN-C04b §6、-C08 §8、-C09 §8、-C13 §9；依据 doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md §4 Errata 表"
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 5
reviewed_sha256:
  doc/plan/GATE-CLOSURE-RULING-2026-11-01.md: f87d0313803e26f32f9f987f764cb1c2ecd7de53bd1c4ca09345703efa57ea5d
  doc/plan/FEA-CONTRACT-FROZEN-C04b.md: a08498fc57eb7f74cd707fdeca4b3cac99e88053c09b6ab2ace204efe325618b
  doc/plan/FEA-CONTRACT-FROZEN-C08.md: ae3da9ed09515389e0509849aa0a58847ef37539b497533ae2e6f17b5cf9d481
  doc/plan/FEA-CONTRACT-FROZEN-C09.md: 9391fb4edfd7a75794bed15440326183bb09b6525489a2ce98ea4c7cec0f2e92
  doc/plan/FEA-CONTRACT-FROZEN-C13.md: 9664f130a044d7b7257ed37ba40bd862746c0b83262c920c8963fb58640bd3f3
  doc/tasks/FEA-CONTRACT-WRAP-1.md: 5181d3a86c4e93e7ccb31759b2ce7332a3f80f862f3a9bce0537305d6fe1b05a
checkps1: "PASS（3 warnings），EXIT=0；默认调用与 -TaskPath doc/tasks/FEA-CONTRACT-WRAP-1.md 两种调用均实跑，输出一致"
verifypins: "PASS (all 13)，EXIT=0；13 个 pin 值与 base 完全一致（C04b 694ce5bc / C08 453f993c / C09 dc51226b / C13 d2cb8de4 / C14 05056cbf …）"
checker_scope_note: >-
  已核实 `tools/governance/check.ps1` **不覆盖**这 5 个文件（`Select-String 'GATE-CLOSURE-RULING|FEA-CONTRACT-FROZEN'` 于 checker 0 命中），
  因此本轮的 `check.ps1` PASS **不能**作为本项（Errata 内容正确性、引用可解析性）的证据；本报告的结论全部来自 diff/原文逐行比对与独立复算。
independence_note: >-
  本复核与被审产出为不同上下文（DSH 主会话 vs 独立 teammate），不构成自审。
  本轮被审文件不含任何 Review 报告，我未参与这些冻结记录/裁定的撰写；我只做只读比对，未改任何被审文件。
decision_extent: >-
  本批准**只覆盖 WRAP-1 的 AC1（L-3 Errata）**，不覆盖 AC2（PLAN 预算压缩）与 AC3（收尾/指针/独立复核）；
  WRAP-1 卡当前仍为 `status: in_progress` 且 AC1–AC3 均未勾选，属正常中间态。AC2/AC3 完成后需对**新 head** 另出复核。
captured_at: 2026-11-01T12:40:02+08:00
captured_by: c01b-reviewer
---

# Review：L-3 Errata（WRAP-1 · AC1）

## 范围与依据

本 Review 只对 `base_commit: 593141773` → `reviewed_head: 14e6e6a3c` 有效。复核全程 HEAD 未前进、工作区 clean。

**被审 diff（实测全量，5 文件 +49/−0）**：

```text
 doc/plan/FEA-CONTRACT-FROZEN-C04b.md       |  8 ++++++++
 doc/plan/FEA-CONTRACT-FROZEN-C08.md        |  8 ++++++++
 doc/plan/FEA-CONTRACT-FROZEN-C09.md        | 12 ++++++++++++
 doc/plan/FEA-CONTRACT-FROZEN-C13.md        |  9 +++++++++
 doc/plan/GATE-CLOSURE-RULING-2026-11-01.md | 12 ++++++++++++
 5 files changed, 49 insertions(+)
```

你自报"5 文件、49 insertions(+), 0 deletions(-)"——**实测一致**（`git diff --numstat` 逐文件 8/8/12/9/12 = 49）。

**依据**：[关闭裁定 §4 Errata 表](../plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)（本项的授权来源与"铁律"）、`AGENTS.md`（历史证据不改写、不改冻结字节）、09 协作协议 §4.1（证据 pin 与可复现性）、[WRAP-1 卡](../tasks/FEA-CONTRACT-WRAP-1.md) AC1、[C14 收口 R1](FEA-C14-CLOSEOUT-r1.md) 建立的"就地更正 vs Append-Errata"分流原则。

**未审到的部分**：R-1′ / R-2′ / R-4 等裁定条文本身的语义正确性（只核"是否被 Errata 注记覆盖"，不重做裁定）；C-04b/C-08/C-09/C-13 契约条款的正确性（不在本轮范围）；AC2/AC3（本 commit 未包含）。

## Architecture

1. **形式合法：纯追加，零删除**。`git diff 593141773 14e6e6a3c` 中**不存在任何 `-` 行**（脚本判定 deleted/changed lines = 0）；5 个 hunk 头均为 `@@ -N,3 +N,k @@`（上下文 3 行不变，只在文件末尾增加），新增小节全部位于**文末**，未在正文中间插入。文件行数增量 8/8/12/9/12 与 numstat 完全吻合。
2. **原文零改写**：所有被指认的旧文句都原样保留（逐条核见验证表 V-E-3…V-E-8）：`GATE-CLOSURE-RULING`:63「C-09 不会提前解锁」、`:111`「C-09 / 不变 / 仍 blocked」、`:112`「保持 OPEN」；C04b §3:43 / §4:49；C08 §4:55 / §6:65；C13 §5:62–63 / §7:74；C09 §6:74。
3. **未触碰冻结契约字节**：`FEA-C13_DRAFT_PROTECTION_DRAFT.md:203` 原样保留（实测该行仍为「**C-09 的条件③（两 Gate 关闭）仍不满足**，C-09 继续 blocked。」）；13 个受 pin 的 DRAFT 文件字节 0 改动（实算哈希与 pin 值逐一相同，`verify_pins.ps1` 13/13 且**与 base 的 pin 值完全一致**）。注意：被追加注记的是 `FEA-CONTRACT-FROZEN-*.md`（**冻结记录 / 历史证据**），不是被 pin 的 DRAFT 正文——这正是裁定 §4「冻结契约正文一律不动；证据/历史裁定文件只追加注记」区分得当之处。
4. **事实性断言经独立复算，全部为真**（这是本项最容易出错的地方，也是 Lead 指定重点）：
   - `ADJ-001 §9 :128` 由 `2ed4ed91a` 更正 → **真**：该 commit 的 ADJ-001 diff 把 `:128` 行的 `G-DELETE-CONTRACT` 从「OPEN（…D06 缺 4 项 / D07 缺多项…）」改为「**CLOSED（2026-11-01）**…」，且 ADJ-001 的 §9「Gate 与审查安排」起于 `:123`，`:128` 确为该表格行。
   - `FEA-CONTRACT_FREEZE_MATRIX.md` 的 Gate 判定块由 `2ed4ed91a` 更正 → **真**（该 commit 把「❌ 不满足」块替换为「✅ CLOSED」块）。
   - 行号引用全部正确：`:63`/`:111`/`:112`、§3 R-1′ `:51`–`:66`（R-2′ 起于 `:68`，故 R-1′ 末内容行确为 `:66`）、`ADJ-001 §9 :128`、`C-13 draft :203`。
   - Gate 现状表述正确：两 Gate CLOSED、`G-DELETE-IMPL` OPEN（与 ADJ-001 `:128`/`:129`、STATUS 一致）。
5. **语义边界：不构成改裁定 / 改冻结契约**。理由：(a) 注记是**追加**且显式标注「原文保留」，原句仍在原位可读；(b) 注记**不自己宣称** Gate 变更权威，全部指向 [关闭裁定](../plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) 与 ADJ-001 `:128` 作为唯一权威（GATE-CLOSURE-RULING §7 末段即如此写）；(c) 被 pin 的契约正文 0 改动（pin 值未变可证）；(d) 处置方式与裁定 §4 的"铁律"逐字一致，属于**执行授权程序**而非越权修订。

## Verification（逐项，含真实输出）

环境：Windows，`pwsh -NoProfile`，HEAD = `14e6e6a3c0493909572f02ac78f5983987624a98`，工作区 clean。

| # | 场景 | 实际执行 | 结果 | 证据 |
|---|---|---|---|---|
| V-E-1 | `check.ps1`（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings），EXIT=0** | `Task: doc\tasks\FEA-CONTRACT-WRAP-1.md`；WARN：10 非终态 Task、STATUS 3147 B、PLAN 6775 B。**注意**：checker 不覆盖这 5 个文件（见 V-E-12），此 PASS 与本项无关 |
| V-E-2 | `check.ps1 -TaskPath` | `… -TaskPath doc/tasks/FEA-CONTRACT-WRAP-1.md` | **PASS（3 warnings），EXIT=0**（与 V-E-1 逐字相同） | 同上 |
| V-E-3 | 只追加性（全 diff） | 统计 `^-[^-]` 行 | **PASS：删除/改写行 = 0** | `git diff` 无 `-` 行；hunk 头 5 个全部为 `-N,3 +N,k`；`numstat` = 8/8/12/9/12（0 deletions） |
| V-E-4 | GATE-CLOSURE-RULING 旧文保留 | 读 `:63`、`:111`、`:112` | **PASS** | `:63` = 「2. **C-09 不会提前解锁**——C-09 条件②「两 Gate 关闭」在两个 Gate 都 OPEN 时不满足（v1 的错误正在此）」；`:111` = 「\| C-09 \| **不变**（仍等两 Gate 真关闭） \| 仍 blocked \|」；`:112` = 「\| `G-DELETE-CONTRACT` / `G-CONTRACT` \| **保持 OPEN** \| 状态真实 \|」 |
| V-E-5 | C04b 旧文保留 | 读 `:43`、`:49` | **PASS** | `:43`「**下游**：C-09…仍 blocked…（Gate 保持 OPEN）」；`:49`「**不构成** Gate 关闭（…均**保持 OPEN**）」 |
| V-E-6 | C08 旧文保留 | 读 `:55`、`:65` | **PASS** | `:55`「Gate 仍不自动关闭…须经 AC8+AC9 裁定」；`:65`「不构成实现授权；不构成 Gate 关闭；不构成远端 push 授权」 |
| V-E-7 | C13 旧文保留 | 读 `:62`–`:63`、`:74` | **PASS** | `:62`「D06（C-08）未冻、D05 剩余子面…**无承载条款**」；`:63`「**C-09 条件③（两 Gate 关闭）仍不满足** → C-09 继续 blocked」；`:74`「**不构成** Gate 关闭」 |
| V-E-8 | C09 旧文保留 | 读 §5 `:68`、§6 `:74` | **PASS** | `:68` L-1 原文（列出 C-13 `:203`、C-04b/C-08/C-13 记录、GATE-CLOSURE-RULING `:63`/`:111`、ADJ-001 `:128` 旧口径）；`:74`「**不构成** `G-DELETE-CONTRACT` 的关闭（D06 仍有 4 项缺口）」 |
| V-E-9 | **`ADJ-001 §9 :128` 由 `2ed4ed91a` 更正（事实断言）** | `git show 2ed4ed91a -- doc/contracts/ADJ-001_…` | **PASS（断言为真）** | 该 commit diff `@@ -125,7 +125,7 @@`，`:128` 行 `G-DELETE-CONTRACT` 由「**OPEN**（2026-11-01 复核：…**D06 缺 4 项** / **D07 缺多项且与 C-09 循环**…）」改为「**CLOSED（2026-11-01）**——D04/C-13、D05/C-06+C-14+C-01b、D06/C-08 v7、D07/C-09 v5+C-01b+C-04b」；ADJ-001 §9 起于 `:123` |
| V-E-10 | 矩阵 Gate 判定块由 `2ed4ed91a` 更正 | `git show 2ed4ed91a -- doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | **PASS（断言为真）** | 该 commit 把「Gate 判定…**❌ 不满足**…D06 缺 4 项…D07 多项未冻且与 C-09 循环」块替换为「**Gate 判定（最终，2026-11-01）**：两 Gate ✅ CLOSED…保留项 L-1…L-9 与 Errata 见该裁定」 |
| V-E-11 | 冻结契约字节 0 改动 | 实算 13 个 DRAFT 哈希 + `verify_pins.ps1` | **PASS** | C14 `05056cbf65f9` / C13 `d2cb8de4dd79` / C08 `453f993c1a16` / C04b `694ce5bc8c8b` / C09 `dc51226b336c` …；`PIN AUDIT: PASS (all 13)`，EXIT=0，pin 值与 base 逐一相同；`C-13 draft :203` 原文未动 |
| V-E-12 | checker 覆盖范围 | `Select-String tools/governance/check.ps1 -Pattern 'GATE-CLOSURE-RULING\|FEA-CONTRACT-FROZEN'` | **PASS（结论成立）** | **0 命中** → 这 5 个文件不在 checker 的 15 个当前文档内，机器 PASS 不能替本项背书（与你的提醒一致） |
| V-E-13 | 新增相对链接可解析 | 解析 5 个文件的全部相对链接并 `Test-Path` | **FAIL（2 处）** | `../contracts/ADJ-001_…` ✓、`GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` ✓、`FEA-CONTRACT-FROZEN-C09.md` ✓、`FEA-CONTRACT-FROZEN-C04b.md` ✓；**`FEA-D07-UNBLOCK.md` ✗ 2 处**（`FEA-CONTRACT-FROZEN-C04b.md:66`、`GATE-CLOSURE-RULING-2026-11-01.md:147`）→ 解析为 `doc/plan/FEA-D07-UNBLOCK.md`（不存在）；真实位置 `doc/tasks/FEA-D07-UNBLOCK.md`。base 版这两处均无该链接（0 命中）→ 由本 commit 引入 |
| V-E-14 | 指针一致性 | 读 STATUS / PLAN / TASK_LEDGER | **PASS** | `STATUS:7` WRAP-1 `in_progress`；`PLAN:48` 同；`TASK_LEDGER:41` 同；与卡片 `status: in_progress` 一致（本轮没有出现 D06/C14 那种阶段漂移） |
| V-E-15 | 行数增量与声明一致 | `git show --numstat` | **PASS** | 8/8/12/9/12 = **49**；每文件行数 base→head：60→68、93→101、82→94、103→112、139→151 |
| V-E-16 | 复核期间状态完整性 | `git rev-parse HEAD` / `git status --porcelain` | **PASS** | HEAD 全程未变；工作区 clean（本 Review 只写了本文件） |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| WRAP-R1-001 | **P2（非阻断，但必须在下一提交修）** | `doc/plan/FEA-CONTRACT-FROZEN-C04b.md:66`、`doc/plan/GATE-CLOSURE-RULING-2026-11-01.md:147` | 新增链接 `[D07 解环](FEA-D07-UNBLOCK.md)` **解析失败**：从 `doc/plan/` 解析为 `doc/plan/FEA-D07-UNBLOCK.md`，实际文件在 `doc/tasks/FEA-D07-UNBLOCK.md`。两处都在**权威治理文档**里，属"注记指向的解环记录打不开"，弱化可追溯性；repo 对当前文档有"失效的本地引用=FAIL"纪律，只是这 5 个文件不在 checker 覆盖面内，故机器没报 | `Test-Path doc/plan/FEA-D07-UNBLOCK.md` → False；`Test-Path doc/tasks/FEA-D07-UNBLOCK.md` → True；`git show 593141773:<file>` 无该链接（0 命中） | 改为 `[D07 解环](../tasks/FEA-D07-UNBLOCK.md)`（2 处）；若将来该记录迁到 `doc/plan/`，再改回。建议同时把它作为 WRAP-1 的收尾检查项（见 P2-004） | open |
| WRAP-R1-002 | **P2（非阻断）** | `doc/plan/FEA-CONTRACT-FROZEN-C08.md:97` | 注记首句「本记录的旧「D07 缺多项」口径**已无残留**——§4 已在 C-08 v7 冻结时更新…」在语义上**暗示本记录曾载有该口径**；实测 `FROZEN-C08` 全文（除本条新注记外）**不含任何 D07 表述**（`Select-String 'D07\|D-07\|D7\|缺\|循环\|多项\|未冻'` 仅命中新注记）。结论（无残留）本身正确，但理由指向了一个本记录从未有过的表述 | `Select-String doc/plan/FEA-CONTRACT-FROZEN-C08.md -Pattern 'D07'` → 仅命中 `:97`/`:99`（新注记）；§5 已知限制仅 L-1/L-2（preparedDigest 编码、防抖建议值） | 措辞改为「经**全文核对**，本记录**不含**「D07 缺多项」表述，无需更正原文；§4 `:55`（Gate 不自动关闭）与 §6 `:65`（不构成 Gate 关闭）是冻结时状态，现行两 Gate CLOSED（[关闭裁定]）」 | open |
| WRAP-R1-003 | **P2（非阻断）** | `doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:58`（裁定 §4 第 3 行，**未被本 commit 修改**） | 裁定 §4 该行括注写「注：`FROZEN-C08 :55` 现文其实已更新，**本行指认以其 §5 历史段落为准**」——但 `FROZEN-C08 §5`（已知限制）只有 L-1/L-2 两条与 D07 无关，`§7 变更记录` 也无 D07 表述，**"§5 历史段落"在本记录中不存在**。这是裁定的括注自身不精确（不是本次注记引入），但它会误导后续核对者 | 同上 V-E-6 与 `Select-String 'D07'` 结果；裁定 `:58` 原文（`git show 593141773:doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` 该行与本 head 相同） | **不要**在 Errata 提交里改裁定正文（裁定是 Gate 权威）。建议：在 C-08 的 Errata 注记里补一句核对结论（同 WRAP-R1-002 的措辞），并在 WRAP-1 的 Closeout/Handoff 记一条待 DSH 裁定的"裁定 §4:58 括注指向落空"事项；若 DSH 认为需要修订裁定，按其自身 `§7 变更记录` 走版本号 | open |
| WRAP-R1-004 | **P2（非阻断）** | `doc/tasks/FEA-CONTRACT-WRAP-1.md`（未改） | AC1 已实现，但卡片**未同步**：AC1 仍为 `- [ ]`（无 `<<STATUS>>` 标记）、测试要求两行仍 `NOT_RUN / 待复核时补`、`canonical_evidence_status: pending`、`delivery_head: null`、Canonical Evidence 表仅占位行。当前卡片是 `in_progress`，这些属**合法中间态**；但 AC2/AC3 完成后进入 `in_review` 前必须补齐，否则 `check.ps1` 会按 lifecycle v3 报 `未找到任何 AC 行` / AC 标记缺失 / 证据为空 | 卡片 `:57`–`:62`（AC 未勾）、`:64`–`:70`（测试表 NOT_RUN）、`:74`（证据占位行）；`check.ps1:816`–`:852`（AC 标记门禁）、`:660`–`:662`（in_review 需 canonical evidence） | 做 AC2/AC3 时同批回填：勾选 AC1–AC3 + `<<MET>>`、测试表写真实结果与证据、Canonical Evidence 填 4 行（至少含本 commit 与复核报告）、`delivery_head` 回填 | open |
| WRAP-R1-005 | **P2（非阻断，过程建议）** | `tools/governance/check.ps1`（覆盖范围） | 本项 5 个文件**不在** checker 的 15 个当前文档内（V-E-12），而本轮事故（2 处死链）恰好只能靠人工发现。同类"权威但未纳入静态检查"的文档（历史裁定、冻结记录）会持续累积这类小缺陷，且 `check.ps1` 的"失效本地引用"能力用不到它们身上 | `Select-String tools/governance/check.ps1 -Pattern 'GATE-CLOSURE-RULING\|FEA-CONTRACT-FROZEN'` → 0 命中 | 二选一：(a) 在 WRAP-1 收尾时加一个一次性"5 文件链接可解析"检查并留证据；(b) 若长期要保，考虑把 `doc/plan/FEA-CONTRACT-FROZEN-*.md` + `GATE-CLOSURE-RULING-*.md` 纳入 checker 的**引用检查子集**（不纳入预算/哨兵检查，避免预算误报）。属工具改进，需单独授权 | open |

**P0：0；P1：0。** 5 条 P2 全部非阻断——其中 **WRAP-R1-001（2 处死链）建议在本批立即修**（改 2 个路径串，纯文本，不涉裁定/契约语义）。

### 对 Lead 8 个提问的逐条答复

**Q1（只追加不删改）**：**成立**。全 diff 无 `-` 行（V-E-3）；5 个 hunk 均为文末追加；`:63`/`:111`/`:112`、C04b §3:43/§4:49、C08 §4:55/§6:65、C13 §5:62–63/§7:74、C09 §5:68/§6:74 全部**原样保留**（V-E-4…V-E-8）。

**Q2（行号正确性）**：**全部正确**。`:63` = C-09 不会提前解锁句；`:111` = C-09/不变/仍 blocked 行；`:112` = 保持 OPEN 行；§3 R-1′ `:51`–`:66`（R-2′ 起 `:68`）；`ADJ-001 §9 :128`（§9 起 `:123`）；`C-13 draft :203`。**这轮比 C14 那轮的「第 18–20 行」精确**，我逐条 `Select-String` 复核，无一处错位。

**Q3（与裁定 §4 的一致性；有无把「D07 缺多项」写到不该写的文件）**：**覆盖齐全、无遗漏**——裁定 §4 的 5 行处置对象（ADJ-001:128 / 矩阵 / C04b·C08·C13 / GATE-CLOSURE-RULING:63:111 / C13 draft:203）**全部有对应动作**：2 行"已由 `2ed4ed91a` 更正"（V-E-9/10 为真）、4 个文件追加注记、C13 draft 保持原字节。
- **但有一处"写到不该写的文件"的措辞风险**：C-08 注记称其"旧「D07 缺多项」口径已无残留"，而 C-08 记录实际从未载有该口径（P2-002）。严格说这是**措辞不精确**，不是覆盖错误——因为裁定 §4 该行本身就把 C-08 列入"需追加注记"，你按表执行是对的。
- **C-13 草案不可改的声明**：✔ 两处都写了（C-09 §8 一行 + C-13 §9 一行），且都点明"属冻结契约正文，须走 `CONTRACT-UNFREEZE-C13` + 重冻 + 重算 pin"（P2 建议之外无问题）。

**Q4（`ADJ-001 §9 :128` 由 `2ed4ed91a` 更正这一事实断言）**：**核实为真，不判 P1**。见 V-E-9：该 commit 的 ADJ-001 diff 正是把 `:128` 的 `G-DELETE-CONTRACT` 行从「OPEN（…D06 缺 4 项 / D07 缺多项…）」改成「CLOSED（2026-11-01）——D04（C-13）/D05（C-06+C-14+C-01b）/D06（C-08 v7）/D07（C-09 v5+C-01b+C-04b）」。同一断言里对矩阵的"已由 `2ed4ed91a` 更正"亦为真（V-E-10）。

**Q5（新增相对链接可解析）**：**3/4 类可解析，1 类失败**。`../contracts/ADJ-001…` ✓、`GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` ✓、`FEA-CONTRACT-FROZEN-C09.md` ✓；**`FEA-D07-UNBLOCK.md` ✗ 2 处**（`FEA-CONTRACT-FROZEN-C04b.md:66`、`GATE-CLOSURE-RULING-2026-11-01.md:147`）。修法：`../tasks/FEA-D07-UNBLOCK.md`。（P2 WRAP-R1-001）

**Q6（语义边界：是否构成改裁定/改冻结契约）**：**不构成，理由四条**：
1. **形式**：纯追加 + 显式「原文保留」，原句仍在原位可读，任何人可对照；Errata 不产生"新裁定"，只是把冻结时状态与现行状态并列。
2. **权威指向**：注记不自行宣布 Gate 变更，全部指向 [关闭裁定](../plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) 与 `ADJ-001 §9 :128`——与裁定 §4 的"Gate 状态的唯一权威"要求一致。
3. **字节**：被 pin 的是 13 份 **DRAFT**；本轮改的是 **FROZEN 记录**（历史/证据类，不在 pin 面），pin 值 13/13 未变可证冻结契约字节 0 改动；唯一真正"属冻结契约正文"的 `C-13 draft :203` 被明确**不动**。
4. **授权**：裁定 §4 明文要求"证据/历史裁定文件只追加注记，不删原文"，本轮正是执行该程序。

**Q7（三命令 + pins）**：两路 `check.ps1` PASS/EXIT 0；`verify_pins.ps1` 13/13 PASS/EXIT 0 且 pin 值与 base 完全一致。**但按你的提醒**：这 5 个文件不在 checker 覆盖面内（V-E-12），机器 PASS 不能证明本项——本报告的结论全部来自 diff/原文比对与哈希复算。

**Q8（P0/P1）**：**无 P0、无 P1**。5 条 P2 非阻断（WRAP-R1-001 建议立即修）。

### 关于 AC1 验收标准是否要调整（你特别问的）

**建议调整，且本轮正好暴露了它的边界。** 现有 AC1 只写「只追加注记、保留原文 + 13 份 DRAFT 0 改动 + C-13 draft:203 保持原字节」，这三条**本轮全部满足**，但**允许了 2 处死链进入权威文档**——因为"引用可解析"没被写成判据。建议 AC1 增补三项可执行判据：

1. **引用可解析**：新增/改动的相对链接必须按**文件所在目录**解析成功（可用 `Test-Path`）。
2. **位指正确**：注记中每个 `:行号` / `§小节` 必须与现行文件一致；跨文件引用建议"小节 + 行号"双标注（避免 C14 那类"第 18–20 行"歧义）。
3. **覆盖对齐**：注记必须与裁定 §4 表**逐行对应**，并对"该行指认的表述在本文件中是否真的存在"给出核对结论（本轮 C-08 就属于"表里有、文件里没有"的情形，需要显式记录）。

**对本轮 decision 的影响（透明说明）**：按**现行 AC1 文本**，本 head 判 **`approved`**（P2 非阻断，与 C14-R1 把"引用位置写错"判为 P2 的先例一致）；**若把上述第 1 条写进 AC1**，则本次 2 处死链应判 **`changes_requested`**。你选哪条路我都接受，只要报告与 AC 口径一致即可——建议你现在补 AC1 判据，然后把死链当 AC1 的一部分一次修完。

## Architecture / Verification 分面结论

- **Architecture：通过**。处置方式与裁定 §4 的"铁律"逐字一致（只追加、原文字节保留、冻结契约正文不动）；唯一 pin 面（13 份 DRAFT）0 改动且 pin 值不变；事实性断言（ADJ-001 `:128`、矩阵、Gate 现状）经独立复算全部为真；不构成改裁定/改契约。缺陷集中在引用精度（P2）。
- **Verification：通过（附条件）**。删除行 0、5 个 hunk 均为文末追加、旧文零改写、行号/小节引用全部正确、13 pins 未动、指针无漂移。**FAIL 1 项**：2 处新链死链（V-E-13）。机器 `check.ps1` PASS 与本项无关（已证实 checker 不覆盖这 5 个文件），故未作为任何 PASS 的依据。

## 结论与复审

**decision：`approved`**（P0 × 0 / P1 × 0 / P2 × 5，全部非阻断）。

L-3 Errata 的**形式、内容、边界、事实断言**四方面均成立：纯追加零删除、旧文全保留、行号与跨文件引用准确、`ADJ-001 §9 :128`/矩阵的 `2ed4ed91a` 断言为真、13 份冻结契约字节 0 改动、不构成改裁定或改冻结契约。**本批准只覆盖 WRAP-1 的 AC1**。

**唯一需要立刻处理的事项**：2 处 `FEA-D07-UNBLOCK.md` 死链（WRAP-R1-001）——建议在后续提交一并改 `../tasks/FEA-D07-UNBLOCK.md`。其余 4 条 P2 可在 WRAP-1 收尾（AC2/AC3）时同批处理。

**复审边界**：AC2（PLAN 压缩到 <5600 B / ≤50 行、历史迁入 `PLAN-HISTORY.md`）与 AC3（指针/checkpoint/独立复核）完成后，必须对**新 head** 另出复核；本报告不延用（09 §6）。届时我会重核：PLAN 预算实测、迁移是否"原样"（字节/内容对比）、checker 是否仍 PASS、以及本轮 5 条 P2 的处置。

—— 报告结束（`decision: approved`；P0×0 / P1×0 / P2×5 非阻断；范围仅 AC1；建议同时收紧 AC1 判据）。
