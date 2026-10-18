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
base_commit: 8bf3ae30a
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: pending
canonical_evidence_status: complete
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

- [x] AC1：**有界关闭（核心）**——在以下叠加场景中，关闭/退出必须在**明确上界**内完成，并给出实测数据：① 存在一个已发出但 sidecar 永不响应的在途请求；② 该 sidecar 进程随后被外部强杀（`Stop-Process -Force`）。给出你选择的上界与理由，并说明它是**硬上界**（靠超时强制推进）而非"通常很快"。理论绝对硬上界 3.0s，叠加场景实测耗时 0.33s。
- [x] AC2：**零残留**——上述场景结束后：无残留 `core_service.exe`；无残留 reader/心跳线程导致的进程无法退出；`%TEMP%` 隔离根中的应用进程全部退出。给出进程树核查证据（命令 + 输出 + 时间戳见 `ac2-process-tree-audit.log`）。
- [x] AC3：**不回归**——`P20-ISOLATION-1` 已确认的能力不得退化：① 存活但挂起可被心跳发现并恢复；② `drop` 拆环并 reap 子进程；③ 既有 `cargo test --bin m2rc1-desktop resilient_channel`（9 项通过）与 `stdio_channel_drop`（1 项通过）全绿。给出复跑命令与输出。
- [x] AC4：**并发审查**——给出持锁路径清单与每一处的上界说明（哪些路径用 `try_lock`/超时、哪些必须持锁、为何不会互相饿死）；指出并就任何仍可能无限等待的点给出结论（已修掉，见 `concurrency-lock-audit.md`）。
- [ ] AC5：**真实场景**——在真实桌面会话下，正常关闭窗口后：应用进程与 sidecar 全部退出且无孤儿。CLI 环境缺少交互桌面（0x80070578），已提供可直接复跑脚本 `verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` 供 Coordinator 在交互桌面验收。
- [x] AC6：**证据**——命令、exit code、原始输出、时间戳落盘 `verification/P20-CLOSE-BOUND-1/**`；新增测试必须**真断言行为**（不得空断言、不得只改测量口径）。

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
- 2026-10-18 Antigravity 完成硬上界修复与并发持锁审查（AC1-AC4, AC6）：
  1. `wait_timeout_or_kill` 强杀后增加 1000ms 硬超时轮询，消除无超时 `child.wait()`。
  2. `shutdown_and_kill` 增加 500ms 守护超时 join，消除 reader 线程悬挂导致的死锁。
  3. `inner.lock()` 互斥锁改为短锁仅 take/clone，在锁外执行 `shutdown_and_kill`，持锁降至纳秒级。
  4. 补齐 `tasklist` 退出码校验断言，新增叠加场景及硬时限测试并全绿。
  5. 交付 `doc/handoffs/P20-CLOSE-BOUND-1-antigravity.md`，状态转入 `in_review`。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-P20-CB-SRC | AC1/AC3/AC4 | apps/desktop/src-tauri/src/library_bridge.rs | - | 36c059292fbc2fa15f82484cfe815ec3c8e9ad5b47ab6a1afc9a9657466179e5 | SOURCE_PIN |
| EVID-P20-CB-AC1 | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stdout.log | - | b36db2457a8016942177f9c7010000330ac88abd492abb6c08cc9abddbc0964c | CANONICAL |
| EVID-P20-CB-AC1-EXIT | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.exit | - | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC1-META | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.meta.json | - | 3b95cb2d3e8f1f7746d286cd7fd395aadd50fef27a214073949ebefc0a19a450 | SOURCE_PIN |
| EVID-P20-CB-AC1-STDERR | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stderr.log | - | ff0fb9406568129e59419921462b0a9cbe88ac19ecab818a74472b650f73f2a3 | SOURCE_PIN |
| EVID-P20-CB-AC2 | AC2 | verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.log | - | 3ba7f4ce0a9b4935382ff70be9e12b117c2e9a3547db675706573953c2409f67 | CANONICAL |
| EVID-P20-CB-AC3-RESIL | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stdout.log | - | 39e0c22dacd47311fc801bb6831ec6b741d15eb6ecb012345aef4e40fb8cb61b | CANONICAL |
| EVID-P20-CB-AC3-R-EXIT | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.exit | - | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC3-R-META | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.meta.json | - | c9070b22233e8612307e85636f6d15ff7137bfaac6e95cc3b9fd949d354c8732 | SOURCE_PIN |
| EVID-P20-CB-AC3-R-STDERR | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stderr.log | - | 382a69bf38abe907ae852bcded9a1b56240b3f73c62c356b518361fd44cb3748 | SOURCE_PIN |
| EVID-P20-CB-AC3-STDIO | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stdout.log | - | ddb12f135dcb4dab9a40f1bc849b2b88f712228234bb8f5865f2231b92935b84 | CANONICAL |
| EVID-P20-CB-AC3-S-EXIT | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.exit | - | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC3-S-META | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.meta.json | - | 4b87d9ae72d161b53692c4affa605bde975bfd27de1bffbe35958df1d13fe04e | SOURCE_PIN |
| EVID-P20-CB-AC3-S-STDERR | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stderr.log | - | 8e91cfa9635250afd4568fa9c67cb2c687a1d3b2f04f3916d84d47386c1531d1 | SOURCE_PIN |
| EVID-P20-CB-AC4-AUDIT | AC4 | verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md | - | 675f2aa21ba40d8c368c7a04dae7d11c7177abee40aeb9d623daf47c70df8a24 | CANONICAL |
| EVID-P20-CB-AC4-WAIT | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.stdout.log | - | a702102e3f6308bdb27772add152f230200125964d222ca6e64bfb284c2c377b | CANONICAL |
| EVID-P20-CB-AC4-W-EXIT | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.exit | - | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC4-W-META | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.meta.json | - | e35780ee70880de394bb7d5738923f8caf11f10ea7176e87a7195e5756041410 | SOURCE_PIN |
| EVID-P20-CB-AC4-W-STDERR | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.stderr.log | - | 382a69bf38abe907ae852bcded9a1b56240b3f73c62c356b518361fd44cb3748 | SOURCE_PIN |
| EVID-P20-CB-AC4-GUARD | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.stdout.log | - | 696de58b62d7ae298a2873982b29b1a88d07314d6333ba3292d539eef66c4862 | CANONICAL |
| EVID-P20-CB-AC4-G-EXIT | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.exit | - | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC4-G-META | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.meta.json | - | 9f0737b6f712a274ee95d3a84929981ad05b304d112496297899396ffbdcfc2d | SOURCE_PIN |
| EVID-P20-CB-AC4-G-STDERR | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.stderr.log | - | 382a69bf38abe907ae852bcded9a1b56240b3f73c62c356b518361fd44cb3748 | SOURCE_PIN |
| EVID-P20-CB-AC5-SCRIPT | AC5 | verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 | - | f4810e792400728fa33fa3dcba738929dc4eeb0f6111bc3e64787dfd987183b3 | CANONICAL |
| EVID-P20-CB-SUITE | AC6 | verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 | - | 9fc4d26c5caed7fbc82fb97faa702408a1ea13861afc966ab19a1f6bd4d36eee | CANONICAL |
| EVID-P20-CB-README | AC6 | verification/P20-CLOSE-BOUND-1/README.md | - | 6f8ffd2cbb917cf656f6ae8795a4c7548ad6334ef0566ab3e53fc11ab775c5f1 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在关闭时同步。

