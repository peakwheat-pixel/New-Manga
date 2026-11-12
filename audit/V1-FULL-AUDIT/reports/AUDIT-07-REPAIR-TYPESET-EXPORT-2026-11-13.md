# AUDIT-07：图片修复、排版与导出

**阶段状态：PARTIAL。** 当前证据覆盖活动 Python Core 的合成遮罩/修复、Pillow 排版与合成、rerender 预览、字体数据面和版本恢复。真实修复模型、真实漫画质量、Avalonia 实际缩放交互及视觉导出质量均未验证。严重度与正式问题归属留给 ZCode 复核。

## 固定范围与方法

- 产品基线：`10e4ee013835605800d3830fb960ae8d3aa04167`；测试生成 HEAD：`4daa7169752b8f9c85fd8f8a01e5660f98f10481`；分支 `main`。
- Task 范围只修改 `audit/V1-FULL-AUDIT/**` 与获准的治理指针；静态捕获确认 `src/apps/tests/requirements.txt/requirements-dev.txt/doc/contracts` 相对产品基线无 diff（EXIT 0）、审计工作树越界路径为 0。审计没有改产品源码、现有产品测试、契约、Schema、依赖或模型文件。
- 测试通过 `tests/audit_runner.py` 运行。图片、数据库和导出目标为测试生成的合成数据，隔离临时目录位于 `New Manga.workspace/task-env/NEW-MANGA-V1-FULL-AUDIT/`。未读取用户漫画，不下载权重，不调用 Vision 或付费 API。
- runner 源码 pin：`4daa7169752b8f9c85fd8f8a01e5660f98f10481`。命令、cwd、Python 3.14 interpreter、生成 HEAD、UTC、elapsed 和 pytest EXIT 均保存在对应日志与 JSON。

## 实现路径核对

### 遮罩、原文清理与回退

- 活动 Core 的 `application.translation.inpaint.mask` 从 Region box / polygon 产生掩码；box 越界会拒绝，polygon 扫描限制在页边界。refine 顺序为 erode 再 dilate，并保证最终遮罩覆盖 raw mask。代码中 `min_region_pixels`、`keep_largest_component` 与 `feather_radius` 没有由当前无依赖 refinement 算法执行；它们不是本轮实测的有效图像处理能力。
- 当前唯一已实现的修复 provider 是 `simple-fill`（掩码内纯色填充）与 `edge-bleed`（邻接像素扩散的结构性基线）。`manga-lama`、`aot-gan`、`brushnet`、`flux-fill` 虽在 route/registry 中声明，但即使依赖被报告可用也保持 `not_implemented` / `implements=false`，不会模拟模型输出或自动越过显式路由策略。
- provider 在尺寸不符、未实现 route、非目标像素变化等情况走 typed failure；成功的重新修复要求生成新的 Clean revision。38 个 inpaint/pipeline 测试覆盖合成几何、fallback/provenance、锁和新 revision；不证明修复质量、边缘连续性或模型性能。

### 排版、字体和像素合成

- `bootstrap.core_service.assemble_production_core` 为活动 headless Core 注入 `PillowFontCatalog`、`PillowTextLayoutEngine` 与 `PillowImageCompositor`。活动 Pillow catalog 只索引 Windows `Fonts` 并按固定链回退；布局使用矩形 region 的宽高、字体度量与横排/竖排分支。没有证据证明它使用气泡轮廓约束、视觉重心或真实漫画标注。
- `application.rendering.style` 提供可信源字号、置信度不足时回退 26px、字号 offset 与 `shrink_to_fit`。自动模式只缩小，不自动放大；手动模式保留用户指定字号，即便文本超出 box。Pillow 实际合成测试生成 PNG 并检查文字像素变化，但不覆盖多种 Windows 字体下的人工观感。
- FEA-14-FONT-1 明确把字体渲染消费留给 FONT-2；其字体库数据面将用户字体复制到 Core `data/fonts/`，而当前 `PillowFontCatalog` 只扫描 Windows `Fonts`。因此本轮不把用户导入字体可供当前 Pillow renderer 使用记为已实现；这是已登记的 FONT-2 限制。
- 仓库没有已跟踪的 `.ttf/.otf/.woff/.woff2` 或模型权重文件。字体服务接受可选 `license_note` 字符串，但不验证许可证真伪或授权范围；该字段只是用户备注。FEA-14-FONT-1 记录内置字体默认空、不随包分发。实际用户字体权利与外部字体许可本轮 `NOT_RUN`，没有据此声称已取得许可。

### revision、预览与导出

- `rerender_page` 将当前 Clean 图像与 region 排版结果合成新的 translated PNG revision；provenance 标记 `ai_invoked=false`。Core stdio 测试用 NMFR 合成帧验证预览可读、目标文字区域发生变化、未编辑/SFX 区域像素保持不变。
- Region revision wire 有 list/restore 现有版本机制，不依赖模拟 Undo/Redo；独立 `test_rc4_revision_commands.py` 覆盖恢复历史、冲突零写入与并发竞争。
- 导出质量没有真实图像前后对照、人工视觉评分或量化画质指标。Core reader export 的相邻 hook 选项测试在本轮出现 3 个失败；这些检查不比较排版图像质量，故单独登记，待 ZCode 判断是否归入本阶段或既有导出问题。
- Avalonia repair tab 静态可见 `rerender_page` 接线；“换 Mask / 换路线 / 重新修复”控件明确禁用并显示“能力待接入”。batch viewmodel 有 `reinpaint_*` 命令映射，但本轮没有真实 UI 会话，因此没有验证屏幕缩放后的坐标、鼠标编辑、焦点、命令执行或导出观感。

## 验证矩阵

| 原始检查项 | 结果 | 证据和边界 |
|---|---|---|
| 文本区域蒙版 | PARTIAL（合成） | box/polygon、refine 覆盖 raw、序列化 round-trip 与边界错误有测试；无真实气泡 mask/标注对照。 |
| 原文消除 | PARTIAL | simple-fill/edge-bleed 的掩码内像素行为和非目标保护通过；learned inpaint routes 未实现。 |
| LaMa 等真实链路 | NOT_IMPLEMENTED | route table、provider registry 与测试均声明 fail-closed；权重与推理 `NOT_RUN`。 |
| 修复 fallback | PARTIAL（合成策略） | 显式 allowed/fallback route 和 provenance 有测试；不证明真实模型故障后的质量。 |
| 图片边界 | PARTIAL（合成） | box 越界拒绝、polygon 裁边及 region composition clipping 有测试；极大分辨率/异常尺寸未压测。 |
| 修复质量 | NOT_RUN | 没有真实模型、真实图像或人工 GT；simple-fill/edge-bleed 只证明像素写入机制。 |
| 消除区域与翻译区域一致性 | PARTIAL（代码/合成） | Region ID 与 geometry 输入贯通；未对真实检测框、屏幕缩放或多 Region 漂移做端到端实测。 |
| 字体加载 | PARTIAL | 活动 renderer 的系统字体选择/回退有测试；用户字体库到 Pillow 渲染仍是 FONT-2 limitation；许可证不校验。 |
| 文本框计算、换行与字号 | PARTIAL（合成） | 布局、自动缩小、手动字号、horizontal/vertical 与 overflow 测试通过；仅矩形 box 和本机字体环境。 |
| 气泡适配 | NOT_RUN（视觉质量） | 后端输入是矩形 region box；未在不规则气泡形状或真实页面上验证。 |
| 日/韩/中文渲染 | PARTIAL（合成） | 文本绘制与 searchable CJK export tests 通过；未评估实际安装字体覆盖率、字形质量或人工样本。 |
| 缩放后的编辑结果 | NOT_RUN | 没有真实 Avalonia GUI 会话；坐标缩放与指针编辑无实测。 |
| Undo/Redo 或修订机制 | PARTIAL（合成） | Region revision list/restore 与新 revision 通过 7 项 wire tests；没有 GUI Undo/Redo 操作演练。 |
| 导出前后质量变化 | NOT_RUN（视觉比较） | 合成 rerender preview 验证修改区/保留区像素差异；无真实导出页质量对照。 |
| 导出旁路观察 | REVIEW_PENDING | 3 个 P16 reader export hook option 参数化用例失败，详见下节；不从中推导 D07 图像质量问题。 |

## 命令与测试结果

| runner 名称 | 测试范围 | 结果 | EXIT |
|---|---|---:|---:|
| `audit07-inpaint-pipeline-20261112T205159956924Z` | `test_inpaint.py` + `test_handlers_pipeline.py` | 38 passed / 0 skipped | 0 |
| `audit07-rendering-20261112T205159956924Z` | Pillow layout/compositor/rerender/style/defaults | 73 passed / 0 skipped | 0 |
| `audit07-core-rerender-export-20261112T205159956924Z` | font wire、settings、production rerender preview、P16 reader export | 127 passed / 3 failed / 0 skipped | 1 |
| `audit07-pillow-source-style-20261112T205159956924Z` | active Pillow source style | 5 passed / 0 skipped | 0 |
| `audit07-font-storage-20261112T205159956924Z` | user font data service/storage | 6 passed / 0 skipped | 0 |
| `audit07-searchable-export-20261112T205159956924Z` | searchable CJK font/export | 7 passed / 0 skipped | 0 |
| `audit07-revision-restore-20261112T205631263951Z` | Core list/restore region revision wire | 7 passed / 0 skipped | 0 |

累计 **263 passed / 3 failed / 0 skipped**。两条 Pillow `Image.getdata()` 弃用警告已保留在原始日志，不改变各自 pytest EXIT。

### 邻接 reader export 失败

失败均来自 `tests/core/test_p16_reader_export.py::test_export_hook_effective_options_match_content_and_history`：ZIP 的 `compression=store` override 返回 `standard`；text 的 `text_representation=json` override 返回 `txt`；空 override 案例期望两条 `hook_invoked` 事件，实际为 0。测试报告 EXIT 1。它检查 reader export hook/options 与历史记录，不测试排版像素质量；没有为此修改产品代码，也未创建/定级正式 issue ID。候选 `AUDIT-07-CAND-001`：归属与严重度 `REVIEW_PENDING`，交 ZCode 复核。

### 用户字体许可证备注

`AUDIT-07-CAND-002` 是范围观察：字体服务把可选 `license_note` 当普通文本保存，不验证许可真伪或授权范围；FEA-14-FONT-1 又明确默认不随包分发字体，并把字体渲染消费留给 FONT-2。本轮没有访问用户字体或核验外部许可，tracked font assets 为 0；没有证据表明发生未授权分发。候选状态为 `REVIEW_PENDING`，由 ZCode 判断该边界是否已被既有 FONT-1 limitation 覆盖，或需另开需求/Task；本审计不改变字体导入语义。

## 未执行与结论

- 真实 LaMa/AOT-GAN/BrushNet/FLUX 权重、CPU/GPU 推理、性能/内存/释放、人工 mask/GT、真实漫画和像素级视觉质量：`NOT_RUN` 或 route `NOT_IMPLEMENTED`。
- Avalonia GUI/TestHost、真实 DPI/缩放、手动改 mask/region、真实 font fallback 和导出视觉对比：`NOT_RUN`。
- 用户字体许可证来源/授权核验：`NOT_RUN`；仓库未跟踪字体，不等于用户字体已获许可。
- Task 全局 AC2/AC3/AC4 继续 `PARTIAL`，Release Gate 继续 `BLOCKED`，Task 保持 `in_progress`。AUDIT-07 只能作为合成链路与代码路径证据，不能宣称真实图像质量、GUI 可用性或全阶段 PASS。下一项按任务 DAG 执行 AUDIT-09；AUDIT-07-CAND-001/002 均由 ZCode 最终裁决。
