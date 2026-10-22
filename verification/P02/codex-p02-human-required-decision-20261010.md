# P02 Phase A / Build Gate · HUMAN_REQUIRED 决策包

**当前状态：用户已批准 Owner 风险例外；早先 B 仅为历史裁决，已被下方最新追加取代。** P02=`in_progress / ACTIVE`；本文件不表示 Task 完成或任何技术 Gate 通过。

## 最新裁决追加（2026-10-10 15:21 UTC）：Owner 批准 private-registry 风险例外

用户正式批准 P02 当前 `private_registry_absence` Gate 的风险例外。最新状态覆盖本文此前的 B 选择；B 作为历史决策保留，不再是当前准入规则。

- 技术事实仍为 `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`，不得伪记为 `PASS`。
- Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`。
- Hard Build Barrier 仍须保持 `EFFECTIVE`，直至完整 execution manifest 经非作者 Review，且用户列明的执行前安全检查全部通过；随后 Codex 才可明确记录其解除。
- 仅豁免“必须在创建前无副作用证明目标 private registry storage 不存在”。profile folder、身份、SID、ACL、TEMP/cache、scratch/input/output 路径、子进程、受保护文件/hash、清理及其他 Gate 安全条件均不豁免。
- 创建只允许固定用户+固定 moniker 单次调用，精确 `S_OK` 后只读验证；其他 HRESULT/未知状态不复用、不推断 absence、不自动清理。未知子进程、未授权 registry/ACL/file 写、身份不符或证据异常时立即停止。
- AC1–AC7 必须真实执行并逐项记录；本例外不自动判 PASS。Windows Sandbox 不查询、不安装、不启用、不启动。
- 必须记录裁决原文：`technical condition unmet; user explicitly accepted residual risk`。

裁决时 Live root=`G:\CODEX\New Manga`，branch=`main`，HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`，启动状态项=`393`。裁决后已开始 P02M execution-manifest 冻结与非作者 Review；当前 profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。此段是用户授权记录，不是执行证据或 Gate PASS。

## 用户裁决记录（2026-10-10）

用户回复“授权评估提权方案”，对应下方第 3 项。授权仅涵盖静态技术评估、更新 P02 Task/规定治理状态文档，并由非作者 Reviewer 独立审阅评估报告；不授权安装或启动管理员/LocalSystem observer、ETW session、驱动或服务，不授权修改 BCD、Secure Boot、签名策略、registry、ACL、label、profile、TEMP/cache/运行目录，也不授权 OS preflight、build、Cargo 或 AC1–AC7。

评估报告 r2：[P02 提权观测/强制方案评估](codex-elevated-isolation-method-assessment-20261010-r2.md)；独立 Review=`APPROVED`，Codex 裁决=`ACCEPTED_AS_STATIC_DOCUMENT_ONLY`，见 [r2 Review](codex-elevated-isolation-method-assessment-review-20261010-r2.md) 和 [Codex adjudication](codex-elevated-isolation-assessment-r2-adjudication-20261010.md)。它没有证明完整子进程/写入闭包，也没有解决 private-registry 创建前缺失条件，不改变 P02 的任何 Gate。Windows Sandbox 仍不查询、不安装、不启用、不启动。

## 决策背景

P02 仍要求 AC1–AC7 的真实 WebView 证据，并要求在构建前先以操作系统证据证明隔离身份、scratch 可写、受保护位置拒绝写入、TEMP/cache 重定向及全部相关子进程闭包。当前 11 项 Gate 的状态仍见 [P02 Task](../../doc/tasks/P02.md)；核心阻塞为 `private_registry_absence=UNPROVABLE / BLOCKED` 和 `hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`。profile 尚未创建；ACL、registry 与 label 未改动；OS preflight、build、Cargo 和 AC1–AC7 均未运行。`BLOCKED / NOT_RUN` 表示尚未测试，不是失败。

P02 Task 已记录本次授权：Codex 可自主确定精确本机 AppContainer profile、TEMP/cache、scratch ACL 与本机 preflight 范围；同时明确授权是范围许可，不是 Gate 证据。Task 还记录尚未确认一种能在 profile 创建前、无副作用地证明目标 private registry 不存在的方法。Microsoft 的 `CreateAppContainerProfile` 文档描述的是创建 profile/data store 的 API，成功返回表示 data store 已创建；不能把调用该 API 当作无副作用的缺失状态探针。[Microsoft Learn：CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)

现有 `DEBUG_PROCESS + Job + ETW` 候选不能证明 P02 要求的任意子进程与全部写入闭包。Microsoft 文档明确说明，`Win32_Process.Create` 创建的子进程不会自动加入 Job；允许 breakaway 时也会影响进程树覆盖。[Microsoft Learn：Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) ETW 记录丢失计数，存在数据丢失时不能声称观测完整；控制 NT Kernel Logger 需要管理员权限或 LocalSystem。[Microsoft Learn：EVENT_TRACE_PROPERTIES](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_properties)、[Microsoft Learn：StartTraceA](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea)

项目证据见 [P02 Task：授权与 Gate](../../doc/tasks/P02.md)、[Phase A method blocker memo r10](codex-phase-a-method-blockers-20261010-r10.md)、[r10 attempt 2 Review](dsh-phase-a-method-blockers-review-r10-attempt2.stdout.md) 与 [Codex adjudication](codex-phase-a-method-blockers-review-r10-attempt2-adjudication.md)。r10 attempt 2 的 Review 是纯文档审查，结果为 `APPROVED_WITH_CONDITIONS`、0 项新 finding、formal `object_binding=NOT_VERIFIED`，不改变上述阻塞。

## 决策选项（第 3 项已选；其余仅作历史记录）

1. **维持现有验收标准（推荐）**：不降低 process/write 闭包要求，也不增加提权、驱动或可写路径；P02 保持 `HUMAN_REQUIRED / BLOCKED`，Codex 仅继续寻找能以已授权范围证明全部条件的方法。找到可审查方案后再复核 Gate。
2. **缩小进程与写入范围**：授权 Codex 起草一个新的 P02 验收方案，明确允许的子进程创建机制、被覆盖的后代范围、受保护位置与可写输出；这会改变现有验收范围，必须由用户确认新标准并经 Review 后才能执行。
3. **授权评估提权观测/强制方案**：允许 Codex 起草包含管理员/LocalSystem、ETW 或驱动/内核过滤器等候选的精确权限、路径、缓存、临时文件和清理范围；在方案冻结并经过独立 Review 前仍不执行任何提权或 OS 操作。此项扩大系统权限与潜在写入范围。

无论选择哪项，Windows Sandbox 仍按用户此前决定保持禁用且不查询、不安装、不启动。此前“收到选择前”的等待状态已结束；当前新的验收准入条件裁决仍待用户决定，Gate 继续保持原值。

**历史建议（已被用户裁决取代）：**当时建议选择 1，保留当前数据保护和验收标准。当前以用户已选择第 3 项为准。

## 历史决策项：是否替换创建前 private-registry absence 条件（已由用户选择维持原标准）

用户选择第 3 项只授权评估提权方案，并未授权改变“创建前无副作用证明目标 private registry 缺失”的现行准入条件。`CreateAppContainerProfile` 的文档说明精确 `S_OK` 表示 data store 创建成功、`HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS)` 表示 application data store 已存在，但没有保证事务原子性、失败无副作用或自动回滚；因此它不能被描述为原缺失探针。[Microsoft Learn：CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)

Codex 已准备候选 [`CreateAppContainerProfile 准入条件替代方案`](codex-appcontainer-create-gate-alternative-20261010.md)，固定草案 SHA-256=`DC4186511DF30CE1AC20B8B53B5C0D9714B6B50947043CEDA31495D8FE1016B9`。非作者 Review=`APPROVED`（P0/P1/P2/P3=`0/0/0/0`），Codex adjudication=`APPROVED_AS_STATIC_PROPOSAL_ONLY`；见 [Review](codex-appcontainer-create-gate-alternative-review-20261010.md) 与 [Codex adjudication](codex-appcontainer-create-gate-alternative-adjudication-20261010.md)。草案提出：固定当前用户和 moniker，只尝试一次创建；只接受精确 `S_OK` 并执行待 Review manifest 定义的创建后只读检查；已存在立即停止，不复用、不删除；其他失败记 `UNKNOWN / BLOCKED`，不自动清理；承认 API 未文档化的部分失败/子对象状态风险。其余 OS 写入路径、profile/ACL/registry/Cleanup 与隔离闭包条件仍须逐项按 Task 冻结和 Review。

裁决前选项如下；用户已于 2026-10-10 13:50 UTC 回复 `B`，选择第 2 项：

1. **接受候选语义变更**：将 Gate 从“调用前证明所有目标 private-registry storage 缺失”改为“精确 `S_OK` 新建结果 + 创建后只读验证”，并接受文档未保证部分失败无残留的风险。此选择只接受该 Gate 语义；实际 API 调用仍需先冻结完整参数、身份、精确读取路径、证据与清理 manifest，并经过独立 Review。其余 Gate 不自动通过。
2. **维持原标准（用户已选择）**：禁止创建前缺失证明不明时调用创建 API；P02 继续 ACTIVE 处理只读技术调查，Gate 本身仍 `BLOCKED`。

裁决后：profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build=`NOT_AUTHORIZED / NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。这些状态不是测试失败。

## 用户裁决 B（2026-10-10 13:50 UTC）

用户回复=`B`，选择维持创建前无副作用证明目标 private-registry storage 缺失的原准入条件。候选 `CreateAppContainerProfile` create-then-verify 语义未被接受。先前针对替代条件的 `HUMAN_REQUIRED` 已关闭；该裁决不放宽、也不通过任何 Gate。

P02 继续 `in_progress / ACTIVE`。Codex 已派发只读官方文档/API-contract 调查，寻找无需创建 profile 且不写 registry 的完整缺失证明方法。Owner=`/root/p02_isolation_advisor`；固定 HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；唯一交付写入路径=`verification/P02/codex-p02-noncreating-registry-absence-options-20261010.md`；独立 Reviewer=`/root/orchestration_docs_review`，待 Owner 交付后派发。此子任务禁止本机 registry/profile/ACL/token 读取、任何 OS/API 调用、Sandbox、preflight、build、Cargo 与产品测试。未 Review/adjudicate 前不更新 Gate。

当前 Gate 仍=`private_registry_absence=UNPROVABLE / BLOCKED`；Phase A=`BLOCKED / NOT_RUN`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；hook/cache/child-process closure=`BLOCKED / NOT_VERIFIED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。
