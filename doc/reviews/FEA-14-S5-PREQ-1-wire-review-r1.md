---
task_id: FEA-14-S5-PREQ-1
reviewer: fresh 独立上下文子 agent（由 Lead 派发；未参与本卡写作/实现）
reviewer_kind: subagent
author: dsh
base_commit: b7aaccfbc
reviewed_head: b7aaccfbc + 未提交工作树（AC2/AC3 契约产物，见 §0 字节锚）
decision: changes_requested
---

# Review：FEA-14-S5-PREQ-1 AC2/AC3 契约产物（wire r1）

## 0. 审查对象、环境与字节锚

- 仓库：`G:\CODEX\New Manga`，`main`。**HEAD = `b7aaccfbc3290eb0ac29902834e4054404925f30`**（工作树在审查期间保持同一 HEAD）。
- **重要环境事实**：AC2/AC3 的契约产物**尚未提交**，全部位于工作树：3 个已跟踪修改 + 3 个未跟踪新文档（`git status --porcelain` 实测，审查开始 `2026-11-10T09:29:03+08:00` / 结束 `09:39:50+08:00` 一致）：
  - `M doc/plan/FEA-C07_API_INVENTORY.md`（diff：35 增 / 1 删）
  - `M doc/plan/FEA-CONTRACT-FROZEN-C07.md`（diff：9 增 / 7 删）
  - `M doc/tasks/FEA-14-S5-PREQ-1.md`（diff：+1 allowed_paths 行）
  - `?? doc/reviews/FEA-14-S5-PREQ-1-wire-r1.md`
  - `?? doc/reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md`
  - `?? doc/reviews/ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES.md`
- 本报告判定所依据的**被审字节**（SHA-256，工作树口径）：
  - inventory `c67c40e72938ac3d5284d778758a17e66f65d760c38e2aa7c6da548a79f47550`
  - frozen C07 `ed9719eefa4d057a40a3e17900de7074a23b94ecd941937278c2a4e0a5fa550d`
  - wire-r1 `a359e128b202f9466e19528e5672b9b131828b8d06779fe67cbce62cf198f5af`
  - UNFREEZE `f7b5da714886b2f705eeffe4e0b594d8dca489c5d4d650ac7371ee1128b69894`
  - NEW-DATA ADJ `9b885078b5b3dc1a80e57420f46ee78c7deda789224dc3f70ed9e249dc76cc8b`
  - card `2827466720debd5b5877f3220bb1be239f27e6e7556ff27a9f71bf33a3ebb191`
  - FEA-15（AC1 注记，已提交）`0e566832b7ff27d87e43fe0190e0f928f722067197f4c1925f77c47929aced3a`
- 只读纪律：本审查仅写本文件；未改生产源码/契约/卡面/证据，未 commit/push；临时日志/脚本仅写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-S5-PREQ-1-r1\`。

## 1. 结论

**`changes_requested`。**

| 计数 | 值 | 主要载体 |
|---|---|---|
| P0 | **0** | 无数据损坏、无冻结字节被错改、pin 正确 |
| P1 | **1** | AC2 wire 契约包缺 `minor` 与 `payload 形状`（R-001） |
| P2 | **4** | errata 写域越界（R-002）、errata 无冻结记录锚点（R-003）、prompt_templates 载体/内置模板矛盾（R-004）、fonts 默认包含 vs SC-11「字体可选」未reconcile（R-005） |
| P3 | **5** | 断链、行号引用过期、frozen §5 缺 v1.2 行、logs 证据缺失、C-07 自述与计划节张力 |

实质通过面：C-07 **旧 54 方法/统计表零改动**；新 pin `c67c40e7…` 与 `Get-FileHash`/`verify_pins` 一致，其余 17 pins 不变；25 条计划命令在 inventory 与 wire 文档间**逐条一致**（4/4/7/5/5=25，54→79、61→86 自洽），与现有 61 个成员**无重名**；UNFREEZE 载体要素齐备且代码零改动；errata 未改 C-01b/C-09 冻结字节（0 pin），四类数据的备份/清理/恢复纪律主体已覆盖。门禁全绿（见 §5）。

## 2. 必查项逐项结论

| # | 必查项 | 结论 | 依据 |
|---|---|---|---|
| 1 | 旧签名与统计 | **PASS** | `git diff HEAD -- doc/plan/FEA-C07_API_INVENTORY.md` = 35 增 / 1 删：唯一删除是状态行旧文案，新增为「S5 计划追加」节；旧 `IReaderProgressSink`（1）、`IHostController`（54）、`IRunController`（6）成员表与统计表逐行未变（审查脚本对 HEAD 与工作树逐表比对相等）。`python tools/generate_api_inventory.py --check` **EXIT 0**，代码实测 **1/54/6 = 61**；脚本 stdout 成员集合与文档旧表**集合相等**（见 R-010 关于既有顺序差异的说明） |
| 2 | pin 正确性 | **PASS** | `Get-FileHash doc/plan/FEA-C07_API_INVENTORY.md -Algorithm SHA256` = `c67c40e72938ac3d5284d778758a17e66f65d760c38e2aa7c6da548a79f47550`，与 frozen §1 新 pin、UNFREEZE §1 新 pin 完全一致；冻结记录**保留前 pin** `3fdb44e49afe…`（§1 第 16 行）。`verify_pins.ps1` **EXIT 0 / PIN AUDIT: PASS (all 18)**；C07 = `c67c40e72938`，其余 17 项与 FEA-14-SET-1 最终证据逐项相同 |
| 3 | UNFREEZE 合规 | **PASS（复核结果待回填）** | 载体 §1 旧/新 pin、变更范围、代码零改动；§3 五条不变量；§4 独立复核要求；§5 复核记录（当前「待复核」）；§6 不构成什么；§2 + frozen §3 第 44 行明确计划节落地规则（并入正式成员表、重跑脚本、重算统计/pin）。本报告即独立复核输入；Lead 须把结论回填载体 §5 与 frozen §1B 后再提交 |
| 4 | wire 清单完整性 | **PARTIAL（R-001）** | 25 条完整覆盖五切片（FONT 4 / LIB 4 / READ 7 / EDIT 5 / AI 5），名称/返回类型/语义与现有 `IHostController` 风格一致，与现有 54+6+1 成员无重名，inventory 计划表与 wire 文档逐条一致，统计 54+25=79、61+25=86 自洽。**但 AC2 原文要求的 `minor` 与 `payload 形状` 缺失**：wire §1.4（第 12 行）明确「参数以代码为权威，本清单只锁名称/返回类型/语义」；全文无 `minor`/协议版本；亦未登记 25 条命令对应的 Core wire 命令名/域/每命令 minor（现有约定见 `HostCommandRegistry.cs:270-271,294-296`：默认 minor 3、P15 settings 7、DELETE 10） |
| 5 | errata 0 pin | **PARTIAL（R-004/R-005）** | C-01b/C-09 草案**零字节改动**（`git status` 无这两个文件；pins C01b `3c9f5af7d74f`、C09 `dc51226b336c` 不变）；四类数据均有备份/清理/恢复条目；§4 明确「若需改冻结文本/语义须另走 UNFREEZE」。**但** `prompt_templates` 载体/内置模板矛盾（R-004），`fonts/` 默认包含与 C-01b SC-11「字体为独立可选项」未 reconcile（R-005） |
| 6 | 范围 | **PARTIAL（R-002）** | 无 `src/**`/`apps/**`/`schema.py`/DDL diff；`git status` 6 项中 5 项在 allowed_paths，**`doc/reviews/ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES.md` 不在**（见 R-002）；卡 AC6 的 `git diff --name-only` 不覆盖 untracked，无法自证 AC3 载体在范围内 |
| 7 | 文档事实一致性 | **PARTIAL** | C-01b `:53-54`（SC-10a/10b）、C-09 `:24-48`（SC-B01/SC-B01a）、`cleanup.py:41 CACHE_SAFE_PREFIXES=("cache/",)`、先例 `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT` 均实测存在且口径相符；但存在断链（R-006）、过期行号（R-007）、frozen §5 缺 v1.2 行（R-008） |

## 3. Findings

| ID | 级别 | 位置 | 事实与影响 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `doc/reviews/FEA-14-S5-PREQ-1-wire-r1.md:12`（及全文）；`doc/tasks/FEA-14-S5-PREQ-1.md:62`（AC2） | **AC2 要求「各自命令、域、minor、payload 形状」落盘，产物只给了命令/域/返回类型/语义**：§1.4 显式把参数交给代码，全文无 `minor`、无 per-command payload 形状、无 Core wire 命令名/域注册。后果：(a) AC2 无法如实标 MET；(b) wire §1 又要求「实现卡只消费本清单，不得再扩 wire」，与本清单未锁 Core wire/payload/minor 矛盾——各实现卡落地时仍需自行定义 Core 命令与 minor/payload，PREQ「一次冻结共用 wire」的目标只覆盖了 App 端口名，未覆盖真正的 wire 面；(c) 5 个切片仍可能各自扩张 wire，五次 UNFREEZE 规避只对 C-07 有效。 | 卡 AC2 `:62`；wire `:12`；`HostCommandRegistry.cs:270-271,294-296`（per-command minor 3/7/10 与 payload probe 先例）；inventory 计划节 `:102-134` 仅名称/返回/切片/语义 | 二选一（建议 a）：(a) 在 wire 文档新增「wire 版本与 payload 口径」节 + 每命令列（Core 命令名、per-command minor、请求 payload 形状/参数名），并说明是否需 C-04b/C-16/C-17 类登记；(b) 由 DSH 记录范围裁决：本轮「wire」= App 端口名称/域/返回/语义，Core wire minor/payload 由各实现卡按既有 minor 约定处理——并同步修改 AC2 文本/卡面（不得沉默降级） | open |
| R-002 | **P2** | `doc/reviews/ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES.md`（新文件，SHA-256 `9b8850…`）；卡 `:21-33` allowed_paths | **AC3 载体越出冻结写域**：6 个改动中唯一 OUT = 该 errata 文件；allowed_paths 只有 `doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md`（精确名）、`FEA-14-S5-PREQ-1-*.md`、`CONTRACT-UNFREEZE-*.md`，均不匹配 `ADJ-2026-11-10-FEA14-NEW-DATA-CATEGORIES.md`。AC6（卡 `:66`）已标 MET「diff ⊆ allowed_paths」，但其检查命令 `git diff --name-only` 不含未跟踪文件，无法覆盖本载体；整体变更集（含 untracked）并不满足 AC6。 | `git status --porcelain` + 逐条 pattern 匹配（5 IN / 1 OUT）；卡 `:21-33,:66` | 卡面 allowed_paths 增加该 errata 精确路径（或允许 `doc/reviews/ADJ-2026-11-10-FEA14-*` 模式）；或把 errata 并入 allowed 的既有文件；随后重跑 AC6 范围检查（含 untracked） | open |
| R-003 | **P2** | 卡 `:63`（AC3）、`:74`（交付物 #3）；`doc/plan/FEA-CONTRACT-FROZEN-C01b.md`、`doc/plan/FEA-CONTRACT-FROZEN-C09.md`；`ADJ-…NEW-DATA-CATEGORIES.md:63-68` | **errata 无冻结记录锚点、无任何索引引用**：先例 `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT` §4（`:41-42`）要求「在 `FEA-CONTRACT-FROZEN-C09.md` 追加 §8 errata、在 `FEA-CONTRACT-FROZEN-C01b.md` 追加 errata 注记」；本次 errata 未在任一冻结记录追加，`rg NEW-DATA-CATEGORIES` 除自引用外**零命中**（卡/scope ADJ/冻结记录均无指针）；卡交付物 #3 写「C-01b/C-09 冻结文档 append-only 段 + 本卡记录」，与实际载体（独立 ADJ 文件）不符。影响：C-01b/C-09 的读者无法从契约记录发现该 errata，可追溯性不闭合。 | 先例 §4 `:41-42`；`rg` 仅命中 errata 自身 `:2,:65`；卡 `:74`；两份 frozen 记录 `rg errata` 仅见 2026-11-09 FEA-13 条目 | 0 pin 方式补齐：在 `FEA-CONTRACT-FROZEN-C01b.md`/`-C09.md` 追加 append-only errata 注记（不碰草案字节、不重算 pin），并把这两个路径与 ADJ 文件加入 allowed_paths；或由 DSH 明确裁决「独立 ADJ 文件即载体，优于先例」并写进卡面交付物 + 冻结记录指针 + scope ADJ | open |
| R-004 | **P2** | `ADJ-…NEW-DATA-CATEGORIES.md:20-27`（§2 表）、`:37-43`（§3 表）；`doc/plan/…ddl-v10-plan.md:37-44`；`settings-storage-shape.md:23,68` | **`prompt_templates` 载体自相矛盾**：§2 表说「`library.db` 表 **或** 非凭据 settings section」（二选一待 AI-1，与 AC4/AC5 一致）；§3 表却把 `prompt_templates` 与 bookmarks/markers 并列为「**是**（DB 表随 `library.db`）」。若 AI-1 选 settings section，则该行归属错误；且 settings section 分支的**恢复纪律**未覆盖（§3 恢复纪律只写了 DB 表与 `fonts/`）。另内置模板：「内置提示词模板 \| **否**（不备份）」与「`prompt_templates` 表随 `library.db` 入包」冲突——DDL 计划 `:41` 的 `builtin` 列说明内置模板是表内行；整表入包时内置行不可能自动被排除，需明确「恢复时重新 seed/忽略内置行」或「导出时过滤」。 | 三份文档对照；DDL `:41,44`；settings shape `:68` | 把 `prompt_templates` 行拆成「表格（若落库）→ 随 library.db，恢复后按内置只读重建/忽略内置行」与「若落 settings → 非凭据 settings，按 C-09 SC-B01a `:41` 已有归属」；补 settings 分支的恢复/清理纪律；内置模板备份语义与表入包方式对齐 | open |
| R-005 | **P2** | `ADJ-…NEW-DATA-CATEGORIES.md:24,29-33,41`；`doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md:55`（SC-11） | **`fonts/` 默认包含 vs SC-11「字体为独立可选项」未 reconcile**：errata 把数据根 `fonts/` 列为**默认包含**（新增白名单）；C-01b SC-11（`:55`）明写「外部原文件与**字体**为独立可选项，开始前显示预计大小/位置/缺失项」。两种读法均存在：若 SC-11 的「字体」指外部原始字体文件，则与库内副本不冲突；但 errata 未做此边界澄清，实现卡可能把 `fonts/` 当作可选/需预览项，或反过来把外部原字体也默认打包，二者都违反既有条款。 | C-01b `:55`；errata 仅以「外部源文件（漫画原文件）…SC-10a 不变」限定漫画（`:29-33`），未提字体 | 在 errata §2/§3 边界处补一行：外部原始字体文件 = 可选（SC-11 不变，不默认打包）；数据根内 `fonts/` 副本 + `font_assets` 条 = 默认包含（SC-10b）；必要时同步 SC-11 的 errata 注记 | open |
| R-006 | **P3** | `doc/plan/FEA-C07_API_INVENTORY.md:3`、`:104` | **相对链接断链**：从 `doc/plan/` 指向 `[UNFREEZE 载体](reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md)`，实际应为 `../reviews/…`；`doc/plan/reviews/` 不存在（`Test-Path` false）。同目录先例（如 C-16）使用 `../reviews/`。 | 实测 `Test-Path doc/plan/reviews` = False；同文件 `:3,:104` | 两处改为 `../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md` | open |
| R-007 | **P3** | 卡 `:62`；`wire-r1.md:10` | **行号引用过期**：两处写「按 `FEA-CONTRACT-FROZEN-C07.md:42` 在同一 Task 内重跑脚本」；冻结记录第 42 行现为「**下游**：…」，落地规则在第 **43–44 行**（`实现注意`/`v1.2 计划追加节`）。 | 冻结记录逐行实测（41 无上游依赖、42 下游、43 实现注意、44 v1.2 规则） | 改为 `:43`（实现注意）或 `:44`（v1.2 落地规则） | open |
| R-008 | **P3** | `doc/plan/FEA-CONTRACT-FROZEN-C07.md:73-79`（§5） | **§5 变更记录缺 v1.2 行**：§5 现有 2026-11-01 建立、2026-11-01 pin 修正、2026-11-02 v1.0→v1.1 三行；本次 v1.2 UNFREEZE 仅在 §1/§1B/§2/§3 留痕，未按自身惯例追加 v1.2 行（载体/日期/范围/pin 新旧）。 | 文件逐行；v1.1 行的既有格式 | 复核通过后追加 v1.2 行：新 pin、旧 pin、范围（计划节）、载体路径、复核结论 | open |
| R-009 | **P3** | 卡 `:77`（交付物 #6）；`verification/FEA-14-S5-PREQ-1/` | **AC2/AC3 门禁日志未留证**：交付物 #6 要求 `verification/FEA-14-S5-PREQ-1/logs/`，实际目录只有 `ddl-v10-plan.md`、`settings-storage-shape.md`，无 logs；AC6 已标 MET，但没有 AC2/AC3 的 `--check`/`verify_pins`/`check.ps1` 日志可复核（本审查的其实测见 §5，可作输入）。 | `Get-ChildItem -Recurse` 实测；卡 `:77` | 收口前把 4 条门禁命令输出（含时间/EXIT/新 pin）落到 `verification/FEA-14-S5-PREQ-1/logs/`；AC6 证据行引用之 | open |
| R-010 | **P3** | `doc/plan/FEA-C07_API_INVENTORY.md:3`（状态行/自述）、`:102-104`（计划节）；冻结记录 `:44` | **C-07 自述「由代码生成/成员行与脚本 stdout 一一对应」与新增人工计划节存在张力**：计划节为人工内容，虽已标注「尚未实现/不计入统计」，但 pin 现覆盖非代码字节，且状态行「成员行与脚本 stdout 一一对应」对计划节不再成立。另发现**既有**（非本次引入）：`IHostController` 的脚本 stdout 成员顺序与文档旧表顺序不同（集合相等、名称/返回类型一致；均由同一 code/HEAD 决定，故为历史整理差异）。影响：不影响旧签名与统计正确性，但会让未来「stdout 全文 diff」核对出现既有噪声。 | 脚本 stdout 与文档逐行比较：集合等、顺序不等；HEAD 版本同样如此；diff 仅 1 处删除（状态行） | 状态行补「计划节除外」或在计划节首行注明「非生成内容」；另可择机对齐旧表顺序（不属本卡必需） | open |

## 4. AC 逐项（本审查只复核 AC2/AC3；AC1/AC4/AC5/AC6 记录现状供 Lead 参考）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 七切片裁决 | **MET（已提交）** | `ADJ-2026-11-10-FEA14-S5-SCOPE.md` 存在（7348 B，已提交）；`FEA-15` append-only 注记在 `b7aaccfbc` 中 +2 行、无删改原句（diff 实测） |
| AC2 共用 wire + 一次 UNFREEZE | **NOT MET（R-001；UNFREEZE 其余要素 PASS）** | pin/统计/UNFREEZE 合规通过；`minor`/`payload 形状` 缺失，AC2 原文未满足 |
| AC3 新数据类别 errata | **PARTIAL（R-002/R-003/R-004/R-005）** | 0 pin 与四类覆盖主体成立；写域越界、无冻结记录锚点、prompt_templates/fonts 语义未闭合 |
| AC4 设置存储形状 | MET（本审查未复检，仅交叉引用） | `verification/FEA-14-S5-PREQ-1/settings-storage-shape.md`（与 R-004 载体二选一表述一致） |
| AC5 DDL v10 计划 | MET（本审查未复检，仅交叉引用） | `verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md`（与 R-004 载体条件一致） |
| AC6 门禁与零改动 | **重新核验后 PARTIAL** | 无 src/apps/DDL diff、pins 18/18、check PASS；但含 untracked 的变更集有 1 个 OUT 文件（R-002），且 logs 未落（R-009） |

## 5. 门禁实测（命令 + 时点 + EXIT）

| # | 命令 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `python tools/generate_api_inventory.py --check` | 09:30:44 | `OK: rendered counts match FEA-C07 doc`；1/54/6 = 61 | **0** |
| 2 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 09:30:53 → 09:30:54 | **PIN AUDIT: PASS (all 18)**；C07 = `c67c40e72938`，其余 17 与 FEA-14-SET-1 最终值逐项相同 | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 09:30:54 → 09:30:56 | PASS（3 warnings：11 非终态 / STATUS 3133 B·30 L 80% / PLAN 6791 B·63 L 80%） | **0** |
| 3b | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-S5-PREQ-1.md` | 09:30:54 → 09:30:56 | PASS（同上 3 warnings） | **0** |
| 4 | `Get-FileHash doc/plan/FEA-C07_API_INVENTORY.md -Algorithm SHA256` | 09:30:35 前后 | `c67c40e72938ac3d5284d778758a17e66f65d760c38e2aa7c6da548a79f47550` = frozen §1 pin | — |
| 5 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 09:29:03 / 09:39:50 | 同一 HEAD `b7aaccfbc…`；工作树 3 M + 3 ??（如上 §0），审查期间无变化 | — |

仓外日志：`G:\CODEX\New Manga.workspace\temp\FEA-14-S5-PREQ-1-r1\`（`gate1-inventory.log`、`gate2-pins.log`、`gate3-check-default.log`、`gate4-check-taskpath.log`、`check_wire.log`）。

## 6. 证据与 NOT_RUN

**已实测（可复现）**：inventory 旧节/统计逐表与 HEAD 相等；计划节 25 行与 wire 文档逐条名称/返回类型/切片一致；计划名与现有 54+6+1 成员无碰撞；25 条 P1–P25 与 #1–#25 顺序一致；`--check`/pins/check 门禁；pin 双处一致；C-01b `:53-55`、C-09 `:24-48,51`、`cleanup.py:41`、先例 ADJ 存在性；`git status` 范围与 untracked 判定；`git diff --numstat`（35/1；9/7；1/0）。

**NOT_RUN（不得记 PASS）**：
- 任何 25 条计划命令的**实现/行为**验证 = NOT_RUN（本卡为文档卡，代码不存在）。
- Core wire 侧命令名/域/`PROTOCOL_MINOR`/payload 的注册与探针 = NOT_RUN（产物未定义；`HostCommandRegistry` 现有 per-command minor 仅作先例证据）。
- C-01b/C-09 冻结记录 errata 落地 = NOT_RUN（尚未写入，故无法核对）。
- 真实备份/恢复/清理行为测试 = NOT_RUN（仅按 `cleanup.py:41`/C-09 文本核对事实）。
- `prompt_templates` 最终载体（DB vs settings）= NOT_RUN（AC4/AC5 明记由 AI-1 冻结时决定）。
- 跨口径 pin（`git cat-file blob` LF SHA-256）记录 = NOT_RUN（本审查仅按仓库既有 worktree pin 口径；§1A 建议的双口径未记录）。
- AC4/AC5 的独立复核 = NOT_RUN（不属于本次指派范围，仅作交叉引用）。

## 7. 处置建议（按顺序）

1. **R-001（P1）**：由 DSH 裁决 wire 包边界并落文——优先补 wire 文档的 per-command「Core 命令/域/minor/payload 形状」列（或明确记录「本轮只锁 App 端口名/域/返回/语义，Core wire 由各实现卡按既有 minor 约定处理」），同步改 AC2 文本，避免 AC2 以未满足状态标 MET。
2. **R-002/R-003（P2）**：卡面 allowed_paths 增补 errata 精确路径；按 0 pin 先例在 `FEA-CONTRACT-FROZEN-C01b.md`/`-C09.md` 追加 errata 注记（同时把这些路径纳入 allowed_paths），或在卡面/冻结记录/scope ADJ 建立对独立 ADJ 文件的指针并明确取代先例的理由；同步交付物 #3 表述。
3. **R-004/R-005（P2）**：errata 补 prompt_templates 两分支与内置模板入包/恢复语义；补 fonts 内部副本 vs 外部原字体（SC-11）边界。
4. **R-006…R-010（P3）**：断链、`:42` 行号、frozen §5 v1.2 行、门禁日志落盘、状态行「一一对应」措辞，可随本次处置一并修。
5. 上述完成并重跑 §5 门禁后，把本复核结论（及处置后的最终 pin）回填 UNFREEZE 载体 §5 与 frozen §1B，再提交并由 DSH 做 r2 复核。

## 8. 审查者声明

本报告由未参与 `FEA-14-S5-PREQ-1` 写作的独立上下文子 agent 出具；只读审查，唯一写入为本文件。所有 PASS 结论均基于本次实测或逐行静态核对；未实测项已在 §6 记 NOT_RUN；被审产物当前为**未提交工作树**，其字节以 §0 SHA-256 锚定；若提交改动了这些字节，本报告结论不自动延续。
