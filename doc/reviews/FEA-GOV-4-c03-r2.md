---
document_id: FEA-GOV-4-c03-r2
kind: independent_review
task_id: FEA-GOV-4
round: 2
scope: narrow（只核 r1 的 2×P1 + 4×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-16；独立上下文；未参与 C-03 草案撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-4-c03-review（r1：changes_requested，P0×0 / P1×2 / P2×4）
reviewed_head: bc141a10a
reviewed_head_full: bc141a10acfb56ca9869d1002f78d5b7fce9d803
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == bc141a10a）；两次处置提交 0b00a4038 + bc141a10a"
reviewed_document: doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md
reviewed_sha256: 3d2dd9c0c217eab411d50fd059a51d36429011e5b238f5d3d3a587c0ac1e842f
reviewed_sha256_basis: "HEAD 的 LF blob（94 行，blob 89dccb450）；与 reviewed_head 相同"
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为非阻断编辑/一致性项（§2.1 sink-only 与 §3 兼容写/只读时序未对齐、§7 变更记录未补 v3/v4、auto 读取失败无降级策略），登记为 K-1/K-2/K-3"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T03:56:40+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（窄面）：FEA-C03 外观持久化处置确认

**本报告不是** 冻结动作、不是代码实现审查，也不构成执行授权。本轮只核 r1 的 2×P1 + 4×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断）。**

r1 的 2×P1 + 4×P2 **全部实质处置到位**，且两处 P1 的修法与我 r1 的建议逐点对应：

- **P1-1 ✅**：§2.1 写者已上移——「`presentation-settings.json` 由 **`NewManga.Appearance` 项目的 `AppearanceCoordinator`** 原子写（方案 `:131`/`:858`）；ThemeEngine 的 `IThemePersistence` 成为**对该存储的适配面**（sink-only）；`PresentationSettingsStore` 落在 `NewManga.Appearance` 内，**不在 ThemeEngine**」；§3 判据同步。与方案 `:131`/`:858`/§15.2 §4 行一致。
- **P1-2 ✅**：§3「写者唯一性」已改为「`ThemeSettingsStore.SaveAsync` 在迁移后**保留一个 release 周期的兼容写**（写旧文件 + 记 warning），**不抛 `NotSupportedException`**」，并写明理由（唯一调用者 `ThemeService.TrySave` `:647-661` 在 `:654` 会 catch 吞掉异常，静默失效更糟）；**新增「`ThemeService` 迁移」判据行**：`TrySave` 改调 `AppearanceCoordinator`、`SaveAsync` 异常只作防复活护栏、`ApplyAsync` 不得静默返回成功、过渡期失败必须提示。
- **P2-1 ✅** §7「9 行」（矩阵实测 9 数据行）；**P2-2 ✅** §3 末条已改 `theme.visualThemeId` ∈ {`newmanga-default`,`builtin.fluent-dark`} + `theme.frontendId` ∈ {`builtin.current-v2`,`builtin.fluent`}；**P2-3 ✅** §2.3 已落到平台机制（`SPI_GETCLIENTAREAANIMATION` / WinRT `UISettings.AnimationsEnabled`，并注明 Avalonia 11.3.22 无该 API）；**P2-4 ✅** 动效证据已改 `ThemeModels.cs:217,354`，三态判据补齐 ①–⑤（decorative/feedback/full/auto/navigation/迁移等价）。

3 条非阻断 P2 为新引入的**编辑一致性**问题（§2.1 与 §3 的兼容写/只读时序未对齐、变更记录未补、`auto` 读取失败无降级），不影响冻结判断。

| 核实项 | 结果 |
|---|---|
| 1. P1-1 写者上移 | **✅ 已处置** |
| 2. P1-2 兼容写 + `ThemeService` 迁移判据 | **✅ 已处置**（兼容写 + 新增判据行逐项覆盖） |
| 3. P2-1 矩阵 9 行 | **✅** |
| 4. P2-2 `theme.visualThemeId` | **✅** |
| 5. P2-3 平台辅助功能机制 | **✅**（`SPI_GETCLIENTAREAANIMATION` / WinRT `UISettings.AnimationsEnabled`） |
| 6. P2-4 证据行号 + 三态判据 | **✅**（`:217,354`；判据 ①–⑤） |
| 7. 新问题 + `check.ps1` | 无新增实质问题；**`check.ps1` PASS(3 warnings) EXIT=0**；未 push；无代码改动 |

---

## 2. 6 处核对明细

### 2.1（P1-1）§2.1 写者归属 —— ✅

- 现文（`:28`）：「`presentation-settings.json`（新文件）由 **`NewManga.Appearance` 项目的 `AppearanceCoordinator`** 原子写（方案 `:131`/`:858`）；ThemeEngine 的 `IThemePersistence` 成为**对该存储的适配面**（sink-only：ThemeEngine 只读它，不再自行写旧文件）。`PresentationSettingsStore` 落在 `NewManga.Appearance` 内，**不在 ThemeEngine**。」
- 与方案对齐：`:131`「`NewManga.Appearance/ # 三层选择/兼容/持久化协调，调用既有 ThemeEngine`」✓；`:858`「由 Appearance coordinator 原子写…`IThemePersistence` 成为该存储的适配面…ThemeEngine sink 和 Theme Studio 只调用 coordinator」✓；§3 判据（`:62`）同步为「只能由 `NewManga.Appearance` 的 `AppearanceCoordinator` 写」✓。

### 2.2（P1-2）§3 兼容写 + `ThemeService` 迁移判据 —— ✅

- 写者唯一性（`:62`）：「`ThemeSettingsStore.SaveAsync` 在迁移后**保留一个 release 周期的兼容写**（写旧文件 + 记 warning），**不抛 `NotSupportedException`**——因为现有唯一调用者 `ThemeService.TrySave`（`Service/ThemeService.cs:647-661`）在 `:654` 会 catch 并吞掉异常，静默失效比兼容写更糟；兼容期结束后由 Appearance 接管全部保存路径」✓（与我 r1 指出的 `:651`/`:654` 事实一致）。
- 新增判据行（`:66`）：「`TrySave` 改为调 `AppearanceCoordinator`；`ThemeSettingsStore.SaveAsync` 的异常只作**防复活护栏**（如果仍有调用方，必须对用户可见——`ApplyAsync` 不得返回成功）；过渡期失败必须提示而非静默降级」✓ 三项子要求（改调 coordinator / 异常可见 / 过渡期提示）齐全。

### 2.3（P2-1）字段矩阵 9 行 —— ✅

- §7 变更记录（`:93`）改为「字段迁移矩阵 **9 行**」✓；矩阵（`:34-44`）实测 9 数据行（含表头共 10 行）✓。

### 2.4（P2-2）§3 末条判据 —— ✅

- 现文（`:67`）：「`theme.visualThemeId` ∈ {`newmanga-default`, `builtin.fluent-dark`}；`theme.frontendId` ∈ {`builtin.current-v2`, `builtin.fluent`}；Current 视觉主题下 material/corners 字段被忽略（不报错）」✓ 不再出现 `theme.packageId`；视觉主题 id 取值与 C-02 V-07 一致 ✓。

### 2.5（P2-3）平台辅助功能机制 —— ✅

- 现文（`:56`）：「`motion.mode=auto` 时读取系统辅助功能设置——**Avalonia 11.3.22 无动画开关 API**，实现须走平台层：Windows 读 `SystemParametersInfo(SPI_GETCLIENTAREAANIMATION)` 或 WinRT `UISettings.AnimationsEnabled`；`full`/`reduce` 为显式覆盖」✓ 与我 r1 的实证（`Directory.Build.props:11` = 11.3.22；包 XML 无 `AnimationsEnabled`）一致，并给出可实现的平台机制。

### 2.6（P2-4）证据行号 + 三态判据 —— ✅

- §1 动效证据（`:20`）改为 `ThemeModels.cs:217,354`（`ReducedMotion` 在 `:354`）✓。
- §3 三态可验证（`:65`）：① `reduce` 下 `decorative` 时长为 0、`feedback` 保留颜色但无位移；② `full` 不受系统设置影响；③ `auto` 按注入的假平台设置切换；④ `navigation` 在 `reduce` 下无动画切换；⑤ 旧 `ReducedMotion=true` 迁移后三类全禁 ✓ 覆盖 r1 指出的全部缺口。

### 2.7 新问题 + `check.ps1` + 数据安全

- **新问题**：无新增实质问题；3 条编辑一致性项见 §3。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0；运行后 `git status` 为空 ✓。
- **数据安全**：两次处置提交（`0b00a4038`：C-03 +7/−7、r1 报告 +178；`bc141a10a`：C-03 +2/−1）只改文档；`git diff --stat 1dfccc1be..HEAD -- src apps` **为空**；**未 push**（`bc141a10a` 非 `origin/main` 祖先）✓。
- 被审字节：C-03 @ `bc141a10a`，LF blob SHA-256 `3d2dd9c0c217…ac1e842f`（94 行）。

---

## 3. 已知限制（非阻断）

#### K-1 — §2.1「sink-only（只读，不再写）」与 §3「兼容写（写旧文件）」及旧文件只读时序未对齐

- 位置：`:28-29`（§2.1）↔ `:62-63`（§3）。
- 问题：§2.1 说 `ThemeSettingsStore` 降为 sink-only（只读、不再写）、「新文件首次成功写入后旧文件转只读」；§3 又说迁移后保留一个 release 周期的兼容写（写旧文件）。若旧文件在首次新文件写入后即被置只读，兼容写会以 `IOException` 失败（退化为 warning）。两处需明确兼容期与只读转换的先后。
- 建议：§2.1 补「**兼容期内旧文件保持可写**；兼容期结束（Appearance 接管全部保存路径）后再转只读并记录转换时点」；§3 迁移幂等行的「旧文件只读」标注为「兼容期结束后」。

#### K-2 — §7 变更记录未补 v3/v4 两轮修订

- 位置：`:91-94`（仅有「建立草案」「v2」两行）。
- 问题：`0b00a4038`（写者上移 + 兼容写 + P2×4）与 `bc141a10a`（`ThemeService` 迁移判据 + 三态判据补全）均未在变更记录留行。
- 建议：补 v3 / v4 两行（变更摘要 + DSH）。

#### K-3 — `auto` 读取失败时的降级策略未定义

- 位置：`:56`。
- 问题：已指明读 `SPI_GETCLIENTAREAANIMATION` / `UISettings.AnimationsEnabled`，但未写「读取失败/异常/平台不提供时按 `full` 还是 `reduce` 处理」，也未要求把平台读取封装为可注入接口（§3 判据③ 的「注入的假平台设置」已隐含可注入，但无失败分支）。
- 建议：补一句「平台读取失败 → 按 `full` 处理并记 warning；平台读取封装为 `IMotionPreferenceSource` 以便单测注入失败场景」。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与** C-03 草案撰写（作者 = DSH）、未参与 V11R / 方案 / C-02 / C-11 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-03 / C-02 / 方案 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证（`git diff`/`git cat-file`/`git show`）。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == bc141a10a`；被审文件 blob `89dccb450`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理）。
- 未执行任何冻结或代码改动（草案为 DRAFT；冻结仍须用户裁决 U-05a/U-05b + C-02 先冻结）。
- 未审 `ThemeService` 的其它调用面（只核 r1 指出的 `TrySave` 路径与草案引用的一致性）。
- 未验证 `SPI_GETCLIENTAREAANIMATION` / WinRT `UISettings.AnimationsEnabled` 在目标 OS 版本的行为（只核草案已指名机制；实际 API 验证属实现 Task）。
- 未验证 `presentation-settings.json` schema（计划态）与 `%APPDATA%` 旧文件只读属性行为。
- 未复核 C-11 草案（另行复核中）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3 非阻断；6 处核实全部到位）。
