# New Manga 一眼路线图（2026-10-08）

人员更新：用户已移除Qoder，图中未来UI/UX责任由ZCode承担；非作者Review与正式Task释放Gate保持。

派生视图；排期事实以 [REBASELINE_PLAN](../../doc/REBASELINE_PLAN.md) 当前覆盖层为准。基线：`main@e4242ecd`。箭头表示启动依赖，不是工期；没有可靠估算，不编造百分比或日期。`M2-xxx` 是规划节点，全部未释放，尚未创建正式 Task 文件。

## 已做到哪里

```mermaid
flowchart TB
  A["已完成：基础架构<br/>Python Core · SQLite · Managed Copy"] --> B["已完成：安全桥接<br/>Tauri IPC · 大图资源通道 · Windows打包"]
  B --> C["已完成：业务竖切<br/>书目/页导航 · 区域改标 · 撤销 · 重渲染"]
  A --> D["已完成：AI生产与实验链<br/>manga检测 · SFX · OCR适配 · JA/KO素材"]
  C --> E["当前产品：部分可操作<br/>Console＋Workbench；任务进度仍占位"]
  D --> E
  E --> F["未完成：完整用户闭环<br/>导入 → 翻译运行/恢复 → 阅读/导出"]
  E --> G["未完成：完整四页界面<br/>书架 / 工作台 / 阅读器 / 设置"]
  F --> H["未完成：整体产品验收<br/>真实质量＋四页行为＋声明的Windows矩阵"]
  G --> H
```

“已完成”仅针对各 Task 冻结范围。AI实验有如实 FAIL 的结论；后端 API 可用、测试模式端到端成功，均不能代替正式界面链路。

## 当前范围内：先收口，再进入整产品主链

```mermaid
flowchart TB
  BASE["当前基线：无 Active / released"] --> M2-TASK-EVIDENCE-RECONCILIATION["M2-TASK-EVIDENCE-RECONCILIATION<br/>proposed / 未释放<br/>台账取证<br/>修正陈旧metadata；追溯两份Review"]
  BASE --> M2-WORKBENCH-REAL-UI-VERIFICATION["M2-WORKBENCH-REAL-UI-VERIFICATION<br/>proposed / 未释放<br/>真UI验证<br/>点击/300ms刷新/对比度/失效窗口"]
  BASE --> M2-PACKAGED-SFX-ENTRY-GATE["M2-PACKAGED-SFX-ENTRY-GATE<br/>proposed / 未释放<br/>第五入口Gate<br/>验证SFX frozen入口；不只确认文件存在"]
  BASE --> M2-PRODUCTION-BRIDGE-VERIFICATION["M2-PRODUCTION-BRIDGE-VERIFICATION<br/>proposed / 未释放<br/>生产命令面验证<br/>常量成员与并发响应；先复现再决定修复"]
  BASE --> M2-ERROR-CONTRACT-NOTES["M2-ERROR-CONTRACT-NOTES<br/>proposed / 未释放<br/>错误语义澄清<br/>category与retryable注记一致"]
  BASE --> M2-GC-DISTRIBUTION-MIGRATION-GATE["M2-GC-DISTRIBUTION-MIGRATION-GATE<br/>proposed / 未释放<br/>GC迁移补证<br/>旧版本退出/命名空间保护；未知保留"]
  M2-WORKBENCH-REAL-UI-VERIFICATION -. "确认实际缺口后" .-> M2-WORKBENCH-INPUT-INTERACTION-FIX["M2-WORKBENCH-INPUT-INTERACTION-FIX<br/>proposed / 未释放<br/>小交互修补<br/>手输image读取/quiet-window busy"]
  M2-TASK-EVIDENCE-RECONCILIATION --> S["M2-PRODUCT-COMPLETION-SCOPE<br/>proposed / 未释放<br/>完整产品范围与验收冻结<br/>Codex汇总；用户裁决；ZCode设计"]
```

取证与验证候选任务 不存在必须全部串行的技术依赖。M2-TASK-EVIDENCE-RECONCILIATION已由本轮提供取证结论；推荐先准备M2-PRODUCT-COMPLETION-SCOPE完整产品范围，范围裁决前可做M2-WORKBENCH-REAL-UI-VERIFICATION/M2-PACKAGED-SFX-ENTRY-GATE，余项按风险插入。启动每个实现前仍须正式 Task、独立 Reviewer 和 allowed_paths。共享主线/契约/启动文件串行集成。M2-GC-DISTRIBUTION-MIGRATION-GATE 是已完成 GC-2 的分发补证，不重新实现 GC-2，也不声称长会话磁盘有界。

## 完整产品：现在就看清后续，而不是每次临时猜下一件

```mermaid
flowchart TB
  M2-PRODUCT-COMPLETION-SCOPE["M2-PRODUCT-COMPLETION-SCOPE<br/>proposed / 未释放<br/>范围＋四页设计冻结<br/>保留四页；Reader解冻须用户裁决"] --> M2-REAL-IMPORT-ADAPTERS["M2-REAL-IMPORT-ADAPTERS<br/>proposed / 未释放<br/>真实导入契约与Core适配<br/>受限来源引用；真实尺寸；Managed Copy"]
  M2-PRODUCT-COMPLETION-SCOPE --> M2-PROVIDER-CREDENTIALS["M2-PROVIDER-CREDENTIALS<br/>proposed / 未释放<br/>设置与凭据安全通道<br/>Provider配置可验证；secret不进普通DTO"]
  M2-PRODUCT-COMPLETION-SCOPE --> M2-LONG-RUN-IPC-CONTRACT["M2-LONG-RUN-IPC-CONTRACT<br/>proposed / 未释放<br/>长任务契约冻结<br/>启动/快照/暂停取消重试/恢复语义"]
  M2-REAL-IMPORT-ADAPTERS --> M2-LIBRARY-IMPORT-UI["M2-LIBRARY-IMPORT-UI<br/>proposed / 未释放<br/>书架与导入产品链<br/>建书/章节/选文件/结果；ZCode接UI"]
  M2-REAL-IMPORT-ADAPTERS --> M2-PIPELINE-RUNTIME-RECOVERY["M2-PIPELINE-RUNTIME-RECOVERY<br/>proposed / 未释放<br/>Pipeline后台运行与恢复<br/>复用现有调度；持久状态；ZCode实现"]
  M2-LONG-RUN-IPC-CONTRACT --> M2-PIPELINE-RUNTIME-RECOVERY
  M2-PIPELINE-RUNTIME-RECOVERY --> M2-WORKBENCH-FULL-OPERATIONS["M2-WORKBENCH-FULL-OPERATIONS<br/>proposed / 未释放<br/>工作台完整操作链<br/>运行/进度/人工译文/Lock/Pin/区域编辑"]
  M2-PROVIDER-CREDENTIALS --> M2-SETTINGS-MAINTENANCE["M2-SETTINGS-MAINTENANCE<br/>proposed / 未释放<br/>完整设置页<br/>配置/凭据/诊断；ZCode实现"]
  M2-PIPELINE-RUNTIME-RECOVERY --> M2-READER-EXPORT-CORE["M2-READER-EXPORT-CORE<br/>proposed / 未释放<br/>阅读与导出契约＋Core<br/>进度/lineage/受控输出；待范围解冻"]
  M2-PRODUCT-COMPLETION-SCOPE -. "Reader解冻裁决" .-> M2-READER-EXPORT-CORE
  M2-READER-EXPORT-CORE --> M2-READER-EXPORT-UI["M2-READER-EXPORT-UI<br/>proposed / 未释放<br/>阅读器与导出UI<br/>读取真实结果/保存进度/安全导出"]
  M2-PROVIDER-CREDENTIALS --> M2-JA-KO-QUALITY-QUALIFICATION["M2-JA-KO-QUALITY-QUALIFICATION<br/>proposed / 未释放<br/>真JA/KO质量资格<br/>检测/OCR/翻译/修复/无字页；DSH验收"]
  M2-PIPELINE-RUNTIME-RECOVERY --> M2-JA-KO-QUALITY-QUALIFICATION
  M2-LIBRARY-IMPORT-UI --> M2-PRODUCT-E2E-ACCEPTANCE["M2-PRODUCT-E2E-ACCEPTANCE<br/>proposed / 未释放<br/>四页完整E2E与数据安全<br/>正常/失败/人工修改/Lock/重启；非作者验收"]
  M2-WORKBENCH-FULL-OPERATIONS --> M2-PRODUCT-E2E-ACCEPTANCE
  M2-SETTINGS-MAINTENANCE --> M2-PRODUCT-E2E-ACCEPTANCE
  M2-READER-EXPORT-UI --> M2-PRODUCT-E2E-ACCEPTANCE
  M2-JA-KO-QUALITY-QUALIFICATION --> M2-PRODUCT-E2E-ACCEPTANCE
  M2-PRODUCT-E2E-ACCEPTANCE --> M2-WINDOWS-RELEASE-GATE["M2-WINDOWS-RELEASE-GATE<br/>proposed / 未释放<br/>最终Windows发布Gate<br/>新fixed-head安装包；声明矩阵；独立审查"]
  M2-PACKAGED-SFX-ENTRY-GATE["M2-PACKAGED-SFX-ENTRY-GATE<br/>proposed / 未释放<br/>第五入口补证"] --> M2-WINDOWS-RELEASE-GATE
  M2-GC-DISTRIBUTION-MIGRATION-GATE["M2-GC-DISTRIBUTION-MIGRATION-GATE<br/>proposed / 未释放<br/>GC分发补证"] --> M2-WINDOWS-RELEASE-GATE
  M2-WINDOWS-RELEASE-GATE -. "另行授权，可选" .-> M2-LEGACY-RETIREMENT["M2-LEGACY-RETIREMENT<br/>proposed / 未释放<br/>Legacy归档/移除<br/>新架构parity通过后；不修旧架构"]
```

完整产品候选任务 是完整目标的条件规划，不解除当前 Reader/跨页联动/页缩略图“明确不做”的冻结。缩略图、跨页联动不作为默认任务。M2-REAL-IMPORT-ADAPTERS/M2-PROVIDER-CREDENTIALS/M2-LONG-RUN-IPC-CONTRACT 内部先契约后实现，正式释放时拆为独立 Task；M2-WORKBENCH-FULL-OPERATIONS新增编辑能力同样先Codex冻结命令、ZCode/Antigravity实现Core、再ZCode接UI；M2-READER-EXPORT-CORE先Core/IPC后M2-READER-EXPORT-UI UI。Pipeline 最小成功链可先用 deterministic provider，真实质量 Gate 依赖 M2-PROVIDER-CREDENTIALS 和可用受控模型/endpoint，不能将 mock PASS 当真质量 PASS。

长会话/磁盘总量、模型扩展与训练不是默认关键路径。BJ13 维持 0.90、手工改标＋skip；Manga109 永久取消。不重新打开已完成 TA3-B2/B3、GC-2、ICU 或 Runner Guard。

## 每一步怎么算完成

```mermaid
flowchart LR
  A["冻结Task<br/>依赖/范围/Owner/基线"] --> B["实现交付<br/>代码＋可复现测试＋Handoff"]
  B --> C["非作者Review<br/>固定提交；条件闭合"]
  C --> D["Codex集成验证<br/>核路径/数据安全/受影响回归"]
  D --> E["done＋更新台账<br/>提前解锁下一规划节点"]
```

额度中断时：读 [RESUME](RESUME.md) → 核 Git/当前 STATUS → 复用报告 → 只重算变化的依赖子图。等待额度恢复无需重做全仓审计；外部 Agent 接管须按协作协议分配，Owner 不得审自己。
