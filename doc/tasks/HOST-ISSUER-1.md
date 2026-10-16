---
id: HOST-ISSUER-1
title: Tauri host 引用签发能力（ImportSourceRef / ExportTargetRef 的 issuer 与受信注入）
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261016_tauri_host_issuer
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P09-FU2, P16, HOST-ISSUER-1-C1, HOST-CORE-1]
base_commit: 2eaa3241295e1f483eabf640289a4bea4126370c
branch: codex/HOST-ISSUER-1-tauri-ref-issuer
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/HOST-ISSUER-1
---

# HOST-ISSUER-1：Tauri host 引用签发能力

## 来源与目标

- 来源（已冻结）：
  - 契约 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` **rev 2.2**：
    **§10.4 `ImportSourceRef`**（读引用）与 **§10.3 `ExportTargetRef`**（写引用）均由 **受信 Tauri host 签发**；
    **React/WebView 不得接收引用或其背后路径**；§12 明确 **"Host issuer 必须由独立 Task 授权"**。
  - P09-FU2（`done`）已实现 Core 侧的 **注入 seam** 与全部 `REF_*` 校验；P16（`done`）已实现 `ExportTargetRef` 的 Core 侧校验。
  - 影响：**P12（书架导入）与 P19（四页 E2E）的真实端到端**在 issuer 缺失时无法验证
    （P18 实测证据：`verification/P18/terminal-matrix.csv`）。
- 目标：在 **Tauri host（Rust）侧**实现引用签发与受信注入，使真实产品链路
  "用户选择 → host 签发 → 注册受信 grant → 注入 Core → Core 校验并消费" 成立。
- **授权依据**：契约 §5.6 明确其**不**增加 Tauri command name；
  契约状态表把 `Tauri command names` 标为 **`UNKNOWN / NOT_IN_SCOPE`**；故本 Task 由 **Task 本身**授权，
  并**必须**遵守既有**宿主同步纪律**（见 AC5）。

## Acceptance Criteria

- [ ] AC1 **导入来源签发**：用户通过 **OS 原生选择**（图片文件 / 文件夹直接子项 / PDF）后，
  host 登记**受限** grant（单一来源、只读、可过期、可撤销）并生成 `ImportSourceRef`
  （字段与语义**严格等于**契约 §10.4，**不得新增字段**）。
- [ ] AC2 **导出目标签发**：用户通过 **OS 原生保存**选择目标后，host 登记**单目标 + 单次调用**的写 grant，
  生成 `ExportTargetRef`（300 秒**绝对过期**、不滑动续期、一次消费），语义**严格等于**契约 §10.3。
- [ ] AC3 **HMAC key 与 host session 生命周期**：key 的生成 / 安全存储 / 加载 / 轮换或失效策略；
  host session 标识与绑定；**撤销**路径；key **不得**进入 WebView 或前端可见面。
- [ ] AC4 **受信 host→Core 注入（不经 WebView）**：ref 仅经可信 host→Core 通道传递并注入 Core 的既有 seam；
  **React/WebView 不得接收** ref 或其背后路径（须有**负向证据**）。
- [ ] AC5 **ACL / capability 与宿主同步纪律**：新增命令必须同步更新 Tauri 面的
  `command_allowlist` 常量、`generate_handler!` 字面清单、`build.rs` app-manifest **与** `capabilities/**` 声明
  （**同一 commit 内**，沿契约 §5.3/§5.4 既有纪律），并补 Rust unit test；
  **不得**扩大既有命令的既有权限。
- [ ] AC6 **契约一致性**：ref 的字段名、作用域、过期、撤销与拒绝语义与 §10.3/§10.4 **完全一致**；
  若发现契约不足 → **停止**并转 `BLOCKED_WAITING_EXTERNAL_DECISION`，**不得**自行扩展 wire。
- [ ] AC7 **安全**：key 与原始路径**不进 WebView**；grant **不可伪造**；越 scope 引用被拒；
  拒绝时**不产生任何目标写入或库写入**（与 Core 侧负向断言对齐）。
- [ ] AC8 **可构建可测**：`cargo build` 与 `cargo test`（或等价的既有 Rust 验证方式）通过并归档**原始日志与退出码**。
- [ ] AC9 固定 head 非作者 Review、Coordinator 集成；未跑项标 `NOT_RUN` / `BLOCKED`。

## 允许修改范围

- `apps/desktop/src-tauri/src/**`（host 侧 Rust 实现）
- `apps/desktop/src-tauri/capabilities/**`、`apps/desktop/src-tauri/permissions/**`（ACL/权限）
- `apps/desktop/src-tauri/build.rs`、`apps/desktop/src-tauri/Cargo.toml`、`apps/desktop/src-tauri/Cargo.lock`
- 本 Task（`doc/tasks/HOST-ISSUER-1.md`）、`doc/handoffs/HOST-ISSUER-1-*.md`、`verification/HOST-ISSUER-1/**`
- 只读引用：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`apps/desktop/src-tauri/src/{core_bridge,library_bridge}.rs`、
  `src/bootstrap/**`、`src/infrastructure/resource_channel/**`、`verification/{P16,P09-FU2,P18}/**`

写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`；**禁止原位覆盖主仓任何文件**。

## 禁止范围

- **不得修改** `doc/contracts/**`（rev 2.2 已冻结）；不得自行扩展 wire 或新增 ref 字段。
- **不得修改** `apps/desktop/src/**`（React/WebView 面）—— UI 接线留待 UI Task（P12/P17）。
- **不得修改** Python Core 实现（`src/**` 只读）；Core 侧 seam 已由 P09-FU2/P16 交付。
- 不新增第三方依赖（若 Tauri 官方 dialog/fs 插件**确需**引入，必须在证据中单列理由、版本与安全影响，并仅限官方插件）。
- 不得降低既有 ACL/权限强度；不得把 ref 或路径暴露给 WebView。
- 不触碰用户数据、主仓 dirty/untracked、既有 worktree；不 push、不 merge（集成由 Coordinator 执行）。
- 若需要**产品级交互取舍**（例如是否允许多选、是否允许文件夹递归），**停止**并转 `BLOCKED_WAITING_EXTERNAL_DECISION`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 签发 | Rust unit test：签发 ref 字段与契约一致 | cargo | NOT_RUN | 无 |
| AC3 key/session | key 生成/加载/撤销用例 | cargo | NOT_RUN | 无 |
| AC4 不入 WebView | 负向断言：WebView 可见面不含 ref/路径 | cargo | NOT_RUN | 无 |
| AC5 宿主同步 | 三处同步 + capabilities 同 commit 的核对 | 只读 + cargo | NOT_RUN | 无 |
| AC7 安全 | 伪造/越 scope 引用被拒、零副作用 | cargo | NOT_RUN | 无 |
| AC8 构建 | `cargo build` + `cargo test`（原始日志 + 退出码） | cargo（本机） | NOT_RUN | 无 |

## 依赖、风险与阻塞

- `depends_on`：P09-FU2（`done`，Core 导入 seam 与校验）、P16（`done`，`ExportTargetRef` Core 侧校验）。
- 风险一（安全）：HMAC key 的存储与轮换是**最高风险项**；key 一旦泄漏即可伪造任意引用 → 必须证明 key 不进 WebView、不可从前端读取。
- 风险二（范围）：契约 §5.6 明确不增加 Tauri command name，但**真实产品必须有一个 UI 可触发的入口**；
  本 Task 只实现**最小**host 入口，**不得**借此实现导入/导出 UI（属 P12/P17）。
- 风险三（构建）：Rust/Tauri 构建可能耗时或受本机环境影响；若无法构建，须给**原始失败证据**并标 `BLOCKED`，不得伪造。
- 阻塞：无预期。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 5）：base=`03412b6558aa1ba9bf0ed109ae41c0e3874f5068`；
  依据契约 §12"Host issuer 必须由独立 Task 授权"+ P09-FU2/P16 已就绪的 Core 侧 seam；
  已核实契约状态表将 `Tauri command names` 标为 `UNKNOWN / NOT_IN_SCOPE`，故**无需** M2-C1 契约修订，
  但**必须**遵守既有宿主同步纪律（AC5）。
  Owner 按 DIR-2 路由为 **codex**（`runtime.json` 中 `zcode = UNKNOWN` 不可用；
  按 AGENTS.md"React UI/UX 由 ZCode 主责，**除非 Task 另行明确分配**"，本 Task 明确分配 host 平台能力给 codex）。
- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无（全部 `NOT_RUN`）。

### 2026-10-16 阻塞上报与 resolution（Owner=codex；Coordinator=dsh）

- **Owner 实测结论**：可信 host **没有任何通道**把 grant 注册进**运行中的** Core，因此 Rust-only 实现无法完成 AC1–AC8。
  关键事实（见 `verification/HOST-ISSUER-1/blocker-assessment.md`）：
  ① `_register_export_target`/`_revoke_export_target`/`_register_import_source`/`_revoke_import_source` 是
  live `CoreServiceServer` 的**私有方法**，**未在 dispatcher 路由**；
  ② Core JSON-RPC 已路由 `ImportPages`/`StartExport`，但**无**注册/撤销命令；
  ③ grant registry 是**该 Core 实例内存态**，第二进程或既有 `host_bridge` sidecar **无法填充**；
  ④ 把注册暴露为 WebView 可调用命令会**破坏** §10.3/§10.4 的受信 host 边界。
- **环境事实**：`cargo build` 与 `cargo test` 均 **exit 101** —— `build.rs` 因 `target/core-sidecar/core-sidecar`
  bundle 缺失而 panic；且专用打包 Python 环境、`frontend/node_modules`、`frontend/dist` 亦缺
  （修复入口：`packaging/m2ac5/build_sidecar.ps1`）。已登记为技术债务 **BL-11**。
- **Resolution（Coordinator）**：建立前置契约 Task **HOST-ISSUER-1-C1**（host→Core grant 注册通道契约），
  冻结 host-only 注册/撤销 wire 与 session 绑定语义（正是 `M2-C1` §11 遗留的 `auth/permission handshake` 项）；
  **本 Task 的 wire 契约冻结并集成后**方可恢复。
- **未集成**：本 Task 的分支 `codex/HOST-ISSUER-1-tauri-ref-issuer`（HEAD `fa270d85`）**保留不合并**，
  待 C1 完成后由 Coordinator 把新版 main 并入该分支再恢复。
- 诚实性确认：Owner **未**伪造任何实现，明确记载"没有变更不能算通过"，且静态扫描仅作基线证据、**不满足** AC4 实现级负向测试。
### 2026-10-16 恢复（Coordinator, dsh）

- **前置已满足**：契约 **rev 2.3 §5.7 `HostControl`** 已冻结并集成（`b9cb0623`）；本分支已并入 main（HEAD `d307503b`），
  唯一冲突按**语义级解析**完成（`depends_on` 取 main 侧含前置契约；`base_commit` 取分支侧实际起点 `2eaa3241`）。
- **`base_commit` 修正**：主仓原值 `03412b65` 是**起草时的当时 HEAD**；本 worktree 的**实际起点**是释放提交 `2eaa3241`，已更正。
- **构建前置（BL-11a，已解决）**：worktree 已通过 junction 获得 gitignored 前置（`target/core-sidecar`、`frontend/dist`），
  **`cargo build --locked` exit 0**（16s）。证据：`.orchestrator/BL11-ENV-EVIDENCE.md`。
- **`cargo test` 口径（重要，AC8 判定依据）**：
  实测 **58 passed / 6 failed**，6 项失败**全部是需要真实 sidecar 的集成测试**，错因 `PROTOCOL_VERSION_UNSUPPORTED` / `CORE_UNAVAILABLE`。
  **主仓对照实验确认同样 58 passed / 6 failed**（失败列表完全相同）→ 属**既有 bundle 与协议 2.3 源码不匹配**的债务（**BL-11b**），**非本 Task 引入**。
  因此 **AC8 判定为**：`cargo build` 通过 **+ 本 Task 新增的 Rust 单元测试**通过；
  这 6 项既有集成失败**不得**计入本 Task 的缺陷，也**不得**用于声称 host issuer 已端到端可用。
- **恢复范围提示**：按 `M2-C1` §5.7 实现 host 侧 `OpenHostSession` / `RegisterImportSource` / `RevokeImportSource` /
  `RegisterExportTarget` / `RevokeExportTarget` / `CloseHostSession`（经 direct-child stdio 的独立 HostControl envelope）；
  **不得**把注册暴露为 WebView 可调用命令；host session credential 与 `core_session_id` 绑定；
  `HOST_ONLY_REQUIRED` / `HOST_SESSION_INVALID` / `CORE_SESSION_MISMATCH` 三拒绝码须有负向证据。
### 2026-10-16 第二次阻塞与 resolution（Owner=codex；Coordinator=dsh）

- **Owner 实证（Coordinator 已逐条核验，全部成立）**：
  1. `HOST-ISSUER-1-C1` 冻结了 §5.7 契约，**但没有交付 Core handler**；契约 §12 原文为
     "**仅授权最小 Core handler/session 改动与 `tests/core/**`，本次不实现 runtime**"；
  2. `src/bootstrap/core_service.py` 对 `HostControl` / `OpenHostSession` / `HOST_ONLY_REQUIRED` 的命中数为 **0**
     —— 当前 HostControl 请求会被当作未知命令拒绝；
  3. 私有 seam 已存在（`_register_export_target` L1491 / `_revoke_export_target` L1509 /
     `_register_import_source` L1515 / `_revoke_import_source` L1551），但**无接收路由**；
  4. Rust `library_bridge.rs` 仍发送 protocol `1.4` 的普通请求。
  → 结论：**Rust-only 改动无法把 grant 注册进 live Core**，Owner 拒绝"写一个接不进去的 issuer 并报告完成"，
  **该判断正确**。
- **Coordinator 自述（规划疏漏与 prompt 错误）**：恢复 HOST-ISSUER-1 时，Coordinator 只确认了"契约已冻结"，
  **未确认"handler 是否已实现"**；且在恢复 prompt 中把 `src/**` 误写为**只读**，
  与 §12 **明确授权** Core handler 改动相矛盾。**本记录为该失误的透明备案。**
- **Resolution（Coordinator）**：建立 **`HOST-CORE-1`**（Core 侧 HostControl handler 实现，
  范围严格等于 §12：`src/bootstrap/core_service.py` + `tests/core/**`），
  **其集成后**方可恢复本 Task（Coordinator 负责 merge 基线）。
- 本 Task 分支保留不合并；未实现任何 Rust 侧改动。
### 2026-10-16 再次恢复（Coordinator, dsh）

- **第二次阻塞的根因已修复**：契约 `M2-C1` §12 只**授权**了最小 Core handler/session 改动却从未实现；
  前置 Task **`HOST-CORE-1` 已实现并集成**（`67ee4a58`），Core 侧的 `HostControl` 接收面（独立命令集、
  session 生命周期、三拒绝码、路由到既有私有 seam）**现已存在于本分支**（已核验：`core_service.py` 的 HostControl 实现命中 20 处；
  `main` 已是本分支祖先）。
- **本次 merge 的语义解析**：3 处冲突按"**保留双方全部记录**"原则处理 ——
  `depends_on` 取 main 侧（现含 `HOST-CORE-1`）；BL-11a/BL-11b 构建前置记录取分支侧；
  第二次阻塞与 Coordinator 失误备案取 main 侧；**残留冲突标记 0**。分支 HEAD `d5ab1e8a`。
- **AC8 口径（不变）**：`cargo build` 通过 + **本 Task 新增 Rust 单元测试**通过；
  6 项真实 sidecar 集成失败归因 **BL-11b**（主仓同现），**不得**计入本 Task 缺陷。
  ⚠️ 注意：由于 **HOST-CORE-1 已把协议抬到 2.3**，bundle 与源码的协议差距**更大**，
  故 BL-11b 的 6 项失败**预期仍在**，仍按上述口径处理。
- **职责边界（本次修正后的正确表述）**：
  - **Core 侧**（`src/bootstrap/core_service.py`、`tests/core/**`）= `HOST-CORE-1` 的交付，**本 Task 只读消费**；
  - **Rust/Tauri 侧**（`apps/desktop/src-tauri/**`）= **本 Task 的实现面**（HostControl 客户端通道 +
    四处宿主同步 + ACL/capability + key/session + Rust 单测）。
  - 恢复 prompt 曾误写为"`src/**` 只读"从而与本 Task 的实际边界不符；**本次已更正**。
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1 | verification/HOST-ISSUER-1/resource-manifest.json | 拟议新增；由 Owner 认领时创建；closeout 时补写 manifest |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：本 Task 全部 AC 尚未执行（`NOT_RUN`）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` / 本 Task 导航在释放时同步。
