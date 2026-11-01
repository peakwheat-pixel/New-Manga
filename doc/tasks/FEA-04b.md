---
id: FEA-04b
title: Fluent 四页交互与视觉规格（设计基线）
kind: design
governance_version: 3
status: in_review
approval: C-11_frozen_2026-11-01 + user_decisions_ADJ-2026-11-01
suggested_owner: zcode
owner: dsh-lead
reviewer: fea04b-scope-reviewer
depends_on:
  - FEA-00
base_commit: fdf7591ac
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

- [x] **AC1 四页规格**：`doc/design/fluent-v1/` 下四页规格齐全，含所有状态（空/载入/错/满）与响应式断点。 <<MET>>
- [x] **AC2 令牌取值**：`Nm.Corner.Fluent.*`、`Nm.Material.*`、`Nm.Elevation.*` 的具体数值 + 与 C-02 V-05 判据①（必须走令牌）的对应表。 <<MET>>
- [x] **AC3 动效参数**：三类动效在 `auto`/`full`/`reduce` 下的时长/曲线表，满足 C-03 §2.3 判据 ①–⑤。 <<MET>>
- [x] **AC4 a11y 与键盘**：焦点顺序、快捷键、高对比、屏幕阅读器标签；与 C-02 V-08b `KeyMap` 无冲突。 <<MET>>
- [ ] **AC5 用户确认与独立评审**：四页设计经用户确认 + 独立 Review（上下文独立）+ DSH 冻结。 <<PARTIAL: 用户确认未进行（自主推进）；独立 Review 待派发>>

## 禁止范围

- 不写生产源码（无 `src/`/`apps/` 写权）；不改冻结契约；不动用户数据；不 push。
- 设计资产不得引入许可不兼容的第三方字体/图标（GPL-3.0 兼容性须记录）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 规格文档评审 | 文档 | DONE（11 文件） | `doc/design/fluent-v1/` |
| AC2 | 令牌取值与 C-02 判据①对表 | 文档 | DONE（01 §2/§3） | `01-design-tokens.md` |
| AC3 | 动效表 vs C-03 判据 ①–⑤ | 文档 | DONE（02 §2/§3） | `02-motion.md` |
| AC4 | 快捷键与 `KeyMap` 比对 | 文档 | DONE（03 §1） | `03-accessibility.md` |
| AC5 | 用户确认 + 独立 Review | 人工 | PENDING（用户确认）/ 待派复核 | `verification/FEA-04b/` |

## Canonical Evidence

进入收口前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-FLUENT-README | AC1–AC4 | `doc/design/fluent-v1/README.md` | e173d156d | 2d7650aa475c2580e528fbc580087393c30f2268365a9dff77332fe8e64c7bc2 | CANONICAL |
| E-FLUENT-TOKENS | AC2 | `doc/design/fluent-v1/01-design-tokens.md` | e173d156d | c7dbdd8bffd2d7fd378eaf723a9d46ca48592febe271d2d39d8f74555c908ff9 | CANONICAL |
| E-FLUENT-MOTION | AC3 | `doc/design/fluent-v1/02-motion.md` | e173d156d | 5de25787b2191a26695336ae9c2d4bc82aa0960d11bd8033ab9cb159126117c7 | CANONICAL |
| E-FLUENT-A11Y | AC4 | `doc/design/fluent-v1/03-accessibility.md` | e173d156d | 412514945178669f429ade7717be49e09e8deb4ab4bcd82863de64ce286249de | CANONICAL |
| E-FLUENT-LAYOUT | AC1 | `doc/design/fluent-v1/04-layout-responsive.md` | e173d156d | 786ed96254b0d3e76959a3f703fe3ed941d4a9ba42966be8e8a3e0bd1b0605fa | CANONICAL |
| E-FLUENT-SHELF | AC1 | `doc/design/fluent-v1/05-page-shelf.md` | e173d156d | 619a8a7c60d1990a87a0f73af7886a28da20961b153a40b60da7dff64bcace7a | CANONICAL |
| E-FLUENT-WORKBENCH | AC1 | `doc/design/fluent-v1/06-page-workbench.md` | e173d156d | bb1e6b08e7e115e89d4de4294ae288c7bbd5da0f67f0471e88ae3aff80a48e5b | CANONICAL |
| E-FLUENT-READER | AC1 | `doc/design/fluent-v1/07-page-reader.md` | e173d156d | 7ed21cc308084ce6792d439895b6f42fefa55e9f4a48d4e61e5982bc82b46179 | CANONICAL |
| E-FLUENT-SETTINGS | AC1 | `doc/design/fluent-v1/08-page-settings.md` | e173d156d | af6b6d9c392b4c2b2d01c8617ec7d75be8e93ff356ab1670af3af8fd91086d25 | CANONICAL |
| E-FLUENT-STATE | AC1 | `doc/design/fluent-v1/09-state-matrix.md` | e173d156d | ed46c107aad1fbb7ab78c6b7c4f26efd0693db73e77ecb0840349d34abe9b126 | CANONICAL |
| E-FLUENT-COMPONENTS | AC1/AC2 | `doc/design/fluent-v1/10-component-inventory.md` | e173d156d | 1ec672367e926c0253f3bbcf049989969c34de440bafe0628e16592bc37129da | CANONICAL |
| E-FLUENT-SELFCHECK | AC1–AC5 | `verification/FEA-04b/design-baseline-selfcheck.md` | e173d156d | c127a8f65441ee41921ac508fac1595fb4b31e250738a3f892928059d2256f23 | CANONICAL |

## Resource Manifest

无 worktree、无临时产物；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。

- 2026-11-02 / DSH：起草 `doc/design/fluent-v1/`（README + 01–10，版本 `fluent-v1.0.0`）与自查清单 `verification/FEA-04b/design-baseline-selfcheck.md`；AC1–AC4 文档完成，待独立复核；AC5 用户确认待办（自主推进模式），独立复核已派发。状态置 `in_review`。
