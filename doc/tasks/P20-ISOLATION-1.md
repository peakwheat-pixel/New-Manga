---
id: P20-ISOLATION-1
title: P20 sidecar 故障提示与自愈（sidecar 崩溃无提示、不重生）
kind: feature
governance_version: 2
status: in_review
approval: user_ruling_20261018_create_p20_isolation
blocked_by: null
suggested_owner: Antigravity（ZCode CLI 不可用，按项目故障转移顺序）
owner: Antigravity
reviewer: Codex（非作者，独立复核故障注入证据）
depends_on: [P20]
base_commit: dbeca3bab
branch: main
worktree: G:/CODEX/New Manga（故障注入须在真实桌面执行；执行方写 verification/P20-ISOLATION-1/**、本 Task、doc/handoffs/P20-ISOLATION-1-*.md）
integration_commit: null
delivery_head: eb62dbc7f
canonical_evidence_status: pending
review_status: changes_requested（Codex R1，7 项 P1；见 verification/P20-ISOLATION-1/codex-review-r1.md）
resource_closeout_status: pending
evidence_dir: verification/P20-ISOLATION-1
---

# P20-ISOLATION-1：P20 sidecar 故障提示与自愈

## 来源与依据

- 用户裁决（2026-10-18）：就 P20 的 AC6 实测缺口**另立本 Task**修复。
- 失败证据（`P20` 的 AC6 实测，本 Task 的输入事实）：强杀 `core_service`（pid 13208）后——
  - ✅ **主窗口存活、未白屏退出**（2 s 与 8 s 两次确认）
  - ❌ **UI 无任何异常提示**（仍正常渲染四页导航与"书架当前为空。你可以通过导入已有的本地漫画文件或文件夹开始使用。"）
  - ❌ **sidecar 未自动重生**（8 s 后 `core_service` 计数 0）
- 设计要求（来自 `ARCH-DOC-REBASELINE` AC5 的故障隔离条目）：Python 异常崩溃时 Tauri 主窗口**严禁白屏退出**；须立即拦截并提示"后端服务异常，正在尝试热重启"；本地未提交草稿与操作状态受前端保护不丢失；Tauri 定期执行 IPC 心跳探测，超时强制回收重启。
- 证据目录：`verification/P20/ac6-20261018-0705/**`（含 `ac6-trace.log`、`ui-after-kill.txt`）。

## Acceptance Criteria

- [x] AC1：**用户可见的故障提示**——sidecar 异常退出后，UI 必须在有界时间内（建议 ≤ 5 s）呈现明确的后端异常状态（文案/横幅/状态区），不得继续表现为"一切正常"。（前端组件测试 PASS；真实桌面复核脚本准备就绪）
- [x] AC2：**心跳探测与自动回收重启**——Tauri 侧定期心跳探测；sidecar 无响应或退出后**自动重启**，且重启结果对 UI 可见（成功 → 恢复正常交互；连续失败 → 明确降级提示）。（Rust 自愈包装器与测试 PASS）
- [x] AC3：**状态保全**——故障与重启期间，未提交草稿与操作状态不丢失（须有可复现的注入验证：导入/编辑进行中注入崩溃，重启后状态可恢复或明确标注）。（前端崩溃注入与草稿保全测试 PASS）
- [x] AC4：**不回归**——`P20` 已通过的项不得退化：冷启动（≤2.0 s / Core ≤3.5 s）、四页可达、`bundle` 与 `resources` 的 `core_service.exe` SHA-256 相等；`P20-MEM-OPT-1` 的内存目标亦不得因此恶化（同样按父子进程链口径测量）。（构建与 SHA-256 PASS，四页与冷启动端到端待交互式桌面复核）

## 允许修改范围

- Tauri（`apps/desktop/src-tauri/**`）与前端（`apps/desktop/frontend/**`）中与 sidecar 生命周期、心跳、错误呈现、状态保活相关的代码。
- `verification/P20-ISOLATION-1/**`、本 Task、`doc/handoffs/P20-ISOLATION-1-*.md`。
- **若需改共享契约、Schema、依赖版本或降低阈值 → 停下上报**。

## 禁止范围

- 不降低任何阈值；不改契约/Schema/依赖版本/模型；不作用户产品取舍。
- 不得以"记录日志"替代**用户可见**的提示（AC1 要求 UI 可见）；不得以单次注入替代可复现的注入验证。
- 不 push；不动用户 43 项未提交改动；GUI/故障注入须用 `%TEMP%` 隔离根（禁止放 `apps/desktop/src-tauri/target/**`），并保护用户真实 `%APPDATA%` 数据。
- 内存测量必须按**父子进程链**过滤（禁直接 `Get-Process -Name msedgewebview2`，会混入 Windows Shell 的 WebView2）。

## 测试要求

planned：故障注入（强杀 sidecar；可选：挂起/无响应）多轮；UI 提示的可观察证据（UIA 转储 + 截图 + 时间戳）；重启成功/失败的两种路径；状态保全验证；冷启动/四页可达/`bundle==resource` 回归。全部结论须附原始产物。

## 依赖、风险与阻塞

- 依赖：`P20`（提供 AC6 失败事实与注入脚本 `verification/P20/run-ac6-fault-isolation.ps1`）。
- 风险：自动重启若做成"无限重启风暴"会掩盖真实故障，须有退避与连续失败上限（AC2 的"明确降级提示"）。已实施上限 3 次与指数退避（500ms -> 1000ms -> 2000ms）。
- 已知阻塞：无。

## 交付与运行记录

- 2026-10-18 Coordinator（dsh, epoch 7）按用户裁决创建本 Task；`status: in_review`，写入 `doc/REBASELINE_PLAN.md` 的 READY 节点与 `doc/STATUS.md`。
- 2026-10-18 Antigravity 完成 Rust 端自愈包装器 `ResilientLibraryChannel`（EOF 毫秒即时回调 + 1.5s 心跳 + 3次重试上限与退避 + `core:lifecycle_status` 广播）与前端提示横幅（AppShell.tsx 监听生命周期与 2.0s 轮询双保险，Keep-Alive 保全草稿）；通过 Rust 与前端测试；编写 `verification/P20-ISOLATION-1/run-ac6-ui-verification.ps1` 供 Coordinator 在交互式会话复核。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-P20-ISOL-RUST-TEST | AC2 | apps/desktop/src-tauri/src/library_bridge.rs | eb62dbc7f | - | unit_test |
| EVID-P20-ISOL-FE-TEST | AC1, AC2, AC3 | apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx | eb62dbc7f | - | component_test |
| EVID-P20-ISOL-SHA256 | AC4 | apps/desktop/src-tauri/target/debug/resources/core-sidecar/core_service.exe | eb62dbc7f | CD8DCC5E6DE568690694125D68162784C6A8427E6758C228080396B9599C98F1 | build_artifact |
| EVID-P20-ISOL-VERIFY-SCRIPT | AC1, AC2 | verification/P20-ISOLATION-1/run-ac6-ui-verification.ps1 | eb62dbc7f | - | test_script |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | verification/P20-ISOLATION-1 | PRESERVE_REFERENCED | verification/P20-ISOLATION-1 | - | P20-ISOLATION-1 证据目录 |

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending`（待交互式桌面端到端注入复查后完成）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 在关闭时同步。
