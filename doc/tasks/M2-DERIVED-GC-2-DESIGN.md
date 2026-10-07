---
id: M2-DERIVED-GC-2-DESIGN
title: 轮换旧 preview 引用安全回收设计
kind: design
status: in_progress
approval: user_directive_2026-10-07_preview_reference_safe_design
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness（非作者）
integrator: Codex
depends_on: [M2-DERIVED-GC-1, M2-RC4-DOMAIN-COMMANDS]
audit_input: 32f9b932d681ba1d551560477d7992cddf6fd7ec
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
branch: codex/m2-derived-gc-2-design
worktree: G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN
integration_commit: null
---

# M2-DERIVED-GC-2-DESIGN

## 来源与目标

用户 2026-10-07 明确执行 preview 回收设计指令；RC4-12 有行有文件的轮换增长仍 open（M2-DERIVED-GC-1 仅 PARTIAL mitigation）。本 Task 只交付设计及下一实现 Task 的范围/Gate，不执行回收。

Live Git main@ab4b7c11 clean，common-dir=G:/CODEX/New Manga/.git；32f9b932..ab4b7c11 仅治理差量；依赖 merge 44859014 / 0a7e0d5b 必须核验为主线祖先。分支/worktree 由 Codex 在本 release commit 后创建，创建结果写入证据；不得复用 dirty checkout。

## Acceptance Criteria

- [ ] AC1：固定 HEAD 下追踪 publisher/catalog、render current/pinned Revision、Core/Rust 独立进程、grant/轮换/读取所有相关调用链，并提供文件/行证据。
- [ ] AC2：给出可删/必留/未知矩阵；仅 TTL、年龄、数量不足以授权删除；Managed Copy/源文件/人工修改/Lock 与 current/pinned 均受保护。
- [ ] AC3：最小生命周期方案明确 issue 与 delete 互斥、在途读取、崩溃恢复、未知历史资源保留、目录/文件逃逸；需要共享 seam/Schema 时明确后继授权范围，不更改现行契约。
- [ ] AC4：拟定后继实现 Task 的实际 base/分支/worktree/allowed_paths/交付/验证 Gate 与可转发指令；本轮只准备、不启动实现。
- [ ] AC5：设计范围 diff 对 src/apps/tests/依赖/Schema 为零；文档检查有命令+HEAD+EXIT；非作者 DSH 固定 head 审查、条件闭合、Codex 集成后才 done。

## 允许修改范围

- doc/tasks/M2-DERIVED-GC-2-DESIGN.md
- doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md（设计稿；不修订现行 wire/Schema）
- verification/M2-DERIVED-GC-2-DESIGN/**
- doc/handoffs/M2-DERIVED-GC-2-DESIGN-*.md
- doc/reviews/M2-DERIVED-GC-2-DESIGN-*.md（Codex 原字节导入 DSH 报告，不代写独立批准）
- Codex 元数据维护：doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、doc/tasks/README.md。

共享变更裁量：本轮可记录内部 catalog/host bridge 生命周期 seam 的设计建议；生产实现、catalog Schema、主产品 Schema、协议字段与依赖变更均未获本轮写权限，必须在后继 Task 明确冻结。

## 禁止范围

src/**、apps/**、tests/**、requirements*、Schema/migration、用户数据/源文件/模型/素材、部署、远端 push、Legacy 实现；不清理任何历史 worktree。

## 测试要求

| 场景 | 命令/环境 | 当前结果 | 证据 |
|---|---|---|---|
| Git/依赖/范围 | PowerShell：git status / rev-parse / merge-base / diff --check | planned / NOT_RUN | 本 Task verification |
| 设计矩阵与链接 | 只读代码核对 + 小型文档验证脚本 | planned / NOT_RUN | 同上 |
| 独立 Review | 真实 DSH，固定 reviewed_head；缺环境标 NOT_RUN | planned / NOT_RUN | 原报告 |
| 产品测试 | 本轮零产品改动，不以历史 PASS 代本轮验证 | NOT_RUN（设计范围） | 不适用 |

## 交付与运行记录

- release：本 commit；后续固定 delivery head 与 Handoff 追加，不自引用本文件提交 Hash。
- ExecutionState：ACTIVE；创建 worktree 后 Owner 将状态转 in_progress/ACTIVE。
- 下一步：实际调用链取证 → 最小设计 → 固定交付 → DSH 独立 Review → 条件闭合 → Codex 集成；不启动后继实现。
