---
id: FEA-07-IMMERSIVE-F11-1
title: 修复 F11 沉浸模式在真实桌面不出现窗口（显示失败兜底 + 主窗恢复 + 错误可见）
kind: fix
governance_version: 3
status: closed_with_limitations
approval: 用户 2026-11-09 明示任务定义（含兜底分支，未要求原生必达）；DSH 裁决 AC5=PARTIAL、以 closed_with_limitations 收口（ADJ §7.19/§7.20）（范围冻结：`OpenImmersiveReader()` 显示失败兜底与错误可见化；`ReaderWindow.Show()` 失败时恢复主窗、不得停留最小化；记录异常到日志；保留 headless 回归。验收：真实桌面 F11 → 无边框全屏窗口覆盖 2560×1440、Esc/F11 退出、主窗恢复原页；失败时主窗不消失且给出提示。证据：`verification/FEA-07-AC5-NATIVE-1/DEFECTS.md` D-AC5-2 + `evidence/watch-immersive-*`）
suggested_owner: dsh
owner: dsh
reviewer: 独立子代理 r1 = changes_requested（R-001…R-011）；r2 待审（同一 head）
depends_on:
  - FEA-07
base_commit: 70a89d009
branch: null
worktree: null
integration_commit: b4f801e2f
delivery_head: b4f801e2f
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-07-IMMERSIVE-F11-1
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/F11HotkeyTests.cs
  - doc/tasks/FEA-07-IMMERSIVE-F11-1.md
  - doc/reviews/FEA-07-IMMERSIVE-F11-1-*.md
  - doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md
  - doc/handoffs/FEA-07-IMMERSIVE-F11-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-07-IMMERSIVE-F11-1/**
out_of_scope:
  - 不改冻结契约/pins/依赖/`tools/e2e/**`/`scripts/**`
  - 不改沉浸窗口视觉/交互语义（无边框 + FullScreen 行为按现状保留）
  - 不做显示拓扑/DPI 相关改动（属 FEA-07-AC5-NATIVE-1）
---

# FEA-07-IMMERSIVE-F11-1

## 背景（缺陷 D-AC5-2）

`verification/FEA-07-AC5-NATIVE-1/DEFECTS.md` 记录了 D-AC5-2：真实桌面上按 F11（手动/注入均验证）后，**主窗被最小化、沉浸 `ReaderWindow` 未出现**；浏览器 F11 可全屏，说明远程键盘正常，问题在应用侧。

代码路径：`MainWindow.TryHandleGlobalKey` → `ToggleImmersiveAsync` → `OpenImmersiveReader()`（`new ReaderWindow(...)` + `window.Show()`；`ReaderWindow` 构造设 `SystemDecorations.None` + `WindowState.FullScreen`）。

## 范围（冻结）

1. `OpenImmersiveReader()` 显示失败兜底与错误可见化；
2. `ReaderWindow.Show()` 失败时**恢复主窗**（不得停留在最小化）；
3. 记录异常到日志；
4. 保留 headless 回归。

## AC

- [x] **AC1**：`TryOpenImmersiveReader()` 捕获 `OpenImmersiveReader()` 的 `Show()` 异常（后者清理后重抛；直接调用成功路径不变），恢复主窗（`WindowState` 不残留 `Minimized`），不向 UI 事件处理器抛出未处理异常。 <<MET>>
- [x] **AC2**：失败时给出可见提示（状态栏文本）并写入日志（`Trace` 错误）。 <<MET>>
- [x] **AC3**：成功路径保持原行为（`LastImmersiveWindow` 设置、`Closed → OnImmersiveWindowClosed`、F11/Esc 退出、页面恢复）。 <<MET>>
- [x] **AC4**：新增 headless 回归：注入显示失败/静默不可见 → `TryOpenImmersiveReader()` 返回 false、`ImmersiveOpenFailure` 非空、主窗未最小化、`LastImmersiveWindow` 为 null；既有 `F11HotkeyTests` 全绿。 <<MET>>
- [ ] **AC5**：真实桌面复测（F11 → 无边框全屏覆盖 2560×1440 / Esc 退出 / 主窗恢复）；若本会话仍无法显示成功，必须记录失败提示可见与主窗保持，作为兜底验收证据，不写 PASS。 <<PARTIAL: legacy 壳原生成功路径已验证（F11→无边框全屏「阅读器」、Esc 关闭、主窗恢复；`evidence/legacy-f11-native-*`）；测试时物理 2K/4K 不在系统中，全屏落在唯一可用显示 1920×1080，未覆盖 2560×1440 目标；默认 v2 壳无 F11 入口（另立 FEA-07-V2-F11-1 待裁决）>>

## 证据

- 缺陷证据：`verification/FEA-07-AC5-NATIVE-1/DEFECTS.md`（D-AC5-2）、`evidence/watch-immersive-*.json`、`evidence/post-f11-*.json`、`evidence/press-f11-*.json`。
- 本卡证据目录：`verification/FEA-07-IMMERSIVE-F11-1/`（测试输出、真实桌面复测 JSON/截图）。

## 实施结果（2026-11-09，DSH）

### 代码
- `MainWindow.TryOpenImmersiveReader()`：捕获 `Show()` 失败（`Exception` 除 OOM），置空 `LastImmersiveWindow`、写 `ImmersiveOpenFailure`、`Trace.TraceError`、写 `immersive-open.log`（共用 `ResolveDiagnosticsRoot`，`--log-dir` 拥有）、`RestoreMainWindowAfterImmersiveFailure()`（`Show()` + 最小化则恢复 `Normal` + `Activate()`）、状态栏提示「全屏阅读器打开失败（已恢复主窗）：…」。
- `Reader.ImmersiveRequested` 入口改走 `TryOpenImmersiveReader()`（不再从 UI 事件抛未处理异常）。
- `ToggleImmersiveAsync`：失败时回退到来源页（不把用户留在 reader 页）。
- 失败提示常驻：`StartHostAsync` 状态赋值在 `ImmersiveOpenFailure != null` 时保留失败提示，不被 Host 状态刷新覆盖。
- `OpenImmersiveReader()` 保留原签名，成功路径行为不变；`ImmersiveShowOverride`（internal）为 headless 故障注入缝。

### 测试
- 新增 `F11_WhenImmersiveShowThrows_RestoresMainWindowAndReportsFailure`：注入显示失败 → `LastImmersiveWindow=null`、`ImmersiveOpenFailure` 含原因、主窗未最小化、页面回退 bookshelf、`immersive-open.log` 含异常；reader 页入口路径同样兜底。
- `F11HotkeyTests` 9/9 通过；全量 .NET：`NewManga.App.Tests 832/0`、`Host 302/0`、`ApplicationCore 31/0`、`DesignSystem/Appearance/ThemeEngine/Presentation` 通过；`CoreClient.Tests` 1 例 `ModelsBuild_BookRun_WithoutInjectedBindings_StillFailsOcrWithProviderNotConfigured` 在全量并发下失败、**单独运行通过** → 归为既有并发 flake（与本次 App-only 变更无关）。

### 原生复测（AC5）
- 新构建真实桌面：应用置顶后用户按 F11 → 无沉浸窗口、主窗**未最小化**、状态栏无失败提示、`immersive-open.log` 未生成 ⇒ **键盘事件未进入应用**（同会话浏览器 F11 可全屏；UIA `FocusedElement` 停留在浏览器输入框）。
- 结论：AC5 `PARTIAL`（headless 兜底已验证；真实桌面全屏/退出/失败提示需在本地控制台会话补测），**不写 PASS**。
- 证据：`evidence/f11-native-after-fix-*.json`、`evidence/f11-fallback-native-*.json`、`evidence/immersive-button-native-*.json`、`%TEMP%`/workspace 截图（含用户内容，仅存仓外）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-IF11-01 | AC1/AC2/AC3（headless 兜底） | `verification/FEA-07-IMMERSIVE-F11-1/evidence/f11-tests-run.txt` | b4f801e2f | 162cd2ea863c34ec3a23fbdb2e3afc5c2c3aa92762a9dadbbd43285249e48149 | CANONICAL |
| EV-IF11-02 | AC3（成功路径兼容） | `verification/FEA-07-IMMERSIVE-F11-1/evidence/reader-immersive-tests-run.txt` | b4f801e2f | 6a354d1739a9ab8bd106903a7f6068f9ee675e7d0dfd1b3efaacd5c9bdc5c634 | CANONICAL |
| EV-IF11-03 | AC4（回归测试源） | `apps/desktop-avalonia/tests/NewManga.App.Tests/F11HotkeyTests.cs` | b4f801e2f | e3e5db89f34f1a081163a748b8444b8843b112e4c623c53507d2fee5715f95d6 | CANONICAL |
| EV-IF11-04 | AC1/AC2（实现） | `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs` | b4f801e2f | 2cc3ccc9396d6865990420a675ab68a5c65e92ed653efe11b967978248ba0129 | CANONICAL |
| EV-IF11-05 | AC5（legacy 原生成功路径） | `verification/FEA-07-IMMERSIVE-F11-1/evidence/legacy-f11-native-20261109-153227.json` | b4f801e2f | 228b520008363ba68195f7370eb8709e543f8b0e7fa3723bc9413857649c802b | CANONICAL |
| EV-IF11-06 | AC5（v2 壳无入口，superseded 采样） | `verification/FEA-07-IMMERSIVE-F11-1/evidence/f11-native-after-fix-20261109-150419.json` | b4f801e2f | 1547664d4d7fd52b36d0ef7bc936ad932601f5f03dc33d1b35984a48be61e2b0 | CANONICAL |
| EV-IF11-07 | 工具（legacy 原生复测） | `verification/FEA-07-IMMERSIVE-F11-1/tools/legacy-f11-native.ps1` | b4f801e2f | cc154de16d7a3cb516f165a5f68b9a0de2acc5381af71a3ba1b52941e0eb2c3b | CANONICAL |
| EV-IF11-08 | 工具（抓取，含 args 缺陷见 N-002） | `verification/FEA-07-IMMERSIVE-F11-1/tools/capture-after-f11.ps1` | b4f801e2f | 7f11daa72938d24417e903c6b7131159842f6a507c88316b7948bd3b5c5b8720 | CANONICAL |
| EV-IF11-09 | AC5 历史采样（同 pid 早期截图，已替代） | `verification/FEA-07-IMMERSIVE-F11-1/evidence/f11-native-after-fix-20261109-150101.json` | b4f801e2f | 51b4218316d7c8b9adca0e7be7f7cfbf5dd816ed70dd5b682660ef567d26ce9e | CANONICAL |
| EV-IF11-10 | AC5（v2 原生按 F11 无窗口） | `verification/FEA-07-IMMERSIVE-F11-1/evidence/f11-fallback-native-20261109-144502.json` | b4f801e2f | 884567d6b8ab3c997a79ca34e8f4bdcb34371c762eacbb767b067ffdd4bb92b0 | CANONICAL |
| EV-IF11-11 | 工具（按钮入口复测） | `verification/FEA-07-IMMERSIVE-F11-1/tools/verify-immersive-button.ps1` | b4f801e2f | fcf48bf87abb2ebdbe599131d51a029126a6105445afbb9cf874fcd28e50950f | CANONICAL |
| EV-IF11-12 | AC5（v2 按钮入口无入口） | `verification/FEA-07-IMMERSIVE-F11-1/evidence/immersive-button-native-20261109-144618.json` | b4f801e2f | 91123ae4493a1f7461914b3c153c1e490cdf5fd8b3c09f4bab173d55bd8a2d16 | CANONICAL |
| EV-IF11-13 | 工具（v2 按钮入口复测） | `verification/FEA-07-IMMERSIVE-F11-1/tools/verify-f11-fallback.ps1` | b4f801e2f | 1a09b75b3f796ebb3ea8a8f25dc984c2a23ed37a3cabbf7fe8738f6522c732b1 | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 应用一律 `--data-root` 隔离；复测期间 UI 显示既有 169 页（AD-003 引用，不复制） |
| display-settings | 复测期间做过模式/缩放试验（ChangeDisplaySettingsEx / Settings UIA） | PRESERVE_UNKNOWN | G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1\moved-evidence | verification/FEA-07-IMMERSIVE-F11-1/evidence/legacy-f11-native-20261109-153227.json | 试验产物已移出仓库；复测时物理 2K/4K 从系统消失（仅剩 Mi TV 1920×1080），**未恢复到 3840×2160@150%**，需用户恢复并核验 |
| tracked-side-effect | 无 | NOT_APPLICABLE | — | — | 单测 `--log-dir` 指向临时目录并清理 |
