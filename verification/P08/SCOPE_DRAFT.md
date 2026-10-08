# P08 产品范围与验收草案

状态：DRAFT / 等待用户裁决与非作者 Review。本文是 P08 的审查材料，范围生效以 Plan 与正式 Task 为准，不修改任何冻结契约或既有产品裁决。

## 当前完成位置

已完成整体代码/任务审计和 P01–P21 路线规划。本轮完成范围草案准备；P08 尚未 done，后继产品实施未释放。现有新架构已登记任务105项收口；196节点历史台账是固定审计快照，不是最新 Task 文件数。不能用这两项数字计算产品完成率。

生产能力复核输入：`ab2f813c0ce311a6712002cafd852b9e7a258380`；与审计输入 e4242ecd 比较，src/apps/tests/packaging 无差量。复用[Core审计](../PROJECT-ROADMAP-20261008/core-audit.md)、[Desktop审计](../PROJECT-ROADMAP-20261008/desktop-audit.md)。旧报告的人员建议由当前协作协议覆盖；Qoder不参与。

## 建议首个完整产品范围（等待批准）

建议以“四页最小用户闭环”作为首个发布目标：空库建书与导入图片 → 配置可用Provider → 翻译运行/暂停/停止/恢复 → 校对与保护 → 阅读结果与导出PNG/ZIP。这只是首个范围建议，不等于 D01/D08 所有目标能力全部完成。

`must`、`deferred`、`out` 都是本草案建议分类。已冻结的数据保护为必须遵守的现行约束；新增能力和对目标需求的延期都须用户裁决。没有裁决的条目不可改为 N/A 或 PASS。

| 能力 | 建议分类 | 实际能力与缺口 | 来源 | 后继任务与可观察验收 |
|---|---|---|---|---|
| 四页入口/默认书架/上下文保留 | must，Reader等待解冻 | App目前Console↔Workbench；Library/Settings在Console内 | D01§1/3；D04§1/15/33；D08 AC-NAV | P12/P14/P15/P17：真实窗口四页切换、空态/错误、重开上下文，不增加第五页 |
| Book/Chapter/Page基本管理 | must基本创建与列表；标签/收藏/归档等细项待裁决 | LibraryService存在，生产只读列表已接；写入口未接 | D04§3–10；D08 AC-LIB/CH/PAGE | P09/P12：空安装态建Book/Chapter、顺序稳定、失败可见；管理细项见D08逐项覆盖表 |
| 图片/文件夹导入与真实尺寸 | must | ImportImagesUseCase可复用；生产decoder恒1×1，正式导入命令缺失 | D04§8；D08 AC-IMPORT | P09/P12：PNG/JPEG受控选源，损坏/逃逸/重复/中断/Unicode判别；源hash零变化 |
| PDF/MOBI输入 | deferred建议 | 存在解析服务与Qt路径；生产闭包未资格验证 | D01§2；D04§8；D08 AC-EXT | P09预留独立格式切片；每个格式单独解析/尺寸/依赖/包内运行Gate，延期不能称全格式支持 |
| paged/Webtoon、长图预算 | must基础行为；容量边界待实测冻结 | tile/坐标基础存在，完整React Reader与长图预算未证实 | D04§9/34/35；D08 AC-WEBTOON/CAP/MEM | P09/P13/P17：一张长图仍一Page、坐标回映、按宽滚动、恢复；预算按D07原目标核验，不臆造数值 |
| 全章/选页翻译与重跑族 | must基础翻译/跳过已翻译/重OCR/重修/重渲染；单Region重全翻译单切片 | PipelineService与九步handler存在；正式StartRun/控制命令缺失 | D04§11–14/22.1/30；D08 AC-CMD/RFULL/PIPE | P11/P13/P14：开始时冻结目标，复用有效步骤，缺Clean重渲染禁止补修复；RFULL锁覆盖必须单独确认 |
| 暂停/继续/停止/失败重试/崩溃恢复 | must | 后端可复用；任务进度面板静态占位 | D04§30/31/51；D08 AC-PAUSE/STOP/CRASH/RETRY/PROGRESS | P11/P13/P14：持久接受后响应、安全边界停步、无半提交、重开恢复；UI请求响应指标沿D08 |
| Region改标/几何/增删/人工译文 | must，按命令拆切片 | 改标/历史恢复已接；文本保存/几何/增删写命令未接 | D04§18/27/32；D08 AC-REGION/TRANS/AUTO | P14：expected_revision冲突、保存后重开真实一致；自动保护人工译文，不只本地改图 |
| 四类Lock/current/pinned/Revision | must现行安全约束 | Core事务守卫存在；UI写入口需接 | D04§28/29；D08 AC-LOCK/REV/CONFLICT/ART | P13/P14/P19：所有新写入口复核锁与输入版本；失败保current、pin不清理、恢复留历史 |
| 翻译约束/术语/TM | must保护现有语义；完整管理UI建议deferred | 后端基础存在，未证明全部生产管理界面可达 | D01§3；D04§20–22；D08 AC-CONSTRAINT/TM | P10/P13/P14：未确认机器结果不写TM、不覆盖人工；完整编辑界面另裁决，不能当全部目标达成 |
| SFX策略/检测/OCR/翻译 | must保留现行能力 | 检测/OCR/翻译有真实实验；BJ13维持0.90+改标/skip；产品配置缺口 | D04§17/19；D08 AC-OCR/SFX/PROVIDER | P10/P13/P18：真实JA/KO样本、可用性与失败原因投影；不复活Manga109任务 |
| 修复与排版 | must可用基线；源样式自动提取/高质量模型待裁决 | SimpleFill/EdgeBleed真实；生产style analyzer空；learned descriptors implements=False | D04§23–26；D08 AC-STYLE/INPAINT/RENDER | P13/P18：mask/版本/文字溢出/源背景可审查；若质量不达标阻止声明支持，不默认引入ML训练 |
| Provider/凭据/网络 | must最小可用配置与安全凭据；完整代理覆盖待裁决 | 普通SFX设置已接；CredentialRef exchange缺失 | D04§38–42；D08 AC-PROVIDER/NET/SEC/SET | P10/P15：密钥不进普通DTO/日志，连接失败可见；配置生效时点/重启/替换/清除须冻结 |
| Reader/阅读进度 | must建议，当前明确不做项须新裁决 | ReadingService存在；正式Projection/SaveProgress与React Reader缺失 | D04§33–36；D08 AC-READ | P16/P17：原图/译图，paged方向/Webtoon按宽、关闭重开进度；跨页联动/页缩略图继续deferred |
| PNG/ZIP导出 | must建议 | ExportService与lineage基础存在；正式授权输出/StartExport/Cancel缺失 | D04§37；D08 AC-EXPORT | P16/P17：stale/missing策略先冻结；临时文件发布、取消清理、来源/顺序/hash、源零写 |
| PDF/CBZ/文本等导出 | deferred建议 | PDFComposer未注入生产装配；其他格式逐项资格未核 | D01§3；D04§37；D08 AC-EXPORT/EXT | P16分格式独立Gate；未测格式显示不可用，不借PNG PASS代替 |
| 回收站/诊断/维护 | must诊断与失败提示；删除/恢复建议单独切片 | Trash/diagnostics可复用，生产维护命令未接 | D04§43/44；D08 AC-TRASH/LOG/CLEAN | P15：同batch恢复、managed-only删除、current/pinned保护；不扩大全局删除范围 |
| DB备份/全库备份恢复 | deferred建议，另行选择 | 备份服务存在；新worker/连接停写恢复未接；DB备份不含Managed Copy | D04§38；D08 AC-BACKUP | P15：若选入必须停写/排空/关闭连接/reassemble/回滚＋隔离故障注入；DB-only明确不可替代全库灾备 |
| 发布/安装/模型运行 | must选定Windows环境 | 固定旧包26/26与本机裁决有效；第五入口/G7迁移/Win10资格缺口 | D07平台；D08 AC-PKG/SMOKE/OPTIONAL | P03/P06/P19/P20：fresh source/installer五入口绑定、受影响Gate；未测Win10不声明支持 |
| 插件Agent/自动更新/签名/模型训练/Legacy移除 | out首轮建议；P21可选 | 未授权新增；Legacy只留证据 | D01扩展目标；Plan现行约束 | 另行范围授权；首轮不投入，不改变这些功能的历史记录 |

## 必须裁决的选项

| 决策 | 推荐 | 替代与影响 | 当前是否已批准 |
|---|---|---|---|
| D1 产品终点 | 四页最小闭环，解冻Reader基础阅读/进度/PNG与ZIP导出 | 暂缓Reader则只能称“选定范围版本”；仍保留Reader缺口 | 否；当前Reader限制仍有效 |
| D2 扩展边界 | 首轮图片输入＋PNG/ZIP输出；暂缓PDF/MOBI/其他格式、完整TM管理、复杂修复模型、备份恢复及插件Agent | 将某项纳入必须增加独立契约/实现/验收切片，不能混进P09/P15无限范围 | 否；deferred只是草案建议 |
| D3 质量与发布 | JA与KO分别资格；先验证当前已裁决本机环境，Win10声明需实测；复杂背景不达标则限制能力声明 | 要求Win10或高质量复杂背景作为首发门槛，则相关环境/模型/真值缺失持续BLOCKED | 否；不能默认降低D07/D08要求 |

D1–D3可逐项批准或修改。即使批准范围，P08仍须非作者Review和集成检查，P09等实现仍逐Task释放。

## 质量与验收口径草案

- 安全门槛不可降级：源文件hash零变化；无静默覆盖人工/Lock/pinned；版本冲突明确返回；失败无半提交；secret泄漏零容忍。逐入口和故障注入验证，不以总测试数量替代。
- 功能门槛：所选范围的正常/失败/重启链全部有production UI与Core可复核证据；acceptance-only、mock和静态React测试分别记录，不能代替真实生产链。
- 真实质量：复用已允许素材与许可，不重新获取Manga109；JA/KO分别锁样本、标注、provider/model/权重hash、设备/参数、逐页逐步骤结果。B3 export OK不能替代terminal状态一致性；K01先核验再定性。
- 数值质量门槛尚未冻结：检测/OCR真值、翻译相似度评测方式、无字页F4与复杂背景修复标准从既有报告逐项列出缺失，再在P18资格方案独立审查。不得编造统一“90%通过率”；BJ13 0.90是当前检测阈值，不能当整个产品质量分数。
- 性能沿D07/D08目标保留：暂停请求UI≤200ms（AC-PAUSE-001），已冻结Workbench刷新≤300ms按原Task测；首次模型加载与推理耗时不混入即时交互指标。容量/长图/内存/显示缩放从对应AC逐项测，缺环境记BLOCKED、未执行记NOT_RUN，延期必须有用户决定。
- 发布矩阵每行绑定OS版本/build、CPU/GPU、Python/模型、source/head、installer SHA、实际命令与EXIT。尊重RG1本机作为净化基线的裁决；旧26/26限旧hash，不推断当前完整产品或Win10。

## 后继工作包拆分（全部未释放）

每个子Task须独立填写base/head、branch/worktree、allowlist和非作者Reviewer。以下后缀仅是草案切片标识，尚无正式Task；父编号固定P09–P20。ZCode视觉设计复用M2-UI1，在新设计Task完成Review后落UI。

| 工作包 | 先后切片与依赖 | 建议Owner / 非作者Reviewer | 拟议允许路径与Gate |
|---|---|---|---|
| P09 | contract→Core/Host真实decoder与受控来源；依赖P08裁决 | Codex→Antigravity；DSH | contract自有修订；src/application/importing、src/bootstrap、apps/desktop/src-tauri相关边界；只选定格式与最小目标，源保护/损坏/中断Gate |
| P10 | credential/config契约→Core/Host；依赖P08 | Codex→Antigravity；DSH | 自有契约、settings/provider安全接线；凭据读写与脱敏Gate，不借普通settings DTO传secret |
| P11 | durable accepted/快照/控制/恢复契约；依赖P08 | Codex；DSH | 自有契约设计与verification；不写runtime，不造第二调度器 |
| P12 | 四页导航设计切片→书架与导入UI；依赖P09＋设计Review | ZCode；DSH | frontend/library与路由最小切片；真实Tauri空库链，保留已有Workbench/SFX能力 |
| P13 | Run接线→控制→恢复；依赖P09/P11 | ZCode；DSH | src/application/tasks既有复用、bootstrap/bridge冻结边界；工作线程/连接所有权、durable状态与故障恢复Gate |
| P14 | 编辑/Lock/Pin写契约→Core→Workbench UI；进度依赖P13 | Codex→Antigravity/ZCode→ZCode；DSH | editing和Task单独指定Rust/React文件；每条写命令逐项冲突/保护，不跨层无限授权 |
| P15 | 设置UI；维护先契约→Core→UI；备份若选需P13排空 | Codex→Antigravity→ZCode；DSH | settings及已选择maintenance组件；错误/配置生效/诊断Gate，备份另切片 |
| P16 | 阅读/输出授权契约→Core；依赖Reader裁决/P13 | Codex→ZCode；DSH | application/reading/export＋桥冻结范围；进度、lineage、取消、格式逐项Gate |
| P17 | Reader设计→Reader/导出UI；依赖P16＋设计Review | ZCode；DSH | frontend拟议reader/export目录；真实结果、重开进度/长图/受控输出，禁静态mock冒充 |
| P18 | 资格方案→JA/KO真实实验；依赖P10/P13/质量裁决 | DSH；Codex或ZCode非作者 | 自有experiments/verification；素材许可、hash、阈值/真值与逐步terminal一致性；生产修复须另Task |
| P19 | 所选范围production E2E；依赖P12/P14/P15/P17/P18 | DSH；Codex非作者 | 自有验证工具/证据；按选定范围验收，正常/失败/重启/人工保护逐项，不将缺Reader称四页完成 |
| P20 | fresh Windows Gate；依赖P19/P03/P06 | ZCode；DSH；Codex集成 | 自有packaging/verification冻结范围；source/installer/五入口/环境矩阵，未知不外推 |

## 看图定位

```mermaid
flowchart LR
  A["已完成<br/>整体审计与路线规划"] --> B["P08 草案已准备<br/>当前：等待产品裁决＋独立Review"]
  B --> C["P09/P10/P11<br/>导入／凭据／长任务契约"]
  C --> D["P12/P13<br/>书架导入／后台运行恢复"]
  D --> E["P14/P15/P16/P17<br/>编辑控制／设置／阅读导出"]
  E --> F["P18/P19/P20<br/>真实质量／整体验收／发布"]
  style B fill:#fff3cd,stroke:#b58105,stroke-width:3px
```

## 下一步可转发指令

Task=P08范围裁决与草案复核；Owner=Codex，建议非作者Reviewer=DeepSeek Harness（尚未认领，不能冒充已审）。仓库G:/CODEX/New Manga，branch/worktree=main/当前主工作区，base=ab2f813c0ce311a6712002cafd852b9e7a258380，交付head用`git log -1 -- verification/P08`实测；Review工作区待Codex创建。只读src/apps/tests与既有Task/原始证据；仅写P08自有草案、Task、verification/Handoff及Codex导航。禁止Schema/依赖/冻结wire/用户数据/历史raw/他人dirty变更。先取得本文D1–D3裁决；再逐D08覆盖表审查traceability/延期/性能和质量口径，固定提交给非作者审查，执行文档链接/依赖/路径检查；缺陷记changes_requested、缺环境NOT_RUN/BLOCKED。通过Review与集成后P08才done；P09以后仍需分别释放。
