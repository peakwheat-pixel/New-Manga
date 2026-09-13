# 02 目标技术架构（Target Technical Architecture）

> 本文件定义新漫画翻译软件的 **To-Be 技术架构**，用于指导后续实现、重构、测试和模块边界控制。
> 本架构与 `01_FUNCTIONAL_ARCHITECTURE.md`、`03_DATA_MODEL.md` 保持一致：**书架、工作台、阅读器、设置为四个同级一级页面**；软件默认启动进入书架。书架中的章节可跳转到工作台或阅读器；其他业务内容优先使用固定面板，不适合固定展示的内容使用悬浮窗。
> 核心原则：**UI 不直接访问数据库、文件存储或模型实现；翻译管线不放在 UI/QML 中；重型 AI 依赖保持可选；领域模型与基础设施解耦。**

---

## 1. 目标技术栈

| 层 / 能力 | 目标技术 | 设计说明 |
|---|---|---|
| 目标平台 | Windows 桌面端 | 新项目只面向 Windows，不以浏览器/Web SPA 作为主运行形态 |
| 桌面 UI | PySide6 + Qt Quick / QML | 负责书架、工作台、阅读器、设置等一级界面 |
| UI 状态 | Qt Property / QObject ViewModel / Model | QML 只绑定可观察状态，不持有业务真值 |
| 应用层 | Python Application Services / Use Cases | 负责导航、导入、翻译任务、保存、导出、校对等用例编排 |
| 领域层 | Python Domain Models | Book / Chapter / Page / Region / TranslationConstraint / PipelineTask 等领域对象 |
| Repository | Repository Interfaces + SQLite/File Adapters | 领域层只依赖接口；具体 SQLite、文件目录由基础设施实现 |
| 元数据持久化 | SQLite | 保存作品、章节、页面索引、状态、任务、翻译约束等结构化数据 |
| 图片/大型资产 | 本地文件系统 Managed Copy | 原图、清理图、译图、缩略图、导出文件、模型文件不直接塞入 SQLite |
| 设置 | SQLite 或独立配置文件 | 用户配置与业务数据分离；敏感 Key 不进入普通日志 |
| 图片处理 | Pillow + OpenCV | 导入预处理、裁切、缩放、颜色分析、合成等 |
| ML 运行时 | PyTorch / ONNX Runtime / Transformers（按 Provider 可选） | 重型依赖不得成为 Core/Domain 的强制 import |
| 文字检测 | DBNet / CTD / YOLO 系 Adapter | 通过统一 DetectionProvider 接口接入 |
| 文字分割 / Mask | Text Segmentation + OpenCV Mask Refinement | 从检测框进一步提取文字像素，执行膨胀、去噪、边界保护和线稿保护，为修复提供高质量 Mask |
| OCR | manga-ocr / 48px / RapidOCR / PaddleOCR Korean / OpenAI-compatible Vision OCR | 通过统一 OCRProvider 接口接入；日漫、韩漫、本地 OCR 与 OpenAI-compatible Vision OCR 统一走 Provider / Adapter 架构 |
| 翻译 | OpenAI-compatible / Sakura / 专用翻译 Adapter | 统一 TranslationProvider；允许本地或远程 Provider |
| 图片修复 | Simple Fill / Anime-Manga LaMa / AOT-GAN / BrushNet / PowerPaint / FLUX Fill | 统一 InpaintProvider + Inpaint Router；按气泡背景、黑白线稿、网点、彩色 Webtoon、复杂结构和质量模式自动选择修复路线 |
| 排版渲染 | 独立 Rendering Service | 与 OCR/翻译 Provider 解耦，负责横排/竖排/字体/描边/自动字号 |
| HTTP 外呼 | httpx | 仅基础设施 Provider 使用；UI/Domain 不直接发网络请求 |
| 网络代理 | Proxy / Network Manager（System / HTTP / HTTPS / SOCKS5） | 统一管理软件外部网络访问；支持系统代理、手动代理、按 Provider 覆盖、直连/绕过规则、连接测试与敏感配置保护 |
| 插件扩展 | Plugin / Hook Adapter | 通过稳定扩展点接入，不允许插件直接破坏 Domain 不变量 |
| 打包 | PyInstaller onedir（Windows） | 优先保证可诊断、可更新；发布前验证 Qt/PySide6 DLL 与可选模型依赖 |
| 测试 | pytest + Qt/UI 集成测试 + Repository/Provider Contract Tests | 单元、集成、数据安全、真实文件路径和关键 UI 状态均需覆盖 |
| CI | GitHub Actions | 至少执行测试、静态检查、打包验证和发布构建 |

---

## 2. 总体技术架构

```mermaid
%%{init: {"flowchart": {"curve": "linear", "nodeSpacing": 28, "rankSpacing": 38}}}%%
flowchart TB

    %% =========================================================
    %% Presentation
    %% =========================================================
    subgraph UI["Presentation / PySide6 + QML"]
        direction LR
        U1["工作台"]
        U2["书架"]
        U3["阅读器"]
        U4["设置"]
    end

    %% =========================================================
    %% Application
    %% =========================================================
    subgraph APP["Application Layer"]
        direction TB

        subgraph APP_ROW1[" "]
            direction LR
            NAV["Navigation Service"]
            LIBUC["Library Use Cases"]
            PIPE["Translation Pipeline<br/>Orchestrator"]
            TASK["Task / Queue Manager"]
        end

        subgraph APP_ROW2[" "]
            direction LR
            EDIT["Edit / Review<br/>Use Cases"]
            READUC["Reader Use Cases"]
            EXPORT["Export Service"]
        end
    end

    %% =========================================================
    %% Domain
    %% =========================================================
    subgraph DOMAIN["Domain Layer"]
        direction LR
        BOOK["Book / Chapter / Page"]
        REGION["Region / Bubble"]
        CON["Translation Constraints<br/>术语表 / 不译表"]
        STATE["Page / Task / Review State"]
    end

    %% =========================================================
    %% Ports
    %% =========================================================
    subgraph PORTS["Ports / Interfaces"]
        direction TB

        subgraph PORT_ROW1[" "]
            direction LR
            REPO["Repository Interfaces"]
            DETP["DetectionProvider"]
            OCRP["OCRProvider"]
            TRP["TranslationProvider"]
        end

        subgraph PORT_ROW2[" "]
            direction LR
            INPP["InpaintProvider"]
            RENDP["RenderingProvider"]
            PLUGP["Plugin / Hook Port"]
        end
    end

    %% =========================================================
    %% Infrastructure
    %% =========================================================
    subgraph INFRA["Infrastructure / Adapters"]
        direction TB

        subgraph INFRA_ROW1[" "]
            direction LR
            SQL["SQLite Repositories"]
            FILES["Managed File Storage"]
            HTTP["HTTP / OpenAI-compatible<br/>Transport"]
            PROXY["Proxy / Network Manager"]
        end

        subgraph INFRA_ROW2[" "]
            direction LR
            DETA["Detection Adapters"]
            OCRA["OCR Adapters"]
            TRA["Translation Adapters"]
            INPA["Inpaint Adapters"]
        end

        subgraph INFRA_ROW3[" "]
            direction LR
            RENA["Rendering Adapter"]
            PLUGA["Plugin Adapters"]
            DEVICE["Device / Model Manager"]
        end
    end

    %% =========================================================
    %% Local / External Resources
    %% =========================================================
    subgraph RES["Local / External Resources"]
        direction LR
        DB[("SQLite")]
        FS[("Project Data / Images /<br/>Thumbnails / Exports")]
        MODELS[("Local Models")]
        API["External APIs /<br/>Local AI Services"]
    end

    %% =========================================================
    %% Layer dependencies
    %% =========================================================
    UI --> APP
    APP --> DOMAIN
    APP --> PORTS
    DOMAIN --> REPO

    %% Repository
    REPO --> SQL
    REPO --> FILES

    %% Provider ports → adapters
    DETP --> DETA
    OCRP --> OCRA
    TRP --> TRA
    INPP --> INPA
    RENDP --> RENA
    PLUGP --> PLUGA

    %% Storage
    SQL --> DB
    FILES --> FS

    %% Local AI / device
    DETA --> DEVICE
    OCRA --> DEVICE
    INPA --> DEVICE
    RENA --> DEVICE
    DEVICE --> MODELS

    %% Network
    TRA --> HTTP
    OCRA -. "Vision OCR" .-> HTTP
    HTTP --> PROXY
    PROXY --> API

    %% Hide layout-only row containers
    style APP_ROW1 fill:transparent,stroke:transparent
    style APP_ROW2 fill:transparent,stroke:transparent
    style PORT_ROW1 fill:transparent,stroke:transparent
    style PORT_ROW2 fill:transparent,stroke:transparent
    style INFRA_ROW1 fill:transparent,stroke:transparent
    style INFRA_ROW2 fill:transparent,stroke:transparent
    style INFRA_ROW3 fill:transparent,stroke:transparent
```

### 架构方向

依赖方向必须保持：

`QML / UI → Application → Domain / Ports → Infrastructure Adapters`

禁止反向依赖：

- Domain 不 import PySide6/QML。
- Domain 不 import SQLite、httpx、PyTorch、Transformers。
- QML 不直接执行 SQL。
- QML 不直接读写项目文件。
- QML 不直接初始化 OCR / 检测 / 翻译 / 修复模型。
- Provider Adapter 不负责界面状态。
- Repository 不负责业务流程编排。
- 所有外部 HTTP/HTTPS/SOCKS 网络访问必须经过统一 Network/Proxy Manager；禁止各 Provider 在业务层散落自定义代理逻辑。

---

## 3. 一级界面与导航架构

书架、工作台、阅读器、设置是四个同级一级页面；软件默认启动进入书架。

```mermaid
flowchart LR

    NAV["Main Navigation<br/>默认：书架"]

    B["书架"]
    W["工作台"]
    R["阅读器"]
    S["设置"]

    NAV --> B
    NAV --> W
    NAV --> R
    NAV --> S

    CH["书架：章节"]

    B --> CH
    CH -.进入翻译.-> W
    CH -.进入阅读.-> R
```

### 导航与窗口规则

1. 一级导航由 `Navigation Service` 统一管理，QML 不自行拼接业务状态。
2. 应用启动默认导航到书架。
3. “书架 → 进入翻译”携带 `book_id + chapter_id` 打开工作台。
4. “书架 → 进入阅读”携带 `book_id + chapter_id + page_id/last_page` 打开阅读器。
5. 书架、工作台、阅读器、设置分别拥有独立 ViewModel；共享数据来自 Application/Repository，而不是相互直接访问。
6. 除四个一级页面外，业务功能优先使用当前页面固定 Panel；无合适固定位置时使用 Dialog / Floating Window，不创建额外一级 Route。
7. Floating Window 支持内容自适应、调整尺寸、最大化、双屏与拖出主窗口；业务真值仍由 Application/Repository 管理。
8. 最近作品、最近章节、最近页与必要 WindowLayoutState 由持久化层保存。

---

## 4. 翻译管线架构

翻译管线由 **Application Layer 的 Pipeline Orchestrator** 统一编排，不放在 QML。

```mermaid
flowchart LR

    IMPORT["导入"]
    DET["文字检测"]
    OCR["OCR"]
    COLOR["配色提取"]
    AUTO["自动术语识别"]

    subgraph CONSTRAINT["作品级翻译约束"]
        G["术语表"]
        N["不译表"]
    end

    TRANS["翻译"]
    INP["文字修复"]
    RENDER["排版渲染"]
    SAVE["保存"]

    IMPORT --> DET --> OCR --> COLOR --> AUTO
    AUTO -->|"新增 / 更新"| G
    G -->|"约束"| TRANS
    N -->|"约束"| TRANS
    OCR --> TRANS

    TRANS --> INP --> RENDER --> SAVE
```

### 翻译约束闭环

翻译约束表不是普通 UI 配置，而是 **作品级 Domain 数据**：

1. 自动术语识别从 OCR / 上下文中发现候选术语。
2. 候选术语经规则处理后写入或更新作品的术语表。
3. 用户可以在书架或工作台人工维护术语表与不译表。
4. PipelineRun 在准备阶段读取当前有效约束并生成 `effective constraint snapshot`；该 Run 内每次创建 Prompt / Request 都读取这份冻结快照。
5. 快照冻结后的约束修改默认只影响下一次 Run；单气泡重译等新 Run 在各自准备阶段生成快照（D06 §10）。
6. 人工修改过的术语优先于自动识别结果；自动流程不得静默覆盖人工锁定值。

---

## 5. Pipeline / Task / Queue 与任务进度面板

所有长耗时任务必须进入统一任务系统，避免 UI 自己管理并发。任务模型与 `03_DATA_MODEL.md` 保持一致：

```text
PipelineRun
├─ PipelineRunTarget
└─ PipelineTask
   └─ StepRun
```

### 5.1 PipelineRun

`PipelineRun` 表示用户发起的一整次操作，例如：

- 全部翻译。
- 全部翻译（跳过已翻译）。
- 选择页翻译。
- 单页翻译。
- 全部 / 选择页 / 单页重新 OCR。
- 全部 / 选择页 / 单页重新修复。
- 全部 / 选择页 / 单页重新渲染。
- 单 Region 重全翻译。

聚合状态至少支持：

```text
pending
running
paused
completed
completed_with_failures
failed
cancelled
interrupted
```

其中：

- `completed_with_failures` 表示批量任务整体结束，但部分页面 / Task 失败。
- `failed` 用于无法继续的 Run 级致命失败。
- 应用异常退出时，原 `running` 必须恢复为 `interrupted`，不得误判成功。

### 5.2 PipelineRunTarget / PipelineTask / StepRun

- `PipelineRunTarget` 固化本次任务的 Book / Chapter / Page / Region 目标集合，支持非连续多选页。
- `PipelineTask` 默认按 Page 或合理批次执行。
- `StepRun` 记录具体 `detect / ocr / color / term_extract / translate / segment / mask_refine / inpaint / render / save / export` 执行情况。
- 已成功且输入仍有效的 Step 可在恢复时跳过。
- Step 输出通过 ArtifactRevision / RegionRevision 保留 provenance。

### 5.3 状态与控制

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Running
    Pending --> Blocked: 缺少输入或 Provider 不可用
    Blocked --> Pending: 修复条件后重新规划
    Running --> Paused: Pause at safe boundary
    Paused --> Running: Continue
    Paused --> Cancelled: Stop
    Running --> Completed
    Running --> CompletedWithFailures
    Running --> Failed
    Running --> Blocked: 剩余单元仅有可解除阻塞
    Running --> Cancelled: Stop
    Running --> Interrupted: App exits unexpectedly
    Interrupted --> Running: Resume after recovery validation
    Interrupted --> Cancelled: Abandon
```

此图展示 Run 的业务状态结果；完整枚举、聚合优先级及 Restart / Abandon 落库语义以 [TASK-002 最小契约 §5～§6](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) 为准。Restart 不改变原 interrupted Run 的状态，而是标记 disposition 并创建新 Run。

控制语义：

- **暂停 Pause**：设置 Run 级 pause request；不再启动新的 Step / Page。正在执行且无法安全取消的 Step 允许完成后再进入 `paused`。
- **继续 Continue**：清除 pause request，从持久化断点继续。
- **停止 Stop**：设置 Run 级 cancel request；停止启动后续工作，剩余 Pending Task 转为 Cancelled；已经完成的 Page、Region、ArtifactRevision 和 Revision 全部保留，不回滚。
- **重试失败页**：创建新的 PipelineRun，仅包含失败目标，以 `source_run_id + retry_reason` 关联来源；原 Run 历史不改写（D03 §22、D06 §58、D08 AC-RETRY-002）。Step 自动重试属于原 Run 内的有限重试，复用相同输入与设置（D06 §56/57）。
- UI 控制命令通过 Application / Task Manager 下发，不由 QML 直接修改 Task 数据库状态。

### 5.4 工作台固定任务进度面板

工作台提供 `TaskProgressPanel`，默认位于**工作台底部固定区域**，可折叠成紧凑进度条。它不是独立页面，也不使用阻塞式 Modal。

推荐 UI 绑定结构：

```text
TaskProgressViewModel
├─ active_run_id
├─ run_title
├─ overall_progress
├─ total_page_count
├─ completed_page_count
├─ failed_page_count
├─ skipped_page_count
├─ waiting_page_count
├─ current_page_id
├─ current_page_name
├─ current_page_thumbnail
├─ current_step_type
├─ step_flow[]
├─ run_status
├─ can_pause
├─ can_continue
└─ can_stop
```

数据来源：

```text
PipelineRun
+ PipelineRunTarget
+ PipelineTask
+ StepRun
+ Page / Thumbnail Artifact
        ↓
TaskProgressProjection / ViewModel
        ↓
QML TaskProgressPanel
```

`TaskProgressViewModel` 是**投影状态，不是新的业务真值**。统计和当前步骤以 Task / StepRun 为准。

面板至少显示：

- 当前任务名称与范围。
- 总体进度条与百分比。
- 当前翻译流程：`检测 → OCR → 配色 → 术语 → 翻译 → Mask → 修复 → 渲染 → 保存`。
- 当前 Step 高亮。
- 当前 Page：页序、文件名，可显示小缩略图。
- 已完成页数。
- 失败页数。
- 跳过页数。
- 等待页数。
- `暂停 / 停止 / 继续` 按钮。

交互：

- 点击“已完成 / 失败 / 跳过”统计，通过 Page List ViewModel 筛选或定位对应页面。
- 点击当前 Page，页面列表滚动并选中该 Page。
- 页面列表与任务面板共享同一 Task Projection，显示 `等待 / 处理中 / 已完成 / 失败 / 跳过 / 已锁定`。
- Panel 折叠后仍显示：任务状态、百分比、当前页、当前 Step 与必要控制按钮。
- 任务完成后若存在失败页，Run 显示“已完成（有失败）”，并提供失败页重试入口。

### 5.5 并发原则

- CPU、GPU、网络 Provider 可使用不同并发策略。
- GPU/大模型任务必须通过统一资源锁或容量控制，不能由各页面自己竞争显存。
- 当前页是“UI 展示焦点”，不等于系统只能单并发；若启用并发，面板应显示主焦点 Page，并在任务详情中展示其他并行 Task。
- 单图翻译、一键翻译、多选翻译、单 Region 重全翻译共用同一 Pipeline 基础能力，只是 Target 和 Step 范围不同。

---

## 6. Provider / Adapter 架构

```mermaid
flowchart TB

    REG["Provider Registry"]

    REG --> DET["DetectionProvider"]
    REG --> OCR["OCRProvider"]
    REG --> TR["TranslationProvider"]
    REG --> INP["InpaintProvider"]
    REG --> REN["RenderingProvider"]

    OCR --> O1["manga-ocr"]
    OCR --> O2["48px / RapidOCR"]
    OCR --> O3["PaddleOCR Korean<br/>韩国条漫 OCR"]
    OCR --> O4["OpenAI-compatible Vision OCR<br/>base_url / api_key / model"]

    TR --> T1["OpenAI-compatible"]
    TR --> T2["Sakura"]
    TR --> T3["其他 Translation Adapter"]

    INP --> I1["Simple Fill / 局部采样"]
    INP --> I2["Anime / Manga LaMa<br/>默认本地修复"]
    INP --> I3["AOT-GAN<br/>备用本地修复"]
    INP --> I4["BrushNet / PowerPaint<br/>复杂背景高质量修复"]
    INP --> I5["FLUX Fill<br/>最高质量回退"]
```

### Provider 规则

1. 每一种能力都通过稳定接口注册，不在业务代码里大量 `if provider == ...`。
2. Provider 配置包含 `id / capability / model / endpoint / credential reference / options`。
3. OpenAI-compatible 接口统一支持 `base_url + api_key + model`。
4. Vision OCR 与普通翻译可以共享 Transport，但 Provider 能力声明必须分开。
5. 韩国条漫 OCR 作为独立 OCR 能力注册，优先使用韩文识别模型；艺术字或复杂区域可回退 Vision OCR。
6. `InpaintProvider` 必须声明能力标签，例如 `simple_background / manga_lineart / screentone / color_webtoon / large_mask / structure_preservation / diffusion / cpu / gpu`，供 `Inpaint Router` 自动选择。
7. 所有需要联网的 Provider 通过统一 `NetworkClient / ProxyManager` 获取网络会话；Provider 可声明是否继承全局代理、使用专用代理或强制直连。
8. Provider 初始化失败必须返回可诊断错误，不允许让应用整体无法启动。
9. 重型模型必须延迟加载，可卸载/释放；Core/Domain 启动不应自动加载全部模型。

---

## 6.1 漫画文字消除 / 图片修复架构

图片修复不采用“所有区域统一交给一个模型”的方式，而采用 **Mask 优先 + 多级 Inpaint Router**。

```mermaid
flowchart LR

    DET["Text Detection<br/>文字区域检测"]
    SEG["Text Segmentation<br/>文字像素分割"]
    MASK["Mask Refinement<br/>膨胀 / 去噪 / 边界与线稿保护"]
    ROUTER["Inpaint Router"]

    SIMPLE["Simple Fill / 局部采样"]
    LAMA["Anime / Manga LaMa"]
    AOT["AOT-GAN"]
    ADV["BrushNet / PowerPaint"]
    FLUX["FLUX Fill"]

    DET --> SEG --> MASK --> ROUTER

    ROUTER -->|"简单气泡 / 纯色背景"| SIMPLE
    ROUTER -->|"普通漫画 / 黑白线稿"| LAMA
    ROUTER -->|"网点 / 结构型区域"| AOT
    ROUTER -->|"彩色 Webtoon / 复杂背景"| ADV
    ROUTER -->|"关键细节 / 高质量回退"| FLUX
```

### 6.1.1 Mask 优先原则

修复质量首先取决于 Mask，而不是单纯依赖更大的生成模型。

目标流程：

`文字检测 → 文字像素分割 → Mask 清理/膨胀 → 保护气泡边框/人物线稿 → 图片修复`

Mask Refinement 至少负责：

- 去除检测框中非文字背景。
- 对文字笔画做适度膨胀，避免残留边缘。
- 尽量保留气泡边框。
- 尽量保留人物、建筑、速度线等结构线。
- 对复杂艺术字允许扩大 Mask，但必须记录原 Mask 与最终 Mask。
- 单气泡重修只影响目标 Region。

### 6.1.2 多级修复策略

| 场景 | 优先路线 | 说明 |
|---|---|---|
| 白色/纯色气泡、小面积文字 | Simple Fill / 局部颜色采样 | 最快、最稳定，避免不必要的生成式重建 |
| 普通黑白日漫、常规线稿 | Anime / Manga LaMa | 默认本地修复路线 |
| 网点、较大缺失、结构连续性要求较高 | AOT-GAN 或 Manga LaMa | 作为结构型备用路线 |
| 韩国彩色 Webtoon、渐变、特效、复杂背景 | BrushNet / PowerPaint | 高质量模式，优先处理复杂彩色场景 |
| 文字覆盖人物、建筑、关键纹理或前述路线失败 | FLUX Fill | 最高质量回退，不作为默认批处理模型 |

### 6.1.3 韩国 Webtoon 专项策略

韩国条漫应拥有独立的 `color_webtoon` 修复能力标签。

原因是彩色 Webtoon 常见：

- 文字直接覆盖渐变背景。
- 文字覆盖人物头发、服装和皮肤。
- 大面积拟声词与特效文字。
- 发光、阴影、速度线和粒子效果。

因此 Router 在 `color_webtoon=true` 且背景复杂时，应优先选择高质量扩散修复 Provider，而不是强制使用普通 LaMa。

### 6.1.4 Inpaint Router 输入

Router 的判断输入建议至少包括：

- `mask_area_ratio`
- `background_complexity`
- `is_speech_bubble`
- `is_solid_background`
- `is_lineart`
- `has_screentone`
- `is_color_webtoon`
- `structure_crossing_mask`
- `preferred_quality`
- `device_capability`
- `provider_availability`

Router 输出：

- 目标 `InpaintProvider`
- 选用原因
- fallback 顺序
- 预计资源等级

### 6.1.5 默认回退链

推荐默认策略：

```text
Simple Fill
    ↓ 不适用 / 失败
Anime / Manga LaMa
    ↓ 结构恢复不足
AOT-GAN
    ↓ 彩色复杂背景 / 高质量需求
BrushNet / PowerPaint
    ↓ 关键区域仍失败
FLUX Fill
```

并非每次都从第一层顺序执行；Router 应根据场景直接选择合适层级。

### 6.1.6 数据保护

- 原图始终保留，不覆盖。
- 每次修复生成新的 clean artifact 或 revision。
- 自动修复不得覆盖已人工确认的修复结果，除非用户明确要求重跑。
- 重跑必须能够指定 Region / Page 范围。
- 保存 `mask / provider / model / options / provenance`，便于复现和比较。
- 高质量扩散模型生成的结果必须允许快速切回 LaMa 或原始版本。


---

## 6.2 网络代理与统一网络访问

软件提供统一网络代理能力，由 `ProxyManager / NetworkManager` 负责。  
UI、Domain、Application 不直接创建代理连接；所有外部网络访问统一经过基础设施层网络客户端。

### 6.2.1 代理模式

至少支持：

- `Direct`：不使用代理。
- `System`：读取 Windows 系统代理设置。
- `HTTP`：手动配置 HTTP 代理。
- `HTTPS`：手动配置 HTTPS 代理。
- `SOCKS5`：支持本地代理客户端或远程 SOCKS5 服务。
- `Provider Override`：单独为某一 Provider 指定代理或直连。

推荐配置模型：

```text
NetworkProfile
├─ mode
├─ http_proxy
├─ https_proxy
├─ socks5_proxy
├─ username
├─ password / credential_ref
├─ bypass_hosts[]
├─ inherit_system
├─ timeout
└─ verify_tls
```

### 6.2.2 作用范围

统一代理至少覆盖：

- OpenAI-compatible Translation / Vision OCR。
- 百度、有道、彩云等云端 API。
- 模型与权重下载。
- Hugging Face / GitHub 等模型或资源访问。
- 网页导入、Firecrawl、gallery-dl 等外部站点。
- Plugin / Plugin Agent 在授权情况下产生的网络请求。
- 更新检查或其他明确需要联网的基础设施功能。

本地服务默认不走代理：

- `localhost`
- `127.0.0.1`
- 本地 Sakura
- 本地 Ollama
- 用户配置的 LAN 服务

这些地址应自动进入 `bypass_hosts`，同时允许用户修改。

### 6.2.3 全局代理与 Provider 覆盖

代理优先级建议：

```text
Provider 专用代理
        ↓
全局软件代理
        ↓
Windows 系统代理
        ↓
Direct
```

规则：

1. 默认 Provider 继承全局软件代理。
2. Provider 可以显式设置 `Direct`，用于本地服务或不希望走代理的接口。
3. Provider 可以使用专用代理，不影响其他网络请求。
4. 代理设置变更后，新建网络会话立即使用新配置；已有长连接按安全策略重建。
5. 不允许把代理地址硬编码在 Provider 实现中。

### 6.2.4 网络客户端

推荐统一封装：

```text
NetworkManager
├─ ProxyManager
├─ HttpClientFactory
├─ TLS / Certificate Policy
├─ Timeout Policy
├─ Retry Policy
├─ Rate Limit Integration
└─ Connectivity Test
```

Provider 不直接：

```python
httpx.Client(proxy="...")
```

而是请求：

```text
NetworkManager
→ create_client(provider_id)
→ 返回已应用代理 / timeout / TLS / retry 的网络客户端
```

这样可确保代理、超时、证书、日志和错误处理策略一致。

### 6.2.5 连接测试

设置中心提供“网络 / 代理”页面，至少支持：

- 测试直连。
- 测试当前代理。
- 测试指定 Provider。
- 显示 DNS / TCP / TLS / HTTP 阶段错误。
- 显示“当前是否经过代理”，但不在日志中暴露代理账号密码。
- 区分代理连接失败与目标 API 鉴权失败。

测试结果只用于诊断，不作为业务数据保存。

### 6.2.6 凭据与安全

- 代理用户名、密码不得明文写入普通日志。
- UI 显示密码时默认掩码。
- 优先通过 Credential Store / credential reference 保存敏感信息。
- 导出普通软件设置时默认不导出代理密码、API Key 等敏感字段。
- 日志中代理 URL 必须脱敏，例如：

```text
socks5://user:***@127.0.0.1:7890
```

- 不允许因“代理可用”而关闭 TLS 校验；`verify_tls=false` 仅作为高级诊断选项，并应明确警告。

### 6.2.7 失败与回退

网络错误应分类：

- `ProxyConnectionError`
- `ProxyAuthenticationError`
- `DNSResolutionError`
- `TLSHandshakeError`
- `ConnectTimeout`
- `ReadTimeout`
- `ProviderAuthenticationError`
- `ProviderRateLimitError`
- `ProviderUnavailableError`

默认不应在代理失败后静默切换直连，避免用户本来希望所有流量必须经过代理却发生泄漏。

如果用户开启“允许代理失败后直连”，才允许：

```text
Proxy
  ↓ 失败
Direct
```

并在 UI 明确显示发生过回退。


---

## 7. 数据与 Repository 架构

### SQLite 保存

建议保存结构化真值：

- Books
- Chapters
- Pages
- Regions
- TranslationConstraints
- PageStatus
- Task / Queue State
- Provider/Profile Metadata
- Network / Proxy Profile Metadata
- Tags
- Recent/Open State
- Audit / Migration Version

### 文件系统保存

```text
data/
└─ books/
   └─ {book_id}/
      ├─ cover/
      ├─ chapters/
      │  └─ {chapter_id}/
      │     ├─ original/
      │     ├─ clean/
      │     ├─ translated/
      │     ├─ thumbnails/
      │     └─ workspace/
      └─ exports/
```

### Repository 原则

- `BookRepository`
- `ChapterRepository`
- `PageRepository`
- `RegionRepository`
- `TranslationConstraintRepository`
- `TaskRepository`
- `SettingsRepository`

Repository Interface 位于 Domain/Application 可依赖区域；SQLite/File 实现在 Infrastructure。

禁止：

`QML → sqlite3`

`QML → Path.write_bytes()`

`Domain → sqlite3`

---

## 8. Managed Copy 与导入安全

本地导入默认采用 **Managed Copy**：

1. 用户选择原始图片/文件夹/PDF/MOBI。
2. 导入器验证文件类型、可读性、重复项和页序。
3. 原始资源复制到项目受控目录。
4. 数据库只保存受控文件引用、哈希、尺寸、顺序等元数据。
5. 后续 OCR、修复、排版、导出基于 Managed Copy，不修改用户原始文件。
6. 删除作品时必须区分“删除项目副本”和“用户原始文件”；默认不得删除用户源文件。

---

## 9. 编辑器与 Region 架构

编辑器使用同一个 Page / Region Domain，不维护第二套独立数据模型。

Region 至少覆盖：

- geometry / polygon
- source_text
- translated_text
- OCR metadata
- text direction
- font / size / color / stroke
- render metadata
- mask / inpaint metadata
- manual edit marker
- review state
- lock state（若启用）
- provider provenance

操作路径：

`QML Canvas → Edit Use Case → Domain Region → Repository → Viewer Refresh`

单气泡 OCR、重译、重渲染只处理目标 Region，不得破坏同页其他人工修改内容。

---

## 10. 单图翻译 / 一键翻译 / 上下文翻译

三类翻译入口共用统一 Translation Use Case：

### 单图翻译

- 默认跳过已完成且不需要重算的步骤。
- 可选择仅当前页。
- 可选择把上页 / 下页文字作为上下文，但只修改当前页目标内容。

### 一键翻译

- 对章节或选定页范围创建批量任务。
- 跳过已翻译、已锁定或明确排除的内容。
- 保护人工修改。
- 支持失败重试和断点恢复。

### 多页上下文模式

- 尽可能把连续多页 OCR 文本作为上下文。
- Context Window 与实际写回范围分离。
- “作为上下文”不等于“允许修改”。
- 超出模型窗口时由 Context Builder 分块，而不是由 UI 拼 Prompt。
- 翻译约束表始终参与上下文构建。

---

## 11. 设备与模型管理

目标增加统一 `DeviceManager / ModelManager`，避免设备判断散落各 Provider。

职责：

- 探测 CUDA / DirectML / CPU 能力。
- 根据 Provider 能力和用户设置选择执行设备。
- GPU 不可用时安全回退 CPU。
- 统一模型缓存和加载状态。
- 支持延迟加载、卸载、清理。
- 提供任务级资源占用信息。
- 不让 QML 直接持有 PyTorch/ONNX 模型实例。

---

## 12. 插件与 Hook 边界

插件属于扩展层，不进入核心 Domain。

推荐扩展点：

- before/after detect
- before/after OCR
- before/after translate
- before/after inpaint
- before/after render
- before/after export

原则：

- Hook 输入输出必须有明确 schema。
- Plugin 崩溃不能破坏核心数据。
- Plugin 不可直接绕过 Repository 修改数据库。
- Plugin 权限与文件/网络访问应可审计。
- Plugin Agent 如保留，只负责生成/管理插件，不进入漫画翻译主链路。

---

## 13. 运行时拓扑

```mermaid
flowchart LR

    subgraph HOST["Windows Desktop Process"]
        APP["PySide6 Application"]
        QML["Qt Quick / QML"]
        APP_LAYER["Application Services"]
        WORKER["Task / Worker Pool"]
        DOMAIN["Domain"]
        INFRA["Repositories / Providers"]
        NETM["Network / Proxy Manager"]
        DEV["Device / Model Manager"]

        APP --> QML
        QML --> APP_LAYER
        APP_LAYER --> DOMAIN
        APP_LAYER --> WORKER
        WORKER --> INFRA
        INFRA --> NETM
        INFRA --> DEV
    end

    DB[("SQLite")]
    FS[("Managed Files")]
    MODELS[("Local Models")]
    NET["External APIs / Local AI Services"]

    INFRA --> DB
    INFRA --> FS
    DEV --> MODELS
    NETM --> NET
```

### 运行时原则

- 不要求启动本地 Flask/HTTP Server 才能运行桌面 UI。
- UI 与业务逻辑通过 Python/Qt 边界调用，不走 localhost HTTP 作为内部主通道。
- 网络仅用于外部 Provider、模型下载、网页导入等明确功能。
- 所有外部网络请求统一经过 Network / Proxy Manager；支持 Direct / System / HTTP(S) / SOCKS5 及 Provider 级覆盖。
- 后台任务不得阻塞 Qt UI Thread。
- 长任务通过 Worker/Task Manager 执行，进度统一回传 ViewModel。

---

## 14. 测试与架构守卫

至少建立以下测试层：

| 测试 | 目标 |
|---|---|
| Domain Unit Tests | 不依赖 Qt/SQLite/模型即可运行 |
| Repository Contract Tests | SQLite/File Adapter 行为一致 |
| Provider Contract Tests | OCR/翻译/检测/修复 Provider 统一契约、能力声明与 fallback 行为 |
| Pipeline Tests | 步骤顺序、跳过、失败、重试、取消 |
| Translation Constraint Tests | 自动术语写入、人工优先、后续翻译读取 |
| Managed Copy Tests | 不修改用户源文件、重复检测、回滚 |
| UI/ViewModel Tests | 书架/工作台/阅读器/设置状态与跳转；任务进度面板、暂停/继续/停止、页数统计与当前页定位 |
| Real Asset Tests | PNG/JPEG/PDF 等真实文件路径、缩略图与解码 |
| Migration Tests | SQLite schema 升级与旧数据兼容 |
| Network / Proxy Tests | Direct / System / HTTP(S) / SOCKS5、bypass、Provider override、认证失败与代理失败行为 |
| Packaging Smoke Test | 打包后的 exe 可启动、Qt DLL/插件完整 |

### 架构守卫

CI 中应检查：

- `domain/` 不得 import `PySide6`
- `domain/` 不得 import `sqlite3`
- `domain/` 不得 import `torch/transformers/onnxruntime`
- `ui/` 不得直接 import 具体 Repository Adapter
- `ui/` 不得直接 import 具体 OCR/翻译/修复实现
- 重型 AI 依赖不得成为 core package 的强制依赖

---

## 15. 明确不采用的旧架构方式

新项目不以以下旧架构作为目标：

- Vue SPA 作为主 UI。
- Flask `localhost:5000` 作为桌面程序内部总线。
- 在前端/QML 中编排完整翻译状态机。
- UI 直接承担 GPU 互斥和并发控制。
- 仅用散落 JSON 文件充当全部应用级数据库。
- Manga Insight / ChromaDB / RAG 作为主项目核心模块。
- 角色工坊作为一级业务能力。
- 各 OCR/检测/修复实现自行决定全局设备策略。
- 页面、书架、翻译管线各自维护重复的状态真值。

旧项目中的算法、模型接口、Provider 经验、导入/导出实现可以作为迁移参考，但必须通过新架构的 Port / Adapter / Repository 边界接入。

---

## 16. 推荐源码边界

```text
src/
├─ ui/
│  ├─ qml/
│  ├─ viewmodels/
│  └─ models/
├─ application/
│  ├─ navigation/
│  ├─ library/
│  ├─ translation/
│  ├─ editing/
│  ├─ reading/
│  ├─ export/
│  └─ tasks/
├─ domain/
│  ├─ books/
│  ├─ pages/
│  ├─ regions/
│  ├─ constraints/
│  └─ tasks/
├─ ports/
│  ├─ repositories/
│  ├─ detection/
│  ├─ ocr/
│  ├─ translation/
│  ├─ inpaint/
│  ├─ rendering/
│  └─ plugins/
├─ infrastructure/
│  ├─ sqlite/
│  ├─ filesystem/
│  ├─ providers/
│  ├─ transport/
│  ├─ network/
│  ├─ devices/
│  └─ plugins/
└─ bootstrap/
   ├─ container.py
   └─ app.py
```

该目录只是目标边界示意；实际迁移时应优先保持已稳定模块和测试，不为“目录漂亮”进行无收益的大规模移动。
