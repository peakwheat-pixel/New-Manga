# P02PRE-R1H round-four 独立静态 Review

日期：2026-10-12（Asia/Shanghai）；Reviewer=`/root/p02_r1h_remediation_review`，未参与实现；Owner=`/root/p02_r1h_codex_owner`；Integrator/Adjudicator=`/root`。

VERDICT=`APPROVED_STATIC_CONTENT`；P0/P1/P2/P3=`0/0/0/0`。在本次冻结范围内未发现新的实质问题。批准仅针对源码静态内容，不表示 parser、自检、fixtures、集成、P02PRE、Gate、Build 或 AC 通过。

冻结 base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`；parent=`0ecada4182d624d4f352a253e09db3bdecbee5d1`；reviewed HEAD=`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`；tree=`c9afca4e9bfd8d1b6a6c3ad5a8a33e0e12c3d87b`；branch=`agent/codex/P02PRE-R1H`；worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`。

Frozen prompt=`verification/P02/codex-p02pre-r1h-remediation4-review-dispatch-20261012.prompt.md`，实测与输入pin的3866 bytes / `2AB18C7E4A30A0AA1C84636E67AF702AACC45A32F61B21FED4A5E7493A51C392`一致。输入pins=`verification/P02/codex-p02pre-r1h-remediation4-review-input-pins-20261012.json`。实质Review前、后逐项bytes/SHA-256均 **source=8/8 MATCH，candidate=3/3 MATCH，pre/post=11/11 MATCH**。当前Task=22941 / `45671AD744C2CD51D831F3513F16CE573D24E7A0CF679DC087E98A29B27A4486`，不沿用其它Task快照。

完整frozen base→HEAD仅三份授权candidate新增（capture/selfcheck/Handoff=1287/722/90行，共2099行）；parent→HEAD代码只修正dictionary访问，Handoff同步交付和未运行说明。审查包含完整candidate的停止/分类/stage/AST/fixtures/输出失败路径，未改capture与此前逐段读取字节的SHA相同，并重新核对相关当前内容；没有只凭单行diff或旧批准作结论。

## R1H-007 的静态处置

`verification/P02/p02pre-r1h-selfcheck.ps1:223` 现为 `$prefix[[int]$index].Extent.Text.Trim() -cne $expectedDirectTexts[[object]$index]`。左侧明确选择prefix数组的位置；右侧将整数键显式转换为object，选择OrderedDictionary的`Item(System.Object key)`，不再调用`Item(int index)`。语义依据为此前已查阅的 [Microsoft Learn about_Hash_Tables（PowerShell 7.6），Accessing values](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_hash_tables?view=powershell-7.6#accessing-values)。没有运行示例或候选。

211–220的全部稀疏整数键与capture的13项prefix对应如下；其余四位置由225–228的专门guard/staging检查约束。

| prefix位置/整数键 | expected text对应目的 | capture行 |
|---:|---|---:|
| 0 | currentRelativePath初始化 | 492 |
| 1 | Path normalization操作名 | 493 |
| 3 | normalizedRelative的Replace | 495 |
| 4 | full的GetFullPath/Join-Path | 496 |
| 6 | canonicalRelative的Substring/Replace | 498 |
| 9 | cursor初始化 | 506 |
| 10 | item=null | 507 |
| 11 | parts路径组件拆分 | 508 |
| 12 | linkSkipped=false | 509 |

键3、9–12不再误读位置或越过dictionary值列表。真实candidate正例647经431调用prefix contract时，原先确定的错位比较已消除；当前合法prefix的文本、guards和调用数量在静态结构上匹配。**这只证明没有发现该静态阻断，不保证实际parser/AST引擎运行已经成功**。R1H-007=`FIXED_STATIC`。

## R1H-005/006 与负例无回归核对

Helper contract117–145继续精确限制Static/receiver/method/arguments、命令数与调用数，允许既有IsNullOrEmpty/Math.Max且拒绝额外/动态/外部调用；610–644保留真实helper检查、合法helper正例和两种外部调用负例。

真实outer-loop prefix205–313仍绑定`foreach ($relative in $record.paths)`、13项direct statements，并约束三条throw guard、staging nested first-path/counter/continue、路径规范化、初始化、command/member/assignment/control-flow。316–435约束真实component loop、相邻两种skip分支、state/flag/break以及outer continue直接block与唯一后续hash；prefix→component和component→continue未增添空白授权区间。没有发现放宽额外目标读取/ACL/枚举的变更。

四个prefix source mutation fixtures676–679仍真实锚定candidate source中`$linkSkipped = $false`至component loop之前；655–659及683–686检查锚点和注入区间。ACL、ReadAllText、hash、枚举注入都会新增prefix direct statement并改变pathLoopIndex=13条件，且不在调用allowlist；原先skip内、break/continue/state变异也保留。source只经过字符串处理、ParseInput生成AST和contract检查；没有执行注入source的路径。**所有fixtures仍NOT_RUN**，没有静态散文冒充已运行的判别力证据。

Capture保持精确nil冻结status/index安全停止、stage/type限制、身份错误停止、CreateNew写证据与写失败不重试/保留部分字节；Handoff如实列出本轮base、单行修复、only diff-check、未知执行器配置以及全部未运行项，没有Gate/AC PASS声明。

## Findings 与 AC dispositions

| 项目 | 本轮静态处置 | 运行/完成边界 |
|---|---|---|
| R1H-001 | `FIXED_BY_FAIL_STOP_STATIC`，capture178–181、401–407和795–823停止传播保留。 | status/index完整冻结等值仍`UNPROVABLE`，不可仅填值放行。 |
| R1H-002 | `FIXED_STATIC`，capture249–270保留stage并拒绝nonzero/repeated/conflicting/unknown mode及既有格式异常；inventory stage0再查保留。 | `NOT_RUN` |
| R1H-003 | `FIXED_STATIC`，capture161–167、517–525精确FileInfo/属性和未知对象停止保留。 | `NOT_RUN` |
| R1H-004 | `FIXED_STATIC_CONTENT`，真实AST/control-flow约束与source mutation覆盖已修复。 | parser/selfcheck/fixture判别力仍`NOT_RUN`。 |
| R1H-005 | `FIXED_STATIC`，纯内存helper形状与正负例保留。 | `NOT_RUN` |
| R1H-006 | `FIXED_STATIC_COVERAGE`，完整prefix、nested staging与间隙约束保留。 | `NOT_RUN` |
| R1H-007 | `FIXED_STATIC`，223明确object-key读取。 | `NOT_RUN` |
| AC1 | 窄分类和安全停止符合静态要求；完整frozen equality仍未证明。 | `NOT_VERIFIED / UNPROVABLE` |
| AC2 | 源码静态意见批准；实际parser/selfcheck必须另留证。 | `NOT_RUN` |
| AC3 | 本次非作者Review无P0/P1/P2，精确输入前后匹配。 | 等待root复核/adjudication，不能由Reviewer标Task完成。 |
| AC4 | 未集成、未运行引擎预检。 | `NOT_RUN` |
| AC5 | 未做final pre-run；缺失冻结基线仍需治理。 | `NOT_RUN` |
| AC6 | 未执行capture/post-run Review，one-shot未消耗。 | `NOT_RUN` |
| AC7 | Gate保持要求无回归；未释放后继。 | `NOT_VERIFIED` |

Architecture：未扩大产品架构、executable/API/path/output或registry/ACL写权限。Verification：本静态Review不替代真实检查；Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`，Build/Cargo=`NOT_RUN`，P02 AC1–AC7=`BLOCKED / NOT_RUN`；Owner waiver仍是风险接受，不是技术PASS。

## 实际读取/命令与限制

- `Get-Content`：frozen prompt/pins、Task当前AC/禁止项、manifest、round3 adjudication、round4 Owner prompt、root delivery verification、完整当前Handoff、当前selfcheck prefix/helper/loops/guards/fixtures/summary段、capture stage/type/baseline/inventory与上层停止及CreateNew失败路径。相同未改部分结合本Reviewer此前完整逐段阅读和本轮SHA一致性核对；读取显示截断的关键223已另行定向补读。
- `Get-Item`、`Get-FileHash -Algorithm SHA256`：只核对pin中已枚举11项source/candidate及相应pin文件；pre/post均11/11，exit=0。
- `git -C <owner-worktree> rev-parse HEAD HEAD^{tree}`：exit=0，符合冻结HEAD/tree；`git diff --stat <base>..<head>`、`diff --name-status <base>..<head>`与`diff <parent>..<head> -- selfcheck-path`：exit=0，完整路径仅三项，单行修复如上。
- 本轮未运行git status、未访问`.tmp.driveupload`。未运行parser、selfcheck或fixtures、preflight、capture、getter/API、tests、Build/Cargo、AC、OS动态或Windows Sandbox。唯一写入本Review报告；candidate/pins/Task/governance均未改。

## 下一接收者

Root Codex复核本报告和同一11项pins并adjudicate。可直接转发指令：在`G:/CODEX/New Manga`核对reviewed HEAD `7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`的三candidate精确字节与root治理状态；按Task AC3完成裁决，再按已获授权的Task边界安排精确集成和PS7 parser/isolated selfcheck。禁止因本Review直接运行capture/Build或解除Gate；冻结双仓status/index缺失仍需明确的后继范围与证据。本Reviewer交付后停止，不做集成/adjudication/successor释放。

未运行parser、自检、fixtures或任何动态验证；冻结Git基线仍UNPROVABLE，静态批准不解除Build Barrier。
