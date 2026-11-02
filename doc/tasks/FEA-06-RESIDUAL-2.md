---
id: FEA-06-RESIDUAL-2
title: Fluent 视觉残项补做（AC2 视觉格 / D-8 decorative 动画）
kind: implementation
governance_version: 3
status: ready
approval: 由 DSH 于 2026-11-03 依据 FEA-06-RESIDUAL-1 closed_with_limitations 的 AC2 PARTIAL/D-8 残项释放；范围待 scope 复核后冻结
suggested_owner: zcode
owner: zcode
reviewer: 待 scope 复核
depends_on:
  - FEA-06-RESIDUAL-1
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-2.md
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - verification/FEA-06-RESIDUAL-2/**
  - doc/handoffs/FEA-06-RESIDUAL-2-*.md
  - doc/reviews/FEA-06-RESIDUAL-2-*.md
---

# FEA-06-RESIDUAL-2：Fluent 视觉残项补做

## 来源
`FEA-06-RESIDUAL-1` 已 `closed_with_limitations`（impl-r4 approved：P0=0/P1=0/P2=1；集成 `669a4ae02`；全量 1245/0/57）。其 AC2 为 PARTIAL，残项经 DSH 登记转本卡。

## 范围（草案，待 scope 复核冻结）
- **IN-1（D-8）**：decorative 三类视觉动画（书架背景渐变 8s 循环、阅读器翻页装饰粒子 400ms、空态插画漂浮 6s）实现 + reduce/category-off 静态降级 + 视觉证据；仅消费冻结 `02-motion.md` 参数。
- **IN-2（I-4 视觉格）**：FEA-06-RESIDUAL-1 组件矩阵中仍 NOT_RUN 的纯视觉状态格（Toast 其余 severity、loading/checked 等）补视觉证据；既有断言只增不减。
- **BLOCKED**：B-5 原生 a11y/DPI/桌面矩阵（D-1 无硬件）。

## 验收草案
- decorative 在 full/auto 真实播放、reduce 禁用；无布局/层级/可读性变化；可复核视觉证据。
- 视觉格逐格证据；全量 1245/0/57 只增不减；旧 FEA-06 PNG 字节不变；check/pins/生成器通过；不 push、不改 Current V2/生成物/冻结设计。