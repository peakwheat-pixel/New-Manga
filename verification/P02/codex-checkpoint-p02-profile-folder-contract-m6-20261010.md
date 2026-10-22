# P02 Rolling Checkpoint：profile-folder 创建前 API 合同评估（P02M6）

## 恢复基线

- 时间：2026-10-10 16:10 UTC。仓库=`G:\CODEX\New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；`main...origin/main [ahead 1365]`；Git common-dir=`G:/CODEX/New Manga/.git`；登记 worktree=`363`。
- 原作者未提交/未跟踪文件继续保留。未 reset、clean、stash、覆盖、删除或 commit；Codex 仅在已登记的 P02/治理文档范围新增或修改文档。
- 最新 safe workspace status 快照：`git --no-optional-locks -c core.fsmonitor=false -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`，同时设 `GIT_OPTIONAL_LOCKS=0`；PowerShell exit=`0`，stderr 空，NUL records=`491`。命令前后 `.git/index` SHA-256 均=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`，大小=`972663 bytes`，LastWriteTimeUtc=`2026-10-10T03:18:18.4750975Z`。这只证明该次 safe status 前后 index 快照一致。
- 重要限制：Codex 此前为 CLI 语法确认实际运行过一次未加 `--no-optional-locks` 的普通 status 命令，exit=`0`、stdout 丢弃；运行前未记录 index hash。运行后的快照 mtime/hash与当前一致，但无 pre-hash 就不能证明当时前后逐字节一致。未重置、覆盖或恢复 index，不把这段说明当 P02 Gate evidence。

## 当前任务与交接

- 唯一 Active 产品 Task=P02；唯一 Active 子任务=`P02M6`，Owner/Author/Integrator=`Codex /root`；非作者 Reviewer=`/root/orchestration_docs_review`，状态=`running`。唯一 Owner 输出=`verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-20261010.md`，`6053 bytes / SHA-256 CF77049EEB7A2C276FBD35A9A7AFF6FD2B4076E2B03FD4CED33BDF7EE47D0BCC`。唯一 Reviewer 写入=`verification/P02/codex-p02-profile-folder-noncreating-contract-assessment-review-20261010.md`。Review 限静态文档合同分析；禁止 Git status、OS/API/profile/registry/ACL/path probe、Sandbox、build/Cargo、AC。
- 最近完成的 P02M5：r5 manifest=`28956 bytes / SHA-256 B97FB2115C17476AAE768368B315D438FB8BE4CC2C5072C88FF36A79DAB1D6E1`；非作者 Review=`APPROVED`（0/0/0/0），报告=`12410 bytes / SHA-256 69D5B01F3DE015C6476C57AB03D46CF58166750CB9ECCDD553172EC4CB3D7F8E`；Codex adjudication=`verification/P02/codex-p02-owner-risk-waiver-manifest-r5-adjudication-20261010.md`。结论只批准精确 manifest 的静态文档，不批准任何运行。
- 最近实际有效 checkpoint 为 2026-10-10 15:55 UTC 的 r3 Review checkpoint。之后新增：r3/r4/r5 Review 与 Codex adjudication 全部收口；r5 MR4-01 修正获得独立静态批准；P02M6 当前 profile-folder path getter 合同分析已交审。未有技术 Gate 变化。

## 用户授权与执行 Gate

- 必须保留用户原句：`technical condition unmet; user explicitly accepted residual risk`。
- `private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`。
- waiver 仅限“创建前无副作用证明目标 private-registry storage 不存在”；profile-folder no-side-effect 不在 waiver 内。
- 当前：`profile_folder_no_side_effect=UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未执行，不是失败）。P02PRE/P02A/P02G/P02AC 仍 BLOCKED。
- 其它 blocker：zero-capability Registry Getter 资格/副作用；WER images/views/destination/T0；native controller/probe source/binary/argv/environment/API/buffer/error state/bootstrap；TEMP/cache/scratch/input/output/file identity/ACL/label 与 pre/post protected hashes；完整 child/broker/COM/WER/write closure；evidence collector/partial incident 实现；真实 build descendants 边界。P02M5 通过不解除这些项。

## P02M6 已完成步骤与证据

1. 静态读取 Microsoft Learn：`GetAppContainerFolderPath`、`SHGetKnownFolderPath`、`KNOWN_FOLDER_FLAG`、`CreateAppContainerProfile`、`Launch an AppContainer`。报告区分了“返回路径映射”与“该 getter 绝不创建”的合同保证。
2. 初步结论：公开合同说 getter 返回 Local AppData 路径且映射到 `SHGetKnownFolderPath(FOLDERID_LocalAppData)`，但未明确 no-create 行为、目标目录缺失时结果或内部 flags；known-folder 文档只明确 `KF_FLAG_CREATE` 会强制创建、`KF_FLAG_DONT_VERIFY` 控制存在性验证，不能直接证明 getter 的内部行为。因此维持 `UNPROVABLE / BLOCKED`，等待 Review 与 Codex adjudication。
3. 不据推断调用目标 API，不查找/猜测 SID 路径，不做实际存在性探测；没有运行任何 OS/API/build/Cargo/AC/Sandbox。

## 精确下一步

- 等待 `/root/orchestration_docs_review` 完成唯一写路径的 Review；完成后由 Codex 复算 Owner report 与 Review 的 bytes/SHA，对官方合同、引用和推断边界作 adjudication。
- 若 Review 认定公开合同不足，`P02PRE` 保持 BLOCKED；继续寻找正式版本化合同或非破坏替代。若最终只能扩大 profile-folder 风险接受，必须由用户单独决定；不得套用 registry waiver。
- 只有所有执行前安全条件都有独立证据并由 Codex 明确通过对应 Gate，才可能解除 Hard Build Barrier；随后才允许依顺序 Build 与 AC1–AC7。出现未知子进程、未授权写入、身份不符或证据异常立即停止。

## 实际 Agent、工具和命令

- `/root/p02_manifest_reviewer`：完成 r5 静态 Review；P0/P1/P2/P3=`0/0/0/0`。`/root/orchestration_docs_review`：P02M6 静态 Review 在途。`/root/p02_isolation_advisor`：本轮未派新任务。所有 Agent 的模型运行时身份/effort未由工具独立暴露；P02 manifest Reviewer 角色配置=`gpt-6.1-sol / medium`；Owner 配置=`gpt-6.1-sol / high`。
- 本轮读写/状态命令包括 PowerShell `Get-Content`、`Select-String`、`Get-Item`、`Get-FileHash`、安全参数的 `git rev-parse`、上述显式禁用 optional locks/fsmonitor 的 porcelain status（exit 0/490 records/index前后hash相同）、`Copy-Item` 创建 r5（复制前确认源/目标路径在仓库内且目标不存在）及文档 patch；用 web 搜索/打开 Microsoft Learn 官方文档。
- 没有运行产品 tests、P02 AC、OS/API/profile/registry/ACL/token/path probe、Sandbox、build 或 Cargo。
