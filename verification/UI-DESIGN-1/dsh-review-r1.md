# UI-DESIGN-1 独立 Review（R1）

| 项 | 值 |
|---|---|
| Task | UI-DESIGN-1（AD-001 四页 UI/UX 设计基线） |
| Owner | zcode |
| Reviewer | dsh（epoch 6；独立于 Owner，未参与设计写作） |
| 交付 commit | `aaf00e59e7eb4fcba83ae6dcbd6a845e2b46fa06`（内容）→ `c59d20554`（证据 pin 回填） |
| 集成 commit | `a24001f9f0c432c0b6670ac4a432cc2863b1c7bf` |
| 基线 | `c6f975d38842487c16491eea67a01cf134c337f8` |
| 结论 | **approved**（无 I1/I2 finding；下列均为已接受的信息性记录） |

## 1. 独立验证实际做了什么（可复现）

| # | 验证项 | 命令 / 方法 | 结果 |
|---|---|---|---|
| V1 | canonical 自检（Owner 被 harness 拒绝、由其明确委托 Reviewer 复跑） | `pwsh -NoProfile -ExecutionPolicy Bypass -File verification/UI-DESIGN-1/selfcheck.ps1`（worktree） | **exit 0，`RESULT: ALL CHECKS PASS`**；W=29 / G=26 |
| V2 | 契约引用**语义级**核验（不只是"名字在文件里"） | 逐行读取 `M2-C1_TYPED_IPC_CONTRACT.md` 被引行，与 §6 表声明逐条比对 | W1→L139 `ListBooks`（含 `page_count int\|null` 的 `1.2` 修订）、W2/W3→L159/L160 `ListChapters`/`ListChapterPages`（wire `list_chapters`/`list_chapter_pages`）、W4→L143 `ImportPages` **2.2 FROZEN**、W17→L556–559 四个事件、W26/W27→L236–248 `settings_get`/`settings_update_section`、W28→L721 `## 8. Error envelope` —— **全部对应准确** |
| V3 | 缺口表诚实性（是否"假装可用"） | 核验两条最关键的缺口声明 | G6 引 M2-C1 §5.7：该节确实冻结 **host-only** HostControl 且明言"不属于 §3 普通 command catalog，也不是 Tauri command" → 因此 P12 必须新增 WebView 可触发的选择器命令，缺口真实；G26：`ImportProgressChanged` 在 §6.2/rev2.2 确为 **UNKNOWN / PROPOSAL** 且给出原因（P09 无持久 operation/snapshot） → 缺口真实 |
| V4 | 范围与主仓保护 | worktree `git status`；主仓 HEAD + `git status --porcelain --untracked-files=no` | worktree 改动**全部**落在允许范围（1 个允许的 task 文件 + 3 个新建路径）；主仓 `4dcd5a949`、**19 项 dirty 与用户清单逐项一致**，无 EXTERNAL_CHANGE |
| V5 | 结构完整性 | 文档 552 行；§0–§10 + AC 对照附表 | §1 Shell、§2–§5 四页（每页六要素）、§6 绑定表、§7 缺口表、§8 令牌、§9 九条边界自证、§10 十条非目标 |
| V6 | 权威纪律 | 检查 §0 的事实优先级与 LEGACY 标注 | CURRENT(AD-001)/REQUIREMENT/冻结契约/既有实现/LEGACY 五层分级清晰；LEGACY 一律标注"历史参考、非绑定"，**未在任何处单独作为要求依据** |

## 2. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 四页覆盖 | **PASS** | V5 + V1(d)：四页各自成节，每页含职责/布局/组件/五态矩阵/交互/键盘焦点 |
| AC2 导航 Shell | **PASS** | §1 冻结 Rail 四入口、keep-alive 语义；依据 08 AC-NAV-003 与 P11 §7.1/7.2（非 LEGACY）；并正确地把"切换不停止任务"归因为**架构事实**而非 UI 义务 |
| AC3 契约绑定表 | **PASS** | V2：29 行绑定，所抽查引用逐条准确；每行给文件+章节+行号，行号标注为基线 commit 下的辅助信息 |
| AC4 wire 缺口表 | **PASS** | V3 + V1：26 条，每条含页面/交互/期望语义/当前缺口/建议后续动作；无 mock、私有路径或绕过 IPC 的消解 |
| AC5 边界合规 | **PASS** | §9 九条（SQLite/路径/模型/大媒体/持久化/事件非真值/Secret/源文件/不发明 wire），与 AD-001 边界表及 M2-C1 §2/§10 一致 |
| AC6 设计令牌 | **PASS** | §8 全部声明为【自有取值】，并显式声明与 LEGACY "参考、非绑定"；无 parity 承诺 |
| AC7 非目标 | **PASS** | §10 十条，含"不裁决 P18 JA/KO 门槛"与"不写产品代码" |
| AC8 自检可核验 | **PASS（由 Reviewer 关闭）** | Owner 会话被 harness 拒绝执行（如实登记 + 等价 bash 证据），canonical 复跑由 Reviewer 执行 → V1 exit 0 |
| AC9 交付 | **PASS（Coordinator 补足）** | Owner 的 `git add` 被拒；Coordinator 按 Owner 预制命令**逐字重放**产生 `aaf00e59e`，内容未改；证据 pin/sha256 已回填 |

## 3. 已接受的信息性记录（非返修项）

- **N1（交付流程，重要）**：ZCode 在本机以 `--mode edit` headless 派发时，**harness 权限层会拒绝全部 shell 命令**（原文 `No permission client configured for Bash`），包括 `powershell`、`git add`、`certutil` 与复合命令。本次后果：Owner 无法自跑自检、无法提交，只能靠 Reviewer/Coordinator 补齐。**建议**：把该事实写入 `.orchestrator/RUNTIME_DIRECTIVES.md` 的 ZCode 派发约定——凡需要执行命令或提交的 ZCode Task，要么改用允许命令的模式，要么在 Task 内显式把"自检复跑/提交"指派给 Owner 之外的执行者。Owner 本次**未伪造任何输出**，处理正确。
- **N2（证据完整性）**：Owner 的等价运行日志已作为 `SOURCE_PIN` 保留为 `selfcheck-output-owner-equivalent.txt`，canonical 日志另存 `selfcheck-output.txt`；两者不互相覆盖。
- **N3（行号漂移）**：§6 的行号相对基线 commit；契约修订后行号会漂移。机器核验以**名字逐字检索**为准（`selfcheck.ps1` (a)），文档已自述此约定，因此不构成缺陷。
- **N4（commit 回放的独立性声明）**：集成前的 `aaf00e59e` 由 Coordinator 机械重放 Owner 的预制命令产生，**未修改文件内容**，交付物作者仍为 zcode。此处如实披露，以便审计区分"作者"与"提交者"。

## 4. 本设计最重要的输出：对 DAG 的影响

§7 的 26 条缺口表明：**P12/P14/P15/P17 并非在设计冻结后即可直接释放**，其中多条被 host/契约缺口前置：

| 缺口 | 阻塞 | 性质 |
|---|---|---|
| **G6 / G19 / G20** | P12（书架导入）、P17（导出） | host 侧需新增 WebView 可触发的"来源/目标选择 + 打开目录"命令（`ImportSourceRef`/`ExportTargetRef`/HostControl 已冻结，但按 §5.7 不得由 WebView 调用） |
| **G17** | P14（工作台） | host→WebView 的**事件转发面**未在任何契约冻结 |
| **G15** | 中断恢复 + NavBadge | 无 `ListRuns`/活动 Run 查询 wire |
| **G21–G25** | P15（设置维护） | Provider Profile / 凭据交换 / Network Profile / 设置范围解析 / 各分区 schema 均无 wire |

结论：下一批 READY 应优先是**契约/host 前置 Task**，而不是直接释放四页实现；P14 的实现面最完整（除 G17 外），若要先出一条端到端可见的线路，建议先解 G17 + G6/G19/G20 中的一个。

## 5. 残余风险

- 设计与实现之间仍可能发现新的 wire 缺口（本设计已把已知项穷举登记，但 §6 只覆盖"需要数据的元素"）。
- §8 令牌为**新架构首次冻结**，尚无任何实现对照，P12/P14 实现时需要一次视觉走查确认可落地。
- 本 Review 未验证 React 侧可编译性（本 Task 不写产品代码），实现 Task 必须自带构建证据。
