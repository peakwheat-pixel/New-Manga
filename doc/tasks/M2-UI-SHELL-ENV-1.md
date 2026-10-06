---
id: M2-UI-SHELL-ENV-1
title: ui_shell QML 事件投递环境敏感失败定性+Quick 后端固定（test-debt）
kind: test-debt
status: in_progress
approval: user_2026-10-07_autonomous_mode_continuation
suggested_owner: Codex Executor
owner: Codex Executor
reviewer: Antigravity（非作者，快速独立 Review）
integrator: Codex
depends_on: [T3.2.1-REPAIR-13]
base_commit: 76379af2
branch: main（测试基础设施单文件修复，直落 main）
worktree: G:/CODEX/New Manga
integration_commit: null
---

# M2-UI-SHELL-ENV-1

## 来源与目标

`tests/ui_shell/test_repair13_import_entry.py` 两例（`test_current_chapter_alias_follows_row_click`、`test_import_entry_enabled_after_row_click`）在当前会话稳定失败，构成全量基线 2 failed 负担。本轮定性并处置测试环境，不改任何 Legacy 产品代码。

## 定性事实（已核实）

- 失败形态：`QTest.mouseClick` 投递后章节行未响应（`currentChapterId` 停留空）；不依赖真实点击投递的三例同文件全过。
- stderr 出现 `TypeError: Cannot read property ... of null` 群（QML 属性在窗口 surface 未就绪时的延迟求值），非断言失败主因。
- 代码零漂移：`git log` 显示测试文件自 REPAIR-13 集成（`6fe7455d`）未变；`src/ui/qml/` 2026-10-01 以来零 commit；PySide6 6.11.2 与 `requirements.txt` pin 一致。
- **决定性对照**：`QT_QPA_PLATFORM=offscreen` 下 5 passed、`QT_QUICK_BACKEND=software` 下 5 passed、默认（RHI/D3D）下 2 failed——失败绑定默认渲染后端，而当前会话窗口 surface 非交互（锁屏/断连显示）时合成鼠标投递丢失。
- 产品边界：Legacy QML 不释放诊断/修复 Task；本 Task 只动 `tests/ui_shell/conftest.py`（测试基础设施）。

## 范围（冻结）

- 仅改 `tests/ui_shell/conftest.py`：`os.environ.setdefault("QT_QUICK_BACKEND", "software")`（保留 Windows 平台+字体库，符合既有 conftest 注释约束；setdefault 尊重外部覆盖）。
- 其他测试文件、src/ui、QML、契约零改动。

## 验收 Gate

1. `pytest tests/ui_shell/test_repair13_import_entry.py -q` = 5 passed。
2. `pytest tests/ui_shell -q` 全绿。
3. pytest 全量：**1862 passed + 1 skipped + 0 failed**（唯一变化=2 例环境性失败转绿）。
4. 非作者 Review 通过（Antigravity）。

## 完成定义

AC 全过 + Review 通过 + STATUS 基线数字更新（2 failed 清零）。

## 交付记录（2026-10-07）

- 实现+收口同 commit：conftest.py `os.environ.setdefault("QT_QUICK_BACKEND", "software")` + docstring 约束说明；零 src/ui/QML/契约改动。
- Reviewer=Antigravity（非作者）：**approve**，0×P0-P3；独立复现决定性对照（RHI 显式=2 failed / software=5 passed / offscreen=5 passed / unset=5 passed）与零漂移三项声称；P4-1 noqa 补 F401 顺手闭、P4-2 证据边界接受（"锁屏/断连显示"子定性为会话状态假设、不可进程内独立观测，处置正确性由 RHI↔software 对照关系独立支撑）、P4-3 上 Task 0 字节 err 杂物已清理。
- Gate：repair13 文件 5 passed；tests/ui_shell 全目录 **150 passed**；全量 pytest **1862 passed + 1 skipped + 0 failed**（唯一变化=2 例环境性失败转绿）。raw 日志 verification/M2-UI-SHELL-ENV-1/raw/。
- 效果：全量基线自本轮起 0 failed（此前仅剩的 2 failed=ui_shell 环境敏感两例清零）。
