# P02 Rolling Checkpoint：P02PRE-R0 受控只读取证

## 2026-10-11 07:34 Asia/Shanghai 当前恢复点：R0 Owner Delivery 完成，Review 通路可用

### 仓库、分支与工作区

- Repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；common-dir=`.git`。
- 最新安全 NUL status=`exit 0 / 513 records / stderr empty`；命令前后 `.git/index` SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；`git worktree list --porcelain`=`361`。没有 prune。
- 当前 turn 开始时执行了一次普通 `git status --porcelain`，没有紧邻 pre-index hash。随后安全 status/index hash 与之前 checkpoint 相同；这不能回溯证明该普通命令无副作用，记录为 `index_side_effect=NOT_VERIFIED`。未恢复、覆盖或重写 index。
- 所有既有未提交内容仍归原作者；本轮仅修改该 Task 明确允许的 Task/Plan/STATUS/Index/checkpoint/P02 Task/evidence 文件。没有 reset、clean、stash、删除或 commit。

### 当前 Task、Owner Delivery 与 Review 状态

- `P02PRE-R0`=`ACTIVE / EVIDENCE_CAPTURED / REVIEW_PENDING`；Owner/Author=`Codex /root`；Integrator/adjudicator=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`，尚未 dispatch。Task=`doc/tasks/P02PRE-R0.md`；冻结 manifest=`verification/P02/p02-readonly-preflight-r0-manifest-20261011.md`。
- R0 evidence=`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`，`99592 bytes / SHA-256 AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3`。文档记录完整 query JSON、逐项实际结果、hash pre/post、分类、限制与脚本错误。
- 主要只读进程 PID=`12280`，首个目标查询为 `WindowsIdentity.GetCurrent(false/true)`；name/SID 与 r6 固定值匹配，authenticated=`true`，auth type=`CloudAP`，thread impersonation=`false`。其后同进程读取冻结的 35 项 Process environment、42 个精确路径/ACL、两条 WER registry 候选、三个候选目录直接子项、13 个固定 hash 对象的 pre/post。
- 实际结果：精确路径 `17 PRESENT / 25 ABSENT`；12 个输入 root 均存在；13 个 scratch leaves 中 11 absent、2 present；smoke readonly canary leaf present，其余两 leaf 与正向 canary file absent；r6 evidence root 和十个固定目标均 absent。现存两个 scratch leaf 的 emptiness 未验证。HKLM LocalDumps key present，HKCU absent；三个 WER 候选 direct child count=`10/11/63`；固定 13 项 pre/post hashes 全相同。
- 当前 Process `HOME` 与 cache path variables unset；`HOMEDRIVE=C:` + `HOMEPATH=\Users\49745` 经组合归一化后与 `USERPROFILE=C:\Users\49745` 匹配。host 变量不能代替 future controller/LPAC child environment。

### R0 执行偏差 / 已知限制

- 一次早期路径 helper 批次在 `Get-Item`/`Get-Acl` 前因函数定义顺序错误停止；随后一批无可捕获 stdout；再一批曾查询精确目标的父组件且工具输出被截断，父组件集合没有在 manifest 冻结。该最后诊断仅用只读 getter；不采用其输出为 evidence，明示给 Reviewer 判断 scope deviation。最终可用 capture 只查询冻结的 42 个精确目标。
- 首次 WER 目录查询因 PowerShell 数组构造错误把三个路径合成无效路径，不作为证据；最后主要 capture 已按三个精确目标重查。
- 另一次同用户/SID PowerShell 只验证 `HOMEDRIVE + HOMEPATH` 的组合 `Path.GetFullPath`，未查询其他系统对象。
- 未调用 P/Invoke、`Add-Type`、子进程、AppContainer/profile API、registry/ACL/file write、protected-path 权限试探、Sandbox、build/Cargo/AC1–AC7；未读取 dump 内容、用户漫画、DB、Lock、Revision、凭据或模型内容。R0 的只读授权没有改变任何 Gate。

### 风险状态与 P02PRE 分类

- `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；固定句=`technical condition unmet; user explicitly accepted residual risk`。只 waiver 创建前证明 private registry storage 不存在。
- profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；P02PRE=`BLOCKED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未运行，不是失败）。
- 已有局部 `PASS_WITH_EVIDENCE`：当前 PS identity/thread impersonation、冻结 host environment 读取、12 个 input root 精确 metadata/ACL、42 个 path 当前状态、WER candidate 当前有限 snapshot、固定 13 项 hash pre/post。
- 仍需 `REQUIRES_ACTIVE_TEST`：两个已存在 scratch leaf 的 empty inventory、canary/effective write boundary、真实 controller/probe/child/broker/WER/write closure。
- `UNPROVABLE`：private registry absence（保持 waiver 原值）、path ancestry/file identity/hardlink/ADS/full protected-invariants inventory/hash、WER policy/views/actual destination/future T0。
- `NOT_SAFE_FOR_R0`：profile folder getter/path、详细 token/elevation/capability P/Invoke。完整逐项理由以 R0 evidence 分类表为准；不能合并成任何整体 Gate PASS。

### 下一精确步骤 / Agent handoff

1. DSH availability 已核验：`dsh --version` exit 0 / `0.2.0-rc.2`；`dsh headless "只回复两个字：收到"` exit 0 / stdout=`收到`。这仅证明通路，不是 Review。
2. 按 DSH skill 及当前 evidence pins 创建自包含 prompt，再将只读 R0 Review 派发给 DeepSeek Harness；保存 prompt/stdout/stderr/exit/mount 日志。
3. 核验 DSH 返回内容与 session 后，按 `mount_session.py --latest` 挂载会话；Codex 单独 adjudicate Review，更新唯一 DAG 与状态。
4. 在新的用户裁决前，不调用任何 profile/API/create/delete/write，也不启动 build/Cargo/AC；Hard Build Barrier 持续 `EFFECTIVE`。

### Agent、模型与恢复

- R0 Reviewer Agent 尚未收到 Review prompt；DSH CLI=`0.2.0-rc.2`，probe 成功。之前 P02M11 Owner `/root/p02_gate_feasibility` 因 usage limit 未返回 handoff，报告文件存在但 `BLOCKED / NOT_VERIFIED`，不作为 R0 Review。Qoder 已退出项目，不分配。
- 本次 root runtime/model 未重新核实；最近已核验值仍为 `gpt-6-luna / max`（2026-10-10 16:53 UTC），不得声称实际使用 `gpt-6.1-sol / high`。
- 已更新的唯一规划/状态入口：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md` 与 `doc/tasks/P02PRE-R0.md`。本 checkpoint 自身为当前 rolling recovery point。

---

## 2026-10-11 06:48 Asia/Shanghai 前一恢复点（已由 07:29 更新取代）

### 仓库与工作区

- Repo=`G:\CODEX\New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；common-dir=`G:/CODEX/New Manga/.git`；`main...origin/main [ahead 1365 / behind 0]`。
- 本 checkpoint 创建前 safe NUL status=`exit 0 / 511 records / stderr empty`；`.git/index` before/after SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。本次 Git 查询使用 `GIT_OPTIONAL_LOCKS=0`、`git --no-optional-locks -c core.fsmonitor=false -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`；index 未发生变化。
- checkpoint 创建后再次 safe NUL status=`exit 0 / 512 records / stderr empty`；`.git/index` before/after SHA-256 仍相同，`git worktree list --porcelain`=`361`。此为最新恢复快照。
- 当前 `git worktree list --porcelain`=`361`，上个 checkpoint=`363`；不运行 prune，也不推测差异来源。HEAD/tree/index hash 与之前安全快照相同。所有原作者未提交内容保留；无 reset、clean、stash、覆盖、删除或 commit。

### 当前授权、Task 与 Gate

- 用户于 2026-10-11 正式授权创建并执行独立 `P02PRE-R0` 受控只读取证 Task。授权仅允许冻结清单里的无副作用只读查询；不是新的风险豁免或任何 Gate PASS。
- Task=`P02PRE-R0`，状态=`ACTIVE / NOT_RUN`，Owner/Author=`Codex /root`，Review 计划=`DeepSeek Harness`（待 evidence pin 后核验 DSH dispatch），Integrator/adjudicator=`Codex /root`。Task=`doc/tasks/P02PRE-R0.md`；manifest=`verification/P02/p02-readonly-preflight-r0-manifest-20261011.md`；结果=`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`。
- 固定第一项 R0 目标查询为当前 PowerShell 的 `WindowsIdentity.GetCurrent(false)` 与 `GetCurrent(true)`，按 manifest 核对 r6 固定 user/SID；若 SID/name 不符、出现 thread impersonation、结果不可读或取证异常，停止所有后续 OS/path/ACL/WER 查询。
- 后续只读范围为 manifest 固定路径/ACL、指定 process environment path 解析、r6 两个 WER registry 候选键与三个目录、固定治理文档与 `.git/index` hash。未知/未获准 getter 记 `NOT_SAFE_FOR_R0`；不调用任何 AppContainer profile API，不做任何写测试。
- 风险裁决保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；必须原样保留 `technical condition unmet; user explicitly accepted residual risk`。Waiver 仅覆盖创建前 proof of private registry absence。
- `P02PRE=BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。

### M11 中断与取证限制

- `/root/p02_gate_feasibility` 的 P02M11 turn 因 usage limit 失败，未发最终 handoff。其文件存在：`verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md`，`27825 bytes / SHA-256 15736303C3241E0C14106EFCAFB8583DF719A566D1879B7A7144B6D079A04A1F`。状态保持 `BLOCKED / NOT_VERIFIED`；文件尚未被 Reviewer/Codex adjudicate，不能视作完成交付。
- Owner 报告记录其首批误运行普通 `git status --short`，执行前没有 index hash；`index_side_effect=NOT_VERIFIED`。当前 `.git/index` SHA 与之前安全快照相同，不能追溯补足缺失的紧邻 pre-hash；不恢复、覆盖或试图重写 index。
- 创建 checkpoint 前 records=`511`，之前 safe snapshot=`509`；新增 R0 Task 与 manifest 是已知新增文档，但没有旧 snapshot 的完整原始 NUL 列表用于断言其他变更不存在。checkpoint 创建后最新 records=`512`。

### 已完成与未完成

- 已重读 AGENTS、Plan、Index、STATUS、Collaboration、P02 Task、R6 manifest、先前 readonly-preflight 候选与 STATUS 指向 checkpoint。
- 已将 `P02PRE-R0` 登记为独立 Task，更新唯一 `REBASELINE_PLAN` DAG、STATUS、Index、父 P02 Task，并冻结 R0 manifest。
- 已用 Microsoft Learn 直接文档核对 PowerShell/.NET identity/environment/path/ACL/registry/hash getter 语义；来源 URL 记录于 R0 manifest。没有执行任何 Windows API/registry/WER/token/path/environment/ACL 状态查询。
- 当前 continuation 的根 runtime 未重新核验；最近一次已核验 root runtime 为 `gpt-6-luna / max`（2026-10-10 16:53 UTC），优先配置 `gpt-6.1-sol / high` 不得被声称已用。一次 `python3 scripts/current_model.py` 因该脚本在 repo root 下不存在而失败，未改仓库。

### 精确下一步

1. 复算并固定当前 Task、manifest、Plan/Status/Index/Checkpoint 与 r6 对象 hash；核对基线 HEAD 不变。
2. 执行 manifest 指定的第一项当前 PowerShell identity/thread impersonation 只读检查并与固定 SID 比较。发现不符/异常立即停止其余 OS 查询。
3. 只有身份匹配且证据无异常时，按 manifest 有序执行其余精确只读查询；不得扩路径、枚举内容、调用 profile/registry getter、写 ACL/文件或运行子进程。
4. 写 R0 evidence，逐项分类 `PASS_WITH_EVIDENCE`、`FAILED`、`UNPROVABLE`、`REQUIRES_ACTIVE_TEST` 或 `NOT_SAFE_FOR_R0`。
5. 固定 Owner evidence pin 后，向非作者 DeepSeek Harness dispatch 独立 Review；若 dispatch 不可用，准确记录 `AWAITING_EXTERNAL_DISPATCH`。Reviewer 完成后由 Codex 单独 adjudicate 并刷新 Task 子图/Gate。

### 实际调用与禁止项

- 本轮使用 PowerShell `Get-Content`、`rg`、`Get-Item`、`Get-FileHash` 读取项目文档；只读 Git 元数据和 safe NUL status；以 `web.run` 打开/搜索 Microsoft Learn 官方文档。首次 Python 快照命令因 shell quoting 错误没有运行 Git；`scripts/current_model.py` 文件未找到；这两项均不是项目 Gate 证据。
- 实际调用 Agent：`/root/p02_gate_feasibility`（P02M11，usage limit 后 turn failed，artifact 存在）；本轮尚未 dispatch R0 Reviewer。此前 M10 Owner/Reviewer 证据及历史 Agent 记录保留于前 checkpoint/Plan。
- 未运行 AppContainer API、profile/Create/Delete、registry/ACL 写入、protected-path write probe、Windows Sandbox、提权、build、Cargo、AC1–AC7、项目测试或用户数据读取。
