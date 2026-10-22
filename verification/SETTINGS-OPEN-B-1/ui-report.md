# SETTINGS-OPEN-B-1 前端实现报告（批次 B-1：模型/GPU + 任务/并发）

- 团队任务：`task-6`
- 实现 agent：`ui-settings-b1`（DeepSeek Harness）
- 仓库 / 分支：`G:\CODEX\New Manga` / `main`（base HEAD `da3b781`，未 commit、未 push）
- 依据：[SETTINGS 分区 Schema 设计 §4.1–§4.2](../../doc/design/SETTINGS_SECTION_SCHEMAS.md)、[SETTINGS-OPEN-B-1 任务](../../doc/tasks/SETTINGS-OPEN-B-1.md)、批次 A 已批准实现（`apps/desktop/frontend/src/settings/**`）
- 实现范围：仅 `apps/desktop/frontend/src/settings/**` 与 `verification/SETTINGS-OPEN-B-1/**`
- 依赖：批次 A 的共享外壳（`client.ts` 通用 section API、`sections.ts` 单一事实源、`useSettingsSection`、`SectionPanelFrame`、`SectionField`）原样复用，未改动其语义；Core 侧两消费点由 `core-settings-b1`（task-5）并行实现。

## 1. 交付结论

- `SettingsPage` 的 **模型/GPU**（`model_gpu`）与 **任务/并发**（`task_concurrency`）两个分类改为 `open: true`，内容区渲染真实可编辑面板，不再渲染 `DisabledSection`。
- 新增两个面板，均完整复用批次 A 外壳的加载 / 重试 / 未设置（JSON null）/ 保存 / 保存后重读 / 关闭 §9 错误投影 / “对之后启动的任务生效”说明 / 保存中禁用 / 失败不丢草稿：
  - `ModelGpuSettingsPanel`：`device_preference` 下拉（`auto | cpu | gpu`，默认 `auto`）、`allow_cpu_fallback` 开关（默认 `true`）；只读说明“设备能力由 Provider 运行时探测”与“GPU 并发策略 / 模型下载不在本批”。
  - `TasksSettingsPanel`：`retry_max_attempts` 数字输入（int 1–3，默认 3）、`retry_backoff_seconds` 数字输入（float 0.1–30，默认 1.0）；只读说明“任务串行执行（并发数不开放）”，不提供任何并发数控件（§2.4 不伪造）。
- **8 开 / 4 关**：provider、network、ocr、translation、inpaint、typeset、model_gpu、task_concurrency 开放；仅 `cache_revision` / `recycle_bin` / `backup_restore` / `plugins` 保持禁用占位与 `未开放` 徽标；`DISABLED_SECTION_TEST_IDS` 只保留这四项。
- `client.ts`：`EditableSettingsSection` union 与运行时镜像 `EDITABLE_SETTINGS_SECTIONS` 增加 `"model_gpu"`、`"tasks"`（`getSection` / `saveSection` 同步）；其余 section 仍为编译期错误。
- 测试：`npm --prefix apps/desktop/frontend test` 全绿（**39 files / 387 tests**，exit 0）；`tsc --noEmit` 无错误（exit 0）。

## 2. 改动清单

| 文件 | 变更 |
|---|---|
| `apps/desktop/frontend/src/settings/client.ts` | `EditableSettingsSection` 增加 `"model_gpu" \| "tasks"`；`EDITABLE_SETTINGS_SECTIONS` 同步为 7 项；注释同步（union 仍是唯一可表达的节名集合） |
| `apps/desktop/frontend/src/settings/sections.ts` | 新增 §4.1 `model_gpu` 与 §4.2 `tasks`：section 名、值域常量/标签、Core 默认值、`normalize*`、`validate*`、`*Values`（payload）、`describe*`（当前持久化值摘要） |
| `apps/desktop/frontend/src/settings/ModelGpuSettingsPanel.tsx` | **新建**：`device_preference` 下拉 + `allow_cpu_fallback` 开关 + 两条只读说明；保存/错误/生效说明走 `SectionPanelFrame` |
| `apps/desktop/frontend/src/settings/TasksSettingsPanel.tsx` | **新建**：`retry_max_attempts` / `retry_backoff_seconds` 数字输入（范围校验）+ 串行执行只读说明；保存/错误/生效说明走 `SectionPanelFrame` |
| `apps/desktop/frontend/src/settings/SettingsPage.tsx` | 两分类 `open: true`；内容区渲染两个新面板；`DISABLED_SECTION_TEST_IDS` 收敛为 4 项；页头注释同步 |
| `apps/desktop/frontend/src/settings/ModelGpuSettingsPanel.test.tsx` | **新建**：加载 / 读取持久化值 / JSON null 未设置 / 越域持久化值折叠默认 / 值域 / 保存 payload + 重读 / 加载错误投影 / 保存失败保留草稿（8 tests） |
| `apps/desktop/frontend/src/settings/TasksSettingsPanel.test.tsx` | **新建**：加载 / 读取 / JSON null 未设置 / 保存 payload + 重读 / 两键范围校验 / 非整数拒绝 / 边界值 / 加载错误投影 / 保存失败保留草稿（10 tests） |
| `apps/desktop/frontend/src/settings/SettingsPage.test.tsx` | 分类矩阵更新为 8 开 4 关；新增 Batch B-1 面板渲染用例；键盘导航改为“依次进入 model_gpu、task_concurrency，关闭分类不被进入”；删除两条已开放分类的禁用断言，其余既有断言保留 |
| `apps/desktop/frontend/src/settings/client.p15.test.ts` | 结构守卫的运行时节名镜像与长度更新（5 → 7），断言 B-1 两节加入冻结 union |
| `apps/desktop/frontend/src/settings/client.sections.test.ts` | 新增一条通用 section 读写用例，覆盖 `model_gpu` / `tasks` 走同一 wire |
| `verification/SETTINGS-OPEN-B-1/ui-report.md` 等 | 本报告与原始证据文件（`frontend-npm-test-raw.txt`、`frontend-targeted-test-raw.txt`、`frontend-tsc-raw.txt`） |

未改动：`useSettingsSection.ts`、`SectionPanelFrame.tsx`、`SectionField.tsx`、批次 A 四面板及其测试、SFX/Provider/Network/凭据面板语义。

## 3. 两节契约（面板实际提交）

| 节 | 提交值（整节 upsert） |
|---|---|
| `model_gpu` | `{ device_preference: "auto" \| "cpu" \| "gpu", allow_cpu_fallback: boolean }` |
| `tasks` | `{ retry_max_attempts: number, retry_backoff_seconds: number }` |

- 均为 `settings_update_section {section, values}`，`section` 使用设计冻结名且被 TS union 约束；键级白名单/值域校验仍由 Core 作为权威（非法值 → `INVALID_REQUEST`，前端只做提交前拦截）。
- 前端不读取、不显示、不提交 `gpu_concurrency`、模型下载/路径、设备状态等未冻结键；`tasks` 不含任何并发数键。

## 4. 类型 / 值域约束（前端侧）

| 键 | 前端约束 |
|---|---|
| `model_gpu.device_preference` | `auto \| cpu \| gpu`（下拉仅 3 项；越域持久化值归一化为 `auto`，永不写回猜测值） |
| `model_gpu.allow_cpu_fallback` | boolean 开关（默认开启；仅表达用户允许，Core 再与 Provider `supports_cpu_fallback` 相与） |
| `tasks.retry_max_attempts` | 整数 1–3（草稿存字符串，payload 为 number；非整数/越界在 UI 行内拦截并禁用保存） |
| `tasks.retry_backoff_seconds` | 数字 0.1–30（payload 为 number；越界在 UI 行内拦截并禁用保存） |

默认值完全取自设计 §4.1/§4.2：`auto` / `true` / `3` / `1.0`；未设置时仅用于展示，不会自动写库。

## 5. 测试证据（原始结果）

### 5.1 验收主命令

```text
PS> npm --prefix apps/desktop/frontend test
 Test Files  39 passed (39)
      Tests  387 passed (387)
   Start at  22:06:46
   Duration  3.38s (transform 3.37s, setup 0ms, collect 38.07s, tests 7.13s, environment 5ms, prepare 8.35s)
[exit code 0]
```

完整原始输出：`verification/SETTINGS-OPEN-B-1/frontend-npm-test-raw.txt`（stderr 中的 `act(...)` 警告为仓库既有测试环境噪声，HEAD 基线同样存在，不影响通过）。

- 基线（HEAD `da3b781`）：37 files / 367 tests；本次新增 2 个测试文件、净增 20 条测试（ModelGpu 8 + Tasks 10 + SettingsPage 净 +1 + client.sections +1），当前 **39 files / 387 tests** 全绿。

### 5.2 本 Task 相关子集

```text
PS> cd apps/desktop/frontend; .\node_modules\.bin\vitest run \
      src/settings/ModelGpuSettingsPanel.test.tsx \
      src/settings/TasksSettingsPanel.test.tsx \
      src/settings/SettingsPage.test.tsx \
      src/settings/client.p15.test.ts \
      src/settings/client.sections.test.ts
 ✓ src/settings/client.sections.test.ts (7 tests)
 ✓ src/settings/client.p15.test.ts (14 tests)
 ✓ src/settings/ModelGpuSettingsPanel.test.tsx (8 tests)
 ✓ src/settings/TasksSettingsPanel.test.tsx (10 tests)
 ✓ src/settings/SettingsPage.test.tsx (17 tests)
 Test Files  5 passed (5)
      Tests  56 passed (56)
[exit code 0]
```

原始输出：`verification/SETTINGS-OPEN-B-1/frontend-targeted-test-raw.txt`

### 5.3 类型检查

```text
PS> cd apps/desktop/frontend; .\node_modules\.bin\tsc --noEmit
(no output)
[exit code 0]
```

原始输出（空，仅退出码）：`verification/SETTINGS-OPEN-B-1/frontend-tsc-raw.txt`
`client.p15.test.ts` 的 `@ts-expect-error` 守卫仍生效：若 `section` 参数被放宽回 `string`，`tsc` 会因“未使用指令”失败。

## 6. 既有测试更新说明（非“绕过失败”）

| 测试 | 更新 | 原因 |
|---|---|---|
| `SettingsPage.test.tsx` 分类 open 矩阵 | 6 开/6 关 → **8 开/4 关**（新增 model_gpu、task_concurrency 为 true） | 本 Task 开放这两个分类 |
| `SettingsPage.test.tsx` 面板渲染用例 | 新增 `ModelGpuSettingsPanel` / `TasksSettingsPanel` 渲染、控件存在、只读说明存在、无禁用占位的断言 | AC4 |
| `SettingsPage.test.tsx` 键盘导航 | 保留 provider→network→ocr→translation 的 3×ArrowDown；typeset 之后 ArrowDown 现在进入 model_gpu → task_concurrency；再 ArrowDown 被钳制在最后一个开放分类，关闭分类永不被进入；新增 ArrowUp 不越界的守卫 | 开放分类集合变化后仍保证“键盘只跳过关闭分类” |
| `SettingsPage.test.tsx` 禁用分区用例 | 删除 model_gpu / task_concurrency 的禁用断言（已开放）；cache_revision 用例补充“点击不切换分类”；保留 recycle_bin / backup_restore / plugins 用例与占位 id 断言（键集收敛为 4 项） | 仅剩 4 个分区未开放 |
| `client.p15.test.ts` 结构守卫 | 运行时镜像断言 5 项 → 7 项、`toHaveLength(7)`，注释同步 | union 按设计扩展 |
| `client.sections.test.ts` | 新增 B-1 两节走通用 `getSection` / `saveSection` 的 wire 形状用例 | 覆盖 item 1 的“同步” |

未删除或弱化任何无关既有断言（批次 A 面板、SFX、Provider、Network、Credential、errors、client 等测试原样通过）。

## 7. 未执行 / 遗留项

| 项 | 状态 | 说明 |
|---|---|---|
| GUI 烟测（两分区保存 + 重启复查） | NOT_RUN（本 agent） | 需真实 Tauri 应用 + Python Core 集成；本 agent 无 GUI 运行环境，交由 Lead/集成阶段执行 |
| 关键截图 | NOT_RUN | 同上 |
| Core 侧消费点（`handlers` 构造 `RetryPolicy`、`heavy_runner` 设备偏好、`run_guarded`） | 非本 agent 范围 | 由 `core-settings-b1`（task-5）并行实现；本报告只覆盖前端 wire 形状与 UI 约束 |
| Core 白名单对 `model_gpu` / `tasks` 的键级校验 | 非本 agent 范围 | 前端提交前已做同样值域拦截，Core 仍为权威 |
| 独立 Review | 待指派 | 按项目规则由非实现者执行 |
| `doc/**`（设计/任务/STATUS/计划/契约）中的并行改动 | 非本 agent | 工作区中这些 doc 变更属于 Lead，不在本报告变更清单内 |

## 8. 合规声明

- 仅修改 `apps/desktop/frontend/src/settings/**` 并新增 `verification/SETTINGS-OPEN-B-1/**` 证据；未改 `src/**`（Python/Core）、未改 `doc/**`、未改 Schema/migration、未改 Provider/Network/凭据/SFX 面板语义。
- 未新增依赖（沿用既有 `package-lock.json` 与 npm 通道）、未 `git commit` / `git push` / `merge` / `rebase`。
- 未删除既有测试文件或无关断言；未使用 `test.skip` / `only` 等绕过手段。
