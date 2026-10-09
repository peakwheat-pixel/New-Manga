## Decision

**CHANGES_REQUESTED**（仅因 1 项 P2 证据指针缺陷；无 P0/P1；本次不涉及产品范围裁决。P02 仍为 `in_progress / ACTIVE`、`NO_SANDBOX_START`，不得启动 Sandbox）

---

## 1. Exact HEAD / tree / base 与我执行的只读命令

| 项 | 值 | 命令 / 退出码 |
|---|---|---|
| HEAD | `e6227e0b0b2c205105c8bc22ee49132d9da779e7` | `git rev-parse HEAD` → exit 0 |
| HEAD tree | `d05694f1a6eb1867a3d0ee1e8416698e2e3f4ed9` | `git rev-parse HEAD^{tree}` → exit 0 |
| 预期 base | `4183e7f7cf366c27aa8ad8a0bc7300af48783470`（可解析） | `git rev-parse <base>` → exit 0 |
| base tree | `6cc9c13a1da760bb60a4cbc369e7b8d90128b4da` | 与文档声称一致 |
| 父子链 | `4183e7f7 → 3fcaee2f59de362c21c7d4e721da9336742ca75e → e6227e0b` | 切片 = 2 个 commit，32 个路径 |
| diff 范围 | 32 paths：`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md` + `verification/P02/**` | `git diff --name-status base..HEAD` → exit 0；范围外路径过滤结果为空 → exit 0 |
| 空白/格式 | base..HEAD 与 HEAD^..HEAD 均无 whitespace error | `git diff --check`（两次）→ exit 0 |
| route validator（我本人在 HEAD 复跑） | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` → **7/7 PASS**（含 “delivery/navigation local links resolve”） | exit 0 |
| 工作区 | 仅 2 个本次 Review harness 生成、未跟踪的会话日志（`verification/P02/dsh-review-p02-current-prestart-r1.{stdout.jsonl,stderr.log}`），无 tracked 修改 | `git status --porcelain` |

结论：HEAD/tree 可确定，diff 确为预期的 P02 文档/证据切片 → **未 BLOCKED**。

---

## 2. Finding 计数

**P0/P1/P2/P3 = 0/0/1/2，open = 3**

---

## 3. Findings

### P02-PRESTART-R1-01 — P2：HostFolder recheck 证据指针指向未提交文件，且 SHA-256 / 结束时间与已提交证据不一致

- 位置：`verification/P02/codex-checkpoint-p02-smoke-prestart-hostfolder-recheck-delivery-r1.md:5-6`；被 `verification/P02/codex-checkpoint-p02-smoke-prestart-current-r1.md:14` 作为“命令和日志 Hash”的承载引用。
- 触发/影响：该行声称 stdout=`verification/P02/r9f-integrated-host-recheck-r1.stdout.log`（SHA-256=`3d954fd88d1e3a740b0a5ff4130c2bdf6426c272efa7c66ff2765c5a788f4c96`）、stderr=`…stderr.log`、exit=`…exit`，结束时间 `2026-10-10T06:26:19+08:00`。实测 `git ls-files` / `git cat-file -e HEAD:<path>` / 工作区枚举均不存在 `r9f-integrated-host-recheck-r1.*`（`git cat-file` → exit 128；全路径 glob → 0 命中），HEAD 历史上也从未提交过该路径。已提交的同类证据是 `r9f-current-prestart-host-recheck-r2.stdout.log`（exit=`0`、stderr 为空、`result=PASS`、`mapping_count=11`、`mismatch_count=0`、`completed_at=2026-10-10T06:45:29+08:00`，实测 SHA-256=`54128239AA482E4CC4E6DEAB50CBCF8876CB76E9674E6B0432DCAAE4F0D1F855`）。即：**结论数值被已提交证据完整支持（见下文核对），但记录中给出的文件、Hash 与时间不可解析且与已提交工件互相矛盾**——与已关闭的 R9F-01（P2「未提交日志引用」）同类，属回归；恢复者按记录无法复现该次 recheck 的证据链。
- 最小修正：把 `…:-5-6` 的 stdout/stderr/exit 指针改为已提交的 `r9f-current-prestart-host-recheck-r2.stdout.log`（SHA-256=`54128239AA482E4CC4E6DEAB50CBCF8876CB76E9674E6B0432DCAAE4F0D1F855`）、`.stderr.log`（空）、`.exit`（`0`），结束时间改为 `2026-10-10T06:45:29+08:00`；或把 `r9f-integrated-host-recheck-r1.{stdout,stderr}.log/.exit` 三件一并提交并注明与 r2 的关系。同时让 `…current-r1.md:14` 只保留一个 canonical stdout 指针。

### P02-PRESTART-R1-02 — P3：route-validator / diff-check 证据绑定在 `3fcaee2f`，未绑定本次 Review 的 exact HEAD

- 位置：`verification/P02/codex-checkpoint-p02-smoke-prestart-review-dispatch-r1.md:8,15-16`（Delivery commit/tree = `3fcaee2f`/`4fb5027c`）；证据文件 `r9f-current-prestart-route-validator-r1.stdout.log`（HEAD=`3fcaee2f`、tree=`4fb5027c`）、`r9f-current-prestart-diff-check-r1.stdout.log`（`git diff HEAD^ HEAD --check`，HEAD=`3fcaee2f`），均由 `e6227e0b` 提交。
- 触发/影响：审查 HEAD 是 `e6227e0b`（tree `d05694f1`），该 commit 自身新增的两份 md 及其余 review-package 文件没有任何绑定于 `e6227e0b` 的 validator/diff-check 记录；会话记录虽然诚实标注了“Delivery commit=3fcaee2f”，但审查包标题与“exact-head”措辞易被读成已覆盖 HEAD。经我本人在 `e6227e0b` 复跑，`verify_plan.py`=7/7 PASS（exit 0）、`git diff --check`（HEAD^..HEAD）=exit 0，**故无事实缺陷，仅为绑定/表述缺口**（同类历史先例 R9F-02 为 P3）。
- 最小修正：在 dispatch checkpoint 或 current checkpoint 显式写明“宿主校验与 route validator/diff-check 绑定 delivery commit `3fcaee2f`；HEAD `e6227e0b` 仅在其上新增 review-package 文件”，或把对 `e6227e0b` 的复跑证据补入包内。

### P02-PRESTART-R1-03 — P3：`doc/STATUS.md` 当前段与历史段缺空行，被 Markdown 合并为同一段

- 位置：`doc/STATUS.md:7-11`（尤其 `:10` 与 `:11` 之间无空行）。
- 触发/影响：第 7–11 行在 CommonMark 下渲染为**同一个段落**，使“历史观测（04:11）”“当前 post-clone 检查”“Host/WSB”“R2 HostFolder”“**前次状态快照（r6）**”五类不同性质的内容视觉上无边界，削弱了“旧 04:11 Stage-1 16/16 明确为历史、不被当作当前”的分层（文字本身已显式标注历史，故仅为 P3；`doc/00_INDEX.md:3-5` 与 Plan 均保留了空行，口径不一致）。
- 最小修正：在 `:7` 之前保留空行外，于 `:7/:8/:9/:10` 之间及 `:11` 之前补回空行，使当前状态与历史快照分段。

---

## 4. 复核覆盖（已独立核对为一致的部分）

1. **范围/一致性**：32 路径全部落在切片声明的允许路径内（4 份文档 + `verification/P02/**`），零越界；`base^{tree}=6cc9c13a` 与各记录一致；`4183e7f7` 确为 `3fcaee2f` 的父提交。
2. **04:11 Stage-1 16/16 的历史定性**：`00_INDEX:5`、`STATUS:7`、`REBASELINE_PLAN:11`、`tasks/P02.md:236`、`current-r1.md:25` 均明确标注为 clone 创建前历史观测、不作本轮 fresh admission → **未被当作当前**。
3. **HostFolder recheck 计数与证据一致**：文档各处（`STATUS:9-10`、`PLAN:8`、`00_INDEX:3`、`P02.md:227,234`、两份 checkpoint）与已提交 `r9f-current-prestart-host-recheck-r2.stdout.log` 完全吻合：11/11 PASS、mismatch=0、issues=0、artifact_validation=PASS、records=204419、verified=50389、full hashes=50356、samples=33、not-computed=138947、reparse issues=0、baseline=`599f325…`、tool=`1bcbc836…`、exit=`0`、stderr 空。且**账目可整除核对**：50389 + 138947 + 15083（与 `smoke-prestart-manifests-r2/summary.json` 的逐映射 `directories` 求和一致）= 204419。
4. **clone / source / EOL / hardlink / output-capability**：`r9f-current-prestart-filesystem-r2.json`＝PASS（12/12 roots、root reparse=0、20/20 input sha、14/14 registered size、3 项 clone EOL pin 全匹配、clone `7ce3c40c` private Git、remote=0、alternates=false、clean），其对 r1 的 supersede 原因亦有自述；`r9f-current-prestart-hardlinks-r1.json`＝3/3 link_count=1、failed=0；`r9f-current-prestart-output-capability-r1.json`＝写入/读回/删除/目录复原全 PASS，且目标仅为 scratch clone 内 canary 目录。
5. **当前 Sky / WSB 陈述有据**：`r9f-current-sky-enumeration-r2.json`（app=40、window=4、WSB app/window=0、未持久化标题）；`r9f-current-host-prestart-r3.json`（InstallState=1、`wsb --version`/`wsb list --raw` exit=0、`WindowsSandboxEnvironments: []`、pwsh 7.6.6、interactive、elevated=false）；`r9f-current-token-integrity-r1.json`＝Medium（S-1-16-8192）。
6. **root protection**：`r9f-host-recheck-root-manifest-pre-ff-r2.json`＝203/203、missing/extra/mismatch/staged=0、digest 与冻结 manifest 一致；我另核对 `codex-process-isolation-root-start-manifest.json`（digest `3a54fa97…`）确为 **4 个 tracked M + 199 个 untracked = 203**，且**本切片 32 个路径无一出现在该冻结清单中 → overlap=0 得到独立佐证**。
7. **无越权 PASS 声明**：全切片未见 Smoke / 产品验收 / Build Gate / Hard Build Barrier 被判 PASS；一律为 `Smoke=NOT_RUN`、完整 preflight 未完成、`Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`Hard Build Barrier=EFFECTIVE`（唯一 `PASS` 属 R9F Review 与历史 Stage-1，且均显式标注）。
8. **一次性限制与 Review 后即时检查仍显式**：一次性尝试见 `PLAN:5,11`、`STATUS:5`、`P02.md:91,237`、`current-r1.md:27,36`、`dispatch:25`；Review 后立即复核见 `current-r1.md:35`、`dispatch:30`、`PLAN:11`、`P02.md:238`。新增/变更的所有本地链接均可解析（我逐文件解析并确认 10 处失效链接全部位于本切片未触碰的历史段落，新增行 0 命中）。
9. **工件自洽性**：7 个新 JSON 全部可解析；6 个新 `.exit` 内容均为 `0`；新 `.stderr.log` 均为空。

## 5. NOT_RUN / UNKNOWN / 覆盖限制

- **NOT_RUN（按指令禁止）**：`wsb start`、任何 Sandbox/guest 命令、Build、GUI、产品测试、HostFolder 的访问/扫描/枚举/哈希——均未执行，故 R2 recheck 与宿主探针**未被我现场复现**，只核对了已提交工件之间的内部一致性与 hash/exit。
- **UNKNOWN**：`r9f-current-host-prestart-r3.json` 只有测量值、无阈值判定字段，`current-r1.md:17`「资源阈值全通过」的 16 项阈值定义不在本切片内，无法逐项判定（数值与历史 16/16 快照同量级）。
- **UNKNOWN**：产生 host/Sky/hardlink/output-capability JSON 的采集脚本未随切片提交，上述 JSON 只能作为已捕获工件采信。
- **NOT_VERIFIED（低影响，观察项，非 finding）**：`dispatch:17`「Selected current JSON evidence parsed successfully … staged diff check PASS」无对应保存工件（JSON 可解析我已复核为真；staged diff check 无留档）。
- **观察项（非 finding）**：`00_INDEX:3` 本次改写后不再复述“仅一次尝试”（其余四处仍显式）；`current-r1.md:9` 的 candidate 129 路径与 `dispatch:10` 的 111 未跟踪路径经两次提交账目可完全对齐（129 = 4 tracked + 125 untracked；125 − 20 = 105，+6 = 111），不构成矛盾。

## 6. 明确确认

**未运行任何 Sandbox 或 `wsb start`，未运行任何 guest 命令，未运行 Build、GUI 或产品测试，未访问/扫描/枚举/哈希任何 HostFolder 内容。** 我未修改任何文件（仅使用只读的 read/grep/glob/git 查询；`verification/P02/dsh-review-p02-current-prestart-r1.{stdout.jsonl,stderr.log}` 是 Review harness 本会话自身产生的未跟踪日志，非我编辑仓库内容）。为核对记录，我只读取了**已提交**的日志与 JSON——其中包含先前记录的 HostFolder 路径名与 record 哈希字符串，但我未接触那些 HostFolder 位置本身。

## 7. 建议的下一步

保持 `NO_SANDBOX_START`。由 Codex 在冻结的文档/证据范围内做最小修订：修正 P02-PRESTART-R1-01 的证据指针与 Hash/时间（并为 R1-02/R1-03 作显式绑定与空行修正），生成新的 delivery commit 后按新 exact HEAD/tree 复跑 `verify_plan.py` 与 `git diff HEAD^ HEAD --check`，再重新派发 DSH 只读 exact-head Review；在上述三项闭合前**不得**执行唯一一次 `wsb start`。