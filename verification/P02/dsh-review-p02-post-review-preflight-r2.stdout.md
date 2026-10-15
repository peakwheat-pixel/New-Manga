# P02 follow-up Review（R2，只读、独立）

## Verdict: **APPROVED**

P0/P1/P2 = 0/0/0，因此允许 fast-forward 集成；残留 1 项 P3（仅措辞绑定，不阻断）+ 3 项 Info。四项 closure 均判 **CLOSED**，但 P3-2 有一个 head 命名精度残留（见 R2-1）。

## Review HEAD / base

| 项 | 值 | 核验 |
|---|---|---|
| Review HEAD | `8a0685c9bf5aec7e7cc51f466f3fec7b176c35de` | `git rev-parse HEAD`（全程未变） |
| HEAD tree | `980a2a47d30630c5d0a7ad6adca32e644fc5ae95` | `git rev-parse HEAD^{tree}`（与给定一致） |
| parent D22 | `0a843a65c28818f92726bd91ae4c244e66fb37ea` / tree `68e8059b7f7c4cdcaeff73679fdc06e7288e55b1` | `git log --format='%H %T %P'` |
| main / base D19 | `1d5845e2b185179d7b683e5279f6520fc0882d97` / tree `e8b97f012db2086f7c33008070ba960d4e51cbd5` | `git rev-parse`；`merge-base --is-ancestor D19 HEAD`=exit 0 |
| 工作区 | `git status --porcelain` 空（0 行）；detached `HEAD` | 开始/结束一致 |
| 变更范围 | 54 files：`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`、`verification/P02/**` | `git diff --name-status D19 HEAD`；`src|apps|tests|packaging|spec|Cargo|package.json|pyproject` 匹配数 **0** |

## P3-1..4 closure matrix

| # | R1 finding | 结论 | 证据 |
|---|---|---|---|
| **P3-1** | 旧 preflight-start continuation 仍写“当前”状态 | **CLOSED** | `doc/tasks/P02.md:332` 标题已改为“（历史启动快照；当前状态见下方 BLOCKED 记录）”；`:336-338` 旧值保留但已被标题明确归为历史，且与 `:340-347`（BLOCKED）无并存歧义。这正是 R1 给出的最小修复选项 |
| **P3-2** | checkpoint 的“下一准确动作”时序过期 | **CLOSED（含 1 项 P3 措辞残留）** | `verification/P02/codex-checkpoint-p02-post-review-preflight-blocked-r1.md:48` 与 `doc/tasks/P02.md:348` 的 next action 已变为“派发 exact-head follow-up Review → fast-forward → 复核 main root manifest → 等 Feature=Enabled”，与本提交阶段 `BLOCKED / DSH_REVIEW_APPROVED / P3_REPAIRED_FOLLOWUP_REVIEW_PENDING / NO_SANDBOX_START`（`:4`、`P02.md:342/347`）一致；不再描述“已由本提交完成的动作” |
| **P3-3** | diffcheck/tip 的 HEAD 绑定只能靠文字 | **CLOSED** | 新增 `post-review-preflight-validation-r3.json`（D21）与 `-r4.json`（D22），逐项绑定 `head/tree/parent/base/command/exit/stdout_sha256/stderr_sha256`；`route-r4.stdout.log:1` 自带 `live HEAD=0a843a65…` 自证。我独立复算：route stdout=`ea211312a76c830082f993866a914cf066373382e5512f735c4c2f2345926805`（=JSON 记录）、stderr/base-diffcheck/commit-diffcheck 均为空文件 hash `e3b0c442…`、三个 `.exit` 内容均为 `0`、`validation-r4.json` 自身 SHA-256=`dc53e26e…` 与 checkpoint `:41` 记录一致 |
| **P3-4** | 三份状态文档口径详略不一致 | **CLOSED** | `doc/00_INDEX.md:3`、`doc/STATUS.md:3`、`doc/REBASELINE_PLAN.md:3/5` 均含 `R5 P0/P1/P2/P3=0/0/0/3、open=3`、`R5F-01/02=false_positive`（PLAN 作“判定为误报”）、`R5F-03=deferred`（PLAN 作“非阻断的可选措辞澄清并延后”），且三处恢复指针同一指向 blocker checkpoint（文件存在） |

## route / diff 命令与 exit

| 命令（本 Reviewer 在本 worktree 实跑） | exit |
|---|---|
| `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`（HEAD=D23，输出 `live HEAD=8a0685c9…`，7/7 PASS，末行 `Product tests/build/GUI: NOT_RUN`） | **0** |
| `git diff D19 D22 --check`（=r4 `base_diffcheck`，stdout/stderr 空） | **0** |
| `git diff HEAD^ HEAD --check`（=r4 `commit_diffcheck`，stdout/stderr 空） | **0** |
| `git diff D19 HEAD --check`（整段候选） | **0** |
| r1/r2/r3 的 `route-*.exit`、`diffcheck-*.exit` 内容复核（r3 stdout SHA=`a1888a01…`=r3 JSON 记录） | 均 `0` |
| checkpoint 引用的 8 个 artifact SHA-256（tool `acef0292…`、baseline `summary.json`=`545ed014…`、hostfolder `fb1222ba…`、filesystem `f5072948…`、host `e28227c2…`、sky `c54271ba…`、root-protection `a613ea61…`、route r1/r2/r3） | 全部 **MATCH** |

## 产品边界与泄漏面

- 边界一致且未混同 Gate：`Feature=UNKNOWN`（非提权 `Get-WindowsOptionalFeature` exit=1 / COMException，`host-r1.json:12-16`、`thresholds.overall=BLOCKED`、`10/11`）、`fresh preflight=BLOCKED`、`wsb start=NOT_RUN`、`Smoke=NOT_RUN`、`build=NOT_AUTHORIZED / NOT_RUN`、`Build Gate=BLOCKED`、`AC1–AC7=BLOCKED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`（checkpoint `:45-47` 显式区分方案 Review / Smoke 准入 / Build Gate / 产品验收）。
- 泄漏面：新增 artifacts 中 **未新增** SID、身份值、无关应用名/窗口标题（`sky-r1.json:7`=`false`；`host-r1.json:48`=`(path omitted)`）。原始 HostFolder stdout（`post-review-preflight-hostfolder-recheck-r1.stdout.log:3-24`）含 11 个宿主绝对路径（含 `C:\Users\49745\…`），属**已知本地路径暴露提示**：我比对同一 11 个 `host_folder` 集合与既有已入库 `verification/P02/r9f-current-prestart-host-recheck-r2.stdout.log` **完全相同（无新增、无消失）**，故不构成新增泄漏类别。另注：既有 `verification/P02/r9f-current-host-prestart-r3.json:4` 含真实 `windows_user_sid`，但该 blob 在本 diff 中未被修改（`git diff --quiet D19 HEAD -- <该文件>`=exit 0），**不是本候选引入**。
- NOT_RUN（未运行、不声称 PASS）：HostFolder 重扫、host inventory、Windows Feature query、`wsb start`、guest command、build/Cargo/Tauri、Vitest、GUI/WebView、任何产品验收、live main root 203 项逐条复算。

## Remaining findings

**R2-1（P3，非阻断）— follow-up Review 目标仍写 `exact D22`，而交付 tip 是 D23**
- 位置：`verification/P02/codex-checkpoint-p02-post-review-preflight-blocked-r1.md:48`；`doc/tasks/P02.md:348`
- 问题：两处 next action 写“由 DeepSeek Harness 对 **exact D22** 做 follow-up Review”，但本次交付的候选 tip / Reviewer worktree HEAD 是 D23=`8a0685c9`，而恰恰是 D23 才携带关闭 P3-3 所需的 `post-review-preflight-validation-r4.json` 与 r4 日志。按字面执行 exact-D22 Review 将看不到 P3-3 的修复证据，与本项目“exact HEAD 绑定”惯例不一致。
- 影响：仅追溯精度；无 Gate、计数或产品风险（本次 Review 已实际覆盖 D23）。
- 最小修复（下一轮 docs-only 提交）：将两处改为“对候选 tip `8a0685c9`（=`0a843a65` + exact-D22 validation records）做 follow-up Review”。

**Info-1** HostFolder 原始 stdout 保留 11 条宿主绝对路径（同既有约定；本轮无需改动）。
**Info-2** PLAN 用中文表述处置（“判定为误报/延后”），未使用字面 `false_positive`/`deferred` 枚举；与 INDEX/STATUS 实质一致，仅词面差异（属既存）。
**Info-3** `validation-r4.json` 的 `commit_diffcheck.command` 为符号式 `git diff HEAD^ HEAD --check`，未像 `base_diffcheck` 那样 SHA 全固定；同文件已记录 `parent`/`head`，绑定可推导，无实质缺口。

## 是否允许 fast-forward 到 main

**允许。** 判据：① 54 条变更 100% 落在冻结范围，产品源码/接口/依赖/Schema 0 改动；② 四项 P3 closure 均有可复算证据，artifact hash 全部 MATCH，`D19..D22`、`HEAD^..HEAD`、`D19..HEAD` 三组 `--check` 与 route validator 均 EXIT 0；③ 唯一阻断点（Feature=`UNKNOWN`）表述准确、fail-closed 未越界执行 `wsb start`/build/产品验收；④ root protection 报告 203/203、`entries_sha256=3a54fa97…`、overlap=0，与主线基线一致。

集成执行约束（Codex）：在该 candidate 上以 `--ff-only` 将 `main` 从 D19=`1d5845e2` 前进到 tip（D16→D19→D22 链上无分叉）；集成后复核 203-entry root manifest 与 candidate/root overlap=0；**不得**把本次文档/证据集成为 Smoke 准入、Build Gate 或产品验收背书，Hard Build Barrier 继续 EFFECTIVE。

**推荐下一步（可直接转发）**：
> 由 Codex 执行：在该 candidate 上 `git merge --ff-only` 集成到 `main`，post-FF 复核 203-entry root manifest（digest `3a54fa97…`、overlap=0）；随后把 R2-1 与 Info-1..3 合并为一次 docs-only 微调（更新 `codex-checkpoint-p02-post-review-preflight-blocked-r1.md:48` 与 `doc/tasks/P02.md:348` 的 follow-up Review 目标为候选 tip D23，并归档本 R2 Review 报告），再交由 DeepSeek Harness 对微调 commit 做 exact-head 复核。P02 仍等待 Windows Sandbox `Feature=Enabled` 的 fresh 可核验结果；UNKNOWN/FAIL 继续禁止 `wsb start`，不提权、不启用 Feature、不运行 guest/build/product test。
