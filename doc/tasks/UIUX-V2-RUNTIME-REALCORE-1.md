---
id: UIUX-V2-RUNTIME-REALCORE-1
title: 真实 Tauri 生产窗 + Python Core 端到端验收（解除 UIUX-V2-RUNTIME-1 的 HUMAN_VERIFY）
kind: verification
governance_version: 3
status: proposed
approval: pending_user_review
suggested_owner: dsh
owner: null
reviewer: null
depends_on: [UIUX-V2-RUNTIME-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UIUX-V2-RUNTIME-REALCORE-1
allowed_paths:
  - doc/tasks/UIUX-V2-RUNTIME-REALCORE-1.md
  - verification/UIUX-V2-RUNTIME-REALCORE-1/**
---

# UIUX-V2-RUNTIME-REALCORE-1：真实 Core 端到端验收（拟议，未释放）

## 来源与目标

- **来源**：[UIUX-V2-RUNTIME-1](UIUX-V2-RUNTIME-1.md) 的 AC12 把 v2 运行时接入的真实端到端验收登记为 **HUMAN_VERIFY / NOT_RUN**——本轮只有 dev server + dev mock 数据的真机截图，没有构建 Tauri 生产窗、也没有跑 Python Core。该 Task 的 R2 明确写着"不得宣称该项已通过"。
- **可观察交付**：在真实 Tauri 生产窗 + 真实 Python Core 下，四页各完成一次可复现的端到端走查并留下原始证据（进程、命令、exit code、截图/录屏、Core 侧日志），把 HUMAN_VERIFY 项逐条转成 PASS/FAIL/BLOCKED。
- **未释放原因**：需要构建环境（Rust/Tauri 工具链、Python Core 依赖、打包产物）与较长的构建时间；且"是否为此投入一轮构建"属于发布线取舍，应由用户裁决。因此本卡只登记范围，不认领、不执行。

## Acceptance Criteria（planned，未释放）

- [ ] **AC1 构建可复现**：记录工具链版本（node/npm/rustc/cargo/python）、构建命令、构建产物 SHA-256 与 exit code；不使用旧构建产物冒充本轮结果。 <<PARTIAL: planned，未执行>>
- [ ] **AC2 四页端到端**：真实 Core 下逐页走查——书架（列表/章节/页数/导入）、工作台（页图/区域/运行投影）、阅读器（页图/翻页/进度写回）、设置（12 分节读回与保存），每页给出截图与 IPC 命令序列。 <<PARTIAL: planned，未执行>>
- [ ] **AC3 页图 host 通道**：确认真实页图经 host HTTP 资源通道渲染（而非 dev 合成图），并记录首字节耗时与失败态。 <<PARTIAL: planned，未执行>>
- [ ] **AC4 故障面**：Core 掉线/重启时四页状态条与错误码表现，与 `ui/PageState` 的 blocked/error 面一致。 <<PARTIAL: planned，未执行>>
- [ ] **AC5 视觉差异**：WebView2 与 Chromium 的亚克力/噪声层渲染差异、高 DPI 与窄窗口表现；差异项如实记 HUMAN_VERIFY 或缺陷。 <<PARTIAL: planned，未执行>>
- [ ] **AC6 独立审查**：由未参与实现的 Agent 复核证据可复现性。 <<PARTIAL: planned，未执行>>

## 允许修改范围

- 本 Task、Handoff、`verification/UIUX-V2-RUNTIME-REALCORE-1/**`。
- 不允许修改产品源码；若端到端暴露缺陷，另立修复 Task（修复范围单独冻结）。

## 禁止范围

- 不改 IPC 契约/Schema/依赖；不 push；不删除既有证据；不使用用户原始漫画素材入库。
- 不得把 dev mock 数据、旧构建产物或"测试全绿"当作端到端证据。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `tauri build`（或 dev 启动）并记录工具链与 SHA | Rust/Tauri 工具链可用 | NOT_RUN（未释放） | 无 |
| AC2–AC5 | 真实窗口逐页走查 + Core 日志 | Python Core 可运行 | NOT_RUN（未释放） | 无 |

## 依赖、风险与阻塞

- 硬依赖：UIUX-V2-RUNTIME-1 已 `done`（集成 `af421b9e6`）。
- 阻塞：未释放（`proposed`）。解除条件：用户确认投入一轮构建；或给出可用的现成构建产物与 Core 启动方式。
- 风险：构建时间与磁盘占用较大；若 Rust 侧存在与本轮前端改动无关的既有构建失败，本 Task 应记录 BLOCKED 而不是修改前端去适配。

## 交付与运行记录

- 尚未释放、未认领、未执行。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| （待释放后填写） | — | — | - | - | CANONICAL |

## Resource Manifest

尚未产生资源；释放后按 `verification/UIUX-V2-RUNTIME-REALCORE-1/resource-manifest.json` 记录。

## Closeout Record

- Closeout date / DSH：未关闭（proposed）。
