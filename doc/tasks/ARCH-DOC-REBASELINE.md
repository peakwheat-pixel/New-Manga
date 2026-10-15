---
id: ARCH-DOC-REBASELINE
title: 新架构需求、验收及输出格式映射Gate
kind: design
governance_version: 2
status: ready
approval: user_authorized_arch_doc_rebaseline_release_20261015
owner: Antigravity
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

来自P08 SCOPE_DRAFT §49/58/71及本轮路线恢复授权。目标是把既有产品要求映射至AD-001新栈，不降低P0/P1、不重写Schema、不新增产品范围。

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

不授权产品代码、Schema、依赖、模型、OS操作或旧QML实现；不降低阈值或作用户产品取舍。不合 main、不 push。

## 测试要求

planned：需求逐项映射/引用有效性/跨文档一致/193 AC及P08-FMT与AC-SMOKE覆盖/指定Task治理检查。当前全部NOT_RUN；不把历史PASS迁移到新栈。

## 依赖、风险与阻塞

P08已完成。Gate 消费者：P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）。

## 交付与运行记录

- 2026-10-15 Owner 路由与认领：Antigravity 认领 Owner，在 worktree `G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE` 执行。
- 2026-10-15 来源 pin 锁定：扫描主仓 10 个未提交架构文档工作区内容，计算 SHA-256、字节数、mtime 并产出 `verification/ARCH-DOC-REBASELINE/source-pins.json`。
- 2026-10-15 AC1~AC6 逐项核验完成：产出 6 份专项证据报告与 1 份总览报告至 `verification/ARCH-DOC-REBASELINE/`。
- 2026-10-15 架构文档对齐：基于 worktree HEAD 版本在 allowlist 文档（`doc/02, 05, 07, 08, 13`）顶栏增加重基线与 AD-001 目标架构对齐说明，旧实现归为 LEGACY / HISTORICAL，不降阈值，不原位覆盖主仓。
- 2026-10-15 交付 Handoff：提交固定 commit，编写 Handoff 报告，移交 DeepSeek Harness 审查。

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
| EVID-DOC-PIN | AC1/SourcePin | verification/ARCH-DOC-REBASELINE/source-pins.json | pending | 1200e967a03f7caad259244cc11e724b35f97e859120a4ef56dbfea54a01f977 | SOURCE_PIN |
| EVID-DOC-AC1 | AC1 | verification/ARCH-DOC-REBASELINE/ac1-coverage-and-sources.md | pending | 577695c0ea10684def679a0bd76dc7553d89fe78837095e13208536a2eb5fb7b | CANONICAL |
| EVID-DOC-AC2 | AC2 | verification/ARCH-DOC-REBASELINE/ac2-cross-document-consistency.md | pending | a28c60c5b1d2b8f6e8285c229c96269748fde08fa1905b61ebb6f6b6fe5d8778 | CANONICAL |
| EVID-DOC-AC3 | AC3 | verification/ARCH-DOC-REBASELINE/ac3-four-pages-and-deferred.md | pending | 94bcd0722e820f1778cce2b943725fda8908df5e2f37242c01aa79caf8d9dc12 | CANONICAL |
| EVID-DOC-AC4 | AC4 | verification/ARCH-DOC-REBASELINE/ac4-p18-quality-and-responsibility.md | pending | d8bb1a38af31c3ed76e5f081680b07515ad184aa307e3d87afc75776d71cc87d | CANONICAL |
| EVID-DOC-AC5 | AC5 | verification/ARCH-DOC-REBASELINE/ac5-p20-nfr-stack-rebaseline.md | pending | bb29dc6fa2a154e8209987e7d4a6b2a259d081a0bb91147d36e62e64f4264044 | CANONICAL |
| EVID-DOC-AC6 | AC6 | verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md | pending | b0276a9c78f217a2398e4367a83783345058bf2a70b89e23fad23af8d0d20ede | CANONICAL |
| EVID-DOC-SUM | AC1-6/Summary | verification/ARCH-DOC-REBASELINE/rebaseline-summary.md | pending | 7703a92bea5cc55f516055ae29b66e8c1196533940e9dba6ea53cdd62614d4f5 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE | pending | 任务交付分支 worktree，保留供 Review 与下游集成 |

## Closeout Record
- 2026-10-15 Owner 路由：`route-agent.py --role owner --task-profile heavy --owner-policy AUTO_SELECT` 选中 **antigravity**（较 codex 同分时由 router tie-break 决定）；权威参与状态以 `.orchestrator/tasks/ARCH-DOC-REBASELINE-role.json` 为准（owner=antigravity，codex 保留为 contributor）。Reviewer 仍为 DeepSeek Harness（非 Owner、非参与者）。
- 2026-10-15 集成与审查：Owner 交付 `70208144` 经 R1 独立 Review（`approved_with_conditions；source-pins 10/10 复核一致）后合并入 main；AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN，按 AC7 由各消费者 Gate（P09/P18/P20/P16/P17）裁决后本 Task 方可 done。

- 2026-10-15 集成落库：合并 `codex/arch-doc-rebaseline` 入 main（merge=`4227e8b509e3a42736229b93df4bd9eec548153d`）。集成前按用户裁定先把主仓 5 个未提交文档固定为基线（`836a12c6`），再合并分支；5 个文档三方自动合并成功，`doc/tasks/ARCH-DOC-REBASELINE.md` 冲突按“双方记录并存”解决。本 Task 维持 `ready`（AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN），按 AC7 待 P09/P18/P20/P16/P17 消费者裁决后方可 done。
