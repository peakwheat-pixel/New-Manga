---
task_id: SETTINGS-OPEN-A-1
author: dsh (Lead, epoch 10)
recipient: Codex / 下一批次 Owner
base_commit: 1fa2c3c58413b6bce972bd20fb044438d538d3d6
delivery_head: 6a303a9d2c66f6ffbfee2aec6ebde359312a6b33
status: approved
---

# Handoff：SETTINGS-OPEN-A-1（设置分区开放批次 A）

## 交付结果

用户 2026-10-22 裁决"设置页 9 个禁用分区全部开放"后，本 Task 完成批次 A：**OCR / 翻译参数+上下文 / 图片修复 / 排版样式** 四个分区从禁用变为可编辑，并在真实 Tauri 应用中生效。

- 实现提交：`87ae85a678880bff840ac77b53f2700e586ad95c`（40 文件，未 push）
- 设计/契约草案：[doc/design/SETTINGS_SECTION_SCHEMAS.md](../design/SETTINGS_SECTION_SCHEMAS.md)（§3 批次 A 键集/值域）
- 任务：[doc/tasks/SETTINGS-OPEN-A-1.md](../tasks/SETTINGS-OPEN-A-1.md)
- 实现报告：[verification/SETTINGS-OPEN-A-1/core-report.md](../../verification/SETTINGS-OPEN-A-1/core-report.md)、[ui-report.md](../../verification/SETTINGS-OPEN-A-1/ui-report.md)

### AC 对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 Core 写入校验（四节白名单/值域；未知键拒绝；未知 section 透传；不落库） | 完成 | `tests/core/test_settings_section_validation.py`（91 项）+ `tests/core/test_core_service_settings.py` 更新；`pytest tests/core -q` 655 passed |
| AC2 排版默认样式接入（两条渲染路径：Run 冻结快照 + 手动整页重渲染） | 完成 | `handlers.typeset_style_defaults`；`handle_render` 与 `handle_rerender_page` 均接入；`pytest tests/pipeline tests/rendering` 164 passed |
| AC3 前端分区开放（四面板 + 翻译参数替换占位） | 完成 | `apps/desktop/frontend/src/settings/{Ocr,TranslationParams,Inpaint,Typeset}SettingsPanel.tsx`；`SettingsPage.tsx` 6 开 6 关 |
| AC4 测试（pytest + Vitest，全部通过、未弱化） | 完成 | 后端 819 passed；前端 37 files / 364 tests passed；tsc 无错误；既有断言按行为变化更新（见 ui-report §4） |
| AC5 证据/Handoff/独立 Review | 完成 | 证据与 Handoff 已提交；独立 Review r1 `changes_requested` → r2 `approved`（`review-r1.md`、`review-r2.md`）；集成目标 commit `6a303a9` |

### 一并修复的存储层缺陷

`_redact()` 按子串匹配键名，把 `translate.context_token_budget` 当敏感键整键丢弃。已按 Lead 裁决做**精确键名豁免**（`_REDACTION_ALLOWED_KEYS`）；回归测试证明 `api_key`/`password`/`auth_token`/`refresh_token`/`secret` 仍被丢弃。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| Core 四节校验 | `python -m pytest tests/core -q` | Windows / Python 3.14.6 / 87ae85a | PASS 655 | core-report.md |
| 新增校验器 | `python -m pytest tests/core/test_settings_section_validation.py -q` | 同上 | PASS 91 | 同上 |
| 渲染两路径 + 持久化 | `python -m pytest tests/pipeline tests/rendering -q` | 同上 | PASS 164 | 同上 |
| Lead 全量后端回归 | `python -m pytest tests/core tests/pipeline tests/rendering -q` | 87ae85a | PASS 819（exit 0） | 本 Handoff 记录 |
| 前端 | `pnpm --dir apps/desktop/frontend test` / `npm test` | node 24 / vitest | PASS 37 files / 364 tests | ui-report + `frontend-*-raw.txt` |
| 类型检查 | `tsc --noEmit` | 同上 | PASS（无输出） | `frontend-tsc-raw.txt` |
| 真实 GUI 烟测 | dev preview → 设置 → 图片修复 → 背景复杂度 medium → 保存 | Tauri dev，隔离数据根 `G:\CODEX\New Manga.workspace\dev-preview\data` | PASS：UI 显示"当前持久化值：均衡 (balanced) · 背景 中 (medium) · dilate 2 / erode 0"；SQLite `pipeline_defaults.settings_json` = `{"inpaint": {"background_complexity": "medium", ...}}` | `gui-smoke.md` + `screenshots/01..06` |
| 重启后读取复查 | dev preview 重启 → 打开图片修复 | 同上 | 见 closeout 追加 | 待记录 |
| `tests/providers` 2 失败 | `python -m pytest tests/providers -q` | 本机环境 | 既有环境问题（transformers 缺 `RTDetrV2ForObjectDetection`），与本改动无关 | core-report §5.3 |
| `tests/application` | — | — | NOT_RUN：仓库无该目录（任务书路径笔误） | core-report §5.2 |

## 接收方式

- 分支 `main`，工作区干净，HEAD = `87ae85a678880bff840ac77b53f2700e586ad95c`（未 push）。
- 复现：仓库根 `pwsh -NoProfile -File tools/dev/dev-preview.ps1`（隔离数据根，不碰用户数据）；设置页应显示 6 个开放分类、6 个"未开放"分类。
- 验证：上述 pytest / vitest 命令。
- 前端测试通道：仓库跟踪的是 npm（`package-lock.json`）；pnpm 11 首次运行会自动生成 `pnpm-workspace.yaml`/`pnpm-lock.yaml`（环境产物，已从提交清理，不属交付物）。

## 下一任务建议（必填）

- Task ID / 标题：**SETTINGS-OPEN-B-1** — 设置分区开放批次 B：模型/GPU、任务/并发、缓存/Revision
- 推荐 Agent / Reviewer：实现 Agent（ZCode 或 Antigravity，按项目分工）；Reviewer=独立子代理（非实现者）
- 推荐原因与前置依赖：批次 A 已建立"每节白名单 + Core 校验 + 面板"模式；批次 B 需要新增消费点（device 偏好/CPU 回退/重试退避/缓存清理 wire），依赖本 Task 的 `settings_sections.py` 扩展点与 `SettingsClient.getSection/saveSection`。
- Recovery point：仓库 `G:\CODEX\New Manga`，`main`，base=`87ae85a`；未创建 worktree（待 Codex 创建）
- 允许修改路径：`src/bootstrap/settings_sections.py`、`src/bootstrap/core_service.py`、`src/bootstrap/settings_commands.py`、`src/infrastructure/devices/**`、`src/infrastructure/providers/runtime.py`、`src/application/maintenance/**`、`apps/desktop/frontend/src/settings/**`、`tests/**`、`verification/SETTINGS-OPEN-B-1/**`
- 禁止范围：不改批次 C（回收站/备份/Plugin）、不改 Schema/migration、不突破 `max_parallel_pages/steps=1` 串行不变量（需用户另行裁决）、不引入 Secret/路径
- 交付物：四节（model_gpu/tasks/cache）白名单与 Core 校验/消费点、对应面板、测试、证据、Handoff
- 验证命令/环境/完成 Gate：`python -m pytest tests/core tests/pipeline tests/rendering -q`、前端 vitest 全绿、GUI 烟测；独立 Review approved
- 可直接转发给 Agent 的指令：见 doc/design/SETTINGS_SECTION_SCHEMAS.md §4；按批次 A 模式实现，禁止发明无消费点的键。

## 风险与遗留

1. **独立 Review 第一轮 `changes_requested`，已返修 r2 并获 `approved`**：评审报告 `verification/SETTINGS-OPEN-A-1/review-r1.md`、`review-r2.md`。处置：B1 `_merge_defaults` 优先级重写（用 domain `TextStyle` 原始字段判断持久化；渲染级回归 `tests/rendering/test_typeset_defaults_merge.py` 在旧实现上 3 failed / 修复后 4 passed）；B2 移除无消费者的 `fill_color`（白名单/映射/UI）；M1 增加 `auto_font_size=false` → `manual_font_size` 必填的跨字段校验；M2 `text_align` 收窄 `left|center`；M3 两份冻结契约补 2026-10-22 增量修订注记；M4 base_commit 更正为真实 `1fa2c3c58413b6bce972bd20fb044438d538d3d6`；m1/m2/m3/m5/m6 分别在设计/前端/测试/任务书/烟测证据中处理。r2 独立测试：pytest `832 passed`（tests/core+pipeline+rendering）、`npm --prefix apps/desktop/frontend test` 37 files/367 tests、tsc exit 0。最终集成目标：`6a303a9d2c66f6ffbfee2aec6ebde359312a6b33`（**不要集成 `87ae85a`**，那是被 r1 否决的实现）。
2. **`typeset.font_family` 未开放**：字体列表/上传需要新增 wire（U-5 边界），设计 §3.4 已注明；当前字体保持 FontCatalog 默认。
3. **跨字段约束**：`auto_font_size=false` 且 `manual_font_size` 未设置现在被 Core 拒绝（r2）；前端同步禁用保存并提示。
4. **partial typeset 语义（用户可见）**：保存任意 `typeset` 键后，未在 Region 持久化的字段取全局默认（例如仅保存 text_color 时 stroke_width 从历史合成 0.0 变为 `RenderTextStyle` 默认 3.0），符合 D03 §11.4 继承顺序；设计 §3.4 已记录。
5. **`text_align` 默认 `start`**：前端按 `left` 显示且不提交 `start`；不改变渲染语义（Qt/Pillow 仅特判 center）。
6. **legacy PySide6 设置 ViewModel** 仍绕过新 Core wire 校验（legacy 面，不在新架构范围）；渲染读取端已做防御。
7. **未 push**：按要求不 push/merge；集成由后续 Codex/主控处理。
8. **GUI 烟测范围**：inpaint 逐分区保存 + 重启复查已做；OCR/翻译/排版的逐分区保存与 typeset 渲染效果由 pytest 渲染级回归覆盖，真实页面渲染效果未做 E2E。
