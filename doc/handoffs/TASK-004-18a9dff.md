---
task_id: TASK-004
author: ZCode
recipient: Codex（转 DeepSeek Harness 独立 Review）
base_commit: 8addf1b7d87c07f51d3acf8275030375be08adda
delivery_head: 18a9dff83fc43a4c5f1fcd7be1aa0a7fe850cf96
status: in_review
---

# Handoff：TASK-004（Windows 运行环境与打包路线验证）

实现 head：`18a9dff`（本 Handoff 在其后以文档提交追加，遵守「Handoff 引用之前实现 head」约定）。
提交列表（自派单 starting_head `27b3948` 起）：

| commit | 说明 |
|---|---|
| `7c80110` | docs(TASK-004): 基线核验通过，ready → in_progress |
| `18a9dff` | exp(TASK-004): 全部实验脚本、原始日志与研究报告（reviewed_head） |

变更路径（全部在 allowed_paths 内）：`experiments/TASK-004/**`、`verification/TASK-004/**`、`doc/research/TASK-004.md`、`doc/tasks/TASK-004.md`（状态与记录）、本 Handoff。未触碰生产 `src/`、根依赖、Schema、AGENTS、其他 Task；冻结范围零变化（`git status` 全程仅出现允许路径）。

## 交付结果与 AC 对照

- **AC1 隔离目录版本验证**：**满足**。三个隔离 venv（Python 3.12.3 / 3.14.0 / 3.12.3-Essentials）实测版本矩阵，OS/架构/命令/退出码全部记录于 [doc/research/TASK-004.md](../research/TASK-004.md) §2～§4 与 [verification/TASK-004](../../verification/TASK-004/env_report.txt)。
- **AC2 无重型 AI 依赖的最小 QML 窗口 + onedir**：**部分满足，干净环境项按约定 BLOCKED**。QML 真实窗口启动/关闭在 3.12 与 3.14 均 PASS；PyInstaller onedir 构建、Qt DLL/plugin 完整性、正常与「无开发 PATH」启动均 PASS；干净 Windows 机器不可得，已明确记录 **BLOCKED**（research §4.4，含解除条件），未用开发机结果替代。
- **AC3 Core/ML 分离、资源路径与锁定版本建议**：**已交付（Proposal）**。research §5：主推 Python 3.12 + PySide6 6.11.2（Essentials 已验证）+ pytest 9.1.1 + PyInstaller 6.22.3；可选 ML 依赖全部 Provider extras 延迟导入。待 Codex 审核后方可作工程输入。
- **AC4 Handoff 与独立 Review**：本 Handoff 即交付；状态已置 `in_review`，等待 DeepSeek Harness 非作者 Review 与 Codex 集成。

## 验证证据

完整结果总表见 [doc/research/TASK-004.md](../research/TASK-004.md) §3（E1～E18）。摘要：

| AC/场景 | 实际命令（摘要） | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 依赖安装 ×2 组合 | `pip install PySide6 pytest pyinstaller`（清华镜像） | venv py312.3 / py314.0；head `18a9dff` | PASS | `verification/TASK-004/logs/pip312.log`、pip 后台日志 |
| QML 真实窗口启动→1.5s→关闭 | `python qml_min/main.py` | 同上；head `18a9dff` | PASS ×2 | `logs/qml_smoke.log` |
| Qt DLL/plugin/QML 模块完整性 | `check_qt_files.py --layout pyside6` | 两 venv；head `18a9dff` | PASS ×2 | `logs/qt_assets_pytest.log` |
| pytest 冒烟（3 项 each） | `pytest test_smoke.py -v` | 两 venv；head `18a9dff` | PASS（3 passed ×2） | `logs/qt_assets_pytest.log` |
| PyInstaller onedir 构建 | `pyinstaller --onedir --add-data main.qml` | py312；head `18a9dff` | PASS（28 s） | `logs/pyinstaller_build.log` |
| onedir 资产完整性 | `check_qt_files.py --layout onedir` | dist 产物 397 MB/2,824 文件 | PASS（missing=[]） | `logs/onedir_run.log` |
| onedir 启动（正常 + 无开发 PATH 模拟） | `task004_smoke.exe`；`cmd /c set PATH=system32+Windows` | dist 产物；head `18a9dff` | PASS ×2（frozen=true，窗口 visible，rc=0） | `logs/onedir_run.log` |
| Essentials-only QML 支撑 | `PySide6_Essentials`+pytest 安装、QML、pytest | venv py312-ess；head `18a9dff` | PASS ×2 | `logs/essentials_only.log` |
| 干净 Windows 环境（另一台机器/VM） | — | — | **BLOCKED**（解除条件见 research §4.4） | — |
| PyInstaller × Py3.14；体积裁剪；Win10 矩阵；安装器/更新；内嵌字体 | — | — | NOT_RUN ×5（理由见 research §3 E13～E17） | — |
| D07 性能指标（冷启动 P95 等） | — | — | N/A（无生产应用） | — |

无 FAIL 项；无以 Mock 冒充模型质量的表述（本 Task 未涉及任何模型）。

## 接收方式

- 分支 / worktree：`agent/zcode/TASK-004-windows-packaging` / `G:/CODEX/New Manga.worktrees/TASK-004-zcode`；reviewed_head 固定 `18a9dff`。
- 复现：[experiments/TASK-004/README.md](../../experiments/TASK-004/README.md)；venv 与构建产物在仓库外 `%LOCALAPPDATA%\Temp\task004-zcode\`（与 TASK-003 隔离，Review 时不得清理他人环境，本目录仅属 TASK-004）。
- Reviewer 建议核对：① `18a9dff` diff 全量阅读；② 重跑 QML 冒烟与 pytest（命令见 README）；③ 核对 research §3 结果表与原始日志一致性；④ 核对 BLOCKED 判定是否符合 TASK-004 AC 与 D07 §82；⑤ allowed_paths 与冻结范围。

## 风险与遗留

1. E12 干净环境 BLOCKED：发布 Gate（D07 §82/§106）前必须由用户/Codex 提供干净 Windows 11（及 best-effort Win10）环境重验。
2. research §5 全部建议为 Proposal，未经 Codex 审核不构成选型；TASK-005 落地 requirements 时需按 §5.1 重验并生成 lock 文件。
3. `experiments/TASK-004/__pycache__/*.pyc` 曾被首个实验提交误收，已 amend 移除（`4a8b250` → `18a9dff`）；`4a8b250` 不作为审查对象。
4. 本机 Python 3.12.3/3.14.0 与 PySide6 6.11.2 的组合升级路径见 research §7。

## 实验附录

- 数据来源：无外部数据集；全部程序为自研最小脚本（本仓库 `experiments/TASK-004/`），无版权与许可问题，无数据 Hash 需求。
- 模型/权重：未安装、未运行任何 AI 模型（符合任务禁止范围）。
- Provider/Runtime：Python 3.12.3 / 3.14.0（官方 CPython，py launcher 分发）；PyPI 官方 wheel，经清华镜像分发；PySide6 6.11.2 / shiboken6 6.11.2 / pytest 9.1.1 / PyInstaller 6.22.3 / hooks-contrib 2026.7。
- 硬件：Ryzen 9 7950X3D / 32 GB / Windows 11 专业版 Build 26200 x64；无 GPU 依赖项被验证。
- 参数与次数：QML 冒烟窗口保持 1500 ms 自动关闭；每实验单次运行；构建 1 次。
- 网络策略：仅 pip 经 HTTPS 访问镜像源；实验程序零网络行为。
- 失败样例：无；唯一计划内失败路径为干净环境 BLOCKED（非执行失败）。
- 限制：单机单 OS；结论不外推至 Win10/Server/ARM64；体积与启动性能未优化未测。
