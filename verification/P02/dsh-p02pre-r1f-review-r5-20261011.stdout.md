# P02PRE-R1F Round 5 独立只读 Review

## Decision

`CHANGES_REQUESTED`

## counts

`P0/P1/P2/P3 = 0/1/2/5`

核心结论：`.tmp.driveupload` 的排除时机与 detached-ref 的精确匹配，在这两份代码路径上写法是正确且保守的；但 `Get-InventoryAction` 的容器分支与逐组件遍历相冲突，使脚本对任何深度 ≥ 2 的 inventory 路径必然 fail-stop，capture 无法达到 `CAPTURED`，因此当前冻结候选不具备可执行性，必须重新冻结后再审。

---

## Findings

### F1 — P1 — `verification/P02/p02pre-r1f-capture.ps1` L117 + L385–L402（自检缺口 L123–L128）

**可复现原因（静态确定）**：`Get-InventoryAction` 第 4 参数 `$IsContainer` 在 L117 参与无条件 STOP：

```powershell
if ($IsReparsePoint -or $GitMode -eq '120000' -or $IsContainer) { return 'STOP' }
```

而 L385–L404 对 candidate 的**每一个**路径组件都调用该函数（L393），并对中间组件传入 `[bool]$item.PSIsContainer`。于是对 `verification/P02/p02pre-r1f-capture.ps1` 这类路径，`partIndex=0` 的 `verification` 组件满足 `IsLeaf=$false`、`IsReparsePoint=$false`、`GitMode='100644'`、`IsContainer=$true` → 返回 `'STOP'` → L402 `throw "Unsupported reparse or non-regular object in protected inventory: ..."` → L413 `Set-RepositoryStop 'PROTECTED_HASH_FAILED'` / `errorOperation='Get-Item path component'` → repo `state ≠ 'CAPTURED'` → L591 `stopReason='MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED'`。

由于 `git ls-files --cached --others --exclude-standard -z` 的候选**必然**包含 `doc/...`、`verification/P02/...`、`apps/...` 等深层路径，capture 在任何一次真实运行中都无法完成受保护库存采集，Task AC（完整宿主只读取证、L49–L51 的五态证据）不可达成。同时 L403 的"非目录 parent"兜底实际上永远不会按作者预期执行，因为普通目录父组件已被 L117 提前判死。

**与 Task/manifest 不一致**：manifest L37 只要求"逐段检查祖先路径，任何 **parent** `ReparsePoint` 立即停止"；manifest L38 的 fail-stop 清单针对的是 reparse / 目录 leaf / 非 regular mode。普通 parent 目录不在其中，L402 的报错文本（"Unsupported reparse or non-regular object"）也证明作者意图是 reparse 或非普通对象，而非普通目录。

**自检为何没有发现**：L123–L128 的样本里，`$IsContainer=$true` 只在 `$IsReparsePoint=$true`（L123、L124）时出现，无法区分"leaf 是目录"与"parent 是目录"；`Get-InventoryAction '100644' $false $false $true` 这一关键形态从未被断言。因此 self-check 的 `PASS` 掩盖了本缺陷，属于"自检证据不能支撑其被引用范围"的情形。

**最小修复**：将容器判定限定到 leaf：

```powershell
if ($IsReparsePoint -or $GitMode -eq '120000' -or ($IsLeaf -and $IsContainer)) { return 'STOP' }
```

并在 `Assert-InventoryPolicySelfCheck` 中补三条断言：(a) `Get-InventoryAction '100644' $false $false $true` 必须**不是** `'STOP'`；(b) `Get-InventoryAction '100644' $false $true $true`（leaf 是目录）必须是 `'STOP'`；(c) 端到端形态断言：3 段路径的 mid 组件决策必须允许继续遍历到 leaf。

---

### F2 — P2 — `verification/P02/p02pre-r1f-capture.ps1` L118 + L392–L393（自检缺口 L125）

**可复现原因**：L392 对不在 index 中的 candidate（`--others` 的未跟踪文件）赋 `$gitMode = $null`，随后 L393 将其绑定到形参 `[string]$GitMode`。PowerShell 会把传入 `$null` 归一为 `[string]::Empty`，因此 L118 的 `$null -ne $GitMode` 是**永真死条件**，只由 `$GitMode -notin @('100644','100755')` 决定结果。后果二选一，其中必有一个为真：

- 若绑定归一为 `''`（当前 PS 5.1 行为的预期结果）：未跟踪的普通 regular file → `'STOP'` → L402 throw。Task L31 明确"当前工作树 dirty"，只要存在任何未被 `.gitignore` 忽略的未跟踪文件（本次 R5 self-check、manifest、capture 脚本等新产物若尚未提交即是此类），main/scratch 任一仓都会 fail-stop，capture 依旧不可完成。
- 若该环境保留 `$null`：未跟踪的普通 regular file → `'HASH_REGULAR_FILE'` → L407 对其执行 `Get-FileHash`。这与 manifest L38"仅允许 regular-file mode=`100644`/`100755`"的字面 fail-stop 规则冲突，也未被 Task AC L44/L48 声明为许可动作——即对未跟踪内容做内容读取和哈希，属于未声明行为。

**自检为何没有发现**：L125 的样本是 `Get-InventoryAction $null $true $true $false`，`$IsReparsePoint=$true` 使 L117 先行返回 `'STOP'`，根本走不到 L118。自检没有"无 index mode 的 regular file"这一形态，因此该分支在两种绑定语义下都未被固定。

**最小修复**：显式化该维度，例如 `Get-InventoryAction` 增加 `[bool]$HasIndexMode` 参数（由 `$indexModes.ContainsKey($relative)` 传入），在函数内用 `[string]::IsNullOrEmpty($GitMode)` 而不是 `$null -ne $GitMode` 判断，并在 Task/manifest 中明确"未跟踪 regular file 的动作是 fail-stop 还是 hash"；同时在 self-check 中为该形态加断言。若作者意图是"未跟踪即 fail-stop"，必须在 Task/manifest 写明其后果（dirty 树上的 fail-stop 是预期行为），否则 AC L49–L51 的完整证据无法产生。

---

### F3 — P2 — `verification/P02/p02pre-r1f-capture.ps1` L107–L109 + L373–L379

**可复现原因**：Task L25 与 manifest L36 要求"对该路径字符串执行**规范化**后，再按 root-relative `.tmp.driveupload` 根/后代排除"。实现只把 `GetFullPath(Join-Path $Root $relative)` 用于 repo 边界检查（L373–L374），**排除判定使用的是未经规范化的 Git 原始 relative 字符串**（L375 → L108 的三个前缀比较）。由此存在未覆盖的路径形式：

- 尾随点/空格段：`.tmp.driveupload./x`、`.tmp.driveupload /x`。字符串前缀不匹配 → 不排除；而 Win32 文件系统语义会把尾随点/空格剥离，`Get-Item`/`Get-FileHash`（L389/L407）实际命中的是 `.tmp.driveupload\x`，即用户上传暂存数据被读取并哈希。
- `./` 前缀形式：`./.tmp.driveupload/x` 同样不匹配前缀，但 L373–L374 的 `GetFullPath` 仍落在仓库根内，边界检查通过。
- 备用数据流形式（`:stream`）在原理上属同类问题。

需要索引中存在此类条目才可触发（Git for Windows 默认 `core.protectNTFS` 会阻止常规 checkout，但 `ls-files` 只忠实输出 index 内容，跨平台或 `update-index --cacheinfo` 构造可产生），因此是"需要构造"的边界绕过而非当前数据的必然暴露；但该脚本的安全属性正是"任何形式下都不读取用户暂存内容"，所以此形式缺口应闭合。

**最小修复**：在 L375 之前增加"危险路径形式拒绝"，对 `$relative` 按 `[\\/]` 逐段检查：段尾为 `.`/空格、段含 `:`、段为 `..` 或 `.`、或规范化结果与原字符串不一致时 fail-stop；或改为用规范化后的相对路径（`$full.Substring($rootFull.Length)` 统一分隔符）参与排除匹配，并对"原始 relative 与规范化相对路径不等价"的情形一律 fail-stop（宁停不读）。同时在 self-check 中加入 `.tmp.driveupload./x`、`.tmp.driveupload /x`、`./.tmp.driveupload/x` 三条断言。

---

### F4 — P3 — `doc/tasks/P02PRE-R1F.md` L82（参照 L34、L92；`p02pre-r1f-manifest-20261011.md` L18）

**可复现原因**：Task L82 的证据列仍写 `final artifact target r6`，而同一文件 L34 与 L92 已把最终 parse artifact 定为 `p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`，manifest L18 也已改述为"R4 follow-up 后再产生并核对 R7 parser artifact"。这正是 Round 4 retry P3-F3 所指出的"陈旧 R6 行"在 Task 内的残留。此外 L81 的 `R5` 指 parser round 5，而同文件 L34/L91/L92 的 `R5` 指 Review Round 5，命名重叠易造成 pins 混淆（历史上已发生过 R3 SHA 截断、F3 陈旧引用两类混淆）。

**最小修复**：把 L82 的 `final artifact target r6` 改为 `NOT_RUN；superseded，final artifact = r8`；并把 parser 轮次统一写作 `parser R5/R6/R7/R8`，Review 轮次统一写作 `Review Round 5`。

---

### F5 — P3 — `doc/tasks/P02PRE-R1F.md` L89、`p02pre-r1f-manifest-20261011.md` L11、`p02pre-r1f-r5-selfcheck-20261011.json` L4–L5

**可复现原因**：首次 helper 失败 artifact 自记 `sourceBytes = 60662`、`sourceSha256 = AA99D7C4D9E38EE8FF14315AAE968226AE1FA67935283408F294603619B2A884`，而 R5 兼容重试 artifact 与当前冻结脚本均为 `60725` / `80C8BC31…E5216`。即该失败证据绑定的是**被替换前的候选字节**，与 R5 当前候选不是同一 artifact。Task L89 与 manifest L11 在引用它时只说明"helper 使用了 PS 5.1 不支持的 `SHA256.HashData`，在 parse/self-check 之前退出"（这一点与 JSON L8–L9、L22 的 CLIXML `MethodNotFound` 完全吻合，不应也不会被描述为脚本 parse 或自检失败），但没有标注其 source pin 与当前候选不同。

**最小修复**：在两处引用中补一句"该 artifact 的 `sourceBytes/SHA256=60662/AA99D7C4…`，绑定替换前的候选字节，不是当前 R5 候选；失败发生在 parse 之前，属 harness failure"。

---

### F6 — P3 — `verification/P02/p02pre-r1f-capture.ps1` L286（参照 `doc/tasks/P02PRE-R1F.md` L48）

**可复现原因**：`Get-RepositoryRecord` 的 record 初值（L286）没有 `errorOperation` 与 `error` 键，二者只在 `Set-RepositoryStop`（L277–L283）里写入。因此**成功**路径下完整 evidence JSON 的 `repository.main` / `repository.scratch` 不会出现 Task AC L48 明确列举的 `errorOperation` 字段（`Get-PartialRepository` L514 恰好因字典缺键返回 `$null`，partial 路径反而是自洽的）。

**最小修复**：在 L286 初值中补 `errorOperation = $null; error = $null`。

---

### F7 — P3 — `p02pre-r1f-manifest-20261011.md` L8（参照 `p02pre-r1f-capture.ps1` L599–L600）

**可复现原因**：manifest L8 声明"36 个环境变量……逐项沿用"R1 allowlist，而 L599 的 `$envNames` 我逐项点数为 **35** 个（LOCALAPPDATA … GIT_TERMINAL_PROMPT）。本次只读范围不允许打开 `p02pre-r1f-r1-manifest-20261011.md`，因此无法判定是 R1F 少采集一项，还是 manifest/R1 的计数本身含混。

**最小修复**：Codex 用 R1 manifest 逐项对账；若确为 35 项，修正 manifest L8 的计数与措辞；若 R1 确为 36 项，补回缺失变量。

---

### F8 — P3 — `verification/P02/p02pre-r1f-capture.ps1` L327 + L370–L380（参照 manifest L36–L38）

**可复现原因**：Task AC 与 manifest 把 `.tmp.driveupload` 的"no-read"表述为"在任何 `Get-Item`、`Get-FileHash`、`Get-Acl` 或其他文件内容/元数据访问之前排除"。脚本自身的 getter 序列（L370 起）确实满足该顺序；但 `git status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`（L327）在排除逻辑**之前**就已执行，Git 会自行对整个工作树（含 `.tmp.driveupload/` 下的 2148 个候选）做 lstat 枚举，并且对 tracked-but-racily-clean 的条目可能重新读取内容以判定工作树是否修改。manifest L37 已豁免"继承的 R1 exact getters"，但两处文档都没有把"排除保证只覆盖脚本自身的 getter 序列，不覆盖 Git status 的内部文件系统访问"写成显式边界。

**最小修复**：在 manifest L36–L37 的 user-staging 段落补一句边界说明（脚本层 no-read 成立；Git status/index getter 的内部访问属继承行为且不读取暂存内容语义）；证据 JSON 中可加一条同义 note。

---

## 逐项核对 1–6

**1. `.tmp.driveupload` 根与任意深度后代在任何 getter 前排除；只存聚合计数与首个相对路径；任何排除使 inventory=`UNPROVABLE` — `PASS`（caveat：F3、F8）**

证据范围：静态阅读 L107–L109、L370–L411、L753–L754。对该 candidate 而言，L375 的排除先于 L389 的 `Get-Item`、L407 的 `Get-FileHash`；只累计 `unreadUserDataCount` 与 `firstUnreadUserDataPath`（L376–L377、L510–L511），不写逐项 size/timestamp/attributes/hash；L424/L753 在有排除时判 `UNPROVABLE`（L753 的 `$repoUnreadUserDataCount -gt 0`），不会虚报完整 hash PASS。限定条件：仅对 Git 规范输出的相对路径形式成立（F3），且排除保证不覆盖 L327 的 Git status 内部访问（F8）。

**2. path normalization 与 repo boundary 校验先于排除且边界正确；separator / 大小写 / 路径形式 — `FAIL`（F3）**

证据范围：L366 构造带尾随 `\` 的 `$rootFull`，L373–L374 以 `OrdinalIgnoreCase` 做前缀比较 → 顺序与边界（`G:\CODEX\New Manga\` 不会误匹配 `...New MangaXYZ\`）正确；separator 覆盖 `/` 与 `\`（L108、L383）；大小写由 `OrdinalIgnoreCase` 覆盖并有 self-check L130 断言。未通过的是"路径形式"：排除匹配使用未规范化的原始 relative，尾随点/空格段与 `./` 前缀形式可绕过排除并被 Win32 解析到同一目录（详见 F3）。另外 Task L25 的"规范化后排除"措辞与实现不符（规范化只用于边界检查），此点归入第 6 项。

**3. detached `symbolic-ref` 仅在冻结条件完全吻合时接受，其他 fail-stop；main 精确匹配 — `PASS`**

证据范围：L111–L113 要求 `exitCode -eq 128`、`stdoutBase64 -eq ''`、`stderrBase64 -ceq 'ZmF0YWw6IHJlZiBIRUFEIGlzIG5vdCBhIHN5bWJvbGljIHJlZgo='` 三项同时精确（`-ceq` 区分大小写；Base64 常量本身即 38 bytes `fatal: ref HEAD is not a symbolic ref\n`，与 manifest L24 一致）；L313–L316 只在 `$ExpectedBranch -eq 'DETACHED'` 时启用该映射，其余非零（含 exit≠128、stdout 非空、stderr 任一字节差异）都走 `$branchQueryFailed` → `GIT_BASELINE_QUERY_FAILED` fail-stop；L324 对 main 用 `stdout.Trim()` 与 `'main'` 精确比较，L325–L326 target mismatch 即停。self-check L133–L135 覆盖"精确接受"与"另一种 stderr 拒绝"两个样本；函数逻辑本身要求三条件同时成立，故其他组合必然被拒，但 self-check 未显式断言这些组合（可选的 P3 覆盖增强，本次不单列 finding）。

**4. inventory counters / 失败路径 / self-check / JSON 输出自洽；不把 skipped user files 或 symlink target 报作已验证 hash — `PASS`（caveat：F6、F7）**

证据范围：三条计数路径分别 `processedCount++`（L376–L379、L396–L398、L409–L410），L414–L415 强制 `processedCount = candidateCount` 且 `omittedCount=0`，与 manifest L39 的等式一致；失败路径经 `Set-RepositoryStop` 计算 `omittedCount`（L282），未解析列表时保持 `candidateCountKnown=false` / `omittedCount=null`（L286–L287）；symlink 只记 `targetRead='NOT_ATTEMPTED'` / `targetHash='NOT_CAPTURED'`（L395）并立即 `break`/`continue`（L400、L405）不再对该路径发起任何查询，`regularFileHashCount` 不含 skipped 项；L753–L754 的 note 也不把 skip/exclusion 说成 PASS。caveat：F6 的字段缺失、F7 的 env 计数待与 R1 manifest 对账。`ls-files` 的 NUL 终止伪空项不计入 candidate（L145–L156、L184）、大小写碰撞 fail-stop（L175、L189–L191）、`indexStages` 结构校验（L167–L174）均与 manifest L34–L35/L48 一致。

**5. R1F 仍限于 manifest 精确只读 allowlist 与一次性 `CreateNew`；无绕过身份/目标校验、未知子进程、范围外写入或提前 capture — `PASS`（证据范围限于本次读取的文件）**

证据范围：子进程仅两类——L91–L92 的 `git.exe`（固定 `rev-parse` / `symbolic-ref` / `status` / `ls-files --cached --others --exclude-standard -z` / 新增 `ls-files --stage -z`）与 L573 的 `whoami.exe /all`，未见 shell、包管理器、编译器、网络或 COM 调用，与 manifest L23 一致；身份在 L563–L586 先校验 `HOME-MY\49745` / SID 才继续，repo target 在 L325–L326 校验 root/common-dir/HEAD/tree/branch；唯一写入是 L788 的 `FileMode.CreateNew`，且 L15 预先拒绝已存在的目标；Git 以 `--no-optional-locks -c core.fsmonitor=false -c core.untrackedCache=false` 运行（L91），避免 index 刷新写盘；L599–L638 的 env / input roots（12）/ output leaves（13）/ canary leaves（3）/ WER 目录（3）/ registry（2 hive × 2 view × 4 value）与 manifest L8 声明的继承清单形态一致，且 canary 只读不写（L630–L634）。脚本自身即 capture，一旦被调用即开始采集，无内部 release gate——这与 manifest L52 由外部 adjudication 释放一次调用的约定相符，属设计约定而非缺陷。**未验证子项**：仓库内是否还存在其它调用点（本次只读文件范围之外）→ 该子项 `UNPROVEN`。

**6. Task / manifest / script / 自检 artifact 的叙述、参数、限制、禁止项、验收标准相互一致 — `FAIL`（F4、F5、F7，及 Task L25 措辞）**

证据范围：一致项——Task L33/L34 的 evidence target、R8 artifact 路径与脚本 L5、manifest L25/L52 一致；Task L42/L44/L45/L47 的验收条件与脚本 L375–L379、L111–L113、L394–L400 的语义一致；Task L61–L63 的 R6/R1 pins、manifest L9/L10 不再被当作当前 baseline；`p02pre-r1f-r5-selfcheck-retry-20261011.json` 自记的 `sourceBytes=60725`、`sourceSha256=80C8BC31…E5216`、`parentRecheckSha256`、`childInputSha256` 三处互相一致，且与用户给定 pin 及 Task L90 / manifest L12 的字面值一致；失败 artifact 的 CLIXML 错误文本与 Task L89 / manifest L11 的"harness 在 parse 前因 `SHA256.HashData` 退出"描述吻合（不得表述为脚本 parse 或自检失败）。不一致项——Task L82 的陈旧 `r6 final`（F4）、失败 artifact 的 source pin 未标注（F5）、env 36 vs 35（F7）、以及 Task L25 "规范化后排除"与实际只对原始字符串匹配的措辞差异（F3 的文档侧）。另外 Task L34/L91 明确要求本轮 Review 不得把 self-check 或本轮静态审查当作 Gate 结果，文档这一限制表述是正确且清晰的。

---

## 证据范围与声明

- 我只阅读了下列文件：`doc/tasks/P02PRE-R1F.md`、`verification/P02/p02pre-r1f-manifest-20261011.md`、`verification/P02/p02pre-r1f-capture.ps1`（803 行）、`verification/P02/p02pre-r1f-r5-selfcheck-retry-20261011.json`、`verification/P02/p02pre-r1f-r5-selfcheck-20261011.json`。
- **我未运行任何命令、未执行该脚本或任何 capture、未调用任何 host getter、registry 或 ACL API，未访问 `.tmp.driveupload` 内容，未读取其任何 metadata，未创建、修改或删除任何文件。**本 Review 的所有结论均来自上述文件的静态阅读。
- `p02pre-r1f-capture.ps1` L639（protected-hash 清单首段）超过读取工具的单行显示上限而被截断为 2000 字符，该清单未能逐条核对 → 该子项 `UNPROVEN`。
- 未打开 `p02pre-r1f-r1-manifest-20261011.md`（不在授权读取清单内），因此 R1 继承 allowlist（12 input roots / 13 output leaves / 3 canary / 环境变量数量 / 保护文件集合）的逐项等价性只能核对形态，不能核对逐项一致 → 该子项 `UNPROVEN`（并由此产生 F7）。
- 我无法在"不运行命令"的前提下独立复算任何 SHA-256 或字节数，因此 Task/manifest/self-check 之间的 pin 一致性只按**字面值**核对，字节数与哈希的独立复核必须由 Codex 在 adjudication 中用 `Get-FileHash` 完成 → `UNPROVEN`。
- F1、F3 的推理是纯静态且结论确定的代码语义推演；F2 的两种后果取决于 PowerShell 对 `[string]$null` 的绑定归一，需 Codex 用 Windows PowerShell 5.1 实测二选一。以上均**尚未在 host 上执行验证**。
- 本次 Review 仅为代码与文档的静态只读审查，**不是** P02PRE Gate、Technical Gate 或 Build Gate 的 PASS；也不改变 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE` 的既有状态。
- 本次审查不能替代 R8 parse-only，也不能替代（更不能建议跳过）Codex pre-run adjudication 与 post-run 五态裁定。

## 推荐下一步

1. Codex（作者）修复 F1（必须）、F2、F3，并顺带处理 F4–F8；F1 修复后 self-check 必须新增"parent 目录组件"与"leaf 目录"断言，F2 修复后必须新增"无 index mode 的 regular file"断言。
2. 修复产生新的 exact bytes 后，重新冻结 Task/manifest/script/self-check pins，并重新派发 Round 5 非作者只读 Review（不沿用本轮结论）。
3. Round 5 复审 `APPROVED` 且 Codex 独立核对 pins 后，才对新 bytes 运行 Windows PowerShell 5.1 `ScriptBlock::Create` parse-only 并落 `p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`（`captureScriptInvoked=false`）。
4. 之后仍需独立的 Codex pre-run adjudication 核验 pins、身份/SID、main/scratch roots 与 refs、输出目标 absent、status/index 稳定、路径范围与保护文件基线；只有全部匹配才可执行 manifest L52 的一次 capture。任何 mismatch 一律保留原始 partial evidence 并停止，不重试、不清理。
