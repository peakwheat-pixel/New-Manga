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
`M2RC1_*` 的模拟环境下完成 静默安装 → 安装态 library probe → 启动 →
资源通道矩阵 / 验收环 / 真窗口生产三种模式 → 干净退出。r1 终版 gate
**GATE PASS（25/25 场景，EXIT=0，被测安装包 sha256=5410e29e…，r0 未重建复用）**。

## AC1-AC5 逐项对照（实测数字 + EXIT）

| AC | 判定 | 实测 | 证据（verification/M2-AC5/） |
|---|---|---|---|
| AC1 打包产物可复现 | **PASS**（差异可解释） | 同输入重跑 tauri build ×2：sidecar `_internal/**` 依赖闭包（157 文件，含 Qt/pyd/DLL）**156/157 相同**（r1 勘误：唯一差异 `_internal/base_library.zip`=stdlib zip 内嵌时间戳，与入口壳同类工具链时间戳差异，见 raw/ac1-repro-sidecar-diff.txt:101,122）；全树 161 文件=156 相同+5 差异（4 个 frozen 入口壳+base_library.zip）；host exe、NSIS 安装包 hash 不同——PyInstaller PKG archive（marshalled code 带 timestamp）/ Rust 链接时间戳 / NSIS 打包时间戳，工具链确定性差异，输入 hash 不变 | [raw/ac1-repro-sidecar-diff.txt](../../verification/M2-AC5/raw/ac1-repro-sidecar-diff.txt)、[raw/ac1-repro-run1-hashes.txt](../../verification/M2-AC5/raw/ac1-repro-run1-hashes.txt)/[run2](../../verification/M2-AC5/raw/ac1-repro-run2-hashes.txt)、[raw/artifact-inventory-final.txt](../../verification/M2-AC5/raw/artifact-inventory-final.txt) |
| AC2 packaged spawn fail-closed + dev 零变化 | **PASS** | `spawn_packaged`：sidecar exe 缺失 → 在构建 Command 之前返回 typed `CORE_SPAWN_FAILED:PACKAGED_SIDECAR_MISSING`（1 个缺失分支单元测试钉死，绝不回落系统 python）；packaged 判定=`M2RC1_PACKAGED=1` 或 `M2RC1_SRC_ROOT` 缺失且 `<exe_dir>/resources/core-sidecar/host_bridge.exe` 存在（3 个解析矩阵单元测试）；dev 路径**行为等价：Command 构建（argv/env/current_dir）逐字一致，仅成功路径子进程接管重构为共享 adopt_child，失败路径语义不变**（r1 A-⑤ 更正）。基线：cargo **38 passed + 1 ignored** EXIT=0（34 基线 + 4 新增 packaged 测试）、pytest **35 passed** EXIT=0、vitest **31 passed** EXIT=0 | [raw/baseline-cargo-test.log](../../verification/M2-AC5/raw/baseline-cargo-test.log)、[raw/baseline-pytest-m2-acceptance.log](../../verification/M2-AC5/raw/baseline-pytest-m2-acceptance.log)、[raw/baseline-vitest-run.log](../../verification/M2-AC5/raw/baseline-vitest-run.log)、r1 复跑 [raw/r1-baseline-cargo-test.log](../../verification/M2-AC5/raw/r1-baseline-cargo-test.log)/[pytest](../../verification/M2-AC5/raw/r1-baseline-pytest-m2-acceptance.log)/[vitest](../../verification/M2-AC5/raw/r1-baseline-vitest-run.log) |
| AC3 clean-start（无系统 Python） | **PASS**（本机 host simulation 口径） | 净化 PATH（剔除 **11 条目**：python/venv/conda/WindowsApps 家族，对齐 cleanstart-gate.json CS-E1 removed_entries）后 `where python` exit=1；NSIS `/S /D=` 静默安装成功（163 文件落盘）；安装态 library probe：core.ping ready、**ListBooks 返回结构合法**、core.shutdown stopped（r1 P2-2 补强 CS-L1/L2/L3）；probe 13/13 PASS（E-01 fetch digest==fixture sha，真实 sidecar 往返）；ac1 双 launch 全 PASS（desktop pid 4540→43864、core pid 39180→48160=真实重启；保存/恢复/Reader/PNG 导出 digest 全匹配）；production 真窗口存活+优雅关闭 | [raw/cleanstart-r1-final.log](../../verification/M2-AC5/raw/cleanstart-r1-final.log)（GATE PASS 25/25 EXIT=0）、[raw/cleanstart-gate.json](../../verification/M2-AC5/raw/cleanstart-gate.json)、[raw/r1-library-probe.log](../../verification/M2-AC5/raw/r1-library-probe.log)、[raw/environment-record.log](../../verification/M2-AC5/raw/environment-record.log) |
| AC4 workflow / path / exit | **PASS** | packaged 缺省数据根 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,derived,managed,data}` 首启动自动创建（catalog.sqlite 落盘；r1 P2-4 起验收时 `APPDATA` pin 进 lab，宿主真实目录零接触零删除）；安装目录 163 文件三模式跑后 hash **零变化**（CS-Z1）；宿主真实 %APPDATA% 全程字节不变（CS-Z4，r1 新增 gate 场景）；lab 源 fixture 4 文件字节不变（CS-Z2）；优雅关闭后四个 sidecar exe 进程零残留（CS-Z3；python.exe 计数为记录性观察，宿主自身有无关进程） | [raw/cleanstart-r1-final.log](../../verification/M2-AC5/raw/cleanstart-r1-final.log) |
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
  `spawn_packaged`（无 `-m`、无 src cwd、typed fail-closed）。dev `spawn`
  **行为等价**（r1 A-⑤ 更正）：Command 构建（argv/env/current_dir）逐字一致，
  仅成功路径子进程接管重构为共享 `adopt_child`；失败路径语义不变，
  两者共享 `adopt_child`。

## packaged 判定与数据根

- 判定（main.rs，3 个解析矩阵单元测试 + 1 个缺失分支测试）：显式 `M2RC1_PACKAGED=1`；或
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

## r1 条件闭合（DSH r1 approved_with_conditions：0×P0/P1、5×P2）

范围硬边界遵守：本节闭合只改 `packaging/m2ac5/**`、`verification/M2-AC5/**`、本
Handoff、`doc/tasks/M2-AC5.md`；`src/**`、`requirements.txt`、`doc/contracts/**`、
`library_bridge.rs`、`ac1_bridge.rs`、`main.rs`、`core_bridge.rs` 零改动
（P3-3/P3-7 Rust 侧建议只登记候选，见下）。安装包未重建，r1 gate 复用 r0 NSIS
产物（sha256 `5410e29e118d24ae28192c241a3fc7a8c3e6f5bcc4def38d7c588e900be61336`）。

| 项 | 闭合内容 | 证据 |
|---|---|---|
| P2-4（安全项） | runner 删除对宿主真实 `%APPDATA%\com.newmanga.m2rc1.desktop` 的一切删除/写入操作；probe/ac1/production/library-probe 四类 launch env 全部 `APPDATA=<lab>/roaming` 隔离（`packaged_user_root()` 读 `APPDATA` 环境变量，main.rs 语义不变）；新增 gate 场景 CS-Z4：宿主真实目录（2 文件）全程前后 hash 零变化 | [run_clean_start_e2e.py](../../packaging/m2ac5/run_clean_start_e2e.py)（HOST_USER_ROOT 只读快照 + production_env/ac1_env/probe_env APPDATA pin）、[raw/cleanstart-r1-final.log](../../verification/M2-AC5/raw/cleanstart-r1-final.log) CS-Z4 |
| P2-2 | runner 新增安装态 stdio probe：直接驱动 `<install>/resources/core-sidecar/core_service.exe` 发 `core.ping`/`ListBooks`/`core.shutdown`（Contract 1.1 envelope，净化 PATH 下）；gate 场景 CS-L1（ping ready + capabilities）/CS-L2（ListBooks 结构合法）/CS-L3（shutdown stopped） | [raw/r1-library-probe.log](../../verification/M2-AC5/raw/r1-library-probe.log)、[raw/cleanstart-r1-final.log](../../verification/M2-AC5/raw/cleanstart-r1-final.log) phase 1.5 |
| P2-3 | 新增 [packaging/m2ac5/README.md](../../packaging/m2ac5/README.md)：build venv 创建命令与固定版本（pyinstaller 6.22.3、PySide6_Essentials 6.11.2）、与产品 requirements.txt 隔离声明、构建步骤（build_sidecar.ps1 → tauri build）、四入口说明；`build_sidecar.ps1` 与 `requirements-build.txt` 注释中的引用即指向它 | packaging/m2ac5/README.md |
| P2-1 | "157 文件 hash 全同"更正为 **156/157 相同**，`_internal/base_library.zip`（stdlib zip 内嵌时间戳）归类为与入口壳同类工具链时间戳差异；四处同步（Task AC1 注、本文件 AC1 行、verification-results AC1 行、checkpoint 行 8） | 本文件 AC1 行、[raw/ac1-repro-sidecar-diff.txt](../../verification/M2-AC5/raw/ac1-repro-sidecar-diff.txt):101,122 |
| P2-5+F | 原始范围审计入库：`git diff --name-status 6f79c040..783fc74f`、`git diff --check 6f79c040..783fc74f; echo EXIT=$?`、`git status --porcelain`；r1 终版范围审计另见 f2 | [raw/f1-scope-audit.log](../../verification/M2-AC5/raw/f1-scope-audit.log)、[raw/f2-final-scope-audit.log](../../verification/M2-AC5/raw/f2-final-scope-audit.log) |
| P3-1 | raw/README.md 改为如实清单（原"全部日志带头+EXIT"不成立：tauri-build-run1/run2、cleanstart-final/run5 无命令头/EXIT 行，已标注；r1 新日志全部带头）；"剔除 10 条目"→**11 条**（对齐 gate.json CS-E1）；"4 单测钉死缺失分支"→"3 测解析矩阵 + 1 测缺失分支" | [raw/README.md](../../verification/M2-AC5/raw/README.md)、本文件 AC 行 |
| P3-2 | runner `where host_bridge.exe` 补 `encoding="mbcs", errors="replace"`（中文 locale 不再炸 reader thread） | run_clean_start_e2e.py assert_no_python_on_path |
| P3-6 | `install_dir` 含空格直接 FAIL（CS-E3 场景，提示改 TEMP）；silent_install 内 `/D=` 最后参数断言 + target 空格 guard | run_clean_start_e2e.py、[raw/cleanstart-r1-final.log](../../verification/M2-AC5/raw/cleanstart-r1-final.log) CS-E3 |
| A-⑤ | "dev spawn 字节不变"更正为"行为等价：Command 构建（argv/env/current_dir）逐字一致，仅成功路径子进程接管重构为共享 adopt_child；失败路径语义不变"（实现 commit eccf88e3 message 中的 "byte-unchanged" 为历史记录，以本更正为准） | 本文件 AC2 行 / 打包方案节 |
| P3-3/P3-7（只登记） | Rust 侧建议（如有）登记为候选，不改 main.rs/core_bridge.rs（本闭合范围硬边界） | 本表 |

## 披露（H 项）

1. **Qt/PySide6 许可与体积**：sidecar 闭包含 PySide6_Essentials 6.11.2 +
   shiboken6 6.11.2（LGPLv3/商业双许可——分发义务：提供许可文本与组件版本信息、
   保留版权声明；LGPL 动态链接口径对 frozen exe 的适用性需在正式分发前由用户
   裁决）。闭包内 PySide6/shiboken 相关资产约 150 项（DLL/pyd/pyi 等），是
   sidecar 95 MB、安装包 26.62 MiB 体积的主要来源（安装包内 LZMA 压缩后）。
2. **安装目录第 4 个可执行 `catalog_loader.exe`**：分发面增项——它具备写
   Core/SQLite catalog 的能力（launcher 侧 seeding 等价物，F-03 产品命令面零扩展）。
   正式分发前建议评估是否保留在安装目录、移入工具子目录或按需下载（候选，不在本
   Task 范围）。
3. **Qt 字体缺失告警**：ac1 packaged 运行 stderr 出现 `QFontDatabase: Cannot find
   font directory .../PySide6/lib/fonts`（raw/cleanstart-ac1-run1-stdout.log:4-5）。
   offscreen 渲染仍产出正确 digest（CS-A4/A5 PASS），但真实 UI 文本渲染前的字体
   部署需要处理（候选登记）。
4. **PyInstaller warn 留痕**（候选登记）：四个入口共用一个 workpath 时 warn 文件
   路径固定（`warn-core_sidecar.txt`），实际只有最后一个入口的分析结果存活——
   四入口各自的 missing-module 报告不完整。如需逐入口留痕，构建脚本应为每入口
   独立 workpath（候选，不在本 Task 范围）。

## 下一接收者

**DeepSeek Harness（非作者 Review）**。r1 条件已全部闭合，建议复核指令：

> 复核 M2-AC5 r1 闭合 @ worktree `G:/CODEX/New Manga.worktrees/M2-AC5-zcode`，
> 分支 `agent/zcode/M2-AC5-package-clean-start`。对照本 Handoff "r1 条件闭合" 表
> 逐项核验 P2-1..P2-5/P3/A-⑤/H：重点 (1) P2-4 安全项——runner 已无宿主真实
> %APPDATA% 删除操作、CS-Z4 前后 hash 证明；(2) P2-2 CS-L1/L2/L3 是否构成 AC3
> "ListBooks workflow 返回"的安装态可观测断言；(3) 勘误数字（156/157、11 条、
> 3+1 单测）与 raw 证据一致性；(4) 披露四段是否完整。r1 gate=25/25 PASS
> （raw/cleanstart-r1-final.log），三层基线 cargo 38+1 / pytest 35 / vitest 31
> 全 EXIT=0。

> Review M2-AC5 @ worktree `G:/CODEX/New Manga.worktrees/M2-AC5-zcode`，分支
> `agent/zcode/M2-AC5-package-clean-start`，base `6f79c040`、implementation head
> `eccf88e3`（+ 文档/证据 commit，见 Task frontmatter）。按
> [doc/handoffs/M2-AC5-eccf88e3.md](M2-AC5-eccf88e3.md) 逐项复核 AC1-AC5：重点核查
> (1) packaged fail-closed 语义与 3 个解析矩阵 + 1 个缺失分支单元测试、(2) dev 分支行为等价性
> （Command 构建逐字一致，adopt_child 重构）、
> (3) clean-start gate 判定逻辑是否真证明"无系统 Python"（PATH 净化断言 + frozen exe
> 服务证据）、(4) PySide6 进闭包裁决与允许路径遵守（library_bridge.rs/ac1_bridge.rs
> 零改动）。证据在 verification/M2-AC5/（verification-results.md + raw/ + checkpoint.md）。
