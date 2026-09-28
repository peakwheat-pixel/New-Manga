# M2-AC1 DSH r3 Review disposition（Owner=ZCode）

- Review report: [M2-AC1-cd261f70-dsh-r3.md](../../doc/reviews/M2-AC1-cd261f70-dsh-r3.md)（DeepSeek Harness 非作者，静态 Review，`decision: approved` 条件批准；r3 新增 P2×1、P3×3、P4×4）
- r3 被审 head：`cd261f70`；本轮返修提交：见 branch tip（本文件所在提交及其前驱）

## 逐条处置

| ID | 级别 | disposition | 处置说明 |
|---|---|---|---|
| R3-01 | P2（唯一必改） | **fixed** | `doc/tasks/M2-AC1.md` 全仓回归行与 Handoff 全仓行改为如实陈述：`2 failed, 1320 passed, 5 skipped, EXIT 1`——失败集中于 Legacy QML 行点击测试（Task 禁改域 `tests/ui_shell/**`，与本 Task 19 路径零交集）；零改动主 checkout @1347a67c 同时刻复现同 2 失败（base 对照）；历史 1322-passed 日志取回命令 `git show a74ce105:verification/M2-AC1/pytest-full-suite.log` 写入两处表格与 NOTE.md。 |
| R3-02 | P3 | **fixed** | 场景计数三处统一为终版 **45**（Task gate 行 / Handoff AC6 行）；NOTE.md 修正为 **36（旧存档）vs 45（终版）**。 |
| R3-03 | P3 | **fixed** | Handoff AC3 行不再引用 r1 旧 PID 数值，改为引用场景 id（`restart-*-pid-differs`）并注明"数值随每次运行不同"，附终版运行数值作示例。 |
| R3-04 | P3（治理） | **fixed** | 补 [review-dsh-r2-disposition.md](review-dsh-r2-disposition.md)（R2-01..07 逐条 fixed/deferred/open + 证据指针）；本文件为 r3 处置。 |
| R3-05 | P4 | **fixed** | `vitest.log` 在干净 tip 真正重采（r2 轮该日志的重定向缺陷导致未落盘，r3 指正准确）：头部 `worktree HEAD=cd261f70` + dirty 计数，正文 19 passed，`# EXIT: 0`。四日志均含 interpreter/toolchain 头 + HEAD 行 + `# EXIT:`；其中 vitest/pytest-full-suite 另含 clean 计数。cargo 与 pytest-m2-acceptance 捕获于干净 tip `521d96ca`（其后至 tip 仅文档/日志变化，被测代码相同），vitest 重采于 `cd261f70`（R4-03 措辞修正）。 |
| R3-06 | P4 | **fixed** | Handoff §接收方式 head 演进链补全：aaf21a13 → 7d157858（r1 被审）→ 5a59ddfe（r1 返修）→ d8c1173b（r2 被审）→ 521d96ca（r2 返修）→ b9d9a8ab（日志重采）→ a57e4834（终版 gate）→ cd261f70（r3 被审）→ 本轮返修 tip，每环附报告/处置链接。 |
| R3-07 | P4 | **fixed** | 历史日志取回方式写入 Task 全仓行、Handoff 全仓行、NOTE.md 三处（`git show a74ce105:...`）。 |
| R3-08 | P4 | **fixed** | 对照日志重采并补全：base checkout commit + 与 base 7db0e7b6 的关系（docs only）、scope（定向对照 5 tests，非全量）、解释器/Python 版本、ISO 时间戳、完整 stderr（含 QML TypeError 根因线索：viewmodel context 注入为 null）、`# EXIT: 1`。 |

## 遗留（不属本 Task，交后续）

- Legacy QML `test_repair13_import_entry.py` 2 个失败的根因（QML viewmodel context 注入为 null 的会话级回归）：r3 建议由 Codex/Qoder 另行登记诊断，不在本 Task 处理。
- F-006/F-010ab（r1 deferred）、R2-04..07 已全部 fixed（r3 复核通过）。
- F-008（3 组 ACL 联动文件范围追认）：维持 open，待 Codex integration record 裁决。
