# M2-AC5 raw/ 证据索引

构建/验收时间线按下列顺序可完整重放。**日志头/EXIT 如实清单（r1 P3-1 更正）**：
r1 起新产生的日志（`r1-*`、`f1-*`、`f2-*`、`cleanstart-r1-final.log`、
`r1-library-probe.log`）全部带 shell/解释器头与 EXIT；r0 时期日志中
`tauri-build-run1/run2.log` 与 `cleanstart-final.log`、`cleanstart-run5.log`
**无命令头/无 EXIT 行**（tauri build 经后台任务重定向捕获、gate EXIT 打印在
控制台而非文件内）——按原样保留作证据，exit 状态以 gate JSON 与
verification-results.md 的复跑记录为准。

行尾注记：三个被测进程直写日志（`cleanstart-probe-stdout.log`、
`cleanstart-ac1-run1/run2-stdout.log`）与两份 tauri build 日志在入库时做了
行尾规范化（CRLF→LF、去行尾空白/EOF 空行）以满足 `git diff --check` 整树
EXIT 0（AC5 硬 gate）；文本行内容未改动。

## 环境与输入

| 文件 | 内容 |
|---|---|
| `environment-record.log` | 工具链版本：git/rustc/cargo/node/npm、构建 venv（Python 3.12.3 + pyinstaller 6.22.3 + PySide6_Essentials 6.11.2 + shiboken6 6.11.2）、tauri-cli 2.12.0、TASK-012-py312 验收 venv |
| `ac1-input-hashes-build1.txt` | 第一次 tauri build 的输入 hash：frontend dist（2 文件）+ sidecar onedir 全树（161 文件，HEAD=71b0e9aa 构建态） |
| `pyinstaller-build-closure-pyside6.log` | PyInstaller 构建（含 PySide6 闭包裁决后的 spec，产出被 tauri build1 打包） |
| `sidecar-entries-smoke.log` | 四个 frozen 入口直接 stdio 冒烟（catalog_loader/host_bridge/core_service/acceptance_bridge 全 EXIT=0） |

## 构建与可复现性（AC1）

| 文件 | 内容 |
|---|---|
| `tauri-build-run1.log` / `tauri-build-run2.log` | 同输入两次 `npx @tauri-apps/cli@2 build`，均 EXIT=0（EXIT 记录于 verification-results.md 与 checkpoint.md；日志文件本身无头——见顶部注记） |
| `ac1-repro-run1-hashes.txt` / `ac1-repro-run2-hashes.txt` | 两次构建的安装包 + host exe hash（不同——链接/打包时间戳，见 verification-results.md 差异解释） |
| `pyinstaller-rebuild-repro.log` | 同输入重跑 PyInstaller |
| `ac1-repro-sidecar-runA.txt` / `-runB.txt` / `-diff.txt` | sidecar 全树（161 文件）两次 hash：**156 相同 + 5 差异**（4 个 frozen 入口 exe + `_internal/base_library.zip`——stdlib zip 内嵌时间戳，与入口壳同类工具链时间戳差异；r1 P2-1 勘误：此前"157 文件全同"表述不准确） |
| `artifact-inventory-final.txt` | 最终产物清单 hash（安装包 5410e29e…、host exe b32f4d32…、四入口 exe） |

## 三层基线（AC2/AC5）

| 文件 | 结果 |
|---|---|
| `baseline-cargo-test.log` | r0：`cargo test --bin m2rc1-desktop`：38 passed + 1 ignored（34 基线 + 4 新增 packaged 测试），EXIT=0 |
| `baseline-pytest-m2-acceptance.log` | r0：`pytest tests/m2_acceptance -q`：35 passed，EXIT=0 |
| `baseline-vitest-run.log` | r0：`npx vitest run`：31 passed（5 文件），EXIT=0 |
| `r1-baseline-cargo-test.log` / `r1-baseline-pytest-m2-acceptance.log` / `r1-baseline-vitest-run.log` | r1 闭合后复跑：38+1 / 35 / 31，全 EXIT=0（r1 闭合只改 packaging/m2ac5 runner 与文档，预期不变） |

## clean-start 验收（AC3/AC4）

| 文件 | 内容 |
|---|---|
| `cleanstart-r1-final.log` | **r1 终版 gate（25/25 场景全 PASS，GATE PASS，EXIT=0）**：新增 CS-E3（无空格 guard）、CS-L1/L2/L3（安装态 library probe）、CS-Z4（宿主真实 %APPDATA% 字节不变）；被测=同一安装包 `5410e29e…`（r0 未重建复用） |
| `cleanstart-gate.json` | r1 终版 gate 结构化结果（含 installer sha256 与 appdata_isolation 记录） |
| `r1-library-probe.log` | P2-2 安装态 stdio probe 原始输出（core.ping/ListBooks/core.shutdown 往返） |
| `cleanstart-final.log` | r0 终版 gate（20/20，被测=同 sha 安装包；无头日志——见顶部注记） |
| `cleanstart-run1..5.log` | r0 迭代过程（run1 PATH 剔除 marker 大小写 bug → run2/3 ac1 lab 目录缺失 → run4 desktop_pid 取样错误 → run5 全绿；保留作 fail→fix→pass 证据） |
| `cleanstart-probe-stdout.log` | packaged probe 模式完整 stdout（13 场景，E-01 digest 一致） |
| `cleanstart-ac1-run1-stdout.log` / `-run2-stdout.log` | packaged ac1 双 launch stdout（exit=0、公告、Qt offscreen；run1 含 Qt 字体缺失告警——披露 H-③） |
| `cleanstart-production-stdout.log` | packaged production 启动 + 优雅关闭 stdout |

归属注记：以上三模式 stdout 日志当前内容为 **r1 gate 运行**产出（runner 每次运行
覆盖写出；r0 运行的同名版本保留在 r0 交付 commit `783fc74f` 的 git 历史中）。
两轮被测安装包 sha256 相同，r1 版本为最新证据。

## 范围审计（AC5/P2-5+F）

| 文件 | 内容 |
|---|---|
| `f1-scope-audit.log` | r0 交付范围原始审计：`git diff --name-status 6f79c040..783fc74f`、`git diff --check 6f79c040..783fc74f; echo EXIT=$?`、`git status --porcelain` |
| `f2-final-scope-audit.log` | r1 闭合后终版范围审计（`6f79c040..<r1-tip>`；commit B 入库） |

口径注记：r0 与 r1 的 clean-start gate 被测安装包 sha256 相同
（`5410e29e118d24ae28192c241a3fc7a8c3e6f5bcc4def38d7c588e900be61336`）。
