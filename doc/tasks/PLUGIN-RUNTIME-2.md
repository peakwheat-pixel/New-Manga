---
id: PLUGIN-RUNTIME-2
title: 真实流水线 Hook 接线
kind: implementation
governance_version: 3
status: done
approval: authorized
owner: Codex
reviewer: reviewer-settings-a
depends_on: [PLUGIN-RUNTIME-1]
base_commit: d28b7a8b1449e5f4790470bcbbba10abcf3ab388
branch: main
worktree: G:/CODEX/New Manga
integration_commit: eb5e821f3798b4d411ddbd60cd52db65208a2812
delivery_head: 2ea97edd6e65260d1276e7b1e505a036dc612f80
canonical_evidence_status: complete
resource_closeout_status: complete
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

| EV-PLUGIN-RUNTIME-2-TEST | AC1/AC2 | verification/PLUGIN-RUNTIME-2/pytest.log | 050530dfb78afaa9877eac1ce727cd40f69f5837 | d93167e3fafec6c8a48d96159a771340ae522642c7c36bd11f5aa157b4926670 | SOURCE_PIN |

| EV-PLUGIN-RUNTIME-2-GATE | AC3 | verification/PLUGIN-RUNTIME-2/validation.md | - | ef5c8bb040a7996323f19fea3df53f704afc9f65a0eeb1284285e6d1d570f010 | CANONICAL |

| EV-PLUGIN-RUNTIME-2-R2-TEST | AC1/AC2 | verification/PLUGIN-RUNTIME-2/pytest-r2.log | - | 1c2b263058842e1a72ddfb9a4f73d105c29e59e4ab40ceef565f242c1b8dedf6 | SOURCE_PIN |
| EV-PLUGIN-RUNTIME-2-R1 | review | verification/PLUGIN-RUNTIME-2/review-r1.md | - | 285f523b373c30e19add128313970e7ea0abb2421b5c83d869aa8a54790015cb | SOURCE_PIN |

| EV-PLUGIN-RUNTIME-2-R3-TEST | 历史 AC1/AC2 | verification/PLUGIN-RUNTIME-2/pytest-r3.log | - | 167d81e5b5a23d7d0633fecc96e410aba426019d79c91556333697a3c3ce4d25 | SOURCE_PIN |
| EV-PLUGIN-RUNTIME-2-R2 | review | verification/PLUGIN-RUNTIME-2/review-r2.md | - | 80ddbf11d054b8f743b926a503321e1dc803d686989be25a8f6d5b1279f71083 | SOURCE_PIN |

| EV-PLUGIN-RUNTIME-2-R3 | Review/AC3 | verification/PLUGIN-RUNTIME-2/review-r3.md | - | a8544ffbab0ddc5ca7928bbe02b5b19482d398615c193d6b11719b25e8273405 | CANONICAL |

| EV-PLUGIN-RUNTIME-2-INTEGRATION | AC1/AC2 | verification/PLUGIN-RUNTIME-2/integration-pytest.log | - | 1b6e5409c31158f6b7044cd0f6c0b12724a1f61b049348c202641ebd2ae8072d | CANONICAL |
| EV-PLUGIN-RUNTIME-2-CLOSEOUT | AC3/closeout | verification/PLUGIN-RUNTIME-2/closeout.md | - | 52e32349065066026d4ff10d8a70e04e1e4318e3252139cc54c0e0946c27e7d9 | CANONICAL |
| EV-PLUGIN-RUNTIME-2-RESOURCES | resource closeout | verification/PLUGIN-RUNTIME-2/resource-manifest.json | - | 903d332b6855ff5c592ec9264f1ad022b1f8aeeaf18c26cc41d1c22c58a4d3e6 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | G:/CODEX/New Manga | verification/PLUGIN-RUNTIME-2/closeout.md | 唯一现有主工作区；六个原有未知文件保留，不清理 |
| task-env/dataset/model/build/artifact/exchange | NOT_APPLICABLE | NOT_APPLICABLE | - | - | 无新增独立资源 |
| temp/test-material | G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2 | verification/PLUGIN-RUNTIME-2/resource-manifest.json | Task/Handoff/Review 引用；逐文件 hash 已记录，不删除 |
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/PLUGIN-RUNTIME-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/PLUGIN-RUNTIME-2 | verification/PLUGIN-RUNTIME-2/resource-manifest.json | 保留历史治理失败日志；无迁移/删除 |
| evidence | verification/PLUGIN-RUNTIME-2 | PRESERVE_REFERENCED | verification/PLUGIN-RUNTIME-2 | verification/PLUGIN-RUNTIME-2/resource-manifest.json | 当前验收与审查证据永久保留 |

## 交付与运行记录

启动时历史记录：STATUS 仍称 RUNTIME-1 closeout，Task YAML done 与正文 in_review 不一致；以 Plan done 与最新独审为依赖依据，本任务仅刷新当前指针，不改历史 Task。用户直接授权本次 Codex 实施，不改 Coordinator lease。

实际验证：Python 3.14，81 passed / 0 skipped；命令见 pytest.log 对应 Handoff。check.ps1 PASS（3 warnings）；STATUS 预算通过。初次系统 temp ACL 失败后使用独立 workspace temp；装配顺序与中文 payload 编码问题已修复。


Handoff：[交接](../handoffs/PLUGIN-RUNTIME-2.md)。实现 head 050530dfb78afaa9877eac1ce727cd40f69f5837；已派发 reviewer-settings-a 独立子代理，仅允许写 review-r1.md。

Review r1 暴露导出 job.history 与最终 options 不一致、TEXT 内容提前生成；Codex 冻结修复范围为同一导出服务及 core_service 请求构造，统一准备有效输入后生成内容/快照，不增加 IPC。

R1 P1/P2 已修复：prepare_request 在 job/history 冻结前幂等应用 before；text_content_factory 按最终 options 生成实际内容。真实 StartExport ZIP/TEXT 及重建 Runtime 历史一致性回归通过；扩展相关测试 102 passed / 0 skipped。待固定 head 后 r2 复审，r1 不适用于新修订。

历史 r2 交付 head：55af609b0cbb4d7dc29160df150b116989b3b0be；当前审查请求 r2，仅允许写 verification/PLUGIN-RUNTIME-2/review-r2.md。r1 为历史发现证据，不代表新 head 审查结论。

R2 空 format_options 覆盖导致文本必需键丢失：现拒绝并 plugin_error 审计，原选项继续；真实 Core 空覆盖回归通过。最新 103 passed / 0 skipped。此前 pytest.log/pytest-r2.log 为历史过程，当前验收以 pytest-r3.log 为准。

历史 r3 请求：2ea97edd6e65260d1276e7b1e505a036dc612f80，review-r3.md 待返回。r1/r2 报告为历史证据。

最新独立 Review：[r3](../../verification/PLUGIN-RUNTIME-2/review-r3.md) approved，精确 head 2ea97edd6e65260d1276e7b1e505a036dc612f80；独立 22 passed / 0 skipped，R1/R2/R3 fixed。Task approved，等待 Codex 按已审 head 完成正式集成记录和资源 closeout，不视作 done。

## Closeout Record

- 2026-10-23 / Codex：按用户本轮授权完成集成验证与关闭。Task **done**；上方运行记录为历史阶段，当前状态以 frontmatter 与本节为准。
- integration_commit：eb5e821f3798b4d411ddbd60cd52db65208a2812；与已审实现 source/tests 一致。
- 集成验证：111 passed / 0 skipped；r3 approved；详情及资源指纹见 Canonical Evidence 的 closeout.md/resource-manifest.json。
- canonical_evidence_status：complete；resource_closeout_status：complete。
- 资源全部原位保留，删除/移动/归档均 0 项 / 0 字节；未关闭资源项：无（保留裁定已闭环，不代表允许清理）。
- STATUS Active 已移除、Plan done、LEDGER 重新生成；无本 Task README/rolling checkpoint Active 指针需要清理。
- 下一任务建议：无需下一步操作；无已释放 READY，沙箱未授权，签名仍等待证书/发布签核。
