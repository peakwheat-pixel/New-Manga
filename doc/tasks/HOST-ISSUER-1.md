---
id: HOST-ISSUER-1
title: Tauri host 引用签发能力（ImportSourceRef / ExportTargetRef 的 issuer 与受信注入）
kind: feature
governance_version: 2
status: blocked
approval: coordinator_release_20261016_tauri_host_issuer
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P09-FU2, P16, HOST-ISSUER-1-C1]
base_commit: 03412b6558aa1ba9bf0ed109ae41c0e3874f5068
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
