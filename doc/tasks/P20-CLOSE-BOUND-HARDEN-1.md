---
id: P20-CLOSE-BOUND-HARDEN-1
title: sidecar 关闭 deadline 与 worker 生命周期加固
kind: fix
governance_version: 2
status: ready
approval: user_authorized_20261018_final_close_hardening
blocked_by: null
suggested_owner: Antigravity
owner: Antigravity
reviewer: Codex
depends_on: [P20-CLOSE-BOUND-1]
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P20-CLOSE-BOUND-HARDEN-1
---

# P20-CLOSE-BOUND-HARDEN-1：sidecar 关闭 deadline 与 worker 生命周期加固

## 来源与目标

来源为 [`P20-CLOSE-BOUND-1` 的第六轮终审](P20-CLOSE-BOUND-1.md) 与 [`Codex R6 Review`](../../verification/P20-CLOSE-BOUND-1/codex-review-r6.md)。用户授权在原 Task 无论 Review 结果如何都收口；本 Task 只接手未闭合的硬上界、线程生命周期、AC2 证据范围与 hash 对齐，不恢复原 Task 的实施状态。

交付结果：关闭实现对每个前台等待与后台 worker 给出可复核边界；不会在 deadline 后继续清理或静默遗留阻塞线程；审计和证据与真实源码、固定 delivery head 一致。

## Acceptance Criteria

- [ ] AC1：deadline CAS 注册有可证明的单次调用上界；零或已过期 deadline 不被映射成未来预算；并发登记测试覆盖所有竞态。
- [ ] AC2：关闭路径中的同步操作逐 callsite 列表并分类，包括 `lock_timeout_recover`、`join`、`Command::spawn`、`Builder::spawn`、管道读取、`kill` 与通知发送。每项要么由代码保证进入 deadline，要么明确说明不属于 WCET 的系统边界；不得将不计时的部分表述为硬 WCET。
- [ ] AC3：fallback/reaper 到期后不再执行 kill、try-wait、锁等待或错误写入；sleep 与错误处理时间包含在其上限内。
- [ ] AC4：reader/writer 等原工作线程在阻塞 I/O 故障注入下可被安全取消并确认结束，或交付明确、有限且可观测的替代生命周期设计；不得在 worker 可能无限存活时以丢弃 `JoinHandle` 宣称已清理。所有 join 只在已确认线程完成时调用，或具有可验证的有限等待。
- [ ] AC5：`concurrency-lock-audit.md` 与源码调用点一对一，计数单位明确；主路径、锁争用/重入/Drop 分支均有闭式预算，逐项说明后台线程 lifetime 和 spawn cost；总和满足当前 Task 阈值，未纳入项显式列出并标 limitation。
- [ ] AC6：AC2 脚本的残留范围与日志声明一致：独立 workspace Python 不误报；断链覆盖仅在有真实跟踪机制及故障注入证据时宣称。否则将结论严格限制于 runner 后代和隔离根命中。
- [ ] AC7：AC5 direct desktop run 的 OutDir、`ac5.exit`、metadata、console log 与 exact build/head 一致；每个 Canonical Evidence SHA-256 与磁盘文件匹配。若读回或写入任一 artifact 失败（包括调用方 Tee 同时锁定同一 console log），脚本仍须独立写出一致的 `ac5.exit` 与 metadata，且真实进程 exit code 一致；加入 artifact-lock 故障用例。
- [ ] AC8：不回归：R-008 心跳恢复、R-003 拆环与 reap、R-006 错误呈现、`MAX_RETRIES=3`、`is_down` 普通写拒绝/关机写放行、既有 resilient 9 项、stdio drop、shutdown writes、2 MB pipe overflow 用例。

## 允许修改范围

- `apps/desktop/src-tauri/src/library_bridge.rs` 中 deadline、shutdown、fallback/reaper 与相应单元测试。
- `verification/P20-CLOSE-BOUND-1/**`、`verification/P20-CLOSE-BOUND-HARDEN-1/**`、本 Task 与专属 Handoff。
- Task 若需重新映射状态，只由 Codex按治理流程修改 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md`。

## 禁止范围

- 不扩大产品行为，不修改 IPC/共享接口、Schema、ACL 或依赖版本。
- 不触碰 P09-AC3-DELETE-1 工作区内容、前端或用户未提交文件。
- 不把无法纳入单一 deadline 的系统调用隐藏在“0 ms”或“忽略不计”项下；任何阈值/验收口径变化须先获用户裁决。
- 不将本 Task 标成 `ready`，直到 Codex 完成 DAG/STATUS 登记、依赖/范围/Owner/base/worktree 冻结。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC5 deadline/WCET | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop <targeted shutdown tests> -- --nocapture` | Windows、Rust toolchain、隔离子进程 | NOT_RUN | `verification/P20-CLOSE-BOUND-HARDEN-1/` |
| AC4 永久阻塞 I/O 与 kill/reap failure | Rust fault-injection tests，覆盖 reader、writer、taskkill spawn/kill/try_wait 失败 | Windows；仅隔离子进程 | NOT_RUN | stdout/stderr/exit/meta 与 PID/句柄结果 |
| AC6 runner scope | 运行 `test-ac1-overlay-bound.ps1`，并同时启动独立 workspace Python 测试与模拟断链后代 | Windows PowerShell；唯一隔离根 | NOT_RUN | residual candidate 清单与 exit |
| AC7 real desktop close | 交互桌面直接运行 `run-desktop-close-verification.ps1`，不经管道包装 | release build 与 WebView2 可用 | NOT_RUN | 自包含 OutDir、`ac5.exit`、metadata、console log、SHA-256 |
| AC8 regression | resilient 9 项、stdio drop、shutdown writes、2 MB pipe overflow；R-006 UI 沿用有效证据或说明未重跑 | Windows；按用户数据隔离规则 | NOT_RUN | 每条命令独立 stdout/stderr/exit/meta |

## 依赖、风险与阻塞

- 依赖：`P20-CLOSE-BOUND-1` 已 `closed_with_limitations`；其 AC1/AC2/AC4/AC5/AC6 原始未完成状态不得在本 Task 前置状态中抹除。
- 风险：标准 Rust 线程无法被任意强制取消；若采用可取消 I/O、句柄关闭或预建 worker，须以 Windows 故障注入证明退出语义和用户数据安全。
- 本 Task 原为 `proposed`；已由 Coordinator 完成冻结，见下节。

## 范围冻结记录（2026-10-18，Coordinator = dsh，epoch 8）

用户 T3 指令：冻结并释放 `P20-CLOSE-BOUND-HARDEN-1`，未闭合清单取 `verification/P20-CLOSE-BOUND-1/codex-review-r6.md` §7。Coordinator 作为 Active Coordinator 完成 DAG/STATUS 登记与依赖/范围/Owner/base/worktree 冻结；**Codex 保持 Reviewer 身份，不参与本 Task 实现**。

| 项 | 冻结值 |
|---|---|
| 状态 | `ready` |
| Owner | Antigravity |
| Reviewer | Codex（独立；`owner != reviewer`） |
| base_commit | `a04e4ea78d5b33a0f91efcdc06b396391c4b165e`（冻结时的实际 HEAD） |
| 工作路径 | `G:/CODEX/New Manga`（与 P20-CLOSE-BOUND-1 同款；不新建 worktree） |
| 证据目录 | `verification/P20-CLOSE-BOUND-HARDEN-1/` |

**base 说明（诚实记录一次基线漂移）**：r6 §7 给出的恢复点为 `835f4bb17df565581a76cf66062760cdd3c85a9e`，该值在复审当时等于 HEAD。此后 `a04e4ea78`（P09-AC3-DELETE-1 R2 修复）使 HEAD 前进。经实测，`git diff --name-only 835f4bb17..a04e4ea78 -- apps/desktop/src-tauri/src/library_bridge.rs` **为空**，即本 Task 的唯一目标源码在两点之间**完全一致**；故 base 对目标文件等价，`835f4bb17` 的 WCET/审计基线结论仍然适用，不需重做 R6 审计。

### r6 §7 未闭合清单 → 本 Task AC 映射（Owner 必须逐条闭环）

| 来源 ID | 级别 | 未闭合点（精确位置见 r6 §7） | 对应 AC |
|---|---|---|---|
| CBH-01 | P1 | deadline 后 child fallback 仍 `kill`/`try_wait`（`library_bridge.rs:2834-2838`）；reader/writer reaper 超时后 detach 仍可能阻塞的原 worker（`2925-2930,2992-2997`）；六处条件式 `join()`（`2893,2907,2919,2960,2974,2986`）；taskkill reaper kill 错误被忽略且轮询可越过 200 ms（`2403-2419`） | AC3 + AC4 |
| CBH-02 | P1 | CAS retry 无硬上界（`1506-1524,3863-3881`）；同步 `Command::spawn`、输出读、`kill`、六次 `Builder::spawn` 及额外 `join` 未纳入 WCET（`2300,2359-2424,2567-2569,2791-2867,2881-3010,4322-4350`）；审计表 `concurrency-lock-audit.md:26,44,52-70` | AC1 + AC2 + AC5 |
| CBH-03 | P2 | AC2 断链进程覆盖与措辞（`test-ac1-overlay-bound.ps1:226-262,273-280`） | AC6 |
| CBH-04 | P2 | exact-head 运行证据：`ac5-20261018-1555/ac5-metadata.json` 记 `head=e44a589a`；`ac5-20261018-1552/ac5-console.log` 记 294.2243 ms 但缺 exit/metadata | AC7 |
| CBH-05 | P2 | AC5 artifact 写入失败控制流（`run-desktop-close-verification.ps1:208-249`；读回不一致分支 `:216-218`） | AC7 |

### 释放前置的已知限制（Owner 与 Coordinator 必须共同遵守）

1. **AC7 的交互式桌面运行不能由 Antigravity 完成**——`agy` 无法创建 WebView2 窗口（`HRESULT 0x80070578`）。Owner 交付可运行脚本与 Rust 侧改动；AC7 的真实桌面直跑由 Coordinator 在真实交互式桌面执行，且该脚本与 `test-ac1-overlay-bound.ps1` **必须独占运行、不得被管道（`Tee-Object` 等）包裹**。
2. **禁止 `git add -A` / `git add .` / `git commit -a`**：用户工作区有 20 个具名未提交文件，误提交即为违规（上一轮已发生过此类事故）。提交只能逐路径 `git add <明确路径>`。
3. 不改写历史 pin：CBH-04 的旧 artifact 缺 exit/metadata 属既成事实，只允许**追加**正确 head 的新证据，不允许"修正"旧记录使其看起来通过。

## 交付与运行记录

- Handoff：待 Owner 认领后创建（`doc/handoffs/P20-CLOSE-BOUND-HARDEN-1-antigravity.md`）。
- Review：待固定 delivery head 后由 Codex 独立复核，输出 `verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r<n>.md`。
- 实际测试：NOT_RUN。
- 2026-10-18 Coordinator（dsh, epoch 8）完成范围冻结与释放登记。

## Canonical Evidence

尚未进入 `in_review`；该表在交付 head 固定后更新。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| 不新建 worktree | 复用 `G:/CODEX/New Manga` | `NOT_APPLICABLE` | 不适用 | 不适用 | 冻结决定：与 P20-CLOSE-BOUND-1 同款直接在真实仓库工作；未创建、未删除资源。 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`：`pending`。
- `resource_closeout_status`：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待 Owner 交付和 Review。
- 当前指针清理：待 Task 激活或关闭时由 Codex同步 STATUS/Plan。
