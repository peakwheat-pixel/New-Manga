---
id: SETTINGS-ERROR-STATE-1
title: 设置页加载失败态的判别测试（闭合条件 3 矩阵唯一无覆盖格）
kind: test
governance_version: 3
status: done
disposition: "GATE3-COVERAGE-MATRIX §3 唯一「完全无覆盖」格（错误态/设置）；DSH 2026-11-15 释放"
approval: DSH 2026-11-15（纯测试补强，零生产代码改动）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - GATE3-COVERAGE-MATRIX
base_commit: 418801499
branch: main
worktree: G:/CODEX/New Manga
integration_commit: e50e7ebc932c22834c6ed2808b89de5ff62c8785
delivery_head: e50e7ebc9
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/SETTINGS-ERROR-STATE-1
allowed_paths:
  - doc/tasks/SETTINGS-ERROR-STATE-1.md
  - doc/reviews/SETTINGS-ERROR-STATE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/SETTINGS-ERROR-STATE-1/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
---

# SETTINGS-ERROR-STATE-1：设置页加载失败态的判别测试

## 来源与目标

`GATE3-COVERAGE-MATRIX` §3 的矩阵里，**唯一一格"完全无覆盖"是「错误态 / 设置」** ——
当时只有 `SettingsPage_HostUnavailable_IsBrowsableButReadOnly`（只读态），没有"加载失败态"测试。

**开卡前先核实现（按纪律）**，结论是：**实现早已存在**，缺的只是测试。

- `SettingsViewModel.LoadAsync`（`SettingsViewModel.cs:139-171`）有 try/catch：捕获任何异常后
  设 `State = FluentPageState.Error`、`Error = $"设置读取失败（{ex.GetType().Name}），可以重试。"`。
- 另有若干失败路径同样设 `Error`（外观保存失败 `:215-219`、coordinator 未注入 `:184-185`、
  只读拒绝 `:191-192`、`reason` 路径 `:198-199`）。

⇒ **本卡不改生产代码**，只补"可判别、能在回退时变红"的测试，并把矩阵该格改判。

**一个可观察交付结果**：当设置读取抛异常时，界面进入错误态并显示可重试文案；若该行为被回退
（异常被吞掉、状态停在 `Loading`/`ReadOnly`、或错误文案消失），测试必须失败。

## Acceptance Criteria

- [x] **AC1 VM 级判别测试**：注入一个在列举设置数据时抛异常的 Host，`await LoadAsync()` 后
      断言 `State == FluentPageState.Error`、`Error` 含"设置读取失败"与"可以重试"。
- [x] **AC2 视图级判别测试**：在真实 shell 里驱动同一失败，断言设置页内容为 `SettingsPageView`
      且**错误态可见**（不只是 VM 字段）。
- [x] **AC3 判别力实测**：临时把 `LoadAsync` 的 catch 改为吞掉异常（或去掉 `State = Error`），
      断言 AC1/AC2 变红；记录实验并**必须还原**。
- [x] **AC4 矩阵改判**：把 `MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` §3「错误态 / 设置」格
      从 ❌ 改为 ✅（带测试名 + 文件:行），并同步 §5 第 1/3 条与 Gate 评估 §15 中"唯一无覆盖"的表述。
- [x] **AC5 零回归**：`App.Tests` 全量 0 failed 且 skip **不增加**（当前 11）。
- [x] **AC6 零生产代码改动**：`git diff` 不触及 `apps/desktop-avalonia/src/**`。

## 允许修改范围

见 frontmatter。只新增测试、改矩阵该格与三指针。

## 禁止范围

- **不得**修改 `src/**`（实现已存在）。
- **不得**放宽既有断言、不得新增 skip/xfail。
- **不得**把"VM 字段为 Error"当作"界面显示错误态"的证据 —— AC2 必须走真实视图。
- 矩阵改判必须有测试依据，不得只改符号。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet test --filter SettingsErrorStateTests` | 无夹具 | **3 passed**（其中 AC1 1 项） | `verification/SETTINGS-ERROR-STATE-1/README.md` |
| AC2 | 同上（`[AvaloniaFact]` 驱动真实视图树） | 无夹具 | **PASS**：断言出现"设置错误"banner + "重试"按钮 | 同上 |
| AC3 | 临时把 `LoadAsync` 的 catch 改为吞异常（`Status = "PROBE swallowed " + ex.GetType().Name`） | 无夹具 | **2 failed / 1 passed**（`Expected: Error / Actual: Loading`）；对照测试 `HealthyLoad_DoesNotShowTheErrorBanner` 正确保持绿；已 `git checkout` 还原，`src/**` diff 归零 | 同上 |
| AC5 | `dotnet test tests/NewManga.App.Tests` | 无夹具 | **950 / 0 / 11 / 961**（本卡前 947/0/11/958，skip 未增加） | `four-pieces.log` |
| AC6 | `git diff --stat -- apps/desktop-avalonia/src` | 仓库根 | **0**（零生产代码改动） | 同上 |

## 依赖、风险与阻塞

- **硬依赖**：`GATE3-COVERAGE-MATRIX`（该格的出处）。
- **风险 R1**：`FakeHostController` 现有方法是否支持"抛异常"？若不支持，需要给 fake 增加可控失败开关
  （属测试替身扩展，不是生产代码）。
- **风险 R2**：设置页在错误态下是否仍渲染 `SettingsPageView`（而不是被 state host 替换）？
  需按实际渲染逻辑断言，不得凭猜测写断言。

## 交付与运行记录

- Handoff：`doc/reviews/SETTINGS-ERROR-STATE-1-review-r1.md`（独立复核 r1，verdict **ACCEPT_WITH_LIMITATIONS**，审查者 `review-settings-error`，未参与实现；被审 head `90dc51ded`）。
- Review：r1 独立上下文完成；复核者另做了"只回退视图 banner"的实验 → **仅 AC2 变红**，证明 AC2 是真实视图树断言而非只看 VM 字段。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。
### 自登记的错误（不淡化）

1. **探针两次没生效却险些当成"已验证"**：第一次用 PowerShell `.Replace()` 做 AC3 探针，字符串里的 `$"..."` 被
   PowerShell 插值，替换未发生、测试仍全绿；第二次改用 Python 后删掉了对 `ex` 的引用，触发 `CS0168` 编译失败
   （也不是"变红"）。第三次才得到真实的 **2 failed / 1 passed**。若前两次就此收工，"判别力已验证"是假的。
2. **越界改文档未登记**：AC4 要求改 Gate 评估 §15，但 `allowed_paths` 当时漏了该文件（r1 复核 P2-1 指出）。
   已补登记。
3. **矩阵格行号写错**：原写 `SettingsErrorStateTests.cs:44/:60`，实际是 `:35`（VM 级）与 `:53`（视图级）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-SES-01 | AC1/AC2/AC3 与实现核实 | verification/SETTINGS-ERROR-STATE-1/README.md | e50e7ebc9 | fbf84657a6d38422501947ee3c156eaaa12791f675e7d2c7dd5b5949c8792ce8 | CANONICAL | BLOB |
| EV-SES-02 | AC5 门禁与全量原始输出 | verification/SETTINGS-ERROR-STATE-1/four-pieces.log | e50e7ebc9 | 6cc981bb466fe8ade8f144260c0af6f9bcb495915061c6970a10e0a5e2003a35 | CANONICAL | BLOB |
| EV-SES-03 | AC1/AC2/AC5 测试本体 | apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsErrorStateTests.cs | e50e7ebc9 | 03342d0aa0b38618a553091a8c2307576dea493090ef62e6821093c9c8f3f69d | CANONICAL | BLOB |
| EV-SES-04 | 失败注入开关（测试替身） | apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs | e50e7ebc9 | afe16f2fe64889b54f1afd22ed96cf4eae63087527fef57125603fe84be70d45 | CANONICAL | BLOB |
| EV-SES-05 | 独立复核 r1（ACCEPT_WITH_LIMITATIONS） | doc/reviews/SETTINGS-ERROR-STATE-1-review-r1.md | e50e7ebc9 | 2ec9573919801d4c33c33fd35e7926ff4d04e68feb67775b90bf47e5b258ef9d | CANONICAL | BLOB |
| EV-SES-06 | AC4 矩阵改判（含范围限定） | doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md | e50e7ebc9 | d790c8dcd78baa79376acdcde401055466804f7155d868891df12658fa3afca2 | CANONICAL | BLOB |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 本卡无新增派生物 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`（6 条 BLOB pin，commit `e50e7ebc932c22834c6ed2808b89de5ff62c8785`）。
- resource_closeout_status：`complete`（无 worktree、无用户数据）。
- 删除、迁移、归档数量/字节数：0。
- **交付结论**：条件 3 矩阵里「错误态 / 设置」格由 ❌ 改 ✅；在**本矩阵限定的 4 页 × 13 类**内，
  ❌ 格已清零。**这不等于"产品 GUI 无缺口"** —— 仍有 2 个 ⚠️ 格、111 个 skip、以及 §0 未纳的流程。
- 未关闭项及保留原因：
  - 只覆盖"设置读取失败"一条失败路径；`SettingsViewModel` 另有外观保存失败、coordinator 未注入、
    只读拒绝等失败路径**未**逐条补测；
  - AC2 断言依赖"设置错误"/"重试"文案，文案改动会使测试变红（期望行为，但需同步矩阵措辞）；
  - 未送 r2 复审：r1 为 `ACCEPT_WITH_LIMITATIONS` 且无 P0/P1，P2/P3 已在本收口提交中处置。
- 当前指针清理：STATUS / Plan / TASK_LEDGER / rolling checkpoint 已更新。
- **本卡自身的错误登记**：① 两次 AC3 探针未生效（PowerShell 插值、删掉 `ex` 触发 CS0168）却险些
  当成"判别力已验证"；② 越界修改 Gate 评估文档未在 `allowed_paths` 登记（r1 P2-1）；③ 矩阵格行号写错
  （44/60 → 实际 35/53）。
