---
task_id: FEA-15-PIN-BASIS-ENFORCE-1
reviewer: ZCode CLI 0.17.1, fresh read-only session
session: sess_fb32a1da-f389-4e0a-b1dc-226bfd412284
decision_turn: turn_219eedb3-126b-44eb-b3ea-1e2cd2bcd144
reviewed_head: bf377705783da10eebcf6585316178984ef663d8
base_commit: bfae0b9bd6a9b85a9a546d2adda0b684783ddb24
cli_exit: 0
decision: APPROVED_WITH_LIMITATIONS
---

# AC2/AC3 follow-up independent Review

## 来源与范围

ZCode 在 2026-11-11T21:47:00.9716108Z 对 validation clone 的 HEAD bf377705783da10eebcf6585316178984ef663d8 作只读复核。仓外 CLI 收据记录了精确 session、turn 与 CLI_EXIT=0；ZCode response 因 plan mode 未给出自身 session 字段，本文 ID 取自同一 CLI receipt。完整收据保存在 verification/FEA-15-PIN-BASIS-ENFORCE-1/ac2ac3-followup-review-zcode-cli-20261112.jsonl。

Reviewer 未参与实现或返修。审查对比固定为 R0 bfae0b9bd6a9b85a9a546d2adda0b684783ddb24 至 reviewed HEAD bf377705783da10eebcf6585316178984ef663d8。ZCode 报告工作树 clean、差异全集 12 项且均在 Task allowed_paths 内；冻结 pins、verify_pins.ps1、.gitattributes、冻结契约及 task_ledger.py 未改。

## 结论

ZCode 返回 APPROVED_WITH_LIMITATIONS：P0=0，P1=3（含一项证据流程项），实现与测试质量在 AC2/AC3 范围内成立，但 reviewed HEAD 上证据链未闭合。该 Review 不 adjudicate AC4、不释放 AC5、不批准集成或 Task 关闭。

## Findings

### P1-1：legacy 二进制 blob 判定变化需测试

Checker 将旧六列表的 Git blob 获取从 cat-file 输出重定向改为 BaseStream。Reviewer 认为 PNG 等二进制 blob 的旧行为可能从 MISMATCH 翻转为 PASS，属于需核验影响面的既有 PASS/FAIL 变化；其所见 legacy 负向/正向覆盖没有二进制 pin 判别用例。Reviewer 建议加入 legacy 二进制用例或在 AC4/AC5 记录影响范围，再复跑四个历史 TaskPath。该项针对 reviewed HEAD 的判断，不改写为已通过。

### P1-2：当时验证证据未入库、Task 卡仍陈旧

Review 时 Task 卡 AC2/AC3 行仍显示实现进行中、测试未执行，AC2/AC3 测试与 gates artifacts 未入库，README 尚无该 checkpoint。ZCode 要求先提交验证证据、更新卡面并完成 pinbackfill，之后才可将 AC2/AC3 标为 MET。

### P1-3：正向测试未验证完整 checker 结果

Reviewer 指出 assert_basis_passes 只检查三个 evidence 错误串缺失，没有断言进程 EXIT=0、Governance check: PASS 或 error 总数为零。若 fixture 因其它门禁失败或引入无关回归，合法 basis 仍可能被误记为通过。

### P2 限制

- P2-4：四个历史 TaskPath 尚未在候选 checker 上实测；保留为 AC5 NOT_RUN。
- P2-5：跨盘 Get-RepoPathInfo 行为缺少显式处理；Reviewer 记录当时 17 个双环境用例通过。
- P2-6：commit 对象不存在与 commit 不含路径使用相同诊断码，失败关闭仍成立。
- P2-7：全量 governance pytest 在较早候选 a2a3401eb EXIT=1，3 个 test_residual_runtime_identity 失败；未修改基线 dd6372420 同样复现。该 Review 未在 bf377 HEAD 运行全量套件。
- P2-8：autocrlf=false 时 C04b/C17 两个 pin mismatch、autocrlf=true 时 16 个 mismatch 与 AC1c 既有 EOL 现象一致；18-pin 门禁留在 AC5。
- P2-9：测试夹具临时目录位于仓库内；中断时可能遗留 ignored 临时目录。

## Review 后补充事实（不属于本次 reviewed HEAD）

实现者随后在实现 worktree 提交 7eefb54dc5ca74ddf9cc5459eb40fb10769a44e1：增加候选与 R0 对同一 PNG 修改后工作树字节的 legacy fallback 对照，并让正向夹具要求完整 checker EXIT=0 与 Governance check: PASS。该提交在 clean HEAD 的专项结果为 18 passed、9 subtests、EXIT=0，日志为 ac2ac3-p1-p3-remediation-committed.log。随后证据已提交到主仓库 a9ca17988e292a7bc391cacb09c3a860a2a02986，post-evidence gates 全部 EXIT=0，详见 main-post-evidence-gates-a9ca17988.log。

以上为独立于 reviewed HEAD 的后续事实，不代表本 reviewer 对 7eef 或 AC4 v2 4ed7f32b3ce9104ecee11aad593bde222055a0df 的 Review。当前代码与 AC4 v2 必须由新的 fresh ZCode Review 复核。