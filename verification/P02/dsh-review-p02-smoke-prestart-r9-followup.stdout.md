已完成只读 exact-head Review。以下为结论。

# P02 R9 follow-up 文档证据修复 — 独立复审（DeepSeek Harness）

## decision
**`CHANGES_REQUESTED`**

R9 Review 的 P3-1/P3-2 就其实质要求已修复并被我独立复算确认；但交付内新增了一处**与本轮修复同类**的证据句柄缺陷（指向未提交日志），另有 2 处证据溯源/措辞精度问题。

## 绑定对象核对（只针对该固定 commit）
| 项 | 值 | 结果 |
|---|---|---|
| `git rev-parse HEAD` | `5fe19efbedf6d46407c92fa7b73897e6794863e2` | ✅ 与固定 Delivery HEAD 一致 |
| `git rev-parse 'HEAD^{tree}'` | `68dfa537a7cb6da99a7e954b6c5f734dd334488d` | ✅ 与固定 Delivery tree 一致 |
| branch / base | `codex/P02-process-isolation`；base=`8b91c8bf032fce3db50bd5a89d5122bf461f0cb2` | ✅ 区间内 1 个 commit，31 路径，全部 `doc/**` + `verification/P02/**`，无产品源码/依赖/契约 |
| tracked 工作区 | `git status --porcelain` 无非 `??` 条目（count=0） | ✅ 结论只对该 commit 成立；untracked 文件（含本 prompt、r9-followup r2/r3/r4 日志）仅作工作区背景，未当作交付内容 |

## finding 计数
**P0=0，P1=0，P2=1，P3=2**

## R9 Review 两项 finding 的关闭判定
- **P3-1 = CLOSED**。`codex-checkpoint-p02-smoke-prestart-r8-candidate.md:8` 仍保留 `4d374260f81ff5868da11a577823b31bb576f6eb8e67414d79235d5f14c679ff`，`:9` 明确其为 R8 commit `6be3dfdb…` 的 checker snapshot 并给出 R9 新值。我从 Git object 独立复算：`6be3dfdb:…check.py` blob → `4d3742…79ff`；`HEAD:…check.py` blob → `1bcbc836b07ba76627816a63206e1dde846201872f6df32d265684abb3020af8`；`r2-manifest-artifact-validation-r6.stdout.log` 与 `r2-manifest-recheck-selftest-r5.stdout.log` 的 `tool_sha256` 均为 `1bcbc8…0af8`。绑定正确。
- **P3-2 = CLOSED（实质）**。`codex-smoke-prestart-manifest-r2-errata.md:3` 与 `codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8` 的 current 引用已统一到 validation r6 / self-test r5，并加注 R8 时点证据说明（措辞问题见 R9F-03）。

## 本轮 findings

**R9F-01 — P2 — 交付内 checkpoint 引用未提交的证据日志，交付内不可复现**
- 路径/行号：`verification/P02/codex-checkpoint-p02-smoke-prestart-r9-followup-candidate.md:8`
- 事实：该行以 `r9-followup-artifact-validation-r2.*`、`r9-followup-selftest-r2.*` 作为 artifact validator 与 synthetic self-test 的证据句柄；但 `git ls-tree -r HEAD -- verification/P02` 中这两个系列**只提交了 `-r1`**（r2/r3 仅存在于工作区、untracked）。同一行引用的 `r9-followup-route-validator-r3.*`、`r9-followup-diff-check-r2.*` 已提交。附带：`:3` 状态边界仍为 `CORRECTION_IN_PROGRESS`，与本文件 `:10`、`doc/tasks/P02.md:94`、`doc/REBASELINE_PLAN.md:9`、`doc/STATUS.md:5` 的“已修复并提交 / pending review”自相矛盾。
- 影响：干净 checkout 中这两条 PASS/EXIT=0 声明无法从交付内验证，与 R8 P2-A（引用未提交 r4/r3 日志）同类，属刚关闭缺陷的同类复发。实质数值无问题：已提交的 `-r1` 两条日志内容与 r2 完全同值（`tool_sha256=1bcbc8…0af8`），我并已实跑复核。
- 最小修复：把 `:8` 的两个句柄改为已提交的 `r9-followup-artifact-validation-r1.*` / `r9-followup-selftest-r1.*`（或补提交 r2 日志），并把 `:3` 状态边界改为交付后状态，重新固定 HEAD/tree 后复审。

**R9F-02 — P3 — 已提交的 “exact-head” route/diff 证据实际产生于被丢弃的非祖先 commit**
- 路径/行号：`verification/P02/r9-followup-route-validator-r3.stdout.log:1`（`live HEAD=8e57687dd8cc59b31374e296ab1f7d705828ade5`）；`verification/P02/r9-followup-diff-check-r2.stderr.log:1-2`（仅 2 个文件处于 dirty 的 pre-amend 状态）；对照 `doc/tasks/P02.md:94`“路线 validator 均已在交付候选上运行”、`doc/REBASELINE_PLAN.md:9`“artifact/route/self-test 验证已完成”。
- 事实：`8e57687d` 与本 commit 同标题、是 amend 前的悬空 commit，**不是 HEAD 的祖先**，其 tree=`1ea5aaf3…` ≠ 交付 tree=`68dfa537…`（差异恰为 INDEX/PLAN/STATUS/P02 正文与 candidate checkpoint 等 5 个文件，即 route validator 所校验的内容）。真正跑在交付 HEAD 上的证据（route validator `live HEAD=5fe19efb…` 7 项 PASS、diff-check 干净）只存在于 untracked 的 `r9-followup-route-validator-r4.*` / `r9-followup-diff-check-r3.*`。
- 影响：交付内无法自证最终文档树通过 route/whitespace 校验（我自行运行的 `verify_plan.py` 在 HEAD 上 7 项 PASS/EXIT=0、`git diff --check base..HEAD`=EXIT=0，故**未发现实际内容缺陷**，仅证据溯源失效）；与 R9 P3-1（证据句柄未绑定当前交付）同族。
- 最小修复：提交并引用最终树运行的 `r9-followup-route-validator-r4.*`、`r9-followup-diff-check-r3.*`；若保留 r3，则在同句显式标注其 `live HEAD=8e57687d…`（amend 前）与交付 HEAD 的差异。

**R9F-03 — P3 — “R5/R4” 简写歧义，重引入 P3-2 想消除的版本混淆**
- 路径/行号：`verification/P02/codex-smoke-prestart-manifest-r2-errata.md:3`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8`
- 事实：两句同时使用 `R6/R5` 与 `R5/R4`；其中 `R5` 在前者指 `r2-manifest-recheck-selftest-r5`（当前证据），在后者指 `r2-manifest-artifact-validation-r5`（R8 时点）。两个系列确实各自存在（validation r5/r6、selftest r4/r5），而 delivery checkpoint 的 “R5/R4 分别是 R8 时点证据” 紧跟在 selftest r5 链接之后，读者可反向读成“当前 self-test r5 是历史证据”。
- 影响：当前/历史证据版本的区分可能被读者反转，削弱 P3-2 修复的意图。
- 最小修复：改用完整文件名（`r2-manifest-artifact-validation-r5` / `r2-manifest-recheck-selftest-r4` 对 `…-r6` / `…-r5`）。

## 自洽性与 Gate 检查
Task/Plan/Status/Index/checkpoint 对 R9 Review `CHANGES_REQUESTED`（`0/0/0/2`）与 follow-up pending 的记录彼此一致；产品 Gate 未被写成 PASS：Stage-1=`PASS`（历史）、Smoke admission=`ADMITTED`（限一次）、Smoke=`NOT_RUN`、完整 preflight=`BLOCKED / INCOMPLETE`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`、HostFolder compare/recheck=`NOT_RUN`。未发现任何 `NOT_RUN/BLOCKED/UNKNOWN → PASS` 的改写。

## 实际运行（均已检查 exit）
- `git rev-parse HEAD`/`HEAD^{tree}`/branch、`git status --porcelain`、`git log`、`git diff --stat`/`--name-only`、`git diff 8b91c8bf..HEAD`、`git show HEAD:<path>`、`git ls-tree -r HEAD`、`git cat-file blob`、`git merge-base --is-ancestor`、`git diff --check 8b91c8bf..HEAD`（EXIT=0）、`git show --check HEAD`
- `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check.py validate` → `PASS`，EXIT=0，`tool_sha256=1bcbc836…0af8`
- `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check-selftest.py` → EXIT=0，`matching=PASS hash/count/status/issue_mismatch=BLOCKED host_scan=NOT_RUN`
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` → `live HEAD=5fe19efb…`，7 项 PASS，EXIT=0
- 仅对 Git object 中的 3 个已提交脚本计算 SHA-256（checker @6be3dfdb/@8b91c8bf/@5fe19efb、self-test），未哈希任何 HostFolder 内容

## 未运行 / 未验证（不写成 PASS）
- 未运行 `recheck` 或任何 scanner；未读取/枚举/扫描/哈希任何实际 HostFolder 内容（`HostFolder compare/recheck=NOT_RUN`）
- 未启动 WSB/Sandbox、guest command、`@oai/sky`、Build、runner/Vitest/GUI/WebView/Cargo 或任何产品测试
- 未独立复现宿主 Stage-1 测量、root manifest 203/203 与 digest、candidate overlap、clone HEAD/tree/porcelain/hardlink/EOL pins、`wsb list` → **NOT_VERIFIED（宿主/运行时限制）**
- 未独立验证“未发生 HostFolder 访问 / 未启动 wsb”这一否定性事实；未复核 R8 其余 finding（P2-B、P3-C..F）及 R9 的宿主类声明，本轮按交付文本采信
- 未读取任何 DSH stderr；未把任何 untracked 文件当作交付内容（untracked 的 r2/r3/r4 日志与 follow-up delivery checkpoint 仅作工作区背景读取）

## 推荐下一步
由 Codex 追加一个纯文档/引用修复 commit：改 `r9-followup-candidate:8` 句柄并同步 `:3` 状态、把 route/diff 证据指向最终树运行日志（并提交 r4/r3）、把 `R5/R4` 简写改为完整文件名；重新固定 HEAD/tree 后派发 DSH R9 follow-up 复审。**在该复审 approved 且只读 HostFolder `recheck`、fresh UI/WSB 预启动检查全部通过前，保持 Hard Build Barrier 有效，不得运行 `wsb start`。**
