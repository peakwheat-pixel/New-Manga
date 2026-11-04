---
task_id: FEA-10
author: Codex（本次全新实现上下文；未自审）
recipient: DeepSeek Harness
base_commit: aa7bcd6161be5df07e2b8bf546600fec04af038f
delivery_head: null
status: partial_delivery
---

# Handoff：FEA-10

## 交付结果

**部分实现交付，尚不可集成关闭。** 工作区 `G:/CODEX/New Manga`，`main`，起始及当前 HEAD 均为 `aa7bcd6161be5df07e2b8bf546600fec04af038f`；无 commit/push，delivery_head 留空。DSH 原有 `status/claimed_at` 改动未回退；Task 按用户交付要求转 `in_review`，其含义不是全部 AC 通过。

已实现：既有 PipelineService 的 Prepare/Accept；Host 内存 candidate 与安全 UI preview；精确四元组 digest；BEGIN IMMEDIATE 接受校验；既有 durable receipt 优先查询；远程 typed provider config 快照；已知源文本翻译的 canonical request 验证；邻页内容 pin；Step seam 的 draft/binding/manual/final 守卫；终态计数修正；真实 IPC/Core 重启测试。复用现有 Run store/scheduler/RegionStepWriter/SqliteTargetCatalog/DraftProtectionService/RunMonitor，不另建真值或调度器。

逐 AC 结论和证据层级见 [AC-MATRIX](../../verification/FEA-10/AC-MATRIX.md)。AC2/AC3/AC4/AC6 未完全满足；AC9 被治理指针及 Review/集成前置阻塞。不得将这些项改写为 MET。

改动文件（精确最终清单另见 `verification/FEA-10/changed-files.txt`；含 untracked）：

- Python：`src/application/tasks/service.py`、`store.py`、`projection.py`；`src/infrastructure/sqlite/pipeline.py`；`src/infrastructure/pipeline/assembly.py`、`executor.py`；`src/infrastructure/providers/handlers.py`、`registry.py`；`src/bootstrap/core_assembly.py`、`core_service.py`。
- C#：`NewManga.CoreClient/CoreServiceClient.cs`；`NewManga.Host/HostRuntime.cs`；`NewManga.App/Services/HostController.cs`、`NullHostController.cs`、`RunContracts.cs`（均在 `apps/desktop-avalonia/src/`）。新增独立 `IPreparedRunController`，没有修改 C-07 的 IHostController 54-member 面。
- 测试：`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10RunIpcTests.cs`；`tests/fea10/test_prepared_run.py`、`test_snapshot_retry.py`、`test_commit_zero_write.py`、`test_idempotent_receipt.py`、`support/restart_core.py`。
- 文档/证据：`doc/tasks/FEA-10.md`、本 Handoff、`verification/FEA-10/**`。

三处 request builder 边界文件、冻结契约、共享组合根、FEA-08/09 closeout 均未修改。既有 .NET 测试重写过 `verification/FEA-09/logs/wire-redacted.ndjson`；已按用户指令恢复，最终再次核对零 diff。

## 验证证据

环境：Python 3.14.6 / pytest 9.1.1（`C:/Python314/python.exe`）；.NET SDK 10.0.401；Node v24.15.0。被测内容为上述 HEAD + 本次未提交工作树；具体字节清单见 DELIVERY-MANIFEST。没有把未提交字节说成已审 commit。

| AC/场景 | 实际命令 | EXIT / 结果 | 日志 |
|---|---|---|---|
| AC1–AC8 Python 全量 | `C:/Python314/python.exe -m pytest tests/fea10 tests/core tests/pipeline -q` | 0；1036 passed，1 项既有 Pillow DeprecationWarning | `verification/FEA-10/logs/python-isolated.log` |
| 卡中逐文件回归 | `C:/Python314/python.exe -m pytest` + 卡中 14 个精确文件 + `-q`（完整命令在日志首行） | 0；204 passed | `verification/FEA-10/logs/python-files-validated.log` |
| 追加 provider 回归 | `C:/Python314/python.exe -m pytest tests/providers -q` | 0；559 passed / 4 skipped（既有环境/optional dependency 门径） | `verification/FEA-10/logs/provider-regressions-second.log` |
| FEA-10 专项 | `C:/Python314/python.exe -m pytest tests/fea10 -q` | 0；33 passed | `verification/FEA-10/logs/fea10-fallback-final.log` |
| AC5 10 类故障与两类事务 | `C:/Python314/python.exe -m pytest tests/fea10/test_commit_zero_write.py -v` | 0；17 passed，逐项名称记录 | `verification/FEA-10/logs/fault-matrix.log` |
| AC7 两进程重启 | `restart_core.py --data-root <fixture> --db <fixture>/library.db --stop`，再同路径 `--start` | 两次均 0；同 run_id、无第二 Run | `verification/FEA-10/logs/restart-core.log` |
| AC3/AC8 production transport/commit | `C:/Python314/python.exe -m pytest tests/fea10/test_snapshot_retry.py::test_preview_and_real_transport_body_use_same_builder_and_pinned_config -q` | 0；1 passed | `verification/FEA-10/logs/canonical-commit.log` |
| Release build | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | 0；0 warning / 0 error | 最终 `logs/dotnet-final-build.log` |
| .NET 全量 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | 0；1344 passed / 0 failed / 75 skipped（通过数未减少） | 最终 `logs/dotnet-final-tests.log` |
| 真实 IPC | `$env:NEWMANGA_FEA10_IPC='1'; $env:NEWMANGA_BUILD_PYTHON='C:/Python314/python.exe'; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Fea10RunIpcTests` | 0；1 passed（含新候选同 fingerprint 同键重放、Core 重启） | 最终 `logs/ipc-final.log` |
| 冻结 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0；17/17 PASS | `verification/FEA-10/logs/pins-final.log` |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | 1；Plan READY 节点仍为 FEA-10，Task 已 in_progress/in_review；需 DSH 改写域外指针 | `verification/FEA-10/logs/governance-initial.log`，最终 `logs/governance-final.log` |
| 范围及原字节 | `git diff --name-only` + untracked 与 allowed_paths 比对；`git diff --exit-code -- verification/FEA-09` | 0；最终范围检查含 untracked；FEA-09 恢复后零 diff | `verification/FEA-10/logs/scope.log` |

新增 .NET IPC 默认环境门径跳过，已单独显式开启；全量新增 1 skip，所以从基线 74 变为 75，不计入通过数。其他 skip 均为既有真实 sidecar/硬件/外部 provider 等 opt-in 门径，不代表对应能力已经验收。

## 接收方式

不切分支、不 stash、不 checkout 主树实现；DSH 在当前 dirty 主树接收。所有新用例的 DataRoot 位于 `G:/CODEX/New Manga.workspace/FEA-10/fixtures/<case>-<uuid>/`，同库重启的精确路径在 restart 日志；没有新依赖、模型或真实源数据。运行测试可复现，禁止将 fixture DB 当作用户库。

Task 卡原 `base_commit=d831cf...` 保留为 scope 历史；本次实际实现基线是 `aa7bcd...`。DSH 集成时填写真正 delivery_head、commit pins 与 Reviewed head，不使用起始 HEAD 冒充包含本次变更的提交。

## 下一任务建议（待 DSH 裁决/释放）

- Task：FEA-10 续作/范围处置；不释放 FEA-11。
- 推荐 Agent：DSH 先处理治理指针及以下契约落地边界；再指派 Codex 继续实现；完成后由 DSH Appointment 全新独立上下文 Reviewer。
- 前置：明确未来 OCR 输出的精确预览口径、全部 provider 的版本快照/blocked 行为、新配置确认流程；必要时窄批 request builder 三文件变更。
- Recovery point：`G:/CODEX/New Manga`，`main`，base/head=`aa7bcd6161be5df07e2b8bf546600fec04af038f` + DELIVERY-MANIFEST 未提交字节；新 worktree 待 DSH 创建。
- 允许路径：Owner 仍仅 FEA-10 卡 allowed_paths；PLAN/STATUS/Appointment 指针由 DSH 单点修改；三处 builder 默认只读，窄改须 DSH 明确批准。
- 禁止：冻结契约、共享组合根、FEA-08/09 closeout/evidence 字节、依赖/Schema/新 wire、真实用户数据、push。
- 交付：补完 AC2/3/4/6 及专项验证，再次 Handoff/EV；上下文独立 Review、DSH 集成验证全部通过后才能 done。
- Gate：卡中全部命令实跑、check PASS、pins 17/17、范围合规、回归不减少、无未说明 NOT_RUN。
- 可直接转发：

> DSH：请在 `G:/CODEX/New Manga` 的 main、HEAD `aa7bcd6161be5df07e2b8bf546600fec04af038f` 接收 FEA-10 未提交交付，先核对 DELIVERY-MANIFEST 与 dirty 文件，不回退 claimed_at 或他人字节。当前 AC2/3/4/6 PARTIAL、AC9 BLOCKED；请先修复 PLAN/STATUS 的 ready 指针并裁决 AC-MATRIX 所列的未来 OCR 精确预览、完整 provider 版本快照/blocked 与新配置确认口径。若需直接冻结/发送同一 HTTP 请求对象，请明确窄批 protocol.py/translation_openai.py/openai_client.py；随后按既有 allowed_paths 重新释放 Codex 续作。完成全部 AC 后固定交付 commit，派全新上下文只读 Review，重跑 build/test/真实 IPC/pytest/check/17 pins/范围与 FEA-09 零 diff，再由 DSH 集成收口。不 push。

## 风险与遗留

1. 精确预览仅对已有源文本的 `retranslate_region` 有 transport 级证明。上游 OCR 依赖请求返回 requires_upstream_output；不得据此宣称所有命令“预览=发送”。
2. 远程 typed config 已冻结，其他 provider 可只含 ID；本地版本不可用 blocked、新配置差异确认流程尚未闭环。普通旧 StartRun 路径继续兼容，不能误称已具有全部新路径的白名单保证。
3. source lease/Binding generation 故障是可注入 seam 测试；未跑 Windows 原生源故障、完整 referenced pipeline 正向读取及 FEA-11/13 行为。
4. AC6 完整 UI 重连/非法终态/重启计数专项矩阵尚未补齐；现有回归不足以将其判 MET。
5. 治理失败来自写域外 Plan 状态指针；不可将 Task 临时改回 ready 以“刷绿”。独立 Review/DSH 集成 NOT_RUN。
6. **早期测试环境偏差**：既有回归继承系统 TEMP/TMP（AppData/Local/Temp），产生测试临时材料；违反此 Task 的目录约束。未使用真实应用数据库、未额外清理/扫描系统 TEMP。最终门禁已改为 workspace 的独立 TEMP/TMP；早期材料保留，交 DSH 处置，不宣称零 AppData 临时写。
7. 历史失败日志保留：新增测试参数、断言匹配、适配器兼容、manual OCR 保护过宽已修复；一次并发 build 被 testhost 占 DLL 而失败，后续需序列化 build/test。没有同一用例连续超过两次仍未解决而继续循环。

无授权删除/移动/清理资源；Resource Manifest 保留 fixtures、bin/obj、证据和未知早期临时材料，disposition 由 DSH 收口。Handoff 不授予提交、集成、关闭或 push 权限。
