---
id: TASK-015
title: 实现阅读器与五种成果导出
kind: implementation
status: in_review
approval: approved
decision: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-012, TASK-014]
base_commit: 1000ac82743b75df8b4b385bc7096a015e13f107
branch: agent/zcode/TASK-015-reader-export
worktree: G:/CODEX/New Manga.worktrees/TASK-015-zcode
integration_commit: null
---

# TASK-015：实现阅读器与五种成果导出

本 Task 由 ZCode 按用户授权实施；固定 base、分支、worktree 与白名单见上方元数据。
第二轮交付已完成，停在 `in_review` 等待 DeepSeek Harness 独立 Review。当前阶段见
[STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。全局 STATUS 暂不由 Owner 更新。

## 来源与目标

D03 §29/31；D04 §33～37；D05 §37～42/51；D06 §96～97；D08 AC-READ/EXPORT。D 编号对应 [文档索引](../00_INDEX.md)。

主责任编号 AC：AC-LIB-004、AC-EXPORT-001、AC-EXPORT-002、AC-EXPORT-003、AC-READ-001、AC-READ-002、AC-READ-003、AC-READ-004、AC-READ-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 实现Original/Translated两模式、RTL/LTR、独立阅读进度/时长与书架摘要；Webtoon完整按宽滚动由TASK-020验证。
- [x] 单图/ZIP/CBZ/PDF/文本全部有范围、顺序、输出路径/命名/覆盖策略与ExportHistory。
- [x] 导出stale明确提示先渲染或继续当前版本，写失败/取消保留原有目标文件和源文件。
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Owner 侧交付已完成；Review 与集成环节待 DeepSeek Harness / Codex 执行后才置 done）

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
- verification/TASK-015/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

实现遵守情况：未触碰 Schema/migration、`src/bootstrap/app.py`、`src/ui/qml/shell/AppShell.qml`、BookDetailPanel/BookshelfViewModel 等白名单外文件。因装配/显示接线在白名单外产生的遗留项（SQLite 迁移、bootstrap 注入 `readerViewModel`、BookDetailPanel 摘要接线、Reader Nav 章节数据源）已在 Handoff"未跑项与风险"与"集成装配指引"登记，待 Codex 裁量范围变更，不由 Owner 自行扩展。

## 测试要求与实际执行

计划命令 `python -m pytest tests/reading_export` 已落地为 63 例专项测试。实际执行（完整命令、环境、退出码、passed/skipped 分列与逐条 skip 原因）见 [作者验证记录](../../verification/TASK-015/author-verification.md)：

- 完整 Qt 环境（Python 3.12.3 + PySide6 6.11.2，`task-envs/TASK-014-py312`）：专项 `63 passed`（退出码 0）；全仓 `535 passed`（退出码 0，连续两轮稳定）。
- 无 PySide6 解释器（Python 3.14.6）：专项 `42 passed, 3 skipped`（退出码 0；skip 原因逐条记录为 PySide6 未安装）；该解释器全仓 Qt 套件收集失败为既有环境限制（与 TASK-013 记录一致），非本 Task 引入。
- NOT_RUN：PDF 外部阅读器像素级验收、真实磁盘满/权限注入、生产装配接线；Webtoon 完整按宽滚动验收归 TASK-020。

## 依赖、风险与阻塞

硬依赖：[TASK-012](TASK-012.md)、[TASK-014](TASK-014.md)。两者均已集成 done。

本任务实现导出不等于发布Gate通过；进度与Webtoon跨模块回归由TASK-020/026补齐。

当前无阻塞。

## 交付与运行记录

- Handoff：[TASK-015-488fafc](../handoffs/TASK-015-488fafc.md)（第二轮交付，实现 head `488fafc`；取代 fac2ffe 轮的 `TASK-015-fac2ffe.md`，旧文件已删除、Git 历史可溯）。
- Review：尚无（等待 DeepSeek Harness 固定 `base=1000ac8`、`head=488fafc` 独立审查）。
- 实际执行/测试：[verification/TASK-015/author-verification.md](../../verification/TASK-015/author-verification.md)。
- 最近状态：2026-09-16 ZCode 完成第二轮实现并回填 AC 与验证证据，停在 `in_review`；未自行标记 approved/done。
