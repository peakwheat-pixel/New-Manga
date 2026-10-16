---
id: HOST-ISSUER-1
title: Tauri host 引用签发能力（ImportSourceRef / ExportTargetRef 的 issuer 与受信注入）
kind: feature
governance_version: 2
status: in_review
approval: coordinator_release_20261016_tauri_host_issuer
suggested_owner: Codex
owner: Codex
reviewer: null
depends_on: [P09-FU2, P16, HOST-ISSUER-1-C1, HOST-CORE-1]
base_commit: 2eaa3241295e1f483eabf640289a4bea4126370c
branch: codex/HOST-ISSUER-1-tauri-ref-issuer
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1
integration_commit: null
delivery_head: 2ad590a31ac2271db7de45f349d94eeaa494775c
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/HOST-ISSUER-1
---

# HOST-ISSUER-1：Tauri host 引用签发能力

## 来源与目标

- 来源（已冻结）：
  - 契约 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` **rev 2.3**：
    **§10.4 `ImportSourceRef`**（读引用）与 **§10.3 `ExportTargetRef`**（写引用）均由 **受信 Tauri host 签发**；
    **§5.7 `HostControl`** 冻结受信 host-only stdio envelope；**React/WebView 不得接收引用或其背后路径**；
    §12 明确 **"Host issuer 必须由独立 Task 授权"**。
  - P09-FU2（`done`）已实现 Core 侧的 **注入 seam** 与全部 `REF_*` 校验；P16（`done`）已实现 `ExportTargetRef` 的 Core 侧校验。
  - 影响：**P12（书架导入）与 P19（四页 E2E）的真实端到端**在 issuer 缺失时无法验证
    （P18 实测证据：`verification/P18/terminal-matrix.csv`）。
- 目标：在 **Tauri host（Rust）侧**实现引用签发与受信注入，使真实产品链路
  "用户选择 → host 签发 → 注册受信 grant → 注入 Core → Core 校验并消费" 成立。
- **授权依据**：契约 §5.6 明确其**不**增加 Tauri command name；
  契约状态表把 `Tauri command names` 标为 **`UNKNOWN / NOT_IN_SCOPE`**；故本 Task 由 **Task 本身**授权，
  并**必须**遵守既有**宿主同步纪律**（见 AC6）。HostControl 操作保持 Rust-only；仅新增不携带路径或 ref 的安全用户动作入口。

## Acceptance Criteria

- [x] AC1 **PASS** — **导入来源签发**：用户通过 **OS 原生选择**（图片文件 / 文件夹直接子项 / PDF）后，
  host 登记**受限** grant（单一来源、只读、可过期、可撤销）并生成 `ImportSourceRef`
  （字段与语义**严格等于**契约 §10.4，**不得新增字段**）。
- [x] AC2 **PASS** — **导出目标签发**：用户通过 **OS 原生保存**选择目标后，host 登记**单目标 + 单次调用**的写 grant，
  生成 `ExportTargetRef`（300 秒**绝对过期**、不滑动续期、一次消费），语义**严格等于**契约 §10.3。
- [x] AC3 **PASS** — **HMAC key 与 host session 生命周期**：key 的生成 / 安全存储 / 加载 / 轮换或失效策略；
  host session 标识与绑定；**撤销**路径；key **不得**进入 WebView 或前端可见面。
- [x] AC4 **PASS** — **受信 host→Core 注入（不经 WebView）**：ref 仅经可信 host→Core 通道传递并注入 Core 的既有 seam；
  **React/WebView 不得接收** ref 或其背后路径（须有**负向证据**）。
- [x] AC5 **PASS** — **HostControl 拒绝码可观测性**：普通 JSON-RPC 对 HostControl 操作被拒为 `HOST_ONLY_REQUIRED`；host 保留 `HOST_SESSION_INVALID` 与 `CORE_SESSION_MISMATCH`；Core 拒绝不调用 seam。
- [x] AC6 **PASS** — **ACL / capability 与宿主同步纪律**：新增用户动作命令同步更新 Tauri `command_allowlist`、`generate_handler!` 字面清单、`build.rs` app-manifest 与 `capabilities/**` 声明（同 commit），并有 Rust unit test；**不得**扩大既有命令权限。
- [x] AC7 **PASS** — **安全**：key 与原始路径**不进 WebView**；grant **不可伪造**；越 scope 引用被拒；
  拒绝时**不产生任何目标写入或库写入**（与 Core 侧负向断言对齐）。
- [x] AC8 **PASS** — `cargo build --locked` exit 0；本 Task 12 个新增/相关 Rust 单元测试通过；Python 3.12.3 + 当前源码环境下完整 Rust suite `76 passed / 0 failed / 1 ignored`。唯一 ignored 是既有、需显式启动的性能探针 `perf_chunk_request_digest_cost`。BL-11b 过期 bundle 基线不计入本 Task，且本次不声称 packaged E2E。
- [x] AC9 **PASS** — 实现 head、Handoff 与证据均已固定并提交；独立 Review、Coordinator 集成与集成后验证保持 `NOT_RUN`，故 Task 状态为 `in_review`。

## 允许修改范围

- `apps/desktop/src-tauri/src/**`（host 侧 Rust 实现）
- `apps/desktop/src-tauri/capabilities/**`、`apps/desktop/src-tauri/permissions/**`（ACL/权限）
- `apps/desktop/src-tauri/build.rs`、`apps/desktop/src-tauri/Cargo.toml`、`apps/desktop/src-tauri/Cargo.lock`
- 本 Task（`doc/tasks/HOST-ISSUER-1.md`）、`doc/handoffs/HOST-ISSUER-1-*.md`、`verification/HOST-ISSUER-1/**`
- 只读引用：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`、`apps/desktop/src-tauri/src/core_bridge.rs`、
  `src/bootstrap/**`、`src/infrastructure/resource_channel/**`、`verification/{P16,P09-FU2,P18}/**`

写入仅限本 Task worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1`；**禁止原位覆盖主仓任何文件**。

## 禁止范围

- **不得修改** `doc/contracts/**`（rev 2.3 已冻结）；不得自行扩展 wire 或新增 ref 字段。
- **不得修改** `apps/desktop/src/**`（React/WebView 面）—— UI 接线留待 UI Task（P12/P17）。
- **不得修改** Python Core 实现（`src/**` 只读）；Core 侧 seam 已由 P09-FU2/P16 交付。
- 不新增第三方依赖（若 Tauri 官方 dialog/fs 插件**确需**引入，必须在证据中单列理由、版本与安全影响，并仅限官方插件）。
- 不得降低既有 ACL/权限强度；不得把 ref 或路径暴露给 WebView。
- 不触碰用户数据、主仓 dirty/untracked、既有 worktree；不 push、不 merge（集成由 Coordinator 执行）。
- 若需要**产品级交互取舍**（例如是否允许多选、是否允许文件夹递归），**停止**并转 `BLOCKED_WAITING_EXTERNAL_DECISION`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 HostControl issuer | 原生 picker、注册/撤销、ImportPages/StartExport 内部注入；ref signature/vector tests | Windows PowerShell；Tauri host + Core 2.3 contract | PASS：实现按 direct-child stdio；12 项 host tests 通过。打包 HostControl E2E `NOT_RUN`（BL-11b） | `verification/HOST-ISSUER-1/cargo-test-host-unit.txt`、`ac7-key-and-ref-security.md` |
| AC3 session/key | CSPRNG credential/key、双 session 绑定、关闭与轮换 | Rust unit tests；Core source pins | PASS：HMAC/canonical vectors 与双 session envelope 断言通过；key 仅 session 内存态 | `cargo-test-host-unit.txt`、`ac7-key-and-ref-security.md` |
| AC4 不入 WebView | WebView 源码与 capability 负向扫描；summary DTO / command-surface tests | Windows PowerShell / ripgrep / cargo | PASS：前端源码敏感字段零匹配；host-only 操作名未暴露 | `verification/HOST-ISSUER-1/ac4-webview-negative.md` |
| AC5 拒绝处理 | 三拒绝码 decode test + HOST-CORE-1 no-seam negative tests | Rust unit + 已完成的 Core evidence | PASS：三码原样保留；Core 逐例断言 seam 未调用 | `verification/HOST-ISSUER-1/ac5-host-denials.md` |
| AC6 宿主同步 | command allowlist / generate_handler / build.rs manifest / capabilities | `cargo test ... app_acl_manifest_is_generated_and_enforced` | PASS：四处同 commit；生产面测试与 ACL manifest test 通过 | `cargo-test-acl-sync.txt`、`main.rs` surface tests |
| AC7 安全 | HMAC vectors、scope 拒绝、Core 既有 REF_* zero-side-effect evidence | Rust unit + P09-FU2/P16 evidence | PASS：host vectors、Core 拒绝矩阵通过；打包产品 E2E `NOT_RUN` | `verification/HOST-ISSUER-1/ac7-key-and-ref-security.md` |
| AC8 构建与测试 | `cargo build --locked`；`cargo test --locked`；`cargo test ... host_` | Windows PowerShell；Python 3.12.3 T1.1.1 env；显式当前 worktree `M2RC1_SRC_ROOT` | PASS：build exit 0；12 focused tests 通过；suite 76/0/1 exit 0。另有 BL-11b packaged baseline 58/6/1 | `cargo-build-locked.txt`、`cargo-test-host-unit.txt`、`cargo-test-full-python312.txt`、`bl11b-status.md` |
| AC9 固定交付 | `git rev-parse HEAD`；Handoff 与 scope/status 核对 | 当前 branch/worktree | PASS：实现提交固定；Review/Coordinator integration `NOT_RUN` | 当前 Handoff 与最终 Git 记录 |

## 依赖、风险与阻塞

- `depends_on`：P09-FU2（`done`，Core 导入 seam 与校验）、P16（`done`，`ExportTargetRef` Core 侧校验）。
- 风险一（安全）：HMAC key 的存储与轮换是**最高风险项**；key 一旦泄漏即可伪造任意引用 → 必须证明 key 不进 WebView、不可从前端读取。
- 风险二（范围）：契约 §5.6 明确不增加 Tauri command name，但**真实产品必须有一个 UI 可触发的入口**；
  本 Task 只实现**最小**host 入口，**不得**借此实现导入/导出 UI（属 P12/P17）。
- 风险三（构建）：Rust/Tauri 构建可能耗时或受本机环境影响；若无法构建，须给**原始失败证据**并标 `BLOCKED`，不得伪造。
- 当前阻塞：无架构阻塞。HostControl 接收端已由 `HOST-CORE-1` 完成；本 Task 只实现 Rust/Tauri host client。打包 sidecar 与协议 2.3 源码匹配的 BL-11b 仍未解决，HostControl packaged E2E 未运行。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 5）：base=`03412b6558aa1ba9bf0ed109ae41c0e3874f5068`；
  依据契约 §12"Host issuer 必须由独立 Task 授权"+ P09-FU2/P16 已就绪的 Core 侧 seam；
  已核实契约状态表将 `Tauri command names` 标为 `UNKNOWN / NOT_IN_SCOPE`，故**无需** M2-C1 契约修订，
  但**必须**遵守既有宿主同步纪律（AC5）。
  Owner 按 DIR-2 路由为 **codex**（`runtime.json` 中 `zcode = UNKNOWN` 不可用；
  按 AGENTS.md"React UI/UX 由 ZCode 主责，**除非 Task 另行明确分配**"，本 Task 明确分配 host 平台能力给 codex）。
- Owner Reality Check（2026-10-16）：实际 worktree 起点=`2eaa3241295e1f483eabf640289a4bea4126370c`，是 Task 原登记 base `03412b6558aa1ba9bf0ed109ae41c0e3874f5068` 的直接子提交；按用户坐标更新本 Task `base_commit`，无分支切换或历史改写。
- 阻塞判定（2026-10-16，Codex）：Rust `StdioLibraryChannel` 只能调用 JSON-RPC dispatcher；Core `_register_*` / `_revoke_*` 是当前 Core 进程内私有方法，无 dispatcher 路由。资源 `host_bridge` 是独立 sidecar，不持有 Import/Export registries。AC1–AC7 因此 BLOCKED；不得通过前端命令或第二个 Core 进程绕过。要求的可信注册 transport 超出冻结的允许路径。
- cargo 验证（2026-10-16）：`cargo build` 与 `cargo test` 均 exit `101`，在 `build.rs` 因缺失 ignored `target/core-sidecar/core-sidecar` 产物提前失败；Rust tests 未启动。专用打包 Python 环境、`frontend/node_modules`、`frontend/dist` 在本 worktree 不存在；未安装依赖或生成 sidecar。
- 证据提交：`bacf151b7f4fd61f5b34666b96a444ee95030874`（阻塞分析、Cargo 原始日志、WebView 静态扫描）。
- Task 状态：`blocked` / `BLOCKED_WAITING_EXTERNAL_DECISION`；实现、Review 和集成都未完成。无新增 Rust 命令、权限或依赖；未引入官方 Tauri dialog/fs plugin。
- 指针同步：`doc/STATUS.md` 仍显示本 Task 为 `ready`；该文件不在本次明确的 allowed_paths 内，未修改。Coordinator 需在获得范围授权后同步状态指针。
- Handoff：`doc/handoffs/HOST-ISSUER-1-codex-bacf151.md`（阻塞交接；无实现 head）。
- Review：`NOT_RUN`（没有实现 head；Owner 不自审）。
- Coordinator 集成：`NOT_RUN`。
- 实际测试：`cargo build`、`cargo test` 均 exit `101`（前置 sidecar 缺失）；WebView 源码静态扫描无匹配、ripgrep exit `1`（预期）。

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
- **2026-10-16 merge resolution（Coordinator, dsh；Merge Conflict 规则：语义级解析，非 ours/theirs）**：
  把 `main`（含前置契约 HOST-ISSUER-1-C1 的 rev 2.3 与治理更新）并入本分支以恢复 HOST-ISSUER-1 时，
  唯一冲突为 `doc/tasks/HOST-ISSUER-1.md` 的 frontmatter。取舍：
  - `depends_on`：分支侧 `[P09-FU2, P16]` vs main 侧 `[P09-FU2, P16, HOST-ISSUER-1-C1]` —— **取 main 侧**（前置契约已集成，保留该边使追溯完整）；
  - `base_commit`：分支侧 `2eaa3241` vs main 侧 `03412b65` —— **取分支侧 `2eaa3241`**，
    因为该 worktree 的**实际起点**是 HOST-ISSUER-1 的释放提交；main 侧的 `03412b65` 是起草时的当时 HEAD（与 P13 Review F2 同类填写误差）。
  其余内容双方均保留。
- **2026-10-16 环境与构建前置（BL-11a/BL-11b）**：本 worktree 已通过 junction 补齐 gitignored 前置
  （`target/core-sidecar`、`frontend/dist`），`cargo build --locked` **exit 0**；
  但 `cargo test --locked` 有 **6 项真实 sidecar 集成测试失败**（`PROTOCOL_VERSION_UNSUPPORTED`/`CORE_UNAVAILABLE`），
  经**主仓对照实验确认同样失败**（58 passed / 6 failed），属**既有 bundle 与协议 2.3 源码不匹配**的债务（BL-11b），
  **非本 Task 引入**。完整证据：`.orchestrator/BL11-ENV-EVIDENCE.md`。
  因此本 Task 的 AC8 判定口径为：`cargo build` 通过 + **新增 Rust 单元测试**通过；6 项真实 sidecar 集成失败归因 BL-11b。
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
## Historical Evidence (初次阻塞交付；不作为本次恢复的 Canonical Evidence)

提交 `bacf151b7f4fd61f5b34666b96a444ee95030874` 包含首次阻塞分析、初次 Cargo 日志与 WebView 静态扫描；其历史版本可直接从 Git 读取。本节不把旧 hash 当作本次交付的工作区 Canonical Evidence。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1 | verification/HOST-ISSUER-1/resource-manifest.json | 保留给独立 Review / Coordinator integration；未清理或迁移 |

## Historical Closeout Record (初次阻塞交付)

- Closeout date / Codex：未关闭；Task 等待外部决策。
- canonical_evidence_status：`partial`（阻塞与运行日志已固定；实现 AC 的证据尚不存在）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：AC1–AC7 因缺少可信 live-Core grant 注入通道而 `BLOCKED`；AC8 两条 cargo 命令 exit 101；AC9 Review / integration `NOT_RUN`。保持 worktree 以供决策后续接。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` / 本 Task 导航在释放时同步。

## Current Delivery Record (2026-10-16)

- 实现 branch：`codex/HOST-ISSUER-1-tauri-ref-issuer`；resume base：`8a990a345c91b4e36cc0bfc6549104b454b24556`；固定实现 head=`2ad590a31ac2271db7de45f349d94eeaa494775c`；Task status=`in_review`。
- 实现：Tauri `StdioLibraryChannel` 对其 direct-child `bootstrap.core_service` 使用独立 HostControl 2.3 envelope，实现六个操作；host session/credential/core session 绑定；native picker 用户动作仅返回摘要；Import/Export ref 在 Rust 内注入到原有 Core 普通业务调用。
- 四处宿主同步：`PRODUCTION_COMMANDS` / `HOST_ISSUER_PRODUCTION_ONLY_COMMANDS`、production `generate_handler!`、`build.rs` app-manifest 与 `capabilities/m2rc1-commands.json` 同步新增三个安全用户动作命令；HostControl 六个操作不出现在 WebView 命令面。
- 依赖：新增官方 `tauri-plugin-dialog`（版本与安全影响见 `verification/HOST-ISSUER-1/dependencies.md`）；未增加插件 JS capability。
- 验证：`cargo build --locked` exit 0；host focused tests 12 passed；ACL manifest test 1 passed；当前 Python source full Rust suite 76 passed / 0 failed / 1 ignored / exit 0。BL-11b 的已记录打包 sidecar 基线 58/6/1 未重建，本 Task 不声称 packaged HostControl E2E。
- 安全与 Core 拒绝：见 AC4/AC5/AC7 证据文件及 HOST-CORE-1 / P09-FU2 / P16 source pins。
- Resource closeout：未触碰用户数据；未迁移、删除、归档或 prune 任何 worktree/环境；保留本 worktree 供独立 Review 与 Coordinator integration。细目见 `verification/HOST-ISSUER-1/resource-manifest.json`。
- Review：`NOT_RUN`（Owner 不自审）；Coordinator integration 与集成后验证：`NOT_RUN`。Task 保持 `in_review`，不得标 `done`。
- 主仓：只读检查；未写入。未 push、未 merge。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| HOSTISSUER-BUILD | AC8 | `verification/HOST-ISSUER-1/cargo-build-locked.txt` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `3519dcd1453e3603f4f2cddc0aa68618e5989498e51196a9a210c50cf402b0f1` | CANONICAL |
| HOSTISSUER-HOST-TESTS | AC1–AC5/AC7 | `verification/HOST-ISSUER-1/cargo-test-host-unit.txt` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `1e6caea4912d34fae283b158048e6cc251f4e4ed719c74d4c3633c64ea1ab875` | CANONICAL |
| HOSTISSUER-ACL-TEST | AC6 | `verification/HOST-ISSUER-1/cargo-test-acl-sync.txt` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `770a2e5027678d212d30cd2571df57f83b5cd2af2b42059bfbe38500fad7b8e8` | CANONICAL |
| HOSTISSUER-FULL-TESTS | AC8 | `verification/HOST-ISSUER-1/cargo-test-full-python312.txt` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `3cda23260ce1a21cf05f26fb7da4f8b73320ba0805bcb760cc363588ef9189aa` | CANONICAL |
| HOSTISSUER-AC4 | AC4 | `verification/HOST-ISSUER-1/ac4-webview-negative.md` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `c7414dfeb4af31bb1eab74fe469cdcaf18a1179f0e1cc81642976c4d8972deac` | CANONICAL |
| HOSTISSUER-AC5 | AC5 | `verification/HOST-ISSUER-1/ac5-host-denials.md` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `120e40785b03c52aeaddd63f3b77431d996562cf41fd0e487e303119a1345662` | CANONICAL |
| HOSTISSUER-AC7 | AC3/AC7 | `verification/HOST-ISSUER-1/ac7-key-and-ref-security.md` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `c6c4ac0e76c3df5eb867c6eb7fa1e00b3b8b32b43d224331bfc73b2157c4245b` | CANONICAL |
| HOSTISSUER-DEPS | Dependency security | `verification/HOST-ISSUER-1/dependencies.md` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `520a61746c51789ca20449c578d4d9c66ba77dfd0194914251cfb6625e4ea7ea` | CANONICAL |
| HOSTISSUER-BL11B | AC8 limitation | `verification/HOST-ISSUER-1/bl11b-status.md` | `3008ee97238451cc46afb0318ecbd446a5dfbe14` | `02b00b029900edda792cfc208e8d543b340bfb8de824f0cf4c4a41cf7775a250` | CANONICAL |
| HOSTISSUER-RESOURCE | Closeout | `verification/HOST-ISSUER-1/resource-manifest.json` | `3008ee97238451cc46afb0318ecbd446a5dfbe14` | `a970b36a62e403da3e97c6f88e0fd6c214fef635caf3482325c2c517e9b9f385` | CANONICAL |
| HOSTISSUER-HANDOFF | AC9 | `doc/handoffs/HOST-ISSUER-1-codex-2ad590a31.md` | `3008ee97238451cc46afb0318ecbd446a5dfbe14` | `d3ddc4d28a266876e6a78c304318720f3f6963f8728b8f688ccdc6b6dc26aa0a` | CANONICAL |
| HOSTISSUER-ISSUER-SOURCE | AC1–AC3/AC7 | `apps/desktop/src-tauri/src/host_issuer.rs` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `612c92b20d0251f2034ed6ef7856c3e8dbb553a7827177bf64eb14dc930a3cbc` | CANONICAL |
| HOSTISSUER-CLIENT-SOURCE | AC1–AC5 | `apps/desktop/src-tauri/src/library_bridge.rs` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `fb818c059870e3bec82071349d37c17ea0000a8089950a12f49f43f552ecabd9` | CANONICAL |
| HOSTISSUER-TAURI-SURFACE | AC4/AC6 | `apps/desktop/src-tauri/src/main.rs` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `b8fe5fd5e064ccaaf4912bd94dd205bc4453d25783a748b1bfa475ec65558c2d` | CANONICAL |
| HOSTISSUER-APP-MANIFEST | AC6 | `apps/desktop/src-tauri/build.rs` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `0ef89e5567905b095503d4200c870872c43bb132695d8ce9da7aa222562e7ab0` | CANONICAL |
| HOSTISSUER-CAPABILITY | AC4/AC6 | `apps/desktop/src-tauri/capabilities/m2rc1-commands.json` | `2ad590a31ac2271db7de45f349d94eeaa494775c` | `4db32b0d0ae22653e8178c1bc907e3d92bafa44518adca346e567f631770f623` | CANONICAL |
| SRC-HOSTISSUER-CONTRACT | AC1–AC7 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `8a990a345c91b4e36cc0bfc6549104b454b24556` | `6a2f38e0b17062d9d4f1d6ee109b4353b745504a5a6b889148781eee84fa2062` | SOURCE_PIN |
| SRC-HOSTCORE-SESSION | AC2 | `verification/HOST-CORE-1/ac2-session-lifecycle.md` | `8a990a345c91b4e36cc0bfc6549104b454b24556` | `adf75e717c05260c548ad041c28e83cbf88c7550ceaeacb1b2c2a2301032c1fe` | SOURCE_PIN |
| SRC-HOSTCORE-DENIALS | AC5 | `verification/HOST-CORE-1/ac4-denials.md` | `8a990a345c91b4e36cc0bfc6549104b454b24556` | `f0c953d59ce7fff3a9c96634e39144902a8cea6ca31c71e641b9dcd5beb4dad8` | SOURCE_PIN |
| SRC-HOSTCORE-DISPATCHER | AC5 | `verification/HOST-CORE-1/ac5-dispatcher-negative.md` | `8a990a345c91b4e36cc0bfc6549104b454b24556` | `f2a8289d71e70a61ec15eea2e24a1b67e67099d7842c25e54f28b3825b8f5a96` | SOURCE_PIN |
| SRC-P09-REF-REJECTIONS | AC7 | `verification/P09-FU2/logs/ac2-ref-rejections-zero-side-effects.txt` | `8a990a345c91b4e36cc0bfc6549104b454b24556` | `0134563175dd8815bddc6895409049ad2e09bc20184f712b73daf35f42e4c7ff` | SOURCE_PIN |
| SRC-P16-EXPORT-REJECTIONS | AC7 | `verification/P16/ac3-target-ref-matrix.md` | `8a990a345c91b4e36cc0bfc6549104b454b24556` | `a0ef395406ce42d30e422254b862e68900c00f591710eacb7859131eb48e39af` | SOURCE_PIN |

注：本表 SHA-256 均按本 worktree 文件使用 `Get-FileHash -Algorithm SHA256` 计算；每行 commit 均经 `git cat-file -e <commit>:<path>` 确认包含该文件。Task 文件本身不列入自引用 hash 表。
