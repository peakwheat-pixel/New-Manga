# 需求与验收追踪（接管基线）

来源：[D08 验收标准](08_ACCEPTANCE_CRITERIA.md)。2026-09-13 从二级标题读取185个带编号条目：104个P0、81个P1、0个P2。主责任 Task 用于安排最终行为交付；设计、底层存储及 UI 等依赖仍须共同验证。任务完成不自动将AC改成PASS。

此表是派生的覆盖路由，不重新定义验收预期。TASK-008 切片相关条目已绑定固定 reviewed_head、Review 与主线集成验证；其余产品级验收结果仍为 NOT_RUN。后续每项证据必须绑定测试commit/环境/命令/产物，不能用文档证据替代未执行的产品行为验证。

验收方法、环境档位、证据口径、性能测量协议、模型阈值状态与组级执行方式由 [TASK-003 验收方法与素材规范](verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md) 定义；本文件只维护追踪路由与当前结果，不复制这些方法或产品定义。素材与许可见 [Fixture Manifest](fixtures/MANIFEST.md)。

**结果真值规则**：AC / ACG 的"当前结果"只在本文件或绑定固定 commit 的 Handoff / Review 报告中维护；结果只能取 `PASS / FAIL / BLOCKED / NOT_RUN / N/A` 之一，不写复合状态。方法规范与 Fixture 清单都不得出现结果副本或结果摘要。

## 编号条目

| AC ID | 级别 | 原始标题 | 主责任 Task | 当前结果 | 当前证据 |
|---|---|---|---|---|---|
| AC-NAV-001 | P0 | 默认进入书架 | [TASK-012](tasks/TASK-012.md) | NOT_RUN | 无应用/测试 |
| AC-NAV-002 | P0 | 一级页面只有四个 | [TASK-012](tasks/TASK-012.md) | NOT_RUN | 无应用/测试 |
| AC-NAV-003 | P1 | 一级页面切换保持上下文 | [TASK-012](tasks/TASK-012.md) | NOT_RUN | 无应用/测试 |
| AC-WIN-001 | P1 | 固定位置优先 | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-WIN-002 | P1 | 编辑窗 Dirty Close | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-WIN-003 | P1 | 查看类外部关闭 | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-WIN-004 | P1 | 悬浮窗内容不溢出 | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-WIN-005 | P1 | 双屏拖动 | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-WIN-006 | P1 | 第二屏消失恢复 | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-LIB-001 | P0 | 新建 Book | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-LIB-002 | P1 | 自定义标签 | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-LIB-003 | P1 | 收藏 / 归档与 Tag 分离 | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-LIB-004 | P1 | 最近打开与阅读摘要 | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-CH-001 | P0 | Book → Chapter → Page | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-CH-002 | P0 | Paged Chapter | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-CH-003 | P0 | Webtoon Chapter | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-CH-004 | P1 | 同一 Book 混合类型 | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-IMPORT-001 | P0 | Managed Copy | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-IMPORT-002 | P0 | 用户源文件不修改 | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-IMPORT-003 | P0 | Copy 中断不产生坏 Page | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-IMPORT-004 | P1 | Unicode 路径 | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-IMPORT-005 | P1 | 重复检测 | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-PAGE-001 | P0 | Page 顺序 | [TASK-007](tasks/TASK-007.md) | NOT_RUN | 无应用/测试 |
| AC-PAGE-002 | P1 | 多选范围 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PAGE-003 | P1 | Page 状态 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-WEBTOON-001 | P0 | 一张长图 = 一张 Page | [TASK-020](tasks/TASK-020.md) | NOT_RUN | 无应用/测试 |
| AC-WEBTOON-002 | P0 | Tile 不是 Page | [TASK-020](tasks/TASK-020.md) | NOT_RUN | 无应用/测试 |
| AC-WEBTOON-003 | P0 | 坐标回映 | [TASK-020](tasks/TASK-020.md) | NOT_RUN | 无应用/测试 |
| AC-WEBTOON-004 | P1 | 按宽缩放 | [TASK-020](tasks/TASK-020.md) | NOT_RUN | 无应用/测试 |
| AC-WEBTOON-005 | P1 | Scroll 恢复 | [TASK-020](tasks/TASK-020.md) | NOT_RUN | 无应用/测试 |
| AC-REGION-001 | P0 | Region 统一模型 | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-REGION-002 | P1 | 几何编辑 | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-REGION-003 | P1 | Reading Order | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-REGION-004 | P1 | Region Type | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-OCR-001 | P0 | 单 Region OCR | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-OCR-002 | P0 | Re-OCR 不覆盖人工译文 | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-OCR-003 | P1 | OCR Provider 优先级 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-OCR-004 | P1 | 韩漫 OCR | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-SFX-001 | P1 | 默认 Skip | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-SFX-002 | P1 | Translate | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-SFX-003 | P1 | Manual | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-CONSTRAINT-001 | P0 | 优先级 | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-CONSTRAINT-002 | P0 | 人工锁定优先 | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-CONSTRAINT-003 | P1 | Candidate Status | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-CONSTRAINT-004 | P1 | Rejected 不重复推荐 | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-TM-001 | P0 | 未确认机器译文不写 TM | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-TM-002 | P0 | 人工确认写 TM | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-TM-003 | P1 | 查询优先级 | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-TM-004 | P1 | TM 不覆盖人工译文 | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-TRANS-001 | P0 | 四级文本 | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-TRANS-002 | P0 | 人工编辑自动保护 | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-TRANS-003 | P0 | Context 与 Write Scope | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-TRANS-004 | P1 | 多页上下文排序 | [TASK-010](tasks/TASK-010.md) | NOT_RUN | 无应用/测试 |
| AC-LOCK-001 | P0 | Page Lock | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-LOCK-002 | P0 | Region Lock | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-LOCK-003 | P0 | Translation Lock | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-LOCK-004 | P0 | Inpaint Lock | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-LOCK-005 | P0 | 写入时再次检查 Lock | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-REV-001 | P0 | 成功重跑创建新 Revision | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-REV-002 | P0 | 失败不改变 current | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-REV-003 | P1 | Pin | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-REV-004 | P1 | 恢复 Revision | [TASK-008](tasks/TASK-008.md) | PASS | [TASK-008 集成验证](../verification/TASK-008/integration-06ba2e7.md)；Review `f9e5977` |
| AC-STYLE-001 | P0 | 自动字号 | [TASK-014](tasks/TASK-014.md) | NOT_RUN | 无应用/测试 |
| AC-STYLE-002 | P1 | Offset 范围 | [TASK-014](tasks/TASK-014.md) | NOT_RUN | 无应用/测试 |
| AC-STYLE-003 | P0 | Shrink-to-fit | [TASK-014](tasks/TASK-014.md) | NOT_RUN | 无应用/测试 |
| AC-STYLE-004 | P1 | 不自动放大 | [TASK-014](tasks/TASK-014.md) | NOT_RUN | 无应用/测试 |
| AC-STYLE-005 | P1 | Region 关闭自动字号 | [TASK-014](tasks/TASK-014.md) | NOT_RUN | 无应用/测试 |
| AC-INPAINT-001 | P0 | Mask 持久化 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-INPAINT-002 | P0 | 新 Clean 不覆盖旧版本 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-INPAINT-003 | P1 | Router provenance | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-INPAINT-004 | P1 | Webtoon Color Route | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-RENDER-001 | P0 | 重新渲染不触发 OCR | [TASK-014](tasks/TASK-014.md) | NOT_RUN | 无应用/测试 |
| AC-RENDER-002 | P0 | 缺 Clean 时阻止 | [TASK-014](tasks/TASK-014.md) | NOT_RUN | 无应用/测试 |
| AC-RFULL-001 | P0 | 完整链 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-RFULL-002 | P0 | 只写目标 Region | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-RFULL-003 | P0 | Page / Region Lock 阻止 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-RFULL-004 | P0 | 专项 Lock 临时覆盖 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-RFULL-005 | P0 | 人工结果保护点 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-CMD-001 | P0 | 全部翻译复用 OCR | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CMD-002 | P0 | 跳过已翻译 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CMD-003 | P1 | 选择页目标冻结 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CMD-004 | P1 | 单页命令 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PIPE-001 | P0 | StepRun 可追踪 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PIPE-002 | P0 | 有效 Step 可 Skip | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PIPE-003 | P0 | Stale 不当作 Valid | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PIPE-004 | P0 | Missing prerequisite | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PAUSE-001 | P0 | 暂停请求 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PAUSE-002 | P0 | 安全边界 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PAUSE-003 | P0 | 继续 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-STOP-001 | P0 | 停止不回滚 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-STOP-002 | P0 | Pending Cancel | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-STOP-003 | P0 | Stop 不是 Delete | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CRASH-001 | P0 | Running → Interrupted | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CRASH-002 | P0 | Resume | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CRASH-003 | P0 | Temp Artifact | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-RETRY-001 | P0 | 失败保留上游结果 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-RETRY-002 | P1 | 失败页重试 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-PROGRESS-001 | P0 | 固定底部 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PROGRESS-002 | P0 | 显示内容 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PROGRESS-003 | P0 | 当前 Page 定位 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PROGRESS-004 | P1 | 失败统计联动 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PROGRESS-005 | P1 | 完成统计联动 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PROGRESS-006 | P0 | CompletedWithFailures | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PROGRESS-007 | P0 | PageList 同源 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PROVIDER-001 | P1 | 同 Provider 多 Profile | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-PROVIDER-002 | P0 | Capability 默认绑定 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-PROVIDER-003 | P0 | Run Snapshot | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-PROVIDER-004 | P0 | Provider 消失后的恢复 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-FALLBACK-001 | P0 | 无配置不跨 Provider | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-FALLBACK-002 | P1 | 显式 fallback | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-NET-001 | P0 | 多 Network Profile | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-NET-002 | P0 | Proxy Failure 不静默 Direct | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-NET-003 | P0 | 显式 Direct Fallback | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-NET-004 | P1 | Connection Test 分阶段 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-SEC-001 | P0 | SQLite 无 Secret 明文 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-SEC-002 | P0 | 日志无 Secret 明文 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-SEC-003 | P0 | Credential Manager | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-SEC-004 | P0 | TLS 默认开启 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-SEC-005 | P1 | 关闭 TLS 必须确认 | [TASK-009](tasks/TASK-009.md) | NOT_RUN | 无应用/测试 |
| AC-ART-001 | P0 | 成功 Commit | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-ART-002 | P0 | Commit 中断 | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-ART-003 | P0 | Hash | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-DB-001 | P0 | Foreign Key | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-DB-002 | P1 | WAL | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-DB-003 | P0 | Migration 前备份 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-DB-004 | P0 | Migration 失败 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-DB-005 | P0 | 新 Schema 被旧 App 打开 | [TASK-006](tasks/TASK-006.md) | NOT_RUN | 无应用/测试 |
| AC-BACKUP-001 | P0 | 手动备份 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-BACKUP-002 | P1 | 自动备份 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-BACKUP-003 | P0 | Restore 前再次备份 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-BACKUP-004 | P0 | Restore 不改源文件 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-TRASH-001 | P0 | 软删除 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-TRASH-002 | P1 | Batch Restore | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-TRASH-003 | P0 | 永久删除确认 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-TRASH-004 | P0 | 源文件安全 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-EXPORT-001 | P0 | 格式 | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-EXPORT-002 | P1 | ExportHistory | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-EXPORT-003 | P1 | Stale 提示 | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-READ-001 | P0 | Original / Translated | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-READ-002 | P1 | 独立阅读进度 | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-READ-003 | P1 | RTL | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-READ-004 | P1 | LTR | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-READ-005 | P1 | Webtoon Vertical | [TASK-015](tasks/TASK-015.md) | NOT_RUN | 无应用/测试 |
| AC-PERF-001 | P1 | 冷启动 | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-PERF-002 | P1 | 一级页面切换 | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-PERF-003 | P1 | 固定面板响应 | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-PERF-004 | P1 | Book 搜索 | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-PERF-005 | P1 | Translation Memory Exact | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-PERF-006 | P1 | Translation Memory Fuzzy | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-CAP-001 | P1 | Library | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-CAP-002 | P1 | Chapter 1000 Page | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-CAP-003 | P1 | 200 Region | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-CAP-004 | P1 | 200k Webtoon | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-MEM-001 | P1 | Core Idle | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-MEM-002 | P1 | 连续切页 | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-MEM-003 | P1 | Floating Window | [TASK-026](tasks/TASK-026.md) | NOT_RUN | 无应用/测试 |
| AC-GPU-001 | P0 | GPU OOM 不崩主程序 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-GPU-002 | P1 | GPU Heavy 默认单并发 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-GPU-003 | P1 | CPU Fallback 可追踪 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-CACHE-001 | P0 | 清 Cache 不删业务真值 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-CACHE-002 | P0 | Pinned 不清理 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-CACHE-003 | P0 | Active Pipeline 输入保护 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-DISK-001 | P1 | 低磁盘 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-LOG-001 | P1 | Log Rotation | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-LOG-002 | P1 | Step 错误信息完整 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-LOG-003 | P1 | Diagnostic Bundle | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-NFR-UI-001 | P0 | AI 不阻塞 UI | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-NFR-UI-002 | P1 | Progress 节流 | [TASK-013](tasks/TASK-013.md) | NOT_RUN | 无应用/测试 |
| AC-PKG-001 | P0 | PyInstaller onedir | [TASK-027](tasks/TASK-027.md) | NOT_RUN | 无应用/测试 |
| AC-PKG-002 | P0 | 干净 Windows 启动 | [TASK-027](tasks/TASK-027.md) | NOT_RUN | 无应用/测试 |
| AC-PKG-003 | P0 | Qt DLL | [TASK-027](tasks/TASK-027.md) | NOT_RUN | 无应用/测试 |
| AC-OPTIONAL-001 | P0 | 缺重型模型仍可启动 | [TASK-005](tasks/TASK-005.md) | NOT_RUN | 无应用/测试 |
| AC-OPTIONAL-002 | P1 | Provider 状态 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-MODEL-001 | P1 | 下载进度 | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-MODEL-002 | P0 | 不完整模型不 Ready | [TASK-019](tasks/TASK-019.md) | NOT_RUN | 无应用/测试 |
| AC-CONFLICT-001 | P0 | Optimistic Write Guard | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CONFLICT-002 | P0 | 同能力写冲突 | [TASK-011](tasks/TASK-011.md) | NOT_RUN | 无应用/测试 |
| AC-CLEAN-001 | P0 | Current 不清理 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-CLEAN-002 | P0 | 用户源文件不清理 | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-CLEAN-003 | P1 | Debug Artifact | [TASK-021](tasks/TASK-021.md) | NOT_RUN | 无应用/测试 |
| AC-CLOSE-001 | P0 | 运行任务关闭 | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-CLOSE-002 | P0 | Dirty + Running 分离 | [TASK-022](tasks/TASK-022.md) | NOT_RUN | 无应用/测试 |
| AC-DOC-001 | P1 | 01~08 文件齐全 | [TASK-001](tasks/TASK-001.md) | PASS | 8份文件存在；审计§2 |
| AC-DOC-002 | P1 | 核心术语统一 | [TASK-002](tasks/TASK-002.md) | PASS | DeepSeek approved `b1b3f5d..885c9a9`；由 `7927169` 集成，契约 §1/5/6 统一术语 |
| AC-DOC-003 | P1 | 四个一级页面统一 | [TASK-001](tasks/TASK-001.md) | PASS | 全文核对四个入口与默认书架；审计§7 |

## 无独立编号的 AC 主题要求

D08有61个AC主题标题，其中 10 个主题没有独立编号子项；不得因上表只提取编号而遗漏。TASK-003 已为全部未编号要求分配稳定组标识（不发明新的产品 ID 或优先级）：10 个零编号主题、7 个 D08 §68～§73/§76 全局规范、7 个扩展项，共 24 个。执行方式、环境与证据口径见[验收方法与素材规范 §8](verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md)，本表只保留追踪回链与结果。

### 零编号 AC 主题（10）

| 组标识 | 原主题 | D08章节 | 主责任Task | 要求 | 当前结果 |
|---|---|---|---|---|---|
| `ACG-DPI` | AC-DPI | §51 | [TASK-022](tasks/TASK-022.md) | 100～200%显示缩放与多屏可达性 | NOT_RUN |
| `ACG-SMOKE` | AC-SMOKE | §53 | [TASK-027](tasks/TASK-027.md) | 干净Windows发布包完整主流程 | NOT_RUN |
| `ACG-OFFLINE` | AC-OFFLINE | §56 | [TASK-026](tasks/TASK-026.md) | 离线本地能力可用、远程不可用状态 | NOT_RUN |
| `ACG-PRIVACY` | AC-PRIVACY | §57 | [TASK-009](tasks/TASK-009.md) | Provider 设置页说明上传给远程 Provider 的数据类型 | NOT_RUN |
| `ACG-SET` | AC-SET | §59 | [TASK-009](tasks/TASK-009.md) | 设置继承和值来源 | NOT_RUN |
| `ACG-PROV` | AC-PROV | §60 | [TASK-011](tasks/TASK-011.md) | OCR/Translation/Inpaint/Render来源链 | NOT_RUN |
| `ACG-ERROR` | AC-ERROR | §62 | [TASK-011](tasks/TASK-011.md) | 错误分类 | NOT_RUN |
| `ACG-ERRUI` | AC-ERRUI | §63 | [TASK-013](tasks/TASK-013.md) | 错误在页面/进度/详情可定位 | NOT_RUN |
| `ACG-AUTO` | AC-AUTO | §64 | [TASK-008](tasks/TASK-008.md) | Autosave条件性要求或明确保存 | NOT_RUN |
| `ACG-SYNC` | AC-SYNC | §67 | [TASK-002](tasks/TASK-002.md) | 06/07增量同步与冻结Gate | NOT_RUN |

`ACG-SYNC` 证据：TASK-002 最小契约已独立批准（`b1b3f5d..885c9a9`）并由 `7927169` 集成。契约获批**只是证据**，不等于 Gate 通过——D08 §67 要求正式实现满足契约 §2～§10 并通过 §11 验证向量后才可通过该 Gate；当前无 Schema 与产品实现，因此结果为 `NOT_RUN`。

### D08 未编号全局规范（§68～§73、§76）

| 组标识 | D08章节 | 主责任Task | 要求 | 当前结果 |
|---|---|---|---|---|
| `ACG-AUTOTEST` | §68 | [TASK-026](tasks/TASK-026.md) | 按 D08 §68 自动化测试最低覆盖清单 | NOT_RUN |
| `ACG-UITEST` | §69 | [TASK-026](tasks/TASK-026.md) | 按 D08 §69 UI/ViewModel 最低覆盖清单 | NOT_RUN |
| `ACG-VISUAL` | §70 | [TASK-022](tasks/TASK-022.md) | 手工视觉验收（DPI/双屏/长文本/多语言/状态） | NOT_RUN |
| `ACG-BENCH` | §71 | [TASK-026](tasks/TASK-026.md) | 每个 Release Candidate 生成 benchmark-report.md | NOT_RUN |
| `ACG-DATASAFE` | §72 | [TASK-026](tasks/TASK-026.md) | 按 D08 §72 数据安全 Gate 逐项核对，任一 FAIL 阻塞发布 | NOT_RUN |
| `ACG-RELEASECHECK` | §73 | [TASK-027](tasks/TASK-027.md) | 按 D08 §73 最终 Release Checklist | NOT_RUN |
| `ACG-READY` | §76 | [TASK-027](tasks/TASK-027.md) | READY 判定条件 | NOT_RUN |

D08 §74（建议验收结果目录）与 §75（verification-summary.md 推荐格式）为建议性章节，**不作为独立验收项**，理由见规范 §8.2；其内容要求已由 `ACG-RELEASECHECK` 与 `ACG-READY` 覆盖。

标识合计 24 个（10 + 7 + 7）；TASK-026 验证，TASK-027 执行最终发布 Gate。

## 01～07 中需补充验收的内容

以下条目尚未成为编号 AC，已分配稳定扩展标识；执行方式见[验收方法与素材规范 §8.4](verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md)。

| 组标识 | 已有来源 | 内容 | 后续处理 | 当前结果 |
|---|---|---|---|---|
| `ACG-EXT-IMPORT` | D01 §2；D04 §8；D05 §52 | 图片/文件夹以外的 PDF、MOBI、网页导入 | TASK-024已定义边界（[contracts/extensions.md §1.1/1.2](contracts/extensions.md)），AC 草案与释放条件待用户批准（U-1/U-2）后转编号 AC，TASK-023实现 | NOT_RUN |
| `ACG-EXT-PLUGIN` | D01 §2；D02 §12；D07 §72 | Plugin/Hooks、AI生成插件Agent | TASK-024已定义边界与 Plugin Agent 保留条件（[contracts/extensions.md §1.3/1.4](contracts/extensions.md)），待用户批准（U-3/U-4）后转编号 AC，TASK-025按获批范围实现 | NOT_RUN |
| `ACG-EXT-FONT` | D01 §2；D05 §48 | 字体上传和资源处理 | TASK-024已定义边界（[contracts/extensions.md §1.5](contracts/extensions.md)），待用户批准（U-5）后转编号 AC，TASK-022实现 | NOT_RUN |
| `ACG-EXT-SAKURA` | D01 §2；D02 §11 | Sakura服务监控、模型/设备就绪状态 | TASK-024已定义草案边界（健康探测级）（[contracts/extensions.md §1.6](contracts/extensions.md)），待用户批准（U-6）后转编号 AC，TASK-019落实批准部分 | NOT_RUN |
| `ACG-EXT-DETECT` | D06 §6/8 | 检测、配色和SourceStyle本身的正确性 | 质量方法见规范 §7；TASK-016/019与TASK-014验证 | NOT_RUN |
| `ACG-EXT-CONTRACT` | D03/D06，G06～G13 | 状态、复合写回、Pin/TM/Review、SFX等未闭合契约 | TASK-002已冻结契约；精确AC待TASK-003/024补齐 | NOT_RUN |
| `ACG-EXT-NFR` | D07目标数值与D08发布要求 | SHOULD/P1/豁免的口径及基准环境 | TASK-001/003核对并形成用户可审核规则，TASK-026实测 | NOT_RUN |

没有明确验收不等于没有需求。新增/延期/豁免必须回写权威文档并保留用户决定，不能静默标N/A。算法实验通过也不替代真实产品端到端验收。
