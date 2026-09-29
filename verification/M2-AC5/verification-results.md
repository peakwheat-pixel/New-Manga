# M2-AC5 Verification Results

- Owner: ZCode（子 agent 代行实现；用户已全权授权编排链）
- base: `6f79c040`（release commit `82c85c0f`）→ claim `71b0e9aa` → 实现/交付 head 见 [doc/tasks/M2-AC5.md](../../doc/tasks/M2-AC5.md) frontmatter `delivery_head`
- 分支 / worktree：`agent/zcode/M2-AC5-package-clean-start` / `G:/CODEX/New Manga.worktrees/M2-AC5-zcode`
- 口径：本机 host simulation（PATH 剔除 + M2RC1_* 清空模拟无系统 Python 环境）；真正干净 Windows 覆盖属 M2 Release Gate，本 Task NOT_RUN（释放时冻结的裁决点）

## AC 判定总表

| AC | 判定 | 实测 | 证据 |
|---|---|---|---|
| AC1 打包产物可复现 | **PASS**（差异可解释） | `npx @tauri-apps/cli@2 build`（tauri-cli 2.12.0）两次产出 NSIS 安装包（26.62 MiB）；PyInstaller onedir sidecar（4 frozen 入口 + 共享 `_internal`，157 文件）打入安装目录 `resources/core-sidecar/`；同输入重跑：`_internal/**` 依赖闭包 hash 全同，4 个入口壳 + host exe + NSIS 安装包 hash 不同——PyInstaller PKG archive / Rust 链接 / NSIS 打包均内嵌时间戳，属确定性的工具链时间戳差异，输入（frontend dist 2 文件、src 侧闭包、spec）hash 不变 | [raw/ac1-input-hashes-build1.txt](raw/ac1-input-hashes-build1.txt)、[raw/tauri-build-run1.log](raw/tauri-build-run1.log)/[run2](raw/tauri-build-run2.log)、[raw/ac1-repro-run1-hashes.txt](raw/ac1-repro-run1-hashes.txt)/[run2](raw/ac1-repro-run2-hashes.txt)、[raw/ac1-repro-sidecar-diff.txt](raw/ac1-repro-sidecar-diff.txt)、[raw/artifact-inventory-final.txt](raw/artifact-inventory-final.txt)、[raw/pyinstaller-build-closure-pyside6.log](raw/pyinstaller-build-closure-pyside6.log) |
| AC2 packaged spawn fail-closed + dev 零变化 | **PASS** | `StdioCoreChannel::spawn_packaged`：sidecar 缺失 → typed `CORE_SPAWN_FAILED:PACKAGED_SIDECAR_MISSING`，构建 `Command` 之前即失败，无系统 python 回落；packaged 判定 = `M2RC1_PACKAGED=1` 显式，或 `M2RC1_SRC_ROOT` 缺失且 `<exe_dir>/resources/core-sidecar/host_bridge.exe` 存在；dev 路径（`-m`、src cwd、M2RC1_* 契约、expect 消息）字节不变；基线：cargo **38 passed + 1 ignored**（34 基线 + 4 新增 packaged 单元测试）、pytest **35 passed**、vitest **31 passed**，全部 EXIT=0 | [raw/baseline-cargo-test.log](raw/baseline-cargo-test.log)、[raw/baseline-pytest-m2-acceptance.log](raw/baseline-pytest-m2-acceptance.log)、[raw/baseline-vitest-run.log](raw/baseline-vitest-run.log) |
| AC3 clean-start（无系统 Python） | **PASS**（本机模拟口径） | 净化 PATH（剔除 python/venv/conda/WindowsApps 共 10 条目）后 `where python` exit=1；清空 M2RC1_*；NSIS `/S /D=` 静默安装 → probe 模式 13 场景全 PASS（E-01 fetch digest 与 fixture sha 一致=真实 sidecar 往返）→ ac1 双 launch（新 PID 重启、保存/恢复/Reader/导出 digest 全匹配）→ production 真窗口存活 + 优雅关闭 | [raw/cleanstart-final.log](raw/cleanstart-final.log)（GATE PASS, EXIT=0）、[raw/cleanstart-gate.json](raw/cleanstart-gate.json)、[raw/cleanstart-probe-stdout.log](raw/cleanstart-probe-stdout.log)、[raw/cleanstart-ac1-run1-stdout.log](raw/cleanstart-ac1-run1-stdout.log)/[run2](raw/cleanstart-ac1-run2-stdout.log)、[raw/cleanstart-production-stdout.log](raw/cleanstart-production-stdout.log)、[raw/environment-record.log](raw/environment-record.log) |
| AC4 workflow / path / exit | **PASS** | packaged 缺省数据根 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,derived,managed,data}` 首启动自动创建（catalog.sqlite 落盘）；安装目录全树 163 文件三模式跑后 hash 零变化；lab 源 fixture 文件 4 个字节不变；优雅关闭后 tasklist 无 host_bridge/core_service/acceptance_bridge/catalog_loader 残留（python.exe 计数为记录性观察——验收宿主机本身有无关 python 进程，"无系统 Python"由净化 PATH 断言 + frozen exe 服务全流程证明） | [raw/cleanstart-final.log](raw/cleanstart-final.log)（CS-R2/CS-Z1/CS-Z2/CS-Z3 全 PASS） |
| AC5 证据纪律 | **PASS** | 固定 HEAD（每日志头记录）；`git diff --check 6f79c040..HEAD` EXIT=0；`git diff --name-status` 全部落在允许路径（core_bridge.rs / main.rs / tauri.conf.json / packaging/m2ac5/** / doc、verification）；`src/**` Python 零改动；三层基线在交付 head 复跑留痕 | 本表、[raw/README.md](raw/README.md)、checkpoint.md |

## 打包方案（三 channel 覆盖裁决）

- **单 onedir 四入口**（`packaging/m2ac5/core_sidecar.spec`）：`host_bridge`（resource channel）+ `core_service`（production library）+ `acceptance_bridge`（M2-AC1 测试模式）+ `catalog_loader`（launcher 侧 seeding 工具，packaged 环境无系统 python 可跑 dev 的 `python -m` seeding）。四入口共享一个 `_internal` 依赖目录。
- **PySide6 进闭包（与释放时"Qt-free"注记的偏差，实测裁决）**：`bootstrap.acceptance_bridge` 的冻结装配 `assemble_acceptance_core`（与 pytest m2_acceptance 共用）硬依赖 PySide6（QGuiApplication + production Qt 渲染适配器，src/bootstrap/acceptance_bridge.py:171-191 有明示 "Requires PySide6"）。Qt 排除时 frozen acceptance_bridge.exe 启动即 ModuleNotFoundError。因此闭包含 Qt；host_bridge/core_service/catalog_loader 的 import 闭包实测仍为 stdlib + 仓库内包（TASK-012 venv 零 site-packages 模块）。这是 M2-AC1 冻结事实，非打包选择；打包层解决，未触碰 `src/**`。
- **pypdfium2/mobi 不进闭包**：延迟 import（PDF/MOBI 文档 rasters），clean-start 验收场景不触及；PyInstaller warn 留痕，后续完整产品分发再议。
- **library/AC1 channel 的 packaged 复用**：两文件的 `spawn(python_exe, src_root, ...)` 签名不在允许路径内，零改动。packaged 下 main.rs 把参数重指向 frozen exe 与 sidecar 目录：PyInstaller 入口包装脚本忽略 `-m <module>` argv，PYTHONPATH/current_dir 指向 sidecar 目录为惰性。core_bridge.rs（在允许路径内）新增 `spawn_packaged`（无 `-m`、无 src cwd）。

## packaged 判定与数据根

- 判定（main.rs，单元测试覆盖）：显式 `M2RC1_PACKAGED=1`；或 `M2RC1_SRC_ROOT` 缺失且 `<exe_dir>/resources/core-sidecar/host_bridge.exe` 存在（裸启动已安装应用）。dev（M2RC1_* 全在）永不进 packaged 分支。
- 数据根缺省：`%APPDATA%\com.newmanga.m2rc1.desktop\{derived,managed,catalog\catalog.sqlite,data}`（首启动 create_dir_all）；显式 `M2RC1_*` env 仍优先（runner 用同一 env 契约 pin lab 目录）。

## clean-start 三模式结果（终版，被测=安装包 5410e29e…）

| 模式 | 结果 | 关键实测 |
|---|---|---|
| probe（资源通道矩阵） | 13/13 PASS | E-01 issue→fetchAll→sha256 == fixture sha（49363 bytes）；E-05 TTL 过期；E-06 remount；D 系列加固面 |
| ac1（验收环双 launch） | 全 PASS | run1/run2 exit=0；desktop pid 4540→43864、core pid 39180→48160（真实重启）；saved 2 页 completed + mock providers；恢复 Reader 2 页 sha 与保存一致；导出 PNG digest 匹配（1122 bytes） |
| production（真窗口） | 全 PASS | 进程存活 ≥10s；`%APPDATA%` 布局落盘（catalog.sqlite/derived/managed/data）；`[m2rc2-allowlist] production:` 公告；优雅关闭无 spawn 失败；sidecar 进程零残留 |

## 迭代与失败记录（诚实留痕）

- run1：PATH 剔除 marker 大小写 bug（`"WindowsApps" in "...windowsapps"` 恒 False）→ 修复后过。
- run2/run3：ac1 lab root 未预创建（显式 `M2RC2_CATALOG_DB` 路径由 launcher 准备——与 dev 契约一致，host 行为正确）→ runner 补 mkdir 后 ac1 跑通。
- run4：desktop_pid 从 results JSON 取（不存在，恒 0）→ 改为 runner 自己 spawn 的 PID 后全绿。
- 实现期：PyInstaller spec REPO_ROOT 多算一级（`infrastructure` missing）→ 修正；构建 venv 缺 PySide6 → 补装并固定版本。

## NOT_RUN / 遗留

- **真干净 Windows 机器安装**（无任何开发工具链的 physical/VM 覆盖）：NOT_RUN，M2 Release Gate 范围（释放时冻结）。
- **卸载流程**（NSIS uninstaller）未验收：本 Task AC 未要求，未测。
- **完整产品分发闭包**：PDF/MOBI 导入器（pypdfium2/mobi）不在 sidecar 闭包；torch/doctor 等生产 provider 同理。当前闭包覆盖 M2 已冻结的三 channel + seeding 工具。
- **NSIS 安装包 / host exe / 入口壳的时间戳非确定性**：差异已解释；若 Release Gate 要求 bit-for-bit 可复现，需引入 `/Brepro`（Rust）、PyInstaller `--build-name` 固定与 SOURCE_DATE_EPOCH 类机制——登记为候选，不在本 Task 范围。
