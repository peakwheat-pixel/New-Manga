---
id: HOST-ISSUER-1
title: Tauri host 引用签发能力（ImportSourceRef / ExportTargetRef 的 issuer 与受信注入）
kind: feature
governance_version: 2
status: blocked
approval: coordinator_release_20261016_tauri_host_issuer
suggested_owner: Codex
owner: Codex
reviewer: null
depends_on: [P09-FU2, P16, HOST-ISSUER-1-C1]
base_commit: 2eaa3241295e1f483eabf640289a4bea4126370c
branch: codex/HOST-ISSUER-1-tauri-ref-issuer
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1
integration_commit: null
delivery_head: null
canonical_evidence_status: partial
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

- [ ] AC1 **BLOCKED** — **导入来源签发**：用户通过 **OS 原生选择**（图片文件 / 文件夹直接子项 / PDF）后，
  host 登记**受限** grant（单一来源、只读、可过期、可撤销）并生成 `ImportSourceRef`
  （字段与语义**严格等于**契约 §10.4，**不得新增字段**）。
- [ ] AC2 **BLOCKED** — **导出目标签发**：用户通过 **OS 原生保存**选择目标后，host 登记**单目标 + 单次调用**的写 grant，
  生成 `ExportTargetRef`（300 秒**绝对过期**、不滑动续期、一次消费），语义**严格等于**契约 §10.3。
- [ ] AC3 **BLOCKED** — **HMAC key 与 host session 生命周期**：key 的生成 / 安全存储 / 加载 / 轮换或失效策略；
  host session 标识与绑定；**撤销**路径；key **不得**进入 WebView 或前端可见面。
- [ ] AC4 **BLOCKED** — **受信 host→Core 注入（不经 WebView）**：ref 仅经可信 host→Core 通道传递并注入 Core 的既有 seam；
  **React/WebView 不得接收** ref 或其背后路径（须有**负向证据**）。
- [ ] AC5 **BLOCKED** — **ACL / capability 与宿主同步纪律**：新增命令必须同步更新 Tauri 面的
  `command_allowlist` 常量、`generate_handler!` 字面清单、`build.rs` app-manifest **与** `capabilities/**` 声明
  （**同一 commit 内**，沿契约 §5.3/§5.4 既有纪律），并补 Rust unit test；
  **不得**扩大既有命令的既有权限。
- [ ] AC6 **BLOCKED_WAITING_EXTERNAL_DECISION** — **契约一致性**：ref 的字段名、作用域、过期、撤销与拒绝语义与 §10.3/§10.4 **完全一致**；
  若发现契约不足 → **停止**并转 `BLOCKED_WAITING_EXTERNAL_DECISION`，**不得**自行扩展 wire。
- [ ] AC7 **BLOCKED** — **安全**：key 与原始路径**不进 WebView**；grant **不可伪造**；越 scope 引用被拒；
  拒绝时**不产生任何目标写入或库写入**（与 Core 侧负向断言对齐）。
- [ ] AC8 **BLOCKED** — `cargo build` 与 `cargo test` 均已运行，但因缺少 ignored Core sidecar bundle 在 `build.rs` 退出 101；未进入 Rust 编译/单测。原始日志见 `verification/HOST-ISSUER-1/cargo-build.txt` 与 `cargo-test.txt`。
- [ ] AC9 **NOT_RUN** — 无实现交付 head；独立 Review 与 Coordinator 集成均未执行。阻塞 Handoff 与证据提交不等于实现交付。

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
| AC1/AC2 签发 | Rust unit test：签发 ref 字段与契约一致 | cargo | BLOCKED：Rust issuer 与 Core grant 注册无法连通 | `verification/HOST-ISSUER-1/blocker-assessment.md` |
| AC3 key/session | key 生成/加载/撤销用例 | cargo | BLOCKED：无可用的 live-Core 注册通道，未生成 key | `verification/HOST-ISSUER-1/blocker-assessment.md` |
| AC4 不入 WebView | 前端静态负向扫描；实现级负向断言未运行 | PowerShell / ripgrep | 静态扫描 NO_MATCHES；AC4 BLOCKED | `verification/HOST-ISSUER-1/webview-static-scan.txt` |
| AC5 宿主同步 | `command_allowlist`、`generate_handler!`、`build.rs` manifest、capability 核对 | 只读 | BLOCKED：没有新增命令或权限；实现切片未落地 | `verification/HOST-ISSUER-1/blocker-assessment.md` |
| AC7 安全 | 伪造/越 scope 引用被拒、零副作用的 host 端到端测试 | cargo | BLOCKED：既有 Core 侧拒绝证据通过；host issuer 未实现 | `verification/P09-FU2/logs/ac2-ref-rejections-zero-side-effects.txt`、`verification/P16/ac3-target-ref-matrix.md`、`verification/HOST-ISSUER-1/blocker-assessment.md` |
| AC8 构建 | `C:\Users\49745\.cargo\bin\cargo.exe build` | Windows PowerShell；当前 worktree | BLOCKED：exit 101，build.rs 缺少 ignored Core sidecar bundle | `verification/HOST-ISSUER-1/cargo-build.txt` |
| AC8 测试 | `C:\Users\49745\.cargo\bin\cargo.exe test` | Windows PowerShell；当前 worktree | BLOCKED：exit 101，同一 build.rs 前置缺失，Rust tests 未启动 | `verification/HOST-ISSUER-1/cargo-test.txt` |

## 依赖、风险与阻塞

- `depends_on`：P09-FU2（`done`，Core 导入 seam 与校验）、P16（`done`，`ExportTargetRef` Core 侧校验）。
- 风险一（安全）：HMAC key 的存储与轮换是**最高风险项**；key 一旦泄漏即可伪造任意引用 → 必须证明 key 不进 WebView、不可从前端读取。
- 风险二（范围）：契约 §5.6 明确不增加 Tauri command name，但**真实产品必须有一个 UI 可触发的入口**；
  本 Task 只实现**最小**host 入口，**不得**借此实现导入/导出 UI（属 P12/P17）。
- 风险三（构建）：Rust/Tauri 构建可能耗时或受本机环境影响；若无法构建，须给**原始失败证据**并标 `BLOCKED`，不得伪造。
- 阻塞：Core 私有 grant 注册 seam 没有可信 Tauri→live-Core 调用通道；契约 §11 将 runtime serialization、process supervision 与 auth/permission handshake 标为 `UNKNOWN / NOT_IN_SCOPE`。在不修改 Python Core 或改变安全边界的前提下，无法完成本 Task 的核心授权注入；必须等待用户/Codex 决定并另行授权窄范围 Core host-only seam。详见 `verification/HOST-ISSUER-1/blocker-assessment.md`。

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
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-HOST-ISSUER-BLOCKER | AC1–AC7 | verification/HOST-ISSUER-1/blocker-assessment.md | bacf151b7f4fd61f5b34666b96a444ee95030874 | b24551e2a27e5d3ca85b94976c3f3aa7aa01625aa39d2b60e0b63c7898225bd6 | CANONICAL |
| EVID-HOST-ISSUER-CARGO-BUILD | AC8 | verification/HOST-ISSUER-1/cargo-build.txt | bacf151b7f4fd61f5b34666b96a444ee95030874 | 3022e6b8b90fa0a34ca54e7fc5225545f62f9e8647860af9b670fb894bc2538f | CANONICAL |
| EVID-HOST-ISSUER-CARGO-TEST | AC8 | verification/HOST-ISSUER-1/cargo-test.txt | bacf151b7f4fd61f5b34666b96a444ee95030874 | b5efe535d3c787488a3440b2956266a105eb212f7970e4739c625cc0aab3ec63 | CANONICAL |
| EVID-HOST-ISSUER-WEBVIEW-SCAN | AC4 | verification/HOST-ISSUER-1/webview-static-scan.txt | bacf151b7f4fd61f5b34666b96a444ee95030874 | 33c47371529e01c9145a710a45bf0a2f28b786c0b5044ad8a6709b143452c34c | CANONICAL |
| SRC-P09-REF-REJECTIONS | AC7 Core consumer precedent | verification/P09-FU2/logs/ac2-ref-rejections-zero-side-effects.txt | cac219fe79e0d741259d92dae12d896e9d357c6c | 0134563175dd8815bddc6895409049ad2e09bc20184f712b73daf35f42e4c7ff | SOURCE_PIN |
| SRC-P16-TARGET-REJECTIONS | AC7 Core consumer precedent | verification/P16/ac3-target-ref-matrix.md | e2c07fa9b172c7a585653e376f309e3e39abd026 | a0ef395406ce42d30e422254b862e68900c00f591710eacb7859131eb48e39af | SOURCE_PIN |
| SRC-HOST-ISSUER-CONTRACT | AC1–AC7 | doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md | 2eaa3241295e1f483eabf640289a4bea4126370c | b8cadc27572a25ec2785f507ca73dbb3d9b27b1cea6083eed9faa0ff46f82ad4 | SOURCE_PIN |
| SRC-HOST-ISSUER-P09-SEAM | AC1/AC4 | verification/P09-FU2/host-issuer-and-test-seam.md | 2eaa3241295e1f483eabf640289a4bea4126370c | 05156daee56bd9f4a38a3dc3014e6b3ed9361698261f910250572fcc3e0f9132 | SOURCE_PIN |
| SRC-HOST-ISSUER-CORE-SERVICE | AC1–AC4 | src/bootstrap/core_service.py | 2eaa3241295e1f483eabf640289a4bea4126370c | efdfc5207bfb5fd2e560d5d0ccc8983bdaf32e85076f3ab9f2c52cbc7fb7b985 | SOURCE_PIN |
| SRC-HOST-ISSUER-CORE-ASSEMBLY | AC1–AC4 | src/bootstrap/core_assembly.py | 2eaa3241295e1f483eabf640289a4bea4126370c | fada146b20bd9b85cb7754ec8c404361370b7380efd93c337b2be1e9c60984b9 | SOURCE_PIN |
| SRC-HOST-ISSUER-RESOURCE-BRIDGE | AC4 | src/infrastructure/resource_channel/host_bridge.py | 2eaa3241295e1f483eabf640289a4bea4126370c | 74246634ac18178cd1d160b612b37797889ca7aedea7a9916a525b8e0b1569f0 | SOURCE_PIN |
| SRC-HOST-ISSUER-TAURI-CORE-BRIDGE | AC4 | apps/desktop/src-tauri/src/core_bridge.rs | 2eaa3241295e1f483eabf640289a4bea4126370c | 4524c34098e9c52c28369f9950b238b90ce477d12671214d1975be7de90c0b1d | SOURCE_PIN |
| SRC-HOST-ISSUER-TAURI-LIBRARY-BRIDGE | AC4 | apps/desktop/src-tauri/src/library_bridge.rs | 2eaa3241295e1f483eabf640289a4bea4126370c | 27fbc5b298a3e9f2616d9ee083dc8e45978cb638270c782f3abab301a9eab06b | SOURCE_PIN |
| SRC-HOST-ISSUER-TAURI-MAIN | AC5 | apps/desktop/src-tauri/src/main.rs | 2eaa3241295e1f483eabf640289a4bea4126370c | 2b5783e2c1a6377885e66220078610c26861f7be83821b8ae48ee4495964f913 | SOURCE_PIN |
| SRC-HOST-ISSUER-TAURI-BUILD | AC5 | apps/desktop/src-tauri/build.rs | 2eaa3241295e1f483eabf640289a4bea4126370c | bedcd26b063205dfdada5bba6c02e80fbcd455e9258f5986246d5fb0a64774b1 | SOURCE_PIN |
| SRC-HOST-ISSUER-CAPABILITY | AC5 | apps/desktop/src-tauri/capabilities/m2rc1-commands.json | 2eaa3241295e1f483eabf640289a4bea4126370c | 7c605b913fd2e67f12680cd12e1d5b74daf81fb988de15d9a21fd6ff8ba9852b | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1 | verification/HOST-ISSUER-1/resource-manifest.json | 拟议新增；由 Owner 认领时创建；closeout 时补写 manifest |

## Closeout Record

- Closeout date / Codex：未关闭；Task 等待外部决策。
- canonical_evidence_status：`partial`（阻塞与运行日志已固定；实现 AC 的证据尚不存在）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：AC1–AC7 因缺少可信 live-Core grant 注入通道而 `BLOCKED`；AC8 两条 cargo 命令 exit 101；AC9 Review / integration `NOT_RUN`。保持 worktree 以供决策后续接。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` / 本 Task 导航在释放时同步。
