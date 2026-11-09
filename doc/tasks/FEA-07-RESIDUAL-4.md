---
id: FEA-07-RESIDUAL-4
title: 既有 headless 用例隔离（legacy MainWindow 每轮 +16 行真实 AppData）与 FEA-07 后续 residual 收口
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：由 `FEA-07-RESIDUAL-3` closeout 的 L-R4b-1（D-R4b-7）re-home；**scope 未冻结，不得实施**；须先独立 scope review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-07
  - FEA-07-RESIDUAL-3
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07-RESIDUAL-4
allowed_paths:
  - doc/tasks/FEA-07-RESIDUAL-4.md
  - doc/reviews/FEA-07-RESIDUAL-4-*.md
  - doc/handoffs/FEA-07-RESIDUAL-4-*.md
  - verification/FEA-07-RESIDUAL-4/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-07-RESIDUAL-4：既有 headless 用例隔离 + FEA-07 后续 residual（占位）

## 来源（`FEA-07-RESIDUAL-3` closeout 登记）
- **L-R4b-1 / D-R4b-7**：既有 headless UI 用例 `Show()` 过 legacy `MainWindow` 且不传 `--log-dir`，**每轮 App.Tests 稳定 +16 行**真实 `%APPDATA%\com.newmanga.desktop\logs\window-material.log`（2026-10-27 起既有，非 R4b 引入）。修复方向：给这些用例补 `--log-dir`（或引入 `--home-root`），使默认套件**零真实 AppData 写入**。
- **L-R4b-2**：AC1「旧结果仅 candidate」证据弱（`region_candidates` 表不存在）→ 用生产 run/step 父行 + 真实陈旧候选补强。
- **L-R4b-3**：AC1 未过 `HostRuntime`/打包 sidecar；AC4 缩放「调用点」未被直接断言（真实 DPI 变化）。
- **L-R4b-4**：全量期间并发写 `verification/` 会触发既有 `FluentResidual2VisualEvidenceTests` 假红 → 静默树/串行门禁。
- **L-R4b-5**：未登记 pytest flake `tests/fea09/test_referenced_flow.py::test_replay_conflicting_fingerprint_rejected`（`sqlite3.InterfaceError`）。
- 规模性能 residual（L-R4a-3）：n50/n200/n500 p95 超 1000 ms，只记录。

## 拟做（待 scope review 冻结）
1. 默认套件真实 AppData 零写入（第一优先，红线级）；
2. 其余 residual 按 review 结论拆分/降级/立项。

## Scope review 结论（2026-11-09，r1）

- 报告：`doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md`（独立上下文子代理；base `a49311cbe`；`check.ps1` PASS / `verify_pins` 18/18）。
- **verdict：`NOT_RECOMMENDED`（现卡按现文：6 项 residual 混装）**；缩窄为 **L-R4b-1-only** 后 `READY-TO-FREEZE`。
- **L-R4b-1 仍存在（未修）**：默认 `NewManga.App.Tests` 有 **16 处** legacy `MainWindow.Show()` 未传 `--log-dir`（6 文件；清单见报告 §2.1），`MainWindow.ResolveDiagnosticsRoot` 无 `--log-dir` 时回退真实 `%APPDATA%\com.newmanga.desktop\logs`，每次 `Show()` 写 1 行。**仅补 `--data-root` 不能隔离**（P1/S-03）。
- 建议范围（报告 §3）：11 条写域 = 6 个既有测试文件（CredentialUi/F11Hotkey/LegacyAppearanceSync/ImportExportUi/RegionWorkbenchUi/ThemeRetirementR4）+ 新增 `LegacyWindowIsolationTests.cs` + 卡/评审/Handoff/`verification/FEA-07-RESIDUAL-4/**`；App 生产文件、共享组合根、PLAN/STATUS、契约/Python 零 diff。
- 建议 AC（报告 §4）：6 条 —— 站点完整、默认套件真实 AppData 零写入强断言（两棵树 delta=0，fail closed）、harness 自检可判别、真实 MainWindow `Show()` 隔离、回归门禁、residual 处置与证据。
- re-home（报告 §2.2）：L-R4b-2 → 候选证据另卡（SPLIT）；L-R4b-3 → HostRuntime 强化（SPLIT）+ 真实 DPI（DEFER，AC5 豁免）；L-R4b-4 → 运行纪律（DEFER）；L-R4b-5 → 本卡仅登记（零代码）；L-R4a-3 → 产品性能卡（DROP）。
- **释放前置**：`doc/REBASELINE_PLAN.md` 预算余 11 B/1 行，须先腾挪；冻结与释放由 DSH 裁决。`status` 保持 `proposed`，未冻结前不得实施。
