# M2-AC5 raw/ 证据索引

全部日志带 shell/解释器头与 EXIT；构建/验收时间线按下列顺序可完整重放。

行尾注记：三个被测进程直写日志（`cleanstart-probe-stdout.log`、
`cleanstart-ac1-run1/run2-stdout.log`）与两份 tauri build 日志在入库时做了
行尾规范化（CRLF→LF、去行尾空白/EOF 空行）以满足 `git diff --check` 整树
EXIT 0（AC5 硬 gate）；文本行内容未改动。

## 环境与输入

| 文件 | 内容 |
|---|---|
| `environment-record.log` | 工具链版本：git/rustc/cargo/node/npm、构建 venv（Python 3.12.3 + pyinstaller 6.22.3 + PySide6_Essentials 6.11.2 + shiboken6 6.11.2）、tauri-cli 2.12.0、TASK-012-py312 验收 venv |
| `ac1-input-hashes-build1.txt` | 第一次 tauri build 的输入 hash：frontend dist（2 文件）+ sidecar onedir 全树（157 文件，HEAD=71b0e9aa 构建态） |
| `pyinstaller-build-closure-pyside6.log` | PyInstaller 构建（含 PySide6 闭包裁决后的 spec，产出被 tauri build1 打包） |
| `sidecar-entries-smoke.log` | 四个 frozen 入口直接 stdio 冒烟（catalog_loader/host_bridge/core_service/acceptance_bridge 全 EXIT=0） |

## 构建与可复现性（AC1）

| 文件 | 内容 |
|---|---|
| `tauri-build-run1.log` / `tauri-build-run2.log` | 同输入两次 `npx @tauri-apps/cli@2 build`，均 EXIT=0 |
| `ac1-repro-run1-hashes.txt` / `ac1-repro-run2-hashes.txt` | 两次构建的安装包 + host exe hash（不同——链接/打包时间戳，见 verification-results.md 差异解释） |
| `pyinstaller-rebuild-repro.log` | 同输入重跑 PyInstaller |
| `ac1-repro-sidecar-runA.txt` / `-runB.txt` / `-diff.txt` | sidecar 全树两次 hash：`_internal/**` 依赖闭包全同，仅 4 个 frozen 入口壳不同（PyInstaller PKG archive 时间戳） |
| `artifact-inventory-final.txt` | 最终产物清单 hash（安装包 5410e29e…、host exe b32f4d32…、四入口 exe） |

## 三层基线（AC2/AC5，HEAD=eccf88e3）

| 文件 | 结果 |
|---|---|
| `baseline-cargo-test.log` | `cargo test --bin m2rc1-desktop`：38 passed + 1 ignored（34 基线 + 4 新增 packaged 测试），EXIT=0 |
| `baseline-pytest-m2-acceptance.log` | `pytest tests/m2_acceptance -q`：35 passed，EXIT=0 |
| `baseline-vitest-run.log` | `npx vitest run`：31 passed（5 文件），EXIT=0 |

## clean-start 验收（AC3/AC4）

| 文件 | 内容 |
|---|---|
| `cleanstart-final.log` | 终版 gate（20 场景全 PASS，GATE PASS，EXIT=0），被测对象=run2 安装包 |
| `cleanstart-gate.json` | 终版 gate 结构化结果 |
| `cleanstart-run1..5.log` | 迭代过程（run1 PATH 剔除 marker 大小写 bug → run2/3 ac1 lab 目录缺失 → run4 desktop_pid 取样错误 → run5 全绿；保留作 fail→fix→pass 证据） |
| `cleanstart-probe-stdout.log` | packaged probe 模式完整 stdout（13 场景，E-01 digest 一致） |
| `cleanstart-ac1-run1-stdout.log` / `-run2-stdout.log` | packaged ac1 双 launch stdout（exit=0、公告、Qt offscreen） |
| `cleanstart-production-stdout.log` | packaged production 启动 + 优雅关闭 stdout（`[m2rc2-allowlist] production:` 公告、无 spawn 失败） |

口径注记：`cleanstart-run5.log` 与 `cleanstart-final.log` 分别对应安装包 #1（2d1511ee…）与安装包 #2（5410e29e…），均为 GATE PASS。
