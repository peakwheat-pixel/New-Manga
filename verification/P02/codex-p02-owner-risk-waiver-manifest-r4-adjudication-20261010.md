# P02 execution manifest r4 Review adjudication

## 固定对象

- 仓库=`G:\CODEX\New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- 被审 r4=`verification/P02/p02-owner-risk-waiver-execution-manifest-r4-20261010.md`，`28347 bytes / SHA-256 DFB2A7DFABBA4BF5F8D17788DC5FD22534DA692A2848918CD4E978D63CA5C300`；Reviewer 核验 pin 匹配。
- 非作者 Review=`verification/P02/p02-owner-risk-waiver-execution-manifest-r4-review-20261010.md`，`11629 bytes / SHA-256 33F2C2712663742CDE00C4CEFEE7E0AA2BD0E7D93B51F9B1B51700D1A0C7A145`；决策=`CHANGES_REQUESTED`；P0/P1/P2/P3=`0/0/1/0`。
- Reviewer=`/root/p02_manifest_reviewer`，非 r4 作者；任务角色配置=`gpt-6.1-sol / medium`，运行时 model ID/effort 未独立暴露。Review 文件为其唯一写入路径。

## Findings 与 Codex 处置

- MR3-01：r4 已在文档层把完整 raw status 与 `protected-status-projection` / `authorized-output-status-deltas` 分开，授权 canary 不再与 raw-status 全等规则冲突。此处置不替代 parser 或执行实现 Review。
- MR4-01 / P2：确认。r4 固定命令没有 `--no-optional-locks`；Git 默认 background refresh 可能写 index 并创建 `index.lock`，破坏 manifest 的宿主无写入和 index hash invariant。Reviewer 未运行该 status 命令，finding 是命令契约风险，不是 Reviewer 证明本机已发生 index 写入。
- Codex 更早实际运行过一次未加 `--no-optional-locks` 的 status 命令用于 CLI 语法确认：`git -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`，PowerShell exit=`0`，stdout 被丢弃。执行前 index hash 未保存，故不能证明前后字节完全一致；执行后只读采样 `.git/index` 为 `972663 bytes / SHA-256 214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`，LastWriteTimeUtc=`2026-10-10T03:18:18.4750975Z`，未发现 `.git/index.lock`。不恢复或覆盖 index；现有 mtime/hash 仅为当前快照，不能替代缺失的 pre-hash。
- Codex adjudication=`CONFIRMED / FIXED_IN_R5_PENDING_INDEPENDENT_REVIEW`。保留 r4 与 Review 原件，创建 r5，将固定命令改为 `git --no-optional-locks -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`。此参数只抑制 Git optional-lock 操作，不作为 Git config、fsmonitor、submodule、helper、controller/descendant 无副作用的完整证明；这些边界仍需后续实现冻结和证据。
- r5=`verification/P02/p02-owner-risk-waiver-execution-manifest-r5-20261010.md`，`28956 bytes / SHA-256 B97FB2115C17476AAE768368B315D438FB8BE4CC2C5072C88FF36A79DAB1D6E1`，已冻结待非作者 Review。Review 通过与否不自动释放 preflight/Create/Build/AC。

## 治理状态与限制

用户 waiver 原值保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。仅豁免创建前以无副作用方式证明目标 private-registry storage 不存在，不豁免其余安全条件。

profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未执行，不是失败）。本 adjudication 与静态 r5 修订均不等同于技术 Gate 或 AC PASS；没有执行 OS/API/profile/registry/ACL/token/path probe、Sandbox、build/Cargo 或 AC。

下一项 Active=`P02M5`：非作者对精确 r5 hash 的静态 Review；Codex 只接受对应 Review 路径写入。若发现问题，保留旧版本并修订新 manifest。所有 Create/OS/API/profile/registry/ACL/probe/build/Cargo/AC 仍禁止，直至各自条件有独立证据且明确完成 Gate。
