---
id: P15-HOST-1
title: 设置面 G21/G22/G23 专用命令的 Tauri host 侧注册与 Core 2.7 配对（P15 UI 的端到端前置）
kind: feature
governance_version: 2
status: done
approval: coordinator_release_20261017_after_P15_core_chain_complete
suggested_owner: Codex
owner: Codex
reviewer: dsh
depends_on: [P15-C1, P15, P15-CORE-1]
base_commit: 26983c62a2ebeb22e4d963febcd8ea49eec70108
branch: codex/P15-HOST-1
worktree: G:/CODEX/New Manga.workspace/worktrees/P15-HOST-1
integration_commit: 4e0e0055b64342e29c8519a1c840d30de911b610
delivery_head: f80678bbd2314e6548b63585e658d2de2d6c17b5
canonical_evidence_status: complete
resource_closeout_status: complete
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
- [x] **AC2 production-only 与冻结形状**：新命令**只**加入 production face（不改 probe / AC1 验收面的冻结形状）；`PRODUCTION_COMMANDS` 计数与各 `generate_handler!` 列表、capabilities、权限自动生成、`build.rs` 注释**四处同步**；计数断言按**合并后真实值**更新（不得删断言）。基点实际为 30 条 production 命令，新增 17 条后为 47；probe / AC1 `command_allowlist` 仍为 7 / 6。
- [x] **AC3 安全边界（硬红线）**：Secret、明文凭据、认证头、`CredentialRef`、原始响应、请求体、文件系统路径、Host/Session 凭据、异常文本、不透明写引用**不得**出现在 WebView 的**请求、返回、事件、错误**任何一处；错误只走契约 **§9 封闭投影**（`category`/`phase`/`action`/`message_key`，键集**封闭**）；`CredentialRef` 只存在于受信 Host↔Core 交换与 Core 持久配置；`settings_provider_run_snapshot_get` 返回**去路径/去引用**安全投影。
- [x] **AC4 与 Core 实现配对**：把 P15-CORE-1 已实现的 Core 命令接到 host 面（协议 minor **2.7**，按契约 §2 与本次派发指令）；任一 Core 面未就绪时必须**失败关闭**（`SETTINGS_UNAVAILABLE`），**不得**静默降级或本地伪造。契约 §4.2 仍有“Core 2.6”旧文，见风险记录。
- [x] **AC5 验证**：Rust source 与 frozen packaged 两套件**正确口径**下全绿（`--skip packaged_sidecar_tests` → 基线 95；`M2RC1_PACKAGED=1 … packaged_sidecar_tests` → 基线 12）；Core pytest 不回归（基线 508）；前端套件不回归（基线 274）。目标套件结果与额外全量 suite 的失败分别记录于证据。
- [x] **AC6 交付**：固定实现 commit + [Handoff](../handoffs/P15-HOST-1-ece3af6.md) + Canonical Evidence。SHA256 按磁盘字节计算，证据固定于实现 commit；`delivery_head` 为实现提交，不自引用后续文档提交；status 为 `in_review`；未声称独立 Review。

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
| AC1/AC2 | 命令注册与四处同步、冻结面计数 | PowerShell 静态核验 + cargo source | 实现 17 条设置命令与 2 条 host-only Core route；Task AC1 另列的 `credential_put` / `credential_clear` 未实现，范围冲突待裁决；四处同步 PASS | `verification/P15-HOST-1/surface-sync-check.txt`、`rust-source.txt` |
| AC3 | Secret/路径/引用四处边界 + 封闭投影 | cargo source | PASS；闭合投影拒绝引用与未知错误键，host-only route 不进入 WebView 面 | `rust-source.txt`、`host-only-route-scan.txt` |
| AC4 | Core 2.7 配对与失败关闭 | cargo source + packaged | PASS；source 集成验证真实 Core 2.7 设置/凭据 route；packaged 原有 12 项回归通过 | `rust-source.txt`、`rust-packaged.txt` |
| AC5 | Rust source / packaged / `pytest tests/core -q` / 前端 | 见命令 | PASS：99 passed / 1 ignored；12 passed；508 passed；274 passed。额外全量 `pytest tests -q` 失败另列风险 | 各测试日志见 Canonical Evidence |

## 依赖、风险与阻塞

- **前置**：**P15-C1（契约，done）**、**P15（UI，done）**。
- 风险一：**名字或字段漂移**（契约已冻结）→ AC1 逐字比对。
- 风险二：**Secret 经新面泄露** → AC3 硬红线 + 反例测试。
- 风险三：**计数断言过时** → 按合并后真实值更新（历史教训：跨 Task 计数冲突必须更新而非删除）。
- **范围冲突（AC1 未关闭）**：本次派发指令限定 17 条 WebView 设置命令 + 2 条仅 Host→Core 凭据命令；Task AC1 / 契约 §2、§4.1 还要求 WebView 可达的 `credential_put` / `credential_clear`。实现未擅自把它们加进 production 面或虚报 AC1 完成；当前 AC1 保持未勾选，需用户明确这两个输入面是否纳入本切片。基点实际 30 条，按本次 17 条增量应为 47，不是旧记录的 28→45。
- **协议文字漂移**：契约 §2（L16）要求 P15 Core minor 2.7，§4.2（L125）仍写私有凭据命令使用 2.6。本次按 §2 与派发指令使用 2.7；未修改冻结契约，需契约责任人后续协调 §4.2。
- **UI 配对风险**：现有 `NetworkProfilePanel` 对 `settings_network_profiles_test` 未提供契约必填的 `provider_profile_id`。Host 保持缺省不伪造 ID，Core 2.7 会拒绝请求；前端不在本 Task 允许修改路径。
- **额外全量测试观察**：实现前运行的 `pytest tests -q` 为 2187 passed、19 failed、9 skipped；失败位于 providers、reading_export、workbench。它不是本 Task 的 `tests/core` 基线口径，且未在干净基线复跑，不能判断其是否为既存失败；详细原始日志保留。
- 阻塞条件：若 Core 2.7 面未就绪 → 该面**失败关闭**并如实登记，**不得**本地伪造或静默降级。

## 交付与运行记录

- 2026-10-17 Coordinator 释放（dsh, epoch 6）：依据 P15 交付 Handoff 的诚实声明与本 Task 的独立 Review finding #3（**UI 完成 ≠ 端到端可用**）。
- 2026-10-17 Codex 实现：`ece3af6056e25dc51094b3d027f72d654a6f4dd1`（基于 `26983c62a2ebeb22e4d963febcd8ea49eec70108`）。
- Handoff：[P15-HOST-1-ece3af6.md](../handoffs/P15-HOST-1-ece3af6.md)。独立 Review：待 DeepSeek Harness 或其他非作者 Reviewer 执行；未将自检记为 Review。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| P15-HOST-1-RUST-SOURCE | AC2–AC4 / AC5 | `verification/P15-HOST-1/rust-source.txt` | b0b32c912ee85a43f7422e6b45ce017b40885304 | `C58C4091574425A8AA9D1A1BDD4A199EFF3C704F5445CFAF7B37BD7100E26677` | CANONICAL |
| P15-HOST-1-RUST-PACKAGED | AC5 | `verification/P15-HOST-1/rust-packaged.txt` | b0b32c912ee85a43f7422e6b45ce017b40885304 | `ECC2E78E0EF572192A9C2C350170EE703FAEF9E76AFFC6EE33B6F2564E1F034D` | CANONICAL |
| P15-HOST-1-CORE-PYTEST | AC5 | `verification/P15-HOST-1/core-pytest.txt` | b0b32c912ee85a43f7422e6b45ce017b40885304 | `C5232DFE01903B324569B8307AA8CA0F62E53648E348FAD6C020EB08BBE47F6F` | CANONICAL |
| P15-HOST-1-FRONTEND | AC5 | `verification/P15-HOST-1/frontend-vitest.txt` | b0b32c912ee85a43f7422e6b45ce017b40885304 | `9BA762538A379544000FDEE9D0BB3F4DD7321CDA299A4CB333D44F829DCF1A8C` | CANONICAL |
| P15-HOST-1-FRONTEND-DEPS | AC5 | `verification/P15-HOST-1/frontend-npm-ci.txt` | b0b32c912ee85a43f7422e6b45ce017b40885304 | `29F6675A3AB780F80D47A2DD380463339C72902B83754C1B58E01972D65CA3D4` | CANONICAL |
| P15-HOST-1-HOST-ONLY-SCAN | AC1 / AC3 | `verification/P15-HOST-1/host-only-route-scan.txt` | b0b32c912ee85a43f7422e6b45ce017b40885304 | `4B9489E8863EB9CE4F0FC25B5B36D4D1F2E95E243B5C9E0EE893814BA54D7CBC` | CANONICAL |
| P15-HOST-1-SURFACE-SYNC | AC1 / AC2 | `verification/P15-HOST-1/surface-sync-check.txt` | b0b32c912ee85a43f7422e6b45ce017b40885304 | `A365C34581B011C218D645EE849123A44A7EE7E67C51624876CA5CC29F25F2E2` | CANONICAL |

| P15-HOST-1-REVIEW-R1 | AC1–AC6 | `verification/P15-HOST-1/dsh-review-r1.md` | `4e0e0055b` | `424bd58133868792057b8787d2be86b2204c29c9b3a732aa6440990c7cafeeb1` | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree + junctions | G:/CODEX/New Manga.workspace/worktrees/P15-HOST-1 | PRESERVE_REFERENCED | 同源保留供 Review | verification/P15-HOST-1/resource-manifest.json (SHA256 `A00BD6DE0F036735E00601C69887ECA91D977C09EBB21C8708AAB203954039FD`) | 两个 junction 均确认保留；未删除/重建 `target/core-sidecar` 或 `frontend/dist` |

## Closeout Record

- Closeout date / Coordinator：2026-10-17（dsh, epoch 6）。Reviewer=**dsh**（`route-agent.py` 路由；Owner=Codex 已机器排除）。
- canonical_evidence_status：`complete`。resource_closeout_status：`complete`（worktree `PRESERVE_REFERENCED`）。删除/迁移/归档：0。
- 交付：`done`。集成 `4e0e0055b64342e29c8519a1c840d30de911b610`（`--no-ff`，**无冲突**）；delivery_head（分支实际 HEAD）`f80678bbd2314e6548b63585e658d2de2d6c17b5`。**pin 已在主仓库复算 0 条**（RV-P15-04）。
- **独立复核（我亲做）**：**host-only 红线多证据封死**——全仓 `rg` 仅命中 `library_bridge.rs` 两处常量、显式 `pub const P15_HOST_ONLY_COMMANDS: [&str; 2]`、**不在** `PRODUCTION_COMMANDS`、**不在**任何 `generate_handler!`、并有专门测试 `p15_core_credential_commands_are_host_only`；**四处同步**以 `surface-sync-check.txt` 记录且 **Owner 用 `git show` 核实基线**（`26983c62a` 为 30 → `30+17=47`）：`PRODUCTION_COMMANDS=47`、`P15=17`、**probe=7 / AC1=6 冻结面未污染**、`generate_handler` 块 7/6/47、ACL 54/54、总 permissions **56**、**P15 capabilities 17/17**、4 个生成 schema 均含 P15 名、缺失项为空。**我亲测**：Rust source **99/0/1**（设 `M2RC1_PYTHON` 后；与该变量缺失时的**假失败**已辨明——main 上同样 panic，与本次交付无关）、Core **508**；packaged **12/0**、前端 **274** 与 Owner 日志一致。
- **本 closeout 释放 2 项跟进**：**P15-C1-FU2**（契约 §4.2 的 minor 文字漂移 2.6→2.7，**Owner 上报属实**）与 **P15-HOST-2**（契约 §4.1 的 WebView 可达凭据入口 `PutCredential`/`ClearCredential` + **接线 host Credential Manager 通道**——当前 `bind/clear_profile_credential` 为 `#[allow(dead_code)]` 且返回 `unavailable("P15 credential channel is unavailable")` 的**失败关闭桩**，诚实但**端到端不可用**）。
- **登记（与本 Task 无关的既有事实）**：全量 pytest（非 `tests/core`）`19 failed / 2187 passed / 9 skipped`，失败集中在**本次未触碰**的 `tests/workbench/**` 等 → **既有**；本项目**正式 Core 基线为 `tests/core`（508）**。Rust source 口径**必须设 `M2RC1_PYTHON`**（Python 3.12.3），否则 `library_bridge` 测试假失败。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 同批同步。
