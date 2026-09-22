# Architecture / Data / UI / Flow 地图

基线：2026-09-22，真实代码逆向部分见
[PROJECT-AUDIT-2026-09-22](../verification/PROJECT-AUDIT-2026-09-22.md)。下文 D01～D08
对应 [文档索引](00_INDEX.md)；旧的 2026-09-13 接管图仍保留为历史对照。

**证据边界：本文件现在同时保存当前 As-Is 与历史 To-Be 视图。凡标记
`Current As-Is` 的内容来自 2026-09-22 master 源码、测试和 Git；凡标记
`To-Be` 的内容仍是目标设计，不能当作实现证据。**

## Current As-Is：master @ `4dfe9e7`

证据：[项目全景审计](../verification/PROJECT-AUDIT-2026-09-22.md)、
`src/`、`tests/`、[RepoWiki map](../wiki/repowiki/repo-map.json)。当前主线已具备
Python/PySide6 QML 桌面骨架、SQLite v3/Managed Copy、书架/工作台/阅读器/设置
四个一级路由、Pipeline/Run 持久化、Region 编辑、导入/导出与 Provider 接缝；
真实远程 Provider 质量、T1.2.1 设置交付和 Windows clean-machine release 仍未闭环。

~~~mermaid
flowchart TB
    QML["src/ui/qml\n四个一级页面"] --> VM["src/ui/viewmodels\nQObject ViewModels"]
    VM --> APP["src/application\nUse cases / settings / pipeline"]
    APP --> DOMAIN["src/domain\nBooks / Pages / Regions / Tasks"]
    APP --> PORTS["src/ports\nRepository / Provider / Network contracts"]
    INFRA["src/infrastructure\nSQLite / filesystem / import / render / provider / transport"] -. implements .-> PORTS
    INFRA --> DB[(SQLite v3)]
    INFRA --> FS[(Managed Copy / revisions / artifacts)]
    INFRA --> NET["Network / Credential / Provider adapters"]
    BOOT["src/bootstrap/app.py"] --> APP
    BOOT --> INFRA
    TESTS["tests/\n1077 collected on current main"] -. verifies .-> APP
    TESTS -. verifies .-> INFRA
~~~

当前真实依赖方向：`ui → application → domain/ports`；
`infrastructure` 实现 ports 并由 `bootstrap` 装配。架构守卫测试禁止
application 反向依赖 infrastructure；QML 不直接访问数据库、文件或模型。

## Historical Stage A As-Is：2026-09-13

以下段落是初始接管时的历史快照，不再描述当前源代码。

~~~mermaid
flowchart LR
    R["G:/CODEX/New Manga"] --> G["Git 已初始化 / master unborn"]
    R --> D["doc/01-08：8 份目标文档"]
    R --> H["本次新增接管与规划文件"]
    D -. "不代表已有实现" .-> N["无 src / tests / DB / QML / 构建配置"]
~~~

| 要求视图 | 真实代码生成状态 | 当前可交付来源 |
|---|---|---|
| System / Technical Architecture | BLOCKED_NO_SOURCE | D01/D02 的目标边界 |
| ER / Data Model | BLOCKED_NO_SCHEMA | D03 的逻辑实体 |
| Screen / Screen-Action / UI Interaction / Feature-UI / UI-to-Service | BLOCKED_NO_UI_SOURCE | D05 的明确映射 |
| User Flow / State Machine / Sequence | BLOCKED_NO_RUNTIME | D04/D06 的目标协议 |

后续 TASK-026 在真实源码上补充每个节点/动作对应的文件、符号、测试和 commit；不存在的节点仍保持目标状态。

## 1. System Architecture（To-Be）

来源：[D01 §1～3](01_FUNCTIONAL_ARCHITECTURE.md)、[D02 §13](02_TECHNICAL_ARCHITECTURE_.md)、D07 §69/87～89。图中外部服务均为用户配置后的能力，不表示当前已接通。

~~~mermaid
flowchart LR
    U["本机单用户"] --> APP["New Manga Windows 桌面应用"]
    SOURCE["用户选定源文件"] -->|"只读导入 / Managed Copy"| APP
    APP --> DB[("SQLite 结构化数据")]
    APP --> FS[("Managed 图片 / Mask / Revision")]
    APP --> SEC["受保护 Credential Store"]
    APP --> LOCAL["可选本地模型 / AI 服务"]
    APP --> NET["统一 Network / Proxy"]
    NET --> REMOTE["用户配置的远程 Provider / 资源下载"]
    APP --> OUTPUT["单图 / ZIP / CBZ / PDF / 文本"]
~~~

本产品是单用户本机应用（D03 §0），三 Agent 开发协作不是产品内的多用户/权限系统。

## 2. Technical Architecture（To-Be）

来源：[D02 §2/6/7/13/16](02_TECHNICAL_ARCHITECTURE_.md)、[D06 §1/80～84](06_TRANSLATION_PIPELINE.md)。箭头区分调用与适配实现；端口数量沿用既有目标，不表示已经创建这些模块。

~~~mermaid
flowchart TB
    Q["QML：四个一级页面 / 固定面板 / 悬浮窗"] --> VM["QObject ViewModel / Observable Model"]
    VM --> APP["Application：导航 / 书架 / 编辑 / 阅读 / 导出"]
    VM --> TASK["Task Manager / Pipeline Orchestrator"]
    APP --> DOMAIN["Domain：内容 / Lock / Revision / 约束"]
    TASK --> DOMAIN
    APP --> PORT["Repository / Provider Ports"]
    TASK --> PORT
    TASK --> WORK["后台 Worker / CPU-GPU-Network-IO 调度"]
    WORK --> PORT
    ADAPTER["SQLite / Filesystem / Provider Adapters"] -. "实现契约" .-> PORT
    ADAPTER --> SQL[("SQLite")]
    ADAPTER --> FILE[("Managed Storage")]
    ADAPTER --> NET["Network / Proxy / Credential"]
    ADAPTER --> MODEL["Device / Model Manager：可选依赖延迟加载"]
~~~

UI 不直接访问 SQL/文件/模型；Domain 不依赖 Qt/SQLite/httpx/ML。Windows 桌面内部主通道是 Python/Qt 调用，目标不要求 Flask/localhost 总线。依赖版本、实际包名、进程隔离方式交 TASK-004/005 决定。

内部处理依赖来自 D06 §3/10：

~~~mermaid
flowchart LR
    ORIGINAL["Original"] --> DET["Detect / Region"]
    DET --> OCR["OCR"]
    OCR --> TERM["Term Extract"]
    TERM --> FREEZE["准备目标范围后冻结约束"]
    FREEZE --> TRANS["Translate + Context + TM"]
    DET --> COLOR["Color / Source Style"]
    DET --> SEG["Text Segmentation"]
    SEG --> MASK["Mask Refinement"]
    MASK --> INPAINT["Inpaint Router / Provider"]
    TRANS --> RENDER["Render"]
    COLOR --> RENDER
    INPAINT --> RENDER
    RENDER --> SAVE["保存 / current / StageState"]
~~~

这是目标 DAG，不要求第一版并行实现；每步安全提交与最终 Save 的精确定义仍见 G13。

## 3. ER / Data Model（To-Be 逻辑模型）

来源：[D03 §2/38/39](03_DATA_MODEL.md)与 [TASK-002 契约 §2～4](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md)。以下只展示主从关系；可空字段、复合 FK 与 current 指针以契约为准，不是已实现 SQL Schema。

~~~mermaid
erDiagram
    BOOK ||--o{ CHAPTER : contains
    CHAPTER ||--o{ PAGE : contains
    PAGE ||--o{ REGION : contains
    BOOK ||--o{ BOOK_TAG : tagged
    TAG ||--o{ BOOK_TAG : links
    CHAPTER ||--o{ READING_PROGRESS : tracks_modes
    PAGE ||--o{ PAGE_STAGE_STATE : tracks
    REGION ||--o{ REGION_STAGE_STATE : tracks
    REGION ||--|| REGION_TEXT_STYLE : current_style
    REGION ||--o{ REGION_REVISION : history
    MEDIA_ARTIFACT ||--o{ ARTIFACT_REVISION : versions
    TRANSLATION_CONSTRAINT ||--o{ CONSTRAINT_REVISION : history
    PIPELINE_RUN ||--o{ PIPELINE_RUN_TARGET : freezes
    PIPELINE_RUN ||--o{ PIPELINE_TASK : schedules
    PIPELINE_TASK ||--o{ STEP_RUN : executes
    PROVIDER_PROFILE ||--o{ PROVIDER_BINDING : selected_by
~~~

| 数据族 | 目标实体 / 字段 | 归属与关键规则 |
|---|---|---|
| 内容 | Book、Chapter、Page、Region、Tag/BookTag | SQLite；无 Volume；Webtoon 一张长图是一逻辑 Page |
| Region 文本 | ocr_text、machine_translation、edited_translation、final_translation | 人工确认值受保护；渲染使用 final |
| 保护与版本 | Page/Region/Translation/Inpaint Lock；RegionRevision、ConstraintRevision | 开始和提交时检查；具体 current/Pin/Review Schema 待补齐（G07/G08） |
| 媒体 | MediaArtifact.current_revision_id → ArtifactRevision | 文件在 Managed Storage；metadata/hash/provenance 在 SQLite；Page/Region 归属见 D03 §16 |
| 状态 | PageStageState、RegionStageState | 当前有效性；overall_status 是派生缓存 |
| 知识 | TranslationConstraint、TranslationMemory | 约束 Chapter > Book > Global；TM 仅接纳确认内容 |
| 执行 | Run、Target、Task、StepRun | Run 快照；任务进度从这些对象派生，不建立进度业务表 |
| 配置 | ProviderProfile、ProviderBinding、NetworkProfile、SettingOverride | 绑定按 scope 解析；实际 Secret 在 Credential Store |
| 用户成果 | ReadingProgress、ExportHistory、RecycleBinEntry | 两种阅读模式独立；软删除带 batch |
| 可靠性 | SchemaMigration、ApplicationMetadata、BackupRecord、CacheQuotaState、ModelInstallationState、AuditEvent | Infrastructure metadata；Cache 可重建，不能作为唯一业务真值 |
| UI 本机状态 | WindowLayoutState | 窗口位置，不复制漫画业务数据 |

目标实体字段见 D03；G06～G13 的参照完整性与写回不变量见 TASK-002 契约，实际 SQL 在 TASK-006 落实，不凭图猜测。

## 4. Screen Map（To-Be）

来源：[D05 §2～5/7/16/37/43](05_UI_MAPPING.md)。

~~~mermaid
flowchart TB
    SHELL["AppShell / 一级导航"] --> B["bookshelf：默认"]
    SHELL --> W["workbench"]
    SHELL --> R["reader"]
    SHELL --> S["settings"]
    B --> BP["Toolbar / BookGrid-List / BookDetail / ChapterList"]
    W --> WP["Toolbar / PageList / Viewer / RegionInspector / TaskProgress"]
    R --> RP["Toolbar / ReaderNav / Viewer"]
    S --> SP["固定分类 / 设置内容"]
    B -. "辅助内容" .-> F["Floating Tool Window / Dialog"]
    W -. "辅助内容" .-> F
    R -. "辅助内容" .-> F
    S -. "辅助内容" .-> F
~~~

作品详情、术语、TM、Revision、任务详情、导入导出、Provider/网络编辑、回收站均不是第五个一级页面。Floating Window 支持双屏；固定 Panel 本身不直接脱离主窗口（D05 §64）。

## 5. Screen-Action Map（To-Be）

来源：D05 §8～14/18～36/38～55/56；命令行为以 D06 §34～47 为准。下表没有实际 handler 路径。

| Screen / 容器 | 动作 | 对象 / 结果 | 关键约束 |
|---|---|---|---|
| 书架 Toolbar | 新建/编辑、搜索、收藏/归档、标签 | Book、Tag/BookTag | 标签删除不删作品 |
| BookDetail / ChapterRow | 创建/排序章节；进入翻译/阅读 | Book+Chapter 上下文 | 只有此处业务跳转到同级页面 |
| 页面管理 / ImportWindow | 图片/文件夹/PDF/MOBI 导入 | Page+Managed Original | 预览顺序与重复策略，源文件不变 |
| PageList | 单选/Ctrl/Shift、排序、锁定/删除 | 当前 Chapter 的 Page | 不跨章节多选 |
| PageList / Toolbar | 全部、跳过已翻译、选页、单页翻译 | PipelineRunTarget 快照 | 改 UI selection 不改变任务范围 |
| PageList 菜单 | reocr / reinpaint / rerender | 当前范围的对应命令 | rerender 缺 Clean 要阻止，不能偷偷重修 |
| Viewer / Inspector | 选择/新建/合并/拆分 Region、编辑几何 | Region+RegionRevision | 按逻辑原图坐标 |
| Inspector 文本/样式 | 保存、确认 final、样式、Lock | Region/TextStyle/Revision；确认后可写 TM | 人工译文自动保护；Dirty 处理 |
| Inspector 命令 | OCR、重译、重全翻译、重修、重渲染 | 单 Region Run | 专项 Lock 临时覆盖须明确确认 |
| TaskProgress | 暂停/继续/停止、筛选/定位 | Run 控制请求 / Task Projection | 成果保留；安全边界 |
| TaskDetail | 错误诊断、失败页重试 | 新 Run 引用旧 Run | 不改写旧 Run 历史 |
| Constraint / TM Window | 人工维护、候选确认/拒绝、查历史 | Constraint/TM | 层级优先；未确认机器文本不入 TM |
| Reader Toolbar / Viewer | 模式、方向、缩放、继续阅读 | ReadingProgress | Original/Translated 独立；Webtoon 按宽 |
| Workbench / Reader ExportWindow | 五种格式导出 | ExportHistory/产物 | stale 提示、明确覆盖策略 |
| Settings / Editors | Provider、Network、连接测试、样式 | 配置/凭据引用 | 显示来源；代理失败默认不直连 |
| Revision / Recycle / Backup | 恢复、Pin、清理、备份 | 版本/回收 batch/Backup | 危险确认，保留保护集合；Pin 范围待 G08 |

## 6. UI Interaction Map（To-Be）

来源：D05 §19/21/31～35/55/58/63。

~~~mermaid
flowchart LR
    B["BookDetail / ChapterRow"] -->|"进入翻译"| W["Workbench"]
    B -->|"进入阅读"| READER["Reader"]
    W --> PAGE["PageList"]
    PAGE -->|"选择 Page"| VIEW["Viewer"]
    VIEW -->|"选择 Region"| INS["Inspector"]
    INS -->|"保存或提交命令"| APP["Edit Use Case / Task Manager"]
    APP --> PROJ["同一 Task Projection"]
    PROJ --> PAGE
    PROJ --> PROGRESS["TaskProgressPanel"]
    PROGRESS -->|"当前页 / 失败筛选"| PAGE
    PROGRESS -->|"查看详情"| DETAIL["TaskDetail Floating Window"]
~~~

Viewer 当前页和 Pipeline 当前页可以不同。切页/切 Region 前处理 Dirty；任务控制不通过 QML 直接写状态。

## 7. Feature-UI Matrix（To-Be）

来源：D05 §57，补充其 §43/48/50/52/53 的明确设置入口。所有格子均表示目标归属，非完成标记。

| 功能 | 书架 | 工作台 | 阅读器 | 设置 | 辅助窗口 |
|---|---|---|---|---|---|
| Book / Chapter / Tag | 主入口 | — | — | — | 编辑/标签 |
| Page / 导入 / 排序 | 入口 | PageList | — | — | 页面管理/导入 |
| 阅读进度 | 摘要 | — | 主入口 | — | — |
| Detection / OCR / 翻译 | — | 执行 | — | Provider/能力配置 | 任务参数 |
| 翻译约束 / TM | 入口 | 摘要/匹配 | — | — | 管理 |
| Region / Lock / 校对 | — | Viewer/Inspector | — | — | Revision |
| Mask / Inpaint | — | Inspector | — | 修复配置 | Revision |
| Rendering / 自动字号 | — | Inspector | — | 全局默认 | — |
| 任务进度/控制 | — | 底部固定 | — | 并发设置 | TaskDetail/失败项 |
| 阅读 | 跳转入口 | 结果入口 | 主入口 | — | 阅读设置 |
| Export | — | 入口 | 入口 | — | 导出 |
| Provider / Network | — | 临时覆盖/状态 | — | 主入口 | 编辑/连接测试 |
| Revision | — | 入口 | — | 清理策略 | 历史/对比 |
| Recycle Bin | 入口 | — | — | 入口 | 恢复/永久删除 |
| 模型/GPU/缓存/备份/Plugin | — | 执行反馈 | — | 分类内容 | 依功能详情；扩展契约待定 |

## 8. UI-to-Service Mapping（To-Be）

来源：[D05 §59](05_UI_MAPPING.md)。表中的类名是原始设计建议，不代表当前文件或 API 存在。

| UI | ViewModel | Application / Use Case |
|---|---|---|
| AppShell | NavigationViewModel | Navigation Service |
| BookshelfView | BookshelfViewModel | Library Use Cases |
| BookDetailPanel | BookDetailViewModel | Book / Chapter Use Cases |
| PageManagementWindow | PageManagementViewModel | Import / Page Use Cases |
| WorkbenchView | WorkbenchViewModel | Translation Application Service |
| PageListPanel | PageListViewModel | Page Query / Task Projection |
| ViewerCanvas | ViewerViewModel | Page / Artifact Query |
| RegionInspector | RegionInspectorViewModel | Edit / Review Use Cases |
| TaskProgressPanel | TaskProgressViewModel | Task / Queue Manager |
| TaskDetailWindow | TaskDetailViewModel | PipelineRun / Task Query |
| ConstraintWindow | ConstraintViewModel | TranslationConstraint Use Cases |
| TranslationMemoryWindow | TranslationMemoryViewModel | TM Use Cases |
| ReaderView | ReaderViewModel | Reader Use Cases |
| SettingsView | SettingsViewModel | Settings Service |
| ProviderEditor | ProviderProfileViewModel | Provider Config Service |
| NetworkEditor | NetworkProfileViewModel | Network Config Service |
| ExportWindow | ExportViewModel | Export Service |
| RecycleBinWindow | RecycleBinViewModel | Recycle Bin Use Cases |
| RevisionWindow | RevisionViewModel | Revision / Artifact Use Cases |

## 9. User Flow（To-Be）

来源：[D04 §2/47～51](04_USER_FLOW.md)。进入阅读/导出不是必须先执行全部 AI 的硬性条件；已有成果可直接使用。

~~~mermaid
flowchart TB
    START["启动 / DB与恢复检查"] --> BOOK["默认书架：选择或新建 Book"]
    BOOK --> CH["选择或新建 Chapter"]
    CH --> IMPORT["导入 / 排序 Page"]
    IMPORT --> W["进入工作台"]
    W --> RUN["选择范围和命令 / 保护检查 / 提交任务"]
    RUN --> PROGRESS["进度 / 暂停 / 继续 / 停止"]
    PROGRESS --> REVIEW["检查结果 / 人工校对"]
    REVIEW --> SAVE["保存 Revision / final / 必要时重渲染"]
    SAVE --> READ["Reader：Original 或 Translated"]
    SAVE --> EXPORT["导出"]
    CH -->|"直接进入阅读"| READ
    PROGRESS -->|"失败项"| RETRY["诊断 / 新 Run 重试失败目标"]
    RETRY --> PROGRESS
~~~

## 10. State Machine（TASK-002 最小契约已冻结；尚未实现）

来源：[TASK-002 契约 §5～6](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md)、D03 §22.1/24.1、D06 §59～65/73、D08 AC-RETRY。失败页重试与 Restart 都创建新 Run，但目标与快照规则不同；原 failed 不回到 pending。

~~~mermaid
stateDiagram-v2
    [*] --> pending
    pending --> running: 调度
    pending --> blocked: 无可运行单元且存在可解除阻塞
    blocked --> pending: 条件解除并重新规划
    blocked --> cancelled: stop
    running --> paused: pause请求且到安全边界
    paused --> running: continue并验证断点
    paused --> cancelled: stop
    running --> completed: 正常终结且无失败
    running --> completed_with_failures: 批量终结且部分失败
    running --> failed: Run级致命错误
    running --> blocked: 剩余单元仅有可解除阻塞
    running --> cancelled: stop并安全结束
    running --> interrupted: 异常退出后识别
    interrupted --> running: 用户继续并通过恢复检查
    interrupted --> cancelled: Abandon
    completed --> [*]
    completed_with_failures --> [*]
    failed --> [*]
    cancelled --> [*]
~~~

Restart 不构成原 Run 的状态转换：原 Run 保持 `interrupted` 并记录 `interruption_disposition=restarted`，新 Run 独立创建。

Continue 使用原 Run/快照；Restart 保留原 interrupted Run并创建新 Run；Abandon 将原 Run 置 cancelled。Stop 与最后一步并发时按事务提交顺序确定 completed 或 cancelled，已提交成果均保留。

StageState 的已确认有效性关系来自 D03 §10、D06 §25～30/88：

~~~mermaid
stateDiagram-v2
    [*] --> not_started
    not_started --> pending
    pending --> running
    running --> completed: 安全提交
    completed --> stale: 相关上游变化
    stale --> pending: 命令允许重跑
    running --> failed: 本次执行失败
    running --> interrupted: 无安全提交而中断
~~~

此图只表达关键路径；完整枚举与聚合优先级见 TASK-002 契约 §5。failed/interrupted 不删除旧可用 Revision；StageState、StepRunStatus 与 ReviewState 已分层。UI Dirty 状态由 D05 §55 单独定义，不复用 Pipeline 状态。

## 11. 关键 Sequence Diagram（To-Be）

### 11.1 Managed Copy 与导入提交

来源：D02 §8、D07 §38；细粒度回收协议待 G13。

~~~mermaid
sequenceDiagram
    actor U as 用户
    participant UI as ImportWindow / VM
    participant APP as Import Use Case
    participant FS as Managed Storage
    participant DB as Repository / SQLite
    U->>UI: 选择文件与目标 Chapter
    UI->>APP: 提交导入设置
    APP->>FS: 只读源文件，复制到受控路径
    FS-->>APP: 校验、Hash、尺寸
    alt 复制或验证失败
        APP-->>UI: 诊断错误，不建立可处理 Page
    else 受控原图完整
        APP->>DB: 短事务提交 Page / Artifact metadata
        DB-->>APP: Commit
        APP-->>UI: 更新页面列表，缩略图异步生成
    end
~~~

### 11.2 批量翻译与范围冻结

来源：D06 §10/13～18/48～50/84。Provider 只返回结果，由应用层验证与写回。

~~~mermaid
sequenceDiagram
    participant UI as Workbench / VM
    participant PIPE as Pipeline
    participant CTX as Context / Constraint
    participant P as Provider Adapter
    participant DB as Repository
    UI->>PIPE: 命令与选中目标
    PIPE->>DB: 固化目标、设置、Provider snapshot
    PIPE->>CTX: 补齐必要 OCR / 术语准备
    CTX-->>PIPE: effective constraint snapshot
    PIPE->>CTX: 构建有明确 Write Scope 的上下文
    CTX-->>PIPE: Context Bundle / 目标 Region IDs
    PIPE->>P: 按冻结配置翻译
    P-->>PIPE: 结构化输出
    PIPE->>PIPE: 校验输出映射、Lock与输入Revision
    PIPE->>DB: 仅提交目标范围的新 Revision
    DB-->>UI: 通过共享投影通知状态
~~~

### 11.3 后台结果与人工修改冲突

来源：D03 §24.1、D06 §89～91、D08 AC-CONFLICT-001、TASK-002 契约 §8。Candidate 与 ReviewState 已冻结，尚未实现。

~~~mermaid
sequenceDiagram
    participant STEP as 后台Step
    participant P as Provider
    participant DB as Repository
    participant EDIT as Edit Use Case
    actor U as 用户
    STEP->>DB: 读取输入Region Revision 10
    STEP->>P: 发起计算
    U->>EDIT: 保存人工编辑
    EDIT->>DB: 提交Revision 12和Lock
    P-->>STEP: 返回针对Revision 10的输出
    STEP->>DB: 提交时检查Lock及当前Revision
    DB-->>STEP: 当前为12，不能覆盖
    STEP-->>U: 保留人工值，记录冲突待检查
~~~

### 11.4 Artifact 原子性与失败保留

来源：D03 §17、D06 §24/88/94、D07 §30～32、TASK-002 契约 §8。不可变正式路径和孤儿文件处理语义已冻结；具体命名与实现由 TASK-006 定义。

~~~mermaid
sequenceDiagram
    participant STEP as Inpaint / Render Step
    participant FS as Managed Storage
    participant DB as SQLite
    STEP->>FS: 临时输出、关闭、验证、Hash
    STEP->>FS: 发布新版本文件
    alt DB提交前失败或崩溃
        Note over FS,DB: 旧current保持；新文件不自动成为current
    else 元数据提交成功
        STEP->>DB: 短事务：新增Revision、更新current和StageState
        DB-->>STEP: Commit成功
    end
~~~

### 11.5 Pause / Stop 与失败页 Retry

来源：D06 §58～65/95、D08 AC-PAUSE/STOP/RETRY。

~~~mermaid
sequenceDiagram
    actor U as 用户
    participant M as Task Manager
    participant W as Worker
    participant DB as Task Repository
    U->>M: Pause 或 Stop
    M->>DB: 保存Run控制请求
    M->>W: 禁止启动新的Step/Page
    W->>DB: 当前不可中断Step安全完成
    alt Pause
        M->>DB: Run paused
        U->>M: Continue
        M->>W: 复查有效性，从断点继续
    else Stop
        M->>DB: 剩余任务cancelled，保留成功成果
    end
    Note over U,DB: 以下是已结束且存在失败页的另一个场景
    U->>M: Retry Failed Pages
    M->>DB: 新Run，只含失败目标，记录source_run_id
    M->>W: 复用有效上游，从失败或stale处开始
~~~

未描述的边界不等于默认成功。完整状态表、Error/Skip reason、校对/Pin、SFX 和分支合成协议见 Gap Register 对应任务。
