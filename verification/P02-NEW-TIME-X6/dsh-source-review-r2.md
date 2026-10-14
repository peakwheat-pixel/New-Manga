# P02-NEW-TIME-X6 — I1 后唯一一次 bounded source Review r2

**reviewed_head**：`3c707261556293bbc884e0b38c63161274aa1638`
**manifest SHA-256**：`8316DE93E3E817F757BEBA0DEDF49155C6C109D36AC9DF532837DE19DCA90040`
**manifest**：`verification/P02-NEW-TIME-X6/dsh-source-review-input-manifest-r2.json`（10 个 pin，`:11-82`；`source_commit=db69a62c…`、`review_head=3c707261…`，`:4-5`）

## Verdict：**PASS**（bounded review passes；无未解决 P0/P1/P2，不请求再次返修）

---

## 1. Pin 核验（含我无法复算的部分）

可离线交叉核对、且**全部一致**：

| 制品 | input manifest r2 | source-manifest-r2 | Task Canonical Evidence |
|---|---|---|---|
| executor | `43ee7be2…` / 105343 B / blob `54afebd9…`（`:28-30`） | `:46-47` | `TASK:114` |
| selftest | `a8823f59…` / 85767 B / blob `9ee1c95a…`（`:35-37`） | `:55-56` | `TASK:115` |
| protocol r2 | `6216b0bc…` / 13555 B（`:42`） | `:64-65` | `TASK:116` |
| inventory r2 | `f980922e…` / 10072 B（`:49`） | `:73-74` | `TASK:117` |

另一致：Handoff `6d34dd92…`（`MAN:21` = `TASK:118`）、input manifest r1 `7b219c5c…`（`MAN:63` = `TASK:119`）、r1 report `b3926a72…`（`MAN:70` = `TASK:121` = `adjudication-r1:6`）、adjudication `ebb80d98…`（`MAN:77` = `TASK:122`）。行数与实读一致：executor 1957（`SMAN:45`）、selftest 944（`SMAN:54`，实读 `selftest:944`）。r2 input manifest 的 10 个输入与 `TASK:102` 记录的 “官方 `--verify`=PASS（10/10）、3264 B” 相符。

**未由我复算**：`pwsh` 在本会话因沙箱无法为工作区建立写授权而不可用（Win32 5），审批通道不可用，故未执行任何命令（含只读命令）；因此 manifest 自身 SHA-256、磁盘字节 SHA-256、`git_blob`、当前 HEAD 与 clean 状态均**未独立复核**，采信 `TASK:102` 记录的 Codex 官方 10/10 verify 与本次派发陈述（该补足见 `adjudication-r1:9` 的既有口径）。

---

## 2. SR-01/02/03 关闭表

| Finding | 结论 | 证据（path:line） | 说明 |
|---|---|---|---|
| **X6-SR-01**（index 采样对象） | **CLOSED** | `EXEC:1728` `@('rev-parse','--absolute-git-dir')`；`EXEC:1862-1864` 归一化 + `Require [IO.Path]::IsPathRooted`（`GIT_ABSOLUTE_DIR_INVALID`，`:1863`，不再回退拼 worktree）+ `Join-Path <worktreeGitDir> index`；`EXEC:1865-1872`/`:1916-1923` 观测更名 `worktree-git-index-hash-before/after` 且 Method/GetterInput 注明来源；`EXEC:1926-1931` 检查更名 `worktree-git-index-after-unchanged`，Expected 明写 “THIS worktree's own index … NOT the main repository .git/index”，Summary 输出 `path=`；`--git-common-dir` 全文 **0 处**（grep）；executor 内无 64-hex 字面量（I2 未回退）；`SELFTEST:221/266/267/268` 对应静态断言。 | 现在唯一被读的 index 是 `$rootIndexPath`（`:1864`）。`adjudication-r1:16` 记录的独立实测 `--absolute-git-dir`=`G:/CODEX/New Manga/.git/worktrees/P02-NEW-TIME-X6`，与本修复目标路径一致。 |
| **X6-SR-02**（freeze manifest 落点） | **CLOSED** | 新纯函数 `EXEC:577-589`（段级 `.`/`..` 拒绝）；多根签名 `EXEC:591-621`：dot-segment 先拒（`:607`）→ `[IO.Path]::GetFullPath` 词法规范化（`:609`）→ `IsPathRooted`（`:611`）→ 空根/根含 dot-segment/规范化失败一律 false fail-closed（`:606/614/617`）→ 分隔符边界、`OrdinalIgnoreCase` 比较（`:618`）；新常量主仓根 `EXEC:129`。**读取字节前四层顺序**：`:1495` 非空 → `:1496` 控制字符 → `:1497` 历史段隔离 → `:1501` dot-segment → `:1505` 双根（`@($script:Worktree,$script:MainRepositoryRoot)`）→ `:1506` Exists → `:1510-1512` manifest 路径链 reparse 检查（`Test-PathAncestorsOrdinary`，要求 `leafExists` + 非 reparse + `allOrdinary`，判定式见 `:1086-1089`）→ **`:1515` ReadAllBytes**。`SELFTEST:274/275/276/277` 接线断言；边界集 `SELFTEST:686-706`（主仓根/根自身拒绝 `:689-690`、主仓内历史 `verification/P02/` 拒绝 `:691`、`..` 别名 `:692`、`.` 段 `:693`、反斜杠 `:694`、大小写 `:695`、空根列表 fail-closed `:696`、**合法 agent-output 根仍被接受 `:698`**、主仓内同名 Task 目录拒绝 `:699`）。 | 三个指定向量（主仓根、dot-segment、reparse/junction）全部覆盖，且均先于 manifest 字节读取；`:698` 同时排除了“修复过度阻断合法落点”的回归。 |
| **X6-SR-03**（raw-capture 授权） | **CLOSED** | `INV:16-29` `rawCaptureAuthorization`：root（`:17`）、rule 明确 `freeze-manifest.json` **不**自动授权同目录任何其它文件（`:18`）、六项必需文件（`:20-25`：`command.md`/`stdout.md`/`stderr.md`/`exit.md`/`environment.md`/`session.md`）、absentPrecondition（`:27`）、partial/failure 保留与同 RunId 绝不补写（`:28`）；目录级目标 `INV:41-47`；逐文件目标含 writer/timing/constraint/status=NOT_CREATED（`:56-96`）。协议侧：`PROTO-R2:75-77` §3.4、`:89-92` §4 目标表、`:98` 位置规则；`SMAN:68-75` pin inventory r2。 | 与 `TASK:42` 的六项（原始命令/stdout/stderr/exit/环境摘要/session）逐项对应，未扩大范围；写入者=ZCode operator session，落在 `TASK:63` 已授权路径内。 |

**Question C（原 scope/AC 是否仍满足）**：AC 文本六项与本 Task 允许/禁止范围**未被 r2 修改**（`TASK:51-71`），r2 只新增/替换本 Task 专属目录内文件；`TASK:77` 仅声明 “AC1 交付部分 PASS（r2）”，`TASK:78-83/103-105` 与 `HANDOFF:76-78` 明确 AC2–AC7、Parser、selftest、freeze、pre-run、one-shot、Build/Cargo、Sandbox、产品 AC1–AC7 **全部 NOT_RUN**，无 X6 运行成功主张。未触碰旧 `verification/P02/**`、旧 H1/P2-1 证据或 13 项历史缺失记录（`HANDOFF:17`，manifest 文件表亦无此类路径）。

---

## 3. 本次修复直接引入的新 P0/P1/P2

**无。** 逐项核对：(a) 写入面未变——全文仍只有 `Open-ExclusiveCreateNew`（`EXEC:1133` `CreateNew` + `FileShare.None`）一个写入点，无 `Remove-Item`/`Set-Content`/`Out-File`/`New-Item`/注册表/`Start-Process`（grep：仅注释与函数名命中）；(b) 子进程仍只有 `ProcessStartInfo` 单一入口（`EXEC:1338`），新增的只是同一冻结 `git.exe` 的只读 `rev-parse --absolute-git-dir`（`EXEC:1728`），未扩大子进程边界；(c) 无悬空变量：`--git-common-dir`/`$commonDirRaw`/`$commonDirNormalized`/`$revCommonDir` 全文 0 处（StrictMode 下不会因改名抛出）；(d) 历史隔离与 `ForbiddenWritePrefixes` 多层保护保持（`EXEC:1497/1553/1605/1561`）；(e) 新检查未把主仓 index 卷入任何读写，也未新增可删除/可覆盖路径 → 无安全、数据损坏或不可逆执行风险。

**非阻塞观察（非 P0/P1/P2，不请求返修，仅作 freeze 程序输入）**：
1. `\\?\` / `//?/` 扩展长度前缀不会被 `GetFullPath` 归一化（`EXEC:609`），而参数 `ValidatePattern` 允许 `//` 形式（`EXEC:99`），故刻意构造的 argv 形式仍可在字符串上“看似在双根之外”。冻結调用式（`PROTO-R2:67-70`）使用普通盘符形式，不构造该形式即不可达；建议 freeze 记录中写明 argv 采用普通盘符路径即可，属 freeze 程序项而非交付返修项。
2. `INV:27` 的 `absentPrecondition` 措辞为“X6-AC5 开始前整个 `<RunId>/` 目录必须 absent”，而同一句与 `INV:45` 又规定目录由 Codex freeze 在 AC4 创建并含 `freeze-manifest.json`；逐项目标（`INV:56-96`）与 `INV:18`（禁止清理/改写、不自动授权 sibling）已无歧义，故仅为读解提示。
3. reparse 链检查现同样作用于 manifest 链（`EXEC:1510-1512`）：若 `G:\CODEX\New Manga.workspace\…` 链上存在 junction/symlink，将以 `FREEZE_MANIFEST_INVALID` fail-closed。这是 `adjudication-r1:17` 要求的语义，且同一子树在 r1 已因输出目录链 `chainAllOrdinary`（`EXEC:1569-1570`）被要求无 reparse，未引入新的环境依赖类别；`HANDOFF:103` 已如实披露，列为下述运行期 Gate。

---

## 4. P3/P4 backlog（明确未重开、未修复）

`X6-SR-04..13` 按 `adjudication-r1:19-28` 与 `source-manifest-r2:18`（`backlogUntouched`）**保持 backlog**；本次未重开、未评估、未要求返修。我可确认它们仍存在于 r2 交付中（例如 selftest 仍在 `SELFTEST:107` 调用 `Get-Process`，对应 X6-SR-05 backlog），但按有界规则不计入本次结论。

---

## 5. Tests / commands NOT_RUN

**Parser、纯内存 selftest、executor、X6 one-shot、freeze manifest 创建、pre-run、git/OS/hash/protected-file/write probe、Build/Cargo、Windows Sandbox、产品 AC1–AC7：全部 NOT_RUN**（与 `TASK:78-83/103-105`、`HANDOFF:76-78`、`SMAN:78-85` 一致）。我本人未执行任何命令（含只读命令），也未编辑任何文件。运行期仍需 Codex 复核：manifest/文件磁盘 SHA 与 `git_blob` 复算（注意 `core.autocrlf` 行尾展开，`PROTO-R2:114`）、Parser 零错误（`PROTO-R2:46-52`）、selftest exit 0 且 SKIP 逐项记录（`PROTO-R2:54-61`）、manifest 路径链与输出链无 reparse/junction、`<RunId>/` 及唯一 `run-<RunId>.json` 在 freeze 时 absent。

---

## 6. 下一步（交 Codex，不新建 Task）

有界 Review r2 **通过**，无 P0/P1/P2 遗留，**不请求再次返修**。Codex 可依 `PROTO-R2:33-42` 直接推进 X6-AC2（运行 protocol r2 §3.1/§3.2 的 Parser 与纯内存 selftest）与 X6-AC4 freeze/pre-run 准备；本次报告对 X6 运行时结果不作任何主张。
