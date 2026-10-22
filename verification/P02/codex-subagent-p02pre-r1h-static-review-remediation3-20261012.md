# P02PRE-R1H round-three 独立静态 Review

日期：2026-10-12（Asia/Shanghai）。Reviewer=`/root/p02_r1h_remediation_review`，未参与 Owner 实现；Owner=`/root/p02_r1h_codex_owner`；Integrator/Adjudicator=`/root`。Task 指定 Reviewer `gpt-6.1-sol/high`，模型声明不代替以下证据。

VERDICT=`CHANGES_REQUESTED`；P0/P1/P2/P3=`0/0/1/0`。R1H-006 的 prefix 覆盖缺口静态修复成立，但新增 **R1H-007 / P2** 导致合法候选也被 self-check 拒绝；此为静态结论，未执行测试。

冻结 base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；parent=`92c90a9ba20f7a1b4ab090837f99c191745524f6`；reviewed HEAD=`0ecada4182d624d4f352a253e09db3bdecbee5d1`；tree=`06986f47ac8363a32ecbf2d0e41ec1d680510940`；branch=`agent/codex/P02PRE-R1H`；worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`。

Frozen prompt=`verification/P02/codex-p02pre-r1h-remediation3-review-dispatch-20261012.prompt.md`；pins=`verification/P02/codex-p02pre-r1h-remediation3-review-input-pins-20261012.json`，实测 SHA-256=`502D164909D99C1BB6E9C4DB918D268181DE5C629F377764103DFBBDCD1CD655`。Review 前、实质审查后逐项 bytes/hash 均 **source=7/7 MATCH，candidate=3/3 MATCH，合计 pre/post=10/10 MATCH**。当前 Task=22941 bytes / `45671AD744C2CD51D831F3513F16CE573D24E7A0CF679DC087E98A29B27A4486`；没有使用历史 Task pin 代替。

完整 frozen base→HEAD 仅新增三份授权 candidate（capture/selfcheck/Handoff=1287/722/83 行，共2092行）。本轮 parent→HEAD 的 selfcheck 完整增量已读取；其未改部分结合此前本 Reviewer 完整静态阅读、本轮当前源和 capture 相同 SHA 复核，不沿用旧批准。

## R1H-007 — P2 / OPEN：稀疏整数键的 OrderedDictionary 被当成位置下标读取

位置：`verification/P02/p02pre-r1h-selfcheck.ps1:211`–`:223`，具体错误读取在 **223**；调用路径为647→431→205。

触发：`$expectedDirectTexts = [ordered]@{ ... }` 使用整数键 `0,1,3,4,6,9,10,11,12`。遍历 `.Keys` 后，223 将 `$prefix[[int]$index]` 与 `$expectedDirectTexts[$index]` 比较。对于 `[ordered]` 对象，整数下标使用 `Item(int index)`，代表值列表中的位置；整数键查询需显式选择 object-key overload。该行为由 [Microsoft Learn：about_Hash_Tables（PowerShell 7.6），Accessing values](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_hash_tables?view=powershell-7.6#accessing-values) 明确说明。

因此 `$index=3` 时，左侧是真实 prefix 第3项 `$normalizedRelative = ...`（capture495），右侧是 ordered dictionary 第4项，也就是键4的 `$full = ...` 文本。两者必不等，contract 返回 false；后续647抛出“真实控制流不满足契约”。更大的稀疏键还可能超出9项 dictionary的位置范围。即使 parser和此前断言全满足，当前合法candidate仍无法通过这个正例检查；四个新增变异负例亦位于647之后，无法在该合法检查拒绝后运行。本报告没有实际运行 parser/selfcheck，不将此描述成已执行失败。

最小修复：保留精确allowlist，仅将右侧访问改成按键读取，例如 `$expectedDirectTexts[[object]$index]`，或用普通 hashtable 替代这个不需要依赖遍历顺序的 `[ordered]`。不要改变 `$prefix` 的整数位置索引。保留合法真实candidate正例与四个负例，在通过独立Review后由Integrator运行既有selfcheck；Owner阶段仍只允许Task规定的`git diff --check`。

Disposition=`OPEN / ACTION_REQUIRED`。此项阻止AC2/AC4自检验收，与安全prefix覆盖的结构修复是不同问题。

## R1H-006 prefix 与四个 fixtures 的静态核对

selfcheck205–228固定真实 `foreach ($relative in $record.paths)`、pathLoopIndex=13，并逐条约束其13项direct statements；186–202精确限制三项throw guards、staging branch内部counter、first-path guard及continue。232–313在这一完整prefix区间内核对commands、成员调用、非调用成员、assignments及控制流。431将该prefix contract接入真实component loop与outer continue邻接检查，旧的loop→continue缺口约束保留。

允许的原始13项与capture492–509一致：current-path/current-operation；安全相对路径guard；normalized-relative；full-path；越界guard；canonical-relative；规范化一致guard；staging exclude；cursor/item/parts/linkSkipped初始化。除R1H-007的键访问错误外，未发现新的目标访问放宽。

新增fixtures位于676–679，使用真实repository function source的 `$linkSkipped = $false` 锚点，分别插入ACL、ReadAllText、hash、directory enumeration。655–659检查锚点与component loop顺序；683–686检查注入片段确实位于prefix和component loop之间。各fixture新增一条direct statement，会使pathLoopIndex从13变14而被206拒绝；同时新增调用不在命令/成员allowlist内。688只把source送入ParseInput取得AST，690检查contract拒绝，没有Invoke-Expression、ScriptBlock执行或调用变异source。它们在源码中确有判别结构，但**尚未执行**，不能计为已通过负例。

R1H-006=`FIXED_STATIC_COVERAGE`，原prefix遗漏得到修补；安全selfcheck整体仍由R1H-007阻塞。

## R1H-001..006 与 AC1–AC7 disposition

| 项目 | 静态处置 / 证据位置 | 运行状态 |
|---|---|---|
| R1H-001 | `FIXED_BY_FAIL_STOP_STATIC`：capture178–181仍固定null baselines；401–407在仓库query/inventory前UNPROVABLE停止，上层停止传播保持。完整双仓冻结等值未证明。 | `NOT_RUN / UNPROVABLE` |
| R1H-002 | `FIXED_STATIC`：capture249–270保存stage并拒绝nonzero、重复/冲突、未知mode及既有格式异常；inventory再要求stage0。 | `NOT_RUN` |
| R1H-003 | `FIXED_STATIC`：capture161–167、517–525的精确FileInfo/属性和未知类型停止保持。 | `NOT_RUN` |
| R1H-004 | 真实skip state/flag/break/continue与调用顺序AST绑定已补齐；整体自检验收仍受R1H-007阻塞。 | `NOT_RUN` |
| R1H-005 | `FIXED_STATIC`：selfcheck117–145精确pure-memory helper receiver/Static/method/arguments；610–644保留真实helper检查、合法正例、外部file-read/Get-Item负例。 | `NOT_RUN` |
| R1H-006 | `FIXED_STATIC_COVERAGE`：13项prefix、nested staging、loop/continue间隙和新增四负例结构如上。 | `NOT_RUN` |
| AC1 | 窄分类与缺失基线安全停止保留；完整frozen equality仍UNPROVABLE，不记AC PASS。 | `NOT_VERIFIED` |
| AC2 | 新P2阻塞合法selfcheck正例；fixtures仅源码存在。 | parser/selfcheck `NOT_RUN` |
| AC3 | 独立静态Review已交付，有P2未解决，批准条件不满足。 | pins `10/10 MATCH`，不代替运行 |
| AC4 | 尚未集成、parser/selfcheck/preflight。 | `NOT_RUN` |
| AC5 | final pre-run未执行。 | `NOT_RUN` |
| AC6 | capture与post-run Review未执行；本Review不消耗one-shot。 | `NOT_RUN` |
| AC7 | Gate不自动放行的约束保持；后继未释放。 | `NOT_VERIFIED` |

Architecture/失败路径：没有修改capture或扩大API、executable、registry/ACL写入、path或output。CreateNew与异常保留部分证据的capture1271–1286保持；Handoff如实描述未执行parser/selfcheck/fixtures。其它未改代码仍是之前已审过且hash一致的字节；本轮没有以历史Review证明runtime或宿主安全。当前nil基线使inventory不可达，不可把该不可达性当成补全基线后skip安全的运行凭证。

## 实际读取、命令与限制

- `Get-Content`：frozen prompt/pins、Task当前AC/限制与末尾派发证据、manifest、Owner round3 prompt、round2 adjudication、完整Handoff；selfcheck新完整diff及相关当前行；capture分类/stage/baseline/inventory/CreateNew失败路径。其余相同source与前轮完整阅读内容由本轮pin确认未变。
- `Get-Item`/`Get-FileHash`：仅10个pins枚举输入及pinsJSON字节/hash核对，pre/post均10/10，命令exit=0。
- `git -C <worktree> rev-parse HEAD HEAD^{tree}`：exit=0，HEAD/tree如冻结值。
- `git diff <parent>..<head> -- verification/P02/p02pre-r1h-selfcheck.ps1`、`git diff --stat <frozen-base>..<head>`、`git diff --name-status <frozen-base>..<head>`：exit=0，候选仅三授权路径；完整candidate审查包括未改capture/hash相同部分，并非只看Owner摘要。
- `web.search/open`：仅查阅上方Microsoft官方PowerShell7.6文档，核实整数OrderedDictionary下标语义；没有向宿主调用任何候选parser/API或运行示例代码。
- 没有git status，没有访问`.tmp.driveupload`。未运行PowerShell parser、自检、preflight、capture、getter/API、tests、Build/Cargo、AC1–AC7、OS动态或Windows Sandbox。唯一写入本报告，候选和治理文件未改。

## 下一步

由`/root`复核pins并adjudicate。可转发原Owner：在`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex` / `agent/codex/P02PRE-R1H`，从`0ecada4182d624d4f352a253e09db3bdecbee5d1`仅修复R1H-007的dictionary按键读取，保持13项prefix和所有正/负例allowlist，必要时同步既有Handoff；只可写三条既有candidate路径，只可运行`git diff --check`。提交新HEAD与pins后交非作者Review；不改Task/manifest/Gates，不运行任何动态或脚本检查。Integrator负责后续集成和真实验证，本Reviewer不adjudicate或释放successor。

未运行parser、自检或任何动态验证；新P2仍开放，Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE不能据本Review解除。
