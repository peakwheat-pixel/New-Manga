---
task_id: FEA-11-HOST-AUTH-4
adjudicator: ZCode CLI session sess_19824073-883d-4ac4-9182-31dc574c972e / turn turn_2c10b897-aab1-4530-9851-abf2ec02629d
adjudicator_kind: agent
reviewed_head: ab54559068fea7df88edf1b7a3e5ac3b275fa4fc
decision: BLOCKED
cli_exit: 0
---

# Review：FEA-11-HOST-AUTH-4 Release Readiness 裁决

**外层执行元数据**：ZCode CLI session sess_19824073-883d-4ac4-9182-31dc574c972e，turn turn_2c10b897-aab1-4530-9851-abf2ec02629d，trace ee63997e-3186-4bd2-9984-ca272d242674，CLI EXIT 0；branch `main`；审查开始时工作树 clean；reviewed HEAD `ab54559068fea7df88edf1b7a3e5ac3b275fa4fc`。
**裁决结果**：Task 继续保持 `proposed`，不得开始实现。该报告裁定 release readiness，不代表实现验收或 Release Gate 通过。
**原始 CLI JSON**：[`zcode-release-readiness-adjudication-20261112.log`](../../verification/FEA-11-HOST-AUTH-4/logs/zcode-release-readiness-adjudication-20261112.log)。
证据链已闭环。Freeze adjudication 原始 CLI JSON 与落盘正文逐段一致已亲证。以下为最终裁决报告（本会话只读，未修改任何文件/Task/Plan/Status，未提交、未 push）。

---

# FEA-11-HOST-AUTH-4 释放就绪（`ready`）裁决报告

| 项 | 值 |
|---|---|
| 裁决者 | ZCode 新独立会话（Project Adjudicator；未参与 HOST-AUTH-4 任何实现/返修，亦非 scope review `sess_34ac7e48` 或 freeze adjudication `sess_74f2e758` 会话） |
| reviewed_head | **`ab54559068fea7df88edf1b7a3e5ac3b275fa4fc`**（branch `main`；工作树 clean。实测方法：`.git/refs/heads/main` 直读 + harness 启动快照双源一致；plan mode 拦截 Bash，与此前两份报告同一限制） |
| 日期 | 2026-11-12 |
| CLI 信封 / EXIT | 外层 headless CLI：session sess_19824073-883d-4ac4-9182-31dc574c972e；turn turn_2c10b897-aab1-4530-9851-abf2ec02629d；trace ee63997e-3186-4bd2-9984-ca272d242674；CLI EXIT 0。完整记录见 `verification/FEA-11-HOST-AUTH-4/logs/zcode-release-readiness-adjudication-20261112.log` |
| 裁决范围 | 仅 `proposed → ready` 释放门；不代表实现完成或 Release Gate 通过 |

## Verdict：**`BLOCKED`** —— Task 唯一裁定为**保持 `proposed`，不得置 `ready`**，**不得开始实现**

**TL;DR（大白话）**：范围本身已经裁定完、没有争议；卡住的是“释放前必须把全量测试基线在本机真实跑一遍钉下来”这个硬前置——而三次实测的结论是：**这台机器上能跑 pytest 但跑出 16 个没解释的失败，.NET 测试一个都跑不起来（不是测试挂了，是测试的载入进程被 Windows 拒绝）**。所以“有效基线”至今不存在，释放条件没满足。16 个失败不能当没看见，也不能想当然说“都是环境问题”——日志自己写着"Root cause not adjudicated"。

---

## 1. 前一裁决“release 时必须实测重钉全量基线”是否已满足？——**未满足**

Freeze adjudication（`doc/reviews/FEA-11-HOST-AUTH-4-freeze-adjudication-2026-11-12.md` §6 第 5 条）裁定该前置为**强制**，其门禁口径（scope r1 §5）= pytest `failed=0, skipped=10` + .NET 8 项目实际执行的 passed 计数。逐份证据核对：

| 尝试 | HEAD | 结果 | 是否构成有效基线 |
|---|---|---|---|
| pytest attempt1（`logs/pytest-release-baseline-20261112.log`） | `9e53948fc` | **EXIT 1**：1654 passed / 10 skipped / **1881 errors**；全部为 `os.scandir(%TEMP%\pytest-of-49745)` 的 `Win32Exception(5)` tmp_path setup PermissionError；日志自标 `NOT_VALID_BASELINE` | 否——环境性 setup 失败，非测试结果 |
| pytest attempt2（`logs/pytest-release-baseline-workspace-20261112.log`） | `007617285` | **EXIT 1**：3519 passed / 10 skipped / **16 failed** / 11 warnings；日志自标 `NOT_VALID_BASELINE (test failures; do not treat as PASS)`、**"Root cause not adjudicated"**；10 skip 理由全列（docTR×2、manga real×1、openssl×5、registry_readiness×1，与 summary 一致） | 否——`failed=0` 不成立 |
| .NET 8 项目（`logs/dotnet-release-baseline-20261112.log`） | `43df25edf` | 8/8 项目 **EXIT 1**；测试计数 **NOT_RUN**；Testhost `Win32Exception(5)` @ `ProcessManager.OpenProcess` / `SetParentProcessExitCallback`；build 全部成功 | 否——**NOT_RUN 不能写 PASS**，零个测试执行 |
| ZCode 单项目探测（`logs/zcode-dotnet-host-probe-20261112.log`，sess_0216118a） | `9584deb6c` | Appearance.Tests 独立执行：同一 `OpenProcess` 拒绝，**0/0/0**，EXIT 1；未提权、未改安全设置、未绕过 | 否——换执行者复现，证明非项目配置问题 |

**交叉验证**：attempt1 的 1654+1881=3535 与 attempt2 的 3519+16=3535 完全对账——16 个失败正是 attempt2 解除 tmp_path 阻塞后**真正运行出来**的失败，不是收集错误，无法当作环境噪音抹掉。

结论：三次尝试是**合格的取证证据**（定位并绕过了 %TEMP% 阻塞、暴露了必须归因的 16 例、证明 Testhost 在本类进程环境结构性不可运行），但**不是基线**。“实测重钉”这一前置**完全未满足**，且这不是唯一缺口——§6 第 1–4 项落卡工序同样未发生（亲证：卡面 AC 仍为占位草案、`approval` 仍写“scope 未冻结”、`base_commit: null`、owner/reviewer `null`；`REBASELINE_PLAN.md` 当前 DAG 无 HOST-AUTH-4 行、READY 节点为“无”；`STATUS.md` 未登记；Ledger 记 `proposed`）。

## 2. 环境阻塞与产品失败的区分（逐类引用日志，不假设）

| 类别 | 定性 | 依据 |
|---|---|---|
| pytest attempt1 的 1881 errors | **环境阻塞**（确定） | 全部同类 tmp_path `PermissionError`（WinError 5）@ 默认 `%TEMP%`；换 workspace basetemp 后即消失（attempt2 零此类 error） |
| .NET Testhost `OpenProcess(5)` | **环境阻塞**（确定，基础设施层） | 崩溃点在 vstest 基础设施（父进程退出监视回调），**先于任何测试加载**；8 项目 + 单项目探测跨执行者（codex/另一 ZCode 会话）一致复现；构建/还原全成功；0 个测试执行 ⇒ 不存在“产品测试失败”的可能 |
| attempt2 的 16 failed | **未归因，不得假设** | 日志原文"Root cause not adjudicated"。三类：P16 export hook effective-options **3 例**（`test_p16_reader_export.py`）；source-match **1 例**（`OperationalError: no such column custom_rank`——数据库 schema 断言失败，形态上更像真实缺陷或 fixture/schema 漂移）；plugin sandbox **12 例**（统一 `PLUGIN_HOOK_UNAVAILABLE`/输出缺失——该族本身测试进程 ACL/沙箱，在受限进程环境失败的**嫌疑最大但无证据**）。另注意：HOST-AUTH-3 轮（`caaaddc53`，2026-11-10）曾全量 3468/0/10 全绿，其后 main 有多提交——16 例既可能环境差异也可能真实回归，**判据只能是对照归因，不能裁决** |

本裁决不修复、不归因这 16 例（非本次职责，也超出 HOST-AUTH-4 范围）；但只要 `failed≠0` 且未归因，**任何规则都不允许把它们钉为 accepted baseline**——协作协议 §6.1 证据纪律明文“`BLOCKED`/`NOT_RUN` 不得记为通过”，scope r1 §5 明文 `failed=0`。仓库无任何条文允许以 failed≠0 重钉门禁基线。

## 3. 唯一阻塞条件与可执行取证步骤

**唯一阻塞条件**：在释放时 HEAD 上获得**有效全量基线**——pytest `failed=0`（16 例经归因消除或证明为环境性并在可运行环境复跑归零）+ .NET 8 项目**实际执行**的 passed 计数——写入卡面。

**环境边界（如实声明）**：本裁决环境（ZCode plan-mode 会话）与 codex 执行面均无法完成 .NET 侧取证——Testhost 需对父进程（vstest）打开句柄，本类 headless/CLI 进程链被 Windows 以错误 5 拒绝，属进程环境限制，**非改动 Windows ACL 不可解除，而改 ACL 被本裁决红线禁止**。所需外部状态 = **一个普通交互桌面 PowerShell 会话**（用户桌面或 DSH 的非受限执行面）。在授权且工具可用时可执行：

1. 普通桌面 PowerShell 中，以既有 venv 口径重跑 `dotnet test`（8 项目逐项目）+ 全量 pytest（attempt2 的 workspace basetemp 口径），日志带 HEAD/EXIT/shell 头逐次入库 `verification/FEA-11-HOST-AUTH-4/logs/`；
2. 若 16 例在普通环境仍失败 → 由 DSH **另立归因 Task**（P16×3 / source-match custom_rank×1 / plugin-sandbox×12 逐例；不并入 HOST-AUTH-4，不扩其 allowed_paths）；若复跑归零 → 以对照日志登记“环境性”判据证据；
3. 基线有效后，DSH 按 freeze adjudication §6 六项落卡（AC/allowed_paths 替换、R-A/R-B 登记、PLAN 增行 + STATUS 登记、`base_commit`=落卡时实测 HEAD、基线写入卡面）→ release commit 置 `ready`。注意 attempt1/attempt2/8 项目日志各自 HEAD 不同（均为纯证据落盘提交），**最终基线必须绑定落卡后的释放 HEAD 重跑**。

## 4. AC 记录方式（按生命周期）

- **首选（本裁决采纳）：Task 整体保持 `proposed` 原状**。依据协作协议 §4（`proposed` 尚未释放、不得实施）与 freeze adjudication §6 第 6 条（"Task remains `proposed` 直到上述全部完成”）；§4.3 的 AC 标记门禁仅对 `in_review/approved/done/closed_with_limitations` 生效，`proposed` 阶段卡面无需也不应现在落 BLOCKED 标记——阻塞事实由本报告承载。
- 若 DSH 选择先落卡（完成 §6 第 1–4 项范围冻结工序）：AC-4-1…13 落 `- [ ]` 草案，**AC-4-14（门禁 AC）必须落 `- [ ] <<BLOCKED: 全量基线未在可运行环境实测重钉——pytest 16 failed 未归因、.NET Testhost NOT_RUN；解除条件=普通桌面环境 failed=0 实测基线写入卡面>>`**，且 `status` 仍保持 `proposed`。两种路径均**不得置 `ready`**，不得“先释放后假装已闭阻塞”。

## 5. 红线遵守与边界

- 未建议扩大 allowed_paths、未建议修复 P16/Source-Match/plugin-sandbox、未建议修改 Windows ACL/安全设置、未重写 0-pin gate、未降低任何全局测试门槛（门禁 `failed=0` 口径原样维持）。
- 已验证 gates（default/TaskPath check EXIT 0、pins 18/18、API inventory EXIT 0 1/79/6=86）：引自本次任务指令转述；本会话 plan mode 拦截列目录/命令，未逐字节亲证，如实登记——它们不是本次争议点，争议点仅在 pytest 16 failed 与 .NET NOT_RUN。
- 原始日志外部 raw output（workspace `agent-output` 路径 + SHA-256）未修改；本会话零写入、零 commit、零 push。
- **是否可继续实现：否。** Task 为 `proposed`，按协作协议 §4 与卡面 `approval` 原文“scope 未冻结，不得实施”，实现不得开始。

---

## 推荐下一步（基于当前仓库状态）

由 DSH 执行基线取证与落卡释放（`.NET Testhost 取证需普通桌面 PowerShell，为当前 API/CLI 执行面不可达的外部状态`）。可直接转发的指令：

```text
FEA-11-HOST-AUTH-4 释放阻塞处置指令（DSH）：
1. 裁决结果：BLOCKED；Task 维持 proposed，不得置 ready、不得开始实现。
   依据：freeze adjudication §6 第 5 条强制前置未满足——pytest 全量 16 failed 未归因
   （verification/FEA-11-HOST-AUTH-4/logs/pytest-release-baseline-workspace-20261112.log，
   NOT_VALID_BASELINE）+ .NET 8 项目 Testhost OpenProcess(5) 全部 NOT_RUN
   （dotnet-release-baseline-20261112.log + zcode-dotnet-host-probe-20261112.log）；NOT_RUN 不得写 PASS。
2. 取证：在普通交互桌面 PowerShell（非 headless CLI 进程）按既有 venv 口径重跑
   8 项目 dotnet test 与全量 pytest（workspace basetemp 口径），日志带 HEAD/EXIT/shell 头
   逐次入库 verification/FEA-11-HOST-AUTH-4/logs/。
3. 分叉：16 例仍败 → 另立归因 Task（P16×3 / source-match custom_rank×1 / plugin-sandbox×12
   逐例；禁止并入 HOST-AUTH-4、禁止扩其 allowed_paths、禁止修 Windows ACL）；
   复跑归零 → 以对照日志登记环境性判据。
4. 基线有效（pytest failed=0 + .NET 实际执行计数、绑定落卡后释放 HEAD）后，按
   freeze adjudication §6 六项落卡（AC-4-11(b)/AC-4-12 修订、allowed_paths 替换、
   R-A/R-B 登记、REBASELINE_PLAN 增行 + STATUS 登记、base_commit 实测钉定、基线写入卡面），
   再由 release commit 置 ready。在此之前不落卡则 Task 保持 proposed 原状，
   若先落卡则 AC-4-14 落 <<BLOCKED: 全量基线未实测重钉（16 failed 未归因、.NET NOT_RUN）>>。
```

无需我方进一步操作。
