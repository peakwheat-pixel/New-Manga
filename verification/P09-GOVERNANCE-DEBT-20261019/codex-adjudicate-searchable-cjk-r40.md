# SEARCHABLE-PDF-CJK-1 裁定（r40）

日期：2026-10-20  
裁定人：Codex（Lead / Architect / Integrator）  
范围：任务激活、语种/混排边界、体积验收及“可搜索 PDF 默认关闭”事实核对。

## 裁定摘要

| 项目 | 裁定 |
|---|---|
| 3.1 Plan 激活 | **选择 C：先登记为 blocked 节点，待字体嵌入许可审查和任务范围冻结后再释放实现。** 该工作不属于已终态 Plan 的现有授权。 |
| 3.2 混排 | **选择 A + C：AC 仅承诺纯 JA、KO、ZH 及拉丁文本页；同页 zh+ko 等无单一候选字体覆盖的混排必须 fail-closed，并记录为 limitation。** 不静默降级成无文本 PDF。 |
| 3.3 体积 | **AC3 的“≤纯图片 PDF 3 倍”不保留为硬门槛；选择 C。** 保留真实字节数测量与解释作为证据，向用户提供图片 PDF / 可搜索 PDF 选择。AC4 的跨页字体共享可继续作为可验证要求。 |
| 默认选项 | **可搜索 PDF 已接入产品 UI，属于用户可选功能；默认是 image-only。** 用户在工作台选择 PDF 后，可通过“PDF 内容”下拉框选择“可搜索双层”。这不是未接线功能，但界面没有解释字体覆盖限制或体积代价。 |

以上为本文件中的治理裁定；**本次未修改 `REBASELINE_PLAN` 或 Task 状态**。因此 `SEARCHABLE-PDF-CJK-1` 仍为 `proposed`，尚未获得实现授权。落实 Plan 节点与后续状态变更需在对应授权范围内另行更新权威文件。

## 一、默认路径与用户可发现性

源码核对结果：

- `src/application/export/service.py:494-498` 仅当 `format_options.pdf_content == "searchable_dual_layer"` 时调用 `compose_searchable`；缺省或其他值走普通 `compose()`。因此服务层默认确实输出图片 PDF。
- `apps/desktop/frontend/src/workbench/ExportDialog.tsx:31` 将 `pdfContent` 初始化为 `image_only`；第 54 行把该值放入 `format_options`；第 82 行在用户选择 PDF 时显示“PDF 内容”选项，明确提供“仅图像”和“可搜索双层”。
- `apps/desktop/frontend/src/workbench/ExportDialog.test.tsx` 验证用户选择 `searchable_dual_layer` 后该值会发送给 `onStart`。`tests/core/test_p16_reader_export.py:523-524` 也分别覆盖 image-only 与 searchable 两种选项。

结论：不是“功能存在但没有接线”。它已进入 Core 服务路径，并在工作台作为显式选项呈现。默认 image-only 是实际产品默认值，避免在用户未选择文本层时承担字体缺失/文件变大的结果；现有证据没有显示这是经用户单独裁定的设计决定。选项对用户可见，但“可搜索双层”没有附带 56 倍体积实测或语言覆盖说明。

## 二、现有证据与需纠正的任务陈述

采用的来源：

- `doc/tasks/SEARCHABLE-PDF-CJK-1.md`
- `doc/tasks/PDF-STREAM-FIX-1.md`
- `verification/PDF-STREAM-FIX-1/searchable-pdf-real-page-verification.md`
- `verification/PDF-STREAM-FIX-1/searchable-pdf-real-page-result.json`
- `src/infrastructure/export/qt_free.py`
- `src/application/export/service.py`
- `apps/desktop/frontend/src/workbench/ExportDialog.tsx`
- `doc/REBASELINE_PLAN.md`

真实页结果证明：带 searchable 选项可嵌入 `P16ExportFont`，并逐字提取 JA、ZH 和拉丁混排文本；同一 82,862-byte 源图得到 12,632,851-byte searchable PDF，对照 image-only PDF 224,454 bytes，约 56.3 倍。该数字是单页实测，不能据此推断每增加一页都会重复增加一份完整字体。

**SEARCHABLE-PDF-CJK-1 对字体重复嵌入的描述与当前源码不一致。** `qt_free.py:43` 在页面循环之前调用一次 `_embedded_font`；`qt_free.py:56` 在同一循环之前只创建一次 `font_file` 对象；`qt_free.py:73` 才进入页面循环。后续各页引用同一 `font_refs`。因此按当前实现，一份 PDF 中字体对象是每份文档创建一次并由多页共享，不是每页重新嵌入完整字体。PDF-STREAM 验证只测了一页，尚无多页体积证据；“200 页会重复 200 次”及“文件体积随页数线性重复字体”应从 Task 中撤回或修正。真实多页尺寸增长仍应作为 AC4 验证，不能只凭代码检查宣布已验收。

AC3 原文已有“≤3 倍；或记录并解释为什么做不到”的替代条款。该替代条款应成为本次范围下的实际验收口径：交付实际字节数、页数、字体/图像构成和解释；不得把 3 倍作为阻断完成的硬阈值。若没有子集化，保留体积限制并让用户在两种 PDF 内容模式间选择。不得为满足比例而降低文本层质量。

## 三、语种和混排范围

Task 提供的 cmap 实测显示：`malgun.ttf` 覆盖韩文、日文假名及拉丁字符但不覆盖中文；`msyh.ttc` 覆盖中文、日文及拉丁字符但不覆盖韩文；本机没有覆盖 zh+ko 的单一候选字体。现有 `_embedded_font` 契约为全页选择一个字体，并在任一非空白字符缺失时抛 `ValueError`。

因此冻结此 Task 的最小产品承诺为：

- AC1 明确为纯韩文页可被真实提取；候选列表须纳入实测含 Hangul 的本机字体。
- AC2 分别验证 JA、KO、ZH、拉丁真实页端到端提取。每页文本只要求该页选中的单一字体完整覆盖。
- **不承诺同一页 zh+ko 或其他无单字体覆盖组合。** 对此类页面维持 fail-closed 并报告明确错误；不得悄悄导出 image-only 并宣称 searchable 成功。
- `malgun.ttf` 的系统来源和字体嵌入/随 PDF 输出的许可须在释放实现前审查。许可证未判明前，此 Task 不进入可执行状态；不引入网络下载字体。

多字体回退或多字体 PDF 嵌入属于新范围，当前不纳入此 Task。

## 四、Plan 与实施状态

`doc/REBASELINE_PLAN.md` 当前将 `PDF-STREAM-FIX-1` 记为 `closed_with_limitations`，其后没有 SEARCHABLE-PDF-CJK-1 节点，Plan 表尾为 `READY 节点：无`。故不能以新 Task 的 `proposed` 状态直接开始实现。

治理决定采用题目选项 **C**：将其作为 **blocked** 节点登记，阻塞理由为字体嵌入许可尚待审查；同时先按本裁定修订 AC，明确纯语种承诺、混排 limitation、AC3 的实测记录口径及 AC4 的真实多页验证。只有许可证审查完成且范围在 Plan 中冻结后，才能解除阻塞并释放实现。

由于本轮授权只允许写本 adjudication 文件，**没有改 Plan、Task 的 `status:` 或其他文件**；此文件不代表 Plan 已实际增加 blocked 节点，也不授予实现权限。

## 五、执行边界与下一步

本次仅写本裁定文件。下一步应由项目治理协调者在获准的治理变更中：①审查并记录 `malgun.ttf` 嵌入许可；②将上述 AC 裁定写回 Task；③按协作协议登记 blocked Plan 节点并更新权威指针。许可证与任务范围均确认后，再决定是否释放实现。当前不得基于本文件直接开工。
