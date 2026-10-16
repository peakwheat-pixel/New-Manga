---
id: HOST-ISSUER-1-C1
title: host→Core grant 注册通道契约（host-only 注册/撤销 wire 与 session 绑定）
kind: design
governance_version: 2
status: in_progress
approval: coordinator_release_20261016_resolution_for_host_issuer_blocker
suggested_owner: Codex
owner: Codex
reviewer: null
depends_on: [P09-FU2, P16]
base_commit: 6a5051dcafa549f200730a4f9824d83d187f07a2
branch: codex/HOST-ISSUER-1-C1-grant-registration-contract
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1
integration_commit: null
delivery_head: af6fa705de54489ce32811cdc8dd3be51a1fd999
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/HOST-ISSUER-1-C1
---

# HOST-ISSUER-1-C1：host→Core grant 注册通道契约

## 来源与目标

- 来源：**HOST-ISSUER-1 的 `BLOCKED_WAITING_EXTERNAL_DECISION`**
  （来源 worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`，文件 `verification/HOST-ISSUER-1/blocker-assessment.md`，固定于 source commit `bacf151b7f4fd61f5b34666b96a444ee95030874`；Owner 实现 head：无；分支 `codex/HOST-ISSUER-1-tauri-ref-issuer`）。
  Owner 以**代码事实**证明：可信 host **没有任何通道**把 grant 注册进**运行中的** Core。
- **缺口事实（Owner 实证，Coordinator 已复核）**：
  1. `src/bootstrap/core_service.py` 的 `_register_export_target` / `_revoke_export_target` / `_register_import_source` /
     `_revoke_import_source` 是 **live `CoreServiceServer` 的私有方法**，**未出现在 dispatcher 路由**中；
  2. Core JSON-RPC 已路由 `ImportPages` / `StartExport`，但**没有**注册/撤销命令；
  3. `src/bootstrap/core_assembly.py` 为**该 Core 实例**在内存中构造 import/export grant registry；
     第二个进程或既有 `host_bridge` sidecar **无法填充 live registry**；
  4. `apps/desktop/src-tauri/src/core_bridge.rs` 只与 resource-channel sidecar 通信（`ping/issue/resolve/touch/revoke/...`），
     **不持有** Import/Export grant registry；
  5. 把注册暴露为 **WebView 可调用**命令会**破坏** §10.3/§10.4 的受信 host 边界。
- **基线契约状态**：本 Task base 的 rev 2.2 §11 把 `auth/permission handshake` 标为 **`UNKNOWN / NOT_IN_SCOPE`**；本次 rev 2.3 只冻结 §5.7 host grant registration/revoke handshake，其他序列化、Tauri command name 与 process supervision 决定仍保留未知。
- 目标：冻结一个**窄范围、host-only** 的 grant 注册/撤销 wire 与 session 绑定语义，
  使 HOST-ISSUER-1 能实现"用户选择 → host 签发 → 注册受信 grant → 注入 Core → Core 校验并消费"。
  本 Task **只做契约设计**，不实现 runtime、不改产品代码。

## Acceptance Criteria

- [x] AC1 **PASS**：§5.7 冻结 HostControl session handshake、导入/导出注册与撤销 request/result/error；明确 React/WebView 不可调用与 Core 拒绝规则。证据：契约 §5.7、`verification/HOST-ISSUER-1-C1/compatibility-impact.md`。
- [x] AC2 **PASS**：grant 绑定 host/Core session；关闭、断线、轮换与 Core restart 的失效语义及 revoke 立即生效边界已定义。证据：契约 §5.7。
- [x] AC3 **PASS**：注册与 §10.3 `ExportTargetRef` / §10.4 `ImportSourceRef` 严格对应；无 ref 字段或签名输入变化；`REF_*` 原样保留。证据：契约 §5.7、§10.3、§10.4 与兼容说明。
- [x] AC4 **PASS**：重复/未知 grant、host/Core session 不符、scope、过期/撤销均有稳定 code/category 和拒绝零副作用要求。证据：契约 §5.7 错误表。
- [x] AC5 **PASS**：§12 只授权 `src/bootstrap/core_service.py` 与 `tests/core/**`；排除 React/WebView、Tauri command/ACL、Schema/migration、依赖及额外产品行为。证据：契约 §12。
- [x] AC6 **PASS**：逐条对照 HOST-ISSUER-1 AC1–AC7、§10.3、§10.4、§5.6，结论为 wire 足以承载 host 签发与注入，且未定义 grant 上限/多选等产品策略。证据：`verification/HOST-ISSUER-1-C1/coverage-matrix.md`。
- [x] AC7 **PASS**：变更仅在契约、Task、Handoff、`verification/HOST-ISSUER-1-C1/**`；未实现 runtime，未改变 P11/P13-C1/P16-C1/P12-C1 冻结 wire。证据：最终 `git diff --name-only 6a5051dcafa549f200730a4f9824d83d187f07a2..HEAD`。
- [ ] AC8 **PARTIAL**：固定提交、Handoff 与工作区/主仓/范围记录完成；非作者 Review 与 Coordinator 集成尚未执行，按要求保持 `NOT_RUN`，本 Task 不标 `done`。证据：本 Task 交付/运行记录与 Handoff。

## 允许修改范围

- **唯一契约文件**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（本 Task 的显式修订授权）。
- 本 Task（`doc/tasks/HOST-ISSUER-1-C1.md`）、`doc/handoffs/HOST-ISSUER-1-C1-*.md`、`verification/HOST-ISSUER-1-C1/**`。
- 只读引用：`doc/tasks/HOST-ISSUER-1.md`、`verification/HOST-ISSUER-1/**`、`doc/tasks/P09-FU2.md`、`doc/tasks/P16.md`、
  `src/bootstrap/core_service.py`、`src/bootstrap/core_assembly.py`、`src/infrastructure/resource_channel/**`、
  `apps/desktop/src-tauri/src/{core_bridge,library_bridge}.rs`、`doc/09_COLLABORATION.md`。
- 写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1`；禁止原位覆盖主仓任何文件。

## 禁止范围

- 不实现 runtime / 产品代码（`src/**`、`apps/**`、`packaging/**` 只读）；不改 Schema/migration；不新增依赖。
- **不得**设计任何"WebView 可调用注册命令"的方案（直接违反受信 host 边界）。
- 不修改 `P11_LONG_TASK_LIFECYCLE_CONTRACT.md`；不改变 P13-C1/P16-C1/P12-C1 已冻结 wire。
- 不触碰 Legacy、用户数据、主仓 dirty/untracked、既有 worktree；不 push、不 merge（集成由 Coordinator 执行）。
- 若注册通道的**产品级**语义需要取舍（例如 grant 上限、是否允许多来源同时注册），**停止**并转
  `BLOCKED_WAITING_EXTERNAL_DECISION`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 host-only 边界 | 静态核对 §5.7 envelope、私有 Core 通道与 public dispatcher 拒绝规则 | 只读契约/代码 | PASS（契约定义）；runtime NOT_RUN | §5.7、`verification/HOST-ISSUER-1-C1/compatibility-impact.md` |
| AC2 session 绑定 | 核对 Core/host session 生命周期及关闭/轮换/restart 语义 | 只读契约/代码 | PASS（契约定义）；runtime NOT_RUN | §5.7 |
| AC3 ref 一致性 | 比对 §10.3/§10.4 字段、签名输入与 `REF_*` | 只读契约/代码 | PASS（静态对照）；runtime NOT_RUN | §5.7、§10.3、§10.4、`verification/HOST-ISSUER-1-C1/compatibility-impact.md` |
| AC4 错误面 | 逐类核对拒绝 code/category 及无 mutation/无 IO 要求 | 只读契约/代码 | PASS（契约定义）；runtime NOT_RUN | §5.7 错误表、`verification/HOST-ISSUER-1-C1/compatibility-impact.md` |
| AC5 授权边界 | 检查 §12 窄 allowlist 与排除项 | 只读契约 | PASS（路径授权已界定） | §12 |
| AC6 覆盖充分性 | HOST-ISSUER-1 AC1–AC7、§10.3/§10.4/§5.6 逐条映射 | 只读文档/代码 | PASS（静态覆盖）；implementation NOT_RUN | `verification/HOST-ISSUER-1-C1/coverage-matrix.md` |

## 依赖、风险与阻塞

- `depends_on`：P09-FU2（`done`，Core 侧 seam 与 `REF_*` 校验）、P16（`done`，`ExportTargetRef` Core 侧校验）。
- 风险一（安全，最高）：该通道一旦被 WebView 触达，**任何** grant 都可被伪造 → 必须设计为**host-only**并给出拒绝机制。
- 风险二（范围）：Core 侧改动必须**最小**（只补路由与 session 绑定），不得借机重构或扩大命令面。
- 风险三（并发写）：本 Task 与 **HOST-ISSUER-1** 都涉及 `core_service.py` 的**不同**改动面；
  HOST-ISSUER-1 当前 `blocked` 且未集成，**本 Task 完成并集成后**才恢复它（Coordinator 负责 merge 基线）。
- 产品级取舍阻塞：无。本契约未裁定 grant 数量上限或用户多选策略。
- Gate 遗留：固定提交与 Handoff 可完成；非作者 Review、Coordinator 集成及 HOST-ISSUER-1 恢复仍待后续执行。

## 交付与运行记录

- 2026-10-16 Owner 认领：worktree G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1，分支 codex/HOST-ISSUER-1-C1-grant-registration-contract，base/初始 HEAD=6a5051dcafa549f200730a4f9824d83d187f07a2；初始 worktree clean，Git common directory=G:/CODEX/New Manga/.git。Task front matter 原 base_commit=2eaa324... 与用户明确坐标/实测 HEAD 不符，已按实测改正；未改主仓。
- 源事实复核：HOST-ISSUER-1 blocker assessment 在本 Task worktree 与主仓均不存在；从只读来源 worktree G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1 的 commit fa270d85d09a6d6781ea76d4d620e70679781f4b 读取，文件由 bacf151b7f4fd61f5b34666b96a444ee95030874 引入。原文件 SHA-256 与本 Task 的 source-pin 一致：b24551e2a27e5d3ca85b94976c3f3aa7aa01625aa39d2b60e0b63c7898225bd6；未修改来源 worktree。
- 固定交付：契约/覆盖对照/兼容性说明提交 af6fa705de54489ce32811cdc8dd3be51a1fd999（delivery head）；Handoff 提交 0603263b1e8e0785c80687e1de0ed891917c1372；blocker source-pin 提交 40afd0b67afa0ab702033bd73489228e064d08e1。Handoff：doc/handoffs/HOST-ISSUER-1-C1-codex-af6fa705d.md。
- 文档静态核验：各 Canonical Evidence 行的 SHA-256 均由当前 worktree 的 Get-FileHash -Algorithm SHA256 计算；各 commit 均包含所列文件。source-pin 与来源 SHA-256 相同。提交前 git diff --cached --check PASS。
- Review：尚无非作者 Review；Coordinator integration 未执行，integration_commit=null。按协作 Gate 保持 Task in_progress，AC8 为 PARTIAL。
- Runtime/Core/Tauri/WebView 测试与构建：NOT_RUN（本 Task 只修订契约，未改实现；未运行测试）。主仓未写入，未 push。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| C1-contract | AC1–AC5 | doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md | af6fa705de54489ce32811cdc8dd3be51a1fd999 | 6a2f38e0b17062d9d4f1d6ee109b4353b745504a5a6b889148781eee84fa2062 | CANONICAL |
| C1-coverage | AC6 | verification/HOST-ISSUER-1-C1/coverage-matrix.md | af6fa705de54489ce32811cdc8dd3be51a1fd999 | 1f477826d3408dfa5147a3ecd5a6404d789c79281be168862fefb5a3295efec9 | CANONICAL |
| C1-compatibility | AC1–AC4, AC7 | verification/HOST-ISSUER-1-C1/compatibility-impact.md | af6fa705de54489ce32811cdc8dd3be51a1fd999 | c9d8ed662d67e738e0fd9e31380227df096661e0948295c92d27d5e0eb2501ba | CANONICAL |
| C1-handoff | AC8 | doc/handoffs/HOST-ISSUER-1-C1-codex-af6fa705d.md | 0603263b1e8e0785c80687e1de0ed891917c1372 | a4c5da3351c5f08c4abfb4ff86fd80ca0fe8d5de88b6b833131896542f760b57 | CANONICAL |
| H1-blocker | AC6 source fact | verification/HOST-ISSUER-1-C1/source-pins/host-issuer-blocker-assessment.md | 40afd0b67afa0ab702033bd73489228e064d08e1 | b24551e2a27e5d3ca85b94976c3f3aa7aa01625aa39d2b60e0b63c7898225bd6 | SOURCE_PIN |
| H1-task | AC6 source contract | doc/tasks/HOST-ISSUER-1.md | 6a5051dcafa549f200730a4f9824d83d187f07a2 | 996934baa05807244225a0ba3530825d68dba4de8911601abdddc43b73e85eae | SOURCE_PIN |
| P09-task | AC3/AC6 source contract | doc/tasks/P09-FU2.md | 6a5051dcafa549f200730a4f9824d83d187f07a2 | adc5f72e40761bca5f5408670c830d3467fceb03d6a105a1df67b74f37c7b33a | SOURCE_PIN |
| P09-seam | AC3/AC6 source evidence | verification/P09-FU2/host-issuer-and-test-seam.md | 6a5051dcafa549f200730a4f9824d83d187f07a2 | 05156daee56bd9f4a38a3dc3014e6b3ed9361698261f910250572fcc3e0f9132 | SOURCE_PIN |
| P16-task | AC3/AC6 source contract | doc/tasks/P16.md | 6a5051dcafa549f200730a4f9824d83d187f07a2 | 7fe5e5b18a18419f25d5372c8713a5b5c084d81f7764db9acac7099dd43831bd | SOURCE_PIN |
| P16-target-ref | AC3/AC6 source evidence | verification/P16/ac3-target-ref-matrix.md | 6a5051dcafa549f200730a4f9824d83d187f07a2 | a0ef395406ce42d30e422254b862e68900c00f591710eacb7859131eb48e39af | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1 | verification/HOST-ISSUER-1-C1/resource-manifest.json | 拟议新增；由 Owner 认领时创建；closeout 时补写 manifest |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：AC1–AC7 契约静态验收已完成；AC8 尚待非作者 Review 与 Coordinator integration，runtime/build 未运行。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` / 本 Task 导航在释放时同步。
