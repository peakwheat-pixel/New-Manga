---
document_id: FEA-C09-r3
kind: independent_review
task_id: task-31（FEA-D07-UNBLOCK AC7）
round: 3
scope: C-09 D07 承载条款独立复核（解环 + 五项 D07 条款）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-31"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: ad6db87c1
reviewed_head_full: ad6db87c18e8c470cc746f958a37d46c248862b9
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == ad6db87c1）；task-31 不存在，按 Lead 指令直接执行、报告名不变"
reviewed_documents:
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md（v3，174 行，blob sha256 65ab692d…）
  - doc/plan/FEA-01_CONTRACT_DRAFT.md `:58`（C-09 声明范围）
  - doc/tasks/FEA-D07-UNBLOCK.md（AC1–AC8）
  - 对照：ADJ-001 PD-01/PD-08、C-01b SC-10a/10b/13/17、C-04b 码表、M2-C1 §5.5/§5.11（`ListRecycleBinBooks`）、C-03（`presentation-settings.json`）、方案 `:520`/`:901`
reviewed_sha256:
  doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md: 65ab692d731bb143d28afac78f61767b82aabe8eb2a8524d4acd1c963d3f892c
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 1
p2_count: 7
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
verifypins: "PASS (all 12)，EXIT=0，本次实跑"
captured_at: 2026-11-01T10:58:00+08:00
captured_by: c01b-reviewer
---

# 独立复核 r3：C-09 D07 承载条款（解环 + 五项补齐）

**本报告不是** 冻结动作、不释放任何 Task。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 1** / P2 × 7）。**

**解环成立 ✓；D07 七项里 6 项有落点、1 项（独占写锁与 pin）无显式落点；新增条款文本大体扎实。但有 1 条 P1 必须修：`SC-B04a` 的「彻底删除」列与冻结的 ADJ-001 语义相反**（把「披露」写成了「阻止」，把「可安全拆分的共享引用不阻断」写成了阻断），而且**条款自己的验证句与表格自相矛盾**。这正是「引用不复写」的反例——它声称引用 ADJ-001，实际改写了语义。

| 6 处核对 | 结果 |
|---|---|
| 1. 解环是否真成立 | **✅ 成立**（C-09 §4 条件③ 已不含 `G-DELETE-CONTRACT`）；**但矩阵 `:28`/`:53` 仍写旧的两 Gate 依赖（残余，P2）** |
| 2. D07 七项是否全覆盖 | **⚠ 6/7**（第 7 项「独占写锁与 pin」无显式落点，P2-1）；另 AC4 的 `backup/1`、`backup/2` 归属漏项（P2-2） |
| 3. 3 个新码 | **✅ 无冲突/无重复**（M2-C1 与 C-04b 均无 `TRASH_` 码）；⚠ `TRASH_ENTRY_NOT_FOUND` 的 category 应为 `not_found` 而非 `validation`（P2-4） |
| 4. `backup/2` | **✅ 自洽**（版本协商/legacy 只读/写端只写 v2）；⚠ 与方案 `:520` 的格式命名三套叫法需统一（P2-5）；与 C-01b SC-10a/10b 无实质双权威 |
| 5. `SC-B04a` | **❌ P1**（与 ADJ-001 PD-01/PD-08 相反 + 条款内自相矛盾） |
| 6. `SC-B01a` catalog | **✅ 判定可成立**（不纳入/可重建），与 ADJ-001/AD-003 无冲突；⚠ `settings` 文件名写错（`appearance*.json` 不存在）、与 C-01b SC-10b 口径需注明（P2-3） |

---

## 2. 6 处核对明细

### 2.1 解环 —— **✅ 成立**（附矩阵残余）

- `FEA-C09:165`（§4 条件③）现文：「**上游契约已冻结**：C-01b、C-04b、C-06、C-14 均已冻结（本契约显式依赖它们的 source/缓存/删除/授权面）；且 **`G-CONTRACT` 已关闭（2026-11-01）**。**本契约不再要求 `G-DELETE-CONTRACT` 关闭**——本契约正是 D07 的承载者之一；D07 的完整覆盖由「本契约冻结 + C-04b + C-01b 相关条款」共同满足，届时才重新判定 `G-DELETE-CONTRACT`。**不引入「部分关闭」Gate 状态**。」
- 我按依赖图走了一遍：`G-DELETE-CONTRACT` 要 D04–D07 冻结 → D07 的承载 = C-09 + C-04b + C-01b → C-09 的条件只要求「上游契约冻结 + `G-CONTRACT` 关闭」→ `G-CONTRACT` 已关闭（`FEA-CONTRACT_FREEZE_MATRIX.md:10`/STATUS 均记 2026-11-01）→ **无任何路径再要求「C-09 等 Gate、Gate 等 C-09」** ✓。C-09 §4 条件②（C-01b 已冻结）与③重复但无害。
- **残余循环语句（P2-6）**：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:28`（C-09 行）仍写「②`G-DELETE-CONTRACT` + `G-CONTRACT` 关闭」、阻塞列仍「两 Gate」；`:53` 第 7 步仍「C-09 冻结（两 Gate 关闭）」。矩阵自称「不是冻结令」，且这是 AC8 待办；但**按矩阵执行仍会卡回循环**——建议 AC8 时一并改。

### 2.2 D07 七项覆盖（FEA-01 `:58`）

| # | D07 声明项 | 承载 | 判定 |
|---|---|---|---|
| 1 | 软删/恢复/TrashEntry 新命令面 | `SC-B06`（`:91`–`:117`）：MoveToTrash/RestoreFromTrash/ListTrash/PurgeTrash + 3 码 | ✅（关系见 P2-4） |
| 2 | 三路径统一 ProtectionPolicy | `SC-B04a`（`:69`–`:82`）：共通函数 + 三路径表 | ⚠ 结构 ✓，**语义 P1** |
| 3 | 备份覆盖清单（settings/catalog） | `SC-B01` + `SC-B01a`（`:24`–`:43`） | ✅（P2-3） |
| 4 | `backup/2` | `SC-B07`（`:120`–`:128`） | ✅（P2-5） |
| 5 | `DatabaseId` | `SC-B03:56` + SC-B07/B08 引用 C-01b SC-18 | ✅ |
| 6 | 自动备份调度归属 | `SC-B08`（`:131`–`:140`） | ✅ |
| 7 | **独占写锁与 pin** | 仅由 **C-01b SC-17**（独占维护锁，迁移）与 **C-01b SC-13**（备份一致性：pin 文件集合）承载；**C-09 自身无对应条款**，§3 接口（`:155`）只列 SC-10a/10b、SC-30/31/33，未引 SC-13/17 | **⚠ P2-1** |

**结论**：D07 七项**都有冻结承载**（第 7 项靠 C-01b），但 C-09 作为「D07 完整承载者」的自我声明（`:165`）与 §3 的接口清单**没把第 7 项映射写出来**——按上一轮 Gate 复核的标准，这属于记账不完整。

### 2.3 三个新错误码 —— ✅ 无冲突，1 处属性建议

- **无冲突/无重复**：`M2-C1` 全文无 `TRASH_` 码；`C-04b` 码表也无 `TRASH_` 码 ✓。C-09 `:102` 已明说「本契约新增；**须在实现前走 M2-C1 的独立字节修订 Task**」✓。
- **属性（P2-4）**：`TRASH_ENTRY_NOT_FOUND` 用 `validation`，而 C-04b 的同类语义码 `BOOK_NOT_FOUND` 用 `not_found`（`:70`，M2-C1 类别表也含 `not_found`）→ 建议改 `not_found`，保持跨契约码表一致。
- 另建议补一句「M2-C1 字节修订复核须含**负向对照**（未扩展时 host 投影对未知码的降级/透传行为）」，与 C-08 块②、C-04b R-2′ 同口径。

### 2.4 `backup/2` —— ✅ 自洽，1 处命名需统一（P2-5）

- 版本协商自洽：`version > 2` → `BACKUP_FORMAT_UNSUPPORTED`；`version == 1` → legacy adapter（**只读、不写回**）；「不得就地升级为 backup/2，升级须导出新包+校验+原子替换」；写端只写 v2 ✓。
- 与 C-01b **无实质双权威**：SC-10a/10b 管「默认包含/不包含哪些数据类别」，SC-B07 管「格式与版本」，两者分工清楚；SC-B01 的「显式清单」扩展点与 SC-B07 的「强制增量①显式清单」是同一要求的两处表述（C-09 内部重复，非跨契约冲突）。
- **命名三套**：方案 `:520` 叫 `newmanga.backup/2`；SC-B07 用 manifest `format: "nmbak"` + `version: 2`；标题/正文又叫 `backup/2`、`backup/1`。建议统一为「逻辑名 `backup/N`；wire 字段 `format:"nmbak", version:N`」并注明与方案命名的对应。

### 2.5 `SC-B04a` —— **❌ P1（与 ADJ-001 相反 + 自相矛盾）**

- 表格（`:73`–`:78`）「显式彻底删除」列：
  - `region_locked/translation_locked/inpaint_locked` → **阻止**（须先列清单并经 PD-01 披露）
  - 人工 revision / 当前 revision → **阻止**（含在 `protection` 披露）
  - 活动草稿 → **阻止**（`draftPageCount`）
  - 共享引用 → **阻止**（`BOOK_DELETE_CONFLICT`）
- ADJ-001 冻结文本：
  - **PD-01**「影响清单…逐项计算并**不得写入任何状态**：…锁定区域数、current Revision、pinned Revision…活动草稿页数、**非终态 Run/Task（同时作为 `BOOK_BUSY` 阻断项）**…」——**披露项不是阻断项**；唯一阻断引用是 `BOOK_BUSY`。
  - **PD-08**「**可安全拆分**的共享引用**不是**删除阻断条件——删除目标项目自有的内容行与清单内自有文件，**保留共享物理原文件与其他项目的绑定**」——只有「无法安全拆分/关系图不一致/未列明的目标外引用」才 fail-closed。
- 条款内矛盾：SC-B04a 自己的验证句（`:80`）写「彻底删除需 **PD-01 披露**」，与表格「阻止」相反。
- 结论：这是**把 ADJ-001 的「披露/确认」语义改写成了「阻止」**，且把 PD-08 的「可安全拆分不阻断」写反——正是本轮要防的「引用不复写」反例。
- 修法：彻底删除列改为「**披露（PD-01）+ 专门确认**」；共享引用行改为「**不可安全拆分时** → `BOOK_DELETE_CONFLICT`（PD-08）」；活动草稿/锁/revision 行同样改为披露口径（与 C-04b 的 `BOOK_BUSY` 只对非终态 Run/Task 一致）。

### 2.6 `SC-B01a` catalog 判定 —— ✅ 可成立

- 判定「不纳入备份，理由 = 可重建（派生索引）」：ADJ-001 只冻结删除语义、AD-003 §3.3 备份规则未提 catalog → **无冲突**；方案 `:901`「catalog.sqlite 归属待 D07 冻结」→ 本表给出归属与理由，**该项解决** ✓。
- 需补口径（P2-3）：① 验证句断言 `settings/appearance*.json` 存在——C-03 确立的文件是 `presentation-settings.json`（新）与 `theme-settings.json`（旧、迁移期后只读），**`appearance*.json` 不存在**，验证不可执行；② C-01b SC-10b 冻结面记录「`settings/*.json`、`catalog.sqlite` 未入包」（现状注记）与本表「非凭据类 settings 入包」存在口径差，建议写明「本表是对 SC-10b 现状注记的更新/细化」；③ catalog 是否属于 SC-10b 列举的「恢复所需索引」需一句否定（可重建 ⇒ 不属于），否则易读成双权威。

---

## 3. 新增问题（P2）

1. **P2-1**（D07 第 7 项映射缺失，`FEA-C09:155`）：§3 未引 C-01b **SC-13**（备份 pin）/ **SC-17**（独占维护锁）；SC-B03 只在迁移语境提 SC-17。建议补「备份期独占写锁与文件 pin 由 C-01b SC-13/SC-17 承载，不复写；本契约只在 SC-B03 细化迁移场景」。
2. **P2-2**（AC4 漏项）：任务 AC4 要求 `settings/*.json`、`catalog.sqlite`、**`backup/1`、`backup/2`** 各自归属；SC-B01a 归属表无 backup/1、backup/2 两行（虽然 FEA-01 `:58` 的声明范围只要求 settings/catalog）。建议补两行（备份包自身不入包 / 旧包仅作为输入）。
3. **P2-3**（SC-B01a 措辞，见 2.6）：`appearance*.json` → `presentation-settings.json`/`theme-settings.json`；补「对 C-01b SC-10b 注记的更新」一句；补 catalog 不属于「恢复所需索引」一句。
4. **P2-4**（SC-B06，见 2.3）：`TRASH_ENTRY_NOT_FOUND` 的 category 改 `not_found`；补 `ListTrash` 与 M2-C1 冻结的 `ListRecycleBinBooks`（M2-C1 `:150`，只返回软删**作品**）的层级关系（条目级 vs 作品级，是否共存/替代）；补 `PurgeTrash` 的 `TrashEntryRef` 与 C-04b `book_ids` 的映射；补 M2-C1 字节修订的负向对照要求。
5. **P2-5**（SC-B07 命名，见 2.4）：统一 `backup/N` 与 `format/version` 的叫法，并注明与方案 `:520` `newmanga.backup/2` 的对应。
6. **P2-6**（矩阵残余循环，见 2.1）：`FEA-CONTRACT_FREEZE_MATRIX.md:28`/`:53` 仍写「两 Gate」；另 `:23` C-04b 行「5 项全未满足」陈旧（上一轮已报，仍未改）。
7. **P2-7**（§4 条件③ 与 §3 接口不一致）：条件③列 C-01b/C-04b/C-06/C-14，而 §3 接口（`:153`–`:159`）还含 **C-08**；建议在条件③补 C-08（已冻结）或说明「C-08 只作接口、不作前置」。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具，`reviewer_kind: subagent`，独立上下文；**task-31 不存在**，按 Lead 指令直接执行、报告名不变。
- **未参与** C-09 起草与 v3 修订（作者 = DSH），未参与 ADJ-001/其他契约冻结。
- 我出具过 C-09 的 FEA-GOV-7 r1/r2 复核（如实披露）；本轮按「解环是否真的无残余、七项是否真的都有落点」逐字核，不因 v2 approved 而放宽。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`。

---

## 5. NOT_RUN

- 未运行程序/pytest；全部为文档、git 历史与脚本输出比对。
- 未核 SC-B06 四命令与 C-07 API inventory 的兼容（C-07 只列现有 API）。
- 未核 `SC-B02`/`SC-B03`/`SC-B05` 的语义质量（本轮只核解环与五项新增）。
- 未核 M2-C1 §5.11.3 码表的实际扩位空间（只确认无 `TRASH_` 重名）。
- 未核 C-13/C-14 接口细节（只确认 C-09 §3 新增两行存在）。
- 未核 FEA-D07-UNBLOCK AC7 的其余记录项（任务文件 AC 复选框仍为未勾选状态，属正常）。

—— 报告结束（`verdict: changes_requested`；解环 ✅，D07 6/7 有落点，P1 = SC-B04a 与 ADJ-001 语义相反；P2 × 7）。
