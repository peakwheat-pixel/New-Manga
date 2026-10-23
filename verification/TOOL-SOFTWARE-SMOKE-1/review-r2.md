---
task_id: TOOL-SOFTWARE-SMOKE-1
reviewer: reviewer-tool-smoke
author: dsh
base_commit: 6e3ce06f96bb48bc7a8de0a114c8391a9bc82014
reviewed_head: c680434eab1ff6abcc4bc204e844ecba0c41979a
decision: approved
---

# Review r2：TOOL-SOFTWARE-SMOKE-1

本 Review 绑定新代码 head `reviewed_head: c680434eab1ff6abcc4bc204e844ecba0c41979a`（review-r1 的
`963ff5e6f` 修复提交），审查时仓库文档 head 为 `6df1fc355efd2b314667af07a8bca0dc8d712064`，证据提交为
`7b2abfa00`（`governance-check.log` 随文档提交 `6df1fc355` 入库）。`review-r1.md` 保持为旧 head 的历史 Review，
不因本 r2 改写。Reviewer 非实现者；本文件之外未修改 Task/Handoff/STATUS/Plan/tools/tests，未执行 git 写操作。
`git diff c680434ea..HEAD -- tools/smoke tests/tools` 为空（文档/证据提交不改变被审代码），故本结论对当前文档
head 下的代码状态同样成立。

## 范围与依据

- **复审范围**：`963ff5e6f..c680434ea` 的修复 diff（5 个文件：`tools/smoke/plugins.py`、`tools/smoke/model.py`、
  `tools/smoke/checks/core.py`、`tools/smoke/checks/packaged.py`、`tests/tools/test_software_smoke.py`），
  修复后证据提交 `7b2abfa00`（9 个文件，含 `review-r1.md`），文档提交 `6df1fc355`（Task/Handoff/STATUS/
  Plan/Ledger + `governance-check.log`）。
- **需求来源**：Task AC1–AC7 与 r1 的 R-001…R-006 disposition；无新增产品需求，无契约/依赖变更。
- **受影响调用链复核**：`PACKAGED-REPACK-VERIFY` 的临时目录快照/清理、`PluginService` 生产装配标志断言、
  `PACKAGED-SANDBOX-HOOK` 对实际执行解释器的断言、CLI 退出码与报告写入路径。生产 API 语义与 r1 相同
  （`assemble_production_core`、`AppContainerSandbox`、`PluginService`、`bootstrap.core_service`），本 r2 未改
  `src/**`/`apps/**`。
- **未审到/不在范围**：GUI 视觉/点击、安装包端到端、模型推理质量、真实用户数据根（Task 非目标）；
  AppContainer OS profile 生命周期仍按 Task R4 声明；全量 pytest 的 3 个既有失败不修。
- **限制**：本 Reviewer 仅能写本文件，复审重跑日志未入库；命令、环境、EXIT 与关键输出见「验证」表。

## Standards（可选视角，executed）

仓库记录标准核对：`AGENTS.md`（工具不得改生产代码/共享契约/依赖）、09 §4.1（canonical evidence pin）、§4.2
（passed/skipped 分列、skip 原因）、§4.3（v3 AC 标记）、§5/§5.1（Handoff 与下一任务建议）、§6.12（Q-009：
EXIT + shell/venv 头、判别力 artefact）。硬性项：范围、v3 标记、Handoff 均满足；证据面已明显改善
（日志头、`-rs` skip 原因、`governance-check.log` 入库），但 **`governance-check.log` 未列入 Canonical Evidence，
`check.ps1` 自身对其报 WARN**（R-007，P2，见 Findings）。Fowler baseline 判断项：`core.py` 与 `wire.py` 各有一份
插件夹具 `_write_plugin`（possible Duplicated Code，r1 已记录，本 r2 未扩大、不阻断）。

## Spec（可选视角，executed）

- **AC1**：入口/选项/JSON/中文摘要/退出码满足；新增 `--json` 写入失败与全层显式 `--skip` 均返回 2（本次实测）。
- **AC2**：11 项 Core 检查 PASS；`_allow_unsandboxed is False` 现由 `CORE-PRODUCTION-WIRING` 断言。
- **AC3**：6 项 Wire 检查 PASS（真实 `bootstrap.core_service` 子进程、typed errors、shutdown exit 0）。
- **AC4**：`tsc --noEmit` + 435 Vitest tests PASS；本次 canonical 为 tsc 2.8s / Vitest 4.6s。
- **AC5**：bundle 布局/最小 PATH/frozen 解析/AppContainer Hook/`--repack` 全 PASS；Hook 现断言实际
  `sys.executable` 等于 bundle 解释器（canonical `executable_verified=true`）；repack 清理 1 个临时插件目录。
- **AC6**：两次全量 PASS/幂等、定向 15 passed、全量 2687 passed/9 skipped/3 failed（失败可判非本 Task 引入）、
  `check.ps1` PASS、独立 Review r2 = 本文件；仅剩 R-007（pin）与 R-008（0.1s 口径）两项 P2。
- **AC7**：`src/**`、`apps/**`、既有 tests、依赖清单零改动；无 GUI/鼠标/截图；非目标已记录。
- **无 scope creep**；修复范围落在既有 allowed_paths。

## Findings

**在记录范围内未发现 P0/P1。** r1 的 R-001…R-006 处置核对如下；新增 R-007/R-008 两项 P2。

### r1 findings disposition

| ID | 原级别 | r1 问题 | r2 处置 | 独立验证 |
|---|---|---|---|---|
| R-001 | P2 | `--repack` 遗留 `%TEMP%/nm-bundled-hook-*` 临时插件 | **fixed** | `packaged.py:258-300` 增加运行前后快照/只删本次新增；本次重跑 `before=0 → after=0`、detail `temp_plugin_dirs_cleaned=1`；评审前 3 个遗留目录已不存在（计数 0） |
| R-002 | P2 | 证据日志缺 shell/venv 头；9 个 skip 无原因；`check.ps1` 无 artefact | **fixed** | `run-1/run-2/repack-run/pytest-tools/pytest-full/baseline` 均含 `# shell`/`# python`/`# cwd`/`# started`/`# exit`；`pytest-full.log` 用 `-q -rs` 逐条列出 9 个 SKIPPED；`governance-check.log` 已入库（pin 缺口见 R-007） |
| R-003 | P2 | Task/Handoff 耗时与证据不一致 | **fixed（残留 0.1s 口径见 R-008）** | 24.0s/Core 15.5s/前端 7.5s（tsc 2.8s、Vitest 4.6s）/repack 7.4s/15 passed/2687 passed 均与 evidence 一致；仅 run-2 23.6s 一项不符 |
| R-004 | P2 | `--json` 写入失败 exit 1；全层 skip exit 0；`--verbose` 无效 | **fixed** | 实测：`.gitignore/x.json` → 中文错误 + **EXIT=2**；全层 `--skip` → 中文错误 + **EXIT=2**；`--verbose` → argparse `unrecognized arguments` + EXIT=2；正常 skip/`--json -` 仍为 0 |
| R-005 | P2 | 弱断言/潜在误报 | **partial / deferred（按声明保留）** | `packaged.py:182,230-241` 断言实际 `sys.executable == bundle python`（canonical `executable_verified=true`）；`core.py:215` 断言 `_allow_unsandboxed is False`；`CORE-NET-ALLOW` 非 PermissionError 语义与前端测试数下限按 Handoff R-005/Task R2 声明 deferred |
| R-006 | P2 | 层失败/BLOCKED 分支无定向测试 | **fixed** | `tests/tools` 由 9 → 15 passed；新增 frontend/node、packaged/bundle、core setup、wire spawn、JSON 写失败、全层 skip 6 个分支测试（`test_software_smoke.py:168-219`），本次重跑 15 passed |

### 新增 findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-007 | P2 | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:113-125`（Canonical Evidence 仅 9 行）；`verification/TOOL-SOFTWARE-SMOKE-1/governance-check.log`（HEAD/`6df1fc355`，SHA-256 `76804a4d…`） | `governance-check.log` 已入库并在 Task 测试表（:88）与 Handoff（:53）引用，但未列入 Canonical Evidence；evidence_dir 共 10 个文件、pin 仅 9 条，`check.ps1` 明确 `WARN: evidence_dir 含未登记过程文件`（见已入库日志第 10 行）。影响：AC6 的治理 Gate 证据未按 §4.1 pin；`canonical_evidence_status` 无法按完整口径置 `complete`。 | 本次重跑 `check.ps1` 同样出现该 WARN（PASS, 4 warnings）；`git ls-tree -r HEAD -- verification/TOOL-SOFTWARE-SMOKE-1` 列出 10 个文件而 Task 表 9 条；`governance-check.log` 仅在 `6df1fc355` 新增。 | 二选一：① 增加 `EV-GOVERNANCE-CHECK` 行（commit `6df1fc355`，sha256 `76804a4d…`，class CANONICAL）；② 若按过程文件归入 workspace，则移动文件并同步修改 Task/Handoff 引用，不能保留未登记状态。closeout 前必须闭环；本 `review-r2.md` 提交后同样应按 `review-r1` 的方式登记或由 Codex 说明其 pin 处置。 | open（deferred，closeout 前修） |
| R-008 | P2 | `doc/tasks/TOOL-SOFTWARE-SMOKE-1.md:84`；`doc/handoffs/TOOL-SOFTWARE-SMOKE-1-c680434ea.md:50` | 幂等行写“24.0s / 23.6s”，但 canonical `run-2.log` 第 6 行是“23.5s”；其余数字均与证据一致。属 R-003 的残留文档口径问题（不影响任何 PASS 结论）。 | `run-2.log:6` = `... 24 项检查，23.5s`；Task:84/Handoff:50 = `23.6s`；`run-1.log`/`smoke-report.json` 的 24.0s 无争议。 | 把两处 23.6s 改为 23.5s（或注明取整/另一次运行），closeout 前与 canonical 证据同口径。 | open（deferred，closeout 前修） |

## 验证

**环境**：Windows（`win32`）/ Python 3.14.6（`C:\Python314\python.exe`）/ Node v24.15.0 / PowerShell 7.6.6 /
仓库 `G:/CODEX/New Manga`，branch `main`，文档 head `6df1fc355`，被审代码 head `c680434ea`
（两者 `tools/smoke`、`tests/tools` blob 相同）。重跑日志位于 `%TEMP%`、未入库（本角色只能写本文件）；
下表记录命令、EXIT 与关键输出。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| AC1–AC5 全量四层 | `python -m tools.smoke.plugins --json %TEMP%\nm-r2-full.json` | 本机环境；`c680434ea` | **PASS，EXIT=0**：4 层/24 项（23 PASS + 1 SKIP 为未传 `--repack`），23.7s（canonical 24.0s）。JSON `schema=nm-software-smoke/1`、`status=PASS`、`summary={layers:4,checks:24,passed:23,failed:0,skipped:1,blocked:0}`；`PACKAGED-SANDBOX-HOOK.detail.executable_verified=true`；无主机绝对路径。 | 本次重跑；canonical `smoke-report.json`（Task pin `19a2ab92…`） |
| AC5 `--repack` + 残留 | `python -m tools.smoke.plugins --only packaged --repack --json %TEMP%\nm-r2-repack.json`；运行前后 `Get-ChildItem %TEMP% -Directory -Filter nm-bundled-hook-*` | 真实 bundle；`c680434ea` | **PASS，EXIT=0**：packaged 5/5（本次层 7.4s/总 7.5s；canonical 层 7.3s/总 7.4s）；`PACKAGED-REPACK-VERIFY.detail={script, exit:0, temp_plugin_dirs_cleaned:1}`；`nm-bundled-hook-*` **0 → 0**，`nm-software-smoke-*` 0。 | 本次重跑；canonical `repack-report.json`（Task pin `5d0deb8a…`）、`repack-run.log`（`800822de…`） |
| AC1 退出码边缘 | `--only wire --json .gitignore/x.json`；`--skip core,wire,frontend,packaged`；`--only nope`；`--verbose`；`--only wire --json -`；`--skip frontend,packaged` | 同上 | `--json` 写失败：中文错误、**EXIT=2**（无 traceback）；全层 skip：中文错误、**EXIT=2**；未知层：**EXIT=2**；`--verbose`：`unrecognized arguments`、**EXIT=2**；`--json -`：可解析 JSON、**EXIT=0**；正常 `--skip`：**EXIT=0**。 | 本次重跑；`plugins.py:175-196` |
| AC2 Core 沙箱 | 全量运行中的 core 层（11 项） | 真实 AppContainer；临时数据根 | **PASS**（本次 11/11，15.2s；canonical 15.5s）：生产装配 `AppContainerSandbox`、`shared_profile=false`，`_allow_unsandboxed` 断言通过；FS 根外读 BLOCKED；无权限网络 PermissionError；超时 `PLUGIN_HOOK_TIMEOUT`；孙进程清理；fail-closed `PLUGIN_HOOK_UNAVAILABLE`；审计 82 事件。 | 本次重跑；canonical `smoke-report.json:29-181`；`core.py:215` |
| AC3 Wire | 全量运行中的 wire 层（6 项），真实 `bootstrap.core_service` 子进程 | 临时数据根 | **PASS**（6/6，0.5s）：`core.ping` 2.3；`plugins.list` 默认关闭/拒绝语义；`PLUGIN_NOT_LOADED`/`PLUGIN_NOT_FOUND`/`PLUGIN_INVALID_REQUEST`；`core.shutdown` exit 0；无 `core_service` 残留进程。 | 本次重跑；canonical `smoke-report.json:183-271` |
| AC4 前端 | 全量运行中的 frontend 层 | 真实 `node_modules`；Node 24.15.0 | **PASS**：`tsc --noEmit` 2.8s + Vitest 45 files/435 tests 4.6s（canonical 2825ms/4648ms）。 | 本次重跑；canonical `smoke-report.json:272-302` |
| AC5 打包层 | 全量运行中的 packaged 层（含默认 SKIP repack） | 真实 `core-sidecar` bundle | **PASS**：布局/最小 PATH/frozen 解析/AppContainer Hook 4 项 PASS + `EXPECTED_REPACK_DISABLED` SKIP；Hook detail `executable_verified=true`。 | canonical `smoke-report.json:304-375`；本次重跑 |
| AC6 定向测试 | `python -m pytest tests/tools -q` | Python 3.14.6 | **PASS：15 passed in 2.22s，EXIT=0**（canonical 15 passed 2.14s）。 | 本次重跑；canonical `pytest-tools.log`（`cba3576b…`） |
| AC6 全量回归 | `python -m pytest tests -q -rs` | Python 3.14.6；`transformers 4.48.3` | **与声明一致**：`3 failed, 2687 passed, 9 skipped, 2 warnings in 235.45s`，**EXIT=1**；失败仍是既有 2×transformers 缺 `RTDetrV2ForObjectDetection` + 1×PySide6 超时；`-rs` 9 条 skip 原因（docTR ×2、openssl ×6、registry-readiness guard ×1）与 canonical 完全一致（canonical 233.94s）。`git diff --stat 6e3ce06f9..HEAD -- src apps` 为空、`-- tests` 仅新增 `tests/tools/test_software_smoke.py`（219 行），可判非本 Task 引入。 | 本次重跑（`%TEMP%\nm-r2-pytest-full.log`）；canonical `pytest-full.log`（`0097a835…`）、`baseline-check.log`（`7ca4398d…`） |
| AC6 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根，`in_review`；PowerShell 7.6.6 | **PASS (4 warnings)，EXIT=0**。警告：① 3 个非终态 Task（GUI blocked、V1 in_review、本 Task in_review，评审期正常）；② `STATUS` 2560 bytes/30 lines 达 80% 预算（本 Task 状态行所致，soft）；③ `REBASELINE_PLAN` 6265 bytes/58 lines 达 80%（Task 注册行所致，soft）；④ **`evidence_dir` 含未登记过程文件 `governance-check.log`（R-007）**。 | 本次重跑输出；canonical `governance-check.log:5-12`（同样 4 warnings、EXIT=0） |
| Canonical Evidence 复核 | 逐文件 `Get-FileHash`；`git ls-tree -r 7b2abfa00/HEAD -- verification/TOOL-SOFTWARE-SMOKE-1`；`git log -- <file>` | `7b2abfa00`；`6df1fc355` | **9 条 pin 全部路径/commit/SHA 一致**：8 个旧 pin + `review-r1.md` 均在 `7b2abfa00`（如 smoke `19a2ab92…`、run-1 `79f4ec18…`、pytest-full `0097a835…`、review-r1 `d11918f0…`）；**`governance-check.log` 未登记**（存在、SHA `76804a4d…`、仅在 `6df1fc355`），evidence_dir 10 文件 vs 9 pin → R-007。 | 本次命令输出；Task:113-125 |
| 范围证明 | `git diff --stat 6e3ce06f9..HEAD -- src apps`；`-- tests`；`git diff --cached`/`--name-only`；`git diff c680434ea..HEAD -- tools/smoke tests/tools` | `6e3ce06f9..HEAD` | `src/**`、`apps/**` 零改动；tests 仅新增 `tests/tools/test_software_smoke.py`（219 行）；完整 diff 只落在 allowed_paths；`c680434ea..HEAD` 对 `tools/smoke`、`tests/tools` 为空（HEAD 之后只加文档/证据）；无依赖/契约文件改动。 | 本次命令输出 |
| Handoff/文档同口径 | 对照 Task:50-51/83-88、Handoff:43-54 与 `smoke-report.json`、`repack-report.json`、`run-1.log`、`run-2.log`、`pytest-tools.log`、`pytest-full.log` | `6df1fc355`/`c680434ea` | 除 `run-2` 23.6s vs 23.5s（R-008）外全部一致：24.0s、Core 15.5s、前端 7.5s（2.8/4.6）、repack 7.4s、15 passed、2687/9/3、`temp_plugin_dirs_cleaned=1` 均可在证据中复现；Resource Manifest 的 temp 两前缀已登记，复查计数 0。 | Task/Handoff 与 canonical 文件 |
| R-001 代码/行为 | 审阅 `packaged.py:258-300`；重跑 repack | `c680434ea` | 前后快照仅删本次新增；实测 `before=0/after=0`、`cleaned=1`；评审前遗留 3 个目录在本次运行前已不存在（计数 0）。 | 本次重跑；`packaged.py:261-299`；`repack-report.json:119-129` |
| R-004 代码/行为 | 审阅 `plugins.py:170-196`；执行边缘命令 | `c680434ea` | `total_checks==0` 在写报告前返回 2；`report.write_json` 的 `OSError` 被捕获返回 2；`--verbose` 已从 parser/RunOptions 移除；正常路径仍 0。 | 本次重跑；`plugins.py:175-196`；`model.py:40-43` |
| R-005 代码 | 审阅 `packaged.py:182,230-241`、`core.py:215`；核 canonical detail | `c680434ea` | Hook 夹具返回 `sys.executable`，工具解析并断言等于 `bundle/python/python.exe`（`executable_verified=true`）；`CORE-PRODUCTION-WIRING` 断言 `_allow_unsandboxed is False`；NET-ALLOW/前端下限仍按声明 deferred。 | canonical `smoke-report.json:351-364`；代码行 |
| R-006 定向覆盖 | 审阅新增 6 个测试并运行 `tests/tools` | `c680434ea` | 15 passed；新增分支覆盖 frontend/node 缺失、packaged/bundle 缺失、core setup 失败、wire spawn 失败、JSON 写失败、全层 skip（`test_software_smoke.py:168-219`），断言 BLOCKED/exit 2。 | 本次重跑；canonical `pytest-tools.log` |
| 残留与进程 | 运行前后 `%TEMP%` 目录、python 进程、`git status` | 同上 | `nm-software-smoke-*`、`nm-bundled-hook-*` 均为 0；无 `core_service` 残留；`git status` 仅剩审查前已存在的 6 个未跟踪 `verification/P04/*.jsonl`（与本 Task 无关）。另有 3 个 `_hook_runner` 进程（18:15–18:17 启动，早于本 Task 交付，来自既有 pytest 夹具），非本工具产生。 | 本次命令输出 |

## Architecture 与 Verification 两面结论

**Architecture（PASS）**：修复全部落在 `tools/smoke/**` 与 `tests/tools/**`，仍为只读工具，不进入生产依赖方向；
`--repack` 的清理责任被放回工具（不再依赖脚本自觉），生产装配 fail-closed 标志与 bundle Hook 实际解释器
都被断言，验证强度较 r1 提高。无生产代码/契约/依赖变更，无分层、安全或持久化阻断项。残留风险：工具仍耦合
生产私有成员（`_allow_unsandboxed`、`_sandbox`、`_hook_interpreter`）与 wire 协议字面量 `2.3`，生产内部重构
会显式 FAIL 而非静默通过；可接受。唯一架构外的治理问题是 R-007 的 evidence pin 缺口。

**Verification（PASS，附 P2）**：本次独立重跑了全量四层、`--repack`、退出码边缘、定向 15 项、全量 pytest、
`check.ps1`、9 条 canonical pin、范围与 Handoff 口径核对：全量 PASS/exit 0；`--repack` PASS/exit 0 且
`nm-bundled-hook-*` 0→0、`cleaned=1`；退出码 2 的两条边缘均按声明生效；全量 pytest 2687/9/3 与证据一致且
可判非本 Task 引入；9/9 pin 匹配。R-001/R-002/R-004/R-006 已闭环，R-003 仅余 R-008 的 0.1s 口径，
R-005 按声明保留 deferred；新增 R-007（治理 log 未 pin）与 R-008（23.6 vs 23.5），均为 P2，不构成 P0/P1，
也不构成关键验证缺失。

## 结论与复审

- **Decision：approved**。固定 `reviewed_head=c680434eab1ff6abcc4bc204e844ecba0c41979a` 可交 Codex 集成；
  文档 head `6df1fc355` 只含 Task/Handoff/指针/证据，不改变被审代码（`c680434ea..HEAD` 对 tools/tests 为空）。
- **closeout 前建议 Lead 处置（不阻断本次批准）**：① 按 R-007 把 `governance-check.log` 登记为 canonical
  pin（commit `6df1fc355`、sha256 `76804a4d…`），或移入 workspace 并同步引用；否则 `canonical_evidence_status`
  无法按 §4.1 完整口径置 `complete`；② 按 R-008 将 Task:84/Handoff:50 的 `23.6s` 改为 `23.5s`；③ 上述两项
  完成后更新 AC6 的 `<<PARTIAL>>` 标记（本次 r2 已核实 AC6 的测试/幂等/治理部分与独立 Review 条件）；④
  R-005 的 NET-ALLOW 语义与前端测试数下限保持 deferred，建议后续工具增强 Task 处理。
- **剩余风险**：AppContainer 依赖本机非受限账户/OS；全量 pytest 的 3 个既有失败留待独立环境/历史测试 Task；
  `CORE-NET-ALLOW` 仍只证明非 `PermissionError`（Task R2 已声明）；无新增生产风险。
- **复审规则**：若后续产生新的代码 head（`tools/smoke/**`、`tests/tools/**` 变化），本批准自动失效并需复审；
  仅文档/证据的收尾提交由 Codex 在集成记录中说明其不改变被审代码事实。本文件保持未提交状态，由 Lead 提交。
