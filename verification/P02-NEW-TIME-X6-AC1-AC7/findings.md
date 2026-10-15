# P02-NEW-TIME-X6-AC1-AC7 Findings & Rollup Summary

- **RunId**: `p02-newtime-ac-20261014-r1`
- **Owner**: Antigravity (Fallback from ZCode)
- **Worktree**: `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-AC1-AC7-ANTIGRAVITY`
- **Branch**: `agent/antigravity/P02-NEW-TIME-X6-AC1-AC7`
- **Packaged EXE**: `G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`
- **SHA-256**: `92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`

---

## 1. AC 执行结论总览

| 场景 / AC | 状态 | 证明层级 | 核心指标 / 观测证据 | 证据路径 |
|---|---|---|---|---|
| **AC1 Runtime Identity** | **PASS** | REAL_IPC | 真实 WebView2 (`Edg/155.0.4283.45`)，`m2rc1-desktop.exe` PID 55192，生产 allowlist 15 命令，固定二进制/源码哈希一致 | `verification/P02-NEW-TIME-X6-AC1-AC7/ac1-identity-a3/` |
| **AC2 Navigation & Operation** | **PASS** | REAL_IPC | 真实鼠标按键切换 Console/Workbench，页面 ID 输入，按钮与面板状态，4 张全量视口截图 | `verification/P02-NEW-TIME-X6-AC1-AC7/ac2-navigation/` |
| **AC3 300ms Quiet-Period & Stale Guard** | **PASS** | REAL_IPC (A) / MOCK_IPC (B) | 连续键盘打字单调时钟静默期实测 302.6ms，无中间前缀泄漏，300ms 窗口内切换旧 timer 成功取消，900ms 迟到响应被当前状态守卫成功拦截 | `verification/P02-NEW-TIME-X6-AC1-AC7/ac3-debounce-a6/` |
| **AC4 Write-Refresh Immediacy** | **PASS** | REAL_WEBVIEW_MOCK_IPC | retype (0.1ms, DOM rev 2, sfx), undo (0.1ms, DOM rev 3, speech), restore (0.1ms, DOM rev 5, speech, 8 revisions) 全部三项写后刷新均 < 300ms 且立即读回 | `verification/P02-NEW-TIME-X6-AC1-AC7/ac4-write-refresh-a2/` |
| **AC5 Keyboard & Focus** | **PASS** | REAL_IPC | Tab 遍历链、Enter 激活 Workbench、Shift+Tab 反向遍历、键盘输入、Space/禁用状态观察（Escape 对话框因真实空书库记 NOT_RUN，见 Finding P-04） | `verification/P02-NEW-TIME-X6-AC1-AC7/ac5-keyboard-a2/` |
| **AC6 Contrast & Token Mapping** | **PASS (with findings)** | REAL_IPC | 11 个代表性 DOM 采样点完成 alpha 合成与对比度计算；无浅色模式入口记 NOT_APPLICABLE；发现 1 项对比度不达标与 Token 未接入 | `verification/P02-NEW-TIME-X6-AC1-AC7/ac6-contrast/` |
| **AC7 Rollup & Manifest** | **PASS** | - | 汇总结算全量 AC1–AC6 证据，分类整理测试脚手架修复与产品 Findings，输出交接与审计物 | `verification/P02-NEW-TIME-X6-AC1-AC7/` |

---

## 2. 产品问题目录 (Product Findings)

根据协作契约与 Task 边界，**Owner 不自审、不修改产品代码，所有产品发现如实登记，交由 Codex 与后续 DAG 决策**：

### Finding P-01: 应用根文本对比度未达 WCAG 4.5:1
- **严重度**: P3 / Non-blocking Accessibility
- **位置**: `body > div` (`app root text`)
- **观测值**:
  - 前景: `#D8E0E8` (`rgb(216.0, 224.0, 232.0)`)
  - 合成背景: `#101418`
  - 计算对比度: `4.19:1` (阈值要求: `>= 4.5:1`)
- **建议后继**: 由 UI/UX (ZCode) 微调根文本前景灰度值或背景底色，使对比度达到 4.5:1 以上。

### Finding P-02: F Token 规范未接入 React 运行时样式
- **严重度**: P3 / Design System Integration
- **位置**: 全局 DOM 样式（Console / Workbench）
- **观测值**: 11 个采样点的 computed colors 均为组件内部硬编码 HEX 颜色，与 `doc/design/tokens-cand-f.json` 候选调色板未建立 CSS 变量或主题类绑定（`token_mapping: UNMAPPED`）。
- **建议后继**: 后续视觉打磨 Task 中引入 CSS 变量或 Token Theme Provider 统一管理。

### Finding P-03: 浅色主题入口缺失
- **严重度**: P3 / Feature Scope
- **观测值**: DOM 普查结果显示当前前端无主题切换控件或浅色模式样式定义。
- **状态记录**: 按 AC6 规则判定为 `NOT_APPLICABLE`。

### Finding P-04: 真实空数据环境下无法通过键盘 Escape 关闭历史确认对话框
- **严重度**: P3 / Testability in Empty DB
- **观测值**: 在无预置漫画数据的真实运行模式下，无法在 UI 中创建或选中带有 speech 标注的 region，因而无法拉起改标确认弹窗。
- **状态记录**: AC5 中 Escape 对话框关闭路径诚实记录为 `NOT_RUN`。

---

## 3. 测试脚手架修复记录 (Test Harness Fixes - T Category)

按 Task 授权在 write scope（`apps/desktop/frontend/e2e/p02-new-time/**`）内完成以下修复：
1. **T-01 (Clean Targets Order)**: 调整 `lib/app.mjs` 与 `lib/env.mjs`，确保在创建任何日志/证据文件之前先完成 clean 检查并冻结状态。
2. **T-02 (Scenario Isolation & Attempts)**: 实现 `resolveScenarioRoot` 与参数化 `launchDirs(scenarioRoot)`，各 AC 脚本在 `run-r1/<scenario>/` 独立执行，已有内容自动递增 attempt（严禁覆盖或删除）。
3. **T-03 (Syntax Fix)**: 修复 `ac6-contrast.mjs` 中 `COLLECT_SOURCE` 内未转义的反引号模板字符串。
4. **T-04 (Tauri Bridge Proxy & Timing Isolation)**: 升级 `lib/cdp.mjs` 中的 `INVOKE_WRAPPER_SOURCE`，针对 Tauri v2 运行时特性采用 Proxy 包装，彻底解决对象 freeze 与属性拦截问题；在 `ac3-debounce.mjs` 中按 monotonic start timestamp 精确限定过滤区间；并在 `ac4-write-refresh.mjs` 中处理透明 SVG `<rect fill="none">` 的 stroke 边框点击。
