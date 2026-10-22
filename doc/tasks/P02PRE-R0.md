---
id: P02PRE-R0
title: P02 受控只读取证
kind: verification
status: done
approval: user_authorized_read_only_preflight_20261011
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
depends_on: [P02M7R, P02M8R, P02M9R, P02M10R]
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
---

# P02PRE-R0：受控只读取证

## 来源与目标

用户于 2026-10-11 明确授权 Codex 创建并执行独立 `P02PRE-R0` 只读预检。授权仅允许不会创建、删除或修改系统/项目状态的精确查询；不是风险豁免，也不代表任何 Gate PASS。此 Task 与 [P02](P02.md) 及已 Review 的 r6 manifest 对齐。

目标是在不启动 AppContainer/API probe 的前提下，采集当前执行 PowerShell 进程身份、已登记路径/ACL、受限 TEMP/cache/path 映射、精确 WER 候选对象及固定文档的 SHA-256，并将全部 P02PRE 条件逐项标为 `PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST` 或 `NOT_SAFE_FOR_R0`。

## Acceptance Criteria

- [x] R0 manifest 已在 OS/path/ACL/WER 查询前冻结；最终完整采集进程先核验当前身份与 thread impersonation，再继续其余查询。早期失败/输出不完整批次已披露，不作为证据。
- [x] 非作者 Reviewer=`DeepSeek Harness` 独立 Review；结论=`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`，P0/P1/P2/P3=`0/0/5/6`。Reviewer 接受有限证据交付并评估父组件诊断偏差；Codex 已按逐项 adjudication 限定可采纳证据，不把不可重建批次用作 PASS。
- [x] 主要 R0 进程仅执行冻结的只读 getter/query；未写系统/项目对象、未做 protected-path 权限试探。Codex 编排期间有一次未冻结父组件集合的只读诊断批次，已记录并交 Reviewer 评估。
- [x] 最终采集只对 manifest 列出的精确路径读 metadata/ACL；不递归扫描 scratch 输入/输出、不读取文件内容（固定文档 SHA-256 除外），不读取用户漫画、数据库、Lock、current/pinned Revision、凭据或模型内容。
- [x] 实际结果保存至 [R0 evidence](../../verification/P02/p02-readonly-preflight-r0-evidence-20261011.md)，逐项标明观察范围和局限；未采集项未记 PASS。
- [x] `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER` 原值保持；按原文记录 `technical condition unmet; user explicitly accepted residual risk`。
- [x] Review=`verification/P02/p02-readonly-preflight-r0-review-20261011.md`；Codex adjudication=`verification/P02/codex-p02pre-r0-adjudication-20261011.md`。Reviewer 与 adjudicator 分离；证据、裁决与摘要均固定对象 hash。
- [x] 根据真实证据和 Codex adjudication 更新 R0 slice 与 P02PRE 分类；总体 P02PRE=`BLOCKED`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。本 Task 不授权 build、Cargo、AC 或 AppContainer 创建。

## 允许修改范围

- 本 Task、唯一规划事实源 `doc/REBASELINE_PLAN.md`、运行状态 `doc/STATUS.md`、导航索引 `doc/00_INDEX.md`、父 Task `doc/tasks/P02.md`、本 Task checkpoint。
- `verification/P02/p02-readonly-preflight-r0-manifest-20261011.md`、`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` 及 Codex adjudication。
- 为按 DSH dispatch skill 记录 Review，可由 Codex 创建固定 prompt/stdout/stderr/exit/mount 日志：`verification/P02/dsh-p02pre-r0-review-20261011.prompt.md`、`.stdout.md`、`.stderr.log`、`.exit`、`.mount.log`；这些文件只记录派发与 Reviewer 输出，不增加 OS 取证范围。
- 独立 Reviewer 仅写 `verification/P02/p02-readonly-preflight-r0-review-20261011.md`。

## 禁止范围

- `CreateAppContainerProfile`、`DeleteAppContainerProfile`、`GetAppContainerFolderPath`、`GetAppContainerRegistryLocation`、`DeriveAppContainerSidFromAppContainerName`；任何 AppContainer/profile 创建或删除。
- Registry 写、ACL/owner/label 修改、文件/目录写入/删除/移动/覆盖、protected-path 写权限探测、未列 registry/API/path 查询、递归目录扫描。
- `Add-Type`/PInvoke、编译/JIT、`whoami` 或其它未冻结子进程；任何未证明为只读无副作用的 API 必须标 `NOT_SAFE_FOR_R0`。
- Build/Cargo/AC1–AC7、提权、服务/驱动/ETW、联网下载、Windows Sandbox 查询/安装/启用/启动。
- 读取漫画/用户库、数据库、Lock、current/pinned Revision、凭据、模型内容或未列路径内容。

## 测试与证据要求

本 Task 是受控只读取证，不运行产品测试。逐项实际结果、错误和未执行项写入 R0 evidence。需要写入/动态行为才能证明的条件标 `REQUIRES_ACTIVE_TEST`；缺合同/缺对象绑定标 `UNPROVABLE`；查询本身不符合只读证明标准标 `NOT_SAFE_FOR_R0`。本 Task 完成后的独立 Review 与 Codex adjudication 必须分别留文件和对象 pin。

## 依赖、风险与阻塞

- 硬依赖：P02M7R、P02M8R、P02M9R、P02M10R 的静态 Review/adjudication 及用户 2026-10-11 只读预检授权。
- 不依赖 P02M11；该静态综合任务因 Owner 额度中断而保持 `BLOCKED / NOT_VERIFIED`，其已存在文件不可替代本 Task 的 Review 或宿主取证。
- 目标 AppContainer profile folder 的精确路径仍未知；不得猜路径或调用可能有副作用的 getter。
- Build Barrier 在本 Task 全程保持 `EFFECTIVE`；只有 Codex 在 Review/adjudication 后重新评估所有执行前 Gate，才能更新状态。

## 交付与运行记录

- Owner delivery：`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`；`99592 bytes / SHA-256 AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3`。
- 主要采集进程 PID=`12280`；身份/SID匹配、无 thread impersonation；42 个精确路径（17 present / 25 absent），两项只读 registry key（HKLM present / HKCU absent），三目录直接子项计数=`10/11/63`，固定 13 项 hash pre/post 一致。
- 交付状态=`EVIDENCE_CAPTURED_WITH_TOOLING_DEVIATIONS / REVIEW_REQUIRED`；有早期 path/WER 脚本或输出缺陷，已在 evidence 中逐项披露。R0 Task 尚未完成 Review/adjudication。
- Review：非作者 DeepSeek Harness；`dsh --version`=`0.2.0-rc.2` exit 0；只回复“收到”的通路 probe exit 0；Review dispatch exit 0，session=`session-a5935233-2e4b-41e4-a18a-08ab4c09a1d6`，已挂入 `New Manga` workspace。Reviewer=`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`，findings=`0/0/5/6`；报告=`verification/P02/p02-readonly-preflight-r0-review-20261011.md`，`29404 bytes / SHA-256 427F582D87A54E8C5B7CB65FB72F1B067BD226B8E6DFA66873FDC996E6B5C554`。
- Codex adjudication=`ACCEPTED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY_WITH_LIMITS`；文件=`verification/P02/codex-p02pre-r0-adjudication-20261011.md`，`11145 bytes / SHA-256 E66131960E35A35C8E6F051EFE0F1C167CEBE2DBC78D849DA00A2642D901375E`。R0 Task=`DONE`，仅关闭受控只读取证交付切片，不关闭总体 P02PRE。
- 下一 READY Task=`P02PRE-R0S1`：只查询两个已登记 scratch leaf 的直接子项 metadata；不得读内容、递归、写入、修改 ACL/registry、调用 AppContainer API、构建或运行 AC。Owner=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`；由 Codex adjudicate。冻结与恢复信息见 `verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md` 及后续 R0S1 Task-local checkpoint。
- 实际查询：已运行冻结范围内的只读查询；产品测试不适用于本 Task，build/Cargo/AC 未运行且仍禁止。
- Integrator：Codex /root；独立 Reviewer 返回后单独 adjudicate。
