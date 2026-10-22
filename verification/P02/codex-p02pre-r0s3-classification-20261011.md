# P02PRE-R0S3 Delivery：剩余条件分类与安全候选收口

## 对象、基线与方法

- Task=`doc/tasks/P02PRE-R0S3.md`；Owner/Author=`Codex /root`；Reviewer=`DeepSeek Harness`；Integrator/Adjudicator=`Codex /root`。
- Repo=`G:/CODEX/New Manga`；branch=`main`；base/head=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- 目的：按用户规定的五种状态重新分类 P02PRE 剩余条件，并判定现有证据是否支持另一个安全、可执行的 R0 capture Task。
- 方法：静态阅读和 pin 版本化 Task、manifest、evidence、Review、adjudication；比较其已记录的执行事实与限制。没有运行目标机 query、Windows API、Registry/WER、ACL/path/hash probe 或任何产品测试。
- Root runtime model/effort=`gpt-6-luna / max`，`python3 scripts/current_model.py` 的输出固定于 `verification/P02/codex-p02pre-r0s3-runtime-20261011.json`（local session trace，`2026-10-11T00:51:56.615Z`）。当前环境实际配置不是优先请求的 `gpt-6.1-sol / high`；不声称使用后者。顾问 advice 未独立绑定 runtime model/effort，不作为事实来源。
- `/root/r0s1_manifest_advisor` 只读意见认为无可释放的新 R0 capture；该意见没有独立文件/bytes/SHA pin，故只作为规划线索。Codex 对照下表版本化来源独立复核后形成结论。
- 初版 Delivery=`2026-10-11 08:55 Asia/Shanghai`；Round 1 修订版 freeze=`2026-10-11 09:06 Asia/Shanghai`；状态=`IN_REVIEW`。Round 2 Review 绑定本版 Delivery、Task 和下表 pins。

## 结论

**当前没有能在已冻结工具边界下安全执行的新增 R0 只读取证项。** R0S2 的 getter body 尽管是只读候选，PowerShell 实际 executable/argv、profile、module analysis cache、PSReadLine history 与 `exec_command` wrapper/temp/log 行为仍无无副作用证明；因此 runner=`NOT_SAFE_FOR_R0`，HKLM `LocalDumps` 两视图查询=`NOT_RUN`，键当前状态=`UNPROVABLE`。不尝试更换 Python、Node、cmd 或其它 runner；任何新 runner 都必须先单独冻结并 Review 启动和 wrapper 边界。

没有已执行且失败的 AC 或测试：`FAILED = ∅`。R0S1 在任何 G: path query 前安全停止；R0S2 被 Review 否决且没有运行。安全停止和 NOT_RUN 都不是失败。

## 剩余条件分类

分类针对“条件对象”和“当前采集方法”分别填写；某个条件可以是 `UNPROVABLE`，同时其候选 getter/runner 为 `NOT_SAFE_FOR_R0`。下表完整合并 R0、R0S1、R0S2 adjudication 的既有行；`NOT_VERIFIED` 是 r0 index 证据的原始记录属性，不是第五枚举的替代值。

| 条件 / 证据对象 | 条件分类 | 当前采集方法分类 | 判定边界与来源 |
|---|---|---|---|
| PID 12280 host process 的实际 user/SID/thread impersonation | `PASS_WITH_EVIDENCE` | `PASS_WITH_EVIDENCE`（仅当次采集） | 不外推子进程身份或未来状态；R0 evidence/adjudication。 |
| Host process 冻结 environment 原始值与词法 path parsing | `PASS_WITH_EVIDENCE` | `PASS_WITH_EVIDENCE`（仅 host process） | 不代替 future child environment 检查；R0 evidence/adjudication。 |
| PID 51516 的 `HOMEDRIVE+HOMEPATH` 与 host `USERPROFILE` 组合 | `PASS_WITH_EVIDENCE` | `PASS_WITH_EVIDENCE`（辅助进程） | 仅辅助进程当时点；future child home mapping=`REQUIRES_ACTIVE_TEST`。 |
| 12 个 input roots 精确 leaf metadata/ACL、13 个 scratch leaf 存在状态及两个 canary 当前状态 | `PASS_WITH_EVIDENCE` | `PASS_WITH_EVIDENCE`（限冻结 getter/对象） | 不证明 ancestors/effective access/未来 LPAC 权限；R0 adjudication。 |
| 精确 ACL SDDL/descriptor | `PASS_WITH_EVIDENCE` | `PASS_WITH_EVIDENCE`（descriptor only） | descriptor 不等于 effective access；R0 adjudication。 |
| 两个现存 scratch leaf 是否 empty-or-absent | `UNPROVABLE` | R0S1 continuation runner=`NOT_SAFE_FOR_R0` | R0S1 在任何 G: path query 前以 `STOP_UNTRUSTED_OR_UNAVAILABLE_BUILTIN_MODULE` 停止；无目标返回。 |
| R0S1 trusted-module continuation predicate 的本机事实 | `UNPROVABLE` | 冻结 continuation method=`NOT_SAFE_FOR_R0` | stop code 不能推出 module count/path/install state；R0S1 evidence/adjudication。 |
| R0S1 frozen `Get-ChildItem` direct-child inventory | scratch emptiness=`UNPROVABLE` | `NOT_SAFE_FOR_R0` | 读取 child names/metadata，与冻结承诺不兼容；未执行。 |
| R0S1 capture 的精确 timestamp、stderr 独立可得性、实际 executable/完整 argv、cmd bytes binding | `UNPROVABLE` | 对已完成的 capture 不可追补 | R0S1 adjudication L39 已列 capture metadata unknown；不重新运行、不回填。 |
| R0 `index_side_effect` | `UNPROVABLE`（副作用未得到前置证据） | 原始审计标记=`NOT_VERIFIED` | R0 adjudication 明记普通 `git status --short` 前缺紧邻 index pre-hash；后来 hash 一致不能补证，不恢复/覆盖 index。 |
| r6 evidence root 与十个冻结 evidence files 的当次 absence | `PASS_WITH_EVIDENCE` | `PASS_WITH_EVIDENCE`（限该清单/时点） | 不证明未来 freshness、并发或路径身份；R0 adjudication。 |
| 三个已登记 WER 候选目录与 candidate key 的受限快照、13 个 protected-file pre/post hashes | `PASS_WITH_EVIDENCE` | `PASS_WITH_EVIDENCE`（限精确候选与当次对象集） | 不证明完整 protected set、WER policy/destination 或 T0；R0 evidence/adjudication。 |
| 未创建 profile 的 exact folder path / pre-create absence | `UNPROVABLE` | `GetAppContainerFolderPath` 候选 getter=`NOT_SAFE_FOR_R0` | 不猜 SID 路径；不调用缺少成功/失败全分支无副作用合同的 getter。R0 旧 adjudication 的合并状态在此拆分为谓词与方法，Gate 未放宽。 |
| Target private registry storage 创建前 absence | `UNPROVABLE` | `GetAppContainerRegistryLocation` zero-capability getter=`NOT_SAFE_FOR_R0` | eligibility/effective write boundary/success-failure no-write 未证；仅保持用户明确 waiver。 |
| HKLM LocalDumps Registry32/Registry64 当前打开结果 | `UNPROVABLE` | R0S2 PowerShell startup/profile/wrapper runner=`NOT_SAFE_FOR_R0` | query=`NOT_RUN`；`login=false` 不证明 `-NoProfile`；不得改换 runner。 |
| WER 实际 reader/view/global/per-image effective policy、完整 image 集合、expanded actor/dump destination、安全 T0 | `UNPROVABLE` | 当前未冻结 raw-value/per-image runner=`NOT_SAFE_FOR_R0` | 即使未来安全取得两个 view 的局部观察，也不能证明 WER 实际 reader/destination；M9/M11。 |
| Token elevation/capabilities、reparse ancestors/file IDs/hardlink/ADS、完整动态 protected invariants 与全量 hash freshness | `UNPROVABLE` | 未冻结 P/Invoke/dynamic inventory/helper=`NOT_SAFE_FOR_R0` | 固定 R0 13 hashes 与局部 metadata 不构成完整集合；r6/M10。 |
| Effective LPAC access、实际 canary allow/deny、future child/broker/WER process tree、TEMP/cache/scratch/output 写闭包、停机清理与未来状态 | `REQUIRES_ACTIVE_TEST`；未实现的精确对象/清单同时=`UNPROVABLE` | 不属于当前 R0 safe read-only capture | 需要未来独立冻结的 controller/probe/identity/input-output manifest；当前 Build Barrier 有效。 |

**`FAILED = ∅`**：没有执行失败的 R0 query 或 AC。R0S1 是安全停止；R0S2 query 与 AC1–AC7=`NOT_RUN`，不改写为失败。

## Round 1 Review 与修订记录

DSH 非作者 Round 1 Review=`NOT_VERIFIED`，P0/P1/P2/P3=`0/0/2/6`；stdout=`verification/P02/dsh-p02pre-r0s3-review-round1-20261011.md`，bytes=`16114`，SHA-256=`3CC2846857A3F2972D5CA02F3B12D314063C8DE8628AC1C3E0F33F342FCF9BF3`；dispatch `.exit=0`。DSH 内容核对支持候选结论，未发现虚假 PASS、扩权或 P0/P1；但其 sandbox 无法独立重算 bytes/SHA 与 tree，故此 verdict 暂不作为最终 Review Gate。

Owner 在 Round 2 前完成的处理：

- P2-01：加入 R0S1 capture metadata=`UNPROVABLE` 与 R0 `index_side_effect=NOT_VERIFIED` 行，保持“未证”与“未运行”边界。
- P2-02：先前 live `doc/STATUS.md` 的 08:47 block 错称 R0S2 Review 在途、M11 未 Review；新的 09:06 current block 已同步 R0S2=`blocked / NOT_SAFE_FOR_R0` 与 M11=`DONE`，并由本 Delivery 的 pin 表固定该状态快照。更晚的 Review/adjudication 状态更新将作为正常的后续状态变化单独记录。
- P3-01/02/03：表格现在分开记录条件与方法分类；`FAILED=∅` 移到表外；profile path predicate=`UNPROVABLE` 与 getter=`NOT_SAFE_FOR_R0` 明确拆分，未放松原 Gate。
- P3-04：补齐可用的源 Task、M7–M11 Owner/Review/Adjudication 与当前状态快照 pins；活文档只代表 Delivery 时点，不冒充 commit 内容。
- P3-05：实际 root model/effort 输出单独固定为 runtime JSON artifact；不推断 Reviewer 或 Advisor 配置。
- P3-06：Round 2 stdout 将 byte-preserving 归档到 Task 声明的官方 Review 路径，并记录 `.exit`、stderr hash 与 session mount。

## 风险、Gate 与执行状态

用户裁决保持原值：

- `private_registry_absence=UNPROVABLE`
- Technical Gate=`NOT_SATISFIED`
- Owner Risk Acceptance=`APPROVED`
- Gate Disposition=`WAIVED_BY_OWNER`
- Build Authorization=`AUTHORIZED_WITH_EXCEPTION`
- 原文=`technical condition unmet; user explicitly accepted residual risk`

P02PRE=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。本 Task 不授权 API/Create/Build/AC，也不查询、安装、启用或启动 Windows Sandbox。

## 静态来源 pins

下表记录交付基线时的精确输入；独立 Reviewer 应自行重算 Task 与 Delivery pin，并抽查完整分类所引用的源文件 pins。

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` | 99592 | `AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3` |
| `verification/P02/p02-readonly-preflight-r0-review-20261011.md` | 29404 | `427F582D87A54E8C5B7CB65FB72F1B067BD226B8E6DFA66873FDC996E6B5C554` |
| `verification/P02/codex-p02pre-r0-adjudication-20261011.md` | 11145 | `E66131960E35A35C8E6F051EFE0F1C167CEBE2DBC78D849DA00A2642D901375E` |
| `verification/P02/p02-readonly-preflight-r0s1-evidence-20261011.md` | 5489 | `05C2DD247D3B0238809DCB90E62B633AAD6B4E777186E4025CD371B371F3FCBD` |
| `verification/P02/p02-readonly-preflight-r0s1-review-20261011.md` | 21262 | `2F27B72FB40D43F7B4DD40925E75283A151EC7E72327D1FD2542F6135DC0E7A0` |
| `verification/P02/codex-p02pre-r0s1-adjudication-20261011.md` | 9413 | `6A4B53B4B0E6955BDBA8F4D8E3C37FA9FF12478C5BF7497382AC1EA5EEBF1422` |
| `doc/tasks/P02PRE-R0S1.md` | 8763 | `C1648322870A59439FFBCAB2A0A7F79687BB94EB2FF182B881F7F570308B92E5` |
| `verification/P02/p02-readonly-preflight-r0s1-manifest-20261011.md` | 22925 | `CA293C34473D25E406E72B7DB05AC9364A69544D41214B93857ABAD11FEC6DE3` |
| `doc/tasks/P02PRE-R0S2.md` | 9015 | `B9A7EFDBC4207CB5258F48BCF1FC0B39DC3C7E467829DB5E210AC6D113A34B90` |
| `verification/P02/p02-readonly-preflight-r0s2-manifest-20261011.md` | 7710 | `589DCD21C0C98128468A8758D433D630D6F3318409025B4F9FE26C548DB2F2FD` |
| `verification/P02/p02-readonly-preflight-r0s2-review-20261011.md` | 19235 | `4EE88FF450005A59E7D3B0B2E36F3D96DEE61038CF95B1BE28B28F642656B19E` |
| `verification/P02/codex-p02pre-r0s2-adjudication-20261011.md` | 8604 | `8D1D395BB284C10AABA9560759F940D96BA7CCB9DE04107B056427AB5D2B91B1` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` | 44307 | `626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE` |
| `verification/P02/codex-p02-profile-folder-versioned-contract-adjudication-20261010.md` | 3985 | `DFE1F6EEAC9C3AF332D3050FD51CE281169264C6D4D56346AF82FE5791400631` |
| `verification/P02/codex-p02-zero-capability-registry-getter-adjudication-20261010.md` | 4259 | `7AA918590AF737A0824BFE292620DCA3824E5E9710AE97BC4D725E9FE5CB4E3C` |
| `verification/P02/codex-p02-wer-per-image-bootstrap-adjudication-20261010.md` | 3127 | `F59409529E0D4E8BB35A833D9B894B92B612068DEA1AD151231DF4ED76F9F334` |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md` | 5560 | `01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159` |
| `verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md` | 27825 | `15736303C3241E0C14106EFCAFB8583DF719A566D1879B7A7144B6D079A04A1F` |
| `verification/P02/codex-p02-unwaived-gate-feasibility-review-20261011.md` | 5857 | `F3578C9D041C8FAE91AAF329B4385A4AC94E1E44DF73633765C18DD82C2B7905` |
| `verification/P02/codex-p02-unwaived-gate-feasibility-adjudication-20261011.md` | 4101 | `5317DB3741E48536C903CC9A91FA3FCE15722DD553A3E7528A6007757AF962A6` |
| `doc/tasks/P02PRE-R0.md` | 7748 | `6935E686DA65A336BFC3EF93222E8EA079F7F2BFE3FB1B79462B3E0A8ABBECA7` |
| `verification/P02/codex-p02-profile-folder-versioned-contract-research-20261010.md` | 23075 | `BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A` |
| `verification/P02/codex-p02-profile-folder-versioned-contract-research-review-20261010.md` | 10860 | `D54339A8A7B85049023D5BAB4C96E4071D2C4DC6AB01E26CF0E4210CB1458E0D` |
| `verification/P02/codex-p02-zero-capability-registry-getter-contract-research-20261010.md` | 15483 | `8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6` |
| `verification/P02/codex-p02-zero-capability-registry-getter-contract-research-review-20261010.md` | 14456 | `52BE5F8B3E8164564A15927D58265531F7137D4D8DE2B36993389C94C97C5155` |
| `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md` | 17105 | `6207483ED6CE62650C346D18D42FC81CD5102C44A028BAF0DE4F131AF60411F3` |
| `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-review-20261010.md` | 13059 | `E5E71E1B28F76B4FFF8190D27E7A6B56F13559090BDB8251EABFEFE2350EE7B7` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md` | 23380 | `A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8` |
| `verification/P02/codex-p02pre-r0s3-runtime-20261011.json` | 309 | `E78FD2A79A6EB94BDDDEA28A4C401394F4E03E9B78D8E5BA6FA6D6B2065ACF37` |
| `doc/tasks/P02PRE-R0S3.md` (frozen Round 2 Task) | 5340 | `361BD7F02CFBFEC6FB6B700B2DD9FCE10DFB0BD0D6998BB8978ADE2B1FB4378D` |
| `doc/STATUS.md` (09:06 current-state snapshot) | 260460 | `B4375872C5546D28EE69B77B2E404D930F21DF4DF86C9340D895C4299AE89AF4` |
| `doc/REBASELINE_PLAN.md` (09:06 DAG snapshot) | 237987 | `4327D4BBA38811A73E531238BF46139E5B233E998F75A4867A6501B8F28FC07D` |
| `doc/00_INDEX.md` (09:06 recovery/index snapshot) | 46506 | `1EE3903A4E1F5675E01BA208124F24B07FBCF8C2EF042AE4B07B942460DB62C4` |
| `doc/tasks/P02.md` (09:06 current subtask record) | 212081 | `04E2E340AA0ECF1F2F6E1C98418529032F81F134B7FDDCECD71B39F61CF9F6F3` |

> pin 表共 34 个文件：26 个静态 evidence/research/Review/adjudication/runtime metadata pins、3 个历史 Task pins、1 个冻结的 R0S3 Task pin、4 个 mutable current-state 快照。四个状态快照仅代表 09:06 文档状态，不冒充 commit 内容。Task 与 Delivery 的 bytes/SHA 由 Round 2 prompt 外部绑定，Delivery 自身不自引用其 hash；后续状态更新由 rolling checkpoint 与 adjudication 记录。
