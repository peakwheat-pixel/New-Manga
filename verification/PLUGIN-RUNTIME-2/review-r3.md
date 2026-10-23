---
task_id: PLUGIN-RUNTIME-2
reviewer: reviewer-settings-a
author: reviewer-settings-a
base_commit: d28b7a8b1449e5f4790470bcbbba10abcf3ab388
reviewed_head: 2ea97edd6e65260d1276e7b1e505a036dc612f80
decision: approved
---

# Review：PLUGIN-RUNTIME-2 r3

**approved**。此前三项导出缺陷均已修复，真实 Core 回归通过；在本次记录范围内未发现新的实质问题。批准仅绑定上方固定实现提交，不代替 Codex 的证据登记、集成验证和 Task closeout。

## 范围与依据

沿用 r1/r2 的 Task/架构/冻结范围、独立性和 trusted-code 边界，复核 `55af609b0..2ea97edd6` 的代码/测试修订，结合 r1/r2 已审查的完整调用链。新 head 在允许路径内；无新增 IPC/UI/Schema/依赖。开始时 main、共享 `.git`，源文件/测试与 reviewed_head 无 diff，六个 P04 未跟踪诊断文件保留；主 Agent 同步 Task/Handoff/pin 的治理修改不改变固定生产内容。

Reviewer 非实现者，仅写本报告，不改生产、测试或其他治理文件，不提交，不执行 push/merge/reset/stash。

## Findings disposition

| 既有 finding | 结论 | 固定 head 证据与实际检查 |
|---|---|---|
| r1 R1：TXT→JSON 覆盖未影响输出 | fixed | `src/bootstrap/core_service.py:2951` 延迟生成文本；`src/application/export/service.py:274` 在最终参数后调用 factory。真实 StartExport JSON 文件解析并核对 page_id |
| r1 R2：运行历史仍保存原参数 | fixed | P16ExportRuntime.start 在创建 job/accept/history 前 prepare_request；真实 ZIP 压缩方式、accept、history 和重建 Runtime 后 history 均检查最终参数一致 |
| r2 R3：空 options 覆盖绕过必需键校验 | fixed | `src/application/export/service.py:258` 在原请求具有 options 时拒绝空覆盖，apply_input 记录 plugin_error 并保留原值。真实 StartExport txt→{} 回归检查 completed、非空输出、accept/history 保持 txt、错误审计存在 |

没有新 Findings。`hooks_prepared` 避免 before 重复调用；三种真实导出场景均检查 before/after 总共 2 个 hook_invoked。after 返回 status=failed 被忽略，最终仍 completed。旧式直接 ExportService 使用空 options 的兼容路径保留，不因此使真实 P16 请求丢失必需字段。

## Architecture

Architecture：PASS。修复将 before_export 放到派生文本内容与冻结历史之前，且实际输出和持久化快照使用同一个准备后的请求；内部 callback/标记没有扩展 IPC。只允许冻结的 options/script/direction/format_options；身份、图像、路径授权、Lock/Revision、发布策略不交给插件覆盖。detect/OCR 与编码/子进程隔离实现没有在本轮修订，沿用 r1 已审结论；没有把旧架构作为验收依据。

## Verification

Windows PowerShell，`C:\Python314\python.exe`，Python 3.14.6，UTF-8。下列为本 Reviewer 实际执行，不把实现者 103 passed 当作本轮独立执行数。

| 场景 | 命令/步骤 | 结果 |
|---|---|---|
| 真实 Core P16 完整测试文件，含三项插件导出回归 | 下方 pytest | PASS：22 passed / 0 skipped |
| 固定源实现一致性 | `git diff 2ea97edd6e65260d1276e7b1e505a036dc612f80 -- src tests` | PASS：无输出，运行前后均核对 |
| 当前治理指针 | `pwsh -NoProfile -File tools/governance/check.ps1` | 最终 PASS，3 warnings；首次 FAIL 的 r2 文档 pin 已由主 Agent 同步 |
| r1/r2 其余定向回归 | 本轮未重复，见历史报告的独立 81/49 passed | NOT_RUN（本轮）；相关实现本轮未变化 |
| GUI、真实模型、全量 pytest、打包 | 未执行 | NOT_RUN，无此类新证据 |

Verification：PASS（本次复审范围）。三项缺陷均有真实入口回归；没有 skipped。临时目录保留在 workspace，由 Codex 资源 manifest 处置。

### 原始运行日志

```text
SHELL=PowerShell; PYTHON=C:\Python314\python.exe; VERSION=3.14.6; UTF8=-X utf8
REVIEWED_HEAD=2ea97edd6e65260d1276e7b1e505a036dc612f80
COMMAND=python -X utf8 -m pytest tests/core/test_p16_reader_export.py -q --tb=short --basetemp='G:/CODEX/New Manga.workspace/temp/PLUGIN-RUNTIME-2/review-r3'
......................                                                   [100%]
22 passed in 4.48s
EXIT=0

COMMAND=pwsh -NoProfile -File tools/governance/check.ps1
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\PLUGIN-RUNTIME-2.md
WARN: 存在 3 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3157 bytes / 31 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5445 bytes / 51 lines
FAIL: Evidence SHA-256 不匹配：verification/PLUGIN-RUNTIME-2/review-r2.md
Governance check: FAIL (1 errors, 3 warnings)
WRAPPER_EXIT=0（同一次 shell 随后执行 git diff；此处检查器自身退出码未单独捕获）
DISPOSITION=主 Agent 同步最终 review-r2.md SHA-256 的 SOURCE_PIN；Reviewer 未修改 Task

COMMAND=pwsh -NoProfile -File tools/governance/check.ps1
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\PLUGIN-RUNTIME-2.md
WARN: 存在 3 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3157 bytes / 31 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5445 bytes / 51 lines
Governance check: PASS (3 warnings)
EXIT=0
```

首次治理检查的 `Governance check: FAIL` 为判定依据；封装 shell 同一调用随后继续执行 git diff，工具汇总 exit 0 不表示该次检查器通过。后一次独立调用已得到 PASS。

## 结论与下一步

**approved**，固定 head 可交 Codex 进入集成验证与 closeout，不在本报告直接关闭 Task。r1/r2 仍保留为发现与修订历史，不再作为当前 head 的拒绝结论。

推荐下一步：Codex 继续当前 PLUGIN-RUNTIME-2，登记本 r3 Review 的真实 hash、核对 Handoff/Task 的 delivery_head 与证据 pin，执行治理及必要集成验证后更新 Task/STATUS/Plan；不得把批准解释为新产品范围、push 或资源清理授权。当前无新的已释放产品 Task，无需下一步产品实施操作。

未检查：GUI、真实模型质量、全量 pytest 与打包；本轮没有重复执行不变的 OCR timeout/crash 矩阵。
剩余风险：继承 trusted-code 非 OS 沙箱边界，以及前期接受的 stdin 阻塞/进程树终止限制；本次未扩大该边界。
