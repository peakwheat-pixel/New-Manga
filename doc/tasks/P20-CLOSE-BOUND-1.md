---
id: P20-CLOSE-BOUND-1
title: sidecar 关闭路径的硬上界（强杀/在途无响应下的有界退出与零残留）
kind: fix
governance_version: 2
status: ready
approval: coordinator_derived_from_user_ruling_20261018_split_r009
blocked_by: null
suggested_owner: Antigravity（ZCode CLI 不可用，按项目故障转移顺序）
owner: Antigravity
reviewer: Codex
depends_on: [P20-ISOLATION-1]
base_commit: 40475db61
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P20-CLOSE-BOUND-1
---

# P20-CLOSE-BOUND-1：关闭路径硬上界

## 来源与范围（本 Task 刻意收窄）

Codex 对 `P20-ISOLATION-1` 的三轮独立复审中，**R-008（存活但 IPC 无响应可被心跳发现并恢复）已确认修复**；**R-009 只完成了一半**：`with_channel` 已改为"加锁克隆 `Arc` 后立即释放"，正常强杀路径也有子进程回收证据，但复审指出：

> `R-009` 的完整关闭时限不覆盖**强杀后的阻塞清理**；硬上界尚未完全成立。

按用户 2026-10-18 裁决（"我来补验证，产品修改另立窄 Task"），**本 Task 只做这一件事**：让关闭/退出路径在"在途请求无响应 + 子进程被强杀"的叠加情况下仍然**有界**。不重开已确认项。

**本 Task 不做**：不改心跳探测语义（R-008 已通过）、不重做引用环（R-003 已通过）、不改错误呈现（R-006 已通过）、不扩大产品范围、不改任何 AC 阈值。

## Acceptance Criteria

- [ ] AC1：**有界关闭（核心）**——在以下叠加场景中，关闭/退出必须在**明确上界**内完成，并给出实测数据：① 存在一个已发出但 sidecar 永不响应的在途请求；② 该 sidecar 进程随后被外部强杀（`Stop-Process -Force`）。给出你选择的上界与理由，并说明它是**硬上界**（靠超时强制推进）而非"通常很快"。
- [ ] AC2：**零残留**——上述场景结束后：无残留 `core_service.exe`；无残留 reader/心跳线程导致的进程无法退出；`%TEMP%` 隔离根中的应用进程全部退出。给出进程树核查证据（命令 + 输出 + 时间戳）。
- [ ] AC3：**不回归**——`P20-ISOLATION-1` 已确认的能力不得退化：① 存活但挂起可被心跳发现并恢复；② `drop` 拆环并 reap 子进程；③ 既有 `cargo test --bin m2rc1-desktop resilient_channel`（8 项）与 `stdio_channel_drop`（1 项）全绿。给出复跑命令与输出。
- [ ] AC4：**并发审查**——给出持锁路径清单与每一处的上界说明（哪些路径用 `try_lock`/超时、哪些必须持锁、为何不会互相饿死）；指出并就任何仍可能无限等待的点给出结论（修掉或明确说明为何不可达）。
- [ ] AC5：**真实场景**——在真实桌面会话下，正常关闭窗口后：应用进程与 sidecar 全部退出且无孤儿（给出实测命令与结果）。若某一步只能由 Coordinator 在交互式桌面复跑，**必须**给出可直接粘贴的复跑命令，且不得声称该步已通过。
- [ ] AC6：**证据**——命令、exit code、原始输出、时间戳落盘 `verification/P20-CLOSE-BOUND-1/**`；新增测试必须**真断言行为**（不得空断言、不得只改测量口径）。

## 允许修改范围

- `apps/desktop/src-tauri/src/library_bridge.rs`、`main.rs` 中**与关闭/退出/回收/锁上界相关**的最小改动，以及配套单元测试。
- `verification/P20-CLOSE-BOUND-1/**`、本 Task、`doc/handoffs/P20-CLOSE-BOUND-1-*.md`。
- **不得**修改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/P20.md`、`doc/tasks/P20-ISOLATION-1.md`（含其 Canonical Evidence 表 —— 改动会让治理检查 FAIL）。

## 禁止范围

- 不改共享契约 / IPC 命令 / Schema / ACL / 依赖版本；不降低任何阈值；不改 AC2 冷启动或 AC3 内存口径。
- 不得为了让 AC1 通过而"只改测量口径"或延长判定窗口；上界必须是**实现保证**。
- 不得弱化或跳过既有测试；不得用日志存在替代进程真实退出。
- 不 push；不动用户 43 项未提交改动；GUI/故障注入用 `%TEMP%` 隔离根（禁止放 `apps/desktop/src-tauri/target/**`）；保护用户真实 `%APPDATA%\com.newmanga.m2rc1.desktop` 数据。

## 测试要求

planned：在途无响应请求 + 强杀子进程的叠加用例（Rust 单元/集成测试，含上界断言与进程回收断言）；既有 9 项 resilient/stdio 测试回归；真实桌面关闭退出的进程树核查。

## 依赖、风险与阻塞

- 依赖：`P20-ISOLATION-1`（`with_channel` 释放锁与 `shutdown_and_kill` 已就位）。
- 风险：**持锁与超时组合**可能引入新的时序窗口（例如超时后旧 channel 仍被在途请求引用）；AC4 必须覆盖。
- 已知阻塞：无。

## 交付与运行记录

- 2026-10-18 Coordinator（dsh, epoch 7）按用户裁决从 R-009 拆出本窄 Task；`status: ready`。
- 建议：先由 owner 给出上界设计（AC1/AC4），再实现并补测试。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在关闭时同步。
