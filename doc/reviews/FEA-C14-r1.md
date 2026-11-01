---
document_id: FEA-C14-r1
kind: independent_review
task_id: task-29（FEA-C14-DRAFT）
round: 1
scope: 独立复核 C-14 草案（D05 剩余范围：重定位/同步 + 容器页映射 + 缓存三缺口），重点覆盖矩阵、可执行性、与已冻结契约的冲突/双权威
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-29"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 0ab75f990
reviewed_head_full: 0ab75f9903873675c5621f6325411bef9985f6b6
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 0ab75f990）"
reviewed_documents:
  - doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md（草案，210 行，SC-S01…SC-S17，blob sha256 2c314aad…）
  - doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md `:419`–`:422`、`:432`、`:459`、`:461`、`:768`
  - doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md `:84`、`:117`（未冻结声明）
  - doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md（SC-01/02/03/20/21/22/25/26/27/29/31/34）
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md（`:39`/`:51`/`:52`/`:64`/`:65`）
  - doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md（`:27`/`:43`/`:72`）与 doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md（PD-01…PD-10）
  - doc/plan/FEA-CONTRACT-FROZEN-C06.md（§3 D05 授权面子集表述）
reviewed_sha256:
  doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md: 2c314aad54f238cdb0c69f3cab070e7b164b44554592bfd3a5801115925bdaf6
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 5
p2_count: 4
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 12)；C14 = MISSING-RECORD (not yet frozen; skipped) —— 符合预期，未冻结不该 PASS"
captured_at: 2026-11-01T10:19:28+08:00
captured_by: c01b-reviewer
---

# 独立复核 r1：FEA-C14 Source 重定位 / 同步 / 容器页映射 / 缓存边界（草案）

**本报告不是** 冻结动作、不释放任何 Task。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 5** / P2 × 4）。**

草案的**骨架是对的**：D05 五项与方案 `:768` 完全一致；§0.1 四条「已承载」我逐行实核**全部为真**；17 条 SC 的 13 条验证可直接执行；与方案原文（`:419`/`:420`/`:421`/`:459`/`:461`/`:432`）的对齐总体准确。

**但有 5 处 P1，其中 3 处正是用户点名的两个风险：**

1. **§4 把「没承载」写成了「已承载」**：`:191` 声称 C-01b 已冻结 `source_entries`/`page_bindings`/`source_sync_plans`/`source_operations` 四张表结构（SC-21/22）——**C-01b 全文没有任何一张表的定义**，且 **AD-003 `:117` 明文说这些表「均未定，由 DSH 在 D05 范围冻结」**。这还与 §0 行 3/4 的「已有承载：无」自相矛盾。
2. **对已冻结 C-01b 形成双权威**：SC-S04/SC-S05/SC-S07 实际复写了 C-01b 已冻结的 **SC-34**（operation journal + receipt + 崩溃恢复）、**SC-26**（Dirty→扫描→diff→预览→事务发布）、**SC-27**（tombstone / binding generation / 旧坐标），但 §0 未把这三条列为「已有承载」，条款也未标「引用不复写」。
3. **SC-S08 与冻结的 C-04b 冲突**：C-04b 冻结的 `DeletePreviewItem`（`:43`）没有 pending operation 字段、全文无 `source_operations`；SC-S08 却要求 preflight 披露 pending 状态——这**必须改 C-04b 契约**，与 C-14 自己的「不改 C-04b 字节」（`:193`）和边界声明（`:8`）矛盾。且 `:143` 引用「C-04b 的 PD-02/PD-03」是**错引**（PD-02 = 单条/批量形状；PD-03 在 C-04b 不存在）。

另 2 处 P1：**C-06 `scope.entry` 与 `EntryId` 的概念混同**（C-06 `:52` 的 `entry` 是被解析到授权根内路径的定位键，未定义 = EntryId；C-14 单方面断言「对齐」= 解释已冻结字段）；**SC-S09 的身份公式自相矛盾**（把 `SourceVersionId` 纳入 `EntryId` 的构成，则改名/重同步换版本时 `EntryId` 必变，与同条「改名后 EntryId 不变」及 SC-S01/SC-S12 冲突）。

---

## 2. Findings

### P1

**P1-1 — §4 虚假「已承载」：C-01b 并未冻结四张表结构（位置 `FEA-C14:191`）**
- 声称：「C-01b（已冻）| `source_entries`/`page_bindings`/`source_sync_plans`/`source_operations` 表结构（SC-21/22）」。
- 实核：① C-01b 全文 grep 这四张表名 **0 命中**；② C-01b SC-21 = 引用源读取需独立授权面（`SourceAccessRegistry` + `source-read` grant），SC-22 = 授权根边界（不跟随越根符号链接），**均非表结构**；③ **AD-003 `:117`**：「本文件**不是**契约冻结：`sources`/…/`source_entries`/`page_bindings`/`source_sync_plans`/`source_operations` 的表名、索引、外键、约束与迁移版本**均未定**，由 DSH 在 D05 范围冻结」。
- 影响：这是用户点名的「把没承载写成已承载」；且与 §0 行 3/4「已有承载：无」直接矛盾；若据此记账，D05 第 3/4 项会看起来已被 C-01b 部分承载。
- 修法：§4 该行改为「AD-003 `:117` 明确未冻结 → **本契约首次定义**这四张表的结构」；注意届时须补 `source_entries` 的完整字段表（当前 SC-S09 只给身份公式，未给列定义），或明确「表结构仍留给后续存储契约」并同步修正 §0 矩阵。

**P1-2 — 双权威：SC-S04/S05/S07 复写 C-01b 冻结条款（位置 `FEA-C14:110`/`:118-120`/`:135-136`）**
- C-01b 冻结条款：**SC-34**（`:98`）「OS 删除与 DB 无分布式事务：以 operation journal + receipt 记录，崩溃恢复先核对 OS 事实再决定是否重发」；**SC-26**（`:85`）「变化后进入 Dirty → 扫描 → diff → 用户预览 → 事务发布新绑定」；**SC-27**（`:86`）「缺失页保留 tombstone、问题与人工修改，不连带删除；变化页新建 binding generation；旧像素坐标不得无条件下套新图」。
- C-14：SC-S04 写 operation journal/receipt/崩溃恢复（`:110-111`）；SC-S05 写预览与「确认与应用之间再变更 → 拒绝」（`:118-120`）；SC-S07 写「缺失页保留 tombstone…不连带删除」「变化页建立新的 binding generation，旧区域只留在旧内容 lineage」（`:135-136`）——与 SC-34/26/27 **同义**。§0 行 3 却写「已有承载：无」，§4 只声明缓存三条款（SC-02/03/20）不复写。
- 影响：同一语义两处定义 → 双权威；将来 C-01b 冻结字节与 C-14 若措辞漂移，实现与审计都无所适从。
- 修法：§0 行 3「已有承载」补 **C-01b SC-26 / SC-27 / SC-34**；SC-S04/05/07 各加一句「引用 C-01b SC-xx，不复写；本契约只补 relink/repoint 区分、范围选择、可执行判据」；或把重复段落收缩为引用 + 增量。

**P1-3 — SC-S08 与冻结 C-04b 冲突 + 引用错误（位置 `FEA-C14:142-143`，对照 `FEA-C04b:43`/`:27`/`:72`）**
- C-04b 冻结的预检出参形状（`:43`）：`{ bookId, title, protection{...}, contentSummary{...}, sharedFileRefs[] }` —— **无 pending operation / source_operations 字段**；C-04b 全文无 `source_operations` 字样。
- SC-S08 要求「删除 preflight 的清单**必须**包含 `source_operations` 的 pending 状态（若有未完成 relink/sync，preflight 须标出）」→ 这是对 C-04b 协议形状的**实质扩展**，与 C-14 `:8`「不改任何已冻结契约的字节」、`:193`「**不改 C-04b 字节**」矛盾。按 C-04b 冻结顺序，M2-C1/预检字段的字节修订须由独立 Task 在释放删除实现前完成（类比 C-08 的块② 模式）。
- 引用错误：`:143`「由 C-04b 的 PD-02/PD-03 约束」——C-04b 的 **PD-02** 是「单条 vs 批量按命令形状分别绑定」（`:27`），**PD-03 在 C-04b 不存在**（C-04b 只落地 PD-01/02/07/08/09）；ADJ-001 的 **PD-03** 是「只读预览必须由 Core 权威计算、无副作用」（`:63`），PD-08 才是共享引用（`:68`）。「不得清理被引用为唯一来源的记录」正确出处应是 **ADJ-001 PD-08 + C-04b 的 `BOOK_DELETE_CONFLICT`（关系图/归属预检，`:72`）**。
- 修法：① 把「preflight 披露 pending operation」明确为 **C-04b 的 UNFREEZE/扩展点**（或 M2-C1 §5.11.2 的独立字节修订 Task），C-14 只定义字段语义需求；② 改引用为 ADJ-001 PD-08 + C-04b `:72` 关系图预检。

**P1-4 — C-06 `scope.entry` 与 `EntryId` 概念混同（位置 `FEA-C14:192`，对照 `FEA-C06:39`/`:51`/`:52`）**
- C-06 冻结文本：`scope` 按「`SourceId / version / entry / rendition`」限定（`:39`）；`RequestSourceRead.scope{ sourceId, version, entry, rendition }`（`:51`）；归属校验「`scope.sourceId/entry` **必须解析到某 `authorizedRoots` 内的路径**（映射在 Verify 时做，越根即拒绝）」（`:52`）。→ `entry` 是**可解析为路径的定位键**，C-06 **未定义其类型、也未说明等于 `EntryId`**；AD-003 `:84` 同样只列「SourceId/version/entry/rendition」。
- C-14 `:192` 断言「grant `scope` 与本契约的 `EntryId` 对齐（`scope.entry`）」——这是**单方面解释已冻结字段**；若实现把 `scope.entry` 传成 `EntryId`，而 C-06 侧按路径解析语义实现，会形成 wire 级不一致；若要等价，需在 C-06 的 UNFREEZE 或协议实现 Task 中显式约定映射（`EntryId → source_entries.locator → path`）。
- 修法：改为「C-06 `scope.entry` 语义为『可解析到授权根内路径的定位键』；本契约的 `EntryId` 经 `source_entries.locator` 解析后可与之对应——**对齐规则须在 C-06/协议层确认，本契约不单方面重定义**」。

**P1-5 — SC-S09 身份公式自相矛盾（位置 `FEA-C14:42`，波及 `:43`/`:45`、`:87`/`:91`、`:66`）**
- 正文：「身份 = `EntryId`（`source_entries`），由 **`SourceId` + `SourceVersionId` + 稳定排序键 + 内容指纹**共同确定（方案 `:419`）」。
- 矛盾：① 同条下一句「同一文件被改名/移动后 `locator` 变、`EntryId` **不变**」——但改名/移动会产生新内容版本 → `SourceVersionId` 变 → 按公式 `EntryId` 应变；② SC-S01（`:87`/`:91`）要求 relink 后 `EntryId` 不变；③ SC-S12（`:66`）要求未变成员保留 `PageId`/人工版本——按公式新 `SourceVersion` 下 `EntryId` 全变。验证（`:45`「改名 ZIP 内成员 → 断言 `EntryId` 不变」）按公式**不可能通过**。
- 另：方案 `:419` 只列 `source_entries` 的列（EntryId、SourceVersionId、locator、稳定排序键、digest…），并未说身份由这些联合确定——这是 C-14 自创公式。
- 修法：身份 = `SourceId` + **稳定排序键**（+ 内容指纹用于区分同名不同内容），**`SourceVersion` 是内容版本、不参与身份**；行键 = (`SourceVersionId`, `EntryId`)。同时把「按内容指纹也变化时才升级 needs_confirmation」（`:104`）与新口径对齐。

### P2

1. **P2-1（SC-S14 判据与正文相反，`:155` vs `:159`）**：正文「同 last-use 时**先清大文件**（回收效率）」；验证却写「断言 LRU 先清、**变小文件先于小**、被引用产物跳过」——措辞残缺且与正文相反，判据不可执行。改为「同 last-use 时大文件先清」。
2. **P2-2（SC-S15 引用不精确，`:164`）**：「位置必须在受管根内（C-01b SC-01/SC-03 的派生前缀）」——SC-03 的 [现行] 证据确有清理路径前缀白名单（`cleanup.py:41`，受管根前缀），但 **SC-01 是「新导入不创建永久全尺寸输入副本」，与派生前缀无关**。建议改引「C-01b SC-03（`cleanup.py:41` 受管根前缀白名单）」。
3. **P2-3（SC-S13 交叉引用错 + §5 条件 4 过期，`:73`、`:201`）**：`:73`「恢复路径见 SC-S03/SC-S04（重定位）」——SC-S03 = 重定位不改变身份、SC-S04 = 失败与回滚，**都不是恢复路径**；应为 SC-S01/SC-S02（relink/repoint 入口）或新增恢复条款。`:201`「C-14 冻结时**必须同时把本契约加入 `verify_pins.ps1` 的清单**」——脚本 `tools/governance/verify_pins.ps1:12` **已包含** C14；当前实跑输出 `MISSING-RECORD C14 (not yet frozen; skipped)`，故条件应改为「冻结记录建立后 `verify_pins.ps1` 由 skipped 变 OK」。
4. **P2-4（章节编号与矩阵顺序错位）**：§0 矩阵按 D05 顺序列 #3（重定位/同步 = SC-S01…S08）、#4（容器页映射 = SC-S09…S13），但正文 §1 是容器页映射（S09–S13）、§2 才是重定位/同步（S01–S08）——阅读顺序与编号相反，建议 §1/§2 对调或矩阵加「见 §x」列。

---

## 3. 七项判定

| # | 项 | 判定 |
|---|---|---|
| 1 | 覆盖矩阵 vs 原文一致性（含 §0.1 四条逐条核） | **⚠ 部分**：D05 五项与方案 `:768` **完全一致** ✓；**§0.1 四条逐行实核全部为真** ✓（C-06 `:64` = 第 7 条读取预算「超限拒绝不截断」✓；C-01b SC-02 可再生产物+cache key ✓；SC-03 非缓存边界 ✓；SC-20 + C-06 `:65` 两通道隔离 ✓）；**但 §4 虚假「C-01b 已冻表结构」（P1-1）**，且 §0 行 3 低估了 C-01b SC-26/27/34（P1-2） |
| 2 | 17 条 SC 验证可执行性 | **⚠ 13/17 干净**；问题：SC-S14 判据与正文相反（P2-1）、SC-S09 按自身公式验证不成立（P1-5）、SC-S08 依赖 C-04b 不存在的字段（P1-3）、SC-S16「不 OOM」偏粗但可接受 |
| 3 | 与已冻结契约冲突 | **⚠ 有 3 类冲突**：C-01b SC-26/27/34 双权威（P1-2）；SC-S08 vs C-04b 冻结形状 + 错引 PD-02/PD-03（P1-3）；C-06 `scope.entry` ≠ 已证 EntryId（P1-4）。C-01b SC-02/03/20 与 SC-S14/S15/S17 的关系是「范围引用」，**未复写**，无冲突 ✓ |
| 4 | 方案原文对齐 | **✅ 总体准确**：SC-S01↔`:461` ✓；SC-S09/S11↔`:419` ✓（除 P1-5 公式）；SC-S05/S06↔`:421` ✓；SC-S07↔`:459` ✓（但与 C-01b SC-27 重叠，见 P1-2）；SC-S10↔`:420` 字段逐项一致 ✓；SC-S02/S12↔`:461`/`:459` ✓；SC-S04↔`:432` ✓；SC-S13↔`:461` ✓ |
| 5 | 有无越界 / 双权威 | **有**：P1-1（虚假已承载）、P1-2（双权威）、P1-4（解释/改写冻结字段）、P1-3（要求改冻结 C-04b 形状）。**未见超出 D05 范围的内容** ✓ |
| 6 | 冻结条件可达性 + verify_pins | **✅ 可达（前提是 P1 修复）**：§5 五条中 1 需本轮修复后复核；2 四份已冻实核 ✓（`verify_pins` 12/12 OK）；3 与 C-06 冻结记录 `:42`「只承载 D05 授权面子集…重定位·同步/容器页映射/缓存边界由 C-01b、C-09 及后续契约分担」一致 ✓；4 `check.ps1` PASS ✓、`verify_pins` 当前 PASS 且 C14 = MISSING-RECORD skipped（**符合预期**）；但条件 4 措辞过期（P2-3） |
| 7 | 数据安全 + check.ps1 | **✅**：`check.ps1` PASS (3 warnings) EXIT=0；`verify_pins.ps1` PASS (all 12)；未 push（223）；工作树干净；只读复核，唯一写入为本报告 |

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文；未参与 C-14 起草（作者 = DSH），未参与 C-01b/C-06/C-04b/C-08 的实现或冻结。
- 我出具过 C-01b/C-06/C-04b/C-08 的部分复核报告（如实披露）；本轮按「草案是否可冻结」标准从严核，不因先前批准过被引用契约而放宽。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；实跑 `check.ps1` 与 `verify_pins.ps1` 均为只读校验。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档、冻结字节、脚本输出比对结论。
- 未核方案 r4 `:768` 之外的其他 D05 相关段落（只核 C-14 引用的 `:419`–`:422`/`:432`/`:459`/`:461`）。
- 未核 C-01b SC-24/28/30/31/32/33 等其他条款与 C-14 的潜在重叠（只核用户点名的 SC-01/02/03/20/21/22/25/26/27/29/31/34）。
- 未核 C-14 与 C-07（API 清单）/C-09（数据修复）的接口。
- 未核「淘汰策略/持久化/全局上限」在现有代码（`cleanup.py`/资源通道）中的实现现状，只核契约层面是否被已冻结条款承载。
- 未核 C-04b 扩展点的具体字节修订范围（只确认冻结形状无 pending 字段）。
- 未核 `doc/tasks/FEA-C14-DRAFT.md` 的 AC 与 C-14 条款的逐条对应（只核契约草案本身）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×5 / P2×4；骨架与 §0.1 承载证明成立，阻塞点为 §4 虚假已承载、C-01b 双权威、SC-S08 与 C-04b 冲突、C-06 entry 概念混同、SC-S09 身份公式矛盾）。
