# V11R-C-3-READY 证据与就绪包索引

Owner: `design-platform`。分支 `v11r/c3-ready`，基线 = 当前 `main`
`c5037b65fb4c80a42e96869789d12a6e2427e954`（已合入新 UI / ThemeEngine Part B / DS D-1 终态 / B-4 I2b）。
本目录证据由真实执行产生；未执行项明确标注 `NOT_RUN`。

## 交付物

| 项 | 文件 | 说明 |
|---|---|---|
| 依赖图（结论/分类/迁移清单/零引用门） | `DEPENDENCY_GRAPH.md` | 634 引用 / 69 文件，按代码角色与处置分类 |
| 依赖图（机器可读） | `dependency-graph.json` | `references[]` 精确到 file/line/symbol/kind/fate/text |
| 依赖图（全表） | `dependency-graph-table.md` | 脚本生成，勿手改 |
| 依赖图生成器 | `tools/v11r/build-dependency-graph.ps1` | main 移动后重跑即可刷新 |
| 迁移门测试 | `apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/LegacyThemeRetirementGateTests.cs` | 26 例：9 旧 ID 文件级端到端 + 未知/空/旧键 + 幂等 + 表完整性 |
| 删除批次清单 | `DELETION_BATCHES.md` | A 可删 / B 需先迁移 / C 证据 pin 保护；R1–R6 顺序；旧测试→替代断言映射 |
| 回滚脚本 | `tools/v11r/rollback-theme-retire.ps1` | tag 回滚 + 设置备份/恢复 + build/旧符号/设置解析 smoke |
| 回滚演练步骤 | `ROLLBACK_DRILL.md` | L0 dry-run 已执行；L1/L2 NOT_RUN（留到 C-3） |
| L0 dry-run 证据 | `rollback-dry-run.log` | 脚本真实输出 |
| L3 对比度矩阵 | `verification/V11R-D-1/contrast-matrix.md` | 4 套盘 × 5 级背景；含未达标明细与判定依据 |
| L3 数据 | `contrast-matrix.json` | 机器可读比率/门槛/pass |
| L3 生成器 | `tools/v11r/contrast-matrix.ps1` | 从 tokens.json + 高对比字典重算 |

## 最终门禁（基线 `c5037b65`）

- `dotnet build NewManga.sln -warnaserror`：**0 warning / 0 error**（`build.log`）
- `dotnet test NewManga.sln --no-build`：**0 fail**；ThemeEngine **229**、DS **67**、App **237**(+6 skip)、Host **42**(+24 skip)、CoreClient **42**(+25 skip)（`test.log`）
- 迁移门 `LegacyThemeRetirementGate`：**26/26 pass**（`migration-gate-tests.log`）
- ThemeEngine 全量：**229/229 pass**（`themeengine-tests.log`）

## 验证命令

```powershell
# 迁移门测试（C-3 拆除前置门）
dotnet test apps/desktop-avalonia/tests/NewManga.ThemeEngine.Tests/NewManga.ThemeEngine.Tests.csproj `
  -warnaserror --filter "FullyQualifiedName~LegacyThemeRetirementGate"

# 依赖图刷新（main 移动后）
pwsh -NoProfile -File tools/v11r/build-dependency-graph.ps1

# 对比度矩阵刷新
pwsh -NoProfile -File tools/v11r/contrast-matrix.ps1

# 回滚 dry-run
pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 -DryRun   # tag 未建也可跑，完整 Plan + EXIT_CODE=0
```

## 边界与 NOT_RUN

- 本任务**不改** DS / ThemeEngine 产品代码、不改旧 `NewManga.Theme`、不改 App；仅新增测试、证据与 `tools/v11r/**`。
- 依赖图按当前 main 快照生成；C-3 执行时必须重跑（R2/R6），不能沿用旧 JSON 判定零引用。
- 回滚 L1/L2 演练、真实桌面启动 smoke：`NOT_RUN`（C-3 执行时）。
- 对比度矩阵的 **6 行 / 7 对**未达标明细是**真实计算结果**（JSON 含 `failing_pairs` 与 pair 明细），已附判定与建议；不是伪造通过。
- 旧测试替代映射中 5 条“需新增”断言（字体二进制审计、窗口 chrome 行为、窗口材质 fallback、首帧非阻塞、
  Theme Studio 设置页）必须在 C-3 R4 前补齐，否则不得删对应旧测试。




