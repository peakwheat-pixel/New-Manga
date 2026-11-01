---
document_id: FEA-GOV-12-review
kind: independent_review
task_id: FEA-GOV-12
scope: narrow（C-03 v5 迁移等价性 + 系统优先级分歧声明 + C-02 V-05 判据④）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-24（独立上下文；未参与 C-02/C-03 撰写与 Codex 意见处置）"
reviewer_independent: true
reviewed_by_implementer: false
reviewed_head: 2a540fcc3
reviewed_head_full: 2a540fcc33495d1085ca731bfa2f34fef82465e2
reviewed_head_note: "任务 pin reviewed_head = 2a540fcc3。复核期间 HEAD 前进 3 个提交到 7aa54bf23（1017ea648 冻结 C-01b；db6322191 冻结 C-05/C-12/C-07；7aa54bf23 冻结 C-02/C-11）——均属**另一 Agent 的冻结工作，非本 reviewer 写入**。被审两文件内容未变：C-03 全程 UNCHANGED（3aea4d910）；C-02 仅状态行由 DRAFT 改 FROZEN（e9a4f5af1 → fcea994ae），V-05 判据④ 正文逐字未变"
reviewed_documents:
  - doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md
  - doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md
reviewed_sha256:
  doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md: 45063eaa768f4936ceabacb35cacc9a4d4801a99c91bda79326a1101affc0420
  doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md: ecae0c8dfb3de5319dc8508e903ea704c0029cc65460f8e569731aa2b376b8f2
reviewed_sha256_basis: "HEAD 的 LF blob（C-03 102 行、C-02 141 行）"
baseline: "apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Motion.Reduced.axaml · Theming/DesignSystemThemeManager.cs · NewManga.ThemeEngine/Service/ThemeService.cs · Models/ThemeModels.cs · Validation/ThemeValidator.cs · doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md（r4 `:865`/`:874`/`:1041`）"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 5
p2_note: "5 条均为非阻断（方案 r4 引用行号错位、U-05c 选项不完整、三态/三类命名未映射、旧 true 分支的加载失败路径未纳入等价性说明、C-02 ④ 未指定限定校验路径落点）"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑（工作树含他人未提交改动）"
captured_at: 2026-11-01T08:33:41+08:00
captured_by: c01b-reviewer
---

# 独立复核：C-03 v5 / C-02 V-05 判据④（Codex 独立意见处置）

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。本轮实核代码事实（`Motion.Reduced.axaml`、`DesignSystemThemeManager`、`ThemeService`、`ThemeModels`/`ThemeValidator`）与方案 r4 原文，逐项核对 Codex 意见 ③ 的处置。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 5 非阻断）。**

**Codex 意见 ③ 的两处修正都正确**，且我都做了独立实证：

- **`false → full` 正确**：`DesignSystemThemeManager.SetReducedMotion(false)`（`:405-415`）走 `CommitOverlay(ref _motionOverlay, null)`（`:411`）→ 移除 reduced 覆盖层、`ReducedMotion=false`，即**完整动效**（= `full`，不是 `auto`）；`auto` 在现有代码中不存在（无系统读取路径）✓。
- **`true → reduce + 三类全禁` 正确**：`Motion.Reduced.axaml` 全文 12 行，4 个时长键（`Fast`/`Instant`/`Normal`/`Slow`）全部 `00:00:00` + `Nm.Motion.Enabled=False` ✓。
- **与方案 r4 的迁移口径一致**：方案 `:865` 明写「旧 bool **true→off、false→on**」——C-03 修后的 `true→reduce`/`false→full` 与之一致（off=reduce、on=full）✓。
- **系统优先级冲突已显式声明**：C-03 `:59` 与 U-05c（`:86`）都写明「方案 r4 与本草案不能同时成立」，未隐藏 ✓；判据②（`:69`）已同步为「`full` 下不跟随系统（显式覆盖，见 U-05c）」✓。
- **C-02 V-05 判据④**（`:75`，本提交新增）准确：`ThemeCorners.MaxRadius`（`ThemeModels.cs:206` = `public const double MaxRadius = 3.0;`）确为共享上限，`ThemeValidator.cs:223` 的 `ValidateCorner` 依赖它（另有 `ThemePaletteComposer.cs:188`、`ThemeStudioEditorViewModel.cs:660` 也依赖）；④ 与 ①–③ 无重复/矛盾 ✓。
- **顺序铁律成立**：`ThemeService.TrySave`（`:647-661`）在 `:654` catch `IOException/UnauthorizedAccessException/NotSupportedException` 后只记 warning 返回 `false`；`ApplyAsync`（`:147-180`）在 `:159-165` 应用成功即调 `TrySave`、并在 `:179` **直接返回 `result`（不看保存结果）** → 「界面已应用但设置没保存」的判断成立 ✓；与 §2.1 `:29`、判据「迁移幂等」`:67`、「写者唯一性」`:66` 三处时序自洽 ✓。

5 条 P2 都是引用/措辞/选项完备性层面：方案 r4 的行号写错（`:866` → 实为 `:874`）、U-05c 缺第三种折中设计、`auto/full/reduce` 与方案 `on/off/system` 及两类「三类分类」命名未给映射、旧 `true` 分支的加载失败路径未纳入等价性说明、C-02 ④ 未指定「限定校验路径」的具体落点。

| 核验项 | 判定 |
|---|---|
| 1. 迁移等价性 | **通过**（`true`/`false` 两分支均实核；P2-4 第三分支说明） |
| 2. 系统优先级 | **部分**（冲突已显式声明 ✓；P2-1 引用行号错、P2-2 选项不完整、P2-3 命名映射缺） |
| 3. 判据② | **通过**（已随分歧声明同步改） |
| 4. C-02 V-05 判据④ | **通过**（引用准确、与 ①–③ 无重复；P2-5 落点待细化） |
| 5. 顺序铁律与判据表自洽 | **通过**（三处时序一致；理由经代码实核成立） |
| 6. 数据安全 | **通过**（只读；`check.ps1` PASS；未 push；工作树他人改动已记录） |

---

## 2. Findings

### P2

#### P2-1 — 方案 r4 引用行号错位：`:866` 实为 `:874`

- 位置：C-03 `:59`（「方案 r4 `:866` 写「系统 reduced motion **覆盖所有类别**」」）、`:86`（U-05c「本草案 vs 方案 r4 `:866` 冲突」）。
- 证据：方案 r4 `:866` 是迁移表 `FollowSystemAccent` 行；「…三类强度，**系统 reduced motion 覆盖所有类别**」实际在 **`:874`**；另 `:1041` 亦写「…三类动效分别切换且**系统 reduced-motion 优先**」。
- 建议：两处引用改为 `:874`（可并列补 `:1041`）。

#### P2-2 — U-05c 选项不完整（缺第三种合理设计）

- 位置：C-03 `:86`（U-05c 行）。
- 现状：只给「用户显式优先」（推荐）与「若改系统优先，`full` 语义与判据②需同步改」两种。
- 问题：第三种常见设计——**系统优先 + `full` 例外需二次确认/提示**（系统开 reduced 时用户选 `full` 弹确认或强制提示）——未列入；而它恰是「尊重系统辅助功能、但不完全剥夺用户显式选择」的折中，评审时容易被漏掉。
- 建议：U-05c 列三案：A 用户显式优先（推荐）/ B 系统优先全覆盖（方案 r4 现状）/ C 系统优先但 `full` 需二次确认；并注明 C 案对判据②/UI 的影响。

#### P2-3 — 三态与三类命名未与方案 r4 建立映射

- 位置：C-03 §2.3 `:48-54` vs 方案 r4 `:874`/`:1041`。
- 证据：方案用 `motion.mode=on/off/system`；C-03 用 `auto/full/reduce`（`on≈full`、`off≈reduce`、`system≈auto`，但文档未写）。方案的三类强度是 **page-transition/overlay/hover**（`:874`、`:1041` 写「页面/浮层/悬停」）；C-03 的三类是 **navigation/feedback/decorative**（`:52-54`），未给对应关系（如 overlay↔decorative？hover↔feedback？）。
- 影响：冻结后两套术语并存，实现者可能按方案的三类建字段、按 C-03 的键名写测试，导致分类/label 不一致。
- 建议：§2.3 加一行映射（`on=full`、`off=reduce`、`system=auto`；`page-transition→navigation`、`hover→feedback`、`overlay→decorative`（以实际语义为准）），或声明方案术语为「描述性、不进入契约」。

#### P2-4 — 旧 `true` 分支的加载失败路径未纳入等价性说明

- 位置：C-03 §2.3 `:56`（「旧 `true` → reduce 且三类全禁（等价旧行为…）」）。
- 证据：`SetReducedMotion(true)` 走 `TryLoadAndRecord(_resources.ReducedMotion, …)`（`:417`），**加载失败返回 `false` 且不进入 reduce**（`ReducedMotion` 保持 `false`，即实际仍是 full）；另有 `_disposed` 抛异常（`:407`）。而 C-03 的等价性说明只覆盖「true 成功 → reduce」与「false → full」两态。
- 影响：「等价旧行为」在 true 分支上并非无条件成立（旧运行时 overlay 加载失败时旧行为 = full）。迁移按**持久化值域**映射（true→reduce）本身正确，但措辞「等价旧行为」过强。
- 建议：补一句「迁移按**持久化值域**等价；旧实现在 overlay 加载失败时的瞬时行为（`SetReducedMotion` 返回 false）不纳入映射」。

#### P2-5 — C-02 ④ 未指定「限定校验路径」的落点

- 位置：C-02 V-05 判据④ `:75`。
- 现状：④ 禁止提高全局 `ThemeCorners.MaxRadius`，并要求「Fluent 必须走独立键组 + **限定校验路径**」——但未说明该路径落在哪：`ThemeValidator.ValidateCorner`（`:221-231`）目前对**所有** corner 键套用 `MaxRadius`（3.0），Fluent 的 4/6/8（`Nm.Corner.Fluent.*`）若走同一路径必被判违规；`ThemePaletteComposer.cs:188` 也是同一上限。
- 风险：实现者可能二选一——改共享上限（被 ④ 禁止）或不知道如何放行 Fluent 键，导致 U-04 批准后实现卡住。
- 建议：④ 补「限定路径」的具体形态，例如「`ValidateCorner` 对键名以 `Nm.Corner.Fluent.` 开头的项使用独立上限（4/6/8）；composer 路径同步；共享上限与 current-v2 校验不变」，或指向 V-03/FEA-04b 的键清单。

---

## 3. 六项核验明细（含代码证据）

1. **迁移等价性**：见 §1 与 P2-4。`Motion.Reduced.axaml` 全文 12 行（4 个 `Nm.Motion.Duration.*` = `00:00:00` + `Nm.Motion.Enabled=False`）；`SetReducedMotion` 两分支 `:409-415`（false）/`:417-425`（true）；文件头注「@generated … Reduced-motion overlay: zeroes every duration and flips Nm.Motion.Enabled to false」✓。
2. **系统优先级**：冲突**已声明**（`:59` 原文「两者不能同时成立。本草案取用户显式优先…」）；U-05c 存在（`:86`）；问题只在引用行号与选项完备性（P2-1/P2-2/P2-3）。
3. **判据②**：`:69`「②`full` 下不跟随系统（显式覆盖，见 U-05c 的分歧声明）」✓ 与 U-05c 推荐（用户显式优先）一致；与判据①③④⑤无冲突。
4. **C-02 V-05 判据④**：`:75` ④ 存在且引用准确（`ThemeModels.cs:206`、`ThemeValidator.cs:223` 实核）；`Nm.Corner.Fluent` 全仓 0 命中（尚未实现，符合计划态）；与 ①–③ 无重复/矛盾；P2-5 为落点细化。C-02 文件本提交仅此一行变更（+1/−1，`:75`），未触碰其它判据 ✓。
5. **顺序铁律**：`:70` 与 `:66`「兼容写不抛」、`:67`「兼容期内旧文件仍可写→结束转只读」、§2.1 `:29`「首次成功写入后兼容期→结束转只读」自洽；代码依据：`ThemeService.cs:647-661`（TrySave catch at `:654`）、`ApplyAsync :159-165` 与 `:179` 返回 `result`（不反映 save 失败）→ 结论成立 ✓。
6. **数据安全**：两份被审文件的**被审内容**未变（C-03 blob 全程 `3aea4d910`；C-02 仅状态行 `e9a4f5af1 → fcea994ae`，V-05 判据④ 正文逐字未变）；本轮只读，未改任何文件；`check.ps1` 实跑 `PASS (3 warnings)` EXIT=0；`origin/main..HEAD` = 195 提交（**未 push**）。**工作树一度非洁净**：C-05/C-07/C-12 三个 M + 三个新增 `FEA-CONTRACT-FROZEN-{C05,C07,C12}.md`（mtime 08:33:29–08:33:45），随后被另一 Agent 提交（`1017ea648`/`db6322191`/`7aa54bf23`）——**非本 reviewer 写入**，我全程未触碰。

> **治理提示（冻结时序）**：C-02 在**本轮复核期间**被冻结（`7aa54bf23`，状态行改为 FROZEN，内容即 V-05 判据④ 未变）。因此 **P2-5 属「冻结后发现」**：按冻结规则不应直接改冻结文本，建议登记到后续修订载体/Task；**C-03 尚未冻结**（矩阵第 4 步待第 3 步完成后），P2-1…P2-4 可在 C-03 冻结前直接修。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**，`task-24`）身份出具本报告，`reviewer_kind: subagent`，独立上下文。
- **未参与** C-02/C-03 撰写、未参与 Codex 意见处置、未参与 `apps/**`、`src/**` 任何实现；C-02/C-03 的既有复核报告由我出具（如实披露），本轮对两文件与代码/方案**直接读原文**重核，未引用既有报告结论。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰工作树中他人的在途改动。执行的命令为只读 `check.ps1`、`git`/`Get-Content`/`Select-String` 取证。
- **工作树状态记录**：任务 pin `reviewed_head = 2a540fcc3`；复核末 HEAD = `7aa54bf23`（另一 Agent 的 3 个冻结提交，见上）；被审两文件的被审内容未变；报告落盘后 `git status --porcelain` 仅有本报告（`??`）；`origin/main..HEAD` = 195 提交（未 push）。

---

## 5. NOT_RUN

- 未运行 `dotnet build` / `dotnet test` / 任何编译或单测（C-03 单测 ①–⑤ 属计划态）。
- 未验证「Avalonia 11.3.22 无动画开关 API」的论断（未查 Avalonia 源码/文档；该断言的正确性留给实现 Task）。
- 未核 Windows `SPI_GETCLIENTAREAANIMATION` / WinRT `UISettings.AnimationsEnabled` 的实际可用性。
- 未核 C-02 其余判据（①–③、V-01…V-10）与 V-04/V-06/V-07 的完整内容（只核 V-05 判据④）。
- 未核 FEA-04b 的 4/6/8 数值基线（计划态）。
- 未核远端历史细节（仅核本地 `origin/main..HEAD` 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×5 非阻断）。
