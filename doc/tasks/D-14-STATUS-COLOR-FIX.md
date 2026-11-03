---
id: D-14-STATUS-COLOR-FIX
title: 修复 StatusCatalog NotStarted 颜色键（D-14 裁决 A）
kind: implementation
governance_version: 3
status: in_progress
approval: Codex CLI 裁决 A（doc/reviews/ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md，2026-11-03）；由 DSH 释放
suggested_owner: codex
owner: codex
reviewer: impl-r1 changes_requested（P1=3）→ impl-r2 changes_requested（P1=1/P2=5，仍证据纪律）→ 已 r2 补正（完整日志+57 skip 明细+模板 Handoff+pin 修正）；**impl-r3 复核中**
depends_on:
  - FEA-06-RESIDUAL-2
base_commit: 195422c2fdf72f0460d2e265b53e22a2c5eff6fd
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 5ecc1e4c6e1b99a9b53ad0d9bcd11d7489ee36e2（DSH/D-7 实施，独立 impl Review 待）
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/D-14-STATUS-COLOR-FIX
allowed_paths:
  - doc/tasks/D-14-STATUS-COLOR-FIX.md
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Controls/Status.cs
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - verification/D-14-STATUS-COLOR-FIX/**
  - doc/handoffs/D-14-STATUS-COLOR-FIX-*.md
  - doc/reviews/D-14-STATUS-COLOR-FIX-*.md
---

# D-14：StatusCatalog NotStarted 颜色键修复

## 背景与裁决
- 冲突：`StatusCatalog.ColorKey(NotStarted)` = `Nm.Color.Text.Disabled`，而 `Controls.Status.axaml` 的 `StatusGlyph.notstarted` 与普通状态文字使用 `Nm.Color.Text.Secondary`（注释要求 ≥4.5:1 可读）。
- **Codex 裁决 A**（`doc/reviews/ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md`）：将 `StatusCatalog.ColorKey(StatusKind.NotStarted)` 改为 `NmKeys.Color.Text.Secondary`，保留样式 Secondary 映射，修正 XML 注释；不新增颜色令牌/枚举/API 字段。
- 依据：两套普通主题中 Secondary 对比度均 ≥4.5:1，Disabled 均不足（裁决报告 §2）。

## 范围
- IN：`StatusCatalog.ColorKey` 单点修改 + 注释；新增/更新测试断言 `ColorKey(NotStarted) == NmKeys.Color.Text.Secondary`、catalog 与 StatusGlyph 样式一致、NotStarted 文本对比度 ≥4.5:1（两套主题）。
- OUT：不改其它 StatusKind 映射、不改样式令牌、不改 FEA-06-RESIDUAL-2 已提交的证据与测试（其 NotStarted 特判可在本卡后续清理，需保留证据字节）。
- BLOCKED：无。

## 验收
```
dotnet build apps\desktop-avalonia\NewManga.sln --nologo
dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo
pwsh -NoProfile -File tools\governance\check.ps1
pwsh -NoProfile -File tools\governance\verify_pins.ps1
```
基线 1292/0/57 只增不减；旧证据字节不变；不 push。

## 交付
commit + `verification/D-14-STATUS-COLOR-FIX/impl-verification.log` + `doc/handoffs/D-14-STATUS-COLOR-FIX-impl.md`；完成后独立 impl Review。

## 实施记录（DSH，D-7 故障转移）

- 背景：Codex 限额至 10:25、ZCode retry ≈08:05；按 D-7 由 DSH 实施、独立 Review 后关闭。
- 变更：StatusCatalog.ColorKey(StatusKind.NotStarted) → NmKeys.Color.Text.Secondary + XML 注释；新增 D14StatusNotStartedTests（catalog 映射 + light/dark × Bg.Canvas/Bg.Panel 对比度 ≥4.5:1）。
- 验证：build 0/0；定向 3/3 PASS；无过滤全量 **1292/0/57**；check PASS(3)；pins 15/15。
- 证据：verification/D-14-STATUS-COLOR-FIX/impl-verification.log（SHA 289384ade531880e08b6ca3911635de5b0c761c8c415e0a25e5015592b582ff9，commit 5ecc1e4c6）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-D14-IMPL | AC-映射/对比度/回归 | verification/D-14-STATUS-COLOR-FIX/impl-verification.log | 075dc1682 | e699fe813905e16dfac35eef36af7a3602f7c20d25109ba07703421d9055f681（git blob，复现：git cat-file -p 075dc1682:verification/D-14-STATUS-COLOR-FIX/impl-verification.log） | CANONICAL |

## 后续节点

- 本卡关闭后无现成 READY 节点（FEA-09…13 端口线未实例化）；待裁决 **D-15（已修正）**：D-14 后按顺序先起草 **FEA-08（Source/回收站隔离原型）** scope 草案（FEA-09 依赖 FEA-08，不应先行）；推荐由 DSH 起草并派独立 scope Review，否则等待用户指定。
