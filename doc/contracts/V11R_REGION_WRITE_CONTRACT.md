# V11R Region 写面 + 文本读投影契约 v1.3（FROZEN）

状态：`FROZEN`（2026-10-30；v1 = V11R-F0-1 写面，v1.1 = V11R-F0-2 文本读投影，v1.2 = F0-1 I1 有界返修，v1.3 = F0-1 I2 有界返修：软删目标存活校验 / 真实交错并发验证 / Host 输入上限 / DB_FAILED 独立错误路径 / F0-2 DTO 严格存在性；Owner 产出，Lead 裁定文件归属）。
任务卡：`doc/tasks/V11R-F0-1.md`（写面，高风险）、`doc/tasks/V11R-F0-2.md`（文本读投影，关闭 GAP-2）。
上游：审计 §5.1 F-01（`New_Manga_前后端功能与接口现状审计_V1.1_修订完整版.md`）、
`doc/plan/V11R_AVALONIA_CONTRACT.md` §1.2/§5.3、`doc/design/redesign-v1/40-fusion/FUSION_SPEC.md` §4/§8 F-01。
实现：`src/bootstrap/core_service.py`（wire handler）、`src/application/editing/service.py`（use case）、
`src/domain/regions/entities.py`、`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/{HostCommandRegistry,HostCommandDispatcher,RegionTextProjection}.cs`。
命令清册编号：本文件是总契约 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 的 **C067–C077** 节（总契约由 V11R-A-3 维护，不得在本文件重复冻结 C001–C066）。

---

## 0. 范围与非目标

本契约冻结两部分：
1. 审计 §5.1 F-01 指出的 Region 写面在 IPC 上的 10 条新命令（C067–C076）；
2. V11R-F0-1 遗留 GAP-2 的 Region 文本只读投影（C077，V11R-F0-2 补齐）。

它们是既有 Region 命令族（C042 `set_region_type` / C043 `list_regions` / C044
`list_region_revisions` / C045 `restore_region_revision` / C046 `rerender_page` / C047
`resolve_page_resource`）的**追加**，C042–C047 的入参/出参/错误码**逐字节不变**。

**读命令选型（F0-2 裁定）**：任务卡允许 `get_region`（单 region）或
`list_page_region_texts`（整页）二选一，选型标准是「Studio Page 载入一页的 region 列表 + 文本应在
1 次命令内完成」。选 **`list_page_region_texts`（page-scoped）**：Page 工作区首帧必然需要该页全部
live region，单 region 命令会退化成 N+1 次往返；本命令一次返回整页投影，并支持可选
`region_ids` 严格过滤（刷新/局部重读；未知或跨页 region → TARGET_NOT_FOUND）。

非目标：
- `IHostController` / `HostController` 的 C# 便捷方法（写权归 V11R-A-1/A-2 的 core-bridge；本任务
  只提供 `HostCommandDispatcher` 可调命令与 `RegionPageTextProjection` 解析 DTO）；
- 任何 UI 视图、ViewModel、旧 `apps/desktop` 代码；
- 用户源文件/Managed Copy 内容（这些命令不接触文件系统，见 §5）。

---

## 1. 通用协议语义

### 1.1 Envelope 与 minor 策略（裁定）

请求（与既有命令完全一致）：

```json
{"protocol": "new-manga.core", "version": {"major": 2, "minor": 3},
 "request_id": "<id>", "command": "<command>", "payload": {...}}
```

应答：`{"protocol", "version": {"major": 2, "minor": 3}, "request_id", "result" | null, "error" | null}`。

**minor 策略（明确决定，非默认）**：11 条命令（C067–C077，10 写 + 1 读）全部使用**逐命令族
minor = 3**（与 `set_region_type` / `list_regions` 同族），Core 的 `PROTOCOL_MINOR` 保持 3，
**零 protocol bump**。理由：

1. Core 的版本门只对 `CreateBook/CreateChapter`（minor 8）、`PermanentlyDelete*`（minor 10）与
   P15 settings 族（minor 7）做严格 minor 门禁；Region 族按 major=2 受理任意整数 minor；
2. 既有追加族（`cleanup.*` / `backup.*` / `plugins.*` / `rerender_page` /
   `list_region_revisions` / `resolve_page_resource`）都落在 minor 3，这是本仓库已固化的
   「追加命令面不 bump」先例；
3. bump 会改变所有客户端声明的 envelope 版本，属于本任务未授权的共享契约变更。

C# 侧 `HostCommandRegistry` 中 11 条命令的 `CoreMinor` 均为 `3`；
`RegionWriteCommandNames`（10 写）、`RegionReadCommandNames`（1 读）与并集
`V11RAdditiveCommandNames`（11）显式暴露追加集合；冻结的 66 条 Rust 快照**不修改**（见 §8 验证）。

### 1.2 错误 envelope（复用既有 typed 字面量，零新增错误类型）

```json
{"code": "<SCREAMING_SNAKE_CASE>", "category": "<validation|conflict|not_found|internal>",
 "message": "<固定安全短语或校验原因>", "retryable": false}
```

| code | category | 触发 |
|---|---|---|
| `INVALID_REQUEST` | `validation` | payload 形状/几何/枚举/编号非法，或超过 v1.3 输入上限（写前 fail-closed，零持久化） |
| `INPUT_REVISION_CHANGED` | `conflict` | `expected_revision` / `expected_revisions` 过期或不可解析（零写） |
| `TARGET_NOT_FOUND` | `not_found` | region / page / revision 不存在、已被软删除，或**批量事务内发现目标已被并发软删**（I2/P1-A；零写） |
| `UNKNOWN` | `internal` | 未归类内部失败（含 **DB_FAILED**：busy/IO/事务回滚，I2/P2-D），固定短语 `Region write failed`，无原始异常文本 |

`message` 安全约束：不包含 OS 路径、用户数据原文（人工译文只在成功 result 回显）、
数据库/异常堆栈；几何拒绝只投影 `region_canvas` 的 typed reason
（`TOO_FEW_POINTS` / `TOO_MANY_POINTS` / `DEGENERATE_GEOMETRY` / `PAGE_SIZE_UNAVAILABLE`）。
**DB 故障不得映射为 conflict**（v1.3/I2）：数据库 busy/IO 失败走 `UNKNOWN`/internal 固定短语，
调用方不得按“刷新后重试写”的冲突语义处理。

### 1.3 几何写入形状（normalized points）

```json
"geometry": {"points": [[0.1, 0.1], [0.4, 0.4]]}
```

- 每点 `[x, y]` 为 **归一化 0..1 有限数**（`bool` 不是数）；≥2 点；
- 2 点为轴对齐矩形（任意角序）；≥3 点为多边形环（按给定顺序）；
- Core 用 `application/editing/region_canvas.py::normalized_to_page_geometry`
  （既有唯一映射）转换：半进位 `floor(n*size+0.5)`、坐标 clamp 到 `[0, size]`、
  零面积/重复角/共线环一律 `INVALID_REQUEST`；
- 写入按页像素整数持久化；回读投影与 C043 `list_regions` 的 normalized 形状**同构**：
  `{"bbox": [x, y, w, h], "polygon": [[x, y], ...]}`（`page_geometry_to_normalized` 唯一逆向映射）。

UI 从不提供页像素尺寸，也从不接触存储坐标。

**v1.3/I2 输入上限（P2-E，Core 与 Host 同值 fail-closed；超限 `INVALID_REQUEST`）**：

| 上限 | 值 | 适用 |
|---|---:|---|
| `MAX_REGIONS_PER_PAGE` | 500 | `create_region`（页内 live region 数）/ `reorder_regions` 列表长度 |
| `MAX_REGION_IDS_PER_BATCH` | 64 | `merge_regions` 的 `region_ids` |
| `MAX_SPLIT_PARTS` | 64 | `split_region` 的 `parts` |
| `MAX_GEOMETRY_POINTS` | 512 | 任意 `geometry.points` / 单个 part 的点数 |

常数定义在 `application/editing/region_canvas.py`；Core 在任何持久化之前拒绝，Host 在发帧前拒绝。
理由：每个复合写是一个 `BEGIN IMMEDIATE` 事务（busy timeout 5s），无界输入会长时间持锁并让其他写者 BUSY。

### 1.4 `expected_revision` 乐观锁（统一语义）

- 值 = 调用方最近一次观察到的 **current revision 编号**（`list_regions` 行的 `revision_no`、
  `list_region_revisions.current_revision_no`、或任一写命令返回的 `revision_no`）；
- 必须为正整数；缺省 = 不启用守卫（向后兼容，C042/C045 既有语义）；
- 语义与 C042/C045 完全一致：不可解析或不是 current 指针 ⇒ `INPUT_REVISION_CHANGED`，
  **零写**（不是「吞掉冲突后继续写」）；
- **事务内二次校验（v1.2 / I1）**：单 region 命令在 commit seam 事务内二次校验
  `expected_current_revision_id`；**多 region 命令（merge/split 的源、reorder）与 delete/pin
  全部走 `commit_region_batch`——在同一个 `BEGIN IMMEDIATE` 内先重读并比较每个 expected
  current 指针，再执行任何写；任一过期 ⇒ 整批回滚、零写**。不允许出现「前 N 个已写、第 N+1 个
  冲突」的部分提交。
- 多 region 命令使用 `expected_revisions: {"<region_id>": <revision_no>, ...}`：
  必须**恰好覆盖**本次受影响的 region 集合，缺项/多项 ⇒ `INVALID_REQUEST`；
- **目标存活事务内校验（v1.3 / I2/P1-A）**：批量事务在比较 expected 之前，对**每个既有目标**
  （merge/split 源、reorder 全部 region、delete 目标、pin 目标）重读 `deleted_at IS NULL`；
  任一目标已被并发软删 ⇒ 整批回滚 + `TARGET_NOT_FOUND`（零写）。软删执行**条件 UPDATE**
  （`deleted_at IS NULL` 且（若给 expected）`current_revision_id = expected`）并强制
  `rowcount == 1`；pin 更新同样要求目标 region 仍 live。两个调用者在首个提交前都通过
  `_require_region` 是正常并发场景，必须由本校验兜住，不能产生第二套 merge/split 结果。
- `create_region` 不支持也不需要守卫：创建不存在「先前 revision」，且 region_id 由服务端生成，
  冲突面为零（见 §7 GAP-4 记录）。

**幂等性总则**：所有 revision 写命令（geometry / manual / confirm / lock / merge / split /
reorder 的变更 region）都是 **append-only 非幂等**——每次成功调用产生新 revision，重试会留下
额外历史；这是既有 T027/T028 的冻结语义，本任务不引入客户端幂等键、不静默去重。
`pin_revision` 是幂等旗标写（不产生 revision）；`reorder_regions` 对相同顺序是**效果幂等**
（仅变更 region 产生 revision，重复调用零新 revision）；`delete_region` 二次调用是
`TARGET_NOT_FOUND`（安全失败，无数据变化）。

---

## 2. 逐命令契约（C067–C077）

所有命令均为 `core` 通道，C# Host 命令名与 Core wire 命令名**同名**，`minor=3`。

### C067 `create_region`

| 项 | 内容 |
|---|---|
| 入参 | `page_id`! 非空串；`geometry`! §1.3；`region_type`? 六值枚举（`speech` 默认）；`reading_order`? 正整数（缺省=页内追加） |
| 出参 | `{region_id, revision_no, reading_order, region_type, sfx_policy}`（提交后有效状态） |
| 错误 | `INVALID_REQUEST`（payload/枚举/几何）、`TARGET_NOT_FOUND`（page 不存在）、`UNKNOWN` |
| 乐观锁 | 不适用（§1.4） |
| 幂等 | 非幂等：每次调用创建新 region + 其第 1 个 revision |
| 语义 | 复用 `RegionEditingService.create_region`（TASK-002 §2.1：首 revision 与 current 指针同一次原子 commit）；SFX 策略复用 EV-8 共享规则：仅 `region_type=sfx` 携带**当前全局** `sfx.policy`，其余类型强制 `skip`；命令写永远是用户写（首 revision `origin=user`，机器检测候选仍走 pipeline 内部路径）；显式 `reading_order` 原样使用、不做唯一性重排（UI 建议省略以自动追加）；**v1.2/I1：实体行 + 首 revision + current 指针在同一个 `BEGIN IMMEDIATE` 内提交，失败整批回滚，绝无「无 current revision 的孤儿 region」**；**v1.3/I2：页内 live region ≥ `MAX_REGIONS_PER_PAGE`(500) ⇒ `INVALID_REQUEST`** |

### C068 `delete_region`

| 项 | 内容 |
|---|---|
| 入参 | `region_id`!；`expected_revision`? |
| 出参 | `{region_id, deleted: true}` |
| 错误 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`、`UNKNOWN` |
| 乐观锁 | 支持；过期 ⇒ conflict 零写 |
| 幂等 | 软删除本身**不新增 revision**；二次调用 `TARGET_NOT_FOUND`，历史/current/pinned 不变 |
| 语义 | 仅写 `deleted_at`（既有 `delete_region`）；`list_regions` 不再返回该 region，但 `region_revisions` 与 current 指针对历史审计仍可寻址；不删除用户数据；**v1.2/I1：current 指针比较与 `deleted_at` 写入在同一个 `BEGIN IMMEDIATE` 内完成（过期即整批零写）**；**v1.3/I2：目标已被并发软删 ⇒ 事务内整批回滚 + `TARGET_NOT_FOUND`（零写），绝不重写 `deleted_at`** |

### C069 `save_region_geometry`

| 项 | 内容 |
|---|---|
| 入参 | `region_id`!；`geometry`! §1.3；`expected_revision`? |
| 出参 | `{region_id, revision_no, geometry}`（`geometry` 为 normalized 回读形状） |
| 错误 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`、`UNKNOWN` |
| 乐观锁 | 支持；解析为 current revision id 后进 seam 事务内二次校验 |
| 幂等 | 非幂等（append-only：即使几何相同也产生新 revision） |
| 语义 | 复用 `save_geometry`（D06 §87 geometry save 产生 user revision）；仅改几何，文字/样式/锁/排序保持 |

### C070 `merge_regions`

| 项 | 内容 |
|---|---|
| 入参 | `page_id`!；`region_ids`! ≥2 个互异非空 id（必须同页且 live）；`expected_revisions`? 恰好覆盖这些 id |
| 出参 | `{region_id, revision_no, reading_order, region_type, sfx_policy, deleted_region_ids: [...]}` |
| 错误 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`（源 region 不存在/已删）、`UNKNOWN` |
| 乐观锁 | 支持（映射）；**全部条目在任何写之前校验**，任一过期 => 零写 |
| 幂等 | 非幂等；成功后重试 ⇒ 源已被软删，`TARGET_NOT_FOUND` |
| 语义 | 复用 `merge_regions`（D03 §6.4）：覆盖 bbox + 多边形拼接、OCR/机翻以空格拼接、任一源的人工保护继承（`manual_edited`+`translation_locked`，重新确认由 merge 后 region 自己承担）、新 region 从 revision 1 开始、源软删除且历史保留；**v1.2/I1：新 region 行+首 revision+全部源软删同一事务；源 current revision 在事务内重核对（任一过期整批零写）；继承「有效锁」——源 region 级或文本级锁任一为真即视为锁定，并一致写入新 region 的两个投影（P1-3）**；**v1.3/I2：事务内重读全部源 `deleted_at IS NULL`（并发软删 ⇒ `TARGET_NOT_FOUND` 整批零写）**；`region_ids` ≤ `MAX_REGION_IDS_PER_BATCH`(64) |

### C071 `split_region`

| 项 | 内容 |
|---|---|
| 入参 | `region_id`!；`parts`! ≥2 个几何点列表（每个 ≥2 点，§1.3）；`expected_revision`? |
| 出参 | `{source_region_id, source_deleted: true, regions: [{region_id, revision_no, reading_order, region_type}]}` |
| 错误 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`、`UNKNOWN` |
| 乐观锁 | 支持；写入第一个 part 前校验 |
| 幂等 | 非幂等；成功后重试 ⇒ `TARGET_NOT_FOUND` |
| 语义 | 复用 `split_region`（D03 §6.4）：交互切割由编辑器给几何；每 part 新历史 revision 1、阅读序按 part 顺序；源软删除；人工保护继承；**v1.2/I1：全部 part 行+首 revision+源软删同一事务（中途失败不得留下 live 源 + 半套 part）；源 current revision 事务内重核对；每 part 继承源「有效锁」并写入两个投影（P1-3）**；**v1.3/I2：源在事务内被并发软删 ⇒ `TARGET_NOT_FOUND` 整批零写**；`parts` ≤ `MAX_SPLIT_PARTS`(64)，单 part 点数 ≤ `MAX_GEOMETRY_POINTS`(512) |

### C072 `reorder_regions`

| 项 | 内容 |
|---|---|
| 入参 | `page_id`!；`ordered_region_ids`! 该页 live region id 的**精确全排列**（缺项/多项/重复 ⇒ INVALID_REQUEST）；`expected_revisions`? 恰好覆盖全部 id |
| 出参 | `{page_id, regions: [{region_id, revision_no, reading_order}]}`（按请求顺序；`revision_no` 为调用后 current） |
| 错误 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`（page 未知）、`UNKNOWN` |
| 乐观锁 | 支持（映射）；先整体校验，再逐 region 入 seam 二次校验 |
| 幂等 | **效果幂等**：位置未变的 region 不产生 revision；相同顺序重复调用零新 revision |
| 语义 | 复用 `reorder_regions`（TASK-028 §3.4：reading_order 是 revision-owned state）；拒绝部分列表，避免制造重复/空洞阅读序；**v1.2/I1：整批排列变更 + 各自新 revision 在同一个 `BEGIN IMMEDIATE` 内提交，事务内重核对所有 expected current 指针（含未变更 region 的检查），任一冲突整批回滚、零写（P1-2）**；**v1.3/I2：事务内对列表内每个 region 重读 `deleted_at IS NULL`（并发软删 ⇒ `TARGET_NOT_FOUND` 整批零写）**；列表长度 ≤ `MAX_REGIONS_PER_PAGE`(500) |

### C073 `save_manual_translation`

| 项 | 内容 |
|---|---|
| 入参 | `region_id`!；`edited_translation`! string（允许空串=清空人工稿）；`expected_revision`? |
| 出参 | `{region_id, revision_no, review_state, text: {ocr_text, machine_translation, edited_translation, final_translation, final_source, edited_confirmed, manual_edited, translation_locked}}` |
| 错误 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`、`UNKNOWN` |
| 乐观锁 | 支持（seam 内二次校验） |
| 幂等 | 非幂等（append-only） |
| 语义 | 复用 `save_manual_translation`（D03 §8.4）：设置人工译文、`manual_edited=true`、`translation_locked=true`，review_state=`needs_review`；**未显式确认前不成为 final**（§8.3）；不覆盖机翻字段、不改几何/类型 |

### C074 `confirm_region_final`

| 项 | 内容 |
|---|---|
| 入参 | `region_id`!；`expected_revision`? |
| 出参 | 同 C073 外形（`review_state="confirmed"`） |
| 错误 | 同 C073 |
| 乐观锁 | 支持 |
| 幂等 | 非幂等（append-only；重复确认各产生一个 confirmed revision） |
| 语义 | 复用 `confirm_final`（D06 §87）：非空人工译文 → 成为 confirmed final（`final_source=edited`）；空人工译文 → 仅锁定 review_state，final 仍按 §8.3 解析（机翻或空），不篡改文字 |

### C075 `set_region_lock`

| 项 | 内容 |
|---|---|
| 入参 | `region_id`!；`region_locked`? / `translation_locked`? / `inpaint_locked`?（三者至少一个，值为 bool）；`expected_revision`? |
| 出参 | `{region_id, revision_no, review_state, region_locked, translation_locked, inpaint_locked}` |
| 错误 | `INVALID_REQUEST`（无任何锁字段 / 非 bool）、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`、`UNKNOWN` |
| 乐观锁 | 支持 |
| 幂等 | 非幂等（显式用户锁操作按 D06 §87 视为一次保存，每次产生新 revision，即使值未变） |
| 语义 | **V11R-F0-1 新增 use case**（application 层原缺失，见 §6）：`set_locks()` 组合既有域方法（`Region.set_region_locked` / `set_inpaint_locked`、`RegionText.lock_translation` / `unlock_translation`）并走同一原子 commit seam；revision snapshot 携带三锁；`translation_locked` 同时镜像到 `Region.set_translation_locked`（top-level 投影），保证 pipeline 的 LockSnapshot（读 `regions.translation_locked` 列）与文本级人工保护旗标一致；不改文字/几何/类型 |

### C076 `pin_revision`

| 项 | 内容 |
|---|---|
| 入参 | `region_id`!；`revision_no`! 正整数；`pinned`! bool；`expected_revision`? |
| 出参 | `{region_id, revision_no, is_pinned, current_revision_no}` |
| 错误 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`（expected 过期）、`TARGET_NOT_FOUND`（region 或 revision 不存在）、`UNKNOWN` |
| 乐观锁 | 支持（仅守卫 current 指针仍是调用方观察到的 revision；pin 本身不依赖 current） |
| 幂等 | **幂等**：重复写同一 flag 无新状态、无新 revision |
| 语义 | 复用 `set_revision_pinned`（AC-REV-003）：专用单语句事务只翻 `is_pinned`，**从不 upsert 不可变历史**、不移动 current 指针、不产生 revision；pin 保护 revision 免于 cleanup/清理（见 M2-C1 §5）；**v1.2/I1：current 指针比较与 is_pinned 更新在同一个 `BEGIN IMMEDIATE` 内完成（目标 revision 存在性为 append-only 历史的无竞态前置校验），过期即零写（P2-4）**；**v1.3/I2：pin 目标 region 必须仍 live（事务内重读 + UPDATE 的 live 条件），并发软删 ⇒ `TARGET_NOT_FOUND` 零写** |

### C077 `list_page_region_texts`（V11R-F0-2，读命令，关闭 GAP-2）

| 项 | 内容 |
|---|---|
| 入参 | `page_id`! 非空串；`region_ids`? 非空、互异的非空 id 数组（严格过滤；省略=整页） |
| 出参 | `{page_id, page_size: {width, height} \| null, regions: RegionTextDetail[]}`，reading_order 升序 |
| RegionTextDetail | `{region_id, page_id, region_type, sfx_policy, reading_order, geometry: {bbox, polygon} \| null, text: {ocr_text, machine_translation, edited_translation, final_translation, final_source, edited_confirmed, manual_edited, translation_locked}, locks: {region_locked, translation_locked, inpaint_locked}, review_state, origin, revision_no, current_revision_id, is_pinned, pinned_revision_nos: int[], created_at, updated_at}` |
| 错误 | `INVALID_REQUEST`（payload/`region_ids` 形状）、`TARGET_NOT_FOUND`（过滤 id 不存在、已软删或属于其它页）、`UNKNOWN` |
| 乐观锁 | 不适用（只读） |
| 幂等 | 只读，天然幂等 |
| 语义 | 纯读投影，**一条命令完成 Studio Page 首帧的「整页 region + 四轨文本」载入**（避免 N+1；这是选型依据）。`text` 是快照契约的四级文本原值（未编辑 region 的 `final_source="none"`、空串就是真实值，不得补占位）；`review_state`/`origin`/`revision_no`/`current_revision_id`/`is_pinned` 取自 current 指针指向的 revision；`pinned_revision_nos` 列出历史中所有 pinned 号；`geometry` 是 normalized 回读形状（与 C043 同构），页行拿不到像素范围时为 `null`（不伪造）；`page_size` 在未知页为 `null`。未知 page / 无 region 页均返回 `regions: []`（C043 先例：空数据不是错误）。`locks.translation_locked`（Region 列投影）与 `text.translation_locked`（人工保护旗标）分别原值投影，双投影含义见 §6 GAP-3。 |

---

## 3. 数据安全不变量（独立审查重点）

1. **current/pinned 不被破坏**：所有 revision 写走既有 `commit_region_revision` 原子 seam
   （`BEGIN IMMEDIATE` 内重读 current、比较 id、插 revision、同步 revision-owned state、更新指针，
   失败整体回滚）；`pin_revision` 只翻 `is_pinned`；`delete_region` 只写 `deleted_at`。
2. **复合写全有或全无（v1.2/I1）**：create / merge / split / reorder / delete / pin 走
   `commit_region_batch`——实体行、首 revision、current 指针、源软删、pin 旗标与全部 expected
   current 重核对都在**同一个 `BEGIN IMMEDIATE`** 内；任一步失败整批回滚，因此不存在
   「无 current revision 的 region」「merged 行与 live 源共存」「live 源 + 半套 part」
   「部分重排」「delete/pin 跨过已变化的 current」。事务内重核对是防 TOCTOU 的唯一权威点，
   调用前预检查只是快速失败。
3. **锁继承（v1.2/I1）**：merge/split 继承「有效锁」（源 region 级或文本级任一为真），并**一致写入
   region 列与 text_json 两个投影**；显式 `set_region_lock` 的锁定语义因此不会因合并/拆分丢失，
   机器翻译步骤继续走既有锁/candidate 通道而不会覆盖受保护文本。既有 `save_manual_translation`
   只写文本级旗标的行为**未改**（GAP-3 双投影说明保留，单独契约决策）。
4. **目标存活（v1.3/I2/P1-A）**：批量事务在比较 expected 前，对每个既有目标重读
   `deleted_at IS NULL`；软删是条件 UPDATE 且 `rowcount` 必须为 1；pin UPDATE 带 live 条件。
   任一目标已被并发软删 ⇒ 整批回滚 + `TARGET_NOT_FOUND`（零写）。这堵住「两个调用者都在首个
   提交前通过预检」时重复 merge/split 生成第二套结果集的窗口，也禁止 delete/pin 写已删目标。
5. **DB 故障不是冲突（v1.3/I2/P2-D）**：`RegionCommitStatus.DB_FAILED` 映射到独立的
   `GuardStatus.DB_FAILED`，wire 走 `UNKNOWN`/internal 固定短语；绝不伪装成
   `INPUT_REVISION_CHANGED`（否则 UI 会刷新后重试写）。
6. **输入有界（v1.3/I2/P2-E）**：`MAX_REGIONS_PER_PAGE` / `MAX_REGION_IDS_PER_BATCH` /
   `MAX_SPLIT_PARTS` / `MAX_GEOMETRY_POINTS` 在 Core 与 Host 两侧同值 fail-closed；
   超限 ⇒ `INVALID_REQUEST` 且零写，避免单个写事务长时间持有 SQLite 写锁。
7. **不可变历史**：本任务不 upsert/不删除任何 `region_revisions` 行；restore 语义不变（新建
   RESTORED revision 而非回移指针）。
8. **人工保护**：manual save/lock 的 `translation_locked` 会让机器写走既有 candidate 通道
   （`apply_machine_translation` 的 LOCK_CHANGED / §8.4），写命令不解除保护。
9. **源文件**：10 条写命令与 1 条读命令的 payload/result 均不含 OS 路径、文件名、base64 图像或
   managed path；不读不写用户源文件与 Managed Copy 内容（几何是 DB 内坐标，不是文件）。
10. **自动/机器写与用户写分离**：本任务全部是用户写（origin=USER），不修改 pipeline 的
    machine-write guard、candidate 持久化与锁比较语义。
11. **失败面**：任何校验失败在持久化之前返回（写前 fail-closed）；conflict/not_found 零写；
    内部失败仅固定短语，详情只进 stderr。Host 侧 v1.2/I1 起同时拒绝领域非法值
    （归一化坐标越界、非正整数 revision/reading_order），v1.3/I2 起同时拒绝超限批量输入。

### 3.1 安全边界（page / book 作用域，v1.2）

- **单 region 命令按裸 `region_id` 定位**（读命令 `list_region_revisions`/`rerender` 系同理）：
  Host 与 Core 不额外要求调用方声明 page/book；命令语义是「按 id 操作该 id 指向的对象」。
- **项目当前没有定义按书（book）授权模型**：本任务**不新增**临时 ACL、不做假权限校验，
  GAP 面保持诚实（这是产品/平台层未来的授权职责，不是 Region 写面的隐藏实现）。
- **跨书 id 的授权由 Host 未来 ACL 承担**：一旦产品定义按书访问控制，应在 Host 命令入口按
  `region_id → page → chapter → book` 解析归属并拒绝越权（Core 侧保持「按 id 定位」的原子语义）。
- **当前 UI 约束**：Studio 只传自己**已经加载**的 page/region id；不得凭列表外的 id 猜测/试探。
  `list_page_region_texts` 的 `region_ids` 过滤会拒绝未知或跨页 id（`TARGET_NOT_FOUND`），
  但这是命令面一致性校验，**不是**授权机制。
- `merge_regions`/`reorder_regions` 要求全部输入 region 属于同一 `page_id`（跨页 ⇒ `INVALID_REQUEST`），
  这是数据一致性约束，同样不承担授权语义。

---

## 4. C# Host/CoreClient 侧契约

- `HostCommandRegistry`：`RegionNames` 追加 11 名（10 写 + 1 读）；`CoreBindings` 映射同名 Core
  命令、`Minor=3`；`RegionWriteCommandNames`（10）、`RegionReadCommandNames`（1）与并集
  `V11RAdditiveCommandNames`（11）显式暴露追加集合；`All` = 冻结 66 条迁移命令 + 11 条追加命令。
- `HostCommandDispatcher.WriteCorePayload`：逐命令做 legacy 边界的 fail-closed 参数校验
  （`INVALID_ARGUMENTS`，发帧前拒绝），并写出 §2 的精确 payload：
  - 几何：`geometry.points` ≥2 个 `[x,y]` 有限数对，**且必须在归一化 `[0,1]` 内**（v1.2/I1）；split `parts` 为 ≥2 个点列表；
  - v1.3/I2 上限：geometry 点数 ≤512、`split_region.parts` ≤64、`merge_regions.region_ids` ≤64、
    `reorder_regions.ordered_region_ids` ≤500（与 §1.3 Core 常数同值）；超限发帧前 `INVALID_ARGUMENTS`；
  - `expected_revisions`：对象，key 非空、value **正整数**；`set_region_lock` 至少一个锁字段；
  - v1.2/I1：`expected_revision` / `reading_order` 必须为正整数（present ⇒ >0），`revision_no`
    必须为正整数；领域非法值在发帧前以 `INVALID_ARGUMENTS` 拒绝；
  - `edited_translation` 允许空串（文本写入专用 `RequireText`）；
  - `list_page_region_texts.region_ids`：可选，非空、互异非空字符串；省略/null 即整页。
- V11R-F0-2 新增读取 DTO（`NewManga.CoreClient.Commands`）：
  `RegionPageTextProjection.Parse(JsonElement)` → `{PageId, PageWidth, PageHeight, Regions}`，
  其中 `RegionTextDetail` 含 `RegionFourTrackText` / `RegionLockProjection` /
  `RegionGeometryProjection?`（null 保留未知页的几何缺失，不伪造），严格解析、缺字段即
  `FormatException`；**v1.3/I2（F0-2 修复项 P2-C）：必需字段先要求属性存在，再看值是否允许 null —
  `geometry` / `page_size` 缺失属性 ⇒ `FormatException`；显式 null 仍合法（未知页/无 extent）**；
  UI 通过 `HostRuntime.Commands.InvokeAsync(name, args)` 获取
  `HostCommandResult.Value` 后传入 `Parse`（`IHostController` 便捷方法归属 core-bridge 的
  V11R-A-1/A-2 任务，不在本契约内）。
- 冻结 66 条命令的既有路由/minor 不变；快照文件
  `verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json` **未编辑**。

---

## 5. 复用与实现映射（AC1 证据）

| 命令 | 复用实现（不重写） | 本任务改动 |
|---|---|---|
| C067 | `RegionEditingService.create_region` | 无 |
| C068 | `delete_region` | +`expected_revision_no` 守卫 |
| C069 | `save_geometry` | +`expected_revision_no` 参数（解析后进 seam） |
| C070 | `merge_regions` | +`expected_revisions` 全量前置校验 |
| C071 | `split_region` | +`expected_revision_no` 前置校验 |
| C072 | `reorder_regions` | +`expected_revisions` 前置校验 + per-region seam 二次校验 |
| C073 | `save_manual_translation` | +`expected_revision_no` |
| C074 | `confirm_final` | +`expected_revision_no` |
| C075 | **新增** `set_locks()`（组合既有域方法） | +`Region.set_translation_locked`、`RegionText.lock_translation`（对称域方法） |
| C076 | `set_revision_pinned` | +`expected_revision_no`；`LookupError` → typed `RegionRevisionNotFound`；v1.2/I1：事务化 guard |
| C077 | **新增** `RegionEditingService.list_region_details()`（只读组合：`list_regions` + `list_revisions` + `region_canvas` 逆向映射 + 共享 `region_text_state()`） | V11R-F0-2；不新增写路径、不补占位值 |

**v1.2/I1 复合写 seam**：C067/C068/C070/C071/C072/C076 的「实体行 + 首 revision + current 指针 +
源软删 + pin 旗标 + 全部 expected 重核对」统一走新增的
`RegionRevisionCommitter.commit_region_batch(...)`（SQLite 实现在
`src/infrastructure/sqlite/regions.py`，单 `BEGIN IMMEDIATE`）；没有第二条写路径。

新增的读辅助：`RegionEditingService.current_revision(region_id)`（写后有效状态回读）、
`region_text_state(region)`（四级文本单一投影定义，写/读共用）、
`list_region_details(page_id, page_size=...)`（C077 的页码级真实投影）、
`effective_region_locks(regions)`（merge/split 有效锁继承）。
**v1.3/I2 的 seam 状态**：`commit_region_batch` 新增 `RegionCommitStatus.TARGET_NOT_FOUND`
（既有目标被并发软删）；soft delete 改为条件 UPDATE + rowcount 校验；pin UPDATE 带 live 条件。
`GuardStatus` 新增 `DB_FAILED`（与 conflict 分离）。
全部新增写参数均为 keyword-only 且默认 `None`，既有调用点零行为变化。

---

## 6. GAP 清单（能力核实结论；不假装已实现）

| ID | 类别 | 事实 | 处置 |
|---|---|---|---|
| GAP-1 | **已填**（application 层缺失） | `set_region_lock` 无 use case：域有 `Region.set_region_locked` / `set_inpaint_locked` / `RegionText.unlock_translation`，但没有把锁变更持久化为 revision 的应用层入口（此前唯一锁写是 manual save 的隐式上锁） | 本任务新增薄 `set_locks()`（组合既有域方法 + 同一 commit seam，锁变更产生 revision，D06 §87）+ 两个对称域方法；**明确标注为 V11R-F0-1 新增**，非既有能力 |
| GAP-2 | **CLOSED（V11R-F0-2）** | Region **文本只读**投影曾缺失：`list_regions` 是 5 字段最小 DTO，IPC 上没有命令返回四级文本；C044 只返回 revision 摘要 | 新增 C077 `list_page_region_texts`（page-scoped，1 次命令完成首帧载入；含四轨文本/锁/review_state/is_pinned/pinned 历史/几何，全部真实投影）。实现见 `service.list_region_details` + `core_service.handle_list_page_region_texts`；测试 `tests/core/test_region_text_read_command.py`（11 用例）；证据 `verification/V11R-F0-2/`。**GAP-2 关闭**；UI 不再需要伪造文本 |
| GAP-3 | **记录**（既有设计双投影） | `Region.translation_locked`（列，pipeline LockSnapshot 读它）与 `RegionText.translation_locked`（text_json，人工保护判定读它）是既有双表示；既有 `save_manual_translation` 只写 text 级 | 显式 `set_region_lock` 同时同步两者；C077 把两份原值分别投影（`locks.translation_locked` / `text.translation_locked`）；**v1.2/I1：merge/split 继承有效锁并一致写入两个投影（P1-3 已修）**。**未改**既有 manual save 行为（保持既有语义，bug 修复需独立契约决策），作为已知风险保留 |
| GAP-4 | **决策记录** | `create_region` 无 `expected_revision` | 创建无先前 revision，无冲突面；§1.4 已冻结说明，不是遗漏 |
| GAP-5 | **边界** | `IHostController`/`HostController` 未追加 Region 写便捷方法 | 写权属 core-bridge（契约 §1.2）；本任务只保证命令真实可调（`HostRuntime.Commands`），UI 任务按 V11R_AVALONIA_CONTRACT 消费 |
| GAP-6 | **记录** | merge/split 对源 region 只软删，不产生“删除 revision” | 既有 D03 §6.4/TASK-002 语义，源历史与 current/pin 保留；未改 |

契约差异：任务卡 AC7 原文为「契约文档更新（与 V11R-A-3 命令契约合并）」；Lead 裁定
A-3 的 `V11R_COMMAND_CONTRACT_V1.md` 由 core-bridge 独占，本文件作为其 **C067–C077** 引用节，
不重复冻结 C001–C066。此为经批准的偏差。

---

## 7. Studio Page 消费指引（实施建议，不构成 UI 设计冻结）

1. 打开页（首帧，**1 次命令**）：`list_page_region_texts {page_id}` 一次拿到整页 region +
   四轨文本 + 三锁 + review_state + is_pinned/pinned 历史 + normalized 几何；无需再逐个 region 读
   （如果只需要最小 5 字段列表，C043 `list_regions` 仍可用）。局部刷新/选中重读可带
   `region_ids` 严格过滤。
2. 画布新建框选 → `create_region`（points 为归一化点列）；读回 `region_id/revision_no`。
3. 拖拽/缩放结束 → `save_region_geometry`，带上次 `revision_no` 作 `expected_revision`；
   `INPUT_REVISION_CHANGED` 时**不要重试写**，重新 `list_page_region_texts` 让用户确认后重做。
4. 合并/拆分/排序 → 对应命令带 `expected_revisions`/`expected_revision`；排序必须发全量全排列。
5. 文本：编辑后 `save_manual_translation`（带 expected）→ 用户 `Enter` 确认 → `confirm_region_final`。
6. 锁页签 → `set_region_lock`（只发变化的锁字段）；历史页签 → `pin_revision`。
7. 删除 → `delete_region`（带 expected）；UI 需二次确认（命令本身不做确认门，契约语义为显式用户动作）。
8. 任何 error：按 `code` 分类呈现（validation/conflict/not_found/internal），不要静默吞 conflict。
9. 解析：C# 侧用 `RegionPageTextProjection.Parse(result.Value)`；缺字段严格失败而不是静默空值，
   `Geometry=null`/`PageWidth=null` 只出现在页行不可用的真实情形（**v1.3/I2：缺属性 ≠ 显式 null，
   缺属性即解析失败**）。
10. 批量输入上限（§1.3）：UI 在生成请求前限制 part/region/vertex 数量；超限命令返回
    `INVALID_REQUEST`（validation），不要按 conflict 处理。
11. DB 忙碌/IO 故障（v1.3/I2）返回 `UNKNOWN`/internal 固定短语；UI 显示“操作失败，可重试”，
    不要走“刷新后重做”的冲突流程。

---

## 8. 验证出口（证据见 `verification/V11R-F0-1/`、`verification/V11R-F0-2/`、`verification/V11R-F0-1-I1/`、`verification/V11R-F0-1-I2/`）

| Gate | 命令 | 通过标准 |
|---|---|---|
| Python 全量 | `python -m pytest -q`（仓库根） | exit 0，无新增失败；新增用例见 `tests/core/test_region_write_commands.py`、`tests/core/test_region_text_read_command.py`、`tests/editing/test_region_write_guards.py`、`tests/core/test_region_atomicity.py`、`tests/core/test_region_batch_locking.py`、`tests/core/test_region_transactional_guards.py`、`tests/core/test_region_lock_inheritance.py`、`tests/core/test_region_target_liveness.py`、`tests/core/test_region_concurrency.py`、`tests/core/test_region_db_failure.py`、`tests/core/test_region_limits.py` |
| Core 契约用例 | `python -m pytest -q tests/core/test_region_*.py tests/editing/test_region_*.py` | 全绿（每命令成功/冲突/非法参数 + 重启后锁持久化 + 文本读投影 + 原子回滚/并发冲突零写/锁继承/事务化 delete-pin + 软删目标存活 + 真实交错并发 + DB_FAILED + 输入上限） |
| C# 构建 | `dotnet build NewManga.sln -warnaserror`（`apps/desktop-avalonia`） | 0 warning / 0 error |
| C# 测试 | `dotnet test NewManga.sln --no-build` | 全绿（`RegionWriteCommandTests`：11 条注册/minor/精确 payload/边界拒绝/DTO 严格解析 + v1.2/I1 领域非法值边界 + v1.3/I2 缺失必需字段/超限批量用例） |
| 快照不变量 | 同 C# 测试 | 冻结 66 快照 ⊆ registry；追加集恰为 `V11RAdditiveCommandNames`（10 写 + 1 读） |

**v1.2/I1 返修验证要求（已满足，证据见 `verification/V11R-F0-1-I1/README.md`）**：
失败注入必须证明「无 current revision 的 region 行不存在」；并发/过期必须证明「整批零写」；
显式 `set_region_lock(translation_locked=true)` 后 merge/split 必须仍锁定（双投影）且机器翻译
不覆盖文本；delete/pin 的 guard 与写入必须同事务。

**v1.3/I2 返修验证要求（已满足，证据见 `verification/V11R-F0-1-I2/README.md`）**：
已软删目标再 merge/split/delete/pin ⇒ `TARGET_NOT_FOUND` 且零写；并发测试必须使用**独立 SQLite
连接 + 同步 barrier** 在预检与提交之间真实交错（current 推进 / 软删 / 两个 region 同时过期），
并断言 revision/顺序/软删/pin 全部零写；DB 故障必须是 UNKNOWN/internal 固定短语（非 conflict）；
超限输入必须 `INVALID_REQUEST` 且零写。

---

## 9. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-10-30 | v1 冻结：10 条命令契约、minor 3 策略、几何/乐观锁/幂等/错误码/数据安全、C# 注册与 payload、GAP 清单（V11R-F0-1 Owner） |
| 2026-10-30 | v1.1（V11R-F0-2）：新增 C077 `list_page_region_texts`（page-scoped 文本读投影，关闭 GAP-2）、`RegionPageTextProjection` 解析 DTO、`RegionReadCommandNames`/`V11RAdditiveCommandNames`；GAP-2 标 CLOSED，GAP-3 “既有 manual save 未改”显式保留；契约升版原因见 §0 读命令选型。 |
| 2026-10-30 | v1.2（V11R-F0-1 I1 有界返修，独立审查 r1 FAIL 处置）：P1-1 复合写全有或全无（`commit_region_batch` 单事务）；P1-2 多 region 乐观锁事务内整批重核对、整批零写；P1-3 merge/split 继承有效锁并写双投影；P2-4 delete/pin guard 与写入同事务；P2-5 Host 发帧前拒绝坐标越界/非正整数等领域非法值。逐项处置表见 `verification/V11R-F0-1-I1/README.md`。 |
| 2026-10-30 | v1.3（V11R-F0-1 I2 有界返修，独立审查 r2 FAIL 处置）：P1-A 批量事务重读目标 `deleted_at IS NULL`、条件软删 rowcount=1、pin 带 live 条件，已删目标 ⇒ `TARGET_NOT_FOUND` 零写；P1-B 独立 SQLite 连接 + barrier 的真实交错并发测试；P2-C（**F0-2 修复项**）DTO 缺属性严格失败、显式 null 仍合法；P2-D `GuardStatus.DB_FAILED` 独立，wire UNKNOWN/internal 固定短语；P2-E 输入上限（500 region / 64 merge / 64 part / 512 vertex，Core 与 Host 同值 `INVALID_REQUEST`）。逐项处置表见 `verification/V11R-F0-1-I2/README.md`。 |
