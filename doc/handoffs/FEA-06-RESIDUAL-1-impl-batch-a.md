# FEA-06-RESIDUAL-1 Handoff（Batch A 交付 → Batch B 待派，2026-11-02）

> 事实以 Git 与仓库文件为准。本 handoff 由 DSH 在 ZCode 实现会话崩溃后收尾时撰写。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-RESIDUAL-1.md` — 范围 v3 已冻结（scope-r3 approved，ZCode；P0=0/P1=0/P2=4 实施期处置） |
| base_commit | `82529a3d5864a39f362e414b67bca774d743f862` |
| 实现执行 | **ZCode CLI**（Codex 额度故障转移；`--mode yolo`；会话 `impl-batch-a-zcode-raw.log` 记录崩溃 exit -1073740791） |
| I-6 commit | `83fa1b186` — 四 Fluent VM 等价拆分（1408 行→四文件+共享基类） |
| Batch A commit | 本批功能与证据 commit（见 `git log`；I-1/I-2/I-3/I-9/I-10/I-12/I-13/I-14） |
| 证据 | `verification/FEA-06-RESIDUAL-1/batch-a-verification.log` |
| 安全回归 | **1170 passed / 0 failed / 57 skipped**（= 基线 1137 + 33 新测试；PNG 用例排除，旧证据未覆盖） |
| 治理 | build 0/0；TokenGen 292 rows / ThemeGen `--check` up-to-date；check.ps1 PASS(3)；verify_pins 15/15 |

## 2. Batch A 结果

- **I-6**：完成（`83fa1b186`；`FluentPageViewModels.cs` 1408 行拆为 Shelf/Workbench/Reader/Settings + 共享基类；既有测试不改弱）。
- **I-1/I-2/I-3/I-9/I-10/I-12/I-13/I-14**：完成，测试覆盖于 `FluentResidualBatchATests` 与 `FluentResidualSettingsLeaveTests`（33 tests）。
- **Batch B 未做**：I-4（组件 full 状态矩阵）、I-5（motion 三态×三类）、I-7（PNG opt-in）、I-8（Elevation 消费+高对比回退）、I-11（焦点环/浮层焦点/Tab 序）。

## 3. 事件与处置（必须记录）

- ZCode 会话在完成大部分实现后崩溃（`0xC0000409`），未写证据/Handoff；工作树遗留 10 个修改 + 2 个新测试文件 + 3 个被默认全量覆盖的 `verification/FEA-06/screens/*.png`。
- DSH 处置：恢复 3 个旧 PNG 到 HEAD 字节；核对全部改动在 allowed_paths 内；修正 1 个异步测试竞态（改为 `PumpUntil`；实现语义未改）；重建 + 安全全量 + 生成器/治理验证；补写本 handoff 与证据日志。
- **未完成的安全义务**：I-7（PNG opt-in）在 Batch B；在那之前全量验证必须使用排除 `FluentPages_RenderHeadlessPngEvidence` 的 filter，不得声称无过滤全量已复跑。

## 4. Batch B 派发建议

- 建议实现 Agent：Codex CLI（若额度恢复）或 ZCode 新会话；必须先读 Task 范围 v3 的 Batch B 子项与 `doc/reviews/FEA-06-RESIDUAL-1-scope-r3.md` R3-002/R3-003/R3-004 口径。
- 顺序：I-7（PNG opt-in，恢复无过滤全量 1138/0/57 起点）→ I-4（组件×适用状态矩阵 + 有效属性断言）→ I-5（motion 三态×三类表驱动）→ I-11（焦点环/浮层焦点/Tab 序 + Current 对照）→ I-8（Elevation 消费 + high-contrast 回退 + Current 对照）。
- 验收：build 0/0；无过滤全量 1138/0/57 起点 + 新增测试；FEA-07 非回归子集；两生成器；check/pins；旧证据字节不变（`verification/FEA-06/screens/**` SHA 对照）。
- 之后：fresh 独立 impl Review（Codex 恢复则 Codex，否则 ZCode）→ DSH 集成验证 → done/closed_with_limitations。
