# P02PRE-R1 非作者独立静态 Review

**结论：`CHANGES_REQUESTED`**
P0=`0` / P1=`2` / P2=`6` / P3=`3`（共 11 项）
安全侧：**未发现范围外写入或路径越界**；但**证据完整性/版本兼容性有实质缺口**，因此本轮不给出可执行放行（不作 `APPROVED`）。

---

## 一、Review 覆盖与未覆盖（先声明事实边界）

**已独立完成（只读）**

- 完整读取 `doc/tasks/P02PRE-R1.md`（55 行全文）、`verification/P02/p02pre-r1-manifest-20261011.md`（71 行全文）、`verification/P02/p02pre-r1-capture.ps1`（300 行全文），逐行核对查询对象、参数、进程、写入路径与分类语义。
- 交叉读取 `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`（239 行全文），逐条比对 §允许读取路径（12 输入根）、§Scratch 写入/ACL/输入输出（13 leaves + 3 canary）、§TEMP/cache 环境表、§Registry 读写边界（WER 两键 + 3 目录）、§受保护文件（Git 命令与 `.git/HEAD|index|config`）、§证据（64 MiB / CREATE_NEW）。
- 核对存在性：`verification/P02/p02pre-r1-evidence-20261011.json`、`doc/tasks/P02PRE-R0S6.md`、`verification/P02/p02pre-r0s6-checkpoint-20261011.md` 均**不存在/已存在**已按 glob 结果确认（证据文件当前不存在，符合“Review 前不得运行”）。
- 用 Microsoft Learn（PowerShell 5.1 文档）确认 `Get-Acl -LiteralPath` 在 5.1 中存在（ByLiteralPath 参数集，WinPS 3.0 引入），排除了一个疑似 P0 误报。

**未覆盖 / 未核验（不得被我方文字替代）**

1. **bytes/SHA-256 未独立复算**：本会话 `pwsh` 工具在沙箱准备阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`），按指令未做 ACL 修改、未提权重试、未绕行、未换 shell。故 Task/manifest/script 的 `6050 / 9085 / 19113 bytes` 与三个 SHA-256 与 prompt pin 的匹配**未经我独立确认**（内容级审查成立，hash 级绑定未成立，按仓库先例「不可核验 ≠ 不匹配」）。
2. **未运行任何东西**：未执行 capture script、未跑 PowerShell/Git/OS/API/registry/WER/token/ACL/path 命令、未做 build/Cargo/AC、未改 Gate 或 Task 状态、未写任何文件。
3. 只做了必要范围的 r6 交叉核对；未重审 r1–r5 全部历史证据、未复核 scratch 实际 HEAD/tree（`7ce3c40c…`/`ce8056b8…`）、未复核治理文件（Plan/STATUS/COLLABORATION）当前文本。
4. 静态审查**不是**脚本已运行、也不是任何 OS 条件通过的证据。

---

## 二、Findings

### P1-1｜捕获结果的原子性风险：一次 64 MiB 上限即“零证据”结束
- **位置**：`p02pre-r1-capture.ps1:288-297`（`ConvertTo-Json -Depth 16` 后 `finally` 内一次性写盘）；对照 `manifest:15-16`、`manifest:71`、`task:37`。
- **触发**：主仓与 scratch 均启用 `--untracked-files=all` + `ls-files --cached --others --exclude-standard`，会对**每个** Git 登记/未跟踪 regular file 记录 path/length/LastWriteTimeUtc/SHA-256（`:163-179`），并另存 status 的 Base64 全文（`:159`）。JSON 先在内存成型，超过 67108864 字节则抛错，`finally` 之前中止，**磁盘不产生任何文件**。
- **影响**：本仓库 `verification/P02` 单目录已有 1201 个路径（glob 实测），工作区含大量未跟踪内容且 dirty；一旦超限，唯一允许的运行结果不存在，按 `manifest:71` 又不允许重试/修复，R1 直接空转一轮，且错误归属会被外层 runner 记为脚本异常而非“证据超限”。
- **具体修复**（任一，需 back-to-Review）：(a) 明确 64 MiB 的适用性与超限后的记录方式（例如先写一段固定头再由外层追加，或改为 `CreateNew` 后流式分块写同一文件）；(b) 缩小 inventory 范围 / 记录 hash 前先输出估算与 `recordCount`；(c) 决定是否允许超限时仍产出“截断声明 + 已完成集合”的证据文件。**不要**用删除/重跑来绕过。

### P1-2｜原始字节 vs 规范化字符串：status 的 SHA/Base64 不是 Git 原始输出
- **位置**：`p02pre-r1-capture.ps1:51-52`（`StandardOutputEncoding = UTF8`）、`:56-60`（`ReadToEndAsync` 得字符串）、`:153`（`[Text.Encoding]::UTF8.GetBytes([string]$status.stdout)`）、`:158-159`；对照 r6 `:158`「以 NUL 分隔解析，不对路径 quoting/空格/非 ASCII 做文本替换」与 `manifest:62-63`。
- **触发**：任意非 UTF-8 合法序列的路径字节（`core.quotepath=false` 下 Git 直接输出原始字节）或非 UTF-8 区域设置，字符串往返会引入 U+FFFD 替换字符。
- **影响**：`status.sha256`/`base64` 被称为“raw bytes”，实际是 UTF-8 解码再编码的结果，**不是**可与其他工具复算对齐的原始字节摘要；与 r6 的 raw status 口径存在不可见偏差。
- **具体修复**：以字节方式读取子进程 stdout（例如 `Stream` + `Read` 到 `MemoryStream`，不设文本编码），对**真字节数组**同时计算 SHA-256、Base64 与 record 解析；`whoami` 等文本输出可另设字段。旁证记录已在 `verification/P02/p02pre-r0s6-review-20261011.stderr.log` 的同类讨论中出现，建议一并闭环。

### P2-1｜`HOMEDRIVE`+`HOMEPATH` 仅记录、未做拼接一致性断言
- **位置**：`p02pre-r1-capture.ps1:249-250`；对照 r6 `:34`「`HOMEDRIVE+HOMEPATH` 必须精确组合」、`:99`。
- **触发**：任何与 scratch `tmp\home` 组合不一致的环境值。
- **影响**：分类直接落为 `tempCache = PASS_WITH_EVIDENCE`（`:278`），不一致的组合仍可被读成“已取证通过”，违反“不得把未知事实转成 PASS”。
- **修复**：加入拼接比较（`$homedrive + $homepath` 与 scratch `tmp\home` 的规范化比较），不一致记 `FAILED` 或 `UNPROVABLE` 并进入停机上报告。

### P2-2｜`QUERY_ERROR` 停止条件未实现（ACL 变化/未知对象/范围外访问）
- **位置**：全脚本；对照 `manifest:69-71`、`task:36`、`task:53`。
- **触发**：运行期发生 ACL/SDDL 变化、出现未冻结的 WER 值/子键、或对象所有权不可核验时。
- **影响**：脚本对这些条件的处置是“照常记录并继续/正常收尾”，没有把“任何意外写/ACL 变化、WER query 出现未冻结对象”升级为停机上报告；作为证据审查，无法区分“安安静静”与“悄悄变了”。亦可并入 P1-1 一并改：把 per-object 的 `QUERY_ERROR` 计数与阈值写入顶层，并在非零时置 `stopReason`（例如 `STOP_SCOPE_OR_ACL_UNCERTAIN`），退出非零但仍落盘完整 partial 证据。
- **修复**：显式实现并落证停止条件（对所有 allowlist 外访问为零、per-object `QUERY_ERROR` 计数、以及文档化的 ACL 稳定性口径）。

### P2-3｜reparse 校验仅在“对象自身”，不含祖先链
- **位置**：`:85-101`（`Get-FileRecord` 只查 `$item.Attributes`）、`:105-127`（`Get-ExactDirectoryRecord` 同样只查对象自身）、`:131-136`（只查 repo root 与 `.git`）、`:182`（`.git\HEAD`/`index`/`config` 走 `Get-FileRecord`）；对照 r6 `:70`「任一根的 file ID、reparse、路径组件或现有授权不可核验即停机」、`manifest:28`。
- **触发**：任一查询根/叶子**祖先**中存在 junction/symlink（例如某 `task-envs` 或工具目录被链接），对象自身非 reparse 故不会被记录为异常。
- **影响**：`Get-Item`/`Get-FileHash`/`Get-Acl` 会沿链跟随，实际读取对象可能与冻结字符串的字面路径不一致，且证据里看不出这一点；对 `.git/index` 的同理情形还会削弱 TOCTOU（`indexStable`，`:137/183/184`）的证明力。
- **修复**：对每个查询对象逐段校验祖先 reparse 状态（脚本已在文件 inventory 循环 `:169-174` 用同一手法做对，建议抽出为公共函数复用到所有对象与 repo root 的 `.git` 链）。

### P2-4｜枚举被字符串化成数字，而非可读名称
- **位置**：`:200`、`:209`（`hive = [string]$hive`）、`:200`（`view = [string]$view`）。
- **触发**：无条件。
- **影响**：证据里出现 `[Microsoft.Win32.RegistryHive]` 的**数值**（LocalMachine=2147483648 等）而非 `LocalMachine`/`CurrentUser`、`Registry32/Registry64`，降低可读性与后续独立复核的确定性。
- **修复**：用 `[System.Enum]::GetName(...)` 或 `$hive.ToString()`（显式调用实例方法，避免 PowerShell 自动字符串化路径差异）。

### P2-5｜`.NET Framework 托管枚举的显示名依赖运行时**
- **位置**：`:198`、`:194` 的 `OpenBaseKey`、`RegistryView.Registry32/64`。
- **触发**：任何运行时/框架差异。
- **影响**：与 P2-4 叠加时更难判断记录的是哪个 hive/view；属“证据可复核性”而非安全缺陷。
- **修复**：同上显式 `GetName`，并对 hive/view 记 `DisplayName` 与数值双字段。

### P2-6｜`Get-FileRecord` 对 `REPARSE_POINT`/`NOT_FILE` 不抛错、不停止
- **位置**：`:91`、`:90`、`:182-183`；对照 `task:53`「遇到 reparse/非 regular 文件无法安全归属……停止」。
- **触发**：`.git\HEAD`/`.git\index`/`.git\config` 被重定向为 reparse（worktree、junction、攻击面）。
- **影响**：脚本返回 `REPARSE_POINT` 记录后继续后续对象，**没有**进入停机路径，属“静默降级证据”。同时 `gitMetadata.add()` 的返回状态从未被聚合断言。
- **修复**：把 `gitMetadata` 三件的 `state` 与两个 index 快照显式纳入 `$record.state`/`stopReason` 判定。

### P3-1｜`finally` 内抛错会掩盖原始 stopReason / 退出归因
- **位置**：`:287-297` 与 `:299`。
- **触发**：`ConvertTo-Json` 或证据写盘本身失败（含父目录不可用、磁盘满）。
- **影响**：`finally` 的异常先于 `:299` 的 `throw`，外层只看到写盘异常，丢失已判定的 `stopReason`；且 `:289` 的 64 MiB 判断在 `finally` 内抛出会附带二次异常语义。
- **修复**：写入/序列化包一层 try/catch，把异常追加到 `$Result.errors` 并保留原 `stopReason`（仍不清理、不重试）。

### P3-2｜WER registry 量未记“last-write metadata（若 getter 可得）”
- **位置**：`:200-206`；对照 `manifest:55`。
- **触发**：无条件。
- **影响**：manifest 用“若可得”豁免，属可接受缺口，但应在证据里显式标注“not available/未采集”而不是省略字段，避免被读成漏采。
- **修复**：增加 `lastWrite: 'NOT_AVAILABLE_BY_GETTER'` 或等价字段。

### P3-3｜porcelain 计数口径未注明
- **位置**：`:157`（以 NUL 切分计非空段为 `recordCount`）。
- **影响**：与 `--no-renames` 组合时通常等于记录数，但未在证据中声明口径；重命名/异常记录下可能出现 1 条记录 2 段。
- **修复**：字段名或旁注写明“NUL 分段数（近似记录数）”。

---

## 三、明确通过的部分（避免只报缺口）

- **写入面最小且合规**：全脚本唯一写操作是 `:290` 的 `[IO.File]::Open($EvidencePath, FileMode::CreateNew, Write, None)`，路径为 `manifest:15` 授权的唯一 evidence 路径；无 append/overwrite/retry/move/delete，无 scratch/工具根/user data/WER/registry 写入，无 ACL/owner/label 改动，无 profile Create/Delete，无 build/Cargo/AC，无外部下载，无 Sandbox 查询。
- **存在性门先于一切查询**：`:15` 先判 evidence 目标，命中即抛错、零查询、零写入；`finally` 未执行（该分支不在 try 内），不会产生第二份证据。证据文件当前确实不存在（glob 实测），符合作者“Review 前不得运行”的声明。
- **身份门顺序正确**：`:216-237` 先取 `WindowsIdentity.GetCurrent()`/SID/authentication/impersonation/IsInRole/PID/启动时间/executable/PowerShell 版本/CWD 与 `whoami.exe /all`，与 `ExpectedUser=HOME-MY\49745`、`ExpectedSid=S-1-5-21-…-1001` 比较，不匹配即置 `IDENTITY_MISMATCH`，后续全部块被跳过（`:237-281`），符合 `manifest:20`。
- **子进程 allowlist 精确**：仅 `C:\Program Files\Git\mingw64\bin\git.exe`（`rev-parse --show-toplevel --git-common-dir HEAD HEAD^{tree}`、`symbolic-ref --short HEAD`、`status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`、`ls-files --cached --others --exclude-standard -z`）与 `C:\Windows\System32\whoami.exe /all`；`UseShellExecute=false`、无 shell/compiler/package manager/network/COM；`--no-optional-locks` 及四项 `-c` 与 `manifest:61` 逐字一致；`-C "<root>"` 对含空格路径正确加引号。
- **对象清单逐项一致**：12 输入根、13 output leaves、3 canary leaves、WER 两键×两 view×四 value、3 个 WER 目录、36 个环境变量名、12 个 protected hash 文件——与 r6 表、`manifest:26-57`、`manifest:273` 的清单逐项对齐，未发现额外对象或漏项（唯一差异为相对路径带/不带尾斜杠，不影响 `Join-Path` 结果）。
- **分类语义未被篡改**：`manifest:69`/`task:23`/`task:38` 要求的 `UNPROVABLE`/`REQUIRES_ACTIVE_TEST`/`NOT_RUN` 固定值原样写入（`:33-38`），未把 `UNPROVABLE` 改写为 PASS；`human-required` 原文与 Gate 状态不在本脚本职责内，未见越权声明。
- **Windows PowerShell 5.1 兼容性（静态）未发现明确不兼容构造**：`Get-Acl -LiteralPath` 经 Microsoft Learn 5.1 文档确认存在；`.NET Framework 4.5+` 的 `ReadToEndAsync`、`FileStream.Flush(true)`、`ConvertTo-Json -Depth`、`[ordered]@{}` 均在 5.1 可用；`if` 作为赋值右侧表达式（`:145-149`、`:185`）在 5.1 合法（不可用于参数位，本脚本未如此使用）。但这只是静态判断，见 P1 前置的“未实测”缺口。

---

## 四、对“本 preflight 能否放行一次调用”的回答

- **可以安全 Review**：脚本的**读集合**与**写集合**均在 allowlist 内，未发现范围外路径/进程、未发现覆盖/截断、未发现用户数据、漫画、数据库、Lock、Revision、凭据、模型、WER dump 内容被读取，也未发现 ACL/owner/label/registry 写入。就此意义，它在“不会造成不可接受副作用”上**未见阻塞项**。
- **但本轮不作为单一调用放行**：P1-1（超限即零证据）与 P1-2（raw status 字节口径不符 r6）会直接影响 R1 证据的**存在性与可复算性**——而 R1 的全部价值就是产出可被独立复核的宿主基线。按项目规则，证据口径不成立时不应执行（`manifest:9`、`manifest:71`）。同时 `p02pre-r1-*` 产物当前只有 manifest 与脚本（glob 实测），尚无任何 5.1 实测/解析证据，而 `manifest:13` 冻结的是 `Windows PowerShell`（CWD=`G:\CODEX\New Manga`）。
- 因此建议顺序：**修 P1-1/P1-2（可一并处理 P2-1/P2-2/P2-6）→ 冻结新 bytes/SHA → 非作者再审 → Codex adjudication → 才允许唯一一次调用**。任何修补都必须重新绑定 hash，不得就地“边跑边改”。

---

## 五、给下一步的最小可执行指令（供 Codex 转发，非我方执行）

> 致 Codex（P02PRE-R1 Owner）：非作者 Review 结论为 `CHANGES_REQUESTED`（P0=0/P1=2/P2=6/P3=3）。请在 `verification/P02/p02pre-r1-capture.ps1` 与 `p02pre-r1-manifest-20261011.md` 内闭环：(1) 证据写入原子性与 64 MiB 口径（流式或分块写同一 `CreateNew` 目标，超限仍产出带“已采集/未采集”标记的 partial 证据）；(2) status stdout 以原始字节采集并据此计算 SHA-256/Base64 与解析 records；(3) `HOMEDRIVE+HOMEPATH` 拼接一致性断言；(4) 明确实现并落证 `QUERY_ERROR`/ACL 变化/未冻结 WER 对象/范围外访问的停止条件与顶层计数；(5) 所有查询对象（含 `.git/HEAD|index|config` 与各 root 的 `.git` 链）做祖先 reparse 校验并把异常纳入 stopReason；(6) hive/view 用可读名称。修改后重新冻结 bytes/SHA，并**在真实 Windows PowerShell 5.1 下做一次只读解析核查**（例如 `powershell.exe -NoProfile -NonInteractive -Command "$null=[scriptblock]::Create((Get-Content -Raw 'verification/P02/p02pre-r1-capture.ps1'))"`，仅解析、不执行、不写文件），把命令/exit/stdout 存为 `verification/P02/**` 证据后交非作者复审与本轮 findings 处置说明。在复审通过前，不得运行 capture script、不得创建 `p02pre-r1-evidence-20261011.json`，Build Gate/Hard Build Barrier/AC1–AC7 维持现状。

**（Review 结束；本报告不构成脚本已运行或任何 OS 条件通过的证据。）**