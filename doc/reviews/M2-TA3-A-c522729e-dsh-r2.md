# approved_with_conditions

（限定复核 round 2；非作者静态 Reviewer。**只读，未修改任何文件。**）

## 0. 沙箱声明（影响本轮核验手段，必须先读）

本会话 **pwsh 全部不可用**：三次尝试（含 `-C`/`workdir`/无 workdir/子目录）均返回同一个沙箱初始化失败 —— `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-TA3-A-E2E-SMOKE-zcode)`。随后按最小必要升级 `danger-full-access` 重试被拒：`requires approval, but no approval channel is available`。**故本轮为纯静态核验**（read/grep/glob + 只读 reflog），以下两项未能执行、需集成方补：

1. **15 项 sha256 的盘上复算**（provenance 内容已逐行核对，但哈希值未与磁盘复算比对）；
2. **`git diff --name-status / diff --stat / 单 hunk` 的文件清单核验**。

唯一可得的 git 侧只读证据是 worktree reflog（`G:/CODEX/New Manga/.git/worktrees/M2-TA3-A-E2E-SMOKE-zcode/logs/HEAD`），其关键信息：`dc2b9aca → 8a754caf（docs: pin delivery head dc2b9aca (amend chain disclosed)）→ afd59c32 →(amend) c522729e（DSH r1 repair - provenance anchor, doc fixes, literal snapshot assertion）`。**即 `dc2b9aca..c522729e` 实际含 2 个 commit，不是单个 commit**（与预期文件集不冲突，但"单 commit"表述不成立；文件清单仍需集成方 `git diff --name-status` 定案）。

## 1. 逐条件核对（r1 → 本轮）

| r1 条件 | 修复主张 | 静态核验结论 |
|---|---|---|
| **P1-1** 证据链未锚定 / probe 不可复跑 | 新增 `raw/00-provenance.txt`（head + 3 脚本/7 JSON/5 PNG sha256 + 不可复跑声明），原 ac*.log 正文不重写 | **closed（静态）**。文件存在，40 行；`head=dc2b9aca`、`base=bebcfcde…`、`claim=1328a766` 与 Task/Handoff `base_commit`、reflog claim commit 三方一致；脚本 3 + summaries 7 + PNG 5 = 15 项与实际盘上文件一一对应（glob 已确认）；probe 不可复跑声明与 L-6 一致。**5 份 PNG 哈希与 commit-1 的 `smoke-*.json` 内 `export.sha256` 逐值一致**（`9bbd3876…`/`c5497a49…`/`02499d71…`/`207410cb…`/`c4518157…`）。未闭合项仅"哈希未盘上复算"（沙箱所致，非缺陷）→ 见 §4 指令 1、2。 |
| **P2-1** K11 `wall_s` 113.0 失真 | Task/Handoff 两处改 100.76 | **closed**。Task:64、Handoff:33 均为 `100.76`；`summaries/smoke-K11.json:542` 与 `smoke-report.json:62` 亦为 `100.76`，三向一致；全仓 grep 无残留 `113.0`。 |
| **P2-2** Run1「整页链」措辞 | Task §AC2 + Handoff §1 补 primary-region 语义句 | **closed**。Task:49、Handoff:17 均含"region 级步骤按生产 backfill 语义只作用于 primary region，其余 region 由 Run2 逐个覆盖"。修复时**新增的生产引用也已核真**：`src/application/tasks/service.py:939-942` 原文即"Multi-Region pages still run their pipeline steps against the first Region (`reading_order` 1)"，引用成立。 |
| **P3-1** 94→92 | Task/Handoff 计数改 92 | **closed**。Task:83、Task:91、Handoff:44 均为 92；97−5=92 算术成立；全文仅 Task:129 的 r1 轨迹行保留"94→92"字样（属轨迹引用，非残留错误）。 |
| **P3-2** 断言判别力 | `test_catalog.py` 单 hunk 改 5 case 显式字面快照，92 case fail-closed 不变 | **closed（值域已逐值核对）**。`test_catalog.py:49-73`：`ta3a_cases={BJ02,BJ06,K01,K02,K11}`，非 TA3-A 分支仍为 `pipeline_status == {stage:"NOT_RUN" for stage in expected_pipeline}` 全等（语义与原快照等价）；`expected_ta3a` 5 组与我逐键读出的 `cases.json` 实际值**完全一致**：K01:382-454 ✓、K02:459-535 ✓、K11:4296-4346 ✓、BJ02:4525-4593 ✓、BJ06:4804-4869 ✓（含键集全等，故任一 STAGE 退化 FAIL/NOT_RUN 均会变红）；与 `ac4` 日志的 PASS keys 逐 case 互证（K01/K02 各 7、K11 3、BJ02/BJ06 各 8）。**但回归证据未随断言更新 → 见新 P2-1。** |
| **P3-3** cosmetic/README 漂移登记 | L-7 登记不改代码；L-2 扩为 README:7,26-29；L-6 新增 | **closed**。L-7（Task:125）四项**全部静态核真**：`run_smoke.py:273` 注释确提 known gap；`run_smoke.py:489-491` 的 `generated_at_utc` 确在 case 循环（:503）之前取时=运行开始（与 `smoke-report.json` 02:52:27Z + 各 case wall 合计 ≈46.1min ≈ K11 完成 03:38:36Z 吻合）；`--keep-scratch`(:464) 全文件无任何读取处且无 rmtree/TemporaryDirectory 清理调用 → no-op 属实；`probe_artifacts.py:19,26-29` 的 `LIMIT SAMPLES_PER_STEP*4` 后仅取 `[:SAMPLES_PER_STEP]` → 放大确实无效。L-2 的 `README.md:7`（"当前所有应用 Pipeline 都是 `NOT_RUN`"）与 `:26-29`（4 行表格均含"应用 Pipeline `NOT_RUN`"）逐行属实。L-6 与 provenance 尾段表述一致。 |

**结论：r1 六项条件在静态证据层面全部 closed**；其中 P1-1 的"哈希与磁盘一致"与 P3-2 的"改后仍 82 passed"两条**证据闭环**尚未完成（前者沙箱所限，后者见下）。

## 2. 新增问题

- **P2-1（新，证据锚定）：ac3 回归日志仍锚定旧断言版本。** `raw/ac3-pytest-regression.log:3-4` 为 `HEAD=b94ebe87` / `date=2026-09-30T03:47:17Z`；而 `test_catalog.py` 的断言块是 r1 返修（reflog `afd59c32`@04:04:57Z → `c522729e`）才改成字面快照的（`ac4:26-28` 可证 b94ebe87 时该文件 delta 仅 12+/1-，与当前 29 行断言块不符）。Task:130「82 passed 保持」与 Handoff:44「修改后 82 passed」**在修复后的 head 上没有对应捕获证据**。我的静态逐值核对显示该断言**应当通过**，故这是证据卫生问题、非疑似失败。**闭合方式（二选一）**：在 `c522729e` 重跑 pytest 并刷新 ac3（推荐，约 10s）；或在 Task/Handoff 注明「ac3 为 b94ebe87 捕获，r1 断言变更后未重跑，已静态逐值核对」。
- **P3-1（新，文字漂移）**：`doc/handoffs/M2-TA3-A-1328a76.md:23` 仍写"遗留 L-1…L-5"，而同文件 §7/§8 已列 L-1…L-7、Task 已定义到 L-7 → 改为 `L-1…L-7`。
- **P3-2（新，同类漂移未登记）**：`test_assets/comic_golden_suite/manifests/local_asset_inventory.json:5`（"currently NOT_RUN"）与 `:713`（`peppercarrot_e04_ko`，即 K11 所在来源条目）在 K11 已回填 PASS 后同样失实/含混；L-2 只登记了 README。建议 L-2 扩为 `README.md:7,26-29` + `local_asset_inventory.json:5,713`，或新增 L-8（README/inventory 均不在本 Task 允许路径，交集成方随收口处理）。
- **P3-3（新，措辞张力，informational）**：provenance:7-9 称五个头行"were written at execution time"，Task:134 称 `319a3036` 系"仅 raw 日志头对齐交付 head 重生成"。两者在"头行是否被事后重写"上读感冲突（按时间线，ac1 头行 `HEAD=1328a766`@03:40:57Z、ac2-5 `HEAD=b94ebe87`@03:47:17Z 与各自捕获时刻自洽，b94ebe87 提交于 03:46:48Z）。建议统一为「头行由捕获脚本按当时工作区态写入、ac1 头行附运行起点注记；正文为原始 stdout 未重写」，避免后续读者误判证据链。
- **无新增 P1。** 我未发现生产代码改动、范围外文件改动或契约改动。

## 3. 本轮未复核项（限定复核边界，如实声明）

生产 seam 调用、provider 身份、回归 82 passed 的真实执行、像素零入库、cases.json 33 行 diff 等 r1 已成立项**本轮不重审**（仅就 r1 条件涉及处做静态交叉验证：PNG 哈希↔summaries、断言值↔cases.json↔ac4）。

## 4. 可直接转发的集成指令

> 致 Codex（集成）：
> 请对 worktree `G:\CODEX\New Manga.worktrees\M2-TA3-A-E2E-SMOKE-zcode`、分支 `agent/zcode/M2-TA3-A-E2E-SMOKE`、head `c522729e`（实现 head `dc2b9aca`）执行以下**只读/证据**收口，命令可直接复制（Git Bash）：
>
> ```bash
> cd "G:/CODEX/New Manga.worktrees/M2-TA3-A-E2E-SMOKE-zcode"
>
> # 1) 返修范围核验：期望只有 doc/handoffs、doc/tasks、tests/m2_test_assets/test_catalog.py、verification/M2-TA3-A/raw/00-provenance.txt
> git log --oneline dc2b9aca..c522729e          # 预期 2 个 commit（8a754caf + c522729e）
> git diff --name-status dc2b9aca..c522729e
> git diff dc2b9aca..c522729e -- tests/m2_test_assets/test_catalog.py   # 预期单一 hunk
>
> # 2) SHA256 锚定复算（provenance 为 SHA256SUMS 兼容格式，'#' 注释会被 sha256sum 忽略）
> sha256sum -c verification/M2-TA3-A/raw/00-provenance.txt    # 预期 15 行全 OK
>
> # 3) 修复后回归证据重捕获（DSH r2 新 P2-1：ac3 仍锚定 b94ebe87 旧断言）
> PYTHONPATH=src "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
>   -m pytest tests/m2_test_assets tests/m2_acceptance -q     # 预期 82 passed, EXIT=0
> # 将上述输出刷新到 verification/M2-TA3-A/raw/ac3-pytest-regression.log（头行 HEAD=c522729e）；
> # 或在 Task:130 / Handoff:44 注明「ac3 为 b94ebe87 捕获，r1 断言变更后未重跑」。
> ```
>
> 另请随收口一并处理三条**不阻断**文字项（均为 P3，作者侧或集成侧一行改）：① `Handoff:23` "遗留 L-1…L-5" → `L-1…L-7`；② L-2 扩为 `README.md:7,26-29` + `local_asset_inventory.json:5,713`（或新增 L-8）；③ 统一 provenance:7-9 与 Task:134 关于 raw 日志头行的措辞（正文未重写、头行按当时工作区态写入）。
>
> 上述 1)–3) 全绿即可将 DSH r2 的 `approved_with_conditions` 转为 `approved` 并进入集成；若 1) 出现预期外路径或 2) 出现任一 FAIL，则退回作者返修。

**下一步建议（按 AGENTS.md）**：由 Codex 执行 §4 的 1)–3) 并落盘 ac3 新证据；这 3 条收口不需新 Task、不需再派 Review，除非 1)/2) 出现不符预期结果。
