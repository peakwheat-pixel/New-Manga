---
document_id: FEA-03-scope-r4
kind: independent_scope_review
reviewer: fea03-scope-reviewer
reviewer_kind: subagent
reviewer_source: "同一独立席位续任（DSH Agent Teams durable teammate `fea03-scope-reviewer`，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 起草、v1–v5 范围冻结、UNFREEZE 载体或 v5 处置起草）"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh
base_commit: fe2fbb113
reviewed_head: fe2fbb113
reviewed_head_full: fe2fbb113acb779dfc254cc37e0e84abce79b8bd
repository: G:/CODEX/New Manga
scope: "FEA-03 范围冻结 v5 独立复核（r3 P1×4/P2×12 逐项 disposition）；C-13 v6 与 UNFREEZE 已在 r3 单独批准、本轮不重审字节，仅确认 pin 未变"
decision: changes_requested
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 12
checkps1: "Governance check: PASS (2 warnings)，EXIT=0"
verifypins: "PIN AUDIT: PASS (all 15)；C13 = 8faf1e805eac（与 r3 相同）；FEA01 = 0370c18932b1（未变）"
captured_at: 2026-11-02T00:02:00+08:00
captured_by: fea03-scope-reviewer
---

# Review：FEA-03 范围冻结 v5（base/reviewed_head = `fe2fbb113`）

**结论：`changes_requested`（P0 × 0 / P1 × 2 / P2 × 12）。不写 `approved`。**

**A（C-13 v6 / UNFREEZE）**：r3 已单独判 `approved`；本轮确认 C-13 契约字节与 pin 未再变动（`8faf1e80…`），不再重审。r3 指出的冻结记录留痕（§1B/§2/§9）本轮已补齐（见 §2.5）。

**B（v5 范围冻结）**：r3 的 P1×4 中 **2 条闭环、2 条 partial**；P2×12 中 **2 条闭环、1 条 partial、9 条 open**。v5 的 commit message 本身只声明处置 P1×4（未声明 P2×12），与派发信息“P2×12 已处置”不一致——本报告按实际 diff 逐条核验。

剩余 P1：
1. **receipt/AC 单复数未同步**：R-RECEIPT-1 已改 `revisionIds` 映射，但 R-RECEIPT-2、R-APPLY-2、AC4、AC15、V8/V20/V21 仍写“同 revisionId / 1 revision”，与 AC7 的多 Region apply 冲突；`commitIntent` 的 `contentDigest` 仍是单值，多 Region 无法逐区恢复。
2. **journal intent 崩溃窗口未完全闭环**：恢复只比对 `contentDigest`，缺“current revision id 不等于 expectedRevisionIds”守卫——apply 内容与 base 相同时会误判已提交；事务失败/receipt 写失败后的 intent 清理与 fail-closed 未定义；页尺寸依赖未写明。

本报告只审范围冻结，不评价实现、不构成实现验收或 Gate 关闭。

---

## 0. 复核对象、方法与环境

**被审 head `fe2fbb113`**（parent `f91a7683b`，即 r3 被审提交；main 线性，工作区 clean）。v5 提交共 6 个文档变更（+305/−10）：

1. `doc/tasks/FEA-03.md`（v5 卡，**+9/−7 行**，实际只改 9 处：标题、Q-11 标注、R-RECEIPT-1、R-APPLY-3、AC11、AC16、V19、新增 V25、closeout）
2. `doc/plan/FEA-CONTRACT-FROZEN-C13.md`（+3/−1：§1B v6 复核行、§2 条件 1b 行、§9 pin 句）
3. `doc/plan/FEA-CONTRACT-FROZEN-FEA01.md`（+4：§6 Errata，FEA-01 本体字节未动）
4. `doc/reviews/FEA-03-scope-r3.md`（+287，r3 报告入库）
5. `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（v5/r4 指针）

**未改**：任何源码、schema、C-13 契约字节、UNFREEZE 载体、GOAL-PROGRESS、TASK_LEDGER、approval/review_appointment 元数据。

**对照材料（只读）**：C-13 v6 全文与冻结记录；`doc/contracts/V11R_REGION_WRITE_CONTRACT.md:146-150`、`:233`；`src/application/editing/{ports.py,service.py,region_canvas.py}`；`src/infrastructure/sqlite/{schema.py,regions.py,library.py}`；`src/domain/regions/entities.py`；`src/domain/pages/entities.py`；r1–r3 报告；v5 commit message。

**环境与只读证据**

- `git rev-parse HEAD` = `fe2fbb113acb…`；`git status --porcelain` 为空（clean）；复核期间未改任何被审文件。
- `verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，C13 `8faf1e805eac`（与 r3 相同）、FEA01 `0370c18932b1`（未变）；`check.ps1` → `PASS (2 warnings)`。
- C-13 文件实际 sha256 仍为 `8FAF1E80…`；FEA-01 冻结记录 §6 Errata 生效但 FEA-01 契约本体未被修改（pin 未变可证）。

**未执行**：未运行 `pytest`/`dotnet test`（无实现可测）；未做运行时崩溃/并发实测；未逐字节重审 C-04b/C-08/C-05（本卡不改）。

---

## 1. r3 findings 逐项 disposition 核验（16 条）

状态：**closed** / **partial** / **open**。

| r3 ID | r3 问题（摘要） | v5 处置（证据） | 核验结论 | r4 关联 |
|---|---|---|---|---|
| R3-P1-01 | AC11/V19 与去重优先矛盾 | AC11 拆四子场景（卡 `:139`）、V19 同步（`:177`）；R-APPLY-3 不再做 DB 内容去重（`:94`），旧路径 revision 不会被“nontoken 重放”命中，stale 路径可达 | **closed**（旧→新未刷新 = stale、base 刷新 = 2、新→旧 = 2、同 token 重放 = 同 revisionIds，与 R-APPLY-2 自洽） | — |
| R3-P1-02 | R-APPLY-3 不可实现 | 改 journal intent 方案（`:94`）：apply 前写 intent、提交后写 receipt 清 intent、重启用 `revision_by_id` + digest 比对；不再依赖 base/摘要列，不再需要应用层访问 batch 事务 | **partial**：可实现了（读方法在写域、current 可取、无缺列/事务依赖），但崩溃窗口未完全闭环 | R4-P1-02 |
| R3-P1-03 | receipt 单 revisionId 与多 Region 冲突 | R-RECEIPT-1 改 `revisionIds: {regionId: revisionId}`（`:84`） | **partial**：receipt 文件 schema 已改；但 AC4/AC15/R-RECEIPT-2/R-APPLY-2/V8/V20/V21 仍为单 revisionId，intent 的 contentDigest 仍单值 | R4-P1-01 |
| R3-P1-04 | AC16 无 V | 新增 V25（`:178`），AC16 引用 V25（`:144`） | **closed**（active 登记 / Session 结束 / 孤儿 / receipt 保留四场景均有期望）；V 矩阵标题与顺序为 P2 | R4-P2-11 |
| R3-P2-01 | 来源仍引 C-13 v5 pin | 来源 2（`:51`）**未改** | **open** | R4-P2-01 |
| R3-P2-02 | 冻结记录 §1B/§2/§9 未按 v6 留痕 | §1B 增 v6 复核行（`:27`）、§2 增条件 1b（`:36`）、§9 pin 句改为 v6（`:115`）；载体时序说明与 §1A③ LF sha 未补 | **closed**（核心三项已补）；低残留归 R4-P2-12 | R4-P2-12 |
| R3-P2-03 | FEA-01 文档旧 pin 波及 | FEA-01 冻结记录 §6 Errata（`:81-83`）：只记 pin 漂移、声明 FEA-01 本体字节不变；`verify_pins` FEA01 仍 `0370c189…` | **closed** | — |
| R3-P2-04 | Q-9 digest 超集口径 | 卡内无说明，Q-9（`:66`）/R-DIGEST-1（`:99`）未改 | **open** | R4-P2-07 |
| R3-P2-05 | “扩展 seam”与铁律 2 张力 | 卡内无说明，R-APPLY-1（`:92`）未改 | **open** | R4-P2-08 |
| R3-P2-06 | 重放/过期 precedence | 卡内未写顺序 | **open** | R4-P2-09 |
| R3-P2-07 | receipt 7 天清理窗口 | R-RECEIPT-3（`:86`）未改 | **open** | R4-P2-10 |
| R3-P2-08 | AC13 基线（tests/domain 不存在 + tests/infrastructure 过宽） | AC13（`:141`）未改；`tests/domain` 当前仍不存在 | **open** | R4-P2-03 |
| R3-P2-09 | `rg` 命令未排除定义 | R-LEGACY-3（`:104`）未改 | **open** | R4-P2-04 |
| R3-P2-10 | C-13 `:94` 导出/删除 preflight deferral | 卡内仍无登记 | **open** | R4-P2-05 |
| R3-P2-11 | V24 .NET 命令 / V22/V23 注入方式 | 未改（`:145`/`:180-183`） | **open** | R4-P2-06 |
| R3-P2-12 | 元数据/写权/AC2 层级 | 标题改 v5；来源 5（`:54`）仍“本版 v3”、approval（`:7`）、review_appointment（`:21`）、AC14（`:142`）、tests/core 写权（`:41-42`）、AC2/V3 未改 | **partial** | R4-P2-02 |

**计数**：closed 4、partial 3、open 9（共 16）。

---

## 2. 逐项核查（对应派发清单 1–6）

### 2.1 R3-P1-01（AC11/V19）

- AC11（`:139`）现为四子场景：旧路径同文两次 = 2；同 token 重放 → 同 `revisionIds`、不新增；**旧→新（base 刷新为旧写入后的 current）= 2**；**旧→新（base 未刷新）= stale 拒绝、1**；**新→旧 = 2**（旧 append）。
- V19（`:177`）与 AC11 一致。R-APPLY-3 改为 intent 方案后，旧路径写出的 revision 不会被“新 token 的 receipt 命中”或 DB 内容去重命中；未刷新 base 的新路径 apply 走 stale → `STALE_BASE_REVISION`。与 R-APPLY-2 的优先级自洽。**R3-P1-01 闭环。**
- 残余：AC11 使用 `revisionIds`（复数），但 AC4/AC15/V8/V20 仍是单数（见 §2.3）。

### 2.2 R3-P1-02（journal intent 方案）

- **写域与读方法**：`RegionRepository.revision_by_id(revision_id)` 属 `src/application/editing/**`（`allowed_paths:30`）＋ `src/infrastructure/sqlite/**`（`:33`）内，可加；`regions.current_revision_id` 可经 `get_region`（`ports.py:20`）读取；`region_revisions` 的 PK 是 `region_revision_id`（`schema.py:251-252`），按 id 查询可行。**不依赖不存在的列，也不需要在 batch 事务内查重** ✓。
- **digest 可比性（含 r3 更正）**：revision snapshot 的 geometry 是页像素（`entities.py` 的 `snapshot_state`）；R-LEGACY-2 的 canonical 要求 `geometry(normalized)`。**更正 r3 报告的一处错误**：r3 称“`pages` 表没有宽高列”不准确——`pages.width/height` 由迁移 `schema.py:186-194`（尤其 `:193-194`）加入，且 `library.py:292-301` 的 `_PAGE_COLUMNS` 读写这两列；因此页尺寸可经 Page 仓储取到（`RegionRepository` 目前不暴露 page 读取，需在 editing/core_assembly 侧注入 Page 读依赖，属写域可解决）。所以 digest 不是“不可比”，而是**卡内未写页尺寸来源与 `PAGE_SIZE_UNAVAILABLE` 处理**（P2 级）。
- **崩溃窗口（未完全闭环）→ P1**：
  1. **缺 base-id 守卫**：恢复只“读 current revision 比对 contentDigest”。崩溃发生在 intent 写后、SQLite 事务提交前时，current 仍是 base revision；若 apply 内容与 base 完全相同（无内容变化的 apply，例如用户未改内容直接 apply / 改后回退），base snapshot 的 digest 与 intent 的 contentDigest 相同 → 会被误判“已提交”并补 receipt，返回 base 的 revision（未写新 revision），与“显式 apply 应产生 revision”的语义不符。恢复应先判断 `current_revision_id != expectedRevisionIds[regionId]`。
  2. **失败路径未定义**：apply 因 stale/protection/DB 失败后 intent 是否清除未写；若残留，重启恢复可能把失败结果误判为已提交或“未提交”（取决于 digest）。receipt 写失败后进程若继续服务（非崩溃），后续 apply 会推进 current，重启恢复时 digest 不匹配 → 清 intent → 同 token 重放重复写。应定义 apply 失败必清 intent、receipt 写失败 fail-closed。
  3. **多 Region digest 单值**：`commitIntent{…, contentDigest, …}` 只存一个摘要，但一次 apply 可含多个 Region（AC7）；逐区恢复/补 receipt 需要 per-region digest 或明确的“combined digest”定义（当前未写）。
  4. **同进程非崩溃恢复**：R-APPLY-3 只描述“重启恢复”；进程内 receipt 缺失而 intent 存在的行为（如 receipt 写失败后同 token 重放）未定义。
- **journal 一致性（P2）**：intent 写入 journal，但 R-JOURNAL-1（`:79`）内容定义仍是“11 字段 + status/savedAt”；AC5/V10 的崩溃点（tmp/rename）未覆盖“intent 已落盘、事务未提交”这一新窗口的恢复断言。→ R4-P2-11。

### 2.3 R3-P1-03（receipt 多 Region）

- R-RECEIPT-1（`:84`）已改为 `revisionIds: {regionId: revisionId}`，文件 schema 自洽 ✓。
- **未同步**：R-RECEIPT-2（`:85`）“读 receipt 返回同 `revisionId`”；R-APPLY-2（`:93`）“返回既有 `revisionId`”；AC4（`:132`）“1 revision、同 revisionId”；AC15（`:143`）“同 token 重放 → 同 revisionId”；V8（`:166`）/V20（`:179`）/V21（`:180`）仍写单数；AC4/AC15 与 AC7 的多 Region apply（3 Region → 3 revision）冲突。**协议 schema 改了，验收语义未改** → 仍为 P1（R4-P1-01）。
- intent（`:94`）的 `contentDigest` 单值问题同属该类。

### 2.4 R3-P1-04（AC16 / V25）

- V25（`:178`）覆盖：`edit-open` 登记 active / Session 结束无残留 journal / 孤儿 `discarded` / receipt 按 R-RECEIPT-3 保留；AC16（`:144`）引用 V25 ✓。**闭环**。
- 形式问题：V 矩阵标题仍写“V1–V24”（`:155`，现已有 V25）；V25 插在 V19 与 V20 之间（`:178`），编号顺序不连续。→ R4-P2-11。

### 2.5 P2 清单核验（派发清单第 5 项）

| 派发项 | 核验结果 | 证据 |
|---|---|---|
| 冻结记录 §1B/§2/§9 按 v6 补齐 | ✅ 核心三项已补 | C-13 冻结记录 `:27`、`:36`、`:115`；§1B 行写“r3 approved、pin `d2cb8de4…`→`8faf1e80…`”，§2 增 1b 行，§9 pin 句已改 v6 |
| FEA-01 冻结记录 Errata 只记 pin 漂移、不改 FEA-01 字节 | ✅ | FEA-01 记录 `:81-83`；`verify_pins` FEA01 仍 `0370c189…`，FEA-01 契约文件不在 v5 提交文件列表 |
| C-13 `:94` 导出/删除 preflight deferral | ❌ 未登记 | 卡内无“导出/preflight/`:94`”字样（grep 无命中） |
| AC13 基线（`tests/domain` 不存在） | ❌ 未处理 | AC13（`:141`）未改；`Test-Path tests/domain` = False；`tests/infrastructure` 仍整目录 |
| `rg` 排除定义 | ❌ 未处理 | R-LEGACY-3（`:104`）仍只有“排除定义与 tests 后 0 命中”，无 flags |
| V24 的 .NET 命令 | ❌ 未加 | AC12/V24（`:140`/`:183`）仍无 `dotnet test` 命令 |
| Q-9 digest 与 SC-D12 公式口径（超集是否需一句） | ❌ 未加 | Q-9（`:66`）/R-DIGEST-1（`:99`）未改；SC-D12 公式仍为 `三锁 + manualFlagIn(text_json)` |
| 重放/过期 precedence | ❌ 未写 | R-APPLY-2（`:93`）、V9（`:167`）未改 |
| receipt 7 天清理后 `EDIT_TOKEN_REUSED` 窗口 | ❌ 未定义 | R-RECEIPT-3（`:86`）/AC15（`:143`）未改 |
| “扩展 seam”与 C-13 冻结记录“不改 ports.py 契约”的张力 | ❌ 未说明 | R-APPLY-1（`:92`）/R-DIGEST-1（`:99`）未改；冻结记录铁律 2 在 `:53` 未动 |
| 来源 v5 pin（r3-P2-01） | ❌ 未改 | 卡 `:51` 仍“C-13 冻结 v5（pin `d2cb8de4…`）” |
| 版本/元数据（r3-P2-12） | ⚠ 仅标题改 v5 | `:54` 仍“本版 v3”；`approval`（`:7`）缺 Q-7…Q-10；`review_appointment`（`:21`）未列 r3/r4；AC14（`:142`）仍写“r3 approved（P0/P1=0）”而 r3 实为 changes_requested；`tests/core` 两文件仍可写（`:41-42`）；AC2/V3 未写 flush 层级 |

**结论**：v5 实际处置的是 P1×4（其中 2 条 partial）＋ 2 条 P2（P2-02 核心、P2-03）＋标题；其余 9 条 P2 未处置。v5 的 commit message 也只列了这些，未声称处置 P2×12（与派发信息不一致，需以 diff 为准）。

### 2.6 新问题（v5 引入/暴露）

1. **R-RECEIPT-2/R-APPLY-2/R-LEGACY-2 仍写“DB 去重”**（`:85`、`:93`、`:103`），但 R-APPLY-3 已明确“不用 DB 内容去重”，三处措辞与新机制冲突，易误导实现（P2-11）。
2. **R-JOURNAL-1 内容定义未含 commitIntent**（`:79`），intent 写入 journal 后与“11 字段 + status/savedAt”定义不一致（P2-11）。
3. **V 矩阵标题 “V1–V24” 与新增 V25 不一致**，且 V25 插在 V19/V20 之间（P2-11）。
4. **AC14 仍写 r3 approved**：r3 实际是 `changes_requested`（P1×4），本轮 r4 也未完成；该 AC 应指向 r4/最新一轮（P2-02）。
5. **GOAL-PROGRESS §3B 未更新**：`:58` 仍写“r2 changes_requested → v4（含 UNFREEZE）| r3 待审”，未记录 r3 结果与 v5（P2-12）。
6. **closeout v5 表述**（`:214`）称“处置 r3（P0=0、UNFREEZE approved、P1×4/P2×12）”，但未列 P2 实际处置范围，读者会误以为 P2 全部闭环（P2-12）。
7. **intent 失败路径**：apply 校验失败/DB 失败后 intent 清理未写；receipt 写失败未定义 fail-closed（已并入 R4-P1-02）。

---

## 3. Findings（r4）

| 编号 | 级别 | 位置 | 问题 | 建议 | 状态 |
|---|---|---|---|---|---|
| R4-P1-01 | P1 | 卡 `:84-86`、`:93-94`（R-RECEIPT/R-APPLY）、`:132`（AC4）、`:143`（AC15）、`:166`/`:179-180`（V8/V20/V21） | R-RECEIPT-1 已改 `revisionIds` 映射，但 R-RECEIPT-2（“同 revisionId”）、R-APPLY-2（“返回既有 revisionId”）、AC4（“1 revision、同 revisionId”）、AC15（“同 revisionId”）、V8/V20/V21（单数）未同步；AC4/AC15 与 AC7 的多 Region apply（3 Region → 3 revision）冲突；intent 的 `contentDigest` 仍单值，多 Region 无法逐区恢复/补 receipt | 把 R-RECEIPT-2/R-APPLY-2/AC4/AC15/V8/V20/V21 统一为 `revisionIds` 映射语义（AC4 明确“单 Region”或写“N Region → N revisionIds”）；intent 改 per-region digest（或写明 combined digest 的定义与比较方式）；V20/V21 增“多 Region 部分命中/全命中”场景 | open |
| R4-P1-02 | P1 | 卡 `:94`（R-APPLY-3）、`:79`（R-JOURNAL-1）、`:133`/`:168`（AC5/V10）、`:143`（AC15）、`:179`（V20） | journal intent 崩溃窗口未完全闭环：①恢复只比对 contentDigest，缺 `current_revision_id != expectedRevisionIds` 守卫——apply 内容与 base 相同时（无内容变化 apply）会误判已提交并补 receipt（返回 base revision、未写新 revision）；②apply 失败（stale/protection/DB）后 intent 是否清除未写；③receipt 写失败后进程继续服务（非崩溃）会使 current 前进，重启恢复 digest 不匹配 → 清 intent → 同 token 重放重复写，未定义 fail-closed；④同进程非崩溃恢复行为未定义 | 恢复顺序：读当前 revision ids → 等于 expectedRevisionIds 则未提交（清 intent）→ 否则逐区比对 digest，一致则补 receipt/清 intent、不一致清 intent；apply 任何失败必须清 intent；receipt 写失败 fail-closed（重试或停止接受新 apply）；写明页尺寸来源（`pages.width/height`，`schema.py:193-194`）与 `PAGE_SIZE_UNAVAILABLE` 处理；V10/AC5 增 intent 崩溃点，V20 增恢复两分支 | open |
| R4-P2-01 | P2 | 卡 `:51`（来源 2） | 来源仍写“C-13 冻结 v5（pin `d2cb8de4…`）”，与 v6/pin `8faf1e80…` 不一致（r3-P2-01 未处置） | 改为 C-13 冻结 v6 + pin `8faf1e80…`，链接 UNFREEZE 载体与 r3 复核 | open |
| R4-P2-02 | P2 | 卡 `:7`（approval）、`:21`（review_appointment）、`:54`（“本版 v3”）、`:142`（AC14）、`:41-42`（tests/core 写权）、`:130`（AC2） | 元数据/写权残留：①来源 5 仍“本版 v3”；②`approval` = `Q1_Q3_Q6_Q11` 缺 Q-7…Q-10；③`review_appointment` 未列 r3（changes_requested）与 r4（待审）；④AC14 仍写“范围复核 r3 approved（P0/P1=0）”，事实错误（r3 为 changes_requested，P1×4）；⑤`tests/core` 两个基线文件仍授予写权；⑥AC2/V3 未写 flush 断言层级 | 统一 v5 版本措辞；`approval` 补全 Q-1…Q-11；`review_appointment` 增 r3/r4；AC14 改“范围复核 r4 approved（P0/P1=0）”；`tests/core` 两文件从写权移除或写明 DSH 批准例外；AC2 注明 Core seam 断言 + UI 接线归 FEA-04/06 | open |
| R4-P2-03 | P2 | 卡 `:141`（AC13） | AC13 基线仍含当前不存在的 `tests/domain`（pytest 会报路径错误）与过宽的 `tests/infrastructure`（plugin 打包等无关项）；未写基线“实现前”如何取得、skip/失败如何裁定 | 明确 `tests/domain` 随新测试创建（或从基线命令移除）、`tests/infrastructure` 收窄到相关文件；基线逐文件 outcome + skip 原因写入 Handoff | open |
| R4-P2-04 | P2 | 卡 `:104`（R-LEGACY-3） | `rg "save_manual_translation\(" src apps` 未给排除定义/tests 的可执行 flags，字面执行会命中 `def save_manual_translation(` | 给出完整命令（如 `rg -t py "save_manual_translation\(" src apps` 并排除定义行/`-g '!**/service.py'`），说明 tests 排除方式 | open |
| R4-P2-05 | P2 | 卡 `:52`、`:143`（AC16）、C-13 `:94` | C-13 `:94` 的导出/删除 preflight deferral 仍未登记（活跃草稿产生后必须显式承接的边界） | 在“来源与授权”或“交付项映射”加一行：本卡不实现导出/删除 preflight，分别由导出 Task AC 与 C-04b UNFREEZE 承载（引用 C-13 `:94`） | open |
| R4-P2-06 | P2 | 卡 `:140`/`:183`（AC12/V24）、`:145`/`:181-182`（AC17/V22/V23） | V24/AC12 无 .NET 测试命令；V22 “data-root 不可写”注入方式未定义；V23 双实例可用同进程两 handle 模拟（r3 已实测）但卡未写；“标记不可持久化”如何表示未定义 | 写明 `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj`；V22 选一种注入方式；V23 写同进程双 handle；定义“不可持久化”标记与对 FEA-04 的暴露方式 | open |
| R4-P2-07 | P2 | 卡 `:66`（Q-9）、`:99`（R-DIGEST-1）；C-13 SC-D12 公式 | digest 输入是三锁 + `text_json.translation_locked` + `text_json.manual_edited`，是 SC-D12 公式（`三锁 + manualFlagIn(text_json)`）的超集；方向正确但需口径说明，避免实现复核按字面判偏离 | 在 Q-9 或 C-13 冻结记录 Errata 写清“`manualFlagIn(text_json)` 的实现取 `translation_locked` 与 `manual_edited` 的派生，二者均属保护位；无假阳性” | open |
| R4-P2-08 | P2 | 卡 `:92`（R-APPLY-1）、`:99`（R-DIGEST-1）；C-13 冻结记录 `:53`（铁律 2） | R-APPLY-1 要求“保护/digest 检查在事务内（扩展 seam）”，但 C-13 冻结记录铁律 2 写“这是实现 Task 的 AC，不是改 `ports.py` 契约”；扩展 `commit_region_batch` 签名/`RegionLockSnapshot` 是否算改契约未界定 | 明确扩展形态（向后兼容的可选关键字参数或新 committer 方法，不改既有调用语义），并在 C-13 冻结记录 Errata 记录该解释；或改用适配器内部比较（不改协议），二选一写入卡内 | open |
| R4-P2-09 | P2 | 卡 `:89`（R-TOKEN-1）、`:93`（R-APPLY-2）、`:132`（AC4）、`:167`（V9） | 重放/过期 precedence 未写：SC-D04 要求过期 token 拒绝并返回 `EDIT_TOKEN_EXPIRED`；R-APPLY-2“先查 receipt”若先于 token 校验，过期重放会返回 revision 而非过期错误 | 写明前置顺序：token 存在/归属/未过期 → receipt 命中（返回 revisionIds）→ stale → 写；补 V9/V20 交叉场景（过期 + receipt 命中） | open |
| R4-P2-10 | P2 | 卡 `:85-86`（R-RECEIPT-2/3）、`:143`（AC15） | receipt 在 Draft `discarded` 或 7 天未活动时删除；删除后 `EDIT_TOKEN_REUSED`（同 token 不同内容）不可判，AC15 该断言隐含时间窗口但卡未定义 | 定义幂等窗口（receipt 保留至 Draft 清理，或明确 7 天后只保证同内容幂等），并写明清理后不同内容重放的行为 | open |
| R4-P2-11 | P2 | 卡 `:79`（R-JOURNAL-1）、`:85`/`:93`/`:103`（旧“DB 去重”措辞）、`:155`（V1–V24 标题）、`:178`（V25 位置）、`:133`/`:168`（AC5/V10） | journal intent 的一致性缺口：①R-JOURNAL-1 内容定义未含 `commitIntent`；②R-RECEIPT-2/R-APPLY-2/R-LEGACY-2 仍写“DB 去重/返回 revisionId”，与 R-APPLY-3 新机制冲突；③V 矩阵标题仍“V1–V24”但已有 V25，且 V25 插在 V19/V20 之间；④AC5/V10 未覆盖 intent 落盘而事务未提交的崩溃恢复断言 | 更新 R-JOURNAL-1 内容定义（含 `commitIntent`）；把三处“DB 去重”改为 receipt/intent 措辞；V 矩阵标题改 V1–V25、V25 移到末尾；AC5/V10 增“intent 已落盘、事务未提交”崩溃场景 | open |
| R4-P2-12 | P2 | `doc/checkpoints/GOAL-PROGRESS-2026-11-01.md:58`、卡 `:214`（closeout）、C-13 载体 `:45-58` | ①GOAL §3B 的“范围复核”行仍停在 r2 changes_requested → v4（含 UNFREEZE）与“r3 待审”，未记录 r3 结果与 v5；②closeout v5 称“处置 r3（P0=0、UNFREEZE approved、P1×4/P2×12）”，未列 P2 实际处置范围（实际仅 2 条 P2 + 标题），易误读为全部闭环；③C-13 载体 §4/§5 仍写“复核通过后更新记录”，与记录已在 v5 更新的事实不符；§1A③ LF blob sha 未补 | 更新 GOAL §3B（r3 changes_requested → v5、r4 待审）；closeout 列出 P2 处置范围（或写明“P2 部分处置、余项见 r4”）；载体补“记录已预置、r3 通过后确认生效”的时序说明，补 LF blob sha | open |

---

## 4. 验证记录（实际执行）

| 场景 | 命令/步骤 | 环境/commit | 结果 | 证据/备注 |
|---|---|---|---|---|
| HEAD 与工作区 | `git rev-parse HEAD`；`git status --porcelain` | `fe2fbb113`，main | PASS（clean） | `fe2fbb113acb779dfc254cc37e0e84abce79b8bd` |
| v5 提交范围 | `git show --name-status`；`git diff --stat f91a7683b..HEAD` | `fe2fbb113` | 6 文件（卡/C-13 记录/FEA-01 记录/r3 报告/STATUS/PLAN） | 无源码、无 schema、无 C-13 契约字节改动 |
| C-13 / FEA-01 pin | `verify_pins.ps1`；`Get-FileHash` | `fe2fbb113` | C13 `8faf1e80…` 未变；FEA01 `0370c189…` 未变 | `PIN AUDIT: PASS (all 15)` |
| 治理检查器 | `check.ps1` | `fe2fbb113` | PASS（2 warnings） | 11 非终态 Task；STATUS 3169 bytes/31 lines 80% |
| card diff 逐行 | `git diff f91a7683b..HEAD -- doc/tasks/FEA-03.md` | `fe2fbb113` | 仅 10 处修改：标题/Q-11/R-RECEIPT-1/R-APPLY-3/AC11/AC16/V19/V25/closeout | 其余规则/AC/V 未动 |
| r3-P2 逐项 | 读卡全文 + grep 导出/preflight/rg/tests/domain/V24 | `fe2fbb113` | 9 条 P2 未处置、1 条 partial | 见 §2.5 |
| revision_by_id 可行性 | 读 `ports.py:17-34`、`schema.py:251-252`、`regions.py` | `fe2fbb113` | 无现有实现；PK 可查；写域允许新增 | R4-P1-02 部分可解 |
| pages 尺寸（r3 更正） | 读 `schema.py:186-194`、`library.py:292-301`、`pages/entities.py` | `fe2fbb113` | `pages.width/height` 存在（迁移 `:193-194`） | r3 结论更正 |
| 多 Region AC 一致性 | 读 AC4 `:132`、AC7 `:135`、AC15 `:143`、V8/V20/V21 | `fe2fbb113` | AC4/AC15/V8/V20/V21 仍单数，与 AC7 冲突 | R4-P1-01 |
| GOAL/closeout/carrier | 读 GOAL `:58`、卡 `:214`、载体 `:45-58` | `fe2fbb113` | GOAL 未更新；closeout 未列 P2 范围；载体时序未改 | R4-P2-12 |
| 运行 pytest / dotnet test | — | — | **NOT_RUN** | 无实现可测；范围冻结阶段 |
| 崩溃/并发实跑 | — | — | **NOT_RUN** | 无实现 |
| C-04b/C-08/C-05 正文 | — | — | **NOT_RUN** | 非本卡写域 |

---

## 5. r3 自我更正

r3 报告 §3.2 第 ③ 点与 §5 验证表曾写“`pages` 表没有宽高列（`schema.py:54-63`）”，并据此把“normalized geometry 需页尺寸”列为 P1 不可实现点之一。经本轮复核：`schema.py` 的 `pages` 基础 DDL 之后有迁移段 `:186-194`，其中 `:193-194` 加入 `width`/`height`；`library.py:292-301` 的 `_PAGE_COLUMNS` 读写这两列。**页尺寸可从 pages 表取得**，该点因此降级：不是“不可实现”，而是“卡未写页尺寸来源与 `PAGE_SIZE_UNAVAILABLE` 处理”（P2 级，已并入 R4-P1-02 的建议）。特此更正并保留在案。

---

## 6. 边界声明、结论与复审

**边界声明**

- 本 Review 只审 v5 范围冻结与 r3 findings 的 disposition；C-13 v6/UNFREEZE 已在 r3 单独 approved，本轮只确认 pin 未变，不重审契约字节。不评价实现、不构成实现验收、不构成 Task 释放或 Gate 关闭。
- 未修改任何被审文件；未 commit、未 push；只新增本报告。未访问用户数据。
- `check.ps1`/`verify_pins.ps1` 的 PASS 是机械结果，不替代范围判定。

**关键结论**

- **`changes_requested`（P0 × 0 / P1 × 2 / P2 × 12）。不写 `approved`。**
- r3-P1-01 闭环（AC11/V19 四子场景与 R-APPLY-2 自洽）；r3-P1-04 闭环（V25/AC16）。
- r3-P1-02 **partial**：journal intent 方案可落地（读方法/current 可读/无缺列/无事务依赖），但崩溃窗口仍有 4 个未闭环点（base-id 守卫、失败路径、per-region digest、同进程非崩溃恢复）→ R4-P1-02。
- r3-P1-03 **partial**：receipt schema 已改 `revisionIds`，但 AC4/AC15/R-RECEIPT-2/R-APPLY-2/V8/V20/V21/intent 仍单数 → R4-P1-01。
- r3-P2×12：closed 2（P2-02 核心、P2-03）、partial 1（P2-12）、open 9（P2-01/04–11）；v5 的 commit message 也只声明 P1×4，派发信息“P2×12 已处置”与 diff 不符。
- C-13 记录 §1B/§2/§9 已补齐 ✓；FEA-01 Errata 只记 pin 漂移且 FEA-01 字节未变 ✓；C-13 `:94` deferral、AC13 基线、rg、V24 命令、Q-9 口径、precedence、7 天窗口、seam 张力均仍未处置。

**建议最小闭环顺序**

1. **R4-P1-01**：把 R-RECEIPT-2/R-APPLY-2/AC4/AC15/V8/V20/V21 统一为 `revisionIds` 映射；intent 增加 per-region digest 或定义 combined digest；V20/V21 增多 Region 全命中/部分命中场景。
2. **R4-P1-02**：恢复增加 `current_revision_id != expectedRevisionIds` 守卫；apply 失败清 intent；receipt 写失败 fail-closed；写明页尺寸来源（`pages.width/height`）与 `PAGE_SIZE_UNAVAILABLE`；V10/AC5/V20 增 intent 崩溃与恢复两分支。
3. **R4-P2-11**：更新 R-JOURNAL-1 内容定义、三处“DB 去重”措辞、V 矩阵标题/顺序、AC5/V10 intent 崩溃点。
4. **R4-P2-01/02/03/04/05/06/07/08/09/10/12**：按 §3 表逐项处理；其中 P2-01/02/12 为机械性文档项，可与上述修改同一处置提交完成。
5. 修订后以新 head 提交，派 r5（可基于 diff 复审）；只有 P0/P1 清零才写 `approved`。

**复审口径**：r5 需逐条 disposition 本报告 2 条 P1 与 12 条 P2（fixed/deferred with owner/not applicable + 理由），确认 `verify_pins`（C13 `8faf1e80…`、FEA01 `0370c189…`）与 `check.ps1`，并确认 GOAL/STATUS/PLAN/closeout 指针与 v5 实际处置一致；实现复核（`doc/reviews/FEA-03-r1.md`）仍不在本报告范围。

---

*Reviewer：`fea03-scope-reviewer`（DSH Agent Teams durable teammate，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 的起草、v1–v5 范围冻结、UNFREEZE 载体或 v5 处置起草）。日期：2026-11-01/02。*
