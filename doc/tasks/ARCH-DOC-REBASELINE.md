---
id: ARCH-DOC-REBASELINE
title: 新架构需求、验收及输出格式映射Gate
kind: design
governance_version: 2
status: proposed
approval: user_authorized_roadmap_registration_only_20261015
owner: Codex
reviewer: DeepSeek Harness
depends_on: [P08]
base_commit: null
branch: null
worktree: null
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

## 允许修改范围（正式释放前需逐文件冻结）

候选仅doc/02_TECHNICAL_ARCHITECTURE_.md、doc/05_UI_MAPPING.md、doc/07_NON_FUNCTIONAL_REQUIREMENTS.md、doc/08_ACCEPTANCE_CRITERIA.md、doc/13_ACCEPTANCE_TRACEABILITY.md及本Task自有证据。01/03/04/06或AD-001若确需调整先由Codex单列允许路径。现有dirty文档先pin来源并在新worktree适配，禁止原位覆盖。

## 禁止范围

当前proposed不允许实施。后续也不授权产品代码、Schema、依赖、模型、OS操作或旧QML实现；不降低阈值或作用户产品取舍。

## 测试要求

planned：需求逐项映射/引用有效性/跨文档一致/193 AC及P08-FMT与AC-SMOKE覆盖/指定Task治理检查。当前全部NOT_RUN；不把历史PASS迁移到新栈。

## 依赖、风险与阻塞

P08已完成；本Task未冻结执行坐标、未分配worktree，保持proposed。仅P22-REBASE-1是拟释放实施切片。Gate消费者：P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）。

## 交付与运行记录

仅登记，无实现、无Review、无运行。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

未启动，无可关闭资源。
