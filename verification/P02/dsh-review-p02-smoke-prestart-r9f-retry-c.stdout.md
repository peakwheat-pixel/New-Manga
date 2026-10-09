# P02 R9F exact-head Review（DeepSeek Harness，非作者 Reviewer）

## decision

**`APPROVED`**

绑定对象唯一：`d90dd8f1d44dd022314bb63a305b013dcadb6a44` / tree `ad67989bee362c29fdedaa0fb44bf4864de693c7`，detached、clean、parent=`5fe19efbedf6d46407c92fa7b73897e6794863e2`。R9F-01/02/03 全部关闭，无 open finding。

## 绑定与 scope 核对

| 项 | 值 | 结果 |
|---|---|---|
| `git rev-parse HEAD` | `d90dd8f1d44dd022314bb63a305b013dcadb6a44` | ✅ |
| `git show -s --format=%T HEAD` | `ad67989bee362c29fdedaa0fb44bf4864de693c7` | ✅ |
| `git status --porcelain` | 空（tracked/untracked 均 0 行） | ✅ clean |
| `git rev-list --parents -n 1 HEAD` | parent=`5fe19efbedf6d46407c92fa7b73897e6794863e2` | ✅ |
| diff scope | 33 files（+158/−18），全部 `doc/**` + `verification/P02/**` | ✅ 无产品源码/依赖/契约 |
| candidate worktree | HEAD/tree 同值；仅 untracked 历史日志 | ✅ 未当作交付内容 |

## finding 计数

**P0=0，P1=0，P2=0，P3=0**

## 三项返修判定

**R9F-01（原 P2）→ CLOSED**
- 位置：`verification/P02/codex-checkpoint-p02-smoke-prestart-r9-followup-candidate.md:3,8`；`verification/P02/codex-checkpoint-p02-smoke-prestart-r9-followup-delivery.md:3,7`；`verification/P02/codex-checkpoint-p02-smoke-prestart-r9f-candidate.md:3,8`
- 证据：artifact/self-test 句柄已改为 commit 内实际提交的完整文件名——`r9-followup-artifact-validation-r3.{stdout.log,exit}`、`r9-followup-selftest-r3.{stdout.log,exit}`（`git ls-tree -r HEAD` 命中，exit 均 `0`）；状态边界改为 `DELIVERED / REVIEW_PENDING`，与 `r9-followup-review.md:3`（`REVIEW_CHANGES_REQUESTED`，历史时点）及 Task/Plan/Status/Index 的“已修复 / pending”表述一致，`CORRECTION_IN_PROGRESS` 矛盾已消除。
- 补充独立复算：`HEAD:…manifest-check.py` blob SHA-256=`1bcbc836…0af8`，与 `r2-manifest-artifact-validation-r6.stdout.log` / `r2-manifest-recheck-selftest-r5.stdout.log` 的 `tool_sha256` 完全一致；`6be3dfdb:…manifest-check.py` blob=`4d374260…79ff`，与 R8 历史 hash 声明一致。本 commit 新增行 46 个本地引用链接全部可解析（missing=0）。

**R9F-02（原 P3）→ CLOSED**
- 位置：`doc/tasks/P02.md:95`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r9-followup-candidate.md:8`、`r9-followup-delivery.md:7`
- 证据：route/diff 证据现指向 `r9-followup-route-validator-r4.stdout.log`（`live HEAD=5fe19efbedf6d46407c92fa7b73897e6794863e2`，7 项 PASS，exit=`0`）与 `r9-followup-diff-check-r3`（stdout 空、exit=`0`）；`5fe19efb` 经 `git merge-base --is-ancestor` 确认为 HEAD 祖先（exit 0），而 amend 前的 `8e57687d` 明确为非祖先（exit 1），且不再有任何当前状态文档以它作为交付证据。独立复算：`git diff 5fe19efb^ 5fe19efb --check`=$`EXIT 0`，与提交日志一致。P02:95 正确标注为 “Precommit route validator 与 diff check=`EXIT=0`”，`r9f-candidate.md:8` 亦显式声明其非 R9F post-commit exact-head 证据，未越权声称。

**R9F-03（原 P3）→ CLOSED**
- 位置：`verification/P02/codex-smoke-prestart-manifest-r2-errata.md:3`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8`
- 证据：两处当前引用均为完整文件名 `r2-manifest-artifact-validation-r6` / `r2-manifest-recheck-selftest-r5`，早期证据显式写作 `artifact-validation-r5` / `self-test-r4`；`git grep -E "R5/R4|R6/R5"` 在这两个文件中**无命中**（exit 1）。残留的 `R5/R4` 仅出现在 R8/R9/F 历史 Review 报告的 finding 叙述中，不再作为当前证据简称。

## 一致性与 Gate 检查

- Task `:90-95`、Plan `:7,:9`、Status `:5,:9,:11`、Index `:3`、4 个 checkpoint 对 “R9 follow-up Review=`CHANGES_REQUESTED`（`0/0/1/2`）@ `5fe19efb` / tree `68dfa537…`；P3-1/P3-2 CLOSED；R9F-01/02/03 已修复；R9F exact-head Review pending” 表述彼此自洽。
- 产品 Gate 未被写成 PASS：Stage-1=`PASS`（均显式标“历史”）、Smoke admission=`ADMITTED`（限一次）、Smoke=`NOT_RUN`、完整 preflight=`BLOCKED / INCOMPLETE`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`、HostFolder compare/recheck=`NOT_RUN`。未发现任何 `NOT_RUN/BLOCKED/UNKNOWN → PASS` 改写。

## 实际执行命令与 exit code

| 命令 | 结果 / exit |
|---|---|
| `git rev-parse HEAD` / `git show -s --format=%T HEAD` / `git status --porcelain` | `d90dd8f1…` / `ad67989b…` / 空；exit `0` |
| `git diff 5fe19efb…d90dd8f1` | 33 files，范围合规；exit `0` |
| `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | `live HEAD=d90dd8f1…`，7 项 PASS，**exit `0`** |
| `git diff HEAD^ HEAD --check` | 无输出，**exit `0`** |
| `git diff 5fe19efb^ 5fe19efb --check`（附加复算） | 无输出；exit `0` |
| `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check.py validate`（附加） | **exit `2`，`BLOCKED: r3 config byte/EOL mismatch`** |
| `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check-selftest.py`（附加） | **exit `1`**（同一 config 前置校验失败） |

未修改任何文件；运行后 `git status --porcelain` 仍为空。

## 未运行 / 未验证（不记为 PASS）

- 未运行 `recheck`/scanner，未读取、枚举、扫描或哈希任何 HostFolder 内容（`HostFolder compare/recheck=NOT_RUN`）。
- 未启动 `wsb start`/Sandbox、guest command、Build、runner/Vitest/GUI/WebView/Cargo 或任何产品测试。
- 宿主 Stage-1、root manifest 203/203 与 digest、clone pins/hardlink/EOL、`wsb list` 等否定性/宿主类事实本轮未独立复核 → `NOT_VERIFIED`。

## 非阻断观察（不计入 finding 计数，不改变本 commit 结论）

1. **EOL 复现环境差异**：R2 checker 硬校验 `codex-p02-wsb-smoke-config-r3.xml` 为 2609 bytes/LF。Git blob=`2609` bytes/LF，但本 review checkout（`core.autocrlf=true`）落盘为 `2631` bytes/CRLF，故 `validate`/self-test 在本 checkout 无法复现 PASS（exit 2/1）；candidate worktree 为 LF 2609，其 `PASS / EXIT=0` 声明可在该处成立。该差异**并非本 commit 引入**（XML 与 checker 均未在本 diff 内变更），属 checkout/证据可移植性限制，故不列为 open finding；建议后续修订为 checker 增加 CRLF→LF 归一化或在使用说明中显式标注。
2. `r9-followup-route-validator-r3.*`（`live HEAD=8e57687d`）与 `r9-followup-diff-check-r2.*` 仍作为历史文件留存但已无当前文档引用；如需保留，建议下轮标一句历史性说明。
3. `codex-checkpoint-p02-smoke-prestart-r9f-candidate.md:3` 的 “Base/current HEAD=`5fe19efb…`” 属提交前时点措辞，`:11` 已说明交付 HEAD 由 `git rev-parse` 取得；仅措辞层面，无 hash 绑定错误。
4. `doc/REBASELINE_PLAN.md` / `doc/STATUS.md` 历史快照段仍有与本次无关的既有失效 M2 链接（未被本 commit 触碰；`verify_plan.py` 的 delivery/navigation link 检查在本 HEAD 通过）。

## 推荐下一步

本 fixed HEAD/tree 已获独立 exact-head Review `APPROVED`。按冻结顺序，下一步由 Integrator=Codex 执行只读 HostFolder `recheck` 与 fresh UI/WSB/资源/clone 预启动核验；全部通过前 Hard Build Barrier 保持有效，不得 `wsb start`；本 Reviewer 本轮未触碰 HostFolder。

```text
[Codex Integrator] 基于已 APPROVED 的固定交付 d90dd8f1d44dd022314bb63a305b013dcadb6a44 / tree ad67989bee362c29fdedaa0fb44bf4864de693c7：
1) 运行只读 HostFolder recheck（不做写入/重新采集），任一 unknown/mismatch 立即 BLOCKED；
2) 重新采集并保存 @oai/sky 枚举输出与时间、WSB identity/list、clone pins/hardlink、碎盘/内存阈值；
3) 全部 PASS 后才允许 `wsb start`（限一次 Smoke）；Smoke 不通过 Build Gate；
4) 结果写入新的 verification/P02 checkpoint，固定新 HEAD/tree 后再派发 DSH exact-head Review。
禁止：产品源码/依赖/契约变更、Build、runner/Vitest/GUI/WebView/Cargo、产品测试、读取或哈希 HostFolder 内容用于交付。
```
