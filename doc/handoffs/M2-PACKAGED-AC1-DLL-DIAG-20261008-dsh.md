---
task_id: M2-PACKAGED-AC1-DLL-DIAG
author: DeepSeek Harness (Owner)
recipient: Codex（非作者 Reviewer / Integrator）
base_commit: 9063c317937b86bed1f6ff3e2f2c5d224dc10553
delivery_head: null
status: draft
---

# Handoff：M2-PACKAGED-AC1-DLL-DIAG

## 交付结果

只读 DLL 诊断的**静态部分**已完成，执行部分因 DSH 本会话沙箱不可用而全部 NOT_RUN。
delivery_head **未能固定**（未提交状态，见"接收方式"）；期望 start_head `24e0ec6e5c6d64a35daad006565919818616b317`。

- 已产出：`verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md`、`dll-closure-matrix.json`、
  `raw/exec-20261008-dsh-notrun.log`、`probe/{run_dll_diag_probe.ps1,pe_import_probe.py,README.md}`、本 Handoff。
- 未实施任何修复；未改 Plan/STATUS/总索引；未将本 Task 置 done；未自审。
- 与 AC 对照：AC1 NOT_RUN（git/hash 实测）；AC2 NOT_RUN（复现）；AC3 静态完成（14 项候选，含 UNKNOWN）；
  AC4 PROVEN（日志级环境差量）；AC5 部分（文件已写、未提交、head 未固定）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 git/HEAD/clean/common-dir | `git rev-parse HEAD` 等 | 本 worktree | NOT_RUN | `raw/exec-20261008-dsh-notrun.log` |
| AC1 installer SHA256 复测 | `Get-FileHash` | 只读证据树 | NOT_RUN（文档三方互证 MATCH） | `raw/exec-20261008-dsh-notrun.log` |
| AC2 复现 QtGui 导入失败 | 运行 packaged `acceptance_bridge.exe` | 未执行 | NOT_RUN | `probe/run_dll_diag_probe.ps1` 步骤 5 |
| AC2 原始失败只读复核 | read `cleanstart-ac1-run1-stdout.log` | HEAD cfb5d2ee | PROVEN（linear 173 处 ImportError，exit=1） | `verification/M2-RUNNER-SNAPSHOT-DEBT/raw/packaged/cleanstart-ac1-run1-stdout.log` |
| AC3 bundle 闭包枚举 | glob `_internal/**` | 构建产物 target tree | PROVEN（Qt6Core/Qt6Gui/pyside6.abi3/shiboken6.abi3/MSVC 齐全；icuin*/d3dcompiler_47 缺席） | `dll-closure-matrix.json` |
| AC4 环境差量 | read 两份构建日志 | HEAD cfb5d2ee | PROVEN（PS5.1 `-Force` 全量成功；PS7 无 `-Force` 走短路只补 weights，EXIT=0/0.8s） | `raw/sidecar-build.log:548-569`、`raw/sidecar-weights-retry.log` |
| AC5 产品/历史零差量 | `git diff --check`、`git diff <base> HEAD -- src apps tests packaging` | — | NOT_RUN（工具限制）；人为边界：本会话只写 verification/** 与 doc/** | `raw/exec-20261008-dsh-notrun.log` |

## 接收方式

- 分支 `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG`；worktree `G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh`。
- **当前交付处于未提交工作区状态**（DSH 无 git）：Codex 需先 `git status`/`git diff` 核对变更均在
  `verification/M2-PACKAGED-AC1-DLL-DIAG/**`、`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-*.md`、
  `doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md` 内，再决定由谁提交并写入 delivery_head。
- 复现/取证据：执行 `probe/run_dll_diag_probe.ps1`（仅写本 Task `lab/`、`raw/`）。
  关键前置：installer hash 门通过；若用 NSIS 安装树请传 `-InstallDir`。

## 下一任务建议（必填）

- Task ID / 标题：`M2-PACKAGED-AC1-DLL-CLOSURE-FIX`（**待 Codex 创建并冻结**，本 Task 不创建）
- 推荐 Agent / Reviewer：Antigravity 或 ZCode 实施（打包层）/ 非作者 DSH 或 Qoder Review
- 推荐原因与前置依赖：需先由 probe 结果确定具体缺失/失败模块；前置 = 本诊断结论 + probe 原始日志
- Recovery point：`G:/CODEX/New Manga`，branch/worktree **待 Codex 创建**；base 固定为本次诊断 delivery_head
- 允许修改路径（建议）：`packaging/m2ac5/core_sidecar.spec`、`packaging/m2ac5/build_sidecar.ps1`、
  必要时 `packaging/m2ac5/requirements-build.txt`；`src/**` 除非 probe 证明代码级原因，否则不开
- 禁止范围与新增授权条件：不改系统 PATH、不装开发 Qt、不 deploy/push/merge main、
  不修改历史 raw 与 runner 阈值；修复范围与依赖变更需用户/Codex 另行冻结
- 交付物：spec/脚本 diff、Qt/PySide6 闭包 build-time 断言、fresh `-Force` 构建日志、固定 installer SHA256
- 验证命令、环境与完成 Gate：fixed-head `-Force` 重建 → installer hash 固定 → 全新 clean-start 26 项完整 Gate
  → 非作者 Review → Codex 集成验证
- 可直接转发给 Agent 的指令：**尚未可派发**——须先由 Codex 实跑 probe 并冻结修复范围与 allowed_paths

## 风险与遗留

- 根因**具体 DLL/符号仍 UNKNOWN**；类别结论为"packaged 进程内 `PySide6.QtGui` 依赖链存在 Win32 126 未解析模块"。
- 未覆盖：安装态 `_internal` 完整性（C12）、运行期 DLL 搜索集（C13）、符号级错配（C14 其余分支）。
- 诊断完成**不**解除 `M2-RUNNER-SNAPSHOT-DEBT` blocking，也**不**代表 packaged 完整 PASS。
- 回退：本 Task 无产品变更，删除/丢弃 verification 与 handoff 文件即可完全回退。

## 实验附录（仅实验任务）

- 数据来源：既有只读证据（`verification/M2-RUNNER-SNAPSHOT-DEBT/**`）与构建产物目录清单；无外部数据、无许可问题。
- 模型/权重：本诊断未加载任何权重；installer SHA256 与 build-fingerprint 一致（未在本会话复测）。
- 硬件/环境：Windows 11 `10.0.26300`；Python 3.12.3；PyInstaller 6.22.3；PySide6_Essentials/shiboken6 均 6.11.2。
- 运行次数：本会话 0 次成功执行（3 次 shell 尝试均在启动前失败）。
- 质量判断：静态"文件存在/导入表可解析"只记 PROVEN_PROVENANCE，不记 PASS；无 PASS 声明。
