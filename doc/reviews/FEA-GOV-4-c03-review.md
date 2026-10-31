---
document_id: FEA-GOV-4-c03-review
kind: independent_review
task_id: FEA-GOV-4
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-16（独立上下文；未参与 C-03 草案撰写，未参与 V11R 合案 / 方案 / C-01b / C-02 / C-11 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 1dfccc1be
reviewed_head_full: 1dfccc1be8a3ef9bb4159765cc1783fa2b2a2e8d
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == 1dfccc1be）"
reviewed_document: doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md
reviewed_sha256: 4e547663902dc8cbb0cc239c0dcd96ca34711ed40c45e6ff4dac9179dc07c3e3
reviewed_sha256_basis: "HEAD 的 LF blob（93 行，blob 4f1292c4c）；与 reviewed_head 相同"
baseline: "doc/plan/V11R_AVALONIA_CONTRACT.md §4（FROZEN）· doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md（r4 @ 74a772167）§6.1/§15.2/§15.6 · doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md（V-07）· 代码 apps/desktop-avalonia/src/NewManga.ThemeEngine/"
repository: G:/CODEX/New Manga
source_branch: main
verdict: changes_requested
p0_count: 0
p1_count: 2
p2_count: 4
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T03:54:29+08:00
captured_by: c01b-reviewer
---

# 独立复核：FEA-C03 外观持久化与字段迁移（草案）

**本报告不是** 冻结动作、不是代码实现审查，也不构成执行授权。本轮核对草案 §1 现状表与代码事实是否一致、§2 目标设计的可行性、§3 判据与 §4 冻结条件是否可执行、双 id 是否与 C-02 V-07 对齐，以及数据安全与 `check.ps1`。

## 1. 结论

**verdict：`changes_requested`（P0 × 0 / **P1 × 2** / P2 × 4）。**

草案的**骨架与大部分事实是准确的**：§1 现状表的五条引用（`ThemeSettingsStore.cs:7,64,66` / `:11,131`、`ThemeModels.cs:349-355` / `:330-346`、`ThemeModels.cs:217`、`LegacyThemeMigration.cs`）经实测**全部对得上**；§2.2 迁移矩阵覆盖了 `ThemeSettings` 的**全部 6 个字段** + 4 个新字段；§2.3 三态 + 三类的迁移等价路径（`true → reduce + 三类全禁`）成立；双 id 已在 §2.1/§2.2 与 C-02 V-07 对齐；§4 四条冻结条件完整可执行。

但有两处**可行性 P1**：

1. **唯一写者的归属与方案冲突（P1-1）**：草案 §2.1/§3 把 `presentation-settings.json` 的写者定为 **ThemeEngine 内的 `PresentationSettingsStore`**；而方案明确要求由 **Appearance coordinator**（新项目 `NewManga.Appearance`，`：131`）原子写该文件，`IThemePersistence` 只作**适配面**，ThemeEngine sink 与 Theme Studio **只调用 coordinator**（方案 `:858`；§15.2 §4 行 `:850` 亦写「Appearance coordinator 是唯一设置写者」）。这两处不能同时成立。
2. **`SaveAsync` 抛 `NotSupportedException` 会让既有保存路径静默失效（P1-2）**：现有唯一调用者是 `ThemeService.TrySave`（`Service/ThemeService.cs:647-661`），它在 `:651` 调用 `_persistence.SaveAsync(...)`，并在 `:654` **`catch (… or NotSupportedException)` 降级为 warning**、返回 false。按草案让 `ThemeSettingsStore.SaveAsync` 抛该异常后，主题/布局改动不会落盘，却只表现为一条 warning —— 草案未定义 `ThemeService` 的迁移落点。

4 条 P2 为计数、判据字段、辅助功能 API 与证据行号精度问题（见 §3），可与 P1 同批修订。

| 审查项 | 判定 |
|---|---|
| 1. 现状表准确性 | **通过** —— 五组引用实测吻合（`ThemeSettingsStore.cs:7/11/64/66/131`、`ThemeModels.cs:217/330-346/349-355`、`LegacyThemeMigration.cs`）；仅「动效」证据行号 `:353` 应 `:354`（P2-4） |
| 2. 目标设计可行性 | **不通过** —— 写者归属（P1-1）与 sink-only 迁移落点（P1-2） |
| 3. 字段迁移矩阵 | **通过** —— 覆盖 6 老字段 + material/corners/schemaVersion 4 新字段；`ReducedMotion=true → reduce` 等价成立；仅「10 行」计数错（实为 9 行，P2-1） |
| 4. 动效三态/三类 | **部分** —— 三态 + 三类可验证；「读取系统辅助功能（Avalonia `PlatformSettings`）」未落到具体 API（11.3.22 无 `GetAnimationsEnabled`，P2-3）；§3 三态判据覆盖不全（P2-4） |
| 5. 双 id 体系 | **部分** —— §2.1/§2.2 与 C-02 V-07 对齐 ✓；§3 末条判据仍写 `theme.packageId` + 「`builtin.fluent` 主题包 id」（P2-2） |
| 6. 冻结条件 §4 | **通过** —— ①独立复核 ②U-05a/U-05b ③C-02 已冻结 ④`check.ps1` PASS，四条完整且可执行（③与 C-02 §6 `:124` 一致） |
| 7. 数据安全 + `check.ps1` | **通过** —— 仅改文档；无代码/用户数据；未 push；`check.ps1` PASS(3 warnings) EXIT=0 |

---

## 2. 逐项核对

### 2.1 现状表（§1）—— ✅ 实测吻合

| 草案断言 | 代码实测 |
|---|---|
| 持久化文件 `%APPDATA%/NewManga/theme-settings.json`（`ThemeSettingsStore.cs:7,64,66`） | `:7` 注释写明该路径 ✓；`:64` `DefaultDirectory` ✓；`:66-67` `DefaultSettingsFilePath => Path.Combine(DefaultDirectory, ThemeDefaults.SettingsFileName)` ✓ |
| `ThemeSettingsStore : IThemePersistence`（唯一实现）（`:11,131`） | `:11` `public sealed class ThemeSettingsStore : IThemePersistence` ✓；`:131` `public async Task SaveAsync(...)` ✓；全仓仅此一个实现（`ThemeContracts.cs:94` 为接口，`ThemeService.cs` 仅消费者）✓ |
| `ThemeSettings(ThemeId, Appearance, Contrast, LayoutProfile, ReducedMotion, FollowSystemAccent)`（`ThemeModels.cs:349-355`） | 实测 349-355 字段逐一对上（`ReducedMotion` 在 **354**）✓ |
| `LayoutProfile(Id, Navigation, Shelf, Density, Workbench, Reader)`，V1 仅 `TopBand`（`:330-346`） | 实测吻合 ✓（V11R §4 亦注「V1 只实现 TopBand，其余保留枚举」）✓ |
| 动效只有 `ReducedMotion` 布尔；`ThemeMotion` 是主题包时长不持久化（`:217,353`） | `:217` `ThemeMotion(int FastMs, int NormalMs, int SlowMs)` ✓；`ReducedMotion` 在 **354**（`:353` 是 `LayoutProfile Layout`）→ 行号偏一行（P2-4） |
| 损坏容错：读失败回退默认（`ThemeSettingsStore.cs` 注释与 `Load()`） | `:7` 注释「never lets a corrupt …」✓；`:69-70` 「Reads settings; never throws for missing/corrupt/unreadable files」✓ |
| `LegacyThemeMigration` 存在（退役主题 id 迁移） | `Persistence/LegacyThemeMigration.cs` 存在，含 `LegacyThemeMapping(LegacyId, …)` ✓ |

### 2.2 目标设计（§2.1 / §3）—— ⚠️ P1-1 / P1-2

- **写者归属**：草案「`presentation-settings.json`（新文件）作为单一写点；`ThemeSettingsStore` 降为 sink-only」+ §3「只能由 **ThemeEngine** 的 `PresentationSettingsStore` 写」。
  方案基准：`:131` 分层列表新增 `NewManga.Appearance/  # 三层选择/兼容/持久化协调，调用既有 ThemeEngine`；`:858`「唯一写者方案：由 **Appearance coordinator** 原子写 `presentation-settings.json`，**`IThemePersistence` 成为该存储的适配面**，ThemeEngine sink 和 Theme Studio **只调用 coordinator**」；§15.2 §4 行 `:850`「Appearance coordinator 是唯一设置写者，旧 `Settings` 为同源只读投影…旧 persistence 适配同一文档」。→ 两者写者层级不同（P1-1）。
- **旧文件只读时序**：「新文件首次成功写入后，`theme-settings.json` 转为只读（保留为迁移输入）」+ §3 判据「旧文件存在 → 首次读时迁移 → 写新文件 → 旧文件只读；重复启动不再写旧文件」——时序自洽、Windows 侧可用 `FileAttributes.ReadOnly` 实现 ✓ 可执行。但**写入方**是谁仍受 P1-1 影响。
- **`SaveAsync` 抛异常的影响面**（P1-2）：`ThemeService.TrySave`（`:647-661`）是唯一调用点，`:651` `_persistence.SaveAsync(settings).GetAwaiter().GetResult()`，`:654` `catch (… or NotSupportedException)` → 写入失败被降级为 `ThemeIssueCodes.SettingsIoFailed` warning 并返回 `false`。因此：
  - 若按草案抛 `NotSupportedException` 而**不改调用方**，用户改主题/布局后**不落盘**，界面只可能出现一条 warning（多数场景用户不可见）→ 静默数据丢失风险；
  - 草案 §3/§6 均未提 `ThemeService` 的迁移落点（方案 `:858` 的「旧 API 在过渡期桥接」也未在草案中体现）。

### 2.3 字段迁移矩阵（§2.2）—— ✅ 覆盖完整（P2-1 计数）

- 数据行实测 **9 行**：`ThemeId`、`Appearance`、`Contrast`、`LayoutProfile.*`、`ReducedMotion`、`FollowSystemAccent`、`material.*`、`corners.scale`、`schemaVersion` —— 覆盖 `ThemeSettings` 全部 6 字段 + 4 个新字段（material 两个键同行）✓ 无缺项。
- `ThemeId` 行已按 C-02 V-07 拆成 `theme.visualThemeId`（`newmanga-default` / `builtin.fluent-dark`）+ `theme.frontendId`（`builtin.current-v2` / `builtin.fluent`）✓ 与 C-02 V-07 一致。
- `ReducedMotion` 迁移：`true → reduce`、`false → auto`；§2.3「`true` 映射为 `mode=reduce` 且三类全禁（等价旧行为）」——旧行为是全禁动效，新表述等价 ✓ 成立。
- 仅 §7 变更记录写「字段迁移矩阵 **10 行**」与实测 9 行不符（P2-1）。

### 2.4 动效三态/三类（§2.3）—— ⚠️ P2-3 / P2-4

- 三态 `auto/full/reduce` + 三类 `navigation/feedback/decorative` 的可验证性成立（§3 判据：`reduce` 下 `decorative` 时长为 0；`full` 不受系统设置影响）✓。
- **系统辅助功能读取未落地**：草案只写「读取系统辅助功能设置（Avalonia `PlatformSettings`）」。实测 pining 的 Avalonia 版本为 **11.3.22**（`apps/desktop-avalonia/Directory.Build.props:11`），其 `Avalonia.Base.xml` 中 `IPlatformSettings` 的公开成员抽查为 `GetTapSize/GetDoubleTapSize/GetDoubleTapTime/GetColorValues/GetPaperSize/…`，**未见 `GetAnimationsEnabled` 一类成员**（全包 XML 检索 `AnimationsEnabled` 为空）；仓库现有代码也未用 `PlatformSettings`（只有 `RequestedThemeVariant`）。→ 「`auto` 读系统设置」需要指名的实现机制（如 Windows `SPI_GETCLIENTAREAANIMATION` + 平台回退策略）与降级行为，否则不可实现也不可审查（P2-3）。
- **判据覆盖不全**（P2-4）：`auto` 跟随系统、`navigation`/`feedback` 在 `reduce` 下的具体行为（无动画切换 / 保留颜色去位移）均无单测判据；只测 `decorative=0` 与 `full` 两项。

### 2.5 双 id 体系 —— ⚠️ P2-2

- §2.1 理由与 §2.2 `ThemeId` 行已与 C-02 V-07 对齐 ✓（视觉主题 id vs frontend id，值映射正确）。
- §3 末条判据：「`builtin.fluent` **主题包 id** 在 `theme.packageId` 合法；`builtin.current-v2` 下 material/corners 字段被忽略」——① `theme.packageId` **不在 §2.2 矩阵**中（矩阵字段为 `theme.visualThemeId`/`theme.frontendId`）；② `builtin.fluent` 是 **frontend id**，其视觉主题 id 是 `builtin.fluent-dark`（C-02 V-07）。→ 判据不可执行且与 C-02 未对齐（P2-2）。

### 2.6 冻结条件（§4）—— ✅

- 四条：① 独立复核（上下文独立）② 用户裁决 U-05a/U-05b ③ C-02 已冻结（引 C-02 §6 `:124`）④ `check.ps1` PASS —— 与 C-02 §6 的冻结条件模式一致，且补上了「C-02 先冻结」的前置序 ✓ 完整可执行。

### 2.7 数据安全与治理 —— ✅

- `1dfccc1be` 仅改 `doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md`（+13/−5）；`git diff --stat 0c491d0db..HEAD -- src apps` 为空（无代码改动）；无用户数据。
- **未 push**：`1dfccc1be` 非 `origin/main` 祖先 ✓。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 为既有：7 个非终态 Task、`STATUS.md` 2883 B / 80%、`REBASELINE_PLAN.md` 6547 B / 80%）；运行后 `git status` 为空 ✓。
- 被审字节：C-03 @ `1dfccc1be`，LF blob SHA-256 `4e547663902d…dc07c3e3`（93 行）。

---

## 3. Findings

### P1

#### P1-1 — 唯一写者归属与方案冲突：草案把写者放在 ThemeEngine 内，方案要求 Appearance coordinator

- 位置：C-03 `:28`（§2.1「唯一写者」）、`:62`（§3 判据「只能由 ThemeEngine 的 `PresentationSettingsStore` 写」）。
- 证据（方案）：`:131` 分层新增 `NewManga.Appearance/  # 三层选择/兼容/持久化协调，调用既有 ThemeEngine`；`:858`「唯一写者方案：由 **Appearance coordinator** 原子写 `presentation-settings.json`，**`IThemePersistence` 成为该存储的适配面**，ThemeEngine sink 和 Theme Studio **只调用 coordinator**；`IThemeService.Settings` 从同一 generation 投影」；`:850`（§15.2 §4 行）「Appearance coordinator 是唯一设置写者，旧 `Settings` 为同源只读投影，`SetLayoutAsync` 经桥接映射或明确拒绝不支持项；旧 persistence 适配同一文档」。
- 影响：若按草案冻结，ThemeEngine 将拥有 frontend 选择（`theme.frontendId`）等跨层状态的写权，与方案的分层（Appearance 负责三层选择/兼容/持久化协调）冲突；后续 FEA-05/FEA-06 会按两套不同的写者归属实现，`IThemePersistence` 适配面语义也会分叉。
- 建议：改为「**Appearance coordinator 是唯一写者**（`NewManga.Appearance`）；`ThemeEngine` 侧只保留 `IThemePersistence` **适配面**与 sink（只读/接收投影）；若 `PresentationSettingsStore` 必须存在于 ThemeEngine，则限定其为 coordinator 的**存储适配实现**、不得自行受理写入」。

#### P1-2 — `SaveAsync` 抛 `NotSupportedException` 会让现有保存路径静默失效（唯一调用点 `ThemeService.TrySave` 会吞掉该异常）

- 位置：C-03 `:62`（§3 判据「`ThemeSettingsStore` 的 `SaveAsync` 在迁移后必须抛 `NotSupportedException`（或用 `[Obsolete(error:true)]`）」）。
- 证据（代码）：`apps/desktop-avalonia/src/NewManga.ThemeEngine/Service/ThemeService.cs:646-661`：
  - `:647` `private bool TrySave(ThemeSettings settings, List<ThemeValidationIssue> issues)`
  - `:651` `_persistence.SaveAsync(settings).GetAwaiter().GetResult();`
  - `:654` `catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)` → 记 `ThemeIssueCodes.SettingsIoFailed` warning，`return false`。
- 影响：判据一旦落地，用户在 Current 界面改主题/布局后**不会持久化**，且失败只以 warning 形式存在（`ApplyAsync` 仍可能返回成功）→ 设置静默丢失。草案 §3/§6 未定义 `ThemeService`（及其 `TrySave`）的迁移落点，也没有「过渡期兼容」条款（方案 `:858` 明确要求「旧 API 在过渡期桥接」）。
- 建议：§3 增一条迁移判据：`ThemeService.TrySave`（`:647-661`）**改调 Appearance coordinator**；`ThemeSettingsStore.SaveAsync` 的 `NotSupportedException` 只作为「防止旧写入复活」的护栏，并明确过渡期行为（写入失败必须对用户可见，不得降级为 warning）；`ThemeService` 的契约变化在 FEA-05 Task 中显式记录。

### P2

#### P2-1 — §7 变更记录称「字段迁移矩阵 10 行」，实测 9 行

- 位置：C-03 `:92`；矩阵 `:34-44`（表头 + 分隔 + 9 数据行）。
- 建议：改为「9 行」或补一行（如把 material 两个键拆两行），保持文档自洽。

#### P2-2 — §3 末条判据引用不存在的字段 `theme.packageId`，且把 frontend id 当主题包 id

- 位置：C-03 `:66`。
- 证据：§2.2 矩阵字段为 `theme.visualThemeId` / `theme.frontendId`（`:36`）；C-02 V-07 明确视觉主题 id 为 `builtin.fluent-dark`、`builtin.fluent` 是 frontend id。
- 建议：改为「视觉主题 `builtin.fluent-dark` 在 `theme.visualThemeId` 合法且已注册；frontend 为 `builtin.current-v2` 时 material/corners 字段被忽略（不报错）」。

#### P2-3 — 系统辅助功能读取未落到具体 API（Avalonia 11.3.22 无 `GetAnimationsEnabled`）

- 位置：C-03 `:56`（「`motion.mode=auto` 时读取系统辅助功能设置（Avalonia `PlatformSettings`）」）。
- 证据：`apps/desktop-avalonia/Directory.Build.props:11` `AvaloniaVersion = 11.3.22`；该版本 `Avalonia.Base.xml` 中 `IPlatformSettings` 未列出 animations-enabled 类成员（全包 XML 检索 `AnimationsEnabled` 为空）；仓库现有代码未使用 `PlatformSettings`。
- 建议：指名机制（例如 Windows `SPI_GETCLIENTAREAANIMATION`，经平台 adapter 注入，便于单测注入假实现），并写明取不到时的回退（默认 `auto ≈ full` 或 `≈ reduce` 须择一并记录理由）。

#### P2-4 — 证据行号偏一行 + §3 三态判据覆盖不全

- 位置：C-03 `:20`（证据 `ThemeModels.cs:217,353`，`ReducedMotion` 实际在 **354**）；§3 `:65`（只测 `decorative=0` 与 `full`）。
- 建议：行号改 `:354`；判据补 `auto` 跟随系统、`navigation`（reduce → 无动画切换）、`feedback`（reduce → 保留颜色、去位移）与迁移等价（`ReducedMotion=true` → `reduce` + 三类关闭）。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-16`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-03 草案撰写（作者 = DSH）、未参与 V11R 合同 / FEA-00 方案 / C-01b / C-02 / C-11 撰写，未参与 `src/**`、`apps/**` 任何实现。
- **利益披露**：我出具过 C-01b r1–r5、FEA-GOV-1、FEA-GOV-2、FEA-GOV-3、FEA-C02 r1/r2 复核；本轮对代码事实（`ThemeSettingsStore.cs`、`ThemeModels.cs`、`ThemeService.cs`、`LegacyThemeMigration.cs`、`Directory.Build.props`、Avalonia 11.3.22 包 XML）与方案 §6.1/§15.2/§15.6 均**直接读取**，未引用既有报告结论。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-03 / C-02 / V11R / 方案 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == 1dfccc1be`；被审文件 blob `4f1292c4c`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理 Task）。
- 未执行任何冻结或代码改动（草案为 DRAFT；冻结须独立复核 + U-05a/U-05b 用户裁决 + C-02 先冻结）。
- 未审 `ThemeService` 全部调用面（只核 `SaveAsync` 的唯一调用点 `TrySave` 与异常处理）；未审计 `IThemeService` 的其它用法。
- 未验证 `presentation-settings.json` 的实际 schema 文件（尚不存在，属计划态）；未验证 Windows 只读属性在 `%APPDATA%` 下的实际行为。
- 未核 Avalonia `PlatformSettings` 的**完整** API 面（只抽查 11.3.22 包 XML 中 `IPlatformSettings` 成员与 `AnimationsEnabled` 关键字），也未排除通过 `Application.Current.PlatformSettings` 之外的其它路径读取辅助功能设置。
- 未复核 C-11 草案（另由 FEA-GOV-4 其余 Review 承担）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: changes_requested`，P0×0 / P1×2 / P2×4）。
