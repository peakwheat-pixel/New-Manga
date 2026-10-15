# P02-NEW-TIME-X6 执行 Protocol（r2，I1 bounded repair 版）

- Task：P02-NEW-TIME-X6（P02 新时点 X6 动态闭包与一次性执行）
- Owner：ZCode（session `sess_bd06f60b-b6d1-4cc8-a7e7-4dbcb647458f`）；Reviewer：DeepSeek Harness；Integrator：Codex /root
- 交付 worktree：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6`；branch `agent/zcode/P02-NEW-TIME-X6`
- 源码基线 base commit：`bc502e7aae07074fff7228d585674e87d53efcfd`；r1 交付 head：`8b4daf9b0db452cb1b37768f570f04a1e8e589e6`（DSH review r1 + Codex adjudication r1 输入，保留为历史证据）
- 本文件状态：PROPOSAL-ONLY，且为 r1 协议（`x6-execution-protocol-r1.md`，保留原样）的 I1 bounded repair 修订。本阶段未运行任何 parser/selftest/executor；下述命令均为待 Codex 在对应 Gate 通过后运行的精确候选命令。

## 0. r2 相对 r1 的差异（仅限三个经 Codex 确认的 P2 blocker）

按 `codex-source-review-adjudication-r1.md` 的 I1 决定，本 r2 只修复：

1. **X6-SR-01（P2）**：executor 的 index 完整性检查改用 `git rev-parse --absolute-git-dir`（本 linked worktree 私有 gitdir，即 `<主仓>/.git/worktrees/P02-NEW-TIME-X6`）解析被采样 index；不再使用 `--git-common-dir`（链接 worktree 下返回主仓 `.git`，导致采样主仓 index）。检查 ID 更名为 `worktree-git-index-after-unchanged`，Expected/Note 写明被测文件的真实路径语义；非绝对 gitdir 输出 fail-closed（`GIT_ABSOLUTE_DIR_INVALID`）。主仓 index 从不被读或写。
2. **X6-SR-02（P2）**：freeze-manifest 路径判定在读取 manifest 字节前 fail-closed 四层：拒绝 `.`/`..` 段（新纯函数 `Test-PathContainsDotSegment`）；`Test-PathOutsideRepository` 改为多根签名 `-RepositoryRoots`，在 `[IO.Path]::GetFullPath` 词法规范化的绝对路径上同时要求位于 Task worktree 与主仓 `G:/CODEX/New Manga` 之外（主仓历史 `verification/P02/` 树随主仓根一并被拒）；`Test-PathAncestorsOrdinary` 拒绝 manifest 路径链中任何 reparse/junction；历史段隔离与 `ForbiddenWritePrefixes` 保持不变。规范化失败、相对路径或空根列表一律 fail-closed。
3. **X6-SR-03（P2）**：`output-target-inventory-r2.json` 显式授权 `<RunId>/` 为冻结 raw-capture 根，逐文件列出 `command.md`/`stdout.md`/`stderr.md`/`exit.md`/`environment.md`/`session.md` 六项必需原始记录的写入者、创建时点、freeze 时必须 absent 的前提与 partial/failure 保留规则；明确 `freeze-manifest.json` 不自动授权同目录任何其它文件。

P3/P4（X6-SR-04..13）按裁决仅列 backlog，本 r2 不修。

## 1. 交付物与来源血统（r2）

| 文件（仓库相对路径） | 角色 | 相对 r1 的变化 |
|---|---|---|
| verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1 | X6 executor（唯一 live 执行体） | 原路径定点修复 X6-SR-01/02（见 §0）；r1 字节由 delivery commit 8b4daf9b 与 `dsh-source-review-input-manifest-r1.json` 的 pin 保留 |
| verification/P02-NEW-TIME-X6/executor/p02-new-time-x6-selftest.ps1 | 纯内存 selftest | 新增 `Test-PathContainsDotSegment` 提取与 X6-SR-01/02 直接相关的静态与纯函数断言；替换 `Test-PathOutsideRepository` 旧签名单根断言为双根边界断言集 |
| verification/P02-NEW-TIME-X6/protocol/x6-execution-protocol-r2.md | 本文件 | r1 协议保留原样；r2 新文件 |
| verification/P02-NEW-TIME-X6/output-target-inventory-r2.json | 输出目标清单 r2 | r1 清单保留原样；r2 显式授权 `<RunId>/` raw-capture（X6-SR-03） |
| verification/P02-NEW-TIME-X6/source-manifest-r2.json | 交付源码 hash 清单 r2 | r1 manifest 保留原样；r2 pin 上述文件的 I1 修复后字节 |

改绑差异（executor 相对 r1）：gitdir 观测 `git-absolute-git-dir`；index 路径 `Require IsPathRooted` 后 `Join-Path <gitdir> index`；freeze gate 新增 dot-segment Require、双根 Require 与 manifest 路径链 reparse 检查；其余（schema、freeze-manifest 契约、唯一 CreateNew、fail-closed 顺序、NotRun 表、disposition）与 r1 审查版一致。

交付字节形态：UTF-8 无 BOM、LF 行尾、无 trailing whitespace。源码不含自身 SHA、不含运行 commit hash（I2：全部经外部 freeze manifest argv 绑定）。

## 2. Gate 顺序（不可越过）

1. **source delivery r2（本阶段，I1 repair）**：ZCode 交付修复后的 executor/selftest 与 protocol/inventory/source-manifest r2，停在 `in_review`。
2. **Codex deterministic VERIFY（delivery HEAD）**：核对本 protocol §3 命令、§4 输出目标 absent/unignored、§5 冻结输入、允许路径清单（仅 `verification/P02-NEW-TIME-X6/**` 与 Task 文件/Handoff），并冻结 r2 source manifest 作为 bounded Review 输入。
3. **DSH bounded source Review r2**：检查 X6-SR-01/02/03 是否关闭、是否引入新 P0/P1/P2、原 AC 是否仍满足、是否引入安全/数据损坏/不可逆风险；对精确 r2 delivery HEAD 与 immutable input manifest 独立审查。
4. **Codex adjudication + Parser/纯内存 selftest**：运行 §3.1/§3.2；必须零 parser 错误、selftest 全 PASS/已知 SKIP。
5. **Codex freeze**：按 §5 生成 freeze manifest（Task worktree 与主仓之外），重新固定当时 main HEAD、实际 source/target、身份、argv、CWD、全部 pins。
6. **Codex final pre-run**：只读预检 = `PRE_RUN_PASS` 后才释放执行。
7. **ZCode one-shot X6（至多一次）**：运行 §3.3 并按 §4 raw-capture 授权同步产出 `<RunId>/` 六项原始记录；失败/partial 原样保留，不重跑。
8. **Codex result VERIFY / integration**，随后才允许释放独立 post-run Review Task。

## 3. 精确候选命令（全部待 Gate 释放后运行）

### 3.1 PowerShell 7.6.6 Parser 零错误检查（Codex，DSH Review r2 后）

```
pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6/verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1', [ref]$null, [ref]$e) | Out-Null; if ($e.Count) { $e; exit 1 } else { 'PARSER_ZERO_ERRORS'; exit 0 }"
```

（对 selftest 文件同构执行一次；两文件都必须零错误。）

### 3.2 纯内存 selftest（Codex，DSH Review r2 后；SKIP 项逐项记录）

```
CWD: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6
pwsh -NoProfile -File verification/P02-NEW-TIME-X6/executor/p02-new-time-x6-selftest.ps1
```

预期：exit 0；stdout 人读日志 + SUMMARY-JSON 一行；fixture 写入 `G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/<stamp>-pure-selftest/`（保留不清理）；live 项全部 SKIP 不计 PASS。原始 stdout/stderr/exit 写入 `agent-output/zcode/P02-NEW-TIME-X6/selftest-r1/`。

### 3.3 X6 one-shot（ZCode，仅在 final pre-run=PRE_RUN_PASS 后，至多一次）

```
CWD: G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6
pwsh -NoProfile -File verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1 \
  -RunId <frozen RunId> \
  -FreezeManifestPath "G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/<RunId>/freeze-manifest.json" \
  -FreezeManifestSha256 <64-hex of the manifest bytes, frozen by Codex>
```

预期：exit 0 = 全部 checks PASS；输出唯一 CreateNew NDJSON `run-<RunId>.json`（meta/observation/closed 行，closed 自包含）。exit 2/3/4/5/6 = 对应 BLOCKED_* fail-closed；失败与 partial 输出原样保留，同一 RunId 永不重试。

### 3.4 X6 one-shot 的 raw capture（ZCode，与 §3.3 同一 RunId，逐项对应 X6-AC5）

按 `output-target-inventory-r2.json` 的 `rawCaptureAuthorization`，在 `<RunId>/` 内由 ZCode operator session 产出六项必需原始记录：`command.md`（启动前写：完整 argv、executor 路径、RunId、FreezeManifestPath、FreezeManifestSha256、CWD、启动 UTC）、`environment.md`（启动前写：shell/解释器版本、身份、相关 GIT_* 环境缺失）、`session.md`（启动前写：session/派发标识）、`stdout.md` 与 `stderr.md`（进程退出后落盘的原始流）、`exit.md`（退出后写：OS exit code 与观测 UTC）。任何 outcome（含非零 fail-closed）都保留已写子集；缺失部分在 Handoff 记为 absent，绝不以同 RunId 补写。

## 4. 候选 RunId 与输出目标清单（全部为候选，未经 Codex freeze 不得创建）

RunId 命名模板：`x6-<YYYYMMDDTHHMM>CST-p02-newtime-r1`（正则 `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` 内）。Owner 提交的具体候选（Codex freeze 时二选一或按模板取当前时戳，须与全部历史 RunId 不冲突）：

- 候选 A：`x6-20261014T1500CST-p02-newtime-r1`
- 候选 B：`x6-20261014T1530CST-p02-newtime-r1`

| 目标（绝对路径） | 创建者/时机 | 性质 |
|---|---|---|
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-<RunId>.json | executor CreateNew（one-shot 时） | 唯一 executor 写目标；目标必须 absent/unignored，禁止复用 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/<RunId>/ | Codex freeze（目录 + manifest）；ZCode（六项 raw capture） | 冻结 raw-capture 根（X6-SR-03）；freeze 前整目录 absent；仅含 manifest 与六个显式授权文件 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/<RunId>/freeze-manifest.json | Codex freeze（worktree 与主仓之外） | freeze 输入，argv 绑定 SHA-256；不授权任何同目录其它文件 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/<RunId>/{command,environment,session}.md | ZCode（one-shot 启动前） | 必需 raw capture（X6-AC5）；freeze 时 absent；任何 outcome 保留 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/<RunId>/{stdout,stderr,exit}.md | ZCode（one-shot 进程退出后） | 必需 raw capture（X6-AC5）；partial 原样保留，绝不重试 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/source-delivery-r1/** | ZCode r1 阶段已创建 | 派发提示/命令记录/环境摘要（历史输入，不触碰） |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/source-delivery-r2/** | 未创建（I1 派发仅授权 repo 内三个写入路径；本轮 raw 命令记录保留于 ZCode owner session 证据） | 如后续派发授权 agent-output 写入再创建 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/selftest-r1/** | Codex 运行 §3.2 时 | selftest 原始 stdout/stderr/exit |
| G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/<stamp>-pure-selftest/** | selftest fixture | 保留不清理；不与用户漫画数据混放 |

freeze-manifest 位置规则（X6-SR-02 后由 executor 强制）：路径不得含 `.`/`..` 段；词法规范化后必须位于 Task worktree 与主仓 `G:/CODEX/New Manga` 之外；路径链不得含 reparse/junction；历史段隔离不变。

禁写边界（fail-closed）：executor 拒绝任何命中 `P02PRE-R1H-*` 历史家族段的路径；输出目标不得位于 `G:\CODEX\New Manga\verification\P02\` 旧证据目录（`ForbiddenWritePrefixes`，分隔符边界）；不触碰 `.tmp.driveupload`；不修改主仓 dirty/untracked 用户内容。

## 5. Codex freeze manifest 必含字段（schema `P02-NEW-TIME-X6-freeze-manifest-1`，r2 无契约变化）

沿 baseline freeze 契约（P02-NEW-TIME-X6 executor 的 shape/binding 校验即按此执行）：

- `schema`、`task=P02-NEW-TIME-X6`、`runId`（与 argv 一致）、`deliveryHead`（40-hex，freeze 时实际 HEAD，即 r2 delivery head）、`baseCommit=bc502e7aae07074fff7228d585674e87d53efcfd`、`branch=agent/zcode/P02-NEW-TIME-X6`、`cwd`、`worktree`、`outputDir=G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6`、`outputTargets=["run-<RunId>.json"]`
- `identity{name,sid}`（home-my\49745 / S-1-5-21-2196946971-914346751-4210154634-1001）
- `tools{pwshExe,gitExe,whoamiExe}` 与 `expectedRuntime{psVersion=7.6.6,psEdition=Core,languageMode=FullLanguage,gitVersion=git version 2.52.0.windows.1}`
- `contractPins[]`：doc/09_COLLABORATION.md、doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md、doc/templates/TASK.md、doc/templates/HANDOFF.md、doc/templates/REVIEW.md（size+sha256）
- `taskDeliverablePins[]`（size+sha256）：必须含 executor self-pin `verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1`（binding 强制）；建议同时 pin selftest、本 protocol r2、source-manifest-r2.json 与 Task 快照
- `mutableObservationPaths[]`（只观察不 pin）：主仓 STATUS/REBASELINE_PLAN/00_INDEX/doc/tasks/P02-NEW-TIME-X6.md 与本 checkpoint
- `forbiddenHistorySegments[]`：P02PRE-R1H-H1/H2/P2-1（executor 以源码常量固定执行隔离；该 manifest 字段被记录但不参与 executor 判定——见 r1 review backlog X6-SR-07，非本次范围）

注意：本 Task worktree 内源码为 LF 磁盘字节交付；Codex freeze 必须在实际执行环境的磁盘字节上取 hash（若 checkout 行尾展开导致与 source-manifest-r2.json 记录不一致，以执行环境磁盘字节重新 pin 并在 freeze 记录差异，不得沿用旧值）。

## 6. 禁止项（本 protocol 全程有效）

不运行旧 attempt6 executor；不写 `verification/P02/**`；不 Build/Cargo/产品 AC1–AC7/Windows Sandbox/capture-getter/profile-registry-ACL 写 API/未冻结子进程；不重跑/清理/回滚/删除任何 RunId 输出；不修改用户源文件、Lock、current/pinned Revision 与主仓 dirty/untracked 内容。
