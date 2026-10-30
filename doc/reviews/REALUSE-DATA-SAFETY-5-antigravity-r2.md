---
task: REALUSE-DATA-SAFETY-5
round: 2
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: FAIL_WITH_MUST_FIX
reviewed_head: 232ff7510
reviewed_base: a5c08bfb0
captured_by: dsh-lead
capture_note: >
  Antigravity 原始回答逐字保存（agy headless --output-format json 的 response 字段）。
  正文未做任何编辑。四轮里前三轮都是 FAIL_WITH_MUST_FIX，且两轮针对的是同一件事：
  我第一次把「没搜到」写成了「不存在」，第二次又只把更正写进了仓外文件。
---

# REALUSE-DATA-SAFETY-5 独立审查（Round 2，Antigravity）

**本轮核心问题**：更正只写进了仓外 DEFECTS.md，版本化的 Task 卡与 Handoff 里错误断言全盘残留

## 复核逐项评估

---

### 1. M1 记录更正彻底性核查

| 文件与行号 | 状态 | 详细核查结果 |
|---|---|---|
| `DEFECTS.md:159-166` | **已修复** | 明确写出了纠正声明，承认上一版因使用 `### MA-xx` 正则导致漏检列表项 `- **MA-21**` 的真实原因，不再有“从未存在”的断言。 |
| `DEFECTS.md:181-182` | **部分修复** | 复核总表中 MA-21/22 虽已补充列出，但右侧处理列仍写作“仍成立（待修）/ 本批修或记录”，尚未更新为终态判定（MA-21 明确记录暂不修与理由；MA-22 明确已修）。 |
| [`doc/tasks/REALUSE-DATA-SAFETY-5.md:51`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L51) | **未修复** | **严重残留**。AC1 说明文本依然写着：`已核对 9 条中的 8 条（MA-20 的脚本不在仓库，无法核对）` 与 `MA-20（脚本归属待确认）`。 |
| [`doc/tasks/REALUSE-DATA-SAFETY-5.md:52`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L52) | **未修复** | **严重残留**。AC2 依然勾选并保留旧断言：`<<NOT_APPLICABLE: DEFECTS.md 实际只到 MA-20，MA-21/22 从未存在（B4 批次表记账错误）；已把编号越界与 B4 的真实内容一并记入 DEFECTS.md 复核记录>>`。 |
| [`doc/tasks/REALUSE-DATA-SAFETY-5.md:63`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L63) | **未修复** | 测试要求表格中依然写着：`8/9 条判定完成（1 条脚本不在仓库）`。 |
| [`doc/tasks/REALUSE-DATA-SAFETY-5.md:68`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L68) | **未修复** | 测试要求表格中依然写着：`AC2 \| 人工核对编号边界 \| — \| N/A（编号不存在）`。 |
| [`doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md:20`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md#L20) | **未修复** | 交接单依然写着：`\| MA-20 \| 未核对 \| \scripts/install.ps1\ 不在仓库，先确认归属 \|`。 |
| [`doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md:22`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md#L22) | **未修复** | 交接单依然保留加粗断言：`**MA-21 / MA-22 不存在**：DEFECTS.md 实际只到 MA-20，B4 表引用了从未写下的编号。` |

> **判定**：仓外复核记录补充了解释，但在版本化管理的事实源头（Task 卡和 Handoff 文件）中，**所有关于 MA-20 脚本缺失、MA-21/22 不存在的错误断言完全未作任何修改，全盘残留**。

---

### 2. MA-22 实现风险与测试评估

| 检查维度 | 状态 | 依据与代码事实 |
|---|---|---|
| 是否会误删刚写入的文件 | **无风险** | [`HostGrantCoordinator.cs:541-543`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/src/NewManga.Host/HostGrantCoordinator.cs#L541-L543) 中使用 `files.OrderByDescending(f => f.LastWriteTimeUtc).Skip(EvidenceRetentionLimit)`。刚刚写入磁盘的文件拥有最新的时间戳，在倒序排列中位于索引 0，`Skip(200)` 会稳固跳过前 200 个最新文件，被删除的只能是第 201 个及更旧的文件。 |
| 并发与运行期安全性 | **无风险** | `PruneEvidence()` 在 `lock (_evidenceGate)` 临界区内部调用（第 521 行），保证了多线程写入串行化；且无论是目录遍历还是具体文件删除，均被包裹在 `catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)` 中并静默吸收，绝对不会因文件占用或并发冲突导致用户正常的导入/导出主流程崩溃。 |
| 阈值 200 是否合理 | **合理** | 实测 169 页的长篇章节单次全量导入产生 169 个 JSON。200 的上限不仅能完整保留最近一次长篇导入的所有 grant 凭证，而且将目录空间稳稳限制在 ~200KB 内，彻底消除了数万碎片小文件膨胀的长期隐患。 |
| 是否有测试 / 是否必须补 | **建议补充，非阻塞** | 目前全仓尚无直接覆盖 `PruneEvidence()` 的单元测试。由于该机制带有严密的静默异常防护，不属于高风险破坏性逻辑；但从工程规范而言，建议在 `GrantIssuerTests.cs` 中补充一个快速的目录文件修剪断言用例。 |

---

### 3. MA-21 不修的理由评估

- **状态**：**已修复（理由完全成立）**
- **依据**：
  1. MA-21 属于 **P4 卫生项**，仅表现为 wire 日志中偶发的空请求/重复进度响应，对用户界面进度渲染、数据库持久化和续读状态均无任何负面影响；
  2. 该重复现象源于底层 stdio 传输层与协议适配层的双向观察机制，在缺乏专门端到端 wire 交互回归矩阵的情况下擅自变更底层记录逻辑，引入时序死锁或握手误报的风险远高于收益；
  3. AC2 的验收规则明确允许“在 Task 中明确记录为何不值得做”。只要在 Task 卡和 DEFECTS.md 中如实登记该决策理由，即符合要求。

---

### 4. MA-20 改判准确性核查

| 文件与行号 | 状态 | 详细核查结果 |
|---|---|---|
| `DEFECTS.md:180` | **已修复** | 表述非常准确：定位到了真实路径 [`apps/desktop-avalonia/scripts/install.ps1:4`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/apps/desktop-avalonia/scripts/install.ps1#L4)，指明了 `$DataRoot` 默认指向真实 `%APPDATA%\com.newmanga.desktop` 的代码事实，并客观决策“安装脚本隔离涉及部署流程，留给后续 Task 处理”。 |
| `doc/tasks/REALUSE-DATA-SAFETY-5.md` | **未修复** | 见前文 M1，Task 卡第 51 行和第 63 行依然残留“MA-20 脚本不在仓库”的旧断言，未同步更新。 |

---

### 5. 其他治理与文档检查

| 检查项 | 状态 | 依据与代码事实 |
|---|---|---|
| README 备份扩展名 | **已修复** | [`README.md:35`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/README.md#L35) 已由 `*.nmbak` 更新为 `*.sqlite-backup`，并明确说明两者不再共用命名空间。 |
| Canonical Evidence commit pin | **已修复** | [`doc/tasks/REALUSE-DATA-SAFETY-5.md:77-81`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md#L77-L81) 已 pin 到真实提交 `f25120e17`，仓外非法路径行已移除。 |
| 治理检查器（check.ps1） | **待刷新** | 运行 `tools/governance/check.ps1` 目前仅剩 1 项失败：`FAIL: TASK_LEDGER 已过期：声明 8 个非终态 Task，实际 7 个`，需执行 `python tools/governance/task_ledger.py --write` 刷新计数。 |

---

## 总结论

**FAIL_WITH_MUST_FIX**

虽然功能代码（MA-14~18、MA-22）修复正确、测试全套通过（876 passed / 0 failed）、README 同步到位，但**在项目权威事实载体（Task 卡与交接单）中，严重残留着已证实失实的全套旧断言（包括“MA-21/22 从未存在”、“MA-20 脚本缺失”等）**。

按项目治理协议，文档是项目的绝对真实事实来源，不能出现“对话中已承认错误，但在版本化文件里依然一字未改”的脱节状态。

### 必须修复清单（Must-Fix）：
1. **修改 [`doc/tasks/REALUSE-DATA-SAFETY-5.md`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/tasks/REALUSE-DATA-SAFETY-5.md)**：
   - 第 51 行与第 63 行：更正 MA-20 说明（已在 `apps/desktop-avalonia/scripts/install.ps1` 核对，涉及部署隔离留后处理）；
   - 第 52 行与第 68 行：更正 AC2 说明与测试表（记录真实的 MA-21/22 核对结果：MA-22 限制 200 已修，MA-21 属于观测性卫生项记录不修理由）；
2. **修改 [`doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5/doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md)**：
   - 第 20 行与第 22 行：移除“MA-21/22 不存在”和“MA-20 脚本不在仓库”的陈旧语句，与当前事实对齐；
3. **刷新 Ledger**：
   - 运行 `python tools/governance/task_ledger.py --write` 解决治理检查器最后一项报错。

---

## 推荐下一步

通知实现 Agent（DSH）修改上述文档中的残留错误断言并提交 commit，随后由审查者进行最终收口确认。
