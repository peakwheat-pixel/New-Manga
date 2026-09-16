# Task 索引

TASK-001～TASK-014、TASK-028 设计、TASK-029 统一 SQLite 持久化实现、TASK-030 入口装配与 TASK-031 生产 ImageDecoder/Managed Copy 适配器已完成并集成；TASK-013 生产 Pipeline seam 已以 `integration_commit=49c72fdf` 集成，R-1 已以 `integration_commit=734d5b3` 完成生产 Workbench 装配；TASK-016 已以 `integration_commit=9bf85f5` 完成集成；TASK-015 已按窗口条款收口 `done`（integration_commit=`fa72cee`，Review=`approved_subagent`）；TASK-024/017 由窗口授权解冻实施中，TASK-018～TASK-027 其余保持 `proposed`/冻结。**建议 Owner 不是实际派单。** 单个 Task 文件是状态真值，本表只提供标题和依赖导航。详细阶段与 Gate 见 [STATUS](../STATUS.md) 与 [Roadmap](../12_ROADMAP.md)。2026-09-16 23:30 ～ 09-17 08:30（Asia/Shanghai）为 ZCode 全权窗口：除已收口的 TASK-016 外，窗口目标 TASK-015、TASK-024、TASK-017 由 ZCode 全权执行并代行集成，条款见 [STATUS](../STATUS.md)「ZCode 全权窗口授权」。

| Task | 交付目标 | 建议 Owner | 硬依赖 |
|---|---|---|---|
| [TASK-001](TASK-001.md) | 修订目标文档引用与已确定的一致性问题 | Codex | 已释放；状态见 Task |
| [TASK-002](TASK-002.md) | 冻结最小数据与执行契约 | Codex | done；integration `7927169` |
| [TASK-003](TASK-003.md) | 补齐验收规格与测试素材规范，并关闭 F-08 | DeepSeek Harness | done；integration `db269e9` |
| [TASK-004](TASK-004.md) | 验证 Windows 运行环境与打包路线 | ZCode | done；integration `a501372` |
| [TASK-005](TASK-005.md) | 建立最小工程入口与架构守卫 | Codex | done；integration `6607f75` |
| [TASK-006](TASK-006.md) | 实现持久化与 Artifact 安全提交基础 | ZCode | done；integration `32a7314`；TASK-005 |
| [TASK-007](TASK-007.md) | 实现书架领域与本地图片导入 | ZCode | done；integration `2b64b0f`；TASK-006 |
| [TASK-008](TASK-008.md) | 实现 Region 编辑、Revision 与人工保护 | ZCode | done；integration `06ba2e7`；TASK-007 |
| [TASK-009](TASK-009.md) | 实现 Provider 配置、网络策略与凭据边界 | ZCode | done；integration `6c732be`；TASK-006 |
| [TASK-010](TASK-010.md) | 实现翻译约束、TM 与 Context | ZCode | done；integration `a225790`；TASK-008, TASK-009 |
| [TASK-011](TASK-011.md) | 实现命令计划、任务调度与可恢复进度 | Codex | done；integration `369e95f`；TASK-008, TASK-009, TASK-010 |
| [TASK-012](TASK-012.md) | 实现四页导航与书架 UI | ZCode | done；integration `78987c8`；TASK-005, TASK-007 |
| [TASK-013](TASK-013.md) | 实现工作台与任务进度交互 | ZCode | done；workbench integration `f0814a8`；生产 Pipeline seam integration `49c72fdf`；R-1 integration `734d5b3`；TASK-011, TASK-012, TASK-014 |
| [TASK-014](TASK-014.md) | 实现配色与文字排版渲染 | ZCode | done；integration `a943297`；TASK-008 |
| [TASK-015](TASK-015.md) | 实现阅读器与五种成果导出 | ZCode | done；base `1000ac8`；integration `fa72cee`；窗口同体 Review approved_subagent（期满补外部复审）；TASK-012, TASK-014 |
| [TASK-016](TASK-016.md) | OCR 与检测路线独立实验 | DeepSeek Harness | done；integration `9bf85f5`；Review `878ac16`；TASK-003, TASK-004 |
| [TASK-017](TASK-017.md) | Translation 与上下文输出协议实验 | DeepSeek Harness | TASK-003, TASK-004 |
| [TASK-018](TASK-018.md) | Mask / Inpainting 路线独立实验 | DeepSeek Harness | TASK-003, TASK-004 |
| [TASK-019](TASK-019.md) | 集成已验证的检测/OCR/翻译/修复 Provider | ZCode | TASK-011, TASK-014, TASK-016, TASK-017, TASK-018, TASK-024 |
| [TASK-020](TASK-020.md) | 实现 Webtoon 分块处理与阅读 | ZCode | TASK-013, TASK-015, TASK-019 |
| [TASK-021](TASK-021.md) | 完善备份恢复、回收站、清理与诊断 | Codex | TASK-006, TASK-011, TASK-015 |
| [TASK-022](TASK-022.md) | 补齐工具窗口、设置与视觉交互验收 | ZCode | TASK-009, TASK-010, TASK-013, TASK-015, TASK-021, TASK-024 |
| [TASK-023](TASK-023.md) | 实现 PDF/MOBI 与网页导入路线 | ZCode | TASK-007, TASK-009, TASK-012, TASK-024 |
| [TASK-024](TASK-024.md) | 明确扩展能力及验收覆盖边界（仅设计） | Codex | TASK-001, TASK-003 |
| [TASK-025](TASK-025.md) | 按批准契约实现 Plugin/Hooks 与可选扩展 | ZCode | TASK-019, TASK-022, TASK-024 |
| [TASK-026](TASK-026.md) | 独立集成审查与质量/性能验收 | DeepSeek Harness | TASK-020, TASK-021, TASK-022, TASK-023, TASK-025 |
| [TASK-027](TASK-027.md) | 发布候选集成、打包与最终验收 | Codex | TASK-026 |
| [TASK-028](TASK-028.md) | 冻结统一 SQLite 持久化设计（实现由 TASK-029 承接） | Codex | TASK-002, TASK-006, TASK-007, TASK-008 |
| [TASK-029](TASK-029.md) | 实现统一 SQLite 持久化 | ZCode | done；integration `0b0b855`；TASK-028 |
| [TASK-030](TASK-030.md) | Main.qml/bootstrap 最小生产装配 | ZCode | done；integration `fef9dd3`；TASK-005, TASK-007, TASK-012, TASK-029, TASK-031 |
| [TASK-031](TASK-031.md) | 生产 ImageDecoder 与 Managed Copy 适配器 | Codex | done；integration `e9d5185`；TASK-006, TASK-007, TASK-029 |

每个任务含具体 Acceptance Criteria、允许修改路径与测试要求。TASK-005 已建立最小 `src/bootstrap`、`src/domain`、`src/ui` 与 `tests/core`；其余路径仍是拟议所有权边界，ready 前由 Codex 对照实际结构确认。Task 不能越过依赖、冻结状态或扩大允许范围。
