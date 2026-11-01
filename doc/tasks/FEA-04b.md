---
id: FEA-04b
title: Fluent 四页交互与视觉规格（设计基线）
kind: design
governance_version: 3
status: ready
approval: C-11_frozen_2026-11-01 + user_decisions_ADJ-2026-11-01
suggested_owner: zcode
owner: null
reviewer: null
depends_on:
  - FEA-00
base_commit: b6d5ccdef
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-04b
allowed_paths:
  - doc/tasks/FEA-04b.md
  - doc/design/fluent-v1/**
  - verification/FEA-04b/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-04b-*.md
---

# FEA-04b：Fluent 四页交互与视觉规格（设计基线）

## 来源与授权链

- 候选来源：方案 r4 §12.1（`:643`）+ §15.6（`:925`）
- 释放依据：**C-11 已冻结**（2026-11-01，[冻结记录](../plan/FEA-CONTRACT-FROZEN-C11.md)）→ 候选 → 建卡流程启用
- 用户裁决：[ADJ-2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)（U-04=批准 per-scheme 例外 / U-05a=纳入动效三态三类 / U-05c=A 用户优先）
- 上游契约：C-02（V11R 修订单，**已冻结**，V-05 定义 Fluent 视觉例外的边界）、C-03（外观持久化，**已冻结**，定义 `motion`/`corners`/`material` 字段）、C-05（页可见性，**已冻结**）

## 为什么是它先做

按 C-11 §7 的依赖序，S0/S1 中：
- `FEA-01` 稳定端口冻结：其交付含 **C-10 交互契约附件**，而 C-10 待 **U-03** 裁决 → **部分阻塞**
- `FEA-02`/`FEA-03`/`FEA-07`：依赖 FEA-01 → 阻塞
- `FEA-05` 三层注册与资源隔离：依赖 FEA-01/02 → 阻塞；且其视觉数值需 FEA-04b 基线
- **`FEA-04b`：只依赖 FEA-00（已完成），无生产写域，能解锁 FEA-05/06 的数值与结构基线** → 当前唯一可释放候选

## 交付范围（DSH 冻结）

| 项 | 内容 |
|---|---|
| 四页规格 | 书架 / 工作台 / 阅读器 / 设置——每页的布局、层级、状态、空态/错态/加载态 |
| 响应式 | 最小窗口、分栏折叠、双屏/拔屏、DPI 缩放 |
| 动效 | 按 C-03 的 `navigation`/`feedback`/`decorative` 三类给出参数（`reduce` 下的行为必须可验证） |
| 键盘与 a11y | 焦点顺序、快捷键（与 C-02 V-08b 的 `KeyMap` 一致）、高对比、屏幕阅读器标签 |
| 可测尺寸与组件 | 圆角（`Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)`）、材质（`Nm.Material.*`）、层次（`Nm.Elevation.*`）的具体取值 + 组件清单 |
| 版本化设计基线 | `doc/design/fluent-v1/` 下的规格文档 + 设计资产 + 版本号 |

## 验收标准

- [ ] **AC1 四页规格**：`doc/design/fluent-v1/` 下四页规格齐全，含所有状态（空/载入/错/满）与响应式断点。 <<PARTIAL: 待实现>>
- [ ] **AC2 令牌取值**：`Nm.Corner.Fluent.*`、`Nm.Material.*`、`Nm.Elevation.*` 的具体数值 + 与 C-02 V-05 判据①（必须走令牌）的对应表。 <<PARTIAL: 待实现>>
- [ ] **AC3 动效参数**：三类动效在 `auto`/`full`/`reduce` 下的时长/曲线表，满足 C-03 §2.3 判据 ①–⑤。 <<PARTIAL: 待实现>>
- [ ] **AC4 a11y 与键盘**：焦点顺序、快捷键、高对比、屏幕阅读器标签；与 C-02 V-08b `KeyMap` 无冲突。 <<PARTIAL: 待实现>>
- [ ] **AC5 用户确认与独立评审**：四页设计经用户确认 + 独立 Review（上下文独立）+ DSH 冻结。 <<PARTIAL: 待实现>>

## 禁止范围

- 不写生产源码（无 `src/`/`apps/` 写权）；不改冻结契约；不动用户数据；不 push。
- 设计资产不得引入许可不兼容的第三方字体/图标（GPL-3.0 兼容性须记录）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 规格文档评审 | 文档 | NOT_RUN | 待补 |
| AC2 | 令牌取值与 C-02 判据①对表 | 文档 | NOT_RUN | 待补 |
| AC3 | 动效表 vs C-03 判据 ①–⑤ | 文档 | NOT_RUN | 待补 |
| AC4 | 快捷键与 `KeyMap` 比对 | 文档 | NOT_RUN | 待补 |
| AC5 | 用户确认 + 独立 Review | 人工 | NOT_RUN | 待补 |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
