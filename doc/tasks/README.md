# Task 索引

TASK-001～TASK-008 已完成并集成；TASK-028 的统一 SQLite 持久化设计已冻结但实现未释放；TASK-009～TASK-027 保持 `proposed`，尚未释放。**建议 Owner 不是实际派单。** 单个 Task 文件是状态真值，本表只提供标题和依赖导航。详细阶段与 Gate 见 [STATUS](../STATUS.md) 与 [Roadmap](../12_ROADMAP.md)。

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
| [TASK-009](TASK-009.md) | 实现 Provider 配置、网络策略与凭据边界 | ZCode | TASK-006 |
| [TASK-010](TASK-010.md) | 实现翻译约束、TM 与 Context | ZCode | TASK-008, TASK-009 |
| [TASK-011](TASK-011.md) | 实现命令计划、任务调度与可恢复进度 | Codex | TASK-008, TASK-009, TASK-010 |
| [TASK-012](TASK-012.md) | 实现四页导航与书架 UI | ZCode | TASK-005, TASK-007 |
| [TASK-013](TASK-013.md) | 实现工作台与任务进度交互 | ZCode | TASK-011, TASK-012, TASK-014 |
| [TASK-014](TASK-014.md) | 实现配色与文字排版渲染 | ZCode | TASK-008 |
| [TASK-015](TASK-015.md) | 实现阅读器与五种成果导出 | ZCode | TASK-012, TASK-014 |
| [TASK-016](TASK-016.md) | OCR 与检测路线独立实验 | DeepSeek Harness | TASK-003, TASK-004 |
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
| [TASK-028](TASK-028.md) | 冻结统一 SQLite 持久化设计（实现未释放） | Codex | TASK-006, TASK-007, TASK-008 |

每个任务含具体 Acceptance Criteria、允许修改路径与测试要求。TASK-005 已建立最小 `src/bootstrap`、`src/domain`、`src/ui` 与 `tests/core`；其余路径仍是拟议所有权边界，ready 前由 Codex 对照实际结构确认。Task 不能越过依赖、冻结状态或扩大允许范围。
