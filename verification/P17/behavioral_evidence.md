# P17 阅读器行为证据（Behavioral Evidence）

## 1. 范围与边界核验

- **本 Task 严格只实现设计基线 §4 阅读器页**，覆盖 **W18**（`GetReaderProjection`）、**W19**（`SaveReadingProgress`）、**W20**（`ReadingProgressChanged`），消费既有 **W2/W3** 与 **W5**（`resolve_page_resource` → 资源通道）。
- **导出面板（W21–W25）与 G20 reveal 归 P14 工作台**：本 Task 绝未实现、绝未复制该面板，代码库检索确认 `ExportDialog` / `StartExport` / `open_folder` 类符号在 `src/reader/**` 内为 0 命中。
- **只做前端修改**：全部实现集中在 `apps/desktop/frontend/src/reader/**` 与 `src/shell/AppShell.tsx`，未修改 Rust/Tauri 核心、Python Core、契约定义或依赖清单。

---

## 2. 逐条行为证据（AC2 / AC3）

### 2.1 进度恢复（resume vs beginning）
- **契约要求**：`GetReaderProjection` 的 `start_position="beginning"` 不得改动已保存进度；`"resume"` 恢复保存位置。
- **实现位置**：[`apps/desktop/frontend/src/reader/ReaderToolbar.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderToolbar.tsx) 与 [`apps/desktop/frontend/src/reader/ReaderPage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPage.tsx)。
- **测试证据**：`src/reader/ReaderPage.test.tsx` 单测 `"switches between resume and beginning start positions without mutating saved progress (AC2)"` 验证传入 `start_position="beginning"` 时向 host 发出正确请求，且 Rust 端 `reader_commands_reach_frozen_core_with_typed_rejections` 证明 `sqlite_unchanged=true`。

### 2.2 模式切换独立进度键（Original vs Translated）
- **契约要求**：`original` 和 `translated` 是独立进度键，切换模式重新投影。
- **实现位置**：[`apps/desktop/frontend/src/reader/ReaderPage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPage.tsx) `handleModeChange`。
- **测试证据**：`src/reader/ReaderPage.test.tsx` 验证切换至 `translated` 时，以独立模式 key 向 host 请求 `library_get_reader_projection` 并刷新对应进度。

### 2.3 页图经资源通道获取（W5）
- **契约要求**：页图只能经 `resolve_page_resource` 与 §10 资源通道获取；不得下发/持有任何文件系统路径。
- **实现位置**：[`apps/desktop/frontend/src/reader/ReaderPageImage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPageImage.tsx)。
- **测试证据**：`src/reader/ReaderPage.test.tsx` 单测 `"loads projection via library_get_reader_projection (W18) and renders pages via resource channel (W5, AC2)"` 验证 `issue_resource_url` 获取 opaque URL，分块获取字节转为 `blob:URL`，全流程无 OS 文件路径泄漏。

### 2.4 Webtoon 原图像素坐标换算
- **契约要求**：Webtoon 的 `scroll_offset_y` 使用**逻辑 Page 原图像素坐标**；视口进行显示坐标 ↔ 原图坐标双向映射。
- **实现位置**：[`apps/desktop/frontend/src/reader/WebtoonReaderView.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/WebtoonReaderView.tsx) `getScale` 与 `handleScroll`。
- **换算公式**：
  $$\text{scale} = \frac{\text{renderedWidth}}{\text{page.width\_px}}$$
  $$\text{source\_offset\_y} = \text{round}\left(\frac{\text{scrollTop}}{\text{scale}}\right)$$
- **测试证据**：`src/reader/ReaderPage.test.tsx` 单测 `"supports Webtoon vertical scrolling with logical Page original-image pixel coordinate mapping (AC2, M2-C1 §6.3)"` 验证滚动触发的保存参数 `scrollOffsetY` 属于合法非负数值，且初始进入根据 `initial_position.scroll_offset_y` 按比例还原视口滚动。

### 2.5 `SaveReadingProgress` 缺失 `elapsed_seconds_delta` 不重发
- **契约要求**：`SaveReadingProgress` 的 `elapsed_seconds_delta` 缺失即不发送；不重发已接受区间。
- **实现位置**：[`apps/desktop/frontend/src/reader/client.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/client.ts) `saveReadingProgress`。
- **测试证据**：`src/reader/client.test.ts` 单测 `"omits elapsed_seconds_delta when missing or undefined (AC2 contract red line)"` 严密断言 payload 中绝不出现该字段。

### 2.6 缺失译图以 null 呈现
- **契约要求**：缺失的译图以 `null` 呈现，显示原文并标注「未翻译」角标，不得以路径或伪造引用替代。
- **实现位置**：[`apps/desktop/frontend/src/reader/ReaderPageImage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPageImage.tsx)。
- **测试证据**：`src/reader/ReaderPage.test.tsx` 单测 `"presents missing translated artifact as null with fallback to original and '未翻译' badge"` 验证角标出现且安全回退原图通道。

### 2.7 事件纪律（AC3）
- **契约要求**：收到 `core:ReadingProgressChanged` 后**必须重查快照**，不得用事件 payload 直接驱动位置。
- **实现位置**：[`apps/desktop/frontend/src/reader/ReaderPage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPage.tsx) 订阅 `onReadingProgressChanged` 并在回调中仅触发 `fetchProjection`。
- **测试证据**：`src/reader/ReaderPage.test.tsx` 单测 `"satisfies AC3 Event Discipline: re-queries snapshot on core:ReadingProgressChanged without using event payload to drive position"` 验证收到事件后重新触发 host 查询，位置不因 payload 直接跳转。

---

## 3. 测试与验证总结

| 验证项 | 命令 / 方式 | 结果 | 产物证据 |
|---|---|---|---|
| 前端测试套件 | `npm --prefix apps/desktop/frontend test` | **19 passed (19), 193 passed (193)** | `verification/P17/vitest.log` |
| 前端生产构建 | `npm --prefix apps/desktop/frontend run build` | **EXIT 0 (541ms, 75 modules)** | `verification/P17/build.log` |
| Python Core 套件 | `pytest tests/core` | **407 passed, 1 warning (37.24s)** | `verification/P17/pytest.log` |
| Rust Source 套件 | `cargo test --skip packaged_sidecar_tests` | **95 passed, 0 failed, 1 ignored (0.92s)** | `verification/P17/cargo-source.log` |
| Rust Packaged 套件 | `cargo test packaged_sidecar_tests` | **12 passed, 0 failed, 0 ignored (20.29s)** | `verification/P17/cargo-packaged.log` |
| 边界审计 | 静态正则扫描与代码审阅 | **PASS (0 violations)** | `verification/P17/boundary_audit.txt` |
| **GUI e2e 测试** | Windows Headless WebView2 | **NOT_RUN（无头 Windows 无法取得 WebView2 窗口句柄 `0x80070578`，如实声明未运行，绝不以单测通过表述为 e2e 通过）** | 本说明文档 |
