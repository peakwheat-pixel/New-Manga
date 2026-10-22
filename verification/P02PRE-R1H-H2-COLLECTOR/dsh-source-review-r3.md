# P02PRE-R1H-H2-COLLECTOR — R3 exact-head 非作者静态 Review

**Verdict：`APPROVED_STATIC_CONTENT`**（R2-01 / R2-02 / R2-03 / R2-04 / P4 均在 f8ea commit 的代码中真实、完整闭合；无回归；仅 4 项非阻塞 P3 精度/加固项）

> 本 Review 只读、未写任何仓库文件、未运行任何脚本/collector/getter/子进程/Build/AC/Sandbox。全部结论来自静态源码阅读与 git 自有文本记录。

---

## 一、固定目标与身份验证

| 项 | 值 | 我的验证 |
|---|---|---|
| reviewed code commit | `f8ea2edc7c2097f6f87676cafe7a3e2377a3f050` | ✅ 来源：worktree reflog 文本（git 自己写入） |
| 后续文档提交 | `8bba48bd9c0f08ffe6e81a5fd2277514595d0d27` | ✅ 是 f8ea2ed 的子提交，消息为 `commit: docs(P02): record R3 repair delivery and handoff for H2 collector` |
| base | `4a90d820a5d58a54cbc190665fbd87d563bc19af` | ✅ f8ea2ed 的父提交 |

依据 `G:/CODEX/New Manga/.git/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3/logs/HEAD`（4 行，git 自身写入）：

```
4a90d820… → 4a90d820…  reset: moving to HEAD
4a90d820… → f8ea2ed…   commit: fix(P02): close R2 findings for H2 collector R3 per source-review-r2-adjudication
f8ea2ed…  → 8bba48b…   commit: docs(P02): record R3 repair delivery and handoff for H2 collector
```

**已读的实际代码文件（worktree HEAD = 8bba48b）**：
- `tools/p02/h1-raw-pre-run.ps1`（全文 1735 行，分 3 段读完）
- `tools/p02/h1-raw-pre-run-selftest.ps1`（全文 658 行）

### blob 验证状态（重要，必须如实声明）

- ✅ **我完成**：提交存在性、父/子关系、doc commit 在 code commit 之后（reflog 文本）。
- ⚠️ **我未能完成**：对这两个文件**独立复算 git blob SHA-1 / SHA-256**。本会话 `pwsh` 在启动阶段即被沙箱拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`），连 `git rev-parse` 都无法执行；显式提权重试被拒（no approval channel）；派生的只读子代理得到同一确定性错误（9/9 命令零执行）。**我未做任何绕过或替代执行。**
- **替代交叉印证（非我复算）**：manifest 固定 `gitBlob b3fb4b62…(collector)` / `ae89e89b…(selftest)`；两次**相互独立**的执行（Owner R3 日志 `SUMMARY-JSON` 与 Codex 独立复跑 `codex-r3-9fb4e2897b874003a9a988aaf7665f96-run-record.json` 的 `sourceBefore/sourceAfter`）都把该 worktree 路径下的文件哈希为 `AB8A92ED…` / `0744549D…`，与 manifest 的 `sha256` 及 Task Canonical Evidence 表一致。结合「HEAD 仅由一条 docs commit 从 f8ea2ed 前进」，可支持“代码文件与 f8ea commit 相同”，但**这是间接推断，不是我复算的 blob 相等性**。

---

## 二、逐项 closure 判定（从代码实现独立判定）

### R2-01 — 输出 absent/链/卷/排除证据时序 —— ✅ CLOSED

| 判别点 | 代码证据（`h1-raw-pre-run.ps1`） | 判定 |
|---|---|---|
| 证据在 CreateNew **前**真实采集 | `New-OutputPreflightCapture` 定义 L584-611；主序列调用 **L1085**，`Open-ExclusiveCreateNew` 在 **L1093** | ✅ 顺序真实（非伪造） |
| 纯字符串排除先于任何 FS API | L589-590 先做 `Test-PathUnderExclusion`，之后才 L594-597 访问 | ✅ |
| absent 判定真实 | L597 `targetAbsent = ($outputFileChain.leafAbsent -and -not (Test-Path -LiteralPath $OutputFile))`；`leafAbsent` 来自 L511-547 的 lstat 分类 | ✅ 我复算：文件存在/悬挂链接都不会得出 `targetAbsent=$true` |
| CreateNew 后如实记录 | L1093 建流 → **L1095** `New-OutputPostCreateFacts`（L613-630）记 `targetExists`/`exclusiveStreamOpen`（`CanWrite`，建流用 `FileShare.None` L741） | ✅ 未把 post-create 冒充 preflight |
| check 的 JSON Pointer 与记录相符 | check L1199-1204，`ObservedPointer = "$($outputSafety.pointer)/output/value"`（L1201）；observation L1180-1189 的 `value = @{preCreate=…;postCreate=…}` 同体序列化 | ✅ `Add-Check` 的 L772-774 运行期 `Resolve-JsonPointer` 会实际解析该 pointer |
| `outputSafetyOk` 可达真值 | L1190-1198 由 preCreate(4 项) + postCreate(3 项) 组成，全部只在成功建流后为真 | ✅ R2 的“必 exit 4”根因消失 |
| CreateNew 冲突仍 fail-closed | 预存则 L1091 `Require targetAbsent` → `OUTPUT_PRECHECK_FAILED` → exit 2；竞态窗口则由 L741 `FileMode.CreateNew` 抛 → L1713 catch → exit 5 | ✅ 两条路径都非零退出、不覆盖 |

### R2-02 — leaf lstat 分类 / 真缺失 vs 查询错误 / 祖先与 target fail-closed —— ✅ CLOSED（列出被枚举路径）

- leaf 自身用**不解引用**方式分类：L515 `[IO.File]::GetAttributes($Path)`（GetFileAttributes 语义，末段 reparse 不解引用），L523-525 取 `ReparsePoint`/`Directory`；仅当 `leafReparsePoint` 时才在 L526-533 取 `LinkTarget`（且 try/catch 包裹）。**未**使用会解引用的 `Test-Path`/`File.Exists` 做 leaf 分类（L597 的 `Test-Path` 与 `leafAbsent` 是 `-and`，只会更保守）。
- 真缺失 vs 属性查询错误**在链分类里正确区分**：L535 解构 `InnerException`；L536-541 仅 `FileNotFoundException`/`DirectoryNotFoundException` → `leafAbsent=$true`；**其它异常** → L542-546 `leafExists=$false, leafAbsent=$false, leafAttributeError=…`，并被 L580 `allOrdinary` 条件与各 `Require`/checks 变成 FAIL。
- 祖先 reparse：L559-564 `DirectoryInfo.Attributes & ReparsePoint` → `reparseComponents` → L576-580 `allOrdinary=false`。
- 文件挡住目录链：L565-566 → `nonDirectoryComponents` → 同样 fail-closed。
- 消费方约束：
  - 输出目录 leaf（L1090 `leafExists -and -not leafReparsePoint`）；
  - 固定路径批量（L1212-1249：`allOrdinary` + `noLeafReparse`，覆盖三 repo / protected / Packages / root index / 9 pins / 7 targets）；
  - protected 前后（L1265、L1675-1677 均要求 `-not reparsePoint`）；
  - 7 targets（L1589-1595：`-not exists` **且** `leafAbsent` **且** `-not leafReparsePoint`；父目录 `isDirectory -and -not reparsePoint -and targetChain.allOrdinary`）。
- dangling junction 不会被当成 absent：悬挂链接/连接点在 `GetAttributes` 下 `exists=$true + ReparsePoint` → L1590 `$absentOk` 为假 → FAIL。该行为有两次独立执行事实（Owner L177-L190 与 Codex 独立复跑 L163-L173 全 PASS，含 `r202-dangling-junction-fails-target-absence-check`）。

### R2-03 — 全入口排除守卫 / 动态清单 / 排除子树不被探测 —— ✅ CLOSED

我把 collector 中**所有**实际 FS/子进程访问点逐一与守卫对照（47 处 API 匹配全查）：

| 访问点 | 本地守卫（先于访问） |
|---|---|
| L597 / L627 `Test-Path` | L589-590（同函数内先查） |
| L721 `DriveInfo` | L721 自身首句 |
| L741 `FileStream CreateNew` | L738 |
| L878-879 `File/Directory.Exists`（helper 启动） | **L865**（executable/cwd/argv 在 `[IO.File]::Exists` 之前） |
| L960 读 pin / L986 `GetAttributes` / L1009,L1014 Info / L1035,L1038,L1042 protected | L952 / L972+L980+L834 / L1025+L834 |
| L1086 `Directory.Exists(outputDir)` | L1081-1082 + L1085 内 L589 |
| L1279 / L1693 读 root index | 经 `-GetterInput @{path=…}` → L834 |
| L1609/L1612 读 frozen executor | L834（input 为该 pin 路径） |

- **规范化/大小写/分隔符**：L443-448 —— `/`→`\`、`TrimEnd('\')`、按 `\` 切段、`-eq` 精确段比较（PowerShell 字符串 `-eq` 大小写不敏感，满足 Windows 需求）。无假阳性：status argv 中的 `:(exclude).tmp.driveupload` 作为**整段**不等于 `.tmp.driveupload`（L446），不会误伤 L1541/L1551/L1563 的 helper 守卫。
- **guard 顺序**：getter 在 `& $Body` 之前（L833-835）；helper 在 `Process.Start` 之前（L864-865）；均在 observation 建立前抛出。
- **动态 TEMP/TMP 派生路径**：先 `temp-tmp-env`（L1412-1420，无 FS）→ 构建 lab的位置 plan → `path-probe-plan` getter（L1435-1441，其 `GetterInput` 含 TEMP/TMP/scratch，触发 L834 守卫，**排除子树在此 fail-closed 之前不会被探测**）→ **L1462-1476** `exclusion-scope-dynamic-paths` 产出完整 `{path, underExclusion}` 清单并保存为 raw observation → 才在 L1484-1492 逐项 probe。清单确实放在 `-GetterInput`（L1464）与 observation output（L1471-1475），pointer L1479 指向该 value。
- **固定路径清单**：L1147-1154 含 `RootIndexPath`、H1 Task snapshot 绝对路径、`ScratchCacheProbePaths`、target 与其**派生父目录**；L1157 起把它作为 `GetterInput`（不再靠闭包读外层变量），L1161-1169 逐项落 `{path, underExclusion}`，L1171 `Require` fail-closed。
- 两处 `exclusion-scope-*` getter 是纯内存判定、无 FS 访问，跳过入口守卫是刻意设计；全文件仅这两个 id 使用该前缀（已 grep 确认）。

### R2-04 — `root-index-hash-after` 时序 —— ✅ CLOSED

- 最后一个子进程：`target-7-check-ignore`（循环 L1579-1604 内的 L1585）。
- 之后仍有文件读取：frozen executor `ReadAllText`（L1612）、source pins after（L1660-1669）、protected after（L1672，含 `ReadAllBytes`/`Get-Acl`/`Get-Item -Stream`）。
- `root-index-hash-after` 采样：**L1688-1695**，随后 L1696-1703 与 before 真比较（不一致即 FAIL）。
- closed 行：L1706-1712。→ after 采样确为 close 前最后一个 observation，与 L1699 `Expected` 文本一致。

### P4 — 精度项 —— ✅ CLOSED

- `path-probe-plan-unique-ids` 的 `observedPointer` 现为 `$probePlanObs.pointer/output/value`（L1450），该 observation 的 body（L1438-1441）返回 `New-PathProbePlan` 的 `{plan, foldedDuplicates}`，**完整 plan 可解析可达**（plan 位于 `…/output/value/plan`）。
- `nonDirectoryComponents` 真实分类（L565-566），并被 `allOrdinary`（L577）实际消费：输出 preflight `Require`（L1087）与 `path-chain-fixed-paths`（L1238-1243）均以它决定 FAIL。

---

## 三、绕过 / 新回归专项检查

| 检查 | 结果 |
|---|---|
| 唯一写通道 | ✅ 仅 L741 `CreateNew + FileShare.None`；全文件无 `Set-Content`/`Out-File`/`WriteAll*`/`Remove-Item`/`Move/Copy`（grep 确认） |
| status argv 15 项、排除 pathspec 独立最后 | ✅ L637-642，与冻结字面一致（未回归） |
| Gate 原值块 / `NEW_TIME_EVIDENCE` / `CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE` / `historyNote` / `notRun` | ✅ L188-199、L201-202、L802、L804-812（字面未变） |
| NUL 保真 / 空字节非缺失 / base64 无省略 | ✅ L240-314（无 limit/omit 分支） |
| 禁止面（Add-Type / P-Invoke / Start-Process / Invoke-Expression / AppContainer / Toolhelp / ACL 写） | ✅ 全文件 0 命中；注册表仅 `OpenSubKey(name,$false)`（L1378） |
| dangling pointer fail-closed（H2-04） | ✅ L770-774 仍运行期解析；我逐处核对全部 27 个 `Add-Check` 的 pointer 均指向先前 `Save-Observation` 的节点与其子键（`/output/value` 或 `/output/stdout`） |
| 不读取 `.tmp.driveupload` | ✅ 唯一出现位置是 status 的最后 pathspec（L641）与纯字符串判定函数 |
| 输出路径不在 root repo 内（不扰动 frozen index/status） | ✅ `…/New Manga.workspace/agent-output/…` 与 root `G:/CODEX/New Manga` 为兄弟目录 |

---

## 四、Findings（全部 P3，非阻塞）

### P3-1 `Get-PathProbeObservation` 把**所有** `GetAttributes` 失败塌缩为“合法缺失”

- 位置：`tools/p02/h1-raw-pre-run.ps1` **L983-993**（`$attrEx = $_`（L988）赋值后**从未被读取**；`$null -eq $attr` → 直接 `return New-PathProbeAbsentValue`）；对照链分类的正确判别在 **L534-546**。
- 触发条件：被探测路径的 `[IO.File]::GetAttributes` 因**非缺失**原因抛错（`UnauthorizedAccessException`、`ArgumentException`、`PathTooLongException` 等）。
- 后果：raw observation 会写下 `exists=false, reparsePoint=$null`（无任何 error 字段），而 `profile-moniker-packages-probe`（L1403-1409，`-Result 'PASS'` 无条件）与 TEMP/TMP/scratch 逐项 probe（L1486-1491，同样无条件 PASS）会据此给出“不存在”的证据。**不构成 fail-open**：真正门控运行的 7 target 判定 L1589-1595 都同时 `-and $targetChain.leafAbsent/-not leafReparsePoint`，查询错误在那里必然变成 FAIL/exit 4；因此仅影响“证据忠实度”，与本 Task 的核心交付目的直接相关但无越权授予。
- 最小修复：在 probe body 中按 L535 的方式解构 `InnerException`；非 `FileNotFound/`DirectoryNotFound` 时返回显式 `attributeError` 字段（并令上述两个 PASS check 改判 `NOT_VERIFIED` 或 fail-closed），不再复用 CX-01 的“合法缺失”shape。

### P3-2 probe 对非目录 leaf 会解引用链接目标，且悬挂文件链接会丢证据

- 位置：**L1012-1018** —— `$fi = [IO.FileInfo]::new($src.path)`，**L1015 `$value.length = $fi.Length`** 在 L1016 的 `if ($isReparse) { linkTarget = … }` **之前**执行。
- 触发条件：某个固定探测路径本身是**文件符号链接**（live 或 dangling）。
- 后果：(a) `FileInfo.Length` 会解析末段链接，与该 getter 自述的 `-Method`（L976 “lstat existence probe; never follows link target”）不一致——这是纯字符串守卫无法识别的间接路径，理论上可造成对排除子树内目标的 metadata 读取（**契约已明确接受纯字符串模型**，且链分类对门控路径 fail-closed，故不升级）；(b) dangling 文件链接时 L1015 抛错被 L1017 吞掉，L1016 永不执行 → `linkTarget` 证据丢失。
- 最小修复：先判 `$isReparse`，reparse 时只取 `LinkTarget`、跳过 `Length`；或仅在 `-not $isReparse` 时读 `Length`。

### P3-3 `tools-pwsh` 探测的是**运行时 `$PSHOME`**，不在排除守卫/清单覆盖内

- 位置：**L1305-1318**（`-GetterInput` 只含冻结字面 `expectedPsHome`，L1307；body 用实时 `$PSHOME` 做 `Join-Path` 与 `[IO.File]::Exists`，L1314-1316）；固定路径清单 L1147-1154 **不含** `$PSHOME`。
- 后果：该 `File.Exists` 的实参既不是被守卫检查的输入串，也不在 manifest 中，是全文件**唯一**不受纯字符串排除守卫直接覆盖的 FS 访问入口。实际不可达：冻结环境下 `$PSHOME='C:\Program Files\PowerShell\7'`（其 `pwsh.exe` 已作为 `$script:PwshExe` 在清单内 L1148），若 `$PSHOME` 漂移则 L1320-1321 判定 FAIL → exit 4，仍 fail-closed。
- 最小修复：把 `$PSHOME` 纳入 `Assert-InputsNotUnderExclusion` 的检查值（或在 L1314 之前先 `Require ($PSHOME -ceq $script:ExpectedPsHome)`）。

### P3-4 leaf-reparse 断言集合漏掉启动器二进制与 H1 Task snapshot

- 位置：`$chainPaths` **L1207-1211**（RootRepo/CandidateRepo/A6/protected/Packages/RootIndexPath + 9 pins + 7 targets）对比排除清单 **L1147-1154**（后者含 `WhoamiExe`、`PwshExe`、`GitExe`、H1 Task 绝对路径）。
- 后果：被**执行**的 `$script:GitExe`（L947/L1329/L1541/L1551/L1563/L1585）与 `$script:WhoamiExe`（L1363），以及被读取的 H1 Task snapshot（L1252），都没有 `leafReparsePoint -eq $false` 断言；若这些固定二进制路径上是 reparse point，collector 会照常启动而不是 fail-closed。需要在 `C:\Program Files\Git\cmd`、`C:\Windows\System32`、PowerShell 安装目录具备写权限才可利用，属加固项而非现实越权路径；R2-02 的裁决清单亦未点名这些路径。
- 最小修复：把 `$script:GitExe`、`$script:WhoamiExe`、`$script:PwshExe` 与 H1 snapshot 路径加入 `$chainPaths`（它们不适用 target 的 `absent` 语义，只需 `allOrdinary`/`noLeafReparse`）。

### 备注（非 finding，文档精度）

Task/Handoff 把 P4 的 pointer 写成 `/observations/8/output/plan`；代码实际为 `/observations/<seq>/output/value`（plan 位于其下 `…/output/value/plan`）。代码侧满足“指向含完整 plan 的 raw observation”，文档侧字面路径不精确，值得在下一轮文档追加时修正。

---

## 五、未执行范围与限制（明确）

- **未运行**：任何 shell/git/hash 命令、live collector、getter、executor、Build/Cargo、AC1–AC7、Sandbox、注册表/ACL/Profile 探测；**未修改/未写入任何文件**（含仓库与 workspace）。
- **未能执行**：独立的 git blob / sha256 复算（原因见 §一）。故本 Review 的“exact-head”绑定强度为：reflog 提交关系 + 两次独立执行日志的哈希交叉印证，而非我自己的字节复算。
- **未覆盖**：R2 版本源码文件、R1/R2 的历史日志原文、`source-review-r2-input-verification.json` 明细；Parser/selftest 日志仅作为**执行事实**采信（Owner `156 PASS/0 FAIL/6 SKIP`、Codex 独立复跑同样 `156/0/6`、两处 `collectorSha256=AB8A92ED…`），未代替代码审查。
- 本 Task 状态结论（Technical Gate `NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo 与 AC1–AC7 `NOT_RUN`、v2 P2-1 仍 OPEN、不作为 X6 S0）**不因本 Review 改变**；live-run 仍未释放。

---

## 六、结论与推荐下一步

**`APPROVED_STATIC_CONTENT`**：R2 adjudication 接受的 R2-01(P1)/R2-02(P2)/R2-03(P2)/R2-04(P3) 与 P4 精度项，在 `f8ea2edc7c2097f6f87676cafe7a3e2377a3f050` 的代码中均已真实闭合，未发现新的可利用绕过或回归；4 项 P3 只建议随下一轮硬化处理，不阻塞。

**推荐下一步（可直接转发）**：

> 对 code head `f8ea2edc7c2097f6f87676cafe7a3e2377a3f050`（worktree `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3`，branch `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3`）执行：
> (1) **Codex**：独立复算 collector/selftest 的 git blob SHA-1 与 SHA-256（manifest 记 `b3fb4b62…`/`ae89e89b…`，`ab8a92ed…`/`0744549d…`），确认 HEAD(8bba48b) 与 f8ea2ed 的两文件字节相同——本会话因 Windows 沙箱 `grantWrite` 失败（Win32 5）无法执行 git，未完成该复算；随后对本 Review 做 adjudication。
> (2) 若 Codex 采纳，冻结 run Task（RunId + exact targets）后才允许运行 live collector；R3 代码本身已是新的 delivery head，**不得**携带旧静态批准直接跑。
> (3) 可选：把 P3-1（probe 缺失/错误判别）、P3-2（`FileInfo.Length` 解引用）、P3-3（`$PSHOME` 守卫覆盖）、P3-4（启动器二进制 leaf-reparse 断言）登记为 R4 硬化项，并修正 Handoff 中 P4 pointer 的字面路径。
