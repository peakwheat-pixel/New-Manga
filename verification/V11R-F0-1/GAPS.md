# V11R-F0-1 GAP 清单（能力核实结论，不假装实现）

核实方法：直接阅读 + 运行既有 Core 装配与测试，**不以 grep 缺失单独证明**。
结论分三类：`FILLED`（本任务补齐并标注）、`OPEN`（真实缺口，不属本任务或需 Lead 决策）、
`DECISION`（记录性决策，不是遗漏）。

---

## GAP-1 — `set_region_lock` 在 application 层不存在（本任务 FILLED，必须标注为新增）

**事实**

- 域层已有：`Region.set_region_locked` / `Region.set_inpaint_locked`
  （`src/domain/regions/entities.py`），`RegionText.unlock_translation`（同文件）。
- 域层**缺**“重新上翻译锁”的对称方法；application 层**没有任何**把三把锁持久化为 revision 的
  use case。此前唯一锁写是 `save_manual_translation` 内隐式 `translation_locked = True`
  （`src/application/editing/service.py:849` 起），无法显式解锁/加锁。
- D06 §87 要求锁变更产生 revision；因此不能靠“直接改列”实现。

**处置（已实现）**

- 新增 `RegionEditingService.set_locks()`（`service.py:904`）：薄的 use case，组合既有域
  setter，走同一 `commit_region_revision` 原子 seam，一次调用 = 一个 user revision。
- 新增 `RegionText.lock_translation()`（`entities.py:191`）与
  `Region.set_translation_locked()`（`entities.py:270`）。
- 明确记录：**该 use case 为 V11R-F0-1 新增**（契约 §2 C075/§5），不是既有能力。
- 测试：`tests/editing/test_region_write_guards.py`（revision+1、双投影、解锁清旗标）；
  `tests/core/test_region_write_commands.py`（锁变更 → revision+1 → 重启后仍锁定）。

---

## GAP-2 — Region 文本只读投影缺失（OPEN，超出 F-01 范围，需 Lead 决策）

**事实**

- `list_regions`（C043）返回的 `RegionListSummary` 是**最小 5 字段** + 可选 normalized
  `geometry`：`region_id / region_type / sfx_policy / origin / revision_no`
  （`service.py:498` `list_region_summaries`），不含任何文本。
- `list_region_revisions`（C044）返回 revision 摘要（`service.py` `list_revision_summaries`），
  不含快照文本、不含 `text` 字段。
- 全仓 IPC 命令清册（审计 §5）没有其它 region 文本读命令；`rerender_page` / 资源命令都不带文本。
- 本任务写命令的 result 回显了“本次写后”的 `text`，但那只能覆盖刚写过的 region，不能用于页面初次载入。

**影响（必须诚实声明）**

Studio · Page 模式初次打开一页时，IPC 上没有通道读取已存在的四级文本
（ocr/machine/edited/final）与锁/确认状态；UI **不得伪造**文本或把它标成“能力待接入”以外的样子
（FUSION_SPEC §4 的 A 类映射规则：UI 标注“能力待接入”而不是假装可用）。

**建议（Lead 决策，不在本任务实施）**

1. 新增读命令（更干净）：`get_region`（region 详情：text/四轨/lock/revision 摘要）或
   `list_region_texts {page_id}`，minor 3，只读；
2. 或对 C043 做 additively widening（增加 optional `text` 字段）——但 C043 是既有冻结命令面，
   需 DSH/契约裁决，不能由本任务单方改；
3. 若采用方案 1，建议排入 Wave-2 的独立任务（Owner 非本任务），本任务不预留半成品。

---

## GAP-3 — 翻译锁的双投影（既有设计，记录为风险，本任务不改既有语义）

**事实**

- `regions.translation_locked` 列（`src/infrastructure/sqlite/regions.py:59` 读取）与
  `regions.text_json.translation_locked`（同文件 text 状态）是同一概念的两份持久化表示；
- pipeline 的 `LockSnapshot.translation_locked` 读**列**（`src/infrastructure/sqlite/pipeline.py:894`）；
- 人工保护判定与机器写守卫读**文本级**旗标（`RegionText.apply_machine_translation`、
  `service.apply_machine_translation` 的 early check）；
- 既有 `save_manual_translation` 只写文本级，不改列（既有行为，测试 `test_text_protection.py` 固化）。

**处置**

- 本任务的显式 `set_region_lock` 同时同步两份投影（契约 §2 C075），避免 UI 锁操作对 pipeline
  不可见；
- **未改** `save_manual_translation` 的既有行为（改动会变更既有 pipeline 语义，超出本任务授权）；
  该双投影不一致属既有技术债，记录在此供后续任务裁决。

---

## GAP-4 — `create_region` 无 `expected_revision`（DECISION，不是遗漏）

创建不存在“先前 current revision”，且 region_id 由服务端生成，冲突面为零；若强行要求
expected_revision 只能引入伪造语义。契约 §1.4/§2 C067 已冻结说明。其余 9 条命令全部支持乐观锁。

---

## GAP-5 — `IHostController` / `HostController` 无 Region 写便捷方法（边界，不属本任务）

按 `doc/plan/V11R_AVALONIA_CONTRACT.md` §1.2 共享写权：`App/Services/IHostController.cs`、
`HostController.cs` 归 core-bridge；本任务只保证命令在 Host/CoreClient 层真实可调
（`HostRuntime.Commands.InvokeAsync`），UI 任务的便捷方法由对应 Owner 追加。C# 侧无新 DTO
（既有 `HostCommandDescriptor` / `HostCommandResult` 足够），符合“最小改动”。

---

## GAP-6 — 合并/拆分不产生“删除 revision”（既有语义，记录）

`merge_regions` / `split_region` 对源 region 只做软删除（`deleted_at`），不新增“删除 revision”；
源历史与 current/pin 保留（可审计）。这是既有 D03 §6.4 / TASK-002 语义，本任务未改。
若未来需要“删除操作也进 revision 历史”，需独立契约决策。

---

## 非 GAP 的既有能力（已核实真实存在，未重写）

- `create_region` / `delete_region` / `save_geometry` / `merge_regions` / `split_region` /
  `reorder_regions` / `save_manual_translation` / `confirm_final` / `set_revision_pinned` /
  `restore_revision_with_number` / `set_region_type` 全部在 `src/application/editing/service.py`
  真实实现并走 `commit_region_revision` 原子 seam；本任务只是加 wire 层与乐观锁参数。
- 几何归一化/反归一化唯一映射在 `src/application/editing/region_canvas.py`（已复用，未复制）。
- SQLite 原子 seam 与 pin 单语句事务在 `src/infrastructure/sqlite/regions.py`（已复用）。
