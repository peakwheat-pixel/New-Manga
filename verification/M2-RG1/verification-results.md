# M2-RG1 verification results — M2 Release Gate (Windows 本机口径)

- 审计对象：M2-AC5 交付形态（NSIS installer + PyInstaller onedir 四入口自包含 sidecar）
- base：`875eb818abc74a498c84026016dd1a1c72e0ad50`（M2-AC5 收口）
- 交付链：claim `33280f5e` → console-policy fix `29c71024` → gate runner + gate run `a1100d75` → evidence/bookkeeping（终 tip）
- **Release candidate（Gate 绑定）installer**：`apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe`
  sha256 = `d222073becc50d593a3f0d706ef799df45d369a51f13c1e81423dbeef7ed09db`（console-policy 修复后重建；修复前 build1 为 `def5b92bab950983…`，仅作 AC1 fresh-build 过程证据）
- 用户裁决（2026-09-29，原文存档于 Task 文件）："把本机视为干净widows环境。若本机通过，则视为pass" —— 本机（Windows 11 专业版 x64 build 26200.9457，AMD Ryzen 9 7950X3D，32 GB）= 干净 Windows 验证基座
- gate runner：`packaging/release-gate/run_release_gate.py`；机器可读汇总：[raw/rg1-gate.json](raw/rg1-gate.json)（verdict **PASS**，23/23 场景）

## AC × 结果 × 证据

| AC | 结果 | 关键数字 / 裁决 | 证据 |
|---|---|---|---|
| AC1 构建锚定 | **PASS** | fresh worktree @ base 顺序构建：build_sidecar.ps1（EXIT=0，pyinstaller 6.22.3）→ frontend build → `npx @tauri-apps/cli@2 build`（EXIT=0，tauri-cli 2.12.0）；sidecar 全清单 161 文件（与 M2-AC5 runA 清单首文件 sha256 一致：`F81DC49E…_bz2.pyd`）；工具链/OS 快照入库；后续全部 gate 运行绑定 `d222073b…` | [raw/rg1-build-sidecar.log](raw/rg1-build-sidecar.log)、[raw/rg1-frontend-build.log](raw/rg1-frontend-build.log)、[raw/rg1-tauri-build-run1.log](raw/rg1-tauri-build-run1.log)、[raw/rg1-tauri-build-run2-fix.log](raw/rg1-tauri-build-run2-fix.log)、[raw/rg1-sidecar-manifest-build1.txt](raw/rg1-sidecar-manifest-build1.txt)、[raw/rg1-environment-record.log](raw/rg1-environment-record.log)、[raw/rg1-os-detail.log](raw/rg1-os-detail.log) |
| AC2 GUI console policy | **PASS** | ① installed exe PE OptionalHeader Subsystem=**2（GUI）**（修复前侦察实测=3）；② EnumWindows 运行期观测：3 轮 production 冷启动中（各保持 alive 10 s）与干净退出后（sidecar 全部收割）`ConsoleWindowClass` 命中数=**0/0/0**；③ 静态源审计：`windows_subsystem` 属性由 `cfg_attr(not(debug_assertions),…)` 门控、4 处 `CREATE_NO_WINDOW` 全部位于 `#[cfg(windows)]`、`core_sidecar.spec` `console=True` 参数值未改（注释同步） | [raw/rg1-gate.json](raw/rg1-gate.json)（RG1-PE1 / RG1-PE2 / RG1-CW1-R1..3 / RG1-CW2-R1..3）、[raw/rg1-console-policy-fix.diff](raw/rg1-console-policy-fix.diff)、[raw/rg1-tauri-build-run2-fix.log](raw/rg1-tauri-build-run2-fix.log) |
| AC3 Cold start metrics（只测录，无阈值） | **PASS** | app 冷启动（CreateProcess→首个可见非 Console 顶层窗口，逐轮新 lab APPDATA）：min **46.0** / median **48.2** / max **157.1** ms（n=3）；core ready（spawn→`core.ping` ready）：min **239.1** / median **240.5** / max **240.9** ms（n=3）；ac1 handshake（spawn→`pong`，M2AC1_TEST_MODE=1 冻结配置）：min **266.5** / median **268.2** / max **280.1** ms（n=3）；净化 PATH 移除 11 条、保留 45 条 | [raw/rg1-gate.json](raw/rg1-gate.json)（timings + environment）、[raw/rg1-gate-run.log](raw/rg1-gate-run.log) |
| AC4 Packaged dependency closure | **PASS** | 四入口安装态 stdio 往返全通：core_service（core.ping ready + ListBooks envelope + shutdown）、host_bridge（ping + issue/resolve/revoke，opaque=`m2id.v1.…`，loader-seeded catalog）、acceptance_bridge（ping/pong + shutdown）、catalog_loader（CLI 参数从 worktree 源确认 → lab seed 2 行 → sqlite3 读回）；PyInstaller warn 文件入库并逐类审查：missing 共 **11** 条，全部为条件/可选导入（`fcntl`/`grp`/`posix`/`pwd`/`readline`/`resource`/`vms_lib`/`java`/`_winreg`/`_posixsubprocess`/`_frozen_importlib_external`），**0 条 load-time-critical**（四入口运行期往返即操作性证据）；M2-AC5 clean-start 25 场景回归 **25/25 PASS**（同 installer） | [raw/rg1-gate.json](raw/rg1-gate.json)（RG1-DC1..DC4 / RG1-W1）、[raw/rg1-warn-warn-core_sidecar.txt](raw/rg1-warn-warn-core_sidecar.txt)、[raw/rg1-m2ac5-cleanstart-gate.json](raw/rg1-m2ac5-cleanstart-gate.json)、[raw/rg1-m2ac5-cleanstart-runner.log](raw/rg1-m2ac5-cleanstart-runner.log) |
| AC5 Windows support matrix | **PASS（按冻结裁决）** | 支持矩阵声明：**Windows 11 x64（本机 build 26200）已验证（本 Gate）；Windows 10 及其他 build NOT_RUN（如实披露，不阻断）**；本机快照：Windows 11 专业版 10.0.26200.9457 x64，Ryzen 9 7950X3D（16C/32T），33.98 GB | [raw/rg1-environment-record.log](raw/rg1-environment-record.log)、[raw/rg1-os-detail.log](raw/rg1-os-detail.log)、本表、Task 文件、Handoff（三处 NOT_RUN 披露） |
| AC6 证据纪律与范围 | **PASS** | 每日志带 shell/解释器头 + 固定 HEAD + 每命令 EXIT；`git diff --name-status 875eb818..<delivery>` 全落两级允许路径（4 个条件允许源文件 + spec 注释 + 新增 gate/evidence/doc）；`git diff --check 875eb818..<delivery>` EXIT=0（3 处 evidence 日志行尾空格已做规范化清理，见 raw/README 注记）；三层基线全绿（下表）；NSIS 卸载测试 NOT_RUN（不在 Backlog 四项范围）；`src/**` Python 零改动 | [raw/rg1-scope-audit.log](raw/rg1-scope-audit.log)、[raw/rg1-final-scope-audit.log](raw/rg1-final-scope-audit.log)、三层基线日志（下表） |

## 三层基线（交付 head）

| 层 | 结果 | 证据 |
|---|---|---|
| `TASK-012-py312 python -m pytest tests/m2_acceptance -q` | **35 passed**，EXIT=0 | [raw/rg1-baseline-pytest-m2-acceptance.log](raw/rg1-baseline-pytest-m2-acceptance.log) |
| `cargo test --bin m2rc1-desktop`（M2RC1_PYTHON/TASK-012 + M2RC1_SRC_ROOT） | **38 passed; 0 failed; 1 ignored**，EXIT=0 | [raw/rg1-baseline-cargo-test.log](raw/rg1-baseline-cargo-test.log) |
| `npx vitest run`（apps/desktop/frontend） | **31 passed (5 files)**，EXIT=0 | [raw/rg1-baseline-vitest-run.log](raw/rg1-baseline-vitest-run.log) |

## 披露事项

1. **M2-AC5 证据"运行→搬运→还原"**：clean-start runner 把证据写死到 worktree 的 `verification/M2-AC5/raw/`（P3-9(b) 已知行为，runner 禁改）。本次运行产出后复制改名 `rg1-m2ac5-*` 入 `verification/M2-RG1/raw/`，随后 `git restore verification/M2-AC5/`——该目录在本 Task 交付中零提交（scope audit 佐证）。
2. **warn 文件布局**：PyInstaller 6.22 对单 spec 多 Analysis 只产出一份合并 `warn-core_sidecar.txt`（覆盖全部 4 入口），非释放侦察时预期的"4 份 warn-*.txt"；审查对象（4 入口全部 missing 模块集合）不变。
3. **acceptance_bridge probe 配置**：该 bridge 仅在其冻结的显式测试配置（`M2AC1_TEST_MODE=1`）下装配核心，裸 probe 按设计应答 `AC1_BRIDGE_MISCONFIGURED`（首跑如实记录 FAIL 后修正 probe env，与 M2-AC5 ac1_env 同口径；非放宽断言）。
4. **零触碰口径**：gate runner 与 25 场景 runner 的全部 spawn 均 pin `APPDATA`/`NEWMANGA_DATA_ROOT` 进 lab；宿主真实 `%APPDATA%\com.newmanga.m2rc1.desktop` 全程只读（CS-Z4 files=2 byte-identical）。首次 gate run 曾以缺省 data root 短暂 spawn core_service 计时 probe（默认落在宿主 `%LOCALAPPDATA%\New Manga`，该目录 M2-AC5 时期已存在、本次未产生新文件），runner 随即改为逐轮 lab data root 并复跑全量 gate。
5. **NOT_RUN**：Windows 10 / 其他 build 实机覆盖（AC5 冻结裁决：候选，不阻断）；NSIS 卸载链路（非 Backlog 四项）。
6. **行尾空格规范化**：3 份 evidence 日志（rg1-console-policy-fix.diff / rg1-gate-run.log / rg1-os-detail.log）入库后做了行尾空格清理以满足 `git diff --check` EXIT=0；清理仅删除行尾空白字符，内容（sha256/数字/路径/命令输出）逐字符保留。
