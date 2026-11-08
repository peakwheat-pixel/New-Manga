# 变异自检（FEA-07-RESIDUAL-3 / R4b）

> 目的：证明 AC1 / AC3 / AC4 的判别断言是**承载证据的**，不是「写了但从不失败」的装饰。
> 每组：`sha256` 记录 → 注入故障 → **RED**（原始输出落 `logs/`）→ 从字节备份复原 → `sha256` **MATCH** → 复绿。
> 备份目录：`G:\CODEX\New Manga.workspace\FEA-07-RESIDUAL-3\mutation-backup\`（仓外，不随交付提交）。

## ① AC1 / A03：注入「切换过程写了保护列」

**故障注入**（`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea07Residual3IpcTests.cs`，切换循环之后、`after-switches` 快照之前）：
用内嵌 Python 对真实 `library.db` 执行 `UPDATE regions SET text_json='{"text":["mutation-leak"],"v":99}'`，
模拟「切换事务回归成会写库」。

- **RED**（`logs/mutation-1-a03-real-write.log`）：

```
frontend switching wrote the real library.db:
regions.<region>.text_json: {"text":["protected-pause-state"],"v":2} -> {"text":["mutation-leak"],"v":99}
失败! - 失败: 1，通过: 0，已跳过: 0，总计: 1
```

- **①b 附带判别（同一故障下删掉「切换前后快照」断言）**：`logs/mutation-1b-a03-assertion-removed.log`
  → 仍然 **RED**，这次由 AC1 的第二步逐列断言（`Assert.Equal(Column(before,"regions.<x>.text_json"), …)`）检出：

```
Assert.Equal() Failure: Strings differ
Expected: "{"text":["protected-pause-state"],"v":2}"
Actual:   "{"text":["mutation-leak"],"v":99}"
```

  ⇒ 「切换前建库快照 + 逐列相同」这条判别链**有两处独立检出点**（防御纵深）；字面删掉一条断言**不会**让故障漏检。
  因此不采用「只删断言」的形式（删断言本身永远不会让测试变红，无法作为变异证据），改为注入它所守护的故障。

- **复原**：`sha256` `74cdba4d250b936f9e16fcd641535e654e06eea588be6222453016293a39b0f2` **MATCH**
  → 复绿 `logs/mutation-1-restored-green.log`：**1 passed / 0 failed / 0 skipped**。

> 复原踩坑记录（口径，不隐藏）：`Copy-Item` 保留原 `LastWriteTime`，MSBuild 认为文件未变而跳过编译，首轮「复绿」跑到了旧的变异 DLL
> （仍 RED）。`touch` 时间戳后重新构建，复绿成功。该踩坑不影响 RED/MATCH 结论。

## ② AC3：恢复路径改为「直接采用 journal target」

**故障注入**（`apps/desktop-avalonia/tests/NewManga.App.Tests/Fea07Residual3CrashTests.cs`，把生产恢复入口
`App.RecoverInterruptedSwitch` 换成 `appearance.SaveAsync(settings with { FrontendId = interrupted.TargetFrontendId })`）。

- **RED**（`logs/mutation-2-ac3-adopt-target.log`）：`crash-switch.ps1` **exit code 12**（recover 断言失败）：

```
错误消息: Assert.Equal() Failure: Values differ
Expected: RolledBack
Actual:   Rendered
FATAL(12): recover fact failed
```

  ⇒ 证明「journal 终态必须是 `RolledBack`」不是被 target 覆盖也能过；生产恢复入口是必需的，不是可跳过的装饰。

- **复原**：`sha256` `a0d0b421a3f997d356bef7aa93a628d2999b63fa28e2325a83e11eb77c258b36` **MATCH**
  → 复绿 `logs/mutation-2-restored-green.log`：脚本 **exit code 0**，
  `recover evidence: status=ok journalStage=RolledBack finalFrontendId=builtin.current-v2 latestMode=Light secondRecoveryChangedNothing=True protectedColumnDiffs=0`。

## ③ AC4：删除 `StartupDiagnostics` 接线（诊断行断言必须 RED）

**故障注入**（`apps/desktop-avalonia/src/NewManga.App/App.axaml.cs`：删掉 `StartupDiagnostics.Install(options.ToHostOptions().LogDirectory);` 一行）。
**必须重建 App.Tests**（真实进程用例用的是 `NewManga.App.Tests/bin/.../NewManga.App.exe`；只重建 App 项目不够——首轮
`--no-build` 跑到了旧 exe，误显绿，已纠正重跑）。

- **RED**（`logs/mutation-3-ac4-sink-removed.log`）：门禁 `NEWMANGA_FEA07_STARTUP_PROCESS=1` 的真实进程 fact：

```
default: startup.log was not written
失败! - 失败: 1，通过: 0，已跳过: 0，总计: 1
```

- **复原**：`sha256` `07c93db9b979a16fbd2746383ede35f9535b6bd4012e11bb5dc52980f3ac2ce3` **MATCH**（`git diff --stat` = `+2` 行）
  → 复绿 `logs/mutation-3-restored-green.log`：**1 passed / 0 failed / 0 skipped**。

## 汇总

| # | AC | 故障注入 | RED 证据 | 复原 sha256 | 复绿 |
|---|---|---|---|---|---|
| ① | AC1 / A03 | 切换后写 `regions.text_json` | `logs/mutation-1-a03-real-write.log`（+ ①b 删断言仍 RED） | `74cdba4d…` MATCH | 1/0/0 |
| ② | AC3 | 恢复直接采用 journal target | `logs/mutation-2-ac3-adopt-target.log`（脚本 exit 12） | `a0d0b421…` MATCH | 脚本 exit 0 |
| ③ | AC4 | 删除 `StartupDiagnostics.Install` 接线 | `logs/mutation-3-ac4-sink-removed.log`（startup.log 缺失） | `07c93db9…` MATCH | 1/0/0 |
