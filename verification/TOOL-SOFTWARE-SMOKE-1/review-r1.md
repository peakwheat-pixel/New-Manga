---
task_id: TOOL-SOFTWARE-SMOKE-1
reviewer: reviewer-tool-smoke
author: dsh
base_commit: 6e3ce06f96bb48bc7a8de0a114c8391a9bc82014
reviewed_head: 963ff5e6f77f153de2a58153940c96c7569ef22c
decision: approved
---

# Review：TOOL-SOFTWARE-SMOKE-1

本 Review 只对 `reviewed_head: 963ff5e6f77f153de2a58153940c96c7569ef22c`（工具本体 + 定向测试）有效。
审查时仓库文档 head 为 `94067d20e`（Task `in_review` + Handoff + STATUS/Plan/Ledger），证据提交为
`2052b4619c0c17663271060d4e065284521a18b3`。`git diff 963ff5e6f..HEAD` 只新增文档与 `verification/`
证据，`tools/smoke/**` 与 `tests/tools/**` 在 `963ff5e6f` 与 `HEAD` 的 blob 完全相同，故本结论对当前文档
head 下的代码状态同样成立。Reviewer 非实现者，未修改实现/测试/文档，未执行 `git commit/push/reset/stash`。

## 范围与依据

- **需求来源**：`doc/tasks/TOOL-SOFTWARE-SMOKE-1.md` 的 AC1–AC7、允许/禁止范围，以及用户 2026-10-23
  「制作插件/软件检查工具替代手工 GUI 冒烟」授权（方案 D：Core 沙箱 + 真实 Core wire + 前端
  tsc/Vitest + 真实 core-sidecar bundle）。Task 未引用 D01–D08 条文，故 Spec 依据按 Task AC 原文。
- **审查对象**：`6e3ce06f9..963ff5e6f` 的 12 个新增文件（`tools/smoke/**` 2,262 行、`tests/tools/**` 160 行），
  证据提交 `2052b4619` 的 8 个文件，以及文档提交 `94067d20e` 的 Task/Handoff/指针文档。
- **受影响调用链**：工具 → 生产装配 `bootstrap.core_service.assemble_production_core`、`PluginService`、
  `AppContainerSandbox`、真实 `python -m bootstrap.core_service` 子进程、前端 `tsc`/Vitest、真实
  `apps/desktop/src-tauri/target/core-sidecar/core-sidecar/python/python.exe` 与
  `packaging/m2ac5/verify_bundled_python.ps1`。逐项核对了这些生产 API 的签名/语义与工具调用一致。
- **未审到/不在范围**：GUI 视觉与点击、安装包端到端、检测模型推理质量、真实用户数据根（Task 明确非目标）；
  AppContainer profile 的 OS 级生命周期只按 Task R4 记录，不作清理验证。全量 pytest 的 3 个既有失败不修，
  只核对「非本 Task 引入」的证据链。
- **限制**：本 Reviewer 只允许写本文件，复审重跑日志未另存入库；命令、环境、EXIT 与关键输出已逐项记入
  下方「验证」表。既有 canonical 日志的头部/跳过原因缺口记为 R-002。

## Standards（可选视角，executed）

按仓库记录标准逐条核对：`AGENTS.md`（只读工具、不得改生产代码/共享契约/依赖）、[09 协作协议](../09_COLLABORATION.md)
§4.1（canonical evidence pin）、§4.2（passed/skipped 分列与 skip 原因）、§4.3（v3 AC 标记）、§5/§5.1（Handoff、
下一任务建议）、§6.12（Q-009 证据纪律，EXIT + shell/venv 头、判别力 artefact）。硬性项：范围、pin、v3 标记
均满足；证据纪律存在格式缺口（R-002，P2）。Fowler baseline 判断项：`tools/smoke/checks/core.py:_write_plugin`
与 `tools/smoke/checks/wire.py:_write_plugin` 各有一份插件夹具写入逻辑，属 **possible Duplicated Code**；
两处夹具字段/用途不同（Core 含权限矩阵、Wire 只含两个插件），不构成硬性违规，不阻断。

## Spec（可选视角，executed）

- **AC1** 满足：一键入口、`--only/--skip/--list-checks/--json/--keep-artifacts/--repack`、JSON 字段与中文摘要、
  退出码 0/1/2 均实测（退出码边缘见 R-004）。
- **AC2** 满足：11 项 Core 检查在真实 AppContainer 上通过（生产装配接线、发现/拒绝、状态、Hook、FS/NET 拒绝、
  NET 放行、超时、进程树清理、fail-closed、审计）。
- **AC3** 满足：6 项 Wire 检查驱动真实 `bootstrap.core_service` 子进程，默认关闭、状态往返、三类 typed error、
  审计、`core.shutdown` exit 0。
- **AC4** 满足：`tsc --noEmit` 与全量 Vitest（45 files / 435 tests）PASS；node_modules/node 缺失时 BLOCKED 的
  分支已实现（未在本机触发）。
- **AC5** 满足：bundle 布局、最小 PATH 启动、frozen `_hook_interpreter()` 解析、AppContainer 内 bundle Hook、
  `--repack` 复用 `verify_bundled_python.ps1` 均通过（`--repack` 临时残留见 R-001）。
- **AC6**：定向 9 passed、全量 pytest 结果与声明一致且可判非本 Task 引入、两次全量幂等、`check.ps1` PASS；
  唯一偏差点是 `--repack` 残留与证据格式（R-001/R-002），故本 Review 批准但建议 Lead 在 closeout 前处置后再更新标记。
- **AC7** 满足：`src/**`、`apps/**`、既有 tests、依赖清单均未改；未使用 GUI/鼠标/截图；文档标注非目标。
- **无 scope creep**。STATUS 中 `GUI-PLUGIN-SANDBOX-SMOKE-1` 标签由 `paused` 修正为 `blocked` 与任务文件
  既有 `status: blocked` 一致，未改变其恢复/关闭决定，不计为越界。

## Findings

**在记录范围内未发现 P0/P1。** 以下 6 项均为 P2，均不阻断批准，记 `deferred` 由 Lead 在 closeout 前处置或登记遗留。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P2 | `tools/smoke/checks/packaged.py:236-270`；`packaging/m2ac5/verify_bundled_python.ps1:83,99-101`；`doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:130` | `--only packaged --repack` 复用脚本时，脚本内部 `tempfile.mkdtemp(prefix='nm-bundled-hook-')` 生成的临时插件目录不会被清理；每个 repack 运行在 `%TEMP%` 留一份合成插件 + `library.db`。AC1/AC6 “无残留临时插件” 的表述对 repack 路径不成立，Resource Manifest 的 temp 行只登记 `nm-software-smoke-*`，漏记该目录。 | 本机现存 `nm-bundled-hook-c6wrbkky`（2026-10-23 20:27:14，实现者证据 repack）、`-ckh407k4`（20:23:41）、`-hy31rb_q`（18:59:20）；复审者重跑 `--only packaged --repack`（20:41:49）也产生 `-oxbriv00`（已由复审者清理）。每个目录含 `library.db`、`plugins/acme-bundled/{manifest.json,plugin.py}`；默认全量运行无 `nm-software-smoke-*` 残留。 | 工具在 repack 前后清理本次新增的 `nm-bundled-hook-*`（或让脚本 OutDir 覆盖该临时根），并在 Resource Manifest 登记/清理现存目录；closeout 前删除这 3 个目录。 | deferred |
| R-002 | P2 | `verification/TOOL-SOFTWARE-SMOKE-1/run-1.log:1-9`、`pytest-tools.log:1-5`、`pytest-full.log:1`、`baseline-check.log:1-6`、`repack-run.log:1-9`；`doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:87-88` | 证据纪律（09 §6.12/Q-009、§4.2）缺口：① 入库日志只有 `# command`/`# started`/`# exit`，缺 shell 类型与解释器路径头；② 全量 pytest 的 9 个 skip 只记总数、未逐条给原因（日志未用 `-rs`）；③ `check.ps1` 的 PASS 只写在 Handoff 叙述中，无入库输出 artefact。影响可复核性（本 Reviewer 已独立重跑并补齐 skip 原因，见验证表，故不构成关键验证缺失）。 | `pytest-tools.log` 头两行即命令/时间，无解释器；`pytest-full.log` 末尾仅 `3 failed, 2681 passed, 9 skipped`，无 SKIPPED 行；Task:88 以 “Handoff” 为证据而 Handoff:52 只陈述 PASS。复审 `-rs` 重跑得到 9 条 skip 原因：docTR 未安装 ×2、openssl unavailable ×6、registry-readiness 的既有 guard ×1。 | 重新生成带 “shell/venv 头 + EXIT” 的日志（或在日志中追加环境头）；用 `-rs` 重跑或把 9 条原因写入 Task；把 `check.ps1` 输出入库并在 Task 引用。 | deferred |
| R-003 | P2 | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:51,83,85`；`doc/handoffs/TOOL-SOFTWARE-SMOKE-1-963ff5e6f.md:48` | Task/Handoff 的耗时数字与 canonical 证据不一致：文档写 `--repack` 10.4s、`tsc` 3.8s、Vitest 4.9s；`repack-report.json` 为 `duration_ms: 7567`（packaged 层 7423）、`smoke-report.json` 为 tsc 2744ms、Vitest 4599ms（`repack-run.log` 总 7.6s / 打包层 7.4s）。数字无法追溯到入库 artefact，属文档准确性问题（不改变 PASS 结论）。 | `repack-report.json:5,60`；`smoke-report.json:284-300`；`repack-run.log:3,7`；对照 Task:51/83/85、Handoff:48。 | 将文档数字改为与 canonical 证据一致，或注明是更早的 ad-hoc 运行；closeout 时保持 Task/Handoff/证据同口径。 | deferred |
| R-004 | P2 | `tools/smoke/plugins.py:186`（`report.write_json` 在 try/finally 之外）、`:77,138`（`--verbose` 只解析未使用）、`checks/packaged.py:79-82`（`finally: pass` 死代码） | 退出码契约的边缘与无效果选项：① 报告写入失败（如 `--json .gitignore/x.json`，父路径是文件）抛 `FileExistsError` traceback，进程 EXIT=1，而 AC1 规定工具自身错误为 2；② 全部层被显式 `--skip` 时输出 `status=SKIP`、0 项检查、EXIT=0，CI 可能把 “什么都没跑” 读成通过；③ `--verbose` 无任何效果。 | 本机执行 `python -m tools.smoke.plugins --only wire --json .gitignore/x.json` → 末行 `FileExistsError`、EXIT=1；`python -m tools.smoke.plugins --skip core,wire,frontend,packaged` → `SKIP（4 层，0 项检查）`、EXIT=0；`grep verbose` 仅见解析与赋值。 | 把报告写入包进 `try/except OSError` 返回 2（并打印中文错误）；0 检查时至少输出警告并按需要返回非 0；实现或删除 `--verbose`；移除死代码。 | deferred |
| R-005 | P2 | `tools/smoke/checks/core.py:205-224`、`:351-367`；`tools/smoke/checks/packaged.py:172-233`；`tools/smoke/checks/frontend.py:113-135` | 弱断言/潜在误报 PASS 路径：① `CORE-NET-ALLOW` 只要求非 `PermissionError`，本次证据 detail 是 `{"net":"BLOCKED","kind":"TimeoutError"}`，只证明 capability 未被拒绝（Task R2 已声明，但 “被放行” 的语义弱于 AC2 字面）；② `PACKAGED-SANDBOX-HOOK` 只断言 Hook 返回 `{"bundled": true}`，未证明实际执行解释器就是 bundle `python.exe`；若生产回归为忽略 `_hook_interpreter()`，该检查仍可能 PASS；③ `CORE-PRODUCTION-WIRING` 未断言生产 `PluginService._allow_unsandboxed is False`（生产装配 `src/bootstrap/core_assembly.py:1213-1222` 确为 False，但回归不会被该检查发现）；④ `FRONTEND-VITEST` 只要求解析出 “Tests >0 passed”，大量删除前端测试仍会 PASS。 | `smoke-report.json:114-124`（NET-ALLOW detail）、`:351-364`（packaged hook detail 只有固定字符串 `interpreter=bundle python.exe`，没有实际路径断言）；`core_assembly.py:1213-1222`；`frontend.py:113-135`；生产 `run_hook` 走 `_hook_interpreter()` 的代码见 `src/infrastructure/plugins/service.py:405`。 | 让 packaged Hook 夹具返回 `sys.executable` 并断言等于 bundle 解释器路径；把 `_allow_unsandboxed is False` 加入 CORE-PRODUCTION-WIRING；Vitest 记录 tests/files 并与基线/仓库测试文件数对照（允许显式更新）；NET-ALLOW 至少把 “TimeoutError” 与 “真正放行” 分开报告。 | deferred |
| R-006 | P2 | `tests/tools/test_software_smoke.py:28-160` | 定向测试只覆盖 `model`/`report`/CLI 选择逻辑（9 cases），四个层的失败/BLOCKED 分支（如 `FRONTEND-DEPS-MISSING`、`PACKAGED-BUNDLE-MISSING`、`CORE-SETUP-FAILED`、`WIRE-SETUP-FAILED`、`EXPECTED_REPACK_DISABLED`）没有定向测试；这些错误码只能由代码审查背书，未来改动可能静默回归。 | 9 个测试名与断言均集中在状态推导/报告/CLI；`all_blocked` 只测了通用函数，未调用任何层 `run()` 的 BLOCKED 路径（测试仅用 model 层手工构造的 BLOCKED `LayerResult`）。 | 用 monkeypatch/临时目录为各层 `run()` 的缺依赖分支补测试，并断言退出码 1；可放入 `tests/tools/`，不扩大 Task 范围。 | deferred |

## 验证

**环境**：Windows（`win32`）/ Python 3.14.6（`C:\Python314\python.exe`）/ Node v24.15.0（`E:\Program Files\nodejs\node.exe`）/ PowerShell 7.6.6 / 仓库 `G:/CODEX/New Manga`，branch `main`，文档 head `94067d20e`，被审代码 head `963ff5e6f`（两者 `tools/smoke`、`tests/tools` blob 相同）。重跑日志临时位于 `%TEMP%`、未入库（本角色只能写本文件）；下表记录命令、EXIT 与关键输出。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| AC1 全量四层 | `python -m tools.smoke.plugins --json %TEMP%\nm-review-smoke.json` | 本机环境；代码 `963ff5e6f`（= HEAD blob） | **PASS**：4 层 / 24 项（23 PASS + 1 SKIP 仅因未传 `--repack`），EXIT=0，23.7s（canonical 23.3s）。JSON：`schema=nm-software-smoke/1`、`status=PASS`、`summary={layers:4,checks:24,passed:23,failed:0,skipped:1,blocked:0}`、`environment={platform:win32,python:3.14.6,repack:false,screenshots:disabled,gui:not_used,mouse:not_used}`，JSON 内无主机绝对路径。 | 本次复审重跑；canonical `verification/TOOL-SOFTWARE-SMOKE-1/smoke-report.json`（`2052b4619`，sha256 `c3ce68ce…f17dfd` 与工作区一致） |
| AC1 分层抽测 | `--only core`；`--only wire`；`--only frontend`；`--only packaged`（各自 `--json %TEMP%\nm-review-<layer>.json`） | 同上 | 全部 **EXIT=0**：core 11/11 PASS 14.7s；wire 6/6 PASS 0.5s；frontend 2/2 PASS 7.2s；packaged 4 PASS + 1 SKIP 0.5s。每份 JSON 均 `schema=nm-software-smoke/1`、`status=PASS`，运行层 `layer_status=PASS`，未运行层为 `SKIP` 且带 `skip_reason`。 | 本次复审重跑；canonical `smoke-report.json` 的逐层 `layers[].checks[]` 与之同构 |
| AC1 退出码与选项 | `--list-checks`；`--only nope`；`--only ''`；`--skip frontend,packaged`；`--json -`；`--keep-artifacts` | 同上 | `--list-checks`：24 行、EXIT=0；未知/空层列表：中文用法错误、**EXIT=2**；`--skip`：17 项、未选层 SKIP、EXIT=0；`--json -`：stdout 为可解析 JSON（`status=PASS`）、摘要走 stderr、EXIT=0；`--keep-artifacts`：输出临时目录且存在，复审者随后删除。 | 本次复审重跑；`plugins.py:81-103,122-195` |
| AC1 退出码边缘 | `--only wire --json .gitignore/x.json`；`--skip core,wire,frontend,packaged` | 同上 | **边缘 FAIL（不阻断，见 R-004）**：报告写入失败抛 `FileExistsError` traceback、**EXIT=1**，而 AC1 规定工具自身错误为 2；全层显式 skip 为 `status=SKIP`、0 项检查、EXIT=0。 | 本次复审重跑；`plugins.py:186` |
| AC2 Core 沙箱层 | 全量运行中的 core 层（11 项） | 真实 AppContainer；临时数据根；`963ff5e6f` | **PASS**（本次 11/11，14.7s；canonical 15.0s）。关键 detail：`sandbox=AppContainerSandbox`、`shared_profile=false`；FS 根外读 `BLOCKED`；无权限网络 `PermissionError`；超时 `PLUGIN_HOOK_TIMEOUT`、`elapsed_ms≈2.3s`；孙进程 pid 在超时后 `wait_pid_gone` 为真；fail-closed `PLUGIN_HOOK_UNAVAILABLE`；审计 82 事件且无秘密/载荷。 | canonical `smoke-report.json:29-181`；本次复审重跑；生产 API 核对：`src/infrastructure/plugins/service.py:132-153,405-414`、`src/infrastructure/plugins/sandbox.py:204-368`、`src/bootstrap/core_assembly.py:1213-1222` |
| AC3 Wire 层 | 全量运行中的 wire 层（6 项），真实 `python -m bootstrap.core_service` 子进程 | `963ff5e6f`；临时数据根 | **PASS**（6/6，0.5s）：`core.ping` 返回 `protocol_version {major:2, minor:3}`；`plugins.list` 默认 `global_enabled=false`、拒绝原因 `PLUGIN_PERMISSIONS_UNSUPPORTED`；`PLUGIN_NOT_LOADED`/`PLUGIN_NOT_FOUND`/`PLUGIN_INVALID_REQUEST` 与 `category=validation/not_found`、`retryable=false` 均命中；审计含 `load_ok/load_rejected/enabled`；`core.shutdown` 结果 `{status:stopped}`、进程 exit 0，运行后无 `core_service` 残留进程。 | canonical `smoke-report.json:183-271`；本次复审重跑；`tools/smoke/checks/wire.py`；生产 `core_service.py:204-291,4042-4046` |
| AC4 前端层 | 全量运行中的 frontend 层；另 `--only frontend` | 真实 `apps/desktop/frontend/node_modules`；Node 24.15.0 | **PASS**：`tsc --noEmit` PASS（本次 2.7s；canonical 2744ms），Vitest 45 files / **435 tests passed**（本次 4.6s；canonical 4599ms）。 | canonical `smoke-report.json:272-302`；本次复审重跑；`tools/smoke/checks/frontend.py:45-146` |
| AC5 打包层 | 全量运行中的 packaged 层；`python -m tools.smoke.plugins --only packaged --repack --json %TEMP%\nm-review-repack.json` | 真实 core-sidecar bundle：`.../core-sidecar/core-sidecar/python/python.exe` 存在；`core_service.exe` 存在 | **PASS**：默认 4 PASS + 1 SKIP（`EXPECTED_REPACK_DISABLED`）；`--repack` 5/5 PASS、EXIT=0、8.1s（packaged 层 7.9s；canonical 7.6s/7.4s），repack detail 为 `script=packaging/m2ac5/verify_bundled_python.ps1, exit=0`。见 R-001 的残留。 | canonical `repack-report.json`、`repack-run.log`（sha 与表一致）；本次复审重跑 |
| AC5 frozen 解析判别力 | 按 `PACKAGED-FROZEN-RESOLVE` 同一逻辑独立运行两次：期望 bundle 解释器（正控）与期望 `C:\Python314\python.exe`（负控） | `src/**` 只读；`sys.frozen=True`、`sys.executable=<bundle>/core_service.exe` | 正控：`resolved=...\core-sidecar\python\python.exe`、`frozen-resolution-ok`、EXIT=0；负控：`AssertionError`、**EXIT=1**。证明该断言不是恒真，且 `_hook_interpreter()` 在模拟 frozen 下确解析到 bundle。 | 本次复审重跑（脚本在 `%TEMP%`，已删）；生产 `service.py:88-129`；canonical `smoke-report.json:339-349` |
| AC6 定向测试 | `python -m pytest tests/tools -q` | Python 3.14.6；`963ff5e6f` | **PASS：9 passed in 1.65s，EXIT=0**（canonical 9 passed in 1.63s）。 | 本次复审重跑；canonical `pytest-tools.log`（sha `b8e377dd…`） |
| AC6 全量回归 | `python -m pytest tests -q` | Python 3.14.6；`transformers 4.48.3`（`hasattr(...,'RTDetrV2ForObjectDetection')=False`）；`963ff5e6f`/HEAD | **PASS（与声明一致；命令 EXIT=1 系 3 个既有失败）**：`3 failed, 2681 passed, 9 skipped, 2 warnings in 231.05s`。失败仍是同一 3 例：`test_detection_manga_real.py` 两例（transformers 缺 `RTDetrV2ForObjectDetection`）、`test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately`（PySide6 超时）。`-rs` 重跑：`3 failed, 2681 passed, 9 skipped in 233.35s`，9 条 skip 原因：docTR 未安装 ×2、openssl unavailable ×6、registry-readiness 既有 guard ×1。**非本 Task 引入的依据**：`git diff --stat 6e3ce06f9..HEAD -- src apps tests` 仅 `A tests/tools/test_software_smoke.py`（160 行），`src/**`、`apps/**` 与既有 tests 零改动；失败在既有环境/历史测试。 | 本次复审重跑（`%TEMP%\nm-review-pytest-full.log`、`nm-review-pytest-skips.log`，未入库）；canonical `pytest-full.log`（sha `3fc2c41a…`）、`baseline-check.log`（sha `b447f67b…`） |
| AC6 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根，`in_review`；PowerShell 7.6.6 | **PASS (2 warnings)，EXIT=0**。警告解释：① “3 个非终态 Task” = `GUI-PLUGIN-SANDBOX-SMOKE-1(blocked)`、`V1-RELEASE-SIGNING-1(in_review)`、本 Task `in_review`，属评审期正常状态；② `REBASELINE_PLAN` 6262 bytes / 58 lines（80% 预算，base 为 4499 bytes），由本 Task 注册行增加所致，仅为预算 soft warning，不影响 PASS。 | 本次复审重跑输出；`tools/governance/check.ps1` |
| Canonical Evidence 表 | 逐文件 `Get-FileHash -Algorithm SHA256`；`git ls-tree -r 2052b4619 -- verification/TOOL-SOFTWARE-SMOKE-1`；`git diff 2052b4619..HEAD -- verification/TOOL-SOFTWARE-SMOKE-1` | `2052b4619`；工作区 | **8/8 通过**：8 个路径都存在且都被 `2052b4619` 包含；SHA-256 全部与 Task 表一致（如 `smoke-report.json c3ce68ce…`、`run-1 42b3df32…`、`pytest-full 3fc2c41a…`）；evidence_dir 共 8 个文件、无未登记文件；`2052b4619..HEAD` 对该目录 diff 为空。 | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:112-123`；本次复审命令输出 |
| 范围证明 | `git diff --stat 6e3ce06f9..HEAD -- src apps tests`；`git diff --name-status 6e3ce06f9..HEAD` | `6e3ce06f9..HEAD` | `src/**`、`apps/**` 无改动；`tests` 仅新增 `tests/tools/test_software_smoke.py`；完整 diff 只落在 allowed_paths（`tools/smoke/**`、`tests/tools/**`、`verification/TOOL-SOFTWARE-SMOKE-1/**`、Task/Handoff/STATUS/Plan/Ledger）；无 `pyproject.toml`/`package.json`/契约文件改动。 | 本次复审命令输出；`git log --oneline` |
| 边界（无 GUI/鼠标/截图） | 静态检查 `tools/smoke/**` 是否引用 GUI/鼠标/截图库；读取报告 `environment`；核对子进程命令 | `963ff5e6f` | 无 PySide6/pyautogui/screenshot/uiautomation 等引用（仅注释与 JSON 元数据）；所有子进程为 python/node/pwsh；报告声明 `gui=not_used`、`mouse=not_used`、`screenshots=disabled`。 | `grep`/Select-String 输出；`report.py:71-78`；本次重跑的 JSON |
| 幂等、仓库与临时清理 | 连续全量运行（canonical run-1/run-2 + 本次重跑）；运行前后 `git status`、`%TEMP%\nm-software-smoke-*`、python 进程 | 同上 | 两次全量均 PASS 且 `git status` 仅剩审查前已存在的 6 个未跟踪 `verification/P04/*.jsonl`（与本 Task 无关，未触碰）；`nm-software-smoke-*` 运行前后均为 0；无 `core_service` 残留进程。另有 3 个 `_hook_runner` 进程于 18:15–18:17 启动（早于本 Task 交付，来自既有 pytest 夹具），非本工具产生；`--repack` 的 `nm-bundled-hook-*` 残留见 R-001。 | 本次复审命令输出；canonical `run-1.log`/`run-2.log`；`doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:130` |
| Resource Manifest 可执行性 | 执行 Manifest temp 行的检查命令；核对 worktree/agent-output 行 | 同上 | temp 行 `Get-ChildItem $env:TEMP -Directory -Filter nm-software-smoke-*` 无结果（与 Manifest 一致）；worktree 为 NOT_APPLICABLE（主 worktree）；无 agent-output 资源。**但 Manifest 未覆盖 R-001 的 repack 残留**。 | 本次复审命令输出；`doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:125-131` |

## Architecture 与 Verification 两面结论

**Architecture（PASS）**：新增代码全部位于 `tools/smoke/**`，是只读检查工具，不进入生产依赖方向；复用生产装配/
沙箱/服务与真实 bundle，不复制第二套生产实现，符合「用真实 seam 守契约」的设计意图。缺依赖/非 Windows/
bundle 缺失时统一 `BLOCKED` 而非 PASS，`run_checks` 把未知异常转成 `FAIL(UNEXPECTED_CHECK_ERROR)`，无静默通过路径；
默认无 GUI/鼠标/截图，数据根与临时插件隔离在 `%TEMP%`，AppContainer profile 的 OS 级复用已在 R4 声明。
残留风险：工具依赖生产私有成员（`PluginService._sandbox`、`_hook_interpreter` monkeypatch、构造 kwargs）与
wire 协议字面量 `2.3`，生产内部重构会让工具显式 FAIL 或需要同步更新，不会静默 PASS；可接受，但建议在工具头注释
声明这些耦合点。没有发现分层/契约/安全/持久化方面的架构阻断项。

**Verification（PASS，附 P2）**：本 Review 实际重跑了任务要求的全部 8 组验证（全量四层、逐层抽测、repack、
定向 pytest、全量 pytest、check.ps1、canonical pin、范围证明），结果与 Task/Handoff 声明一致：
全量 PASS/exit 0；`--repack` PASS/exit 0；`tests/tools` 9 passed；全量 pytest 3 failed/2681 passed/9 skipped
且失败可判非本 Task 引入；`check.ps1` PASS（2 条可解释 warning）；8 个 canonical 证据 pin 全部匹配且无未登记
文件；`src/**`、`apps/**` 与既有 tests 零改动。发现的 6 个 P2（repack 残留、证据格式、数字口径、退出码边缘、
弱断言/潜在误报、定向测试覆盖）均不影响上述关键结论，不构成 P0/P1，也不构成关键验证缺失。

## 结论与复审

- **Decision：approved**。固定 `reviewed_head=963ff5e6f77f153de2a58153940c96c7569ef22c` 可交 Codex 集成；
  文档 head `94067d20e` 仅含 Task/Handoff/指针与证据，不改变被审代码。
- **closeout 前建议 Lead 处置（不阻断集成）**：① 清理并登记 R-001 的 3 个 `%TEMP%\nm-bundled-hook-*` 残留，
  同时修正 Resource Manifest / AC 措辞（或让工具自动清理）；② 按 R-002 补齐证据头的 shell/venv 与 9 条 skip 原因、
  把 `check.ps1` 输出入库；③ 按 R-003 统一 Task/Handoff 与 canonical 证据的耗时数字；④ R-004/R-005/R-006 作为
  deferred 建议登记，后续工具 Task 处理；⑤ 处理完成后把 AC6 的 `<<PARTIAL>>` 按实际证据更新（本次 Review 已核实
  AC6 的测试/幂等/治理部分）。
- **剩余风险**：AppContainer 依赖本机非受限账户与 OS 版本；全量 pytest 的 3 个既有失败仍留待独立环境/历史测试
  Task； `--repack` 路径残留已列 R-001。上述风险不改变本 Review 对 `963ff5e6f` 代码与当前证据的批准。
- **复审规则**：若后续产生新的代码 head（`tools/smoke/**`、`tests/tools/**` 变化），本批准自动失效，需对新 head
  复审；仅文档/证据的收尾提交由 Codex 在集成记录中说明其不改变被审代码事实。本文件保持未提交状态，由 Lead 提交。

