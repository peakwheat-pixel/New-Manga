---
task_id: FEA-06-PREREQ-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-implementer
base_commit: 933de92e2
reviewed_head: a57e6a811
decision: approved
counts: { P0: 0, P1: 0, P2: 12 }
---

# FEA-06-PREREQ-1 实现复核 r4（收口确认；独立上下文，本席位未参与实现/返修/收口）

| 字段 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-PREREQ-1.md`（`status: in_review`；范围 r3 approved `97677e402`） |
| base_commit | `933de92e2`（impl-r3 被审 head） |
| reviewed_head | `a57e6a811`（`chore(fea-06-prereq-1): PARTIAL 项取消勾选`；实现处置 `c107d9530`） |
| 实现者 | DSH（Codex 通道故障、ZCode 未安装） |
| reviewer | `fea05-wire-scope-reviewer`（DSH 派发 fresh 子 agent；未参与 PREREQ-1 实现/返修/收口；此前只读评审范围 r1–r3 + impl-r1/r2/r3；符合 2026-10-31 上下文独立裁决） |
| 日期 | 2026-11-03 |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 12（12 条均为接受遗留/建议，不阻断本轮实现复核）** |

> **一句话结论**：**approved**。r3 的 P1×5 已按以下方式闭合：**r3-P1-1 关闭**——`--frontend` 已有 `case "frontend"`（`AppOptions.cs:228`），`--frontend=x`/`--frontend x` 均赋值、空值拒绝，新增 `Frontend_Option_IsParsedBothWays`（App.Tests 433，总数 **978**）。**r3-P1-2/P1-3/P1-4 转为据实 PARTIAL**——AC1/AC3/AC5 取消勾选并注明 W-9/Q-32 未裁决前不闭环（AC1 兼容写、AC3 Material Base/Tint+主题层/R14、AC5 manifest+ThemeValidator 留待 Q-32/PREREQ-2 或后续），不再以 `<<MET>>` 虚假收口，处置可接受。**r3-P1-5 关闭**——`appearance-tests.log` 13、`motion-tests.log` 9、`sln-test.log` 978/0/57、`tokengen-check.log` 290 已更新，8 项 sha256 全部匹配；但 `AC1–AC4` 测试要求行仍 `NOT_RUN`、Closeout 仍有「待关闭时填写」与落表外的 AC6 行、`themegen-check.log` 仍 default-only，列 P2。**独立复跑**：全量 sln **978/0/57**（EXIT 0）、`TokenGen --check` EXIT 0（rows 290）、`ThemeGen --check` EXIT 0；`check.ps1` PASS（4 warnings，均非阻塞）、`verify_pins` 15/15。**注意**：AC1/AC3/AC5 仍是 PARTIAL，本卡不能作为 done 关闭；Q-32 正式裁决、PREREQ-2 写域/任务承接与 AC5 manifest/Validator 需在后续闭环。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改源码/卡/设计；`git status --porcelain` 为空；未 commit/push；本报告为本轮唯一新增文件。
- 独立实测：`dotnet test apps/desktop-avalonia/NewManga.sln` → **EXIT 0**；各项目合计 **978 passed / 0 failed / 57 skipped**（Appearance 13、App 433、ThemeEngine 237、DS 85、ApplicationCore 31、CoreClient 128、Host 51）。`TokenGen -- --check` → **EXIT 0（rows 290）**；`ThemeGen -- --check` → **EXIT 0**。`check.ps1` PASS（4 warnings：11 非终态、STATUS/PLAN 80%、`evidence_dir` 3 个未登记过程文件）；`verify_pins` 15/15。
- 证据表 8 项 sha256 全部匹配当前文件 ✓；`appearance-tests.log` 13、`motion-tests.log` 9、`sln-test.log` 978、`tokengen-check.log` 290 已更新；`themegen-check.log` 未更新（仍 default-only）。

---

## 1. r3 逐项 disposition

| r3 ID | 判定 | r4 证据 |
|---|---|---|
| **r3-P1-1** `--frontend` 未实现 | **CLOSED** | `AppOptions.cs` 新增 `case "frontend"`（`:228`）：空值拒绝、`options.FrontendId = value.Trim()`；`AppOptionsCliRobustnessTests.Frontend_Option_IsParsedBothWays` 覆盖 `=`/空格/空值；App.Tests 433、全量 978 ✓ |
| **r3-P1-2** W-9 对 r2-P1-2 的转移 | **PARTIAL 接受（P2-3）** | 卡 AC1 已取消勾选、`<<PARTIAL>>`，注明兼容写按 W-9 转 PREREQ-2（Q-32 未裁决）；不再以 MET 收口，诚实状态可接受。Q-32 仍待裁决、PREREQ-2 卡未更新（残留） |
| **r3-P1-3** W-9 对 r2-P1-4 的转移 | **PARTIAL 接受（P2-3）** | 卡 AC3 已取消勾选、`<<PARTIAL>>`，注明 Material Base/Tint + 主题层 schema/R14 转 PREREQ-2（Q-32）；不再虚标 MET，可接受。PREREQ-2 写域/任务仍未承接（残留） |
| **r3-P1-4** AC5 `<<MET>>` 不成立 | **PARTIAL 接受（P2-3）** | 卡 AC5 已取消勾选、`<<PARTIAL>>`，注明 manifest `nm.fluent.visual/1` 与 `ThemeValidator` 显式测试未加（P2-17）；不再虚标 MET，可接受 |
| **r3-P1-5** 证据/状态不自洽 | **CLOSED（P2-1/P2-2 残留）** | `appearance-tests.log` 13、`motion-tests.log` 9、`sln-test.log` 978、`tokengen-check.log` 290 已更新，8 项 sha256 全部匹配；但 AC1–AC4 测试行仍 NOT_RUN、Closeout 占位/表外 AC6 行、`themegen-check.log` 仍 default-only（P2） |

---

## 2. AC1–AC6

| AC | 判定 | 说明 |
|---|---|---|
| AC1 | **PARTIAL（已取消勾选）** | 读写/迁移/13 测试已交付；`ThemeSettingsStore` 兼容写按 W-9 转 PREREQ-2（Q-32 未裁决） |
| AC2 | **MET** | Coordinator + `AppOptions.FrontendId` 已注入（`--frontend` 解析/赋值/空值拒绝 + 测试）✓ |
| AC3 | **PARTIAL（已取消勾选）** | Focus/Corner/Elevation/Material 开关共 12 键已生成、`TokenGen --check` up to date；Material Base/Tint 与主题层 schema/R14 转 PREREQ-2（Q-32） |
| AC4 | **MET** | auto/full/reduce、`IMotionPreferenceSource`、判据①–⑤、navigation/迁移测试；`motion-tests.log` 9 ✓ |
| AC5 | **PARTIAL（已取消勾选）** | ThemeGen 生成 + `BuiltInThemes` 懒加载 + Current 不变测试 ✓；`nm.fluent.visual/1` manifest/`ThemeValidator` 显式测试未加 |
| AC6 | **MET** | 独立 978/0/57；`build.log`/`sln-test.log` ✓ |

---

## 3. P2（12 条，接受遗留/建议）

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P2-1 | 卡 `:94-118`、`:117`；`canonical_evidence_status: complete` | **收口文本仍不自洽**：`AC1–AC4` 测试行仍 `NOT_RUN`/「待补」；Closeout 仍有「待关闭时填写」且 `:118` AC6 行落在表外；AC1/AC3/AC5 为 PARTIAL 但 `canonical_evidence_status: complete`、`resource_closeout_status: complete` 仍标 complete | 测试行改 PASS/实际命令；Closeout 整理并去除占位/表外行；PARTIAL 期间 canonical/closeout 状态改 partial 或注明「仅本卡已交付部分」；`approval` 补 impl-r3/r4 记录 |
| P2-2 | `themegen-check.log`；卡 `:95-96,107` | `themegen-check.log` 仍 **default-only**（未体现 fluent），AC5 测试行却写「PASS（fluent 纳入 --check）」；证据表 commit 列仍 `06b7a1b10`（当前 head `a57e6a811`） | 重跑 ThemeGen 输出含 fluent 的日志；同步 commit 列；或明确该日志只证明 default、fluent 由生成器单测覆盖 |
| P2-3 | 卡 W-9 `:88`；goal `:162`；`FEA-06-PREREQ-2.md:21-34` | Q-32 在 goal 仍「待裁决」，卡 W-9 仍写「Q-32（2026-11-03，DSH 裁决）」；PREREQ-2 卡未修改、`allowed_paths` 不含 ThemeEngine/DesignSystem/Appearance（无法承接 r2-P1-2/r2-P1-4） | 正式裁决 Q-32 并修订 PREREQ-2（W-9 行/任务/AC/写域）或在后续卡闭环；统一 W-9/Q-32 记录 |
| P2-4 | `AppOptions.cs` `case "frontend"`；测试 | `--frontend` 仅非空校验，**接受任意 id**（如 `builtin.fluent-dark` 或乱码），无枚举校验/非法值测试；selector 的 fail-safe 在 PREREQ-2，但注入面本身未限域 | 校验 `builtin.current-v2`/`builtin.fluent`，非法值给 `InvalidReason` 或记录 warning；补非法值测试 |
| P2-5 | `AppearanceCoordinator`/`MotionResolver`/`WindowsMotionPreferenceSource` | 组件仍未接入 `Program.cs`/启动组合根（应用落点归 PREREQ-2）；AC2 仅证明属性可注入；`Coordinator` 无 Save | PREREQ-2 接入时补启动读取/通知与保存路径；或在 AC2 补「未接入」说明 |
| P2-6 | `check.ps1` 第 4 警告 | `evidence_dir` 仍含 3 个未登记过程文件：`appearance-coordinator-tests.log`、`delivery-notes.md`、`theme-tests.log` | 移入 workspace 或登记为 SOURCE_PIN，保持证据目录干净 |
| P2-7 | `PLAN:37` | 当前 DAG 行仍写 `FEA-06-PREREQ-1（proposed）`，而同文件行 `:21` 已 `in_review` | 同步 DAG 行 |
| P2-8 | `fluent-dark.nmtheme`；`BuiltInThemes.cs`；`ThemeRegistryTests` | 主题包仍保留 `light` 块（`supportsLight=false`）、`material:"solid"`；`BuiltInThemes` 注释仍称 build-time generated/never validated；registry `All[0]` 变为 fluent-dark 且测试未断言 `ids[0]` | 清理死 light 块/注释；补 registry 顺序断言或 default 优先约定；Material 值随 AC3/P2-3 处理 |
| P2-9 | `TokenMap` Focus.Ring.Color；BoxShadows writer；`AppearanceJson` shape | Focus.Ring.Color 仍为推导值无冻结依据；`<BoxShadows>0 1 2 #26000000` 省略 spread；JSON 仍扁平 dotted + 嵌套混用 | 补 Focus 值依据；显式 `x y blur spread #AARRGGBB` 并加 DS 单测；统一 JSON 形状 |
| P2-10 | `AppearanceStore`；`AppearanceCoordinator` | `Read()` IO/权限异常未捕获；`File.Move(overwrite)` 无 `File.Replace`/fsync；Coordinator 无 Save/`Reload_DoesNotTouchResources` 未断言资源 | 补异常回退/原子写改进/资源断言（可并入 PREREQ-2 接入时） |
| P2-11 | 注释/依赖 | `AppearanceStore.cs:9` 仍引不存在 `C-03 §2.5`；`MotionResolver.cs:13-15` 判据注释仍错；`WindowsMotionPreferenceSource` `[Out] bool[]`/`SetLastError` 未验；`NewManga.Appearance.csproj` 有无用 ThemeEngine 引用；`MaterialAcrylicStrength` 默认 0.5 vs 0.85 | 修正注释/P-Invoke/删除无用引用；统一默认值 |
| P2-12 | 96 语义/迁移测试 | `Nm.Size.MatrixColumnMin` 实现为 `DerivedGlobals` 令牌派生，r3 AC3 原文「非令牌派生」；旧 `...WithAllCategoriesOff` 测试名仍无 categories 断言；迁移读取结果未落 `presentation-settings.json`/`LegacyDocument` 语义仍名不副实 | 改 AC 表述或改常量；补断言；迁移后写新文件并拆 `LegacyDocument` 语义 |

---

## 4. 证据/治理

- 写域：r4 变更均在卡 `allowed_paths` 内 ✓（`AppOptions.cs`/App.Tests/证据/卡/评审）。
- 证据：8 项 sha256 **全部匹配**；`appearance-tests.log` 13、`motion-tests.log` 9、`sln-test.log` 978、`tokengen-check.log` 290、`build.log` 已更新；`themegen-check.log` 仍 default-only（P2-2）。
- 治理：`check.ps1` **PASS（4 warnings，非阻塞）**；`verify_pins` **15/15**；STATUS/PLAN/LEDGER 中卡 `in_review`；但 PLAN DAG `:37` 仍 proposed（P2-7）、证据目录 3 个未登记文件（P2-6）、Q-32/W-9 记录不一致（P2-3）。

## 5. 结论

**approved**（P0=0 / P1=0 / P2=12）。r3 的 5 条 P1 已合理处置：P1-1 真正关闭；P1-2/P1-3/P1-4 以据实 PARTIAL 取消勾选、等待 Q-32/PREREQ-2 与 AC5 manifest/Validator 后续闭环；P1-5 证据刷新且哈希匹配。**注意**：AC1/AC3/AC5 仍为 PARTIAL，本卡不得作为 done 关闭；Q-32 正式裁决、PREREQ-2 写域/任务承接、AC5 manifest/Validator 与 P2 清单需在后续处理。

## 6. 边界声明

本报告只审被审 head 的实现/测试/证据/写域/收口，不审 PREREQ-2/FEA-06 主卡内容；未修改源码/卡/设计，未 commit/push；`check.ps1`/`verify_pins` 为只读参考，独立命令与结果见 §0；行号基于 `a57e6a811` 实测。
