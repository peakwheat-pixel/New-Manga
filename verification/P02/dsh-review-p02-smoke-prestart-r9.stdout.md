已完成全部只读核查。以下为独立复审报告（R9 exact-head）。

---

# P02 R9 Smoke pre-start 证据返修 — 独立复审

## decision
**`CHANGES_REQUESTED`**

R8 的 P2-A、P2-B、P3-C、P3-D、P3-E、P3-F **六项均已实质处置**（我逐项独立验证，见下）；但交付内仍残留 **1 处证据句柄失效（checker SHA-256 与当前交付不一致）**，以及 1 处引用集未收敛到最新已提交证据。两项均为 P3、非门阻断，但按治理文档"引用必须绑定当前交付"的要求，应最小修正后再固定 HEAD。

## 绑定对象确认
| 项 | 值 | 核对 |
|---|---|---|
| `git rev-parse HEAD` | `8b91c8bf032fce3db50bd5a89d5122bf461f0cb2` | ✅ 与固定 Delivery HEAD 一致 |
| `git rev-parse 'HEAD^{tree}'` | `586902273c98399c4737a8f801f0ddfff11408d8` | ✅ 与固定 Delivery tree 一致 |
| branch / worktree | `codex/P02-process-isolation`；`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga` | ✅ 一致 |
| 变更范围 | `git diff --name-only base..HEAD` = 31 路径，全部 `doc/**`(4) + `verification/P02/**`(27) | ✅ 无产品源码/依赖/契约/Schema（仅 documentation/verification） |
| tracked 工作区 | `git status --porcelain -- <changed paths>` 为空 → 结论仅对该 commit 成立 | ✅ 未把 untracked DSH 日志当交付内容 |

## finding 计数
**P0=0，P1=0，P2=0，P3=2**

## R8 findings 逐项处置判定（我独立复核的判据）

| ID | 级别 | 判定 | 我的独立依据 |
|---|---|---|---|
| P2-A | P2 | **CLOSED** | `git grep` 在 HEAD 中，`r2-manifest-artifact-validation-r4*` / `r2-manifest-recheck-selftest-r3*` 只余 R8 历史报告内的被引原文（`dsh-review-p02-smoke-prestart-r8.stdout.md:43-45`，属不可改历史证据）。三处正文（`codex-smoke-prestart-manifest-r2-errata.md:3`、`codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8`、`doc/tasks/P02.md:90/92`）已指向 HEAD 中实际存在的 `r5`/`r4`，并进一步收敛到 `r6`/`r5`。我逐链接验证被引文件均在 HEAD 存在 |
| P2-B | P2 | **CLOSED** | `codex-smoke-prestart-manifest-r1.py:2` = `INVALID_PARTIAL_HISTORY`；`smoke-prestart-manifests-r1/README.md:3` = `NOT_GATE_EVIDENCE`；`doc/tasks/P02.md:90` 现并列区分二者，与文件实际文本逐字相符 |
| P3-C | P3 | **CLOSED** | `doc/00_INDEX.md:3` 已恢复 `Smoke=NOT_RUN；完整 preflight=BLOCKED / INCOMPLETE；Build Gate=BLOCKED；build=NOT_AUTHORIZED / NOT_RUN；AC1–AC7=BLOCKED / NOT_RUN；Hard Build Barrier=EFFECTIVE`（base `:3` 无该句，HEAD 有；`git grep "Hard Build Barrier"` base INDEX 零命中、HEAD 命中） |
| P3-D | P3 | **CLOSED** | `delivery:8` 首句 + `doc/tasks/P02.md:88` + `doc/00_INDEX.md:5` 现明确：12-root inventory 仅 root existence/root-level reparse；11 个 Smoke mapping 才递归；6 个 toolchain mapping 为 metadata-only。我读 `smoke-prestart-manifests-r2/summary.json` 核对：恰好 **6** 个 mapping `hash_mode=metadata_only_with_selected_samples`（index 3,7,8,9,10,11），verified 合计 4+9+2+10+1+7=33，not_computed 合计 138,947 —— 与文档数字逐项一致 |
| P3-E | P3 | **CLOSED** | 我 grep 该 checker 全部 `open(`：`:33/:47/:63/:85/:175/:191` 六处**全部**为 `with open(...) as stream:`，已无裸句柄 |
| P3-F | P3 | **CLOSED（我实际运行确认）** | `codex-smoke-prestart-manifest-check-selftest.py:37` 覆盖 `None/records_sha256/records_count/status/issues` 五种输入，断言 `actual==0/2`、`result==PASS/BLOCKED`、`mismatch_count==0/1`；`check.py:161-162` 将任何 `issues` 非空计入 mismatches，`:174/:182` fail closed（exit 2）。**我实跑 self-test → 5 条全过，EXIT=0**，输出与 `r2-manifest-recheck-selftest-r5.stdout.log` 逐字符一致 |

## 本轮 findings

**P3-1 — R8 candidate checkpoint 的 checker SHA-256 已与当前交付脱钩**
- 路径/行号：`verification/P02/codex-checkpoint-p02-smoke-prestart-r8-candidate.md:8`（`Checker SHA-256=4d374260f81ff5868da11a577823b31bb576f6eb8e67414d79235d5f14c679ff`）
- 事实：我实测 HEAD 的 `codex-smoke-prestart-manifest-check.py` SHA-256 = `1bcbc836b07ba76627816a63206e1dde846201872f6df32d265684abb3020af8`（与 `r2-manifest-artifact-validation-r6.stdout.log` 的 `tool_sha256`、`r2-manifest-recheck-selftest-r5.stdout.log` 的 `tool_sha256`、以及 R9 checkpoint `:7` 三处一致）。`4d3742…79ff` 是 R9 修改 checker（加 context manager）**之前**的版本，现在该句唯一实例已无对应文件，且其同句引用的 r5/r4 证据与当前 checker 不再是同一 artifact；同文件 `:5` 的 scope 句亦称"checker 未改动"，与 R9 实际改动 checker 不符。
- 影响：该历史 checkpoint 内"artifact-only validation / synthetic self-test 绑定本 checker"的溯源链失效；R8 candidate 与 R9 交付之间的 artifact 版本关系不可从交付内自证。
- 最小修复：把 `:8` 的 hash 更新为当前值（或改为指向 r6/r5 日志并注明 `tool_sha256=1bcbc83…`），并在 `:5` scope 句补一句"R9 已修改 checker 的文件句柄处理"。

**P3-2 — 正文引用集未收敛到最新已提交证据（与同批文档指向的 revision 不一致）**
- 路径/行号：`verification/P02/codex-smoke-prestart-manifest-r2-errata.md:3`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8`（均指向 validation `r5` / self-test `r4`）
- 事实：HEAD 同时存在更新的 `r2-manifest-artifact-validation-r6.stdout.log` 与 `r2-manifest-recheck-selftest-r5.stdout.log`；`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md:7`、`doc/STATUS.md:9`、`doc/tasks/P02.md:90/92`、R9 checkpoint `:7` 均指向 r6/r5。两个被引文件确实已提交（P2-A 已不存在死链），但同一交付内"latest"证据出现两套 revision，读者无法判断哪套对应当前 checker。另外所以我实测结果与 `r5` 日志的 `tool_sha256` 一致：`4d3742…79ff` 是旧 checker 的值，而当前 checker 的 hash `1bcbc8…` 只出现在 r6/r5 日志中——即现有 bundle 内 revocation 后必须解释 hash 差异。
- 影响：证据可追溯性未达"同一结论只维护一个权威位置"，会放大 P3-1 的混淆。
- 最小修复：把这两处（或至少 errata）的 validation/self-test 引用统一为 `r6`/`r5`，或在同句显式标注"r5/r4 为 R8 时点证据，当前 checker 的绑定证据见 r6/r5"。

## 未验证 / 未运行（一律不写成 PASS）
**我实际运行（只读）**：
- `git rev-parse HEAD` / `HEAD^{tree}`、`git status`、`git diff --stat/--name-only`、`git diff -U0`、`git show HEAD:<path>`、`git grep`、`git ls-tree`；
- `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check.py validate` → **PASS，EXIT=0**，输出 `records=204419 / full_hashed=50356 / samples=33 / not_computed=138947 / reparse_point_issue_count=0`，`tool_sha256=1bcbc83…`，与 r6 日志逐字段一致；
- `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check-selftest.py` → **EXIT=0**，`matching=PASS hash/count/status/issue_mismatch=BLOCKED host_scan=NOT_RUN`，与 r5 日志一致；
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` → **7 项全 PASS，EXIT=0**；
- 仅计算 **3 个已提交 script 的 SHA-256**（checker / self-test / R1 collector 头部文本读取），未哈希任何 HostFolder 内容；
- 对变更文件内所有相对 Markdown 链接做存在性解析：**新增段落无死链**；报出的失效链接（`doc/REBASELINE_PLAN.md` 中 `reviews/M2-TASKS-PRIMARY-SFX-GATE-…`、`verification/M2-TA3-B/…` 等，`doc/STATUS.md` 中 `reviews/M2-PROD-DETECT-…` 等）经 base 比对确认**全部是 base 已存在的历史遗留，不在本 diff 行内**，不计入本轮。

**我未运行（不是我的 PASS，也不是作者证据的复核）**：
- 未运行 `recheck`，未调用任何 scanner 对真实路径扫描；**未读取/枚举/扫描/哈希任何实际 HostFolder 内容**（`C:\P02\**`、`G:\CODEX\P02-scratch-build-source` 及 Python/Node/Rust/VS/Windows-Kits 根均未触碰）；`HostFolder compare/recheck` 维持 **NOT_RUN**；
- 未启动 `wsb`/Windows Sandbox、任何 guest command、`@oai/sky`；未运行 Build、runner、Vitest、GUI、真实 WebView、Cargo、产品测试；
- 未复核作者侧 Stage-1 宿主测量（CIM/AppX、`wsb` identity/version/hash、cores/RAM/磁盘、SID、203/203 root manifest 与 digest、candidate overlap）、clone 的 HEAD/tree/porcelain/hardlink/EOL pins —— 交付内相关声明我按静态证据采信，**未独立复现，记为 NOT_VERIFIED（宿主限制）**；
- 未独立验证"author 侧未发生 HostFolder 访问 / 未启动 wsb"这一否定性事实（只能静态检查交付文本自洽）；
- 未复现 R9 的 `r9-route-validator-r5`（记录 `live HEAD=6be3dfdb`，为 pre-commit 运行，属预期）、`r9-source-compile-r1`、`r9-diff-check-r5` 三项日志的原始运行，仅核对其被引文件与 exit 存在。
- 门状态按交付现状记录，**不写成 PASS**：Smoke=`NOT_RUN`；完整 preflight=`BLOCKED / INCOMPLETE`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`；Smoke admission=`ADMITTED`（限一次）。

## 建议下一步
由 Codex 在同一分支追加一个纯文档引用修复 commit（最小范围：更新 `r8-candidate:8` 的 checker SHA-256 与 `:5` scope 句；把 errata/delivery 的 validation/self-test 引用收敛到 r6/r5 或显式标注 revision 关系），重新固定 Delivery HEAD/tree 后派发 DSH R9-followup exact-head 复审。**复审 approved 且所有 immediately-pre-start 检查（含尚未运行的只读 HostFolder `recheck`、重新采集保存的 `@oai/sky list_apps/list_windows` 输出/时间、`wsb list --raw`）全 PASS 前，不得运行 `wsb start`**；Smoke 不通过 Build Gate，Hard Build Barrier 保持有效。
