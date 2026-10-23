---
id: PLUGIN-RUNTIME-2
title: 真实流水线 Hook 接线
kind: implementation
governance_version: 3
status: in_review
approval: authorized
owner: Codex
reviewer: reviewer-settings-a
depends_on: [PLUGIN-RUNTIME-1]
base_commit: d28b7a8b1449e5f4790470bcbbba10abcf3ab388
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 050530dfb78afaa9877eac1ce727cd40f69f5837
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/PLUGIN-RUNTIME-2
allowed_paths:
  - src/infrastructure/plugins/service.py
  - src/infrastructure/plugins/_hook_runner.py
  - src/application/export/service.py
  - src/infrastructure/providers/handlers.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - tests/**
  - doc/tasks/PLUGIN-RUNTIME-2.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/REBASELINE_PLAN.md
  - doc/handoffs/**
  - verification/PLUGIN-RUNTIME-2/**
---

# PLUGIN-RUNTIME-2：真实流水线 Hook 接线

## 来源与目标

2026-10-23 用户直接授权。依赖 PLUGIN-RUNTIME-1 已 done，最新独审 verification/PLUGIN-RUNTIME-1/review-r3.md approved。继承 AD-001 新架构与 trusted-code 边界。

## 冻结范围

detect 输入可覆盖 options；ocr 可覆盖 script/direction/options；export 可覆盖 format_options。结果对象直接覆盖同名输入字段；多个插件按发现顺序后者优先。schema_ref=nm-plugin-hook/1；身份、图像字节、路径授权、Lock/Revision、发布策略不交给插件覆盖。after_* 只观察 JSON 摘要，忽略返回。无新增 IPC、设置、依赖或数据库 Schema。

## Acceptance Criteria

- [x] **AC1** detect/ocr/export 真实入口调用 before/after，合法覆盖实际输入，只读 after。 <<MET>>
- [x] **AC2** Run 内全局关闭零插件调用，超时/崩溃跳过并审计、主链继续。 <<MET>>
- [x] **AC3** 固定提交与 Handoff、独立 Review 请求、治理 PASS、STATUS ≤3200 字节。 <<MET>>

## 禁止范围

禁止 push/merge/reset/stash；不修改未跟踪诊断文件；不实现 OS 沙箱、IPC 或 UI。

## 测试要求

planned：定向 pytest 覆盖运行入口、覆盖/只读、超时/崩溃/全局关闭；pwsh -NoProfile -File tools/governance/check.ps1。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

| EV-PLUGIN-RUNTIME-2-TEST | AC1/AC2 | verification/PLUGIN-RUNTIME-2/pytest.log | 050530dfb78afaa9877eac1ce727cd40f69f5837 | d93167e3fafec6c8a48d96159a771340ae522642c7c36bd11f5aa157b4926670 | CANONICAL |

| EV-PLUGIN-RUNTIME-2-GATE | AC3 | verification/PLUGIN-RUNTIME-2/validation.md | - | 1a12582f86ac19ff13c41de160bd9b75918cc00e250d9cc4edacc4f3fea168cf | CANONICAL |

| EV-PLUGIN-RUNTIME-2-R2-TEST | AC1/AC2 | verification/PLUGIN-RUNTIME-2/pytest-r2.log | - | 1c2b263058842e1a72ddfb9a4f73d105c29e59e4ab40ceef565f242c1b8dedf6 | CANONICAL |
| EV-PLUGIN-RUNTIME-2-R1 | review | verification/PLUGIN-RUNTIME-2/review-r1.md | - | 285f523b373c30e19add128313970e7ea0abb2421b5c83d869aa8a54790015cb | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | 原位 | main | 现有主工作区不清理 |
| task-env/dataset/model/artifact/temp/exchange | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无新增 |
| temp | G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2 | PRESERVE_REFERENCED | 原位 | pytest 独立运行目录 | 测试证据复现，无清理 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/PLUGIN-RUNTIME-2 | PRESERVE_REFERENCED | 原位 | 测试日志 | 测试恢复用 |

## 交付与运行记录

当前 HEAD 与文档存在旧指针：STATUS 仍称 RUNTIME-1 closeout，Task YAML done 与正文 in_review 不一致；以 Plan done 与最新独审为依赖依据，本任务仅刷新当前指针，不改历史 Task。用户直接授权本次 Codex 实施，不改 Coordinator lease。

实际验证：Python 3.14，81 passed / 0 skipped；命令见 pytest.log 对应 Handoff。check.ps1 PASS（3 warnings）；STATUS 预算通过。初次系统 temp ACL 失败后使用独立 workspace temp；装配顺序与中文 payload 编码问题已修复。


Handoff：[交接](../handoffs/PLUGIN-RUNTIME-2.md)。实现 head 050530dfb78afaa9877eac1ce727cd40f69f5837；已派发 reviewer-settings-a 独立子代理，仅允许写 review-r1.md。

Review r1 暴露导出 job.history 与最终 options 不一致、TEXT 内容提前生成；Codex 冻结修复范围为同一导出服务及 core_service 请求构造，统一准备有效输入后生成内容/快照，不增加 IPC。

R1 P1/P2 已修复：prepare_request 在 job/history 冻结前幂等应用 before；text_content_factory 按最终 options 生成实际内容。真实 StartExport ZIP/TEXT 及重建 Runtime 历史一致性回归通过；扩展相关测试 102 passed / 0 skipped。待固定 head 后 r2 复审，r1 不适用于新修订。
