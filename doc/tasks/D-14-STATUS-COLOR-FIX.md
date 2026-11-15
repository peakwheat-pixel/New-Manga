---
id: D-14-STATUS-COLOR-FIX
title: 修复 StatusCatalog NotStarted 颜色键（D-14 裁决 A）
kind: implementation
governance_version: 3
status: done
approval: Codex CLI 裁决 A（doc/reviews/ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md，2026-11-03）；由 DSH 释放
suggested_owner: codex
owner: codex
reviewer: impl-r3 **approved**（ZCode CLI fresh session，P0=0/P1=0/P2=2；reviewed_head 4ae5163d9；报告 doc/reviews/D-14-STATUS-COLOR-FIX-impl-r3.md）
depends_on:
  - FEA-06-RESIDUAL-2
base_commit: 195422c2fdf72f0460d2e265b53e22a2c5eff6fd
branch: main
worktree: G:\CODEX\New Manga
integration_commit: e36a7442bd5f704252e4b0af8c63ab4f790000e1
delivery_head: 075dc1682f690bf6b2f902c8cc56fb0c1f7ebbfd（实现 5ecc1e4c6 + 证据补正；impl-r3 approved）
canonical_evidence_status: complete
resource_closeout_status: complete
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

## 验收结论（关闭）

- [x] **AC-1（NotStarted 映射 = NmKeys.Color.Text.Secondary）**：定向 3/3 + 独立复算。 <<MET>>
- [x] **AC-2（light/dark × Bg.Canvas/Bg.Panel 对比度 ≥4.5:1）**：独立复算 Dark 7.9566/7.1372、Light 6.3497/7.0459。 <<MET>>
- [x] **AC-3（不越权/回归/门禁）**：仅 Status.cs 单点+注释；1292/0/57、check PASS(3)、pins 15/15、旧四 PNG 未变、禁止范围 0。 <<MET>>

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| verification artifacts | verification/D-14-STATUS-COLOR-FIX/** | PRESERVE_REFERENCED | verification/D-14-STATUS-COLOR-FIX/integration-verification.log | e36a7442b（commit） | 集成日志被 Task/Review/Handoff 引用；SHA/pins 见 Task Canonical Evidence。 |
| worktree/task-env/dataset/model/test-material/temp/user data | 未创建/未访问 | NOT_APPLICABLE | - | - | 未创建 worktree/task-env；未访问用户数据；测试默认零写入。 |

## Closeout Record

- **终态**：done；关闭 2026-11-03；implementation 5ecc1e4c6，evidence/corrections 075dc1682，integration e36a7442b。
- **复核链**：impl-r1 changes_requested（P1=3 证据纪律）→ impl-r2 changes_requested（P1=1/P2=5）→ DSH 补正 → impl-r3 **approved**（ZCode CLI，P0=0/P1=0/P2=2）。
- **集成**：build 0/0；全量 **1292/0/57**（首次 CoreClient flake，重跑通过并记录）；check PASS(3)；pins 15/15；旧四 PNG 未变；禁止范围 diff=0。
- **残项（不阻断）**：STATUS/Task 生命周期与 Handoff 风险章节已按 r3 P2 补正；全仓若干历史 md 字符损坏（14 个）与 V2 NotStarted 前景分裂、FEA-06 旧特判/注释属仓库既有债，登记后续。
- **后续**：FEA-08（Source/回收站隔离原型）scope 已起草待独立 scope Review；D-15 推荐先于 FEA-09。
