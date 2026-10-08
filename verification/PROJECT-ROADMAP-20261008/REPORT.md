# 全项目任务盘点与整体规划

最新工作点：DSH R2对P08首轮修订head `31c26389`返回`changes_requested`；首轮P1已关闭，N-01..N-06已修订于1ad05d99，R3待启动，shell NOT_RUN因Win32 5。恢复状态见[最新恢复点](../P08/RESUME.md)。后继产品实现未释放；本报告其余审计结论保留为`e4242ecd`时点快照。

2026-10-08后续用户裁决：Qoder退出本项目；本报告的未来分配/可转发指令已改为ZCode主责UI/UX，Codex契约与集成、DSH非作者审查，fallback=ZCode→Antigravity。原Core/Desktop/Plan审计、台账、历史署名和Review保留审计时事实；它们的旧推荐不覆盖当前Plan/AGENTS人员资格。本更新不启动产品Task。

2026-10-08（Asia/Shanghai）。审计输入 `G:/CODEX/New Manga`，`main@e4242ecd419eb0eea098d2f63b40f709aa5caeea`；common-dir=`G:/CODEX/New Manga/.git`。本轮授权为规划/取证/中文图/中断恢复，不包含产品实施。

## 结论

项目已完成大量基础设施、AI生产集成与工作台竖切，**还没有完成从空安装态导入漫画、启动翻译、查看进度、人工修订、阅读和导出的完整四页产品**。目前“做完一个才知道下一个”的主要原因，是既有图记录了已交付 Task 历史，而未来产品能力尚未展开为依赖树；历史 checkpoint、旧候选和新完成状态又混在导航里。

本轮将整体路线放在唯一权威 [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) 顶部，分为“当前范围内收口”与“完整产品待范围裁决”，中文图见 [ROADMAP](ROADMAP.md)。以后只刷新受影响子图，不需要每完成一个小任务重新全仓推演。P01–P21 候选任务是未释放规划节点，正式Task冻结时再拆契约、Core/Host、UI和验收；没有编造工期或完成百分比。

## 完成了哪些任务

全量逐条记录见 [task-inventory.csv](task-inventory.csv)：ID、标题、架构分类、原状态/有效状态、Owner、Reviewer、依赖、base、集成来源与当前HEAD祖先核验。分类解释与已完成主线见 [plan-audit.md](plan-audit.md)。

| 台账集合 | 数量 | 解读 |
|---|---:|---|
| 正式Task文件＋历史T1.1.2映射 | 195＋1＝196 | 跨新旧架构的历史节点总数 |
| DONE_RECORDED | 114 | 105新架构/治理＋9历史完成记录 |
| 历史VERIFIED_COMPLETE / DOC_ONLY | 48 / 5 | 历史完成与文档交付；不代表新架构页面 |
| 登记完成或文档交付合计 | 167 | 不能用167/196作为产品完成率 |
| 历史PARTIAL | 9 | 原范围有局限；不恢复Legacy实施 |
| 历史未完成归档 | 13 | 原未完成项保留；不是当前待执行队列 |
| closed_with_limitations / superseded | 1 / 6 | 受限关闭与被取代；不等同技术完成 |
| 当前进行中 / 已释放 | 0 / 0 | 旧worktree与ready段落不能推断运行中 |

M2前缀正式Task为101个；加GOV-001、两个DIAG-M2与DOC-FIX，新架构/治理105个均有done/集成记录并定位到HEAD祖先。这里只复核现有证据，不冒充重跑105份验收或重新做独立Review。

| 已完成能力组 | 代表任务 | 本次确认的结果边界 |
|---|---|---|
| 架构、Core与数据基础 | M2-D1/I1/I2/R1/UI1；C1/C2；GOV-001 | 分离装配、类型契约、SQLite与Managed Copy；UI1是设计，不是四页实现 |
| 安全IPC与图像通道 | S1/S2/S3；RC1/RC2；IPC1；资源hash/2GiB系列修复 | 真实sidecar/受控资源URL/完整性保护；不是React全页/长条阅读验收 |
| 数据安全与fail-closed | AC1/AC2/AC3/AC4及后继F-1/F-2修复 | 保存恢复、源hash、Lock/current/pinned、export lineage等限定验收 |
| Windows分发基座 | AC5、fresh-checkout、RG1、PROD-DETECT-2/3、PROD-SFX-PROBE-1 | NSIS与五frozen入口；本机有界Gate，不是当前完整产品发布 |
| JA/KO素材与模型集成 | TA1/TA2/TA3系列、manga检测、Paddle3适配、webtoon tiling、SFX训练/部署/GPU系列 | 真素材与指定质量/运行证据；实验done可得FAIL，非全质量达标 |
| 可操作React工作台 | WORKBENCH-REACT-1、MISROUTE-UI、RC4、PAGE-RESOLVE/NAV、两DEBOUNCE | 书→章→页、图像、region改标、历史恢复、重渲染实际接通 |
| 回收与最近加固 | GC1/GC2-DESIGN/GC2、ICU诊断修复、Runner Debt/Guard | GC2已实现done@cea610ed；Runner Guard最新done@e7d1f7f8，不重新释放已闭任务 |

典型区别：DOCTR-QUAL-RUN正式结果FAIL；TA3-B2当轮FAIL，由B3关闭指定KO缺口；GC2实现完成但未知来源/current/pinned和长会话仍保留。原失败日志和局限不改写PASS。Manga109永久取消，旧TA3-B endpoint blocker已被后继收口，BJ13/0.90裁决已确认，不再要求用户重复回答。

## 代码深读后，哪些产品能力没有完成

| 能力 | 当前真实代码 | 未完成部分与后继 |
|---|---|---|
| 四页产品壳 | `App.tsx:74,478`：Console↔Workbench；Library/Settings section | 不是书架/工作台/阅读器/设置四页导航。P08先复用UI1冻结范围/设计，P12/P14/P15/P17分别落地 |
| 空库建书与导入 | LibraryPanel只读ListBooks；Core已有Library/Import API | 无production创建/导入IPC与受控选文件链；`core_service.py:313,369` decoder恒1×1。P09真实decoder/受限来源与Managed Copy，P12接UI |
| 翻译启动与任务控制 | `core_assembly.py`已有PipelineService；生产15条Tauri命令不含StartRun | `WorkbenchToolbar`仅上下文；`TaskProgressPanel:1,31`静态占位。P11冻结接受/快照/控制语义，P13复用后台执行，P14接真实进度 |
| 人工编辑与保护操作 | EditingService/Revision/Lock/pin后端能力、当前改标/restore部分接通 | 译文编辑、Lock/Pin、region增删/几何修改完整UI/IPC parity未接通。P14按已批准需求拆冻结写命令，保护expected revision |
| 设置/Provider凭据 | SettingsPanel真实读取保存SFX三策略 | 完整profiles、credentials、网络/诊断设置与secret exchange未产品化。P10先安全契约/能力，P15接设置页 |
| 阅读与导出 | Python reading/export存在；AC1测试模式可调用 | 无React Reader、production ReaderProjection/进度/Export命令。P16/P17的基础Reader范围已确认，实施待释放，不能借AC1测试桥代替 |
| 真实质量 | 生产manga/SFX、PaddleOCR、remote translation与指定素材run已有证据 | JA G1自动对齐、F4无字页、翻译相似度口径、修复实际质量和域覆盖仍有局限。P18按样本/阈值验收；不默认开启模型训练 |
| 修复模型 | SimpleFill/EdgeBleed可运行；learned registry条目仅登记 | LaMa/AOT/BrushNet/FLUX `implements=False`，不记为实现。是否新增由P08/P18质量差距决定，避免提前堆ML依赖 |
| 源样式/导出格式/维护 | 生产样式分析器返回空列表；PDFComposer未注入；maintenance服务存在 | P08明确样式保持、图片/PDF/MOBI与PNG/ZIP/PDF所选格式；P15落实现行P0/P1维护与DB＋Managed Copy全库备份，接安全停写/回滚；P16逐格式验收。已有服务不等于production能力 |
| 包与安全生命周期 | 第五SFX入口已构建；GC2 namespace/retired保护已实现 | R-003 packaged入口coverage仍未释放；GC G7多版本分发迁移仍是Gate；Windows10未测。P03/P06/P20补限定证据 |

详见 [Core深读](core-audit.md) 与 [Desktop深读](desktop-audit.md)。实际调用链覆盖入口、装配、业务服务、持久化、资源句柄、React消费者、Tauri白名单/ACL、runner与测试证据；不以源码存在测试类直接宣布运行PASS。Core仍有惰性Qt图像读取seam，现有Pillow渲染是真的；不为“Qt-free”口号强制全库重写，按新架构实际功能和packaged执行结果决定适配。

## 整体规划怎样使用

1. **完整产品范围先可审查**：P08决定四页最小parity、验收质量、控制语义、Windows声明矩阵；利用现有UI1和本轮取证，不重做视觉研究。
2. **接通真实输入**：P09/P10/P11可先并行设计，共享契约串行集成；随后P12导入界面、P13后台Pipeline。
3. **接通真实输出与操作**：P14工作台完整运行/编辑、P15设置、P16/P17阅读导出按依赖落实。
4. **质量与发布合流**：P18真质量→P19四页真实E2E→P20声明范围内的固定包发布；P03第五入口与P06迁移安全提前补证。
5. **小债务按风险插入**：P01元数据/报告取证、P02真实DOM、P04并发/命令族验证、P05注记、P07真实剩余交互。无证据缺口直接销项，不制造新抽象。

远期任务是工作包，不是一个Owner同时拥有契约、Core、UI所有路径。正式释放拆为“契约→实现→UI→非作者验收”，各自固定base/允许路径；产品未知项保留proposed / 未释放/等待裁决。Owner与Reviewer不同，Codex集成验证不能替代独立Review。

D1已解冻基础Reader，跨页联动/页缩略图仍延期；P16/P17待P08正式Review/集成后单独释放。缩略图/跨页不作为默认范围。BJ13补标补画仍暂缓。Legacy29个非完全技术完成节点保留历史，不为提高计数继续实施。P21移除Legacy是可选、另授权、parity之后的事。

P08已选择基础Reader；P19/P20保持全部P0/P1和完整主流程，不将未做项N/A后宣称完成。P01取证找不到原Review也可明确NOT_VERIFIED处置，不要求先找齐全部报告才准备P08。B3的8/8 export OK不代表每个Run严格状态都COMPLETED；K01 terminal/step不一致在P18先核验，不凭旧报告宣布当前bug。

## 文档冲突与证据限制

- `M2-DERIVED-GC-2.md`头`integration_commit:null`落后于正文done@cea610ed；本轮台账按真实祖先/Plan显示完成，不重新派发。
- `M2-PROD-DETECT-3.md`页头完整SHA不存在；真实短hash解析为`8fe5199c6d05d144052141ad02ed054bbaa90645`且为HEAD祖先，CSV保留来源，不掩盖错字段。
- ANNOTATE-R2、SYNTH-BG-AUTO页头落后于集成；两份原独立Review载体尚NOT_VERIFIED，不能把祖先核验当独立批准。
- AD-001与12_ROADMAP的早期“当前”现实、旧图ready/blocked与后继完成不一致。本轮仅在Plan/Index/Roadmap导航加最新入口与历史标签；不篡改历史报告/原日志或产品需求。
- stdio两锁/响应关联、卡死/超时为静态候选，尚未动态复现。P04先验证；不能直接宣布bug、直接修或造通用RPC框架。

Packaged26/26的已入库证据绑定source=`3d532c1f99e49da703d2076bd67d46b710866637`与installer SHA=`ef617573ab39c0469079203489f4db4af78ae4e3437f8d97d87a3565bb40fa75`；Guard的测试范围不含本轮fresh整包重建。尊重RG1用户“本机视为干净Windows基座，通过即PASS”裁决，该Task结论有效；不额外强加独立干净机作为既有Gate条件，也不把限定结果扩写成Win10或完整四页发布通过。

本轮产品pytest/cargo/vitest、GUI与fresh build全部 **NOT_RUN**：任务是规划盘点，复跑整套不能证明缺少的UI/IPC已实现，且会消耗时间。现有测试与日志按原commit/环境引用。另执行本轮台账/祖先/依赖/链接/范围与空白检查，结果见 [validation.log](validation.log)。

本轮 [planning-check.md](planning-check.md) 有界一致性核对未发现done/PASS夸大或Reader偷解冻；指出PC-01恢复点过时、PC-02日志尚未生成。Codex已更新RESUME并真实执行verify_plan.py，完整日志EXIT=0；两项完成处置。该核对不是产品Independent Review，不对产品Task新增approved。检查器可在恢复时复制运行，固定统计只适用于本审计快照，后续Task变化应刷新台账，不能硬改assert维持绿。

## Plus额度与恢复

本轮采用三个互不重复的GPT-6.1 Sol high审计，每个从独立短brief开始；主会话实测模型GPT-6.1 Sol、effort=medium，未声称改为high。高推理的三路结果用于整体规划；不派发产品实现、不创建定时轮询、不下载素材、不重跑全量测试。未来常规工作优先每次只开一个必要Agent，本次三路已结束后不继续常驻。

开始读取账户工具时5小时窗口剩80%、周窗口剩59%（动态快照，非本轮用量）；它们分别于北京时间2026-10-08 18:35:42、2026-10-14 11:44:12重置。最终以账户页面/工具实时值为准。官方说明额度消耗受模型、任务、上下文、推理、工具等影响，不能精确折算成还可完成几个Task；[OpenAI官方说明](https://learn.chatgpt.com/docs/pricing)。不自动购买额度或消耗免费reset。

[RESUME.md](RESUME.md)已在审计中途落盘，包含base/head、dirty保护、已交付、剩余步骤和可转发恢复指令。工作完成时保存结果/状态边界；恢复先核Live Git和STATUS，若DRIFT_DETECTED仅分析变化。额度恢复后用户可在原chat直接发：

> 继续 New Manga；先读 verification/PROJECT-ROADMAP-20261008/RESUME.md，核验 Git 与 Plan/STATUS，复用已有台账和报告，只推进检查点指定的下一步，不重新全仓审计，不覆盖他人dirty，不启动未释放实现。

无法承诺额度恢复后自动唤醒，也不需要为此新建自动化。若用户选择ZCode/Antigravity接管，本恢复材料可转发，接管者按AGENTS/协作协议核验授权与角色边界；Owner不得审核自己，主协调者只能在安全边界回切。报告、台账与图保存为仓库文件，即使换会话也可恢复。

## 推荐下一任务与可直接转发指令

当前执行点：[P08 DSH正式Review指令](../P08/DSH-REVIEW-PROMPT.md)。D1–D7已全部确认，无需再次询问；固定head、Reviewer与DSH session已登记。下方长指令是此前规划快照，不得替代当前Task与恢复点。

**Task**：[P08](../../doc/tasks/P08.md)“完整产品范围与验收冻结准备”（changes_requested / CHECKPOINTED；D1–D7已确认，首轮固定范围head=`490f9bd9`，DSH报告含4 P1/6 P2）。**Agent**：Codex负责范围/契约，DeepSeek Harness非作者Review；后续ZCode另开设计Task。P08完成前及单独释放前均不得启动后继产品实现。

**Recovery point**：唯一仓库/branch=`G:/CODEX/New Manga`/`main`；审计base=head=`e4242ecd419eb0eea098d2f63b40f709aa5caeea`。后续治理提交与实际HEAD须live核验；正式Task branch/worktree待Codex创建，不臆造。**Scope**：只读src/apps/tests/Task/契约；新正式Task范围拟限自有Task、范围/验收草案、自有verification、Handoff，Plan/STATUS/索引由Codex维护。禁止生产src/apps、Schema、依赖、用户数据、已有raw、既有dirty写入；草案不修改冻结wire或需求。

**Deliverables**：逐产品能力的must/deferred/out矩阵；每个现有命令/后继契约映射；Reader解冻与发布矩阵需用户裁决的具体选项；后继产品与发布候选任务逐步正式Task草案/依赖/Owner/Reviewer/allowlist/Gate。复用UI1，不再造一套视觉规范。**Verification**：PowerShell下Git Reality Check与`git diff --check`、相对固定base路径核验；每项需求能追溯D01/D04/D05/D08/现行Task和源码，草案/UNKNOWN/NOT_RUN如实保留。固定文档交付经非作者Review、Codex集成后才登记该设计Task done；这不释放任何产品实现。

```text
以下为该报告生成时的原始转发指令快照，当前不可执行；事实与恢复步骤以当前Plan、Status和[P08 RESUME](../P08/RESUME.md)为准：在 G:/CODEX/New Manga 继续；先读取 AGENTS.md、doc/REBASELINE_PLAN.md 当前整体路线、doc/STATUS.md，以及 verification/PROJECT-ROADMAP-20261008/{RESUME,REPORT,ROADMAP}.md。审计base/head=e4242ecd419eb0eea098d2f63b40f709aa5caeea，当前branch main；实测HEAD/status/common-dir，保留.qoder-credits和历史dispatch dirty，不reset/clean/stash。建议当前准备=P08，已进入blocked等待裁决/审查，正式ID P08 尚未创建/释放；Codex主责范围/契约、DSH建议非作者审查，ZCode设计另开Task；branch/worktree待Codex实际创建。先复用本轮Core/Desktop/Plan审计和CSV，形成四页must/deferred/out与质量/Windows验收矩阵，提前拆后继产品与发布候选任务的契约/Core/Host/UI/验收依赖，不再每做一个才猜下一步。允许只读生产代码；写集合仅拟议自有Task、范围/验收草案、verification/Handoff与Codex治理导航，禁止生产src/apps、Schema、依赖、冻结wire、用户数据、已有raw和他人dirty。Reader/跨页/缩略图保持当前明确不做，若完整目标需要Reader先列产品裁决，不默认解冻；Manga109永久取消，BJ13維持0.90手工改标+skip。逐项写需求/代码证据、允许路径、实际Owner/Reviewer、可复制测试计划和Gate；planned/NOT_RUN/UNKNOWN不记PASS。仅准备范围，不实施、不派发未释放产品Task。文档固定提交后交非作者Review与Codex集成验证，再更新checkpoint；只有正式释放范围后才逐节点实现。
```
