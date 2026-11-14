# C07 API Inventory · 冻结记录

**契约**：`doc/plan/FEA-C07_API_INVENTORY.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) + [冻结矩阵](../plan/FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C07_API_INVENTORY.md` |
| sha256（冻结后最终字节） | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750`（v1.9，2026-11-14 UNFREEZE（RO-1）：`FEA-06-RESIDUAL-4A` 为 `IHostController.ListPageRegionTextsAsync`（`Task<RegionPageTextProjection?>`）做 additive **预授权**登记——新增「RO-1 计划追加」节并写死落地判据（成员表 #80、统计 80/87、pin v1.10）；**统计行与正式成员表字节零改动**（仍 79/86，与脚本 stdout 逐行一致）；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md`；**独立字节级复核 r2 `approved`（P0/P1=0；P2=2/P3=5 不阻断；`doc/reviews/FEA-06-RESIDUAL-4A-r2.md`）**，**已重冻**） |
| 前一 pin（v1.8，保留原值） | `8ccaba05cbc21eec04a366f8bfa2be2dea4515ba90e6d5aab95b11a7c47f0509`（v1.8：AI-1 P21–P25 落地统计 79/86，S5 计划节 25/25 全部落地；已由 AI-1 r2 approved 重冻） |
| 前一 pin（v1.7，保留原值） | `89781583964eb81db0e12974fdd03adc44231461ac3b2fad65f0eacdb74261c6`（v1.7：EDIT-1 P16–P20 落地 74/81；已由 r2 approved 重冻） |
| 前一 pin（v1.6，保留原值） | `7c033bf76af1726b71e1ce92a5b3c221d880cf7a36bfc44ef3d4467582d5457d`（v1.6：LIB-1 成员表同步 P1–P15，69/76；已由 r3 approved 重冻） |
| 前一 pin（v1.5，保留原值） | `9c1eb974342af889c8c3acb8b7f7d7893ba44f05ee4b32c871116e249b321d74`（v1.5：LIB-1 P5–P8 落地统计 69/76；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md`） |
| 前一 pin（v1.4，保留原值） | `8d92a32feed771e416d1c1c003ec806e0c5c4712209fd2e097c0a723252bab5c`（v1.4：FONT-1 P1–P4 落地统计 65/72；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-10-FONT1.md`） |
| 前一 pin（v1.3，保留原值） | `59ab90f7d717fdd44816d22284d00e2a53ab48581d644c97e9dccd3ccc6a1b5a`（v1.3：READ-1 P9–P15 落地统计 61/68；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-10-READ1.md`） |
| 前一 pin（v1.2，保留原值） | `5673b1c4b53e69ec36f1897ea5bb0ba8eeedbf437320381ee1b2a04448bf2aa6`（v1.2：PREQ「S5 计划追加」节；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md`） |
| 前一 pin（v1.1，保留原值） | `3fdb44e49afe9fb25e715c5a41bd247cee269c194d045e1f79946f25067dd714`（v1.1：Draft 7 端口 54/61；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-02.md`） |
| r1 复核锚（未冻结，处置前字节） | `c67c40e72938ac3d5284d778758a17e66f65d760c38e2aa7c6da548a79f47550` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | v1.0：r2 approved（FEA-GOV-10-r2）；v1.1：**r3 approved（FEA-05-PORT-1，P0/P1=0，P2×11 接受）**；v1.2：**r2 approved**（`doc/reviews/FEA-14-S5-PREQ-1-wire-review-r2.md`）；v1.3：READ-1 r2 approved（`doc/reviews/FEA-14-READ-1-r2.md`）；v1.4：FONT-1 r5 approved（`doc/reviews/FEA-14-FONT-1-r5.md`）；v1.5/v1.6：LIB-1 r1 `changes_requested` → r1 处置 → r2 `changes_requested` → r2 处置 → **r3 `approved`**（`doc/reviews/FEA-14-LIB-1-r3.md`，P0/P1/P2=0；P3=1 accepted；被审 head `de595f69d`，覆盖 v1.6 字节）；v1.7：EDIT-1 实现落地 → **r2 `approved`**（`doc/reviews/FEA-14-EDIT-1-r2.md`，P0/P1/P2=0；P3=1 accepted；被审 head `54b87dcc9`，覆盖 v1.7 字节；r1 发现 C-07 S5 节残留 P16–P18 行 → 已删除并重算 pin `89781583…`）；v1.8：AI-1 实现落地（74→79 / 81→86）→ r1 `changes_requested`（F-01 事务/F-02 成员表 `Changed` 事件行）→ 处置并重算 pin `8ccaba05…` → **r2 `approved`**（`doc/reviews/FEA-14-AI-1-r2.md`，P0/P1/P2=0；P3=7；被审 head `2737d035a`）；**v1.9：r1 `changes_requested`（P0=0/P1=2，记录层假陈述）→ 处置（不触 inventory 字节）→ r2 `approved`（P0/P1=0；P2=2/P3=5 不阻断；`doc/reviews/FEA-06-RESIDUAL-4A-r2.md`；被审 head `756ab29e2`），已重冻** |
| 复核后到冻结的改动 | v1.1：Draft 端口 7 方法 + 统计/成员表；v1.2：新增「S5 计划追加」节；v1.3：READ-1 统计 61/68；v1.4：FONT-1 统计 65/72；v1.5：LIB-1 统计 69/76；v1.6：P1–P15 成员表同步；v1.7：EDIT-1 统计 74/81 + P16–P20 成员表并入（S5 节只剩 P21–P25）；**v1.8：AI-1 统计 79/86 + P21–P25 成员表并入（S5 节 25/25 全落地）**；v1.9：新增「RO-1 计划追加」节（1 条预授权）+ 状态行/生成日期行注记，**统计与正式成员表零改动** |
| 处置 | v1.1 **已重冻**（2026-11-02，r3 approved）；v1.2 **UNFREEZE 已生效**（2026-11-10，PREQ AC2）；v1.3–v1.5 已随各自实现卡重算 pin；**v1.6 已重冻**（2026-11-10，LIB-1 r3 approved）；**v1.7 随 EDIT-1 实现落地重算 pin**（`89781583…`；r1 处置后已修正 S5 节残留行，字节以此为准），**已由 EDIT-1 r2 approved 重冻**；**v1.8 随 AI-1 实现落地重算 pin**（`8ccaba05…`；r1 处置修正 `Changed（事件）` 行后以此为准），**已由 AI-1 r2 approved 重冻**；**v1.9 随 `FEA-06-RESIDUAL-4A` 契约前置重算 pin**（`91e51ab7…`；字节改动 = 计划节 + 两处注记，统计/成员表零改动），**已由 r1→处置→r2 `approved` 重冻（2026-11-14）** |

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验

| # | C-07 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（P1 生成脚本缺失）→ 入库脚本 → r2 [approved](../reviews/FEA-GOV-10-r2.md)（P0×0 / P1×0 / P2×3）；v1.2 UNFREEZE 复核：见载体 §4/§5；v1.7：EDIT-1 r2 approved（`doc/reviews/FEA-14-EDIT-1-r2.md`）；v1.8：AI-1 r2 approved（`doc/reviews/FEA-14-AI-1-r2.md`）；**v1.9：r1 `changes_requested`（P0=0/P1=2，记录层假陈述）→ 处置 → r2 `approved`（P0/P1=0；P2=2/P3=5 不阻断；`doc/reviews/FEA-06-RESIDUAL-4A-r2.md`；被审 head `756ab29e2`）→ 已重冻** |
| 2 | 生成脚本入库 | ✅ | [`tools/generate_api_inventory.py`](../../tools/generate_api_inventory.py)（177 行，UTF-8 stdout 固定） |
| 3 | `--check` 通过 | ✅ | `python tools/generate_api_inventory.py --check` → EXIT=0，**1/79/6 = 86**（代码实测；v1.8 起「S5 计划追加」节 25/25 已全部落地、无待实现行；v1.6 起正式成员表逐行与 stdout 一致，计数一致不等于成员表一致；v1.9 新增「RO-1 计划追加」节 1 条**预授权**、不计入脚本统计，RO-1 行落地后应为 `1/80/6 = 87`） |
| 4 | `check.ps1` PASS | ✅ | 冻结时 PASS；2026-11-10 UNFREEZE 后 `check.ps1`（默认 + `-TaskPath`）PASS（3 persistent warnings）；**v1.9**：新增 `doc/tasks/FEA-06-RESIDUAL-4A.md` 使 `doc/TASK_LEDGER.md` 的 `task files`/`non-terminal` 计数变化（599/7 → 600/8），经 DSH 2026-11-14 授权执行一次 `python tools/governance/task_ledger.py --write` 后，`check.ps1`（默认 + `-TaskPath`）**PASS (3 warnings)**，台账随同一 commit 提交 |

## 3. 依赖与后果

- **无上游依赖**（清单只读代码）。
- **下游**：所有涉及 `IHostController`/`IRunController`/`IReaderProgressSink` 的实现 Task（须按清单保持旧签名）。
- **实现注意**：清单是**基线**；新增/删除端口方法须在同一 Task 内重跑脚本并更新清单，diff 即审查信号。
- **S5 计划追加节**（`## S5 计划追加`）：25 条命令为**预冻结名单**。实现卡落地时须（a）把对应行从「计划追加」移入正式成员表；（b）重跑脚本并把统计更新为实测值；（c）重算 pin 并在实现卡内记录。**已全部落地 25/25**（READ-1 P9–P15 → v1.3；FONT-1 P1–P4 → v1.4；LIB-1 P5–P8 → v1.5 统计、v1.6 成员表同步；EDIT-1 P16–P20 → v1.7；AI-1 P21–P25 → v1.8），计划节自此无待实现行；计划节本身不改变旧签名。
- **RO-1 计划追加节**（`## RO-1 计划追加`，v1.9 新增）：1 条**预授权**命令（`ListPageRegionTextsAsync` / `Task<RegionPageTextProjection?>`，落地卡 `FEA-06-RESIDUAL-4B`）。落地时须（a）在 `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs` 加该方法，并在 `HostController` / `NullHostController` / 测试 `FakeHostController` 三处实现（降级一律 `null`）；（b）重跑脚本、把该行并入正式成员表第 **80** 行并把统计改为 `80 / 87`（`--check` 须 EXIT 0 且成员表逐行 = stdout）；（c）重算 pin（**v1.10**）并在实现卡内记录。计划节本身不改变旧签名，也不改变当前统计。

## 4. 不构成什么

- **不构成**实现授权（实现须按 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成**远端 push 授权。

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `5919b084c906f5cdc79d7e6e1b425f05347d915a77bb5c50f9f97f09c3960b5f` |
| 修正后 pin（最终字节） | `17c8f7016a368a0a827e9a656f9126d9949564aed9d5dc31462c0b5787f1b0c5` |
| 差异范围 | **仅状态行** DRAFT→FROZEN，条款字节未动 |

**为什么保留原值**：pin 是证据，不能静默替换。原值可独立复现（还原本次冻结动作后重算即得），因此证明冻结前的确切字节；修正后的值才是后续校验基准。

**冻结字节 = 复核字节？** 见 §1B。

**纪律（自本记录起）**：
1. pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；
2. 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；
3. 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径；
4. **冻结提交本身不得含条款编辑**——最后处置必须在冻结**之前**的独立提交完成并经复核。


**为什么保留原值**：pin 是证据，不能静默替换。原值证明「条款内容与冻结前一致」（状态行是元数据，条款字节未动）；修正后的值才是后续校验的基准。

**纪律（自本记录起）**：① pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；② 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；③ 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径。
## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `17c8f7016a368a0a827e9a656f9126d9949564aed9d5dc31462c0b5787f1b0c5`；新增 §1A 修正记录与纪律（见上） | DSH |
| 2026-11-02 | **UNFREEZE v1.0→v1.1（FEA-05-PORT-1）**：`IHostController` 47→54（+7 Draft 端口）、合计 54→61、变更类别 11→18；pin 重算为 `5c48083f…`（原 v1.0 pin `17c8f701…` 保留于 §1A 历史行，不静默替换）；UNFREEZE 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-02.md`；重新独立复核（`FEA-05-PORT-1-impl-r*`） | DSH |
| 2026-11-10 | **UNFREEZE v1.1→v1.2（FEA-14-S5-PREQ-1）**：inventory 新增「S5 计划追加」节（25 条计划命令：FONT 4 / LIB 4 / READ 7 / EDIT 5 / AI 5），**代码/旧 54 签名/统计零改动**（`--check` 仍 1/54/6=61）；pin 重算为 `5673b1c4…`（v1.1 pin `3fdb44e4…` 保留，r1 锚 `c67c40e7…` 保留为未冻结中间值）；载体 [CONTRACT-UNFREEZE-2026-11-10-C07](../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md)；独立复核 r1 `changes_requested` → 处置 → **r2 `approved`**（P0/P1/P2=0，6×P3 不阻断） | DSH |
| 2026-11-10 | **UNFREEZE v1.2→v1.3（FEA-14-READ-1）**：统计 `IHostController` 54→**61**、合计 61→**68**（P9–P15 落地）；pin `59ab90f7…`；载体 [CONTRACT-UNFREEZE-2026-11-10-READ1](../reviews/CONTRACT-UNFREEZE-2026-11-10-READ1.md)；卡面复核 r2 approved（`doc/reviews/FEA-14-READ-1-r2.md`） | DSH |
| 2026-11-10 | **UNFREEZE v1.3→v1.4（FEA-14-FONT-1）**：统计 61→**65**、合计 68→**72**（P1–P4 落地）；pin `8d92a32f…`；载体 [CONTRACT-UNFREEZE-2026-11-10-FONT1](../reviews/CONTRACT-UNFREEZE-2026-11-10-FONT1.md)；卡面复核 r5 approved（`doc/reviews/FEA-14-FONT-1-r5.md`） | DSH |
| 2026-11-10 | **UNFREEZE v1.4→v1.5（FEA-14-LIB-1）**：统计 65→**69**、合计 72→**76**（P5–P8 落地）；pin `9c1eb974…`；载体 [CONTRACT-UNFREEZE-2026-11-10-LIB1](../reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md)；LIB-1 r1 复核指出本记录缺 v1.3/v1.4/v1.5 行、S5 节与成员表未同步（R-05/R-07） | DSH |
| 2026-11-10 | **UNFREEZE v1.5→v1.6（FEA-14-LIB-1 r1 处置）**：正式成员表按脚本 stdout 重建并同步 P1–P15（**69 方法 + 4 非方法成员，逐行一致**），统计不变（69/76）；「S5 计划追加」节改为只列剩余 P16–P25；§1 pin 链补齐 v1.3–v1.6 原值、§1B/§2/§3 口径同步；pin `7c033bf7…`（v1.5 `9c1eb974…` 保留）；载体 [CONTRACT-UNFREEZE-2026-11-10-LIB1](../reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md)（v1.6 附录） | DSH |
| 2026-11-10 | **v1.6 待重冻（LIB-1 r2 `changes_requested`）**：r2 独立复核确认 C-07 成员表逐行等于 stdout、统计/pin/§1B/§2/§3/§5 自洽（v1.6 字节本身无 finding）；阻断项均为产品残余（R-02 未知 tag typed/半写、R-04 sort_order 撞序）与 4×P3。r2 处置只改产品/测试/证据字节，**C-07 字节未变、pin 仍 `7c033bf7…`**；待 r3 独立复核覆盖 v1.6 后重冻收口；报告 `doc/reviews/FEA-14-LIB-1-r2.md` | DSH |
| 2026-11-10 | **v1.6 重冻（LIB-1 r3 approved）**：r3 独立复核 `approved`（P0/P1/P2=0，P3=1 accepted），逐行核对 C-07 成员表 = stdout、pin = 文件 SHA-256、冻结记录 §1–§5 自洽；C-07 字节自 v1.6 起未再改，pin 保持 `7c033bf7…`；报告 `doc/reviews/FEA-14-LIB-1-r3.md`（被审 head `de595f69d`） | DSH |
| 2026-11-10 | **UNFREEZE v1.6→v1.7（FEA-14-EDIT-1）**：`IHostController` 69→**74**、合计 76→**81**（P16–P20 落地：`ListIssueMarkersAsync`/`CreateIssueMarkerAsync`/`ResolveIssueMarkerAsync`/`ReopenIssueMarkerAsync`/`DeleteIssueMarkerAsync`）；成员表按脚本 stdout 重建为 74 方法 + 4 非方法成员（`ALL_MATCH: True`）；S5 计划节只剩 P21–P25（已落地 20/25）；pin `89781583…`（v1.6 `7c033bf7…` 保留；r1 处置把初值 `bb775912…` 修正为 `89781583…`，差异仅 S5 节删除残留的 P16–P18 三行）；载体 [CONTRACT-UNFREEZE-2026-11-10-EDIT1](../reviews/CONTRACT-UNFREEZE-2026-11-10-EDIT1.md)；复核：`--check` EXIT 0、`verify_pins` 18/18，独立复核随 EDIT-1 r2 | DSH |
| 2026-11-10 | **v1.7 重冻（EDIT-1 r2 approved）**：r2 独立复核 `approved`（P0/P1/P2=0；P3=1 accepted：卡片 closeout 文字旧，已随收口更新），逐项关闭 r1 的 F-01–F-05；C-07 S5 计划节只剩 P21–P25、成员表 74+4 与 stdout 逐行一致、pin `89781583…` = 文件 SHA-256；报告 `doc/reviews/FEA-14-EDIT-1-r2.md`（被审 head `54b87dcc9`） | DSH |
| 2026-11-10 | **UNFREEZE v1.7→v1.8（FEA-14-AI-1）**：`IHostController` 74→**79**、合计 81→**86**（P21–P25 落地：`ListPromptTemplatesAsync`/`SavePromptTemplateAsync`/`DeletePromptTemplateAsync`/`CopyBuiltinPromptTemplateAsync`/`GetPromptTemplateReferencesAsync`）；成员表按脚本 stdout 重建为 79 方法 + 4 非方法成员（`ALL_MATCH: True`）；S5 计划节 **25/25 全部落地**、无待实现行；pin `8ccaba05…`（v1.7 `89781583…` 保留；r1 处置把初值 `58dbae4c…` 修正为 `8ccaba05…`，差异仅 `Changed（事件）` 一行）；载体 [CONTRACT-UNFREEZE-2026-11-10-AI1](../reviews/CONTRACT-UNFREEZE-2026-11-10-AI1.md)；复核：`--check` EXIT 0、`verify_pins` 18/18，独立复核随 AI-1 r2 | DSH |
| 2026-11-10 | **v1.8 重冻（AI-1 r2 approved）**：r2 独立复核 `approved`（P0/P1/P2=0；P3=7 登记/接受），关闭 r1 的 F-01（P23 单事务）与 F-02（`Changed（事件）`）；C-07 成员表 79+4 与 stdout 逐行一致、S5 计划节 25/25、pin `8ccaba05…` = 文件 SHA-256；报告 `doc/reviews/FEA-14-AI-1-r2.md`（被审 head `2737d035a`） | DSH |
| 2026-11-14 | **UNFREEZE v1.8→v1.9（FEA-06-RESIDUAL-4A，RO-1 additive 预授权）**：`IHostController` **仍 79**、合计 **仍 86**（**统计行与正式成员表字节零改动**，成员表 = stdout `ALL_MATCH: True`）；新增「RO-1 计划追加」节预授权 `ListPageRegionTextsAsync`（`Task<RegionPageTextProjection?>`），写死落地判据（成员表 **#80**、统计 **80/87**、pin **v1.10**、三处实现 + `NullHostController`/Fake 降级 `null`）；状态行/生成日期行加 v1.9 注记；pin `91e51ab7…`（v1.8 `8ccaba05…` 保留于 §1 前一 pin 行）；载体 [CONTRACT-UNFREEZE-2026-11-14-C07-RO1](../reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md)；复核：`--check` EXIT 0（`1/79/6=86`）、`verify_pins` 18/18；**独立字节级复核 r1 `changes_requested`（P0=0 / P1=2，均为记录层事实错误，字节层全过）→ 处置 → r2 `approved`（P0/P1=0；P2=2/P3=5 不阻断；报告 [r1](../reviews/FEA-06-RESIDUAL-4A-r1.md) / [r2](../reviews/FEA-06-RESIDUAL-4A-r2.md)），已重冻**；`check.ps1` 在台账重生成后 PASS，重生成前曾因 TASK_LEDGER 计数过期报错 | residual-4a（DSH 派出）；重冻 DSH |
