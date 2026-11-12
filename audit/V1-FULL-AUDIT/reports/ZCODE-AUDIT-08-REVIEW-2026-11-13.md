# AUDIT-08 独立交付审查报告

- verdict：`ACCEPT`
- reviewed_head：`fb1f6086b6436f6c471d1bd52e97873588450813`（`main`）
- reviewer：ZCode，独立只读上下文；本次未参与 AUDIT-08 实施或返修
- ZCode session：`sess_c08b6522-2689-4b26-bf73-68c5ca867ee6`
- CLI：`0.17.1`；`--mode plan --json --locale zh-CN`；EXIT 0
- findings：0 P0 / 0 P1 / 0 P2 / 2 P3
- 原始响应：`evidence/zcode-audit08-review-20261113.json`，SHA-256=`104D00B257EA3B6B9DB3FA3698897CD49C6A4E20DB0CF17855AA2D8AA7970472`；dispatch log=`logs/zcode-audit08-review-dispatch-20261113.log`

## 结论

ZCode 接受 AUDIT-08 的有限专项结论。报告覆盖边界总体诚实；`284 passed / 0 skipped / EXIT 0` 及缺陷复现 probe 的 EXIT 0 均未被写成产品 PASS；`SEG-B-PROBES-002` 的 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`、`pre_restore_packages=1` 与报告结论及源码路径一致。多文件部分写明确保持为未实测静态推断。

## Findings

### P3-1：原始条款“异常中断”未单独列映射

- 位置：`reports/AUDIT-08-SQLITE-PERSISTENCE-2026-11-13.md` 的覆盖矩阵；原始条款见 `source/ORIGINAL-USER-AUDIT-INSTRUCTIONS-2026-10-24.txt` AUDIT-08。
- 说明：`tests/core/test_connection_ownership.py` 的 error-path rollback 用例提供了有限相关证据，但原矩阵没有独立列出“异常中断”，容易让读者漏认这一原始检查点。
- 影响：表述遗漏，不改变专项 FAIL 结论；不能由此推断所有业务事务异常都已注入验证。
- 建议：矩阵中显式列“异常中断”，说明已测的并发 error-path `rollback()` 及仍未覆盖的逐点 Python exception / 磁盘异常注入。
- 处置：已在返修版报告中加入独立“异常中断”行，并限定其为 error-path rollback 的有限覆盖。

### P3-2：post-pinbackfill 门禁日志未列入 Canonical Evidence

- 位置：`doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md` 中 AUDIT08 Canonical Evidence 行；head `fb1f6086b` 内 `logs/audit08-post-pinbackfill-*.log` 与 default runner JSON 已提交，但未 pin。
- 说明：首轮 TaskPath/pins/API 日志 pin 于报告前的门禁 head，Task Canonical Evidence 完成 pinbackfill 后，四项门禁又在 `0742a572eba783d9ff3b7a064850f0d932c98823` 上运行。AUDIT-11 的阶段记录曾将 post-pinbackfill gate 日志纳入 pin 表，因此这批 AUDIT-08 输出也应在下一次 Canonical Evidence 更新时纳入。
- 影响：当前 Task `in_progress` 且 Canonical Evidence 状态仍为 `pending`，不是本阶段结论的阻断项；属于证据索引完整性建议。
- 建议：将 default log/JSON、TaskPath、pins、API 四项输出加入下一次 Task pinbackfill，并复跑治理检查。
- 处置：计划在返修版 pinbackfill 中加入这 5 个文件（default log 与 JSON、TaskPath/pins/API logs），并复跑 default、TaskPath、verify_pins、API inventory。

## 审查范围及限制

ZCode 对照了原始 AUDIT-08 清单、Task/状态/映射文件、专项报告、测试源码、日志/JSON、相关 SQLite 实现和 AUDIT08 Canonical Evidence 行。确认最终测试批次 generated HEAD=`5802af0a2cf812b3a977f58c5b7c161bba2c9199`，包含已提交的 synthetic probe 源；`284 passed in 23.53s`、0 skipped、EXIT 0；nmbak finding probe 的四个观测值与日志一致。default gate 的内容及 TaskPath/pins/API 的 0742a572 输出也与记录相符。

ZCode 未运行测试或任何命令，且未在其只读 plan 环境独立复算 raw Git blob SHA-256；该限制在 ZCode 原始响应中明确披露。主审计会话已在证据 pinbackfill 时使用 `git cat-file blob <commit>:<path>` 对当时 15 条 AUDIT08 Canonical Evidence 行按 raw Git blob bytes 计算 SHA-256；后续新增 pin 也将以同一方法核算，TaskPath check 作为机械复核。

本 Review 接受的是 AUDIT-08 报告与证据的有限性和诚实度，不是产品发布准入，也不关闭全审 Task。`SEG-B-PROBES-002` 仍需另行释放产品修复 Task。
