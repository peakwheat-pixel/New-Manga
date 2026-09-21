# 接管审计、当前状态与 Gap Analysis

> **历史快照声明（2026-09-21）**：本文档记录 2026-09-13 的初始接管状态，不是当前实现基线。当前代码、Gap、任务审计和路线以 [REBASELINE_PLAN](REBASELINE_PLAN.md)、[STATUS](STATUS.md) 与 [Rebaseline Verification](14_TAKEOVER_VERIFICATION.md) 为准。

审计日期：2026-09-13，Asia/Shanghai。范围仅为 G:/CODEX/New Manga 及其 Git 元数据。D01～D08 的定义与实际文件路径见 [索引](00_INDEX.md)。本报告是本次接管快照，持续状态见 [STATUS](STATUS.md)。

§1～8 保留接管时观察，行号和原始指纹对应初始基线 `496b4ed`；TASK-001 后续修订见 §9，TASK-002 契约冻结见 §10。历史“未提交/未授权”描述不代表当前状态。

## 1. 结论

这是一个已初始化 Git、持有完整目标文档组、尚无应用源码的项目。不能把它描述为已存在的漫画软件重构工程；D01 中的“现有能力”来自未随本仓库提供的旧代码引用，当前无法核验。

现有 8 份 Markdown 共 297,016 字节、17,715 行，全部逐份检查。未发现独立产品 PRD、项目规则文件、源代码、测试、SQL、依赖清单、构建配置、CI、设计图片或 Figma 导出；功能需求、数据模型和 UI 规则分别存在于这 8 份目标文档中。未检索其他项目、私有聊天或外部旧仓库来补造事实。

“从真实代码生成运行架构/ER/UI映射”目前没有输入，状态为 BLOCKED_NO_SOURCE。已提供一张仓库现状图，以及 11 类有出处、明确标为 To-Be 的目标视图；这些不是代码逆向成果。源码到位后需按真实 source/test/commit 更新。

## 2. 仓库与 Git 检查证据

| 检查 | 2026-09-13 观察 | 意义 |
|---|---|---|
| Get-ChildItem -Force；rg --files --hidden --no-ignore -g '!.git' | 接管前仅 .git 与 doc；doc 下 8 个文件 | 包括隐藏/被忽略文件的检查；无应用实现 |
| AGENTS 检查 | G:/AGENTS.md、G:/CODEX/AGENTS.md、项目及 doc/AGENTS.md 均无 | 本次新增共同入口 |
| git rev-parse --show-toplevel | G:/CODEX/New Manga | 唯一项目根 |
| git status --short --branch | No commits yet on master；8 份文档未跟踪 | 没有版本化项目基线 |
| git rev-parse --verify HEAD；git log | 无有效 HEAD；分支无提交 | 无可审查的项目提交历史 |
| git ls-files；git branch -a；git remote -v | 均无条目 | 无跟踪文件、已创建分支 ref 或 remote |
| git worktree list --porcelain | 仅主工作区；HEAD 全零；refs/heads/master | 没有协作 worktree |
| git reflog show --all；git log --all | 无提交历史输出 | 未发现其他项目开发历史 |
| git show-ref；git cat-file -t | Codex 会话生成的 refs/codex/turn-diffs/.../base 指向 tree | 工具工作区快照，不是项目 commit 或历史里程碑 |
| git ls-tree -r 该 tree | 同样只有这 8 份文档 | 内部快照未包含遗漏源码 |
| 路径检查 | src、tests、test、pyproject.toml、requirements.txt、package.json、.github、README.md、.gitignore 不存在 | 无入口、测试命令、锁定依赖或发布包可验证 |

git diff 没有输出不能解释成“仓库无修改”：当前所有项目文件均未跟踪。Codex 内部快照 ref 可能随会话变化；不把它登记为项目基线。

## 3. 原始文档指纹

原始 01～08 本次保留原字节内容。这组 SHA256 用于后续确认审计对象，而非替代 Git commit。

| 文档 | 行数 | SHA256 |
|---|---:|---|
| D01 | 255 | 5a1af01c966702bc8c7b7da7ab81bb62922444944097362334481d99d060cb78 |
| D02 | 1078 | 499634aecf3e3cdece0e4b6ce80d4e9ec60c6a531f3e82a412e3397604f63189 |
| D03 | 2723 | 1cecff6ae8610c721a4bf2fcf8b33a670f18c3a9f72aa612303420f7ff49a26b |
| D04 | 1995 | 3b7f858a116b39967f23dc351012bb01f8ca5a71cea6f33259e3cca24e3d2399 |
| D05 | 2295 | 9258a8ba14b383e80d86394d373e96ae0f2d981ba27845758a08b0749a1d2ee0 |
| D06 | 3244 | 68a9e266542d5c22a1c6e7a98c5a9203879051bffc0c5dc9d5086c4fd50da439 |
| D07 | 2940 | aa8cceb6c027e983fb3b560fdff3464361a366f1b1d629e06f1b860e829b5c00 |
| D08 | 3185 | d3207cc18147ef0839d6a8af9efe8c4fabc2a48c63564a363a1e8196b439767c |

## 4. 当前实现与需求对照

| 目标能力 | 文档证据 | 当前源码/测试证据 | 差距性质 |
|---|---|---|---|
| Windows/PySide6/QML 四页应用 | D02 §1/3/13；D05 §2 | 无启动入口或 QML | 未实现，不是已验证缺陷 |
| Book/Chapter/Page、导入、标签、阅读 | D03 §3～5/29～30；D04 §4～10 | 无实体、Repository、导入器 | 未实现 |
| Region、四级文本、Lock、Revision | D03 §6～17；D08 AC-REGION/LOCK/REV | 无代码或数据库 | 未实现 |
| OCR/翻译/Mask/Inpaint/Rendering | D01 §5；D06 §6～24 | 无 Provider 或算法；旧路径不存在 | 未实现；效果未知 |
| Pipeline/进度/重试/恢复 | D06 §34～79 | 无 scheduler/worker/ViewModel | 未实现；契约尚有歧义 |
| Constraint/TM/Context | D03 §12～14；D06 §9～18 | 无实现与固定数据集 | 未实现 |
| Provider/代理/Credential | D03 §25～28；D07 §63～72 | 无配置或客户端 | 未实现 |
| Webtoon/多屏/DPI | D05 §40/64～65；D07 §8～15 | 无真实素材、截图或基准 | 未实现；不可宣称质量达标 |
| 导出/回收站/备份/清理 | D03 §31～34/45；D07 §37～51 | 无文件协议/迁移/测试 | 未实现 |
| 扩展能力与发布 | D01 §2；D02 §12；D08 §52～76 | 无插件、CI、发布包 | 范围/验收待细化，尚未实现 |

不能计算“功能完成百分比”：没有实现证据，也没有统一的功能计数口径。只能确定目前不存在可执行产品。

## 5. 已落实到 D03 的同步项

| 项目 | 当前证据 | 结论 |
|---|---|---|
| StageState stale | D03 L657～676 | 已有正式枚举与解释 |
| Region command types | D03 L1267～1271 | OCR/重译/重全翻译/重修/重渲染均已有 |
| Retry 来源 | D03 L1360～1376 | source_run_id、retry_reason、新 Run 规则已写入 |
| Optimistic guard | D03 L1551、1570～1599 | 输入 Region revision 与写入复查规则已有 |
| 可靠性 metadata | D03 §17.4、§34、§46 | app/schema version、完整性、Backup/Cache/Model metadata 已补入 |

因此不应再创建“从零添加 stale 字段”等重复任务。需要关闭 D06 §71/105、D07 §115、D08 §67 的同步遗留说明，并审查具体存储契约是否足够。

## 6. Gap Register

严重度是本次接管建议的实施风险级别，不修改 D08 的验收优先级。以下“缺口”均为文档/实施准备度结论，不冒充测试失败。

| ID / 等级 | 证据与差异 | 影响 / 下一动作 | Task |
|---|---|---|---|
| G01 / Blocker | 无 src/tests/HEAD；D02 §16 仅目录示意 | 无法逆向或复现；先审核接管、提交基线，再受控启动 | TASK-001/004/005 |
| G02 / Major | 接管前无 AGENTS、Task、Review 约定 | 本次提供协作规范；尚待用户接受及实际协作验证 | 本次接管 |
| G03 / Major | D01 L213～228/253 的源码引用不在仓库；D03～08 引用不存在的历史长文件名 | 不能认定可迁移能力或版本血缘；修订来源说明、链接 | TASK-001 |
| G04 / Major | D03 已同步；D06 §71/105、D07 §115 仍要求补充 | 会导致重复设计；逐项关闭旧建议，保留审计轨迹 | TASK-001 |
| G05 / Blocker | D02 L366 与 D04 L1156 将 Failed→Pending；D03 L1375、D06 §58/95、D08 AC-RETRY-002 要求新 Run | 需分开 Step retry、同 Run resume、新 Run retry；明确 Restart/Abandon | TASK-001/002/011 |
| G06 / Blocker | D03 §23 Task status 无 skipped；§24 Step status 未枚举；D06 §26 有 BLOCKED、§90 有 needs_review；§74 统计遗漏 paused/cancelled，§75 未定义零 Step 分母 | 持久状态、决策、进度分类不能混用；补全状态映射及聚合边界，包括 Region/Book target 展开 | TASK-002/011/013 |
| G07 / Blocker | D03 §24.1 使用 current_region_revision_id，但 Region 字段/ER 未明确 current 引用；单个 input_region_revision_id 与 D06 §84 多 Region Context Group 并存 | 明确每目标输入/输出 revision 映射及同事务 compare-and-write，不能只做事务外比较 | TASK-002/006/008/011 |
| G08 / Major | D05 §30/53 允许 Region/Constraint Revision Pin，但 D03 只有 ArtifactRevision.is_pinned；D05 §14 TM 禁用，D03 §14 无禁用字段；review_state 缺枚举 | UI 操作无完整存储契约；决定支持字段或正式调整 UI，禁止自行删需求 | TASK-002/008/010/022 |
| G09 / Major | D02 L296 每次请求读当前约束；D06 §10 要求 Run 准备后冻结 effective snapshot | 批量运行复现规则不一致；明确冻结时点及术语新增如何进入本 Run | TASK-001/002/010 |
| G10 / Major | D06 §29 Region geometry 使 OCR/Mask 等失效；§86 又将 Region geometry 列入仅 Render 失效且不使 OCR/Inpaint 失效 | 需区分内容几何与纯排版变化，统一失效矩阵 | TASK-002/008/011/014 |
| G11 / Blocker | D06 §85 只定义 SFX Translation skip；§3 DAG 的 Mask/Inpaint 分支可独立执行 | 未定义跳过/仅人工 SFX 的图像处理行为，存在擦除却无替代译文的风险（推断） | TASK-002/010/019 |
| G12 / Major | D03 为字段/ER草案；无 FK/唯一性/NULL规则/SQL；Review 状态、Region来源、目标关系等未完整落库 | 先冻结最小 Schema/DTO/错误码与测试示例；不得将 D03 宣称可直接建最终全库 | TASK-002/006 |
| G13 / Blocker | D06 §24 称每成功 Step 提交，§3 图仅末尾 Save；§94 要求中途成功结果保留；单 Region 操作可能合成 Page 级图 | 明确每步提交和最终汇总；正式文件用版本路径；合成范围、并发和故障点需契约 | TASK-002/006/011/014 |
| G14 / Major | D07 §3/4/73 等为 SHOULD；D08 对应 P1 并要求 100% PASS，AC-PERF-001 又允许豁免；暂停反馈由 SHOULD 升为 P0 | 阈值、支持矩阵、例外如何影响 READY 尚需统一，不能默许降低 Gate | TASK-001/003/004/026 |
| G15 / Major | D01 §5 指定模型路线；无真实测试素材、效果报告或依赖版本 | 模型可用性、质量、内存/设备路线不能保证；独立可复现实验后再选具体版本 | TASK-016/017/018/019 |
| G16 / Major | D05 有布局/窗口规则，但无视觉稿、完整色彩/尺寸 token；D08 要求多语言/DPI/多屏视觉检查 | 可确定信息架构，不能声称复刻现有 UI；后续依据 D05 补最小视觉规范及用户评审 | TASK-012/022/026 |
| G17 / Major | D08 185 个编号 AC，另有无编号组；D01 的网页/PDF/MOBI/Plugin Agent/字体/Sakura 等覆盖不完整 | 建完整追踪表和范围决定；P0/P1 不能因未出现在下一切片就消失 | TASK-003/023/024/025 |
| G18 / Major | D02 目标技术未固定兼容版本，打包/CI不存在；D07硬件值为建议 | 先验证 Windows/QML/可选依赖/打包最小路线，再锁依赖；当前系统 Python 不代表选型 | TASK-004/005/027 |

## 7. 当前验收状态

D08 中按二级标题提取到 185 个编号条目：P0=104、P1=81、P2=0。没有编号 P2 不表示没有低优先级需求。共有 61 个 AC 主题一级标题，其中有仅组级要求；它们也纳入追踪，不能在发布时漏计。

本次只执行文档审计：AC-DOC-001（8 文件齐全）PASS；AC-DOC-003（四个一级页面、默认书架）PASS；AC-DOC-002（术语/状态语义一致）FAIL，依据 G05/G06。其余 182 个编号 AC 均 NOT_RUN；无应用、测试框架或真实数据可运行。AC-SYNC 的字段存在性已核对，但冻结 Gate 尚未完成。

没有执行 OCR、翻译、修复 Benchmark，没有构建程序，没有声称任何产品测试通过。当前 NOT READY。

## 8. 本次交付与审核

本次新增项目入口、Source of Truth、协作协议、三种交付模板、11 类目标视图、Gap、Roadmap、27 个依赖 Task 和完整编号 AC 路由。原始 01～08 保持原字节；未实现未来 Task，未创建应用骨架、依赖环境、工作分支或远端。文档核验结果见 [接管验证记录](14_TAKEOVER_VERIFICATION.md)。

请审核：

1. 是否接受“文档基线阶段、没有现存应用实现”的现状认定；代码逆向部分当前明确不可完成。
2. 是否接受 Codex 集成、ZCode 实现、DeepSeek 实验/测试/独立审查，以及同仓库 linked worktree 规则。
3. 是否接受先解决 G03～G14 的契约一致性，再建立可运行切片的路线。
4. 审核批准范围是否只到接管，或释放明确列出的后续 Task。默认全部 TASK-001～027 仍为 proposed。

此清单是交付后的用户审核入口，不代表已经批准或已经实施。

## 9. TASK-001 修订与首次 Review

用户于 2026-09-13 允许提交初始基线并启动 TASK-001；基线为 `496b4ed`，工作分支为 `agent/codex/TASK-001-doc-consistency`。八份目标文档的本次改动可从 Git diff 逐项追溯，§3 指纹继续保留为修订前证据。

| Gap | 本次修订 | 保留事项 |
|---|---|---|
| G01/G02 | 初始 Git 基线和协作文档已获授权并提交；DeepSeek 已完成首次独立 Review | 应用源码/产品测试仍不存在；ZCode 尚未接入 |
| G03 | D03～08 改用实际文件名；D01 §5 明确旧代码来源未提供、不可核验 | 旧实现能力仍 Unknown，未删目标能力 |
| G04 | 本文 §5 保留唯一同步核验表；D06 §105、D07 §115 改为引用该表；D08 §67 只保留条件式 Gate | 仅关闭重复维护；Schema Gate 尚未完成 |
| G05 | D02/D04 取消原失败 Run 回到 Pending 的重试表达；D06 §58 明确新 Run 和来源字段 | Restart/Abandon、中间调度状态仍归 TASK-002，未启动 |
| G09 | D02 §4 与 D04 §20 明确准备阶段冻结约束，翻译阶段读取 Run 快照 | 更细的契约与测试向量仍归 TASK-002，未启动 |
| G14 | D07 与 D08 明确 NFR 等级不自动覆盖发布优先级；记录正式豁免的待决边界 | 数值、P0/P1、Release Gate 不变；豁免政策与支持矩阵仍待用户决定及后续任务 |

DeepSeek 首次独立 Review 绑定 `496b4ed..615a073`，结论为 `changes_requested`（P0=0、P1=1、P2=9），详见 [Review 报告](reviews/TASK-001-615a073.md)。本节记录的后续修订须绑定新 head 复审，不能沿用首次结论。G06～G13 等契约缺口仍存在，AC-DOC-002 仍 FAIL；AC-DOC-001/003 可作本次文档检查，其他产品 AC 继续 NOT_RUN。所有 TASK-002～027 保持 proposed。

复现入口：[TASK-001](tasks/TASK-001.md)、[文档检查脚本](../verification/TASK-001/verify.ps1)。初始 [接管验证记录](14_TAKEOVER_VERIFICATION.md) 是历史快照，不作为当前修订的验证结果。

## 10. TASK-002 最小契约冻结

用户于 2026-09-13 允许启动 TASK-002，并批准 Codex 依据既有需求完成后续最小设计取舍。冻结真源为 [TASK-002 最小数据与执行契约](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md)；D02/D03/D04/D05/D06/D08/D11 只同步各自职责内的入口和关键枚举，不复制整份契约。

| Gap / Review | 冻结位置 | 结果边界 |
|---|---|---|
| G06 | 契约 §5～6 | Run/Task/Step/Decision/Stage/Review 分层；blocked/skip/零计划/竞态与聚合明确 |
| G07 | 契约 §2、§4、§8 | current 指针、多目标输入输出、事务内 compare-and-write 与 Candidate 明确 |
| G08 | 契约 §2 | Region/Constraint Revision Pin、TM disabled、来源与 ReviewState 明确 |
| G09 | 契约 §3 | Run 创建时冻结快照；Continue 复用、Restart 重读当前配置 |
| G10 | 契约 §7.1 | 内容几何与仅排版几何分开，失效矩阵统一 |
| G11 | 契约 §7.2 | SFX skip/manual 不自动擦除图像文字 |
| G12 | 契约 §2～4、§9～10 | 最小关系约束、Port/DTO 与错误码明确；未生成 SQL |
| G13 | 契约 §8 | 每 Step 独立提交、最终汇总、不可变文件与 Region 局部合成明确 |
| R-011 | 契约 §6.2 | Restart 创建新 Run，沿用目标并重读 current/Lock/配置；原 interrupted Run 保留 |
| F-08 / P2 | 复审报告；待后续授权文档同步 | canonical 契约与 D05 已允许 blocked Stop；D02/D04/D11 派生图尚缺 `blocked → cancelled`，不阻塞本次冻结 |
| F-09 / P2 | master `c39ba99` | AGENTS 当前授权改为只回指 STATUS/Task，避免阶段状态再次过期 |

DeepSeek Harness 已批准 `b1b3f5d..885c9a9`，F-01～F-07 全部 resolved；Codex 以 `7927169` 集成并完成切片验证。TASK-003～027 未授权、未启动，仓库仍无应用源码、SQL、测试框架或可执行产品。

## 11. 生产可达性复核（2026-09-19）

**来源**：Qoder 的只读盘点 [PRODUCTION-REACHABILITY-AUDIT-2026-09-18](research/PRODUCTION-REACHABILITY-AUDIT-2026-09-18.md)（用户指示“只读盘点、不动代码”），经 **Codex 独立复核**（自写探针与证据见 [verification/POSTHOC-REACHABILITY-AUDIT-2026-09-18](../verification/POSTHOC-REACHABILITY-AUDIT-2026-09-18/codex-verification.md)）。本节只登记**已复核**的断点，不改动 §1～§10 的历史快照。

**结论**：STATUS 的「产品发布状态 NOT READY」成立，且依据比既有文档更强——**自动翻译整链在生产装配面上存在四道彼此独立的断点**，即使补齐真实模型依赖（AC-RFULL-001 的既有 `BLOCKED` 条件），从 UI 触发仍然跑不通：

| # | 级别 | 断点 | 复核方式 |
|---|---|---|---|
| 1 | P0 | 生产任务执行复用 GUI 线程创建的 SQLite 连接（`open_database` 在启动线程；`RunController` 在 QThread 里执行同一个 `PipelineService`）⇒ 首个 store 访问即 `sqlite3.ProgrammingError`；worker 崩溃后 run 在 DB 中停留 `running` | **端到端**复现（真实 `assemble_services` + 真实 `RunController`；主线程对照可跑完 ⇒ 纯连接归属问题）。**2026-09-19 收口**：TASK-048（`be558ca`）修掉跨线程异常，但其「共享单连接」方案被 Qoder 后置复审判 **W1 `overturn`（Q-001 P0：两线程 commit/rollback 同一事务 ⇒ 孤儿 Revision 10/10、静默丢写 7/7、run 被静默打死 3/10）**；重开后由 **TASK-060（`e7de64d`）**以「每线程连接归属 + typed BEGIN + drain-aware close」闭环。**另案（open）**：连接注册表**永不驱逐**（R-002）、`remove_managed` 的解析一致性（R-010）、`"." in parts` 死条件（R-011）。 |
| 2 | P0 | 生产无 Region 创建入口（`create_region` 无 UI 调用点），且 `build_production_handlers` 未注册 `detect` ⇒ 区域类步骤无输入 | **端到端**复现（`step_runs` 行 = `ocr region=None status=failed code=INVALID_INPUT`）。**2026-09-19 更正（Qoder 复审 Q-004）**：TASK-049（`e94d5af`）已把**接缝**接上（注册 `detect` handler + detection→Region 生产路径 + VM 槽），但**生产仍惰性**——`detector=None`、无 UI 调用者 ⇒ **落 Region 数仍为 0**；且该收口**只对含 `ocr` 的命令成立**，页级 `REINPAINT_ALL`/`RERENDER_ALL` 在无 Region 页上仍报 `INVALID_INPUT requires a Region target`（两条 region-free 链计入缺口）。 |
| 3 | P1 | 生产 Pipeline 的 `settings` / `provider_bindings` 恒为 `None`（`app.py:529-531` 只传 handlers / clean_probe）⇒ 越过区域墙后 `_chain` 抛 `PROVIDER_NOT_CONFIGURED`；根因含设置页空壳 | **端到端**：先经应用服务造出 Region，再跑 `OCR_REGION` → 运行期 `PROVIDER_NOT_CONFIGURED` |
| 4 | P1 | `commandError` 在 QML 中没有消费者 ⇒ 上述三类失败对用户完全静默 | **静态**：`src/ui/qml/**` 0 命中；13 处全部在 workbench ViewModel |

**另有**：**P-6**（工作台三档视图恒空白）已在 catalog 缝端到端复核——同一页同一 Managed Copy，workbench 的 `translated`/`compare` 恒空而 reader 能解析出 translated artifact；**E-1** 复现——`QT_QPA_PLATFORM=offscreen` 使 `tests/rendering` 两条断言假失败（2 failed / 61 passed；不设该变量 63 passed），故全仓口径须**不设**该变量；**P-5**（书架导入入口）静态不成立、运行期需 GUI 确证。**P-7～P-10（P2）尚未逐条复核。**

**证据方法论（要点）**：现有 **848 条测试**全绿，是因为它们走 mock/内存装配或直接调用用例层；`assemble_services` + 真实 SQLite + worker 线程这条**生产路径**没有任何测试穿过——因此 `N passed` 类证据无法否证上述断点。

**处置**：findings 采纳为**已复核事实**；**是否开切片、顺序与范围由用户裁决**（Codex 建议顺序：跨线程连接 → Region 入口/`detect` → provider 与设置写入面 → `commandError` 上屏 → 工作台视图）。本节不释放任何 Task。

**2026-09-19 进展**：**P-1 已闭环**（TASK-048 → 后置复审推翻 → TASK-060 `e7de64d` 收口；余 R-002/R-010/R-011 另案）；**P-2 接缝已闭、生产仍惰性**（行内更正）；P-3 已由 TASK-050（`21b7301`）接通读/写面（读面属**沿用既有能力**，见 Q-005 注）；P-4 已由 TASK-052（`a1c8171`，provisional 呈现）收口；P-6 已由 TASK-051（`65d1e13`）收口；P-5 仍待 GUI 确证；P-7/P-8 与 TASK-047/059 设计门相关；P-9 需产品裁决导出落点；**P-10 已由 TASK-058（`414a8e1`）收口**。
