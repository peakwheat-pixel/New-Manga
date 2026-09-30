# DOC-FIX-LOCK-CHANGED-STALE-COMMENTS 独立非作者 Review **r2**（DeepSeek Harness）

**decision：准予集成（approved）** — 0×P0、0×P1；**P2-1 / P2-2 均判定 closed**；新增 3×P3（N-1～N-3）+ 8×P4，全部属集成记录/导航面收口，不构成集成前置阻塞。

**审查方式声明（严格只读）**：本轮未修改任何文件、未执行任何命令。`pwsh` 本次三度被沙箱拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\DOC-FIX-STALE-COMMENTS-zcode)`；随后按规则做的一次 `danger-full-access` 提权重试被「requires approval, but no approval channel is available」拒绝）。因此凡需实际复算的数值（`sha256`、`co_code`、`EXIT`）一律标 `not_verified` 并给出集成方一条命令的闭合条件；结构/口径/链路类事实由我独立读取文件与 Git 元数据（只读）核实。

**reviewed_head 声明（重要，见 N-1）**：分支 ref `agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS` 的真实值 = **`8b00d1995cf41cefca75cf887427a5021372327f`**（独立读取 `G:\CODEX\New Manga\.git\refs\heads\agent\zcode\DOC-FIX-LOCK-CHANGED-STALE-COMMENTS`）。派发口径所称「返修 commit 928b881d（当前 tip）」中，`928b881d` 是 `8b00d199` 的直接父（reflog 独立证据）。下文对两者结论一致：`8b00d199` 相对 `928b881d` 仅多一个「import DSH non-author r1」提交，落点为 `doc/reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-768a0933-dsh-r1.md`，属 Task:42 允许路径 `doc/reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-*`。

**独立 Git 元数据证据**（`G:\CODEX\New Manga\.git\worktrees\DOC-FIX-STALE-COMMENTS-zcode\logs\HEAD`）：
`4ed3c044`(release/reset) → `74022cdc`(claim) → `65f0facb`(fix 两处注释) → `1dd30dc7`(handoff) → `768a0933`(evidence: whitespace-only normalization = r1 被审 tip) → **`928b881d`**(repair r2: DSH P2-1 provenance-note + wording limits, P2-2 probe script in-repo + r2 log with header/EXIT + instruction-stream claim scope, P3-1/2/3/6 metadata & scope-r2 & AC1 disclosure) → **`8b00d199`**(review: import DSH non-author r1 @ tip 768a0933)。

---

## 一、声称闭合项逐条判定

### P2-1 — provenance 锚定失效表述未限定 —— **closed**（数值层 not_verified；附 N-3）
**依据（独立核实）**：
1. 新证据 `verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/00-provenance-note.txt` 存在（32 行），`§M2-TA3-A provenance manifest 的字节级影响（P2-1）`:7-13 写实新旧 sha256（run_smoke.py `f1b5976d…`→`30d55acd…`；acceptance_bridge.py `b2d7b86e…`→`3e4b1fd1…`，两值均为 64 位 hex，格式合规）。
2. **旧值锚点经我逐字核对成立**：note:8/11 的 `f1b5976de517290a294b7ea3b0c804e59c87f45b610ed9d8f4a047ce8c4850d9` 与 `verification/M2-TA3-A/raw/00-provenance.txt:18` 的清单行逐字一致 ⇒ note 的「改前 = manifest 所钉值」锚定正确。
3. **计数与范围声明经我核对成立**：`M2-TA3-A/raw/00-provenance.txt:18-32` 恰为 15 条清单行 ⇒ note:21 的「15/15 → 14/15」预测计数正确；该清单内确无 `acceptance_bridge.py` ⇒ note:13 括注（「该文件不在 M2-TA3-A manifest 内」）正确。
4. **口径限定已替换过强表述**：`doc/tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md:29` 已改为「dc2b9aca pin 仍为有效历史标识、行为等价由 AC1/AC2 支撑；但 M2-TA3-A provenance 的**字节级 sha256 自检在 main/tip 上不再全绿**……须在 M2-TA3-A 交付 worktree 复算字节级 15/15」，并指向新 note；`doc/handoffs/…-delivery-20260930.md:21` 同口径重写（含 `f1b5976d…`→`30d55acd…`、一行 FAILED 属预期）⇒ 与 r1 建议 (a)(b) 逐条对应。
5. note:17-19 与 Task:29/Handoff:21 三方口径一致（行为等价由 AC1+AC2 支撑、历史 pin 有效、字节自检退化属预期），未再出现「不受注释演进影响」的绝对句（该句已从两处文档消失）。

**not_verified**：`30d55acd…`/`3e4b1fd1…` 两个新值与「tip 工作区字节」的对应无法由我执行复算（沙箱拒绝执行）。闭合条件（集成 gate 一条命令）：
```bash
git show 4ed3c044:experiments/M2-TA3-A/run_smoke.py | sha256sum   # 期望 f1b5976d…
sha256sum experiments/M2-TA3-A/run_smoke.py                      # 期望 30d55acd…
git show 4ed3c044:src/bootstrap/acceptance_bridge.py | sha256sum # 期望 b2d7b86e…
sha256sum src/bootstrap/acceptance_bridge.py                     # 期望 3e4b1fd1…
```

### P2-2 — 探针不可复现 + 「零逻辑变化」措辞过强 —— **closed**（附 P3-7/N-2）
**依据（独立核实）**：
1. **探针脚本已入库且可复现要素齐全**：`verification/…/raw/bytecode_probe.py`（64 行）。docstring:7-12 明示 claim scope ——「proves instruction-stream (`co_code`) equality only」，并逐项声明盲区 `co_consts`（含「where this task's docstring change legitimately lives」的预期差异声明）/`co_names`/`co_varnames`/`co_linetable`·`co_firstlineno`（「both files net +2 lines」）/exception tables，并写明「完整零逻辑证明 = AC1 的 human-readable diff TOGETHER with this probe」；:14-16 给出 usage 与 Exit 语义。这正是 r1 建议的三个动作合一。
2. **r1 影响①的根因已闭合**：脚本:22 `BASE = "4ed3c044"`、:39-41 `subprocess.run(["git","show",f"{BASE}:{rel}"], check=True)` —— 改前 blob 的取得方式由「未记录」变为**代码内自明**（`git show`，非副本），「不存在内嵌脚本」的问题不再存在。
3. **失败处理与覆盖率逻辑经我静态审读成立**：code object 仅存活于 `co_consts`，:29-33 的递归即完整闭包；:48-52 集合不等时打印对称差并 `overall=False`；:53-57 逐对象 diff 判定；:58-60 结论行 + 返回码 0/1。不存在「对象数不等仍报 ALL-EQUAL」的静默通过路径。
4. **r2 log 取证规格已对齐同 Task 其余证据**：`ac2-bytecode-probe-r2.log:1` 含 shell / interpreter / worktree HEAD / 完整 cmd，:2-4 输出 `objects=37`、`objects=15`、`ALL-EQUAL (instruction stream unchanged)`，:5 `EXIT=0`；`37+15=52` 与 Task:34、Handoff:19 三处数字一致 ⇒ 规格与 `ac1-…log:1,37`、`ac2-acceptance-regression.log:1,4` 持平。
5. **措辞限定已落实**：Task:34 AC2 标题改为「**指令流零变化的机器证据；DSH P2-2 限定口径**」并写明「探针**只证明指令流零变化**……完整零逻辑结论=AC1 注释-only diff 与本探针**共同**支撑」；Handoff:19 同口径；初版 `ac2-bytecode-probe.log`（3 行）保留不删，Task:34 明示其为 inline 探针、结论与 r2 一致 ⇒ 与 r1 建议 (b) 逐字对应。

**残留（不改变 closed 判定）**：
- **P3-7（新）**：`Handoff:50` 命令表仍写「字节码探针（compile+递归 co_code 对比，**见 ac2 log 头部内嵌脚本**）」—— 这正是 r1 P2-2 影响①的原始误导句，未改指入库脚本 `bytecode_probe.py`。因 Handoff:19 与启动/复现方式 `:65` 已正确指向入库脚本、且脚本本体已在仓库可读，误导面已大幅收窄，故判「closing 残留」而非 not-closed。
- **P4（新）**：`Handoff:40` AC 对照表、`Task:54` 测试表、`Task:36` AC4 行的证据链接仍只指初版/旧 log，r2 log 与脚本未挂全。
- **not_verified**：`objects=37/15` 与 `ALL-EQUAL` 的**数值**仍为 Owner 运行结果（我未能执行）。另 `ac2-bytecode-probe-r2.log:1` 记录的运行点是 `768a0933`（返修提交之前）——基准为 `git show 4ed3c044` vs 工作区文件，且 `ac4-scope-proof-r2.log:5-10` 显示当时工作区除 4 个新证据文件外无未提交改动、产品面已提交，故 r2 log 对返修 tip 的效力可维持（时点已在 Handoff:33 披露）。集成方如要求 tip 级复跑，一条命令即可：`"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/bytecode_probe.py`。

### P3-1 — Task `status`/`delivery_head` —— **closed**（附 P4）
**依据**：`doc/tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md:5` = `status: in_review` ✓；`:16` = `delivery_head: 768a0933 (r1 被审 tip；本轮 DSH 条件返修后由集成方回填终 tip)` ✓，与 r1 建议（`status: in_review`、`delivery_head: 768a0933`）逐字一致；`:67` 的转态声明与 frontmatter 不再互斥。
**P4**：`:16` 的 768a0933 未含 `928b881d`/`8b00d199`（措辞已由「集成方回填终 tip」兜底）；`§交付与运行记录`（:66-68）未登记返修轮次与 `928b881d`。

### P3-2 — Handoff 提交链与真实链路不符 —— **closed**（附 P4）
**依据**：`Handoff:23-31` 提交链表已按 reflog 写实四行：`74022cdc`(claim) / `65f0facb`(实现+AC1-AC4 证据) / `1dd30dc7`(Handoff 首版) / `768a0933`(归一化 = r1 被审 tip)，我以 reflog 逐行比对**全部命中**；`:33` 新增证据捕获时点披露（「各 log 的 shell 头记录 `worktree @ 74022cdc`（实现后、提交前）；提交链随后成型」）与 `ac1-…log:1`（@74022cdc）、`ac2-acceptance-regression.log:1`（@74022cdc）、两 r2 log（@768a0933）的实际值一致 ⇒ 满足 r1 建议。
**P4**：`Handoff:6` frontmatter `delivery_head: 74022cdc + 本 Handoff 文档提交（实现/证据见 worktree tip）` 未同步真实链；`:31` 的返修行只写「（本轮）」无 hash（`928b881d`）。

### P3-3 — AC4 未枚举实际变更文件 —— **closed**（附 P4）
**依据**：`verification/…/raw/ac4-scope-proof-r2.log` 补齐 r1 所要求的两件：`:2-3` `git rev-parse HEAD`（=768a0933，绑定记录点）、`:5-9` **未过滤** `git status --porcelain`（4 条 `??`，与本轮实际新增文件一一对应）、`:12-20` **未过滤** `git diff --name-status 4ed3c044..HEAD`（8 行全量：`M` 2 个产品文件 + `M` Task + `A` Handoff + `A` 4 个证据 log）、`:23-24` `git diff --check` EXIT=0。范围纪律经我侧旁证一致：`verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/` 下恰为 9 个文件（release 1 + raw 8 = 原 5 + 本轮 4），**零多余产物**；`doc/reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-*` 恰 1 个（r1 报告），无越权改写迹象。
**P4**：该 log 的 range 端点是 `768a0933`（返修前 tip），返修新增的 4 个文件当时以 `??` 形式出现在 porcelain 中而非 range 的 `A` 行 —— 变更集合在 log 内完整（8 + 4），但 `Handoff:33`「r2（tip 全量未过滤枚举）」的「全量」略夸；`ac4-scope-proof-r2.log:10` 的 `(empty = clean)` 注释紧跟 4 行非空输出，易被误读（见 N-5）。

### P3-6 — AC1 原始捕获未留存 —— **closed**
**依据**：`00-provenance-note.txt:27-32` §AC1 原始捕获披露写实：「`ac1-comment-only-diff.log` 为 whitespace-only 归一化副本（文件内已披露）；**原始捕获未单独留存、已不可得**。归一化仅压平 raw `git diff` 上下文空行的行尾空白，未增删任何 diff 内容行」+ 引用 r1 的 tip 字节独立复核结论 ⇒ 这正是 r1 建议的「否则在附注中写实『原始捕获已不可得，仅披露』」分支；`ac1-comment-only-diff.log:39` 的 in-file 披露保留未删。

### 未声称闭合的 r1 项（保持原级、不阻塞）
- **P3-4**（`run_smoke.py:303` 同类第三处注释）：**not-closed（维持 open）**。我复核 `experiments/M2-TA3-A/run_smoke.py:303` 仍为 `# Known planner gap: region-less backfill chain (M2-AC1 handoff).`；`doc/tasks/M2-TA3-A.md:125` 的 L-7 仍为 ①②③ 三项，未加 ④；`:305` 的证据键字面量未动 ✓（符合 r1 的「不得改名」）。→ 由集成记录登记 L-7 ④（Owner 未声称，r1 亦指派集成记录）。
- **P3-5**（`page-level chain` 措辞）：**not-closed（维持 open，低危）**。`run_smoke.py:273` 仍含「real detect; page-level chain; …」，未附 primary-region 限定。→ 集成记录或后续文本轮收口。
- **P4-3**（DIAG-002 重复键）：仍在（`doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md:15` 与 `:17` 两条 `integration_commit:`）。
- **P4-4**（`doc/tasks/README.md:7`）：仍写「当前无 `in_progress`/`ready` Task」，与本 Task 存续冲突；导航面属 Codex 职责。

---

## 二、新发现问题（N 系列）

- **N-1（P3）——被审 tip 口径错位**：分支 ref 实为 `8b00d199`，派发/Owner 口径称「当前 tip = 928b881d」。`8b00d199` 的 reflog 消息为「review(DOC-FIX-STALE): import DSH non-author r1 (approved_with_conditions …) at tip 768a0933」，落点 `doc/reviews/…-768a0933-dsh-r1.md`（允许路径）。影响：Reviewed-HEAD 绑定与集成记录的 head 可能不一致。建议：集成记录明确写 `reviewed_head = 8b00d199`（或声明 reviewed=`928b881d` 且 `8b00d199` 为纯文档导入）。**not_verified**：`8b00d199` 的 tree 是否**仅**新增该文件，我无法以 git 枚举（沙箱拒绝执行）——集成 gate 用 `git show --stat 8b00d199` 一次即可确认。
- **N-2（P3，新）——探针 key 命名碰撞**：`bytecode_probe.py:30` 以 `prefix + code.co_name` 为键、:46-47 转 `dict`，同一父 code object 下多个同名嵌套对象（如多个 `<lambda>`、多层同名内嵌 `def`）会互相覆盖 ⇒ `objects=37/15` 可能低于真实 code object 总数、比较面可能出现漏项。本 Task 未引入新命名碰撞、base/new 两侧规则相同，故对本次「全等」结论的判别力影响有限。建议：改用索引路径（如 `parent#i.name`）或对 `len(map)` 与递归计数一致加断言。
- **N-3（P4，新）——字节基准混用**：note:11「改前（base 4ed3c044 **blob**，即 manifest 所钉值）」用 blob（LF）字节，note:12「改后（**本 Task tip 工作区**）」用工作区字节；若该 worktree 检出为 CRLF，两者基准不一致，`sha256sum -c` 的「仅一行 FAILED」预测会失真。`M2-TA3-A/raw/00-provenance.txt:14-15` 已提示 autocrlf 风险，建议集成复算统一以 `git show`（两版 blob）为基准，或在 note 中标注字节基准。同段 note:20「在 **main/tip** 上……FAILED」在集成前对 main 不成立（main 仍是 `f1b5976d…`，15/15 全绿），且与 note:22-24「预期验证环境 = 交付 worktree」轻微张力 —— 建议集成记录写「本 Task 集成后」。
- **N-4（P4，新）——P2-2 措辞限定未覆盖全部产出面**：`doc/STATUS.md:14`「零逻辑改动（字节码 co_code 全等证明）」、`verification/…/release-d1c56e5d.md:14`「零逻辑改动为硬约束（字节码 co_code 逐对象全等为集成前置）」、`Task:25`「机器可核的『零逻辑变化』证据」、`Task:54` 结果列「52 code object 全等，ALL-EQUAL」、初版 `ac2-bytecode-probe.log:3`「zero logic change」。其中 release 证据与初版 log 属历史捕获**不应改写**；STATUS/Task 属导航与自述面，建议集成时统一为「指令流（co_code）零变化」，完整结论由 AC1 diff 共同支撑。
- **N-5（P4，新）**：`ac4-scope-proof-r2.log:10` 的 `(empty = clean)` 紧跟在 4 行非空输出之后，语义误导（疑为「若输出为空即干净」的模板残留），建议集成时不改原文而在记录中加一行解读。
- **N-6（P4，新）**：探针 docstring 的盲区清单未包含 `co_freevars`/`co_cellvars`（r1 曾列举），可在探针注释内补全（不影响结论）。

---

## 三、方法有效性重估（r1 复核点 (4) 的 r2 答复）

`co_code` 全等仍**不是**「零逻辑变化」的充分证明（`co_consts` 变 `"completed"→"failed"` 时 `co_code` 可逐字节相同），但 r2 的处置已把该局限从「隐性过强断言」转为**显式声明的 claim scope**：Task AC2 / Handoff §AC2 均写「只证指令流零变化」，探针 docstring 亦列出盲区与预期差异，并明确完整结论由 AC1（我已于 r1 用 tip 字节独立核对 `+`/`-` 两侧）与探针**共同**支撑。我本轮再次静态核对：`src/bootstrap/acceptance_bridge.py:337-343` 与 `experiments/M2-TA3-A/run_smoke.py:273-275` 的当前字节与 `ac1-comment-only-diff.log:12-14,29-33` 的 `+` 侧逐字一致 ⇒ 返修轮**未再触碰产品文件**，r2 log 的时点问题不改变交付内容。方法层面结论：**部分充分、已诚实限定**，作为旁证可用，作为唯一证明不可用。

---

## 四、集成前/集成时收口清单（全部非阻塞）

1. 复算 sha256（N-3 注意统一 LF/blob 基准）与重跑探针（`bytecode_probe.py`，期望 `EXIT=0`、52 全等）；跑一次 `git show --stat 8b00d199`（N-1）。
2. 明确并记录 `reviewed_head`（`8b00d199` 或 `928b881d` + 导入说明）；回填 Task `delivery_head` 终值与 `§交付与运行记录` 返修轮（`928b881d`/`8b00d199`）；同步 `Handoff:6` frontmatter 与 `:31` 的 hash。
3. 清理 `Handoff:50`「见 ac2 log 头部内嵌脚本」（P3-7）；把 `Handoff:40`、`Task:36`、`Task:54` 的证据链接升级为 `bytecode_probe.py`/`ac2-bytecode-probe-r2.log`/`ac4-scope-proof-r2.log`（P4）。
4. 按 P2-2 口径回填 `STATUS:14` 与 `Task:25`/`Task:54` 的过强措辞（N-4）；release 证据与初版 log 保持原文不动。
5. 集成记录登记 L-7 ④（`run_smoke.py:303`，P3-4）、`page-level chain` 措辞（P3-5）、行号整体 +2 换算注（P4-1）、DIAG-002 重复键（P4-3）、`tasks/README.md:7`（P4-4）、`ac4-scope-proof-r2.log:10` 注释解读（N-5）。

---

## 五、结论

**Architecture**：无（不触分层/契约/依赖/持久化）。
**Verification**：AC1 r1 已 verified（tip 字节逐字一致，本轮复核对返修后字节仍成立）；AC2③ `4 passed EXIT=0` verified（规格合规，Owner 运行结果）；**AC2①② 的 r1 阻塞项（脚本零命中/无头无 EXIT/措辞过强）已闭合为「可复现 + 显式 claim scope」**；AC3 verified（口径限定后）；AC4 范围枚举已补齐（closed，附 P4）。
**条件闭合**：r1 的两条合并前条件 **P2-1 = closed、P2-2 = closed**；P3-1/P3-2/P3-3/P3-6 = closed（各带 P4 残留）。无 P0/P1，无 not-closed 的 P2。

⇒ **准予集成**。请 Codex 按 §四 清单在集成记录/导航回填时一次性收口；其中 P3-4、P3-5、P3-7、N-1～N-6 均不影响本次两处注释修正的交付正确性。归档说明：按本轮派发要求「输出全文到 stdout、不修改任何文件」，本报告未落盘 `doc/reviews/`；如需归档，由 Codex 以 `doc/reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-<reviewed_head>-dsh-r2.md` 落盘即可（内容以本文件为准）。

**推荐下一步（基于当前仓库状态）**：由代行 Codex 执行集成——在 `agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS`（tip `8b00d199`）上先跑 §四第 1 条的 sha256/探针复算，再以 `--no-ff` 合并并在集成记录一次性收口 §四第 2～5 条；无需其它新 Task，无需用户裁决。
