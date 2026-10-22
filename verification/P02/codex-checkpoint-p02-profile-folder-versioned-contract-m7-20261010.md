# P02 Rolling Checkpoint：P02M7/M8/M9 静态合同补查

## 恢复基线

- 捕获时间=`2026-10-10 16:19 UTC`；仓库=`G:\CODEX\New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；`main...origin/main [ahead 1365]`；Git common-dir=`G:/CODEX/New Manga/.git`；登记 worktree=`363`。
- 原作者既有未提交内容保留；没有 reset、clean、stash、覆盖、删除或 commit。共享工作区中 Task/Plan/STATUS/Index 与 checkpoint 是受控治理文档；M7 Owner/Reviewer 各自只写唯一 evidence 文件。
- checkpoint 前最新 safe NUL status 样本（16:15 UTC）命令=`git --no-optional-locks -c core.fsmonitor=false -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`；环境=`GIT_OPTIONAL_LOCKS=0`；exit=`0`；records=`494`；stderr 空。`.git/index` 前后 SHA=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`，size=`972663`，mtime=`2026-10-10T03:18:18.4750975Z`。这不能回溯证明早先不带 `--no-optional-locks` 的 status 没有写 index；Codex 未恢复或覆盖 index。

## 任务与已完成证据

- P02M6=`DONE / APPROVED_AS_STATIC_ASSESSMENT_ONLY`。Owner 报告=`6053 bytes / SHA-256 CF77049EEB7A2C276FBD35A9A7AFF6FD2B4076E2B03FD4CED33BDF7EE47D0BCC`；非作者 Review=`APPROVED`，`7776 bytes / SHA-256 C015A7BD0F38BF7C32F63F6515A8C4BDF7B74823C16A2A181DCA79043EC34744`，P0/P1/P2/P3=`0/0/0/0`；Codex adjudication=`verification/P02/codex-p02-profile-folder-noncreating-contract-adjudication-20261010.md`。结论仍为 `profile_folder_no_side_effect=UNPROVABLE / BLOCKED`。
- M6 adjudication 已复核 Review 边界：非作者 Reviewer 未独立重算 Owner hash 或重读 waiver；Codex 已复算对象并对照原决策/Task。只接受静态分析结论；不作 OS 事实或 Create 放行。
- 与此前实际 checkpoint（16:10 UTC）相比：M6 Review 与 Codex adjudication 收口；M7、M8 已建立并派发。所有 OS/Create/Build/Cargo/AC/Gate 状态无变化。

## 当前授权与 Gate

- 唯一 Active 产品 Task=P02；当前 Active 子任务=`P02M7 + P02M8 + P02M9`。
- 用户风险裁决：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；固定说明=`technical condition unmet; user explicitly accepted residual risk`。
- waiver 仅限“必须在创建前无副作用证明目标 private registry storage 不存在”。不覆盖 profile-folder no-side-effect、identity/SID、ACL、TEMP/cache、scratch/input/output、child/write boundary、pre/post hashes 或其它 Gate。
- profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未执行，不是失败）。P02PRE/P02A/P02G/P02AC 均未放行。

## M7 Agent 交接

- Owner=`/root/p02_isolation_advisor`；角色=只读 API/平台合同研究；Integrator=`Codex /root`；独立 Reviewer=`/root/orchestration_docs_review`。Agent runtime model/effort 由工具不可见；不声称使用特定模型。
- Baseline=`main@cddff58469b56e181019a8ddfeade80684bc7eb9`。Owner 唯一写入=`verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md`；Reviewer 唯一写入=`verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md`。
- Owner 只查 Microsoft/Windows SDK 版本化合同是否直接承诺 `GetAppContainerFolderPath` no-create，或有官方支持的创建前精确路径/缺失检查替代方法；锁定来源版本与适用范围并分开事实和推断。禁止调用 OS/API、猜 SID path、读取本机 profile/registry/ACL/token/path、Sandbox、build/Cargo/AC 或改动其他文件。
- Review 只对固定报告做独立静态审查，复核来源 pin、合同解释、适用范围及是否足以覆盖 no-create/缺失状态；禁止运行 OS/API 或修改 Owner 文件。Owner 不审自己的研究。
- M7 若没有充分正式合同，结果只是 `NOT_RESOLVED / BLOCKED`；不得扩张 waiver。Codex 复核对象与 Review hashes 后刷新子图，再自动选下一个 READY 静态 blocker 任务。

## M8 Agent 交接

- Task=`P02M8`；Owner=`/root/orchestration_docs_review`；角色=只读 API/平台合同研究；Integrator=`Codex /root`；独立 Reviewer=`/root/p02_manifest_reviewer`。M8 不审查 M7，也不改写 M7 的路径。
- Baseline=`main@cddff58469b56e181019a8ddfeade80684bc7eb9`。Owner 唯一写入=`verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md`；Reviewer 唯一写入=`verification/P02/codex-p02-zero-capability-registry-getter-contract-research-review-20261010.md`。
- 范围：静态核查官方版本化合同对 `GetAppContainerRegistryLocation(KEY_READ)` 的访问语义、zero-capability LPAC 适用性及能否证明所需读取边界；固定来源/版本并区分明文合同与推断。禁止 OS/API 调用、读取本机 token/capabilities/registry、打开相邻 key、Sandbox、build/Cargo/AC。
- M8 来源不足则仅结论 `NOT_RESOLVED / BLOCKED`；不得把 registry absence waiver 扩张为 registry Getter 能力/安全 Gate 的豁免。

## M9 Agent 交接

- Task=`P02M9`；Owner=`/root/p02_manifest_reviewer`；角色=只读 WER/T0 官方合同研究；Integrator=`Codex /root`；独立 Reviewer=`/root/p02_isolation_advisor`。Agent runtime model/effort 由工具不可见，不猜测。
- Baseline=`main@cddff58469b56e181019a8ddfeade80684bc7eb9`。Owner 唯一写入=`verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md`；Reviewer 唯一写入=`verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-review-20261010.md`。
- 范围：只查 Microsoft WER 官方来源对 LocalDumps per-image 配置、适用 hives/views、dump destinations 与初始化顺序的公开合同；不读本机 registry/环境变量/dump 目录，不声称已知当前配置。若无安全 T0 次序或需读取未授权状态才能精确冻结，则保持 BLOCKED。

## 精确下一步

分别接收 M7/M8/M9 Delivery 后，Codex 复算 bytes/SHA 与 baseline、核验各自 Reviewer 独立性及 findings，并分别 adjudicate。任一研究未解决则保持对应 blocker 和所有运行状态原值。之后从剩余安全 blocker 中选择有依据、无冲突的只读合同研究 Task；不运行执行前 OS 检查或调用创建 API，直到 manifest 中的每个执行前安全条件都有证据且用户 waiver 边界不变。

## 实际命令与限制

- `git rev-parse HEAD`、branch、tree、ahead count 与 worktree list 只读核验；safe Git status 如上，exit=`0`。
- PowerShell `Get-Item`/`Get-FileHash` 对 M6 report/review、r5 manifest/review/adjudication、用户决策记录均 exit=`0`；M6 pin 与本 checkpoint/adjudication 记录一致。
- 未运行 tests、Windows API/OS/profile/registry/ACL/token/path probe、Windows Sandbox、build、Cargo 或 AC1–AC7。
