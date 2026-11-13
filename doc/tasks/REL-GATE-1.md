---
id: REL-GATE-1
title: Release Gate 可执行证据补齐（GUI 冒烟 / 构建 / NOT_RUN 边界）
kind: verification
governance_version: 3
status: ready
resume_status: ready
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [AUDIT14-V1-MANIFEST-1]
base_commit: 903014273
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REL-GATE-1
allowed_paths:
  - verification/REL-GATE-1/**
  - doc/tasks/REL-GATE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# REL-GATE-1：Release Gate 可执行证据补齐（GUI 冒烟 / 构建 / NOT_RUN 边界）

## 来源与目标

`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` 维持 **BLOCKED**，缺 clean install、真实 GUI 全验收、真实模型 API 调用、完整验收证据。本 Task 在**不安装、不发布、不调用付费模型 API**的边界内，补齐可执行证据：固定 HEAD/构建、GUI 冒烟（V2 shell 隔离数据根）、发布产物生成（workspace 内，不安装）、明确 NOT_RUN 项；不改变 Release Gate 结论，不声称产品已发布。

## Acceptance Criteria

- [ ] **AC1**：固定 HEAD 与构建证据（.NET 构建/app 构建、EXIT、原始输出），记录 build 环境。
- [ ] **AC2**：GUI 冒烟：在隔离数据根启动 V2 shell，记录进程存活、截图/日志、EXIT 与限制；若环境无法启动，记录 BLOCKED 并保留原始 stderr。
- [ ] **AC3**：发布产物生成到 workspace（`publish.ps1` 路径策略已改）或明确 NOT_RUN；安装/卸载、真实模型 API、clean install 明确 NOT_RUN，不写成 PASS。
- [ ] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决；Release Gate 维持 BLOCKED 并记录本 Task 能/不能证明的内容。

## 允许修改范围

- `verification/REL-GATE-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

安装/卸载/发布/上传、真实模型 API 付费调用、产品源码、契约、依赖、真实用户数据、远端写操作、历史改写。

## 测试要求

构建与 GUI 冒烟保存原始 stdout/stderr/EXIT/时间；不可运行项写 NOT_RUN/BLOCKED；不得把截图存在写成完整产品验收。
