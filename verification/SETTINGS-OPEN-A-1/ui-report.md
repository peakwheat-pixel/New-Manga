# SETTINGS-OPEN-A-1 前端实现报告（批次 A，含返修 r2）

- 团队任务：`task-2`（初版）、`task-4`（返修 r2）
- 实现 agent：`ui-settings-a`（DeepSeek Harness）
- 仓库 / 分支：`G:\CODEX\New Manga` / `main`（未 commit、未 push）
- 依据：[SETTINGS 分区 Schema 设计 §3](../doc/design/SETTINGS_SECTION_SCHEMAS.md)、[SETTINGS-OPEN-A-1 任务](../doc/tasks/SETTINGS-OPEN-A-1.md)、[独立 Review r1](review-r1.md)
- 实现范围：仅 `apps/desktop/frontend/src/settings/**` 与 `verification/SETTINGS-OPEN-A-1/**`
- 返修状态：review r1 的前端 finding **B2 / M1 / M2 / m2 / m5 已处理**（见 §2）；其余 finding（B1 等 Core 侧、M3/M4/m1/m3/m4/m6/n1/n2）不在本 agent 范围，见 §7。

## 1. 交付结论（r2）

- 设置页 `ocr` / `translate`（翻译参数/上下文）/ `inpaint` / `typeset` 四个分区开放；
  `translation` 分类保留 SFX 面板并加入翻译参数面板；`ocr` / `inpaint` / `typeset`
  内容区为真实可编辑面板，不再渲染 `DisabledSection`。
- 四个面板均实现：section 读取（`settings_get {section}`）、JSON null 的“未设置 + Core
  默认值”提示、前端值域校验、整节保存（`settings_update_section {section, values}`）、
  保存后重新读取回显、加载/保存错误走 `SettingsErrorBar`（关闭 §9 投影）、
  “对之后启动的任务生效”说明、保存中禁用与错误不丢草稿。
- r2 之后 `typeset` 的冻结面为 **10 键**（移除 `fill_color`，本批仍不含 `font_family`）；
  `text_align` 值域收窄为 `left | center`；关闭自动字号时必须填写手动字号（前后端一致约束）。
- 其余 6 个分区（model_gpu / task_concurrency / cache_revision / recycle_bin /
  backup_restore / plugins）保持禁用占位与 `未开放` 徽标；导航 `aria-label`/`title`
  的“未开放：等待 section schema 冻结”只保留给这 6 个分区。
- Lead 裁决同步：`translate.context_token_budget` 键名保持不变，前端按设计 §3.2 原样提交，
  未做任何改名或降级。
- 测试：`npm --prefix apps/desktop/frontend test` 全绿（37 files / 367 tests）；
  `tsc --noEmit` 无错误。

## 2. 返修 r2 记录（review r1 finding → 处理）

| finding | 处理 | 落点 / 证据 |
|---|---|---|
| **B2**（blocker）`typeset.fill_color` 全链路无消费者（假控件） | 前端彻底移除：`TypesetSettingsDraft` 字段、默认值、归一化、校验、payload、持久化值摘要、面板控件全部删除；测试断言页面不存在 `typeset-fill-color` 控件 | `sections.ts`（类型/默认/归一化/`validateTypesetSettingsDraft`/`typesetSettingsValues`/`describeTypesetSettings`）、`TypesetSettingsPanel.tsx`、`TypesetSettingsPanel.test.tsx`（“reads …”“sends manual_font_size=null …” 两条测试均显式断言无该控件/无该键）；保存 payload 键集测试改为 10 键 |
| **M2**（major）`text_align: right` 无渲染实现 | 值域收窄为 `left \| center`：类型、`TEXT_ALIGN_VALUES`、标签、校验文案、下拉选项同步；旧持久化 `start`/`right` 读取时折叠为 `left` 展示且永不写回；测试断言下拉只有 `left`/`center`，并新增“legacy start/right → left”用例 | `sections.ts`、`TypesetSettingsPanel.tsx`、`TypesetSettingsPanel.test.tsx` |
| **M1**（major）`auto_font_size=false` + `manual_font_size=null` 会让渲染失败 | 新增跨字段校验：关闭自动字号时 `manual_font_size` 必填（非空且 1–500），否则行内错误 + 禁止保存；`auto_font_size=true` 时留空合法；payload 仍整节 upsert 且 `manual_font_size: number \| null`；新增专门测试（关闭自动→清空→错误+禁用；填回合法值→错误消失+可保存） | `sections.ts::validateTypesetSettingsDraft`、`TypesetSettingsPanel.tsx`（行内错误/禁用态/hint）、`TypesetSettingsPanel.test.tsx`（M1 用例） |
| **m2**（minor）section 参数为任意 `string` | `getSection` / `saveSection` 参数收窄为冻结 union `EditableSettingsSection = "ocr" \| "translate" \| "inpaint" \| "typeset" \| "sfx"`；新增运行时镜像 `EDITABLE_SETTINGS_SECTIONS`；`useSettingsSection` 同类型；`client.p15.test.ts` 恢复结构守卫：运行时钉住 5 个节名 + 用 `@ts-expect-error` 保证“任意节名（如 `bogus_section`）是编译错误”（由验收命令中的 `tsc --noEmit` 强制执行；闭包不执行、无 wire 调用） | `client.ts`、`useSettingsSection.ts`、`client.p15.test.ts` |
| **m5**（minor）验收通道不可复现（pnpm 依赖校验） | 验收主命令改为 `npm --prefix apps/desktop/frontend test`（仓库跟踪 `package-lock.json`）；原始证据重跑并覆盖为 npm 通道输出；本机 pnpm 11 自动生成的两个未跟踪环境文件已删除；`frontend-pnpm-test-raw.txt` 仅作历史环境记录，不再作为验收证据 | 本报告 §5、`frontend-npm-test-raw.txt`、`frontend-tsc-raw.txt` |

未处理（超出本 agent 范围，留给 Lead/Core writer）：B1（`_merge_defaults` 优先级）、M3（冻结契约同步）、
M4（base commit pin）、m1（`manual_font_size` 值域设计对齐）、m3（Core 测试拒绝循环补 `translate`）、
m4（治理元数据）、m6（逐分区 GUI 烟测）、n1/n2（回读失败文案/损坏数据区分）。

## 3. 改动清单

### 3.1 本轮 r2 修改（相对 commit `87ae85a`）

| 文件 | 变更 |
|---|---|
| `apps/desktop/frontend/src/settings/sections.ts` | 移除 `fill_color`（类型/默认/归一化/校验/payload/描述）；`TextAlign` 收窄为 `left \| center`（标签/值域/文案）；新增 M1 跨字段校验；归一化把旧 `start`/`right` 折叠为 `left` |
| `apps/desktop/frontend/src/settings/TypesetSettingsPanel.tsx` | 移除“填充颜色”控件；对齐下拉只剩 left/center 并更新 hint；自动字号/手动字号 hint 说明跨字段约束；未设置文案去掉 fill_color |
| `apps/desktop/frontend/src/settings/TypesetSettingsPanel.test.tsx` | 更新读取/保存/未设置用例为 10 键；断言无 fill_color 控件、对齐仅 left/center；新增 legacy align 与 M1 跨字段用例；保存 payload 键集更新 |
| `apps/desktop/frontend/src/settings/client.ts` | 新增 `EditableSettingsSection` 冻结 union 与运行时镜像 `EDITABLE_SETTINGS_SECTIONS`；`getSection` / `saveSection` 参数收窄 |
| `apps/desktop/frontend/src/settings/useSettingsSection.ts` | `section` 选项类型改用 `EditableSettingsSection` |
| `apps/desktop/frontend/src/settings/client.p15.test.ts` | 结构守卫恢复为“冻结 union + 任意节名编译错误”的等价断言 |
| `verification/SETTINGS-OPEN-A-1/ui-report.md` / `frontend-npm-test-raw.txt` / `frontend-tsc-raw.txt` | 本报告与 r2 重跑原始证据 |

### 3.2 初版交付文件（commit `87ae85a` 已包含，r2 后仍有效）

| 文件 | 内容 |
|---|---|
| `settings/client.ts` | 通用 `getSection<T>` / `saveSection`（r2 收窄 union），复用 `settings_get` / `settings_update_section` 与 `SettingsClientError` 错误映射 |
| `settings/sections.ts` | 批次 A 四节单一事实源（section 名、值域、Core 默认值、归一化、校验、payload、摘要） |
| `settings/useSettingsSection.ts` | 四面板共享生命周期（加载/重试/保存/保存后重读/错误投影） |
| `settings/SectionPanelFrame.tsx` | 共享面板外壳（卡片、骨架、错误条、未设置提示、保存态、“对之后启动的任务生效”说明、当前持久化值） |
| `settings/SectionField.tsx` | 共享字段行 + 输入样式 + `onChange`/`onInput` 双通道写草稿 |
| `settings/OcrSettingsPanel.tsx` | `ocr.script` / `ocr.direction` |
| `settings/TranslationParamsPanel.tsx` | `translate.context_pages`（1–5，默认 1）/ `context_token_budget`（200–8000，默认 2000） |
| `settings/InpaintSettingsPanel.tsx` | `preferred_quality` / `background_complexity` / `dilate_radius`（0–10）/ `erode_radius`（0–10） |
| `settings/TypesetSettingsPanel.tsx` | typeset 可编辑键（r2 后 10 键） |
| `settings/SettingsPage.tsx` | 四个分类开放 + 翻译分类双面板 + 阅读方向指引说明 |
| `settings/SettingsPage.test.tsx` | 6 开/6 关矩阵、开放面板渲染、禁用分区断言、键盘/ARIA 更新 |
| `settings/*Panel.test.tsx`、`settings/client.sections.test.ts` | 各面板与公共 client 的挂载级测试 |

### 3.3 关键 wire 契约（面板实际提交）

| 节 | 提交值 |
|---|---|
| `ocr` | `{ script, direction }` |
| `translate` | `{ context_pages: number, context_token_budget: number }` |
| `inpaint` | `{ preferred_quality, background_complexity, dilate_radius: number, erode_radius: number }` |
| `typeset`（r2 后） | `{ text_color, stroke_enabled, stroke_color, stroke_width: number, line_spacing: number, text_align: "left" \| "center", text_direction, auto_font_size, font_size_offset: number, manual_font_size: number \| null }` |

均为整节 upsert，`section` 使用设计冻结名且被 TS union 约束；每节的键域/值域校验仍由 Core 作为权威。

## 4. 类型/值域约束（前端侧）

| 键 | 前端约束 |
|---|---|
| `ocr.script` | `japanese \| korean \| chinese \| latin` |
| `ocr.direction` | `horizontal \| vertical` |
| `translate.context_pages` | 整数 1–5 |
| `translate.context_token_budget` | 整数 200–8000 |
| `inpaint.preferred_quality` | `fast \| balanced \| quality` |
| `inpaint.background_complexity` | `low \| medium \| high` |
| `inpaint.dilate_radius` / `erode_radius` | 整数 0–10 |
| `typeset.text_color` / `stroke_color` | `#RRGGBB`（`<input type="color">` + 文本回显） |
| `typeset.stroke_width` | 0–20 |
| `typeset.line_spacing` | 1.0–3.0 |
| `typeset.text_align` | `left \| center` |
| `typeset.text_direction` | `auto \| horizontal \| vertical` |
| `typeset.font_size_offset` | 整数 -5–+5 |
| `typeset.manual_font_size` | 可空；非空时 1–500；`auto_font_size=false` 时**必填**（M1） |
| `typeset.fill_color` | **已移除**（B2；前端不显示、不读取、不提交） |
| `typeset.font_family` | 本批不开放（无控件、不提交） |

## 5. 测试证据（原始结果，r2 重跑）

### 5.1 验收主命令（npm 通道，仓库跟踪 package-lock）

```text
PS> npm --prefix apps/desktop/frontend test
...
 Test Files  37 passed (37)
      Tests  367 passed (367)
   Start at  21:16:02
   Duration  3.68s (transform 3.38s, setup 0ms, collect 38.44s, tests 7.80s, environment 6ms, prepare 8.99s)
[exit code 0]
```

完整原始输出：`verification/SETTINGS-OPEN-A-1/frontend-npm-test-raw.txt`

- 初版基线：32 files / 327 tests 全绿；r1 交付：364 tests；r2：**367 tests**（+3：M1 跨字段、legacy text_align、section union 结构守卫）。
- settings 子集：14 files / 112 tests 全绿。

### 5.2 类型检查（同时是 m2 类型级守卫的执行者）

```text
PS> cd apps/desktop/frontend; .\node_modules\.bin\tsc --noEmit
(no output)
[exit code 0]
```

原始输出（空）：`verification/SETTINGS-OPEN-A-1/frontend-tsc-raw.txt`
`client.p15.test.ts` 中两条 `@ts-expect-error` 只有在该参数仍是 `string` 时才会变成“未使用指令”，
因此 `tsc` 通过即证明“任意节名调用”是编译错误。

### 5.3 pnpm 通道（历史记录，不作为验收证据）

`frontend-pnpm-test-raw.txt` 记录的是 r1 期间本机 pnpm 11.25.0 的结果；在干净 commit 上
`pnpm --dir apps/desktop/frontend test` 会因 `ERR_PNPM_IGNORED_BUILDS`（esbuild build script 未批准）
在依赖校验阶段失败，属于环境前置而非代码失败。按 m5 裁决，验收主命令改为 npm 通道；
本机 pnpm 自动生成的 `apps/desktop/frontend/pnpm-lock.yaml`、`pnpm-workspace.yaml`（未跟踪）已删除。

## 6. 既有测试更新说明（非“绕过失败”）

| 测试 | 更新 | 原因 |
|---|---|---|
| `SettingsPage.test.tsx` 分类 open 矩阵 | provider/network/ocr/translation/inpaint/typeset 6 开，其余 6 关 | 用户裁决 + 批次 A 设计开放 |
| `SettingsPage.test.tsx` OCR/inpaint/typeset 禁用用例 | 改为“可点击 + 渲染真实面板 + 无禁用占位” | 同上 |
| `SettingsPage.test.tsx` 翻译参数占位用例 | 改为渲染 `TranslationParamsPanel`，SFX 面板保留 | 同上 |
| `SettingsPage.test.tsx` 键盘导航 | 保留 3×ArrowDown → translation，并补充 typeset 之后 ArrowDown 仍停留（跳过 model_gpu） | 分类集合变化后防止关闭分类被键盘进入 |
| `SettingsPage.test.tsx` ARIA | 开放分类 `aria-label`/`title` 为 null、`aria-disabled=false`、文本不含“未开放” | “未开放”只保留给仍未开放分区 |
| `client.p15.test.ts` 结构守卫 | 初版：`saveSection` function；r2：冻结 union 运行时钉住 + 任意节名编译错误（`@ts-expect-error`） | 新增 section API 后恢复等价的结构约束（review m2） |
| `TypesetSettingsPanel.test.tsx` | 10 键读写、无 fill_color、left/center、M1 跨字段 | review r1 B2/M1/M2 |

未改动其余既有测试（SFX、Provider、Network、Credential、SettingsPanel、errors、client.test 等），全部原样通过，未删除或弱化无关断言。

## 7. 未执行 / 遗留项

| 项 | 状态 | 说明 |
|---|---|---|
| E2E/GUI 烟测（逐分区保存 + 重启复查 + typeset 渲染效果） | NOT_RUN（本 agent） | 需集成阶段在真实 Tauri 应用执行；review r1 m6 指出的覆盖缺口仍在 |
| 关键截图 | NOT_RUN | 同上 |
| B1 `_merge_defaults` 优先级 | 非本 agent 范围 | Core writer / Lead；前端仅按冻结键集提交 |
| M3 冻结契约同步、M4 base commit pin | 非本 agent 范围 | Lead/Codex 在集成前处理 |
| M1 的 Core 侧跨字段拒绝（`auto_font_size=false` 且 manual 为空 → INVALID_REQUEST） | 前端已做 UI 约束；Core 侧由 Core writer 对齐 | 前端校验先拦截，但 Core 白名单仍应拒绝该组合（review r1 建议） |
| B2/M2 的设计文档与 Core 白名单同步（`fill_color` 移除、`right` 收窄） | 待 Lead/Core writer | 设计 §3.4 仍列 `fill_color`/`right`；本 agent 无权改 `doc/**`/`src/**` |
| m1 `manual_font_size` 值域（设计 `>0` vs 实现 1–500） | 未处理（review 未要求本 agent 修） | 需设计/Core/UI 三处统一；当前 UI 与 Core 实现一致（1–500） |
| n1 `getSection` 非对象载荷静默当 null；n2 保存成功但回读失败的文案 | 未处理（review 未要求本 agent 修，属 nit） | 可后续优化 |
| `typeset.text_align` 旧值兼容 | 已处理 | `start`/`right` 读取折叠为 `left`，永不写回 |

## 8. 合规声明

- 仅修改 `apps/desktop/frontend/src/settings/**`，并更新 `verification/SETTINGS-OPEN-A-1/**` 证据；
  未改 `src/**`（Python/Core）、未改 `doc/**`、未改 Schema/migration、未改 Provider/Network/凭据/SFX 面板语义。
- 未新增依赖、未 `git commit` / `git push`。
- Core 侧并行修改（`src/bootstrap/**`、`src/infrastructure/**`、`tests/**` 等）属于其它 writer，
  不在本报告变更清单内。
