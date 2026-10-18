---
id: P20-CLOSE-BOUND-HARDEN-1
title: sidecar 关闭 deadline 与 worker 生命周期加固
kind: fix
governance_version: 2
status: in_review
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
delivery_head: ed737b5d262d6f7d7b07d8b70900d6af71c11b3c
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

| evidence_id | AC/Gate | path | commit | sha256 | class (CANONICAL / SOURCE_PIN) |
|---|---|---|---|---|---|
| ac1-deadline-cas-monotonic.exit | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac1-deadline-cas-monotonic.meta.json | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 844cfa358ccdba6043aba5fa2f3d924aa31c841bd6adcfb77eea99329a14c7c3 | CANONICAL |
| ac1-deadline-cas-monotonic.stderr.log | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac1-deadline-cas-monotonic.stdout.log | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 8fc7a7ba9f4acd85c8b4756368d219f01ebab97f51c4d0bc0208709b217f4b32 | CANONICAL |
| ac1-overlay-bound.exit | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-overlay-bound.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac1-overlay-bound.meta.json | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-overlay-bound.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | cb40da466fed8816b5847af5ef512a936f6921f4edd90e127094773c9e1ac178 | CANONICAL |
| ac1-overlay-bound.stderr.log | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-overlay-bound.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 60d3d69c936112191e4001a27825b33e018e7dd03f9a7e2312bacf74cfc412eb | CANONICAL |
| ac1-overlay-bound.stdout.log | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-overlay-bound.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 53c7513effcb4a45bdddd14d08fb414e916ea66dc98755cd5eb5caf3650143ab | CANONICAL |
| ac1-shutdown-writes.exit | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-shutdown-writes.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac1-shutdown-writes.meta.json | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-shutdown-writes.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | ec5320a54dd0b9ddd441c41432c9c05cf8c91050ac510ed8a222de6e7a5ee429 | CANONICAL |
| ac1-shutdown-writes.stderr.log | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-shutdown-writes.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac1-shutdown-writes.stdout.log | AC1 | verification/P20-CLOSE-BOUND-HARDEN-1/ac1-shutdown-writes.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 62adf97a57964504168f8ff4aef2b34563d9fa650e19bbeef7cc6b890359a670 | CANONICAL |
| ac2-process-tree-audit.exit | AC2/AC6 | verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac2-process-tree-audit.log | AC2/AC6 | verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4fd27f8763c564c6fb0a4e177d1b73cec4381098aa944acde21528190c60be76 | CANONICAL |
| ac2-process-tree-audit.meta.json | AC2/AC6 | verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 8c8c5ccb36e96786e012b3249f1fe94fc4fe5e36335a8f7225bc719f17ef99f2 | CANONICAL |
| ac3-child-fallback-post-deadline.exit | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-child-fallback-post-deadline.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac3-child-fallback-post-deadline.meta.json | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-child-fallback-post-deadline.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 3b192dc8363e824eae07db7fa72b91f0e52f4271cdb0ee055a1126494efe2fa5 | CANONICAL |
| ac3-child-fallback-post-deadline.stderr.log | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-child-fallback-post-deadline.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 7504d0476652b943248c4b5f009c611289b578d179f3bba7f417c052fa0bdf61 | CANONICAL |
| ac3-child-fallback-post-deadline.stdout.log | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-child-fallback-post-deadline.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 0414ca2d34c2d55625ac50652414c5ca29511def0eff3939551a60f7f3b2171a | CANONICAL |
| ac3-resilient-channel.exit | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-resilient-channel.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac3-resilient-channel.meta.json | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-resilient-channel.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 1941244d718a50546f9ec5cad68d8fb7f734b778c93b3dee638ec9b840d0b4a6 | CANONICAL |
| ac3-resilient-channel.stderr.log | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-resilient-channel.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac3-resilient-channel.stdout.log | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-resilient-channel.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 1a6678dac674ca635169ff20cd21da1f6660267798602314b9e23e84713a18f1 | CANONICAL |
| ac3-stdio-channel-drop.exit | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-stdio-channel-drop.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac3-stdio-channel-drop.meta.json | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-stdio-channel-drop.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 8bdcb0d66ea8b323649c22a572f21dd93161c64e0577d7c68ec7f2e3999e8c86 | CANONICAL |
| ac3-stdio-channel-drop.stderr.log | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-stdio-channel-drop.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | ed820c9b1c856b900c1a5f93f6791b64332efeaf4d7895933337bbd851dcc4cf | CANONICAL |
| ac3-stdio-channel-drop.stdout.log | AC3 | verification/P20-CLOSE-BOUND-HARDEN-1/ac3-stdio-channel-drop.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4a9b5deb86fdfba55160b76b621ba9775d34618b2aa40a74e46c4f0c9df4b4ba | CANONICAL |
| ac4-blocked-reader-worker.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-blocked-reader-worker.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 870967c4c6d18b77072af392670b105e00b328203f03d771f820736f7de126bb | CANONICAL |
| ac4-blocked-reader-worker.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6dbe49b2e5753498db7d13333f95458be027ad4199fff36183aaec08d8f82102 | CANONICAL |
| ac4-blocked-reader-worker.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 92a954609844c06e6592ddb125c9cdc35d8123124f1421fa4566838bb44b0f48 | CANONICAL |
| ac4-blocked-writer-worker.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-blocked-writer-worker.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | b485b521b4bf50fdc5ea37cf326bd4353f516bb02c7849f0720b6afac68a685c | CANONICAL |
| ac4-blocked-writer-worker.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac4-blocked-writer-worker.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | f720f148ad57f730189399c1b29f249cd441a58021ded9845c30658f097cc112 | CANONICAL |
| ac4-child-lock-contention.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-child-lock-contention.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-child-lock-contention.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-child-lock-contention.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | cad38302e5eaef26c1bc43f8c0f2427cd7005e5f886e268927c20237b21663c4 | CANONICAL |
| ac4-child-lock-contention.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-child-lock-contention.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 3ef5b186a5df1c5f45000a9100905c5db4ab928a7e3806f490981941e67ef9aa | CANONICAL |
| ac4-child-lock-contention.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-child-lock-contention.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | a19e097aa6cfb84721de156d2b76de1d2d25576e8ecb687b8c77285e2d4ec7fb | CANONICAL |
| ac4-inner-lock-contention.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-contention.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-inner-lock-contention.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-contention.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 1abeec943d0aa5e4eadb4276eecc6ef63a1a2065b5348de8a5ea158773ae5f3f | CANONICAL |
| ac4-inner-lock-contention.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-contention.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | ad29ca311d80b3a1a920c6025b046108d2aa48668375287605830a909695ed3a | CANONICAL |
| ac4-inner-lock-contention.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-contention.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 84d80426b0661b48267099c8d0f29f4270c70c7e2aa6bd857f7c98834421f0b2 | CANONICAL |
| ac4-inner-lock-fallback-spawn-failure.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-spawn-failure.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-inner-lock-fallback-spawn-failure.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-spawn-failure.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | f99822a6a1c65ed6c0b074fd6056dd511de207c5d4267daf82e051c5cd599219 | CANONICAL |
| ac4-inner-lock-fallback-spawn-failure.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-spawn-failure.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 70cc6871a9e83d18807c1fecd75709fb78cb0131b5ea5bc3f08ab5b1176cf3c4 | CANONICAL |
| ac4-inner-lock-fallback-spawn-failure.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-spawn-failure.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 0670f75ad920c777e070ad3f539ec001df8883c853db3c2672e242e6479c831d | CANONICAL |
| ac4-inner-lock-fallback-timeout.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-timeout.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-inner-lock-fallback-timeout.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-timeout.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 9faac76fe984491962a07775670a1ad29cd8983a7e4de740cbb4831ab089fde3 | CANONICAL |
| ac4-inner-lock-fallback-timeout.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-timeout.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6c60c50ae62491ebdd70c84ef94aea7b9edd1f8fcee5425053e37f228cd04b45 | CANONICAL |
| ac4-inner-lock-fallback-timeout.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-inner-lock-fallback-timeout.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | a56dc7bf291b482e2f92be8fbadefeea06652daba207eac015393b50ee26cb52 | CANONICAL |
| ac4-pending-lock-contention.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-pending-lock-contention.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-pending-lock-contention.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-pending-lock-contention.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 2fa9126c3f5e1c4becd186d23bd9a83def5906db20551024029ad8b431fd71c4 | CANONICAL |
| ac4-pending-lock-contention.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-pending-lock-contention.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 5f41abee566069f3db6e4d45b173649f15550e972eb34520c765b4c0e7a4b100 | CANONICAL |
| ac4-pending-lock-contention.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-pending-lock-contention.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | c3e8843b5099ecd4283e3204ceabe579d4dce314c6e6b4580d4b1b42798f7e9e | CANONICAL |
| ac4-poisoned-child-lock.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-poisoned-child-lock.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-poisoned-child-lock.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-poisoned-child-lock.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 08a73aa6f648978177df2d0e00b1c09473ba6fed3694c24dcbc2611c16fc8958 | CANONICAL |
| ac4-poisoned-child-lock.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-poisoned-child-lock.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6dbe49b2e5753498db7d13333f95458be027ad4199fff36183aaec08d8f82102 | CANONICAL |
| ac4-poisoned-child-lock.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-poisoned-child-lock.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 749f62b329d2f4dea71408a080ba5485c1a2be4ab8324b003e541d1988fb8bd6 | CANONICAL |
| ac4-reader-guard.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reader-guard.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-reader-guard.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reader-guard.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 7a5700d50436f6d198fa7e25a7408ff312ff17451f42ae7378d07f7ef34b80b0 | CANONICAL |
| ac4-reader-guard.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reader-guard.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac4-reader-guard.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reader-guard.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | bd814f514936194bfadb95606ddd76e68e79b3c861ba838e7b38923625b30aa3 | CANONICAL |
| ac4-reentrant-child-reap-check.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reentrant-child-reap-check.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-reentrant-child-reap-check.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reentrant-child-reap-check.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | c710ffe979ec51efb8540a105ec2d5162ed25db46b521d9f285500142c7f7e16 | CANONICAL |
| ac4-reentrant-child-reap-check.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reentrant-child-reap-check.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 999eb7936cbb9ba03273564cfa55e0d27ca7d98e665350a132902808c212e9a4 | CANONICAL |
| ac4-reentrant-child-reap-check.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-reentrant-child-reap-check.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 601f118bcb1455a2a60b774af02897a1ff34df5b2df741d9fd5b0ff50dd684ef | CANONICAL |
| ac4-taskkill-fault-injection.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-taskkill-fault-injection.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-taskkill-fault-injection.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-taskkill-fault-injection.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | ef6308d4fa13f35740f3fe5982dd1c2bc2ff44c8cad2954ebb459f70a2074ff8 | CANONICAL |
| ac4-taskkill-fault-injection.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-taskkill-fault-injection.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 0a8785598b14411379585e06610c7d997b81fee3066c962065956535edd3bcb3 | CANONICAL |
| ac4-taskkill-fault-injection.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-taskkill-fault-injection.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 51265805d760402ae555f9205297cbf24f11a2f3895f0574c28071068d8d2f2b | CANONICAL |
| ac4-wait-timeout-or-kill.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-wait-timeout-or-kill.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-wait-timeout-or-kill.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-wait-timeout-or-kill.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 156d023fe394de89d89e42fb9ead0ce24831e59db5afd28008b83d1f59f6f1de | CANONICAL |
| ac4-wait-timeout-or-kill.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-wait-timeout-or-kill.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac4-wait-timeout-or-kill.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-wait-timeout-or-kill.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 0b98545fc6ce30182c734efc1af3e486bd4bccff5d04eb424f1b2876343a2480 | CANONICAL |
| ac4-writer-pipe-overflow.exit | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-writer-pipe-overflow.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac4-writer-pipe-overflow.meta.json | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-writer-pipe-overflow.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e844e7d9676561e17e949cdf1eb2bebc2ad63abbd6095701db95af9db5926264 | CANONICAL |
| ac4-writer-pipe-overflow.stderr.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-writer-pipe-overflow.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac4-writer-pipe-overflow.stdout.log | AC4 | verification/P20-CLOSE-BOUND-HARDEN-1/ac4-writer-pipe-overflow.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6aadfcf32b99b655129ec15ff70bab2715ebe59b03505bae7d3a41bdd1223a6b | CANONICAL |
| ac8-is-down-write-routing.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-is-down-write-routing.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-is-down-write-routing.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-is-down-write-routing.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 263a3d9af95b5af303b1d3eb76524c4ac503756105fdc84a396058e58dd6b2f4 | CANONICAL |
| ac8-is-down-write-routing.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-is-down-write-routing.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac8-is-down-write-routing.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-is-down-write-routing.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6ff29591a1989f1d85f3647aa91c4f423cf7084af0b5f854c0baf1452c05241d | CANONICAL |
| ac8-max-retries-3.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-max-retries-3.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-max-retries-3.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-max-retries-3.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 5a0f9647c5ece432e10fc46b220b48ec2d9562daa991877dfff79f3bda46824b | CANONICAL |
| ac8-max-retries-3.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-max-retries-3.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6dbe49b2e5753498db7d13333f95458be027ad4199fff36183aaec08d8f82102 | CANONICAL |
| ac8-max-retries-3.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-max-retries-3.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 5138b0683ddf17603e91a05a4f62a5d635a1d009de6683ea932048a1aecbf29e | CANONICAL |
| ac8-pipe-overflow-2mb.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-pipe-overflow-2mb.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-pipe-overflow-2mb.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-pipe-overflow-2mb.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 038cdade45874b7fcb8889e6e8e6294bab9840eb032f103dd5dca3e85a6eea6b | CANONICAL |
| ac8-pipe-overflow-2mb.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-pipe-overflow-2mb.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4178ee3e1e01a0f1d05dac7cba399535afb3b7e53fb7fe662c47bb552b792b47 | CANONICAL |
| ac8-pipe-overflow-2mb.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-pipe-overflow-2mb.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 7cea89a4f6c4100406c34988ea92429185e05511a27c0f89ffd5641f406a03b4 | CANONICAL |
| ac8-r003-cycle-break-and-reap.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r003-cycle-break-and-reap.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-r003-cycle-break-and-reap.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r003-cycle-break-and-reap.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6012e9722d65cc6f81b4017edf59fbde0315c823058df6297116aab88505e050 | CANONICAL |
| ac8-r003-cycle-break-and-reap.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r003-cycle-break-and-reap.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 31f19f7eab74e4126aa6b69d35fa62f0df68e90eb621a336011c89148a761993 | CANONICAL |
| ac8-r003-cycle-break-and-reap.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r003-cycle-break-and-reap.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | b3e67819709244a61b0b92573a8763a8e93a7d8244c6b1041afe51b073f40d8b | CANONICAL |
| ac8-r006-error-presentation.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r006-error-presentation.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-r006-error-presentation.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r006-error-presentation.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 3990d789abbafe4478431d04c52b4aa15e0b9c9336964755039d2d69154f37a0 | CANONICAL |
| ac8-r006-error-presentation.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r006-error-presentation.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 35850e0d81785ea057975dca3a96ca77f5b3c028241b19b764b09825794e4486 | CANONICAL |
| ac8-r006-error-presentation.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r006-error-presentation.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | eae753688a9e0d2c41d670eddd706350a5d2b34dd2ba2061bb9c09014ad99e06 | CANONICAL |
| ac8-r008-heartbeat-recovery.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r008-heartbeat-recovery.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-r008-heartbeat-recovery.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r008-heartbeat-recovery.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 97e0588e9cec6f24957659a4518bb55063f2aa35a927e50bf0dbd0bc5ae60651 | CANONICAL |
| ac8-r008-heartbeat-recovery.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r008-heartbeat-recovery.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e04b1e8c8f74bd118333213d0f6341e7f2264cc8b73deb73fb6fd1be3b47b9e3 | CANONICAL |
| ac8-r008-heartbeat-recovery.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-r008-heartbeat-recovery.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 4afcc27855752a1eedae1e2aacb725887f55643e1a3d5cb683cb024f3a969c1f | CANONICAL |
| ac8-regression-summary.md | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-regression-summary.md | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 56bbc4bb0744643a75429f4133c76d853f0ae478f6ad925ba949af139c3f38ca | CANONICAL |
| ac8-resilient-suite-9-tests.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-resilient-suite-9-tests.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-resilient-suite-9-tests.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-resilient-suite-9-tests.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | b86059ccf25cfb630f1915001d2504f49556d54980270c49047a6b36376295cf | CANONICAL |
| ac8-resilient-suite-9-tests.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-resilient-suite-9-tests.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 49a135a734a1fd7a50b991be11f1b4318ae807348c127e1bfaf31e6be34a4909 | CANONICAL |
| ac8-resilient-suite-9-tests.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-resilient-suite-9-tests.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | a451f8df9f07695f33035934d21884b1fe31f110455f32946feae090f6c340e2 | CANONICAL |
| ac8-shutdown-writes-suite.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-shutdown-writes-suite.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-shutdown-writes-suite.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-shutdown-writes-suite.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | ab42a4b92b62d1e5d2b17ddbd92c0e9265b06d8962d298b5ffa87fa5cb5e26ec | CANONICAL |
| ac8-shutdown-writes-suite.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-shutdown-writes-suite.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6dbe49b2e5753498db7d13333f95458be027ad4199fff36183aaec08d8f82102 | CANONICAL |
| ac8-shutdown-writes-suite.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-shutdown-writes-suite.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 25b0157f518bc788334488a2c0c544a716b85017a933c45944ef59620d378270 | CANONICAL |
| ac8-stdio-channel-drop.exit | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-stdio-channel-drop.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | CANONICAL |
| ac8-stdio-channel-drop.meta.json | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-stdio-channel-drop.meta.json | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | d012f051b39d8daa3057d7e9e17e414e08f978ba47dc22a2a4230fcb08ea33d0 | CANONICAL |
| ac8-stdio-channel-drop.stderr.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-stdio-channel-drop.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 6dbe49b2e5753498db7d13333f95458be027ad4199fff36183aaec08d8f82102 | CANONICAL |
| ac8-stdio-channel-drop.stdout.log | AC8 | verification/P20-CLOSE-BOUND-HARDEN-1/ac8-stdio-channel-drop.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | ab17e679a4842284dd0fde7d6c4894d9d79e6f234f42708c93c4bc6331a30d02 | CANONICAL |
| artifact-lock-fault.exit | AC7 | verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.exit | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9 | CANONICAL |
| artifact-lock-fault.stderr.log | AC7 | verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.stderr.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | CANONICAL |
| artifact-lock-fault.stdout.log | AC7 | verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.stdout.log | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | aaa4ba1da2e8e912e7638d07d9280d9b4bc870ac4e52fedf5032b489a33518e8 | CANONICAL |
| codex-review-r1.md | Gate | verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r1.md | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 521aac1945713264ca75f13f1932268600e847998c42cb3e626c4b2eb853d0d8 | SOURCE_PIN |
| run-ac8-regression.ps1 | Gate | verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1 | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | f7052bd6d05ff4a42c1c15c69484746513fb88882b4b0a788e06c26076e1def7 | CANONICAL |
| SHA256SUMS.txt | Gate | verification/P20-CLOSE-BOUND-HARDEN-1/SHA256SUMS.txt | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | 75dead1c630cce19d7365f172a7fde6710de1e63f17736b039f0b9c768deefe3 | CANONICAL |
| test-artifact-lock-fault.ps1 | AC7 | verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1 | ed737b5d262d6f7d7b07d8b70900d6af71c11b3c | ac3be7672a388a4f099b11ae59feed62b7b0294611c17aec19a9f2f7dad84374 | CANONICAL |

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
