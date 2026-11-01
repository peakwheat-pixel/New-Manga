---
task_id: task-13
document_id: FEA-01-FREEZE-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-13"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh-lead（DSH 主会话，Lead / Architect / Integrator）
base_commit: a2bda2f1d
reviewed_head: b0aa7cb6a
reviewed_head_full: b0aa7cb6adb9effc6c63bf5e9e2eb219bb0696bc
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == b0aa7cb6adb9effc6c63bf5e9e2eb219bb0696bc）；工作区 clean"
repository: G:/CODEX/New Manga
source_branch: main
scope: "A：FEA-01 稳定端口冻结 v2（门禁链 4/4、pin、§1B、稳定端口唯一载体、pins 15/15）；B：FEA-02-CORE 范围卡（写域、AC、L 判定、状态/阻塞、ready 前置）"
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 5
reviewed_sha256:
  doc/plan/FEA-01_CONTRACT_DRAFT.md: 0370c18932b14baf47697c92a38909c2886475305e8c539799d63c074967cfd5
  doc/plan/FEA-CONTRACT-FROZEN-FEA01.md: d15105898a7ce99139fe5467275b5233970a9ad53fd4358e96ede5448c258e77
  doc/tasks/FEA-02-CORE.md: 8eba366a9ae5b9e7efda1afdcb0b3f4d869fbdc612c3495630db76fcc8b2d5a6
checkps1: "PASS（2 warnings），EXIT=0；默认与 -TaskPath doc/tasks/FEA-02-CORE.md 两路一致（WARN：12 非终态、STATUS 3171 B）"
verifypins: "PASS (all 15)，EXIT=0；14 份既有 pin 值与冻结前逐一相同；FEA01 = 0370c18932b1"
freeze_pin_dual: "worktree == git blob == 记录 §1 == 0370c189…（三者独立复算一致）；15251 B / 134 行"
same_defect_check: >-
  无重复问题。P1-001 是新类型（**门禁链声明的证据缺口**，不是字节/格式问题）；P1-002 是 B 线**范围冻结本身的执行性缺口**（写域不含解决方案文件）。
  两条都不是我前几轮提过的问题的重演，故按现行标准判 P1。
independence_note: >-
  本复核与被审产出为不同上下文（DSH 主会话 vs 独立 teammate），不构成自审；未参与本 Task 的实现/返修，未修改任何被审文件（仅写本报告）。
captured_at: 2026-11-01T19:32:48+08:00
captured_by: c01b-reviewer
---

# Review：FEA-01 冻结（A）+ FEA-02-CORE 范围卡（B）

## 范围与依据

本 Review 只对 `base_commit: a2bda2f1d` → `reviewed_head: b0aa7cb6a` 有效。复核全程 HEAD 未前进、工作区 clean。

**实测提交（12 文件 +346/−16）**：`doc/plan/FEA-01_CONTRACT_DRAFT.md`(+36/−?)→ FROZEN v2、`doc/plan/FEA-CONTRACT-FROZEN-FEA01.md`（新 62 行）、`verification/FEA-01-FREEZE/closeout-check.md`（新 44 行）、`tools/governance/verify_pins.ps1`（+FEA01）、`doc/tasks/FEA-01-FREEZE-1.md`（新 82 行）、`doc/tasks/FEA-02-CORE.md`（新 107 行）、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`、`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md`(+3，U-12)、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/checkpoints/AUTONOMOUS-2026-11-01.md`。**无代码文件改动。**

**依据**：用户追加裁决 **U-12**（ADJ `:66`，19:25 确认）；ADJ 主表 6 项（`:15`–`:20`）；方案 §15.6 候选表（`:921` FEA-02-CORE 行）；FEA-01 §1 冻结顺序 / §3 待决项；C-07 冻结记录与 `FEA-C07_API_INVENTORY.md`；`check.ps1:636`–`:655`（READY 节点与 DAG 校验）、`:816`–`:852`（AC 标记）；`verify_pins.ps1:6`–`:26`。

## A. FEA-01 稳定端口冻结

### Architecture

1. **字节与 pin 三口径一致**：`worktree` = `git blob` = 记录 §1 = **`0370c18932b14baf47697c92a38909c2886475305e8c539799d63c074967cfd5`**；15251 B / 134 行与记录一致；§1A 记「无修正」（首次计算即终值）✓。
2. **§1B 披露与真实 diff 完全对应**：真实 diff 恰 5 组（状态行 / §1 门禁链 3 行 + 证据链接 / §2 说明段 / 新增 §2A / 变更记录 1 行），记录 §1B 逐项列 ①–⑤ 一一对应，**无未披露改动、无新增/删除变更包** ✓。
3. **稳定端口唯一载体**：`§2A` 明写「C-07「应用端口与兼容面」由 `FEA-C07_API_INVENTORY.md` 承载（pin `17c8f7016a36…`，方法清单由代码生成、替换旧「36」口径）…**不另起第二份端口清单**」；与 C-07 清单首段（`:9`）「本文件即该清单基线，替换冻结文档中的「36」口径」及「36/47/57 三种计数不得互相替代」（`:11`）**口径一致** ✓。
4. **pins 15/15 且 14 份旧值未变** ✓；两路 `check.ps1` PASS ✓；第 5 步「Task 释放」如实标 ⛔ 未发生 ✓。
5. **但门禁链第 1 步的证据链有缺口（P1-001）**：冻结字节 §3 的八行状态列**全部仍写「待你裁决」**（U-03…U-08，`:100`–`:105`，其中 U-06/U-07/U-08 为离线阅读/外部卷/凭据字体备份），而状态行与记录 §2 宣称「门禁链 4/4」且第 1 步 =「用户裁决（§3 待决项）✅」。→ 冻结文档自相矛盾：一边说门禁过了，一边列着 6 项待裁决。

### Verification（A，含真实输出）

| # | 场景 | 实际执行 | 结果 | 证据 |
|---|---|---|---|---|
| V-A-1 | **pin 双口径** | `Get-FileHash`（worktree）＋ `git cat-file blob b0aa7cb6a:…`→temp→`Get-FileHash` | **PASS** | 三者同为 `0370c189…`；15251 B / 134 L |
| V-A-2 | 记录 §1 值与实测 | 读 `FEA-CONTRACT-FROZEN-FEA01.md:16`–`:17` | **PASS** | 与实测一致 |
| V-A-3 | **§1B vs 真实 diff** | `git diff a2bda2f1d b0aa7cb6a -- doc/plan/FEA-01_CONTRACT_DRAFT.md` 全读 | **PASS（5/5 已披露）** | ①状态行 DRAFT→FROZEN v2 ②§1 门禁链标 4/4 + 「Task 释放」标未发生 + closeout 链接（+1 散句）③§2 说明补「决策状态列为冻结前快照」④新增 §2A ⑤变更记录冻结行 |
| V-A-4 | 门禁链第 2–4 步 | `git cat-file -e 74a772167`；读 r8 verdict；pins | **PASS** | `74a772167` 存在；`FEA-00-dsh-r8.md` = `approved`；14 份子契约 pin 全 OK；FEA-01 自身 pin 已建 |
| V-A-5 | **门禁链第 5 步** | 读 `:20` 与记录 §2 第 5 行 | **PASS** | 「`Task 释放 ← 未发生`」「⛔ 未发生（有意）…`G-DELETE-IMPL` 仍 OPEN」 |
| V-A-6 | **稳定端口唯一载体** | 读 §2A + C-07 清单 `:9`/`:11` | **PASS** | 单载体声明明确；与 C-07 清单的三口径表述不冲突（FEA-01 说的是"清单替换旧计数口径"这一表述层面，未混淆 36/47/57 三个计数） |
| V-A-7 | pins 15/15 + 14 旧值 | `verify_pins.ps1` | **PASS** | 14 行旧 pin 值与上一轮逐一相同；新增 `OK FEA01 0370c18932b1`；`PASS (all 15)` EXIT=0 |
| V-A-8 | 两路 checker | 默认 + `-TaskPath` | **PASS** | `PASS (2 warnings)` ×2（WARN：12 非终态、STATUS 3171 B） |
| V-A-9 | 完成证据 | 读 `verification/FEA-01-FREEZE/closeout-check.md` | **PASS（实质）** | 门禁链 4/4 表 + pin 审计 15/15 + 冻结前后差异 + 边界；性质标注为「不替代复核」✓ |
| V-A-10 | **门禁链第 1 步证据（P1-001）** | 读 FEA-01 §3 `:96`–`:105`；ADJ 主表 + 追加表；AD-003 | **FAIL（证据缺口）** | §3 八行状态列：「U-01 已记录(AD-003)/U-02 已由 ADJ-001 冻结（**待你确认采用**）/U-03、U-04、U-05、U-06、U-07、U-08 **全部「待你裁决」**」；ADJ 只裁决了 U-03/U-04/U-05（主表）+ 追加 U-06…U-12（**与 §3 的 U-06…U-08 是不同事物**）；AD-003 `:66`–`:67` 覆盖了 U-08（外部文件/字体可选、服务密钥默认不备份），U-06/U-07 无对应裁决 |
| V-A-11 | U 编号碰撞 | 对比 FEA-01 §3 与 ADJ 追加表 | **FAIL（文档级风险，见 P2-004）** | §3 的 U-06=离线阅读、U-07=外部卷、U-08=凭据字体备份；ADJ 追加 U-06=`T=4 DIP`、U-07=L1–L4、U-08=Manifest 偏离——**同号不同物** |

## B. FEA-02-CORE 范围卡

### Architecture

1. **写域边界清楚**：`§范围` 明写唯一写域 = `apps/desktop-avalonia/src/NewManga.ApplicationCore/**` + `apps/desktop-avalonia/tests/**`；不写 `NewManga.App/**`、`CoreClient/**`、`src/**`（Python）、契约文档；共享组合根改动须另行范围确认 ✓；`allowed_paths` 与范围段一致（另含本卡/STATUS/PLAN/LEDGER/checkpoint/复核报告/evidence_dir，属生命周期文件，可接受）。
2. **保留 Current 入口 / 不双调度**：范围段与禁止段两处写明 ✓。
3. **AC1–AC7 可执行**：AC1（程序集引用清单不含 `Avalonia*`）、AC2（N 观察者 → 底层轮询调用计数 = 1）、AC3（意图键去重 + in-flight 复用）、AC4（request-scoped error + 不污染共享缓存）、AC5（Current 非回归）、AC6（L 判定落入卡）、AC7（独立复核）——**全部有可观察断言对象**，覆盖用户首批验收四项 ✓；测试要求表 5 行均 `NOT_RUN`、证据表占位、卡未勾选 → **无「未实现却标通过」** ✓。
4. **L-1/L-2/L-5 判定**：三项均判 `NOT_APPLICABLE`（本卡）并各附再触发条件 ✓；**无机械复制**（未把四表 DDL / M2-C1 码表 / 恢复独占锁 AC 塞进本卡）✓；「不适用 ≠ 豁免」引用了 `FEA-C11_IMPL_PREREQS.md` §0 ✓。
5. **但写域缺一处执行性要素（P1-002）**：`NewManga.sln` 列了**全部 14 个项目**（含 5 个 `*.Tests`），新建 `src/NewManga.ApplicationCore/` 与 `tests/NewManga.ApplicationCore.Tests/` 必须往 sln 加 2 条项目条目；而 `allowed_paths` **不含** `apps/desktop-avalonia/NewManga.sln` → 标准构建/测试门禁（sln 级 `dotnet build`）无法覆盖本卡产物，实现者要么违规写 sln，要么产物游离在门禁之外。
6. **状态与阻塞**：`status: proposed` + `blocked_by: FEA-01-FREEZE-1` ✓；PLAN `:12`/`:26` 已登记本卡（proposed）✓；但 `ready` 前置还缺 2 项精确动作（P2-005）。

### Verification（B，含真实输出）

| # | 场景 | 实际执行 | 结果 | 证据 |
|---|---|---|---|---|
| V-B-1 | 卡结构与写域 | 读 `FEA-02-CORE.md:23`–`:48` | **PASS（边界）/ 缺 sln（P1-002）** | `allowed_paths` 含 ApplicationCore + tests；不含 `NewManga.sln` |
| V-B-2 | **解决方案结构** | 读 `apps/desktop-avalonia/NewManga.sln` 全部 `Project(...)` 行 | **FAIL（P1-002）** | 14 个项目条目，含 `src\NewManga.CoreClient` … `tests\NewManga.ThemeEngine.Tests`；无 `NewManga.ApplicationCore`（该目录当前**不存在**） |
| V-B-3 | 共享构建属性 | 读 `Directory.Build.props` | 备注 | 共享 `net9.0`/`Nullable`/`TreatWarningsAsErrors`；新项目继承即可，**无需改 props**（故 sln 是唯一缺项） |
| V-B-4 | AC 覆盖首批验收四项 | 逐条对表 | **PASS** | AC1←无 Avalonia 依赖；AC2←多观察者一次轮询；AC3←同一意图重试不重复启动；AC4←请求错误互不串扰 |
| V-B-5 | AC 可执行性 | 读 AC1–AC7 与测试要求表 | **PASS（AC5 需明确判据，P2-002）** | 每 AC 均有断言对象；AC5「无双调度」在"本卡不接线"前提下缺少可执行判据 |
| V-B-6 | 无「未实现却标通过」 | 读 AC 勾选、测试表、证据表、Closeout | **PASS** | AC 全未勾选；测试表 5 行 `NOT_RUN`；证据表占位；Closeout「范围冻结中…待复核」 |
| V-B-7 | **L 判定** | 读 L 表 `:62`–`:68` | **PASS（1 处再触发条件偏窄，P2-003）** | 三项 N/A + 再触发条件；未见机械复制 |
| V-B-8 | 状态/阻塞与 PLAN | 读卡 `:6`/`:13`–`:14`、PLAN `:12`/`:24`/`:26` | **PASS（ready 前置见 P2-005）** | `proposed` + `blocked_by: FEA-01-FREEZE-1`；PLAN 已列本卡 |
| V-B-9 | **模拟置 `ready`（TEMP）** | 复制卡改 `status: ready` → `check.ps1 -TaskPath` | **FAIL（1 条真实错误）** | `FAIL: READY Task 未出现在 Plan 的 READY 节点：FEA-02-CORE`（`check.ps1:655`；PLAN `:24` 仍是「READY 节点：无」）。另 2 条为 TEMP 路径伪错误 |
| V-B-10 | **模拟置 `approved`（FEA-01-FREEZE-1，TEMP）** | 改 status → `check.ps1 -TaskPath` | **FAIL（5 条真实错误）** | canonical evidence 占位 + AC1–AC4 缺 `<<MET>>` + `WARN: evidence_dir 含未登记过程文件（closeout-check.md）`；1 条 TEMP 伪错误 |
| V-B-11 | 卡与 §15.6 一致性 | 读方案 `:921` | **PASS** | 方案写域 = ApplicationCore + 对应 tests；「保留 Current 原入口；不得双调度」；L2 验收 = 无 Avalonia 引用、唯一轮询及调用次数——卡与之一致 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| **FEA01-P1-001** | **P1** | `doc/plan/FEA-01_CONTRACT_DRAFT.md:96`–`:105`（§3）+ `doc/plan/FEA-CONTRACT-FROZEN-FEA01.md:37`（§2 第 1 行）+ `:30`（§1B） | **门禁链「4/4」第 1 步的证据缺口**：冻结字节 §3 八行状态列**全部仍写「待你裁决」**（U-03…U-08；U-02 还写「待你确认采用」），而状态行/记录 §2 宣称第 1 步「用户裁决（§3 待决项）」✅。实测：ADJ 只裁决 U-03/U-04/U-05；U-08 由 AD-003 `:66`-`:67` 覆盖；**U-06（离线阅读）/U-07（外部卷）无对应裁决或覆盖记录**。→ 冻结文档一边说门禁过了、一边列着 6 项待裁决；这是本次冻结的**核心声明**，不能以"反正是快照"含混过去 | V-A-10；§3 `:98`–`:105`；ADJ `:15`–`:20`、`:54`/`:60`–`:66`；AD-003 `:66`–`:67` | 在**冻结记录**（不在 pin 面，**无需 UNFREEZE**）补一节「§3 待决项对账」：逐项写 U-01→AD-003、U-02→ADJ-001（并注"用户确认采用"状态）、U-03/U-04/U-05→ADJ 主表 6 项、U-06/U-07→按方案默认执行（用户未提异议，记为"默认采用"）、U-08→AD-003 `:66`–`:67`；并在 §2 第 1 行把证据改成「ADJ 6 项 + 追加 U-06…U-12 + AD-003/ADJ-001 覆盖 + §3 对账（见 §2A）」 | open |
| **FEA02-P1-002** | **P1** | `doc/tasks/FEA-02-CORE.md:23`–`:32`（`allowed_paths`）+ `:45`（写域） | **范围冻结不可执行**：`apps/desktop-avalonia/NewManga.sln` 列了全部 14 个项目（含 5 个 `.Tests`），而本卡要在 `src/NewManga.ApplicationCore/` + `tests/…` 新建项目——**加 sln 条目是必需的**，但 `allowed_paths` 不含 `NewManga.sln`。后果：实现者要么违规写 sln（越界），要么产物不进 sln → 标准门禁（sln 级 `dotnet build`/`dotnet test`）覆盖不到 AC1–AC5 证据 | V-B-2；V-B-3（`Directory.Build.props` 无需改，sln 是唯一缺项） | 二选一：①`allowed_paths` 加 `apps/desktop-avalonia/NewManga.sln`，并在范围段写明「仅新增 ApplicationCore(+Tests) 两条项目条目，不改既有项目/平台配置」；②若有意不注册 sln，则在范围段与 AC 里写明「构建/测试以 csproj 直跑（给出确切命令），sln 注册留给接线 Task」——但②会让实现产物脱离标准门禁，**推荐①** | open |
| FEA01-P2-002 | P2（非阻断） | `doc/STATUS.md:12`；`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:10` | 两处**陈旧计数**：STATUS 仍写「14 份契约已全部冻结（含 C-10）；**FEA-01 待冻结**」，矩阵仍写「已冻结 14 份」+ 追加裁决列「U-06…U-11」（漏 **U-12**）。实测 FEA-01 已冻结（15/15） | `doc/STATUS.md:12`；矩阵 `:10`；`verify_pins` 15/15 | STATUS `:12` 改「14 份子契约 + FEA-01 全部冻结（`verify_pins` 15/15）」；矩阵进度段改「已冻结 14 份 + FEA-01 伞契约冻结」并补 U-12 | open |
| FEA02-P2-003 | P2（非阻断） | `doc/tasks/FEA-02-CORE.md:56`（AC5） | AC5 的「**无「双调度」**」在"本卡不写 `NewManga.App/**`、不接线"的前提下**没有可执行判据**（新路径尚不存在，断言恒真）。建议改写为可验证的两段：①现有入口行为等价（现有测试基线非回归，逐项列出跑的测试项目）；②结构断言：本卡 diff 不触及 `apps/desktop-avalonia/src/NewManga.App/**`（即未新增第二调度路径），"真实接线后的无双调度"留给接线 Task 验证 | V-B-5 | 按上改写 AC5；并在卡里注明"本卡不接线，接线 Task 另行冻结范围" | open |
| FEA02-P2-004 | P2（非阻断） | `doc/tasks/FEA-02-CORE.md:65`（L-2 再触发条件） | L-2 判 N/A 的再触发条件写的是「新增 `RUN_*`/`TRASH_*` 码或改主机白名单」，**未覆盖另一种会被本卡实际触发的路径**：把既有 Run 错误码 → `category` 映射（host 投影逻辑）搬入 ApplicationCore。若实现这么做，就实质承接了 L-2 的白名单语义，却不会触发再评估 | V-B-7；L-2 行原文；`FEA-C11_IMPL_PREREQS.md:18` | 再触发条件补一句：「或把既有 Run 错误码→category 映射 / host 投影白名单逻辑搬入 ApplicationCore → 转 `blocked` 并复核 L-2」 | open |
| FEA01-P2-005 | P2（非阻断；含 **2 条硬前置**） | FEA-01 §3 与 ADJ 追加表（编号体系） | **U 编号碰撞**：FEA-01 §3 的 U-06/U-07/U-08 = 离线阅读/外部卷/凭据字体备份；ADJ 追加裁决的 U-06/U-07/U-08 = `T=4 DIP`/L1–L4/Manifest 偏离。同一 `U-0x` 在两份权威文档指不同裁决，审计时必混。冻结字节已无法改（须 UNFREEZE），但必须在**记录侧**留下消歧 | V-A-11；§3 `:103`–`:105`；ADJ `:60`–`:62` | 冻结记录加一行消歧声明：「本清单 §3 的 U-0x 为 FEA-01 内部编号（r1 §5.3 遗留），与 ADJ 追加裁决 U-0x 非同一体系；引用时须写全 `FEA-01 §3 U-06` / `ADJ U-06`」；后续文档禁止裸用 `U-0x` 指代 ADJ 追加裁决以外的项 | open |
| FEA-P2-006 | P2（非阻断；**置 approved / ready 的硬前置**） | `doc/tasks/FEA-01-FREEZE-1.md:45`–`:48`、`:69`；`doc/REBASELINE_PLAN.md:24` | ①`FEA-01-FREEZE-1` 置 `approved` 会 FAIL：AC1–AC4 缺 `<<MET>>`、Canonical Evidence 仅占位行、且 `evidence_dir` 有未登记过程文件（`closeout-check.md`）——**与 PREREQ-1 同类（第二次）**；②`FEA-02-CORE` 置 `ready` 会 FAIL：PLAN `:24` 仍「READY 节点：无」，`check.ps1:640`–`:655` 要求 READY 节点列出该 id（我实测报 `READY Task 未出现在 Plan 的 READY 节点`） | V-B-9、V-B-10（真实错误清单） | 置 approved 前：AC1–AC4 加 `<<MET>>`（AC4 依据本报告 P0/P1 修订后复审）+ 证据行（如 `E-FREEZE-DOC \| AC1 \| doc/plan/FEA-CONTRACT-FROZEN-FEA01.md \| b0aa7cb6a \| <sha256> \| CANONICAL`、`E-FREEZE-EVIDENCE \| AC3 \| verification/FEA-01-FREEZE/closeout-check.md \| b0aa7cb6a \| <sha256> \| CANONICAL`）；置 ready 前：PLAN `:24` 改「READY 节点：FEA-02-CORE」、`:12`/`:26` 状态词同步，并把 `blocked_by` 处置掉（建议 `FEA-01-FREEZE-1` 走 `done`（integration `b0aa7cb6a`）后再置 ready，避免 ready 卡挂着未完成 blocker） | open |

**P0：0。P1：2。** 5 条 P2 非阻断。

## 对 Lead 10 项核对要求的答复

**A1 门禁链 4/4 是否属实**：**第 2–4 步属实**（r8 `approved` @`74a772167` ✓、14 份子契约 pin 全 OK ✓、FEA-01 自身冻结 ✓），**第 5 步如实标未发生 ✓**；**第 1 步证据不足 → P1-001**（§3 六行仍写"待你裁决"，记录未逐项对账；U-06/U-07 无裁决或覆盖证据）。
**A2 pin 双口径**：**PASS**（三口径同为 `0370c189…`，15251 B / 134 L）。
**A3 §1B vs 真实 diff**：**PASS**（5 组一一对应，无未披露改动，无条款增删）。
**A4 稳定端口唯一载体**：**PASS**（`FEA-C07_API_INVENTORY.md` @ pin `17c8f7016a36…`；不另建第二份；与 C-07 清单 §1 的三计数表述不冲突）。
**A5 pins/check**：**PASS**（15/15；14 旧值未变；两路 PASS）。
**B6 写域/Current/组合根**：**边界表述 PASS，但写域缺 `NewManga.sln` → P1-002**；"保留 Current 入口、不双调度"两处写明 ✓；共享组合根改动列为需另行范围确认 ✓。
**B7 AC 可执行性与覆盖**：**PASS**（AC1–AC7 覆盖用户首批验收四项且各有断言对象；无未实现却标通过）；AC5 的"无双调度"需按 P2-003 改写。
**B8 L 判定**：**PASS**（三项 N/A + 再触发条件；无机械复制；不属"该带未带"——本卡不新增 wire 码、不触 DB/恢复；仅再触发条件漏了"搬入映射"情形 → P2-004）。
**B9 proposed/blocked_by 一致性**：**一致** ✓；`ready` 前置见 P2-006（PLAN READY 节点 + blocker 收尾）。
**B10 `ready` 前缺什么（精确清单）**：①修 P1-002（写域加 sln）；②PLAN `:24` READY 节点列出 `FEA-02-CORE`（否则 `check.ps1:655` FAIL）；③PLAN `:12`/`:26` 与 STATUS `:7`/`:11` 状态词同步为 `ready`；④`blocked_by` 指向的 `FEA-01-FREEZE-1` 应终态化（done，integration `b0aa7cb6a`）；⑤卡内 AC1–AC7 在实现前保持未勾选（无需标记）。

## 结论

**decision：`changes_requested`**（P0 × 0 / **P1 × 2** / P2 × 5）。

两条 P1 都是**一两处文本/路径级别**的修正，不涉及冻结字节（可不动 pin）：

1. **P1-001**（A）：冻结记录补「§3 待决项对账」，把第 1 步 ✅ 的证据补齐（U-01→AD-003、U-02→ADJ-001、U-03/U-04/U-05→ADJ 主表、U-06/U-07→方案默认采用、U-08→AD-003）：**冻结字节不动 → 无需 UNFREEZE**。
2. **P1-002**（B）：`allowed_paths` 加 `apps/desktop-avalonia/NewManga.sln`（写明仅新增 2 条项目条目），或在卡内明确"不注册 sln、csproj 直跑"的替代验证路径。

修完后请给我**新 head 做 R2 极简复审**（只核：§3 对账表是否与 ADJ/AD-003 逐项对得上、卡写域与 sln 判定、两条 P2 硬前置是否落实），通过后我再判 `approved`，你即可置 `FEA-01-FREEZE-1` `approved`/`done` 并把 `FEA-02-CORE` 置 `ready` 交 Codex。

**边界**：本报告不构成实现授权（`G-DELETE-IMPL` 仍 OPEN）、不构成 push 授权；A 线冻结字节在我批准前不得再改（改则须重算 pin 并在 §1B 重披露）。

—— 报告结束（`decision: changes_requested`；A 线冻结字节/pin/§1B/端口载体/pins 全部 PASS，唯门禁链第 1 步证据缺口 P1-001；B 线范围与 AC 基本合格，唯写域缺 sln 致不可执行 P1-002）。
