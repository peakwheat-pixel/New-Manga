---
document_id: FEA-C13-r2
kind: independent_review
task_id: FEA-C13
round: 2
scope: very-narrow（只核 r1 的 P1×2 + P2×9 处置，共 11 处）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-28（独立上下文；未参与 C-13 v2 修订）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-C13-r1（r1：changes_requested，P0×0 / P1×2 / P2×9）
reviewed_head: 53b3048ee
reviewed_head_full: 53b3048ee6181b5db5ad4c3c94e0a43a2764fe95
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 53b3048ee）；task-28 不存在，按 Lead 指令直接执行、报告名不变"
reviewed_document: doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md（v2，210 行）
reviewed_sha256: 9b60c9f16143a48af3960fcc252cd6dbc377501fa4da0c7b1140043c85d57cff
reviewed_sha256_basis: "HEAD 的 LF blob（由 53b3048ee 引入）"
baseline: "doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md §13.2 `:767` · src/domain/regions/entities.py `:204-219`（TextStyle）· src/infrastructure/sqlite/schema.py `:224-281` · src/infrastructure/sqlite/regions.py `:461` · C-04b（**已冻结**，§2.1 `:42-47`、§2.2 `:49-58`、码表 §2.3）· C-08 · C-05"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 8
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T09:07:05+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（极窄面）：C-13 草稿与保护契约 v2

**本报告不是** 冻结动作、不释放任何 Task。本轮只核 r1 的 2×P1 + 9×P2 是否处置到位、有无引入新矛盾。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 8）。**

**11 处中 6 处完全到位，5 处部分/未到位**：

| # | 项 | 结果 |
|---|---|---|
| P1-1 | SC-D10 白名单改为 `TextStyle` 真实 6 键 | **✅ 完全到位**（逐字一致，见 §2） |
| P1-2 | SC-D12 `protectionDigest` | **⚠ 部分**（公式只用现有列 ✓、零迁移 ✓；但引入新错误码 + 要求冻结契约变更未走 UNFREEZE → **P1-1**；分工论证与 C-04b 原文不符 → **P1-2**） |
| P2-1 | 字段数 10→11 | ✅ 到位（`:45`） |
| P2-2 | SC-D09 验证 | ⚠ 部分（已补 `:124`，但「pivoted 键」无定义 + 与 SC-D10 `:141` 矛盾 → P2-1） |
| P2-3 | 去重键统一 | ⚠ 部分（`:176` 已统一 ✓；`:175` 旧表述残留 + 过渡期结束仍无客观判据 → P2-2） |
| P2-4 | `candidate`→`RegionCandidate` | ⚠ 部分（主要位置已改 ✓；§7 `:186` 仍写「同一语义不同层」与 §4 `:101` **自相矛盾** + 裸 `candidate` 残留 → P2-3） |
| P2-5 | 行号修正 | ✅ 到位（`:6` 为 224-249 / 251-271 / 275-281） |
| P2-6 | grep 排除第三方 | ✅ 到位（`:21`） |
| P2-7 | `origin` 取值域 | ❌ 未到位（只把 `provenance` 改名为 `origin`，**无取值域定义** → P2-4） |
| P2-8 | 结果面转交 C-08 | ✅ 到位（`:100`、`:193`） |
| P2-9 | 导出/删除前 flush 提示 | ✅ 到位（`:94`，但它对**已冻结的 C-04b** 提出新要求 → 归 P1-1） |

**两条新 P1 都出在 SC-D12 上**：

1. **P1-1（协议/冻结契约冲突）**：SC-D12 引入**新错误码 `STALE_PROTECTION`**（`:166`/`:169`），并要求 C-04b 的 preflight「记录逐 Region 的 `protectionDigest`」（`:165`）——但 **C-04b 已在 `b3e3220a4` 冻结**，其码表是「12 行稳定 + 2 host 级/兜底 + 2 新增」（`BOOK_DELETE_STALE_PREVIEW` 等），**没有 `STALE_PROTECTION`**（全仓检索仅 C-13 出现）。C-13 未声明对 C-04b 的修改需 UNFREEZE，直接要求冻结契约改行为/加码 = 事实上的 UNFREEZE 级变更。
2. **P1-2（分工论证的事实错误）**：SC-D12 `:162` 称「清单没变但用户刚给某区域加了 Lock，`inventory_digest` 察觉不到」——**与 C-04b 原文不符**：C-04b `:43` 的 `DeletePreviewItem.protection` 已含 `lockCount`/`manualRegionCount`/`currentRevisionId`/`pinnedRevisionIds`/`activeRunIds`/`draftPageCount`；`:46` 的逐书 digest 输入字段**明确包含** `lockCount`、`manualRegionCount`、`currentRevisionId`、`pinnedRevisionIds`；`:57` 还写「目标/**保护集合**/文件清单任一变化即失效」。**单加一个 Lock 会改 `lockCount` → `inventory_digest` 能察觉**。
   真实缺口另有其形：①**计数不变而分布变**（A 加锁、B 解锁 → `lockCount` 相同）；②**region 级**指针变化不进 book 级 `currentRevisionId`。SC-D12 应据此重写分工，而不是用错误反例。

其余 8 条为 P2（SC-D09 inpaint 悬空、SC-D11 残留、§7 矛盾、`origin` 未定义、digest 覆盖面/假阳性说明、SC 编号错乱、粒度成本）。

---

## 2. P1-1 复核明细（SC-D10，完全到位）

- 代码事实（我实核）：`src/domain/regions/entities.py:204-212`
  ```text
  font_family: str = ""            font_size: int | None = None
  text_color: str = ""             stroke_color: str = ""
  stroke_width: float = 0.0        auto_font_size_enabled: bool = True
  ```
  `as_jsonable()` = `dict(self.__dict__)`（`:214-215`）；`from_jsonable` = `TextStyle(**data)`（`:217-219`）；写入路径 `src/infrastructure/sqlite/regions.py:461`。
- C-13 v2 `:128-137` 的 6 键：`font_family` / `font_size`(int?) / `auto_font_size_enabled`(bool) / `text_color` / `stroke_color` / `stroke_width`(float) —— **逐字、逐类型一致，全部 snake_case，无 camelCase 残留** ✓。
- 「扩键 = 先改 `TextStyle` 再 UNFREEZE」（`:139`）✓；inpaint 三键「当前不存在、不冻结」（`:141`）✓；与 C-02 V-05 不同平面的边界声明（`:143`）✓；验证用例改为 `text_color` 正例 + `customFoo` 反例（`:145`）✓。
- → **P1-1 已闭环**。

---

## 3. P1-2 复核明细（SC-D12）

### 3.1 做对的部分 ✅

- 公式只用现有列：`region_locked`/`translation_locked`/`inpaint_locked`（`schema.py:235-237`）、`current_revision_id`（`:238`）、`updated_at`（`:240`）——**全部存在，零 schema 迁移成立** ✓。
- `preflight 记录 → 确认时重算 → STALE_PROTECTION` 的流程逻辑清晰 ✓；`updated_at` 的假阳性被显式承认并定性为 fail-safe（`:167`）✓；验证用例可执行（`:169`）✓。

### 3.2 P1（必须改）

#### P1-A — 新错误码 `STALE_PROTECTION` + 要求冻结的 C-04b 改行为，未走 UNFREEZE

- 位置：C-13 `:165-166`（要求 C-04b preflight 记录逐 Region digest、返回 `STALE_PROTECTION`）、`:94`（要求写进「C-04b 的 preflight 契约与导出实现 Task 的 AC」）。
- 事实：C-04b 已冻结（`b3e3220a4`「冻结 C-04b/C-06」）；其码表为 12 稳定 + 2 host 级/兜底 + 2 新增（`BOOK_DELETE_STALE_PREVIEW`、`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`），**无 `STALE_PROTECTION`**（全仓仅 C-13 两处）；C-04b `:22` 明写错误投影是**封闭联合**、`code` 必须在 §5.11.3 集合内。
- 影响：若按 C-13 现文实现，删除 preflight 会返回一个**冻结契约里不存在的码** → 违反 C-04b 封闭联合；且「preflight 契约增加逐 Region digest」本身就是对冻结契约 `DeletePreviewItem` 出参形状的变更。
- 建议（二选一）：
  1. **复用现有码**：`BOOK_DELETE_STALE_PREVIEW`（C-04b §2.2 `:55` 定义：「不匹配 → conflict / retryable=false，需重新预览」）——语义完全覆盖「保护状态变化需重新预览」，无需新码；
  2. 若坚持新码：在 C-13 明确「需先对 C-04b 走 UNFREEZE + M2-C1 码表修订（2.12 或按序）」，并把该前置写入 C-13 冻结条件。
- 附带：`:94`「该要求写入 C-04b 的 preflight 契约」同样需要 UNFREEZE 路径，不能以「实现 Task 的 AC」代替契约变更。

#### P1-B — 「`inventory_digest` 察觉不到加 Lock」与 C-04b 原文不符

- 位置：C-13 `:162`。
- 反证（C-04b 实核）：
  - `:43` `DeletePreviewItem = { …, protection: { lockCount, currentRevisionId, pinnedRevisionIds[], activeRunIds[], draftPageCount, manualRegionCount }, … }`；
  - `:46` 逐书 digest 输入字段含 `lockCount`、`manualRegionCount`、`currentRevisionId`、`pinnedRevisionIds`、`activeRunIds`、`draftPageCount`；
  - `:57`「目标/**保护集合**/文件清单任一变化即失效」。
  → 单加一个 Lock 会改变 `lockCount`（`manualRegionCount` 也可能变），`inventory_digest` **会**察觉；C-13 的反例不成立。
- 真实缺口（应改写为）：
  1. **计数不变、分布变化**（A 加锁 + B 解锁 → `lockCount` 相同；`currentRevisionId` 是 book 级，region 级 current 变化不体现）；
  2. `updated_at`/区域级 revision 指针等**不在 C-04b digest 输入**内的字段变化；
  3. 逐 Region 的**漂移检测**（book 级聚合看不出一部分区域变、另一部分抵消）。
- 影响：这条错误论证是 SC-D12 的**唯一理由**；若按错误前提冻结，会以「C-04b 不够用」为由向冻结契约加一套并行的 digest（重复且代价高），而真实缺口反而没被准确描述。
- 建议：重写 `:162` 的分工论述（保留结论「两者都要」，但用真实反例），并说明 `protectionDigest` 与 `inventory_digest` 的**优先关系**（preflight 先比 inventory，再逐 Region 比 protection）。

---

## 4. P2（8 条）

#### P2-1 — SC-D09 的 inpaint 条款悬空 + 「pivoted」错词

- 位置：`:121`（「`inpaint_locked=1` → style 中与 **inpaint 相关的键**只读（**白名单见下**）」）、`:124`（验证「样式白名单中的 **pivoted** 键拒」）。
- 矛盾：SC-D10 `:141` 已声明 inpaint 三键**当前不存在、本契约不冻结** → `:121` 指向的白名单里没有任何 inpaint 键；`:124` 的「pivoted 键」也不存在（应为 inpaint 相关键，且当前无键可测）。
- 建议：`:121` 改为「`inpaint_locked=1` 时，**未来若新增 inpaint 样式键**（需先扩 `TextStyle`）按 SC-D10 的白名单拒绝；当前无 inpaint 键，验证以『键不存在时拒绝写入』为负向用例」；删掉「pivoted」。

#### P2-2 — SC-D11 旧表述残留 + 过渡期结束无客观判据（P2-3 未完全处置）

- 位置：`:175` 仍写「同一 `(RegionId, BaseRevisionId)` 的写入…必须幂等」（无内容摘要，与 `:176` 统一键不一致）；`:177` 「过渡期结束条件：…（由实现 Task 判定）」仍无客观判据。
- 建议：`:175` 改为「同一 `(RegionId, BaseRevisionId, 内容摘要)` 的写入必须幂等」；`:177` 改为可判定条件（如「旧路径调用点 = 0 且旧路径测试全部迁移」）。

#### P2-3 — §7 `:186` 与 §4 `:101` 自相矛盾 + 裸 `candidate` 残留（P2-4 未完全处置）

- `:101` 明说「C-08 的 `candidate store` 是 Run 层的临时存储，**二者不是一回事**」；`:186` 却写「本契约的 candidate 与 C-08 的 prepared 是**同一语义在不同层**…」→ 直接冲突。
- 裸 `candidate` 残留：`:22`（「编辑草稿的 candidate 语义未定义」）、`:89`（SC-D06「先成为 candidate」）、`:96`/`:98`（节标题）。
- 建议：`:186` 改为「**不同语义**（编辑层 RegionCandidate vs Run 层 PreparedRun/candidate store），不得互相替代」；`:22`/`:89` 改 `RegionCandidate`；标题保留「candidate-only prepare」可加注。

#### P2-4 — `origin` 仍无取值域（P2-7 未到位）

- 位置：`:102`（`RegionCandidate` 携带 `{candidateId, RegionId, BaseRevisionId, origin}`）。
- 问题：只把 `provenance` 改名为 `origin`，未定义取值（machine/user/imported/restored？pipeline/translate？）。
- 建议：明确「`origin` ∈ `region_revisions.origin` 的同名 4 值（`schema.py:256-257`）」或给出本契约自己的枚举。

#### P2-5 — SC-D12 的 digest 未覆盖 `RegionText` 级 manual flag

- 位置：`:154-157`（公式只用 `regions` 列）。
- 事实：manual protection 的**文本级标志**存在 `RegionText.translation_locked`（`entities.py` 注释与 `service.py:128-129` 的 `any(region.translation_locked or region.text.translation_locked)` 合并逻辑）；该标志序列化在 `text_json` 中，不在 `regions.translation_locked` 列。
- 风险：若「列已镜像文本级标志」的不变量在某个写入路径失效（例如只改文本级 flag 未同步列），`protectionDigest` 会**漏报**保护变化——与「宁可多报不可漏报」的 fail-safe 目标相反。
- 建议：加一句「`regions` 三锁列必须与 `RegionText` 级 manual 标志保持同步（不变量）；preflight 记录 digest 前必须断言该不变量」，或把 `text_json` 的相关位纳入 digest 输入。

#### P2-6 — SC-D12 假阳性来源说明不全

- 位置：`:167` 只把 `updated_at` 列为假阳性来源。
- 事实：公式中 **`current_revision_id` 也会**因保护无关的修订（如普通文本保存）变化 → 同样产生假阳性。
- 建议：改为「`updated_at` 与 `current_revision_id` 均可能因非保护写入变化 → 假阳性是刻意 fail-safe」。

#### P2-7 — SC 编号与顺序错乱

- 现象：`## 5A. Protection 版本`（`:147`）夹在 §5 与 §6 之间；**SC-D12 出现在 SC-D11 之前**（`:149` vs `:172`）。
- 建议：把 SC-D12 移到 SC-D11 之后并改号为 SC-D12（或 D11→D12 重排），节号改 §6、旧 §6 顺延；否则引用「SC-D11/SD-D12」时易错。

#### P2-8 — SC-D12 的粒度与 C-04b book 级 digest 的载荷/一致性成本未说明

- 现象：C-04b preflight 的出参是**逐 book**（`inventoryDigests: {[bookId]: string}`，`:42`）；SC-D12 要求「记录**逐 Region** 的 `protectionDigest`」（`:165`）。一本书可能有数百 Region → 出参体积、跨端传输、重算成本都需说明。
- 建议：明确 digest 形态（①逐 Region digest 数组 + 上限/分页；或②book 级聚合 `protectionDigest`（对逐 Region digest 再 sha256）以与 C-04b 形状对齐），并写进 C-04b UNFREEZE 的增量（与 P1-A 合并处理）。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。**task-28 不存在**，按 Lead 指令直接执行、报告名 `FEA-C13-r2.md`。
- **未参与** C-13 v2 修订（作者 = DSH），未参与 `src/**`/`apps/**` 实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；执行的命令为只读 `check.ps1` 与 `git`/`Get-Content`/`Select-String` 取证。
- **利益披露**：C-13 是 D04 缺口的补洞契约，我 r1 判 `changes_requested`；本轮对「是否真改到位」逐条实核，未因期待冻结而放水。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 53b3048ee`。

---

## 6. NOT_RUN

- 未运行程序/pytest；SC-D10 键、SC-D12 列、C-04b digest 输入字段均为**静态源码/文档**结论。
- 未验证 `protectionDigest` 的实际性能（逐 Region sha256 在大书上的成本）。
- 未核 C-08 的字段级接口（只核 `candidate store` 命名相关行）。
- 未核 U-03 用户裁决（未裁决）。
- 未核冻结矩阵/STATUS 是否需登记 C-13 v2（本轮范围外）。
- 未核 C-04b 冻结记录（`FEA-CONTRACT-FROZEN-C04b.md`）对「后续修改需 UNFREEZE」的具体措辞（若冻结记录已写，P1-A 的处置可引用它）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×8；11 处：6 完全到位 + 5 部分/未到位）。
