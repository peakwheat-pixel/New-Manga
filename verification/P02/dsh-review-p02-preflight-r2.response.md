# P02 非提权宿主 Preflight R2 exact-head Review（非作者独立审查 · 只读）

## 0. 审查对象与身份

| 项 | 值 | 我的核验方式 |
|---|---|---|
| reviewed HEAD | `7d8951c28cd954d7e325cd53e7991f3bec87d971` | `git rev-parse HEAD` |
| reviewed tree | `1340c5282e32361c117f0aeacb670d412fe568c9` | `git rev-parse HEAD^{tree}`（与固定值一致） |
| parent | `b14c7d2750cc53f0ae4edae6f3f5435398edccc9` | `git rev-parse HEAD^`（与固定值一致） |
| task base / live main | `6855c113e6a44320d9555777900cfb78a218d383` | `git -C G:/CODEX/New Manga rev-parse HEAD` → 同值，branch=`main` |
| reviewer worktree | `C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`，branch=`codex/P02-process-isolation`，common dir=`G:/CODEX/New Manga/.git` | 只读 |
| worktree cleanliness | **clean**（审查前后 `git status --porcelain` 均 0 项） | 只读；本 Reviewer 未写任何文件 |
| 固定 commit 存在性 | `80cf5651`=change commit（tree `234cd26f`）、`cd3e86d6`=scope freeze、`b14c7d27`=R2 evidence commit、`561f4105`=R1 candidate（tree `2560664959`） | 全部 verify 通过 |
| base→HEAD 提交链 | `6855c113` → `561f4105` → `cd3e86d6` → `80cf5651` → `b14c7d27` → `7d8951c2`（5 commit） | `git show -s --format=%T %P` |

被审角色：Owner/author=Codex；非作者 Reviewer=DeepSeek Harness；Integrator=Codex。本 Reviewer 全程只读：未修改/暂存/提交/删除任何文件，未提权，未查询/更改任何 Windows Feature，未运行 `wsb`、Sandbox、clone、Smoke、Build、产品 runner、测试、GUI 或 WebView。

## 1. Decision

**`APPROVED`** — P0/P1/P2/P3 = **0 / 0 / 0 / 3**

R1 P2-01 已闭合；R1 P3-01..P3-05 全部按冻结范围修复且状态如实；26 路径候选全部落在冻结授权内（无越界、无产品/契约/测试/依赖改动）；root 保护清单 203/203、staged=0、路径交集=0 由我独立复算一致。3 项新 P3 均为文档/证据口径精度问题，不阻断集成。本文档/证据修复**可以集成**（见 §6）。

## 2. Findings

### N-01（P3）「24-path allowlist」与 r7 冻结清单不一致，且候选含 6 条未枚举的延续路径
- 证据：`verification/P02/codex-preflight-r2-validation.md:5`「The 24 current candidate paths equal the 24-path allowlist; unexpected paths=0」与 `:15`「Candidate paths=24」；对照 `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md:89–102`（r7「Allowed paths and exact scope」逐条枚举 27 条，其中 7 条在 HEAD 尚不存在：r2-review checkpoint + `dsh-review-p02-preflight-r2.*` 6 件）。
- 我实测：HEAD 候选 = **26** 路径（`80cf5651` 时 = 24）。其中 6 条未被 r7 枚举但存在于候选：`codex-scratch-build-preflight-inputs-r1.tsv`、`wsb-version-r1.{stdout,stderr}.txt`、`wsb-list-raw-r1.{stdout,stderr}.txt`、`codex-checkpoint-p02-non-elevated-preflight-start.md`；经 `git diff 561f4105..7d8951c2` 核验这 6 条**自 R1 candidate 起逐字节未变**，当时由候选自冻结范围 `codex-checkpoint-p02-preflight-scope-frozen.md:6` 覆盖并已被 R1 Review 接受。
- 影响：结论（无越界路径）成立，但「等于 allowlist / unexpected=0」无法仅凭 r7 机械复现；未来读者可能读成漏项。非阻塞。
- 关闭要求：把允许集表述为「r7 ∪ R1 candidate 已审冻结范围」，或直接列明这 6 条延续文件，并把「24」标注为 `80cf5651` 口径、`26` 为 reviewed HEAD 口径。

### N-02（P3）验证证据链只覆盖 `80cf5651`/`b14c7d27`，未覆盖受审 HEAD 的 4 份文档刷新
- 证据：`codex-preflight-r2-validation.md:4/:5/:15` 与 `codex-checkpoint-p02-preflight-r2-delivery.md:6` 均以 fixed change HEAD=`80cf5651`（24 路径）为口径；`codex-preflight-r2-validation.md:26` 自述下一步需「run validation once more on the resulting review target HEAD」；而 `git diff b14c7d27..7d8951c2` 仍修改了 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`，仓库内**无** `7d8951c2` 上的复跑记录。
- 影响：r7 §R2 acceptance（`scope-delta:104`）要求的 validator/link/diff 证据在受审 HEAD 上没有作者侧留痕（无虚假 PASS，属留痕缺口）。
- 我在 exact HEAD 独立复跑并留痕于此：`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` → EXIT=0（196 节点、分类/依赖/路由一致、`PASS: delivery/navigation local links resolve`、`live HEAD=7d8951c2`）；`git diff --check 6855c113..HEAD` → EXIT=0；changed-Markdown 相对链接扫描 = 15 文件 / 766 目标 / 10 missing（并回放 base blob 确认这 10 条在 `6855c113` 即已缺失，新增断链=0）；复跑后 worktree 仍 clean。
- 关闭要求（非阻断）：在 R2 review checkpoint / R2 validation record 中登记「validation rerun on `7d8951c2`」及上述结果，或注明该 4 段文档仅指针刷新、无新增链接与结构变更。

### N-03（P3）preflight start checkpoint 存在时间线与状态自相矛盾
- 证据：`verification/P02/codex-checkpoint-p02-non-elevated-preflight-start.md:3` 时间=`2026-10-09 15:58 UTC`（23:58 +08）、状态=`PREFLIGHT_SCOPE_FROZEN / READY_TO_RUN`；同文件 `:9` 却写「初始动作已完成：只读采集与状态同步已写入本候选」；而采集窗口为 `2026-10-10 00:03–00:09 +08`=`16:03–16:09 UTC`（`codex-scratch-build-preflight-r1.md:3`），比该 checkpoint 晚 5 分钟。
- 影响：start checkpoint 的「READY_TO_RUN」与「已完成」并存，读者可能误读为采集先于冻结完成。仅文档一致性，不涉及任何 Gate；该文件自 `561f4105` 起未变，属 R1 候选遗留。
- 关闭要求：在后续触碰时注明该完成句为交付时补记，或修正时间戳/状态标签。

## 3. 对 R1 条件与 P3 的逐项判定

| R1 项 | R2 判定 | 依据（我独立核验） |
|---|---|---|
| **P2-01** 授权基础不可审计 | **CLOSED（可集成前闭合）** | `scope-delta:81–104`（r7）在**修复 commit 之前**冻结于 `cd3e86d6`；明确记录用户 2026-10-10 持续有效的 `PROJECT_ORCHESTRATION_AUTHORIZATION` + 仓库 AGENTS.md 的 Codex 计划/状态/任务协调与集成角色（`:85`），并明文「supersedes earlier prohibitions on the named shared-document edits only to the exact extent listed below」（同段），逐条限定 4 份文档只改当前段与 P02 的 Codex-only Gate 记录（`:90–93`）。实测改动确未越段：INDEX 仅首个当前工作段、STATUS 仅「最新状态」段、PLAN 仅当前 checkpoint + 上一段降级标注、`doc/tasks/P02.md` 仅 Codex Scratch Isolation Preflight checkpoint 条目 + 1 句历史标注；AC/Owner allowlist/依赖/父状态零改动。残余观察（不计数）：该授权为**外部任务指令**、由作者自述入档，库内无独立版本化凭证；本次派发指令本身确认了该授权与 r7 引用方式，且 r5/r6 的禁止条款已被 r7 定向覆盖，故对本次精确修复足够。若日后用户撤回该授权，这 4 段编辑需重新取证；建议 P02 closeout 时在 Task 内引用同一授权记录。 |
| **P3-01** PASS 字样 | **CLOSED** | `codex-scratch-build-preflight-r1.md:23` = `MATCH_PREDICTED / CHECKOUT_NOT_RUN`，同行注明「此状态不表示 checkout PASS」；`doc/tasks/P02.md` 新条目亦写「source pins 仅 `MATCH_PREDICTED / CHECKOUT_NOT_RUN`」。全候选已无 `PASS_WITH_LIMIT` 残留（仅存在于 R1 response 对旧措辞的引述）。 |
| **P3-02** 机器可读测量/provenance | **CLOSED（含 1 条非阻断残余）** | `codex-scratch-build-preflight-observations-r1.json`：`captured_at=2026-10-10T00:25:26.8980781+08:00`、`capture_context.is_elevated=false`、PowerShell 7.6.6、`Win32_ComputerSystem.TotalPhysicalMemory_bytes`、`Win32_OperatingSystem.TotalVisibleMemorySize_KiB/FreePhysicalMemory_KiB(→MiB)`、`Win32_Processor.Name/Architecture/NumberOfCores/VirtualizationFirmwareEnabled`、`Win32_LogicalDisk freeBytes/sizeBytes/freeGiB`、当前用户 AppX `PackageFullName/Version/InstallLocation`、`TargetLength_bytes/TargetFileVersion/TargetSHA256`、命令清单与 CLI 证据窗口+exit codes。我复算全部单位换算：33,981,165,568 B=31.647 GiB；33,184,732 KiB=31.647 GiB；19,144,520 KiB=18,696.0 MiB；359,125,831,680 B=334.462 GiB；1,395,791,908,864 B=1,299.933 GiB —— 与报告/INDEX/STATUS/PLAN/P02/checkpoint 的摘要值**全部一致**；我另独立 `Get-FileHash` 复核 `wsb.exe`=156,160 B / `247e092b…c441`，与 JSON 及报告一致。残余：文件名为 `…-r1.json` 而 `captured_at` 是 R2 00:25 复测，R1 原值仅存于报告表格（R1/R2 区分在报告 `:19/:20/:32` 与各状态文档中已写明）——建议后续在 JSON 增加 `reading_round` 字段。 |
| **P3-03** 14 路径计数 | **CLOSED** | `codex-checkpoint-p02-non-elevated-preflight-delivery.md:5` 已写「4 个 doc 当前状态段 + 10 个 verification 证据文件（包含本 delivery checkpoint）构成，共 14 paths」；我实测 `6855c113..561f4105` = **恰 14 路径** = 4 doc + 10 verification（preflight-r1、inputs TSV、hostfolders TSV、4 个 wsb 原始输出、start、scope-frozen、delivery）。 |
| **P3-04** manifest HEAD 语义 | **CLOSED** | `head=549a6544f0be1eec66c09ece393fd1a409f10bf3` 经核验为 `6855c113` 的**祖先** commit（`docs(P02): record blocked scratch build gate`），报告/checkpoint/STATUS/PLAN/P02 均写明「冻结创建时 HEAD，而 203 条与 live main 匹配」。我独立复算 manifest 规范化哈希：36,985 bytes / `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`，与 manifest 自记及所有引用一致；live root `main@6855c113`、`git status --porcelain -z -uall` 203 条（199×`??` + 4×` M`）、逐条 path/status 比对 **203/203 match，missing/extra/status-mismatch=0/0/0，staged=0**。 |
| **P3-05** HostFolder 域/计数 | **CLOSED** | TSV 已有 `mapping_domain` 列，12 行 = **1 Scratch RW + 9 Smoke RO + 2 Build-only RO**（我解析确认）；`verification/P02/codex-p02-wsb-smoke-config-r3.xml` 实测 **11 条** `<MappedFolder>`（1 RW + 1 clone 内 canary RO + 9 输入 RO，**不含 Git**），故「12 个宿主根 vs 11 条映射」的口径区分属实、未混读。 |

## 4. 范围 / diff / 保护现场核对（问题 3）

- `base..HEAD` = **26 路径**：4 个 `doc/**`（全 M）+ 22 个 `verification/P02/**`（1 M = scope-delta r7，21 A）。**无**产品源码/测试/依赖/Schema/IPC/契约/用户数据路径；WSB XML 与 canonical hash 未被触碰（`codex-p02-wsb-smoke-config-r3.xml` 仍 2609 bytes，未出现在 diff 中）。
- 授权归属：22 条 verification 中 20 条被 r7 `:94–102` 枚举；余 6 条见 N-01，均为 R1 候选中已审、本轮未变的延续文件 → **无未授权改动**。
- 保护现场：root dirty ∩ candidate = **0**（我以 203 条 manifest 路径集与 26 条候选路径集独立求交）；root staged=0；`G:\CODEX\P02-scratch-build-source` 实测不存在（未创建）。
- 独立抽样 pins：`Python312\python.exe`、`nodejs\npm.cmd`、`rc.exe`、`yolo11s-seg.onnx`（40 MB）4/4 SHA-256 与 `inputs-r1.tsv` 登记值一致；`wsb.exe` 长度+哈希一致（见 P3-02）。

## 5. 虚假 PASS / 状态如实性（问题 4、5）

- 未发现虚假 PASS：报告中 `PASS` 均限定于已实测的宿主只读项（root manifest、非提权判定、WSB identity/version/session list、clone 不存在、架构/虚拟化、资源阈值、HostFolder 存在性、20 个文件 pins）；source pins 已降为 `MATCH_PREDICTED / CHECKOUT_NOT_RUN`；HostFolder 项明写「逐路径存在性检查」。
- 时间戳一致性：`00:03–00:09`（采集）、`00:07`（scope frozen）、`00:11`（delivery）、`00:22`（R1 review）、`00:25`（R2 复测/JSON `captured_at`）、`00:34`（R2 delivery + validation）与各自 UTC 换算正确、先后自洽；唯一例外见 N-03。
- 状态边界正确且跨文档一致：Feature=`UNKNOWN`（未查询）、完整 preflight=`BLOCKED / INCOMPLETE`、Smoke admission=`NOT_ADMITTED`、Smoke=`NOT_AUTHORIZED / NOT_RUN`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hook/cache 静态闭包=`BLOCKED / NOT_VERIFIED`、Hard Build Barrier 有效；4 份状态文档已无「P2-01/P3 正在修订」之类过期措辞，R2 未被表述为已批准（`DSH exact-head R2 Review 待派发，尚未集成`）。
- 路线/链接/差异证据如实：`verify_plan.py` EXIT=0（196 节点）我在 exact HEAD 复现；`codex-preflight-r2-validation.md:13` 的「13 Markdown / 765 targets / 10 pre-existing missing / 0 new」与其自身口径（fixed change commit，不含后加的 delivery+validation 两文件）自洽，我按 HEAD 口径得 15 文件 / 766 targets / 同 10 条 base 即缺断链，**0 新增**。
- 未运行声明属实：候选未声称运行过任何产品测试、Smoke、Build、Feature 查询或 AC 验收；我也未运行这些。R6 follow-up 引用（head `2394dc98`、N-06 closed、新 findings `0/0/0/0`）与 `dsh-review-process-isolation-r6.followup.response.md` 一致。

## 6. 结论与集成建议

- **Decision：`APPROVED`**（P0/P1/P2/P3 = 0/0/0/3）。R1 **P2-01 已闭合**；**P3-01、P3-03、P3-04、P3-05 关闭**，**P3-02 关闭**（附 1 条命名/口径残余建议）。
- **该文档/证据修复可以集成**：可对 reviewed HEAD `7d8951c2` 做本地 fast-forward；集成后按冻结验收复跑 route validator、`git diff --check`、目标 HEAD/tree、root 203 项 protected manifest 与路径交集。N-01/N-02/N-03 为非阻断 P3，可随下一次文档触碰一并登记（N-02 建议在集成前顺手把 HEAD 口径复跑写进 R2 review/delivery checkpoint）。
- 本决定**仅**确认文档/证据修复：Windows Sandbox Feature 仍 `UNKNOWN`；完整 preflight 仍 `BLOCKED / INCOMPLETE`；Smoke 仍 `NOT_ADMITTED / NOT_AUTHORIZED / NOT_RUN`；Build Gate 仍 `BLOCKED`、build 仍 `NOT_AUTHORIZED / NOT_RUN`；P02 AC1–AC7 仍 `BLOCKED / NOT_RUN`；Hard Build Barrier 继续有效。未运行产品测试、Smoke、Build、Feature 查询或任何 AC 验收，也不据此推导。

## 7. 下一条安全动作

> **给 Codex（Integrator，用于 `codex/P02-process-isolation` @ `7d8951c28cd954d7e325cd53e7991f3bec87d971`）：** R2 exact-head Review = `APPROVED`（0/0/0/3），P2-01 与 P3-01..P3-05 全部闭合，可本地 fast-forward 集成。集成前把「reviewed HEAD `7d8951c2` 上 route validator EXIT=0（196 节点）、`git diff --check` EXIT=0、相对链接 0 新增断链」记入 R2 review/delivery checkpoint（N-02）；把 N-01（allowlist 口径/延续路径）与 N-03（start checkpoint 时间线）登记为待触碰的非阻断文档项。集成后复跑 validator、`git diff --check`、目标 HEAD/tree、root 203 项 manifest 与路径交集，并刷新状态指针。**不得**提权、查询/启用 Windows Feature、运行 `wsb`、创建 `G:\CODEX\P02-scratch-build-source`、启动 Sandbox/Smoke/Build 或产品测试；Feature=`UNKNOWN`、完整 preflight=`BLOCKED / INCOMPLETE`、Smoke=`NOT_ADMITTED / NOT_AUTHORIZED / NOT_RUN`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier 保持有效。

**Reviewer 声明**：本次审查全程只读；未修改、暂存、提交或删除任何文件，未改动本 checkout、Git index、main root 或其他 worktree；未提权、未查询/更改/启用任何 Windows Feature、未运行 `wsb`/Sandbox/Smoke/Build/产品 runner/测试/GUI/WebView、未创建或改动 scratch clone、未访问用户数据或凭据；未执行的检查一律记为 `UNKNOWN`/`NOT_RUN`/`BLOCKED`/`NOT_VERIFIED`，未写为 PASS。