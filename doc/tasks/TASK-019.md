---
id: TASK-019
title: 集成已验证的检测/OCR/翻译/修复 Provider
kind: implementation
status: blocked
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-011, TASK-014, TASK-016, TASK-017, TASK-018, TASK-024]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-019：集成已验证的检测/OCR/翻译/修复 Provider

**BLOCKED（2026-09-17 窗口条款登记，后续复核）**：2026-09-16 ZCode 全权窗口解冻名单仅含 TASK-015/024/017，本 Task 不在名单内；窗口授权已归还。U-6 已批准 Sakura 监控只做健康探测与就绪状态、不做显存或负载等深度指标，但该范围决定不释放 TASK-019。
当前仍不能转为 ready：硬依赖 TASK-018 已释放为 `ready`，但尚未完成并集成 `done`；TASK-019 也未获得单独用户释放授权。TASK-017 已 done，但其真实 OpenAI-compatible Provider 的协议/成本/时延实测仍 NOT_RUN（付费端点未配置），因此相关真实端点证据仍缺。本机未运行 Sakura 服务，AC-EXT-SAKURA-001 的真实服务验证因此 NOT_RUN；健康探测端点须在 TASK-019 交付中明确。D08 §78 的 AC-EXT-SAKURA-001 已列入本任务，D13 结果为 NOT_RUN。本文件保持 status=blocked、approval=pending_user_review，owner/base/branch/worktree 为空。
当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D02 §6/11；D06 §6～23/51～57/80～85；D08 AC-OCR/INPAINT/FALLBACK/GPU/MODEL。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-OCR-001、AC-OCR-004、AC-INPAINT-001、AC-INPAINT-002、AC-INPAINT-003、AC-INPAINT-004、AC-RFULL-001、AC-RFULL-002、AC-RFULL-003、AC-RFULL-004、AC-RFULL-005、AC-FALLBACK-001、AC-FALLBACK-002、AC-GPU-001、AC-GPU-002、AC-GPU-003、AC-OPTIONAL-002、AC-MODEL-001、AC-MODEL-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 按已批准实验报告实现明确选定能力，覆盖本地OCR、韩文OCR、兼容Vision、Translation以及Simple Fill/漫画修复和彩色路线；不可用候选明确禁用，未获批范围不能称完成。
- [ ] 通过统一网络/设备/文件边界接入Pipeline，严格输出映射、显式fallback、Mask/模型/options/provenance与单Region写回限制。
- [ ] 模型延迟加载、下载进度/取消/Hash、Ready判定、OOM隔离、GPU重任务默认单并发；CPU fallback仅在Provider声明支持时执行。
- [ ] D08 §78 的 AC-EXT-SAKURA-001：Sakura Profile 连接测试给出健康/就绪状态与原因，探测范围遵守 U-6；真实服务验证与实现证据必须实测，当前 D13 结果 NOT_RUN。SAKURA-002/003 仍为草案，不自动纳入本任务。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/infrastructure/providers/**
- src/infrastructure/devices/**
- src/application/translation/inpaint/**
- src/ports/detection/**
- src/ports/ocr/**
- src/ports/translation/**
- src/ports/inpaint/**
- tests/providers/**
- doc/tasks/TASK-019.md
- doc/handoffs/TASK-019-*.md
- verification/TASK-019/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/providers；每能力contract与mock错误路径，缺依赖不阻止Core。
- 运行授权真实样本端到端，比较目标/非目标Region、原图Hash、人工锁及新Revision；记录实际设备与模型。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-011](TASK-011.md)、[TASK-014](TASK-014.md)、[TASK-016](TASK-016.md)、[TASK-017](TASK-017.md)、[TASK-018](TASK-018.md)、[TASK-024](TASK-024.md)。依赖必须已经集成 done 才可开始。

若必需模型不可用，阻止相关AC完成并由用户决定范围；不能只交Mock冒充真实集成。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-17 blocker 复核及 TASK-018 释放后：U-6 范围已批准；AC-EXT-SAKURA-001 已正式编号并追踪为 NOT_RUN。TASK-018 已 `ready` 但未完成，仍为 TASK-019 硬依赖；TASK-017 真实 Provider 协议/成本/时延 NOT_RUN（付费端点未配置），本机 Sakura 服务未运行，真实探测验证 NOT_RUN；TASK-019 未获单独释放，状态维持 blocked，不创建 Owner/base/branch/worktree。
