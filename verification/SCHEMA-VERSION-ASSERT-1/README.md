# SCHEMA-VERSION-ASSERT-1 证据

按 Codex 裁决（2026-11-15）实施。

## 裁决要点（Codex 原文摘要）

- **方案 C 不属于"放宽既有断言"** —— 属"修正随产品迁移演进而过时的测试预期"。
  判断标准是是否削弱应验证的产品约束，不能仅因测试由红变绿就认定违规。
- 建议测试内常量 `Support/CoreSchema.cs`（`Current = 14`），不升格为产品契约。
- 必须加**默认执行**的跨语言守护：调 Python `default_migrations()` 校验数量；环境缺失**应失败**；
  **预期值不得取自被测回执**；**不得用正则读 `MIGRATION_V14_NAME`**。

## 实施

| 文件 | 改动 |
|---|---|
| `tests/.../Support/CoreSchema.cs` | 新增 `internal static class CoreSchema { public const int Current = 14; }` |
| `Fea11HostAuthIpcTests.cs` / `Fea11Residual4AIpcTests.cs` / `Fea11SourceIpcTests.cs` | 3 处 `Assert.Equal(9, …schema_version…)` → `Assert.Equal(CoreSchema.Current, …)` + `using …Support;` |
| `PythonSchemaMigrationGuardTests.cs` | 新增 `[Fact]`（默认执行）：`python -B -c "…default_migrations()…print('COUNT', len(...))"`，断言 `COUNT == CoreSchema.Current` |

守护测试的两个"不"：**不读被测回执**（问 Python 模块，不读 `schema_migrations` 或 IPC 回执）；
**不静默跳过**（`NEWMANGA_BUILD_PYTHON` 指向不存在文件 → 断言失败；未配置 → 用 `python`，不可用则抛）。

## 判别力

| 实验 | 结果 |
|---|---|
| 正常 | **1 passed** |
| **`CoreSchema.Current` 临时改 13** | **FAIL**：`Expected: 13, Actual: 14`（已还原，`PROBE`=0） |

## 效果（带 opt-in 三类定向复跑）

修复前 7+ 个 schema 失败 → 修复后 **13 个：11 passed / 2 failed**。
剩余 2 个**不是 schema**：`Fea11SourceIpcTests.FullSyncChain_…` 与
`Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_…`，
错误 `new container must produce a changed page`（source chain 逻辑，**待归因**）。

## 未做

- 2 个 `FullSyncChain` 失败未归因。
- `Fea11HostAuthIpcTests` 的 2 个 `NEWMANGA_FEA11_CRASH_STATE` 依赖未处理（环境变量）。
- 未跑无夹具三项目全量（本卡只改测试常量 + 新增默认测试；后者需要 python，这是**有意**的）。
