# UX 基础模型（三套方向共享的业务骨架）

> 本文件把已核实的业务规则转换成 **UI/UX 必须表达的模型**。三套设计方向可以有完全不同的信息架构、导航范式与视觉语言，但**不得违反本文件定义的语义**。
> 冻结依据：`doc/03_DATA_MODEL.md`、`doc/06_TRANSLATION_PIPELINE.md`、`doc/01_FUNCTIONAL_ARCHITECTURE.md` 及 L1 代码盘点。

---

## 1. 对象层级与寻址

```
Workspace（本地数据根 / Managed Copy 根）
└─ Book（作品：标题、封面、标签、状态）
   └─ Chapter（章节：Paged/RTL/LTR 或 Webtoon/Vertical）
      └─ Page（页面：单图或超长条图）
         └─ Region（文字区域：对白/旁白/拟声词/标题/注释/其他）
            └─ RegionRevision（区域版本：OCR/译文/样式/修复/lock 快照）
```

派生对象：`ArtifactRevision`（原图 / clean / mask / render 的资产版本）、`PipelineRun` → `PipelineTask` → `StepRun`、`TranslationConstraint`、`TranslationMemory`、`ExportHistory`、`RecycleBinEntry`。

设计含义：

- **Region 是编辑的第一等公民**，不是 Page。Page 是阅读与批量的单位。
- 任何界面都必须能回答「我现在在哪一层」，且切换层级不丢上下文。

---

## 2. 作用域 × 动作矩阵（全产品唯一操作模型）

旧界面的核心问题是操作入口按"页面"分散（右键菜单、工具栏、Inspector 按钮各一套）。新设计统一为二维模型：

### 2.1 作用域（Scope）— 第一轴

| Scope | 定义 | 选择方式 |
|---|---|---|
| `chapter` | 当前章节全部页 | 默认作用域，无需显式选择 |
| `selection` | 用户多选的页/Region 集合 | 列表多选 |
| `page` | 当前页 | 当前页上下文 |
| `region` | 当前选中 Region | 画布/列表选中 |

**规则**：作用域必须始终可见（作用域栏/状态条/选中计数），且操作按钮必须携带作用域后缀（「重新渲染 · 本章 23 页」/「重新渲染 · 选中 5 页」）。禁止存在"看不出会影响多少范围"的按钮。

### 2.2 动作（Action）— 第二轴

| Action | 语义 | 影响 |
|---|---|---|
| `translate` | 全部翻译（补齐必要上游，复用有效 OCR） | 新建译文 Revision，不覆盖 Lock/人工终稿 |
| `translate_untranslated` | 只处理未翻译/失败/缺失 | 同上，跳过已完成与锁定 |
| `reocr` | 重新 OCR | 使下游 translate/render 失效（stale） |
| `reinpaint` | 重新文字修复 | 使 render 失效 |
| `rerender` | 重新排版渲染 | 只重渲染，**不得**偷偷执行 OCR/翻译/修复 |
| `retranslate_region_full` | 单 Region 全链路重跑 | 只作用于目标 Region，可临时覆盖该 Region 的专项锁（需确认） |
| `confirm` | 校对确认（review_state → confirmed） | 不改变内容，只改可信度；人工确认后进入保护 |
| `lock` / `unlock` | 加锁/解锁 | 影响后续自动化 |
| `export` | 导出 | 只读产出，不改变 Revision |

### 2.3 合法性与保护

- 任何动作在执行前必须显示：**作用域内有多少单元会被跳过**（Lock / 已确认 / 无有效上游）。
- 任何会覆盖人工成果的动作必须显式确认，并给出「影响 N 条人工译文」的量化提示。
- `rerender` 永远不得隐式触发上游步骤。

### 2.4 设计含义

三套方向可以用三种完全不同的方式表达这个矩阵，但矩阵本身必须存在：

- 一种可以把矩阵做成**常驻动作带 + 作用域选择器**；
- 一种可以把矩阵做成**队列任务构建器**（先选作用域，再选动作，生成 Run）；
- 一种可以把矩阵做成**命令面板 + 上下文动作环**。

禁止：把动作散落在多个入口、依赖右键菜单作为唯一入口、按钮不显示作用域。

---

## 3. 内容四轨模型

同一 Region 在流水线中产生四类内容，它们**同时存在且互相依赖**，这是本产品与普通图片编辑器/文本编辑器的本质区别：

| 轨道 | 内容 | 可见形态 |
|---|---|---|
| **原图轨** | Original Artifact（永不修改的用户源） | 原始页面 |
| **文本轨** | `ocr_text` → `machine_translation` → `edited_translation` → `final_translation`，含 `review_state` | 文本面板 / 行级对照 |
| **修复轨** | Text Segmentation → Mask → Clean Artifact（已抹除原文字） | 无字图 / mask 叠加 |
| **排版轨** | TextStyle + Color + Render（最终成品图） | 成品页 |

**设计含义（关键）**：

1. 用户的心智模型不是"一张图"，而是"四层叠加"。设计必须能让人看出**当前看到的是哪一轨**，以及四轨的完成度差异。
2. 「原文 vs 译文」对照不是可选功能，是核心工作界面之一。
3. 「修复轨」和「排版轨」的失败必须能被单独定位（常见：译文有了但修复失败 → 成品页缺字）。
4. 同一 Region 的四轨状态可能不一致（`ocr` completed、`translate` stale、`inpaint` failed），UI 必须能表达这种不一致，不能只给一个"页状态"。

---

## 4. 状态模型（唯一真值）

### 4.1 阶段级 `StageState`

阶段：`detect / ocr / color / term_extract / translate / segment / mask_refine / inpaint / render / review / export`

状态：`not_started / pending / running / completed / stale / failed / skipped / interrupted / cancelled`

**`stale` 是产品的核心语义**：该阶段曾成功，但上游（Region 几何、OCR、Mask、Clean、TextStyle 等）发生变化，当前结果不再有效。历史 Revision 仍保留。

设计要求：
- `stale` 必须有独立视觉表达（不同于 `failed`、不同于 `not_started`）。
- 显示"过期"时必须给出**过期原因**（哪个上游变了）。
- 禁止把 `stale` 折叠进"未完成"或"失败"。

### 4.2 页 / 区域综合状态（面向人）

`未处理 / 处理中 / 部分完成 / 已完成 / 需校对 / 失败 / 已锁定`

综合状态是**派生值**，底层 StageState 才是真值。UI 必须能从综合状态**下钻**到阶段矩阵。

### 4.3 Run 状态

`pending / running / paused / blocked / completed / completed_with_failures / failed / cancelled / interrupted`

- `completed_with_failures`：Run 结束但有失败单元，**成功成果有效**。必须与 `failed` 明确区分。
- `blocked`：存在需用户解除的前置阻塞（如 Provider 未配置）。必须能直接跳到修复该阻塞的位置。
- `interrupted`：异常退出。下次启动必须提供 继续 / 重新开始 / 放弃 三选一。

### 4.4 进度投影

`TaskProgressSnapshot` 必须同时表达：总体进度、当前 Step、当前 Page、已完成/失败/跳过/等待/处理中页数、`can_pause / can_continue / can_stop`。**页列表与进度面板必须同源**，不允许两套真值。

---

## 5. 保护与审阅闭环

### 5.1 四级 Lock（优先级从上到下）

```
Page Lock  >  Region Lock  >  Translation Lock / Inpaint Lock
```

| Lock | 阻止 | 不阻止 |
|---|---|---|
| Page Lock | 该页全部自动处理 | 阅读、导出、手动编辑（手动编辑仍需符合 Region 规则） |
| Region Lock | 该 Region 全部自动处理 | — |
| Translation Lock | 自动翻译/重译覆盖译文 | 重新渲染 |
| Inpaint Lock | 自动重新修复 | 用现有 clean 重新渲染 |

### 5.2 人工保护链

```
用户编辑译文 → manual_edited = true → translation_locked = true → 自动流程不得静默覆盖
```

设计要求：加锁必须**可见且可解释**（"因人工编辑而锁定，点击解除"），不得出现"为什么流水线跳过了这一条"的困惑。

### 5.3 审阅闭环（review_state）

```
unreviewed（机器产出未看） → needs_review（被标记需复核） → confirmed（人工确认）
```

设计要求：
- 必须提供「待确认队列」类的工作视图，支持逐条确认与批量确认。
- 确认动作必须低成本（单键），并能连续处理下一条。
- `confirmed` 之后的内容进入保护，任何自动化不得覆盖（除非显式解除）。
- 术语一致性提示必须出现在审阅界面（作者的术语表/不译表约束）。

---

## 6. 错误与恢复模型

### 6.1 六类错误源

| 类别 | 代表错误 | 用户可做的动作 |
|---|---|---|
| Input / Domain | MissingOCRText、InvalidGeometry、LockBlocked | 修数据、解锁、重跑 |
| Provider | 认证失败、限流、不可用、非法响应 | 换 Provider、改配置、重试 |
| Network | 代理/DNS/TLS/超时 | 改网络配置、测试连接、重试 |
| Device / Model | 模型加载失败、OOM、设备不可用 | 换设备、降并发、装模型 |
| Storage | 读/写/提交/事务失败 | 检查磁盘、重试、看日志 |
| Pipeline | 输出映射、上下文构建、中断、取消 | 重跑、跳过、报告 |

### 6.2 恢复路径

每个失败单元必须至少提供：**重试该单元** / **跳过该单元** / **查看详情** / **定位到修复配置的位置**。

设计要求：
- **错误不能只做 Toast**。Toast 只能作为提示，真值必须在任务态/对象态里可查。
- 失败必须可按类聚合（"12 页失败：9 个 Provider 限流、3 个 OOM"），否则用户无法批量处置。
- 失败的 Page/Region 必须保留已完成上游成果，重试从断点继续（不得整页重跑）。

---

## 7. 长任务与并发

- Run 生命周期：创建 → 排队 → 运行 → （暂停/继续）→ 完成 / 完成有失败 / 失败 / 取消 / 中断 / 阻塞。
- 暂停：只在安全边界生效；必须显示"正在等待当前步骤安全结束"。
- 停止：不回滚已完成成果；剩余单元标 `cancelled`。
- 崩溃恢复：启动时必须显式提示上次中断的 Run，禁止静默重启。
- 同一 Page 多任务冲突：必须串行化并给出阻塞提示。
- 并发资源（GPU / CPU / 网络并发）是**可配置且可见**的，不得隐式降速。

---

## 8. 桌面输入模型（共享下限）

| 层 | 要求 |
|---|---|
| 全局 | 命令面板（全部命令 + 作用域提示）；全局搜索/跳转；视图切换；撤销/重做（可编辑内容） |
| 对象导航 | 上/下一个 Region、上/下一页、上/下一章；跳转到第 N 页；跳转到下一个失败/待确认 |
| 编辑 | 进入/退出文本编辑；确认并下一条；放弃修改；IME 安全（不拦截中日韩输入组合） |
| 画布 | 缩放（滚轮/Ctrl+滚轮）、平移（空格拖拽/中键）、适应窗口（单键）、100% |
| 鼠标 | 单击选择、拖拽移动 Region、拖角缩放、Shift 多选、右键上下文（次要入口）、悬停提示（延迟 ≤400ms） |
| 危险操作 | 必须可键盘取消；不得把 Enter 默认绑到破坏性动作 |

**可访问性下限**：正文对比度 ≥ 4.5:1（大字号 ≥3:1），焦点环始终可见，全部功能可键盘完成，颜色不是唯一状态载体（必须配合形状/文字/图标）。

---

## 9. 设计必须表达的 12 个「状态真相」

任何方向的原型必须能展示下列状态，否则视为状态设计不完整：

1. 空工作区（首次启动，无任何作品）
2. 导入中 / 导入失败（部分成功）
3. 章节无页面 vs 页面无 Region
4. 流水线运行中（含当前 Step / 当前页 / 进度）
5. 流水线暂停（等待安全边界）
6. 流水线完成但有失败（`completed_with_failures`）
7. 流水线阻塞（`blocked`，Provider 未配置）
8. 中断恢复（`interrupted` → 继续/重开/放弃）
9. Region 部分完成（OCR 完成、翻译失败）
10. `stale`（上游变化导致结果过期，含原因）
11. 待确认队列（`review_state = needs_review` 积压）
12. 危险确认（永久删除 / 覆盖 N 条人工译文 / 恢复备份）

---

## 10. 与三套方向的关系

| 层 | 共享（本文件） | 各方向自由 |
|---|---|---|
| 语义 | 对象层级、作用域、动作、四轨、状态、Lock、审阅、错误、长任务 | 如何表达、放在哪里、用什么交互 |
| 结构 | 必须可达的能力集合 | 导航范式、工作空间划分、页面数量与组织 |
| 视觉 | 质量门槛与反模式 | 全部视觉语言、令牌、字体、色彩、图标 |

**判定标准**：三套方向中任意两套，如果把导航骨架与主工作对象交换后仍能互换使用，则说明差异不足，判不合格。
