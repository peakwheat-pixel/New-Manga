# FINAL-VALIDATION-1 Handoff（终验与发布重建）

- Task: `doc/tasks/FINAL-VALIDATION-1.md`（依赖 CORE-SLIM-2 / RELEASE-PACKAGE-1）
- Branch: `task/FINAL-VALIDATION-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/FINAL-VALIDATION-1`
- Base: `78784afaf`（含 CORE-SLIM-2 集成 `fe346c50a` 与 closeout；卡面 base `d3f081870` 为依赖集成前）
- Delivery head: `97fd10afe`（实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push（按卡禁止）。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 侧车重建（新 spec，无 Qt/无 torch） | **MET**：37.1s 构建；Core 运行时 **186.3 MiB**；Qt 0 / torch 栈 0；冻结能力 smoke **7/7** | `sidecar-build.log`、`sidecar-measure.json`、`capability-smoke.json` |
| AC2 重打包（含 sidecar + 模型策略） | **MET**：base zip **97.75 MB ≤150**；models zip **690.94 MB ≤2 GB**；许可三件套逐字节一致 | `package-facts.json`、`package-summary-base.json`、`package-summary-models.json` |
| AC3 全量回归 | **MET**：test.ps1 102/102；pytest **3F/2739P/9S（0 新增）**；旧壳 vitest **60/60 文件 567/567 用例**；parity `--check` 零漂移 | `scripts-test.log`、`pytest.log`、`vitest.log`、`parity-check.log` |
| AC4 安装 smoke | **MET**：安装→启动→窗口→退出 0→无残留；sidecar_bundled=true（1954 文件/186.3 MiB） | `install-smoke.json`（base）、`install-smoke-models.json`（models 变体） |
| AC5 收尾文档 | **MET**：AD-002 §8/§8.1 S0–S5 完成；DISPLAY-PERF-DECISION-1 关闭；MANUAL_VERIFY 最新版（真机 5 项，NOT_RUN by agent） | `doc/AD-002_*.md`、`doc/tasks/DISPLAY-PERF-DECISION-1.md`、`apps/desktop-avalonia/docs/MANUAL_VERIFY.md` |
| AC6 门禁 | **MET** | check.ps1 PASS；64-hex pin；本 Handoff |

## 2. 本轮改动

| 文件 | 改动 |
|---|---|
| `apps/desktop-avalonia/scripts/package.ps1` | 新增 `-SidecarDir` / `-WithModels` / `-MaxZipMB`；把 Core 侧车按 `<stage>/app/core-sidecar/` 随包（SidecarLocator 第一候选）；VERSION.json 写明模型分发策略；每包输出 `package-manifest.json` + `package-summary-<variant>.json`；体积闸门按变体（150MB / 2048MB） |
| `apps/desktop-avalonia/scripts/install.ps1` | 校验包内 Core 侧车（core_service/host_bridge 必须存在）+ 输出 `sidecar_bundled/sidecar_files/sidecar_bytes/models_bundled/variant` |
| `apps/desktop-avalonia/scripts/install-smoke.ps1` | 记录安装侧车/模型事实（不再硬编码 `sidecar_bundled=false`）；AC 标签改 AC4 |
| `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md` | §8 改「已全部完成」+ §8.1 S0–S5 完成表（状态/集成锚点/终验结论） |
| `doc/tasks/DISPLAY-PERF-DECISION-1.md` | `status: in_review → done`；Closeout Record 补齐（Evidence complete / 资源 preserve / 未关闭项），记录 Lead 终验关闭裁决 |
| `apps/desktop-avalonia/docs/MANUAL_VERIFY.md` | 最新版：被测包名/体积、sidecar 与模型分离说明、安装前置自动验证项、真机 5 项采集方法（保持 NOT_RUN by agent） |

产品源码（`src/**`、`apps/desktop-avalonia/src/**`）零改动；协议/命令语义/Host 契约零改动。

## 3. 体积（终验实测）

| 产物 | zip | 预算 | 解压 | sidecar | models |
|---|---|---|---|---|---|
| base `NewManga-0.1.0-win-x64.zip` | **97.75 MB** | ≤150 MB ✔ | 214.25 MB | 186.31 MiB 内含 | 不含（分离策略，VERSION.json） |
| models `NewManga-0.1.0-win-x64-models.zip` | **690.94 MB** | ≤2 GB ✔ | 856.54 MB | 828.59 MiB 内含 | 642.3 MiB 内含 |

zip sha256：base `8780c8de…819dac`；models `4da9179b…bbd9d`。
许可三件套（两包）：`LICENSE cde3a5c4…f9a88c` / `NOTICE.md 6b3d9bd0…5f57412` / `THIRD_PARTY_LICENSES.md 72927e68…4313ecc`（与仓库根逐字节一致）。

## 4. 回归证据

- pytest：`3 failed, 2739 passed, 9 skipped`（与基线 **3F/2739P/9S** 相同失败集合；0 新增）。
- `apps/desktop-avalonia/scripts/test.ps1`：`TEST PASS (Debug): 102/102 passed, 0 skipped`（新构建无标签 sidecar 副本）。
- 旧壳 vitest（证据保全的 Tauri/React 前端）：`Test Files 60 passed (60)` / `Tests 567 passed (567)`（= 基线）。
- command parity：`extract-command-surface.py --check` → **PASS**（66 commands，零漂移）。
- 安装 smoke（base）：窗口句柄出现 / console 0 / exit 0 / 残留进程 0 / 安装目录已删除 / sidecar_bundled=true / license_copy_ok=true。

## 5. Record Decision / 说明

1. **侧车随包**：发布件按 `<app dir>/core-sidecar` 携带 Core（SidecarLocator 第一候选），避免“装完 app 但 Core 缺失”的不可运行包；`install.ps1` 缺侧车直接 throw。
2. **模型分发策略**：base 包**不含模型**（≤150MB 口径），首次检测为 typed `PROVIDER_NOT_CONFIGURED`（指引放置 `%APPDATA%\com.newmanga.desktop\models` 或换 models 包）；models 包把 642.3 MiB 模型放 `app/core-sidecar/models`（≤2GB 口径）。两包都在 `VERSION.json.models` 明示。
3. **旧壳处置**：旧 Tauri/React 前端仍作为**证据**原位保留并跑 vitest（60/567 不漂移）；发布件走 Avalonia + Core sidecar（AD-002 S5 语义：不再参与发布）。
4. **范围补充**：AC5 要求的 `doc/AD-002_*.md` 与 `doc/tasks/DISPLAY-PERF-DECISION-1.md` 不在本卡 `allowed_paths` 内，但为 AC5 显式要求，已按 AC5 落位；建议 DSH 集成时补卡或在 closeout 确认。`doc/handoffs/**` 同样未列，本文件按 AC6 落位。

## 6. 遗留 / NOT_RUN

- **NOT_RUN（用户真机）**：MANUAL_VERIFY 5 项（Mica 取色、DPR2 400% 像素、工作集峰值 ≤1.5GB、微软拼音 20 字、沉浸阅读 Esc）。
- 安装 smoke 的窗口断言 = 主窗口句柄出现 + 退出码 0 + 无控制台 + 无残留；**书架语义**仍属 MANUAL_VERIFY。
- 未做代码签名 / NSIS / MSIX（不在本卡范围；发布形态为 zip + install.ps1）。
- base 包首次检测会因模型分离而 typed NOT_CONFIGURED（预期行为，已写入包内文档）。
- 需独立 Review（Owner 不得自审）。
