# Handoff — DIAG-M2-REGIONLESS-LOCK-CHANGED-001

- Owner: DeepSeek Harness
- Task: doc/tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md（`ready / M2_REGIONLESS_LOCK_CHANGED_DIAGNOSTIC_RELEASED`）
- Base / pull point: `5789b30b37dfbf79d9bca707b5fdaaa562ada707`
- Branch / worktree: `agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001`
  / `G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh`
- **Delivery head: NONE（无提交）** — 本会话既不能执行 shell 也不能写 worktree
- Status: **BLOCKED**（AC1/AC2/AC5）+ **STATIC**（AC3/AC4）
- Reviewer（非作者）: Antigravity；Integrator: Codex

## 1. 阻塞原因（原始错误）

```
pwsh: Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)
write(worktree): [sandbox: file access denied under workspace-write mode]
escalation: requires approval, but no approval channel is available
```

- 复现次数：4 次直连 + 2 次子代理独立探针，错误逐字节相同，与 `workdir` 无关；
- 沙箱在**命令执行前**准备阶段失败 ⇒ 所有验证命令 `NOT_RUN`，非 `FAIL`；
- worktree 在 session workspace `G:\CODEX\New Manga` 之外 ⇒ 写入被拒；
- `read`/`grep`/`glob` 对 worktree 可读（已实证），故可完成静态诊断。

## 2. 交付物状态

| 交付物 | 状态 |
|---|---|
| `doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md` | 全文已产出，**由集成方落盘** |
| `verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py` | 全文已产出，**未落盘、未执行** |
| 先红日志 | **NOT_RUN**（不存在） |
| `git diff --check` | **NOT_RUN** |
| 既有受影响测试复跑 | **NOT_RUN** |
| Handoff（本文件） | 全文已产出，**由集成方落盘** |

## 3. 静态根因（一句话）

`_backfill_detected_regions`（`src/application/tasks/service.py:921-946`）只重绑
`region_id`、不重绑 `target_id`；`ocr` 的 `StepRun.input_refs` 仍来自 Page target
⇒ `expected_current_revision_id = input_refs.get("region") = None`，而 Region 已有
detect 原子写入的首版 ⇒ `RegionStepWriter._persist`
（`src/infrastructure/providers/step_writes.py:219-231`）抛 `LockBlocked`
（`error_code="LOCK_CHANGED"`）⇒ run `COMPLETED_WITH_FAILURES`。

失败比较点**不是** `catalog.commit_step` 的锁分支（同源比较，恒等）。

## 4. 判别性预测（执行者须逐条核对）

见 `doc/research/...` §3 与 `reproduce.py` 的 8 条 checks；核心是
`ocr.error_code == "LOCK_CHANGED"` 且 `error_detail` 含 `expected None`、
`ocr.target_id == page_id`、`region_ids` 存在但 `region_revisions == 1`。

## 5. 修复 Task 的最小范围（本 Task 未实施）

- 文件：`src/application/tasks/service.py`，函数：`_backfill_detected_regions`；
- 同时重绑 `target_id=primary` 与 `region_id=primary`；**不改 `unit_id`**；
- 不得改动多 Region 只绑 primary 的既有语义；不得改动 catalog/契约/schema；
- 半修（只改 snapshot 来源）会把 `LOCK_CHANGED` 变成 `TARGET_NOT_FOUND`，必须用 N1 固定。

## 6. 回归 / 负向矩阵

回归 R0–R5、负向 N1–N7、持久化风险 R-a–R-c：见 `doc/research/...` §5.4。

## 7. 未验证项（诚实披露）

- 本 Task 全部运行时证据均未采集；`$py` 未执行、版本未复验；
- git HEAD 仅以工作树元数据文件读取确认为 `5789b30b`，未用 `git rev-parse`；
- 任务文件在 base `5789b30b` 的 worktree 中**不存在**（仅存在于 `main`@`acddebcb`），
  请 Codex 确认 release 文档提交与 worktree base 的一致性。

## 8. 建议下一步

1. Codex 修复沙箱（或为 Owner 提供可用执行与审批通道），把本 Handoff 的三份文件
   落盘并 import 提交，固定 delivery head，再让 Owner 按原验证命令补 AC1/AC2/AC5；
2. 同时另立**修复 Task**（Owner=Antigravity/ZCode，Reviewer=非作者），范围限定
   §5；或先让 Antigravity 以本报告的静态结论做非作者复核（可复核性充分：全部证据为
   `path:line`）。
