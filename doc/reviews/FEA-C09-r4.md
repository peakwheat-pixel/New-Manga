---
document_id: FEA-C09-r4
kind: independent_review
task_id: task-32（FEA-D07-UNBLOCK AC7 前复核）
round: 4
scope: C-09 v4 极窄面复核（r3 的 P1×1 + P2×7 + 矩阵解环同步）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: f21216893
reviewed_head_full: f21216893eec74e4878a4dfc0213f0edf0b62520
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == f21216893）"
reviewed_documents:
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md（v4，189 行，blob sha256 e1f3a0a8…）
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md（C-09 行 `:28`、第 7 步 `:53`、Gate 表 `:62-63`）
  - 对照：ADJ-001 PD-01/PD-08（`:58`/`:68`）、C-04b `DeletePreviewItem`（`:43`/`:44`）、C-01b SC-10a/10b/13/17、M2-C1 rev 2.11 `ListRecycleBinBooks`（`:150`）、C-03 `presentation-settings.json`/`theme-settings.json`
reviewed_sha256:
  doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md: e1f3a0a8a9f28e1a55e90700994cfbe5a99f1606da111e46fede0e1a04a614e7
  doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md: 87e3bbc339a6b141bcc21401403587c5e0f6f863d216fa9cd00ee4f9fc867ac5
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 5
p2_note: "5 条均为文字精度/外部记账类（K-1…K-5），不阻断 AC7；建议在冻结前顺手修 K-1、K-4，并在冻结记录 §1B 登记"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 12)，EXIT=0，本次实跑"
captured_at: 2026-11-01T11:02:00+08:00
captured_by: c01b-reviewer
---

# 独立复核 r4：C-09 v4（解环 + 五项 D07 条款 + 矩阵同步）

**本报告不是** 冻结动作、不释放任何 Task。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 5 非阻断，登记为 K-1…K-5）。**

**8 处全部到位**：P1 的 SC-B04a 语义已按 ADJ-001 **真正**纠正（我逐字对照了 PD-01/PD-08 原文，不是看 DSH 的措辞）；D07 七项 **7/7** 有落点；`backup/1`/`backup/2` 入表；settings 文件名改用 `presentation-settings.json` 并注明与 SC-10b 的细化关系；码属性、两个映射、负向对照齐；命名统一为一种落地写法；矩阵 C-09 行/第 7 步已解环；条件③ 已含 C-08。

| # | 核对项 | 结果 |
|---|---|---|
| 1 | P1：SC-B04a 披露 vs 阻断 | **✅**（彻底删除列 = 披露+专门确认、非阻断；共享引用 = 可安全拆分不阻断/不可拆分才 `BOOK_DELETE_CONFLICT`；新增「非终态 Run/Task → `BOOK_BUSY`」行，与 PD-01 的「唯一硬阻断项」一致） |
| 2 | P2-1：D07 七项 7/7 | **✅**（第 7 项「独占写锁与 pin」由 §3 `:169` 挂 C-01b SC-13/SC-17） |
| 3 | P2-2：backup/1、backup/2 入表 | **✅**（`:42`/`:43`） |
| 4 | P2-3：settings 文件名 + SC-10b 口径 | **✅**（`:45` 改用 `presentation-settings.json`；`:47` 明写「对 SC-10b 现状注记的细化更新」） |
| 5 | P2-4：码属性 + 两个映射 + 负向对照 | **✅**（`:113` `not_found`；`:117` ListTrash 关系；`:119` PurgeTrash 委托 C-04b；`:128` 负向对照） |
| 6 | P2-5：命名统一 | **✅**（`:136` 明写 `format:"nmbak"`+`version:2` 为落地命名，`newmanga.backup/2` 只是设计稿命名） |
| 7 | P2-6：矩阵解环 | **✅**（`:28` 不再要求 `G-DELETE-CONTRACT`；`:53` 解环后不等 Gate；`:63` `G-CONTRACT` 已 CLOSED）；⚠ 旧表述残留在**其他文档**（K-5） |
| 8 | P2-7：条件③ 含 C-08 | **✅**（`:179` 列出 C-01b/C-04b/C-06/C-08/C-14） |

---

## 2. 8 处核对明细

### 2.1 P1：SC-B04a 与 ADJ-001 —— **✅ 真的对齐了**

我逐字对照 ADJ-001：
- **PD-01**（`:58`）：「影响清单…逐项计算并**不得写入任何状态**：…锁定区域数、current Revision、pinned Revision…活动草稿页数、**非终态 Run/Task（同时作为 `BOOK_BUSY` 阻断项）**…」——**披露项不是阻断项**；PD-01 里唯一的硬阻断是「非终态 Run/Task → `BOOK_BUSY`」。
- **PD-08**（`:68`）：「**可安全拆分**的共享引用**不是**删除阻断条件——删除目标项目自有的内容行与清单内自有文件，**保留共享物理原文件与其他项目的绑定**；…**就共享引用冲突而言**，无法安全拆分、关系图/归属不一致、或存在未列明的目标外引用，使整批 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED`」。

C-09 v4 的对照（`:79`–`:83`）：
- 三锁 → 彻底删除：**披露 + 专门确认（PD-01，`protection.lockCount`）；非阻断** ✓
- 人工 revision / 当前 revision → **披露；非阻断** ✓（字段引用见 K-1）
- 活动草稿 → 披露（`protection.draftPageCount`）；非阻断 ✓
- 共享引用 → **可安全拆分不阻断 / 不可拆分·关系图不一致·未列明 → `BOOK_DELETE_CONFLICT`（fail-closed）** ✓（与 PD-08 逐句对应）
- **新增行**：非终态 Run / Task → **阻断 `BOOK_BUSY`（PD-01 的唯一硬阻断项）** ✓
- 「关键」段（`:85`）明确「披露≠有锁就拒绝」，并给出后果说明 ✓；「阻止」只保留在自动清理列（保护人工成果）✓
- 验证句（`:87`）已一致：自动清理被阻止 / 软删通过 / 彻底删除可进行但先 PD-01 披露确认 / 有非终态 Run → `BOOK_BUSY` ✓
- 「不复写」（`:89`）声明语义由 ADJ-001 定义、本条款只管共用判定 ✓
- 字段名与 C-04b `DeletePreviewItem.protection{lockCount, currentRevisionId, pinnedRevisionIds[], activeRunIds[], draftPageCount, manualRegionCount}`（`:43`）一致 ✓（`lockCount`/`draftPageCount`/`pinnedRevisionIds` 均为真实字段）

### 2.2 P2-1：D07 七项 7/7

§3 `:169` 新增：「**D07「独占写锁与 pin」由 C-01b SC-13（pin）与 SC-17（独占维护锁）承载——本契约引用不复写**（对应 SC-B03 对 SC-17 的引用）」✓。七项映射：①SC-B06 ②SC-B04a ③SC-B01/01a ④SC-B07 ⑤DatabaseId（SC-B03/07/08）⑥SC-B08 ⑦SC-13/17（§3）→ **7/7**。

### 2.3 P2-2：backup/1、backup/2 入表

`:42`「`backup/1` 旧包 | **否**（不复制进新包）| 只可读取/恢复（legacy adapter），不升级、不搬运」；`:43`「`backup/2` 新包 | **是**（本契约写端产物）| 见 SC-B07」✓ 两行进表。**K-2**：`backup/2` 行「是」在「是否入包」列易被读成「新包把自己打进包」，建议改「不适用（产物本身）」。

### 2.4 P2-3：settings 文件名与 SC-10b

`:45` 验证改为断言 `settings/credentials*` 缺失、**`settings/presentation-settings.json`（C-03 的新文件）**与 `settings/theme-settings.json`（旧、只读迁移输入）存在、`catalog.sqlite` 不在包内 ✓；`:47` 明写「SC-10b 的 [现状注记] 记『`settings/*.json` 未入包』——本表是**对该注记的细化更新**（拆凭证类/非凭据类），不是重写 SC-10b 冻结字节；差异由本契约冻结记录登记」✓。**K-3**：C-03 记的旧文件实际路径是 `%APPDATA%/NewManga/theme-settings.json`（`ThemeSettingsStore.cs:7`），C-09 统一加了 `settings/` 前缀——两者需以 C-03 为准核对（本仓 checkout 无 `src/` 可复核实现，按文档口径 C-03 更具体）。

### 2.5 P2-4：码属性 + 两个映射 + 负向对照

- `:113` `TRASH_ENTRY_NOT_FOUND` → **`not_found`** ✓（对齐 M2-C1 类别表与 C-04b `BOOK_NOT_FOUND` `:70`）。
- `:117` ListTrash ↔ `ListRecycleBinBooks`（M2-C1 `:150`）关系有说明 ✓，但**K-4**：其中「建议：…`ListRecycleBinBooks` 为 Host 投影」与 M2-C1 rev 2.11 的冻结事实不符——`ListRecycleBinBooks` 是**冻结的 Core command**（另有 production Tauri command 为 Host 侧），建议改为「`ListRecycleBinBooks` 是已冻结 Core command，`ListTrash` 为其底层能力/替代候选，映射在实现 Task 确认」。
- `:119` PurgeTrash 委托 `PreviewPermanentDeleteBooks` + `PermanentlyDeleteBooks`（含 PD-01 披露与专门确认）✓。
- `:126` 验证补「PurgeTrash 带确认但目标含非终态 Run → `BOOK_BUSY` 且零副作用」✓。
- `:128` 负向对照：未扩 M2-C1 时 3 个 `TRASH_*` 码被 host 投影层白名单降级为 `category=unknown`（与 C-08 `allowedRunErrorCodes` 同模式）✓。
- 残留小项（不影响本轮判定）：`TRASH_RESTORE_LAYER_MISMATCH` 仍用于**备份**恢复（SC-B09 `:161`），名字带 `TRASH_` 但语义是 backup 层不匹配——建议后续改名或注明「该码兼用于 backup 恢复」。

### 2.6 P2-5：命名统一

`:135`「包根 `manifest.json` 的 `format: "nmbak"` + `version: 2`；`backup/1` 为 `version: 1`」+ `:136`「方案 `:520` 的 `newmanga.backup/2` 是**设计稿命名**；落地命名是 `format:"nmbak"+version:2`（标题的 `backup/2` 是简写）…**不得混用三种写法**」✓ 只剩一种落地写法。

### 2.7 P2-6：矩阵解环

- `:28` C-09 行：「①C-01b/C-04b/C-06/C-08/C-14 冻结 ②`G-CONTRACT` 关闭 ✅（**不再要求 `G-DELETE-CONTRACT`**——解环）」✓
- `:53` 第 7 步：「C-09 冻结（上游契约全冻 + 独立复核；**解环后不再等 Gate 关闭**）」✓
- `:63` `G-CONTRACT`：**已 CLOSED 2026-11-01** ✓（与 AD-003 `:128` 一致）
- **K-5（非矩阵，属外部记账）**：旧「C-09 等两 Gate / 仍 blocked」表述仍存在于：
  - `doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:203`（**已冻结契约**）
  - `doc/plan/FEA-CONTRACT-FROZEN-C04b.md:43`、`FEA-CONTRACT-FROZEN-C08.md:55`、`FEA-CONTRACT-FROZEN-C13.md:63`（冻结记录）
  - `doc/plan/GATE-CLOSURE-RULING-2026-11-01.md:63`、`:111`（裁定）
  - `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:128` 仍写「D07 缺多项**且与 C-09 循环**」
  这些不是 C-09 的循环（C-09 条件已改），但会让读者以为 C-09 仍被 Gate 卡；冻结字节不能直接改，建议以 **新裁定/errata**（如 GATE-CONTRACT-CLOSURE 增补一节或 C-09 冻结记录 §1B/§3 引用说明）统一更正，并顺手修矩阵 `:20`（C-01b「③（用户 R）」）、`:23`（C-04b「5 项全未满足」）、`:25`（C-06「`G-CONTRACT: OPEN`」）三处陈旧阻塞列。

### 2.8 P2-7：条件③ 含 C-08

`:179` 列「C-01b、C-04b、C-06、**C-08**、C-14 均已冻结…且 `G-CONTRACT` 已关闭…不代表 `G-DELETE-CONTRACT` 关闭…**不引入「部分关闭」**」✓

---

## 3. 新增问题（P2 × 5，非阻断）

1. **K-1（`SC-B04a` `:80` 字段路径）**：「人工 revision / 当前 revision → 披露（PD-01，`contentSummary` / `pinnedRevisionIds`）」——`pinnedRevisionIds`/`currentRevisionId` 在 **`protection`** 下（C-04b `:43`），人工 revision 数是 `protection.manualRegionCount`；`contentSummary` 只含 chapters/pages/artifacts/deletedFiles/deletedBytes。建议改为「`protection.manualRegionCount` / `protection.currentRevisionId` / `protection.pinnedRevisionIds[]`」。
2. **K-2（`SC-B01a` `:43`）**：`backup/2` 行「是否入包 = 是（本契约写端产物）」易误读；建议改「不适用（备份包本身是产物，不入包）」。
3. **K-3（`SC-B01a` `:45` 路径前缀）**：C-03 记 `theme-settings.json` 在 `%APPDATA%/NewManga/` 根下（`ThemeSettingsStore.cs:7`），C-09 写成 `settings/theme-settings.json`；`settings/*.json` 在 C-01b 语境指 provider/network/bindings 一类。建议以 C-03 为准不写死 `settings/` 前缀，或注明「路径以 C-03 冻结记录为准」。
4. **K-4（`SC-B06` `:117`）**：把 M2-C1 冻结的 `ListRecycleBinBooks`（Core command，rev 2.11）说成「Host 投影」；建议改为「已冻结 Core command；`ListTrash` 为其底层能力/替代候选，映射在实现 Task 确认」。
5. **K-5（外部记账，见 2.7）**：C-13 `:203`、三份冻结记录、GATE-CLOSURE-RULING `:63`/`:111`、ADJ-001 `:128` 仍写「C-09 等两 Gate/循环」；矩阵 `:20`/`:23`/`:25` 阻塞列陈旧。建议新裁定/errata 统一更正（冻结字节不直接改）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文。
- 未参与 C-09 起草与 v4 修订（作者 = DSH）；本轮逐字对照 ADJ-001 PD-01/PD-08 原文与 C-04b 字段定义，未按 DSH 的转述判定。
- 我出具过 C-09 的 r3（changes_requested）与更早的 FEA-GOV-7 r1/r2 复核（如实披露）。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 本仓 checkout 无 `src/`（C#/Python 源码不在该树上），未复核 `ThemeSettingsStore.cs`/`nmbak.py` 实际路径与实现——K-3 只按 C-03 文档口径提出。
- 未核 SC-B02/B03/B05/B08/B09 的语义质量（本轮只核 r3 的 8 处）。
- 未核 M2-C1 §5.11.3 的实际扩位空间（只确认无 `TRASH_` 重名）。
- 未核 C-09 与 C-13/C-14 接口的深层一致性（只确认 §3 新增两行存在且表述合理）。

—— 报告结束（`verdict: approved`；8 处全部到位；P2×5 为文字精度/外部记账类 K 项，不阻断 AC7）。
