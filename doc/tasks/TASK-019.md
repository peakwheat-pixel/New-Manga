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

**BLOCKED（2026-09-17 窗口条款登记）**：2026-09-16 ZCode 全权窗口的解冻名单仅含
TASK-015/024/017，本 Task 属窗口排除项"解冻名单之外的任务仍冻结"。按条款登记
`blocked`：blocker=窗口授权不覆盖解冻（前状态 `proposed`）；恢复条件=用户批准释放
（届时按流程填 owner/base_commit/branch/worktree 后转 `ready`），即使解除冻结也须先登记两项输入缺口：TASK-018 仍为 `blocked`、TASK-017 的真实
端点层（Provider/成本/时延实测）仍 NOT_RUN（付费端点未配置）。
当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D02 §6/11；D06 §6～23/51～57/80～85；D08 AC-OCR/INPAINT/FALLBACK/GPU/MODEL。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-OCR-001、AC-OCR-004、AC-INPAINT-001、AC-INPAINT-002、AC-INPAINT-003、AC-INPAINT-004、AC-RFULL-001、AC-RFULL-002、AC-RFULL-003、AC-RFULL-004、AC-RFULL-005、AC-FALLBACK-001、AC-FALLBACK-002、AC-GPU-001、AC-GPU-002、AC-GPU-003、AC-OPTIONAL-002、AC-MODEL-001、AC-MODEL-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 按已批准实验报告实现明确选定能力，覆盖本地OCR、韩文OCR、兼容Vision、Translation以及Simple Fill/漫画修复和彩色路线；不可用候选明确禁用，未获批范围不能称完成。
- [ ] 通过统一网络/设备/文件边界接入Pipeline，严格输出映射、显式fallback、Mask/模型/options/provenance与单Region写回限制。
- [ ] 模型延迟加载、下载进度/取消/Hash、Ready判定、OOM隔离、GPU重任务默认单并发；CPU fallback仅在Provider声明支持时执行。
- [ ] TASK-024确认的Sakura本地服务监控范围有实际状态/故障反馈及测试；未批准的监控行为不自行扩展。
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
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
