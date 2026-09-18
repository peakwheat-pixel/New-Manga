---
id: TASK-027
title: 发布候选集成、打包与最终验收
kind: integration
status: proposed
approval: pending_user_review
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [TASK-026]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-027：发布候选集成、打包与最终验收

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D02 §1/14；D07 §81～82/106/111；D08 §52～53/71～76。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-PKG-001、AC-PKG-002、AC-PKG-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 固定RC commit/app/schema版本，生成onedir包并记录构建命令/Hash/依赖；远端CI仅在项目配置后启用。
- [ ] 干净Windows完成启动→书架→创建Book/Chapter→导入→工作台Pipeline→保存→阅读→导出→重启数据存在。
- [ ] 按D08要求完成P0/P1、数据安全、性能、独立Review与打包Gate，输出READY或NOT READY及证据。
- [ ] 实际发布另遵循用户授权；准备RC不等于自动上传、push、发release或删除历史包。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- .github/workflows/**
- packaging/**
- src/bootstrap/**
- pyproject.toml
- requirements*.txt
- uv.lock
- verification/**
- doc/STATUS.md
- doc/release-notes.md
- doc/tasks/TASK-027.md
- doc/handoffs/TASK-027-*.md
- verification/TASK-027/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 运行全部适用本地测试、打包Smoke、干净机主流程、Secret与源文件安全检查。
- 记录集成commit与被测artifact哈希；任何生产修订使相关旧Review失效并重验。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-026](TASK-026.md)。依赖必须已经集成 done 才可开始。

当前无remote/CI/干净机证据；不能把开发机启动当成最终发布验证。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。

> **2026-09-19 ZCode 全权窗口条目**：本 Task 已纳入 [STATUS](../STATUS.md) 的窗口队列（W12+ 尾项），但**门槛未达成**：需 **TASK-026** 完成 + **用户发布审核**。门槛满足前一律记 `BLOCKED（前置未达成）`，**不得跳过前置强行开工**；窗口内如需调整门槛，由 Codex 在 T1 后处理。
