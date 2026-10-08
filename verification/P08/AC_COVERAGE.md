# P08 D08逐项覆盖索引

固定来源：[D08](../../doc/08_ACCEPTANCE_CRITERIA.md)。编号AC和发布/总Gate逐项列出。本表的`NOT_RUN`记录新架构 To-Be 路由状态，不覆盖[doc/13](../../doc/13_ACCEPTANCE_TRACEABILITY.md)中绑定历史commit的12条Legacy `PASS`：AC-REGION-001..004、AC-OCR-002、AC-TRANS-001/002、AC-REV-003/004、AC-DOC-001/002/003；其原证据仍以doc/13逐行链接为准。未编号ACG主题（§51/56/57/59/60/62/63/64/67）及§78仍为草案的AGENT-001/002、FONT-003、SAKURA-002/003、ACG-EXT-DETECT、ACG-EXT-CONTRACT、ACG-EXT-NFR继续由doc/13追踪，不在本表重复；§74/75与§79是建议性内容，不作为独立验收项或单独PASS。AC-DOC-001..003是§66正式开发前Gate：历史PASS不自动关闭新架构Gate，Architecture Documentation Rebaseline Task完成目标架构映射后、且在P09开发释放前逐项核定。D1–D7已确认，表内工作包均未认领；结果均NOT_RUN。各行区分建议实现切片与验收职责；失败后修复另立Task。D08 §73/76门槛保持；全库备份和模型下载已选入。新增非D08编号格式验收见SCOPE_DRAFT的P08-FMT表；P08-FMT临时权威来源为该表与P16/P17契约，须由单独授权的Architecture Documentation Rebaseline Task转录至D08或doc/13后，才能成为长期追踪项。

| D08项 | 原标题/要求 | 建议实现切片（未认领） | 验收责任 | 决策处理 | 结果 |
|---|---|---|---|---|---|
| AC-NAV-001 | [P0] 默认进入书架 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NAV-002 | [P0] 一级页面只有四个 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NAV-003 | [P1] 一级页面切换保持上下文 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-WIN-001 | [P1] 固定位置优先 | ZCode UI切片：P12/P14/P15/P17按窗口所属页面分配；P20只测安装包 | ZCode提供实际UI/Windows证据；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；UI行为由对应页面实现，P20不承担功能实现 | NOT_RUN |
| AC-WIN-002 | [P1] 编辑窗 Dirty Close | ZCode UI切片：P12/P14/P15/P17按编辑窗所属页面分配；关闭确认实现与AC-CLOSE-001/002共享 | ZCode提供编辑窗交互证据；DSH分别验证编辑窗脏数据与应用运行/脏状态关闭边界；Codex集成 | INCLUDED：用户D5/D7；AC-CLOSE-001/002另保留应用级证据 | NOT_RUN |
| AC-WIN-003 | [P1] 查看类外部关闭 | ZCode UI切片：P12/P14/P15/P17按查看窗所属页面分配 | ZCode提供实际UI证据；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；查看类与编辑/危险确认类关闭边界保持 | NOT_RUN |
| AC-WIN-004 | [P1] 悬浮窗内容不溢出 | ZCode UI切片：P12/P14/P15/P17按窗口所属页面分配 | ZCode提供DPI/长文本/窗口尺寸证据；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；功能实现归对应UI Task | NOT_RUN |
| AC-WIN-005 | [P1] 双屏拖动 | ZCode UI/窗口切片：P12/P14/P15/P17按窗口所属页面分配；P20平台矩阵 | ZCode提供双屏真实Windows证据；P20执行矩阵；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；P20仅承担平台Gate与打包验证 | NOT_RUN |
| AC-WIN-006 | [P1] 第二屏消失恢复 | ZCode UI/窗口切片：P12/P14/P15/P17按窗口所属页面分配；P20平台矩阵 | ZCode提供断开/恢复真实Windows证据；P20执行矩阵；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；P20仅承担平台Gate与打包验证 | NOT_RUN |
| AC-LIB-001 | [P0] 新建 Book | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LIB-002 | [P1] 自定义标签 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LIB-003 | [P1] 收藏 / 归档与 Tag 分离 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LIB-004 | [P1] 最近打开与阅读摘要 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CH-001 | [P0] Book → Chapter → Page | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CH-002 | [P0] Paged Chapter | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CH-003 | [P0] Webtoon Chapter | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CH-004 | [P1] 同一 Book 混合类型 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-IMPORT-001 | [P0] Managed Copy | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-IMPORT-002 | [P0] 用户源文件不修改 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-IMPORT-003 | [P0] Copy 中断不产生坏 Page | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-IMPORT-004 | [P1] Unicode 路径 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-IMPORT-005 | [P1] 重复检测 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PAGE-001 | [P0] Page 顺序 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PAGE-002 | [P1] 多选范围 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PAGE-003 | [P1] Page 状态 | P09/P12 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-WEBTOON-001 | [P0] 一张长图 = 一张 Page | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-WEBTOON-002 | [P0] Tile 不是 Page | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-WEBTOON-003 | [P0] 坐标回映 | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-WEBTOON-004 | [P1] 按宽缩放 | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-WEBTOON-005 | [P1] Scroll 恢复 | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REGION-001 | [P0] Region 统一模型 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REGION-002 | [P1] 几何编辑 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REGION-003 | [P1] Reading Order | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REGION-004 | [P1] Region Type | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-OCR-001 | [P0] 单 Region OCR | P13/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-OCR-002 | [P0] Re-OCR 不覆盖人工译文 | P13/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-OCR-003 | [P1] OCR Provider 优先级 | P13/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-OCR-004 | [P1] 韩漫 OCR | P13/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SFX-001 | [P1] 默认 Skip | P13/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SFX-002 | [P1] Translate | P13/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SFX-003 | [P1] Manual | P13/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CONSTRAINT-001 | [P0] 优先级 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CONSTRAINT-002 | [P0] 人工锁定优先 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CONSTRAINT-003 | [P1] Candidate Status | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CONSTRAINT-004 | [P1] Rejected 不重复推荐 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TM-001 | [P0] 未确认机器译文不写 TM | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TM-002 | [P0] 人工确认写 TM | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TM-003 | [P1] 查询优先级 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TM-004 | [P1] TM 不覆盖人工译文 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRANS-001 | [P0] 四级文本 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRANS-002 | [P0] 人工编辑自动保护 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRANS-003 | [P0] Context 与 Write Scope | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRANS-004 | [P1] 多页上下文排序 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOCK-001 | [P0] Page Lock | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOCK-002 | [P0] Region Lock | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOCK-003 | [P0] Translation Lock | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOCK-004 | [P0] Inpaint Lock | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOCK-005 | [P0] 写入时再次检查 Lock | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REV-001 | [P0] 成功重跑创建新 Revision | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REV-002 | [P0] 失败不改变 current | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REV-003 | [P1] Pin | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-REV-004 | [P1] 恢复 Revision | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STYLE-001 | [P0] 自动字号 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STYLE-002 | [P1] Offset 范围 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STYLE-003 | [P0] Shrink-to-fit | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STYLE-004 | [P1] 不自动放大 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STYLE-005 | [P1] Region 关闭自动字号 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-INPAINT-001 | [P0] Mask 持久化 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-INPAINT-002 | [P0] 新 Clean 不覆盖旧版本 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-INPAINT-003 | [P1] Router provenance | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-INPAINT-004 | [P1] Webtoon Color Route | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RENDER-001 | [P0] 重新渲染不触发 OCR | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RENDER-002 | [P0] 缺 Clean 时阻止 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RFULL-001 | [P0] 完整链 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RFULL-002 | [P0] 只写目标 Region | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RFULL-003 | [P0] Page / Region Lock 阻止 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RFULL-004 | [P0] 专项 Lock 临时覆盖 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RFULL-005 | [P0] 人工结果保护点 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CMD-001 | [P0] 全部翻译复用 OCR | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CMD-002 | [P0] 跳过已翻译 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CMD-003 | [P1] 选择页目标冻结 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CMD-004 | [P1] 单页命令 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PIPE-001 | [P0] StepRun 可追踪 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PIPE-002 | [P0] 有效 Step 可 Skip | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PIPE-003 | [P0] Stale 不当作 Valid | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PIPE-004 | [P0] Missing prerequisite | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PAUSE-001 | [P0] 暂停请求 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PAUSE-002 | [P0] 安全边界 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PAUSE-003 | [P0] 继续 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STOP-001 | [P0] 停止不回滚 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STOP-002 | [P0] Pending Cancel | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-STOP-003 | [P0] Stop 不是 Delete | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CRASH-001 | [P0] Running → Interrupted | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CRASH-002 | [P0] Resume | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CRASH-003 | [P0] Temp Artifact | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RETRY-001 | [P0] 失败保留上游结果 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-RETRY-002 | [P1] 失败页重试 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROGRESS-001 | [P0] 固定底部 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROGRESS-002 | [P0] 显示内容 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROGRESS-003 | [P0] 当前 Page 定位 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROGRESS-004 | [P1] 失败统计联动 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROGRESS-005 | [P1] 完成统计联动 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROGRESS-006 | [P0] CompletedWithFailures | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROGRESS-007 | [P0] PageList 同源 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROVIDER-001 | [P1] 同 Provider 多 Profile | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROVIDER-002 | [P0] Capability 默认绑定 | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROVIDER-003 | [P0] Run Snapshot | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PROVIDER-004 | [P0] Provider 消失后的恢复 | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-FALLBACK-001 | [P0] 无配置不跨 Provider | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-FALLBACK-002 | [P1] 显式 fallback | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NET-001 | [P0] 多 Network Profile | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NET-002 | [P0] Proxy Failure 不静默 Direct | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NET-003 | [P0] 显式 Direct Fallback | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NET-004 | [P1] Connection Test 分阶段 | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SEC-001 | [P0] SQLite 无 Secret 明文 | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SEC-002 | [P0] 日志无 Secret 明文 | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SEC-003 | [P0] Credential Manager | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SEC-004 | [P0] TLS 默认开启 | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-SEC-005 | [P1] 关闭 TLS 必须确认 | P10/P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-ART-001 | [P0] 成功 Commit | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-ART-002 | [P0] Commit 中断 | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-ART-003 | [P0] Hash | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-DB-001 | [P0] Foreign Key | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-DB-002 | [P1] WAL | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-DB-003 | [P0] Migration 前备份 | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-DB-004 | [P0] Migration 失败 | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-DB-005 | [P0] 新 Schema 被旧 App 打开 | P11/P13/P19 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-BACKUP-001 | [P0] 手动备份 | P15全库备份契约/Core/UI；依赖P13停写排空；Codex→Antigravity→ZCode | DSH故障注入；Codex检查连接回收/回滚/Managed Copy声明 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-BACKUP-002 | [P1] 自动备份 | P15全库备份契约/Core/UI；依赖P13停写排空；Codex→Antigravity→ZCode | DSH故障注入；Codex检查连接回收/回滚/Managed Copy声明 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-BACKUP-003 | [P0] Restore 前再次备份 | P15全库备份契约/Core/UI；依赖P13停写排空；Codex→Antigravity→ZCode | DSH故障注入；Codex检查连接回收/回滚/Managed Copy声明 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-BACKUP-004 | [P0] Restore 不改源文件 | P15全库备份契约/Core/UI；依赖P13停写排空；Codex→Antigravity→ZCode | DSH故障注入；Codex检查连接回收/回滚/Managed Copy声明 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRASH-001 | [P0] 软删除 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRASH-002 | [P1] Batch Restore | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRASH-003 | [P0] 永久删除确认 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-TRASH-004 | [P0] 源文件安全 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-EXPORT-001 | [P0] 格式 | P16/P17；D08“单图”到PNG的映射按D1/D2用户选择并由P16契约冻结 | DSH独立验证；Codex集成 | INCLUDED：D08原文只写单图/ZIP；PNG是用户选定首发格式，不声称D08原文限定PNG | NOT_RUN |
| AC-EXPORT-002 | [P1] ExportHistory | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-EXPORT-003 | [P1] Stale 提示 | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-READ-001 | [P0] Original / Translated | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-READ-002 | [P1] 独立阅读进度 | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-READ-003 | [P1] RTL | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-READ-004 | [P1] LTR | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-READ-005 | [P1] Webtoon Vertical | P16/P17 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PERF-001 | [P1] 冷启动 | P13/P14/P17（性能缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PERF-002 | [P1] 一级页面切换 | P13/P14/P17（性能缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PERF-003 | [P1] 固定面板响应 | P13/P14/P17（性能缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PERF-004 | [P1] Book 搜索 | P13/P14/P17（性能缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PERF-005 | [P1] Translation Memory Exact | P13/P14/P17（性能缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PERF-006 | [P1] Translation Memory Fuzzy | P13/P14/P17（性能缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CAP-001 | [P1] Library | P09/P13/P17（容量缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CAP-002 | [P1] Chapter 1000 Page | P09/P13/P17（容量缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CAP-003 | [P1] 200 Region | P09/P13/P17（容量缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CAP-004 | [P1] 200k Webtoon | P09/P13/P17（容量缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-MEM-001 | [P1] Core Idle | P09/P13/P17（内存缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-MEM-002 | [P1] 连续切页 | P09/P13/P17（内存缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-MEM-003 | [P1] Floating Window | P09/P13/P17（内存缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-GPU-001 | [P0] GPU OOM 不崩主程序 | P18/P20 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-GPU-002 | [P1] GPU Heavy 默认单并发 | P18/P20 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-GPU-003 | [P1] CPU Fallback 可追踪 | P18/P20 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CACHE-001 | [P0] 清 Cache 不删业务真值 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CACHE-002 | [P0] Pinned 不清理 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CACHE-003 | [P0] Active Pipeline 输入保护 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-DISK-001 | [P1] 低磁盘 | P13/P15（磁盘缺口另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOG-001 | [P1] Log Rotation | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOG-002 | [P1] Step 错误信息完整 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-LOG-003 | [P1] Diagnostic Bundle | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NFR-UI-001 | [P0] AI 不阻塞 UI | P12/P14/P15/P17（UI瓶颈另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-NFR-UI-002 | [P1] Progress 节流 | P12/P14/P15/P17（UI瓶颈另立修复Task） | DSH验证；ZCode提供UI/Windows环境证据；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-PKG-001 | [P0] PyInstaller onedir | P20 target-installer包装切片；须由Architecture Documentation Rebaseline Task形成新架构等价条目后执行 | ZCode提供目标安装包与环境证据；DSH独立验证；Codex集成 | INCLUDED：用户D5门槛/优先级不变；原PyInstaller语义属Legacy，目标架构等价核定前NOT_RUN | NOT_RUN |
| AC-PKG-002 | [P0] 干净 Windows 启动 | P20 Tauri/Python Sidecar安装包切片；Architecture Documentation Rebaseline Task先映射D08发布证据 | ZCode提供全新Windows环境证据；DSH独立验证；Codex集成 | INCLUDED：用户D5门槛/优先级不变；目标安装包独立验证，不继承PyInstaller/QML PASS | NOT_RUN |
| AC-PKG-003 | [P0] Qt DLL | Architecture Documentation Rebaseline Task须先给出目标架构等价要求；实现/验证分配依新条目 | Codex映射；DSH独立验证；Codex集成 | INCLUDED：用户D5门槛/优先级不变；Qt DLL语义属Legacy，目标等价核定前NOT_RUN，不造空洞PASS | NOT_RUN |
| AC-OPTIONAL-001 | [P0] 缺重型模型仍可启动 | P20目标安装包；P18仅负责模型/质量资格证据 | ZCode提供安装包证据；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；目标架构Gate映射完成前NOT_RUN | NOT_RUN |
| AC-OPTIONAL-002 | [P1] Provider 状态 | P15设置/Provider UI；P20另验安装包 | ZCode提供Provider状态及安装包证据；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；P18不承担设置或包装实现 | NOT_RUN |
| AC-MODEL-001 | [P1] 下载进度 | P15模型下载契约/Core/Host/UI；Codex→Antigravity→ZCode | DSH验证下载/断点/Ready语义；P20另验安装包 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-MODEL-002 | [P0] 不完整模型不 Ready | P15模型下载契约/Core/Host/UI；Codex→Antigravity→ZCode | DSH验证下载/断点/Ready语义；P20另验安装包 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CONFLICT-001 | [P0] Optimistic Write Guard | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CONFLICT-002 | [P0] 同能力写冲突 | P13/P14/P18 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CLEAN-001 | [P0] Current 不清理 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CLEAN-002 | [P0] 用户源文件不清理 | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CLEAN-003 | [P1] Debug Artifact | P15 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CLOSE-001 | [P0] 运行任务关闭 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-CLOSE-002 | [P0] Dirty + Running 分离 | P11/P13/P14 | DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| AC-DOC-001 | [P1] 01~08 文件齐全 | Architecture Documentation Rebaseline Task（P09前单独登记/释放） | Codex映射；DSH独立核对；不代表产品实现 | INCLUDED：§66正式开发前Gate；doc/13历史PASS仅是Legacy证据，新架构核定前为NOT_RUN | NOT_RUN |
| AC-DOC-002 | [P1] 核心术语统一 | Architecture Documentation Rebaseline Task（P09前单独登记/释放） | Codex映射；DSH独立核对；不代表产品实现 | INCLUDED：§66正式开发前Gate；doc/13历史PASS仅是Legacy证据，新架构核定前为NOT_RUN | NOT_RUN |
| AC-DOC-003 | [P1] 四个一级页面统一 | Architecture Documentation Rebaseline Task（P09前单独登记/释放） | Codex映射；DSH独立核对；不代表产品实现 | INCLUDED：§66正式开发前Gate；doc/13历史PASS仅是Legacy证据，新架构核定前为NOT_RUN | NOT_RUN |
| AC-EXT-IMPORT-003 | [P2] 未加密 PDF 按页导入 | P09输入契约/Core/Host→P12 UI；Codex→Antigravity/ZCode | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | INCLUDED：用户D2选入PDF输入；逐格式安全Gate | NOT_RUN |
| AC-EXT-IMPORT-004 | [P2] 加密或损坏 PDF 零半成品拒绝 | P09输入契约/Core/Host→P12 UI；Codex→Antigravity/ZCode | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | INCLUDED：用户D2选入PDF输入；逐格式安全Gate | NOT_RUN |
| AC-EXT-PLUGIN-001 | [P2] 本地插件 Hook 按 Schema 执行 | 首发延期；未来另授权独立扩展Task | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | DEFERRED：用户D6；目标保留，非PASS/N/A | NOT_RUN |
| AC-EXT-PLUGIN-002 | [P2] 插件崩溃或超时被隔离 | 首发延期；未来另授权独立扩展Task | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | DEFERRED：用户D6；目标保留，非PASS/N/A | NOT_RUN |
| AC-EXT-PLUGIN-003 | [P2] 缺少权限声明的插件拒绝加载 | 首发延期；未来另授权独立扩展Task | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | DEFERRED：用户D6；目标保留，非PASS/N/A | NOT_RUN |
| AC-EXT-FONT-001 | [P2] 获准上传字体可选并用于渲染 | 首发延期；未来另授权独立扩展Task | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | DEFERRED：用户D6；目标保留，非PASS/N/A | NOT_RUN |
| AC-EXT-FONT-002 | [P2] 损坏或超限字体拒绝且无半成品 | 首发延期；未来另授权独立扩展Task | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | DEFERRED：用户D6；目标保留，非PASS/N/A | NOT_RUN |
| AC-EXT-SAKURA-001 | [P2] Sakura 连接测试报告健康与就绪状态 | 首发延期；未来另授权独立扩展Task | 对应实现Owner按Task分配；DSH独立验证；Codex集成 | DEFERRED：用户D6；目标保留，非PASS/N/A | NOT_RUN |
| D08-AC-SMOKE | §53 发布包主流程：启动→建Book/Chapter→导入→工作台Pipeline→保存→阅读→导出→关闭/重启数据仍在 | P09建书契约/Core/Host；P12/P13/P14/P16/P17实际界面链 | P19 production E2E；P20 Windows clean smoke；DSH独立验证；Codex集成 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| D08-GATE-68 | §68 自动化测试最低覆盖 | P09/P13/P14/P15/P16（逐子任务实现测试） | P19汇总门槛；DSH独立验证 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| D08-GATE-69 | §69 UI自动化/ViewModel最低覆盖 | P12/P14/P15/P17的ZCode UI切片；Architecture Documentation Rebaseline Task先映射ViewModel至React/TypeScript目标等价测试 | P19对目标UI测试面验收；DSH独立Review；Codex集成 | INCLUDED：用户D5门槛不变；“ViewModel”旧技术术语不得直接套用，等价验收映射前NOT_RUN | NOT_RUN |
| D08-GATE-70 | §70 手工视觉验收：DPI/多屏/长文本/中日韩/状态 | P12/P14/P15/P17 | ZCode运行/提供截图，DSH非作者核验；不得只靠mock | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| D08-GATE-71 | §71 Benchmark Release Gate（Cold Start/切页/长图/内存等） | P12/P13/P14/P15/P17测量接线；优化缺口另立Task | P19报告、P20固定环境；DSH审数据 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| D08-GATE-72 | §72 数据安全Release Gate（源/人工/Revision/Stop/Crash/Migration/Secret） | P09/P10/P13/P14/P15/P16逐写路径保护 | P19故障注入且全部PASS；失败BLOCK RELEASE | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| D08-GATE-73 | §73 Final Release Checklist（P0/P1 100%、Backup/Restore、测试/包/更新说明） | P08用户确定基线；P09–P20按所选范围实现 | P20逐格提交证据；DSH独立Review；Codex做集成判定 | INCLUDED：用户D5门槛保持；§73要求全部达成，当前NOT_RUN | NOT_RUN |
| D08-GATE-74 | §74 验证证据目录结构（建议） | P19/P20可采用的verification归档建议 | 非独立验收；证据结构适用性由Codex整理 | ADVISORY ONLY：依doc/13口径，不是独立Gate或单独PASS | NOT_RUN |
| D08-GATE-75 | §75 verification-summary报告格式（建议） | P19/P20可采用的报告格式建议 | 非独立验收；报告格式适用性由DSH核验 | ADVISORY ONLY：依doc/13口径，不是独立Gate或单独PASS | NOT_RUN |
| D08-GATE-76 | §76 READY判定：P0/P1全过/数据安全/clean Windows | P09–P20实际实现，不以验收替代能力 | P20提交证据；DSH独立Review；Codex依据证据决策READY/NOT READY | INCLUDED：用户D5/D7；P0/P1门槛保持，当前未执行 | NOT_RUN |
| D08-GATE-77 | §77 D01–D08共同目标基线 | P08选定范围并记录合法增修版本 | Codex + DSH 文档一致性审查 | INCLUDED：用户D5/D7；维持D08现行要求 | NOT_RUN |
| D08-GATE-78 | §78扩展要求汇总 | P09/P12选入PDF/MOBI；Plugin/Hook、字体、Sakura监控首发延期 | DSH逐选定格式验收；Codex集成 | 用户D2/D6：选入/延期已确认；不豁免P0/P1 | NOT_RUN |
| D08-GATE-79 | §79 D08阶段结束建议与用户验收收口（建议） | P08范围裁决；P19结果；P20发布Gate | 建议性签收参考；不作为独立验收 | ADVISORY ONLY：无独立Gate或单独PASS | NOT_RUN |
