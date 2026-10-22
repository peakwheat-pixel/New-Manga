---
task_id: P02M
reviewer: Codex /root/p02_manifest_reviewer
author: Codex /root
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9
decision: changes_requested
---

# Review：P02 execution manifest r1

本次变更登记 private-registry absence 单项风险例外，并定义条件式 native LPAC synthetic probe 候选。它保留 Create 与 Build 的阻塞，不能作为 OS 执行许可。静态审查发现 1 项 P1、2 项 P2，均 open；应先修订并复审。

## 范围与依据

- Reviewer 为 `/root/p02_manifest_reviewer`，不是 manifest 作者 `/root`，也不是 Advisor `/root/p02_isolation_advisor`。角色配置由派发及 STATUS 明确为 `gpt-6.1-sol / medium`；运行时没有独立模型/effort introspection，不能声称另行核验实际后端。
- 仅审查 manifest 内容、范围、对象绑定与停止条件；仅写本报告。读取 Plan 当前裁决、STATUS 当前与 15:21 快照、00_INDEX、协作协议 §5.1/§6、Review 模板、P02 Task AC/范围与 :684–701、两份当前 recovery checkpoint、Advisor 全文、contract r7 身份/路径/ACL/进程/Gate 段落及 preflight r3 全文。旧 r7/r3 是历史输入，当前禁止直接执行。
- 实际 Git 只读核验：主仓 `G:/CODEX/New Manga`、branch=`main`、HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`、common-dir=`G:/CODEX/New Manga/.git`；开始时 porcelain 条目 396。命令 shell 为 PowerShell，返回 `exit_code=0`。这只是仓库核验，不是 token、profile 或 ACL 证据。
- 没有修改被审 manifest、Task、Plan、STATUS、代码或其他作者文件；没有执行 OS/API/profile/registry/ACL/token 查询、Sandbox、文件探针、build/Cargo、产品测试或 AC。

### Exact object binding

| 字段 | 派发 pin | Reviewer 实测 | 结论 |
|---|---|---|---|
| 对象 | `verification/P02/p02-owner-risk-waiver-execution-manifest-r1-20261010.md` | 同一路径 | MATCH |
| bytes | 19626 | 19626（`Get-Item ... Length`） | MATCH |
| SHA-256 | `8DB5B79DD1F4F166455E4769C4B06D0EB0DDE1CEE80822DE7F3137E4B15DD720` | 同值（`Get-FileHash -Algorithm SHA256`） | MATCH |
| 仓库 HEAD | `cddff58469b56e181019a8ddfeade80684bc7eb9` | 同值（`git rev-parse HEAD`） | MATCH |

`object_binding=VERIFIED`，仅针对本次精确 manifest bytes；不是对该 HEAD 全部 dirty 内容的批准，也不是 OS 对象绑定。文件尚未成为固定提交的 blob，因此内容身份由路径/bytes/SHA 补充绑定。

## Architecture：executed / CHANGES_REQUESTED

风险例外限于创建前 private-registry storage absence proof（manifest :7、Task :686–688），没有把技术条件写为 PASS。固定 user/moniker、空 capability、exact `S_OK`、失败不重试、拒绝复用及不自动清理均保留。r1 将 ACL 变更冻结为零；不存在可执行的 ACE mask 或 label mutation，任何未来变更必须 r2 重审。这一限制本身没有扩大 waiver。

profile-folder 前置证明、zero-capability Registry Getter、完整 WER bootstrap、native controller/probe 与 child/broker/write closure 明确保留为阻塞。修正 HANDLE_LIST/Job 通知充分性方向符合官方合同；没有把 synthetic 单进程结果推广到 build。身份来源和文件/证据边界仍有以下真实冲突，故不能批准本冻结对象。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| MR1-01 | P1 | manifest :18、:23；`doc/tasks/P02.md:691`；`codex-checkpoint-p02-owner-risk-waiver-start-20261010.md:15` | 固定 expected SID 的第四个哈希分量为 `2661600285`，既有 Derive 记录为 `2661602853`。两者是不同身份；按 :130 实测比较会阻塞，若直接沿用候选值则 profile-folder/token/ACL 身份不能与既有原始调用证据绑定。 | 静态字符串比较：Task :691、15:21 STATUS 与 start checkpoint :15 均记录 `...-2661602853-...`；r1 :18、当前 STATUS 与 review checkpoint :19 则记录 `...-2661600285-...`。本 Reviewer 未运行 Derive，不能裁定正确值。 | Codex 核对已有原始 Derive artefact；不足时记身份 `NOT_VERIFIED`，保留 Create 阻塞。保留 r1，形成有证据来源的 r2 身份 pin，澄清相关历史记录，并对新对象复审；不猜哪一位是笔误。 | open / 无修订 commit |
| MR1-02 | P2 | manifest :54、:58–64、:86、:103–109 | :86 写“scratch 根以外均禁止写入”及十二子树唯一许可；TEMP/TMP 却固定在 scratch 外的 profile `Temp`，正向 canary 也位于十二子树之外。若后续 Gate 放行 canary 或 TEMP 写入，执行者无法从同一冻结 allowlist 判断是否违规。零 ACL 变更并不解决文件写许可冲突。 | :63 与 :86 的字面范围冲突；:106 的 `verification/P02/tmp/lpac-write-control/` 不属于 :90–101 列出的 `tmp/`（它是 scratch 根直属 tmp）。:26 仅解释 Create 所生 profile store，不列 profile Temp 后续写许可。未实际写入。 | r2 分别明确 Create API 自身可能创建的对象、probe 实际文件写许可及未来 build/cache 候选。若 r1 范围不允许 profile TEMP 写，明确只回读映射并禁止写；canary 明确作为精确例外或继续未释放。不要泛化整个 profile 为可写。 | open / 无修订 commit |
| MR1-03 | P2 | manifest :120–121、:133、:136 | protected 清单包含主仓全部非 ignored untracked regular files，又要求任意新增/差异即停机；同轮治理证据在主仓新 evidence root 中逐阶段落盘，但没有冻结这些精确宿主写入与 pre/post 集合/时点的关系。若 pre-hash 后写 preflight/create-result 等再采 post，会因本轮合法证据触发停机；不同实现可临时排除 evidence 根而失去精确绑定。 | :120 明确新建 8 个阶段证据文件且每个测量进程停止后写；:121 对 `--others --exclude-standard` 集合要求同一集合且任何新增停机，未定义宿主证据精确例外、统一内存缓冲/最终落盘顺序或全程冻结集。Advisor §6.3/§8 已要求精确 exclusions 和阶段顺序。 | r2 冻结一条可执行顺序：例如在最终 post/WER/comparison 完成前将测量证据有界保留内存、测量停止后一次写精确已列文件；或先独立审查逐文件治理写 exclusion 与时点。记录容量/失败/中断处理，禁止事后排除整个 `verification/P02` 或 evidence 根。 | open / 无修订 commit |

这些 findings 是文档一致性问题，不是已发生越界、Create 失败或产品测试失败。:113、:127–136 已坦承未冻结的实现与方法，因此未把每个明确 blocker 重复登记成新 finding。

## Verification：静态审查已执行；OS/Create/Build release 为 BLOCKED

| 场景 | 实际命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 精确文档对象 | `Get-Item -LiteralPath <manifest>`；`Get-FileHash -Algorithm SHA256 -LiteralPath <manifest>` | PowerShell；上述 HEAD；exit 0 | PASS（仅文档绑定） | 本报告 exact binding 表；19626 bytes / 指定 SHA |
| 仓库恢复 | `git rev-parse HEAD`、`git branch --show-current`、`git rev-parse --path-format=absolute --git-common-dir`、porcelain 计数 | PowerShell；上述 HEAD；exit 0 | PASS（仅恢复信息） | main / 同 HEAD / 同 common-dir / 396 条 |
| waiver、身份、allowlist、证据顺序静态一致性 | 读取绑定对象与版本化依据，逐条交叉比较 | 本精确 manifest | FAIL | MR1-01..03；没有以实际运行失败命名 |
| Microsoft 公开合同 | 通过 web 读取下列官方文档及相关字段 | Microsoft Learn，2026-10-10 本轮读取 | PASS（仅来源读取） | 下方直接官方链接；不证明本机状态 |
| 固定 token/SID/Create/Profile precheck | 未执行；任务明令禁止 OS/API | 当前 HEAD | NOT_RUN / release BLOCKED | 身份证据冲突及 profile-folder 无副作用方法未验证 |
| Registry Getter、ACL、TEMP/cache、安全路径、pre/post hashes、WER、child/broker/write closure | 未执行；任务明令禁止查询或探针 | 当前 HEAD | NOT_RUN / release BLOCKED | 没有 OS artefact；不得用本文替代 |
| Sandbox/build/Cargo/AC1–AC7 | 未执行；任务明令禁止 | 当前 HEAD | NOT_RUN / BLOCKED | Hard Build Barrier 仍 EFFECTIVE；没有 build/AC 结果 |

静态读取的终端输出是本次审查工具结果；未另存运行日志，唯一允许写入为本报告。上述 PASS 不代表 P02 产品 Gate、隔离 Gate 或 AC PASS；没有测试数量可汇总。

### 已核对的官方合同与边界

- Create 返回值及 current-user profile/folders/registry 语义支持严格一次调用与失败归属处理；不提供全事务回滚保证。[CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)
- Folder API 返回路径并受调用身份影响；该页没有完整创建前无副作用 absence 合同，不能仅凭此页关闭前置条件。[GetAppContainerFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerfolderpath)
- Getter 绑定 current profile/current user；API 页未给出 zero-capability LPAC 例外或无额外初始化保证。LPAC 文档称 registry 访问需 `registryRead`，所以 r1 :32/:134 的阻塞有效。[GetAppContainerRegistryLocation](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getappcontainerregistrylocation)、[Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)
- HANDLE_LIST 需要 `bInheritHandles=TRUE`；r1 选择 FALSE 且不使用 HANDLE_LIST，后续增加需重审。[UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
- 普通 Job 通知不保证送达，PID 也可能退出/复用；不能据此证明所有短命后代 token。[JOBOBJECT_ASSOCIATE_COMPLETION_PORT](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port)
- WER LocalDumps 可有 per-image override 和自定义 DumpFolder，且独立于其他 WER 开关；冻结默认三目录无法单独证明 destination 闭包。[Collecting User-Mode Dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps)

### 阻止下一阶段 release 的未知项

1. **OS preflight**：未冻结已审 native controller、精确 DLL/EXE、API/access masks/flags、超时、stdout/缓冲协议、完整环境块和安全 bootstrap。:109 的 READ_CONTROL 读取意图不能替代 file-ID/reparse/hash 各自 API 合同；r1 不得借旧 r7/r3 或 Advisor API 候选临时补实现。
2. **Create**：除 MR1-01 修订外，profile-folder 前置无副作用路径/缺失证明仍未知；zero-cap LPAC Getter 资格与副作用仍未知；准确 WER 映像/views/destination/T0 许可顺序未冻结；scratch/canary/ACL/label/file-ID/ADS/hardlink/inventory、protected baseline 与证据根新鲜度均没有实际证据。waiver 不覆盖这些问题。
3. **probe resume**：实际 LPAC token 字段不变量、Job/child policy、无 broker/COM/外部特权 handle 的实现与强制边界尚无已审代码或执行证据。禁止以 polling、self-report、hash MATCH 或无 Job 通知解除。
4. **Build/Hard Barrier**：真实 compiler/package manager/WebView 后代 allowlist、完整 token 与写入闭包没有冻结及验证；single-process synthetic probe 即使未来成功也不满足。ACL 当前零变更，现有授权不够即 BLOCKED，不能现场补 ACE 或 label。
5. **清理**：r1 的停止、保留现场、不自动 Delete/递归清理规则清楚；不存在可执行删除授权。未来确需清理必须先冻结精确对象所有权、关闭句柄/进程顺序、API、结果与重试上限，另审；不能借 :26 猜 moniker 残留属于本轮。

## 结论与复审

`decision=changes_requested`。Architecture 因身份绑定和授权/证据范围冲突要求修订；Verification 仅静态范围已执行，全部安全执行项仍 NOT_RUN，关键证据缺失阻止 OS/Create/Barrier release。本 Review 不允许 Create、profile/registry/ACL/file 变更、build/Cargo、AC 或 Sandbox。风险接受继续为单项 `WAIVED_BY_OWNER`，技术事实仍 `NOT_SATISFIED`；未撤销用户裁决。

推荐下一步为 **Codex 的 P02M r2 文档修订与 adjudication**。恢复点为主仓 `G:/CODEX/New Manga`、`main@cddff58469b56e181019a8ddfeade80684bc7eb9`；现有 r1 保持不变。Owner=Codex；Reviewer 必须为非作者，可继续本 Reviewer。依赖是本报告及既有用户 waiver；允许路径须由 Codex 在 Task/STATUS 重新明确，建议新 `verification/P02/p02-owner-risk-waiver-execution-manifest-r2-20261010.md` 与精确 adjudication/恢复记录，禁止产品代码、其他作者未提交内容及一切 OS/API/build 操作。本建议不自行释放新范围。

可直接转发给 Codex：在 `G:/CODEX/New Manga` 的 `main`、base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9` 完成 P02M 文档 adjudication。先登记 r2 允许路径并处置 MR1-01..03：核对已有 Derive 原始 artefact、不猜 SID；明确 scratch/profile TEMP/canary 精确写入范围；冻结 protected 清单与宿主证据落盘顺序。保留 r1 及本 Review，交付新 r2 bytes/SHA、findings disposition 与 checkpoint，派非作者复审。仅读文档/Git/官方合同，所有 OS/API/profile/registry/ACL/token/文件探针/Sandbox/build/Cargo/AC 保持 NOT_RUN，Hard Build Barrier 保持 EFFECTIVE；未解决方法记 BLOCKED，不记 PASS。

未检查：任何本机 OS 安全状态、二进制、代码执行、build 或 AC；本次仅静态文档审查。
残余风险：用户只接受 registry 创建前 absence 证明缺失，其他未知安全条件仍阻止执行。
