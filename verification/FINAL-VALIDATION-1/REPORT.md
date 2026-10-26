# FINAL-VALIDATION-1 报告：终验与发布重建

- Task: `doc/tasks/FINAL-VALIDATION-1.md`（依赖 CORE-SLIM-2、RELEASE-PACKAGE-1）
- Branch/Worktree: `task/FINAL-VALIDATION-1` / `G:/CODEX/New Manga.workspace/worktrees/FINAL-VALIDATION-1`
- Base: `78784afaf`（= CORE-SLIM-2 集成 `fe346c50a` + closeout `78784afaf`；卡面 base `d3f081870` 为依赖集成前，实际基线取含依赖的最新 HEAD）
- 未 push（按卡禁止）。

## 0. 结论（AC 逐条）

| AC | 判定 | 一句话证据 |
|---|---|---|
| AC1 侧车重建 | **MET** | 新 spec 重建 37.1s；整包 828.6 MiB / 不含模型 **186.3 MiB**；Qt 0、torch 栈 0；冻结能力 smoke **7/7 PASS** |
| AC2 重打包 | **MET** | base zip **97.75 MB（≤150）**、models zip **690.94 MB（≤2048）**；sidecar 随包；许可三件套逐字节一致 |
| AC3 全量回归 | **MET** | test.ps1 **102/102**；pytest **3F/2739P/9S（0 新增）**；旧壳 vitest **60/60 文件 567/567 用例**；command parity `--check` **PASS（66 命令零漂移）** |
| AC4 安装 smoke | **MET** | base 包安装→启动→窗口（handle 10683238）→退出 code 0→无残留（0 进程/0 安装目录）；sidecar_bundled=true（1954 文件/186.3MiB） |
| AC5 收尾文档 | **MET** | AD-002 §8 标 S0–S5 全部完成；DISPLAY-PERF-DECISION-1 关闭；MANUAL_VERIFY.md 最新版（真机 5 项，NOT_RUN by agent） |
| AC6 门禁 | **MET** | check.ps1 PASS；64-hex pin；Handoff |

## 1. AC1 侧车重建（新 spec：无 Qt / 无 torch）

- 构建：`packaging/m2ac5/build_sidecar.ps1 -PythonExe <build venv> -Force`，HEAD=`78784afaf`，PyInstaller 6.22.3，
  **exit=0（37.1s）**；spec 的 closure 断言输出：`onnxruntime (663 pure modules) + onnxruntime_pybind11_state.pyd + DirectML.dll`。
- 体积（`verification/FINAL-VALIDATION-1/sidecar-measure.json`）：

| 项 | 值 |
|---|---|
| 整包 | 828.6 MiB（1,964 文件） |
| **Core 运行时（不含 models）** | **186.3 MiB**（`_internal` 142.5 + `python/` 41.9 + 5 exe 1.95） |
| models | 642.3 MiB（RT-DETR-v2 ONNX 163.7 + SFX YOLO 38.9 + manga-ocr ONNX 439.6） |
| 闭包内 Qt / torch 栈 | **0 / 0**（`qtArtifacts=[]`、`torchArtifacts=[]`） |
| 共享 `.pyc` | 859 个（noarchive 去重，5 entry 共用） |
| 5 个 entry exe | host_bridge/core_service/acceptance_bridge/catalog_loader/sfx_detect_probe 各 ~0.39 MiB |

- 启动/协议 smoke（无标签副本，规避 AC11 Low-IL）：`capability-smoke.json` **7/7 PASS** ——
  catalog_loader 播种、core_service `core.ping`（protocol 2.3）、acceptance_bridge
  seed_fixture（真实导入）/run_pipeline（渲染）/reader_pages/export_page、sfx_detect_probe 启动（ORT+DML 在冻结 exe 内可用）。

## 2. AC2 重打包（含 Core 侧车 + 模型分发策略）

`apps/desktop-avalonia/scripts/package.ps1` 扩展（本轮改动）：

- 新增 `-SidecarDir`（默认 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar`）与 `-WithModels`；
  侧车按 `<stage>/app/core-sidecar/` 布局随包（`SidecarLocator` 的第一候选 `<app dir>/core-sidecar`）。
- `install.ps1` 现在**校验包内 Core 侧车**（core_service/host_bridge 必须存在）并输出
  `sidecar_bundled/sidecar_files/sidecar_bytes/models_bundled`；`install-smoke.ps1` 记录同样字段。
- `VERSION.json.models` 写明模型分发策略：base 包 `separated`（模型不入包；首次检测 typed
  `PROVIDER_NOT_CONFIGURED`，模型放 `%APPDATA%\com.newmanga.desktop\models` 或改用 models 包）；
  models 包 `bundled`（`app/core-sidecar/models` 随包）。

| 产物 | zip 体积 | 预算 | 解压体积 | sidecar | models | 许可三件套 |
|---|---|---|---|---|---|---|
| `NewManga-0.1.0-win-x64.zip`（base） | **97.75 MB** | ≤150 MB ✔ | 214.25 MB | 186.31 MiB（含） | 不含（分离） | 逐字节一致 ✔ |
| `NewManga-0.1.0-win-x64-models.zip` | **690.94 MB** | ≤2 GB ✔ | 856.54 MB | 828.59 MiB（含） | 642.3 MiB（含） | 逐字节一致 ✔ |

许可哈希（两包一致）：`LICENSE cde3a5c4…f9a88c` / `NOTICE.md 6b3d9bd0…5f57412` /
`THIRD_PARTY_LICENSES.md 72927e68…4313ecc`（与仓库根逐字节比对，脚本内失败即 throw）。
每包另有 `package-manifest.json`（全文件 sha256 清单）与 `package-summary-{base,models}.json`。

## 3. AC3 全量回归

| 门 | 结果 | 证据 |
|---|---|---|
| pytest（vs 基线 3F/2739P/9S） | **3 failed, 2739 passed, 9 skipped**（失败集合与基线一致：2×`test_detection_manga_real` weights-missing 环境 + 1×`test_workbench_viewmodel` 基线 flaky） | `pytest.log` |
| Avalonia 单命令 | `TEST PASS (Debug): 102/102 passed, 0 skipped` | `scripts-test.log` |
| 旧壳 vitest（基线 60 文件/567 用例） | **Test Files 60 passed (60) / Tests 567 passed (567)** | `vitest.log` |
| command parity `--check` | **PASS**：production command surface matches snapshot（66 commands，零漂移） | `parity-check.log` |
| 依赖安装可复跑 | `npm install --no-audit --no-fund` exit=0（140 packages，9.9s） | `vitest-install.log` |

## 4. AC4 安装 smoke

`install-smoke.ps1`（本轮更新：校验/记录随包 sidecar 与 models）：

- base 包：`install → 从安装目录启动 → 窗口句柄出现（10683238）→ 无控制台窗口（0）→ 退出码 0 →
  uninstall → 残留进程 0、安装目录已删除`；`sidecar_bundled=true`（1954 文件/186.3 MiB）、`license_copy_ok=true`。
- models 包：同脚本复跑（见 `install-smoke-models.json`；含模型 sidecar 828.6 MiB）。

## 5. AC5 收尾文档

- `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md`：§8 标题改「已全部完成」，新增 §8.1 S0–S5 完成表（各阶段状态 + 集成锚点 + 终验结论）。
- `doc/tasks/DISPLAY-PERF-DECISION-1.md`：`status: done`，Closeout Record 补齐（Evidence complete / 资源 preserve / 未关闭项）；
  关闭依据：Lead 2026-10-27 终验收口裁决（该卡为证据/设计型 Task，AC1–AC16 全 MET；独立技术复核如需另行指派）。
- `apps/desktop-avalonia/docs/MANUAL_VERIFY.md`：最新版（被测包名/体积、sidecar 与模型分离说明、安装前置自动验证项、
  真机 5 项采集方法；状态保持 **NOT_RUN by agent**，数字必须由用户真机填写）。

## 6. 范围与遗留

- 未改协议/命令语义/Host 契约；未删除能力；未 push/gc/prune；未伪造安装结果。
- 本轮代码改动仅 `apps/desktop-avalonia/scripts/{package,install,install-smoke}.ps1` + 文档 + 证据；产品源码零改动。
- **NOT_RUN（需用户真机）**：MANUAL_VERIFY 5 项（Mica、DPR2 400%、工作集峰值、微软拼音 20 字、沉浸 Esc）。
- **风险/说明**：
  1. 安装 smoke 的窗口断言为“主窗口句柄出现 + 退出码 0 + 无控制台 + 无残留”，书架语义仍属 MANUAL_VERIFY；
  2. 侧车从 repo 构建目录打包（未做代码签名）；签名/NSIS/MSIX 不在本卡范围；
  3. base 包不含模型（策略见 VERSION.json），首次检测按预期 typed NOT_CONFIGURED；
  4. `doc/AD-002_*.md` 与 `doc/tasks/DISPLAY-PERF-DECISION-1.md` 不在本卡 `allowed_paths` 内，但 AC5 显式要求修改；已按 AC5 落位并在 Handoff 标注，建议 DSH 补卡或在集成时确认。
