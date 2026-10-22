# SETTINGS 分区 Schema 设计（G25 白名单扩展）

- 状态：`proposed`（2026-10-22，用户裁决：设置页全部 9 个禁用分区开放）
- 依据：[AD001 四页设计基线](../design/AD001_FOUR_PAGE_UI_BASELINE.md) §5、[P15 设置 IPC 契约](../contracts/P15_SETTINGS_IPC_CONTRACT.md) §7（G25）、[04 用户流程](../04_USER_FLOW.md) §38–§43、现有 Core 消费点（见下表）
- 本文件是逐分区契约冻结的前置设计；冻结后以契约为准，本文件不替代契约。

## 1. 目标与范围

设置页 12 分类中，当前仅 Provider、网络/代理、翻译（SFX 策略）可编辑；其余 9 个分类（OCR、图片修复、排版样式、模型/GPU、任务/并发、缓存/Revision、回收站、备份/恢复、Plugin/Hooks）与翻译分类内的"翻译参数/上下文策略"禁用。

本设计把"未开放"从 11 项收敛为 0，按三批实施：

| 批次 | 分区 | 后端现状 | 风险 |
|---|---|---|---|
| A | OCR、翻译参数/上下文、图片修复、排版样式 | Core 已有消费点，写入即对新 Run 生效；排版默认样式合并语义已存在 | 低 |
| B | 模型/GPU、任务/并发、缓存/Revision | 部分消费点，需要新增装配/调度接入 | 中 |
| C | 回收站、备份/恢复、Plugin/Hooks | 回收站/清理/备份应用层用例已存在，但 Core/Tauri wire 与自动策略缺失；Plugin 从零实现 | 高 |

## 2. 通用约束

1. **wire 不变**：继续使用 `settings.get` / `settings.update_section`（M2-C1 §5.3），不新增通用"任意键写入"。Core 侧按本节白名单逐键校验，未知节/未知键 fail-closed。
2. **写入即校验**：非法值在任何持久化之前以 typed 错误拒绝（`SettingsRequestError` → `INVALID_REQUEST`），避免损坏启动读取。
3. **快照语义不变**：设置写入 `pipeline_defaults.settings`，对**之后启动的 Run** 生效；进行中的 Run 使用冻结快照。UI 必须显示"对之后的任务生效"。
4. **不伪造**：没有消费点的设置不得开放。若某键暂无法生效，就不出现在白名单里，也不在 UI 出现假控件。
5. **安全边界**：设置 DTO 不承载 Secret、明文凭据、认证头或任意文件系统路径。字体以字体族名（FontCatalog 已解析）而非路径出现。
6. **REV 透明**：所有值均为普通配置值；不新增凭据/路径类字段。

## 3. 批次 A：核心翻译参数（本节先实现）

### 3.1 OCR（section `ocr`）

| 键 | 类型 / 值域 | 默认 | 消费点（现状） |
|---|---|---|---|
| `script` | `japanese` \| `korean` \| `chinese` \| `latin` | `japanese` | `src/infrastructure/providers/handlers.py:329`；枚举 `src/ports/providers/ocr.py`（`ALL_SCRIPTS`） |
| `direction` | `horizontal` \| `vertical` | `horizontal` | `handlers.py:330`；枚举 `ALL_DIRECTIONS` |

- 覆盖键：本批不扩展（`SETTING_KEYS` 无 `ocr.*`）。全局值经 Run `settings_snapshot` 进入 OCR handler。
- UI：两个下拉框 + 保存；显示"对之后启动的任务生效"。

### 3.2 翻译参数 / 上下文策略（section `translate`）

| 键 | 类型 / 值域 | 默认 | 消费点（现状） |
|---|---|---|---|
| `context_pages` | int，1–5 | `1`（`DEFAULT_CONTEXT_PAGES`） | `handlers.py:938`（多页上下文窗口） |
| `context_token_budget` | int，200–8000 | `2000`（`DEFAULT_CONTEXT_TOKEN_BUDGET`） | `handlers.py:412`；context builder 预算 |

- `glossary` 不在此分区开放（术语表/不译表属于书架/工作台维护面，另立契约）。
- `context.strategy` 覆盖键（`SETTING_KEYS` 现有）本批仍只读，不提供写入口。
- UI：两个数值输入（带范围校验与说明）。

### 3.3 图片修复（section `inpaint`）

| 键 | 类型 / 值域 | 默认 | 消费点（现状） |
|---|---|---|---|
| `preferred_quality` | `fast` \| `balanced` \| `quality` | `balanced` | `handlers.py:596`；`application/translation/inpaint/router.py`（`ALL_QUALITIES`） |
| `background_complexity` | `low` \| `medium` \| `high` | `low` | `handlers.py:597`；`router.py`（`ALL_COMPLEXITIES`） |
| `dilate_radius` | int，0–10 | `2` | `handlers.py:524` |
| `erode_radius` | int，0–10 | `0` | `handlers.py:525` |

- 不开放：`is_speech_bubble` 等 Region 级路由信号（不是用户设置）、`route_policy`（内部路由结构，另立契约）。
- UI：两个下拉框 + 两个数值输入；附"质量越高越慢"说明。

### 3.4 排版样式（section `typeset`）与阅读方向（section `reading`）

排版默认样式由 `RenderService` 的 `style_defaults` 合并进每个 Region（`application/rendering/service.py:459`、`_merge_defaults` D03 §11.4 继承顺序）。现状：装配点 `core_assembly.py:1104` 传入 `None`；本批把 settings 派生的默认值接上（建议注入 `Callable[[], RenderTextStyle | None]` 以便设置保存后即时生效）。

| 键 | 类型 / 值域 | 默认 | 消费点 / 计划 |
|---|---|---|---|
| `font_family` | string（必须存在于 FontCatalog；否则拒绝） | `Source Han Sans K Bold` | **本批不开放**：字体列表/上传需要新增 wire（U-5 边界另立 Task）；批次 A 的 typeset 白名单不含此项，面板只显示当前默认字体 |
| `text_color` | `#RRGGBB` | `#000000` | 同上 |
| `fill_color` | `#RRGGBB` | 默认渲染样式 | 同上 |
| `stroke_enabled` | bool | `true` | 同上 |
| `stroke_color` | `#RRGGBB` | `#FFFFFF` | 同上 |
| `stroke_width` | float，0–20 | 默认（`DEFAULT_STROKE_WIDTH`） | 同上 |
| `line_spacing` | float，1.0–3.0 | 默认（`DEFAULT_LINE_SPACING`） | 同上 |
| `text_align` | `left` \| `center` \| `right` | 默认（`DEFAULT_TEXT_ALIGN`） | 同上 |
| `text_direction` | `auto` \| `horizontal` \| `vertical` | `auto` | 同上 |
| `auto_font_size` | bool | `true` | 同上（D03 §11.2 自动字号） |
| `font_size_offset` | int，-5–+5 | `0` | 同上 |
| `manual_font_size` | float，> 0（仅 `auto_font_size=false` 时有意义） | `null` | 同上 |

阅读方向（section `reading`，键 `direction`：`rtl` \| `ltr` \| `vertical`）：
- 现状：方向是 **Book/Chapter 属性**（`domain/library/entities.py`），Run 覆盖解析已支持 `reading.direction`（`settings_commands.py:836`），但阅读器/工作台实际取章节属性。
- 本批不伪造"全局阅读方向"控件；排版分区内只放**说明 + 书籍/章节方向的入口指引**（方向在书架/章节属性里改）。若用户要求"新建章节默认方向"，另立契约与消费点后再开放。

### 3.5 写入校验（Core）

`handle_settings_update_section` 对每个白名单节：
- 未知键 → `INVALID_REQUEST`（不再透传）；
- 类型/值域不符 → `INVALID_REQUEST` + 字段名；
- 未知 section 保持现有透传（向后兼容），但 UI 不会提交白名单外的节；
- 校验后仍走 `PipelineDefaultsService.save_settings_section`。

## 4. 批次 B：运行环境与维护

### 4.1 模型/GPU（section `model_gpu`）

| 键（拟议） | 值域 | 默认 | 需要新增的消费点 |
|---|---|---|---|
| `device_preference` | `auto` \| `cpu` \| `gpu` | `auto` | `infrastructure/devices/manager.py` 设备选择（新增） |
| `allow_cpu_fallback` | bool | `true` | Provider runtime 设备回退（新增） |
| `gpu_concurrency` | `serial` \| `allow_concurrent` | `serial` | 单槽 gate（`manager.py` 现为默认单槽，需显式开关） |

- 模型下载/路径管理不在本分区（D07 §84 模型下载语义另立 Task）。
- 只读展示：当前设备能力（`DeviceInfo`：kind/name/state/error_code）。

### 4.2 任务/并发（section `tasks`）

| 键（拟议） | 值域 | 默认 | 消费点（现状/新增） |
|---|---|---|---|
| `retry_max_attempts` | int，1–3 | `3` | `providers/runtime.py:_retry_policy` 读取 `settings["providers"]["retry"]`（现状），可迁移到 `tasks.retry`（新增映射） |
| `retry_backoff_seconds` | float，0.1–30 | `1.0` | `RetryPolicy`（需扩展 runtime 读取） |

- **并发数不开放**：`application/tasks/service.py` 明确 `max_parallel_pages=1` / `max_parallel_steps=1` 为强制不变量；UI 只显示"任务串行执行"的只读说明。若用户要求可调并发，需先裁决突破不变量并改调度器，另立 Task。

### 4.3 缓存/Revision（section `cache`）

| 键/操作（拟议） | 值域 | 默认 | 需要新增的消费点 |
|---|---|---|---|
| `auto_cleanup_days` | `never` \| `7` \| `30` \| `90` | `never` | 启动/定时清理调度（新增） |
| 清理操作 | 预览 + 执行 + 重试挂起项 | — | `application/maintenance/cleanup.py`（已存在，需接 Core/Tauri wire） |

- Revision 保留策略暂不开放（需要 revision 存储层语义与 GC 设计落地，见 `M2_DERIVED_PREVIEW_GC_DESIGN.md`）。

## 5. 批次 C：数据安全与扩展

### 5.1 回收站（section `recycle_bin`）

| 键/操作 | 值域 | 默认 | 现状 |
|---|---|---|---|
| `auto_cleanup_days` | `never` \| `7` \| `30` \| `90` | `never`（D04 §43.4） | 无调度，需新增 |
| 批次列表 | — | — | `application/maintenance/trash.py:list_batches`（已存在） |
| 同批恢复 | — | — | `trash.py:restore_batch`（已存在） |
| 永久删除 | — | — | `trash.py:purge_batch`（已存在）；Core 现有 `PermanentlyDeleteBook(s)` 只覆盖 book 级 |

- 需要新增 Core/Tauri wire：`ListTrashBatches` / `RestoreTrashBatch` / `PurgeTrashBatch`，并接自动清理调度。

### 5.2 备份/恢复（section `backup`）

| 键/操作 | 值域 | 默认 | 现状 |
|---|---|---|---|
| `auto_backup` | bool | `false` | 无消费点，需新增 |
| `auto_backup_days` | 1–30 | `7` | 需新增 |
| `keep_count` | 1–20 | `5` | 需新增 |
| 创建/列出/恢复备份 | — | — | `infrastructure/sqlite/backup.py`（已存在 create/restore/backup_records）；需接 Core/Tauri wire 与 UI |

- 恢复必须保留 pre-restore 自动备份（既有语义），UI 二次确认。

### 5.3 Plugin / Hooks（section `plugins`）

- 契约草案：[extensions.md](../contracts/extensions.md) §1.3（U-3 已批准：仅本地目录插件；manifest.json；六组 Hook；权限逐项默认关闭；fail-closed；崩溃隔离；审计）。
- 分期：
  - C1（管理面）：插件目录只读展示、插件清单（id/版本/权限/状态）、启用/禁用、重载、打开目录；`plugins.enabled` 总开关。
  - C2（执行面）：六组 Hook（按 D02 §12，首批建议 before/after export + before/after ocr）、versioned JSON schema、异常跳过 + Plugin Error 记录 + 审计。
- 需要新增：插件发现/加载/权限模型/审计表/UI。

## 6. 错误与安全

- 所有写入错误走既有 `SettingsRequestError` 封闭投影；不回显原始响应/认证头/路径。
- 字体族名必须命中 FontCatalog；否则拒绝并提示重新选择。
- 备份/回收站操作需明确确认；永久删除与恢复不得删除用户源文件（沿用 D04 §43.3 与 Managed Copy 语义）。

## 7. 验收

| 层 | 验收 |
|---|---|
| Core（pytest） | 每节：合法写入生效、非法值/未知键拒绝、未知 section 兼容、默认值投影 |
| 前端（Vitest） | 每个面板：渲染、修改、保存调用、错误展示、禁用态移除 |
| E2E/GUI 烟测 | 真实应用中 9 个分类全部可点击进入；保存后重启仍保留；新 Run 使用新值 |

## 8. 待裁决 / 开放问题

1. 排版字体来源：批次 A 仅内置 FontCatalog 字体；用户上传字体（U-5 已批准边界）作为后续 Task。
2. 阅读方向：维持"书籍/章节属性"，设置页不提供全局默认（如需要另立）。
3. 模型/GPU 的"GPU 并发"与任务/并发"可调并发"：需用户裁决是否突破当前串行不变量。
4. 备份/恢复与 Plugin 的 MVP 范围：建议 C1 管理面先行、C2 执行面另批。
