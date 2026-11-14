---
id: TRANS-BINDING-BRIDGE
title: 自动翻译配置桥：把 P15 profile/能力绑定镜像进 Run 侧 settings.providers.profiles
kind: implementation
governance_version: 3
status: in_progress
disposition: "L1-T-A（2026-11-14 DSH 释放）；依据 MAINT-1-AUTO-TRANSLATE-FEASIBILITY-2026-11-14 §7/§9"
approval: DSH 2026-11-14 释放（评估结论：零冻结契约改动、零 UNFREEZE；本卡是自动翻译唯一必做的新代码）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: 73a182a61
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TRANS-BINDING-BRIDGE
allowed_paths:
  - doc/tasks/TRANS-BINDING-BRIDGE.md
  - doc/reviews/TRANS-BINDING-BRIDGE-*.md
  - verification/TRANS-BINDING-BRIDGE/**
  - src/application/settings/**
  - src/infrastructure/providers/**
  - src/bootstrap/**
  - tests/**
out_of_scope:
  - 冻结契约字节（C-01b…C-17、M2-C1、ADJ-001）
  - 新增 Core wire 命令、新增 IHostController 成员
  - schema/DDL 变更、依赖变更、远端写操作
  - apps/**（Host/UI 侧由 T-B/T-C 承担）
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（DSH 维护）
---

# TRANS-BINDING-BRIDGE：自动翻译配置桥

## 问题（评估 §0 / §5）

Run 运行时读取的是 `pipeline_defaults.settings["providers"]["profiles"]`（`src/infrastructure/providers/runtime.py:182-193` 的 `_profile_settings`），而 Settings 的 P15 profile / 能力绑定只写 JSON store（`src/bootstrap/settings_commands.py:590-682`）。**两者之间没有生产写入方**，因此 `translate` 步骤取不到 binding，停在 `PROVIDER_NOT_CONFIGURED`（`src/infrastructure/providers/handlers.py:1266-1274`）。

这正是「用户配好 Provider、点了翻译、仍报未配置」的根因。

## Acceptance Criteria

- [ ] **AC1 镜像写入**：当 P15 profile 或能力绑定写入成功后，同一事务/同一 seam 内把对应条目镜像进 `pipeline_defaults.settings["providers"]["profiles"]`；镜像形状与 `runtime.py` 读取的键一致（至少 `provider_type` / `base_url` / `model` / `credential_ref` / `capabilities`）。
- [ ] **AC2 只含引用、不含密钥**：镜像**绝不**包含 secret 本体，只含 `credential_ref`（与 `REAL-TRANSLATE-PROVIDER-1` 的既有纪律一致）。
- [ ] **AC3 fail-closed**：镜像写入失败必须 typed 失败并回滚，不允许「JSON store 写了、镜像没写」的半写状态。
- [ ] **AC4 复用既有 seam**：优先复用 `PipelineDefaultsService.save_settings_section`（`src/bootstrap/core_service.py:3106-3113`）这一 seam，**不新增 wire 命令**。
- [ ] **AC5 不新增契约面**：不新增 Core wire 命令、不新增 `IHostController` 成员；`generate_api_inventory.py --check` 维持 `1/80/6=87`；`verify_pins` 18/18。
- [ ] **AC6 判别测试**：至少一条「写入 profile+binding 后，`_profile_settings` 能读到该 profile」的测试；再一条「镜像失败 → 不留半写」的测试。
- [ ] **AC7 门禁**：`check.ps1`（默认 + 本卡 TaskPath）、`verify_pins`、`generate_api_inventory --check`、受影响 pytest 全绿。
- [ ] **AC8 生效时机说明**：在卡面与证据里写明「装配期一次性闭包 settings（`core_assembly.py:1421-1423`）⇒ 配置变更需重启 Core 才生效」，供 T-C 的 UI 文案使用。

## 允许修改范围

见 front matter `allowed_paths`。**不得**改 `apps/**`（Host/UI 属 T-B/T-C）。

## 禁止范围

冻结契约字节、新 wire 命令、新端口成员、schema/DDL、依赖、远端写、三指针。

## 测试要求

Python：`C:\Python314\python.exe -m pytest`（定向 + 全量不得新增 failed）。

## 风险

- 镜像与 store 双写可能引入一致性窗口：AC3 的 fail-closed 是硬要求。
- `settings["providers"]` 的存储位置需先确认（DB settings 表 vs JSON），**先取证再改**。
- 若发现镜像必须改冻结契约才能表达，**停下回卡报 DSH**，不得擅自 UNFREEZE。

## 证据计划

`verification/TRANS-BINDING-BRIDGE/README.md` + `logs/`（测试与门禁原始输出、镜像前后快照）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树 |

## Closeout Record

- 未关闭（当前 `in_progress`）。
