# M2-AC1 DSH r1 Review disposition（Owner=ZCode）

- Review report: [M2-AC1-7d157858-dsh-r1.md](../../doc/reviews/M2-AC1-7d157858-dsh-r1.md)（DeepSeek Harness 非作者，静态 Review，`decision: approved` 条件下批准；P0=0、P1=0、P2×5、P3×3、P4×5）
- r1 被审 head：`7d157858f570fa6399073d0419b0adba6d13ee0f`；返修后新 head：见 branch tip（`e2e-gate-full/raw/e2e-gate.json` 的 `implementation_commit` 字段机器绑定）

## 逐条处置

| ID | 级别 | disposition | 处置说明 |
|---|---|---|---|
| F-001 | P2 | **fixed** | `run_e2e.py` 新增 `{sample}-restore-saved-matches-run1` 场景：run2 的 `saved`（重启后从持久化重读）与 run1 `saved` 按 `index` 排序逐页比对（消除枚举顺序隐含依赖），并断言 `providers`/`run_status`。gate PASS（两样本）。 |
| F-002 | P2 | **fixed** | 同上一场景覆盖 `run2.saved == run1.saved`；另新增 `{sample}-restore-internals-match-restored-saved`：run2 内部 `viewed`/`exported.sha256` 与 run2 自身重读的 `saved` 一致（同一次恢复启动内自洽）。gate PASS。 |
| F-003 | P2 | **fixed** | `main.rs::app_acl_manifest_is_generated_and_enforced` 改为遍历 `command_allowlist(true,false) ∪ command_allowlist(false,true)`（probe 7 条 + ac1 面 6 条），逐条断言 `__app-acl__` 存在 `allow-*`；ac1 权限名写错现在在此失败。cargo 26 passed。 |
| F-004 | P3 | **fixed** | `run_e2e.py` 新增 `{sample}-export-png-decodes`：gate 内用 PySide6 QImage 解码导出 PNG，断言非空解码 + 尺寸 == fixture（240×320），并把 RGB32 像素摘要（如 `b191d8e5fad6`）写入 gate JSON。gate PASS（两样本，像素摘要一致）。 |
| F-005 | P2 | **fixed（澄清 + 证据补强）** | 事实：gate runner 与桌面/Core sidecar **均**运行于 TASK-012-py312 venv（Python 3.12.3）——`M2RC1_PYTHON=sys.executable` 即 venv 解释器，Core stderr 的 PySide6 路径佐证。r1 证据中 `EVN-python` 记录的 `C:\Python314` 是 runner 对 **PATH 上 `python`** 的工具链探测结果，不是 runner 解释器——原 gate 未记录 runner 解释器，导致两种记录表面冲突。修复：`record_environment` 移除 PATH `python` 探测、新增 `EVN-runner-python`（`sys.executable` + `sys.version`）；gate JSON 顶层新增 `runner_executable` 与 `implementation_commit`。新证据：`e2e-gate-full/raw/e2e-gate.json` `runner_executable = G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`。Task 测试表与 Handoff 环境表述同步精确化。 |
| F-006 | P4 | **deferred** | `status` 的 `empty/restore` 二态对"run1 半途崩溃"仍 fail-closed（以 `AC1_SEED_CONFLICT` 失败，无假 PASS 面）；`partial` 三态属诊断增强，不阻塞闭环。留待后续验收 harness 迭代。 |
| F-007 | P3 | **fixed** | 三处注释修正：`mock_local.py::MockLocalDetectionProvider` docstring、`core_assembly.py` mock 分支注释、`acceptance_bridge.method_run_pipeline` docstring——均明确说明 seeded fixture 下 **detect 步骤不执行、`resume_blocked` 分支不被触发**，mock detector 仅为装配完整性（region-less 页 fail-closed 于 capability gap）而注册，其 detect 路径未被本 Task 验收。 |
| F-008 | P2（治理） | **open（待 Codex 裁决）** | 非 Owner 权限。Owner 立场不变：3 组文件（build.rs / capabilities / gen+permissions 生成物）是 Task L41"测试 command 仅显式测试模式注册"的 Tauri ACL 机制必然产物，无生产面扩张（F-003 修复后该论断有单测守卫）。请 Codex 在 integration record 显式追认。 |
| F-009 | P3 | **fixed** | 四个测试日志全部补 `# interpreter/toolchain` 头与 `# EXIT:` 尾（并记录 worktree HEAD）；gate JSON 顶层新增 `implementation_commit`（证据↔commit 机器绑定）。注：入库的 `e2e-gate-full` 证据由**返修提交后的 head** 重跑生成（见下方重跑记录）。 |
| F-010 | P4 | **partially fixed / deferred** | (c) fixed：`output_path` 缺失现显式 `FAIL`（不再把 `"None"` 当路径）。(a)(b) deferred：`log_dir` 参数化与进程树超时清理属验收 harness 的健壮性打磨，两次完整 gate 均未触发，留待后续迭代。 |
| F-011 | P4 | **fixed** | spawn argv 抽为 `ac1_bridge::spawn_args()` 并新增 `spawn_args_target_the_acceptance_module` 字面断言 `["-m","bootstrap.acceptance_bridge"]`；原失败路径测试更名为 `spawn_fails_typed_on_missing_python`（名称与判别力一致）。cargo 26 passed。 |
| F-012 | P4 | **fixed** | `commandSurface.test.ts` 新增 "ac1 commands are denied on production and probe surfaces"：`AC1_TEST_COMMANDS` 三命令在两模式均 reject。vitest 19 passed。 |
| F-013 | P4 | **fixed** | seed Region 的 origin 由 `USER` 改为 `MACHINE`（与 detect 步骤 region_creator 同源，纯 harness fixture region，不冒充用户编辑），并加注释说明理由。全仓 pytest 1322 passed + 5 skipped 零回归。 |

## 返修后验证（全部在返修工作区执行）

| 门禁 | 结果 |
|---|---|
| `pytest tests/m2_acceptance -q` | 4 passed, EXIT 0 |
| 全仓 `pytest -q -rs` | 1322 passed + 5 skipped, EXIT 0 |
| `cargo test --locked` | 26 passed, EXIT 0 |
| `npm test`（vitest） | 3 files, 19 passed, EXIT 0 |
| `python verification/M2-AC1/run_e2e.py`（完整构建版） | **GATE PASS，44 场景全 PASS**（含 4 个新增场景） |

复审时请以 branch tip 为准（r1 被审 head `7d157858` 之后的返修 commit），逐条核对上表 disposition 并给出通过/不通过结论。
