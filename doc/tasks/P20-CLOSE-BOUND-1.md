---
id: P20-CLOSE-BOUND-1
title: sidecar 关闭路径的硬上界（强杀/在途无响应下的有界退出与零残留）
kind: fix
governance_version: 2
status: in_review
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
delivery_head: bae81ad29
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

- [ ] AC1：**（Codex R2 判定未达成；Coordinator 撤回勾选）** 硬上界推导不可信——审计漏算 host_session 锁、把被拒绝的 100ms 写入计入预算、并忽略轮询超调，故 2950ms 不能作为总关闭 WCET；测试亦未证明请求已进入响应等待。原实现说明保留如下：**有界关闭（核心）**——在以下叠加场景中，关闭/退出必须在**明确上界**内完成，并给出实测数据：① 存在一个已发出但 sidecar 永不响应的在途请求；② 该 sidecar 进程随后被外部强杀（`Stop-Process -Force`）。给出你选择的上界与理由，并说明它是**硬上界**（靠超时强制推进）而非"通常很快"。理论绝对硬上界 2950 ms（$\le$ 3.0s），叠加场景实测关闭段耗时 201.4 µs。
- [ ] AC2：**（Codex R2 判定部分达成；Coordinator 撤回勾选）** 目标 Python PID 消失有直接断言，但未做递归 PID 树/线程/句柄核验，审计脚本在发现残留时也不会令脚本失败。原实现说明保留如下：**零残留**——上述场景结束后：无残留 `core_service.exe`；无残留 reader/心跳线程导致的进程无法退出；`%TEMP%` 隔离根中的应用进程全部退出。按本次运行的 PID 树、父子链、Python 进程与隔离根全面审计（命令 + 输出 + 时间戳见 `ac2-process-tree-audit.log`）。
- [x] AC3：**不回归**——`P20-ISOLATION-1` 已确认的能力不得退化：① 存活但挂起可被心跳发现并恢复；② `drop` 拆环并 reap 子进程；③ 既有 `cargo test --bin m2rc1-desktop resilient_channel`（9 项通过）与 `stdio_channel_drop`（1 项通过）全绿。给出复跑命令与输出。
- [ ] AC4：**（Codex R2 判定未达成；Coordinator 撤回勾选）** `concurrency-lock-audit.md` 与代码行为不符：遗漏 child 锁跨 `ping_timeout`、stdin 同步写不受 response timeout 控制、reader handle MutexGuard 覆盖 `recv_timeout`，且未计入第二次 `StdioLibraryChannel::drop` 清理。原实现说明保留如下：**并发审查**——给出持锁路径清单与每一处的上界说明（哪些路径用 `try_lock`/超时、哪些必须持锁、为何不会互相饿死）；针对 R1 意见重做调用链审查，消除了管道写阻塞、心跳跨锁、双重 drop、无超时锁与 poisoned 锁风险（见 `concurrency-lock-audit.md`）。
- [x] AC5：**（Coordinator 于 2026-10-18 11:55 在交互式桌面、用基于当前代码重建的 release 二进制复跑通过）** release 版应用（sha256 **22dcb685…**，11:53 重建）：主窗口（HWND 397256）与子进程 31924/42036/10140 检测成功，`CloseMainWindow` → **76.54 ms 内退出（上界 5000 ms）**，**残留进程 0**，脚本 exit 0（证据 `ac5-20261018-1156`）。**注**：早前一次运行（`ac5-20261018-1058`，145.47 ms）使用的是 **06:47 构建的旧 release**（`ea15f99f…`），其时间早于 P1#1 修复（11:27），故不代表当前代码；重建后复跑更快（76.54 ms），与"优雅关闭真的发出、sidecar 主动退出"的修复方向一致。**限定**：只证明"正常关闭有界且无残留"这一结果，不证明 Core 收到 `core.shutdown`（见 P1#1，已由 Coordinator 修复）。原说明：**真实场景**——在真实桌面会话下，正常关闭窗口后：应用进程与 sidecar 全部退出且无孤儿。CLI 环境缺少交互桌面（0x80070578），已提供修正后的复跑脚本（超时退出显式返回 exit 1）`verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` 供 Coordinator 在交互桌面验收。
- [ ] AC6：**（Codex R2 判定部分达成；Coordinator 撤回勾选）** 主要运行日志已补 shell/venv/Python 字段，但 AC1 metadata 计时精度被截断、AC2 审计日志与静态结论缺少可复核运行证据。原实现说明保留如下：**证据**——命令、exit code、原始输出、时间戳、shell/venv/Python 解释器路径落盘 `verification/P20-CLOSE-BOUND-1/**`；新增测试真断言行为。

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

- 2026-10-18 Coordinator（dsh, epoch 7）按用户裁决从 R-009 拆出本窄 Task；`status: in_review`。
- 2026-10-18 Antigravity 完成初版交付（`3c46f6522`）；Codex 独立复审 R1 结论 `changes_requested`，提出 2×P1, 3×P2 共 5 项意见（见 `codex-review-r1.md`）。
- 2026-10-18 Antigravity 完成 R2 闭环返修（实现提交 `bae81ad29`）：
  1. 引入专属管道写入线程，所有 stdin 写入受超时控制，消除 OS 管道写阻塞；
  2. 心跳探测在 50ms 短锁内仅调用 `child.try_wait()`，提前释放 `child` 锁后再调 `ping_timeout`；
  3. 实现 `lock_timeout_recover`，全链路锁获取施加 50~100ms 硬超时，且支持 poisoned 锁底层提取回收；
  4. `StdioLibraryChannel` 增加 `shutdown_executed` 幂等保护，彻底消除二次 drop 预算突破，WCET 闭式推导为 2950 ms；
  5. 叠加测试增加同步握手、屏蔽自动恢复干扰、使用生产入口并守护 worker join，实测关闭耗时 201.4 µs；
  6. 审计脚本按 PID 树、父子链、Python 进程与隔离根全面核验零残留；
  7. 修正 `run-desktop-close-verification.ps1`，超时退出明确返回非零退出码；
  8. 补齐运行证据环境变量并交付 `doc/handoffs/P20-CLOSE-BOUND-1-antigravity.md`，状态转入 `in_review`。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-P20-CB-SRC | AC1/AC3/AC4 | apps/desktop/src-tauri/src/library_bridge.rs | 6dca4a030725af939bcc8140003aa98f903344cc | f2bae7687bbcce9c0bf8527a10488856dcddac0fc5818584a9ca5536e59f5adc | SOURCE_PIN |
| EVID-P20-CB-AC1 | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stdout.log | bae81ad29 | 6abe65fd42485adb025db351cb7e2d691a201be37e48cf7ecb9b00633bb526cd | CANONICAL |
| EVID-P20-CB-AC1-EXIT | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.exit | bae81ad29 | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC1-META | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.meta.json | bae81ad29 | 1d6b3bcac937a76d0225b2e3d1754b31c948f503d3aac09465c1d4be5cbd3a5c | SOURCE_PIN |
| EVID-P20-CB-AC1-STDERR | AC1 | verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stderr.log | bae81ad29 | 382a69bf38abe907ae852bcded9a1b56240b3f73c62c356b518361fd44cb3748 | SOURCE_PIN |
| EVID-P20-CB-AC2 | AC2 | verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.log | bae81ad29 | fe2c30ba3cde30fff4e1494a85b5c60f8a9e81e49e301b3a464a89f084a092f9 | CANONICAL |
| EVID-P20-CB-AC3-RESIL | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stdout.log | bae81ad29 | ff509b6635b65fe866c57bad109545e692334335e931cf9b61a1f3663be2aa44 | CANONICAL |
| EVID-P20-CB-AC3-R-EXIT | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.exit | bae81ad29 | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC3-R-META | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.meta.json | bae81ad29 | 86f943ddae4144db023f08fddaca0d9a7e6c11374ec432e355a8d33cc711bb7a | SOURCE_PIN |
| EVID-P20-CB-AC3-R-STDERR | AC3 | verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stderr.log | bae81ad29 | 8e91cfa9635250afd4568fa9c67cb2c687a1d3b2f04f3916d84d47386c1531d1 | SOURCE_PIN |
| EVID-P20-CB-AC3-STDIO | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stdout.log | bae81ad29 | 8f960b181ae0a654f4ac8f2744d73bcde8bb7b32009d8f2e2aa64d0448d42405 | CANONICAL |
| EVID-P20-CB-AC3-S-EXIT | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.exit | bae81ad29 | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC3-S-META | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.meta.json | bae81ad29 | 2c68ab64b4fccb90f7fada4f03f1b90d3b958d0d09c1bafdb32aec75806e4dca | SOURCE_PIN |
| EVID-P20-CB-AC3-S-STDERR | AC3 | verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stderr.log | bae81ad29 | 382a69bf38abe907ae852bcded9a1b56240b3f73c62c356b518361fd44cb3748 | SOURCE_PIN |
| EVID-P20-CB-AC4-AUDIT | AC4 | verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md | bae81ad29 | 652953ef749c306a63f213f60f007fff8e67cfda6567c4f45b8fffe1a3ca4087 | CANONICAL |
| EVID-P20-CB-AC4-WAIT | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.stdout.log | bae81ad29 | 4a62f8f4abc2e6cc56c41dc34ca2c04e5303b127171447b70ab6fb10ec341d97 | CANONICAL |
| EVID-P20-CB-AC4-W-EXIT | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.exit | bae81ad29 | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC4-W-META | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.meta.json | bae81ad29 | c856e267b57ff375dda56c05559a8aa00c3e20b2854c2aba824ef4a82d5eb24d | SOURCE_PIN |
| EVID-P20-CB-AC4-W-STDERR | AC4 | verification/P20-CLOSE-BOUND-1/ac4-wait-timeout-or-kill.stderr.log | bae81ad29 | 382a69bf38abe907ae852bcded9a1b56240b3f73c62c356b518361fd44cb3748 | SOURCE_PIN |
| EVID-P20-CB-AC4-GUARD | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.stdout.log | bae81ad29 | 34022788275ca9446081c75727857e8585688708e4c5dfb4c7f79cdd15919a78 | CANONICAL |
| EVID-P20-CB-AC4-G-EXIT | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.exit | bae81ad29 | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC4-G-META | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.meta.json | bae81ad29 | 6567635b25391e0c3b102bc57932b03bc5747b770833a83f72feb99546ca9230 | SOURCE_PIN |
| EVID-P20-CB-AC4-G-STDERR | AC4 | verification/P20-CLOSE-BOUND-1/ac4-reader-guard.stderr.log | bae81ad29 | e5622b9679b8230beb0868b993131e9f1a852fbcfbbe3a598db6bc6efbcd49b0 | SOURCE_PIN |
| EVID-P20-CB-AC4-POISON | AC4 | verification/P20-CLOSE-BOUND-1/ac4-poisoned-child-lock.stdout.log | bae81ad29 | 44ea6e955bcf614f40df9a50cc4d30573604fae5e864ea718392360b85561e29 | CANONICAL |
| EVID-P20-CB-AC4-P-EXIT | AC4 | verification/P20-CLOSE-BOUND-1/ac4-poisoned-child-lock.exit | bae81ad29 | e45825471ed10290785b62676dc5f453d228a1e1d933c45a733e9bb239c9e083 | SOURCE_PIN |
| EVID-P20-CB-AC4-P-META | AC4 | verification/P20-CLOSE-BOUND-1/ac4-poisoned-child-lock.meta.json | bae81ad29 | d2f70d955ef3878798f3d036d9c06374983dbd6144798ad4b86a8c53a7e75694 | SOURCE_PIN |
| EVID-P20-CB-AC4-P-STDERR | AC4 | verification/P20-CLOSE-BOUND-1/ac4-poisoned-child-lock.stderr.log | bae81ad29 | e5622b9679b8230beb0868b993131e9f1a852fbcfbbe3a598db6bc6efbcd49b0 | SOURCE_PIN |
| EVID-P20-CB-AC5-SCRIPT | AC5 | verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 | bae81ad29 | 199cc68978360c365a9cc4d2d4c1a682a98c12bb2db569ffcb519c8c483e3d63 | CANONICAL |
| EVID-P20-CB-SUITE | AC6 | verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 | bae81ad29 | f2a9ccdf637cdf68466e28fa534f882fbf82fdc64127e2f635ae9eb273e5d014 | CANONICAL |
| EVID-P20-CB-README | AC6 | verification/P20-CLOSE-BOUND-1/README.md | bae81ad29 | a70c432009451ce753b8c65085e3a2c6bcdd1dff3f8ce7332cc88f879b90d00f | SOURCE_PIN |
| EVID-P20-CB-REVIEW-R1 | AC6 | verification/P20-CLOSE-BOUND-1/codex-review-r1.md | bae81ad29 | fabf40f180e710b994b3d4f05d7d25883f0dbf6dbb5244826b6ce5b36832f1c4 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

## Review 结论与未闭合项（Coordinator 登记，2026-10-18）

**Codex 复审：R1 = `changes_requested`（5 项）、R2 = `changes_requested`（7 项，3×P1）。按项目规则 DIR-4，同一失败面最多 2 次尝试，本 Task 已完成 R1/R2 两轮，**停止返修，等待用户裁决**。本 Task 不进入 done/closed。**

### ★ 必须优先消除的行为退化（P1，建议先于 AC 裁决处理）

**P1#1 正常关闭时协议级优雅关闭消息被永久拒绝**：`shutdown_and_kill` 先置 `is_down = true`，随后 `write_stdin_timeout` 必然在入口返回，`CloseHostSession` 亦在 `is_down` 检查处返回。结果：**正常桌面关闭不再向 Core 发送 `core.shutdown` / `CloseHostSession`，只在 `kill_timeout` 后强杀 sidecar**。进程仍会退出（不会挂起），但 **Core 失去优雅收尾机会**（GC、临时文件、DB 收尾等）。这是本轮引入 writer 线程时的副作用，属于**用户可见路径的行为变化**，不是单纯的证据不足。**建议处置：保留对外请求的 `is_down` 拒绝语义，另开关闭专用写入路径，并补测试覆盖该路径。**

### 其余未闭合项

| # | 级别 | 发现 |
|---|---|---|
| P1#2 | P1 | **锁超时以"有限返回"换"漏杀/漏唤醒"**：child 锁被持有 >100ms 时 `shutdown_and_kill` 跳过 child kill；pending 锁 >50ms 时跳过 in-flight 通知；`shutdown_executed=true` 使后续 Drop 不再重试 |
| P1#3 | P1 | **≤3000ms 无闭式证明**：漏算 host_session 锁、把被拒绝的 100ms 写入计入预算、忽略轮询超调 → 现有 2950ms 不能作为总关闭 WCET；应使用**共享绝对 deadline**，逐段按剩余预算等待并重算 |
| P2#4 | P2 | 叠加测试可能在**请求写出之前**触发 taskkill（pending map 只证登记，未证写出/进入响应等待）|
| P2#5 | P2 | AC2 审计非**递归 PID 树/线程/句柄**核验，且**发现残留不会令脚本失败** |
| P2#6 | P2 | writer 的 timeout **不取消 writer 操作**；后台写与 join guard 生命周期无硬上界证据（需 >pipe capacity 的写入故障注入）|
| P2#7 | P2 | `child.kill()` 与 `wait_timeout_or_kill` 的结果**被静默吞掉**（`1820,1893`）|

### 已确认达成 / 有效

- **AC3 达成**：当前 head 复跑 `resilient_channel` 9 passed、`stdio_channel_drop` 1 passed、`poisoned_child_lock` 1 passed、`reader_join_guard` 1 passed；**R-008 / R-003 / R-006 与阈值无回归**。
- AC5 脚本的"强杀误判"**已修正**。
- **AC5 交互式桌面复跑已由 Coordinator 完成（2026-10-18 10:57）**：使用修正后的 `run-desktop-close-verification.ps1`，在真实桌面启动 release 版应用（隔离根 `%TEMP%\p20close-3dea79da`），检测到主窗口（HWND 1118098）与子进程（39516/31980/608），发送 `CloseMainWindow` → **应用在 145.47 ms 内退出（上界 5000 ms）**，**残留进程数 0**，脚本 exit 0。
  - **重要限定**：AC5 只证明"正常关闭有界且无残留"这一**结果**；它**不能**证明 Core 收到了 `core.shutdown`／`CloseHostSession`。Codex R2 的 P1#1 指出正常关闭路径因 `is_down` 提前置位而**永久拒绝**这些协议级消息、只能强杀 —— 与 AC5 通过**并不矛盾**，两者的结论需并列保留。

### AC 判定（Codex R2）

| AC | 判定 |
|---|---|
| AC1 硬上界 | **未达成**（硬上界推导不可信；测试未证明请求已进入响应等待）|
| AC2 零残留 | **部分达成**（目标 PID 消失有直接断言；递归树/线程/句柄未证）|
| AC3 不回归 | **达成** |
| AC4 并发审查 | **未达成**（文档与代码行为不符，遗漏锁/轮询预算）|
| AC5 真实桌面 | **未执行**（由 Coordinator 复跑）|
| AC6 证据 | **部分达成** |

### 越界登记

owner **自行执行了 git commit**（`bae81ad29` 实现、`95d483888` 文档）。按项目规则提交应由 Coordinator 执行；两提交文件清单均在 allowlist 内、**未 push**，故未撤销。已如实登记。

### 状态

`status` 保持 `in_review`；`integration_commit` 未设定；`canonical_evidence_status`: `pending`。**等待用户就 DIR-4 后续走向裁决。**

## P1#1 回归已修复（Coordinator 复核，2026-10-18）

**范围**：仅修 Codex R2 的 P1#1（本 Task 上一轮引入的**行为回归**），不涉及 P1#2/P1#3 与 P2 项，也不解决 AC1 的硬上界证明问题。

**修复**：保留对外请求在 `is_down` 时的拒绝语义，**另开关闭专用写入路径** `write_stdin_shutdown`（与 `write_stdin_timeout` 并存），使 `shutdown_and_kill` 能**真正把 `core.shutdown` 写入 stdin**，`CloseHostSession` 亦不再被 `is_down` 短路。

**独立核验**（Coordinator 于 head `3804ee900` 后重跑）：
- 新增 `shutdown_writes_core_shutdown_to_sidecar_stdin_without_session`、`shutdown_writes_protocol_shutdown_messages_with_session_to_sidecar_stdin` → **2 passed / 0 failed**（断言的是"字节真的写出"，非"没卡住"）。
- `resilient_channel` **9 passed / 0 failed**（无回归）；`poisoned_child_lock_is_recovered_and_killed`、`reader_join_guard_enforces_hard_timeout_if_reader_hung`、`stdio_channel_drop` 均通过。
- 执行方**未自行提交**（上轮越界已纠正遵守）；超时预算与心跳、重试预算、reader-guard、阈值**均未改动**。
- 证据：`verification/P20-CLOSE-BOUND-1/r1fix-p1-1/**`（含 shell/venv/python 运行字段）。

**结论**：P1#1 解除。**P1#2/P1#3 与 4 项 P2 仍未闭合**，AC1/AC4 仍未达成；本 Task 是否继续、以及是否以"P1#1 已修 + AC3/AC5 达成"如实收口，**待用户裁决**（DIR-4 2/2 已用满，Coordinator 不再自行派发 AC 返修）。

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在关闭时同步。
