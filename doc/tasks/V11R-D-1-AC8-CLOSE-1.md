---
id: V11R-D-1-AC8-CLOSE-1
title: 核证 V11R-D-1 AC8（reduced-motion）在新壳已实现并闭合
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: ac8-review-r2（独立上下文子 agent，APPROVED_WITH_LIMITATIONS；r1 为 CHANGES_REQUESTED）
integration_commit: 654cd3e97
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - AC-BLOCKED-CLASSIFY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 C「AC blocked 项中可归因闭合项」
base_commit: 37c4cf0b3
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/V11R-D-1-AC8-CLOSE-1
allowed_paths:
  - doc/tasks/V11R-D-1-AC8-CLOSE-1.md
  - doc/tasks/V11R-D-1.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/V11R-D-1-AC8-CLOSE-1/**
---

# V11R-D-1-AC8-CLOSE-1：核证 reduced-motion 在新壳已实现

## 来源

`AC-BLOCKED-CLASSIFY-1` 把 `V11R-D-1` AC8 判为 `IMPL` 类（**当前树 live gap**），依据是：
`App.axaml:20` 仍 include 旧 `AppStyles.axaml`，其 `Border.nm-bookcard` 固定 `BrushTransition 0:0:0.12`
使「全应用 reduced-motion 未达」（DEVIATIONS D-12）。

## 调查结论（改变了判定方向）

深入读代码后发现**不是 live gap，而是「旧壳残留 + 新壳已修」**：

| 壳 | 入口 | reduced-motion |
|---|---|---|
| **新壳（产品默认）** `FluentShellSurface` | `App.axaml.cs:233` | **已完整实现**：`MotionTimings.Resolve` 在 reduce 时把 `FeedbackHoverMilliseconds` 归零（`MotionTimings.cs:62`）；`ApplyFeedbackTransitions` 在 attach 与每次 re-resolve 时清除按钮过渡（`FluentShellSurface.axaml.cs:790-820`）；维护 `motion-reduced`/`motion-feedback`/`motion-navigation` class（`:731-737`） |
| 旧壳（`--shell=legacy`） `MainWindow` | `App.axaml.cs:448` | 未响应：`AppStyles.axaml` 的 `Border.nm-bookcard` 固定 0.12s（D-12） |

⇒ `AppStyles.axaml` 的固定过渡**只影响已退役的旧壳路径**，不是产品默认路径的缺陷。

## 目标（一个可观察结果）

AC8 由 `blocked` 改判 `verified`，附「新壳机制点 + 测试通过数 + 旧壳残留如实披露」三项证据。

## Acceptance Criteria

- [x] **AC1 机制核证**：给出**默认壳 `builtin.current-v2`（项目侧 0 处动画声明）**与 **第二界面 `builtin.fluent`（`MotionTimings.cs:62` reduce 时归零）**的核证点。 <<MET>>
- [x] **AC2 测试实证**：跑 reduced-motion 相关测试，记录 passed/failed 与耗时、EXIT。 <<MET>>
- [x] **AC3 改判 + 如实披露**：AC8 改判 `verified`；注释同时写明**旧壳 `--shell=legacy` 的残留未响应**， <<MET>>
      不声称「全应用无条件达成」。
- [x] **AC4 不改代码**：本轮**不修改任何 `.cs`/`.axaml` 生产代码**（只核证与改判）。 <<MET>>
- [x] **AC5 不回归**：全局 `check.ps1` PASS；`verify_pins` 18/18；`api_inventory` 1/80/6=87； <<MET>>
      `verify_final.py` 计数 189→190 verified / 65→64 blocked。
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 禁止范围

- 不得为「让旧壳也达成」而改 `AppStyles.axaml` 或旧壳代码（旧壳已按 AD-002 退役）；
- 不得修改 `verification/V11R-D-1/**` 既有证据；
- 不得声称旧壳也满足。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| reduced-motion 测试 | `dotnet test … --filter "FullyQualifiedName~MotionMatrixResidual\|FullyQualifiedName~FluentMotionResidual\|FullyQualifiedName~MotionTimings"` | 13 passed / 0 failed |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-AC8-01 | AC1/AC3 核证总述（WORKTREE_ENV=Windows11+dotnet9） | verification/V11R-D-1-AC8-CLOSE-1/README.md | 654cd3e97 | 01505648eec8189397dc2fc1606fb01c30a00d13beeacb4be632c707f4f3e35c | CANONICAL | WORKTREE |
| EV-AC8-02 | AC2 reduced-motion 测试（13 passed）（WORKTREE_ENV=Windows11+dotnet9） | verification/V11R-D-1-AC8-CLOSE-1/motion-tests.log | 654cd3e97 | 33799cecabb2af06b0bc7bfcfcca42d04a9ad92be407a7864c3642e43bbe70c1 | CANONICAL | WORKTREE |
| EV-AC8-03 | AC1 默认壳与范围边界（V2 无动画 + FEA-00:25）（WORKTREE_ENV=Windows11+dotnet9） | verification/V11R-D-1-AC8-CLOSE-1/default-shell-and-scope.txt | 654cd3e97 | 1417d75ebeb0f323b66fed71429c7a8cbee25eb4f7376fb94fde4d84e2700979 | CANONICAL | WORKTREE |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/V11R-D-1-AC8-CLOSE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH；实现 `d01a2babd` + r1 返修 `654cd3e97`。
- **结果**：`V11R-D-1` AC8 由 `blocked` 改判 `verified`，按**受支持产品界面**口径：
  - 默认壳 `builtin.current-v2`：项目侧 0 处动画声明 ⇒ 无动画可禁；
  - 第二界面 `builtin.fluent`：完整链路 + 13 passed（更宽 55 passed）；
  - 旧壳 `--shell=legacy`：**明写不满足**，依 `FEA-00:25`（[建议] 级方案口径）不在受支持界面范围；
  - 焦点环 2px outline 与 §2.3 对比度：22 passed（`ContrastTokenTests` 等）。
- **独立复核两轮**：
  - r1 `CHANGES_REQUESTED`（0/2/3/3）—— 抓出**默认壳搞错**（`App.axaml.cs:233` 仅 presentation-host 可达）
    与**退役依据引错**（AD-002 指 Tauri 壳）；核心结论「verified 按提交形态过宽」。
  - r2 **APPROVED_WITH_LIMITATIONS**（0/0/3/4）—— 两个 P1 均关闭；剩余为文档层面。
    r2 的 P2-1（README 未随返修更新）/P2-3（AC 未勾选）/P3-3（引用精度）/P3-4（EXIT=1 未披露）
    已在本收口修正；P2-2（AC8 正文无条件表述，正文不可改）由注释 + D-12 缓解；
    P3-1（FEA-00:25 是 [建议] 非冻结契约）已在证据 §6 注明强度；
    P3-2（框架 knob 动画两壳同样不受 reduce、且无护栏）已在证据 §2 如实记录。
- **计数**：`verified 189 → 190`、`blocked 65 → 64`。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. 框架内置动画（`ToggleSwitch` knob）在两壳均不受 reduce —— **先存**，需另立卡；
  2. 无「V2 加动画后 reduced-motion 静默回退」的护栏（建议加 lint/回归测试）；
  3. AC8 正文无条件表述与注释限定存在张力（正文受 verify_final 约束不可改）；
  4. `V11R-D-1` 的 4 条先存 `-TaskPath` 错误（lifecycle v2 frontmatter 缺陷）未处理。
