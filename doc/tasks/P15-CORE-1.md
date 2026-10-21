---
id: P15-CORE-1
title: 设置面 G21/G22/G23 专用命令的 Core 侧实现（Python Core 2.6；配对 P15-C1 契约）
kind: feature
governance_version: 2
status: superseded
approval: coordinator_ruling_20261017_scope_split_after_owner_escalation
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15-C1, P10, P13-C1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: complete
evidence_dir: verification/P15-CORE-1
---

# P15-CORE-1：设置面专用命令的 Core 侧实现

## 来源（**为什么需要本 Task**）

- **契约已冻结**：[P15_SETTINGS_IPC_CONTRACT.md](../contracts/P15_SETTINGS_IPC_CONTRACT.md)（P15-C1，done `f07221313`）已冻结 G21/G22/G23/G24 的 **wire**（命令名、参数、结果、错误与 §9 投影）。
- **UI 已交付**：P15 设置页 done（`c78ded304`），但其 Handoff **如实声明**这些命令**尚未在 host/Core 侧实现**，当前落入 §9 `SETTINGS_UNAVAILABLE`。
- **派发前置核对（Coordinator 实测）**：Python Core **完全没有**这些命令（9 条抽查全部 0 命中），host 侧亦仅 `settings_get`/`settings_update_section` → **必须先在 Core 实现**，host 注册才能配对。

**本 Task = Core 侧实现**；host 侧注册由 [P15-HOST-1](P15-HOST-1.md) 承接（依赖本 Task）。

## Acceptance Criteria

- [ ] **AC1 命令实现（逐字按契约）**：在 Python Core 实现 [契约](../contracts/P15_SETTINGS_IPC_CONTRACT.md) **§3.2 / §5.1 / §5.2 / §6 / §4.2** 声明的命令与参数/结果**逐字一致**（**不得**改名、增删字段、改错误语义）：
      - Provider：`settings_provider_profiles_list/create/update/delete`、`settings_provider_bindings_set/clear/resolve`、`settings_provider_run_snapshot_get`；
      - Network：`settings_network_profiles_list/create/update/delete`、`settings_network_profiles_test`、`settings_network_profile_default_set/clear`、`settings_network_profile_resolve`；
      - 覆盖解析：`settings_resolve_overrides`（**只读**）；
      - 凭据：`BindProfileCredential` / `ClearProfileCredential`（**受信 Host↔Core**；`credential_ref` 由 Host 提供，Core 校验归属）。
- [ ] **AC2 处置语义（契约硬边界）**：Profile **多 Profile 同 Provider** 可表达；Capability 绑定解析顺序 **任务→章节→作品→全局**且**缺失/禁用不隐式回退**；Network 连接测试**六阶段**（Proxy→DNS→TCP→TLS→HTTP→Provider Auth）**未执行阶段标记**、**失败保留阶段**、**代理失败不静默直连**、**TLS 关闭须危险确认**；Run Snapshot 为**创建时冻结值的只读投影**（编辑配置不改既有 Snapshot）；凭据**先写新引用再切换**、失败保留旧绑定、清除即撤销且后续 Run 解析**不换用其他 Provider**。
- [ ] **AC3 协议与兼容**：按契约声明将 Core 协议推进至 **minor 2.6**（major 不变）；**既有命令与语义零变化**（`settings_get`/`settings_update_section` 及更早 wire 不动）；不得破坏 probe / AC1 验收面。
- [ ] **AC4 安全（硬红线）**：Secret、明文凭据、认证头、`CredentialRef`、原始响应、路径、异常文本**不得**出现在任何返回/错误/事件中；错误只走契约 **§9 封闭投影**的键集；`settings_provider_run_snapshot_get` 返回**去路径/去引用**投影；**不得**把 `CredentialRef` 或 Secret 放入普通 settings DTO。
- [ ] **AC5 验证**：新增 Core 测试覆盖 AC1–AC4（含**反例**：非法键/类型、未授权引用、TLS 未确认、代理失败不得直连、Secret 不得回显、解析回溯矩阵）；`pytest tests/core` **全绿且不回归**（基线 **407**）；如涉及设置持久化，**不得**破坏既有数据（迁移必须向后兼容，或有明确拒绝）。
- [ ] **AC6 交付**：固定 commit + [Handoff](../templates/HANDOFF.md) + Canonical Evidence（sha256 按**磁盘字节**且**在与检查器相同的工作树核对**——**BL-16/RV-P15-04**；`commit` 列填**原样** `git rev-parse HEAD`——**BL-17**；`class` 仅 `CANONICAL`/`SOURCE_PIN`——**BL-19**；`delivery_head` 不自引用即将产生的 SHA——**BL-15**；`status` 合法值、交付用 `in_review`；**BL-18**：不得把自请审查写成独立 Review）。

## 允许修改范围

- `src/**`（Python Core：命令分发、设置/凭据/网络域实现、模型/持久化）
- `tests/core/**`（新增与必要修改；**不得弱化既有断言**）
- 本 Task、`doc/handoffs/P15-CORE-1-*.md`、`verification/P15-CORE-1/**`
- **只读参考**：P15-C1 契约、P10 契约、M2-C1 §3.2/§5.3/§5.7/§10、设计基线 §5

## 禁止范围

- **不得**改契约（`doc/contracts/**`）——wire 已冻结；若发现契约与实现确需对齐，**先上报 Coordinator**，不得自行改契约；
- **不得**改 `apps/desktop/**`（host 注册属 P15-HOST-1）；
- **不得**改 Schema/迁移/依赖清单（如需迁移，先上报）；
- **不得**把 Secret/路径/引用暴露到返回/错误/事件；**不得**为过测试而放宽安全边界或删除既有断言；
- **不得**改 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty；不 `push`/`merge`/`reset`/`stash`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 逐条命令 request/result/error 形状 | pytest | NOT_RUN | 无 |
| AC2 | 解析回溯矩阵、六阶段测试、凭据原子性 | pytest | NOT_RUN | 无 |
| AC3 | 协议 minor 与既有语义不变 | pytest | NOT_RUN | 无 |
| AC4 | Secret/路径/引用反例 + §9 投影键集 | pytest | NOT_RUN | 无 |
| AC5 | `python -m pytest tests/core -q` | py312 venv | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **前置**：**P15-C1（契约，done）**、P10（凭据/设置逻辑边界，done）、P13-C1。
- 风险一：**命令名/字段漂移** → AC1 逐字比对契约。
- 风险二：**Secret 经新命令泄露** → AC4 反例测试为硬门。
- 风险三：**任务过大** → 若 Owner 评估超出单轮可完成范围，**先上报 Coordinator 拆分**（例如按 G21 / G23+G22 两块），**不得**自行缩小契约要求的命令集。
- 阻塞条件：若契约某面缺少实现所需语义 → **如实在 Handoff 登记并失败关闭该面**，不得静默降级或本地伪造。

## 交付与运行记录

- 2026-10-17 Coordinator 释放（dsh, epoch 6）：**派发前置核对**发现 Core 侧完全缺失这些命令（9 条抽查 0 命中）→ 按本项目 "Core Task → host 配对" 惯例拆分释放。
- Handoff：尚无。Review：尚无。实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1 | PRESERVE_UNKNOWN | G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1 | verification/P15-CORE-1/resource-manifest.json | 未交付的隔离 worktree；保留原位、未清理；本 Task 未产生实现或产品数据 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 尚未派发与执行。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放与关闭时同步。

## 阻塞与拆分（2026-10-17，Coordinator 裁决）

**Owner（Codex）在实现前失败关闭并上报**：契约 §5.2 的 `TestNetworkProfile` 在 `provider_profile_id` 缺省且 Direct/System 模式下**无探测目标**，而 `status` 仅 `passed | failed`（L194）且 `failed` 需唯一失败阶段（L212）→ **全阶段 `not_run` 时被迫报 `passed`（假阳性）**。**裁决：阻塞成立，Owner 处置正确**（拒绝自选公网/loopback/假目标、拒绝伪造阶段结果）。

**本 Task 被拆分取代**（见 [ruling-P15-CORE-1-network-test.md](../../verification/PROJECT-ORCHESTRATION-20261016/ruling-P15-CORE-1-network-test.md)）：

| 子 Task | 范围 | 释放条件 |
|---|---|---|
| **P15-CORE-1A** | G21 Provider 面 + G24 覆盖解析 | 可立即释放 |
| **P15-CORE-1B** | G22 凭据 + G23 Network CRUD/默认/解析（**不含** test 命令） | 可立即释放 |
| **P15-CORE-1C** | `settings_network_profiles_test`（六阶段） | **必须等 [P15-C1-FU1](P15-C1-FU1.md) 关闭** |

Owner 成果：基线 `407 passed`（与我独立实测一致）已归档于其 worktree；**无实现提交**（HEAD 未移动），未改契约/apps/Schema/依赖。

## 历史收口（2026-10-21，dsh；r1 修正）

- 收口状态：`superseded`（**不声称本 Task 完成**）。本 Task 因契约 `TestNetworkProfile` 语义阻塞，经 Coordinator 拆分为
  `P15-CORE-1A`（G21 Provider + G24 覆盖解析，`done`，commit `9232802c0`）、`P15-CORE-1B`（G22 凭据 + G23 Network CRUD/默认/解析，`done`，commit `6cf3c8209`）、
  `P15-CORE-1C`（六阶段连接测试，`done`，commit `52b0974ad`）。Core 命令已由该三个子 Task 实现并接线；本 Task 自身无独立交付与 Handoff，故为 superseded，而非"能力不存在"。
- 原始阻塞记录保留在上文（契约 §5.2 无探测目标 → 假阳性风险；Owner 失败关闭正确）；本次仅改状态、manifest 证据指向真实文件并追加本说明，不删除历史记录。
- 依据：`verification/V1-FINALIZE-20261021/legacy-task-closure-adjudication.md`；worktree 保留原位，未删除或移动。
