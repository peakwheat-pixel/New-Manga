# FEA-11-WATCH-1 Handoff（Host-only 目录 watcher hint → 全量重枚举）

- 日期：2026-11-06（Asia/Shanghai）
- Owner：`fea12-core-host`（DSH Agent Teams）
- Task：`doc/tasks/FEA-11-WATCH-1.md`（status → `in_review`）
- Base：`919c9aa1e`；Branch `main`；未 push、未创建 worktree。
- 实现 commit：`e60105cf9`（本 Handoff 随实现同 commit 交付；未 push）。
- 证据：`verification/FEA-11-WATCH-1/`（`record.md`、`logs/**`、`host-watch-runtime.json`、`scope-validation.log`、`changed-files.txt`）。

## 1. 交付内容

新增：

- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceWatcher.cs`：Host-only 只读目录 watcher（`SourceWatchOptions` / `ISourceWatchHandle` / `ISourceWatchFactory` / 生产 `FileSystemWatcher` 适配 / `SourceWatcher`）。
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceWatcherTests.cs`（15 例；fake adapter + 注入时钟 + 1 例真实隔离文件树）。
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11WatchHostRuntimeTests.cs`（gated `[HostSidecarFact]`，Ready→arm→真实事件 hint→Dispose disarm）。

修改：

- `Sources/SourceScanScheduler.cs`：`HintSource/HintAllTargets/HintPending/HintIdleAsync`；tick 单飞合并 + 释放 gate 后最多 1 次 replay；hinted 同预算优先、按实际扫描结果消费 due bit；`TargetSetChanged` + `TargetSnapshot()`；`SetWatcherStatus` 与 `Snapshot().Watcher`。
- `Sources/SourceScanStatus.cs`：closed `SourceScanWatcherStatus` + `SourceScanStatus.Watcher`（无路径/grant/session）。
- `HostOptions.cs`：`SourceWatchEnabled=true`、`SourceWatchMaxWatches=256`、`SourceWatchInternalBufferBytes=65536`、`SourceWatchDebounceMilliseconds=2000`。
- `HostRuntime.cs`：Ready 后、scheduler `Start()` 后 arm watcher（先于冷启动枚举）；`Stop/Dispose` 先 `StopSourceWatcher()` 再停 scheduler/Core；新增 `Watcher` 属性。
- `tests/.../SourceScanSchedulerTests.cs`：+6 AC-W4 用例。
- `doc/tasks/FEA-11-WATCH-1.md`：status/AC-W/证据/Owner 交付段。

**未触碰**：App/UI/Core/契约/schema/依赖/STATUS/PLAN/LEDGER/reviews/18 pins；未使用真实用户数据；无新依赖（BCL `System.IO.FileSystemWatcher`）。

## 2. 语义摘要（与卡冻结口径一致）

1. 事件只产生 per-source due bit；N 事件在 2000ms 去抖窗口内合并为 1 次；不向 scheduler/状态传递路径/change type；**hint 不是 changed/deleted 证据**。
2. 一次 hint → 一次既有 `ScanSourceSync` 全量重枚举；受 SCAN-1 单飞/预算/退避/pause/零写约束；命令集合精确 `{ScanSourceSync}`。
3. overflow / 根删除 / 句柄失效 → 不崩；全部 target due（下一 tick 起受预算跨 tick 完成）、`OverflowCount/Degraded/Uncovered` 计数、re-arm 或 typed 降级；周期扫描兜底。
4. 只 watch 已注册 target 根；file 精确文件（父目录 + filter + 事件名二次精确匹配）、folder 递归；arm 前 registry 复核；撤销/不可读 → `uncovered`。
5. 生命周期：Start 幂等；Stop/Dispose 幂等，Stop 后零 hint；Host 停机顺序 watcher → scheduler → session/Core。

## 3. 测试与门禁（实跑）

| Gate | 结果 | 证据 |
|---|---|---|
| Host 单测全量 | **179 passed / 0 failed / 55 skipped**（基线 158/54；+21 新增、+1 gated skip） | `logs/watcher-unit.log` |
| gated HostRuntime watcher | **1/0/0**（Ready→armed→Active=1→HintCount=1→Dispose 后 null） | `logs/watcher-runtime.log`、`host-watch-runtime.json` |
| 全量 .NET RUN1/RUN2 | **1521/0/86**、**1521/0/86**，EXIT 0（基线 1500/0/85 不降） | `logs/dotnet-full-1.log`、`logs/dotnet-full-2.log` |
| 全量 pytest | **3212 passed / 10 skipped**（与引用基线一致；零 Python 改动，仍实跑） | `logs/pytest-full.log` |
| 判别变异 M1/M2/M3 | 分别红（去抖合并/overflow 全量 due/优先排序）；恢复后重跑绿 | `logs/mutation-m1-debounce.log`、`mutation-m2-overflow.log`、`mutation-m3-priority.log` |
| pins / API / check / scope | 18/18；PASS；PASS（3 既有 warnings）；scope diff 空 | `logs/pins.log`、`logs/api-inventory.log`、`logs/check.log`、`scope-validation.log` |

全量 .NET 每轮后执行 `git checkout -- verification/FEA-09`；本轮两轮均 0 failed（无 flaky 需隔离复跑）。

## 4. AC-W 判定

AC-W1…AC-W5 全 **MET**（逐条证据见 `verification/FEA-11-WATCH-1/record.md` §2）。AC11-1 **不回填**；本卡不做启动全量扫描。L10 不解决；SCAN-2 RH-3 不修。

## 5. 复现命令

```powershell
# Host 单测（含新增）
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build
# gated HostRuntime watcher 用例（真实 sidecar 包）
$env:NEWMANGA_CORECLIENT_SIDECAR_DIR='apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar'
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Fea11WatchHostRuntimeTests"
# 全量
dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build
git checkout -- verification/FEA-09
C:/Python314/python.exe -m pytest tests -q -p no:cacheprovider
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-WATCH-1.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
C:/Python314/python.exe tools/generate_api_inventory.py --check
git diff --name-only 919c9aa1e..HEAD -- doc/plan doc/contracts src/   # 期望空
```

## 6. 残余风险 / limitation

- watcher 仅是检测延迟优化：漏事件（网络盘/卷类型/句柄失效）由 SCAN-1 周期扫描兜底，不作为正确性依赖。
- folder 根内任意层事件都映射为该 source due（无增量 diff）——符合冻结语义，但大目录可能增加全量重枚举频率（受预算/单飞约束）。
- `SourceScanScheduler` target 集仍只增不减（SCAN-2 RH-3 不修）；撤销/替换 target 由 arm 复核与 refresh 拆除覆盖。
- HostRuntime seam 无 fake-Core/注入时钟：gated 用例覆盖生产 wiring 与真实 OS 事件；确定性断言在组件级。
- 真实树事件测试理论上可能 flaky（本轮两轮全量 + 隔离运行均绿）。
- AC11-1 仍 PARTIAL（本卡不回填）；L10 不解决。

## 7. 复审就绪

- reviewed_head：实现 commit（见 `git log -1` 与本文件头部；本文件与代码同一 commit）。
- 复审重点：
  1. AC-W1：file/folder arm 规则、registry 复核、Stop 后零 hint、gated 用例断言；
  2. AC-W2：N→1 去抖、hint 非 changed、脱敏；
  3. AC-W3：overflow/根删除/上限/预算跨 tick；
  4. AC-W4：单飞 replay≤1、hinted 优先、backoff/pause 不绕过、命令集合；
  5. AC-W5：门禁数字与证据 sha、scope diff、无新依赖。
- 实现者未自审；未 push（DSH 负责集成/推送）。
