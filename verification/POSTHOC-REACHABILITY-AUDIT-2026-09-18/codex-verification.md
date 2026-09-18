# Codex 独立复核：Qoder《生产可达性盘点》的 P0/P1

**对象**：[doc/research/PRODUCTION-REACHABILITY-AUDIT-2026-09-18.md](../../doc/research/PRODUCTION-REACHABILITY-AUDIT-2026-09-18.md)
（作者 Qoder，只读盘点，基线 master `16f7d75`）。

**复核方**：Codex（盘点作者之外的独立一方）。**方法**：只读；不复用盘点的结论——用仓库自己的装配入口
`bootstrap.app.assemble_services(...)` + 真实 SQLite 文件 + 真实 `RunController`（QThread/moveToThread/queued start）驱动，
我自己写探针与断言。**环境**：pwsh + `G:/CODEX/New Manga.task-envs/TASK-012-py312`、`PYTHONDONTWRITEBYTECODE=1`、
`-p no:cacheprovider`；探针只写临时目录。

## 逐项裁定

| 项 | 级别 | 盘点自述状态 | 我的裁定 | 我的证据 |
|---|---|---|---|---|
| **P-1** 生产任务执行复用 GUI 线程的 SQLite 连接 | P0 | MECHANISM+STATIC | **成立（端到端）** | [codex-p1-threadsqlite-probe.txt](codex-p1-threadsqlite-probe.txt)：`[A]` 真实 `PipelineService` 在另一线程 → `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread`；`[B]` **真实 `RunController`（QThread）** → `runCrashed` 同一条错误；`[C]` 同一份装配在主线程可跑完 ⇒ 纯线程问题 |
| **P-2** 生产无法创建 Region，且无 `detect` handler | P0 | VERIFIED（静态） | **成立（端到端）** | [codex-p2-p6-probe.txt](codex-p2-p6-probe.txt)：真实 `translate_all` 运行的 `step_runs` 行为 `ocr region=None status=failed code=INVALID_INPUT detail=step 'ocr' requires a Region target`；`build_production_handlers` 只注册 8 个 step 类型（`ocr/color/term_extract/translate/segment/mask_refine/inpaint/render`，**无 detect**）；`create_region` 全仓只有定义、`src/ui/**` 无调用点 |
| **P-3** provider 绑定与 settings 恒为空 | P1 | VERIFIED（静态） | **成立（端到端）** | [codex-p3-wall-order-probe.txt](codex-p3-wall-order-probe.txt)：我经应用服务造出一个 Region 后跑 `OCR_REGION` → plan 阶段 `decision=run`，运行期 `step_runs` 得 `PROVIDER_NOT_CONFIGURED`（`no provider binding configured for step 'ocr'`）⇒ 越过 P-2 后确实撞上 P-3 |
| **P-4** `commandError` 在 QML 无消费者 | P1 | VERIFIED | **成立（静态）** | `rg commandError src/ui/qml/` → **0 命中**；13 处全部在 `ui/viewmodels/workbench/viewmodel.py`（定义 + 11 处 emit） |
| **P-5** 书架「导入图片」打不开对话框 | P1 | VERIFIED（静态）/ 运行期 NOT_RUN | **成立（静态）** | `BookshelfView.qml:21-26` 读 `detailArea.chapters.currentChapterId`，而 `chapters` 是 `BookDetailPanel.qml:105` 的 **`id`**（跨组件不可解析）⇒ 表达式求值失败、`importDialog.open()` 不执行。**运行期未复现**（与盘点一致：需 GUI 会话） |
| **P-6** 工作台三档视图恒空白 | P1 | VERIFIED | **成立（端到端于 catalog 缝）** | [codex-p2-p6-probe.txt](codex-p2-p6-probe.txt)：同一页、同一 Managed Copy——`_ManagedPageCatalog.image_url(page,"original")` 非空，而 `"translated"` 与 `"compare"` 均返回 `''`；`_ManagedReaderCatalog` 对同页解析出非空 `translated_path` ⇒ 不对称 |
| **E-1** offscreen 使字体度量类断言假失败 | P3 | — | **成立** | [codex-e1-offscreen-check.txt](codex-e1-offscreen-check.txt)：`QT_QPA_PLATFORM=offscreen` → `2 failed, 61 passed`；去掉该变量 → `63 passed`（`tests/rendering`） |

## 我新增的子观察（盘点报告未含）

1. **P-1 的影响面更宽**：worker 崩溃后我在同一个 DB 里读回 run 状态仍为 **`running`**——即"点了没反应"之外，运行记录会停在运行中，只能靠下次启动的
   `PipelineService.recover_running_runs()` 兜底（该 API 存在，但本切片未验证其是否被启动流程调用）。
2. **墙的顺序实测**：P-1 → P-2 → P-3。带 Region 的 `OCR_REGION` 计划为 `run`、运行期才 `PROVIDER_NOT_CONFIGURED`；不带 Region 的页级 `ocr` 单元则在
   `handle_ocr` 的第一行 `_require_region` 就被 `INVALID_INPUT` 拦下（`_require_region` 早于 `_chain`）。
3. **对照结论**：同一份生产装配在**主线程**下能跑完整条命令（`completed_with_failures`），因此 P-1 是**纯线程归属**问题，不是装配或数据问题——
   这排除了"装配本身坏了"这一解释。

## 未复核 / 未覆盖（如实声明）

- **P-7～P-10（P2）**：本次未逐条复核（盘点自述其状态，未列入本次委托范围）。
- **P-4 / P-5 的运行时现象**：仍需真实 GUI 会话（点击导入、观察错误上屏）；本次只做到静态与对象树/装配层。
- **`recover_running_runs` 的生产调用点**：未核实。

## 采纳与处置建议（Codex）

- **采纳**：P-1 / P-2 / P-3 / P-4 / P-6 与 E-1 作为**已复核事实**录入
  [10 现状与差距](../../doc/10_CURRENT_STATE_AND_GAPS.md) §11 与 [STATUS](../../doc/STATUS.md)；P-5 记为"静态成立、运行期待 GUI 确证"。
- **优先级建议（待用户批准后另立切片，本文档不释放任何 Task）**：P-1（连接归属/每线程取连接）→ P-2（Region 创建入口 + `detect` handler）→
  P-3（provider 绑定与 settings 写入面，关联 P-8 设置页）→ P-4（`commandError` 上屏）→ P-6（工作台视图解析 translated/compare）。
- **口径建议**：把 E-1 写进 STATUS 的 flaky/环境节——"全仓口径须**不设** `QT_QPA_PLATFORM`"，否则任何 Agent 会拿到两条假失败。
