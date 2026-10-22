# 设置分区 Schema — 批次 C（回收站 / 备份恢复 / Plugin-Hooks）

- 状态：**设计冻结提案（待用户裁决）**；裁决前不得实现、不得在设置页开放任何写控件。
- 依据：[SETTINGS_SECTION_SCHEMAS.md](SETTINGS_SECTION_SCHEMAS.md) §5、[P15_SETTINGS_IPC_CONTRACT.md](../contracts/P15_SETTINGS_IPC_CONTRACT.md) §7–§8、D04 §43（回收站）、D03 §34.3 / D07 §48（备份）、[extensions.md](../contracts/extensions.md) §1.3（Plugin/Hooks，U-3 已批准范围）。
- 本轮范围：**只产出设计与决策清单**（Task `SETTINGS-OPEN-C-1-DESIGN`）；实现拆成 C-1/C-2/C-3 三个后续 Task，用户裁决并释放后才写产品代码。

## 0. 批次边界与分期

| 分期 | 分区 | 本轮性质 | 是否有新增 wire | 是否有写控件 |
|---|---|---|---|---|
| C-1 回收站 | `recycle_bin` | 操作面（查看 + 清空） | **无**（复用既有 `library_list_recycle_bin_books` / `library_delete_books_permanently`） | 无（仅危险操作按钮） |
| C-2 备份/恢复 | `backup` | 操作面（创建/列出/恢复/删除） | **有**（4 条应用层命令 + Tauri 文件选择） | 无（无 `auto_backup` 开关） |
| C-3 Plugin C1 | `plugins` | 只读说明 + 管理面（冻结，不实现） | 有（冻结在 C-3 实现前） | 无（`plugins.enabled` 默认关，实现前 UI 只读） |

**硬约束**：三节的 `settings_get` / `settings_update_section` 写路径**均不开放**（P15 白名单不变）。理由：这三节的"设置键"没有真实消费点（无调度、无执行器），开放写控件就是重演 `typeset.fill_color` 假控件事故（批次 A review B2 已定案）。操作面只提供**真实动作**，动作的效果由既有/新增 Core 服务保证。

## 1. 通用纪律（三节共享）

1. 危险操作（永久删除、恢复覆盖）必须 **二次确认**；确认语义由 Core 校验，UI 不得省略。
2. 所有 IPC 不投影 OS 绝对路径（沿 B-2 cleanup 的 `_no_absolute_paths` 纪律）；备份/恢复日志只记相对名或备份 id。
3. 所有失败走既有 `CORE_ERROR` 封闭错误码 + 既有 `error_envelope`；不新增通用错误码，除非本节明确列出。
4. 未知/非法 payload → `INVALID_REQUEST`（validation，non-retryable）。
5. 前端 React 不拼路径、不读文件；路径只作为 Tauri 命令参数传入（既有导出/导入先例）。
6. 任一操作失败不得让 Core 崩溃/留下半状态；失败可重试且幂等（同 B-2 cleanup 口径）。

---

## 2. 回收站（section `recycle_bin`，C-1）

### 2.1 定位

回收站是**操作面**，不是设置表单：

- `settings_get` 不返回该 section 的键（无冻结键集）；`settings_update_section` 对 `recycle_bin` 返回既有 `UNKNOWN_SECTION`/`INVALID_SECTION`（与"未开放"一致）。
- `auto_cleanup_days`（D04 §43.4）**本期不开放**：回收站自动清理需要启动/定时调度消费点，当前 Core 无调度器；写了也不会生效，属假控件。写入本节时在 Task/Handoff 记录"无调度消费点，未开放"。

### 2.2 查看（复用既有 wire）

| 项 | 设计 |
|---|---|
| Core 命令 | `library_list_recycle_bin_books`（**已存在**，Tauri production 命令） |
| payload | 无（空对象） |
| result | `BookSummary[]`（`book_id/title/original_title/is_favorite/is_archived/page_count/created_at/updated_at`）——**不新增 `deleted_at`**（现有投影无此字段，不扩 wire） |
| 空态 | 空数组 = "回收站为空"，不是错误；UI 显示"回收站为空" |
| 失败 | 沿用既有 `CORE_ERROR` 投影 |

### 2.3 清空（复用既有 wire，分批 + 整库保护）

| 项 | 设计 |
|---|---|
| Core 命令 | `library_delete_books_permanently`（**已存在**，Tauri production 命令） |
| payload | `{book_ids, confirmed_book_ids, confirm_count, confirm_permanent_delete}`；`confirmed_book_ids` 必须与 `book_ids` **全等**，`confirm_count == len(book_ids)`，`confirm_permanent_delete === true`（无省略） |
| 分批 | 单次 ≤ **20** 本（Core 硬限，`BOOK_DELETE_BATCH_LIMIT_EXCEEDED`）；UI 按批循环，**每批独立确认语义**（逐批 payload 自洽），不做"跨批一次性确认"的 Override |
| 整库保护 | 若回收站包含全部书籍，Core 返回 `BOOK_DELETE_BATCH_WHOLE_LIBRARY`（conflict）；UI 必须**原样提示"不能删除整个书库"**，不得绕过（这是既有安全边界，不因设置页入口而放宽） |
| 回滚 | 永久删除不可恢复（由 Core 语义决定）；UI 二次确认弹窗必须写明"永久删除，不可恢复"与数量 |
| 幂等 | 删除后再次提交同一批 → 书籍已不存在，Core 返回既有 not-found/幂等语义（按既有实现）；UI 重新拉列表 |

### 2.4 UI 行为（`CacheRevision` 同级分类）

1. 进入分区自动调用 `library_list_recycle_bin_books`（挂载时一次 + 手动刷新按钮）。
2. 展示：数量、书籍标题列表（可滚动）、每行 `title` + 可选 `page_count`；不展示绝对路径。
3. 操作：`清空回收站` 按钮；点击后二次确认弹窗：`将永久删除 N 本书（不可恢复）`，确认后按 2.3 分批执行。
4. 执行中禁用按钮；失败显示错误码映射后的中文文案（`BOOK_DELETE_BATCH_WHOLE_LIBRARY` → "不能删除整个书库"；`BOOK_DELETE_BATCH_PREFLIGHT_FAILED` → "有任务/导出正在进行，稍后重试" 等）。
5. 成功后重新拉列表（应为空），显示"已清空"。
6. 只读说明（面板底部）："回收站自动清理策略未开放（当前没有调度器）；此处只提供手动清空。"

### 2.5 AC（C-1 实现时）

- AC1 查看：真实列表与数量来自 Core，不 mock；空态/错误态可区分。
- AC2 清空：≤20 分批、确认语义严格（篡改 `confirm_count` 被 Core 拒绝）、整库保护原样提示。
- AC3 无写 section：`settings_update_section` 对 `recycle_bin` 仍拒绝；无 `auto_cleanup_days` 控件。
- AC4 测试：pytest（handler/分批/整库拒绝）+ Vitest（列表/确认/错误映射）+ GUI 烟测（隔离库：建 2 本 → 删到回收站 → 设置页清空）。

---

## 3. 备份/恢复（section `backup`，C-2）

### 3.1 备份包格式 v1（冻结）

**文件形态**：单文件 `.nmbak`（zip 容器，扩展名自定义，内容标准 zip）。**目录形态不做**（避免半拷贝）。

```
<backup_id>.nmbak
├── manifest.json          # 格式/版本/生成信息/文件清单/校验
├── library.db             # SQLite 一致备份（既有 sqlite backup API）
├── library.db.sidecar.json# 既有 self-describing sidecar（schema_version + sha256）
└── managed/               # 受管文件（按 DB 中的 storage-relative managed_path 命名）
    ├── src/<book>/<...>   # 源图/中间产物（Managed Copy）
    └── ...
```

`manifest.json` 冻结字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `format` | string | 固定 `"nm-backup"` |
| `format_version` | int | 固定 `1`（破坏性变化才升级，读端拒绝未知 major） |
| `app_version` | string | 应用版本（来自 `app_version` 通道） |
| `schema_version` | int | DB schema 版本 |
| `created_at` | string | UTC ISO-8601 |
| `backup_type` | string | `manual` \| `automatic` \| `pre_migration` \| `pre_restore`（沿用既有枚举） |
| `database_sha256` | string | `library.db` 的 SHA-256 |
| `managed_file_count` | int | managed/ 下文件数 |
| `managed_total_bytes` | int | managed/ 总大小 |
| `revision_refs` | array | `{revision_id, region_id, managed_path, sha256, size_bytes}`——DB 中 current/pinned revision 引用受管文件的清单 |
| `verified` | bool | 生成时自检结果（读回校验通过才 true） |

**校验规则**：恢复前必须 `manifest.format == "nm-backup"`、`format_version` 支持、`database_sha256` 与库文件一致、`revision_refs` 每条 `sha256` 与 managed 文件一致；任一失败 → `BACKUP_CORRUPT`（validation，non-retryable），不得开始恢复。

**不含内容**（明确排除）：临时文件、trash 批次、导出产物、日志、缓存（`cache/`）、`plugins/`。

### 3.2 备份类型与触发

| 类型 | 触发 | 本期 |
|---|---|---|
| `manual` | 设置页"立即备份"按钮 | **C-2 实现** |
| `automatic` | 定时/启动调度 | **不开放**（无调度消费点；与 `auto_backup` 键一起留空） |
| `pre_migration` | schema 迁移前 | 既有 Core 语义（若已接线则复用；本期不新增 UI） |
| `pre_restore` | 恢复前自动 | **C-2 必须**（恢复的可回滚性依赖它） |

`auto_backup` / `auto_backup_days` / `keep_count` 三个键**本期不开放**（无调度器；与本文件 §1 纪律一致）。

### 3.3 恢复语义与冲突（冻结）

1. **覆盖式恢复**（沿用既有 `BackupLedger.restore_backup` 语义）：用备份库**覆盖当前 live DB**；不是合并。
2. **恢复前自动备份**：先创建 `pre_restore` 备份（完整包，含当前 live 状态）；若该备份失败 → **中止恢复**（无回滚点的恢复禁止执行）。
3. **managed 文件恢复**：按 manifest 清单写入 `<managed_root>/<managed_path>`；目标已存在时**覆盖**（与 DB 覆盖一致），但写入前先校验包内 sha256；包内缺失但 DB 引用存在 → 恢复后 `managed_consistency_report` 报 missing（不阻断恢复，报告给 UI）。
4. **revision 引用**：恢复后 `revision_refs` 中的 current/pinned revision 必须可解析；解析失败 → 报告（`BACKUP_RESTORE_INCOMPLETE`，category `conflict`）且 UI 显示受影响 revision 数量；不回滚已覆盖的 DB（回滚靠 pre_restore）。
5. **进行中 Run**：恢复是破坏性的，Core 必须在恢复前**拒绝存在 running Run**（`BACKUP_RESTORE_BUSY`，conflict，retryable=true）——不能出现"Run 快照指向旧 DB"的错乱。
6. **恢复后**：Core 重新加载 schema 版本（沿用 migrator 既有路径），不重启进程；UI 要求用户手动刷新其他页面（或 Tauri 触发全局刷新事件，C-2 实现时定）。

### 3.4 新增 wire（C-2）

| 命令 | 通道 | payload | result | 错误码 |
|---|---|---|---|---|
| `backup_create` | 应用层（StdioLibraryChannel） | `{backup_type:"manual"}`（**目标目录不出现在 payload**：写入固定备份根） | `{backup_id, path?（相对名）, size_bytes, created_at, verified}` | `BACKUP_CREATE_FAILED` |
| `backup_list` | 应用层 | `{}` | `[{backup_id, backup_type, created_at, size_bytes, schema_version, verified}]` | — |
| `backup_restore` | 应用层 | `{backup_id, confirm_restore:true}` | `{restored_from, pre_restore_backup_id, schema_versions, managed_consistency}` | `BACKUP_NOT_FOUND` / `BACKUP_CORRUPT` / `BACKUP_RESTORE_BUSY` / `BACKUP_RESTORE_INCOMPLETE` |
| `backup_delete` | 应用层 | `{backup_id}` | `{removed:true}` | `BACKUP_NOT_FOUND` |
| `backup_export`（可选） | Tauri 侧 dialog 选择目标目录后调用 | `{backup_id, target_dir}` | `{path}` | `BACKUP_EXPORT_FAILED` |

- **文件选择**：`backup_export` / 未来导入（`backup_import`）由 **Tauri 侧** `tauri_plugin_dialog`（既有 `blocking_pick_folder` 先例）选目录/文件，Core 只接收已选路径；React 不接触路径组装的细节（按钮 → `invoke` → Rust dialog → `invoke` Core）。
- 备份根固定：`<data_root>/backups/`（即有 `SqliteBackupService.backup_root` 语义）；不做用户任意路径写入（导出为复制到用户选择目录，属可选）。
- 协议 minor：应用层命令扩张，minor 保持 3（沿 B-2 先例；host 命令集合不变）。

### 3.5 安全边界

- 路径：Core 只接受 `backup_id`（32 hex）与备份根内解析；`backup_export` 的 `target_dir` 由 Tauri 选择后传入，Core 校验目标为绝对目录且非受管根内部（避免把备份写回受管目录）。
- 内容：恢复只读写受管与 DB，不触碰用户源文件（源文件不在受管根内，本就不在包内）。
- 确认：`backup_restore` 要求 `confirm_restore:true`；UI 二次确认弹窗写明"覆盖当前全部数据，恢复前自动备份"。

### 3.6 AC（C-2 实现时）

- AC1 包格式：生成包含 manifest/db/sidecar/managed，`verified=true`；损坏包被 `BACKUP_CORRUPT` 拒绝。
- AC2 恢复：覆盖 + pre_restore 生成 + consistency 报告；running Run 时 `BACKUP_RESTORE_BUSY`。
- AC3 列出/删除：真实文件；`BACKUP_NOT_FOUND` 幂等。
- AC4 前端：列表/创建/恢复二次确认/错误映射；无 `auto_backup` 控件。
- AC5 GUI 烟测：隔离数据根建库 → 备份 → 改数据 → 恢复 → 数据回到备份点。

---

## 4. Plugin/Hooks（section `plugins`，C-3）

### 4.1 安装来源与目录（冻结）

- **仅本地目录插件**（U-3 已批准；不做市场/在线分发/自动更新）。
- 插件根：`%LOCALAPPDATA%/New Manga/plugins/<plugin_id>/`（`data_root` 外的用户级目录；实现时以 `app_data_dir` 解析，不写死）。
- 安装 = 用户把插件目录放入插件根（设置页"打开插件目录"按钮）；**不做应用内安装器**。
- 插件目录对插件自身只读（插件不得自更新）；应用只读扫描插件目录，不写插件文件（除启用状态/审计存 DB）。

### 4.2 manifest v1（冻结字段）

`manifest.json`（插件根下每个 `<plugin_id>/` 一份）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 是 | `[a-z0-9-]{3,64}`，必须与目录名一致 |
| `name` | string | 是 | 展示名（≤80 字符） |
| `version` | string | 是 | semver `MAJOR.MINOR.PATCH` |
| `min_app_version` | string | 否 | 低于则拒绝加载 |
| `entry` | string | 是 | 相对于插件目录的入口文件（**仅 `.py`**，C-3 冻结 Python 插件） |
| `hooks` | array | 是 | 声明要挂载的 Hook，取值见 4.4；未知 Hook → 拒绝加载 |
| `permissions` | array | 是 | 取值 `{}`（C-3 只支持无权限插件）——见 4.3 |
| `description` | string | 否 | ≤200 字符 |

**拒绝规则**：字段缺失/类型错/`id` 与目录不符/未知 Hook/未知权限/入口不存在 → **不加载**（fail-closed），记录 `plugin_load_rejected` 审计。

### 4.3 权限与信任边界（冻结）

- **默认全部禁用**：`plugins.enabled = false`（全局总开关默认关）；已发现插件默认 `disabled`。
- **逐项权限**：C-3 首版权限集为 `files_read` / `files_write` / `network` / `model`（实际枚举以实现 Task 冻结为准），**默认关闭**；未声明的权限 = 不可用（fail-closed）。
- **C-3 首发限制**：只支持 `permissions: []` 的插件（无文件/网络/模型访问），即"纯计算/纯格式化"插件；带权限的插件在 C-2 执行面另批放开。
- **崩溃隔离**：Hook 调用在独立进程（或受隔离子进程）内执行，超时/崩溃 = 该次 Hook 跳过 + `plugin_error` 审计 + 主链路继续。
- **禁止绕 Repository**：插件不得直接连 DB/仓库；入参出参只走 versioned JSON schema。
- **审计**：每次加载/启用/禁用/调用/错误写 `plugin_events`（表结构在 C-3 冻结）。
- **安全默认值**：未知/损坏 manifest 不加载；`plugins.enabled=false` 时任何 Hook 都不调用。

### 4.4 Hook 契约（C2 执行面，冻结枚举）

按 D02 §12 六组 Hook：`before_detect` / `after_detect` / `before_ocr` / `after_ocr` / `before_export` / `after_export`（具体命名以实现 Task 冻结为准）。入参/出参为 versioned JSON schema（`schema_ref` 字段声明）；Hook 异常不改变主链路状态。

### 4.5 无实现前的 UI（本批只读）

- 设置页 `Plugin/Hooks` 分类**保持"未开放"状态**，按钮不开放；面板若存在只显示只读说明：

  > 插件系统尚未实现：当前版本未安装插件运行时。设计已冻结（本地目录插件、manifest v1、Hook 默认禁用、崩溃隔离、审计）；实现后将在此管理已安装插件与权限。

- 不提供"启用/禁用/重载/打开目录"按钮（无运行时，按钮无效果 = 假控件）。

### 4.6 AC（C-3 实现时）

- AC1 发现：合法 manifest 列出；未知 Hook/权限/字段 → 拒绝加载 + 审计。
- AC2 默认禁用：`plugins.enabled=false` 时 Hook 不调用；启用后仅声明的 Hook 被调用。
- AC3 隔离：Hook 崩溃/超时不影响主链路，记录 `plugin_error`。
- AC4 审计：加载/拒绝/启用/禁用/调用/错误均可查询。
- AC5 无实现前 UI 只读（本设计交付即满足；C-3 实现前不得出现可点控件）。

---

## 5. 新增 wire 总表（实现时）

| 命令 | 归属 | 状态 | 说明 |
|---|---|---|---|
| `library_list_recycle_bin_books` | 既有 | 已存在 | 回收站查看（C-1 复用） |
| `library_delete_books_permanently` | 既有 | 已存在 | 清空（C-1 复用，≤20/批） |
| `backup_create` / `backup_list` / `backup_restore` / `backup_delete` | 新增 | C-2 | 应用层命令；host 集合不变 |
| `backup_export`（可选） | 新增 | C-2 | Tauri dialog 选目录后调用 |
| `plugins_list` / `plugins_set_enabled` / `plugins_reload` / `plugins_open_dir` | 新增 | C-3 | 管理面；执行面另批 |
| `plugin_events_list` | 新增 | C-3 | 审计查询 |

宿主同步纪律（沿 M2-C1 §5.3）：Tauri `command_allowlist` / `generate_handler!` / `build.rs` manifest / capabilities 同 commit 同步；probe/ac1 模式冻结；前端 commandSurface pin 更新。

## 6. 决策清单（**需要用户裁决**）

每条：问题 → 选项 → 推荐 → 影响。裁决前不得实现。

- **D1 回收站清空确认**：仅二次确认对话框，还是要求用户输入"清空"字样？
  - 选项：a) 对话框二次确认（显示数量）；b) 输入字符串确认。
  - 推荐：**a**（数量已由既有 `confirm_count`/`confirmed_book_ids` 机制强校验；输入字符串对非技术用户过重）。
  - 影响：UI 文案与 Vitest 断言。
- **D2 回收站列表字段**：只展示现有投影（无"删除时间"），还是新增 `deleted_at` 到 wire？
  - 推荐：**只展示现有投影**（不扩 wire；无 `deleted_at` 时显示"已删除"）。
- **D3 备份包是否包含 managed 源图**：
  - 选项：a) 全量（SQLite + managed + revision 引用，体积大）；b) 仅 SQLite + revision 元数据（恢复后源图缺失需重新导入）；c) 用户可选。
  - 推荐：**a 全量**（备份语义完整；"仅元数据"恢复后不可渲染，属假备份）。
- **D4 备份目标位置**：固定备份根（`<data_root>/backups/`）+ 可选导出到用户目录，还是每次让用户选目录？
  - 推荐：**固定根 + 可选 `backup_export`**（固定根才能做 pre_restore/list/delete；任意目录会让 pre_restore 落点不可控）。
- **D5 恢复策略**：覆盖（既有语义）还是合并？
  - 推荐：**覆盖** + 强制 `pre_restore` 自动备份（既有 `BackupLedger` 语义，不新增合并复杂度）。
- **D6 恢复时进行中 Run**：拒绝恢复（推荐）还是允许并静默丢弃？
  - 推荐：**拒绝**（`BACKUP_RESTORE_BUSY`），避免 Run 快照与 DB 错位。
- **D7 Plugin 安装来源**：确认仅本地目录（U-3 已批准）？是否允许 `.zip` 导入？
  - 推荐：**C-3 仅本地目录**；zip 导入留待执行面（需解压校验与路径安全）。
- **D8 Plugin 运行时形态**：Python 插件（进程内？）还是外部进程？
  - 推荐：**外部进程（受隔离子进程）**，与"崩溃隔离"一致；Python 插件通过受控入口执行。
  - 影响：C-3 实现量与扩展文档；若选进程内则崩溃隔离退化为 try/except（不推荐）。
- **D9 Plugin 默认值确认**：`plugins.enabled=false` + 已安装插件默认禁用 + C-3 首发仅 `permissions: []` 插件——确认？
  - 推荐：**全部确认**（fail-closed）。
- **D10 Hook 首批范围**：C2 首批只做 `before_export` / `after_export` / `before_ocr` / `after_ocr`（extensions §1.3 建议）？
  - 推荐：**确认**（四组；detect 两组后续）。
- **D11 回收站/备份/Plugin 三节的 `settings_update_section` 是否永久拒绝**：确认"操作面 ≠ 设置键"（本文件结论）？
  - 推荐：**确认**（避免为写而写的假键）。

## 7. 实现分期与依赖

| 分期 | Task（建议） | 依赖 | 交付 |
|---|---|---|---|
| C-1 回收站 | `SETTINGS-OPEN-C-1-RECYCLE` | 本设计裁决 | 设置页回收站面板（查看/清空）+ pytest/Vitest + GUI 烟测；**无新 wire** |
| C-2 备份/恢复 | `SETTINGS-OPEN-C-2-BACKUP` | C-1（同批可并行但 UI 独立） | 备份包 v1 + 4/5 条新命令 + Tauri 文件选择 + 面板 + pytest/Rust/Vitest/GUI |
| C-3 Plugin C1 | `SETTINGS-OPEN-C-3-PLUGIN` | C-2（审计/隔离设施可复用） | manifest v1 发现 + 默认禁用 + 只读管理面；执行面 C2 另批 |

## 8. 风险与开放问题

1. **备份体积**：全量包可能数 GB；C-2 需要进度与磁盘空间检查（不设假进度条：先 `shutil.disk_usage` 预检 + 流式复制）。
2. **恢复的原子性**：覆盖 DB + 写 managed 不是原子事务；靠 `pre_restore` 回滚点，UI 必须提示"恢复前自动备份"。
3. **Plugin 进程隔离**：Windows 下的子进程权限/超时/输出上限需要实现 Task 冻结；首版可先只支持"纯计算"插件（无文件/网络）。
4. **安全审计**：插件审计表需要 migration（C-3 实现时新增，属 Schema 变更，需用户授权）。
5. **P15 §7 未开放状态**：本设计不改 P15 冻结契约；C-1/C-2/C-3 实现时按 B-2 先例补增量注记（应用层命令扩张、minor 不变）。
