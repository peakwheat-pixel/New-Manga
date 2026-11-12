# AUDIT-14：历史技术债务与 V1 完整性（静态阶段）

状态：`PARTIAL`。本阶段只做了固定 HEAD 上的静态文档、组合根和显式能力标记核对；没有运行 GUI、构建、测试、迁移、真实模型或真实用户数据。阶段结果不能代表全审通过。

## 1. 范围、方法与限制

- 项目产品基线：`10e4ee013835605800d3830fb960ae8d3aa04167`；本次静态检查生成于 `main` 的 `a9924499fc5271fb1f917ea031d701c419003dcc`。`git diff --quiet 10e4ee013835605800d3830fb960ae8d3aa04167 HEAD -- src apps tests` 实测无输出、EXIT 0（产品路径没有相对审计基线的 tracked diff）。
- 按文档真相地图、当前 STATUS / DAG、AD-002 / AD-003、README、V11R 历史验收快照，以及 Avalonia app composition root 和明确 `NOT_WIRED` 代码做定点核对。完整命令、生成 HEAD、时间、每条 EXIT 和搜索输出在 `logs/audit14-static-20261112T192852Z.log` 与 `evidence/audit14-static-20261112T192852Z.json`；可用 `python audit/V1-FULL-AUDIT/scripts/audit14_static_inventory.py` 重跑同一有界清单。
- 不以目标架构、`doc/01_FUNCTIONAL_ARCHITECTURE.md` 等 REQUIREMENT REFERENCE，或旧程序计划中的每个项目，自动推导为 V1 发布承诺；它们的权威分类见 `doc/00_INDEX.md:46`。未完成的项仅列候选观察，不自行定级为正式产品缺陷。
- AC2 原要求为 15 项均须有结果或具名阻断。本阶段是静态分类，不覆盖真实运行验收。特别是切换各 shell 的实际路由、四页功能完整性、真实模型/GUI、安装包及真实源文件生命周期均未在本阶段执行。

## 2. 承诺范围与可计数边界

仓库没有一份权威、版本化且逐项标注“V1 承诺 / V1 完成 / 后续规划”的功能总账，因而**不能可靠给出 V1 承诺总数或未来规划总数**。本次只可计数所查来源明确写出的条目：README 有 5 个功能域标题（Bookshelf、Workbench、Reader、Settings、Export）及 4 个一级页面；这些是当前产品说明，不等同于经过逐项签署的 V1 验收清单。AD-002 的 57-command 迁移说明和已完成的 S0–S5 属于架构/迁移范围，也不应再统计成尚待实施的未来规划。

建议后续以独立、经授权的需求/文档 Task 建立 V1 功能承诺台账，并将“已承诺但未完成”和“明确延期到后续版本”分栏。该建议不扩展本审计 Task 的允许修改范围。

## 3. 功能实现分类（仅静态证据）

| 范围 | 静态分类 | 观察与证据 | V1 判定限制 |
|---|---|---|---|
| 传统 Avalonia `MainWindow` 的四页与 Host 接线 | `STATIC_WIRED` | composition root 创建真实 `HostController`（`apps/desktop-avalonia/src/NewManga.App/App.axaml.cs:93`）。`MainWindow` 将 Bookshelf、Workbench、Reader、Settings 分别放入导航页集合（`Views/MainWindow.axaml.cs:94-117`），页面切换会触发 Workbench 加载、Settings 凭据/网络档案刷新；Reader 有加载和进度保存入口（同文件 `210-246`）。 | 只证明静态可达与注入真实 Host；不能证明运行成功、所有按钮可用或符合 V1 验收。该壳是可选回退路径之一。 |
| V2 Studio 的批量 Run、区域文本/锁定状态、成品页 Final/Split | `PARTIAL / UI_PRESENT_NOT_WIRED` | 可运行的 V2 shell 注册 Studio view（`Shell/V2/AppShellV2.axaml.cs:53-58`），构造时只传 Host、selection 和 `onRunTracked`，未传 `runSource/textSource/flagSource`；`StudioPageViewModel` 默认采用三个 `NotWired` source（`ViewModels/V2/Studio/StudioPageViewModel.cs:270-282`），`BuildNotWiredInventory()` 明确列出 Run 投影、四级文本读取、锁/失败角标及 Final/Split 页资源均 `NOT_WIRED`（`1808-1835`）。同一 Studio 中 Terms view model 默认为 `NotWiredTermsSource`（`StudioWorkspaceViewModel.cs:28-33`；`StudioTermsViewModel.cs:45-47,79-82`）。 | 这是已证实的静态能力缺口，但是否属于 V1 承诺未找到可逐项对应的权威台账；真实 GUI 表现未执行，作为待 ZCode 定级的候选。 |
| Source / Host 授权与回收站层 | `IMPLEMENTATION_PRESENT; END-TO-END NOT_RUN` | AD-003 §4 写“当前均无实现”（`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:118-119`）；当前树已有 `SourceAccessRegistry`、`HostOperationOrchestrator`（`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs:17`、`HostOperationOrchestrator.cs:15`），`HostController` 也含 `MoveToTrashAsync`、`RestoreFromTrashAsync`（`Services/HostController.cs:3373-3383`）。 | 类/方法存在不等于整条 UI、授权、Core、DB 路径端到端完成。AD-003 是决策日快照；须按当前实现逐条更新状态，不能把此差异反推成系统全量完成或缺陷。 |
| 导出、主题与配置说明 | `DOCUMENTED; PARTLY STATICALLY WIRED` | README 宣称 ZIP/PDF 导出、主题、网络档案和凭据；传统 Reader 将 controller / file picker 注入导出入口（`Views/MainWindow.axaml.cs:109-110`）。 | 本阶段没有执行导出，也没有逐个核实 PDF searchable layer、打包模型或凭据存取行为。README 声明不等于运行验收。 |
| Mock / fixture-only 主功能 | `NO MOCK-ONLY CORE FLOW ESTABLISHED` | 生产 composition root 使用 `HostController`；现有代码另有 `NullHostController` 与 reader fixtures 作为预览/回退支持。 | 未全量审阅所有 test double 和其调用方；不能以本结果声称全仓不存在仅由 Mock 支持的页面/操作。 |
| 真实 GUI、安装包、真实漫画/模型与源文件变化 | `NOT_RUN` | 本阶段没有实际启动应用、执行安装/升级、加载真实权重、调用真实 provider 或访问用户作品。 | 不能用静态检查或历史 V11R 截图/验收替代当前版本运行结论。 |

## 4. 历史代码、文档和维护债务

1. **历史前端仍在仓库，且有当前工具引用旧路径。** `apps/desktop/src-tauri`、`apps/desktop/frontend` 和 `src/ui`（PySide/QML）仍可枚举到；AGENTS 与 AD-002 将 Tauri/React/PySide 定义为历史。`.github/workflows/build-release.yml` 当前会调用 Avalonia installer（约 112 行），而 `apps/desktop-avalonia/scripts/build-installer.ps1` 在未提供 `-IconPath` 时回退到 `apps/desktop/src-tauri/icons/icon.ico`（约 55 行）；另有 `prepare-sidecar.ps1` 默认从旧 Tauri `target/release/resources` 取 sidecar。旧工具/资产尚未完全隔离。CI 因文件存在而可工作，但这会让新架构的发布脚本依赖旧架构路径；本阶段没有执行 clean release 来确认失败/影响。
2. **README 与当前决策/发布说明漂移。** README `:21` 将新导入描述为 managed copy，与 AD-003 当前默认 ReferencedSource 不一致；README 自述 `0.1.1`，其构建、校验和安装示例仍命名 `0.1.0`（`:11,80-120`）。这是文档/版本入口一致性问题，未验证实际发布资产。
3. **文档导航自相矛盾。** `doc/00_INDEX.md:87` 写根目录没有 README，但 `README.md` 实际存在。V11R 程序文件仍标 `ACTIVE`（`doc/V11R_PROGRAM.md:3`），而 STATUS 和 00_INDEX 均记录 V11R 已收官并发布 v0.1.1。历史计划可保留，但状态应明确标记为历史快照。
4. **AD-003 的“未实现”列表过期。** `SourceAccessRegistry`、Host 操作协调和 trash Host 方法在当前树可见，但 AD-003 §4 仍以“当前均无实现 / NOT_WIRED”陈述。只将可直接反证的条目列为文档漂移；其他 Source、删除、恢复入口仍需按 UI → Host → Core → DB 分层逐项复核。
5. **多 shell 增加验证面。** App composition 支持 `MainWindow` 回退、V2 shell，以及由 frontend selection 进入 Fluent shell 的分支（`App.axaml.cs:131-176`）。静态上它们复用部分 Host，但页面结构和可用能力并不完全相同；双 UI 的差异是否符合发布策略属于架构风险，需由独立审查和真实 GUI 回归判断，不在此宣称已经造成用户缺陷。

## 5. 候选观察（待 ZCode 独立定级）

下列均为审计作者提交的候选，不是已定 severity 的正式 findings，也不授权修复：

- `AUDIT-14-CAND-001`：V1/未来功能没有统一承诺总账，README、当前架构决策与历史计划状态存在可证实漂移；影响是无法可靠统计完成率并可能误把规划项当缺陷。
- `AUDIT-14-CAND-002`：V2 Studio 页面有显式 `NOT_WIRED` 批量 Run、区域文本/状态和 Final/Split 能力；需确认它们是否在当前承诺内以及现有可见状态是否足够。
- `AUDIT-14-CAND-003`：Avalonia release helper 仍从旧 Tauri 路径取图标/sidecar；当前 CI 是否受该路径脆弱性影响需由 clean build/release 证据确认。
- `AUDIT-14-CAND-004`：多 shell 路由和功能面差异扩大后续 V2 的回归矩阵；当前运行风险未实测。

Issue ledger 状态保持 `REVIEW_PENDING`，没有自行赋予 P0–P3。现有 AUDIT-01/08/11 等已复核问题仍分别以其原始证据和状态为准，本报告不重定级或重复登记。

## 6. 结论与后续范围

AUDIT-14 已完成一轮定点静态核对，能证明四页旧壳存在真实 Host 接线，也能证明 V2 Studio 有明确未接线能力；同时发现若干历史代码路径和文档快照漂移。由于 V1/未来承诺没有统一的权威逐项清单，且没有运行当前 GUI/安装包，本专项维持 `PARTIAL`，不统计 V1 完成百分比、不把未来规划全部写成 V1 缺陷。

后续需要：ZCode 对候选观察作独立定级；按剩余 DAG 继续 AUDIT-03/04/07/09/10/12/13；全审正式报告、完整问题去重、交付 HEAD 门禁及 Release Gate 仍未完成。产品代码、发布脚本、README、AD-003 和索引均未在本 Task 中修改。
