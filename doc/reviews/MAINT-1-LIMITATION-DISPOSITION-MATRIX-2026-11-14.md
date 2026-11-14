# limitation 处置矩阵（MAINT-1 线收口载体，2026-11-14）

- 用途：满足 `doc/reviews/MAINT-1-P6-LINE-CLOSEOUT-VERDICT.md` 判为**未达成**的 **DoD §1**（9 个 `closed_with_limitations` 节点未逐条转 done+waiver）与 **DoD §3**（limitation 未逐条处置：C1 约 13 / C2 5 未决）。
- 性质：**append-only 裁决记录 + 处置矩阵**。不改 9 张历史 Task 卡、不改 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md` / `doc/TASK_LEDGER.md`、不改 `src/**` / `apps/**` / `tests/**`、不改任何 Review / `verification/**` 历史字节。
- 已有载体（本文件**不重复**其内容，只做映射与补缺）：
  - C3：`doc/reviews/MAINT-1-C3-OUT-CARRIER-2026-11-14.md`（6 项，下文记 `C3-n`）
  - C4：`doc/reviews/MAINT-1-C4-WAIVER-CARRIER-2026-11-14.md`（10 项，下文记 `W#`）
  - 分类正本：`doc/reviews/MAINT-1-P3-LIMITATION-TRIAGE.md`（9 节点 → C1/C2/C3/C4）
- 裁决人：DSH（用户 2026-11-14 全权授权）。**用户可事后推翻任一条**；推翻后按对应项重开卡。

## 0. 判定口径：`closed_with_limitations` + 正式载体 ≡ DoD §1 的「done + 显式 waiver」

`doc/reviews/MAINT-1-P6-LINE-CLOSEOUT-VERDICT.md:11` 的 §1 判据原文是「FEA-* 全部 done，**或 done + 显式 waiver**（含 `NOT_APPLICABLE` 原因与保留的 `NOT_RUN` 证据）」。本文件主张并定义如下等价关系：

1. **等价关系**：一个节点满足 `closed_with_limitations` **且** 其每一项 limitation 都能指向「正式载体条目（C3 OUT / C4 waiver / 裁决记录）」或「本循环已解的实现证据或明确保留原因」，即视为满足 §1 的「done + 显式 waiver」。二者差别仅在**状态字面值**，不在「是否有未完成项」与「是否已被显式裁决」这两个实质要件上。
2. **为什么不改 9 张历史卡的 status**：
   - 项目字节保留规则与 2026-10-25 接管记录要求历史 Task 卡、Review、证据 pin 保持原字节；把 `closed_with_limitations` 批量改写为 `done` 会**改写历史**，并使既有 Review 与 gateway 结论（"带 limitation 完成"）与卡面字面值矛盾；
   - `closed_with_limitations` 的语义本身就含「已交付 + 明确未达成部分」，与 `done + waiver` 在验收信息量上是同一件事的两种记法；
   - 反向做法（把 `done` 卡改成 `closed_with_limitations`）同样会被视为改写历史，故本文**只做映射，不翻转任何卡**。
3. **等价关系成立的举证责任在本文件**：每个 limitation 项必须有 `L-<节点>-<n>` 编号 + 处置 + 证据指针；**任何无指针的行视为未处置**（即 DoD §3 未达成）。§4 逐条列出仍无法处置或需 DSH 终裁的项。

## 1. 总表（9 节点 / 39 项）

处置码：`SOLVED` 本循环已解并给证据｜`IMPL` 建议实现后才能 MET（需卡）｜`C3` 已有 OUT 载体｜`C2` 契约对齐待裁（本文件给建议）｜`WAIVER` 已有 C4 waiver｜`KEEP` 保留 NOT_RUN/原分类（本文件补原因与证据指针）｜`UNCERTAIN` 证据不足，不得当已处置。

| # | 节点 | limitation 项（原卡行号） | 处置 | 载体 / 证据指针 | 悬空 |
|---|---|---|---|---|---|
| L-A31-1 | FEA-15-A3-1 | `window-material.log` 在只给 `--data-root` 时回落真实 `%APPDATA%`（`doc/tasks/FEA-15-A3-1.md:98`） | `C3` | `C3-6`（`doc/reviews/MAINT-1-C3-OUT-CARRIER-2026-11-14.md:17`）；源码 `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:1041-1051`（`ResolveDiagnosticsRoot`） | 否 |
| L-A31-2 | FEA-15-A3-1 | 真实手势 / IME / 多屏 / DPI / 主题 / 托盘（`:99`） | `WAIVER` | `W6`（`doc/reviews/MAINT-1-C4-WAIVER-CARRIER-2026-11-14.md:25`） | 否 |
| L-R1-1 | FEA-14-READ-1 | Fluent Reader UI 未接线（偏好应用/书签面板/整书进度/reset 确认）（`doc/tasks/FEA-14-READ-1.md:160`） | `IMPL` | 拆卡已建立：`doc/tasks/FEA-14-READ-2.md`；**残余可见控件见 L-R2-1** | 是（经 L-R2-1） |
| L-R1-2 | FEA-14-READ-1 | P12/P15 返回类型与 `confirm_token` 偏差（`:160`） | `C2` | 本文件 §3-C2-5（建议 OUT）；原登记见 `FEA-14-READ-1` limitation 段 | 否（建议 OUT） |
| L-R1-3 | FEA-14-READ-1 | 真实手势 / IME / 多屏 / DPI / 主题 / 托盘 / 真实进程重启（`:160`） | `WAIVER` | `W1`（C4 载体 `:20`） | 否 |
| L-R2-1 | FEA-14-READ-2 | 书签面板 / 整书进度 / reset 确认的**可见控件**未接线（VM+测试已覆盖）（`doc/tasks/FEA-14-READ-2.md:116`） | `IMPL` | 本文件 §3-C1-1（建议：一张 UI 控件卡即可闭环）；VM 证据 `doc/tasks/FEA-14-READ-2.md:115` | **是** |
| L-R2-2 | FEA-14-READ-2 | 真实 UI 手势 / IME / 多屏 / DPI / 主题 / 托盘 / 真实进程重启 / 可见 UI 截图（`:116`） | `WAIVER` | `W1` | 否 |
| L-F1-1 | FEA-14-FONT-1 | FONT-2 范围：渲染消费、设置页字体 UI、家族/字重元数据解析（fontTools）、内置字体授权（不随包）（`doc/tasks/FEA-14-FONT-1.md:153`） | `C3` | `C3-5`（C3 载体 `:16`）；许可边界 `AGENTS.md`「许可证边界」段 | 否 |
| L-F1-2 | FEA-14-FONT-1 | wire 级 `FONT_DELETE_FAILED` 负例未补（storage 已覆盖）（`:153`） | `IMPL` | 本文件 §3-C1-2（补 1 个定向测试；storage 侧证据见该卡交付段 `:152`） | **是** |
| L-F1-3 | FEA-14-FONT-1 | 大文件 / 并发 / 占用文件未压测（`:153`） | `IMPL`（大文件/并发）+ `KEEP`（占用文件） | 本文件 §3-C1-3；`W4`（C4 载体 `:23`）只覆盖渲染消费与真实占用 | 部分 |
| L-F1-4 | FEA-14-FONT-1 | 日志 HEAD 为生成时工作树（证据口径）（`:153`） | `C3` | 本文件 §3-C3-7（证据口径说明，非产品项） | 否 |
| L-L1-1 | FEA-14-LIB-1 | ① `ChapterSummary` 不投影 `kind`（`doc/tasks/FEA-14-LIB-1.md:164`） | `IMPL` | 本文件 §3-C1-4（LIB-2 扩 DTO） | **是** |
| L-L1-2 | FEA-14-LIB-1 | ② `custom_rank` write-only、P6 自定义/数字排序未实现（`:164`） | `IMPL`（读回闭环）+ `C3`（排序 UI 范围） | 本文件 §3-C1-5；UI 范围未释放，参照 `C3-3` 同型口径 | 部分 |
| L-L1-3 | FEA-14-LIB-1 | ③ R-11 三项 deferral（kind 语义体积、`number_value`、`books.normalized_title` 唯一索引）（`:164`） | `C2` | 本文件 §3-C2-4（建议 OUT + 重开条件） | 否（建议 OUT） |
| L-L1-4 | FEA-14-LIB-1 | ④ R3-001 64 位边界校验缺失（`:164`） | `IMPL` | 本文件 §3-C1-6（小卡，补边界断言） | **是** |
| L-L1-5 | FEA-14-LIB-1 | ⑤ 真实 Host↔Core 进程级联调 / LIB UI·tags UI / Volume 实体 / 万级章性能（`:164`） | `WAIVER` | `W5`（C4 载体 `:24`） | 否 |
| L-E1-1 | FEA-14-EDIT-1 | ① `issue_markers` 无外键、删书不清理孤儿行（`doc/tasks/FEA-14-EDIT-1.md:139`） | `C3` | `C3-4`（C3 载体 `:15`） | 否 |
| L-E1-2 | FEA-14-EDIT-1 | ② `position` 形状 `{x,y}` 为未定义处实现裁决（`:139`） | `C3` | `C3-2`（C3 载体 `:13`） | 否 |
| L-E1-3 | FEA-14-EDIT-1 | ③ 批量 resolve/delete、分页/跨书过滤、`kind` 预置集合（`:139`） | `C3` | `C3-3`（C3 载体 `:14`） | 否 |
| L-E1-4 | FEA-14-EDIT-1 | ④ 真实 Host↔Core IPC / EDIT UI / 管线联动 / 万级性能（`:139`） | `WAIVER` | `W2`（C4 载体 `:21`） | 否 |
| L-AI1-1 | FEA-14-AI-1 | ① P24 客户端只回 `template_id`（name 需 P21 刷新）（`doc/tasks/FEA-14-AI-1.md:154`） | `C3` | 本文件 §3-C3-8（有既定替代路径 P21，不构成缺陷） | 否 |
| L-AI1-2 | FEA-14-AI-1 | ② 引用写入方（译文/任务/规则）留后续卡（`:154`） | `C3` | 本文件 §3-C3-9（引用写入方未释放，无消费者） | 否 |
| L-AI1-3 | FEA-14-AI-1 | ③ `UPDATE OR REPLACE` 覆盖同 `(kind,owner_id)` label（F-03）（`:154`） | `C2` | 本文件 §3-C2-2（建议 OUT + 重开条件） | 否（建议 OUT） |
| L-AI1-4 | FEA-14-AI-1 | ④ name 唯一/规范化范围（F-05，待 ADJ）（`:154`） | `C2` | 本文件 §3-C2-1（建议 OUT + 重开条件） | 否（建议 OUT） |
| L-AI1-5 | FEA-14-AI-1 | ⑤ DDL「version 不可变」已裁决（F-08）（`:154`） | `C3` | `C3-1`（C3 载体 `:12`） | 否 |
| L-AI1-6 | FEA-14-AI-1 | ⑥ 死方法 `reassign_references`（N-01）与 `test_issue_markers` 旧注释（F-06 残余）（`:154`） | `IMPL` | 本文件 §3-C1-7（微清理，可并入维护卡） | **是** |
| L-AI1-7 | FEA-14-AI-1 | ⑦ 真实 IPC / P24 活 Core 端到端 / 模板 UI（AI-2）/ 真实 AI 网络 / 并发大库（`:154`） | `WAIVER` | `W3`（C4 载体 `:22`）；模型 API `NOT_RUN` 见 `doc/design/V1_COMMITMENT_MANIFEST.md:6` | 否 |
| L-AC1-1 | FEA-15-ACCEPT-1 | pytest 16 failed（既有基线）（`doc/tasks/FEA-15-ACCEPT-1.md:131`） | `SOLVED` | `doc/reviews/MAINT-1-P11-CUSTOM-RANK-ADJUDICATION.md:66`：全量 **3537 passed / 10 skipped / 0 failed**（316.39s）；Q6 归因 `doc/reviews/MAINT-1-P9-Q6-PYTEST-ADJUDICATION.md` | 否（证据在仓外，见 §4-R2） |
| L-AC1-2 | FEA-15-ACCEPT-1 | .NET 127 failed「根因未定」（`:131`） | `SOLVED` | `doc/tasks/MAINT-1-RELEASE-MONITOR.md:74-75`（93 ACL + 31 仓库根发现 + 3 删除；真实仓库全量 **1875 passed / 0 failed / 109 skipped**）；日志 `verification/MAINT-1-RELEASE-MONITOR/logs/dotnet-full-current.log` | 否 |
| L-AC1-3 | FEA-15-ACCEPT-1 | 当前版本**安装**演练 NOT_RUN（`:131`） | `WAIVER` | `W7`（C4 载体 `:26`，含"真实 clean install"） | 否 |
| L-AC1-4 | FEA-15-ACCEPT-1 | 可见 UI 验收 NOT_RUN（`:131`） | `WAIVER` + 部分 `SOLVED` | 首屏层已补：`doc/tasks/MAINT-1-RELEASE-MONITOR.md:82-83`（四页冒烟 + 截图）；**全验收**仍 `W7` | 否 |
| L-AC1-5 | FEA-15-ACCEPT-1 | 真实用户库升级 / 回退 NOT_RUN（`:131`） | `WAIVER` | `W7` | 否 |
| L-AC1-6 | FEA-15-ACCEPT-1 | 30 条 pin 中 27 条跨 checkout 工作区哈希不可复现（`:131`） | `UNCERTAIN` | 口径与盘点已落地：`doc/tasks/FEA-15-PIN-POLICY-1.md`（done）、`doc/tasks/FEA-15-PIN-EOL-GOV-1.md`（done，只读盘点）；**逐条重钉是否执行本轮未核实** → §4-R1 | **是** |
| L-AC1-7 | FEA-15-ACCEPT-1 | 62 个共享 fixture 候选 / 系统 Python ACL / AppContainer profile 维持 `PRESERVE_UNKNOWN`；构建 worktree `PRESERVE_REFERENCED`（`:131`） | `KEEP` | 属**资源 disposition**（非技术 limitation）：卡面 `:131-132`；资源保留不构成 DoD §3 的技术缺口，但需登记 | 否 |
| L-PB1-1 | FEA-15-PIN-BASIS-ENFORCE-1 | `FEA-06-PREREQ-1` TaskPath FAIL（13 errors / EXIT=1）（`doc/tasks/FEA-15-PIN-BASIS-ENFORCE-1.md:415`） | `C3`（建议） | 本文件 §3-C3-10（不改历史卡面）；**本轮实测复现** `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-06-PREREQ-1.md` → `FAIL (13 errors, 3 warnings) / EXIT=1`；同项见 `doc/reviews/MAINT-1-P6-LINE-CLOSEOUT-VERDICT.md:39` | 否（建议 OUT） |
| L-PB1-2 | FEA-15-PIN-BASIS-ENFORCE-1 | `CHAPTER-SELECTOR-1` TaskPath FAIL（6 errors）（`:415`） | `SOLVED` | 已转绿：`doc/tasks/MAINT-1-RELEASE-MONITOR.md:99`（补 `<<MET>>` 与 Manifest）；**本轮实测** `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/CHAPTER-SELECTOR-1.md` → `PASS (3 warnings) / EXIT=0`；`:102`「单卡 FAIL 清单 2 → 1」 | 否 |
| L-PB1-3 | FEA-15-PIN-BASIS-ENFORCE-1 | full suite 历史 `61 passed / 2 skipped / 3 failed / EXIT=1`（`:415`） | `UNCERTAIN` | 该卡后续 R-001 全行 audit `164/164 / FAIL_ROWS=0 / EXIT=0`（`:411`）已取代部分结论，但**未找到该专项 suite 在终态 head 的复跑日志** → §4-R3；建议补一次复跑（§3-C1-8） | **是** |
| L-PB1-4 | FEA-15-PIN-BASIS-ENFORCE-1 | Linux 运行 `NOT_RUN`（`:415`） | `WAIVER` | `W8`（C4 载体 `:27`） | 否 |
| L-PB1-5 | FEA-15-PIN-BASIS-ENFORCE-1 | P2-1 / P2-2 / P3-B / P3-D 保留原分类（`:415-416`） | `KEEP` | 原分类正本：该卡 `:7`（`AC4 ACCEPT_WITH_LIMITATIONS`，P2-1/P2-2 由 ZCode 接纳为限制）与 `:415-416`；本文件不重新分类 | 否 |

**统计（按主处置码计，共 39 项）**：`C3` **10**（含本文件新裁 4 项 L-F1-4/L-AI1-1/L-AI1-2/L-PB1-1，及 1 项"建议 C3"）/ `WAIVER` **10**（其中 L-AC1-4 兼"部分已解"）/ `IMPL` **8**（其中 L-F1-3、L-L1-2 为部分实现）/ `C2` **4**（第 5 项 C2 已由 `C3-2` 归位，不重复计）/ `SOLVED` **3**（L-AC1-1、L-AC1-2、L-PB1-2）/ `KEEP` **2** / `UNCERTAIN` **2**。合计 10+10+8+4+3+2+2 = **39**。

## 2. 逐节点摘要

| 节点 | 摘要 | 悬空 `L-*` |
|---|---|---|
| `FEA-15-A3-1` | 日志根回落属有意发行默认（C3-6）＋ 原生交互矩阵未执行为 C4（W6）。 | 无 |
| `FEA-14-READ-1` | UI 未接线已拆 `READ-2`；P12/P15 契约偏差归 C2（建议 OUT）；真实交互 C4（W1）。 | 有：经 `L-R2-1` |
| `FEA-14-READ-2` | **可见控件仍未接线**（唯一实质 C1）；真实交互 C4（W1）。 | **有 1 项** |
| `FEA-14-FONT-1` | FONT-2 范围 C3-5；wire 负例与压测仍缺（C1）；占用文件保留；日志口径登记。 | **有 2 项** |
| `FEA-14-LIB-1` | `kind` 投影、`custom_rank` 读回、64 位边界三项 C1；R-11 deferral C2；真实联调 C4（W5）。 | **有 3 项（其中 1 部分）** |
| `FEA-14-EDIT-1` | 四项 limitation 全部已有 C3-2/C3-3/C3-4 与 W2 承接。 | 无 |
| `FEA-14-AI-1` | ⑤ DDL 裁决 C3-1；①/② 本文件补裁 C3-8/C3-9；③/④ C2（建议 OUT）；⑥ 微清理 C1；⑦ C4（W3）。 | **有 1 项（⑥）** |
| `FEA-15-ACCEPT-1` | pytest 16F 与 .NET 127F **均已解**（3537/0/0；1875/0/109）；安装/可见 UI 全验收/真实库 C4（W7）；pin 27/30 **UNCERTAIN**。 | **有 1 项 UNCERTAIN** |
| `FEA-15-PIN-BASIS-ENFORCE-1` | `CHAPTER-SELECTOR-1` 已转绿；`FEA-06-PREREQ-1` 建议 OUT（本文件 §3-C3-10）；专项 suite 需复跑（UNCERTAIN/IMPL）；Linux C4（W8）。 | **有 1 项 UNCERTAIN** |

## 3. C1 / C2 未决项裁决建议（DSH 终裁，逐项给理由）

> 分类沿用 `doc/reviews/MAINT-1-P3-LIMITATION-TRIAGE.md:44-50`（C1 约 13 / C2 5）。下列编号为本文件新增，供裁决引用。

### 3.1 C1（工程可闭环）——建议分布：**实现 8 项 / OUT 2 项 / 保留 NOT_RUN 3 项 = 13 项**

| # | 项（来源） | 建议 | 理由 |
|---|---|---|---|
| C1-1 | READ-2 可见控件接线（L-R2-1） | **实现** | VM 行为与 7 个 VM 测试已覆盖（`doc/tasks/FEA-14-READ-2.md:115`），只缺 View 层控件；是**用户可见**缺口，价值最高，一张 UI 卡可闭环 |
| C1-2 | FONT `FONT_DELETE_FAILED` wire 负例（L-F1-2） | **实现** | storage 侧已覆盖，wire 侧仅缺 1 个负例断言；成本极低，不做会在下次 wire 变更时失去回归保护 |
| C1-3 | FONT 大文件 / 并发 压测（L-F1-3 前两项） | **实现** | 可在 headless/单测构造（50MB 上限已实现），无需真机；占用文件部分保留 |
| C1-4 | LIB `ChapterSummary` 投影 `kind`（L-L1-1） | **实现** | DTO 只读扩展，无契约风险；不做则 `LIB-2` 无法交付自定义排序 UI |
| C1-5 | LIB `custom_rank` 读回闭环（L-L1-2 前半） | **实现** | 当前 write-only 是**半闭环**（写进去读不出），属实现完整性缺口；排序 UI 范围另归 OUT |
| C1-6 | LIB 64 位边界校验（L-L1-4） | **实现** | 输入边界缺 1 组断言，成本低、风险明确（大 id 截断） |
| C1-7 | AI-1 死方法 `reassign_references` + 旧注释（L-AI1-6） | **实现**（微清理） | 死代码与错注释会误导后续卡；可并入任一维护小卡，不需独立发布 |
| C1-8 | PIN-BASIS 专项 suite 复跑留证（L-PB1-3） | **实现**（验证动作） | R-001 已 164/164，但"61/2/3"仍作为 FAIL 陈述挂着；补一次终态复跑即可把 UNCERTAIN 转为 SOLVED |
| C1-9 | FONT 占用文件压测（L-F1-3 后项） | **保留 NOT_RUN** | 需真实文件锁/占用进程，本环境不可构造；`W4` 已 waiver 相邻项 |
| C1-10 | ACCEPT pin 27/30 逐条重钉（L-AC1-6） | **保留 NOT_RUN + UNCERTAIN** | 口径（`PIN-POLICY-1` done）与盘点（`PIN-EOL-GOV-1` done）已定；逐条重钉属**维护性**，不阻塞发布语义。若要清零需单独 GOV 卡 |
| C1-11 | ACCEPT 安装演练（L-AC1-3） | **OUT（已由 W7 承接）** | 与 C4 安装项为同一件事，重复计会虚增 C1；统一记 `W7` |
| C1-12 | ACCEPT 资源 `PRESERVE_UNKNOWN`（L-AC1-7） | **保留 NOT_RUN（资源登记）** | 属资源 disposition（`RESOURCE-CLOSEOUT`），不是技术 limitation；按资源清单保留即可 |
| C1-13 | PIN-BASIS `FEA-06-PREREQ-1` TaskPath FAIL（L-PB1-1） | **OUT** | 13 条错误全为「done 卡声明与实际不一致」（DONE+PARTIAL AC / Manifest 缺失）；修它必须改写 done 卡的状态或 AC 标记 = **改历史字节**，与字节保留规则冲突；且不影响全局门禁（仅单卡 `-TaskPath` 红）。见 §3.3 |

> C1 分布核对：**实现 8**（C1-1…C1-8）/ **OUT 2**（C1-11 由 `W7` 承接、C1-13 不改历史卡）/ **保留 NOT_RUN 3**（C1-9 占用文件、C1-10 pin 逐条重钉、C1-12 资源登记）。合计 13，与 triage「约 13」吻合。

### 3.2 C2（契约对齐）——建议分布：**OUT 4 项 / OUT（条件性）1 项 = 5 项全部 OUT**

| # | 项（来源） | 建议 | 理由 |
|---|---|---|---|
| C2-1 | AI-1 name 唯一/规范化（L-AI1-4，F-05） | **OUT** | 现状是「未软删行 name 唯一」；大小写/空白规范化属**产品语义变更**（是否把 `A` 与 `a` 视为同名），无用户提出、无 UI 消费方；改动需 errata + 迁移。重开条件：出现跨大小写重名需求或 UI 显示重复名 |
| C2-2 | AI-1 `UPDATE OR REPLACE` label 覆盖（L-AI1-3，F-03） | **OUT** | 覆盖仅发生在**同一 `(kind,owner_id)` 已有引用**时，而引用写入方尚未启用（L-AI1-2）；今天没有可触发的路径。重开条件：引用写入卡落地时一并改用 UPSERT 合并 |
| C2-4 | LIB-1 R-11 三项 deferral（L-L1-3） | **OUT** | 三项都需 additive/UNFREEZE（`kind` 语义体积、`number_value`、`normalized_title` 唯一索引），当前**无消费者**；为无消费者的字段改冻结契约不划算。重开条件：出现按数字排序/规范化检索需求 → 走 C-07/C-01b UNFREEZE |
| C2-5 | READ-1 P12/P15 返回类型与 `confirm_token` 偏差（L-R1-2） | **OUT** | 偏差已登记且 UI 未使用 `confirm_token`（reset 确认由 VM 侧 `confirm=true` 表达，`doc/tasks/FEA-14-READ-2.md:115`）；对齐需改 wire 返回类型 = 二次 UNFREEZE，收益为零。重开条件：客户端需要 token 级幂等确认 |
| C2-3 | EDIT-1 `position` 是否升为跨卡契约 | **OUT（条件性，已由 C3-2 归位）** | `C3-2` 已裁"不提升为跨卡契约"；作为 C2 的怀疑项**解除**，不重复计。若将来提升，需 PREQ errata/ADR（C3-2 重开条件同） |

### 3.3 本文件新增的 OUT（原 triage 未覆盖，需 DSH 确认）

| # | 项 | OUT 理由 |
|---|---|---|
| C3-7 | FONT-1「日志 HEAD 为生成时工作树」（L-F1-4） | 证据口径说明，非产品/契约项；同类口径债务已在多卡披露（如 `FEA-06-RESIDUAL-4A` P3-4）。属记录精度，不构成 limitation 未处置。 |
| C3-8 | AI-1 P24 只回 `template_id`（L-AI1-1） | wire 契约**事实**（P24 返回类型即 `template_id`），UI 展示名一律走 P21 列表；不存在"错误数据"，只是需要二次刷新。以缺陷论处会误导后续卡去改 wire。 |
| C3-9 | AI-1 引用写入方未实现（L-AI1-2） | 引用写入方（译文/任务/规则）属**其他切片范围且从未释放**；AI-1 已交付完整模板 CRUD + 删除替身语义。属范围外，非缺陷。 |
| C3-10 | PIN-BASIS `FEA-06-PREREQ-1` TaskPath FAIL（L-PB1-1） | 见 §3.1 C1-13：修它需改写 done 卡历史字节；影响面仅单卡检查。**保留 FAIL 原文作为治理债登记**（`doc/reviews/MAINT-1-P6-LINE-CLOSEOUT-VERDICT.md:39`）。 |

## 4. 残留清单与 UNCERTAIN（不得当作已处置）

| # | 项 | 缺什么 / 阻塞原因 | 建议动作 |
|---|---|---|---|
| R1 | ACCEPT-1 的「30 条 pin 中 27 条跨 checkout 不可复现」（L-AC1-6） | 政策卡 `FEA-15-PIN-POLICY-1`（done）与盘点卡 `FEA-15-PIN-EOL-GOV-1`（done）已定口径与清单，但**本轮未核实 27 条是否已逐条重钉**；两份卡的 Closeout 均自述"只读盘点/口径"，未含逐条改写记录 | 由 DSH 决定：① 记 OUT（口径已定，重钉属维护）；② 开 `GOV-PIN-REDO-*` 卡清零。**不得**仅凭两份 done 卡宣称"27 条已修" |
| R2 | pytest 0 failed 的证据在**仓外**（`workspace/flea-loop/pytest-full-ro1.log`） | 证据未入库，`verification/**` 无对应 pin；按项目证据纪律，仓外日志不能作为 Canonical Evidence | 建议把该日志（或其摘要 + sha256）补登到 `verification/MAINT-1-RELEASE-MONITOR/logs/` 并在维护记录回填 |
| R3 | PIN-BASIS「full suite 历史 61/2/3 FAIL」（L-PB1-3） | 未找到该专项 suite 在终态 head 的复跑日志；R-001 全行 audit 不覆盖同一组合 | 建议按 §3-C1-8 补一次复跑并留证；在此之前标 UNCERTAIN |
| R4 | `FEA-06-PREREQ-1` 13 条 TaskPath 错误的**最终处置归属** | 本文件建议 OUT（不改历史卡），但这是**治理取舍**，DSH 可能认为"单卡红不可长期存在" | DSH 终裁；若选修复路径，则必须接受改写 done 卡面（需先登记与字节保留规则的冲突裁决） |

## 5. 对 DoD §1 / §3 的判定（基于本矩阵，需 DSH 确认后生效）

| 判据 | 本矩阵下的状态 | 前置条件 |
|---|---|---|
| **DoD §1** | **有条件可判达成** | 9 节点均满足 §0 的等价关系：39 项 limitation 每项都有 `C3`/`W#`/`SOLVED`/`KEEP` 指针。**剩余不确定**仅 §4 的 R1（pin 27/30 重钉现状）与 R3（PIN-BASIS 专项 suite 复跑）—— 二者闭合后 §1 可判达成；R4 属治理取舍，不影响 §1 实质判定 |
| **DoD §3** | **仍未达成**（当前） | 需 C1 的 8 项 `IMPL` 落地并 MET、C2/C3 建议经 DSH 裁决、§4 的 R1–R4 清零或明确 OUT。**C3/C4 两类的逐项载体已齐**（C3 6 项 + 本文件新增 4 项 = 10；C4 10 项），仅剩 C1/C2 的裁决与实现 |

**不得写成 PASS 的口径**：本文件是**处置前置件**，不是完成声明。它把 §3 从「未分类未处置」推进到「逐项有建议、有指针」，但 **C1 的实现工作尚未开始**（需 `MAINT-2-*` 系列卡，受 `doc/REBASELINE_PLAN.md` 64/64 行预算约束，见 `doc/reviews/MAINT-1-P6-LINE-CLOSEOUT-VERDICT.md:47-52`）。

## 6. 可推翻性

- 任一条 OUT/WAIVER 若被用户或被后续证据推翻，按 append-only 记录推翻原因并重开对应卡；已实现部分不受影响。
- 本文件**不改变任何节点状态**；`closed_with_limitations` 保持原值，`done` 卡保持原字节。

## DSH 终裁（2026-11-14）

逐条终裁；未列出的项按载体建议通过。

### 接受（无修改）

- **§0 等价关系接受为 DSH 裁决**：`closed_with_limitations` + 正式逐项 waiver 载体 ≡ DoD §1 的「done + 显式 waiver」。理由：字节保留优先于状态改写；载体已逐项给出原因与保留的 NOT_RUN 证据指针。**但须在 DoD 判定报告中写明这是 DSH 的解释口径，不是既有裁决原文。**
- **C2 5 项全 OUT**：接受（每项均有重开条件）。
- **新增 C3-7…C3-10**：接受。
- **② pin 27/30 保留 NOT_RUN + UNCERTAIN 标注**：接受。诚实标注优于虚假确定性。
- **③ C3-8 / C3-9（AI-1 的 P24 投影与引用写入方）**：接受 OUT，但**加严重开条件**——一旦出现任何消费者（第二个基底文本消费者、外部工具写引用、V2 Studio），必须自动重开，不得依赖人工记忆。
- **① C3-10（`FEA-06-PREREQ-1` 13 errors）**：接受 OUT，但**限定条件**——仅当「单张卡 `-TaskPath` 红」不被计入 DoD §4 的四件套时成立；须在 DoD 判定报告中显式披露「默认 check 绿、单卡红 1 张」的事实，不得让读者以为全部卡都绿。

### 条件接受

- **C1 的 8 项「实现」是待办，不是已完成**。载体把它们标 `IMPL` 是正确的，但 **DoD §3 在这 8 项落地前仍未达成**。它们须以 1–2 张实现卡落地（建议合并为 `MAINT-2-C1-BATCH-1`），每项带判别测试；不得在载体里把 `IMPL` 读成 `SOLVED`。

### 驳回

- 无。

### 更正要求

- 载体总表「39 项」须与 9 个节点对齐；若某节点 limitation 项数有争议，**以卡面原文为准**，不以 triage 转述为准（triage 是二手整理）。