# DSH Review Task P02PRE-R0S3

请对当前工作区中的只读静态分类交付做独立审查。你是 Reviewer，不是作者；不要修改任何文件，不运行测试，不执行任何 OS/API、Registry/WER、profile、token、ACL、path、TEMP/cache、scratch、protected hash、Build、Cargo 或 AC 操作，也不要查询、安装、启用或启动 Windows Sandbox。

## 固定对象与基线

- Repo=`G:/CODEX/New Manga`；branch=`main`；base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Task=`doc/tasks/P02PRE-R0S3.md`（请独立重算 bytes/SHA）。
- Owner Delivery=`verification/P02/codex-p02pre-r0s3-classification-20261011.md`（请独立重算 bytes/SHA）。
- Owner=`Codex /root`；你是非作者 Reviewer；Codex 负责 adjudication/integration。

## 审查要求

1. 校验 Task 与 Delivery pins、HEAD/tree、Owner/Reviewer 分离；抽查 Delivery 的源文件 pin 表。
2. 判断五种规定分类是否完整、事实边界是否准确：`PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST`、`NOT_SAFE_FOR_R0`。条件状态和采集方法状态必须分开；`NOT_RUN`、安全停止不得写成 `FAILED`。
3. 重点核实 R0S1 在任何 G: path query 前停止；R0S2 因 PowerShell startup/profile/module cache/history/executable/argv/wrapper side effects 无法证明而 `NOT_SAFE_FOR_R0`，Registry query=`NOT_RUN`；不要建议重试或换 shell/runtime。
4. 核实 R0 有限时点 `PASS_WITH_EVIDENCE` 不外推完整 protected set 或安全 Gate；M7/M8/M9/M10/M11 的 unresolved 条件没有被提升为 PASS。
5. 核实用户裁决逐字保留：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`。
6. 不要把本 Review 当 Gate PASS，不新增授权，不推断目标机当前状态。

## 输出格式

用简体中文交付结论 `APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE`、P0/P1/P2/P3 计数、每个 finding 的证据与修正建议、pins/HEAD 结果、未覆盖项和实际 runtime model/effort（无法核实则 `NOT_VERIFIED`）。只做静态审查；不要创建本地 Review 文件，我会归档你的 stdout。
