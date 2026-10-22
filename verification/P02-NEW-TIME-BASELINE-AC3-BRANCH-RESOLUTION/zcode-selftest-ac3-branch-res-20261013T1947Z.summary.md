# P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION selftest 证据（ZCode）

- 证据时间（UTC）：started `2026-10-13T19:47:50Z`（本地 2026-10-14，Asia/Shanghai）
- Task：`doc/tasks/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION.md`（AC1/AC2 行）
- resolution 范围：仅继承 finding `AC3-BRANCH-REF-MISMATCH`（P2）——`git-branch-matches-freeze` 把 `git symbolic-ref --quiet HEAD` 的完整 ref 与 manifest 短分支名直接 `-ceq` 比较导致必定 FAIL；manifest 短分支名契约与 binding 不变
- 被测源：fix commit `b29828e48d848b4dfeab8f8be92948fe43d86971`（collector SHA-256 `F55FB778BBFE5307135A7C7943B587F59DFE94139B4B6138F89DDCED7CD49B90`，SUMMARY-JSON 记录）
- 前序：base/delivery 起点 `210b8bc64e055f93a3b899a8e619b5e02b917cdf`；父 Task I1/I2 断言全部保留；live collector 未运行

## 修复对照（继承 finding 逐项）

| Finding 事实 | 修复 |
|---|---|
| `p02-new-time-baseline.ps1` 中 `$branchRef -ceq $manifestBranch`：完整 ref `refs/heads/<name>` 对短名，当前 AC3 必需检查确定 FAIL，collector 以 exit 5 `BLOCKED_BY_FAILED_CHECKS` 结束 | 提取纯函数 `Test-BranchRefMatchesManifest`：`$BranchRef -ceq "refs/heads/$ManifestBranch"`；`git-branch-matches-freeze` 调用点改为经由该函数。正确分支（完整 ref == refs/heads/ + manifest 短名）PASS；错误分支、非 heads namespace、空 detached-HEAD 输出仍 FAIL（fail-closed 不变） |
| manifest 短分支名契约与 binding | 不变：`Test-FreezeManifestShape`/`Test-FreezeManifestBinding` 对 `branch` 的校验（短名 == 源码结构性基准 `agent/zcode/P02-NEW-TIME-BASELINE`）原样保留；check 的 Expected/ObservedSummary 文案（本来就写 `refs/heads/$manifestBranch`）不变 |

## 实际命令与环境

```
pwsh -NoProfile -File tools/p02/p02-new-time-baseline-selftest.ps1 -Stamp 20261013T1947Z
```

- CWD：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE-AC3-BRANCH-RESOLUTION`
- shell：`C:\Program Files\PowerShell\7\pwsh.exe`；PowerShell 7.6.6 / Core / FullLanguage；OS Microsoft Windows 10.0.26300
- 命令原文：`zcode-selftest-ac3-branch-res-20261013T1947Z.command.txt`；环境记录：`zcode-selftest-ac3-branch-res-20261013T1947Z.env.txt`

## 结果（原始）

| 项目 | 值 |
|---|---|
| OS EXIT | 0（`...exit` 文件内容 `0`） |
| assertsPassed | 212（父 Task i2-r3 为 202 → +10：2 静态 + 7 行为 + 1 函数存在性） |
| assertsFailed | 0 |
| assertsSkipped | 7（与父 Task 相同，全部 Task 禁止范围，不计为 PASS） |
| stderr | 空（0 字节，SHA-256 `E3B0C442...B855`） |
| liveQueriesExecuted / liveCollectorExecuted / gitChildExecuted / historicalInputAccessed | 全部 false（SUMMARY-JSON，revision=`i2-r3+ac3-branch-res`） |
| fixtureDir | `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE/20261013T1947Z-pure-selftest`（保留不删除） |

## 本 resolution 新增断言（10 项，全部 PASS）

静态（collector 源文本）：
- `ast-branch-ref-compare-via-pure-helper` — `git-branch-matches-freeze` 必须经由 `Test-BranchRefMatchesManifest` 比较
- `ast-branch-ref-no-direct-full-vs-short-compare` — 旧的 `$branchRef -ceq $manifestBranch` 直接比较（本次修复的缺陷形态）必须保持不存在

函数存在性（AST 提取列表）：`extract-function-present:Test-BranchRefMatchesManifest`

行为（纯函数正/负例）：
- `branch-ref-full-ref-matches-manifest-short-name` — 正例：`refs/heads/agent/zcode/P02-NEW-TIME-BASELINE` vs 短名 → true
- `branch-ref-wrong-branch-fails-closed` — 负例：hyphen 后缀兄弟分支 → false
- `branch-ref-unrelated-branch-fails-closed` — 负例：`refs/heads/main` → false
- `branch-ref-non-heads-namespace-fails-closed` — 负例：`refs/tags/...` → false
- `branch-ref-bare-short-name-not-a-runtime-ref` — 负例：裸短名不是 symbolic-ref 输出 → false
- `branch-ref-empty-detached-head-fails-closed` — 负例：空输出（detached HEAD）→ false
- `branch-ref-compare-stays-case-sensitive` — 负例：大小写漂移 → false（与 git-head pin 同为大小写敏感）

既有 202 项断言（parser、AST 契约、I1 历史隔离、I2 freeze-manifest seam、失败分类、meta/closed 行工厂、git argv、CreateNew/partial 保留等）语义全部保留、全部 PASS，无回退。

## 逐项 SKIP（未运行，属禁止/未授权范围，不计为 PASS）

1. `live-collector-run` — 禁止运行 live collector；须父 Task 恢复后由 Codex 新建外部 freeze manifest 并重新走父 Task AC3/AC4 Gate。
2. `live-git-child` — 纯自检不启动 git 子进程。
3. `live-whoami-child` — 身份比对留待 live 范围。
4. `live-registry-acl-profile-getter` — 本 Task 范围无任何 registry/ACL/profile API。
5. `executor-dynamic-process-enumeration` — 历史 executor 与进程枚举禁止。
6. `x6-post-run-review-build-cargo-ac-sandbox` — X6、post-run Review、Build/Cargo、产品 AC1–AC7、Windows Sandbox 为后续 Gate，本 Task 未释放。
7. `historical-input-access` — 不读取/改写/补齐任何 H1/P2-1 历史输入、结论、finding 或缺失记录。

## 本轮未运行项（诚实登记）

- live collector / collector output：NOT_RUN（禁止；本 Task 不得运行）。
- DSH bounded Review（AC3）：NOT_RUN（待 Codex 分派，Review head=本 delivery HEAD）。
- Codex 集成 VERIFY / 父 Task AC3/AC4 Gate：NOT_RUN（集成后由 Codex 执行）。
- 上述任何一项均不得被表述为 PASS。
