---
document_id: FEA-GOV-4-c02-r2
kind: independent_review
task_id: FEA-GOV-4
round: 2
scope: narrow（只核 r1 的 4×P1 + 6×P2 处置、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（按 lead 直接派发；未参与 C-02 草案撰写，未参与 V11R 合同 / 方案 / C-01b / C-03 / C-11 撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-4-c02-review（r1：changes_requested，P0×0 / P1×4 / P2×6）
reviewed_head: bc2fd4d2b
reviewed_head_full: bc2fd4d2b398745ce9a738f11a516eed4639f158
reviewed_head_note: "复核期间 HEAD 未前进（维持 bc2fd4d2b）"
reviewed_document: doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md
reviewed_sha256: 9c56e7eb85c39de9686dc6471ba472e08e7295b0560feb658c1210132d6e134a
reviewed_sha256_basis: "HEAD 的 LF blob（140 行，blob 8a6a6a16d）；与 reviewed_head 相同"
baseline: "doc/plan/V11R_AVALONIA_CONTRACT.md（FROZEN v1）· doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md（r4 @ 74a772167）"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为不阻断的编辑/统一性问题（V-03「三组」未随四组更新与引用块位置、V-08 两处编辑残留、V-03/V-05 归属键仍用 frontend id），登记为 K-1/K-2/K-3"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T03:50:49+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（窄面）：FEA-C02 V11R 修订单处置确认

**本报告不是** 冻结动作、不是对 V11R 冻结合同的修改，也不构成执行授权。本轮只核 r1 的 4×P1 + 6×P2 是否处置到位、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断）。**

r1 的 **4 条 P1 全部实质解决**：

- **P1-1 ✅**：V-01 已限定为「**本修订单不新增项目**；界面项目（`Frontends.Fluent`、Application/Presentation）按方案 §15.2 的 §1.1 行需 DSH 批准并单独建 Task」，判据改为「**本修订单的改动**不得新增 `NewManga.*.csproj`」+「新增界面项目须有独立 Task 与 DSH 批准记录」——与方案 §15.2 §1.1 行和 §15.6 FEA-06/FEA-07 写域**不再冲突**。
- **P1-2 ✅（V-07 主体到位）**：V-07 已显式区分 **frontend id**（`builtin.current-v2`/`builtin.fluent`，`newmanga.frontend/1`，不进 ThemeEngine 契约）与 **视觉主题 id**（现有 `newmanga-default`，新增 `builtin.fluent-dark`），并给出 `perFrontend` 映射与判据「frontend id 不进入 ThemeEngine 公开面」；V-05 圆角行已改用视觉主题 id。残留 3 处仍以 frontend id 指代主题包（K-3，非阻断）。
- **P1-3 ✅**：V-08 已拆为 **V-08a（§6.1 空间/模式：`SpaceId`/`StudioMode`/`ShellSurface`/`ShellState`/`AppShellV2`）** 与 **V-08b（§6.3 快捷键，按方案 `:852` 立「按 scheme/窗口/焦点上下文路由、仍进程级唯一」）**，两节现行文本概括均正确。仅剩编辑残留（K-2）。
- **P1-4 ✅**：V-03 已增第四组「圆角（Fluent 扩展）`Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)`」，V-05 圆角行改为「冻结组 `None/Sm(2)/Md(3)` **不变**；Fluent 额外使用 `Nm.Corner.Fluent.*`（新增组，随 V-03 登记）」——与 r1 建议逐字对应。

r1 的 6 条 P2 **全部到位**（15 组/40 个、§4、SukiUI、DSH 逐 Task 指派 + 全路径、数值时序、Fluent 专属最小集声明）。

3 条非阻断 P2 均属**编辑/统一性**问题（见 §3 与 K-1/K-2/K-3），不影响冻结判断。

| 核实项 | 结果 |
|---|---|
| 1. P1-1 项目授权 | **✅ 已处置**（限定范围 + 判据改写 + 独立 Task/DSH 批准记录要求） |
| 2. P1-2 双 id 体系 | **✅ 主体到位**（V-07 定义 + 映射 + 判据；K-3 为 3 处归属键残留） |
| 3. P1-3 §6.3 拆分 | **✅ 已处置**（V-08a/V-08b，现行文本正确；K-2 为编辑残留） |
| 4. P1-4 圆角组 | **✅ 已处置**（`Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)` + 冻结组不变） |
| 5. P2-1 计数 | **✅**「15 组」「40 个」 |
| 6. P2-2 §4 引用 | **✅**「V11R §4」 |
| 7. P2-3 SukiUI | **✅** 已补 |
| 8. P2-4 V-02 写权/路径 | **✅**「DSH 逐 Task 指派（建议 ZCode）」+ `apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/**` |
| 9. P2-5 U-04 数值时序 | **✅** 已补「4/6/8 与材质参数由 FEA-04b 确认；本单只冻结『键存在 + 仅 Fluent 生效』的结构」 |
| 10. P2-6 Fluent 专属声明 | **✅** 已补「上述四组为 Fluent 专属最小集，不改变 V11R §2.2 对 Current 主题的全局义务」（位置/措辞见 K-1） |
| 11. 新问题 + `check.ps1` | 无新增实质问题；`check.ps1` **PASS (3 warnings) EXIT=0**；未 push；无代码/用户数据改动 |

---

## 2. 10 处核对明细

### 2.1（P1-1）V-01 项目授权 —— ✅

- 修订（`:33`）：「**本修订单不新增项目**；Fluent 的主题包部分落在 ThemeEngine 内（见 V-07）。**界面项目**（`Frontends.Fluent`、Application/Presentation）的新增**按方案 §15.2 的 §1.1 行**——需 DSH 批准并单独建 Task，不在本修订单范围内。」
- 判据（`:34`）：「**本修订单的改动**不得新增 `NewManga.*.csproj`；Fluent 主题包资源落在 `apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/**` 既有结构内。新增界面项目须有对应的独立 Task 与 DSH 批准记录。」
- 与基准对齐：方案 §15.2 §1.1 行「增经批准的 `Frontends.Fluent`、Application/Presentation 项目与单向依赖图……新增项目路径须列 Task 写域」（`:844`）、§15.6 FEA-06 写域（`:927`）均不再被本单否决 ✓。r1 P1-1 闭环。

### 2.2（P1-2）双 id 体系 —— ✅ 主体到位（K-3 残留）

- V-07（`:88-90`）已明确两套 id 及其归属：frontend id 在方案侧（`activeFrontendId`/`perFrontend`）、视觉主题在 `ThemeKind.BuiltIn` 侧；`perFrontend` 映射 `builtin.current-v2 → newmanga-default`、`builtin.fluent → builtin.fluent-dark`；判据「视觉主题注册表新增 `builtin.fluent-dark` 条目；frontend id 不进入 ThemeEngine 公开面」✓ 可执行。
- V-05 圆角行（`:72`）已改为「仅视觉主题 `builtin.fluent-dark`（及同 frontend 的其他 Fluent 视觉主题）」✓。
- 残留：V-03 适用域（`:56`）、V-05 材质行（`:71`）、V-05 判据②（`:73`）仍以 `builtin.fluent`/`builtin.current-v2` 指代主题包 → K-3（因 V-07 已给出映射，读者可解析，非阻断）。

### 2.3（P1-3）V-08 拆分 —— ✅（K-2 编辑残留）

- V-08a（`:93-97`）现行文本 = `SpaceId`/`StudioMode`/`ShellSurface`/`ShellState`/`IWorkspaceView`/`AppShellV2` ✓ 与 V11R `:245-265` 一致；修订「独立 frontend 项目 + §6.1 语义一致，三枚举值不得变化、ShellState 仍唯一状态源」✓。
- V-08b（`:99-105`）现行文本 = 快捷键 + `Shell/V2/KeyMap.cs` 单一注册表 + 冲突启动断言 ✓ 与 V11R `:274-277` 一致；修订按方案 `:852`「按 scheme/窗口/输入焦点上下文路由（`contextKey = (frontendId, windowRole, focusScope)`），仍进程级唯一」✓ 与方案 §15.2 §6.3 行一致。
- 编辑残留：`:104-105` 连续两行「**例外登记**：无需。」（旧 V-08 行未删净）；`:95` 现行文本末夹带「§6.3 定义快捷键…」（与 V-08b 重复）→ K-2。

### 2.4（P1-4）圆角组 —— ✅

- V-03（`:47-53`）新增第 4 组「圆角（Fluent 扩展）｜`Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)`｜`CornerRadius`」✓。
- V-05 圆角行（`:72`）：「冻结组 `Nm.Corner.None/Sm(2)/Md(3)` **不变**；Fluent 额外使用 `Nm.Corner.Fluent.Sm(4)/Md(6)/Lg(8)`（**新增组，随 V-03 登记**）」✓ —— 与 V11R `:60` 的冻结键集不再冲突，且 current 侧无 `Lg` 使用 ✓。r1 P1-4 闭环。

### 2.5（P2-1…P2-6）—— ✅ 全部到位

| P2 | 现文 | 判定 |
|---|---|---|
| P2-1 计数 | `:46`「V1 最低集 **15 组**」；`:84`「§3.2 自定义控件清单（**40 个**）」 | ✅ |
| P2-2 §4 引用 | `:124`「**V11R §4**（ThemeEngine 公开面）」 | ✅ |
| P2-3 SukiUI | `:111`「禁止引入 `FluentAvaloniaUI` 与 **SukiUI** NuGet」 | ✅ |
| P2-4 V-02 | `:40`「由 **DSH 逐 Task 指派**（建议 ZCode）写」+ 路径 `apps/desktop-avalonia/src/NewManga.ThemeEngine/Themes/**` | ✅ |
| P2-5 U-04 时序 | `:75`「**数值时序**：4/6/8 与材质参数的具体取值由 FEA-04b 四页设计基线确认（方案 `:1032`），本修订单只冻结『键存在 + 仅 Fluent 生效』的结构」 | ✅ |
| P2-6 专属声明 | `:55`「上述四组为 **Fluent 专属最小集**，不改变 V11R §2.2 对 Current 主题的全局义务」 | ✅（位置/自指见 K-1） |

### 2.6 新问题 + `check.ps1` + 数据安全

- **新问题**：无新增**实质**问题；仅 K-1/K-2/K-3 三处编辑级问题（详见 §3）。
- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（3 条 warning 为既有：7 个非终态 Task、`STATUS.md` 2883 B / 80%、`REBASELINE_PLAN.md` 6547 B / 80%）；运行后 `git status` 为空 ✓。
- **数据安全**：`bc2fd4d2b` 只改两个文件（C-02 草案 +42/−16、r1 报告 +213），`git diff --stat 0c491d0db..HEAD -- src apps` 为**空**（无代码改动）；**未 push**（`bc2fd4d2b` 非 `origin/main` 祖先）✓。
- 被审字节：C-02 草案 @ `bc2fd4d2b`，LF blob SHA-256 `9c56e7eb85c3…2d6e134a`（140 行）。

---

## 3. 已知限制（非阻断）

#### K-1 — V-03「适用域限定：这**三**组」未随第四组更新；引用块位置与自指措辞

- 位置：`:56`（「这三组仅在 `builtin.fluent` 主题包内必须存在」）、`:55`（`>` 引用块「…（V-03 末尾）」）。
- 问题：① 已新增 4 组，但适用域句仍写「三组」→ 与 `:47`「新增 4 组」矛盾；② `>` 引用块插在列表项之间、且「（V-03 末尾）」为自指，渲染与阅读都不自然。
- 建议：改为「这四组……」；把 `>` 行改为普通文本行或移到条款末尾。

#### K-2 — V-08 的两处编辑残留

- 位置：`:104-105`（连续两行「例外登记：无需」）、`:95`（V-08a 现行文本夹带 §6.3 快捷键概括）。
- 建议：删掉重复的一行；把 §6.3 的概括从 V-08a 移到 V-08b（V-08b 已有同样内容）。

#### K-3 — V-03/V-05 仍有 3 处以 **frontend id** 指代「主题包」

- 位置：`:56`（V-03 适用域：`builtin.fluent` 主题包 / `builtin.current-v2`）、`:71`（V-05 材质行：仅 `builtin.fluent` 主题包…`builtin.current-v2` 不得使用）、`:73`（V-05 判据②：current-v2 下出现材质…判违规）。
- 说明：V-07 已给出映射，读者可解析；其中 `:73` 的判据② 以「当前 frontend = current-v2」为条件其实是**合法**的 frontend 级规则。
- 建议：只需在 §4 或 V-03 加一句「本单中『`builtin.fluent` 主题包』指其视觉主题 `builtin.fluent-dark`；『current-v2』指界面 `builtin.current-v2` 及其视觉主题 `newmanga-default`」即可统一，无需逐格改写。

---

## 4. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与** C-02 草案撰写（作者 = DSH）、未参与 V11R 合同 / FEA-00 方案 / C-01b / C-03 / C-11 撰写，未参与 `src/**`、`apps/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改 C-02 / V11R / 方案 / Task 卡 / 状态表；未 `git add`/`commit`/`push`；未触碰真实数据根。唯一执行的命令为只读 `check.ps1`（运行后 `git status` 为空）与只读取证。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == bc2fd4d2b`；被审文件 blob `8a6a6a16d`。

---

## 5. NOT_RUN

- 未运行 `pytest` / `dotnet test` / 任何构建（纯文档治理）。
- 未执行任何冻结或合同修订动作（本稿仍为 DRAFT；冻结须独立复核 + 用户裁决 U-04 + DSH 执行）。
- 未审计 V11R 合同其余条款（§5 服务层、§7 构建与证据、§8 变更记录不在本单范围）。
- 未复核 C-03 / C-11 草案（另由 FEA-GOV-4 其他 Review 承担）；仅指出 C-03 与 C-02 共享同一套 id 词汇，建议其复核一并对齐 K-3 的澄清句。
- 未验证 `nm.fluent.visual/1` 的实际 schema 与校验器实现（仓库当前无该 schema 文件，属计划态）。
- 未核远端历史细节（仅核本地 main 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3 非阻断；10 处核实：9 全到位 + 1 主体到位（K-3 残留）；`check.ps1` PASS）。
