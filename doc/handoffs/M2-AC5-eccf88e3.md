---
task_id: M2-AC5
author: ZCode（子 agent 代行实现）
recipient: DeepSeek Harness（非作者 Reviewer）
base_commit: 6f79c040c79ae4389cf73abcae1b26617b1a2fba
release_commit: 82c85c0fcf738ff31fb583fff20f1e01809f16ef
implementation_head: eccf88e36e088d31231469c298f95d919468a2ba
delivery_commit: 交付 commit = `git log --grep "delivery evidence + handoff"`（parent=eccf88e3；自引用不写死）
status: in_review
---

# Handoff：M2-AC5 — Windows Packaging & Clean-start Acceptance

## 交付结果

分支 `agent/zcode/M2-AC5-package-clean-start`、worktree
`G:/CODEX/New Manga.worktrees/M2-AC5-zcode`。实现 head `eccf88e3`；完整复审范围从
base `6f79c040`（release commit `82c85c0f`）到本 Handoff/证据 commit。

**最小可复现 Windows 打包链已建立**：`npx @tauri-apps/cli@2 build`（tauri-cli 2.12.0）
产出 NSIS 安装包（26.62 MiB），内含 PyInstaller onedir 自包含 Core sidecar
（安装目录 `resources/core-sidecar/`）。安装后的应用在剔除 Python 的 PATH、清空
`M2RC1_*` 的模拟环境下完成 静默安装 → 启动 → 资源通道矩阵 / 验收环 / 真窗口生产
三种模式 → 干净退出。终版 gate **GATE PASS（20/20 场景，EXIT=0）**。

## AC1-AC5 逐项对照（实测数字 + EXIT）

| AC | 判定 | 实测 | 证据（verification/M2-AC5/） |
|---|---|---|---|
| AC1 打包产物可复现 | **PASS**（差异可解释） | 同输入重跑 tauri build ×2：sidecar `_internal/**` 依赖闭包（157 文件，含 Qt/pyd/DLL）hash **全同**；4 个 frozen 入口壳、host exe、NSIS 安装包 hash 不同——PyInstaller PKG archive（marshalled code 带 timestamp）/ Rust 链接时间戳 / NSIS 打包时间戳，工具链确定性差异，输入 hash 不变 | [raw/ac1-repro-sidecar-diff.txt](../../verification/M2-AC5/raw/ac1-repro-sidecar-diff.txt)、[raw/ac1-repro-run1-hashes.txt](../../verification/M2-AC5/raw/ac1-repro-run1-hashes.txt)/[run2](../../verification/M2-AC5/raw/ac1-repro-run2-hashes.txt)、[raw/artifact-inventory-final.txt](../../verification/M2-AC5/raw/artifact-inventory-final.txt) |
| AC2 packaged spawn fail-closed + dev 零变化 | **PASS** | `spawn_packaged`：sidecar exe 缺失 → 在构建 Command 之前返回 typed `CORE_SPAWN_FAILED:PACKAGED_SIDECAR_MISSING`（单元测试钉死，绝不回落系统 python）；packaged 判定=`M2RC1_PACKAGED=1` 或 `M2RC1_SRC_ROOT` 缺失且 `<exe_dir>/resources/core-sidecar/host_bridge.exe` 存在；dev 路径字节不变。基线：cargo **38 passed + 1 ignored** EXIT=0（34 基线 + 4 新增 packaged 测试）、pytest **35 passed** EXIT=0、vitest **31 passed** EXIT=0 | [raw/baseline-cargo-test.log](../../verification/M2-AC5/raw/baseline-cargo-test.log)、[raw/baseline-pytest-m2-acceptance.log](../../verification/M2-AC5/raw/baseline-pytest-m2-acceptance.log)、[raw/baseline-vitest-run.log](../../verification/M2-AC5/raw/baseline-vitest-run.log) |
| AC3 clean-start（无系统 Python） | **PASS**（本机 host simulation 口径） | 净化 PATH（剔除 10 条目：python/venv/conda/WindowsApps）后 `where python` exit=1；NSIS `/S /D=` 静默安装成功（163 文件落盘）；probe 13/13 PASS（E-01 fetch digest==fixture sha，真实 sidecar 往返）；ac1 双 launch 全 PASS（desktop pid 4540→43864、core pid 39180→48160=真实重启；保存/恢复/Reader/PNG 导出 digest 全匹配）；production 真窗口存活+优雅关闭 | [raw/cleanstart-final.log](../../verification/M2-AC5/raw/cleanstart-final.log)（GATE PASS EXIT=0）、[raw/cleanstart-gate.json](../../verification/M2-AC5/raw/cleanstart-gate.json)、[raw/environment-record.log](../../verification/M2-AC5/raw/environment-record.log) |
| AC4 workflow / path / exit | **PASS** | packaged 缺省数据根 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,derived,managed,data}` 首启动自动创建（catalog.sqlite 落盘）；安装目录 163 文件三模式跑后 hash **零变化**（CS-Z1）；lab 源 fixture 4 文件字节不变（CS-Z2）；优雅关闭后四个 sidecar exe 进程零残留（CS-Z3；python.exe 计数为记录性观察，宿主自身有无关进程） | [raw/cleanstart-final.log](../../verification/M2-AC5/raw/cleanstart-final.log) |
| AC5 证据纪律 | **PASS** | 每命令 shell/解释器头 + EXIT；`git diff --check 6f79c040..HEAD` **EXIT=0**；`git diff --name-status` 全部在允许路径；**`src/**` Python 零改动**；三层基线在交付 head 复跑留痕 | [checkpoint.md](../../verification/M2-AC5/checkpoint.md)、[raw/README.md](../../verification/M2-AC5/raw/README.md) |

## 打包方案与取舍（风险裁决点 1）

**单 onedir 四入口**（[packaging/m2ac5/core_sidecar.spec](../../packaging/m2ac5/core_sidecar.spec)）：
`host_bridge.exe`（resource channel，`infrastructure.resource_channel.host_bridge`）+
`core_service.exe`（production library，`bootstrap.core_service`）+
`acceptance_bridge.exe`（M2-AC1 测试模式，`bootstrap.acceptance_bridge`）+
`catalog_loader.exe`（launcher 侧 seeding 工具——packaged 环境没有系统 python 可跑
dev runner 的 `python -m ...catalog_loader` seeding 步骤，此为 launcher 等价物；
产品命令面零扩展，F-03 语义不变）。四入口共享一个 `_internal` 依赖目录。

- **PySide6 进闭包（与释放注记"Qt-free"的偏差，实测裁决）**：`assemble_acceptance_core`
  （M2-AC1 冻结装配，pytest 与 E2E 共用）硬依赖 PySide6——`src/bootstrap/acceptance_bridge.py`
  §"Requires PySide6"（QGuiApplication + production Qt 渲染适配器）。排除 Qt 时 frozen
  acceptance_bridge.exe 启动即 ModuleNotFoundError（fail-closed 证明）。因此闭包含 Qt；
  其余三入口 import 闭包实测仍为 stdlib + 仓库内包（TASK-012 venv 零 site-packages 模块）。
  属 M2-AC1 冻结事实而非打包选择；打包层解决，未触碰 `src/**`，不触发停机条款。
- **pypdfium2/mobi 不进闭包**：延迟 import（PDF/MOBI rasters），clean-start 场景不触及；
  PyInstaller warn 留痕。
- **library/AC1 channel 零改动**：`library_bridge.rs`/`ac1_bridge.rs` 不在允许路径，
  spawn 签名保持 `(python_exe, src_root, ...)`；packaged 下 main.rs 把参数重指向 frozen
  exe 与 sidecar 目录（PyInstaller 入口包装脚本忽略 `-m <module>` argv，PYTHONPATH/
  current_dir 指向 sidecar 目录为惰性）。`core_bridge.rs`（在允许路径内）新增
  `spawn_packaged`（无 `-m`、无 src cwd、typed fail-closed），dev `spawn` 行为字节不变，
  两者共享 `adopt_child`。

## packaged 判定与数据根

- 判定（main.rs，4 个新单元测试覆盖判定矩阵）：显式 `M2RC1_PACKAGED=1`；或
  `M2RC1_SRC_ROOT` 缺失且 `<exe_dir>/resources/core-sidecar/host_bridge.exe` 存在
  （已安装应用裸启动）。dev（M2RC1_* 全在）永不进 packaged 分支，无 installed layout
  的 dev 裸跑保持原 expect panic 行为。
- 数据根缺省：`%APPDATA%\com.newmanga.m2rc1.desktop\{derived,managed,catalog\catalog.sqlite,data}`，
  首启动 `create_dir_all`；显式 `M2RC1_*` env 仍优先（runner 用与 dev 相同的 env 契约
  pin lab 目录）。

## 迭代失败记录（fail→fix→pass，全程留痕）

1. PyInstaller spec REPO_ROOT 多算一级目录 → `infrastructure` missing → 修正。
2. 构建 venv 缺 PySide6 → acceptance 入口 ModuleNotFoundError → 补装并 pin 版本。
3. runner PATH 剔除 marker 大小写 bug（`"WindowsApps" in "...windowsapps"` 恒 False）→ 修复。
4. ac1 lab root 未预创建（显式 `M2RC2_CATALOG_DB` 路径由 launcher 准备，与 dev 契约一致，
   host 行为正确）→ runner 补 mkdir。
5. runner desktop_pid 从 results JSON 取（字段不存在恒 0）→ 改用 runner spawn 的 PID。
以上对应 raw/cleanstart-run1..5.log 与 raw/pyinstaller-build-closure-pyside6.log 前置迭代。

## NOT_RUN / BLOCKED / 候选登记

- **NOT_RUN：真干净 Windows 机器安装**（无任何开发工具链的 physical/VM 覆盖）——释放时
  冻结的口径（T3.2.1 host simulation 路线），M2 Release Gate 范围。
- **NOT_RUN：NSIS 卸载流程**——本 Task AC 未要求，未测。
- **候选登记（非本 Task 范围）**：若 Release Gate 要求 bit-for-bit 可复现，需要
  Rust `/Brepro`、PyInstaller 固定 build-id/SOURCE_DATE_EPOCH、NSIS 时间戳固定；
  当前差异已解释为工具链时间戳，输入侧可复现。
- **候选登记**：完整产品分发的 provider 闭包（pypdfium2/mobi/torch 类生产依赖）随
  产品范围扩展另行 Task。
- 无 BLOCKED；未触发 `src/**` 停机条款。

## 范围遵守

- 提交范围（`git diff --name-status 6f79c040..HEAD`）：`core_bridge.rs`、`main.rs`、
  `tauri.conf.json`、`packaging/m2ac5/**`、`doc/**`（Task 登记/治理，release 既有）、
  `verification/M2-AC5/**`——全部在允许路径。
- tauri build 每次重写 `gen/schemas/**`、`permissions/autogenerated/**`（仅行尾表示，
  内容零变化），已按协议 `git checkout --` 还原两次（最终态已还原）。
- 构建产物（frontend/dist、target/**、PyInstaller onedir）全部在 gitignored 路径，
  零产物入 git。构建 venv（`G:/CODEX/New Manga.task-envs/m2ac5-build`）独立于产品运行时
  依赖；`requirements.txt` 零改动。

## 下一接收者

**DeepSeek Harness（非作者 Review）**。建议指令：

> Review M2-AC5 @ worktree `G:/CODEX/New Manga.worktrees/M2-AC5-zcode`，分支
> `agent/zcode/M2-AC5-package-clean-start`，base `6f79c040`、implementation head
> `eccf88e3`（+ 文档/证据 commit，见 Task frontmatter）。按
> [doc/handoffs/M2-AC5-eccf88e3.md](M2-AC5-eccf88e3.md) 逐项复核 AC1-AC5：重点核查
> (1) packaged fail-closed 语义与 4 个新单元测试、(2) dev 分支字节不变的等价性、
> (3) clean-start gate 判定逻辑是否真证明"无系统 Python"（PATH 净化断言 + frozen exe
> 服务证据）、(4) PySide6 进闭包裁决与允许路径遵守（library_bridge.rs/ac1_bridge.rs
> 零改动）。证据在 verification/M2-AC5/（verification-results.md + raw/ + checkpoint.md）。
