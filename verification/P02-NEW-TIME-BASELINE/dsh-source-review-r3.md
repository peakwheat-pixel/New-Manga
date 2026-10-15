我已完成全部只读审查。说明一处环境事实：本会话 shell 在启动前即失败（DSH 无法为工作区根授予写权限，Windows 报「拒绝访问」，且无审批通道），因此工作区写入的授权命令不可用；但 `read`/`glob`/`grep` 只读工具正常，审查已基于**直接读取磁盘上的实际文件**完成，仅“独立重算哈希/git 核验”两项受限。

---

# P02-NEW-TIME-BASELINE — Parent Exact-Source Review（delivery HEAD `318bc2a1`）

## 0. 固定输入与核验状态

| 项 | 值 |
|---|---|
| Task ID | `P02-NEW-TIME-BASELINE` |
| `delivery_head` | `318bc2a1d8ff33e82585f4fa835a9370fad73a4a` |
| Task contract snapshot | `d285908f07ae1aa37a3e3af077d5902bb9abe661`（仅用于范围/验收契约） |
| 待审源码绑定 | 源码 blobs 在 `d285908f` 与 `318bc2a1` 一致（见 §2 AC2 绑定链） |
| Evidence manifest | `verification/P02-NEW-TIME-BASELINE/dsh-source-review-manifest-r3.json` |
| Manifest SHA-256（任务给定） | `5B18C9B56E5BCAA3822290C7C78031A34C9EB23EA004321BF0840100709AB87D` |
| Manifest 验证状态 | `dsh-source-review-manifest-r3-verify.json` = `PASS`，`files_checked: 3`，`problems: []` |
| 已知边界 | `codex-source-verify-r3.json` 记录的同一 manifest hash 与 `0x…` 验证记录与任务给定值一致 |
| 审查范围 | 仅本 Task 合约 + `tools/p02/p02-new-time-baseline.ps1`（1855 行）、`tools/p02/p02-new-time-baseline-selftest.ps1`（871 行） |

**未独立重算的部分**：manifest SHA-256、两个源文件的 SHA-256 与 git blob 均为**未由本 Review 独立重算**（shell 不可用，且不得执行 Git 子进程）。上述绑定依赖 Codex 生成器 `frozen_git_checked: true` + verify `PASS (3/3)` + `codex-source-verify-r3.json`，不冒充我的独立复算。

---

## 1. 结论摘要

- 源码侧**无 P0 / P1 / P2**。
- Git top-level 路径比较修复**正确、最小、且未放宽任何其他路径边界**。
- Source gate 结论：**APPROVED**（仅 source gate；不代表 AC2 由我单方关闭，更不代表 AC3 / X6 / 后续 Gate 释放）。

---

## 2. 逐 AC 源代码审查结论

### AC1（Task 标 `[x]`）— 源侧一致，与既有 deterministic 证据吻合
- **7 项 SKIP 精确存在**：selftest 行 113–119 共 7 项 `Add-Skip`，与 AC1 的“7 项 skip 原因逐项保留”一致。`Add-Skip` 只记录、不触碰 `AssertsPassed`，故 SKIP 不计 PASS（行 71–92、860–871）。
- **静态计数复核 234**：`Assert-True` 调用点 153 处（不含 `Assert-Throws` 内部第 85 行）；其中 6 处位于 `foreach`（行 210/220/277/299/350/585，执行次数 25/3/6/2/33/7 = 76 次）；`Assert-Throws` 11 处各产生 1 次断言。即 `153 − 6 + 76 + 11 = 234`，与 AC1 记录的 `234 PASS / 0 FAIL / 7 SKIP / EXIT=0` **精确吻合**。
- **新增 14 项断言分解**：11 项 `Test-GitToplevelMatchesWorktree` 纯断言（行 758–778）+ 2 项静态 AST 断言（行 245、246）+ 1 项函数抽取断言（行 151 将新 helper 加入 `requiredFunctions`，由行 350 循环产生）。
- **证据绑定**：`codex-post-resolution-selftest-r1.meta.json` → `tested_head = 318bc2a1…`、`source_hashes` 与 r3 manifest 逐字节一致、`234/0/7`、`exit_code 0`、`stderr_bytes 0`、`live_collector_executed: false`。
- **限定成立**：AC1 自述“此项不证明 live baseline 通过”，与源码一致（selftest 从不执行 collector 的 param/preflight/main 序列，仅从 AST 抽取函数定义，见行 343–354）。
- 本 Review **未重跑**该自检（禁止执行自检；且 shell 不可用），因此 AC1 记为“源侧一致 + 与既有 deterministic 证据吻合”，不记为“我执行验证”。

### AC2（Task 标 `[ ]`，即本次待办项）— 源侧满足
- 本次 Review 正是 AC2 缺口中的 “DSH exact-source Review” 一半。另一半 `codex-source-verify-r3.json` = `PASS`，其 `ac2_overall` 明确为 `PENDING_DSH_EXACT_SOURCE_REVIEW`。
- **绑定链（三处独立记录一致）**：
  - r3 manifest：`review_head = 318bc2a1`、`source_commit = d285908f`；collector blob `63083329…`、selftest blob `519a48c7…`。
  - `codex-parent-integration-r1.json`：`changed_paths` 恰为两个允许源文件，`source_sha256` 与 manifest 相同。
  - `codex-source-verify-r3.json`：两文件 `resolution_75c = current_d285 = integration_318` 的 blob 完全相同，`changed_paths_in_delivery` 仅两个脚本。
- **历史 Review 不替代**：旧 source Review `50c60755` 与 resolution bounded Review `75c5cc4f` 仅作历史/子范围依据，本 Review 对 `318bc2a1` 独立成立。
- AC2 的最终关闭属 Codex 裁决范围，本 Review 不自封完成。

### AC3（Task 标 `[ ]`）— **未通过，本 Review 不释放**
- 源码侧：路径比较修复已集成于 `318bc2a1` 且实现正确（§3）；但父 Task **未重新 freeze、未使用 never-before-used RunId、未执行 collector**。
- `baseline-20261014T064250-CST-new2` 仍为 closed `FAILED_STOPPED`、36/37 PASS、唯一 `FAIL=git-toplevel-matches-worktree`、exit 5，原失败记录未被改写。
- **明确不把尚未运行的 AC3 标为通过**，也不据此释放 X6。

### AC4（`[x]`）/ AC6（`[x]`）— 本次不改动其结论
- AC4 仅证明旧失败结果被完整记录与正确处置；AC6 为配额/收敛事实。两者不因本次源码变更而改变，本 Review 不复核、不重开，也不用于替代 AC3。

### AC5（`[ ]`）/ AC7（`[ ]`）— 超出 source gate
- AC5 为 Codex 最终裁决（ADMIT_X6 / BLOCK_X6）；AC7 为集成与 closeout。均不在本 Review 结论范围。

---

## 3. 重点核验：新 Git top-level 路径比较

被审实现（`p02-new-time-baseline.ps1` 行 830–842，调用点行 1620–1628）：

```powershell
$t = ($Toplevel -replace '/', '\').TrimEnd('\')
$w = ($Worktree  -replace '/', '\').TrimEnd('\')
return ($t -ieq $w)
```

| 核验点 | 结论 | 依据 |
|---|---|---|
| 两侧 path separator normalization | **正确**：先统一 `/`→`\`，再 `TrimEnd('\')`，两侧对称 | 行 839–840；对比旧缺陷形态为单边归一化（仅归一化 manifest 侧） |
| Windows 大小写不敏感比较 | **正确**：`-ieq`，与 NTFS 语义一致；且输出卷已被 `driveFormat -ceq 'NTFS'` 约束（行 1478） | 行 841、1478；selftest 行 764 |
| 尾分隔符容忍 | **正确**：`G:…\BASELINE\` 与 `G:…\BASELINE` 视为同一目录 | selftest 行 766 |
| 空输入 fail-closed | **正确**：任一侧 `IsNullOrWhiteSpace` → `$false` | 行 838；selftest 行 778 |
| 精确相等而非前缀包含 | **正确**：使用 `-ieq` 相等，不用 `StartsWith`，故子目录/父目录/同叶子不同父目录/**连字符兄弟目录**全部 fail-closed | selftest 行 770–777 |
| 跨卷失败 | **正确**：不同盘符字符串不等 → `FAIL` → `BLOCKED_BY_FAILED_CHECKS` | selftest 行 768 |
| 调用点唯一 | **正确**：全文件仅行 1622 一处调用，无旁路比较 | `grep` 全量命中确认 |
| 旧单边比较确已移除 | **正确**：`$toplevel -ieq ($manifestWorktree` 在 collector 中零命中（仅存在于 selftest 注释与断言文本，且断言扫描的是 collector 文本，不会自匹配） | 行 246 断言 + grep |
| 是否放宽其他路径边界 | **未放宽**（逐项复核） | 见下 |

**其他路径边界逐项复核（均未被本次修复改动或放宽）**：
- `Test-PathOutsideRepository`（行 558–568）：同样两侧归一化 + 精确 `-ieq` + `StartsWith(…, OrdinalIgnoreCase)` 前缀排除，语义保持严格（worktree 根本身也被拒绝，selftest 行 633）。
- `Test-PathContainsHistorySegment`（行 479–506）：按 `\` 分段，段精确 `-ieq` 或“族名 + `-` 分隔符”前缀；**不使用任意子串包含**，`H2X` / `H2COLLECTOR` 不匹配（selftest 行 504–505 反向断言）。history-isolation 在**任何文件/进程 API 之前**对完整冻结路径集 fail-closed（行 1459–1468）。
- `Test-BranchRefMatchesManifest`（行 821–828）：仍是**大小写敏感** `-ceq`（Git ref 语义正确）；本次的分隔符/大小写放宽**没有**错误地扩散到分支比较（selftest 行 745 反向断言）。
- CWD 冻结检查（行 1472、1709）：单边归一化 `$manifestCwd -replace '/','\'`；因 `[IO.Directory]::GetCurrentDirectory()` 在 Windows 上必返回反斜杠形式，此单边归一化充分；manifest 侧若带尾分隔符只会**更严**（fail-closed）。
- 纵深防御：即便 toplevel 检查本身有偏差，`Test-FreezeManifestBinding`（行 739–742）也强制 manifest 的 `worktree`/`outputDir` 等于源码侧冻结基线，wrong-checkout 仍会被拦截。

**残留边界说明（不构成放宽）**：`TrimEnd('\')` 在“盘根”退化输入下会把 `G:\` 归一为 `G:`，从而与 `G:` 相等。该输入对本 Task 不可达——冻结 worktree 是深层固定路径且被 binding 钉死；已列入 backlog（BL-1），非 blocker。

---

## 4. Findings 表

**无 P0 / P1 / P2。** 以下仅为 backlog，不触发返修，也不改变 source gate 结论。

| ID | 级别 | 源码位置 | 证据 | 是否 blocker |
|---|---|---|---|---|
| BL-1 | P4 | `p02-new-time-baseline.ps1` 行 839–840 | `TrimEnd('\')` 使盘根退化输入 `G:\` 与 `G:` 相等；对本 Task 固定深层 worktree 不可达（且受行 739–742 binding 约束） | 否（backlog） |
| BL-2 | P4 | 行 1600–1633 的 `.stdout.text.Trim()` 家族（含行 1621 `$toplevel`） | git 子进程 exit 0 但 stdout 非合法 UTF-8 时 `.text` 为 `$null`，`.Trim()` 抛异常 → 外层 catch → exit 6 `BLOCKED_EXCEPTION_FAIL_CLOSED`。方向仍是 fail-closed，但以“异常类”而非“check FAIL”呈现 | 否（backlog） |
| BL-3 | P4 | 行 1677–1696 | check id/Expected 提到 “unignored”，但 `Result` 仅由 `OutputPreflight.targetAbsent` 决定；`insideRepository` 用 `String.StartsWith`（当前区域性、大小写敏感）且从不参与判定。因 `outputDir` 被 binding 钉死为仓库外固定路径，该分支不可达 | 否（backlog） |
| BL-4 | P4 | 行 815–819（定义）；selftest 行 722–723（断言） | `New-CheckIgnoreArgv` 已定义并被自检，但在 collector 主序列中从未被调用（unused helper） | 否（backlog） |

（上述条目为本 Review 独立观察；若与既有 resolution backlog 条目重合，不影响级别与结论。）

---

## 5. 安全 / 数据完整性 / 不可逆执行风险

- **不可逆执行风险：未发现新增。** 写通道仍唯一且为 `CreateNew + FileShare.None`（行 1054–1060、1481）；`[IO.FileMode]` 仅 `CreateNew`、`[IO.FileShare]` 仅 `None`（selftest 行 184–187 静态断言）；无 overwrite / retry / delete / `File.Replace`（行 1850–1853 仅 `Dispose`；selftest 行 339 断言 finally 只 dispose）。
- **目标冲突已 fail-closed 两次**：行 1471 `Require (-not [IO.File]::Exists($outputFile))` + 行 1532 `targetAbsent` 参与 `output-path-chain-volume`；且 CreateNew 自身拒绝同 RunId 复用（selftest 行 791–796 验证既有字节不被破坏）。
- **部分证据保留**：每行即时 `WriteLine + Flush`（行 1177–1182），失败 partial 文件不删除不重写（selftest 行 815–839）。
- **数据完整性**：冻结契约/deliverable pin 在采集前后各校验一次（行 1717–1755、1785–1811），`.git/index` 前后哈希比对（行 1757–1829），任何漂移 → `FAIL` → exit 5。
- **历史隔离**：在**任何文件/进程 API 之前**以纯字符串完成，未知项一律 fail-closed（行 1417–1468）；本次未读写任何 H1/P2-1 历史输入、结论、OPEN finding 或 13 项缺失记录，也未把本时点表述为“补齐/替代”。
- **禁止 API**：无 profile/registry/ACL 写 API、无动态进程枚举、无 `Invoke-Expression`/`Start-Process`（selftest 行 162–196、180–182）。
- **残余环境风险（非源码缺陷）**：preflight 记录 worktree 存在 `1 dirty entries`。我无法在不执行 git 的情况下确定其具体路径；两个源文件的哈希已被三处独立 Codex 记录一致钉住，但**该 dirty 条目的身份建议由 Codex 在 AC2 收口时确认**。

---

## 6. 未运行检查、能力限制

**未运行（本次 Review 一律未执行，也不据本 Review 放行）**：
- collector 任何一次 live 采集；未生成新 RunId；未 freeze。
- X6、post-run Review、Build/Cargo、产品 AC1–AC7、Windows Sandbox —— 全部 NOT_RUN / 未释放。
- 自检未重跑、`whoami`/Git 子进程未执行、无 live query。
- 未修改任何文件（含被审源码、Task、evidence、STATUS/Plan/index/checkpoint）。

**能力限制**：
1. **shell 完全不可用**：DSH 无法为工作区根 `G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE` 授予本会话用户写权限（Windows 返回「拒绝访问」），因此 `pwsh` 在命令启动前即失败；尝试更宽权限重试时**无审批通道可用**，按 fail-closed 停止，未做任何权限变更、无回滚。
   - 影响：**无法独立重算** manifest/源文件 SHA-256，**无法独立读取** manifest 之后的文件字节指纹校验；`git` 未运行（亦符合本任务禁止项），故 `dirty entries` 未能定性。审查主体（源码逻辑、范围、边界）不受影响，因为文件是**直接从磁盘读取**的。
   - 若需恢复 shell：把本会话临时切到**完全权限 (full access)**；或允许运行一次工作区文件权限诊断修复命令（仅修复权限、不改文件内容、不改变所有者）。
2. **manifest 绑定结论属 Codex 记录**：`PASS (3/3)`、`frozen_git_checked: true` 及三处 blob 一致性由 `codex-source-verify-r3.json` / `codex-parent-integration-r1.json` 提供，非我独立复算；我已交叉比对三者与 r3 manifest 逐字段一致。
3. 文件字节大小（99513 / 76312）未独立核对（仅有 manifest 声明）。

---

## 7. 结论（仅限 source gate）

**APPROVED**

- 对 `delivery_head = 318bc2a1d8ff33e82585f4fa835a9370fad73a4a` 的两个允许源文件，parent exact-source Review **无 P0/P1/P2**，无 CHANGES_REQUESTED 项，P3/P4 仅入 backlog 且不开返修。
- Git top-level 路径比较修复**满足**“两侧 path separator normalization + Windows 大小写不敏感比较”，并且**未放宽**其他路径边界（历史隔离、仓库外放置、分支 ref 大小写敏感、CWD、输出目标 absent）。
- **本结论不释放任何下游 Gate**：AC3 仍为**未通过（NOT_RUN / NOT_VERIFIED）**，X6 → post-run Review → Build/Cargo → AC1–AC7 保持 BLOCKED；AC2 的 DSH 半边由本 Review 补齐，但最终关闭属 Codex；AC5/AC7 不在本 gate 范围。
- 唯一需 Codex 在 AC2 收口时确认的事项：worktree 那 1 个 dirty 条目的路径身份；以及本会话 shell/权限不可用的环境事实是否需要修复（不影响上述源码判断）。

**推荐下一步**：由 Codex 以本 Review 作为 AC2 的 exact-source 输入，完成 manifest/source VERIFY 的 AC2 收口与 front-matter 更新；随后**另起** fresh freeze（manifest 外置于仓库、argv 绑定 SHA-256）并分配 **never-before-used RunId** 以重新尝试 AC3 的一次 collector —— 本 Review 不作为 AC3 的任何证据。
