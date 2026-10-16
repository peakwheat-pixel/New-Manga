---
id: P15-CORE-1A
title: 设置面 Core 实现 A：G21 Provider 面 + G24 覆盖解析
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261017_split_of_P15_CORE_1
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15-C1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P15-CORE-1A
---

# P15-CORE-1A：设置面 Core 实现 A：G21 Provider 面 + G24 覆盖解析

## 来源
P15-CORE-1 因契约 §5.2 的 TestNetworkProfile 目标缺口**失败关闭**，经裁决拆分为 1A/1B/1C（见 [ruling](../verification/PROJECT-ORCHESTRATION-20261016/ruling-P15-CORE-1-network-test.md)）。**本 Task 不受该缺口影响**，可直接实现。

## 范围
实现契约 **§3.2**（Provider Profile CRUD、Capability 默认绑定）、**§3.3**（Run Snapshot 冻结查看）与 **§6**（`settings_resolve_overrides` 只读）对应的 Core 命令：`settings_provider_profiles_list/create/update/delete`、`settings_provider_bindings_set/clear/resolve`、`settings_provider_run_snapshot_get`、`settings_resolve_overrides`。

## Acceptance Criteria
- [ ] **AC1**：上述命令逐字实现，参数/结果/错误与契约一致。
- [ ] **AC2**：**多 Profile 同 Provider** 可表达；Capability 绑定解析顺序 **任务→章节→作品→全局**，**缺失/禁用不隐式回退**；Run Snapshot 为**创建时冻结值的只读投影**（编辑配置不改既有 Snapshot）。
- [ ] **AC3**：命令在 `core_service` 实现**并**在 `core_assembly` 的 `build_production_handlers` 注册；既有命令与语义**零变化**。
- [ ] **AC4**：`settings_provider_run_snapshot_get` 返回**去路径/去引用**投影；不得含 Secret/认证头/`CredentialRef`/可解析路径。
- [ ] **AC5/AC6**：见下"测试与证据"。

## 允许 / 禁止范围
- **允许**：src/**（Python Core）、	ests/core/**（新增与必要修改，**不得弱化既有断言**）、本 Task、doc/handoffs/P15-CORE-1A-*.md、erification/P15-CORE-1A/**
- **禁止**：不得实现 G22 凭据面、G23 Network 面与 `settings_network_profiles_test`（分别属 1B/1C）
- 契约 **wire 已冻结**（doc/contracts/P15_SETTINGS_IPC_CONTRACT.md）：命令名/参数/结果/错误**逐字一致**，**不得**改名或增删字段；若发现契约问题**停下上报**，不得自行改契约；
- **不得**改 pps/desktop/**、Schema/迁移/依赖；不改 doc/STATUS.md / doc/REBASELINE_PLAN.md；不触碰用户 19 项 dirty；不 push/merge/eset。

## 安全硬红线
Secret / 明文凭据 / 认证头 / CredentialRef / 原始响应 / 路径 / 异常文本**不得**出现在任何**返回、错误、事件**中；错误只走契约 **§9 封闭投影**的键集；CredentialRef 不得进入普通 settings DTO。

## 测试与证据
- 覆盖本范围全部 AC，**必须含反例**（非法键/类型、未授权引用、缺省路径等）；python -m pytest tests/core -q -p no:cacheprovider **全绿且不回归**（基线 **407 passed**，用 G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe）；归档原始日志 + 退出码到 erification/P15-CORE-1A/**；
- 固定 commit + doc/handoffs/P15-CORE-1A-*.md + Canonical Evidence（status: in_review；**BL-15** delivery_head 不自引用；**BL-17** commit 列**原样** git rev-parse HEAD；**BL-19** class 仅 CANONICAL/SOURCE_PIN；**BL-16/RV-P15-04** sha256 按磁盘字节且**须能从主仓库验证**；**BL-18** 不得自请审查冒充独立 Review）。

## 依赖、风险与阻塞
- **前置**：P15-C1（契约，done）。**阻塞条件**：若某面语义不完备 → **失败关闭并上报 Coordinator**（引契约行号），**不得**伪造或静默降级。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。Handoff/Review/测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (\CANONICAL\ / \SOURCE_PIN\) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1A | verification/P15-CORE-1A/resource-manifest.json | 派发时创建；closeout 按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：\pending\。resource_closeout_status：\pending\。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 尚未派发与执行。
- 当前指针清理：\STATUS\ / \REBASELINE_PLAN\ 在释放与关闭时同步。