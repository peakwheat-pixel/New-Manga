---
id: P15-CORE-1C
title: 设置面 Core 实现 C：settings_network_profiles_test 六阶段连接测试（rev 2.7 / A1）
kind: feature
governance_version: 2
status: in_review
approval: coordinator_release_20261017_after_P15-C1-FU1_closed
suggested_owner: Codex
owner: Codex
reviewer: dsh
depends_on: [P15-C1, P15-C1-FU1, P15-CORE-1B]
base_commit: 5f5431b8718b2753e851121909ce3796207b1e72
branch: codex/P15-CORE-1C
worktree: G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C
integration_commit: null
delivery_head: 52b0974ade0250c7cec016de9b909ef00b5370cc
canonical_evidence_status: complete
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
- [x] **AC1**：命令逐字实现；`network_profile_id`/`provider_profile_id` 均**必需非 null**；缺省/非法/不可解析 → **`INVALID_REQUEST`**（**不得**产出 `NetworkTestResult`）。
- [x] **AC2**：**目标恒为 Provider endpoint**；唯一路由选择为请求中的 Network Profile（HTTP/HTTPS/SOCKS5 用其 `proxy_endpoint`；System 用系统对该 endpoint 选出的代理；Direct 直连）；**不得**改用绑定/全局/Direct fallback；`direct_fallback_used` **恒 false**。
- [x] **AC3**：逐阶段按契约判定——DNS 目标为 endpoint 主机名（IP literal → `not_applicable/provider_endpoint_is_ip_literal`）、TCP 为到 endpoint 的**逻辑连接**、TLS 仅 HTTPS endpoint（HTTP → `not_applicable/provider_endpoint_uses_http`）、HTTP **不跨 authority 跟随重定向**、ProviderAuth 不自动重试/不切 Provider（不要求认证 → `not_applicable/provider_auth_not_required`）；System 直连 → `not_applicable/system_route_is_direct`。
- [x] **AC4**：失败阶段保留，其后阶段一律 `not_run/upstream_stage_failed`；`status=passed` ⇒ `failed_stage=null`；`status=failed` ⇒ `failed_stage` 指向唯一失败阶段。
- [x] **AC5 安全**：结果**不得**含原始响应/响应体/请求头/认证头/代理凭据/路径或 endpoint 敏感部分；失败只走 §9 封闭投影；命令在 `core_service` 实现**并**在 `core_assembly` 注册。
- [x] **AC6**：按下述替身反例与完整回归执行并归档证据；测试结论不声称真实网络连通性。

## 允许 / 禁止范围
- **允许**：`src/**`、`tests/core/**`（新增与必要修改，不得弱化既有断言）、本 Task、`doc/handoffs/P15-CORE-1C-*.md`、`verification/P15-CORE-1C/**`
- **禁止**：不得改契约（wire 已冻结于 rev 2.7；有问题**停下上报**并引行号）、`apps/desktop/**`、Schema/迁移/依赖；不得复用/改写 1A/1B 已实现的命令语义；不改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty；不 `push`/`merge`/`reset`。

## 测试与证据
- 覆盖 AC1–AC5，**必须含反例**：缺省/非法 `provider_profile_id` → `INVALID_REQUEST`；**任何情况下不得**出现"无目标却 `passed`"；各模式 × 各阶段的 `not_run`/`not_applicable` 原因正确；代理失败**不得**直连；失败阶段之后全为 `upstream_stage_failed`；结果不含敏感项。测试须以**可注入的探测替身**构造阶段结果（不得真实外连；不得伪造"已真实测试"的结论而未声明替身）。注：真实网络探测能力若无法在测试环境验证，须**如实声明**并保持失败关闭。
- `python -m pytest tests/core -q -p no:cacheprovider` 全绿且不回归（基线 **440 passed**；用 `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe`）；归档日志+退出码。
- 固定 commit + Handoff + Canonical Evidence（`status: in_review`；**BL-15** 不自引用；**BL-17** commit 列原样 `git rev-parse HEAD`；**BL-19** `class` 仅 `CANONICAL`/`SOURCE_PIN`；**BL-16/RV-P15-04** sha256 按磁盘字节且须能从主仓库验证；**BL-18** 不得自请审查冒充独立 Review）。

## 依赖、风险与阻塞
- **前置**：P15-C1、**P15-C1-FU1（done）**、P15-CORE-1B（写范围与 1B 重叠于 `core_service`/`core_assembly` → **须在 1B 关闭后派发**）。
- 风险：**假阳性回归**（无目标报 passed）→ AC1/AC2 为硬门；**真实外连**→ 测试须用替身并如实声明。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）：FU1（A1）已关闭，解除本 Task 的释放门。
- 2026-10-17 Codex 实现并固定 `delivery_head=52b0974ade0250c7cec016de9b909ef00b5370cc`；实现提交后完整 `tests/core` 为 **508 passed / 0 skipped / exit 0**，相对 440 基线增加 68；1 个既有 Pillow 弃用 warning。
- 2026-10-17 Handoff 与验证日志提交于 `fc5407e1b70cb60f04e155c126085ca09e014baf`；本 Task 进入 `in_review`，未执行独立 Review 或集成，不标记 `done`。
- 本次测试使用可注入探测/传输替身，无真实外部 DNS/TCP/TLS/HTTP/ProviderAuth 连通性验证。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| CE-01 | AC2 / AC3 / AC5 | `src/bootstrap/core_assembly.py` | `52b0974ade0250c7cec016de9b909ef00b5370cc` | `ee09ef05c0f6868cd11322b4da5f35bfba6fafd3e0ad06bb3b7565793aed3033` | `CANONICAL` |
| CE-02 | AC1 / AC2 / AC3 / AC4 / AC5 | `src/bootstrap/core_service.py` | `52b0974ade0250c7cec016de9b909ef00b5370cc` | `f0cae3d2286bfa2396897dd5957e06dc897c15f26bb13d8a2260ead02dd990c9` | `CANONICAL` |
| CE-03 | AC1 / AC2 / AC3 / AC4 / AC5 | `src/bootstrap/settings_commands.py` | `52b0974ade0250c7cec016de9b909ef00b5370cc` | `17bc0f75e9332c62b07e00cba3c9f7afea8ffa89833fb1266cca8ed4d3d45824` | `CANONICAL` |
| CE-04 | AC2 / AC3 / AC5 | `src/infrastructure/network/profile_test.py` | `52b0974ade0250c7cec016de9b909ef00b5370cc` | `66238d79424a36d77d070f32b2b96dc7526708b9d36071d9a910305766a7332d` | `CANONICAL` |
| CE-05 | AC1–AC6 | `tests/core/test_p15_core_settings.py` | `52b0974ade0250c7cec016de9b909ef00b5370cc` | `41a40e48c2f7db6d231b0bd40a9316acd8499d356622bf2bd7b39f81f9fe614d` | `CANONICAL` |
| CE-06 | AC1–AC6 / RV-P15-04 | `verification/P15-CORE-1C/pytest-core.log` | `fc5407e1b70cb60f04e155c126085ca09e014baf` | `ced2ee9c85240997130510ba40d467c55bea109835904bc779a836eb5760e061` | `CANONICAL` |
| CE-07 | AC1–AC6 / RV-P15-04 | `verification/P15-CORE-1C/pytest-core.exit-code.txt` | `fc5407e1b70cb60f04e155c126085ca09e014baf` | `13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354` | `CANONICAL` |
| CE-08 | AC1–AC6 / RV-P15-04 | `verification/P15-CORE-1C/pytest-core.command.txt` | `fc5407e1b70cb60f04e155c126085ca09e014baf` | `8feff4893893068681a67ac42b284a58692c0b7144ef35ee554def27fb305c6b` | `CANONICAL` |
| CE-09 | AC1–AC6 / RV-P15-04 | `verification/P15-CORE-1C/pytest-core.environment.txt` | `fc5407e1b70cb60f04e155c126085ca09e014baf` | `64c869ce153aadae941eb9d61bf55ba20a2a18b465670746650e6379de4fd21d` | `CANONICAL` |
| CE-10 | Handoff / review handover | `doc/handoffs/P15-CORE-1C-52b0974ad.md` | `fc5407e1b70cb60f04e155c126085ca09e014baf` | `f033446592b1022b0924983d70e812abdf50d4cfcdab72e52fa22376fb330b38` | `CANONICAL` |
| CE-11 | Resource inventory | `verification/P15-CORE-1C/resource-manifest.json` | `fc5407e1b70cb60f04e155c126085ca09e014baf` | `dc831cb30c6cd2f931337d73464b6facf706b746f185b38c2d88d610382206c4` | `CANONICAL` |
| SP-01 | Frozen wire source: §5.2 and §9 | `doc/contracts/P15_SETTINGS_IPC_CONTRACT.md` | `5f5431b8718b2753e851121909ce3796207b1e72` | `b6b29246c01cb4cdd7a360bf8d34b4499cabbd751cce6d98e6309fe7a0d40090` | `SOURCE_PIN` |

RV-P15-04 哈希复核：上表 SHA-256 均基于当前 worktree 的磁盘字节。`verification/P15-CORE-1C/canonical-hash-verification.txt` 使用主仓库 `G:/CODEX/New Manga` 可读的固定 Git objects，并按 `core.autocrlf=true` 的 Windows checkout 字节复建；12/12 项与磁盘哈希一致。复核只读，没有改动主仓库工作树。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1C | verification/P15-CORE-1C/resource-manifest.json | 保留本 worktree 与固定提交；未 push/merge/reset，未触碰主仓库既有 dirty 文件 |

## Closeout Record

- Closeout date / Codex：2026-10-17 / Codex；Task 状态仍为 `in_review`，尚未通过 Review/集成 Gate。
- canonical_evidence_status：`complete`。resource_closeout_status：`pending`。
- 删除/迁移数量与字节数：0；归档入库的普通证据文件 10 个。pytest 临时目录保留未提交：2536 个文件、283557767 bytes。
- 未关闭项及保留原因：两次临时目录清理均被自动审查以 `blocked by policy` 拒绝；目录未删除、未移动、未提交。详见 `verification/P15-CORE-1C/resource-manifest.json`。
- 当前指针清理：未改 `STATUS` / `REBASELINE_PLAN`；待独立 Review 与 Codex 集成 Gate 后由协调者更新。
