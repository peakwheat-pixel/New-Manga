---
id: FEA-04-IMPL-1
title: FEA-04 下游实现（Current 适配：Frontends.Current + V2 state/route/VM adapter；保留旧入口）
kind: implementation
governance_version: 3
status: closed_with_limitations
approval: 承接 doc/tasks/FEA-04.md 的范围冻结（approval dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q20；scope 复核 approved doc/reviews/FEA-04-scope-r1/r2）；本卡只承接实现，不重开范围
suggested_owner: zcode
owner: null
reviewer: null
depends_on:
  - FEA-04
base_commit: a42af804b
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-04-IMPL-1
allowed_paths:
  - doc/tasks/FEA-04-IMPL-1.md
  - doc/tasks/FEA-04.md
  - doc/reviews/FEA-04-impl-*.md
  - doc/handoffs/FEA-04-IMPL-1-*.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/V2/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/**
  - verification/FEA-04-IMPL-1/**
---

# FEA-04-IMPL-1：FEA-04 下游实现

> ## ⛔ 本卡已撤销（2026-11-16，DSH）—— 是我建错了，保留以免重犯
>
> **本卡的前提是错的。** 我（DSH）在 R11 建这张卡时，依据是 `FEA-04` 卡面上
> 「AC1–AC8 一律标 `blocked: 实现未开始`」这句话，推断「实现还没开始，需要一张实现卡」。
> **我没有先核实实现是否已交付** —— 这是流程错误。
>
> 2026-11-16 核实结果：**FEA-04 的实现早已交付并通过独立复核**：
> - 代码在：`Shell/V2/Frontends/CurrentFrontend.cs`（12493 B）、`CurrentSessionMemento.cs`（4112 B）、
>   `Views/V2/Route/CurrentRouteAdapter.cs`（1642 B）
> - 测试在：`tests/NewManga.App.Tests/FEA04CurrentAdapterTests.cs`（16804 B，17 项）
> - 证据在：`verification/FEA-04/`（baseline-comparison / preflight-blocker-matrix / lifecycle-assertions /
>   sln-test-results / build-test-raw.log / git-diff-check / governance-check / verify-pins）
> - 复核在：**`doc/reviews/FEA-04-r3.md` = `approved`（P0=0 / P1=0，reviewed_head `af9625e7e`）**，
>   且 r3 `:105` 明写「AC1–AC7 在 head 均有实测/证据支撑（本席位独立复跑 931/0/60、0 failed）」
>
> ⇒ `FEA-04` 的 AC1–AC8 **已逐条依据既有证据闭合**（见该卡各 AC 注释，含基线 commit 替换与 AC8 点名矛盾两处诚实登记）。
> **本卡的 8 条 AC 从未需要单独实现，全部撤销为 `NOT_APPLICABLE`。**
>
> **教训（已写入交接包）**：卡面的 `blocked: 实现未开始` **不等于**「实现不存在」——
> 处理任何 blocked AC 前，**先核实现/测试/证据/复核是否已存在**，再决定是补证据还是立新卡。
> 这与 R11 在 `M2-SFX` AC4 上踩的是**同一类错**（blocked 理由会过期）。


## 为什么需要这张卡（不要重开范围）

`doc/tasks/FEA-04.md` 是**范围冻结卡**，它自己写得很清楚（`AC-CHECKBOX-AUTHORITY-1` 语义登记，2026-11-15）：

> 本卡是**范围冻结卡**。`status: done` 表示**范围冻结与 scope 复核完成**，
> **不代表 AC1–AC8 已满足** —— 那些是**下游实现**的验收条件，本卡只冻结范围。
> 因此下述 AC 一律标 `blocked: 实现未开始`，不冒充完成。

⇒ `FEA-04` 的 AC1–AC8 **不是本卡欠账**，而是**缺一张实现卡**。
在实现卡出现之前，这 8 条既不能关闭、也不该被当成「可闭合项」——它们是**无路径项**。
本卡即为该缺失的实现卡：**只承接实现，不重新讨论范围**。

**范围与规则一律以 `doc/tasks/FEA-04.md` 为唯一权威**，本卡不复制第二份定义，只引用：

| 内容 | 权威位置 |
|---|---|
| 来源与授权（方案 §12.1/§15.3/§15.6） | `doc/tasks/FEA-04.md` §来源与授权 |
| DSH 裁决 Q-16…Q-20（不实现 wire / csproj 单点例外 / 目录归属 / switch 只做 preflight / blocker 形状冻结） | 同上 §来源与授权 第 5 条 |
| 冻结设计规则 **R-CURRENT-1…3 / R-STATE-1…4 / R-SWITCH-1…3** | 同上 §冻结设计规则 |
| **§15.3 迁出表（S1–S6 逐项「现状 → 新权威 → 验收」）** | 同上 §15.3 迁出表 |
| 写域（Q-17/Q-18） | 同上 frontmatter `allowed_paths` + Q-18（`Frontends.Current`→`Shell/V2/Frontends/`、route adapter→`Views/V2/Route/`） |

## Acceptance Criteria —— **全部撤销（NOT_APPLICABLE）**

> 本卡撤销，故 8 条 AC 一律 `NOT_APPLICABLE`。原始 AC 文本仍在下方**保留不改**，便于审计「当初想做什么」；
> 其实际达成情况见 `doc/tasks/FEA-04.md` 的对应 AC 注释（已有证据闭合）。

- [x] **AC1 旧入口保留** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC1 已依据既有证据闭合>>
- [x] **AC2 行为基线不退化** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC2 已依据 baseline-comparison.md 闭合>>
- [x] **AC3 无第二份业务真值** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC3 已依据 Handoff 私有状态审计 + r3 闭合>>
- [x] **AC4 §15.3 六项迁出** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC4 已依据 S1–S6 对照表 + 未迁出登记 + r3 闭合>>
- [x] **AC5 fail-closed preflight** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC5 已依据 preflight-blocker-matrix.md（17/17）闭合>>
- [x] **AC6 生命周期** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC6 已依据 lifecycle-assertions.md 闭合>>
- [x] **AC7 回归与证据** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC7 已依据 verification/FEA-04/ 齐备闭合>>
- [x] **AC8 独立复核** —— <<NOT_APPLICABLE: 本卡撤销；FEA-04 AC8 已依据 FEA-04-r3.md approved(P0=0/P1=0) 闭合>>

### 原始 AC 文本（保留不改，仅供审计）



> 以下 8 条**逐条承继**自 `doc/tasks/FEA-04.md` 的冻结 AC（语义不变，不新增不弱化）。
> 判据写法与 `FEA-04` 完全一致，便于交叉核对。

原拟｜**AC1 旧入口保留**：公开签名/路由不变；`git diff` 只允许内部实现 + 适配层新增，每处改动 Handoff 说明。
      （依据 R-CURRENT-1）
原拟｜**AC2 行为基线不退化**：`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings`
      在 `91be6c134` 的逐工程计数为基线；实现后同命令逐工程 **≥ 基线**（Handoff 附前后表）。
      不允许弱化断言，只允许新增。（依据 R-CURRENT-2）
原拟｜**AC3 无第二份业务真值**：VM 私有状态清单（Handoff）逐项区分 **UI 态 / 业务态**；业务态读取统一经
      R-STATE-1 的权威源；**新增私有缓存/registry 字段零个或逐项说明**。（依据 R-STATE-3）
原拟｜**AC4 §15.3 六项迁出**：S1–S6 每项给出「现状字段 → 新权威 → 断言」；**未迁出项必须在 Handoff 明确登记**
      （不得静默省略）。（依据 R-STATE-1 + §15.3 表）
原拟｜**AC5 fail-closed preflight**：Q-20 五个 blocker 各有用例
      （`PENDING_REGION_TYPE` / `PENDING_CONFIRMATION` / `UNFLUSHED_RUN_KEY` / `UNMAPPED_READER_ANCHOR` / `UNMAPPED_SHELL_STATE`）；
      存在任一 blocker → `allowed=false` + 返回对应 `PreflightBlocker(Code, Source, Detail)` + **零 Host/Core 副作用**；
      无 blocker → `allowed=true` 且**不触发新 Run**。（依据 R-STATE-2 + R-SWITCH-1/2）
原拟｜**AC6 生命周期**：关闭/重建内容前后 `hostBefore`/`hostAfter` 满足
      `ReferenceEquals(hostBefore, hostAfter)`；`FakeHostController.StartCalls` / `HostController.StartRequests` 计数**不增**。
      （依据 R-STATE-4）
原拟｜**AC7 回归与证据**：sln 测试日志、基线对照表、preflight blocker 矩阵入 `verification/FEA-04-IMPL-1/**`。
原拟｜**AC8 独立复核**：实现复核 `doc/reviews/FEA-04-impl-r1.md` **approved（P0/P1=0）**。
      （范围复核已由 `FEA-04` 完成，本卡不重复；本条只要求**实现面**复核）

## 建议交付批次（按依赖排序，可分批提交）

| 批 | 内容 | 对应 AC | 说明 |
|---|---|---|---|
| **B0** | 冻结基线测量：在 `91be6c134` 上跑 R-CURRENT-2 命令，产出**逐工程基线表**入证据目录 | AC2（前置） | **必须先做**，否则 AC2 无法判定 |
| **B1** | `Frontends.Current` 骨架（`Shell/V2/Frontends/`）+ route adapter（`Views/V2/Route/`），只做**转发与状态映射** | AC1、AC3 | 不实现 wire、不启动 Fluent（Q-16/Q-19） |
| **B2** | `preflight` + 5 个 blocker + `PreflightBlocker` 形状（Q-20 冻结） | AC5 | 先写**失败用例**再写实现；零副作用要有断言 |
| **B3** | 生命周期（R-STATE-4）：关闭/重建不 Dispose Host、不隐式 Start | AC6 | `ReferenceEquals` + `StartCalls` 不增 |
| **B4** | §15.3 六项迁出（S1–S6 逐项），未迁出项在 Handoff 登记 | AC4、AC3 | 逐项「现状→新权威→断言」 |
| **B5** | 回归与证据 + 独立复核 | AC2、AC7、AC8 | 复核须**上下文独立**（作者可派子 agent） |

## 禁止范围

1. **不重开范围**：不得改 `FEA-04` 的冻结规则、§15.3 表、Q-16…Q-20 裁决。要改须先由 DSH 出书面裁定。
2. **不实现 wire**（Q-16）：S1–S3 权威为 ApplicationCore 本地；S4 只做映射、不新增命令；wire 归 FEA-05/FEA-07。
3. **不实现切换执行 / 不启动 Fluent / 不改运行期路由**（Q-19 / R-SWITCH-3）：switch 只做 preflight。
4. **不新建工程、不改 sln**（Q-18）；`NewManga.App.csproj` 加 `NewManga.ApplicationCore` 引用是**唯一单点例外**（Q-17），须在 Handoff 记录。
5. **不弱化既有断言**（R-CURRENT-2）：只允许新增测试，不允许放宽/删除。
6. **不做机器绑定**：不得在代码里硬编码用户路径（参见 `GOV-DECLARATION-SCAN-CLEANUP-1` 登记的 R-2 教训）。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 基线 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` | `91be6c134` 检出 | NOT_RUN | 待填 |
| AC2 实现后 | 同上（当前 head） | 仓库 | NOT_RUN | 待填 |
| AC5 blocker | `dotnet test tests/NewManga.App.Tests --filter FullyQualifiedName~Preflight` | 仓库 | NOT_RUN | 待填 |
| AC6 生命周期 | 同上 `--filter FullyQualifiedName~Lifecycle` | 仓库 | NOT_RUN | 待填 |
| AC4 迁出 | 同上 `--filter FullyQualifiedName~StateMigration` | 仓库 | NOT_RUN | 待填 |
| AC7 门禁 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库 | NOT_RUN | 待填 |

## 与 `FEA-04` 的关系（关账口径）

- `FEA-04` 的 AC1–AC8 **保持 `[ ]` + `blocked: 实现未开始`**，并在其卡面追加一条 append-only 注记
  指向本卡 —— **不把范围冻结卡伪装成实现完成**。
- 本卡 `done` 的判据 = 自身 AC1–AC8 全部达成 + AC8 独立复核 approved。
- 本卡完成后，`FEA-04` 的 AC1–AC8 才可**依据本卡的证据**依次翻 `[x]`；
  在此之前任何一方都不得声称「FEA-04 已实现」。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

| EV-IMPL1-RETRACT | 撤销记录 | `verification/FEA-04-IMPL-1/RETRACTION.md` | 28f146037 | `6c9231988c932cff3b3e6116d1cb5ce15237e59d485c7cfab8bd40413f00e297` | `CANONICAL` |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/FEA-04-IMPL-1/ | NOT_APPLICABLE | - | - | 本卡撤销，无实现产物；仅一份撤销记录 |
