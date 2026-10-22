# P02M9 Codex adjudication：WER per-image / views / T0 静态合同研究

## 裁决

- Task=`P02M9`；结论=`ACCEPTED_AS_STATIC_RESEARCH_ONLY`；Task 状态=`DONE`（仅静态合同研究）。
- Owner=`/root/p02_manifest_reviewer`；非作者 Reviewer=`/root/p02_isolation_advisor`；Integrator=`Codex /root`。
- 基线 branch=`main`；base/reviewed HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。
- Owner report=`verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md`，`17105 bytes`，SHA-256=`6207483ED6CE62650C346D18D42FC81CD5102C44A028BAF0DE4F131AF60411F3`。
- Independent Review=`verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-review-20261010.md`，`13059 bytes`，SHA-256=`E5E71E1B28F76B4FFF8190D27E7A6B56F13559090BDB8251EABFEFE2350EE7B7`；Verdict=`APPROVED_AS_STATIC_RESEARCH_ONLY`，P0/P1/P2/P3=`0/0/0/0`。
- Codex 已读取报告与 Review，并核对其对象 pin、作者/Reviewer 分离、固定 HEAD 及声明范围；按 Microsoft 官方文档验证 per-image precedence、LocalDumps 字段不支持 HKCU、通用 WOW64 view 规则与其适用边界。Review 同意报告没有把通用 registry view 外推为 WER 内部 reader 事实，也没有把公开规则当作本机配置或 T0 无副作用证据。

## 保留的技术状态

- `wer_per_image_rules=PARTIALLY_DOCUMENTED`。
- `host_wer_configuration=NOT_READ / NOT_VERIFIED`。
- `wer_view_destination_binding=NOT_RESOLVED / BLOCKED`。
- `t0_bootstrap_safe_order=NOT_RESOLVED / BLOCKED`。
- 本机 policy、所有实际 WER 目的地、映像/view、environment expansion actor 和 bootstrap 期间的完整进程/写入边界均未核实。M9 不修改或扩大执行 manifest 的授权。
- 没有调用 OS/API、读取本机 registry/WER 目录/environment/token/profile/path/ACL，没有运行 Sandbox、build、Cargo 或 AC；没有产生 profile、registry、ACL 或文件写入证据。

## Gate 与用户风险裁决

`private_registry_absence=UNPROVABLE` 保持技术事实；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；必须逐字保留：`technical condition unmet; user explicitly accepted residual risk`。该例外只覆盖创建前无副作用证明目标 private registry storage 不存在，不覆盖 WER、profile-folder、T0、identity/SID、ACL、TEMP/cache、scratch/input/output、子进程/写入闭包、protected-file/hash 或其他安全要求。

因此 P02 Build Gate 仍=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。本 adjudication 不构成 Build Gate PASS，也不授权 API 调用。

## 接续

P02M9 的静态合同研究与独立 Review 已完成；WER view/destination 与安全 T0 仍是未解决的执行前条件。下一步由 Codex 在唯一规划事实源和 P02 Task 中释放一个独立、只做静态文档冻结的 manifest reconciliation Task；在其交付和独立 Review 完成前，不进入 OS/API preflight、Create、Build 或 AC。
