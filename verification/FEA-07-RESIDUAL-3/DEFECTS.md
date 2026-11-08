# DEFECTS / 口径偏差登记（FEA-07-RESIDUAL-3 / R4b）

> 本卡只登记**观测到的事实**。未修项均为**不在 allowed_paths 内**或**超出本卡范围**，不伪造修复、不改契约/生产语义。

## D-R4b-1（口径偏差，证据强度）冻结卡列名 `region_candidates` 在冻结 schema 中不存在

- **事实**：`doc/tasks/FEA-07-RESIDUAL-3.md:52` 要求比对 `regions.text_json`、`current_revision_id`、三锁列、manual 位、`region_revisions` 行数、**`region_candidates` 行数**。`src/infrastructure/sqlite/schema.py` 无 `region_candidates` 表；候选结果的真实存储是 `step_result_candidates`，V5 迁移把它改名为 `step_result_candidates_v5`（`schema.py:534-550`）。
- **本卡处置**：比对脚本按「存在则取 `step_result_candidates_v5`，否则取 `step_result_candidates`，都不存在则计 0」读；AC1 的「旧结果仅 candidate」断言为 **候选存量 0 → 0、零解析、陈旧 base 未进入 `current_revision_id`**（`README.md` §6.1 已如实降级说明）。
- **未做（需 DSH 裁决）**：若要 `region_candidates` 强证据，需要在冻结库里造出合法 `pipeline_runs`/`step_runs` 父行（`run_json` 必须由真实装配写出）并让候选被解析；**伪造 `run_json` 会让真实 Core 在启动恢复时崩溃**（本卡实测：`KeyError: 'run_id'`，`recover_running_runs` → `_run(value["run_id"])`），因此不做伪造。建议由候选/结果卡以生产装配路径补强。
- **不影响结论**：AC1 的「切换不得写保护列」由 6 个列族 + 2 个行数逐列比对承担；候选存量是其中一项且保持 0。

## D-R4b-2（r1 已修，扩域留痕）`--shell=legacy` 曾把诊断写到真实 `%APPDATA%`，忽略 `--log-dir`

- **r0 事实**：`apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:883-895`（`WriteMaterialDiagnostics`）
  硬编码 `Path.Combine(GetFolderPath(ApplicationData), "com.newmanga.desktop", "logs", "window-material.log")`，
  与 `AppOptions.LogDirectory`/`--log-dir` 无关。该文件 **2026-10-27** 起已有条目（远早于本卡）；本卡 r0 的 AC4
  `--shell=legacy` 真实进程用例又各追加 1 行（独立 Review r1 度量：14,272 → 14,275）。
- **r1 修复（DSH 2026-11-08 裁决 A，授权扩域该单文件）**：改为「显式 `--log-dir` 时 `LogDirectory` 拥有全部日志文件
  （含本文件）；无 `--log-dir` 保留历史每用户位置」。实际 diff **+5/−1**（3 行语义 + 2 行理由注释；Lead 批复口径
  写 +3/−1，指语义行）。未改组合根逻辑、未改 `*.axaml`、未动其它 `src/NewManga.App/**`。
- **r1 验证（红线）**：gated AC4 fact 14/14 + `startup-matrix.ps1` 4/4 均为真实 `%APPDATA%`
  `window-material.log` 行数 `14275 → 14275`（delta=0）；legacy 用例的 `window-material.log` 落在隔离 `--log-dir`（1 行）。
- **r1 变异证据**：把三行改回硬编码（M4，保留 env 隔离）→ 隔离目录断言 RED；再把 env 隔离也去掉（M4b = r0 现场）→
  真实 `%APPDATA%` `14275 → 14276`（**+1**）且用例 RED（`logs/mutation-4b-p1-redline-regression.log`）；
  复原后两文件 sha256 MATCH、复绿 delta=0（`logs/mutation-4-restored-green.log`）。
- **残留说明（如实登记）**：M4b 主动造成的 **+1 行不删除**（删除本身就是又一次真实目录写入）；此后基线为 `14276`，
  所有 r1 运行均 `delta=0`。
- **测试侧第二道闸（纵深防御）**：`StartupDiagnosticsTests` 与 `startup-matrix.ps1` 还向子进程注入隔离的
  `APPDATA`/`LOCALAPPDATA`/`USERPROFILE`，并用同一环境字典回读子进程值确认注入生效。实测口径更正：
  **单独注入 `APPDATA` 不足以改变** `Environment.GetFolderPath(ApplicationData)`（CSIDL/KnownFolder）；
  `APPDATA`+`USERPROFILE` 同时注入时该 API 返回隔离路径。因此「产品契约（`--log-dir` 拥有全部日志）」是主闸，
  env 注入是第二道闸 —— 这也是变异 M4（只回退产品契约、保留 env 隔离）仍 RED 的原因：隔离目录断言直接失败。

## D-R4b-6（erratum，P3-01）卡面把 `region_locked` 写成 `sfx_locked`

- **事实**：`doc/tasks/FEA-07-RESIDUAL-3.md:52` 写作 `translation_locked`/`inpaint_locked`/**`sfx_locked`**；
  冻结 schema（`src/infrastructure/sqlite/schema.py:248-250`）的实际列是 **`region_locked`** / `translation_locked` /
  `inpaint_locked`，另有 `sfx_policy ∈ {skip, translate, manual}`（卡面所谓「manual 位」= `sfx_policy='manual'` 行数）。
- **处置**：本卡的比对与断言按真实列名执行（`region_locked`），本文件与 `README.md` §3/§6 记为 erratum；不改卡面字节
  （卡面 `status`/验收行由 DSH 关账）。

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

## D-R4b-7（既有测试隔离缺口，未修；r1 保真登记）headless 里 `Show()` 过 legacy `MainWindow` 的既有用例仍写真实 `%APPDATA%`

- **事实**：r1 修复后「显式 `--log-dir` 拥有全部日志文件」成立，但没有 `--log-dir` 的调用方仍按设计落历史每用户位置。
  既有 App.Tests 里有一批用例构造并显示 legacy `MainWindow`（`MainWindow`/`--shell=legacy` 面共 16 个文件命中，
  其中 `StartupCompatibilityMatrixTests`(5)、`FluentShellTests`(1)、`AppOptionsCliRobustnessTests`(1) 等）且**不传** `--log-dir`
  ⇒ 每次显示会向真实 `%APPDATA%\com.newmanga.desktop\logs\window-material.log` 追加 1 行。
- **度量（r1 返修期间）**：`14276 → 14340`（**+64**），分布在两轮 App.Tests + 两轮全量 sln + pytest 之间；
  **对照实验**：只跑一轮 `NewManga.App.Tests`（默认门禁，无 gated）→ `14340 → 14356`（**+16 行/轮**）；
  单独只跑 `StartupCompatibilityMatrixTests`（2 例、7 个 shell、无 `Show()`）→ **delta=0**，说明触发点是 `Show()` 而非构造。
- **与 r1 的关系**：**与 r1 的 P1 无关**（r1 只改「有 `--log-dir` 时」的行为；这些用例没有 `--log-dir`，修复前后同样写真实路径，
  属**既有**测试隔离缺口）。AC4 红线断言（gated fact 14/14、`startup-matrix.ps1` 4/4）在各次运行均为 **delta=0**。
- **为什么不修**：修复方式是给这些既有用例补 `--log-dir`（`tests/NewManga.App.Tests/**` 虽在 allowed_paths，但属新增改动面、
  超出 r1 的 finding 范围，且会改动多份既有测试）。建议另立卡：`--log-dir`（或测试用 `--home-root`）覆盖全部既有 UI 用例。
- **影响**：不影响产品行为（发行版无 `--log-dir` 时历史位置是刻意保留的默认）；只影响「测试是否触碰真实用户目录」的纯度。

## D-R4b-8（r1 证据噪声，已处理）并发写入会让既有 `FluentResidual2VisualEvidenceTests` 假红

- **事实**：`FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 断言
  「运行期间 `git status --porcelain -- verification` 前后一致」。r1 首轮全量运行期间本会话在编辑本证据目录、
  另有外部 `gates-lead.log` 落盘 ⇒ 快照 `??` → ` M`，该用例 FAIL（1 failed）。
- **处置**：静默树复跑 **1792/0/107**；原失败日志保留为 `logs/full-solution-tests-first-run-concurrent-write.txt`。
  **不修改**该既有断言（不属于本卡范围）；登记为「并发写入假红」。

## D-R4b-5（口径提醒，非缺陷）AC1 的「真实 Host」边界

- 本卡 AC1 用的「真实 Host 面」= production `CoreServiceClient`（真实 Python `core_service` over stdio）+
  production `HostCommandDispatcher`（Host 命令路由/payload/结果映射）+ production `CurrentRunIntentCoordinator`
  （intent 去重）。**未**经 `HostRuntime`（需要打包 sidecar 可执行文件）与 Avalonia 组合根；UI 侧 layout/Loaded/render
  门禁由既有 headless 用例覆盖。此边界在 `README.md` §6.2 如实登记，避免把「真实 Host 面」写成「完整生产进程链路」。
