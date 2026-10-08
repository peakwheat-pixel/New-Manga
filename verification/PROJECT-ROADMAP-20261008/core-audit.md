# Python Core / Pipeline / 数据安全只读审计

审计日期：2026-10-08（Asia/Shanghai）。审计输入：`G:/CODEX/New Manga`，`main@e4242ecd419eb0eea098d2f63b40f709aa5caeea`，Git common directory=`G:/CODEX/New Manga/.git`。执行者：Codex 内部只读审计子代理。允许写入仅本报告。生产代码、治理文件、数据库、权重及用户数据零修改；没有启动外部 Agent、模型下载、真实 API 请求、产品或昂贵测试套件。

已读 `AGENTS.md`、`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md` 当前覆盖层/M2 扩展树、`doc/STATUS.md` 顶部、`doc/09_COLLABORATION.md`、AD-001、M2-C1 与 RC-4 契约及相关 Task/verification。当前 STATUS/Plan 顶部为**无 Active / released Task**；下方历史 ready/blocked 文字不能用于实施。Plan 没有正式 M3/M4 树；下列 `P-*` 全是 `PLANNED_PLACEHOLDER` 建议，未创建、未释放。

工作区开工时已有 `.qoder-credits/report.json` modified、Qoder canvas untracked、两项 Antigravity dispatch artifact untracked，均保留原作者内容。其他审计作者的并行文件不属于本报告审查范围。

## 结论

Core 的可复用业务基础已经相当完整：SQLite/Managed Copy、Region/Revision、Pipeline 编排与恢复、检测/OCR/翻译基线、确定性基础修复、Pillow 重渲染、阅读进度和导出服务都有真实代码。**当前正式 React/Tauri 产品命令面尚不足以让用户完成“新建书籍→批量导入→配置翻译→启动整链→中断恢复→阅读→导出”。**部分链路只有验收桥、实验 driver 或 Legacy UI 接通。

优先级应是把既有服务以冻结、受控命令接入正式桌面，先解决真正的导入适配器、异步运行/状态投影/恢复、Settings provider/credential 设置，再接 Reader/Export/维护。模型扩展与质量研究另列，不能拿 provider 名称、测试文件或 Mock PASS 代替真实能力或正式桌面 PASS。

## 1. 实际入口和调用链

| 层 | 当前真实调用链与证据 | 判断 |
|---|---|---|
| 正式桌面 Core | `apps/desktop/src-tauri/src/main.rs:195` 起生产 invokes → `library_bridge.rs` → stdio → `src/bootstrap/core_service.py:1741` → `assemble_production_core:327` → `assemble_core_services:744` | 新架构生产路径。Python 拥有 DB/领域；Rust 转发。生产命令面由 `main.rs:102` 起各命令数组及 `command_allowlist:136` 定义。 |
| Core command surface | `core_service.py:1104` dispatch：ping、ListBooks、core.detect、settings.get/update_section、set_region_type、list_regions、list_region_revisions、restore_region_revision、rerender_page、list_chapters、list_chapter_pages、resolve_page_resource、shutdown | 原有写业务并非全部放开；不存在 StartRun、ControlRun、Import、SaveReadingProgress、StartExport、Backup/Restore 等生产命令。`core.detect` 还是直接编码图片的诊断/检测入口，并不是用户点击“翻译整章”的持久 PipelineRun。 |
| 编排装配 | `core_assembly.py:1028` handlers → `build_production_pipeline`（`infrastructure/pipeline/assembly.py:17`）→ `PipelineService`（`application/tasks/service.py:188`）→ `SqlitePipelineStore`/`SqliteTargetCatalog`/`SqliteSnapshotProvider` | 真实可复用业务。装配运行 startup recovery；未等于正式前端能创建或控制 Run。 |
| 模型步骤 | `infrastructure/providers/handlers.py:182` 注册 detect/ocr/color/term_extract/translate/segment/mask_refine/inpaint/render；各 handler 经 Port/registry/writer | handler 九步骤已齐，不应再立“补缺 render/color/term handler”任务。 |
| 测试验收入口 | `bootstrap/acceptance_bridge.py:1` 明确 acceptance-only、`M2AC1_TEST_MODE=1`；`assemble_acceptance_core:164` 使用 Qt adapters+mock providers；`method_run_pipeline:330` 驱动真持久化 | 有效证明 Mock 编排/落盘/重启/Reader/PNG 导出。不能升级为产品 import/start/export 已实现；production mode 不注册 ac1_request（`main.rs:523`）。 |
| Legacy UI / 实验 | `bootstrap/app.py` 装配 QML ViewModels；`experiments/M2-TA3-B/**` driver 直接调用 Core/Pipeline | 可复用的服务与实验质量证据；不是新 React/Tauri 用户入口。只迁移产品行为，不释放 Legacy 修复。 |

契约明示尚未实现的 Proposal：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5 中 CreateBook/Chapter、Import、StartRun/GetRunSnapshot/GetTaskProjection/ControlRun/RetryFailedTargets、Create/DeleteRegion/SaveManualTranslation/SetRevisionPinned、Reader/ReadingProgress、StartExport/CancelExport；runtime 与并发/长任务语义需新 Task 冻结。已落地章节导航并不等于 ReaderProjection。

## 2. 能力盘点：新架构接通、可复用、占位分开

| 能力 | 当前实现与源码 | 已完成 Task / 历史证据 | 当前缺口 |
|---|---|---|---|
| DB 与 Managed Copy | `infrastructure/sqlite/connection.py:81` thread-routed connection；schema/migrator；`filesystem/managed_storage.py:97` temp+fsync、`:114` publish；library/regions/artifacts adapter | M2-I1 `cff1e0a8`；M2-AC2 `9d3c1db5`；其更早持久化 Task 是服务沿用依据 | 不需要重写数据库。跨新 Run worker/IPC restore 的连接所有权仍需新的端到端 Gate。 |
| 书籍/章节/页 | `application/library/service.py` 与 `sqlite/library.py` CRUD；Core ListBooks/ListChapters/ListChapterPages；PageResource resolve | M2-IPC1 `04c1394a`；页导航 `657af2e3`；资源 resolve `9e242b0c` | 正式产品写入口缺 Create/Update/Delete/Favorite/Archive、书籍/章节新增、导入；书架展示已有库与创建新的用户库是不同完成面。 |
| 图片导入 | `application/importing/images/service.py:50`：源只读、hash去重、decode→copy→Page；`infrastructure/importing.py:99` 有真 QtImageDecoder、`:137` ManagedCopyStoreAdapter | Legacy 导入服务可复用；M2-AC2数据证据及 ALLOC `f9c15e45` 真大图路径 | 生产 `core_service.py:313` 的 `_PassthroughImageDecoder` 忽略 bytes 恒返回1×1，`:369` 注入真 importer。现无正式Import，因此是接线前置缺口；不得直接把该装配暴露成生产导入。需真实 decode 校验/尺寸/格式与受控宿主文件授权。 |
| PDF/MOBI 导入 | `importing/documents/service.py:118`；`core_assembly.py:813` 装配 PDFium/Mobi raster。失败 typed，source readonly、沿用Managed Copy | TASK-023/041/043 历史实现、导入测试 | 正式IPC未接；raster编码仍有Qt链。生产闭包是否包含全部可选解析器要逐格式Gate；先按已批准格式最小切片，不默认宣称全格式可用。 |
| 检测 | manga RT-DETR、docTR回退选择、SFX并行；`core_assembly.py:889` 起backend/权重查找；`detection_manga.py` 长条tile+坐标回映；`detection_sfx.py` hash pin、V2B、EP与重叠仲裁 | DETECT-1/2/3 `056617e4/9e44fb21/8fe5199c`；TILING `061fbb60`；SFX T4 `cff4923e`、GPU `931a6d03`、EPFAIL `9a29e742`、probe `177b356a` | 生产检测能力已实现；BJ13阈值0.90/手动改标+skip裁决维持。`core.detect`不做持久Run任务。不存在再跑旧docTR以“全部检测待实现”的理由。 |
| OCR | `providers/ocr_local.py` MangaOcrProvider/PaddleKoreanOcrProvider；Paddle bytes→BGR ndarray修正；Vision OCR仅显式配置fallback；handlers:316 | PADDLE3X-1；TA3-B2/B3真实OCR证据 | 正式设置未有完整provider绑定/模型可用性/密钥流程；真实OCR库和模型在dev OCR专用venv成功不等于现安装包可用。本审计未加载模型/运行OCR。 |
| 翻译 | handlers:382 构建上下文与协议、OpenAI-compatible/Sakura Port adapter；runtime.py:530 起registry；StdlibTransport+vault resolver在core_assembly:836注入 | TASK-017/019沿用；TA3-B2 `228b70c5`、B3 `0f872d1b`真实remote证据 | 产品尚无 CredentialRef exchange、provider/profile/binding管理、连接测试的完整正式IPC。settings_update_section仅普通设置投影，不等于API key安全存储通路。旧quality-report中临时env resolver不能作为生产credential完整Gate。 |
| 遮罩/修复 | handlers:471/518/566；geometry mask/refine、inpaint protection/router；`providers/inpaint_routes.py` SimpleFill/EdgeBleed真实算法 | TASK-018/019沿用，TA3 A/B真实链 | `runtime.py:609` LaMa/AOT/BrushNet/FLUX descriptor `implements=False`+factory=None；仅模型名称/依赖要求注册，占位并fail-closed。彩色复杂背景高质量修复尚无learned implementation/qualification。 |
| 源样式提取 | SourceStyleService、真实PixelSourceStyleAnalyzer在旧Qt装配有用；color handler已注册 | TASK-033/035等沿用 | 正式core_service:321 `_StubStyleAnalyzer`恒返回[]，所以headless rerender使用默认/已有样式，不等于生产源字体/色彩自动检测完成。需样式保持目标先冻结再接真实分析器。 |
| 渲染 | `application/rendering/service.py:173` rerender_page、region渲染；PillowFontCatalog/TextLayout/Compositor（core_service:342起）与NMFR decode真实装配；RenderService单独写translated pointer | RC-4 `0a7e0d5b`、contracts/RC4 rev1.6、`tests/core/test_rc4_stdio_render_preview.py:84` | 同步单页rerender已可达；通用PipelineRun重渲染族未接。批量逐region对整页画布多次合成，长条页性能/内存是实测候选，不应顺手重构。 |
| 人工编辑/历史 | `editing/service.py:307`改标；`:697`手工译文；`:734`恢复；regions.py:201事务；Core list/restore/retype | RETYPE `d8019810`；RC4 `0a7e0d5b` | 改标/恢复已接通；创建删除区域、几何编辑、手工译文保存/confirm/锁与pin写命令尚未正式接通。只读几何不等于可编辑Canvas。 |
| Reader | `reading/service.py`＋SQLite progress store、`core_assembly.py:348` reader catalog当前translated/Managed original | AC1 Mock loop；T3.1.1 SQLite store历史复用 | 正式GetReaderProjection/SaveReadingProgress缺失；页导航读取和原图资源已有，但阅读进度持久化/translated current/恢复/长条Reader需专门接入。 |
| Export | `export/service.py:216` export：stale/missing策略、temp→os.replace、hash、history、repeat；PNG/ZIP等现有write分支 | EXPORT-LINEAGE `d71883ec`、M2-AC4 `fc991821`、AC1 PNG | 正式Start/CancelExport与受控输出文件选择缺失；`core_assembly.py:1149` ExportService未注入pdf_composer，PDF分支`:423`因此fail-closed；pdf_qt.py是可复用Qt实现，不能标headless PDF完成。 |
| 删除/清理/备份恢复 | TrashService软删/同batch恢复/永久删/失败重试；SqliteBackupService `.backup`、sidecar/hash/pre_restore/rollback；cleanup/log/diagnostics服务 | Legacy maintenance Task只作已存能力；tests/storage/test_backup_restore.py等 | CoreServices仅注入trash/diagnostics，不注入BackupLedger；生产IPC无trash/cleanup/backup/restore。恢复涉及全部worker/连接停写，不能把Legacy restore_gate的PASS直接搬到新IPC。 |
| 派生preview GC | Core启动命名空间exclusive→sweep→shared，识别retired且非current/pinned、身份/hash/size匹配才删副本；未知保留 | GC1 `44859014`；**GC2 `cea610ed`已经done**；`git merge-base --is-ancestor cea610ed HEAD` EXIT=0 | 不再把GC2记待实施。Runner快照/历史raw已分别done `73588624/e7d1f7f`；剩余第五入口packaged assertion R-003与模块装载R-06按原deferred，不扩大成本。 |

## 3. 安全与恢复：既有保证和新入口必须承担的 Gate

### 3.1 已存在的保护

- 原文件只读/Managed Copy：`ImportImagesUseCase`先hash/decode再copy、拷贝存在后才写Page；重复SKIP不制造第二份。`ManagedCopyStoreAdapter`校验源名为单路径组件、验hash、不可变revision路径；读取面以resolved containment限制managed根。永久删除额外拒绝`..`/绝对路径/junction/reparse（managed_storage.py:125）。
- revision原子性：`sqlite/regions.py:201` `BEGIN IMMEDIATE`内重读current/Lock→插revision→更新pointer→commit；失败rollback。`sqlite/artifacts.py:137`先唯一temp/验hash/publish，再短事务比较pointer，失败保旧current并报告orphan。恢复新建restored revision，不改写原历史或pin（editing/service.py:734、RC4测试）。
- Run提交与并发保护：`tasks/service.py:627`校验output target映射；`sqlite/pipeline.py:568`重读输入revision/Lock与原子pointer/stage；冲突在service:661保为candidate，而非覆盖人工成果。OCR/translate writer同样事务expected守卫（providers/step_writes.py:210起）；render handler:774声明RenderService为translated唯一写者、返回revision_updates={}。
- 持久Run恢复：`create_run:213`冻结scope/settings/provider/context快照；`SqlitePipelineStore:393`保存Run/Task/Step/Candidate；`recover_running_runs:902`将遗留running改INTERRUPTED，`control_run:845`支持continue/restart/abandon；`retry_failed_targets:919`创建source-linked新Run。暂停/停止在step边界检查，不能宣传能中断正在阻塞的远端请求/模型调用。
- fail-closed：provider依赖/配置失败typed穿handler→StepExecutionError→run账目；不存在默认虚构OCR/译文。Mock providers只有明确acceptance flag注册。未知命令/协议版本拒绝，不输出OS路径/traceback到普通wire。
- 派生图回收：core_service.py:1741启动阶段保护namespace，`:1833`reverify product DB、current/pin/source identity/hash/size；`:1889`未知或query失败保留。GC只回收副本，不删除来源artifact，不按年龄/数量猜安全。
- 备份恢复既有实现：`sqlite/backup.py:129`校验ID/路径/sidecar/hash/schema→pre_restore→overwrite SQLite→migrate/integrity→managed consistency；失败回滚pre_restore。Managed consistency仅报告缺失，不恢复图片；**这是数据库备份，不是完整用户库图片备份**（backup.py:260）。

### 3.2 正式用户入口必须补证的边界

1. **长任务不能堵塞串行stdio控制通道。** 现Core `serve_forever`串行dispatch、Rust桥请求mutex。把同步execute_run直接放进dispatch会占用控制/查询；需要冻结“提交run即返回accepted→独立worker→持久snapshot/projection查询→control”最小机制。先复用PipelineService，不建第二套状态机。恢复应展示INTERRUPTED并让用户continue/restart/abandon，不自动重试收费API。
2. **新用户真实导入不得走1×1 stub。** 新建书/章、选文件/目录、授权受控读token、Core decode/copy、报告partial/pending/cancel/duplicate必须组成一条可验收链；大图拒绝与真正尺寸一起验证。IPC不让WebView传任意路径或Base64整本漫画。
3. **Settings热更新不等于provider运行时已重装配。** 当前provider registry和sfx policy在装配时读取；`settings.update_section`持久defaults。设计要冻结新Run使用新settings、旧Run用旧快照、runtime/binding缓存生效时点与安全重载，避免UI显示已改而执行仍旧配置。
4. **Reader/Export必须使用同一current revision。** 当前服务和locator可复用；新ReaderProjection与Export scope必须明确stale/missing/fallback、source/render/Run lineage。输出路径由宿主选择能力授权；覆盖取消失败不改原输入和已存在目标。
5. **维护恢复需应用级停写。** ThreadRoutedConnection只保证每线程事务，不会自动阻止其他worker/sidecar继续写；`_restore_database`注释依赖restore gate。新架构需排空Run/heartbeat/preview/DB所有连接并安全重装配，不能直接调用overwrite restore。
6. **发布闭包与纯headless是不同Gate。** 正式单页render是Pillow；完整pipeline像素源`core_assembly.py:238`仍惰性PySide6 QImage，document raster也有Qt编码、Webtoon TiledPageRasterizer仍有Qt支撑。能启动无GUI Core不等于完整执行无Qt。按ADR最终目标另立最小adapter替换切片；不重写Domain/Application。

这些是规划缺口/新seam验收要求。本轮未运行触发器，不将它们定级为当前已复现的产品P0/P1。

## 4. 证据账本：哪些 PASS 可以引用

本轮只进行了源码/文档/测试阅读和Git事实核对，**本轮所有产品、模型、native、构建、真实质量测试=NOT_RUN**；没有以测试文件存在记PASS。下列是已入库、绑定历史commit的既有证据，适用范围保留。

| 已有证据 | 固定结果与边界 |
|---|---|
| `verification/M2-AC2/verification-results.md`（delivery `8db6d150`、integration `9d3c1db5`） | Python3.12.3、Task012解释器、11数据保护测试passed、EXIT0；source/hash/duplicate/Managed copy/missing/manual+Lock/pin/restore/reassemble/INTERRUPTED。纯Core API夹具，不代表正式导入或Run IPC。 |
| `verification/M2-AC3/integration-a63d3372/integration.md`（merge `cac37485`） | 冻结tip复跑8 provider fail-closed、23 m2 acceptance、EXIT0；错误注入经mock typed。明确retry_failed_targets/recover_running_runs直达补强候选、mutation边界，不能扩大成全网络真实故障已验收。 |
| M2-AC1 `f162193b` | Mock/Local完整loop与SQLite落盘/重启/Reader/PNG。独立于真实OCR/翻译质量，也独立于正常产品命令面。 |
| `verification/M2-TA3-B/quality-report.md`，B2 merge `228b70c5` | 首run正式结论FAIL，pipeline_failures=10；JA10case export OK，KO检测/大图缺口；JA CER NOT_AUTOMATED、KO6样本CER0.0556 directional且排除规则下偏。不能从done推断质量PASS。 |
| `verification/M2-TA3-B/ko-fullrun-report.md`，B3 merge `0f872d1b` | 后续8/8 KO export OK关闭F1/F2；**按pipeline_failures=0严格Gate只有K02/K02.rerun/K05全绿**，其余空OCR typed failures；K01 run1=FAILED但steps全绿尚登记未知（报告:81），本轮未复现/断言已修；KO多页CER NOT_AUTOMATED，相似度min=0仍保守FAIL known limitation。不得简写“8/8全质量Gate通过”。 |
| `tests/core/test_rc4_revision_commands.py:145/199/271`、`test_rc4_stdio_render_preview.py:84`与RC4 Task | 测试真实新history/restore/expected冲突/并发，stdio真实NMFR→文字PNG→resource preview；Task/STATUS记录done@`0a7e0d5b`。本轮不重跑。 |
| GC2 `cea610ed` | 当前代码并祖先核对确认已集成；Plan/STATUS记1941passed+1skip/Cargo62+1ignore/Vitest140及G1-G7判别证据。旧“GC1只部分缓解”不能当全current；G7/原debt按后续runner证据解释。 |
| `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/integration-validation.log`，merge `e7d1f7f` | Python3.14/3.12各8passed、缺省CLI exit2、snapshot16项PASS、raw61hash一致；产品完整Gate NOT_RUN。DSH命令因sandbox为NOT_RUN，批准不是其现场重跑。 |

质量层剩余判断：检测训练/切换研究已完成，继续维持现生产参数；真实OCR/翻译对已选素材成功并非总体识别/翻译/修复可读性验收。G2人工GT/质量审阅、译文/SFX质量样本与learned inpainting都应单列目标和预算，不能由API成功或export存在替代。

## 5. 推荐的完整 Core 任务切片与依赖

以下是规划候选，需Codex纳入Plan、STATUS、Task冻结base/owner/reviewer/worktree/allowed_paths后才能实施。优先串行冻结共享契约；产品四页不增一级页面。Owner/Reviewer明确分离。

| 候选 | 依赖/推荐顺序 | Owner / Reviewer / Integrator | 最小交付与 Gate |
|---|---|---|---|
| **P-CORE-COMMAND-DESIGN**：冻结导入、Run、恢复、Reader/Export基础命令与host授权 | 首选下一步；已有M2-C1/RC4/Nav/GC2 done | Codex / DeepSeek Harness / Codex | 准确DTO/errors/allowlist与生命周期、worker/快照/控制恢复设计；路径/credential安全边界；明确当前1×1stub/Qt/PDF与settings生效点。只读设计，不改生产；独立review+集成后释放实现。 |
| **P-IMPORT-CORE-ADAPTER**：正式真实图片decoder | 前一设计中格式/尺寸/资源预算冻结 | Antigravity / DSH / Codex | 替换生产导入stub，沿已有ImageDecoder Port；真JA/KO/大图/损坏图尺寸与拒绝、source hash/Managed Copy零损；不自动新增依赖。PDF/MOBI只在明确格式预算获准后单独实现。 |
| **P-LIBRARY-IMPORT-COMMANDS**：书/章创建与受控导入 | DESIGN+ADAPTER | Antigravity（Python/host seam）/ DSH / Codex；Qoder另持前端实现Task | 新库创建→用户选文件→token授权→Core copy/partial报告→重启可见；取消/去重/坏图/源不变/越权路径拒绝。Core/Rust/React分写集合；产品真实invoke Gate。 |
| **P-SETTINGS-PROVIDER-CREDENTIALS**：provider/profile/binding与vault入口 | DESIGN；可在不交叠路径时与Import后续分支排期 | Codex冻结共享seam；Antigravity实现Core；Qoder实现UI；DSH审查 | endpoint/model/profile/binding选择、credential引用存删、连接测试、readiness；secret不走普通settings/log/event；旧Run快照固定、新Run确实用新配置；缺key/endpoint typed、重启恢复。冻结runtime重载，无隐式模型下载。 |
| **P-RUN-LIFECYCLE-CORE**：正式异步Run提交/投影/控制恢复 | DESIGN+IMPORT+SETTINGS最小链 | ZCode / DSH / Codex | reuse PipelineService/SQLite；accepted即时返回、单个受控执行worker、GetRunSnapshot/GetTaskProjection、pause/stop/continue/restart/abandon/retry。运行时查询不堵塞、kill/restartINTERRUPTED、旧成果/人工/Lock/pin零损；生产stdio/Tauri测试+mock确定性产品loop。 |
| **P-WORKBENCH-PIPELINE-UI**：前端任务进度/失败/恢复与最小完整执行 | RUN Core+Qoder先冻结UI行为 | Qoder / DSH或Codex（非作者） / Codex | 翻译本页/选择/章范围、持久projection、control能力、失败重试、重启恢复提示；UI不自算权威状态。应用invoke真实E2E及可读图像检查，费用API不自动重试。 |
| **P-REGION-EDIT-COMMANDS**：手工译文/几何/增删/锁pin | DESIGN+Run写保护冻结；沿RC4/retype | Antigravity Core＋Qoder UI独立Task / DSH / Codex | 复用RegionEditingService、expected revision、防覆盖、Lock、用户origin、历史pin；人工保存→rerender→Reader/export一致。merge/split/高级绘制后续按产品取舍，不一次全放开。 |
| **P-READER-PROGRESS-COMMANDS**：Reader投影与进度 | DESIGN+导航/资源已done；译文模式依赖RUN | Antigravity Core＋Qoder Reader / DSH / Codex | 当前translated/original资源、缺图/stale状态、chapter/page/scroll持久进度；重启/跨章与长条页恢复，资源撤销/替换不串页。复用ReadingService。 |
| **P-EXPORT-COMMANDS**：PNG/ZIP最小导出与谱系 | DESIGN+READER/RUN当前revision链 | Antigravity / DSH / Codex；Qoder表单单Task | 受控输出选择、后台export/cancel/history/repeat、stale/missing判定与谱系；同current revision Reader像素/导出hash一致、覆盖/失败取消保目标与源。PDF单独adapter/闭包Gate，无PDFComposer不记PASS。 |
| **P-MAINTENANCE-RECOVERY**：回收站/备份恢复安全命令 | DESIGN+RUN worker生命周期；恢复需全部连接Gate | Antigravity / DSH / Codex | 软删/还原/受控purge，SQLite备份/校验/pre_restore/rollback，managed缺失报告；恢复前停写/排空/reassemble。明确DB-only与全库备份产品边界，用户决定是否包含原图副本；不能冒充完整漫画库备份。 |
| **P-CORE-HEADLESS-PIXELS**：完整pipeline/document像素adapter去Qt | DESIGN+真实用户最小链；可先审计选择替换面 | Antigravity / DSH / Codex | 仅替换image source/crop/PNG/document render ports，不碰领域；JA/KO真实图与NMFR、render、导出产物/坐标一致，memory/time域预算。现用Pillow已安装可优先；纯Qt-free Gate必须在拒绝PySide6环境实跑真实pipeline。 |
| **P-QUALITY-CLOSURE**：真实质量缺口与高级修复研究 | 正式用户链+固定case/GT/预算；用户审阅明确 | DSH研究，Antigravity已冻结实现，Qoder质量操作UI / 非作者Reviewer / Codex | 首先核K01 terminal异常是否仍存在；JA/KO代表GT、空OCR/零检测语义、remote确定性known limitation、SFX/译文/修复/渲染逐项Gate。learned修复先选一候选真模型/spike，不一次造四种。当前未授权新API成本/下载/用户审核不能记通过。 |
| **P-DESKTOP-RELEASE-CORE-E2E**：正式用户链发布收口 | 以上所选产品scope均独立review集成后 | Codex / DSH / Codex | 干净/批准的本机Windows正式安装包，从新库完成import→configure→run→kill/recover→manual→reader→export；五入口閉包/第五assertion R003、真实OCR依赖/权重、credential、source/Lock/pin/managed/hash/退出复核；未承诺格式/model明确保持N/A/NOT_RUN而非虚报。 |

最小可用链可先只做图片→现真实基线检测/OCR/remote翻译→基础修复→render→PNG/ZIP；复杂文档、learned修复、全库备份与纯headless完全去Qt不应阻塞已经冻结的小切片，是否进入发布scope由用户裁决。数据保护、恢复、secret、无越权路径不可删减。

## 6. 可直接转发的下一任务准备

**Task**：`P-CORE-COMMAND-DESIGN`（PLANNED_PLACEHOLDER，只读设计，非释放）。**Agent**：Owner=Codex；Reviewer=DeepSeek Harness（非作者）；Integrator=Codex。**Recovery point**：审计库`G:/CODEX/New Manga`、branch=`main`、审计base/head=`e4242ecd419eb0eea098d2f63b40f709aa5caeea`；实施worktree待Codex创建，正式base/head须释放时重查，不复用聊天推断。**Scope**：先建议仅新Task、Task-local verification/设计稿；允许路径正式冻结后写入。`src/**`、`apps/**`、`tests/**`、Schema、依赖、权重、真实用户数据禁改；共享M2-C1/契约修订由Codex单独明确授权。**Deliverables**：生产命令事实表、导入/run/control/recovery/reader/export/credential DTO与error表、最小异步机制、host capability设计、分写集合Task清单/依赖、planned test矩阵、独立Review/Handoff。

**Forwardable instruction**：

> 在唯一仓库 `G:/CODEX/New Manga` 为 `P-CORE-COMMAND-DESIGN` 准备只读设计冻结。审计base/head为 `e4242ecd419eb0eea098d2f63b40f709aa5caeea`，branch `main`；开始时重查STATUS/Plan/HEAD/dirty/common-dir，正式worktree待Codex创建。本任务尚未释放，不实施生产修改。追踪 `bootstrap/core_service.py`、`core_assembly.py`、`application/tasks/service.py`、importing/editing/reading/export/maintenance服务、Rust生产allowlist与M2-C1 Proposal；先冻结真实图片导入/host文件授权、Run提交accepted与worker/持久snapshot/control/recovery、provider绑定/secret/生效点，再给Reader/Export最小命令与范围。明确1×1decoder、styles stub、Qt像素源、PDF未注入、learned修复implements=False限制。交付新Task-local设计与分切片/Owner/依赖/Gate建议，生产/Schema/依赖/用户数据零写；所有planned/NOT_RUN不得写PASS。由真实非作者DSH审查固定设计head，Codex集成后再逐Task释放。不得重开Legacy、复制完整业务状态机或派发外部实施。

**Verification**（设计期可复制、只读）：`git rev-parse HEAD`、`git status --short --branch`、`git rev-parse --path-format=absolute --git-common-dir`、`rg -n 'command ==|command in' src/bootstrap/core_service.py`、`rg -n 'StartRun|GetRunSnapshot|ControlRun|StartExport|Credential' doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`。实现期候选定向验证命令：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/core tests/m2_acceptance tests/pipeline tests/storage -q`，只在释放范围触碰相关模块时选子集；native/React/真实图片/安装包命令由对应正式Task冻结，当前全部planned/NOT_RUN。逐次日志必须包含解释器/shell/head/EXIT和skip原因；同commit代码独立Review+集成后Gate才能done。

## 7. 未覆盖范围与审计限制

没有运行测试、真实OCR/翻译/修复质量、安装包、GPU/EP、性能/内存、备份恢复、用户库文件检查；没有审完整Rust协议安全实现/React视觉交互/打包闭包（由其他专题审计处理）。本报告对这些只定位seam与必须Gate。现有quality report的人工质量表未逐图审阅，K01异常仅持久证据候选，不声称当前可复现。PDF/MOBI raster、字体排版、Webtoon streaming与TM/constraints合并算法没有逐行全审；沿用能力成立但完整产品验收待各Task。

本次不是正式独立Review批准，不改变任何Task状态、Scope或授权。推荐下一步为Codex先冻结`P-CORE-COMMAND-DESIGN`并纳入规划；没有已释放的实施Task，当前无需下一步实施操作。
