# AUDIT-08 Follow-up 独立审查报告

- verdict：`ACCEPT`
- reviewed_head：`f3320cc9de84dd769c60064537555d5ccd59005c`（`main`）
- reviewer：ZCode，`reviewer_kind=agent`，全新只读上下文；未参与 AUDIT-08 实施或返修
- ZCode session：`sess_d439aa3c-df30-4ca3-a840-30f0ee78c1a0`
- trace / turn：`f13bf459-e415-447d-9bfd-51a0468b8591` / `turn_be671c03-02e5-465f-9fc6-959389738cf4`
- CLI：`0.17.1`，`--mode plan --json --locale zh-CN`，EXIT 0
- findings：0 P0 / 0 P1 / 0 P2 / 1 P3；另 2 条 observation
- 原始响应：`evidence/zcode-audit08-followup-review-20261113.json`，SHA-256=`28531575D0CC426FA02AF88B6B508D7118D116A4EB58B041D4C1A4AB9750C3FC`
- 派发日志：`logs/zcode-audit08-followup-review-dispatch-20261113.log`，SHA-256=`1A0C93401A914B2E8132C4D0B09B394E8A3E24EF1950C27C3028E76F43C708B9`

## 结论

ZCode 接受 `f3320cc9d` 上 AUDIT-08 的范围、限制、首轮 P3 处置、状态口径及 34 条 Canonical Evidence。该结论只接受这次有限专项交付，不将 `AUDIT-08=FAIL` 提升为 PASS，不是全审发布准入，也不关闭 `NEW-MANGA-V1-FULL-AUDIT`。

### 首轮 P3 处置复核

- P3-1 已修复：修订版报告单列“异常中断”，只认定 connection ownership 测试中显式 `rollback()` 的窄面覆盖，明确没有逐类注入 Python exception 或磁盘异常。
- P3-2 已处置：Task 卡已列入 `0742a572`、`a932b756`、`25614d45` 三批 pinbackfill/报告修订后的门禁输出，范围与日志中的 generated HEAD、EXIT 一致。
- 对当前表内 34 条 pin，ZCode 表示已逐项重算 raw Git blob SHA-256 且全部匹配；本审计会话也独立重算 34 条并加验下述 5 个 gate 文件，结果 39/39 匹配，见 `logs/audit08-pin-verify-followup-20261113.log`（SHA-256=`7D7D51942DB55F5772DAFCD2064A5523E423CCC4AEA2F5B90A19006CF8C1A46C`，generated HEAD=`f3320cc9de84dd769c60064537555d5ccd59005c`，EXIT 0）。

## Finding

### P3-3：`d6658d123` 上的最终门禁输出尚未列入 Task Canonical Evidence

- 位置：`doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md` 的 AUDIT-08 Canonical Evidence 表，以及 `audit/V1-FULL-AUDIT/AUDIT_RESUME.md` 的 2026-11-13 恢复点。
- 缺失的五个文件：default check log 与 JSON、TaskPath check、`verify_pins.ps1`、API inventory 日志；均由提交 `f3320cc9de84dd769c60064537555d5ccd59005c` 固定，内容显示在 generated HEAD=`d6658d123ba14d4f586b1675652d64a5d2e5d523` 运行，四项均 EXIT 0。
- 影响：非阻断的证据索引缺口；Task 仍为 `in_progress`，`canonical_evidence_status: pending`，AUDIT-08 结论仍为 `FAIL`。
- 建议：下一次 Canonical Evidence pinbackfill 将上述五项与本轮 Review 记录一并加入 Task 表，并在 pinbackfill HEAD 复跑 default/TaskPath check、18 pins 与 API inventory；恢复点同步记下 `d6658d123` 四项结果。
- 当前处置：已在本次后续 pinbackfill 中补录五项，并如实更新恢复点；独立 closure review 尚待执行。ZCode 建议将“最新 post-pinbackfill 门禁输出在下一次 pinbackfill 整批纳入”的滚动规则写入表注，以避免门禁日志与证据 pin 产生递归追逐。

## Observations

1. Task 卡 `SCOPE-POSTCOMMIT-GATES-1` 行原先使用 9 位 commit `0f76e6a79`，与 40 位格式不一致。完整 commit 为 `0f76e6a79503d2dd19d3cadb5e14f7a3c835192a`；本轮同步补全，未改变其指向。
2. 本轮 AC4 的“follow-up Review 待完成”需改为记录当前 ACCEPT 与 P3-3 的处置/复核进度。

## 审查范围及限制

ZCode 核验了项目治理与协作指针、原始 AUDIT-08 指令、专项报告、测试源码、Task 状态、AUDIT 状态/恢复点、三批 pinbackfill gate、`d6658d123` gate 文件、34 条 pin 及 12 个被引 commit。Review CLI 未运行测试或产品命令；git 只读取证由其独立上下文派发的 Explore 子代理 `agent_d2b8f343`、`agent_4c364d1b` 执行。主审计会话对 34 条现有 Canonical Evidence 和 5 个 `d6658d123` gate 文件另行执行 `git cat-file blob` / SHA-256 实测，39/39 PASS、EXIT 0。

本轮没有修改产品源码、测试、契约、Schema、依赖或真实用户数据；没有重放 probes、访问远端或运行产品测试。真实数据库、运行时任务迁移、真实损坏/断电恢复、多文件部分写与私人素材仍按 AUDIT-08 报告列为未验证。后续依当前 DAG 继续 AUDIT-05/06；全审 Task 继续 `in_progress`，Release Gate 继续 `BLOCKED`。
