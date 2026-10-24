# 方向 C · 工坊 Atelier —— 12 状态真相

> 规范来源 `10-ux/13_STATE_MODELS.md §3`。本方向全部 12 个状态都可从 **状态演示面板**（轨道右侧眼睛图标 / `S` / `?state=<key>`）一键切换。
> 键名即 URL 参数：`index.html?state=blocked`。

## 1. 状态的四组基元（不可合并成单一状态灯）

| 组 | 取值 | 本方向表达位置 |
|---|---|---|
| 执行态 | not_started / pending / running / interrupted / cancelled | 矩阵单元符号 + Run 状态带 |
| 结果态 | completed / failed / skipped / stale | 矩阵单元符号 + 事件列 |
| 审阅态 | unreviewed / needs_review / confirmed | REV 列 + 抽屉 + VERIFY 行状态 |
| 保护态 | page_locked / region_locked / translation_locked / inpaint_locked | 抽屉 Region 表 `·锁` + 批量动作跳过原因 |

矩阵行只显示"主状态"（`derived`），四组明细一律在抽屉里可下钻——不允许用单一绿灯概括。

## 2. 十二个状态在本方向的落点

> 面板结构：**12 个主状态（编号 01–12）+ 2 个补充状态（补1/补2）**，头部计数显示 `12 / 12 + 2`。
> 合并说明：规范 §3 的「导入部分失败 / 章节无页面 / 页面无 Region」在面板里被折进 02、03 两条（导入与章节两条主线各带一次失败处置），
> 为避免规范项失去独立演示入口，另以「补1 导入部分失败」「补2 页面无 Region」单列，键名仍可 `?state=import_part_fail` / `?state=page_no_region` 直达。
> 同时按矩阵语义补充了「09 Region 部分完成（同页状态不一致）」与「10 过期 stale」两个高价值真相——它们是本方向矩阵的核心论点。

| # | key | 场景 | 本方向呈现 | 页面可见证据 |
|---|---|---|---|---|
| 01 | `empty` | 空工作区 | 对话框内 `.empty`：数据根 / 缓存路径 / 导入入口 + 引导，无插画 | `?state=empty` |
| 02 | `importing` | 导入中 / 部分失败 | `.import-list` 逐文件状态 + 总进度 18/2/3 + 取消 / 重试失败项 | `?state=importing` |
| 03 | `chapter_empty` | 章节无页面 / 页面无 Region | 「本章还没有页面」+ 上一/下一章；页内未检测到文字区域时给置信阈值 | `?state=chapter_empty` |
| 补1 | `import_part_fail` | 导入部分失败（单列） | 失败文件 + 原因（格式不支持 / 重复页）+ 重试或跳过 | `?state=import_part_fail` |
| 补2 | `page_no_region` | 页面无 Region（单列） | 「022.jpg 未检测到文字区域」+ 阈值 0.30 + 手绘入口 | `?state=page_no_region` |
| 04 | `running` | 流水线运行中 | QUEUE 工作面 + Run 面板：step 5/9、当前页 021、18/2/1/2、暂停/停止 | `?state=running` |
| 05 | `paused` | 暂停中 | 「将在当前步骤（translate）安全结束后生效」；状态带 paused，◐ 停止呼吸 | `?state=paused` |
| 06 | `done_with_fail` | 完成但有失败 | `completed_with_failures` + 「成果已保留」+ 按错误码聚合 + 只重试失败 | `?state=done_with_fail` |
| 07 | `blocked` | 阻塞 | 队列横幅 `R-8828 blocked · Provider 认证失效（401）· 影响 21 页` + 修复配置 / 修复后恢复 | `?state=blocked` |
| 08 | `resume` | 中断恢复 | 三选一对话框：继续（剩余 13 页）/ 重新开始 / 放弃，含影响面 | `?state=resume` |
| 09 | `partial` | Region 部分完成 | 同页 9 Region：OCR/色彩/术语全完成，1 个翻译失败 → 只重试该 Region | `?state=partial` |
| 10 | `stale` | 过期 stale | 上游几何变更 → render 过期，历史版本保留；提供「重跑过期项 / 查看原因」 | `?state=stale` |
| 11 | `review_backlog` | 待确认积压 | 自动切 VERIFY + 筛选 `review`；40 条待确认、当前审阅位置在 Region 检查清单 | `?state=review_backlog` |
| 12 | `danger` | 危险确认 | 停止 Run 对话框：影响对象 5 页、不可撤销标记、`Esc` 可退 | `?state=danger` |

## 3. 状态转换必须留痕（本方向实现）

| 转换 | 实现 |
|---|---|
| 动作开始 | 底部提示条 + 作用域计数（`选中 N 单元 · 作用域 P 页 × S 阶段`），不出现"点了没反应" |
| 动作完成 | 结果摘要（成功/失败/跳过）+ 受影响单元符号更新 |
| 上游 → 下游 stale | 行 derived 变紫 ▨，事件列写「render 过期 ← p019 geometry」，门禁段计数 +1 |
| 乐观锁冲突 | 对话框给「刷新 / 覆盖」两选，绝不静默重试 |
| 暂停生效 | 先说明"本步结束后暂停"，生效后状态带 `paused` + ◐ 停呼吸 |
| 停止生效 | 「18 页成果保留 · 剩余 5 页等待重新排队」 |

## 4. 加载与占位规则

- 首次加载：保留行高/列宽的骨架（矩阵按 22px 行高占位），不用居中 spinner。
- 增量：保留旧内容 + 局部指示，不整页闪白。
- 长任务：必须有分母（`18/23 页`），不单独给百分比。
- 未知时长：不确定进度条 + 当前步骤名，不假装百分比。
- 空态：一句话 + 一个主操作，无插画。

## 5. 错误呈现两级

- **就地**：`.ip-err` / 事件列 / 抽屉「错误码 + 后果 + 建议动作」，例：`ProviderRateLimitError · 翻译被限流，2 次重试后停止 · 建议降低并发或更换 Provider`。
- **汇总**：Run 面板「失败聚合（按错误码）」`ProviderRateLimitError 018 / ModelLoadError 019 / stale render 020`，可展开到对象。

错误码取自 `00_SAMPLE_DATA §6`：`ProviderRateLimitError`、`ModelLoadError`、`MissingOCRText`、`LockBlocked`、`INPUT_REVISION_CHANGED`、`ProxyConnectionError`（+ `OutputMappingError` 用于 R-8829）。

## 6. 状态与门禁的关系

门禁是**状态的聚合视图**，不是独立状态机：`DETECT 通过 → OCR 78% 有 2 异常 → VERIFY 41% → INPAINT 63% 有 4 异常 → RENDER 52% 有 9 异常`。RENDER 未通过时导出对话框必须给出「先修复 12 页 / 仍然导出（报告标注）」两条路径，不允许无声导出半成品。
