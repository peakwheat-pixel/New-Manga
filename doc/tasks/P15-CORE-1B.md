---
id: P15-CORE-1B
title: 设置面 Core 实现 B：G22 凭据面 + G23 Network CRUD/默认/解析（不含测试命令）
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
evidence_dir: verification/P15-CORE-1B
---

# P15-CORE-1B：设置面 Core 实现 B：G22 凭据面 + G23 Network CRUD/默认/解析（不含测试命令）

## 来源
P15-CORE-1 因契约 §5.2 的 TestNetworkProfile 目标缺口**失败关闭**，经裁决拆分为 1A/1B/1C（见 [ruling](../verification/PROJECT-ORCHESTRATION-20261016/ruling-P15-CORE-1-network-test.md)）。**本 Task 不受该缺口影响**，可直接实现。

## 范围
实现契约 **§4.2**（受信 Host↔Core：`BindProfileCredential` / `ClearProfileCredential`）与 **§5.1**（Network Profile CRUD、`settings_network_profile_default_set/clear`、`settings_network_profile_resolve`）。**不含** `settings_network_profiles_test`（属 1C，等 P15-C1-FU1）。

## Acceptance Criteria
- [ ] **AC1**：上述命令逐字实现；`Bind/ClearProfileCredential` **只**经受信 Host→Core 路由，**不注册为 WebView 可调用**。
- [ ] **AC2**：Network Profile 模式/`proxy_endpoint` 组合校验（HTTP/HTTPS/SOCKS5 必需且 scheme 相符；Direct/System 必须 null）；`verify_tls` 默认 true、关闭需 `confirm_disable_tls_verification: true`；`allow_proxy_failure_direct_fallback` **默认 false**；默认选择键**仅**由 `SetGlobalNetworkProfile` 写；解析顺序 **Provider→Global→System→Direct**。
- [ ] **AC3**：凭据**先写新引用再切换**（失败保留旧绑定）、清除即撤销且后续 Run 解析**不换用其他 Provider/Credential**；`credential_ref` 由 Host 提供、Core 校验归属。
- [ ] **AC4**：命令在 `core_service` 实现**并**在 `core_assembly` 注册；既有命令与语义**零变化**。
- [ ] **AC5/AC6**：见下"测试与证据"。

## 允许 / 禁止范围
- **允许**：src/**（Python Core）、	ests/core/**（新增与必要修改，**不得弱化既有断言**）、本 Task、doc/handoffs/P15-CORE-1B-*.md、erification/P15-CORE-1B/**
- **禁止**：不得实现 G21 Provider 面（属 1A）与 `settings_network_profiles_test`（属 1C）
- 契约 **wire 已冻结**（doc/contracts/P15_SETTINGS_IPC_CONTRACT.md）：命令名/参数/结果/错误**逐字一致**，**不得**改名或增删字段；若发现契约问题**停下上报**，不得自行改契约；
- **不得**改 pps/desktop/**、Schema/迁移/依赖；不改 doc/STATUS.md / doc/REBASELINE_PLAN.md；不触碰用户 19 项 dirty；不 push/merge/eset。

## 安全硬红线
Secret / 明文凭据 / 认证头 / CredentialRef / 原始响应 / 路径 / 异常文本**不得**出现在任何**返回、错误、事件**中；错误只走契约 **§9 封闭投影**的键集；CredentialRef 不得进入普通 settings DTO。

## 测试与证据
- 覆盖本范围全部 AC，**必须含反例**（非法键/类型、未授权引用、缺省路径等）；python -m pytest tests/core -q -p no:cacheprovider **全绿且不回归**（基线 **407 passed**，用 G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe）；归档原始日志 + 退出码到 erification/P15-CORE-1B/**；
- 固定 commit + doc/handoffs/P15-CORE-1B-*.md + Canonical Evidence（status: in_review；**BL-15** delivery_head 不自引用；**BL-17** commit 列**原样** git rev-parse HEAD；**BL-19** class 仅 CANONICAL/SOURCE_PIN；**BL-16/RV-P15-04** sha256 按磁盘字节且**须能从主仓库验证**；**BL-18** 不得自请审查冒充独立 Review）。

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
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B | verification/P15-CORE-1B/resource-manifest.json | 派发时创建；closeout 按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：\pending\。resource_closeout_status：\pending\。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 尚未派发与执行。
- 当前指针清理：\STATUS\ / \REBASELINE_PLAN\ 在释放与关闭时同步。