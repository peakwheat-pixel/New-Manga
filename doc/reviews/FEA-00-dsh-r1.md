---
review_id: FEA-00-dsh-r1
task: FEA-00（候选切片；仓库无 FEA-00 Task 文件、无 worktree，未释放实现）
author: Codex（方案作者，未参与本次审查）
reviewer: DSH 独立 Reviewer 池 `review-a-frontend-shell` / `review-b-source-state` / `review-c-appearance-task`（三者均未参与方案编写）；DSH Lead 汇总、交叉复核与裁决
reviewer_independent: true
reviewed_by_implementer: false
zcode_reviewer_status: reviewer_unavailable（本机无 `zcode` CLI，仅有 Electron 桌面应用与 pending updater；见 §1.4）
round: 1
reviewed_document: doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md
reviewed_document_sha256: bc309965cfb6cc2a1c8dd37a144e77ad4dca8664eddee6e7c2e87fe3da5ac85f
source_head: 1180cdba79e4d610521dde13f0c8a458220f9d90
source_branch: main
requirement_document_sha256: 508273c4599f9a0e1e33250f9b4d75660ee72fbd7d0c76f678b7aa7751979808
verdict: changes_requested
captured_at: 2026-10-31T18:38:12+08:00
captured_by: DSH（Lead / Architect / Integrator）
---

# 独立 Review：FEA-00 可切换前端架构方案（第 1 轮）

**本报告不是** ADR、冻结契约、Task 释放、实现验收或集成批准。它固定被审文档的字节与源码 head，给出 findings、十项架构问题结论、阻塞项与 DSH 处置清单。`verdict: changes_requested` —— 不含批准。

## 1. 范围与依据

### 1.1 被审对象与定位方式

| 项 | 值 | 复核方式 |
|---|---|---|
| 仓库 | `G:/CODEX/New Manga`（Git common dir = 仓库内 `.git`） | `git rev-parse --git-common-dir` |
| 分支 / HEAD | `main` / `1180cdba79e4d610521dde13f0c8a458220f9d90` | `git rev-parse HEAD`（与任务给定基线一致，无漂移） |
| 被审方案 | `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`，793 行，**未跟踪（`??`）** | `Get-FileHash -Algorithm SHA256` |
| 方案 SHA-256 | `bc309965cfb6cc2a1c8dd37a144e77ad4dca8664eddee6e7c2e87fe3da5ac85f`，与冻结值**逐字节一致**（审查前后各算一次） | 同上 |
| 需求来源 | `doc/design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md`，259 行，未跟踪；SHA-256 `508273c4…1979808` | 同上 |
| 未被审 | `main@1180cdba` 之后不存在该方案的任何提交；**方案不能只用 HEAD 定位**，故以文件 SHA-256 为主定位、HEAD 为代码证据的定位 | — |

**时点漂移登记（不覆盖、不还原他人内容）**：审查开始时工作区有 **9 个 tracked 文档 modified**（`.orchestrator/RUNTIME_DIRECTIVES.md`、`.orchestrator/agents.json`、`AGENTS.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、`doc/AI_COORDINATION.md`、`doc/GOVERNANCE_TAKEOVER_2026-10-25.md`、`doc/V11R_PROGRAM.md`、`doc/design/EXECUTION_DIRECTIVE_AD002_V2.md`）与 2 个 untracked（方案 + 需求）。这些改动属其他作者，本次未触碰。核对 `git diff -- AGENTS.md` 确认**产品边界行（`AGENTS.md:43`）未变**，故架构边界引用对 HEAD 与工作区同时成立。

因此方案 §14.3 所述"`git diff --name-only`：无 tracked 文件修改"是**交付时点陈述**，审查时已不成立；这是他人改动的时点差异，**不是方案作者的错误**，但任何以该句为证据的结论都需重新取时点。

### 1.2 审查范围

方案 §1–§14 全文（重点 §1、§2 表 F01–F22、§3、§4.1/4.2/4.3、§5、§6、§7、§8、§9、§10、§11、§12、§13、§14），逐条回答用户十项架构问题，并对照：需求文档 §1–§7 全量、`AGENTS.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/plan/V11R_AVALONIA_CONTRACT.md`（FROZEN）、`doc/V11R_PROGRAM.md §8`（R-01..R-25）、`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（§1.4/§3/§5/GAP）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md §5.11.2`、当前 Task `REALUSE-DATA-SAFETY-6`、真实生产代码（C# / Python）。

**不在范围**：实现、契约冻结、Task 释放、真实用户数据迁移、任何写操作；`verification/**` 历史证据（除 `doc/STATUS.md` 明确引用者外不扫描）。

### 1.3 审查方法（事实 / 建议 / 假设三分）

- **[代码核实事实]**：本次直接读取当前 HEAD 的代码、测试、权威文档得到的静态事实。**不代表运行通过**。
- **[架构建议]**：方案的主张，尚未冻结为契约或实现。
- **[待验证假设]**：方案 H1–H7 与本次标注的未验证判断。
- 判据纪律：**不把概念图、接口声明草稿、冻结文档中的枚举/类型清单、历史计划当作已实现能力**；对方案的每条"已核实事实"都回到生产调用点、事务边界与测试去核对，而非只读类型声明。
- 机械核验：对方案内 55 处 markdown 文件引用与 `#L` 行号做**全量存在性与范围**校验；对治理检查器做**读实现 + 只读运行**双重核验。

### 1.4 独立性、席位与写权（DSH 冻结）

| 项 | 冻结值 |
|---|---|
| 切片 Owner（协调/处置） | DSH（Lead / Architect / Integrator）；DSH 未参与方案编写，不构成自审 |
| Reviewer 席位 | ZCode：`reviewer_unavailable`（`Get-Command zcode` 未命中；仅有 `%APPDATA%\ZCode` 桌面应用与 pending updater）。Codex：**因系方案作者回避**（"不得审自己的方案"） |
| 实际执行 | 按 `doc/V11R_PROGRAM.md §5` 的 "Reviewer = Codex / 独立 DSH teammate（不参与实现）" 条款，DSH 指派 3 名未参与编写的独立 Reviewer 分片审查，DSH 汇总并交叉复核 |
| 写权 | Reviewer 仅写 `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/slice{A,B,C}.md`；DSH 仅写**本报告**。方案、生产代码、需求、Task、STATUS、Plan、冻结历史证据**均未修改** |
| 报告路径 | `doc/reviews/FEA-00-dsh-r1.md`（用户建议路径为 `FEA-00-zcode-r1.md`；因 ZCode 不可用，按实际作者命名，避免伪造署名） |

**口径声明（必须随结论一起引用）**：`AGENTS.md:34` 规定独审由未参与实现的 ZCode 或 Codex 执行。本轮两者均不可得，故**本报告不构成**该条文意义上的"独立批准"，其 `verdict` 仅为 `changes_requested`，**不含任何批准语义**。若后续需要正式批准，必须由 ZCode 恢复可用或由用户另行裁决席位，并对**同一 hash 的修订版**重新 Appointment。

**方案作者的可信度说明（正面核验）**：方案对其自身性质（"不是 ADR/冻结契约/Task 释放"）、对 `IRunProjectionPoller` 实体缺失、对 STATUS/命令标题差异、对 F20 写入时序风险的**主动登记**是诚实的；本次未发现"把概念图或冻结文档枚举当作已实现能力"的系统性问题。问题集中在**引证精度**、**个别断言的定级**、**契约修订的条款级缺失**与**需求覆盖的归属缺口**。

## 2. Findings

严重度口径：**P0 = 阻塞采纳**（方案在处置前不得转为契约冻结或释放候选 Task，或对应能力线必须 `blocked`）；**P1 = 进入实现前必须处置**（否则必然返工，或破坏"无第二业务真值 / 不丢输入 / 不提前覆盖"目标，或与冻结契约冲突）；**P2 = 精度、归属、边界与可验证性改进项**，可与后续修订并行。

### 2.1 P0 — 阻塞采纳

| ID | 级别 | 文档位置 | 代码/文档证据 | 具体失败场景 | 影响 | 建议修订 |
|---|---|---|---|---|---|---|
| **F-01** | **P0** | §1:25；§13.1:716（"引用原件已确认，不重新询问这些方向"）；§13.2 D01:732；§14.2 第 7 行:777 | `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md:4`（哨兵 `… + SQLite + Managed Copy`）、`:5`（`Decision authority: User`）、`:14`、`:23`（"Managed Copy｜保持既有实现与验收"）；`AGENTS.md:43`（"后续 Task…只允许落在该架构"）；`tools/governance/check.ps1:259-262`（只校验 AD-002 全文仍含哨兵字面量）；需求文档 `:18`、`:251` 自认需架构裁决 | DSH 若按 D01 由"DSH 冻结"直接把 ReferencedSource 写进 AD-002：① 这是**用户裁决的架构决策**（AD-002 `Decision authority: User`），DSH 单方修订越权；② 若改哨兵字面量，`check.ps1` 会红（`AD-002 缺少冻结的唯一目标架构哨兵`）；③ 若保留哨兵再加覆盖章节，检查器**仍全绿**，形成"文档通过、架构未裁决"的既成事实 | Source 线（FEA-08/09/11/12/13）在无架构授权下开工；备份完整性定义、回收站能否触及原件、迁移方向、资源通道信任根、删除授权模型五项下游全部连带变更 | ① 将"默认存储语义 Managed Copy → ReferencedSource"升格为**用户的 ADR 裁决项**（AD-002 v1.1 或新 AD-003），裁决前 Source 线 `blocked`；② §13.1 改写为"产品目标已确认 / **架构决策未裁决**"；③ D01 增列下游反转清单（备份/回收站/迁移/资源通道/删除授权）与 `check.ps1` 哨兵口径处置；④ 明确 `check.ps1 PASS` **不能**作为架构一致性证据 |
| **F-02** | **P0** | §9.1:497（"不能因'用户点彻底删除'绕过**已冻结** current/pinned 规则"）；§9.1 表:472、§9.2:486-497 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:735`：「DB 全有/全无：…**移除项目 Lock/current/pinned Revision**…」（本轮已独立复核该行原文）；实现一致：`src/infrastructure/sqlite/library.py:1069-1101` `execute_permanent_delete_db` 直接 DELETE `artifact_revisions`/`region_revisions`/`regions`/`pages`/`books`；pin 的冻结语义仅覆盖 **cleanup**：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md:267` | 用户在回收站对含人工锁定译文的书执行"彻底删除"：按方案实现 → protection preflight 拒绝（用户无法删除自己的书）；按冻结契约实现 → 方案声称的"不得绕过"被违反 | **对冻结契约的反向陈述**：方案把"新增保护策略"写成"沿用已冻结规则"，实现方无论选边都破坏一边；且方案未把它列为契约反转，DSH 处置清单（D07）无此项 | ① §9.1 改判为"**与 `M2-C1 §5.11.2` 现行语义相反，需 DSH 裁决**"；② 区分三层保护：GC/清理（pin/current 有保护）、应用回收站软删（不删数据）、**用户显式彻底删除**（现行=解除保护，方案提议=拒绝）；③ D07 增列 `M2-C1 §5.11.2`（含 `:752`）修订项与其测试影响面；④ §13.1 "彻底删除终局流程"标注为**与冻结契约冲突的用户取舍** |

### 2.2 P1 — 进入实现前必须处置

| ID | 级别 | 文档位置 | 代码证据 | 具体失败场景 | 影响 | 建议修订 |
|---|---|---|---|---|---|---|
| **F-03** | P1 | §4.1:140（只列"V11R §2/§3/§6"）；§7.1:346（单列 §4）；§13.2 D02:733（列"§1/§2/§3/§4/§6"）；§6.1:288（`nm.fluent.visual/1`） | `V11R_AVALONIA_CONTRACT.md:19-21`（新 UI 代码只落 `Views/V2`/`ViewModels/V2`/`Shell/V2`）、`:26-33`（`NewManga.sln`/`App.axaml`/`App.csproj`/`App.axaml.cs` 唯一写者=DSH）、`:66`（禁止圆角>3px/阴影/渐变/模糊）、`:69-72`（状态符号由 DS `StatusGlyph` 提供，UI 不得自造）、`:76-90`（R-14 唯一例外清单）、`:91-113`（DS 公开面）、`:150-164`/`:187`（`IThemeService`/`IThemePersistence` 冻结面）、`:191`（切换不得重建窗口）、`:253`/`:265`/`:277`（ShellState 唯一状态源 / AppShellV2 唯一窗口内容 / KeyMap 单一注册表）；需求 `:14`、`:212`（亚克力/圆角/层次/模糊）；`V11R_PROGRAM §8` R-03（不引入 SukiUI/FluentAvalonia） | DSH 依 §4.1 只改 §2/§3/§6 → FEA-05 落地时才发现 §1.2 写权与 §4 持久化语义必须改；或依 D02 泛改但漏 §2.4 例外登记与 §6.1/§6.3 → 独立审查仍可依 §2.4 判 Fluent 违规，或反之 Fluent 事实上豁免全部令牌纪律形成第二套 DS | 冻结契约修订范围**三处口径不一致且无条款级替换文本**；`nm.fluent.visual/1` 与 R-01/R-11"单一设计系统"的关系未处置 | 合并为**一张逐条契约修订清单**：条款号 → 现行文本 → 修订文本/适用域 → 审查判据 → 例外登记要求。至少覆盖 §1.1/§1.2/§2.2/§2.3/§2.4/§3/§4/§6.1/§6.3，并显式重申 R-03（"Fluent"=视觉风格，不是 FluentAvalonia 依赖） |
| **F-04** | P1 | §12.1 FEA-06:622（依赖"**已冻结四页设计**"）；§13.1 末:726 | 需求 `:9`/`:16`（效果图是视觉概念，不构成功能要求）、`:31`（不强制其他方案采用左导航/相同尺寸）、`:259`（"当前图像存于会话生成目录…并非版本化设计资产；如需冻结视觉基线须另行选定、保存与评审"）；`doc/design/redesign-v1/40-fusion/` 是**当前三空间** V2 设计基线，不是 Fluent 四页 | FEA-06 唯一设计依赖物**不存在**：S2 要么无法开工，要么实现后无验收基准（返工） | 候选 DAG 存在悬空依赖；S2 的"四页和四页预览"不可判定 | 新增前置候选 Task（如 `FEA-04b` Fluent 四页交互与视觉规格冻结，Owner ZCode 起草 / DSH 冻结，依赖 FEA-00 与用户 §13.1 裁决），并把 FEA-06 依赖改指该交付物 |
| **F-05** | P1 | §12.1:614-631（写域列只有"组件/目录"级）；§6.1:316 | `V11R_AVALONIA_CONTRACT.md:26-33`（组合根与 `App/Views/V2/**`/`Shell/V2/**` 的唯一写者分别是 DSH / ui-shell / ui-studio） | FEA-05/06 必须新建项目并接线 `NewManga.sln`/`App.axaml`/`App.csproj`（唯一写者=DSH），候选表却把 Owner 写成 ZCode；FEA-04 要动 ui-shell/ui-studio 写域 | 释放即要么越权违反 V11R §1.2，要么任务无法完成；S2 并行期冲突概率最高 | 候选表为每行补 `write_scopes`（workspace-relative 目录前缀）+ `shared-file owner`（组合根由 DSH 单点提交）；FEA-04 明确沿用 V11R §1.2 写权还是 DSH 重新指派 |
| **F-06** | P1 | §6.1:298-318（新 `presentation-settings.json` 含 `appearance/contrast/reducedMotion/perFrontend`；:316 声称"迁移后不能存在两个写者"）；§4.3:212（复用 Theme **Persistence**） | `NewManga.ThemeEngine/Service/ThemeService.cs:163/213/227/244/258/268/277/294/326`（每个 setter 末尾 `TrySave`）、`:647-661`（`_persistence.SaveAsync`）、`:392-396`（Initialize 迁移后回写）；`Persistence/ThemeSettingsStore.cs:131-166`（原子写 `theme-settings.json`）；`App.axaml.cs:104-113` 生产注入口；冻结 `V11R_AVALONIA_CONTRACT.md:150-164`、`:187` | 用户在 Fluent 设置页改外观 → 打开 Theme Studio 应用主题（`ThemeService` 用自己内存里的 `_settings` 回写旧文件）→ 重启：两个文件都声明 appearance 权威，后写者生效，设置页与界面不一致；叠加切换事务的 `last-known-good` 无唯一落点 | **第二份业务真值直接成立**（正是十项问题 1 的核心）；Theme Studio 仍是外观第二写者 | ① DSH 在 FEA-01/D02 冻结**唯一写者**（建议 `presentation-settings.json` 唯一，ThemeEngine 降为 sink-only 或 `IThemePersistence` 适配到同一文档）；② D02 明确 `IThemeService.Settings`/`IThemePersistence` 语义变更；③ FEA-05 AC 增"迁移后旧文件字节不再变化、任何 setter 不再写旧文件" |
| **F-07** | P1 | §2 F20:62（"本次未复现为缺陷"）；§10.3 第 1 条:567（"不能提前改 live `regions.text_json`"）；**§14.2 第 9 行:779 却把"prepare 不提前写 live"列为已覆盖**；§12.1 FEA-10:626 | `src/infrastructure/providers/step_writes.py:195-281`：`_persist` 在**独立事务** `BEGIN IMMEDIATE`（207）→ 只比对 `current_revision_id`（219-231）→ `INSERT region_revisions`（248-266）→ **`UPDATE regions SET text_json=…`（269-276）→ `commit()`（277）**；模块注释 `:267-268` 自述"text 归 region 所有，**pointer 留给 seam**"；seam 另事务 `pipeline.py:742-800` 才 CAS 指针，`:798-800` 走 `db_failed`。本轮已独立复核该段 | ① 运行中一次 DB 错误或 `write_in_current_transaction` 抛 `STALE_RUN_SNAPSHOT` → `commit_step` 失败，指针回滚但 **text_json 保留机器译文**；② prepare 与 seam 之间另一写者改指针 → seam 拒绝，text 已被覆盖；③ prepare 后崩溃 → 重启 run 为 INTERRUPTED，live 文本显示从未提交的结果 | "live 文本零提前变化"在现有 Core 上**不成立**；方案 §14.2 却把它列为已覆盖，属**内部自相矛盾**，会让 DSH 误判结果应用安全已达标 | ① F20 改判为 **[事实] 数据安全缺陷**（非"未复现"），并说明这是既有 Core 缺陷、需独立修复门；② 明确处置位置（先于双 UI，或与 FEA-10 拆出的"prepare 不写 live"小任务），不得只挂在 S3"完整验证"；③ FEA-10 AC 增可执行回归：**prepare 后 seam 拒绝/抛错 ⇒ `regions.text_json`、`current_revision_id`、`region_revisions` 行数三处零变化**，覆盖 pause/cancel/crash |
| **F-08** | P1 | §10.2:559（"继续/失败重试默认复用原快照"）；§12.3 A05/A06:688-689 | `src/application/tasks/service.py:1112-1138` `retry_failed_targets` → `create_run(..., source_run_id=…)` 无 overrides；`create_run` 内 `service.py:245` `frozen = snapshots.freeze(...)` 取**当前** defaults；对比 `plan_run(mode="continue")`（`:367-417`）复用同一 run 对象 | 用户改了模型/提示词/词表后点"重试失败页" → 新 run 用**新**配置静默重跑，与需求 `:168`/`:171`"任务启动后的设置修改只影响新任务""失败重试默认沿用原快照"相反 | 任务快照承诺在 retry 分支破裂；用户无法解释同一任务为何换模型；A05/A06 未覆盖 | §10.2 明确 retry 二选一语义（复用 source run 快照并显示差异 / 显式创建关联新任务）；FEA-10 AC 与 A05 增"修改配置后重试失败页 → payload/model 与 source run 快照一致或已显式确认" |
| **F-09** | P1 | §7.1:365-371（Flush/Checkpoint 依赖"草稿写入共享 session 并等 journal ACK"）；§12.1 FEA-04:620（"无 VM 私有第二份业务真值"）；§5.2:265 | `StudioPageViewModel.cs:265-301`（ctor 注入 `IHostController`；私有 `_runProjection:259`、`_lastRerenderSummary:258`、`_pendingNavigation:257`）、`StudioInspectorViewModel.cs:282,289`（`_pendingRegionType` 仅 VM）、`StudioBatchViewModel.cs:306-316,329`（私有 `_runId/_projection/_intentIdempotencyKey`）、`ReaderOverlayViewModel.cs:25-38`、`ConsoleViewModel.cs:21,200-215` | 用户在 V2 Studio 改区域类型但未保存（pending 只在 Inspector VM）→ 切到 Fluent：切换事务只 flush "共享 session 草稿"，该 pending 从未进入共享缓冲 → 旧内容树释放 → **编辑丢失**；反向，FEA-04 若严格"无 VM 私有真值"则接近重写 1785 行 `StudioPageViewModel` 与 2752 行 `ConsoleViewModel` | 十项问题 1 与 3 在首阶段都无法闭环；FEA-04 变成无界隐性重写，与 §4.1:116"不一次物理搬动所有代码"冲突 | ① FEA-01 冻结"**必须迁出的状态清单**"（按 VM/字段）；② FEA-04 逐项验收 + V2 行为不退化基线；③ 明确 **fail-closed**：存在未迁移 VM 私有编辑态时阻止切换（§7.2:381 已有"中止切换"分支，需落到 Current VM） |
| **F-10** | P1 | §5.2:265（"同一区域首阶段只允许一个活跃写 session，**其他窗口只读镜像**"）；§3:110；§7.3:389-395 | 需求 `:143`（编辑/待处理面板"可拖出独立窗口到第二显示器"）、`:148-150`（画布拖动改几何 + 面板改样式）；方案 §7.3 自己也支持浮窗 | 用户把编辑面板拖到副屏并选中区域：在主窗画布拖动改几何、同时在浮窗改字号/颜色（需求明确允许）→ 按 §5.2 浮窗只能只读；若实现为都可编辑，则"单一活跃写 session"无对应机制（未定义同 `DraftId` 下几何/样式/文本的分域并发） | Fluent 工作台核心交互在多窗口下不可用或走样；十项问题 5 的"多窗口可编辑"不能成立 | 改为按 `(SessionId, RegionId)` 的 draft owner，并定义同 `DraftId` 的分字段并发规则（几何/样式/文本分域，禁止自动文本合并）；或明确"浮窗只读"并列为用户取舍项（见 §5.3 U-03） |
| **F-11** | P1 | §8.1:413（"新页 `source_mode=referenced`"）；§11.1 步骤 4:586 | `src/infrastructure/sqlite/library.py:299-302` `_COMPLETE_PAGE_WHERE = "source_hash IS NOT NULL AND managed_original_ref IS NOT NULL AND width/height IS NOT NULL"`，被 `existing_source_hashes:317-323`、`max_source_order:332-337`、`get_page:358-364`、`list_pages:367-371` 与 `core_service.py` 的 `handle_resolve_page_resource`（`page is None or not page.managed_original_ref → RegionLookupError`）共用；`schema.py:195-196` 列可空但读面当必要条件 | 引用模式新页无 managed copy ⇒ `managed_original_ref` 为 NULL ⇒ 对全部现有读路径不可见：书架页数、章节页列表、阅读器投影、页资源解析、导入去重、页序上限 → **用户导入后"书是空的"** | "直接引用"落地的第一道硬门槛；该谓词原本用于隐藏崩溃残留的半写行，改成 source-mode 感知后会同时**削弱崩溃安全不变量** | ① §8.1/§11.1 增写"页可见性/完整性谓词"迁移（新增显式完整性标记区分"崩溃半写"与"引用模式合法无副本"），列出 5 处读路径；② §12.3 增补反例断言（引用页在 list_pages / reader projection / resolve_page_resource 可见）；③ D05 把该谓词列为共享面变更 |
| **F-12** | P1 | §8.2:423（"每次 Host session 重新签发…`source-read` grant"）、:425；§8.4:454-456（`SourceReadLease`）；§4.3:211 | `src/bootstrap/core_service.py:1231-1232`（`OpenHostSession` 每进程仅一次，二次 `HOST_SESSION_ALREADY_OPENED`）；`src/infrastructure/resource_channel/import_source_refs.py:153-154`（TTL 硬上限 300s）、`:169-173`（目录成员必须直属）、`:192-203`（registry 只接受首个 session）、`:278-279`（`consumed=True` 一次性）；`HostIssuer.cs` `NextExpiry` 299s、`CollectImportEntries` 用非递归 `Directory.EnumerateFiles`；grant registry **纯内存**（进程重启即失效） | ①"每次 Host session 重签"当前不可实现（session 每进程一次、grant 绑死该 session）；② 300s TTL 与"整话翻译期间持续强校验、结果应用前重取 lease"根本冲突——每次重取都需 Host 参与提交边界；③ 目录 grant 仅单层直属，需求 `:69`"包含子文件夹"不成立 | 把"临时导入授权"复用为"长期源读取"的核心机制缺口；若按文字实现，FEA-09 后期必须重做 grant 协议（连带 Host/Core 冻结契约与 parity 快照）；`SourceAccessRegistry` 的"按 generation 跨重启核对"在内存 registry 上无法验证 | ① §8.2 明确 grant **种类**：新增 `source-read`（可续租/可撤销/按租约）与旧 `ImportPages`（一次性 ≤5min）并存且不可混用；② §8.4 定义 lease 续租/过期/撤销与 Core↔Host 往返；③ 明写递归授权根需要新模型；④ `SourceAccessRegistry` 明确要求**持久化**；⑤ D05 增列授权面契约变更与 parity 影响 |
| **F-13** | P1 | §9.2:486-497（把"默认软删 + 应用回收站 + 单项恢复"写成对现状的继承）；§14.2 第 8 行:778 | `src/bootstrap/core_service.py` 命令面只有 `PermanentlyDeleteBook`/`PermanentlyDeleteBooks`（`:298`、`:4403`）与 `ListRecycleBinBooks`（`:4559`），**无**软删/恢复命令（本轮已独立 grep 复核）；`LibraryService.delete_book` 仅被 legacy Qt `src/ui/viewmodels/bookshelf/viewmodel.py:294` 调用；`apps/.../LibraryViewModel.cs:97-98,106,795` 自述"删除/回收站：能力待接入"，恢复/永久删除是 `CanConfirm: false` 的空确认 | 方案按"复用既有回收站语义"排期 FEA-12 → 漏掉软删/恢复/`TrashEntry` 三组新命令与 V2 接线；而当前产品面**唯一可达删除是不可逆硬删** | 需求 `:82-87` 的核心安全承诺（默认软删、不删原件、可恢复）与当前能力相反，工作量与风险被低估；直接命中十项问题 8 | ① §9.2 增写"现状核对"（命令面无软删/恢复；`delete_book` 只在 legacy；V2 NOT_WIRED）；② FEA-12 交付清单显式列新增命令与 Host V2 接线，并把"硬删是当前唯一可达删除"列为现状风险；③ §14.2 第 8 行不得据 §9 文本判"覆盖完整" |
| **F-14** | P1 | §9.3:501（"默认包括：一致的业务 DB/设置…"）、:505、:511；§2 F16:58 | `nmbak.py:174-265` 只打包 `library.db` + sidecar + `managed/**`；`core_assembly.py:1506-1509` 的 `provider_profiles.json`/`network_profiles.json`/`provider_capability_bindings.json` 存 `data_root/settings/`；`core_service.py:5747` `catalog/catalog.sqlite`；`core_service.py:1967-1999` backup handler **不持** `_write_lock`（对比 `:1442` 永久删除持锁）；`nmbak.py:270-337` restore **先覆盖 DB 再恢复文件**（源码注释自认 "the DB is already overwritten"）；既有自动备份刷新/轮转（`core_service.py:5625-5700`，manual 包永不自动删）未被 F16 记载 | ① 用户按概念 `:91-94` 备份后换机：**服务配置/模型选择/词表引用所在 profile JSON 全部丢失**，包仍标 `verified=true`；② 备份与并发删除/导入交错 → 文件集合与 DB 快照来自不同时刻；③ restore 先毁后验，与需求 `:92-93`"不自动覆盖、失败保留原数据"相反 | 备份是"直接引用原件"后唯一还能自证完整的机制，当前包不覆盖全部应用内数据，而 §9.3 用"一致的业务 DB/设置"掩盖三处缺失 | ① §9.3 逐项列清"应用内数据"并标注现状覆盖（library.db ✅ / managed/** ✅ / settings/*.json ❌ / catalog.sqlite ⚠️ 需 D07 定口径）；② 明写 backup 必须取独占锁 + pin 文件集合；③ backup/2 必须**先 staging 校验再原子切换**；④ F16 补记既有自动备份刷新与"manual 不自动删"；⑤ D07 增列 profile/catalog 归属 |
| **F-15** | P1 | §8.2:429、§9.1:470、§9.2:495 | `src/infrastructure/filesystem/managed_storage.py:126-204`（`remove_managed` 全部守卫建立在"用户源文件永远在受管根之外"）；`src/application/maintenance/trash.py:11-17`、`cleanup.py:13-20` 明写该不变量；`library.py:518-523,768-786` 共享引用 preflight 比较的是 `managed_original_ref`；`core_service.py:3221`/`core_assembly.py:1025` `ManagedRootTrust` 是**单一受管根**的启动快照 | 引入引用源后 Core/Host 必须新增对根外路径的读（进而删除/回收）能力，该结构性不变量**退役**；而 `remove_managed`、`purge_batch`、`cleanup`、`preflight_permanent_delete` 四处守卫全按旧不变量设计。典型事故：某条旧清理/重试路径被喂进一个外部路径 | 方案描述了新流程，但**未把"既有结构性安全保证被移除"列为跨模块风险**，也没指定哪个模块今后唯一负责"永不触碰用户原件" | ① §8.2/§9.1 增"**不变量退役声明**"：根外路径的写/删权限收敛到唯一新模块（SourceAccessRegistry + Windows 回收站桥），其余删除/清理路径保持"只接受受管相对路径"并由类型区分；② 明写 `remove_managed` **不得**扩展为接受绝对路径；③ FEA-12 AC 增负例：旧清理/重试入口输入外部路径必须 typed 拒绝；④ `ManagedRootTrust` 需要"每授权根/每授权代"的等价快照 |
| **F-16** | P1 | §6.1:318（三层存储关系）、§6.2 表:322-332、§11.1 第 2 步:584 | 冻结 `V11R_AVALONIA_CONTRACT.md:135-142`（`LayoutProfile(Navigation,Shelf,Density,Workbench,Reader)`）、`:144-146`（`ThemeSettings`）；`ThemeModels.cs:326-346` 注释"V1 只实现 TopBand"；`ThemeService.SetLayoutAsync:258-274` 整包持久化 | 三层模型要表达"界面方案/视觉主题/比例方案"正交，但冻结 `LayoutProfile` 把 `Navigation/Shelf/Density/Workbench/Reader` 捆成一个持久化值：`Navigation` 与新"界面方案"重复，`Density` 与比例方案部分重叠，`Workbench/Reader` 属业务偏好（需求 `:124` 按书保存）→ 迁移器无法确定字段归属；Current 仍可通过 `SetLayoutAsync` 写整包与新比例方案冲突 | 产生"幽灵状态"；迁移规则不可判定；FEA-01 冻结新 Appearance API 时无旧 API 处置依据 | D02 增 **ThemeSettings/LayoutProfile 字段迁移矩阵**（保留 / 迁到 Core 按书偏好 / 迁到 scale schema / 废弃）+ 用户可见迁移规则；FEA-01 显式声明旧 API 的桥接或停用 |

### 2.3 P2 — 可并行修订

| ID | 级别 | 文档位置 | 证据与问题 | 建议修订 |
|---|---|---|---|---|
| **F-17** | P2 | §10.1 快照表:523-533；§2 F21:63 | 上下文页文本在执行时从 live 读（`handlers.py:1129-1159` `live.text.ocr_text`）；payload 只含 page_id/regions/context/glossary/hash（`ports/translation/protocol.py:93-121`）；无提示词文本/字体摘要字段。任务运行中编辑邻页 → 同一任务不同 step 带不同上下文，预览与实际发送跨时间不稳定 | F21 措辞升级为"已核实上下文内容不入快照、提示词/字体无字段"；§10.1 快照表补"上下文页内容或不可变 blob 引用"必须落库；FEA-10 AC 增"运行期改邻页 → 已接受任务 context 不变或显式 stale" |
| **F-18** | P2 | §12.2:664（"先建立 capability/需求追溯矩阵"）；§12.1 全表 | 追溯矩阵**无交付物**；FEA-02/04/05/06 的 AC 偏笼统（"四页和四页预览"不可判定）；候选表无验证等级/证据目录列；概念 `:151` 要求"DSH 在交互契约中冻结移动阈值/工具快捷键/可编辑状态"，§13.2 无对应项 | 追溯矩阵与交互契约作为 **FEA-01 交付物**（含"需求条目 → 能力 → Task → AC → 证据"四列）；候选表补"验证等级 + evidence_dir + 可观察 AC"列 |
| **F-19** | P2 | §4.2:186-199（`IFrontendInstance.MainContent` 单 `Control`）vs §4.3:221、§7.3:389-395 | 方案自相矛盾：单 Control 无法表达第二窗口；当前 V2 是单根（`AppShellV2.axaml.cs:98-126`），legacy 先例是两 Window 共享同一 VM（`MainWindow.axaml.cs:484-505`）。冻结后 FEA-07 只能绕过接口私建 Window，`WindowBroker` 的 capture/rollback 覆盖不到浮窗 | 接口改返回 `IReadOnlyList<FrontendWindowContent>`（`WindowRole`/`Control`/`memento`）；FEA-01 明确 `WindowBroker` 是唯一 Window 创建者 |
| **F-20** | P2 | §7.1:370（"首帧与必要控件检查成功"后才释放旧树） | Avalonia 11.3.22 无同步"首帧已绘制"观测；现有代码只有 `Loaded`/`SizeChanged`（`AppShellV2.axaml.cs:75,132-146`）。实现者会用 `Task.Delay`/`DispatcherPriority.Render` 猜首帧 → 慢机/4K 长页下判成功、释放旧树、用户看到空白且回退失效 | Commit 判定改为可观测组合（完整 layout pass + `Loaded` + 一次 Render 优先级回调 + 关键控件几何非零），写入 FEA-07 AC 与 A01/A08 |
| **F-21** | P2 | §7.1:346、§7.3:389-395、§6.2:326 | `AppShellV2.axaml.cs:105-124` 在创建时固定 `Width/Height/MinWidth`、`Window.Background`、`TransparencyLevelHint = WindowMaterial.ForCurrentOs()`；需求 `:212` 要求亚克力可开关。切换只换内容树 → 材质/MinWidth 不变；若为套材质重建窗口则违反"保留主原生窗口"并丢失位置/全屏 | Commit/Rollback 清单显式包含窗口级属性（材质/背景/MinWidth/Title），由 `WindowBroker` 独占修改 |
| **F-22** | P2 | §13.2 D03:734；§4.3:215 | `IHostController.cs`（423 行）实测 **47 个 `Task` 方法** + `IReaderProgressSink`(1) + `IRunController`(6) = 54 个方法需保持签名；冻结 `V11R_AVALONIA_CONTRACT.md:239` 写"已有 **36** 方法"。方案未重盘该口径（本轮已独立复核 47 个 Task 方法） | D03/FEA-01 用脚本或反射从接口生成清单作为冻结附件，并注明"36"是审计 §6 时点口径，不当作当前事实 |
| **F-23** | P2 | §2 F08:50（"现有 Undo 有恢复历史 revision 语义"） | 只对 legacy 成立：`Views/ReaderWorkbenchPages.cs:533-560,709`；V2 Studio **无** Undo/Ctrl+Z（`ViewModels/V2/**` 与 `Shell/V2/KeyMap.cs` grep 0 命中）；Region 契约 `:146-149` 所有 revision 写命令 append-only 非幂等 | F08 明确"Undo 仅 legacy；V2 无 Undo；legacy 的 Undo=revision 恢复 ≠ 草稿撤销"；FEA-03 分别为"草稿 patch history"与"revision restore"建 AC |
| **F-24** | P2 | §2 F10:52（"`Program.cs:82` 有 PerMonitorV2"） | `Program.cs:82` 是 `public static void EnablePerMonitorV2()` **定义，全仓唯一命中、无调用点**（本轮已 grep 复核）；实际生效的是 `App.manifest:6-7`（`dpiAware true/pm` + `dpiAwareness PerMonitorV2`）；V2 无 `Screens` 枚举/DPI 变更响应 | F10 引证改为 `app.manifest:6-7`；启动处显式调用或删除死代码；H2 增加"发布件 manifest 生效"校验项 |
| **F-25** | P2 | F 表引证精度：`:43`（`App.axaml.cs:31`、`AppOptions.cs:60`）、`:44`（`ShellState.cs:1`）、`:47`（`ThemeModels.cs:332`）、`:49`（`AppShellV2.axaml.cs:50`）、`:52`（`MainWindow.axaml.cs:315`） | 正确位置：`App.axaml.cs:56`（创建）、`AppOptions.cs:71`（`DefaultShellId="v2"`；`:60` 是 `StartupThemeId`，本轮复核）、`ShellState.cs:6/32`、`ThemeModels.cs:330`、`AppShellV2.axaml.cs:50` 是 Studio adapter、`MainWindow.axaml.cs:484-505`（创窗；`:315` 是 `LastImmersiveWindow` 判断）。**注**：本轮 55/55 引用的文件存在性与行号范围**全部通过**，此处仅为锚点不指向符号 | F 表统一为"文件:行(符号名)"；交付前用 `Select-String` 复核 |
| **F-26** | P2 | §2 F06:48、§4.3:210、§12.1 FEA-02:618 | 多路轮询实测：共享 `RunStatusMonitor` 1s（`RunStatusMonitor.cs:38,225,233`，Console 已接入 `ConsoleViewModel.cs:200-203`）+ Batch 视图级 750ms（`StudioBatchControls.cs:629-630` → `StudioBatchViewModel:698-707`）+ Export 700ms（`StudioToolsOverlay.cs:73-74`）+ Import 300ms（`ImportExportPanels.cs:669`）+ Page 按需（`StudioPageViewModel.cs:1281`） | FEA-02 只抽 `IRunDataSource` 不足以闭环 R-24；Plan 写明"轮询 owner = Presentation 层可注入时钟调度器，View 内 `DispatcherTimer` 必须移除"；A01 场景加请求次数断言 |
| **F-27** | P2 | §4.1:116（"新增纯界面通常无需修改后端"）、§4.3:221 vs §12.1 FEA-03:619、§7.1:366 | 无任何 draft/journal 实现；而 Fluent 首阶段依赖 FEA-03 的 Core draft journal 与 §7.1 的 journal ACK（Python 写域）。"纯界面不改后端"只在"第三个最小布局"验证成立 | 明确"切换不丢输入"的最低保证（内存共享缓冲 vs Core journal）与所属阶段；把 L116 的承诺限定为第三个最小布局，单列 FEA-03 的 Python 写域与数据安全影响 |
| **F-28** | P2 | §7.3:395（"不能由任意 UI 的 `Window.Closed` Dispose Host"） | 现状两种错误先例并存：legacy 确在 `Window.Closed` 同步 Dispose Host（`MainWindow.axaml.cs:166` `Closed += OnClosed`、`:842-843` flush 进度、`:852` `DisposeAsync().GetAwaiter().GetResult()`，本轮复核）；V2 路径**完全不 Dispose**（grep 仅 legacy 命中 `DisposeAsync`） | F01/F10 增"Host 所有权现状"；FEA-02 删除 `Window.Closed→Dispose` 路径并移交 ExitCoordinator；增"切换/关浮窗/正常退出后 sidecar 存活与清理"自动化测试 |
| **F-29** | P2 | §8.1:407-408（`source_versions` 含"扫描/解码器版本"） | PDF 页 hash 是**渲染 PNG** 的摘要（`documents/service.py:168-179`，`scale=2.0` 是"implementation default, not a frozen contract"）。解码器/scale/编码升级 → 同一未变源产生不同 digest → §8.3 状态机把全库引用页判 Dirty，一次应用更新后集体要求重新确认 | `source_versions` 拆为 **content identity**（容器 bytes digest + size/mtime 线索）与 **rendition observation**（decoder/scale/参数 + 输出 digest）；变化判定只对 content identity 触发 Dirty；§8.3 增"解码器升级不得触发用户确认"断言 |
| **F-30** | P2 | §8.1:409（`page_bindings`）、§9.3:509、§11.2:594（`DatabaseId`） | 全仓 `src/**` grep `DatabaseId`/`database_id` = **0 命中**；`schema.py` 只有通用 `metadata` 表。跨库恢复/合并必须区分"同库另一份备份"与"另一台机器的另一个库"，方案把 `DatabaseId` 当既有标识使用；旧库无法自动获得（且迁移 journal 需要它，形成鸡生蛋） | §8.1/§11.2 把 `DatabaseId` 标注为**新增**，规定生成/回填方式（首次写 `metadata` 生成 UUID，迁移 journal 第一笔即写）；旧库回填前按"身份未知"保守处理；D07 增列该原语 |
| **F-31** | P2 | §8.4:458-460、§8.3:446 | 目录 grant 只支持单层直属成员（`import_source_refs.py:169-173`；`HostIssuer.CollectImportEntries` 非递归），需求 `:69` 要求含子文件夹；**ZIP/CBZ 无任何解码路径**（`documents/service.py:93-101` 只接受 `%PDF-`，其余 `UNSUPPORTED_FORMAT`） | §8.4 明写"递归授权根 + 容器解码器（ZIP/CBZ）为新增能力，当前 0 实现"；FEA-08 能力矩阵按 5 种输入逐项列 NOT_IMPLEMENTED/需新增 |
| **F-32** | P2 | §9.1:478（"GC 使用引用图"）、:497（"共用 protection preflight"）、§2 F15:57 | 现状是**三套互不相同**机制：cache 清理靠前缀白名单且"never opens the database"（`cleanup.py:13-20,39-41`）；页级 `TrashService.purge_batch` 无任何保护检查（`trash.py:196-254`）；book 级硬删靠 6 项预检、无 pin/Lock 概念（`library.py:704-847`） | 三条既有删除/清理路径的保护现状矩阵，明确 ProtectionPolicy 为**新建**并替换/包住三者；草稿 journal 位置必须**不在** `cache/` 前缀下；D07 把"三路径统一"列为独立验收项 |
| **F-33** | P2 | §5.1 表:229-239、§5.2:247/265 | 全仓 `src/**` grep `draft`/`edit_token`/`edit_session` = **0**；无 draft 表/journal/编辑令牌。阅读进度虽真实持久（`schema.py:420-434` `reading_progress(UNIQUE(book_id,chapter_id,mode), last_page_id, scroll_offset_x/y, progress_percent…)`），但不足以承载 §5.1 的 `PageId + normalized position + viewport anchor` | 状态表增"现状"列或逐格标 [事实]/[建议]，把"Core draft journal""edit-session token"明确写为**新增**；说明阅读进度现状与目标锚点模型差距，作为 FEA-14-READ 输入 |
| **F-34** | P2 | §9.2:486（"书名占用在恢复提交事务中检查"）、§8.4:460 | `schema.py` `books(book_id, title, created_at, updated_at, deleted_at)` — **无 UNIQUE、无 title 规范化列**；全仓无同名校验；创建/改名/导入/恢复四条路径各写各的 | 明确"书名唯一"为**新增应用级不变量**（唯一索引或单点服务，含忽略大小写/去空格规范化列），列出五处调用路径 |
| **F-35** | P2 | §6.1:287（`componentContracts`）、§6.2:324-326 | 无对应实现/定义：V11R §3 只有控件样式 Classes 清单与自定义控件名单，没有版本化"组件契约"；兼容四态中的组件维度不可执行 | 把组件契约并入 FEA-01（key 集合/版本/必选/缺失 fallback）；或降级为"比例 slot ID 契约"并写清语义 |
| **F-36** | P2 | §6.1:311（`"reducedMotion": "system"`）、§6.2:325 | 冻结 `ThemeSettings.ReducedMotion` 是 `bool`（`ThemeModels.cs:349-355`）；需求 `:213` 要求动效"开启/关闭/跟随系统，**分别控制页面切换、浮层和悬停**" → 三态字符串与冻结 bool 不一致，分类动效在任何层都无字段 | 明确动效模型（全局开关 + 3 分类强度 + 跟随系统）与其持久化位置；列入 D02 与 FEA-05 AC |
| **F-37** | P2 | §6.2:328（比例键示例）；§12.1 FEA-05:621 | 需求 `:214` 要 8 类分项 + 整体缩放 + 多套方案保存 + 单项/全部恢复默认；方案示例只给 5 个键，缺顶部工具栏/列表行高/缩略图栏/浮层 4 类，且无"多套方案/恢复默认"模型 | §6.2 补 slot 清单与用户自定义方案持久化模型；FEA-05 AC 增"多套方案保存/单项与全部恢复默认/越界拒绝" |
| **F-38** | P2 | §12.1 FEA-09:625；§12.3 A10 | FEA-09 只有 4 条 AC（不复制原件/hash·mtime 不变/共享源独立/grant 不变），缺需求 `:68-70` 的格式矩阵、自然排序、重复名 occurrence、加密密码重试（不进日志）、逐项跳过原因、取消保留成功项、进度事件 | FEA-09 AC 补上述项或拆子 Task，否则可出现"能导入但不满足需求规则"仍通过验收 |
| **F-39** | P2 | §12.1/§12.2 全表 | 六组需求**无归属**：动效分类（`:213`、`:117`）、多套比例方案与整体缩放（`:214`）、工作台设置默认值（`:202`）、缓存位置迁移与容量（`:242-243`）、回收站保留期限与撤销入口（`:84`）、自动备份调度与保留数量（`:244`）、关于页许可/第三方许可（`:247`，且 AD-002 §5 列为发布 Gate 义务） | 在 FEA-14 内增子切片或指定归属（建议 FEA-14-SET 扩"界面与主题/动效/比例/工作台默认值/文件与存储/许可展示"；FEA-12 加保留期限与清理调度；FEA-13 加自动备份调度），每项至少一条 AC |
| **F-40** | P2 | §12.1 FEA-10:626 vs §12.2 FEA-14-AI:671 | 两个候选都声明拥有 request builder（FEA-10 "PreparedRun/request builder"、FEA-14-AI "各 provider 的 request builder"），无边界（canonical payload 归谁、provider 特化谁写） | 明确 canonical request builder 只在 FEA-10 冻结，FEA-14-AI 只交 provider 适配/能力清单 |
| **F-41** | P2 | §12.1:614-631、§12.3:700-710 | 候选表无验证等级列，AC 多为散文（FEA-02/04/05/06 部分不可判定）；`V11R_PROGRAM §3` 的 L1–L4 与契约 §7 的 `verification/<TASK-ID>/` 未接入 | 候选表增"验证等级 + evidence_dir + 可观察 AC"列 |
| **F-42** | P2 | §11.2 回退表:598-604、§12.1 | 回退只在**程序级**定义；FEA-03/09/10/12/13 无 per-task 中止/回滚/"旧端仍可读"AC | 每个高风险候选补"中止/回滚/旧端可读"AC 并引用 §11.2 |
| **F-43** | P2 | §6.1:316（"UI/主题/比例设置放 Host 提供的私有设置目录"） | 实际由 **App** 解析：`App.axaml.cs:104-113` `ThemeHome.Resolve(options)` → `ThemeStudioService.CreateProduction(settingsFilePath)`；`ThemeHome.cs:50-77` 纯 App 侧静态解析，Host 不参与 | 改为"由 App/Presentation 组合根用 `--theme-home` 解析并注入"，或把"Host 新增设置目录服务"标为 [建议] 并入 FEA-01 端口 |

### 2.4 已核验为真（避免只列问题）

- **F01–F22 事实表的代码定位总体可靠**：切片 A 逐条核对 F01–F10 得 **7 属实 / 3 部分属实 / 0 失实**；切片 B 核对 F11–F17、F22 得 **5 属实（F12/F13/F14/F17/F22）/ 2 部分属实（F11/F15/F16，且 F16 还有遗漏而非错误）**；切片 C 核对 F18–F21 得 **F18/F19 完全成立、F20 时序成立但定级错、F21 方向正确**。未发现系统性"把概念图/枚举当已实现"。
- **方案 55 处 markdown 引用 100% 通过**：55/55 文件存在且 `#L` 行号在文件范围内（DSH 全量脚本核验）。行号失准仅 5 处锚点不指向符号（F-25），不影响断言成立。
- **治理检查器可复现方案 §14.3 的结论**：`pwsh -NoProfile -File tools/governance/check.ps1` → `Governance check: PASS (2 warnings)`、`EXIT=0`、scope "13 current documents"。**但**该检查器不扫描 `doc/design/**`、也不能识别"保留哨兵 + 增补覆盖性决策"（见 F-01），**不能**作为架构一致性的证据。
- **方案对自身局限的登记是诚实的**：`:5` 声明不是 ADR/契约/Task；`:741` 声明作者不能自审；`:782` 声明自查不替代独立 Review；F06 关于 `IRunProjectionPoller` 的措辞准确区分了"缺少命名的实体"与"缺少能力"（实测源码 0 命中、`RunStatusMonitor` 已存在且 Console 已接入）。
- **方案已正确识别的既有缺口**（本轮复核成立）：Run 已持久化且有幂等（`pipeline.py:387-403,547-579`）；`IHostController` 确实在 App 内且很宽；主题机制可复用但"完整界面不是 ThemePackage"；`LayoutProfile` 只有 TopBand 实现；V2 Studio 默认源确为 NOT_WIRED；legacy Undo 实为 revision 恢复；V2 确无窗口注册表/跨屏恢复。

## 3. 十项架构问题结论

| # | 问题 | 结论 | 关键依据（finding） |
|---|---|---|---|
| 1 | 独立 UI 与共享 ApplicationCore/Host/Core 职责是否清楚、是否产生第二份业务真值 | **部分闭环**。分层职责表与状态权威表边界清楚，`ShellState` 已是选择/路由的单一源，Run 已由共享 monitor 承接，UI 无直连 CoreClient/SQLite；但外观持久化存在**双真值双写者**，Current VM 私有业务态迁移无清单 | F-06、F-09 |
| 2 | 接口/适配/复用是否有真实代码支持；新增纯界面是否通常无需改后端 | **部分闭环**。复用映射与真实文件一致，冻结契约的 append-only 非幂等描述准确；但兼容面口径失真（36 vs 54）、"纯界面不改后端"仅对第三个最小布局成立、引用页读面门槛未覆盖 | F-22、F-27、F-11、F-03 |
| 3 | 注册/预览/切换/失败回退是否闭环，是否重复启动任务或丢输入 | **部分闭环（方案设计最强项）**。六步事务、switch-journal、故障矩阵、"Loaded/构造禁 StartRun"结构完整，且现状确实无注册/切换（从零建，无假装已有）；但接口无法表达多窗口、Commit 首帧不可观测、切换未覆盖窗口级属性、VM 私有编辑态会在切换中丢失、配置落点不唯一 | F-19、F-20、F-21、F-09、F-06 |
| 4 | 草稿/撤销/阅读位置/任务状态是否独立于 View/ViewModel | **方向可接受、现状描述基本准确**。Run 与幂等已独立；阅读进度部分独立（按 book+chapter+mode，只有 y 偏移）；**草稿/编辑令牌/撤销栈全仓 0 实现**，FEA-03 应按"全新建子系统"排期而非"接线"；§5.1 表未标事实/建议易高估现状 | F-33、F-09、F-23 |
| 5 | 多窗口/双屏/混合 DPI/拔屏/重新停靠是否可实现 | **需求点覆盖完整、实现与验证均未成立**。§7.3 覆盖角色/位置/拔屏/redock/全屏保存；但现存代码零窗口管理（`WindowBroker/WindowId/Screens` 全 0），H2 只能真机验证（本环境 `BLOCKED`），且"只读镜像"规则与"画布+浮窗同时编辑"需求冲突 | F-10、F-19、F-21、F-24 |
| 6 | 界面/视觉主题/比例/组件兼容规则是否明确、是否与 V11R 冻结契约协调 | **不达标**。三层分离与 V11R §4 的 ThemePackage 边界同向，比例模型（DIP、单位/上下限/步长、不整体 RenderTransform）可实现；但 §2.2 硬规则、§2.3/§3 组件面、§4 持久化、§6.1/§6.3 结构与需求**直接矛盾**，修订请求必要却无条款级文本、三处口径不一；组件契约无定义；字段迁移矩阵缺失；动效分类无模型 | F-03、F-06、F-16、F-35、F-36、F-37 |
| 7 | 直接引用原文件的身份/授权/变化/共享/页匹配/删除/旧数据迁移是否安全 | **身份模型是本次方案最扎实的部分，但未闭环**。分层身份、watcher 仅 hint、digest 强校验、重复 occurrence、tombstone 不连带删除均正确；但授权不可续租/不可递归/无持久 registry、引用页对读路径不可见、删除面现状被高估、解码器版本污染身份、`DatabaseId` 不存在 | F-01、F-11、F-12、F-13、F-29、F-30、F-31 |
| 8 | Lock/人工/current·pinned/备份/回收站/清理保护是否完整 | **不完整**。双 Lock 投影被正确识别并交 DSH；但 current/pinned 的"已冻结"说法与 `M2-C1 §5.11.2` **相反**，备份包缺 settings/catalog 且无写锁、restore 先毁后验，回收站写面在产品面不存在，清理保护是三套异构机制被称"共用 preflight" | F-02、F-13、F-14、F-15、F-32、F-34 |
| 9 | 任务预览与配置快照是否同源；暂停/恢复/重试/结果应用能否防止覆盖后续修改 | **未闭环**。目标正确；现有暂停安全点与 `continue` 重验有真实代码基础；但无预览对象（只在 `create_run` freeze）、上下文 live 读/提示词/字体无快照字段、失败重试不复用原快照、**prepare 阶段已提前写 live 文本**使"防覆盖"在现有 Core 上不成立 | F-07、F-08、F-17 |
| 10 | 候选 Task 的依赖/写域/验收/回退是否足够具体、是否遗漏需求 | **可作 DSH 输入，不能直接作为 DAG 释放**。阶段划分与安全排序（尤其 Source 线 08→09→10→11→12→13）正确，FEA-08/10/11/12/13 的 AC 质量好；但 FEA-06 依赖不存在、写域与 V11R §1.2 冲突、FEA-02/04/05/06 的 AC 偏笼统、per-task 回退缺失、追溯矩阵无交付物、7 组需求无归属 | F-04、F-05、F-18、F-38、F-39、F-40、F-41、F-42 |

**总体判断**：方案的**架构方向可采纳**（独立 Avalonia UI 模块 + 共享 ApplicationCore/Presentation/Host/Python Core，不做第二份 Core、不做 `if (fluent)` 分支），**事实基础总体可靠**；但**"可实施"与"可验收"两项均不成立**，且存在 2 项 P0（架构决策权与冻结契约反向陈述）。

## 4. 需求覆盖结论

对照需求文档 §2–§7 全量条目（DSH 逐节映射 + 切片 C 的 R1–R11）：

| 需求面 | 覆盖结论 | 说明 |
|---|---|---|
| §2 书架（视图切换/搜索/多标签 AND/排序/滚动保留/视图样式单独记住/卷话番外同级/自定义顺序/书名规范化唯一/封面） | **大体覆盖、部分无归属** | FEA-14-LIB 建模名称/编号/顺序/规范化唯一约束、§5.1 明确"重启重置 + 视图样式单独持久化"；但多标签 AND、标签删除影响说明、组合筛选、右键菜单、详情浮层拖动、封面默认页码规则无 Task 归属（F-39） |
| §3 导入与原文件（格式矩阵/顺序/重复名/加密重试/引用提示/进度/取消保留/缺失重定位/外部变化预览/隐藏文件） | **规则方向覆盖、AC 覆盖不足** | §8.3/§8.4 对变化检测、匹配、重复 occurrence、tombstone、不自动套用人工修改写得具体；但 FEA-09 只有 4 条 AC，格式矩阵/加密/跳过原因/进度无验收（F-38），且 ZIP/CBZ 与递归目录 0 实现（F-31） |
| §4 删除/回收站/备份 | **语义覆盖、能力与契约冲突** | §9.2/§9.3 的流程（DeletePlan、逐项 journal、Windows 回收站、默认 defer、UseBackup 前保全）完整且保守；但与 `M2-C1 §5.11.2` 冲突（F-02）、产品面只有硬删（F-13）、备份不完整（F-14）、保留期限与撤销入口无归属（F-39） |
| §5 阅读器 | **部分覆盖、细节缺失** | FEA-14-READ 覆盖模式/方向/配对/缩放/锚点/书签/跨内容序列/总进度/搜索；但章节交界分隔线与名称提示、工具栏自动隐藏与等待时间、Esc 分层、翻页效果与动效强度、阅读设置即时预览与"恢复默认（当前书/全部）"、页码输入跳转、导航键语义**无承接**（F-39） |
| §6 工作台 | **覆盖最好的一面** | §10.2 的进度口径（已完成页数/实际总页数、不计等待失败跳过、锁定跳过标"已完成（含跳过区域）"、整批请求范围、非适用标 N/A、只在结果持久化后计数）与 §10.1 的配置快照六组、§9.1 的锁定样式白名单重渲染都很具体；缺：页面选择语义（Shift/Ctrl/筛选后全选/切换保留）、右键唯选语义、查找面板、工作台设置默认值（F-39） |
| §7 设置 | **机制覆盖、条目缺口较多** | §6.2/§6.3 覆盖主题/比例/预览/高对比/纯色回退；FEA-14-AI/FONT/SET/EXPORT 覆盖服务/提示词/词表/识别/字体/快捷键/诊断；缺：分类动效（F-36）、多套比例方案（F-37）、缓存位置与容量（F-39）、自动备份调度（F-39）、**关于页许可与第三方许可（AD-002 §5 的发布 Gate 义务）**、开机自启 |

**覆盖方法缺口（本身即 finding）**：方案 §12.2 自述"先建立 capability/需求追溯矩阵"，但 §12.1 无该交付物，导致上述"无归属"无法被机械发现（F-18）。

## 5. 处置建议

### 5.1 阻塞采纳的问题（处置前不得转契约/释放）

1. **F-01（P0）** 架构默认存储语义变更需**用户裁决**；`check.ps1` 不构成兜底。Source 线在裁决前 `blocked`。
2. **F-02（P0）** §9.1 与 `M2-C1 §5.11.2` 的相反语义需 DSH 裁定并区分"用户显式彻底删除"与"回收站到期 GC"。
3. **F-03、F-04、F-05（P1）** V11R 条款级修订单、Fluent 四页设计冻结前置、候选写域/组合根写权——三者是**冻结 FEA-01 与释放 S2 的前置**。
4. **F-06、F-09、F-10、F-07、F-08（P1）** 会写进契约与验收口径（唯一写者、必须迁出状态清单、draft owner 规则、prepare 不写 live、retry 快照），**先裁决再冻结**，否则 FEA-03/05/07/10 必然返工。

### 5.2 可后续验证的问题（不作为本轮结论，但必须进 Task）

- **H1**（双根 + 弹窗资源隔离、100 次切换无串染）、**H2**（真机 100/150/200% 混合 DPI、换主屏、拔副屏、redock）、**H3**（热切换 p50/p95、内存峰值、输入冻结）——本环境**无法验证**（见 §6.3）。
- **H4/H4b**（稳定 lease 与授权续租）、**H5**（Windows 回收站负向原型）、**H6**（PDF 重生成/ZIP 重编码/GIF/密码格式的精确页匹配）、**H7**（F20 写入时序的运行时 RED 复现）。
- F-20 首帧判定、F-21 窗口级属性、F-24 发布件 manifest 生效性、F-26 轮询请求次数、F-29 解码器升级行为——都应在对应 Task AC 中以**可执行断言**落地。

### 5.3 需要用户裁决的产品取舍

| # | 取舍 | 现状/冲突 | 建议默认 |
|---|---|---|---|
| U-01 | 是否把 AD-002 的架构哨兵与"默认不复制原件"改为 ReferencedSource（F-01） | AD-002 `Decision authority: User`；`AGENTS.md:43` 只允许落在 Managed Copy 架构 | 需用户明确裁决（ADR）；未裁决前保持 Managed Copy 默认 |
| U-02 | 用户"彻底删除"是否解除 Lock/current/pinned（F-02） | 冻结 `M2-C1 §5.11.2` = 移除；方案 = 拒绝 | 建议区分：用户显式彻底删除可解除（沿用冻结语义），仅回收站到期 GC 阻受保护项 |
| U-03 | 首阶段浮窗是否允许与主窗同时编辑同一区域（F-10） | 方案 §5.2 只读镜像；需求 `:143`/`:148-150` 暗示可编辑 | 建议按 `(SessionId, RegionId)` draft owner + 分字段并发；若不接受，则明确降级为只读并写入需求 |
| U-04 | Fluent 是否豁免 V11R §2.2 的圆角/阴影/模糊禁令（F-03） | V11R 硬规则 + R-14 唯一例外清单；需求要求亚克力/层次 | 需 DSH 起草 per-scheme 例外登记（与 R-14 同构）并经用户确认，不得事实上豁免全部令牌纪律 |
| U-05 | 阅读器翻页效果/动效分类是否纳入首阶段（F-36、F-39） | 需求 `:117`/`:213` 要求；方案无归属 | 建议纳入，但明确"首阶段可降级为跟随系统 + 单一强度" |
| U-06 | 引用原件后是否承诺完全离线阅读/重建（需求 `:74`） | 方案 §13.1 已列，默认仅引用 + 有限缓存 | 保持方案默认；若要求离线，需另定存储与空间预算 |
| U-07 | 外部卷支持范围（网络盘/可移动盘/云占位） | 方案 §13.1 已列 | 先验证本地 NTFS；不可证一致读取的卷显式受限 |
| U-08 | 凭据与字体备份范围（需求 `:245`） | 方案 §13.1 已列，默认不备份密钥 | 保持默认；恢复时要求重新授权 |

### 5.4 DSH 契约变更清单（修订方案 §13.2 D01–D08 并新增）

| # | 变更包 | 涉及权威/共享面 | 必须冻结的内容 | 关联 finding |
|---|---|---|---|---|
| C-01 | 架构默认存储语义 | AD-002（含哨兵与 `:23` 责任表）、`AGENTS.md:43`、`check.ps1` 哨兵口径 | Managed Copy 默认 → ReferencedSource 默认的**用户 ADR**；旧 Managed 双读；下游五项反转清单；哨兵常量与 AD-002 文本的同步处置方式 | F-01 |
| C-02 | V11R 契约条款级修订单 | `V11R_AVALONIA_CONTRACT.md` §1.1/§1.2/§2.2/§2.3/§2.4/§3/§4/§6.1/§6.3 | 逐条"现行文本 → 修订文本/适用域 → 审查判据 → 例外登记"；重申 R-03；`nm.fluent.visual/1` 的定位与校验器归属 | F-03、F-35、F-36 |
| C-03 | 外观持久化与字段迁移 | `ThemeSettings`/`LayoutProfile`/`IThemeService`/`IThemePersistence`，新 `presentation-settings.json` | 唯一写者；旧文件停止写的时点；字段迁移矩阵（保留/迁 Core 按书偏好/迁 scale schema/废弃）；动效三态与分类模型 | F-06、F-16、F-36 |
| C-04 | 彻底删除语义 | `M2-C1 §5.11.2`、Region 契约 pin 语义、相关测试 | 三层保护区分（GC / 软删 / 用户显式彻底删除）；`M2-C1` 是否需要修订及其测试影响面 | F-02 |
| C-05 | 页可见性/完整性谓词 | `src/infrastructure/sqlite/library.py` 读面、`core_service` 页解析 | 新增显式完整性标记；5 处读路径改造；不削弱"崩溃半写"防护 | F-11 |
| C-06 | Source 授权面 | 导入/资源控制面、Host issuer、新 `SourceReadService`、`SourceAccessRegistry` | grant 种类（一次性导入 / 可续租 source-read）、续租/撤销/过期、递归授权根、持久化 registry generation、读取预算 | F-12、F-15、F-31 |
| C-07 | 应用端口与兼容面 | `IHostController`/`IRunController`/CoreClient/Registry/Dispatcher/命令清册 | 由代码生成的方法清单（替换"36"口径）、request-scoped error、能力握手、增量为准、旧签名不变的可验证基线 | F-22、F-25 |
| C-08 | Run 快照与幂等 | `IRunController`、PreparedRun、配置快照、凭据引用、任务投影 | preview 与发送同源、不可变内容 pin、retry 是否复用 source run 快照、控制 pending 状态、真实完成口径、断线 receipt | F-07、F-08、F-17、F-26 |
| C-09 | 删除/备份/迁移 | Trash/purge/GC、`nmbak`/`migrator`、Windows 回收站桥 | 软删/恢复/TrashEntry 新命令面、三路径统一 ProtectionPolicy、备份覆盖清单（settings/catalog）、`backup/2`、`DatabaseId`、自动备份调度归属、独占写锁与 pin | F-13、F-14、F-30、F-32 |
| C-10 | 交互契约与需求追溯 | 新交付物（FEA-01 附件） | 手势优先级与移动阈值、快捷键作用域、可编辑态、draft owner 规则；"需求→能力→Task→AC→证据"矩阵 | F-10、F-18、F-39 |
| C-11 | 候选 Task 表补列与前置 Gate | 方案 §12 | 每行补 `write_scopes`/`shared-file owner`/验证等级/`evidence_dir`/per-task 回退/需求映射；把 H1/H2/H3/H4b 写成候选的前置 Gate；补 Fluent 设计冻结前置 Task | F-04、F-05、F-41、F-42 |
| C-12 | 治理检查器定位 | `tools/governance/check.ps1` | 明确它**不检测**"保留哨兵 + 覆盖性决策"，也不扫描 `doc/design/**`；是否扩展属独立裁决（受协作协议 §4.4 核验前置约束） | F-01 |

## 6. 验证

### 6.1 已执行检查（全部只读；均为静态核查，不代表运行通过）

| # | 检查 | 命令/方式 | 结果 |
|---|---|---|---|
| 1 | 方案指纹（审查前后各一次） | `Get-FileHash -Algorithm SHA256` | `bc30996…5ac85f`，与冻结值一致（两次一致） |
| 2 | 需求指纹 | 同上 | `508273c4…1979808`，与方案引用一致 |
| 3 | 分支/HEAD/common dir/工作区 | `git rev-parse --abbrev-ref HEAD`、`rev-parse HEAD`、`--git-common-dir`、`status --porcelain`、`worktree list` | `main` / `1180cdba…` / `.git` / 9 modified + 2 untracked / 未新增或删除任何 worktree |
| 4 | 方案内 55 处文件引用全量校验 | DSH 脚本：正则抽取 `](path#Lx)` → 存在性 + 行号范围 | **55/55 通过**（存在且在范围内）；另人工核对 5 处锚点不指向符号（F-25） |
| 5 | 治理检查器（只读运行 + 读实现） | `pwsh -NoProfile -File tools/governance/check.ps1` | `PASS (2 warnings)` / `EXIT=0` / "13 current documents"；并确认 `:259-262` 只校验 AD-002 含哨兵字面量、`$truthPaths`/`$staticFiles` 不含 `doc/design/**` |
| 6 | 关键行号抽检（DSH 亲自复核） | 直接读取被引行 | `Program.cs:82`=`EnablePerMonitorV2()` 定义且为全仓唯一命中；`app.manifest:6-7`=PerMonitorV2 实际声明；`MainWindow.axaml.cs:166/852`=`Closed += OnClosed` / `DisposeAsync().GetAwaiter().GetResult()`；`AppOptions.cs:60`=`StartupThemeId`、`:71`=`DefaultShellId="v2"`；`library.py:299-302`=`_COMPLETE_PAGE_WHERE` 含 `managed_original_ref IS NOT NULL`；`step_writes.py:207-281` 独立事务内 `UPDATE regions SET text_json` 后 `commit()`；`M2-C1:735`="移除项目 Lock/current/pinned Revision"；`IHostController.cs` 47 个 `Task` 方法 |
| 7 | 命令面核对 | grep `src/bootstrap/core_service.py` | 仅 `PermanentlyDeleteBook`/`PermanentlyDeleteBooks` + `ListRecycleBinBooks`；无软删/恢复命令 |
| 8 | 符号存在性反证 | grep `IRunProjectionPoller`/`WindowBroker`/`FrontendRegistry`/`Screens.`/`Undo`（V2）/`draft`/`edit_token` | 分别 0 命中或仅文档文字/仅 legacy，支持 F-06、F-11、F-24、F-26、F-33 |
| 9 | 冻结契约交叉核对 | 读 `V11R_AVALONIA_CONTRACT.md`、`V11R_REGION_WRITE_CONTRACT.md`、`M2-C1_TYPED_IPC_CONTRACT.md`、`V11R_PROGRAM.md §5/§8` | 形成 §2.1 F-02、§2.2 F-03、§2.3 F-33 等结论 |
| 10 | 独立 Reviewer 分片产出 | 3 名 Reviewer 各出 1 份报告（42.8KB / 53.8KB / 46.6KB） | 三份均自复核冻结 hash、HEAD 与只读纪律；DSH 对 P0/P1 的**关键代码证据逐条复跑**（第 6–8 行） |

### 6.2 NOT_RUN（不得写成 PASS）

- `dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror`、`dotnet test … --no-build`、`python -m pytest -q`：本轮为方案只读审查，未运行构建/测试。
- `tools/run_translate_probe.py`、安装 smoke、打包与发布件 manifest 生效性：未运行。
- F20 的**运行时 RED 复现**：本轮给出的是静态代码与时序证明（独立事务先提交），未运行复现；如需运行级证据须另派受控执行型任务。
- 主题切换实测、Run 暂停/恢复真机、源文件 lease、Windows 回收站、备份/恢复、孤儿进程检查：需运行应用与受控数据，超出只读边界。
- H1/H3/H4/H4b/H5/H6/H7 原型：需新建工程或写入数据，未执行。
- Mermaid 渲染：未运行渲染器（仅文本结构阅读）。
- `verification/**` 历史证据：按 `AGENTS.md` 只读当前 Task 引用，未做全量扫描。

### 6.3 BLOCKED

- **H2（混合 DPI 双屏真机）与 H3（热切换性能）**：本会话无桌面显示环境，无法验证；因此"多窗口/双屏可实现性"只给设计层结论（§3 第 5 项），**不给可行性实测结论**。
- **"当前行为未退化"类结论**：未运行测试，只能引用测试存在性与静态代码。
- **ZCode 独立批准**：`reviewer_unavailable`（CLI 未部署）。本报告的 `changes_requested` 不受影响，但若后续需要**批准**，必须另行 Appointment。

### 6.4 本轮未改动

方案、生产代码、需求文档、现有 Task、`STATUS`、`REBASELINE_PLAN`、`V11R_PROGRAM`、冻结契约与历史证据**均未修改**；未创建/释放 Task，未运行迁移，未清理数据/worktree/分支，未 push。唯一写入本报告；三份切片报告位于 `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/`（按工作区规则存放）。`doc/00_INDEX.md` 未登记本报告（超出本轮写权；见 §7 待办）。

## 7. 结论与复审

**结论**：`changes_requested`。方案**方向可采纳**、**事实基础总体可靠**（F 表无失实，55/55 引用通过），但**当前版本不可转为架构/契约变更，也不可释放任何候选实现 Task**。理由：2 项 P0（架构决策权归属错误、对冻结契约的反向陈述）与 14 项 P1 中有 6 项会直接写进契约与验收口径。

**转入下一轮的准入条件（r2 复审基准）**：

1. F-01 已由用户裁决（或明确标注为 `blocked_pending_user`）并在方案中如实改写；D01 拆分为"用户 ADR"与"契约/数据安全"两包。
2. F-02 已裁定并写清三层保护与 `M2-C1 §5.11.2` 的处置（修订或保留）。
3. F-03 已产出**条款级** V11R 修订单（含 §1.1/§1.2/§2.2/§2.4/§3/§4/§6.1/§6.3），并与 F-06/F-16 的字段迁移矩阵合并。
4. F-04 已补 Fluent 四页设计冻结前置 Task；F-05 候选表已补 `write_scopes` 与组合根写权。
5. F-07/F-08/F-09/F-10 已给出明确裁决或可执行 AC 草案。
6. §12 候选表补"验证等级 + evidence_dir + per-task 回退 + 需求映射"，并附需求追溯矩阵。
7. 修订后的方案重新固定 SHA-256；复审对**新 hash + 同一 HEAD** 进行，旧结论不自动适用。

**复审不覆盖**：修订后的方案若同时改动生产代码或契约，需另行 Appointment（本报告的代码事实只对 `main@1180cdba` 有效）。

**待 DSH 后续动作（不在本轮写权内）**：`doc/00_INDEX.md` 登记本报告；`doc/STATUS.md`/Task 指针是否引用本报告；是否把 FEA-00 正式立项为 Task（若立项，须先冻结 Owner/Reviewer/base/allowed_paths）。

---

**附：finding 溯源映射（供 DSH 与作者对账）**

| 本报告 | 来源 |
|---|---|
| F-01 | B-01 + DSH（`AD-002:5` 决策权、`check.ps1:259-262`、`AGENTS.md:43` 交叉核验） |
| F-02 | B-02 + DSH（`M2-C1:735` 原文复核） |
| F-03 | C04 + A11 + DSH（`V11R` 条款号逐一比对） |
| F-04 | C05 |
| F-05 | C06 |
| F-06 | A01 + C02 |
| F-07 | C01 + DSH（`step_writes.py:207-281` 复核） |
| F-08 | C07 |
| F-09 | A03 |
| F-10 | A02 |
| F-11 | B-03 + DSH（`_COMPLETE_PAGE_WHERE` 复核） |
| F-12 | B-04 + B-15 |
| F-13 | B-05 + DSH（命令面 grep 复核） |
| F-14 | B-06 + B-13 |
| F-15 | B-07 |
| F-16 | C03 |
| F-17 | C08 |
| F-18 | C16 + DSH（追溯矩阵/交互契约缺口） |
| F-19 | A04 |
| F-20 | A05 |
| F-21 | A06 |
| F-22 | A07 + DSH（47 个 `Task` 方法复核） |
| F-23 | A08 |
| F-24 | A09 + DSH（`EnablePerMonitorV2` 唯一命中复核） |
| F-25 | A10 + DSH（55/55 校验 + 5 处锚点核对） |
| F-26 | A12 |
| F-27 | A13 |
| F-28 | A14 + DSH（`MainWindow.axaml.cs:166/852` 复核） |
| F-29 | B-08 |
| F-30 | B-09 |
| F-31 | B-10 |
| F-32 | B-11 |
| F-33 | B-12 |
| F-34 | B-14 |
| F-35 | C10 |
| F-36 | C11 |
| F-37 | C12 |
| F-38 | C13 |
| F-39 | C14 + DSH 需求覆盖矩阵 |
| F-40 | C15 |
| F-41 | C16 |
| F-42 | C17 |
| F-43 | C09 |
