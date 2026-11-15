# 我错了：裸跑"通过"其实是 SKIP —— `FILE_IDENTITY_CHANGED` 是真实缺陷

- head: `e66323bf2`
- 记录时间：2026-11-16

## 我此前的错误结论（R87 / R88 / R92 三次重复）

我在 R87 写：

> 三个测试**单跑全部 EXIT=0** ⇒ 不是稳定失败，只在两个测试一起跑时偶发。

在 R88 用它建卡，定性为「并发 flaky」。
在 R92 用它写 AC2 结论「裸环境 0 failed / 331 passed / 74 skipped」。

**这个推理链的起点是错的。**

## 实际是什么

用 `--logger "console;verbosity=detailed"` 单跑 `GrantIssuerTests`：

```
[xUnit.net] NewManga.Host.Tests.GrantIssuerTests.ShellActions_Open_Whitelisted_... [SKIP]
[xUnit.net] NewManga.Host.Tests.GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_... [SKIP]
[xUnit.net] NewManga.Host.Tests.GrantIssuerTests.Import_IntoNewChapter_Executes_... [SKIP]
[xUnit.net] NewManga.Host.Tests.GrantIssuerTests.ShellActions_RealOpener_... [SKIP]

已跳过 ... [1 ms]
已跳过 ... [1 ms]
已跳过 ... [1 ms]
已跳过 ... [1 ms]
```

**裸跑时这 3 个测试是 `[SKIP]`，根本没执行。**
而 `dotnet test` 的 `EXIT=0` **不区分 passed 与 skipped** —— 我把它当成了「通过」。

## 真正的结论

| 环境 | 这 3 个测试的状态 |
|---|---|
| 裸 `dotnet test` | **SKIP**（缺 `NEWMANGA_*` fixture 环境变量） |
| `test.ps1` | **实际执行** ⇒ 2 个失败、1 个（Fea11）已修好 |

⇒ `FILE_IDENTITY_CHANGED` **不是 flaky、不是并发问题**，而是这 2 个测试
**第一次真正执行**时暴露出来的**真实失败**。

## 这解释了所有此前矛盾的数据

| 现象 | 旧解释（错） | 新解释（对） |
|---|---|---|
| 裸跑 331 passed / 74 skipped | "3 个测试通过" | 3 个**跳过** |
| test.ps1 下 358 passed / 44 skipped | "30 个测试从 skip 变执行" | 正确；其中包含这 3 个 |
| 单跑 EXIT=0 | "通过" | **skipped 也返回 0** |
| 两次 test.ps1 都失败 | "确定性并发触发" | **它们真的失败了**（与并发无关） |

`passed + skipped = 405` 在两个环境下相同，**正是 skip↔pass 互换的证据**，我当时却读成了"并行度上升"。

## 对已做工作的影响

- **`SourceAccessRegistry` 的修复仍然有效且必要**：`Fea11WatchHostRuntimeTests` 的
  `SOURCE_REGISTRY_BUSY` 确实被消除了（3 failed -> 2 failed，passed 358 -> 359），
  那是被 skip 掩盖的**另一个真实缺陷**。修复本身没问题。
- **`HOST-CONCURRENCY-FLAKY-1` 的定性和 AC2 结论需要更正**：
  - 「并发 flaky」→ 应改为「首次真正执行时暴露的失败 + 一个真实的锁等待缺陷」；
  - AC2 的"复现"其实只是"在会执行它们的环境下运行"。
- **`FILE_IDENTITY_CHANGED` 是一个独立的新缺陷**，需要单独定位：
  注册时 Host 记录的 `file_id` 与导入时 Python `st_ino`
  （`scanner.py:163` `_stat_folder_entry` -> `st_dev`/`st_ino`/`st_size`）不一致。

## 共同根因（本会话第 6 次同类错误）

**把「命令成功退出」当成「被测行为正确」。**

前 5 次：
1. 夹具副本错认成产品 bundle
2. 从 weights 警告推断 pending 原因
3. probe 用点号命令名
4. probe 自己传 null
5. 诊断代码改控制流跳过断言

**第 6 次**：把 xUnit 的 `EXIT=0`（含 skipped）当成 passed。

**纪律**：判断"测试通过"必须看**具体结果行**（`已通过` / `失败` / `已跳过`），
`EXIT=0` 只说明"没有失败"，**不说明"跑过了"**。

## 下一步

1. 更正 `HOST-CONCURRENCY-FLAKY-1` 的定性（本文件即证据）；
2. 定位 `FILE_IDENTITY_CHANGED`：对比 Host 侧注册写入的 `file_id` 与 Python 侧
   `normalize_identity(st_dev, st_ino)` 的口径；
3. 这两个测试是**真实失败的测试**，修好它们才能让 `test.ps1` 真正变绿。
