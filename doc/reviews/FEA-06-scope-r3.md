---
task_id: FEA-06
reviewer: subagent_zcode
reviewer_kind: subagent
author: dsh-lead
base_commit: 53060cd6749b9daa304fe11fd80525d9cdc9fb08
reviewed_head: 3c7f311d88b24bde462a61690e15d2c66f8c4683
decision: approved
counts: { P0: 0, P1: 0, P2: 3 }
---

# FEA-06 范围冻结复核 r3（增量轮：r2-P0/P1 处置 + 无新问题）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06.md`（`proposed`，Fluent UI 四页实现；`owner: codex`（用户 2026-11-02 指派，W-10）） |
| base_commit | `53060cd6749b9daa304fe11fd80525d9cdc9fb08`（`git merge-base` 直系父，为被审 head 的直接父） |
| reviewed_head | `3c7f311d88b24bde462a61690e15d2c66f8c4683`（`fix(fea-06): 处置 scope-r2 P0/P1…`；6 文件 +213/−12：`App.axaml.cs` 1 行、`FluentShell.axaml.cs` +48、`FluentShellTests.cs` +6、卡 +32、checkpoint §33 +6、r2 报告入库） |
| reviewer | **subagent_zcode**——DSH Lead 经 `subagent_zcode` 派发的**独立上下文子代理**；本席位未参与 FEA-06 的任何起草、范围处置（含本被审 commit）或实现，符合 2026-10-31 上下文独立裁决 |
| 日期 | 2026-11-02（r3 轮） |
| 审查对象 | 仅两项：r2-P0（Fluent 壳依赖注入预置，W-12）与 r2-P1（AC2–AC5 对齐 09 状态矩阵）的处置充分性；P2 抽查；本次修复是否引入新 P0/P1。**不重开全量范围复核**（r2 已完成的写域/组件 AC/治理指针等结论不复查） |
| 结论 | **approved**（P0=0 / P1=0 / P2=3）——**FEA-06 可置 `ready` 并按 W-10 释放 Codex**（释放前动作见 §7） |
| 前置核实 | `git rev-parse HEAD` = `3c7f311d…` ✓；`git status --short` 空（clean）✓；`git log --oneline -4` 链一致 ✓ |

> **一句话结论**：r2-P0 已按 r2 报告建议①精准落地——组合根 Fluent 分支一行传参 + `FluentShell` 可选参数/只读属性 + 组合根测试三 `Assert.Same`，V2/legacy 分支与 selector 语义零改动，全量 **1022/0/57** 与基线逐位一致；r2-P1 已兑现——AC2–AC5 四列与 `09-state-matrix.md:8-16` **逐行一致**（含「—」列说明），「未就绪」术语错位已除。r2 的 10 条 P2 中 6 条入卡、4 条入派发 brief，抽查全部落实。新发现仅 3 条 P2 级注记（任务拆解 P3 摘要行「8 态」旧口径残留、派发 brief 正文两处滞后、approval/STATUS 轮次字段滞后），均不阻塞释放，随 DSH 释放前刷新动作一并处理即可。

---

## 0. 方法与只读声明

- 只读核查被审 head；除本报告外未修改任何源码/卡/契约/STATUS/PLAN/LEDGER/证据；未 commit/push。本报告为本轮唯一新增文件。
- 本轮实测（全部在 `3c7f311d8` 工作区）：
  - `git diff --stat 53060cd67..3c7f311d8` → 6 文件 +213/−12（与处置声明一致；代码面仅 3 文件）。
  - `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` → **exit 0，0 警告 / 0 错误**。
  - `dotnet test …NewManga.sln --no-build --settings …NewManga.runsettings` → **全量 1022 passed / 0 failed / 57 skipped**（Appearance 21/0/0、Host 51/0/28、ThemeEngine 253/0/0、DesignSystem 86/0/0、ApplicationCore 31/0/0、CoreClient 128/0/22、App 452/0/7；与 AC8 基线及 PREREQ-2 集成口径逐位一致；r2 轮的 CoreClient 时间敏感 flaky 本轮首跑即未复现）。
  - `pwsh -NoProfile -File tools/governance/check.ps1` → **PASS（3 warnings：9 非终态 Task；STATUS 3196B/29 行 80%；PLAN 4100B/62 行 80%——与 r2 轮完全相同，非本处置新增）**；`verify_pins.ps1` → **PASS（all 15）**。
- 行号全部基于 `3c7f311d8` 实测。

---

## 1. r2-P0 闭环核验（Fluent 壳依赖注入预置，W-12）——**已闭环**

| 核验点 | 判定 | 证据（文件:行号） |
|---|---|---|
| 组合根 Fluent 分支传入三实例 | ✓ | `App.axaml.cs:137-138`：`return selection.IsFluent ? FluentShell.CreateRoot(options, selection, controller, appearance, themeManager)`——`controller`（`:77` 构造的唯一 `HostController`）、`appearance`（`:66-69` 构造的唯一 `AppearanceCoordinator`）、`themeManager`（`_designSystemTheme`）全部进入 Fluent 壳 |
| V2/legacy 分支语义未变 | ✓ | `App.axaml.cs:133-134` `--shell=legacy` 优先分支（`CreateLegacyShell(controller, options, themeManager)`）与 `:139` V2 分支（`CreateV2Shell(application, controller, options, themeManager, appearance, themeHome)`）逐字未动；selector `FrontendSelector.Select(options.FrontendId, appearance.FrontendId)`（`:75`）未动。`git diff` 证实 `App.axaml.cs` 全文件仅 1 行变更（即 `:138` 传参行） |
| `FluentShell` ctor/`CreateRoot` 扩为可选参数 | ✓ | `FluentShell.axaml.cs:76-82` ctor 五参全部带 `= null` 默认值（`options/selection/host/appearance/themeManager`）——既有 `(options, selection)` 与无参调用保持源兼容；`:138-144` `CreateRoot` 同样五可选参数并转发 |
| 暴露只读属性三件 | ✓ | `FluentShell.axaml.cs:121` `public IHostController? HostController { get; }`、`:127` `public AppearanceCoordinator? Appearance { get; }`、`:132` `public DesignSystemThemeManager? ThemeManager { get; }`——均只读属性，XML doc 明示「single shared」语义与「never by constructing a second controller」禁令 |
| 测试断言三实例同一 | ✓ | `FluentShellTests.cs:122` `CompositionRoot_DispatchesToFluentV2AndLegacyShells`：`:146` `Assert.Same(controller, fluentShell.HostController)`、`:147` `Assert.Same(coordinator, fluentShell.Appearance)`、`:148` `Assert.Same(manager, fluentShell.ThemeManager)`；同一测试内 V2（`Assert.IsType<AppShellV2>`）与 legacy（`Assert.IsType<MainWindow>`，且 selector 指向 fluent 时仍走 legacy）分支断言**全部保留在场**——测试纯增强（+6 行），未削弱 |
| 无自建第二 Host/Coordinator 残留 | ✓ | 全 src/ 源码 grep `new HostController\|new AppearanceCoordinator\|new AppearanceStore`：仅组合根 `App.axaml.cs:66/77` 两处构造（单实例语义保持）；其余命中全部在 `tests/**`（测试自建临时实例，各自独立 TempRoot 路径与生命周期，合法）。`FluentShell.axaml.cs` 内无任何构造 |
| 依赖注入足以支撑 AC2–AC5 | ✓ | **AC2** 书库读：经注入的 `IHostController`；**AC3** Draft 7 方法：`IHostController.cs:422-458`（`OpenDraftAsync:422`/`PatchDraftAsync:430`/`PrepareCandidateAsync:437`/`ApplyCandidatesAsync:445`/`GetDraftAsync:450`/`ListDraftsAsync:454`/`DiscardDraftAsync:458`）经 W-2 指定的同一接口可达；**AC4** 进度保存：`IHostController.cs:116` `interface IHostController : IReaderProgressSink, IRunController, …`——注入实例即承载进度面；**AC5** 外观保存：`AppearanceCoordinator.cs:67` `SaveAsync`（`:21` 类注释明示 owns SaveAsync，唯一写者）经注入的 `Appearance` 实例直达；令牌/主题面经 `ThemeManager`。四页 ViewModel 从壳只读属性取用即为合法通路，无需触碰组合根 |
| W-12 与 W-9/AC10 自洽 | ✓ | W-12（卡 `:133`）明示「DSH 单点预置……`App.axaml.cs` 仍不在 FEA-06 写域」；W-9（卡 `:130`）「不含 `App.axaml`/组合根」未改；本次组合根改动由 DSH 在处置 commit 内完成、不属于 Codex 实现写域，AC10 范围纪律不受影响；front matter `allowed_paths`（卡 `:26-42`）与 r2 版逐项一致——**写域未被扩权** |

---

## 2. r2-P1 闭环核验（AC2–AC5 对齐 09 状态矩阵）——**已闭环**

对照基准：`09-state-matrix.md:8-16`（9 状态行 × 四页列）。逐列核验（全部基于 `3c7f311d8` 实测）：

| 页 | AC 位置 | 逐行对照结果 |
|---|---|---|
| **AC2 书架** | 卡 `:100` | 09 书架列 9 行**全部在列**：空〔首次空态+导入主按钮〕✓ / 空〔筛选后，保留筛选+清除筛选〕✓ / 载入〔6 封面骨架+「正在读取书架…」〕✓ / 错误〔错误卡+重试+控制台入口〕✓ / **满〔网格/列表+统计〕✓（r2 缺项已补）** / 部分〔扫描中进度条；已就绪项可用〕✓ / **只读〔顶部警示；导入/删除禁用〕✓（「未就绪」术语错位已改为 09/05 术语「只读」）** / 运行中〔扫描/导入进度，与部分同态不重复计数〕✓ / 冲突列「—」✓（含说明） |
| **AC3 工作台** | 卡 `:101` | 09 工作台列 **9 行全部在列**（AC 明写「全部 9 行实现」，r2 缺的 2 行已补）：空〔未选章节→跳书架；批量无 Run→「开始处理」〕✓ / **空〔批量筛选无结果→保留 chips+清空选择〕✓（r2 缺项已补）** / 载入〔画布/检查器骨架+「读取中」〕✓ / 错误〔错误卡+重试；画布保留上一帧〕✓ / 满〔画布+检查器+操作条；未保存圆点〕✓ / 部分〔未决确认模态 保存/丢弃/取消；flush 失败留旧 UI〕✓ / 冲突〔冲突条+查看对照；应用禁用；不自动合并〕✓（09 原文「冲突条（文本/锁/binding）」的括号细节在 AC 中缩写，核心判据「+查看对照；应用禁用；不自动合并」全保） / 只读〔检查器禁用+转移入口〕✓ / **运行中〔Run 投影条+暂停/停止/重试；intent key 复用〕✓（r2 缺项已补）** |
| **AC4 阅读器** | 卡 `:102` | 09 阅读器列全部行在列：空〔「本章节暂无页面」+返回〕✓（r2 缺项已补）/ 载入〔上一页保留+进度环〕✓ / 错误〔错误占位+重试+返回〕✓ / **满〔正常阅读；条自动隐藏〕✓（r2 缺项已补）** / **部分〔缺页占位「页面未就绪」+可重试；其余页可翻〕✓（r2 缺项已补；「页面未就绪」为缺页占位文案措辞、出自 07 正文，非状态名错位）** / 只读〔只读警示，源不可用〕✓ / 运行中〔进度写回中，不阻塞〕✓ / 筛选/冲突列「—」✓（含说明） |
| **AC5 设置** | 卡 `:103` | 09 设置列全部行在列（r2 时完全无清单，现已补齐）：空〔防御空态+重试〕✓ / **空〔搜索无结果→「无匹配」+清空搜索〕✓** / 载入〔卡片骨架；分组列表先显示〕✓ / 错误〔顶部错误条+重试；保存失败保留输入〕✓ / 满〔全分组可编辑〕✓ / 部分〔字段禁用+原因 Tooltip；Fluent 材质在 Current 下〕✓ / 只读〔保存禁用；可浏览〕✓ / 冲突/运行中列「—」✓（含说明） |

- **W-8 兑现**：卡 `:129` W-8「以 `09-state-matrix.md` 为唯一状态清单，AC2–AC5 逐页覆盖」+ 各 AC 明写「`09-state-matrix.md` 本页列全部行实现」——处置声明与事实相符。
- **术语错位清零**：全卡 grep「未就绪」仅剩 AC4 缺页占位文案一处（07 正文措辞，正确用法）；r2 指出的 AC2 状态名「未就绪」已改「只读」。09 状态轴术语（空/空〔筛选后〕/载入/错误/满/部分/冲突/只读/运行中）与 AC 清单无一处错位。

---

## 3. P2 处置抽查（r2 遗留 10 条）——**全部落实**

| r2 项 | 落点 | 实测 |
|---|---|---|
| P2-1 AC5 漏 appearance/contrast | 卡 | ✓ 卡 `:103`「含深/浅 `appearance`、对比度 `contrast`」已入字段清单 |
| P2-2 internal 与「保留旧 UI」张力 | 卡 | ✓ 卡 `:101` AC3 映射表 internal 行「错误卡在位显示并保留旧 UI/上一帧、不清屏」 |
| P2-3 W-6 缺 07:3/08:3 锚点 | 卡 | ✓ 卡 `:127` W-6「阅读器=`ReaderOverlay` 浮层（`07:3`），设置=ThemeStudio surface 承载外观组（`08:3`），两者不新增 SpaceId」 |
| P2-4 设置页其余分组承载 | brief | ✓ brief「口径补充」第 2 条（按 `08 §3` 在 Fluent 设置页内实现，数据语义沿用既有 surface 契约） |
| P2-5 depends_on 缺 FEA-04/FEA-05-WIRE-1 | 卡 front matter | ✓ 卡 `:12-13` `depends_on` 已含 `FEA-04` 与 `FEA-05-WIRE-1`（六项全列） |
| P2-6 资产边界 | 卡 + brief | ✓ 卡 `:115` 禁止范围「资产边界（r2-P2-6）：沿用 `NmIcon`…不新增资产/字体；确需新增 → 停等 DSH」+ brief 第 4 条 |
| P2-7 17 快捷键口径 | 卡 | ✓ 卡 `:99` AC1「17 个既有冻结快捷键可达（全局 10 + 空间级 7：Tab + J/K/[/]/Shift+[/]）」 |
| P2-8 令牌缺口停等 | brief | ✓ brief「口径补充」第 3 条（停等 DSH 裁决，不得自行改 TokenMap/生成物） |
| P2-9 失败归因 | brief | ✓ brief「口径补充」第 5 条（先单独重跑归因，不直接判基线漂移） |
| P2-10 交付顺序 | brief | ✓ brief「口径补充」第 6 条（P1 Shell → P6 组件 → P2 → P3 → P4 → P5 → 收口）+ 第 7 条 G-4 归 FEA-07 + brief 阶段 1/2/3 全序展开 |

W-12 注入口径亦已入 brief（「口径补充」第 1 条：复用实例、禁止第二 Host/Coordinator、`App.axaml.cs` 不在写域）——与卡 W-12 一致。

---

## 4. 无新问题核验（是否引入新 P0/P1）——**无**

- **组合根改动是否影响 V2/legacy 启动**：否。`App.axaml.cs` 单行变更仅 Fluent 分支传参；V2/legacy 分支与 selector 逐字未动；`CompositionRoot_DispatchesToFluentV2AndLegacyShells` 三分支断言全过；全量 1022/0/57 与 PREREQ-2 集成基线逐位一致。
- **测试是否削弱**：否。`FluentShellTests.cs` +6 行纯增强（三个 `Assert.Same`），既有断言（含 V2/legacy 分派与 legacy 回滚语义）全部保留。
- **允许路径是否被扩权**：否。front matter `allowed_paths` 与 r2 版一致；W-9 仍排除组合根；W-12 以「DSH 单点预置 + Codex 只消费」闭合注入通路，未给实现者开任何新写路径。
- **W-12 与 W-9/AC10 自洽**：见 §1 末行——DSH 改动承载在处置 commit（本被审 head）内，实现期写域边界不变。
- **可选参数空引用风险**：`HostController`/`Appearance`/`ThemeManager` 为可空注入（默认 null）——PREREQ-2 既有测试（headless 构造 `FluentShell` 不传三参）兼容性保持；生产组合根路径恒传三实例（`CreateShell` 对 controller/appearance/themeManager 有 `ArgumentNullException.ThrowIfNull` 防线，`App.axaml.cs:126-132`）。四页实现时按 W-12/brief 口径取用注入实例即可，无新暴露面。
- **本处置 commit 的写域纪律**：改动 3 个代码文件中 `FluentShell.axaml.cs`/`FluentShellTests.cs` 均在卡 allowed_paths 内；`App.axaml.cs` 由 DSH 以 Lead 身份单点持有（W-12 明文授权路径），治理归属自洽。

**结论：本次修复未引入任何新 P0/P1。**

---

## 5. 新发现 P2（3 条，接受/建议，不阻塞释放）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **r3-P2-1** | 卡 `:91`（任务拆解 P3 行） | 摘要行残留旧口径「本页 **8 态**」，与 AC3「全部 **9 行**」不一致（DSH 改 AC 时漏改该摘要行）；同行「Draft 7 方法接入（Open/Patch/Prepare/Apply/Status/Discard）」简称清单列 6 项对 7 方法（实际 `IHostController.cs:422-458` 为 Open/Patch/Prepare/Apply/Get/List/Discard）。验收以 AC3（「Draft 7 方法经 `IHostController`，W-2」+「全部 9 行」）为准，无机械验收歧义 | DSH 置 ready 时顺手把 P3 行「8 态」改「9 态（09 工作台列全行）」、方法简称补「Get/List」（或删括号简称）——1 行 docs-only |
| **r3-P2-2** | `G:\CODEX\New Manga.workspace\exchange\FEA-06-codex-brief.md`（正文） | brief 头部仍写「scope 修订 commit `53060cd67`」「scope-r2 approved 后派发」，且正文阶段 2 残留旧口径：Shelf 状态摘要用「未就绪」术语且缺 满/只读/运行中；Workbench 写「8 态」——恰是 r2-P1 刚纠正的两处错位。brief 的「口径补充」段（W-12/P2-4/6/8/9/10）已是新口径，但正文未同步（brief 为半新半旧状态）。brief 自定位为「approved 后派发」的草稿、必读第 1 条指向卡、验收以卡 AC 为准，故不阻塞；但**若按现状直接派发，会把刚纠正的术语错位重新喂给 Codex** | DSH 派发前刷新 brief：头部依据 commit 改为届时 HEAD（处置后 ≥`3c7f311d8`）、「W-1…W-11」改「W-1…W-12」、阶段 2 的 Shelf/Workbench 状态摘要改为「按 09 本页列全行（以卡 AC2–AC5 为准）」 |
| **r3-P2-3** | 卡 `:7` `approval: pending_scope_review_r2`；`STATUS.md:7`「scope-r2 复核中」 | 轮次字段滞后于实际（现为 r3；r2 报告与 checkpoint §33 已先行入库）。属状态指针滞后非事实漂移，DSH 置 ready 时随 approval/status 一并更新即可 | 置 ready 时同步：卡 `approval` 改 ready 口径、`STATUS.md:7` 改「scope-r3 approved、ready、按 W-10 派 Codex」；另释放时**刷新 `base_commit` 至届时 main HEAD**（现为 `5a4717009`，落后当前 HEAD 三代——r2 报告 §6 与 checkpoint §33 均已列此动作） |

---

## 6. 治理一致性

- `check.ps1` **PASS（3 warnings）** 与 `verify_pins.ps1` **PASS（all 15）** 本轮在 `3c7f311d8` 复跑通过；3 条 warnings 与 r2 轮完全相同（既有口径，非本处置引入）。
- checkpoint §33（`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`，本 commit +6 行）如实记录 r2 结论、处置内容与本轮验证口径，预告「scope-r3 → approved 后置 ready、刷新 base_commit → 按 W-10 派 Codex」——与实际流程一致。
- owner=codex（用户 2026-11-02 指派）四处落盘（卡 approval/owner + W-10、STATUS:7、PLAN、checkpoint §32）在 r2 已核，本处置未改动归属。
- 用户代理 127.0.0.1:7890（本轮未触网，仅备案）。

---

## 7. 结论与释放前动作

**r2-P0 闭环 ✓、r2-P1 闭环 ✓、P2 处置全部落实 ✓、无新 P0/P1 ✓ —— decision：approved（P0=0 / P1=0 / P2=3）。**

**FEA-06 可置 `ready` 并按 W-10 释放 Codex 实施。** DSH 释放前按序完成：

1. 处置本报告 3 条 P2（均为 1 行级 docs-only / 草稿刷新，可合并进置 ready 的同一 commit）：
   - 卡 `:91` P3 行「8 态」→「9 态」并补齐/删除方法简称（r3-P2-1）；
   - brief 头部依据 commit、W 范围、阶段 2 两处状态摘要刷新（r3-P2-2）；
   - 卡 `approval` 置 ready 口径 + `STATUS.md:7` 同步（r3-P2-3）。
2. **刷新卡 `base_commit` 至届时 main HEAD**（≥`3c7f311d8`）。
3. 指定 reviewer（释放时填卡 `reviewer` 流程位；实现完成后按 2026-10-31 上下文独立口径派发独立实现复核）。
4. 按 checkpoint §32 既有结论派发 Codex：`codex exec -m gpt-6-luna`、cwd=仓库根，任务文本 = `G:\CODEX\New Manga.workspace\exchange\FEA-06-codex-brief.md`（刷新后版本）。
5. Codex 交付后：独立上下文实现复核 → DSH 集成验证（全量 + 两 `--check` + `check.ps1`/`verify_pins`）→ done。

---

## 8. 边界声明

本报告只审 **r2-P0/P1 的处置充分性、P2 落实抽查与是否引入新问题**：不重开全量范围复核（r2 已结论项不再复查）、不审设计数值本身（fluent-v1.0.0 FROZEN，FEA-04b r5 approved）、不审未写的四页实现、未运行 UI 像素/交互验证；`check.ps1`/`verify_pins` 为只读参考，不替代审查。行号基于 `3c7f311d8` 实测，判据未为放行降低。本席位未参与 FEA-06 起草/范围处置/实现，除本报告外未修改任何文件、未 commit/push。**本报告不构成实现授权**；实现授权以 DSH 置 `ready` + 按 W-10 派发为准。
