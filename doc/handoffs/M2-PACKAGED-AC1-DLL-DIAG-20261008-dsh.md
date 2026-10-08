---
task_id: M2-PACKAGED-AC1-DLL-DIAG
author: DeepSeek Harness (Owner)
recipient: Codex（非作者 Reviewer / Integrator）
base_commit: 9063c317937b86bed1f6ff3e2f2c5d224dc10553
reviewed_draft_head: f0ad317c77c1ca35f156e8fd8c0d3f73502cdd50
delivery_head: null
status: draft
---

# Handoff：M2-PACKAGED-AC1-DLL-DIAG（r1 返修）

## 交付结果

只读 DLL 诊断的静态部分完成 + Codex Review r1 的有界返修（R1/R2/R3）完成；
执行部分因 DSH 本会话沙箱不可用仍全部 **NOT_RUN**。
`delivery_head` **仍为 null、未固定**：本会话无 git 能力，未提交、未实测 HEAD。
本轮返修起点 = Codex 提交的 draft head **`f0ad317c77c1ca35f156e8fd8c0d3f73502cdd50`**（引用自 Review r1，未用 git 实测）；
新 head 与独立验证由 Codex 记录。

- 已产出/本轮修改：`verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md`、
  `dll-closure-matrix.json`、`probe/run_dll_diag_probe.ps1`（R1/R2 修正）、
  `raw/exec-20261008-dsh-notrun.log`（r1 起原文保留，未改动）、
  `probe/{pe_import_probe.py,README.md}`、本 Handoff、`doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md` 运行记录。
- r1 的原始最终回答与其 NOT_RUN 日志**原文保留**，本轮未改写历史证据。
- 未实施任何修复；未改 Plan/STATUS/总索引；未将本 Task 置 done；未自审；未解除 runner debt。
- AC 对照：AC1 NOT_RUN；AC2 NOT_RUN；AC3 静态完成（含 UNKNOWN）；AC4 PROVEN（日志级）；AC5 部分（未提交、head 未固定）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 git/HEAD/clean/common-dir、diff --check | `git rev-parse` 等 | 本 worktree | NOT_RUN | `raw/exec-20261008-dsh-notrun.log` |
| AC1 installer SHA256 复测 | `Get-FileHash` | 只读证据树 | NOT_RUN（文档三方互证 MATCH） | 同上 |
| AC2 复现 QtGui 导入失败 | 运行 packaged `acceptance_bridge.exe` | 未执行 | NOT_RUN | `probe/run_dll_diag_probe.ps1` 步骤 5（仅自有 lab） |
| AC2 原始失败只读复核 | read `cleanstart-ac1-run1-stdout.log` | HEAD cfb5d2ee | PROVEN（linear 173 处 ImportError，exit=1；**Win32 错误码 UNKNOWN**） | `verification/M2-RUNNER-SNAPSHOT-DEBT/raw/packaged/cleanstart-ac1-run1-stdout.log` |
| AC3 构建树静态闭包枚举 | glob `_internal/**` | 构建产物 target tree | 枚举结果（非加载验证、不推证安装态） | `dll-closure-matrix.json` |
| AC4 环境差量 | read 两份构建日志 | HEAD cfb5d2ee | PROVEN（PS5.1 `-Force` 全量成功；PS7 无 `-Force` 走短路只补 weights，EXIT=0/0.8s） | `raw/sidecar-build.log:548-569`、`raw/sidecar-weights-retry.log` |
| AC5 产品/历史零差量 | `git diff <base> HEAD -- src apps tests packaging` | — | NOT_RUN（工具限制）；人为边界：本轮只改 Task 自己的 REPORT/矩阵/probe/Handoff/Task | `raw/exec-20261008-dsh-notrun.log` |

## r1 返修记录（本轮）

- **R1（P1，已修）**：`probe/run_dll_diag_probe.ps1` 步骤 1 fail-closed——installer 不存在或 SHA256 与固定 pin
  不一致时立即 `throw`（非零退出），不再打印 BLOCKED/DRIFT 后继续执行。
- **R2（P1，已修）**：探针默认 **static-read-only**，**不启动任何 exe**；仅 `-CopyBundle` 时才复制，
  采用 **copy-only（`robocopy /E`，无 `/MIR`、无 PURGE 删除式同步，源树只读）**；复制 exit≥8，或 lab 内
  `acceptance_bridge.exe` / `_internal/PySide6/Qt6Gui.dll` / `Qt6Core.dll` / `pyside6.abi3.dll` /
  `shiboken6.abi3.dll` 缺失或 SHA256 不一致时**立即停止**；只有"复制成功 + 自有 lab 内已核验"才允许步骤 5，
  **绝不**从原证据 bundle 启动。
- **R3（P2，已修）**：`REPORT.md`、`dll-closure-matrix.json`、本 Handoff 同步修正——具体 **Win32 错误码 = UNKNOWN**
  （原日志无 `GetLastError`），删除"Win32 126 / ERROR_MOD_NOT_FOUND 高置信"表述；明确"DLL 未出现在枚举的
  构建树"**不证明**安装树缺失、**不证明**实际加载失败；矩阵新增作用域声明，候选 C1–C5/C8–C10 判定改为
  "在被扫描树中如此 / 安装态与影响 UNKNOWN"。
- 边界遵守：本轮未改 `src/apps/tests/packaging`、未改 Plan/STATUS、未新增框架或依赖、未部署/推送/合并。

## 接收方式

- 分支 `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG`；worktree `G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh`。
- **当前交付处于未提交工作区状态**（DSH 无 git）：Codex 需先 `git status`/`git diff` 确认变更均在
  `verification/M2-PACKAGED-AC1-DLL-DIAG/**`、`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-*.md`、
  `doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md` 内，再决定提交并记录新 head 与独立验证。
- 实跑方式（静态/隔离两种，均只写本 Task `lab/`、`raw/`）：
  1) 静态：`pwsh -NoProfile -File verification/M2-PACKAGED-AC1-DLL-DIAG/probe/run_dll_diag_probe.ps1 -InstallDir '<lab install>'`
  2) 复现：追加 `-CopyBundle`（复制成功且核验后才运行自有 lab 副本）。

## 下一任务建议（必填）

- Task ID / 标题：`M2-PACKAGED-AC1-DLL-CLOSURE-FIX`（**待 Codex 创建并冻结**，本 Task 不创建）
- 推荐 Agent / Reviewer：Antigravity 或 ZCode 实施（打包层）/ 非作者 DSH 或 Qoder Review
- 推荐原因与前置依赖：需先由 probe 结果确定具体缺失/失败模块；前置 = 本诊断结论 + probe 原始日志
- Recovery point：`G:/CODEX/New Manga`，branch/worktree **待 Codex 创建**；base 固定为本次诊断的最终交付 head（待 Codex 记录）
- 允许修改路径（建议）：`packaging/m2ac5/core_sidecar.spec`、`packaging/m2ac5/build_sidecar.ps1`、
  必要时 `packaging/m2ac5/requirements-build.txt`；`src/**` 除非 probe 证明代码级原因（当前无证据），否则不开
- 禁止范围与新增授权条件：不改系统 PATH、不装开发 Qt、不 deploy/push/merge main、不改历史 raw 与 runner 阈值；
  修复范围与依赖变更需用户/Codex 另行冻结
- 交付物：spec/脚本 diff、Qt/PySide6 闭包 build-time 断言、fresh `-Force` 构建日志、固定 installer SHA256
- 验证命令、环境与完成 Gate：fixed-head `-Force` 重建 → installer hash 固定 → 全新 clean-start 26 项完整 Gate
  → 非作者 Review → Codex 集成验证
- 可直接转发给 Agent 的指令：**尚未可派发**——须先由 Codex 实跑 probe 并冻结修复范围与 allowed_paths

## 风险与遗留

- 根因**具体 DLL/符号与 Win32 错误码均 UNKNOWN**；连"依赖解析失败"这一类别也只是**未验证推断（medium）**。
- 未覆盖：安装态 `_internal` 完整性（C12）、运行期 DLL 搜索集（C13）、符号级错配（C14 其余分支）。
- 诊断完成**不**解除 `M2-RUNNER-SNAPSHOT-DEBT` blocking，也**不**代表 packaged 完整 PASS。
- 回退：本 Task 无产品变更，丢弃 verification 与 handoff 文件即可完全回退。

## 实验附录（仅实验任务）

- 数据来源：既有只读证据（`verification/M2-RUNNER-SNAPSHOT-DEBT/**`）与构建产物目录清单；无外部数据、无许可问题。
- 模型/权重：本诊断未加载任何权重；installer SHA256 与 build-fingerprint 一致（未在本会话复测）。
- 硬件/环境：Windows 11 `10.0.26300`；Python 3.12.3；PyInstaller 6.22.3；PySide6_Essentials/shiboken6 均 6.11.2。
- 运行次数：本会话 0 次成功执行（按 r1 指示未再重复权限尝试）。
- 质量判断：静态"文件存在/导入表可解析"只记观测，不记 PASS；无 PASS 声明，无系统 Loader 事实声明。
