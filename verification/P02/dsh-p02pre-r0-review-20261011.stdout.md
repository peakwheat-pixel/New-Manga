# P02PRE-R0 独立 Review（对象：`verification/P02/p02-readonly-preflight-r0-review-20261011.md`）

## 0. Review 元数据

| 字段 | 值 |
|---|---|
| Review ID | `P02PRE-R0-REVIEW-20261011-DSH-01` |
| Reviewer | DeepSeek Harness（非作者；未参与 R0 manifest/evidence 编写） |
| Owner / Author | Codex `/root` |
| Integrator / Adjudicator | Codex `/root`（本 Review 不代替其裁决） |
| 日期 | 2026-10-11（Asia/Shanghai） |
| 被审对象 | `P02PRE-R0` Task、R0 manifest、R0 evidence，及其依赖/治理 pin 文件（见 §1） |
| 基线 | repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b` |
| 结论枚举 | `APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`（限定采纳范围见 §5） |
| Finding 计数 | P0=0；P1=0；P2=5；P3=6 |
| Gate 效力 | **无**。本 Review 不授予、不放行、不改变 P02PRE、Technical Gate、Build Gate、Hard Build Barrier、AC1–AC7 的任何状态 |

## 1. 被审文件 pins（由 Codex 在 Review 前固定；本 Reviewer 未执行任何命令、未重算本地状态）

| 对象 | bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R0.md` | 6473 | `FE04EBDDA5BDE0312A498F5A191CE07A32751B3096254B0D0B0F8244292694FD` |
| `verification/P02/p02-readonly-preflight-r0-manifest-20261011.md` | 11567 | `8D2977BD0B7310F04E05FDF44D89F5B38981C64AD93E9BE3C2F97366FDDC9ECE` |
| `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` | 99592 | `AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3` |
| `doc/tasks/P02.md` | 205841 | `7CD0CF655A556A9F681629DC44B23AB7F54B7B308789762B13E0AC3DC60989EB` |
| `doc/REBASELINE_PLAN.md` | 226162 | `D9E70DA2A7A16D330483DD3DCCDBDC5D711969C7185030E709001AD152E498AE` |
| `doc/STATUS.md` | 252181 | `97CEB9B0FBC3488152F5DBC199627B20765B944CB50B6CF023CB33E3ADC6A626` |
| `doc/00_INDEX.md` | 42650 | `2FCD361FE6DE96D94AF31510CD1425AF9BC257BF39F30DD92B0F5F5240C298A0` |
| `verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md` | 13189 | `C584EF6B08AC04D84745081E97C3C5D18FF0CDC651C6299251FEBEC0D1A0910E` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` | 44307 | `626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE` |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md` | 23380 | `A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8` |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md` | 5560 | `01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159` |

## 2. Method 与 Limitations

**方法**：仅对上述 11 个固定文件做文本审查。逐项核对 R0 manifest 的冻结范围与停止条件、R0 evidence 的执行记录/表/机器可读 JSON/分类表、R0 Task 的验收文本、r6 合同与被裁决的 r6 Review/adjudication、以及 checkpoint 与四个治理入口中与 R0 有关的状态陈述；对计数、对象枚举、分类枚举做逐行比对。

**限制**：

- 本 Review 未执行任何命令、测试、Git 状态、哈希重算、系统/API/registry/ACL/path/environment/WER 查询，未启动任何进程，未写任何文件；因此 **pins 的 bytes/SHA-256 与宿主实际状态均按派发给定，未独立复算**。对象绑定来自派发等值，不等同于 Reviewer 复算。
- 结论只针对交付文本的范围、绑定、分类与表述；不含任何从文本推导的技术 PASS，也不判断真实 OS 对象当前是否存在/可访问。
- 未读取上表以外文件；四个大文档只做与 R0 有关的定向检索与摘录，不对治理文档做全量审计。
- Review 明确不裁决授权是否充分，只指出授权绑定缺口；最终由 Codex adjudicate。

## 3. 逐问结论（Q1–Q7）

### Q1「manifest 是否在宿主查询前冻结；最终 capture 是否只调用许可 getter；是否绑定同一先核验进程身份」

- **manifest 冻结**：manifest §94–96 自述「本 manifest 在任何 R0 OS/path/ACL/WER 查询之前冻结……当前 `NOT_RUN`」，且其文本不含任何查询结果；checkpoint 06:48 段（早于 R0 capture 窗口 `2026-10-10T23:16:33Z`）已记「冻结 R0 manifest」。**结论：与冻结前一致，但目前没有独立 pin**（R0 manifest 被自身 §69 排除在 hash 集合之外）→ 见 **P3-6**。
- **许可 getter**：最终作为证据的调用与 manifest §21 清单一致（`WindowsIdentity.GetCurrent`、`Environment.GetEnvironmentVariable`、`Path.GetFullPath`、`Get-Item`、`Get-Acl`、`OpenSubKey(...,false)`、`Get-ChildItem`、`Get-FileHash`），未出现写 API、P/Invoke、`Add-Type`、AppContainer/profile API 或外部子进程调用记录。**例外**：`Get-Item -LiteralPath -Force`、`Get-ChildItem -LiteralPath -Force` 使用了清单未列出的 `-Force` → 见 **P3-1**。
- **同一进程身份绑定**：**部分成立**。主 capture 绑定 PID=12280（evidence L22「在主要查询进程 PID=`12280` 中首先执行」），机器可读记录中 identity `atUtc=23:16:33.9414550Z` 早于所有带时间的 registry/WER 记录（`23:16:34.193Z`–`.208Z`），且均在窗口结束 `23:16:34.2092070Z` 内；但 `HOMEDRIVE + HOMEPATH` 组合校验跑了**第二个 PowerShell 进程**（evidence L9），其身份只有文字声明、无机器可读身份记录 → 见 **P2-1**。
- 另有一批**未冻结枚举**的父组件只读诊断（evidence L35），输出被截断 → 见 **P2-2**。

### Q2「42 path / 35 env / HOMEDRIVE+HOMEPATH / 2 registry key / 3 WER 目录 / 13 hash 的内部一致性、越界与缺失」

内部一致性核对结果（文本比对）：

| 组 | 计数核对 | 结论 |
|---|---|---|
| 精确路径 | manifest §35–50 枚举 12+13+3+1+13=**42**；evidence L87–131 表 42 行；JSON `paths` 42 项；`PRESENT=17 / ABSENT=25` 与 `counts.paths` 一致 | 一致，无越界对象 |
| 环境变量 | manifest §27 列 **35** 名；evidence L45–81 表 35 行；JSON `environment` 35 项；非路径 5 项（`isPath:false`） | 名集一致 |
| 非路径变量固定值比较 | manifest §27 要求记录「非路径变量是否等于 r6 固定值」；evidence 仅记 `(unset)` | **缺失** → P2-4 |
| HOMEDRIVE+HOMEPATH | evidence L43/L53–54 记 `C:`+`\Users\49745`，组合 `C:/Users/49745` 与 `USERPROFILE` 一致；单独 `HOMEPATH` 的 `G:\Users\49745` 已标明为片段 | 表述诚实，但组合结果与执行进程绑定不完整 → P2-1、P2-4 |
| registry | manifest §59–60 两键；evidence 与 JSON `registry` 2 项；`view=Default`、`writableRequested=false`（HKLM present / HKCU absent） | 一致，无枚举越界 |
| WER 目录 | manifest §62–63 三目录；`childCount=10/11/63`；JSON 子项与 markdown 表计数一致（CrashDumps 10、ReportQueue 11、ReportArchive 63；ReportArchive 63 项为计数+结构+抽样名称一致，未逐名两两对照） | 一致 |
| 固定 hash | manifest §69 列 12 文档+`.git/index`=**13**；evidence L233–247 13 行；JSON `hashesPre/hashesPost` 各 13 项，逐项 pre=post 相同；`.git/index` 值与 manifest §8 的值相同 | 一致（窗口内）→ 但与 Review pins 不同，见 P3-4 |

越界与缺失汇总：越界为父组件批次（P2-2）、第二 PowerShell 进程（P2-1）、`-Force`（P3-1）、WER 两键相对 r6 的读取口径（P2-5）；缺失为非路径变量比较（P2-4）、路径对象采样时间与批次进程归属（P3-2）、NUL status 原始输出/哈希与 509→512 差异解释（P3-3）、manifest 冻结时点 pin（P3-6）。

### Q3「父组件诊断批次偏差是否要求 changes requested」

**不要求 `CHANGES_REQUESTED`，但必须限定证据采纳范围。** 理由：该批次（evidence L35「包含精确对象及其父组件，工具返回内容被截断，无法确认该次逐对象输出」）只使用只读 `Get-Item`/`Get-Acl`，未产生写；其输出不可重建，已明确「不作为证据」；最终结论只依赖 42 个冻结对象批次。但它确实违反 manifest §33「不递归……遇到 reparse ancestor、无法确认路径组件……停止该路径并记录 `UNPROVABLE`」的对象冻结约束，因此：(a) 不得据此推断任何祖先/父组件元数据成功或失败（包括**不得**推测未捕获输出为成功）；(b) 42 个对象的祖先/reparse 状态只能保持 `UNPROVABLE`——evidence L85「祖先组件、file ID、hardlink、ADS 与 canonical identity 未证明」与分类表 L265 已如实保留；(c) 后续 freeze 必须显式枚举允许的祖先对象或明文禁止祖先查询。判级 **P2**（见 P2-2）。

### Q4「第一次 WER 批次无效与有限 snapshot 的表述」

**符合要求，无需修正。** evidence L36 明确「首次 WER 目录批次因 PowerShell 数组优先级错误，将三个路径拼成一条无效路径，回报 `ABSENT`；该结果不是三个候选目录的查询」，随后同进程按三个精确路径重查（`atUtc=23:16:34.2036199Z/…2060242Z/…2085287Z`，均在主窗口内）。evidence L142 明确「采样不是 future controller 的安全 T0，也没有枚举 WER policy values、per-image/global policy、registry view alternatives、dump destination……」；分类表 L267 将 WER policy/view/destination/future T0 记为 `UNPROVABLE`。全篇未见把该 snapshot 说成 T0、真实 dump destination 或 WER policy 证明。

### Q5「分类是否准确区分局部观察/缺失证据/动态行为；是否把 waiver 当技术 PASS 或放行 Build Gate」

分类表 14 行逐行核验：

| # | evidence 行 | 条件 | 分类 | Reviewer 判定 |
|---|---|---|---|---|
| 1 | L255 | 当前进程 user/SID/thread impersonation | `PASS_WITH_EVIDENCE` | 准确（caveat 覆盖未来 controller token/PID/elevation） |
| 2 | L256 | 当前 Process 环境变量/TEMP/cache/HOMEDRIVE+HOMEPATH | `PASS_WITH_EVIDENCE` | **需限缩 scope 并补非路径比较** → P2-4 |
| 3 | L257 | 12 输入根 leaf 元数据/ACL | `PASS_WITH_EVIDENCE` | 准确（祖先/file ID/LPAC access 已列为未证） |
| 4 | L258 | 13 scratch leaf 当前存在状态 | `PASS_WITH_EVIDENCE` | 准确（明示只描述当前 leaf 状态） |
| 5 | L259 | 两个已存在 scratch leaf 的 empty-or-absent | `REQUIRES_ACTIVE_TEST` | **分类不精确** → P2-3 |
| 6 | L260 | canary ACL 正/负行为与真实 write boundary | `REQUIRES_ACTIVE_TEST` | 准确 |
| 7 | L261 | r6 evidence root 与十文件 absence | `PASS_WITH_EVIDENCE` | 准确（未来新鲜度/并发已声明） |
| 8 | L262 | profile folder path / pre-create absence | `NOT_SAFE_FOR_R0` | 准确，与 manifest §51 一致 |
| 9 | L263 | private registry absence | `UNPROVABLE` | 准确，waiver 未被写成 PASS |
| 10 | L264 | 详细 token/elevation/LPAC capability | `NOT_SAFE_FOR_R0` | 准确 |
| 11 | L265 | path ancestry/file ID/hardlink/ADS + full protected-invariants hash | `UNPROVABLE` | 准确 |
| 12 | L266 | 当前 WER 候选有限观察 | `PASS_WITH_EVIDENCE` | 准确（限制段在 L142） |
| 13 | L267 | WER policy/view/destination/T0 | `UNPROVABLE` | 准确 |
| 14 | L268 | controller/probe/子进程/COM/broker/WER/短命进程/build descendants 闭包 | `REQUIRES_ACTIVE_TEST` | 准确 |

- **无 `FAILED` 行是准确的**：没有任何已冻结局部条件存在直接相反证据（例如两个 leaf 存在并不违反「empty-or-absent」，因为「empty」仍可能成立；只读 ACL 失败也未发生：17/17 `READ`）。
- **waiver ≠ 技术 PASS**：evidence L14/L16/L263 与 manifest §13/§15 均保持 `private_registry_absence=UNPROVABLE`、`Technical Gate=NOT_SATISFIED`、`Gate Disposition=WAIVED_BY_OWNER`、原文 `technical condition unmet; user explicitly accepted residual risk`；治理入口一致（`STATUS.md:11`「不是新风险豁免或 Gate PASS」、`P02.md:59`「不能把该条件写为技术 PASS」）。
- **未放行 Gate**：evidence L278 与 `STATUS.md:15/17`（「任何 Gate、Build Barrier、AC1–AC7 或产品状态均未放行/改变」）、`REBASELINE_PLAN.md:13` 一致，均为 P02PRE=`BLOCKED`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。四处治理文档均无「R0 已完成 / Review 已通过」文字（`P02PRE-R0=ACTIVE / EVIDENCE_CAPTURED / REVIEW_PENDING`）。

### Q6「六类未解决项是否被如实保留为未解决」

| 要求保留项 | evidence 位置与短引用 | 判定 |
|---|---|---|
| 两个已存在 scratch leaf 的空目录条件 | L135「不能证明 r6 要求的『empty or absent』」；L259 分类 | 已保留，但分类标签需修正（P2-3）；且 r6 §119「非空、无法列全……时 BLOCKED」在分类表中无对应行 |
| 路径祖先 / reparse / file-ID / hardlink / ADS | L85「祖先组件、file ID、hardlink、ADS 与 canonical identity 未证明」；L265 `UNPROVABLE` | 已保留 |
| ACL effective access | L85「其中出现写能力 mask 不等于有效 token access 结论」；L138「不能据此推断 LPAC 实际 access」 | 已保留 |
| 未来 child token / cache / TEMP | L43「不能将 host 值当作未来 controller/LPAC child 的 environment readback 或写入闭包证据」；L256 | 已保留 |
| WER policy / view / destination / T0 | L142；L267 `UNPROVABLE` | 已保留 |
| private registry | L262 `NOT_SAFE_FOR_R0`；L263 `UNPROVABLE` | 已保留 |
| 完整 protected-invariants hash | L29「仅为固定文档子集，不是 r6 完整动态 protected-invariants inventory/hash」；L249；L265 | 已保留（manifest §71 同义） |
| 未知子进程闭包 | L268「本轮没有启动 API/probe/build 或子进程，因而没有动态 OS 执行证据」 | 已保留 |

### Q7「工具错误与普通 `git status` 缺紧邻 index pre-hash 是否被隐去或错误描述；治理读取与主要 R0 OS query 是否区分」

- **已披露，未隐去**：helper 定义顺序失败、无可捕获 stdout 批次、父组件批次截断（L33–35）、WER 数组错误（L36）、普通 `git status --porcelain` 无紧邻 pre-index hash（L37「该命令属于 Codex 治理状态读取，不属于主要 R0 OS 查询进程」）、`Get-Content`/`rg` 治理文档检索（L39）。checkpoint 亦独立记录同样三项偏差（L22–24）并把普通 status 记为 `index_side_effect=NOT_VERIFIED`（L9）。
- **描述正确性**：L37「不回溯证明前次调用无副作用」与 checkpoint L9 语义一致；未发现把未验证事项写成已验证。
- **区分程度**：L37/L39 已把治理状态读取与主要 R0 OS query 分开；但 NUL status 与 `.git/index` hash 的**执行进程**未声明（L8 只记命令与结果，L39 又断言主要 R0 进程无子进程）→ 见 **P3-2/P3-3**。

## 4. Findings

| 级别 | 数量 |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 5 |
| P3 | 6 |

### P2-1（P2）HOMEDRIVE+HOMEPATH 组合校验在第二个 PowerShell 进程执行，身份绑定只有文字声明

- **位置/短引用**：manifest §19「所有调用由本 Task 的当前 PowerShell 进程执行；身份查询是第一项目标系统状态查询」；evidence L9「随后仅为校验 `HOMEDRIVE + HOMEPATH` 组合，另一个同用户/SID 且无 thread impersonation 的 PowerShell 进程于 `2026-10-10T23:17:30.4412666Z` 运行 `Path.GetFullPath`」；evidence L24；机器可读 capture 仅含 PID=12280 的 identity 块。
- **影响**：manifest 的「同一进程」绑定对主 capture 成立，但对这一条辅助查询不成立；该进程的 SID/无 impersonation 无机器可读记录，组合结果（`C:/Users/49745`）也只存在于叙述文本中，JSON 中 `HOMEPATH.fullPath=G:\\Users\\49745` 是**单值**解析结果，不能替代组合结果。该行 `PASS_WITH_EVIDENCE`（L256）因此有一半支撑落在未绑定进程上。
- **最小修订**：或在绑定进程内重做该组合校验并记录其 identity/时间；或将该行限定为「主进程 `USERPROFILE`/`HOMEDRIVE`/`HOMEPATH` 值读取成功 + 组合校验属跨进程未绑定旁证」，并把组合结论标 `UNPROVABLE` 直至重采；同时在 manifest/evidence 记录这一偏差。

### P2-2（P2）父组件诊断批次访问未冻结对象集合且输出不可重建

- **位置/短引用**：evidence L35「有一个路径诊断批次包含精确对象及其父组件，工具返回内容被截断……父组件集合未冻结枚举；因此该批次不作为证据」；manifest §33「遇到 reparse ancestor、无法确认路径组件……停止该路径并记录 `UNPROVABLE`」；manifest §80 停止条件。
- **影响**：这是对冻结对象枚举（而非 getter 类别）的实际越界；被访问对象集合无法从交付物重建，故「仅访问清单内对象」的范围断言不可独立验证。好的一面：结论不依赖该批次，evidence L85/L265 已把祖先身份留为 `UNPROVABLE`。
- **最小修订**：在 manifest 停止条件与 evidence 偏差段显式写「该批次违反 §33 的对象冻结，非 PASS 证据，且不用于推断祖先状态」；后续 freeze 明确「允许/禁止祖先元数据查询」二者之一。**不要求 `CHANGES_REQUESTED`**；采纳范围限定为 42 个精确对象。

### P2-3（P2）两个已存在 scratch leaf 的 empty-or-absent 分类与定义不符，且未映射 r6 的 BLOCKED 停止条件

- **位置/短引用**：evidence L259「当前必须 empty-or-absent 的两个已存在 scratch leaf | `REQUIRES_ACTIVE_TEST` | R0 不读取目录内容」；manifest §78 定义「`REQUIRES_ACTIVE_TEST` 表示必须运行后续受控 API/写入/真实子进程测试才可证明」；r6 §119「每个目标在执行前须精确 inventory：不存在或为空方可用；非空、无法列全、reparse/hardlink/ADS/ACL 不明时 BLOCKED」。
- **影响**：目录是否为空只需一次**只读、非递归枚举**即可判定，不属于「API/写入/真实子进程测试」；写成 `REQUIRES_ACTIVE_TEST` 会把「本 Task 合同内采样不足」误表述为「必须动态测试」，可能推迟一个只读即可完成的执行前必查项，并使 r6 §119 的 `BLOCKED` 语义在分类表中没有落点（checkpoint L32 沿用同一标签）。
- **最小修订**：该行改为 `UNPROVABLE`（原因：R0 冻结 scope 明确排除目录内容枚举）并增加一句「按 r6 §119，该 leaf 在执行前必须 inventory，当前状态等价 `BLOCKED` 待枚举」；同步 checkpoint 同一分类。

### P2-4（P2）环境行未记录非路径变量与 r6 固定值的比较，且行 scope 与 r6 子环境固定映射语义混淆

- **位置/短引用**：manifest §27「只记录路径变量的原始字符串与词法绝对路径，及**非路径变量是否等于 r6 固定值**」；evidence L71/L80「`HF_HUB_DISABLE_IMPLICIT_TOKEN` … `(unset)`」等 5 项；r6 §100/§102/§109/§113 固定 `PYTHONDONTWRITEBYTECODE=1`、`PYTHONNOUSERSITE=1`、`HF_HUB_DISABLE_IMPLICIT_TOKEN=1`、`GIT_CONFIG_NOSYSTEM=1`、`GIT_TERMINAL_PROMPT=0`；evidence L256 行标题「当前 Process 冻结环境变量……`HOMEDRIVE+HOMEPATH` | `PASS_WITH_EVIDENCE`」。
- **影响**：(a) manifest 明文要求的比较结论缺失，且实际值是 `unset ≠ 1/1/1/1/0`（即 host 进程不满足 r6 固定映射），只能靠读者自行推断；(b) r6 §99 要求 `HOMEDRIVE+HOMEPATH` 组合等于 scratch `tmp\home`，而观测值指向 host profile `C:\Users\49745`；正文 caveat（L43）已声明 host 值不能代替 child readback，但 `PASS_WITH_EVIDENCE` 的行标题容易被读成 r6 子环境条件已满足；(c) `HOMEDRIVE` 的 `Path.GetFullPath("C:")` 是「C 盘当前目录」语义，表内 `C:\` 与 `HOMEPATH` 的 `G:\Users\49745` 都属片段，需行内注记（`HOMEPATH` 的注记已在 L43/L54，但 `HOMEDRIVE` 的 `C:\` 无行内说明）。
- **最小修订**：为 5 个非路径变量补「≠ r6 固定值（unset）」列/脚注；把 L256 行标题限定为「host 当前 Process 环境读取成功（非 r6 子环境合规）」；对 `C:`/`\Users\49745` 的单独 `GetFullPath` 结果加行内「片段，drive-relative 解析」注记。

### P2-5（P2）WER 两键读取与 r6「不是当前读取许可/继续禁止实际读」之间的授权 delta 未绑定

- **位置/短引用**：manifest §57–60（把两键列为 R0 查询对象）；evidence L27（HKLM present / HKCU absent）；r6 §66「此处字符串保持 r5 候选，不是已解析实际目标，**也不是本轮读取许可**」；r6 Review L63「同时明确不是当前读取许可」；r6 Review L80「保留原候选上限并**继续禁止实际读**」；R0 Task front-matter `approval: user_authorized_read_only_preflight_20261011`（授权原文与对象枚举不在本次 pins 内）。
- **影响**：读取本身是只读存在性查询（`OpenSubKey(path,false)`，未枚举 values/subkeys），未发现写副作用；但读取依据只有 Task 中对用户授权的**指称**，其原文与确切对象范围不可从固定 pins 自证。这属于 scope/授权绑定问题，须由 Codex adjudicate，不能由 Reviewer 代为裁决，也不能作为「r6 已授权读取」的翻案。
- **最小修订**：在 manifest/evidence 增加「authorization delta」段：引用用户 2026-10-11 授权原文、说明其精确枚举，并声明 R0 的 WER 候选读取是**另行授权的有限只读范围**，不修改 r6 §66 与唯一 waiver 的边界。

### P3-1（P3）使用了冻结 getter 清单未列出的 `-Force` 开关

- **位置/短引用**：manifest §21 只冻结「`Get-Item -LiteralPath`（指定对象元数据）」「`Get-ChildItem -LiteralPath`（只列 WER 目录直接子项）」；evidence L25「`Get-Item -LiteralPath -Force`」、L28「`Get-ChildItem -LiteralPath -Force`」。
- **影响**：`-Force` 只读，无状态改变，但会扩大可见对象集合（hidden/system），严格说超出「仅执行冻结 getter/query」的字面范围。
- **最小修订**：在 manifest 明文允许或禁止 `-Force`；evidence 调用表列出完整参数。

### P3-2（P3）机器可读 capture 缺逐批次进程与时间归属

- **位置/短引用**：evidence L29（hash「查询前/后各一次」，无时刻）、JSON `paths` 各项无 `atUtc`（仅 registry/WER 有）、JSON `counts`（L1776–1799）只含 paths/wer/hashesEqual，无 environment/registry 计数；evidence L8（NUL status 与 `.git/index` 值）与 L39「主要 R0 OS 查询进程未调用外部程序……或子进程」。
- **影响**：无法把路径观测与 hash 前后时刻独立排序到 identity 之后；NUL status/index hash 究竟由哪个进程执行未声明——若在 PID 12280 内执行，则 L39 的「无子进程」断言与 `git status` 派生 `git.exe` 冲突；若在其它进程，则该部分记录的进程归属不清。
- **最小修订**：为路径批次、hash pre/post、NUL status 分别记录执行 PID 与开始/结束时间；`counts` 补 environment/registry 计数（manifest §65 已要求 registry/WER 逐对象时间，可同规则扩展）。

### P3-3（P3）NUL status 记录数差异未在 evidence 内解释，原始 stdout/哈希未保存，命令字符串相对 r6 有变体

- **位置/短引用**：manifest §8「冻结前安全 NUL status=`exit 0 / 509 records`」；evidence L8「exit `0`，512 records」；checkpoint L8/L57/L73「513 / 512 / 511 … 之前 safe snapshot=509」及「没有旧 snapshot 的完整原始 NUL 列表用于断言其他变更不存在」；r6 §158 冻结命令含 `-c core.quotepath=false`，evidence L8 实际命令增加 `-c core.fsmonitor=false`；checkpoint L9 把普通 status 记为 `index_side_effect=NOT_VERIFIED`，evidence L37 无该标签。
- **影响**：三个数字的差异只在 checkpoint 中有部分解释（新增 Task/manifest 与 checkpoint/evidence 文件），evidence 内未交叉引用，读者无法从交付物独立核验「512 records / exit 0」，也无法排除其它 worktree 变化。
- **最小修订**：保存 NUL status 原始 stdout 或其 SHA-256；在 evidence 引用 checkpoint 的 509/511/512/513 序列解释与 `index_side_effect=NOT_VERIFIED` 标签；注明 `-c core.fsmonitor=false` 属相对 r6 §158 冻结字符串的**收窄性变体**（降低副作用面，但仍应显式记录）。

### P3-4（P3）evidence 的 13 项 hash 与本次 Review pins 不同，须防止被当成 Review 对象绑定

- **位置/短引用**：evidence L238 `doc/STATUS.md = 1163E219…` vs 本 Review pin `97CEB9B0…`；L241 `doc/tasks/P02PRE-R0.md = FB7E6D98…` vs pin `FE04EBDD…`；L236/L237/L240 与 `doc/REBASELINE_PLAN.md`/`doc/00_INDEX.md`/`doc/tasks/P02.md` 的 pins 亦不同；L242 checkpoint `C3CDC95E…` vs pin `C584EF6B…`；而 L243–L245 的 r6 manifest/review/adjudication 与 pins **一致**。
- **影响**：这不是 evidence 内部矛盾（窗口内 pre=post 成立，L249），但该 13 项集合只证明 **capture 窗口内** 文档未被改写，不能作为 Review 时对象身份的证据；治理文档在 capture→Review 之间确实发生了追加（否则 hash 不会变）。
- **最小修订**：在 evidence 或 adjudication 明确「13 项 hash 为窗口内基线；Review 以 Codex 另行固定的 pins 为准」，并列明 capture→review 期间治理文档变化的原因（R0 Task/STATUS/Plan/Index/checkpoint 追加）。

### P3-5（P3）`OS preflight=NOT_RUN` 与 R0 已执行的只读 OS 查询并存且无范围说明

- **位置/短引用**：`doc/STATUS.md:29`「profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`……」；`doc/tasks/P02.md:61` 同句；同一文件 `STATUS.md:15` 已另记 `P02PRE-R0=ACTIVE / EVIDENCE_CAPTURED / REVIEW_PENDING`；evidence 未提及该治理字段。
- **影响**：`OS preflight=NOT_RUN` 应指**执行阶段** P02PRE 预检未运行，但与被保留的 R0 只读 OS 查询并列时容易被误读为「R0 未做任何 OS 查询」或反之。
- **最小修订**：在 evidence/checkpoint/adjudication 加一句「`OS preflight=NOT_RUN` 指执行阶段 P02PRE 预检；R0 的有限只读查询不改变该字段」，无需改动 gate 值。

### P3-6（P3）「manifest 在查询前冻结」缺乏独立 pin

- **位置/短引用**：manifest §94「本 manifest 在任何 R0 OS/path/ACL/WER 查询之前冻结……当前 `NOT_RUN`」、§96；manifest §69「当前 R0 manifest/evidence/review/adjudication 文件不纳入自身 hash 输入」；checkpoint L78「……并冻结 R0 manifest」（06:48 段，早于 capture 窗口）；R0 Task L27 勾选项。
- **影响**：冻结先于查询这一点由 Codex 自述文档 + 一个后来被追加过的 checkpoint 段佐证，但没有 capture 前对 R0 manifest 的独立 bytes/SHA 记录，无法从固定 pins 独立核验「冻结时内容 == 执行时依据」。
- **最小修订**：在 checkpoint 或派发记录中登记 R0 manifest 在 freeze 时刻的 bytes/SHA-256（cost 极低），或由 adjudication 明确该时间顺序为「自述+旁证」而非独立可验证事实。

## 5. 采纳范围（evidence adoption scope）与边界

**本 Review 采纳**：R0 evidence 作为**只读、窗口内**的宿主观察记录可用于以下有限范围——PID=12280 主 capture 内的身份/SID/无 thread impersonation；35 项 Process 环境变量原始值与词法归一化（含 `HOME` 及缓存变量 unset 的事实）；42 个精确对象的存在性/类型/属性/leaf reparse/ACL Owner+SDDL（17/25，0 查询错误）；两个 WER registry 候选键的只读存在性；三个 WER 目录的直接子项 name/type/length/last-write；13 项固定文档与 `.git/index` 的窗口内 pre/post 一致性。

**本 Review 不采纳 / 不构成**：

- 不构成对冻结进程单绑定性的完整认证（P2-1、P2-2、P3-1、P3-2）；
- 不构成对祖先/reparse/file-ID/hardlink/ADS、effective access、WER policy/view/destination/T0、future child env/cache/TEMP、完整 protected-invariants inventory/hash、私有 registry absence、未知子进程闭包的证明；
- 不构成 R0 的 WER 读取授权范围已自证的结论（P2-5，交 adjudicator）；
- 不构成「治理文档自 capture 以来未变」的证明（P3-4）。

**是否需要重采**：无 P0/P1，且所有偏差均已披露、均为只读、结论不依赖偏差批次，故 **不要求 `CHANGES_REQUESTED`**。若 Codex adjudication 需要「全部调用在单一冻结进程 + 仅冻结对象」的无条件认证，则应以上表 P2-1/P2-2 的限定方式采纳，或另行执行一次**有界重采/冻结范围修正**，而不是把现有文本读作已认证。

## 6. 结论

- 结论枚举：**`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`**（限定采纳范围见 §5）。
- Finding 计数：**P0=0；P1=0；P2=5；P3=6**。
- 本 Review 不构成技术 PASS，不改变任何 Gate，不代替 Codex adjudication，不解除 Build Barrier；Task 的 Review 勾选项可据此记录，但 P02PRE-R0 是否完成、Gate 是否重评，只能由 Codex 在另行固定 Review 对象 pin 后 adjudicate。
- 无技术 PASS 结论可从本文字审查推导。
