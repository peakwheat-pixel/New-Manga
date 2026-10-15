---
id: ARCH-DOC-REBASELINE
title: 新架构需求、验收及输出格式映射Gate
kind: design
governance_version: 2
status: ready
approval: user_authorized_arch_doc_rebaseline_release_20261015
owner: Codex
reviewer: DeepSeek Harness
depends_on: [P08]
base_commit: 4ef92f3daa527adac752b8fc52d492176697a292
branch: codex/arch-doc-rebaseline
worktree: G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE
integration_commit: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/ARCH-DOC-REBASELINE
---

# ARCH-DOC-REBASELINE

## 来源与目标

来自P08 SCOPE_DRAFT §49/58/71及本轮路线恢复授权。仅登记proposed，不释放或认领；base/branch/worktree在正式释放时由Codex创建并冻结。目标是把既有产品要求映射至AD-001新栈，不降低P0/P1、不重写Schema、不新增产品范围。

## Acceptance Criteria

- [ ] AC1：AC-DOC-001逐份核验01–08覆盖，新技术架构/权限与UI映射具备正式来源，不只证明文件存在。
- [ ] AC2：AC-DOC-002领域/Pipeline/版本/受控来源/持久化与错误语义跨文档一致，有逐项对照证据。
- [ ] AC3：AC-DOC-003四一级页面/默认书架/基础Reader/延期项与01/04/05/08一致；四页设计独立释放，不以文档替代设计审查。
- [ ] AC4：P18的JA/KO、无字页、质量AC对应新链，明确真实样本/真值/阈值/version/device/model/endpoint证据责任；旧结果不继承。
- [ ] AC5：P20的Tauri/WebView2/Python sidecar/Windows/UI/可选模型对应旧stack-specific条目，逐项保留要求与新证据Gate。
- [ ] AC6：P08-FMT PNG/ZIP/CBZ/PDF/文本转录长期验收追踪；P16/P17在消费对应格式契约前须此项完成。
- [ ] AC7：固定head非作者Review、Codex集成与逐消费者Gate裁决；某项未完成不标整Task done，可按消费者拆独立已审交付但须另冻结。

## 允许修改范围（2026-10-15 冻结）

- `doc/02_TECHNICAL_ARCHITECTURE_.md`、`doc/05_UI_MAPPING.md`、`doc/07_NON_FUNCTIONAL_REQUIREMENTS.md`、`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`：仅做 AD-001 新栈映射与一致性对齐，不新增产品范围、不降低任何阈值。
- 本 Task（`doc/tasks/ARCH-DOC-REBASELINE.md`）、`doc/handoffs/ARCH-DOC-REBASELINE-*.md`、`verification/ARCH-DOC-REBASELINE/**`。
- 写入仅限本 Task 的 worktree（`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`）；**禁止原位覆盖主仓现有 dirty 文档**。
- `doc/01_FUNCTIONAL_ARCHITECTURE.md`、`doc/03_DATA_MODEL.md`、`doc/04_USER_FLOW.md`、`doc/06_TRANSLATION_PIPELINE.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 仍**不在** allowlist；确需调整须先由 Codex 单列允许路径并重新冻结。

## 禁止范围

当前proposed不允许实施。后续也不授权产品代码、Schema、依赖、模型、OS操作或旧QML实现；不降低阈值或作用户产品取舍。

## 测试要求

planned：需求逐项映射/引用有效性/跨文档一致/193 AC及P08-FMT与AC-SMOKE覆盖/指定Task治理检查。当前全部NOT_RUN；不把历史PASS迁移到新栈。

## 依赖、风险与阻塞

P08已完成；本Task未冻结执行坐标、未分配worktree，保持proposed。仅P22-REBASE-1是拟释放实施切片。Gate消费者：P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）。

## 交付与运行记录

仅登记，无实现、无Review、无运行。

### 2026-10-15 冻结与释放（Coordinator dsh, epoch=5，guarded-write）

- 来源：用户 2026-10-15 在 P04 关闭后选定"冻结并释放 ARCH-DOC-REBASELINE"。
- 冻结执行坐标：base=`4ef92f3daa527adac752b8fc52d492176697a292`（main HEAD）；branch=`codex/arch-doc-rebaseline`；worktree=`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`（由 Owner 在认领时创建）。
- 逐文件 allowlist 见"允许修改范围（2026-10-15 冻结）"；主仓现有 dirty 架构文档须**先 pin 来源指纹（`verification/ARCH-DOC-REBASELINE/source-pins.json`）再在新 worktree 适配**，禁止原位覆盖。
- 角色：Owner=Codex、Reviewer=DeepSeek Harness（非 Owner、非 contributors/repair participants）、Integrator=Codex；权威参与状态见 `.orchestrator/tasks/ARCH-DOC-REBASELINE-role.json`。
- Gate 消费者：P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）。AC7 要求固定 head 非作者 Review 与逐消费者裁决；可按消费者拆为独立已审交付，但须另行冻结。
- 仍未授权：产品代码、Schema、依赖、模型、OS 操作、旧 QML 实现；不改阈值、不作用户产品取舍；不 push。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

未启动，无可关闭资源。
