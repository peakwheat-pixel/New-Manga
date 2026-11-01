---
task_id: task-8
document_id: FEA-WRAP-CLOSEOUT-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-8"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead（DSH 主会话，Lead / Architect / Integrator）
base_commit: 8dfe9e371
reviewed_head: 6c0195437
reviewed_head_full: 6c01954373f44b656baa4a22b22e084eb6968267
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 6c01954373f44b656baa4a22b22e084eb6968267）；工作区 clean"
repository: G:/CODEX/New Manga
source_branch: main
scope: "WRAP-1 收口：AC1 增补判据 + AC2（PLAN 预算压缩/历史原样迁入）+ AC3（指针/检查/checkpoint）+ 证据与 Resource Manifest 的 done 门禁 + done 提交范围裁定"
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 5
prior_review: doc/reviews/FEA-WRAP-ERRATA-r1.md
prior_decision: approved
reviewed_sha256:
  doc/tasks/FEA-CONTRACT-WRAP-1.md: 15ee8a12836a50891c15393c9e69704746ab54db9420c9c4a9334af2a19537a0
  doc/REBASELINE_PLAN.md: 2257B/32L（实测，见 V-W-4）
  doc/PLAN-HISTORY.md: 8e292d43c4c30584bca76d3aa3c4127e1cb551ae6535c6ecba6ce3e05b87efaf
  verification/FEA-CONTRACT-WRAP-1/closeout-check.md: 6aeaf45e7e52c8d55e07841c3ac02874feac183cbaf53ea72d894b7d13691087
  doc/checkpoints/AUTONOMOUS-2026-11-01.md: 3ad45ee3c4aa7ca3acd5d7ec9b2292509c21f7682d9eef6bc5634fdbe993a3b2
checkps1: "in_review 状态：PASS（2 warnings），EXIT=0（默认与 -TaskPath 两种调用均实跑一致）；**done 门禁模拟：FAIL**（1 个真实错误 + 1 个 TEMP 路径伪错误，见 P1-001）"
verifypins: "PASS (all 13)，EXIT=0；pin 值与 base 相同；本 commit 未触及任何受 pin 文件"
decision_extent: >-
  本决定覆盖 AC1 增补 / AC2 / AC3 / 证据表 / checkpoint 的复核，以及 done 提交范围裁定。
  **P1-001（Resource Manifest 第 3 行 disposition 非法）未修前不得做 done 提交**——已用 `$env:TEMP` 模拟证明 done 门禁会 FAIL。
same_defect_check: >-
  P1-001 与本 Task 既往复核无重复（首次发现，源于 Lead 本轮新增的 done 门禁模拟要求）；
  它是**机械可判定**缺陷（一行 disposition 词表不合法），非内容真实性问题。
independence_note: >-
  本复核与被审产出为不同上下文（DSH 主会话 vs 独立 teammate），不构成自审；我未参与 WRAP-1 的实现/返修，未修改任何被审文件（仅写本报告）。
captured_at: 2026-11-01T13:03:46+08:00
captured_by: c01b-reviewer
---

# Review：WRAP-1 收口（AC1 增补 + AC2 + AC3）

## 范围与依据

本 Review 只对 `base_commit: 8dfe9e371` → `reviewed_head: 6c0195437` 有效。复核全程 HEAD 未前进、工作区 clean。

**实测 diff（6 文件 +133/−52）**：`doc/PLAN-HISTORY.md`(+38/−0)、`doc/REBASELINE_PLAN.md`(+8/−33)、`doc/TASK_LEDGER.md`(+4/−4)、`doc/checkpoints/AUTONOMOUS-2026-11-01.md`(+17/−2)、`doc/tasks/FEA-CONTRACT-WRAP-1.md`(+25/−13)、`verification/FEA-CONTRACT-WRAP-1/closeout-check.md`(+41/−0，新建)。**未触及 13 份受 pin 契约、未触及代码、未触及 Gate 文件。**

**依据**：[AC1 R1 复核](FEA-WRAP-ERRATA-r1.md)（本文件 frontmatter 的三条增补判据来源）、WRAP-1 卡 AC1–AC3、裁定 §4 Errata 表、09 §4.1/§4.2/§5.1/§5.2、`check.ps1` 的 done 门禁（`:743`/`:744`/`:746`/`:749`/`:784`–`:812`）、[C14 收口先例](FEA-C14-CLOSEOUT-r1.md)。

**未审的**：`PLAN-HISTORY.md` 既有前半段（41 行，非本次迁入）；其它 Task 的 done 合法性（D06/C14 已由前轮复核）；用户裁定事项本身。

## Architecture

1. **AC1 增补判据全部成立**（三条：链接可解析、行号一致、与裁定 §4 逐行对齐 + "表里有、文件里没有"的核对结论）。
2. **AC2 达标且迁移是逐字节原样**：PLAN `2257 B / 32 行`（阈值 `<5600 B` 且 `≤50 行`，同时消除 80% 告警）；`PLAN-HISTORY` 纯新增 `38/0`；迁入的 31 行与 base PLAN 第 9–39 行 **31/31 逐字节相同（0 差异）**；PLAN 保留 READY 行、活动程序、当前 DAG、终态约束段。
3. **AC3 部分成立**：两路 `check.ps1` PASS(2w)、`verify_pins.ps1` 13/13、`TASK_LEDGER` 已重生成且为 `in_review`；但 **STATUS/PLAN 仍写 `in_progress`**（P2-001）。
4. **证据与门禁**：4 条 evidence 的 sha256 全部实算一致（双口径成立，`-` + sha256 属 §4.1 合法形态）；**但 Resource Manifest 第 3 行 disposition `PRESERVE` 不在检查器词表内 → done 门禁 FAIL（P1-001）**。
5. **checkpoint 真实、无虚假陈述**：5 项队列行的 check/pins/报告/问题齐全，start-state 三个数值与历史 ledger/字节实测吻合；8 项待裁决覆盖真实遗留。瑕疵为行 5 缺 HEAD、"队列 5 项全部完成"措辞早于 in_review 完成、重复 `## 收尾` 标题（P2-003）。
6. **done 提交范围**：你列的范围**基本可接受，但必须追加 Resource Manifest 第 3 行的一词修正**（P1-001）——否则 done 提交必然 FAIL。详见末节裁定。

## Verification（逐项，含真实输出）

环境：Windows，`pwsh -NoProfile`，HEAD = `6c0195437…`，工作区 clean。

| # | 场景 | 实际执行 | 结果 | 证据 |
|---|---|---|---|---|
| V-W-1 | AC1：5 文件死链 | 按文件所在目录解析全部相对链接 | **PASS：0 死链** | 5 个被注记文件全部可解析（含 `../tasks/FEA-D07-UNBLOCK.md` 2 处已修） |
| V-W-2 | AC1：行号/小节一致 | `Select-String` 抽 `:63`/`:111`/`:112`、C04b §3/§4、C08 `:55`/`:65`、C13 `:62-63`/`:74`、C09 `:68`/`:74`、C13 草案 `:203` | **PASS** | `:63` = 「C-09 不会提前解锁…」；`:111` = 「\| C-09 \| **不变**（仍等两 Gate 真关闭） \| 仍 blocked \|」；C13 草案 `:203` = 「**C-09 的条件③（两 Gate 关闭）仍不满足**…」——全部与注记引用一致 |
| V-W-3 | AC1：与裁定 §4 对齐 + C-08 核对结论 | 读 C-08 §8 注记 | **PASS** | `:97` 已写「**经全文核对，本记录原本就不含「D07 缺多项」表述**（除本节外全文 0 命中）…裁定 §4 括注所称「以其 §5 历史段落为准」在本记录中**指向落空**」——即我 R1 要求的"表里有、文件里没有"结论 ✅ |
| V-W-4 | **AC2：PLAN 预算** | `Get-Item` + 行数 | **PASS** | **2257 B / 32 行**（阈值 5600 B / 51 行；`check.ps1` 已无 PLAN 预算 WARN） |
| V-W-5 | **AC2：迁移纯新增** | `git diff --numstat 8dfe9e371 6c0195437 -- doc/PLAN-HISTORY.md` | **PASS** | `38 0`（与你的自述一致） |
| V-W-6 | **AC2：31 行逐字节原样** | 取 diff 的 38 个新增行去掉前 7 行说明/表头，与 `git show 8dfe9e371:doc/REBASELINE_PLAN.md` 第 9–39 行逐行比对 | **PASS：31/31 完全一致，mismatch = 0** | 含 base 第 22 行的空行也一并原样保留（见 P2-004） |
| V-W-7 | AC2：不删被引用当前状态 | 读 head PLAN 全文 32 行 | **PASS** | 当前 DAG 表（WRAP/C10/C14+D06/NEW-MANGA）、`READY 节点：无`（`:21`）、活动程序段（`:16`–`:23`）、历史快照 + 终态约束段（`:25`–`:32`）全部保留；新增迁移说明 `:14` |
| V-W-8 | **AC3：三命令** | `check.ps1` / `check.ps1 -TaskPath` / `verify_pins.ps1` | **PASS** | `PASS (2 warnings)` EXIT=0 ×2（WARN = 11 非终态 Task、STATUS 80%）；`PIN AUDIT: PASS (all 13)` EXIT=0 |
| V-W-9 | AC3：指针一致性 | 读 STATUS/PLAN/LEDGER 三处 | **FAIL（部分）** | 卡 `in_review`、LEDGER `:44` = `in_review` ✓；但 **STATUS `:7` = `in_progress`（"PLAN 预算/收尾待做"）**、**PLAN `:9` = `in_progress`** → 见 P2-001 |
| V-W-10 | AC3：closeout-check 记录准确性 | 与实跑结果对表 | **1 处偏差** | PASS(2w) ✓、pins 13/13 ✓、STATUS 3157 B/32 行 ✓、PLAN 6777→2257 ✓、history 9504 ✓；**`PLAN-HISTORY` 基线写 4132 B，实测 `git cat-file -s` = 4131 B** ✗ |
| V-W-11 | **证据表 4 条双口径** | 逐条实算 sha256（worktree 与 `git cat-file blob <commit>:<path>`） | **PASS** | `E-WRAP-ERRATA-R1` `0d183364…` = worktree = `500aa6b27` blob ✓；`E-ERRATA-DOC` `ae4a432b…` @`500aa6b27` ✓；`E-PLAN-HISTORY` `8e292d43…` ✓（`-` commit + sha256，§4.1 合法）；`E-WRAP-CHECK` `6aeaf45e…` ✓ |
| V-W-12 | checkpoint：5 行队列 | 逐行读 | **部分**（P2-003） | 行 1–4 均有 HEAD/check/pins/报告/问题 ✓；**行 5 的 HEAD 列写「in_review（收口材料见下一行补记）」且无下一行**✗；check/pins 值 `PASS (2w)` / `13/13` ✓ |
| V-W-13 | checkpoint：start-state 真实性 | 与历史 ledger/字节实测比对 | **PASS（精确）** | 声明「STATUS 3159 B / PLAN 6687 B / 11 非终态 Task」↔ `git cat-file -s 6358cfd05:doc/STATUS.md` = **3159**、PLAN = **6687**、`git show 6358cfd05:doc/TASK_LEDGER.md`「non-terminal **11**」——三项全对 |
| V-W-14 | checkpoint：8 项待裁决 | 逐条比对真实遗留 | **PASS** | C-10 冻结/`T`、L1–L4 口径、Manifest 偏离、L-1…L-9、`G-DELETE-IMPL`、非队列 Task、已接受 P2 债务、裁定 §4:58 括注落空 —— 与工程实际一一对应，无编造 |
| V-W-15 | checkpoint：收尾节 | 读 `:45`–`:55` | **部分**（P2-003） | 「队列 5 项全部完成」早于第 5 项 in_review 完成；另有**两个** `## 收尾` 标题（`:45` 与 `:53`，后者为空占位） |
| V-W-16 | **done 门禁模拟（原样）** | 复制卡到 `$env:TEMP`，改 `status: done` + `integration_commit: 6c0195437` + `resource_closeout_status: complete`，跑 `check.ps1 -TaskPath` | **FAIL（2 errors）** | `FAIL: Resource disposition 无效：PRESERVE`（真实错误，P1-001）+ `FAIL: 失效的本地引用 …→ ../plan/…`（TEMP 路径伪错误，非缺陷） |
| V-W-17 | **done 门禁模拟（修 P1 后）** | 同上 + 第 3 行 disposition → `NOT_APPLICABLE` | **disposition 错误消失** | 剩余 2 errors 均为模拟环境伪错误：`../plan/…` 相对链接（TEMP 下不可解析）+ 「文件名与 id 不一致」（我用了 `WRAP-fixed.md` 且首次模拟用原名时**无**此错误）→ 证明 **PRESERVE 是唯一真实阻断项** |
| V-W-18 | ledger 计数 | 实测文件数与 status 分布 | **PASS（附 P2-005）** | `git ls-files 'doc/tasks/*.md'` = 484 − README = 483 = ledger `task files` ✓；status 表 terminal 合计 393+41+18+11+8 = **471** ✓；non-terminal 列 11 + `(none)` 1 = 12 → 合计 483 ✓（口径见 P2-005） |
| V-W-19 | 13 份受 pin 契约 | `git show --name-only` + pins | **PASS** | 本 commit 未含任何 `FEA-C0*`/`FEA-C1*` 文件；pins 13/13 与 base 同值 |
| V-W-20 | 复核期间状态完整性 | `git rev-parse HEAD` / `git status --porcelain` | **PASS** | HEAD 全程未变；工作区 clean（仅新增本报告；模拟均在 `$env:TEMP`，跑完即删） |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| **WRAP-P1-001** | **P1** | `doc/tasks/FEA-CONTRACT-WRAP-1.md:89`（Resource Manifest 第 3 行） | **`disposition: PRESERVE` 不在检查器词表内** → `done` 提交必然 FAIL，WRAP-1 无法关闭。检查器只接受 `DELETE_SAFE / MIGRATE / ARCHIVE / PRESERVE_REFERENCED / PRESERVE_USER_DATA / PRESERVE_UNKNOWN / NOT_APPLICABLE`（`check.ps1:784`；`:88` 词表在 JSON 路径另有 `ALREADY_ABSENT`）。而 `PRESERVE_UNKNOWN` 还要求 destination 存在，本行 destination 是 `-`，故**正解是 `NOT_APPLICABLE`**（该文件是仓内证据，不是待处置资源） | `check.ps1:784`/`:792`；TEMP 模拟输出「FAIL: Resource disposition 无效：PRESERVE」；改成 `NOT_APPLICABLE` 后该错误消失（V-W-16/17） | 把 `:89` 第 3 列 `PRESERVE` → **`NOT_APPLICABLE`**（其余 5 列不动）；或直接删掉该行（D06/C14 卡均只有 2 行也通过 done 门禁）。修完再跑一次 TEMP 模拟确认无真实错误 | open |
| WRAP-P2-001 | P2（非阻断，但**必须并入 done 提交**） | `doc/STATUS.md:7`、`:11`、`:20`；`doc/REBASELINE_PLAN.md:9` | 三处指针不一致：卡 = `in_review`、LEDGER = `in_review`，但 **STATUS `:7` 仍写 `in_progress`（"PLAN 预算/收尾待做"）**、**PLAN `:9` 仍写 `in_progress`**；另有两条陈旧行：STATUS `:20`「检查器债务：PLAN 行数超预算」（已不成立）、STATUS `:11`「下一候选：C-10 交互契约（U-03 已裁，**可起草**）」（已起草并 approved）。AC3 要求"三处指向真实状态"，本 head 未完全满足；`closeout-check.md` §5 的"指针一致性"表把 STATUS 记成 `in_progress` 却未标注与卡不一致 | V-W-9；STATUS `:7`/`:9`/`:11`/`:20`；PLAN `:9` | done 提交里把 STATUS `:7` 改为"当前 Task：FEA-C10-DRAFT（approved，未冻结）"、删/改 `:20`、更新 `:11`；PLAN `:9` 的 WRAP 行改 `done`（你已计划）；并在 `closeout-check.md` §5 补一句"in_review 时刻 STATUS 仍为 in_progress，done 提交同批更新"以留痕 | open |
| WRAP-P2-002 | P2（非阻断） | `verification/FEA-CONTRACT-WRAP-1/closeout-check.md`（budget 表 `PLAN-HISTORY` 行） | 记录不精确：`PLAN-HISTORY` **基线写成 4132 B，实测 4131 B**（差 1 字节）。其余数值全部核对正确：PASS(2w)、pins 13/13、STATUS 3157 B/32 行、PLAN 6777→2257、history 9504 B/79 行 | `git cat-file -s 8dfe9e371:doc/PLAN-HISTORY.md` = **4131**；head 文件 = 9504 ✓ | 把 4132 改 4131（或标"≈4.1 KB 量级"）。轻微，但本表是 AC2 的核心证据，数字应与实测一致 | open |
| WRAP-P2-003 | P2（非阻断） | `doc/checkpoints/AUTONOMOUS-2026-11-01.md:25`（队列行 5）、`:45`–`:55`（收尾节） | ①行 5 HEAD 列写「**in_review**（收口材料见下一行补记）」，但第 5 行已是表尾、**没有"下一行"**（悬空引用），且缺 HEAD hash `6c0195437`；②收尾节「**队列 5 项全部完成**」早于第 5 项 in_review→done 完成；③存在**两个** `## 收尾` 标题（`:45`「收尾（2026-11-01）」与 `:53` 空占位） | V-W-12/15；checkpoint `:25`、`:45`、`:53` | done 提交同批：行 5 HEAD 填 `6c0195437`、删「见下一行补记」、问题列填复核结论；收尾句改"队列 5 项均已交付（第 5 项已收口为 done）"；合并/删除空占位 `## 收尾` | open |
| WRAP-P2-004 | P2（非阻断） | `doc/PLAN-HISTORY.md:62`（迁入块内空行）、`:43`–`:45`（迁入说明）；`doc/REBASELINE_PLAN.md:14` | ①迁入块**原样继承**了旧 PLAN 表格内的空行（base 第 22 行，现 `PLAN-HISTORY:62`）→ 历史表被切成两段，**后半 17 行（`:63`–`:79`）在 GFM 下将渲染为无表头的裸文本**。这是"原样"要求的必然结果，**不要改这 31 行**；②措辞不精确：迁入块被称为"终态节点"，但其中至少 2 行并非终态 —— `NEW-MANGA-V1-FULL-AUDIT`（`blocked`，且同时保留在 PLAN 当前 DAG `:12`）、`GIT-CLEAN-*`（`in_review/ready/proposed/approved`，Rust 线冻结） | V-W-6（31/31 一致含该空行）；`PLAN-HISTORY:62` 为空、`:63` 起为无表头数据行；PLAN `:12` 仍有 NEW-MANGA | ①保持 31 行不动，在迁入块**之后**加一行说明（不触碰原字节）：「上文 `:62` 的空行来自旧 PLAN 原文；其后为续表（原样保留，未重排）」，并在 checkpoint 已知限制登记；②把 `PLAN-HISTORY:43`/`PLAN:14` 的"终态节点"改为「2026-10 及更早的**非活动节点**（含 1 条 blocked、1 条 Rust 线冻结快照）」 | open |
| WRAP-P2-005 | P2（非阻断，既有问题） | `doc/TASK_LEDGER.md:9`–`:14`、`:20`–`:33` | 计数口径不直观：`task files 483 = terminal 471 + non-terminal 11 + (none) 1`。status 表里 `(none) | 1 | no` 指 `doc/tasks/UIUX-FUSION-IMPL-1.md`（**该卡无 `status:` 字段**，属既有问题）；metric 块只写 `non-terminal 11`，读者按 471+11=482≠483 会以为账不平。`closeout-check.md` §5 声称"计数与磁盘一致"——磁盘一致 ✓，但缺 `(none)` 口径说明 | V-W-18；`git ls-files`=484、README 无 status 被排除、`UIUX-FUSION-IMPL-1.md` 无 status | 二选一：在 ledger 生成逻辑/metric 块显式列 `(none) 1`（需改 `task_ledger.py`，属治理工具变更，可另开 Task）；或在 `closeout-check.md` §5 加半句"483 = 471 终态 + 11 非终态 + 1 无 status（UIUX-FUSION-IMPL-1）"。**本 Task 不必修** | open |

**P0：0。P1：1（WRAP-P1-001）。** 5 条 P2 全部非阻断。

## 对 Lead 提问的逐条答复

**1. AC1 增补三条判据**：**全部通过**——5 文件死链 **0**；`:63`/`:111`/`:112`、C04b §3/§4、C08 `:55`/`:65`、C13 `:62-63`/`:74`、C09 `:68`/`:74`、C13 草案 `:203` 逐条一致；与裁定 §4 的五行为对齐；**C-08「表里有、文件里没有」的核对结论已写入注记**（`:97`），并记录了"裁定 §4 括注指向落空"而不改裁定正文（正是 R1 建议的处置）。

**2. AC2**：**通过**。`2257 B / 32 行` < 阈值；`PLAN-HISTORY` `38 0` 纯新增；**迁入 31 行与 base PLAN 第 9–39 行 31/31 逐字节相同（我自己抽了全量对比，不是抽 3–5 行）**；PLAN 保留 READY/活动程序/当前 DAG/终态约束段。

**3. AC3**：**部分通过**。两路 checker PASS(2w)、pins 13/13、ledger 一致；**但 STATUS/PLAN 仍 `in_progress`**，与卡的 `in_review` 不一致（P2-001）。`closeout-check.md` 除 `PLAN-HISTORY` 基线 4132→**4131** 1 字节偏差外（P2-002），其余数值全部与实测一致（含 start-state 的 3159 B / 6687 B / 11 非终态，我逐项复算精确命中）。

**4. checkpoint**：**真实、无虚假陈述**。5 行队列的 check/pins/报告/问题齐全（行 5 缺 HEAD，P2-003）；8 项待裁决覆盖真实遗留（与工程实际一一对应，无编造）；收尾节除"队列 5 项全部完成"措辞偏早与重复标题外，无夸大（"未 push / 13 pins 未动 / 未自审"均可复现）。

**5. 证据表 / Resource Manifest**：**证据表 4 条双口径全部验真**（逐条实算 sha256 与 commit 位置）；`-` commit + sha256 合法。**Resource Manifest：3 行表格结构 6 列合规，但第 3 行 disposition `PRESERVE` 非法 → done 门禁 FAIL（P1-001）**。这就是本轮最重要的发现：**你计划的 done 提交若"不改 Resource Manifest"，会直接 FAIL**。

**6. done 提交范围裁定（明确回答）**——你列的范围**可接受，但必须追加一项、并建议补两项**：

| 你计划的动作 | 裁定 |
|---|---|
| `status: done` | ✅ 可 |
| `integration_commit: 6c0195437` | ✅ 可（`check.ps1:743` 要求） |
| `resource_closeout_status: complete` | ✅ 可（`:746`） |
| Closeout 一行 | ✅ 可 |
| STATUS 指针 → `FEA-C10-DRAFT`（approved/未冻结） | ✅ 可（且**必须**，否则 `:633`/指针不一致） |
| PLAN 当前 DAG 的 WRAP → done | ✅ 可（注意重算字节，勿让 PLAN 回涨超 5600 B——当前 2257 B，余量很大） |
| checkpoint 第 5 行回填 | ✅ 可（按 P2-003 一次性补齐 HEAD/措辞/重复标题） |
| TASK_LEDGER 重生成 | ✅ 可（`--write`） |
| **不改 AC 正文 / 证据表** | ✅ **正确**——AC 已 `<<MET>>` 且经本轮核验；证据表 4 条已验真 |
| **不改 Resource Manifest** | ❌ **必改**：第 3 行 `PRESERVE` → `NOT_APPLICABLE`（P1-001 的修法）。这是**唯一必须突破原范围**的一处 |
| 建议追加（可选） | `delivery_head: 6c0195437`（与 integration 同值，便于追溯）；STATUS `:20`/`:11` 两条陈旧行按 P2-001 一并更新；`closeout-check.md` 4131 修正（P2-002） |

**明确不越界的部分**：不得改 AC 正文与证据表（已核验正确，改动会改变被批准字节）；不得动 13 份受 pin 契约；不得改 Gate 状态；不得 push。

**7. 三命令 + pins**：`check.ps1` PASS(2w)/0 ×2；`verify_pins.ps1` 13/13/0；13 份受 pin 契约在本 commit 内 0 改动。

## Architecture / Verification 分面结论

- **Architecture：不通过（1 项机制缺陷）**。AC1 增补三条全部成立；AC2 是**教科书级合格**（预算达标 + 逐字节原样迁移 + 当前状态未丢）；AC3 的机器侧通过、指针侧未同步；证据与 checkpoint 的主体真实。唯一阻断项是 **Resource Manifest 的 disposition 词表不合规**——它会让 done 门禁 FAIL，属"提交即失败"的机制缺陷，与内容真实性无关。
- **Verification：两路 PASS，但 done 门禁模拟 FAIL**。V-W-1…V-W-8、V-W-11、V-W-13、V-W-14、V-W-18…V-W-20 为 PASS；V-W-9（指针）部分失败；**V-W-16 done 门禁 FAIL → P1**；V-W-17 证明修掉 disposition 后唯一剩余为模拟环境伪错误。

## 结论与复审

**decision：`changes_requested`**（P0 × 0 / **P1 × 1** / P2 × 5）。P1 未闭合，不得 `approved`，**也不得先做 done 提交**（会 FAIL）。

**唯一阻断项**：`doc/tasks/FEA-CONTRACT-WRAP-1.md:89` 的 `PRESERVE` → `NOT_APPLICABLE`（一词）。这是机械修正，不改变任何交付内容；改完后 done 门禁即可通过（V-W-17 已证明）。

**复审要求（R2，只需极短）**：

1. 修 P1-001（一词），并按 P2-001/003 在 done 提交里补齐 STATUS/PLAN/checkpoint（这本来就是你的计划）。
2. 把 done 提交 + P1 修正一起给我新 head，我做 R2 极简复审：**TEMP 再模拟一次 done 门禁**（应只剩路径伪错误）+ 三命令 + 13 pins + 三处指针一致 + AC 正文与证据表字节未变。预计数分钟，不重开 AC1/AC2 已通过项。
3. 若你选择**先修 P1、再让我确认、最后才做 done**，也完全可以（更稳）：R2 通过后你再提交 done。

**给最终回复留的素材**：本段全部 commit **未 push**（`git status` clean、无远端写）；13 pins 13/13 未动；用户在线后待裁决 8 项（见 checkpoint）；**C-10 仍未冻结**（待用户裁定阈值 `T`）——这是当前唯一阻塞"契约线完全收口"的外部条件。

—— 报告结束（`decision: changes_requested`；P1×1 = Resource Manifest disposition 非法导致 done 门禁 FAIL；P2×5 非阻断；AC2 逐字节迁移与证据双口径均已独立验真）。
