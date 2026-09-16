---
id: TASK-015
title: 实现阅读器与五种成果导出
kind: implementation
status: ready
approval: approved_by_user
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

本 Task 已获用户批准并登记为 `ready`，等待 Owner 在固定 worktree 中认领并实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §29/31；D04 §33～37；D05 §37～42/51；D06 §96～97；D08 AC-READ/EXPORT。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-LIB-004、AC-EXPORT-001、AC-EXPORT-002、AC-EXPORT-003、AC-READ-001、AC-READ-002、AC-READ-003、AC-READ-004、AC-READ-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 实现Original/Translated两模式、RTL/LTR、独立阅读进度/时长与书架摘要；Webtoon完整按宽滚动由TASK-020验证。
- [ ] 单图/ZIP/CBZ/PDF/文本全部有范围、顺序、输出路径/命名/覆盖策略与ExportHistory。
- [ ] 导出stale明确提示先渲染或继续当前版本，写失败/取消保留原有目标文件和源文件。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review（或 2026-09-16 窗口期内用户授权的子 agent Review，登记为 approved_subagent）与授权集成者集成验证后才能 done；窗口期交付须在期满后补外部 post-hoc 复审。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

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

## 测试要求

- 计划：python -m pytest tests/reading_export；重启继续阅读、双模式独立、缺译图、五格式内容/页序/元数据。
- 非法/Unicode文件名、已有目标文件、磁盘错误和stale选择；验证导出产物可重新读取。
- 实现前结果全部 `NOT_RUN`；Owner 必须在本 Task 目录建立后记录实际测试命令、环境、退出码与输出。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-012](TASK-012.md)、[TASK-014](TASK-014.md)。依赖必须已经集成 done 才可开始。

本任务实现导出不等于发布Gate通过；进度与Webtoon跨模块回归由TASK-020/026补齐。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持 `BLOCKED`。本次实际 Owner 为 ZCode；2026-09-16 窗口期内 Review 由 ZCode 子 agent 承担（结论登记 `approved_subagent`），Reviewer 栏 DeepSeek Harness 为期满补审与后续协作的外部 Reviewer；实现不得扩展到白名单外路径。

## 交付与运行记录

- Handoff：待 Owner 交付。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-16 用户批准释放；`ready`，固定 base=`1000ac82743b75df8b4b385bc7096a015e13f107`，等待 Owner 认领。
