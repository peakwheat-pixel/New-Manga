# SETTINGS-OPEN-B-2 前端 UI 报告（task-8，缓存/Revision 清理面板）

- 任务：task-8 / SETTINGS-OPEN-B-2 AC3 + AC4（前端部分）
- 基线：`main` @ `7d19164f838607e68e2b6970bbbd57bee7bd5777`（工作区中 `doc/**` 与 `src/**` 的未提交改动属于其他并行 Agent；本 Task 未写这些路径）
- 角色：前端实现 agent（ui-settings-b2）
- 日期：2026-10-22
- 设计依据：`doc/design/SETTINGS_SECTION_SCHEMAS.md` §4.3；任务：`doc/tasks/SETTINGS-OPEN-B-2.md`
- Wire 对齐：2026-10-22 收到 wire-settings-b2（task-7）的最终 JSON 投影确认并按此实现；task-7 已完成（Core + Tauri 均已落地，见 `verification/SETTINGS-OPEN-B-2/wire-report.md` §2），本报告已按最终实现复核。
- 结论：前端实现与任务测试完成；wire 落地后复跑 `npm test`（41 files / 406 tests）与 `tsc --noEmit`（exit 0）仍全绿。GUI 烟测为 NOT_RUN——需要构建并运行 Tauri 应用，属于 AC5 集成验证（见 §7）。

## 1. 变更清单

| 文件 | 类型 | 变更 |
|---|---|---|
| `apps/desktop/frontend/src/settings/client.ts` | 修改 | +230 行：三个 cleanup 命令常量、`CleanupTarget/CleanupPreview/CleanupItem/CleanupOutcome` 类型、投影防御解析、`getCleanupPreview/runCleanup/retryPendingCleanups` 三个方法 |
| `apps/desktop/frontend/src/settings/CacheRevisionPanel.tsx` | 新增 | 342 行：缓存/Revision 操作面板（自动预览、清理、重试、结果/失败明细、只读说明、错误投影、防重复提交） |
| `apps/desktop/frontend/src/settings/SettingsPage.tsx` | 修改 | 30 行：`cache_revision` 分类 `open: true` 并渲染面板；`DISABLED_SECTION_TEST_IDS` 仅保留 `recycle_bin / backup_restore / plugins`（9 开 3 关）；注释同步 |
| `apps/desktop/frontend/src/settings/SettingsPage.test.tsx` | 修改 | 80 行：矩阵 9/3、键盘导航、B-2 面板打开断言、禁用占位 test id 集合更新 |
| `apps/desktop/frontend/src/settings/CacheRevisionPanel.test.tsx` | 新增 | 11 个用例：面板行为、ruled wire mapping、兼容 items 数组、两种错误投影 |
| `apps/desktop/frontend/src/settings/client.cleanup.test.ts` | 新增 | 8 个用例：命令名、无参数调用、三种投影解析与错误映射 |

未改动：`src/**`（Python）、`apps/desktop/src-tauri/**`、`doc/**`；未加依赖；未 commit/push。

## 2. Wire 契约（前端侧，已与 task-7 确认）

Tauri 命令名固定、全部无参数（`invoke(command)` 只传命令名，production-only，返回 Core 投影原样透传）：

- `cleanup_preview`：
  ```json
  { "targets": [ {"relative_path": "cache/webtoon-tiles/tile-....png", "size_bytes": 123} ],
    "total_bytes": 1234, "pending_cleanups": 0 }
  ```
  targets 恒为数组（可为空）；`total_bytes` / `pending_cleanups` 恒为数字；无嵌套 `preview` 字段。
- `cleanup_run` / `cleanup_retry_pending`：
  ```json
  { "items": { "<relative_path>": {"status": "ok|failed|skipped", "reason": ""} },
    "removed": 0, "failed": 0, "skipped": 0 }
  ```
  **`items` 是 object（path → {status,reason} mapping），不是数组**；计数为数字；空清理时 `items = {}`。
- 错误：无 cleanup 服务 → `CORE_UNAVAILABLE`（String code，与 `settings_get` 同错误通道 → invoke reject）；payload 非 object → `INVALID_REQUEST`；两者都不带本地路径。
- Tauri 侧核对（task-7 完成后）：`apps/desktop/src-tauri/src/main.rs` 的三个命令均为 `#[tauri::command]` 且只接收 `State<AppState>`（**无 payload**），返回 `serde_json::Value` / String code；`CLEANUP_PRODUCTION_ONLY_COMMANDS`、`command_allowlist`、`generate_handler![]`、`capabilities/m2rc1-commands.json`、`build.rs` 清单均已同步（与本前端命令常量逐字一致）。Core 侧 `handle_cleanup_preview()` 返回 `targets/total_bytes/pending_cleanups`，`_cleanup_outcome_projection()` 返回 `items`(mapping)/`removed`/`failed`/`skipped`，与上述 JSON 一致。

Client 返回类型（UI 内部统一成数组 + 计数，便于渲染）：

```ts
interface CleanupTarget { relative_path: string; size_bytes: number }
interface CleanupPreview { targets: CleanupTarget[]; total_bytes: number; pending_cleanups: number }
interface CleanupItem { relative_path: string; status: "ok" | "failed" | "skipped"; detail?: string }
interface CleanupOutcome { items: CleanupItem[]; removed: number; failed: number; skipped: number }
```

### 2.1 解析防御（与 Python 事实源的差异）

实际读取 `src/application/maintenance/cleanup.py` 后确认（与任务文字“to_dict 已存在”有偏差，故做多形状兼容）：

- `CleanupPreview` 原本**没有 `to_dict()`**；task-7 已补（`targets/total_bytes`），Core 侧 `handle_cleanup_preview()` 再补 `result["pending_cleanups"] = service.pending_cleanup_count()`（已核对 `src/bootstrap/core_service.py:1776-1786`），最终 shape 与 §2 一致。
- `CleanupOutcome.to_dict()`（cleanup.py:92）当前返回 **mapping** `{relative_path: {"status", "reason"}}`，不含顶层 `items/removed/failed/skipped`；Core 侧 `_cleanup_outcome_projection()` 把它包在 `items` 下并附三个计数（已核对 `src/bootstrap/core_service.py:483-493`），即 §2 的最终投影。
- 前端接受三种形状，统一归一化：
  1. ruled task-7：`{items:{path:{status,reason}}, removed, failed, skipped}`；
  2. 旧 mapping：`{path:{status,reason}}`（计数由 status 推导）；
  3. 兼容 items 数组：`{items:[{relative_path,status,detail?}], ...}`；
  另容错 `{preview:{...}}` / `{outcome:{...}}` 嵌套、`total_bytes` 缺失（按 targets 求和）、`pending_cleanups` 为数组（取长度）或 `{count}`。
- 防御规则：未知/缺失 `status` fail-closed 为 `failed`（绝不把未确认的删除显示成成功）；计数优先用服务端数字，缺省由 items 推导；非法条目丢弃；非对象 payload 折叠为空预览/零结果，不抛异常。
- 错误映射：沿用 `SettingsClientError` + `toClientError`（fallback `SETTINGS_UNAVAILABLE`）；面板经 `projectSettingsError(code, "settings_resolution")` 走既有 §9 封闭投影（未新增 phase 枚举值），DOM 只出现固定中文短句，不回显原始 code/路径/异常文本。

## 3. 面板行为与 test id

`CacheRevisionPanel`（`data-testid="cache-revision-panel"`）：

- 挂载自动 `cleanup_preview`；加载中骨架 `cache-revision-panel-loading`；加载失败 `cache-revision-panel-load-error`（§9 短句 + 重试按钮 `...-load-error-retry`）。
- 预览区：`cache-revision-panel-summary` 显示“可清理 N 个文件 / X MB”（B/KB/MB 自适应，1 位小数）；`cache-revision-panel-pending` 显示“挂起项：N 个”；空缓存显示 `cache-revision-panel-empty`“无可清理文件”。
- 操作按钮：`cache-revision-panel-cleanup-btn`（“清理缓存”）与 `cache-revision-panel-retry-btn`（“重试挂起项”）。
  - 请求中 `disabled` + `aria-disabled`，文案变为“清理中…/重试中…”，`cache-revision-panel-busy-state` 给出进行中文案；`busyRef` 同步防重复（React 状态未刷新时的第二次点击也无效）。
  - 空缓存禁用清理；`pending_cleanups === 0` 时禁用重试（不提供假操作）。
- 结果区：`cache-revision-panel-result`（`data-operation="cleanup|retry"`、`data-removed/failed/skipped`）显示“成功 A 个 · 失败 B 个 · 跳过 C 个”；失败项 `cache-revision-panel-failures` → 每项 `cache-revision-panel-failure`（路径 + `detail` 明细）。成功后自动重读预览（静默刷新，刷新失败不覆盖本次操作结果）。
- 操作失败：`cache-revision-panel-action-error`（§9 闭投影），当动作为 retry 时提供重试按钮重新执行上次操作；按钮恢复可用。
- 只读说明：`cache-revision-panel-policy-note` 明确“Revision 保留策略与自动清理未开放——当前没有调度器与存储消费点，因此不提供自动清理天数或保留策略控件”（无假开关）。
- 复用现有外壳风格与 `tokens`（卡片/标题/次要文本/按钮/错误条 `SettingsErrorBar`），未新增依赖、未新增全局样式。

## 4. SettingsPage 分类矩阵

- `cache_revision`: `open: true`，内容区 `settings-content-cache-revision` 渲染 `CacheRevisionPanel`。
- `DISABLED_SECTION_TEST_IDS` 仅剩 `recycleBin / backupRestore / plugins` → **9 开 / 3 关**。
- 键盘导航：`task_concurrency` 之后的下一个开放分类为 `cache_revision`，再向下 clamp 在 `cache_revision`，不会进入回收站等关闭分类。
- 保留的既有断言：12 分类冻结顺序与标签、200px nav、内容区切换不重挂载、未开放分类徽标/aria/placeholder、Batch A/B-1 面板打开断言均未删除。

## 5. 任务测试原始结果

### 5.1 前端全量（验收命令）

命令（仓库根目录）：`npm --prefix apps/desktop/frontend test`

```text
 Test Files  41 passed (41)
      Tests  406 passed (406)
   Start at  23:04:33
   Duration  3.43s (transform 3.30s, setup 0ms, collect 41.69s, tests 7.91s, environment 6ms, prepare 8.62s)
exit code: 0
```

原始日志：`verification/SETTINGS-OPEN-B-2/ui-test-frontend.log`

### 5.2 本 Task 定向用例

命令（仓库根目录）：
`npm --prefix apps/desktop/frontend test -- src/settings/CacheRevisionPanel.test.tsx src/settings/client.cleanup.test.ts src/settings/SettingsPage.test.tsx`

```text
 ✓ src/settings/client.cleanup.test.ts (8 tests) 5ms
 ✓ src/settings/CacheRevisionPanel.test.tsx (11 tests) 136ms
 ✓ src/settings/SettingsPage.test.tsx (17 tests) 268ms
 Test Files  3 passed (3)
      Tests  36 passed (36)
   Duration  1.24s (transform 219ms, setup 0ms, collect 1.15s, tests 409ms, environment 0ms, prepare 358ms)
exit code: 0
```

原始日志：`verification/SETTINGS-OPEN-B-2/ui-test-targeted.log`

### 5.3 类型检查（验收命令）

命令（`apps/desktop/frontend`）：`.\node_modules\.bin\tsc --noEmit`

```text
（无诊断输出）
tsc --noEmit exit code: 0
```

原始日志：`verification/SETTINGS-OPEN-B-2/ui-tsc.log`

### 5.4 覆盖矩阵（AC3/AC4 前端）

| 场景 | 用例 |
|---|---|
| 预览空 | `renders 无可清理文件 and disables both operations for an empty cache`；SettingsPage B-2 分类测试 |
| 预览有数据（数量/字节/挂起项） | `auto-previews via cleanup_preview ...` |
| 清理成功计数 + 操作后重读预览 | `runs cleanup, shows removed/failed/skipped counts, and re-reads the preview` |
| 失败明细（ruled wire：items 为 mapping） | `renders the failure detail for the ruled wire shape (items as a mapping)` |
| 兼容 items 数组投影 | `also accepts an items ARRAY projection (forward-compatible) ...` |
| Python `to_dict()` mapping 投影 | `accepts the Python CleanupOutcome.to_dict() mapping form ...`（面板）+ `client.cleanup.test.ts` 同场景 |
| 重试挂起项 | `retries the persisted pending ledger via cleanup_retry_pending` |
| 按钮提交中禁用 + 防重复 | `disables both buttons while an operation is in flight and ignores a second click` |
| 操作错误 §9 投影 + 再重试 | `a failed operation shows the closed §9 projection and allows a real retry` |
| 加载错误 + 重试 | `a failed preview shows the safe error and retry re-reads the preview` |
| 键盘导航/矩阵 9/3/占位 id | `SettingsPage.test.tsx` 更新后的矩阵、导航、占位集合断言 |

## 6. 约束核对

- 未改 `src/**`（Python）、`apps/desktop/src-tauri/**`、`doc/**`（`git status` 中这些路径的改动均来自其他并行 Agent，本 Task 未写）。
- 未新增依赖、未改 `package.json`/lockfile。
- 未 commit / push / merge / rebase。
- 无假控件：自动清理天数、Revision 保留策略均未出现控件，仅只读说明。
- 未新增缓存删除路径：前端只调用固定三命令，实际删除语义完全在 `CleanupService`/安全前缀内。

## 7. 集成状态 / 未完成项（重要）

1. **Wire 已全部落地**：task-7 已完成（wire-report 已写）。`src/application/maintenance/cleanup.py`（`CleanupPreview.to_dict()`）、`src/bootstrap/core_assembly.py`（组装 `CleanupService`）、`src/bootstrap/core_service.py`（`_CLEANUP_COMMANDS`、`handle_cleanup_preview/run/retry_pending`、`_cleanup_outcome_projection`、`CORE_UNAVAILABLE` 映射）与 `apps/desktop/src-tauri/**`（三命令、production-only 清单、allowlist、capabilities、build.rs）均已出现并与本报告的 §2 JSON 一致（本报告生成后已复核）。前端命令名/无参调用以 `client.cleanup.test.ts` 的 mock 断言固定，Tauri 侧逐字一致。
2. **`pending_cleanups` 已确认**：`handle_cleanup_preview()` 返回 `preview().to_dict()` 并追加 `pending_cleanups = pending_cleanup_count()`；前端解析与 §2 一致。
3. **GUI 烟测 NOT_RUN**：打开缓存分类 → 预览 → 清理 → 重启复查 pending 需要构建并运行 Tauri 应用（AC5），属集成验证，不在本前端 Task 内执行；建议 Lead 在集成阶段执行。
4. 环境事实记录：`CleanupPreview.to_dict()` 原先不存在、`CleanupOutcome.to_dict()` 为 mapping 形式（cleanup.py:61/92），与任务文字描述不一致；本实现已多形状兼容并在 §2.1 留证，供 Lead/wire writer 收口。

## 8. 推荐下一步

- Lead 集成阶段：构建并运行 Tauri 应用做一次 AC5 GUI 烟测（打开缓存分类 → 预览 → 清理 → 重启复查 pending 一致），确认最终 JSON 与 §2 无差异。预期无需返修；若 Tauri 透传字段与约定不符，仅需调整 `client.ts` 的 normalize 函数（面板与 test id 不变），并补一条真实 payload 的回归断言。
