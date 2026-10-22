# P02 Stage A r5 正式 Review（DSH，非作者）

| 字段 | 值 |
|---|---|
| 对象 | base `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`；reviewed_head **`172eee84240e101186b12f1aa09e8a2f9ec92d68`**；expected tree `a5b1af3e0708463df6865c8e49c9679e57e3fa85`；parent r4 `cc1bd7505f3fc48079db7ea2719040e77a8c58dd`；branch `agent/antigravity/P02-real-webview-harness` |
| decision | **`changes_requested`**（Stage A only） |
| 计数 | **P0/P1/P2/P3 = 0/0/2/4（open 6）** |

**我亲自核验**：分支引用=`172eee84`✔；reflog `cc1bd750→172eee84`（parent=r4、单提交）✔；`refs/heads/main`=`5de8d44c`=base✔；运行期 porcelain 16×`M`（`probe-execution-full.log:30-45`）全在 allowlist、无删除✔；harness 985 行 / runner 195 行 / TS / 夹具 / 交付 JSON 逐段阅读✔；WCAG 数值与判定逻辑复算✔；`types.ts`、`library/types.ts`、`RegionOverlay.tsx`、`relabelMachine.ts` 契约对照✔；Task `status: in_progress`、`integration_commit: null`✔。
**我不能核验**：`pwsh` 不可用（`SetNamedSecurityInfoW Win32 5 grantWrite …`）⇒ tree `a5b1af3e`/`d2569f6c`、scope SHA-256、任何 SHA-256、`git status/diff` 未复核；**未执行** runner/探针/harness/tsc/PowerShell/Vitest/build/GUI/WebView。**Codex 的 exact-head replay（`G:/CODEX/New Manga/verification/P02/r5-codex-exact-head-review.md` 与 `r5-codex-*` artifacts）是 Codex 执行，不是 DSH 运行结果**；其结论我仅作输入采用，并已在代码层独立复核。

## R4-01 – R4-11 处置

| ID | 判定 | 依据 |
|---|---|---|
| R4-01 P2 | **closed** | `ts:162` 显式 `const effectiveFg: [number, number, number] = …`；runner `:114-133` 执行 focused tsc，交付 Full 日志 `:52-54` Step 2 `EXIT: 0`；Codex detached tsc exit 0 |
| R4-02 P2 | **closed** | `harness:101-137` 从 `region/types.ts` 解析 `REGION_TYPE_VALUES`/`SfxPolicy`/`RegionOrigin`，用于 region/revision 的 `region_type/sfx_policy/origin`（`:290,292,294,318,323,324`） |
| R4-03 P2 | **closed** | 两阶段：runner 先 `Flush-Log`(`:157-159`) 再 `--finalize`(`:163`)；`finalize_artifact_hashes`(`:931-970`) 在定稿后哈希 5 件工件、不哈希自身、写 `finalization_status: FINALIZED`；交付 JSON `:36,43,45` FINALIZED；Codex 在 fixed r5 Full detached run 复算 5/5 match |
| R4-04 P3 | **partial → R5-01** | 评估器已 fail-closed（`harness:441-476`：缺/非 int `exit_code` 即拒绝；绑定 `probe_inputs_sha256`），探针也真的写出该字段（`static_control_probe.py:173-184`）；但**调用方 PASS 谓词未含 `report_is_fresh`** |
| R4-05 P3 | **closed** | 自检真实调用 `evaluate_static_probe_report`（`:479-515`，覆盖 stale head / dirty 输入 / 缺 exit / malformed）；`report_freshness_verified` 改为实算值（`:667`，交付 JSON `:124`=true）。注：覆盖止于评估器边界，调用方缺陷（R5-01）不在其内 |
| R4-06 P3 | **partial → R5-03** | catch 记录失败步骤/命令/参数/异常类型/`LastExitCode` 并显式 Flush（`:176-190`）；但**未持久化子进程 stdout/stderr**、Message 可被截断、`$LASTEXITCODE` 可能为陈旧值、未记录 StackTrace；Handoff:52/Task:149/RESUME:20 所称「详细 Message/StackTrace」「微探针实测」无 artifact 支撑（Codex failure probe 亦如此认定） |
| R4-07 P3 | **closed** | `load_authoritative_enums` 文件缺失/正则失败/解析为空即 `raise`（`:106,112,115,120,123,128,131`），由 PRE-01 `except Exception` 记 FAIL（`:605-613`） |
| R4-08 P3 | **closed** | 计数器 + `all_rejected_as_expected`（executed=rejected=4 且 skipped=0，`:430`），PRE-01 断言之（`:581`）；交付 JSON `:86`「4/4 executed and rejected (skipped: 0)」 |
| R4-09 P3 | **closed** | `ts:217` `(role === "disabled" \|\| role === "ui_component") ? 3.0 : 4.5` ⇒ large_text=4.5；夹具 `:233` `large_text_min_ratio: 4.5` |
| R4-10 P3 | **closed** | runner `:48-58` 任何命令前即写入 header+`Status: IN_PROGRESS` 并落盘；`Get-Command python` 移入 try(`:102`)；Codex 注入失败实验确认日志被新 IN_PROGRESS 记录替换 |
| R4-11 P3 | **closed** | `:245` `page_count` 允许 `None\|int`；`:297-309` 校验 bbox 4 个 [0,1] 数值（排除 bool）与 polygon 点的 [x,y] 结构/范围 |

## Open findings

| ID | 级 | 位置 | 触发/影响 | 最小修复 |
|---|---|---|---|---|
| R5-01 | **P2** | `harness:635-652`（尤其 `:642-644`、`:652`） | 新鲜度失败→重试；若重试未替换旧报告（探针在写盘前崩溃/被杀），`:640-644` 会重新读旧报告并把 `observed_exit` **覆盖为旧报告的 `exit_code=0`**；而 `probe_pass = (observed_exit==0 and overall_status=="PASS")`——**PASS 谓词不含 `report_is_fresh`** ⇒ 旧 PASS 可被判 PASS（`report_is_fresh=false` 只写进 details）。这正是 R4-04 想禁的场景 | 谓词改为 `report_is_fresh and observed_exit==0 and overall_status=="PASS"`；重试后不得用报告值覆盖 `proc.returncode`（分别记录） |
| R5-02 | **P2** | `run-webview.ps1:155-172`、`:159`、`:191-195` | `--finalize` **非零但不抛异常**时：日志已在 `:158` 定稿并写明「Full Stage A execution completed successfully with EXIT=0.」，失败只 `Write-Host`、未 append；`LogsFlushed=true` 使 `finally` 不再重写 ⇒ **失败运行的证据日志永久宣称成功**（且 header `Status: IN_PROGRESS` 在任何路径都未被终结，交付的成功日志亦然） | 在 `exit $finExit` 前 append `Status: FAILED` + finalize 退出码并再 Flush；成功路径置 `Status: COMPLETED` |
| R5-03 | P3 | `run-webview.ps1:176-190` | 异常路径不保存失败子进程的完整 stdout/stderr（Codex 观测：Message 仅首行，完整诊断只在外层 stderr）；`$LASTEXITCODE` 在抛出后读取，若在 `&`/`2>&1` 处抛错则可能取到上一流程的陈旧值，且 `EXIT:` 行不会写入；无 StackTrace | catch 内落盘捕获的 output/原始 stderr 与显式子进程退出码（并标注可能未知），补齐 StackTrace；归档所述微探针证据 |
| R5-04 | P3 | `run-webview.ps1:115-133`（`:116` 绝对路径） | **fail-open**：两个 tsc 候选都不存在时只写 Warning，随后照常走到 exit 0；报告仍为 3 PASS/0 FAIL，**没有 TS 检查的 NOT_RUN/FAIL 标记**；且候选 2 是硬编码根工作区绝对路径，与本 worktree/机器耦合 | 缺失 tsc 记 FAIL 或在报告中记 NOT_RUN；改用仓库内可解析路径；把 TS 门的结论纳入机器可读证据 |
| R5-05 | P3 | `harness:781-797` | PRE-03 顶层 `status` 恒为 `"PASS"`，不受逐 token/live/alpha `contrast_result` 影响，`all_passed` 也不因单个 FAIL 置假 ⇒ 若某 token 低于阈值，details 会写 FAIL 而场景仍报 PASS（当前全部达标，故未产生假 PASS） | 由 `calculated_ratios`/`live_ratios`/`alpha_evaluations` 汇总派生 PRE-03 状态 |
| R5-06 | P3 | `doc/handoffs/…handoff.md:30,41`；`RESUME.md:14`；`P02.md:147,149` | 声明「彻底闭合 R4-01 至 R4-11 全部 11 项」，但 R4-04（R5-01）与 R4-06（R5-03）仅 partial；R4-04 行称「杜绝同 HEAD 下 dirty 文件误用旧 PASS」强于代码保证；R4-06 行称记录 StackTrace 而代码未记录 | 按实际状态改写为 closed/partial 并注明残余 |

## 六项专项结论

1. **缺失 tsc 是否只警告并通过？——是**（R5-04）：`:130-133` 仅 Warning，随后仍 exit 0；交付运行确实找到 tsc 并 `EXIT: 0`（full 日志 `:52-54`），故当前证据未失真，但该门是 fail-open。
2. **PRE-02 是否可在新鲜度失败且重试未替换旧报告时凭旧 PASS 通过？——可以**（R5-01）：PASS 谓词不含 `report_is_fresh`，且重试分支用旧报告 `exit_code` 覆盖真实 `returncode`。
3. **抛出原生进程错误时是否记录完整输出与真实子退出码？——仅部分**（R5-03）：记录步骤/命令/参数/类型/`LastExitCode`，但无子进程输出、无 StackTrace、退出码来源不可靠；Codex failure-path 仅部分覆盖，且 Owner 所称微探针无归档。
4. **`--finalize` 非零（未抛异常）时定稿日志是否如实记失败？——否**（R5-02）：日志已写「completed successfully with EXIT=0」，失败不入日志且 `finally` 不再刷写。
5. **五项 artifact hash 是否绑定定稿后字节、是否避免自引用？——是**：`finalize` 在 runner `Flush-Log` 之后独立进程执行、5 件定稿工件逐一哈希、JSON 自身不入表（`:935,959-961`）；Codex 在 fixed r5 Full detached run 复算 5/5 match。我无法复算哈希（无 shell），但代码时序与交付 JSON 的 `FINALIZED`/`finalized_at` 自洽。
6. **枚举闭集/fail-closed/4 组 mutation/large_text/page_count/geometry——全部通过**：见 R4-02/07/08/09/11 各行；`authoritative_enums_enforced` 现输出真实解析集合，mutation 计数器真实，`large_text` 与夹具阈值均为 4.5。

## 架构、范围与 AC

变更 ⊆ allowlist（`verification/P02/**`、`e2e/**`、`doc/handoffs/P02-*.md`、`doc/tasks/P02.md`，16 paths，无删除）；`frontend/dist`、`cargo-target` 不存在；仅标准库；无 shell/网络/删除；未触碰产品 `src/**`、Tauri、Python Core、SQLite、共享契约、依赖、设计 token、Codex-only 路径；Hard Build Barrier 有效。**AC1–AC6 一律 BLOCKED / `exit_code: null`**；PRE-01/02/03 仅为静态前置（3 PASS）。**NOT_RUN**：Cargo/Tauri/sidecar、Vitest、前端 build、真实 WebView2/CDP/鼠标键盘、computed-color 采集、AC1–AC6 运行时、任何我未亲自执行的命令与哈希。

## Final verdict

`changes_requested`（Stage A only；P02 保持 `in_progress`，`integration_commit: null`）。r5 实质闭合 R4-01/02/03/05/07/08/09/10/11，并让 R4-03 的哈希链在 Codex 独立复算下 5/5 成立；但仍有 2 项 P2：**PRE-02 调用方仍可凭旧 PASS 通过（PASS 谓词缺 `report_is_fresh` + 重试覆盖真实退出码）**、**`--finalize` 失败会让证据日志永久宣称成功**；另有 4 项 P3（异常路径输出/退出码与微探针声明不符、TS 门 fail-open 且路径耦合、PRE-03 状态不随计算结果、Handoff/RESUME 过度闭合）。建议 Owner 在 allowlist 内提交 r6 修正 R5-01/R5-02 并澄清 R5-03/R5-04/R5-05/R5-06 后由 DSH 复审；Codex 对新 head 重跑 exact replay 并归档五项哈希与失败路径证据。**本 Review 不代表 P02 完成。**