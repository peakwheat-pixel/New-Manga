---
task_id: M2-PACKAGED-AC1-DLL-DIAG
author: DeepSeek Harness (Owner)
recipient: Codex（非作者 Reviewer / Integrator）
base_commit: 9063c317937b86bed1f6ff3e2f2c5d224dc10553
reviewed_draft_head: f0ad317c77c1ca35f156e8fd8c0d3f73502cdd50
codex_evidence_head: a84980c394ac9c5380c87e097e081065818aa265
delivery_head: 229c6c371d34234b65bbdd67fff73f341c60930f
status: in_review
---

# Handoff：M2-PACKAGED-AC1-DLL-DIAG（r2：本地隔离执行证据整合）

## 交付结果

本轮把 **Codex 本机隔离执行证据**（执行者 Codex；DSH 无 shell，仅只读核对）整合进报告：
**根因已 PROVEN 并限定范围** = 包内 `_internal/icuuc.dll` 遮蔽 System32 同名 ICU，且仅导出 `_78` 后缀符号，
缺少 `Qt6Core.dll` 需要的 20 个无后缀 ICU 符号 → Qt6Core 原生加载 WinError 127 → `import PySide6.QtGui` 失败。
**不是** 26 项 Gate PASS，**不是**安装修复，**未**推定其它构建/环境。
DSH `delivery_head` 仍为 null（无 git 能力，不猜）；证据 head 固定为 `a84980c394ac9c5380c87e097e081065818aa265`；
报告提交 commit 由 Codex 完成后补记。

- 本轮修改：`verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md`（r2 版）、
  `verification/M2-PACKAGED-AC1-DLL-DIAG/dll-closure-matrix.json`（r2）、
  `doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md`（AC 记录 + status=in_review）、本 Handoff。
- 未改动：所有 `raw/**` 原始日志、`local-evidence.md`、Codex 支持 probe（`run_local_probe.py`/`loader_probe.py`/
  `symbol_probe.py`/`run_icu_control.py`）、产品源码与 packaging、其它历史证据；未新增依赖；未启动修复。
- 外层 wrapper EXIT0 **不**等于 bridge PASS；实测既没有 decode：原 case bridge **EXIT1 / 0.8s**（QtGui 错误复现），
  自有反事实 case bridge **EXIT0 / 0.42s**。

## 验证证据

| AC/场景 | 实际命令/步骤（执行者） | 环境与被测 head | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 输入固定 | installer + 5 exe hash 实测（Codex） | HEAD 13804524 系列 | MATCH | `local-evidence.md:4`；DSH 侧 NOT_RUN |
| AC2 有界复现 | 自有 lab 同 hash 副本运行桥（Codex） | purged PATH、EOF、lab data root | 原 case **EXIT1/0.8s** + QtGui 错误 | `raw/icu-control-result.json`、两份 icu-control 日志 |
| AC2 反事实 | 同副本仅改名包内 icuuc（字节保留） | 同上 | **EXIT0/0.42s** | `raw/icu-control-owned_icu_renamed.log` |
| AC3 native 加载 | `loader_probe.py`（Codex） | HEAD 36765f4b | 同 hash Qt6Core/QtGui WinError **127**；shiboken/icuuc 可加载 | `raw/loader-probe.log` |
| AC3 系统 ICU 对照 | 预加载 System32/icuuc.dll（Codex） | HEAD 5cd31dda，独立进程 | 同 hash Qt6Core/QtGui **可加载** | `raw/loader-system-icu-control.log` |
| AC3 符号对照 | `symbol_probe.py`（Codex） | HEAD 13804524，pefile 2024.8.26 | Qt6Core→icuuc `imported:20`，20 个无后缀符号缺失 | `raw/symbol-probe-full-exports.json` |
| AC3 来源/版本 | 三树 hash + FileVersion（Codex） | lab/installed/build_env | icuuc 三树一致（`39aec884…`），Qt 6.11.2.0 | `raw/binary-version-origin.json` |
| AC4 差量 | 原 full build/weights 日志（历史） | source_head cfb5d2ee | PS5.1 `-Force` 成功 + weights EXIT1；PS7 短路补 weights EXIT0 | `raw/sidecar-build.log`、`raw/sidecar-weights-retry.log` |
| AC5 Review/集成 | — | — | **待 Codex**；DSH 不自审、不 done | 本 Handoff |

## DSH 独立核对与局限（不盲抄父总结）

- 已只读核对 4 个支持 probe 的**代码逻辑**与**原始数据**：`run_icu_control.py` 的断言/hash 门/env 隔离/字节保留式改名成立。
- 局限：反事实是"移除包内 ICU"而非提供可用 ICU78；只 2 case、单次运行；`loader_probe.py` 宿主是 T1.1.1 python.exe
  而非冻结进程；预加载 System32 ICU 是构造对照；symbol probe 为静态匹配、不解析 forwarder；
  **delay-import 扫描未独立验证 → 已从根因链中排除**（DSH 自建 `probe/pe_import_probe.py` 的 delay 解析同理排除）。
- 勘误：`raw/symbol-probe.json` 的"QtGui→QtCore 缺 64 符号"系 pefile 默认 8192 导出上限伪差，
  已按 ERR-1 记录并**禁止**当根因；初次 wrapper 路径预检失败/缺 PATHEXT 的失败记录保留为 ERR-2。

## 接收方式

- 分支 `agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG`；worktree `G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh`。
- 本会话无 git：请 Codex 先 `git status`/`git diff` 确认变更仅在
  `verification/M2-PACKAGED-AC1-DLL-DIAG/{REPORT.md,dll-closure-matrix.json}`、
  `doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md`、`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-*.md` 内，再提交并补记 head。
- Task 已置 `in_review`（AC1–AC4 由 Codex 实测达成；AC5 待 Review/集成）。**禁止**由 DSH 自行 done。

## 下一任务建议（必填）

- Task ID / 标题：`M2-PACKAGED-AC1-ICU-ISOLATION-FIX`（**未创建/未释放**，待用户与 Codex 冻结）
- 推荐 Agent / Reviewer：Antigravity 或 ZCode 实施；非作者 Reviewer = DeepSeek Harness
- 推荐原因与前置依赖：根因已 PROVEN 且有反事实对照；前置 = 本 Task 通过 Codex 非作者 Review 与文档集成
- Recovery point：`G:/CODEX/New Manga`；branch/worktree **待 Codex 创建**；base 固定为本次诊断交付 head（由 Codex 记录）
- 允许修改路径（建议）：`packaging/m2ac5/**` + 该 Task 自己的 `verification/**`
- 禁止范围与新增授权条件：不改系统 PATH、不装开发 Qt、不改历史 raw、不 deploy/push/merge main；
  **不得全局删除 ICU78**（其它依赖需求未核实）；改依赖版本/共享契约须先交用户
- 交付物：packaging 层隔离方案 diff、fresh build 日志、固定 installer SHA、完整 26 项 Gate 结果
- 验证命令、环境与完成 Gate：fresh Sidecar + NSIS → 固定 installer SHA → 全新 clean-start **完整 26 项**
  → 非作者 Review → Codex 集成验证
- 可直接转发给 Agent 的指令：**尚未可派发**——须先由用户/Codex 冻结范围与 allowed_paths

## 风险与遗留

- 范围限定：根因结论仅对**本固定 installer 产物 + 本机**成立，不外推。
- UNKNOWN：原 Gate 运行的 Win32 错误码（无 GetLastError）；installed 树未做改名对照；
  其它仍需 ICU78 的依赖未核实；完整 26 项 Gate 未跑。
- 诊断完成**不**解除 `M2-RUNNER-SNAPSHOT-DEBT` blocking；修复须另开 Task 并 fresh 验收。
- 回退：本 Task 无产品变更，丢弃报告/矩阵/Handoff 变更即可。

## 实验附录（仅实验任务）

- 数据来源：本 Task `raw/**` 与 Codex 支持 probe 产物；无外部数据、无许可问题。
- 权限/边界：支持 probe 只写自有 `lab/`、`raw/`；产品、原 bundle、installed tree 均未修改（E4 hash 一致佐证）。
- 运行次数：反事实对照 1 轮 2 case；native 加载对照 2 组；静态符号 1 次（full exports）。
- 质量判断：诊断级证据充分；**不**替代系统 Loader 全量事实、**不**替代 26 项 Gate。

## 固定报告与审查接收（Codex追加）

实际delivery_head=229c6c371d34234b65bbdd67fff73f341c60930f；证据head=a84980c3，支持代码/执行head见raw头。
非作者Review=doc/reviews/M2-PACKAGED-AC1-DLL-DIAG-229c6c37-codex-r3.md，approved。
独立verify_local_evidence实际EXIT0；自有Python内存compile与diff检查通过，无产品差量。
已接收报告/矩阵及边界，等待Codex文档集成；diag done不等于runner解锁。
下一步候选M2-PACKAGED-AC1-ICU-ISOLATION-FIX，Owner=Antigravity，Reviewer=DSH，Integrator=Codex，未释放。
实际新base与完整实施指令将在主仓库verification/M2-PACKAGED-AC1-DLL-DIAG/NEXT_IMPLEMENTATION.md登记；
branch/worktree待Codex创建并实测，不猜路径。不得自动开始packaging或依赖修改。
