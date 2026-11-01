---
task_id: task-3
document_id: FEA-C14-CLOSEOUT-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-3"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead（DSH 主会话，Lead / Architect / Integrator）
base_commit: 1ca385d67
reviewed_head: ff432e97c
reviewed_head_full: ff432e97ce1d23c3d6014d9368b0cf5fadf82bd2
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == ff432e97ce1d23c3d6014d9368b0cf5fadf82bd2）；工作区 clean（git status --porcelain 空）"
repository: G:/CODEX/New Manga
source_branch: main
scope: "FEA-C14-DRAFT 收口材料：status→in_review、AC6 事实更正、AC5/AC6 粘行修复、Canonical Evidence 4 行、Resource Manifest 两行 + 偏离登记、verification/FEA-C14/closeout-note.md 新增、TASK_LEDGER 同步"
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 6
reviewed_sha256:
  doc/tasks/FEA-C14-DRAFT.md: 15e8dedb97ec6fab28bf1c6b27a49162ef6bb45ce024aabc2cbb55890f1b403e
  verification/FEA-C14/closeout-note.md: 8cf2deb6b198a8f4072eb3dcfa0ea232dfe517f999f71e61bf62f1225f475907
  doc/TASK_LEDGER.md: 6cbf6db0c5bdeb076ff044a8e84293c0848d9c162c9c142477b5504956b45b3a
  doc/STATUS.md: fad72c3f258ef2651643062731bb089efc1ced6ff91f9d745e75e0c6964578ac
  doc/REBASELINE_PLAN.md: 61fe90ef528bd3eb23a2362a2d6c789dce3380afac92a4f20359f62c06a10c65
scope_note: >-
  被审任务描述提到「同 commit 的 doc/STATUS.md / doc/REBASELINE_PLAN.md / doc/TASK_LEDGER.md / checkpoint 改动」；
  实测 `git show --name-status ff432e97c` 只有 **3 个文件**（task card、verification/FEA-C14/closeout-note.md、doc/TASK_LEDGER.md），
  STATUS / PLAN / checkpoint **均未在本 commit 修改**。本报告按实测 diff 复核，并把该出入记入 P2-1。
checkps1: "PASS（3 warnings），EXIT=0；默认调用与 -TaskPath doc/tasks/FEA-C14-DRAFT.md 两种调用均实跑，输出一致"
verifypins: "PASS (all 13)，EXIT=0；C14 pin = 05056cbf65f950bc1fdfd1632e6e065bb3f65cb8b75e5e9843d2384430b749e9，与 draft 实算一致；FROZEN-C14 = a34d0f2a…，与本卡 E-C14-FROZEN 一致"
independence_note: >-
  本复核与被审产出为不同上下文（DSH 主会话 vs 独立 teammate），不构成自审。
  披露：4 条 Canonical Evidence 中 3 条（FEA-C14-r1 / FEA-C14-r2 / FEA-CONTRACT-FROZEN-C14）与本人早前复核/冻结链相关，
  其中 r1、r2 两份复核报告由本人（c01b-reviewer）出具。本轮只裁定「收口材料是否忠实、准确、可复现」以及「AC6 更正是否属事实更正」，
  不为既有 Review 重新出具批准，也不因作者身份放宽标准；我对自己 r2 的 `approved` 仍按原文引用，未追认任何超出其 scope 的结论。
conditional_approval: >-
  本批准只对 ff432e97c 的字节有效。随后的 `done` 提交应为**纯元数据回填**（status / integration_commit / resource_closeout_status / Closeout 一行 / STATUS 指针迁移 / TASK_LEDGER）；
  若该提交改动 AC 正文、证据表或资源清单内容，按 09 §6「分支随后变化不延用旧批准」，本批准失效并须新 head 复审。
captured_at: 2026-11-01T12:33:00+08:00
captured_by: c01b-reviewer
---

# Review：FEA-C14-DRAFT 收口（R1）

## 范围与依据

本 Review 只对 `base_commit: 1ca385d67`（D06 关闭提交）→ `reviewed_head: ff432e97c` 有效。复核全程 HEAD 未前进、工作区 clean。

**被审 diff（实测全量，3 文件 +63/−23）**：

```text
 doc/TASK_LEDGER.md                    |  6 ++---
 doc/tasks/FEA-C14-DRAFT.md            | 51 +++++++++++++++++++++--------------
 verification/FEA-C14/closeout-note.md | 29 ++++++++++++++++++++
```

> **与任务描述的出入（如实记录）**：任务描述写「同 commit 的 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md` / checkpoint 改动」，但 `git show --name-status ff432e97c` 只有上述 3 个文件，STATUS / PLAN / checkpoint 未改。本报告的复核按实测 diff 进行，该出入本身进入 P2-1。

**依据**：`AGENTS.md`（发现事实与文档不一致须留证据；历史 Review/署名不改写）、[09 协作协议](../09_COLLABORATION.md) §4（状态机）、§4.1（每个已释放 AC/Gate 指向一个当前证据项；commit **或** SHA-256）、§4.2（Resource Manifest、allowed_paths、`done` 前门禁）、§4.3（AC 标记）、§6（批准不延用到新 head）、[R1/R2 在 D06 上的同型先例](FEA-D06-CLOSEOUT-r2.md)、`tools/governance/check.ps1`（只读阅读判定逻辑）。

**未审到的部分**：AC1–AC5 与方案 `:432`/`:459`/`:461`、C-01b/C-06/C-04b 的条款级逐字对照（仍 NOT_RUN，与 Task 自述一致；我只抽查了证据链与冻结字节）；r1/r2 复核结论的语义正确性（引用其 frontmatter 结论，不重做判定）；C-14 契约条款本身的语义（不在本轮范围）。

## Architecture

1. **AC6 的更正属于「事实更正 + 证据指针对齐」，不是改判。** 原 AC6 声称「`doc/reviews/FEA-C14-r1.md`（`approved`，P0/P1 = 0）」；实测 r1 的 frontmatter 为 `verdict: changes_requested`、`p1_count: 5`、`p2_count: 4`；r2 才是 `approved`、`p0=0/p1=0`。更关键的是：**权威冻结记录本身早已写对**——`doc/plan/FEA-CONTRACT-FROZEN-C14.md:36` 写「r1（**5 P1**）→ r2 approved（0 P0/P1）」。所以原 AC6 是**卡片创建时的陈旧错误**（`f449dfab8` 建卡时写入，当时 r1 尚不存在），并非对某个已被批准的判断做反向改写。AC6 的**规范性要求**（"独立复核 `approved`（P0/P1 = 0）后由 DSH 冻结"）一字未变，改动只在"哪一轮/哪份文件满足它"与 r1 的真实状态。
2. **旧卡的结构缺陷被修掉**：base 的 AC5 行尾带有字面 `\n`，把 AC6 粘成同一物理行（AC 行数因此少一条）。head 已拆为两条独立 AC 行，实测 `literal '\n'` 残留 **0**，6 条 AC 各占一行且行末均为 `<<MET>>`（check.ps1 §4.3 正则依赖"每 AC 一行"，此修复是必要的）。
3. **证据链完整且可复现**：4 条 evidence 我在 commit blob 与 worktree 双口径重算，全部逐字一致；3 条 commit 型 evidence 的 commit 均为 head 祖先且确实包含所 pin 文件；AC1–AC6 每条都有证据行覆盖（E-C14-R1→AC1–AC5、E-C14-R2→AC1–AC6、E-C14-FROZEN→AC6），满足 §4.1。
4. **资源闭环口径沿用 D06 的先例**：仓库内 `NOT_APPLICABLE` + 仓外 `PRESERVE_UNKNOWN`（引用 D06 的 32 项共享清单，本线 3 项），并附「用户口径 vs 检查器」偏离登记；`E-RES-C14` 的 `AC/Gate` 列写 `Res/Closeout`（比 D06 当初的 `Resource` 更清晰，已吸收 R2-003 的建议）。
5. **冻结字节未动**：`git diff 1ca385d67 ff432e97c -- doc/plan/` 为空；13 pins 13/13；C-14 draft 实算 `05056cbf65f9…` 与 pin 一致；FROZEN-C14 实算 `a34d0f2a…` 与本卡 E-C14-FROZEN 一致。
6. **无代码、无契约双权威复写**：本轮只改生命周期与证据登记，未复制契约正文。

## Verification（逐项，含真实输出）

环境：Windows，`pwsh -NoProfile`，workdir `G:\CODEX\New Manga`，HEAD = `ff432e97ce1d23c3d6014d9368b0cf5fadf82bd2`，工作区 clean。

| # | 场景 | 实际执行 | 结果 | 证据 |
|---|---|---|---|---|
| V-C14-1 | `check.ps1`（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings），EXIT=0** | `Task: doc\tasks\FEA-C14-DRAFT.md`；WARN：10 非终态 Task、STATUS 3156 B、PLAN 6745 B |
| V-C14-2 | `check.ps1 -TaskPath` | `… -TaskPath doc/tasks/FEA-C14-DRAFT.md` | **PASS（3 warnings），EXIT=0**（与 V-C14-1 逐字相同） | 同上 |
| V-C14-3 | `verify_pins.ps1` | `… verify_pins.ps1` | **PASS (all 13)，EXIT=0** | C14 `05056cbf65f9`；`PIN AUDIT: PASS (all 13)` |
| V-C14-4 | 4 条 evidence 双口径复算 | `git cat-file -e` / `git cat-file blob`→`$env:TEMP`→`Get-FileHash` | **PASS（4/4）** | E-C14-R1 `b91014b3…`(16685) @172eae3c8；E-C14-R2 `69ff58bf…`(11201) @e35f37603；E-C14-FROZEN `a34d0f2a…`(5265) @e35f37603；E-RES-C14 `8cf2deb6…`(1229) commit `-`。worktree 与 blob **全部一致**，3 个 commit 均 head 祖先 |
| V-C14-5 | AC 标记 | 正则统计 head 的卡片 | **PASS** | `- [x]` = 6、AC 行 6 条、**每条 `<<MET>>` 位于行末**（第 65–70 行）、`- [ ]` = 0；第 7 处 `<<MET>>` 是 Closeout 第 112 行的行内引用，非 AC 标记 |
| V-C14-6 | 字面 `\n` 粘行 | `[regex]::Matches($t,'\\n')` | **PASS（0 残留）** | 原 AC5 行尾的 `\n- [x] **AC6` 已拆分 |
| V-C14-7 | **AC6 事实更正** | 读 `doc/reviews/FEA-C14-r1.md` / `-r2.md` frontmatter + `FEA-CONTRACT-FROZEN-C14.md:36` | **PASS（更正准确）** | r1 `verdict: changes_requested` / `p0 0` / `p1 5` / `p2 4`；r2 `verdict: approved` / `p0 0` / `p1 0` / `p2 4`；FROZEN-C14 `:36` 早已写「r1（5 P1）→ r2 approved（0 P0/P1）」 |
| V-C14-8 | 测试表诚实性 | 读测试表 | **PASS** | AC1–AC5 = `NOT_RUN（本收口不重跑条款级对照）` + 注（`:88`）；AC6 = `PASS` + r2 frontmatter 依据。未把未跑写成 PASS |
| V-C14-9 | Resource Manifest | 读 `:99`–`:108` | **PASS（结构）** | 两行 6 列：`doc-task/NOT_APPLICABLE`（仓库内）、`temp-scripts/PRESERVE_UNKNOWN`（仓外）；integrity = `verification/FEA-D06-GAP/workspace-tmp-manifest.md`；`:103` 偏离登记在位 |
| V-C14-10 | **`done` 门禁模拟** | 复制 head 卡片到 `$env:TEMP\FEA-C14-DRAFT.md`，改 `status: done` / `integration_commit: ff432e97c` / `resource_closeout_status: complete`，跑 `check.ps1 -TaskPath` | **PASS（EXIT=0，0 errors）** | 输出 `Governance check: PASS (3 warnings)`；说明 4 条 evidence、两行 manifest、`evidence_dir` 扫描在 `done` 分支全部通过。阴性对照：把 integrity 改成不存在文件 ⇒ `FAIL: Resource manifest 不存在`（EXIT=1）→ 门禁确实在跑 |
| V-C14-11 | 跨 Task 引用可解析 | 读 D06 共享清单 | **部分成立（见 P2-2）** | 清单内**条目** `#18 fix_c14_r1.py` / `#19 fix_c14_r2.py` / `#20 c14_sha.txt` 存在；但它们在**文件第 30–32 行**，卡片与 closeout-note 均写「第 18–20 行」（那 3 行实为 `#6 fix_r11.py` / `#7 fix_s7.py` / `#8 sync_c08_records.py`） |
| V-C14-12 | `evidence_dir` | `Get-ChildItem verification/FEA-C14` | **PASS** | 唯一文件 `closeout-note.md`（1229 B）= E-RES-C14，无未登记文件 |
| V-C14-13 | 写集合 3/3 | 逐项对 head 的 `allowed_paths`（`:22`–`:30`） | **PASS（3/3）** | `doc/tasks/FEA-C14-DRAFT.md`←`:22`；`doc/TASK_LEDGER.md`←`:27`；`verification/FEA-C14/closeout-note.md`←`:30`（`verification/FEA-C14/**`） |
| V-C14-14 | 冻结字节 / 13 pins | `git diff 1ca385d67 ff432e97c -- doc/plan/`；pins | **PASS** | `doc/plan/` diff 为空；13/13 PASS；C14 draft `05056cbf65f9…`；FROZEN-C14 `a34d0f2a…` |
| V-C14-15 | 三处指针一致性 | 读 STATUS/PLAN/LEDGER | **FAIL（见 P2-1）** | 卡片 `in_review`、`TASK_LEDGER.md:43` `in_review`；但 `doc/STATUS.md:7` 与 `doc/REBASELINE_PLAN.md:48` 仍为 **`in_progress`**（本 commit 未改这两份） |
| V-C14-16 | TASK_LEDGER 计数真实性 | 读 summary + `git ls-files` | **PASS** | `non-terminal tracked by git = 10`（与 check.ps1 的 10 一致）；各状态计数和 = 481 = tracked Task 文件数（含 README 时 482） |
| V-C14-17 | 前置 D06 关闭是否符合我的 R2 条件（旁证） | `git diff 1027de616 1ca385d67 -- doc/tasks/FEA-D06-GAP.md` | **PASS（旁证，不在本轮范围）** | D06 done 提交对被审正文仅改了 `status` / `integration_commit` / `resource_closeout_status` + 1 行 Closeout；符合我在 D06-R2 设的 `conditional_approval`（纯元数据回填） |
| V-C14-18 | 复核期间状态完整性 | `git rev-parse HEAD` / `git status --porcelain` | **PASS** | HEAD 全程 `ff432e97c`；工作区 clean（本 Review 只写了本文件） |

**模拟方法披露（证据纪律）**：V-C14-10 只能对"状态改后的副本"验证（`check.ps1:742` 的 Resource Manifest 分支仅在终态或 approved+integration_commit 时执行）。副本只写入 `$env:TEMP`（仓库外），**仓库内文件未被修改**，跑完即删除。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| C14-R1-001 | **P2（非阻断）** | `doc/STATUS.md:7`、`doc/REBASELINE_PLAN.md:48` | 三处指针不自洽：卡片与 `TASK_LEDGER.md:43` 已是 `in_review`，但 STATUS 与 PLAN 仍写 `in_progress`。STATUS 是"唯一 Active Task 与运行状态权威"，读者会看到两个阶段；本 commit 只同步了 ledger，反而让三者内部矛盾。`check.ps1` 只在 STATUS 指向**终态** Task 时报错（`:633`），抓不到阶段不符 | `git show --name-status ff432e97c` 无 STATUS/PLAN；`git diff` 中 `TASK_LEDGER.md` 已 `in_review`；`STATUS:7`/`PLAN:48` 仍 `in_progress` | 与 D06 的 R-004 同型：`done` 提交必须把 STATUS 指针迁走（否则 `check.ps1:633` FAIL）并在同一提交把 PLAN `:48` 改为 `done`；如需在 `in_review` 阶段就一致，可本批补一个纯元数据提交 | open |
| C14-R1-002 | **P2（非阻断）** | `doc/tasks/FEA-C14-DRAFT.md:101`、`verification/FEA-C14/closeout-note.md:25` | 跨 Task 清单引用写成「**第 18–20 行**」，按文件行号读到的却是 `#6 fix_r11.py` / `#7 fix_s7.py` / `#8 sync_c08_records.py`；目标内容的真实位置是**清单条目 `#18`–`#20` = 文件第 30–32 行**。引用可经"条目编号"歧义恢复，但按字面"行"会找错 | `Get-Content verification/FEA-D06-GAP/workspace-tmp-manifest.md`：`line 30 = #18 fix_c14_r1.py`、`line 31 = #19 fix_c14_r2.py`、`line 32 = #20 c14_sha.txt`；`lines 18–20` = `#6/#7/#8` | 两处都改为「清单条目 `#18`–`#20`（文件第 30–32 行）」；后续 task 引用同一清单时统一用条目号 | open |
| C14-R1-003 | **P2（非阻断）** | `doc/tasks/FEA-C14-DRAFT.md:11`–`:12`（`depends_on: FEA-GOV-11`） | 依赖未对账：`FEA-GOV-11` 仍 `in_progress`（其 AC1/AC2 标 `<<PARTIAL: 待用户裁决>>`），而 C-14 契约已冻结、`G-CONTRACT` 已关闭。`check.ps1` **完全不校验 `depends_on`**（`Select-String depends_on` 命中 0），所以 PASS 不覆盖此项。`done` 前若不说清依赖如何满足，会出现"依赖未完成的任务已关闭" | `doc/tasks/FEA-GOV-11.md:6 = in_progress`、`:47`–`:49` PARTIAL；C14 卡 `:11`–`:12`；`check.ps1` 无 depends_on 校验 | 在 Closeout 增一行「依赖对账」：说明 GOV-11 的 4 项用户裁决（R / U-04 / U-05a / U-05b）与 C-14 无关，C-14 的冻结前置已由 `e35f37603` + `G-CONTRACT` CLOSED 满足；或把 `depends_on` 改为已满足的引用。**建议在 `done` 提交前完成**（纯记录性，不改代码/契约） | open |
| C14-R1-004 | **P2（非阻断）** | `verification/FEA-C14/closeout-note.md:25` | `PRESERVE_UNKNOWN` 的保留理由引用了 **D06 的** `add_c08_d06.py`（不在本线这 3 个文件内），而本线 3 项中真正动过被冻结字节的是 `fix_c14_r1.py` / `fix_c14_r2.py`——两者都直接改写 `doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md`（即后来 pin 到 `05056cbf…` 的字节）。结论（PRESERVE_UNKNOWN）正确，但理由与文件不匹配，弱化了记录的可核查性 | `Select-String -Path fix_c14_r1.py/fix_c14_r2.py -Pattern "p = "` ⇒ 均 `doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md`；closeout-note `:25` 原文引 `add_c08_d06.py` | 改为「本线 `fix_c14_r1.py`/`fix_c14_r2.py` 直接改写过 C-14 草案字节（v2/v3），删除会降低冻结字节可复现性；共享清单整体保留理由另见 D06 清单开头」 | open |
| C14-R1-005 | **P2（非阻断）** | `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md:20` | 预算余量更紧：STATUS **3156 / 3200 B（98.6%）**、32/45 行；PLAN **6745 / 7000 B（96.4%）**、57/64 行。`done` 提交还要改 STATUS（迁指针）与 PLAN（`:48`），**任何净增都会触发预算 FAIL**。另：STATUS `:20`「检查器债务：PLAN 行数超预算」仍不成立（57<64 行、6745<7000 B），是过期陈述（D06-R2 的 R2-005 遗留未处理） | `check.ps1` 的 3 warnings；`check.ps1:614`–`:615` 预算；STATUS 实际字节数与行数 | `done` 提交对 STATUS/PLAN 做**净零或净减**改写；顺手把「PLAN 行数超预算」更新为当前真实债务或删除 | open |
| C14-R1-006 | **P2（非阻断）** | `doc/tasks/FEA-C14-DRAFT.md:70`、`:114` | AC6 更正本身合法（见下"Q1 裁定"），但建议把**文书原则**写清：Task 卡片（未冻结、生命周期内、错误被权威物证反驳）可**就地更正 + 留痕**；而冻结契约 / Gate 裁定 / Review 结论 / evidence pin 属"历史不可改写"类，才必须**追加 Errata**。当前 `:114` 只说"更正为 r1→r2 链并在此留痕"，未写原则，后续（尤其 L-3 Errata）容易两套做法混用 | 卡片 `:70`（新 AC6）、`:114`（事实更正留痕） | 在 `:114` 后补一句原则说明；AC6 也可考虑保持"规范性要求"为主句、把 r1 历史细节留在证据表（E-C14-R1 已在），减少 AC 行携带会过期的历史 | open |

**P0：0；P1：0。** 6 条 P2 **全部非阻断**，不阻止进入 `done`；其中 **C14-R1-001 与 C14-R1-005 必须在 `done` 提交内处理**（否则 STATUS 指针未迁走会让 `check.ps1:633` FAIL、预算也可能 FAIL）。

### 对 Lead 6 个提问的裁定

**Q1（AC6 事实更正是否合法：纠正引用错误 vs 改 AC 内容/改判）**：**合法，属"事实更正 + 证据指针对齐"，不是改判。**
- **原文是错的**：r1 实测 `changes_requested`（P1×5 / P2×4），不是 `approved`；且`FEA-CONTRACT-FROZEN-C14.md:36`（权威冻结记录）从一开始就写「r1（5 P1）→ r2 approved（0 P0/P1）」。所以原 AC6 与"权威物证"直接矛盾，是 `f449dfab8` 建卡时（r1 尚未产出）留下的陈旧声明。
- **AC 的规范内容没有被改**：AC6 的要求是"独立复核 `approved`（P0/P1 = 0）后由 DSH 冻结"——这句一字未动；被改的只是"哪一轮/哪份文件满足它"以及 r1 的真实状态。r2 确实 `approved`（p0=0/p1=0，p2=4 非阻断），更正后陈述准确。
- **留痕到位**：Closeout `:114` 明确写"原 AC6 写 r1 approved 与事实不符…本收口更正为 r1→r2 链并在此留痕"，且证据表同时保留 `E-C14-R1` 与 `E-C14-R2`——错误没有被抹掉历史，而是被标注并保留两条证据。
- **为什么不必改成「保留原文 + 追加 Errata」**：本仓库的"不改写"纪律约束的是**历史证据类**制品（Review 报告、日志、evidence pin、冻结契约字节——AGENTS.md「历史 Review 与署名不改写」、任务卡「不改冻结字节」）。Task 卡片不是冻结字节，且它**没有**任何被批准过的基线：错的是引用，不是判断。若保留错误 AC 原文再加注，会让一条**错误的证据引用**继续以 `<<MET>>` 形式出现在 AC 列表里，反而更容易被后续引用。**推荐保持现状（就地更正 + 留痕）**，并补 C14-R1-006 的原则句。
- **对 3 号任务（L-3 Errata）的直接结论**：你说的「只追加注记、不删原文」对 **L-3 这类冻结/裁定正文**是**正确**的——那是"历史不可改写"类；**不要**因为 C14 这次就地更正而反过来改成只在卡片上加注。两类制品的正确做法不同，请按"是否冻结/是否已被批准为权威"分流。

**Q2（`E-RES-C14` 用 `-` commit + sha256 是否满足 §4.1）**：**满足，与 D06 的 `E-RES` 同口径。** §4.1 允许"含该文件的 commit，**或**仓外/原始输入的 SHA-256"；`check.ps1:672`–`:674` 把 `-` 归一为空 commit 后要求"commit 或 sha 至少其一"，`:686`–`:714` 对 worktree/blob 双口径校验。实跑 PASS（V-C14-1）。补充：该文件已在本 commit 内，`blob@ff432e97c` 的 sha256 就是 `8cf2deb6…`，等价于 commit+sha 双绑定。**保持现状，不建议回填 commit**（会造成改表→改文件→改 sha 的自指循环，且使 `done` 不再是纯元数据提交）。

**Q3（跨 Task 引用 D06 的 `verification/FEA-D06-GAP/workspace-tmp-manifest.md` 是否可接受）**：**可以接受，但有两点要求。**
- **可接受**：§4.1 只要求 evidence 项"记录仓库相对路径 + commit 或 SHA-256"，未禁止跨 Task 引用；`check.ps1` 的 `Resource Manifest` 校验对 integrity 只做"路径存在且为文件"（`:804`–`:806`），不校验归属；`evidence_dir` 扫描只针对 `verification/FEA-C14`（`:719`–`:737`），因此把 C14 的说明放在自己目录、把**共享清单**放在 D06 目录不会互相污染。`done` 模拟实测通过（V-C14-10）。
- **要求 1（必须修）**：引用位置写成"第 18–20 行"是错的，应写"清单条目 `#18`–`#20`（文件第 30–32 行）"——见 C14-R1-002。
- **要求 2（建议）**：该清单是 **D06 的 `evidence_dir` 内文件**，其内容由 D06 的证据表（`E-RES`）登记。C14 只是**引用方**，不是所有者 → 若后续有人编辑该清单（例如新增条目），C14 的引用会指向变化的行号。建议在 C14 卡片里写明"引用 D06 清单的**条目号**（而非行号）"，并接受该清单可能增长。若你更希望强隔离，替代方案是让 C14 的 closeout-note 自带这 3 项的 sha256（已部分具备：清单里现在没有逐项重复，但可以补），代价是两处需要同步。

**Q4（写集合 3/3 是否都在 allowed_paths）**：**是，3/3**（V-C14-13）。`doc/TASK_LEDGER.md` 在 `:27`，`verification/FEA-C14/**` 在 `:30`，task card 在 `:22`。注意：本 commit 新增的两个 allowed_path（`doc/plan/FEA-CONTRACT-FROZEN-C14.md`、`doc/checkpoints/**`）本轮**未被使用**——不是缺陷，但说明它们是"为收口预留"；`done` 提交若用到，已在授权内。

**Q5（三命令 + 13 pins）**：**全通过**（V-C14-1/2/3/14）：两路 `check.ps1` PASS/EXIT 0；`verify_pins.ps1` 13/13 PASS/EXIT 0；C-14 draft 实算 `05056cbf65f9…` 与 pin 一致；`FROZEN-C14` `a34d0f2a…`；`git diff -- doc/plan/` 为空。

**Q6（是否有 P0/P1）**：**无 P0、无 P1**。6 条 P2 全部非阻断；`done` 前需处理 C14-R1-001（STATUS/PLAN 指针）与 C14-R1-005（预算净零），二者都是纯元数据动作。

### 旁证：D06 的 `done` 提交符合我在 R2 设的条件

顺手核了 `1ca385d67`（base）：它对我 R2 批准的那个 head 只改了 `status: done`、`integration_commit: 1027de616`、`resource_closeout_status: complete` 与 1 行 Closeout，未动 AC/证据表/资源清单正文 → 符合 D06-R2 的 `conditional_approval`（纯元数据回填）。这一点**不属于本轮被审范围**，仅作闭环留痕。

## Architecture / Verification 分面结论

- **Architecture：通过**。AC6 更正是有权威物证支持的事实更正，规范性要求未变且留痕完整；AC 行结构缺陷已修；4 条证据双口径可复现且覆盖 AC1–AC6；资源口径与 D06 先例一致并已登记偏离；冻结字节与 13 pins 未动；3/3 写集合在授权内。架构侧仅存治理卫生项（P2-1…P2-6）。
- **Verification：通过**。两路 `check.ps1` PASS/EXIT 0、`verify_pins.ps1` 13/13 PASS/EXIT 0、4 条 evidence 双口径一致、6/6 AC 标记合规且零 `\n` 残留、`done` 门禁经模拟+阴性对照验证可用、`evidence_dir` 无未登记文件、`doc/plan/` 零改动。NOT_RUN 项（AC1–AC5 条款级对照）如实保留、未被写成 PASS。

## 结论与复审

**decision：`approved`**（P0 × 0 / P1 × 0 / P2 × 6，全部非阻断）。

收口材料真实可复现，且本轮的"AC6 事实更正"经我独立比对 r1/r2 frontmatter 与冻结记录 §:36 后确认为**必要且准确的纠错**，未改变 AC 的规范含义，也未触碰冻结字节。可交 DSH 进入 `done`。

**`done` 提交的机械前置（代码依据）**：

1. `check.ps1:633`：`done` 后 STATUS 的「当前 Task」指针必须迁走，否则默认调用 `FAIL: STATUS 仍指向终态 Task`。（同时把 `PLAN:48` 更新为 `done`，避免 V-C14-15 的不一致延续。）
2. `check.ps1:743`/`:744`/`:746`：`integration_commit` 非空、`canonical_evidence_status: complete`、`resource_closeout_status: complete`——前两项已满足，第三项待回填。
3. 预算：STATUS 3156/3200 B、PLAN 6745/7000 B，`done` 提交需**净零或净减**（C14-R1-005）。
4. 建议同批处理 C14-R1-003（依赖对账一行）与 C14-R1-002（引用改条目号），二者都只改本 Task 卡。

**复审通道**：若 `done` 提交超出"纯元数据回填"（改 AC/证据/资源清单正文），请把我列入新 head 复审；若同时修 P2-2/P2-3/P2-4 的文字，也一并送审更稳妥（可复用本报告 ID）。

—— 报告结束（`decision: approved`；P0×0 / P1×0 / P2×6 非阻断；条件：`done` 仅元数据回填 + STATUS 指针迁移 + 预算净零）。
