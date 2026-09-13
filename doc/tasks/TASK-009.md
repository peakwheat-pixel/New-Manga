---
id: TASK-009
title: 实现 Provider 配置、网络策略与凭据边界
kind: implementation
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-006]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-009：实现 Provider 配置、网络策略与凭据边界

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §25～28；D06 §49～57；D07 §63～72/87～89；D08 AC-PROVIDER/NET/SEC/SET/PRIVACY。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-OCR-003、AC-PROVIDER-001、AC-PROVIDER-002、AC-PROVIDER-003、AC-PROVIDER-004、AC-NET-001、AC-NET-002、AC-NET-003、AC-NET-004、AC-SEC-001、AC-SEC-002、AC-SEC-003、AC-SEC-004、AC-SEC-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 支持多个Provider/Network Profile、按能力和任务/章节/作品/全局解析，记录有效设置来源和用于Run的快照。
- [ ] 统一Direct/System/HTTP/HTTPS/SOCKS5/bypass/override策略；代理失败默认禁止直连，显式fallback可追踪。
- [ ] Secret只进入受保护Credential Store，SQLite/日志/普通导出无明文；TLS默认开启；分阶段连接诊断与本地/远程数据提示。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/application/settings/**
- src/infrastructure/network/**
- src/infrastructure/transport/**
- src/infrastructure/credentials/**
- src/ports/network/**
- src/ports/providers/**
- tests/network/**
- doc/tasks/TASK-009.md
- doc/handoffs/TASK-009-*.md
- verification/TASK-009/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/network；本地可控端点验证代理/bypass/鉴权/超时/429/fallback，不依赖真实付费API。
- 扫描临时数据库与测试日志无测试Secret；Profile修改不改变既有快照。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-006](TASK-006.md)。依赖必须已经集成 done 才可开始。

UI由TASK-022接入；具体OCR/Translation模型适配在TASK-019。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
