---
id: P15-HOST-1
title: 设置面 G21/G22/G23 专用命令的 Tauri host 侧注册与 Core 2.6 配对（P15 UI 的端到端前置）
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261017_after_P15_core_chain_complete
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15-C1, P15, P15-CORE-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P15-HOST-1
---

# P15-HOST-1：设置面专用命令的 host 侧注册（消费 P15-CORE-1 的 Core 实现）

## 来源（**为什么需要本 Task**）

P15（设置页 UI）已 `done`，其交付在 Handoff 与本 Task 的 [P15 closeout](../tasks/P15.md) 中**如实声明**：G21/G22/G23 的专用命令已由 **P15-C1 契约冻结**，但 **Tauri host 侧注册属后续配对 Task**；**当前二进制内这些操作会落入契约 §9 的 `SETTINGS_UNAVAILABLE` 投影**——即 **UI 完成 ≠ 端到端可用**。

**分工（Coordinator 2026-10-17 派发前置核对后拆分）**：Core 侧实现归 **[P15-CORE-1](P15-CORE-1.md)**（因 Core **完全缺失**这些命令，实测 9 条抽查 0 命中）；**本 Task 只做 host 侧注册与配对**，依赖 P15-CORE-1 完成。

## Acceptance Criteria

- [ ] **AC1 命令面注册（Host）**：按 [P15_SETTINGS_IPC_CONTRACT.md](../contracts/P15_SETTINGS_IPC_CONTRACT.md) **§3.2 / §5.1 / §5.2 / §6** 注册下列命令（**名字与参数必须逐字一致，不得改名或加字段**）：
      - Provider：`settings_provider_profiles_list/create/update/delete`、`settings_provider_bindings_set/clear/resolve`、`settings_provider_run_snapshot_get`；
      - Network：`settings_network_profiles_list/create/update/delete`、`settings_network_profiles_test`、`settings_network_profile_default_set/clear`、`settings_network_profile_resolve`；
      - 覆盖解析：`settings_resolve_overrides`（只读）；
      - 凭据：`credential_put` / `credential_clear`（Host 所有安全输入面）+ **受信 Host↔Core** 的 `BindProfileCredential` / `ClearProfileCredential`（**不得**注册为 WebView 可调用）。
- [ ] **AC2 production-only 与冻结形状**：新命令**只**加入 production face（不改 probe / AC1 验收面的冻结形状）；`PRODUCTION_COMMANDS` 计数与各 `generate_handler!` 列表、capabilities、权限自动生成、`build.rs` 注释**四处同步**；计数断言按**合并后真实值**更新（不得删断言）。
- [ ] **AC3 安全边界（硬红线）**：Secret、明文凭据、认证头、`CredentialRef`、原始响应、请求体、文件系统路径、Host/Session 凭据、异常文本、不透明写引用**不得**出现在 WebView 的**请求、返回、事件、错误**任何一处；错误只走契约 **§9 封闭投影**（`category`/`phase`/`action`/`message_key`，键集**封闭**）；`CredentialRef` 只存在于受信 Host↔Core 交换与 Core 持久配置；`settings_provider_run_snapshot_get` 返回**去路径/去引用**安全投影。
- [ ] **AC4 与 Core 实现配对**：把 P15-CORE-1 已实现的 Core 命令接到 host 面（协议 minor 2.6）；任一 Core 面未就绪时必须**失败关闭**（`SETTINGS_UNAVAILABLE`），**不得**静默降级或本地伪造。
- [ ] **AC5 验证**：Rust source 与 frozen packaged 两套件**正确口径**下全绿（`--skip packaged_sidecar_tests` → 期望 95+ 基线；`M2RC1_PACKAGED=1 … packaged_sidecar_tests` → 期望 12+ 基线）；Core pytest 不回归；前端套件不回归（期望 ≥274）。
- [ ] **AC6 交付**：固定 commit + [Handoff](../templates/HANDOFF.md) + Canonical Evidence（sha256 按**磁盘字节**且**在与检查器相同的工作树（主仓库）核对**——**BL-16/RV-P15-04 教训**；`commit` 列填**原样** `git rev-parse HEAD`——**BL-17**；`class` 仅 `CANONICAL`/`SOURCE_PIN`——**BL-19**；`delivery_head` 不自引用即将产生的 SHA——**BL-15**；`status` 用合法值，交付时 `in_review`；**BL-18**：不得把自请审查写成独立 Review）。

## 允许修改范围

- `apps/desktop/src-tauri/**`（命令注册、ACL/权限、`build.rs` 计数与列表、测试）
- `doc/contracts/**`（**仅当**发现契约与实现必须对齐的**新增**细节；**不得**重开既有冻结语义）
- 本 Task、`doc/handoffs/P15-HOST-1-*.md`、`verification/P15-HOST-1/**`

## 禁止范围

- **不得**改名/加字段/发明契约未冻结的命令或 wire；**不得**重开 P15-C1/P10 已冻结语义；
- **不得**改前端 `apps/desktop/frontend/**`（P15 已交付；如需 UI 配合，另立 Task）；
- **不得**把 Secret/路径/引用暴露到 WebView **四处**；**不得**为通过测试而放宽安全边界或删除既有断言；
- **不得**改 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md`；不触碰用户 19 项 dirty；不 `push`/`merge`/`reset`/`stash`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 命令注册与四处同步 | cargo | NOT_RUN | 无 |
| AC3 | Secret/路径/引用四处边界 + 封闭投影 | cargo 测试 | NOT_RUN | 无 |
| AC4 | Core 2.6 配对与失败关闭 | cargo + packaged | NOT_RUN | 无 |
| AC5 | Rust source / packaged / pytest / 前端 | 见命令 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **前置**：**P15-C1（契约，done）**、**P15（UI，done）**。
- 风险一：**名字或字段漂移**（契约已冻结）→ AC1 逐字比对。
- 风险二：**Secret 经新面泄露** → AC3 硬红线 + 反例测试。
- 风险三：**计数断言过时** → 按合并后真实值更新（历史教训：跨 Task 计数冲突必须更新而非删除）。
- 阻塞条件：若 Core 2.6 侧 handler 未就绪 → 该面**失败关闭**并如实登记，**不得**本地伪造或静默降级。

## 交付与运行记录

- 2026-10-17 Coordinator 释放（dsh, epoch 6）：依据 P15 交付 Handoff 的诚实声明与本 Task 的独立 Review finding #3（**UI 完成 ≠ 端到端可用**）。
- Handoff：尚无。Review：尚无。实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/P15-HOST-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/P15-HOST-1 | verification/P15-HOST-1/resource-manifest.json | 释放/派发时创建；closeout 按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 尚未派发与执行。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在释放与关闭时同步。