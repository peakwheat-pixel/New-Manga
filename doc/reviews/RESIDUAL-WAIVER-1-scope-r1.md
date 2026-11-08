# RESIDUAL-WAIVER-1 scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（session `4092531d-b97b-49c8-b74c-c3e057066aa0`；未参与本裁决起草） |
| 模式 | 严格只读（read/grep/glob + 只读 git；一次只读环境查询：`Screen.AllScreens`/`Win32_VideoController`/`PerMonitorSettings`） |
| 被审 head | `4070f0043`（main，clean） |
| 被审对象 | `doc/plan/RESIDUAL-CLOSEOUT-PLAN-2026-11-08.md` §2 的 R0 裁决集（10 项）与 R1–R4 草案 |
| 结论 | **`NOT_RECOMMENDED`** —— R0 现稿不应冻结：至少 4 项被误分类（可工程闭环的 C1 写成 C4/C3）、2 项契约依据不成立、硬件前提与事实不符（本机现有 2 个活动显示器）、翻 done 需改写 17 条历史 AC 行并与 `09_COLLABORATION:79` 及 HOST-AUTH-1 的 Codex 终裁冲突 |
| 落盘 | 正文由该子代理产出，DSH 落盘并按 §评审结论 修订方案（见 `doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` v2） |

## 0. 评审先钉住的两个基线事实

1. PLAN 头部写 `.NET 1691/0/96`、AUTORUN 要求 `≥1691`，但 `doc/STATUS.md:20` 权威基线写 **1683/0/96** → 按现 head 执行会假失败；**R0/R1 必须重钉基线**。
2. R0 v1 说「10 项」但 PLAN §2 表只有 8 行且分类互相矛盾（第 6 行 `C2/C3`、第 7 行 `C2`、第 8 行 `C1 不做`）；「10 项」与 PLAN 不一致 → **必须先统一清单**。

## 1. 逐项核实结论（摘要）

| # | 项 | 评审判定 | 关键反证 |
|---|---|---|---|
| 1 | FEA-07 AC1（原生 IME + A03 真库 + ACK 重连 + 真实 Run） | **split** | A03/ACK/Run 可用 gated 真实 sidecar+真实 SQLite 测（`ChapterCreationTests.cs:161-251`、`RunControllerTests.cs:284-440`、`Fea11SourceIpcTests.cs:437`、`tests/fea11/test_source_lineage_run.py:8`）；仅原生 IME 真需原生会话 |
| 2 | FEA-07 AC2（双屏 broker + `(SessionId,RegionId)` 单写 + Host 生命周期） | **split** | `WindowBroker.cs:24-66` **尚未实现**单写 owner（功能缺口，非硬件）；ADJ-2026-11-01:20 已冻结语义；仅「真实双屏落位」需原生 |
| 3 | FEA-07 AC5（双屏/拔屏/DPI 矩阵） | **disagree（「无硬件」不成立）** | 本机 **2 个活动显示器**；仓库记录 3 个虚拟适配器（`P20-MEM-OPT-1.md:32`、`GPU-ORT-PROBE-1/REPORT.md:25`）；`GOAL-PROGRESS:311` 原文为「本机**可能**无双屏」的推测。正确状态=**未执行**，非「无硬件」 |
| 4 | FEA-06-RESIDUAL-2（Tab 遍历 + a11y + 200% DPI + 原生截图） | **split** | Tab 遍历与 `AutomationProperties`/UIA 可 headless 断言（`FluentFocusPageCoverageTests.cs:42-59`、`V2AccessibilityTests.cs:24|137|201`）；仅 Narrator 行为/200% 像素/原生截图需原生 |
| 5 | FEA-11 AC11-1 / L-STARTUP | **agree（C3），但理由要改** | AD-003 `:87-93` 与 C-01b SC-25（`:84`）四项组合**不含**启动全量扫描但也未禁止；C-17 `:18` 只说明 `source_list_scan_targets` 枚举目标不读内容 → 依据应为「契约解释 + 产品范围」，**不得写「C-17 规定不做」** |
| 6 | FEA-11 AC11-3 / L-M1（PDF 插页 pixel profile） | **disagree（不是「能力外/无消费者」）** | C-15 §3.2 `:230` **明确点名「插页」**需 pixel 证据一对一匹配；`matcher.py:164-194/219-227/307-333` 是真实消费者；PDF 降级导致全页 needs_confirmation（用户可见代价） → 应 BLOCKED 或产品显式决定 |
| 7 | FEA-11 AC11-6（folder relink 一律拒绝） | **disagree（不是「C-15 冻结规则」）** | C-17 `:278` 允许「能证明同一」的 relink（无法证明才转 repoint）；现拒绝源于 folder grant 缺 `container_facts`（`service.py:467-478`）+ folder identity 键疑似不符 C-15 `:216`（`runtime.py:978-991`，已登记 `L-S4-2`）；且**无测试**（`FEA-11-r7.md:34` R7-05 open）；L-6 后半句（跨卷/成员重排/其他项目）未覆盖 |
| 8 | FEA-11 其他 L 项「不属节点 AC」 | **disagree** | L-1/L-8/L-9 分别是 AC11-8/AC11-9 残项（R1/R3 必须补）；L-2 由 LINEAGE-1 done；只有 L-11（IPC flake）是测试债务；「大库冷启动成本」属 SCAN 线（`FEA-11-SCAN-1.md:208/226`、`-SCAN-2.md:252`），R0 v1 张冠李戴 |
| 9 | FEA-07 AC6（UI freeze 上限估计） | **agree（C1，不 waive）** | `PerformanceBaselineTests.cs:127` 取最大切换耗时当 freeze 上限，不是 UI 线程调度停顿；可用 Dispatcher 心跳测最大调度间隔，headless 可闭环 |
| 10 | FEA-06-RESIDUAL-2 五个 BLOCKED 格 | **agree（C1，不 waive）** | 依赖已 done（`REBASELINE_PLAN:16-21`）；Fluent 侧确实未接数据（`WorkbenchPageView.cs:279-308` 硬编码「端口尚未接入（B-2）」）；V2 侧有可复用映射（`StudioRunControllerDataSource.cs:27-90`） |

## 2. 契约依据核对（评审原文表，摘要）

| 条款 | 行号 | 结论 |
|---|---|---|
| AD-003 §3.6 / C-01b SC-25 | `AD-003:87-93`、`C01b:3,84` | 四项检测组合**不含**启动全量扫描，也未禁止 → 支持「不要求」，不支持「契约禁止」 |
| C-17 §0 / §3.2 / §5.3 | `C17:18`、`:161`、`:169`、`:278` | `:161`/`:169` = ACK/recovery 的 **fresh grant/授权重验** 明文要求（R1 合同依据成立）；`:278` = relink 允许「能证明同一」，无法证明才转 repoint |
| C-15 §3.1/§3.2/§5 | `C15:214,216,218`、`:223-231`、`:316` | §3.2 `:230` 明确覆盖「插页」；folder identity = volume serial + file id；§5 `:316` = 原生证据未取得只能标 LIMITED，不得 PASS |
| 09_COLLABORATION §4 | `:77,79` | `done` 需逐项 AC 证据；`closed_with_limitations`「除新授权外不恢复实施」，且不等技术完成/可发布 |
| check.ps1 AC 门禁 | `tools/governance/check.ps1:814-851` | `status: done` 下 `<<PARTIAL>>/<<BLOCKED>>` 直接报错；`<<MET>>` 必须 `[x]` 且不带原因；`<<NOT_APPLICABLE>>` 必须 `[x]` 且有原因。**4 卡共 17 条未勾选 AC 需改写** |
| HOST-AUTH-1 终裁 | `doc/tasks/FEA-11-HOST-AUTH-1.md:95` | Codex 终裁要求「AC3 保持 PARTIAL，不改写为 PASS」→ 翻转需**用户级新授权**并明写取代关系 |

## 3. 评审列出的「疑似被误 waive」项（DSH 已全部采纳）

A 级：FEA-07 AC1 的 A03/ACK/Run（C1 冒充 C4）；FEA-07 AC2 的单写 owner/Host 生命周期（C1 冒充 C4）。
B 级：FEA-06-RESIDUAL-2 的 Tab 遍历 + a11y 属性（C1 混入 C4）。
C 级：FEA-11 AC11-6 folder relink（契约误读 + 无测试 + L-6 只处理一半）；FEA-11 AC11-3/L-M1 PDF（「无消费者」不成立）。
D 级：FEA-07 AC5 的「无硬件」前提（事实错误）。
E 级：覆盖缺口——FEA-07 AC8 原生截图无 disposition、AC3「暂停期间保护状态变化」未进 R4 AC、FEA-11 AC11-5 未回填、AC11-8/9 依赖 R1/R3。

## 4. 评审给出的必填边界（DSH 已写入 ADJ §0）

waiver ≠ 实测通过；NA ≠ 产品范围外；done ≠ 可发布；「无硬件」不能当挡箭牌；「无消费者」必须举证；「契约禁止」必须给原文；原生项只能 `NOT_RUN` + 保留恢复条件；17 条 AC 行改写属高风险动作须逐条 before/after + 授权；`RESIDUAL-2` 的 BLOCKED 表格不被 AC 门禁看见（done 不覆盖它）；基线须当轮重钉；C-17:161 是 R1 合同依据；用户可推翻。
