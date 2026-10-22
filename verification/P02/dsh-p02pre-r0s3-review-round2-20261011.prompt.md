# DSH Review Task P02PRE-R0S3 — Round 2

请对 Owner 修订后的静态分类交付做独立复审。本轮不要求你尝试改变沙箱权限；只读审查文件。如果无法在你的运行环境复算某项 hash/tree，请把它作为单独的 `NOT_VERIFIED` 限制报告，不要提权、改 ACL、换路径绕过或把 pin 失败当作内容 finding。Codex 已在主工作区独立复算 Task/Delivery 与表中源 pins。

## 冻结对象与 Git 基线

- Repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Task=`doc/tasks/P02PRE-R0S3.md`；`5340 bytes / SHA-256 361BD7F02CFBFEC6FB6B700B2DD9FCE10DFB0BD0D6998BB8978ADE2B1FB4378D`。
- Owner Delivery=`verification/P02/codex-p02pre-r0s3-classification-20261011.md`；`15302 bytes / SHA-256 3E0E61D82578A48F09374B03D225E987986A8517DE821A82FD189E765CAFEBC0`。
- Round 1 Review=`verification/P02/dsh-p02pre-r0s3-review-round1-20261011.md`；`16114 bytes / SHA-256 3CC2846857A3F2972D5CA02F3B12D314063C8DE8628AC1C3E0F33F342FCF9BF3`。
- `doc/STATUS.md` 09:06 snapshot=`260460 bytes / SHA-256 B4375872C5546D28EE69B77B2E404D930F21DF4DF86C9340D895C4299AE89AF4`。
- `doc/REBASELINE_PLAN.md` 09:06 snapshot=`237987 bytes / SHA-256 4327D4BBA38811A73E531238BF46139E5B233E998F75A4867A6501B8F28FC07D`。
- `doc/00_INDEX.md` 09:06 snapshot=`46506 bytes / SHA-256 1EE3903A4E1F5675E01BA208124F24B07FBCF8C2EF042AE4B07B942460DB62C4`。
- `doc/tasks/P02.md` 09:06 snapshot=`212081 bytes / SHA-256 04E2E340AA0ECF1F2F6E1C98418529032F81F134B7FDDCECD71B39F61CF9F6F3`。
- Owner=`Codex /root`；你是非作者 Reviewer；Integrator/adjudicator=`Codex /root`。

## Round 1 修订点

Round 1=`NOT_VERIFIED`、P0/P1/P2/P3=`0/0/2/6`。请核实修订版是否完整处理：

- P2-01：显式加入 R0S1 capture timestamp、stderr、executable/argv、cmd bytes 绑定=`UNPROVABLE`，并保留 R0 `index_side_effect=NOT_VERIFIED`。
- P2-02：明确 Round 1 时 STATUS 的旧状态与 R0S2/M11 已完成证据冲突；STATUS/Plan/Index/P02 当前 snapshot 已更新且在 Delivery pins 中固定。
- P3-01/02：将条件与采集方法分列，`FAILED=∅` 放在表外。
- P3-03：profile path predicate=`UNPROVABLE`，candidate getter=`NOT_SAFE_FOR_R0`，说明这是更精确分列而非弱化 Gate。
- P3-04：Task、R0/R0S1/R0S2、M7–M11、R6 与 current-state 的相关 pins 足以支持该 Delivery 的范围。
- P3-05：root runtime model/effort 有独立 JSON 记录；不得推断 Advisor/Reviewer model。
- P3-06：Round 2 stdout 将归档至 Task 声明的正式 Review 路径，dispatch exit/stderr/session mount 有独立记录。

## 内容审查要求

1. 校验五种分类完整准确：`PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST`、`NOT_SAFE_FOR_R0`；条件对象与方法状态不可混淆。
2. 校验有限 R0 状态不会外推完整 protected set、未来状态、有效 LPAC access、WER policy/destination 或 Gate PASS。
3. 确认 R0S1 在任何 G: path query 前停止；scratch emptiness=`UNPROVABLE`；R0S2 PowerShell runner=`NOT_SAFE_FOR_R0`、LocalDumps query=`NOT_RUN`、当前 key 状态=`UNPROVABLE`。不得建议重放或更换 runner。
4. 校验 `FAILED=∅` 与 R0/R0S1 capture metadata、R0 index side-effect 的边界记录。
5. 校验用户裁决逐字保留：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`。
6. 检查 Round 1 每个 finding 的具体处理，指出任何剩余 P0/P1/P2/P3 与文件/行证据。
7. 不运行测试/宿主 query，不修改文件、不新增授权、不查询/安装/启用/启动 Windows Sandbox。

## 输出

简体中文。给出结论 `APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE`、P0/P1/P2/P3 数量、Task/Delivery/HEAD pin 结果（无法自行复算则分列）、Round 1 findings disposition、未覆盖风险和实际 runtime model/effort（无法核验=`NOT_VERIFIED`）。请输出完整 Review 正文供 Codex 原样归档；不要创建/修改本地文件。
