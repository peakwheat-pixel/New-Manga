---
id: F11-HOTKEY-1
title: 全局 F11 快捷键（沉浸/全屏切换）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_followups_batch_a2
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/F11-HOTKEY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/F11-HOTKEY-1
integration_commit: b63025690
delivery_head: ec94991c399c94f771e7bc1958dcf868585eae34
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/F11-HOTKEY-1
allowed_paths:
  - doc/tasks/F11-HOTKEY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/F11-HOTKEY-1/**
  - G:/CODEX/New Manga.workspace/task-envs/F11-HOTKEY-1/**
  - G:/CODEX/New Manga.workspace/worktrees/F11-HOTKEY-1/**
---

# F11-HOTKEY-1：全局 F11 快捷键（沉浸/全屏切换）

> 交付状态：**ready-for-integration**（实现 `ec94991c3` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。

## 背景

READER-LIBRARY-WIRE-1 的沉浸入口目前只有工具栏按钮 + 双击；遗留项要求 **F11** 全局快捷键（在应用任意页面均可切换）。

## Acceptance Criteria

- [x] **AC1 快捷键**：应用内按 **F11** 切换沉浸/全屏（非阅读器页进入时打开当前书的沉浸？或先进入阅读器再沉浸——行为需在 Record Decision 中定并测试）；Esc 退出后回到原页面。→ **MET**：记录于下方 Record Decision。阅读器页 F11 → 沉浸窗（全屏 1400x787），Esc → 回阅读器页；书架页 F11 → 先切阅读器再开沉浸，Esc/F11 → 回书架。证据：`live-evidence.json`、`screens/03-06`、headless 8 项。
- [x] **AC2 不干扰输入**：搜索框/文本框聚焦时 F11 不吞字、不误触发；与现有键位（H/F/方向键）无冲突。→ **MET**：搜索框聚焦（值「雾港来信」）时 background/foreground F11 均不触发、文本不变；Tab 移出后同会话 F11 正常打开（正反对照）；修饰键 F11 忽略；非 F11 键不消费；沉浸窗内 H/F/方向键行为不变。证据：`screens/02-*`、`live-evidence.json.window_state_timeline`、`F11HotkeyTests`。
- [x] **AC3 测试**：Avalonia.Headless 覆盖「按 F11 进入/退出」「焦点在输入框时不触发」；真机一次（截图/窗口状态）。→ **MET**：headless 8 项（`tests/NewManga.App.Tests/F11HotkeyTests.cs`）；真机 6 张截图 + 窗口状态时间线（1↔2 窗口）。证据：`test/*`、`screens/*`、`live-evidence.json`。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 基线 3F/2739P/9S 无新增失败。→ **MET**：**153/153 passed, 0 skipped**（coreclient 40 / host 42 / app 71；上卡 145 + 本轮 8）；vitest **60 files / 567 tests**；pytest **3F/2739P/9S**（与基线一致）。证据：`test/summary.json`、`test/dotnet-test-Debug.log`、`test/vitest.log`、`test/pytest.log`。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（快捷键注册方式/冲突策略）。→ **MET**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/F11-HOTKEY-1.md` PASS；下方 14 条 Canonical Evidence pin；`doc/handoffs/F11-HOTKEY-1-handoff.md`（含 Record Decision）。

## Record Decision：F11 行为定义

| 项 | 决定 | 理由 |
|---|---|---|
| 注册方式 | **Avalonia 窗口级 `KeyDown`（Tunnel，`handledEventsToo`）**，应用内生效 | 任务禁止抢占其他应用；源码扫描 `RegisterHotKey/HotKeyManager/GlobalHotKey/SetWindowsHookEx/Win32Properties` **0 命中**（`live-evidence.json.source_grep`） |
| 触发条件 | **裸 F11**（无 Ctrl/Alt/Shift）；带修饰键不消费、不切换 | 避免与系统/其它组合键冲突，防止误触发 |
| 阅读器页按 F11 | 打开当前书沉浸窗（全屏无边框），与工具栏按钮/双击共用 `OpenImmersiveReader()` | 单入口，不引入第二套全屏实现 |
| 非阅读器页按 F11 | **先切到阅读器页**（加载当前/默认书），**再打开沉浸窗**，并记录来源页 | 任务要求应用任意页面可用；页内上下文保持可预期 |
| 关闭沉浸（Esc 或再按 F11） | 回到按 F11 前的页面；本来在阅读器页则回阅读器页 | 满足「Esc 退出后回到原页面」，F11 不改变用户页面上下文 |
| 输入框聚焦 | F11 **不触发、不消费**；不吞字、不改文本 | 搜索/重命名输入优先；避免打断输入法/文本编辑 |
| 沉浸窗内按 F11 | 关闭沉浸窗（toggle off），走同一返回规则 | 「切换」语义一致；Esc 为等价退出键 |
| 与 H/F/方向键 | 不受 F11 影响；处理集中在 `ReaderWindow.TryHandleKey`，F11 为其新增分支 | 无冲突，headless 与真机均验证 |

## 实现摘要（全部 `apps/desktop-avalonia/**`）

- `src/NewManga.App/Views/MainWindow.axaml.cs`：窗口 Tunnel `KeyDown`；`TryHandleGlobalKey(Key, KeyModifiers)`（裸 F11 + 输入框守卫）；`IsTextInputFocused()`；`ToggleImmersiveAsync()`；`_pageBeforeImmersive` + 沉浸窗 `Closed` 恢复来源页；`LastImmersiveToggle`/`ImmersiveRestorePage`（测试/证据）。
- `src/NewManga.App/Views/ReaderWorkbenchPages.cs`：`ReaderWindow.TryHandleKey` 新增 F11 分支（`F11Count++`、flush 进度、`Close()`），类文档更新。
- `tests/NewManga.App.Tests/F11HotkeyTests.cs`（新，8 项）：进入/退出与来源页恢复、阅读器页来源、输入框聚焦不触发（`Show()`+`Focus()`）、修饰键忽略、非 F11 键不消费、沉浸窗内 F11 与 H/F/箭头共存、无库书 fixture 回退。
- 说明：worktree 从 A 组第二批释放提交 `04b657131` 建立；任务卡冻结 base 仍记 `171529b5d`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
| F1 | AC3 | verification/F11-HOTKEY-1/runtime-logs/core-service.stderr.log | ec94991c3 | f9bf37a4bbf2620164a2e563db17b136f7da1026aa9c5495af818cd71f89776b | CANONICAL |
| F2 | AC3 | verification/F11-HOTKEY-1/test/results-app.trx | ec94991c3 | cfe2ed92ebaa50ccaa245df26d87683c62c4c26077240e47595ecf51ff07cd73 | CANONICAL |
| F3 | AC3 | verification/F11-HOTKEY-1/test/results-coreclient.trx | ec94991c3 | 961a7abf362bb77a1af9ccf6d0f3a9d12f0aac8706a32f16a35b5554182be154 | CANONICAL |
| F4 | AC3 | verification/F11-HOTKEY-1/test/results-host.trx | ec94991c3 | be235f6bfa370b6432aad74ac4086cfacf0f684d0893748f888e183ad958d862 | CANONICAL |
| F5 | AC3 | verification/F11-HOTKEY-1/test/test.ps1-final.log | ec94991c3 | 6f8d21f482104a8a8093f6d91419e880bc08df1e228e39aef638579914433960 | CANONICAL |
|---|---|---|---|---|---|
| F11-TEST-SUMMARY | AC4 | verification/F11-HOTKEY-1/test/summary.json | ec94991c399c94f771e7bc1958dcf868585eae34 | bd19da29eed72d4669689b876137b9d2fb52b9cde039c8fe9a54fa384ddc72b1 | CANONICAL |
| F11-TEST-LOG | AC4 | verification/F11-HOTKEY-1/test/dotnet-test-Debug.log | ec94991c399c94f771e7bc1958dcf868585eae34 | adc3ed73d424b917c164109c95e462d4578053abba7c8844feb8d90f533c61ff | CANONICAL |
| F11-VITEST | AC4 | verification/F11-HOTKEY-1/test/vitest.log | ec94991c399c94f771e7bc1958dcf868585eae34 | 975b113346f5a5e09af3d92eb3ff1e1e4fa487dab093f588cc2b6316da45e967 | CANONICAL |
| F11-PYTEST | AC4 | verification/F11-HOTKEY-1/test/pytest.log | ec94991c399c94f771e7bc1958dcf868585eae34 | a83908b51010437d6437134cd6ab57035ed4146dff963b0013ea59af7e90074d | CANONICAL |
| F11-LIVE | AC1/AC2/AC3 | verification/F11-HOTKEY-1/live-evidence.json | ec94991c399c94f771e7bc1958dcf868585eae34 | bf025ed2985e1aea091e435471ae4fc99581f4aee55be1372267389766ce8d6a | CANONICAL |
| F11-SHOT-BOOKSHELF | AC1/AC3 | verification/F11-HOTKEY-1/screens/01-bookshelf-initial.png | ec94991c399c94f771e7bc1958dcf868585eae34 | ddb52d02dd8d4e668db320a406d0ae8ee898486062e4dc0ab081ae73f4208b47 | CANONICAL |
| F11-SHOT-TEXTBOX | AC2/AC3 | verification/F11-HOTKEY-1/screens/02-textbox-focus-f11-noop.png | ec94991c399c94f771e7bc1958dcf868585eae34 | 548cea932e762313b7757081d52bfb86af3a20c55c8ffdf2c38d0eee1e77363a | CANONICAL |
| F11-SHOT-IMMERSIVE-READER | AC1/AC3 | verification/F11-HOTKEY-1/screens/03-immersive-f11-from-reader.png | ec94991c399c94f771e7bc1958dcf868585eae34 | f5759e365e08f20fbb6f65dc80d1e83e2a8a1f2a89dbdaa417b51d36bc14fc4f | CANONICAL |
| F11-SHOT-RESTORED-READER | AC1/AC3 | verification/F11-HOTKEY-1/screens/04-restored-reader-after-esc.png | ec94991c399c94f771e7bc1958dcf868585eae34 | 85bcd4834e716aa59c32db251bfa70bfaa27acb74ee3ef95dfe845384535be7f | CANONICAL |
| F11-SHOT-IMMERSIVE-BOOKSHELF | AC1/AC3 | verification/F11-HOTKEY-1/screens/05-immersive-f11-from-bookshelf.png | ec94991c399c94f771e7bc1958dcf868585eae34 | f5759e365e08f20fbb6f65dc80d1e83e2a8a1f2a89dbdaa417b51d36bc14fc4f | CANONICAL |
| F11-SHOT-RESTORED-BOOKSHELF | AC1/AC3 | verification/F11-HOTKEY-1/screens/06-restored-bookshelf-after-f11-toggle.png | ec94991c399c94f771e7bc1958dcf868585eae34 | 57c49764b22bcbc227fef81f742fe4db77a3fc3ccc7f4f4930d37c53b254bb1b | CANONICAL |
| F11-WIRE | AC1/AC3 | verification/F11-HOTKEY-1/runtime-logs/wire-real-machine.ndjson | ec94991c399c94f771e7bc1958dcf868585eae34 | 9db5c612bc0f6bcab13199044bba4e74e33400bcbeee824fffbe30ea63290f8b | CANONICAL |
| F11-HOSTLOG | AC1/AC3 | verification/F11-HOTKEY-1/runtime-logs/host.log | ec94991c399c94f771e7bc1958dcf868585eae34 | cb05e1a478e73d2d941f6351da277bdacb30bcad8d520cc02208b28932a3e526 | CANONICAL |
| F11-REPORT | AC5 | verification/F11-HOTKEY-1/REPORT.md | ec94991c399c94f771e7bc1958dcf868585eae34 | 145e31bfa85383d303819b82615391dfe04d386cc742066bb17b8e1565f1e0e7 | CANONICAL |

> 注：截图 03 与 05 的 sha256 相同——两次都是从同一本书同一章的同一位置打开沉浸窗，Avalonia 渲染结果逐字节一致；两者分别记录了「阅读器来源」与「书架来源」两个进入路径（窗口状态时间线/`live-evidence.json` 可区分）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/F11-HOTKEY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/F11-HOTKEY-1 | `evidence/`（测试/wire/screens）+ `pkg/app`（29.4 MB 发布件，`core-sidecar` junction）+ `isolated-data`（EXTERNAL：BOOK-FIXTURE 副本） | 2026-10-27 本卡收口时目录存在；`live-evidence.json` 引用其路径；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `ec94991c3`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（14 条 pin 指向 delivery_head）。
- resource_closeout_status：`pending`（task-env 保留引用，未清理）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；数据根为 workspace 副本，源 BOOK-FIXTURE 未改）。
- 未关闭项及保留原因：真机未单跑「书架来源 + Esc」组合（与「书架来源 + F11 关闭」共用同一 `Closed` 恢复路径；headless 已覆盖）；从书架返回时焦点若自动回到搜索框，F11 被输入框守卫忽略（设计使然，Record Decision 已声明）；未注册系统级 F11（应用不在前台时不生效，符合任务限制）；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- 行为定义（Record Decision）：Avalonia 窗口级 Tunnel KeyDown，仅裸 F11；**不注册系统级热键**（RegisterHotKey/HotKeyManager/GlobalHotKey/SetWindowsHookEx/Win32Properties 源码 0 命中）；输入框聚焦优先。
- AC1：阅读器页 F11→当前书沉浸（全屏 1400×787）；非阅读器页 F11→先切阅读器页加载当前/默认书再开沉浸并记录来源页；Esc/再按 F11→回来源页。
- AC2：搜索框聚焦时 F11 不触发/不消费/文本不变；修饰键 F11 忽略；H/F/Esc/方向键不受影响。
- AC3：Headless 8 项 + 真机 6 张截图（01–06，含窗口时间线、搜索文本保留）+ live-evidence.json（10 断言 true、source_grep=0）。
- AC4：DSH 复跑 scripts/test.ps1 → 见执行记录（实现方报 153/153：40/42/71）；vitest 60/567；pytest 3F/2739P/9S 无新增。
- AC5：check.ps1 -TaskPath PASS；14 条 64-hex pin；Handoff（含 Record Decision）。
- 遗留（记录不阻塞）：① 未注册系统级 F11（后台不生效，需另开任务+授权）；② 书架返回时焦点若自动回搜索框则 F11 被守卫忽略（设计声明）；③ 真机未单跑「书架来源+Esc」（与 F11 关闭同路径，headless 覆盖）。
- 集成：b63025690。
