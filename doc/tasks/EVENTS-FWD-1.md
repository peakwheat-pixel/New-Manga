---
id: EVENTS-FWD-1
title: 冻结并实现 host→WebView 事件转发面（解 UI-DESIGN-1 的 G17；P14 前置）
kind: feature
governance_version: 2
status: done
approval: coordinator_release_20261016_confirmed_gap_g17
suggested_owner: Codex
owner: Antigravity
reviewer: dsh
depends_on: [P13-C1, HOST-ISSUER-1-C1, UI-DESIGN-1]
base_commit: 6c28a02e9
branch: agent/antigravity/EVENTS-FWD-1
worktree: G:/CODEX/New Manga.workspace/worktrees/EVENTS-FWD-1
integration_commit: 22920f8dbbfc076e0cbeaadbf1cc8852c5790d0b
delivery_head: 5f1d9870ea87361255589719cd66fa392238504f
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/EVENTS-FWD-1
---

# EVENTS-FWD-1：host→WebView 事件转发面（G17）

## 来源与目标

- **来源（设计基线缺口 G17）**：[AD-001 四页 UI/UX 设计基线](../design/AD001_FOUR_PAGE_UI_BASELINE.md) §7
  的 **G17**：「Run/Export/Reading 事件到 WebView 的转发面 —— 事件 wire 已冻结，但 host→WebView 转发
  （Tauri event emit 等）未在任何契约冻结」→ 建议动作「host 侧 Task：冻结事件转发面（**P14 前置**）」。
- **Coordinator 只读复核确认缺口真实（2026-10-16）**：
  - `apps/desktop/src-tauri/src/**.rs` 中 **`.emit` 出现 0 次**（无任何 host→WebView 事件转发）；
  - 前端 `apps/desktop/frontend/src/**` **无** `listen(` / `@tauri-apps/api/event` 依赖；
  - 契约 [M2-C1](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) **§6.2 Event catalog（L546）** 已冻结：
    `TaskFailed`/`RunPaused`/`RunCompleted`/`CurrentPageStepChanged`（**P13-C1 frozen**）、
    `ExportProgressChanged`/`ReadingProgressChanged`（**2.1 FROZEN**）；
    而 `CoreAvailabilityChanged`（L560）仍为 **UNKNOWN / PROPOSAL**。
- **目标**：在**不改变已冻结 Core 事件 wire** 的前提下，**冻结并实现** host→WebView 的转发面，
  使 P14（工作台）等页面能按 §6.2 收到失效提示并重查快照。
- **边界（关键）**：本 Task **只**转发 §6.2 中**已 FROZEN** 的六类事件；
  **不得**发明 `CoreAvailabilityChanged`（属另一缺口 **G16**，未冻结）。

## Acceptance Criteria

- [x] **AC1 冻结转发面（先契约，后实现）**：在 [M2-C1](../contracts/M2-C1_TYPED_IPC_CONTRACT.md) 中**新增 revision 2.4**（§6.4、§3.2、§11、§12），
      冻结 host→WebView 的**事件名与 payload 投影**，并明确：
      ① 投影自 §6.2 的六类已冻结事件（逐条给出 Core wire 出处）；
      ② **不传递路径/引用/字节**（对齐 §10.2/§10.3/§10.4：WebView 不得取得任意 OS 路径或签名材料）；
      ③ 事件**只是失效提示**，**不是真值**——消费方必须重查快照（对齐 §6.2 与 P11 §7.1/§7.3）；
      ④ 未冻结的 `CoreAvailabilityChanged` **明确排除**并注明属 G16；`ImportProgressChanged` 属 G26 明确排除。
      给出了独立的 `compatibility-impact.md` 兼容性影响说明；**未**改动既有冻结事件的字段或语义。
- [x] **AC2 实现（host 侧）**：Python Core 产生的 §6.2 事件经 host 异步 reader 线程安全投影并通过 Tauri `app.emit` 转发；
      capabilities 增加 `core:event:allow-listen` / `core:event:allow-unlisten`；
      事件转发**未**成为新的命令面（不暴露 host-only 能力）。
- [x] **AC3 消费侧最小接线**：提供最小的前端订阅入口（`apps/desktop/frontend/src/events.ts`），
      导出 6 类 typed listener helper 函数（`onTaskFailed`、`onRunPaused`、`onRunCompleted`、`onCurrentPageStepChanged`、`onExportProgressChanged`、`onReadingProgressChanged`），
      供实现 Task（P14 等）直接复用；单测 `events.test.ts` 全部 PASS；本 Task **不做**页面级 UI。
- [x] **AC4 真实链路证据与分层证据**：在**已重建的 2.3 frozen bundle** 上验证 `packaged_sidecar_tests` 全部 7 个测试 PASS（含 event sink 注册与生命周期）；
      因生产命令集保持冻结且无端到端触发 PipelineRun 的命令，端到端触发状态如实记录为 `BLOCKED_ON_TRIGGER_COMMAND`，
      并提供完整的四层分层证据（安全投影过滤、Stdio 多路复用与旁路无干扰、真实 bundle 运行时、前端类型解包与分发），原始日志与退出码已落盘。
- [x] **AC5 不越界**：未改 Core 侧 §6.2 的既有事件字段/语义；未实现 `CoreAvailabilityChanged` 或其他未冻结事件；
      未改契约无关章节；未新增产品依赖。
- [x] **AC6 不回归**：`tests/core/**`（395 passed）与既有 Rust 测试（79 passed + 1 ignored (8 filtered) + 1 concurrent passed + 7 packaged passed）全绿；
      前端 177 个测试全绿且 build 成功；Cargo 生成的 27 个 CRLF 噪音已使用 `git diff` 判定并全部恢复。
- [x] **AC7 固定交付**：提交固定 commit、Handoff（`doc/handoffs/EVENTS-FWD-1-fwd1.md`）、Canonical Evidence 真实 sha256 登记完毕；不 `push`、不 `merge`。

## 允许修改范围

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（**仅**新增 revision 与转发面小节；不得改写既有冻结内容）
- `apps/desktop/src-tauri/src/**`（事件转发实现与四处同步）
- `apps/desktop/frontend/src/**`（最小 typed listener 入口；不做页面 UI）
- 两侧对应测试文件；本 Task、`doc/handoffs/EVENTS-FWD-1-*.md`、`verification/EVENTS-FWD-1/**`
- 只读引用：[设计基线](../design/AD001_FOUR_PAGE_UI_BASELINE.md)、[P11 长任务契约](../contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md)、
  [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)

## 禁止范围

- **不得**改动 §6.2 既有冻结事件的字段/语义；**不得**把 UNKNOWN/PROPOSAL 的事件（`CoreAvailabilityChanged`、`ImportProgressChanged`）当作可用面实现。
- **不得**顺着事件 payload 把路径、opaque 引用或签名材料下发给 WebView。
- **不得**改 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)、Schema、依赖清单、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`；
  **不得触碰**用户 19 项 dirty/untracked。
- 不得删除或弱化既有测试；不 `push`/`merge`/`reset`/`stash`。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 契约 revision 评审：事件名/投影/排除项/兼容性 | 只读/文档审查 | PASS：rev 2.4 冻结六类事件安全投影，排除未冻结事件，保证向后兼容与 P14 轮询降级 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`<br>`verification/EVENTS-FWD-1/compatibility-impact.md` |
| AC2/AC3 | host 转发的单元/集成测试 + 前端 typed listener 单测 | 本地 Rust + Node 环境 | PASS：`cargo test` 4 个 event_fwd 单测全绿；前端 vitest 177 个测试全绿，`npm run build` 成功 | `verification/EVENTS-FWD-1/cargo-tests.log`<br>`verification/EVENTS-FWD-1/frontend-tests.log`<br>`verification/EVENTS-FWD-1/frontend-build.log` |
| AC4 | 2.3 frozen bundle 上的真实事件链路（或分层证据） | 重建后的 2.3 bundle + 本地环境 | 端到端因生产命令面冻结处于 `BLOCKED_ON_TRIGGER_COMMAND`；分层证据 Layer 1-4 全绿 | `verification/EVENTS-FWD-1/packaged-sidecar-tests.log`<br>`verification/EVENTS-FWD-1/evidence-layering.md` |
| AC6 | `tests/core/**` + Rust 测试全绿 + 并发无干扰 | Python 3.12 + Rust dev/packaged | PASS：pytest 395 passed；Rust 79 passed, 1 ignored (8 filtered)；concurrent 1 passed；packaged 7 passed | `verification/EVENTS-FWD-1/python-tests.log`<br>`verification/EVENTS-FWD-1/concurrent-roundtrips.log` |

## 依赖、风险与阻塞

- `depends_on` 均已 `done`（P13-C1 冻结了 4 个事件；HOST-ISSUER-1-C1 冻结了 host-only 控制面；UI-DESIGN-1 冻结了设计基线并登记 G17）。
- 风险一：**Core 事件在 stdio JSONL 流上**，host 需要在不破坏既有请求/响应多路复用的前提下旁路转发；
  实现须证明不干扰既有 channel 语义（对齐 ENV-BUNDLE-1-FU1 的 `same_channel_concurrent_round_trips` 先例）。
- 风险二：**P14 依赖本 Task**；若本 Task 未收口，P14 只能在"无事件、仅轮询"的降级形态下实现——本 Task 不得阻断 P14 的降级路径。
- 风险三：把"事件"当成"真值"使用（设计基线 §9 第 6 条明令禁止）→ 契约与实现都必须写明消费方需重查快照。
- 阻塞条件：若 host 侧通道结构上无法在不改 Core 的前提下旁路事件 → 如实 `BLOCKED` + 原始证据，交 Coordinator 裁决（可能需要 Core 侧配合的独立 Task）。

## 交付与运行记录

- 2026-10-16 Coordinator 释放（dsh, epoch 6）：依据 UI-DESIGN-1 §7 的 G17 + Coordinator 只读复核
  （`.emit` 0 次、前端无 event 依赖、§6.2 已冻结六类事件、`CoreAvailabilityChanged` 仍 UNKNOWN）。
  释放前已按 UI-DESIGN-1 的 I1 教训**先核实缺口真实**，避免为不存在的工作释放 Task。
- 2026-10-16 Antigravity 实施完成：
  - AC1：契约升级至 rev 2.4，冻结 §6.4 事件转发面并编写 `compatibility-impact.md`；
  - AC2：在 `library_bridge.rs` 中实现后台 reader 异步路由与安全投影，在 `main.rs` 中接入 `app.emit`，更新 capabilities；
  - AC3：在 `apps/desktop/frontend/src/events.ts` 中提供 typed listener helper 函数，并通过 `events.test.ts`（177/177 单元测试全过，构建成功）；
  - AC4：完成四层分层证据，全套测试通过；如实报告端到端触发链因生产命令面保护而处于 `BLOCKED_ON_TRIGGER_COMMAND`；
  - AC5/AC6：未越界修改 Core wire，无多余依赖；全套 Python（395 项）与 Rust 测试（88 项）全绿，恢复 27 个 CRLF 噪音；
  - AC7：登记 Canonical Evidence，生成 Handoff。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EVID-FWD-COMPAT | AC1 | `verification/EVENTS-FWD-1/compatibility-impact.md` | `6229e230f` | `7c8597150e339f42c6dbbe9933f739fb4e8f6b672ab9abeed6678a3dc2c32aad` | `CANONICAL` |
| EVID-FWD-PYTHON | AC6 | `verification/EVENTS-FWD-1/python-tests.log` | `6229e230f` | `2a004dee4d7b565c1e5e57e4efa377f87e3503972cd423ca5e5fc8d640d344fd` | `CANONICAL` |
| EVID-FWD-RUST-UNIT | AC2/AC6 | `verification/EVENTS-FWD-1/cargo-tests.log` | `6229e230f` | `3e93cf4a01be9f1872cde0091b5d5cfa925c376c8ee4237c788bc79fe82e2aa8` | `CANONICAL` |
| EVID-FWD-CONCURRENT | AC2/AC6 | `verification/EVENTS-FWD-1/concurrent-roundtrips.log` | `6229e230f` | `64906757c7b74900fb49b4750d74b4ad9373bfb23fdde0a08040d5aa32161c1d` | `CANONICAL` |
| EVID-FWD-PACKAGED | AC4/AC6 | `verification/EVENTS-FWD-1/packaged-sidecar-tests.log` | `6229e230f` | `4c91aeeaa2fddc2fdcc684c28e4e7f35a94e882b6a2ef042228b28e6bb2b1942` | `CANONICAL` |
| EVID-FWD-LAYERING | AC4 | `verification/EVENTS-FWD-1/evidence-layering.md` | `6229e230f` | `ffb5c140c655d6d51b9b8fefa4660f9cb14937782a454388e2c348a8ad020134` | `CANONICAL` |
| EVID-FWD-FE-TEST | AC3/AC6 | `verification/EVENTS-FWD-1/frontend-tests.log` | `6229e230f` | `899450ef31c8899727ca0eb02446e5dbabf1f6c7379f61545889cc381aff98ae` | `CANONICAL` |
| EVID-FWD-FE-BUILD | AC3/AC6 | `verification/EVENTS-FWD-1/frontend-build.log` | `6229e230f` | `9d3ea38314dc7aa2d517f54bfd31ef89a01bd1e2539ce939fa17e8979700f22e` | `CANONICAL` |

| EVID-FWD-REVIEW | AC1-AC7 | `verification/EVENTS-FWD-1/dsh-review-r1.md` | `b0432a89f` | - | REVIEW |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/EVENTS-FWD-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/EVENTS-FWD-1 | verification/EVENTS-FWD-1/resource-manifest.json | 本 Task 独立 worktree；closeout 时按 Worktree Safety Inventory 复核后填写 |

## Closeout Record

- Closeout date / Coordinator：2026-10-16（dsh, epoch 6）。Reviewer=dsh（独立于 Owner=Antigravity）。
- canonical_evidence_status：`complete`。8 个原始证据 pin 已**逐个复算**：**6 个一致**；`compatibility-impact.md` 与 `evidence-layering.md` 的 owner pin **与磁盘文件不符**（owner 计算 pin 后文件又有落盘变化），closeout 按实际文件复算并**更正 pin**（这是"证据 pin 以实测为准"的处置，非返修项；治理检查器对 `done` 会同时校验 commit 含路径与 sha256 匹配）。
- resource_closeout_status：`complete`（worktree `PRESERVE_REFERENCED`）。删除、迁移、归档数量/字节数：0。
- 交付：`done`。集成 `22920f8dbbfc076e0cbeaadbf1cc8852c5790d0b`；delivery_head（分支实际 HEAD）`5f1d9870ea87361255589719cd66fa392238504f`（owner 记录的 `6229e230f` 为 amend 前的陈旧值，按 BL-7 以实测为准）。
- Review：R1 初判 `changes_requested`（唯一 I1 = 共享契约重复 h1 与冲突的当前修订声明）→ 返修 `6229e230f` → 复核 **I1 CONVERGED** → 判定 **approved**。
- 集成冲突与解析：与 HOST-TTL-BOUNDARY-1 在 `packaged_sidecar_tests.rs` 末尾同时追加测试 → 合并时**语义级**解析，**两侧测试全部保留**；合并后重跑 frozen 2.3 打包套件 **9 passed / 0 failed**（TTL 两个往返测试 + 本 Task 的 event sink 测试均通过），证明解析未丢失任一侧功能。
- **未关闭项及保留原因**：AC4 的端到端触发如实为 `BLOCKED_ON_TRIGGER_COMMAND` —— 当时生产命令面**没有任何命令可启动 Pipeline Run**（该缺口已由 [RUN-IPC-1](RUN-IPC-1.md) 释放修复）。因此本 Task **不声称**已验证真实事件从 Core 经 host 到达 WebView；已提供四层分层证据（安全投影过滤 / stdio 多路复用旁路无干扰 / 真实 bundle 运行时 / 前端类型解包）。**P14 接入 `StartRun` 后须补做该端到端段。**
- 同类教训：owner 三次出现"记录自身 commit SHA 后再 amend"导致 `delivery_head` 陈旧 → 已登记 **BL-15**（Handoff 不应自引用将产生的 SHA，或由 Coordinator 在 closeout 冻结）。
- 当前指针清理：`STATUS` / `REBASELINE_PLAN` 已同步（EVENTS-FWD-1 移出 READY；**P14 前置仅剩 RUN-IPC-1**）。
