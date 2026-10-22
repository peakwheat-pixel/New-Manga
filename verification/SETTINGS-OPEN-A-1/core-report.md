# SETTINGS-OPEN-A-1 Core 实现报告

- 任务：`doc/tasks/SETTINGS-OPEN-A-1.md`（批次 A，Core 侧）
- 实现者：DSH teammate `core-settings-a`（Lead：`lead`）
- 设计依据：[SETTINGS 分区 Schema 设计](../design/SETTINGS_SECTION_SCHEMAS.md) §2、§3.1–§3.5
- 日期：2026-10-22
- 状态：**实现与测试完成，未 commit**（按任务禁令，不执行 git commit/push/reset/stash）
- 基线 commit：`1fa2c3c58bcb0d5eb4d144d87e71d1ca7b3d3eac`（`main`），报告生成时 HEAD 仍为该 commit

## 1. 工作区/commit 前状态说明

- 报告生成时 `git status`：本 Task 的 Core 改动均为**未提交工作区改动**；`HEAD` 未移动。
- 工作区同时存在其他 writer（前端 `ui-settings-a`）的未提交前端文件与 `doc/STATUS.md` 改动；本报告只覆盖 Core 侧，未触碰 `apps/desktop/frontend/**`。
- 未执行 `git commit` / `push` / `reset` / `stash`。commit 点与集成由 Lead/Codex 在独立 Review 后处理。
- 本 Task 的报告/证据仅本文件；未创建 worktree/artifact。

## 2. 改动清单

| # | 文件 | 类型 | 说明 |
|---|---|---|---|
| 1 | `src/bootstrap/settings_sections.py` | 新增 | 批次 A 四节白名单/值域校验器：`SettingsSectionError(ValueError)`、`validate_settings_section(section, values)`。未知 section 返回 `None`（透传）；四节返回规范化 values（键名不变、JSON 数值转 schema 类型）；非法键/值拒绝。 |
| 2 | `src/bootstrap/core_service.py` | 修改 | `handle_settings_update_section` 在任何持久化之前调用校验器；`SettingsSectionError` → `SettingsRequestError`（既有 `INVALID_REQUEST`/`validation` 投影），非法写不落库。`handle_rerender_page`（手动整页重渲染命令）读取**当前全局** `pipeline_defaults.read().settings`，经 `typeset_style_defaults` 派生 `style_defaults` 并传给 `render.rerender_page(page_id, style_defaults=...)`（即时生效；手动命令无 Run 快照）。同步更新 handler/module docstring。 |
| 3 | `src/application/rendering/service.py` | 修改 | `RenderService.rerender_region` 新增关键字参数 `style_defaults: RenderTextStyle | None = None`，并原样透传给内部 `_prepare_region`（与 `rerender_page` 的 D03 §11.4 语义一致）。默认 `None` 时行为不变。 |
| 4 | `src/infrastructure/providers/handlers.py` | 修改 | 新增 `typeset_style_defaults(settings)`：仅映射白名单字段到 `RenderTextStyle`，`font_family` 等保持默认；缺失/非映射 section → `None`；非法枚举 `text_direction` 回退 `TextDirection.AUTO`；损坏值逐字段跳过（防御）。`handle_render` 用 `run.settings_snapshot` 派生并传 `style_defaults=`。 |
| 5 | `src/infrastructure/sqlite/pipeline.py` | 修改（Lead 2026-10-22 授权扩展） | `_redact` 增加**精确键名**豁免 `_REDACTION_ALLOWED_KEYS = frozenset({"context_token_budget"})`；`_SENSITIVE_PARTS` 与递归结构未改。 |
| 6 | `tests/core/test_settings_section_validation.py` | 新增 | Core 侧验收测试（91 项）：校验器单测、真实 production assembly 的 wire 合法/非法/未知键/未知 section/bool-int 回归/路径不回显、保存→下一 Run 快照、`style_defaults` 透传、`typeset` 映射与防御、**手动 `rerender_page` 使用当前全局 typeset 默认值**。 |
| 7 | `tests/core/test_core_service_settings.py` | 修改 | 旧断言按新冻结契约更新（未删除/弱化）：原“ocr 任意键透传”改为“未知 section（`providers`）透传”；路径回显测试对白名单节改为“写入被拒且不落库/不回显”。 |
| 8 | `tests/pipeline/test_pipeline_production_seam.py` | 修改（Lead 授权） | 新增安全回归：`context_token_budget` 持久化成功，同时 `api_key`/`password`/`auth_token`/`refresh_token`/`secret` 仍被丢弃且不出现在存储 JSON。 |

未改动：Schema/migration、依赖、Provider/Network/凭据/SFX 既有 wire 语义、`apps/desktop/frontend/**`、批次 B/C 分区。

## 3. 关键 diff 摘要

### 3.1 白名单与值域（`src/bootstrap/settings_sections.py`）

- `ocr`：`script ∈ {japanese,korean,chinese,latin}`、`direction ∈ {horizontal,vertical}`
- `translate`：`context_pages` int 1..5、`context_token_budget` int 200..8000
- `inpaint`：`preferred_quality ∈ {fast,balanced,quality}`、`background_complexity ∈ {low,medium,high}`、`dilate_radius`/`erode_radius` int 0..10
- `typeset`：`text_color`/`fill_color`/`stroke_color` 为 `#RRGGBB`；`stroke_enabled`/`auto_font_size` bool；`stroke_width` float 0..20；`line_spacing` float 1.0..3.0；`text_align ∈ {left,center,right}`；`text_direction ∈ {auto,horizontal,vertical}`；`font_size_offset` int -5..5；`manual_font_size` null 或 float 1..500
- 规范化：int 保持 int，float 字段（含 `manual_font_size`）统一转 `float`；字符串保持原值；未知键整片拒绝（不做部分接受）。
- **bool 是 int 子类**：int/float 字段显式排除 bool（`translate.context_pages=True`、`typeset.font_size_offset=True` 等均拒绝）；bool 字段拒绝 0/1。
- 未知 section 返回 `None`；已知 section 的空 `{}` 合法（保持写入空对象的既有语义）。

### 3.2 `handle_settings_update_section`

```python
try:
    validated = validate_settings_section(section, values)
except SettingsSectionError as error:
    raise SettingsRequestError(str(error)) from error
stored = values if validated is None else validated
defaults = self._core.pipeline_defaults.save_settings_section(section, stored)
```

校验先于 `save_settings_section`，错误文案含 `<section>.<field>` 与允许域，经既有 `_project_settings_value` 投影（错误文本中的 OS 路径也会被脱敏）。

### 3.3 渲染接入（两条渲染路径）

```python
# 路径 1：Pipeline render 步（handlers.handle_render）
outcome = self.deps.render_service.rerender_region(
    region_id,
    style_defaults=typeset_style_defaults(run.settings_snapshot),
)

# 路径 2：手动整页重渲染命令（core_service.handle_rerender_page，无 Run 上下文）
style_defaults = typeset_style_defaults(
    self._core.pipeline_defaults.read().settings   # 当前全局设置，即时生效
)
outcome = self._core.render.rerender_page(page_id, style_defaults=style_defaults)

# application/rendering/service.rerender_region
prepared = self._prepare_region(
    stored, source_style_result, style_defaults, allow_sfx=True
)
```

- `_merge_defaults` 未改：Region 已持久化值仍覆盖 defaults（D03 §11.4 顺序）。
- 映射：`auto_font_size → auto_font_size_enabled`，`text_direction → TextDirection`；`font_family`/`overflow_policy`/`detected_source_font_size` 等保持 `RenderTextStyle` 默认。
- 无 `typeset`、非 Mapping、空 Mapping → `None`（历史行为逐字节不变）。
- 两条路径语义差异（符合设计 §2.3）：Pipeline render 步使用 **Run 冻结快照**（保存后对下一次启动的 Run 生效）；手动 `rerender_page` 没有 Run，读取**当前全局**设置（保存后立即生效）。

### 3.4 `_redact` 最小豁免（安全相关，Lead 裁决 B）

```python
_REDACTION_ALLOWED_KEYS = frozenset({"context_token_budget"})

if str(key) in _REDACTION_ALLOWED_KEYS
   or not any(part in str(key).lower() for part in _SENSITIVE_PARTS)
```

- 仅精确键名 `context_token_budget` 豁免；`_SENSITIVE_PARTS` 与递归结构未改。
- 已证明该键是普通整数配置（`translate` 节，消费点 `handlers.py` translate 步），非 Secret；豁免不会扩大其他键的放行面。

## 4. 测试命令与原始结果

运行环境：Windows，`python 3.14.6`，`pytest 9.1.1`，仓库根目录 `G:\CODEX\New Manga`，分支 `main`。

| 命令 | 原始结果 | 结论 |
|---|---|---|
| `python -m pytest tests/core -q` | `655 passed, 1 warning in 46.53s` | **PASS**（exit 0） |
| `python -m pytest tests/core -k settings -q` | `239 passed, 416 deselected in 9.91s` | **PASS** |
| `python -m pytest tests/core/test_settings_section_validation.py -q` | `91 passed in 2.32s` | **PASS**（新增） |
| `python -m pytest tests/pipeline -q` | `95 passed in 1.41s` | **PASS** |
| `python -m pytest tests/rendering -q` | `69 passed, 1 warning in 2.11s` | **PASS** |
| `python -m pytest tests/core tests/rendering tests/pipeline -q` | `819 passed, 2 warnings in 48.92s` | **PASS** |
| `python -m pytest tests/providers -q` | `2 failed, 440 passed, 3 skipped in 10.68s` | 2 个失败为**改动前既有环境问题**（见 §5.3），与本次改动无关 |
| `python -m pytest tests/application -q` | `ERROR: file or directory not found: tests/application` | **NOT_RUN**：仓库不存在 `tests/application`（见 §5.2）；等价覆盖用 `tests/rendering`/`tests/pipeline` 结果 |

改动前基线：`python -m pytest tests/core -q` exit 0（全绿）；`python -m pytest tests/rendering -q` = `69 passed`。改动后上述必需套件仍全绿。

补充：`tests/core/test_core_service_settings.py::test_settings_commands_redact_paths_in_every_section` 已按新契约更新并随 `tests/core` 全绿；`tests/pipeline/test_pipeline_production_seam.py::test_sqlite_snapshot_keeps_context_token_budget_but_still_redacts_secrets` 单项 `1 passed`。手动整页重渲染两条新增测试（有/无 typeset）随新文件 91 项全绿。

## 5. 冲突、裁决与开放项

### 5.1 `translate.context_token_budget` 被存储层静默丢弃（已按 Lead 裁决 B 修复）

- **现象**：`src/infrastructure/sqlite/pipeline.py` 的 `_redact()` 对**任意层级键名**做子串过滤 `_SENSITIVE_PARTS = ("secret","password","token","api_key","apikey")`；`context_token_budget` 含 `token`，在 `PipelineDefaultsService.save_settings_section` → `SqliteSnapshotProvider.set_defaults` 落库前被整键删除。实测修复前：写入 `{"context_pages":3,"context_token_budget":4096}` 后投影/存储只剩 `{"context_pages":3}`，下一 Run 快照与 `handlers.py` 消费点永远读到默认 2000，设计 §3.2 的键等于不可用。
- **裁决**：Lead 2026-10-22 裁定选 B（根因修复），并扩展 task-1 允许范围到 `src/infrastructure/sqlite/pipeline.py` 及对应测试。
- **修复**：精确键名豁免（§3.4）；安全回归测试证明真正的敏感键仍被丢弃。
- **验证**：`settings.update_section` 写入后 `settings.get`、`pipeline_defaults.read().settings`、下一 Run `settings_snapshot["translate"]` 均含 `context_token_budget: 4096`。

### 5.2 环境/路径冲突：`tests/application` 不存在

任务书与本 Task 要求运行 `python -m pytest tests/application`，但当前仓库测试按领域分布在 `tests/core`、`tests/rendering`、`tests/pipeline`、`tests/providers` 等，**没有 `tests/application` 目录**（命令原始输出：`ERROR: file or directory not found: tests/application`）。本报告以 `tests/rendering`（渲染服务/真实 Qt 渲染栈）+ `tests/pipeline`（Snapshots/Run 持久化）作为等价覆盖，未新建空目录。

### 5.3 既有环境失败（与本次改动无关，未修复）

`tests/providers/test_detection_manga_real.py` 2 个用例失败：

```
ProviderError: PROVIDER_FAILED: manga detector engine failed to load from
G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector:
AttributeError('module transformers has no attribute RTDetrV2ForObjectDetection')
```

原因：本机 `transformers` 版本无 `RTDetrV2ForObjectDetection` + 外部权重路径，属既有环境/依赖问题；未改 detection 代码。报告生成前该文件即失败，本次改动不触及该路径。

### 5.4 设计 §3.4 `font_family` 未开放（保守跳过，未发明键；Lead 已确认）

设计 §3.4 的 typeset 表包含 `font_family`（要求命中 FontCatalog 否则写入拒绝），但批次 A 冻结白名单**不含** `font_family`；Lead 2026-10-22 明确该键不在批次 A（AC2 文本已由 Lead 同步更新，前端任务也明确“不含字体选择”）。因此本实现按默认 `Source Han Sans K Bold` 处理，对 `typeset` 提交 `font_family` 会按未知键返回 `INVALID_REQUEST` 并保留旧值——这是保守且正确的实现，不构成缺陷。字体选择/ FontCatalog 写入校验留待后续 Task 扩白名单与消费点。

### 5.5 渲染入口覆盖范围（两条路径均已接入）

- 路径 1 — Pipeline `render` 步（`handle_render` → `rerender_region(style_defaults=...)`）：数据来自 Run 冻结的 `settings_snapshot["typeset"]`；保存后**下一次启动的 Run** 生效，进行中的 Run 保持旧快照（符合设计 §2.3 快照语义）。测试：保存 typeset → 新 Run 快照包含该节（`test_saved_typeset_section_freezes_into_the_next_run_snapshot`），`handle_render` 映射/透传（`test_handle_render_maps_the_typeset_whitelist_from_the_run_snapshot`）。
- 路径 2 — 手动整页重渲染命令 `core.rerender_page`（`core_service.handle_rerender_page`）：手动命令没有 Run 上下文，因此读取**当前全局** `pipeline_defaults.read().settings["typeset"]`（`typeset_style_defaults`）并传给 `render.rerender_page(page_id, style_defaults=...)`，保存后立即生效。测试：`test_manual_rerender_page_uses_the_persisted_typeset_defaults`（断言 RenderService 收到映射后的 `RenderTextStyle`）与 `test_manual_rerender_page_without_typeset_keeps_the_default_style`（无 typeset → `None`，历史行为不变）。
- 设计 §3.4 建议的 `core_assembly.py` `Callable[[], RenderTextStyle | None]` 注入点未采用：本 Task 的实现改为在两条真实渲染入口处读取（Pipeline 用 Run 冻结快照、手动命令用当前全局设置），语义等价且无需改渲染装配；`core_assembly.py` 未改动。

## 6. 遗留项与风险

1. **未 commit**：所有改动为工作区改动，需 Lead/Codex 固定 commit 并进入独立 Review；本报告不含 commit hash。
2. **真实应用烟测 NOT_RUN**：未启动 dev preview 做“保存→重启→新 Run 生效”的 GUI 烟测（需要前端与运行环境；前端由 `ui-settings-a` 负责）。Core 侧用真实生产 assembly + 真实 Run 快照测试替代了链路证明。
3. **跨字段约束缺口**：`auto_font_size=false` 且 `manual_font_size` 未设置时，写入校验按冻结值域**允许**（设计未定义跨字段规则），但渲染时 `resolve_font_size` 会抛 `StyleResolutionError`，render 步以 `MISSING_REQUIRED_INPUT` fail-closed。建议前端在 auto 关闭时强制 manual size，或在后续 Task 增加跨字段校验；当前不会静默错误渲染。
4. **`text_align` 默认值差异**：`RenderTextStyle` 默认 `start`，本批值域为 `left|center|right`；未写入时保持 `start`（与 `left` 同义，Qt/Pillow 仅特判 `center`），已验证无渲染语义变化。
5. **遗留 legacy UI 绕过**：`src/ui/viewmodels/settings/viewmodel.py` 仍直接调用 `PipelineDefaultsService.save_settings_section`（PySide6 legacy 面，不在本 Task/新架构范围），不经 Core wire 校验；`handle_render` 的读取器对损坏/旧值做了防御（逐字段跳过），因此最坏情况是回退默认样式，不会崩溃渲染。
6. **`_redact` 豁免的边界**：豁免按精确键名、作用于所有 section/层级；未来若在别处新增同名键也会一并豁免。当前 `context_token_budget` 是普通整数配置键，该风险低且已被安全回归测试约束（其他敏感键仍丢弃）。
7. **`typeset` 键 `fill_color` 默认值**：设计写“默认渲染样式”，代码为 `DEFAULT_FILL_COLOR = #FFFFFF`；未写入时保持代码默认，符合“默认值由代码定义”的口径。

## 7. 验收对照（Core 部分）

- AC1 Core 写入校验：**已实现并测试**（四节合法写入/投影/落库；非法枚举/越界/类型错误/未知键 → `INVALID_REQUEST` 且存储不变；未知 section 透传；bool 不作为 int 接受）。
- AC2 排版默认样式接入：**已实现（两条渲染路径）**：`RenderService.style_defaults` 已接入 `rerender_region`；`handle_render` 从 Run 冻结快照派生并透传（保存→下一 Run 生效）；`handle_rerender_page` 从当前全局设置派生并透传（保存→立即生效）；Region 持久化样式优先（`_merge_defaults` 未改）。`font_family` 按 Lead 裁决不在批次 A 白名单（§5.4），其余键覆盖完整。
- AC3/AC4（前端/Vitest）：不在本 writer 范围（`ui-settings-a`），本报告 NOT_RUN。
- AC5（固定 commit/截图/独立 Review/Handoff）：未 commit；截图/烟测 NOT_RUN；独立 Review 由 Lead 指派非实现者执行。
