# P02-NEW-TIME-X6 执行 Protocol（r1，源码交付版）

- Task：P02-NEW-TIME-X6（P02 新时点 X6 动态闭包与一次性执行）
- Owner：ZCode（session `sess_bd06f60b-b6d1-4cc8-a7e7-4dbcb647458f`）；Reviewer：DeepSeek Harness；Integrator：Codex /root
- 交付 worktree：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6`；branch `agent/zcode/P02-NEW-TIME-X6`
- 生命周期 commit（认领/in_progress）：`83fb737e39ee663b85b14e6fa03168813a8624c6`；源码基线 base commit：`bc502e7aae07074fff7228d585674e87d53efcfd`
- 本文件状态：PROPOSAL-ONLY。本阶段（source delivery r1）未运行任何 parser/selftest/executor；下述命令均为待 Codex 在对应 Gate 通过后运行的精确候选命令。

## 1. 交付物与来源血统

| 文件（仓库相对路径） | 角色 | 来源 |
|---|---|---|
| verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1 | X6 executor（唯一 live 执行体） | 以已审查集成的 baseline collector `tools/p02/p02-new-time-baseline.ps1`（commit d6745a45 集成、bc502e7a pin、SHA-256 `ED1A48393F516934E285B17AE1E7210B3B4C5DADA7B1DD3568A68806E302AF66`）为模式基础定点改绑；未调用、未读取旧 attempt6 executor |
| verification/P02-NEW-TIME-X6/executor/p02-new-time-x6-selftest.ps1 | 纯内存 selftest（Parser AST 提取纯函数；不执行/dot-source 主脚本） | 以 `tools/p02/p02-new-time-baseline-selftest.ps1`（SHA-256 `0E34F959EB564E4BE449AFA89CB774168F3EDB232B6204B37B7B54611744BF0B`）为模式基础定点改绑并新增写保护断言 |

改绑差异（executor）：schema `P02-NEW-TIME-X6-executor-1`、freeze manifest schema `P02-NEW-TIME-X6-freeze-manifest-1`、TaskId、OutputDir、Worktree、ExpectedBranch、BaseCommit（bc502e7a）；self-pin 路径改为本 Task executor 路径；NotRun 表改为 X6 语境（本 run 即唯一 X6 one-shot；post-run Review/Build/Cargo/AC1–AC7/Sandbox 保持 NOT_RUN）；disposition `EXECUTED_X6_DYNAMIC_CLOSURE`；新增 Task X6 禁止写根 `ForbiddenWritePrefixes`（`G:\CODEX\New Manga\verification\P02\`）与纯函数 `Test-PathUnderAnyForbiddenPrefix`（分隔符边界语义：`verification/P02-NEW-TIME-X6/` 不被误伤），在 CreateNew 前对输出目标 fail-closed。

交付字节形态：UTF-8 无 BOM、LF 行尾、无 trailing whitespace。源码不含自身 SHA、不含运行 commit hash（I2：全部经外部 freeze manifest argv 绑定）。

## 2. Gate 顺序（不可越过）

1. **source delivery（本阶段，已完成待验收）**：ZCode 交付 executor/selftest/protocol/manifest/inventory/Handoff，停在 `in_review`。
2. **Codex VERIFY（delivery HEAD）**：核对本 protocol §3 命令、§4 输出目标 absent/unignored、§5 冻结输入、允许路径清单（仅 `verification/P02-NEW-TIME-X6/**` 与 Task 文件）。
3. **DSH bounded source Review**：对精确 delivery HEAD 与 immutable source manifest 独立审查；未解决 P0/P1/P2 不得进入 pre-run。
4. **Codex adjudication + Parser/纯内存 selftest**：运行 §3.1/§3.2；必须零 parser 错误、selftest 全 PASS/已知 SKIP。
5. **Codex freeze**：按 §5 生成 freeze manifest（仓库外），重新固定当时 main HEAD、实际 source/target、身份、argv、CWD、全部 pins。
6. **Codex final pre-run**：只读预检 = `PRE_RUN_PASS` 后才释放执行。
7. **ZCode one-shot X6（至多一次）**：运行 §3.3；失败/partial 原样保留，不重跑。
8. **Codex result VERIFY / integration**，随后才允许释放独立 post-run Review Task。

## 3. 精确候选命令（全部待 Gate 释放后运行）

### 3.1 PowerShell 7.6.6 Parser 零错误检查（Codex，DSH Review 后）

```
pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6/verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1', [ref]$null, [ref]$e) | Out-Null; if ($e.Count) { $e; exit 1 } else { 'PARSER_ZERO_ERRORS'; exit 0 }"
```

（对 selftest 文件同构执行一次；两文件都必须零错误。）

### 3.2 纯内存 selftest（Codex，DSH Review 后；SKIP 项逐项记录）

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

## 4. 候选 RunId 与输出目标清单（全部为候选，未经 Codex freeze 不得创建）

RunId 命名模板：`x6-<YYYYMMDDTHHMM>CST-p02-newtime-r1`（正则 `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` 内）。Owner 提交的具体候选（Codex freeze 时二选一或按模板取当前时戳，须与全部历史 RunId 不冲突）：

- 候选 A：`x6-20261014T1500CST-p02-newtime-r1`
- 候选 B：`x6-20261014T1530CST-p02-newtime-r1`

| 目标（绝对路径） | 创建者/时机 | 性质 |
|---|---|---|
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-<RunId>.json | executor CreateNew（one-shot 时） | 唯一 executor 写目标；目标必须 absent/unignored，禁止复用 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/<RunId>/freeze-manifest.json | Codex freeze（仓库外） | freeze 输入，argv 绑定 SHA-256 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/source-delivery-r1/** | ZCode 本阶段已创建 | 派发提示/命令记录/环境摘要 |
| G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/selftest-r1/** | Codex 运行 §3.2 时 | selftest 原始 stdout/stderr/exit |
| G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/<stamp>-pure-selftest/** | selftest fixture | 保留不清理；不与用户漫画数据混放 |

禁写边界（fail-closed）：executor 拒绝任何命中 `P02PRE-R1H-*` 历史家族段的路径；输出目标不得位于 `G:\CODEX\New Manga\verification\P02\` 旧证据目录（`ForbiddenWritePrefixes`，分隔符边界）；不触碰 `.tmp.driveupload`；不修改主仓 dirty/untracked 用户内容。

## 5. Codex freeze manifest 必含字段（schema `P02-NEW-TIME-X6-freeze-manifest-1`）

沿 baseline freeze 契约（P02-NEW-TIME-X6 executor 的 shape/binding 校验即按此执行）：

- `schema`、`task=P02-NEW-TIME-X6`、`runId`（与 argv 一致）、`deliveryHead`（40-hex，freeze 时实际 HEAD）、`baseCommit=bc502e7aae07074fff7228d585674e87d53efcfd`、`branch=agent/zcode/P02-NEW-TIME-X6`、`cwd`、`worktree`、`outputDir=G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6`、`outputTargets=["run-<RunId>.json"]`
- `identity{name,sid}`（home-my\49745 / S-1-5-21-2196946971-914346751-4210154634-1001）
- `tools{pwshExe,gitExe,whoamiExe}` 与 `expectedRuntime{psVersion=7.6.6,psEdition=Core,languageMode=FullLanguage,gitVersion=git version 2.52.0.windows.1}`
- `contractPins[]`：doc/09_COLLABORATION.md、doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md、doc/templates/TASK.md、doc/templates/HANDOFF.md、doc/templates/REVIEW.md（size+sha256）
- `taskDeliverablePins[]`（size+sha256）：必须含 executor self-pin `verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1`（binding 强制）；建议同时 pin selftest、本 protocol、source-manifest-r1.json 与 Task 快照
- `mutableObservationPaths[]`（只观察不 pin）：主仓 STATUS/REBASELINE_PLAN/00_INDEX/doc/tasks/P02-NEW-TIME-X6.md 与本 checkpoint
- `forbiddenHistorySegments[]`：P02PRE-R1H-H1/H2/P2-1

注意：本 Task worktree 内源码为 LF 磁盘字节交付；Codex freeze 必须在实际执行环境的磁盘字节上取 hash（若 checkout 行尾展开导致与 source-manifest-r1.json 记录不一致，以执行环境磁盘字节重新 pin 并在 freeze 记录差异，不得沿用旧值）。

## 6. 禁止项（本 protocol 全程有效）

不运行旧 attempt6 executor；不写 `verification/P02/**`；不 Build/Cargo/产品 AC1–AC7/Windows Sandbox/capture-getter/profile-registry-ACL 写 API/未冻结子进程；不重跑/清理/回滚/删除任何 RunId 输出；不修改用户源文件、Lock、current/pinned Revision 与主仓 dirty/untracked 内容。
