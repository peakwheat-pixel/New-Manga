---
task_id: FEA-11
reviewer: 独立上下文子 agent（fresh subagent；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator）
base_commit: 89d54ef4
reviewed_head: ac4b6fabc
decision: changes_requested
---

# Review：FEA-11（r5）

> 说明：本报告由 DSH 依据 r5 Reviewer（fresh subagent，未参与实现/r1–r4）返回的完整报告正文落盘（2026-11-05）。Reviewer 审查 `89d54ef4..ac4b6fabc`；审查期间 DSH 提交 `fceb0766f`（r4 落盘）与 `ac4b6fabc`（r5 residual）；`ac4b` 的 delta 已逐行复核；只读仓库、未 commit、工作树 clean；产物在 `workspace/FEA-11/review-r5/`。

## 结论
**changes_requested**（对 `ac4b6fabc`；对 `fceb0766f` 亦同）。
- **P0=1**：P0-1 Host 自签 HostAuthorization 未变；`FEA-11-HOST-AUTH-1` 仍 proposed、未获用户显式接受 limitation，阻断 done。
- **P1=1**：**P1-04R**——`source_get_sync_capabilities` 被移入不可达路径（HostLocal channel → `HostLocalAsync` → `Grants.HandleCommandAsync` default throw；新 handler 在仅 HostControl 调用的 `SourceOperationCompletionAsync`，且先要求 operation_id，`{}` payload 直接 INVALID_REQUEST），以及 `reason` 返回 `"CORE_CAPABILITY_MISSING"` 越出 §5.2 闭集。两项在 `103cff986` 已修，但 r6 需另立 head 复审（sync-over-async、证据 head）。
- **P2**：r4 的 11 项中 3 项 fixed（P2-05/07/10）、其余 partial/not-fixed；N-01 fixed；N-03/N-04 not-fixed；N-05/N-06 partial；另有测试卫生/证据件新发现。

## 关键验证
- `pytest tests/fea11` **40 passed**（ac4b，3.76s，EXIT 0）；`pytest tests` **3051/10/0**（fceb，231.72s，EXIT 0）；check PASS（14 非终态、PLAN 80%）；pins 18/18；task ledger 512/512；C-17 零 diff。
- `test_source_command_parity.py`：14/14 名称、channel split 正确；局限：纯静态文本解析、循环无 else、不验证 dispatch。
- P2-09：normal `MarkCommitted` 保存整条 operation JSON（含完整 commit）；**recovery 崩溃窗只回填 commit_digest、不写 CommitReceiptJson**（partially）。
- 交付件：changed-files 80/80 与 diff 一致、含 r4/AC4/parity/r5 log；但 `delivery_head` 仍 fceb、EV 仍 ed5、r6 log 未入 manifest；Handoff 门禁标题/STATUS 下一步/PLAN 行尾/AC-MATRIX 状态行仍旧口径。

## AC 判定
AC11-2 MET（仅 Core seam）；其余 9 项 PARTIAL（判定诚实）。**done 不成立**；**closed_with_limitations 当前不成立**（前置：P1-04R、P0-1 用户接受或 HOST-AUTH-1 完成、LINEAGE-1 完成或 PLAN 明改、交付件在最终 HEAD 重生成并对齐、补 capability/CommitReceipt/folder/IPC flake 测试）。

## 处置建议
1. capability handler 回 HostLocal、reason 改 `capability_missing`、补 fake-Core 测试；
2. RecoverAsync 同时写 CommitReceiptJson（normal+recovery 断言）；
3. 证据件在最终 HEAD 重生成并对齐（EV/Manifests/Handoff/STATUS/AC-MATRIX/PLAN/Task card/ledger）；
4. 测试卫生（parity else、folder limitation 登记、AC11-1 消费者口径）；
5. P0-1/LINEAGE-1 前置；`103cff986` 后另立 head 复审。
