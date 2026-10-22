# SETTINGS-OPEN-A-1 前端实现报告（批次 A）

- 团队任务：`task-2`（SETTINGS-OPEN-A-1 Frontend：四个设置面板 + 分类开放）
- 实现 agent：`ui-settings-a`（DeepSeek Harness）
- 仓库 / 分支：`G:\CODEX\New Manga` / `main`（未 commit、未 push）
- 依据：[SETTINGS 分区 Schema 设计 §3](../doc/design/SETTINGS_SECTION_SCHEMAS.md)、[SETTINGS-OPEN-A-1 任务](../doc/tasks/SETTINGS-OPEN-A-1.md)
- 实现范围：仅 `apps/desktop/frontend/src/settings/**` 与 `verification/SETTINGS-OPEN-A-1/**`

## 1. 交付结论

- 设置页 `ocr` / `translate`（翻译参数/上下文）/ `inpaint` / `typeset` 四个分区已开放；
  `translation` 分类保留 SFX 面板并加入翻译参数面板；`ocr` / `inpaint` / `typeset`
  内容区为真实可编辑面板，不再渲染 `DisabledSection`。
- 四个面板均实现：section 读取（`settings_get {section}`）、JSON null 的“未设置 + Core
  默认值”提示、前端值域校验、整节保存（`settings_update_section {section, values}`）、
  保存后重新读取回显、加载/保存错误走 `SettingsErrorBar`（关闭 §9 投影）、
  “对之后启动的任务生效”说明、保存中禁用与错误不丢草稿。
- 其余 6 个分区（model_gpu / task_concurrency / cache_revision / recycle_bin /
  backup_restore / plugins）保持禁用占位与 `未开放` 徽标；导航 `aria-label`/`title`
  的“未开放：等待 section schema 冻结”只保留给这 6 个分区。
- 测试：`pnpm --dir apps/desktop/frontend test` 全绿（37 files / 364 tests），
  `tsc --noEmit` 无错误；`npm test`（同一 vitest 套件，仓库跟踪的 package-lock 通道）交叉验证一致。
- Lead 裁决同步：`translate.context_token_budget` 键名保持不变，前端按设计 §3.2 原样提交，
  未做任何改名或降级。

## 2. 改动清单

### 2.1 修改（M）

| 文件 | 变更 |
|---|---|
| `apps/desktop/frontend/src/settings/client.ts` | 新增通用 `getSection<T>(section): Promise<T \| null>` 与 `saveSection(section, values): Promise<void>`；复用 `SETTINGS_GET_COMMAND` / `SETTINGS_UPDATE_SECTION_COMMAND` 与 `SettingsClientError` 错误映射；null / 缺失 section 均返回 null（与 `getSfxSection` 的 frozen-None 语义一致），非对象载荷 fail-closed 为 null。既有方法语义未改。 |
| `apps/desktop/frontend/src/settings/SettingsPage.tsx` | `ocr`/`inpaint`/`typeset` 改 `open: true`；翻译分类 `SfxPolicyControl` + `TranslationParamsPanel`；ocr/inpaint/typeset 渲染对应面板；`DISABLED_SECTION_TEST_IDS` 移除已开放分支；排版分类内“阅读方向”改为只读指引说明（设计 §3.4，不提供假控件、不再用 DisabledSection 占位）；标题注释同步。 |
| `apps/desktop/frontend/src/settings/SettingsPage.test.tsx` | 按行为变化更新：分类 open 断言（6 开 / 6 关）、开放分类可点击并渲染真实面板、翻译参数占位消失、键盘导航断言与补充；保留 6 个仍禁用分区的 disabled + `未开放` + `等待 section schema 冻结` 断言。 |
| `apps/desktop/frontend/src/settings/client.p15.test.ts` | 更新唯一一条随行为变化的“无通用 update 方法”结构守卫：`updateSection` 仍未定义，`saveSection` 现在是冻结的命名 section API（逐节白名单仍在 Core），`saveSfxPolicy` 不变。 |

### 2.2 新增（A）

| 文件 | 内容 |
|---|---|
| `apps/desktop/frontend/src/settings/sections.ts` | 批次 A 四节的单一前端事实源：section 名、枚举/值域/范围常量、Core 默认值、wire→draft 归一化、前端校验、draft→payload 构造、持久化值摘要文案。 |
| `apps/desktop/frontend/src/settings/useSettingsSection.ts` | 四面板共享生命周期（加载 / 重试 / 保存 / 保存后重新读取 / 关闭错误投影），沿用 SfxPolicyControl 的状态模式。 |
| `apps/desktop/frontend/src/settings/SectionPanelFrame.tsx` | 共享面板外壳：卡片、标题、加载骨架、“对之后启动的任务生效”说明、未设置提示、保存按钮/状态、错误条、当前持久化值。 |
| `apps/desktop/frontend/src/settings/SectionField.tsx` | 共享字段行（label/htmlFor/hint/`role=alert` 行内校验）+ 输入样式 + `onChange`/`onInput` 双通道写草稿（jsdom 与 WebView 均可用，沿用 ProviderProfilePanel 既有模式）。 |
| `apps/desktop/frontend/src/settings/OcrSettingsPanel.tsx` | `ocr.script`（japanese/korean/chinese/latin）、`ocr.direction`（horizontal/vertical）下拉 + 保存。 |
| `apps/desktop/frontend/src/settings/TranslationParamsPanel.tsx` | `translate.context_pages`（int 1–5，默认 1）、`translate.context_token_budget`（int 200–8000，默认 2000）数字输入 + 前端范围校验。 |
| `apps/desktop/frontend/src/settings/InpaintSettingsPanel.tsx` | `inpaint.preferred_quality`（fast/balanced/quality）、`background_complexity`（low/medium/high）、`dilate_radius`（0–10）、`erode_radius`（0–10），附“质量越高越慢”说明。 |
| `apps/desktop/frontend/src/settings/TypesetSettingsPanel.tsx` | `typeset` 11 键：text_color / fill_color / stroke_color（`<input type="color">` + `#RRGGBB` 文本回显）、stroke_enabled、stroke_width（0–20）、line_spacing（1.0–3.0）、text_align（left/center/right）、text_direction（auto/horizontal/vertical）、auto_font_size、font_size_offset（-5..5）、manual_font_size（可空，1–500）。**不含 font_family**（本批不开放）。 |
| `apps/desktop/frontend/src/settings/OcrSettingsPanel.test.tsx` | 6 tests：加载、读取回显+生效说明、未设置默认、保存 payload+重读、加载错误投影+重试、保存失败保留草稿。 |
| `apps/desktop/frontend/src/settings/TranslationParamsPanel.test.tsx` | 8 tests：加载、读取回显、未设置默认、数值 payload+保存中+重读、context_pages 越界拦截、token_budget 越界拦截、加载错误、保存失败保留草稿。 |
| `apps/desktop/frontend/src/settings/InpaintSettingsPanel.test.tsx` | 7 tests：加载、读取回显、未设置默认、payload+重读、dilate 越界拦截、加载错误、保存失败保留草稿。 |
| `apps/desktop/frontend/src/settings/TypesetSettingsPanel.test.tsx` | 9 tests：加载、全键读取回显（含 font_family 不存在）、未设置默认样式、11 键 typed payload+重读、manual 空值→null、stroke/line 越界拦截、offset/manual 越界拦截、加载错误、保存失败保留草稿。 |
| `apps/desktop/frontend/src/settings/client.sections.test.ts` | 6 tests：`getSection` 精确请求/返回、null 与缺失可区分、非对象 fail-closed、读错误映射；`saveSection` 精确 `{section, values}`、写错误映射。 |

### 2.3 关键 wire 契约（面板实际提交）

| 节 | 提交值 |
|---|---|
| `ocr` | `{ script, direction }` |
| `translate` | `{ context_pages: number, context_token_budget: number }` |
| `inpaint` | `{ preferred_quality, background_complexity, dilate_radius: number, erode_radius: number }` |
| `typeset` | `{ text_color, fill_color, stroke_enabled, stroke_color, stroke_width: number, line_spacing: number, text_align, text_direction, auto_font_size, font_size_offset: number, manual_font_size: number \| null }` |

均为整节 upsert，`section` 使用设计冻结名；每节的键域/值域校验仍由 Core 作为权威，前端校验仅为可用性预检。

## 3. 测试证据（原始结果）

### 3.1 主命令（验收命令）

```text
PS> pnpm --dir apps/desktop/frontend test
...
 Test Files  37 passed (37)
      Tests  364 passed (364)
   Start at  20:32:43
   Duration  3.43s (transform 3.49s, setup 0ms, collect 36.45s, tests 7.33s, environment 5ms, prepare 8.34s)
[exit code 0]
```

完整原始输出：`verification/SETTINGS-OPEN-A-1/frontend-pnpm-test-raw.txt`

### 3.2 类型检查

```text
PS> cd apps/desktop/frontend; .\node_modules\.bin\tsc --noEmit
(no output)
[exit code 0]
```

原始输出（空）：`verification/SETTINGS-OPEN-A-1/frontend-tsc-raw.txt`

### 3.3 交叉验证（同一 vitest 套件，npm 通道）

```text
PS> cd apps/desktop/frontend; npm test
 Test Files  37 passed (37)
      Tests  364 passed (364)
   Start at  20:32:58
```

完整原始输出：`verification/SETTINGS-OPEN-A-1/frontend-npm-test-raw.txt`

### 3.4 基线对比

- 变更前基线：32 files / 327 tests 全绿。
- 变更后：37 files / 364 tests 全绿（+5 测试文件、+37 tests：四个面板 30 + client.sections 6 + SettingsPage 净 +1）。

## 4. 既有测试更新说明（非“绕过失败”）

| 测试 | 原断言 | 现断言 | 原因 |
|---|---|---|---|
| `SettingsPage.test.tsx` 分类 open 矩阵 | provider/network/translation 3 开，其余 9 关 | provider/network/ocr/translation/inpaint/typeset 6 开，其余 6 关 | 用户裁决 + 本批设计显式开放 4 个分区，属行为变化 |
| `SettingsPage.test.tsx` OCR/inpaint/typeset 禁用用例 | disabled + `未开放` + 占位框 | 可点击、渲染真实面板、无禁用占位 | 同上 |
| `SettingsPage.test.tsx` 翻译参数/上下文占位用例 | `settings-disabled-section-translation-context` 可见且禁用 | 同一位置渲染 `TranslationParamsPanel`，占位消失，SFX 面板保留 | 同上 |
| `SettingsPage.test.tsx` 键盘导航 | 3×ArrowDown 落在 translation | 同一断言保留，并补充“typeset 之后再 ArrowDown 仍停留（跳过 model_gpu）” | 分类集合变化后防止关闭分类被键盘进入 |
| `SettingsPage.test.tsx` ARIA | 仅断言禁用分类含 `未开放` | 追加：开放分类 `aria-label`/`title` 为 null、`aria-disabled=false`、文本不含 `未开放` | 任务要求“未开放”只保留给仍未开放分区 |
| `client.p15.test.ts` 结构守卫 | `saveSection` 必须 undefined | `saveSection` 为 function（命名 section API，逐节白名单在 Core）；`updateSection` 仍未定义 | 任务 1 明确新增 `saveSection`，属冻结行为变化；未放宽为任意 section 透传 |

未改动的其余既有测试（SFX、Provider、Network、Credential、SettingsPanel、errors、client.test 等）全部原样通过，未删除或弱化任何断言。

## 5. 环境说明（重要，非交付改动）

本机全局 pnpm 为 11.25.0。首次执行 `pnpm test` 时 pnpm 的依赖校验自动触发 `pnpm install`，
生成了**未跟踪**的 `apps/desktop/frontend/pnpm-lock.yaml` 与 `apps/desktop/frontend/pnpm-workspace.yaml`；
若缺少后者中的 `allowBuilds: esbuild: true` / `verifyDepsBeforeRun: false`，
`pnpm test` 会在依赖校验阶段以 `ERR_PNPM_IGNORED_BUILDS` 退出（与测试本身无关）。

- 这两个文件不在本任务交付范围（untracked，不会进入任何 commit），仅作为本机运行前置；
- 仓库原本使用 npm（跟踪的 `package-lock.json`），因此另给 `npm test` 的等价原始结果作为独立证据；
- 未新增/升级任何依赖，未修改 `package.json`。

## 6. 未执行 / 遗留项

| 项 | 状态 | 说明 |
|---|---|---|
| E2E/GUI 烟测（真实 Tauri 应用逐分区保存 + 重启复查 + 新 Run 生效） | NOT_RUN | 本 agent 运行环境无已构建桌面应用；需 Lead/集成阶段执行 |
| 关键截图 | NOT_RUN | 同上，无 GUI 会话 |
| Core 侧联调（写入校验、`style_defaults` 装配） | 依赖 `task-1`（另一个 agent） | 前端按冻结键集提交；Core `INVALID_REQUEST` 会经 `SettingsErrorBar` 显示 |
| `typeset.text_align` 旧值 `start` | 设计差异记录 | 设计值域为 left/center/right，而 Python `DEFAULT_TEXT_ALIGN = "start"`。前端把持久化的 `start` 显示为 `left`（同向可视结果），且永远不会提交 `start`；待 Core 白名单确认对旧值兼容 |
| 阅读方向（`reading`） | 按设计 §3.4 不开放 | typeset 分区内仅显示指引（书籍/章节属性），无全局控件、无假键 |
| `typeset.font_family` | 本批不开放 | 面板无该控件，未提交该键 |
| 保存后的“当前持久化值”展示 | 已实现 | 保存成功 → 重新 `settings_get` → 用 Core 返回投影渲染（非本地乐观回显） |

## 7. 合规声明

- 仅修改 `apps/desktop/frontend/src/settings/**`，并新增本报告与原始日志于 `verification/SETTINGS-OPEN-A-1/`；
  未改 `src/**`（Python/Core）、未改 Schema/migration、未改 Provider/Network/凭据/SFX 面板语义。
- 未新增依赖、未 `git commit` / `git push`。
- Core 侧并行修改（`src/bootstrap/**`、`src/infrastructure/**`、`tests/**` 等）均来自 `task-1` 的另一个 writer，
  不在本报告变更清单内。
