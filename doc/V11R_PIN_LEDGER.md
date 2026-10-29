# V11R 任务 Pin 账本（交付 HEAD / 合并点 / 证据 / 审查状态）

状态：`ACTIVE`（2026-10-30，DSH 维护；L3/L4 验收与最终报告以此为本）。
说明：`merge` 为合入 main 的合并提交（`git log --merges`）；`delivery` 为 Owner 交付/最终 pin；证据目录为仓库内路径。审查状态为独立审查（Codex 通道 / 独立 DSH Reviewer）。

| 任务 | delivery HEAD | merge 到 main | 证据 | 审查状态 |
|---|---|---|---|---|
| V11R-A-1 CreateChapter | `f4f176f66` | 早期 merge（A-1 单独） | `verification/V11R-A-1/` | 待 L3 批次 |
| V11R-A-2 IRunController | `9709029d4` | `672d72484`（A-2 merge） | `verification/V11R-A-2/` | 待 L3 批次 |
| V11R-A-3 66 命令契约 | `bfde74c8d` | `e793e0594` | `doc/contracts/V11R_COMMAND_CONTRACT_V1.md`、`verification/V11R-A-3/` | 待 L3 批次 |
| V11R-A-4 CI 可重建 | `fe7e4723c` | `555ace718` | `verification/V11R-A-4/`、`tools/ci/` | 待 L3 批次 |
| V11R-A-5 P0 写入策略 | `06914ec1f`（代码 `74d6f37e9`） | `f23f44da7` | `doc/plan/V11R_WRITE_POLICY.md`、`verification/V11R-A-5/` | 待 L3 批次（高风险，优先） |
| V11R-A-6 启动自检 | — | — | — | in_progress |
| V11R-A-7 export stale_policy | — | — | — | in_progress |
| V11R-D-1 Design System | `be76f1681` | `e070cc074` | `verification/V11R-D-1/`（含 contrast-matrix） | r1 FAIL（P1 已修）；**r2 审查进行中** |
| V11R-C-1 Theme Engine | `09cd62710`（代码 `daff73dba`） | `cc14a41d5`、`907339511`、`69ce04eef`、`0b44645ea` | `verification/V11R-C-1/`、`CONSUMER_GUIDE.md`、`INT_WIRING.md` | 待 L3 批次（203–229 测试） |
| V11R-C-3-READY 退役就绪 | `9acddc23f` | `5f4a0eee5` | `verification/V11R-C-3-READY/` | 待 L3 批次 |
| V11R-F0-1 Region 写面 | `1a457111c`（I2 最终） | **未合并（等复审）** | `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` v1.3、`verification/V11R-F0-1-I2/` | r1 FAIL、r2 FAIL；**r3 审查进行中** |
| V11R-F0-2 Region 文本投影 | `089cdb761`（修复 `1798d2e00`） | 随 F0-1 整支合并 | `verification/V11R-F0-2/` | 随 F0-1 复审 |
| V11R-B-1 外壳+Library | `09f8ad183` + `23217ac25`（证据） | `9a58f71ee`、`22b57ca91` | `verification/V11R-B-1/` | r1 PASS_WITH_ISSUES→I1 已修；**r3 审查进行中** |
| V11R-B-2 Console | `f3da3aaf3` | `9a58f71ee` | `verification/V11R-B-2/` | r2 PASS_WITH_ISSUES（P2 修复排期）；r3 审查中 |
| V11R-B-3 Studio Page | `19797be98`（I2c） | `3c543856a`、`5927c83a6`、`68dd925a6` | `verification/V11R-B-3/` | r1 FAIL→I1/I2c 已修；**r3 审查进行中** |
| V11R-B-4 Studio Batch | `19797be98`（I2c） | `3c543856a`、`3e14ead4f`、`c5037b65f`、`68dd925a6` | `verification/V11R-B-4/` | r2 FAIL（2×P1）→I2a/I2b 已修；r3 审查中 |
| V11R-B-5 导出/术语 | `455d2c432` | `1e6a3c4ee` | `verification/V11R-B-5/` | 待独立复核（拟并入下一轮） |
| V11R-C-2 Theme Studio | — | — | — | in_progress |
| V11R-INT-0 壳集成 | — | — | — | in_progress（ui-shell） |
| V11R-INT-1 默认入口切换 | — | — | — | pending（Lead） |
| V11R-C-3 旧主题退役 | — | — | `doc/plan/V11R_THEME_RETIREMENT_PLAN.md` | pending（R1–R6，前置 C-3-READY 已交付） |

## 已知缺口（须在 L4 前关闭）

| 缺口 | 来源 | 处置 |
|---|---|---|
| `IHostController.StartExportAsync` 未暴露 `stale_policy`（Core 支持 abort/continue_existing） | B-5 核实 | `V11R-A-7` 进行中 |
| 术语表/不译表无 Core 读写命令 | A-3 契约 GAP + B-5 核实 | UI 标 NOT_WIRED；能力缺口登记，不伪造 |
| 过期/待确认计数无投影口径 | B-4 核实 | 显示 `—`；需 Core 投影扩展（follow-up） |
| 页缩略图网格需 Host 缩略图命令 | B-1 核实 | follow-up（资源通道预取） |
| 并行测试临时 SQLite 争用 | 多次观测 | A-6 测试基础设施修复 |
| 状态色在 overlay/canvas 背景的部分对比度不足 | C-3-READY contrast matrix（14 对） | 组件约束（状态只落 panel/raised + statusMuted）或后续令牌修订；需 Lead 裁定 |
| Windows 实机 / DPI / IME / Trim / AOT / 屏幕阅读器 | 各任务 NOT_RUN | L4 实机验证 |
