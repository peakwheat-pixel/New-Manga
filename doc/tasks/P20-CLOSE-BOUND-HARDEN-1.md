---
id: P20-CLOSE-BOUND-HARDEN-1
title: sidecar 关闭 deadline 与 worker 生命周期加固
kind: fix
governance_version: 2
status: proposed
approval: user_authorized_20261018_final_close_hardening
blocked_by: null
suggested_owner: Antigravity
owner: null
reviewer: Codex
depends_on: [P20-CLOSE-BOUND-1]
base_commit: 835f4bb17df565581a76cf66062760cdd3c85a9e
branch: null
worktree: null
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
- 本 Task 当前 `proposed`，不等于 Owner 已认领或实现获释放。

## 交付与运行记录

- Handoff：待 Owner 认领后创建。
- Review：待固定 delivery head 后由 Codex 独立复核。
- 实际测试：NOT_RUN。

## Canonical Evidence

尚未进入 `in_review`；该表在交付 head 固定后更新。

| evidence_id | AC/Gate | path | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| Proposed worktree | 待 Codex 创建，优先 `G:/CODEX/New Manga.workspace/P20-CLOSE-BOUND-HARDEN-1/` | `NOT_APPLICABLE` | 待创建 | 待记录 | Task 仍 proposed；未创建、未删除资源。 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- `canonical_evidence_status`：`pending`。
- `resource_closeout_status`：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待 Owner 交付和 Review。
- 当前指针清理：待 Task 激活或关闭时由 Codex同步 STATUS/Plan。
