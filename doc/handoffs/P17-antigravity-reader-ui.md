---
task_id: P17
author: antigravity
recipient: Codex
base_commit: 536962909963eaeeff7e94ff511f76f927652cd6
delivery_head: pending
status: ready_for_review
---

# Handoff：P17 阅读器 Reader UI 实现

## 交付结果

依据 [AD001_FOUR_PAGE_UI_BASELINE.md](../design/AD001_FOUR_PAGE_UI_BASELINE.md) **§4 阅读器**与 [P17 Task 需求](../tasks/P17.md)，本项目已完成四页中第四页——阅读器 Reader 的完整前端实现与自动化测试覆盖。

主要交付内容如下：

1. **类型与客户端适配（W18 / W19）**：
   - [`apps/desktop/frontend/src/reader/types.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/types.ts)：定义 `ReaderProjection`、`ReaderPageProjection`、`ReadingProgressSnapshot` 等符合 M2-C1 rev 2.1 §6.3 的完整 DTO 类型。
   - [`apps/desktop/frontend/src/reader/client.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/client.ts)：实现 `library_get_reader_projection` 与 `library_save_reading_progress` 的安全调用。严格遵守 AC2 语义红线：`elapsed_seconds_delta` 缺失即不发送（不重发已接受区间），支持 Webtoon 源图像素坐标换算。
   - [`apps/desktop/frontend/src/reader/client.test.ts`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/client.test.ts)：6/6 单测全绿。

2. **工具栏与导航控制（§4.2, §4.3 ReaderToolbar）**：
   - [`apps/desktop/frontend/src/reader/ReaderToolbar.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderToolbar.tsx)：48px 固定高工具栏，包含章节标题、返回书架按钮、Original/Translated 模式切换、位置指示器（当前页/总页数或 Webtoon 进度百分比）、跳页/翻页控件、起始位置（继续 resume / 从头开始 beginning）选择以及进度保存状态指示。

3. **分页与条漫视口（§4.3 PagedReaderView / WebtoonReaderView）**：
   - [`apps/desktop/frontend/src/reader/PagedReaderView.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/PagedReaderView.tsx)：支持 `rtl`（从右向左，下一页在左）与 `ltr`（从左向右，下一页在右）方向语义，提供左右两侧点击翻页区域。
   - [`apps/desktop/frontend/src/reader/WebtoonReaderView.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/WebtoonReaderView.tsx)：宽度自适应垂直滚动条漫，一张长图恰一个逻辑 Page；通过 $\text{scale} = \text{renderedWidth} / \text{page.width\_px}$ 实现视口滚动坐标 ↔ 逻辑 Page 原图像素坐标的双向换算。

4. **页图安全加载与状态角标（W5 / §10 资源通道）**：
   - [`apps/desktop/frontend/src/reader/ReaderPageImage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPageImage.tsx)：页图严格经 `resolve_page_resource` 与 §10 资源通道（`ResourceChannelClient`：`issue_resource_url` → 分块拉取 → `Blob` → `createObjectURL`）获取，全程绝不下发/持有任何 OS 文件系统路径。
   - **缺失译图安全回退**：当 `translated.resource_ref === null` 时，安全回退展示原文，并显式标注「未翻译 (回退原文)」角标，绝不以本地路径或伪造引用替代。
   - **过期译文指示**：当 `rendered_from_revision_id !== current_source_revision_id` 时，显式标注「译文可能过期」角标。
   - 包含骨架加载指示与分块加载错误重试机制。

5. **空状态与主容器联动（AC1, AC2, AC3, §4.4, §4.6）**：
   - [`apps/desktop/frontend/src/reader/ReaderEmptyState.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderEmptyState.tsx)：无章节上下文与空页面指引。
   - [`apps/desktop/frontend/src/reader/ReaderPage.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPage.tsx)：实现五态（loading / empty / error / disabled / progress）控制；Original/Translated 独立保存键；节流（800ms debounce）进度保存；满足 AC3 事件消费纪律（监听 `core:ReadingProgressChanged` 仅作为失效提示重新拉取 Core 快照，绝不用 payload 直接驱动位置）；支持全套键盘快捷键（`←/→`、`PageUp/PageDown`、`Home/End`、`O/T`、`Esc`）。
   - [`apps/desktop/frontend/src/shell/AppShell.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/shell/AppShell.tsx)：透传 `invoke` 到 `ReaderPage`。
   - [`apps/desktop/frontend/src/reader/ReaderPage.test.tsx`](file:///G:/CODEX/New%20Manga.workspace/worktrees/P17/apps/desktop/frontend/src/reader/ReaderPage.test.tsx)：10/10 单元与集成测试全绿。

6. **严格遵守范围边界**：
   - **绝未实现导出面板（W21–W25）与 G20 reveal**：已在代码库和单测中进行严格边界断言（`verification/P17/boundary_audit.txt` 确认 0 违规），导出面板与 reveal 专属 P14 工作台。

---

## 逐 AC 对照表

| AC | 要求摘要 | 状态 | 交付证据与说明 |
|---|---|---|---|
| **AC1** | 严格按 §4 实现（区域布局、组件分解、状态矩阵、交互清单、键盘焦点） | **PASS** | `src/reader/ReaderToolbar.tsx`, `PagedReaderView.tsx`, `WebtoonReaderView.tsx`, `ReaderPage.tsx`, `ReaderPage.test.tsx` |
| **AC2** | 契约语义逐条遵守（资源通道、无路径、beginning 不改进度、独立进度键、delta 缺失不发、Webtoon 像素坐标、缺失译图为 null） | **PASS** | `src/reader/client.ts`, `ReaderPageImage.tsx`, `WebtoonReaderView.tsx`, `src/reader/client.test.ts` (6 tests), `ReaderPage.test.tsx` (10 tests) |
| **AC3** | 事件消费纪律（收到 `core:ReadingProgressChanged` 必须重查快照，不得用 payload 直接驱动位置） | **PASS** | `src/reader/ReaderPage.tsx` 事件监听仅触发 `fetchProjection`，`ReaderPage.test.tsx` 专项单测验证重查行为 |
| **AC4** | 缺口禁用而非发明（导出面板与 G20 归 P14 不在 P17 出现，无 wire 的交互均安全封禁） | **PASS** | `verification/P17/boundary_audit.txt` (0 violations)，导出功能 0 引入 |
| **AC5** | 自动化测试与构建证据（npm test 全绿、npm run build 成功、tests/core 与 Rust 不回归、如实声明 GUI e2e 未运行） | **PASS** | Vitest 193/193 pass, Vite build exit 0, pytest 407/407 pass, cargo test source 95/95 pass, cargo packaged 12/12 pass；e2e 如实声明未运行 |
| **AC6** | 交付物固定（commit、Handoff、Canonical Evidence 磁盘字节 sha256、BL-15 规约） | **PASS** | 本 Handoff、`doc/tasks/P17.md`、`verification/P17/**` |

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物（真实磁盘 sha256） |
|---|---|---|---|---|
| 前端全量单测 | `npm --prefix apps/desktop/frontend test` | Node v22.14.0 / vitest 2.1.9 | **PASS**（19 files / 193 tests passed） | `verification/P17/vitest.log`<br>`82c5de3d9250037801508d50bb6d980a300b42ad386635aac29df5280d958777` |
| 前端生产构建 | `npm --prefix apps/desktop/frontend run build` | tsc + vite 5.4.21 | **PASS**（exit code 0, 75 modules, 541ms） | `verification/P17/build.log`<br>`8a573c7f304367a3ef82f0774d1219ae1ca4f5f91ff8946d6d51ce44f34b60eb` |
| Python Core 套件 | `python -m pytest tests/core` | Python 3.14.6 / pytest 9.1.1 | **PASS**（407 passed, 1 warning, 37.24s） | `verification/P17/pytest.log`<br>`cc92ade6d2a7c98c0241295f09b47898635105d5ad9537b2d7edd208f7eef230` |
| Rust Source 套件 | `$env:M2RC1_PYTHON="C:\Python314\python.exe"; cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests` | Rust 1.98.1 | **PASS**（95 passed, 0 failed, 1 ignored） | `verification/P17/cargo-source.log`<br>`47a0ad1d17edfdd0f7e1e5e1ee3fdcd5709766f089477680949c55f8dfa72948` |
| Rust Packaged 套件 | `$env:M2RC1_PACKAGED='1'; cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml packaged_sidecar_tests -- --test-threads=1 --nocapture` | Rust 1.98.1 / frozen bundle | **PASS**（12 passed, 0 failed, 0 ignored） | `verification/P17/cargo-packaged.log`<br>`f4d61723d54a498ecc5137d4f35f668302593c67ceef5aa869b209c3bfd8db09` |
| 边界与红线审计 | 静态代码与正则扫描 | PowerShell | **PASS**（0 处越界/路径/导出引用） | `verification/P17/boundary_audit.txt`<br>`2bb99d4b9775ebf6c3cc095882262af08c61d31410520421a1028e54e3e3aba9` |
| 行为证据总结 | 逐项契约与设计基线核验报告 | Markdown | **PASS** | `verification/P17/behavioral_evidence.md`<br>`c49b5c2e853835c4f0ad191359d5ab76e62b09fb45d16166901da9c73c04d839` |
| 资源清单 | 资源处置清单 | JSON | **PASS** | `verification/P17/resource-manifest.json`<br>`3af8f3ed49daab9099c98c5ccf6f8b648bc275471c17e3748bff793d24298fe8` |
| **GUI e2e 测试** | Windows Headless WebView2 | 无头环境 | **NOT_RUN** | **无头 Windows 无法取得 WebView2 窗口句柄 `0x80070578`；如实声明未运行，绝不以单测通过表述为 e2e 通过** |
| **治理检查器** | `tools/governance/check.ps1` | 本工作树 | **NOT_RUN** | **本 worktree 内无 `tools/governance/` 目录，检查器只在主仓库可用，如实说明** |

---

## 接收方式

- **工作区**：`G:/CODEX/New Manga.workspace/worktrees/P17`
- **分支**：`agent/antigravity/P17`
- **复现命令**：
  1. `npm --prefix apps/desktop/frontend test src/reader`（验证阅读器专项单测）
  2. `npm --prefix apps/desktop/frontend test`（验证全量前端单测）
  3. `npm --prefix apps/desktop/frontend run build`（验证前端生产编译）
  4. `python -m pytest tests/core`（验证 Python Core 无回归）
  5. `cargo test --locked --manifest-path apps/desktop/src-tauri/Cargo.toml -- --skip packaged_sidecar_tests`（验证 host 侧无回归）

---

## 下一任务建议（必填）

- **Task ID / 标题**：P17 Review R1 复核与集成验收（P17-REVIEW）
- **推荐 Agent / Reviewer**：dsh
- **推荐原因与前置依赖**：P17 阅读器 UI 依据设计基线 §4 实现完毕，前端单测、生产编译、Core 与 Rust 测试套件全绿，所有契约语义红线（无路径、资源通道、beginning 不改写、独立进度键、缺失译图 null、坐标映射、事件重查快照）均由测试钉死，且严守边界未实现导出面板。现需要 Reviewer dsh 进行独立代码审查与 Gate 裁决。
- **Recovery point**：`G:/CODEX/New Manga.workspace/worktrees/P17`，分支 `agent/antigravity/P17`。
- **允许修改路径**：`doc/reviews/P17-*.md`、`verification/P17/**`
- **禁止范围与新增授权条件**：不得修改已实现的阅读器组件核心逻辑；不得合并分支；不得引入未授权契约修改。
- **交付物**：`doc/reviews/P17-review-dsh-r1.md`
- **验证命令、环境与完成 Gate**：
  - 复跑 `npm --prefix apps/desktop/frontend test src/reader` 全绿；
  - 检查 `verification/P17/boundary_audit.txt` 与 `behavioral_evidence.md`；
  - Gate: Reviewer approved。
- **可直接转发给 Agent 的指令**：
  > 请在工作目录 `G:/CODEX/New Manga.workspace/worktrees/P17`（分支 `agent/antigravity/P17`）对 Task P17「阅读器 Reader UI 实现」执行独立 Code Review（Reviewer: dsh）。重点核对：(1) 严格按设计基线 §4 实现，(2) 严守边界未实现归属 P14 的导出面板（W21-W25）与 G20，(3) AC2 语义红线（资源通道、无路径、beginning 不改进度、模式独立进度键、delta 缺失不发、Webtoon 像素坐标、缺失译图为 null），(4) AC3 收到事件重查快照，(5) 前端单测、构建、Core 与 Rust 不回归。审查报告写入 `doc/reviews/P17-review-dsh-r1.md`。

---

## 风险与遗留

- **GUI e2e 未运行**：由于无头 Windows 环境缺乏物理显示输出，无法创建 WebView2 窗口句柄（错误码 `0x80070578`），因此如实声明未运行 GUI e2e，待有真实桌面的集成测试环境中进行最终端到端验收。
- **治理检查器**：本 worktree 内无 `tools/governance/check.ps1`，该检查器需在主仓运行。
- **BL-15 规约遵循**：本 Handoff 的 `delivery_head` 保持为 `pending`，由 Coordinator 在 closeout 时以 `git rev-parse HEAD` 冻结，不在此自引用尚未产生的 commit SHA。
