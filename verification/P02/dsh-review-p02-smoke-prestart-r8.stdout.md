已完成全部只读核查。以下为独立复审报告。

---

# P02 R7 Smoke pre-start 证据返修 — 独立复审（R8 exact-head）

## decision
**`CHANGES_REQUESTED`**

返修方向正确、F-01..F-10 的主体已实质闭合（含可复现 validator 与 synthetic recheck 自检），但交付内存在**同一提交中的证据链引用不一致**（部分文档指向未提交的旧版日志），另有若干独立小缺陷。

## 绑定对象确认
| 项 | 值 | 核对 |
|---|---|---|
| `git rev-parse HEAD` | `6be3dfdb1911a358ac779e1398437b0411bf2cfa` | ✅ 与固定 Delivery HEAD 一致 |
| `git rev-parse 'HEAD^{tree}'` | `f2d7b2637e18b59470cffd239287f130fe0beebc` | ✅ 与固定 tree 一致 |
| branch / worktree | `codex/P02-process-isolation`；当前目录即 review worktree | ✅ `git worktree list` |
| 变更范围 | `git diff --name-only base..HEAD` = 29 路径，全部 `doc/**`(4) + `verification/P02/**`(25) | ✅ 无产品源码/依赖/契约 |
| tracked 工作区状态 | `git status --untracked-files=no` 空 → 已跟踪文件与 HEAD 逐字节一致 | ✅ 结论只对该 commit 成立 |

## finding 计数
**P0=0，P1=0，P2=2，P3=5**（既有 F-01 主体闭合；下表 P2/P3 含 1 项由返修自身引入）

## R7 F-01..F-10 逐项处置判定

| ID | 判定 | 依据 |
|---|---|---|
| F-01 P2 | **CLOSED**（含下方 P2-A/P3-B 引用缺陷） | 新增 `codex-smoke-prestart-manifest-check.py` 独立复核：config 2609B/无 CRLF/hash、11 mappings 与冻结期望一致、summary 的 PASS/11、clone HEAD+tree pin、`issues=[]`、index 1..11、逐 records SHA-256、canonical 字节、排序、casefold 冲突、schema 键集/枚举/null、type 计数、verified/not_computed、全量 vs 选样策略、`totals==EXPECTED_TOTALS`、policy(reparse) 派生。**我本次独立运行 `validate` → PASS/EXIT=0，输出与 r5 日志逐字段一致**；日志 `tool_sha256=4d3742…79ff` == 交付 checker 实测 SHA-256，绑定成立 |
| F-02 P2 | **CLOSED（实现层）** | `check.py:142-178` recheck 只读（仅 `scanner.scan_mapping` + stdout，无写入）；逐 mapping 比较 `status/records_count/files/directories/verified_files/not_computed_files/records_sha256/hash_mode` 并把当前 `issues` 全部计入 mismatches；任何 mismatch → `BLOCKED` + exit 2（fail closed）；`mismatch_count/matches_baseline` 留证。synthetic 自检实测覆盖 match→exit0 与 `records_sha256` 篡改→exit2。**我未运行 recheck、未触 HostFolder** |
| F-03 P3 | **CLOSED** | `doc/STATUS.md:3`、`doc/00_INDEX.md:3` 已恢复"P05…故障转移"句与 `verification/P05/dsh-review-blocked-checkpoint-5288db42.md` 链接，与 base 一致 |
| F-04 P3 | **CLOSED** | `codex-checkpoint-p02-smoke-admission-r2.md:14` 取消"start 前"限定、`:20` 重写为 post-start 绑定并显式写 "This timing-only clarification is recorded in [R3 sequencing clarification]"，R3 侧双向指针齐全 |
| F-05 P3 | **PARTIALLY CLOSED** | 11-mapping vs 12-root 集合差桥接已加（`P02.md:90`、`REBASELINE_PLAN.md:7`、`STATUS.md:9`、`delivery:8`），但 base `delivery:8` 原有的"12 根中 6 个工具链根只记录 metadata"深度披露被删除、未替换 → 见 P3-D |
| F-06 P3 | **CLOSED** | 新增 `smoke-prestart-manifests-r1/README.md`（`INVALID_PARTIAL_HISTORY / NOT_GATE_EVIDENCE / SUPERSEDED_BY_R2`）+ `r1.py:2-3` 头部声明；仅 `P02.md:90` 的字面转述略有偏差 → 见 P3-B |
| F-07 P3 | **CLOSED** | `P02.md:90`、`delivery:8`、`r2-errata.md:3` 均记 `UNKNOWN / NOT_RECORDED`，未写成 PASS |
| F-08 P3 | **CLOSED** | `r2.py:282` 已由硬编码改为 `reparse_point_issue_count` 派生；已提交 `summary.json` 旧字段保留但 `README/errata/P02.md` 均声明其非测量值；checker `:124-126` 亦按 issues 派生 |
| F-09 P3 | **CLOSED** | `r3-sequencing.md:4` 与 `delivery:10` 均把"4 windows"降为"历史观察、原始输出未留存、启动前必须重新枚举并保存" |
| F-10 P3 | **CLOSED** | `00_INDEX.md:5` 现含 204,419 / 50,356 全量哈希 / 33 选样 / 138,947 未计算，且 `:3` 说明为"精确覆盖 r3 XML 的 11 个映射" |

## 本轮 findings

**P2-A — 交付内引用了未提交的旧版验证日志（证据链不一致）**
- 路径/行号：
  - `verification/P02/codex-smoke-prestart-manifest-r2-errata.md:3` → `r2-manifest-artifact-validation-r4.stdout.log`、`r2-manifest-artifact-validation-r4.exit`、`r2-manifest-recheck-selftest-r3.stdout.log`、`r2-manifest-recheck-selftest-r3.exit`
  - `verification/P02/codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8` → `r2-manifest-artifact-validation-r4.stdout.log` / `.exit`
  - `doc/tasks/P02.md:90` → `…-r4.stdout.log` / `.exit`、`…-recheck-selftest-r3.stdout.log`
- 事实：`git ls-tree -r HEAD -- verification/P02/` 中**只有 r5（validation）与 r4（selftest）存在**；上述 r4/r3 日志仅存在于工作区、**untracked**，`git show HEAD:<path>` 报 path not in commit。同一提交内 `REBASELINE_PLAN.md:7`、`STATUS.md:9`、`P02.md:92`、`r8-candidate:8` 却指向 r5/r4。
- 影响：F-01/F-07 的闭合声明在交付物中**不可复现**——在非本 worktree 的干净 checkout 中这些链接为死链。三个被引文件的 exit 均为 0（磁盘上可直接读；r5/r4 日志内容一致），故不影响结论正确性，只影响证据可追溯性与内部一致。
- 最小修复：把上述 5 处引用统一改为已提交的 `r2-manifest-artifact-validation-r5.stdout.log` / `.exit` 与 `r2-manifest-recheck-selftest-r4.stdout.log` / `.exit`（或反之，将 r4/r3 纳入提交并回退另 4 处）。

**P2-B — `P02.md` 对 R1 脚本标记的字面陈述与文件内容不符**
- 路径/行号：`doc/tasks/P02.md:90`（"R1 invalid partial 已在目录 README 和脚本头部标为 `NOT_GATE_EVIDENCE`"）对照 `verification/P02/codex-smoke-prestart-manifest-r1.py:2-3`
- 事实：脚本头部实际为 `# INVALID_PARTIAL_HISTORY: …` / `# Never treat R1 records as R2 or Gate evidence; …`，**不含字面串 `NOT_GATE_EVIDENCE`**；该字面串只出现在 `smoke-prestart-manifests-r1/README.md:3`。R7 F-06 的 r1 侧最小修复要求是"同义声明"（语义已满足），但 Task 现在对"脚本头部"作了过强的事实断言。
- 影响：文档对自身证据的精确性断言不成立（治理文档事实一致性问题），不影响 R1 无效性判定。
- 最小修复：`r1.py` 头部加 `NOT_GATE_EVIDENCE` 字面串，或把 `P02.md:90` 改为"目录 README 标为 `NOT_GATE_EVIDENCE`，脚本头部标为无效历史"。

**P3-C — INDEX 丢失了 gate 状态汇总行**
- 路径/行号：`doc/00_INDEX.md:5`（对照 base 同位）
- 事实：base `INDEX:5` 末尾有 "Smoke=`NOT_RUN`；完整 preflight=`BLOCKED / INCOMPLETE`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`"；HEAD 该句被删除（`git grep` 在 HEAD 的 INDEX 中零命中）。同一提交的 `PLAN:9`、`STATUS:11`、`P02.md:91` 仍完整保留。
- 影响：入口文档不再自明地显示硬屏障仍有效，属摘要信息回退（其余三文档齐备，故未升级为 P2）。
- 最小修复：在 `INDEX:5` 恢复该 gate 句，或明确以链接指向 `STATUS` 的 gate 段。

**P3-D — F-05 深度披露未替换（12-root/11-mapping 桥接的一半）**
- 路径/行号：`verification/P02/codex-checkpoint-p02-smoke-prestart-r2-delivery.md:8`（对照 base `:8`）、`doc/tasks/P02.md:88`
- 事实：base `delivery:8` 的 "Four small roots … Six large toolchain roots record full path/type/size trees plus `33` selected … remaining file bytes are explicitly `not_computed`" 被整段替换为计数句；新句只说明"2 个 Build-only Git 根不属于 Smoke XML"与"50,356 文件全量哈希/33 选样/138,947 未计算"，**未说明 12 根中仍各有 metadata-only 根**（`P02.md:88` 亦仅给 12/12 + root-level reparse=0）。
- 影响：读者仍可能把 12/12 roots 的存在性/根级检查读成"12 根均已递归覆盖"——正是 R7 指出的误读路径。
- 最小修复：在 `delivery:8` 或 `P02.md:88/90` 补一句"12-root inventory 仅覆盖根存在性与 root-level reparse；Smoke XML 的 11 个映射才做递归 manifest，其中 6 个工具链根为 metadata-only"。

**P3-E — `check.py` 未关闭文件句柄**
- 路径/行号：`verification/P02/codex-smoke-prestart-manifest-check.py:63`、`:84`、`:174`
- 事实：`open(...).read()` 与 `sha256(open(__file__,"rb").read())` 未用上下文管理器；CPython 引用计数下可回收，但属资源管理瑕疵。
- 影响：无功能影响；仅在实现被扩展/长期驻留时可能累积句柄。
- 最小修复：改用 `with open(...) as stream:`。

**P3-F — synthetic 自检只覆盖核心判决单一路径**
- 路径/行号：`verification/P02/codex-smoke-prestart-manifest-check-selftest.py:19-40`
- 事实：mismatch 情形仅篡改 mapping 1 的 `records_sha256`；未覆盖"仅 `records_count`/`status`/`issues` 变化"等非哈希字段分支，也未断言 `verify_clone` 被跳过的事实（`:16` 是 monkey-patch）。
- 影响：核心判决（记录集同一性 + fail closed）确已闭合；但若将来有人误删 `fields` 元组中的非哈希字段，自检不会报警。
- 最小修复：对 `records_count`/`status`/`issues` 各加一条 mismatch 断言。

## 未验证 / 未运行（不写成 PASS）
**我实际运行（只读）**：`git rev-parse HEAD` / `HEAD^{tree}` / `worktree list` / `status` / `diff --stat|--name-only` / `ls-tree` / `show` / `grep -n`；`Get-FileHash` 计算 3 个脚本 SHA-256；**`python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check.py validate` → PASS，EXIT=0（输出与 r5 日志逐字段一致）**；**`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` → 7 项全 PASS，EXIT=0**。

**我未运行（一律不是我的 PASS）**：
- **未运行 `recheck`**，未调用任何 scanner 对真实路径的扫描；未读取/枚举/扫描/哈希任何 HostFolder 内容（`C:\P02\**`、`G:\CODEX\P02-scratch-build-source`、Python/Node/Rust/VS/Windows-Kits 根均未触碰）。
- 未启动 `wsb`/Windows Sandbox、任何 guest command、`@oai/sky`；未运行 Build、runner、Vitest、GUI、真实 WebView、Cargo、产品测试。
- 未验证交付中"author 侧已跑"的 route validator/source-compile/diff-check 日志之外的新运行；未复核作者 Stage-1 宿主测量（CIM/AppX、`wsb` identity、cores/RAM/磁盘、SID、203/203 root manifest、digest）、clone 的 HEAD/tree/porcelain/hardlink/EOL pins。
- 未验证 `recheck` 在真实宿主上的行为与其耗时/IO 影响；`HostFolder compare` 在交付中本就标记为 NOT_RUN，本次维持 NOT_RUN。
- 门状态按现状采信为待验证：Smoke=`NOT_RUN`、完整 preflight=`BLOCKED / INCOMPLETE`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`。

## 建议下一步
由 Codex 在同一分支追加一个纯文档/引用修复 commit（最小范围：统一 5 处 r4/r3 → r5/r4 引用、修正 `P02.md:90` 的 R1 标记陈述、恢复 `INDEX:5` 的 gate 句、补 12-root 深度披露句，可一并修 P3-E/F），重新固定 Delivery HEAD/tree 后派发 DSH exact-head 复审。复审 approved 且所有立即 pre-start 检查（含尚未运行的只读 HostFolder recheck、新采集的 `@oai/sky` 输出）全 PASS 前，不得运行 `wsb start`；Smoke 不通过 Build Gate。
