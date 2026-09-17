---
id: TASK-015
title: 实现阅读器与五种成果导出
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-012, TASK-014]
base_commit: 1000ac82743b75df8b4b385bc7096a015e13f107
branch: agent/zcode/TASK-015-reader-export
worktree: G:/CODEX/New Manga.worktrees/TASK-015-zcode
integration_commit: fa72cee
---

# TASK-015：实现阅读器与五种成果导出

本 Task 由 ZCode 按用户授权实施。2026-09-16 用户追加 9 小时 ZCode 全权窗口授权
（完整条款见 [STATUS](../STATUS.md)「ZCode 全权窗口授权（2026-09-16）」章节）：窗口内
Review 由 ZCode 子 agent 执行、结论登记 `approved_subagent`（用户授权的同体审查，
不等同协作协议 §1 的跨 Agent 独立批准），ZCode 代行主线集成；窗口期满后由用户安排
外部 post-hoc 复审。本 Task 已完成实施、窗口内 Review 与窗口授权集成，状态 `done`；期满补外部 post-hoc 复审的义务不消失。

## 来源与目标

D03 §29/31；D04 §33～37；D05 §37～42/51；D06 §96～97；D08 AC-READ/EXPORT。D 编号对应 [文档索引](../00_INDEX.md)。

主责任编号 AC：AC-LIB-004、AC-EXPORT-001、AC-EXPORT-002、AC-EXPORT-003、AC-READ-001、AC-READ-002、AC-READ-003、AC-READ-004、AC-READ-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 实现Original/Translated两模式、RTL/LTR、独立阅读进度/时长与书架摘要；Webtoon完整按宽滚动由TASK-020验证。
- [x] 单图/ZIP/CBZ/PDF/文本全部有范围、顺序、输出路径/命名/覆盖策略与ExportHistory。
- [x] 导出stale明确提示先渲染或继续当前版本，写失败/取消保留原有目标文件和源文件。
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review（或 2026-09-16 窗口期内用户授权的子 agent Review，登记为 approved_subagent）与授权集成者集成验证后才能 done；窗口期交付须在期满后补外部 post-hoc 复审。（子 agent Review `approved_subagent`；集成 `fa72cee`；master 复验 536 passed）

AC 对照的实际测试证据见 [作者验证记录](../../verification/TASK-015/author-verification.md)。

## 允许修改范围

以下为相对仓库根目录的允许路径；实现未越界。

- src/application/reading/**
- src/application/export/**
- src/ui/qml/reader/**
- src/ui/viewmodels/reader/**
- src/ui/qml/windows/ExportWindow.qml
- src/ui/viewmodels/export/**
- tests/reading_export/**
- doc/tasks/TASK-015.md
- doc/handoffs/TASK-015-*.md
- doc/reviews/TASK-015-*.md（窗口授权条款新增的报告入库路径）
- verification/TASK-015/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

实现遵守情况：未触碰 Schema/migration、`src/bootstrap/app.py`、`src/ui/qml/shell/AppShell.qml`、BookDetailPanel/BookshelfViewModel 等白名单外文件（Review 三轴复核确认）。因装配/显示接线在白名单外产生的遗留项（SQLite 迁移、bootstrap 注入 `readerViewModel`、BookDetailPanel 摘要接线、Reader Nav 章节数据源）已在 Handoff"未跑项与风险"与"集成装配指引"登记，待外部复审与后续 Task 裁量，不由 Owner 自行扩展。

## 测试要求与实际执行

计划命令 `python -m pytest tests/reading_export` 已落地为 64 例专项测试（含 Review
修订轮新增的 R-002 卡死回归与 R-003 恢复用例）。实际执行（完整命令、环境、退出码、
passed/skipped 分列与逐条 skip 原因）见 [作者验证记录](../../verification/TASK-015/author-verification.md)：

- 完整 Qt 环境（Python 3.12.3 + PySide6 6.11.2，`task-envs/TASK-014-py312`）：专项 `64 passed`（退出码 0）；全仓 `536 passed`（退出码 0）。
- 无 PySide6 解释器（Python 3.14.6）：专项 `42 passed, 3 skipped`（退出码 0；skip 原因逐条记录为 PySide6 未安装）；该解释器全仓 Qt 套件收集失败为既有环境限制（与 TASK-013 记录一致），非本 Task 引入。
- NOT_RUN/BLOCKED（不掩盖，期满随集成交付补外部复审）：PDF 外部阅读器像素级验收、真实磁盘满/权限注入、生产装配接线（bootstrap 不在白名单）；Webtoon 完整按宽滚动验收归 TASK-020。

## 依赖、风险与阻塞

硬依赖：[TASK-012](TASK-012.md)、[TASK-014](TASK-014.md)。两者均已集成 done。

本任务实现导出不等于发布Gate通过；进度与Webtoon跨模块回归由TASK-020/026补齐。

当前无阻塞。

## 交付与运行记录

- Handoff：[TASK-015-488fafc](../handoffs/TASK-015-488fafc.md)（第二轮交付；取代 fac2ffe 轮的 `TASK-015-fac2ffe.md`，旧文件已删除、Git 历史可溯）。
- Review：[TASK-015-488fafc](../reviews/TASK-015-488fafc.md)——窗口授权下 ZCode 子 agent 执行；首轮 `changes_requested`（P1×2、P2×4），修订 `ac4ff19` 后复审改判 **`approved_subagent`**（R-001~R-006 全部 fixed，R-007 deferred 至 TASK-020）；期满后需外部 post-hoc 复审。
- 实际执行/测试：[verification/TASK-015/author-verification.md](../../verification/TASK-015/author-verification.md)。
- 最近状态：2026-09-17 窗口授权收口 `done`：实现 `488fafc`、Review 修订 `ac4ff19`（approved_subagent）、文档 `a915d56`、integration merge=`fa72cee`；master 集成复验全仓 `536 passed, 0 skipped`、专项 `42 passed, 3 skipped`（无 PySide6 解释器）。`reviewer` 栏 DeepSeek Harness 为期满补审与后续协作的外部 Reviewer。
- post-hoc Review：DeepSeek Harness 报告 commit `9b77685`（reviewed_head=`a915d562`，approved）；R-101 已关闭，验证记录见 [author-verification.md](../../verification/TASK-015/author-verification.md)。
