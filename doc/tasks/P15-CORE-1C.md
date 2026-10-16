---
id: P15-CORE-1C
title: 设置面 Core 实现 C：settings_network_profiles_test 六阶段连接测试（rev 2.7 / A1）
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261017_after_P15-C1-FU1_closed
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15-C1, P15-C1-FU1, P15-CORE-1B]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P15-CORE-1C
---

# P15-CORE-1C：六阶段连接测试的 Core 实现

## 来源
P15-CORE-1 因 `TestNetworkProfile` 目标语义缺口**失败关闭**，经裁决拆为 1A/1B/1C。缺口已由 **[P15-C1-FU1](P15-C1-FU1.md)（done）** 按**用户裁决 A1** 修订契约（minor **2.7**）：
- `TestNetworkProfile { network_profile_id, provider_profile_id }` —— **`provider_profile_id` 必需**；
- 目标**恒为**所选 Provider 的 `endpoint`；
- 缺省/null/非法/不可解析 → **`INVALID_REQUEST`**，**不得**转换为阶段 `not_run` 或 `status=passed`；
- **禁止**自选公网/loopback/假目标、禁止把 Proxy 主机冒充 TLS/HTTP 目标、禁止伪造阶段结果。

## 范围
实现契约 **§5.2（rev 2.7）** 的 `settings_network_profiles_test`：六阶段（Proxy→DNS→TCP→TLS→HTTP→ProviderAuth）按 **5 模式 × 6 阶段**判定表执行，并返回 `NetworkTestResult`。

## Acceptance Criteria
- [ ] **AC1**：命令逐字实现；`network_profile_id`/`provider_profile_id` 均**必需非 null**；缺省/非法/不可解析 → **`INVALID_REQUEST`**（**不得**产出 `NetworkTestResult`）。
- [ ] **AC2**：**目标恒为 Provider endpoint**；唯一路由选择为请求中的 Network Profile（HTTP/HTTPS/SOCKS5 用其 `proxy_endpoint`；System 用系统对该 endpoint 选出的代理；Direct 直连）；**不得**改用绑定/全局/Direct fallback；`direct_fallback_used` **恒 false**。
- [ ] **AC3**：逐阶段按契约判定——DNS 目标为 endpoint 主机名（IP literal → `not_applicable/provider_endpoint_is_ip_literal`）、TCP 为到 endpoint 的**逻辑连接**、TLS 仅 HTTPS endpoint（HTTP → `not_applicable/provider_endpoint_uses_http`）、HTTP **不跨 authority 跟随重定向**、ProviderAuth 不自动重试/不切 Provider（不要求认证 → `not_applicable/provider_auth_not_required`）；System 直连 → `not_applicable/system_route_is_direct`。
- [ ] **AC4**：失败阶段保留，其后阶段一律 `not_run/upstream_stage_failed`；`status=passed` ⇒ `failed_stage=null`；`status=failed` ⇒ `failed_stage` 指向唯一失败阶段。
- [ ] **AC5 安全**：结果**不得**含原始响应/响应体/请求头/认证头/代理凭据/路径或 endpoint 敏感部分；失败只走 §9 封闭投影；命令在 `core_service` 实现**并**在 `core_assembly` 注册。
- [ ] **AC6**：见下测试与证据要求。

## 允许 / 禁止范围
- **允许**：`src/**`、`tests/core/**`（新增与必要修改，不得弱化既有断言）、本 Task、`doc/handoffs/P15-CORE-1C-*.md`、`verification/P15-CORE-1C/**`
- **禁止**：不得改契约（wire 已冻结于 rev 2.7；有问题**停下上报**并引行号）、`apps/desktop/**`、Schema/迁移/依赖；不得复用/改写 1A/1B 已实现的命令语义；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty；不 `push`/`merge`/`reset`。

## 测试与证据
- 覆盖 AC1–AC5，**必须含反例**：缺省/非法 `provider_profile_id` → `INVALID_REQUEST`；**任何情况下不得**出现"无目标却 `passed`"；各模式 × 各阶段的 `not_run`/`not_applicable` 原因正确；代理失败**不得**直连；失败阶段之后全为 `upstream_stage_failed`；结果不含敏感项。测试须以**可注入的探测替身**构造阶段结果（不得真实外连；不得伪造"已真实测试"的结论而未声明替身）。注：真实网络探测能力若无法在测试环境验证，须**如实声明**并保持失败关闭。
- `python -m pytest tests/core -q -p no:cacheprovider` 全绿且不回归（基线 **407**；用 `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe`）；归档日志+退出码。
- 固定 commit + Handoff + Canonical Evidence（`status: in_review`；**BL-15** 不自引用；**BL-17** commit 列原样 `git rev-parse HEAD`；**BL-19** `class` 仅 `CANONICAL`/`SOURCE_PIN`；**BL-16/RV-P15-04** sha256 按磁盘字节且须能从主仓库验证；**BL-18** 不得自请审查冒充独立 Review）。

## 依赖、风险与阻塞
- **前置**：P15-C1、**P15-C1-FU1（done）**、P15-CORE-1B（写范围与 1B 重叠于 `core_service`/`core_assembly` → **须在 1B 关闭后派发**）。
- 风险：**假阳性回归**（无目标报 passed）→ AC1/AC2 为硬门；**真实外连**→ 测试须用替身并如实声明。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）：FU1（A1）已关闭，解除本 Task 的释放门。
- Handoff/Review/测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C | verification/P15-CORE-1C/resource-manifest.json | 派发时创建；closeout 按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 尚未派发与执行。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放与关闭时同步。