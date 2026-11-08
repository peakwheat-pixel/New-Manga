# DEFECTS / 口径偏差登记（FEA-07-RESIDUAL-3 / R4b）

> 本卡只登记**观测到的事实**。未修项均为**不在 allowed_paths 内**或**超出本卡范围**，不伪造修复、不改契约/生产语义。

## D-R4b-1（口径偏差，证据强度）冻结卡列名 `region_candidates` 在冻结 schema 中不存在

- **事实**：`doc/tasks/FEA-07-RESIDUAL-3.md:52` 要求比对 `regions.text_json`、`current_revision_id`、三锁列、manual 位、`region_revisions` 行数、**`region_candidates` 行数**。`src/infrastructure/sqlite/schema.py` 无 `region_candidates` 表；候选结果的真实存储是 `step_result_candidates`，V5 迁移把它改名为 `step_result_candidates_v5`（`schema.py:534-550`）。
- **本卡处置**：比对脚本按「存在则取 `step_result_candidates_v5`，否则取 `step_result_candidates`，都不存在则计 0」读；AC1 的「旧结果仅 candidate」断言为 **候选存量 0 → 0、零解析、陈旧 base 未进入 `current_revision_id`**（`README.md` §6.1 已如实降级说明）。
- **未做（需 DSH 裁决）**：若要 `region_candidates` 强证据，需要在冻结库里造出合法 `pipeline_runs`/`step_runs` 父行（`run_json` 必须由真实装配写出）并让候选被解析；**伪造 `run_json` 会让真实 Core 在启动恢复时崩溃**（本卡实测：`KeyError: 'run_id'`，`recover_running_runs` → `_run(value["run_id"])`），因此不做伪造。建议由候选/结果卡以生产装配路径补强。
- **不影响结论**：AC1 的「切换不得写保护列」由 6 个列族 + 2 个行数逐列比对承担；候选存量是其中一项且保持 0。

## D-R4b-2（既有缺陷，未修）`--shell=legacy` 把诊断写到真实 `%APPDATA%`，忽略 `--log-dir`

- **事实**：`apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:883-895`（`WriteMaterialDiagnostics`）硬编码
  `Path.Combine(Environment.GetFolderPath(ApplicationData), "com.newmanga.desktop", "logs", "window-material.log")`，
  与 `AppOptions.LogDirectory`/`--log-dir` 无关。证据：该文件在 **2026-10-27** 已有条目（远早于本卡），本卡 AC4 的
  `--shell=legacy` 真实进程用例又追加了 1 行（`logs/startup-matrix.log` 与 `evidence/startup-matrix-r4b.json` 的
  `shell-legacy` 用例时间戳对应）。
- **影响**：W-9「测试/证据所有 data/theme/journal 路径限定隔离根」在 **legacy 外壳的一条诊断日志**上不成立（不是用户数据、
  不是 `library.db`、不是主题设置；仅追加式日志行）。
- **未修原因**：`MainWindow.axaml.cs` 不在本卡 `allowed_paths`（仅 `App.axaml.cs` ≤5 行 + 新 `StartupDiagnostics.cs`）；
  改它属于生产行为/组合根变更，需 DSH 另立卡。
- **对本卡证据的影响**：AC4 的 default / presentation-host / corrupt-appearance 三组用例**不触碰**真实 `%APPDATA%`
  （实测：`%APPDATA%\com.newmanga.desktop` 40 分钟内唯一新增写入即 `window-material.log`，来自 `--shell=legacy` 用例；
  `%APPDATA%\NewManga` 零新增）。见 `RESOURCE-MANIFEST.json` 的 `user-data` / `tracked-side-effect` 行。

## D-R4b-3（既有 flaky，未修）pytest `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`

- **事实**：与 R4a 登记的同一既有 flaky（`doc/tasks/FEA-07-RESIDUAL-2.md:195` L-R4a-4）。本卡零 Python 源码/测试改动
  （`git diff HEAD -- src tests` 为空），该 flaky 与 AC1/AC3/AC4 无关。
- **处置**：全量结果按实际记录（`logs/pytest-r4b.txt`）；若命中，隔离复跑 `tests/plugin/test_plugin_sandbox.py` 确认通过，
  与 R4a 同口径，不掩盖。

## D-R4b-4（脚本缺陷，本卡内已修）PowerShell 参数拼接把多个 CLI 参数合并成一个

- **事实**：`startup-matrix.ps1` 初版用 `@('--data-root=' + $x, '--log-dir=' + $y, ...)`，PowerShell 把逗号解析得比 `+`
  更紧 → 生成**一个**空格连接的参数，真实 App 因此收不到 `--log-dir`/`--exit-after`，首轮实跑 `default` 用例超时（脚本
  超时保护生效，exit code 未误记 PASS）。
- **修复**：改为 `[System.Collections.Generic.List[string]]` 逐个 `Add()`，并把完整 argv 写进日志（`argCount=5/6`）。
- **副作用**：该次失败运行在真实 `%APPDATA%\com.newmanga.desktop` 下留了 1 行 `window-material.log`（见 D-R4b-2），
  未触碰用户数据；目录原本存在。
- **复发防护**：脚本现在显式记录 argv，回归时可从日志判定参数是否被合并。

## D-R4b-5（口径提醒，非缺陷）AC1 的「真实 Host」边界

- 本卡 AC1 用的「真实 Host 面」= production `CoreServiceClient`（真实 Python `core_service` over stdio）+
  production `HostCommandDispatcher`（Host 命令路由/payload/结果映射）+ production `CurrentRunIntentCoordinator`
  （intent 去重）。**未**经 `HostRuntime`（需要打包 sidecar 可执行文件）与 Avalonia 组合根；UI 侧 layout/Loaded/render
  门禁由既有 headless 用例覆盖。此边界在 `README.md` §6.2 如实登记，避免把「真实 Host 面」写成「完整生产进程链路」。
